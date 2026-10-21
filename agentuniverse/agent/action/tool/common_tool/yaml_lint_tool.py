#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: yaml_lint_tool.py

"""Structural quality linter for YAML documents, built on the standard
library plus the framework's existing PyYAML dependency.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network review layer for agents that emit or
receive YAML — the format every agentUniverse component is configured
in. The existing YAML tools all *consume* the format: JsonYamlTool
(#3579) converts between JSON and YAML, the config subsystem parses
files, and nothing anywhere examines a YAML document's structural
quality. A document whose duplicate keys PyYAML silently collapses to
the last value, whose plain ``yes`` folds into a boolean, or whose
``010`` resolves as octal 8 reaches every downstream consumer quietly
damaged. YamlLintTool sits in front of them: lint the structure,
profile the topology, or compute exact safe fixes.

Everything runs offline on the ``yaml_text`` string. Parsing uses
``yaml.SafeLoader`` through the tool's own subclass; no file I/O, no
network, no unsafe constructors. A single leading UTF-8 BOM is
stripped before any parsing (rule YML002 reports it), so line and
column numbers — 1-based, straight from PyYAML's own marks — always
refer to the stream after the BOM, exactly where the parser looked.
``col`` is the 1-based column and is always an integer (1 for
document-level findings).

Two passes power the lint. The *compose pass* walks the full node
tree (every node carries a start mark, a resolved tag and a scalar
style), giving the value-level rules their positions. The *construct
pass* runs the loader over the stream with a duplicate-key-collecting
SafeLoader subclass: plain PyYAML lets a repeated mapping key silently
overwrite the earlier one, so the subclass records every repeat — with
the line marks of both occurrences — before the mapping is built.
Alias targets are shared node objects in the composed tree, so the
walker counts each anchor site once and never expands aliases — the
classic billion-laughs document costs nothing.

Supported modes
---------------
* ``lint`` — run the rule table below over ``yaml_text`` and return
  ``ok`` plus ``findings``. Each finding is ``{code, severity, line,
  col, message, hint}``. ``ok`` is True only when no finding of
  severity error or warning was raised (info-only stays ok). When
  PyYAML rejects the text, YML001 carries the parser's own problem
  mark (context mark as fallback) and the parse-dependent rules are
  skipped; the raw-line rules (BOM, tabs, trailing spaces) still run —
  with block-scalar regions unprotected, since those regions cannot
  be located in an unparseable stream. Findings are sorted by (line,
  col, code), capped at 200 entries (``finding_count`` keeps the true
  total and ``findings_truncated`` flags the cut).
* ``profile`` — topology statistics over the whole stream: collection
  and scalar counts, key count, maximum nesting depth with the path
  of the deepest collection, list count / item count / longest list
  with its path, a scalar type histogram keyed by resolved tag (str /
  int / float / bool / null / timestamp / other), anchor and alias
  usage (definition count, use count, first-seen names, and whether
  any alias closes a cycle), and mapping-key naming-style consistency:
  snake_case, kebab-case and lowerCamel keys counted separately (flat
  lowercase words and anything else are neutral); two or more of the
  three styles coexisting yields a note in ``notes``. Aliases are
  counted once at their definition site.
* ``fix_hints`` — exact, safe, purely textual repairs only: strip the
  UTF-8 BOM, strip trailing spaces, and single-quote plain ``yes`` /
  ``no`` / ``on`` / ``off`` scalars. Every edit reports ``{action,
  line, col, original, replacement}``, the edits are applied to
  produce ``fixed_text``, and ``remaining`` re-lints the fixed text so
  what is left is exactly what the tool refuses to touch (duplicate
  keys, deep nesting, non-string keys — restructuring is never
  attempted). When the text does not parse, BOM and trailing-space
  edits are still offered (``parse_failed`` is set and quoting is
  skipped: quoting positions need a successful parse); block scalar
  regions cannot be protected in that case. Trailing spaces and tabs
  *inside* block scalars (``|`` / ``>``) are literal content: the
  scanner's block-scalar token spans protect them from the
  trailing-space and tab rules, and leading tabs on quoted-scalar
  continuation lines are legal, so those lines are protected from the
  tab rule too.

Rule table (mode ``lint``)
--------------------------
======== =================== ======== =================================================== ==========================================================
Code     Slug                Sev.     Trigger (exact)                                   Hint
======== =================== ======== =================================================== ==========================================================
YML001   syntax_error        error    PyYAML rejects the stream (scanner, parser,        fix the reported position first — structural checks
                                      composer or constructor error, including the       need a parseable document
                                      unhashable-key case); line/col from the problem
                                      mark, context mark as fallback; nesting too deep
                                      for the parser surfaces here as a recursion
                                      failure
YML002   bom                 info     the text starts with a UTF-8 BOM                  strip it (fix_hints) — legal YAML, but it pollutes
                                      (``\\ufeff``); PyYAML accepts it                  naive consumers
YML003   tab_indentation     error    a line's leading whitespace contains a tab        replace indentation tabs with spaces — YAML forbids
                                      and the line is not protected block-scalar or    tabs in indentation
                                      quoted-continuation content; every unpro-
                                      tected occurrence is also a YML001 parse
                                      failure (verified: PyYAML rejects each)
YML004   trailing_spaces     info     a line ends with spaces or tabs outside block      strip them (fix_hints) — inside quoted multi-line
                                      scalar content (where they are literal)           scalars they fold away silently
YML005   duplicate_keys      error    a mapping repeats a key: keys compare by          rename the keys — plain yaml.safe_load silently
                                      resolved value (case-insensitive booleans,        keeps the last value
                                      underscore / base-normalized ints, quoted =
                                      plain strings); one finding per repeat, both
                                      lines in the message; merge keys (``<<``) are
                                      exempt; int 1 vs float 1.0 and NaN-vs-NaN follow
                                      text buckets (documented edges)
YML006   implicit_octal      info     a plain scalar matches ``[-+]?0[0-7_]+`` —         quote it ('010') or write 0o10 / 10 — YAML 1.1
                                      PyYAML resolves it as base-8 (``010`` → 8);       (PyYAML) reads 010 as octal, YAML 1.2 readers
                                      ``0o10`` does NOT resolve (stays a string)        leave 010 as a string
YML007   implicit_bool_word  info     a plain scalar yes/no/on/off (any case)            quote it ('yes') or use true/false — YAML 1.2
                                      resolves to a boolean under PyYAML (YAML 1.1);    core schema does not treat these words as booleans
                                      true/false are unambiguous and never flagged
YML008   empty_value_key     warning  a mapping key's value is an implicit empty         fill in the value or write null explicitly —
                                      (``key:`` with nothing after it, block or         implicit null is usually a truncated edit
                                      flow); explicit ``null`` / ``~`` are deliberate
                                      and never flagged
YML009   deeply_nested      info     a collection nests deeper than ``max_depth``       flatten the structure — deeply nested YAML is hard
                                      (default 12, option range 1..128); fires once     to read and easy to misindent
                                      per document at the first offending collection,
                                      with its depth and path in the message
YML010   non_string_key      info     a mapping key resolves to a non-string             quote it ('1') or rename it — non-string keys
                                      scalar (int, float, bool, null, timestamp) or     survive YAML but surprise JSON round-trips and
                                      is a collection; ``on:`` is a bool key; merge     strict schema validators
                                      keys are exempt
YML011   multiline_plain_    info     a plain (unquoted) scalar spans several lines;     switch to a literal block scalar (|) to keep
         _scalar                      YAML folds the line breaks into spaces            the line breaks — the fold is invisible in the
                                      (``one\\n  two`` parses as ``one two``)            source
YML012   document_without_   warning  a document in the stream has no content — a       drop the stray marker or fill the document in
         _content                     blank or comment-only stream (reported at line
                                      1), or a document that is only ``---`` markers
                                      or implicit null (reported at its marker line;
                                      an explicit ``null`` document is content)
YML013   multiple_documents  info     the stream carries more than one YAML document     split the file or pass allow_multiple_documents=
                                      (``---`` separators); reported at the marker       true when the stream is meant to be multi-doc
                                      starting the second document
======== =================== ======== =================================================== ==========================================================

Options and error matrix
------------------------
``allow_multiple_documents`` (bool, default False) suppresses YML013
while the document count is still reported. ``max_depth`` (int,
default 12, range 1..128) gates YML009. ``rules`` maps any implemented
rule code to False to disable that single rule for the call. Fix mode
replaces the lint options with ``remove_bom`` / ``strip_trailing_spaces``
/ ``quote_bool_words`` (bools, default True). Options are validated per
mode — a lint-only option in profile mode is an error, and vice versa.

``ValueError`` is raised for: an unknown mode; a non-string or
oversized ``yaml_text`` (over ``max_input_chars`` = 1,000,000
characters, the 1 MB cap); malformed options of any kind. Every parser
failure — tabs, syntax errors, unhashable keys, nesting too deep for
the parser's recursion — is a *finding*, not an exception; profile
mode raises ValueError on an unparseable stream because it has
nothing to report. All findings and statistics are exact and the run
is fully deterministic.
"""

import re
from typing import Any, ClassVar

import yaml
from pydantic import ConfigDict
from yaml.nodes import MappingNode, ScalarNode, SequenceNode
from yaml.tokens import AliasToken, AnchorToken, ScalarToken

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# Static vocabulary
# ---------------------------------------------------------------------------

_MERGE_TAG_SUFFIX = "merge"

# Rule codes -> (slug, severity, hint).
_RULES: dict = {
    "YML001": ("syntax_error", "error",
               "fix the reported position — structural checks need a "
               "parseable document"),
    "YML002": ("bom", "info",
               "strip the BOM (fix_hints) before feeding naive consumers"),
    "YML003": ("tab_indentation", "error",
               "replace indentation tabs with spaces — YAML forbids "
               "tabs in indentation"),
    "YML004": ("trailing_spaces", "info",
               "strip them (fix_hints) — quoted multi-line scalars fold "
               "them away silently"),
    "YML005": ("duplicate_keys", "error",
               "rename the keys — plain yaml.safe_load silently keeps "
               "the last value"),
    "YML006": ("implicit_octal", "info",
               "quote it ('010') or write 0o10 / 10 — YAML 1.1 readers "
               "treat 010 as octal"),
    "YML007": ("implicit_bool_word", "info",
               "quote it ('yes') or use true/false — YAML 1.2 does not "
               "treat these words as booleans"),
    "YML008": ("empty_value_key", "warning",
               "fill the value in or write null explicitly"),
    "YML009": ("deeply_nested", "info",
               "flatten the structure — deep nesting is easy to misindent"),
    "YML010": ("non_string_key", "info",
               "quote it ('1') or rename it — non-string keys surprise "
               "JSON round-trips and validators"),
    "YML011": ("multiline_plain_scalar", "info",
               "use a literal block scalar (|) to keep the line breaks"),
    "YML012": ("document_without_content", "warning",
               "drop the stray marker or fill the document in"),
    "YML013": ("multiple_documents", "info",
               "split the stream or pass allow_multiple_documents=true"),
}
_RULE_CODES: tuple = tuple(_RULES)

# Per-mode option gates for the error matrix.
_LINT_OPTIONS = frozenset(
    {"allow_multiple_documents", "max_depth", "rules"}
)
_PROFILE_OPTIONS: frozenset = frozenset()
_FIX_OPTIONS = frozenset(
    {"remove_bom", "strip_trailing_spaces", "quote_bool_words"}
)
_MODE_OPTIONS = {"lint": _LINT_OPTIONS, "profile": _PROFILE_OPTIONS,
                 "fix_hints": _FIX_OPTIONS}

# YAML 1.1 plain-scalar octal look (the PyYAML resolver reads these
# base-8: 010 -> 8).
_OCTAL_LOOK = re.compile(r"\A[-+]?0[0-7_]+\Z")
# Plain boolean words whose YAML 1.2 status differs from PyYAML's 1.1
# reading; true/false are unambiguous and never flagged.
_BOOL_WORD_VALUES = frozenset({"yes", "no", "on", "off"})

# Key naming styles (profile): snake, kebab and lowerCamel are the
# competing styles; flat words and anything else stay neutral.
_SNAKE_RE = re.compile(r"\A(?:[a-z0-9]+_[a-z0-9_]+|[A-Z0-9]+_[A-Z0-9_]+)\Z")
_KEBAB_RE = re.compile(r"\A[a-z0-9]+(?:-[a-z0-9]+)+\Z")
_CAMEL_RE = re.compile(r"\A[a-z][a-z0-9]*(?:[A-Z][a-z0-9]*)+\Z")
_FLAT_RE = re.compile(r"\A[a-z][a-z0-9]*\Z")
_NAMING_STYLES: tuple = ("snake", "kebab", "camel")
_NAMING_BUCKETS: tuple = _NAMING_STYLES + ("flat", "other")

# Document start markers at the beginning of a line ('---').
_MARKER_RE = re.compile(r"\A---(?=[\s])|\A---\Z")

# Simple identifiers render bare inside profile paths.
_SIMPLE_KEY_RE = re.compile(r"\A[A-Za-z0-9_\-]{1,40}\Z")

# Scalar tag suffix -> histogram bucket.
_SCALAR_TAG_TYPES: dict = {
    "str": "str", "int": "int", "float": "float", "bool": "bool",
    "null": "null", "timestamp": "timestamp",
}

# The raw text of a bool word at an exact position.
_WORD_AT_RE = re.compile(r"\A[A-Za-z]+")


def _err(message: str) -> ValueError:
    """Return the ValueError every validation branch raises."""
    return ValueError(message)


def _tag_suffix(node: Any) -> str:
    """The short tag name — 'str', 'int', 'merge'... — of a node."""
    return node.tag.rsplit(":", 1)[-1]


def _mark_pos(mark: Any) -> tuple:
    """1-based (line, col) of a PyYAML mark."""
    if mark is None:
        return 1, 1
    return mark.line + 1, mark.column + 1


def _finding(code: str, line: int, col: int, message: str) -> dict:
    """Assemble one finding dict from the rule table."""
    _slug, severity, hint = _RULES[code]
    return {
        "code": code, "severity": severity,
        "line": line, "col": col, "message": message, "hint": hint,
    }


def _display_path(path: str, cap: int = 100) -> str:
    """Cap a profile path for messages."""
    return path if len(path) <= cap else path[: cap - 3] + "..."


# ---------------------------------------------------------------------------
# Canonical keys and the duplicate-key-safe loader (construct pass)
# ---------------------------------------------------------------------------

def _yaml_int_value(text: str) -> int:
    """Replicate PyYAML's YAML 1.1 int construction for canonical keys."""
    value = text.replace("_", "")
    sign = 1
    if value[0] in "+-":
        if value[0] == "-":
            sign = -1
        value = value[1:]
    if value[:2] == "0b":
        return sign * int(value[2:], 2)
    if value[:2] == "0x":
        return sign * int(value[2:], 16)
    if ":" in value:
        total = 0
        for digit in (int(part) for part in value.split(":")):
            total = total * 60 + digit
        return sign * total
    if value[0] == "0":
        return sign * int(value, 8)
    return sign * int(value, 10)


def _yaml_float_value(text: str) -> float:
    """Replicate PyYAML's float construction for canonical keys."""
    value = text.replace("_", "").lower()
    sign = 1.0
    if value[0] in "+-":
        if value[0] == "-":
            sign = -1.0
        value = value[1:]
    if value == ".inf":
        return sign * float("inf")
    if value == ".nan":
        return float("nan")
    if ":" in value:
        total = 0.0
        for digit in (float(part) for part in value.split(":")):
            total = total * 60.0 + digit
        return sign * total
    return sign * float(value)


def _canonical_key(node: Any) -> tuple:
    """Hashable canonical form of a mapping key node.

    Mirrors how the python dict PyYAML builds would compare keys:
    plain and quoted strings are equal, booleans compare
    case-insensitively, ints compare across 0x / 0b / 0-prefix /
    underscore spellings, floats across .inf spellings. Merge keys are
    excluded by the caller. Collection keys collapse to structure.
    Documented edges: int 1 vs float 1.0 and NaN-vs-NaN compare by
    text bucket (the built dict would equate the former).
    """
    if isinstance(node, ScalarNode):
        suffix = _tag_suffix(node)
        if suffix == "str":
            return ("s", node.value)
        if suffix == "bool":
            return ("b", node.value.lower())
        if suffix == "null":
            return ("n",)
        if suffix == "int":
            try:
                return ("i", _yaml_int_value(node.value))
            except (ValueError, IndexError):
                return ("r", node.tag, node.value)
        if suffix == "float":
            try:
                return ("f", _yaml_float_value(node.value))
            except (ValueError, IndexError):
                return ("r", node.tag, node.value)
        return ("r", node.tag, node.value)
    if isinstance(node, SequenceNode):
        return ("q", tuple(_canonical_key(item) for item in node.value))
    if isinstance(node, MappingNode):
        return ("m", frozenset(
            (_canonical_key(key), _canonical_key(value))
            for key, value in node.value
        ))
    return ("r", "unknown", repr(node))


def _key_display(node: Any) -> str:
    """Short human-readable form of a key node for messages."""
    if isinstance(node, ScalarNode):
        text = node.value
        return text if len(text) <= 24 else text[:21] + "..."
    if isinstance(node, SequenceNode):
        return "[sequence key]"
    if isinstance(node, MappingNode):
        return "{mapping key}"
    return "key"


class _LintLoader(yaml.SafeLoader):
    """SafeLoader subclass that surfaces duplicate mapping keys.

    Plain PyYAML lets a repeated mapping key silently overwrite the
    earlier one while building the python dict. This subclass inspects
    every mapping's raw key list — before merge flattening — and
    records each repeat with the line marks of both occurrences into
    ``self.duplicates`` before the standard construction proceeds.
    """

    def __init__(self, stream: Any) -> None:
        super().__init__(stream)
        # (line, col, display, first_line) per duplicate occurrence.
        self.duplicates: list = []

    def construct_mapping(self, node: Any, deep: bool = False) -> dict:
        """Record duplicate keys, then build the mapping normally."""
        self._collect_duplicate_keys(node)
        return super().construct_mapping(node, deep)

    def _collect_duplicate_keys(self, node: Any) -> None:
        first_seen: dict = {}
        for key_node, _value_node in node.value:
            if _tag_suffix(key_node) == _MERGE_TAG_SUFFIX:
                continue
            canonical = _canonical_key(key_node)
            try:
                hash(canonical)
            except TypeError:
                canonical = ("r", repr(canonical))
            line, col = _mark_pos(key_node.start_mark)
            if canonical in first_seen:
                self.duplicates.append(
                    (line, col, _key_display(key_node), first_seen[canonical])
                )
            else:
                first_seen[canonical] = line


# ---------------------------------------------------------------------------
# Raw-line scan (tabs, trailing spaces, document markers)
# ---------------------------------------------------------------------------

def _scan_raw_lines(text: str) -> dict:
    """Tab / trailing-space / marker positions from the raw lines.

    Returns ``{"tabs": [(line, col)], "trailing": [(line, col)],
    "markers": [line]}`` with 1-based positions. Whitespace-only lines
    count as trailing whitespace, never as tab indentation; callers
    protect block-scalar and quoted-continuation ranges afterwards.
    """
    tabs: list = []
    trailing: list = []
    markers: list = []
    for index, line in enumerate(text.split("\n"), 1):
        without_cr = line.rstrip("\r")
        if _MARKER_RE.match(without_cr):
            markers.append(index)
        body = without_cr.rstrip(" \t")
        if body != without_cr:
            trailing.append((index, len(body) + 1))
        if not body:
            continue
        indent = line[: len(line) - len(line.lstrip(" \t"))]
        if "\t" in indent:
            tabs.append((index, indent.index("\t") + 1))
    return {"tabs": tabs, "trailing": trailing, "markers": markers}


# ---------------------------------------------------------------------------
# Token scan (anchors, aliases, protected scalar regions)
# ---------------------------------------------------------------------------

def _scan_tokens(text: str) -> dict:
    """Anchor / alias usage and block / quoted scalar line ranges.

    Returns ``{"anchors": [(name, line)], "aliases": [(name, line)],
    "block_ranges": [(lo, hi)], "quoted_ranges": [(lo, hi)]}`` with
    1-based inclusive line ranges. Block scalar ranges cover the
    literal content lines only; quoted ranges cover the continuation
    lines (line 2 onward of a multi-line quoted scalar), where leading
    tabs and folded trailing spaces are token content rather than
    indentation noise.
    """
    result: dict = {"anchors": [], "aliases": [], "block_ranges": [],
                    "quoted_ranges": []}
    for token in yaml.scan(text, Loader=yaml.SafeLoader):
        if isinstance(token, AnchorToken):
            result["anchors"].append(
                (token.value, token.start_mark.line + 1)
            )
        elif isinstance(token, AliasToken):
            result["aliases"].append(
                (token.value, token.start_mark.line + 1)
            )
        elif isinstance(token, ScalarToken):
            if token.start_mark.line == token.end_mark.line:
                continue
            lo = token.start_mark.line + 2
            if token.style in ("|", ">"):
                hi = token.end_mark.line
                if hi >= lo:
                    result["block_ranges"].append((lo, hi))
            elif token.style in ("'", '"'):
                hi = token.end_mark.line + 1
                if hi >= lo:
                    result["quoted_ranges"].append((lo, hi))
    return result


def _protected(lines: list, ranges: list) -> frozenset:
    """The 1-based line numbers inside any (lo, hi) range."""
    covered: set = set()
    for lo, hi in ranges:
        covered.update(range(lo, hi + 1))
    return frozenset(line for line in lines if line in covered)


def _assign_markers(markers: list, doc_lines: list) -> list:
    """Assign each document the '---' marker that starts it.

    ``markers`` are the 1-based '---' line numbers in order and
    ``doc_lines`` the first-content line of each composed document.
    Markers are consumed in order: the first document takes the first
    marker at or above its content line only when that marker precedes
    the content (an implicit first document takes none); each later
    document takes the next marker at or above its content line.
    Returns one marker line (or None) per document.
    """
    assigned: list = []
    pointer = 0
    for doc_line in doc_lines:
        chosen = None
        if pointer < len(markers) and markers[pointer] <= doc_line:
            chosen = markers[pointer]
            pointer += 1
        assigned.append(chosen)
    return assigned


# ---------------------------------------------------------------------------
# Tree walker (compose pass: value-level rules + profile statistics)
# ---------------------------------------------------------------------------

def _path_segment(key_node: Any) -> str:
    """Render a mapping key as a profile path segment."""
    if (isinstance(key_node, ScalarNode)
            and _tag_suffix(key_node) == "str"
            and _SIMPLE_KEY_RE.match(key_node.value)):
        return key_node.value
    return repr(_key_display(key_node))


def _classify_key_style(value: str) -> str:
    """Naming style class of one string mapping key."""
    if _SNAKE_RE.match(value):
        return "snake"
    if _KEBAB_RE.match(value):
        return "kebab"
    if _CAMEL_RE.match(value):
        return "camel"
    if _FLAT_RE.match(value):
        return "flat"
    return "other"


class _Stats:
    """Mutable profile accumulator shared by the walker."""

    def __init__(self) -> None:
        self.mapping_count = 0
        self.key_count = 0
        self.scalar_count = 0
        self.list_count = 0
        self.list_item_count = 0
        self.longest_list: dict = {}
        self.scalar_types: dict = {
            "str": 0, "int": 0, "float": 0, "bool": 0,
            "null": 0, "timestamp": 0, "other": 0,
        }
        self.max_depth = 0
        self.deepest_path = ""
        self.naming: dict = dict.fromkeys(_NAMING_BUCKETS, 0)
        self.recursive_anchor = False


def _walk_tree(root: Any, findings: list, stats: _Stats, max_depth: int,
               deep_reported: list) -> list:
    """Iterative DFS over one composed document.

    Collects YML006..YML011 findings and every profile statistic, and
    returns the bool-word sites as ``[(line, col, word)]`` for the
    fix pass. Alias targets are shared node objects, so a node seen
    before is a reuse: it is skipped (counted once at its definition
    site), and a reuse still on the ancestor stack marks a recursive
    anchor. Scalars that serve as mapping keys take part in the
    scalar-level rules too, but nesting depth counts collections only.
    """
    bool_words: list = []
    visited: set = set()
    ancestors: set = set()
    # Stack items: ("node", node, depth, path) | ("exit", node_id).
    stack: list = [("node", root, 0, "")]
    while stack:
        kind, payload, depth, path = stack.pop()
        if kind == "exit":
            ancestors.discard(payload)
            continue
        node = payload
        if id(node) in visited:
            if id(node) in ancestors:
                stats.recursive_anchor = True
            continue
        visited.add(id(node))
        if isinstance(node, ScalarNode):
            stats.scalar_count += 1
            suffix = _tag_suffix(node)
            stats.scalar_types[
                _SCALAR_TAG_TYPES.get(suffix, "other")
            ] += 1
            if node.style is not None:
                continue
            line, col = _mark_pos(node.start_mark)
            if suffix == "int" and _OCTAL_LOOK.match(node.value):
                try:
                    parsed = _yaml_int_value(node.value)
                except (ValueError, IndexError):
                    parsed = "?"
                findings.append(_finding(
                    "YML006", line, col,
                    f"plain scalar {node.value} resolves as base-8 to "
                    f"{parsed} under YAML 1.1 (PyYAML)"
                ))
            elif (suffix == "bool"
                    and node.value.lower() in _BOOL_WORD_VALUES):
                findings.append(_finding(
                    "YML007", line, col,
                    f"plain scalar {node.value} resolves to a boolean "
                    "under YAML 1.1 (PyYAML)"
                ))
                bool_words.append((line, col, node.value))
            elif node.end_mark.line > node.start_mark.line:
                span = node.end_mark.line - node.start_mark.line + 1
                findings.append(_finding(
                    "YML011", line, col,
                    f"plain scalar spans {span} lines and folds the "
                    "line breaks into spaces"
                ))
            continue
        collection_depth = depth + 1
        if collection_depth > stats.max_depth:
            stats.max_depth = collection_depth
            stats.deepest_path = path or "[root]"
        if isinstance(node, SequenceNode):
            stats.list_count += 1
            stats.list_item_count += len(node.value)
            if len(node.value) > stats.longest_list.get("length", -1):
                stats.longest_list = {
                    "length": len(node.value), "path": path or "[root]",
                }
        else:
            stats.mapping_count += 1
            for key_node, value_node in node.value:
                suffix = _tag_suffix(key_node)
                if suffix == _MERGE_TAG_SUFFIX:
                    continue
                stats.key_count += 1
                if isinstance(key_node, ScalarNode) and suffix == "str":
                    stats.naming[_classify_key_style(key_node.value)] += 1
                key_line, key_col = _mark_pos(key_node.start_mark)
                if not (isinstance(key_node, ScalarNode)
                        and suffix == "str"):
                    findings.append(_finding(
                        "YML010", key_line, key_col,
                        f"mapping key {_key_display(key_node)!r} "
                        f"resolves to a non-string ({suffix})"
                    ))
                if (isinstance(value_node, ScalarNode)
                        and _tag_suffix(value_node) == "null"
                        and value_node.value == ""):
                    findings.append(_finding(
                        "YML008", key_line, key_col,
                        f"key {_key_display(key_node)!r} has an implicit "
                        "empty value (parses as null)"
                    ))
        if collection_depth > max_depth and not deep_reported:
            deep_reported.append(True)
            line, col = _mark_pos(node.start_mark)
            findings.append(_finding(
                "YML009", line, col,
                f"collection nesting reaches depth {collection_depth} at "
                f"{_display_path(path) or '[root]'} (limit {max_depth})"
            ))
        ancestors.add(id(node))
        stack.append(("exit", id(node), 0, ""))
        children: list = []
        if isinstance(node, MappingNode):
            for key_node, value_node in node.value:
                if _tag_suffix(key_node) == _MERGE_TAG_SUFFIX:
                    continue
                if isinstance(key_node, ScalarNode):
                    # Key scalars join the scalar-level rules at the
                    # same depth; values descend one level.
                    children.append(("node", key_node, depth, path))
                segment = _path_segment(key_node)
                child_path = segment if not path else f"{path}.{segment}"
                children.append(
                    ("node", value_node, collection_depth, child_path)
                )
        else:
            for index, item in enumerate(node.value):
                children.append((
                    "node", item, collection_depth,
                    f"{path}[{index}]" if path else f"[{index}]",
                ))
        stack.extend(reversed(children))
    return bool_words


# ---------------------------------------------------------------------------
# Error mark extraction
# ---------------------------------------------------------------------------

def _syntax_finding(error: BaseException) -> dict:
    """Map a PyYAML error (or recursion failure) to a YML001 finding."""
    mark = getattr(error, "problem_mark", None) or \
        getattr(error, "context_mark", None)
    line, col = _mark_pos(mark)
    if isinstance(error, RecursionError):
        message = ("nesting is too deep for the YAML parser "
                   "(recursion limit reached)")
    else:
        context = getattr(error, "context", None)
        problem = getattr(error, "problem", None)
        detail = f"{type(error).__name__}: "
        if problem:
            message = detail + (
                f"{context}: {problem}" if context else str(problem)
            )
        else:
            message = detail + str(error).strip()
    return _finding("YML001", line, col, message)


# ---------------------------------------------------------------------------
# Stream parsing helpers
# ---------------------------------------------------------------------------

def _parse_stream(text: str) -> tuple:
    """Compose every document; map failures to a YML001 finding.

    Returns ``(documents, parse_finding)`` where ``documents`` is
    ``None`` when the compose pass failed outright.
    """
    try:
        documents = list(yaml.compose_all(text, Loader=_LintLoader))
        return documents, None
    except (yaml.YAMLError, RecursionError) as error:
        return None, _syntax_finding(error)


def _collect_duplicates(text: str) -> tuple:
    """Construct pass for duplicate keys via the loader subclass."""
    loader = _LintLoader(text)
    try:
        while loader.check_data():
            loader.get_data()
        return loader.duplicates, None
    except (yaml.YAMLError, RecursionError) as error:
        return loader.duplicates, _syntax_finding(error)
    finally:
        try:
            loader.dispose()
        except AttributeError:
            pass


# ---------------------------------------------------------------------------
# Fix hints
# ---------------------------------------------------------------------------

def _quote_word(raw: str) -> str:
    """Single-quoted YAML rendering of a bool word."""
    return "'" + raw.replace("'", "''") + "'"


def _apply_edits(text: str, edits: list) -> str:
    """Apply line/col level textual edits to ``text``.

    Edits are ``{line, col, original, replacement}`` with 1-based
    positions into each line's content (excluding the terminator).
    Edits on one line never overlap; they are applied from the last
    position backwards so earlier positions stay valid.
    """
    if not edits:
        return text
    lines = text.split("\n")
    by_line: dict = {}
    for edit in edits:
        by_line.setdefault(edit["line"], []).append(edit)
    for line_no, line_edits in by_line.items():
        content = lines[line_no - 1]
        terminator = ""
        if content.endswith("\r"):
            content, terminator = content[:-1], "\r"
        for edit in sorted(line_edits,
                           key=lambda item: item["col"], reverse=True):
            start = edit["col"] - 1
            end = start + len(edit["original"])
            if content[start:end] == edit["original"]:
                content = content[:start] + edit["replacement"] \
                    + content[end:]
        lines[line_no - 1] = content + terminator
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mode runners
# ---------------------------------------------------------------------------

def _run_lint(tool: Any, text: str, allow_multiple: bool,
              max_depth: int, disabled: frozenset) -> dict:
    """Collect every enabled finding over the stream.

    A single leading UTF-8 BOM is stripped before any parsing (rule
    YML002 reports it); every reported line and column refers to the
    stream after the BOM, matching the marks PyYAML itself reports.
    """
    had_bom = text.startswith("\ufeff")
    work = text[1:] if had_bom else text
    findings: list = []
    parsed = True
    report_syntax = "YML001" not in disabled

    # Token pass: anchors, aliases, protected regions.
    try:
        tokens = _scan_tokens(work)
    except (yaml.YAMLError, RecursionError) as error:
        tokens = None
        if report_syntax:
            findings.append(_syntax_finding(error))
        parsed = False

    # Compose pass: the node tree.
    documents = None
    if parsed:
        documents, parse_finding = _parse_stream(work)
        if parse_finding is not None and report_syntax:
            findings.append(parse_finding)
        if documents is None:
            parsed = False

    # Construct pass: duplicate keys via the loader subclass.
    duplicates: list = []
    if parsed:
        duplicates, duplicate_error = _collect_duplicates(work)
        if duplicate_error is not None and report_syntax:
            findings.append(duplicate_error)

    document_count = len(documents) if documents is not None else None

    # Raw-line rules, protected by the scalar regions.
    raw = _scan_raw_lines(work)
    tab_protected: frozenset = frozenset()
    trailing_protected: frozenset = frozenset()
    if tokens is not None:
        tab_protected = _protected(
            [line for line, _col in raw["tabs"]],
            tokens["block_ranges"] + tokens["quoted_ranges"],
        )
        trailing_protected = _protected(
            [line for line, _col in raw["trailing"]],
            tokens["block_ranges"],
        )
    if had_bom and "YML002" not in disabled:
        findings.append(_finding(
            "YML002", 1, 1,
            "the text starts with a UTF-8 BOM (\\ufeff)"
        ))
    if "YML003" not in disabled:
        for line, col in raw["tabs"]:
            if line in tab_protected:
                continue
            findings.append(_finding(
                "YML003", line, col,
                "leading whitespace contains a tab — YAML forbids tabs "
                "in indentation"
            ))
    if "YML004" not in disabled:
        for line, col in raw["trailing"]:
            if line in trailing_protected:
                continue
            findings.append(_finding(
                "YML004", line, col,
                "line ends with trailing whitespace"
            ))
    if "YML005" not in disabled:
        for line, col, display, first_line in duplicates:
            findings.append(_finding(
                "YML005", line, col,
                f"duplicate mapping key {display!r} (first defined at "
                f"line {first_line}); PyYAML keeps the last value"
            ))

    # Value-level rules over the composed tree.
    bool_words: list = []
    if documents:
        stats = _Stats()
        deep_reported: list = []
        for document in documents:
            bool_words.extend(
                _walk_tree(document, findings, stats, max_depth,
                           deep_reported)
            )
        doc_lines = [
            document.start_mark.line + 1 for document in documents
        ]
        doc_markers = _assign_markers(raw["markers"], doc_lines)
        if "YML012" not in disabled:
            for document, marker in zip(documents, doc_markers):
                if not (isinstance(document, ScalarNode)
                        and _tag_suffix(document) == "null"
                        and document.value == ""):
                    continue
                node_line = document.start_mark.line + 1
                findings.append(_finding(
                    "YML012", marker if marker is not None else node_line,
                    1, "document has no content (implicit null)"
                ))
        if ("YML013" not in disabled and not allow_multiple
                and document_count > 1):
            second_marker = doc_markers[1]
            findings.append(_finding(
                "YML013",
                second_marker if second_marker is not None
                else doc_lines[1],
                1,
                f"{document_count} documents in one stream — the second "
                "starts here"
            ))
    elif parsed and not documents:
        # Blank or comment-only stream: no document at all.
        if "YML012" not in disabled:
            findings.append(_finding(
                "YML012", 1, 1,
                "the stream contains no YAML document"
            ))

    findings.sort(key=lambda item: (
        item["line"], item["col"], item["code"]
    ))
    truncated = len(findings) > tool.MAX_FINDINGS
    return {
        "mode": "lint",
        "ok": not any(
            finding["severity"] in ("error", "warning")
            for finding in findings
        ),
        "parsed": parsed,
        "document_count": document_count,
        "finding_count": len(findings),
        "findings_truncated": truncated,
        "findings": findings[: tool.MAX_FINDINGS],
        "_bool_words": bool_words,
    }


def _run_profile(text: str) -> dict:
    """Topology statistics over the whole stream."""
    work = text[1:] if text.startswith("\ufeff") else text
    tokens = _scan_tokens(work)
    documents, parse_finding = _parse_stream(work)
    if documents is None:
        raise _err(
            "profile mode requires a parseable YAML stream "
            f"({parse_finding['message']})"
        )
    stats = _Stats()
    findings: list = []
    for document in documents:
        _walk_tree(document, findings, stats, 0, [])
    anchor_names: list = []
    for name, _line in tokens["anchors"]:
        if name not in anchor_names:
            anchor_names.append(name)
    styles = stats.naming
    present = [style for style in _NAMING_STYLES if styles[style] > 0]
    mixed = len(present) > 1
    dominant = None
    if present:
        dominant = min(
            present, key=lambda style: (-styles[style],
                                        _NAMING_STYLES.index(style))
        )
    notes: list = []
    if mixed:
        detail = ", ".join(f"{style}={styles[style]}" for style in present)
        notes.append(
            f"key naming styles are mixed ({detail}) — pick one "
            "convention"
        )
    return {
        "mode": "profile",
        "document_count": len(documents),
        "mapping_count": stats.mapping_count,
        "key_count": stats.key_count,
        "scalar_count": stats.scalar_count,
        "max_depth": stats.max_depth,
        "deepest_path": stats.deepest_path or None,
        "list_count": stats.list_count,
        "list_item_count": stats.list_item_count,
        "longest_list": stats.longest_list or None,
        "scalar_types": stats.scalar_types,
        "anchors": {
            "definitions": len(tokens["anchors"]),
            "uses": len(tokens["aliases"]),
            "names": anchor_names[:20],
            "recursive": stats.recursive_anchor,
        },
        "naming": {
            "styles": styles,
            "dominant": dominant,
            "mixed": mixed,
        },
        "notes": notes,
    }


def _run_fix_hints(tool: Any, text: str, remove_bom: bool,
                   strip_trailing: bool, quote_words: bool) -> dict:
    """Compute exact safe textual edits and the fixed text.

    All line/column positions refer to the stream after a leading
    BOM, matching the lint output; ``fixed_text`` re-attaches the BOM
    when ``remove_bom`` is disabled.
    """
    had_bom = text.startswith("\ufeff")
    work = text[1:] if had_bom else text
    lint = _run_lint(tool, work, False, 12, frozenset())
    parsed = lint["parsed"]
    raw = _scan_raw_lines(work)
    lines = work.split("\n")

    edits: list = []
    if remove_bom and had_bom:
        edits.append({
            "action": "remove_bom", "line": 1, "col": 1,
            "original": "\ufeff", "replacement": "",
        })
    if strip_trailing and raw["trailing"]:
        try:
            tokens = _scan_tokens(work)
            trailing_protected = _protected(
                [line for line, _col in raw["trailing"]],
                tokens["block_ranges"],
            )
        except (yaml.YAMLError, RecursionError):
            trailing_protected = frozenset()
        for line, col in raw["trailing"]:
            if line in trailing_protected:
                continue
            content = lines[line - 1].rstrip("\r")
            body = content.rstrip(" \t")
            edits.append({
                "action": "strip_trailing_spaces", "line": line,
                "col": col, "original": content[len(body):],
                "replacement": "",
            })
    if quote_words and parsed:
        for line, col, word in lint["_bool_words"]:
            match = _WORD_AT_RE.match(lines[line - 1][col - 1:])
            if not match or match.group(0) != word:
                # The finding and the raw line disagree (should not
                # happen); refuse the edit rather than corrupt text.
                continue
            edits.append({
                "action": "quote_bool_word", "line": line, "col": col,
                "original": word, "replacement": _quote_word(word),
            })
    lint.pop("_bool_words", None)
    edits.sort(key=lambda edit: (edit["line"], edit["col"]))
    fixed_work = _apply_edits(work, edits)
    if had_bom and not remove_bom:
        fixed_text = "\ufeff" + fixed_work
    else:
        fixed_text = fixed_work
    applied: list = []
    for action in ("remove_bom", "strip_trailing_spaces",
                   "quote_bool_word"):
        count = sum(1 for edit in edits if edit["action"] == action)
        if count:
            applied.append({"action": action, "count": count})
    remaining = _run_lint(tool, fixed_text, False, 12, frozenset())
    return {
        "mode": "fix_hints",
        "parse_failed": not parsed,
        "edits": edits,
        "applied": applied,
        "fixed_text": fixed_text,
        "remaining_count": remaining["finding_count"],
        "remaining_truncated": remaining["findings_truncated"],
        "remaining": remaining["findings"],
    }


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

class YamlLintTool(Tool):
    """Structural quality linter for YAML documents.

    The tool never touches the filesystem or the network — it
    examines YAML *text* with the framework's existing PyYAML
    dependency driven through a duplicate-key-collecting SafeLoader
    subclass: lint the structure against the documented rule table,
    profile the document topology, or compute exact safe textual
    fixes. See the module docstring for the full rule table, the mode
    reference and the documented edge notes.

    Class attributes:
        MODES (tuple): Supported modes (lint, profile, fix_hints).
        RULE_CODES (tuple): All implemented rule codes.
        MAX_DEPTH_LIMIT (int): Upper bound for the max_depth option.
        MAX_FINDINGS (int): Findings list cap per lint run.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "yaml_lint_tool"
    description: str = (
        "YAML document structural quality linter — pure stdlib plus the "
        "framework's existing PyYAML, no files, no network. lint mode "
        "checks a stream against a documented 13-rule table (parser "
        "errors mapped to PyYAML's own problem marks; BOM; tab "
        "indentation with block-scalar protection; trailing spaces; "
        "duplicate mapping keys that plain PyYAML silently collapses "
        "to the last value, detected via a duplicate-key-safe "
        "SafeLoader subclass; plain scalars that resolve as octal "
        "(010 -> 8) or as booleans (yes/no/on/off); implicit empty "
        "values; nesting deeper than a configurable depth; non-string "
        "keys; plain multi-line scalars whose breaks fold away; "
        "contentless documents; multi-document streams with an allow "
        "option), each finding carrying severity, 1-based "
        "line/column, message and hint; profile mode reports topology "
        "statistics (mapping/key/scalar/list counts, max depth with "
        "path, longest list, scalar type histogram, anchor and alias "
        "usage with recursive detection, key naming-style "
        "consistency); fix_hints mode computes exact safe textual "
        "edits only (BOM strip, trailing-space strip, quoting "
        "yes/no/on/off) with line/column positions, applies them into "
        "fixed_text and re-lints what remains — it never "
        "restructures."
    )

    MODES: ClassVar[tuple] = ("lint", "profile", "fix_hints")
    RULE_CODES: ClassVar[tuple] = _RULE_CODES
    MAX_DEPTH_LIMIT: ClassVar[int] = 128
    MAX_FINDINGS: ClassVar[int] = 200

    max_input_chars: int = 1_000_000

    def execute(
        self,
        mode: Any = None,
        yaml_text: Any = None,
        allow_multiple_documents: Any = None,
        max_depth: Any = None,
        rules: Any = None,
        remove_bom: Any = None,
        strip_trailing_spaces: Any = None,
        quote_bool_words: Any = None,
    ) -> dict:
        """Lint, profile or compute safe fixes for YAML text.

        Args:
            mode (str): One of ``lint``, ``profile`` or ``fix_hints``.
            yaml_text (str): The YAML stream to examine. Blank and
                comment-only streams lint to document_without_content
                instead of erroring. Capped at 1,000,000 characters.
            allow_multiple_documents (bool): Suppress the
                multiple_documents finding while still reporting the
                count. Default False. Lint mode only.
            max_depth (int): Nesting threshold for deeply_nested.
                Default 12, range 1..128. Lint mode only.
            rules (dict): Map a rule code (YML001..YML013) to False to
                disable that single rule for the call. Lint mode only.
            remove_bom (bool): Offer the BOM strip edit. Default True.
                Fix mode only.
            strip_trailing_spaces (bool): Offer trailing-space strip
                edits. Default True. Fix mode only.
            quote_bool_words (bool): Offer single-quoting edits for
                plain yes/no/on/off scalars. Default True. Fix mode
                only.

        Returns:
            dict: ``lint`` → ``{mode, ok, parsed, document_count,
            finding_count, findings_truncated, findings}`` with each
            finding ``{code, severity, line, col, message, hint}``;
            ``profile`` → ``{mode, document_count, mapping_count,
            key_count, scalar_count, max_depth, deepest_path,
            list_count, list_item_count, longest_list, scalar_types,
            anchors, naming, notes}``; ``fix_hints`` → ``{mode,
            parse_failed, edits, applied, fixed_text, remaining_count,
            remaining_truncated, remaining}``.

        Raises:
            ValueError: If the mode is unknown, ``yaml_text`` is not a
                string or exceeds the 1,000,000-character cap, an
                option is not valid for the mode, or any option value
                is malformed. Parser failures are findings, not
                exceptions; profile mode raises ValueError on an
                unparseable stream because it has nothing to report.
        """
        if mode not in self.MODES:
            raise _err(f"mode must be one of {self.MODES}, got {mode!r}")

        provided = {
            "allow_multiple_documents": allow_multiple_documents,
            "max_depth": max_depth,
            "rules": rules,
            "remove_bom": remove_bom,
            "strip_trailing_spaces": strip_trailing_spaces,
            "quote_bool_words": quote_bool_words,
        }
        for option, value in provided.items():
            if value is not None and option not in _MODE_OPTIONS[mode]:
                raise _err(
                    f"{option!r} is not a {mode} mode option "
                    f"(allowed: {sorted(_MODE_OPTIONS[mode])})"
                )

        if not isinstance(yaml_text, str):
            raise _err(
                "yaml_text must be a string, got "
                f"{type(yaml_text).__name__}"
            )
        if len(yaml_text) > self.max_input_chars:
            raise _err(
                f"yaml_text exceeds the {self.max_input_chars:,}-character "
                f"limit (got {len(yaml_text):,} characters)"
            )

        if mode == "profile":
            return _run_profile(yaml_text)

        if mode == "lint":
            if allow_multiple_documents is None:
                allow_multiple_documents = False
            if not isinstance(allow_multiple_documents, bool):
                raise _err(
                    "allow_multiple_documents must be a boolean, got "
                    f"{allow_multiple_documents!r}"
                )
            if max_depth is None:
                max_depth = 12
            if isinstance(max_depth, bool) or not isinstance(max_depth, int):
                raise _err(
                    f"max_depth must be an integer, got {max_depth!r}"
                )
            if not 1 <= max_depth <= self.MAX_DEPTH_LIMIT:
                raise _err(
                    f"max_depth must be between 1 and "
                    f"{self.MAX_DEPTH_LIMIT}, got {max_depth}"
                )
            disabled = self._resolve_rules(rules)
            result = _run_lint(
                self, yaml_text, allow_multiple_documents, max_depth,
                disabled,
            )
            result.pop("_bool_words", None)
            return result

        # mode == "fix_hints"
        for option, value in (
            ("remove_bom", remove_bom),
            ("strip_trailing_spaces", strip_trailing_spaces),
            ("quote_bool_words", quote_bool_words),
        ):
            if value is not None and not isinstance(value, bool):
                raise _err(f"{option} must be a boolean, got {value!r}")
        return _run_fix_hints(
            self, yaml_text,
            True if remove_bom is None else remove_bom,
            True if strip_trailing_spaces is None else strip_trailing_spaces,
            True if quote_bool_words is None else quote_bool_words,
        )

    # -- validation helpers ------------------------------------------------

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
