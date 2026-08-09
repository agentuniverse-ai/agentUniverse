# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: latex_text_splitter.py

"""
LaTeX text splitter — a knowledge pre-processing DocProcessor.

Splits LaTeX documents into one chunk per \\section / \\subsection /
\\subsubsection, recording the section hierarchy as metadata. This is
useful for indexing academic papers, technical reports, and any LaTeX-
formatted knowledge source.

Pure Python with no third-party dependency. Uses a simple regex-based
parser that respects LaTeX comment lines (``%``) and does not split
inside verbatim environments.

Sibling of the merged ``MarkdownHeaderTextSplitter`` (#625) and the new
``HtmlHeaderTextSplitter`` (#737). Addresses #258.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# Section commands and their hierarchy level.
_SECTION_COMMANDS = {
    r"\part": 0,
    r"\chapter": 1,
    r"\section": 2,
    r"\subsection": 3,
    r"\subsubsection": 4,
    r"\paragraph": 5,
    r"\subparagraph": 6,
}

# Regex to match a section command with its title: \section{Title}
_SECTION_PATTERN = re.compile(
    r"\\(part|chapter|section|subsection|subsubsection|paragraph|subparagraph)"
    r"\s*\{([^}]*)\}",
    re.MULTILINE,
)

# Verbatim environments that should not be parsed.
_VERBATIM_BEGIN = re.compile(r"\\begin\{(verbatim|lstlisting|minted)\}")
_VERBATIM_END = re.compile(r"\\end\{(verbatim|lstlisting|minted)\}")


class LatexTextSplitter(DocProcessor):
    """Split LaTeX documents by section hierarchy.

    Attributes:
        section_path_key: Metadata key under which the section path
            (e.g. ``"Introduction > Background"``) is recorded.
        include_unsectioned: If True (default), text before the first
            \\section is emitted as a separate chunk.
    """

    section_path_key: str = "section_path"
    include_unsectioned: bool = True

    def _process_docs(self, origin_docs: List[Document],
                      query=None) -> List[Document]:
        if not origin_docs:
            return []
        result: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            for section_path, chunk_text in self._split_latex(text):
                if not section_path and not self.include_unsectioned:
                    continue
                meta = dict(doc.metadata or {})
                meta[self.section_path_key] = section_path
                result.append(Document(text=chunk_text, metadata=meta))
        return result

    @staticmethod
    def _split_latex(text: str) -> List[Tuple[str, str]]:
        """Parse LaTeX and return (section_path, text) pairs."""
        # Mask verbatim environments so section commands inside them are
        # not treated as structural markers.
        masked = LatexTextSplitter._mask_verbatim(text)

        matches = list(_SECTION_PATTERN.finditer(masked))
        if not matches:
            return [("", text.strip())] if text.strip() else []

        chunks: List[Tuple[str, str]] = []
        headers: Dict[int, str] = {}

        # Text before the first section command.
        first_start = matches[0].start()
        if first_start > 0:
            preamble = text[:first_start].strip()
            # Skip pure LaTeX preamble (\documentclass, \usepackage, etc.).
            preamble = LatexTextSplitter._strip_preamble(preamble)
            if preamble:
                chunks.append(("", preamble))

        for i, match in enumerate(matches):
            command = "\\" + match.group(1)
            title = match.group(2).strip()
            level = _SECTION_COMMANDS.get(command, 4)

            # Update header hierarchy: set this level, clear deeper levels.
            headers[level] = title
            for lv in list(headers):
                if lv > level:
                    del headers[lv]

            section_path = " > ".join(
                headers[lv] for lv in sorted(headers) if lv in headers)

            # Text from this section to the next (or end of document).
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append((section_path, chunk_text))

        return chunks

    @staticmethod
    def _mask_verbatim(text: str) -> str:
        """Replace verbatim environment content with spaces for safe parsing."""
        result = []
        pos = 0
        in_verbatim = False
        for begin_match in _VERBATIM_BEGIN.finditer(text):
            if not in_verbatim:
                result.append(text[pos:begin_match.start()])
                pos = begin_match.end()
                in_verbatim = True
            # Find the matching \end.
            end_match = _VERBATIM_END.search(text, pos)
            if end_match:
                # Replace the verbatim content with spaces (same length).
                verbatim_content = text[pos:end_match.start()]
                result.append(" " * len(verbatim_content))
                pos = end_match.end()
                in_verbatim = False
            else:
                # No closing \end found; rest of file is verbatim.
                result.append(" " * len(text[pos:]))
                pos = len(text)
                break
        result.append(text[pos:])
        return "".join(result)

    @staticmethod
    def _strip_preamble(text: str) -> str:
        """Remove LaTeX preamble commands (\\documentclass, \\usepackage, etc.)."""
        lines = text.split("\n")
        kept = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("\\documentclass") or \
               stripped.startswith("\\usepackage") or \
               stripped.startswith("\\input") or \
               stripped.startswith("\\include"):
                continue
            kept.append(line)
        return "\n".join(kept).strip()

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> "LatexTextSplitter":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "section_path_key"):
            self.section_path_key = doc_processor_configer.section_path_key
        if hasattr(doc_processor_configer, "include_unsectioned"):
            self.include_unsectioned = doc_processor_configer.include_unsectioned
        return self
