#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: cfg_lint_tool.py

"""INI / configuration (``.cfg`` / ``.ini``) *file linting* tool built
purely on the stdlib ``configparser`` semantics.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the quality layer for INI-style configuration
files — the still-unclaimed INI format niche next to the sibling
format linters (TomlLintTool #4012, YamlLintTool #4013, JsonLintTool
#4018, EnvLintTool #4017). The ground truth for every *syntax*
verdict is the standard library itself: the internal scanner is a
faithful line-mode port of ``configparser.ConfigParser._read`` with
its default settings (``strict=True``, ``=`` and ``:`` delimiters,
``#`` and ``;`` full-line comment prefixes, inline comment prefixes
``None``, option names lowercased via ``optionxform``, sections
case-sensitive, ``[DEFAULT]`` special, continuation lines indented
deeper than their option line). The lint result carries an explicit
``configparser_would_reject`` verdict, and the unit tests verify it
differentially against a real ``configparser.ConfigParser().read_string``
call over a generated corpus of 300+ INI texts.

Three modes, all offline and deterministic:

* ``lint`` — analyze INI text and report findings as
  ``[{line, code, message, severity}]`` sorted by ``(line, code)``:

  - Syntax errors (severity ``error``), each mirroring an exception
    the default strict ``configparser`` raises — the tool *reports*
    them, it never crashes on them:
    ``missing_section_header`` (a non-blank, non-comment, non-header
    line before the first section — exactly where
    ``MissingSectionHeaderError`` fires), ``duplicate_section``
    (same exact-case section header twice, ``DuplicateSectionError``),
    ``duplicate_option`` (same lowercased key twice in one section,
    ``DuplicateOptionError`` — this also covers case-spelling
    collisions such as ``Key`` / ``key`` because ``configparser``
    lowercases keys by default), ``key_without_value`` (an
    in-section line without any ``=`` / ``:`` delimiter — a bare key
    such as ``timeout`` — collected by ``ParsingError``) and
    ``unparseable_line`` (an in-section line whose option name is
    empty, e.g. ``= value`` — also a ``ParsingError``).
  - Correctness / portability risks (severity ``warning``):
    ``duplicate_option_case`` (the exact-case spellings differ while
    the lowercased forms collide — the extra nuance on top of
    ``duplicate_option``), ``duplicate_default_section`` (a repeated
    ``[DEFAULT]`` block — ``configparser`` tolerates the block
    itself and only fails later on repeated options inside it, so
    this is a warning, not an error), ``bom_present`` (a UTF-8 BOM:
    ``configparser`` then raises ``MissingSectionHeaderError`` at
    line 1 because the BOM character prefixes the first line and
    breaks the ``[section]`` match — the lint reports both
    ``bom_present`` and the mirrored ``missing_section_header`` at
    line 1, faithful to the oracle), ``inline_comment_risk`` (a
    ``;`` or ``#`` inside an option *value* — the default
    ``inline_comment_prefixes=None`` keeps it as data, but parsers
    configured with inline comment prefixes — or other INI dialects
    — would truncate the value) and ``interpolation_risk`` (the
    value contains a ``%`` pattern that the default
    ``BasicInterpolation`` would trip over at ``get()`` time:
    ``%(name)s`` referencing a name resolvable neither in the
    section nor in ``[DEFAULT]``, a bare ``%`` not followed by
    ``%`` or ``(``, a ``%( ... `` token without a ``)s``
    terminator, or — mirroring ``_interpolate_some``'s recursion —
    a reference chain that is cyclic or nested deeper than
    ``MAX_INTERPOLATION_DEPTH`` (10) or that reaches another option
    whose own value fails; ``read_string`` itself accepts all of
    these, access raises ``InterpolationMissingOptionError`` /
    ``InterpolationSyntaxError`` / ``InterpolationDepthError``).
  - Style (severity ``info``): ``missing_final_newline``,
    ``trailing_whitespace`` (whitespace before the line terminator;
    a lone ``\\r`` left by a CRLF terminator is not counted as
    trailing whitespace), ``tab_indentation`` (a tab inside the
    leading indentation — accepted by ``configparser`` but fragile
    in editors that expand tabs).

  Line-number citations mirror ``configparser`` itself.
  ``missing_section_header`` cites the physical line of the first
  non-blank, non-comment line — configparser's own 1-based physical
  counting, *not* zero-based content counting: with a one-line
  comment preamble above a section-less key, the citation is one
  line later than the "content line" users expect (the documented
  ``line N+1`` behavior of ``MissingSectionHeaderError``); with a
  BOM-only first line the citation pins line 1 even when the
  section header sits visibly on line 2. ``duplicate_section`` /
  ``duplicate_option`` cite the *repeated* header / key, exactly
  like the exceptions' ``[line N]`` fields, and the two
  ``ParsingError`` codes cite the bogus lines the exception would
  collect.

* ``parse`` — a structured, deterministic parse report built by the
  same line-mode scan, *even when configparser would reject the
  text* (the scanner records problems instead of raising, and
  re-enters duplicated sections to keep reporting): payload carries
  ``sections`` (``{name: {keys: [original spellings in
  first-appearance order], values: {lowercased key: value}
  (multiline continuation values joined with newlines, last
  occurrence wins for repeated keys, mirroring non-strict
  configparser), duplicate_keys: [{key, lines}], raw_lines: sorted
  physical line numbers of the section's header / option /
  continuation lines}}``, ``comments`` (full-line ``#`` / ``;``
  comments as ``[{line, text}]``), ``section_order`` (first
  appearance order) and ``total_lines``. Secret masking (family
  rule, same as EnvLintTool / EnvFileTool): a key whose name
  contains ``KEY``, ``SECRET``, ``PASSWORD`` or ``TOKEN``
  (case-insensitive substring) never has its value echoed — parse
  output renders it as ``***``. Finding *messages* never contain
  values at all, only section / key names and line numbers — and for
  a secret-ish key even the interpolation reference token inside its
  value is masked out of the message.

* ``check`` — evaluate named policy options against the text and
  return a pass / fail summary: ``require_section_header`` (default
  true), ``require_parseable`` (default true — no ``key_without_value``
  / ``unparseable_line``), ``require_unique_sections`` (default
  true — includes a repeated ``[DEFAULT]``), ``require_unique_options``
  (default true), ``require_final_newline`` (default false),
  ``forbid_inline_comments`` (default false), ``forbid_tabs``
  (default false) and ``forbid_bom`` (default false). Each check
  reports ``{name, ok, codes, violations}`` with sorted unique
  violation lines; the summary is ``pass`` only when every enabled
  check passes; check order is fixed by the declaration order.

Malformed *parameters* (unknown mode, non-string text, oversized
input, unknown / non-boolean check option) raise a ``ValueError``
before any computation. The tool never touches the filesystem or
the network.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# --------------------------------------------------------------------- #
# configparser ground-truth regexes (verbatim from the stdlib defaults)
# --------------------------------------------------------------------- #

_SECTCRE = re.compile(r"\[(?P<header>.+)\]")
_OPTCRE = re.compile(r"(?P<option>.*?)\s*(?P<vi>=|:)\s*(?P<value>.*)$")
_NONSPACECRE = re.compile(r"\S")

# Comment prefixes of the default configparser.
_COMMENT_PREFIXES = ("#", ";")

# Default section name (case-sensitive comparison, as in configparser).
_DEFAULT_SECTION = "DEFAULT"

# Name substrings marking a key as secret-ish (case-insensitive).
_SECRET_MARKERS = ("KEY", "SECRET", "PASSWORD", "TOKEN")

_MASK = "***"
_MAX_TEXT_CHARS = 100_000

# BasicInterpolation's interpolation-token regex (verbatim stdlib
# _KEYCRE semantics: %\( then one or more non-')' chars then \)s).
_INTERPVAR_CRE = re.compile(r"%\(([^)]+)\)s")

# configparser.MAX_INTERPOLATION_DEPTH — BasicInterpolation raises
# InterpolationDepthError above this reference nesting depth.
_MAX_INTERPOLATION_DEPTH = 10

# Valid policy options for check mode, in fixed (declaration) order,
# with their defaults and the lint codes they police.
_CHECK_OPTIONS: tuple[tuple[str, bool, tuple[str, ...]], ...] = (
    ("require_section_header", True, ("missing_section_header",)),
    ("require_parseable", True, ("key_without_value", "unparseable_line")),
    ("require_unique_sections", True, ("duplicate_section", "duplicate_default_section")),
    ("require_unique_options", True, ("duplicate_option",)),
    ("require_final_newline", False, ("missing_final_newline",)),
    ("forbid_inline_comments", False, ("inline_comment_risk",)),
    ("forbid_tabs", False, ("tab_indentation",)),
    ("forbid_bom", False, ("bom_present",)),
)

# --------------------------------------------------------------------- #
# lint rule registry: code -> severity (single source of truth)
# --------------------------------------------------------------------- #

SEVERITIES = {
    # syntax errors — mirror the default strict configparser's raises
    "missing_section_header": "error",
    "duplicate_section": "error",
    "duplicate_option": "error",
    "key_without_value": "error",
    "unparseable_line": "error",
    # correctness / portability risks
    "duplicate_option_case": "warning",
    "duplicate_default_section": "warning",
    "bom_present": "warning",
    "inline_comment_risk": "warning",
    "interpolation_risk": "warning",
    # style
    "missing_final_newline": "info",
    "trailing_whitespace": "info",
    "tab_indentation": "info",
}

RULES = tuple(sorted(SEVERITIES))

# Codes whose presence means the default strict configparser would
# raise while reading the text (the differential oracle contract).
_MIRROR_ERROR_CODES = (
    "missing_section_header",
    "duplicate_section",
    "duplicate_option",
    "key_without_value",
    "unparseable_line",
)


class CfgLintTool(Tool):
    """INI configuration linting tool mirroring stdlib ``configparser``.

    Attributes:
        max_text_chars (int): Upper bound on the INI text input;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    name: str = "cfg_lint_tool"
    description: str = (
        "Cfg lint tool — lint INI configuration text with the Python "
        "stdlib configparser semantics as ground truth, purely offline, "
        "no network required. lint mode reports findings "
        "[{code, severity, line, message}] from 13 deterministic rules "
        "(missing section header, duplicate sections, duplicate options "
        "including case collisions, keys without values, unparseable "
        "lines, repeated DEFAULT blocks, BOM, inline-comment and "
        "interpolation portability risks, missing final newline, "
        "trailing whitespace, tab indentation) plus an explicit "
        "configparser_would_reject verdict (mode='lint'); parse returns "
        "a structured section/key/comment report built by the same "
        "line-mode scan even when configparser would reject the text "
        "(mode='parse'); check evaluates named policy options "
        "(require_section_header, require_parseable, "
        "require_unique_sections, require_unique_options, "
        "require_final_newline, forbid_inline_comments, forbid_tabs, "
        "forbid_bom) into a pass/fail summary (mode='check'). Values of "
        "secret-ish keys (KEY/SECRET/PASSWORD/TOKEN) are never echoed "
        "in full."
    )

    MODES: ClassVar[tuple] = ("lint", "parse", "check")

    max_text_chars: int = _MAX_TEXT_CHARS

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        options: Any = None,
    ) -> dict[str, Any]:
        """Run one INI lint/parse/check operation.

        Args:
            mode (str): One of ``lint`` / ``parse`` / ``check``.
            text (str): The INI text (required for every mode; may be
                empty — an empty file lints clean).
            options (dict): ``check`` mode only — a dict of policy
                option name -> bool; omitted options take their
                documented defaults.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string plus the mode-specific fields).

        Raises:
            ValueError: If a parameter is malformed (raised before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})")
        clean_text = self._validate_text(text)
        check_flags = None
        if mode == "check":
            check_flags = self._validate_options(options)
        scan = self._scan(clean_text)
        if mode == "lint":
            return self._run_lint(scan)
        if mode == "parse":
            return self._run_parse(scan)
        return self._run_check(scan, check_flags)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"cfg_lint_tool: {message}")

    def _validate_text(self, text: Any) -> str:
        """Validate the INI text input (may be empty, must be str)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            self._invalid(f"text must be a string (got {text!r})")
        if len(text) > self.max_text_chars:
            self._invalid(
                f"text exceeds the {self.max_text_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_options(cls, options: Any) -> dict[str, bool]:
        """Validate check-mode policy options against the registry."""
        if options is None:
            return {name: default for name, default, _ in _CHECK_OPTIONS}
        if isinstance(options, bool) or not isinstance(options, dict):
            cls._invalid(f"options must be a dict of {{name: bool}} (got {options!r})")
        known = {name for name, _, _ in _CHECK_OPTIONS}
        flags: dict[str, bool] = {}
        for key, value in options.items():
            if not isinstance(key, str) or key not in known:
                cls._invalid(
                    f"unknown check option {key!r}; valid options: "
                    f"{', '.join(sorted(known))}"
                )
            if isinstance(value, bool) is False:
                cls._invalid(f"check option {key!r} must be a boolean (got {value!r})")
            flags[key] = value
        for name, default, _ in _CHECK_OPTIONS:
            flags.setdefault(name, default)
        return flags

    # ------------------------------------------------------------------ #
    # Core: faithful line-mode port of configparser._read (defaults)
    # ------------------------------------------------------------------ #

    @classmethod
    def _split_lines(cls, text: str) -> list[str]:
        """Split exactly like iterating the string through StringIO.

        Lines split on ``\\n`` only (a lone ``\\r`` stays inside the
        line, matching ``io.StringIO`` iteration); a trailing newline
        is a terminator, not an extra empty line; empty text has no
        lines at all.
        """
        if text == "":
            return []
        lines = text.split("\n")
        if text.endswith("\n"):
            lines.pop()
        return lines

    @classmethod
    def _scan(cls, text: str) -> dict[str, Any]:
        """Scan INI text with configparser's default state machine.

        Records every condition the default strict ``configparser``
        would raise (plus the risk / style conditions) *without ever
        raising itself*, and builds the structured section / key /
        comment report used by all three modes.
        """
        lines = cls._split_lines(text)
        findings: list[dict[str, Any]] = []

        def flag(code: str, line: int, message: str) -> None:
            findings.append(
                {"line": line, "code": code, "message": message, "severity": SEVERITIES[code]}
            )

        # --- whole-text conditions ----------------------------------- #
        bom = text.startswith("\ufeff")

        # --- configparser._read state -------------------------------- #
        sections: dict[str, dict[str, Any]] = {}
        section_order: list[str] = []
        comments: list[dict[str, Any]] = []
        seen_sections: set[str] = set()  # 'elements_added' section names
        seen_options: set[tuple[str, str]] = set()  # (sectname, lowerkey)
        cursect: str | None = None  # current section name (or None)
        sectname: str | None = None  # name of the section being read
        optname: str | None = None  # lowercased current option (or None)
        indent_level = 0

        def section_record(name: str) -> dict[str, Any]:
            record = sections.setdefault(
                name,
                {
                    "keys": [],  # original spellings, first-appearance order
                    "spellings": {},  # lowerkey -> original spelling
                    "values": {},  # lowerkey -> [parts] (joined later)
                    "key_lines": {},  # lowerkey -> first line
                    "duplicate_keys": {},  # lowerkey -> [lines]
                    "raw_lines": [],
                },
            )
            return record

        for lineno, line in enumerate(lines, 1):
            # -- full-line comment detection (inline prefixes are None
            #    in the default parser, so only full-line stripping) -- #
            stripped_for_comment = line.strip()
            comment_start = None
            for prefix in _COMMENT_PREFIXES:
                if stripped_for_comment.startswith(prefix):
                    comment_start = 0
                    break
            comments_on_line = comment_start == 0
            if comments_on_line:
                comments.append({"line": lineno, "text": stripped_for_comment})
            value = "" if comments_on_line else line
            value = value.strip()
            if not value:
                # blank line: with the default empty_lines_in_values=True
                # a blank line inside a value keeps an empty part (the
                # parser appends '' when a value is being continued).
                if not comments_on_line and cursect is not None and optname:
                    parts = sections[cursect]["values"].get(optname)
                    if parts is not None:
                        parts.append("")
                continue
            # -- continuation line? (deeper indent than the option) ---- #
            first_nonspace = _NONSPACECRE.search(line)
            cur_indent_level = first_nonspace.start() if first_nonspace else 0
            if cursect is not None and optname and cur_indent_level > indent_level:
                parts = sections[cursect]["values"].get(optname)
                if parts is not None:
                    parts.append(value)
                    sections[cursect]["raw_lines"].append(lineno)
                    if ";" in value or "#" in value:
                        flag(
                            "inline_comment_risk",
                            lineno,
                            "continuation line value contains ';' or '#' — the "
                            "default configparser keeps it as data, parsers "
                            "with inline_comment_prefixes would truncate it",
                        )
                continue
            # -- section header or option line -------------------------- #
            indent_level = cur_indent_level
            mo = _SECTCRE.match(value)
            if mo:
                sectname = mo.group("header")
                record = section_record(sectname)
                record["raw_lines"].append(lineno)
                if sectname in seen_sections:
                    # strict parser raises DuplicateSectionError here
                    message = (
                        f"section '{sectname}' declared again — the default "
                        "strict configparser raises DuplicateSectionError at "
                        "this line"
                    )
                    if sectname == _DEFAULT_SECTION:
                        # the parser treats a repeated [DEFAULT] as a plain
                        # re-entry (no DuplicateSectionError for DEFAULT);
                        # flag it as the risk it is instead
                        flag("duplicate_default_section", lineno, message)
                    else:
                        flag("duplicate_section", lineno, message)
                else:
                    seen_sections.add(sectname)
                    if sectname != _DEFAULT_SECTION:
                        section_order.append(sectname)
                    else:
                        # first [DEFAULT] block: tracked, not in section_order
                        pass
                cursect = sectname
                # a section header can't start with a continuation line
                optname = None
                continue
            if cursect is None:
                # strict parser raises MissingSectionHeaderError here —
                # cited at the *physical* line of the offending line
                # (configparser's 1-based counting; skipped blank and
                # comment preamble lines are not counted as content)
                flag(
                    "missing_section_header",
                    lineno,
                    "non-blank, non-comment line before any section header — "
                    "the default configparser raises MissingSectionHeaderError "
                    f"citing physical line {lineno}",
                )
                continue
            record = sections[cursect]
            record["raw_lines"].append(lineno)
            mo = _OPTCRE.match(value)
            if mo:
                raw_option = mo.group("option")
                if not raw_option:
                    # collected by the parser's ParsingError, raised at EOF
                    flag(
                        "unparseable_line",
                        lineno,
                        "line has a delimiter but an empty option name — the "
                        "default configparser records it in ParsingError "
                        f"as [line {lineno}]",
                    )
                spelling = raw_option.rstrip()
                optname = spelling.lower()  # the default optionxform; an
                # empty option name stays '' — falsy, exactly as in the
                # parser, where '' disables value continuation
                if (sectname, optname) in seen_options:
                    flag(
                        "duplicate_option",
                        lineno,
                        f"option '{optname}' in section '{sectname}' defined "
                        "again — the default strict configparser raises "
                        f"DuplicateOptionError at line {lineno}",
                    )
                    if spelling != record["spellings"].get(optname):
                        flag(
                            "duplicate_option_case",
                            lineno,
                            f"'{record['spellings'].get(optname)}' and "
                            f"'{spelling}' collide once lowercased — the "
                            "default optionxform lowercases option names, so "
                            "these are the same key to configparser",
                        )
                    dup = record["duplicate_keys"].setdefault(optname, [])
                    dup.append(lineno)
                    # non-strict behavior: the later value wins
                    record["values"][optname] = [mo.group("value").strip()]
                else:
                    seen_options.add((sectname, optname))
                    if optname not in record["spellings"]:
                        record["keys"].append(spelling)
                        record["spellings"][optname] = spelling
                        record["key_lines"][optname] = lineno
                    record["values"][optname] = [mo.group("value").strip()]
                if ";" in mo.group("value") or "#" in mo.group("value"):
                    flag(
                        "inline_comment_risk",
                        lineno,
                        "option value contains ';' or '#' — the default "
                        "configparser (inline_comment_prefixes=None) keeps it "
                        "as data, parsers with inline comment prefixes would "
                        "truncate it",
                    )
            else:
                # no delimiter at all in the line: a bare key or stray text
                flag(
                    "key_without_value",
                    lineno,
                    "line inside a section has no '=' or ':' delimiter — the "
                    "default configparser records it in ParsingError as "
                    f"[line {lineno}]",
                )

        # --- style / risk passes over physical lines ------------------ #
        for lineno, line in enumerate(lines, 1):
            body = line[:-1] if line.endswith("\r") else line
            if body != body.rstrip():
                flag(
                    "trailing_whitespace",
                    lineno,
                    "line has trailing whitespace before the terminator",
                )
            leading = line[: len(line) - len(line.lstrip())]
            if "\t" in leading:
                flag(
                    "tab_indentation",
                    lineno,
                    "leading indentation contains a tab — configparser accepts "
                    "it, but editors expanding tabs may break continuation "
                    "depth",
                )
        if text and not text.endswith("\n"):
            flag(
                "missing_final_newline",
                len(lines),
                "file does not end with a newline",
            )
        if bom:
            flag(
                "bom_present",
                1,
                "text starts with a UTF-8 BOM (\\\\ufeff) — configparser then "
                "raises MissingSectionHeaderError at line 1 because the BOM "
                "prefixes the first line and breaks the section-header match",
            )

        # --- finalize values (mirror _join_multiline_values: join the
        # parts, then rstrip — trailing blank parts disappear) -------- #
        for record in sections.values():
            record["values"] = {
                key: "\n".join(parts).rstrip()
                for key, parts in record["values"].items()
            }

        # --- interpolation risk over the joined values ---------------- #
        cls._flag_interpolation_risk(sections, flag)

        findings.sort(key=lambda f: (f["line"], f["code"]))
        codes = sorted({f["code"] for f in findings})
        would_reject = any(f["code"] in _MIRROR_ERROR_CODES for f in findings)
        return {
            "lines": lines,
            "line_count": len(lines),
            "bom": bom,
            "final_newline": text == "" or text.endswith("\n"),
            "sections": sections,
            "section_order": section_order,
            "comments": comments,
            "findings": findings,
            "codes": codes,
            "would_reject": would_reject,
        }

    @classmethod
    def _flag_interpolation_risk(cls, sections: dict[str, Any], flag: Any) -> None:
        """Flag values the default BasicInterpolation would trip on.

        ``read_string`` accepts any value; interpolation happens at
        ``get()`` time. Two passes:

        *Per-value scan* — flags a value when it contains a ``%`` that
        is not an escape (``%%``) and not the start of a ``%(name)s``
        token, a ``%( ... `` token without the ``)s`` terminator, or a
        complete ``%(name)s`` token whose name resolves neither in the
        section nor in ``[DEFAULT]`` (case-insensitively, matching
        ``optionxform``).

        *Reference-chain walk* — mirrors ``BasicInterpolation.
        _interpolate_some`` exactly (same token regex, same
        section-over-[DEFAULT] lookup map, same depth counter): a value
        also trips at ``get()`` time when its reference chain is
        cyclic or nested deeper than ``MAX_INTERPOLATION_DEPTH`` (10)
        — ``InterpolationDepthError`` — or when it references another
        option whose own value fails (the error propagates to every
        reader up the chain). Values already flagged by the per-value
        scan are not re-flagged.
        """
        default_keys = (
            {k.lower() for k in sections.get(_DEFAULT_SECTION, {}).get("keys", [])}
            if _DEFAULT_SECTION in sections
            else set()
        )
        flagged: set[tuple[str, str]] = set()
        for name, record in sections.items():
            resolvable = {k.lower() for k in record["keys"]} | default_keys
            for lowerkey, joined in record["values"].items():
                index = joined.find("%")
                if index == -1:
                    continue
                while index != -1:
                    tail = joined[index + 1 :]
                    if tail.startswith("%"):
                        index = joined.find("%", index + 2)
                        continue
                    if tail.startswith("("):
                        close = joined.find(")s", index)
                        if close == -1:
                            flag(
                                "interpolation_risk",
                                record["key_lines"].get(lowerkey, 1),
                                f"value of '{lowerkey}' in section '{name}' has "
                                "an unterminated '%(' interpolation token — the "
                                "default BasicInterpolation raises "
                                "InterpolationSyntaxError when the value is read",
                            )
                            flagged.add((name, lowerkey))
                            break
                        ref = joined[index + 2 : close].lower()
                        if ref not in resolvable:
                            # the reference token is a piece of the value —
                            # never echo it for a secret-ish key
                            shown = (
                                "an interpolation token"
                                if cls._is_secret(lowerkey)
                                else f"'%({ref})s'"
                            )
                            flag(
                                "interpolation_risk",
                                record["key_lines"].get(lowerkey, 1),
                                f"value of '{lowerkey}' in section '{name}' "
                                f"references {shown} which resolves neither "
                                "in the section nor in [DEFAULT] — the default "
                                "BasicInterpolation raises "
                                "InterpolationMissingOptionError when the value "
                                "is read",
                            )
                            flagged.add((name, lowerkey))
                        index = joined.find("%", close + 2)
                        continue
                    flag(
                        "interpolation_risk",
                        record["key_lines"].get(lowerkey, 1),
                        f"value of '{lowerkey}' in section '{name}' has a '%' "
                        "not followed by '%', '(' or a terminated token — the "
                        "default BasicInterpolation raises "
                        "InterpolationSyntaxError when the value is read",
                    )
                    flagged.add((name, lowerkey))
                    break

        # --- reference-chain walk (second pass) ------------------------- #
        default_values = (
            dict(sections[_DEFAULT_SECTION]["values"])
            if _DEFAULT_SECTION in sections
            else {}
        )
        for name, record in sections.items():
            # the lookup map _interpolate_some uses: [DEFAULT] values
            # overlaid with the section's own (for the [DEFAULT] record
            # itself this is its own values, exactly like _unify_values)
            merged = dict(default_values)
            merged.update(record["values"])
            for lowerkey, joined in record["values"].items():
                if (name, lowerkey) in flagged or "%" not in joined:
                    continue
                error = cls._interp_reachability(merged, joined, 1, {})
                if error is None:
                    continue
                kind, detail, depth = error
                line = record["key_lines"].get(lowerkey, 1)
                if kind == "depth":
                    message = (
                        f"value of '{lowerkey}' in section '{name}' starts an "
                        "interpolation chain that is cyclic or nested deeper "
                        f"than configparser's MAX_INTERPOLATION_DEPTH "
                        f"({_MAX_INTERPOLATION_DEPTH}) — the default "
                        "BasicInterpolation raises InterpolationDepthError "
                        "when the value is read"
                    )
                elif kind == "missing":
                    # unflagged by the first pass ⇒ the referenced name
                    # resolves, but its own value fails further down
                    shown = (
                        "another option"
                        if cls._is_secret(lowerkey)
                        else f"'{detail}'"
                    )
                    message = (
                        f"value of '{lowerkey}' in section '{name}' references "
                        f"{shown} whose own value fails interpolation — reading "
                        "this value raises the same "
                        "InterpolationMissingOptionError"
                    )
                elif depth > 1:
                    message = (
                        f"value of '{lowerkey}' in section '{name}' references "
                        "another option whose own value has invalid '%' "
                        "syntax — reading this value raises the same "
                        "InterpolationSyntaxError"
                    )
                else:
                    message = (
                        f"value of '{lowerkey}' in section '{name}' has a "
                        "'%(' token without a well-formed ')s' terminator — "
                        "the default BasicInterpolation raises "
                        "InterpolationSyntaxError when the value is read"
                    )
                flag("interpolation_risk", line, message)

    @classmethod
    def _interp_reachability(
        cls,
        merged: dict[str, str],
        value: str,
        depth: int,
        memo: dict[tuple[str, int], Any],
    ) -> Any:
        """Mirror ``BasicInterpolation._interpolate_some`` error behavior.

        Walks ``value`` against the fixed lookup map ``merged`` exactly
        as the stdlib does when ``get()`` resolves a value: ``%%`` is
        an escape, ``%(name)s`` (stdlib ``_KEYCRE`` shape) looks up the
        lowercased name in the map and recurses into the referenced
        value when it contains any ``%``, anything else is a syntax
        error. Returns ``None`` when the read succeeds, else a tuple
        ``(kind, detail, depth)`` with kind ``depth`` / ``missing`` /
        ``syntax``. Results are memoized per (value, depth); depth is
        strictly increasing along reference edges, so the recursion is
        bounded by ``_MAX_INTERPOLATION_DEPTH + 1``.
        """
        if depth > _MAX_INTERPOLATION_DEPTH:
            return ("depth", None, depth)
        memo_key = (value, depth)
        if memo_key in memo:
            return memo[memo_key]
        result = None
        pos = 0
        while True:
            index = value.find("%", pos)
            if index == -1:
                break
            nxt = value[index + 1 : index + 2]
            if nxt == "%":
                pos = index + 2
                continue
            if nxt == "(":
                match = _INTERPVAR_CRE.match(value, index)
                if match is None:
                    result = ("syntax", None, depth)
                    break
                var = match.group(1).lower()
                sub = merged.get(var)
                if sub is None:
                    result = ("missing", var, depth)
                    break
                if "%" in sub:
                    result = cls._interp_reachability(merged, sub, depth + 1, memo)
                    if result is not None:
                        break
                pos = match.end()
                continue
            result = ("syntax", None, depth)
            break
        memo[memo_key] = result
        return result

    # ------------------------------------------------------------------ #
    # Secret masking (family rule shared with the dotenv tool family)
    # ------------------------------------------------------------------ #

    @classmethod
    def _is_secret(cls, key: str) -> bool:
        """True when a key name looks secret-ish."""
        upper = key.upper()
        return any(marker in upper for marker in _SECRET_MARKERS)

    @classmethod
    def _mask_if_secret(cls, key: str, value: str) -> str:
        """Mask a value when its key name looks secret-ish."""
        if cls._is_secret(key):
            return _MASK
        return value

    # ------------------------------------------------------------------ #
    # Mode payloads
    # ------------------------------------------------------------------ #

    @classmethod
    def _run_lint(cls, scan: dict[str, Any]) -> dict[str, Any]:
        """Build the lint payload from a scan."""
        findings = scan["findings"]
        counts = {"error": 0, "warning": 0, "info": 0}
        for finding in findings:
            counts[finding["severity"]] += 1
        return {
            "result": "ok" if not findings else "findings",
            "findings": findings,
            "codes": scan["codes"],
            "counts": counts,
            "total_findings": len(findings),
            "total_lines": scan["line_count"],
            "configparser_would_reject": scan["would_reject"],
        }

    @classmethod
    def _run_parse(cls, scan: dict[str, Any]) -> dict[str, Any]:
        """Build the structured parse payload from a scan."""
        sections: dict[str, Any] = {}
        option_count = 0
        for name, record in scan["sections"].items():
            values = {
                key: cls._mask_if_secret(key, value)
                for key, value in record["values"].items()
            }
            duplicates = []
            for key, repeat_lines in record["duplicate_keys"].items():
                first = record["key_lines"].get(key)
                all_lines = [first, *repeat_lines] if first is not None else list(repeat_lines)
                duplicates.append({"key": key, "lines": sorted(all_lines)})
            duplicates.sort(key=lambda e: e["lines"][0])
            sections[name] = {
                "keys": list(record["keys"]),
                "values": values,
                "duplicate_keys": duplicates,
                "raw_lines": sorted(set(record["raw_lines"])),
            }
            option_count += len(record["keys"])
        return {
            "result": "ok" if not scan["would_reject"] else "parse_errors",
            "sections": sections,
            "section_order": list(scan["section_order"]),
            "comments": scan["comments"],
            "total_lines": scan["line_count"],
            "option_count": option_count,
            "configparser_would_reject": scan["would_reject"],
        }

    @classmethod
    def _run_check(cls, scan: dict[str, Any], flags: dict[str, bool]) -> dict[str, Any]:
        """Evaluate the policy options against a scan."""
        checks = []
        failed = 0
        for name, _default, codes in _CHECK_OPTIONS:
            enabled = flags[name]
            if not enabled:
                checks.append(
                    {"name": name, "ok": True, "enabled": False, "codes": list(codes), "violations": []}
                )
                continue
            violations = sorted(
                {f["line"] for f in scan["findings"] if f["code"] in codes}
            )
            ok = not violations
            if not ok:
                failed += 1
            checks.append(
                {
                    "name": name,
                    "ok": ok,
                    "enabled": True,
                    "codes": list(codes),
                    "violations": violations,
                }
            )
        return {
            "result": "pass" if failed == 0 else "fail",
            "checks": checks,
            "passed": len(checks) - failed,
            "failed": failed,
        }
