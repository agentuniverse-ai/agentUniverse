"""TinyMonotoneRunTool: up monotone runs of 2+ steps over 10 values, equal ok on (au1k series #11, sequence)."""

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


def au_algo_011(x, p1=3, p2=100, p3=False, p4="both") -> dict:
    """Scan a numeric series for monotone runs of a minimum length.

    Args:
        x: number, list of numbers or a comma/semicolon separated numeric string.
        p1: Minimum run length in observations, bounds [2, 20].
        p2: Observations considered, bounds [3, 500].
        p3: When True equal consecutive values are tolerated inside a run.
        p4: Direction vocabulary, one of "up", "down", "both".

    Returns:
        dict with ``direction``, ``values``, ``runs`` (<=20, 0-based inclusive),
        ``run_count``, ``longest_run``, ``coverage``, ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non numeric/list/string x, a
            non numeric item, or fewer than ``p1`` values; the offending value is
            quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 2 <= p1 <= 20):
        raise ValueError(f"p1 must be an int in [2, 20], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 3 <= p2 <= 500):
        raise ValueError(f"p2 must be an int in [3, 500], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("up", "down", "both"):
        raise ValueError(f"p4 must be 'up', 'down' or 'both', got {p4!r}")
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        raw = [x]
    elif isinstance(x, str):
        raw = [chunk for chunk in re.split(r"[,;]", x) if chunk.strip()]
    elif isinstance(x, (list, tuple)):
        raw = list(x)
    else:
        raise ValueError(f"x must be a number, list or numeric string, got {x!r}")
    values = []
    for item in raw:
        try:
            values.append(float(item))
        except (TypeError, ValueError):
            raise ValueError(f"x items must be numbers, got {item!r}")
    truncated, values = len(values) > p2, values[:p2]
    if len(values) < p1:
        raise ValueError(f"x must provide {p1} values, got {len(values)!r}")
    spans, start, trend = [], 0, 0
    for index in range(1, len(values)):
        diff = values[index] - values[index - 1]
        step = 0 if abs(diff) <= 1e-12 else (1 if diff > 0 else -1)
        if step == 0 and not p3:
            if trend:
                spans.append((start, index - 1, trend))
            start, trend = index, 0
        elif step and trend == 0:
            trend = step
        elif step and step != trend:
            spans.append((start, index - 1, trend))
            start, trend = index - 1, step
    if trend:
        spans.append((start, len(values) - 1, trend))
    wanted = {"up": (1,), "down": (-1,), "both": (1, -1)}[p4]
    runs = [{"start": b, "end": e, "length": e - b + 1,
             "trend": "up" if sign > 0 else "down"}
            for b, e, sign in spans if sign in wanted and e - b + 1 >= p1]
    covered = {step for run in runs for step in range(run["start"], run["end"] + 1)}
    return {
        "direction": p4, "values": len(values), "runs": runs[:20],
        "run_count": len(runs),
        "longest_run": max((run["length"] for run in runs), default=0),
        "coverage": round(len(covered) / len(values), 4), "truncated": truncated,
    }


class TinyMonotoneRunTool(Tool):
    """Fully offline sequence reasoning component (au1k #11).

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

    label: str = Field(default="au1k#11", description="series provenance label")

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
            "index": 11,
            "algo": 'au_algo_011',
            "semantic": 'tiny_monotone_run',
            "category": 'sequence',
            "docnote": 'up monotone runs of 2+ steps over 10 values, equal ok on',
            "params": {'p1': 2, 'p2': 10, 'p3': True, 'p4': 'up'},
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
        p1 = p1 if p1 is not None else 2
        p2 = p2 if p2 is not None else 10
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'up'
        if action == "run":
            result = au_algo_011(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 2, 'p2': 10, 'p3': True, 'p4': 'up'})
        canned = {'p1': 3}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_011(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

