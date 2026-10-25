"""TinyRhymeClusterTool: 1-char rhyme keys, plain mode, 10 items, casefold on (au1k series #6, text)."""

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


def au_algo_006(x, p1=3, p2=80, p3=True, p4="plain") -> dict:
    """Group tokens by a trailing rhyme key and report rhyme density.

    Args:
        x: str, list, dict or number; a list stays an ordered item list.
        p1: Suffix length in characters, bounds [1, 8].
        p2: Items considered, bounds [1, 200].
        p3: When True tokens are casefolded before keying.
        p4: Key vocabulary, "plain" or "vowel_stripped" (silent vowels dropped).

    Returns:
        dict with ``mode``, ``suffix``, ``items``, ``clusters``, ``rhyme_density``,
        ``perfect_groups`` (<=20 ``{"key", "size", "members"}``), ``near_pairs``
        (<=10 ``{"left", "right", "nucleus"}``), ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 bound or vocabulary violation, on a non
            str/list/dict/number x, or when no token survives normalisation;
            the offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 8):
        raise ValueError(f"p1 must be an int in [1, 8], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("plain", "vowel_stripped"):
        raise ValueError(f"p4 must be 'plain' or 'vowel_stripped', got {p4!r}")
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
    cleaned = [item.strip().strip(".,;:!?\"'") for item in items]
    cleaned = [item.casefold() if p3 else item for item in cleaned if item]
    if not cleaned:
        raise ValueError(f"x must contain a non-empty item, got {x!r}")
    truncated, cleaned = len(cleaned) > p2, cleaned[:p2]
    groups, nuclei = {}, {}
    for word in cleaned:
        stem = (word.rstrip("aeiouy") or word) if p4 == "vowel_stripped" else word
        groups.setdefault(stem[-p1:], []).append(word)
        vowels = re.findall(r"[aeiouy]+", word)
        nuclei[word] = (vowels[-1] if vowels else "") + word[-1:]
    ordered = sorted(groups.items(), key=lambda pair: (-len(pair[1]), pair[0]))
    near, seen = [], set()
    for index, left in enumerate(cleaned):
        for right in cleaned[index + 1:]:
            if nuclei[left] == nuclei[right] and left[-p1:] != right[-p1:]:
                signature = tuple(sorted((left, right)))
                if signature not in seen:
                    seen.add(signature)
                    near.append({"left": left, "right": right,
                                 "nucleus": nuclei[left]})
    return {
        "mode": p4, "suffix": p1, "items": len(cleaned), "clusters": len(groups),
        "rhyme_density": round(sum(1 for members in groups.values()
                                   if len(members) > 1) / len(groups), 4),
        "perfect_groups": [{"key": key, "size": len(members), "members": members[:8]}
                           for key, members in ordered[:20]],
        "near_pairs": near[:10], "truncated": truncated,
    }


class TinyRhymeClusterTool(Tool):
    """Fully offline text reasoning component (au1k #6).

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

    label: str = Field(default="au1k#6", description="series provenance label")

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
            "index": 6,
            "algo": 'au_algo_006',
            "semantic": 'tiny_rhyme_cluster',
            "category": 'text',
            "docnote": '1-char rhyme keys, plain mode, 10 items, casefold on',
            "params": {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'plain'},
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
        p4 = p4 if p4 is not None else 'plain'
        if action == "run":
            result = au_algo_006(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 1, 'p2': 10, 'p3': True, 'p4': 'plain'})
        canned = {'p1': 2}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_006(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

