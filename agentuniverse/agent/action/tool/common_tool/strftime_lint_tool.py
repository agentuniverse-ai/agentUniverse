#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: strftime_lint_tool.py

"""strftime/strptime format-string linting and explanation tool.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency utility for
datetime *format strings*. The family's temporal tools operate on
values — ``DurationTool`` (#3513) parses ISO 8601 durations,
``IsoWeekTool`` (#3894) does ISO week calendar arithmetic,
``DateTimeTool`` (#3420) parses and formats datetimes — but none of
them inspects the format string itself. This tool is that missing
layer: it answers "is this ``%Y-%m-%d``-style format string correct,
portable and round-trippable?" before an agent ever renders a
datetime with it.

Directive taxonomy (the linter's core knowledge, verified against
CPython 3.11 ``datetime`` on POSIX in the test suite):

* **C89 core** (ISO/IEC 9899:1990 ``strftime``): ``%a %A %b %B %c
  %d %H %I %j %m %M %p %S %U %w %W %x %X %y %Y %Z`` and ``%%``.
* **C99 / POSIX.1-2001 additions**: ``%C %D %e %F %g %G %h %n %r
  %R %t %T %u %V %z`` — absent from strict C89 platforms and from
  MSVC runtimes before VS2015.
* **glibc/BSD extensions** (no ISO C status): ``%k %l %s %P %v``,
  the ``%:z``/``%::z``/``%:::z`` colon-offset forms, and every
  flag/width/modifier prefix (``%-d``, ``%_m``, ``%0H``, ``%^a``,
  ``%#Z``, ``%3Y``, ``%Ec``, ``%Od``).
* **CPython-only**: ``%f`` (microseconds) — understood by
  ``datetime.strftime``/``strptime`` but by no C ``strftime``.

By policy ``%n`` and ``%t`` (plain whitespace) are treated as safe
and never flagged, although they are formally C99 additions; the
policy is documented here rather than hidden.

Four modes:

* ``lint`` — static, pure-Python analysis (no ``strftime`` calls,
  identical results on every platform). Findings are
  ``{line, code, message, severity}`` records with 1-based line
  numbers inside the format string. Codes: ``unknown_directive``
  (error — the message lists the full valid set),
  ``dangling_percent`` (error — a trailing bare ``%`` raises
  ``ValueError`` at render time on glibc and renders a literal
  ``'%'`` on BSD/macOS), ``locale_dependent`` (info —
  ``%c %x %X`` render and re-parse differently outside the C
  locale), ``gnu_extension`` (info — glibc/BSD-only directives,
  ``%:z`` forms, and every flag/width/modifier prefix; the message
  notes that CPython ``strptime`` rejects flag forms, so they can
  never round-trip), ``non_c89_directive`` (info — C99/POSIX.1-2001
  directives missing from strict C89 and pre-2015 MSVC runtimes),
  ``tz_directive_caveat`` (info — ``%Z``: ``strptime`` accepts only
  UTC, GMT and the runtime's ``time.tzname`` values and yields a
  naive datetime; ``%z`` renders ``''`` for naive datetimes),
  ``non_ascii_literal`` (info), ``no_directives`` (warning — a
  format with no directive at all, e.g. a ``YYYY-MM-DD``-style
  template mistake) and ``empty_format`` (warning). ``%%`` renders
  a literal percent and is never flagged; ``%n``/``%t`` are never
  flagged (policy above).
* ``explain`` — one entry per directive in order of appearance:
  ``{directive, meaning, example_output, parsed_by_strptime,
  gnu_only, windows_note}``. ``example_output`` is rendered with
  the fixed reference datetime ``2024-02-29T13:45:06.123456+00:00``
  (a leap-year Thursday chosen so ``%d``, ``%j``, ISO-week and
  AM/PM directives all produce distinctive values) by calling the
  runtime's real ``strftime``; a directive the runtime cannot
  render yields ``None``. ``parsed_by_strptime`` reflects CPython's
  ``datetime.strptime`` (itself pure Python, so this flag is
  platform-independent) and is context-aware: ``%G``/``%V`` count
  as parseable only when the ISO trio (``%G``+``%V``+a weekday
  directive) is present, because ``strptime`` raises a pairing
  error otherwise. When ``%s`` is present the result carries a
  ``determinism_notes`` entry: on BSD/macOS its rendering depends
  on the runtime's local timezone even for aware datetimes.
* ``probe`` — the live-platform oracle: renders each directive
  (and the whole format) through the runtime's real
  ``datetime.strftime`` against the fixed reference datetime or a
  caller-supplied ISO datetime. Results are by construction
  platform-dependent — that is their purpose (this very platform,
  macOS, renders ``%^a`` literally and ``%:z`` as ``':z'``).
* ``roundtrip_check`` — computes for real whether
  ``datetime.strptime(datetime.strftime(REFERENCE, fmt), fmt)``
  recovers a datetime. Returns ``possible``, ``recovered_iso``,
  ``loss_fields`` (year/month/day/hour/minute/second/microsecond/
  utcoffset fields the format fails to carry back — e.g. a
  ``%S``-only format loses everything but the second) and
  ``pitfalls`` observed honestly, including: ``%Z`` parses but
  yields a naive datetime (offset lost), ``%j`` without a year
  defaults to 1900 (non-leap — wrong date, not merely partial),
  ``%U``/``%W`` are ignored for date computation unless a year and
  weekday are also present, flag/width forms render on glibc but
  are rejected by ``strptime``, ``%s`` rendering is local-timezone
  dependent on BSD/macOS, a directive appearing twice (except
  ``%%``) breaks CPython ``strptime``'s regex with ``re.error``
  ("redefinition of group name"), and an empty format
  "round-trips" to the 1900-01-01 defaults.

Input validation is strict and happens before any computation:
unknown mode, non-string format, a format over 4,000 characters, a
``datetime`` argument outside ``probe`` mode, or a malformed
(non-ISO, over 64 characters, wrong type) datetime string raise a
``ValueError``. All computations are deterministic given the same
platform and inputs; the reference datetime is a fixed constant.
"""

import re
import sys
from datetime import datetime, timezone
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# The fixed reference datetime: a leap-year Thursday chosen so every
# directive family produces distinctive, checkable output.
REFERENCE_DATETIME = datetime(2024, 2, 29, 13, 45, 6, 123456, tzinfo=timezone.utc)
REFERENCE_DATETIME_ISO = "2024-02-29T13:45:06.123456+00:00"

# Directive families.
FAMILY_C89 = "c89"
FAMILY_C99_POSIX = "c99_posix"
FAMILY_GNU = "gnu"
FAMILY_PYTHON = "python"

# Per-directive knowledge base. Keys are the base directive letters.
# strptime: whether CPython datetime.strptime understands the bare
# directive (%G/%V are context-dependent and resolved separately).
DIRECTIVES: dict[str, dict[str, Any]] = {
    "a": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Abbreviated weekday name (e.g. Thu)"},
    "A": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Full weekday name (e.g. Thursday)"},
    "b": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Abbreviated month name (e.g. Feb)"},
    "B": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Full month name (e.g. February)"},
    "c": {"family": FAMILY_C89, "strptime": True, "locale": True,
          "meaning": "Locale's date and time representation "
                     "(C locale: Thu Feb 29 13:45:06 2024)"},
    "C": {"family": FAMILY_C99_POSIX, "strptime": False,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "Century as a decimal number (00-99)"},
    "d": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Day of the month, zero-padded (01-31)"},
    "D": {"family": FAMILY_C99_POSIX, "strptime": False,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "Date, equivalent to %m/%d/%y"},
    "e": {"family": FAMILY_C99_POSIX, "strptime": False,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "Day of the month, space-padded ( 1-31)"},
    "F": {"family": FAMILY_C99_POSIX, "strptime": False,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "Full date, equivalent to %Y-%m-%d"},
    "f": {"family": FAMILY_PYTHON, "strptime": True,
          "windows_note": "CPython extension, not part of C strftime; "
                          "non-Python consumers will not understand it",
          "meaning": "Microseconds, zero-padded (000000-999999) — "
                     "a CPython extension"},
    "g": {"family": FAMILY_C99_POSIX, "strptime": False,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "ISO 8601 week-based year without century (00-99)"},
    "G": {"family": FAMILY_C99_POSIX, "strptime": None,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "ISO 8601 week-based year with century "
                     "(strptime requires %G + %V + a weekday together)"},
    "h": {"family": FAMILY_C99_POSIX, "strptime": False,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "Abbreviated month name, equivalent to %b"},
    "H": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Hour, 24-hour clock, zero-padded (00-23)"},
    "I": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Hour, 12-hour clock, zero-padded (01-12)"},
    "j": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Day of the year, zero-padded (001-366)"},
    "k": {"family": FAMILY_GNU, "strptime": False,
          "windows_note": "glibc/BSD extension; not supported on Windows",
          "meaning": "Hour, 24-hour clock, space-padded ( 0-23)"},
    "l": {"family": FAMILY_GNU, "strptime": False,
          "windows_note": "glibc/BSD extension; not supported on Windows",
          "meaning": "Hour, 12-hour clock, space-padded ( 1-12)"},
    "m": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Month as a decimal number, zero-padded (01-12)"},
    "M": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Minute, zero-padded (00-59)"},
    "n": {"family": FAMILY_C99_POSIX, "strptime": False,
          "windows_note": "plain whitespace; C99, but rejected by "
                          "CPython strptime",
          "meaning": "Newline character"},
    "p": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Locale's AM/PM indicator"},
    "P": {"family": FAMILY_GNU, "strptime": False,
          "windows_note": "glibc extension (lowercase am/pm); not "
                          "supported on Windows and rendered literally "
                          "on macOS/BSD",
          "meaning": "am/pm, lowercase (glibc semantics)"},
    "r": {"family": FAMILY_C99_POSIX, "strptime": False,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "Time, equivalent to %I:%M:%S %p"},
    "R": {"family": FAMILY_C99_POSIX, "strptime": False,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "Time, equivalent to %H:%M"},
    "s": {"family": FAMILY_GNU, "strptime": False,
          "windows_note": "glibc/BSD extension; not supported on "
                          "Windows; on BSD/macOS the rendering depends "
                          "on the runtime's local timezone even for "
                          "aware datetimes",
          "meaning": "Seconds since the Unix epoch "
                     "(environment-dependent on BSD/macOS)"},
    "S": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Second, zero-padded (00-61, leap-second range)"},
    "t": {"family": FAMILY_C99_POSIX, "strptime": False,
          "windows_note": "plain whitespace; C99, but rejected by "
                          "CPython strptime",
          "meaning": "Tab character"},
    "T": {"family": FAMILY_C99_POSIX, "strptime": False,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "Time, equivalent to %H:%M:%S"},
    "u": {"family": FAMILY_C99_POSIX, "strptime": True,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "ISO 8601 weekday (1-7, Monday=1)"},
    "U": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Week number, Sunday as the first day (00-53); "
                     "strptime ignores it for date computation unless "
                     "a year and weekday are also given"},
    "v": {"family": FAMILY_GNU, "strptime": False,
          "windows_note": "BSD-family extension; not supported on "
                          "Windows",
          "meaning": "Date, equivalent to %e-%b-%Y"},
    "V": {"family": FAMILY_C99_POSIX, "strptime": None,
          "windows_note": "C99/POSIX.1-2001; missing from MSVC "
                          "runtimes before VS2015 (modern UCRT has it)",
          "meaning": "ISO 8601 week number (01-53) "
                     "(strptime requires %G + %V + a weekday together)"},
    "w": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Weekday as a decimal number (0-6, Sunday=0)"},
    "W": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Week number, Monday as the first day (00-53); "
                     "strptime ignores it for date computation unless "
                     "a year and weekday are also given"},
    "x": {"family": FAMILY_C89, "strptime": True, "locale": True,
          "meaning": "Locale's date representation "
                     "(C locale: 02/29/24)"},
    "X": {"family": FAMILY_C89, "strptime": True, "locale": True,
          "meaning": "Locale's time representation "
                     "(C locale: 13:45:06)"},
    "y": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Year without century (00-99)"},
    "Y": {"family": FAMILY_C89, "strptime": True,
          "meaning": "Year with century"},
    "z": {"family": FAMILY_C99_POSIX, "strptime": True, "tz": True,
          "windows_note": "C99/POSIX.1-2001; unsupported by strftime "
                          "in MSVC runtimes before VS2015; renders '' "
                          "for naive datetimes on POSIX",
          "meaning": "UTC offset in the form +HHMM (aware datetimes "
                     "only; '' for naive datetimes on POSIX)"},
    "Z": {"family": FAMILY_C89, "strptime": True, "tz": True,
          "windows_note": "Windows renders the full time-zone name "
                          "(e.g. 'Coordinated Universal Time') instead "
                          "of the abbreviation",
          "meaning": "Time-zone name (aware datetimes only; '' for "
                     "naive datetimes on POSIX); strptime accepts only "
                     "UTC, GMT and the runtime's time.tzname values, "
                     "and yields a naive datetime"},
    "%": {"family": FAMILY_C89, "strptime": True,
          "meaning": "A literal '%' character"},
}

# Policy whitelist: C99 additions rendered as plain whitespace that
# are near-universally supported and never flagged by lint.
LINT_EXEMPT = frozenset({"n", "t"})

# Directives documented to vary with the locale.
LOCALE_DEPENDENT = frozenset({"c", "x", "X"})

# Fixed C-locale renderings of the locale-dependent directives at the
# reference datetime (C locale: %c = '%a %b %e %H:%M:%S %Y',
# %x = '%m/%d/%y', %X = '%H:%M:%S'). Hardcoded so lint never calls
# strftime: its documented guarantee is byte-identical findings on
# every platform and in every process locale (a live call would echo
# the process's LC_TIME rendering while the text claims the C locale).
C_LOCALE_EXAMPLES: dict[str, str] = {
    "c": "Thu Feb 29 13:45:06 2024",
    "x": "02/29/24",
    "X": "13:45:06",
}

# ISO-trio weekday directives accepted by strptime next to %G/%V.
_ISO_WEEKDAY = frozenset({"A", "a", "w", "u"})

_VALID_SET = ", ".join(
    "%" + letter for letter in sorted(DIRECTIVES, key=lambda c: (c.lower(), c))
) + ", %:z, %::z, %:::z"

_FLAG_CHARS = "-_0^#EO"
# Fields tracked by round-trip loss analysis, in reporting order.
_FIELD_ORDER = (
    "year", "month", "day", "hour", "minute", "second",
    "microsecond", "utcoffset",
)


class _Token:
    """One directive occurrence found by the static scanner."""

    __slots__ = ("start", "end", "line", "letter", "flags", "width",
                 "colons", "dangling", "unknown", "note")

    def __init__(self, start: int, end: int, line: int, letter: str,
                 flags: str, width: str, colons: int, dangling: bool,
                 unknown: bool, note: str | None = None) -> None:
        self.start = start
        self.end = end
        self.line = line
        self.letter = letter
        self.flags = flags
        self.width = width
        self.colons = colons
        self.dangling = dangling
        self.unknown = unknown
        self.note = note

    @property
    def text(self) -> str:
        """The verbatim directive text as it appears in the format."""
        if self.dangling:
            return "%"
        return "%" + self.flags + self.width + ":" * self.colons + self.letter

    @property
    def has_prefix(self) -> bool:
        """True when flags, a width or an E/O modifier is present."""
        return bool(self.flags or self.width)


class StrftimeLintTool(Tool):
    """strftime/strptime format-string linter built on the stdlib.

    Attributes:
        max_format_chars (int): Upper bound on the ``fmt`` input length.
        max_dt_chars (int): Upper bound on the ``dt`` ISO string length.
        max_pitfalls (int): Cap on the ``pitfalls`` list length.
        max_codepoints_listed (int): Non-ASCII code points echoed in
            finding messages.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "strftime_lint_tool"
    description: str = (
        "Strftime lint tool — strftime/strptime format-string linting, "
        "explanation, platform probing and round-trip checking with pure "
        "Python stdlib, no network required. The datetime family's tools "
        "(DurationTool, IsoWeekTool, DateTimeTool) operate on temporal "
        "values; this tool inspects the format string itself. mode='lint' "
        "statically checks a format string for unknown % directives "
        "(error, listing the valid set), a dangling trailing %, "
        "locale-dependent %c/%x/%X (info), glibc/BSD-only directives and "
        "flag/width/modifier forms like %-d %_m %0H %^a %#Z %3Y %Ec "
        "(info — CPython strptime rejects flag forms), C99/POSIX.1-2001 "
        "directives beyond the C89 core such as %F %T %e %G %V (info), "
        "%Z/%z caveats (strptime %Z accepts only UTC/GMT/time.tzname "
        "values and yields a naive datetime; %z renders '' for naive "
        "datetimes), non-ASCII literals (info), directive-free formats "
        "and empty formats (warning); findings carry {line, code, "
        "message, severity}. mode='explain' returns each directive in "
        "order of appearance with its meaning, a deterministic example "
        "rendered at the fixed reference datetime 2024-02-29T13:45:06."
        "123456+00:00, whether CPython strptime parses it (context-aware "
        "for the %G/%V/weekday trio), gnu_only and windows_note flags. "
        "mode='probe' renders each directive and the whole format "
        "through the runtime's real datetime.strftime (optionally at a "
        "caller-supplied ISO datetime) — the live platform oracle. "
        "mode='roundtrip_check' computes for real whether "
        "strptime(strftime(reference, fmt), fmt) recovers a datetime, "
        "reporting loss_fields and honestly observed pitfalls (%Z offset "
        "loss, %j without a year defaulting to 1900, %U/%W ignored for "
        "date computation, flag forms rejected by strptime, %s "
        "environment dependence). Strict validation, size caps, "
        "deterministic output."
    )

    MODES: ClassVar[tuple] = ("lint", "explain", "probe", "roundtrip_check")

    max_format_chars: ClassVar[int] = 4_000
    max_dt_chars: ClassVar[int] = 64
    max_pitfalls: ClassVar[int] = 6
    max_codepoints_listed: ClassVar[int] = 5

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(self, mode: Any, fmt: Any = None, dt: Any = None) -> dict[str, Any]:
        """Run one strftime format-string operation.

        Args:
            mode (str): One of ``lint`` / ``explain`` / ``probe`` /
                ``roundtrip_check``.
            fmt (str): The strftime/strptime format string to inspect.
                May be empty (each mode reports that honestly) but no
                longer than 4,000 characters.
            dt (str): Probe mode only — an ISO 8601 datetime string the
                directives are rendered against (default: the fixed
                reference datetime). Rejected in the other modes.

        Returns:
            Dict[str, Any]: The mode's payload (findings for ``lint``,
            directive entries for ``explain``/``probe``, the round-trip
            verdict for ``roundtrip_check``).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        format_string = self._validate_fmt(fmt)
        if mode == "lint":
            self._reject_option("dt", dt, allowed_modes=("probe",))
            return self._run_lint(format_string)
        if mode == "explain":
            self._reject_option("dt", dt, allowed_modes=("probe",))
            return self._run_explain(format_string)
        if mode == "probe":
            target = self._validate_dt(dt)
            return self._run_probe(format_string, target)
        self._reject_option("dt", dt, allowed_modes=("probe",))
        return self._run_roundtrip(format_string)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"strftime_lint_tool: {message}")

    @classmethod
    def _validate_fmt(cls, fmt: Any) -> str:
        """Validate the format string (empty is allowed, oversized is not)."""
        if fmt is None or isinstance(fmt, bool) or not isinstance(fmt, str):
            cls._invalid(f"fmt must be a string (got {fmt!r})")
        if len(fmt) > cls.max_format_chars:
            cls._invalid(
                f"fmt exceeds the {cls.max_format_chars:,}-character limit "
                f"(got {len(fmt):,} characters)"
            )
        return fmt

    @classmethod
    def _validate_dt(cls, dt: Any) -> datetime:
        """Validate the optional probe datetime; default to the reference."""
        if dt is None:
            return REFERENCE_DATETIME
        if isinstance(dt, bool) or not isinstance(dt, str):
            cls._invalid(f"dt must be an ISO 8601 datetime string (got {dt!r})")
        if not dt:
            cls._invalid("dt must be an ISO 8601 datetime string (got '')")
        if len(dt) > cls.max_dt_chars:
            cls._invalid(
                f"dt exceeds the {cls.max_dt_chars}-character limit "
                f"(got {len(dt)} characters)"
            )
        normalized = dt.strip()
        if normalized.endswith(("Z", "z")):
            normalized = normalized[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            cls._invalid(
                f"dt must be an ISO 8601 datetime string (got {dt!r})"
            )
        return parsed

    @classmethod
    def _reject_option(cls, name: str, value: Any, allowed_modes: tuple) -> None:
        """Reject an option passed outside its allowed modes."""
        if value is not None:
            cls._invalid(
                f"{name} is only accepted in {', '.join(allowed_modes)} mode"
            )

    # ------------------------------------------------------------------ #
    # Static scanner (shared by every mode; no strftime calls)
    # ------------------------------------------------------------------ #

    @classmethod
    def _scan(cls, fmt: str) -> list[_Token]:
        """Tokenize every ``%``-introduced directive in the format.

        Unknown letters and dangling ``%`` characters are represented
        as tokens flagged ``unknown`` / ``dangling`` so all modes share
        one view of the format string.
        """
        tokens: list[_Token] = []
        i = 0
        length = len(fmt)
        while i < length:
            if fmt[i] != "%":
                i += 1
                continue
            line = fmt.count("\n", 0, i) + 1
            # Literal %%: never flagged, consumes both characters.
            if i + 1 < length and fmt[i + 1] == "%":
                tokens.append(_Token(i, i + 2, line, "%", "", "", 0,
                                     False, False))
                i += 2
                continue
            j = i + 1
            flags = ""
            while j < length and fmt[j] in _FLAG_CHARS:
                flags += fmt[j]
                j += 1
            width = ""
            while j < length and fmt[j].isdigit():
                width += fmt[j]
                j += 1
            colons = 0
            while j < length and fmt[j] == ":":
                colons += 1
                j += 1
            if j >= length:
                tokens.append(_Token(i, length, line, "", flags, width,
                                     colons, True, False))
                break
            letter = fmt[j]
            if colons and (letter != "z" or colons > 3):
                tokens.append(_Token(i, j + 1, line, letter, flags, width,
                                     colons, False, True,
                                     note="a ':' is only valid before 'z' "
                                          "(glibc %:z forms)"))
                i = j + 1
                continue
            known = letter in DIRECTIVES or (colons and letter == "z")
            if letter == "%" and (flags or width or colons):
                known = False
            tokens.append(_Token(i, j + 1, line, letter, flags, width,
                                 colons, False, not known))
            i = j + 1
        return tokens

    @staticmethod
    def _iso_trio_present(tokens: list[_Token]) -> bool:
        """Whether %G, %V and a weekday directive all appear (no flags)."""
        bare_letters = {
            token.letter for token in tokens
            if not token.dangling and not token.unknown and not token.has_prefix
        }
        return "G" in bare_letters and "V" in bare_letters and bool(
            bare_letters & _ISO_WEEKDAY
        )

    @staticmethod
    def _strptime_parseable(token: _Token, trio: bool) -> bool:
        """The static parsed_by_strptime verdict for one token."""
        if token.dangling or token.unknown:
            return False
        if token.has_prefix or token.colons:
            return False
        if token.letter in ("G", "V"):
            return trio
        entry = DIRECTIVES[token.letter]
        if entry["strptime"] is None:  # pragma: no cover - guarded above
            return False
        return bool(entry["strptime"])

    # ------------------------------------------------------------------ #
    # lint mode
    # ------------------------------------------------------------------ #

    def _run_lint(self, fmt: str) -> dict[str, Any]:
        """Static analysis; identical results on every platform."""
        tokens = self._scan(fmt)
        findings: list[dict[str, Any]] = []
        if not fmt:
            findings.append({
                "code": "empty_format",
                "severity": "warning",
                "line": 1,
                "message": "the format string is empty — it renders '' and "
                           "strptime('', '') 'succeeds' only by returning the "
                           "1900-01-01 defaults",
            })
        else:
            if not tokens:
                findings.append({
                    "code": "no_directives",
                    "severity": "warning",
                    "line": 1,
                    "message": "the format contains no % directive at all — "
                               "plain text renders verbatim and re-parses "
                               "nothing (a 'YYYY-MM-DD'-style template "
                               "mistake?)",
                })
            for token in tokens:
                self._lint_token(fmt, token, findings)
        self._lint_non_ascii(fmt, findings)
        findings.sort(key=lambda f: (f["line"], f.get("_start", 0), f["code"]))
        for finding in findings:
            finding.pop("_start", None)
        counts = {"error": 0, "warning": 0, "info": 0}
        for finding in findings:
            counts[finding["severity"]] += 1
        return {
            "mode": "lint",
            "format": fmt,
            "findings": findings,
            "finding_counts": {**counts, "total": len(findings)},
        }

    @classmethod
    def _finding(cls, findings: list, code: str, severity: str,
                 line: int, start: int, message: str) -> None:
        """Append one finding carrying its sort key internally."""
        findings.append({
            "code": code,
            "severity": severity,
            "line": line,
            "message": message,
            "_start": start,
        })

    def _lint_token(self, fmt: str, token: _Token,
                    findings: list[dict[str, Any]]) -> None:
        """Emit findings for one scanned token."""
        if token.dangling:
            self._finding(
                findings, "dangling_percent", "error", token.line,
                token.start,
                "dangling '%': the format ends with a bare '%' (after "
                + (f"'{token.flags}{token.width}'" if token.flags or token.width
                   else "nothing")
                + ") — datetime.strftime raises ValueError for it at "
                  "render time on glibc, while BSD/macOS silently "
                  "renders a literal '%': broken everywhere, in "
                  "different ways",
            )
            return
        if token.unknown:
            detail = f"unknown directive {token.text!r}"
            if token.note:
                detail += f" ({token.note})"
            if token.letter == "%" and (token.flags or token.width):
                detail = f"invalid directive {token.text!r} ('%%' cannot " \
                         f"take flags or a width)"
            self._finding(
                findings, "unknown_directive", "error", token.line,
                token.start,
                f"{detail} — valid directives are: {_VALID_SET}",
            )
            return
        letter = token.letter
        if letter == "%":
            return  # a literal % is always fine
        entry = DIRECTIVES[letter]
        if token.has_prefix or token.colons:
            described = self._describe_prefix(token)
            self._finding(
                findings, "gnu_extension", "info", token.line, token.start,
                f"{described} is a glibc strftime feature — unsupported on "
                f"Windows (where %# has different, alternate-form meaning) "
                f"and rejected by CPython strptime, so a format using it "
                f"can never round-trip",
            )
            return
        if letter in LOCALE_DEPENDENT:
            self._finding(
                findings, "locale_dependent", "info", token.line,
                token.start,
                f"%{letter} output varies with the locale (and strptime "
                f"expects the current locale's representation) — under the "
                f"C locale it renders {C_LOCALE_EXAMPLES[letter]!r}",
            )
            return
        if letter == "Z":
            self._finding(
                findings, "tz_directive_caveat", "info", token.line,
                token.start,
                "%Z: strptime accepts only UTC, GMT and the runtime's "
                "time.tzname values and yields a naive datetime (the "
                "offset is lost); naive datetimes render '' on POSIX and "
                "Windows renders the full zone name",
            )
            return
        if letter == "z":
            self._finding(
                findings, "tz_directive_caveat", "info", token.line,
                token.start,
                "%z: renders '' for naive datetimes; a C99/POSIX.1-2001 "
                "directive missing from MSVC runtimes before VS2015",
            )
            return
        if entry["family"] == FAMILY_GNU:
            extra = ""
            if letter == "s":
                extra = ("; its rendering also depends on the runtime's "
                         "local timezone on BSD/macOS, even for aware "
                         "datetimes")
            self._finding(
                findings, "gnu_extension", "info", token.line, token.start,
                f"%{letter} is a glibc/BSD extension, not ISO C — "
                f"unsupported on Windows and rejected by CPython "
                f"strptime{extra}",
            )
            return
        if entry["family"] == FAMILY_C99_POSIX and letter not in LINT_EXEMPT:
            self._finding(
                findings, "non_c89_directive", "info", token.line,
                token.start,
                f"%{letter} was added by C99/POSIX.1-2001 — it is beyond "
                f"the C89 strftime core and missing from MSVC runtimes "
                f"before VS2015 (CPython strptime "
                f"{'understands' if entry['strptime'] else 'rejects'} it)",
            )
            return
        # C89 core directives (and the whitelisted %n/%t) are clean.

    @staticmethod
    def _describe_prefix(token: _Token) -> str:
        """Human description of a flag/width/modifier prefix."""
        parts = [f"flag {ch!r}" for ch in token.flags]
        if token.width:
            parts.append(f"width {token.width}")
        if token.colons:
            parts.append(f"'{':' * token.colons}' colon form")
        return f"{' '.join(parts)} in {token.text!r}"

    @classmethod
    def _lint_non_ascii(cls, fmt: str,
                        findings: list[dict[str, Any]]) -> None:
        """Flag non-ASCII characters (one info finding at the first)."""
        positions = [i for i, ch in enumerate(fmt) if ord(ch) > 0x7F]
        if not positions:
            return
        line = fmt.count("\n", 0, positions[0]) + 1
        codepoints = ", ".join(
            f"U+{ord(fmt[i]):04X}" for i in positions[:cls.max_codepoints_listed]
        )
        if len(positions) > cls.max_codepoints_listed:
            codepoints += ", ..."
        cls._finding(
            findings, "non_ascii_literal", "info", line, positions[0],
            f"{len(positions)} non-ASCII character(s) in the format "
            f"(first at line {line}: {codepoints}) — literal text renders "
            f"verbatim, but non-ASCII output may be mangled by "
            f"non-UTF-8 consumers",
        )

    # ------------------------------------------------------------------ #
    # explain mode
    # ------------------------------------------------------------------ #

    def _run_explain(self, fmt: str) -> dict[str, Any]:
        """One knowledge-base entry per directive, in appearance order."""
        tokens = self._scan(fmt)
        trio = self._iso_trio_present(tokens)
        entries: list[dict[str, Any]] = []
        determinism_notes: list[str] = []
        for token in tokens:
            entry = self._explain_token(token, trio)
            entries.append(entry)
            if (not token.unknown and not token.dangling
                    and token.letter == "s"):
                determinism_notes.append(
                    "%s: on BSD/macOS the rendering depends on the "
                    "runtime's local timezone even for aware datetimes — "
                    "example_output reflects this environment"
                )
        result: dict[str, Any] = {
            "mode": "explain",
            "format": fmt,
            "reference_datetime": REFERENCE_DATETIME_ISO,
            "directives": entries,
        }
        if determinism_notes:
            result["determinism_notes"] = determinism_notes
        return result

    @classmethod
    def _explain_token(cls, token: _Token, trio: bool) -> dict[str, Any]:
        """Build one explain entry; the example comes from real strftime."""
        if token.dangling:
            return {
                "directive": token.text,
                "meaning": None,
                "example_output": None,
                "parsed_by_strptime": False,
                "gnu_only": False,
                "windows_note": None,
            }
        known = not token.unknown
        example = None
        if known:
            try:
                example = REFERENCE_DATETIME.strftime(token.text)
            except ValueError:
                example = None
        gnu_only = bool(
            known
            and (token.has_prefix or token.colons
                 or DIRECTIVES[token.letter]["family"] == FAMILY_GNU)
        )
        return {
            "directive": token.text,
            "meaning": DIRECTIVES[token.letter]["meaning"] if known else None,
            "example_output": example,
            "parsed_by_strptime": cls._strptime_parseable(token, trio),
            "gnu_only": gnu_only,
            "windows_note": (
                DIRECTIVES[token.letter].get("windows_note") if known else None
            ),
        }

    # ------------------------------------------------------------------ #
    # probe mode
    # ------------------------------------------------------------------ #

    def _run_probe(self, fmt: str, target: datetime) -> dict[str, Any]:
        """Render every directive through the runtime's real strftime."""
        tokens = self._scan(fmt)
        entries: list[dict[str, Any]] = []
        for token in tokens:
            if token.dangling:
                entries.append({
                    "directive": token.text,
                    "output": None,
                    "error": "dangling '%' — datetime.strftime raises "
                             "ValueError at render time on glibc, while "
                             "BSD/macOS silently renders a literal '%'",
                })
                continue
            try:
                rendered = target.strftime(token.text)
                error = None
            except ValueError as exc:
                rendered = None
                error = f"datetime.strftime raised ValueError: {exc}"
            entries.append({
                "directive": token.text,
                "output": rendered,
                "error": error,
            })
        try:
            whole = target.strftime(fmt)
            render: dict[str, Any] = {"ok": True, "output": whole}
        except ValueError as exc:
            render = {"ok": False, "error": f"ValueError: {exc}"}
        return {
            "mode": "probe",
            "format": fmt,
            "datetime": target.isoformat(),
            "datetime_source": (
                "default_reference" if target is REFERENCE_DATETIME
                else "provided"
            ),
            "platform": sys.platform,
            "platform_note": "outputs are produced by this runtime's real "
                             "datetime.strftime and vary across platforms "
                             "— that variance is what this mode measures",
            "render": render,
            "directives": entries,
        }

    # ------------------------------------------------------------------ #
    # roundtrip_check mode
    # ------------------------------------------------------------------ #

    def _run_roundtrip(self, fmt: str) -> dict[str, Any]:
        """Compute the real strptime(strftime(...)) round-trip verdict."""
        result: dict[str, Any] = {
            "mode": "roundtrip_check",
            "format": fmt,
            "reference_datetime": REFERENCE_DATETIME_ISO,
        }
        tokens = self._scan(fmt)
        try:
            rendered = REFERENCE_DATETIME.strftime(fmt)
        except ValueError as exc:
            return {
                **result,
                "rendered": None,
                "possible": False,
                "recovered_iso": None,
                "loss_fields": None,
                "pitfalls": [
                    f"datetime.strftime raised ValueError: {exc}"
                ],
            }
        result["rendered"] = rendered
        try:
            recovered = datetime.strptime(rendered, fmt)
        except (ValueError, re.error) as exc:
            pitfalls = [
                f"datetime.strptime rejected the rendered value "
                f"({rendered!r}): {type(exc).__name__}: {exc}"
            ]
            pitfalls.extend(self._static_pitfalls(tokens))
            return {
                **result,
                "possible": False,
                "recovered_iso": None,
                "loss_fields": None,
                "pitfalls": pitfalls[: self.max_pitfalls],
            }
        loss_fields = self._loss_fields(recovered)
        pitfalls = self._static_pitfalls(tokens)
        if not tokens:
            pitfalls.append(
                "the format carries no directive at all — strptime "
                "'succeeds' only by returning the 1900-01-01 defaults"
            )
        result.update({
            "possible": True,
            "recovered_iso": recovered.isoformat(),
            "loss_fields": loss_fields,
            "pitfalls": pitfalls[: self.max_pitfalls],
        })
        return result

    @staticmethod
    def _loss_fields(recovered: datetime) -> list[str]:
        """Fields the round-trip failed to carry back from the reference.

        A field counts as lost whenever the recovered value differs
        from the reference (strptime fills unspecified fields with
        1900-01-01 00:00:00.000000 and leaves the datetime naive).
        """
        lost: list[str] = []
        pairs = (
            ("year", recovered.year, REFERENCE_DATETIME.year),
            ("month", recovered.month, REFERENCE_DATETIME.month),
            ("day", recovered.day, REFERENCE_DATETIME.day),
            ("hour", recovered.hour, REFERENCE_DATETIME.hour),
            ("minute", recovered.minute, REFERENCE_DATETIME.minute),
            ("second", recovered.second, REFERENCE_DATETIME.second),
            ("microsecond", recovered.microsecond,
             REFERENCE_DATETIME.microsecond),
        )
        for name, got, want in pairs:
            if got != want:
                lost.append(name)
        if recovered.utcoffset() != REFERENCE_DATETIME.utcoffset():
            lost.append("utcoffset")
        return lost

    def _static_pitfalls(self, tokens: list[_Token]) -> list[str]:
        """Pitfalls derivable from the format content, honestly stated."""
        pitfalls: list[str] = []
        bare = [
            token for token in tokens
            if not token.dangling and not token.unknown and not token.has_prefix
        ]
        letters = {token.letter for token in bare}
        repeated = sorted(
            letter for letter in letters if letter != "%"
            and sum(1 for token in bare if token.letter == letter) > 1
        )
        if repeated:
            pitfalls.append(
                "a directive appearing more than once ("
                + ", ".join("%" + letter for letter in repeated)
                + ") breaks CPython strptime's regex — it raises "
                "re.error ('redefinition of group name')"
            )
        if "Z" in letters:
            pitfalls.append(
                "%Z parses but yields a naive datetime — the UTC offset "
                "is not recovered; strptime accepts only UTC, GMT and "
                "the runtime's time.tzname values"
            )
        if "j" in letters and "Y" not in letters and "G" not in letters:
            pitfalls.append(
                "%j without a year: strptime defaults the year to 1900 "
                "(a non-leap year) — the recovered date is wrong, not "
                "merely partial"
            )
        if "U" in letters or "W" in letters:
            pitfalls.append(
                "%U/%W are ignored by strptime for date computation "
                "unless the year and a weekday are also specified "
                "(CPython-documented behavior)"
            )
        if ("G" in letters or "V" in letters) and not self._iso_trio_present(tokens):
            pitfalls.append(
                "%G/%V require each other plus a weekday directive "
                "(%A/%a/%w/%u) or strptime raises a pairing ValueError"
            )
        if any(token.has_prefix for token in tokens):
            pitfalls.append(
                "flag/width forms are glibc strftime features; CPython "
                "strptime rejects them, so this format can never "
                "round-trip on CPython"
            )
        if "s" in letters:
            pitfalls.append(
                "%s rendering is local-timezone dependent on BSD/macOS "
                "(it may not match datetime.timestamp())"
            )
        if "n" in letters or "t" in letters:
            pitfalls.append(
                "%n/%t render whitespace but CPython strptime rejects "
                "both directives"
            )
        return pitfalls
