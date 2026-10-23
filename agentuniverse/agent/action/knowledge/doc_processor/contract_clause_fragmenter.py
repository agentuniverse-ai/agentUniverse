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
    """
    id: str
    text: str
    clause_type: str
    hierarchy_level: int
    parent_id: Optional[str] = None
    children_ids: List[str] = None
    position: int = 0

    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []


class ContractClauseFragmenter(DocProcessor):
    """Fragment legal contracts by individual clauses while preserving hierarchy.

    This processor parses legal contracts and fragments them into individual clauses
    based on common legal formatting patterns. It preserves the hierarchical structure
    (Article → Section → Subsection) and creates separate documents for each clause
    with rich metadata about relationships and dependencies.

    Attributes:
        preserve_hierarchy: Whether to preserve and track clause hierarchy.
        clause_patterns: List of regex patterns for detecting clauses.
        min_clause_length: Minimum length for a valid clause (characters).
        extract_references: Whether to extract cross-references between clauses.
        skip_on_error: Whether to skip documents that fail processing.
    """

    preserve_hierarchy: bool = True
    clause_patterns: List[str] = None
    min_clause_length: int = 10
    extract_references: bool = True
    skip_on_error: bool = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.clause_patterns is None:
            self.clause_patterns = [
                r'^Article\s+[IVX\d]+\.?\s*',
                r'^ARTICLE\s+[IVX\d]+\.?\s*',
                r'^Section\s+\d+(\.\d+)*\.?\s*',
                r'^SECTION\s+\d+(\.\d+)*\.?\s*',
                r'^\d+(\.\d+)*\.?\s+',  # Fixed: makes trailing dot optional
                r'^第[一二三四五六七八九十百千\d]+条\s*',  # Chinese: 第X条
                r'^[一二三四五六七八九十百千\d]+、\s*',  # Chinese enumeration
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

        lines = text.split('\n')
        current_pos = 0

        for line_idx, line in enumerate(lines):
            line_stripped = line.strip()

            if not line_stripped:
                current_pos += len(line) + 1  # +1 for newline
                continue

            # Check each pattern
            for pattern in self.clause_patterns:
                match = re.match(pattern, line_stripped, re.IGNORECASE)
                if match:
                    # Determine clause type and ID
                    clause_type, clause_id = self._parse_clause_header(line_stripped)

                    # Find the end of this clause (start of next clause or end of text)
                    end_pos = self._find_clause_end(lines, line_idx + 1, current_pos + len(line))

                    boundaries.append((current_pos, end_pos, clause_type, clause_id))
                    break

            current_pos += len(line) + 1  # +1 for newline

        return boundaries

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

            # Check if this line starts a new clause
            for pattern in self.clause_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    return current_pos

            current_pos += len(line) + 1  # +1 for newline

        # Reached end of document
        return current_pos

    def _parse_clause_header(self, header: str) -> Tuple[str, str]:
        """Parse clause header to extract type and ID.

        Args:
            header: Clause header string.

        Returns:
            Tuple of (clause_type, clause_id).
        """
        header = header.strip()

        # Article patterns
        if re.match(r'^(Article|ARTICLE)\s+', header, re.IGNORECASE):
            match = re.search(r'[IVX\d]+', header)
            clause_id = match.group(0) if match else 'unknown'
            return ('article', f'article_{clause_id}')

        # Section patterns
        if re.match(r'^(Section|SECTION)\s+', header, re.IGNORECASE):
            match = re.search(r'\d+(\.\d+)*', header)
            clause_id = match.group(0) if match else 'unknown'
            return ('section', f'section_{clause_id}')

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
            clause_text = text[start:end].strip()

            if len(clause_text) < self.min_clause_length:
                logger.debug(f"Skipping short clause: {clause_id} (length: {len(clause_text)})")
                continue

            clause_node = ClauseNode(
                id=clause_id,
                text=clause_text,
                clause_type=clause_type,
                hierarchy_level=0,  # Will be determined in hierarchy parsing
                position=idx
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

            # Create document
            doc = Document(
                text=clause.text,
                metadata=metadata,
                keywords=original_doc.keywords
            )

            clause_docs.append(doc)

        return clause_docs

    def _extract_references(self, text: str, all_clauses: List[ClauseNode]) -> List[str]:
        """Extract cross-references to other clauses.

        Args:
            text: Clause text.
            all_clauses: All clauses in the document.

        Returns:
            List of referenced clause IDs.
        """
        references = []

        # Common reference patterns
        patterns = [
            r'(Article|ARTICLE)\s+([IVX\d]+)',
            r'(Section|SECTION)\s+(\d+(\.\d+)*)',
            r'clause\s+(\d+(\.\d+)*)',
            r'第(.+?)条',  # Chinese
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ref_text = match.group(0)
                # Try to find matching clause
                for clause in all_clauses:
                    if ref_text.lower() in clause.text.lower()[:100]:  # Check beginning of clause
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

        return self
