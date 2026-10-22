"""TinyAngleReduceTool: degrees circular statistics, 4 angle buckets, 0 decimals, wrap on (au1k series #22, numeric)."""

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


def au_algo_022(x, p1=8, p2=2, p3=True, p4="degrees") -> dict:
    """Reduce a set of angles to circular statistics and angle buckets.

    Args:
        x: number, list of numbers, dict of numbers or a numeric angles string.
        p1: Number of equal angle buckets, bounds [2, 36].
        p2: Decimal places applied to floats in the result, bounds [0, 6].
        p3: When True angles are wrapped into the primary circle first.
        p4: Input unit vocabulary, "degrees" or "radians".

    Returns:
        dict with ``unit``, ``count``, ``mean_angle``, ``resultant``, ``circular_std``,
        ``dominant_bucket``, ``bucket_counts``, ``wrapped``, ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non numeric x, or an empty sample.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 2 <= p1 <= 36):
        raise ValueError(f"p1 must be an int in [2, 36], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 0 <= p2 <= 6):
        raise ValueError(f"p2 must be an int in [0, 6], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("degrees", "radians"):
        raise ValueError(f"p4 must be 'degrees' or 'radians', got {p4!r}")
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
        raise ValueError(f"x must provide an angle, got {x!r}")
    truncated, values = len(values) > 1000, values[:1000]
    radians, wrapped = [], 0
    for value in values:
        angle = value if p4 == "radians" else math.radians(value)
        if p3:
            normalised = math.fmod(angle, 2.0 * math.pi) % (2.0 * math.pi)
            wrapped += 1 if abs(normalised - angle) > 1e-12 else 0
            angle = normalised
        radians.append(angle)
    sum_cos = sum(math.cos(angle) for angle in radians)
    sum_sin = sum(math.sin(angle) for angle in radians)
    resultant = math.hypot(sum_cos, sum_sin) / len(radians)
    mean = math.atan2(sum_sin, sum_cos) % (2.0 * math.pi)
    counts = [0] * p1
    for angle in radians:
        counts[int(angle / (2.0 * math.pi) * p1) % p1] += 1
    best = max(range(p1), key=lambda index: (counts[index], -index))
    digits, start = min(p2 + 2, 8), best * (2.0 * math.pi) / p1
    return {
        "unit": p4, "count": len(radians),
        "mean_angle": round(mean if p4 == "radians" else math.degrees(mean), p2),
        "resultant": round(resultant, digits),
        "circular_std": round(math.sqrt(max(-2.0 * math.log(resultant), 0.0)), digits),
        "dominant_bucket": {"start": round(start if p4 == "radians" else math.degrees(start), p2),
                            "count": counts[best]},
        "bucket_counts": counts, "wrapped": wrapped, "truncated": truncated,
    }


class TinyAngleReduceTool(Tool):
    """Fully offline numeric reasoning component (au1k #22).

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

    label: str = Field(default="au1k#22", description="series provenance label")

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
            "index": 22,
            "algo": 'au_algo_022',
            "semantic": 'tiny_angle_reduce',
            "category": 'numeric',
            "docnote": 'degrees circular statistics, 4 angle buckets, 0 decimals, wrap on',
            "params": {'p1': 4, 'p2': 0, 'p3': True, 'p4': 'degrees'},
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
        p1 = p1 if p1 is not None else 4
        p2 = p2 if p2 is not None else 0
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'degrees'
        if action == "run":
            result = au_algo_022(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 4, 'p2': 0, 'p3': True, 'p4': 'degrees'})
        canned = {'p1': 5}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_022(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

