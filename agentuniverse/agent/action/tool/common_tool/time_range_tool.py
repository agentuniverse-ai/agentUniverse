#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: time_range_tool.py

"""Time-of-DAY range arithmetic tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency clock-time helper:
agents that reason about **times of day** — opening hours
(``"09:00"``-``"12:00"``), overnight shifts that cross midnight
(``"22:00"``-``"06:00"``), meeting windows, on-call rotations —
rather than calendar dates, workdays or duration lengths.

A *range* is a pair of strict 24-hour ``HH:MM`` clock times, a
half-open interval ``[start, end)`` — the **end is exclusive** — of
minutes since midnight. ``start == end`` is rejected: a degenerate
pair denotes an empty range (and a full 24h day is deliberately not
expressible by a single pair, since ``"09:00"``-``"09:00"`` would be
ambiguous between "nothing" and "everything"). When ``start > end``
the range **crosses midnight** (``22:00``-``06:00`` = 480 minutes
running 22:00 -> 24:00 -> 06:00); wraparound is handled natively by
every mode. Internally each range is a circular arc — an anchor
minute plus a length of 1..1439 minutes — and every operation is
done with interval arithmetic on a normalized day-local
``[0, 1440)`` timeline, so results are exact and deterministic.

Six modes:

* ``overlap`` — two ranges to the minutes they share (``0`` when
  disjoint or merely touching, since ends are exclusive) plus the
  overlapping sub-ranges; ``22:00``-``06:00`` vs ``05:00``-``07:00``
  share exactly 60 minutes (``05:00``-``06:00``).
* ``contains`` — a range plus a single ``HH:MM`` time to a boolean;
  boundary semantics follow the half-open interval (``09:00`` is
  inside ``09:00``-``12:00``, ``12:00`` is not).
* ``subtract`` — range A minus range B to the remaining sub-ranges
  (0, 1 or 2 of them) with wraparound support
  (``22:00``-``06:00`` minus ``05:00``-``07:00`` = ``22:00``-``05:00``).
* ``merge`` — a list of ranges (each ``["HH:MM", "HH:MM"]`` or a
  ``"HH:MM-HH:MM"`` string) to the coalesced, sorted, non-overlapping
  cover: overlapping *and merely touching* ranges join
  (``09:00``-``12:00`` + ``12:00``-``15:00`` = one 360-minute range).
  Wraparound inputs are normalized to possibly-two day-local segments
  (``22:00``-``06:00`` -> ``[22:00, 24:00)`` + ``[00:00, 06:00)``)
  and segments that meet across the midnight boundary are re-joined
  into a single wraparound output range — that day-local
  normalization is the documented, deterministic answer to the
  "merge across midnight is ambiguous" trap, and the result carries
  a note whenever it applies. A merged cover of the full 24h day is
  reported as ``full_day: true`` with an empty ``ranges`` list,
  because no single start/end pair could encode it.
* ``gap`` — two ranges to the idle minutes between them: ``0`` when
  the ranges overlap or touch, otherwise the smaller of the two
  circular gaps (``09:00``-``12:00`` / ``13:00``-``17:00`` -> 60),
  with the full complement of the union listed as gap ranges.
* ``info`` — one range to its duration in minutes, its
  ``crosses_midnight`` flag and its canonical day-local segments.

Input validation is strict and happens before any computation:
malformed parameters — unknown mode, times outside the strict
zero-padded 24-hour ``HH:MM`` form (``"9:00"``, ``"09:0"``,
``"24:00"``, ``"12:60"``, padded whitespace, non-strings, booleans),
``start`` equal to ``end``, a missing required parameter, a
``ranges`` list that is not a list, over the 100-entry cap, or whose
items are neither 2-element lists/tuples of strict times nor
``"HH:MM-HH:MM"`` strings — raise a ``ValueError``. No wall clock is
read anywhere: the tool is fully deterministic and offline.
"""

import re
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Strict 24-hour clock time: exactly HH:MM, zero-padded, 00..23 / 00..59.
# Minutes of 60+ and the hour 24 are structurally rejected here.
_TIME_RE = re.compile(r"\A([01]\d|2[0-3]):([0-5]\d)\Z")
# Range given as a single "HH:MM-HH:MM" string (merge mode items).
_RANGE_STR_RE = re.compile(r"\A([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)\Z")

MINUTES_PER_DAY = 1440

# A parsed range: (start minute 0..1439, length 1..1439). The length is
# the forward distance (end - start) % 1440, so a wraparound range is a
# single circular arc like any other.
Range = Tuple[int, int]
# A day-local half-open segment [x, y) on the linear 0..1440 timeline.
Segment = Tuple[int, int]


class TimeRangeTool(Tool):
    """Time-of-DAY range arithmetic tool built purely on the stdlib.

    Attributes:
        max_merge_ranges (int): Upper bound on the number of input
            ranges accepted by the ``merge`` mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "time_range_tool"
    description: str = (
        "Clock-time range arithmetic tool — pure Python stdlib, no "
        "network required, times are strict 24h HH:MM and range ends "
        "are exclusive. Measure shared minutes of two ranges with "
        "midnight-crossing support (mode='overlap': 22:00-06:00 vs "
        "05:00-07:00 -> 60), test membership of a single time "
        "(mode='contains'), subtract one range from another into "
        "remaining sub-ranges (mode='subtract'), coalesce a list of "
        "overlapping or touching ranges into a sorted cover "
        "(mode='merge', day-local normalization for wraparound "
        "inputs, full-day flag), get the idle minutes between two "
        "ranges (mode='gap') or a range's duration and "
        "crosses_midnight flag with its day-local segments "
        "(mode='info')."
    )

    MODES: ClassVar[tuple] = (
        "overlap",
        "contains",
        "subtract",
        "merge",
        "gap",
        "info",
    )

    max_merge_ranges: int = 100

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        start: Any = None,
        end: Any = None,
        start2: Any = None,
        end2: Any = None,
        time: Any = None,
        ranges: Any = None,
    ) -> Dict[str, Any]:
        """Run one clock-time range operation.

        Args:
            mode (str): One of ``overlap`` / ``contains`` /
                ``subtract`` / ``merge`` / ``gap`` / ``info``.
            start (str): First range start ``HH:MM`` (inclusive).
            end (str): First range end ``HH:MM`` (**exclusive**); a
                start later than the end denotes a range crossing
                midnight. Required by every mode except ``merge``.
            start2 (str): Second range start; required by
                ``overlap``, ``subtract`` (as the removed range) and
                ``gap``.
            end2 (str): Second range end (exclusive); required
                together with ``start2``.
            time (str): A single ``HH:MM`` clock time; required by
                ``contains``.
            ranges (list): Input ranges for ``merge`` — up to 100
                items, each a 2-element list/tuple of ``HH:MM``
                strings or a ``"HH:MM-HH:MM"`` string.

        Returns:
            Dict[str, Any]: The operation result — minutes, boolean
                verdicts and ``HH:MM`` sub-ranges — plus the call
                context. Every output range is a
                ``{"start", "end", "minutes", "crosses_midnight"}``
                payload with half-open semantics.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens): unknown mode, non-canonical
                times, ``start`` equal to ``end``, missing required
                parameters, or a ``ranges`` list of bad shape or
                over the cap.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "overlap":
            first = self._parse_range(start, end, "start", "end")
            second = self._parse_range(start2, end2, "start2", "end2")
            return self._run_overlap(first, second, start, end, start2, end2)
        if mode == "contains":
            clock_range = self._parse_range(start, end, "start", "end")
            minute = self._parse_time(time, "time")
            return self._run_contains(clock_range, minute, time)
        if mode == "subtract":
            clock_range = self._parse_range(start, end, "start", "end")
            removed = self._parse_range(start2, end2, "start2", "end2")
            return self._run_subtract(clock_range, removed)
        if mode == "merge":
            parsed = self._parse_ranges(ranges)
            return self._run_merge(parsed)
        if mode == "gap":
            first = self._parse_range(start, end, "start", "end")
            second = self._parse_range(start2, end2, "start2", "end2")
            return self._run_gap(first, second)
        # info
        clock_range = self._parse_range(start, end, "start", "end")
        return self._run_info(clock_range, start, end)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"time_range_tool: {message}")

    @classmethod
    def _parse_time(cls, value: Any, label: str) -> int:
        """Parse a strict zero-padded 24-hour ``HH:MM`` clock time.

        Only the exact form passes: one or two digit hours must be
        zero-padded, the hour 24 and minutes of 60+ are rejected, and
        so are surrounding whitespace, non-strings and booleans.
        Returns minutes since midnight (0..1439).
        """
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
            or not _TIME_RE.match(value)
        ):
            cls._invalid(
                f"{label} must be a 24-hour clock time in strict "
                f"zero-padded HH:MM form (got {value!r})"
            )
        hours, minutes = int(value[:2]), int(value[3:])
        return hours * 60 + minutes

    @classmethod
    def _parse_range(
        cls, start: Any, end: Any, start_label: str, end_label: str
    ) -> Range:
        """Parse a ``start``/``end`` pair into a circular arc.

        The pair must be two strict ``HH:MM`` times with
        ``start != end``: equality would denote an empty range, and
        the full 24h day is deliberately not encodable by one pair
        (use ``merge`` with two complementary ranges and read its
        ``full_day`` flag instead).
        """
        start_minute = cls._parse_time(start, start_label)
        end_minute = cls._parse_time(end, end_label)
        if start_minute == end_minute:
            cls._invalid(
                f"{start_label} and {end_label} must differ: equal "
                "times denote an empty range (a full 24h day is not "
                "representable by a single HH:MM pair — merge two "
                f"complementary ranges instead) (got {start!r})"
            )
        return start_minute, (end_minute - start_minute) % MINUTES_PER_DAY

    def _parse_ranges(self, ranges: Any) -> List[Range]:
        """Parse the ``ranges`` list of the ``merge`` mode.

        Accepts up to ``max_merge_ranges`` items, each either a
        2-element list/tuple of strict ``HH:MM`` strings or a single
        ``"HH:MM-HH:MM"`` string. Every item must again have
        differing start and end.
        """
        if not isinstance(ranges, list):
            self._invalid(
                f"ranges must be a list of HH:MM pairs or "
                f"HH:MM-HH:MM strings (got {type(ranges).__name__})"
            )
        if not 1 <= len(ranges) <= self.max_merge_ranges:
            self._invalid(
                f"ranges must contain between 1 and "
                f"{self.max_merge_ranges} items (got {len(ranges)})"
            )
        parsed: List[Range] = []
        for index, item in enumerate(ranges):
            label = f"ranges[{index}]"
            if isinstance(item, str):
                match = _RANGE_STR_RE.match(item)
                if not match:
                    self._invalid(
                        f"{label} must be an 'HH:MM-HH:MM' string "
                        f"(got {item!r})"
                    )
                start_value, end_value = item[:5], item[6:]
            elif isinstance(item, (list, tuple)):
                if len(item) != 2:
                    self._invalid(
                        f"{label} must have exactly a start and an "
                        f"end (got {len(item)} elements)"
                    )
                start_value, end_value = item[0], item[1]
            else:
                self._invalid(
                    f"{label} must be an 'HH:MM-HH:MM' string or a "
                    f"2-element list/tuple of HH:MM strings "
                    f"(got {item!r})"
                )
            parsed.append(
                self._parse_range(start_value, end_value,
                                  label + " start", label + " end")
            )
        return parsed

    # ------------------------------------------------------------------ #
    # Circular-arc helpers (day-local [0, 1440) interval algebra)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _format_time(minute: int) -> str:
        """Format minutes since midnight as zero-padded ``HH:MM``."""
        return f"{minute // 60:02d}:{minute % 60:02d}"

    @classmethod
    def _placed_segments(cls, anchor: int, length: int) -> List[Segment]:
        """Place an arc on the linear day-local ``[0, 1440)`` timeline.

        ``anchor`` is the arc's start minute on that timeline and
        ``length`` its forward length; an arc running past 1440 wraps
        and therefore contributes two segments.
        """
        if anchor + length <= MINUTES_PER_DAY:
            return [(anchor, anchor + length)]
        return [
            (anchor, MINUTES_PER_DAY),
            (0, anchor + length - MINUTES_PER_DAY),
        ]

    @staticmethod
    def _coalesce_segments(segments: List[Segment]) -> List[Segment]:
        """Sort and coalesce segments on the linear timeline.

        Overlapping and merely *touching* segments ([a, b) followed
        by [b, c)) merge into one — between touching segments no idle
        minute exists.
        """
        merged: List[Segment] = []
        for start, end in sorted(segments):
            if merged and start <= merged[-1][1]:
                if end > merged[-1][1]:
                    merged[-1] = (merged[-1][0], end)
            else:
                merged.append((start, end))
        return merged

    @staticmethod
    def _subtract_segments(
        base: List[Segment], holes: List[Segment]
    ) -> List[Segment]:
        """Subtract half-open hole segments from half-open base ones."""
        result = list(base)
        for hole_start, hole_end in holes:
            nxt: List[Segment] = []
            for seg_start, seg_end in result:
                if hole_end <= seg_start or hole_start >= seg_end:
                    nxt.append((seg_start, seg_end))
                    continue
                if seg_start < hole_start:
                    nxt.append((seg_start, hole_start))
                if hole_end < seg_end:
                    nxt.append((hole_end, seg_end))
            result = nxt
        return result

    @staticmethod
    def _overlap_minutes(first: Range, second: Range) -> int:
        """Shared minutes of two circular arcs (0 when disjoint)."""
        first_start, first_len = first
        second_start, second_len = second
        offset = (first_start - second_start) % MINUTES_PER_DAY
        total = 0
        for seg_start, seg_end in TimeRangeTool._placed_segments(
            offset, first_len
        ):
            lo = max(seg_start, 0)
            hi = min(seg_end, second_len)
            if hi > lo:
                total += hi - lo
        return total

    @classmethod
    def _range_payload(cls, clock_range: Range) -> Dict[str, Any]:
        """Serialize a circular arc as the standard output payload."""
        start, length = clock_range
        end = (start + length) % MINUTES_PER_DAY
        return {
            "start": cls._format_time(start),
            "end": cls._format_time(end),
            "minutes": length,
            "crosses_midnight": end < start,
        }

    @classmethod
    def _segments_payload(cls, clock_range: Range) -> List[List[int]]:
        """Day-local ``[x, y)`` minute segments of a range (info mode)."""
        return [[x, y] for x, y in cls._placed_segments(*clock_range)]

    # ------------------------------------------------------------------ #
    # Modes
    # ------------------------------------------------------------------ #

    def _run_overlap(
        self,
        first: Range,
        second: Range,
        start: Any,
        end: Any,
        start2: Any,
        end2: Any,
    ) -> Dict[str, Any]:
        """Shared minutes of two circular arcs, with the sub-ranges.

        The circle is cut at the second range's start: in that frame
        the second arc is the plain interval ``[0, L2)`` and the
        first arc contributes at most two segments, so the overlap is
        plain linear intersection — exact for wraparound inputs.
        """
        first_start, first_len = first
        second_start, second_len = second
        offset = (first_start - second_start) % MINUTES_PER_DAY
        overlap: List[Range] = []
        for seg_start, seg_end in self._placed_segments(offset, first_len):
            lo = max(seg_start, 0)
            hi = min(seg_end, second_len)
            if hi > lo:
                overlap.append(
                    ((second_start + lo) % MINUTES_PER_DAY, hi - lo)
                )
        overlap.sort()
        minutes = sum(length for _, length in overlap)
        return {
            "mode": "overlap",
            "first": {"start": start, "end": end,
                      **self._range_payload(first)},
            "second": {"start": start2, "end": end2,
                       **self._range_payload(second)},
            "overlap_minutes": minutes,
            "overlaps": minutes > 0,
            "overlap_ranges": [self._range_payload(r) for r in overlap],
        }

    def _run_contains(
        self, clock_range: Range, minute: int, time: Any
    ) -> Dict[str, Any]:
        """Whether a single time lies inside a half-open range.

        Membership of the circular arc: the forward distance from the
        range start must stay below its length, which pins the
        exclusive-end rule at both ends — also across midnight.
        """
        start, length = clock_range
        inside = (minute - start) % MINUTES_PER_DAY < length
        return {
            "mode": "contains",
            "start": self._format_time(start),
            "end": self._format_time((start + length) % MINUTES_PER_DAY),
            "time": time,
            "contains": inside,
            "duration_minutes": length,
            "crosses_midnight": (
                (start + length) % MINUTES_PER_DAY < start
            ),
        }

    def _run_subtract(self, clock_range: Range, removed: Range) -> Dict[str, Any]:
        """Range A minus range B, as remaining circular sub-ranges.

        The circle is cut at A's start, so A becomes ``[0, LA)`` and
        B at most two hole segments; linear subtraction of the holes
        leaves 0, 1 or 2 pieces which map back to clock ranges.
        """
        start, length = clock_range
        removed_start, removed_len = removed
        offset = (removed_start - start) % MINUTES_PER_DAY
        holes = self._placed_segments(offset, removed_len)
        pieces = self._subtract_segments([(0, length)], holes)
        remaining: List[Range] = [
            ((start + seg_start) % MINUTES_PER_DAY, seg_end - seg_start)
            for seg_start, seg_end in pieces
        ]
        remaining.sort()
        remaining_minutes = sum(n for _, n in remaining)
        return {
            "mode": "subtract",
            "start": self._format_time(start),
            "end": self._format_time((start + length) % MINUTES_PER_DAY),
            "removed": self._range_payload(removed),
            "remaining": [self._range_payload(r) for r in remaining],
            "remaining_minutes": remaining_minutes,
            "removed_minutes": length - remaining_minutes,
        }

    def _run_merge(self, parsed: List[Range]) -> Dict[str, Any]:
        """Coalesce ranges into the sorted non-overlapping cover.

        Wraparound inputs are normalized to possibly-two day-local
        segments first; coalescing then runs on the linear day-local
        timeline, where touching is unambiguous, and a tail segment
        ending at 1440 that meets a head segment starting at 0 is
        re-joined into a single wraparound output range. That
        normalization is the documented, deterministic resolution of
        the "merge across midnight is ambiguous" trap, and the result
        notes it whenever wraparound was involved. Full-day coverage
        is reported as a flag because no single pair encodes it.
        """
        segments: List[Segment] = []
        wrapped_input = False
        for start, length in parsed:
            if start + length > MINUTES_PER_DAY:
                wrapped_input = True
            segments.extend(self._placed_segments(start, length))
        merged = self._coalesce_segments(segments)

        note = None
        full_day = merged == [(0, MINUTES_PER_DAY)]
        result: List[Range] = []
        if full_day:
            note = (
                "merged coverage is the full 24h day; a single "
                "HH:MM pair cannot encode it (start == end is "
                "rejected), so ranges is empty and full_day is true"
            )
        else:
            has_head = merged[0][0] == 0
            has_tail = merged[-1][1] == MINUTES_PER_DAY
            if has_head and has_tail and len(merged) >= 2:
                # A tail [s, 1440) meets a head [0, e) across the
                # midnight boundary: one wraparound range s -> e.
                result.append(
                    (merged[-1][0],
                     (merged[0][1] - merged[-1][0]) % MINUTES_PER_DAY)
                )
                wrapped_input = True
                middle = merged[1:-1]
            else:
                middle = merged
            result.extend(
                (seg_start, seg_end - seg_start)
                for seg_start, seg_end in middle
            )
            result.sort()
        if wrapped_input and note is None:
            note = (
                "wraparound ranges were normalized to possibly-two "
                "day-local segments (22:00-06:00 -> [22:00, 24:00) + "
                "[00:00, 06:00)) and re-joined across midnight on "
                "that day-local timeline"
            )
        payload: Dict[str, Any] = {
            "mode": "merge",
            "count": len(result),
            "ranges": [self._range_payload(r) for r in result],
            "total_minutes": (
                MINUTES_PER_DAY if full_day
                else sum(n for _, n in result)
            ),
            "full_day": full_day,
        }
        if note is not None:
            payload["note"] = note
        return payload

    def _run_gap(self, first: Range, second: Range) -> Dict[str, Any]:
        """Idle minutes between two ranges and the complement arcs.

        The circular complement of the union of both arcs is computed
        on the day-local timeline cut at the first range's start.
        When the ranges intersect or merely touch, the idle time
        between them is 0 by definition (ends are exclusive, so
        touching ranges are back-to-back); otherwise the two arcs
        leave exactly two gaps and the idle window is the smaller
        one. The full complement is always listed for inspection.
        """
        first_start, first_len = first
        second_start, second_len = second
        segments = self._placed_segments(0, first_len) + (
            self._placed_segments(
                (second_start - first_start) % MINUTES_PER_DAY, second_len
            )
        )
        merged = self._coalesce_segments(segments)

        gaps: List[Range] = []
        if merged == [(0, MINUTES_PER_DAY)]:
            pass  # the two ranges tile the whole day: no idle minute
        elif len(merged) == 1:
            seg_start, seg_end = merged[0]
            gaps = [((first_start + seg_end) % MINUTES_PER_DAY,
                     (seg_start - seg_end) % MINUTES_PER_DAY)]
        else:
            for (_, end), (next_start, _) in zip(merged, merged[1:]):
                gaps.append(
                    ((first_start + end) % MINUTES_PER_DAY,
                     (next_start - end) % MINUTES_PER_DAY)
                )
            last_end = merged[-1][1]
            gaps.append(
                ((first_start + last_end) % MINUTES_PER_DAY,
                 (merged[0][0] - last_end) % MINUTES_PER_DAY)
            )
        gaps.sort()

        overlap_minutes = self._overlap_minutes(first, second)
        touches = (
            (first_start + first_len) % MINUTES_PER_DAY == second_start
            or (second_start + second_len) % MINUTES_PER_DAY == first_start
        )
        connected = overlap_minutes > 0 or touches
        gap_minutes = 0 if connected else min(n for _, n in gaps)
        return {
            "mode": "gap",
            "first": self._range_payload(first),
            "second": self._range_payload(second),
            "gap_minutes": gap_minutes,
            "gaps": [self._range_payload(g) for g in gaps],
            "connected": connected,
            "union_minutes": first_len + second_len - overlap_minutes,
        }

    def _run_info(
        self, clock_range: Range, start: Any, end: Any
    ) -> Dict[str, Any]:
        """Duration, midnight flag and day-local segments of a range."""
        start_minute, length = clock_range
        end_minute = (start_minute + length) % MINUTES_PER_DAY
        return {
            "mode": "info",
            "input": {"start": start, "end": end},
            "start": self._format_time(start_minute),
            "end": self._format_time(end_minute),
            "start_minutes": start_minute,
            "end_minutes": end_minute,
            "duration_minutes": length,
            "crosses_midnight": end_minute < start_minute,
            "segments": self._segments_payload(clock_range),
        }
