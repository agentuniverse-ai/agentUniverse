#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: cron_expression_tool.py

"""Cron expression parsing / explanation tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency schedule helper:
agents frequently need to reason about cron schedules emitted by
platforms, CI systems or operators, and this tool lets them validate,
explain and project those expressions without shelling out to
``crontab`` or pulling a third-party cron library.

Supported syntax — standard five-field Vixie-style cron:

* fields: ``minute`` (0-59), ``hour`` (0-23), ``day of month`` (1-31),
  ``month`` (1-12), ``day of week`` (0-7, where both 0 and 7 mean
  Sunday).
* per-field atoms: ``*`` (all values), a single number, a range
  ``a-b``, and any comma-separated list of those; steps ``/n`` are
  supported as ``*/n`` (whole field), ``a-b/n`` (stepped range) and
  ``a/n`` (from ``a`` to the end of the field, stepped).
* month names ``jan``-``dec`` and day names ``sun``-``sat``
  (case-insensitive), also inside ranges such as ``mon-fri``.
* macros ``@daily`` (also ``@midnight``), ``@hourly``, ``@weekly``,
  ``@monthly`` and ``@yearly`` (also ``@annually``).
* standard day-of-month / day-of-week OR semantics: when *both* fields
  are restricted (neither is the literal ``*``), a day matches when
  *either* field matches.

Deliberately **not** supported (they fail validation with a precise
per-field error rather than being misread): Quartz / Jenkins extensions
such as ``L`` (last day), ``W`` (nearest weekday), ``#`` (nth weekday)
and ``?``; six-field expressions with a seconds or year field; and the
``@reboot`` macro (scheduling semantics, not an expression to parse).

Three modes:

* ``validate`` — parse the expression and report per-field errors
  precisely (value out of range, reversed range, non-positive step,
  unrecognized name, stray characters, wrong field count, unknown
  macro).
* ``describe`` — a human-readable English summary, e.g. ``30 * * * *``
  becomes "At 30 minutes past every hour".
* ``next`` — the next N run datetimes strictly after a given (or
  injected) ``now``.  Matches are found by iterating candidate minutes
  with wholesale skips: a non-matching month jumps to the first minute
  of the next month, a non-matching day jumps to the next midnight, a
  non-matching hour jumps to the next hour boundary, so each loop pass
  performs O(1) work and skips at least one minute.  A hard iteration
  cap (``max_iterations``, default 1,000,000, at most 5,000,000)
  bounds the number of candidate examinations — worst-case runtime is
  therefore O(max_iterations) constant-time checks and memory stays
  O(count).  Honest limits: expressions that can *never* match (for
  example ``0 0 31 2 *``, February 31st) exhaust the cap and return an
  ``iteration_cap_exceeded`` error instead of looping forever, and the
  scan is bounded by roughly ``max_iterations`` minutes / days /
  months of skip distance rather than an unbounded calendar search.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode, missing expression,
non-integer or out-of-range ``count`` / ``max_iterations``, unparsable
``now``) raise a ``ValueError``, mirroring the other common tools.
Errors that depend on the *content being processed* — an invalid cron
expression in the ``describe`` / ``next`` modes, or exhausting the
iteration cap — are returned as structured ``error`` payloads so an
agent can react without catching exceptions.  The ``validate`` mode
never raises for content problems; it reports them per field in its
normal result.
"""

from datetime import datetime, timedelta
from typing import Any, ClassVar, Dict, FrozenSet, List, Optional, Set, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Cron day-of-week numbering: 0 (and 7) = Sunday ... 6 = Saturday.
# Python's datetime.weekday() numbers Monday=0..Sunday=6, so the cron
# day of an arbitrary datetime is (weekday + 1) % 7.
_CRON_SUNDAY = 0

MONTH_NAMES: Dict[str, int] = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
DOW_NAMES: Dict[str, int] = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6,
}
MONTH_FULL_NAMES: Dict[int, str] = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May",
    6: "June", 7: "July", 8: "August", 9: "September", 10: "October",
    11: "November", 12: "December",
}
DOW_FULL_NAMES: Dict[int, str] = {
    0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
    5: "Friday", 6: "Saturday",
}

# Field order of a five-field cron expression plus allowed ranges and
# the (optional) name table each field accepts.
FIELD_SPECS: Tuple[Dict[str, Any], ...] = (
    {"name": "minute", "low": 0, "high": 59, "names": None},
    {"name": "hour", "low": 0, "high": 23, "names": None},
    {"name": "day-of-month", "low": 1, "high": 31, "names": None},
    {"name": "month", "low": 1, "high": 12, "names": MONTH_NAMES},
    {"name": "day-of-week", "low": 0, "high": 7, "names": DOW_NAMES},
)


class CronExpressionTool(Tool):
    """Parse, validate, explain and project cron expressions (stdlib only).

    Attributes:
        default_max_iterations (int): Default hard cap on candidate
            examinations for the ``next`` mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "cron_expression_tool"
    description: str = (
        "Cron expression tool — pure Python stdlib, no network required. "
        "Parses standard five-field cron expressions (minute hour "
        "day-of-month month day-of-week) supporting '*', lists, ranges, "
        "steps, month/day names and the @daily/@hourly/@weekly/@monthly/"
        "@yearly macros. mode='validate' reports per-field parse errors, "
        "mode='describe' returns a human-readable English summary, and "
        "mode='next' returns the next N run datetimes after a given or "
        "injected now (minute iteration with a hard iteration cap)."
    )

    MODES: ClassVar[tuple] = ("validate", "describe", "next")
    # @-macros expand to fixed five-field expressions (crontab(5)).
    MACROS: ClassVar[Dict[str, str]] = {
        "@yearly": "0 0 1 1 *",
        "@annually": "0 0 1 1 *",
        "@monthly": "0 0 1 * *",
        "@weekly": "0 0 * * 0",
        "@daily": "0 0 * * *",
        "@midnight": "0 0 * * *",
        "@hourly": "0 * * * *",
    }
    DEFAULT_MAX_ITERATIONS: ClassVar[int] = 1_000_000
    HARD_MAX_ITERATIONS: ClassVar[int] = 5_000_000
    MAX_COUNT: ClassVar[int] = 100

    default_max_iterations: int = 1_000_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        expression: Any = None,
        now: Any = None,
        count: Any = None,
        max_iterations: Any = None,
    ) -> Dict[str, Any]:
        """Run one cron operation.

        Args:
            mode (str): One of ``validate`` / ``describe`` / ``next``.
            expression (str): The cron expression — either five
                whitespace-separated fields or one of the supported
                ``@`` macros. Required for every mode.
            now (str | datetime): ``next`` mode only — the reference
                "current" time; matches are strictly after it. Accepts
                an ISO-8601 string (``2026-01-15T10:30:00`` or just
                ``2026-01-15``) or a ``datetime``; defaults to the
                system clock. Tests inject a fixed value.
            count (int): ``next`` mode only — how many upcoming run
                datetimes to return; 1-100, default 1.
            max_iterations (int): ``next`` mode only — hard cap on
                candidate examinations (1-5,000,000, default
                1,000,000). Unmatchable expressions exhaust the cap
                and return an ``iteration_cap_exceeded`` error.

        Returns:
            Dict[str, Any]: ``validate`` returns ``valid`` plus
                ``errors`` (per field) and, on success, the expanded
                ``fields`` and a ``normalized`` expression.
                ``describe`` returns a human-readable ``description``.
                ``next`` returns ``matches`` (ISO-8601 strings strictly
                after ``now``), the resolved ``now`` and the number of
                ``iteration_checks`` performed. Content-level failures
                (invalid expression in describe/next, exhausted
                iteration cap) return a structured ``error`` payload.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_expression = self._validate_expression(expression)
        if mode == "validate":
            return self._run_validate(clean_expression)

        # Malformed `next` parameters raise before any computation, as
        # documented — even when the expression itself is invalid too.
        clean_now: Optional[datetime] = None
        clean_count = clean_cap = 0
        if mode == "next":
            clean_count = self._validate_count(count)
            clean_cap = self._validate_max_iterations(max_iterations)
            clean_now = self._validate_now(now)

        parsed = self._parse(clean_expression)
        if parsed.error_fields:
            return self._expression_error(mode, clean_expression, parsed)
        if mode == "describe":
            return {
                "mode": "describe",
                "expression": clean_expression,
                "description": self._describe(parsed),
            }
        return self._run_next(
            clean_expression, parsed, clean_now, clean_count, clean_cap
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"cron_expression_tool: {message}")

    @classmethod
    def _validate_expression(cls, expression: Any) -> str:
        """Validate the ``expression`` parameter (type-level checks only)."""
        if (
            expression is None
            or isinstance(expression, bool)
            or not isinstance(expression, str)
        ):
            cls._invalid(
                f"expression must be a non-empty cron string (got {expression!r})"
            )
        expression = expression.strip()
        if not expression:
            cls._invalid("expression must be a non-empty cron string (got '')")
        if len(expression) > 200:
            cls._invalid(
                f"expression exceeds the 200-character limit "
                f"(got {len(expression)} characters)"
            )
        return expression

    @classmethod
    def _validate_count(cls, count: Any) -> int:
        """Validate the ``next``-mode match count."""
        if count is None:
            return 1
        if isinstance(count, bool) or not isinstance(count, int):
            cls._invalid(f"count must be an integer between 1 and 100 (got {count!r})")
        if not 1 <= count <= cls.MAX_COUNT:
            cls._invalid(
                f"count must be an integer between 1 and {cls.MAX_COUNT} "
                f"(got {count!r})"
            )
        return count

    @classmethod
    def _validate_max_iterations(cls, max_iterations: Any) -> int:
        """Validate the ``next``-mode iteration cap."""
        if max_iterations is None:
            return cls.DEFAULT_MAX_ITERATIONS
        if isinstance(max_iterations, bool) or not isinstance(max_iterations, int):
            cls._invalid(
                "max_iterations must be an integer between 1 and "
                f"{cls.HARD_MAX_ITERATIONS:,} (got {max_iterations!r})"
            )
        if not 1 <= max_iterations <= cls.HARD_MAX_ITERATIONS:
            cls._invalid(
                "max_iterations must be an integer between 1 and "
                f"{cls.HARD_MAX_ITERATIONS:,} (got {max_iterations:,})"
            )
        return max_iterations

    @classmethod
    def _validate_now(cls, now: Any) -> datetime:
        """Resolve and validate the ``next``-mode reference time.

        Accepts ``None`` (system clock), a ``datetime`` or an ISO-8601
        string (a bare date is treated as midnight of that day).
        """
        if now is None:
            return datetime.now()
        if isinstance(now, datetime):
            return now
        if isinstance(now, bool) or not isinstance(now, str):
            cls._invalid(
                "now must be a datetime or an ISO-8601 string such as "
                f"'2026-01-15T10:30:00' (got {now!r})"
            )
        try:
            return datetime.fromisoformat(now.strip())
        except ValueError:
            cls._invalid(
                "now must be an ISO-8601 datetime such as "
                f"'2026-01-15T10:30:00' or a date like '2026-01-15' "
                f"(got {now[:64]!r})"
            )

    # ------------------------------------------------------------------ #
    # Expression parsing
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse(cls, expression: str) -> "_ParsedCron":
        """Parse a cron expression into per-field allowed-value sets.

        Any content problem (wrong field count, unknown macro, bad
        atom) is collected into ``error_fields`` instead of raising so
        the ``validate`` mode can report every broken field at once.
        """
        errors: List[Dict[str, str]] = []
        tokens = expression.split()
        if tokens[0].startswith("@"):
            if len(tokens) != 1:
                errors.append({
                    "field": "macro",
                    "message": (
                        "a macro must be a single token such as "
                        f"@daily, got {len(tokens)} tokens"
                    ),
                })
                return _ParsedCron(errors, expression)
            macro = tokens[0].lower()
            if macro not in cls.MACROS:
                errors.append({
                    "field": "macro",
                    "message": (
                        "unknown macro — supported macros are: "
                        f"{', '.join(sorted(set(cls.MACROS)))} "
                        f"(got {tokens[0][:64]!r})"
                    ),
                })
                return _ParsedCron(errors, expression)
            expanded = cls.MACROS[macro]
            parsed = cls._parse_fields(expanded.split(), errors)
            parsed.macro = macro
            parsed.expanded = expanded
            return parsed
        return cls._parse_fields(tokens, errors)

    @classmethod
    def _parse_fields(
        cls, tokens: List[str], errors: List[Dict[str, str]]
    ) -> "_ParsedCron":
        """Expand the five field tokens (no macro handling)."""
        if len(tokens) != 5:
            errors.append({
                "field": "expression",
                "message": (
                    "a cron expression must contain exactly 5 "
                    "whitespace-separated fields (minute hour "
                    "day-of-month month day-of-week); "
                    f"got {len(tokens)} field(s)"
                ),
            })
            return _ParsedCron(errors, None)
        sets: List[Set[int]] = []
        stars: List[bool] = []
        for token, spec in zip(tokens, FIELD_SPECS):
            allowed, info = cls._expand_field(token, spec)
            if allowed is None:
                errors.append({"field": spec["name"], "message": info})
            else:
                sets.append(allowed)
                stars.append(info)
        if errors:
            return _ParsedCron(errors, None)
        return _ParsedCron([], None, sets=tuple(frozenset(s) for s in sets),
                           stars=tuple(stars))

    @classmethod
    def _expand_field(
        cls, token: str, spec: Dict[str, Any]
    ) -> Tuple[Optional[Set[int]], Any]:
        """Expand one field token to its allowed-value set.

        Returns ``(allowed_set, is_star)`` on success — ``is_star`` is
        True only for the literal ``*`` — or ``(None, error_message)``
        on failure.
        """
        name, low, high, names = (
            spec["name"], spec["low"], spec["high"], spec["names"]
        )
        allowed: Set[int] = set()
        for part in token.split(","):
            if not part:
                return None, (
                    f"the {name} field contains an empty list element; "
                    f"use single values without stray commas (got {token[:64]!r})"
                )
            error = cls._expand_part(part, name, low, high, names, allowed)
            if error:
                return None, error
        return allowed, token == "*"

    @classmethod
    def _expand_part(
        cls,
        part: str,
        name: str,
        low: int,
        high: int,
        names: Optional[Dict[str, int]],
        allowed: Set[int],
    ) -> Optional[str]:
        """Expand one comma-separated atom (``*``, ``a``, ``a-b``, with step)."""
        # Optional step suffix.
        step = 1
        base = part
        if "/" in part:
            base, _, step_text = part.partition("/")
            if not step_text:
                return (
                    f"the {name} field has a '/' with no step value "
                    f"(got {part[:64]!r})"
                )
            # Plain ASCII digit runs only: int() would also accept
            # underscores ('1_5'), signs ('+2') and non-ASCII digits,
            # none of which are cron syntax.
            if not (step_text.isascii() and step_text.isdigit()):
                return (
                    f"the {name} field step must be a positive integer "
                    f"(got {step_text[:64]!r})"
                )
            step = int(step_text)
            if step < 1:
                return (
                    f"the {name} field step must be a positive integer, "
                    f"not {step}"
                )

        # Base: '*', a single value, or a range.
        if base == "*":
            start, end = low, high
        elif "-" in base:
            start_text, _, end_text = base.partition("-")
            start, error = cls._parse_value(start_text, name, low, high, names)
            if error:
                return error
            end, error = cls._parse_value(end_text, name, low, high, names)
            if error:
                return error
            if start > end:
                return (
                    f"the {name} field range start {start_text[:64]} is "
                    f"greater than the range end {end_text[:64]}"
                )
        else:
            value, error = cls._parse_value(base, name, low, high, names)
            if error:
                return error
            if "/" in part:
                # 'a/n' — from a to the end of the field, stepped.
                start, end = value, high
            else:
                start, end = value, value
        allowed.update(range(start, end + 1, step))
        # Day-of-week: both 0 and 7 mean Sunday.
        if name == "day-of-week" and high == 7 and 7 in allowed:
            allowed.discard(7)
            allowed.add(_CRON_SUNDAY)
        return None

    @classmethod
    def _parse_value(
        cls,
        text: str,
        name: str,
        low: int,
        high: int,
        names: Optional[Dict[str, int]],
    ) -> Tuple[Optional[int], Optional[str]]:
        """Parse one boundary value: a number or a month/day name."""
        value_text = text.strip()
        if not value_text:
            return None, (
                f"the {name} field contains an empty value "
                f"(got {text[:64]!r})"
            )
        if names is not None and value_text.lower() in names:
            return names[value_text.lower()], None
        # Plain ASCII digit runs only: int() would also accept
        # underscores ('1_0'), signs ('+5') and non-ASCII digit
        # characters (e.g. Eastern Arabic numerals), none of which are
        # cron syntax.
        if not (value_text.isascii() and value_text.isdigit()):
            if names is MONTH_NAMES:
                hint = " (month names jan-dec are also accepted)"
            elif names is DOW_NAMES:
                hint = " (day names sun-sat are also accepted)"
            else:
                hint = ""
            return None, (
                f"the {name} field value {value_text[:64]!r} is not a "
                f"valid integer{hint}"
            )
        value = int(value_text)
        if not low <= value <= high:
            return None, (
                f"the {name} field value {value} is out of range "
                f"{low}-{high}"
            )
        return value, None

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def _run_validate(self, expression: str) -> Dict[str, Any]:
        """Validate and report per-field errors / expanded fields."""
        parsed = self._parse(expression)
        if parsed.error_fields:
            return {
                "mode": "validate",
                "expression": expression,
                "valid": False,
                "errors": parsed.error_fields,
            }
        result: Dict[str, Any] = {
            "mode": "validate",
            "expression": expression,
            "valid": True,
            "errors": [],
            "fields": {
                spec["name"]: sorted(values)
                for spec, values in zip(FIELD_SPECS, parsed.sets)
            },
            "normalized": self._normalize(parsed),
        }
        if parsed.macro:
            result["macro"] = parsed.macro
            result["expanded"] = parsed.expanded
        return result

    @classmethod
    def _normalize(cls, parsed: "_ParsedCron") -> str:
        """Render the parsed fields as a compact canonical expression."""
        parts = []
        for values, is_star in zip(parsed.sets, parsed.stars):
            if is_star:
                parts.append("*")
                continue
            pieces = []
            for run_start, run_end in cls._runs(sorted(values)):
                if run_start == run_end:
                    pieces.append(str(run_start))
                elif run_end - run_start == 1:
                    pieces.extend((str(run_start), str(run_end)))
                else:
                    pieces.append(f"{run_start}-{run_end}")
            parts.append(",".join(pieces))
        return " ".join(parts)

    # ------------------------------------------------------------------ #
    # describe mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _describe(cls, parsed: "_ParsedCron") -> str:
        """Build a human-readable English summary."""
        minutes, hours, dom, month, dow = parsed.sets
        dom_star, month_star, dow_star = (
            parsed.stars[2], parsed.stars[3], parsed.stars[4]
        )

        time_part = cls._describe_time(minutes, hours)
        day_part = cls._describe_days(dom, dom_star, dow, dow_star)
        month_part = "" if month_star else (
            "in " + cls._render_runs(sorted(month), cls._render_month_name)
        )
        return ", ".join(p for p in (time_part, day_part, month_part) if p)

    @classmethod
    def _describe_time(
        cls, minutes: FrozenSet[int], hours: FrozenSet[int]
    ) -> str:
        """Describe the minute/hour part of the schedule."""
        if len(minutes) == 60 and len(hours) == 24:
            return "Every minute"
        if len(hours) == 24:
            if len(minutes) == 1:
                only = next(iter(minutes))
                return (
                    f"At {only} minute"
                    f"{'s' if only != 1 else ''} past every hour"
                )
            step = cls._uniform_step(minutes, 0)
            if step is not None:
                return f"Every {step} minutes"
            return (
                "At minutes "
                + cls._join_names([str(m) for m in sorted(minutes)])
                + " past every hour"
            )
        if len(minutes) == 60:
            hour_names = [f"hour {h:02d}" for h in sorted(hours)]
            return "Every minute during " + cls._join_names(hour_names)
        times = [
            f"{h:02d}:{m:02d}" for h in sorted(hours) for m in sorted(minutes)
        ]
        return "At " + cls._join_names(times)

    @classmethod
    def _describe_days(
        cls,
        dom: FrozenSet[int],
        dom_star: bool,
        dow: FrozenSet[int],
        dow_star: bool,
    ) -> str:
        """Describe the day-of-month / day-of-week part (OR semantics)."""
        if dom_star and dow_star:
            return ""
        dom_text = (
            "" if dom_star
            else cls._render_runs(
                sorted(dom), cls._render_dom_start, cls._render_dom_end
            )
        )
        dow_text = (
            "" if dow_star
            else cls._render_runs(sorted(dow), DOW_FULL_NAMES.__getitem__)
        )
        if dom_text and dow_text:
            return f"on {dom_text} or on {dow_text} (whichever matches)"
        return "on " + (dom_text or dow_text)

    @staticmethod
    def _render_month_name(value: int) -> str:
        """Render one month run endpoint for the describe mode."""
        return MONTH_FULL_NAMES[value]

    @staticmethod
    def _render_dom_start(value: int) -> str:
        """Render the first endpoint of a day-of-month run."""
        return f"day {value}"

    @staticmethod
    def _render_dom_end(value: int) -> str:
        """Render the last endpoint of a day-of-month run."""
        return f"day {value} of the month"

    @classmethod
    def _render_runs(cls, values: List[int], render, render_end=None) -> str:
        """Describe a sorted value set, compressing consecutive runs.

        Singletons render as the plain name, runs of length two as
        "X and Y" and longer runs as "X through Y" (e.g. "Monday
        through Friday", "day 1 through day 5 of the month").  The
        optional ``render_end`` renders the final endpoint of a run
        differently, as the day-of-month renderer does.
        """
        render_end = render_end or render
        pieces: List[str] = []
        for run_start, run_end in cls._runs(values):
            if run_start == run_end:
                pieces.append(render_end(run_start))
            elif run_end - run_start == 1:
                pieces.append(f"{render(run_start)} and {render_end(run_end)}")
            else:
                pieces.append(
                    f"{render(run_start)} through {render_end(run_end)}"
                )
        return cls._join_names(pieces)

    @staticmethod
    def _runs(values: List[int]) -> List[Tuple[int, int]]:
        """Compress a sorted list into inclusive consecutive runs."""
        runs: List[Tuple[int, int]] = []
        start = prev = values[0]
        for value in values[1:]:
            if value == prev + 1:
                prev = value
                continue
            runs.append((start, prev))
            start = prev = value
        runs.append((start, prev))
        return runs

    @classmethod
    def _uniform_step(
        cls, values: FrozenSet[int], start: int
    ) -> Optional[int]:
        """Return n when values are exactly start, start+n, ... up to 59."""
        ordered = sorted(values)
        if len(ordered) < 2 or ordered[0] != start:
            return None
        step = ordered[1] - ordered[0]
        if step < 1 or ordered != list(range(start, 60, step)):
            return None
        return step

    @classmethod
    def _join_names(cls, names: List[str]) -> str:
        """Join a list of names/times, bounding very long enumerations."""
        if len(names) == 1:
            return names[0]
        if len(names) == 2:
            return f"{names[0]} and {names[1]}"
        if len(names) <= 6:
            return ", ".join(names[:-1]) + f" and {names[-1]}"
        head = ", ".join(names[:6])
        return f"{head}, … and {len(names) - 6} more"

    # ------------------------------------------------------------------ #
    # next mode
    # ------------------------------------------------------------------ #

    def _run_next(
        self,
        expression: str,
        parsed: "_ParsedCron",
        now: datetime,
        count: int,
        max_iterations: int,
    ) -> Dict[str, Any]:
        """Compute the next run datetimes after ``now``.

        ``now`` / ``count`` / ``max_iterations`` arrive already
        validated by :meth:`execute`.
        """
        matches, capped, checks = self._iterate_matches(
            parsed, now, count, max_iterations
        )
        base: Dict[str, Any] = {
            "mode": "next",
            "expression": expression,
            "now": now.isoformat(),
            "count": count,
        }
        if capped:
            return {
                **base,
                "error": {
                    "type": "iteration_cap_exceeded",
                    "message": (
                        f"gave up after {max_iterations:,} candidate checks "
                        f"with {len(matches)} of {count} requested "
                        "matches found — the expression is either "
                        "unmatchable (e.g. February 31st) or its next "
                        "runs lie beyond the scan horizon; raise "
                        "max_iterations (up to "
                        f"{self.HARD_MAX_ITERATIONS:,}) or widen the "
                        "schedule"
                    ),
                },
                "matches": [m.isoformat() for m in matches],
                "iteration_checks": checks,
            }
        return {
            **base,
            "matches": [m.isoformat() for m in matches],
            "iteration_checks": checks,
        }

    @classmethod
    def _iterate_matches(
        cls,
        parsed: "_ParsedCron",
        now: datetime,
        count: int,
        cap: int,
    ) -> Tuple[List[datetime], bool, int]:
        """Iterate candidate minutes after ``now`` collecting matches.

        Each loop pass performs O(1) work and skips at least one
        minute: non-matching months jump to the next month start,
        non-matching days jump to the next midnight and non-matching
        hours jump to the next hour boundary.  The hard ``cap`` bounds
        the number of passes, so total work is O(cap) and memory is
        O(count).
        """
        minutes, hours, dom, months, dow = parsed.sets
        dom_star, dow_star = parsed.stars[2], parsed.stars[4]

        def day_matches(candidate: datetime) -> bool:
            dom_hit = candidate.day in dom
            dow_hit = (candidate.weekday() + 1) % 7 in dow
            if dom_star:
                return dow_hit
            if dow_star:
                return dom_hit
            return dom_hit or dow_hit  # standard cron OR semantics

        # Candidates start strictly after `now` (floored to the minute).
        cursor = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        matches: List[datetime] = []
        checks = 0
        while len(matches) < count:
            checks += 1
            if checks > cap:
                return matches, True, checks - 1
            if cursor.month not in months:
                if cursor.month == 12:
                    cursor = cursor.replace(
                        year=cursor.year + 1, month=1, day=1, hour=0, minute=0
                    )
                else:
                    cursor = cursor.replace(
                        month=cursor.month + 1, day=1, hour=0, minute=0
                    )
                continue
            if not day_matches(cursor):
                cursor = (cursor + timedelta(days=1)).replace(hour=0, minute=0)
                continue
            if cursor.hour not in hours:
                cursor = (cursor + timedelta(hours=1)).replace(minute=0)
                continue
            if cursor.minute not in minutes:
                cursor = cursor + timedelta(minutes=1)
                continue
            matches.append(cursor)
            cursor = cursor + timedelta(minutes=1)
        return matches, False, checks

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    def _expression_error(
        self, mode: str, expression: str, parsed: "_ParsedCron"
    ) -> Dict[str, Any]:
        """Build the structured error payload for an invalid expression."""
        summary = "; ".join(
            f"{error['field']}: {error['message']}"
            for error in parsed.error_fields
        )
        return {
            "mode": mode,
            "expression": expression,
            "error": {
                "type": "invalid_expression",
                "message": f"expression is invalid — {summary}"[:500],
                "field_errors": parsed.error_fields,
            },
        }


class _ParsedCron:
    """Internal parse result: field sets, star flags or field errors.

    Attributes:
        error_fields: Per-field error entries when parsing failed.
        macro: The ``@`` macro token when one was used.
        expanded: The five-field expansion of the macro.
        sets: A 5-tuple of allowed values (minute, hour, dom, month,
            dow).
        stars: A 5-tuple of booleans — True when the field text was
            the literal ``*`` (drives the cron day OR semantics).
    """

    __slots__ = ("error_fields", "macro", "expanded", "sets", "stars")

    def __init__(
        self,
        error_fields: List[Dict[str, str]],
        expanded: Optional[str],
        sets: Tuple[FrozenSet[int], ...] = (),
        stars: Tuple[bool, ...] = (),
    ) -> None:
        self.error_fields = error_fields
        self.macro: Optional[str] = None
        self.expanded = None
        self.sets = sets
        self.stars = stars
