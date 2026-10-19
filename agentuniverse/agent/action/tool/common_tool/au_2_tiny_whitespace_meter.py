"""TinyWhitespaceMeterTool: strict whitespace policy over 4 lines, 2-space indent unit (au1k series #2, text)."""

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


def au_algo_002(x, p1=40, p2=4, p3=True, p4="strict") -> dict:
    """Measure indentation and trailing-whitespace hygiene of a text block.

    Counts blank lines, tabs, trailing spaces and indent widths in ``p2`` units;
    ``p4`` selects which of those offenders are reported.

    Args:
        x: str, list, dict or number; lists and dicts become newline-joined lines.
        p1: Lines inspected, bounds [1, 500].
        p2: Indent unit width in spaces, bounds [2, 16].
        p3: When True tabs are expanded with ``p2``-wide stops before measuring.
        p4: Policy vocabulary, one of "strict", "collapse", "strip".

    Returns:
        dict with ``lines``, ``blank_lines``, ``trailing_lines``, ``tab_lines``,
        ``max_indent``, ``max_indent_units``, ``irregular_indents``, ``policy``,
        ``policy_offenders`` (<=20 ``{"line": int, "kind": str}``),
        ``clean_ratio``, ``truncated``.

    Raises:
        ValueError: if p1/p2/p3/p4 break the bounds or vocabulary above, if x is
            not a str/list/dict/number, or if the text view is blank; the
            offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 500):
        raise ValueError(f"p1 must be an int in [1, 500], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 2 <= p2 <= 16):
        raise ValueError(f"p2 must be an int in [2, 16], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("strict", "collapse", "strip"):
        raise ValueError(f"p4 must be in ('strict', 'collapse', 'strip'), got {p4!r}")
    if isinstance(x, str):
        text = x
    elif isinstance(x, (list, tuple)):
        text = "\n".join(str(item) for item in x)
    elif isinstance(x, dict):
        text = "\n".join(f"{key}={value}" for key, value in x.items())
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        text = str(x)
    else:
        raise ValueError(f"x must be str, list, dict or number, got {x!r}")
    if not text.strip():
        raise ValueError(f"x must contain a non-space character, got {x!r}")
    lines = text.splitlines()
    truncated, lines = len(lines) > p1, lines[:p1]
    rendered = [line.expandtabs(p2) if p3 else line for line in lines]
    widths = [len(line) - len(line.lstrip(" ")) for line in rendered if line.strip()]
    irregular = [n + 1 for n, line in enumerate(rendered) if line.strip()
                 and (len(line) - len(line.lstrip(" "))) % p2]
    trailing = [n + 1 for n, line in enumerate(rendered)
                if line.strip() and line != line.rstrip()]
    offenders = ([{"line": n, "kind": "irregular_indent"} for n in irregular]
                 + [{"line": n, "kind": "trailing_space"} for n in trailing])
    offenders.sort(key=lambda item: (item["line"], item["kind"]))
    blank = sum(1 for line in rendered if not line.strip())
    keep = {"strict": offenders,
            "collapse": [i for i in offenders if i["kind"] == "irregular_indent"],
            "strip": [i for i in offenders if i["kind"] == "trailing_space"]}
    return {
        "lines": len(lines), "blank_lines": blank, "trailing_lines": len(trailing),
        "tab_lines": sum(1 for line in lines if "\t" in line),
        "max_indent": max(widths) if widths else 0,
        "max_indent_units": (max(widths) // p2) if widths else 0,
        "irregular_indents": len(irregular), "policy": p4,
        "policy_offenders": keep[p4][:20],
        "clean_ratio": round(max(len(lines) - blank - len(trailing)
                                 - len(irregular), 0) / len(lines), 4) if lines else 0.0,
        "truncated": truncated,
    }


class TinyWhitespaceMeterTool(Tool):
    """Fully offline text reasoning component (au1k #2).

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

    label: str = Field(default="au1k#2", description="series provenance label")

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
            "index": 2,
            "algo": 'au_algo_002',
            "semantic": 'tiny_whitespace_meter',
            "category": 'text',
            "docnote": 'strict whitespace policy over 4 lines, 2-space indent unit',
            "params": {'p1': 4, 'p2': 2, 'p3': True, 'p4': 'strict'},
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
        p1 = p1 if p1 is not None else 4
        p2 = p2 if p2 is not None else 2
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'strict'
        if action == "run":
            result = au_algo_002(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 4, 'p2': 2, 'p3': True, 'p4': 'strict'})
        canned = {'p1': 5}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_002(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

