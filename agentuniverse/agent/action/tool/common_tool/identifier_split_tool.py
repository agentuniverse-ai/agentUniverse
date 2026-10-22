#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: identifier_split_tool.py

"""Code identifier word extraction tool — the inverse of case conversion.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency identifier tokenizer.
Search and matching over code symbols needs the *words* inside an
identifier — ``getHTTPResponseCode`` should surface a query for
"response" — but a case converter only maps one identifier to another.
This tool extracts the word list (acronyms intact), so an agent can
build a searchable vocabulary out of symbol lists before any retrieval
step. It complements ``CaseConverterTool``: that tool CONVERTS between
case styles, this tool splits an identifier INTO words and re-joins a
word list back into a chosen style.

Four modes, all built purely on the standard library:

* ``split`` — identifier (string) → ``words`` list plus the detected
  style (``camel`` / ``pascal`` / ``snake`` / ``kebab`` /
  ``screaming_snake`` / ``mixed``). The exact ruleset, applied left to
  right after separator handling:

  Separators — runs of ``_`` and ``-`` are separators and never appear
  inside a word, with two preservation rules: a LEADING separator run
  stays attached to the first word (``_private_value`` →
  ``["_private", "value"]``) and a TRAILING run stays attached to the
  last word (``value_`` → ``["value_"]``), so Python privacy and dunder
  markers survive a round-trip. Every interior run — single or doubled
  — is a plain separator (``foo__bar`` → ``["foo", "bar"]``).

  Within a separator-free token the characters form maximal runs of
  lowercase, UPPERCASE or digits; boundaries between adjacent runs:

  - lowercase → UPPERCASE: SPLIT (``getHTTP`` → ``get|HTTP``).
  - UPPERCASE run of length >= 2 → lowercase: SPLIT BEFORE THE LAST
    UPPERCASE letter — the uppercase run is kept whole as an acronym
    and its last letter starts the capitalized word that follows
    (``HTTPServer`` → ``HTTP|Server``, ``XMLHttpRequest`` →
    ``XML|Http|Request``).
  - single UPPERCASE → lowercase: MERGE (a capitalized word:
    ``Server``).
  - letter run (any case) → digits: MERGE — a digit run attaches to
    the preceding letter run (``base64`` → ``["base64"]`` not
    ``["base", "64"]``; ``SHA256`` → ``["SHA256"]``; ``utf8`` →
    ``["utf8"]``).
  - digits → UPPERCASE: SPLIT — digits start a new word before a
    following uppercase letter (``utf8Decode`` → ``["utf8",
    "Decode"]``, ``HTTP2Server`` → ``["HTTP2", "Server"]``,
    ``SHA256Hash`` → ``["SHA256", "Hash"]``).
  - digits → lowercase: MERGE — a lowercase run continues the word
    through digits (``md5sum`` → ``["md5sum"]``; only an uppercase
    letter or a separator marks a new word).

  An uppercase run that is followed by nothing, by digits or by
  another uppercase run (impossible — runs are maximal) stays whole:
  ``NASA`` → ``["NASA"]``, ``IO`` → ``["IO"]``, ``A`` → ``["A"]``.

  Style detection is lexical and deterministic: both ``_`` and ``-``
  → ``mixed``; ``_`` with both letter cases → ``mixed`` (``get_HTTP``),
  with uppercase only → ``screaming_snake``, otherwise ``snake``;
  ``-`` with any uppercase → ``mixed`` (no upper-kebab style), else
  ``kebab``; no separators — all-uppercase letters (>= 2 letters) →
  ``screaming_snake`` (a degenerate one-word constant, ``NASA``),
  first letter uppercase → ``pascal``, otherwise ``camel`` (which
  covers flat lowercase and letterless tokens such as ``utf8`` or
  ``42``).

* ``rejoin`` — words (list) + style → identifier. Styles follow the
  ``CaseConverterTool`` identifier style names: ``snake``,
  ``kebab``, ``camel``, ``pascal``, ``constant`` and its synonym
  ``screaming`` (join with ``_``/``-`` and lowercase; camel/pascal
  capitalize each hump; constant uppercases everything). Words are
  lowercased into the join exactly as ``CaseConverterTool`` does
  (``["HTTP", "Server"]`` → ``http_server`` / ``httpServer`` /
  ``HttpServer`` / ``HTTP_SERVER``), so acronyms do not survive rejoin
  casing and the split identity is case-insensitive:
  ``lower(split(rejoin(words, s))) == lower(words)`` — with two
  inherent exceptions where a boundary is genuinely not representable
  across styles: a pure-digit word (the trailing ``2`` of
  ``ERROR_CODE_2``) merges back into the preceding hump under
  separator-less styles, and uppercasing styles inject a new
  digit-before-uppercase hump into uncased digit tokens
  (``md5sum`` → ``MD5SUM`` → ``MD5|SUM``).
  Leading and trailing separator characters inside a word
  (``"_private"``) pass through untouched. For the full text-level
  case styles (upper, lower, title, sentence, slug) use
  ``CaseConverterTool`` directly.

* ``is_identifier`` — text (string) → validity against the ASCII
  code-identifier grammar ``^[A-Za-z_][A-Za-z0-9_]*$`` (Python
  identifiers scoped to ASCII: no dash, no leading digit, no spaces),
  a keyword flag against the embedded 35-word hard Python keyword
  list (``False`` ... ``yield``, case-sensitive; soft keywords such as
  ``match`` are NOT included), the first invalid character position as
  ``invalid_reason`` and the best-effort ``style_detected``. Unicode
  letters are reported invalid — the grammar is deliberately ASCII.

* ``batch_split`` — identifiers (list) → per-identifier splits plus a
  search vocabulary: the unique lowercased words with occurrence
  counts across the whole batch (keyed case-insensitively so
  ``HTTPServer`` and ``http_server`` both feed the same "server"
  entry; keys are lowercased verbatim, separators attached by the
  preservation rules included), in deterministic first-appearance
  order. An item that fails identifier validation does not abort the
  batch: it yields a structured per-item ``error`` entry.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, wrong types, ``None`` required
inputs, non-string items, empty strings where an identifier is
required, characters outside ``[A-Za-z0-9_-]`` for split identifiers
and rejoin words, unknown rejoin style, inputs over the size caps)
raise a ``ValueError``, mirroring the other common tools.
"""

import re
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Charset accepted for split identifiers and rejoin words: ASCII
# letters, digits, underscore and dash (nothing else — no spaces, no
# dots, no Unicode).
_IDENTIFIER_CHARSET = re.compile(r"^[A-Za-z0-9_-]+$")
# ASCII code-identifier grammar used by is_identifier.
_PYTHON_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# Maximal lowercase / UPPERCASE / digit runs inside a separator-free
# token.
_TOKEN_RUN = re.compile(r"[a-z]+|[A-Z]+|[0-9]+")
# The 35 hard keywords of Python 3 (keyword.kwlist, embedded so the
# answer is pinned across interpreter versions; soft keywords such as
# match, case, type and _ are deliberately excluded).
_PYTHON_KEYWORDS = frozenset({
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else",
    "except", "finally", "for", "from", "global", "if", "import", "in",
    "is", "lambda", "nonlocal", "not", "or", "pass", "raise",
    "return", "try", "while", "with", "yield",
})
# Input size caps (module-level so classmethods can read them).
_MAX_IDENTIFIER_CHARS = 10_000
_MAX_ITEMS = 10_000
_MAX_TOTAL_CHARS = 200_000


class IdentifierSplitTool(Tool):
    """Code identifier word extractor / re-joiner / validator.

    Attributes:
        max_identifier_chars (int): Upper bound on a single identifier
            or ``text`` input length.
        max_items (int): Upper bound on the number of ``words`` /
            ``identifiers`` items.
        max_total_chars (int): Upper bound on the total number of
            characters across all list items.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "identifier_split_tool"
    description: str = (
        "Identifier split tool — extract the words inside code "
        "identifiers, pure Python stdlib, no network. mode='split' "
        "splits an identifier into words with acronyms preserved "
        "(HTTPServer -> [HTTP, Server], XMLHttpRequest -> [XML, Http, "
        "Request], utf8Decode -> [utf8, Decode], base64 -> [base64]) "
        "and detects the style (camel/pascal/snake/kebab/"
        "screaming_snake/mixed), mode='rejoin' joins a word list back "
        "into snake/kebab/camel/pascal/constant (screaming) style — "
        "CaseConverterTool covers full text case conversions, "
        "mode='is_identifier' checks the ASCII identifier grammar "
        "^[A-Za-z_][A-Za-z0-9_]*$ with a Python keyword flag, and "
        "mode='batch_split' splits a symbol list and builds a "
        "lowercased word vocabulary with counts. Round-trip identity: "
        "lower(split(rejoin(words, style))) == lower(words)."
    )

    MODES: ClassVar[tuple] = ("split", "rejoin", "is_identifier", "batch_split")
    REJOIN_STYLES: ClassVar[dict] = {
        # target style name -> (joiner, casing) where casing is one of
        # "lower", "capitalize", "upper" applied per word.
        "snake": ("_", "lower"),
        "kebab": ("-", "lower"),
        "camel": ("", "camel"),
        "pascal": ("", "capitalize"),
        "constant": ("_", "upper"),
        "screaming": ("_", "upper"),
    }

    max_identifier_chars: int = _MAX_IDENTIFIER_CHARS
    max_items: int = _MAX_ITEMS
    max_total_chars: int = _MAX_TOTAL_CHARS

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        identifier: Any = None,
        words: Any = None,
        style: Any = None,
        text: Any = None,
        identifiers: Any = None,
    ) -> Dict[str, Any]:
        """Run one identifier operation.

        Args:
            mode (str): One of ``split`` / ``rejoin`` / ``is_identifier``
                / ``batch_split``.
            identifier (str): The identifier to split; required for the
                ``split`` mode (non-empty, ``[A-Za-z0-9_-]+``).
            words (List[str]): The word list to re-join; required for
                the ``rejoin`` mode (1..N non-empty items, each
                ``[A-Za-z0-9_-]+``).
            style (str): The target style for the ``rejoin`` mode —
                ``snake`` / ``kebab`` / ``camel`` / ``pascal`` /
                ``constant`` / ``screaming``.
            text (str): The string to check; required for the
                ``is_identifier`` mode (any string; emptiness and
                invalid characters are reported, not raised).
            identifiers (List[str]): The symbol list to split;
                required for the ``batch_split`` mode. Items that fail
                identifier validation yield structured per-item errors.

        Returns:
            Dict[str, Any]: The operation result — ``words`` /
            ``word_count`` / ``style_detected`` for ``split``, the
            joined identifier under ``result`` for ``rejoin``, the
            grammar / keyword verdict for ``is_identifier``, and the
            per-item splits plus the counted ``vocabulary`` for
            ``batch_split``.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "split":
            clean = self._validate_identifier(identifier)
            words = self.split_words(clean)
            return {
                "mode": "split",
                "identifier": clean,
                "words": words,
                "word_count": len(words),
                "style_detected": self.detect_style(clean),
            }
        if mode == "rejoin":
            clean_words = self._validate_words(words)
            clean_style = self._validate_style(style)
            return {
                "mode": "rejoin",
                "style": clean_style,
                "result": self.rejoin_words(clean_words, clean_style),
            }
        if mode == "is_identifier":
            clean_text = self._validate_text(text)
            valid = bool(_PYTHON_IDENTIFIER.match(clean_text))
            return {
                "mode": "is_identifier",
                "text": clean_text,
                "valid": valid,
                "is_keyword": clean_text in _PYTHON_KEYWORDS,
                "invalid_reason": None if valid else self._invalid_reason(clean_text),
                "style_detected": self.detect_style(clean_text),
            }
        clean_list = self._validate_identifiers(identifiers)
        return self._run_batch_split(clean_list)

    # ------------------------------------------------------------------ #
    # Core algorithms (pure, deterministic)
    # ------------------------------------------------------------------ #

    @classmethod
    def split_words(cls, identifier: str) -> List[str]:
        """Split an already-validated identifier into its words."""
        # Peel the leading and trailing separator runs; they stay
        # attached to the first / last word.
        start = 0
        end = len(identifier)
        while start < end and identifier[start] in "_-":
            start += 1
        while end > start and identifier[end - 1] in "_-":
            end -= 1
        lead, trail, core = identifier[:start], identifier[end:], identifier[start:end]
        if not core:
            # The whole identifier is one separator run.
            return [identifier]
        words: List[str] = []
        for token in re.split(r"[_-]+", core):
            if token:
                words.extend(cls._split_token(token))
        words[0] = lead + words[0]
        words[-1] = words[-1] + trail
        return words

    @classmethod
    def _split_token(cls, token: str) -> List[str]:
        """Split one separator-free token on case/digit boundaries."""
        words: List[str] = []
        current = ""
        prev_kind = ""
        for run in _TOKEN_RUN.findall(token):
            head = run[0]
            kind = "u" if head.isupper() else ("l" if head.islower() else "d")
            if not current:
                current, prev_kind = run, kind
            elif prev_kind == "l" and kind == "u":
                # lower -> Upper: a camel hump starts.
                words.append(current)
                current, prev_kind = run, kind
            elif prev_kind == "u" and kind == "l":
                # Upper-run followed by lowercase: a single Upper
                # capitalizes the word ("Server"); a longer run keeps
                # itself whole as an acronym and donates its last
                # letter to the new word ("HTTPServer" -> HTTP|Server).
                if len(current) == 1:
                    current += run
                else:
                    words.append(current[:-1])
                    current = current[-1] + run
                prev_kind = "l"
            elif prev_kind == "d" and kind == "u":
                # digits -> Upper: digits never join a following hump.
                words.append(current)
                current, prev_kind = run, kind
            else:
                # letter run -> digits ("base64", "SHA256") or digits
                # -> lowercase ("md5sum"): the runs merge.
                current += run
                prev_kind = kind
        if current:
            words.append(current)
        return words

    @classmethod
    def detect_style(cls, text: str) -> str:
        """Detect the case style of a string (best effort, lexical)."""
        has_under = "_" in text
        has_dash = "-" in text
        has_lower = any(ch.islower() for ch in text)
        has_upper = any(ch.isupper() for ch in text)
        letters = [ch for ch in text if ch.isalpha()]
        if has_under and has_dash:
            return "mixed"
        if has_under:
            if has_lower and has_upper:
                return "mixed"
            return "screaming_snake" if has_upper else "snake"
        if has_dash:
            return "mixed" if has_upper else "kebab"
        if len(letters) >= 2 and not has_lower:
            return "screaming_snake"
        if letters and letters[0].isupper():
            return "pascal"
        return "camel"

    @classmethod
    def rejoin_words(cls, words: List[str], style: str) -> str:
        """Join already-validated words into the target style."""
        joiner, casing = cls.REJOIN_STYLES[style]
        if casing == "lower":
            return joiner.join(word.lower() for word in words)
        if casing == "upper":
            return joiner.join(word.upper() for word in words)
        if casing == "capitalize":
            return joiner.join(word.capitalize() for word in words)
        # camel: first word fully lowercase, each hump capitalized.
        return words[0].lower() + "".join(
            word.capitalize() for word in words[1:]
        )

    @classmethod
    def _invalid_reason(cls, text: str) -> str:
        """Explain the first violation of the identifier grammar."""
        if not text:
            return "empty string"
        if not (text[0].isascii() and (text[0].isalpha() or text[0] == "_")):
            return (
                f"starts with {text[0]!r} (an identifier must start with "
                "an ASCII letter or underscore)"
            )
        for index, ch in enumerate(text):
            if not (ch.isascii() and (ch.isalnum() or ch == "_")):
                return (
                    f"contains {ch!r} at position {index} (only ASCII "
                    "letters, digits and underscores are allowed)"
                )
        return None  # pragma: no cover - unreachable for invalid texts

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"identifier_split_tool: {message}")

    @classmethod
    def _check_string(cls, value: Any, name: str, allow_empty: bool) -> str:
        """Validate a plain string input."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{name} must be a string (got {value!r})")
        if not allow_empty and not value:
            cls._invalid(f"{name} must not be empty")
        if len(value) > _MAX_IDENTIFIER_CHARS:
            cls._invalid(
                f"{name} exceeds the {_MAX_IDENTIFIER_CHARS:,}-character "
                f"limit (got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _validate_identifier(cls, identifier: Any) -> str:
        """Validate the ``identifier`` input (split mode)."""
        clean = cls._check_string(identifier, "identifier", allow_empty=False)
        if not _IDENTIFIER_CHARSET.match(clean):
            cls._invalid(
                "identifier must contain only ASCII letters, digits, "
                f"underscore and dash (got {identifier!r})"
            )
        return clean

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input (is_identifier mode; any string)."""
        return cls._check_string(text, "text", allow_empty=True)

    @classmethod
    def _validate_words(cls, words: Any) -> List[str]:
        """Validate the ``words`` input (rejoin mode)."""
        if words is None or isinstance(words, (str, bool)) or not isinstance(words, (list, tuple)):
            cls._invalid(f"words must be a list of strings (got {words!r})")
        if not words:
            cls._invalid("words must contain at least one word")
        if len(words) > _MAX_ITEMS:
            cls._invalid(
                f"words exceeds the {_MAX_ITEMS:,}-item limit "
                f"(got {len(words):,} items)"
            )
        total = 0
        for word in words:
            if isinstance(word, bool) or not isinstance(word, str):
                cls._invalid(f"every word must be a string (got {word!r})")
            if not word:
                cls._invalid("every word must be non-empty")
            if not _IDENTIFIER_CHARSET.match(word):
                cls._invalid(
                    "every word must contain only ASCII letters, digits, "
                    f"underscore and dash (got {word!r})"
                )
            total += len(word)
        if total > _MAX_TOTAL_CHARS:
            cls._invalid(
                f"words total more than {_MAX_TOTAL_CHARS:,} characters "
                f"(got {total:,} characters)"
            )
        return list(words)

    @classmethod
    def _validate_style(cls, style: Any) -> str:
        """Validate the ``style`` input (rejoin mode)."""
        if style is None or isinstance(style, bool) or not isinstance(style, str):
            cls._invalid(f"style must be a string (got {style!r})")
        if style not in cls.REJOIN_STYLES:
            cls._invalid(
                "style must be one of: "
                f"{', '.join(cls.REJOIN_STYLES)} (got {style!r})"
            )
        return style

    @classmethod
    def _validate_identifiers(cls, identifiers: Any) -> List[str]:
        """Validate the ``identifiers`` input (batch_split mode)."""
        if identifiers is None or isinstance(identifiers, (str, bool)) or not isinstance(identifiers, (list, tuple)):
            cls._invalid(
                f"identifiers must be a list of strings (got {identifiers!r})"
            )
        if len(identifiers) > _MAX_ITEMS:
            cls._invalid(
                f"identifiers exceeds the {_MAX_ITEMS:,}-item limit "
                f"(got {len(identifiers):,} items)"
            )
        total = 0
        for item in identifiers:
            if isinstance(item, bool) or not isinstance(item, str):
                cls._invalid(
                    f"every identifiers item must be a string (got {item!r})"
                )
            total += len(item)
        if total > _MAX_TOTAL_CHARS:
            cls._invalid(
                f"identifiers total more than {_MAX_TOTAL_CHARS:,} "
                f"characters (got {total:,} characters)"
            )
        return list(identifiers)

    # ------------------------------------------------------------------ #
    # batch_split
    # ------------------------------------------------------------------ #

    @classmethod
    def _run_batch_split(cls, identifiers: List[str]) -> Dict[str, Any]:
        """Split every item and build the counted word vocabulary."""
        results: List[Dict[str, Any]] = []
        vocabulary: Dict[str, int] = {}
        for item in identifiers:
            if (
                not item
                or len(item) > _MAX_IDENTIFIER_CHARS
                or not _IDENTIFIER_CHARSET.match(item)
            ):
                results.append({
                    "identifier": item,
                    "error": {
                        "type": "invalid_identifier",
                        "message": (
                            "identifier must be a non-empty string of "
                            "ASCII letters, digits, underscore and dash "
                            f"within the {_MAX_IDENTIFIER_CHARS:,}-character "
                            f"limit (got {item!r})"
                        ),
                    },
                })
                continue
            words = cls.split_words(item)
            results.append({
                "identifier": item,
                "words": words,
                "word_count": len(words),
                "style_detected": cls.detect_style(item),
            })
            for word in words:
                vocabulary[word.lower()] = vocabulary.get(word.lower(), 0) + 1
        return {
            "mode": "batch_split",
            "count": len(identifiers),
            "results": results,
            "vocabulary": vocabulary,
            "vocabulary_size": len(vocabulary),
        }
