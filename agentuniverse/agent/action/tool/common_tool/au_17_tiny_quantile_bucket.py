"""TinyQuantileBucketTool: 2 linear quantile bins, 0 decimals, outer edges on (au1k series #17, numeric)."""

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


def au_algo_017(x, p1=4, p2=2, p3=True, p4="linear") -> dict:
    """Bucket a numeric sample into equal-probability quantile bins.

    Args:
        x: number, list of numbers, dict of numbers or a numeric string.
        p1: Number of equal-probability bins, bounds [2, 20].
        p2: Decimal places applied to floats in the result, bounds [0, 6].
        p3: When True the outer edges are the sample minimum and maximum.
        p4: Interpolation vocabulary, "linear", "lower" or "higher".

    Returns:
        dict with ``bins``, ``method``, ``count``, ``edges`` (``p1 + 1`` floats),
        ``counts``, ``labels``, ``median``, ``iqr``, ``empty_bins``, ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non numeric x, or too few observations.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 2 <= p1 <= 20):
        raise ValueError(f"p1 must be an int in [2, 20], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 0 <= p2 <= 6):
        raise ValueError(f"p2 must be an int in [0, 6], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("linear", "lower", "higher"):
        raise ValueError(f"p4 must be 'linear', 'lower' or 'higher', got {p4!r}")
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
    if len(values) < p1:
        raise ValueError(f"x must provide {p1} values, got {len(values)!r}")
    truncated, values = len(values) > 2000, sorted(values[:2000])

    def quantile(fraction):
        """Return one quantile of the sorted sample under ``p4``."""
        position = fraction * (len(values) - 1)
        low, high = int(math.floor(position)), int(math.ceil(position))
        if p4 == "lower" or low == high:
            return values[low]
        if p4 == "higher":
            return values[high]
        return values[low] * (high - position) + values[high] * (position - low)

    edges = [quantile(index / p1) for index in range(p1 + 1)]
    if p3:
        edges[0], edges[-1] = values[0], values[-1]
    counts = [0] * p1
    for value in values:
        counts[min(max(bisect.bisect_right(edges, value) - 1, 0), p1 - 1)] += 1
    return {
        "bins": p1, "method": p4, "count": len(values),
        "edges": [round(edge, p2) for edge in edges], "counts": counts,
        "labels": [f"q{index}-q{index + 1}" for index in range(p1)],
        "median": round(quantile(0.5), p2),
        "iqr": round(quantile(0.75) - quantile(0.25), p2),
        "empty_bins": sum(1 for count in counts if count == 0),
        "truncated": truncated,
    }


class TinyQuantileBucketTool(Tool):
    """Fully offline numeric reasoning component (au1k #17).

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

    label: str = Field(default="au1k#17", description="series provenance label")

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
            "index": 17,
            "algo": 'au_algo_017',
            "semantic": 'tiny_quantile_bucket',
            "category": 'numeric',
            "docnote": '2 linear quantile bins, 0 decimals, outer edges on',
            "params": {'p1': 2, 'p2': 0, 'p3': True, 'p4': 'linear'},
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
        p2 = p2 if p2 is not None else 0
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'linear'
        if action == "run":
            result = au_algo_017(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 2, 'p2': 0, 'p3': True, 'p4': 'linear'})
        canned = {'p1': 3}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_017(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

