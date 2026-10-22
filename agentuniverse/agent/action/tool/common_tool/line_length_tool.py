#!/usr/bin/env python3
"""Line-length distribution auditing for lint-style text QA."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import unicodedata
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool


class LineLengthTool(Tool):
    """Audit how long the lines of a text are before pasting it into terminals, PRs, or docs.

    The tool is a read-only counterpart to string-shaping helpers: it measures
    line widths and reports where a configured limit would be exceeded, but it
    never rewrites the text. Four modes are supported:

    - ``audit``: full report — total lines, length stats (min/mean/median/max),
      an eight-bucket length histogram, the count of lines over ``limit`` with
      the first 50 offenders, and the longest line.
    - ``find``: positions of lines either over ``limit`` (``direction="over"``)
      or within ``[min_length, limit)`` (``direction="under"``), capped at 100.
    - ``stats_only``: the distribution without needing a limit.
    - ``wrap_preview``: count-only preview of how many lines a
      TextWrapTool-style wrap at ``width=limit`` would reflow (lines longer
      than ``limit``); the wrap itself is not performed.

    Measurement conventions:

    - Lines are produced by ``str.splitlines``: ``\\n``, ``\\r\\n``, and ``\\r``
      all terminate lines and the terminator is excluded from the length. A
      trailing terminator does not create an extra final empty line
      (``"a\\n"`` is one line), and an empty text has zero lines.
    - Empty lines are counted in ``total_lines`` and land in the ``0-20``
      histogram bucket.
    - By default lengths count code points. With ``display_width=True`` lines
      are measured in terminal columns using east-asian width (wide/fullwidth
      characters count as 2, everything else as 1) so CJK text is judged the
      way a terminal renders it. Previews are always truncated by code points.
    """

    max_lines: int = 100_000
    max_text_chars: int = 10_000_000
    max_offending_lines: int = 50
    max_find_results: int = 100
    min_limit: int = 1
    max_limit: int = 10_000

    _MODES: ClassVar[tuple[str, ...]] = ("audit", "find", "stats_only", "wrap_preview")
    _DIRECTIONS: ClassVar[tuple[str, ...]] = ("over", "under")
    _BUCKET_BOUNDS: ClassVar[tuple[int, ...]] = (20, 40, 60, 80, 100, 120, 160)
    _BUCKET_LABELS: ClassVar[tuple[str, ...]] = (
        "0-20",
        "21-40",
        "41-60",
        "61-80",
        "81-100",
        "101-120",
        "121-160",
        "161+",
    )
    _PREVIEW_CHARS: ClassVar[int] = 60
    _WRAP_NOTE: ClassVar[str] = (
        "Count-only preview: lines whose measured length exceeds the limit are exactly the "
        "lines a TextWrapTool-style wrap at that width would reflow. This tool does not "
        "modify the text; use TextWrapTool (#3555) to perform the actual wrapping."
    )

    def execute(
        self,
        mode: str = "audit",
        text: str = "",
        limit: int | None = None,
        min_length: int | None = None,
        direction: str = "over",
        display_width: bool = False,
    ) -> dict[str, Any]:
        try:
            operation = self._mode(mode)
            body = self._text(text)
            checked_limit = self._limit(limit, operation)
            checked_direction = self._direction(direction, operation)
            checked_min = self._min_length(min_length, operation, checked_direction, checked_limit)
            checked_display = self._display_width(display_width)
            lines = body.splitlines()
            if len(lines) > self.max_lines:
                raise ValueError(f"text has more than max_lines ({self.max_lines}) lines")
            lengths = [self._measure(line, checked_display) for line in lines]
            common = {
                "mode": operation,
                "measure": "display_columns" if checked_display else "codepoints",
                "total_lines": len(lines),
            }
            if operation == "find":
                return self._find(lines, lengths, common, checked_limit, checked_min, checked_direction)
            distribution = self._distribution(lines, lengths)
            if operation == "stats_only":
                return {"status": "success", **common, **distribution}
            if operation == "wrap_preview":
                over = [i + 1 for i, length in enumerate(lengths) if length > checked_limit]
                return {
                    "status": "success",
                    **common,
                    "limit": checked_limit,
                    "lines_over_limit": len(over),
                    "wrap_required": bool(over),
                    "over_limit_line_nos": over[: self.max_offending_lines],
                    "over_limit_truncated": len(over) > self.max_offending_lines,
                    "note": self._WRAP_NOTE,
                }
            return self._audit(lines, lengths, common, distribution, checked_limit)
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc))
        except Exception as exc:
            return self._error("operation_error", f"Line length audit failed: {exc}")

    @staticmethod
    def _error(kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message}

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in LineLengthTool._MODES:
            raise ValueError("mode must be audit, find, stats_only, or wrap_preview")
        return mode

    def _text(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("text must be a string")
        if len(value) > self.max_text_chars:
            raise ValueError(f"text exceeds max_text_chars ({self.max_text_chars})")
        return value

    def _limit(self, value: Any, operation: str) -> int:
        if value is None:
            if operation == "stats_only":
                return 0
            return 80
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("limit must be an integer")
        if not self.min_limit <= value <= self.max_limit:
            raise ValueError(f"limit must be between {self.min_limit} and {self.max_limit}")
        return value

    @staticmethod
    def _direction(value: Any, operation: str) -> str:
        if operation != "find":
            return "over"
        if not isinstance(value, str):
            raise TypeError("direction must be a string")
        direction = value.strip().lower()
        if direction not in LineLengthTool._DIRECTIONS:
            raise ValueError("direction must be over or under")
        return direction

    @staticmethod
    def _min_length(value: Any, operation: str, direction: str, limit: int) -> int:
        if operation != "find":
            if value is not None:
                raise ValueError("min_length is only valid in find mode")
            return 0
        if value is None:
            return 0
        if direction != "under":
            raise ValueError("min_length is only valid when direction is under")
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("min_length must be an integer")
        if value < 0 or value >= limit:
            raise ValueError(f"min_length must be between 0 and {limit - 1} for limit {limit}")
        return value

    @staticmethod
    def _display_width(value: Any) -> bool:
        if not isinstance(value, bool):
            raise TypeError("display_width must be a boolean")
        return value

    @staticmethod
    def _measure(line: str, display_width: bool) -> int:
        if not display_width:
            return len(line)
        return sum(2 if unicodedata.east_asian_width(char) in ("W", "F") else 1 for char in line)

    @classmethod
    def _preview(cls, line: str) -> str:
        if len(line) <= cls._PREVIEW_CHARS:
            return line
        return line[: cls._PREVIEW_CHARS] + "..."

    @classmethod
    def _longest(cls, lines: list[str], lengths: list[int]) -> dict[str, Any] | None:
        if not lengths:
            return None
        index = lengths.index(max(lengths))
        return {
            "line_no": index + 1,
            "length": lengths[index],
            "preview": cls._preview(lines[index]),
        }

    @classmethod
    def _distribution(cls, lines: list[str], lengths: list[int]) -> dict[str, Any]:
        histogram = dict.fromkeys(cls._BUCKET_LABELS, 0)
        for length in lengths:
            histogram[cls._bucket(length)] += 1
        if lengths:
            ordered = sorted(lengths)
            count = len(ordered)
            middle = count // 2
            median = ordered[middle] if count % 2 else (ordered[middle - 1] + ordered[middle]) / 2
            stats = {
                "min": ordered[0],
                "mean": round(sum(ordered) / count, 2),
                "median": round(median, 2),
                "max": ordered[-1],
            }
        else:
            stats = {"min": 0, "mean": 0, "median": 0, "max": 0}
        return {"stats": stats, "histogram": histogram, "longest_line": cls._longest(lines, lengths)}

    @classmethod
    def _bucket(cls, length: int) -> str:
        for bound, label in zip(cls._BUCKET_BOUNDS, cls._BUCKET_LABELS):
            if length <= bound:
                return label
        return cls._BUCKET_LABELS[-1]

    def _audit(
        self,
        lines: list[str],
        lengths: list[int],
        common: dict[str, Any],
        distribution: dict[str, Any],
        limit: int,
    ) -> dict[str, Any]:
        offenders = [
            {"line_no": i + 1, "length": length, "preview": self._preview(line)}
            for i, (line, length) in enumerate(zip(lines, lengths))
            if length > limit
        ]
        return {
            "status": "success",
            **common,
            "limit": limit,
            **distribution,
            "over_limit": len(offenders),
            "over_limit_lines": offenders[: self.max_offending_lines],
            "over_limit_truncated": len(offenders) > self.max_offending_lines,
        }

    def _find(
        self,
        lines: list[str],
        lengths: list[int],
        common: dict[str, Any],
        limit: int,
        min_length: int,
        direction: str,
    ) -> dict[str, Any]:
        if direction == "over":
            matches = [(i, length) for i, length in enumerate(lengths) if length > limit]
        else:
            matches = [(i, length) for i, length in enumerate(lengths) if min_length <= length < limit]
        return {
            "status": "success",
            **common,
            "limit": limit,
            "direction": direction,
            "min_length": min_length if direction == "under" else None,
            "match_count": len(matches),
            "matches": [
                {"line_no": i + 1, "length": length, "preview": self._preview(lines[i])}
                for i, length in matches[: self.max_find_results]
            ],
            "truncated": len(matches) > self.max_find_results,
        }
