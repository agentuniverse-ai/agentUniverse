"""TinyDedupeSketchTool: shingle near-duplicate sketch, shingle 1, 10 paragraphs (au1k series #10, text)."""

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


def au_algo_010(x, p1=3, p2=60, p3=True, p4="shingle") -> dict:
    """Sketch near-duplicate paragraphs with token shingles.

    Args:
        x: str, list, dict or number; list items become separate paragraphs.
        p1: Shingle size in tokens, bounds [1, 6].
        p2: Paragraphs considered, bounds [1, 200].
        p3: When True paragraphs are casefolded before shingling.
        p4: Comparison vocabulary, "shingle" (Jaccard) or "prefix".

    Returns:
        dict with ``mode``, ``paragraphs``, ``kept``, ``duplicates``,
        ``duplicate_ratio``, ``groups`` (<=20), ``signatures`` (<=10), ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non str/list/dict/number x,
            or when no paragraph survives; the offending value is quoted.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 6):
        raise ValueError(f"p1 must be an int in [1, 6], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("shingle", "prefix"):
        raise ValueError(f"p4 must be 'shingle' or 'prefix', got {p4!r}")
    if isinstance(x, str):
        text = x
    elif isinstance(x, (list, tuple)):
        text = "\n".join(str(item) for item in x)
    elif isinstance(x, dict):
        text = "\n".join(f"{key} {value}" for key, value in x.items())
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        text = str(x)
    else:
        raise ValueError(f"x must be str, list, dict or number, got {x!r}")
    blocks = re.split(r"\n\s*\n", text.strip())
    if len(blocks) < 2:
        blocks = [line for line in text.splitlines() if line.strip()]
    paragraphs = [(item.strip().casefold() if p3 else item.strip()).split()
                  for item in blocks]
    paragraphs = [tokens for tokens in paragraphs if tokens]
    if not paragraphs:
        raise ValueError(f"x must contain a paragraph, got {x!r}")
    truncated, paragraphs = len(paragraphs) > p2, paragraphs[:p2]
    kept, groups = [], []
    for index, tokens in enumerate(paragraphs):
        signature = (set(tuple(tokens[o:o + p1])
                         for o in range(max(len(tokens) - p1 + 1, 1)))
                     if p4 == "shingle" else {tuple(tokens[:p1])})
        match, best = None, 0.0
        for kept_index, (previous, _) in enumerate(kept):
            union = signature | previous
            overlap = len(signature & previous) / len(union) if union else 1.0
            if overlap > best:
                best, match = overlap, kept_index
        if match is not None and best >= 0.5:
            groups.append({"kept": match + 1, "drop": index + 1,
                           "overlap": round(best, 4)})
        else:
            kept.append((signature, index))
    return {
        "mode": p4, "paragraphs": len(paragraphs), "kept": len(kept),
        "duplicates": len(groups),
        "duplicate_ratio": round(len(groups) / len(paragraphs), 4),
        "groups": groups[:20],
        "signatures": [" ".join(paragraphs[position])[:60]
                       for _, position in kept[:10]],
        "truncated": truncated,
    }


class TinyDedupeSketchTool(Tool):
    """Fully offline text reasoning component (au1k #10).

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

    label: str = Field(default="au1k#10", description="series provenance label")

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
            "index": 10,
            "algo": 'au_algo_010',
            "semantic": 'tiny_dedupe_sketch',
            "category": 'text',
            "docnote": 'shingle near-duplicate sketch, shingle 1, 10 paragraphs',
            "params": {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'shingle'},
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
        p4 = p4 if p4 is not None else 'shingle'
        if action == "run":
            result = au_algo_010(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 1, 'p2': 10, 'p3': True, 'p4': 'shingle'})
        canned = {'p1': 2}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_010(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

