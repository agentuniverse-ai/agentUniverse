"""TinyDegreeMapTool: out degree map of 10 edges, top 1, undirected on (au1k series #27, structural)."""

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


def au_algo_027(x, p1=5, p2=60, p3=False, p4="both") -> dict:
    """Build a directed degree map from "source->target" edges.

    Args:
        x: list of "a->b" edge strings, or a comma/space separated string of them.
        p1: Ranked nodes returned, bounds [1, 20].
        p2: Edges considered, bounds [1, 500].
        p3: When True every edge is also traversed backwards (undirected view).
        p4: Degree vocabulary, "out", "in" or "both".

    Returns:
        dict with ``metric``, ``edges``, ``nodes``, ``self_loops``, ``degree_map``
        (<=``p1`` ``{"node", "degree"}``), ``hub``, ``sources`` (<=10), ``sinks``
        (<=10), ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non str/list x, an empty edge
            list, or an edge without two non-empty endpoints; the offending value
            is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 20):
        raise ValueError(f"p1 must be an int in [1, 20], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 500):
        raise ValueError(f"p2 must be an int in [1, 500], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("out", "in", "both"):
        raise ValueError(f"p4 must be 'out', 'in' or 'both', got {p4!r}")
    if isinstance(x, str):
        raw = [chunk for chunk in re.split(r"[,;\s]+", x.strip()) if chunk]
    elif isinstance(x, (list, tuple)):
        raw = [str(item) for item in x]
    else:
        raise ValueError(f"x must be a str or list of edges, got {x!r}")
    if not raw:
        raise ValueError(f"x must provide an edge, got {x!r}")
    truncated, raw = len(raw) > p2, raw[:p2]
    out_degree, in_degree, loops = {}, {}, 0
    for item in raw:
        head, _, tail = item.partition("->")
        head, tail = head.strip(), tail.strip()
        if not head or not tail:
            raise ValueError(f"x edges must be 'a->b', got {item!r}")
        loops += 1 if head == tail else 0
        for node in (head, tail):
            out_degree.setdefault(node, 0)
            in_degree.setdefault(node, 0)
        out_degree[head] += 1
        in_degree[tail] += 1
        if p3:
            out_degree[tail] += 1
            in_degree[head] += 1
    ranked = sorted(({"node": node, "degree": out_degree[node] if p4 == "out" else
                      in_degree[node] if p4 == "in" else out_degree[node] + in_degree[node]}
                     for node in out_degree),
                    key=lambda entry: (-entry["degree"], entry["node"]))
    return {
        "metric": p4, "edges": len(raw), "nodes": len(out_degree), "self_loops": loops,
        "degree_map": ranked[:p1], "hub": ranked[0]["node"] if ranked else None,
        "sources": [node for node in sorted(out_degree)
                    if out_degree[node] and not in_degree[node]][:10],
        "sinks": [node for node in sorted(out_degree)
                  if in_degree[node] and not out_degree[node]][:10],
        "truncated": truncated,
    }


class TinyDegreeMapTool(Tool):
    """Fully offline structural reasoning component (au1k #27).

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

    label: str = Field(default="au1k#27", description="series provenance label")

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
            "index": 27,
            "algo": 'au_algo_027',
            "semantic": 'tiny_degree_map',
            "category": 'structural',
            "docnote": 'out degree map of 10 edges, top 1, undirected on',
            "params": {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'out'},
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
        p4 = p4 if p4 is not None else 'out'
        if action == "run":
            result = au_algo_027(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 1, 'p2': 10, 'p3': True, 'p4': 'out'})
        canned = {'p1': 2}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_027(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

