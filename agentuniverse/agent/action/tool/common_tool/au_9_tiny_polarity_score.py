"""TinyPolarityScoreTool: posneg lexicon score over 20 tokens, min 1, casefold on (au1k series #9, text)."""

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


def au_algo_009(x, p1=200, p2=2, p3=True, p4="posneg") -> dict:
    """Score a text view against a small offline polarity lexicon.

    Counts positive and negative markers (or certainty and hedge markers) and
    reports a normalised score in [-1.0, 1.0]. The lexicon is deliberately tiny
    so a reviewer can audit every hit; it is not a trained sentiment model.

    Args:
        x: str, list, dict or number; lists/dicts flatten to a joined text view.
        p1: Maximum tokens scored, bounds [1, 500].
        p2: Minimum tokens required, bounds [1, 50].
        p3: When True tokens are casefolded before lookup.
        p4: Lexicon vocabulary, "posneg" or "certainty".

    Returns:
        dict with ``lexicon``, ``tokens``, ``positive``, ``negative``, ``score``,
        ``label`` ("positive"/"negative"/"neutral"), ``hits`` (<=20
        ``{"token", "polarity"}``), ``truncated``.

    Raises:
        ValueError: if p1/p2/p3/p4 break the bounds or vocabulary above, if x is
            not a str/list/dict/number, or if fewer than ``p2`` tokens remain;
            the offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 1 <= p1 <= 500):
        raise ValueError(f"p1 must be an int in [1, 500], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 50):
        raise ValueError(f"p2 must be an int in [1, 50], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("posneg", "certainty"):
        raise ValueError(f"p4 must be 'posneg' or 'certainty', got {p4!r}")
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
    tokens = re.findall(r"[^\W_]+", text.casefold() if p3 else text, flags=re.UNICODE)
    if len(tokens) < p2:
        raise ValueError(f"x must yield {p2} tokens, got {len(tokens)!r}")
    lexicons = {
        "posneg": ("good great best better love like fast clear clean win safe strong "
                   "happy stable useful",
                   "bad worse worst hate dislike slow unclear dirty lose risk weak sad "
                   "broken flaky buggy"),
        "certainty": ("must always never definitely certain clearly proven guaranteed "
                      "exactly",
                      "maybe perhaps might could unclear possibly roughly probably guess"),
    }
    positives, negatives = (set(part.split()) for part in lexicons[p4])
    truncated, tokens = len(tokens) > p1, tokens[:p1]
    positive = sum(1 for token in tokens if token in positives)
    negative = sum(1 for token in tokens if token in negatives)
    score = (positive - negative) / len(tokens)
    return {
        "lexicon": p4, "tokens": len(tokens), "positive": positive,
        "negative": negative, "score": round(score, 4),
        "label": "positive" if score > 0.05 else
                 ("negative" if score < -0.05 else "neutral"),
        "hits": [{"token": token, "polarity": 1 if token in positives else -1}
                 for token in tokens
                 if token in positives or token in negatives][:20],
        "truncated": truncated,
    }


class TinyPolarityScoreTool(Tool):
    """Fully offline text reasoning component (au1k #9).

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

    label: str = Field(default="au1k#9", description="series provenance label")

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
            "index": 9,
            "algo": 'au_algo_009',
            "semantic": 'tiny_polarity_score',
            "category": 'text',
            "docnote": 'posneg lexicon score over 20 tokens, min 1, casefold on',
            "params": {'p1': 20, 'p2': 1, 'p3': True, 'p4': 'posneg'},
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
        p1 = p1 if p1 is not None else 20
        p2 = p2 if p2 is not None else 1
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'posneg'
        if action == "run":
            result = au_algo_009(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 20, 'p2': 1, 'p3': True, 'p4': 'posneg'})
        canned = {'p1': 21}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_009(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

