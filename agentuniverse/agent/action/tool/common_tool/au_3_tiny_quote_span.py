"""TinyQuoteSpanTool: single-quote span scan, min span 0, 5 spans, offsets on (au1k series #3, text)."""

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


def au_algo_003(x, p1=2, p2=40, p3=True, p4="both") -> dict:
    """Extract quoted spans with an escape-aware single-pass scanner.

    Toggles a span on the selected quote characters, treats a backslash as an
    escape for the next character and drops spans shorter than ``p1``.

    Args:
        x: str, list, dict or number; lists/dicts flatten to a joined text view.
        p1: Minimum span length in characters, bounds [0, 80].
        p2: Spans retained, bounds [1, 200].
        p3: When True each record also carries ``start`` and ``end`` offsets.
        p4: Quote vocabulary, one of "single", "double", "both".

    Returns:
        dict with ``quote``, ``spans`` (<=``p2`` ``{"text", "length"}`` records
        plus offsets when ``p3``), ``span_count``, ``unterminated``,
        ``quote_histogram``, ``min_length``, ``truncated``.

    Raises:
        ValueError: if p1/p2/p3/p4 break the bounds or vocabulary above, if x is
            not a str/list/dict/number, or if the text view is blank; the
            offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 0 <= p1 <= 80):
        raise ValueError(f"p1 must be an int in [0, 80], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("single", "double", "both"):
        raise ValueError(f"p4 must be in ('single', 'double', 'both'), got {p4!r}")
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
    active = {"single": "'", "double": '"', "both": "'\""}[p4]
    spans, histogram = [], {}
    opened, start, escaped = None, 0, False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif opened is None:
            if char in active:
                opened, start = char, index + 1
        elif char == opened:
            body = text[start:index]
            if len(body) >= p1:
                record = {"text": body, "length": len(body)}
                if p3:
                    record.update({"start": start, "end": index})
                spans.append(record)
                histogram[opened] = histogram.get(opened, 0) + 1
            opened = None
    return {
        "quote": p4, "spans": spans[:p2], "span_count": len(spans),
        "unterminated": 1 if opened is not None else 0,
        "quote_histogram": histogram, "min_length": p1,
        "truncated": len(spans) > p2,
    }


class TinyQuoteSpanTool(Tool):
    """Fully offline text reasoning component (au1k #3).

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

    label: str = Field(default="au1k#3", description="series provenance label")

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
            "index": 3,
            "algo": 'au_algo_003',
            "semantic": 'tiny_quote_span',
            "category": 'text',
            "docnote": 'single-quote span scan, min span 0, 5 spans, offsets on',
            "params": {'p1': 0, 'p2': 5, 'p3': True, 'p4': 'single'},
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
        p1 = p1 if p1 is not None else 0
        p2 = p2 if p2 is not None else 5
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'single'
        if action == "run":
            result = au_algo_003(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 0, 'p2': 5, 'p3': True, 'p4': 'single'})
        canned = {'p1': 1}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_003(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

