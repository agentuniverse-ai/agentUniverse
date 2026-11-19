"""TinyBalancePointTool: len mass balance split, 2% tolerance, 50-char scan (au1k series #8, text)."""

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


def au_algo_008(x, p1=400, p2=12, p3=True, p4="len") -> dict:
    """Find the index at which prefix mass and suffix mass balance.

    Args:
        x: str, list, dict or number; lists/dicts flatten to a joined text view.
        p1: Characters scanned, bounds [1, 2000].
        p2: Accepted imbalance in percent of total mass, bounds [0, 100].
        p3: When True the earliest acceptable split wins, else the latest.
        p4: Mass vocabulary: "len", "vowel" (vowels weigh 2) or "word".

    Returns:
        dict with ``metric``, ``index`` (-1 when nothing fits), ``found``,
        ``left_mass``, ``right_mass``, ``imbalance``, ``candidates``, ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 bound or vocabulary violation, on a non
            str/list/dict/number x, or on a blank text view; the offending value
            is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 2000):
        raise ValueError(f"p1 must be an int in [1, 2000], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 0 <= p2 <= 100):
        raise ValueError(f"p2 must be an int in [0, 100], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("len", "vowel", "word"):
        raise ValueError(f"p4 must be 'len', 'vowel' or 'word', got {p4!r}")
    if isinstance(x, str):
        text = x
    elif isinstance(x, (list, tuple)):
        text = " ".join(str(item) for item in x)
    elif isinstance(x, dict):
        text = " ".join(f"{key} {value}" for key, value in x.items())
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        text = str(x)
    else:
        raise ValueError(f"x must be str, list, dict or number, got {x!r}")
    if not text.strip():
        raise ValueError(f"x must contain a non-space character, got {x!r}")
    truncated, work = len(text) > p1, text[:p1]
    if p4 == "word":
        matches = list(re.finditer(r"\S+", work))
        positions = [match.end() for match in matches]
        weights = [len(match.group(0)) for match in matches]
    else:
        positions = list(range(1, len(work) + 1))
        weights = ([2 if char.lower() in "aeiou" else 1 for char in work]
                   if p4 == "vowel" else [1] * len(work))
    total = sum(weights)
    if not total:
        raise ValueError(f"x must contain measurable mass, got {x!r}")
    best, best_gap, best_left, candidates, running = None, None, 0, 0, 0
    for offset, position in enumerate(positions):
        running += weights[offset]
        gap = abs(running - (total - running)) / total * 100.0
        if gap <= p2:
            candidates += 1
            if best_gap is None or gap < best_gap - 1e-12 or (
                    not p3 and abs(gap - best_gap) <= 1e-12):
                best, best_gap, best_left = position, gap, running
    if best is None:
        return {"metric": p4, "index": -1, "found": False, "left_mass": 0,
                "right_mass": total, "imbalance": 100.0, "candidates": 0,
                "truncated": truncated}
    return {
        "metric": p4, "index": best, "found": True, "left_mass": best_left,
        "right_mass": total - best_left,
        "imbalance": round(abs(best_left - (total - best_left)) / total * 100.0, 4),
        "candidates": candidates, "truncated": truncated,
    }


class TinyBalancePointTool(Tool):
    """Fully offline text reasoning component (au1k #8).

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

    label: str = Field(default="au1k#8", description="series provenance label")

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
            "index": 8,
            "algo": 'au_algo_008',
            "semantic": 'tiny_balance_point',
            "category": 'text',
            "docnote": 'len mass balance split, 2% tolerance, 50-char scan',
            "params": {'p1': 50, 'p2': 2, 'p3': True, 'p4': 'len'},
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
        p1 = p1 if p1 is not None else 50
        p2 = p2 if p2 is not None else 2
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'len'
        if action == "run":
            result = au_algo_008(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 50, 'p2': 2, 'p3': True, 'p4': 'len'})
        canned = {'p1': 51}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_008(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

