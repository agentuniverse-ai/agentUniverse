#!/usr/bin/env python3
"""Zero-dependency Markdown formatting / beautifying tool."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import re
from typing import Any, Dict, List, Optional, Tuple

from agentuniverse.agent.action.tool.tool import Tool

# Placeholder sentinels used to shield code spans and fenced blocks from the
# text-level transforms. Control characters never occur in normal Markdown.
_PROTECT_TOKEN = "\x00MDBLOCK{}\x00"
_PROTECT_RE = re.compile("\x00MDBLOCK(\\d+)\x00")

# ATX heading: up to three leading spaces, 1-6 hashes, optional closing hashes.
_ATX_HEADING_RE = re.compile(r"^( {0,3})(#{1,6})([ \t]*)(.+?)[ \t]*#*[ \t]*$")
_LOOSE_HASHES_RE = re.compile(r"^( {0,3})(#{1,})([ \t]*)(\S.*?)[ \t]*#*[ \t]*$")

# List items: marker followed by whitespace (CommonMark requirement).
_UNORDERED_ITEM_RE = re.compile(r"^(\s*)([*+-])([ \t]+)(.*?)[ \t]*$")
_ORDERED_ITEM_RE = re.compile(r"^(\s*)(\d{1,9})([.)])([ \t]+)(.*?)[ \t]*$")

# GFM table separator row: pipes, dashes, colons, spaces only; >= 1 dash.
_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$")
_TABLE_ROW_HAS_PIPE_RE = re.compile(r"^[^\n]*\|")

# Inline spans and structural lines for the stats mode.
_INLINE_CODE_RE = re.compile(r"(`+)(?!`)(.+?)\1")
_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_BLOCKQUOTE_RE = re.compile(r"^\s{0,3}>\s?")
_THEMATIC_BREAK_RE = re.compile(r"^\s{0,3}(?:(?:\*\s*){3,}|(?:_\s*){3,}|(?:-\s*){3,})$")

_MODES = ("beautify", "normalize_headings", "fix_lists", "fix_tables", "stats")


class MarkdownBeautifyTool(Tool):
    """Format, normalize, and analyze Markdown text with pure-regex rules.

    Modes:

    * ``beautify`` — run the full pipeline: setext headings become ATX,
      heading levels are normalized (no skipped levels), trailing whitespace
      is stripped, blank lines are regularized, fenced code blocks are
      re-fenced with backticks, list markers are unified and ordered lists
      renumbered, and tables are column-aligned.
    * ``normalize_headings`` — convert setext to ATX headings and shift every
      level by ``heading_shift`` (positive demotes, negative promotes),
      clamped to levels 1-6.
    * ``fix_lists`` — unify unordered markers to ``list_marker`` (default
      ``-``) and optionally renumber ordered lists from 1 per list.
    * ``fix_tables`` — pad/truncate rows to the header width, rebuild every
      table with aligned columns and a normalized separator row.
    * ``stats`` — structural counts (headings per level, paragraphs, list
      items, tables, code blocks, links, images, blockquotes, …).

    The tool is deliberately dependency-free: everything is regular
    expressions and line scanning over the input string, so it runs in any
    environment without a Markdown library. Code blocks and inline code are
    protected from every transformation via placeholder substitution.

    Attributes:
        max_input_chars: Upper bound on accepted input length.
        default_list_marker: Marker used for unordered lists when the
            ``list_marker`` argument is not given; one of ``-``, ``*``, ``+``.
        default_ordered_delimiter: Delimiter after ordered-list numbers,
            ``.`` or ``)``.
    """

    max_input_chars: int = 1_000_000
    default_list_marker: str = "-"
    default_ordered_delimiter: str = "."

    def execute(
        self,
        mode: str = "beautify",
        markdown: str = "",
        heading_shift: int = 0,
        list_marker: Optional[str] = None,
        ordered_delimiter: Optional[str] = None,
        renumber_ordered: bool = True,
        **_: Any,
    ) -> Dict[str, Any]:
        """Run one Markdown operation and return a structured result.

        Args:
            mode: One of ``beautify``, ``normalize_headings``, ``fix_lists``,
                ``fix_tables``, ``stats``.
            markdown: The Markdown source text.
            heading_shift: Level shift for ``normalize_headings``; positive
                demotes (adds levels), negative promotes.
            list_marker: Unordered-list marker for ``fix_lists``; defaults to
                the tool's ``default_list_marker``.
            ordered_delimiter: ``.`` or ``)`` after ordered-list numbers.
            renumber_ordered: Renumber ordered lists starting at 1.

        Returns:
            Dict[str, Any]: ``{"status": "success", "mode": ..., ...}`` with
            ``markdown`` (transform modes) or ``stats`` (stats mode); errors
            come back as ``{"status": "error", ...}``.
        """
        try:
            operation = self._mode(mode)
            text = self._input(markdown)
            shift = self._shift(heading_shift)
            bullet = self._marker(list_marker or self.default_list_marker)
            delimiter = self._delimiter(
                ordered_delimiter or self.default_ordered_delimiter)

            if operation == "stats":
                return {"status": "success", "mode": operation,
                        "stats": self._stats(text)}

            result = self._dispatch(operation, text, shift, bullet,
                                    delimiter, renumber_ordered)
            return {
                "status": "success",
                "mode": operation,
                "markdown": result,
                "changed": result != text,
            }
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive boundary
            return self._error(mode, "operation_error",
                               f"Markdown operation failed: {exc}")

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> Dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message,
                "mode": mode}

    @staticmethod
    def _mode(mode: str) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        operation = mode.strip().lower()
        if operation not in _MODES:
            raise ValueError(
                f"mode must be one of {', '.join(_MODES)}, got: {mode!r}")
        return operation

    def _input(self, markdown: str) -> str:
        if markdown is None:
            markdown = ""
        if not isinstance(markdown, str):
            raise TypeError("markdown must be a string")
        if len(markdown) > self.max_input_chars:
            raise ValueError(
                f"markdown exceeds max_input_chars ({self.max_input_chars})")
        # Normalize line endings so Windows-authored documents flow through
        # the same line-based rules.
        return markdown.replace("\r\n", "\n").replace("\r", "\n")

    @staticmethod
    def _shift(heading_shift: int) -> int:
        if isinstance(heading_shift, bool) or not isinstance(heading_shift, int):
            raise TypeError("heading_shift must be an integer")
        if not -5 <= heading_shift <= 5:
            raise ValueError("heading_shift must be between -5 and 5")
        return heading_shift

    @staticmethod
    def _marker(marker: str) -> str:
        if marker not in ("-", "*", "+"):
            raise ValueError(f"list_marker must be '-', '*' or '+', "
                             f"got: {marker!r}")
        return marker

    @staticmethod
    def _delimiter(delimiter: str) -> str:
        if delimiter not in (".", ")"):
            raise ValueError(f"ordered_delimiter must be '.' or ')', "
                             f"got: {delimiter!r}")
        return delimiter

    # ------------------------------------------------------------------ #
    # Dispatch
    # ------------------------------------------------------------------ #

    def _dispatch(self, operation: str, text: str, shift: int, bullet: str,
                  delimiter: str, renumber: bool) -> str:
        if operation == "normalize_headings":
            protected, blocks = self._protect(text)
            return self._restore(
                self._normalize_headings(protected, shift), blocks)
        if operation == "fix_lists":
            protected, blocks = self._protect(text)
            return self._restore(
                self._fix_lists(protected, bullet, delimiter, renumber), blocks)
        if operation == "fix_tables":
            protected, blocks = self._protect(text)
            return self._restore(self._fix_tables(protected), blocks)
        return self._beautify(text, shift, bullet, delimiter, renumber)

    def _beautify(self, text: str, shift: int, bullet: str, delimiter: str,
                  renumber: bool) -> str:
        protected, blocks = self._protect(text)
        protected = self._normalize_headings(protected, shift, flatten=True)
        protected = self._fix_lists(protected, bullet, delimiter, renumber)
        protected = self._fix_tables(protected)
        protected = self._normalize_blank_lines(protected)
        return self._restore(protected, blocks)

    # ------------------------------------------------------------------ #
    # Code protection
    # ------------------------------------------------------------------ #

    def _protect(self, text: str) -> Tuple[str, List[str]]:
        """Replace fenced code blocks and inline code with placeholders.

        Fenced blocks are re-formatted while extracted: the fence becomes
        three backticks, the info string is trimmed and lowercased, and the
        body is preserved verbatim. Inline code spans are stored untouched.

        Args:
            text: Original Markdown.

        Returns:
            Tuple[str, List[str]]: Text with placeholder lines/spans plus the
            protected fragments, restore order preserved by index.
        """
        blocks: List[str] = []
        output: List[str] = []
        lines = text.split("\n")
        fence_re = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")
        i = 0
        while i < len(lines):
            line = lines[i]
            match = fence_re.match(line)
            if match and match.group(1).startswith("```"):
                # Opening backtick fence: scan to the closing fence.
                body: List[str] = []
                i += 1
                while i < len(lines) and not re.match(
                        r"^\s{0,3}`{3,}[ \t]*$", lines[i]):
                    body.append(lines[i])
                    i += 1
                i += 1  # consume the closing fence (or run off the end)
                info = match.group(2).strip().lower()
                blocks.append(f"```{info}\n" + "\n".join(body) + "\n```")
                output.append(_PROTECT_TOKEN.format(len(blocks) - 1))
                continue
            if match and match.group(1).startswith("~~~"):
                body = []
                i += 1
                while i < len(lines) and not re.match(
                        r"^\s{0,3}~{3,}[ \t]*$", lines[i]):
                    body.append(lines[i])
                    i += 1
                i += 1
                info = match.group(2).strip().lower()
                blocks.append(f"```{info}\n" + "\n".join(body) + "\n```")
                output.append(_PROTECT_TOKEN.format(len(blocks) - 1))
                continue
            output.append(self._protect_inline(line, blocks))
            i += 1
        return "\n".join(output), blocks

    @staticmethod
    def _protect_inline(line: str, blocks: List[str]) -> str:
        def _stash(match: "re.Match[str]") -> str:
            blocks.append(match.group(0))
            return _PROTECT_TOKEN.format(len(blocks) - 1)

        return _INLINE_CODE_RE.sub(_stash, line)

    @staticmethod
    def _restore(text: str, blocks: List[str]) -> str:
        """Put protected fragments back, in nesting-free order."""
        return _PROTECT_RE.sub(
            lambda m: blocks[int(m.group(1))], text)

    # ------------------------------------------------------------------ #
    # Headings normalization
    # ------------------------------------------------------------------ #

    def _normalize_headings(self, text: str, shift: int = 0,
                            flatten: bool = False) -> str:
        """Convert setext headings to ATX and normalize ATX levels.

        With ``flatten`` (the beautify path) heading levels additionally
        collapse to a gap-free hierarchy: the first level used becomes 1 and
        each deeper level is at most one below the previous heading's.

        Args:
            text: Protected Markdown text.
            shift: Integer level shift applied after flattening.
            flatten: Whether to repair skipped heading levels.

        Returns:
            str: Text with normalized ATX headings only.
        """
        lines = text.split("\n")
        lines = self._setext_to_atx(lines)
        level_map: Dict[int, int] = {}
        out: List[str] = []
        for line in lines:
            match = _ATX_HEADING_RE.match(line) or \
                _LOOSE_HASHES_RE.match(line)
            if not match:
                out.append(line.rstrip())
                continue
            hashes, content = match.group(2), match.group(4).strip().rstrip("#").strip()
            original = len(hashes)
            level = original
            if flatten:
                # Repair skipped levels with a stable mapping: sibling
                # headings (same original level) always land on the same
                # normalized level, and no heading is ever deeper than one
                # below the shallowest level seen so far.
                if original not in level_map:
                    if level_map:
                        level = min(original, max(level_map.values()) + 1)
                    level_map[original] = min(6, level)
                level = level_map[original]
            level = min(6, max(1, level + shift))
            out.append(f"{'#' * level} {content}" if content else
                       f"{'#' * level}")
        return "\n".join(out)

    @staticmethod
    def _setext_to_atx(lines: List[str]) -> List[str]:
        """Rewrite setext underlines (``===`` / ``---``) as ATX headings.

        A pure ``=+`` line makes the previous non-blank line an H1; a pure
        ``-{1,}`` line makes it an H2 when that previous line can start a
        paragraph (not itself a heading, list, quote, table or fence
        placeholder). This mirrors CommonMark, where ``text`` + ``---`` is a
        setext H2 rather than a thematic break.
        """
        out: List[str] = []
        for line in lines:
            stripped = line.strip()
            if out and stripped and set(stripped) <= {"="}:
                out[-1] = f"# {out[-1].strip()}"
                continue
            if out and stripped and set(stripped) <= {"-"} and \
                    _can_open_paragraph(out[-1]):
                out[-1] = f"## {out[-1].strip()}"
                continue
            out.append(line)
        return out

    # ------------------------------------------------------------------ #
    # List normalization
    # ------------------------------------------------------------------ #

    def _fix_lists(self, text: str, bullet: str, delimiter: str,
                   renumber: bool) -> str:
        """Unify unordered markers and renumber ordered lists.

        Unordered items become ``bullet``-prefixed regardless of their
        original ``*`` / ``+`` / ``-`` marker; ordered items are rewritten as
        ``N<delimiter>`` with N restarting at 1 for each contiguous list at
        the same indentation. Indentation is preserved.

        Args:
            text: Protected Markdown text.
            bullet: Target unordered marker (``-``, ``*`` or ``+``).
            delimiter: Target ordered delimiter (``.`` or ``)``).
            renumber: Whether to renumber ordered lists from 1.

        Returns:
            str: Text with unified list markers.
        """
        delimiter = self._delimiter(delimiter)
        lines = text.split("\n")
        out: List[str] = []
        counters: Dict[int, int] = {}
        for line in lines:
            unordered = _UNORDERED_ITEM_RE.match(line)
            ordered = _ORDERED_ITEM_RE.match(line)
            if unordered:
                # A different marker type always starts a new list.
                counters.clear()
                out.append(f"{unordered.group(1)}{bullet} "
                           f"{unordered.group(4).strip()}")
            elif ordered:
                indent = len(ordered.group(1).expandtabs(4))
                if renumber:
                    counters[indent] = counters.get(indent, 0) + 1
                    number = counters[indent]
                else:
                    number = int(ordered.group(2))
                out.append(f"{ordered.group(1)}{number}{delimiter} "
                           f"{ordered.group(5).strip()}")
            elif line.strip():
                # Any other non-blank line terminates every running list
                # (blank lines keep loose lists alive for renumbering).
                counters.clear()
                out.append(line.rstrip())
            else:
                out.append(line.rstrip())
        return "\n".join(out)

    # ------------------------------------------------------------------ #
    # Table normalization
    # ------------------------------------------------------------------ #

    def _fix_tables(self, text: str) -> str:
        """Rebuild GFM tables with aligned columns.

        A table is a header row containing a pipe whose following line is a
        separator (dashes/colons/pipes only). Every table is re-emitted with
        cells padded to the column width and a normalized separator that
        preserves per-column alignment (``:---``, ``---:``, ``:---:``).
        Rows are padded or truncated to the header's column count.

        Args:
            text: Protected Markdown text.

        Returns:
            str: Text with realigned tables.
        """
        lines = text.split("\n")
        out: List[str] = []
        i = 0
        while i < len(lines):
            if self._starts_table(lines, i):
                j = i + 2
                while j < len(lines) and _TABLE_ROW_HAS_PIPE_RE.search(lines[j]) \
                        and lines[j].strip():
                    j += 1
                out.extend(self._rebuild_table(lines[i:j]))
                i = j
                continue
            out.append(lines[i])
            i += 1
        return "\n".join(out)

    @staticmethod
    def _starts_table(lines: List[str], index: int) -> bool:
        if index + 1 >= len(lines):
            return False
        header, separator = lines[index], lines[index + 1]
        return bool(_TABLE_ROW_HAS_PIPE_RE.search(header) and
                    "|" in separator and
                    _TABLE_SEPARATOR_RE.match(separator) and
                    "-" in separator)

    @staticmethod
    def _rebuild_table(rows: List[str]) -> List[str]:
        header_cells = _split_row(rows[0])
        alignments = _parse_alignments(rows[1], len(header_cells))
        body = [_split_row(row) for row in rows[2:]]

        width = len(header_cells)
        padded = [header_cells]
        for cells in body:
            cells = cells[:width] + [""] * (width - len(cells))
            padded.append(cells)

        # Every column is at least three characters wide so the separator
        # row's "---" fits inside the column and the grid stays aligned.
        widths = [max(3, max(len(row[c]) for row in padded))
                  for c in range(width)]
        result = [_join_row(padded[0], widths, alignments)]
        result.append("| " + " | ".join(
            _alignment_bar(alignments[c], widths[c]) for c in range(width))
            + " |")
        for row in padded[1:]:
            result.append(_join_row(row, widths, alignments))
        return result

    # ------------------------------------------------------------------ #
    # Blank-line normalization
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_blank_lines(text: str) -> str:
        """Regularize vertical whitespace around block elements.

        Runs of blank lines collapse to one; headings and fenced-block
        placeholders get a blank line before them when adjacent to other
        content, and a heading is followed by a blank line when content
        continues; leading blank lines vanish and the document ends with
        exactly one newline. Only unambiguous block boundaries (headings,
        fence placeholders) receive spacing, so prose containing pipes or
        asterisks is never split apart.

        Args:
            text: Protected, already-transformed Markdown.

        Returns:
            str: Text with canonical blank-line placement.
        """
        lines = [line.rstrip() for line in text.split("\n")]
        compact: List[str] = []
        for line in lines:
            if line == "" and (not compact or compact[-1] == ""):
                continue
            compact.append(line)
        while compact and compact[0] == "":
            compact.pop(0)
        while compact and compact[-1] == "":
            compact.pop()

        out: List[str] = []
        for line in compact:
            if _is_block_boundary(line) and out and out[-1] != "":
                out.append("")
            if out and _is_heading(out[-1]) and line != "" and \
                    not _is_block_boundary(line):
                out.append("")
            out.append(line)
        return "\n".join(out) + "\n" if out else ""

    # ------------------------------------------------------------------ #
    # Statistics
    # ------------------------------------------------------------------ #

    def _stats(self, text: str) -> Dict[str, Any]:
        """Compute structural statistics for a Markdown document.

        Counting happens with code fenced off as placeholders so that list
        markers or hash signs inside code are not misread as structure.

        Args:
            text: Original Markdown.

        Returns:
            Dict[str, Any]: Counts of lines, words, headings per level,
            paragraphs, list items, tables, code blocks, links, images,
            blockquote lines and thematic breaks.
        """
        protected, blocks = self._protect(text)
        fence_blocks = sum(1 for b in blocks if b.startswith("```"))
        languages = sorted({
            b.split("\n", 1)[0][3:].strip()
            for b in blocks
            if b.startswith("```") and b.split("\n", 1)[0][3:].strip()})

        lines = protected.split("\n")
        # Setext underlines become ATX hashes before counting, so both
        # heading styles land in the same per-level counters and underline
        # lines are not mistaken for paragraphs or thematic breaks.
        lines = self._setext_to_atx(lines)
        non_blank = [line for line in lines if line.strip()]

        headings: Dict[str, int] = {f"h{level}": 0 for level in range(1, 7)}
        paragraphs = 0
        in_paragraph = False
        unordered_items = ordered_items = 0
        max_list_depth = 0
        table_count = 0
        blockquote_lines = 0
        thematic_breaks = 0

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            heading_match = _ATX_HEADING_RE.match(line) or \
                _LOOSE_HASHES_RE.match(line)
            is_list = _UNORDERED_ITEM_RE.match(line) or \
                _ORDERED_ITEM_RE.match(line)
            is_quote = bool(_BLOCKQUOTE_RE.match(line))

            if heading_match:
                level = min(6, len(heading_match.group(2)))
                headings[f"h{level}"] += 1
                in_paragraph = False
            elif self._starts_table(lines, i):
                table_count += 1
                i += 2
                while i < len(lines) and lines[i].strip() and \
                        _TABLE_ROW_HAS_PIPE_RE.search(lines[i]):
                    i += 1
                continue
            elif is_list:
                indent = len(line) - len(line.lstrip())
                max_list_depth = max(max_list_depth, indent // 2 + 1)
                if _UNORDERED_ITEM_RE.match(line):
                    unordered_items += 1
                else:
                    ordered_items += 1
                in_paragraph = False
            elif is_quote:
                blockquote_lines += 1
                in_paragraph = False
            elif _PROTECT_RE.match(stripped):
                in_paragraph = False
            elif _THEMATIC_BREAK_RE.match(line):
                thematic_breaks += 1
                in_paragraph = False
            elif stripped == "":
                in_paragraph = False
            elif not in_paragraph:
                paragraphs += 1
                in_paragraph = True
            i += 1

        inline_code = sum(1 for b in blocks if not b.startswith("```"))
        # Links and images are counted on the protected text so that link
        # syntax appearing inside code is not reported as document structure.
        links = len(_LINK_RE.findall(protected))
        images = len(_IMAGE_RE.findall(protected))
        words = len(protected.split())

        return {
            "lines": len(lines),
            "non_blank_lines": len(non_blank),
            "chars": len(text),
            "words": words,
            "headings": headings,
            "heading_total": sum(headings.values()),
            "paragraphs": paragraphs,
            "list_items": {
                "unordered": unordered_items,
                "ordered": ordered_items,
                "total": unordered_items + ordered_items,
                "max_nesting_level": max_list_depth,
            },
            "tables": table_count,
            "code_blocks": {
                "fenced": fence_blocks,
                "inline": inline_code,
                "languages": languages,
            },
            "links": links,
            "images": images,
            "blockquote_lines": blockquote_lines,
            "thematic_breaks": thematic_breaks,
        }


def _can_open_paragraph(line: str) -> bool:
    """Whether a line may serve as a setext heading's text."""
    stripped = line.strip()
    if not stripped:
        return False
    return not (stripped.startswith(("#", ">", "|")) or
                _UNORDERED_ITEM_RE.match(stripped) or
                _ORDERED_ITEM_RE.match(stripped) or
                _PROTECT_RE.match(stripped) or
                _THEMATIC_BREAK_RE.match(stripped))


def _is_heading(line: str) -> bool:
    return bool(_ATX_HEADING_RE.match(line) or _LOOSE_HASHES_RE.match(line))


def _is_block_boundary(line: str) -> bool:
    return _is_heading(line) or bool(_PROTECT_RE.match(line.strip()))


def _split_row(row: str) -> List[str]:
    """Split a table row into trimmed cells on unescaped pipes.

    Escaped pipes (``\\|``) stay inside their cell untouched, so rebuilding
    the row round-trips literal pipes without breaking column structure.
    """
    trimmed = row.strip()
    if trimmed.startswith("|"):
        trimmed = trimmed[1:]
    if trimmed.endswith("|") and not trimmed.endswith("\\|"):
        trimmed = trimmed[:-1]
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", trimmed)]


def _parse_alignments(separator: str, count: int) -> List[str]:
    """Extract per-column alignment from a separator row."""
    cells = [cell.strip() for cell in _split_row(separator)]
    result: List[str] = []
    for column in range(count):
        cell = cells[column] if column < len(cells) else ""
        left = cell.startswith(":")
        right = cell.endswith(":") and len(cell) > 1
        result.append("center" if left and right else
                      "right" if right else "left")
    return result


def _alignment_bar(alignment: str, width: int) -> str:
    dashes = max(3, width)
    if alignment == "center":
        return f":{'-' * (dashes - 2)}:"
    if alignment == "right":
        return f"{'-' * (dashes - 1)}:"
    return "-" * dashes


def _join_row(cells: List[str], widths: List[int],
              alignments: List[str]) -> str:
    padded = []
    for index, cell in enumerate(cells):
        width = widths[index]
        if alignments[index] == "right":
            padded.append(cell.rjust(width))
        elif alignments[index] == "center":
            padded.append(cell.center(width))
        else:
            padded.append(cell.ljust(width))
    return "| " + " | ".join(padded) + " |"
