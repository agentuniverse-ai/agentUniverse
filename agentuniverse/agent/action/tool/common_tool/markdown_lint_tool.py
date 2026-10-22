#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: markdown_lint_tool.py

"""Whole-document Markdown quality linter built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency quality gate for
agents that *emit or receive* Markdown. The existing Markdown tools
each cover one slice — MarkdownTocTool (#3732) generates linked
tables of contents, MarkdownTableValidatorTool (#3848) validates only
GFM tables, MarkdownLinkExtractorTool (#3714) audits only links — and
HeadingConsistencyChecker (#3739) validates heading structure as a
knowledge-side pre-processing component that stamps its findings into
document metadata for pipeline consumers. None of them returns a
whole-document lint report to the caller. MarkdownLintTool fills that
gap: one call checks headings, lists, code fences, links, raw HTML
and line hygiene together, profiles the document, or proposes safe
text-only fixes.

Everything runs offline on the ``markdown_text`` string with no file
I/O, no network and no third-party parser. Line numbers are 1-based
over *logical lines*: a single leading UTF-8 BOM is stripped silently
and ``\\r\\n`` / lone ``\\r`` terminators are normalized to ``\\n``
before any scanning, so CRLF documents report identical line numbers
to their LF twins (the ``fixed_text`` of fix_hints is always
LF-joined).

Fence-interior immunity — the CodeBlockDetector (#3802) family rules
--------------------------------------------------------------------
Fence recognition follows CommonMark exactly as CodeBlockDetector
(#3802) implements it: an opener is a line indented by at most 3
spaces whose remainder starts with a maximal run of 3 or more
backticks or tildes; the rest of the line is the info string whose
lowercased first word is the language; a backtick opener may not
carry backticks in its info string. A closer must repeat the opener's
fence character at least as many times, be indented by at most 3
spaces and carry nothing but optional whitespace after the run. Every
rule below is immune inside a fence block's interior — list, HTML,
tab, long-line, bare-URL and empty-link violations inside code
samples never fire; the fence rules themselves (MD008/MD009/MD010)
fire on the fence lines by definition. A same-character closing run
*shorter* than the opener does not close the fence (CommonMark) and
is not separately flagged; indented (4-space) code blocks are not
tracked — the simplification is documented here.

Supported modes
---------------
* ``lint`` — run the rule table below over ``markdown_text`` and
  return ``ok`` plus ``findings``. Each finding is ``{code,
  severity, line, message, hint}``. ``ok`` is True only when no
  finding of severity error or warning was raised (info-only stays
  ok). Findings are sorted by (line, code, message), capped at 200
  entries (``finding_count`` keeps the true total and
  ``findings_truncated`` flags the cut).
* ``profile`` — document statistics: the heading tree (count, per
  level, max depth, every heading's line/level/text capped at 60
  characters), list shape (list blocks, unordered and ordered item
  counts), code fences (count, closed/unclosed, language histogram,
  fences without a language), inline link census (total, internal,
  external — a destination carrying a URI scheme counts external,
  anchors and relative paths internal), and word counting with the
  family tokenizer shared by ReadingTimeTool (#3928) and
  ReadingLevelScorer: a word is a Latin alphabetic run (inner
  hyphens and apostrophes kept, so ``state-of-the-art`` and
  ``don't`` are one word each), a digit run, or ONE CJK character
  (Han, kana, Hangul). Words are counted over prose lines only
  (fence lines and fence interiors excluded). Reading stats use the
  ReadingTimeTool (#3928) reference rate of 238 wpm (Brysbaert
  2019) with its rounding rules (ceiled seconds, humanized
  ``"3 min 12 s"``) — ReadingTimeTool remains the dedicated tool
  for time estimation and word budgets; this profile only surfaces
  the headline numbers.
* ``fix_hints`` — apply safe *textual* repairs only, never
  structural ones: append a closing fence (same character, same run
  length) for a fence left open at end of document, and strip
  trailing whitespace on lines whose trailing run is NOT two or more
  plain spaces (a 2+ space run is a CommonMark hard break — kept and
  only flagged by MD013; a single trailing space, a trailing tab or
  a mixed run is invisible noise — stripped). Fence lines and fence
  interiors are never touched. ``applied`` lists each repair and
  ``remaining`` re-lints the fixed text with the same options, so
  what is left is exactly what textual fixing cannot heal (heading
  jumps, marker mixing, empty links, ...).

Rule table (mode ``lint``)
--------------------------
===============================  ========  =====================================  ==================================================
Code                             Sev.      Trigger (exact)                         Hint
===============================  ========  =====================================  ==================================================
MD001 heading_level_jump         warning   consecutive ATX headings skip levels    link with an intermediate heading —
                                          downward (h1 followed by h4 skips        h2 in the example
                                          h2 and h3); reported at the deeper
                                          heading
MD002 multiple_h1                warning   a second (or later) level-1 heading     demote the later h1 to h2 or merge
                                          appears; each occurrence after the       sections
                                          first is reported at its line
MD003 heading_empty              error     an ATX heading whose text is empty      give the heading a title
                                          (``##`` alone or hashes plus spaces,
                                          including ``## ##``)
MD004 heading_trailing_hashes_   warning   a heading closes with hashes but the    match the closing count to the
      inconsistent                        run differs from the opening count       opening count (``## Title ##``)
                                          (``## Title ###``)
MD005 list_marker_mixing         warning   document-level summary: unordered       pick one marker character for the
                                          items use 2+ distinct markers among      whole document
                                          ``-`` ``*`` ``+``; dominant = most
                                          frequent (ties: -, *, +), reported
                                          once at the first non-dominant line
                                          with the full breakdown
MD006 list_indent_not_multiple_2 warning   a list item line's leading spaces are   re-indent list levels by 2 spaces
      indent                              not a multiple of 2 (1, 3, 5...)
MD007 tab_in_list_indent         warning   a tab appears in a list item's          use spaces for list indentation
                                          leading whitespace
MD008 code_fence_unclosed        error     a fence opened but never closed         add the matching closing fence
                                          through end of document; reported at     (fix_hints appends it)
                                          the opening fence line
MD009 code_fence_lang_missing    info      an opening fence carries no language    tag the fence — ```python — for
                                          in its info string                      highlighters
MD010 fence_char_mismatch        error     while a fence is open, a closer-shaped  close with the opening character —
                                          line uses the OTHER character (```      ``` opened, ~~~ attempted
                                          opened, ~~~ line); per CommonMark it
                                          does not close the fence, so MD008
                                          also fires when no proper closer
                                          follows
MD011 bare_url                   info      a bare http(s) URL sits in prose         wrap as <https://...> autolink or
                                          outside inline code, link destinations   [text](url)
                                          and autolinks; one finding per line
                                          with the count and first URL
MD012 html_raw_block             info      a line starts (up to 3 spaces) with a   many pipelines strip raw HTML —
                                          block-level HTML tag or ``<!--``        prefer Markdown constructs
                                          (div, table, p, h1..h6, ul, script,
                                          ...) — inline HTML mid-line does not
                                          fire
MD013 trailing_spaces_hard_      info      a prose line ends with two or more      hard breaks are invisible and
      break_ambiguity                    spaces — a CommonMark hard break         editor-strippable; prefer an
                                          many editors strip invisibly            explicit backslash break
MD014 line_too_long              warning   a prose line longer than                rewrap; LineLengthTool (#3915) is
                                          ``max_line_length`` (default 120)        the dedicated line-width auditor —
                                          characters after right-trimming         this rule is only the markdown-
                                          whitespace; lines containing any        specific variant that exempts
                                          ``http://`` or ``https://`` URL are      lines with an unbreakable URL
                                          exempt (URLs often cannot be rewrapped)
MD015 inconsistent_bullet_case   warning   within one contiguous run of unordered  capitalize sibling items uniformly
                                          items at the same indentation, an       (first letter item is the
                                          item's first ASCII letter case differs   reference)
                                          from the first lettered item's; one
                                          finding per run at the deviating line
MD016 empty_link                 warning   an inline link renders nothing or goes   fill in the text and destination
                                          nowhere: ``[]()`` (empty link) or        (or remove the link)
                                          ``[text]()`` (missing destination);
                                          images ``![...]()`` are exempt
===============================  ========  =====================================  ==================================================

Options and error matrix
------------------------
``max_line_length`` is an integer 40..500, default 120; ``rules``
maps any implemented rule code to False to disable that single rule
for the call (both accepted in lint and fix_hints — fix_hints re-lints
with the caller's thresholds). ``close_unclosed_fence`` and
``strip_trailing_spaces`` (fix_hints only, default True) toggle the
two repairs. Options are validated per mode — a lint option in
profile mode is an error, and vice versa. The ``fixed_text`` of
fix_hints is always LF-joined with one trailing newline.

``ValueError`` is raised for: an unknown mode; a non-string, empty,
whitespace-only or oversized ``markdown_text`` (over
``max_input_chars`` = 100,000 characters); malformed options of any
kind. All findings and statistics are exact and the run is fully
deterministic.
"""

import re
from fractions import Fraction
from math import ceil
from typing import Any, ClassVar, Optional

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# Static vocabulary
# ---------------------------------------------------------------------------

# Fence scanning (CodeBlockDetector #3802 family rules).
_FENCE_RUN_RE = re.compile(r"\A(`+|~+)(.*)\Z")
_MAX_FENCE_INDENT = 3

# ATX heading: 0-3 spaces, 1-6 hashes, then end of line or whitespace.
_ATX_HEADING_RE = re.compile(r"\A( {0,3})(#{1,6})(.*)\Z")
_TRAILING_HASHES_RE = re.compile(r"(#+)\Z")

# Thematic breaks (checked before list markers: `* * *` / `- - -` are
# not list items).
_THEMATIC_BREAK_RE = re.compile(
    r"\A {0,3}(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})\Z"
)

# List item lines: marker must be followed by a space/tab or EOL.
_UNORDERED_ITEM_RE = re.compile(r"\A([ \t]*)([-*+])([ \t]|\Z)")
_ORDERED_ITEM_RE = re.compile(r"\A([ \t]*)([0-9]{1,9})([.)])([ \t]|\Z)")

# Unordered markers in MD005 tie-break priority order.
_MARKERS: tuple = ("-", "*", "+")

# Inline shapes for the line-scoped rules.
_CODE_SPAN_RE = re.compile(r"`+[^`\n]*`+")
_MD_LINK_RE = re.compile(r"!?\[[^\]\n]*\]\([^)\n]*\)")
_PLAIN_LINK_RE = re.compile(r"\[([^\]\n]*)\]\(([^)\n]*)\)")
_AUTOLINK_RE = re.compile(r"<[^\s<>\n]+>")
_BARE_URL_RE = re.compile(r"https?://[^\s<>\[\]`]+")
_URL_HINT_RE = re.compile(r"https?://")
_LINK_DEF_RE = re.compile(r"\A {0,3}\[[^\]\n]+\]:[^\n]*")

# Block-level HTML tags whose opening/closing line triggers MD012.
_BLOCK_TAGS = frozenset((
    "address", "article", "aside", "blockquote", "body", "caption",
    "center", "col", "colgroup", "dd", "details", "dialog", "div",
    "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form",
    "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup",
    "hr", "html", "iframe", "legend", "li", "main", "menu", "nav",
    "ol", "optgroup", "option", "p", "pre", "script", "section",
    "select", "style", "summary", "table", "tbody", "td", "tfoot",
    "th", "thead", "title", "tr", "ul",
))
_HTML_BLOCK_RE = re.compile(r"\A {0,3}(?:</?([A-Za-z][A-Za-z0-9-]*)|<!--)")

# A URI scheme at the start of a link destination marks it external.
_SCHEME_RE = re.compile(r"\A[A-Za-z][A-Za-z0-9+.\-]*:")

# Family tokenizer (ReadingTimeTool #3928 / ReadingLevelScorer): a
# Latin alphabetic run (inner hyphens/apostrophes kept), a digit run,
# or ONE CJK character (Han, kana, Hangul).
_WORD_RE = re.compile(
    r"[A-Za-z]+(?:[-'][A-Za-z]+)*|[0-9]+|[\u4e00-\u9fff\u3040-\u30ff"
    r"\uac00-\ud7af]"
)
_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")

# Reading reference rate shared with ReadingTimeTool (#3928):
# Brysbaert (2019) meta-analysis of silent reading, 238 wpm.
_READING_WPM = 238

# Rule codes -> (slug, severity, hint). ``ok`` is False when any
# error or warning fires.
_RULES: dict = {
    "MD001": ("heading_level_jump", "warning",
              "link with an intermediate heading (h2 between h1 and h4)"),
    "MD002": ("multiple_h1", "warning",
              "demote the later h1 to h2 or merge the sections"),
    "MD003": ("heading_empty", "error",
              "give the heading a title"),
    "MD004": ("heading_trailing_hashes_inconsistent", "warning",
              'match the closing count to the opening ("## Title ##")'),
    "MD005": ("list_marker_mixing", "warning",
              "pick one unordered marker character for the document"),
    "MD006": ("list_indent_not_multiple_2", "warning",
              "re-indent list levels by 2 spaces"),
    "MD007": ("tab_in_list_indent", "warning",
              "use spaces for list indentation"),
    "MD008": ("code_fence_unclosed", "error",
              "add the matching closing fence (fix_hints appends it)"),
    "MD009": ("code_fence_lang_missing", "info",
              "tag the fence (```python) for highlighters"),
    "MD010": ("fence_char_mismatch", "error",
              "close the fence with its opening character"),
    "MD011": ("bare_url", "info",
              "wrap as <https://...> autolink or [text](url)"),
    "MD012": ("html_raw_block", "info",
              "prefer Markdown constructs over raw HTML blocks"),
    "MD013": ("trailing_spaces_hard_break_ambiguity", "info",
              "prefer an explicit backslash hard break"),
    "MD014": ("line_too_long", "warning",
              "rewrap the line (URL-bearing lines are exempt)"),
    "MD015": ("inconsistent_bullet_case", "warning",
              "capitalize sibling list items uniformly"),
    "MD016": ("empty_link", "warning",
              "fill in the link text and destination"),
}
_RULE_CODES: tuple = tuple(_RULES)

# Per-mode option gates for the error matrix. fix_hints shares the
# lint options so its re-lint runs with the caller's thresholds.
_LINT_OPTIONS = frozenset({"max_line_length", "rules"})
_PROFILE_OPTIONS: frozenset = frozenset()
_FIX_OPTIONS = frozenset({
    "close_unclosed_fence", "strip_trailing_spaces",
    "max_line_length", "rules",
})
_MODE_OPTIONS = {"lint": _LINT_OPTIONS, "profile": _PROFILE_OPTIONS,
                 "fix_hints": _FIX_OPTIONS}


def _err(message: str) -> ValueError:
    """Return the ValueError every validation branch raises."""
    return ValueError(message)


def _cap(text: str, cap: int = 50) -> str:
    """Cap a preview string, appending ``...`` when cut."""
    return text if len(text) <= cap else text[: cap - 3] + "..."


def _parse_opener(line: str) -> Optional[tuple]:
    """Parse one line as a fence opener (CodeBlockDetector rules).

    Returns ``(fence_char, run_length, language)`` or None. A line
    indented by more than 3 spaces is never an opener; a backtick
    opener may not carry backticks in its info string.
    """
    stripped = line.lstrip(" ")
    if len(line) - len(stripped) > _MAX_FENCE_INDENT:
        return None
    match = _FENCE_RUN_RE.match(stripped)
    if match is None:
        return None
    fence = match.group(1)
    if len(fence) < 3:
        return None
    info = match.group(2).strip()
    if fence[0] == "`" and "`" in info:
        return None
    language = info.split()[0].lower() if info else ""
    return fence[0], len(fence), language


def _closing_run(line: str, char: str) -> Optional[int]:
    """Length of ``line``'s fence run when it is closer-shaped for
    ``char`` (indent <= 3, run of ``char``, nothing but whitespace
    after), else None."""
    stripped = line.lstrip(" ")
    if len(line) - len(stripped) > _MAX_FENCE_INDENT:
        return None
    if not stripped.startswith(char):
        return None
    match = _FENCE_RUN_RE.match(stripped)
    if match is None:
        return None
    run, rest = match.group(1), match.group(2)
    if run[0] != char or rest.strip():
        return None
    return len(run)


def _scan_fences(lines: list) -> tuple:
    """Scan every fence block.

    Returns ``(fences, immune)`` where ``fences`` lists one dict per
    block — ``{"open_line", "close_line", "char", "length",
    "language", "mismatches"}`` (``close_line`` None when the fence
    stays open, ``mismatches`` the lines of MD010 closer-shaped runs
    of the other character) — and ``immune`` is the set of 0-based
    line indices a non-fence rule must never see: every fence line
    (openers and closers) plus every interior line of every block.
    """
    fences: list = []
    immune: set = set()
    index = 0
    total = len(lines)
    while index < total:
        opener = _parse_opener(lines[index])
        if opener is None:
            index += 1
            continue
        char, length, language = opener
        block = {
            "open_line": index,
            "close_line": None,
            "char": char,
            "length": length,
            "language": language,
            "mismatches": [],
        }
        immune.add(index)
        scan = index + 1
        while scan < total:
            run = _closing_run(lines[scan], char)
            if run is not None and run >= length:
                block["close_line"] = scan
                immune.add(scan)
                break
            other = _closing_run(
                lines[scan], "`" if char == "~" else "~"
            )
            if other is not None and other >= 3:
                block["mismatches"].append((scan, other))
            immune.add(scan)
            scan += 1
        fences.append(block)
        if block["close_line"] is None:
            # Everything to end of document stays fence interior.
            immune.update(range(index + 1, total))
            index = total
        else:
            index = block["close_line"] + 1
    return fences, immune


def _strip_inline_code(line: str) -> str:
    """Remove inline code spans so their content is never linted."""
    return _CODE_SPAN_RE.sub(" ", line)


def _bare_urls(line: str) -> list:
    """Bare http(s) URLs outside code spans, links, autolinks and
    link-reference definition lines."""
    if _LINK_DEF_RE.match(line):
        return []
    scrubbed = _AUTOLINK_RE.sub(" ", _MD_LINK_RE.sub(" ",
                               _strip_inline_code(line)))
    return _BARE_URL_RE.findall(scrubbed)


def _plain_links(line: str) -> list:
    """Non-image inline links as ``(text, dest, is_image)`` tuples."""
    results: list = []
    scrubbed = _strip_inline_code(line)
    for match in _PLAIN_LINK_RE.finditer(scrubbed):
        is_image = match.start() > 0 and scrubbed[match.start() - 1] == "!"
        results.append((match.group(1), match.group(2), is_image))
    return results


def _parse_heading(line: str) -> Optional[tuple]:
    """Parse an ATX heading line.

    Returns ``(level, text, closing_len)`` where ``text`` has any
    closing hash run removed and ``closing_len`` is the removed run's
    length (0 when absent), or None when the line is not an ATX
    heading. ``## ##`` parses to level 2, empty text, closing 2.
    """
    match = _ATX_HEADING_RE.match(line)
    if match is None:
        return None
    rest = match.group(3)
    if rest and rest[0] not in (" ", "\t"):
        return None
    level = len(match.group(2))
    body = rest.strip()
    closing_len = 0
    closing = _TRAILING_HASHES_RE.search(body)
    if closing and (closing.start() == 0 or body[closing.start() - 1] == " "):
        closing_len = len(closing.group(1))
        body = body[: closing.start()].rstrip()
    return level, body, closing_len


def _humanize_seconds(seconds: int) -> str:
    """ReadingTimeTool (#3928) rounding rules, verbatim family form."""
    if seconds == 0:
        return "0 s"
    if seconds < 1:
        return "< 1 s"
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    parts_h = f"{hours} h" if hours else ""
    parts_m = f"{minutes} min" if minutes else ""
    parts_s = f"{secs} s" if secs else ""
    return " ".join(part for part in (parts_h, parts_m, parts_s) if part)


# ---------------------------------------------------------------------------
# lint mode
# ---------------------------------------------------------------------------

def _run_lint(tool: Any, lines: list, max_line_length: int,
              disabled: frozenset) -> dict:
    """Run the full rule table; returns the lint result dict."""
    fences, immune = _scan_fences(lines)
    findings: list = []

    def add(code: str, line: int, message: str) -> None:
        if code in disabled:
            return
        slug, severity, hint = _RULES[code]
        findings.append({
            "code": code,
            "severity": severity,
            "line": line,
            "message": message,
            "hint": hint,
        })

    # Fence rules (MD008 / MD009 / MD010) — by definition the only
    # rules that fire on fence lines; every other rule skips the
    # ``immune`` set (fence lines + interiors) below.
    for block in fences:
        if not block["language"]:
            add("MD009", block["open_line"] + 1,
                "code fence opens without a language in its info string")
        for mismatch_line, run in block["mismatches"]:
            add("MD010", mismatch_line + 1,
                f"closing attempt uses "
                f"{'~' if block['char'] == '`' else '`'} ({run} chars) "
                f"while the fence opened with {block['char'] * block['length']}"
                f" — it does not close the fence (CommonMark)")
        if block["close_line"] is None:
            add("MD008", block["open_line"] + 1,
                f"code fence ({block['char'] * block['length']}) never "
                f"closes through end of document")

    # Single pass over prose lines (indices 0-based, reported +1).
    last_heading_level: Optional[int] = None
    h1_count = 0
    marker_counts = {marker: 0 for marker in _MARKERS}
    marker_first: dict = {}
    unordered_items: list = []  # (line_no, indent_len, marker, text)

    for index, line in enumerate(lines):
        if index in immune:
            continue
        line_no = index + 1

        # --- headings ------------------------------------------------
        heading = _parse_heading(line)
        if heading is not None:
            level, text, closing_len = heading
            if not text:
                add("MD003", line_no, "heading has empty text")
            elif closing_len and closing_len != level:
                add("MD004", line_no,
                    f"closing hash run ({closing_len}) differs from the "
                    f"opening level ({level})")
            if last_heading_level is not None and level > last_heading_level + 1:
                skipped = ", ".join(
                    f"h{depth}"
                    for depth in range(last_heading_level + 1, level)
                )
                add("MD001", line_no,
                    f"heading level jumps h{last_heading_level} -> h{level} "
                    f"(skips {skipped})")
            last_heading_level = level
            if level == 1:
                h1_count += 1
                if h1_count > 1:
                    add("MD002", line_no,
                        f"multiple level-1 headings: this is h1 #{h1_count}")

        # --- fences openers are handled above; other fence-shaped lines
        # that were not openers (backticks in info, short runs) fall
        # through as prose — deliberate, documented.

        # --- thematic breaks are never list items --------------------
        if _THEMATIC_BREAK_RE.match(line):
            continue

        # --- list items ----------------------------------------------
        unordered = _UNORDERED_ITEM_RE.match(line)
        ordered = None if unordered is not None \
            else _ORDERED_ITEM_RE.match(line)
        if unordered is not None or ordered is not None:
            if unordered is not None:
                indent_ws = unordered.group(1)
                marker = unordered.group(2)
                text = line[unordered.end():].strip()
                marker_counts[marker] += 1
                marker_first.setdefault(marker, line_no)
                unordered_items.append(
                    (line_no, len(indent_ws), marker, text)
                )
            else:
                indent_ws = ordered.group(1)
            if "\t" in indent_ws:
                add("MD007", line_no,
                    "tab in list item leading whitespace — use spaces")
            elif len(indent_ws) % 2:
                add("MD006", line_no,
                    f"list item indent is {len(indent_ws)}, not a multiple "
                    f"of 2")

        # --- line-level rules ----------------------------------------
        stripped = line.rstrip()
        trailing_spaces = line[len(line.rstrip(" ")):]
        if stripped and len(trailing_spaces) >= 2:
            add("MD013", line_no,
                f"line ends with {len(trailing_spaces)} spaces — a hard "
                f"break many editors strip invisibly; prefer a backslash "
                f"break")
        if len(stripped) > max_line_length and \
                not _URL_HINT_RE.search(line):
            add("MD014", line_no,
                f"line is {len(stripped)} characters after trailing "
                f"whitespace, over the {max_line_length}-character limit "
                f"(URL-bearing lines exempt)")

        html = _HTML_BLOCK_RE.match(line)
        if html is not None and html.group(1) is not None and \
                html.group(1).lower() not in _BLOCK_TAGS:
            html = None
        if html is not None:
            tag = "!--" if html.group(1) is None else html.group(1).lower()
            add("MD012", line_no,
                f"raw HTML block (<{tag}>) — many Markdown pipelines "
                f"strip raw HTML")

        urls = _bare_urls(line)
        if urls:
            add("MD011", line_no,
                f"{len(urls)} bare URL(s) outside links/autolinks "
                f"(first: {_cap(urls[0])}) — wrap as <url> or [text](url)")

        for text_, dest, is_image in _plain_links(line):
            if is_image:
                continue
            if not text_ and not dest.strip():
                add("MD016", line_no,
                    'empty link "[]()" — neither text nor destination')
            elif text_ and not dest.strip():
                add("MD016", line_no,
                    f"missing link destination "
                    f"[{_cap(text_, 30)!r}]() — the link goes nowhere")

    # MD005 — document-level marker mixing summary.
    used = [marker for marker in _MARKERS if marker_counts[marker]]
    if len(used) > 1:
        dominant = max(
            _MARKERS,
            key=lambda marker: (
                marker_counts[marker], -_MARKERS.index(marker)
            ),
        )
        first_other = min(
            marker_first[marker]
            for marker in used if marker != dominant
        )
        breakdown = ", ".join(
            f"{marker!r} x{marker_counts[marker]}" for marker in used
        )
        add("MD005", first_other,
            f"unordered list markers mixed in one document ({breakdown}); "
            f"dominant is {dominant!r}, first differing line "
            f"{first_other}")

    # MD015 — capitalization within contiguous same-indent runs.
    run: list = []
    runs: list = []

    def flush() -> None:
        nonlocal run
        if run:
            runs.append(run)
            run = []

    previous_line: Optional[int] = None
    previous_indent = -1
    for item in unordered_items:
        line_no, indent_len, _marker, text = item
        letter = text[:1]
        participates = bool(letter) and ("A" <= letter <= "Z" or
                                         "a" <= letter <= "z")
        contiguous = (previous_line is not None
                      and line_no == previous_line + 1
                      and indent_len == previous_indent)
        if not contiguous:
            flush()
        run.append((line_no, participates, letter))
        previous_line, previous_indent = line_no, indent_len
    flush()
    for entries in runs:
        reference = next(
            (entry for entry in entries if entry[1]), None
        )
        if reference is None:
            continue
        ref_letter = reference[2]
        ref_upper = ref_letter.isupper()
        for line_no, participates, letter in entries:
            if not participates:
                continue
            if letter.isupper() != ref_upper:
                add("MD015", line_no,
                    f"list item capitalization inconsistent — first "
                    f"lettered item starts {ref_letter!r} "
                    f"({'upper' if ref_upper else 'lower'}), this item "
                    f"starts {letter!r}")
                break

    findings.sort(key=lambda finding: (
        finding["line"], finding["code"], finding["message"]
    ))
    total = len(findings)
    truncated = total > tool.MAX_FINDINGS
    ok = not any(
        finding["severity"] in ("error", "warning")
        for finding in findings
    )
    return {
        "mode": "lint",
        "ok": ok,
        "line_count": len(lines),
        "finding_count": total,
        "findings_truncated": truncated,
        "findings": findings[: tool.MAX_FINDINGS],
    }


# ---------------------------------------------------------------------------
# profile mode
# ---------------------------------------------------------------------------

def _run_profile(tool: Any, lines: list) -> dict:
    """Profile headings, lists, fences, links, words and reading."""
    fences, immune = _scan_fences(lines)

    headings: list = []
    by_level: dict = {}
    unordered_items = 0
    ordered_items = 0
    languages: dict = {}
    without_lang = 0
    unclosed = 0
    links_total = 0
    links_internal = 0
    links_external = 0

    for block in fences:
        if block["language"]:
            languages[block["language"]] = (
                languages.get(block["language"], 0) + 1
            )
        else:
            without_lang += 1
        if block["close_line"] is None:
            unclosed += 1

    prose_lines: list = []
    for index, line in enumerate(lines):
        if index in immune:
            continue
        prose_lines.append(line)

        heading = _parse_heading(line)
        if heading is not None:
            level, text, _closing = heading
            headings.append({
                "line": index + 1,
                "level": level,
                "text": _cap(text, 60),
            })
            by_level[level] = by_level.get(level, 0) + 1
        elif not _THEMATIC_BREAK_RE.match(line):
            if _UNORDERED_ITEM_RE.match(line):
                unordered_items += 1
            elif _ORDERED_ITEM_RE.match(line):
                ordered_items += 1

        for text_, dest, is_image in _plain_links(line):
            if is_image or not dest.strip():
                continue
            links_total += 1
            token = dest.split()[0]
            if _SCHEME_RE.match(token):
                links_external += 1
            else:
                links_internal += 1

    words = sum(len(_WORD_RE.findall(line)) for line in prose_lines)
    cjk_chars = sum(len(_CJK_RE.findall(line)) for line in prose_lines)
    raw_seconds = Fraction(words * 60, _READING_WPM)
    seconds = 0 if words == 0 else ceil(raw_seconds)

    return {
        "mode": "profile",
        "line_count": len(lines),
        "word_count": words,
        "cjk_char_count": cjk_chars,
        "headings": {
            "count": len(headings),
            "max_depth": max(by_level) if by_level else 0,
            "by_level": {str(level): by_level[level]
                         for level in sorted(by_level)},
            "items": headings,
        },
        "lists": {
            "list_blocks": _count_list_blocks(lines, immune),
            "unordered_items": unordered_items,
            "ordered_items": ordered_items,
        },
        "code_fences": {
            "count": len(fences),
            "closed": len(fences) - unclosed,
            "unclosed": unclosed,
            "languages": languages,
            "without_lang": without_lang,
        },
        "links": {
            "total": links_total,
            "internal": links_internal,
            "external": links_external,
        },
        "reading": {
            "wpm": _READING_WPM,
            "seconds": seconds,
            "humanized": _humanize_seconds(seconds),
        },
    }


def _count_list_blocks(lines: list, immune: set) -> int:
    """Count maximal runs of list-item lines (any marker, unordered or
    ordered) on non-immune lines; a blank or non-item line ends a
    block."""
    blocks = 0
    in_block = False
    for index, line in enumerate(lines):
        if index in immune or _THEMATIC_BREAK_RE.match(line):
            in_block = False
            continue
        is_item = bool(
            _UNORDERED_ITEM_RE.match(line) or _ORDERED_ITEM_RE.match(line)
        )
        if is_item and not in_block:
            blocks += 1
        in_block = is_item
    return blocks


# ---------------------------------------------------------------------------
# fix_hints mode
# ---------------------------------------------------------------------------

def _run_fix_hints(tool: Any, lines: list, close_unclosed_fence: bool,
                   strip_trailing_spaces: bool, max_line_length: int,
                   disabled: frozenset) -> dict:
    """Apply the two safe textual repairs and re-lint the result."""
    fences, immune = _scan_fences(lines)

    fixed = list(lines)
    applied: list = []

    if strip_trailing_spaces:
        stripped_count = 0
        for index, line in enumerate(fixed):
            if index in immune:
                continue
            # Keep content lines ending with 2+ spaces (CommonMark
            # hard break); strip every other trailing-whitespace run
            # — single spaces, tabs, mixed runs and whitespace-only
            # lines (a whitespace-only line parses as blank).
            if line.strip() and len(line) - len(line.rstrip(" ")) >= 2:
                continue
            trimmed = line.rstrip()
            if trimmed != line:
                fixed[index] = trimmed
                stripped_count += 1
        if stripped_count:
            applied.append({
                "action": "strip_trailing_spaces",
                "count": stripped_count,
            })

    if close_unclosed_fence:
        for block in fences:
            if block["close_line"] is None:
                fixed.append(block["char"] * block["length"])
                applied.append({
                    "action": "close_unclosed_fence",
                    "line": block["open_line"] + 1,
                    "fence": block["char"] * block["length"],
                })
                break

    fixed_text = "\n".join(fixed) + "\n"
    relint = _run_lint(tool, fixed, max_line_length, disabled)
    return {
        "mode": "fix_hints",
        "fixed_text": fixed_text,
        "applied": applied,
        "remaining_count": relint["finding_count"],
        "remaining_truncated": relint["findings_truncated"],
        "remaining": relint["findings"],
    }


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

class MarkdownLintTool(Tool):
    """Whole-document Markdown quality linter built purely on the
    stdlib.

    The tool never touches the filesystem or the network — it
    examines Markdown *text*: lint it against the documented 16-rule
    table (headings, lists, code fences, bare URLs, raw HTML, hard
    breaks, long lines, empty links) with fence-interior immunity for
    every rule, profile its structure and reading stats, or apply
    safe textual fix hints. See the module docstring for the full
    rule table, the mode reference and the CommonMark fence rules.

    Class attributes:
        MODES (tuple): Supported modes (lint, profile, fix_hints).
        RULE_CODES (tuple): All implemented rule codes.
        MAX_FINDINGS (int): Findings list cap per lint run.
        MAX_LINE_LENGTH_BOUNDS (tuple): min/max for the option.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "markdown_lint_tool"
    description: str = (
        "Whole-document Markdown quality linter — pure Python stdlib, "
        "no files, no network, no third-party parser. lint mode checks "
        "a documented 16-rule table with full fence-interior immunity "
        "(CodeBlockDetector family fence tracking): heading level "
        "jumps, multiple h1, empty headings, inconsistent closing "
        "hashes, mixed unordered markers, non-2-space list indents, "
        "tabs in list indent, unclosed code fences with the opening "
        "line, fences without a language, wrong-character closing "
        "fences, bare URLs, raw block-level HTML, 2-space hard-break "
        "ambiguity, over-120-character lines with a URL exemption, "
        "inconsistent sibling item capitalization and empty links "
        "[]()/[text](), each finding carrying code, severity, 1-based "
        "line, message and hint; profile mode reports the heading tree "
        "(per level, max depth, items), list and fence statistics with "
        "a language histogram, the internal/external link census, "
        "family-tokenizer word counts (CJK-aware) and 238-wpm reading "
        "stats; fix_hints applies only safe textual repairs — closing "
        "an unclosed fence and stripping non-hard-break trailing "
        "whitespace — and re-lints what remains."
    )

    MODES: ClassVar[tuple] = ("lint", "profile", "fix_hints")
    RULE_CODES: ClassVar[tuple] = _RULE_CODES
    MAX_FINDINGS: ClassVar[int] = 200
    MAX_LINE_LENGTH_BOUNDS: ClassVar[tuple] = (40, 500)

    max_input_chars: int = 100_000

    def execute(
        self,
        mode: Any = None,
        markdown_text: Any = None,
        max_line_length: Any = None,
        rules: Any = None,
        close_unclosed_fence: Any = None,
        strip_trailing_spaces: Any = None,
    ) -> dict:
        """Lint, profile or fix-hint Markdown text.

        Args:
            mode (str): One of ``lint``, ``profile`` or ``fix_hints``.
            markdown_text (str): The Markdown text. A single leading
                UTF-8 BOM is stripped silently and CRLF / CR line
                endings are normalized to LF before scanning, so line
                numbers match the LF twin document.
            max_line_length (int): Width threshold for rule MD014.
                Default 120, range 40..500. Lint and fix_hints modes.
            rules (dict): Map a rule code (MD001..MD016) to False to
                disable that single rule for the call. Lint and
                fix_hints modes.
            close_unclosed_fence (bool): Append a matching closing
                fence for a fence open at end of document in fix_hints
                mode. Default True. Fix_hints mode only.
            strip_trailing_spaces (bool): Strip trailing whitespace
                that is not a 2+-plain-space hard break in fix_hints
                mode. Default True. Fix_hints mode only.

        Returns:
            dict: ``lint`` → ``{mode, ok, line_count, finding_count,
            findings_truncated, findings}`` with each finding
            ``{code, severity, line, message, hint}``; ``profile`` →
            ``{mode, line_count, word_count, cjk_char_count,
            headings, lists, code_fences, links, reading}``;
            ``fix_hints`` → ``{mode, fixed_text, applied,
            remaining_count, remaining_truncated, remaining}``.

        Raises:
            ValueError: If any argument is malformed or the input is
                empty, whitespace-only or oversized.
        """
        if mode not in self.MODES:
            raise _err(f"mode must be one of {self.MODES}, got {mode!r}")

        provided = {
            "max_line_length": max_line_length, "rules": rules,
            "close_unclosed_fence": close_unclosed_fence,
            "strip_trailing_spaces": strip_trailing_spaces,
        }
        for option, value in provided.items():
            if value is not None and option not in _MODE_OPTIONS[mode]:
                raise _err(
                    f"{option!r} is not a {mode} mode option "
                    f"(allowed: {sorted(_MODE_OPTIONS[mode])})"
                )

        if not isinstance(markdown_text, str):
            raise _err(
                "markdown_text must be a string, got "
                f"{type(markdown_text).__name__}"
            )
        if not markdown_text:
            raise _err("markdown_text must be non-empty")
        if len(markdown_text) > self.max_input_chars:
            raise _err(
                f"markdown_text exceeds the {self.max_input_chars:,}-"
                f"character limit (got {len(markdown_text):,} characters)"
            )
        if not markdown_text.strip():
            raise _err("markdown_text must contain non-whitespace content")

        work_text = markdown_text
        if work_text.startswith("\ufeff"):
            work_text = work_text[1:]
        work_text = work_text.replace("\r\n", "\n").replace("\r", "\n")
        lines = work_text.split("\n")
        # A trailing terminator leaves one empty trailing line; keep
        # line numbering identical to the raw split.
        if lines and lines[-1] == "":
            lines.pop()

        if mode == "lint":
            max_line_length = self._resolve_max_line_length(
                max_line_length
            )
            disabled = self._resolve_rules(rules)
            return _run_lint(self, lines, max_line_length, disabled)
        if mode == "profile":
            return _run_profile(self, lines)
        for option, value in (
            ("close_unclosed_fence", close_unclosed_fence),
            ("strip_trailing_spaces", strip_trailing_spaces),
        ):
            if value is not None and not isinstance(value, bool):
                raise _err(f"{option} must be a boolean, got {value!r}")
        return _run_fix_hints(
            self, lines,
            True if close_unclosed_fence is None else close_unclosed_fence,
            True if strip_trailing_spaces is None else strip_trailing_spaces,
            self._resolve_max_line_length(max_line_length),
            self._resolve_rules(rules),
        )

    # -- validation helpers ------------------------------------------------

    @classmethod
    def _resolve_max_line_length(cls, value: Any) -> int:
        """Validate the optional MD014 width threshold."""
        if value is None:
            return 120
        low, high = cls.MAX_LINE_LENGTH_BOUNDS
        if isinstance(value, bool) or not isinstance(value, int):
            raise _err(
                f"max_line_length must be an integer, got {value!r}"
            )
        if not low <= value <= high:
            raise _err(
                f"max_line_length must be between {low} and {high}, "
                f"got {value}"
            )
        return value

    @classmethod
    def _resolve_rules(cls, rules: Any) -> frozenset:
        """Validate the per-rule disable map; returns disabled codes."""
        if rules is None:
            return frozenset()
        if not isinstance(rules, dict):
            raise _err(
                f"rules must be a dict, got {type(rules).__name__}"
            )
        disabled = set()
        for key, value in rules.items():
            if key not in _RULES:
                raise _err(
                    f"rules keys must be one of {list(_RULE_CODES)}, "
                    f"got {key!r}"
                )
            if not isinstance(value, bool):
                raise _err(
                    f"rules[{key!r}] must be a boolean, got {value!r}"
                )
            if not value:
                disabled.add(key)
        return frozenset(disabled)
