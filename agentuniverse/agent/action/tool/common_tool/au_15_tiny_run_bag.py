"""TinyRunBagTool: encode run bag, min run 1, 10 tokens, merged on (au1k series #15, sequence)."""

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


def au_algo_015(x, p1=2, p2=80, p3=True, p4="encode") -> dict:
    """Run-length encode a token stream or collapse it into a bag.

    With ``p3`` True order is preserved and equal neighbours fold into one run;
    with ``p3`` False the order is dropped and the result is a multiplicity bag.

    Args:
        x: str, list, dict or number giving the token stream.
        p1: Minimum run length reported, bounds [1, 20].
        p2: Tokens considered, bounds [1, 200].
        p3: When True adjacent duplicates merge and order is preserved.
        p4: Output vocabulary, "encode" (per-segment runs) or "summary" (adds a
            run-length histogram).

    Returns:
        dict with ``mode``, ``merged``, ``tokens``, ``segments``, ``runs`` (<=20),
        ``longest_run``, ``distinct``, ``repeat_ratio``, ``run_histogram``,
        ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non str/list/dict/number x, or
            an empty token stream; the offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 20):
        raise ValueError(f"p1 must be an int in [1, 20], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("encode", "summary"):
        raise ValueError(f"p4 must be 'encode' or 'summary', got {p4!r}")
    if isinstance(x, str):
        tokens = x.split()
    elif isinstance(x, (list, tuple)):
        tokens = [str(item) for item in x]
    elif isinstance(x, dict):
        tokens = [part for pair in x.items() for part in (str(pair[0]), str(pair[1]))]
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        tokens = [str(x)]
    else:
        raise ValueError(f"x must be str, list, dict or number, got {x!r}")
    if not tokens:
        raise ValueError(f"x must contain a token, got {x!r}")
    truncated, tokens = len(tokens) > p2, tokens[:p2]
    segments = []
    for token in tokens:
        if p3 and segments and segments[-1][0] == token:
            segments[-1][1] += 1
        else:
            segments.append([token, 1])
    if not p3:
        counts = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
        segments = sorted(([t, c] for t, c in counts.items()),
                          key=lambda pair: (-pair[1], pair[0]))
    histogram = {}
    for _, count in segments:
        histogram[str(count)] = histogram.get(str(count), 0) + 1
    return {
        "mode": p4, "merged": p3, "tokens": len(tokens), "segments": len(segments),
        "runs": [{"token": t, "count": c} for t, c in segments
                 if c >= p1][:20],
        "longest_run": max(count for _, count in segments),
        "distinct": len({token for token in tokens}),
        "repeat_ratio": round(sum(count for _, count in segments if count > 1)
                              / len(tokens), 4),
        "run_histogram": histogram if p4 == "summary" else {},
        "truncated": truncated,
    }


class TinyRunBagTool(Tool):
    """Fully offline sequence reasoning component (au1k #15).

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

    label: str = Field(default="au1k#15", description="series provenance label")

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
            "index": 15,
            "algo": 'au_algo_015',
            "semantic": 'tiny_run_bag',
            "category": 'sequence',
            "docnote": 'encode run bag, min run 1, 10 tokens, merged on',
            "params": {'p1': 1, 'p2': 10, 'p3': True, 'p4': 'encode'},
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
        p4 = p4 if p4 is not None else 'encode'
        if action == "run":
            result = au_algo_015(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 1, 'p2': 10, 'p3': True, 'p4': 'encode'})
        canned = {'p1': 2}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_015(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

