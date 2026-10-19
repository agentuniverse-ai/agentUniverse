#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: vcf_tool.py

"""vCard (.vcf) contact parsing tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency reader for vCard
contact data — the contact-management counterpart of the calendar
(iCalendar) side. Contact-centric agents can parse VCARD text, summarize
address books, and search contacts without any third-party package.

The tool supports three modes:

* ``parse`` — parse VCARD text into a list of contact dicts.
  ``BEGIN:VCARD`` / ``END:VCARD`` blocks are located case-insensitively
  and the ``VERSION`` property (2.1 / 3.0 / 4.0) is tracked per
  contact. Supported properties: ``FN``, ``N`` (split on ``;`` into
  family / given / additional / prefix / suffix), ``NICKNAME``, ``ORG``
  (organization;units), ``TITLE``, ``TEL``, ``EMAIL``, ``ADR``
  (7-component split: pobox / ext / street / locality / region /
  postal code / country), ``URL``, ``NOTE``, ``BDAY`` and ``CATEGORIES``
  (comma split). ``TEL`` / ``EMAIL`` / ``ADR`` parameter types accept
  both the bare vCard 2.1 style (``TEL;CELL;PREF:...`` — parameter
  values given without a ``TYPE=`` name prefix) and the 3.0 / 4.0
  style (``TEL;TYPE=CELL:...``, including quoted ``TYPE="CELL,WORK"``
  lists and 4.0 ``PREF=1``). Text value escapes (``\\\\``, ``\\n``,
  ``\\,``, ``\\;``) are unescaped, quoted-printable values
  (``ENCODING=QUOTED-PRINTABLE``, including the bare 2.1 form) are
  decoded to UTF-8, and RFC folded lines (continuations starting with
  a space) — including quoted-printable soft line breaks — are
  unfolded. Unsupported properties are kept in a per-contact ``raw``
  mapping and ``item1.TEL``-style group prefixes are stripped. Scalar
  fields use the first occurrence when a property repeats.
* ``summary`` — address book overview: total count plus, per contact,
  the FN, the phone and email counts, and a missing-FN flag.
* ``filter`` — case-insensitive substring search over the ``FN``,
  ``EMAIL``, ``ORG`` and ``N`` fields, returning the full parsed
  contacts that match together with the fields each one matched on.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, missing / empty / non-string text,
a missing or empty ``filter`` query, oversized text or query,
non-positive caps) raise a ``ValueError``. Failures that depend on the
*content being parsed* — structural BEGIN/END mismatches (an
``END:VCARD`` without an open card, a nested ``BEGIN``, a card that is
never closed, non-VCARD blocks such as ``BEGIN:VCALENDAR``), a property
line without a ``:`` or with an invalid name, text without any VCARD
block, invalid quoted-printable data (bad ``=XX`` escapes or bytes that
are not valid UTF-8), and exceeding the contact cap — are returned as a
structured ``error`` payload so an agent can react without catching
exceptions.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict, StrictInt

from agentuniverse.agent.action.tool.tool import Tool

_HEX_DIGITS = frozenset("0123456789ABCDEFabcdef")
_NEWLINE_RE = re.compile(r"\r\n|\r|\n")
# Property (or group-prefixed property) name, e.g. TEL / X-SOCIAL / item1.TEL.
_PROP_NAME_RE = re.compile(r"\A[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\Z")
# vCard text escapes (RFC 6350 section 3.4): \\ \n \N \, \;
_ESCAPE_MAP = {"n": "\n", "N": "\n", ",": ",", ";": ";", "\\": "\\"}


class _ContentError(Exception):
    """Internal marker for content-level failures turned into error payloads."""

    def __init__(self, error_type: str, message: str) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message


class VcfTool(Tool):
    """vCard contact parsing tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
        max_contacts (int): Upper bound on the number of VCARD blocks
            parsed in one call.
        max_query_chars (int): Upper bound on the ``filter`` query.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "vcf_tool"
    description: str = (
        "vCard contact tool — pure Python stdlib, no network required. "
        "Parse VCARD text into structured contacts (mode='parse': "
        "BEGIN/END:VCARD blocks, vCard 2.1/3.0/4.0, "
        "FN/N/NICKNAME/ORG/TITLE/TEL/EMAIL/ADR/URL/NOTE/BDAY/CATEGORIES, "
        "2.1-style bare and 3.0/4.0 TYPE= parameters, quoted-printable "
        "values, escape sequences and line folding), summarize an "
        "address book with per-contact FN and phone/email counts plus "
        "missing-FN flags (mode='summary'), or filter contacts by "
        "case-insensitive substring over FN/EMAIL/ORG/N fields "
        "(mode='filter')."
    )

    MODES: ClassVar[tuple] = ("parse", "summary", "filter")
    N_KEYS: ClassVar[tuple] = (
        "family", "given", "additional", "prefix", "suffix",
    )
    ADR_KEYS: ClassVar[tuple] = (
        "pobox", "ext", "street", "locality", "region", "postal_code",
        "country",
    )

    max_text_chars: StrictInt = 100_000
    max_contacts: StrictInt = 1_000
    max_query_chars: StrictInt = 256

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        query: Any = None,
    ) -> dict[str, Any]:
        """Run one vCard operation.

        Args:
            mode (str): One of ``parse`` / ``summary`` / ``filter``.
            text (str): The VCARD text (one or more ``BEGIN:VCARD`` ...
                ``END:VCARD`` blocks). Required by every mode.
            query (str): ``filter`` mode only — case-insensitive
                substring matched against the FN / EMAIL / ORG and N
                fields of every parsed contact.

        Returns:
            Dict[str, Any]: ``parse`` — the full contact list;
            ``summary`` — per-contact FN / phone / email counts with
            missing-FN flags; ``filter`` — the matching contacts with
            the fields each match was found in. Content-level failures
            (structural BEGIN/END mismatches, text without any VCARD
            block, invalid quoted-printable data, contact count over
            the cap) are returned as a structured ``error`` payload.

        Raises:
            ValueError: If any parameter is malformed (before any
                parsing happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        self._validate_caps()
        clean_text = self._validate_text(text)
        clean_query = self._validate_query(mode, query)
        try:
            contacts = self._parse_contacts(clean_text)
        except _ContentError as exc:
            return self._error_result(
                {"mode": mode}, exc.error_type, exc.message
            )
        if mode == "parse":
            return {
                "mode": "parse",
                "count": len(contacts),
                "contacts": contacts,
            }
        if mode == "summary":
            return self._summarize(contacts)
        return self._filter(contacts, clean_query)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any parsing)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"vcf_tool: {message}")

    def _validate_caps(self) -> None:
        """Validate the configurable bounds are positive integers."""
        for field_name in ("max_text_chars", "max_contacts", "max_query_chars"):
            value = getattr(self, field_name)
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value <= 0
            ):
                self._invalid(
                    f"{field_name} must be a positive integer (got {value!r})"
                )

    def _validate_text(self, text: Any) -> str:
        """Validate the ``text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"text must be a non-empty VCARD string (got {text!r})")
        if not text:
            self._invalid("text must be a non-empty VCARD string (got '')")
        if len(text) > self.max_text_chars:
            self._invalid(
                f"text exceeds the {self.max_text_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    def _validate_query(self, mode: str, query: Any) -> Any:
        """Validate the ``query`` input (only meaningful for filtering)."""
        if mode != "filter":
            if query is not None:
                self._invalid("query is only accepted in filter mode")
            return None
        if (
            query is None
            or isinstance(query, bool)
            or not isinstance(query, str)
        ):
            self._invalid(
                f"query must be a non-empty string in filter mode (got {query!r})"
            )
        if not query:
            self._invalid("query must be a non-empty string in filter mode (got '')")
        if len(query) > self.max_query_chars:
            self._invalid(
                f"query exceeds the {self.max_query_chars:,}-character limit "
                f"(got {len(query):,} characters)"
            )
        return query

    # ------------------------------------------------------------------ #
    # Parsing pipeline: unfold -> split blocks -> parse properties
    # ------------------------------------------------------------------ #

    def _parse_contacts(self, text: str) -> list[dict[str, Any]]:
        """Parse VCARD text into contact dicts (raises ``_ContentError``)."""
        logical = self._logical_lines(text)
        blocks = self._split_blocks(logical)
        return [
            self._parse_block(index, lines)
            for index, lines in enumerate(blocks, start=1)
        ]

    @staticmethod
    def _logical_lines(text: str) -> list[str]:
        """Split into logical lines, unfolding continuations.

        RFC 6350 folding: a physical line starting with a space (or
        tab) continues the previous line; the leading whitespace
        character itself is removed. Quoted-printable soft line breaks:
        when the previous line carries a ``QUOTED-PRINTABLE`` parameter
        and ends with ``=``, the ``=`` is dropped and the next physical
        line (which starts in column zero) is appended directly.
        """
        logical: list[str] = []
        for line in _NEWLINE_RE.split(text):
            if not logical:
                logical.append(line)
            elif line.startswith((" ", "\t")):
                logical[-1] += line[1:]
            elif (
                VcfTool._is_qp_line(logical[-1]) and logical[-1].endswith("=")
            ):
                logical[-1] = logical[-1][:-1] + line
            else:
                logical.append(line)
        return logical

    @staticmethod
    def _is_qp_line(line: str) -> bool:
        """Return True when the line's parameter head declares QP encoding."""
        head = line.split(":", 1)[0]
        return "QUOTED-PRINTABLE" in head.upper()

    def _split_blocks(self, lines: list[str]) -> list[list[str]]:
        """Group logical lines into per-VCARD property-line lists.

        Non-empty lines outside any VCARD block (a preamble between
        cards) are ignored; structural anomalies — a nested ``BEGIN``,
        an ``END`` without an open card, a non-VCARD block such as
        ``BEGIN:VCALENDAR``, a card that is never closed, and an input
        without any card — raise ``_ContentError``.
        """
        blocks: list[list[str]] = []
        current: list[str] | None = None
        for line in lines:
            if not line.strip():
                continue
            marker = self._block_marker(line)
            if marker is None:
                if current is not None:
                    current.append(line)
                continue
            kind, value = marker
            block = value.strip().upper()
            if kind == "BEGIN":
                if current is not None:
                    raise _ContentError(
                        "malformed_vcard",
                        f"nested BEGIN:{block} inside an unclosed VCARD block",
                    )
                if block != "VCARD":
                    raise _ContentError(
                        "malformed_vcard",
                        f"only BEGIN:VCARD blocks are supported "
                        f"(got BEGIN:{value.strip()!r})",
                    )
                current = []
            else:
                if current is None:
                    raise _ContentError(
                        "malformed_vcard",
                        f"END:{block} without an open BEGIN:VCARD block",
                    )
                if block != "VCARD":
                    raise _ContentError(
                        "malformed_vcard",
                        f"only END:VCARD closes a card (got END:{value.strip()!r})",
                    )
                blocks.append(current)
                current = None
        if current is not None:
            raise _ContentError(
                "malformed_vcard",
                "unterminated VCARD block: END:VCARD is missing before "
                "the end of the input",
            )
        if not blocks:
            raise _ContentError(
                "no_vcard_blocks",
                "the text does not contain any BEGIN:VCARD block",
            )
        if len(blocks) > self.max_contacts:
            raise _ContentError(
                "too_many_contacts",
                f"input contains {len(blocks)} contacts which exceeds the "
                f"{self.max_contacts:,}-contact limit",
            )
        return blocks

    def _block_marker(self, line: str) -> tuple[str, str] | None:
        """Return ("BEGIN"|"END", value) for block marker lines, else None."""
        split = self._split_content_line(line)
        if split is None:
            return None
        name, value = split
        upper = name.upper()
        if upper in ("BEGIN", "END"):
            return upper, value
        return None

    @staticmethod
    def _split_content_line(line: str) -> tuple[str, str] | None:
        """Split ``NAME[;PARAM]:VALUE`` at the first unquoted colon."""
        in_quotes = False
        for idx, char in enumerate(line):
            if char == '"':
                in_quotes = not in_quotes
            elif char == ":" and not in_quotes:
                return line[:idx], line[idx + 1:]
        return None

    def _parse_block(self, index: int, lines: list[str]) -> dict[str, Any]:
        """Parse one VCARD block's property lines into a contact dict."""
        contact: dict[str, Any] = {
            "index": index,
            "version": None,
            "fn": None,
            "n": None,
            "nickname": None,
            "org": None,
            "title": None,
            "tel": [],
            "email": [],
            "adr": [],
            "url": None,
            "note": None,
            "bday": None,
            "categories": [],
            "raw": {},
        }
        for line in lines:
            split = self._split_content_line(line)
            if split is None:
                raise _ContentError(
                    "malformed_vcard",
                    "invalid property line (expected 'NAME[;PARAM]:value'): "
                    f"{self._preview(line)}",
                )
            head, value = split
            name = head.split(";", 1)[0]
            name = name.rsplit(".", 1)[-1]  # strip item1.-style group prefixes
            if not _PROP_NAME_RE.match(name):
                raise _ContentError(
                    "malformed_vcard",
                    "invalid property line (expected 'NAME[;PARAM]:value'): "
                    f"{self._preview(line)}",
                )
            name = name.upper()
            types, qp = self._parse_params(head)
            if qp:
                value = self._decode_qp(value)

            if name == "VERSION":
                if contact["version"] is None:
                    contact["version"] = self._unescape(value.strip())
            elif name == "FN":
                if contact["fn"] is None:
                    contact["fn"] = self._unescape(value)
            elif name == "N":
                if contact["n"] is None:
                    contact["n"] = self._structured_split(value, self.N_KEYS)
            elif name == "NICKNAME":
                if contact["nickname"] is None:
                    contact["nickname"] = self._unescape(value)
            elif name == "ORG":
                if contact["org"] is None:
                    parts = self._split_unescaped(value, ";")
                    contact["org"] = {
                        "name": self._unescape(parts[0]) if parts else "",
                        "units": [self._unescape(p) for p in parts[1:]],
                    }
            elif name == "TITLE":
                if contact["title"] is None:
                    contact["title"] = self._unescape(value)
            elif name == "TEL":
                contact["tel"].append(
                    {"value": self._unescape(value), "types": self._dedupe(types)}
                )
            elif name == "EMAIL":
                contact["email"].append(
                    {"value": self._unescape(value), "types": self._dedupe(types)}
                )
            elif name == "ADR":
                entry = self._structured_split(value, self.ADR_KEYS)
                entry["types"] = self._dedupe(types)
                contact["adr"].append(entry)
            elif name == "URL":
                if contact["url"] is None:
                    contact["url"] = self._unescape(value)
            elif name == "NOTE":
                if contact["note"] is None:
                    contact["note"] = self._unescape(value)
            elif name == "BDAY":
                if contact["bday"] is None:
                    contact["bday"] = self._unescape(value)
            elif name == "CATEGORIES":
                contact["categories"].extend(
                    self._unescape(p) for p in self._split_unescaped(value, ",")
                )
            else:
                contact["raw"].setdefault(name, []).append(self._unescape(value))
        return contact

    @staticmethod
    def _parse_params(head: str) -> tuple[list[str], bool]:
        """Extract (types, quoted_printable) from a content-line head.

        Accepts ``KEY=VALUE`` parameters (3.0/4.0 style, values possibly
        quoted or comma-separated) and bare value tokens (2.1 style —
        an implied ``TYPE=``; a bare ``QUOTED-PRINTABLE`` marks the
        value encoding). Parameter keys other than ``TYPE`` / ``PREF``
        (e.g. ``CHARSET``, ``VALUE``, ``LABEL``, ``LANGUAGE``) are
        recognized but not turned into types.
        """
        types: list[str] = []
        qp = False
        in_quotes = False
        params: list[str] = []
        buf: list[str] = []
        for char in head:
            if char == '"':
                in_quotes = not in_quotes
                buf.append(char)
            elif char == ";" and not in_quotes:
                params.append("".join(buf))
                buf = []
            else:
                buf.append(char)
        params.append("".join(buf))

        for param in params[1:]:
            token = param.strip()
            if not token:
                continue
            key, eq, raw_value = token.partition("=")
            if not eq:
                if token.upper() == "QUOTED-PRINTABLE":
                    qp = True
                else:
                    types.append(token.upper())
                continue
            key_upper = key.strip().upper()
            if key_upper == "TYPE":
                for value in VcfTool._param_values(raw_value):
                    types.append(value.upper())
            elif key_upper == "ENCODING":
                if any(
                    "QUOTED-PRINTABLE" in value.upper()
                    for value in VcfTool._param_values(raw_value)
                ):
                    qp = True
            elif key_upper == "PREF":
                types.append("PREF")
        return types, qp

    @staticmethod
    def _param_values(raw: str) -> list[str]:
        """Split one parameter value on commas, dropping empty parts."""
        raw = raw.strip()
        if len(raw) >= 2 and raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        return [part.strip() for part in raw.split(",") if part.strip()]

    # ------------------------------------------------------------------ #
    # Value decoding helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _split_unescaped(value: str, separator: str) -> list[str]:
        """Split on a separator, keeping ``\\X`` escape pairs intact."""
        parts: list[str] = []
        buf: list[str] = []
        idx = 0
        length = len(value)
        while idx < length:
            char = value[idx]
            if char == "\\" and idx + 1 < length:
                buf.append(value[idx:idx + 2])
                idx += 2
            elif char == separator:
                parts.append("".join(buf))
                buf = []
                idx += 1
            else:
                buf.append(char)
                idx += 1
        parts.append("".join(buf))
        return parts

    @staticmethod
    def _unescape(text: str) -> str:
        """Resolve ``\\\\``, ``\\n`` / ``\\N``, ``\\,`` and ``\\;`` escapes."""
        out: list[str] = []
        idx = 0
        length = len(text)
        while idx < length:
            char = text[idx]
            if char == "\\" and idx + 1 < length and text[idx + 1] in _ESCAPE_MAP:
                out.append(_ESCAPE_MAP[text[idx + 1]])
                idx += 2
            else:
                out.append(char)
                idx += 1
        return "".join(out)

    def _structured_split(
        self, value: str, keys: tuple[str, ...]
    ) -> dict[str, Any]:
        """Split an N/ADR value on unescaped ``;`` into a fixed-key dict."""
        parts = [self._unescape(p) for p in self._split_unescaped(value, ";")]
        padded = (parts + [""] * len(keys))[: len(keys)]
        return dict(zip(keys, padded))

    def _decode_qp(self, value: str) -> str:
        """Decode a quoted-printable value to UTF-8, per ``=XX`` escape."""
        if "=" not in value:
            return value
        raw = bytearray()
        idx = 0
        length = len(value)
        while idx < length:
            char = value[idx]
            if char == "=":
                escape = value[idx + 1:idx + 3]
                if (
                    len(escape) == 2
                    and escape[0] in _HEX_DIGITS
                    and escape[1] in _HEX_DIGITS
                ):
                    raw.append(int(escape, 16))
                    idx += 3
                else:
                    raise _ContentError(
                        "invalid_quoted_printable",
                        "quoted-printable value has a dangling or malformed "
                        f"'=' escape: {self._preview(value)}",
                    )
            else:
                raw.extend(char.encode("utf-8"))
                idx += 1
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            raise _ContentError(
                "invalid_quoted_printable",
                "quoted-printable value decodes to bytes that are not "
                "valid UTF-8 text",
            ) from None

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        """Drop duplicate type tokens, preserving first-seen order."""
        seen: list[str] = []
        for item in items:
            if item and item not in seen:
                seen.append(item)
        return seen

    @staticmethod
    def _preview(text: str) -> str:
        """Short quoted preview for error messages."""
        snippet = text[:80]
        suffix = "..." if len(text) > 80 else ""
        return f"{snippet!r}{suffix}"

    # ------------------------------------------------------------------ #
    # summary / filter modes
    # ------------------------------------------------------------------ #

    def _summarize(self, contacts: list[dict[str, Any]]) -> dict[str, Any]:
        """Build the address book overview."""
        entries: list[dict[str, Any]] = []
        missing = 0
        for contact in contacts:
            fn = contact["fn"]
            fn_missing = fn is None or not fn.strip()
            if fn_missing:
                missing += 1
            entries.append(
                {
                    "index": contact["index"],
                    "fn": fn,
                    "phones": len(contact["tel"]),
                    "emails": len(contact["email"]),
                    "missing_fn": fn_missing,
                }
            )
        return {
            "mode": "summary",
            "count": len(contacts),
            "missing_fn_count": missing,
            "contacts": entries,
        }

    def _filter(
        self, contacts: list[dict[str, Any]], query: str
    ) -> dict[str, Any]:
        """Case-insensitive substring search over FN/EMAIL/ORG/N fields."""
        needle = query.lower()
        matched: list[dict[str, Any]] = []
        for contact in contacts:
            fields: list[str] = []
            fn = contact["fn"]
            if fn and needle in fn.lower():
                fields.append("fn")
            if any(
                needle in item["value"].lower() for item in contact["email"]
            ):
                fields.append("email")
            org = contact["org"]
            if org is not None and (
                needle in org["name"].lower()
                or any(needle in unit.lower() for unit in org["units"])
            ):
                fields.append("org")
            structured_name = contact["n"]
            if structured_name is not None and any(
                needle in structured_name[key].lower() for key in self.N_KEYS
            ):
                fields.append("n")
            if fields:
                matched.append({**contact, "matched_fields": fields})
        return {
            "mode": "filter",
            "query": query,
            "count": len(matched),
            "contacts": matched,
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: dict[str, Any], error_type: str, message: str
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
