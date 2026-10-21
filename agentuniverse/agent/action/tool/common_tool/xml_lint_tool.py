#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: xml_lint_tool.py

"""Structural quality linter for XML documents, built entirely on the
standard library's ElementTree / expat stack — no third-party XML
dependency, no file I/O, no network.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network review layer for agents that emit or
receive XML. The existing XML tools all *consume* the format:
XmlPathTool (#3744) runs compact XPath-style queries against a parsed
document, XmlReader (PR #3328) ingests XML into the knowledge stack,
and the XmlSplitter (#827) chunks documents for embedding — none of
them examines a document's structural quality. A document whose
duplicate attributes expat rejects, whose ``&foo;`` entity never
existed, or whose nesting runs fifteen levels deep reaches every
downstream consumer as an opaque parse failure or an unreadable blob.
XmlLintTool sits in front of them: lint the structure, profile the
topology, or compute safe formatting suggestions.

Everything runs offline on the ``xml_text`` string. Parsing goes
through :mod:`xml.etree.ElementTree` over UTF-8 bytes (so documents
may carry an ``encoding=`` declaration), with comments and processing
instructions retained via a ``TreeBuilder`` so they can be counted; a
second pass over the same bytes drives raw expat purely as a position
oracle — expat's ``CurrentLineNumber`` / ``CurrentColumnNumber`` are
recorded for every start tag in document order, which ElementTree
itself does not expose. A single leading UTF-8 BOM is stripped before
any parsing (rule XML007 reports it), so line and column numbers —
1-based, like the rest of the tool family — always refer to the text
after the BOM, exactly where the parser looked. Columns are 1-based
integers (expat's 0-based offset plus one); document-level findings
use column 1.

Security — XXE protection: before ANY parsing, a character-level
pre-scan rejects documents containing ``<!DOCTYPE`` or ``<!ENTITY``
markup, the same guard XmlPathTool (#3744) uses and XmlReader (#3328)
endorses. DTDs and entities are the vehicle for XXE and
entity-expansion attacks, so the tool refuses to hand such documents
to the parser at all: XML002 is a hard error citing that security
rationale, and the parse-dependent rules are skipped (the raw-line
rules — BOM, long lines, encoding declaration — still run, they never
touch the parser). The scan is case-sensitive — ``<!DOCTYPE`` and
``<!ENTITY`` are the only spellings valid XML allows — and
conservative: mentions inside comments or CDATA are rejected too.
Since no entity can ever be declared through this path, any ``&name;``
other than the five predefined entities that survives to the parser
is undefined by construction and surfaces as XML003.

Supported modes
---------------
* ``lint`` — run the rule table below over ``xml_text`` and return
  ``ok`` plus ``findings``. Each finding is ``{code, severity, line,
  col, message, hint}``. ``ok`` is True only when no finding of
  severity error was raised (every rule in the table is either error
  or info; info-only documents stay ok). When expat rejects the text
  the failure is mapped to XML001..XML006 with expat's own position
  (verified against real expat over a 30-document malformed matrix),
  and the parse-dependent rules are skipped; the raw-line rules still
  run. Findings are sorted by (line, col, code), capped at 200
  entries (``finding_count`` keeps the true total and
  ``findings_truncated`` flags the cut).
* ``profile`` — topology statistics over the parsed document: root
  tag, element count, maximum depth with the path of the deepest
  element, the ten most frequent element tags, attribute count, text
  statistics (non-empty text/tail node count, total characters,
  longest single text node), distinct namespaces in use, and
  processing-instruction / comment counts. Profile mode raises
  ValueError on a DTD-bearing, unparseable or surrogate-broken
  document because it has nothing to report.
* ``fix_hints`` — safe suggestions only, never applied: a BOM strip
  note (line 1, col 1 — the BOM is legal, stripping it is a choice),
  and a pretty-print suggestion — the canonical 2-space
  re-serialization via ``ET.indent(tree, space="  ")`` plus
  ``ET.tostring`` — with a unified-diff summary capped at 40 lines.
  ``applied`` is always False; nothing is written back or executed.
  Whitespace stripping per line is deliberately NOT offered:
  trailing whitespace inside text content is *literal* in XML and
  trimming it changes the document, so the tool refuses the
  temptation. The canonical form renames namespace prefixes (ns0,
  ns1, ...) and renders self-closing tags as ``<b />``; when
  namespaces are in use or the source carries an XML declaration the
  suggestion carries an explicit note about those rewrites. A comment
  / PI preserving parse backs the suggestion, and mixed-content text
  is left in place (``ET.indent`` only touches whitespace-only
  nodes).

Rule table (mode ``lint``)
--------------------------
======== ================== ====== =================================================== ===========================================================
Code     Slug               Sev.   Trigger (exact)                                      Hint
======== ================== ====== =================================================== ===========================================================
XML001   syntax_error       error  expat rejects the document and the code is           fix the reported position first — quality
                                  none of the mapped ones below: mismatched tag,        rules need a well-formed document
                                  junk after the document element, invalid token,
                                  unclosed token / CDATA section, invalid character
                                  reference, text outside the root; line/col are
                                  expat's own, 1-based, message verbatim
XML002   dtd_or_entity      error  the pre-parse scan finds ``<!DOCTYPE`` or            remove it: DTDs and entities are the vehicle
                                  ``<!ENTITY`` (first occurrence, located); the         for XXE and entity-expansion attacks, so
                                  document is never parsed — the XXE guard of           the tool refuses to parse it at all
                                  XmlPathTool (#3744); conservative: comment and
                                  CDATA mentions count; parse-dependent rules are
                                  skipped, raw-line rules still run
XML003   undeclared_entity  error  expat code 11 ``undefined entity`` — an              use &amp; / &lt; / &gt; / &apos; / &quot;
                                  ``&name;`` reference beyond the five predefined       or a character reference &#...; — defining
                                  entities or a character reference; the entity         entities needs a DTD, which this tool
                                  name is extracted at the reported column when         rejects outright
                                  the source shows one there (attribute-value
                                  positions report expat's generic message)
XML004   duplicate_attri-   error  expat code 8 ``duplicate attribute`` — the same      rename one of them — XML forbids repeated
         bute                       element repeats an attribute name; the repeated      attribute names on a single element
                                  name is extracted at the reported column when
                                  the source shows one there
XML005   root_missing       error  the document is empty or whitespace-only (expat      add the root element — an XML document
                                  ``no element found``); reported at line 1, col 1     must have exactly one
XML006   pi_or_comment_only error  non-whitespace content exists but comments and       add the root element — comments and PIs
                                  processing instructions are all of it (regex-        alone are not a document
                                  stripped proof, reported at line 1, col 1)
XML007   bom                info   the text starts with a UTF-8 BOM (``\\ufeff``) —      strip it (fix_hints notes it) — legal in
                                  legal in XML, but it pollutes BOM-naive               XML, but it pollutes BOM-naive consumers
                                  consumers; the BOM is stripped before parsing,
                                  so every later position refers to the post-BOM
                                  text
XML008   very_long_line     info   a line exceeds 5,000 characters (lines split on      wrap it — thousand-character lines defeat
                                  ``\\n`` only, ``\\r`` included in the length);        review and diffs
                                  col is 5,001, the first character past the
                                  threshold; one finding per offending line
XML009   non_utf8_declared  info   the XML declaration (anchored at offset 0)           re-encode to UTF-8 or fix the declaration
                                  declares an encoding other than utf-8 / utf8         — this tool feeds UTF-8 bytes to expat,
                                  (case-insensitive) while the document carries        so a foreign declaration and the actual
                                  non-ASCII content; col points at the declared        bytes disagree wherever it matters
                                  value
XML010   empty_element      info   an element has no child elements and no text         fill it in, self-close deliberately or
                                  beyond whitespace — attributes do not count;         drop it — ``<x/>`` is often intentional,
                                  one finding per element (self-closing and            hence info
                                  ``<x></x>`` are indistinguishable after a
                                  parse)
XML011   mixed_content_     info   an element mixes child elements with non-            wrap the text in its own element — mixed
         _element                   whitespace text (its own text or any child's        content makes schema validation and
                                  tail; CDATA merges into text); one finding per       downstream processing fragile
                                  element
XML012   deeply_nested      info   an element nests deeper than ``max_depth``           flatten the structure — deep XML is hard
                                  (default 12, range 1..128); fires once per           to read and easy to misindent
                                  document at the first offending element, with
                                  its depth and path in the message
XML013   namespace_heavy    info   the document uses more than 10 distinct              prune unused namespaces — heavy namespace
                                  namespaces in use (element tags plus attribute       use obscures element identity and bloats
                                  names, ``{uri}`` forms); fires once at the           every query
                                  element whose tag or attributes cross the
                                  limit
======== ================== ====== =================================================== ===========================================================

Options and error matrix
------------------------
``max_depth`` (int, default 12, range 1..128) gates XML012. ``rules``
maps any implemented rule code to False to disable that single rule
for the call (unknown codes and non-boolean values are ValueError).
Disabling XML002 suppresses its finding but never re-enables parsing:
a DTD-bearing document is refused wholesale regardless of the rule
map — the guard is security policy, not a style preference. Element
tags are quoted in ElementTree's expanded ``{uri}name`` form
throughout findings and profile output. Profile and fix_hints accept
no options at all — any option passed with those modes is a
ValueError.

``ValueError`` is raised for: an unknown mode; a non-string or
oversized ``xml_text`` (over ``max_input_chars`` = 1,000,000
characters, the 1 MB cap); an option that does not belong to the
mode; malformed option values; and, in profile mode only, a document
the tool cannot parse (DTD guard, expat failure, or unpaired
surrogates — the reason is embedded in the message). In lint and
fix_hints modes every parser failure is a finding / structured
``parse_failed`` field, never an exception. Unpaired surrogates — a
``str`` that cannot be encoded to UTF-8 at all — lint as XML001 and
mark ``parse_failed`` in fix_hints. All findings and statistics are
exact and the run is fully deterministic.
"""

import difflib
import re
import xml.etree.ElementTree as ET
import xml.parsers.expat as expat
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# Static vocabulary
# ---------------------------------------------------------------------------

_BOM = "\ufeff"

# XXE guard markers — the only spellings valid XML allows, so the scan
# is case-sensitive (mirrors XmlPathTool #3744).
_DTD_MARKERS: tuple = ("<!DOCTYPE", "<!ENTITY")

# Rule codes -> (slug, severity, hint).
_RULES: dict = {
    "XML001": ("syntax_error", "error",
               "fix the reported position first — quality rules need a "
               "well-formed document"),
    "XML002": ("dtd_or_entity", "error",
               "remove it: DTDs and entities are the vehicle for XXE and "
               "entity-expansion attacks, so the tool refuses to parse it "
               "at all"),
    "XML003": ("undeclared_entity", "error",
               "use &amp;/&lt;/&gt;/&apos;/&quot; or a character reference "
               "&#...; — defining entities needs a DTD, which this tool "
               "rejects outright"),
    "XML004": ("duplicate_attribute", "error",
               "rename one of them — XML forbids repeated attribute names "
               "on a single element"),
    "XML005": ("root_missing", "error",
               "add the root element — an XML document must have exactly "
               "one"),
    "XML006": ("pi_or_comment_only", "error",
               "add the root element — comments and PIs alone are not a "
               "document"),
    "XML007": ("bom", "info",
               "strip it (fix_hints notes it) — legal in XML, but it "
               "pollutes BOM-naive consumers"),
    "XML008": ("very_long_line", "info",
               "wrap it — thousand-character lines defeat review and "
               "diffs"),
    "XML009": ("non_utf8_declared", "info",
               "re-encode to UTF-8 or fix the declaration — this tool "
               "feeds UTF-8 bytes to expat, so a foreign declaration and "
               "the actual bytes disagree wherever it matters"),
    "XML010": ("empty_element", "info",
               "fill it in, self-close deliberately or drop it — <x/> is "
               "often intentional, hence info"),
    "XML011": ("mixed_content_element", "info",
               "wrap the text in its own element — mixed content makes "
               "schema validation and downstream processing fragile"),
    "XML012": ("deeply_nested", "info",
               "flatten the structure — deep XML is hard to read and "
               "easy to misindent"),
    "XML013": ("namespace_heavy", "info",
               "prune unused namespaces — heavy namespace use obscures "
               "element identity and bloats every query"),
}
_RULE_CODES: tuple = tuple(_RULES)

# Per-mode option gates for the error matrix.
_LINT_OPTIONS: frozenset = frozenset({"max_depth", "rules"})
_PROFILE_OPTIONS: frozenset = frozenset()
_FIX_OPTIONS: frozenset = frozenset()
_MODE_OPTIONS: dict = {
    "lint": _LINT_OPTIONS, "profile": _PROFILE_OPTIONS,
    "fix_hints": _FIX_OPTIONS,
}

# Fixed thresholds (documented in the rule table).
_LONG_LINE_THRESHOLD: int = 5000
_NAMESPACE_LIMIT: int = 10
_FINDING_CAP: int = 200
_DIFF_CAP: int = 40

# The XML declaration must sit at offset 0 of the (post-BOM) text; the
# encoding pseudo-attribute is lowercase per the XML specification.
_DECL_ENCODING_RE = re.compile(
    r"\A<\?xml\b[^>]*?encoding\s*=\s*(['\"])(.*?)\1", re.DOTALL)

# Comment / PI stripping used only to prove pi_or_comment_only.
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_PI_RE = re.compile(r"<\?.*?\?>", re.DOTALL)

# Extractions at an expat-reported column (XML name syntax).
_NAME_AT_RE = re.compile(r"[A-Za-z_:][A-Za-z0-9_.:\-]*")
_ENTITY_AT_RE = re.compile(r"&([A-Za-z_:][A-Za-z0-9_.:\-]*);")

# Encoding values that mean UTF-8 (label comparison is case-insensitive).
_UTF8_LABELS: frozenset = frozenset({"utf-8", "utf8"})

# Expat error codes mapped to dedicated rules; everything else is XML001.
_EXPAT_NO_ELEMENTS = 3       # "no element found"
_EXPAT_DUPLICATE_ATTRIBUTE = 8
_EXPAT_UNDEFINED_ENTITY = 11


def _err(message: str) -> ValueError:
    """Return the ValueError every validation branch raises."""
    return ValueError(message)


def _finding(code: str, line: int, col: int, message: str) -> dict:
    """Assemble one finding dict from the rule table."""
    _slug, severity, hint = _RULES[code]
    return {
        "code": code, "severity": severity,
        "line": line, "col": col, "message": message, "hint": hint,
    }


def _locate(text: str, index: int) -> tuple:
    """1-based (line, col) of a character index, counting characters."""
    line = text.count("\n", 0, index) + 1
    col = index - (text.rfind("\n", 0, index) + 1) + 1
    return line, col


def _display_path(path: str, cap: int = 100) -> str:
    """Cap a profile path for messages."""
    return path if len(path) <= cap else path[: cap - 3] + "..."


def _is_element(node: Any) -> bool:
    """True for a real element (comments / PIs carry function tags)."""
    return isinstance(node.tag, str)


def _strip_comments_and_pis(text: str) -> str:
    """Remove well-formed comments and PIs (pi_or_comment_only proof)."""
    return _PI_RE.sub("", _COMMENT_RE.sub("", text))


def _find_dtd_marker(text: str):
    """First ``<!DOCTYPE`` / ``<!ENTITY`` occurrence, or None.

        Character-level and case-sensitive — the two markers are the
        only spellings valid XML allows — and conservative: mentions
        inside comments or CDATA are flagged too (same policy as
        XmlPathTool #3744).
    """
    best_index, best_marker = -1, None
    for marker in _DTD_MARKERS:
        index = text.find(marker)
        if index >= 0 and (best_index < 0 or index < best_index):
            best_index, best_marker = index, marker
    if best_index < 0:
        return None
    return best_index, best_marker


def _encode(text: str):
    """UTF-8 encode, mapping unpaired surrogates to None."""
    try:
        return text.encode("utf-8")
    except UnicodeEncodeError:
        return None


def _parse(payload: bytes) -> ET.Element:
    """Parse guarded UTF-8 bytes with comments and PIs retained."""
    builder = ET.TreeBuilder(insert_comments=True, insert_pis=True)
    return ET.fromstring(payload, parser=ET.XMLParser(target=builder))


def _message_only(parse_error: ET.ParseError) -> str:
    """expat's message without the redundant position suffix."""
    message = parse_error.msg or str(parse_error)
    return message.rsplit(": line ", 1)[0]


def _source_line(text: str, line: int):
    """The 1-based source line, or None when out of range."""
    lines = text.split("\n")
    if 1 <= line <= len(lines):
        return lines[line - 1]
    return None


def _name_at(text: str, line: int, col: int):
    """An XML name starting exactly at a reported 1-based column."""
    source = _source_line(text, line)
    if source is not None and 1 <= col <= len(source):
        match = _NAME_AT_RE.match(source, col - 1)
        if match:
            return match.group(0)
    return None


def _entity_at(text: str, line: int, col: int):
    """An ``&name;`` reference starting exactly at a 1-based column."""
    source = _source_line(text, line)
    if source is not None and 1 <= col <= len(source):
        match = _ENTITY_AT_RE.match(source, col - 1)
        if match:
            return match.group(1)
    return None


def _map_parse_error(text: str, exc: ET.ParseError) -> dict:
    """Map one expat failure to its dedicated finding (XML001..XML006)."""
    position = getattr(exc, "position", None) or (1, 0)
    line = position[0] or 1
    col = (position[1] or 0) + 1
    code = getattr(exc, "code", None)
    message = _message_only(exc)

    if code == _EXPAT_NO_ELEMENTS:
        if not text.strip():
            return _finding(
                "XML005", 1, 1,
                "no root element: the document is empty or "
                "whitespace-only" + (f" (expat: {message})" if message else ""),
            )
        if not _strip_comments_and_pis(text).strip():
            return _finding(
                "XML006", 1, 1,
                "no root element: the document contains only comments "
                "and/or processing instructions"
                + (f" (expat: {message})" if message else ""),
            )
        return _finding("XML001", line, col, message)

    if code == _EXPAT_DUPLICATE_ATTRIBUTE:
        name = _name_at(text, line, col)
        detail = f"duplicate attribute {name!r}" if name else message
        return _finding("XML004", line, col, detail)

    if code == _EXPAT_UNDEFINED_ENTITY:
        name = _entity_at(text, line, col)
        if name:
            return _finding(
                "XML003", line, col,
                f"undefined entity &{name}; — only the five predefined "
                "entities and character references are available (DTDs "
                "are rejected before parsing)",
            )
        return _finding("XML003", line, col, message)

    return _finding("XML001", line, col, message)


# ---------------------------------------------------------------------------
# Position oracle (raw expat) and the tree walk
# ---------------------------------------------------------------------------

def _start_positions(payload: bytes) -> list:
    """(line, 0-based col) of every start tag, in document order.

        ElementTree does not expose source positions, so this drives
        expat — the very engine ET uses — purely to record
        ``CurrentLineNumber`` / ``CurrentColumnNumber`` for each start
        element. The bytes already parsed cleanly through ET, so this
        pass cannot fail; its i-th entry aligns with the i-th real
        element of the pre-order walk (comments and PIs never fire
        StartElementHandler).
    """
    parser = expat.ParserCreate()
    positions: list = []
    parser.StartElementHandler = (
        lambda name, attrs: positions.append(
            (parser.CurrentLineNumber, parser.CurrentColumnNumber)
        )
    )
    parser.Parse(payload, True)
    return positions


def _walk(root: ET.Element) -> list:
    """Pre-order (element, depth, parent_index) records.

        Comments and processing instructions are kept in the walk (for
        counting) but flagged as non-elements so callers can skip them.
        Iterative on purpose: recursion would overflow on deeply
        nested documents that the depth rule exists to flag.
    """
    order: list = []
    stack: list = [(root, 1, -1)]
    while stack:
        node, depth, parent = stack.pop()
        index = len(order)
        order.append((node, depth, parent))
        for child in reversed(node):
            stack.append((child, depth + 1, index))
    return order


def _path_of(order: list, index: int) -> str:
    """Tag path of a walked element, root first, '/'-joined."""
    tags: list = []
    while index >= 0:
        node, _depth, parent = order[index]
        tags.append(str(node.tag))
        index = parent
    return "/".join(reversed(tags))


def _namespace_of(name: str):
    """The URI of an ElementTree ``{uri}name``, or None."""
    if name.startswith("{"):
        end = name.find("}")
        if end > 0:
            return name[1:end]
    return None


def _collect(order: list):
    """Shared statistics over the walked tree.

        Returns (stats, element_index_of) where stats feeds profile
        mode; element_index_of maps a walk record index to its
        real-element ordinal (the index into the position oracle).
    """
    tag_counts: dict = {}
    namespaces: dict = {}
    attribute_count = 0
    text_node_count = 0
    text_length_total = 0
    text_length_max = 0
    pi_count = 0
    comment_count = 0
    element_count = 0
    element_index_of: dict = {}

    for index, (node, _depth, _parent) in enumerate(order):
        if node.tag is ET.Comment:
            comment_count += 1
            continue
        if node.tag is ET.ProcessingInstruction:
            pi_count += 1
            continue
        element_index_of[index] = element_count
        element_count += 1
        tag_counts[node.tag] = tag_counts.get(node.tag, 0) + 1
        attribute_count += len(node.attrib)
        for name in [node.tag, *node.attrib]:
            uri = _namespace_of(name)
            if uri is not None:
                namespaces[uri] = namespaces.get(uri, 0) + 1
        for text in [node.text, *(child.tail for child in node)]:
            if text:
                text_node_count += 1
                text_length_total += len(text)
                text_length_max = max(text_length_max, len(text))

    stats = {
        "element_count": element_count,
        "tag_counts": tag_counts,
        "namespaces": namespaces,
        "attribute_count": attribute_count,
        "text_node_count": text_node_count,
        "text_length_total": text_length_total,
        "text_length_max": text_length_max,
        "pi_count": pi_count,
        "comment_count": comment_count,
    }
    return stats, element_index_of


def _top_tags(tag_counts: dict, limit: int = 10) -> list:
    """The most frequent tags: count desc, tag asc, capped at 10."""
    ranked = sorted(
        tag_counts.items(), key=lambda item: (-item[1], item[0])
    )
    return [
        {"tag": tag, "count": count} for tag, count in ranked[:limit]
    ]


# ---------------------------------------------------------------------------
# lint mode
# ---------------------------------------------------------------------------

def _raw_line_findings(text: str, disabled: frozenset) -> list:
    """The rules that never touch the parser: XML008 and XML009."""
    findings: list = []
    if "XML008" not in disabled:
        for number, line in enumerate(text.split("\n"), start=1):
            if len(line) > _LONG_LINE_THRESHOLD:
                findings.append(_finding(
                    "XML008", number, _LONG_LINE_THRESHOLD + 1,
                    f"line {number} is {len(line):,} characters long "
                    f"(threshold {_LONG_LINE_THRESHOLD:,})",
                ))
    if "XML009" not in disabled:
        match = _DECL_ENCODING_RE.match(text)
        if match:
            declared = match.group(2)
            if declared.lower() not in _UTF8_LABELS and any(
                ord(char) > 0x7F for char in text
            ):
                line, col = _locate(text, match.start(2))
                findings.append(_finding(
                    "XML009", line, col,
                    f"XML declaration says encoding={declared!r} but the "
                    "document carries non-ASCII content while the tool "
                    "parses UTF-8 bytes",
                ))
    return findings


def _structure_findings(
    order: list, positions: list, max_depth: int, disabled: frozenset,
) -> list:
    """Parse-dependent rules: XML010, XML011, XML012, XML013.

        ``ordinal`` is the running count of real elements seen so far
        minus one — the index of the current element's entry in the
        position oracle, which records exactly the real-element start
        tags in document order.
    """
    findings: list = []
    deepest_done = "XML012" in disabled
    ns_done = "XML013" in disabled
    seen_namespaces: set = set()
    ordinal = -1

    for index, (node, depth, _parent) in enumerate(order):
        if not _is_element(node):
            continue
        ordinal += 1
        if "XML010" not in disabled:
            text = node.text or ""
            if len(node) == 0 and not text.strip():
                detail = (
                    "whitespace-only text" if text else "no text"
                )
                line, col0 = positions[ordinal]
                findings.append(_finding(
                    "XML010", line, col0 + 1,
                    f"element {node.tag!r} is empty ({detail}, no child "
                    "elements) — may be intentional",
                ))
        if "XML011" not in disabled and len(node) > 0:
            mixed = bool((node.text or "").strip()) or any(
                (child.tail or "").strip() for child in node
            )
            if mixed:
                line, col0 = positions[ordinal]
                findings.append(_finding(
                    "XML011", line, col0 + 1,
                    f"element {node.tag!r} mixes child elements with "
                    "non-whitespace text content",
                ))
        if not deepest_done and depth > max_depth:
            line, col0 = positions[ordinal]
            findings.append(_finding(
                "XML012", line, col0 + 1,
                f"element {node.tag!r} nests {depth} levels deep at "
                f"{_display_path(_path_of(order, index))} "
                f"(threshold {max_depth})",
            ))
            deepest_done = True
        if not ns_done:
            crossed = False
            for name in [node.tag, *node.attrib]:
                uri = _namespace_of(name)
                if uri is not None and uri not in seen_namespaces:
                    seen_namespaces.add(uri)
                    if len(seen_namespaces) > _NAMESPACE_LIMIT:
                        crossed = True
            if crossed:
                line, col0 = positions[ordinal]
                findings.append(_finding(
                    "XML013", line, col0 + 1,
                    f"element {node.tag!r} pushes the document past "
                    f"{_NAMESPACE_LIMIT} distinct namespaces in use "
                    f"({len(seen_namespaces)} so far)",
                ))
                ns_done = True
    return findings


def _finalize(findings: list) -> dict:
    """Sort, cap and envelope the finding list for lint mode."""
    findings.sort(key=lambda item: (item["line"], item["col"], item["code"]))
    total = len(findings)
    truncated = total > _FINDING_CAP
    return {
        "ok": not any(f["severity"] == "error" for f in findings),
        "finding_count": total,
        "findings_truncated": truncated,
        "findings": findings[:_FINDING_CAP] if truncated else findings,
    }


def _run_lint(tool: Any, xml_text: str, max_depth: int,
              disabled: frozenset) -> dict:
    """The full lint pipeline over one document."""
    findings: list = []
    parsed = False

    bom_present = xml_text.startswith(_BOM)
    text = xml_text[1:] if bom_present else xml_text
    if bom_present and "XML007" not in disabled:
        findings.append(_finding(
            "XML007", 1, 1,
            "document starts with a UTF-8 BOM — legal in XML, but it "
            "can confuse BOM-naive consumers; positions below refer to "
            "the post-BOM text",
        ))

    findings.extend(_raw_line_findings(text, disabled))

    guard = _find_dtd_marker(text)
    if guard is not None:
        if "XML002" not in disabled:
            index, marker = guard
            line, col = _locate(text, index)
            findings.append(_finding(
                "XML002", line, col,
                f"document contains {marker} markup at line {line}: the "
                "tool refuses to parse DTDs or entities — they are the "
                "vehicle for XXE and entity-expansion attacks — so the "
                "whole document is rejected before any parsing",
            ))
        result = _finalize(findings)
        result.update(mode="lint", parsed=False)
        return result

    payload = _encode(text)
    if payload is None:
        if "XML001" not in disabled:
            findings.append(_finding(
                "XML001", 1, 1,
                "xml_text contains unpaired surrogates and cannot be "
                "encoded to UTF-8 for parsing",
            ))
        result = _finalize(findings)
        result.update(mode="lint", parsed=False)
        return result

    try:
        root = _parse(payload)
        parsed = True
    except ET.ParseError as exc:
        mapped = _map_parse_error(text, exc)
        if mapped["code"] not in disabled:
            findings.append(mapped)
        result = _finalize(findings)
        result.update(mode="lint", parsed=False)
        return result

    positions = _start_positions(payload)
    order = _walk(root)
    findings.extend(
        _structure_findings(order, positions, max_depth, disabled)
    )
    result = _finalize(findings)
    result.update(mode="lint", parsed=True)
    return result


# ---------------------------------------------------------------------------
# profile mode
# ---------------------------------------------------------------------------

def _run_profile(xml_text: str) -> dict:
    """Topology statistics; ValueError when nothing can be parsed."""
    text = xml_text[1:] if xml_text.startswith(_BOM) else xml_text
    guard = _find_dtd_marker(text)
    if guard is not None:
        index, marker = guard
        line, col = _locate(text, index)
        raise _err(
            f"profile mode requires DTD-free XML: {marker} markup at "
            f"line {line}, column {col} is rejected before parsing "
            "(XXE guard)"
        )
    payload = _encode(text)
    if payload is None:
        raise _err(
            "profile mode requires well-formed XML: xml_text contains "
            "unpaired surrogates and cannot be encoded to UTF-8"
        )
    try:
        root = _parse(payload)
    except ET.ParseError as exc:
        raise _err(
            "profile mode requires well-formed XML: "
            f"{_message_only(exc)}"
        )

    positions = _start_positions(payload)
    order = _walk(root)
    stats, index_of = _collect(order)

    depths = [depth for node, depth, _p in order if _is_element(node)]
    max_depth = max(depths) if depths else 0
    deepest_index = next(
        index for index, (node, depth, _p) in enumerate(order)
        if _is_element(node) and depth == max_depth
    )
    deepest_node = order[deepest_index][0]
    deepest_line, deepest_col0 = positions[index_of[deepest_index]]

    return {
        "mode": "profile",
        "root_tag": root.tag if _is_element(root) else "",
        "element_count": stats["element_count"],
        "max_depth": max_depth,
        "deepest_path": _display_path(_path_of(order, deepest_index)),
        "deepest_element": {
            "tag": str(deepest_node.tag),
            "line": deepest_line,
            "col": deepest_col0 + 1,
        },
        "top_tags": _top_tags(stats["tag_counts"]),
        "attribute_count": stats["attribute_count"],
        "text_node_count": stats["text_node_count"],
        "text_length_total": stats["text_length_total"],
        "text_length_max": stats["text_length_max"],
        "namespaces": sorted(stats["namespaces"]),
        "namespace_count": len(stats["namespaces"]),
        "pi_count": stats["pi_count"],
        "comment_count": stats["comment_count"],
    }


# ---------------------------------------------------------------------------
# fix_hints mode
# ---------------------------------------------------------------------------

def _run_fix_hints(xml_text: str) -> dict:
    """BOM note plus a never-applied pretty-print suggestion."""
    bom_present = xml_text.startswith(_BOM)
    text = xml_text[1:] if bom_present else xml_text
    result: dict = {
        "mode": "fix_hints",
        "applied": False,
        "parse_failed": False,
        "parse_error": None,
        "bom_suggestion": None,
        "pretty_print": None,
    }
    if bom_present:
        result["bom_suggestion"] = {
            "action": "strip_utf8_bom",
            "line": 1,
            "col": 1,
            "note": "the BOM is legal in XML; stripping it is a "
                    "choice for BOM-naive consumers — never applied "
                    "automatically",
        }

    guard = _find_dtd_marker(text)
    if guard is not None:
        _index, marker = guard
        result["parse_failed"] = True
        result["parse_error"] = (
            f"{marker} markup is rejected before any parsing (XXE "
            "guard) — no re-serialization is offered for "
            "DTD-bearing documents"
        )
        return result

    payload = _encode(text)
    if payload is None:
        result["parse_failed"] = True
        result["parse_error"] = (
            "xml_text contains unpaired surrogates and cannot be "
            "encoded to UTF-8"
        )
        return result

    try:
        root = _parse(payload)
    except ET.ParseError as exc:
        result["parse_failed"] = True
        result["parse_error"] = (
            f"XML is not well-formed: {_message_only(exc)} — fix the "
            "syntax before re-formatting"
        )
        return result

    # Canonical 2-space re-serialization (comments and PIs retained).
    ET.indent(root, space="  ")
    suggested = ET.tostring(root, encoding="unicode")
    changed = suggested != text

    notes: list = [
        "never applied automatically — adopt it manually and re-lint",
    ]
    if text.startswith("<?xml"):
        notes.append(
            "the XML declaration is not part of the re-serialization; "
            "re-add it if the consumer needs one"
        )
    stats, _index_of = _collect(_walk(_parse(payload)))
    if stats["namespaces"]:
        notes.append(
            "namespace prefixes are normalized (ns0, ns1, ...): the "
            "suggestion is semantically equivalent but textually "
            "different from prefixed sources"
        )
    notes.append(
        "the canonical form renders self-closing tags as <b /> and "
        "never touches mixed-content text"
    )

    pretty: dict = {
        "applicable": True,
        "applied": False,
        "changed": changed,
        "notes": notes,
    }
    if changed:
        original_lines = text.splitlines()
        suggested_lines = suggested.splitlines()
        diff_lines = list(difflib.unified_diff(
            original_lines, suggested_lines,
            fromfile="original", tofile="suggested", lineterm="", n=2,
        ))
        added = sum(1 for entry in diff_lines
                    if entry.startswith("+") and not
                    entry.startswith("+++"))
        removed = sum(1 for entry in diff_lines
                      if entry.startswith("-") and not
                      entry.startswith("---"))
        pretty["summary"] = {
            "lines_before": len(original_lines),
            "lines_after": len(suggested_lines),
            "added_lines": added,
            "removed_lines": removed,
        }
        pretty["unified_diff"] = diff_lines[:_DIFF_CAP]
        pretty["diff_truncated"] = len(diff_lines) > _DIFF_CAP
        pretty["suggested_text"] = suggested
    else:
        pretty["summary"] = {
            "lines_before": len(text.splitlines()),
            "lines_after": len(suggested.splitlines()),
            "added_lines": 0,
            "removed_lines": 0,
        }
        pretty["unified_diff"] = []
        pretty["diff_truncated"] = False
    result["pretty_print"] = pretty
    return result


# ---------------------------------------------------------------------------
# The tool
# ---------------------------------------------------------------------------

class XmlLintTool(Tool):
    """Lint, profile or format-hint XML documents."""

    MODES: ClassVar[set] = {"lint", "profile", "fix_hints"}
    MAX_DEPTH_LIMIT: ClassVar[int] = 128
    DEFAULT_MAX_DEPTH: ClassVar[int] = 12

    max_input_chars: int = 1_000_000

    def execute(
        self,
        mode: Any = None,
        xml_text: Any = None,
        max_depth: Any = None,
        rules: Any = None,
    ) -> dict:
        """Lint, profile or compute safe formatting hints for XML text.

        Args:
            mode (str): One of ``lint``, ``profile`` or ``fix_hints``.
            xml_text (str): The XML document to examine. Empty and
                comment-only documents lint to root_missing /
                pi_or_comment_only findings instead of erroring.
                Capped at 1,000,000 characters.
            max_depth (int): Nesting threshold for the deeply_nested
                rule. Default 12, range 1..128. Lint mode only.
            rules (dict): Map a rule code (XML001..XML013) to False to
                disable that single rule for the call. Lint mode only.

        Returns:
            dict: ``lint`` → ``{mode, ok, parsed, finding_count,
            findings_truncated, findings}`` with each finding
            ``{code, severity, line, col, message, hint}``; ``profile``
            → ``{mode, root_tag, element_count, max_depth,
            deepest_path, deepest_element, top_tags, attribute_count,
            text_node_count, text_length_total, text_length_max,
            namespaces, namespace_count, pi_count, comment_count}``;
            ``fix_hints`` → ``{mode, applied, parse_failed,
            parse_error, bom_suggestion, pretty_print}`` where
            ``applied`` is always False — suggestions are never
            executed.

        Raises:
            ValueError: If the mode is unknown, ``xml_text`` is not a
                string or exceeds the 1,000,000-character cap, an
                option is not valid for the mode, or any option value
                is malformed. Profile mode additionally raises
                ValueError on a document the tool cannot parse (DTD
                guard, expat failure, unpaired surrogates) because it
                has nothing to report.
        """
        if mode not in self.MODES:
            raise _err(f"mode must be one of {self.MODES}, got {mode!r}")

        provided = {"max_depth": max_depth, "rules": rules}
        for option, value in provided.items():
            if value is not None and option not in _MODE_OPTIONS[mode]:
                raise _err(
                    f"{option!r} is not a {mode} mode option "
                    f"(allowed: {sorted(_MODE_OPTIONS[mode])})"
                )

        if not isinstance(xml_text, str):
            raise _err(
                "xml_text must be a string, got "
                f"{type(xml_text).__name__}"
            )
        if len(xml_text) > self.max_input_chars:
            raise _err(
                f"xml_text exceeds the {self.max_input_chars:,}-character "
                f"limit (got {len(xml_text):,} characters)"
            )

        if mode == "profile":
            return _run_profile(xml_text)

        if mode == "lint":
            if max_depth is None:
                max_depth = self.DEFAULT_MAX_DEPTH
            if isinstance(max_depth, bool) or not isinstance(max_depth, int):
                raise _err(f"max_depth must be an integer, got {max_depth!r}")
            if not 1 <= max_depth <= self.MAX_DEPTH_LIMIT:
                raise _err(
                    f"max_depth must be between 1 and "
                    f"{self.MAX_DEPTH_LIMIT}, got {max_depth}"
                )
            disabled = self._resolve_rules(rules)
            return _run_lint(self, xml_text, max_depth, disabled)

        # mode == "fix_hints"
        return _run_fix_hints(xml_text)

    # -- validation helpers ------------------------------------------------

    @classmethod
    def _resolve_rules(cls, rules: Any) -> frozenset:
        """Validate the per-rule disable map; returns disabled codes."""
        if rules is None:
            return frozenset()
        if not isinstance(rules, dict):
            raise _err(f"rules must be a dict, got {type(rules).__name__}")
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
