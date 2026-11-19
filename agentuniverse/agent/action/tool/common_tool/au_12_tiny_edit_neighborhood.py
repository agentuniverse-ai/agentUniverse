"""TinyEditNeighborhoodTool: levenshtein neighbourhood radius 0 over 10 tokens, casefold on (au1k series #12, sequence)."""

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


def au_algo_012(x, p1=2, p2=40, p3=True, p4="levenshtein") -> dict:
    """Count items within a bounded edit distance of a pivot token.

    The first item is the pivot; every other item gets a distance under the
    ``p4`` metric, turning typo clusters into a histogram and a neighbour list.

    Args:
        x: list of tokens, whitespace string, number or dict (keys are used).
        p1: Maximum accepted distance, bounds [0, 4].
        p2: Items considered, bounds [1, 200].
        p3: When True tokens are casefolded before comparison.
        p4: Metric vocabulary, "levenshtein" (edit operations) or "hamming".

    Returns:
        dict with ``metric``, ``pivot``, ``items``, ``within``, ``ratio``,
        ``histogram`` (distance str -> count), ``neighbours`` (<=20), ``max_distance``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non list/dict/str/number x, or fewer
            than two items; the offending value is quoted.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 0 <= p1 <= 4):
        raise ValueError(f"p1 must be an int in [0, 4], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("levenshtein", "hamming"):
        raise ValueError(f"p4 must be 'levenshtein' or 'hamming', got {p4!r}")
    if isinstance(x, str):
        items = x.split()
    elif isinstance(x, (list, tuple)):
        items = [str(item) for item in x]
    elif isinstance(x, dict):
        items = [str(key) for key in x]
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        items = [str(x)]
    else:
        raise ValueError(f"x must be str, list, dict or number, got {x!r}")
    if len(items) < 2:
        raise ValueError(f"x must contain two items, got {x!r}")
    truncated, items = len(items) > p2, items[:p2]
    items = [(item.strip()[:64]).casefold() if p3 else item.strip()[:64] for item in items]
    pivot, cap, histogram, distances = items[0], p1 + 1, {}, []
    for other in items[1:]:
        if p4 == "hamming":
            distance = cap if len(other) != len(pivot) else sum(
                1 for left, right in zip(pivot, other) if left != right)
        elif abs(len(other) - len(pivot)) > p1:
            distance = cap
        else:
            previous = list(range(len(other) + 1))
            for row in range(1, len(pivot) + 1):
                current = [row] + [0] * len(other)
                for column in range(1, len(other) + 1):
                    cost = 0 if pivot[row - 1] == other[column - 1] else 1
                    current[column] = min(previous[column] + 1, current[column - 1] + 1,
                                          previous[column - 1] + cost)
                previous = current
            distance = previous[-1]
        distance = min(distance, cap)
        distances.append((other, distance))
        histogram[str(distance)] = histogram.get(str(distance), 0) + 1
    within = sorted((pair for pair in distances if pair[1] <= p1), key=lambda p: (p[1], p[0]))
    return {
        "metric": p4, "pivot": pivot, "items": len(items), "within": len(within),
        "ratio": round(len(within) / len(distances), 4), "histogram": histogram,
        "neighbours": [{"token": t, "distance": d} for t, d in within[:20]],
        "max_distance": max(distance for _, distance in distances), "truncated": truncated,
    }


class TinyEditNeighborhoodTool(Tool):
    """Fully offline sequence reasoning component (au1k #12).

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

    label: str = Field(default="au1k#12", description="series provenance label")

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
            "index": 12,
            "algo": 'au_algo_012',
            "semantic": 'tiny_edit_neighborhood',
            "category": 'sequence',
            "docnote": 'levenshtein neighbourhood radius 0 over 10 tokens, casefold on',
            "params": {'p1': 0, 'p2': 10, 'p3': True, 'p4': 'levenshtein'},
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
        p1 = p1 if p1 is not None else 0
        p2 = p2 if p2 is not None else 10
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'levenshtein'
        if action == "run":
            result = au_algo_012(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 0, 'p2': 10, 'p3': True, 'p4': 'levenshtein'})
        canned = {'p1': 1}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_012(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

