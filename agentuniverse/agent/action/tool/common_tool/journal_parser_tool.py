#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: journal_parser_tool.py

"""Dated journal / worklog / meeting-notes parser built purely on the stdlib.

Addresses an *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency structural parser
for date-headed entries — the format diaries, worklogs and meeting
notes use. It complements in-text date extraction: instead of finding
dates mentioned anywhere inside prose, it recognises lines that START
an entry (the date is the heading) and splits the text into the
structured records that journal-style agents need.

An entry delimiter is a line that begins — after at most three
leading spaces/tabs and an optional Markdown heading of one to six
``#`` marks followed by whitespace — with one of:

* an ISO date — ``2026-10-19`` (strict zero-padded ``YYYY-MM-DD``);
* a slash date, year first — ``2026/10/19`` (month and day may be
  one or two digits);
* a US slash date, month first — ``10/19/2026`` (four-digit year);
* a CJK date — ``2026年10月19日``;
* an English weekday name — ``Monday`` ... ``Sunday``
  (case-insensitive, full names only).

The date token must be followed by the end of the line, whitespace or
punctuation (anything but an ASCII letter or digit), so prose such as
``2026-10-19abc`` is not mistaken for a heading. Anything after the
token on the delimiter line is captured as the entry ``title`` with
leading separator punctuation (``: - – — = , ; |`` and spaces)
trimmed. Entry content is every line up to (not including) the next
delimiter; the delimiter line itself is the first line of the entry
``text``, so ``preamble`` plus all entry texts reconstruct the input
exactly.

Weekday headings carry no year, so their dates are inferred
(documented heuristic):

* by default a weekday entry attaches to the Monday-based week of
  the most recent explicit-date entry — ``Tuesday`` following
  ``2026-10-19`` (a Monday) resolves to ``2026-10-20``. The resolved
  date may lie before its anchor (``Monday`` after an explicit
  ``2026-10-21`` resolves to ``2026-10-19``), which surfaces as a
  negative ``next_date_gap_days`` and is flagged by ``summary``; and
* when the injectable ``reference_year`` option is set and no
  explicit date has been seen yet, weekday entries resolve forward
  from January 1 of that year — the first ``Monday`` of 2026 is
  ``2026-01-05`` (January 1 is a Thursday) and each resolved date
  advances the anchor, so a later ``Monday`` resolves to
  ``2026-01-12``.

Lines that merely LOOK like delimiters are tolerated as plain
content and reported, never fatal: ``2026-13-01`` / ``2026-02-30`` /
``13/45/2026`` / ``2026年13月1日`` (regex-shaped but not a real
calendar date — reason ``invalid_date``), date skeletons glued to
letters or digits such as ``2026-10-19abc`` (no clean token boundary
— reason ``ambiguous_boundary``), and weekday headings that cannot
be resolved because no explicit date precedes them and no
``reference_year`` was given (reason ``unresolvable_weekday``).
Tolerated lines stay in the preamble / entry body where they were
found and are listed under ``ignored_delimiters``.

Three modes are supported. ``parse`` returns every entry as
``{index, line_start, line_end, date, raw_date, inferred, title,
lines, text, next_date_gap_days}`` plus the preamble and the
tolerated lines. ``summary`` returns the entry count, date range,
mean/max gap in days, per-entry line counts and the out-of-order
entries (negative gap). ``filter`` returns the entries whose date
falls within an inclusive ``start_date`` / ``end_date`` range and/or
whose text contains ``substring`` (``case_sensitive`` option; both
criteria AND together when both are given).

Input validation is strict and happens before any parsing: a wrong
``mode``, a non-string / empty / oversized ``text``, a malformed
``reference_year``, a filter with no criteria, unparseable or
inverted range bounds, an empty or non-string ``substring``, or a
non-boolean ``case_sensitive`` raise a ``ValueError``, mirroring the
other common tools. Everything the tool returns is deterministic.
"""

import datetime as datetime_module
import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Up to three leading spaces/tabs, then an optional Markdown heading
# ("#", "##", ... "# ######") that must be followed by whitespace.
_HEADING_PREFIX = r"[ \t]{0,3}(?:#{1,6}[ \t]+)?"
# A date token must not run into an ASCII letter or digit.
_TOKEN_BOUNDARY = r"(?![0-9A-Za-z])"
# Punctuation trimmed off the start of an entry title.
_TITLE_SEPARATORS = " \t:-–—=,;|*"
# Strict ISO calendar date, used for the filter range bounds.
_STRICT_ISO = re.compile(r"\A[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")


def _strict(skeleton: str, flags: int = 0) -> "re.Pattern[str]":
    """Compile a strict delimiter pattern (prefix + skeleton + boundary)."""
    return re.compile(_HEADING_PREFIX + skeleton + _TOKEN_BOUNDARY, flags)


def _loose(skeleton: str, flags: int = 0) -> "re.Pattern[str]":
    """Compile a look-alike pattern (no trailing token boundary)."""
    return re.compile(_HEADING_PREFIX + skeleton, flags)


class JournalParserTool(Tool):
    """Dated journal / log entry parser built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input
            length; longer inputs are rejected before any parsing.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "journal_parser_tool"
    description: str = (
        "Journal parser tool — pure Python stdlib, no network required. "
        "Splits dated journal/log/diary/meeting-notes text into structured "
        "entries at date-headed lines (ISO 2026-10-19, slash 2026/10/19, "
        "US 10/19/2026, CJK 2026年10月19日, weekday names, or Markdown "
        "'## 2026-10-19' headings): mode='parse' returns entries with "
        "parsed ISO date, raw date as written, title, line counts, text "
        "and next-entry gap days plus the preamble and tolerated "
        "look-alike lines; mode='summary' returns entry count, date "
        "range, mean/max gap days, per-entry line counts and out-of-order "
        "entries flagged; mode='filter' returns entries matching an "
        "inclusive start_date/end_date range and/or a substring "
        "(optional case_sensitive). Weekday headings resolve against the "
        "week of the most recent explicit-date entry, or forward from "
        "January 1 of an injectable reference_year."
    )

    MODES: ClassVar[tuple] = ("parse", "summary", "filter")
    # Python's date.weekday(): Monday == 0.
    WEEKDAYS: ClassVar[Dict[str, int]] = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    max_text_chars: int = 100_000

    _STRICT: ClassVar[Tuple[Tuple[str, "re.Pattern[str]"], ...]] = (
        (
            "iso",
            _strict(r"(?P<raw>(?P<y>[0-9]{4})-(?P<m>[0-9]{2})-(?P<d>[0-9]{2}))"),
        ),
        (
            "ymd_slash",
            _strict(r"(?P<raw>(?P<y>[0-9]{4})/(?P<m>[0-9]{1,2})/(?P<d>[0-9]{1,2}))"),
        ),
        (
            "mdy_slash",
            _strict(r"(?P<raw>(?P<m>[0-9]{1,2})/(?P<d>[0-9]{1,2})/(?P<y>[0-9]{4}))"),
        ),
        (
            "cjk",
            _strict(r"(?P<raw>(?P<y>[0-9]{4})年(?P<m>[0-9]{1,2})月(?P<d>[0-9]{1,2})日)"),
        ),
        (
            "weekday",
            _strict(
                r"(?P<raw>Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)",
                re.IGNORECASE,
            ),
        ),
    )
    # Look-alike detectors: same skeletons without the clean token
    # boundary (the CJK one also tolerates a missing trailing 日).
    _LOOSE: ClassVar[Tuple["re.Pattern[str]", ...]] = (
        _loose(r"[0-9]{4}-[0-9]{2}-[0-9]{2}"),
        _loose(r"[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}"),
        _loose(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}"),
        _loose(r"[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}(?:日)?"),
        _loose(
            r"Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday",
            re.IGNORECASE,
        ),
    )

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        reference_year: Any = None,
        start_date: Any = None,
        end_date: Any = None,
        substring: Any = None,
        case_sensitive: Any = None,
    ) -> Dict[str, Any]:
        """Parse, summarize or filter dated journal entries.

        Args:
            mode (str): One of ``parse`` / ``summary`` / ``filter``.
            text (str): The journal text. Required for every mode; a
                non-empty string of at most 100,000 characters.
            reference_year (int | str): Optional anchor year for
                weekday headings that appear before any explicit-date
                entry: they resolve forward from January 1 of that
                year, each resolved date advancing the anchor. Once an
                explicit date has been seen, weekday headings attach
                to that entry's Monday-based week regardless.
            start_date (str): Filter mode only — inclusive lower ISO
                ``YYYY-MM-DD`` bound on entry dates.
            end_date (str): Filter mode only — inclusive upper ISO
                ``YYYY-MM-DD`` bound on entry dates.
            substring (str): Filter mode only — substring that must
                appear in the entry text. Combined with the date
                range using AND when both are given.
            case_sensitive (bool): Filter mode only — whether the
                substring match is case sensitive; defaults to
                ``False``.

        Returns:
            Dict[str, Any]: The mode result (always including
            ``mode`` and ``entry_count``). ``parse`` adds
            ``entries`` / ``preamble`` / ``ignored_delimiters``;
            ``summary`` adds date range, gap statistics,
            ``per_entry_lines`` and out-of-order flags; ``filter``
            adds ``match_count`` / ``criteria`` / ``entries``.

        Raises:
            ValueError: If any parameter is malformed (before any
                parsing happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        clean_year = self._validate_reference_year(reference_year)
        parsed = self._parse_entries(clean_text, clean_year)

        if mode == "parse":
            return {
                "mode": "parse",
                "entry_count": len(parsed["entries"]),
                "total_lines": parsed["total_lines"],
                "preamble": parsed["preamble"],
                "preamble_lines": parsed["preamble_lines"],
                "entries": parsed["entries"],
                "ignored_delimiters": parsed["ignored"],
            }
        if mode == "summary":
            return self._summary(parsed)
        return self._filter(
            parsed, start_date, end_date, substring, case_sensitive
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any parsing)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"journal_parser_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text.strip():
            cls._invalid("text must be a non-empty string (got only whitespace)")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_reference_year(cls, reference_year: Any) -> Optional[int]:
        """Validate the optional weekday-anchor ``reference_year``."""
        if reference_year is None:
            return None
        if isinstance(reference_year, bool) or isinstance(
            reference_year, float
        ):
            cls._invalid(
                "reference_year must be an integer year or None "
                f"(got {reference_year!r})"
            )
        if isinstance(reference_year, str):
            if not reference_year.isdigit():
                cls._invalid(
                    "reference_year must be an integer year or None "
                    f"(got {reference_year!r})"
                )
            reference_year = int(reference_year)
        if not isinstance(reference_year, int):
            cls._invalid(
                "reference_year must be an integer year or None "
                f"(got {reference_year!r})"
            )
        if not 1 <= reference_year <= 9999:
            cls._invalid(
                "reference_year must be a calendar year between 1 and 9999 "
                f"(got {reference_year!r})"
            )
        return reference_year

    @classmethod
    def _validate_bound(cls, label: str, value: Any) -> Optional[Any]:
        """Validate one inclusive ISO date bound for filter mode."""
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{label} must be an ISO 'YYYY-MM-DD' date (got {value!r})")
        if not _STRICT_ISO.match(value):
            cls._invalid(f"{label} must be an ISO 'YYYY-MM-DD' date (got {value!r})")
        try:
            return datetime_module.date(
                int(value[0:4]), int(value[5:7]), int(value[8:10])
            )
        except ValueError:
            cls._invalid(f"{label} is not a real calendar date (got {value!r})")

    # ------------------------------------------------------------------ #
    # Delimiter recognition
    # ------------------------------------------------------------------ #

    @classmethod
    def _title_after(cls, line: str, position: int) -> str:
        """Extract the entry title from the rest of a delimiter line."""
        return line[position:].lstrip(_TITLE_SEPARATORS).rstrip()

    def _match_delimiter(
        self, line: str
    ) -> Tuple[str, Optional[str], Optional[Any], str]:
        """Classify one line against the delimiter patterns.

        Returns a ``(kind, raw_date, date, title)`` tuple:

        * ``("explicit", raw, date, title)`` — a real dated heading;
        * ``("weekday", raw, None, title)`` — a weekday heading whose
          date still has to be resolved against an anchor;
        * ``("invalid_date" | "ambiguous_boundary", None, None, "")``
          — the line merely looks like a delimiter and is tolerated
          as content;
        * ``(None, None, None, "")`` — plain content.
        """
        for kind, pattern in self._STRICT:
            match = pattern.match(line)
            if match is None:
                continue
            raw = match.group("raw")
            if kind == "weekday":
                return ("weekday", raw, None, self._title_after(line, match.end()))
            try:
                parsed_date = datetime_module.date(
                    int(match.group("y")),
                    int(match.group("m")),
                    int(match.group("d")),
                )
            except ValueError:
                return ("invalid_date", raw, None, "")
            return ("explicit", raw, parsed_date, self._title_after(line, match.end()))
        for pattern in self._LOOSE:
            if pattern.match(line) is not None:
                return ("ambiguous_boundary", None, None, "")
        return (None, None, None, "")

    # ------------------------------------------------------------------ #
    # Core parsing
    # ------------------------------------------------------------------ #

    def _parse_entries(
        self, text: str, reference_year: Optional[int]
    ) -> Dict[str, Any]:
        """Split the text into preamble, entries and tolerated lines."""
        lines = text.splitlines()
        records: List[Dict[str, Any]] = []
        preamble: List[str] = []
        ignored: List[Dict[str, Any]] = []
        current_body: Optional[List[str]] = None
        anchor_explicit: Optional[Any] = None
        anchor_reference: Optional[Any] = None

        for line_number, line in enumerate(lines, 1):
            kind, raw, parsed_date, title = self._match_delimiter(line)

            if kind == "explicit":
                anchor_explicit = parsed_date
                current_body = [line]
                records.append(
                    {
                        "date": parsed_date,
                        "line_start": line_number,
                        "raw_date": raw,
                        "inferred": False,
                        "title": title,
                        "body": current_body,
                    }
                )
                continue

            if kind == "weekday":
                weekday = self.WEEKDAYS[raw.lower()]
                if anchor_explicit is not None:
                    # Default heuristic: attach to the Monday-based week
                    # of the most recent explicit-date entry.
                    week_start = anchor_explicit - datetime_module.timedelta(
                        days=anchor_explicit.weekday()
                    )
                    resolved = week_start + datetime_module.timedelta(
                        days=weekday
                    )
                elif reference_year is not None:
                    # Reference-year heuristic: resolve forward from
                    # January 1 (or the last resolved weekday), so a
                    # weekday-only journal still moves ahead in time.
                    base = anchor_reference or datetime_module.date(
                        reference_year, 1, 1
                    )
                    resolved = base + datetime_module.timedelta(
                        days=(weekday - base.weekday()) % 7
                    )
                    anchor_reference = resolved
                else:
                    ignored.append(
                        {
                            "line_number": line_number,
                            "raw": line,
                            "reason": "unresolvable_weekday",
                        }
                    )
                    if current_body is None:
                        preamble.append(line)
                    else:
                        current_body.append(line)
                    continue
                current_body = [line]
                records.append(
                    {
                        "date": resolved,
                        "line_start": line_number,
                        "raw_date": raw,
                        "inferred": True,
                        "title": title,
                        "body": current_body,
                    }
                )
                continue

            if kind == "invalid_date":
                ignored.append(
                    {
                        "line_number": line_number,
                        "raw": line,
                        "reason": "invalid_date",
                    }
                )
            elif kind == "ambiguous_boundary":
                ignored.append(
                    {
                        "line_number": line_number,
                        "raw": line,
                        "reason": "ambiguous_boundary",
                    }
                )

            if current_body is None:
                preamble.append(line)
            else:
                current_body.append(line)

        entries: List[Dict[str, Any]] = []
        for position, record in enumerate(records):
            body = record["body"]
            entry = {
                "index": position + 1,
                "line_start": record["line_start"],
                "line_end": record["line_start"] + len(body) - 1,
                "date": record["date"].isoformat(),
                "raw_date": record["raw_date"],
                "inferred": record["inferred"],
                "title": record["title"],
                "lines": len(body),
                "text": "\n".join(body),
                "next_date_gap_days": None,
            }
            if position + 1 < len(records):
                entry["next_date_gap_days"] = (
                    records[position + 1]["date"] - record["date"]
                ).days
            entries.append(entry)

        return {
            "entries": entries,
            "dates": [record["date"] for record in records],
            "total_lines": len(lines),
            "preamble": "\n".join(preamble),
            "preamble_lines": len(preamble),
            "ignored": ignored,
        }

    # ------------------------------------------------------------------ #
    # summary mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _summary(parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Build the summary statistics over the parsed entries."""
        entries = parsed["entries"]
        dates = parsed["dates"]
        gaps = [
            (dates[position + 1] - dates[position]).days
            for position in range(len(dates) - 1)
        ]
        date_min = min(dates).isoformat() if dates else None
        date_max = max(dates).isoformat() if dates else None
        out_of_order = [
            {
                "index": position + 1,
                "date": entries[position]["date"],
                "previous_date": entries[position - 1]["date"],
                "gap_days": gaps[position - 1],
            }
            for position in range(1, len(entries))
            if gaps[position - 1] < 0
        ]
        return {
            "mode": "summary",
            "entry_count": len(entries),
            "total_lines": parsed["total_lines"],
            "preamble_lines": parsed["preamble_lines"],
            "date_min": date_min,
            "date_max": date_max,
            "date_range_days": (
                (max(dates) - min(dates)).days if dates else None
            ),
            "mean_gap_days": (
                round(sum(gaps) / len(gaps), 2) if gaps else None
            ),
            "max_gap_days": max(gaps) if gaps else None,
            "out_of_order_count": len(out_of_order),
            "out_of_order_entries": out_of_order,
            "per_entry_lines": [
                {
                    "index": entry["index"],
                    "date": entry["date"],
                    "raw_date": entry["raw_date"],
                    "lines": entry["lines"],
                }
                for entry in entries
            ],
            "ignored_delimiter_count": len(parsed["ignored"]),
        }

    # ------------------------------------------------------------------ #
    # filter mode
    # ------------------------------------------------------------------ #

    def _filter(
        self,
        parsed: Dict[str, Any],
        start_date: Any,
        end_date: Any,
        substring: Any,
        case_sensitive: Any,
    ) -> Dict[str, Any]:
        """Return the entries matching the date range and/or substring."""
        if start_date is None and end_date is None and substring is None:
            self._invalid(
                "filter mode requires at least one of: start_date, "
                "end_date, substring (got none)"
            )
        start = self._validate_bound("start_date", start_date)
        end = self._validate_bound("end_date", end_date)
        if start is not None and end is not None and start > end:
            self._invalid(
                f"start_date must not be after end_date "
                f"(got {start_date!r} > {end_date!r})"
            )
        if substring is not None and (
            isinstance(substring, bool) or not isinstance(substring, str)
        ):
            self._invalid(f"substring must be a non-empty string (got {substring!r})")
        if substring == "":
            self._invalid("substring must be a non-empty string (got '')")
        if case_sensitive is None:
            case_sensitive = False
        if isinstance(case_sensitive, bool) is False:
            self._invalid(
                f"case_sensitive must be a boolean (got {case_sensitive!r})"
            )

        needle = substring
        if substring is not None and not case_sensitive:
            needle = substring.lower()

        matching = []
        for entry, entry_date in zip(parsed["entries"], parsed["dates"]):
            if start is not None and entry_date < start:
                continue
            if end is not None and entry_date > end:
                continue
            if needle is not None:
                haystack = (
                    entry["text"] if case_sensitive else entry["text"].lower()
                )
                if needle not in haystack:
                    continue
            matching.append(entry)

        return {
            "mode": "filter",
            "entry_count": len(parsed["entries"]),
            "match_count": len(matching),
            "criteria": {
                "start_date": start.isoformat() if start else None,
                "end_date": end.isoformat() if end else None,
                "substring": substring,
                "case_sensitive": case_sensitive,
            },
            "entries": matching,
        }
