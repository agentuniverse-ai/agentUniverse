#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: regex_explain_tool.py

"""Regex pattern explainer tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration).  The existing ``RegexTool`` (#767) *runs* a pattern —
match / extract / replace / split — but nothing in the framework can
tell an agent *what a pattern means*.  This tool fills that gap: it
tokenises a regular expression and returns a plain-language breakdown
of every token, a one-line summary for simple patterns, and generated
example strings, all without any network access.

Three modes are supported:

* ``explain`` — tokenise the pattern into ``[{token, kind, meaning,
  position, ...}]``.  The supported subset covers literals, ``.``,
  character classes ``[...]`` (with ranges and negation), the escapes
  ``\\d \\w \\s \\D \\W \\S \\b \\B \\n \\t \\r \\f \\v`` and escaped
  literal characters such as ``\\.`` or ``\\\\``, the anchors ``^`` and
  ``$``, groups — capturing ``(...)``, non-capturing ``(?:...)``,
  named ``(?P<name>...)``, positive lookahead ``(?=...)`` and negative
  lookahead ``(?!...)`` — alternation ``|``, the quantifiers ``*``,
  ``+``, ``?``, ``{n}``, ``{n,}``, ``{n,m}`` and ``{,m}`` (each with an
  optional lazy ``?`` suffix) and the inline flags ``(?i)`` ``(?m)``
  ``(?s)``.  Constructs outside this subset (lookbehind, numbered or
  named backreferences, ``\\p`` Unicode classes, ``\\A`` / ``\\Z``,
  scoped flag groups, comments, conditionals, ``\\x`` / ``\\u`` / octal
  escapes, possessive quantifiers such as ``*+``, atomic groups
  ``(?>...)`` and POSIX classes ``[:alpha:]``, ...) are each flagged
  with their position in a structured ``unsupported`` list instead of
  silently mis-explaining them — the subset is documented, and honest
  about its limits.
* ``validate`` — compile check via ``re.compile``.  Compilation
  failures are the *payload* here: the ``re.error`` message, position,
  line and column are returned in a structured ``error`` object.
* ``examples`` — generate two or three strings that match the
  pattern, for *simple* patterns only (literal runs, the class
  shorthands, bracket classes and quantifiers, optionally anchored).
  Every candidate is verified with ``re.fullmatch`` before being
  returned; patterns that use groups, alternation, lookarounds, dot,
  boundaries, inline flags or unsupported constructs get a structured
  note instead of examples.

Input validation is strict and happens before any work: a malformed
``mode`` or ``pattern`` (wrong type, over-long) raises ``ValueError``.
In ``explain`` and ``examples`` mode a pattern that fails to compile
raises ``ValueError`` — *unless* the tokeniser flagged unsupported
constructs whose presence explains the failure (for example ``\\p{L}``
is not valid Python ``re`` syntax at all), in which case the breakdown
is still returned together with the ``compile_error`` details, so an
agent learns *why* the pattern does not compile rather than just that
it does not.

Generation is fully deterministic: example strings are built from
fixed representative characters and repetition counts (minimum /
maximum / middle), never from randomness.
"""

import re
import sys
from typing import Any, Callable, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# Static tables
# ---------------------------------------------------------------------------

# Meanings of the class shorthands, keyed by the letter after the backslash.
_SHORTHAND_MEANINGS: Dict[str, str] = {
    "d": "any digit character (0-9)",
    "D": "any character that is not a digit",
    "w": "any word character (a letter, a digit or an underscore)",
    "W": "any character that is not a word character "
    "(not a letter, digit or underscore)",
    "s": "any whitespace character (space, tab, newline and similar)",
    "S": "any character that is not whitespace",
}

# Plain-language names for characters used in summaries ("a hyphen").
_CHAR_NAMES: Dict[str, str] = {
    ".": "period",
    "-": "hyphen",
    "_": "underscore",
    "@": "at sign",
    "+": "plus sign",
    "/": "slash",
    ":": "colon",
    ",": "comma",
    ";": "semicolon",
    "=": "equals sign",
    "?": "question mark",
    "!": "exclamation mark",
    "#": "hash sign",
    "%": "percent sign",
    "&": "ampersand",
    "*": "asterisk",
    "(": "left parenthesis",
    ")": "right parenthesis",
    "[": "left bracket",
    "]": "right bracket",
    "{": "left brace",
    "}": "right brace",
    "|": "vertical bar",
    "^": "caret",
    "$": "dollar sign",
    "~": "tilde",
    "`": "backtick",
    "'": "apostrophe",
    '"': "double quote",
    "<": "less-than sign",
    ">": "greater-than sign",
    " ": "space",
    "\n": "newline character",
    "\t": "tab character",
    "\r": "carriage return",
}

# Control escapes understood inside and outside character classes.
_CONTROL_ESCAPES: Dict[str, str] = {
    "n": "a newline character",
    "t": "a tab character",
    "r": "a carriage return",
    "f": "a form feed character",
    "v": "a vertical tab character",
}

_CONTROL_CHARS: Dict[str, str] = {
    "n": "\n", "t": "\t", "r": "\r", "f": "\f", "v": "\v",
}

# Summary nouns for the shorthand classes (singular / plural).
_SHORTHAND_NOUNS: Dict[str, Tuple[str, str]] = {
    "d": ("digit", "digits"),
    "D": ("non-digit", "non-digits"),
    "w": ("word character", "word characters"),
    "W": ("non-word character", "non-word characters"),
    "s": ("whitespace character", "whitespace characters"),
    "S": ("non-whitespace character", "non-whitespace characters"),
}

# Deterministic representative characters for example generation.
_SHORTHAND_REPRESENTATIVES: Dict[str, Tuple[str, str, str]] = {
    "d": ("0", "5", "9"),
    "D": ("a", "Z", "!"),
    "w": ("a", "A", "1"),
    "W": (" ", "!", "."),
    "s": (" ", "\t", " "),
    "S": ("a", "Z", "!"),
}

# Characters each shorthand matches, for negated-class candidate checks.
_SHORTHAND_MEMBERS: Dict[str, Tuple[str, ...]] = {
    "d": tuple("0123456789"),
    "w": tuple("aAbBzZ09_"),
    "s": (" ", "\t", "\n"),
}

# Inline flag letters supported (global form only, e.g. (?ims)).
_INLINE_FLAG_MEANINGS: Dict[str, str] = {
    "i": "case-insensitive matching",
    "m": "multiline: '^' and '$' match at line boundaries",
    "s": "dotall: '.' also matches newline",
}

# Fixed candidate order for picking representatives of negated classes.
_NEGATED_CANDIDATES = "aAXqZ9_ !-"

# {n} / {n,} / {n,m} / {,m} quantifier bodies.
_BRACES = re.compile(r"\{(\d+)?(?:,(\d*))?\}")

_POSIX_CLASS_SHAPE = re.compile(r"\[:[a-z]+:\]")

# Python 3.11 started treating "{,m}" as {0,m}; earlier versions keep it
# a literal brace.  Gate the tokenizer on the same behaviour.
_BRACE_COMMA_MIN_SUPPORTED = sys.version_info >= (3, 11)

# Repetition-count guards for example generation.
_MAX_EXTRA_REPEAT = 25  # optional extra repetitions beyond the minimum
_MAX_REQUIRED_REPEAT = 100  # hard cap on exemplifiable required repeats

# Upper bound on the ``pattern`` input length (kept in sync with the
# ``max_pattern_chars`` model field; class-level field access is not
# available on pydantic models, so the validator uses this constant).
_MAX_PATTERN_CHARS = 10_000


class RegexExplainerTool(Tool):
    """Regex pattern explainer built purely on the stdlib ``re`` module.

    Attributes:
        max_pattern_chars (int): Upper bound on the ``pattern`` input
            length; longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "regex_explain_tool"
    description: str = (
        "Regex explainer tool — pure Python stdlib, no network required. "
        "Explains what a regular expression means in plain language: "
        "mode='explain' returns a token-by-token breakdown "
        "[{token, kind, meaning, position}] plus a one-line summary for "
        "simple patterns; mode='validate' compiles the pattern and returns "
        "the re.error message and position on failure; mode='examples' "
        "generates 2-3 verified matching strings for simple patterns "
        "(literals, classes and quantifiers)."
    )

    MODES: ClassVar[tuple] = ("explain", "validate", "examples")

    max_pattern_chars: int = 10_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        pattern: Any = None,
    ) -> Dict[str, Any]:
        """Explain, validate or exemplify one regular expression.

        Args:
            mode (str): One of ``explain`` / ``validate`` / ``examples``.
            pattern (str): The regular expression pattern to process.
                The empty string is a valid (compiling) pattern and is
                accepted in every mode.

        Returns:
            Dict[str, Any]: For ``validate`` always a payload whose
                ``valid`` flag reflects the compile check and whose
                ``error`` object carries the ``re.error`` message /
                position / line / column on failure.  For ``explain``
                and ``examples`` a payload with the token breakdown,
                the ``unsupported`` construct list, the summary (or the
                note explaining its omission), the generated example
                strings (or the note explaining why none were
                generated), and — only when the pattern fails to
                compile because of constructs outside the supported
                subset — the ``compile_error`` details.

        Raises:
            ValueError: If ``mode`` or ``pattern`` is malformed, or if
                (in ``explain`` / ``examples`` mode) the pattern fails
                to compile for reasons other than unsupported-construct
                usage.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_pattern = self._validate_pattern(pattern)

        if mode == "validate":
            return self._run_validate(clean_pattern)

        tokens, unsupported = self._tokenize(clean_pattern)
        compile_error = self._try_compile(clean_pattern)
        if compile_error is not None and not unsupported:
            self._invalid(
                f"pattern does not compile: {compile_error['message']} "
                f"(use mode='validate' to inspect the error)"
            )
        if mode == "explain":
            return self._run_explain(clean_pattern, tokens, unsupported,
                                     compile_error)
        return self._run_examples(clean_pattern, tokens, unsupported)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"regex_explain_tool: {message}")

    @classmethod
    def _validate_pattern(cls, pattern: Any) -> str:
        """Validate the ``pattern`` input."""
        if (
            pattern is None
            or isinstance(pattern, bool)
            or not isinstance(pattern, str)
        ):
            cls._invalid(f"pattern must be a string (got {pattern!r})")
        if len(pattern) > _MAX_PATTERN_CHARS:
            cls._invalid(
                f"pattern exceeds the {_MAX_PATTERN_CHARS:,}-character "
                f"limit (got {len(pattern):,} characters)"
            )
        return pattern

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _try_compile(cls, pattern: str) -> Optional[Dict[str, Any]]:
        """Compile the pattern; return ``None`` or the error details."""
        try:
            re.compile(pattern)
        except re.error as exc:
            return {
                "message": str(exc),
                "position": getattr(exc, "pos", None),
                "lineno": getattr(exc, "lineno", None),
                "colno": getattr(exc, "colno", None),
            }
        return None

    def _run_validate(self, pattern: str) -> Dict[str, Any]:
        """Compile check; the compile error is the payload, not an error."""
        context = {"mode": "validate", "pattern": pattern}
        error = self._try_compile(pattern)
        if error is None:
            return {
                **context,
                "valid": True,
                "result": "valid",
                "error": None,
            }
        return {
            **context,
            "valid": False,
            "result": f"invalid: {error['message']}",
            "error": error,
        }

    # ------------------------------------------------------------------ #
    # Tokenizer — the heart of the explain mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _tokenize(
        cls, pattern: str
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Scan ``pattern`` into explanation tokens plus unsupported flags."""
        tokens: List[Dict[str, Any]] = []
        unsupported: List[Dict[str, Any]] = []

        def flag(construct: str, position: int, message: str) -> None:
            unsupported.append(
                {"construct": construct, "position": position,
                 "message": message}
            )

        i = 0
        length = len(pattern)
        while i < length:
            char = pattern[i]
            if char == "\\":
                i = cls._scan_escape(pattern, i, tokens, flag)
            elif char == "[":
                i = cls._scan_class(pattern, i, tokens, flag)
            elif char == "(":
                i = cls._scan_group(pattern, i, tokens, flag)
            elif char == ")":
                tokens.append({
                    "token": ")",
                    "kind": "group_close",
                    "meaning": "end of the innermost currently open group",
                    "position": i,
                })
                i += 1
            elif char == "|":
                tokens.append({
                    "token": "|",
                    "kind": "alternation",
                    "meaning": "alternation — the pattern matches the part "
                    "before or the part after this marker",
                    "position": i,
                })
                i += 1
            elif char == ".":
                tokens.append({
                    "token": ".",
                    "kind": "dot",
                    "meaning": "any character except a newline (any "
                    "character at all with the dotall flag)",
                    "position": i,
                })
                i += 1
            elif char == "^":
                tokens.append({
                    "token": "^",
                    "kind": "anchor",
                    "meaning": "anchor — the start of the string (or the "
                    "start of a line with the multiline flag)",
                    "position": i,
                })
                i += 1
            elif char == "$":
                tokens.append({
                    "token": "$",
                    "kind": "anchor",
                    "meaning": "anchor — the end of the string (or the end "
                    "of a line with the multiline flag)",
                    "position": i,
                })
                i += 1
            elif char in "*+?":
                if char == "+" and tokens \
                        and tokens[-1]["kind"] == "quantifier":
                    i = cls._flag_possessive(pattern, i, tokens, flag)
                else:
                    i = cls._scan_quantifier(pattern, i, tokens)
                    i = cls._skip_lazy(pattern, i, tokens)
            elif char == "{":
                i = cls._scan_braces(pattern, i, tokens)
                i = cls._skip_lazy(pattern, i, tokens)
            else:
                tokens.append({
                    "token": char,
                    "kind": "literal",
                    "meaning": f"the literal character '{char}'",
                    "position": i,
                    "char": char,
                })
                i += 1
        return tokens, unsupported

    # ------------------------------------------------------------------ #
    # Tokenizer pieces
    # ------------------------------------------------------------------ #

    @classmethod
    def _scan_escape(
        cls,
        pattern: str,
        i: int,
        tokens: List[Dict[str, Any]],
        flag: Callable[[str, int, str], None],
    ) -> int:
        """Scan one escape sequence starting at ``pattern[i] == '\\\\'``."""
        start = i
        i += 1
        if i >= len(pattern):
            # Trailing backslash: not a listed unsupported construct, so
            # leave it as a plain token; the compile check rejects it.
            tokens.append({
                "token": "\\",
                "kind": "literal",
                "meaning": "the literal character '\\' (trailing "
                "backslash)",
                "position": start,
                "char": "\\",
            })
            return i
        letter = pattern[i]
        if letter in _SHORTHAND_MEANINGS:
            tokens.append({
                "token": f"\\{letter}",
                "kind": "shorthand",
                "meaning": _SHORTHAND_MEANINGS[letter],
                "position": start,
                "which": letter,
            })
            return i + 1
        if letter in ("b", "B"):
            meaning = (
                "a word boundary (a position between a word character and "
                "a non-word character)"
                if letter == "b"
                else "a position that is not a word boundary"
            )
            tokens.append({
                "token": f"\\{letter}",
                "kind": "boundary",
                "meaning": meaning,
                "position": start,
            })
            return i + 1
        if letter in _CONTROL_ESCAPES:
            tokens.append({
                "token": f"\\{letter}",
                "kind": "literal",
                "meaning": _CONTROL_ESCAPES[letter],
                "position": start,
                "char": _CONTROL_CHARS[letter],
            })
            return i + 1
        if not letter.isalnum():
            tokens.append({
                "token": f"\\{letter}",
                "kind": "literal",
                "meaning": f"the literal character '{letter}'",
                "position": start,
                "char": letter,
            })
            return i + 1
        # Alphanumeric escapes outside the supported subset.
        if letter.isdigit():
            if letter == "0":
                message = ("octal character escape \\0 — outside the "
                           "supported subset")
            else:
                message = (f"backreference \\{letter} — outside the "
                           "supported subset")
        elif letter == "p":
            message = ("Unicode property class \\p — outside the supported "
                       "subset (Python 're' does not support \\p at all)")
        elif letter in ("A", "Z"):
            message = (f"anchor \\{letter} (absolute "
                       f"{'start' if letter == 'A' else 'end'} of string) — "
                       "outside the supported subset")
        elif letter == "g":
            message = ("backreference escape \\g<...> — outside the "
                       "supported subset")
        else:
            message = f"escape \\{letter} — outside the supported subset"
        tokens.append({
            "token": f"\\{letter}",
            "kind": "unsupported",
            "meaning": message,
            "position": start,
        })
        flag(f"\\{letter}", start, message)
        return i + 1

    @classmethod
    def _scan_class(
        cls,
        pattern: str,
        i: int,
        tokens: List[Dict[str, Any]],
        flag: Callable[[str, int, str], None],
    ) -> int:
        """Scan a bracket character class starting at ``pattern[i] == '['``."""
        start = i
        i += 1
        negated = False
        if i < len(pattern) and pattern[i] == "^":
            negated = True
            i += 1
        items: List[Dict[str, Any]] = []
        first = True
        closed = False
        while i < len(pattern):
            char = pattern[i]
            if char == "]" and not first:
                closed = True
                i += 1
                break
            first = False
            if char == "\\" and i + 1 < len(pattern):
                letter = pattern[i + 1]
                if letter in ("d", "w", "s"):
                    items.append({"type": "shorthand", "value": letter})
                    i += 2
                    continue
                if letter in _CONTROL_ESCAPES:
                    items.append({
                        "type": "char",
                        "value": _CONTROL_CHARS[letter],
                    })
                    i += 2
                    continue
                if letter.isalnum():
                    message = (f"escape \\{letter} inside a character "
                               "class — outside the supported subset")
                    items.append({"type": "unsupported",
                                  "value": f"\\{letter}"})
                    flag(f"\\{letter}", i, message)
                    i += 2
                    continue
                # Escaped punctuation: \] \- \\ etc.
                items.append({"type": "char", "value": letter})
                i += 2
                continue
            # Range "x-y" between two plain characters.
            if (
                char != "\\"
                and i + 2 < len(pattern)
                and pattern[i + 1] == "-"
                and pattern[i + 2] not in ("]", "\\")
            ):
                items.append({"type": "range", "start": char,
                              "end": pattern[i + 2]})
                i += 3
                continue
            items.append({"type": "char", "value": char})
            i += 1
        rendered = cls._render_class_items(items)
        prefix = "any character NOT in:" if negated else "any character in:"
        if closed:
            meaning = f"{prefix} {rendered}"
        else:
            meaning = f"unterminated character class — {prefix} {rendered}"
        text = pattern[start:i]
        posix = _POSIX_CLASS_SHAPE.search(text)
        if posix is not None:
            message = (
                f"POSIX character class {posix.group(0)} — outside the "
                "supported subset (Python 're' does not support POSIX "
                "classes; the brackets are matched as literal characters)"
            )
            flag(posix.group(0), start + posix.start(), message)
        tokens.append({
            "token": text,
            "kind": "char_class",
            "meaning": meaning,
            "position": start,
            "negated": negated,
            "items": items,
        })
        return i

    @classmethod
    def _render_class_items(cls, items: List[Dict[str, Any]]) -> str:
        """Render class items as a human-readable list."""
        shorthand_names = {"d": "digits", "w": "word characters",
                           "s": "whitespace"}
        parts: List[str] = []
        for item in items:
            if item["type"] == "char":
                parts.append(f"'{item['value']}'")
            elif item["type"] == "range":
                parts.append(f"'{item['start']}' to '{item['end']}'")
            elif item["type"] == "shorthand":
                parts.append(shorthand_names[item["value"]])
            else:
                parts.append(item["value"])
        return ", ".join(parts)

    @classmethod
    def _scan_group(
        cls,
        pattern: str,
        i: int,
        tokens: List[Dict[str, Any]],
        flag: Callable[[str, int, str], None],
    ) -> int:
        """Scan a group opener starting at ``pattern[i] == '('``."""
        start = i
        rest = pattern[i:]

        def emit(token: str, style: str, meaning: str) -> int:
            tokens.append({
                "token": token,
                "kind": "group_open",
                "meaning": meaning,
                "position": start,
                "style": style,
            })
            return i + len(token)

        if rest.startswith("(?:"):
            return emit(
                "(?:", "non_capturing",
                "start of a non-capturing group (grouping only, the "
                "matched text is not kept)",
            )
        if rest.startswith("(?P<"):
            end = pattern.find(">", i)
            if end == -1:
                token = pattern[i:]
                message = ("named group is missing its closing '>' — "
                           "outside the supported subset")
                flag(token, start, message)
                tokens.append({"token": token, "kind": "unsupported",
                               "meaning": message, "position": start})
                return len(pattern)
            name = pattern[i + 4:end]
            token = pattern[i:end + 1]
            tokens.append({
                "token": token,
                "kind": "group_open",
                "meaning": f"start of a named capturing group '{name}' "
                "(the matched text is kept under that name)",
                "position": start,
                "style": "named",
                "name": name,
            })
            return i + len(token)
        if rest.startswith("(?P="):
            end = pattern.find(")", i)
            token = pattern[i:end + 1] if end != -1 else pattern[i:]
            message = ("named backreference (?P=name) — outside the "
                       "supported subset")
            flag(token, start, message)
            tokens.append({"token": token, "kind": "unsupported",
                           "meaning": message, "position": start})
            return i + len(token)
        if rest.startswith("(?="):
            return emit(
                "(?=", "lookahead_positive",
                "start of a positive lookahead (the enclosed pattern must "
                "match here, without consuming input)",
            )
        if rest.startswith("(?!"):
            return emit(
                "(?!", "lookahead_negative",
                "start of a negative lookahead (the enclosed pattern must "
                "NOT match here, without consuming input)",
            )
        if rest.startswith("(?<=") or rest.startswith("(?<!"):
            is_positive = rest.startswith("(?<=")
            token = "(?<=" if is_positive else "(?<!"
            message = (
                "positive lookbehind assertion (?<=...) — outside the "
                "supported subset"
                if is_positive
                else "negative lookbehind assertion (?<!...) — outside "
                "the supported subset"
            )
            flag(token, start, message)
            tokens.append({"token": token, "kind": "unsupported",
                           "meaning": message, "position": start})
            return i + len(token)
        if rest.startswith("(?>"):
            message = ("atomic group (?>...) — outside the supported "
                       "subset")
            flag("(?>", start, message)
            tokens.append({"token": "(?>", "kind": "unsupported",
                           "meaning": message, "position": start})
            return i + 3
        if rest.startswith("(?#"):
            end = pattern.find(")", i)
            token = pattern[i:end + 1] if end != -1 else pattern[i:]
            message = "comment group (?#...) — outside the supported subset"
            flag(token, start, message)
            tokens.append({"token": token, "kind": "unsupported",
                           "meaning": message, "position": start})
            return i + len(token)
        if rest.startswith("(?("):
            message = ("conditional group (?(id)yes|no) — outside the "
                       "supported subset")
            flag("(?(", start, message)
            tokens.append({"token": "(?(", "kind": "unsupported",
                           "meaning": message, "position": start})
            return i + 3
        if rest.startswith("(?"):
            # Inline flags: global (?ims) is supported; scoped (?i:...)
            # and any other letters are flagged as unsupported.
            j = i + 2
            while j < len(pattern) and pattern[j] in "ims":
                j += 1
            if j > i + 2 and j < len(pattern) and pattern[j] == ")":
                flag_letters = pattern[i + 2:j]
                meanings = "; ".join(
                    _INLINE_FLAG_MEANINGS[c] for c in flag_letters
                )
                tokens.append({
                    "token": pattern[i:j + 1],
                    "kind": "flag",
                    "meaning": f"inline flag — {meanings}",
                    "position": start,
                    "flags": flag_letters,
                })
                return j + 1
            if j > i + 2 and j < len(pattern) and pattern[j] == ":":
                token = pattern[i:j + 1]
                message = ("scoped inline flags (?i:...) — outside the "
                           "supported subset")
                flag(token, start, message)
                tokens.append({"token": token, "kind": "unsupported",
                               "meaning": message, "position": start})
                return j + 1
            stop = min(j + 1, len(pattern)) if j > i + 2 else i + 2
            token = pattern[i:stop]
            message = ("unsupported group syntax (?...) — outside the "
                       "supported subset")
            flag(token, start, message)
            tokens.append({"token": token, "kind": "unsupported",
                           "meaning": message, "position": start})
            return stop
        return emit(
            "(", "capturing",
            "start of a capturing group (the matched text is kept for "
            "backreferences)",
        )

    @classmethod
    def _flag_possessive(
        cls,
        pattern: str,
        i: int,
        tokens: List[Dict[str, Any]],
        flag: Callable[[str, int, str], None],
    ) -> int:
        """Flag a possessive ``+`` suffix at ``pattern[i]``."""
        message = ("possessive quantifier '+' — matches like the greedy "
                   "quantifier but never gives up what it matched — "
                   "outside the supported subset")
        flag("+", i, message)
        tokens.append({
            "token": "+",
            "kind": "unsupported",
            "meaning": message,
            "position": i,
        })
        return i + 1

    @classmethod
    def _scan_quantifier(
        cls, pattern: str, i: int, tokens: List[Dict[str, Any]]
    ) -> int:
        """Scan ``*`` / ``+`` / ``?`` at ``pattern[i]``."""
        char = pattern[i]
        minimum, maximum, meaning = {
            "*": (0, None,
                  "zero or more repetitions of the previous element "
                  "(greedy)"),
            "+": (1, None,
                  "one or more repetitions of the previous element "
                  "(greedy)"),
            "?": (0, 1,
                  "zero or one repetition of the previous element "
                  "(greedy)"),
        }[char]
        tokens.append({
            "token": char,
            "kind": "quantifier",
            "meaning": meaning,
            "position": i,
            "min": minimum,
            "max": maximum,
            "lazy": False,
        })
        return i + 1

    @classmethod
    def _scan_braces(
        cls, pattern: str, i: int, tokens: List[Dict[str, Any]]
    ) -> int:
        """Scan a ``{n}`` / ``{n,}`` / ``{n,m}`` / ``{,m}`` quantifier."""
        match = _BRACES.match(pattern, i)
        body = match.group(0) if match else None
        low_raw = match.group(1) if match else None
        high_raw = match.group(2) if match else None
        # "{,m}" only quantifies on Python >= 3.11; otherwise literal.
        if body is None or (low_raw is None
                            and not _BRACE_COMMA_MIN_SUPPORTED):
            tokens.append({
                "token": "{",
                "kind": "literal",
                "meaning": "the literal character '{'",
                "position": i,
                "char": "{",
            })
            return i + 1
        minimum = int(low_raw) if low_raw is not None else 0
        if high_raw is None and "," not in body:
            maximum: Optional[int] = minimum
            meaning = (f"exactly {minimum} repetitions of the previous "
                       "element")
        elif high_raw in (None, ""):
            maximum = None
            meaning = (f"{minimum} or more repetitions of the previous "
                       "element (greedy)")
        else:
            maximum = int(high_raw)
            meaning = (f"between {minimum} and {maximum} repetitions of "
                       "the previous element (greedy)")
        tokens.append({
            "token": body,
            "kind": "quantifier",
            "meaning": meaning,
            "position": i,
            "min": minimum,
            "max": maximum,
            "lazy": False,
        })
        return match.end()

    @classmethod
    def _skip_lazy(
        cls, pattern: str, i: int, tokens: List[Dict[str, Any]]
    ) -> int:
        """Fold a lazy ``?`` suffix into the previous quantifier token."""
        if i < len(pattern) and pattern[i] == "?":
            previous = tokens[-1] if tokens else None
            if previous is not None and previous["kind"] == "quantifier":
                previous["token"] += "?"
                previous["lazy"] = True
                previous["meaning"] = (
                    previous["meaning"].replace(" (greedy)", "")
                    + " — lazy: matches as few repetitions as possible"
                )
                return i + 1
            # A bare '?' here is itself a quantifier (e.g. after '{').
            return cls._scan_quantifier(pattern, i, tokens)
        return i

    # ------------------------------------------------------------------ #
    # explain mode payload
    # ------------------------------------------------------------------ #

    @classmethod
    def _run_explain(
        cls,
        pattern: str,
        tokens: List[Dict[str, Any]],
        unsupported: List[Dict[str, Any]],
        compile_error: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        summary, summary_note = cls._summarize(tokens)
        return {
            "mode": "explain",
            "pattern": pattern,
            "valid": compile_error is None,
            "tokens": tokens,
            "unsupported": unsupported,
            "summary": summary,
            "summary_note": summary_note,
            "compile_error": compile_error,
        }

    # ------------------------------------------------------------------ #
    # Summary generation (simple patterns only)
    # ------------------------------------------------------------------ #

    @classmethod
    def _summarize(
        cls, tokens: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], Optional[str]]:
        """One-line plain-English summary, or ``None`` plus a note."""
        if not tokens:
            return ("the empty pattern — matches any string (including "
                    "the empty string)", None)

        omit_reason = cls._summary_blocker(tokens)
        if omit_reason is not None:
            return None, f"summary omitted: {omit_reason}"

        leading_anchor = tokens[0]["kind"] == "anchor" \
            and tokens[0]["token"] == "^"
        trailing_anchor = tokens[-1]["kind"] == "anchor" \
            and tokens[-1]["token"] == "$"
        body = tokens[1 if leading_anchor else 0:
                      len(tokens) - 1 if trailing_anchor else len(tokens)]
        if not body:
            return ("matches only the empty string", None)

        # Group literal characters that are not individually quantified
        # into runs; a literal directly followed by a quantifier stays
        # separate because the quantifier binds to it alone.  Escaped
        # literals (\n, \., ...) never merge into runs so each keeps a
        # clear phrase of its own.
        elements: List[Tuple[str, Any, Optional[Dict[str, Any]]]] = []
        literal_run = ""
        for index, token in enumerate(body):
            following = body[index + 1] if index + 1 < len(body) else None
            following_quant = following is not None \
                and following["kind"] == "quantifier"
            if token["kind"] == "literal":
                plain = len(token["token"]) == 1
                if plain and following is not None \
                        and following["kind"] == "literal":
                    literal_run += token["char"]
                    continue
                if following_quant:
                    if literal_run:
                        elements.append(("run", literal_run, None))
                        literal_run = ""
                    elements.append(("atom", token, following))
                    continue
                if plain:
                    literal_run += token["char"]
                    continue
                if literal_run:
                    elements.append(("run", literal_run, None))
                    literal_run = ""
                elements.append(("atom", token, None))
                continue
            if literal_run:
                elements.append(("run", literal_run, None))
                literal_run = ""
            if token["kind"] == "quantifier":
                continue
            if token["kind"] == "shorthand":
                elements.append(("atom", token,
                                 following if following_quant else None))
        if literal_run:
            elements.append(("run", literal_run, None))

        phrases: List[str] = []
        for kind, payload, quant in elements:
            if kind == "run":
                phrases.append(cls._phrase_run(payload))
            elif payload["kind"] == "literal":
                phrases.append(cls._phrase_quantified_literal(
                    payload["char"], quant))
            else:
                noun, noun_plural = _SHORTHAND_NOUNS[payload["which"]]
                if quant is None:
                    phrases.append(f"{cls._article(noun)} {noun}")
                else:
                    phrases.append(cls._phrase_quantified_noun(
                        noun, noun_plural, quant))
        summary = ", ".join(phrases)
        if leading_anchor and trailing_anchor:
            summary += ", anchored"
        elif leading_anchor:
            summary += ", anchored at the start"
        elif trailing_anchor:
            summary += ", anchored at the end"
        return summary, None

    @classmethod
    def _summary_blocker(
        cls, tokens: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Return why the pattern is not summary-eligible, or ``None``."""
        for index, token in enumerate(tokens):
            kind = token["kind"]
            if kind in ("literal", "shorthand", "quantifier"):
                continue
            if kind == "anchor":
                if token["token"] == "^" and index == 0:
                    continue
                if token["token"] == "$" and index == len(tokens) - 1:
                    continue
                return ("anchors are only summarised at the very start "
                        "('^') or very end ('$') of a pattern")
            reasons = {
                "dot": "the any-character dot '.'",
                "char_class": "bracket character classes '[...]'",
                "boundary": "word boundaries",
                "group_open": "groups",
                "group_close": "groups",
                "alternation": "alternation '|'",
                "flag": "inline flags",
                "unsupported": "constructs outside the supported subset",
            }
            reason = reasons.get(kind, f"'{token['token']}'")
            return (f"the summary covers only literals, the class "
                    f"shorthands (\\d \\w \\s and their negations) and "
                    f"quantifiers; this pattern uses {reason}")
        return None

    @classmethod
    def _article(cls, word: str) -> str:
        """Return the indefinite article for a noun ("a" / "an")."""
        return "an" if word[:1].lower() in "aeiou" else "a"

    @classmethod
    def _phrase_run(cls, run: str) -> str:
        if len(run) == 1:
            name = _CHAR_NAMES.get(run)
            if name:
                return f"{cls._article(name)} {name}"
            return f"the character '{run}'"
        return f"the text '{run}'"

    @classmethod
    def _phrase_quantified_literal(
        cls, char: str, quant: Optional[Dict[str, Any]]
    ) -> str:
        if quant is None:
            return cls._phrase_run(char)
        name = _CHAR_NAMES.get(char)
        if name is None:
            return cls._phrase_quantified_noun(
                f"'{char}' character", f"'{char}' characters", quant)
        return cls._phrase_quantified_noun(name, f"{name}s", quant)

    @classmethod
    def _phrase_quantified_noun(
        cls, noun: str, noun_plural: str, quant: Dict[str, Any]
    ) -> str:
        minimum = quant["min"]
        maximum = quant["max"]
        lazy = " (lazy)" if quant["lazy"] else ""
        if maximum == minimum:
            if minimum == 1:
                return f"1 {noun}{lazy}"
            return f"{minimum} {noun_plural}{lazy}"
        if maximum is None:
            if minimum == 0:
                return f"zero or more {noun_plural}{lazy}"
            if minimum == 1:
                return f"one or more {noun_plural}{lazy}"
            return f"{minimum} or more {noun_plural}{lazy}"
        if minimum == 0 and maximum == 1:
            return f"an optional {noun}{lazy}"
        if minimum == 0:
            return f"up to {maximum} {noun_plural}{lazy}"
        return f"{minimum} to {maximum} {noun_plural}{lazy}"

    # ------------------------------------------------------------------ #
    # examples mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _run_examples(
        cls,
        pattern: str,
        tokens: List[Dict[str, Any]],
        unsupported: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        context = {"mode": "examples", "pattern": pattern}
        if unsupported:
            return {
                **context,
                "examples": [],
                "note": ("examples are generated only for simple patterns "
                         "built from literals, the class shorthands, "
                         "bracket character classes and quantifiers; this "
                         "pattern uses constructs outside the supported "
                         "subset"),
            }
        blocker = cls._examples_blocker(tokens)
        if blocker is not None:
            return {**context, "examples": [], "note": blocker}
        atoms = cls._atom_tiers(tokens)
        for _, _, quant in atoms:
            if quant is not None and quant["min"] > _MAX_REQUIRED_REPEAT:
                return {
                    **context,
                    "examples": [],
                    "note": ("examples are not generated when a required "
                             f"repetition count exceeds "
                             f"{_MAX_REQUIRED_REPEAT}"),
                }
        compiled = re.compile(pattern)
        verified: List[str] = []
        for candidate in cls._candidate_strings(atoms):
            if candidate not in verified and compiled.fullmatch(candidate):
                verified.append(candidate)
            if len(verified) == 3:
                break
        if not verified:
            return {
                **context,
                "examples": [],
                "note": ("no example string could be generated and "
                         "verified against this pattern"),
            }
        return {**context, "examples": verified, "note": None}

    @classmethod
    def _examples_blocker(
        cls, tokens: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Return why examples cannot be generated, or ``None``."""
        for token in tokens:
            kind = token["kind"]
            if kind in ("literal", "shorthand", "char_class", "quantifier",
                        "anchor"):
                continue
            reasons = {
                "dot": "the any-character dot '.'",
                "boundary": "word boundaries",
                "group_open": "groups",
                "group_close": "groups",
                "alternation": "alternation '|'",
                "flag": "inline flags",
                "unsupported": "constructs outside the supported subset",
            }
            reason = reasons.get(kind, f"'{token['token']}'")
            return (f"examples are generated only for simple patterns "
                    f"built from literals, the class shorthands, bracket "
                    f"character classes and quantifiers; this pattern "
                    f"uses {reason}")
        return None

    @classmethod
    def _atom_tiers(
        cls, tokens: List[Dict[str, Any]]
    ) -> List[Tuple[str, Any, Optional[Dict[str, Any]]]]:
        """Reduce tokens to ``(atom_kind, atom, quantifier)`` triples."""
        atoms: List[Tuple[str, Any, Optional[Dict[str, Any]]]] = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            quant: Optional[Dict[str, Any]] = None
            if index + 1 < len(tokens) \
                    and tokens[index + 1]["kind"] == "quantifier":
                quant = tokens[index + 1]
                index += 2
            else:
                index += 1
            if token["kind"] == "literal":
                atoms.append(("literal", token["char"], quant))
            elif token["kind"] == "shorthand":
                atoms.append(("shorthand", token["which"], quant))
            elif token["kind"] == "char_class":
                atoms.append(("class", token, quant))
        return atoms

    @classmethod
    def _class_tiers(cls, class_token: Dict[str, Any]) -> List[str]:
        """Three deterministic representative characters for a class."""
        if class_token.get("negated"):
            positive: List[str] = []
            for item in class_token["items"]:
                if item["type"] == "char":
                    positive.append(item["value"])
                elif item["type"] == "range":
                    start, end = ord(item["start"]), ord(item["end"])
                    positive.extend(
                        chr(code) for code in range(start, end + 1)
                        if code < 0x2100
                    )
                elif item["type"] == "shorthand":
                    positive.extend(_SHORTHAND_MEMBERS[item["value"]])
                    positive.extend(
                        _SHORTHAND_REPRESENTATIVES[item["value"]])
            found: List[str] = []
            for candidate in _NEGATED_CANDIDATES:
                if candidate not in positive and candidate not in found:
                    found.append(candidate)
                if len(found) == 3:
                    break
            while len(found) < 3:
                found.append(found[-1] if found else "a")
            return found
        candidates: List[str] = []
        for item in class_token["items"]:
            if item["type"] == "char":
                candidates.append(item["value"])
            elif item["type"] == "range":
                start, end = ord(item["start"]), ord(item["end"])
                candidates.append(chr(start))
                if end > start:
                    candidates.append(chr((start + end) // 2))
                    candidates.append(chr(end))
                else:
                    candidates.extend([item["start"], item["start"]])
            elif item["type"] == "shorthand":
                candidates.extend(
                    _SHORTHAND_REPRESENTATIVES[item["value"]])
        if not candidates:
            candidates = ["a", "a", "a"]
        return [
            candidates[0],
            candidates[1] if len(candidates) > 1 else candidates[0],
            candidates[-1] if len(candidates) > 1 else candidates[0],
        ]

    @classmethod
    def _repetition_tiers(
        cls, quant: Optional[Dict[str, Any]]
    ) -> Tuple[int, int, int]:
        """(minimum, upper, middle) repetition counts for one atom."""
        if quant is None:
            return (1, 1, 1)
        minimum = quant["min"]
        maximum = quant["max"]
        if maximum == minimum:  # {n}
            return (minimum, minimum, minimum)
        if maximum is None:  # * + {n,}
            top = minimum + 1 if minimum < _MAX_EXTRA_REPEAT else minimum
            return (minimum, top, minimum)
        # Bounded range {n,m} / {,m}: keep the upper sample close to the
        # minimum so examples stay short but still vary.
        top = maximum if maximum - minimum <= _MAX_EXTRA_REPEAT \
            else minimum + _MAX_EXTRA_REPEAT
        middle = (minimum + top) // 2
        return (minimum, top, middle)

    @classmethod
    def _candidate_strings(
        cls, atoms: List[Tuple[str, Any, Optional[Dict[str, Any]]]]
    ) -> List[str]:
        """Build up to three deterministic candidate strings."""
        unique: List[str] = []
        for tier in (0, 1, 2):
            pieces: List[str] = []
            for atom_kind, atom, quant in atoms:
                if atom_kind == "literal":
                    chars = [atom, atom, atom]
                elif atom_kind == "shorthand":
                    chars = list(_SHORTHAND_REPRESENTATIVES[atom])
                else:
                    chars = cls._class_tiers(atom)
                count = cls._repetition_tiers(quant)[tier]
                pieces.append(chars[tier] * count)
            candidate = "".join(pieces)
            if candidate not in unique:
                unique.append(candidate)
        return unique
