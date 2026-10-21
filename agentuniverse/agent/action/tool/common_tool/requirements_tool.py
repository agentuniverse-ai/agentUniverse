#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: requirements_tool.py

r"""Requirements.txt inspection and diffing tool, pure Python stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) at the **dependency-file layer**: the requirements.txt
file itself. Every Python project carries one; agents that bump
dependencies, review upgrade PRs or chase environment drift need to
answer file-shaped questions — "what exactly does this file pin,
and is each line well-formed?", "which lines are risky or
inconsistent with the rest of the file?" and "what changed between
the lock-style snapshot we had and the one we have now?" — none of
which is about *resolving* versions against each other.

Three modes, all offline and deterministic:

* ``parse`` — requirements.txt text into structured entries
  ``{raw, kind, name, name_raw, specifier, extras?, markers?,
  editable?, vcs?, url?, path?, hash?, comment?, line}`` (fields
  beyond the core carry ``kind`` — requirement / editable /
  direct_url / vcs / path — and the as-written spelling
  ``name_raw``). ``name`` is the PEP 503
  normalized form (lowercase, runs of ``-_.`` collapsed to a single
  ``-``); ``specifier`` / ``markers`` are kept **verbatim** (spaces,
  quoting style and clause order untouched — round-trippable);
  ``extras`` is the bracket list as written. Editable installs
  (``-e`` / ``--editable``) carry ``editable: true`` plus their
  ``path`` or ``url`` (VCS editables carry ``vcs``); direct URL
  lines (``https://…``, ``git+https://…#egg=…``, wheel / sdist
  links, PEP 508 ``name @ url`` direct references) carry ``url``
  and, when the scheme says so, ``vcs`` (git / hg / svn / bzr);
  ``--hash=algo:digest`` options are collected into ``hash``.
  Unparsable lines never fail the run: they are collected as
  structured ``errors`` with 1-based line numbers and a reason.
  Comments and blank lines are reported **distinctly** (a comment
  list and a blank-line count, never as entries or errors), and
  known pip requirements-file *options* (``-r`` / ``--requirement``,
  ``-c`` / ``--constraint``, ``-f`` / ``--find-links``,
  ``-i`` / ``--index-url``, ``--extra-index-url``, ``--trusted-host``,
  ``--no-binary``, ``--only-binary``, ``--no-index``, ``--pre``,
  ``--prefer-binary``, ``--require-hashes``) are captured in an
  ``options`` list instead of being mistaken for requirements.
* ``lint`` — quality findings over the parsed file, each with a
  ``code``, a ``severity`` (info / warning / error), the line and
  the offending ``raw`` text: ``non_pinned_no_specifier`` (a bare
  name — floating dependency, info), ``mixed_pin_styles`` (some
  entries pinned with ``==`` / ``===``, others ranged with ``>=`` /
  ``~=`` / ``<`` — an inconsistent file, warning, file-level),
  ``version_pinned_too_tightly`` (``==`` at patch level
  ``X.Y.Z`` — the classic library anti-pattern, info heuristic —
  apps legitimately pin exactly, libraries rarely should),
  ``editable_without_path`` (``-e`` target that is neither a path
  nor a URL — error), ``duplicate_names`` (two entries for the same
  package *after* PEP 503 normalization — ``foo_bar`` vs ``foo-bar``
  collide, warning), ``url_without_hash`` (a URL / VCS / direct-ref
  line without any ``--hash`` — supply-chain pinning, info),
  ``very_old_line_format`` (the ``distribute``-era shapes: the
  setuptools-predecessor ``distribute`` package itself, or legacy
  ``0.6c9``-style versions, info), ``case_inconsistent_names``
  (``Foo`` vs ``foo`` — same package spelled two ways, info) and
  ``mixed_relative_absolute_editable`` (an editable block mixing
  relative and absolute targets, warning, file-level).
* ``diff`` — two requirements texts (a "freeze drift" check: the
  output of ``pip freeze`` today vs. yesterday, or lockfile
  snapshots) into ``added`` / ``removed`` / ``changed`` plus
  counts. Entries are keyed by their normalized name (nameless
  path / URL lines fall back to their raw text); each ``changed``
  row carries ``name``, the full ``from`` / ``to`` entry summaries
  and the ``specifier_changed`` / ``marker_changed`` /
  ``extras_changed`` flags (plus ``other_changed`` for url / path /
  vcs / editable / hash moves). Duplicate names pair up
  positionally (first-with-first); the leftover tail lands in
  added / removed — deterministic and documented. Parse errors of
  either side pass through as ``errors_old`` / ``errors_new`` so a
  drift check never hides a malformed line.

Division of labor inside the family (see the Distinction section of
the PR): **EnvSchemaTool** (#4002) and **EnvLintTool** (#4017) work
on ``.env`` files; **VersionConstraintTool** (#3995) resolves
*semver range sets* in the abstract (npm-style ranges, candidates,
binding constraint, conflicts). This tool inspects the
**requirements.txt format itself** — PEP 508 requirement lines
(names, extras, environment markers, specifiers kept verbatim),
editable / VCS / direct-URL / path lines, hashes and pip options —
and diffs two files. Constraint *solving* is explicitly NOT done
here: the specifier grammar is validated loosely (each clause is
``op + version-token``; whether the clauses can be satisfied
together against a pool of versions is #3995's job), and markers
are validated for shape (non-empty, balanced parentheses and
quotes, a safe charset, at least one comparison) but never
*evaluated*.

Grammar notes (deliberate, documented choices):

* Comment handling mirrors pip: a comment starts at the first
  ``#`` that either begins the line or is preceded by whitespace —
  including one that would sit inside a quoted marker string, and
  including ``#egg=`` only when whitespace precedes it (URL
  fragments glued to the URL are preserved). A line whose content
  is empty after comment stripping is a *comment line*, not blank.
* The file is line-oriented: pip-style backslash line
  continuations are NOT joined — a line ending in ``\`` is
  reported as an error (``unsupported_line_continuation``).
  Multi-line requirements do not exist in this format's common
  practice; the choice keeps every line independently attributable.
* PEP 508 lines accept what ``packaging.requirements.Requirement``
  accepts where it matters for structure: whitespace around
  operators (``>= 2.0``), a trailing comma, empty extras brackets
  (``foo[]``), wildcard clauses (``==1.2.*``, ``!=1.2.*``),
  arbitrary-equality ``===anything`` and digit-leading names —
  while ``~=1`` (compatible release needs two release components)
  and a missing comma between clauses are errors, matching
  ``packaging``. A ``name @ url`` direct reference requires no
  scheme (``foo@1.0`` is accepted with ``url='1.0'``), matching
  ``packaging`` 23.x literally.
* Hash options may repeat and may carry comma-separated values
  (``--hash=sha256:a,sha256:b``); any other ``--``-token inside a
  requirement line is an error.

Input validation is strict and happens before any parsing: wrong
parameter types raise ``ValueError``; the text inputs are capped
at 10,000 lines, 10,000 characters per line and 4,000,000
characters total (the empty string is a valid empty file). All
output ordering is deterministic: entries, errors, comments and
options in file order; lint findings sorted by (line, code) with
file-level findings last; diff rows sorted by name.
"""

import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# ------------------------------------------------------------------ #
# Limits (reject pathological inputs before any work)
# ------------------------------------------------------------------ #

_MAX_LINES = 10_000
_MAX_LINE_CHARS = 10_000
_MAX_TEXT_CHARS = 4_000_000

# ------------------------------------------------------------------ #
# Grammar building blocks
# ------------------------------------------------------------------ #

# PEP 508 project name: starts and ends alnum, middle may use . _ -.
_NAME_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?")
# PEP 503 canonicalization: collapse runs of -_. to a single -, lower.
_NAME_COLLAPSE_RE = re.compile(r"[-_.]+")
# A URL scheme prefix (git+https, https, file, ssh, ...).
_SCHEME_RE = re.compile(r"^([A-Za-z][A-Za-z0-9+.-]*)://")
# Editable option forms: '-e <t>', '-e=<t>', '--editable <t>', '--editable=<t>'.
_EDITABLE_RE = re.compile(r"^(?:-e|--editable)(?:\s+|=)\s*(.*)$", re.S)
# PEP 508 direct reference: name[extras] @ url [; markers].
_DIRECT_REF_RE = re.compile(
    r"^\s*([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)"
    r"(\s*\[[^\]]*\])?"
    r"\s*@\s*(\S+)"
    r"(?:\s*;\s*(.+))?$"
)
# One specifier clause: operator + version token (a version starts
# with a letter or digit — '==1.0' fine, '>==1.0' and '== =1.0'
# rejected, matching packaging).
_CLAUSE_RE = re.compile(
    r"^\s*(===|==|!=|<=|>=|~=|<|>)\s*([0-9A-Za-z][^\s,;#]*)\s*$"
)
# Editable option prefix on a line (dispatch only).
_EDITABLE_PREFIX_RE = re.compile(r"^(?:-e|--editable)(?:\s+|=|$)")
# A --hash option token (may carry comma-separated values).
_HASH_TOKEN_RE = re.compile(r"^--hash=(.*)$", re.S)
# Loose hash value: algorithm ':' digest.
_HASH_VALUE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_+-]*:[0-9A-Fa-f]+$")
# Marker safety: letters, digits, comparisons, quotes, parens, space.
_MARKER_CHARS_RE = re.compile(r"^[A-Za-z0-9_.!<>~=\"'()\s-]+$")
# A marker must contain at least one comparison (or an `in` test).
_MARKER_OP_RE = re.compile(r"===|==|!=|<=|>=|<|>|~=")
# VCS schemes recognized in URLs (the '+https' / 'ssh' family).
_VCS_SCHEMES = ("git", "hg", "svn", "bzr")
# Leading release components of a version token (for the ~= rule).
_LEADING_RELEASE_RE = re.compile(r"^\d+(?:\.\d+)*")
# Legacy setuptools / distribute era version: 0.6c9, 0.6r1.
_LEGACY_VERSION_RE = re.compile(r"^\d+\.\d+[cr]\d+$")
# Egg fragment inside a URL: '#egg=name'.
_EGG_FRAGMENT_RE = re.compile(r"[#&]egg=([^&#\s]+)")
# Wheel filename: name-version-pytags.whl (PEP 427).
_WHEEL_NAME_RE = re.compile(
    r"^(?P<name>[^-]+)-(?P<version>[^-]+)-[^-]+-[^-]+-[^-]+\.whl$"
)
# Sdist filename: name-version.tar.gz / .zip / .tar.bz2 (best effort).
_SDIST_NAME_RE = re.compile(
    r"^(?P<name>.+)-(?P<version>\d[^-]*)"
    r"(?:\.tar\.gz|\.tar\.bz2|\.tgz|\.zip)$"
)

# pip requirements-file options recognized by the parser. Value
# options capture their argument; flag options stand alone.
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
    "--no-binary": "no-binary",
    "--only-binary": "only-binary",
}
_FLAG_OPTIONS: Dict[str, str] = {
    "--no-index": "no-index",
    "--pre": "pre",
    "--prefer-binary": "prefer-binary",
    "--require-hashes": "require-hashes",
}

# Lint severities per finding code.
_SEVERITIES: Dict[str, str] = {
    "non_pinned_no_specifier": "info",
    "mixed_pin_styles": "warning",
    "version_pinned_too_tightly": "info",
    "editable_without_path": "error",
    "duplicate_names": "warning",
    "url_without_hash": "info",
    "very_old_line_format": "info",
    "case_inconsistent_names": "info",
    "mixed_relative_absolute_editable": "warning",
}

_NOTE_DIVISION = (
    "the dependency-file layer: requirements.txt lines are parsed "
    "(PEP 508 name / extras / markers, editable, VCS, direct URL, "
    "path, hashes, options) and diffed; .env files are handled by "
    "EnvSchemaTool / EnvLintTool and abstract semver constraint-set "
    "resolution by VersionConstraintTool — specifiers here are kept "
    "verbatim and validated for shape only, never solved"
)


# ------------------------------------------------------------------ #
# Pure helpers
# ------------------------------------------------------------------ #

def _normalize_name(name: str) -> str:
    """PEP 503 normalization: lowercase, runs of -_. -> a single '-'."""
    return _NAME_COLLAPSE_RE.sub("-", name).lower()


def _split_comment(line: str) -> Tuple[str, Optional[str]]:
    """Split a line into (content, comment) the way pip does.

    A comment starts at the first ``#`` that begins the line or is
    preceded by whitespace; a ``#`` glued to a URL (``…#egg=x``)
    is part of the content. Returns the content and the comment
    text without the leading ``#`` (or ``None``).
    """
    for index, char in enumerate(line):
        if char == "#" and (index == 0 or line[index - 1] in " \t"):
            return line[:index], line[index + 1:].strip()
    return line, None


def _extract_hash_options(text: str) -> Tuple[str, List[str], Optional[str]]:
    """Pull ``--hash=algo:digest`` tokens out of a line body.

    Returns ``(remaining_text, hashes, error)`` — hash values may be
    comma-separated inside one option; any other ``--``-prefixed
    token (or a ``--hash`` without a value) is an error.
    """
    hashes: List[str] = []
    kept: List[str] = []
    for token in text.split():
        if not token.startswith("--"):
            kept.append(token)
            continue
        if token == "--hash":
            return text, [], "a --hash option carries no value"
        match = _HASH_TOKEN_RE.match(token)
        if match is None:
            return text, [], (
                f"unexpected option {token!r} inside a requirement "
                f"line (only --hash=<algo>:<digest> may follow a "
                f"requirement)"
            )
        values = [value for value in match.group(1).split(",") if value]
        if not values:
            return text, [], "a --hash option carries no value"
        for value in values:
            if not _HASH_VALUE_RE.match(value):
                return text, [], (
                    f"malformed hash value {value!r} — expected "
                    f"'<algorithm>:<hex digest>'"
                )
        hashes.extend(values)
    return " ".join(kept), hashes, None


def _vcs_of(url: str) -> Optional[str]:
    """The VCS behind a URL (git / hg / svn / bzr) or None."""
    match = _SCHEME_RE.match(url)
    if match is None:
        return None
    scheme = match.group(1)
    base = scheme.split("+", 1)[0]
    return base if base in _VCS_SCHEMES else None


def _name_from_url(url: str) -> Optional[str]:
    """Best-effort package name behind a URL line.

    Prefers the ``#egg=`` fragment (pip's convention for source
    trees), then the wheel filename grammar (PEP 427 — wheel file
    names replace ``-`` with ``_``, which normalization undoes),
    then a source-archive filename. ``None`` when nothing matches.
    """
    egg = _EGG_FRAGMENT_RE.search(url)
    if egg is not None:
        return _normalize_name(egg.group(1))
    last_segment = url.rstrip("/").rsplit("/", 1)[-1].split("#", 1)[0]
    wheel = _WHEEL_NAME_RE.match(last_segment)
    if wheel is not None:
        return _normalize_name(wheel.group("name"))
    sdist = _SDIST_NAME_RE.match(last_segment)
    if sdist is not None:
        return _normalize_name(sdist.group("name"))
    return None


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


def _validate_clauses(specifier: str) -> Optional[str]:
    """Loosely validate a comma-separated PEP 440 clause list.

    Each clause must be ``operator + version-token``; a trailing
    comma is tolerated; ``~=`` needs at least two release
    components (matching ``packaging``). Returns an error message
    or None. Exact satisfiability is NOT judged here (see
    VersionConstraintTool).
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
                f"expected '<op><version>' with op one of "
                f"== != <= >= ~= < > === and a version without "
                f"spaces, commas, ';' or '#'"
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

    Non-empty, balanced parentheses, and a charset limited to what
    marker grammar can contain. Markers are never evaluated here.
    """
    text = markers.strip()
    if not text:
        return "an environment marker after ';' must not be empty"
    if not _MARKER_CHARS_RE.match(text):
        return (
            f"the marker {text[:64]!r} uses characters outside the "
            f"marker grammar (allowed: letters, digits, comparison "
            f"operators, quotes, parentheses, spaces, '.', '_', '-', "
            f"'~', '=')"
        )
    if text.count("'") % 2 or text.count('"') % 2:
        return (
            f"the marker {text[:64]!r} leaves a quote unterminated"
        )
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


def _extras_list(bracketed: Optional[str]) -> Optional[List[str]]:
    """Parse a '[a, b]' extras bracket into a list (None if absent).

    An empty bracket yields an empty list (matching ``packaging``).
    """
    if bracketed is None:
        return None
    inner = bracketed.strip()[1:-1].strip()
    if not inner:
        return []
    return [part.strip() for part in inner.split(",")]


def _absolute_path(path: str) -> bool:
    """Whether an editable path target is absolute (vs relative)."""
    if path.startswith(("/", "~")) or path.startswith("\\\\"):
        return True
    head = path.split("/", 1)[0].split("\\", 1)[0]
    return len(head) == 2 and head[1] == ":" and head[0].isalpha()


def _summary_for_diff(entry: Dict[str, Any]) -> Dict[str, Any]:
    """The compact entry summary carried by diff from/to rows."""
    return {
        "line": entry["line"],
        "raw": entry["raw"],
        "specifier": entry.get("specifier"),
        "markers": entry.get("markers"),
        "extras": entry.get("extras"),
        "url": entry.get("url"),
        "path": entry.get("path"),
        "vcs": entry.get("vcs"),
        "editable": entry.get("editable", False),
        "hash": entry.get("hash"),
    }


# ------------------------------------------------------------------ #
# The parser (one pure function over the text)
# ------------------------------------------------------------------ #

def _parse_requirements(text: str) -> Dict[str, Any]:
    """Parse requirements.txt text into a structured document.

    Returns ``{counts, entries, errors, comments, options}`` —
    errors carry 1-based ``line`` numbers and a ``reason``; comment
    and blank lines are reported distinctly, never as entries.
    """
    entries: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    comments: List[Dict[str, Any]] = []
    options: List[Dict[str, Any]] = []
    blank_lines = 0

    lines = text.splitlines()
    for index, raw_line in enumerate(lines, start=1):
        raw = raw_line.rstrip("\r\n")
        content, comment = _split_comment(raw)
        stripped = content.strip()
        if comment is not None and not stripped:
            comments.append({"line": index, "raw": raw, "text": comment})
            continue
        if not stripped:
            blank_lines += 1
            continue
        if stripped.endswith("\\"):
            errors.append(
                {
                    "line": index,
                    "raw": raw,
                    "reason": (
                        "backslash line continuation is not supported "
                        "— this parser is line-oriented; join the "
                        "continuation manually"
                    ),
                }
            )
            continue

        if _EDITABLE_PREFIX_RE.match(stripped):
            entry, error = _parse_editable(stripped, raw, index)
        elif stripped.startswith("-"):
            entry, error = _parse_option(stripped, raw, index)
        else:
            entry, error = _parse_requirement(stripped, raw, index)

        if error is not None:
            errors.append({"line": index, "raw": raw, "reason": error})
            continue
        if entry is not None and entry.get("kind") == "option":
            options.append(entry)
            continue
        if entry is not None:
            if comment:
                entry["comment"] = comment
            entries.append(entry)

    return {
        "counts": {
            "total_lines": len(lines),
            "entries": len(entries),
            "errors": len(errors),
            "comments": len(comments),
            "blank_lines": blank_lines,
            "options": len(options),
        },
        "entries": entries,
        "errors": errors,
        "comments": comments,
        "options": options,
    }


def _parse_option(stripped: str, raw: str, line: int) -> Tuple[
    Optional[Dict[str, Any]], Optional[str]
]:
    """Parse a leading '-'-option line (editable handled earlier)."""
    token = stripped.split(None, 1)[0]
    # Long / short options may carry their value after '='
    # ('--requirement=more.txt'), pip's optparse behavior.
    inline_value: Optional[str] = None
    if "=" in token:
        token, inline_value = token.split("=", 1)
    trailing = stripped[len(stripped.split(None, 1)[0]):].strip()
    value = " ".join(
        part for part in (inline_value, trailing) if part
    ).strip() or None
    if token in _VALUE_OPTIONS:
        if not value:
            return None, (
                f"the option {token} requires a value (got the bare "
                f"option on the line)"
            )
        return (
            {
                "kind": "option",
                "line": line,
                "raw": raw,
                "option": token,
                "name": _VALUE_OPTIONS[token],
                "value": value,
            },
            None,
        )
    if token in _FLAG_OPTIONS:
        return (
            {
                "kind": "option",
                "line": line,
                "raw": raw,
                "option": token,
                "name": _FLAG_OPTIONS[token],
                "value": None,
            },
            None,
        )
    return None, (
        f"unknown requirements-file option {token!r} (recognized: "
        f"-e/--editable, {', '.join(sorted(_VALUE_OPTIONS))}, "
        f"{', '.join(sorted(_FLAG_OPTIONS))})"
    )


def _parse_editable(stripped: str, raw: str, line: int) -> Tuple[
    Optional[Dict[str, Any]], Optional[str]
]:
    """Parse an editable install line (``-e`` / ``--editable``)."""
    match = _EDITABLE_RE.match(stripped)
    # A bare '-e' / '--editable' is still recorded as an editable
    # entry without a target — the lint rule editable_without_path
    # reports it (the line shape IS recognizable, just unusable).
    target = match.group(1).strip() if match is not None else ""
    entry: Dict[str, Any] = {
        "kind": "editable",
        "line": line,
        "raw": raw,
        "name": None,
        "specifier": None,
        "editable": True,
    }
    if not target:
        # Recorded as-is; the lint rule editable_without_path flags
        # it as an error (the line IS recognizable, just unusable).
        return entry, None
    target, hashes, hash_error = _extract_hash_options(target)
    if hash_error is not None:
        return None, hash_error
    if hashes:
        entry["hash"] = hashes
    if not target:
        entry["path"] = None
        return entry, None

    direct = _DIRECT_REF_RE.match(target)
    if direct is not None:
        name_raw, extras_raw, url, markers = direct.groups()
        entry["name"] = _normalize_name(name_raw)
        entry["name_raw"] = name_raw
        entry["url"] = url
        vcs = _vcs_of(url)
        if vcs:
            entry["vcs"] = vcs
        extras = _extras_list(extras_raw)
        if extras is not None:
            entry["extras"] = extras
        if markers is not None:
            marker_error = _validate_markers(markers)
            if marker_error is not None:
                return None, marker_error
            entry["markers"] = markers.strip()
        return entry, None

    if _SCHEME_RE.match(target):
        entry["url"] = target
        vcs = _vcs_of(target)
        if vcs:
            entry["vcs"] = vcs
        entry["name"] = _name_from_url(target)
        return entry, None

    if _is_pathish(target):
        entry["path"] = target
        return entry, None

    # A bare token: editable needs a project path or URL — the lint
    # rule editable_without_path reports it (error severity).
    entry["path"] = None
    if _NAME_RE.fullmatch(target):
        entry["name"] = _normalize_name(target)
        entry["name_raw"] = target
    return entry, None


def _parse_requirement(stripped: str, raw: str, line: int) -> Tuple[
    Optional[Dict[str, Any]], Optional[str]
]:
    """Parse a non-option requirement line.

    Dispatch: PEP 508 direct reference (``name @ url``) → bare URL
    (scheme) → local path → standard ``name[extras] spec ; markers``.
    """
    direct = _DIRECT_REF_RE.match(stripped)
    if direct is not None:
        name_raw, extras_raw, url, markers = direct.groups()
        entry: Dict[str, Any] = {
            "kind": "direct_url",
            "line": line,
            "raw": raw,
            "name": _normalize_name(name_raw),
            "name_raw": name_raw,
            "specifier": None,
            "url": url,
        }
        vcs = _vcs_of(url)
        if vcs:
            entry["vcs"] = vcs
        extras = _extras_list(extras_raw)
        if extras is not None:
            entry["extras"] = extras
        if markers is not None:
            marker_error = _validate_markers(markers)
            if marker_error is not None:
                return None, marker_error
            entry["markers"] = markers.strip()
        return entry, None

    if _SCHEME_RE.match(stripped):
        url, hashes, hash_error = _extract_hash_options(stripped)
        if hash_error is not None:
            return None, hash_error
        if " " in url:
            return None, (
                f"a URL requirement must be a single token — found "
                f"extra text after {url.split()[0]!r}"
            )
        entry = {
            "kind": "vcs" if _vcs_of(url) else "direct_url",
            "line": line,
            "raw": raw,
            "name": _name_from_url(url),
            "specifier": None,
            "url": url,
        }
        vcs = _vcs_of(url)
        if vcs:
            entry["vcs"] = vcs
        if hashes:
            entry["hash"] = hashes
        return entry, None

    if _is_pathish(stripped):
        path, hashes, hash_error = _extract_hash_options(stripped)
        if hash_error is not None:
            return None, hash_error
        return (
            {
                "kind": "path",
                "line": line,
                "raw": raw,
                "name": None,
                "specifier": None,
                "path": path,
            },
            None,
        )

    # Standard PEP 508: name[extras] specifier ; markers
    name_match = _NAME_RE.match(stripped)
    if name_match is None or name_match.start() != 0:
        return None, (
            f"expected a PEP 508 package name, a URL, a path or an "
            f"option at line start — got {stripped[:64]!r}"
        )
    name_raw = name_match.group(0)
    rest = stripped[name_match.end():].lstrip()

    extras_raw: Optional[str] = None
    if rest.startswith("["):
        close = rest.find("]")
        if close < 0:
            return None, (
                f"the extras bracket of {name_raw!r} is never closed"
            )
        extras_raw = rest[: close + 1]
        rest = rest[close + 1:].lstrip()

    if rest.startswith("@"):
        return None, (
            f"the direct reference {name_raw + ' @ ' + rest[1:].strip()!r} "
            f"is malformed — a valid form is 'name @ <url>' with the "
            f"URL free of spaces"
        )

    body, semicolon, marker_part = rest.partition(";")
    specifier = body.strip()
    if semicolon:
        marker_error = _validate_markers(marker_part)
        if marker_error is not None:
            return None, marker_error

    specifier, hashes, hash_error = _extract_hash_options(specifier)
    if hash_error is not None:
        return None, hash_error
    if specifier:
        clause_error = _validate_clauses(specifier)
        if clause_error is not None:
            return None, clause_error

    entry = {
        "kind": "requirement",
        "line": line,
        "raw": raw,
        "name": _normalize_name(name_raw),
        "name_raw": name_raw,
        "specifier": specifier if specifier else None,
    }
    extras = _extras_list(extras_raw)
    if extras is not None:
        entry["extras"] = extras
    if semicolon:
        entry["markers"] = marker_part.strip()
    if hashes:
        entry["hash"] = hashes
    return entry, None


# ------------------------------------------------------------------ #
# The linter (pure function over the parsed document)
# ------------------------------------------------------------------ #

def _lint_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """Run every lint rule over a parsed requirements document."""
    entries = document["entries"]
    findings: List[Dict[str, Any]] = []

    def add(code: str, detail: str, line: Optional[int] = None,
            raw: Optional[str] = None, name: Optional[str] = None,
            lines: Optional[List[int]] = None) -> None:
        finding: Dict[str, Any] = {
            "code": code,
            "severity": _SEVERITIES[code],
            "detail": detail,
        }
        if line is not None:
            finding["line"] = line
        if lines is not None:
            finding["lines"] = lines
        if raw is not None:
            finding["raw"] = raw
        if name is not None:
            finding["name"] = name
        findings.append(finding)

    # ---- per-entry rules ------------------------------------------ #
    named = [e for e in entries if e.get("name")]
    for entry in entries:
        raw, name = entry["raw"], entry.get("name")

        if (
            entry.get("kind") == "requirement"
            and entry.get("name")
            and not entry.get("specifier")
        ):
            add(
                "non_pinned_no_specifier",
                "a bare package name — installs whatever the index "
                "serves today (a floating dependency)",
                line=entry["line"], raw=raw, name=name,
            )

        specifier = entry.get("specifier")
        if specifier:
            for clause in specifier.split(","):
                clause = clause.strip()
                if clause.startswith("=="):
                    version = clause[2:].strip()
                    release = _LEADING_RELEASE_RE.match(version)
                    if release is not None and len(
                        release.group(0).split(".")
                    ) >= 3:
                        add(
                            "version_pinned_too_tightly",
                            f"patch-level pin '=={version}' — exact "
                            f"patch pins are usually too tight for "
                            f"libraries (heuristic: applications pin "
                            f"exactly on purpose)",
                            line=entry["line"], raw=raw, name=name,
                        )
                    break

        if name == "distribute":
            add(
                "very_old_line_format",
                "'distribute' is the setuptools predecessor package, "
                "unmaintained since 2013",
                line=entry["line"], raw=raw, name=name,
            )
        elif specifier:
            for clause in specifier.split(","):
                version = re.sub(
                    r"^(===|==|!=|<=|>=|~=|<|>)\s*", "", clause.strip()
                )
                if _LEGACY_VERSION_RE.match(version):
                    add(
                        "very_old_line_format",
                        f"the {version!r} version uses the legacy "
                        f"setuptools/distribute '0.6c9' scheme",
                        line=entry["line"], raw=raw, name=name,
                    )
                    break

        if entry.get("editable") and not entry.get("path") and not (
            entry.get("url")
        ):
            add(
                "editable_without_path",
                "the editable target is neither a path nor a URL — "
                "pip would reject this install",
                line=entry["line"], raw=raw, name=name,
            )

        if (
            entry.get("url") or entry.get("vcs")
        ) and not entry.get("hash"):
            add(
                "url_without_hash",
                "a URL / VCS requirement without --hash — the "
                "content at the URL can change silently",
                line=entry["line"], raw=raw, name=name,
            )

    # ---- file-level rules ----------------------------------------- #
    exact = [
        e for e in entries
        if e.get("specifier") and re.search(
            r"(?:^|,)\s*(?:={2,3})", e["specifier"]
        )
    ]
    ranged = [
        e for e in entries
        if e.get("specifier") and re.search(
            r"(?:^|,)\s*(?:~=|>=|<=|<|>)", e["specifier"]
        )
    ]
    if exact and ranged:
        add(
            "mixed_pin_styles",
            f"{len(exact)} entr{'y' if len(exact) == 1 else 'ies'} "
            f"pin exactly (== / ===) while {len(ranged)} use ranges "
            f"(>= / ~= / < …) — pick one style per file (exact pins "
            f"on lines "
            f"{[e['line'] for e in exact]}, ranges on lines "
            f"{[e['line'] for e in ranged]})",
        )

    edit_paths = [e for e in entries if e.get("editable") and e.get("path")]
    relative = [e for e in edit_paths if not _absolute_path(e["path"])]
    absolute = [e for e in edit_paths if _absolute_path(e["path"])]
    if relative and absolute:
        add(
            "mixed_relative_absolute_editable",
            f"editable targets mix relative (lines "
            f"{[e['line'] for e in relative]}) and absolute (lines "
            f"{[e['line'] for e in absolute]}) paths — the file "
            f"breaks when moved",
        )

    # ---- name-grouped rules --------------------------------------- #
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for entry in named:
        groups.setdefault(entry["name"], []).append(entry)
    for name in sorted(groups):
        group = groups[name]
        if len(group) > 1:
            add(
                "duplicate_names",
                f"'{name}' is required {len(group)} times (lines "
                f"{[e['line'] for e in group]}) — the last install "
                f"wins",
                name=name, lines=[e["line"] for e in group],
            )
        spellings = {e.get("name_raw") or "" for e in group}
        lowered = {s.lower() for s in spellings}
        if len(spellings) > 1 and len(lowered) == 1:
            add(
                "case_inconsistent_names",
                f"'{name}' is spelled {sorted(spellings)!r} — "
                f"differing only in case",
                name=name, lines=[e["line"] for e in group],
            )

    # Deterministic order: per-line findings by (line, code), then
    # the file-level findings (no line) last, stably by code.
    per_line = sorted(
        [f for f in findings if "line" in f],
        key=lambda f: (f["line"], f["code"]),
    )
    file_level = sorted(
        [f for f in findings if "line" not in f],
        key=lambda f: f["code"],
    )
    ordered = per_line + file_level
    counts = {
        "total": len(ordered),
        "info": sum(1 for f in ordered if f["severity"] == "info"),
        "warning": sum(1 for f in ordered if f["severity"] == "warning"),
        "error": sum(1 for f in ordered if f["severity"] == "error"),
    }
    return {"findings": ordered, "finding_counts": counts}


# ------------------------------------------------------------------ #
# The differ (pure function over two parsed documents)
# ------------------------------------------------------------------ #

def _diff_documents(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """Diff two parsed requirements documents (freeze-drift view)."""
    added: List[Dict[str, Any]] = []
    removed: List[Dict[str, Any]] = []
    changed: List[Dict[str, Any]] = []
    unchanged = 0

    def key_of(entry: Dict[str, Any]) -> str:
        if entry.get("name"):
            return entry["name"]
        return "\x00unnamed\x00" + entry["raw"]

    groups_old: Dict[str, List[Dict[str, Any]]] = {}
    for entry in old["entries"]:
        groups_old.setdefault(key_of(entry), []).append(entry)
    groups_new: Dict[str, List[Dict[str, Any]]] = {}
    for entry in new["entries"]:
        groups_new.setdefault(key_of(entry), []).append(entry)

    for key in sorted(set(groups_old) | set(groups_new)):
        olds, news = groups_old.get(key, []), groups_new.get(key, [])
        for old_entry, new_entry in zip(olds, news):
            before = _summary_for_diff(old_entry)
            after = _summary_for_diff(new_entry)
            specifier_changed = before["specifier"] != after["specifier"]
            marker_changed = before["markers"] != after["markers"]
            extras_changed = (
                sorted(map(str.lower, before["extras"] or []))
                != sorted(map(str.lower, after["extras"] or []))
            )
            other_changed = (
                before["url"] != after["url"]
                or before["path"] != after["path"]
                or before["vcs"] != after["vcs"]
                or before["editable"] != after["editable"]
                or before["hash"] != after["hash"]
            )
            if (
                specifier_changed or marker_changed or extras_changed
                or other_changed
            ):
                changed.append(
                    {
                        "name": key,
                        "from": before,
                        "to": after,
                        "specifier_changed": specifier_changed,
                        "marker_changed": marker_changed,
                        "extras_changed": extras_changed,
                        "other_changed": other_changed,
                    }
                )
            else:
                unchanged += 1
        for leftover in olds[len(news):]:
            removed.append(
                {"name": key, "raw": leftover["raw"], "line": leftover["line"]}
            )
        for leftover in news[len(olds):]:
            added.append(
                {"name": key, "raw": leftover["raw"], "line": leftover["line"]}
            )

    return {
        "counts": {
            "total_old": old["counts"]["entries"],
            "total_new": new["counts"]["entries"],
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "unchanged": unchanged,
        },
        "added": added,
        "removed": removed,
        "changed": changed,
        "errors_old": old["errors"],
        "errors_new": new["errors"],
    }


# ------------------------------------------------------------------ #
# The tool
# ------------------------------------------------------------------ #

class RequirementsTool(Tool):
    """Requirements.txt inspection and diffing tool (pure stdlib).

    Attributes:
        max_lines (int): Upper bound on the line count of any
            requirements text.
        max_line_chars (int): Upper bound on any single line.
        max_text_chars (int): Upper bound on a whole text input.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "requirements_tool"
    description: str = (
        "Requirements.txt inspection and diffing tool — pure Python "
        "stdlib, no network required. Parse a requirements.txt into "
        "structured entries (mode='parse': per-line raw text, PEP 503 "
        "normalized name, verbatim specifier / environment markers, "
        "extras, editable / VCS / direct-URL / path lines, --hash "
        "options; unparsable lines become errors with line numbers, "
        "comments and blank lines are reported distinctly and pip "
        "file options like -r / -i / -f are captured as options), "
        "lint the file for dependency hygiene (mode='lint': floating "
        "bare names, mixed == vs >= pin styles, patch-level exact "
        "pins, editables without a path, duplicate names after PEP "
        "503 normalization, URLs without hashes, distribute-era "
        "legacy lines, case-inconsistent spellings, mixed "
        "relative/absolute editables — each info / warning / error) "
        "and diff two snapshots freeze-drift style (mode='diff': "
        "added / removed / changed with specifier / marker / extras "
        "change flags). Constraint-set resolution is NOT done here — "
        "specifiers are validated for shape only (see "
        "VersionConstraintTool)."
    )

    MODES: ClassVar[tuple] = ("parse", "lint", "diff")

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        requirements: Any = None,
        requirements_old: Any = None,
        requirements_new: Any = None,
    ) -> Dict[str, Any]:
        """Run one requirements-file operation.

        Args:
            mode (str): One of ``parse`` / ``lint`` / ``diff``.
            requirements (str): The requirements.txt text for the
                ``parse`` and ``lint`` modes (an empty string is a
                valid empty file).
            requirements_old (str): The old snapshot for ``diff``.
            requirements_new (str): The new snapshot for ``diff``.

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
        if mode == "diff":
            return self._run_diff(requirements_old, requirements_new)
        return self._run_single(mode, requirements)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"requirements_tool: {message}")

    @classmethod
    def _validate_text(cls, value: Any, name: str) -> str:
        """Validate a requirements-text parameter (type and caps)."""
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

    # ------------------------------------------------------------------ #
    # parse / lint modes
    # ------------------------------------------------------------------ #

    def _run_single(
        self, mode: str, requirements: Any
    ) -> Dict[str, Any]:
        """Shared driver for the single-file modes."""
        self._validate_text(requirements, "requirements")
        document = _parse_requirements(requirements)
        result: Dict[str, Any] = {
            "mode": mode,
            "counts": document["counts"],
            "errors": document["errors"],
            "comments": document["comments"],
            "options": document["options"],
        }
        if mode == "parse":
            result["entries"] = document["entries"]
            result["note"] = _NOTE_DIVISION
            return result
        lint = _lint_document(document)
        result.update(lint)
        result["note"] = (
            "version_pinned_too_tightly is an info heuristic — exact "
            "patch pins are intentional for applications; the "
            "duplicate / case rules key on the PEP 503 normalized "
            "name; " + _NOTE_DIVISION
        )
        return result

    # ------------------------------------------------------------------ #
    # diff mode
    # ------------------------------------------------------------------ #

    def _run_diff(
        self, requirements_old: Any, requirements_new: Any
    ) -> Dict[str, Any]:
        """The freeze-drift mode: diff two requirements snapshots."""
        old_text = self._validate_text(requirements_old, "requirements_old")
        new_text = self._validate_text(requirements_new, "requirements_new")
        old = _parse_requirements(old_text)
        new = _parse_requirements(new_text)
        diff = _diff_documents(old, new)
        return {
            "mode": "diff",
            **diff,
            "note": (
                "entries are keyed by the PEP 503 normalized name "
                "(nameless path / URL lines by their raw text); "
                "duplicated names pair first-with-first and the tail "
                "lands in added / removed; parse errors of either "
                "side pass through as errors_old / errors_new so a "
                "drift check never hides a malformed line"
            ),
        }
