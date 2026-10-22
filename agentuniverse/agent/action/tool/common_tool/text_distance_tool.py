#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: text_distance_tool.py

"""Text distance / similarity tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency string metric agents
can call for matching plumbing: fuzzy key comparison, near-duplicate
detection, typo tolerance, or ranking candidates by closeness.

The tool is a strictly-validated façade over two classic dynamic
programming measures and supports three modes:

* ``levenshtein`` — the classic edit distance: the minimum number of
  single-character insertions, deletions and substitutions needed to
  turn ``text_a`` into ``text_b``.
* ``damerau_levenshtein`` — the *restricted* Damerau-Levenshtein
  distance (optimal string alignment): everything Levenshtein allows
  plus transpositions of two *adjacent* characters, with no substring
  edited more than once (``"teh"`` -> ``"the"`` costs 1, not 2). The
  unrestricted variant that re-edits substrings is deliberately not
  implemented: it is not a metric and is rarely what callers want.
* ``similarity`` — a normalized ``0.0``-``1.0`` similarity score
  computed as ``1 - distance / max(len(a), len(b))`` using either the
  ``levenshtein`` or the ``damerau_levenshtein`` metric (``metric``
  option). Identical strings score ``1.0``; two strings with no
  characters in common score ``0.0``. Two empty strings are identical
  and score ``1.0``.

Both distances are symmetric, zero only for identical strings, and
satisfy the triangle inequality. Comparison is character-based over
the full Unicode range and exact; an optional ``case_sensitive``
flag (default ``True``) controls whether ``str.casefold()`` is applied
to both inputs before measuring, giving case-insensitive comparison.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode or metric, non-string inputs,
texts over 10,000 characters each, or a character-count product over
4,000,000 — the pure-Python DP matrix bound, measured on the
case-folded texts the dynamic program actually runs on, so
casefold's character expansion cannot push the real matrix past the
limit) raise a ``ValueError``, mirroring the other common tools.
There are no content-level failure
modes: every pair of valid strings has a well-defined distance, so
results are always returned, never raised.
"""

from typing import Any, ClassVar, Dict, List

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class TextDistanceTool(Tool):
    """String edit distance / similarity tool built purely on the stdlib.

    Attributes:
        max_chars (int): Upper bound on the length of each input text;
            longer inputs are rejected before any computation.
        max_matrix_cells (int): Upper bound on ``len(text_a) *
            len(text_b)``; larger products are rejected because the
            pure-Python dynamic program is quadratic in that product.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    name: str = "text_distance_tool"
    description: str = (
        "Text distance tool — pure Python stdlib, no network required. "
        "Levenshtein edit distance (mode='levenshtein'), restricted "
        "Damerau-Levenshtein / optimal-string-alignment distance that "
        "also counts adjacent transpositions "
        "(mode='damerau_levenshtein'), and a normalized 0-1 similarity "
        "score (mode='similarity') based on either metric via the "
        "'metric' option, with optional case-insensitive comparison."
    )

    MODES: ClassVar[tuple] = ("levenshtein", "damerau_levenshtein", "similarity")
    METRICS: ClassVar[tuple] = ("levenshtein", "damerau_levenshtein")

    max_chars: int = 10_000
    max_matrix_cells: int = 4_000_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text_a: Any = None,
        text_b: Any = None,
        case_sensitive: Any = None,
        metric: Any = None,
    ) -> Dict[str, Any]:
        """Measure the distance / similarity between two texts.

        Args:
            mode (str): One of ``levenshtein`` / ``damerau_levenshtein``
                / ``similarity``.
            text_a (str): The first text. Empty strings are valid (the
                distance to a non-empty text is its length).
            text_b (str): The second text. Empty strings are valid.
            case_sensitive (bool): ``True`` (default) compares the texts
                exactly; ``False`` applies ``str.casefold()`` to both
                texts before measuring.
            metric (str): ``similarity`` mode only — ``levenshtein``
                (default) or ``damerau_levenshtein``, the distance the
                normalized score is based on. Ignored by the two
                distance modes.

        Returns:
            Dict[str, Any]: Always a ``result`` key — the integer edit
                distance for the distance modes, or the float
                similarity in ``0.0..1.0`` for the ``similarity`` mode
                (which also carries the underlying ``distance``) —
                plus the call context (mode, metric, input lengths,
                resolved ``case_sensitive`` flag).

        Raises:
            ValueError: If any parameter is malformed (unknown mode or
                metric, non-string texts, texts over ``max_chars``
                characters, or a length product over
                ``max_matrix_cells`` — measured after ``casefold()``
                when ``case_sensitive=False``, since casefold can
                expand characters).
        """
        if mode not in self.MODES:
            self._invalid(f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})")
        clean_a = self._validate_text("text_a", text_a)
        clean_b = self._validate_text("text_b", text_b)
        clean_case_sensitive = self._validate_case_sensitive(case_sensitive)
        if not clean_case_sensitive:
            clean_a = clean_a.casefold()
            clean_b = clean_b.casefold()
        # The cell bound guards the dynamic program, so it is checked on the
        # (case-folded) texts the DP actually runs on: casefold can expand a
        # character (e.g. "ß" -> "ss", "ﬃ" -> "ffi") and must not be able to
        # push the real matrix past the limit.
        if len(clean_a) * len(clean_b) > self.max_matrix_cells:
            self._invalid(
                f"len(text_a) * len(text_b) must not exceed "
                f"{self.max_matrix_cells:,} cells for the pure-Python "
                f"dynamic program (got {len(clean_a):,} x "
                f"{len(clean_b):,} = {len(clean_a) * len(clean_b):,})"
            )

        context: Dict[str, Any] = {
            "mode": mode,
            "length_a": len(clean_a),
            "length_b": len(clean_b),
            "case_sensitive": clean_case_sensitive,
        }
        if mode == "similarity":
            clean_metric = self._validate_metric(metric)
            distance = self._distance(clean_metric, clean_a, clean_b)
            longest = max(len(clean_a), len(clean_b))
            similarity = 1.0 if longest == 0 else 1.0 - distance / longest
            return {
                **context,
                "metric": clean_metric,
                "distance": distance,
                "result": similarity,
            }
        return {**context, "result": self._distance(mode, clean_a, clean_b)}

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_distance_tool: {message}")

    def _validate_text(self, label: str, text: Any) -> str:
        """Validate one input text (empty strings are well-defined)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"{label} must be a string (got {text!r})")
        if len(text) > self.max_chars:
            self._invalid(
                f"{label} exceeds the {self.max_chars:,}-character limit (got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_case_sensitive(cls, case_sensitive: Any) -> bool:
        """Validate the ``case_sensitive`` flag (None means default)."""
        if case_sensitive is None:
            return True
        if isinstance(case_sensitive, bool):
            return case_sensitive
        cls._invalid(f"case_sensitive must be a boolean or None (got {case_sensitive!r})")

    @classmethod
    def _validate_metric(cls, metric: Any) -> str:
        """Validate the ``similarity``-mode ``metric`` selector."""
        if metric is None:
            return "levenshtein"
        if metric not in ("levenshtein", "damerau_levenshtein"):
            cls._invalid(f"metric must be one of: {', '.join(cls.METRICS)} (got {metric!r})")
        return metric

    # ------------------------------------------------------------------ #
    # Distance kernels (pure functions, no shared state)
    # ------------------------------------------------------------------ #

    @classmethod
    def _distance(cls, metric: str, a: str, b: str) -> int:
        """Dispatch to the selected distance kernel."""
        if metric == "damerau_levenshtein":
            return cls._osa_distance(a, b)
        return cls._levenshtein_distance(a, b)

    @staticmethod
    def _levenshtein_distance(a: str, b: str) -> int:
        """Classic edit distance (insert / delete / substitute).

        Two-row dynamic program, O(len(a) * len(b)) time and O(min)
        space; empty inputs short-circuit to the other length.
        """
        if a == b:
            return 0
        if not a:
            return len(b)
        if not b:
            return len(a)
        if len(a) < len(b):
            a, b = b, a
        previous = list(range(len(b) + 1))
        for i, char_a in enumerate(a, start=1):
            current = [i]
            for j, char_b in enumerate(b, start=1):
                substitution_cost = 0 if char_a == char_b else 1
                current.append(
                    min(
                        previous[j] + 1,  # deletion
                        current[j - 1] + 1,  # insertion
                        previous[j - 1] + substitution_cost,  # substitution
                    )
                )
            previous = current
        return previous[-1]

    @staticmethod
    def _osa_distance(a: str, b: str) -> int:
        """Restricted Damerau-Levenshtein (optimal string alignment).

        Levenshtein plus transpositions of two adjacent characters,
        with no substring edited more than once. Three-row dynamic
        program: the ``i-2`` row is needed for the transposition term.
        """
        if a == b:
            return 0
        if not a:
            return len(b)
        if not b:
            return len(a)
        two_back: List[int] = []
        one_back = list(range(len(b) + 1))
        for i, char_a in enumerate(a, start=1):
            current = [i]
            for j, char_b in enumerate(b, start=1):
                substitution_cost = 0 if char_a == char_b else 1
                best = min(
                    one_back[j] + 1,  # deletion
                    current[j - 1] + 1,  # insertion
                    one_back[j - 1] + substitution_cost,  # substitution
                )
                if i > 1 and j > 1 and char_a == b[j - 2] and a[i - 2] == char_b:
                    best = min(best, two_back[j - 2] + 1)  # transposition
                current.append(best)
            two_back = one_back
            one_back = current
        return one_back[-1]
