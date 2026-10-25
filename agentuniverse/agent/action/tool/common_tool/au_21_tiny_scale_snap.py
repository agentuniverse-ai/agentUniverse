"""TinyScaleSnapTool: roman ladder snapping, tolerance 0%, 10 values, zero on (au1k series #21, numeric)."""

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


def au_algo_021(x, p1=40, p2=10, p3=False, p4="roman") -> dict:
    """Snap numbers onto a documented ladder of canonical scale values.

    Args:
        x: number, list of numbers, dict of numbers or a comma/semicolon
            separated numeric string.
        p1: Values considered, bounds [1, 200].
        p2: Maximum accepted relative residual in percent, bounds [0, 100].
        p3: When True zero joins every ladder.
        p4: Ladder vocabulary, "roman", "quarters" (0.25 steps) or "binary".

    Returns:
        dict with ``scale``, ``values``, ``snapped``, ``ladder_size``, ``results``
        (<=20 ``{"value", "snapped", "residual"}``), ``mean_residual``,
        ``max_residual``, ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation or a non numeric x; the offending
            value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 200):
        raise ValueError(f"p1 must be an int in [1, 200], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 0 <= p2 <= 100):
        raise ValueError(f"p2 must be an int in [0, 100], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("roman", "quarters", "binary"):
        raise ValueError(f"p4 must be 'roman', 'quarters' or 'binary', got {p4!r}")
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
    truncated, values = len(values) > p1, values[:p1]
    ladders = {
        "roman": [1.0, 2.0, 3.0, 4.0, 5.0, 10.0, 20.0, 30.0, 40.0, 50.0, 100.0,
                  200.0, 300.0, 400.0, 500.0, 1000.0],
        "quarters": [step * 0.25 for step in range(1, 41)],
        "binary": [float(2 ** power) for power in range(0, 17)],
    }
    ladder = sorted(set(ladders[p4] + ([0.0] if p3 else [])))
    results, residuals, snapped = [], [], 0
    for value in values:
        nearest = min(ladder, key=lambda step: (abs(step - value), step))
        base = abs(value) if abs(value) > 1e-12 else 1.0
        residual = abs(nearest - value) / base * 100.0
        accepted = residual <= p2
        snapped += 1 if accepted else 0
        residuals.append(residual if accepted else 0.0)
        results.append({"value": round(value, 4),
                        "snapped": round(nearest if accepted else value, 4),
                        "residual": round(residual if accepted else 0.0, 4)})
    return {
        "scale": p4, "values": len(values), "snapped": snapped,
        "ladder_size": len(ladder), "results": results[:20],
        "mean_residual": round(sum(residuals) / len(residuals), 4) if residuals else 0.0,
        "max_residual": round(max(residuals), 4) if residuals else 0.0,
        "truncated": truncated,
    }


class TinyScaleSnapTool(Tool):
    """Fully offline numeric reasoning component (au1k #21).

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

    label: str = Field(default="au1k#21", description="series provenance label")

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
            "index": 21,
            "algo": 'au_algo_021',
            "semantic": 'tiny_scale_snap',
            "category": 'numeric',
            "docnote": 'roman ladder snapping, tolerance 0%, 10 values, zero on',
            "params": {'p1': 10, 'p2': 0, 'p3': True, 'p4': 'roman'},
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
        p4 = p4 if p4 is not None else 'roman'
        if action == "run":
            result = au_algo_021(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 10, 'p2': 0, 'p3': True, 'p4': 'roman'})
        canned = {'p1': 11}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_021(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

