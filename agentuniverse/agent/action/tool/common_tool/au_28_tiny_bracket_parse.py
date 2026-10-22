"""TinyBracketParseTool: round bracket scan, depth cap 3, 20 chars, quotes skipped on (au1k series #28, structural)."""

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


def au_algo_028(x, p1=12, p2=400, p3=True, p4="all") -> dict:
    """Parse bracket nesting with a stack and report the first defect.

    Args:
        x: str, list, dict or number; lists/dicts flatten to a joined text view.
        p1: Maximum accepted nesting depth, bounds [1, 50].
        p2: Characters inspected, bounds [2, 2000].
        p3: When True characters inside single or double quotes are skipped.
        p4: Alphabet vocabulary, "round" (only "()") or "all" (also "[]" and "{}").

    Returns:
        dict with ``alphabet``, ``ok``, ``pairs``, ``max_depth``, ``over_depth``,
        ``first_error``, ``unclosed`` (<=10), ``depth_profile`` (<=40), ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a non str/list/dict/number x, or a blank
            text view; the offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 50):
        raise ValueError(f"p1 must be an int in [1, 50], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 2 <= p2 <= 2000):
        raise ValueError(f"p2 must be an int in [2, 2000], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("round", "all"):
        raise ValueError(f"p4 must be 'round' or 'all', got {p4!r}")
    if isinstance(x, str):
        text = x
    elif isinstance(x, (list, tuple)):
        text = " ".join(str(item) for item in x)
    elif isinstance(x, dict):
        text = " ".join(f"{key}={value}" for key, value in x.items())
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        text = str(x)
    else:
        raise ValueError(f"x must be str, list, dict or number, got {x!r}")
    if not text.strip():
        raise ValueError(f"x must contain a non-space character, got {x!r}")
    truncated, work = len(text) > p2, text[:p2]
    pairs = {"(": ")"} if p4 == "round" else {"(": ")", "[": "]", "{": "}"}
    closers = {value: key for key, value in pairs.items()}
    stack, profile, matched, first_error, quote = [], [], 0, None, None
    for index, char in enumerate(work):
        if p3 and quote:
            quote = None if char == quote else quote
            continue
        if p3 and char in "'\"":
            quote = char
        elif char in pairs:
            stack.append((char, index))
            profile.append(len(stack))
        elif char in closers:
            profile.append(max(len(stack) - 1, 0))
            if not stack:
                first_error = first_error or {"index": index, "char": char, "reason": "closer_without_opener"}
            elif stack[-1][0] != closers[char]:
                first_error = first_error or {"index": index, "char": char,
                                              "reason": f"mismatch_with_{stack[-1][0]}_at_{stack[-1][1]}"}
                stack.pop()
            else:
                stack.pop()
                matched += 1
    if stack and not first_error:
        first_error = {"index": stack[-1][1], "char": stack[-1][0], "reason": "unclosed_opener"}
    return {
        "alphabet": p4, "ok": first_error is None, "pairs": matched,
        "max_depth": max(profile, default=0), "over_depth": max(profile, default=0) > p1,
        "first_error": first_error, "unclosed": [opener for opener, _ in stack][:10],
        "depth_profile": profile[:40], "truncated": truncated,
    }


class TinyBracketParseTool(Tool):
    """Fully offline structural reasoning component (au1k #28).

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

    label: str = Field(default="au1k#28", description="series provenance label")

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
            "index": 28,
            "algo": 'au_algo_028',
            "semantic": 'tiny_bracket_parse',
            "category": 'structural',
            "docnote": 'round bracket scan, depth cap 3, 20 chars, quotes skipped on',
            "params": {'p1': 3, 'p2': 20, 'p3': True, 'p4': 'round'},
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
        p1 = p1 if p1 is not None else 3
        p2 = p2 if p2 is not None else 20
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'round'
        if action == "run":
            result = au_algo_028(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 3, 'p2': 20, 'p3': True, 'p4': 'round'})
        canned = {'p1': 4}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_028(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

