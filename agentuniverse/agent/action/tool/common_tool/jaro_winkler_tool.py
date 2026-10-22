#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: jaro_winkler_tool.py

"""Jaro / Jaro-Winkler string similarity tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency string matcher.
Jaro-Winkler is the standard similarity for short-string / name
matching (deduplication, entity resolution, typo-tolerant lookup) and
complements the edit-distance axis of ``TextDistanceTool`` and the
phonetic axis of ``PhoneticCodeTool``.

The tool implements the standard Jaro similarity (Jaro 1989) and the
Winkler modification (Winkler 1990) on top of it, and supports four
modes:

* ``similarity`` — two strings to a ``jaro`` score (0-1, 4 decimal
  places) and a ``jaro_winkler`` score (0-1, 4 dp) computed with the
  standard parameters: ``prefix_scale`` p = 0.1 capped at 4 common
  prefix characters and ``boost_threshold`` bt = 0.7 — both
  configurable with documented bounds (``0 < prefix_scale <= 0.25``
  per Winkler's note that p must stay below 1/4 so the score cannot
  exceed 1; ``0 <= boost_threshold <= 1``). The prefix boost is only
  applied when the Jaro score is strictly greater than the boost
  threshold. Characters match only within the standard match window
  ``floor(max(len_a, len_b) / 2) - 1`` (clamped to 0). Empty-string
  conventions: both strings empty -> 1.0, exactly one empty -> 0.0.
* ``compare`` — one pair plus a ``threshold`` (default 0.85) to a
  ``matches`` boolean plus both scores. A pair matches when its
  Jaro-Winkler score is greater than or equal to the threshold.
* ``best_match`` — one string plus a ``candidates`` list to the
  candidates ranked by Jaro-Winkler score descending, truncated to
  ``top_n`` (default 10); ties are broken alphabetically (ascending
  code-point order) so the ranking is fully deterministic.
* ``cluster`` — a list of strings to groups built with union-find:
  every pair whose Jaro-Winkler score is ``>= threshold`` (default
  0.85) is merged, so each group is the connected component of the
  similarity graph — membership is transitive through intermediate
  strings even when two group members are themselves below the
  threshold. Groups are sorted by size descending, then by first
  member; members within a group are sorted alphabetically.

Comparison is case-sensitive by default; ``casefold=True`` folds every
input with ``str.casefold()`` before any scoring (original strings are
preserved in the output).

Scores are reported, compared against thresholds and ranked at the
reported 4-decimal precision, so every decision is consistent with the
displayed values.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode, non-string inputs,
oversized strings or lists, out-of-bounds ``threshold`` /
``prefix_scale`` / ``boost_threshold``, non-positive ``top_n``) raise a
``ValueError``, mirroring the other common tools.
"""

import math
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class JaroWinklerTool(Tool):
    """Jaro / Jaro-Winkler string similarity tool (pure stdlib).

    Input bounds (rejected before any computation): any single string
    is capped at :obj:`MAX_STRING_CHARS` characters, the ``best_match``
    candidates list at :obj:`MAX_CANDIDATES` items and the ``cluster``
    items list at :obj:`MAX_CLUSTER_ITEMS` items (pairwise cluster
    scoring is quadratic in that count).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "jaro_winkler_tool"
    description: str = (
        "Jaro-Winkler string similarity tool — pure Python stdlib, no "
        "network required. similarity mode scores two strings with the "
        "Jaro (0-1, 4dp) and Jaro-Winkler (0-1, 4dp) measures (standard "
        "params: prefix_scale 0.1 capped at 4 prefix chars, "
        "boost_threshold 0.7, match window floor(max(len)/2)-1; both "
        "empty -> 1.0, one empty -> 0.0), compare mode adds a "
        "thresholded matches boolean (default 0.85), best_match ranks a "
        "candidate list by score with alphabetical tie-breaking, and "
        "cluster mode groups a list of strings by pairwise Jaro-Winkler "
        ">= threshold using union-find (transitive connected "
        "components). Case-sensitive by default, casefold=True for "
        "case-insensitive scoring."
    )

    MODES: ClassVar[tuple] = ("similarity", "compare", "best_match", "cluster")

    # Standard Jaro-Winkler parameters (Winkler 1990).
    DEFAULT_PREFIX_SCALE: ClassVar[float] = 0.1
    MAX_PREFIX_SCALE: ClassVar[float] = 0.25
    MAX_PREFIX_CHARS: ClassVar[int] = 4
    DEFAULT_BOOST_THRESHOLD: ClassVar[float] = 0.7
    # Thresholded-mode defaults.
    DEFAULT_COMPARE_THRESHOLD: ClassVar[float] = 0.85
    DEFAULT_TOP_N: ClassVar[int] = 10
    # Scores are reported, compared and ranked at this precision.
    SCORE_DECIMALS: ClassVar[int] = 4
    # Input bounds (see the class docstring).
    MAX_STRING_CHARS: ClassVar[int] = 2_000
    MAX_CANDIDATES: ClassVar[int] = 1_000
    MAX_CLUSTER_ITEMS: ClassVar[int] = 500

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text_a: Any = None,
        text_b: Any = None,
        text: Any = None,
        candidates: Any = None,
        items: Any = None,
        threshold: Any = None,
        top_n: Any = None,
        prefix_scale: Any = None,
        boost_threshold: Any = None,
        casefold: Any = None,
    ) -> Dict[str, Any]:
        """Run one similarity operation.

        Args:
            mode (str): One of ``similarity`` / ``compare`` /
                ``best_match`` / ``cluster``.
            text_a (str): First string of the ``similarity`` and
                ``compare`` modes (may be empty — see the module
                docstring for the empty-string conventions).
            text_b (str): Second string of the ``similarity`` and
                ``compare`` modes.
            text (str): The reference string of the ``best_match`` mode.
            candidates (list[str]): The strings ranked by ``best_match``;
                a non-empty list.
            items (list[str]): The strings grouped by ``cluster``; a
                non-empty list.
            threshold (float): ``compare`` / ``cluster`` mode — a pair
                matches / is merged when its Jaro-Winkler score is
                ``>= threshold``; ``0 <= threshold <= 1``, default 0.85.
            top_n (int): ``best_match`` mode — maximum number of ranked
                candidates to return; integer ``>= 1``, default 10
                (fewer candidates than ``top_n`` returns all of them).
            prefix_scale (float): Jaro-Winkler prefix weight p,
                ``0 < p <= 0.25`` (Winkler's note: p must stay below
                1/4), default 0.1.
            boost_threshold (float): Jaro score above which the prefix
                boost is applied (strictly greater than),
                ``0 <= bt <= 1``, default 0.7.
            casefold (bool): ``True`` to fold every input with
                ``str.casefold()`` before scoring (original strings are
                kept in the output); default ``False`` (case-sensitive).

        Returns:
            Dict[str, Any]: The mode result — scores (``jaro``,
                ``jaro_winkler``), booleans (``matches``) and groups
                (``groups``) as described in the module docstring.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_casefold = self._validate_casefold(casefold)
        clean_prefix_scale = self._validate_prefix_scale(prefix_scale)
        clean_boost = self._validate_boost_threshold(boost_threshold)

        if mode in ("similarity", "compare"):
            clean_a = self._require_string(text_a, "text_a")
            clean_b = self._require_string(text_b, "text_b")
            if mode == "similarity":
                return self._run_similarity(
                    clean_a, clean_b, clean_casefold,
                    clean_prefix_scale, clean_boost,
                )
            clean_threshold = self._validate_threshold(
                threshold, self.DEFAULT_COMPARE_THRESHOLD
            )
            return self._run_compare(
                clean_a, clean_b, clean_threshold, clean_casefold,
                clean_prefix_scale, clean_boost,
            )

        if mode == "best_match":
            clean_text = self._require_string(text, "text")
            clean_candidates = self._require_string_list(
                candidates, "candidates", self.MAX_CANDIDATES
            )
            clean_top_n = self._validate_top_n(top_n)
            return self._run_best_match(
                clean_text, clean_candidates, clean_top_n, clean_casefold,
                clean_prefix_scale, clean_boost,
            )

        clean_items = self._require_string_list(
            items, "items", self.MAX_CLUSTER_ITEMS
        )
        clean_threshold = self._validate_threshold(
            threshold, self.DEFAULT_COMPARE_THRESHOLD
        )
        return self._run_cluster(
            clean_items, clean_threshold, clean_casefold,
            clean_prefix_scale, clean_boost,
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"jaro_winkler_tool: {message}")

    @classmethod
    def _require_string(cls, value: Any, label: str) -> str:
        """Validate a string input (empty allowed — conventions defined)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{label} must be a string (got {value!r})")
        if len(value) > cls.MAX_STRING_CHARS:
            cls._invalid(
                f"{label} exceeds the {cls.MAX_STRING_CHARS:,}-character "
                f"limit (got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _require_string_list(
        cls, value: Any, label: str, cap: int
    ) -> List[str]:
        """Validate a non-empty list of strings bounded by ``cap``."""
        if isinstance(value, bool) or not isinstance(value, list) or not value:
            cls._invalid(
                f"{label} must be a non-empty list of strings (got {value!r})"
            )
        if len(value) > cap:
            cls._invalid(
                f"{label} exceeds the {cap:,}-item limit "
                f"(got {len(value):,} items)"
            )
        for index, item in enumerate(value):
            if item is None or isinstance(item, bool) or not isinstance(item, str):
                cls._invalid(
                    f"{label}[{index}] must be a string (got {item!r})"
                )
            if len(item) > cls.MAX_STRING_CHARS:
                cls._invalid(
                    f"{label}[{index}] exceeds the "
                    f"{cls.MAX_STRING_CHARS:,}-character limit "
                    f"(got {len(item):,} characters)"
                )
        return value

    @classmethod
    def _validate_threshold(cls, value: Any, default: float) -> float:
        """Validate a similarity ``threshold`` (defaults to ``default``)."""
        if value is None:
            return default
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            cls._invalid(
                f"threshold must be a number between 0 and 1 (got {value!r})"
            )
        number = float(value)
        if not math.isfinite(number) or not 0.0 <= number <= 1.0:
            cls._invalid(
                "threshold must be between 0 and 1 inclusive "
                f"(got {number!r})"
            )
        return number

    @classmethod
    def _validate_prefix_scale(cls, value: Any) -> float:
        """Validate the Winkler ``prefix_scale`` weight."""
        if value is None:
            return cls.DEFAULT_PREFIX_SCALE
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            cls._invalid(
                "prefix_scale must be a number greater than 0 and at "
                f"most {cls.MAX_PREFIX_SCALE} (got {value!r})"
            )
        number = float(value)
        if not math.isfinite(number) or not 0.0 < number <= cls.MAX_PREFIX_SCALE:
            cls._invalid(
                "prefix_scale must be greater than 0 and at most "
                f"{cls.MAX_PREFIX_SCALE} — Winkler's note requires the "
                f"prefix weight to stay below 1/4 so the score cannot "
                f"exceed 1 (got {number!r})"
            )
        return number

    @classmethod
    def _validate_boost_threshold(cls, value: Any) -> float:
        """Validate the ``boost_threshold`` Jaro-score gate."""
        if value is None:
            return cls.DEFAULT_BOOST_THRESHOLD
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            cls._invalid(
                "boost_threshold must be a number between 0 and 1 "
                f"(got {value!r})"
            )
        number = float(value)
        if not math.isfinite(number) or not 0.0 <= number <= 1.0:
            cls._invalid(
                "boost_threshold must be between 0 and 1 inclusive "
                f"(got {number!r})"
            )
        return number

    @classmethod
    def _validate_top_n(cls, value: Any) -> int:
        """Validate the ``best_match`` result count."""
        if value is None:
            return cls.DEFAULT_TOP_N
        if isinstance(value, bool) or not isinstance(value, int):
            cls._invalid(f"top_n must be a positive integer (got {value!r})")
        if value < 1:
            cls._invalid(f"top_n must be a positive integer (got {value!r})")
        return value

    @classmethod
    def _validate_casefold(cls, value: Any) -> bool:
        """Validate the ``casefold`` flag."""
        if value is None:
            return False
        if not isinstance(value, bool):
            cls._invalid(f"casefold must be a boolean (got {value!r})")
        return value

    # ------------------------------------------------------------------ #
    # Core similarity functions (pure, deterministic)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _jaro_counts(a: str, b: str) -> Tuple[int, int, float]:
        """Return ``(matches, transpositions, jaro)`` for two strings.

        Implements the standard Jaro similarity: two characters match
        when they are equal and no further apart than the match window
        ``floor(max(len_a, len_b) / 2) - 1`` (clamped to 0); half the
        number of matched characters that appear in a different order
        are the transpositions.

        Empty-string conventions: both empty -> ``(0, 0, 1.0)``;
        exactly one empty -> ``(0, 0, 0.0)``.
        """
        if a == b:
            # Covers the both-empty case (1.0) and the fast path for
            # identical strings.
            return len(a), 0, 1.0
        len_a, len_b = len(a), len(b)
        if len_a == 0 or len_b == 0:
            return 0, 0, 0.0
        window = max(0, max(len_a, len_b) // 2 - 1)
        flags_a = [False] * len_a
        flags_b = [False] * len_b
        matches = 0
        for i in range(len_a):
            low = max(0, i - window)
            high = min(i + window + 1, len_b)
            for j in range(low, high):
                if not flags_b[j] and a[i] == b[j]:
                    flags_a[i] = True
                    flags_b[j] = True
                    matches += 1
                    break
        if matches == 0:
            return 0, 0, 0.0
        # Count matched characters of `a` and `b`, in order, that differ.
        transpositions = 0
        k = 0
        for i in range(len_a):
            if flags_a[i]:
                while not flags_b[k]:
                    k += 1
                if a[i] != b[k]:
                    transpositions += 1
                k += 1
        transpositions //= 2
        score = (
            matches / len_a
            + matches / len_b
            + (matches - transpositions) / matches
        ) / 3.0
        return matches, transpositions, score

    @classmethod
    def _jaro_similarity(cls, a: str, b: str) -> float:
        """Jaro similarity of two strings (0-1)."""
        return cls._jaro_counts(a, b)[2]

    @classmethod
    def _jaro_winkler_similarity(
        cls,
        a: str,
        b: str,
        prefix_scale: float = DEFAULT_PREFIX_SCALE,
        boost_threshold: float = DEFAULT_BOOST_THRESHOLD,
    ) -> float:
        """Jaro-Winkler similarity of two strings (0-1).

        Applies the Winkler prefix boost — ``l * prefix_scale * (1 -
        jaro)`` where ``l`` is the length of the longest common prefix
        capped at :obj:`MAX_PREFIX_CHARS` (4) characters — only when
        the Jaro score is strictly greater than ``boost_threshold``.
        """
        jaro = cls._jaro_similarity(a, b)
        if jaro > boost_threshold:
            prefix = 0
            for char_a, char_b in zip(a, b):
                if char_a == char_b and prefix < cls.MAX_PREFIX_CHARS:
                    prefix += 1
                else:
                    break
            jaro = jaro + prefix * prefix_scale * (1.0 - jaro)
        return jaro

    def _score_pair(
        self,
        a: str,
        b: str,
        casefold: bool,
        prefix_scale: float,
        boost_threshold: float,
    ) -> Dict[str, float]:
        """Score one pair, reporting both measures at 4 decimal places."""
        if casefold:
            a, b = a.casefold(), b.casefold()
        jaro = round(self._jaro_similarity(a, b), self.SCORE_DECIMALS)
        jaro_winkler = round(
            self._jaro_winkler_similarity(a, b, prefix_scale, boost_threshold),
            self.SCORE_DECIMALS,
        )
        return {"jaro": jaro, "jaro_winkler": jaro_winkler}

    # ------------------------------------------------------------------ #
    # similarity / compare modes
    # ------------------------------------------------------------------ #

    def _run_similarity(
        self,
        text_a: str,
        text_b: str,
        casefold: bool,
        prefix_scale: float,
        boost_threshold: float,
    ) -> Dict[str, Any]:
        """Score one pair of strings with both measures."""
        scores = self._score_pair(
            text_a, text_b, casefold, prefix_scale, boost_threshold
        )
        return {
            "mode": "similarity",
            "text_a": text_a,
            "text_b": text_b,
            **scores,
        }

    def _run_compare(
        self,
        text_a: str,
        text_b: str,
        threshold: float,
        casefold: bool,
        prefix_scale: float,
        boost_threshold: float,
    ) -> Dict[str, Any]:
        """Score one pair and decide the match against the threshold."""
        scores = self._score_pair(
            text_a, text_b, casefold, prefix_scale, boost_threshold
        )
        return {
            "mode": "compare",
            "text_a": text_a,
            "text_b": text_b,
            "threshold": threshold,
            "matches": scores["jaro_winkler"] >= threshold,
            **scores,
        }

    # ------------------------------------------------------------------ #
    # best_match mode
    # ------------------------------------------------------------------ #

    def _run_best_match(
        self,
        text: str,
        candidates: List[str],
        top_n: int,
        casefold: bool,
        prefix_scale: float,
        boost_threshold: float,
    ) -> Dict[str, Any]:
        """Rank candidates by Jaro-Winkler score (ties alphabetical)."""
        ranked: List[Dict[str, Any]] = []
        for candidate in candidates:
            scores = self._score_pair(
                text, candidate, casefold, prefix_scale, boost_threshold
            )
            ranked.append({"candidate": candidate, **scores})
        # Jaro-Winkler descending, then candidate ascending (code-point
        # order) — a total, deterministic ordering.
        ranked.sort(
            key=lambda entry: (-entry["jaro_winkler"], entry["candidate"])
        )
        return {
            "mode": "best_match",
            "text": text,
            "candidate_count": len(candidates),
            "top_n": top_n,
            "matches": ranked[:top_n],
        }

    # ------------------------------------------------------------------ #
    # cluster mode (union-find over the similarity graph)
    # ------------------------------------------------------------------ #

    def _run_cluster(
        self,
        items: List[str],
        threshold: float,
        casefold: bool,
        prefix_scale: float,
        boost_threshold: float,
    ) -> Dict[str, Any]:
        """Group items whose pairwise Jaro-Winkler score >= threshold.

        Every at-threshold pair is merged with union-find, so each
        group is a connected component of the similarity graph: an
        item joins a group through any chain of at-threshold pairs,
        even when it is itself below the threshold against some other
        group member.
        """
        count = len(items)
        parent = list(range(count))

        def find(index: int) -> int:
            root = index
            while parent[root] != root:
                root = parent[root]
            while parent[index] != root:  # path compression
                parent[index], index = root, parent[index]
            return root

        def union(left: int, right: int) -> None:
            root_left, root_right = find(left), find(right)
            if root_left != root_right:
                parent[root_right] = root_left

        for i in range(count):
            for j in range(i + 1, count):
                scores = self._score_pair(
                    items[i], items[j], casefold, prefix_scale, boost_threshold
                )
                if scores["jaro_winkler"] >= threshold:
                    union(i, j)

        components: Dict[int, List[str]] = {}
        for index, item in enumerate(items):
            components.setdefault(find(index), []).append(item)
        groups = [sorted(members) for members in components.values()]
        # Largest groups first, then by first (smallest) member.
        groups.sort(key=lambda group: (-len(group), group[0]))
        return {
            "mode": "cluster",
            "threshold": threshold,
            "item_count": count,
            "group_count": len(groups),
            "groups": groups,
        }
