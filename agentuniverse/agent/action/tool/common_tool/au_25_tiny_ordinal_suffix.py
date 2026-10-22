"""TinyOrdinalSuffixTool: short ordinals up to 100, 10 numbers, number shown on (au1k series #25, structural)."""

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


def au_algo_025(x, p1=1000, p2=40, p3=True, p4="short") -> dict:
    """Format integers with English ordinal suffixes.

    The suffix rules are the classic ones: 1st, 2nd, 3rd, but 11th, 12th and 13th
    take "th". ``p4`` selects casing and zero padding.

    Args:
        x: number, list of numbers, dict of numbers or a numeric string.
        p1: Maximum accepted magnitude, bounds [1, 1000000].
        p2: Items considered, bounds [1, 200].
        p3: When True the number is prefixed ("21st"), else only "st" is returned.
        p4: Style vocabulary, "short", "upper" or "padded" (zero-filled to the
            width of ``p1``).

    Returns:
        dict with ``style``, ``items``, ``formatted`` (<=20 strings),
        ``suffix_counts``, ``teen_exceptions``, ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non integer item, or a magnitude
            above ``p1``; the offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 1000000):
        raise ValueError(f"p1 must be an int in [1, 1000000], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("short", "upper", "padded"):
        raise ValueError(f"p4 must be 'short', 'upper' or 'padded', got {p4!r}")
    if isinstance(x, dict):
        raw = list(x.values())
    elif isinstance(x, str):
        raw = [chunk for chunk in re.split(r"[,;\s]+", x.strip()) if chunk]
    elif isinstance(x, (list, tuple)):
        raw = list(x)
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        raw = [x]
    else:
        raise ValueError(f"x must be numeric or a numeric sequence, got {x!r}")
    truncated, raw = len(raw) > p2, raw[:p2]
    formatted, counts, teens, width = [], {}, 0, len(str(p1))
    for item in raw:
        if isinstance(item, bool):
            raise ValueError(f"x items must be integers, got {item!r}")
        try:
            number = int(item)
        except (TypeError, ValueError):
            raise ValueError(f"x items must be integers, got {item!r}")
        if abs(number) > p1:
            raise ValueError(f"x items must not exceed {p1}, got {item!r}")
        tail = abs(number) % 100
        if 11 <= tail <= 13:
            suffix, teens = "th", teens + 1
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(abs(number) % 10, "th")
        counts[suffix] = counts.get(suffix, 0) + 1
        body = (suffix.upper() if p4 == "upper" else
                str(number).zfill(width) + suffix if p4 == "padded" else suffix)
        formatted.append(f"{number}{body}" if p3 else body)
    return {
        "style": p4, "items": len(formatted), "formatted": formatted[:20],
        "suffix_counts": counts, "teen_exceptions": teens, "truncated": truncated,
    }


class TinyOrdinalSuffixTool(Tool):
    """Fully offline structural reasoning component (au1k #25).

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

    label: str = Field(default="au1k#25", description="series provenance label")

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
            "index": 25,
            "algo": 'au_algo_025',
            "semantic": 'tiny_ordinal_suffix',
            "category": 'structural',
            "docnote": 'short ordinals up to 100, 10 numbers, number shown on',
            "params": {'p1': 100, 'p2': 10, 'p3': True, 'p4': 'short'},
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
        p1 = p1 if p1 is not None else 100
        p2 = p2 if p2 is not None else 10
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'short'
        if action == "run":
            result = au_algo_025(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 100, 'p2': 10, 'p3': True, 'p4': 'short'})
        canned = {'p1': 101}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_025(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

