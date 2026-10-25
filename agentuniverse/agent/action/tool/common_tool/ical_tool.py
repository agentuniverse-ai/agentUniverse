#!/usr/bin/env python3
"""Offline iCalendar (.ics) parsing, linting, and folding per RFC 5545.

The tool exposes four deterministic modes built strictly on the Python
standard library (``re`` and ``datetime``); ``python-dateutil`` is used
opportunistically for recurrence expansion when installed and is never
required:

* ``parse``  - unfold the RFC 5545 3.1 folding grammar, split every content
               line into name / parameters / value, and return the component
               tree (VCALENDAR, VEVENT, VTODO, VJOURNAL, VTIMEZONE with
               nested STANDARD/DAYLIGHT, VALARM inside VEVENT/VTODO/VJOURNAL),
               the fold-site log, and the calendar-level properties (VERSION /
               PRODID / CALSCALE) with findings for the ones RFC 5545 requires.
* ``lint``   - structural and semantic findings: BEGIN/END nesting, lines
               over the 75-octet SHOULD limit measured in *octets* (not
               characters, so multibyte text counts more), leading-space
               lines that the 3.1 grammar must treat as continuations but
               that read like new properties, missing required properties per
               component, DATE vs DATE-TIME form mismatches, TZID parameters
               without a matching VTIMEZONE, RRULE grammar (FREQ required,
               COUNT+UNTIL mutually exclusive, COUNT/INTERVAL positive
               integers, WKST a weekday, UNTIL form must match DTSTART form
               and its UTC-ness must match DTSTART's zone form), value-type
               checks (PRIORITY 0-9, PERCENT-COMPLETE 0-100, SEQUENCE
               non-negative integer, CALSCALE, GEO two floats), parameter
               quoting, and TEXT escapes.
* ``events`` - normalized event list: ISO-normalized start/end, all-day
               detection, implied end resolution (DTEND, DURATION, next
               calendar date for DATE values, same instant per RFC 5545
               3.6.1), recurrence normalization, and the next occurrences
               computed forward from DTSTART with the built-in engine (or
               dateutil when available).
* ``fold``   - re-fold unfolded text per 3.1 so every physical line is at
               most 75 octets, folding at character boundaries only (never
               inside a UTF-8 sequence), and self-verify the
               unfold(fold(x)) == x round trip on logical lines.

Semantics notes:

* Line breaks: RFC 5545 requires CRLF. Bare LF (and bare CR) input is
  accepted so real-world files parse, and lint reports it as an information
  finding (``non_crlf_line_break``) or a warning (``mixed_line_endings``).
* The ``max_components`` cap is enforced on the returned tree: components
  beyond the cap (and their content) are dropped with a single
  ``component_cap_reached`` warning, and parse/events surface
  ``components_truncated``.
* Determinism: no wall-clock reads anywhere. Recurrence occurrences are
  generated forward from DTSTART, never from "now"; caps and scan bounds are
  fixed constants; findings are emitted in line order.
* The recurrence subset supported by the built-in engine is documented in
  the ``events`` output: FREQ in DAILY/WEEKLY/MONTHLY/YEARLY with INTERVAL,
  COUNT, UNTIL, WKST, BYDAY (plain weekdays) for WEEKLY, and BYMONTHDAY
  (positive) for MONTHLY. When ``python-dateutil`` is importable it expands
  the same rules (and more); the ``engine`` field discloses which engine
  produced each answer.
* IANA time-zone arithmetic (TZID to offset math) is intentionally out of
  scope: occurrences keep the DTSTART wall time, which is exactly correct
  for DATE-valued rules and documented for DATE-TIME rules.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

# ---------------------------------------------------------------------------
# RFC 5545 grammar tables (frozen reference tables, not derivations)
# ---------------------------------------------------------------------------

#: Component names registered by RFC 5545 section 7 (components registry).
_KNOWN_COMPONENTS: frozenset[str] = frozenset({
    "VCALENDAR", "VEVENT", "VTODO", "VJOURNAL", "VFREEBUSY",
    "VTIMEZONE", "STANDARD", "DAYLIGHT", "VALARM",
})

#: Components allowed to nest inside another component (RFC 5545 3.6).
_NESTING: dict[str, tuple[str, ...]] = {
    "VCALENDAR": ("VEVENT", "VTODO", "VJOURNAL", "VFREEBUSY", "VTIMEZONE"),
    "VEVENT": ("VALARM",),
    "VTODO": ("VALARM",),
    "VJOURNAL": ("VALARM",),
    "VTIMEZONE": ("STANDARD", "DAYLIGHT"),
}

#: Required properties per component. VEVENT follows RFC 5545 3.6.1 (UID and
#: DTSTAMP required, DTSTART required when no METHOD property is present,
#: which this tool assumes).
_REQUIRED_PROPS: dict[str, tuple[str, ...]] = {
    "VCALENDAR": ("PRODID", "VERSION"),
    "VEVENT": ("UID", "DTSTAMP", "DTSTART"),
    "VTODO": ("UID", "DTSTAMP"),
    "VJOURNAL": ("UID", "DTSTAMP"),
    "VTIMEZONE": ("TZID",),
    "STANDARD": ("DTSTART", "TZOFFSETFROM", "TZOFFSETTO"),
    "DAYLIGHT": ("DTSTART", "TZOFFSETFROM", "TZOFFSETTO"),
    "VALARM": ("ACTION", "TRIGGER"),
}
_REQUIRED_PROP_REF = {
    "VCALENDAR": "RFC 5545 3.7.3/3.7.4",
    "VEVENT": "RFC 5545 3.6.1",
    "VTODO": "RFC 5545 3.6.2",
    "VJOURNAL": "RFC 5545 3.6.3",
    "VTIMEZONE": "RFC 5545 3.6.5",
    "STANDARD": "RFC 5545 3.6.5",
    "DAYLIGHT": "RFC 5545 3.6.5",
    "VALARM": "RFC 5545 3.6.6",
}

#: Property names registered by RFC 5545 8.3.2 (properties registry).
_KNOWN_PROPERTIES: frozenset[str] = frozenset({
    # 3.7 calendar properties
    "CALSCALE", "METHOD", "PRODID", "VERSION",
    # 3.8.1 descriptive
    "ATTACH", "CATEGORIES", "CLASS", "COMMENT", "DESCRIPTION", "GEO",
    "LOCATION", "PERCENT-COMPLETE", "PRIORITY", "RESOURCES", "STATUS",
    "SUMMARY",
    # 3.8.2 date and time
    "COMPLETED", "DTEND", "DUE", "DTSTART", "DURATION", "FREEBUSY", "TRANSP",
    # 3.8.3 time zone
    "TZID", "TZNAME", "TZOFFSETFROM", "TZOFFSETTO", "TZURL",
    # 3.8.4 relationship
    "ATTENDEE", "CONTACT", "ORGANIZER", "RECURRENCE-ID", "RELATED-TO",
    "URL", "UID",
    # 3.8.5 recurrence
    "EXDATE", "RDATE", "RRULE",
    # 3.8.6 alarm
    "ACTION", "REPEAT", "TRIGGER",
    # 3.8.7 change management
    "CREATED", "DTSTAMP", "LAST-MODIFIED", "SEQUENCE",
    # 3.8.8 miscellaneous
    "REQUEST-STATUS",
    # structural
    "BEGIN", "END",
})

#: Parameter names registered by RFC 5545 8.3.3.
_KNOWN_PARAMS: frozenset[str] = frozenset({
    "ALTREP", "CN", "DELEGATED-FROM", "DELEGATED-TO", "DIR", "ENCODING",
    "FMTTYPE", "FBTYPE", "LANGUAGE", "MEMBER", "PARTSTAT", "RANGE",
    "RELATED", "RELTYPE", "ROLE", "RSVP", "SENT-BY", "TZID", "VALUE",
})

#: TEXT-valued properties whose values carry the 3.3.11 escapes.
_TEXT_PROPS: frozenset[str] = frozenset({
    "SUMMARY", "DESCRIPTION", "COMMENT", "LOCATION", "CONTACT", "TZNAME",
    "PRODID", "UID", "RELATED-TO", "CATEGORIES", "RESOURCES", "REQUEST-STATUS",
    "CALSCALE", "METHOD", "CLASS", "STATUS", "TRANSP",
})

#: RRULE rule parts registered by RFC 5545 3.3.10.
_KNOWN_RULE_PARTS: frozenset[str] = frozenset({
    "FREQ", "UNTIL", "COUNT", "INTERVAL", "BYSECOND", "BYMINUTE", "BYHOUR",
    "BYDAY", "BYMONTHDAY", "BYYEARDAY", "BYWEEKNO", "BYMONTH", "BYSETPOS",
    "WKST",
})

_KNOWN_FREQ: frozenset[str] = frozenset({
    "SECONDLY", "MINUTELY", "HOURLY", "DAILY", "WEEKLY", "MONTHLY", "YEARLY",
})

#: Date-valued properties checked for DATE / DATE-TIME form (3.8.2.x).
_DATETIME_PROPS: frozenset[str] = frozenset({
    "DTSTART", "DTEND", "DUE", "COMPLETED", "RECURRENCE-ID",
    "CREATED", "DTSTAMP", "LAST-MODIFIED", "EXDATE", "RDATE",
})

#: The built-in recurrence engine's supported subset (echoed in output).
_BUILTIN_SUBSET = (
    "FREQ=DAILY|WEEKLY|MONTHLY|YEARLY with INTERVAL, COUNT, UNTIL, WKST; "
    "BYDAY (plain weekdays) with WEEKLY; BYMONTHDAY (positive) with MONTHLY"
)

_WEEKDAY_NAMES: dict[str, int] = {
    "MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6,
}

# Grammar fragments (RFC 5545 3.1, 3.3.4, 3.3.5, 3.3.6, 3.3.10, 3.3.14).
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*$")
_DATE_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})$")
_DATETIME_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})(Z?)$")
_DURATION_RE = re.compile(
    r"^([+-]?)P(?:(\d+)W)?(?:(\d+)D)?"
    r"(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$"
)
_TZOFFSET_RE = re.compile(r"^[+-]\d{4}(\d{2})?$")
_GEO_RE = re.compile(
    r"^[+-]?(?:\d+(?:\.\d+)?|\.\d+);[+-]?(?:\d+(?:\.\d+)?|\.\d+)$"
)
_BYDAY_ITEM_RE = re.compile(r"^([+-]?\d{1,2})?(MO|TU|WE|TH|FR|SA|SU)$")
_LOOKS_LIKE_PROPERTY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*:")
_INT_RE = re.compile(r"^\d+$")
_UNTIL_DATE_RE = re.compile(r"^\d{8}$")
_UNTIL_DATETIME_RE = re.compile(r"^\d{8}T\d{6}Z?$")

_UTCTZ = timezone.utc


def _octets(text: str) -> int:
    """Length of ``text`` in UTF-8 octets (RFC 5545 measures octets, not chars)."""
    return len(text.encode("utf-8", errors="replace"))


# ---------------------------------------------------------------------------
# Unfolding / folding (RFC 5545 3.1)
# ---------------------------------------------------------------------------

def _detect_line_endings(text: str) -> dict[str, Any]:
    """Count CRLF / lone LF / lone CR occurrences in the raw text."""
    crlf = text.count("\r\n")
    lone_lf = text.count("\n") - crlf
    lone_cr = text.count("\r") - crlf
    if crlf and not lone_lf and not lone_cr:
        mode = "CRLF"
    elif not crlf and lone_lf and not lone_cr:
        mode = "LF"
    elif not crlf and lone_cr and not lone_lf:
        mode = "CR"
    elif not crlf and not lone_lf and not lone_cr:
        mode = "NONE"
    else:
        mode = "MIXED"
    return {
        "crlf": crlf, "lone_lf": lone_lf, "lone_cr": lone_cr,
        "mode": mode, "mixed": mode == "MIXED",
    }


def _split_physical(text: str) -> list[str]:
    """Split on CRLF / CR / LF and drop one trailing empty piece."""
    physical = re.split(r"\r\n|\r|\n", text)
    if physical and physical[-1] == "":
        physical.pop()
    return physical


def _unfold(text: str) -> dict[str, Any]:
    """Unfold per 3.1: CRLF + one SPACE/HTAB is removed.

    Returns the logical lines, the fold-site log, and the anomalies only the
    unfolding stage can see: a continuation line with nothing to continue,
    and continuation lines that read like fresh content lines under the 3.1
    grammar-ambiguity note.
    """
    physical = _split_physical(text)
    logical: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []
    for index, raw in enumerate(physical, 1):
        if raw[:1] in (" ", "\t"):
            piece = raw[1:]
            if not logical:
                anomalies.append({
                    "code": "continuation_without_previous",
                    "severity": "error", "line": index,
                    "message": (
                        f"Physical line {index} starts with a linear white-space "
                        "character but there is no previous line to continue "
                        "(RFC 5545 3.1: CRLF + SPACE/HTAB only continues a line)."
                    ),
                })
                logical.append({"text": piece, "physical": index, "folds": 0})
                continue
            target = logical[-1]
            target["text"] += piece
            target["folds"] += 1
            if _LOOKS_LIKE_PROPERTY_RE.match(piece):
                anomalies.append({
                    "code": "suspicious_continuation",
                    "severity": "warning", "line": index,
                    "message": (
                        f"Continuation at physical line {index} reads like a new "
                        "content line ('NAME:value'). The RFC 5545 3.1 grammar "
                        "forces this text to be treated as a continuation of the "
                        "previous line; a producer almost certainly emitted a "
                        "property with a leading space or folded two separate "
                        "properties together."
                    ),
                })
        else:
            logical.append({"text": raw, "physical": index, "folds": 0})
    fold_sites = [
        {"logical_line": position, "physical_line": entry["physical"],
         "continuations": entry["folds"]}
        for position, entry in enumerate(logical, 1) if entry["folds"]
    ]
    return {
        "logical": logical,
        "fold_sites": fold_sites,
        "anomalies": anomalies,
        "physical_count": len(physical),
    }


def _fold_line(line: str, limit: int = 75) -> list[str]:
    """Fold one logical line: the first piece fits ``limit`` octets; every
    continuation is one SPACE plus at most ``limit - 1`` content octets.

    Folding happens at character boundaries only, so a UTF-8 sequence is
    never split (the 3.1 implementation note about mid-sequence folds).
    """
    if _octets(line) <= limit:
        return [line]
    pieces: list[str] = []
    budget = limit
    start = 0
    text_length = len(line)
    while start < text_length:
        end = start
        while end < text_length and _octets(line[start:end + 1]) <= budget:
            end += 1
        if end == start:  # defensive: single character wider than the budget
            end = start + 1
        pieces.append(line[start:end])
        start = end
        budget = limit - 1  # each continuation costs one SPACE
    return pieces


def _fold_text(text: str) -> str:
    """Fold every logical line of ``text``; join with CRLF and a final CRLF."""
    physical: list[str] = []
    for raw in _split_physical(text):
        folded = _fold_line(raw)
        physical.append(folded[0])
        physical.extend(" " + piece for piece in folded[1:])
    return "\r\n".join(physical) + "\r\n" if physical else ""


# ---------------------------------------------------------------------------
# Content line grammar (RFC 5545 3.1)
# ---------------------------------------------------------------------------

def _split_unquoted(text: str, separator: str) -> list[str]:
    """Split on ``separator`` while respecting double-quoted param values."""
    parts: list[str] = []
    buf: list[str] = []
    in_quotes = False
    for ch in text:
        if ch == '"':
            in_quotes = not in_quotes
            buf.append(ch)
        elif ch == separator and not in_quotes:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    return parts


def _parse_content_line(raw: str) -> dict[str, Any]:
    """Parse ``name *(';' param) ':' value`` from one unfolded line."""
    head: str | None = None
    value = ""
    in_quotes = False
    for index, ch in enumerate(raw):
        if ch == '"':
            in_quotes = not in_quotes
        elif ch == ":" and not in_quotes:
            head = raw[:index]
            value = raw[index + 1:]
            break
    if head is None:
        return {"ok": False, "error": "missing_colon"}
    segments = _split_unquoted(head, ";")
    name = segments[0]
    params: dict[str, list[str]] = {}
    param_order: list[str] = []
    param_issues: list[dict[str, Any]] = []
    for segment in segments[1:]:
        if "=" not in segment:
            param_issues.append({
                "code": "malformed_param", "severity": "warning",
                "detail": segment[:80],
                "message": f"Parameter '{segment[:80]}' lacks '=' (RFC 5545 3.1).",
            })
            continue
        pname, _, raw_values = segment.partition("=")
        if not _NAME_RE.match(pname):
            param_issues.append({
                "code": "invalid_param_name", "severity": "warning",
                "detail": pname[:80],
                "message": f"Invalid parameter name '{pname[:80]}' (RFC 5545 3.1).",
            })
        values: list[str] = []
        for raw_value in _split_unquoted(raw_values, ","):
            if raw_value.count('"') % 2 == 1:
                param_issues.append({
                    "code": "mismatched_param_quotes", "severity": "error",
                    "detail": f"{pname}={raw_value[:80]}",
                    "message": (
                        f"Parameter {pname} has an unbalanced double quote "
                        "(RFC 5545 3.1 param-value / quoted-string)."
                    ),
                })
            if len(raw_value) >= 2 and raw_value.startswith('"') and raw_value.endswith('"'):
                values.append(raw_value[1:-1])
            else:
                values.append(raw_value)
        if not values or values == [""]:
            param_issues.append({
                "code": "empty_param_value", "severity": "warning",
                "detail": pname,
                "message": f"Parameter {pname} has an empty value (RFC 5545 3.1).",
            })
        key = pname.upper()
        if key not in params:
            params[key] = values
            param_order.append(key)
        else:
            params[key].extend(values)
    return {
        "ok": True, "name": name, "params": params,
        "param_order": param_order, "value": value,
        "param_issues": param_issues,
    }


def _unescape_text(value: str) -> tuple[str, list[str]]:
    """Apply the 3.3.11 TEXT escapes; return the bad escape tokens."""
    out: list[str] = []
    bad: list[str] = []
    index = 0
    length = len(value)
    while index < length:
        ch = value[index]
        if ch != "\\":
            out.append(ch)
            index += 1
            continue
        if index + 1 >= length:
            bad.append("<trailing>")
            break
        nxt = value[index + 1]
        if nxt in ("n", "N"):
            out.append("\n")
        elif nxt in ("\\", ";", ","):
            out.append(nxt)
        else:
            bad.append("\\" + nxt)
            out.append(nxt)
        index += 2
    return "".join(out), bad


# ---------------------------------------------------------------------------
# Value grammars (RFC 5545 3.3)
# ---------------------------------------------------------------------------

def _parse_ical_date(raw: str) -> dict[str, Any]:
    """DATE (3.3.4): YYYYMMDD."""
    match = _DATE_RE.match(raw)
    if not match:
        return {"ok": False, "error": "not_a_date"}
    year, month, day = (int(g) for g in match.groups())
    try:
        parsed = date(year, month, day)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "date": parsed, "iso": parsed.isoformat(), "form": "DATE"}


def _parse_ical_datetime(raw: str) -> dict[str, Any]:
    """DATE-TIME (3.3.5): YYYYMMDDTHHMMSS[Z]. Seconds are required; 60 is the
    leap-second allowance of the grammar (computation clamps it to 59)."""
    match = _DATETIME_RE.match(raw)
    if not match:
        return {"ok": False, "error": "not_a_datetime"}
    year, month, day, hour, minute, second, zulu = match.groups()
    try:
        parsed_date = date(int(year), int(month), int(day))
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    leap_second = second == "60"
    if not leap_second and (int(hour) > 23 or int(minute) > 59 or int(second) > 59):
        return {"ok": False, "error": f"invalid time {hour}:{minute}:{second}"}
    parsed = datetime(
        parsed_date.year, parsed_date.month, parsed_date.day,
        int(hour), int(minute), 59 if leap_second else int(second),
        tzinfo=_UTCTZ if zulu == "Z" else None,
    )
    return {
        "ok": True, "datetime": parsed, "date": parsed_date,
        "iso": parsed.isoformat(), "form": "DATE-TIME",
        "utc": zulu == "Z", "leap_second": leap_second,
    }


def _parse_duration(raw: str) -> dict[str, Any]:
    """DURATION (3.3.6): [+/-]P[nW][nD][T[nH][nM][nS]]."""
    match = _DURATION_RE.match(raw)
    if not match:
        return {"ok": False, "error": "not_a_duration"}
    sign, weeks, days, hours, minutes, seconds = match.groups()
    if not any((weeks, days, hours, minutes, seconds)):
        return {"ok": False, "error": "no duration components"}
    if "T" in raw and not any((hours, minutes, seconds)):
        return {"ok": False, "error": "T without time components"}  # e.g. P1DT
    weeks_n, days_n, hours_n, minutes_n, seconds_n = (
        int(n) if n else 0 for n in (weeks, days, hours, minutes, seconds)
    )
    delta = timedelta(
        weeks=weeks_n, days=days_n, hours=hours_n,
        minutes=minutes_n, seconds=seconds_n,
    )
    if sign == "-":
        delta = -delta
    return {
        "ok": True, "timedelta": delta, "sign": sign or "+",
        "weeks": weeks_n, "days": days_n, "hours": hours_n,
        "minutes": minutes_n, "seconds": seconds_n,
        "total_seconds": int(delta.total_seconds()), "iso8601": raw,
    }


def _parse_rrule(raw: str) -> dict[str, Any]:
    """Parse the RECUR value (3.3.10 / 3.8.5.3) plus grammar findings."""
    parts: dict[str, str] = {}
    duplicates: list[str] = []
    findings: list[dict[str, Any]] = []
    for chunk in raw.split(";"):
        if not chunk:
            continue
        if "=" not in chunk:
            findings.append({
                "code": "rrule_invalid_value", "severity": "warning",
                "detail": chunk[:80],
                "message": f"RRULE part '{chunk[:80]}' lacks '=' (RFC 5545 3.3.10).",
            })
            continue
        key, _, value = chunk.partition("=")
        if key in parts:
            duplicates.append(key)
        parts[key] = value
    freq = parts.get("FREQ")
    if not freq:
        findings.append({
            "code": "rrule_missing_freq", "severity": "error",
            "message": "RRULE has no FREQ rule part (RFC 5545 3.8.5.3: FREQ MUST be specified).",
        })
    elif freq not in _KNOWN_FREQ:
        findings.append({
            "code": "rrule_invalid_value", "severity": "error",
            "detail": f"FREQ={freq}",
            "message": f"Unknown FREQ value '{freq}' (RFC 5545 3.3.10).",
        })
    for key in parts:
        if key not in _KNOWN_RULE_PARTS:
            findings.append({
                "code": "rrule_unknown_rule_part", "severity": "warning",
                "detail": key,
                "message": f"Unknown RRULE rule part '{key}' (RFC 5545 3.3.10).",
            })
    if "COUNT" in parts and "UNTIL" in parts:
        findings.append({
            "code": "rrule_count_until_exclusive", "severity": "error",
            "message": "RRULE specifies both COUNT and UNTIL (RFC 5545 3.3.10: they MUST NOT occur in the same rule).",
        })
    if "COUNT" in parts and (not _INT_RE.match(parts["COUNT"]) or int(parts["COUNT"]) < 1):
        findings.append({
            "code": "rrule_invalid_value", "severity": "error",
            "detail": f"COUNT={parts['COUNT']}",
            "message": "RRULE COUNT must be a positive integer (RFC 5545 3.3.10).",
        })
    if "INTERVAL" in parts and (not _INT_RE.match(parts["INTERVAL"]) or int(parts["INTERVAL"]) < 1):
        findings.append({
            "code": "rrule_invalid_value", "severity": "error",
            "detail": f"INTERVAL={parts['INTERVAL']}",
            "message": "RRULE INTERVAL must be a positive integer (RFC 5545 3.3.10).",
        })
    if "WKST" in parts and parts["WKST"] not in _WEEKDAY_NAMES:
        findings.append({
            "code": "rrule_invalid_value", "severity": "error",
            "detail": f"WKST={parts['WKST']}",
            "message": "RRULE WKST must be a weekday name MO..SU (RFC 5545 3.3.10).",
        })
    byday: list[str] = []
    if "BYDAY" in parts:
        for item in parts["BYDAY"].split(","):
            item = item.strip().upper()
            if not _BYDAY_ITEM_RE.match(item):
                findings.append({
                    "code": "rrule_invalid_value", "severity": "error",
                    "detail": f"BYDAY={item}",
                    "message": f"Invalid BYDAY entry '{item}' (RFC 5545 3.3.10 weekdaynum).",
                })
            else:
                byday.append(item)
    bymonthday: list[int] = []
    if "BYMONTHDAY" in parts:
        for item in parts["BYMONTHDAY"].split(","):
            item = item.strip()
            if not re.match(r"^[+-]?\d{1,2}$", item) or not 1 <= abs(int(item)) <= 31:
                findings.append({
                    "code": "rrule_invalid_value", "severity": "error",
                    "detail": f"BYMONTHDAY={item}",
                    "message": f"Invalid BYMONTHDAY entry '{item}' (RFC 5545 3.3.10).",
                })
            else:
                bymonthday.append(int(item))
    until: dict[str, Any] | None = None
    if "UNTIL" in parts:
        until_raw = parts["UNTIL"]
        if _UNTIL_DATE_RE.match(until_raw):
            parsed = _parse_ical_date(until_raw)
            if parsed.get("ok"):
                until = {"raw": until_raw, "form": "DATE", "iso": parsed["iso"],
                         "date": parsed["date"]}
            else:
                until = {"raw": until_raw, "form": "DATE", "invalid": parsed.get("error")}
                findings.append({
                    "code": "rrule_invalid_value", "severity": "error",
                    "detail": f"UNTIL={until_raw}",
                    "message": f"RRULE UNTIL is not a valid date ({parsed.get('error')}).",
                })
        elif _UNTIL_DATETIME_RE.match(until_raw):
            parsed = _parse_ical_datetime(until_raw)
            if parsed.get("ok"):
                until = {"raw": until_raw, "form": "DATE-TIME",
                         "utc": until_raw.endswith("Z"),
                         "iso": parsed["iso"], "datetime": parsed["datetime"]}
            else:
                until = {"raw": until_raw, "form": "DATE-TIME", "invalid": parsed.get("error")}
                findings.append({
                    "code": "rrule_invalid_value", "severity": "error",
                    "detail": f"UNTIL={until_raw}",
                    "message": f"RRULE UNTIL is not a valid date-time ({parsed.get('error')}).",
                })
        else:
            findings.append({
                "code": "rrule_invalid_value", "severity": "error",
                "detail": f"UNTIL={until_raw}",
                "message": "RRULE UNTIL must be a DATE or DATE-TIME value (RFC 5545 3.3.10).",
            })
    normalized: dict[str, Any] = {
        "FREQ": freq if freq in _KNOWN_FREQ else freq,
        "INTERVAL": int(parts["INTERVAL"]) if "INTERVAL" in parts and _INT_RE.match(parts["INTERVAL"]) else 1,
        "COUNT": int(parts["COUNT"]) if "COUNT" in parts and _INT_RE.match(parts["COUNT"]) else None,
        "UNTIL": until,
        "BYDAY": byday,
        "BYMONTHDAY": bymonthday,
        "WKST": parts["WKST"] if parts.get("WKST") in _WEEKDAY_NAMES else "MO",
        "present_parts": parts,
    }
    extras = [k for k in parts if k not in {
        "FREQ", "INTERVAL", "COUNT", "UNTIL", "BYDAY", "BYMONTHDAY", "WKST",
    }]
    normalized["extras"] = extras
    return {
        "parts": parts, "normalized": normalized, "findings": findings,
        "duplicates": duplicates, "extras": extras,
    }


# ---------------------------------------------------------------------------
# Recurrence expansion
# ---------------------------------------------------------------------------

def _builtin_occurrences(
    rule: dict[str, Any],
    dtstart: date | datetime,
    count: int,
    cap: int,
) -> dict[str, Any]:
    """Expand the supported RRULE subset forward from ``dtstart``.

    Occurrences keep the DTSTART wall time; no wall-clock or IANA time-zone
    arithmetic is performed. Mirrors dateutil on the documented subset:
    DTSTART is the first occurrence when it matches its own pattern, COUNT
    counts DTSTART, UNTIL is inclusive, and calendar-invalid candidates
    (February 30, day 31 of a short month, February 29 of a common year)
    are skipped rather than clamped.
    """
    if count <= 0:
        return {"occurrences": [], "unsupported": [], "hit_scan_cap": False}
    freq = rule.get("FREQ")
    interval = rule.get("INTERVAL") or 1
    is_datetime = isinstance(dtstart, datetime)
    start_date = dtstart.date() if is_datetime else dtstart
    start_time = dtstart.time() if is_datetime else None
    present = rule.get("present_parts") or {}
    byday = rule.get("BYDAY") or []
    bymonthday = rule.get("BYMONTHDAY") or []

    unsupported: list[str] = []
    if freq not in ("DAILY", "WEEKLY", "MONTHLY", "YEARLY"):
        unsupported.append(f"FREQ={freq}")
    if "BYDAY" in present and freq != "WEEKLY":
        unsupported.append("BYDAY outside WEEKLY")
    for entry in byday:
        if re.match(r"^[+-]\d", entry):
            unsupported.append(f"BYDAY ordinal {entry}")
    if bymonthday and freq != "MONTHLY":
        unsupported.append("BYMONTHDAY outside MONTHLY")
    if any(d < 0 for d in bymonthday):
        unsupported.append("BYMONTHDAY negative")
    unsupported.extend(rule.get("extras") or [])
    if unsupported:
        return {"occurrences": [], "unsupported": unsupported, "hit_scan_cap": False}

    # COUNT=0 is invalid grammar (lint flags it); both engines read it as
    # unbounded so the answer stays deterministic instead of half-empty.
    limit_count = rule.get("COUNT") or None
    until = rule.get("UNTIL") if isinstance(rule.get("UNTIL"), dict) else None
    until_date = until.get("date") if until else None
    until_datetime = until.get("datetime") if until else None
    wkst = _WEEKDAY_NAMES.get(rule.get("WKST", "MO"), 0)

    def at_bound(candidate: date) -> bool:
        """Inclusive UNTIL bound. Zone-free comparison rules:

        * aware DTSTART vs UNTIL Z: exact instant comparison;
        * naive DTSTART (TZID form) vs UTC UNTIL: the bound instant is read
          as wall time (the Z dropped), which matches the RFC 5545 3.8.5.3
          examples for negative-offset zones and needs no IANA math;
        * DATE-form DTSTART with a DATE UNTIL: whole-day inclusive;
        * DATE-form UNTIL against a DATE-TIME DTSTART (a form RFC 5545
          3.3.10 forbids): the bound is that date at midnight, matching
          dateutil's reading.
        """
        if until_date is not None:
            if is_datetime:
                return datetime.combine(candidate, start_time) > \
                    datetime.combine(until_date, time())
            return candidate > until_date
        if until_datetime is not None:
            bound = until_datetime
            if is_datetime:
                candidate_dt = datetime.combine(candidate, start_time,
                                                tzinfo=dtstart.tzinfo)
                if dtstart.tzinfo is not None:
                    if bound.tzinfo is None:
                        bound = bound.replace(tzinfo=_UTCTZ)
                    return candidate_dt > bound
                return candidate_dt > bound.replace(tzinfo=None)
            return candidate > bound.date()
        return False

    results: list[date | datetime] = []
    hit_cap = False

    def make(candidate: date) -> date | datetime:
        if is_datetime:
            return datetime.combine(candidate, start_time, tzinfo=dtstart.tzinfo)
        return candidate

    def emit(candidate: date) -> bool:
        """Record one candidate; True means stop generating."""
        if candidate < start_date:
            return False
        if at_bound(candidate):
            return True
        results.append(make(candidate))
        if limit_count is not None and len(results) >= limit_count:
            return True
        return len(results) >= count

    if freq == "DAILY":
        for k in range(cap):
            if emit(start_date + timedelta(days=k * interval)):
                break
        else:
            hit_cap = True
    elif freq == "WEEKLY":
        # Emit in chronological order: sort by the offset from WKST, not by
        # the weekday number (with WKST=SU, Sunday comes first in a week).
        if byday:
            weekdays = sorted({_WEEKDAY_NAMES[d[-2:]] for d in byday},
                              key=lambda w: (w - wkst) % 7)
        else:
            weekdays = [start_date.weekday()]
        week_anchor = start_date - timedelta(days=(start_date.weekday() - wkst) % 7)
        stop = False
        for k in range(cap):
            week_start = week_anchor + timedelta(weeks=k * interval)
            for weekday in weekdays:
                if emit(week_start + timedelta(days=(weekday - wkst) % 7)):
                    stop = True
                    break
            if stop:
                break
        else:
            hit_cap = True
    elif freq == "MONTHLY":
        month_days = sorted({d for d in bymonthday if d > 0}) if bymonthday \
            else [start_date.day]
        stop = False
        for k in range(cap):
            month_index = start_date.year * 12 + (start_date.month - 1) + k * interval
            year, month = divmod(month_index, 12)
            for day in month_days:
                try:
                    candidate = date(year, month + 1, day)
                except ValueError:
                    continue  # e.g. February 31: skipped, dateutil-compatible
                if emit(candidate):
                    stop = True
                    break
            if stop:
                break
        else:
            hit_cap = True
    else:  # YEARLY
        for k in range(cap):
            try:
                candidate = date(start_date.year + k * interval,
                                 start_date.month, start_date.day)
            except ValueError:
                continue  # e.g. February 29 of a common year
            if emit(candidate):
                break
        else:
            hit_cap = True

    return {
        "occurrences": results[:count],
        "unsupported": [],
        "hit_scan_cap": hit_cap and len(results) < count,
    }


def _dateutil_occurrences(
    rule: dict[str, Any],
    dtstart: date | datetime,
    count: int,
) -> dict[str, Any] | None:
    """Expand with python-dateutil when importable; None when unavailable or
    the rule uses something dateutil cannot express through this mapping."""
    try:
        from dateutil import rrule as du_module  # type: ignore
    except Exception:  # pragma: no cover - depends on the environment
        return None
    du = du_module.rrule
    if count <= 0:
        return {"occurrences": [], "engine_notes": "python-dateutil"}
    freq = rule.get("FREQ")
    freq_map = {
        "DAILY": du_module.DAILY, "WEEKLY": du_module.WEEKLY,
        "MONTHLY": du_module.MONTHLY, "YEARLY": du_module.YEARLY,
        "HOURLY": du_module.HOURLY, "MINUTELY": du_module.MINUTELY,
        "SECONDLY": du_module.SECONDLY,
    }
    if freq not in freq_map:
        return None
    weekday_codes = {
        "MO": du_module.MO, "TU": du_module.TU, "WE": du_module.WE,
        "TH": du_module.TH, "FR": du_module.FR, "SA": du_module.SA,
        "SU": du_module.SU,
    }
    is_date_form = not isinstance(dtstart, datetime)
    seed = datetime.combine(dtstart, time()) if is_date_form else dtstart
    kwargs: dict[str, Any] = {"freq": freq_map[freq], "dtstart": seed,
                              "interval": rule.get("INTERVAL") or 1}
    if rule.get("COUNT"):
        kwargs["count"] = rule["COUNT"]
    else:
        # Never materialize an unbounded generator (dateutil would iterate
        # to the year 10000); only ``count`` results are ever needed and a
        # COUNT bound does not change the first N occurrences.
        kwargs["count"] = max(count, 1)
    until = rule.get("UNTIL") if isinstance(rule.get("UNTIL"), dict) else None
    if until and not rule.get("COUNT"):
        if "datetime" in until:
            bound = until["datetime"]
            if seed.tzinfo is None and bound.tzinfo is not None:
                bound = bound.replace(tzinfo=None)  # wall-time reading
            elif seed.tzinfo is not None and bound.tzinfo is None:
                bound = bound.replace(tzinfo=_UTCTZ)
            kwargs["until"] = bound
        elif "date" in until:
            kwargs["until"] = datetime.combine(until["date"], time())
    if rule.get("BYDAY"):
        byweekday = []
        for entry in rule["BYDAY"]:
            match = _BYDAY_ITEM_RE.match(entry)
            if not match:
                return None
            ordinal, code = match.groups()
            base = weekday_codes[code]
            byweekday.append(base(int(ordinal)) if ordinal else base)
        kwargs["byweekday"] = byweekday
    if rule.get("BYMONTHDAY"):
        kwargs["bymonthday"] = rule["BYMONTHDAY"]
    if rule.get("WKST"):
        kwargs["wkst"] = weekday_codes.get(rule["WKST"], du_module.MO)
    extra_map = {
        "BYSECOND": "bysecond", "BYMINUTE": "byminute", "BYHOUR": "byhour",
        "BYYEARDAY": "byyearday", "BYWEEKNO": "byweekno", "BYMONTH": "bymonth",
        "BYSETPOS": "bysetpos",
    }
    parts = rule.get("present_parts") or {}
    for extra in rule.get("extras") or []:
        key = extra_map.get(extra)
        if key is None or extra not in parts:
            return None
        try:
            kwargs[key] = [int(v) for v in parts[extra].split(",")]
        except ValueError:
            return None
    try:
        expanded = list(du(**kwargs))[:count]
    except Exception:
        return None
    if is_date_form:
        expanded = [value.date() for value in expanded]
    return {"occurrences": expanded, "engine_notes": "python-dateutil"}


# ---------------------------------------------------------------------------
# Component tree assembly
# ---------------------------------------------------------------------------

def _build_components(
    logical_lines: list[dict[str, Any]],
    anomalies: list[dict[str, Any]],
    max_components: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    """Assemble the component tree from BEGIN/END lines (RFC 5545 3.6)."""
    roots: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = list(anomalies)
    truncated = False
    component_count = 0
    cap_reported = False
    for position, entry in enumerate(logical_lines, 1):
        raw = entry["text"]
        if raw == "":
            findings.append({
                "code": "empty_line", "severity": "warning", "line": position,
                "message": "Empty content line (RFC 5545 3.1 contentline is never empty).",
            })
            continue
        parsed = _parse_content_line(raw)
        if not parsed.get("ok"):
            findings.append({
                "code": "missing_colon", "severity": "error", "line": position,
                "message": f"Content line {position} has no ':' name/value separator: '{raw[:60]}'.",
            })
            continue
        name_upper = parsed["name"].upper()
        if not _NAME_RE.match(parsed["name"]):
            findings.append({
                "code": "invalid_property_name", "severity": "error", "line": position,
                "detail": parsed["name"][:60],
                "message": f"Invalid property name '{parsed['name'][:60]}' (RFC 5545 3.1 iana-token).",
            })
        for issue in parsed.get("param_issues", []):
            issue["line"] = position
            issue.setdefault("property", name_upper)
            findings.append(issue)
        value = parsed["value"]
        if name_upper == "BEGIN":
            component_count += 1
            if component_count > max_components:
                # Enforce the cap: the component and everything inside it are
                # dropped from the tree; a single finding discloses the cut.
                truncated = True
                if not cap_reported:
                    findings.append({
                        "code": "component_cap_reached", "severity": "warning",
                        "line": position, "detail": value.upper(),
                        "message": (
                            f"Calendar has more than max_components={max_components} "
                            f"components; BEGIN:{value.upper()} (logical line "
                            f"{position}) and everything after it are dropped "
                            "from the returned tree."
                        ),
                    })
                    cap_reported = True
                stack.append({"_skipped": True})
                continue
            node = {
                "type": value.upper(), "raw_type": value, "line": position,
                "end_line": None, "properties": [], "components": [],
            }
            if stack:
                stack[-1]["components"].append(node)
            else:
                if roots:
                    findings.append({
                        "code": "content_outside_vcalendar", "severity": "error",
                        "line": position, "detail": value.upper(),
                        "message": (
                            f"Component {value.upper()} begins outside any VCALENDAR "
                            "(RFC 5545 3.4: components nest inside an iCalendar object)."
                        ),
                    })
                roots.append(node)
            stack.append(node)
            continue
        if name_upper == "END":
            expected = value.upper()
            if not stack:
                findings.append({
                    "code": "unexpected_end", "severity": "error", "line": position,
                    "detail": expected,
                    "message": f"END:{value} with no matching BEGIN (RFC 5545 3.6).",
                })
                continue
            top = stack[-1]
            if top.get("_skipped"):
                stack.pop()
                continue
            if top["type"] != expected:
                findings.append({
                    "code": "component_end_mismatch", "severity": "error",
                    "line": position,
                    "detail": f"expected END:{top['type']}, got END:{expected}",
                    "message": (
                        f"END:{value} closes {top['type']} (opened at logical line "
                        f"{top['line']}); components must nest properly (RFC 5545 3.6)."
                    ),
                })
                stack.pop()
                continue
            top["end_line"] = position
            stack.pop()
            continue
        prop = {
            "name": name_upper, "raw_name": parsed["name"],
            "params": parsed["params"], "value": value, "line": position,
        }
        if stack and not stack[-1].get("_skipped"):
            stack[-1]["properties"].append(prop)
        elif stack:
            continue  # inside a capped-out component: dropped with the cap finding
        else:
            findings.append({
                "code": "content_outside_vcalendar", "severity": "error",
                "line": position, "detail": name_upper,
                "message": f"Property {name_upper} appears outside any component (RFC 5545 3.4).",
            })
    for node in stack:
        if node.get("_skipped"):
            continue
        findings.append({
            "code": "component_not_closed", "severity": "error",
            "line": node["line"], "detail": node["type"],
            "message": f"BEGIN:{node['raw_type']} at logical line {node['line']} is never closed (RFC 5545 3.6).",
        })
    return roots, findings, truncated


def _iter_components(components: list[dict[str, Any]]):
    for node in components:
        yield node
        yield from _iter_components(node["components"])


# ---------------------------------------------------------------------------
# Lint: semantic checks over the assembled tree
# ---------------------------------------------------------------------------

def _value_pieces(name: str, raw: str) -> list[str]:
    """Multi-valued date properties list several values comma-separated."""
    return raw.split(",") if name in ("EXDATE", "RDATE") else [raw]


def _check_datetime_form(prop: dict[str, Any], piece: str) -> list[dict[str, Any]]:
    """VALUE parameter vs actual DATE/DATE-TIME form plus grammar validation."""
    findings: list[dict[str, Any]] = []
    name = prop["name"]
    declared = None
    for value in prop["params"].get("VALUE", []):
        declared = value.upper()
    allowed = ("DATE", "DATE-TIME", "PERIOD") if name == "RDATE" else ("DATE", "DATE-TIME")
    actual = None
    if _parse_ical_datetime(piece).get("ok"):
        actual = "DATE-TIME"
    elif _parse_ical_date(piece).get("ok"):
        actual = "DATE"
    if declared not in (None,) + allowed and actual is not None:
        findings.append({
            "code": "unknown_value_type", "severity": "warning",
            "line": prop["line"], "property": name, "detail": declared,
            "message": f"{name} declares unknown VALUE type '{declared}'.",
        })
    if actual is None and declared in (None, "DATE", "DATE-TIME"):
        findings.append({
            "code": "invalid_datetime", "severity": "error",
            "line": prop["line"], "property": name, "detail": piece[:40],
            "message": (
                f"{name} value '{piece[:40]}' is neither a DATE nor a DATE-TIME "
                "(RFC 5545 3.3.4/3.3.5)."
            ),
        })
        return findings
    if declared == "DATE" and actual == "DATE-TIME":
        findings.append({
            "code": "datetime_form_mismatch", "severity": "error",
            "line": prop["line"], "property": name, "detail": piece[:40],
            "message": f"{name};VALUE=DATE carries a DATE-TIME value '{piece[:40]}' (RFC 5545 3.3.4).",
        })
    elif declared == "DATE-TIME" and actual == "DATE":
        findings.append({
            "code": "datetime_form_mismatch", "severity": "error",
            "line": prop["line"], "property": name, "detail": piece[:40],
            "message": f"{name};VALUE=DATE-TIME carries a DATE value '{piece[:40]}' (RFC 5545 3.3.5).",
        })
    if actual == "DATE" and "TZID" in prop["params"]:
        findings.append({
            "code": "tzid_on_date", "severity": "warning",
            "line": prop["line"], "property": name,
            "detail": prop["params"]["TZID"][0][:60],
            "message": (
                f"{name} is a DATE value; the TZID parameter is only defined for "
                "DATE-TIME values (RFC 5545 3.2.19 / 3.8.5.3)."
            ),
        })
    return findings


def _walk_semantic_lint(
    components: list[dict[str, Any]], findings: list[dict[str, Any]],
) -> None:
    """Required properties, value types, escapes, TZID, RRULE per component."""
    tzids_defined: set[str] = set()
    for node in _iter_components(components):
        if node["type"] == "VTIMEZONE":
            for prop in node["properties"]:
                if prop["name"] == "TZID":
                    tzids_defined.add(prop["value"])
    if not any(n["type"] == "VCALENDAR" for n in components):
        findings.append({
            "code": "no_vcalendar", "severity": "error", "line": 1,
            "message": "No VCALENDAR component found (RFC 5545 3.4 requires BEGIN:VCALENDAR).",
        })
    for node in _iter_components(components):
        ctype = node["type"]
        present = {p["name"] for p in node["properties"]}
        for required in _REQUIRED_PROPS.get(ctype, ()):
            if required not in present:
                findings.append({
                    "code": "missing_required_property", "severity": "error",
                    "line": node["line"], "component": ctype, "detail": required,
                    "message": (
                        f"{ctype} (line {node['line']}) is missing required property "
                        f"{required} ({_REQUIRED_PROP_REF.get(ctype, 'RFC 5545 3.6')})."
                    ),
                })
        if ctype not in _KNOWN_COMPONENTS:
            findings.append({
                "code": "unknown_component", "severity": "warning",
                "line": node["line"], "detail": ctype,
                "message": f"Unknown component type '{ctype}' (RFC 5545 3.6 / 8.3.1).",
            })
        allowed = _NESTING.get(ctype)
        if allowed is not None:
            for child in node["components"]:
                if child["type"] not in allowed:
                    findings.append({
                        "code": "invalid_nesting", "severity": "error",
                        "line": child["line"], "component": child["type"],
                        "detail": f"{child['type']} inside {ctype}",
                        "message": (
                            f"{child['type']} (line {child['line']}) cannot nest inside "
                            f"{ctype} (RFC 5545 3.6)."
                        ),
                    })
        dtstart_form = None
        dtstart_zone = None
        dtstart_line = node["line"]
        dtend_form = None
        for prop in node["properties"]:
            name = prop["name"]
            raw = prop["value"]
            if name in _DATETIME_PROPS:
                for piece in _value_pieces(name, raw):
                    if name == "RDATE" and "/" in piece:
                        continue  # PERIOD form: out of this tool's scope
                    findings.extend(_check_datetime_form(prop, piece))
                    if name == "DTSTART":
                        if _parse_ical_datetime(piece).get("ok"):
                            dtstart_form = "DATE-TIME"
                            dtstart_zone = (
                                "utc" if piece.endswith("Z")
                                else "tzid" if prop["params"].get("TZID")
                                else "floating"
                            )
                        elif _parse_ical_date(piece).get("ok"):
                            dtstart_form = "DATE"
                        dtstart_line = prop["line"]
                    elif name == "DTEND":
                        if _parse_ical_datetime(piece).get("ok"):
                            dtend_form = "DATE-TIME"
                        elif _parse_ical_date(piece).get("ok"):
                            dtend_form = "DATE"
                for tzid in prop["params"].get("TZID", []):
                    if tzid not in tzids_defined:
                        findings.append({
                            "code": "tzid_without_vtimezone", "severity": "warning",
                            "line": prop["line"], "property": name,
                            "detail": tzid[:80],
                            "message": (
                                f"{name};TZID={tzid[:80]} references a time zone with no "
                                "matching VTIMEZONE component in this calendar "
                                "(RFC 5545 3.6.5)."
                            ),
                        })
                continue
            if name == "DURATION" and not _parse_duration(raw).get("ok"):
                findings.append({
                    "code": "invalid_duration", "severity": "error",
                    "line": prop["line"], "property": name, "detail": raw[:40],
                    "message": f"DURATION value '{raw[:40]}' is not a valid dur-value (RFC 5545 3.3.6).",
                })
            elif name == "PRIORITY":
                if not _INT_RE.match(raw) or not 0 <= int(raw) <= 9:
                    findings.append({
                        "code": "value_out_of_range", "severity": "error",
                        "line": prop["line"], "property": name, "detail": raw[:20],
                        "message": f"PRIORITY must be an integer 0..9, got '{raw[:20]}' (RFC 5545 3.8.1.9).",
                    })
            elif name == "PERCENT-COMPLETE":
                if not _INT_RE.match(raw) or not 0 <= int(raw) <= 100:
                    findings.append({
                        "code": "value_out_of_range", "severity": "error",
                        "line": prop["line"], "property": name, "detail": raw[:20],
                        "message": f"PERCENT-COMPLETE must be an integer 0..100, got '{raw[:20]}' (RFC 5545 3.8.2.8).",
                    })
            elif name == "GEO" and not _GEO_RE.match(raw):
                findings.append({
                    "code": "invalid_geo", "severity": "error",
                    "line": prop["line"], "property": name, "detail": raw[:40],
                    "message": f"GEO value '{raw[:40]}' is not two semicolon-separated decimal floats (RFC 5545 3.8.1.6).",
                })
            elif name == "SEQUENCE" and not _INT_RE.match(raw):
                findings.append({
                    "code": "value_out_of_range", "severity": "error",
                    "line": prop["line"], "property": name, "detail": raw[:20],
                    "message": f"SEQUENCE must be a non-negative integer, got '{raw[:20]}' (RFC 5545 3.8.7.4).",
                })
            elif name == "CALSCALE" and raw.upper() != "GREGORIAN":
                findings.append({
                    "code": "unknown_calscale", "severity": "warning",
                    "line": prop["line"], "property": name, "detail": raw[:40],
                    "message": f"CALSCALE '{raw[:40]}' is not GREGORIAN, the only scale RFC 5545 3.7.1 defines.",
                })
            elif name in ("TZOFFSETFROM", "TZOFFSETTO") and not _TZOFFSET_RE.match(raw):
                findings.append({
                    "code": "invalid_utc_offset", "severity": "error",
                    "line": prop["line"], "property": name, "detail": raw[:20],
                    "message": f"{name} value '{raw[:20]}' is not [+/-]HHMM[SS] (RFC 5545 3.3.14).",
                })
            elif name in _TEXT_PROPS:
                _, bad = _unescape_text(raw)
                for escape in bad[:10]:
                    findings.append({
                        "code": "invalid_escape", "severity": "error",
                        "line": prop["line"], "property": name,
                        "detail": escape[:20],
                        "message": (
                            f"{name} contains invalid TEXT escape '{escape[:20]}' "
                            "(RFC 5545 3.3.11 allows only \\n \\N \\, \\; \\\\)."
                        ),
                    })
            if name == "RRULE":
                parsed_rule = _parse_rrule(raw)
                for finding in parsed_rule["findings"]:
                    finding["line"] = prop["line"]
                    finding["property"] = "RRULE"
                    finding.setdefault("component", ctype)
                    findings.append(finding)
                if parsed_rule["duplicates"]:
                    findings.append({
                        "code": "rrule_duplicate_part", "severity": "warning",
                        "line": prop["line"], "property": "RRULE",
                        "detail": ",".join(sorted(set(parsed_rule["duplicates"]))),
                        "message": "RRULE repeats a rule part (RFC 5545 3.3.10).",
                    })
                until = parsed_rule["normalized"]["UNTIL"]
                if isinstance(until, dict) and dtstart_form and until.get("form") != dtstart_form:
                    findings.append({
                        "code": "rrule_until_form_mismatch", "severity": "error",
                        "line": prop["line"], "property": "RRULE",
                        "component": ctype,
                        "detail": f"DTSTART {dtstart_form} vs UNTIL {until.get('form')}",
                        "message": (
                            "RRULE UNTIL must have the same value type as DTSTART "
                            f"(DTSTART is {dtstart_form}, UNTIL is {until.get('form')}); "
                            "this is the classic interoperability bug (RFC 5545 3.3.10)."
                        ),
                    })
                elif (isinstance(until, dict) and until.get("form") == "DATE-TIME"
                        and dtstart_form == "DATE-TIME" and dtstart_zone is not None):
                    # RFC 5545 3.3.10: a floating DTSTART needs a local UNTIL;
                    # a UTC or TZID DTSTART needs a UTC UNTIL. Warning, not
                    # error: real-world files (and the RFC's own 3.8.5.3
                    # illustrations) mix these constantly.
                    until_utc = bool(until.get("utc"))
                    if dtstart_zone == "floating" and until_utc:
                        findings.append({
                            "code": "rrule_until_zone_form_mismatch",
                            "severity": "warning", "line": prop["line"],
                            "property": "RRULE", "component": ctype,
                            "detail": "floating DTSTART with UTC UNTIL",
                            "message": (
                                "DTSTART is a date-time with local time (floating), so "
                                "RRULE UNTIL must also be local time, but it ends with "
                                "'Z' (RFC 5545 3.3.10)."
                            ),
                        })
                    elif dtstart_zone in ("utc", "tzid") and not until_utc:
                        findings.append({
                            "code": "rrule_until_zone_form_mismatch",
                            "severity": "warning", "line": prop["line"],
                            "property": "RRULE", "component": ctype,
                            "detail": f"{dtstart_zone} DTSTART with non-UTC UNTIL",
                            "message": (
                                "DTSTART is a date-time with UTC time or a time zone "
                                "reference, so RRULE UNTIL must be UTC time (end with "
                                "'Z'), but it does not (RFC 5545 3.3.10)."
                            ),
                        })
            if prop["raw_name"].upper().startswith("X-"):
                findings.append({
                    "code": "x_property", "severity": "info",
                    "line": prop["line"], "component": ctype,
                    "detail": prop["raw_name"][:60],
                    "message": f"Non-standard property {prop['raw_name'][:60]} (RFC 5545 3.8.8.2 extension point).",
                })
            elif name not in _KNOWN_PROPERTIES:
                findings.append({
                    "code": "unknown_property", "severity": "warning",
                    "line": prop["line"], "component": ctype,
                    "detail": prop["raw_name"][:60],
                    "message": f"Unknown property '{prop['raw_name'][:60]}' (not an RFC 5545 3.7/3.8 name nor X-).",
                })
            for pname in prop["params"]:
                if pname.startswith("X-"):
                    findings.append({
                        "code": "x_param", "severity": "info",
                        "line": prop["line"], "property": name, "detail": pname[:60],
                        "message": f"Non-standard parameter {pname[:60]} (RFC 5545 3.2.10 extension point).",
                    })
                elif pname not in _KNOWN_PARAMS:
                    findings.append({
                        "code": "unknown_param", "severity": "warning",
                        "line": prop["line"], "property": name, "detail": pname[:60],
                        "message": f"Unknown parameter '{pname[:60]}' (not an RFC 5545 3.2 name nor X-).",
                    })
        if ctype == "VEVENT" and dtstart_form and dtend_form and dtstart_form != dtend_form:
            findings.append({
                "code": "datetime_form_mismatch", "severity": "error",
                "line": dtstart_line, "component": ctype,
                "detail": f"DTSTART {dtstart_form} vs DTEND {dtend_form}",
                "message": (
                    "VEVENT DTSTART and DTEND must use the same value form "
                    f"(got {dtstart_form} vs {dtend_form}; RFC 5545 3.8.2.2)."
                ),
            })


def _check_octet_limits(text: str, findings: list[dict[str, Any]]) -> None:
    """The 75-octet SHOULD of 3.1, measured in UTF-8 octets per physical line."""
    for index, piece in enumerate(_split_physical(text), 1):
        octets = _octets(piece)
        if octets > 75:
            findings.append({
                "code": "long_line_over_75_octets", "severity": "warning",
                "line": index, "detail": f"{octets} octets / {len(piece)} chars",
                "folded": piece[:1] in (" ", "\t"),
                "message": (
                    f"Physical line {index} is {octets} octets over {len(piece)} "
                    "characters; RFC 5545 3.1 lines SHOULD NOT exceed 75 octets "
                    "(octets, not characters: multibyte text counts more per character)."
                ),
            })


# ---------------------------------------------------------------------------
# Calendar-level helpers
# ---------------------------------------------------------------------------

def _calendar_props(components: list[dict[str, Any]]) -> dict[str, Any]:
    """VERSION / PRODID / CALSCALE of the first VCALENDAR plus RFC findings."""
    result: dict[str, Any] = {
        "VERSION": {"present": False, "value": None},
        "PRODID": {"present": False, "value": None},
        "CALSCALE": {"present": False, "value": None, "default": "GREGORIAN"},
        "findings": [],
        "vcalendar_count": 0,
    }
    calendars = [c for c in components if c["type"] == "VCALENDAR"]
    result["vcalendar_count"] = len(calendars)
    calendar = calendars[0] if calendars else None
    if calendar is None:
        for key in ("VERSION", "PRODID"):
            result["findings"].append(
                f"missing {key} (required by RFC 5545 3.7 on every VCALENDAR; "
                "no VCALENDAR present)"
            )
        return result
    properties = {p["name"]: p["value"] for p in calendar["properties"]}
    for key in ("VERSION", "PRODID", "CALSCALE"):
        if key in properties:
            result[key] = {"present": True, "value": properties[key]}
    if "VERSION" not in properties:
        result["findings"].append("missing VERSION (required by RFC 5545 3.7.4)")
    if "PRODID" not in properties:
        result["findings"].append("missing PRODID (required by RFC 5545 3.7.3)")
    return result


def _slim_component(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": node["type"],
        "line": node["line"],
        "end_line": node["end_line"],
        "properties": [
            {"name": p["name"], "params": p["params"], "value": p["value"],
             "line": p["line"]}
            for p in node["properties"]
        ],
        "components": [_slim_component(child) for child in node["components"]],
    }


class IcalTool(Tool):
    """Offline iCalendar (.ics) parsing, linting, event normalization, and folding."""

    max_text_chars: int = 1_048_576
    max_logical_lines: int = 10_000
    max_components: int = 2_000
    max_findings: int = 200
    max_events: int = 100
    max_occurrences: int = 3
    max_scan_periods: int = 5_000
    max_fold_sites: int = 500

    _MODES: ClassVar[tuple[str, ...]] = ("parse", "lint", "events", "fold")

    def execute(
        self,
        mode: str,
        text: str | None = None,
        max_occurrences: int | str | None = None,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            body = text if isinstance(text, str) else ""
            occurrence_cap = (
                self._occurrence_cap(max_occurrences) if operation == "events" else None
            )
            if operation == "parse":
                return self._parse(body)
            if operation == "lint":
                return self._lint(body)
            if operation == "events":
                return self._events(body, occurrence_cap)
            return self._fold(body)
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error(mode, "operation_error", f"iCalendar analysis failed: {exc}")

    # ------------------------------------------------------------------
    # validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode}

    def _mode(self, mode: Any) -> str:
        if not isinstance(mode, str) or mode not in self._MODES:
            allowed = ", ".join(self._MODES)
            raise ValueError(f"mode must be one of: {allowed}")
        return mode

    def _occurrence_cap(self, max_occurrences: Any) -> int:
        if max_occurrences is None:
            return self.max_occurrences
        if isinstance(max_occurrences, bool) or not isinstance(max_occurrences, (int, str)):
            raise ValueError("max_occurrences must be an integer between 0 and 10")
        try:
            value = int(max_occurrences)
        except (TypeError, ValueError) as exc:
            raise ValueError("max_occurrences must be an integer between 0 and 10") from exc
        if not 0 <= value <= 10:
            raise ValueError("max_occurrences must be an integer between 0 and 10")
        return value

    def _validate_config(self) -> None:
        for name in (
            "max_text_chars", "max_logical_lines", "max_components",
            "max_findings", "max_events", "max_occurrences", "max_scan_periods",
            "max_fold_sites",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError(f"{name} must be a positive integer")

    def _prepare(self, text: str) -> dict[str, Any]:
        if not isinstance(text, str) or text == "":
            raise ValueError("text is required: the iCalendar content to analyze")
        if len(text) > self.max_text_chars:
            raise ValueError(f"text exceeds max_text_chars={self.max_text_chars} characters")
        endings = _detect_line_endings(text)
        unfolded = _unfold(text)
        logical = unfolded["logical"]
        if len(logical) > self.max_logical_lines:
            raise ValueError(
                f"text unfolds to {len(logical)} logical lines, over the "
                f"max_logical_lines={self.max_logical_lines} cap"
            )
        return {"endings": endings, "unfolded": unfolded, "logical": logical}

    def _assemble(
        self, prepared: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
        return _build_components(
            prepared["logical"], prepared["unfolded"]["anomalies"], self.max_components,
        )

    # ------------------------------------------------------------------
    # mode: parse
    # ------------------------------------------------------------------

    def _parse(self, text: str) -> dict[str, Any]:
        prepared = self._prepare(text)
        roots, findings, components_truncated = self._assemble(prepared)
        all_folds = prepared["unfolded"]["fold_sites"]
        component_counts: dict[str, int] = {}
        property_count = 0
        for node in _iter_components(roots):
            component_counts[node["type"]] = component_counts.get(node["type"], 0) + 1
            property_count += len(node["properties"])
        max_octets = max((_octets(entry["text"]) for entry in prepared["logical"]), default=0)
        return {
            "status": "ok",
            "mode": "parse",
            "line_endings": prepared["endings"],
            "unfold_log": {
                "total_folds": len(all_folds),
                "fold_sites": all_folds[: self.max_fold_sites],
                "fold_sites_truncated": len(all_folds) > self.max_fold_sites,
                "physical_lines": prepared["unfolded"]["physical_count"],
                "logical_lines": len(prepared["logical"]),
            },
            "components": [_slim_component(node) for node in roots],
            "calendar_props": _calendar_props(roots),
            "stats": {
                "components": component_counts,
                "properties": property_count,
                "max_logical_line_octets": max_octets,
                "components_truncated": components_truncated,
            },
            "structure_findings": [f for f in findings if f["severity"] == "error"],
            "notes": [
                "Unfolding per RFC 5545 3.1 removes CRLF plus one SPACE/HTAB.",
                "Bare LF/CR is accepted and reported in line_endings (RFC requires CRLF).",
                "property.line is the 1-based unfolded logical line number.",
            ],
        }

    # ------------------------------------------------------------------
    # mode: lint
    # ------------------------------------------------------------------

    def _lint(self, text: str) -> dict[str, Any]:
        prepared = self._prepare(text)
        roots, findings, _ = self._assemble(prepared)
        _walk_semantic_lint(roots, findings)
        _check_octet_limits(text, findings)
        endings = prepared["endings"]
        if endings["lone_lf"] or endings["lone_cr"]:
            if endings["mixed"]:
                findings.append({
                    "code": "mixed_line_endings", "severity": "warning", "line": 1,
                    "message": (
                        "Mixed CRLF and bare LF/CR line breaks; RFC 5545 3.1 "
                        "requires CRLF consistently."
                    ),
                })
            else:
                findings.append({
                    "code": "non_crlf_line_break", "severity": "info", "line": 1,
                    "detail": f"{endings['lone_lf']} bare LF, {endings['lone_cr']} bare CR",
                    "message": (
                        "RFC 5545 3.1 requires CRLF line breaks; bare LF is accepted "
                        "here with this information finding (pinned tolerance)."
                    ),
                })
        for finding in findings:
            finding.setdefault("line", 0)
        findings.sort(key=lambda f: (
            f.get("line", 0), f["code"], str(f.get("detail", "")), f["message"],
        ))
        total = len(findings)
        truncated = total > self.max_findings
        findings = findings[: self.max_findings]
        counts = {"error": 0, "warning": 0, "info": 0}
        for finding in findings:
            counts[finding["severity"]] += 1
        return {
            "status": "ok",
            "mode": "lint",
            "ok": counts["error"] == 0,
            "findings": findings,
            "summary": {
                "counts": counts, "total": total, "truncated": truncated,
                "codes": sorted({f["code"] for f in findings}),
            },
            "line_endings": endings,
            "notes": [
                "Octet limits are measured in UTF-8 bytes: multibyte characters count "
                "more than one octet per character (RFC 5545 3.1).",
                "A line starting with SPACE/HTAB is always a continuation per the "
                "RFC 5545 3.1 grammar; suspicious ones are flagged, never reinterpreted.",
                "line is the physical line for unfolding-stage codes (non_crlf_line_break, "
                "continuation_without_previous, suspicious_continuation, "
                "long_line_over_75_octets) and the logical line elsewhere.",
            ],
        }

    # ------------------------------------------------------------------
    # mode: events
    # ------------------------------------------------------------------

    def _events(self, text: str, occurrence_cap: int) -> dict[str, Any]:
        prepared = self._prepare(text)
        roots, _, components_truncated = self._assemble(prepared)
        events: list[dict[str, Any]] = []
        truncated = False
        for node in _iter_components(roots):
            if node["type"] != "VEVENT":
                continue
            if len(events) >= self.max_events:
                truncated = True
                break
            events.append(self._normalize_event(node, occurrence_cap))
        return {
            "status": "ok",
            "mode": "events",
            "events": events,
            "event_count": len(events),
            "truncated": truncated,
            "components_truncated": components_truncated,
            "notes": [
                "Deterministic: occurrences are generated forward from DTSTART, "
                "never from the wall clock; identical input yields identical output.",
                f"Built-in recurrence subset: {_BUILTIN_SUBSET}.",
                "python-dateutil expands the same subset (and more) when installed; "
                "the engine field always discloses which engine produced the occurrences.",
                "End resolution: DTEND, else DURATION, else next calendar date for "
                "DATE values and the same instant for DATE-TIME (RFC 5545 3.6.1).",
                "RDATE/EXDATE are parsed but not folded into the occurrence list.",
                "IANA zone math is out of scope: occurrences keep the DTSTART wall time.",
            ],
        }

    def _normalize_event(self, node: dict[str, Any], occurrence_cap: int) -> dict[str, Any]:
        props: dict[str, dict[str, Any]] = {}
        for prop in node["properties"]:
            props.setdefault(prop["name"], prop)
        summary_raw = props.get("SUMMARY")
        summary = _unescape_text(summary_raw["value"])[0] if summary_raw else ""
        location_raw = props.get("LOCATION")
        location = _unescape_text(location_raw["value"])[0] if location_raw else ""

        def value_of(name: str) -> dict[str, Any]:
            prop = props.get(name)
            if not prop:
                return {"iso": None, "form": None, "utc": False,
                        "tzid": None, "raw": None}
            tzid = prop["params"].get("TZID", [None])[0]
            as_datetime = _parse_ical_datetime(prop["value"])
            info = as_datetime if as_datetime.get("ok") else _parse_ical_date(prop["value"])
            if not info.get("ok"):
                return {"iso": None, "form": None, "utc": False, "tzid": tzid,
                        "raw": prop["value"], "invalid": info.get("error")}
            return {"iso": info["iso"], "form": info["form"],
                    "utc": bool(info.get("utc")), "tzid": tzid,
                    "raw": prop["value"]}

        start_info = value_of("DTSTART")
        end_info = value_of("DTEND")
        all_day = start_info["form"] == "DATE"
        end_iso = end_info["iso"]
        implied_by = None
        duration_raw = props.get("DURATION")
        duration_norm = None
        if duration_raw:
            parsed = _parse_duration(duration_raw["value"])
            if parsed.get("ok"):
                duration_norm = {
                    "raw": duration_raw["value"],
                    "total_seconds": parsed["total_seconds"],
                    "iso8601": parsed["iso8601"],
                }
        if end_iso is None and duration_norm is not None and start_info["iso"] is not None:
            parsed_duration = _parse_duration(duration_raw["value"])
            as_datetime = _parse_ical_datetime(props["DTSTART"]["value"])
            if as_datetime.get("ok"):
                end_iso = (as_datetime["datetime"] + parsed_duration["timedelta"]).isoformat()
            else:
                as_date = _parse_ical_date(props["DTSTART"]["value"])
                if as_date.get("ok"):
                    end_iso = (as_date["date"] + parsed_duration["timedelta"]).isoformat()
            implied_by = "DURATION"
        elif end_iso is None and start_info["iso"] is not None:
            implied_by = "next_calendar_date" if all_day else "same_instant"
            if all_day:
                as_date = _parse_ical_date(props["DTSTART"]["value"])
                end_iso = (as_date["date"] + timedelta(days=1)).isoformat() \
                    if as_date.get("ok") else start_info["iso"]
            else:
                end_iso = start_info["iso"]
        recurrence = None
        rrule_prop = props.get("RRULE")
        if rrule_prop:
            recurrence = self._normalize_recurrence(
                rrule_prop, props.get("DTSTART"), occurrence_cap,
            )
        alarms = sum(1 for c in node["components"] if c["type"] == "VALARM")
        unexpanded = [name for name in ("RDATE", "EXDATE") if name in props]
        return {
            "uid": props["UID"]["value"] if "UID" in props else None,
            "summary": summary or None,
            "location": location or None,
            "line": node["line"],
            "start": start_info,
            "end": {
                "iso": end_iso,
                "form": end_info["form"] or start_info["form"],
                "utc": end_info["utc"] if end_info["raw"] else start_info["utc"],
                "tzid": end_info["tzid"] if end_info["raw"] else start_info["tzid"],
                "raw": end_info["raw"],
                "implied_by": implied_by,
            },
            "all_day": all_day,
            "duration": duration_norm,
            "status": props["STATUS"]["value"] if "STATUS" in props else None,
            "transparency": props["TRANSP"]["value"] if "TRANSP" in props else None,
            "recurrence": recurrence,
            "alarms": alarms,
            "unexpanded": unexpanded,
        }

    def _normalize_recurrence(
        self,
        rrule_prop: dict[str, Any],
        dtstart_prop: dict[str, Any] | None,
        occurrence_cap: int,
    ) -> dict[str, Any]:
        parsed = _parse_rrule(rrule_prop["value"])
        normalized = parsed["normalized"]
        until_display = None
        if isinstance(normalized["UNTIL"], dict):
            until_display = {
                key: value for key, value in normalized["UNTIL"].items()
                if key not in ("date", "datetime")
            }
        unsupported: list[str] = []
        occurrences: list[str] = []
        engine: str | None = None
        notes: list[str] = []
        dtstart: date | datetime | None = None
        if dtstart_prop is None:
            unsupported.append("no DTSTART to expand from")
        else:
            as_datetime = _parse_ical_datetime(dtstart_prop["value"])
            as_date = _parse_ical_date(dtstart_prop["value"])
            dtstart = as_datetime["datetime"] if as_datetime.get("ok") else (
                as_date["date"] if as_date.get("ok") else None
            )
            if dtstart is None:
                unsupported.append("DTSTART is not a valid DATE or DATE-TIME")
        if dtstart is not None:
            builtin = _builtin_occurrences(normalized, dtstart, occurrence_cap,
                                           self.max_scan_periods)
            unsupported = builtin["unsupported"]
            occurrences_raw = None
            if unsupported:
                dateutil_result = _dateutil_occurrences(normalized, dtstart, occurrence_cap)
                if dateutil_result is not None:
                    engine = "dateutil"
                    unsupported = []
                    occurrences_raw = dateutil_result["occurrences"]
                    notes.append(
                        "outside the built-in subset; expanded by python-dateutil"
                    )
            else:
                dateutil_result = _dateutil_occurrences(normalized, dtstart, occurrence_cap)
                if dateutil_result is not None:
                    engine = "dateutil"
                    occurrences_raw = dateutil_result["occurrences"]
                else:
                    engine = "builtin"
                    occurrences_raw = builtin["occurrences"]
                if builtin.get("hit_scan_cap"):
                    notes.append(
                        f"occurrence scan stopped at max_scan_periods={self.max_scan_periods}"
                    )
            occurrences = [value.isoformat() for value in occurrences_raw or []]
        return {
            "rrule": rrule_prop["value"],
            "normalized": {
                "FREQ": normalized["FREQ"],
                "INTERVAL": normalized["INTERVAL"],
                "COUNT": normalized["COUNT"],
                "UNTIL": until_display,
                "BYDAY": normalized["BYDAY"],
                "BYMONTHDAY": normalized["BYMONTHDAY"],
                "WKST": normalized["WKST"],
                "other_parts": parsed["extras"],
            },
            "engine": engine,
            "supported": not unsupported,
            "unsupported_parts": unsupported,
            "next_occurrences": occurrences,
            "occurrence_count_returned": len(occurrences),
            "supported_subset": _BUILTIN_SUBSET,
            "notes": notes,
        }

    # ------------------------------------------------------------------
    # mode: fold
    # ------------------------------------------------------------------

    def _fold(self, text: str) -> dict[str, Any]:
        if not isinstance(text, str) or text == "":
            raise ValueError("text is required: the unfolded iCalendar content to fold")
        if len(text) > self.max_text_chars:
            raise ValueError(f"text exceeds max_text_chars={self.max_text_chars} characters")
        logical_before = [entry["text"] for entry in _unfold(text)["logical"]]
        folded = _fold_text(text)
        round_trip = [entry["text"] for entry in _unfold(folded)["logical"]]
        physical = [piece for piece in folded.split("\r\n") if piece != ""]
        max_octets = max((_octets(piece) for piece in physical), default=0)
        fold_count = sum(1 for piece in physical if piece[:1] in (" ", "\t"))
        return {
            "status": "ok",
            "mode": "fold",
            "folded_text": folded,
            "physical_lines": len(physical),
            "fold_sites": fold_count,
            "max_physical_line_octets": max_octets,
            "limit_octets": 75,
            "round_trip_ok": round_trip == logical_before,
            "notes": [
                "Folding per RFC 5545 3.1: CRLF + single SPACE, at most 75 octets per "
                "physical line (74 content octets per continuation plus the SPACE).",
                "Folds happen at character boundaries only: no UTF-8 sequence is split.",
                "Output always uses CRLF and ends with CRLF; round_trip_ok compares "
                "logical lines, not raw bytes.",
            ],
        }
