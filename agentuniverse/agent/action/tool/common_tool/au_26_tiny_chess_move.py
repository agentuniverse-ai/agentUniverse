"""TinyChessMoveTool: 3x3 N mobility, 5 moves listed, both colours on (au1k series #26, structural)."""

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


def au_algo_026(x, p1=8, p2=40, p3=False, p4="N") -> dict:
    """Count board-bounded piece moves on a mask-style chess board.

    The board is written row by row separated by "/" with "." for an empty square
    and the piece letter elsewhere; uppercase pieces are the player's. Only board
    bounds and blockers are modelled (pseudo-legal mobility).

    Args:
        x: board string ("..../...." rows of ``p1`` cells) or list of rows.
        p1: Board width in squares, bounds [3, 8].
        p2: Moves listed, bounds [1, 200].
        p3: When True both colours move, otherwise only uppercase pieces do.
        p4: Piece vocabulary, "N" (knight), "K" (king) or "R" (rook).

    Returns:
        dict with ``piece``, ``board_size``, ``occupied``, ``total_moves``,
        ``pieces`` (<=20), ``moves`` (<=``p2`` "e2->g3" strings), ``truncated``.

    Raises:
        ValueError: on a p1/p2/p3/p4 violation, a wrong row count or width, or a cell
            outside ".NKRnkr"; the offending value is quoted in the message.
    """
    if not (isinstance(p1, int) and not isinstance(p1, bool) and 3 <= p1 <= 8):
        raise ValueError(f"p1 must be an int in [3, 8], got {p1!r}")
    if not (isinstance(p2, int) and not isinstance(p2, bool) and 1 <= p2 <= 200):
        raise ValueError(f"p2 must be an int in [1, 200], got {p2!r}")
    if not isinstance(p3, bool):
        raise ValueError(f"p3 must be a bool, got {p3!r}")
    if p4 not in ("N", "K", "R"):
        raise ValueError(f"p4 must be 'N', 'K' or 'R', got {p4!r}")
    if isinstance(x, str):
        rows = x.split("/")
    elif isinstance(x, (list, tuple)):
        rows = [str(row) for row in x]
    else:
        raise ValueError(f"x must be a board string or list of rows, got {x!r}")
    if len(rows) != p1:
        raise ValueError(f"x must have {p1} rows, got {len(rows)!r}")
    for row in rows:
        if len(row) != p1 or any(cell not in ".NKRnkr" for cell in row):
            raise ValueError(f"x rows must be {p1} cells of '.NKRnkr', got {row!r}")
    files, offsets = "abcdefgh"[:p1], {
        "N": [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)],
        "K": [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
        "R": [(1, 0), (-1, 0), (0, 1), (0, -1)],
    }[p4]
    total, pieces, moves = 0, [], []
    for rank, row in enumerate(rows):
        for file, cell in enumerate(row):
            if cell == "." or (not p3 and not cell.isupper()):
                continue
            count = 0
            for delta_file, delta_rank in offsets:
                step = 1
                while True:
                    target_file, target_rank = file + delta_file * step, rank + delta_rank * step
                    if not (0 <= target_file < p1 and 0 <= target_rank < p1):
                        break
                    count += 1
                    moves.append(f"{files[file]}{p1 - rank}->{files[target_file]}{p1 - target_rank}") if len(moves) < p2 else None
                    if rows[target_rank][target_file] != "." or p4 != "R":
                        break
                    step += 1
            total += count
            pieces.append({"square": f"{files[file]}{p1 - rank}", "moves": count,
                           "colour": "white" if cell.isupper() else "black"})
    return {
        "piece": p4, "board_size": p1, "occupied": sum(1 for row in rows for cell in row if cell != "."),
        "total_moves": total, "pieces": pieces[:20], "moves": moves[:p2], "truncated": len(pieces) > 20 or total > p2,
    }


class TinyChessMoveTool(Tool):
    """Fully offline structural reasoning component (au1k #26).

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

    label: str = Field(default="au1k#26", description="series provenance label")

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
            "index": 26,
            "algo": 'au_algo_026',
            "semantic": 'tiny_chess_move',
            "category": 'structural',
            "docnote": '3x3 N mobility, 5 moves listed, both colours on',
            "params": {'p1': 3, 'p2': 5, 'p3': True, 'p4': 'N'},
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
        p2 = p2 if p2 is not None else 5
        p3 = p3 if p3 is not None else True
        p4 = p4 if p4 is not None else 'N'
        if action == "run":
            result = au_algo_026(x, p1=p1, p2=p2, p3=p3, p4=p4)
            return {"action": "run", "x_kind": type(x).__name__, "result": result}
        # action == "alt": the canned alternative of this assignment,
        # then any explicit caller overrides on top.
        overridden = dict({'p1': 3, 'p2': 5, 'p3': True, 'p4': 'N'})
        canned = {'p3': False}
        for key, value in canned.items():
            overridden[key] = value
        overridden.update(provided)
        result = au_algo_026(x, **overridden)
        return {"action": "alt", "x_kind": type(x).__name__,
                "canned": canned,
                "provided": provided,
                "result": result}

