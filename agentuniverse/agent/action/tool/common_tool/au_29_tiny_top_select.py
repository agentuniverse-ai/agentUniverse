"""TinyTopSelectTool: first top-1 selection over 10 scores, descending on (au1k series #29, search)."""

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


def au_algo_029(x, p1=3, p2=40, p3=True, p4="first") -> dict:
    """Select the top-k scored items with an explicit tie-break policy.

    Args:
        x: list of numbers or "name=score" strings, a dict of name -> score, or a
            comma separated string of the same.
        p1: Items selected, bounds [1, 20].
        p2: Items considered, bounds [1, 200].
        p3: When True the highest scores rank first, otherwise the lowest.
        p4: Tie-break vocabulary, "first" (earlier input wins), "last" (later
            input wins) or "lex" (alphabetical name wins).

    Returns:
        dict with ``descending``, ``k``, ``items``, ``selected`` (<=``p1``
        ``{"name", "score", "rank"}``), ``cut_score``, ``cut_tie``, ``dropped``,
        ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, an unsupported x container, a
            malformed item, a non numeric score, or an empty item list; the
            offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 20):
        raise ValueError(f"p1 must be an int in [1, 20], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("first", "last", "lex"):
        raise ValueError(f"p4 must be 'first', 'last' or 'lex', got {p4!r}")
    if isinstance(x, dict):
        raw = [[name, value] for name, value in x.items()]
    elif isinstance(x, str):
        raw = [chunk for chunk in re.split(r"[,;]", x) if chunk.strip()]
    elif isinstance(x, (list, tuple)):
        raw = list(x)
    else:
        raise ValueError(f"x must be a list, dict or str of scored items, got {x!r}")
    items = []
    for position, item in enumerate(raw):
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            name, score = str(item[0]), item[1]
        elif isinstance(item, str) and "=" in item:
            name, score = item.split("=", 1)[0].strip(), item.split("=", 1)[1]
        elif isinstance(item, (int, float)) and not isinstance(item, bool):
            name, score = str(item), item
        else:
            raise ValueError(f"x items must be numbers or 'name=score', got {item!r}")
        try:
            items.append((name, float(score), position))
        except (TypeError, ValueError):
            raise ValueError(f"x scores must be numeric, got {item!r}")
    if not items:
        raise ValueError(f"x must provide an item, got {x!r}")
    truncated, items = len(items) > p2, items[:p2]
    tie = {"first": lambda entry: entry[2], "last": lambda entry: -entry[2],
           "lex": lambda entry: entry[0]}[p4]
    ordered = sorted(items, key=(lambda entry: (-entry[1], tie(entry))) if p3
                     else (lambda entry: (entry[1], tie(entry))))
    cut = ordered[p1 - 1][1] if len(ordered) >= p1 else None
    return {
        "descending": p3, "k": p1, "items": len(items),
        "selected": [{"name": name, "score": round(score, 6), "rank": rank + 1}
                     for rank, (name, score, _) in enumerate(ordered[:p1])],
        "cut_score": round(cut, 6) if cut is not None else None,
        "cut_tie": bool(len(ordered) > p1 and cut is not None
                        and abs(ordered[p1][1] - cut) <= 1e-12),
        "dropped": max(len(ordered) - p1, 0), "truncated": truncated,
    }


class TinyTopSelectTool(Tool):
    """Fully offline search reasoning component (au1k #29).

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

    label: str = Field(default="au1k#29", description="series provenance label")

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
            "index": 29,
            "algo": 'au_algo_029',
            "semantic": 'tiny_top_select',
            "category": 'search',
            "docnote": 'first top-1 selection over 10 scores, descending on',
            "params": {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'first'},
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
        p4 = p4 if p4 is not None else 'first'
        if action == "run":
            result = au_algo_029(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 1, 'p2': 10, 'p3': True, 'p4': 'first'})
        canned = {'p1': 2}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_029(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

