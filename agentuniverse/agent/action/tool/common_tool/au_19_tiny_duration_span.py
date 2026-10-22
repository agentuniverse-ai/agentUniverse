"""TinyDurationSpanTool: span lengths in days, first 5 spans, 0-day offset, endpoints counted (au1k series #19, numeric)."""

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


def au_algo_019(x, p1=20, p2=0, p3=True, p4="days") -> dict:
    """Do date arithmetic over ISO spans and report weekday structure.

    Args:
        x: "start/end" spans, 2-item sequences, or a dict with start/end keys.
        p1: Spans considered, bounds [1, 100].
        p2: Day offset added to both endpoints before measuring, bounds [0, 365].
        p3: When True both endpoints count, so a one-day span reports 1 day.
        p4: Unit vocabulary, "days", "weeks" or "months".

    Returns:
        dict with ``unit``, ``spans``, ``records`` (<=20), ``total_days``,
        ``longest_days``, ``total``, ``overlaps``, ``weekday_counts``, ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a malformed span, a date that is not
            ``YYYY-MM-DD``, or an end before its start; the value is quoted.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 100):
        raise ValueError(f"p1 must be an int in [1, 100], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 0 <= p2 <= 365):
        raise ValueError(f"p2 must be an int in [0, 365], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("days", "weeks", "months"):
        raise ValueError(f"p4 must be 'days', 'weeks' or 'months', got {p4!r}")
    if isinstance(x, dict):
        raw = [[x.get("start"), x.get("end")]]
    elif isinstance(x, str):
        raw = [x]
    elif isinstance(x, (list, tuple)):
        raw = list(x)
    else:
        raise ValueError(f"x must be a str, list or dict of spans, got {x!r}")
    spans = []
    for item in raw:
        parts = ([chunk.strip() for chunk in item.split("/")] if isinstance(item, str) else
                 [str(part).strip() for part in item] if isinstance(item, (list, tuple)) else [])
        if len(parts) != 2:
            raise ValueError(f"x spans must be 'start/end' pairs, got {item!r}")
        try:
            begin, finish = date.fromisoformat(parts[0]), date.fromisoformat(parts[1])
        except ValueError:
            raise ValueError(f"x dates must be YYYY-MM-DD, got {item!r}")
        if finish < begin:
            raise ValueError(f"x span ends before it starts, got {item!r}")
        spans.append((begin, finish))
    if not spans:
        raise ValueError(f"x must provide a span, got {x!r}")
    truncated, spans = len(spans) > p1, spans[:p1]
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    records, weekdays = [], {}
    for begin, finish in spans:
        start = date.fromordinal(begin.toordinal() + p2)
        end = date.fromordinal(finish.toordinal() + p2)
        days = (end - start).days + (1 if p3 else 0)
        months = (end.year - start.year) * 12 + (end.month - start.month) - (
            1 if end.day < start.day else 0)
        weekday = names[start.weekday()]
        weekdays[weekday] = weekdays.get(weekday, 0) + 1
        records.append({"start": start.isoformat(), "end": end.isoformat(), "days": days,
                        "weeks": days // 7, "months": months, "weekday": weekday})
    overlaps = sum(1 for i in range(len(spans)) for j in range(i + 1, len(spans))
                   if spans[j][0] <= spans[i][1])
    return {
        "unit": p4, "spans": len(spans), "records": records[:20],
        "total_days": sum(r["days"] for r in records), "overlaps": overlaps,
        "longest_days": max(r["days"] for r in records), "total": sum(r[p4] for r in records),
        "weekday_counts": weekdays, "truncated": truncated,
    }


class TinyDurationSpanTool(Tool):
    """Fully offline numeric reasoning component (au1k #19).

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

    label: str = Field(default="au1k#19", description="series provenance label")

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
            "index": 19,
            "algo": 'au_algo_019',
            "semantic": 'tiny_duration_span',
            "category": 'numeric',
            "docnote": 'span lengths in days, first 5 spans, 0-day offset, endpoints counted',
            "params": {'p1': 5, 'p2': 0, 'p3': True, 'p4': 'days'},
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
        p1 = p1 if p1 is not None else 5
        p2 = p2 if p2 is not None else 0
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'days'
        if action == "run":
            result = au_algo_019(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 5, 'p2': 0, 'p3': True, 'p4': 'days'})
        canned = {'p1': 6}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_019(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

