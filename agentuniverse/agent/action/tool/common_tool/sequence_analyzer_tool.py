#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: sequence_analyzer_tool.py

"""Numeric sequence pattern classification tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency helper for
math-education agents: where ``RangeGeneratorTool`` *generates* ranges
and classification-type detectors work on text, nothing in the common
tool set *analyzes* an existing numeric sequence. This tool reads a
list of 3-100 finite numbers and answers the three questions a
maths tutor asks: what pattern is this, what comes next, and which
value is missing.

All detection is exact ``decimal.Decimal`` arithmetic inside a fixed
50-significant-digit context — never binary floats — so
``[0.1, 0.2, 0.3]`` is exactly arithmetic with difference 0.1. Three
modes are supported:

* ``classify`` — detect every pattern the sequence satisfies:
  ``arithmetic`` (constant first difference), ``geometric`` (constant
  positive ratio, verified by exact cross-multiplication
  ``t[i+1]**2 == t[i]*t[i+2]`` so no division rounding can fake a
  match), ``fibonacci-like`` (each term equals the sum of the previous
  two), ``quadratic`` (constant *non-zero* second difference; a zero
  second difference is just arithmetic), ``constant`` (all terms
  equal) and ``primes`` (every term an integer prime, checked by 6k+/-1
  trial division with the documented bound ``n < 10**12``; sequences
  containing an integer outside ``[2, 10**12)`` simply skip the primes
  check). Multiple types may hold at once — a constant sequence is
  also arithmetic with difference 0 and, when non-zero, geometric
  with ratio 1; ``[2, 3, 5]`` is both fibonacci-like and primes. The
  result reports ``types`` in canonical order, the pattern parameters
  (``difference`` / ``ratio`` / ``second_difference``) and the next
  term predicted by the *strongest* detected type with priority
  ``quadratic > fibonacci-like > geometric > arithmetic > constant``
  (``primes`` is a property, not a generator, so a primes-only
  sequence predicts ``null``). ``next_term_confidence`` is the
  deterministic heuristic ``min(0.99, 0.60 + 0.10 * (n - 4))`` for
  quadratic and ``min(0.99, 0.60 + 0.10 * (n - 3))`` otherwise,
  rounded to two decimals. A sequence matching no type returns
  ``types: ["none"]`` with a ``null`` next term.
* ``next_n`` — extend the sequence by ``k`` terms (1-10) following the
  strongest detected type. ``none``-typed sequences cannot be
  extended and raise a ``ValueError``.
* ``missing`` — a sequence of 4-100 entries holding exactly one null
  (``None``, or the literal string ``"null"``/``"None"``) recovers
  the missing value. The best-fitting type is decided in two tiers:
  first the types the *remaining terms satisfy on their own* (the
  same classify predicates applied to the known terms as a flat
  sequence, scanned in priority order), then — only if none of those
  yields a verified completion — bridging fits that hold position-
  aware across the gap. In both tiers a candidate is derived from
  the known runs (gap arithmetic / signed geometric mean /
  recurrence bridges / second-difference chains), all available
  derivations of a type must agree, and the completed sequence is
  re-verified with the exact classifiers above, so a returned value
  always makes the *whole* sequence fit the reported type.
  Consequences: ``[null, 16, 64, 256]`` resolves to 4 (geometric —
  the remaining terms are geometric, and flat evidence outranks the
  quadratic completion 112 that any three numbers would vacuously
  admit), ``[1, 1, 2, 3, null, 8]`` resolves to 5 via fibonacci-like
  although the remaining terms alone are not fibonacci-like
  (bridging tier), and ``[3, 6, 9, null]`` resolves to 15 because
  the remaining terms are both arithmetic and fibonacci-like and the
  priority prefers the latter. When no type yields a verified
  completion a ``ValueError`` is raised.

Input validation is strict and happens before any computation: an
unknown mode, a non-list sequence, fewer than 3 or more than 100
numbers, non-number elements (booleans are rejected explicitly —
``True`` is an ``int`` in Python), non-finite floats (NaN/inf), a
``missing`` sequence without exactly one null or with fewer than 3
numeric terms, a ``k`` outside 1-10 or supplied outside ``next_n``,
and an inextendible / unsolvable sequence all raise ``ValueError``.
The tool reads no clock, no randomness and no network: identical
input yields byte-identical output.
"""

import math
from decimal import Decimal, localcontext
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Fixed decimal context: enough head-room that additions and exact
# cross-multiplications of realistically sized inputs never round.
_DECIMAL_PREC = 50

# Primes are checked by 6k+/-1 trial division; past this bound the
# square root exceeds ~10**6 iterations and the check is skipped
# (documented, deterministic, no silent timeouts).
_PRIME_BOUND = 10 ** 12

TYPE_ARITHMETIC = "arithmetic"
TYPE_GEOMETRIC = "geometric"
TYPE_FIBONACCI = "fibonacci-like"
TYPE_QUADRATIC = "quadratic"
TYPE_CONSTANT = "constant"
TYPE_PRIMES = "primes"
TYPE_NONE = "none"

# Canonical reporting order of the `types` list.
CANONICAL_TYPE_ORDER: Tuple[str, ...] = (
    TYPE_ARITHMETIC,
    TYPE_GEOMETRIC,
    TYPE_FIBONACCI,
    TYPE_QUADRATIC,
    TYPE_CONSTANT,
    TYPE_PRIMES,
)

# Strength priority used to pick the predicting / completing type.
# `primes` is a property, not a generator, and never predicts.
PRIORITY_ORDER: Tuple[str, ...] = (
    TYPE_QUADRATIC,
    TYPE_FIBONACCI,
    TYPE_GEOMETRIC,
    TYPE_ARITHMETIC,
    TYPE_CONSTANT,
)

# Minimum sequence length at which each type becomes decidable.
_MIN_TERMS: Dict[str, int] = {
    TYPE_QUADRATIC: 4,  # two second differences needed
    TYPE_ARITHMETIC: 3,
    TYPE_GEOMETRIC: 3,
    TYPE_FIBONACCI: 3,
    TYPE_CONSTANT: 3,
    TYPE_PRIMES: 3,
}


def _is_null_marker(value: Any) -> bool:
    """Whether an entry stands for the missing value in `missing` mode."""
    if value is None:
        return True
    return isinstance(value, str) and value.strip().lower() in ("null", "none")


def _is_prime(n: int) -> bool:
    """Deterministic 6k+/-1 trial-division primality test."""
    if n < 2:
        return False
    if n < 4:  # 2 and 3
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    limit = math.isqrt(n)
    factor = 5
    while factor <= limit:
        if n % factor == 0 or n % (factor + 2) == 0:
            return False
        factor += 6
    return True


class SequenceAnalyzerTool(Tool):
    """Classifies numeric sequences and extends / repairs them.

    Attributes:
        max_terms (int): Upper bound on sequence length accepted by
            any mode (the minimum of 3 numbers is enforced per mode).
        max_next_n (int): Upper bound on the ``k`` continuation count
            of the ``next_n`` mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "sequence_analyzer_tool"
    description: str = (
        "Numeric sequence pattern analyzer — pure Python stdlib decimal "
        "arithmetic, no network required. Classify a list of 3-100 "
        "finite numbers (mode='classify': types detected — arithmetic "
        "(constant difference), geometric (constant ratio > 0, exact "
        "Decimal cross-multiplication), fibonacci-like (each = sum of "
        "previous two), quadratic (constant non-zero second difference), "
        "constant (all equal), primes (all prime by trial division, "
        "bound n < 10**12); multiple types can hold; params "
        "difference/ratio/second_difference; next_term predicted by the "
        "strongest type with priority quadratic > fibonacci-like > "
        "geometric > arithmetic > constant; no type -> types "
        "[\"none\"] and null next_term), extend a sequence by k=1-10 "
        "terms following the strongest type (mode='next_n'), and "
        "recover the single missing value of a sequence holding "
        "exactly one null via the best-fitting type, verified on the "
        "completed sequence (mode='missing')."
    )

    MODES: ClassVar[tuple] = ("classify", "next_n", "missing")

    max_terms: int = 100
    max_next_n: int = 10

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        sequence: Any = None,
        k: Any = None,
    ) -> Dict[str, Any]:
        """Run one sequence analysis operation.

        Args:
            mode (str): One of ``classify`` / ``next_n`` / ``missing``.
            sequence (list): 3-100 (``missing``: 4-100 with exactly
                one null) finite numbers; bools, NaN, inf and other
                non-numbers are rejected.
            k (int | str): Continuation count 1-10, required by (and
                only valid for) the ``next_n`` mode.

        Returns:
            Dict[str, Any]: ``classify`` → ``types``, ``params``,
            ``strongest_type``, ``next_term``,
            ``next_term_confidence``; ``next_n`` → the same detection
            plus ``next_terms``; ``missing`` → ``missing_index``,
            ``missing_value``, ``type`` and ``completed_sequence``.

        Raises:
            ValueError: On any malformed input (before computation),
            when extending a typeless sequence, or when no type can
            complete a sequence with a missing value.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if (
            sequence is None
            or isinstance(sequence, (str, bytes))
            or not isinstance(sequence, (list, tuple))
        ):
            self._invalid(
                "sequence must be a list of numbers (got "
                f"{type(sequence).__name__})"
            )
        if mode == "next_n":
            count = self._validate_k(k)
        elif k is not None:
            self._invalid(
                f"k only applies to the next_n mode (got k={k!r})"
            )

        with localcontext() as ctx:
            ctx.prec = _DECIMAL_PREC
            if mode == "missing":
                return self._run_missing(list(sequence))
            terms = self._to_decimals(list(sequence))
            detection = self._detect(terms)
            if mode == "next_n":
                return self._run_next_n(terms, detection, count, sequence)
            return self._run_classify(terms, detection, sequence)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"sequence_analyzer_tool: {message}")

    @classmethod
    def _validate_k(cls, value: Any) -> int:
        """Validate the next_n continuation count (int or digit string)."""
        if isinstance(value, bool):
            cls._invalid(f"k must be an integer 1-10 (got {value!r})")
        if isinstance(value, int):
            number = value
        elif isinstance(value, str) and value.strip().isdigit():
            number = int(value.strip())
        else:
            cls._invalid(f"k must be an integer 1-10 (got {value!r})")
        if not 1 <= number <= 10:
            cls._invalid(f"k must be between 1 and 10 (got {number})")
        return number

    @classmethod
    def _to_decimal(cls, value: Any, index: int) -> Decimal:
        """Convert one sequence entry to an exact Decimal.

        Floats enter through ``str`` (their shortest repr), so 0.1
        becomes the exact decimal 0.1 rather than the binary float
        noise; ints are exact by construction. Booleans — ``int``
        subclasses in Python — and non-finite floats are traps that
        are rejected explicitly.
        """
        label = f"sequence[{index}]"
        if isinstance(value, bool):
            cls._invalid(f"{label} must be a number (got {value!r})")
        if isinstance(value, int):
            return Decimal(value)
        if isinstance(value, float):
            if not math.isfinite(value):
                cls._invalid(f"{label} must be finite (got {value!r})")
            return Decimal(str(value))
        cls._invalid(f"{label} must be a number (got {value!r})")

    @classmethod
    def _to_decimals(cls, values: List[Any]) -> List[Decimal]:
        """Validate a null-free sequence and convert it to Decimals."""
        if not 3 <= len(values) <= 100:
            cls._invalid(
                f"sequence must hold 3-100 numbers (got {len(values)})"
            )
        return [cls._to_decimal(v, i) for i, v in enumerate(values)]

    # ------------------------------------------------------------------ #
    # Exact Decimal predicates (shared by every mode)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _diffs(terms: List[Decimal]) -> List[Decimal]:
        """First differences of consecutive terms (exact subtraction)."""
        return [terms[i + 1] - terms[i] for i in range(len(terms) - 1)]

    @classmethod
    def _is_constant(cls, terms: List[Decimal]) -> bool:
        """All terms equal."""
        return all(t == terms[0] for t in terms)

    @classmethod
    def _is_arithmetic(cls, terms: List[Decimal]) -> bool:
        """Constant first difference (exactly, including d = 0)."""
        diffs = cls._diffs(terms)
        return all(d == diffs[0] for d in diffs)

    @classmethod
    def _is_fibonacci(cls, terms: List[Decimal]) -> bool:
        """Each term equals the sum of the previous two."""
        return all(
            terms[i] == terms[i - 1] + terms[i - 2]
            for i in range(2, len(terms))
        )

    @classmethod
    def _quadratic_second_difference(
        cls, terms: List[Decimal]
    ) -> Optional[Decimal]:
        """The constant second difference, or None.

        Requires at least 4 terms (two second differences) and a
        *non-zero* second difference: a zero one reduces exactly to
        the arithmetic type and would make every arithmetic sequence
        double-report as quadratic.
        """
        if len(terms) < _MIN_TERMS[TYPE_QUADRATIC]:
            return None
        first = cls._diffs(terms)
        second = [first[i + 1] - first[i] for i in range(len(first) - 1)]
        if any(s != second[0] for s in second):
            return None
        return second[0] if second[0] != 0 else None

    @staticmethod
    def _geometric_ratio(terms: List[Decimal]) -> Optional[Decimal]:
        """The constant ratio (> 0) of a geometric sequence, or None.

        Constancy is verified by exact cross-multiplication
        ``t[i+1]**2 == t[i] * t[i+2]`` — multiplication never rounds
        within the context, unlike division, so a ratio that is not
        exactly constant can never fake a match. The ratio itself is
        reported from the last pair via one rounded division. Terms
        must be non-zero and share one sign (ratio > 0), so
        alternating-sign sequences such as ``[1, -2, 4, -8]`` are
        deliberately excluded.
        """
        if any(t == 0 for t in terms):
            return None
        if not (all(t > 0 for t in terms) or all(t < 0 for t in terms)):
            return None
        for i in range(len(terms) - 2):
            if terms[i + 1] * terms[i + 1] != terms[i] * terms[i + 2]:
                return None
        return terms[-1] / terms[-2]

    @classmethod
    def _all_primes(cls, terms: List[Decimal]) -> bool:
        """Whether every term is an integer prime below 10**12.

        Non-integral terms, or any integer outside ``[2, 10**12)``,
        make the primes type undecided rather than false: the check
        is simply skipped for such sequences (documented bound of the
        trial-division method).
        """
        for term in terms:
            if term != term.to_integral_value():
                return False
            if not 2 <= term < _PRIME_BOUND:
                return False
        return all(_is_prime(int(t)) for t in terms)

    @classmethod
    def _matches(cls, kind: str, terms: List[Decimal]) -> bool:
        """Whether a completed sequence satisfies one exact predicate."""
        if kind == TYPE_CONSTANT:
            return cls._is_constant(terms)
        if kind == TYPE_ARITHMETIC:
            return cls._is_arithmetic(terms)
        if kind == TYPE_FIBONACCI:
            return cls._is_fibonacci(terms)
        if kind == TYPE_GEOMETRIC:
            return cls._geometric_ratio(terms) is not None
        if kind == TYPE_QUADRATIC:
            return cls._quadratic_second_difference(terms) is not None
        return False

    # ------------------------------------------------------------------ #
    # Detection shared by classify / next_n
    # ------------------------------------------------------------------ #

    @classmethod
    def _detect(
        cls, terms: List[Decimal]
    ) -> Tuple[List[str], Dict[str, Decimal], Optional[str]]:
        """Detect every type the sequence satisfies.

        Returns the canonically ordered type list, the pattern
        parameters found along the way, and the strongest (highest
        priority) predicting type — ``None`` when only `primes` or
        nothing at all was detected.
        """
        found: List[str] = []
        params: Dict[str, Decimal] = {}
        if cls._is_constant(terms):
            found.append(TYPE_CONSTANT)
        if cls._is_arithmetic(terms):
            found.append(TYPE_ARITHMETIC)
            params["difference"] = terms[-1] - terms[-2]
        ratio = cls._geometric_ratio(terms)
        if ratio is not None:
            found.append(TYPE_GEOMETRIC)
            params["ratio"] = ratio
        if cls._is_fibonacci(terms):
            found.append(TYPE_FIBONACCI)
        second = cls._quadratic_second_difference(terms)
        if second is not None:
            found.append(TYPE_QUADRATIC)
            params["second_difference"] = second
        if cls._all_primes(terms):
            found.append(TYPE_PRIMES)
        ordered = [t for t in CANONICAL_TYPE_ORDER if t in found]
        strongest = next((t for t in PRIORITY_ORDER if t in found), None)
        return ordered, params, strongest

    @classmethod
    def _extend(
        cls,
        terms: List[Decimal],
        strongest: str,
        params: Dict[str, Decimal],
        count: int,
    ) -> List[Decimal]:
        """Continue the sequence by ``count`` terms of the strongest type.

        The geometric continuation multiplies as ``cur * cur / prev``
        — one division per step — so integer chains such as
        ``[2, 4, 8, 16]`` extend exactly (32, 64, ...) instead of
        drifting through a rounded stored ratio.
        """
        out: List[Decimal] = []
        prev, cur = terms[-2], terms[-1]
        difference = params.get("difference")
        second = params.get("second_difference")
        for _ in range(count):
            if strongest == TYPE_QUADRATIC:
                nxt = cur + (cur - prev) + second
            elif strongest == TYPE_FIBONACCI:
                nxt = cur + prev
            elif strongest == TYPE_GEOMETRIC:
                nxt = cur * cur / prev
            elif strongest == TYPE_ARITHMETIC:
                nxt = cur + difference
            else:  # constant
                nxt = cur
            out.append(nxt)
            prev, cur = cur, nxt
        return out

    @staticmethod
    def _num(value: Decimal) -> Any:
        """Render a Decimal as an int when integral, else a float."""
        if value == value.to_integral_value():
            return int(value)
        return float(value)

    @classmethod
    def _confidence(cls, terms: List[Decimal], strongest: str) -> float:
        """Deterministic next-term confidence, two decimals.

        ``min(0.99, 0.60 + 0.10 * extra_terms)`` where extra terms are
        the confirmations beyond the minimum a type needs to be
        decidable at all (4 terms for quadratic, 3 for the rest).
        """
        extra = len(terms) - _MIN_TERMS[strongest]
        return round(min(0.99, 0.60 + 0.10 * extra), 2)

    # ------------------------------------------------------------------ #
    # Modes
    # ------------------------------------------------------------------ #

    def _run_classify(
        self,
        terms: List[Decimal],
        detection: Tuple[List[str], Dict[str, Decimal], Optional[str]],
        sequence: Any,
    ) -> Dict[str, Any]:
        """Classify a sequence and predict its next term."""
        types, params, strongest = detection
        if strongest is None:
            # Either nothing was detected at all, or only `primes` —
            # a property, not a generator: there is nothing to
            # predict from either way.
            return {
                "mode": "classify",
                "sequence": list(sequence),
                "types": types if types else [TYPE_NONE],
                "params": {
                    key: self._num(value)
                    for key, value in params.items()
                },
                "strongest_type": None,
                "next_term": None,
                "next_term_confidence": 0.0,
            }
        next_term = self._extend(terms, strongest, params, 1)[0]
        return {
            "mode": "classify",
            "sequence": list(sequence),
            "types": types,
            "params": {
                key: self._num(value) for key, value in params.items()
            },
            "strongest_type": strongest,
            "next_term": self._num(next_term),
            "next_term_confidence": self._confidence(terms, strongest),
        }

    def _run_next_n(
        self,
        terms: List[Decimal],
        detection: Tuple[List[str], Dict[str, Decimal], Optional[str]],
        count: int,
        sequence: Any,
    ) -> Dict[str, Any]:
        """Extend the sequence by ``count`` terms of its strongest type."""
        types, params, strongest = detection
        if strongest is None:
            self._invalid(
                "sequence matches no supported pattern (types: "
                f"{[TYPE_NONE]}); it cannot be extended"
            )
        return {
            "mode": "next_n",
            "sequence": list(sequence),
            "types": types,
            "strongest_type": strongest,
            "k": count,
            "next_terms": [
                self._num(t)
                for t in self._extend(terms, strongest, params, count)
            ],
        }

    def _run_missing(self, values: List[Any]) -> Dict[str, Any]:
        """Recover the single missing value of a punctured sequence."""
        if not 4 <= len(values) <= 100:
            self._invalid(
                "missing mode needs 4-100 entries (3+ numbers plus "
                f"exactly one null; got {len(values)})"
            )
        hole_indexes = [
            i for i, v in enumerate(values) if _is_null_marker(v)
        ]
        if len(hole_indexes) == 0:
            self._invalid(
                "missing mode requires exactly one null in the sequence "
                "(found 0; use mode='classify' for null-free sequences)"
            )
        if len(hole_indexes) > 1:
            self._invalid(
                "missing mode requires exactly one null in the sequence "
                f"(found {len(hole_indexes)} at indexes {hole_indexes})"
            )
        hole = hole_indexes[0]
        left = [
            self._to_decimal(v, i)
            for i, v in enumerate(values[:hole])
        ]
        right = [
            self._to_decimal(v, i)
            for i, v in enumerate(values[hole + 1:], start=hole + 1)
        ]
        if len(left) + len(right) < 3:
            self._invalid(
                "missing mode needs at least 3 numeric terms besides "
                f"the null (got {len(left) + len(right)})"
            )
        # Tier 1: types the remaining terms satisfy on their own —
        # flat evidence first, so a type cannot hijack a gap on the
        # strength of a completion alone (any three numbers admit a
        # vacuous "constant" second difference, which would otherwise
        # let quadratic preempt a genuine geometric run such as
        # [null, 16, 64, 256]).
        # Tier 2: bridging fits that only hold position-aware.
        knowns = left + right
        flat_types, _, _ = self._detect(knowns)
        scan_order = [k for k in PRIORITY_ORDER if k in flat_types] + [
            k for k in PRIORITY_ORDER if k not in flat_types
        ]
        for kind in scan_order:
            candidate = self._missing_candidate(kind, left, right)
            if candidate is None:
                continue
            completed = left + [candidate] + right
            if self._matches(kind, completed):
                return {
                    "mode": "missing",
                    "sequence": list(values),
                    "missing_index": hole,
                    "missing_value": self._num(candidate),
                    "type": kind,
                    "completed_sequence": [
                        v if i != hole else self._num(candidate)
                        for i, v in enumerate(values)
                    ],
                }
        self._invalid(
            "no supported pattern fits the known terms (tried the "
            "types the remaining terms satisfy on their own, then "
            "bridging fits, in priority order: "
            f"{', '.join(PRIORITY_ORDER)}); the missing value is "
            "undetermined"
        )

    # ------------------------------------------------------------------ #
    # Missing-value candidates (position-aware, verified afterwards)
    # ------------------------------------------------------------------ #

    @classmethod
    def _missing_candidate(
        cls, kind: str, left: List[Decimal], right: List[Decimal]
    ) -> Optional[Decimal]:
        """Derive a fill-in candidate of one type, or None.

        Every derivation is position-aware — the gap length between
        the known runs is honoured — and all available derivations of
        a type must agree exactly. The candidate is only a proposal:
        the caller re-verifies the completed sequence with the exact
        classifiers before accepting it.
        """
        if kind == TYPE_CONSTANT:
            knowns = left + right
            if not all(t == knowns[0] for t in knowns):
                return None
            return knowns[0]

        if kind == TYPE_ARITHMETIC:
            # Differences inside each known run, plus the gap-2
            # spanning difference halved exactly (division by 2
            # always terminates in decimal).
            sources: List[Decimal] = list(
                dict.fromkeys(cls._diffs(left) + cls._diffs(right))
            )
            if left and right:
                sources.append((right[0] - left[-1]) / 2)
            if not sources:
                return None
            step = sources[0]
            if any(s != step for s in sources):
                return None
            return left[-1] + step if left else right[0] - step

        if kind == TYPE_FIBONACCI:
            candidates: List[Decimal] = []
            if len(left) >= 2:
                candidates.append(left[-1] + left[-2])  # t[m] = t[m-1]+t[m-2]
            if len(right) >= 2:
                candidates.append(right[1] - right[0])  # t[m+2]-t[m+1]
            if left and right:
                candidates.append(right[0] - left[-1])  # t[m+1]-t[m-1]
            return cls._agreed(candidates)

        if kind == TYPE_GEOMETRIC:
            knowns = left + right
            if any(t == 0 for t in knowns):
                return None
            if not (
                all(t > 0 for t in knowns) or all(t < 0 for t in knowns)
            ):
                return None
            candidates = []
            if left and right:
                # Geometric mean across the gap, signed like the terms.
                root = (left[-1] * right[0]).sqrt()
                candidates.append(root if left[-1] > 0 else -root)
            if len(left) >= 2:
                candidates.append(left[-1] * left[-1] / left[-2])
            if len(right) >= 2:
                candidates.append(right[0] * right[0] / right[1])
            return cls._agreed(candidates)

        # TYPE_QUADRATIC
        seconds: List[Decimal] = []
        if len(left) >= 3:
            left_second = cls._run_second_difference(left)
            if left_second is not None:
                seconds.append(left_second)
        if len(right) >= 3:
            right_second = cls._run_second_difference(right)
            if right_second is not None:
                seconds.append(right_second)
        candidates = []
        if seconds:
            if any(s != seconds[0] for s in seconds):
                return None
            c = seconds[0]
            if len(left) >= 3:
                candidates.append(2 * left[-1] - left[-2] + c)
            if len(right) >= 3:
                candidates.append(2 * right[0] - right[1] + c)
        elif len(left) == 2 and len(right) == 2:
            # Two short runs: d4 = d1 + 3c bridges the gap exactly, so
            # c = (d4 - d1) / 3 and t[m] = left[-1] + d1 + c. The
            # division rounds whenever 3 does not divide; the
            # verification of the completed sequence rejects those.
            d1 = left[1] - left[0]
            d4 = right[1] - right[0]
            candidates.append(left[1] + d1 + (d4 - d1) / 3)
        return cls._agreed(candidates)

    @staticmethod
    def _agreed(candidates: List[Decimal]) -> Optional[Decimal]:
        """The single value all derivations agree on, else None."""
        if not candidates:
            return None
        if any(c != candidates[0] for c in candidates):
            return None
        return candidates[0]

    @classmethod
    def _run_second_difference(
        cls, terms: List[Decimal]
    ) -> Optional[Decimal]:
        """Constant second difference of a run, zero allowed (unlike
        the quadratic *predicate* — a bridging candidate may derive
        c = 0 and still be rejected by verification)."""
        first = cls._diffs(terms)
        second = [first[i + 1] - first[i] for i in range(len(first) - 1)]
        if not second or any(s != second[0] for s in second):
            return None
        return second[0]
