"""TinyRomanNumeralTool: canonical Roman numerals, cap 100, 5 items, strict on (au1k series #23, structural)."""

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


def au_algo_023(x, p1=3999, p2=40, p3=True, p4="canonical") -> dict:
    """Parse Roman numerals, validate their form and re-encode them.

    Args:
        x: list, number or string of Roman numerals (split on commas or spaces).
        p1: Maximum accepted value, bounds [1, 3999].
        p2: Numerals considered, bounds [1, 100].
        p3: When True the input must be the canonical subtractive form (IV, IX,
            XL); when False any well-formed numeral is accepted (IIII, VIIII).
        p4: Output style, "canonical" (subtractive) or "additive" (IIII, VIIII).

    Returns:
        dict with ``style``, ``strict``, ``numerals``, ``results`` (<=20
        ``{"input", "value", "roman"}``), ``total``, ``largest``, ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a character outside "IVXLCDM", a value
            outside [1, ``p1``], or a non-canonical numeral; the value is quoted.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 3999):
        raise ValueError(f"p1 must be an int in [1, 3999], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 100):
        raise ValueError(f"p2 must be an int in [1, 100], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("canonical", "additive"):
        raise ValueError(f"p4 must be 'canonical' or 'additive', got {p4!r}")
    if isinstance(x, str):
        raw = [chunk for chunk in re.split(r"[,;\s]+", x.strip()) if chunk]
    elif isinstance(x, (list, tuple)):
        raw = [str(item) for item in x]
    else:
        raise ValueError(f"x must be a str or list of Roman numerals, got {x!r}")
    if not raw:
        raise ValueError(f"x must provide a numeral, got {x!r}")
    truncated, raw = len(raw) > p2, raw[:p2]
    pairs = (("M", 1000), ("CM", 900), ("D", 500), ("CD", 400), ("C", 100), ("XC", 90),
             ("L", 50), ("XL", 40), ("X", 10), ("IX", 9), ("V", 5), ("IV", 4), ("I", 1))
    ladder = pairs if p4 == "canonical" else tuple(pair for pair in pairs if len(pair[0]) == 1)
    results = []
    for item in raw:
        upper = item.strip().upper()
        if any(char not in "IVXLCDM" for char in upper):
            raise ValueError(f"x must be IVXLCDM only, got {item!r}")
        value, cursor = 0, 0
        while cursor < len(upper):
            symbol, weight = next(pair for pair in pairs if upper.startswith(pair[0], cursor))
            value, cursor = value + weight, cursor + len(symbol)
        if not 1 <= value <= p1:
            raise ValueError(f"x value outside [1, {p1}], got {item!r}")
        remaining, parts = value, []
        for symbol, weight in ladder:
            while remaining >= weight:
                parts.append(symbol)
                remaining -= weight
        roman = "".join(parts)
        if p3:
            strict_parts, strict_remaining = [], value
            for symbol, weight in pairs:
                while strict_remaining >= weight:
                    strict_parts.append(symbol)
                    strict_remaining -= weight
            if "".join(strict_parts) != upper:
                raise ValueError(f"x numeral is not canonical, got {item!r}")
        results.append({"input": item, "value": value, "roman": roman})
    return {
        "style": p4, "strict": p3, "numerals": len(results), "results": results[:20],
        "total": sum(entry["value"] for entry in results),
        "largest": max(entry["value"] for entry in results), "truncated": truncated,
    }


class TinyRomanNumeralTool(Tool):
    """Fully offline structural reasoning component (au1k #23).

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

    label: str = Field(default="au1k#23", description="series provenance label")

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
            "index": 23,
            "algo": 'au_algo_023',
            "semantic": 'tiny_roman_numeral',
            "category": 'structural',
            "docnote": 'canonical Roman numerals, cap 100, 5 items, strict on',
            "params": {'p1': 100, 'p2': 5, 'p3': True, 'p4': 'canonical'},
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
        p2 = p2 if p2 is not None else 5
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'canonical'
        if action == "run":
            result = au_algo_023(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 100, 'p2': 5, 'p3': True, 'p4': 'canonical'})
        canned = {'p1': 101}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_023(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

