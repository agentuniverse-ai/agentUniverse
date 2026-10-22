"""TinyCollationOrderTool: casefold collation of 20 keys truncated at 4 chars (au1k series #7, text)."""

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


def au_algo_007(x, p1=24, p2=150, p3=True, p4="casefold") -> dict:
    """Build a collation sketch: ordering, inversions and duplicate keys.

    Args:
        x: str, list, dict or number; a dict contributes its keys.
        p1: Key truncation width in characters, bounds [1, 32].
        p2: Items considered, bounds [1, 200].
        p3: When True ties keep input order, else they sort by original text.
        p4: Collation vocabulary: "casefold", "case_sensitive" or "numeric".

    Returns:
        dict with ``policy``, ``items``, ``order`` (<=20), ``first``, ``last``, ``inversions``,
        ``adjacent_ordered``, ``duplicate_groups``, ``sorted_ratio``, ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non str/list/dict/number x, or
            an empty item list; the offending value is quoted.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 32):
        raise ValueError(f"p1 must be an int in [1, 32], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("casefold", "case_sensitive", "numeric"):
        raise ValueError(f"p4 must be 'casefold', 'case_sensitive' or 'numeric',"
                         f" got {p4!r}")
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
    if not items:
        raise ValueError(f"x must contain an item, got {x!r}")
    truncated, items = len(items) > p2, items[:p2]

    def collation_key(text):
        """Derive the bounded sort key for one item under the active policy."""
        if p4 == "case_sensitive":
            return (text[:p1],)
        if p4 == "casefold":
            return (text[:p1].casefold(),)
        return tuple((0, int(piece), "") if piece.isdigit() else (1, 0, piece)
                     for piece in re.findall(r"\d+|\D+", text[:p1].casefold()))

    keyed = [(collation_key(item), position, item) for position, item in enumerate(items)]
    ordered = sorted(keyed, key=(lambda entry: (entry[0], entry[1])) if p3
                     else (lambda entry: (entry[0], entry[2])))
    inversions = sum(1 for left in range(len(keyed)) for right in range(left + 1, len(keyed))
                     if keyed[left][0] > keyed[right][0])
    collisions = {}
    for key, _, item in keyed:
        collisions.setdefault(repr(key), []).append(item)
    names = [entry[2] for entry in ordered]
    return {
        "policy": p4, "items": len(items), "order": names[:20],
        "first": names[0], "last": names[-1], "inversions": inversions,
        "adjacent_ordered": sum(1 for index in range(len(ordered) - 1)
                                if ordered[index][0] <= ordered[index + 1][0]),
        "duplicate_groups": [{"key": group[0], "count": len(group)} for _, group
                             in sorted(collisions.items()) if len(group) > 1][:10],
        "sorted_ratio": (round(1.0 - inversions / (len(items) * (len(items) - 1) / 2), 4)
                         if len(items) > 1 else 1.0),
        "truncated": truncated,
    }


class TinyCollationOrderTool(Tool):
    """Fully offline text reasoning component (au1k #7).

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

    label: str = Field(default="au1k#7", description="series provenance label")

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
            "index": 7,
            "algo": 'au_algo_007',
            "semantic": 'tiny_collation_order',
            "category": 'text',
            "docnote": 'casefold collation of 20 keys truncated at 4 chars',
            "params": {'p1': 4, 'p2': 20, 'p3': True, 'p4': 'casefold'},
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
        p2 = p2 if p2 is not None else 20
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'casefold'
        if action == "run":
            result = au_algo_007(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 4, 'p2': 20, 'p3': True, 'p4': 'casefold'})
        canned = {'p1': 5}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_007(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

