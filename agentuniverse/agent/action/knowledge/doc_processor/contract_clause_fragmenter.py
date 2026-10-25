# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @Email   : ai@example.com
# @FileName: contract_clause_fragmenter.py

import re
import logging
from typing import List, Optional, Dict, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)

# Sentence boundary pattern used when splitting over-long clauses at sentence
# boundaries (Latin and CJK sentence enders) before falling back to raw cuts.
# The ender must follow a letter (not a digit), so clause numbers ("1.", "3.2.")
# and years are not mistaken for sentence ends.
_SENTENCE_BOUNDARY_RE = re.compile(r'(?<=[^\W\d_][.!?。！？])\s+')

# Clause types produced by ALLCAPS boilerplate headings and their level in the
# clause hierarchy: preamble/recitals introduce the contract, the operative
# grant and the execution block conclude it, so all sit at the top level.
_BOILERPLATE_LEVEL = 0


@dataclass
class ClauseNode:
    """Represents a clause in the contract hierarchy.

    Attributes:
        id: Unique identifier for the clause.
        text: Content of the clause.
        clause_type: Type of clause (article, section, subsection, etc.).
        hierarchy_level: Depth in the hierarchy (0 for top-level).
        parent_id: ID of parent clause (None for top-level).
        children_ids: IDs of child clauses.
        position: Position in the original document.
        char_start: Start offset of the clause text within the source text.
        char_end: End offset (exclusive) of the clause text within the source text.
    """
    id: str
    text: str
    clause_type: str
    hierarchy_level: int
    parent_id: Optional[str] = None
    children_ids: List[str] = None
    position: int = 0
    char_start: int = 0
    char_end: int = 0

    def __post_init__(self):
        """Initialize the dataclass fields, defaulting children_ids to an empty list when it is None.
        """
        if self.children_ids is None:
            self.children_ids = []


class ContractClauseFragmenter(DocProcessor):
    """Fragment legal contracts by individual clauses while preserving hierarchy.

    This processor parses legal contracts and fragments them into individual clauses
    based on common legal formatting patterns. It preserves the hierarchical structure
    (Article → Section → Subsection) and creates separate documents for each clause
    with rich metadata about relationships and dependencies.

    Recognized clause markers include numbered clauses (`1.`, `1.1`), `Article` /
    `Section` headings, lettered sub-clauses (`(a)`, `(B)`), Chinese markers
    (`第一条`, `一、`, `（一）`) and ALLCAPS boilerplate headings (`WHEREAS`,
    `NOW, THEREFORE`, `IN WITNESS WHEREOF`). Every fragment records the exact
    character span of its text within the source document via the
    `char_start` / `char_end` metadata keys, so callers can always map a fragment
    back to its origin (`source[char_start:char_end] == fragment.text`).

    Attributes:
        preserve_hierarchy: Whether to preserve and track clause hierarchy.
        clause_patterns: List of regex patterns for detecting clauses.
        min_clause_length: Minimum length for a valid clause (characters).
        extract_references: Whether to extract cross-references between clauses.
        skip_on_error: Whether to skip documents that fail processing.
        keep_preamble: Whether to keep the preamble before the first clause marker
            and the WHEREAS recital blocks as fragments (dropped by default).
        max_fragment_chars: Maximum characters per fragment; over-long clauses are
            split at sentence boundaries (raw character cuts as fallback for
            run-on sentences) with `part_index` / `part_count` metadata.
            0 (default) disables splitting.
        boilerplate_patterns: Regex patterns for ALLCAPS boilerplate headings that
            start a new fragment.
    """

    preserve_hierarchy: bool = True
    clause_patterns: List[str] = None
    min_clause_length: int = 10
    extract_references: bool = True
    skip_on_error: bool = True
    keep_preamble: bool = False
    max_fragment_chars: int = 0
    boilerplate_patterns: List[str] = None

    def __init__(self, **data):
        """Initialize the fragmenter and populate the default clause-detection regex patterns when none were provided.

        Args:
            **data: Field values for the fragmenter.
        """
        super().__init__(**data)
        if self.clause_patterns is None:
            self.clause_patterns = [
                r'^Article\s+[IVX\d]+\.?\s*',
                r'^ARTICLE\s+[IVX\d]+\.?\s*',
                r'^Section\s+\d+(\.\d+)*\.?\s*',
                r'^SECTION\s+\d+(\.\d+)*\.?\s*',
                r'^\d+(\.\d+)*\.?\s+',  # Fixed: makes trailing dot optional
                r'^\([a-zA-Z]\)\s*',  # Lettered sub-clauses: (a), (B), ...
                r'^第[一二三四五六七八九十百千\d]+条\s*',  # Chinese: 第X条
                r'^[一二三四五六七八九十百千\d]+、\s*',  # Chinese enumeration
                r'^[（(][一二三四五六七八九十百千\d]+[)）]\s*',  # Chinese parenthesized: （一）, (二)
            ]
        if self.boilerplate_patterns is None:
            self.boilerplate_patterns = [
                r'^WHEREAS\b[,\s]*',  # Recital block
                r'^NOW[,\s]+THEREFORE\b[,\s]*',  # Operative grant
                r'^IN\s+WITNESS\s+WHEREOF\b[,\s]*',  # Execution block
            ]

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Fragment documents into individual clauses.

        Args:
            origin_docs: List of contract documents to fragment.
            query: Optional query object (not used in this processor).

        Returns:
            List of clause documents with hierarchy metadata.
        """
        if not origin_docs:
            return []

        logger.info(f"Starting clause fragmentation of {len(origin_docs)} documents")

        all_clause_docs = []

        for doc in origin_docs:
            try:
                clause_docs = self._fragment_document(doc)
                all_clause_docs.extend(clause_docs)
                logger.info(f"Fragmented document {doc.id} into {len(clause_docs)} clauses")
            except Exception as e:
                logger.error(f"Failed to fragment document {doc.id}: {e}")
                if not self.skip_on_error:
                    raise
                # Pass through original document if skip_on_error is True
                all_clause_docs.append(doc)

        logger.info(f"Total clauses created: {len(all_clause_docs)}")
        return all_clause_docs

    def _fragment_document(self, doc: Document) -> List[Document]:
        """Fragment a single document into clauses.

        Args:
            doc: Document to fragment.

        Returns:
            List of clause documents.
        """
        text = doc.text

        # Step 1: Detect clause boundaries
        boundaries = self._detect_clause_boundaries(text)

        if not boundaries:
            logger.warning(f"No clauses detected in document {doc.id}, returning as single clause")
            return [self._create_single_clause_doc(doc, text, 0)]

        # Step 2: Extract clause texts
        clauses = self._extract_clauses(text, boundaries)

        if not clauses:
            # Every detected fragment was filtered out (e.g. recital blocks with
            # keep_preamble=False, or clauses below min_clause_length).
            logger.warning(f"All detected clauses were filtered out in document {doc.id}, returning as single clause")
            return [self._create_single_clause_doc(doc, text, 0)]

        # Step 3: Build hierarchy if enabled
        if self.preserve_hierarchy:
            hierarchy = self._parse_hierarchy(clauses)
        else:
            hierarchy = {}

        # Step 4: Create documents for each clause
        clause_docs = self._create_clause_documents(doc, clauses, hierarchy)

        return clause_docs

    def _detect_clause_boundaries(self, text: str) -> List[Tuple[int, int, str, str]]:
        """Detect clause boundaries in the text.

        Args:
            text: Contract text to analyze.

        Returns:
            List of tuples: (start_pos, end_pos, clause_type, clause_id).
        """
        boundaries = []
        boilerplate_counters: Dict[str, int] = {}

        lines = text.split('\n')
        current_pos = 0

        for line_idx, line in enumerate(lines):
            line_stripped = line.strip()

            if not line_stripped:
                current_pos += len(line) + 1  # +1 for newline
                continue

            # Check each pattern (clause markers plus ALLCAPS boilerplate headings)
            for pattern in self._boundary_patterns():
                match = re.match(pattern, line_stripped, re.IGNORECASE)
                if match:
                    # Determine clause type and ID
                    clause_type, clause_id = self._parse_clause_header(line_stripped, boilerplate_counters)

                    # Find the end of this clause (start of next clause or end of text)
                    end_pos = self._find_clause_end(lines, line_idx + 1, current_pos + len(line))

                    boundaries.append((current_pos, end_pos, clause_type, clause_id))
                    break

            current_pos += len(line) + 1  # +1 for newline

        # Optionally keep the preamble (text before the first marker) as its own fragment
        if self.keep_preamble and boundaries and boundaries[0][0] > 0 and text[:boundaries[0][0]].strip():
            boundaries.insert(0, (0, boundaries[0][0], 'preamble', 'preamble'))

        return boundaries

    def _boundary_patterns(self) -> List[str]:
        """Return every pattern that can start a new clause fragment.

        Returns:
            Clause marker patterns plus ALLCAPS boilerplate heading patterns.
        """
        return list(self.clause_patterns or []) + list(self.boilerplate_patterns or [])

    def _find_clause_end(self, lines: List[str], start_line_idx: int, start_pos: int) -> int:
        """Find the end position of a clause.

        Args:
            lines: All text lines.
            start_line_idx: Line index to start searching from.
            start_pos: Character position to start from.

        Returns:
            End position of the clause.
        """
        current_pos = start_pos

        for line_idx in range(start_line_idx, len(lines)):
            line = lines[line_idx]

            # Check if this line starts a new clause (marker or boilerplate heading)
            for pattern in self._boundary_patterns():
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    return current_pos

            current_pos += len(line) + 1  # +1 for newline

        # Reached end of document
        return current_pos

    def _parse_clause_header(self, header: str,
                             boilerplate_counters: Optional[Dict[str, int]] = None) -> Tuple[str, str]:
        """Parse clause header to extract type and ID.

        Args:
            header: Clause header string.
            boilerplate_counters: Mutable per-document counters used to number
                repeated boilerplate blocks (e.g. recital_1, recital_2).

        Returns:
            Tuple of (clause_type, clause_id).
        """
        header = header.strip()

        # Article patterns
        if re.match(r'^(Article|ARTICLE)\s+', header, re.IGNORECASE):
            match = re.match(r'^Article\s+([IVX\d]+)', header, re.IGNORECASE)
            clause_id = match.group(1).upper() if match else 'unknown'
            return ('article', f'article_{clause_id}')

        # Section patterns
        if re.match(r'^(Section|SECTION)\s+', header, re.IGNORECASE):
            match = re.search(r'\d+(\.\d+)*', header)
            clause_id = match.group(0) if match else 'unknown'
            return ('section', f'section_{clause_id}')

        # Lettered sub-clause patterns: (a), (B), ...
        match = re.match(r'^\(([a-zA-Z])\)', header)
        if match:
            return ('lettered', f'lettered_{match.group(1).lower()}')

        # Chinese parenthesized markers: （一）, (二), ...
        match = re.match(r'^[（(]([一二三四五六七八九十百千\d]+)[)）]', header)
        if match:
            return ('lettered', f'lettered_{match.group(1)}')

        # ALLCAPS boilerplate headings
        counters = boilerplate_counters if boilerplate_counters is not None else {}
        if re.match(r'^WHEREAS\b', header, re.IGNORECASE):
            counters['recital'] = counters.get('recital', 0) + 1
            return ('recital', f"recital_{counters['recital']}")
        if re.match(r'^NOW[,\s]+THEREFORE\b', header, re.IGNORECASE):
            counters['operative'] = counters.get('operative', 0) + 1
            return ('operative', f"operative_{counters['operative']}")
        if re.match(r'^IN\s+WITNESS\s+WHEREOF\b', header, re.IGNORECASE):
            counters['execution'] = counters.get('execution', 0) + 1
            return ('execution', f"execution_{counters['execution']}")

        # Numbered patterns
        match = re.match(r'^(\d+(\.\d+)*)', header)
        if match:
            clause_id = match.group(1)
            level = clause_id.count('.')
            clause_type = f'subsection_level_{level}'
            return (clause_type, f'clause_{clause_id}')

        # Chinese patterns
        if re.match(r'^第[一二三四五六七八九十百千\d]+条', header):
            match = re.search(r'第(.+?)条', header)
            clause_id = match.group(1) if match else 'unknown'
            return ('article', f'article_{clause_id}')

        # Fallback
        return ('clause', 'clause_unknown')

    def _extract_clauses(self, text: str, boundaries: List[Tuple[int, int, str, str]]) -> List[ClauseNode]:
        """Extract clause nodes from boundaries.

        Args:
            text: Full contract text.
            boundaries: List of clause boundaries.

        Returns:
            List of ClauseNode objects.
        """
        clauses = []

        for idx, (start, end, clause_type, clause_id) in enumerate(boundaries):
            raw = text[start:end]
            lead = len(raw) - len(raw.lstrip())
            tail = len(raw) - len(raw.rstrip())
            clause_text = raw.strip()
            # Exact character span of the stripped clause text within the source
            char_start = start + lead
            char_end = end - tail

            # Recital blocks are non-operative preamble text; drop them unless kept
            if clause_type == 'recital' and not self.keep_preamble:
                logger.debug(f"Dropping recital block (keep_preamble=False): {clause_id}")
                continue

            if len(clause_text) < self.min_clause_length:
                logger.debug(f"Skipping short clause: {clause_id} (length: {len(clause_text)})")
                continue

            clause_node = ClauseNode(
                id=clause_id,
                text=clause_text,
                clause_type=clause_type,
                hierarchy_level=0,  # Will be determined in hierarchy parsing
                position=idx,
                char_start=char_start,
                char_end=char_end,
            )

            clauses.append(clause_node)

        return clauses

    def _parse_hierarchy(self, clauses: List[ClauseNode]) -> Dict[str, ClauseNode]:
        """Parse hierarchical relationships between clauses.

        Args:
            clauses: List of clause nodes.

        Returns:
            Dictionary mapping clause IDs to updated ClauseNode objects.
        """
        hierarchy: Dict[str, ClauseNode] = {}

        for clause in clauses:
            hierarchy[clause.id] = clause

        # Determine hierarchy levels and parent-child relationships
        for i, clause in enumerate(clauses):
            # Determine hierarchy level based on clause type
            if clause.clause_type == 'article':
                clause.hierarchy_level = 0
            elif clause.clause_type == 'section':
                clause.hierarchy_level = 1
            elif clause.clause_type == 'lettered':
                # Lettered items nest under both numbered sub-clauses ("1.1")
                # and their ancestors ("1.", Section), so they sit below both.
                clause.hierarchy_level = 4
            elif clause.clause_type in ('preamble', 'recital', 'operative', 'execution'):
                clause.hierarchy_level = _BOILERPLATE_LEVEL
            elif clause.clause_type.startswith('subsection_level_'):
                level = int(clause.clause_type.split('_')[-1])
                clause.hierarchy_level = 2 + level
            else:
                clause.hierarchy_level = 2

            # Find parent clause
            if i > 0 and clause.hierarchy_level > 0:
                # Look backwards for parent
                for j in range(i - 1, -1, -1):
                    prev_clause = clauses[j]
                    if prev_clause.hierarchy_level < clause.hierarchy_level:
                        clause.parent_id = prev_clause.id
                        prev_clause.children_ids.append(clause.id)
                        break

        return hierarchy

    def _create_clause_documents(self, original_doc: Document, clauses: List[ClauseNode],
                                 hierarchy: Dict[str, ClauseNode]) -> List[Document]:
        """Create Document objects for each clause.

        Args:
            original_doc: Original contract document.
            clauses: List of clause nodes.
            hierarchy: Clause hierarchy mapping.

        Returns:
            List of clause documents.
        """
        clause_docs = []

        for clause in clauses:
            # Build metadata
            metadata = {
                'processor_name': self.name,
                'processor_version': '1.0',
                'processing_timestamp': datetime.now().isoformat(),
                'source_document_id': original_doc.id,
                'clause_id': clause.id,
                'clause_type': clause.clause_type,
                'hierarchy_level': clause.hierarchy_level,
                'position': clause.position,
            }

            # Exact character span of the fragment within the source text
            metadata['char_start'] = clause.char_start
            metadata['char_end'] = clause.char_end

            # Add original metadata
            if original_doc.metadata:
                metadata['original_metadata'] = original_doc.metadata

            # Add hierarchy information
            if self.preserve_hierarchy:
                metadata['parent_clause'] = clause.parent_id
                metadata['children_clauses'] = clause.children_ids

            # Extract references if enabled
            if self.extract_references:
                references = self._extract_references(clause.text, clauses)
                if references:
                    metadata['clause_references'] = references

            # Split over-long clauses (disabled when max_fragment_chars is 0)
            parts = self._split_clause_parts(clause)

            if len(parts) == 1:
                doc = Document(
                    text=clause.text,
                    metadata=metadata,
                    keywords=original_doc.keywords
                )
                clause_docs.append(doc)
                continue

            for part_index, (part_text, part_start, part_end) in enumerate(parts):
                part_metadata = dict(metadata)
                part_metadata['char_start'] = part_start
                part_metadata['char_end'] = part_end
                part_metadata['part_index'] = part_index
                part_metadata['part_count'] = len(parts)
                doc = Document(
                    text=part_text,
                    metadata=part_metadata,
                    keywords=original_doc.keywords
                )
                clause_docs.append(doc)

        return clause_docs

    def _split_clause_parts(self, clause: ClauseNode) -> List[Tuple[str, int, int]]:
        """Split an over-long clause into bounded parts.

        The clause is first split at sentence boundaries so that parts stay
        readable; a single sentence longer than max_fragment_chars is split at
        raw character positions as a fallback. All parts keep the clause
        metadata and carry part_index / part_count keys.

        Args:
            clause: The clause node to split.

        Returns:
            List of (part_text, char_start, char_end) tuples with absolute
            offsets into the source text; a single tuple when no split is
            needed.
        """
        text = clause.text
        max_chars = self.max_fragment_chars
        if not max_chars or max_chars <= 0 or len(text) <= max_chars:
            return [(text, clause.char_start, clause.char_end)]

        # Candidate cut positions: just after each inter-sentence gap
        cuts = [m.end() for m in _SENTENCE_BOUNDARY_RE.finditer(text)]
        cuts.append(len(text))

        spans: List[Tuple[int, int]] = []
        start = 0
        end = 0
        for cut in cuts:
            if cut <= start:
                continue
            if cut - start <= max_chars:
                end = cut
                continue
            if end > start:
                spans.append((start, end))
                start = end
            # Single sentence longer than max_chars: raw character fallback
            while cut - start > max_chars:
                spans.append((start, start + max_chars))
                start += max_chars
            end = cut
        if end > start:
            spans.append((start, end))

        parts = []
        for span_start, span_end in spans:
            raw = text[span_start:span_end]
            lead = len(raw) - len(raw.lstrip())
            tail = len(raw) - len(raw.rstrip())
            part_text = raw.strip()
            if not part_text:
                continue
            parts.append((part_text,
                          clause.char_start + span_start + lead,
                          clause.char_start + span_start + len(raw) - tail))
        return parts

    def _extract_references(self, text: str, all_clauses: List[ClauseNode]) -> List[str]:
        """Extract cross-references to other clauses.

        Resolve complete identifiers at the beginning of target headings, not
        number prefixes or mentions in their bodies. For example, Section 1
        does not refer to Section 10 or Section 1.1. This does not disambiguate
        duplicate section identifiers under different articles.

        Args:
            text: Clause text.
            all_clauses: All clauses in the document.

        Returns:
            List of referenced clause IDs.
        """
        references = []

        # Match a complete marker, then compare it with the target's heading.
        # Substring searches would resolve Section 1 to Section 10/1.1 and
        # would mistake mentions in another clause's body for definitions.
        boundary = r'(?!\w|\.\d)'
        patterns = [
            (r'\bArticle\s+([IVX\d]+)' + boundary,
             r'Article\s+([IVX\d]+)' + boundary),
            (r'\bSection\s+(\d+(?:\.\d+)*)' + boundary,
             r'Section\s+(\d+(?:\.\d+)*)' + boundary),
            (r'\bclause\s+(\d+(?:\.\d+)*)' + boundary,
             r'(?:clause\s+)?(\d+(?:\.\d+)*)' + boundary),
            (r'第([一二三四五六七八九十百千\d]+)条',
             r'第([一二三四五六七八九十百千\d]+)条'),
        ]

        for pattern, heading_pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                reference_id = match.group(1).casefold()
                for clause in all_clauses:
                    heading = re.match(heading_pattern, clause.text.lstrip(), re.IGNORECASE)
                    if heading and heading.group(1).casefold() == reference_id:
                        if clause.id not in references:
                            references.append(clause.id)

        return references

    def _create_single_clause_doc(self, original_doc: Document, text: str, position: int) -> Document:
        """Create a single clause document when no structure is detected.

        Args:
            original_doc: Original document.
            text: Clause text.
            position: Position index.

        Returns:
            Clause document.
        """
        metadata = {
            'processor_name': self.name,
            'processor_version': '1.0',
            'processing_timestamp': datetime.now().isoformat(),
            'source_document_id': original_doc.id,
            'clause_id': 'single_clause',
            'clause_type': 'unstructured',
            'hierarchy_level': 0,
            'position': position,
            'char_start': 0,
            'char_end': len(text) if text else 0,
        }

        if original_doc.metadata:
            metadata['original_metadata'] = original_doc.metadata

        return Document(
            text=text,
            metadata=metadata,
            keywords=original_doc.keywords
        )

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'ContractClauseFragmenter':
        """Initialize fragmenter parameters from configuration.

        Args:
            doc_processor_configer: Configuration object containing fragmenter parameters.

        Returns:
            Initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "preserve_hierarchy"):
            self.preserve_hierarchy = doc_processor_configer.preserve_hierarchy
        if hasattr(doc_processor_configer, "clause_patterns"):
            self.clause_patterns = doc_processor_configer.clause_patterns
        if hasattr(doc_processor_configer, "min_clause_length"):
            self.min_clause_length = doc_processor_configer.min_clause_length
        if hasattr(doc_processor_configer, "extract_references"):
            self.extract_references = doc_processor_configer.extract_references
        if hasattr(doc_processor_configer, "skip_on_error"):
            self.skip_on_error = doc_processor_configer.skip_on_error
        if hasattr(doc_processor_configer, "keep_preamble"):
            self.keep_preamble = doc_processor_configer.keep_preamble
        if hasattr(doc_processor_configer, "max_fragment_chars"):
            self.max_fragment_chars = doc_processor_configer.max_fragment_chars
        if hasattr(doc_processor_configer, "boilerplate_patterns"):
            self.boilerplate_patterns = doc_processor_configer.boilerplate_patterns

        return self
