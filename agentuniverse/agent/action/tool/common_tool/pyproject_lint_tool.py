#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: pyproject_lint_tool.py

r"""Pyproject.toml project-metadata linting tool, pure Python stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) at the **project-metadata layer**: the ``[project]``
table (PEP 621) of a ``pyproject.toml``. Agents that scaffold
packages, review packaging PRs or audit third-party projects need
to answer metadata questions — "is this project table complete
and well-formed?", "does the declared metadata agree with PEP 621
/ PEP 639?", "what does this project require at a glance?" — and
until now nothing in the family looked *inside* the parsed TOML:
**TomlLintTool** (#4012) stops at TOML syntax and style,
**RequirementsTool** (#4021) stops at the requirements.txt file.

Two modes, both offline and deterministic:

* ``lint`` — pyproject.toml text into structured findings
  ``{code, severity, field, message}`` (severity info / warning /
  error; ``field`` is the ``[project]`` sub-key the finding is
  about, or ``None`` for file-level findings; findings sort by
  (file-level first, field, code, message) — deterministic). The
  rule set, with severities:

  - ``toml_parse_error`` (error, file-level) — the text is not
    parseable TOML; the single finding returned, nothing else
    runs.
  - ``missing_project_table`` (error, file-level) — no
    ``[project]`` table and no ``[tool.poetry]`` either.
  - ``poetry_layout`` (info, file-level) — Poetry layout handling:
    ``[tool.poetry]`` without ``[project]`` is NOT an error — one
    info finding carries the documented best-effort mapping
    (name / version / description from ``[tool.poetry]``,
    requires-python mapped from the Poetry ``python`` constraint,
    extras as optional groups); a hybrid file (both tables) gets
    the same info with a keep-them-in-sync note while the full
    PEP 621 rule set still runs. Poetry caret / tilde constraints
    are documented as NOT PEP 508 — never errors here.
  - ``project_not_table`` (error) / ``tool_shape`` (error) — the
    top-level tables are the wrong TOML type.
  - ``name_missing`` (error) / ``name_invalid`` (error — PEP 508
    name grammar) / ``name_not_normalized`` (info — valid but not
    the PEP 503-normalized lowercase spelling).
  - ``version_missing`` (error) / ``version_invalid`` (error —
    full PEP 440 grammar: epoch, release, pre / post / dev with
    the canonical separators, local segment).
  - ``requires_python_invalid`` (error — clause set grammar
    aligned with ``packaging`` 23.x: wildcard tokens only after
    ``==`` / ``!=``, local versions only with ``==`` / ``===`` /
    ``!=``, ``~=`` needs two release components, empty segments
    tolerated; satisfiability is NEVER judged — that is
    VersionConstraintTool's job, #3995).
  - ``license_deprecated_table`` (info — the PEP 621 table form
    ``license = {text = …}`` / ``{file = …}`` is deprecated by
    PEP 639 in favor of the SPDX expression string form) /
    ``license_shape`` (error — table with neither text nor file) /
    ``license_file_dangling`` (error — ``license.file`` not among
    the supplied file listing).
  - ``description_missing`` (info).
  - ``readme_shape`` (error — table form without ``file`` or
    ``text``) / ``readme_dangling`` (error — the readme file is
    not among the supplied file listing; string and ``file``-table
    forms both checked).
  - ``authors_shape`` / ``maintainers_shape`` (error — not a
    list; an entry not a table; an entry with neither ``name``
    nor ``email``; a non-string / empty ``name``; an ``email``
    that fails the address grammar — the same family regex for
    authors and maintainers).
  - ``keywords_shape`` (error — not a list of non-empty strings).
  - ``classifiers_shape`` (error — not a list of strings) /
    ``classifier_unknown`` (info — heuristic: the first trove
    segment is not one of the known roots).
  - ``urls_shape`` (error — the ``[project.urls]`` table must map
    every key to a string).
  - ``dependencies_shape`` (error) / ``dependency_invalid``
    (error — each entry is checked as a loose PEP 508 requirement
    string with exactly the RequirementsTool grammar: name /
    extras / verbatim specifier clauses / environment markers and
    ``name @ url`` direct references).
  - ``optional_dependencies_shape`` (error) /
    ``optional_group_shape`` (error — a group value is not a list
    of strings) / ``optional_dependency_invalid`` (error).
  - ``duplicate_dependency`` (warning — the same package twice in
    one list *after* PEP 503 normalization, the RequirementsTool
    rule: ``Foo_bar`` and ``foo-bar`` collide).
  - ``dependency_overlap`` (warning — a package both in
    ``dependencies`` and in an optional group; cross-group
    duplication is deliberately not flagged — overlapping extras
    are legal).
  - ``dynamic_shape`` (error) / ``dynamic_unknown_field``
    (warning — not one of the 17 PEP 621 / PEP 639 field names) /
    ``dynamic_conflict`` (error — a field listed in ``dynamic``
    AND statically set; PEP 621 forbids both).
  - ``scripts_shape`` (error — ``scripts`` / ``gui-scripts`` not
    a string table) / ``script_name_invalid`` (error — a console
    script name outside the letters / digits / ``.`` ``_`` ``-``
    grammar) / ``entry_points_shape`` (error) /
    ``entry_point_target_invalid`` (error — the value is not
    ``dotted.module`` or ``dotted.module:object`` with an
    optional trailing ``[extra]`` bracket).
  - ``build_system_missing`` (info) / ``build_system_shape``
    (error — ``requires`` not a list of strings or
    ``build-backend`` not a string).

  Fields listed in ``dynamic`` skip their *missing* check and any
  static-shape check once ``dynamic_conflict`` fires (one finding
  per problem, no double reporting).

* ``project_summary`` — the quick-look mode:
  ``{layout, name, version, requires_python, dependency_count,
  optional_groups, python_requires_range, entry_points_count,
  dynamic_fields}`` — layout ``pep621`` / ``poetry`` / ``none``;
  the Poetry layout maps the same best-effort fields as the
  ``poetry_layout`` info note (``[tool.poetry.dependencies]``
  counted without the ``python`` key; extras as groups; caret
  python constraints converted to a range). For PEP 621,
  ``dependency_count`` counts the string entries of
  ``dependencies``, ``entry_points_count`` sums ``scripts`` +
  ``gui-scripts`` + every ``entry-points`` group, and
  ``python_requires_range`` is the parsed min / max bounds of
  ``requires-python`` (``>`` / ``>=`` / ``==`` / ``===`` / ``~=``
  feed the min — ``~= X.Y`` maps to ``>= X.Y, < X+1.0`` padded to the
  token's width — ``<`` / ``<=`` feed the max, ``!=`` clauses are
  ignored; bounds compare release segments only, so whether the
  clauses can be *satisfied together* stays with
  VersionConstraintTool (#3995)).

File-existence checks (``readme_dangling``,
``license_file_dangling``) only run when the caller supplies
``available_files`` — a list of project-root-relative paths (the
tool never touches the filesystem; the listing is the caller's,
e.g. from view_file_tool). Without the listing the checks are
skipped, documented in the result ``note``.

Division of labor inside the family (see the Distinction section
of the PR): **TomlLintTool** (#4012) lints TOML syntax and style
generically — quoting, tables, arrays, whitespace; it never
interprets ``[project]`` semantics. **RequirementsTool** (#4021)
inspects the requirements.txt *file* — PEP 508 lines, editables,
URLs, hashes, options — and diffs two snapshots. This tool is the
only one that reads the parsed ``[project]`` metadata: PEP 621
field shapes, PEP 440 versions, specifier clauses, PEP 639
license forms, dynamic-field conflicts, dependency normalization
(the same PEP 503 rule as #4021) and the quick-look summary.
Constraint *solving* is explicitly NOT done here (#3995), and
TOML syntax errors are TomlLintTool's layer (this tool reports
one ``toml_parse_error`` finding because it cannot proceed, then
stops).

Grammar notes (deliberate, documented choices):

* Version parsing implements the canonical PEP 440 grammar
  (``[N!]N(.N)*[{a|b|rc}N][.postN][.devN][+local]`` with the
  separator-tolerant spellings packaging accepts — ``1.0.b1``,
  ``1.0post``, ``v1.0``, implicit ``-N`` posts) and rejects what
  packaging 23.x rejects (``1..2``, ``next``, ``1.0-``); the
  offline tests round-trip seeded versions against
  ``packaging.version.Version`` when it is importable.
* Specifier clauses: empty segments after splitting on ``,`` are
  skipped (packaging's behavior — ``">=3.10,"`` is valid); a
  wildcard ``.*`` token only after ``==`` / ``!=``; a local
  ``+local`` segment only after ``==`` / ``===`` / ``!=``; ``~=``
  needs two release components.
* Requirement strings accept the loose RequirementsTool grammar
  (operators with flexible spacing, wildcard clauses on any
  operator, trailing commas, empty extras, ``===anything``,
  shape-checked markers) so the two tools agree by construction.
* The README / license existence check compares
  ``./``-stripped, backslash-normalized path strings
  case-sensitively — no filesystem access, deterministic on
  every platform.

Input validation is strict and happens before any parsing: wrong
parameter types raise ``ValueError``; the pyproject text is
capped at 10,000 lines, 10,000 characters per line and 4,000,000
characters total; ``available_files`` at 5,000 entries of 4,096
characters. Content-level problems (unparseable TOML, a bad
version, a dangling readme) are findings, never exceptions.
"""

import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

try:  # Python >= 3.11 ships tomllib in the stdlib.
    import tomllib
except ModuleNotFoundError:  # Python 3.10: tomli (a repo dependency).
    import tomli as tomllib  # type: ignore[no-redef]

from agentuniverse.agent.action.tool.tool import Tool

# ------------------------------------------------------------------ #
# Limits (reject pathological inputs before any work)
# ------------------------------------------------------------------ #

_MAX_LINES = 10_000
_MAX_LINE_CHARS = 10_000
_MAX_TEXT_CHARS = 4_000_000
_MAX_FILES = 5_000
_MAX_FILE_ENTRY_CHARS = 4_096

# ------------------------------------------------------------------ #
# Grammar building blocks
# ------------------------------------------------------------------ #

# PEP 508 project name: starts and ends alnum, middle may use . _ -.
_NAME_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?")
# PEP 503 canonicalization (the RequirementsTool #4021 rule):
# collapse runs of -_. to a single -, lower.
_NAME_COLLAPSE_RE = re.compile(r"[-_.]+")
# The canonical PEP 440 version grammar (separator-tolerant spellings
# accepted, matching packaging 23.x acceptance).
_VERSION_RE = re.compile(
    r"^\s*v?"
    r"(?:(?P<epoch>[0-9]+)!)?"
    r"(?P<release>[0-9]+(?:\.[0-9]+)*)"
    r"(?:[-_.]?(?P<pre_l>alpha|a|beta|b|preview|pre|c|rc)"
    r"[-_.]?(?P<pre_n>[0-9]+)?)?"
    r"(?:(?:-(?P<post_n1>[0-9]+))"
    r"|(?:[-_.]?(?P<post_l>post|rev|r)[-_.]?(?P<post_n2>[0-9]+)?))?"
    r"(?:[-_.]?dev[-_.]?(?P<dev_n>[0-9]+)?)?"
    r"(?:\+(?P<local>[a-z0-9]+(?:[-_.][a-z0-9]+)*))?"
    r"\s*$",
    re.IGNORECASE,
)
# One specifier clause: operator + version token.
_CLAUSE_RE = re.compile(r"^\s*(===|==|!=|<=|>=|~=|<|>)\s*([^\s,;#]+)\s*$")
# A PEP 508 direct reference: name[extras] @ url [; markers].
_DIRECT_REF_RE = re.compile(
    r"^\s*([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)"
    r"(\s*\[[^\]]*\])?"
    r"\s*@\s*(\S+)"
    r"(?:\s*;\s*(.+))?$"
)
# Marker safety (shape only, never evaluated — the family rule).
_MARKER_CHARS_RE = re.compile(r"^[A-Za-z0-9_.!<>~=\"'()\s-]+$")
_MARKER_OP_RE = re.compile(r"===|==|!=|<=|>=|<|>|~=")
# Simplified RFC 5322 address grammar — the same regex for authors
# and maintainers (the family rule).
_EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)
# Console script / entry-point target: dotted module [: dotted
# object] with an optional trailing extras bracket.
_IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
_DOTTED_TARGET_RE = re.compile(
    rf"^{_IDENT}(?:\.{_IDENT})*"
    rf"(?::{_IDENT}(?:\.{_IDENT})*)?"
    r"(?:\s*\[[^\]]+\])?$"
)
# Console script names share the project-name grammar.
_SCRIPT_NAME_RE = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$"
)
# Leading release components of a version token (the ~= rule).
_LEADING_RELEASE_RE = re.compile(r"^\d+(?:\.\d+)*")
# Poetry caret python constraint: ^X.Y.Z
_POETRY_CARET_RE = re.compile(r"^\s*\^(\d+(?:\.\d+)*)\s*$")

# Known trove classifier roots (the classifier_unknown heuristic).
_CLASSIFIER_ROOTS = frozenset(
    {
        "Development Status",
        "Environment",
        "Framework",
        "Intended Audience",
        "License",
        "Natural Language",
        "Operating System",
        "Programming Language",
        "Topic",
        "Typing",
        "Private",
    }
)

# The PEP 621 (+ PEP 639 license-files) field names dynamic may list.
_DYNAMIC_FIELDS = frozenset(
    {
        "name",
        "version",
        "description",
        "readme",
        "requires-python",
        "license",
        "license-files",
        "authors",
        "maintainers",
        "keywords",
        "classifiers",
        "urls",
        "dependencies",
        "optional-dependencies",
        "scripts",
        "gui-scripts",
        "entry-points",
    }
)

# Lint severities per finding code.
_SEVERITIES: Dict[str, str] = {
    "toml_parse_error": "error",
    "missing_project_table": "error",
    "poetry_layout": "info",
    "project_not_table": "error",
    "tool_shape": "error",
    "name_missing": "error",
    "name_invalid": "error",
    "name_not_normalized": "info",
    "version_missing": "error",
    "version_invalid": "error",
    "description_missing": "info",
    "readme_shape": "error",
    "readme_dangling": "error",
    "requires_python_invalid": "error",
    "license_deprecated_table": "info",
    "license_shape": "error",
    "license_file_dangling": "error",
    "authors_shape": "error",
    "maintainers_shape": "error",
    "keywords_shape": "error",
    "classifiers_shape": "error",
    "classifier_unknown": "info",
    "urls_shape": "error",
    "dependencies_shape": "error",
    "dependency_invalid": "error",
    "optional_dependencies_shape": "error",
    "optional_group_shape": "error",
    "optional_dependency_invalid": "error",
    "duplicate_dependency": "warning",
    "dependency_overlap": "warning",
    "dynamic_shape": "error",
    "dynamic_unknown_field": "warning",
    "dynamic_conflict": "error",
    "scripts_shape": "error",
    "script_name_invalid": "error",
    "entry_points_shape": "error",
    "entry_point_target_invalid": "error",
    "build_system_missing": "info",
    "build_system_shape": "error",
}

_NOTE_DIVISION = (
    "the project-metadata layer: the parsed [project] table "
    "(PEP 621) is linted — TomlLintTool (#4012) covers TOML "
    "syntax / style generically and RequirementsTool (#4021) the "
    "requirements.txt file, so neither sees metadata semantics; "
    "dependency names normalize with the RequirementsTool PEP 503 "
    "rule and requirement strings use its loose PEP 508 grammar; "
    "constraint-set solving stays with VersionConstraintTool "
    "(#3995) — bounds are parsed here, never judged for "
    "satisfiability"
)

_NOTE_POETRY = (
    "poetry layout is handled best-effort, never as errors: "
    "name / version / description map from [tool.poetry], "
    "requires-python from its python constraint (caret ^X.Y "
    "converted to >=X.Y,<X+1.0 best-effort), extras become "
    "optional groups and [tool.poetry.dependencies] is counted "
    "without the python key; Poetry caret / tilde constraints are "
    "NOT PEP 508 — run 'poetry check' or the Poetry migration "
    "guide for a full conversion to [project]"
)


# ------------------------------------------------------------------ #
# Pure helpers — names, versions, specifiers
# ------------------------------------------------------------------ #

def _normalize_name(name: str) -> str:
    """PEP 503 normalization (the RequirementsTool #4021 rule).

    Lowercase, runs of ``-_.`` collapsed to a single ``-``.
    """
    return _NAME_COLLAPSE_RE.sub("-", name).lower()


def _parse_version(text: str) -> Optional[Dict[str, Any]]:
    """Parse a PEP 440 version string; None when invalid.

    Accepts the separator-tolerant spellings packaging accepts
    (``1.0.b1``, ``1.0post``, ``1.0-1``, ``v1.0``, ``1!2.0``,
    ``1.0+local-1``); returns ``{epoch, release, pre, post, dev,
    local}`` with ``release`` the dot-joined release digits.
    """
    match = _VERSION_RE.match(text)
    if match is None:
        return None
    return {
        "epoch": match.group("epoch"),
        "release": match.group("release"),
        "pre": match.group("pre_l"),
        "post": match.group("post_l") or match.group("post_n1"),
        "dev": match.group("dev_n") is not None or None,
        "local": match.group("local"),
    }


def _version_key(parsed: Dict[str, Any]) -> Tuple[int, Tuple[int, ...]]:
    """Comparable key over (epoch, release) for bound arithmetic.

    Trailing zeros are stripped per PEP 440 (``1.0`` == ``1``);
    pre / post / dev / local never participate in bound picking.
    """
    epoch = int(parsed["epoch"] or 0)
    release = [int(part) for part in parsed["release"].split(".")]
    while release and release[-1] == 0:
        release.pop()
    return (epoch, tuple(release))


def _parse_specifier(text: str) -> Tuple[
    Optional[List[Tuple[str, str]]], Optional[str]
]:
    """Parse a comma-separated specifier set (requires-python).

    Aligned with ``packaging`` 23.x: empty segments after the
    split are skipped (``">=3.10,"`` is fine, so is the empty
    string); each clause is ``operator + version-token``;
    ``===`` (arbitrary equality) takes any token verbatim; a
    ``.*`` wildcard token only after ``==`` / ``!=``; a ``+local``
    segment only after ``==`` / ``===`` / ``!=``; ``~=`` needs
    two release components. Returns ``(clauses, error)`` with the
    clauses as ``(operator, version-token)`` pairs, verbatim.
    Satisfiability is NEVER judged (VersionConstraintTool's job).
    """
    clauses: List[Tuple[str, str]] = []
    segments = [segment for segment in text.split(",") if segment.strip()]
    if not segments:
        return [], None
    for segment in segments:
        match = _CLAUSE_RE.match(segment)
        if match is None:
            return None, (
                f"malformed specifier clause {segment.strip()!r} — "
                f"expected '<op><version>' with op one of "
                f"== != <= >= ~= < > ==="
            )
        operator, token = match.group(1), match.group(2)
        if operator == "===":
            # Arbitrary equality takes any token verbatim (the
            # packaging rule) — wildcards and locals included.
            clauses.append((operator, token))
            continue
        if token.endswith(".*"):
            if operator not in ("==", "!="):
                return None, (
                    f"the wildcard token {token!r} is only valid "
                    f"with '==' or '!=' (got {operator!r})"
                )
            prefix = _parse_version(token[:-2])
            if prefix is None:
                return None, (
                    f"the wildcard token {token!r} has an invalid "
                    f"version prefix"
                )
            clauses.append((operator, token))
            continue
        parsed = _parse_version(token)
        if parsed is None:
            return None, (
                f"the version {token!r} of clause "
                f"{operator + token!r} is not PEP 440"
            )
        if parsed["local"] is not None and operator not in (
            "==", "===", "!="
        ):
            return None, (
                f"a local version segment is only valid with "
                f"'==' / '===' / '!=' (got {operator!r} in "
                f"{operator + token!r})"
            )
        if operator == "~=":
            components = parsed["release"].split(".")
            if len(components) < 2:
                return None, (
                    f"the compatible-release clause {operator + token!r} "
                    f"needs at least two release components (e.g. "
                    f"'~=3.10')"
                )
        clauses.append((operator, token))
    return clauses, None


def _bump_for_compatible_release(token: str) -> str:
    """The exclusive upper bound of ``~= token`` (PEP 440).

    ``~=3.10`` implies ``< 4.0`` (the penultimate component +1,
    the tail dropped, formatted at the token's component width);
    ``~=2.2.1`` implies ``< 2.3.0``.
    """
    components = [int(part) for part in token.split(".")]
    bumped = components[:-1]
    bumped[-1] += 1
    while len(bumped) < len(components):
        bumped.append(0)
    return ".".join(str(part) for part in bumped)


def _python_bounds(
    clauses: List[Tuple[str, str]]
) -> Dict[str, Optional[str]]:
    """The min / max bounds of a parsed requires-python set.

    ``>`` / ``>=`` / ``==`` / ``===`` / ``~=`` feed the min (the
    largest lower bound wins), ``<`` / ``<=`` / ``~=`` feed the max (the
    smallest upper bound wins), ``!=`` clauses are ignored. Bound
    values are the verbatim clause tokens (``~=`` contributes its
    computed bump). Returns ``{"min": …, "max": …}`` with None for
    an unbounded side. Only release segments compare — never
    satisfiability.
    """
    min_token: Optional[str] = None
    max_token: Optional[str] = None
    min_key: Optional[Tuple[int, Tuple[int, ...]]] = None
    max_key: Optional[Tuple[int, Tuple[int, ...]]] = None
    for operator, token in clauses:
        if operator in (">", ">=", "==", "==="):
            parsed = _parse_version(token)
            if parsed is None:
                continue
            key = _version_key(parsed)
            if min_key is None or key > min_key:
                min_key, min_token = key, token
            # An exact pin (no wildcard) bounds both sides.
            if (
                operator in ("==", "===")
                and not token.endswith(".*")
                and (max_key is None or key < max_key)
            ):
                max_key, max_token = key, token
        elif operator == "~=":
            parsed = _parse_version(token)
            if parsed is None:
                continue
            key = _version_key(parsed)
            bump = _bump_for_compatible_release(token)
            if min_key is None or key > min_key:
                min_key, min_token = key, token
            bump_key = _version_key(_parse_version(bump))  # type: ignore[arg-type]
            if max_key is None or bump_key < max_key:
                max_key, max_token = bump_key, bump
        elif operator in ("<", "<="):
            parsed = _parse_version(token)
            if parsed is None:
                continue
            key = _version_key(parsed)
            if max_key is None or key < max_key:
                max_key, max_token = key, token
    return {"min": min_token, "max": max_token}


# ------------------------------------------------------------------ #
# Pure helpers — requirement strings (RequirementsTool grammar)
# ------------------------------------------------------------------ #

def _validate_clauses(specifier: str) -> Optional[str]:
    """Loosely validate a comma-separated PEP 440 clause list.

    Exactly the RequirementsTool rule: each clause is ``operator
    + version-token`` (flexible spacing, any token including the
    ``==1.2.*`` wildcard), a trailing comma is tolerated, ``~=``
    needs two release components.
    """
    text = specifier.strip()
    if text.endswith(","):
        text = text[:-1].rstrip()
    if not text:
        return "an empty specifier is not a specifier (drop the commas)"
    for clause in text.split(","):
        match = _CLAUSE_RE.match(clause)
        if match is None:
            return (
                f"malformed specifier clause {clause.strip()!r} — "
                f"expected '<op><version>'"
            )
        operator, version = match.group(1), match.group(2)
        if operator == "~=":
            leading = _LEADING_RELEASE_RE.match(version)
            components = (
                leading.group(0).split(".") if leading is not None else []
            )
            if len(components) < 2:
                return (
                    f"the compatible-release clause {clause.strip()!r} "
                    f"needs at least two release components (e.g. "
                    f"'~=1.2')"
                )
    return None


def _validate_markers(markers: str) -> Optional[str]:
    """Shape-check an environment-marker expression (loosely).

    The family rule: non-empty, safe charset, balanced quotes and
    parentheses, at least one comparison. Never evaluated.
    """
    text = markers.strip()
    if not text:
        return "an environment marker after ';' must not be empty"
    if not _MARKER_CHARS_RE.match(text):
        return (
            f"the marker {text[:64]!r} uses characters outside the "
            f"marker grammar"
        )
    if text.count("'") % 2 or text.count('"') % 2:
        return f"the marker {text[:64]!r} leaves a quote unterminated"
    if _MARKER_OP_RE.search(text) is None and " in " not in f" {text} ":
        return (
            f"the marker {text[:64]!r} contains no comparison — a "
            f"marker is built from 'variable <op> value' comparisons "
            f"joined by and / or"
        )
    depth = 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return (
                    f"the marker {text[:64]!r} closes a parenthesis "
                    f"that was never opened"
                )
    if depth != 0:
        return (
            f"the marker {text[:64]!r} leaves {depth} unclosed "
            f"parenthesis(es)"
        )
    return None


def _parse_requirement_string(text: str) -> Tuple[
    Optional[str], Optional[str]
]:
    """Parse one PEP 508 requirement string (loose, #4021 rule).

    Accepts ``name``, ``name[extras] specifier ; markers`` and
    ``name[extras] @ url`` direct references; returns the PEP 503
    normalized name (or None for a nameless failure) and an error
    message (or None). Editable / hash / requirements-file option
    syntax does not exist in the [project] array form and is an
    error here.
    """
    stripped = text.strip()
    if not stripped:
        return None, "an empty string is not a requirement"

    direct = _DIRECT_REF_RE.match(stripped)
    if direct is not None:
        name_raw, _extras_raw, url, markers = direct.groups()
        if markers is not None:
            marker_error = _validate_markers(markers)
            if marker_error is not None:
                return None, marker_error
        return _normalize_name(name_raw), None

    name_match = _NAME_RE.match(stripped)
    if name_match is None or name_match.start() != 0:
        return None, (
            f"expected a PEP 508 package name at the start — got "
            f"{stripped[:64]!r}"
        )
    name_raw = name_match.group(0)
    rest = stripped[name_match.end():].lstrip()

    if rest.startswith("["):
        close = rest.find("]")
        if close < 0:
            return None, f"the extras bracket of {name_raw!r} is never closed"
        rest = rest[close + 1:].lstrip()

    if rest.startswith("@"):
        return None, (
            f"the direct reference "
            f"{name_raw + ' @ ' + rest[1:].strip()!r} is malformed — "
            f"a valid form is 'name @ <url>' with the URL free of "
            f"spaces"
        )

    body, semicolon, marker_part = rest.partition(";")
    specifier = body.strip()
    if semicolon:
        marker_error = _validate_markers(marker_part)
        if marker_error is not None:
            return None, marker_error
    if specifier:
        clause_error = _validate_clauses(specifier)
        if clause_error is not None:
            return None, clause_error
    return _normalize_name(name_raw), None


# ------------------------------------------------------------------ #
# Pure helpers — file listing, classifiers, entry points
# ------------------------------------------------------------------ #

def _normalize_path(path: str) -> str:
    """Normalize a project-root-relative path for comparison.

    Leading ``./`` dropped, backslashes folded to forward slashes,
    surrounding whitespace stripped. Case-sensitive (documented).
    """
    stripped = path.strip().replace("\\", "/")
    while stripped.startswith("./"):
        stripped = stripped[2:]
    return stripped


def _classifier_root(classifier: str) -> str:
    """The first trove segment of a classifier string."""
    return classifier.split(" :: ", 1)[0].strip()


def _entry_points_count(project: Dict[str, Any]) -> int:
    """Total console scripts + gui scripts + entry-point entries."""
    count = 0
    for key in ("scripts", "gui-scripts"):
        table = project.get(key)
        if isinstance(table, dict):
            count += len(table)
    groups = project.get("entry-points")
    if isinstance(groups, dict):
        for group in groups.values():
            if isinstance(group, dict):
                count += len(group)
    return count


# ------------------------------------------------------------------ #
# Poetry layout mapping (best-effort, informational only)
# ------------------------------------------------------------------ #

def _poetry_mapping(poetry: Any) -> Dict[str, Any]:
    """The documented best-effort [tool.poetry] -> [project] map."""
    mapping: Dict[str, Any] = {
        "name": None,
        "version": None,
        "description": None,
        "requires_python": None,
        "dependency_count": 0,
        "optional_groups": [],
    }
    if not isinstance(poetry, dict):
        return mapping
    for key, target in (
        ("name", "name"),
        ("version", "version"),
        ("description", "description"),
    ):
        value = poetry.get(key)
        if isinstance(value, str) and value:
            mapping[target] = value
    python_constraint = None
    dependencies = poetry.get("dependencies")
    if isinstance(dependencies, dict):
        python_constraint = dependencies.get("python")
        mapping["dependency_count"] = len(
            [key for key in dependencies if key != "python"]
        )
    if isinstance(python_constraint, str) and python_constraint:
        mapping["requires_python"] = python_constraint
    extras = poetry.get("extras")
    if isinstance(extras, dict):
        mapping["optional_groups"] = sorted(str(key) for key in extras)
    return mapping


def _poetry_python_range(constraint: Optional[str]) -> Optional[
    Dict[str, Optional[str]]
]:
    """Best-effort range for a Poetry python constraint.

    A caret ``^X.Y`` converts to ``>=X.Y, <X+1.0`` (standard caret
    semantics on the leading non-zero component are documented as
    a simplification); anything parseable as a PEP 440 clause set
    parses directly; anything else yields None. Never an error.
    """
    if not constraint or not isinstance(constraint, str):
        return None
    caret = _POETRY_CARET_RE.match(constraint)
    if caret is not None:
        token = caret.group(1)
        parsed = _parse_version(token)
        if parsed is None:
            return None
        components = [int(part) for part in token.split(".")]
        if components[0] != 0 or len(components) == 1:
            bump = [components[0] + 1]
        elif len(components) >= 2 and components[1] != 0:
            bump = [0, components[1] + 1]
        elif len(components) >= 3:
            bump = [0, 0, components[2] + 1]
        else:
            return None
        width = max(len(components), len(bump))
        while len(components) < width:
            components.append(0)
        while len(bump) < width:
            bump.append(0)
        return {
            "min": ".".join(str(part) for part in components),
            "max": ".".join(str(part) for part in bump),
        }
    clauses, error = _parse_specifier(constraint)
    if error is not None or not clauses:
        return None
    return _python_bounds(clauses)


# ------------------------------------------------------------------ #
# The linter (pure function over the parsed document)
# ------------------------------------------------------------------ #

def _lint_document(
    doc: Dict[str, Any], available_files: Optional[set]
) -> List[Dict[str, Any]]:
    """Run every lint rule over a parsed pyproject document."""
    findings: List[Dict[str, Any]] = []

    def add(code: str, detail: str, field: Optional[str] = None) -> None:
        findings.append(
            {
                "code": code,
                "severity": _SEVERITIES[code],
                "field": field,
                "message": detail,
            }
        )

    # --- top-level shapes ----------------------------------------- #
    tool = doc.get("tool")
    poetry = tool.get("poetry") if isinstance(tool, dict) else None
    if "tool" in doc and not isinstance(tool, dict):
        add(
            "tool_shape",
            "the top-level 'tool' value must be a TOML table — "
            "tool configuration cannot be read",
            "tool",
        )
        poetry = None

    build = doc.get("build-system")
    if build is None:
        add(
            "build_system_missing",
            "no [build-system] table — frontends fall back to legacy "
            "setuptools behavior; declaring requires and "
            "build-backend is recommended (PEP 517)",
        )
    elif not isinstance(build, dict):
        add(
            "build_system_shape",
            "the top-level 'build-system' value must be a TOML table",
            "build-system",
        )
    else:
        requires = build.get("requires")
        if requires is not None and (
            not isinstance(requires, list)
            or any(not isinstance(item, str) for item in requires)
        ):
            add(
                "build_system_shape",
                "build-system.requires must be a list of strings",
                "build-system.requires",
            )
        backend = build.get("build-backend")
        if backend is not None and not isinstance(backend, str):
            add(
                "build_system_shape",
                "build-system.build-backend must be a string",
                "build-system.build-backend",
            )

    # --- project detection ---------------------------------------- #
    if "project" not in doc:
        if isinstance(poetry, dict):
            mapping = _poetry_mapping(poetry)
            add(
                "poetry_layout",
                "no [project] table — [tool.poetry] detected (Poetry "
                f"layout), mapped best-effort: name={mapping['name']!r} "
                f"version={mapping['version']!r} "
                f"description={mapping['description']!r} "
                f"requires-python={mapping['requires_python']!r} "
                f"({len(mapping['optional_groups'])} extras, "
                f"{mapping['dependency_count']} dependencies without "
                "the python key); " + _NOTE_POETRY,
            )
        else:
            add(
                "missing_project_table",
                "no [project] table (PEP 621) and no [tool.poetry] "
                "either — the file declares no project metadata at "
                "all",
            )
        return findings

    project = doc.get("project")
    if not isinstance(project, dict):
        add(
            "project_not_table",
            "the top-level 'project' value must be a TOML table "
            "(PEP 621)",
            "project",
        )
        return findings

    if isinstance(poetry, dict):
        add(
            "poetry_layout",
            "both [project] and [tool.poetry] are present (hybrid, "
            "typical mid-migration state) — modern tools read "
            "[project], Poetry still reads [tool.poetry]: keep the "
            "two in sync (Poetry >= 1.2 supports PEP 621 project "
            "tables); " + _NOTE_POETRY,
        )

    # --- dynamic (parsed first: it gates the missing checks) ------ #
    dynamic: List[str] = []
    dynamic_raw = project.get("dynamic")
    if dynamic_raw is not None:
        if (
            not isinstance(dynamic_raw, list)
            or any(
                isinstance(item, (dict, list, bool))
                or not isinstance(item, str)
                for item in dynamic_raw
            )
        ):
            add(
                "dynamic_shape",
                "project.dynamic must be a list of strings (the "
                "field names the build backend computes)",
                "dynamic",
            )
        else:
            dynamic = [str(item) for item in dynamic_raw]
            for item in dynamic:
                if item not in _DYNAMIC_FIELDS:
                    add(
                        "dynamic_unknown_field",
                        f"dynamic entry {item!r} is not a PEP 621 / "
                        f"PEP 639 field name (known: "
                        f"{', '.join(sorted(_DYNAMIC_FIELDS))})",
                        "dynamic",
                    )
            for item in dict.fromkeys(dynamic):
                if item in project:
                    add(
                        "dynamic_conflict",
                        f"the field {item!r} is listed in dynamic AND "
                        f"set statically — PEP 621 forbids declaring "
                        f"a field dynamic while also giving it a "
                        f"value",
                        item,
                    )

    def skip(field: str) -> bool:
        """Whether the field's static checks are skipped (dynamic
        conflict already reported, or legitimately dynamic)."""
        return field in dynamic

    # --- name ------------------------------------------------------ #
    if not skip("name"):
        if "name" not in project:
            add(
                "name_missing",
                "project.name is missing — every distribution "
                "needs a name",
                "name",
            )
        else:
            name = project["name"]
            if not isinstance(name, str) or not _NAME_RE.fullmatch(name):
                add(
                    "name_invalid",
                    f"project.name {name!r} is not a valid PEP 508 "
                    f"project name (letters / digits / '.' '_' '-' "
                    f"starting and ending with a letter or digit)",
                    "name",
                )
            elif name != _normalize_name(name):
                add(
                    "name_not_normalized",
                    f"project.name {name!r} is not the PEP 503 "
                    f"normalized spelling "
                    f"(expected {_normalize_name(name)!r} — "
                    f"lowercase, '-_' '.' runs collapsed)",
                    "name",
                )

    # --- version --------------------------------------------------- #
    if not skip("version"):
        if "version" not in project:
            add(
                "version_missing",
                "project.version is missing and not declared "
                "dynamic — every distribution needs a version",
                "version",
            )
        else:
            version = project["version"]
            if not isinstance(version, str) or _parse_version(
                version
            ) is None:
                add(
                    "version_invalid",
                    f"project.version {version!r} is not a valid "
                    f"PEP 440 version (expected the shape "
                    f"[N!]N(.N)*[aN|bN|rcN][.postN][.devN][+local] "
                    f"— e.g. '1.0.0rc1', '1!2.0', '0.0.19')",
                    "version",
                )

    # --- description (info only) ----------------------------------- #
    if not skip("description") and "description" not in project:
        add(
            "description_missing",
            "project.description is missing — a one-line summary is "
            "what indexes show next to the name (info, not "
            "required)",
            "description",
        )

    # --- readme ----------------------------------------------------- #
    if not skip("readme") and "readme" in project:
        readme = project["readme"]
        readme_file: Optional[str] = None
        if isinstance(readme, str):
            readme_file = readme
        elif isinstance(readme, dict):
            if "file" in readme:
                readme_file = (
                    readme["file"]
                    if isinstance(readme["file"], str) else None
                )
                if readme_file is None:
                    add(
                        "readme_shape",
                        "project.readme.file must be a string",
                        "readme",
                    )
            elif "text" not in readme:
                add(
                    "readme_shape",
                    "the project.readme table has neither 'file' nor "
                    "'text' — one of the two is required",
                    "readme",
                )
        else:
            add(
                "readme_shape",
                f"project.readme {readme!r} must be a file path "
                f"string or a table with 'file'/'text'",
                "readme",
            )
        if readme_file is not None and available_files is not None:
            if _normalize_path(readme_file) not in available_files:
                add(
                    "readme_dangling",
                    f"project.readme points at {readme_file!r} which "
                    f"is not among the {len(available_files)} "
                    f"supplied project files — the reference dangles",
                    "readme",
                )

    # --- requires-python ------------------------------------------- #
    if not skip("requires-python") and "requires-python" in project:
        spec = project["requires-python"]
        if not isinstance(spec, str):
            add(
                "requires_python_invalid",
                f"project.requires-python {spec!r} must be a "
                f"specifier-set string (e.g. '>=3.10')",
                "requires-python",
            )
        else:
            _clauses, spec_error = _parse_specifier(spec)
            if spec_error is not None:
                add(
                    "requires_python_invalid",
                    f"project.requires-python {spec!r}: {spec_error}",
                    "requires-python",
                )

    # --- license (PEP 639 aware) ------------------------------------ #
    if not skip("license") and "license" in project:
        license_value = project["license"]
        if isinstance(license_value, dict):
            if "text" not in license_value and "file" not in license_value:
                add(
                    "license_shape",
                    "the project.license table has neither 'text' "
                    "nor 'file' — one of the two is required",
                    "license",
                )
            else:
                add(
                    "license_deprecated_table",
                    "project.license uses the table form "
                    "({"
                    + ", ".join(
                        f"{key}=…" for key in license_value
                    )
                    + "}) — deprecated by PEP 639: use an SPDX "
                    "license expression string (license = \"MIT\") "
                    "and the license-files list for the full text",
                    "license",
                )
            license_file = license_value.get("file")
            if (
                isinstance(license_file, str)
                and available_files is not None
                and _normalize_path(license_file) not in available_files
            ):
                add(
                    "license_file_dangling",
                    f"project.license.file points at {license_file!r} "
                    f"which is not among the supplied project "
                    f"files — the reference dangles",
                    "license",
                )
        elif not isinstance(license_value, str):
            add(
                "license_shape",
                f"project.license {license_value!r} must be an SPDX "
                f"expression string or a table with 'text'/'file'",
                "license",
            )

    # --- authors / maintainers (the family email regex) ------------- #
    for field, plural in (("authors", "author"), (
        "maintainers", "maintainer"
    )):
        if skip(field) or field not in project:
            continue
        entries = project[field]
        if not isinstance(entries, list):
            add(
                f"{field}_shape",
                f"project.{field} must be a list of tables with "
                f"name and/or email",
                field,
            )
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                add(
                    f"{field}_shape",
                    f"the {plural} entry #{index + 1} {entry!r} must "
                    f"be a table with name and/or email (PEP 621)",
                    field,
                )
                continue
            name = entry.get("name")
            email = entry.get("email")
            has_name = isinstance(name, str) and name.strip()
            has_email = isinstance(email, str) and email.strip()
            if not has_name and not has_email:
                add(
                    f"{field}_shape",
                    f"the {plural} entry #{index + 1} has neither "
                    f"name nor email — at least one is required",
                    field,
                )
                continue
            if "name" in entry and not has_name:
                add(
                    f"{field}_shape",
                    f"the {plural} entry #{index + 1} name must be a "
                    f"non-empty string",
                    field,
                )
            if has_email and not _EMAIL_RE.match(email):
                add(
                    f"{field}_shape",
                    f"the {plural} entry #{index + 1} email "
                    f"{email!r} is not a valid address "
                    f"(local@domain.tld)",
                    field,
                )

    # --- keywords ---------------------------------------------------- #
    if not skip("keywords") and "keywords" in project:
        keywords = project["keywords"]
        if (
            not isinstance(keywords, list)
            or any(
                isinstance(item, (dict, list, bool))
                or not isinstance(item, str)
                or not item.strip()
                for item in keywords
            )
        ):
            add(
                "keywords_shape",
                "project.keywords must be a list of non-empty "
                "strings",
                "keywords",
            )

    # --- classifiers -------------------------------------------------- #
    if not skip("classifiers") and "classifiers" in project:
        classifiers = project["classifiers"]
        if (
            not isinstance(classifiers, list)
            or any(
                isinstance(item, (dict, list, bool))
                or not isinstance(item, str)
                for item in classifiers
            )
        ):
            add(
                "classifiers_shape",
                "project.classifiers must be a list of trove "
                "classifier strings",
                "classifiers",
            )
        elif isinstance(classifiers, list):
            for item in classifiers:
                if isinstance(item, str) and (
                    _classifier_root(item) not in _CLASSIFIER_ROOTS
                ):
                    add(
                        "classifier_unknown",
                        f"the classifier {item!r} does not start "
                        f"with a known trove root (heuristic — the "
                        f"known roots: "
                        f"{', '.join(sorted(_CLASSIFIER_ROOTS))})",
                        "classifiers",
                    )

    # --- urls --------------------------------------------------------- #
    if not skip("urls") and "urls" in project:
        urls = project["urls"]
        if (
            not isinstance(urls, dict)
            or any(not isinstance(value, str) for value in urls.values())
        ):
            add(
                "urls_shape",
                "project.urls must be a table mapping every label "
                "to a URL string",
                "urls",
            )

    # --- dependencies (+ duplicates, RequirementsTool grammar) -------- #
    dependency_names: set = set()
    if not skip("dependencies") and "dependencies" in project:
        dependencies = project["dependencies"]
        if (
            not isinstance(dependencies, list)
            or any(
                isinstance(item, (dict, list, bool))
                or not isinstance(item, str)
                for item in dependencies
            )
        ):
            add(
                "dependencies_shape",
                "project.dependencies must be a list of PEP 508 "
                "requirement strings",
                "dependencies",
            )
        elif isinstance(dependencies, list):
            seen: Dict[str, str] = {}
            for item in dependencies:
                name, req_error = _parse_requirement_string(item)
                if req_error is not None:
                    add(
                        "dependency_invalid",
                        f"the dependency {item!r}: {req_error}",
                        "dependencies",
                    )
                    continue
                if name in seen:
                    add(
                        "duplicate_dependency",
                        f"the package {name!r} appears twice in "
                        f"project.dependencies ({seen[name]!r} and "
                        f"{item!r}) after PEP 503 normalization",
                        "dependencies",
                    )
                else:
                    seen[name] = item
            dependency_names = set(seen)

    # --- optional-dependencies (+ dup + overlap) ----------------------- #
    if not skip("optional-dependencies") and (
        "optional-dependencies" in project
    ):
        optionals = project["optional-dependencies"]
        if not isinstance(optionals, dict):
            add(
                "optional_dependencies_shape",
                "project.optional-dependencies must be a table of "
                "group name -> requirement list",
                "optional-dependencies",
            )
        else:
            overlaps: List[Tuple[str, str]] = []
            for group in sorted(optionals):
                group_field = f"optional-dependencies.{group}"
                entries = optionals[group]
                if (
                    not isinstance(entries, list)
                    or any(
                        isinstance(item, (dict, list, bool))
                        or not isinstance(item, str)
                        for item in entries
                    )
                ):
                    add(
                        "optional_group_shape",
                        f"the optional group {group!r} must be a "
                        f"list of PEP 508 requirement strings",
                        group_field,
                    )
                    continue
                seen: Dict[str, str] = {}
                for item in entries:
                    name, req_error = _parse_requirement_string(item)
                    if req_error is not None:
                        add(
                            "optional_dependency_invalid",
                            f"the group {group!r} dependency "
                            f"{item!r}: {req_error}",
                            group_field,
                        )
                        continue
                    if name in seen:
                        add(
                            "duplicate_dependency",
                            f"the package {name!r} appears twice in "
                            f"the group {group!r} ({seen[name]!r} "
                            f"and {item!r}) after PEP 503 "
                            f"normalization",
                            group_field,
                        )
                    else:
                        seen[name] = item
                for name in sorted(seen):
                    if name in dependency_names:
                        overlaps.append((group, name))
            for group, name in sorted(overlaps):
                add(
                    "dependency_overlap",
                    f"the package {name!r} is in project.dependencies "
                    f"AND in the optional group {group!r} — an extra "
                    f"re-listing a core dependency usually means a "
                    f"mistake",
                    f"optional-dependencies.{group}",
                )

    # --- scripts / gui-scripts ------------------------------------------ #
    def lint_scripts_table(table: Any, field: str) -> None:
        if not isinstance(table, dict) or any(
            not isinstance(value, str) for value in table.values()
        ):
            add(
                "scripts_shape",
                f"project.{field} must be a table mapping console "
                f"script names to 'module:object' strings",
                field,
            )
            return
        for script_name in sorted(table):
            if not _SCRIPT_NAME_RE.match(script_name):
                add(
                    "script_name_invalid",
                    f"the {field} name {script_name!r} contains "
                    f"invalid characters — console script names use "
                    f"letters / digits / '.' '_' '-'",
                    field,
                )
            target = table[script_name]
            if not _DOTTED_TARGET_RE.match(target):
                add(
                    "entry_point_target_invalid",
                    f"the {field} entry {script_name!r} target "
                    f"{target!r} must be 'dotted.module' or "
                    f"'dotted.module:object' with an optional "
                    f"trailing [extra] bracket",
                    field,
                )

    if not skip("scripts") and "scripts" in project:
        lint_scripts_table(project["scripts"], "scripts")
    if not skip("gui-scripts") and "gui-scripts" in project:
        lint_scripts_table(project["gui-scripts"], "gui-scripts")

    # --- entry-points ----------------------------------------------------- #
    if not skip("entry-points") and "entry-points" in project:
        groups = project["entry-points"]
        if not isinstance(groups, dict):
            add(
                "entry_points_shape",
                "project.entry-points must be a table of group "
                "name -> entry tables",
                "entry-points",
            )
        else:
            for group in sorted(groups):
                group_field = f"entry-points.{group}"
                entries = groups[group]
                if (
                    not isinstance(entries, dict)
                    or any(
                        not isinstance(value, str)
                        for value in entries.values()
                    )
                ):
                    add(
                        "entry_points_shape",
                        f"the entry-points group {group!r} must be a "
                        f"table mapping names to 'module:object' "
                        f"strings",
                        group_field,
                    )
                    continue
                for entry_name in sorted(entries):
                    target = entries[entry_name]
                    if not _DOTTED_TARGET_RE.match(target):
                        add(
                            "entry_point_target_invalid",
                            f"the entry-points {group!r} entry "
                            f"{entry_name!r} target {target!r} must "
                            f"be 'dotted.module' or "
                            f"'dotted.module:object'",
                            group_field,
                        )

    # --- deterministic ordering ------------------------------------------- #
    findings.sort(
        key=lambda finding: (
            0 if finding["field"] is None else 1,
            finding["field"] or "",
            finding["code"],
            finding["message"],
        )
    )
    return findings


# ------------------------------------------------------------------ #
# The summary (pure function over the parsed document)
# ------------------------------------------------------------------ #

def _summarize_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """The quick-look summary of a parsed pyproject document."""
    tool = doc.get("tool")
    poetry = tool.get("poetry") if isinstance(tool, dict) else None
    project = doc.get("project") if isinstance(doc.get("project"), dict) else None

    if project is None and isinstance(poetry, dict):
        mapping = _poetry_mapping(poetry)
        return {
            "layout": "poetry",
            "name": mapping["name"],
            "version": mapping["version"],
            "requires_python": mapping["requires_python"],
            "dependency_count": mapping["dependency_count"],
            "optional_groups": mapping["optional_groups"],
            "python_requires_range": _poetry_python_range(
                mapping["requires_python"]
            ),
            "entry_points_count": _poetry_entry_points_count(poetry),
            "dynamic_fields": [],
            "note": _NOTE_POETRY,
        }
    if project is None:
        return {
            "layout": "none",
            "name": None,
            "version": None,
            "requires_python": None,
            "dependency_count": 0,
            "optional_groups": [],
            "python_requires_range": None,
            "entry_points_count": 0,
            "dynamic_fields": [],
            "note": (
                "no [project] table and no [tool.poetry] — the file "
                "declares no project metadata (see the lint mode's "
                "missing_project_table finding)"
            ),
        }

    name = project.get("name")
    version = project.get("version")
    requires_python = project.get("requires-python")
    dependencies = project.get("dependencies")
    dependency_count = (
        len(
            [
                item
                for item in dependencies
                if isinstance(item, str)
            ]
        )
        if isinstance(dependencies, list)
        else 0
    )
    optionals = project.get("optional-dependencies")
    optional_groups = (
        sorted(str(key) for key in optionals)
        if isinstance(optionals, dict)
        else []
    )
    python_requires_range = None
    if isinstance(requires_python, str):
        clauses, _error = _parse_specifier(requires_python)
        if clauses:
            python_requires_range = _python_bounds(clauses)
    dynamic_raw = project.get("dynamic")
    dynamic_fields = (
        [str(item) for item in dynamic_raw if isinstance(item, str)]
        if isinstance(dynamic_raw, list)
        else []
    )
    return {
        "layout": "pep621",
        "name": name if isinstance(name, str) else None,
        "version": version if isinstance(version, str) else None,
        "requires_python": (
            requires_python if isinstance(requires_python, str) else None
        ),
        "dependency_count": dependency_count,
        "optional_groups": optional_groups,
        "python_requires_range": python_requires_range,
        "entry_points_count": _entry_points_count(project),
        "dynamic_fields": dynamic_fields,
        "note": (
            "python_requires_range compares release segments only "
            "and never judges satisfiability (VersionConstraintTool, "
            "#3995); dependency_count counts the string entries of "
            "dependencies; entry_points_count sums scripts, "
            "gui-scripts and every entry-points group; " + _NOTE_DIVISION
        ),
    }


def _poetry_entry_points_count(poetry: Dict[str, Any]) -> int:
    """Poetry plugins + scripts entry count (best-effort)."""
    count = 0
    scripts = poetry.get("scripts")
    if isinstance(scripts, dict):
        count += len(scripts)
    plugins = poetry.get("plugins")
    if isinstance(plugins, dict):
        for group in plugins.values():
            if isinstance(group, dict):
                count += len(group)
    return count


# ------------------------------------------------------------------ #
# The tool
# ------------------------------------------------------------------ #

class PyprojectLintTool(Tool):
    """Pyproject.toml project-metadata linting tool (pure stdlib).

    Attributes:
        max_lines (int): Upper bound on the line count of the
            pyproject.toml text.
        max_line_chars (int): Upper bound on any single line.
        max_text_chars (int): Upper bound on the whole text input.
        max_files (int): Upper bound on the available_files list.
        max_file_entry_chars (int): Upper bound on one file entry.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "pyproject_lint_tool"
    description: str = (
        "Pyproject.toml project-metadata linting tool — pure Python "
        "stdlib (tomllib), no network required. Lint the [project] "
        "table (PEP 621) into structured findings (mode='lint': "
        "missing/invalid name, missing or non-PEP 440 version, "
        "invalid requires-python clauses, PEP 639 deprecated license "
        "table form, dangling readme/license file references against "
        "a supplied file listing, authors/maintainers entry shapes "
        "and email syntax, keywords/classifiers/urls shapes, "
        "dependencies and optional-dependencies checked as loose "
        "PEP 508 strings with duplicate and overlap rules after PEP "
        "503 normalization, dynamic fields statically set (PEP 621 "
        "conflict), scripts/entry-points names and dotted targets, "
        "missing build-system — each info / warning / error; "
        "Poetry-style [tool.poetry] projects get documented "
        "best-effort mapping notes, never errors) and get the "
        "quick-look summary (mode='project_summary': name, version, "
        "requires-python with parsed min/max bounds, dependency "
        "count, optional groups, entry-points count, dynamic "
        "fields). TOML syntax/style is TomlLintTool's layer and "
        "requirements.txt is RequirementsTool's — this tool reads "
        "the parsed project metadata only."
    )

    MODES: ClassVar[tuple] = ("lint", "project_summary")

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        pyproject: Any = None,
        available_files: Any = None,
    ) -> Dict[str, Any]:
        """Run one pyproject-metadata operation.

        Args:
            mode (str): One of ``lint`` / ``project_summary``.
            pyproject (str): The pyproject.toml text.
            available_files (Optional[List[str]]): Project-root
                relative paths that exist (the caller's listing);
                enables the readme / license dangling checks. None
                disables them.

        Returns:
            Dict[str, Any]: The operation result — findings or the
                summary payload, with content-level problems (an
                unparseable file, a bad version) carried inside
                the payload instead of raising.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} "
                f"(got {mode!r})"
            )
        text = self._validate_text(pyproject, "pyproject")
        files = self._validate_files(available_files)

        try:
            doc = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            if mode == "project_summary":
                return {
                    "mode": mode,
                    "layout": "none",
                    "name": None,
                    "version": None,
                    "requires_python": None,
                    "dependency_count": 0,
                    "optional_groups": [],
                    "python_requires_range": None,
                    "entry_points_count": 0,
                    "dynamic_fields": [],
                    "note": (
                        f"the text is not parseable TOML "
                        f"({error}); a summary needs a parseable "
                        f"file — see the lint mode's "
                        f"toml_parse_error finding"
                    ),
                }
            return {
                "mode": mode,
                "findings": [
                    {
                        "code": "toml_parse_error",
                        "severity": "error",
                        "field": None,
                        "message": (
                            f"the text is not parseable TOML: {error} "
                            f"(syntax-level checking is TomlLintTool's "
                            f"layer, #4012; nothing else runs)"
                        ),
                    }
                ],
                "counts": {"findings": 1, "errors": 1, "warnings": 0, "infos": 0},
                "note": _NOTE_DIVISION,
            }

        if mode == "project_summary":
            return {"mode": mode, **_summarize_document(doc)}

        findings = _lint_document(doc, files)
        counts = {
            "findings": len(findings),
            "errors": sum(
                1 for finding in findings
                if finding["severity"] == "error"
            ),
            "warnings": sum(
                1 for finding in findings
                if finding["severity"] == "warning"
            ),
            "infos": sum(
                1 for finding in findings
                if finding["severity"] == "info"
            ),
        }
        note = (
            "readme / license existence checks require the "
            "available_files listing (None supplied — skipped); "
            "classifier_unknown is an info heuristic over the known "
            "trove roots; " + _NOTE_DIVISION
        )
        return {
            "mode": mode,
            "findings": findings,
            "counts": counts,
            "note": note,
        }

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"pyproject_lint_tool: {message}")

    @classmethod
    def _validate_text(cls, value: Any, name: str) -> str:
        """Validate a pyproject-text parameter (type and caps)."""
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
    def _validate_files(cls, value: Any) -> Optional[set]:
        """Validate the available_files listing; None passes."""
        if value is None:
            return None
        if isinstance(value, (str, bytes, bool)) or not isinstance(
            value, (list, tuple, set, frozenset)
        ):
            cls._invalid(
                f"available_files must be a list of path strings or "
                f"None (got {value!r})"
            )
        items = list(value)
        if len(items) > _MAX_FILES:
            cls._invalid(
                f"available_files exceeds the {_MAX_FILES:,}-entry "
                f"limit (got {len(items):,} entries)"
            )
        normalized: set = set()
        for item in items:
            if (
                isinstance(item, bool)
                or not isinstance(item, str)
                or not item.strip()
            ):
                cls._invalid(
                    f"every available_files entry must be a "
                    f"non-empty path string (got {item!r})"
                )
            if len(item) > _MAX_FILE_ENTRY_CHARS:
                cls._invalid(
                    f"the available_files entry {item[:32]!r}… "
                    f"exceeds the {_MAX_FILE_ENTRY_CHARS:,}-character "
                    f"limit"
                )
            normalized.add(_normalize_path(item))
        return normalized
