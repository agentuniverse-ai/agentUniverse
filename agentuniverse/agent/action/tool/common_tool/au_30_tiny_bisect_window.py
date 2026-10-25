"""TinyBisectWindowTool: left bisect window +/-1 around the median of 10 values (au1k series #30, search)."""

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


def au_algo_030(x, p1=10, p2=60, p3=True, p4="left") -> dict:
    """Find the index window around the sample median with bisection.

    Sorts the observations, takes the median as pivot and uses ``bisect`` to
    locate the first and last index inside ``pivot +/- p1``; ``p4`` decides which
    side wins when a value sits exactly on a bound.

    Args:
        x: number, list of numbers, dict of numbers or a numeric string.
        p1: Half-width of the window in value units, bounds [1, 100].
        p2: Observations considered, bounds [1, 200].
        p3: When True the window is clamped to the observed range.
        p4: Boundary vocabulary, "left" or "right" (mirror behaviour).

    Returns:
        dict with ``bias``, ``count``, ``pivot``, ``window`` (``{"low", "high"}``),
        ``lo_index``, ``hi_index``, ``inside``, ``sample`` (<=10), ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non numeric x, or an empty
            sample; the offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 100):
        raise ValueError(f"p1 must be an int in [1, 100], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("left", "right"):
        raise ValueError(f"p4 must be 'left' or 'right', got {p4!r}")
    if isinstance(x, dict):
        raw = list(x.values())
    elif isinstance(x, str):
        raw = [chunk for chunk in re.split(r"[,;]", x) if chunk.strip()]
    elif isinstance(x, (list, tuple)):
        raw = list(x)
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        raw = [x]
    else:
        raise ValueError(f"x must be numeric or a numeric sequence, got {x!r}")
    values = []
    for item in raw:
        try:
            values.append(float(item))
        except (TypeError, ValueError):
            raise ValueError(f"x items must be numbers, got {item!r}")
    if not values:
        raise ValueError(f"x must provide a value, got {x!r}")
    truncated, values = len(values) > p2, sorted(values[:p2])
    pivot = values[len(values) // 2]
    low = max(pivot - p1, values[0]) if p3 else pivot - p1
    high = min(pivot + p1, values[-1]) if p3 else pivot + p1
    if p4 == "left":
        lo, hi = bisect.bisect_left(values, low), bisect.bisect_right(values, high)
    else:
        lo = max(bisect.bisect_right(values, low - 1e-12) - 1, 0)
        hi = min(bisect.bisect_left(values, high) + 1, len(values))
    inside = values[lo:hi]
    return {
        "bias": p4, "count": len(values), "pivot": round(pivot, 6),
        "window": {"low": round(low, 6), "high": round(high, 6)},
        "lo_index": lo, "hi_index": hi, "inside": len(inside),
        "sample": [round(value, 6) for value in inside[:10]], "truncated": truncated,
    }


class TinyBisectWindowTool(Tool):
    """Fully offline search reasoning component (au1k #30).

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

    label: str = Field(default="au1k#30", description="series provenance label")

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
            "index": 30,
            "algo": 'au_algo_030',
            "semantic": 'tiny_bisect_window',
            "category": 'search',
            "docnote": 'left bisect window +/-1 around the median of 10 values',
            "params": {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'left'},
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
        p1 = p1 if p1 is not None else 1
        p2 = p2 if p2 is not None else 10
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'left'
        if action == "run":
            result = au_algo_030(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 1, 'p2': 10, 'p3': True, 'p4': 'left'})
        canned = {'p1': 2}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_030(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

