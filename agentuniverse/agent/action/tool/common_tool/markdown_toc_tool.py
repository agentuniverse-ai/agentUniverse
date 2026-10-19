#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: markdown_toc_tool.py

"""Linked table-of-contents generator for Markdown, pure stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) and pairs with two sibling contributions: the
knowledge-side ``OutlineExtractor`` (#3531) that analyzes document
outlines before ingestion, and the ``MarkdownBeautifyTool`` (#3339)
that normalizes Markdown formatting — none of them generates a linked
table of contents, which is what this tool does. It is built purely on
``re`` and line scanning, so it runs in any environment without a
Markdown library and without network access.

Three modes are supported:

* ``generate`` — scan the document's ATX headings (levels bounded by
  ``min_level`` / ``max_level``, default 2-3 for compactness) and
  produce an indented bullet-list TOC whose entries link to
  GitHub-style heading anchors. An existing TOC — a contiguous
  bullet-list block where every item is purely a local anchor link —
  is refreshed in place at the same position by default
  (``replace=True``); with ``replace=False`` the fresh TOC is appended
  to the end of the document instead. When no TOC exists yet the new
  one is always appended. Heading slugs follow the ``github-slugger``
  rules: lowercase, strip punctuation (keeping hyphens and
  underscores), spaces become hyphens, and repeated headings get
  ``-1`` / ``-2`` … suffixes counted in document order over *all*
  headings (a filtered-out level still occupies its slug name).
* ``anchors`` — list every heading with its level, text, source line,
  and the computed slug, including duplicate-suffix evidence
  (occurrence index and a ``duplicate_suffix`` flag).
* ``check`` — verify that every local anchor link (``[text](#slug)``)
  in the document resolves to a computed heading slug, returning the
  list of broken links with line numbers.

Fenced code blocks (``` / ~~~) are immune: headings and TOC-looking
bullet blocks inside them are ignored, and links inside fences or
inline code spans are not checked. Everything is deterministic — the
output depends only on the input text.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, non-string ``markdown``,
non-integer or out-of-range levels, ``min_level > max_level``,
oversized input) raise a ``ValueError``, mirroring the other common
tools. A ``generate`` call whose level range matches no heading
returns a structured ``error`` payload (``no_headings_in_range``) so
an agent can react without catching exceptions.
"""

import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# --------------------------------------------------------------------- #
# Line-level Markdown structures (CommonMark-faithful subsets)
# --------------------------------------------------------------------- #

# ATX heading: up to three leading spaces, 1-6 hashes, then either end
# of line or whitespace + content. `#foo` (no space) is not a heading.
_ATX_HEADING_RE = re.compile(r"^( {0,3})(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")

# Trailing closing hash sequence of an ATX heading: hashes at end of
# content must be preceded by whitespace (or be the whole content).
_CLOSING_HASHES_RE = re.compile(r"(?:\A|[ \t]+)#+[ \t]*\Z")

# Fenced code block open: up to three leading spaces, 3+ backticks or
# tildes; a backtick fence's info string may not contain backticks.
_FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
# Fenced code block close: same fence character, at least as long.
_FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")

# Bullet list item (used for TOC block detection): limited leading
# indentation, a `-` / `*` / `+` marker, whitespace, non-empty content.
_LIST_ITEM_RE = re.compile(r"^(\s{0,14})([-*+])([ \t]+)(\S.*)$")

# TOC item content: the entire item is one link whose target is a
# local anchor (starts with '#', no whitespace inside the target);
# escaped brackets (\[ \]) inside the link text are tolerated.
_TOC_ITEM_CONTENT_RE = re.compile(r"\A\[(?:\\.|[^\]])*\]\(#[^)\s]*\)\Z")

# Inline code span, removed before link scanning (links shown as
# literal code are not real links in rendered Markdown).
_INLINE_CODE_RE = re.compile(r"(`+)(?!`)(.+?)\1")

# Inline link with a local anchor target; negative lookbehind skips
# images (`![alt](#x)` is not a link).
_LOCAL_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(#([^)\s]*)\)")

# Any inline link (used to unwrap links in heading text before
# slugging — GitHub slugs the rendered text, i.e. the link label).
_ANY_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\([^)]*\)")

# --------------------------------------------------------------------- #
# github-slugger pinned slug rules
# --------------------------------------------------------------------- #

# Characters removed before spaces become hyphens (github-slugger's
# removal set for the ranges that matter in practice): C0 controls and
# DEL; ASCII punctuation/symbols EXCEPT hyphen and underscore; the
# Latin-1 punctuation/symbol ranges; general punctuation (dashes,
# quotes, bullets …). Letters, digits, hyphens, underscores, spaces,
# CJK and other scripts are kept verbatim.
_SLUG_STRIP_RE = re.compile(
    "[\u0000-\u001F\u007F"          # control characters + DEL
    "\u0021-\u002C\u002E-\u002F"    # ASCII punctuation, but not '-' (0x2D)
    "\u003A-\u0040"                 # : ; < = > ? @
    "\u005B-\u005E\u0060"           # [ \ ] ^ ` — underscore (0x5F) kept
    "\u007B-\u007E"                 # { | } ~
    "\u00A1-\u00A9\u00AB-\u00B4"    # Latin-1 punctuation (¡ ¢ £ … ´)
    "\u00B6-\u00B9\u00BB-\u00BF"    # ¶ · ¹ » … ¿
    "\u00D7\u00F7"                  # × ÷
    "\u2010-\u2027\u2030-\u205E"    # general punctuation (– — ‘ ’ “ ” …)
    "]+"
)


class MarkdownTocTool(Tool):
    """Linked table-of-contents tool for Markdown, pure stdlib.

    Modes:

    * ``generate`` — build an indented bullet-list TOC of the ATX
      headings between ``min_level`` and ``max_level`` (default 2-3),
      linking each entry to its GitHub-style heading anchor; an
      existing all-anchor bullet block is refreshed in place
      (``replace=True``, the default) or the new TOC is appended
      (``replace=False`` / no existing TOC).
    * ``anchors`` — list every heading with its computed slug and
      duplicate-suffix evidence.
    * ``check`` — verify every local anchor link resolves to a
      heading slug; report the broken ones.

    Attributes:
        max_input_chars (int): Upper bound on the accepted ``markdown``
            input length; longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "markdown_toc_tool"
    description: str = (
        "Markdown table-of-contents tool — pure Python stdlib, no "
        "network required. Generate a linked, indented bullet-list TOC "
        "from ATX headings with GitHub-style anchors and refresh an "
        "existing TOC in place (mode='generate', levels bounded by "
        "min_level/max_level, default 2-3), list every heading with its "
        "computed slug and duplicate-suffix evidence (mode='anchors'), "
        "or check that every local anchor link resolves to a heading "
        "slug (mode='check')."
    )

    MODES: ClassVar[tuple] = ("generate", "anchors", "check")

    max_input_chars: int = 1_000_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        markdown: Any = None,
        min_level: Any = None,
        max_level: Any = None,
        replace: Any = None,
    ) -> Dict[str, Any]:
        """Run one table-of-contents operation.

        Args:
            mode (str): One of ``generate`` / ``anchors`` / ``check``.
            markdown (str): The Markdown source text.
            min_level (int | str): Shallowest heading level included by
                ``generate``; 1-6, default 2. Accepted as an integer or
                a digit string; validated (together with
                ``max_level``) in every mode even though only
                ``generate`` uses the range.
            max_level (int | str): Deepest heading level included by
                ``generate``; 1-6, default 3.
            replace (bool): ``generate`` only — when an existing TOC
                block is detected, replace it in place at the same
                position (``True``, the default) or append the fresh
                TOC at the end of the document (``False``). Without an
                existing TOC the new one is always appended.

        Returns:
            Dict[str, Any]: ``{"status": "success", "mode": ..., ...}``
            — ``markdown`` / ``toc`` / ``entries`` / ``action`` for
            ``generate``, ``headings`` for ``anchors``, and
            ``broken_links`` / ``ok`` for ``check`` — or a structured
            ``{"status": "error", ...}`` payload for content-level
            failures (no heading matched the level range).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        operation = self._validate_mode(mode)
        text = self._validate_markdown(markdown)
        low = self._validate_level(min_level, "min_level", 2)
        high = self._validate_level(max_level, "max_level", 3)
        if low > high:
            self._invalid(
                f"min_level must be <= max_level (got {low} > {high})"
            )
        if replace is None:
            replace = True
        if not isinstance(replace, bool):
            self._invalid(f"replace must be a boolean (got {replace!r})")

        lines = text.split("\n")
        masked = self._mask_fenced_code(lines)
        headings = self._collect_headings(lines, masked)

        if operation == "generate":
            return self._run_generate(text, lines, masked, headings, low, high, replace)
        if operation == "anchors":
            return self._run_anchors(headings)
        return self._run_check(lines, masked, headings)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"markdown_toc_tool: {message}")

    @classmethod
    def _validate_mode(cls, mode: Any) -> str:
        """Validate the mode selector."""
        if mode is None:
            cls._invalid("mode is required (generate / anchors / check)")
        if isinstance(mode, bool) or not isinstance(mode, str):
            cls._invalid(
                "mode must be one of: "
                f"{', '.join(cls.MODES)} (got {mode!r})"
            )
        operation = mode.strip().lower()
        if operation not in cls.MODES:
            cls._invalid(
                "mode must be one of: "
                f"{', '.join(cls.MODES)} (got {mode!r})"
            )
        return operation

    def _validate_markdown(self, markdown: Any) -> str:
        """Validate the ``markdown`` input (empty documents are legal)."""
        if markdown is None or isinstance(markdown, bool) or not isinstance(markdown, str):
            self._invalid(
                f"markdown must be a string (got {markdown!r})"
            )
        if len(markdown) > self.max_input_chars:
            self._invalid(
                f"markdown exceeds the {self.max_input_chars:,}-character "
                f"limit (got {len(markdown):,} characters)"
            )
        return markdown

    @classmethod
    def _validate_level(cls, level: Any, name: str, default: int) -> int:
        """Validate a heading-level bound (int or digit string, 1-6)."""
        if level is None:
            return default
        if isinstance(level, bool):
            cls._invalid(f"{name} must be an integer between 1 and 6 (got {level!r})")
        if isinstance(level, str):
            stripped = level.strip()
            if not stripped.isdigit():
                cls._invalid(f"{name} must be an integer between 1 and 6 (got {level!r})")
            level = int(stripped)
        if not isinstance(level, int):
            cls._invalid(f"{name} must be an integer between 1 and 6 (got {level!r})")
        if not 1 <= level <= 6:
            cls._invalid(f"{name} must be between 1 and 6 (got {level})")
        return level

    # ------------------------------------------------------------------ #
    # Document scanning (fences, headings, slugs)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _mask_fenced_code(lines: List[str]) -> List[bool]:
        """Return a per-line mask: True for lines inside fenced code.

        Fence state follows CommonMark: an opening fence is 3+ backticks
        or tildes preceded by up to three spaces (a backtick fence's
        info string may not contain backticks); a closing fence repeats
        the same character with at least the opening length.
        """
        masked = [False] * len(lines)
        fence_char: Optional[str] = None
        fence_len = 0
        inside = False
        for index, line in enumerate(lines):
            if inside:
                masked[index] = True
                close = _FENCE_CLOSE_RE.match(line)
                if (
                    close is not None
                    and close.group(1)[0] == fence_char
                    and len(close.group(1)) >= fence_len
                ):
                    inside = False
                continue
            open_match = _FENCE_OPEN_RE.match(line)
            if open_match is not None:
                marker, info = open_match.group(1), open_match.group(2)
                if marker[0] == "`" and "`" in info:
                    continue  # not a fence opening
                fence_char, fence_len, inside = marker[0], len(marker), True
                masked[index] = True
        return masked

    @classmethod
    def _slugify(cls, heading_text: str) -> str:
        """Compute the base anchor slug for one heading text.

        Pinned to the github-slugger rules: lowercase, strip the
        punctuation/symbol ranges listed in ``_SLUG_STRIP_RE`` (hyphens
        and underscores survive), then turn spaces into hyphens. CJK
        and other non-punctuation characters are kept verbatim, so
        ``"C++ & C#"`` -> ``"c--c"`` and ``"中文 标题"`` -> ``"中文-标题"``.
        """
        lowered = _ANY_LINK_RE.sub(r"\1", heading_text).lower()
        stripped = _SLUG_STRIP_RE.sub("", lowered)
        return stripped.replace(" ", "-")

    @classmethod
    def _collect_headings(
        cls, lines: List[str], masked: List[bool]
    ) -> List[Dict[str, Any]]:
        """Collect every ATX heading with its document-order slug.

        Duplicate suffixes (``-1`` / ``-2`` …) are counted over *all*
        headings, not only the ones a later level filter keeps — a
        filtered-out heading still occupies its anchor name on GitHub.
        """
        headings: List[Dict[str, Any]] = []
        occurrences: Dict[str, int] = {}
        for index, line in enumerate(lines):
            if masked[index]:
                continue
            match = _ATX_HEADING_RE.match(line)
            if match is None:
                continue
            level = len(match.group(2))
            raw = match.group(3) if match.group(3) is not None else ""
            text = _CLOSING_HASHES_RE.sub("", raw).strip()
            base = cls._slugify(text)
            count = occurrences.get(base, 0)
            occurrences[base] = count + 1
            slug = base if count == 0 else f"{base}-{count}"
            headings.append(
                {
                    "level": level,
                    "text": text,
                    "slug": slug,
                    "line": index + 1,
                    "occurrence": count + 1,
                }
            )
        return headings

    # ------------------------------------------------------------------ #
    # generate mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _find_toc_block(
        cls, lines: List[str], masked: List[bool]
    ) -> Optional[Tuple[int, int]]:
        """Locate the first existing TOC block, if any.

        A TOC block is a maximal run of consecutive unmasked bullet
        items where *every* item's content is purely one local anchor
        link. Returns the inclusive (start, end) line indexes.
        """
        start: Optional[int] = None
        run_is_toc = True
        for index, line in enumerate(lines):
            if not masked[index]:
                item = _LIST_ITEM_RE.match(line)
            else:
                item = None
            if item is not None:
                if start is None:
                    start, run_is_toc = index, True
                if not _TOC_ITEM_CONTENT_RE.match(item.group(4)):
                    run_is_toc = False
                continue
            if start is not None:
                if run_is_toc:
                    return (start, index - 1)
                start = None
        if start is not None and run_is_toc:
            return (start, len(lines) - 1)
        return None

    @staticmethod
    def _build_toc_lines(
        headings: List[Dict[str, Any]], min_level: int, max_level: int
    ) -> List[str]:
        """Render the indented bullet list of anchor links."""
        lines: List[str] = []
        for heading in headings:
            level = heading["level"]
            if not min_level <= level <= max_level:
                continue
            indent = "  " * (level - min_level)
            text = heading["text"].replace("[", "\\[").replace("]", "\\]")
            lines.append(f"{indent}- [{text}](#{heading['slug']})")
        return lines

    def _run_generate(
        self,
        text: str,
        lines: List[str],
        masked: List[bool],
        headings: List[Dict[str, Any]],
        min_level: int,
        max_level: int,
        replace: bool,
    ) -> Dict[str, Any]:
        """Generate / refresh the TOC block inside the document."""
        toc_lines = self._build_toc_lines(headings, min_level, max_level)
        if not toc_lines:
            return self._error_result(
                "generate",
                error_type="no_headings_in_range",
                message=(
                    "no ATX heading matched the requested level range "
                    f"[{min_level}, {max_level}]; nothing to put in the "
                    "table of contents"
                ),
            )

        block = self._find_toc_block(lines, masked)
        action: str
        if block is not None and replace:
            start, end = block
            if lines[start : end + 1] == toc_lines:
                action = "unchanged"
                new_text = text
            else:
                action = "replaced"
                new_text = "\n".join(
                    lines[:start] + toc_lines + lines[end + 1:]
                )
        else:
            action = "appended"
            new_text = text.rstrip("\n") + "\n\n" + "\n".join(toc_lines) + "\n"

        return {
            "status": "success",
            "mode": "generate",
            "markdown": new_text,
            "toc": "\n".join(toc_lines),
            "entries": len(toc_lines),
            "action": action,
            "existing_toc_found": block is not None,
            "changed": new_text != text,
            "min_level": min_level,
            "max_level": max_level,
        }

    # ------------------------------------------------------------------ #
    # anchors mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _run_anchors(headings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """List every heading with its slug and duplicate evidence."""
        rows = [
            {
                "level": heading["level"],
                "text": heading["text"],
                "slug": heading["slug"],
                "line": heading["line"],
                "occurrence": heading["occurrence"],
                "duplicate_suffix": heading["occurrence"] > 1,
            }
            for heading in headings
        ]
        return {
            "status": "success",
            "mode": "anchors",
            "count": len(rows),
            "headings": rows,
        }

    # ------------------------------------------------------------------ #
    # check mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _run_check(
        lines: List[str], masked: List[bool], headings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Verify that every local anchor link resolves to a slug."""
        slugs = {heading["slug"] for heading in headings}
        checked = 0
        broken: List[Dict[str, Any]] = []
        for index, line in enumerate(lines):
            if masked[index]:
                continue
            scrubbed = _INLINE_CODE_RE.sub("", line)
            for match in _LOCAL_LINK_RE.finditer(scrubbed):
                checked += 1
                fragment = match.group(2)
                if fragment not in slugs:
                    broken.append(
                        {
                            "text": match.group(1),
                            "anchor": f"#{fragment}",
                            "line": index + 1,
                        }
                    )
        return {
            "status": "success",
            "mode": "check",
            "links_checked": checked,
            "broken_count": len(broken),
            "broken_links": broken,
            "ok": not broken,
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(mode: str, error_type: str, message: str) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            "status": "error",
            "mode": mode,
            "error_type": error_type,
            "error": str(message)[:500],
        }
