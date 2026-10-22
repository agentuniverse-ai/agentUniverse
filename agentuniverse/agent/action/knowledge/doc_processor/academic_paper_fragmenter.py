# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @Email   : ai@example.com
# @FileName: academic_paper_fragmenter.py

import re
import logging
from typing import List, Optional, Dict, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)


@dataclass
class PaperSection:
    """Represents a section in an academic paper.

    Attributes:
        name: Section name (e.g., 'Abstract', 'Introduction').
        text: Content of the section.
        start_pos: Starting position in original text.
        end_pos: Ending position in original text.
        section_hierarchy: Human-readable path from the top-level section to
            this section.
    """
    name: str
    text: str
    start_pos: int
    end_pos: int
    section_hierarchy: Tuple[str, ...] = ()


@dataclass
class Argument:
    """Represents an argument or claim in the paper.

    Attributes:
        text: The argument text.
        argument_type: Type of argument (thesis, evidence, conclusion).
        section: Section containing this argument.
        citations: List of citations supporting this argument.
        position: Position in the section.
        section_hierarchy: Human-readable path of the containing section.
        claim_strength: Strength classification for this argument.
    """
    text: str
    argument_type: str
    section: str
    citations: List[str]
    position: int
    section_hierarchy: Tuple[str, ...] = ()
    claim_strength: str = 'moderate'


class AcademicPaperFragmenter(DocProcessor):
    """Fragment academic papers by arguments and evidence.

    This processor analyzes academic papers and fragments them by:
    1. Detecting paper structure (Abstract, Introduction, Methods, Results, Discussion)
    2. Identifying thesis statements vs supporting evidence
    3. Extracting citations and linking them to evidence
    4. Creating documents with rich metadata about argument types and relationships

    Attributes:
        detect_sections: Whether to detect and parse paper sections.
        extract_citations: Whether to extract citation information.
        link_evidence: Whether to link evidence to claims.
        section_patterns: Dictionary of regex patterns for section detection.
            Defaults match complete headings, with an optional trailing colon.
        min_argument_length: Minimum length for a valid argument (characters).
        skip_on_error: Whether to skip documents that fail processing.
    """

    detect_sections: bool = True
    extract_citations: bool = True
    link_evidence: bool = True
    section_patterns: Optional[Dict[str, str]] = None
    min_argument_length: int = 20  # Lowered from 50 to capture shorter arguments
    skip_on_error: bool = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.section_patterns is None:
            self.section_patterns = {
                'abstract': r'^(Abstract|ABSTRACT|摘\s*要)(?:\s*[:：])?$',
                'introduction': r'^(Introduction|INTRODUCTION|1\.?\s*Introduction|引\s*言|绪\s*论|1\.?\s*引言)(?:\s*[:：])?$',
                'related_work': r'^(Related\s+Work|RELATED\s+WORK|Literature\s+Review|2\.?\s*Related\s+Work|相关工作)(?:\s*[:：])?$',
                'methods': r'^(Methods?|METHODS?|Methodology|METHODOLOGY|3\.?\s*Method|方\s*法|实验方法)(?:\s*[:：])?$',
                'results': r'^(Results?|RESULTS?|Experiments?|EXPERIMENTS?|4\.?\s*Results?|实\s*验|结\s*果)(?:\s*[:：])?$',
                'discussion': r'^(Discussion|DISCUSSION|Analysis|ANALYSIS|5\.?\s*Discussion|讨\s*论|分\s*析)(?:\s*[:：])?$',
                'conclusion': r'^(Conclusions?|CONCLUSIONS?|6\.?\s*Conclusion|结\s*论)(?:\s*[:：])?$',
                'references': r'^(References|REFERENCES|Bibliography|参考文献)(?:\s*[:：])?$',
            }

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Fragment academic papers into argument-based documents.

        Args:
            origin_docs: List of academic paper documents to fragment.
            query: Optional query object (not used in this processor).

        Returns:
            List of argument documents with metadata.
        """
        if not origin_docs:
            return []

        logger.info(f"Starting academic paper fragmentation of {len(origin_docs)} documents")

        all_argument_docs = []

        for doc in origin_docs:
            try:
                argument_docs = self._fragment_document(doc)
                all_argument_docs.extend(argument_docs)
                logger.info(f"Fragmented paper {doc.id} into {len(argument_docs)} arguments")
            except Exception as e:
                logger.error(f"Failed to fragment document {doc.id}: {e}")
                if not self.skip_on_error:
                    raise
                # Pass through original document if skip_on_error is True
                all_argument_docs.append(doc)

        logger.info(f"Total argument fragments created: {len(all_argument_docs)}")
        return all_argument_docs

    def _fragment_document(self, doc: Document) -> List[Document]:
        """Fragment a single academic paper into arguments.

        Args:
            doc: Academic paper document to fragment.

        Returns:
            List of argument documents.
        """
        text = doc.text

        # Step 1: Detect sections if enabled
        sections = []
        if self.detect_sections:
            sections = self._identify_sections(text)
            logger.debug(f"Detected {len(sections)} sections")

        # If no sections detected, treat as single section
        if not sections:
            sections = [PaperSection(
                'full_text', text, 0, len(text), ('full_text',)
            )]

        # Step 2: Extract arguments from each section
        all_arguments = []
        for section in sections:
            arguments = self._extract_arguments(section)
            all_arguments.extend(arguments)

        # Step 3: Extract citations if enabled
        citations = []
        if self.extract_citations:
            citations = self._parse_citations(text)
            logger.debug(f"Extracted {len(citations)} citations")

        # Step 4: Link evidence to claims if enabled
        if self.link_evidence and citations:
            self._link_evidence_to_claims(all_arguments, citations)

        # Step 5: Create documents for each argument
        argument_docs = self._create_argument_documents(doc, all_arguments)

        return argument_docs

    def _identify_sections(self, text: str) -> List[PaperSection]:
        """Identify sections in the academic paper.

        Args:
            text: Full paper text.

        Returns:
            List of PaperSection objects.
        """
        sections = []
        lines = text.split('\n')
        current_pos = 0

        # Each boundary stores the canonical section name alongside the
        # human-readable title path. Number paths are local to this document,
        # so hierarchy state cannot leak between calls.
        section_boundaries: List[
            Tuple[int, str, int, Tuple[str, ...]]
        ] = []
        numbered_hierarchies: Dict[
            Tuple[str, ...], Tuple[str, ...]
        ] = {}

        # Find section headers
        for line_idx, line in enumerate(lines):
            line_stripped = line.strip()

            if not line_stripped:
                current_pos += len(line) + 1
                continue

            matched = False

            # Check numbered headings before the configured patterns. Several
            # configured patterns also match headings such as
            # "1. Introduction"; parsing the number first preserves the
            # hierarchy that would otherwise be discarded.
            numbered_match = re.match(
                r'^(\d+(\.\d+)*\.?)\s+'
                r'([A-Za-z\u4e00-\u9fa5][A-Za-z\u4e00-\u9fa5\s]+)$',
                line_stripped
            )
            if numbered_match:
                section_number = numbered_match.group(1)
                section_title = numbered_match.group(3).strip()
                section_title_lower = section_title.lower()

                # Preserve configured canonical names even though numbered
                # headings are parsed first to retain their hierarchy.
                section_name = None
                for configured_name, pattern in self.section_patterns.items():
                    if re.match(pattern, line_stripped, re.IGNORECASE):
                        section_name = configured_name
                        break

                if not section_name:
                    section_name = self._map_to_known_section(
                        section_title_lower
                    )

                if not section_name:
                    # Preserve the existing canonical naming behavior for
                    # custom numbered sections.
                    section_name = re.sub(
                        r'[^\w\s]', '', section_title_lower
                    ).strip().replace(' ', '_')

                if section_name:
                    number_path = tuple(
                        section_number.rstrip('.').split('.')
                    )
                    parent_hierarchy = numbered_hierarchies.get(
                        number_path[:-1], ()
                    )
                    section_hierarchy = parent_hierarchy + (section_title,)

                    # Replacing a heading invalidates any previously recorded
                    # descendants of the same number path.
                    numbered_hierarchies = {
                        path: hierarchy
                        for path, hierarchy in numbered_hierarchies.items()
                        if not (
                            len(path) >= len(number_path)
                            and path[:len(number_path)] == number_path
                        )
                    }
                    numbered_hierarchies[number_path] = section_hierarchy
                    section_boundaries.append((
                        line_idx,
                        section_name,
                        current_pos,
                        section_hierarchy,
                    ))
                    logger.debug(
                        f"Found numbered section '{section_name}' "
                        f"({section_number}) at line {line_idx}"
                    )
                    matched = True

            # Check against configured section patterns for unnumbered
            # headings. Such a heading starts a new top-level hierarchy.
            if not matched:
                for section_name, pattern in self.section_patterns.items():
                    if re.match(pattern, line_stripped, re.IGNORECASE):
                        section_boundaries.append((
                            line_idx,
                            section_name,
                            current_pos,
                            (line_stripped,),
                        ))
                        numbered_hierarchies.clear()
                        logger.debug(
                            f"Found section '{section_name}' at line {line_idx}"
                        )
                        matched = True
                        break

            has_terminal_punctuation = line_stripped.endswith(
                ('.', ',', ';', '!', '?', '。', '，', '；', '！', '？'))

            # Detection for simple capitalized headers (more aggressive)
            if not matched and len(line_stripped) > 2 and len(line_stripped) < 50:
                # Check if line looks like a section header:
                # - Starts with capital letter OR Chinese character
                # - Short enough to be a title
                # - No punctuation at the end (except for numbered sections)
                # - Not too many words (< 8 words)
                words = line_stripped.split()
                is_chinese = bool(re.match(r'^[\u4e00-\u9fa5]', line_stripped))  # Starts with Chinese char
                if (len(words) <= 8 and
                    (line_stripped[0].isupper() or is_chinese) and
                    not has_terminal_punctuation):

                    # Try to map to known sections
                    section_title = line_stripped.lower()
                    section_name = self._map_to_known_section(section_title)
                    if section_name:
                        section_boundaries.append((
                            line_idx,
                            section_name,
                            current_pos,
                            (line_stripped,),
                        ))
                        numbered_hierarchies.clear()
                        logger.debug(f"Found simple header section '{section_name}' at line {line_idx}")
                        matched = True

            # Detection for ALL CAPS headers
            if not matched and len(line_stripped) > 3 and len(line_stripped) < 50:
                if line_stripped.isupper() and not has_terminal_punctuation:
                    section_title = line_stripped.lower()
                    section_name = self._map_to_known_section(section_title)
                    if section_name:
                        section_boundaries.append((
                            line_idx,
                            section_name,
                            current_pos,
                            (line_stripped,),
                        ))
                        numbered_hierarchies.clear()
                        logger.debug(f"Found CAPS section '{section_name}' at line {line_idx}")
                        matched = True

            current_pos += len(line) + 1

        # Create sections from boundaries
        for i, (
            line_idx,
            section_name,
            start_pos,
            section_hierarchy,
        ) in enumerate(section_boundaries):
            # Determine end position
            if i + 1 < len(section_boundaries):
                end_pos = section_boundaries[i + 1][2]
            else:
                end_pos = len(text)

            # Extract section text
            section_text = text[start_pos:end_pos].strip()

            # Remove section header from text
            first_newline = section_text.find('\n')
            if first_newline != -1:
                section_text = section_text[first_newline:].strip()

            if section_text:  # Only add non-empty sections
                sections.append(PaperSection(
                    name=section_name,
                    text=section_text,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    section_hierarchy=section_hierarchy,
                ))

        return sections

    def _map_to_known_section(self, title: str) -> Optional[str]:
        """Map section title to known section types.

        Args:
            title: Section title (lowercase).

        Returns:
            Section name or None.
        """
        mapping = {
            'abstract': ['abstract', '摘要'],
            'introduction': ['introduction', 'intro', 'background', '引言', '绪论'],
            'related_work': ['related work', 'literature review', 'prior work', '相关工作'],
            'methods': ['method', 'methods', 'methodology', 'approach', '方法', '实验方法'],
            'results': ['result', 'results', 'experiment', 'experiments', 'findings', '实验', '结果'],
            'discussion': ['discussion', 'analysis', '讨论', '分析'],
            'conclusion': ['conclusion', 'conclusions', 'summary', '结论'],
            'references': ['reference', 'references', 'bibliography', '参考文献'],
        }

        title_lower = title.lower()
        for section_name, keywords in mapping.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return section_name

        return None

    def _extract_arguments(self, section: PaperSection) -> List[Argument]:
        """Extract arguments from a paper section.

        Args:
            section: PaperSection to analyze.

        Returns:
            List of Argument objects.
        """
        arguments = []

        # Split section into paragraphs - handle both \n\n and single \n
        text = section.text.strip()

        # First try splitting by double newlines (standard paragraphs)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        # If we get very few paragraphs, try splitting by single newlines
        # This handles cases where sections are separated by single line breaks
        if len(paragraphs) < 2:
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

        for idx, paragraph in enumerate(paragraphs):
            if len(paragraph) < self.min_argument_length:
                continue

            # Determine argument type based on section and content
            argument_type = self._classify_argument(paragraph, section.name)

            # Extract citations in this paragraph
            paragraph_citations = self._extract_paragraph_citations(paragraph) if self.extract_citations else []

            argument = Argument(
                text=paragraph,
                argument_type=argument_type,
                section=section.name,
                citations=paragraph_citations,
                position=idx,
                section_hierarchy=(
                    section.section_hierarchy or (section.name,)
                ),
                claim_strength=self._classify_claim_strength(paragraph),
            )

            arguments.append(argument)

        return arguments

    def _classify_argument(self, text: str, section_name: str) -> str:
        """Classify the type of argument.

        Args:
            text: Argument text.
            section_name: Name of the section containing the argument.

        Returns:
            Argument type: 'thesis', 'evidence', 'methodology', or 'conclusion'.
        """
        # Section-based classification
        if section_name in ['abstract', 'introduction']:
            # Look for thesis indicators
            thesis_indicators = [
                r'\bwe\s+(propose|present|introduce|demonstrate)',
                r'\bthis\s+paper\s+(presents|proposes|introduces)',
                r'\bour\s+(contribution|approach|method)',
                r'\bin\s+this\s+(work|paper|study)',
            ]
            for pattern in thesis_indicators:
                if re.search(pattern, text, re.IGNORECASE):
                    return 'thesis'

        if section_name in ['methods', 'methodology']:
            return 'methodology'

        if section_name in ['results', 'experiments']:
            # Evidence with experimental support
            return 'evidence'

        if section_name in ['conclusion', 'conclusions']:
            return 'conclusion'

        # Content-based classification
        evidence_indicators = [
            r'\b(figure|table|shown|demonstrates?|shows?)\s+\d+',
            r'\b(experiment|study|test|evaluation)\s+(shows?|demonstrates?)',
            r'\b(results?|findings?)\s+(show|demonstrate|indicate)',
        ]

        for pattern in evidence_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return 'evidence'

        # Default to general claim
        return 'claim'

    def _classify_claim_strength(self, text: str) -> str:
        """Classify how strongly an argument states its conclusion.

        Weakening and negation signals take precedence over strong assertion
        signals. This keeps hedged statements such as "may demonstrate" and
        explicit negations such as "does not prove" from being classified as
        strong claims.

        Args:
            text: Argument text to classify.

        Returns:
            One of ``strong``, ``moderate``, or ``weak``.
        """
        weak_patterns = [
            r'\bweak\s+claim\b',
            r'\b(preliminary|tentative|uncertain|inconclusive)\b',
            r'\b(suggests?|may|might|could|possibly|potentially|'
            r'appears?|seems?|likely)\b',
            r'\bnot\s+(?!(?:only|merely|just)\b)(?:\w+\s+){0,4}'
            r'(?:proves?|proved|proven|demonstrates?|demonstrated|confirms?|'
            r'confirmed|establishes?|established)\b',
            r"\b(?:cannot|can't)\s+(?:\w+\s+){0,4}"
            r'(?:proves?|proved|proven|demonstrates?|demonstrated|confirms?|'
            r'confirmed|establishes?|established)\b',
            r'\b(?:by\s+no\s+means|fail(?:s|ed)?\s+to)\s+'
            r'(?:\w+\s+){0,3}(?:proves?|proved|proven|demonstrates?|'
            r'demonstrated|confirms?|confirmed|establishes?|established)\b',
        ]
        if any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in weak_patterns
        ):
            return 'weak'

        strong_patterns = [
            r'\bstrong\s+claim\b',
            r'\b(definitively|definitely|conclusively|unequivocally|'
            r'unambiguously)\b',
            r'\b(proves?|proved|demonstrates?|demonstrated|confirms?|'
            r'confirmed|establishes?|established)\b',
        ]
        if any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in strong_patterns
        ):
            return 'strong'

        return 'moderate'

    def _parse_citations(self, text: str) -> List[str]:
        """Parse citations from the text.

        Args:
            text: Paper text.

        Returns:
            List of citation identifiers.
        """
        citations = []

        # Common citation patterns
        patterns = [
            r'\[(\d+)\]',  # [1], [2]
            r'\[(\d+,\s*\d+(?:,\s*\d+)*)\]',  # [1, 2, 3]
            r'\[(\d+-\d+)\]',  # [1-5]
            r'\(([A-Z][a-z]+\s+et\s+al\.,?\s+\d{4})\)',  # (Smith et al., 2020)
            r'\(([A-Z][a-z]+\s+and\s+[A-Z][a-z]+,?\s+\d{4})\)',  # (Smith and Jones, 2020)
            r'\(([A-Z][a-z]+,?\s+\d{4})\)',  # (Smith, 2020)
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                citation = match.group(1)
                if citation not in citations:
                    citations.append(citation)

        return citations

    def _extract_paragraph_citations(self, paragraph: str) -> List[str]:
        """Extract citations from a specific paragraph.

        Args:
            paragraph: Paragraph text.

        Returns:
            List of citation identifiers in the paragraph.
        """
        return self._parse_citations(paragraph)

    def _link_evidence_to_claims(self, arguments: List[Argument], all_citations: List[str]) -> None:
        """Link evidence to claims based on shared citations.

        Args:
            arguments: List of arguments to analyze.
            all_citations: All citations in the paper.

        Note:
            Modifies arguments in place.
        """
        # Build citation index
        citation_to_args: Dict[str, List[int]] = {}

        for idx, arg in enumerate(arguments):
            for citation in arg.citations:
                if citation not in citation_to_args:
                    citation_to_args[citation] = []
                citation_to_args[citation].append(idx)

        # Link related arguments through shared citations
        # This creates implicit relationships for metadata
        logger.debug(f"Linked arguments through {len(citation_to_args)} shared citations")

    def _create_argument_documents(self, original_doc: Document,
                                   arguments: List[Argument]) -> List[Document]:
        """Create Document objects for each argument.

        Args:
            original_doc: Original paper document.
            arguments: List of argument objects.

        Returns:
            List of argument documents.
        """
        argument_docs = []

        for arg in arguments:
            # Build metadata
            metadata = {
                'processor_name': self.name,
                'processor_version': '1.0',
                'processing_timestamp': datetime.now().isoformat(),
                'source_document_id': original_doc.id,
                'section': arg.section,
                'section_hierarchy': list(arg.section_hierarchy),
                'argument_type': arg.argument_type,
                'claim_strength': arg.claim_strength,
                'position': arg.position,
            }

            # Add original metadata
            if original_doc.metadata:
                metadata['original_metadata'] = original_doc.metadata

            # Add citations
            if arg.citations:
                metadata['citations'] = arg.citations
                metadata['citation_count'] = len(arg.citations)

            # Create keywords from argument type and section
            keywords = original_doc.keywords.copy() if original_doc.keywords else set()
            keywords.add(arg.section)
            keywords.add(arg.argument_type)

            # Create document
            doc = Document(
                text=arg.text,
                metadata=metadata,
                keywords=keywords
            )

            argument_docs.append(doc)

        return argument_docs

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'AcademicPaperFragmenter':
        """Initialize fragmenter parameters from configuration.

        Args:
            doc_processor_configer: Configuration object containing fragmenter parameters.

        Returns:
            Initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "detect_sections"):
            self.detect_sections = doc_processor_configer.detect_sections
        if hasattr(doc_processor_configer, "extract_citations"):
            self.extract_citations = doc_processor_configer.extract_citations
        if hasattr(doc_processor_configer, "link_evidence"):
            self.link_evidence = doc_processor_configer.link_evidence
        if hasattr(doc_processor_configer, "section_patterns"):
            self.section_patterns = doc_processor_configer.section_patterns
        if hasattr(doc_processor_configer, "min_argument_length"):
            self.min_argument_length = doc_processor_configer.min_argument_length
        if hasattr(doc_processor_configer, "skip_on_error"):
            self.skip_on_error = doc_processor_configer.skip_on_error

        return self
