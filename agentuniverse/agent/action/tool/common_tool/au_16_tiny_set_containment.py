"""TinySetContainmentTool: jaccard containment of two 5-token sides, min length 1, casefold on (au1k series #16, sequence)."""

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


def au_algo_016(x, p1=2, p2=60, p3=True, p4="jaccard") -> dict:
    """Measure set containment between two halves of one token list.

    The token "||" splits the input into set A and set B; without it the list is
    split at the midpoint. The score plus the tokens carried by only one side is
    the shape of a coverage or drift review.

    Args:
        x: list of tokens, a "||"-separated string, or a dict whose keys are set
            A and whose values are set B.
        p1: Minimum token length kept, bounds [1, 20].
        p2: Tokens kept per side, bounds [2, 200].
        p3: When True tokens are casefolded and stripped before comparison.
        p4: Score vocabulary, "jaccard", "dice" or "overlap" (share of the
            smaller side).

    Returns:
        dict with ``metric``, ``a_size``, ``b_size``, ``intersection``, ``union``,
        ``score``, ``only_a`` (<=10), ``only_b`` (<=10), ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non list/str/dict x, a string
            without "||", or a side that filters down to nothing; the offending
            value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 20):
        raise ValueError(f"p1 must be an int in [1, 20], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 2 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [2, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("jaccard", "dice", "overlap"):
        raise ValueError(f"p4 must be 'jaccard', 'dice' or 'overlap', got {p4!r}")
    if isinstance(x, dict):
        left_raw = [str(key) for key in x]
        right_raw = [str(value) for value in x.values()]
    elif isinstance(x, str):
        if "||" not in x:
            raise ValueError(f"x must contain the '||' separator, got {x!r}")
        left_raw, right_raw = (part.split() for part in x.split("||", 1))
    elif isinstance(x, (list, tuple)):
        items = [str(item) for item in x]
        cut = items.index("||") if "||" in items else len(items) // 2
        left_raw, right_raw = items[:cut], items[cut + (1 if "||" in items else 0):]
    else:
        raise ValueError(f"x must be a list, str or dict, got {x!r}")
    clean = lambda values: [(value.strip().casefold() if p3 else value.strip())
                            for value in values
                            if len(value.strip()) >= p1][:p2]
    left, right = set(clean(left_raw)), set(clean(right_raw))
    if not left or not right:
        raise ValueError(f"x must yield two non-empty sides, got {x!r}")
    shared = left & right
    score = {"jaccard": lambda: len(shared) / len(left | right),
             "dice": lambda: 2 * len(shared) / (len(left) + len(right)),
             "overlap": lambda: len(shared) / min(len(left), len(right))}[p4]()
    return {
        "metric": p4, "a_size": len(left), "b_size": len(right),
        "intersection": len(shared), "union": len(left | right),
        "score": round(score, 4), "only_a": sorted(left - right)[:10],
        "only_b": sorted(right - left)[:10],
        "truncated": len(left_raw) > p2 or len(right_raw) > p2,
    }


class TinySetContainmentTool(Tool):
    """Fully offline sequence reasoning component (au1k #16).

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

    label: str = Field(default="au1k#16", description="series provenance label")

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
            "index": 16,
            "algo": 'au_algo_016',
            "semantic": 'tiny_set_containment',
            "category": 'sequence',
            "docnote": 'jaccard containment of two 5-token sides, min length 1, casefold on',
            "params": {'p1': 1, 'p2': 5, 'p3': True, 'p4': 'jaccard'},
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
        p2 = p2 if p2 is not None else 5
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'jaccard'
        if action == "run":
            result = au_algo_016(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 1, 'p2': 5, 'p3': True, 'p4': 'jaccard'})
        canned = {'p1': 2}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_016(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

