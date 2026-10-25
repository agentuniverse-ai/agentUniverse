#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: cron_humanizer_tool.py

"""Natural-language description tool for cron expressions (stdlib only).

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the readability layer of the cron tool family:
``CronExpressionTool`` parses, validates and projects schedules, while
this tool *renders* them as human-readable sentences for config review
UIs, audit logs and agent-facing explanations — in English or natural
Chinese, at three levels of detail, with smell warnings for schedules
that surprise people.

The grammar implemented here is intentionally identical to the
``CronExpressionTool`` family rules, kept standalone (no import of the
sibling module, which may not be present on every branch revision):

* standard five-field Vixie-style cron — ``minute`` (0-59), ``hour``
  (0-23), ``day of month`` (1-31), ``month`` (1-12), ``day of week``
  (0-7, where both 0 and 7 mean Sunday);
* per-field atoms: ``*``, a single value, a range ``a-b``, any
  comma-separated list of those; steps ``/n`` as ``*/n`` (whole
  field), ``a-b/n`` (stepped range) and ``a/n`` (from ``a`` to the
  end of the field, stepped);
* month names ``jan``-``dec`` and day names ``sun``-``sat``
  (case-insensitive), also inside ranges such as ``mon-fri``;
* macros ``@daily`` (also ``@midnight``), ``@hourly``, ``@weekly``,
  ``@monthly`` and ``@yearly`` (also ``@annually``);
* standard day-of-month / day-of-week OR semantics: when *both*
  fields are restricted (neither is the literal ``*``), a day matches
  when *either* field matches.

Two modes:

* ``describe`` — render the whole expression as one sentence.
  ``style='full'`` (default) yields "At minute 30 of every hour",
  ``style='short'`` the compact "Hourly at :30" and
  ``style='verbose'`` the full sentence plus a parenthesised
  per-field raw annotation.  ``locale='en'`` (default) or ``'zh'``
  renders natural phrasing (``每小时的第30分钟``).  The result also
  carries ``warnings`` — smell notices for schedules that are valid
  cron but probably not what the author meant: day-of-month values
  that never occur in the restricted (or any) months, the DOM/DOW
  OR quirk, redundant ``/1`` steps and steps wider than the field
  span.
* ``describe_fields`` — a per-field ``{field, raw, description}``
  breakdown of the same parse, in the requested locale.

Malformed *parameters* (unknown mode/locale/style, non-string or
oversized expression) raise a ``ValueError`` before any computation,
mirroring the other common tools.  An *invalid expression* is never
described — it returns a structured ``error`` payload with precise
per-field messages so an agent can react without catching exceptions.
"""

from typing import Any, ClassVar, Dict, FrozenSet, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Cron day-of-week numbering: 0 (and 7) = Sunday ... 6 = Saturday.
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
DOW_ABBREVIATIONS: Dict[int, str] = {
    0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat",
}
MONTH_ZH_NAMES: Dict[int, str] = {m: f"{m}月" for m in range(1, 13)}
DOW_ZH_NAMES: Dict[int, str] = {
    0: "周日", 1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五", 6: "周六",
}
# Locale-display names for the five cron fields (warning messages).
FIELD_ZH_NAMES: Dict[str, str] = {
    "minute": "分钟", "hour": "小时", "day-of-month": "日",
    "month": "月", "day-of-week": "周",
}
# Longest month of each month number (February counts 29: its leap-year
# best case, so '0 0 29 2 *' warns as leap-year-only, not never-firing).
MONTH_MAX_DAYS: Dict[int, int] = {
    1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30,
    10: 31, 11: 30, 12: 31,
}

FIELD_SPECS: Tuple[Dict[str, Any], ...] = (
    {"name": "minute", "low": 0, "high": 59, "names": None},
    {"name": "hour", "low": 0, "high": 23, "names": None},
    {"name": "day-of-month", "low": 1, "high": 31, "names": None},
    {"name": "month", "low": 1, "high": 12, "names": MONTH_NAMES},
    {"name": "day-of-week", "low": 0, "high": 7, "names": DOW_NAMES},
)


class CronHumanizerTool(Tool):
    """Render cron expressions as natural-language descriptions.

    The readability companion of the ``CronExpressionTool`` family:
    the same standalone grammar (five fields, lists, ranges, steps,
    month/day names, 0 and 7 both Sunday, ``@`` macros, DOM/DOW OR
    semantics), but instead of validating or projecting it *explains*
    — one sentence per expression in English or Chinese, three styles
    (short / full / verbose), a per-field breakdown and warnings for
    valid-but-smelly schedules.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "cron_humanizer_tool"
    description: str = (
        "Cron humanizer tool — renders cron expressions as natural-"
        "language descriptions, pure Python stdlib, no network. Parses "
        "standard five-field cron (minute hour day-of-month month "
        "day-of-week) with '*', lists, ranges, steps, month/day names "
        "and @macros using the CronExpressionTool family grammar. "
        "mode='describe' renders one sentence (locale en|zh, style "
        "short|full|verbose) plus warnings for smells such as a day 31 "
        "that never occurs in the restricted months, the day-of-month/"
        "day-of-week OR quirk, redundant */1 steps and steps wider "
        "than the field span; mode='describe_fields' returns a "
        "per-field {field, raw, description} breakdown. Invalid "
        "expressions are never described — they return a structured "
        "error payload."
    )

    MODES: ClassVar[tuple] = ("describe", "describe_fields")
    LOCALES: ClassVar[Tuple[str, ...]] = ("en", "zh")
    STYLES: ClassVar[Tuple[str, ...]] = ("short", "full", "verbose")
    # Same expansions as the family tool (crontab(5)).
    MACROS: ClassVar[Dict[str, str]] = {
        "@yearly": "0 0 1 1 *",
        "@annually": "0 0 1 1 *",
        "@monthly": "0 0 1 * *",
        "@weekly": "0 0 * * 0",
        "@daily": "0 0 * * *",
        "@midnight": "0 0 * * *",
        "@hourly": "0 * * * *",
    }
    MAX_EXPRESSION_LENGTH: ClassVar[int] = 200

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        expression: Any = None,
        locale: Any = None,
        style: Any = None,
    ) -> Dict[str, Any]:
        """Render one cron expression for humans.

        Args:
            mode (str): ``describe`` (one sentence) or
                ``describe_fields`` (per-field breakdown).
            expression (str): The cron expression — five
                whitespace-separated fields or one supported ``@``
                macro. Required.
            locale (str): ``en`` (default) or ``zh`` — the language
                of the rendered text, field descriptions and warning
                messages. Case-insensitive.
            style (str): ``describe`` mode only — ``full`` (default,
                "At minute 30 of every hour"), ``short`` ("Hourly at
                :30") or ``verbose`` (full plus a parenthesised
                per-field raw annotation). Ignored by
                ``describe_fields``. Case-insensitive.

        Returns:
            Dict[str, Any]: ``describe`` returns ``text``, ``style``,
                ``locale`` and ``warnings``; ``describe_fields``
                returns ``fields`` (a list of ``{field, raw,
                description}``) and ``warnings``. Both carry the
                original ``expression`` and, for macros, the ``macro``
                and its five-field ``expanded`` form. An invalid
                expression is never described — a structured
                ``error`` payload with per-field ``field_errors`` is
                returned instead.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_locale = self._validate_locale(locale)
        clean_style = self._validate_style(style)
        clean_expression = self._validate_expression(expression)

        parsed = self._parse(clean_expression)
        if parsed.error_fields:
            return self._expression_error(mode, clean_expression, parsed)
        warnings = self._warnings(parsed, clean_locale)
        base: Dict[str, Any] = {
            "mode": mode,
            "expression": clean_expression,
        }
        if parsed.macro:
            base["macro"] = parsed.macro
            base["expanded"] = parsed.expanded
        if mode == "describe":
            return {
                **base,
                "text": self._render_describe(
                    parsed, clean_locale, clean_style
                ),
                "style": clean_style,
                "locale": clean_locale,
                "warnings": warnings,
            }
        return {
            **base,
            "locale": clean_locale,
            "fields": self._render_fields(parsed, clean_locale),
            "warnings": warnings,
        }

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"cron_humanizer_tool: {message}")

    @classmethod
    def _validate_locale(cls, locale: Any) -> str:
        """Validate the ``locale`` parameter (default ``en``)."""
        if locale is None:
            return "en"
        if isinstance(locale, bool) or not isinstance(locale, str):
            cls._invalid(
                f"locale must be one of: {', '.join(cls.LOCALES)} "
                f"(got {locale!r})"
            )
        cleaned = locale.strip().lower()
        if cleaned not in cls.LOCALES:
            cls._invalid(
                f"locale must be one of: {', '.join(cls.LOCALES)} "
                f"(got {locale!r})"
            )
        return cleaned

    @classmethod
    def _validate_style(cls, style: Any) -> str:
        """Validate the ``style`` parameter (default ``full``)."""
        if style is None:
            return "full"
        if isinstance(style, bool) or not isinstance(style, str):
            cls._invalid(
                f"style must be one of: {', '.join(cls.STYLES)} "
                f"(got {style!r})"
            )
        cleaned = style.strip().lower()
        if cleaned not in cls.STYLES:
            cls._invalid(
                f"style must be one of: {', '.join(cls.STYLES)} "
                f"(got {style!r})"
            )
        return cleaned

    @classmethod
    def _validate_expression(cls, expression: Any) -> str:
        """Validate the ``expression`` parameter (type-level checks)."""
        if (
            expression is None
            or isinstance(expression, bool)
            or not isinstance(expression, str)
        ):
            cls._invalid(
                f"expression must be a non-empty cron string "
                f"(got {expression!r})"
            )
        expression = expression.strip()
        if not expression:
            cls._invalid("expression must be a non-empty cron string (got '')")
        if len(expression) > cls.MAX_EXPRESSION_LENGTH:
            cls._invalid(
                f"expression exceeds the {cls.MAX_EXPRESSION_LENGTH}-character "
                f"limit (got {len(expression)} characters)"
            )
        return expression

    # ------------------------------------------------------------------ #
    # Expression parsing (CronExpressionTool family grammar)
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse(cls, expression: str) -> "_HumanizedCron":
        """Parse the expression, collecting per-field content errors."""
        errors: List[Dict[str, str]] = []
        tokens = expression.split()
        if tokens[0].startswith("@"):
            if len(tokens) != 1:
                errors.append({
                    "field": "macro",
                    "message": (
                        "a macro must be a single token such as @daily, "
                        f"got {len(tokens)} tokens"
                    ),
                })
                return _HumanizedCron(errors, None)
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
                return _HumanizedCron(errors, None)
            expanded = cls.MACROS[macro]
            parsed = cls._parse_fields(expanded.split(), errors)
            parsed.macro = macro
            parsed.expanded = expanded
            return parsed
        return cls._parse_fields(tokens, errors)

    @classmethod
    def _parse_fields(
        cls, tokens: List[str], errors: List[Dict[str, str]]
    ) -> "_HumanizedCron":
        """Parse the five field tokens (no macro handling)."""
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
            return _HumanizedCron(errors, None)
        fields: List[_FieldParse] = []
        for token, spec in zip(tokens, FIELD_SPECS):
            field = cls._parse_field(token, spec)
            if field.error:
                errors.append({"field": spec["name"], "message": field.error})
            else:
                fields.append(field)
        if errors:
            return _HumanizedCron(errors, None)
        return _HumanizedCron([], None, fields=tuple(fields))

    @classmethod
    def _parse_field(cls, token: str, spec: Dict[str, Any]) -> "_FieldParse":
        """Parse one field token into values plus step atoms."""
        name, low, high, names = (
            spec["name"], spec["low"], spec["high"], spec["names"]
        )
        values: set = set()
        atoms: List[Dict[str, Any]] = []
        for part in token.split(","):
            if not part:
                return _FieldParse.failed(
                    name, token,
                    f"the {name} field contains an empty list element; "
                    f"use single values without stray commas "
                    f"(got {token[:64]!r})",
                )
            atom, error = cls._parse_part(part, name, low, high, names)
            if error:
                return _FieldParse.failed(name, token, error)
            atoms.append(atom)
            values.update(range(atom["start"], atom["end"] + 1, atom["step"]))
        # Day-of-week: both 0 and 7 mean Sunday (family rule).
        if name == "day-of-week" and 7 in values:
            values.discard(7)
            values.add(_CRON_SUNDAY)
        return _FieldParse(
            name=name,
            raw=token,
            values=frozenset(values),
            is_star=token == "*",
            atoms=tuple(atoms),
        )

    @classmethod
    def _parse_part(
        cls,
        part: str,
        name: str,
        low: int,
        high: int,
        names: Optional[Dict[str, int]],
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """Parse one comma-separated atom into a start/end/step triple."""
        step = 1
        explicit_step = False
        base = part
        if "/" in part:
            base, _, step_text = part.partition("/")
            explicit_step = True
            if not step_text:
                return {}, (
                    f"the {name} field has a '/' with no step value "
                    f"(got {part[:64]!r})"
                )
            if not (step_text.isascii() and step_text.isdigit()):
                return {}, (
                    f"the {name} field step must be a positive integer "
                    f"(got {step_text[:64]!r})"
                )
            step = int(step_text)
            if step < 1:
                return {}, (
                    f"the {name} field step must be a positive integer, "
                    f"not {step}"
                )

        if base == "*":
            start, end = low, high
            kind = "star" if not explicit_step else "star_step"
        elif "-" in base:
            start_text, _, end_text = base.partition("-")
            start, error = cls._parse_value(start_text, name, low, high, names)
            if error:
                return {}, error
            end, error = cls._parse_value(end_text, name, low, high, names)
            if error:
                return {}, error
            if start > end:
                return {}, (
                    f"the {name} field range start {start_text[:64]} is "
                    f"greater than the range end {end_text[:64]}"
                )
            kind = "range" if not explicit_step else "range_step"
        else:
            value, error = cls._parse_value(base, name, low, high, names)
            if error:
                return {}, error
            if explicit_step:
                # 'a/n' — from a to the end of the field, stepped.
                start, end = value, high
                kind = "value_step"
            else:
                start, end = value, value
                kind = "value"
        return {
            "kind": kind,
            "part": part,
            "start": start,
            "end": end,
            "step": step,
            "explicit_step": explicit_step,
        }, None

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
    # describe mode — sentence rendering
    # ------------------------------------------------------------------ #

    @classmethod
    def _render_describe(
        cls, parsed: "_HumanizedCron", locale: str, style: str
    ) -> str:
        """Render the whole expression in the requested style."""
        if style == "short":
            return cls._compose_short(parsed, locale)
        if locale == "zh":
            text = cls._compose_zh(parsed)
            annotation = cls._verbose_annotation_zh(parsed)
        else:
            text = cls._compose_en(parsed)
            annotation = cls._verbose_annotation_en(parsed)
        if style == "verbose":
            return f"{text} {annotation}"
        return text

    # ---- full style, English ---------------------------------------- #

    @classmethod
    def _compose_en(cls, parsed: "_HumanizedCron") -> str:
        """Assemble the full-style English sentence."""
        minutes, hours, dom, months, dow = parsed.fields
        time_txt = cls._en_time(minutes, hours)
        day_txt = "" if (dom.is_star and dow.is_star) else cls._en_days(
            dom, dow
        )
        month_txt = "" if months.is_star else "in " + cls._en_months(months)
        return " ".join(p for p in (time_txt, day_txt, month_txt) if p)

    @classmethod
    def _en_time(
        cls, minutes: "_FieldParse", hours: "_FieldParse"
    ) -> str:
        """Render the minute/hour part (full style, English)."""
        if minutes.is_star and hours.is_star:
            return "Every minute"
        shape = cls._shape_of(minutes)
        if hours.is_star:
            if shape["kind"] == "single":
                return f"At minute {shape['start']} of every hour"
            if shape["kind"] == "contiguous":
                return (
                    f"At minutes {shape['start']} through {shape['end']} "
                    "past every hour"
                )
            if shape["kind"] == "star_step":
                return f"Every {shape['step']} minutes"
            if shape["kind"] == "value_step":
                return (
                    f"Every {shape['step']} minutes starting at minute "
                    f"{shape['start']}"
                )
            if shape["kind"] == "range_step":
                return (
                    f"Every {shape['step']} minutes from minute "
                    f"{shape['start']} to minute {shape['end']}"
                )
            return (
                "At minutes "
                + cls._join_en([str(m) for m in sorted(minutes.values)])
                + " past every hour"
            )
        hours_txt = cls._en_hours_desc(hours)
        if minutes.is_star:
            return f"Every minute during {hours_txt}"
        kind, start, end, step = (
            shape["kind"], shape["start"], shape["end"], shape["step"]
        )
        if kind == "star_step":
            return f"Every {step} minutes during {hours_txt}"
        if kind == "value_step":
            return (
                f"Every {step} minutes starting at minute {start} "
                f"during {hours_txt}"
            )
        if kind == "range_step":
            return (
                f"Every {step} minutes from minute {start} to minute "
                f"{end} during {hours_txt}"
            )
        if kind == "single":
            only = start
            if len(hours.values) <= 6:
                times = [f"{h:02d}:{only:02d}" for h in sorted(hours.values)]
                return "At " + cls._join_en(times)
            return f"At minute {only} past {hours_txt}"
        if kind == "contiguous":
            return f"During minutes {start} through {end} of {hours_txt}"
        if len(hours.values) * len(minutes.values) <= 6:
            times = [
                f"{h:02d}:{m:02d}"
                for h in sorted(hours.values)
                for m in sorted(minutes.values)
            ]
            return "At " + cls._join_en(times)
        return (
            "At minutes "
            + cls._join_en([str(m) for m in sorted(minutes.values)])
            + f" past {hours_txt}"
        )

    @classmethod
    def _en_hours_desc(cls, hours: "_FieldParse") -> str:
        """Render restricted hours as hour 9 / hours 9 through 17 / list."""
        ordered = sorted(hours.values)
        if len(ordered) == 1:
            return f"hour {ordered[0]}"
        shape = cls._shape_of(hours)
        if shape["kind"] == "contiguous":
            return f"hours {shape['start']} through {shape['end']}"
        return "hours " + cls._join_en([str(h) for h in ordered])

    @classmethod
    def _en_days(cls, dom: "_FieldParse", dow: "_FieldParse") -> str:
        """Render the day part (full style, English, OR semantics)."""
        dom_txt = "" if dom.is_star else cls._en_dom_desc(dom)
        dow_txt = "" if dow.is_star else cls._en_dow_desc(dow)
        if dom_txt and dow_txt:
            return f"{dom_txt} or {dow_txt} (whichever matches)"
        return dom_txt or dow_txt

    @classmethod
    def _en_dom_desc(cls, dom: "_FieldParse") -> str:
        """Render restricted days of the month (on ...)."""
        ordered = sorted(dom.values)
        if len(ordered) == 1:
            return f"on day {ordered[0]} of the month"
        pieces = cls._run_pieces(ordered)
        return "on days " + cls._join_en(pieces) + " of the month"

    @classmethod
    def _en_dow_desc(cls, dow: "_FieldParse") -> str:
        """Render restricted days of the week by name (on ...)."""
        pieces = cls._run_pieces(sorted(dow.values), cls._dow_name)
        return "on " + cls._join_en(pieces)

    @classmethod
    def _en_months(cls, months: "_FieldParse") -> str:
        """Render restricted months by name."""
        ordered = sorted(months.values)
        if len(ordered) == 1:
            return MONTH_FULL_NAMES[ordered[0]]
        pieces = cls._run_pieces(ordered, cls._month_name)
        return cls._join_en(pieces)

    # ---- full style, Chinese ---------------------------------------- #

    @classmethod
    def _compose_zh(cls, parsed: "_HumanizedCron") -> str:
        """Assemble the full-style Chinese sentence."""
        minutes, hours, dom, months, dow = parsed.fields
        time_txt = cls._zh_time(minutes, hours)
        day_txt = cls._zh_days(dom, dow, months)
        month_txt = "" if months.is_star else cls._zh_months(months)
        # The default 每天 is only spelled out in front of bare clock
        # times; frequency phrases (每15分钟, 从第10分钟起…) already
        # imply every day.
        if day_txt == "每天":
            prefix_day = "每天" if time_txt[0].isdigit() else ""
        else:
            prefix_day = day_txt + "的"
        return month_txt + prefix_day + time_txt

    @classmethod
    def _zh_time(
        cls, minutes: "_FieldParse", hours: "_FieldParse"
    ) -> str:
        """Render the minute/hour part (full style, Chinese)."""
        if minutes.is_star and hours.is_star:
            return "每分钟"
        shape = cls._shape_of(minutes)
        if hours.is_star:
            if shape["kind"] == "single":
                return f"每小时的第{shape['start']}分钟"
            if shape["kind"] == "contiguous":
                return f"每小时的第{shape['start']}到{shape['end']}分钟"
            if shape["kind"] == "star_step":
                return f"每{shape['step']}分钟"
            if shape["kind"] == "value_step":
                return f"从第{shape['start']}分钟起每{shape['step']}分钟"
            if shape["kind"] == "range_step":
                return (
                    f"第{shape['start']}到{shape['end']}分钟内"
                    f"每{shape['step']}分钟"
                )
            return (
                "每小时的第"
                + cls._join_zh([str(m) for m in sorted(minutes.values)])
                + "分钟"
            )
        hours_txt = cls._zh_hours_desc(hours)
        if minutes.is_star:
            return f"{hours_txt}的每分钟"
        kind, start, end, step = (
            shape["kind"], shape["start"], shape["end"], shape["step"]
        )
        if kind == "star_step":
            return f"{hours_txt}内每{step}分钟"
        if kind == "value_step":
            return f"{hours_txt}内从第{start}分钟起每{step}分钟"
        if kind == "range_step":
            return f"{hours_txt}内第{start}到{end}分钟每{step}分钟"
        if kind == "single":
            only = start
            if len(hours.values) <= 6:
                times = [f"{h:02d}:{only:02d}" for h in sorted(hours.values)]
                return cls._join_zh(times)
            return f"{hours_txt}的第{only}分钟"
        if kind == "contiguous":
            return f"{hours_txt}的第{start}到{end}分钟"
        if len(hours.values) * len(minutes.values) <= 6:
            times = [
                f"{h:02d}:{m:02d}"
                for h in sorted(hours.values)
                for m in sorted(minutes.values)
            ]
            return cls._join_zh(times)
        return (
            hours_txt
            + "的第"
            + cls._join_zh([str(m) for m in sorted(minutes.values)])
            + "分钟"
        )

    @classmethod
    def _zh_hours_desc(cls, hours: "_FieldParse") -> str:
        """Render restricted hours as 9点 / 9点至17点 / a list."""
        ordered = sorted(hours.values)
        if len(ordered) == 1:
            return f"{ordered[0]}点"
        shape = cls._shape_of(hours)
        if shape["kind"] == "contiguous":
            return f"{shape['start']}点至{shape['end']}点"
        return cls._join_zh([f"{h}点" for h in ordered])

    @classmethod
    def _zh_days(
        cls, dom: "_FieldParse", dow: "_FieldParse", months: "_FieldParse"
    ) -> str:
        """Render the day part (full style, Chinese, OR semantics)."""
        prefix = "每月" if months.is_star else ""
        dom_txt = "" if dom.is_star else cls._zh_dom_desc(dom, prefix)
        dow_txt = "" if dow.is_star else cls._zh_dow_desc(dow)
        if dom_txt and dow_txt:
            return f"{dom_txt}或{dow_txt}（任一匹配）"
        return dom_txt or dow_txt or "每天"

    @classmethod
    def _zh_dom_desc(cls, dom: "_FieldParse", prefix: str) -> str:
        """Render restricted days of the month (每月 prefix unless the
        month field already restricts the context)."""
        ordered = sorted(dom.values)
        if len(ordered) == 1:
            return f"{prefix}{ordered[0]}日"
        pieces: List[str] = []
        for start, end in cls._runs(ordered):
            if end - start >= 2:
                pieces.append(f"{start}到{end}日")
            else:
                pieces.extend(f"{d}日" for d in range(start, end + 1))
        return prefix + cls._join_zh(pieces)

    @classmethod
    def _zh_dow_desc(cls, dow: "_FieldParse") -> str:
        """Render restricted days of the week as 每周..."""
        pieces: List[str] = []
        for start, end in cls._runs(sorted(dow.values)):
            if end - start >= 2:
                pieces.append(
                    f"{DOW_ZH_NAMES[start]}至{DOW_ZH_NAMES[end]}"
                )
            else:
                pieces.extend(DOW_ZH_NAMES[d] for d in range(start, end + 1))
        joined = cls._join_zh(pieces)
        # Every piece starts with 周 — drop the duplicated radical so
        # '每周' + '周一至周五' renders 每周一至周五, not 每周周一至周五.
        if joined.startswith("周"):
            joined = joined[1:]
        return "每周" + joined

    @classmethod
    def _zh_months(cls, months: "_FieldParse") -> str:
        """Render restricted months as 1月 / 1月至3月 / list."""
        ordered = sorted(months.values)
        if len(ordered) == 1:
            return f"{ordered[0]}月"
        shape = cls._shape_of(months)
        if shape["kind"] == "contiguous":
            return f"{shape['start']}月至{shape['end']}月"
        return cls._join_zh([f"{m}月" for m in ordered])

    # ---- short style ------------------------------------------------- #

    @classmethod
    def _compose_short(cls, parsed: "_HumanizedCron", locale: str) -> str:
        """Assemble the compact short-style sentence (month, day, time)."""
        minutes, hours, dom, months, dow = parsed.fields
        if locale == "zh":
            time_txt = cls._zh_time_short(minutes, hours)
            day_txt = cls._zh_days_short(dom, dow)
            month_txt = "" if months.is_star else cls._zh_months_short(months)
            if dom.values == {1} and dow.is_star and months.is_star:
                day_txt, month_txt = "每月", ""
            elif (
                dom.values == {1} and dow.is_star and months.values == {1}
            ):
                day_txt, month_txt = "每年", ""
            if not day_txt and not month_txt:
                if time_txt[0].isdigit():
                    return "每天" + time_txt
                return time_txt
            return month_txt + day_txt + time_txt
        time_txt = cls._en_time_short(minutes, hours)
        day_txt = cls._en_days_short(dom, dow)
        month_txt = "" if months.is_star else cls._en_months_short(months)
        if dom.values == {1} and dow.is_star and months.is_star:
            day_txt, month_txt = "Monthly", ""
        elif dom.values == {1} and dow.is_star and months.values == {1}:
            day_txt, month_txt = "Yearly", ""
        segs = [s for s in (month_txt, day_txt, time_txt) if s]
        if not day_txt and not month_txt and time_txt.startswith("at "):
            return "Daily " + time_txt
        return " ".join(segs)

    @classmethod
    def _en_time_short(
        cls, minutes: "_FieldParse", hours: "_FieldParse"
    ) -> str:
        """Compact time rendering (short style, English)."""
        if minutes.is_star and hours.is_star:
            return "Every minute"
        shape = cls._shape_of(minutes)
        mm = [f":{m:02d}" for m in sorted(minutes.values)]
        if hours.is_star:
            if shape["kind"] == "single":
                return f"Hourly at {mm[0]}"
            if shape["kind"] == "contiguous":
                return (
                    f"Hourly at :{shape['start']:02d}-:{shape['end']:02d}"
                )
            if shape["kind"] == "star_step":
                return f"Every {shape['step']} min"
            if shape["kind"] == "value_step":
                return f"Every {shape['step']} min from {mm[0]}"
            if shape["kind"] == "range_step":
                return (
                    f"Every {shape['step']} min from :{shape['start']:02d} "
                    f"to :{shape['end']:02d}"
                )
            return f"Hourly at {cls._join_en(mm)}"
        hours_txt = cls._en_hours_compact(hours)
        if minutes.is_star:
            return f"Every minute in hours {hours_txt}"
        kind, start, end, step = (
            shape["kind"], shape["start"], shape["end"], shape["step"]
        )
        if kind == "star_step":
            return f"Every {step} min in hours {hours_txt}"
        if kind == "value_step":
            return f"Every {step} min from :{start:02d} in hours {hours_txt}"
        if kind == "range_step":
            return (
                f"Every {step} min from :{start:02d} to :{end:02d} "
                f"in hours {hours_txt}"
            )
        if kind == "single":
            only = start
            if len(hours.values) <= 6:
                times = [f"{h:02d}:{only:02d}" for h in sorted(hours.values)]
                return "at " + cls._join_en(times)
            return f":{only:02d} in hours {hours_txt}"
        if kind == "contiguous":
            return f":{start:02d}-:{end:02d} in hours {hours_txt}"
        if len(hours.values) * len(minutes.values) <= 6:
            times = [
                f"{h:02d}:{m:02d}"
                for h in sorted(hours.values)
                for m in sorted(minutes.values)
            ]
            return "at " + cls._join_en(times)
        return f"{cls._join_en(mm)} in hours {hours_txt}"

    @classmethod
    def _en_hours_compact(cls, hours: "_FieldParse") -> str:
        """Compact restricted-hours rendering: 9 / 9-17 / 9,12,15."""
        ordered = sorted(hours.values)
        if len(ordered) == 1:
            return str(ordered[0])
        shape = cls._shape_of(hours)
        if shape["kind"] == "contiguous":
            return f"{shape['start']}-{shape['end']}"
        return ",".join(str(h) for h in ordered)

    @classmethod
    def _en_days_short(cls, dom: "_FieldParse", dow: "_FieldParse") -> str:
        """Compact day rendering (short style, English)."""
        dom_txt = "" if dom.is_star else cls._en_dom_short(dom)
        dow_txt = "" if dow.is_star else cls._en_dow_short(dow)
        if dom_txt and dow_txt:
            return f"{dom_txt} or {dow_txt}"
        return dom_txt or dow_txt

    @classmethod
    def _en_dom_short(cls, dom: "_FieldParse") -> str:
        """Compact days of the month: day 1 / days 1-5 / days 2,15."""
        ordered = sorted(dom.values)
        if len(ordered) == 1:
            return f"day {ordered[0]}"
        shape = cls._shape_of(dom)
        if shape["kind"] == "contiguous":
            return f"days {shape['start']}-{shape['end']}"
        return "days " + ",".join(str(d) for d in ordered)

    @classmethod
    def _en_dow_short(cls, dow: "_FieldParse") -> str:
        """Compact days of the week: Sundays / Weekdays / Mon-Fri / Mon/Wed."""
        if dow.values == {1, 2, 3, 4, 5}:
            return "Weekdays"
        if dow.values == {0, 6}:
            return "Weekends"
        ordered = sorted(dow.values)
        if len(ordered) == 1:
            return f"{DOW_FULL_NAMES[ordered[0]]}s"
        shape = cls._shape_of(dow)
        if shape["kind"] == "contiguous":
            start, end = shape["start"], shape["end"]
            return f"{DOW_ABBREVIATIONS[start]}-{DOW_ABBREVIATIONS[end]}"
        return "/".join(DOW_ABBREVIATIONS[d] for d in ordered)

    @classmethod
    def _en_months_short(cls, months: "_FieldParse") -> str:
        """Compact months: Jan / Jan-Mar / Jan,Jun,Jul."""
        ordered = sorted(months.values)
        if len(ordered) == 1:
            return MONTH_FULL_NAMES[ordered[0]][:3]
        shape = cls._shape_of(months)
        if shape["kind"] == "contiguous":
            return (
                f"{MONTH_FULL_NAMES[shape['start']][:3]}-"
                f"{MONTH_FULL_NAMES[shape['end']][:3]}"
            )
        return ",".join(MONTH_FULL_NAMES[m][:3] for m in ordered)

    @classmethod
    def _zh_time_short(
        cls, minutes: "_FieldParse", hours: "_FieldParse"
    ) -> str:
        """Compact time rendering (short style, Chinese)."""
        if minutes.is_star and hours.is_star:
            return "每分钟"
        shape = cls._shape_of(minutes)
        mm = [f":{m:02d}" for m in sorted(minutes.values)]
        if hours.is_star:
            if shape["kind"] == "single":
                return f"每小时 {mm[0]}"
            if shape["kind"] == "contiguous":
                return f"每小时 :{shape['start']:02d}-:{shape['end']:02d}"
            if shape["kind"] == "star_step":
                return f"每{shape['step']}分钟"
            if shape["kind"] == "value_step":
                return f"从{mm[0]}起每{shape['step']}分钟"
            if shape["kind"] == "range_step":
                return (
                    f"从:{shape['start']:02d}到:{shape['end']:02d}"
                    f"每{shape['step']}分钟"
                )
            return f"每小时 {cls._join_zh(mm)}"
        hours_txt = cls._zh_hours_compact(hours)
        if minutes.is_star:
            return f"{hours_txt}每分钟"
        kind, start, end, step = (
            shape["kind"], shape["start"], shape["end"], shape["step"]
        )
        if kind == "star_step":
            return f"{hours_txt}每{step}分钟"
        if kind == "value_step":
            return f"{hours_txt}从:{start:02d}起每{step}分钟"
        if kind == "range_step":
            return (
                f"{hours_txt}的:{start:02d}-:{end:02d}每{step}分钟"
            )
        if kind == "single":
            only = start
            if len(hours.values) <= 6:
                times = [f"{h:02d}:{only:02d}" for h in sorted(hours.values)]
                return cls._join_zh(times)
            return f"{hours_txt}的:{only:02d}"
        if kind == "contiguous":
            return f"{hours_txt}的:{start:02d}-:{end:02d}"
        if len(hours.values) * len(minutes.values) <= 6:
            times = [
                f"{h:02d}:{m:02d}"
                for h in sorted(hours.values)
                for m in sorted(minutes.values)
            ]
            return cls._join_zh(times)
        return f"{hours_txt}的{cls._join_zh(mm)}"

    @classmethod
    def _zh_hours_compact(cls, hours: "_FieldParse") -> str:
        """Compact restricted-hours rendering: 9点 / 9-17点 / 9点、12点."""
        ordered = sorted(hours.values)
        if len(ordered) == 1:
            return f"{ordered[0]}点"
        shape = cls._shape_of(hours)
        if shape["kind"] == "contiguous":
            return f"{shape['start']}-{shape['end']}点"
        return cls._join_zh([f"{h}点" for h in ordered])

    @classmethod
    def _zh_days_short(cls, dom: "_FieldParse", dow: "_FieldParse") -> str:
        """Compact day rendering (short style, Chinese)."""
        dom_txt = "" if dom.is_star else cls._zh_dom_short(dom)
        dow_txt = "" if dow.is_star else cls._zh_dow_short(dow)
        if dom_txt and dow_txt:
            return f"{dom_txt}或{dow_txt}"
        return dom_txt or dow_txt

    @classmethod
    def _zh_dom_short(cls, dom: "_FieldParse") -> str:
        """Compact days of the month: 1日 / 1-5日 / 1日、15日."""
        ordered = sorted(dom.values)
        if len(ordered) == 1:
            return f"{ordered[0]}日"
        shape = cls._shape_of(dom)
        if shape["kind"] == "contiguous":
            return f"{shape['start']}-{shape['end']}日"
        return cls._join_zh([f"{d}日" for d in ordered])

    @classmethod
    def _zh_dow_short(cls, dow: "_FieldParse") -> str:
        """Compact weekdays: 工作日 / 周末 / 每周一 / 周一至周五 / list."""
        if dow.values == {1, 2, 3, 4, 5}:
            return "工作日"
        if dow.values == {0, 6}:
            return "周末"
        ordered = sorted(dow.values)
        if len(ordered) == 1:
            return f"每周{DOW_ZH_NAMES[ordered[0]][1:]}"
        shape = cls._shape_of(dow)
        if shape["kind"] == "contiguous":
            start, end = shape["start"], shape["end"]
            return f"{DOW_ZH_NAMES[start]}至{DOW_ZH_NAMES[end]}"
        return cls._join_zh([DOW_ZH_NAMES[d] for d in ordered])

    @classmethod
    def _zh_months_short(cls, months: "_FieldParse") -> str:
        """Compact months: 1月 / 1-3月 / 1月、6月."""
        ordered = sorted(months.values)
        if len(ordered) == 1:
            return f"{ordered[0]}月"
        shape = cls._shape_of(months)
        if shape["kind"] == "contiguous":
            return f"{shape['start']}-{shape['end']}月"
        return cls._join_zh([f"{m}月" for m in ordered])

    # ---- verbose annotations ---------------------------------------- #

    @classmethod
    def _verbose_annotation_en(cls, parsed: "_HumanizedCron") -> str:
        """Parenthesised per-field raw annotation (English labels)."""
        fields = "; ".join(
            f"{field.name}: {field.raw}" for field in parsed.fields
        )
        if parsed.macro:
            return f"({parsed.macro} = {fields})"
        return f"({fields})"

    @classmethod
    def _verbose_annotation_zh(cls, parsed: "_HumanizedCron") -> str:
        """Parenthesised per-field raw annotation (Chinese labels)."""
        labels = ("分", "时", "日", "月", "周")
        fields = "；".join(
            f"{label}: {field.raw}"
            for label, field in zip(labels, parsed.fields)
        )
        if parsed.macro:
            return f"（{parsed.macro} 展开为 {fields}）"
        return f"（{fields}）"

    # ------------------------------------------------------------------ #
    # describe_fields mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _render_fields(
        cls, parsed: "_HumanizedCron", locale: str
    ) -> List[Dict[str, str]]:
        """Per-field {field, raw, description} in the given locale."""
        renderers = (
            cls._field_renderers_zh() if locale == "zh"
            else cls._field_renderers_en()
        )
        return [
            {
                "field": field.name,
                "raw": field.raw,
                "description": renderers[field.name](field),
            }
            for field in parsed.fields
        ]

    @classmethod
    def _field_renderers_en(cls) -> Dict[str, Any]:
        """Per-field description builders, English."""
        def render_minute(field: "_FieldParse") -> str:
            if field.is_star:
                return "every minute"
            return cls._describe_value_set(
                field,
                render_value=str,
                single=lambda v: f"at minute {v}",
                contiguous=lambda a, b: f"at minutes {a} through {b}",
                star_step=lambda s, vals: f"every {s} minutes ({vals})",
                value_step=lambda a, s, vals: (
                    f"every {s} minutes starting at {a} ({vals})"
                ),
                range_step=lambda a, b, s, vals: (
                    f"every {s} minutes from {a} to {b} ({vals})"
                ),
                plain=lambda pieces: f"at minutes {pieces}",
            )

        def render_hour(field: "_FieldParse") -> str:
            if field.is_star:
                return "every hour"
            return cls._describe_value_set(
                field,
                render_value=str,
                single=lambda v: f"at hour {v}",
                contiguous=lambda a, b: f"at hours {a} through {b}",
                star_step=lambda s, vals: f"every {s} hours ({vals})",
                value_step=lambda a, s, vals: (
                    f"every {s} hours starting at {a} ({vals})"
                ),
                range_step=lambda a, b, s, vals: (
                    f"every {s} hours from {a} to {b} ({vals})"
                ),
                plain=lambda pieces: f"at hours {pieces}",
            )

        def render_dom(field: "_FieldParse") -> str:
            if field.is_star:
                return "every day of the month"
            return cls._describe_value_set(
                field,
                render_value=str,
                single=lambda v: f"on day {v} of the month",
                contiguous=lambda a, b: (
                    f"on days {a} through {b} of the month"
                ),
                star_step=lambda s, vals: (
                    f"every {s} days of the month ({vals})"
                ),
                value_step=lambda a, s, vals: (
                    f"every {s} days starting on day {a} ({vals})"
                ),
                range_step=lambda a, b, s, vals: (
                    f"every {s} days from day {a} to day {b} ({vals})"
                ),
                plain=lambda pieces: f"on days {pieces} of the month",
            )

        def render_month(field: "_FieldParse") -> str:
            if field.is_star:
                return "every month"
            return cls._describe_value_set(
                field,
                render_value=cls._month_name,
                single=lambda v: f"in {cls._month_name(v)}",
                contiguous=lambda a, b: (
                    f"in {cls._month_name(a)} through {cls._month_name(b)}"
                ),
                star_step=lambda s, vals: f"every {s} months ({vals})",
                value_step=lambda a, s, vals: (
                    f"every {s} months starting in {cls._month_name(a)} "
                    f"({vals})"
                ),
                range_step=lambda a, b, s, vals: (
                    f"every {s} months from {cls._month_name(a)} to "
                    f"{cls._month_name(b)} ({vals})"
                ),
                plain=lambda pieces: f"in {pieces}",
            )

        def render_dow(field: "_FieldParse") -> str:
            if field.is_star:
                return "every day of the week"
            return cls._describe_value_set(
                field,
                render_value=cls._dow_name,
                single=lambda v: f"on {cls._dow_name(v)}",
                contiguous=lambda a, b: (
                    f"on {cls._dow_name(a)} through {cls._dow_name(b)}"
                ),
                star_step=lambda s, vals: (
                    f"every {s} days of the week ({vals})"
                ),
                value_step=lambda a, s, vals: (
                    f"every {s} days of the week starting on "
                    f"{cls._dow_name(a)} ({vals})"
                ),
                range_step=lambda a, b, s, vals: (
                    f"every {s} days of the week from {cls._dow_name(a)} "
                    f"to {cls._dow_name(b)} ({vals})"
                ),
                plain=lambda pieces: f"on {pieces}",
            )

        return {
            "minute": render_minute,
            "hour": render_hour,
            "day-of-month": render_dom,
            "month": render_month,
            "day-of-week": render_dow,
        }

    @classmethod
    def _field_renderers_zh(cls) -> Dict[str, Any]:
        """Per-field description builders, Chinese."""
        def render_minute(field: "_FieldParse") -> str:
            if field.is_star:
                return "每分钟"
            return cls._describe_value_set(
                field,
                render_value=str,
                single=lambda v: f"第{v}分钟",
                contiguous=lambda a, b: f"第{a}到{b}分钟",
                star_step=lambda s, vals: f"每{s}分钟（{vals}）",
                value_step=lambda a, s, vals: (
                    f"从第{a}分钟起每{s}分钟（{vals}）"
                ),
                range_step=lambda a, b, s, vals: (
                    f"第{a}到{b}分钟每{s}分钟（{vals}）"
                ),
                plain=lambda pieces: f"第{pieces}分钟",
                join=cls._join_zh,
            )

        def render_hour(field: "_FieldParse") -> str:
            if field.is_star:
                return "每小时"
            return cls._describe_value_set(
                field,
                render_value=lambda v: f"{v}点",
                single=lambda v: f"{v}点",
                contiguous=lambda a, b: f"{a}点到{b}点",
                star_step=lambda s, vals: f"每{s}小时（{vals}）",
                value_step=lambda a, s, vals: (
                    f"从{a}点起每{s}小时（{vals}）"
                ),
                range_step=lambda a, b, s, vals: (
                    f"{a}点到{b}点每{s}小时（{vals}）"
                ),
                plain=lambda pieces: pieces,
                join=cls._join_zh,
            )

        def render_dom(field: "_FieldParse") -> str:
            if field.is_star:
                return "每天"
            return cls._describe_value_set(
                field,
                render_value=lambda v: f"{v}日",
                single=lambda v: f"{v}日",
                contiguous=lambda a, b: f"{a}到{b}日",
                star_step=lambda s, vals: f"每{s}日（{vals}）",
                value_step=lambda a, s, vals: (
                    f"从{a}日起每{s}日（{vals}）"
                ),
                range_step=lambda a, b, s, vals: (
                    f"{a}到{b}日每{s}日（{vals}）"
                ),
                plain=lambda pieces: pieces,
                join=cls._join_zh,
            )

        def render_month(field: "_FieldParse") -> str:
            if field.is_star:
                return "每月"
            return cls._describe_value_set(
                field,
                render_value=cls._month_name_zh,
                single=lambda v: f"{v}月",
                contiguous=lambda a, b: f"{a}月至{b}月",
                star_step=lambda s, vals: f"每{s}个月（{vals}）",
                value_step=lambda a, s, vals: (
                    f"从{a}月起每{s}个月（{vals}）"
                ),
                range_step=lambda a, b, s, vals: (
                    f"{a}月至{b}月每{s}个月（{vals}）"
                ),
                plain=lambda pieces: pieces,
                join=cls._join_zh,
            )

        def render_dow(field: "_FieldParse") -> str:
            if field.is_star:
                return "每天"
            return cls._describe_value_set(
                field,
                render_value=cls._dow_name_zh,
                single=cls._dow_name_zh,
                contiguous=lambda a, b: (
                    f"{cls._dow_name_zh(a)}至{cls._dow_name_zh(b)}"
                ),
                star_step=lambda s, vals: f"每{s}天（{vals}）",
                value_step=lambda a, s, vals: (
                    f"从{cls._dow_name_zh(a)}起每{s}天（{vals}）"
                ),
                range_step=lambda a, b, s, vals: (
                    f"{cls._dow_name_zh(a)}至{cls._dow_name_zh(b)}"
                    f"每{s}天（{vals}）"
                ),
                plain=lambda pieces: pieces,
                join=cls._join_zh,
            )

        return {
            "minute": render_minute,
            "hour": render_hour,
            "day-of-month": render_dom,
            "month": render_month,
            "day-of-week": render_dow,
        }

    @classmethod
    def _describe_value_set(
        cls,
        field: "_FieldParse",
        render_value: Any,
        single: Any,
        contiguous: Any,
        star_step: Any,
        value_step: Any,
        range_step: Any,
        plain: Any,
        join: Any = None,
    ) -> str:
        """Shape-dispatch a field's value set to a description phrase.

        Uses the parsed atom when the field has exactly one (so
        ``*/15`` / ``10/20`` / ``9-17/2`` keep their written intent)
        and falls back to value-set shaping for mixed lists.  The
        stepped callbacks receive the rendered (bounded) value
        enumeration for the parenthetical expansion.
        """
        join = join or cls._join_en
        values = sorted(field.values)
        rendered = join([render_value(v) for v in values])
        shape = cls._shape_of(field)
        kind = shape["kind"]
        if kind == "single":
            return single(shape["start"])
        if kind == "contiguous":
            return contiguous(shape["start"], shape["end"])
        if kind == "star_step":
            return star_step(shape["step"], rendered)
        if kind == "value_step":
            return value_step(shape["start"], shape["step"], rendered)
        if kind == "range_step":
            return range_step(
                shape["start"], shape["end"], shape["step"], rendered
            )
        return plain(rendered)

    # ------------------------------------------------------------------ #
    # Warnings — valid cron that probably is not what the author meant
    # ------------------------------------------------------------------ #

    @classmethod
    def _warnings(
        cls, parsed: "_HumanizedCron", locale: str
    ) -> List[Dict[str, Any]]:
        """Detect the four schedule smells, localized per locale."""
        dom_field, month_field, dow_field = (
            parsed.fields[2], parsed.fields[3], parsed.fields[4]
        )
        found: List[Dict[str, Any]] = []

        mismatch = cls._day_month_mismatch(dom_field, month_field, locale)
        if mismatch:
            found.append(mismatch)
        if not dom_field.is_star and not dow_field.is_star:
            found.append(cls._or_quirk_warning(locale))
        for field in parsed.fields:
            for atom in field.atoms:
                if atom["explicit_step"] and atom["step"] == 1:
                    found.append(
                        cls._redundant_step_warning(field, atom, locale)
                    )
                elif (
                    atom["step"] > 1
                    and atom["end"] - atom["start"] < atom["step"]
                ):
                    found.append(
                        cls._step_exceeds_warning(field, atom, locale)
                    )
        return found

    @classmethod
    def _day_month_mismatch(
        cls,
        dom_field: "_FieldParse",
        month_field: "_FieldParse",
        locale: str,
    ) -> Optional[Dict[str, Any]]:
        """Warn when day-of-month values cannot occur in some months."""
        if dom_field.is_star:
            return None
        dom_values = sorted(dom_field.values)
        if month_field.is_star:
            skipped = [
                m for m in range(1, 13)
                if all(d > MONTH_MAX_DAYS[m] for d in dom_values)
            ]
            if not skipped:
                return None
            if locale == "zh":
                message = (
                    f"{cls._join_zh([str(d) for d in dom_values])}日并非"
                    "每个月都存在——该调度会在以下月份静默跳过："
                    + cls._join_zh([MONTH_ZH_NAMES[m] for m in skipped])
                )
            else:
                message = (
                    "day-of-month "
                    + cls._join_en([str(d) for d in dom_values])
                    + " does not exist in every month — the schedule "
                    "silently skips "
                    + cls._join_en([MONTH_FULL_NAMES[m] for m in skipped])
                )
            return {
                "type": "day_month_mismatch",
                "field": None,
                "message": message,
            }
        months = sorted(month_field.values)
        never = all(
            d > MONTH_MAX_DAYS[m] for d in dom_values for m in months
        )
        if never:
            if locale == "zh":
                message = (
                    "受限的月份"
                    + cls._join_zh([MONTH_ZH_NAMES[m] for m in months])
                    + "中不存在"
                    + cls._join_zh([str(d) for d in dom_values])
                    + "日——该调度永远不会触发"
                )
            else:
                message = (
                    "the day-of-month value(s) "
                    + cls._join_en([str(d) for d in dom_values])
                    + " never occur in "
                    + cls._join_en([MONTH_FULL_NAMES[m] for m in months])
                    + " — this schedule can never fire"
                )
            return {
                "type": "day_month_mismatch",
                "field": None,
                "message": message,
            }
        leap_only = months == [2] and set(dom_values) == {29}
        if leap_only:
            message = (
                "2月29日只在闰年存在——该调度仅在闰年触发"
                if locale == "zh"
                else "February 29 only exists in leap years — this "
                "schedule fires only in leap years"
            )
            return {
                "type": "day_month_mismatch",
                "field": None,
                "message": message,
            }
        return None

    @classmethod
    def _or_quirk_warning(cls, locale: str) -> Dict[str, Any]:
        """Warn about the DOM/DOW OR semantics surprise."""
        message = (
            "“日”与“周”两个字段同时受限时，cron 采用“或”语义——任一字段"
            "命中即触发，而非两者同时满足（常被误认为“与”）"
            if locale == "zh"
            else "day-of-month and day-of-week are both restricted, so "
            "standard cron OR semantics apply — the schedule fires when "
            "either field matches, not only when both do (commonly "
            "mistaken for AND)"
        )
        return {
            "type": "dom_dow_or_semantics",
            "field": None,
            "message": message,
        }

    @classmethod
    def _redundant_step_warning(
        cls, field: "_FieldParse", atom: Dict[str, Any], locale: str
    ) -> Dict[str, Any]:
        """Warn about an explicit '/1' step, which changes nothing."""
        part = atom["part"]
        stripped = part[:-2] if part.endswith("/1") else "*"
        message = (
            f"{FIELD_ZH_NAMES[field.name]}字段的“/1”步长是冗余的——"
            f"“{part}”与“{stripped}”等价"
            if locale == "zh"
            else f"the {field.name} field step '/1' is redundant — "
            f"'{part}' matches the same values as '{stripped}'"
        )
        return {
            "type": "redundant_step_one",
            "field": field.name,
            "message": message,
        }

    @classmethod
    def _step_exceeds_warning(
        cls, field: "_FieldParse", atom: Dict[str, Any], locale: str
    ) -> Dict[str, Any]:
        """Warn about a step wider than the atom's usable span."""
        start, end, step = atom["start"], atom["end"], atom["step"]
        message = (
            f"{FIELD_ZH_NAMES[field.name]}字段的步长 {step} 超过"
            f"（{start}-{end}）的跨度——实际只会命中 {start}"
            if locale == "zh"
            else f"the {field.name} field step {step} is wider than the "
            f"span {start}-{end} — only value {start} can ever match"
        )
        return {
            "type": "step_exceeds_range",
            "field": field.name,
            "message": message,
        }

    # ------------------------------------------------------------------ #
    # Shared shaping / naming helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _shape_of(cls, field: "_FieldParse") -> Dict[str, Any]:
        """Classify a field's value shape for the phrasing dispatch.

        Prefers the single written atom's kind (``single``,
        ``contiguous`` for a plain range, ``star_step`` for ``*/n``,
        ``value_step`` for ``a/n``, ``range_step`` for ``a-b/n``) so
        the rendering keeps the author's intent; a value set built
        from a mixed list is shaped from its runs (``single`` /
        ``contiguous`` / ``step`` / ``list``).
        """
        values = field.values
        ordered = sorted(values)
        if len(field.atoms) == 1:
            atom = field.atoms[0]
            kind = atom["kind"]
            if kind == "value":
                return {"kind": "single", "start": atom["start"],
                        "end": atom["end"], "step": 1}
            if kind == "range" or kind == "star":
                return {"kind": "contiguous", "start": atom["start"],
                        "end": atom["end"], "step": 1}
            return {"kind": kind, "start": atom["start"],
                    "end": atom["end"], "step": atom["step"]}
        # Mixed lists: only collapse contiguous runs — never invent a
        # step for values the author wrote out individually (so
        # '1,15' stays a list, not 'every 14 days from 1 to 15').
        shape = cls._step_shape(values)
        if shape is not None and shape[2] == 1:
            start, end, _ = shape
            kind = "single" if start == end else "contiguous"
            return {"kind": kind, "start": start, "end": end, "step": 1}
        return {"kind": "list", "start": ordered[0],
                "end": ordered[-1], "step": 1}

    @staticmethod
    def _step_shape(values: FrozenSet[int]) -> Optional[Tuple[int, int, int]]:
        """Return ``(start, end, step)`` when the set is a single run.

        A set matches when it equals ``range(start, end + 1, step)``
        for ``step >= 1``; a plain contiguous range is ``step == 1``
        and a single value ``(v, v, 1)``.  Returns ``None`` for an
        arbitrary (non-steppable) value set.
        """
        ordered = sorted(values)
        if not ordered:
            return None
        if len(ordered) == 1:
            return ordered[0], ordered[0], 1
        if ordered == list(range(ordered[0], ordered[-1] + 1)):
            return ordered[0], ordered[-1], 1
        step = ordered[1] - ordered[0]
        if step > 1 and ordered == list(
            range(ordered[0], ordered[-1] + 1, step)
        ):
            return ordered[0], ordered[-1], step
        return None

    @staticmethod
    def _run_pieces(values: List[int], render: Any = None) -> List[str]:
        """Describe a sorted value list, compressing runs of 3+.

        Singletons and pairs render as individual pieces; a run of
        three or more renders once as ``start through end`` (rendered
        via ``render`` when given, e.g. weekday or month names).
        """
        pieces: List[str] = []
        for start, end in CronHumanizerTool._runs(values):
            if end - start >= 2:
                if render is not None:
                    pieces.append(f"{render(start)} through {render(end)}")
                else:
                    pieces.append(f"{start} through {end}")
            else:
                for value in range(start, end + 1):
                    pieces.append(
                        str(value) if render is None else render(value)
                    )
        return pieces

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

    @staticmethod
    def _join_en(names: List[str]) -> str:
        """Join names as 'A', 'A and B', 'A, B and C' (bounded)."""
        if len(names) == 1:
            return names[0]
        if len(names) == 2:
            return f"{names[0]} and {names[1]}"
        if len(names) <= 6:
            return ", ".join(names[:-1]) + f" and {names[-1]}"
        head = ", ".join(names[:6])
        return f"{head}, … and {len(names) - 6} more"

    @staticmethod
    def _join_zh(names: List[str]) -> str:
        """Join names as 'A'、'A和B'、'A、B和C' (bounded)."""
        if len(names) == 1:
            return names[0]
        if len(names) == 2:
            return f"{names[0]}和{names[1]}"
        if len(names) <= 6:
            return "、".join(names[:-1]) + f"和{names[-1]}"
        head = "、".join(names[:6])
        return f"{head}……等{len(names)}个"

    @staticmethod
    def _month_name(value: int) -> str:
        """Full English month name."""
        return MONTH_FULL_NAMES[value]

    @staticmethod
    def _month_name_zh(value: int) -> str:
        """Chinese month label (1月..12月)."""
        return MONTH_ZH_NAMES[value]

    @staticmethod
    def _dow_name(value: int) -> str:
        """Full English weekday name (0 = Sunday)."""
        return DOW_FULL_NAMES[value]

    @staticmethod
    def _dow_name_zh(value: int) -> str:
        """Chinese weekday label (0 = 周日)."""
        return DOW_ZH_NAMES[value]

    # ------------------------------------------------------------------ #
    # Error payload (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @classmethod
    def _expression_error(
        cls, mode: str, expression: str, parsed: "_HumanizedCron"
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


class _FieldParse:
    """One parsed cron field: raw token, value set, star flag, atoms.

    Attributes:
        name: Field name from FIELD_SPECS.
        raw: The raw field token as written.
        values: FrozenSet of allowed values (day-of-week 7 folded to 0).
        is_star: True only for the literal ``*`` token (drives the cron
            day OR semantics and the day-part rendering).
        atoms: The parsed comma-separated atoms (kind, part, start,
            end, step), used by the shape dispatch and warnings.
    """

    __slots__ = ("name", "raw", "values", "is_star", "atoms", "error")

    def __init__(
        self,
        name: str,
        raw: str,
        values: FrozenSet[int] = frozenset(),
        is_star: bool = False,
        atoms: Tuple[Dict[str, Any], ...] = (),
        error: Optional[str] = None,
    ) -> None:
        self.name = name
        self.raw = raw
        self.values = values
        self.is_star = is_star
        self.atoms = atoms
        self.error = error

    @classmethod
    def failed(cls, name: str, raw: str, message: str) -> "_FieldParse":
        """Build a failed field parse carrying the error message."""
        return cls(name=name, raw=raw, error=message)


class _HumanizedCron:
    """Internal parse result: five field parses or per-field errors.

    Attributes:
        error_fields: Per-field error entries when parsing failed.
        macro: The ``@`` macro token when one was used.
        expanded: The five-field expansion of the macro.
        fields: A 5-tuple of ``_FieldParse`` (minute, hour,
            day-of-month, month, day-of-week) on success.
    """

    __slots__ = ("error_fields", "macro", "expanded", "fields")

    def __init__(
        self,
        error_fields: List[Dict[str, str]],
        expanded: Optional[str],
        fields: Tuple[_FieldParse, ...] = (),
    ) -> None:
        self.error_fields = error_fields
        self.macro: Optional[str] = None
        self.expanded: Optional[str] = None
        self.fields = fields
