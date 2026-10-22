#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: random_pick_tool.py

"""Seeded random selection tool built purely on the stdlib ``random`` module.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency picker agents can
call whenever a choice has to be made *from caller-provided data*:
drawing candidates, subsampling a corpus, weighting options by score,
or shuffling a list reproducibly.

The tool complements ``RandomDataGeneratorTool`` (PR #3484), which
*generates synthetic values* such as names, emails, hex tokens and
UUIDs; this tool never invents values — it *selects* from the list the
caller passes in. Four modes are supported:

* ``pick`` — choose ``k`` items from ``items`` with or without
  replacement (``with_replacement``, default ``False``). Without
  replacement the ``k`` indices are distinct and ``1 <= k <= len``;
  with replacement an item may recur and ``k`` may exceed the list
  length (bounded by ``max_k``).
* ``weighted`` — choose ``k`` items from ``items`` according to
  ``weights`` (ints/floats >= 0), *without replacement*: zero-weight
  items are excluded from the draw and after every draw the remaining
  weights are renormalized over the surviving pool, so a heavy item
  keeps its proportional influence throughout the draw. ``k`` is
  bounded by the number of positive-weight items.
* ``shuffle`` — seeded deterministic shuffle of ``items``; the result
  carries both the shuffled items and, for each position, the index
  the item had in the original list.
* ``sample_indices`` — choose ``k`` distinct indices from
  ``range(n)`` without touching any list at all.

Seeding is the point of the tool: when ``seed`` is provided the tool
builds a fresh ``random.Random(seed)`` per call, so the same seed
always yields the same result for the same inputs. When ``seed`` is
absent a ``random.SystemRandom`` source is used and the result reports
``seed_used: null`` — genuinely unpredictable, not reproducible.

Input validation is strict and happens before any draw: unknown mode,
missing ``items`` / ``weights`` / ``k`` / ``n``, a non-list or empty or
oversized list, length-mismatched or non-finite or negative or
all-zero weights, out-of-bounds ``k`` / ``n``, a non-bool
``with_replacement``, and a ``seed`` that is neither an integer nor a
non-empty string (booleans are rejected everywhere an integer is
expected — ``True`` is not a valid ``k``, weight or seed) raise a
``ValueError``, mirroring the other common tools.
"""

import math
import random
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class RandomPickTool(Tool):
    """Seeded selection / sampling tool built purely on the stdlib.

    Selects values from caller-provided lists (it never generates
    data), with full determinism when a ``seed`` is given.

    Attributes:
        max_items (int): Upper bound on the ``items`` / ``weights``
            list length and on the ``n`` of ``sample_indices``; longer
            inputs are rejected before any draw.
        max_k (int): Upper bound on ``k`` for the with-replacement
            ``pick`` mode, the only mode where ``k`` may exceed the
            list length.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "random_pick_tool"
    description: str = (
        "Random pick tool — seeded selection from caller-provided "
        "lists, pure Python stdlib, no network required. Choose k "
        "items with or without replacement (mode='pick'), draw k "
        "items without replacement with zero-weight items excluded "
        "and weights renormalized after each draw (mode='weighted'), "
        "shuffle deterministically and get original indices "
        "(mode='shuffle'), or sample k distinct indices from range(n) "
        "(mode='sample_indices'). Provide a seed for a reproducible "
        "result; without one an OS-entropy source is used and "
        "seed_used is null."
    )

    MODES: ClassVar[tuple] = (
        "pick",
        "weighted",
        "shuffle",
        "sample_indices",
    )

    max_items: int = 10_000
    max_k: int = 10_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        items: Any = None,
        weights: Any = None,
        k: Any = None,
        n: Any = None,
        with_replacement: Any = None,
        seed: Any = None,
    ) -> dict[str, Any]:
        """Run one selection operation.

        Args:
            mode (str): One of ``pick`` / ``weighted`` / ``shuffle`` /
                ``sample_indices``.
            items (list): The values to select from. Required for the
                ``pick``, ``weighted`` and ``shuffle`` modes; not used
                by ``sample_indices``. Any JSON-style values are
                accepted, duplicates included (``indices`` in the
                result disambiguates them).
            weights (list): Per-item numbers (ints/floats >= 0) for
                the ``weighted`` mode; must match ``items`` in length.
                Zero-weight items are excluded from the draw and at
                least one weight must be positive.
            k (int): How many values to pick — required for the
                ``pick``, ``weighted`` and ``sample_indices`` modes.
                Without replacement ``1 <= k <= pool size``; with
                replacement ``1 <= k <= 10_000``. Not used by
                ``shuffle``.
            n (int): The exclusive upper bound of the index range —
                required for the ``sample_indices`` mode
                (``1 <= n <= 10_000``).
            with_replacement (bool): ``pick`` mode only — allow the
                same item to be drawn more than once (default
                ``False``).
            seed (int | str): Optional seed. When given, a fresh
                ``random.Random(seed)`` drives the draw, so the same
                inputs plus seed always produce the same result. When
                omitted an OS-entropy ``random.SystemRandom`` source
                is used and the result reports ``seed_used: null``.

        Returns:
            Dict[str, Any]: A uniform payload with the call context
            (``mode``, ``k`` or ``n``), ``picked`` (the selected
            values), ``indices`` (their positions — for ``shuffle``
            the original index of every shuffled position),
            ``with_replacement`` and ``seed_used`` (the seed echoed
            back, or ``None`` when the OS-entropy source was used).

        Raises:
            ValueError: If any parameter is malformed (before any
                draw happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        rng, seed_used = self._make_rng(seed)
        if mode == "sample_indices":
            return self._run_sample_indices(rng, seed_used, n, k)
        clean_items = self._validate_items(items)
        if mode == "shuffle":
            return self._run_shuffle(rng, seed_used, clean_items)
        if mode == "weighted":
            clean_weights = self._validate_weights(weights, clean_items)
            return self._run_weighted(
                rng, seed_used, clean_items, clean_weights, k
            )
        return self._run_pick(rng, seed_used, clean_items, k, with_replacement)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any draw)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"random_pick_tool: {message}")

    @classmethod
    def _validate_int(cls, value: Any, label: str) -> int:
        """Validate an integer parameter, rejecting the bool trap."""
        if isinstance(value, bool) or not isinstance(value, int):
            cls._invalid(f"{label} must be an integer (got {value!r})")
        return value

    @classmethod
    def _validate_items(cls, items: Any) -> list:
        """Validate the ``items`` list every list-based mode requires."""
        if not isinstance(items, list):
            cls._invalid(f"items must be a non-empty list (got {items!r})")
        if not items:
            cls._invalid("items must be a non-empty list (got [])")
        if len(items) > 10_000:
            cls._invalid(
                f"items exceed the 10,000-entry limit (got {len(items):,})"
            )
        return items

    @classmethod
    def _validate_weights(cls, weights: Any, items: list) -> list:
        """Validate the ``weights`` list of the weighted mode."""
        if not isinstance(weights, list):
            cls._invalid(f"weights must be a list of numbers (got {weights!r})")
        if len(weights) != len(items):
            cls._invalid(
                "weights must match items in length "
                f"(got {len(weights)} weights for {len(items)} items)"
            )
        for weight in weights:
            if isinstance(weight, bool) or not isinstance(weight, (int, float)):
                cls._invalid(
                    f"weights must be ints/floats >= 0 (got {weight!r})"
                )
            if not math.isfinite(weight):
                cls._invalid(
                    "weights must be finite numbers >= 0 "
                    f"(got {weight!r})"
                )
            if weight < 0:
                cls._invalid(f"weights must be ints/floats >= 0 (got {weight!r})")
        if sum(weights) <= 0:
            cls._invalid("weights must contain at least one positive value")
        return weights

    @classmethod
    def _validate_k(cls, k: Any, limit: int) -> int:
        """Validate ``k`` against an inclusive upper ``limit``."""
        k = cls._validate_int(k, "k")
        if k < 1:
            cls._invalid(f"k must be >= 1 (got {k})")
        if k > limit:
            cls._invalid(
                f"k must be <= {limit:,} for this mode and input (got {k:,})"
            )
        return k

    @classmethod
    def _validate_seed(cls, seed: Any) -> Any:
        """Validate the optional ``seed`` (int or non-empty string)."""
        if seed is None:
            return None
        if isinstance(seed, bool):
            cls._invalid(f"seed must be an integer or a non-empty string (got {seed!r})")
        if isinstance(seed, int):
            return seed
        if isinstance(seed, str) and seed:
            return seed
        cls._invalid(f"seed must be an integer or a non-empty string (got {seed!r})")

    @classmethod
    def _make_rng(cls, seed: Any) -> tuple[random.Random, Any]:
        """Build the draw's random source.

        A seeded source is a *fresh* ``random.Random(seed)`` per call,
        so the same seed reproduces the same result no matter how many
        calls came before. An unseeded source is ``random.SystemRandom``
        (OS entropy) and is reported back as ``seed_used: null``.
        """
        seed_used = cls._validate_seed(seed)
        if seed_used is None:
            return random.SystemRandom(), None
        return random.Random(seed_used), seed_used

    # ------------------------------------------------------------------ #
    # pick mode
    # ------------------------------------------------------------------ #

    def _run_pick(
        self,
        rng: random.Random,
        seed_used: Any,
        items: list,
        k: Any,
        with_replacement: Any,
    ) -> dict[str, Any]:
        """Choose k items from the list, with or without replacement."""
        if with_replacement is None:
            with_replacement = False
        if not isinstance(with_replacement, bool):
            self._invalid(
                f"with_replacement must be true or false (got {with_replacement!r})"
            )
        if with_replacement:
            clean_k = self._validate_k(k, self.max_k)
            indices = [rng.randrange(len(items)) for _ in range(clean_k)]
        else:
            clean_k = self._validate_k(k, len(items))
            indices = rng.sample(range(len(items)), clean_k)
        return self._selection_result(
            mode="pick",
            rng_context={"k": clean_k},
            seed_used=seed_used,
            indices=indices,
            items=items,
            with_replacement=with_replacement,
        )

    # ------------------------------------------------------------------ #
    # weighted mode
    # ------------------------------------------------------------------ #

    def _run_weighted(
        self,
        rng: random.Random,
        seed_used: Any,
        items: list,
        weights: list,
        k: Any,
    ) -> dict[str, Any]:
        """Draw k items without replacement, weights renormalized per draw.

        Zero-weight items never enter the pool. Each draw picks an
        item with probability proportional to its weight within the
        surviving pool; the drawn item is removed and the remaining
        weights are implicitly renormalized over the new total, which
        is the correct successive-sampling semantics for weighted
        sampling without replacement.
        """
        # Only positive-weight items are eligible for the draw.
        pool = [
            (index, weight)
            for index, weight in enumerate(weights)
            if weight > 0
        ]
        eligible = len(pool)
        clean_k = self._validate_k(k, eligible)
        picked_positions: list[int] = []
        for _ in range(clean_k):
            total = sum(weight for _, weight in pool)
            threshold = rng.random() * total
            cumulative = 0.0
            chosen_slot = len(pool) - 1
            for slot, (_, weight) in enumerate(pool):
                cumulative += weight
                if threshold < cumulative:
                    chosen_slot = slot
                    break
            picked_positions.append(pool.pop(chosen_slot)[0])
        return self._selection_result(
            mode="weighted",
            rng_context={"k": clean_k, "eligible_items": eligible},
            seed_used=seed_used,
            indices=picked_positions,
            items=items,
            with_replacement=False,
        )

    # ------------------------------------------------------------------ #
    # shuffle mode
    # ------------------------------------------------------------------ #

    def _run_shuffle(
        self, rng: random.Random, seed_used: Any, items: list
    ) -> dict[str, Any]:
        """Shuffle the list deterministically; report original indices."""
        indices = list(range(len(items)))
        rng.shuffle(indices)
        return self._selection_result(
            mode="shuffle",
            rng_context={"k": len(items)},
            seed_used=seed_used,
            indices=indices,
            items=items,
            with_replacement=False,
        )

    # ------------------------------------------------------------------ #
    # sample_indices mode
    # ------------------------------------------------------------------ #

    def _run_sample_indices(
        self, rng: random.Random, seed_used: Any, n: Any, k: Any
    ) -> dict[str, Any]:
        """Pick k distinct indices from range(n)."""
        n = self._validate_int(n, "n")
        if n < 1:
            self._invalid(f"n must be >= 1 (got {n})")
        if n > 10_000:
            self._invalid(f"n exceeds the 10,000 limit (got {n:,})")
        clean_k = self._validate_k(k, n)
        indices = rng.sample(range(n), clean_k)
        return {
            "mode": "sample_indices",
            "n": n,
            "k": clean_k,
            "with_replacement": False,
            "seed_used": seed_used,
            "indices": indices,
            "picked": list(indices),
        }

    # ------------------------------------------------------------------ #
    # Result assembly
    # ------------------------------------------------------------------ #

    @staticmethod
    def _selection_result(
        mode: str,
        rng_context: dict[str, Any],
        seed_used: Any,
        indices: list,
        items: list,
        with_replacement: bool = False,
    ) -> dict[str, Any]:
        """Build the uniform ``picked`` / ``indices`` payload."""
        return {
            "mode": mode,
            **rng_context,
            "with_replacement": with_replacement,
            "seed_used": seed_used,
            "picked": [items[index] for index in indices],
            "indices": list(indices),
        }
