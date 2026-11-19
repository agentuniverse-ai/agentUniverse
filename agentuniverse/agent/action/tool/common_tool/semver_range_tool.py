#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: semver_range_tool.py

"""npm-style semantic-version *range* tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the dependency-management layer on top of semantic
versioning: given a concrete ``X.Y.Z`` version and an npm
``package.json`` style range expression, decide compatibility — the
question every ``npm install`` / ``npm update`` / lockfile audit has
to answer.

Where a version *parsing / comparing / bumping* helper covers single
versions, this tool implements the full **range grammar** documented
by npm's ``node-semver``: the tilde and caret shortcuts, hyphen
ranges, x-ranges (``1.2.x`` / ``*``), comparison primitives with
partial right-hand sides, whitespace-separated AND conjunctions,
``||`` unions — and the notorious npm **prerelease rule** (a version
with a pre-release only satisfies a range when at least one
comparator of the matching union branch carries a pre-release on the
same ``major.minor.patch`` tuple, so ``1.2.3-alpha`` satisfies
``^1.2.3-alpha`` but NOT ``>=1.2.3``).

Four modes:

* ``satisfies`` — does one version satisfy a range? Returns the
  boolean verdict, the index and expanded comparator list of the
  first matching ``||`` union branch (or ``None``), the parsed
  version fields and the normalized range.
* ``explain`` — expand a range into its union branches of primitive
  comparators, exactly the desugaring npm applies:
  ``^1.2.3`` → ``[">=1.2.3", "<2.0.0"]``, ``~1.2.3`` →
  ``[">=1.2.3", "<1.3.0"]``, ``1.2.x`` → ``[">=1.2.0", "<1.3.0"]``,
  ``1.2.3 - 2.3`` → ``[">=1.2.3", "<2.4.0"]`` (a partial hyphen upper
  bound excludes the whole next ``.0`` series), ``^0.2.3`` →
  ``[">=0.2.3", "<0.3.0"]`` and ``^0.0.3`` → ``[">=0.0.3",
  "<0.0.4"]`` (the 0.x / 0.0.x caret special cases), ``>1.2`` →
  ``[">=1.3.0"]`` and ``<=1.2`` → ``["<1.3.0"]`` (partial comparator
  right-hand sides).
* ``versions`` — filter and sort a candidate list against a range:
  the satisfying versions ascending by semver precedence (the
  ``min/maxSatisfying`` building block), the count, the highest and
  lowest match, a sample of rejected versions and per-entry reasons
  for list items that are not valid semver at all.
* ``intersect`` — intersect two ranges into a simplified equivalent
  (or an ``empty`` verdict when no version can satisfy both).
  Best-effort by design and documented as such: each union-branch
  pair of the two inputs is merged into one AND comparator set, the
  strongest lower / upper bound is kept, and emptiness is decided
  exactly (a release triple must fit the bounds, or a pre-release
  whose tuple is gated on *both* sides). The printed expression
  captures release semantics exactly; it may admit same-tuple
  pre-releases that only one input range would have rejected, since
  npm gates pre-releases per union branch rather than per bound.

Grammar accepted (strict npm subset, all offline): union branches
split on ``||``; a branch is either a hyphen range ``partial -
partial`` (spaces required, as in npm) or one-or-more
whitespace-separated comparators ANDed together; a comparator is a
primitive (``> >= < <= =`` + partial), a tilde ``~partial``, a caret
``^partial``, a bare x-range (``1.2.x``, ``1.2``, ``1``, ``*``) or a
full version (exact match); partials allow x / X / * placeholders
(any component after an x placeholder is collapsed, npm-style); a
pre-release requires a full ``X.Y.Z`` core and follows the semver
2.0.0 identifier rules; build metadata is accepted and ignored; a
leading ``v`` is stripped; whitespace between an operator and its
version is tolerated and glued (npm's comparator-trim behavior,
``>= 1.2.3`` ≡ ``>=1.2.3``); an entirely empty branch means ``*``.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, missing / empty / oversized
strings — ranges and versions are capped at 1,000 characters, the
candidate list at 1,000 entries) raise a ``ValueError``, mirroring
the other common tools. Errors that depend on the *content being
processed* — a version that is not strict semver, a malformed range —
are returned as a structured ``error`` payload (invalid ranges cite
the 0-based character ``position`` of the offending fragment, its
``branch`` index and the ``fragment`` text) so an agent can react
without catching exceptions. Unlike npm — which silently turns an
unparseable comparator into a matches-nothing ``<0.0.0-0`` — this
tool reports malformed ranges explicitly; the genuine npm
matches-nothing desugarings that are *valid grammar* (``>*`` →
``<0.0.0-0``, contradictory exact comparators) are kept.
"""

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

# Input length limits (range expressions and versions are short; the
# bounds exist purely to reject pathological inputs early).
_MAX_CHARS = 1_000
_MAX_VERSIONS = 1_000
# How many rejected/invalid list entries are reported individually.
_MAX_REPORTED = 50


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
                    f"alphanumerics and hyphens [0-9A-Za-z-] — got {part!r}"
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

    def sort_key(self) -> tuple:
        """Key for dedupe / strength comparisons."""
        if self.is_any:
            return ("*", ())
        return (self.op, self.version.precedence_key)  # type: ignore


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
    """One union branch: an AND of comparators plus its source span."""

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
# Branch intersection (best-effort, documented)
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


def _pair_nonempty(bounds: _Bounds, gating: set) -> bool:
    """Whether any version satisfies the merged comparators (exact).

    ``gating`` holds the triples whose pre-releases BOTH input
    branches admit (npm per-branch gating ANDed across the pair).
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


def _simplify_pair(
    branch_a: _Branch,
    branch_b: _Branch,
) -> Optional[List[_Comparator]]:
    """Merge two union branches; ``None`` when the pair is empty."""
    merged: List[_Comparator] = [
        c for c in branch_a.comparators + branch_b.comparators
        if not c.is_any
    ]
    gating = branch_a.gating_triples & branch_b.gating_triples
    bounds = _Bounds(merged)
    if not _pair_nonempty(bounds, gating):
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


class SemverRangeTool(Tool):
    """npm-style semantic-version range tool built purely on the stdlib.

    Attributes:
        max_chars (int): Upper bound on any single string input;
            longer inputs are rejected before any work.
        max_versions (int): Upper bound on the number of candidate
            versions of the ``versions`` mode.
        max_reported (int): Number of rejected / invalid candidate
            entries reported individually (the rest are only
            counted).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "semver_range_tool"
    description: str = (
        "npm-style semantic-version range tool — pure Python stdlib, no "
        "network required. Check whether a version satisfies an npm "
        "package.json range (mode='satisfies'), expand a range into its "
        "primitive comparators (mode='explain'), filter and sort a "
        "candidate list against a range (mode='versions'), and "
        "intersect two ranges into a simplified equivalent or an empty "
        "verdict (mode='intersect'). Full npm grammar: tilde ~, caret ^ "
        "with the 0.x special cases, hyphen ranges with partial upper "
        "bounds, x-ranges (1.2.x, *), comparison primitives with "
        "partial right-hand sides, whitespace AND conjunctions, || "
        "unions, and the npm prerelease rule (a prerelease only "
        "matches when a comparator of the matching branch carries a "
        "prerelease on the same major.minor.patch tuple)."
    )

    MODES: ClassVar[tuple] = (
        "satisfies",
        "explain",
        "versions",
        "intersect",
    )

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        version: Any = None,
        version_range: Any = None,
        versions: Any = None,
        version_range_b: Any = None,
    ) -> Dict[str, Any]:
        """Run one npm-range operation.

        Args:
            mode (str): One of ``satisfies`` / ``explain`` /
                ``versions`` / ``intersect``.
            version (str): The version to check — required for the
                ``satisfies`` mode. An optional leading ``v`` is
                accepted and stripped; build metadata is validated and
                ignored for matching.
            version_range (str): The npm range expression — required
                for every mode; the first range of ``intersect``.
            versions (list[str]): Candidate versions — required for
                the ``versions`` mode (bounded to 1,000 entries).
            version_range_b (str): The second range — required for
                the ``intersect`` mode.

        Returns:
            Dict[str, Any]: The operation result — a structured
            payload per mode — or a structured ``error`` payload for
            content-level failures (a version that is not strict
            semver, a malformed range with the 0-based character
            ``position`` of the offending fragment).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} "
                f"(got {mode!r})"
            )
        if mode == "satisfies":
            return self._run_satisfies(version, version_range)
        if mode == "explain":
            return self._run_explain(version_range)
        if mode == "versions":
            return self._run_versions(version_range, versions)
        return self._run_intersect(version_range, version_range_b)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"semver_range_tool: {message}")

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
    def _validate_versions(cls, value: Any) -> List[str]:
        """Validate the ``versions`` candidate list parameter."""
        if value is None or isinstance(value, (str, bytes)) or not (
            isinstance(value, (list, tuple))
        ):
            cls._invalid(
                f"versions must be a list of version strings "
                f"(got {value!r})"
            )
        if not value:
            cls._invalid("versions must be a non-empty list")
        if len(value) > _MAX_VERSIONS:
            cls._invalid(
                f"versions exceeds the {_MAX_VERSIONS:,}-entry limit "
                f"(got {len(value):,} entries)"
            )
        cleaned: List[str] = []
        for entry in value:
            if (
                entry is None
                or isinstance(entry, bool)
                or not isinstance(entry, str)
            ):
                cls._invalid(
                    f"every versions entry must be a string "
                    f"(got {entry!r})"
                )
            if not entry:
                cls._invalid("every versions entry must be a non-empty string")
            if len(entry) > _MAX_CHARS:
                cls._invalid(
                    f"a versions entry exceeds the {_MAX_CHARS:,}-"
                    f"character limit (got {len(entry):,} characters)"
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

    def _parse_range_param(
        self,
        value: Any,
        name: str,
        context: Dict[str, Any],
    ) -> Any:
        """Validate + parse a range parameter, error payload on junk."""
        clean = self._validate_string(value, name)
        try:
            return _parse_range(clean)
        except _RangeError as exc:
            return self._error_result(
                context,
                error_type="invalid_range",
                message=exc.message,
                position=exc.position,
                fragment=exc.fragment[:64],
                branch=exc.branch,
            )

    # ------------------------------------------------------------------ #
    # satisfies mode
    # ------------------------------------------------------------------ #

    def _run_satisfies(
        self,
        version: Any,
        version_range: Any,
    ) -> Dict[str, Any]:
        """Check one version against a full npm range."""
        clean_version = self._validate_string(version, "version")
        clean_range = self._validate_string(version_range, "version_range")
        context: Dict[str, Any] = {
            "mode": "satisfies",
            "version": clean_version,
            "version_range": clean_range,
        }
        parsed, message = _parse_version(clean_version)
        if parsed is None:
            return self._error_result(
                context,
                error_type="invalid_version",
                message=message or "invalid version",
                which="version",
            )
        branches = self._parse_range_param(
            clean_range, "version_range", context
        )
        if isinstance(branches, dict):
            return branches
        matched: Optional[int] = None
        for index, branch in enumerate(branches):
            if branch.matches(parsed):
                matched = index
                break
        return {
            **context,
            "major": parsed.major,
            "minor": parsed.minor,
            "patch": parsed.patch,
            "prerelease": ".".join(parsed.prerelease_ids) or None,
            "build": ".".join(parsed.build_ids) or None,
            "satisfies": matched is not None,
            "matched_branch": matched,
            "matched_comparators": (
                branches[matched].texts() if matched is not None else None
            ),
            "branches": [branch.texts() for branch in branches],
            "normalized": _normalized_range(branches),
        }

    # ------------------------------------------------------------------ #
    # explain mode
    # ------------------------------------------------------------------ #

    def _run_explain(self, version_range: Any) -> Dict[str, Any]:
        """Expand a range into primitive comparator lists."""
        clean_range = self._validate_string(version_range, "version_range")
        context: Dict[str, Any] = {
            "mode": "explain",
            "version_range": clean_range,
        }
        branches = self._parse_range_param(
            clean_range, "version_range", context
        )
        if isinstance(branches, dict):
            return branches
        return {
            **context,
            "branches": len(branches),
            "comparators": [branch.texts() for branch in branches],
            "normalized": _normalized_range(branches),
        }

    # ------------------------------------------------------------------ #
    # versions mode
    # ------------------------------------------------------------------ #

    def _run_versions(
        self,
        version_range: Any,
        versions: Any,
    ) -> Dict[str, Any]:
        """Filter and sort candidate versions against a range."""
        clean_range = self._validate_string(version_range, "version_range")
        candidates = self._validate_versions(versions)
        context: Dict[str, Any] = {
            "mode": "versions",
            "version_range": clean_range,
            "versions": len(candidates),
        }
        branches = self._parse_range_param(
            clean_range, "version_range", context
        )
        if isinstance(branches, dict):
            return branches
        matches: List[Tuple[_SemVer, str]] = []
        rejected: List[Tuple[_SemVer, str]] = []
        invalid: List[Dict[str, Any]] = []
        invalid_count = 0
        for index, entry in enumerate(candidates):
            parsed, message = _parse_version(entry)
            if parsed is None:
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
            if any(branch.matches(parsed) for branch in branches):
                matches.append((parsed, entry))
            else:
                rejected.append((parsed, entry))
        matches.sort(key=lambda pair: pair[0].precedence_key)
        rejected.sort(key=lambda pair: pair[0].precedence_key)
        return {
            **context,
            "matches_count": len(matches),
            "matches": [entry for _, entry in matches],
            "min_satisfying": matches[0][1] if matches else None,
            "max_satisfying": matches[-1][1] if matches else None,
            "rejected_count": len(rejected),
            "rejected_sample": [
                entry for _, entry in rejected[:_MAX_REPORTED]
            ],
            "invalid_count": invalid_count,
            "invalid": invalid,
            "normalized": _normalized_range(branches),
        }

    # ------------------------------------------------------------------ #
    # intersect mode
    # ------------------------------------------------------------------ #

    def _run_intersect(
        self,
        version_range: Any,
        version_range_b: Any,
    ) -> Dict[str, Any]:
        """Intersect two ranges (best-effort, documented)."""
        clean_a = self._validate_string(version_range, "version_range")
        clean_b = self._validate_string(version_range_b, "version_range_b")
        context: Dict[str, Any] = {
            "mode": "intersect",
            "version_range": clean_a,
            "version_range_b": clean_b,
        }
        branches_a = self._parse_range_param(clean_a, "version_range",
                                             context)
        if isinstance(branches_a, dict):
            return branches_a
        branches_b = self._parse_range_param(clean_b, "version_range_b",
                                             context)
        if isinstance(branches_b, dict):
            return branches_b
        merged_branches: List[List[_Comparator]] = []
        seen: set = set()
        for branch in branches_a:
            for other in branches_b:
                simplified = _simplify_pair(branch, other)
                if simplified is None:
                    continue
                key = tuple(c.text() for c in simplified)
                if key not in seen:
                    seen.add(key)
                    merged_branches.append(simplified)
        if not merged_branches:
            return {
                **context,
                "empty": True,
                "intersection": None,
                "branches": [],
                "note": (
                    "no version can satisfy both ranges — the "
                    "intersection is empty"
                ),
            }
        merged_branches.sort(key=lambda comps: [c.text() for c in comps])
        if any(
            len(comps) == 1 and comps[0].is_any
            for comps in merged_branches
        ):
            intersection = "*"
        else:
            intersection = " || ".join(
                " ".join(c.text() for c in comps)
                for comps in merged_branches
            )
        return {
            **context,
            "empty": False,
            "intersection": intersection,
            "branches": [
                [c.text() for c in comps] for comps in merged_branches
            ],
            "note": (
                "best-effort simplification: branch pairs are merged by "
                "AND and reduced to their strongest bounds; the printed "
                "expression captures release versions exactly and may "
                "admit same-tuple prereleases that only one input "
                "range would accept (npm gates prereleases per union "
                "branch)"
            ),
        }
