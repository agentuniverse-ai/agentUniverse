"""TinyWaypointPathTool: euclid waypoint compression, tolerance 0, 5 points, ends kept on (au1k series #14, sequence)."""

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


def au_algo_014(x, p1=3, p2=40, p3=True, p4="euclid") -> dict:
    """Compress a polyline by dropping waypoints that stay within tolerance.

    Args:
        x: list of waypoints ("x,y" strings or 2-item sequences) or such a string.
        p1: Perpendicular tolerance in coordinate units, bounds [0, 500].
        p2: Waypoints considered, bounds [2, 200].
        p3: When True the first and last waypoints are always kept.
        p4: Distance vocabulary, "euclid" or "manhattan".

    Returns:
        dict with ``metric``, ``input_points``, ``kept_points``, ``dropped``, ``compression``, ``path_before``,
        ``path_after``, ``kept`` (<=20), ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, an unsupported x container, a non 2-D
            numeric waypoint, or fewer than two waypoints; the value is quoted.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 0 <= p1 <= 500):
        raise ValueError(f"p1 must be an int in [0, 500], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 2 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [2, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("euclid", "manhattan"):
        raise ValueError(f"p4 must be 'euclid' or 'manhattan', got {p4!r}")
    if isinstance(x, str):
        raw = [chunk for chunk in re.split(r"[;\n]", x) if chunk.strip()]
    elif isinstance(x, (list, tuple)):
        raw = list(x)
    else:
        raise ValueError(f"x must be a list of waypoints or a string, got {x!r}")
    points = []
    for item in raw:
        try:
            pair = re.split(r"[, ]+", item.strip()) if isinstance(item, str) else item
            points.append((float(pair[0]), float(pair[1])))
        except (IndexError, TypeError, ValueError):
            raise ValueError(f"x waypoints must be 2-D numeric points, got {item!r}")
    if len(points) < 2:
        raise ValueError(f"x must contain two waypoints, got {x!r}")
    truncated, points = len(points) > p2, points[:p2]

    def deviation(point, start, end):
        """Distance between one waypoint and the chord joining two others."""
        dx, dy = end[0] - start[0], end[1] - start[1]
        scale = dx * dx + dy * dy
        ratio = 0.0 if not scale else max(0.0, min(1.0, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / scale))
        offset = (point[0] - (start[0] + ratio * dx), point[1] - (start[1] + ratio * dy))
        return math.hypot(*offset) if p4 == "euclid" else abs(offset[0]) + abs(offset[1])

    keep, stack = {0, len(points) - 1}, [(0, len(points) - 1)]
    while stack:
        begin, end = stack.pop()
        worst, index = max(((deviation(points[i], points[begin], points[end]), i)
                            for i in range(begin + 1, end)), default=(-1.0, -1))
        if index >= 0 and worst > p1:
            keep.add(index)
            stack.extend([(begin, index), (index, end)])
    if not p3:
        keep = {index for index in keep if 0 < index < len(points) - 1} or {0}
    kept = [points[index] for index in sorted(keep)]
    before = round(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:])), 3)
    after = round(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(kept, kept[1:])), 3)
    return {
        "metric": p4, "input_points": len(points), "kept_points": len(kept),
        "dropped": len(points) - len(kept), "compression": round(len(kept) / len(points), 4),
        "path_before": before, "path_after": after,
        "kept": [[round(px, 3), round(py, 3)] for px, py in kept][:20], "truncated": truncated,
    }


class TinyWaypointPathTool(Tool):
    """Fully offline sequence reasoning component (au1k #14).

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

    label: str = Field(default="au1k#14", description="series provenance label")

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
            "index": 14,
            "algo": 'au_algo_014',
            "semantic": 'tiny_waypoint_path',
            "category": 'sequence',
            "docnote": 'euclid waypoint compression, tolerance 0, 5 points, ends kept on',
            "params": {'p1': 0, 'p2': 5, 'p3': True, 'p4': 'euclid'},
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
        p2 = p2 if p2 is not None else 5
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'euclid'
        if action == "run":
            result = au_algo_014(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 0, 'p2': 5, 'p3': True, 'p4': 'euclid'})
        canned = {'p1': 1}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_014(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

