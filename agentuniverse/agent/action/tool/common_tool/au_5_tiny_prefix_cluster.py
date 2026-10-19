"""TinyPrefixClusterTool: 1-char prefix clusters over 10 items, lex order (au1k series #5, text)."""

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


def au_algo_005(x, p1=2, p2=80, p3=True, p4="lex") -> dict:
    """Cluster items by a fixed-length prefix into a review index.

    Builds ``prefix -> members`` buckets and reports bucket sizes, the singleton
    share and the largest bucket, which exposes naming collisions and
    auto-complete fan-out.

    Args:
        x: str, list, dict or number; a list stays an ordered item list.
        p1: Prefix length in characters, bounds [1, 8].
        p2: Items considered, bounds [1, 200].
        p3: When True items are casefolded and stripped before bucketing.
        p4: Ordering vocabulary, "lex" (by key) or "count" (by size then key).

    Returns:
        dict with ``prefix``, ``items``, ``clusters``, ``cluster_list`` (<=20
        ``{"key", "size", "members"}``), ``largest``, ``singleton_ratio``,
        ``truncated``.

    Raises:
        ValueError: if p1/p2/p3/p4 break the bounds or vocabulary above, if x is
            not a str/list/dict/number, or if no item survives normalisation;
            the offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 8):
        raise ValueError(f"p1 must be an int in [1, 8], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("lex", "count"):
        raise ValueError(f"p4 must be one of ('lex', 'count'), got {p4!r}")
    if isinstance(x, str):
        items = x.split()
    elif isinstance(x, (list, tuple)):
        items = [str(item) for item in x]
    elif isinstance(x, dict):
        items = [f"{key} {value}" for key, value in x.items()]
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        items = [str(x)]
    else:
        raise ValueError(f"x must be str, list, dict or number, got {x!r}")
    cleaned = [item.strip().casefold() if p3 else item.strip() for item in items]
    cleaned = [item for item in cleaned if item]
    if not cleaned:
        raise ValueError(f"x must contain a non-empty item, got {x!r}")
    truncated, cleaned = len(cleaned) > p2, cleaned[:p2]
    buckets = {}
    for item in cleaned:
        buckets.setdefault(item[:p1], []).append(item)
    ordered = sorted(buckets.items(),
                     key=(lambda pair: pair[0]) if p4 == "lex"
                     else (lambda pair: (-len(pair[1]), pair[0])))
    listing = [{"key": key, "size": len(members), "members": members[:8]}
               for key, members in ordered[:20]]
    singles = sum(1 for members in buckets.values() if len(members) == 1)
    return {
        "prefix": p1, "items": len(cleaned), "clusters": len(buckets),
        "cluster_list": listing, "largest": listing[0] if listing else None,
        "singleton_ratio": round(singles / len(buckets), 4) if buckets else 0.0,
        "truncated": truncated,
    }


class TinyPrefixClusterTool(Tool):
    """Fully offline text reasoning component (au1k #5).

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

    label: str = Field(default="au1k#5", description="series provenance label")

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
            "index": 5,
            "algo": 'au_algo_005',
            "semantic": 'tiny_prefix_cluster',
            "category": 'text',
            "docnote": '1-char prefix clusters over 10 items, lex order',
            "params": {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'lex'},
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
        p4 = p4 if p4 is not None else 'lex'
        if action == "run":
            result = au_algo_005(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 1, 'p2': 10, 'p3': True, 'p4': 'lex'})
        canned = {'p1': 2}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_005(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

