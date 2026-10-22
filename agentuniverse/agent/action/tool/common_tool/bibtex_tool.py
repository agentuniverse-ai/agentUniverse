#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: bibtex_tool.py

"""BibTeX bibliography parsing tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency bibliography parser
for academic agents: the ArXiv / PubMed / Crossref / Semantic Scholar
tools find papers online, but none of them can read the ``.bib`` files
those searches ultimately produce. This tool parses BibTeX source text
directly and exposes four modes:

* ``parse`` — full parse of ``.bib`` text into entries
  ``{"type", "key", "fields"}``. ``@article{key, ...}`` and the
  parenthesised ``@article(key, ...)`` form are both accepted; field
  values may be brace-delimited (nested braces preserved verbatim, so
  ``{B}ib{T}e{X}`` capitalisation protection survives), quoted
  (``"..."`` — a brace group inside quotes protects a literal ``"``),
  bare numbers, or ``#``-concatenations of those parts; ``@string``
  macros (case-insensitive names) are expanded wherever they are
  referenced later in the file, and the twelve month macros
  ``jan``..``dec`` are predefined to their full English month names
  (as every standard BibTeX style defines them) so the ubiquitous
  ``month = jan`` works out of the box — an explicit ``@string``
  overrides a month default. ``@comment`` and ``@preamble`` blocks
  are skipped, as is any text between entries — including an
  ``@word`` that is not followed by ``{`` or ``(`` (an email address
  in comment text, for example), which BibTeX itself likewise skips.
  The name fields ``author`` and ``editor`` are
  returned as lists of person objects ``{"first", "last", "jr",
  "raw"}``: the value is split on the standalone word ``and``
  (case-insensitive, brace depth 0, so ``{Barnes and Noble}`` stays
  one person), and each person honours both the ``Last, First`` order
  (including the ``Last, Jr, First`` three-comma form) and the
  ``First von Last`` order with BibTeX's von rule — in the latter
  the last name starts at the first token beginning with a lowercase
  letter (``Ludwig van Beethoven`` → last ``van Beethoven``), a
  brace-protected token never counts as a von particle, and with no
  von particle the final token is the last name; a lone token is
  treated as the last name (typical for braced organisation names).
* ``summary`` — entry count, per-type counts, the numeric year range,
  and one ``"Author et al., Year, Title (venue)"`` line per entry
  (first author's last name plus ``et al.`` when there are several
  authors; ``editor`` is used when ``author`` is absent and
  ``Anonymous`` when neither exists; the venue is ``journal`` else
  ``booktitle`` else ``publisher``; missing parts are omitted).
* ``filter`` — subset of entries matching ALL supplied matchers:
  ``entry_type`` (exact, case-insensitive), ``query``
  (case-insensitive substring against the citation key or any field
  value, person names matched via their raw form) and the inclusive
  ``year_from`` / ``year_to`` range (entries without a four-digit year
  are excluded only when a year matcher is given).
* ``to_keys`` — just the citation keys, in file order.

Content-level failures are returned as a structured ``error`` payload
(never raised): ``unbalanced_braces``, ``undefined_macro``,
``duplicate_key`` and ``syntax`` all carry the failing character
position as ``{"offset", "line", "column"}`` (line/column are
1-based). Malformed parameters raise ``ValueError`` before any parsing
happens, mirroring the other common tools. Runs of whitespace in
field values are collapsed to single spaces, matching BibTeX's
token-based value model; every other character, including protective
braces, is preserved verbatim.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_WHITESPACE = " \t\r\n\f\v"
_ENTRY_TYPE_RE = re.compile(r"[A-Za-z]+")
_FIELD_NAME_RE = re.compile(r"[A-Za-z0-9_.:+/-]+")
_MACRO_NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.:+-]*")
_NUMBER_RE = re.compile(r"[0-9]+")
_YEAR_RE = re.compile(r"\d{4}")
_WHITESPACE_RUN_RE = re.compile(r"\s+")

# The twelve month macros every standard BibTeX style defines (jan =
# "January" ... dec = "December"). Real .bib files write `month = jan`
# ubiquitously, so the parser seeds them alongside @string definitions;
# an explicit @string{jan = ...} in the file overrides the default.
_MONTH_MACROS: dict[str, str] = {
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}

# Citation-key characters: everything up to whitespace, ',', '{', '}',
# '(', ')', '"', '#' or '='.
_CITATION_KEY_STOP = set(",{}()\"" + _WHITESPACE + "#=")


class _BibtexParseError(Exception):
    """Internal: a content-level BibTeX parse failure with a position."""

    def __init__(self, error_type: str, message: str, pos: int) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.pos = pos


class _BibtexScanner:
    """Character-level scanner over one BibTeX source string."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.n = len(text)
        self.pos = 0
        # Month macros are predefined (BibTeX styles define them all);
        # @string definitions in the file extend and override these.
        self.macros: dict[str, str] = dict(_MONTH_MACROS)
        self.entries: list[dict[str, Any]] = []
        self._seen_keys: set[str] = set()

    # -- low-level helpers ------------------------------------------- #

    def _skip_ws(self) -> None:
        while self.pos < self.n and self.text[self.pos] in _WHITESPACE:
            self.pos += 1

    def _peek(self) -> str | None:
        return self.text[self.pos] if self.pos < self.n else None

    def _fail(self, error_type: str, message: str, pos: int) -> None:
        raise _BibtexParseError(error_type, message, pos)

    # -- top level ---------------------------------------------------- #

    def scan(self) -> list[dict[str, Any]]:
        """Scan the whole input, returning the entry list."""
        while True:
            at = self.text.find("@", self.pos)
            if at == -1:
                break
            self.pos = at + 1
            match = _ENTRY_TYPE_RE.match(self.text, self.pos)
            if match is None:
                # A stray '@' (e.g. an email address in inter-entry
                # comment text) is treated as comment text and skipped.
                continue
            entry_type = match.group(0).lower()
            self.pos = match.end()
            self._skip_ws()
            opener = self._peek()
            if opener not in ("{", "("):
                # BibTeX itself is lenient here ("I'm skipping whatever
                # remains of this entry"): an '@word' not followed by
                # '{'/'(' — e.g. an email address inside comment text —
                # is treated as comment text and skipped.
                continue
            closer = "}" if opener == "{" else ")"
            open_pos = self.pos
            self.pos += 1
            if entry_type == "comment":
                self._skip_balanced(entry_type, opener, closer, open_pos)
            elif entry_type == "preamble":
                self._read_value()  # validated, then discarded
                self._expect_closer(entry_type, closer, open_pos)
            elif entry_type == "string":
                self._parse_string_block(entry_type, closer, open_pos)
            else:
                self._parse_entry(entry_type, opener, closer, open_pos)
        return self.entries

    def _skip_balanced(
        self, entry_type: str, opener: str, closer: str, open_pos: int
    ) -> None:
        """Skip a brace- (or paren-) balanced block, e.g. ``@comment``."""
        depth = 1
        while self.pos < self.n:
            ch = self.text[self.pos]
            if ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    self.pos += 1
                    return
            self.pos += 1
        self._fail(
            "unbalanced_braces",
            f"unterminated @{entry_type} block opened here — "
            f"missing the closing {closer!r}",
            open_pos,
        )

    def _expect_closer(
        self, entry_type: str, closer: str, open_pos: int
    ) -> None:
        self._skip_ws()
        ch = self._peek()
        if ch is None:
            self._fail(
                "unbalanced_braces",
                f"unterminated @{entry_type} block opened here — "
                f"missing the closing {closer!r}",
                open_pos,
            )
        if ch != closer:
            self._fail(
                "syntax",
                f"expected {closer!r} to close the @{entry_type} block "
                f"(got {ch!r})",
                self.pos,
            )
        self.pos += 1

    # -- @string blocks ----------------------------------------------- #

    def _parse_string_block(
        self, entry_type: str, closer: str, open_pos: int
    ) -> None:
        """Parse ``@string{name = value, ...}`` macro definitions."""
        while True:
            self._skip_ws()
            if self._peek() == closer:
                self._fail(
                    "syntax", "empty @string block", self.pos
                )
            match = _MACRO_NAME_RE.match(self.text, self.pos)
            if match is None:
                self._fail(
                    "syntax",
                    "expected a macro name in @string block",
                    self.pos,
                )
            name = match.group(0)
            self.pos = match.end()
            self._skip_ws()
            if self._peek() != "=":
                self._fail(
                    "syntax",
                    f"expected '=' after macro name {name!r} in @string "
                    f"block (got {self._peek()!r})",
                    self.pos,
                )
            self.pos += 1
            self._skip_ws()
            self.macros[name.lower()] = self._read_value()
            self._skip_ws()
            if self._peek() == ",":
                self.pos += 1
                continue
            self._expect_closer(entry_type, closer, open_pos)
            return

    # -- regular entries ---------------------------------------------- #

    def _parse_entry(
        self, entry_type: str, opener: str, closer: str, open_pos: int
    ) -> None:
        """Parse one regular ``@type{key, field = value, ...}`` entry."""
        self._skip_ws()
        key_start = self.pos
        while self.pos < self.n:
            ch = self.text[self.pos]
            if ch in _CITATION_KEY_STOP or ch == closer:
                break
            self.pos += 1
        key = self.text[key_start:self.pos]
        if not key:
            self._fail(
                "syntax",
                f"missing citation key in @{entry_type} entry",
                key_start,
            )
        if key in self._seen_keys:
            self._fail(
                "duplicate_key",
                f"duplicate citation key {key!r} (first defined earlier "
                f"in the file)",
                key_start,
            )
        self._seen_keys.add(key)

        fields: dict[str, Any] = {}
        self._skip_ws()
        if self._peek() == ",":
            self.pos += 1
            while True:
                self._skip_ws()
                if self._peek() == closer:
                    break
                if self._peek() is None:
                    self._fail(
                        "unbalanced_braces",
                        f"unterminated @{entry_type} entry opened here — "
                        f"missing the closing {closer!r}",
                        open_pos,
                    )
                match = _FIELD_NAME_RE.match(self.text, self.pos)
                if match is None:
                    self._fail(
                        "syntax",
                        f"expected a field name in @{entry_type} entry "
                        f"{key!r}",
                        self.pos,
                    )
                field_name = match.group(0).lower()
                self.pos = match.end()
                self._skip_ws()
                if self._peek() != "=":
                    self._fail(
                        "syntax",
                        f"expected '=' after field name {field_name!r} "
                        f"(got {self._peek()!r})",
                        self.pos,
                    )
                self.pos += 1
                self._skip_ws()
                # BibTeX itself warns on repeated fields and keeps the
                # last value; this parser does the same, documented.
                fields[field_name] = self._read_value()
                self._skip_ws()
                after_value = self._peek()
                if after_value == ",":
                    self.pos += 1
                    continue
                if after_value == closer:
                    break
                if after_value is None:
                    self._fail(
                        "unbalanced_braces",
                        f"unterminated @{entry_type} entry opened here "
                        f"— missing the closing {closer!r}",
                        open_pos,
                    )
                self._fail(
                    "syntax",
                    f"expected ',' or {closer!r} after the value of "
                    f"field {field_name!r} (got {after_value!r})",
                    self.pos,
                )
        if self._peek() != closer:
            if self._peek() is None:
                self._fail(
                    "unbalanced_braces",
                    f"unterminated @{entry_type} entry opened here — "
                    f"missing the closing {closer!r}",
                    open_pos,
                )
            self._fail(
                "syntax",
                f"expected ',' or {closer!r} after citation key {key!r} "
                f"(got {self._peek()!r})",
                self.pos,
            )
        self.pos += 1

        for name in BibtexTool.NAME_FIELDS:
            if name in fields:
                fields[name] = BibtexTool.split_persons(fields[name])
        self.entries.append(
            {"type": entry_type, "key": key, "fields": fields}
        )

    # -- values -------------------------------------------------------- #

    def _read_value(self) -> str:
        """Read one field value: parts joined with '#', macros expanded.

        Each part is a braced ``{...}`` group (nested braces preserved
        verbatim), a quoted ``"..."`` string (brace groups inside
        protect literal quotes), a bare number, or a macro reference
        resolved against the ``@string`` definitions seen so far.
        """
        parts: list[str] = []
        while True:
            self._skip_ws()
            ch = self._peek()
            if ch == "{":
                parts.append(self._read_braced())
            elif ch == '"':
                parts.append(self._read_quoted())
            else:
                # Match the token regexes directly (never str.isdigit /
                # str.isalpha, which are True for non-ASCII characters
                # like '²' or '中' that the BibTeX token grammar then
                # cannot consume): bare ASCII digits, else a macro name.
                match = _NUMBER_RE.match(self.text, self.pos)
                if match is not None:
                    parts.append(match.group(0))
                    self.pos = match.end()
                else:
                    match = _MACRO_NAME_RE.match(self.text, self.pos)
                    if match is None:
                        self._fail(
                            "syntax",
                            f"expected a field value ({{...}}, \"...\", "
                            f"number or macro name) but got {ch!r}",
                            self.pos,
                        )
                    name = match.group(0)
                    macro = self.macros.get(name.lower())
                    if macro is None:
                        self._fail(
                            "undefined_macro",
                            f"undefined @string macro {name!r} — define "
                            f"it with @string{{{name} = ...}} before it "
                            f"is referenced",
                            self.pos,
                        )
                    parts.append(macro)
                    self.pos = match.end()
            self._skip_ws()
            if self._peek() == "#":
                self.pos += 1
                continue
            return BibtexTool.collapse_whitespace("".join(parts))

    def _read_braced(self) -> str:
        """Read a ``{...}`` value, returning its content verbatim."""
        open_pos = self.pos
        self.pos += 1
        depth = 1
        start = self.pos
        while self.pos < self.n:
            ch = self.text[self.pos]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    content = self.text[start:self.pos]
                    self.pos += 1
                    return content
            self.pos += 1
        self._fail(
            "unbalanced_braces",
            "unterminated braced value opened here — missing the "
            "matching '}'",
            open_pos,
        )

    def _read_quoted(self) -> str:
        """Read a ``"..."`` value; brace groups protect literal quotes."""
        open_pos = self.pos
        self.pos += 1
        depth = 0
        start = self.pos
        while self.pos < self.n:
            ch = self.text[self.pos]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    self._fail(
                        "unbalanced_braces",
                        "unbalanced '}' inside a quoted value — braces "
                        "within \"...\" must be closed before the value "
                        "ends",
                        self.pos,
                    )
            elif ch == '"' and depth == 0:
                content = self.text[start:self.pos]
                self.pos += 1
                return content
            self.pos += 1
        self._fail(
            "unbalanced_braces",
            "unterminated quoted value opened here — missing the "
            "closing '\"'",
            open_pos,
        )


class BibtexTool(Tool):
    """BibTeX bibliography parsing tool built purely on the stdlib.

    Attributes:
        max_bib_chars (int): Upper bound on the ``bib`` input length;
            longer inputs are rejected before any parsing.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "bibtex_tool"
    description: str = (
        "BibTeX tool — pure Python stdlib, no network required. Parse "
        ".bib bibliography text into entries with type, citation key and "
        "fields (mode='parse', with brace-balanced values preserving "
        "nested braces, quoted values, '#'-concatenation and @string "
        "macro expansion incl. predefined month macros jan..dec, "
        "@comment/@preamble skipped, author/editor split into person "
        "lists with BibTeX's Last, First and First von Last name "
        "orders), summarise a file (mode='summary', "
        "with counts by type, year range and per-entry one-liners), "
        "filter entries (mode='filter', with entry_type / query "
        "substring / year range) and list citation keys in order "
        "(mode='to_keys')."
    )

    MODES: ClassVar[tuple] = ("parse", "summary", "filter", "to_keys")
    NAME_FIELDS: ClassVar[tuple] = ("author", "editor")
    max_bib_chars: ClassVar[int] = 1_000_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        bib: Any = None,
        entry_type: Any = None,
        query: Any = None,
        year_from: Any = None,
        year_to: Any = None,
    ) -> dict[str, Any]:
        """Run one BibTeX operation.

        Args:
            mode (str): One of ``parse`` / ``summary`` / ``filter`` /
                ``to_keys``.
            bib (str): The ``.bib`` source text. Required for every
                mode; a non-empty string of at most 1,000,000
                characters (a file whose entries are all skipped, e.g.
                only comments, simply yields zero entries).
            entry_type (Any): ``filter`` mode only — exact entry-type
                match, case-insensitive (e.g. ``"article"``).
            query (Any): ``filter`` mode only — case-insensitive
                substring matched against the citation key or any field
                value (person names via their raw form).
            year_from (Any): ``filter`` mode only — inclusive lower
                bound on the four-digit year; an int or digit string.
            year_to (Any): ``filter`` mode only — inclusive upper bound
                on the four-digit year; an int or digit string.

        Returns:
            Dict[str, Any]: The operation result (always a ``count``
            plus mode-specific keys) or a structured ``error`` payload
            ``{"type", "message", "position"}`` for content-level
            failures (unbalanced braces, undefined macros, duplicate
            citation keys, syntax errors) with the failing character
            position as ``offset`` / ``line`` / ``column``.

        Raises:
            ValueError: If any parameter is malformed (before any
                parsing happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_bib = self._validate_bib(bib)
        clean_matchers = (
            self._validate_matchers(entry_type, query, year_from, year_to)
            if mode == "filter"
            else None
        )
        if clean_matchers is None and mode != "filter":
            self._reject_filter_args(mode, entry_type, query, year_from, year_to)

        try:
            entries = _BibtexScanner(clean_bib).scan()
        except _BibtexParseError as exc:
            return self._error_result(mode, clean_bib, exc)
        if mode == "parse":
            return {"mode": "parse", "count": len(entries), "entries": entries}
        if mode == "summary":
            return self._summarize(entries)
        if mode == "filter":
            return self._filter_entries(entries, clean_matchers)
        return {"mode": "to_keys", "count": len(entries), "keys": [e["key"] for e in entries]}

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any parsing)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"bibtex_tool: {message}")

    @classmethod
    def _validate_bib(cls, bib: Any) -> str:
        """Validate the ``bib`` source text."""
        if bib is None or isinstance(bib, bool) or not isinstance(bib, str):
            cls._invalid(f"bib must be a non-empty string (got {bib!r})")
        if not bib:
            cls._invalid("bib must be a non-empty string (got '')")
        if len(bib) > cls.max_bib_chars:
            cls._invalid(
                f"bib exceeds the {cls.max_bib_chars:,}-character limit "
                f"(got {len(bib):,} characters)"
            )
        return bib

    @classmethod
    def _validate_matchers(
        cls, entry_type: Any, query: Any, year_from: Any, year_to: Any
    ) -> dict[str, Any]:
        """Validate the ``filter``-mode matchers (all combined with AND)."""
        if entry_type is not None:
            if isinstance(entry_type, bool) or not isinstance(entry_type, str):
                cls._invalid(
                    f"entry_type must be a non-empty string or None (got {entry_type!r})"
                )
            if not entry_type:
                cls._invalid("entry_type must be a non-empty string or None (got '')")
        if query is not None:
            if isinstance(query, bool) or not isinstance(query, str):
                cls._invalid(
                    f"query must be a non-empty string or None (got {query!r})"
                )
            if not query:
                cls._invalid("query must be a non-empty string or None (got '')")
        clean_from = cls._validate_year_bound("year_from", year_from)
        clean_to = cls._validate_year_bound("year_to", year_to)
        if (
            entry_type is None
            and query is None
            and clean_from is None
            and clean_to is None
        ):
            cls._invalid(
                "filter mode requires at least one matcher: entry_type, "
                "query, year_from or year_to"
            )
        matchers: dict[str, Any] = {}
        if entry_type is not None:
            matchers["entry_type"] = entry_type.lower()
        if query is not None:
            matchers["query"] = query
        if clean_from is not None:
            matchers["year_from"] = clean_from
        if clean_to is not None:
            matchers["year_to"] = clean_to
        return matchers

    @classmethod
    def _validate_year_bound(cls, name: str, value: Any) -> int | None:
        """Validate one inclusive year bound (int or digit string)."""
        if value is None:
            return None
        if isinstance(value, bool):
            cls._invalid(f"{name} must be an integer year or None (got {value!r})")
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        cls._invalid(f"{name} must be an integer year or None (got {value!r})")

    @classmethod
    def _reject_filter_args(
        cls,
        mode: str,
        entry_type: Any,
        query: Any,
        year_from: Any,
        year_to: Any,
    ) -> None:
        """Reject filter-specific arguments outside the filter mode."""
        for name, value in (
            ("entry_type", entry_type),
            ("query", query),
            ("year_from", year_from),
            ("year_to", year_to),
        ):
            if value is not None:
                cls._invalid(
                    f"{name} is only accepted in filter mode (mode={mode!r})"
                )

    # ------------------------------------------------------------------ #
    # summary / filter modes
    # ------------------------------------------------------------------ #

    @classmethod
    def _summarize(cls, entries: list[dict[str, Any]]) -> dict[str, Any]:
        """Count entries by type and year range, one line per entry."""
        type_counts: dict[str, int] = {}
        years: list[int] = []
        lines: list[str] = []
        for entry in entries:
            entry_type = entry["type"]
            type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
            year = cls.extract_year(entry["fields"].get("year"))
            if year is not None:
                years.append(year)
            lines.append(cls._one_liner(entry))
        return {
            "mode": "summary",
            "count": len(entries),
            "types": {key: type_counts[key] for key in sorted(type_counts)},
            "year_range": (
                [min(years), max(years)] if years else None
            ),
            "entries": lines,
        }

    @classmethod
    def _one_liner(cls, entry: dict[str, Any]) -> str:
        """Build ``Author et al., Year, Title (venue)`` for one entry."""
        fields = entry["fields"]
        names = fields.get("author") or fields.get("editor") or []
        if names:
            label = cls._display_name(names[0]["last"]) or cls._display_name(
                names[0]["raw"]
            )
            if len(names) > 1:
                label += " et al."
        else:
            label = "Anonymous"
        parts = [label]
        year = cls.extract_year(fields.get("year"))
        if year is not None:
            parts.append(str(year))
        title = fields.get("title")
        if title:
            parts.append(title)
        line = ", ".join(parts)
        venue = fields.get("journal") or fields.get("booktitle") or fields.get(
            "publisher"
        )
        if venue:
            line += f" ({venue})"
        return line

    @classmethod
    def _filter_entries(
        cls, entries: list[dict[str, Any]], matchers: dict[str, Any]
    ) -> dict[str, Any]:
        """Return the entries matching every supplied matcher (AND)."""
        entry_type = matchers.get("entry_type")
        query = matchers.get("query")
        year_from = matchers.get("year_from")
        year_to = matchers.get("year_to")
        needle = query.lower() if query is not None else None
        matched = []
        for entry in entries:
            if entry_type is not None and entry["type"] != entry_type:
                continue
            if needle is not None:
                haystack = cls._searchable_text(entry)
                if needle not in haystack.lower():
                    continue
            if year_from is not None or year_to is not None:
                year = cls.extract_year(entry["fields"].get("year"))
                if year is None:
                    continue
                if year_from is not None and year < year_from:
                    continue
                if year_to is not None and year > year_to:
                    continue
            matched.append(entry)
        return {
            "mode": "filter",
            "count": len(matched),
            "matchers": matchers,
            "entries": matched,
        }

    @classmethod
    def _searchable_text(cls, entry: dict[str, Any]) -> str:
        """Join the key and every field value into one search string."""
        pieces = [entry["key"]]
        for value in entry["fields"].values():
            if isinstance(value, list):  # parsed person list
                pieces.extend(person["raw"] for person in value)
            else:
                pieces.append(value)
        return "\n".join(pieces)

    # ------------------------------------------------------------------ #
    # Person-name helpers (BibTeX name splitting)
    # ------------------------------------------------------------------ #

    @staticmethod
    def collapse_whitespace(value: str) -> str:
        """Collapse runs of whitespace to single spaces and strip."""
        return _WHITESPACE_RUN_RE.sub(" ", value).strip()

    @staticmethod
    def _name_tokens(value: str) -> list[str]:
        """Split on whitespace at brace depth 0, keeping braces intact."""
        tokens: list[str] = []
        buffer: list[str] = []
        depth = 0
        for char in value:
            if char == "{":
                depth += 1
                buffer.append(char)
            elif char == "}":
                depth -= 1
                buffer.append(char)
            elif char.isspace() and depth == 0:
                if buffer:
                    tokens.append("".join(buffer))
                    buffer = []
            else:
                buffer.append(char)
        if buffer:
            tokens.append("".join(buffer))
        return tokens

    @staticmethod
    def _split_top_level_commas(value: str) -> list[str]:
        """Split on commas at brace depth 0 (braced commas are literal)."""
        parts: list[str] = []
        buffer: list[str] = []
        depth = 0
        for char in value:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            if char == "," and depth == 0:
                parts.append("".join(buffer))
                buffer = []
            else:
                buffer.append(char)
        parts.append("".join(buffer))
        return parts

    @staticmethod
    def _is_von_token(token: str) -> bool:
        """True when a name token is a BibTeX ``von`` particle.

        A von word starts with an ASCII lowercase letter; a
        brace-protected token (``{van}``) starts with ``{`` and is
        never a von word, exactly as in BibTeX.
        """
        return bool(token) and "a" <= token[0] <= "z"

    @classmethod
    def split_persons(cls, value: str) -> list[dict[str, str]]:
        """Split a name field into person objects.

        The value is split on the standalone word ``and``
        (case-insensitive, brace depth 0 — ``{Barnes and Noble}`` is
        one person). Each person is parsed into ``first`` / ``last`` /
        ``jr`` / ``raw``: two or more comma-separated parts mean
        ``Last, First`` (three parts: ``Last, Jr, First``); without a
        top-level comma the name is in ``First von Last`` order with
        BibTeX's von rule — the last name starts at the first token
        that begins with a lowercase letter (``Ludwig van Beethoven``
        → first ``Ludwig``, last ``van Beethoven``); with no such
        token the final token is the last name and a lone token is a
        last name only. Brace-protected tokens never count as von
        particles (``{de la Cruz}, Maria`` keeps ``{de la Cruz}`` as
        an unsplit last name).
        """
        segments: list[list[str]] = []
        current: list[str] = []
        for token in cls._name_tokens(value):
            if token.lower() == "and" and current:
                segments.append(current)
                current = []
            else:
                current.append(token)
        if current:
            segments.append(current)
        persons = []
        for segment in segments:
            raw = cls.collapse_whitespace(" ".join(segment))
            parts = [cls.collapse_whitespace(part) for part in
                     cls._split_top_level_commas(raw)]
            if len(parts) == 1:
                tokens = cls._name_tokens(parts[0])
                if not tokens:
                    first = last = jr = ""
                elif len(tokens) == 1:
                    first, last, jr = "", tokens[0], ""
                else:
                    # First von Last: the last name absorbs the von
                    # particles, so it starts at the first lowercase
                    # (von) token — except the final token, which is
                    # always part of the last name.
                    von_index = next(
                        (
                            index
                            for index, token in enumerate(tokens[:-1])
                            if cls._is_von_token(token)
                        ),
                        None,
                    )
                    if von_index is None:
                        first = " ".join(tokens[:-1])
                        last = tokens[-1]
                    else:
                        first = " ".join(tokens[:von_index])
                        last = " ".join(tokens[von_index:])
                    jr = ""
            elif len(parts) == 2:
                last, first, jr = parts[0], parts[1], ""
            else:
                last, jr = parts[0], parts[1]
                first = ", ".join(parts[2:])
            persons.append({"first": first, "last": last, "jr": jr, "raw": raw})
        return persons

    # ------------------------------------------------------------------ #
    # Small shared helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def extract_year(value: Any) -> int | None:
        """Extract the first four-digit year from a year field value."""
        if not isinstance(value, str):
            return None
        match = _YEAR_RE.search(value)
        return int(match.group(0)) if match else None

    @staticmethod
    def _display_name(last: str) -> str:
        """Strip one fully-wrapping brace pair for display labels."""
        if len(last) >= 2 and last.startswith("{") and last.endswith("}"):
            return last[1:-1]
        return last

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _position(text: str, offset: int) -> dict[str, int]:
        """Convert a character offset into offset / line / column."""
        offset = max(0, min(offset, len(text)))
        line = text.count("\n", 0, offset) + 1
        column = offset - (text.rfind("\n", 0, offset) + 1) + 1
        return {"offset": offset, "line": line, "column": column}

    @classmethod
    def _error_result(
        cls, mode: str, text: str, exc: _BibtexParseError
    ) -> dict[str, Any]:
        """Build a structured error payload with the failure position."""
        return {
            "mode": mode,
            "error": {
                "type": exc.error_type,
                "message": str(exc.message)[:500],
                "position": cls._position(text, exc.pos),
            },
        }
