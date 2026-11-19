"""TinyZipfRankTool: word token ranking, top 1, min length 1, casefold on (au1k series #4, text)."""

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


def au_algo_004(x, p1=10, p2=3, p3=True, p4="word") -> dict:
    """Rank token frequencies and test them against a Zipf-style fit.

    Orders tokens by descending count, fits log-rank against log-count by least
    squares and reports the mean relative error against a pure Zipf law.

    Args:
        x: str, list, dict or number; lists/dicts flatten to a joined text view.
        p1: Leading ranks used in the fit, bounds [1, 50].
        p2: Minimum token length in characters, bounds [1, 200].
        p3: When True tokens are casefolded before counting.
        p4: Tokenizer vocabulary, "word" (punctuation trimmed) or "alnum".

    Returns:
        dict with ``tokens``, ``distinct``, ``top_tokens``, ``zipf_slope``,
        ``fit_error``, ``hapax_ratio``, ``monotone_decay``, ``truncated``.

    Raises:
        ValueError: if p1/p2/p3/p4 break the bounds or vocabulary above, if x is
            not a str/list/dict/number, or if no token survives the ``p2``
            filter; the offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 50):
        raise ValueError(f"p1 must be an int in [1, 50], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("word", "alnum"):
        raise ValueError(f"p4 must be one of ('word', 'alnum'), got {p4!r}")
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
    lowered = text.casefold() if p3 else text
    tokens = (re.findall(r"[^\W_]+", lowered, flags=re.UNICODE) if p4 == "alnum"
              else [item.strip(".,;:!?()[]{}\"'`") for item in lowered.split()])
    tokens = [token for token in tokens if len(token) >= p2]
    if not tokens:
        raise ValueError(f"x must yield a token of length {p2!r}, got {x!r}")
    truncated, tokens = len(tokens) > 5000, tokens[:5000]
    counts = {token: len(list(group))
              for token, group in itertools.groupby(sorted(tokens))}
    head = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:p1]
    ranks = [math.log(rank + 1) for rank in range(len(head))]
    freqs = [math.log(count) for _, count in head]
    mean_r, mean_f = sum(ranks) / len(head), sum(freqs) / len(head)
    spread = sum((value - mean_r) ** 2 for value in ranks)
    slope = (sum((r - mean_r) * (f - mean_f) for r, f in zip(ranks, freqs))
             / spread) if spread else 0.0
    top = head[0][1]
    error = sum(abs(count - top / (rank + 1)) / (top / (rank + 1))
                for rank, (_, count) in enumerate(head)) / len(head)
    return {
        "tokens": len(tokens), "distinct": len(counts),
        "top_tokens": [{"token": t, "count": c, "rank": i + 1}
                       for i, (t, c) in enumerate(head)],
        "zipf_slope": round(slope, 4), "fit_error": round(error, 4),
        "hapax_ratio": round(sum(1 for c in counts.values() if c == 1)
                             / len(counts), 4),
        "monotone_decay": all(head[i][1] >= head[i + 1][1]
                              for i in range(len(head) - 1)),
        "truncated": truncated,
    }


class TinyZipfRankTool(Tool):
    """Fully offline text reasoning component (au1k #4).

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

    label: str = Field(default="au1k#4", description="series provenance label")

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
            "index": 4,
            "algo": 'au_algo_004',
            "semantic": 'tiny_zipf_rank',
            "category": 'text',
            "docnote": 'word token ranking, top 1, min length 1, casefold on',
            "params": {'p1': 1, 'p2': 1, 'p3': True, 'p4': 'word'},
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
        p2 = p2 if p2 is not None else 1
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'word'
        if action == "run":
            result = au_algo_004(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 1, 'p2': 1, 'p3': True, 'p4': 'word'})
        canned = {'p1': 2}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_004(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

