#!/usr/bin/env python3

"""Bounded version reasoning: evaluate, compare, sort and select versions.

The reasoning helpers are importable module-level functions, while the
``VersionRangeTool`` component wraps them for the agent tool registry. The
tool performs no network access and raises ``ValueError`` for malformed
input.
"""

import functools
import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool

_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.]+)?$")
_QUALIFIERS = (">=", "<=", "==", "!=", ">", "<")
_DEFAULT_MAX_COMPARATORS = 12
_DEFAULT_MAX_CHARS = 240

ParsedVersion = Tuple[int, int, int, Optional[Tuple[Any, ...]]]
Comparator = Tuple[str, Tuple[int, int, int, Optional[Tuple[Any, ...]]]]


def parse_version(text: str) -> ParsedVersion:
    """Parse '1.2.3' or '1.2.3-rc.1' and raise ValueError otherwise.

    The three numeric parts must be non-negative integers. The prerelease,
    when present, splits on dots: purely numeric identifiers become int,
    the remaining identifiers become lowercase strings. Surrounding
    whitespace is not accepted.
    """
    if not isinstance(text, str):
        raise ValueError("version must be a string: %r" % (text,))
    if not _VERSION_RE.match(text):
        raise ValueError("malformed version: %r" % (text,))
    core, _, prerelease = text.partition("-")
    major, minor, patch = (int(part) for part in core.split("."))
    trail: Optional[Tuple[Any, ...]] = None
    if prerelease:
        tokens: List[Any] = []
        for token in prerelease.split("."):
            if not token:
                raise ValueError("empty prerelease identifier: %r" % (text,))
            tokens.append(int(token) if token.isdigit() else token.lower())
        trail = tuple(tokens)
    return major, minor, patch, trail


def _compare_parsed(left: ParsedVersion, right: ParsedVersion,
                    include_prerelease: bool = True) -> int:
    """Order two parsed versions and return -1, 0 or 1.

    The numeric triple dominates. Without prerelease ordering, versions whose
    triples match compare equal. Otherwise a released version outranks its
    prereleases, and prerelease identifiers compare pairwise: numbers before
    names, numbers by value, names lexicographically, shorter prefixes lose.
    """
    if left[:3] != right[:3]:
        return -1 if left[:3] < right[:3] else 1
    if not include_prerelease:
        return 0
    trail_a = left[3]
    trail_b = right[3]
    if trail_a == trail_b:
        return 0
    if trail_a is None:
        return 1
    if trail_b is None:
        return -1
    for one, two in zip(trail_a, trail_b):
        if one == two:
            continue
        if isinstance(one, int) and isinstance(two, int):
            return -1 if one < two else 1
        if isinstance(one, int):
            return -1
        if isinstance(two, int):
            return 1
        return -1 if one < two else 1
    return -1 if len(trail_a) < len(trail_b) else 1


def compare_versions(left: str, right: str, include_prerelease: bool = True) -> int:
    """Order two version strings; returns -1, 0 or 1.

    With ``include_prerelease`` disabled, versions that agree on their numeric
    triple compare equal even when their prereleases differ.
    """
    return _compare_parsed(parse_version(left), parse_version(right), include_prerelease)


def _render(version: ParsedVersion) -> str:
    """Render a parsed version back into its canonical spelling."""
    core = "%d.%d.%d" % (version[0], version[1], version[2])
    if version[3] is None:
        return core
    return core + "-" + ".".join(str(token) for token in version[3])


def parse_constraint(text: str, max_comparators: int = _DEFAULT_MAX_COMPARATORS,
                     max_chars: int = _DEFAULT_MAX_CHARS) -> List[Comparator]:
    """Parse '>=1.2.0, <2.0.0, !=1.5.0' into (qualifier, version) pairs.

    Comparators separate on commas; surrounding whitespace is trimmed and a
    bare version implies equality. Duplicate and redundant comparators are
    preserved. An entirely empty constraint yields no comparators, which
    every version satisfies. Bounds: at most ``max_comparators`` comparators
    taken from at most ``max_chars`` characters.
    """
    if not isinstance(text, str):
        raise ValueError("constraint must be a string: %r" % (text,))
    if len(text) > max_chars:
        raise ValueError("constraint too long: %d > %d" % (len(text), max_chars))
    if not text.strip():
        return []
    comparators: List[Comparator] = []
    for part in text.split(","):
        piece = part.strip()
        if not piece:
            raise ValueError("empty comparator in constraint: %r" % (text,))
        qualifier = "=="
        for probe in _QUALIFIERS:
            if piece.startswith(probe):
                qualifier = probe
                piece = piece[len(probe):].strip()
                break
        comparators.append((qualifier, parse_version(piece)))
        if len(comparators) > max_comparators:
            raise ValueError("too many comparators: > %d" % (max_comparators,))
    return comparators


def evaluate(comparators: List[Comparator], version: str,
             include_prerelease: bool = True) -> Tuple[bool, List[str]]:
    """Return (satisfied, mismatches) for one candidate version.

    A comparator such as ('>=', (1, 2, 0, None)) is reported in the mismatch
    list as '>=1.2.0'. The order of the comparators is preserved.
    """
    candidate = parse_version(version)
    failed: List[str] = []
    for qualifier, target in comparators:
        relation = _compare_parsed(candidate, target, include_prerelease)
        if qualifier == "==":
            ok = relation == 0
        elif qualifier == "!=":
            ok = relation != 0
        elif qualifier == ">":
            ok = relation > 0
        elif qualifier == ">=":
            ok = relation >= 0
        elif qualifier == "<":
            ok = relation < 0
        else:
            ok = relation <= 0
        if not ok:
            failed.append(qualifier + _render(target))
    return (not failed), failed


def sort_versions(versions: List[str], include_prerelease: bool = True,
                  limit: int = 200) -> Tuple[List[str], int]:
    """Sort versions ascending, deduplicated; returns (ordered, duplicates).

    Entries must be strings. The first spelling of every version is kept, so
    distinct spellings of equal versions, such as '1.2.3' and '1.02.3', both
    survive and keep their input order. Sorting is stable.
    """
    if not isinstance(versions, list):
        raise ValueError("versions must be a list")
    if len(versions) > limit:
        raise ValueError("too many versions: %d > %d" % (len(versions), limit))
    unique: List[str] = []
    seen = set()
    duplicates = 0
    for item in versions:
        if not isinstance(item, str):
            raise ValueError("version entries must be strings: %r" % (item,))
        if item in seen:
            duplicates += 1
            continue
        seen.add(item)
        unique.append(item)
    ordered = sorted(unique, key=functools.cmp_to_key(
        lambda one, two: compare_versions(one, two, include_prerelease)))
    return ordered, duplicates


def select_latest(versions: List[str], comparators: List[Comparator],
                  include_prerelease: bool = True,
                  limit: int = 200) -> Tuple[Optional[str], int]:
    """Return (greatest satisfying version, distinct satisfied count).

    When no listed version satisfies every comparator, the selection is None
    and the count is 0. Version ordering is numeric, so 1.10.0 outranks 1.9.9.
    """
    ordered, _duplicates = sort_versions(versions, include_prerelease, limit)
    satisfying = [item for item in ordered if evaluate(comparators, item, include_prerelease)[0]]
    if not satisfying:
        return None, 0
    best = max(satisfying, key=functools.cmp_to_key(
        lambda one, two: compare_versions(one, two, include_prerelease)))
    return best, len(satisfying)


class VersionRangeTool(Tool):
    """Evaluate, compare, sort and select versions without any network access."""

    MAX_COMPARATORS: ClassVar[int] = 12
    MAX_EXPRESSION_CHARS: ClassVar[int] = 240
    MAX_LISTED: ClassVar[int] = 200

    default_include_prerelease: bool = Field(
        default=True, description="Order prerelease identifiers unless the caller overrides include_prerelease")

    def execute(self, action: str = "check", constraint: str = "", version: str = "",
                other: str = "", versions: Optional[List[str]] = None,
                include_prerelease: Optional[bool] = None) -> Dict[str, Any]:
        """Run one bounded version-reasoning action.

        Args:
            action: One of check, compare, sort, latest.
            constraint: Comparators such as '>=1.2.0, <2.0.0, !=1.5.0'. A bare
                version means equality; an empty constraint accepts everything.
            version: The candidate for check, or the left side of compare.
            other: The right side of compare.
            versions: A list of 1..200 versions for sort and latest.
            include_prerelease: Overrides the configured default ordering.

        Returns:
            A structured, JSON-serializable dict. check reports satisfied, the
            parsed comparators and the failing ones; compare reports relation
            -1, 0 or 1; sort reports the deduplicated ascending order and the
            duplicate count; latest reports the greatest satisfying version or
            None.

        Raises:
            ValueError: If the action, versions, constraint or version input
                is malformed or exceeds the configured bounds.
        """
        if action not in ("check", "compare", "sort", "latest"):
            raise ValueError("unknown action: %r" % (action,))
        flag = self.default_include_prerelease if include_prerelease is None else include_prerelease
        if action == "check":
            comparators = parse_constraint(constraint, self.MAX_COMPARATORS, self.MAX_EXPRESSION_CHARS)
            satisfied, mismatches = evaluate(comparators, version, flag)
            return {
                "action": "check",
                "constraint": constraint,
                "comparators": [qualifier + _render(target) for qualifier, target in comparators],
                "version": version,
                "satisfied": satisfied,
                "mismatches": mismatches,
            }
        if action == "compare":
            relation = compare_versions(version, other, flag)
            return {"action": "compare", "left": version, "right": other, "relation": relation}
        if action == "sort":
            listed = versions if versions is not None else []
            ordered, duplicates = sort_versions(listed, flag, self.MAX_LISTED)
            return {
                "action": "sort",
                "count": len(listed),
                "unique": len(ordered),
                "duplicates": duplicates,
                "sorted": ordered,
            }
        comparators = parse_constraint(constraint, self.MAX_COMPARATORS, self.MAX_EXPRESSION_CHARS)
        listed = versions if versions is not None else []
        selected, satisfied = select_latest(listed, comparators, flag, self.MAX_LISTED)
        return {
            "action": "latest",
            "selected": selected,
            "satisfied_count": satisfied,
            "pool": len(listed),
            "comparators": [qualifier + _render(target) for qualifier, target in comparators],
        }
