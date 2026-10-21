#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: freeze_diff_tool.py

r"""Pip-freeze / installed-distribution snapshot comparison, pure
Python stdlib plus ``importlib.metadata`` (itself stdlib) — no
network, no subprocess, no pip import.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) at the **environment layer**: not the requirements.txt
file and not abstract range algebra, but *what is actually
installed right now*. Agents that debug "works on my machine"
reports, verify a deploy box or review a Docker image need to ask
environment-shaped questions — "what does this interpreter
actually carry?", "does the installed environment satisfy the
declared requirements, and what has crept in that the file never
asked for?" and "what moved between the freeze snapshot from
before the change and the one after it?"

Three modes:

* ``installed`` — inventory of the environment. With no ``freeze``
  text it reads the **live** interpreter through
  ``importlib.metadata.distributions()`` (every installed
  distribution's PEP 503 normalized name, its version and the
  count of its declared dependencies — ``requires_dist_count`` —
  sorted by name). With a ``freeze`` text it parses that instead:
  each ``name==version`` (or ``===``) pin becomes one
  distribution, editable (``-e …``) and direct-reference
  (``name @ url``) lines are reported as non-pin lines, comments
  and blanks are counted, and anything unparsable lands in
  ``errors`` with a 1-based line number. The payload carries a
  ``source`` tag — ``live`` or ``text``.
* ``compare`` — the environment-drift verdict. A requirements.txt
  text is checked against an installed environment (a ``freeze``
  text, or the live interpreter when no text is given): every
  declared requirement becomes a row ``{name, name_raw, spec,
  clauses, satisfied, installed_version?}`` where ``satisfied``
  is computed by evaluating each specifier clause against the
  installed version (details below). Requirements that are
  installed are further split into ``satisfied`` /
  unsatisfied-but-present; declared names with **nothing**
  installed land in ``missing_not_installed``. The reverse
  direction — installed distributions the file never declared —
  is ``undeclared_installed``, after an exempt list (default
  ``pip``, ``setuptools``, ``wheel`` — the bootstrap tooling that
  appears in every environment but is almost never declared; the
  ``exempt`` argument replaces the list) has filtered its matches
  into ``exempt_filtered`` so the drift rows stay signal.
  ``summary`` carries all counts. Requirements lines with
  environment markers are **not** judged (markers are not
  evaluated here — see RequirementsTool) and are listed verbatim
  in ``marker_lines`` — their names never count as undeclared
  drift either, since they are conditional declarations; editable
  / URL / path lines cannot be version-compared and are listed in
  ``non_version_lines``; ``--hash`` options inside a line are not
  consumed (hash linting is RequirementsTool's job), so such
  lines land in ``errors``; all three groups are excluded from
  the verdict counts.
* ``snapshot_diff`` — the before/after mode. Two pip-freeze texts
  (yesterday vs today, or the CI log before and after a change)
  into ``upgraded`` / ``downgraded`` (``{name, from, to}`` —
  direction decided by PEP 440 ordering), ``added`` /
  ``removed`` (``{name, version}``) and an ``unchanged_count``.
  Ordering uses ``packaging.version.Version`` when that optional
  distribution is importable, else the built-in minimal PEP 440
  parser (epoch, zero-trimmed release tuple, pre / post / dev
  keys, local tail — the documented tuple encoding); the payload
  names which one via ``ordering``. Pairs whose versions neither
  parser accepts never guess: they are collected in ``unparsed``.

Division of labor inside the family (see the Distinction section
of the PR): **RequirementsTool** (#4021) *parses and lints the
requirements.txt file itself* (PEP 508 lines kept verbatim,
editable / VCS / URL / hash hygiene, two-file diff);
**VersionConstraintTool** (#3995) *resolves abstract semver range
sets* (candidates, binding constraint, conflicts) with no
environment attached. This tool is the third leg: it **compares
installed-environment snapshots** — pip freeze text or the live
``importlib.metadata`` view — against a declared file or against
each other. What is installed vs what was declared is exactly the
drift the other two cannot see.

The satisfaction evaluator (``compare`` mode): each clause is one
of ``==`` / ``!=`` (including the trailing-``.*`` wildcard form),
``>=`` / ``<=`` / ``>`` / ``<`` / ``~=``
(compatible release) / ``===`` (arbitrary string equality,
case-insensitive). Equality zero-pads release tuples
(``1.0`` == ``1.0.0``), ignores a candidate local segment when the
clause pins none (``==1.0`` accepts ``1.0+local``) and requires an
exact local match when it does. Wildcards prefix-match the padded
release tuple (``==1.2.0.*`` accepts ``1.2``), ``~=``
downgrades to ``>=`` + the parent-prefix wildcard
(``~=1.2.3`` is ``>=1.2.3, ==1.2.*``). Ordering uses the minimal
PEP 440 key: ``(epoch, zero-trimmed release, pre-key, post-key,
dev-key, local-key)`` where ``1.0.dev1 < 1.0a1 < 1.0rc1 < 1.0 <
1.0.post1 < 1.0.1``. Pre-release policy mirrors
``packaging.specifiers``: a pre-release or dev candidate is
rejected outright unless some ``==`` / ``>=`` / ``<=`` / ``~=``
/ ``===`` clause itself mentions a pre-release version; ``>``
additionally rejects post-releases and local versions the clause
does not pin, ``<`` rejects same-base pre-releases of a final
clause. When the optional ``packaging`` distribution is importable
it is used for the verdict (cross-checked against the minimal
evaluator by the unit-test differential); the payload records
which via ``verifier`` — ``packaging`` or ``minimal-evaluator``.
Known, documented divergence: packaging 23.x raises on an ``===``
clause whose operand is not a version; this tool answers those
with plain string equality (packaging 24+ does the same).

Out of scope: ``outdated_guess`` (what *could* be upgraded needs
index queries — network — and is deliberately NOT attempted by an
offline tool); marker evaluation; constraint solving; anything
reading the filesystem beyond installed-distribution metadata.

Determinism: every text path is fully deterministic (file order,
sorted outputs, sorted summaries). The ``live`` source is by
definition environment-dependent — the same interpreter always
yields the same payload, but two machines will not; duplicate
distribution names are resolved first-enumeration-wins and counted
in ``duplicates``, nameless metadata records are skipped and
counted in ``skipped_nameless``.

Input validation is strict and happens before any work: wrong
parameter types raise ``ValueError``; the text inputs are capped
at 10,000 lines, 10,000 characters per line and 4,000,000
characters total; the exempt list is capped at 1,000 entries.
"""

import itertools
import re
from importlib import metadata as _importlib_metadata
from typing import Any, ClassVar, Dict, List, NamedTuple, Optional, Set, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# ------------------------------------------------------------------ #
# Optional packaging accelerators (never required)
# ------------------------------------------------------------------ #

try:  # pragma: no cover - import outcome depends on the machine
    from packaging.specifiers import SpecifierSet as _SpecifierSet
    from packaging.version import Version as _PackagingVersion
except ImportError:  # pragma: no cover
    _SpecifierSet = None
    _PackagingVersion = None

# ------------------------------------------------------------------ #
# Limits (reject pathological inputs before any work)
# ------------------------------------------------------------------ #

_MAX_LINES = 10_000
_MAX_LINE_CHARS = 10_000
_MAX_TEXT_CHARS = 4_000_000
_MAX_EXEMPT = 1_000

# ------------------------------------------------------------------ #
# Grammar building blocks
# ------------------------------------------------------------------ #

# PEP 503 canonicalization: collapse runs of -_. to a single -, lower.
_NAME_COLLAPSE_RE = re.compile(r"[-_.]+")
# A pip freeze pin line: name == version / name === version.
_FREEZE_PIN_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)"
    r"\s*(?P<op>===|==)\s*(?P<version>\S+)$"
)
# Editable prefix on a freeze / requirements line.
_EDITABLE_PREFIX_RE = re.compile(r"^(?:-e|--editable)(?:\s+|=|$)")
# A URL scheme prefix (git+https, https, file, ssh, ...).
_SCHEME_RE = re.compile(r"^([A-Za-z][A-Za-z0-9+.-]*)://")
# One specifier clause: operator + version token.
_CLAUSE_OP_RE = re.compile(r"^(===|==|!=|<=|>=|~=|<|>)\s*(.+)$")
# Requirement line: name, optional extras bracket, optional clause list.
_REQ_LINE_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)"
    r"(?:\s*\[(?P<extras>[^\]]*)\])?"
    r"(?P<rest>.*)$"
)
# Marker safety: letters, digits, comparisons, quotes, parens, space.
_MARKER_CHARS_RE = re.compile(r"^[A-Za-z0-9_.!<>~=\"'()\s-]+$")
_MARKER_OP_RE = re.compile(r"===|==|!=|<=|>=|<|>|~=")
# pip requirements-file options recognized in compare mode.
_VALUE_OPTIONS: Dict[str, str] = {
    "-r": "requirement",
    "--requirement": "requirement",
    "-c": "constraint",
    "--constraint": "constraint",
    "-f": "find-links",
    "--find-links": "find-links",
    "-i": "index-url",
    "--index-url": "index-url",
    "--extra-index-url": "extra-index-url",
    "--trusted-host": "trusted-host",
}
_FLAG_OPTIONS: Dict[str, str] = {
    "--no-index": "no-index",
    "--pre": "pre",
    "--prefer-binary": "prefer-binary",
    "--require-hashes": "require-hashes",
}
# The bootstrap tooling that every environment carries but almost
# no requirements.txt declares; overridable via the exempt argument.
_DEFAULT_EXEMPT: Tuple[str, ...] = ("pip", "setuptools", "wheel")

# Minimal PEP 440 version grammar (epoch, release, pre, post,
# implicit post -N, dev, local). Deliberately the same surface
# packaging.version accepts, minus spellings that normalize away.
_VERSION_RE = re.compile(
    r"""^\s*[vV]?
    (?:(?P<epoch>\d+)!)?
    (?P<release>\d+(?:\.\d+)*)
    (?:[-_.]?(?P<pre_l>alpha|a|beta|b|preview|pre|rc|c)[-_.]?(?P<pre_n>\d*))?
    (?:(?:[-_.]?(?:post|rev|r)[-_.]?(?P<post_n>\d*))|(?:-(?P<post_n2>\d+)))?
    (?:[-_.]?dev[-_.]?(?P<dev_n>\d*))?
    (?:\+(?P<local>[a-z0-9]+(?:[-_.][a-z0-9]+)*))?
    \s*$""",
    re.VERBOSE | re.IGNORECASE,
)
_PRE_ALIASES = {"alpha": "a", "beta": "b", "c": "rc", "pre": "rc", "preview": "rc"}
_PRE_RANK = {"a": 0, "b": 1, "rc": 2}


# ------------------------------------------------------------------ #
# Version parsing — the minimal PEP 440 tuple encoding
# ------------------------------------------------------------------ #

class _V(NamedTuple):
    """One parsed version (the minimal PEP 440 tuple encoding).

    Attributes:
        epoch (int): the ``1!`` epoch component.
        release (Tuple[int, ...]): dotted numeric release.
        pre (Optional[Tuple[str, int]]): normalized (letter, number)
            pre-release — letter one of a / b / rc.
        post (Optional[int]): post-release number.
        dev (Optional[int]): dev number.
        local (Tuple[str, ...]): local version segments (lowercased).
        text (str): the version as written.
    """

    epoch: int
    release: Tuple[int, ...]
    pre: Optional[Tuple[str, int]]
    post: Optional[int]
    dev: Optional[int]
    local: Tuple[str, ...]
    text: str = ""

    @property
    def is_prerelease(self) -> bool:
        """PEP 440: a pre-release carries a pre or a dev segment."""
        return self.pre is not None or self.dev is not None

    def cmpkey(self) -> tuple:
        """A totally ordered key mirroring packaging's Version."""
        trimmed = tuple(
            reversed(
                tuple(
                    itertools.dropwhile(
                        lambda x: x == 0, reversed(self.release)
                    )
                )
            )
        )
        if self.pre is None and self.post is None and self.dev is not None:
            pre_key: Tuple = (0,)  # a bare dev release sorts lowest
        elif self.pre is None:
            pre_key = (2,)  # final release sorts above any pre
        else:
            pre_key = (1, _PRE_RANK[self.pre[0]], self.pre[1])
        post_key: Tuple = (0,) if self.post is None else (1, self.post)
        dev_key: Tuple = (0, self.dev) if self.dev is not None else (1,)
        local_key = tuple(
            (1, int(part), "") if part.isdigit() else (0, 0, part)
            for part in self.local
        )
        return (self.epoch, trimmed, pre_key, post_key, dev_key, local_key)

    def base_version(self) -> "_V":
        """The release-only view (pre / post / dev / local dropped)."""
        return _V(self.epoch, self.release, None, None, None, (), self.text)


def _public(version: _V) -> _V:
    """The public view of a version (local segment stripped)."""
    return _V(
        version.epoch,
        version.release,
        version.pre,
        version.post,
        version.dev,
        (),
        version.text,
    )


def _parse_version(text: str) -> Optional[_V]:
    """Parse one version string, or ``None`` when not PEP 440."""
    match = _VERSION_RE.match(str(text))
    if match is None:
        return None
    epoch = int(match.group("epoch") or 0)
    release = tuple(int(part) for part in match.group("release").split("."))
    pre: Optional[Tuple[str, int]] = None
    if match.group("pre_l"):
        letter_raw = match.group("pre_l").lower()
        letter = _PRE_ALIASES.get(letter_raw, letter_raw)
        pre = (letter, int(match.group("pre_n") or 0))
    post: Optional[int] = None
    if match.group("post_n") is not None:
        post = int(match.group("post_n") or 0)
    elif match.group("post_n2") is not None:
        post = int(match.group("post_n2"))
    dev: Optional[int] = None
    if match.group("dev_n") is not None:
        dev = int(match.group("dev_n") or 0)
    local: Tuple[str, ...] = ()
    if match.group("local"):
        local = tuple(
            part.lower() for part in re.split(r"[-_.]", match.group("local"))
        )
    return _V(epoch, release, pre, post, dev, local, str(text))


def _versions_equal(spec: _V, candidate: _V) -> bool:
    """``==`` semantics: zero-padded release equality.

    A clause without a local segment ignores the candidate's local
    segment; a clause with one requires the exact same local tail.
    """
    if spec.epoch != candidate.epoch:
        return False
    width = max(len(spec.release), len(candidate.release))
    padded_spec = spec.release + (0,) * (width - len(spec.release))
    padded_cand = (
        candidate.release + (0,) * (width - len(candidate.release))
    )
    if padded_spec != padded_cand:
        return False
    if (spec.pre, spec.post, spec.dev) != (
        candidate.pre, candidate.post, candidate.dev,
    ):
        return False
    if spec.local:
        return spec.local == candidate.local
    return True


def _wildcard_match(prefix: _V, candidate: _V) -> bool:
    """``==X.Y.*`` semantics: padded release prefix match."""
    if candidate.epoch != prefix.epoch:
        return False
    width = len(prefix.release)
    padded = candidate.release + (0,) * max(0, width - len(candidate.release))
    return padded[:width] == prefix.release


def _clause_allows_prereleases(op: str, version_text: str) -> bool:
    """Packaging's rule: an inclusive clause that itself mentions a
    pre-release opts the whole set into pre-release candidates."""
    if op not in ("==", ">=", "<=", "~=", "==="):
        return False
    text = version_text
    if op == "==" and text.endswith(".*"):
        text = text[:-2]
    parsed = _parse_version(text)
    return parsed is not None and parsed.is_prerelease


def _canonical_str(version: _V) -> str:
    """The canonical PEP 440 spelling (packaging's ``str(Version)``)."""
    parts: List[str] = []
    if version.epoch:
        parts.append(f"{version.epoch}!")
    parts.append(".".join(str(part) for part in version.release))
    if version.pre is not None:
        parts.append(f"{version.pre[0]}{version.pre[1]}")
    if version.post is not None:
        parts.append(f".post{version.post}")
    if version.dev is not None:
        parts.append(f".dev{version.dev}")
    if version.local:
        parts.append("+{}".format(".".join(version.local)))
    return "".join(parts)


def _clause_ok_minimal(op: str, version_text: str, candidate: _V) -> bool:
    """Evaluate one clause with the minimal evaluator (documented)."""
    if op == "===":
        # packaging compares the canonicalized candidate against the
        # literal operand, case-insensitively.
        return (
            _canonical_str(candidate).lower()
            == version_text.strip().lower()
        )
    if op in ("==", "!=") and version_text.endswith(".*"):
        prefix = _parse_version(version_text[:-2])
        if prefix is None:
            return False
        matched = _wildcard_match(prefix, candidate)
        return matched if op == "==" else not matched
    spec = _parse_version(version_text)
    if spec is None:
        return False
    if op == "==":
        return _versions_equal(spec, candidate)
    if op == "!=":
        return not _versions_equal(spec, candidate)
    if op == "~=":
        if len(spec.release) < 2:
            return False
        prefix = _V(spec.epoch, spec.release[:-1], None, None, None, ())
        public = _public(candidate)
        return public.cmpkey() >= spec.cmpkey() and _wildcard_match(
            prefix, candidate
        )
    # packaging compares >= / <= on the public view (local stripped).
    public_key, spec_key = _public(candidate).cmpkey(), spec.cmpkey()
    if op == ">=":
        return public_key >= spec_key
    if op == "<=":
        return public_key <= spec_key
    if op == ">":
        if not public_key > spec_key:
            return False
        # packaging: > rejects post / local versions only of the very
        # version the clause mentions (same base version).
        same_base = (
            candidate.base_version().cmpkey() == spec.base_version().cmpkey()
        )
        if spec.post is None and candidate.post is not None and same_base:
            return False
        if candidate.local and same_base:
            return False
        return True
    if op == "<":
        if not public_key < spec_key:
            return False
        # packaging: < rejects same-base pre-releases of a final.
        if (
            not spec.is_prerelease
            and candidate.is_prerelease
            and candidate.base_version().cmpkey()
            == spec.base_version().cmpkey()
        ):
            return False
        return True
    return False


def _evaluate_minimal(
    clauses: List[Tuple[str, str]], version_text: str
) -> Tuple[bool, Optional[str]]:
    """The whole minimal-evaluator verdict for one installed version."""
    candidate = _parse_version(version_text)
    if candidate is None:
        return False, "installed version is not parseable PEP 440"
    if candidate.is_prerelease and not any(
        _clause_allows_prereleases(op, text) for op, text in clauses
    ):
        return (
            False,
            "pre-release installed version excluded (no ==, >=, <=, ~= "
            "or === clause mentions a pre-release)",
        )
    for op, text in clauses:
        if not _clause_ok_minimal(op, text, candidate):
            return False, f"clause {op}{text} not satisfied"
    return True, None


def _evaluate(
    clauses: List[Tuple[str, str]], version_text: str
) -> Tuple[bool, Optional[str]]:
    """Verdict via packaging when importable, else the minimal one.

    The failure reason always comes from the minimal evaluator —
    the two agree on the shared grammar (the unit-test differential
    pins this), so the reason is never misleading.
    """
    minimal_ok, minimal_reason = _evaluate_minimal(clauses, version_text)
    if _SpecifierSet is None or _parse_version(version_text) is None:
        return minimal_ok, minimal_reason
    text = ",".join(f"{op}{version}" for op, version in clauses)
    try:
        packaging_ok = _SpecifierSet(text).contains(version_text)
    except Exception:
        # Known divergence: packaging 23.x raises on an === clause
        # whose operand is not a version — keep the minimal verdict.
        return minimal_ok, minimal_reason
    if packaging_ok:
        return True, None
    return False, minimal_reason or "clause set not satisfied"


def _ordering_key(version_text: str):
    """PEP 440 ordering key — packaging's when importable."""
    if _PackagingVersion is not None:
        return _PackagingVersion(version_text)  # may raise InvalidVersion
    parsed = _parse_version(version_text)
    if parsed is None:
        raise ValueError(f"not PEP 440: {version_text!r}")
    return parsed.cmpkey()


# ------------------------------------------------------------------ #
# Freeze-text parsing
# ------------------------------------------------------------------ #

def _parse_freeze(text: str) -> Dict[str, Any]:
    """Parse a pip-freeze text into pins / non-pins / errors."""
    pins: Dict[str, Dict[str, Any]] = {}
    editables: List[Dict[str, Any]] = []
    direct_urls: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    comments = 0
    blanks = 0
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            blanks += 1
            continue
        if line.startswith("#"):
            comments += 1
            continue
        pin = _FREEZE_PIN_RE.match(line)
        if pin is not None:
            name_raw = pin.group("name")
            name = _normalize_name(name_raw)
            if name in pins:
                errors.append(
                    {
                        "line": number,
                        "raw": raw,
                        "reason": f"duplicate pin for '{name}' "
                        f"(first wins)",
                    }
                )
                continue
            pins[name] = {
                "name": name,
                "name_raw": name_raw,
                "version": pin.group("version"),
            }
            continue
        if _EDITABLE_PREFIX_RE.match(line):
            editables.append({"line": number, "raw": raw})
            continue
        if " @ " in line:
            direct_urls.append({"line": number, "raw": raw})
            continue
        errors.append(
            {
                "line": number,
                "raw": raw,
                "reason": "not a pin (name==version), editable or "
                "direct-reference (name @ url) line",
            }
        )
    return {
        "pins": pins,
        "editables": editables,
        "direct_urls": direct_urls,
        "errors": errors,
        "comments": comments,
        "blanks": blanks,
    }


# ------------------------------------------------------------------ #
# Requirements-text parsing (the compare subset)
# ------------------------------------------------------------------ #

def _normalize_name(name: str) -> str:
    """PEP 503 normalization: lowercase, runs of -_. -> a single '-'."""
    return _NAME_COLLAPSE_RE.sub("-", name).lower()


def _split_comment(line: str) -> Tuple[str, Optional[str]]:
    """Split a line into (content, comment) the way pip does."""
    for index, char in enumerate(line):
        if char == "#" and (index == 0 or line[index - 1] in " \t"):
            return line[:index], line[index + 1:].strip()
    return line, None


def _is_pathish(text: str) -> bool:
    """Whether a token is a local path (never a PEP 508 name)."""
    if not text:
        return False
    return (
        text[0] in "./~"
        or "/" in text
        or "\\" in text
        or text in (".", "..")
    )


def _parse_clauses(
    spec_text: str,
) -> Tuple[Optional[List[Tuple[str, str]]], Optional[str]]:
    """Parse a comma-separated clause list (``None`` = no specifier).

    Returns ``(clauses, error)`` — a trailing comma is tolerated,
    each clause is ``(op, version_text)`` with light validation:
    the version token must parse as PEP 440 (wildcard and ``===``
    exempt where packaging exempts them), ``.*`` only on ``==`` /
    ``!=`` and only trailing, ``~=`` needs two release components.
    """
    spec_text = spec_text.strip()
    if not spec_text:
        return None, None
    clauses: List[Tuple[str, str]] = []
    pieces = [piece.strip() for piece in spec_text.split(",")]
    for piece in pieces:
        if not piece:
            continue  # tolerate a trailing comma
        match = _CLAUSE_OP_RE.match(piece)
        if match is not None:
            op, version = match.group(1), match.group(2).strip()
        else:
            op_match = re.match(r"^(===|==|!=|<=|>=|~=|<|>)", piece)
            if op_match is None:
                return None, (
                    f"clause {piece!r} does not start with an operator "
                    f"(== != <= >= ~= < > ===)"
                )
            op = op_match.group(1)
            version = piece[op_match.end():].strip()
            if not version:
                return None, f"clause {piece!r} carries no version"
        if version.endswith(".*"):
            if op not in ("==", "!="):
                return None, (
                    f"clause {piece!r}: a trailing .* wildcard is only "
                    f"valid with == or !="
                )
            if _parse_version(version[:-2]) is None:
                return None, (
                    f"clause {piece!r}: '{version[:-2]}' is not a "
                    f"PEP 440 version"
                )
        elif op == "===":
            if not version.strip():
                return None, f"clause {piece!r} carries no operand"
        else:
            parsed = _parse_version(version)
            if parsed is None:
                return None, (
                    f"clause {piece!r}: '{version}' is not a PEP 440 "
                    f"version"
                )
            if parsed.local and op not in ("==", "!=", "==="):
                return None, (
                    f"clause {piece!r}: a local version segment is only "
                    f"valid with ==, != or === (PEP 440 forbids it in "
                    f"range clauses)"
                )
            if op == "~=" and len(parsed.release) < 2:
                return None, (
                    f"clause {piece!r}: ~= needs at least two release "
                    f"components (e.g. ~=1.2)"
                )
        clauses.append((op, version))
    if not clauses:
        return None, None
    return clauses, None


def _validate_markers(markers: str) -> Optional[str]:
    """Loose marker validation (shape only — never evaluated)."""
    if not markers.strip():
        return "marker is empty"
    if not _MARKER_CHARS_RE.match(markers):
        return (
            "marker contains characters outside the accepted set "
            "(letters, digits, comparisons, quotes, parentheses)"
        )
    if not _MARKER_OP_RE.search(markers):
        return "marker contains no comparison"
    if markers.count("(") != markers.count(")"):
        return "marker has unbalanced parentheses"
    if markers.count('"') % 2 or markers.count("'") % 2:
        return "marker has an unterminated quote"
    return None


def _parse_requirements_declarations(text: str) -> Dict[str, Any]:
    """Parse requirements text into version-checkable declarations."""
    declared: List[Dict[str, Any]] = []
    marker_lines: List[Dict[str, Any]] = []
    non_version: List[Dict[str, Any]] = []
    options: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    comments: List[str] = []
    blanks = 0
    for number, raw in enumerate(text.splitlines(), start=1):
        content, comment = _split_comment(raw)
        if comment is not None:
            comments.append(comment)
        stripped = content.strip()
        if not stripped:
            blanks += 1
            continue
        # pip requirements-file options never declare a dependency.
        head = stripped.split()[0]
        if head in _VALUE_OPTIONS or head in _FLAG_OPTIONS:
            options.append({"line": number, "raw": stripped})
            continue
        if _EDITABLE_PREFIX_RE.match(stripped):
            non_version.append(
                {"line": number, "raw": raw, "kind": "editable"}
            )
            continue
        # A named PEP 508 direct reference (foo @ https://...) is a
        # requirement line, not a bare path — detect it before the
        # pathish check so the slash inside the URL does not win.
        direct_ref = None
        if " @ " in stripped:
            left = stripped.split(" @ ", 1)[0].strip()
            base_name = _REQ_LINE_RE.match(left)
            if base_name is not None and (
                base_name.group("name") == left
                or left.startswith(base_name.group("name") + "[")
            ):
                direct_ref = "direct_url"
        if direct_ref is None and (
            _SCHEME_RE.match(stripped) or _is_pathish(stripped)
        ):
            direct_ref = "path_or_url"
        if direct_ref is not None:
            non_version.append(
                {"line": number, "raw": raw, "kind": direct_ref}
            )
            continue
        # Split off an environment marker (never evaluated here).
        main, marker = stripped, None
        if ";" in stripped:
            main, marker = (part.strip() for part in stripped.split(";", 1))
            marker_error = _validate_markers(marker)
            if marker_error is not None:
                errors.append(
                    {"line": number, "raw": raw, "reason": marker_error}
                )
                continue
        match = _REQ_LINE_RE.match(main)
        if match is None:
            errors.append(
                {
                    "line": number,
                    "raw": raw,
                    "reason": "not a PEP 508 requirement line",
                }
            )
            continue
        name_raw = match.group("name")
        extras_raw = match.group("extras")
        extras = [
            piece.strip()
            for piece in (extras_raw or "").split(",")
            if piece.strip()
        ]
        if extras_raw is not None and extras_raw.strip() and not extras:
            errors.append(
                {
                    "line": number,
                    "raw": raw,
                    "reason": "empty extras item in bracket",
                }
            )
            continue
        rest = match.group("rest").strip()
        if rest.startswith("@"):
            # PEP 508 direct reference: foo @ https://... (also the
            # spaceless foo@1.0 spelling packaging 23.x accepts).
            non_version.append(
                {"line": number, "raw": raw, "kind": "direct_url"}
            )
            continue
        clauses, clause_error = _parse_clauses(rest)
        if clause_error is not None:
            errors.append(
                {"line": number, "raw": raw, "reason": clause_error}
            )
            continue
        spec_text = (
            None
            if clauses is None
            else re.sub(r"\s*,\s*", ",", rest.rstrip(",").strip())
        )
        entry: Dict[str, Any] = {
            "line": number,
            "name": _normalize_name(name_raw),
            "name_raw": name_raw,
            "extras": extras,
            "spec": spec_text,
            "clauses": [{"op": op, "version": v} for op, v in clauses]
            if clauses
            else [],
        }
        if marker is not None:
            entry["marker"] = marker
            marker_lines.append(entry)
        else:
            declared.append(entry)
    return {
        "declared": declared,
        "marker_lines": marker_lines,
        "non_version": non_version,
        "options": options,
        "errors": errors,
        "comments": comments,
        "blanks": blanks,
    }


# ------------------------------------------------------------------ #
# The live environment (importlib.metadata, stdlib)
# ------------------------------------------------------------------ #

def _live_distributions() -> Tuple[List[Dict[str, Any]], int, int]:
    """Read the live interpreter's installed distributions.

    Returns ``(distributions_sorted, duplicates, skipped_nameless)``.
    Distributions are deduplicated by normalized name (first
    enumeration wins); records without a name are skipped.
    """
    seen: Dict[str, Dict[str, Any]] = {}
    duplicates = 0
    skipped = 0
    for dist in _importlib_metadata.distributions():
        try:
            metadata = dist.metadata
            raw = metadata["Name"] if metadata is not None else None
            version = str(dist.version or "")
            requires = dist.requires
            requires_count = len(requires) if requires else 0
        except Exception:  # pragma: no cover - broken metadata record
            skipped += 1
            continue
        if not raw or not str(raw).strip():
            skipped += 1
            continue
        name = _normalize_name(str(raw))
        if name in seen:
            duplicates += 1
            continue
        seen[name] = {
            "name": name,
            "name_raw": str(raw),
            "version": version,
            "requires_dist_count": requires_count,
        }
    ordered = sorted(seen.values(), key=lambda item: item["name"])
    return ordered, duplicates, skipped


# ------------------------------------------------------------------ #
# compare mode
# ------------------------------------------------------------------ #

def _compare_declarations(
    document: Dict[str, Any],
    installed: Dict[str, str],
    exempt: Set[str],
    source: str,
    verifier: str,
) -> Dict[str, Any]:
    """The environment-drift verdict: declared vs installed."""
    rows: List[Dict[str, Any]] = []
    missing: List[str] = []
    satisfied_count = 0
    unsatisfied_installed = 0
    declared_names: Set[str] = set()
    # Marker lines are declarations too (conditional ones we cannot
    # evaluate) — their names never count as undeclared drift.
    declared_names.update(entry["name"] for entry in document["marker_lines"])
    for entry in document["declared"]:
        name = entry["name"]
        declared_names.add(name)
        version = installed.get(name)
        row: Dict[str, Any] = {
            "name": name,
            "name_raw": entry["name_raw"],
            "spec": entry["spec"],
            "extras": entry["extras"],
            "clauses": entry["clauses"],
        }
        if version is None:
            row["satisfied"] = False
            row["reason"] = "not installed"
            missing.append(name)
            rows.append(row)
            continue
        row["installed_version"] = version
        clauses = [
            (clause["op"], clause["version"]) for clause in entry["clauses"]
        ]
        ok, reason = _evaluate(clauses, version)
        row["satisfied"] = ok
        if reason:
            row["reason"] = reason
        parsed_installed = _parse_version(version)
        for clause in row["clauses"]:
            clause["satisfied"] = (
                _clause_ok_minimal(
                    clause["op"], clause["version"], parsed_installed
                )
                if parsed_installed is not None
                else False
            )
        if ok:
            satisfied_count += 1
        else:
            unsatisfied_installed += 1
        rows.append(row)

    undeclared: List[Dict[str, Any]] = []
    exempt_filtered: List[Dict[str, Any]] = []
    for name in sorted(installed):
        if name in declared_names:
            continue
        item = {"name": name, "version": installed[name]}
        if name in exempt:
            exempt_filtered.append(item)
        else:
            undeclared.append(item)

    total_installed = len(installed)
    non_version = document["non_version"]
    marker_lines = document["marker_lines"]
    return {
        "declared": rows,
        "missing_not_installed": missing,
        "undeclared_installed": undeclared,
        "exempt_filtered": exempt_filtered,
        "marker_lines": marker_lines,
        "non_version_lines": non_version,
        "errors": document["errors"],
        "options": document["options"],
        "comments": document["comments"],
        "blanks": document["blanks"],
        "summary": {
            "total_installed": total_installed,
            "declared": len(rows),
            "satisfied": satisfied_count,
            "unsatisfied_installed": unsatisfied_installed,
            "missing": len(missing),
            "marker_excluded": len(marker_lines),
            "non_version_lines": len(non_version),
            "undeclared_installed": len(undeclared),
            "exempt_filtered": len(exempt_filtered),
        },
        "source": source,
        "verifier": verifier,
    }


# ------------------------------------------------------------------ #
# snapshot_diff mode
# ------------------------------------------------------------------ #

def _snapshot_diff(
    old: Dict[str, Any], new: Dict[str, Any], ordering: str
) -> Dict[str, Any]:
    """The before/after mode: two freeze snapshots."""
    upgraded: List[Dict[str, Any]] = []
    downgraded: List[Dict[str, Any]] = []
    added: List[Dict[str, Any]] = []
    removed: List[Dict[str, Any]] = []
    unparsed: List[Dict[str, Any]] = []
    unchanged = 0
    old_pins, new_pins = old["pins"], new["pins"]
    for name in sorted(set(old_pins) | set(new_pins)):
        before = old_pins.get(name)
        after = new_pins.get(name)
        if before is None:
            added.append({"name": name, "version": after["version"]})
            continue
        if after is None:
            removed.append({"name": name, "version": before["version"]})
            continue
        from_version, to_version = before["version"], after["version"]
        if from_version == to_version:
            unchanged += 1
            continue
        try:
            if _ordering_key(to_version) > _ordering_key(from_version):
                upgraded.append(
                    {"name": name, "from": from_version, "to": to_version}
                )
            elif _ordering_key(to_version) < _ordering_key(from_version):
                downgraded.append(
                    {"name": name, "from": from_version, "to": to_version}
                )
            else:
                unchanged += 1  # e.g. 1.0 -> 1.0.0 under PEP 440
        except ValueError:
            unparsed.append(
                {"name": name, "from": from_version, "to": to_version}
            )
    return {
        "upgraded": upgraded,
        "downgraded": downgraded,
        "added": added,
        "removed": removed,
        "unchanged_count": unchanged,
        "unparsed": unparsed,
        "errors_old": old["errors"],
        "errors_new": new["errors"],
        "ignored_old": old["editables"] + old["direct_urls"],
        "ignored_new": new["editables"] + new["direct_urls"],
        "ordering": ordering,
    }


# ------------------------------------------------------------------ #
# The tool
# ------------------------------------------------------------------ #

class FreezeDiffTool(Tool):
    """Pip-freeze / installed-distribution snapshot comparison tool.

    Attributes:
        max_lines (int): Upper bound on the line count of any text.
        max_line_chars (int): Upper bound on any single line.
        max_text_chars (int): Upper bound on a whole text input.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "freeze_diff_tool"
    description: str = (
        "Pip-freeze / installed-distribution snapshot comparison — "
        "pure Python stdlib plus importlib.metadata (stdlib), no "
        "network, no subprocess. Inventory the environment "
        "(mode='installed': live importlib.metadata view with PEP 503 "
        "normalized names, versions and requires_dist_count, or a "
        "pip-freeze text parsed into name==version pins with source "
        "tag live|text), judge environment drift (mode='compare': a "
        "requirements.txt text vs the freeze text or the live "
        "environment — per-requirement satisfied verdicts via a "
        "==/!=/>=/<=/~=/</>/=== evaluator (packaging when importable, "
        "else a documented minimal PEP 440 one), missing_not_installed, "
        "undeclared_installed after a pip/setuptools/wheel exempt "
        "list) and diff two freeze snapshots (mode='snapshot_diff': "
        "upgraded / downgraded / added / removed / unchanged with "
        "PEP 440 ordering). outdated_guess (index queries) is out of "
        "scope — offline by design. RequirementsTool (#4021) "
        "parses/lints the requirements file itself; "
        "VersionConstraintTool (#3995) resolves abstract range sets — "
        "this tool is the installed-environment drift layer."
    )

    MODES: ClassVar[tuple] = ("installed", "compare", "snapshot_diff")

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        requirements: Any = None,
        freeze: Any = None,
        freeze_old: Any = None,
        freeze_new: Any = None,
        exempt: Any = None,
    ) -> Dict[str, Any]:
        """Run one environment-snapshot operation.

        Args:
            mode (str): One of ``installed`` / ``compare`` /
                ``snapshot_diff``.
            requirements (str): The requirements.txt text for
                ``compare`` (required there, ignored otherwise).
            freeze (str): A pip-freeze text — optional inventory
                source for ``installed`` and ``compare`` (the live
                interpreter is read when absent).
            freeze_old (str): The before snapshot for
                ``snapshot_diff`` (required there).
            freeze_new (str): The after snapshot for
                ``snapshot_diff`` (required there).
            exempt (list): Names filtered out of
                ``undeclared_installed`` for ``compare`` (default
                ``pip``, ``setuptools``, ``wheel``).

        Returns:
            Dict[str, Any]: The operation result — a structured
                payload per mode, with content-level problems (an
                unparsable line) carried inside the payload instead
                of raising.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} "
                f"(got {mode!r})"
            )
        if mode == "installed":
            return self._run_installed(freeze)
        if mode == "compare":
            return self._run_compare(requirements, freeze, exempt)
        return self._run_snapshot_diff(freeze_old, freeze_new)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"freeze_diff_tool: {message}")

    @classmethod
    def _validate_text(cls, value: Any, name: str) -> str:
        """Validate a text parameter (type and caps)."""
        if (
            value is None
            or isinstance(value, bool)
            or not isinstance(value, str)
        ):
            cls._invalid(f"{name} must be a string (got {value!r})")
        if len(value) > _MAX_TEXT_CHARS:
            cls._invalid(
                f"{name} exceeds the {_MAX_TEXT_CHARS:,}-character "
                f"limit (got {len(value):,} characters)"
            )
        lines = value.splitlines()
        if len(lines) > _MAX_LINES:
            cls._invalid(
                f"{name} exceeds the {_MAX_LINES:,}-line limit (got "
                f"{len(lines):,} lines)"
            )
        for number, line in enumerate(lines, start=1):
            if len(line) > _MAX_LINE_CHARS:
                cls._invalid(
                    f"line {number} of {name} exceeds the "
                    f"{_MAX_LINE_CHARS:,}-character limit (got "
                    f"{len(line):,} characters)"
                )
        return value

    @classmethod
    def _validate_exempt(cls, value: Any) -> Set[str]:
        """Validate the exempt list; None means the documented default."""
        if value is None:
            return {_normalize_name(name) for name in _DEFAULT_EXEMPT}
        if isinstance(value, (str, bytes)) or isinstance(value, bool):
            cls._invalid(
                f"exempt must be a list of package names (got "
                f"{value!r})"
            )
        if not isinstance(value, (list, tuple, set)):
            cls._invalid(
                f"exempt must be a list of package names (got "
                f"{value!r})"
            )
        entries: List[str] = []
        for entry in value:
            if (
                isinstance(entry, bool)
                or not isinstance(entry, str)
                or not entry.strip()
            ):
                cls._invalid(
                    f"exempt entries must be non-empty strings (got "
                    f"{entry!r})"
                )
            entries.append(_normalize_name(entry))
        if len(entries) > _MAX_EXEMPT:
            cls._invalid(
                f"exempt exceeds the {_MAX_EXEMPT:,}-entry limit "
                f"(got {len(entries):,} entries)"
            )
        return set(entries)

    # ------------------------------------------------------------------ #
    # installed mode
    # ------------------------------------------------------------------ #

    def _run_installed(self, freeze: Any) -> Dict[str, Any]:
        """Inventory: live interpreter or a pip-freeze text."""
        if freeze is not None:
            text = self._validate_text(freeze, "freeze")
            parsed = _parse_freeze(text)
            distributions = sorted(
                parsed["pins"].values(), key=lambda item: item["name"]
            )
            return {
                "mode": "installed",
                "source": "text",
                "distributions": distributions,
                "count": len(distributions),
                "editables": parsed["editables"],
                "direct_urls": parsed["direct_urls"],
                "errors": parsed["errors"],
                "comments": parsed["comments"],
                "blanks": parsed["blanks"],
                "note": (
                    "a freeze text carries no dependency metadata, so "
                    "requires_dist_count appears only in the live "
                    "source; editable and direct-reference lines are "
                    "reported but not treated as pins"
                ),
            }
        distributions, duplicates, skipped = _live_distributions()
        return {
            "mode": "installed",
            "source": "live",
            "distributions": distributions,
            "count": len(distributions),
            "duplicates": duplicates,
            "skipped_nameless": skipped,
            "note": (
                "live results are environment-dependent by definition "
                "— the same interpreter always yields the same "
                "payload, two machines will not; duplicate names are "
                "resolved first-enumeration-wins"
            ),
        }

    # ------------------------------------------------------------------ #
    # compare mode
    # ------------------------------------------------------------------ #

    def _run_compare(
        self, requirements: Any, freeze: Any, exempt: Any
    ) -> Dict[str, Any]:
        """Declared vs installed: the drift verdict."""
        req_text = self._validate_text(requirements, "requirements")
        exempt_set = self._validate_exempt(exempt)
        document = _parse_requirements_declarations(req_text)
        if freeze is not None:
            freeze_text = self._validate_text(freeze, "freeze")
            parsed = _parse_freeze(freeze_text)
            installed = {
                name: pin["version"] for name, pin in parsed["pins"].items()
            }
            source = "text"
            errors_env = parsed["errors"]
        else:
            live, _, _ = _live_distributions()
            installed = {item["name"]: item["version"] for item in live}
            source = "live"
            errors_env = []
        verifier = "packaging" if _SpecifierSet is not None else (
            "minimal-evaluator"
        )
        result = _compare_declarations(
            document, installed, exempt_set, source, verifier
        )
        result["mode"] = "compare"
        result["exempt"] = sorted(exempt_set)
        result["errors_environment"] = errors_env
        result["note"] = (
            "marker lines are listed but never judged (markers are "
            "not evaluated here — RequirementsTool keeps them "
            "verbatim); editable / URL / path lines cannot be "
            "version-compared and are listed in non_version_lines; "
            "conflict_pairs is not reported — this mode compares one "
            "file against one environment"
        )
        return result

    # ------------------------------------------------------------------ #
    # snapshot_diff mode
    # ------------------------------------------------------------------ #

    def _run_snapshot_diff(
        self, freeze_old: Any, freeze_new: Any
    ) -> Dict[str, Any]:
        """Before/after: two freeze snapshots."""
        old_text = self._validate_text(freeze_old, "freeze_old")
        new_text = self._validate_text(freeze_new, "freeze_new")
        old = _parse_freeze(old_text)
        new = _parse_freeze(new_text)
        ordering = (
            "packaging"
            if _PackagingVersion is not None
            else "pep440-minimal"
        )
        diff = _snapshot_diff(old, new, ordering)
        return {
            "mode": "snapshot_diff",
            **diff,
            "note": (
                "only name==version pins participate; editable and "
                "direct-reference lines are passed through as "
                "ignored_old / ignored_new; pairs whose versions the "
                f"{ordering} parser rejects land in unparsed instead "
                "of guessing"
            ),
        }
