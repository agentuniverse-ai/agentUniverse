"""TinyIsoCalendarTool: iso_week coordinates, 10 dates, 0-day offset, monday weeks (au1k series #20, numeric)."""

import bisect
import datetime
import hashlib
import heapq
import itertools
import json
import math
import re
from datetime import date, timedelta
from typing import Any, ClassVar, Dict, Optional

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool


def au_algo_020(x, p1=20, p2=0, p3=True, p4="iso_week") -> dict:
    """Resolve ISO dates into calendar coordinates and rank them.

    Args:
        x: one ``YYYY-MM-DD`` date, a list of them, or a dict of them.
        p1: Dates considered, bounds [1, 200].
        p2: Day offset applied before analysis, bounds [0, 30].
        p3: When True weeks start on Monday (ISO), else weekday 0 is Sunday.
        p4: Primary coordinate vocabulary, "iso_week", "quarter" or "weekday".

    Returns:
        dict with ``target``, ``dates``, ``records`` (<=20 ``{"date",
        "iso_year", "iso_week", "weekday", "weekday_name", "quarter",
        "day_of_year"}``), ``distribution``, ``dominant``, ``first``,
        ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non str/list/dict x, or a date
            that is not ``YYYY-MM-DD``; the offending value is quoted.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 200):
        raise ValueError(f"p1 must be an int in [1, 200], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 0 <= p2 <= 30):
        raise ValueError(f"p2 must be an int in [0, 30], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("iso_week", "quarter", "weekday"):
        raise ValueError(f"p4 must be 'iso_week', 'quarter' or 'weekday', got {p4!r}")
    if isinstance(x, str):
        raw = [x]
    elif isinstance(x, (list, tuple)):
        raw = [str(item) for item in x]
    elif isinstance(x, dict):
        raw = [str(value) for value in x.values()]
    else:
        raise ValueError(f"x must be a str, list or dict of dates, got {x!r}")
    parsed = []
    for item in raw:
        try:
            parsed.append(date.fromisoformat(item.strip()))
        except ValueError:
            raise ValueError(f"x dates must be YYYY-MM-DD, got {item!r}")
    if not parsed:
        raise ValueError(f"x must provide a date, got {x!r}")
    truncated, parsed = len(parsed) > p1, parsed[:p1]
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    records = []
    for current in parsed:
        shifted = date.fromordinal(current.toordinal() + p2)
        iso_year, iso_week, iso_weekday = shifted.isocalendar()
        records.append({
            "date": shifted.isoformat(), "iso_year": int(iso_year),
            "iso_week": int(iso_week),
            "weekday": int(iso_weekday - 1 if p3 else (shifted.weekday() + 1) % 7),
            "weekday_name": names[shifted.weekday()],
            "quarter": (shifted.month - 1) // 3 + 1,
            "day_of_year": shifted.timetuple().tm_yday})
    ordered = sorted(records, key=lambda record: (record[p4], record["date"]))
    distribution = {}
    for record in ordered:
        distribution[str(record[p4])] = distribution.get(str(record[p4]), 0) + 1
    return {
        "target": p4, "dates": len(ordered), "records": ordered[:20],
        "distribution": distribution,
        "dominant": sorted(distribution.items(), key=lambda pair: (-pair[1], pair[0]))[0][0],
        "first": ordered[0]["date"], "truncated": truncated,
    }


class TinyIsoCalendarTool(Tool):
    """Fully offline numeric reasoning component (au1k #20).

    Actions:
      - "run": apply the documented default parameterization to x.
      - "alt": apply the alternative parameterization 'p1/p3 override'.
      - "meta": return this assignment' provenance without computing.

    Any p1..p4 passed explicitly overrides the assignment value; None keeps it.
    Malformed inputs raise ValueError quoting the offending value.
    """

    MAX_X_CHARS: ClassVar[int] = 240
    MAX_X_ITEMS: ClassVar[int] = 200
    ACTIONS: ClassVar[tuple] = ("run", "alt", "meta")

    label: str = Field(default="au1k#20", description="series provenance label")

    def execute(self, action: str = "run", x: Any = None,
                 p1: Any = None,
                 p2: Any = None,
                 p3: Any = None,
                 p4: Any = None) -> Dict[str, Any]:
        """Run one bounded reasoning action. See the class docstring."""
        if action not in self.ACTIONS:
            raise ValueError("unknown action: %r" % (action,))
        assignment = {
            "series": "au1k",
            "index": 20,
            "algo": 'au_algo_020',
            "semantic": 'tiny_iso_calendar',
            "category": 'numeric',
            "docnote": 'iso_week coordinates, 10 dates, 0-day offset, monday weeks',
            "params": {'p1': 10, 'p2': 0, 'p3': True, 'p4': 'iso_week'},
        }
        if action == "meta":
            assignment["limits"] = {"MAX_X_CHARS": self.MAX_X_CHARS,
                                    "MAX_X_ITEMS": self.MAX_X_ITEMS}
            assignment["label"] = self.label
            return assignment
        provided = {}
        if p1 is not None:
            provided['p1'] = p1
        if p2 is not None:
            provided['p2'] = p2
        if p3 is not None:
            provided['p3'] = p3
        if p4 is not None:
            provided['p4'] = p4
        provided_keys = sorted(provided)
        provided = dict((k, provided[k]) for k in provided_keys)
        p1 = p1 if p1 is not None else 10
        p2 = p2 if p2 is not None else 0
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'iso_week'
        if action == "run":
            result = au_algo_020(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 10, 'p2': 0, 'p3': True, 'p4': 'iso_week'})
        canned = {'p1': 11}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_020(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

