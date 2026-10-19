"""TinyIntervalNameTool: classic interval names up to 12 semitones, 5 items, compound on (au1k series #24, structural)."""

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


def au_algo_024(x, p1=24, p2=40, p3=True, p4="classic") -> dict:
    """Name musical intervals from semitone distances.

    Args:
        x: number, list of numbers, dict of numbers or a numeric string of
            semitone counts.
        p1: Maximum accepted semitone distance, bounds [1, 48].
        p2: Items considered, bounds [1, 100].
        p3: When True octave-exceeding distances are compound, else reduced modulo 12.
        p4: Naming vocabulary, "classic" (full names) or "abbrev" (P5, m3, M7).

    Returns:
        dict with ``style``, ``items``, ``results`` (<=20), ``quality_counts``,
        ``compound_count``, ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non numeric or negative item, or an
            item above ``p1``; the offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 48):
        raise ValueError(f"p1 must be an int in [1, 48], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 100):
        raise ValueError(f"p2 must be an int in [1, 100], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("classic", "abbrev"):
        raise ValueError(f"p4 must be 'classic' or 'abbrev', got {p4!r}")
    if isinstance(x, dict):
        raw = list(x.values())
    elif isinstance(x, str):
        raw = [chunk for chunk in re.split(r"[,;]", x) if chunk.strip()]
    elif isinstance(x, (list, tuple)):
        raw = list(x)
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        raw = [x]
    else:
        raise ValueError(f"x must be numeric or a numeric sequence, got {x!r}")
    values = []
    for item in raw:
        try:
            values.append(float(item))
        except (TypeError, ValueError):
            raise ValueError(f"x items must be numbers, got {item!r}")
    truncated, values = len(values) > p2, values[:p2]
    names = ("unison", "minor 2nd", "major 2nd", "minor 3rd", "major 3rd",
             "perfect 4th", "tritone", "perfect 5th", "minor 6th", "major 6th",
             "minor 7th", "major 7th", "octave")
    short = ("P1", "m2", "M2", "m3", "M3", "P4", "TT", "P5", "m6", "M6", "m7", "M7", "P8")
    quality = ("perfect", "minor", "major", "minor", "major", "perfect", "tritone",
               "perfect", "minor", "major", "minor", "major", "perfect")
    results, counts, compound_count = [], {}, 0
    for value in values:
        semitones = int(value)
        if semitones < 0 or semitones > p1:
            raise ValueError(f"x items must be within [0, {p1}], got {value!r}")
        octaves, remainder = divmod(semitones, 12)
        reduced = remainder if p3 else semitones % 12
        label = names[reduced] if p4 == "classic" else short[reduced]
        if p3 and semitones > 12:
            label = f"{'octave' if octaves == 1 else f'{octaves} octaves'} + {label}"
        compound_count += 1 if semitones > 12 else 0
        counts[quality[reduced]] = counts.get(quality[reduced], 0) + 1
        results.append({"semitones": semitones, "name": label, "quality": quality[reduced],
                        "inversion": 12 - reduced if reduced else 0,
                        "compound": semitones > 12})
    return {
        "style": p4, "items": len(results), "results": results[:20],
        "quality_counts": counts, "compound_count": compound_count,
        "truncated": truncated,
    }


class TinyIntervalNameTool(Tool):
    """Fully offline structural reasoning component (au1k #24).

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

    label: str = Field(default="au1k#24", description="series provenance label")

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
            "index": 24,
            "algo": 'au_algo_024',
            "semantic": 'tiny_interval_name',
            "category": 'structural',
            "docnote": 'classic interval names up to 12 semitones, 5 items, compound on',
            "params": {'p1': 12, 'p2': 5, 'p3': True, 'p4': 'classic'},
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
        p1 = p1 if p1 is not None else 12
        p2 = p2 if p2 is not None else 5
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'classic'
        if action == "run":
            result = au_algo_024(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 12, 'p2': 5, 'p3': True, 'p4': 'classic'})
        canned = {'p1': 13}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_024(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

