#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: regex_lint_tool.py

"""Regular-expression pattern linting, structure, explanation and risk
estimation tool.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency utility for the
*patterns themselves*. The family's regex tools operate on values —
``RegexTool`` (#767) matches, extracts, replaces and splits with a
caller-supplied pattern, ``RegexExplainerTool`` (#3804) narrates a
pattern's pieces — but neither of them, and nothing else in the
common tool family, answers *"is this pattern safe to compile, and
what could it cost to run against untrusted input?"* before an agent
embeds it in a pipeline. This tool is that missing static layer.

Everything is grounded in the CPython ``re`` engine of the running
interpreter (developed and oracle-tested against 3.11; 3.10 works
through the deprecated ``sre_parse`` alias of ``re._parser`` — the
parser is CPython-internal but its tuple-tree shape has been stable
since 3.8, and this is documented rather than hidden):

* compile verdicts are mirrored byte-for-byte from the real
  ``re.compile`` — when it raises, the finding reproduces the actual
  exception message and, when the engine reports one, the exact
  error position;
* CPython 3.11 facts baked into the knowledge base (each verified
  against this interpreter family in the test suite): a mid-pattern
  ``(?i)`` raises ``global flags not at the start of the
  expression``; possessive quantifiers (``a++``), atomic groups
  (``(?>...)``) and scoped inline flags (``(?i:...)``) compile on
  3.11 but not on 3.10 (the repository floor) — flagged as
  ``py311_only_syntax`` info; ``re`` treats a stray ``{...}`` that
  is not a valid quantifier as literal braces (flagged as a likely
  format-template leak); ``[`` inside a character class emits
  CPython's ``Possible nested set`` warning while POSIX engines
  would parse it completely differently — flagged; ``[]`` raises
  ``unterminated character set``; ``\w`` matches ``①`` U+2460 and
  CJK and ``\s`` matches NBSP under the default ``str`` semantics
  (verified: ``re.match(r"\\w", "①")`` is a match) while ``.`` does
  not match newline unless ``DOTALL`` is set — all surfaced as info
  findings.

Four modes:

* ``lint`` — pattern plus optional documented flag names
  (``IGNORECASE``, ``MULTILINE``, ``DOTALL``, ``ASCII``, ``UNICODE``,
  ``VERBOSE`` and their one-letter aliases) produce findings
  ``{code, message, span, severity}`` (``span`` is ``[start, end]``
  in the pattern string). Compile failures are mirrored from the
  real exception with named codes — ``parse_error`` plus specific
  codes such as ``unterminated_group``, ``unterminated_character_class``,
  ``duplicate_group_name``, ``undefined_group_reference``,
  ``unknown_group_name_ref``, ``lookbehind_variable_width`` (span
  located structurally — CPython reports no position for this
  error), ``bad_repeat_range`` (``{2,1}``), ``double_quantifier``
  (``a**``), ``misplaced_global_flag`` (``a(?i)b``),
  ``repeat_count_overflow`` (``a{4294967296}`` raises
  ``OverflowError`` at a bound below CPython's ``MAXREPEAT``) and
  ``pattern_too_deep`` (very deep nesting raises ``RecursionError``
  inside ``sre`` parsing; empirically depth 500 fails while 200
  compiles). The scanner mirrors CPython's ASCII-only digit rule:
  ``{m,n}`` bounds and backslash references consume ``0-9`` only, so
  ``a{٢}`` is literal brace text and ``\1٢`` is the reference ``\1``
  followed by the character ``٢`` — exactly what the engine does
  (``str.isdigit`` would accept both and even crash on ``'²'``).
  Compile-success findings are the static analyses:
  catastrophic-backtracking detection severity-graded —
  ``redos_exponential`` (warning; nested quantifiers over
  overlapping alphabets ``(a+)+``, ``(a*)*b``, empty-matching inner
  ``(a?)+``, bounded-outer ``(.*a){10}b``, and overlapping-prefix
  alternations under a quantifier ``(a|aa)+$``, ``(a|ab)*c``,
  ``(a|a)*``) versus ``redos_polynomial`` (info; adjacent unbounded
  overlapping quantifiers ``a*a*a*b``, ``(.*a).*b``). Exponential
  grading requires the ambiguity to compound with input length —
  an unbounded quantifier on the outer scope or on the repeated
  inner element — so bounded shapes whose re-partitioning space is
  a constant (the canonical IPv4 octet
  ``(25[0-5]|2[0-4]\d|[01]?\d?\d)`` under ``{3}``) stay quiet;
  ``redos_untrusted_input`` info notes for unbounded dot runs that
  escaped the graded detectors; ``nested_set_possible`` warning;
  ``brace_literal`` info; ``huge_repeat_bound`` warning (match-time
  work, documented heuristic); ``unicode_class_wide`` info (with the
  verified ``①``/NBSP facts and the ``re.ASCII`` suggestion);
  ``dot_not_dotall`` info reminder; ``inline_flag_scope`` info;
  ``py311_only_syntax`` info; ``empty_pattern`` info.
* ``structure`` — a deterministic parse-tree summary from the
  scanner (cross-checked against ``re._parser`` in the test suite):
  ``nodes`` (typed tree with spans, per-node quantifier ``{min,
  max, kind}`` and group metadata, capped output), a ``group_map``
  ``{number: name-or-null}`` that byte-agrees with the parser's own
  ``state.groupdict``, and ``group_spans`` ``{number: [start, end]}``
  pointing at the real parentheses. A conditional's yes/no split is
  the first ``|`` at the body's own nesting depth (CPython's rule);
  conditional ladders nested deeper than 200 levels — deeper than
  any consumer of the tree looks — are scanned opaquely with their
  capture groups still counted, so numbering stays correct without
  the recursive decomposition that would overflow the interpreter
  stack on ~500-deep ``(?(1)(?(1)...))`` patterns the engine itself
  compiles fine.
* ``explain`` — a deterministic human-readable walk: one English
  fragment per top-level alternative, a group index table and
  backreference/lookaround annotations.
* ``estimate`` — pattern plus a sample text length produce a
  ``basic_ops`` scan-work estimate (formula documented below) and a
  ``backtracking_risk_class`` of ``linear`` / ``polynomial`` /
  ``exponential`` / ``unknown`` with reasons. The classification is
  heuristic — regex power analysis is undecidable — and conservative
  by design (it over-warns rather than stays silent), which the
  docs state explicitly.

Strict validation (types, flag names, mode-specific options, a
4,000-character pattern cap, node-count caps — every limit is a
real settable pydantic model field, not a dead class constant),
no network, no third-party imports, deterministic output.
"""

import re
import warnings
from typing import Any, ClassVar, Iterator, Optional

from pydantic import ConfigDict, Field

from agentuniverse.agent.action.tool.tool import Tool

# CPython's regex parser: ``re._parser`` is the 3.11+ name; 3.10 still
# ships it as the (deprecated-alias) ``sre_parse`` module. The module
# is CPython-internal but its API surface has been stable 3.8–3.11;
# the tests cross-check this tool's own scanner against it.
try:  # pragma: no cover - exercised implicitly on every supported run
    import re._parser as _sre_parser
except ImportError:  # Python 3.10
    import sre_parse as _sre_parser  # type: ignore[no-redef]

try:  # pragma: no cover
    _MAXREPEAT: int = _sre_parser.MAXREPEAT
except AttributeError:  # pragma: no cover - future-proofing
    _MAXREPEAT = 4294967295

# Severity ranking for deterministic finding order.
_SEVERITY_RANK = {"error": 0, "warning": 1, "info": 2}

# Accepted flag names (long and one-letter forms, case-insensitive).
_FLAG_ALIASES = {
    "I": "IGNORECASE", "IGNORECASE": "IGNORECASE",
    "M": "MULTILINE", "MULTILINE": "MULTILINE",
    "S": "DOTALL", "DOTALL": "DOTALL",
    "A": "ASCII", "ASCII": "ASCII",
    "U": "UNICODE", "UNICODE": "UNICODE",
    "X": "VERBOSE", "VERBOSE": "VERBOSE",
}
_FLAG_VALUES = {
    "IGNORECASE": re.IGNORECASE,
    "MULTILINE": re.MULTILINE,
    "DOTALL": re.DOTALL,
    "ASCII": re.ASCII,
    "UNICODE": re.UNICODE,
    "VERBOSE": re.VERBOSE,
}
_FLAG_LETTERS = {"i", "m", "s", "a", "u", "x", "-"}

# re.error message fragments mapped to dedicated finding codes. The
# fallback is parse_error; the mirrored message is always str(exc).
_ERROR_CODE_MAP = (
    ("look-behind requires fixed-width", "lookbehind_variable_width"),
    ("redefinition of group name", "duplicate_group_name"),
    ("invalid group reference", "undefined_group_reference"),
    ("unknown group name", "unknown_group_name_ref"),
    ("unterminated character set", "unterminated_character_class"),
    ("missing ), unterminated subpattern", "unterminated_group"),
    ("min repeat greater than max repeat", "bad_repeat_range"),
    ("multiple repeat", "double_quantifier"),
    ("nothing to repeat", "nothing_to_repeat"),
    ("global flags not at the start", "misplaced_global_flag"),
    ("unexpected end of pattern", "unexpected_end"),
    ("unknown extension", "unknown_extension"),
    ("bad character in group name", "bad_group_name"),
    ("bad escape", "bad_escape"),
    ("missing {", "bad_escape"),
)

# Character-class shorthand escapes (``\d`` and friends).
_SHORTHAND = frozenset("dDwWsS")
# Zero-width escapes.
_ANCHOR_ESCAPES = frozenset("bBAZ")
# Escapes whose literal meaning differs from the escaped letter.
_LITERAL_ESCAPE_MAP = {"n": "\n", "t": "\t", "r": "\r", "f": "\f",
                       "v": "\v", "a": "\a", "0": "\0", "f": "\f"}

# Node kinds produced by the internal scanner.
K_LITERAL = "literal"
K_CLASS = "class"
K_DOT = "dot"
K_SHORTHAND = "shorthand"
K_ANCHOR = "anchor"
K_BACKREF = "backref"
K_GROUP = "group"
K_COND = "conditional"
K_BRACE = "brace_literal"
K_UNKNOWN = "unknown_extension"

# Group kinds.
G_CAPTURE = "capture"
G_NAMED = "named"
G_NONCAP = "noncapture"
G_LOOKAHEAD_POS = "lookahead_positive"
G_LOOKAHEAD_NEG = "lookahead_negative"
G_LOOKBEHIND_POS = "lookbehind_positive"
G_LOOKBEHIND_NEG = "lookbehind_negative"
G_ATOMIC = "atomic"
G_FLAGS_GLOBAL = "flags_global"
G_FLAGS_SCOPED = "flags_scoped"
G_COMMENT = "comment"
_LOOKBEHIND_KINDS = (G_LOOKBEHIND_POS, G_LOOKBEHIND_NEG)
_LOOKAROUND_KINDS = (G_LOOKAHEAD_POS, G_LOOKAHEAD_NEG) + _LOOKBEHIND_KINDS


# Nesting depth beyond which conditional bodies are scanned opaquely
# (see ``RegexLintTool._scan_conditional``): the decomposition there is
# recursive and would overflow the interpreter stack on ~500-deep
# conditionals the real engine compiles fine, while every consumer of
# the tree is depth-capped well below this bound anyway.
_CONDITIONAL_NESTING_CAP = 200


def _is_hex(ch: str) -> bool:
    return ch in "0123456789abcdefABCDEF"


# CPython's sre parser accepts only ASCII digits inside ``{m,n}`` and
# after a backslash (``re`` treats ``a{٢}`` as the literal text
# ``a{٢}`` and ``\\٢`` as a literal-escape, while ``str.isdigit`` also
# accepts ``'٢'``/``'²'`` and ``int('²')`` even raises) — the scanner
# mirrors the ASCII-only rule.
_ASCII_DIGITS = frozenset("0123456789")


def _is_ascii_digit(ch: str) -> bool:
    return ch in _ASCII_DIGITS


# Sentinel for "alphabet not yet computed" (None is a valid alphabet).
_ALPHA_UNSET = object()


def _ascii_digit_span(text: str) -> int:
    """Length of the leading run of ASCII digits in ``text``."""
    k = 0
    while k < len(text) and text[k] in _ASCII_DIGITS:
        k += 1
    return k


class _Node:
    """One parse-tree node (kept lightweight; serialized on demand)."""

    __slots__ = ("kind", "start", "end", "literal", "class_info",
                 "quant", "group", "branches", "parent", "alpha_cache")

    def __init__(self, kind: str, start: int, end: int) -> None:
        self.kind = kind
        self.start = start
        self.end = end
        self.literal: Any = None
        self.class_info: Any = None
        self.quant: Any = None
        self.group: Any = None
        self.branches: list[list["_Node"]] = []
        self.parent: Optional["_Node"] = None
        self.alpha_cache: Any = _ALPHA_UNSET

    def set_quant(self, quant: dict) -> None:
        self.quant = quant

    def is_group(self) -> bool:
        return self.kind == K_GROUP and isinstance(self.group, dict)


def _new_quant(quant_min: int, quant_max: int, kind: str,
               start: int, end: int) -> dict:
    return {"min": quant_min, "max": quant_max, "kind": kind,
            "span": (start, end)}


class RegexLintTool(Tool):
    """Static regular-expression pattern analyzer built on stdlib ``re``.

    Attributes:
        max_pattern_chars (int): Upper bound on the pattern length
            (real settable model field, like every limit below).
        max_findings (int): Cap on the lint findings list.
        max_nodes_out (int): Cap on serialized structure nodes.
        analysis_depth_cap (int): Depth beyond which detectors treat a
            subtree as opaque (the compile oracle is unaffected).
        huge_repeat_threshold (int): Bounded-repetition upper bound
            beyond which ``huge_repeat_bound`` fires.
        max_text_length (int): Upper bound on estimate's text length.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "regex_lint_tool"
    description: str = (
        "Regex lint tool — static analysis of regular-expression "
        "patterns: compile validity mirrored from the real re engine, "
        "severity-graded catastrophic-backtracking (ReDoS) risk "
        "detection and engine-portability flags, plus parse-tree "
        "structure, deterministic explanation and work estimation. "
        "Pure Python stdlib (re and the re._parser/sre_parse internal "
        "parser), no network. mode='lint' checks a pattern (with "
        "optional documented flags IGNORECASE/MULTILINE/DOTALL/ASCII/"
        "UNICODE/VERBOSE) and returns {code, message, span, severity} "
        "findings: compile failures mirror the actual exception "
        "(message and position, including [] raising 'unterminated "
        "character set', duplicate group names, undefined group "
        "references, (?<=a+) lookbehind fixed-width errors with the "
        "span located structurally, {2,1} min>max, a** multiple "
        "repeat, a(?i)b misplaced global flags, a{4294967296} "
        "OverflowError and very-deep-nesting RecursionError); "
        "compile-success analyses are severity-graded ReDoS detection "
        "(redos_exponential warning: (a+)+, (a*)*b, (a|aa)+$, (a|ab)*c, "
        "(.*a){10}b nested quantifiers and overlapping-prefix "
        "alternations — fired only when the ambiguity can compound with "
        "input length, i.e. an unbounded quantifier on the outer scope "
        "or the repeated inner element, so the canonical IPv4 octet "
        "(25[0-5]|2[0-4]\\d|[01]?\\d?\\d) under {3} stays quiet; "
        "redos_polynomial info: a*a*a*b, (.*a).*b "
        "adjacent unbounded overlapping quantifiers; redos_untrusted_"
        "input info notes), nested-set [[a][b]] warnings (CPython "
        "warns, POSIX engines diverge), literal-brace {name} format-"
        "template leak info, huge {1,1000000} repeat bounds warning, "
        "unicode pitfalls info (\\w matches ① and CJK, \\s matches "
        "NBSP — verified on CPython 3.11 — re.ASCII suggested), "
        "dot-does-not-match-newline reminders, inline-flag scoping "
        "notes and py311_only_syntax info for possessive/atomic/"
        "scoped-flag syntax absent from 3.10. mode='structure' "
        "returns a deterministic parse-tree summary with typed nodes, "
        "per-node quantifiers, a group_map byte-agreeing with the "
        "real parser's state.groupdict and group spans pointing at "
        "real parentheses. mode='explain' returns deterministic "
        "English fragments per top-level alternative, a group index "
        "table and backreference/lookaround annotations. "
        "mode='estimate' returns a documented basic_ops scan-work "
        "estimate plus a backtracking_risk_class of linear/polynomial/"
        "exponential/unknown with reasons (heuristic, conservative). "
        "All documented limits (max_pattern_chars, max_findings, "
        "max_nodes_out, analysis_depth_cap, huge_repeat_threshold, "
        "max_text_length) are real settable model fields. "
        "Strict validation, size caps, deterministic output."
    )

    MODES: ClassVar[tuple] = ("lint", "structure", "explain", "estimate")
    FLAG_MODES: ClassVar[tuple] = ("lint", "estimate")

    # Real pydantic fields: every limit documented in the class
    # docstring's Attributes section is settable per instance
    # (``RegexLintTool(max_findings=5)``), validated at construction.
    max_pattern_chars: int = Field(default=4_000, ge=1)
    max_findings: int = Field(default=200, ge=1)
    max_nodes_out: int = Field(default=2_000, ge=1)
    analysis_depth_cap: int = Field(default=250, ge=1)
    huge_repeat_threshold: int = Field(default=100_000, ge=2)
    max_text_length: int = Field(default=10**9, ge=1)

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(self, mode: Any, pattern: Any = None,
                flags: Any = None, text_length: Any = None
                ) -> dict[str, Any]:
        """Run one regex pattern analysis.

        Args:
            mode (str): One of ``lint`` / ``structure`` / ``explain`` /
                ``estimate``.
            pattern (str): The regular-expression pattern to analyze
                (up to 4,000 characters; the empty pattern is valid
                and reported honestly).
            flags (list[str] | str | None): Flag names for ``lint`` and
                ``estimate`` — ``IGNORECASE``, ``MULTILINE``,
                ``DOTALL``, ``ASCII``, ``UNICODE``, ``VERBOSE`` or
                their one-letter aliases. Rejected in the other modes.
            text_length (int): ``estimate`` only — the sample input
                length (0..10^9) the work estimate assumes. Rejected
                in the other modes.

        Returns:
            Dict[str, Any]: The mode's payload.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        pat = self._validate_pattern(pattern)
        if mode in self.FLAG_MODES:
            flag_names = self._validate_flags(flags)
        else:
            self._reject_option("flags", flags,
                                allowed_modes=self.FLAG_MODES)
            flag_names = []
        if mode == "estimate":
            length = self._validate_text_length(text_length)
        else:
            self._reject_option("text_length", text_length,
                                allowed_modes=("estimate",))
            length = 0
        flag_value = 0
        for name in flag_names:
            flag_value |= _FLAG_VALUES[name]

        if mode == "lint":
            return self._run_lint(pat, flag_names, flag_value)
        root = self._parse_tree(pat, flag_value)
        if mode == "structure":
            return self._run_structure(pat, root, flag_names, flag_value)
        if mode == "explain":
            return self._run_explain(pat, root)
        return self._run_estimate(pat, root, flag_names, length)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    def _invalid(self, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"regex_lint_tool: {message}")

    def _validate_pattern(self, pattern: Any) -> str:
        """Validate the pattern (empty allowed, oversized rejected)."""
        if pattern is None or isinstance(pattern, bool) \
                or not isinstance(pattern, str):
            self._invalid(f"pattern must be a string (got {pattern!r})")
        if len(pattern) > self.max_pattern_chars:
            self._invalid(
                f"pattern exceeds the {self.max_pattern_chars:,}-character "
                f"limit (got {len(pattern):,} characters)"
            )
        return pattern

    def _validate_flags(self, flags: Any) -> list[str]:
        """Validate and normalize the flag-name list."""
        if flags is None:
            return []
        if isinstance(flags, str):
            items = [flags]
        elif isinstance(flags, (list, tuple)) and all(
                isinstance(f, str) for f in flags):
            items = list(flags)
        else:
            self._invalid(
                "flags must be a flag name or a list of flag names from "
                "IGNORECASE, MULTILINE, DOTALL, ASCII, UNICODE, VERBOSE "
                f"(or i, m, s, a, u, x) (got {flags!r})"
            )
        resolved: list[str] = []
        for item in items:
            name = _FLAG_ALIASES.get(item.upper())
            if name is None:
                self._invalid(
                    f"unknown flag {item!r}; valid flags: IGNORECASE, "
                    "MULTILINE, DOTALL, ASCII, UNICODE, VERBOSE "
                    "(or i, m, s, a, u, x)"
                )
            if name not in resolved:
                resolved.append(name)
        if "ASCII" in resolved and "UNICODE" in resolved:
            self._invalid(
                "flags ASCII and UNICODE are mutually exclusive "
                "(re.compile rejects re.ASCII | re.UNICODE)"
            )
        return resolved

    def _validate_text_length(self, text_length: Any) -> int:
        """Validate estimate's sample text length."""
        if isinstance(text_length, bool) or not isinstance(text_length, int):
            self._invalid(
                f"text_length must be an integer (got {text_length!r})"
            )
        if text_length < 0 or text_length > self.max_text_length:
            self._invalid(
                f"text_length must be between 0 and {self.max_text_length:,} "
                f"(got {text_length:,})"
            )
        return text_length

    def _reject_option(self, name: str, value: Any,
                       allowed_modes: tuple = ()) -> None:
        """Reject an option passed outside its allowed modes."""
        if value is not None:
            if allowed_modes:
                self._invalid(
                    f"{name} is only accepted in {', '.join(allowed_modes)} "
                    "mode"
                )
            else:
                self._invalid(f"{name} is not accepted in this mode")

    # ------------------------------------------------------------------ #
    # Compile oracle — the verdict mirrored byte-for-byte
    # ------------------------------------------------------------------ #

    def _compile_verdict(self, pattern: str, flag_value: int) -> dict:
        """Run the real compile and mirror its outcome.

        Returns ``{"raises", "exc_type", "message", "position"}``.
        RecursionError from absurd nesting and OverflowError from
        repeat counts beyond MAXREPEAT are part of the honest verdict
        (both verified on CPython 3.11: depth 500 nesting fails while
        depth 200 compiles; ``a{4294967296}`` raises OverflowError
        while ``a{4294967295}`` — MAXREPEAT itself — compiles).
        """
        try:
            with warnings.catch_warnings():
                # CPython emits "Possible nested set" warnings during
                # compile; the lint layer reports that condition itself
                # (nested_set_possible) with a span, so the raw warning
                # is suppressed here for deterministic behavior.
                warnings.simplefilter("ignore")
                re.compile(pattern, flag_value)
        except re.error as exc:
            return {"raises": True, "exc_type": "re.error",
                    "message": str(exc),
                    "position": getattr(exc, "pos", None)}
        except OverflowError as exc:
            return {"raises": True, "exc_type": "OverflowError",
                    "message": str(exc) or "the repetition number is "
                                            "too large",
                    "position": None}
        except RecursionError:
            return {"raises": True, "exc_type": "RecursionError",
                    "message": "maximum recursion depth exceeded while "
                               "parsing (pattern nesting too deep for "
                               "CPython's sre parser)",
                    "position": None}
        return {"raises": False, "exc_type": None, "message": None,
                "position": None}

    # ------------------------------------------------------------------ #
    # Structural scanner — iterative, span-accurate
    # ------------------------------------------------------------------ #

    def _parse_tree(self, pattern: str, flag_value: int,
                    cond_depth: int = 0) -> _Node:
        """Scan the pattern into a span-accurate tree (iterative).

        The scanner never raises on malformed input: compile failures
        are the compile oracle's job; unterminated constructs simply
        end the scan gracefully. Group numbers follow CPython's rule
        (opening-paren order; only capturing and named groups count).
        ``cond_depth`` tracks conditional nesting so absurdly deep
        ``(?(1)(?(1)...))`` ladders degrade instead of recursing.
        """
        verbose = bool(flag_value & re.VERBOSE)
        root = _Node("root", 0, len(pattern))
        # Stack frames: (group_node, outer_sequence, outer_branches)
        stack: list[tuple[_Node, list[_Node], list[list[_Node]]]] = []
        current: list[_Node] = []
        branches: list[list[_Node]] = []
        group_counter = 0
        i, n = 0, len(pattern)
        last_repeatable: Optional[_Node] = None

        while i < n:
            ch = pattern[i]
            # VERBOSE mode ignores whitespace and #-comments outside
            # character classes.
            if verbose and ch == "#":
                j = pattern.find("\n", i)
                i = n if j == -1 else j + 1
                continue
            if verbose and ch.isspace():
                i += 1
                continue
            if ch == "\\":
                node, i2 = self._scan_escape(pattern, i)
                current.append(node)
                i = i2
                last_repeatable = None if node.kind == K_ANCHOR else node
                continue
            if ch == "[":
                node, i2 = self._scan_class(pattern, i)
                current.append(node)
                i = i2
                last_repeatable = node
                continue
            if ch == ".":
                node = _Node(K_DOT, i, i + 1)
                current.append(node)
                i += 1
                last_repeatable = node
                continue
            if ch in "^$":
                node = _Node(K_ANCHOR, i, i + 1)
                node.literal = ch
                current.append(node)
                i += 1
                last_repeatable = None
                continue
            if ch == "|":
                branches.append(current[:])
                current.clear()
                i += 1
                last_repeatable = None
                continue
            if ch == "(":
                info = self._scan_group_prefix(pattern, i)
                if info["error"] is not None:
                    node = _Node(K_UNKNOWN, i, n)
                    node.literal = info["error"]
                    current.append(node)
                    break
                if info["kind"] in (G_FLAGS_GLOBAL, G_COMMENT):
                    node = _Node(K_GROUP, info["start"], info["end"])
                    node.group = info
                    current.append(node)
                    i = info["end"]
                    last_repeatable = None
                    continue
                if info["kind"] == "backref_name":
                    node = _Node(K_BACKREF, info["start"], info["end"])
                    node.literal = info["name"]
                    current.append(node)
                    i = info["end"]
                    last_repeatable = node
                    continue
                if info["kind"] == K_COND:
                    node, i2, group_counter = self._scan_conditional(
                        pattern, info, group_counter,
                        cond_depth=cond_depth)
                    current.append(node)
                    i = i2
                    last_repeatable = node
                    continue
                if info["kind"] in (G_CAPTURE, G_NAMED):
                    group_counter += 1
                    info["number"] = group_counter
                gnode = _Node(K_GROUP, info["start"], n)
                gnode.group = info
                stack.append((gnode, current, branches))
                current = []
                branches = []
                i = info["body_start"]
                last_repeatable = None
                continue
            if ch == ")":
                if stack:
                    gnode, outer_current, outer_branches = stack.pop()
                    body_branches = list(branches)
                    body_branches.append(current[:])
                    current.clear()
                    gnode.branches = body_branches
                    gnode.end = i + 1
                    for br in body_branches:
                        for child in br:
                            child.parent = gnode
                    outer_current.append(gnode)
                    current = outer_current
                    branches = outer_branches
                    i += 1
                    last_repeatable = gnode
                    continue
                # Stray ')' is a literal for CPython.
                node = _Node(K_LITERAL, i, i + 1)
                node.literal = ")"
                current.append(node)
                i += 1
                last_repeatable = node
                continue
            if ch == "{":
                quant, i2 = self._scan_brace(pattern, i)
                if quant is not None and last_repeatable is not None \
                        and last_repeatable.quant is None:
                    last_repeatable.set_quant(quant)
                    i = i2
                    continue
                # CPython treats a brace run that is not an applicable
                # quantifier as literal text (including '{2}' with
                # nothing to repeat — unlike '*', which errors).
                node = _Node(K_BRACE, i, i2)
                node.literal = pattern[i:i2]
                current.append(node)
                i = i2
                last_repeatable = node
                continue
            if ch in "*+?":
                if last_repeatable is not None and \
                        last_repeatable.quant is None:
                    qmin, qmax = {"*": (0, _MAXREPEAT),
                                  "+": (1, _MAXREPEAT),
                                  "?": (0, 1)}[ch]
                    kind = "greedy"
                    end = i + 1
                    if i + 1 < n and pattern[i + 1] == "?":
                        kind = "lazy"
                        end += 1
                    elif i + 1 < n and pattern[i + 1] == "+":
                        kind = "possessive"
                        end += 1
                    last_repeatable.set_quant(
                        _new_quant(qmin, qmax, kind, i, end))
                    i = end
                    continue
                # Nothing to repeat: CPython errors ('*') or takes the
                # brace literally; the compile oracle owns the verdict.
                node = _Node(K_LITERAL, i, i + 1)
                node.literal = ch
                current.append(node)
                i += 1
                last_repeatable = node
                continue
            node = _Node(K_LITERAL, i, i + 1)
            node.literal = ch
            current.append(node)
            i += 1
            last_repeatable = node

        # Close any unbalanced groups gracefully; the compile oracle
        # reports the actual error.
        while stack:
            gnode, outer_current, outer_branches = stack.pop()
            body_branches = list(branches)
            body_branches.append(current[:])
            current.clear()
            gnode.branches = body_branches
            gnode.end = n
            for br in body_branches:
                for child in br:
                    child.parent = gnode
            outer_current.append(gnode)
            current = outer_current
            branches = outer_branches
        if current or not branches:
            branches.append(current[:])
        root.branches = branches
        for br in branches:
            for child in br:
                child.parent = root
        return root

    def _scan_escape(self, pattern: str, i: int) -> tuple[_Node, int]:
        """Scan one backslash escape starting at ``pattern[i] == '\'``."""
        n = len(pattern)
        start = i
        j = i + 1
        if j >= n:  # trailing bare backslash: literal
            node = _Node(K_LITERAL, start, n)
            node.literal = "\\"
            return node, n
        c = pattern[j]
        if c in _SHORTHAND:
            node = _Node(K_SHORTHAND, start, j + 1)
            node.literal = c
            return node, j + 1
        if c in _ANCHOR_ESCAPES:
            node = _Node(K_ANCHOR, start, j + 1)
            node.literal = "\\" + c
            return node, j + 1
        if c == "N":
            if j + 1 < n and pattern[j + 1] == "{":
                close = pattern.find("}", j + 2)
                if close != -1:
                    node = _Node(K_LITERAL, start, close + 1)
                    node.literal = pattern[start:close + 1]
                    return node, close + 1
            node = _Node(K_LITERAL, start, j + 1)
            node.literal = pattern[start:j + 1]
            return node, j + 1
        if c == "0":
            k = j + 1
            while k < n and k - j <= 3 and pattern[k] in "01234567":
                k += 1
            node = _Node(K_LITERAL, start, k)
            node.literal = pattern[start:k]
            return node, k
        if _is_ascii_digit(c):
            # CPython consumes only ASCII digits into the reference;
            # anything else is a separate literal (e.g. ``\\1٢`` is
            # backref 1 followed by the character ``٢``).
            k = j + 1
            while k < n and _is_ascii_digit(pattern[k]):
                k += 1
            node = _Node(K_BACKREF, start, k)
            node.literal = pattern[j:k]
            return node, k
        if c == "x" and j + 2 < n and _is_hex(pattern[j + 1]) \
                and _is_hex(pattern[j + 2]):
            node = _Node(K_LITERAL, start, j + 3)
            node.literal = pattern[start:j + 3]
            return node, j + 3
        if c == "u" and j + 4 < n and all(
                _is_hex(pattern[j + t]) for t in range(1, 5)):
            node = _Node(K_LITERAL, start, j + 5)
            node.literal = pattern[start:j + 5]
            return node, j + 5
        if c == "U" and j + 8 < n and all(
                _is_hex(pattern[j + t]) for t in range(1, 9)):
            node = _Node(K_LITERAL, start, j + 9)
            node.literal = pattern[start:j + 9]
            return node, j + 9
        # Everything else is a single literal character (unknown alpha
        # escapes like \p are compile errors the oracle reports;
        # punctuation escapes stand for the escaped character).
        node = _Node(K_LITERAL, start, j + 1)
        node.literal = pattern[start:j + 1]
        return node, j + 1

    @staticmethod
    def _escape_char(source: str) -> str:
        """The single character an escape-literal node stands for."""
        if not source.startswith("\\") or len(source) < 2:
            return source
        body = source[1:]
        if body and body[0] in _LITERAL_ESCAPE_MAP:
            return _LITERAL_ESCAPE_MAP[body[0]]
        if body[:1] == "x" and len(body) == 3:
            try:
                return chr(int(body[1:], 16))
            except ValueError:
                return body
        if body[:1] == "u" and len(body) == 5:
            try:
                return chr(int(body[1:], 16))
            except ValueError:
                return body
        return body if len(body) == 1 else body[:1]

    def _scan_class(self, pattern: str, i: int) -> tuple[_Node, int]:
        """Scan one character class starting at ``pattern[i] == '['``."""
        n = len(pattern)
        start = i
        j = i + 1
        negated = False
        if j < n and pattern[j] == "^":
            negated = True
            j += 1
        chars: list[str] = []
        ranges: list[list[str]] = []
        categories: list[str] = []
        nested_set = False
        first = True
        pending: Optional[str] = None  # last single char, range-eligible
        while j < n and (pattern[j] != "]" or first):
            c = pattern[j]
            first = False
            if c == "\\" and j + 1 < n:
                e = pattern[j + 1]
                if e in _SHORTHAND:
                    categories.append(e)
                    pending = None
                elif e == "N" and pattern[j + 2:j + 3] == "{":
                    close = pattern.find("}", j + 3)
                    j = n - 2 if close == -1 else close - 1
                    pending = None
                elif e == "x" and pattern[j + 3:j + 4] and \
                        _is_hex(pattern[j + 2]) and _is_hex(pattern[j + 3]):
                    chars.append(self._escape_char(pattern[j:j + 4]))
                    pending = chars[-1]
                    j += 4
                    continue
                else:
                    chars.append(self._escape_char(pattern[j:j + 2]))
                    pending = chars[-1]
                j += 2
                continue
            if c == "[":
                nested_set = True
                pending = None
                j += 1
                continue
            if c == "-" and pending is not None and j + 1 < n \
                    and pattern[j + 1] != "]":
                hi_src = pattern[j + 1]
                if hi_src == "\\" and j + 2 < n:
                    hi = self._escape_char(pattern[j + 1:j + 3])
                    j += 2
                else:
                    hi = hi_src
                    j += 1
                ranges.append([pending, hi])
                if pending in chars:
                    chars.remove(pending)
                pending = None
                j += 1
                continue
            chars.append(c)
            pending = c
            j += 1
        node = _Node(K_CLASS, start, min(j + 1, n))
        node.class_info = {
            "negated": negated,
            "chars": sorted(set(chars)),
            "ranges": ranges,
            "categories": sorted(set(categories)),
            "nested_set": nested_set,
        }
        return node, min(j + 1, n)

    def _scan_group_prefix(self, pattern: str, i: int) -> dict:
        """Classify a ``(`` prefix; never raises."""
        n = len(pattern)
        info = {"start": i, "end": None, "body_start": None,
                "kind": G_CAPTURE, "name": None, "number": None,
                "flags": None, "error": None}
        if i + 1 >= n or pattern[i + 1] != "?":
            info["body_start"] = i + 1
            return info
        j = i + 2
        if j >= n:
            info["error"] = "unexpected end of pattern"
            return info
        c = pattern[j]
        if c == ":":
            info["kind"] = G_NONCAP
            info["body_start"] = j + 1
            return info
        if c == "=":
            info["kind"] = G_LOOKAHEAD_POS
            info["body_start"] = j + 1
            return info
        if c == "!":
            info["kind"] = G_LOOKAHEAD_NEG
            info["body_start"] = j + 1
            return info
        if c == ">":
            info["kind"] = G_ATOMIC
            info["body_start"] = j + 1
            return info
        if c == "#":
            close = pattern.find(")", j + 1)
            info["kind"] = G_COMMENT
            info["end"] = n if close == -1 else close + 1
            return info
        if c == "<":
            if j + 1 < n:
                d = pattern[j + 1]
                if d == "=":
                    info["kind"] = G_LOOKBEHIND_POS
                    info["body_start"] = j + 2
                    return info
                if d == "!":
                    info["kind"] = G_LOOKBEHIND_NEG
                    info["body_start"] = j + 2
                    return info
            # (?<name>…): .NET/JS-style named group — Python rejects it.
            info["error"] = "unknown extension ?<"
            return info
        if c == "P":
            if j + 1 < n and pattern[j + 1] == "<":
                close = pattern.find(">", j + 2)
                if close == -1:
                    info["error"] = "unknown extension ?P<"
                    return info
                info["kind"] = G_NAMED
                info["name"] = pattern[j + 2:close]
                info["body_start"] = close + 1
                return info
            if j + 1 < n and pattern[j + 1] == "=":
                close = pattern.find(")", j + 2)
                if close == -1:
                    info["error"] = "unknown extension ?P="
                    return info
                info["kind"] = "backref_name"
                info["name"] = pattern[j + 2:close]
                info["end"] = close + 1
                return info
            info["error"] = "unknown extension ?P"
            return info
        if c == "(":
            close = pattern.find(")", j + 1)
            if close == -1:
                info["error"] = "unexpected end of pattern"
                return info
            info["kind"] = K_COND
            info["name"] = pattern[j + 1:close]
            info["body_start"] = close + 1
            return info
        # Inline flags: (?imsx-a) global or (?imsx-a: scoped.
        k = j
        while k < n and pattern[k] in _FLAG_LETTERS and \
                (pattern[k].isalpha() or pattern[k] == "-"):
            k += 1
        flag_part = pattern[j:k]
        valid = bool(flag_part) and all(
            f.isalpha() or f == "-" for f in flag_part) and all(
            f.lower() in _FLAG_LETTERS for f in flag_part)
        if valid and k < n and pattern[k] in (")", ":"):
            if pattern[k] == ")":
                info["kind"] = G_FLAGS_GLOBAL
            else:
                info["kind"] = G_FLAGS_SCOPED
            info["flags"] = flag_part
            info["end"] = k + 1 if pattern[k] == ")" else info["end"]
            info["body_start"] = None if pattern[k] == ")" else k + 1
            return info
        info["error"] = "unknown extension ?" + pattern[j]
        return info

    def _scan_conditional(self, pattern: str, info: dict,
                          group_counter: int,
                          cond_depth: int = 0) -> tuple[_Node, int, int]:
        """Scan ``(?(ref)yes|no)``; sub-branches keep whole-pattern
        spans and continue the outer group numbering.

        The yes/no separator is the first ``|`` at the conditional
        body's own nesting depth (CPython semantics — a ``|`` inside a
        nested group, class or comment does not split). Conditional
        nesting deeper than ``_CONDITIONAL_NESTING_CAP`` levels is
        scanned opaquely: capture groups inside the body are still
        counted (so later group numbers stay correct) but the body is
        not decomposed — beyond that depth the structure serializer
        and every detector are depth-capped anyway, and the recursive
        decomposition would otherwise overflow the interpreter stack
        on patterns the real engine compiles fine.
        """
        n = len(pattern)
        node = _Node(K_COND, info["start"], n)
        node.group = dict(info)
        body_start = info["body_start"]
        k = self._find_conditional_end(pattern, body_start)
        node.end = min(k + 1, n)

        if cond_depth >= _CONDITIONAL_NESTING_CAP:
            node.group["degraded"] = True
            ranges = self._capture_group_ranges_raw(pattern, body_start, k)
            # Each counted group becomes a placeholder node that rides
            # the tree like any ordinary group: enclosing conditional
            # parts renumber it span-ordered at every level, so the
            # global numbering stays correct across sub-parse
            # boundaries without any out-of-band accounting.
            placeholders: list[_Node] = []
            for gstart, gend in ranges:
                group_counter += 1
                ph = _Node(K_GROUP, gstart, gend)
                ph.group = {"kind": G_CAPTURE, "number": group_counter,
                            "name": None, "placeholder": True}
                ph.parent = node
                placeholders.append(ph)
            node.branches = [placeholders]
            return node, node.end, group_counter

        # First '|' at the body's own depth splits yes from no.
        sep = self._find_top_level_bar(pattern, body_start, k)
        yes_src = pattern[body_start:sep] if sep != -1 \
            else pattern[body_start:k]
        no_src = pattern[sep + 1:k] if sep != -1 else ""
        while len(node.branches) < 2:
            node.branches.append([])

        sub_yes = self._parse_tree(yes_src, 0, cond_depth + 1)
        yes_branch = sub_yes.branches[0] if sub_yes.branches else []
        group_counter = self._renumber_and_attach(
            node, 0, sub_yes, yes_branch, body_start, group_counter)

        sub_no = self._parse_tree(no_src, 0, cond_depth + 1)
        if len(sub_no.branches) <= 1:
            no_branch = sub_no.branches[0] if sub_no.branches else []
            offset = sep + 1 if sep != -1 else k
            group_counter = self._renumber_and_attach(
                node, 1, sub_no, no_branch, offset, group_counter)
        else:
            # The no side keeps its own alternation (e.g. the ``c|d``
            # of ``(?(1)b|c|d)``): wrap it in a synthetic non-capturing
            # group so both alternatives survive the walk.
            wrapper = _Node(K_GROUP, 0, len(no_src))
            wrapper.group = {"kind": G_NONCAP, "number": None,
                             "name": None}
            wrapper.branches = sub_no.branches
            for branch in wrapper.branches:
                for child in branch:
                    child.parent = wrapper
            offset = sep + 1 if sep != -1 else k
            group_counter = self._renumber_and_attach(
                node, 1, sub_no, [wrapper], offset, group_counter)
            wrapper.parent = node
        return node, node.end, group_counter

    def _renumber_and_attach(self, node: _Node, target: int, sub: _Node,
                             branch: list[_Node], offset: int,
                             group_counter: int) -> int:
        """Renumber a parsed conditional part's groups onto the global
        counter (span order is preserved by parsing yes before no),
        shift it to whole-pattern coordinates and attach it."""
        for _, gnode in self._groups_in_order(sub):
            group_counter += 1
            gnode.group["number"] = group_counter
        self._shift_tree(branch, offset)
        for child in branch:
            child.parent = node
        node.branches[target] = branch
        return group_counter

    def _find_conditional_end(self, pattern: str, body_start: int) -> int:
        """Index of the ``)`` closing a conditional body (len == end)."""
        n = len(pattern)
        depth = 1
        k = body_start
        while k < n:
            c = pattern[k]
            if c == "\\":
                k += 2
                continue
            if c == "[":
                k = self._skip_class(pattern, k)
                continue
            if c == "(" and pattern[k + 1:k + 2] == "?" \
                    and pattern[k + 2:k + 3] == "#":
                close = pattern.find(")", k + 3)
                k = n if close == -1 else close + 1
                continue
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    return k
            k += 1
        return n

    def _find_top_level_bar(self, pattern: str, start: int,
                            end: int) -> int:
        """Index of the first ``|`` at depth 0 in ``pattern[start:end]``
        (-1 when absent), skipping escapes, classes and comments."""
        depth = 0
        j = start
        while j < end:
            c = pattern[j]
            if c == "\\":
                j += 2
                continue
            if c == "[":
                j = self._skip_class(pattern, j)
                continue
            if c == "(" and pattern[j + 1:j + 2] == "?" \
                    and pattern[j + 2:j + 3] == "#":
                close = pattern.find(")", j + 3)
                j = end if close == -1 else close + 1
                continue
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == "|" and depth == 0:
                return j
            j += 1
        return -1

    def _capture_group_ranges_raw(self, pattern: str, start: int,
                                  end: int) -> list[tuple[int, int]]:
        """``(start, end)`` spans of capture groups in
        ``pattern[start:end]`` without recursion, in open-paren order
        (used by the degraded deep-conditional path so group numbering
        stays correct)."""
        ranges: list[tuple[int, int]] = []
        stack: list[tuple[int, bool]] = []
        j = start
        while j < end:
            c = pattern[j]
            if c == "\\":
                j += 2
                continue
            if c == "[":
                j = self._skip_class(pattern, j)
                continue
            if c == "(":
                if pattern[j + 1:j + 2] == "?" \
                        and pattern[j + 2:j + 3] == "#":
                    close = pattern.find(")", j + 3)
                    j = end if close == -1 else close + 1
                    continue
                sub = self._scan_group_prefix(pattern, j)
                is_capture = sub["error"] is None and sub["kind"] in (
                    G_CAPTURE, G_NAMED)
                stack.append((j, is_capture))
                if sub["body_start"] is not None:
                    j = sub["body_start"]
                elif sub["end"] is not None:
                    j = sub["end"]
                else:
                    j += 1
                continue
            if c == ")" and stack:
                opened, is_capture = stack.pop()
                if is_capture:
                    ranges.append((opened, j + 1))
            j += 1
        # Unbalanced groups (malformed input) keep open spans.
        ranges.extend((opened, end) for opened, is_capture
                      in reversed(stack) if is_capture)
        ranges.sort()
        return ranges

    def _groups_in_order(self, root: _Node) -> list[tuple[int, _Node]]:
        """Capture groups of a tree in open-paren (span) order."""
        found = []
        for node, _ in self._walk(root):
            if node.is_group() and node.group.get("number"):
                found.append((node.start, node))
        found.sort(key=lambda item: item[0])
        return [(g.start, g) for _, g in
                sorted([(s, g) for s, g in found], key=lambda t: t[0])]

    def _shift_tree(self, nodes: list[_Node], offset: int) -> None:
        """Shift every span in a subtree by ``offset``."""
        for node in nodes:
            stack = [node]
            while stack:
                cur = stack.pop()
                cur.start += offset
                cur.end += offset
                if cur.quant is not None:
                    s, e = cur.quant["span"]
                    cur.quant["span"] = (s + offset, e + offset)
                for branch in cur.branches:
                    stack.extend(branch)

    def _skip_class(self, pattern: str, i: int) -> int:
        """Index just past a character class starting at ``[``."""
        n = len(pattern)
        j = i + 1
        first = True
        while j < n and (pattern[j] != "]" or first):
            if pattern[j] == "\\":
                j += 1
            first = False
            j += 1
        return j + 1

    def _scan_brace(self, pattern: str, i: int) -> tuple[Optional[dict], int]:
        """Scan a ``{...}`` run at ``i``.

        Returns ``(quantifier, end)`` when the run parses as a valid
        ``{m}``/``{m,}``/``{m,n}``/``{,n}`` quantifier, else
        ``(None, end)`` so the caller emits a literal-brace node
        (CPython semantics: matched literally).
        """
        n = len(pattern)
        close = pattern.find("}", i + 1)
        if close == -1:
            return None, n
        body = pattern[i + 1:close]
        if not body:
            return None, close + 1
        lo, sep, hi = body.partition(",")
        # ASCII-only digits: ``a{٢}``/``a{²}`` are literal braces for
        # the real engine even though ``str.isdigit`` accepts them.
        if not sep and lo and _ascii_digit_span(lo) != len(lo):
            return None, close + 1
        if sep and lo and _ascii_digit_span(lo) != len(lo):
            return None, close + 1
        if sep and hi and _ascii_digit_span(hi) != len(hi):
            return None, close + 1
        if not lo and (not sep or not hi):
            # "{}" and "{,}" are literals for CPython.
            return None, close + 1
        lo_n = int(lo) if lo else None
        hi_n = int(hi) if sep and hi else None
        if not sep:
            qmin = qmax = lo_n
        elif not hi:
            qmin, qmax = lo_n, _MAXREPEAT
        else:
            qmin = lo_n or 0
            qmax = hi_n
        kind = "greedy"
        end = close + 1
        if end < n and pattern[end] == "?":
            kind = "lazy"
            end += 1
        elif end < n and pattern[end] == "+":
            kind = "possessive"
            end += 1
        return _new_quant(qmin, qmax, kind, i, end), end

    # ------------------------------------------------------------------ #
    # Iterative tree walk
    # ------------------------------------------------------------------ #

    def _walk(self, root: _Node) -> Iterator[tuple[_Node, int]]:
        """Yield ``(node, depth)`` depth-first without recursion."""
        stack: list[tuple[_Node, int]] = [(root, 0)]
        while stack:
            node, depth = stack.pop()
            yield node, depth
            if depth >= self.analysis_depth_cap:
                continue
            children: list[_Node] = []
            for branch in node.branches:
                children.extend(branch)
            for child in reversed(children):
                stack.append((child, depth + 1))

    def _groups_by_number(self, root: _Node) -> dict[int, _Node]:
        groups: dict[int, _Node] = {}
        for node, _ in self._walk(root):
            if node.is_group() and node.group.get("number"):
                groups[node.group["number"]] = node
        return groups

    # ------------------------------------------------------------------ #
    # Width computation (lookbehind fixed-width mirror)
    # ------------------------------------------------------------------ #

    def _sequence_width(self, branch: list[_Node],
                        ctx: dict) -> Optional[tuple[int, int]]:
        """Width of one sequence; None when variable/unknown."""
        lo = hi = 0
        for child in branch:
            w = self._node_width(child, ctx)
            if w is None:
                return None
            lo += w[0]
            hi += w[1]
        return lo, hi

    def _node_width(self, node: _Node,
                    ctx: dict) -> Optional[tuple[int, int]]:
        """Compute ``(min, max)`` width or None (variable/unknown).

        Mirrors CPython: every alternation branch must share one fixed
        width, quantifiers must have min == max, and a backreference's
        width is its group's width. Iterative post-order so deep
        patterns cannot blow the interpreter stack; an explicit
        ``computing`` set breaks backreference cycles.
        """
        results: dict[int, Optional[tuple[int, int]]] = {}
        stack: list[tuple[_Node, int]] = [(node, 0)]
        while stack:
            current, phase = stack.pop()
            if phase == 1:
                results[id(current)] = self._eval_width(
                    current, results, ctx)
                continue
            stack.append((current, 1))
            if len(stack) > 4 * self.analysis_depth_cap:
                results[id(current)] = None
                stack.pop()  # drop the eval frame just pushed
                continue
            for branch in current.branches:
                for child in reversed(branch):
                    stack.append((child, 0))
        return results.get(id(node))

    def _eval_width(self, node: _Node,
                    results: dict[int, Optional[tuple[int, int]]],
                    ctx: dict) -> Optional[tuple[int, int]]:
        """Evaluate one node's width from already-evaluated children."""
        if node.kind == K_LITERAL:
            text = str(node.literal)
            width = 1 if text.startswith("\\") else len(text)
        elif node.kind in (K_CLASS, K_DOT, K_SHORTHAND):
            width = 1
        elif node.kind == K_ANCHOR:
            width = 0
        else:
            width = None
        if width is not None:
            if node.quant is not None:
                if node.quant["min"] != node.quant["max"]:
                    return None
                return width * node.quant["min"], width * node.quant["min"]
            return width, width
        if node.kind == K_BACKREF:
            ref = node.literal
            if isinstance(ref, str) and ref \
                    and _ascii_digit_span(ref) == len(ref):
                base = self._group_width(int(ref), ctx)
            else:
                base = None
            if base is None or node.quant is None:
                return base
            if node.quant["min"] != node.quant["max"]:
                return None
            return (base[0] * node.quant["min"],
                    base[0] * node.quant["min"])
        if node.kind in (K_GROUP, K_COND):
            if node.kind == K_COND and node.group \
                    and node.group.get("degraded"):
                return None  # opaque deep-conditional body
            widths = []
            for branch in node.branches:
                lo = hi = 0
                for child in branch:
                    w = results.get(id(child))
                    if w is None:
                        return None
                    lo += w[0]
                    hi += w[1]
                widths.append((lo, hi))
            if not widths:
                return 0, 0
            first = widths[0]
            if any(w != first for w in widths[1:]):
                return None
            if node.quant is not None:
                if node.quant["min"] != node.quant["max"]:
                    return None
                return (first[0] * node.quant["min"],
                        first[0] * node.quant["min"])
            return first
        return None

    def _group_width(self, number: int, ctx: dict) \
            -> Optional[tuple[int, int]]:
        """Width of capture group ``number`` (memoized, cycle-safe)."""
        if number in ctx["widths"]:
            return ctx["widths"][number]
        if number in ctx["computing"]:
            return None
        node = ctx["groups"].get(number)
        if node is None:
            return None
        ctx["computing"].add(number)
        virtual = _Node(K_GROUP, node.start, node.end)
        virtual.branches = node.branches
        virtual.quant = None
        width = self._node_width(virtual, ctx)
        ctx["computing"].discard(number)
        ctx["widths"][number] = width
        return width

    def _width_context(self, root: _Node) -> dict:
        return {"widths": {}, "computing": set(),
                "groups": self._groups_by_number(root)}

    def _lookbehind_fixed(self, node: _Node, ctx: dict) -> bool:
        """Structural verdict: is this lookbehind's width fixed?"""
        virtual = _Node(K_GROUP, node.start, node.end)
        virtual.branches = node.branches
        virtual.quant = None
        return self._node_width(virtual, ctx) is not None

    # ------------------------------------------------------------------ #
    # Alphabet approximation for overlap tests
    # ------------------------------------------------------------------ #

    def _alphabet(self, node: _Node) -> Any:
        """Approximate a node's alphabet for overlap testing.

        Returns a ``frozenset`` of characters, a shorthand marker
        (``"d" "w" "s" "D" "W" "S"``), the dot marker ``"."``, or
        ``None`` = unknown/unbounded — assumed to overlap everything
        (ranges wider than 16, negated classes, complex units).
        Results are memoized on the node so repeated pair probes over
        large patterns stay cheap instead of quadratic.
        """
        if node.alpha_cache is _ALPHA_UNSET:
            node.alpha_cache = self._compute_alphabet(node)
        return node.alpha_cache

    def _compute_alphabet(self, node: _Node) -> Any:
        """The uncached alphabet approximation (see ``_alphabet``)."""
        if node.quant is not None and node.quant["min"] > 1:
            pass  # repetition count does not change the alphabet
        if node.kind == K_LITERAL:
            text = str(node.literal)
            if text.startswith("\\"):
                return frozenset(self._escape_char(text))
            return frozenset(text) if text else frozenset()
        if node.kind == K_DOT:
            return "."
        if node.kind == K_SHORTHAND:
            return str(node.literal)
        if node.kind == K_CLASS:
            info = node.class_info or {}
            if info.get("negated"):
                return None
            if info.get("categories"):
                return None
            chars = set(info.get("chars", ()))
            for lo, hi in info.get("ranges", ()):
                if ord(hi) - ord(lo) > 256:
                    return None  # too wide to expand — assume overlap
                chars.update(chr(cp) for cp in range(ord(lo), ord(hi) + 1))
            return frozenset(chars)
        if node.kind == K_GROUP and node.branches and \
                all(len(branch) == 1 for branch in node.branches):
            # Single-element alternation like (a|b): union alphabets.
            merged: set = set()
            wildcard = False
            single = True
            for branch in node.branches:
                if len(branch) != 1:
                    single = False
                    break
                alpha = self._alphabet(branch[0])
                if alpha is None or alpha == "." or \
                        not isinstance(alpha, frozenset):
                    wildcard = True
                    break
                merged |= alpha
            if single and not wildcard:
                return frozenset(merged)
            return None
        return None

    def _overlaps(self, alpha_a: Any, alpha_b: Any) -> bool:
        """Conservative overlap test (True == assume overlap)."""
        if alpha_a is None or alpha_b is None:
            return True
        if alpha_a == "." or alpha_b == ".":
            return True
        if isinstance(alpha_a, frozenset) and isinstance(alpha_b, frozenset):
            return bool(alpha_a & alpha_b)
        if isinstance(alpha_a, str) and isinstance(alpha_b, str):
            if {alpha_a, alpha_b} == {"d", "s"}:
                return False
            return True
        if isinstance(alpha_a, frozenset):
            return any(self._char_in_category(c, alpha_b) for c in alpha_a)
        if isinstance(alpha_b, frozenset):
            return any(self._char_in_category(c, alpha_a) for c in alpha_b)
        return True

    @staticmethod
    def _char_in_category(ch: str, shorthand: str) -> bool:
        """Membership test through the real engine (deterministic)."""
        try:
            return re.fullmatch("\\" + shorthand, ch) is not None
        except re.error:
            return True

    def _node_covers_char(self, node: _Node, ch: str) -> bool:
        """Might this node consume the character ``ch``? (conservative)"""
        if node.kind == K_LITERAL:
            text = str(node.literal)
            if text.startswith("\\"):
                return ch == self._escape_char(text)
            return ch in text
        if node.kind == K_DOT:
            return True
        if node.kind == K_SHORTHAND:
            return self._char_in_category(ch, str(node.literal))
        if node.kind == K_CLASS:
            info = node.class_info or {}
            if info.get("negated"):
                return True
            if ch in info.get("chars", ()):
                return True
            for lo, hi in info.get("ranges", ()):
                if lo <= ch <= hi:
                    return True
            for cat in info.get("categories", ()):
                if self._char_in_category(ch, cat):
                    return True
            return False
        return True  # groups/backrefs/unknown — assume it can

    def _pins(self, mid: _Node, unit: _Node) -> bool:
        """True when ``mid`` is a mandatory separator that provably
        cannot consume any character ``unit`` can — it pins the runs
        and disambiguates the split."""
        if mid.quant is not None and mid.quant["min"] == 0:
            return False  # optional: may be skipped, cannot pin
        mid_chars: Optional[list[str]] = None
        if mid.kind == K_LITERAL:
            text = str(mid.literal)
            mid_chars = [self._escape_char(text)] if text.startswith("\\") \
                else list(text)
        elif mid.kind == K_CLASS and mid.class_info \
                and not mid.class_info.get("negated") \
                and not mid.class_info.get("categories"):
            info = mid.class_info
            mid_chars = list(info.get("chars", ()))
            for lo, hi in info.get("ranges", ()):
                if ord(hi) - ord(lo) > 256:
                    return False  # not enumerable — no proof
                mid_chars.extend(chr(cp) for cp in
                                 range(ord(lo), ord(hi) + 1))
        if mid_chars is None:
            return False
        return all(not self._node_covers_char(unit, c) for c in mid_chars)

    def _first_unit(self, branch: list[_Node]) -> Optional[_Node]:
        """The first consuming (non-zero-width) node of a sequence."""
        for child in branch:
            if child.kind != K_ANCHOR:
                return child
        return None

    def _is_unbounded(self, quant: Optional[dict]) -> bool:
        return quant is not None and quant["max"] >= _MAXREPEAT

    def _is_repeatable(self, quant: Optional[dict]) -> bool:
        return quant is not None and quant["max"] >= 2

    # ------------------------------------------------------------------ #
    # Backtracking / ReDoS detectors (iterative, conservative)
    # ------------------------------------------------------------------ #

    def _detect_redos(self, root: _Node) -> list[dict]:
        """Run the severity-graded backtracking detectors.

        Returns entries carrying ``grade`` = ``"exponential"`` or
        ``"polynomial"``; the lint layer maps grades to severities.
        Heuristic and conservative by design — ambiguity that cannot
        be disproved is assumed.
        """
        findings: list[dict] = []
        nodes = [node for node, _ in self._walk(root)]
        seen: set[tuple[str, int, int]] = set()

        def record(code: str, grade: str, span: tuple[int, int],
                   message: str) -> None:
            key = (code, span[0], span[1])
            if key in seen:
                return
            seen.add(key)
            findings.append({"code": code, "grade": grade,
                             "span": [span[0], span[1]],
                             "message": message})

        # --- Rule A: nested quantifiers over overlapping alphabets ---
        for node in nodes:
            if not (node.is_group() or node.kind in (K_DOT, K_SHORTHAND,
                                                     K_CLASS, K_LITERAL)):
                continue
            if not self._is_repeatable(node.quant):
                continue
            for desc, _ in self._walk(node):
                if desc is node:
                    continue
                if desc.quant is None:
                    continue
                # A nested repetition counts when it can repeat (max>=2)
                # or can match the empty string (min==0) — an
                # empty-matching inner element under a quantifier is
                # the (a?)+ shape.
                if not (self._is_repeatable(desc.quant)
                        or desc.quant["min"] == 0):
                    continue
                if not self._nested_related(desc, node):
                    continue
                # Compounding gate: the ambiguity must be able to grow
                # with the input — an unbounded quantifier either on
                # the outer scope (2^n partitions) or on the repeated
                # inner element (n^k splits). When both sides are
                # bounded (the canonical IPv4 octet
                # ``(25[0-5]|2[0-4]\d|[01]?\d?\d)`` under ``{3}``) the
                # re-partitioning space is a constant independent of
                # input length and the pattern is not catastrophic.
                if not (self._is_unbounded(node.quant)
                        or self._is_unbounded(desc.quant)):
                    continue
                inner_alpha = self._alphabet(desc)
                can_empty = desc.quant["min"] == 0
                follows = self._follow_within(desc, node)
                overlap = any(self._overlaps(inner_alpha,
                                            self._alphabet(f))
                              for f in follows)
                body_solo = self._body_is_only(node, desc)
                if can_empty or overlap or body_solo:
                    outer_desc = "unbounded" if self._is_unbounded(
                        node.quant) else f"{{...,{node.quant['max']}}}"
                    record(
                        "redos_exponential", "exponential",
                        (node.start, node.end),
                        f"nested quantifier: the group at [{node.start}, "
                        f"{node.end}] is repeated ({outer_desc}) and "
                        f"contains the repeated element at [{desc.start}, "
                        f"{desc.end}] with an ambiguous split of the same "
                        "text — on failing input the engine explores "
                        "exponentially many partitions (catastrophic "
                        "backtracking; classic ReDoS shapes: (a+)+, "
                        "(a*)*, (a?)+, (.*a){10}))"
                    )
                    break

        # --- Rule B: overlapping-prefix alternation under a quantifier --
        for node in nodes:
            if not self._is_repeatable(node.quant):
                continue
            # Compounding gate (same principle as Rule A): only an
            # unbounded outer repetition lets the per-iteration branch
            # ambiguity compound with input length — a bounded
            # repetition of an ambiguous alternation (the IPv4 octet
            # shape under ``{3}``) re-partitions a constant number of
            # ways and is left to the polynomial/untrusted notes.
            if not self._is_unbounded(node.quant):
                continue
            # The quantified unit's own branches …
            scopes: list[tuple[_Node, list[list[_Node]]]] = [
                (node, node.branches)]
            # … plus descendant alternations without an intervening
            # quantified group.
            for desc, _ in self._walk(node):
                if desc is node or len(desc.branches) < 2:
                    continue
                if not (desc.is_group() or desc.kind == K_COND):
                    continue
                if self._quantified_between(desc, node):
                    continue
                scopes.append((desc, desc.branches))
            for scope, branches in scopes:
                if len(branches) < 2:
                    continue
                units = [self._first_unit(b) for b in branches]
                for a in range(len(units)):
                    for b in range(a + 1, len(units)):
                        ua, ub = units[a], units[b]
                        if ua is None or ub is None:
                            record(
                                "redos_exponential", "exponential",
                                (scope.start, scope.end),
                                f"alternation at [{scope.start}, "
                                f"{scope.end}] under a quantifier has an "
                                "empty branch — every position can be "
                                "split arbitrarily many ways (exponential "
                                "on failing input)"
                            )
                            continue
                        if self._overlaps(self._alphabet(ua),
                                         self._alphabet(ub)):
                            record(
                                "redos_exponential", "exponential",
                                (scope.start, scope.start),
                                f"alternation at [{scope.start}, "
                                f"{scope.end}] under a quantifier has "
                                "branches whose first elements overlap — "
                                "failing input forces exponential "
                                "re-partitioning (classic shapes: "
                                "(a|aa)+$, (a|ab)*c, (a|a)*)"
                            )

        # --- Rule C: adjacent unbounded overlapping quantifiers ------
        unbounded_nodes = [nd for nd in nodes
                           if self._is_unbounded(nd.quant) and
                           nd.kind != K_ANCHOR]
        for node in unbounded_nodes:
            alpha_node = self._alphabet(node)
            for follower, intermediates in self._follow_chain(node):
                if not self._is_unbounded(follower.quant):
                    continue
                if follower is node:
                    continue
                if self._is_ancestor(follower, node) or \
                        self._is_ancestor(node, follower):
                    continue  # nested pair — Rule A territory
                if not self._overlaps(alpha_node, self._alphabet(follower)):
                    continue
                # Every consuming unit between the pair must also
                # overlap both alphabets — a mandatory separator whose
                # charset is disjoint from both (the '@' between
                # [\w.+-]+ and [\w-]+) pins the runs and kills the pair.
                alpha_follower = self._alphabet(follower)
                pinned = any(self._pins(mid, node) and
                             self._pins(mid, follower)
                             for mid in intermediates)
                if pinned:
                    continue
                if any(not (self._overlaps(self._alphabet(mid), alpha_node)
                            and self._overlaps(self._alphabet(mid),
                                              alpha_follower))
                       for mid in intermediates):
                    continue
                record(
                    "redos_polynomial", "polynomial",
                    (min(node.start, follower.start),
                     max(node.end, follower.end)),
                    f"adjacent unbounded quantifiers over overlapping "
                    f"text ([{node.start}, {node.end}] and "
                    f"[{follower.start}, {follower.end}]) — a failing "
                    "suffix forces quadratic re-splitting of the span "
                    "between them (polynomial backtracking; classic "
                    "shapes: a*a*a*b, (.*a).*b)"
                )
                break  # one finding per unbounded node is enough
        return findings

    def _nested_related(self, desc: _Node, outer: _Node) -> bool:
        """True when ``desc`` sits inside ``outer``'s body."""
        return self._is_ancestor(outer, desc)

    def _can_match_empty(self, node: _Node) -> bool:
        """Can this element match the empty string?"""
        if node.kind == K_ANCHOR:
            return True
        if node.quant is not None:
            return node.quant["min"] == 0
        return False

    def _tail_can_empty(self, parent: _Node, node: _Node) -> bool:
        """Can everything after ``node`` in its branch match empty?"""
        for branch in parent.branches:
            if node not in branch:
                continue
            return all(self._can_match_empty(child)
                       for child in branch[branch.index(node) + 1:])
        return False

    def _follow_within(self, node: _Node, scope: _Node) -> list[_Node]:
        """Units that can follow ``node`` before leaving ``scope``.

        The immediately following sibling found while climbing toward
        the scope, plus — because the scope group repeats and the rest
        of the body after ``node`` can match empty — the scope's own
        first units (the loop-around; this may legitimately be ``node``
        itself, the (a+|b+)*$ self-overlap shape). Deeper descendants
        are covered because Rule A runs on every quantified scope.
        """
        followers: list[_Node] = []
        ancestor = node.parent
        current = node
        while ancestor is not None and ancestor is not scope:
            follower = self._next_sibling(ancestor, current)
            if follower is not None:
                followers.append(follower)
                break  # only the immediately-following unit matters
            current = ancestor
            ancestor = ancestor.parent
        # Loop-around: reachable only when the body tail can match
        # empty (otherwise a mandatory separator pins the boundary —
        # the reason ([0-9]+[a-z]+)+ is safe while (\w+\s?)* is not).
        if node.parent is scope and self._tail_can_empty(scope, node):
            for branch in scope.branches:
                unit = self._first_unit(branch)
                if unit is not None:
                    followers.append(unit)
        return followers

    def _follow_chain(self, node: _Node,
                      max_hops: int = 12,
                      max_followers: int = 48
                      ) -> Iterator[tuple[_Node, list[_Node]]]:
        """Yield ``(follower, intermediates)`` pairs for consuming units
        on the linear path after ``node``: the rest of its branch, then
        — as each enclosing group completes — the units after that
        group, plus loop-around first units of quantified ancestors.
        Intermediates are the consuming units between ``node`` and the
        follower.

        Lazy on purpose: consumers stop at the first interesting
        follower (Rule C records one finding per node), so pairs are
        produced on demand and capped at ``max_followers`` — an eager
        list made 4,000-character ``a*a*...a*b`` patterns spend seconds
        building millions of pairs nobody reads.
        """
        pairs_yielded = 0
        intermediates: list[_Node] = []
        current = node
        ancestor = node.parent
        hops = 0
        while ancestor is not None and hops < max_hops:
            hops += 1
            for branch in ancestor.branches:
                if current not in branch:
                    continue
                for child in branch[branch.index(current) + 1:]:
                    if child.kind == K_ANCHOR:
                        continue
                    yield child, list(intermediates)
                    pairs_yielded += 1
                    if pairs_yielded >= max_followers:
                        return
                    intermediates.append(child)
                break
            # The enclosing group completes; loop around if quantified.
            if current is not node and current.quant is not None:
                for branch in current.branches:
                    unit = self._first_unit(branch)
                    if unit is not None and unit is not node:
                        yield unit, list(intermediates)
                        pairs_yielded += 1
                        if pairs_yielded >= max_followers:
                            return
            current = ancestor
            ancestor = ancestor.parent

    def _next_sibling(self, parent: _Node, node: _Node) -> Optional[_Node]:
        """The node right after ``node`` in its parent's branch."""
        for branch in parent.branches:
            if node not in branch:
                continue
            idx = branch.index(node)
            if idx + 1 < len(branch):
                nxt = branch[idx + 1]
                if nxt.kind == K_ANCHOR:
                    # Anchors are zero-width; keep looking past them.
                    if idx + 2 < len(branch):
                        return branch[idx + 2]
                    return None
                return nxt
            return None
        return None

    def _body_is_only(self, group_node: _Node, desc: _Node) -> bool:
        """True when the group's body is just the repeated element."""
        consuming = [nd for branch in group_node.branches for nd in branch
                     if nd.kind != K_ANCHOR]
        return consuming == [desc]

    def _quantified_between(self, node: _Node, scope: _Node) -> bool:
        """True when a quantified group sits between node and scope."""
        current = node.parent
        while current is not None and current is not scope:
            if current.quant is not None:
                return True
            current = current.parent
        return False

    def _is_ancestor(self, maybe_ancestor: _Node, node: _Node) -> bool:
        current = node.parent
        while current is not None:
            if current is maybe_ancestor:
                return True
            current = current.parent
        return False

    # ------------------------------------------------------------------ #
    # lint mode
    # ------------------------------------------------------------------ #

    def _run_lint(self, pattern: str, flag_names: list[str],
                  flag_value: int) -> dict[str, Any]:
        verdict = self._compile_verdict(pattern, flag_value)
        findings: list[dict] = []

        if verdict["raises"]:
            exc_type = verdict["exc_type"]
            message = verdict["message"] or ""
            position = verdict["position"]
            if exc_type == "OverflowError":
                code = "repeat_count_overflow"
            elif exc_type == "RecursionError":
                code = "pattern_too_deep"
            else:
                code = "parse_error"
                for fragment, mapped in _ERROR_CODE_MAP:
                    if fragment in message:
                        code = mapped
                        break
            span = [position, position + 1] if isinstance(position, int) \
                else [0, len(pattern)]
            if code == "lookbehind_variable_width":
                span = self._locate_variable_lookbehind(pattern) or span
            findings.append({
                "code": code,
                "message": f"re.compile raises {exc_type}: {message}",
                "span": span,
                "severity": "error",
            })
        else:
            findings.extend(self._static_findings(pattern, flag_value))

        findings.sort(key=lambda f: (
            f["span"][0], f["span"][1], _SEVERITY_RANK[f["severity"]],
            f["code"],
        ))
        truncated = False
        if len(findings) > self.max_findings:
            findings = findings[:self.max_findings]
            truncated = True
        summary = {level: sum(1 for f in findings
                              if f["severity"] == level)
                   for level in ("error", "warning", "info")}
        return {
            "pattern": pattern,
            "flags": flag_names,
            "compiles": not verdict["raises"],
            "compile_error": (None if not verdict["raises"] else {
                "type": verdict["exc_type"],
                "message": verdict["message"],
                "position": verdict["position"],
            }),
            "findings": findings,
            "summary": summary,
            "truncated": truncated,
        }

    def _locate_variable_lookbehind(
            self, pattern: str) -> Optional[list[int]]:
        """Span of the first lookbehind whose width is not fixed."""
        try:
            root = self._parse_tree(pattern, 0)
        except Exception:  # pragma: no cover - scanner is total
            return None
        ctx = self._width_context(root)
        for node, _ in self._walk(root):
            if not node.is_group():
                continue
            if node.group.get("kind") not in _LOOKBEHIND_KINDS:
                continue
            if not self._lookbehind_fixed(node, ctx):
                return [node.start, node.end]
        return None

    def _static_findings(self, pattern: str, flag_value: int) -> list[dict]:
        """Findings for a pattern that compiles (static analyses)."""
        findings: list[dict] = []
        if pattern == "":
            findings.append({
                "code": "empty_pattern",
                "message": "the empty pattern matches at every "
                           "position of any input (re.compile('') is "
                           "valid)",
                "span": [0, 0],
                "severity": "info",
            })
            return findings
        root = self._parse_tree(pattern, flag_value)
        nodes = [node for node, _ in self._walk(root)]
        ascii_flag = bool(flag_value & re.ASCII)
        dotall_flag = bool(flag_value & re.DOTALL)

        # Severity-graded ReDoS detection.
        for entry in self._detect_redos(root):
            severity = "warning" if entry["grade"] == "exponential" \
                else "info"
            findings.append({
                "code": entry["code"],
                "message": entry["message"],
                "span": entry["span"],
                "severity": severity,
            })

        shorthand_spans: dict[str, list[list[int]]] = {}
        possessive = False
        nested_set_span: Optional[list[int]] = None
        for node in nodes:
            if node is root:
                continue
            if node.kind == K_CLASS and node.class_info and \
                    node.class_info.get("nested_set") and \
                    nested_set_span is None:
                nested_set_span = [node.start, node.end]
            if node.kind == K_BRACE:
                findings.append({
                    "code": "brace_literal",
                    "message": (
                        f"{node.literal!r} is not a quantifier here — "
                        "Python re compiles it as literal brace "
                        "characters; if a format template like '{name}' "
                        "leaked into the pattern, escape the braces "
                        "({{name}}) or build the pattern differently"
                    ),
                    "span": [node.start, node.end],
                    "severity": "info",
                })
            if node.kind == K_SHORTHAND and not ascii_flag:
                shorthand_spans.setdefault(str(node.literal), []) \
                    .append([node.start, node.end])
            if node.kind == K_ANCHOR and node.literal == "\\b" \
                    and not ascii_flag:
                shorthand_spans.setdefault("b_word", []) \
                    .append([node.start, node.end])
            if node.kind == K_DOT and node.quant is not None \
                    and not dotall_flag:
                shorthand_spans.setdefault("dot", []) \
                    .append([node.start, node.end])
            if node.quant is not None and node.quant["max"] < _MAXREPEAT \
                    and node.quant["max"] > self.huge_repeat_threshold:
                findings.append({
                    "code": "huge_repeat_bound",
                    "message": (
                        f"bounded repetition {{..., {node.quant['max']:,}}} "
                        "compiles, but each match attempt may perform that "
                        "many unit steps — effective work grows with the "
                        "bound (documented heuristic; CPython's MAXREPEAT "
                        f"is {_MAXREPEAT:,}, above which compilation "
                        "raises OverflowError)"
                    ),
                    "span": [node.start, node.quant["span"][1]],
                    "severity": "warning",
                })
            if node.quant is not None and node.quant["kind"] == "possessive":
                possessive = True
            if node.is_group():
                kind_ = node.group.get("kind")
                if kind_ == G_ATOMIC:
                    possessive = True
                if kind_ == G_FLAGS_SCOPED:
                    findings.append({
                        "code": "py311_only_syntax",
                        "message": (
                            "scoped inline flags ((?i:...)) compile on "
                            "Python 3.11+ but not on 3.10 (the "
                            "repository's floor)"
                        ),
                        "span": [node.start, node.end],
                        "severity": "info",
                    })
                if kind_ == G_FLAGS_GLOBAL and node.start == 0:
                    findings.append({
                        "code": "inline_flag_scope",
                        "message": (
                            "global inline flag group "
                            f"(?{node.group.get('flags')}) applies to the "
                            "whole pattern including every later "
                            "alternation branch; a scoped group (?i:...) "
                            "limits the effect but needs Python 3.11+ "
                            "(see py311_only_syntax)"
                        ),
                        "span": [node.start, node.end],
                        "severity": "info",
                    })

        if nested_set_span is not None:
            findings.append({
                "code": "nested_set_possible",
                "message": (
                    "character class contains '[' — CPython emits "
                    "'Possible nested set' and treats it as a literal "
                    "member, but POSIX and many cross-platform engines "
                    "parse nested classes completely differently; write "
                    "the class without the inner brackets"
                ),
                "span": nested_set_span,
                "severity": "warning",
            })
        if possessive:
            findings.append({
                "code": "py311_only_syntax",
                "message": (
                    "possessive quantifiers (a*+) and atomic groups "
                    "((?>...)) compile on Python 3.11+ but raise on 3.10 "
                    "(the repository's floor) — avoid them if the pattern "
                    "must stay 3.10-compatible"
                ),
                "span": [0, len(pattern)],
                "severity": "info",
            })
        unicode_notes = {
            "d": r"\d matches any Unicode decimal digit under str "
                 "semantics (verified on CPython 3.11: Devanagari "
                 "digits match, ① U+2460 does not); use re.ASCII for "
                 "0-9 only",
            "D": r"\D is the complement of the Unicode-wide \d",
            "w": r"\w matches any Unicode word character — verified on "
                 r"CPython 3.11: re.match(r'\w', '①') succeeds and CJK "
                 "matches too; use re.ASCII for [a-zA-Z0-9_] only",
            "W": r"\W is the complement of the Unicode-wide \w",
            "s": r"\s matches Unicode whitespace — verified on CPython "
                 "3.11: NBSP U+00A0 matches; use re.ASCII for "
                 r"' \t\n\r\f\v' only",
            "S": r"\S is the complement of the Unicode-wide \s",
            "b_word": r"\b is Unicode-aware for str patterns: word "
                      "boundaries exist around CJK and other non-ASCII "
                      "letters; use re.ASCII for ASCII-only boundaries",
        }
        for key in sorted(shorthand_spans):
            if key == "dot":
                continue
            findings.append({
                "code": "unicode_class_wide",
                "message": unicode_notes[key],
                "span": shorthand_spans[key][0],
                "severity": "info",
            })
        if shorthand_spans.get("dot"):
            findings.append({
                "code": "dot_not_dotall",
                "message": (
                    "'.' does not match newline unless the DOTALL flag "
                    "(re.S / (?s)) is set — a '.*' across multi-line "
                    "input stops at the first newline"
                ),
                "span": shorthand_spans["dot"][0],
                "severity": "info",
            })

        # Unbounded dot runs that escaped the graded detectors still
        # deserve an untrusted-input note.
        dot_runs = [node for node in nodes
                    if node.kind == K_DOT and self._is_unbounded(node.quant)]
        if dot_runs and not any(f["code"].startswith("redos_")
                                for f in findings):
            findings.append({
                "code": "redos_untrusted_input",
                "message": (
                    f"{len(dot_runs)} unbounded '.*'/'.+' element(s): "
                    "fine for trusted input, but when the matched text "
                    "is untrusted, anchor the pattern and keep "
                    "quantified dot runs bounded — failing searches "
                    "scan every split position"
                ),
                "span": [dot_runs[0].start, dot_runs[0].end],
                "severity": "info",
            })
        return findings

    # ------------------------------------------------------------------ #
    # structure mode
    # ------------------------------------------------------------------ #

    def _run_structure(self, pattern: str, root: _Node,
                       flag_names: list[str], flag_value: int
                       ) -> dict[str, Any]:
        nodes_out: list[dict] = []
        truncated = False
        # Iterative pre-order serialization with the node cap.
        stack: list[tuple[_Node, int]] = [(root, 0)]
        while stack:
            node, depth = stack.pop()
            if len(nodes_out) >= self.max_nodes_out:
                truncated = True
                break
            entry: dict[str, Any] = {
                "type": node.kind,
                "span": [node.start, node.end],
            }
            if node.literal is not None:
                entry["literal"] = node.literal
            if node.class_info is not None:
                entry["class"] = node.class_info
            if node.quant is not None:
                entry["quantifier"] = {
                    "min": node.quant["min"],
                    "max": (None if node.quant["max"] >= _MAXREPEAT
                            else node.quant["max"]),
                    "kind": node.quant["kind"],
                    "span": list(node.quant["span"]),
                }
            if node.is_group():
                entry["group"] = {
                    "kind": node.group.get("kind"),
                    "number": node.group.get("number"),
                    "name": node.group.get("name"),
                }
            nodes_out.append(entry)
            if depth >= self.analysis_depth_cap:
                continue
            children: list[_Node] = []
            for branch in node.branches:
                children.extend(branch)
            for child in reversed(children):
                stack.append((child, depth + 1))

        groups_by_number = self._groups_by_number(root)
        group_map: dict[str, Any] = {}
        group_spans: dict[str, list[int]] = {}
        for number in sorted(groups_by_number):
            node = groups_by_number[number]
            group_map[str(number)] = (
                node.group.get("name")
                if node.group.get("kind") == G_NAMED else None)
            group_spans[str(number)] = [node.start, node.end]

        verdict = self._compile_verdict(pattern, flag_value)
        return {
            "pattern": pattern,
            "flags": flag_names,
            "nodes": nodes_out,
            "node_count": len(nodes_out),
            "truncated": truncated,
            "group_map": group_map,
            "group_spans": group_spans,
            "compiles": not verdict["raises"],
        }

    # ------------------------------------------------------------------ #
    # explain mode
    # ------------------------------------------------------------------ #

    def _run_explain(self, pattern: str, root: _Node) -> dict[str, Any]:
        fragments: list[str] = []
        for index, branch in enumerate(root.branches, start=1):
            pieces = [self._describe(child, 0) for child in branch]
            body = "; then ".join(pieces) if pieces \
                else "match the empty string"
            fragments.append(f"alternative {index}: {body}")
        groups: list[dict] = []
        for node, _ in self._walk(root):
            if not node.is_group() or node.group.get("number") is None:
                continue
            info = node.group
            kind = info.get("kind")
            label = {
                G_CAPTURE: "capturing group",
                G_NAMED: "named capturing group",
                G_NONCAP: "non-capturing group",
                G_LOOKAHEAD_POS: "positive lookahead",
                G_LOOKAHEAD_NEG: "negative lookahead",
                G_LOOKBEHIND_POS: "positive lookbehind",
                G_LOOKBEHIND_NEG: "negative lookbehind",
                G_ATOMIC: "atomic group",
            }.get(kind, kind)
            groups.append({
                "number": info.get("number"),
                "name": info.get("name"),
                "kind": label,
                "span": [node.start, node.end],
            })
        groups.sort(key=lambda g: (g["number"] or 0, g["span"][0]))
        annotations: list[dict] = []
        for node, _ in self._walk(root):
            if node.kind == K_BACKREF and isinstance(node.literal, str):
                ref = node.literal
                numeric = bool(ref) and _ascii_digit_span(ref) == len(ref)
                text_ = (f"backreference to group {int(ref)}"
                         if numeric
                         else f"backreference to {ref}")
                annotations.append({
                    "kind": "backreference",
                    "span": [node.start, node.end],
                    "text": text_,
                })
            elif node.is_group():
                kind = node.group.get("kind")
                if kind in _LOOKAROUND_KINDS:
                    annotations.append({
                        "kind": "lookaround",
                        "span": [node.start, node.end],
                        "text": self._describe(node, 0),
                    })
                elif kind == G_ATOMIC:
                    annotations.append({
                        "kind": "atomic",
                        "span": [node.start, node.end],
                        "text": "atomic group — once matched, never "
                                "re-examined (Python 3.11+)",
                    })
                elif node.kind == K_COND:
                    annotations.append({
                        "kind": "conditional",
                        "span": [node.start, node.end],
                        "text": f"conditional matching on group "
                                f"{node.group.get('name')!r}",
                    })
        annotations.sort(key=lambda a: (a["span"][0], a["span"][1],
                                        a["kind"]))
        return {
            "pattern": pattern,
            "alternatives": fragments,
            "groups": groups,
            "annotations": annotations,
        }

    def _quant_phrase(self, quant: dict) -> str:
        """Deterministic English phrase for one quantifier."""
        qmin, qmax, kind = quant["min"], quant["max"], quant["kind"]
        if qmax >= _MAXREPEAT:
            if qmin == 0:
                shape = "star"
            elif qmin == 1:
                shape = "plus"
            else:
                return f"at least {qmin} times ({kind})"
        elif qmin == 0 and qmax == 1:
            shape = "opt"
        else:
            return f"between {qmin} and {qmax} times ({kind})"
        phrases = {
            ("star", "greedy"): "as many times as possible (greedy)",
            ("star", "lazy"): "as few times as possible (lazy)",
            ("star", "possessive"): "as many times as possible, never "
                                    "giving back (possessive, 3.11+)",
            ("plus", "greedy"): "one or more times, greedily",
            ("plus", "lazy"): "one or more times, lazily",
            ("plus", "possessive"): "one or more times, possessively "
                                    "(3.11+)",
            ("opt", "greedy"): "optionally, preferring to match",
            ("opt", "lazy"): "optionally, preferring to skip",
            ("opt", "possessive"): "optionally, never giving back "
                                   "(3.11+)",
        }
        return phrases.get((shape, kind), f"{shape} ({kind})")

    def _describe(self, node: _Node, depth: int) -> str:
        """Deterministic English description of one node."""
        if depth > 24:
            return "…(deeply nested)…"
        quant_suffix = f" {self._quant_phrase(node.quant)}" \
            if node.quant is not None else ""
        if node.kind == K_LITERAL:
            shown = str(node.literal)
            if len(shown) > 24:
                shown = shown[:21] + "…"
            return f"the text {shown!r}{quant_suffix}"
        if node.kind == K_DOT:
            return f"any single character except newline{quant_suffix}"
        if node.kind == K_CLASS:
            info = node.class_info or {}
            body = self._class_text(info)
            neg = "not " if info.get("negated") else ""
            return f"one {neg}of the characters in {body!r}{quant_suffix}"
        if node.kind == K_SHORTHAND:
            meaning = {
                "d": "a digit (Unicode-wide \\d)",
                "D": "a non-digit",
                "w": "a word character (Unicode-wide \\w)",
                "W": "a non-word character",
                "s": "a whitespace character",
                "S": "a non-whitespace character",
            }.get(str(node.literal), str(node.literal))
            return f"{meaning}{quant_suffix}"
        if node.kind == K_ANCHOR:
            meaning = {
                "^": "start of string (or line under MULTILINE)",
                "$": "end of string (or line under MULTILINE)",
                "\\b": "a word boundary",
                "\\B": "not a word boundary",
                "\\A": "start of string",
                "\\Z": "end of string",
            }.get(str(node.literal), str(node.literal))
            return meaning
        if node.kind == K_BACKREF:
            ref = str(node.literal)
            if ref and _ascii_digit_span(ref) == len(ref):
                target = int(ref)
            else:
                target = ref
            return f"the same text as group {target}{quant_suffix}"
        if node.kind == K_BRACE:
            return f"the literal text {node.literal!r}"
        if node.is_group():
            kind = node.group.get("kind")
            inner_bits = []
            for branch in node.branches:
                inner_bits.append("; then ".join(
                    self._describe(c, depth + 1) for c in branch))
            inner = " OR ".join(inner_bits) if inner_bits else "empty"
            labels = {
                G_CAPTURE: "a capturing group matching",
                G_NAMED: f"a group named {node.group.get('name')!r} "
                         "matching",
                G_NONCAP: "a non-capturing group matching",
                G_LOOKAHEAD_POS: "a lookahead asserting ahead:",
                G_LOOKAHEAD_NEG: "a negative lookahead asserting ahead "
                                 "is NOT:",
                G_LOOKBEHIND_POS: "a lookbehind asserting before:",
                G_LOOKBEHIND_NEG: "a lookbehind asserting before is "
                                  "NOT:",
                G_ATOMIC: "an atomic group matching",
                G_FLAGS_GLOBAL: "a global inline-flag group",
                G_FLAGS_SCOPED: "a scoped inline-flag group matching",
                G_COMMENT: "a comment group",
            }
            label = labels.get(kind, "a group matching")
            number = node.group.get("number")
            prefix = f"group {number}: " if number else ""
            return f"{prefix}{label} ({inner}){quant_suffix}"
        if node.kind == K_COND:
            return (f"a conditional on group {node.group.get('name')!r} "
                    "matching one of two branches")
        return "an element the scanner did not classify"

    @staticmethod
    def _class_text(info: dict) -> str:
        """Reconstruct readable class body from class_info."""
        parts = list(info.get("chars", ()))
        for lo, hi in info.get("ranges", ()):
            parts.append(f"{lo}-{hi}")
        parts.extend(info.get("categories", ()))
        body = "".join(parts)
        return "[^" + body + "]" if info.get("negated") else "[" + body + "]"

    # ------------------------------------------------------------------ #
    # estimate mode
    # ------------------------------------------------------------------ #

    def _run_estimate(self, pattern: str, root: _Node,
                      flag_names: list[str],
                      text_length: int) -> dict[str, Any]:
        redos = self._detect_redos(root)
        codes = {entry["code"] for entry in redos}
        reasons: list[str] = []
        unknown_reason = self._unknown_risk_reason(root)
        if "redos_exponential" in codes:
            risk = "exponential"
            reasons.append(
                "nested quantifier / overlapping-prefix alternation "
                "detected — failing inputs can force exponential "
                "re-partitioning (see lint findings)"
            )
        elif unknown_reason is not None:
            # Static bounds are impossible (quantified backreference
            # or conditional) — unknown outranks a merely polynomial
            # hint, because even the polynomial estimate's premises
            # do not hold there.
            risk = "unknown"
            reasons.append(unknown_reason)
        elif "redos_polynomial" in codes:
            risk = "polynomial"
            reasons.append(
                "adjacent unbounded quantifiers over overlapping text "
                "detected — failing suffixes force quadratic re-splitting"
            )
        else:
            risk = "linear"
            reasons.append(
                "no ambiguous repetition detected by the structural "
                "detectors — a single scan of the input"
            )
        return {
            "pattern": pattern,
            "flags": flag_names,
            "text_length": text_length,
            "basic_ops": self._basic_ops(root, text_length),
            "backtracking_risk_class": risk,
            "reasons": reasons,
            "heuristic": True,
        }

    def _unknown_risk_reason(self, root: _Node) -> Optional[str]:
        """Why the risk class cannot be pinned down statically."""
        quantified_backref = False
        conditional = False
        for node, _ in self._walk(root):
            if node.kind == K_BACKREF and node.quant is not None:
                quantified_backref = True
            if node.kind == K_COND:
                conditional = True
        if quantified_backref:
            return ("a quantified backreference is present — "
                    "backtracking cost depends on capture contents, "
                    "which static analysis cannot bound")
        if conditional:
            return ("a conditional (?(n)…) is present — the taken branch "
                    "depends on earlier captures, so the repetition "
                    "structure is not statically known")
        return None

    def _basic_ops(self, root: _Node, text_length: int) -> int:
        """Scan-work estimate (documented heuristic).

        Every leaf atom costs 1 op per repetition actually performed.
        A bounded quantifier counts its minimum; an unbounded one
        assumes the whole sample input is consumed at the unit's
        minimum width (``max(qmin, text_length // 1, 1)`` — leaf atoms
        consume one character). A sequence sums its children; an
        alternation or group takes the most expensive branch.
        Iterative post-order, depth-capped.
        """
        values: dict[int, int] = {}
        stack: list[tuple[_Node, int]] = [(root, 0)]
        while stack:
            node, phase = stack.pop()
            if phase == 1:
                values[id(node)] = self._eval_ops(node, values, text_length)
                continue
            stack.append((node, 1))
            if len(stack) > 4 * self.analysis_depth_cap:
                values[id(node)] = text_length
                stack.pop()
                continue
            for branch in node.branches:
                for child in reversed(branch):
                    stack.append((child, 0))
        return values.get(id(root), 0)

    def _eval_ops(self, node: _Node, values: dict[int, int],
                  text_length: int) -> int:
        """One node's ops from already-evaluated children."""
        if node.kind in (K_LITERAL, K_CLASS, K_DOT, K_SHORTHAND,
                         K_BACKREF, K_BRACE):
            base = 1
            if node.quant is None:
                return base
            if self._is_unbounded(node.quant):
                return base * max(node.quant["min"], text_length, 1)
            return base * node.quant["min"]
        if node.kind in (K_ANCHOR, K_UNKNOWN):
            return 1
        # Group / conditional / root: most expensive branch.
        branch_ops = []
        for branch in node.branches:
            branch_ops.append(sum(values.get(id(c), 1) for c in branch))
        ops = max(branch_ops) if branch_ops else 0
        if node.quant is not None:
            if self._is_unbounded(node.quant):
                return ops * max(node.quant["min"], text_length, 1)
            return ops * node.quant["min"]
        return ops
