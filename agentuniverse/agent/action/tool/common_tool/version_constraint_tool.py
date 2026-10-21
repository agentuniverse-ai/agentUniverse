#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: version_constraint_tool.py

"""Dependency *constraint-set* resolution tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the layer above single-range checks: dependency
resolution proper. Where a semver *range* helper answers "does
version ``X`` satisfy range ``R``?", a package manager must answer
the set question every ``npm install`` / ``pip install`` /
lockfile-audit workflow actually asks — "here is a *group* of
constraints on one package and the versions that exist; which
versions satisfy **all** of them, which one should I pick, which
constraint is doing the real work, and do any two constraints
contradict each other outright?".

Three modes, all offline and deterministic:

* ``resolve`` — a constraint list plus the available versions of the
  package. Every constraint is applied to every available version
  (each check running the full npm range semantics, prerelease
  gating included); the result carries ``satisfiable`` (does any
  version satisfy the whole set), the ``candidates`` — the
  satisfying versions sorted ascending by semver precedence — the
  ``best`` pick (the highest candidate, the ``maxSatisfying``
  decision), the ``binding_constraint`` (the range that eliminated
  the most available versions — ties go to the lowest index — the
  constraint a dependency resolver would blame first), a
  ``per_constraint`` breakdown (``matched_count`` /
  ``excluded_count`` of the available versions per range) and, when
  the set is unsatisfiable, the pairwise-empty constraint pairs that
  explain why.
* ``conflicts`` — a constraint list only. Every pair of ranges is
  intersected (branch pairs of the two ``||`` unions merged by AND
  and reduced to their strongest bounds); pairs whose intersection
  is empty are reported as conflicts. Emptiness is decided exactly
  for release versions and per-triple for gated pre-releases. The
  result also names the ``tightest`` constraint — the one with the
  narrowest release window (an exact pin beats every range; for a
  union the window is the best-effort footprint from the leftmost
  lower bound to the rightmost upper bound, documented in the
  ``note``).
* ``explain_set`` — every constraint expanded into its primitive
  comparators side-by-side (the npm desugaring, one line per
  constraint), plus the computed intersection of the whole set:
  when every constraint is single-branch the strongest merged lower
  / upper bound, its half-open release window and the exact
  emptiness verdict; when unions are present the per-branch-pair
  combinations with their own bounds (best-effort, structured
  ``note`` — npm gates pre-releases per union branch, so a printed
  bound may admit same-tuple pre-releases that only one input
  branch would accept).

The range grammar is the strict npm ``node-semver`` subset: union
branches split on ``||``; a branch is either a hyphen range
``partial - partial`` (spaces required, as in npm) or one-or-more
whitespace-separated comparators ANDed together; a comparator is a
primitive (``> >= < <= =`` + partial), a tilde ``~partial``, a caret
``^partial``, a bare x-range (``1.2.x``, ``1.2``, ``1``, ``*``) or
a full version (exact match); partials allow x / X / * placeholders
(components after an x placeholder collapse npm-style); a
pre-release requires a full ``X.Y.Z`` core and follows the semver
2.0.0 identifier rules; build metadata is accepted and ignored; a
leading ``v`` is stripped; whitespace between an operator and its
version is tolerated and glued (npm's comparator-trim behavior,
``>= 1.2.3`` ≡ ``>=1.2.3``); an entirely empty branch means ``*``.
Caret / tilde desugaring follows npm exactly — ``^0.2.3`` →
``>=0.2.3 <0.3.0`` and ``^0.0.3`` → ``>=0.0.3 <0.0.4`` (the 0.x
special cases), ``1.2.3 - 2.3`` → ``>=1.2.3 <2.4.0`` (a partial
hyphen upper bound excludes the whole next ``.0`` series), ``>1.2``
→ ``>=1.3.0`` — and the npm **prerelease rule** holds throughout: a
pre-release only satisfies a range when a comparator of the matching
union branch carries a pre-release on the same
``major.minor.patch`` tuple (``1.2.3-alpha`` satisfies
``^1.2.3-alpha`` but NOT ``>=1.2.3``), so a set containing
``>=1.2.4`` silently drops ``1.2.4-alpha`` from the candidates.

The grammar engine is implemented **standalone** in this module and
kept rule-for-rule consistent with the engine of the
``SemverRangeTool`` (PR #3991): the two PRs are siblings on
independent branches, so neither can import the other — the shared
npm rules (parser, desugarers, precedence key, prerelease gating,
bound merging) are re-derived here verbatim and any future grammar
change must be applied to both. What this tool adds on top is the
*set* layer: multi-constraint intersection over an available-version
pool, binding-constraint attribution, pairwise conflict detection
and set-level explanation — the dependency-resolution layer over
semver ranges.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, missing / empty / oversized
inputs — constraint strings and version strings are capped at 1,000
characters, the constraint list at 100 entries, the available list
at 1,000 entries) raise a ``ValueError``, mirroring the other common
tools. Errors that depend on the *content being processed* — a
version that is not strict semver, a malformed range — are returned
as a structured ``error`` payload (invalid ranges cite the 0-based
character ``position`` of the offending fragment, its ``branch``
index, the ``fragment`` text and the ``constraint_index`` in the
set) so an agent can react without catching exceptions. Junk
entries inside the available-version list do not fail the run: they
are counted and reported per entry with the parse reason, mirroring
candidate-list handling elsewhere.
"""

import itertools
import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_ASCII_WHITESPACE = re.compile(r"\s")
_NUMERIC = re.compile(r"[0-9]+")
# Semver 2.0.0 §9: identifiers comprise ASCII alphanumerics + hyphen.
_IDENTIFIER = re.compile(r"[0-9A-Za-z-]+")
# Union separator of npm ranges.
_UNION_SPLIT = re.compile(r"\|\|")
# Hyphen ranges require whitespace on both sides of the '-'.
_HYPHEN_SPLIT = re.compile(r"\s+-\s+")
_TOKEN_SPLIT = re.compile(r"\S+")
# Comparison operators, longest first so '>=' beats '>'.
_OPERATORS: Tuple[str, ...] = (">=", "<=", ">", "<", "=")
# Operator / sigil characters (for npm's whitespace-gluing tolerance).
_OP_CHARS = "><=~^"
_X_MARKS = ("x", "X", "*")
# Sentinels for the width of an unbounded release window.
_MAJOR_UNITS = 1_000_000_000_000
_MINOR_UNITS = 1_000_000

# Input length limits (constraint expressions and versions are short;
# the bounds exist purely to reject pathological inputs early).
_MAX_CHARS = 1_000
_MAX_CONSTRAINTS = 100
_MAX_VERSIONS = 1_000
# How many junk list entries / union-branch combinations are reported.
_MAX_REPORTED = 50
_MAX_COMBINATIONS = 64


class _RangeError(Exception):
    """Internal carrier for a malformed range (with position)."""

    def __init__(self, message: str, position: int, fragment: str,
                 branch: int) -> None:
        super().__init__(message)
        self.message = message
        self.position = position
        self.fragment = fragment
        self.branch = branch


class _SemVer:
    """A parsed strict semver 2.0.0 version (internal value object)."""

    __slots__ = ("major", "minor", "patch", "prerelease_ids", "build_ids")

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease_ids: Tuple[str, ...] = (),
        build_ids: Tuple[str, ...] = (),
    ) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease_ids = prerelease_ids
        self.build_ids = build_ids

    @property
    def core_tuple(self) -> Tuple[int, int, int]:
        """The (major, minor, patch) triple."""
        return (self.major, self.minor, self.patch)

    @property
    def is_prerelease(self) -> bool:
        """Whether the version carries a pre-release."""
        return bool(self.prerelease_ids)

    @property
    def precedence_key(self) -> tuple:
        """Sort key implementing spec §11 precedence (build ignored).

        The fourth element separates releases (1) from pre-releases
        (0); the fifth encodes identifiers as ``(0, n)`` for numeric
        ones (compared numerically, always below alphanumeric ones)
        and ``(1, s)`` for alphanumeric ones (compared lexically).
        """
        if not self.prerelease_ids:
            return (self.major, self.minor, self.patch, 1, ())
        identifiers = tuple(
            (0, int(part)) if _NUMERIC.fullmatch(part) else (1, part)
            for part in self.prerelease_ids
        )
        return (self.major, self.minor, self.patch, 0, identifiers)

    @property
    def text(self) -> str:
        """Canonical text without build metadata (range bookkeeping)."""
        out = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease_ids:
            out += "-" + ".".join(self.prerelease_ids)
        return out

    def __str__(self) -> str:  # pragma: no cover - debugging aid
        out = self.text
        if self.build_ids:
            out += "+" + ".".join(self.build_ids)
        return out


def _parse_version(text: str) -> Tuple[Optional[_SemVer], Optional[str]]:
    """Parse a strict semver version with an optional leading ``v``.

    Returns ``(version, None)`` on success or ``(None, message)`` on
    failure. Build metadata is validated but kept on the value.
    """
    raw = text
    if raw[:1] in ("v", "V"):
        raw = raw[1:]
    if _ASCII_WHITESPACE.search(raw):
        return None, (
            f"whitespace is not allowed in a semantic version string "
            f"(got {text[:64]!r})"
        )
    core_and_pre, plus, build_part = raw.partition("+")
    build_ids: Tuple[str, ...] = ()
    if plus:
        if not build_part:
            return None, "build metadata MUST NOT be empty after '+'"
        build_ids = tuple(build_part.split("."))
        for part in build_ids:
            if part == "":
                return None, (
                    f"build identifiers must be non-empty — "
                    f"{build_part[:64]!r} contains an empty identifier"
                )
            if not _IDENTIFIER.fullmatch(part):
                return None, (
                    f"build identifiers must comprise only ASCII "
                    f"alphanumerics and hyphens [0-9A-Za-z-] — "
                    f"got {part!r}"
                )
    core, hyphen, pre_part = core_and_pre.partition("-")
    prerelease_ids: Tuple[str, ...] = ()
    if hyphen:
        if not pre_part:
            return None, (
                "pre-release version MUST NOT be empty — '-' must be "
                "followed by dot-separated non-empty identifiers"
            )
        prerelease_ids = tuple(pre_part.split("."))
        for part in prerelease_ids:
            if part == "":
                return None, (
                    f"pre-release identifiers must be non-empty — "
                    f"{pre_part[:64]!r} contains an empty identifier"
                )
            if not _IDENTIFIER.fullmatch(part):
                return None, (
                    f"pre-release identifiers must comprise only ASCII "
                    f"alphanumerics and hyphens [0-9A-Za-z-] — "
                    f"got {part!r}"
                )
            if (
                _NUMERIC.fullmatch(part)
                and len(part) > 1
                and part[0] == "0"
            ):
                return None, (
                    f"numeric pre-release identifiers MUST NOT include "
                    f"leading zeroes — got {part!r}"
                )
    parts = core.split(".")
    if len(parts) != 3:
        return None, (
            f"a version must be 'MAJOR.MINOR.PATCH' — got "
            f"{len(parts)} dot-separated part(s): {raw[:64]!r}"
        )
    numbers: List[int] = []
    for name, part in zip(("major", "minor", "patch"), parts):
        if part == "":
            return None, f"the {name} version is empty"
        if not _NUMERIC.fullmatch(part):
            return None, (
                f"the {name} version must be a non-negative integer "
                f"— got {part!r}"
            )
        if len(part) > 1 and part[0] == "0":
            return None, (
                f"the {name} version MUST NOT contain leading zeroes "
                f"— got {part!r}"
            )
        numbers.append(int(part))
    return (
        _SemVer(numbers[0], numbers[1], numbers[2], prerelease_ids,
                build_ids),
        None,
    )


class _Partial:
    """A parsed range partial: ``M[.m[.p]]`` with x placeholders."""

    __slots__ = ("major", "minor", "patch", "prerelease_ids")

    def __init__(
        self,
        major: Optional[int],
        minor: Optional[int],
        patch: Optional[int],
        prerelease_ids: Tuple[str, ...] = (),
    ) -> None:
        self.major = major  # None means x (unbounded wildcard)
        self.minor = minor
        self.patch = patch
        self.prerelease_ids = prerelease_ids

    @property
    def is_any(self) -> bool:
        """``*`` / ``x`` with no components pinned at all."""
        return self.major is None

    def as_version(self, minor_default: int = 0,
                   patch_default: int = 0) -> _SemVer:
        """Materialize the partial into a full version."""
        return _SemVer(
            self.major or 0,
            self.minor if self.minor is not None else minor_default,
            self.patch if self.patch is not None else patch_default,
            self.prerelease_ids,
            (),
        )


def _parse_partial(text: str) -> Tuple[Optional[_Partial], Optional[str]]:
    """Parse a range partial per the npm grammar.

    Each of the 1-3 dot-separated components is a number without
    leading zeroes or an ``x`` / ``X`` / ``*`` placeholder; a
    pre-release requires a full numeric ``X.Y.Z`` core; build metadata
    is accepted (and ignored) on a full core only; components after an
    ``x`` placeholder are collapsed npm-style (``1.x.3`` ≡ ``1.x``).
    """
    raw = text
    if raw[:1] in ("v", "V"):
        raw = raw[1:]
    core_and_pre, plus, build_part = raw.partition("+")
    if plus and not build_part:
        return None, "build metadata MUST NOT be empty after '+'"
    del build_part  # build metadata is ignored inside ranges
    core, hyphen, pre_part = core_and_pre.partition("-")
    prerelease_ids: Tuple[str, ...] = ()
    if hyphen:
        if not pre_part:
            return None, (
                "pre-release version MUST NOT be empty — '-' must be "
                "followed by dot-separated non-empty identifiers"
            )
        prerelease_ids = tuple(pre_part.split("."))
        for part in prerelease_ids:
            if part == "" or not _IDENTIFIER.fullmatch(part):
                return None, (
                    f"pre-release identifiers must comprise only ASCII "
                    f"alphanumerics and hyphens [0-9A-Za-z-] — "
                    f"got {part!r}"
                )
            if (
                _NUMERIC.fullmatch(part)
                and len(part) > 1
                and part[0] == "0"
            ):
                return None, (
                    f"numeric pre-release identifiers MUST NOT include "
                    f"leading zeroes — got {part!r}"
                )
    parts = core.split(".")
    if not 1 <= len(parts) <= 3:
        return None, (
            f"expected 'MAJOR[.MINOR[.PATCH]]' (1 to 3 dot-separated "
            f"components, numbers or x placeholders) — got "
            f"{len(parts)} component(s): {core[:64]!r}"
        )
    if hyphen and len(parts) != 3:
        return None, (
            "a pre-release requires a full X.Y.Z version core "
            f"(got {text[:64]!r})"
        )
    if plus and len(parts) != 3:
        return None, (
            "build metadata requires a full X.Y.Z version core "
            f"(got {text[:64]!r})"
        )
    numbers: List[Optional[int]] = []
    saw_x = False
    for part in parts:
        if part == "":
            return None, (
                f"a range component must not be empty — got "
                f"{core[:64]!r}"
            )
        if part in _X_MARKS:
            saw_x = True
            numbers.append(None)
            continue
        if saw_x:
            # npm collapses anything after an x placeholder; a
            # pre-release/build behind an x is rejected above.
            numbers.append(None)
            continue
        if not _NUMERIC.fullmatch(part):
            return None, (
                f"a range component must be a number or an x/X/* "
                f"placeholder — got {part!r}"
            )
        if len(part) > 1 and part[0] == "0":
            return None, (
                f"range components MUST NOT contain leading zeroes — "
                f"got {part!r}"
            )
        numbers.append(int(part))
    if prerelease_ids and any(n is None for n in numbers):
        return None, (
            "a pre-release requires a full numeric X.Y.Z version core "
            f"(x placeholders are not allowed — got {text[:64]!r})"
        )
    # Collapse: a None (x) below hides everything to its right.
    major = numbers[0]
    minor = numbers[1] if len(numbers) > 1 else None
    patch = numbers[2] if len(numbers) > 2 else None
    if major is None:
        minor = None
    if minor is None:
        patch = None
    return _Partial(major, minor, patch, prerelease_ids), None


class _Comparator:
    """One primitive comparator: ``op version`` (op '' means '=')."""

    __slots__ = ("op", "version")

    def __init__(self, op: str, version: Optional[_SemVer]) -> None:
        self.op = op  # '', '>', '>=', '<', '<=' or '*' for ANY
        self.version = version

    @property
    def is_any(self) -> bool:
        """The npm ANY comparator produced by ``*`` / empty branches."""
        return self.op == "*"

    def test(self, version: _SemVer) -> bool:
        """Whether ``version`` passes this comparator (build ignored)."""
        if self.is_any:
            return True
        left = version.precedence_key
        right = self.version.precedence_key  # type: ignore[union-attr]
        if self.op == "":
            return left == right
        if self.op == ">":
            return left > right
        if self.op == ">=":
            return left >= right
        if self.op == "<":
            return left < right
        return left <= right  # '<='

    def text(self) -> str:
        """Canonical rendering (npm style)."""
        if self.is_any:
            return "*"
        if self.op == "":
            return "=" + self.version.text  # type: ignore[union-attr]
        return self.op + self.version.text  # type: ignore[union-attr]


def _any_comparator() -> _Comparator:
    """The npm ANY comparator (matches everything, gates nothing)."""
    return _Comparator("*", None)


def _never_comparator() -> _Comparator:
    """npm's matches-nothing comparator ``<0.0.0-0`` (from ``>*``)."""
    return _Comparator(
        "<", _SemVer(0, 0, 0, ("0",), ())
    )


def _exact_comparator(version: _SemVer) -> _Comparator:
    return _Comparator("", version)


def _next_triple(triple: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """The next discrete (major, minor, patch) triple."""
    return (triple[0], triple[1], triple[2] + 1)


class _Branch:
    """One union branch: an AND of comparators plus its gating set."""

    __slots__ = ("comparators", "gating_triples")

    def __init__(self, comparators: List[_Comparator]) -> None:
        self.comparators = comparators
        # Triples whose pre-releases this branch may admit (npm rule:
        # a comparator with a pre-release gates its own tuple).
        self.gating_triples = {
            c.version.core_tuple
            for c in comparators
            if not c.is_any and c.version is not None
            and c.version.is_prerelease
        }

    def matches(self, version: _SemVer) -> bool:
        """npm ``testSet``: all comparators AND the prerelease gate."""
        for comparator in self.comparators:
            if not comparator.test(version):
                return False
        if version.is_prerelease:
            return version.core_tuple in self.gating_triples
        return True

    def texts(self) -> List[str]:
        if not self.comparators or (
            len(self.comparators) == 1 and self.comparators[0].is_any
        ):
            return [_any_comparator().text()]
        return [c.text() for c in self.comparators]


# --------------------------------------------------------------------- #
# Range parsing (token → comparators, npm desugaring)
# --------------------------------------------------------------------- #

def _desugar_hyphen(
    lower_text: str,
    upper_text: str,
    position: int,
    branch: int,
) -> List[_Comparator]:
    """Desugar ``lower - upper`` per the npm hyphen-replace rules.

    Lower: ``>=`` the zero-filled lower partial (kept verbatim with a
    pre-release on a full core). Upper: ``<=`` on a full core, else
    ``<`` the next bumped component of the partial upper bound
    (``2.3`` → ``<2.4.0``, ``2`` → ``<3.0.0``); an x upper drops the
    upper bound entirely.
    """
    lower, message = _parse_partial(lower_text)
    if lower is None:
        raise _RangeError(message or "invalid lower hyphen bound",
                          position, lower_text, branch)
    upper, message = _parse_partial(upper_text)
    if upper is None:
        raise _RangeError(message or "invalid upper hyphen bound",
                          position, upper_text, branch)
    comparators: List[_Comparator] = []
    if lower.is_any:
        pass  # 'x - ...' contributes no lower bound
    elif lower.minor is None:
        comparators.append(
            _Comparator(">=", _SemVer(lower.major or 0, 0, 0,
                                      lower.prerelease_ids, ()))
        )
    elif lower.patch is None:
        comparators.append(
            _Comparator(
                ">=",
                _SemVer(lower.major or 0, lower.minor, 0,
                        lower.prerelease_ids, ()),
            )
        )
    else:
        comparators.append(
            _Comparator(
                ">=",
                _SemVer(lower.major or 0, lower.minor, lower.patch,
                        lower.prerelease_ids, ()),
            )
        )
    if upper.is_any:
        pass  # '... - x' contributes no upper bound
    elif upper.minor is None:
        comparators.append(
            _Comparator(
                "<",
                _SemVer((upper.major or 0) + 1, 0, 0),
            )
        )
    elif upper.patch is None:
        comparators.append(
            _Comparator(
                "<",
                _SemVer(upper.major or 0, (upper.minor or 0) + 1, 0),
            )
        )
    else:
        comparators.append(
            _Comparator(
                "<=",
                _SemVer(upper.major or 0, upper.minor, upper.patch,
                        upper.prerelease_ids, ()),
            )
        )
    if not comparators:
        comparators.append(_any_comparator())
    return comparators


def _desugar_tilde(partial: _Partial) -> List[_Comparator]:
    """``~`` — patch-level changes (and the pinned minor's series)."""
    if partial.is_any:
        return [_any_comparator()]
    if partial.minor is None:  # ~1 → >=1.0.0 <2.0.0
        return [
            _Comparator(">=", _SemVer(partial.major or 0, 0, 0)),
            _Comparator("<", _SemVer((partial.major or 0) + 1, 0, 0)),
        ]
    lower = partial.as_version()
    upper = _SemVer(partial.major or 0, (partial.minor or 0) + 1, 0)
    return [_Comparator(">=", lower), _Comparator("<", upper)]


def _desugar_caret(partial: _Partial) -> List[_Comparator]:
    """``^`` — compatible per the leftmost-non-zero special cases."""
    if partial.is_any:
        return [_any_comparator()]
    major = partial.major or 0
    lower = partial.as_version()
    if partial.minor is None:
        # ^1 → >=1.0.0 <2.0.0 ; ^0 → >=0.0.0 <1.0.0
        upper = _SemVer(major + 1, 0, 0)
    elif partial.patch is None:
        if major > 0:  # ^1.2 → >=1.2.0 <2.0.0
            upper = _SemVer(major + 1, 0, 0)
        else:  # ^0.2 → >=0.2.0 <0.3.0 ; ^0.0 → >=0.0.0 <0.1.0
            upper = _SemVer(0, (partial.minor or 0) + 1, 0)
    else:
        if major > 0:  # ^1.2.3 → >=1.2.3 <2.0.0
            upper = _SemVer(major + 1, 0, 0)
        elif partial.minor > 0:  # ^0.2.3 → >=0.2.3 <0.3.0
            upper = _SemVer(0, partial.minor + 1, 0)
        else:  # ^0.0.3 → >=0.0.3 <0.0.4
            upper = _SemVer(0, 0, (partial.patch or 0) + 1)
    return [_Comparator(">=", lower), _Comparator("<", upper)]


def _desugar_primitive(
    op: str,
    partial: _Partial,
    token: str,
    position: int,
    branch: int,
) -> List[_Comparator]:
    """Comparison operators with npm partial right-hand sides."""
    if partial.is_any:
        # '>*' / '<x' match nothing; '>=*' / '<=*' / '=*' mean any.
        if op in (">", "<"):
            return [_never_comparator()]
        return [_any_comparator()]
    major = partial.major or 0
    if partial.minor is None:
        # Whole-major partials: >1 → >=2.0.0, <1 → <1.0.0,
        # <=1 → <2.0.0, >=1 → >=1.0.0, =1 → >=1.0.0 <2.0.0.
        if op == ">":
            return [_Comparator(">=", _SemVer(major + 1, 0, 0))]
        if op == "<":
            return [_Comparator("<", _SemVer(major, 0, 0))]
        if op == "<=":
            return [_Comparator("<", _SemVer(major + 1, 0, 0))]
        if op == ">=":
            return [_Comparator(">=", _SemVer(major, 0, 0))]
        return [
            _Comparator(">=", _SemVer(major, 0, 0)),
            _Comparator("<", _SemVer(major + 1, 0, 0)),
        ]
    if partial.patch is None:
        minor = partial.minor or 0
        # >1.2 → >=1.3.0, <1.2 → <1.2.0, <=1.2 → <1.3.0,
        # >=1.2 → >=1.2.0, =1.2 → >=1.2.0 <1.3.0.
        if op == ">":
            return [_Comparator(">=", _SemVer(major, minor + 1, 0))]
        if op == "<":
            return [_Comparator("<", _SemVer(major, minor, 0))]
        if op == "<=":
            return [_Comparator("<", _SemVer(major, minor + 1, 0))]
        if op == ">=":
            return [_Comparator(">=", _SemVer(major, minor, 0))]
        return [
            _Comparator(">=", _SemVer(major, minor, 0)),
            _Comparator("<", _SemVer(major, minor + 1, 0)),
        ]
    # Full version right-hand side: the comparator carries the
    # pre-release verbatim (this is what feeds the npm gating rule).
    version = partial.as_version()
    if op == "=":
        return [_exact_comparator(version)]
    return [_Comparator(op, version)]


def _desugar_token(
    token: str,
    position: int,
    branch: int,
) -> List[_Comparator]:
    """Desugar one whitespace-separated comparator token."""
    body = token
    op = ""
    for candidate in _OPERATORS:
        if body.startswith(candidate):
            op = candidate
            body = body[len(candidate):]
            break
    sigil = ""
    if body[:1] in ("~", "^"):
        sigil = body[0]
        body = body[1:]
    if not body:
        raise _RangeError(
            f"the comparator is incomplete — {token!r} has an operator "
            f"with no version following it",
            position, token, branch,
        )
    if op and sigil:
        raise _RangeError(
            f"the ~ and ^ shortcuts cannot be combined with a "
            f"comparison operator — got {token!r}",
            position, token, branch,
        )
    partial, message = _parse_partial(body)
    if partial is None:
        raise _RangeError(
            message or f"invalid comparator version in {token!r}",
            position, token, branch,
        )
    if sigil == "~":
        return _desugar_tilde(partial)
    if sigil == "^":
        return _desugar_caret(partial)
    if op:
        return _desugar_primitive(op, partial, token, position, branch)
    if partial.is_any:  # bare '*' / 'x'
        return [_any_comparator()]
    if partial.patch is not None:  # bare full version = exact
        return [_exact_comparator(partial.as_version())]
    if partial.minor is not None:  # bare '1.2' / '1.2.x'
        major, minor = partial.major or 0, partial.minor
        return [
            _Comparator(">=", _SemVer(major, minor, 0)),
            _Comparator("<", _SemVer(major, minor + 1, 0)),
        ]
    major = partial.major or 0  # bare '1' / '1.x'
    return [
        _Comparator(">=", _SemVer(major, 0, 0)),
        _Comparator("<", _SemVer(major + 1, 0, 0)),
    ]


def _glued_tokens(text: str, offset: int) -> List[Tuple[str, int]]:
    """Whitespace-split tokens with npm's operator gluing applied.

    npm tolerates whitespace between a comparator operator and its
    version (``>= 1.2.3``); its comparator-trim pass glues them back
    together before parsing. A token made purely of operator
    characters pulls in the following token(s); the reported position
    stays that of the first (operator) token.
    """
    raw = [(m.group(), offset + m.start())
           for m in _TOKEN_SPLIT.finditer(text)]
    glued: List[Tuple[str, int]] = []
    index = 0
    while index < len(raw):
        token, position = raw[index]
        while (
            token
            and all(ch in _OP_CHARS for ch in token)
            and index + 1 < len(raw)
        ):
            index += 1
            token += raw[index][0]
        glued.append((token, position))
        index += 1
    return glued


def _parse_branch(
    text: str,
    offset: int,
    branch: int,
) -> _Branch:
    """Parse one union branch (hyphen form or comparator AND list)."""
    stripped = text.strip()
    if not stripped:
        return _Branch([_any_comparator()])  # empty branch means '*'
    hyphens = list(_HYPHEN_SPLIT.finditer(text))
    if len(hyphens) > 1:
        first = hyphens[1]
        raise _RangeError(
            "a hyphen range must contain exactly one ' - ' separator "
            f"— got {len(hyphens)}",
            offset + first.start(), text.strip()[:64], branch,
        )
    if hyphens:
        match = hyphens[0]
        lower_text = text[: match.start()].strip()
        upper_text = text[match.end():].strip()
        if not lower_text or not upper_text:
            raise _RangeError(
                "a hyphen range needs a version on both sides of "
                f"' - ' (got {stripped[:64]!r})",
                offset, stripped[:64], branch,
            )
        comparators = _desugar_hyphen(
            lower_text, upper_text, offset + match.start(), branch
        )
        return _Branch(comparators)
    comparators: List[_Comparator] = []
    for token, position in _glued_tokens(text, offset):
        comparators.extend(_desugar_token(token, position, branch))
    # ANY comparators are no-ops; drop them unless they are all there is.
    real = [c for c in comparators if not c.is_any]
    return _Branch(real if real else [_any_comparator()])


def _parse_range(text: str) -> List[_Branch]:
    """Parse a full range expression into ``||`` union branches."""
    branches: List[_Branch] = []
    start = 0
    spans: List[Tuple[int, int]] = []
    for match in _UNION_SPLIT.finditer(text):
        spans.append((start, match.start()))
        start = match.end()
    spans.append((start, len(text)))
    for index, (begin, end) in enumerate(spans):
        branches.append(_parse_branch(text[begin:end], begin, index))
    return branches


def _normalized_range(branches: List[_Branch]) -> str:
    """Canonical range text: ' || '-joined branch comparator lists."""
    if any(
        len(b.comparators) == 1 and b.comparators[0].is_any
        for b in branches
    ):
        return "*"  # a '*' branch absorbs the whole union
    return " || ".join(" ".join(b.texts()) for b in branches)


# --------------------------------------------------------------------- #
# Set-level intersection (bounds merging, exact emptiness)
# --------------------------------------------------------------------- #

class _Bounds:
    """Strongest lower / upper bound of a comparator AND list."""

    __slots__ = ("lower", "upper", "exacts", "never")

    def __init__(self, comparators: List[_Comparator]) -> None:
        self.never = any(
            (not c.is_any)
            and c.op == "<"
            and c.version is not None
            and c.version.precedence_key
            == _never_comparator().version.precedence_key  # type: ignore
            for c in comparators
        )
        self.exacts = [c for c in comparators if c.op == ""]
        lowers = [c for c in comparators if c.op in (">", ">=")]
        uppers = [c for c in comparators if c.op in ("<", "<=")]
        self.lower: Optional[_Comparator] = None
        for candidate in lowers:
            if self.lower is None:
                self.lower = candidate
                continue
            key = candidate.version.precedence_key  # type: ignore
            best = self.lower.version.precedence_key  # type: ignore
            if key > best or (
                key == best and candidate.op == ">"
                and self.lower.op == ">="
            ):
                self.lower = candidate
        self.upper: Optional[_Comparator] = None
        for candidate in uppers:
            if self.upper is None:
                self.upper = candidate
                continue
            key = candidate.version.precedence_key  # type: ignore
            best = self.upper.version.precedence_key  # type: ignore
            if key < best or (
                key == best and candidate.op == "<"
                and self.upper.op == "<="
            ):
                self.upper = candidate


def _release_window(
    bounds: _Bounds,
) -> Tuple[Tuple[int, int, int], Optional[Tuple[int, int, int]]]:
    """Half-open window of release triples ``[lo, hi)`` of the bounds.

    ``hi`` is ``None`` when unbounded above (infinity).
    """
    if bounds.lower is None:
        lo = (0, 0, 0)
    else:
        version = bounds.lower.version  # type: ignore
        assert version is not None
        if bounds.lower.op == ">=" or version.is_prerelease:
            lo = version.core_tuple
        else:  # '>' on a release excludes its own triple
            lo = _next_triple(version.core_tuple)
    if bounds.upper is None:
        return lo, None
    version = bounds.upper.version  # type: ignore
    assert version is not None
    if bounds.upper.op == "<=" and not version.is_prerelease:
        hi = _next_triple(version.core_tuple)
    else:
        # '<' on a release, and any bound on a pre-release, exclude
        # the bound version's own release triple.
        hi = version.core_tuple
    return lo, hi


def _set_nonempty(bounds: _Bounds, gating: set) -> bool:
    """Whether any version satisfies the merged comparators (exact).

    ``gating`` holds the triples whose pre-releases EVERY input
    branch admits (npm per-branch gating ANDed across the set).
    A release fits when a triple sits inside the half-open window;
    otherwise a gated pre-release triple must clear both bounds
    (a pre-release can always be grown above a pre-release bound or
    shrunk below an upper bound, so only equality conflicts rule a
    triple out).
    """
    if bounds.never:
        return False
    if bounds.exacts:
        if len(bounds.exacts) > 1:
            keys = {
                c.version.precedence_key for c in bounds.exacts  # type: ignore
            }
            if len(keys) > 1:
                return False
        exact = bounds.exacts[0].version  # type: ignore
        assert exact is not None
        for comparator in (bounds.lower, bounds.upper):
            if comparator is not None and not comparator.test(exact):
                return False
        if exact.is_prerelease and exact.core_tuple not in gating:
            return False
        return True
    lo, hi = _release_window(bounds)
    if hi is None or lo < hi:
        return True  # a release triple fits the window
    lower = bounds.lower
    upper = bounds.upper
    for triple in sorted(gating):
        # Lower feasibility: strictly above the bound's triple, or on
        # the same triple as a pre-release bound (which a longer
        # pre-release can exceed); a release bound sits above every
        # pre-release of its own triple.
        if lower is not None:
            lower_triple = lower.version.core_tuple  # type: ignore
            if triple < lower_triple:
                continue
            if (
                triple == lower_triple
                and not lower.version.is_prerelease  # type: ignore
            ):
                continue
        # Upper feasibility: strictly below the bound's triple, or on
        # the same triple (a pre-release of T is always below T's
        # release and can be shrunk below a T pre-release bound).
        if upper is not None:
            upper_triple = upper.version.core_tuple  # type: ignore
            if triple > upper_triple:
                continue
        # Equality conflict: both bounds on the same pre-release
        # triple — feasible only when the open interval between the
        # two pre-release versions is non-empty (or collapses to one
        # admissible version for >= with <=).
        if (
            lower is not None
            and upper is not None
            and triple == lower.version.core_tuple  # type: ignore
            and triple == upper.version.core_tuple  # type: ignore
            and lower.version.is_prerelease  # type: ignore
            and upper.version.is_prerelease  # type: ignore
        ):
            low_key = lower.version.precedence_key  # type: ignore
            high_key = upper.version.precedence_key  # type: ignore
            if low_key > high_key:
                continue
            if low_key == high_key and not (
                lower.op == ">=" and upper.op == "<="
            ):
                continue
        return True
    return False


def _simplify_branches(
    branches: List[_Branch],
) -> Optional[List[_Comparator]]:
    """Merge one branch per constraint into a single AND set.

    ``None`` when the merged set admits no version at all. This is
    the N-way generalization of the pairwise merge: comparators are
    concatenated, the strongest lower / upper bound wins and the
    pre-release gating triples are intersected across every branch.
    """
    merged: List[_Comparator] = [
        c for branch in branches for c in branch.comparators
        if not c.is_any
    ]
    gating: Optional[set] = None
    for branch in branches:
        if gating is None:
            gating = set(branch.gating_triples)
        else:
            gating &= branch.gating_triples
    if not merged:
        return [_any_comparator()]  # every input branch was '*'
    assert gating is not None  # at least one branch reached this point
    bounds = _Bounds(merged)
    if not _set_nonempty(bounds, gating):
        return None
    if bounds.exacts:
        keys = {
            c.version.precedence_key for c in bounds.exacts  # type: ignore
        }
        if len(keys) == 1:
            return [bounds.exacts[0]]
        return None
    simplified: List[_Comparator] = []
    if bounds.lower is not None:
        simplified.append(bounds.lower)
    if bounds.upper is not None:
        simplified.append(bounds.upper)
    if not simplified:
        simplified.append(_any_comparator())
    return simplified


def _ranges_intersect(branches_a: List[_Branch],
                      branches_b: List[_Branch]) -> bool:
    """Whether two parsed ranges share at least one version.

    A version may pick its branch from either side of the ``||``
    unions, so the ranges intersect as soon as any branch pair is
    non-empty; the emptiness decision per pair is exact (release
    windows plus per-triple prerelease gating).
    """
    for branch_a in branches_a:
        for branch_b in branches_b:
            if _simplify_branches([branch_a, branch_b]) is not None:
                return True
    return False


def _triple_total(triple: Tuple[int, int, int]) -> int:
    """Scalar position of a triple on the discrete version lattice."""
    return (
        triple[0] * _MAJOR_UNITS
        + triple[1] * _MINOR_UNITS
        + triple[2]
    )


def _constraint_tightness(
    branches: List[_Branch],
) -> Tuple[bool, float, Dict[str, Any]]:
    """Best-effort tightness metric of one parsed constraint.

    Returns ``(is_exact_pin, width, span)`` where ``span`` holds the
    footprint release window — the leftmost lower bound to the
    rightmost upper bound over all union branches (an overestimate
    for unions: the covered set may have holes between branches) —
    and ``width`` is the window's span in discrete steps (infinite
    when unbounded above). An exact pin (a single branch holding a
    single ``=version`` comparator) is flagged and always wins.
    """
    is_exact_pin = (
        len(branches) == 1
        and len(branches[0].comparators) == 1
        and branches[0].comparators[0].op == ""
        and not branches[0].comparators[0].is_any
    )
    lo: Tuple[int, int, int] = (0, 0, 0)
    hi: Optional[Tuple[int, int, int]] = None
    unbounded = False
    for branch in branches:
        bounds = _Bounds(
            [c for c in branch.comparators if not c.is_any]
        )
        if is_exact_pin:
            lo = hi = bounds.exacts[0].version.core_tuple  # type: ignore
            break
        branch_lo, branch_hi = _release_window(bounds)
        if branch_lo > lo:
            lo = branch_lo
        if branch_hi is None:
            unbounded = True  # this branch has no upper bound at all
        elif hi is None:
            hi = branch_hi
        elif branch_hi > hi:
            hi = branch_hi
    if unbounded and not is_exact_pin:
        hi = None
    if is_exact_pin:
        width = 0.0
    elif hi is None:
        width = float("inf")
    else:
        width = float(_triple_total(hi) - _triple_total(lo))
    span = {
        "lower_triple": list(lo),
        "upper_triple": list(hi) if hi is not None else None,
    }
    return is_exact_pin, width, span


class VersionConstraintTool(Tool):
    """Dependency constraint-set resolution tool (pure stdlib).

    Attributes:
        max_chars (int): Upper bound on any single string input;
            longer inputs are rejected before any work.
        max_constraints (int): Upper bound on the number of range
            constraints of a set.
        max_versions (int): Upper bound on the number of available
            versions of the ``resolve`` mode.
        max_reported (int): Number of junk available-version entries
            reported individually (the rest are only counted).
        max_combinations (int): Number of union-branch combinations
            expanded by the ``explain_set`` mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "version_constraint_tool"
    description: str = (
        "Dependency constraint-set resolution tool — pure Python "
        "stdlib, no network required. Resolve a group of npm-style "
        "range constraints on one package against its available "
        "versions (mode='resolve': satisfiable verdict, the satisfying "
        "candidates sorted by semver precedence, the best (highest) "
        "pick, the binding constraint that eliminated the most "
        "candidates and a per-constraint matched/excluded breakdown), "
        "detect pairwise conflicts in a constraint set (mode="
        "'conflicts': pairs of ranges with an empty intersection plus "
        "the tightest constraint) and explain the whole set "
        "(mode='explain_set': each range's comparator expansion "
        "side-by-side plus the computed intersection bounds). Full "
        "npm grammar: tilde ~, caret ^ with the 0.x special cases, "
        "hyphen ranges with partial upper bounds, x-ranges (1.2.x, *), "
        "comparison primitives with partial right-hand sides, "
        "whitespace AND conjunctions, || unions, and the npm "
        "prerelease rule (a prerelease only matches when a comparator "
        "of the matching branch carries a prerelease on the same "
        "major.minor.patch tuple)."
    )

    MODES: ClassVar[tuple] = (
        "resolve",
        "conflicts",
        "explain_set",
    )

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        constraints: Any = None,
        available_versions: Any = None,
    ) -> Dict[str, Any]:
        """Run one constraint-set operation.

        Args:
            mode (str): One of ``resolve`` / ``conflicts`` /
                ``explain_set``.
            constraints (list[str]): The constraint set — a list of
                npm range expressions that all apply to the same
                package (required for every mode, bounded to 100
                entries).
            available_versions (list[str]): The versions of the
                package that exist — required for the ``resolve``
                mode (bounded to 1,000 entries); junk entries are
                reported per item instead of failing the run.

        Returns:
            Dict[str, Any]: The operation result — a structured
                payload per mode — or a structured ``error`` payload
                for content-level failures (a malformed range with
                the 0-based character ``position`` of the offending
                fragment and its ``constraint_index``).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} "
                f"(got {mode!r})"
            )
        if mode == "resolve":
            return self._run_resolve(constraints, available_versions)
        if mode == "conflicts":
            return self._run_conflicts(constraints)
        return self._run_explain_set(constraints)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"version_constraint_tool: {message}")

    @classmethod
    def _validate_string(cls, value: Any, name: str) -> str:
        """Validate a string input parameter (type / emptiness)."""
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
        ):
            cls._invalid(f"{name} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{name} must be a non-empty string (got '')")
        if len(value) > _MAX_CHARS:
            cls._invalid(
                f"{name} exceeds the {_MAX_CHARS:,}-character limit "
                f"(got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _validate_constraints(cls, value: Any) -> List[str]:
        """Validate the ``constraints`` list parameter."""
        if value is None or isinstance(value, (str, bytes)) or not (
            isinstance(value, (list, tuple))
        ):
            cls._invalid(
                f"constraints must be a list of npm range strings "
                f"(got {value!r})"
            )
        if not value:
            cls._invalid("constraints must be a non-empty list")
        if len(value) > _MAX_CONSTRAINTS:
            cls._invalid(
                f"constraints exceeds the {_MAX_CONSTRAINTS:,}-entry "
                f"limit (got {len(value):,} entries)"
            )
        cleaned: List[str] = []
        for entry in value:
            if (
                entry is None
                or isinstance(entry, bool)
                or not isinstance(entry, str)
            ):
                cls._invalid(
                    f"every constraints entry must be a string "
                    f"(got {entry!r})"
                )
            if not entry:
                cls._invalid(
                    "every constraints entry must be a non-empty string"
                )
            if len(entry) > _MAX_CHARS:
                cls._invalid(
                    f"a constraints entry exceeds the {_MAX_CHARS:,}-"
                    f"character limit (got {len(entry):,} characters)"
                )
            cleaned.append(entry)
        return cleaned

    @classmethod
    def _validate_versions(cls, value: Any) -> List[str]:
        """Validate the ``available_versions`` list parameter."""
        if value is None or isinstance(value, (str, bytes)) or not (
            isinstance(value, (list, tuple))
        ):
            cls._invalid(
                f"available_versions must be a list of version strings "
                f"(got {value!r})"
            )
        if not value:
            cls._invalid("available_versions must be a non-empty list")
        if len(value) > _MAX_VERSIONS:
            cls._invalid(
                f"available_versions exceeds the {_MAX_VERSIONS:,}-entry "
                f"limit (got {len(value):,} entries)"
            )
        cleaned: List[str] = []
        for entry in value:
            if (
                entry is None
                or isinstance(entry, bool)
                or not isinstance(entry, str)
            ):
                cls._invalid(
                    f"every available_versions entry must be a string "
                    f"(got {entry!r})"
                )
            if not entry:
                cls._invalid(
                    "every available_versions entry must be a non-empty "
                    "string"
                )
            if len(entry) > _MAX_CHARS:
                cls._invalid(
                    f"an available_versions entry exceeds the "
                    f"{_MAX_CHARS:,}-character limit "
                    f"(got {len(entry):,} characters)"
                )
            cleaned.append(entry)
        return cleaned

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any],
        error_type: str,
        message: str,
        **details: Any,
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        error: Dict[str, Any] = {
            "type": error_type,
            "message": str(message)[:500],
        }
        error.update(details)
        return {**context, "error": error}

    def _parse_constraint_set(
        self,
        cleaned: List[str],
        context: Dict[str, Any],
    ) -> Any:
        """Validate + parse every constraint; error payload on junk.

        Returns a list of ``(raw_text, branches)`` pairs or a
        structured error payload citing the first malformed entry,
        its constraint index and the 0-based character position of
        the offending fragment.
        """
        parsed: List[Tuple[str, List[_Branch]]] = []
        for index, text in enumerate(cleaned):
            try:
                parsed.append((text, _parse_range(text)))
            except _RangeError as exc:
                return self._error_result(
                    context,
                    error_type="invalid_range",
                    message=exc.message,
                    position=exc.position,
                    fragment=exc.fragment[:64],
                    branch=exc.branch,
                    constraint_index=index,
                )
        return parsed

    @staticmethod
    def _per_constraint_rows(
        parsed: List[Tuple[str, List[_Branch]]],
    ) -> List[Dict[str, Any]]:
        """Normalized + expanded metadata row per constraint."""
        return [
            {
                "index": index,
                "constraint": text,
                "normalized": _normalized_range(branches),
                "branches": [branch.texts() for branch in branches],
            }
            for index, (text, branches) in enumerate(parsed)
        ]

    # ------------------------------------------------------------------ #
    # resolve mode
    # ------------------------------------------------------------------ #

    def _run_resolve(
        self,
        constraints: Any,
        available_versions: Any,
    ) -> Dict[str, Any]:
        """Pick the versions satisfying every constraint at once."""
        cleaned = self._validate_constraints(constraints)
        candidates_in = self._validate_versions(available_versions)
        context: Dict[str, Any] = {
            "mode": "resolve",
            "constraints": list(cleaned),
            "available_requested": len(candidates_in),
        }
        parsed = self._parse_constraint_set(cleaned, context)
        if isinstance(parsed, dict):
            return parsed
        # Parse the available pool: junk entries are reported, not fatal.
        pool: List[Tuple[_SemVer, str]] = []
        invalid: List[Dict[str, Any]] = []
        invalid_count = 0
        for index, entry in enumerate(candidates_in):
            version, message = _parse_version(entry)
            if version is None:
                invalid_count += 1
                if len(invalid) < _MAX_REPORTED:
                    invalid.append(
                        {
                            "index": index,
                            "version": entry[:64],
                            "reason": message,
                        }
                    )
                continue
            pool.append((version, entry))
        # One pass per constraint over the pool (each check runs the
        # full npm semantics, prerelease gating included).
        per_constraint: List[Dict[str, Any]] = []
        constraint_matches: List[set] = []
        for index, (_, branches) in enumerate(parsed):
            matched_indexes = {
                pool_index
                for pool_index, (version, _) in enumerate(pool)
                if any(b.matches(version) for b in branches)
            }
            constraint_matches.append(matched_indexes)
            per_constraint.append(
                {
                    "index": index,
                    "constraint": cleaned[index],
                    "normalized": _normalized_range(branches),
                    "matched_count": len(matched_indexes),
                    "excluded_count": len(pool) - len(matched_indexes),
                }
            )
        survivors = constraint_matches[0]
        for matched_indexes in constraint_matches[1:]:
            survivors &= matched_indexes
        candidates = [pool[i][1] for i in sorted(
            survivors, key=lambda i: pool[i][0].precedence_key
        )]
        # The binding constraint eliminated the most available
        # versions (largest excluded_count; ties → lowest index).
        binding_index = 0
        for index in range(1, len(per_constraint)):
            if (
                per_constraint[index]["excluded_count"]
                > per_constraint[binding_index]["excluded_count"]
            ):
                binding_index = index
        result: Dict[str, Any] = {
            **context,
            "available_count": len(pool),
            "invalid_count": invalid_count,
            "invalid": invalid,
            "satisfiable": bool(candidates),
            "candidates": candidates,
            "best": candidates[-1] if candidates else None,
            "binding_constraint": {
                **per_constraint[binding_index],
            },
            "per_constraint": per_constraint,
            "normalized": [
                row["normalized"] for row in per_constraint
            ],
        }
        if not candidates:
            # Explain the failure: pairwise-empty constraint pairs.
            conflicts: List[Dict[str, Any]] = []
            for i in range(len(parsed)):
                for j in range(i + 1, len(parsed)):
                    if not _ranges_intersect(
                        parsed[i][1], parsed[j][1]
                    ):
                        conflicts.append(
                            {
                                "indexes": [i, j],
                                "constraints": [
                                    cleaned[i], cleaned[j],
                                ],
                            }
                        )
            result["unsatisfiable_because"] = conflicts or None
            if not conflicts:
                result["note"] = (
                    "no two constraints conflict pairwise, yet no "
                    "available version satisfies all of them together "
                    "— either every available version was invalid "
                    "semver, or each surviving version was rejected by "
                    "the npm prerelease gating rule"
                )
        return result

    # ------------------------------------------------------------------ #
    # conflicts mode
    # ------------------------------------------------------------------ #

    def _run_conflicts(self, constraints: Any) -> Dict[str, Any]:
        """Detect pairwise-empty intersections inside a constraint set."""
        cleaned = self._validate_constraints(constraints)
        context: Dict[str, Any] = {
            "mode": "conflicts",
            "constraints": list(cleaned),
        }
        parsed = self._parse_constraint_set(cleaned, context)
        if isinstance(parsed, dict):
            return parsed
        conflicts: List[Dict[str, Any]] = []
        pairs_checked = 0
        for i in range(len(parsed)):
            for j in range(i + 1, len(parsed)):
                pairs_checked += 1
                if not _ranges_intersect(parsed[i][1], parsed[j][1]):
                    conflicts.append(
                        {
                            "indexes": [i, j],
                            "constraints": [cleaned[i], cleaned[j]],
                            "reason": (
                                "the two ranges share no version at all "
                                "(empty intersection over every union "
                                "branch pair)"
                            ),
                        }
                    )
        # The tightest constraint: exact pins first, then the
        # narrowest release-window footprint (ties → lowest index).
        tightest_index = 0
        tightest_exact = False
        tightest_key: tuple = (1, float("inf"), float("inf"))
        spans: List[Dict[str, Any]] = []
        for index, (_, branches) in enumerate(parsed):
            is_exact, width, span = _constraint_tightness(branches)
            spans.append(span)
            key = (0 if is_exact else 1, width, index)
            if key < tightest_key:
                tightest_key = key
                tightest_index = index
                tightest_exact = is_exact
        return {
            **context,
            "count": len(parsed),
            "normalized": [
                _normalized_range(branches) for _, branches in parsed
            ],
            "pairs_checked": pairs_checked,
            "conflict_free": not conflicts,
            "conflicts": conflicts,
            "tightest": {
                "index": tightest_index,
                "constraint": cleaned[tightest_index],
                "normalized": _normalized_range(
                    parsed[tightest_index][1]
                ),
                "exact": tightest_exact,
                "span": spans[tightest_index],
            },
            "note": (
                "the emptiness verdict per pair is exact for release "
                "versions and per-triple for gated prereleases; the "
                "'tightest' ranking is best-effort — an exact pin "
                "wins, otherwise the narrowest release-window "
                "footprint (for a || union the footprint spans from "
                "the leftmost lower bound to the rightmost upper "
                "bound and may cover holes between branches)"
            ),
        }

    # ------------------------------------------------------------------ #
    # explain_set mode
    # ------------------------------------------------------------------ #

    def _run_explain_set(self, constraints: Any) -> Dict[str, Any]:
        """Expand every constraint and fold the set intersection."""
        cleaned = self._validate_constraints(constraints)
        context: Dict[str, Any] = {
            "mode": "explain_set",
            "constraints": list(cleaned),
        }
        parsed = self._parse_constraint_set(cleaned, context)
        if isinstance(parsed, dict):
            return parsed
        rows = self._per_constraint_rows(parsed)
        simple = all(len(branches) == 1 for _, branches in parsed)
        if simple:
            folded = _simplify_branches(
                [branches[0] for _, branches in parsed]
            )
            if folded is None:
                intersection: Dict[str, Any] = {
                    "simple": True,
                    "empty": True,
                    "expression": None,
                    "lower": None,
                    "upper": None,
                    "window": None,
                }
            else:
                real = [c for c in folded if not c.is_any]
                bounds = _Bounds(real) if real else _Bounds([])
                lower_text = (
                    bounds.lower.text() if bounds.lower is not None
                    else None
                )
                upper_text = (
                    bounds.upper.text() if bounds.upper is not None
                    else None
                )
                if not real:
                    expression = "*"
                    window = {
                        "lower_triple": [0, 0, 0],
                        "upper_triple": None,
                    }
                elif bounds.exacts:
                    # A pin collapses the window onto one triple.
                    triple = bounds.exacts[0].version.core_tuple  # type: ignore
                    expression = bounds.exacts[0].text()
                    window = {
                        "lower_triple": list(triple),
                        "upper_triple": list(triple),
                    }
                else:
                    lo, hi = _release_window(bounds)
                    expression = " ".join(c.text() for c in folded)
                    window = {
                        "lower_triple": list(lo),
                        "upper_triple": list(hi) if hi is not None
                        else None,
                    }
                intersection = {
                    "simple": True,
                    "empty": False,
                    "expression": expression,
                    "lower": lower_text,
                    "upper": upper_text,
                    "window": window,
                }
            intersection["note"] = (
                "every constraint is single-branch, so the intersection "
                "is the strongest merged lower/upper bound; the window "
                "is the half-open [lower, upper) range of release "
                "triples (upper_triple null = unbounded). The printed "
                "expression captures release semantics exactly and may "
                "admit same-tuple prereleases that only one input "
                "constraint would accept (npm gates prereleases per "
                "union branch)"
            )
        else:
            # Unions present: fold every branch combination instead
            # (best-effort, bounded to max_combinations entries).
            combinations: List[Dict[str, Any]] = []
            branch_counts = [len(branches) for _, branches in parsed]
            total = 1
            for count in branch_counts:
                total *= count
            index_lists = itertools.product(*[
                range(count) for count in branch_counts
            ])
            for branch_indexes in index_lists:
                if len(combinations) >= _MAX_COMBINATIONS:
                    combinations.append(
                        {
                            "branch_indexes": None,
                            "truncated": True,
                            "note": (
                                f"only the first {_MAX_COMBINATIONS} of "
                                f"{total:,} union-branch combinations "
                                "are expanded"
                            ),
                        }
                    )
                    break
                branches = [
                    parsed[i][1][branch_indexes[i]]
                    for i in range(len(parsed))
                ]
                folded = _simplify_branches(branches)
                combinations.append(
                    {
                        "branch_indexes": list(branch_indexes),
                        "empty": folded is None,
                        "expression": (
                            " ".join(c.text() for c in folded)
                            if folded is not None else None
                        ),
                    }
                )
            combinations.sort(
                key=lambda row: (
                    row.get("branch_indexes") is None,
                    row.get("branch_indexes") or [],
                    row.get("expression") or "",
                )
            )
            truncated = any(
                row.get("truncated") for row in combinations
            )
            if truncated:
                empty: Optional[bool] = None  # not all pairs expanded
            else:
                empty = not any(
                    not row["empty"] for row in combinations
                )
            intersection = {
                "simple": False,
                "empty": empty,
                "expression": None,
                "combinations": combinations,
                "note": (
                    "at least one constraint uses a || union, so the "
                    "set intersection is the union over all "
                    "branch-pair combinations (each combination merged "
                    "by AND into its strongest bounds); best-effort "
                    "as documented — a combination's expression "
                    "captures release semantics and may admit "
                    "same-tuple prereleases that only one input branch "
                    "would accept"
                ),
            }
        return {
            **context,
            "constraints": rows,
            "intersection": intersection,
        }
