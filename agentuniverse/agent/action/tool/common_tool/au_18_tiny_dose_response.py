"""TinyDoseResponseTool: linear dose-response curve, 4 points, 0 decimals, clamp on (au1k series #18, numeric)."""

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


def au_algo_018(x, p1=24, p2=3, p3=True, p4="linear") -> dict:
    """Interpolate a dose-response style curve between measured points.

    Args:
        x: "dose:response" strings, 2-item sequences or a dict of dose -> response.
        p1: Curve points returned, bounds [2, 100].
        p2: Decimal places applied to doses and responses, bounds [0, 6].
        p3: When True out-of-range queries clamp instead of extrapolating.
        p4: Interpolation vocabulary, "linear" (straight segments) or "step".

    Returns:
        dict with ``method``, ``points``, ``curve`` (<=``p1`` pairs), ``max_response``,
        ``max_dose``, ``half_max_dose``, ``monotone``, ``clamped``, ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, fewer than two parseable pairs,
            or a non numeric pair; the offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 2 <= p1 <= 100):
        raise ValueError(f"p1 must be an int in [2, 100], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 0 <= p2 <= 6):
        raise ValueError(f"p2 must be an int in [0, 6], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("linear", "step"):
        raise ValueError(f"p4 must be 'linear' or 'step', got {p4!r}")
    if isinstance(x, dict):
        raw = [[key, value] for key, value in x.items()]
    elif isinstance(x, str):
        raw = [chunk for chunk in re.split(r"[;\n]", x) if chunk.strip()]
    elif isinstance(x, (list, tuple)):
        raw = list(x)
    else:
        raise ValueError(f"x must be a str, list or dict of pairs, got {x!r}")
    pairs = []
    for item in raw:
        try:
            pair = re.split(r"[:,\s]+", item.strip()) if isinstance(item, str) else item
            pairs.append((float(pair[0]), float(pair[1])))
        except (IndexError, TypeError, ValueError):
            raise ValueError(f"x pairs must be numeric dose/response, got {item!r}")
    if len(pairs) < 2:
        raise ValueError(f"x must provide two pairs, got {x!r}")
    pairs.sort(key=lambda pair: pair[0])
    doses, responses = [pair[0] for pair in pairs], [pair[1] for pair in pairs]
    queries = sorted(set(doses) | {(a + b) / 2.0 for a, b in zip(doses, doses[1:])})
    curve, clamped = [], 0
    for query in queries:
        slot = bisect.bisect_left(doses, query)
        if slot <= 0 or slot >= len(doses):
            near = 0 if slot <= 0 else len(doses) - 2
            slope = (responses[near + 1] - responses[near]) / (doses[near + 1] - doses[near] or 1.0)
            value = responses[near] if p3 else responses[near] + slope * (query - doses[near])
            clamped += 1 if p3 else 0
        elif p4 == "step" or doses[slot] == query:
            value = responses[slot - 1] if p4 == "step" else responses[slot]
        else:
            value = responses[slot - 1] + (query - doses[slot - 1]) / (
                doses[slot] - doses[slot - 1]) * (responses[slot] - responses[slot - 1])
        curve.append({"dose": round(query, p2), "response": round(value, p2)})
    half = min(responses) + (max(responses) - min(responses)) / 2.0
    steps = [b - a for a, b in zip(responses, responses[1:])]
    return {
        "method": p4, "points": len(pairs), "curve": curve[:p1],
        "max_response": round(max(responses), p2),
        "max_dose": round(doses[responses.index(max(responses))], p2),
        "half_max_dose": next((p["dose"] for p in curve if p["response"] >= half), None),
        "monotone": all(step >= 0 for step in steps) or all(step <= 0 for step in steps),
        "clamped": clamped, "truncated": len(queries) > p1,
    }


class TinyDoseResponseTool(Tool):
    """Fully offline numeric reasoning component (au1k #18).

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

    label: str = Field(default="au1k#18", description="series provenance label")

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
            "index": 18,
            "algo": 'au_algo_018',
            "semantic": 'tiny_dose_response',
            "category": 'numeric',
            "docnote": 'linear dose-response curve, 4 points, 0 decimals, clamp on',
            "params": {'p1': 4, 'p2': 0, 'p3': True, 'p4': 'linear'},
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
        p4 = p4 if p4 is not None else 'linear'
        if action == "run":
            result = au_algo_018(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 4, 'p2': 0, 'p3': True, 'p4': 'linear'})
        canned = {'p1': 5}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_018(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

