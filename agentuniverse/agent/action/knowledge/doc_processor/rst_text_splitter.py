# !/usr/bin/env python3

# @Time    : 2026/10/06
# @FileName: rst_text_splitter.py

"""
reStructuredText splitter — a knowledge pre-processing DocProcessor.

Splits each input :class:`Document` into one chunk per reStructuredText
(reST) section title, recording the section hierarchy (e.g.
``"Installation > macOS"``) as chunk metadata so a retrieved chunk can be
traced back to the part of the document it came from. This is the right
splitter for Python docstrings rendered as reST, Sphinx project docs,
PEP-style documents, and any ``.rst`` knowledge source.

reST marks titles with an *adornment*: a line of punctuation drawn under
the title text (``====``, ``----``, ``~~~~`` ...) or over and under it. A
document defines its own hierarchy: the first adornment character seen is
level 1, the next *new* character is one level deeper, and a character
reused later keeps its original level — the level-assignment rule used by
docutils. The splitter reproduces that rule with a pure-Python line
scanner and no third-party dependency.

Sibling of ``MarkdownHeaderTextSplitter`` and ``LatexTextSplitter``;
addresses #258 (knowledge pre-processing components).

Parsing is deliberately conservative, so ordinary text is not mistaken
for structure:

- a title must be preceded by a blank line (or start of document), as
  docutils requires;
- the adornment run must be at least as long as the title text, so a
  paragraph followed by a two-dash signature marker stays a paragraph;
- a lone punctuation line between blank lines is a *transition* and is
  kept as content;
- titles inside literal blocks (indented text following a ``::`` line)
  and inside comment/directive blocks (lines starting with ``..``) are
  treated as content.

It only separates on titles; a section that is still larger than desired
should be chained with a character / token splitter afterwards (splitter
processors compose — the output list is a valid input to the next one).
"""

import re

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Adornment characters allowed by docutils: the printable, non-alphanumeric,
# non-whitespace ASCII characters.
_ADORNMENT_CHARS = frozenset("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")

# A comment or directive opens with ``..`` at column 0 and its body stays
# indented beneath it.
_DIRECTIVE_RE = re.compile(r"^\.\.($|\s)")

# A literal block opens with a paragraph line ending in ``::`` and its
# body stays indented beneath it.
_LITERAL_MARKER_RE = re.compile(r"::\s*$")


def _is_blank(line: str) -> bool:
    """True when the line carries no content."""
    return not line.strip()


def _is_adornment(line: str) -> tuple[str, int] | None:
    """Return ``(char, run_length)`` when ``line`` is an adornment line.

    An adornment line repeats a single punctuation character at least
    once, optionally surrounded by whitespace. Any other line (including
    blank lines and mixed runs such as ``--==``) returns ``None``.
    """
    stripped = line.strip()
    if not stripped or stripped[0] not in _ADORNMENT_CHARS:
        return None
    if any(ch != stripped[0] for ch in stripped):
        return None
    return stripped[0], len(stripped)


class RstTextSplitter(DocProcessor):
    """Split reStructuredText documents by their section title hierarchy.

    Attributes:
        section_path_key (Optional[str]): Metadata key under which the
            joined section hierarchy of a chunk is recorded (e.g.
            ``"Usage > CLI"``). Set to ``None`` to omit the field.
        max_depth (Optional[int]): Deepest section level to split on
            (level 1 is the document's first adornment style). Titles
            deeper than this are kept as ordinary content of their parent
            section. ``None`` (default) splits on every level.
        keep_preamble (bool): When True, content before the first section
            title is emitted as its own chunk (with an empty section
            path); when False it is dropped.
    """

    section_path_key: str | None = "section_path"
    max_depth: int | None = None
    keep_preamble: bool = True

    def _process_docs(self, origin_docs: list[Document],
                      query: Query = None) -> list[Document]:
        """Split each document into title-delimited sections.

        Args:
            origin_docs (List[Document]): Documents whose ``text`` is
                parsed as reStructuredText. Each document's existing
                metadata is preserved on the emitted chunks.
            query (Query, optional): Unused; kept for interface
                compatibility.

        Returns:
            List[Document]: One document per non-empty section, each
            carrying its section hierarchy under ``section_path_key``
            (when configured). An empty input yields an empty list.
        """
        if not origin_docs:
            return []
        chunks: list[Document] = []
        for doc in origin_docs:
            base_meta = dict(doc.metadata or {})
            for text, section_path in self._split_rst(doc.text or ""):
                if not section_path and not self.keep_preamble:
                    continue
                metadata = dict(base_meta)
                if self.section_path_key:
                    metadata[self.section_path_key] = section_path
                chunks.append(Document(text=text, metadata=metadata))
        return chunks

    # ------------------------------------------------------------------ #
    # Splitting (pure) — fully testable without a network
    # ------------------------------------------------------------------ #

    def _split_rst(self, text: str) -> list[tuple[str, str]]:
        """Return ``(chunk_text, section_path)`` pairs for one document."""
        lines = text.splitlines()
        levels: dict[str, int] = {}    # adornment char -> assigned level
        sections: dict[int, str] = {}  # current open section title per level
        buffer: list[str] = []         # lines of the section being collected
        chunks: list[tuple[str, str]] = []

        def level_for(char: str) -> int:
            # docutils rule: a new adornment character opens one level
            # deeper than any character seen so far; a reused character
            # keeps the level it was first assigned.
            if char not in levels:
                levels[char] = len(levels) + 1
            return levels[char]

        def flush() -> None:
            body = "\n".join(buffer).strip("\n")
            buffer.clear()
            if not body:
                return
            chunks.append((body, self._section_path(sections)))

        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]

            # Comment / directive / literal blocks: every line of the
            # indented body is content, so titles inside them (code
            # samples in a literal block, headings in an included file)
            # are never mistaken for structure.
            if self._opens_indented_block(line):
                buffer.append(line)
                i += 1
                while i < n and (not lines[i] or lines[i][0] in " \t"):
                    buffer.append(lines[i])
                    i += 1
                continue

            # A title must be preceded by a blank line (or the document
            # start); a "title" directly after a paragraph line is really
            # just paragraph text (e.g. an e-mail signature marker).
            preceded_by_blank = (i == 0) or _is_blank(lines[i - 1])
            title = self._match_title(lines, i) if preceded_by_blank else None
            if title is not None:
                consumed, char, name = title
                level = level_for(char)
                if self.max_depth is not None and level > self.max_depth:
                    # Deeper than configured: the title and its adornment
                    # lines stay ordinary content of the parent section.
                    buffer.extend(lines[i:i + consumed])
                else:
                    flush()
                    self._push_section(sections, level, name)
                i += consumed
                continue

            buffer.append(line)
            i += 1

        flush()
        return chunks

    @staticmethod
    def _match_title(lines: list[str], i: int) -> tuple[int, str, str] | None:
        """Match a section title starting at ``lines[i]``.

        Returns ``(lines_consumed, adornment_char, title)`` or ``None``
        when ``lines[i]`` does not begin a title. Two reST title styles
        are recognised:

        - underline: ``Title`` followed by an adornment line at least as
          long as the title;
        - overline+underline: an adornment line, the title, then a
          matching adornment line, each at least as long as the title.
        """
        over = _is_adornment(lines[i])
        if over is not None:
            # Overline style needs two more lines: title and underline.
            if i + 2 < len(lines):
                candidate = lines[i + 1]
                under = _is_adornment(lines[i + 2])
                if (not _is_blank(candidate)
                        and _is_adornment(candidate) is None
                        and under is not None
                        and under[0] == over[0]
                        and over[1] >= len(candidate.strip())
                        and under[1] >= len(candidate.strip())):
                    return 3, over[0], candidate.strip()
            return None

        line = lines[i]
        if _is_blank(line) or _is_adornment(line) is not None:
            # A blank line or a lone adornment here is a transition (or
            # padding), never a title.
            return None
        if i + 1 >= len(lines):
            return None
        under = _is_adornment(lines[i + 1])
        if under is not None and under[1] >= len(line.strip()):
            return 2, under[0], line.strip()
        return None

    @staticmethod
    def _push_section(sections: dict[int, str], level: int, title: str) -> None:
        """Open the section at ``level`` and close any deeper open sections."""
        for deeper in [lvl for lvl in sections if lvl >= level]:
            del sections[deeper]
        sections[level] = title

    @staticmethod
    def _section_path(sections: dict[int, str]) -> str:
        """Join the open sections from shallowest to deepest."""
        if not sections:
            return ""
        return " > ".join(sections[lvl] for lvl in sorted(sections))

    @staticmethod
    def _opens_indented_block(line: str) -> bool:
        """True when ``line`` opens a block whose lines are all content.

        Two constructs are recognised: comment / directive blocks opening
        with ``..`` at column 0, and a literal-block marker — a paragraph
        line ending in ``::`` — whose body is the indented block that
        follows.
        """
        return bool(_DIRECTIVE_RE.match(line) or _LITERAL_MARKER_RE.search(line))

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> 'RstTextSplitter':
        """Initialize the splitter from its component config."""
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "section_path_key"):
            self.section_path_key = doc_processor_configer.section_path_key
        if hasattr(doc_processor_configer, "max_depth"):
            self.max_depth = doc_processor_configer.max_depth
        if hasattr(doc_processor_configer, "keep_preamble"):
            self.keep_preamble = doc_processor_configer.keep_preamble
        return self
