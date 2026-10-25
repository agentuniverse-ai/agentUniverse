#!/usr/bin/env python3

# @Time    : 2026/10/20
# @FileName: timezone_abbrev_tool.py

"""
Timezone Abbrev Tool — timezone abbreviation lookup and offset math.

A dependency-free utility covering the timezone *abbreviation* layer:
the EST / PST / CST / IST style short codes that appear in scraped
text, logs, flight tables and human chat. It complements
``DateTimeTool`` (IANA zone names such as ``Asia/Shanghai``) with an
embedded, curated reference table — pure Python standard library, no
``zoneinfo`` database access, no network.

Timezone abbreviations are messier than IANA names: many are shared by
unrelated regions. ``CST`` is China Standard Time (UTC+8), US Central
Standard Time (UTC-6) and Cuba Standard Time (UTC-5); ``IST`` is India
(UTC+5:30) and Israel (UTC+2); ``BST`` is British Summer Time (UTC+1)
and Bangladesh Standard Time (UTC+6). The table flags every ambiguous
abbreviation honestly instead of silently picking one meaning.

Modes (``mode`` argument):

- ``lookup``: abbreviation (case-insensitive) → all matching entries,
  each ``{abbr, name, offset_minutes, sign, dst, ambiguous}``;
- ``convert``: ``time`` (``HH:MM``) + ``from_abbr`` + ``to_abbr`` →
  result time, both UTC offsets and the delta. Ambiguous codes resolve
  to the first table entry and carry a ``warning`` listing the other
  candidates;
- ``now_offset``: abbreviation → its UTC offset only;
- ``search_by_offset``: ``+08:00``-style string or integer minutes →
  every abbreviation at that offset.

All results are structured dicts with a ``status`` field
(``success`` / ``error``); errors are returned, never raised.
Validation is strict: unknown modes, malformed ``HH:MM`` times,
abbreviations outside ``[A-Za-z]{1,5}`` and malformed offsets are
rejected with informative payloads — an unknown abbreviation comes
back with the closest known codes. Everything is deterministic: the
table is static, so no wall-clock reads occur anywhere.

Table honesty: entries record the offset each abbreviation commonly
denotes *today*; ``dst=True`` marks the daylight-saving (summer)
variant of a zone family. Abbreviations are fixed-offset labels and
are not tied to any country's DST calendar — use IANA zones via
``DateTimeTool`` for DST-accurate conversions.

Addresses #252 (common utility tools).
"""

import difflib
import re
from typing import Any

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool

# Public execute() converts validation exceptions into structured tool
# responses instead of raising.
# ruff: noqa: TRY003

_SUPPORTED_MODES = ("lookup", "convert", "now_offset", "search_by_offset")

# Abbreviation shape: 1-5 ASCII letters, case-insensitive.
_ABBR_RE = re.compile(r"^[A-Za-z]{1,5}$")
_MAX_ABBR_LENGTH = 5

# Wall-clock time shape: exactly HH:MM with 00-23 / 00-59.
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")

# UTC offset shape: +HH:MM / -HH:MM with 00-23 / 00-59.
_OFFSET_RE = re.compile(r"^([+-])([01]\d|2[0-3]):([0-5]\d)$")

# Integer search_by_offset bounds: no real offset leaves +/-24h.
_MAX_OFFSET_MINUTES = 1440

# Ground-truth table: (abbr, name, offset_minutes, dst).
#
# Region order: Americas, then Europe/Africa/Middle East, then
# Asia/Oceania. When one abbreviation has several meanings the most
# common English usage is listed FIRST — `convert` and `now_offset`
# resolve ambiguity by that first entry and warn:
#   CST -> US Central (-06:00) before China (+08:00) and Cuba (-05:00)
#   AST -> Canada Atlantic (-04:00) before Arabia (+03:00)
#   BST -> British Summer Time (+01:00) before Bangladesh (+06:00)
#   IST -> India (+05:30) before Israel (+02:00)
#   SST -> Samoa (-11:00) before Solomon Islands (+11:00)
_ABBREVIATION_TABLE: tuple[tuple[str, str, int, bool], ...] = (
    # --- Americas -----------------------------------------------------
    ("EST", "Eastern Standard Time (North America)", -300, False),
    ("EDT", "Eastern Daylight Time (North America)", -240, True),
    ("CST", "Central Standard Time (North America)", -360, False),
    ("CDT", "Central Daylight Time (North America)", -300, True),
    ("MST", "Mountain Standard Time (North America)", -420, False),
    ("MDT", "Mountain Daylight Time (North America)", -360, True),
    ("PST", "Pacific Standard Time (North America)", -480, False),
    ("PDT", "Pacific Daylight Time (North America)", -420, True),
    ("AKST", "Alaska Standard Time", -540, False),
    ("AKDT", "Alaska Daylight Time", -480, True),
    ("HST", "Hawaii-Aleutian Standard Time", -600, False),
    ("HAST", "Hawaii-Aleutian Standard Time", -600, False),
    ("HADT", "Hawaii-Aleutian Daylight Time", -540, True),
    ("AST", "Atlantic Standard Time (Canada)", -240, False),
    ("ADT", "Atlantic Daylight Time (Canada)", -180, True),
    ("NST", "Newfoundland Standard Time (Canada)", -210, False),
    ("NDT", "Newfoundland Daylight Time (Canada)", -150, True),
    ("CLT", "Chile Standard Time", -240, False),
    ("CLST", "Chile Summer Time", -180, True),
    ("ART", "Argentina Time", -180, False),
    ("BRT", "Brasilia Time", -180, False),
    ("BRST", "Brasilia Summer Time", -120, True),
    ("GFT", "French Guiana Time", -180, False),
    ("ECT", "Ecuador Time", -300, False),
    ("PET", "Peru Time", -300, False),
    ("CST", "Cuba Standard Time", -300, False),
    # --- Europe / Africa / Middle East --------------------------------
    ("UTC", "Coordinated Universal Time", 0, False),
    ("GMT", "Greenwich Mean Time", 0, False),
    ("Z", "Zulu Time (UTC)", 0, False),
    ("WET", "Western European Time", 0, False),
    ("WEST", "Western European Summer Time", 60, True),
    ("CET", "Central European Time", 60, False),
    ("CEST", "Central European Summer Time", 120, True),
    ("EET", "Eastern European Time", 120, False),
    ("EEST", "Eastern European Summer Time", 180, True),
    ("MSK", "Moscow Standard Time", 180, False),
    ("BST", "British Summer Time (UK)", 60, True),
    ("WAT", "West Africa Time", 60, False),
    ("WAST", "West Africa Summer Time", 120, True),
    ("CAT", "Central Africa Time", 120, False),
    ("EAT", "East Africa Time", 180, False),
    ("SAST", "South Africa Standard Time", 120, False),
    ("BT", "Baghdad Time", 180, False),
    ("AST", "Arabia Standard Time", 180, False),
    # --- Asia / Oceania ------------------------------------------------
    ("IST", "India Standard Time", 330, False),
    ("IST", "Israel Standard Time", 120, False),
    ("PKT", "Pakistan Standard Time", 300, False),
    ("BST", "Bangladesh Standard Time", 360, False),
    ("ICT", "Indochina Time", 420, False),
    ("MMT", "Myanmar Time", 390, False),
    ("JST", "Japan Standard Time", 540, False),
    ("KST", "Korea Standard Time", 540, False),
    ("CST", "China Standard Time", 480, False),
    ("AWST", "Australian Western Standard Time", 480, False),
    ("ACST", "Australian Central Standard Time", 570, False),
    ("ACDT", "Australian Central Daylight Time", 630, True),
    ("AEST", "Australian Eastern Standard Time", 600, False),
    ("AEDT", "Australian Eastern Daylight Time", 660, True),
    ("ChST", "Chamorro Standard Time", 600, False),
    ("NZST", "New Zealand Standard Time", 720, False),
    ("NZDT", "New Zealand Daylight Time", 780, True),
    ("SST", "Samoa Standard Time", -660, False),
    ("SST", "Solomon Islands Time (deprecated)", 660, False),
)

# abbr (uppercase) -> indices into _ABBREVIATION_TABLE, table order.
_ABBR_INDEX: dict[str, list[int]] = {}
for _i, (_abbr, _name, _off, _dst) in enumerate(_ABBREVIATION_TABLE):
    _ABBR_INDEX.setdefault(_abbr.upper(), []).append(_i)
del _i, _abbr, _name, _off, _dst

# offset_minutes -> indices into _ABBREVIATION_TABLE, table order.
_OFFSET_INDEX: dict[int, list[int]] = {}
for _i, (_abbr, _name, _off, _dst) in enumerate(_ABBREVIATION_TABLE):
    _OFFSET_INDEX.setdefault(_off, []).append(_i)
del _i, _abbr, _name, _off, _dst


def _format_offset(minutes: int) -> str:
    """Render offset minutes as a signed ``+HH:MM`` string."""
    sign = "-" if minutes < 0 else "+"
    hours, mins = divmod(abs(minutes), 60)
    return f"{sign}{hours:02d}:{mins:02d}"


def _entry_dict(index: int) -> dict:
    """Serialize one table entry, ambiguity flag computed per abbr."""
    abbr, name, offset_minutes, dst = _ABBREVIATION_TABLE[index]
    return {
        "abbr": abbr,
        "name": name,
        "offset_minutes": offset_minutes,
        "sign": _format_offset(offset_minutes),
        "dst": dst,
        "ambiguous": len(_ABBR_INDEX[abbr.upper()]) > 1,
    }


class TimezoneAbbrevTool(Tool):
    """Timezone abbreviation lookup and offset arithmetic.

    Attributes:
        nothing configurable beyond the Tool base; the reference
        table is a static module constant, so every mode is
        deterministic and offline.
    """

    name: str = "timezone_abbrev_tool"
    description: str | None = (
        "Timezone abbreviation utilities: lookup abbreviations "
        "(EST, PST, CST, IST, ...) with UTC offsets and ambiguity "
        "flags, convert HH:MM times between abbreviations, get an "
        "abbreviation's offset, and search abbreviations by UTC "
        "offset. Embedded curated table (~55 codes), pure Python, "
        "no dependencies, no network."
    )
    input_keys: list[str] | None = Field(default_factory=lambda: ["mode"])

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def execute(
        self,
        mode: str,
        abbr: str = "",
        time: str = "",
        from_abbr: str = "",
        to_abbr: str = "",
        offset: Any = None,
        **_: Any,
    ) -> dict:
        """Run one timezone-abbreviation ``mode``.

        Returns a structured dict. On success it carries ``mode`` plus
        mode-specific fields; on error it carries ``error_type`` and
        ``error``. Errors are returned, never raised.
        """
        try:
            op = self._normalize_mode(mode)
            if op == "lookup":
                return self._lookup(abbr)
            if op == "convert":
                return self._convert(time, from_abbr, to_abbr)
            if op == "now_offset":
                return self._now_offset(abbr)
            return self._search_by_offset(offset)
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc), mode)
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error(
                "operation_error",
                f"Timezone abbreviation operation failed: {exc}", mode)

    # ------------------------------------------------------------------
    # Argument validation helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_mode(mode: Any) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        op = mode.strip().lower()
        if op not in _SUPPORTED_MODES:
            raise ValueError(
                f"Unsupported mode {mode!r}. Supported: "
                + ", ".join(_SUPPORTED_MODES)
            )
        return op

    @staticmethod
    def _error(kind: str, message: str, mode: Any) -> dict:
        result = {
            "status": "error",
            "error_type": kind,
            "error": message,
        }
        if mode is not None:
            result["mode"] = mode
        return result

    def _normalize_abbr(self, value: Any, label: str) -> str:
        """Validate and uppercase an abbreviation argument."""
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise TypeError(f"{label} must be a string")
        code = value.strip()
        if not code:
            raise ValueError(f"{label} is required and must not be empty")
        if len(code) > _MAX_ABBR_LENGTH or not _ABBR_RE.match(code):
            raise ValueError(
                f"Invalid abbreviation {value!r}: 1-5 ASCII letters "
                "expected (e.g. EST, ChST)")
        return code.upper()

    def _require_entries(self, value: Any, label: str) -> list[dict]:
        """Resolve an abbreviation to its entries or raise with hints."""
        code = self._normalize_abbr(value, label)
        indices = _ABBR_INDEX.get(code)
        if not indices:
            raise ValueError(self._abbr_suggestion(code))
        return [_entry_dict(i) for i in indices]

    @staticmethod
    def _abbr_suggestion(code: str) -> str:
        """Unknown-abbreviation message with the closest known codes."""
        known = sorted(_ABBR_INDEX)
        message = (f"Unknown timezone abbreviation {code!r}. Known codes "
                   "include: " + ", ".join(known[:12]) + ", ...")
        matches = difflib.get_close_matches(code, known, n=3, cutoff=0.6)
        if matches:
            message += f" Closest matches: {', '.join(matches)}."
        return message

    @staticmethod
    def _normalize_time(value: Any) -> str:
        """Validate a strict ``HH:MM`` wall-clock time."""
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise TypeError("time must be a string")
        text = value.strip()
        if not text:
            raise ValueError("time is required and must not be empty")
        if not _TIME_RE.match(text):
            raise ValueError(
                f"Invalid time {value!r}: expected HH:MM with hours "
                "00-23 and minutes 00-59 (e.g. 09:30)")
        return text

    @staticmethod
    def _normalize_offset(value: Any) -> int:
        """Accept ``+08:00``-style strings or integer minutes."""
        if isinstance(value, bool):
            raise TypeError("offset must be a '+HH:MM' string or an "
                            "integer minute count, not a boolean")
        if isinstance(value, int):
            if abs(value) > _MAX_OFFSET_MINUTES:
                raise ValueError(
                    f"offset minutes must not exceed "
                    f"{_MAX_OFFSET_MINUTES} in absolute value")
            return value
        if isinstance(value, str):
            text = value.strip()
            match = _OFFSET_RE.match(text)
            if not match:
                raise ValueError(
                    f"Invalid offset {value!r}: expected +HH:MM or "
                    "-HH:MM (e.g. +08:00, -05:30) or integer minutes")
            sign = -1 if match.group(1) == "-" else 1
            minutes = int(match.group(2)) * 60 + int(match.group(3))
            return sign * minutes
        raise TypeError("offset must be a '+HH:MM' string or an integer "
                        "minute count")

    @staticmethod
    def _ambiguity_warning(code: str, entries: list[dict]) -> str | None:
        """Warning text when an abbreviation has several meanings."""
        if len(entries) < 2:
            return None
        chosen = entries[0]
        others = [
            f"{e['name']} ({e['sign']})" for e in entries[1:]
        ]
        return (
            f"'{code}' is ambiguous — using the first table entry "
            f"{chosen['name']} ({chosen['sign']}). Other candidates: "
            + "; ".join(others)
            + ". Pass an unambiguous abbreviation or an IANA zone name "
            "to DateTimeTool instead."
        )

    # ------------------------------------------------------------------
    # mode: lookup
    # ------------------------------------------------------------------
    def _lookup(self, value: Any) -> dict:
        entries = self._require_entries(value, "abbr")
        code = entries[0]["abbr"].upper()
        return {
            "status": "success",
            "mode": "lookup",
            "abbr": code,
            "ambiguous": len(entries) > 1,
            "count": len(entries),
            "entries": entries,
        }

    # ------------------------------------------------------------------
    # mode: convert
    # ------------------------------------------------------------------
    def _convert(self, time_value: Any, from_value: Any,
                 to_value: Any) -> dict:
        text = self._normalize_time(time_value)
        from_entries = self._require_entries(from_value, "from_abbr")
        to_entries = self._require_entries(to_value, "to_abbr")

        from_entry = from_entries[0]
        to_entry = to_entries[0]
        from_code = from_entry["abbr"].upper()
        to_code = to_entry["abbr"].upper()

        delta = to_entry["offset_minutes"] - from_entry["offset_minutes"]
        hours, minutes = map(int, text.split(":"))
        total = hours * 60 + minutes + delta
        day_shift, result_minutes = divmod(total, 1440)

        result: dict = {
            "status": "success",
            "mode": "convert",
            "time": text,
            "result_time": (f"{result_minutes // 60:02d}:"
                            f"{result_minutes % 60:02d}"),
            "day_shift": day_shift,
            "from_abbr": from_code,
            "to_abbr": to_code,
            "from_offset_minutes": from_entry["offset_minutes"],
            "to_offset_minutes": to_entry["offset_minutes"],
            "from_sign": from_entry["sign"],
            "to_sign": to_entry["sign"],
            "delta_minutes": delta,
            "delta": _format_offset(delta),
        }
        warning = self._ambiguity_warning(from_code, from_entries) \
            or self._ambiguity_warning(to_code, to_entries)
        if warning:
            result["ambiguous"] = True
            result["warning"] = warning
        else:
            result["ambiguous"] = False
        return result

    # ------------------------------------------------------------------
    # mode: now_offset
    # ------------------------------------------------------------------
    def _now_offset(self, value: Any) -> dict:
        entries = self._require_entries(value, "abbr")
        code = entries[0]["abbr"].upper()
        entry = entries[0]
        result = {
            "status": "success",
            "mode": "now_offset",
            "abbr": code,
            "offset_minutes": entry["offset_minutes"],
            "sign": entry["sign"],
            "dst": entry["dst"],
            "ambiguous": len(entries) > 1,
        }
        warning = self._ambiguity_warning(code, entries)
        if warning:
            result["warning"] = warning
        return result

    # ------------------------------------------------------------------
    # mode: search_by_offset
    # ------------------------------------------------------------------
    def _search_by_offset(self, value: Any) -> dict:
        offset_minutes = self._normalize_offset(value)
        indices = _OFFSET_INDEX.get(offset_minutes, [])
        return {
            "status": "success",
            "mode": "search_by_offset",
            "offset_minutes": offset_minutes,
            "sign": _format_offset(offset_minutes),
            "count": len(indices),
            "entries": [_entry_dict(i) for i in indices],
        }
