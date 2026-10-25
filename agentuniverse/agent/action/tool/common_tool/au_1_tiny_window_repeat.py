"""TinyWindowRepeatTool: 3-unit word continuation windows, 60-char cap, casefold on (au1k series #1, text)."""

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


def au_algo_001(x, p1=6, p2=240, p3=True, p4="word") -> dict:
    """Count repeated continuation windows in a text view.

    Slides a ``p1``-wide window over the ``p4`` units and reports how often the
    windows repeat; a high ratio flags boilerplate, duplicated snippets or text
    that is stuck in a loop.

    Args:
        x: str, list, dict or number; lists/dicts flatten to a joined text view.
        p1: Window width in units, bounds [2, 12].
        p2: Characters read from the text, bounds [20, 4000].
        p3: When True the text is casefolded before scanning.
        p4: Unit vocabulary, one of "char", "word".

    Returns:
        dict with ``mode``, ``window``, ``units``, ``windows``, ``distinct_windows``,
        ``repeated_windows``, ``repeat_ratio`` (4 decimals), ``top_repeated``
        (<=20 ``{"window": str, "count": int}``), ``casefolded``, ``truncated``.

    Raises:
        ValueError: if p1/p2/p3/p4 break the bounds or vocabulary above, if x is
            not a str/list/dict/number, or if the text view is blank; the
            offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 2 <= p1 <= 12):
        raise ValueError(f"p1 must be an int in [2, 12], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 20 <= p2 <= 4000):
        raise ValueError(f"p2 must be an int in [20, 4000], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("char", "word"):
        raise ValueError(f"p4 must be one of ('char', 'word'), got {p4!r}")
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
    work = text.casefold() if p3 else text
    truncated, work = len(work) > p2, work[:p2]
    units = list(work) if p4 == "char" else work.split()
    joiner = "" if p4 == "char" else " "
    counts = {}
    for index in range(len(units) - p1 + 1):
        window = joiner.join(units[index:index + p1])
        counts[window] = counts.get(window, 0) + 1
    total = sum(counts.values())
    repeated = sorted(
        ((window, count) for window, count in counts.items() if count > 1),
        key=lambda pair: (-pair[1], pair[0]),
    )
    hits = sum(count for _, count in repeated)
    return {
        "mode": p4, "window": p1, "units": len(units), "windows": total,
        "distinct_windows": len(counts), "repeated_windows": len(repeated),
        "repeat_ratio": round(hits / total, 4) if total else 0.0,
        "top_repeated": [{"window": w, "count": c} for w, c in repeated[:20]],
        "casefolded": p3, "truncated": truncated,
    }


class TinyWindowRepeatTool(Tool):
    """Fully offline text reasoning component (au1k #1).

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

    label: str = Field(default="au1k#1", description="series provenance label")

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
            "index": 1,
            "algo": 'au_algo_001',
            "semantic": 'tiny_window_repeat',
            "category": 'text',
            "docnote": '3-unit word continuation windows, 60-char cap, casefold on',
            "params": {'p1': 3, 'p2': 60, 'p3': True, 'p4': 'word'},
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
        p2 = p2 if p2 is not None else 60
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'word'
        if action == "run":
            result = au_algo_001(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 3, 'p2': 60, 'p3': True, 'p4': 'word'})
        canned = {'p1': 4}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_001(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

