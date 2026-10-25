#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: phone_format_tool.py

"""Phone number normalization tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency phone formatter
agents can call before storing, deduplicating or displaying contact
data.  It is deliberately **not** a port of Google's libphonenumber:
the honest subset implemented here is table-driven dial-code lookup
plus shape heuristics, and its limits are documented below.

Supported modes:

* ``format`` — normalize one phone number to a canonical form, with
  three output variants selected by ``output``:

  - ``e164`` (default) — ``+8613812345678`` style canonical form.
  - ``display`` — E.164 with spaces: a space between the dial code
    and the subscriber digits, plus two documented groupings (NANP
    3-3-4 and China-mobile 3-4-4).  Everything else keeps the
    subscriber digits as one block — real per-country pretty
    printing is out of scope.
  - ``national`` — the domestic form implied by the region table:
    the dial code replaced by the region's national (trunk) prefix.
    China mobile numbers are emitted without the trunk ``0``
    because they are dialed that way domestically.

  Input handling, in order:

  1. Separators (spaces, dashes, dots, parentheses) are stripped.
     Any other character outside digits and a single leading ``+``
     — letters included — is rejected.
  2. A leading ``+`` marks an already-international number: it is
     validated against the ITU E.164 bound of 7-15 digits and
     returned unchanged (an explicit ``default_region`` is *not*
     applied — no region rewrite).
  3. A leading ``00`` (international dialing prefix) is replaced
     with ``+`` and treated like case 2.
  4. Otherwise the ``default_region`` is required.  If the digits
     start with the region's national (trunk) prefix from the
     table, one occurrence is stripped.  If they already start
     with the region's dial code, it is not prepended twice.
     The dial code is then prepended.
  5. ``+1`` (NANP) numbers must carry exactly 10 digits after the
     code, and both the area code (NPA) and the exchange code (NXX)
     must start with 2-9 (the classic ``[2-9]XX`` rule) — the one
     region-specific family of rules enforced beyond length.

* ``classify`` — inspect an already-international number
  (``+``/``00`` form only): region guess from the table via
  longest-prefix match (so ``+1 264 …`` resolves to Anguilla while
  a plain ``+1`` resolves to the shared ``US/CA`` code), digit
  count checked against the loose ITU E.164 bounds of 7-15, and a
  documented China-mobile structural heuristic (``13x``-``19x``,
  11 subscriber digits after ``86``).

* ``extract`` — find phone-shaped substrings in free text and
  format each of them.  Candidate shapes reuse the
  PIIReporter-family heuristics (international ``+`` forms with or
  without separators, China mobile ``1[3-9]`` runs, North-American
  3-3-4 shapes, and general separated digit runs of 7-15 digits),
  guarded against dates (``2023-01-15``, ``01/15/2023``) and
  arithmetic context (``3 +86 …``, ``= 44 123 456 7890``).  Bare
  candidates are formatted with ``default_region`` when given,
  otherwise with the shape-implied region: a contiguous 11-digit
  ``1[3-9]…`` run or a separated span whose leading group is the
  3-digit ``13x``-``19x`` prefix implies China mobile, while other
  10-digit or ``1``-prefixed 11-digit spans imply the NANP ``US``
  default (so ``1-415-555-2671`` is never mistaken for a CN number,
  and vice versa); candidates that cannot be resolved are returned
  per-item as structured errors.  Loose separated digit
  runs that are neither dates nor arithmetic may still surface
  (order numbers, amounts) — extraction is deliberately
  conservative-but-not-exact and reports what it formatted.

Honest-subset notes (what this tool does NOT do): no per-number
type assignment beyond the documented China-mobile heuristic, no
libphonenumber metadata (validity is the loose 7-15 digit bound
plus the NANP 10-digit / leading-2-9 rules), no extension suffixes
(``x123``),
and no carrier/line-type lookups.  National trunk prefixes are a
single table column: real-world exceptions (Italian mobiles carry
no trunk ``0`` in E.164, Mexico removed its ``01`` trunk in 2019,
Spain has no trunk) are encoded in the table where settled, and
the table is small and documented on purpose.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode / output, wrong ``phone`` /
``text`` / ``default_region`` types, empty phone, oversized
inputs) raise a ``ValueError``, mirroring the other common tools.
Failures that depend on the *content being processed* — letters in
the number, digit counts outside the E.164 bounds, NANP length
violations, a missing or unknown region for a national number, an
unknown dial code for the ``national`` output, or a
non-international input to ``classify`` — are returned as a
structured ``error`` payload so an agent can react without
catching exceptions.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Characters allowed between digits of a phone number.
_SEPARATORS = " -.()"
_PHONE_BODY_RE = re.compile(r"\A[0-9" + re.escape(_SEPARATORS) + r"]+\Z")
_DIGITS_RE = re.compile(r"\A[0-9]+\Z")
_BAD_CHARS_RE = re.compile(r"[^0-9" + re.escape(_SEPARATORS) + r"]")

# China mobile shape: 11 subscriber digits starting 1[3-9]. Used as a
# documented structural heuristic (never as a validity guarantee).
_CN_MOBILE_RE = re.compile(r"\A1[3-9]\d{9}\Z")

# ITU-T E.164 loose digit-count bounds (country code included).
_MIN_DIGITS = 7
_MAX_DIGITS = 15

# NANP numbering rule: both the area code (NPA) and the exchange
# code (NXX) must start with 2-9 — codes starting 0/1 are reserved.
_NANP_FIRST_DIGITS = frozenset("23456789")


class PhoneFormatTool(Tool):
    """Phone number normalization tool built purely on the stdlib.

    Attributes:
        max_phone_chars (int): Upper bound on the ``phone`` input
            length; longer inputs are rejected before any work.
        max_text_chars (int): Upper bound on the ``text`` input of
            the extract mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "phone_format_tool"
    description: str = (
        "Phone format tool — pure Python stdlib, no network required. "
        "Normalize one number to E.164 (+8613812345678), a spaced "
        "display variant (+86 138 1234 5678) or the domestic national "
        "form via a documented ~20-region dial-code table "
        "(mode='format'), classify an international number's region "
        "with longest-prefix matching and loose ITU E.164 bounds "
        "(mode='classify'), or extract phone-shaped substrings from "
        "free text with date/arithmetic guards and format each of "
        "them (mode='extract')."
    )

    MODES: ClassVar[tuple] = ("format", "classify", "extract")
    OUTPUTS: ClassVar[tuple] = ("e164", "display", "national")

    # ------------------------------------------------------------------ #
    # Region table (dial code → regions, national trunk prefix)
    # ------------------------------------------------------------------ #
    # Honest subset: ~20 dial codes.  Trunk prefixes are the settled
    # modern values: NANP regions and Hong Kong / Singapore / Mexico /
    # Spain have none; Russia/Kazakhstan dial 8 domestically; the rest
    # of the table uses 0.  Known exceptions (e.g. Italian mobile
    # numbers keep no trunk 0 in E.164) are documented, not modeled.
    DIAL_CODES: ClassVar[dict[str, Any]] = {
        "1": {"regions": ("US", "CA"), "trunk": ""},
        "7": {"regions": ("RU", "KZ"), "trunk": "8"},
        "44": {"regions": ("GB",), "trunk": "0"},
        "49": {"regions": ("DE",), "trunk": "0"},
        "33": {"regions": ("FR",), "trunk": "0"},
        "39": {"regions": ("IT",), "trunk": "0"},
        "34": {"regions": ("ES",), "trunk": ""},
        "55": {"regions": ("BR",), "trunk": "0"},
        "52": {"regions": ("MX",), "trunk": ""},
        "91": {"regions": ("IN",), "trunk": "0"},
        "81": {"regions": ("JP",), "trunk": "0"},
        "82": {"regions": ("KR",), "trunk": "0"},
        "86": {"regions": ("CN",), "trunk": "0"},
        "852": {"regions": ("HK",), "trunk": ""},
        "65": {"regions": ("SG",), "trunk": ""},
        "61": {"regions": ("AU",), "trunk": "0"},
        "64": {"regions": ("NZ",), "trunk": "0"},
        "972": {"regions": ("IL",), "trunk": "0"},
        "971": {"regions": ("AE",), "trunk": "0"},
        "90": {"regions": ("TR",), "trunk": "0"},
    }

    # Extended classify prefixes for the longest-prefix demonstration:
    # NANP participating countries whose +1 area codes identify a
    # specific country, unlike the shared bare +1 (US/CA).
    EXTENDED_PREFIXES: ClassVar[dict[str, str]] = {
        "1264": "AI",   # Anguilla
        "1268": "AG",   # Antigua and Barbuda
        "1242": "BS",   # Bahamas
        "1246": "BB",   # Barbados
        "1441": "BM",   # Bermuda
        "1284": "VG",   # British Virgin Islands
        "1345": "KY",   # Cayman Islands
        "1767": "DM",   # Dominica
        "1473": "GD",   # Grenada
        "1671": "GU",   # Guam
        "1876": "JM",   # Jamaica
        "1809": "DO",   # Dominican Republic (overlays 1829/1849 share it)
        "1829": "DO",
        "1849": "DO",
        "1664": "MS",   # Montserrat
        "1787": "PR",   # Puerto Rico (overlay 1939 shares the region)
        "1939": "PR",
        "1758": "LC",   # Saint Lucia
        "1784": "VC",   # Saint Vincent and the Grenadines
        "1868": "TT",   # Trinidad and Tobago
        "1649": "TC",   # Turks and Caicos
        "1340": "VI",   # U.S. Virgin Islands
        "1684": "AS",   # American Samoa
        "1721": "SX",   # Sint Maarten
    }

    max_phone_chars: int = 64
    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Candidate shapes for the extract mode (PIIReporter family)
    # ------------------------------------------------------------------ #
    _EXTRACT_RES: ClassVar[list] = [
        # International with explicit country code and separators. The
        # final group may be one wide unpunctuated subscriber block
        # (e.g. the tool's own display form '+44 2079460958'), so any
        # group after the dial code may run beyond the classic 2-4.
        re.compile(r"\+\d{1,3}(?:[\s.-]\d{1,14}){1,6}(?!\d)"),
        # International contiguous (11-15 digits).
        re.compile(r"\+\d{11,15}(?!\d)"),
        # China mobile run.
        re.compile(r"\b1[3-9]\d{9}(?!\d)"),
        # North-American (415) 555-2671 shapes.
        re.compile(r"\(\d{3}\)[\s.]?\d{3}[\s.-]\d{4}(?!\d)"),
        # North-American 3-3-4 with separators, optional leading 1-.
        re.compile(r"(?<![\d(])(?:1[\s.-])?\d{3}[\s.-]\d{3}[\s.-]\d{4}(?!\d)"),
        # General separated digit run (7-15 digits after stripping),
        # with optional international + or 00 prefix; the final group
        # may be a wide unpunctuated block ('030 1234567').
        re.compile(r"(?<!\d)(?:\+|00)?\d{1,4}(?:[ .-]\d{1,4}){0,5}[ .-]\d{1,14}(?!\d)"),
    ]

    # Guards against calendar and arithmetic context (PIIReporter family).
    _DATE_RES: ClassVar[list] = [
        re.compile(r"\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b"),
        re.compile(r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{4}\b"),
    ]
    _ARITH_OPERAND_BEFORE = re.compile(r"(?:\d|\))\s*$")
    _ARITH_ASSIGN_BEFORE = re.compile(r"=\s*[\d\s]*$")
    _ARITH_AFTER = re.compile(r"^\s*[=+]\s*\d")

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        phone: Any = None,
        text: Any = None,
        default_region: Any = None,
        output: Any = None,
    ) -> dict[str, Any]:
        """Run one phone formatting operation.

        Args:
            mode (str): One of ``format`` / ``classify`` / ``extract``.
            phone (str): The phone number for the ``format`` and
                ``classify`` modes (separators — spaces, dashes, dots,
                parentheses — are stripped).
            text (str): The text to scan for the ``extract`` mode.
            default_region (str): Two-letter region code (``CN``, ``GB``,
                ``US``, …) used to interpret national/bare input in
                ``format`` and bare candidates in ``extract``.  Ignored
                for numbers that already carry ``+`` / ``00``.
            output (str): ``format`` only — ``e164`` (default),
                ``display`` or ``national``.

        Returns:
            Dict[str, Any]: The operation result (a ``result`` key plus
                the call context) or a structured ``error`` payload for
                content-level failures.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_region = self._validate_region_param(default_region)
        if mode == "format":
            clean_phone = self._validate_phone(phone)
            clean_output = self._validate_output(output)
            return self._run_format(clean_phone, clean_region, clean_output)
        if mode == "classify":
            clean_phone = self._validate_phone(phone)
            return self._run_classify(clean_phone)
        clean_text = self._validate_text(text)
        return self._run_extract(clean_text, clean_region)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"phone_format_tool: {message}")

    @classmethod
    def _validate_phone(cls, phone: Any) -> str:
        """Validate the ``phone`` input (format / classify modes)."""
        if phone is None or isinstance(phone, bool) or not isinstance(phone, str):
            cls._invalid(f"phone must be a non-empty string (got {phone!r})")
        phone = phone.strip()
        if not phone:
            cls._invalid("phone must be a non-empty string (got '')")
        if len(phone) > 64:
            cls._invalid(
                f"phone exceeds the 64-character limit "
                f"(got {len(phone)} characters)"
            )
        return phone

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input (extract mode)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_region_param(cls, region: Any) -> Any:
        """Validate the ``default_region`` parameter type (not membership)."""
        if region is None:
            return None
        if isinstance(region, bool) or not isinstance(region, str):
            cls._invalid(
                f"default_region must be a two-letter region code or None "
                f"(got {region!r})"
            )
        return region.strip().upper() or None

    @classmethod
    def _validate_output(cls, output: Any) -> str:
        """Validate the ``output`` selector of the format mode."""
        if output is None:
            return "e164"
        if output not in cls.OUTPUTS:
            cls._invalid(
                "output must be one of: "
                f"{', '.join(cls.OUTPUTS)} (got {output!r})"
            )
        return output

    # ------------------------------------------------------------------ #
    # Shared normalization helpers
    # ------------------------------------------------------------------ #

    def _clean_digits(self, phone: str) -> tuple:
        """Strip separators; split off a leading ``+`` or ``00``.

        Returns ``(digits, had_plus, had_double_zero)`` or ``None``
        when the input contains characters outside digits, the
        separator set and a single leading ``+`` — the caller converts
        ``None`` into a structured error payload.
        """
        compact = phone.strip()
        if not compact:
            return None
        had_plus = compact.startswith("+")
        if had_plus:
            compact = compact[1:]
        if not _PHONE_BODY_RE.match(compact):
            return None
        digits = compact
        for char in _SEPARATORS:
            digits = digits.replace(char, "")
        had_double_zero = False
        if not had_plus and digits.startswith("00"):
            digits = digits[2:]
            had_double_zero = True
        if not digits or not _DIGITS_RE.match(digits):
            return None
        return digits, had_plus, had_double_zero

    def _region_entry(self, region: str) -> dict:
        """Table entry for a two-letter region code, or ``None``."""
        for code, entry in self.DIAL_CODES.items():
            if entry and region in entry["regions"]:
                return {"dial_code": code, **entry}
        return None

    # ------------------------------------------------------------------ #
    # format mode
    # ------------------------------------------------------------------ #

    def _run_format(
        self, phone: str, region: Any, output: str
    ) -> dict[str, Any]:
        """Normalize one number to the requested output form."""
        context: dict[str, Any] = {
            "mode": "format",
            "output": output,
            "default_region": region,
        }
        cleaned = self._clean_digits(phone)
        if cleaned is None:
            return self._error_result(
                context,
                error_type="invalid_characters",
                message=(
                    "phone may only contain digits, the separators "
                    "space/dash/dot/parentheses and a single leading '+' "
                    f"(got {phone[:64]!r})"
                ),
            )
        digits, had_plus, had_double_zero = cleaned

        if had_plus or had_double_zero:
            # Already international: validate only, never rewrite the
            # region even when default_region was supplied.
            intl = digits
        else:
            if not region:
                return self._error_result(
                    context,
                    error_type="region_required",
                    message=(
                        "a national or bare number requires default_region "
                        "(one of: "
                        f"{self._region_codes_label()}); supply it or prefix "
                        "the number with '+' / '00'"
                    ),
                )
            entry = self._region_entry(region)
            if entry is None:
                return self._error_result(
                    context,
                    error_type="unknown_region",
                    message=(
                        f"default_region {region!r} is not in the dial-code "
                        f"table; supported regions: "
                        f"{self._region_codes_label()}"
                    ),
                )
            dial_code = entry["dial_code"]
            trunk = entry["trunk"]
            body = digits
            if trunk and body.startswith(trunk):
                # One national (trunk) prefix, e.g. CN '0371…' / GB
                # '020…' → significant number.
                body = body[len(trunk):]
            if body.startswith(dial_code):
                # Bare input already carrying its dial code, e.g. US
                # '1-415-555-2671' — never prepend twice.
                body = body[len(dial_code):]
            intl = dial_code + body

        if not _DIGITS_RE.match(intl) or not (
            _MIN_DIGITS <= len(intl) <= _MAX_DIGITS
        ):
            return self._error_result(
                context,
                error_type="invalid_length",
                message=(
                    "E.164 numbers must carry "
                    f"{_MIN_DIGITS}-{_MAX_DIGITS} digits "
                    f"(got {len(intl)}: {'+' + intl if intl else phone!r})"
                ),
            )
        if intl.startswith("1") and len(intl) != 11:
            return self._error_result(
                context,
                error_type="invalid_nanp",
                message=(
                    "+1 (NANP) numbers must carry exactly 10 digits after "
                    f"the code (got {len(intl) - 1}: +{intl})"
                ),
            )
        if intl.startswith("1"):
            # Classic NANP numbering: both the area code (NPA) and the
            # exchange code (NXX) start with 2-9; leading 0/1 is
            # reserved and never valid in an assigned number.
            area_code, exchange_code = intl[1:4], intl[4:7]
            if (
                area_code[0] not in _NANP_FIRST_DIGITS
                or exchange_code[0] not in _NANP_FIRST_DIGITS
            ):
                return self._error_result(
                    context,
                    error_type="invalid_nanp",
                    message=(
                        "+1 (NANP) area and exchange codes must start with "
                        f"2-9 (got area code {area_code!r} and exchange "
                        f"{exchange_code!r} in +{intl})"
                    ),
                )

        e164 = "+" + intl
        if output == "display":
            result = self._display_form(intl)
        elif output == "national":
            national = self._national_form(intl)
            if national is None:
                return self._error_result(
                    context,
                    error_type="unknown_dial_code",
                    message=(
                        "the national output needs the number's dial code in "
                        f"the table (got +{intl}); supported: "
                        f"{self._dial_codes_label()}"
                    ),
                )
            result = national
        else:
            result = e164
        return {
            **context,
            "input_digits": intl,
            "e164": e164,
            "result": result,
        }

    def _display_form(self, intl: str) -> str:
        """E.164-with-spaces display variant (documented groupings)."""
        if intl.startswith("1") and len(intl) == 11:
            subscriber = intl[1:]
            return f"+1 {subscriber[:3]} {subscriber[3:6]} {subscriber[6:]}"
        if (
            intl.startswith("86")
            and len(intl) == 13
            and _CN_MOBILE_RE.match(intl[2:])
        ):
            subscriber = intl[2:]
            return f"+86 {subscriber[:3]} {subscriber[3:7]} {subscriber[7:]}"
        for length in (3, 2, 1):
            if len(intl) > length and self.DIAL_CODES.get(intl[:length]):
                return f"+{intl[:length]} {intl[length:]}"
        return f"+{intl}"

    def _national_form(self, intl: str) -> Any:
        """Domestic form implied by the table, or ``None`` when unknown."""
        for length in (3, 2, 1):
            code = intl[:length]
            entry = self.DIAL_CODES.get(code)
            if entry and len(intl) > length:
                subscriber = intl[length:]
                if (
                    code == "86"
                    and len(intl) == 13
                    and _CN_MOBILE_RE.match(subscriber)
                ):
                    # China mobile numbers are dialed domestically
                    # without the trunk 0.
                    return subscriber
                return entry["trunk"] + subscriber
        return None

    # ------------------------------------------------------------------ #
    # classify mode
    # ------------------------------------------------------------------ #

    def _run_classify(self, phone: str) -> dict[str, Any]:
        """Region guess + loose E.164 bounds for an international number."""
        context: dict[str, Any] = {"mode": "classify"}
        cleaned = self._clean_digits(phone)
        if cleaned is None:
            return self._error_result(
                context,
                error_type="invalid_characters",
                message=(
                    "phone may only contain digits, the separators "
                    "space/dash/dot/parentheses and a single leading '+' "
                    f"(got {phone[:64]!r})"
                ),
            )
        digits, had_plus, had_double_zero = cleaned
        if not (had_plus or had_double_zero):
            return self._error_result(
                context,
                error_type="not_international",
                message=(
                    "classify expects an international number (leading '+' "
                    "or '00'); use the format mode to normalize a national "
                    "number first"
                ),
            )
        matched_prefix: Any = None
        region_guess: Any = None
        # Longest-prefix match: extended +1 area codes (4 digits) beat
        # the shared '1' (US/CA).
        for length in (4, 3, 2, 1):
            prefix = digits[:length]
            if prefix in self.EXTENDED_PREFIXES:
                matched_prefix = prefix
                region_guess = self.EXTENDED_PREFIXES[prefix]
                break
            entry = self.DIAL_CODES.get(prefix)
            if entry and len(digits) > length:
                matched_prefix = prefix
                region_guess = "/".join(entry["regions"])
                break
        subscriber_is_cn_mobile = (
            digits.startswith("86")
            and len(digits) == 13
            and _CN_MOBILE_RE.match(digits[2:]) is not None
        )
        digit_count = len(digits)
        return {
            **context,
            "result": "+" + digits,
            "e164": "+" + digits,
            "region_guess": region_guess,
            "matched_prefix": matched_prefix,
            "digit_count": digit_count,
            "digit_count_valid": _MIN_DIGITS <= digit_count <= _MAX_DIGITS,
            "cn_mobile_heuristic": subscriber_is_cn_mobile,
        }

    # ------------------------------------------------------------------ #
    # extract mode
    # ------------------------------------------------------------------ #

    def _run_extract(self, text: str, region: Any) -> dict[str, Any]:
        """Find phone-shaped spans and format each of them."""
        context: dict[str, Any] = {
            "mode": "extract",
            "default_region": region,
        }
        date_spans: list = []
        for pattern in self._DATE_RES:
            for match in pattern.finditer(text):
                date_spans.append((match.start(), match.end()))

        candidates: list = []
        for pattern in self._EXTRACT_RES:
            for match in pattern.finditer(text):
                candidates.append((match.start(), match.end(), match.group(0)))
        # Deduplicate overlaps: earliest start, then longest span.
        candidates.sort(key=lambda item: (item[0], -(item[1] - item[0])))
        kept: list = []
        for start, end, raw in candidates:
            if any(start < ke and ks < end for ks, ke, _ in kept):
                continue
            kept.append((start, end, raw))
        kept.sort(key=lambda item: item[0])

        phones: list = []
        for start, end, raw in kept:
            if not self._context_ok(text, start, end, date_spans):
                continue
            digits = raw.replace("+", "")
            for char in _SEPARATORS:
                digits = digits.replace(char, "")
            if not _DIGITS_RE.match(digits) or not (
                _MIN_DIGITS <= len(digits) <= _MAX_DIGITS
            ):
                continue
            if digits.startswith("00"):
                digits = digits[2:]
            if not _MIN_DIGITS <= len(digits) <= _MAX_DIGITS:
                continue
            phones.append(self._format_extracted(raw, region))
        return {
            **context,
            "count": len(phones),
            "phones": phones,
            "result": [item["e164"] for item in phones if "e164" in item],
        }

    def _format_extracted(self, raw: str, region: Any) -> dict:
        """Format one extracted span via the format-mode logic."""
        candidate_region = region
        if not raw.startswith("+"):
            stripped = raw
            for char in _SEPARATORS:
                stripped = stripped.replace(char, "")
            if not candidate_region:
                first_group = re.match(r"\d{1,4}", raw)
                first_group_len = len(first_group.group(0)) if first_group else 0
                if _CN_MOBILE_RE.match(stripped) and (
                    stripped == raw or first_group_len == 3
                ):
                    # China-mobile shape: a contiguous 11-digit run, or
                    # a separated span whose leading group is the
                    # 3-digit '13x'-'19x' prefix ('138 1234 5678'). A
                    # NANP form like '1-415-555-2671' carries its
                    # leading 1 as a lone group and is not mistaken
                    # for one.
                    candidate_region = "CN"  # shape-implied
                elif len(stripped) == 10 or (
                    len(stripped) == 11 and stripped.startswith("1")
                ):
                    candidate_region = "US"  # NANP shape (US/CA share +1)
        formatted = self._run_format(raw, candidate_region, "e164")
        item: dict[str, Any] = {"raw": raw}
        if "error" in formatted:
            item["error"] = formatted["error"]
        else:
            item["e164"] = formatted["e164"]
            item["region"] = formatted.get("default_region")
        return item

    def _context_ok(
        self, text: str, start: int, end: int, date_spans: list
    ) -> bool:
        """Guard a candidate against date- and math-like context.

        Mirrors the PIIReporter family guards.
        """
        for ds, de in date_spans:
            if start < de and ds < end:
                return False
        prefix = text[max(0, start - 8):start]
        if text[start:start + 1] == "+" and self._ARITH_OPERAND_BEFORE.search(
            prefix
        ):
            return False
        if self._ARITH_ASSIGN_BEFORE.search(prefix):
            return False
        if self._ARITH_AFTER.match(text[end:end + 8]):
            return False
        return True

    # ------------------------------------------------------------------ #
    # Table labels for error messages
    # ------------------------------------------------------------------ #

    @classmethod
    def _region_codes_label(cls) -> str:
        """Comma-separated list of supported two-letter region codes."""
        codes: list = []
        for entry in cls.DIAL_CODES.values():
            if entry:
                codes.extend(entry["regions"])
        return ", ".join(codes)

    @classmethod
    def _dial_codes_label(cls) -> str:
        """Comma-separated list of supported dial codes."""
        return ", ".join(
            f"+{code}" for code, entry in cls.DIAL_CODES.items() if entry
        )

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
