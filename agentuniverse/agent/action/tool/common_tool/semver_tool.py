#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: semver_tool.py

"""Semantic Versioning 2.0.0 utility tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency version-string
helper agents can call for release plumbing: checking dependency
versions, deciding update order, or computing the next tag.

The tool implements the strict semver.org 2.0.0 grammar — numeric
identifiers without leading zeroes in the version core and in numeric
pre-release identifiers, ASCII alphanumeric/hyphen identifier charset,
non-empty dot-separated identifiers, optional build metadata in which
numeric identifiers MAY carry leading zeroes — and supports four modes:

* ``parse`` — split a version into ``major`` / ``minor`` / ``patch`` /
  ``prerelease`` / ``build`` and report a validity verdict. Invalid
  versions return ``valid=False`` together with a precise error
  message citing the violated spec section (§2 or §9) instead of
  raising.
* ``compare`` — precedence of two versions per spec §11 as ``-1`` /
  ``0`` / ``1``: numeric comparison of the core, a pre-release has
  lower precedence than the matching release, numeric pre-release
  identifiers compare numerically, alphanumeric ones lexically
  (ASCII), numeric identifiers always rank below alphanumeric ones,
  and a larger set of pre-release identifiers wins when all preceding
  identifiers are equal. Build metadata is ignored for precedence.
* ``bump`` — ``major`` / ``minor`` / ``patch`` / ``prerelease`` /
  ``release`` bumps. ``major``/``minor``/``patch`` reset the lower
  fields and drop any pre-release; ``prerelease`` starts the next
  patch pre-release series on a plain version (``1.2.3`` →
  ``1.2.4-rc.0`` with the default ``rc`` label) and continues the
  series on a pre-release version by incrementing the last numeric
  identifier (``1.2.3-rc.9`` → ``1.2.3-rc.10``; a different label
  switches the pre-release channel on the same core);
  ``release`` strips the pre-release (``1.2.3-rc.1`` → ``1.2.3``).
  Build metadata is never carried into a bumped version.
* ``range`` — simple range checks against the supported subset:
  exact versions (``1.2.3``, optional ``=`` and ignored build
  metadata), comparison comparators (``> >= < <=`` with full
  ``X.Y.Z`` versions), tilde ranges (``~1.2.3`` → ``>=1.2.3
  <1.3.0``, ``~1.2``, ``~1``), caret ranges (``^1.2.3``,
  ``^0.2.3`` → ``>=0.2.3 <0.3.0``, ``^0.0.3`` → ``>=0.0.3
  <0.0.4``, and partials ``^1.2`` / ``^0.0`` / ``^1`` / ``^0``),
  and whitespace-separated AND conjunctions of the above
  (``>=1.2.3 <2.0.0``). NOT supported: ``||`` unions, hyphen
  ranges (``1.2 - 2.0``), x-ranges (``1.2.x`` / ``*``), dist-tags
  (``latest``), and partial versions after comparison operators.
  Like npm/node-semver defaults, a version with a pre-release only
  satisfies a range when at least one comparator carries a
  pre-release on the same ``major.minor.patch`` tuple, so ``~1.2.3``
  does not match ``1.2.4-beta``. Every result reports the
  desugared comparator set as ``expanded``.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty or oversized strings,
unknown mode / level, an invalid pre-release ``label``, a ``label``
outside the ``prerelease`` level) raise a ``ValueError``, mirroring
the other common tools. Errors that depend on the *content being
processed* — an invalid version string, bumping ``release`` on a
version without a pre-release, an unsupported or malformed range —
are returned as a structured ``error`` payload so an agent can react
without catching exceptions.
"""

import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_ASCII_WHITESPACE = re.compile(r"\s")
_NUMERIC = re.compile(r"[0-9]+")
# Spec §9: identifiers comprise ASCII alphanumerics and hyphens.
_IDENTIFIER = re.compile(r"[0-9A-Za-z-]+")

# Input length limits (versions and range expressions are short; the
# bounds exist purely to reject pathological inputs early).
_MAX_VERSION_CHARS = 1_000
_MAX_RANGE_CHARS = 1_000
_MAX_LABEL_CHARS = 64


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
    def prerelease(self) -> str:
        """Dot-joined pre-release identifiers ("" when absent)."""
        return ".".join(self.prerelease_ids)

    @property
    def build(self) -> str:
        """Dot-joined build identifiers ("" when absent)."""
        return ".".join(self.build_ids)

    @property
    def core_tuple(self) -> Tuple[int, int, int]:
        """The (major, minor, patch) triple."""
        return (self.major, self.minor, self.patch)

    @property
    def precedence_key(self) -> tuple:
        """Sort key implementing spec §11 precedence (build ignored).

        The fourth element separates releases (1) from pre-releases
        (0); the fifth encodes identifiers as ``(0, n)`` for numeric
        ones (compared numerically, always below alphanumeric ones)
        and ``(1, s)`` for alphanumeric ones (compared lexically).
        Python tuple comparison then gives numeric comparison of the
        core, numeric < alphanumeric, ASCII lexical order, and the
        larger-identifier-set-wins rule for free.
        """
        if not self.prerelease_ids:
            return (self.major, self.minor, self.patch, 1, ())
        identifiers = tuple(
            (0, int(part)) if _NUMERIC.fullmatch(part) else (1, part)
            for part in self.prerelease_ids
        )
        return (self.major, self.minor, self.patch, 0, identifiers)

    def without_build(self) -> "_SemVer":
        """A copy without build metadata (bump / range bookkeeping)."""
        return _SemVer(
            self.major, self.minor, self.patch, self.prerelease_ids, ()
        )

    def __str__(self) -> str:
        text = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease_ids:
            text += "-" + self.prerelease
        if self.build_ids:
            text += "+" + self.build
        return text


def _parse_semver(
    text: str,
) -> Tuple[Optional[_SemVer], Optional[str], Optional[str]]:
    """Parse a strict semantic version string.

    Returns ``(version, None, None)`` on success or
    ``(None, message, rule)`` on failure, where ``message`` precisely
    describes the first violated rule and ``rule`` cites the spec
    section (e.g. ``"semver 2.0.0 §9"``).
    """

    def failure(
        message: str, rule: str
    ) -> Tuple[None, str, str]:
        return None, message, rule

    if _ASCII_WHITESPACE.search(text):
        return failure(
            f"whitespace is not allowed in a semantic version string "
            f"(got {text[:64]!r})",
            "semver 2.0.0 §9",
        )

    # Build metadata: everything after the first '+'. Numeric build
    # identifiers MAY include leading zeroes (spec §9 / §10).
    core_and_pre, plus, build_part = text.partition("+")
    build_ids: Tuple[str, ...] = ()
    if plus:
        if not build_part:
            return failure(
                "build metadata MUST NOT be empty — '+' must be followed "
                "by dot-separated non-empty build identifiers",
                "semver 2.0.0 §9",
            )
        build_ids = tuple(build_part.split("."))
        for part in build_ids:
            if part == "":
                return failure(
                    f"build identifiers must be non-empty — "
                    f"{build_part[:64]!r} contains an empty identifier",
                    "semver 2.0.0 §9",
                )
            if not _IDENTIFIER.fullmatch(part):
                return failure(
                    f"build identifiers must comprise only ASCII "
                    f"alphanumerics and hyphens [0-9A-Za-z-] — got {part!r}",
                    "semver 2.0.0 §9",
                )

    # Pre-release: everything after the first '-' of the remainder;
    # pre-release identifiers may themselves contain hyphens, so only
    # the first '-' separates core from pre-release.
    core, hyphen, pre_part = core_and_pre.partition("-")
    prerelease_ids: Tuple[str, ...] = ()
    if hyphen:
        if not pre_part:
            return failure(
                "pre-release version MUST NOT be empty — '-' must be "
                "followed by dot-separated non-empty pre-release "
                "identifiers",
                "semver 2.0.0 §9",
            )
        prerelease_ids = tuple(pre_part.split("."))
        for part in prerelease_ids:
            if part == "":
                return failure(
                    f"pre-release identifiers must be non-empty — "
                    f"{pre_part[:64]!r} contains an empty identifier",
                    "semver 2.0.0 §9",
                )
            if not _IDENTIFIER.fullmatch(part):
                return failure(
                    f"pre-release identifiers must comprise only ASCII "
                    f"alphanumerics and hyphens [0-9A-Za-z-] — got {part!r}",
                    "semver 2.0.0 §9",
                )
            if (
                _NUMERIC.fullmatch(part)
                and len(part) > 1
                and part[0] == "0"
            ):
                return failure(
                    f"numeric pre-release identifiers MUST NOT include "
                    f"leading zeroes — got {part!r}",
                    "semver 2.0.0 §9",
                )

    # Version core: exactly three numeric identifiers without leading
    # zeroes (spec §2).
    core_parts = core.split(".")
    if len(core_parts) != 3:
        return failure(
            f"the version core must be exactly three dot-separated "
            f"numeric identifiers 'MAJOR.MINOR.PATCH' — got "
            f"{len(core_parts)} part(s): {core[:64]!r}",
            "semver 2.0.0 §9",
        )
    numbers: List[int] = []
    for name, part in zip(("major", "minor", "patch"), core_parts):
        if part == "":
            return failure(
                f"the {name} version is empty — a semantic version must "
                f"start with 'MAJOR.MINOR.PATCH'",
                "semver 2.0.0 §2",
            )
        if not _NUMERIC.fullmatch(part):
            return failure(
                f"the {name} version must be a non-negative integer "
                f"without leading zeroes — got {part!r}",
                "semver 2.0.0 §2",
            )
        if len(part) > 1 and part[0] == "0":
            return failure(
                f"the {name} version MUST NOT contain leading zeroes — "
                f"got {part!r}",
                "semver 2.0.0 §2",
            )
        numbers.append(int(part))
    return (
        _SemVer(numbers[0], numbers[1], numbers[2], prerelease_ids, build_ids),
        None,
        None,
    )


def _parse_partial(
    text: str,
) -> Tuple[Optional[int], Optional[int], Optional[int], Tuple[str, ...], Optional[str]]:
    """Parse a partial version core (1-3 numeric parts) for tilde/caret.

    Returns ``(major, minor|None, patch|None, prerelease_ids, message)``
    — a non-None ``message`` signals failure. Build metadata is
    accepted and ignored; a pre-release requires a full ``X.Y.Z`` core.
    """
    core_and_pre, plus, build_part = text.partition("+")
    del plus, build_part  # build metadata is ignored in ranges
    core, hyphen, pre_part = core_and_pre.partition("-")
    prerelease_ids: Tuple[str, ...] = ()
    if hyphen:
        if not pre_part:
            return None, None, None, (), (
                "pre-release version MUST NOT be empty — '-' must be "
                "followed by dot-separated non-empty pre-release "
                "identifiers"
            )
        prerelease_ids = tuple(pre_part.split("."))
        for part in prerelease_ids:
            if part == "" or not _IDENTIFIER.fullmatch(part):
                return None, None, None, (), (
                    f"pre-release identifiers must comprise only ASCII "
                    f"alphanumerics and hyphens [0-9A-Za-z-] — got {part!r}"
                )
            if (
                _NUMERIC.fullmatch(part)
                and len(part) > 1
                and part[0] == "0"
            ):
                return None, None, None, (), (
                    f"numeric pre-release identifiers MUST NOT include "
                    f"leading zeroes — got {part!r}"
                )
    parts = core.split(".")
    if not 1 <= len(parts) <= 3:
        return None, None, None, (), (
            f"expected 'MAJOR[.MINOR[.PATCH]]' (1 to 3 dot-separated "
            f"numeric identifiers) — got {len(parts)} part(s): "
            f"{core[:64]!r}"
        )
    if hyphen and len(parts) != 3:
        return None, None, None, (), (
            "a pre-release requires a full X.Y.Z version core "
            f"(got {text[:64]!r})"
        )
    numbers: List[int] = []
    for part in parts:
        if not _NUMERIC.fullmatch(part) or (
            len(part) > 1 and part[0] == "0"
        ):
            return None, None, None, (), (
                f"version identifiers must be non-negative integers "
                f"without leading zeroes — got {part!r}"
            )
        numbers.append(int(part))
    while len(numbers) < 3:
        numbers.append(-1)  # sentinel, converted to None below
    major, minor, patch = (
        numbers[0],
        numbers[1] if numbers[1] >= 0 else None,
        numbers[2] if numbers[2] >= 0 else None,
    )
    return major, minor, patch, prerelease_ids, None


class SemverTool(Tool):
    """Semantic Versioning 2.0.0 utility tool built purely on the stdlib.

    Inputs are bounded: version strings are limited to 1,000
    characters, range expressions to 1,000 characters and prerelease
    labels to 64 characters; longer inputs are rejected before any
    work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "semver_tool"
    description: str = (
        "Semantic versioning (semver 2.0.0) tool — pure Python stdlib, "
        "no network required. Parse a version into "
        "major/minor/patch/prerelease/build with a strict validity "
        "verdict citing the violated spec rule (mode='parse'), compare "
        "two versions by semver precedence rules and get -1/0/1 "
        "(mode='compare'), bump major/minor/patch/prerelease levels or "
        "strip a prerelease for release (mode='bump'), and check simple "
        "ranges — exact versions, comparison operators, tilde and caret "
        "ranges (mode='range')."
    )

    MODES: ClassVar[tuple] = ("parse", "compare", "bump", "range")
    LEVELS: ClassVar[tuple] = ("major", "minor", "patch", "prerelease", "release")
    OPERATORS: ClassVar[tuple] = (">", ">=", "<", "<=", "=")
    DEFAULT_PRERELEASE_LABEL: ClassVar[str] = "rc"

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        version: Any = None,
        version_a: Any = None,
        version_b: Any = None,
        level: Any = None,
        label: Any = None,
        version_range: Any = None,
    ) -> Dict[str, Any]:
        """Run one semantic-versioning operation.

        Args:
            mode (str): One of ``parse`` / ``compare`` / ``bump`` /
                ``range``.
            version (str): The version string — required for the
                ``parse``, ``bump`` and ``range`` modes.
            version_a (str): First comparand — required for the
                ``compare`` mode.
            version_b (str): Second comparand — required for the
                ``compare`` mode.
            level (str): Bump level — ``major`` / ``minor`` / ``patch`` /
                ``prerelease`` / ``release`` — required for the ``bump``
                mode.
            label (str): Pre-release channel label for the
                ``prerelease`` bump level; defaults to ``rc``. Only
                valid together with ``level='prerelease'``.
            version_range (str): The range expression — required for
                the ``range`` mode. Supported: exact versions
                (``1.2.3``, optional ``=``; build metadata is
                ignored), comparators ``> >= < <=`` with full
                ``X.Y.Z`` versions, tilde ranges ``~1.2.3`` /
                ``~1.2`` / ``~1``, caret ranges ``^1.2.3`` /
                ``^0.2.3`` / ``^0.0.3`` / ``^1.2`` / ``^0.0`` /
                ``^1`` / ``^0``, and whitespace-separated AND
                conjunctions. Not supported: ``||`` unions, hyphen
                ranges, x-ranges (``1.2.x`` / ``*``), dist-tags,
                partial versions after comparison operators.

        Returns:
            Dict[str, Any]: The operation result — a structured
            payload per mode (fields for ``parse``; ``result`` plus
            context for the others) or a structured ``error`` payload
            for content-level failures (invalid version, releasing a
            version without a prerelease, unsupported range). Every
            ``range`` result also carries the desugared comparator
            set as ``expanded``.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "parse":
            return self._run_parse(version)
        if mode == "compare":
            return self._run_compare(version_a, version_b)
        if mode == "bump":
            return self._run_bump(version, level, label)
        return self._run_range(version, version_range)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"semver_tool: {message}")

    @classmethod
    def _validate_version_param(cls, value: Any, name: str) -> str:
        """Validate a ``version`` input parameter (type / emptiness)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{name} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{name} must be a non-empty string (got '')")
        if len(value) > _MAX_VERSION_CHARS:
            cls._invalid(
                f"{name} exceeds the {_MAX_VERSION_CHARS:,}-character "
                f"limit (got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _validate_label(cls, label: Any) -> str:
        """Validate the ``prerelease``-level ``label`` parameter."""
        if label is None:
            return cls.DEFAULT_PRERELEASE_LABEL
        if isinstance(label, bool) or not isinstance(label, str):
            cls._invalid(
                f"label must be a non-empty ASCII alphanumeric/hyphen "
                f"identifier (got {label!r})"
            )
        if not label:
            cls._invalid(
                "label must be a non-empty ASCII alphanumeric/hyphen "
                "identifier (got '')"
            )
        if len(label) > _MAX_LABEL_CHARS:
            cls._invalid(
                f"label exceeds the {_MAX_LABEL_CHARS}-character limit "
                f"(got {len(label)} characters)"
            )
        if not _IDENTIFIER.fullmatch(label):
            cls._invalid(
                f"label must comprise only ASCII alphanumerics and "
                f"hyphens [0-9A-Za-z-] (got {label!r})"
            )
        if _NUMERIC.fullmatch(label) and len(label) > 1 and label[0] == "0":
            cls._invalid(
                f"a numeric label must not include leading zeroes "
                f"(got {label!r})"
            )
        return label

    # ------------------------------------------------------------------ #
    # parse mode
    # ------------------------------------------------------------------ #

    def _run_parse(self, version: Any) -> Dict[str, Any]:
        """Parse a version and report a strict validity verdict."""
        clean = self._validate_version_param(version, "version")
        parsed, message, rule = _parse_semver(clean)
        if parsed is None:
            return {
                "mode": "parse",
                "version": clean,
                "valid": False,
                **self._error_result(
                    {}, error_type="invalid_version", message=message,
                    rule=rule,
                ),
            }
        return {
            "mode": "parse",
            "version": clean,
            "valid": True,
            "major": parsed.major,
            "minor": parsed.minor,
            "patch": parsed.patch,
            "prerelease": parsed.prerelease,
            "prerelease_identifiers": list(parsed.prerelease_ids),
            "build": parsed.build,
            "build_identifiers": list(parsed.build_ids),
        }

    # ------------------------------------------------------------------ #
    # compare mode
    # ------------------------------------------------------------------ #

    def _run_compare(self, version_a: Any, version_b: Any) -> Dict[str, Any]:
        """Compare two versions by spec §11 precedence."""
        clean_a = self._validate_version_param(version_a, "version_a")
        clean_b = self._validate_version_param(version_b, "version_b")
        context: Dict[str, Any] = {
            "mode": "compare",
            "version_a": clean_a,
            "version_b": clean_b,
        }
        parsed_a, message_a, rule_a = _parse_semver(clean_a)
        if parsed_a is None:
            return self._error_result(
                context,
                error_type="invalid_version",
                message=message_a,
                rule=rule_a,
                which="version_a",
            )
        parsed_b, message_b, rule_b = _parse_semver(clean_b)
        if parsed_b is None:
            return self._error_result(
                context,
                error_type="invalid_version",
                message=message_b,
                rule=rule_b,
                which="version_b",
            )
        key_a = parsed_a.precedence_key
        key_b = parsed_b.precedence_key
        if key_a < key_b:
            result, relation = -1, "lt"
        elif key_a > key_b:
            result, relation = 1, "gt"
        else:
            result, relation = 0, "eq"
        return {
            **context,
            "result": result,
            "relation": relation,
            # Equal precedence but different raw strings differs only
            # in build metadata, which §10 excludes from precedence.
            "differs_only_in_build_metadata": (
                result == 0 and clean_a != clean_b
            ),
        }

    # ------------------------------------------------------------------ #
    # bump mode
    # ------------------------------------------------------------------ #

    def _run_bump(
        self, version: Any, level: Any, label: Any
    ) -> Dict[str, Any]:
        """Bump a version at the requested level."""
        clean = self._validate_version_param(version, "version")
        if level not in self.LEVELS:
            self._invalid(
                f"level must be one of: {', '.join(self.LEVELS)} "
                f"(got {level!r})"
            )
        if label is not None and level != "prerelease":
            self._invalid(
                "label is only valid together with "
                f"level='prerelease' (got level={level!r})"
            )
        clean_label = (
            self._validate_label(label) if level == "prerelease" else None
        )
        context: Dict[str, Any] = {
            "mode": "bump",
            "level": level,
            "from": clean,
        }
        if level == "prerelease":
            context["label"] = clean_label
        parsed, message, rule = _parse_semver(clean)
        if parsed is None:
            return self._error_result(
                context,
                error_type="invalid_version",
                message=message,
                rule=rule,
            )
        if level == "release" and not parsed.prerelease_ids:
            return self._error_result(
                context,
                error_type="no_prerelease",
                message=(
                    "the release bump strips a pre-release — the version "
                    f"must carry one, e.g. '1.2.3-rc.1' (got {clean!r})"
                ),
            )
        bumped = self._bump_parsed(parsed, level, clean_label)
        return {**context, "result": str(bumped.without_build())}

    @staticmethod
    def _bump_parsed(
        parsed: _SemVer, level: str, label: Optional[str]
    ) -> _SemVer:
        """Apply one bump level to a parsed version (build dropped)."""
        if level == "major":
            return _SemVer(parsed.major + 1, 0, 0)
        if level == "minor":
            return _SemVer(parsed.major, parsed.minor + 1, 0)
        if level == "patch":
            return _SemVer(parsed.major, parsed.minor, parsed.patch + 1)
        if level == "release":
            return _SemVer(parsed.major, parsed.minor, parsed.patch)
        # level == "prerelease"
        if not parsed.prerelease_ids:
            # Start the next patch's pre-release series:
            # 1.2.3 -> 1.2.4-<label>.0
            return _SemVer(
                parsed.major, parsed.minor, parsed.patch + 1, (label, "0")
            )
        if parsed.prerelease_ids[0] != label:
            # Different channel: switch the pre-release series on the
            # same core: 1.2.3-alpha.1 -> 1.2.3-rc.0
            return _SemVer(parsed.major, parsed.minor, parsed.patch, (label, "0"))
        identifiers = list(parsed.prerelease_ids)
        for index in range(len(identifiers) - 1, -1, -1):
            part = identifiers[index]
            if _NUMERIC.fullmatch(part):
                # Continue the series: 1.2.3-rc.9 -> 1.2.3-rc.10
                identifiers[index] = str(int(part) + 1)
                return _SemVer(
                    parsed.major,
                    parsed.minor,
                    parsed.patch,
                    tuple(identifiers),
                )
        # No numeric identifier yet: 1.2.3-rc -> 1.2.3-rc.0 (§11: the
        # larger pre-release identifier set has higher precedence).
        return _SemVer(
            parsed.major,
            parsed.minor,
            parsed.patch,
            tuple(identifiers) + ("0",),
        )

    # ------------------------------------------------------------------ #
    # range mode
    # ------------------------------------------------------------------ #

    def _run_range(self, version: Any, version_range: Any) -> Dict[str, Any]:
        """Check one version against a simple range expression."""
        clean_version = self._validate_version_param(version, "version")
        if (
            version_range is None
            or isinstance(version_range, bool)
            or not isinstance(version_range, str)
        ):
            self._invalid(
                f"version_range must be a non-empty string "
                f"(got {version_range!r})"
            )
        if not version_range:
            self._invalid("version_range must be a non-empty string (got '')")
        if len(version_range) > _MAX_RANGE_CHARS:
            self._invalid(
                f"version_range exceeds the {_MAX_RANGE_CHARS:,}-"
                f"character limit (got {len(version_range):,} characters)"
            )
        context: Dict[str, Any] = {
            "mode": "range",
            "range": version_range,
            "version": clean_version,
        }
        parsed_version, message, rule = _parse_semver(clean_version)
        if parsed_version is None:
            return self._error_result(
                context,
                error_type="invalid_version",
                message=message,
                rule=rule,
                which="version",
            )
        comparators, range_message = self._compile_range(version_range)
        if comparators is None:
            return self._error_result(
                context,
                error_type="invalid_range",
                message=range_message,
            )
        return {
            **context,
            "expanded": " ".join(
                display for _, _, display in comparators
            ),
            "result": self._satisfies(parsed_version, comparators),
        }

    @classmethod
    def _compile_range(
        cls, range_text: str
    ) -> Tuple[Optional[List[Tuple[str, _SemVer, str]]], Optional[str]]:
        """Compile a range expression into a list of comparators.

        Returns ``(comparators, None)`` on success or ``(None,
        message)`` for an unsupported or malformed range. Each
        comparator is ``(operator, bound_version, display)``.
        """
        comparators: List[Tuple[str, _SemVer, str]] = []
        tokens = range_text.split()
        if not tokens:
            return None, (
                "the range contains no comparators — provide at least one "
                "comparator, e.g. '1.2.3' or '>=1.2.0 <2.0.0'"
            )
        for token in tokens:
            if token in ("-", "–", "—"):
                return None, (
                    "hyphen ranges ('1.2.3 - 2.3.4') are not supported — "
                    "write '>=1.2.3 <=2.3.4' instead"
                )
            if token in ("||", "|"):
                return None, (
                    "range unions ('a || b') are not supported — check "
                    "each side separately"
                )
        for token in tokens:
            if token.startswith("~"):
                expanded, message = cls._expand_tilde(token[1:])
                if expanded is None:
                    return None, message
                comparators.extend(expanded)
                continue
            if token.startswith("^"):
                expanded, message = cls._expand_caret(token[1:])
                if expanded is None:
                    return None, message
                comparators.extend(expanded)
                continue
            operator = None
            for candidate in (">=", "<=", ">", "<", "="):
                if token.startswith(candidate):
                    operator = candidate
                    break
            if operator is not None:
                operand = token[len(operator):]
                parsed, message, _ = _parse_semver(operand)
                if parsed is None:
                    return None, (
                        f"comparator {token!r}: comparison operators "
                        f"require a full X.Y.Z version — {message}"
                    )
                comparators.append(
                    (
                        operator,
                        parsed,
                        str(parsed.without_build())
                        if operator == "="
                        else operator + str(parsed.without_build()),
                    )
                )
                continue
            parsed, message, _ = _parse_semver(token)
            if parsed is None:
                return None, (
                    f"{token!r} is not a supported range — supported are "
                    f"exact versions ('1.2.3'), comparison operators "
                    f"(> >= < <= =), tilde ranges ('~1.2.3') and caret "
                    f"ranges ('^1.2.3') joined by whitespace; x-ranges "
                    f"('1.2.x', '*'), hyphen ranges, unions and "
                    f"dist-tags are not supported"
                )
            comparators.append(("=", parsed, str(parsed.without_build())))
        return comparators, None

    @staticmethod
    def _expand_partial(
        operand: str, kind: str
    ) -> Tuple[Optional[_SemVer], Optional[str]]:
        """Shared partial-version handling for tilde / caret operands."""
        major, minor, patch, prerelease_ids, message = _parse_partial(
            operand
        )
        if message is not None:
            return None, f"invalid {kind} range {operand!r}: {message}"
        lower = _SemVer(
            major,
            minor if minor is not None else 0,
            patch if patch is not None else 0,
            prerelease_ids,
        )
        return lower, None

    @staticmethod
    def _core_dot_count(operand: str) -> int:
        """Number of dots in the version core of a tilde/caret operand."""
        return operand.split("+")[0].split("-")[0].count(".")

    @classmethod
    def _expand_tilde(
        cls, operand: str
    ) -> Tuple[Optional[List[Tuple[str, _SemVer, str]]], Optional[str]]:
        """Expand a tilde range: ~1.2.3 -> >=1.2.3 <1.3.0, ~1 -> <2.0.0."""
        lower, message = cls._expand_partial(operand, "tilde")
        if lower is None:
            return None, message
        if cls._core_dot_count(operand) == 0:
            # '~X': allow minor-level changes.
            upper = _SemVer(lower.major + 1, 0, 0)
        else:
            # '~X.Y' and '~X.Y.Z': allow patch-level changes.
            upper = _SemVer(lower.major, lower.minor + 1, 0)
        return [
            (">=", lower, ">=" + str(lower.without_build())),
            ("<", upper, "<" + str(upper)),
        ], None

    @classmethod
    def _expand_caret(
        cls, operand: str
    ) -> Tuple[Optional[List[Tuple[str, _SemVer, str]]], Optional[str]]:
        """Expand a caret range (leftmost-non-zero rule).

        ^1.2.3 -> >=1.2.3 <2.0.0; ^0.2.3 -> <0.3.0; ^0.0.3 -> <0.0.4;
        partials: ^1.2 -> <2.0.0, ^0.2 -> <0.3.0, ^0.0 -> <0.1.0,
        ^0 -> <1.0.0, ^1 -> <2.0.0.
        """
        lower, message = cls._expand_partial(operand, "caret")
        if lower is None:
            return None, message
        dots = cls._core_dot_count(operand)
        major, minor, patch = lower.major, lower.minor, lower.patch
        if major > 0:
            upper = _SemVer(major + 1, 0, 0)
        elif dots == 0:  # '^0'
            upper = _SemVer(1, 0, 0)
        elif minor > 0:
            upper = _SemVer(0, minor + 1, 0)
        elif dots == 1:  # '^0.0'
            upper = _SemVer(0, 1, 0)
        else:  # '^0.0.Z'
            upper = _SemVer(0, 0, patch + 1)
        return [
            (">=", lower, ">=" + str(lower.without_build())),
            ("<", upper, "<" + str(upper)),
        ], None

    # ------------------------------------------------------------------ #
    # Range matching
    # ------------------------------------------------------------------ #

    @staticmethod
    def _matches(
        operator: str, candidate_key: tuple, bound_key: tuple
    ) -> bool:
        """Evaluate one comparator against a precedence key."""
        if operator == "=":
            return candidate_key == bound_key
        if operator == ">":
            return candidate_key > bound_key
        if operator == ">=":
            return candidate_key >= bound_key
        if operator == "<":
            return candidate_key < bound_key
        return candidate_key <= bound_key  # "<="

    @classmethod
    def _satisfies(
        cls,
        version: _SemVer,
        comparators: List[Tuple[str, _SemVer, str]],
    ) -> bool:
        """Check whether a version satisfies a comparator set.

        Follows the npm/node-semver default prerelease gating: a
        version with a pre-release only satisfies the set when at
        least one comparator bound carries a pre-release on the same
        major.minor.patch tuple; otherwise prereleases never match
        (so '~1.2.3' does not match '1.2.4-beta').
        """
        if version.prerelease_ids:
            gated = any(
                bound.prerelease_ids and bound.core_tuple == version.core_tuple
                for _, bound, _ in comparators
            )
            if not gated:
                return False
        candidate_key = version.precedence_key
        return all(
            cls._matches(operator, candidate_key, bound.precedence_key)
            for operator, bound, _ in comparators
        )

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any],
        error_type: str,
        message: str,
        rule: Optional[str] = None,
        which: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        error: Dict[str, Any] = {
            "type": error_type,
            "message": str(message)[:500],
        }
        if rule:
            error["rule"] = rule
        if which:
            error["which"] = which
        return {**context, "error": error}
