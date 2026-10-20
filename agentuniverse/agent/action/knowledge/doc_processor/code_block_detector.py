# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: code_block_detector.py

import re
from typing import List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# A fence opener is a maximal run of 3+ backticks or tildes, optionally
# indented by up to 3 spaces, captured together with the remainder of the
# line (the info string candidate).
_FENCE_RE = re.compile(r"^(`+|~+)(.*)$")
# Maximum number of fenced blocks allowed in a document.
_DEFAULT_MAX_BLOCKS = 50
# Placeholder template used when mask=True: the detected language and the
# block's line count are substituted for <lang> and <lines>.
_MASK_TEMPLATE = "\u27e6code:{language}:{lines}\u27e7"


class CodeBlockDetector(DocProcessor):
    """Locate fenced code blocks and stamp spans plus languages into metadata.

    Markdown-heavy corpora — README dumps, design docs, issue trackers,
    archived chat logs — carry large fenced code blocks. Downstream
    components mostly treat that code as noise: embedding models spend
    tokens on it, keyword extractors index identifier names, and splitters
    cut blocks into meaningless fragments. Existing pipeline pieces merely
    defend themselves (``OutlineExtractor`` and
    ``HeadingConsistencyChecker`` skip lines inside fences while parsing
    headings); none actually catalogs where the code lives. This processor
    fills that gap: it scans every document for CommonMark fenced code
    blocks and records each block's language, line span, size, indentation
    and closure state into document metadata, so later stages can decide —
    per block, with exact coordinates — what to mask, split around or drop
    before embedding.

    Fence recognition follows CommonMark: an opener is a line indented by
    at most 3 spaces whose remainder starts with a maximal run of 3 or
    more backticks or tildes; the rest of the line is the info string,
    whose first word (lowercased) is taken as the language (empty string
    when absent). A backtick fence may not carry backticks in its info
    string. A closing fence must be a line indented by at most 3 spaces
    consisting solely of the same fence character repeated at least as
    many times as the opener (trailing spaces allowed, no info text).
    Consequently a ````` fence does not close a `````` block and a tilde
    fence never closes a backtick fence — nested-looking fences simply
    remain content of the enclosing block. A fence left open runs to the
    end of the document and is reported with ``unclosed: true``.

    The scan is pure Python, deterministic and offline. Lines are counted
    by splitting on ``\\n`` (a trailing newline therefore yields one final
    empty line), spans are 1-based inclusive ``[first_line, last_line]``
    covering the fences themselves, and a block's ``line_count`` includes
    its fence lines. Aggregates cover every detected block even when the
    per-block list is capped: ``block_count``, ``total_code_lines``, a
    ``languages`` histogram ordered by descending count then language
    name, ``longest_block_lines`` and ``code_ratio`` (code lines divided
    by total lines, 0.0 for an empty document).

    With ``mask=True`` every block — capped ones included — is replaced in
    the document text by a single placeholder line of the form
    ``\u27e6code:python:12\u27e7`` (language, then line count). Because
    placeholders contain no fence characters, running the detector again
    over masked text finds no fences: masking is idempotent and a second
    pass is a no-op on the text.

    Attributes:
        mask: When true, replace each detected block in the document text
            with a ``\u27e6code:<lang>:<lines>\u27e7`` placeholder line.
            Default false (detect only, text untouched).
        max_blocks: Maximum number of per-block detail entries kept in the
            ``blocks`` list of the stamped metadata; must be >= 1. Blocks
            beyond the cap are still counted in every aggregate. Default 50.
        metadata_key: Metadata key the summary mapping is written to; an
            empty value disables stamping (useful for mask-only pipelines).
            Default ``code_blocks``.
    """

    mask: bool = False
    max_blocks: int = _DEFAULT_MAX_BLOCKS
    metadata_key: str = "code_blocks"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp code-block metadata into (and optionally mask) documents.

        Args:
            origin_docs: Documents to scan, in batch order. Every document
                is stamped and returned — detection never drops or
                reorders documents, it only annotates (and optionally
                masks) them in place.
            query: Query object (unused; detection depends only on the
                documents' own text).

        Returns:
            List[Document]: The same document list, each document carrying
            the code-block summary in ``metadata[metadata_key]`` and, when
            ``mask`` is true, block-free text.
        """
        for doc in origin_docs:
            lines = (doc.text or "").split("\n")
            blocks = self._scan(lines)
            if self.metadata_key:
                self._stamp(doc, self.metadata_key,
                            self._summarize(blocks, len(lines)))
            if self.mask:
                doc.text = self._mask(lines, blocks)
        return origin_docs

    # ------------------------------------------------------------------ #
    # Fence scanning
    # ------------------------------------------------------------------ #

    def _scan(self, lines: List[str]) -> List[dict]:
        """Find every fenced code block in the given lines.

        The scanner advances line by line; on an opener it consumes the
        whole block (through its closer, or to the end of the document
        when unclosed) before resuming, so fence-like lines inside a block
        are never mistaken for new openers.

        Args:
            lines: Document lines, as produced by ``str.split("\\n")``.

        Returns:
            List[dict]: One mapping per block with keys ``language``
            (first info-string word, lowercased; "" when absent),
            ``span`` (1-based inclusive [first, last] line numbers of the
            block including its fences), ``line_count`` (span length),
            ``unclosed`` (bool) and ``indent`` (leading spaces of the
            opener, 0-3), in document order.
        """
        blocks: List[dict] = []
        index = 0
        total = len(lines)
        while index < total:
            opener = self._opener(lines[index])
            if opener is None:
                index += 1
                continue
            char, length, language, indent = opener
            close = self._closer(lines, index + 1, char, length)
            # An unclosed fence runs to the end of the document per
            # CommonMark, so the block's last line is the final line
            # regardless of what follows the opener.
            last = close if close is not None else total - 1
            blocks.append({
                "language": language,
                "span": [index + 1, last + 1],
                "line_count": last - index + 1,
                "unclosed": close is None,
                "indent": indent,
            })
            index = last + 1
        return blocks

    @staticmethod
    def _opener(line: str):
        """Parse one line as a fence opener if it is one.

        Args:
            line: Candidate line.

        Returns:
            tuple | None: ``(fence_char, run_length, language, indent)``
            when the line opens a fence, else None. ``language`` is the
            lowercased first word of the info string ("" when the info
            string is empty or whitespace). Backtick openers whose info
            string contains a backtick are rejected per CommonMark.
        """
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if indent > 3:
            return None
        match = _FENCE_RE.match(stripped)
        if match is None:
            return None
        fence = match.group(1)
        if len(fence) < 3:
            return None
        info = match.group(2).strip()
        if fence[0] == "`" and "`" in info:
            return None
        language = info.split()[0].lower() if info else ""
        return fence[0], len(fence), language, indent

    @staticmethod
    def _closer(lines: List[str], start: int, char: str, length: int):
        """Find the closing fence line of a block opened at line ``start-1``.

        A closer must match the opener's fence character, repeat it at
        least ``length`` times, be indented by at most 3 spaces and carry
        nothing but optional trailing whitespace after the fence run.

        Args:
            lines: Document lines.
            start: First line index to examine (just past the opener).
            char: The opener's fence character (````` `` ``` ```` or ``~``).
            length: The opener's fence run length.

        Returns:
            int | None: Index of the closing line, or None when the fence
            stays open through the end of the document.
        """
        for index in range(start, len(lines)):
            stripped = lines[index].lstrip(" ")
            if len(lines[index]) - len(stripped) > 3:
                continue
            if not stripped.startswith(char):
                continue
            match = _FENCE_RE.match(stripped)
            run, rest = match.group(1), match.group(2)
            # At least as long as the opener, and nothing but whitespace
            # after the run — an info string disqualifies.
            if len(run) >= length and not rest.strip():
                return index
        return None

    # ------------------------------------------------------------------ #
    # Summarizing and masking
    # ------------------------------------------------------------------ #

    def _summarize(self, blocks: List[dict], line_total: int) -> dict:
        """Build the metadata summary over every detected block.

        Args:
            blocks: All detected blocks from ``_scan`` (uncapped).
            line_total: Total number of lines in the document.

        Returns:
            dict: Mapping with ``blocks`` (per-block details, capped at
            ``max_blocks``), ``block_count``, ``total_code_lines``,
            ``languages`` (histogram ordered by descending count then
            language name), ``longest_block_lines`` and ``code_ratio``.
        """
        histogram: dict = {}
        total_code_lines = 0
        longest = 0
        for block in blocks:
            histogram[block["language"]] = \
                histogram.get(block["language"], 0) + 1
            total_code_lines += block["line_count"]
            longest = max(longest, block["line_count"])
        return {
            "blocks": blocks[:self.max_blocks],
            "block_count": len(blocks),
            "total_code_lines": total_code_lines,
            "languages": dict(sorted(histogram.items(),
                                     key=lambda item: (-item[1], item[0]))),
            "longest_block_lines": longest,
            "code_ratio": (total_code_lines / line_total
                           if line_total else 0.0),
        }

    @staticmethod
    def _mask(lines: List[str], blocks: List[dict]) -> str:
        """Replace every detected block with a placeholder line.

        Blocks arrive in ascending, non-overlapping document order from
        ``_scan``, so a single pass stitching the untouched segments and
        one placeholder per block rebuilds the text exactly; everything
        outside blocks — including the trailing newline — is preserved.

        Args:
            lines: Document lines.
            blocks: All detected blocks (uncapped).

        Returns:
            str: The masked document text.
        """
        if not blocks:
            return "\n".join(lines)
        parts: List[str] = []
        cursor = 0
        for block in blocks:
            start, end = block["span"][0] - 1, block["span"][1] - 1
            if start > cursor:
                parts.extend(lines[cursor:start])
            parts.append(_MASK_TEMPLATE.format(
                language=block["language"],
                lines=block["line_count"]))
            cursor = end + 1
        parts.extend(lines[cursor:])
        return "\n".join(parts)

    @staticmethod
    def _stamp(doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping shared
        with other pipeline stages never observes surprising in-place edits.

        Args:
            doc: Document to stamp.
            key: Metadata key.
            value: Metadata value.
        """
        meta = dict(doc.metadata or {})
        meta[key] = value
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'CodeBlockDetector':
        """Initialize and validate the detector from component configuration.

        Validation happens eagerly at load time: a silently misconfigured
        detector (say, a block cap that discards details the pipeline
        relies on) would be far harder to notice than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            CodeBlockDetector: The initialized instance.

        Raises:
            ValueError: On an invalid parameter value or type.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "mask") and \
                doc_processor_configer.mask is not None:
            mask = doc_processor_configer.mask
            if not isinstance(mask, bool):
                raise ValueError("mask must be a boolean")
            self.mask = mask

        if hasattr(doc_processor_configer, "max_blocks") and \
                doc_processor_configer.max_blocks is not None:
            max_blocks = doc_processor_configer.max_blocks
            if isinstance(max_blocks, bool) or \
                    not isinstance(max_blocks, int):
                raise ValueError("max_blocks must be an integer")
            self.max_blocks = max_blocks
            if self.max_blocks < 1:
                raise ValueError("max_blocks must be >= 1")

        if hasattr(doc_processor_configer, "metadata_key") and \
                doc_processor_configer.metadata_key is not None:
            key = doc_processor_configer.metadata_key
            if not isinstance(key, str):
                raise ValueError("metadata_key must be a string")
            self.metadata_key = key

        return self
