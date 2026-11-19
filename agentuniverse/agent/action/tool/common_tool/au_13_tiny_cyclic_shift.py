"""TinyCyclicShiftTool: identity shifts up to 2 over 12 chars, casefold on (au1k series #13, sequence)."""

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


def au_algo_013(x, p1=8, p2=120, p3=True, p4="identity") -> dict:
    """Test cyclic shifts of a text against a character map.

    Rotates the text by every shift in ``1..p1`` and reports whether each
    rotation is a fixed point of the chosen map, plus the minimal period, which
    is how repetitive identifiers are detected.

    Args:
        x: str, list, dict or number; lists/dicts are concatenated into the text.
        p1: Maximum shift in characters, bounds [1, 64].
        p2: Characters considered, bounds [8, 2000].
        p3: When True the text is casefolded before rotation.
        p4: Map vocabulary, "identity", "reverse", "rot13" or "swapcase".

    Returns:
        dict with ``map``, ``length``, ``max_shift``, ``tested``, ``fixed_points``,
        ``periodic_shifts``, ``min_period``, ``samples`` (<=10 ``{"shift",
        "text", "fixed"}``), ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non str/list/dict/number x, a
            blank text or fewer than two surviving characters; the offending
            value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 64):
        raise ValueError(f"p1 must be an int in [1, 64], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 8 <= p2 <= 2000):
        raise ValueError(f"p2 must be an int in [8, 2000], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("identity", "reverse", "rot13", "swapcase"):
        raise ValueError(f"p4 must be 'identity', 'reverse', 'rot13' or"
                         f" 'swapcase', got {p4!r}")
    if isinstance(x, str):
        text = x
    elif isinstance(x, (list, tuple)):
        text = "".join(str(item) for item in x)
    elif isinstance(x, dict):
        text = "".join(f"{key}{value}" for key, value in x.items())
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        text = str(x)
    else:
        raise ValueError(f"x must be str, list, dict or number, got {x!r}")
    work = text.casefold() if p3 else text
    truncated, work = len(work) > p2, work[:p2]
    if not work.strip() or len(work) < 2:
        raise ValueError(f"x must keep two non-space characters, got {x!r}")
    table = str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
                          "nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM")
    mappers = {"identity": lambda value: value, "reverse": lambda value: value[::-1],
               "rot13": lambda value: value.translate(table),
               "swapcase": lambda value: value.swapcase()}
    mapper = mappers[p4]
    samples = []
    for shift in range(1, min(p1, len(work) - 1) + 1):
        rotated = work[shift:] + work[:shift]
        samples.append({"shift": shift, "text": rotated[:32],
                        "fixed": mapper(rotated) == rotated})
    min_period = next((shift for shift in range(1, len(work))
                       if work == work[shift:] + work[:shift]), len(work))
    return {
        "map": p4, "length": len(work), "max_shift": p1, "tested": len(samples),
        "fixed_points": sum(1 for sample in samples if sample["fixed"]),
        "periodic_shifts": sum(1 for sample in samples
                               if sample["text"] == work[:32]),
        "min_period": min_period, "samples": samples[:10], "truncated": truncated,
    }


class TinyCyclicShiftTool(Tool):
    """Fully offline sequence reasoning component (au1k #13).

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

    label: str = Field(default="au1k#13", description="series provenance label")

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
            "index": 13,
            "algo": 'au_algo_013',
            "semantic": 'tiny_cyclic_shift',
            "category": 'sequence',
            "docnote": 'identity shifts up to 2 over 12 chars, casefold on',
            "params": {'p1': 2, 'p2': 12, 'p3': True, 'p4': 'identity'},
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
        p1 = p1 if p1 is not None else 2
        p2 = p2 if p2 is not None else 12
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'identity'
        if action == "run":
            result = au_algo_013(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 2, 'p2': 12, 'p3': True, 'p4': 'identity'})
        canned = {'p1': 3}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_013(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

