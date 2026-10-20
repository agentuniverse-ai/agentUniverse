#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: prompt_template_linter_tool.py

"""Prompt template linter / extractor / filler built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency utility that lets
agents inspect and manipulate agentUniverse prompt templates — the
``{placeholder}`` templates used by the framework's prompt components.

Placeholder convention (discovered from the framework source):

* Extraction — ``agentuniverse/prompt/prompt.py`` builds
  ``input_variables`` with ``re.findall(r'\\{(.*?)}', template)``
  (``Prompt.build_prompt`` and
  ``Prompt.initialize_by_component_configer``), and
  ``agentuniverse/prompt/chat_prompt.py::extract_placeholders`` uses
  the same lazy pattern. Placeholders are therefore ``{name}`` spans
  bounded by the first ``}``.
* Names — every placeholder in the shipped prompts (for example
  ``agentuniverse/agent/default/react_agent/default_en_prompt.yaml``
  with ``{tools}``, ``{tool_names}``, ``{chat_history}``,
  ``{background}``, ``{input}``, ``{agent_scratchpad}``) is a simple
  identifier matching ``[A-Za-z_][A-Za-z0-9_]*``.
* Resolution — the framework fills templates through
  ``Prompt.as_langchain()`` (LangChain ``PromptTemplate`` with the
  default ``f-string`` template format) and then ``.format(**vars)``
  (see ``agentuniverse/base/util/prompt_util.py`` and the planners).
  That is Python ``str.format`` semantics: ``{{`` and ``}}`` are
  escapes for literal braces (NOT placeholders), a single unmatched
  ``{`` or ``}`` is an error, and a ``{`` nested inside a field is an
  error. Substituted values are inserted verbatim and are never
  re-scanned for braces.

The tool aligns with the *resolution* semantics (that is what actually
renders), while flagging constructs where the framework's own lazy
extraction regex would disagree — e.g. it does not honor ``{{``
escapes — through the ``malformed_braces`` finding.

Three modes are supported:

* ``lint`` — scan template text and report findings:
  ``malformed_braces`` (unbalanced ``{`` / ``}``, nested braces —
  error), ``empty_placeholder`` (``{}`` — error), ``invalid_name``
  (names with spaces or special characters — error),
  ``placeholder_in_code`` (placeholder inside a `` ``` `` fenced
  block — warning; note the framework itself intentionally places one
  in ``agentuniverse/base/util/prompt/combine_en_prompt.yaml``),
  ``duplicate_placeholder`` (same name used two or more times — info,
  legal but flagged) and, when a ``known_variables`` list is given,
  ``placeholders_not_in_vars`` / ``vars_without_placeholder`` (info).
* ``extract`` — return the ordered unique placeholder names, mirroring
  the framework's lazy extraction (names that ``lint`` flags as
  invalid are still listed; an empty ``{}`` span has no name and is
  skipped).
* ``fill`` — substitute a ``variables`` mapping into the template
  using the framework's escaping rules (``{{`` -> ``{``, ``}}`` ->
  ``}``, values verbatim). Strict by default: missing variables
  return a structured error listing them and extra variables produce a
  warning list; ``keep_unknown=True`` leaves missing placeholders
  unfilled instead of erroring.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty template, unknown mode,
non-string variable keys or values, more than 200 variables, template
over 100,000 characters) raise a ``ValueError``, mirroring the other
common tools. Errors that depend on the *content being processed* —
malformed template braces in ``fill`` mode, missing variables in
strict mode — are returned as a structured ``error`` payload so an
agent can react without catching exceptions.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Valid placeholder names: simple identifiers, matching every name in
# the framework's shipped prompts (tools, tool_names, chat_history,
# background, input, agent_scratchpad, text, ...).
_IDENTIFIER = re.compile(r"\A[A-Za-z_][A-Za-z0-9_]*\Z")
# CommonMark-style opening fence: up to three leading spaces then ```.
_FENCE_OPEN = re.compile(r"\A {0,3}```")

_MAX_TEMPLATE_CHARS = 100_000
_MAX_VARIABLES = 200

SEVERITY_ORDER = ("error", "warning", "info")


class _ScanResult:
    """Internal result of one template scan.

    Attributes:
        placeholders (list[str]): Well-formed placeholder names in
            order of first appearance (duplicates kept for reporting).
        spans (list[tuple[str, int, int]]): ``(name, start_offset,
            end_offset)`` for every well-formed placeholder.
        findings (list[dict]): Structured findings discovered by the
            scan (malformed braces, empty or invalid names, ...).
    """

    def __init__(self) -> None:
        self.placeholders: list[str] = []
        self.spans: list[tuple[str, int, int]] = []
        self.findings: list[dict[str, Any]] = []


def _line_col(template: str, offset: int) -> tuple[int, int]:
    """Return the 1-based ``(line, column)`` of a character offset."""
    line = template.count("\n", 0, offset) + 1
    column = offset - (template.rfind("\n", 0, offset) + 1) + 1
    return line, column


def _scan(template: str, report_code: bool) -> _ScanResult:
    """Scan a template once, mirroring ``str.format`` brace semantics.

    ``{{`` and ``}}`` are literal-brace escapes and never placeholders;
    a single unmatched ``{`` or ``}`` and a ``{`` nested inside a field
    are malformed. When ``report_code`` is set, a note about fenced
    code blocks is recorded on placeholders found inside one.
    """
    result = _ScanResult()
    length = len(template)
    # A fence may open on the very first line, before any newline.
    in_fence = _FENCE_OPEN.match(template) is not None
    offset = 0

    def add_finding(kind: str, severity: str, message: str, at: int) -> None:
        line, column = _line_col(template, at)
        result.findings.append(
            {
                "type": kind,
                "severity": severity,
                "message": message,
                "line": line,
                "column": column,
            }
        )

    while offset < length:
        char = template[offset]
        if char == "{":
            if template.startswith("{{", offset):
                offset += 2  # escaped literal '{'
                continue
            # Opening a placeholder field: find the bounding '}'.
            end = template.find("}", offset + 1)
            nested = template.find("{", offset + 1, end if end != -1 else length)
            if end == -1:
                add_finding(
                    "malformed_braces",
                    "error",
                    "unbalanced braces: '{' is never closed",
                    offset,
                )
                break
            if nested != -1:
                line, column = _line_col(template, nested)
                add_finding(
                    "malformed_braces",
                    "error",
                    "unbalanced braces: nested '{' inside a placeholder field",
                    offset,
                )
                offset = end + 1  # resync after the first '}'
                continue
            name = template[offset + 1:end]
            if not name:
                add_finding(
                    "empty_placeholder",
                    "error",
                    "empty placeholder '{}': no variable name between the braces",
                    offset,
                )
            elif not _IDENTIFIER.match(name):
                add_finding(
                    "invalid_name",
                    "error",
                    f"invalid placeholder name {name!r}: expected a simple "
                    "identifier ([A-Za-z_][A-Za-z0-9_]*)",
                    offset,
                )
            if name:
                result.placeholders.append(name)
                result.spans.append((name, offset, end + 1))
                if report_code and in_fence:
                    line, column = _line_col(template, offset)
                    result.findings.append(
                        {
                            "type": "placeholder_in_code",
                            "severity": "warning",
                            "message": (
                                f"placeholder {{{name}}} is inside a fenced "
                                "code block; verify this is intentional"
                            ),
                            "line": line,
                            "column": column,
                            "name": name,
                        }
                    )
            offset = end + 1
        elif char == "}":
            if template.startswith("}}", offset):
                offset += 2  # escaped literal '}'
                continue
            add_finding(
                "malformed_braces",
                "error",
                "unbalanced braces: single '}' without a matching '{'",
                offset,
            )
            offset += 1
        else:
            if char == "\n" and _FENCE_OPEN.match(template[offset + 1:]):
                in_fence = not in_fence
            offset += 1
    return result


class PromptTemplateLinterTool(Tool):
    """Lint / extract / fill agentUniverse prompt templates (stdlib only).

    Attributes:
        max_template_chars (int): Upper bound on the ``template`` input
            length; longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "prompt_template_linter_tool"
    description: str = (
        "Prompt template linter tool — pure Python stdlib, no network "
        "required. Lint agentUniverse {placeholder} prompt templates "
        "(mode='lint': malformed braces, empty placeholders, invalid "
        "names, placeholders inside fenced code blocks, duplicates, and "
        "comparison against a known_variables list), extract the ordered "
        "unique placeholder names (mode='extract'), and fill templates "
        "with a variables mapping using the framework's escaping rules "
        "(mode='fill': strict by default, keep_unknown=True leaves "
        "missing placeholders unfilled)."
    )

    MODES: ClassVar[tuple] = ("lint", "extract", "fill")

    max_template_chars: int = _MAX_TEMPLATE_CHARS

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        template: Any = None,
        variables: Any = None,
        known_variables: Any = None,
        keep_unknown: Any = None,
    ) -> dict[str, Any]:
        """Run one prompt-template operation.

        Args:
            mode (str): One of ``lint`` / ``extract`` / ``fill``.
            template (str): The prompt template text using the
                framework's ``{placeholder}`` convention.
            variables (dict[str, str]): Mapping of placeholder name to
                replacement text — required for the ``fill`` mode.
            known_variables (list[str]): Optional list of declared
                variable names — ``lint`` mode only; placeholders not
                in the list and variables without a placeholder are
                both reported.
            keep_unknown (bool): ``fill`` mode only — leave missing
                placeholders unfilled instead of returning a
                missing-variables error. Defaults to ``False``.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                value plus the call context) or a structured ``error``
                payload for content-level failures (malformed template
                braces in fill mode, missing variables in strict
                mode).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_template = self._validate_template(template)
        clean_keep_unknown = self._validate_keep_unknown(keep_unknown)

        if mode == "lint":
            clean_known = self._validate_known_variables(known_variables)
            return self._run_lint(clean_template, clean_known)
        if mode == "extract":
            return self._run_extract(clean_template)
        clean_variables = self._validate_variables(variables)
        return self._run_fill(
            clean_template, clean_variables, bool(clean_keep_unknown)
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"prompt_template_linter_tool: {message}")

    @classmethod
    def _validate_template(cls, template: Any) -> str:
        """Validate the ``template`` input."""
        if template is None or isinstance(template, bool) or not isinstance(template, str):
            cls._invalid(f"template must be a non-empty string (got {template!r})")
        if not template:
            cls._invalid("template must be a non-empty string (got '')")
        if len(template) > _MAX_TEMPLATE_CHARS:
            cls._invalid(
                f"template exceeds the {_MAX_TEMPLATE_CHARS:,}-character limit "
                f"(got {len(template):,} characters)"
            )
        return template

    @classmethod
    def _validate_keep_unknown(cls, keep_unknown: Any) -> bool:
        """Validate the ``keep_unknown`` flag (fill mode)."""
        if keep_unknown is None:
            return False
        if not isinstance(keep_unknown, bool):
            cls._invalid(f"keep_unknown must be a boolean or None (got {keep_unknown!r})")
        return keep_unknown

    @classmethod
    def _validate_known_variables(cls, known_variables: Any) -> list[str]:
        """Validate the optional ``known_variables`` list (lint mode)."""
        if known_variables is None:
            return []
        if isinstance(known_variables, (str, bytes)) or not isinstance(known_variables, (list, tuple)):
            cls._invalid(
                f"known_variables must be a list of non-empty strings (got {known_variables!r})"
            )
        clean: list[str] = []
        for item in known_variables:
            if item is None or isinstance(item, bool) or not isinstance(item, str):
                cls._invalid(
                    "known_variables must be a list of non-empty strings "
                    f"(got item {item!r})"
                )
            if not item:
                cls._invalid(
                    "known_variables must be a list of non-empty strings (got '')"
                )
            if item not in clean:
                clean.append(item)
        return clean

    @classmethod
    def _validate_variables(cls, variables: Any) -> dict[str, str]:
        """Validate the ``variables`` mapping (fill mode): str -> str."""
        if variables is None:
            cls._invalid("variables must be a dict of string variable name to string value (got None)")
        if isinstance(variables, (str, bytes, list, tuple)) or not isinstance(variables, dict):
            cls._invalid(
                f"variables must be a dict of string variable name to string value (got {variables!r})"
            )
        if len(variables) > _MAX_VARIABLES:
            cls._invalid(
                f"variables exceed the {_MAX_VARIABLES}-entry limit (got {len(variables)} entries)"
            )
        for key, value in variables.items():
            if key is None or isinstance(key, bool) or not isinstance(key, str):
                cls._invalid(
                    f"variable names must be non-empty strings (got key {key!r})"
                )
            if not key:
                cls._invalid("variable names must be non-empty strings (got '')")
            if value is None or isinstance(value, bool) or not isinstance(value, str):
                cls._invalid(
                    f"variable values must be strings (got {key!r}={value!r})"
                )
        return dict(variables)

    # ------------------------------------------------------------------ #
    # lint mode
    # ------------------------------------------------------------------ #

    def _run_lint(
        self, template: str, known_variables: list[str]
    ) -> dict[str, Any]:
        """Scan the template and report every category of finding."""
        scan = _scan(template, report_code=True)
        findings = list(scan.findings)

        seen: dict[str, int] = {}
        for name in scan.placeholders:
            seen[name] = seen.get(name, 0) + 1
        for name, count in seen.items():
            if count >= 2:
                occurrences = [
                    _line_col(template, start) for (n, start, _) in scan.spans if n == name
                ]
                line, column = occurrences[0]
                findings.append(
                    {
                        "type": "duplicate_placeholder",
                        "severity": "info",
                        "message": (
                            f"placeholder {{{name}}} is used {count} times "
                            f"(lines {', '.join(str(l) for l, _ in occurrences)}); "
                            "this is legal but each occurrence receives the same value"
                        ),
                        "line": line,
                        "column": column,
                        "name": name,
                    }
                )

        unique_names = list(seen)
        placeholders_not_in_vars: list[str] = []
        vars_without_placeholder: list[str] = []
        if known_variables:
            known_set = set(known_variables)
            placeholders_not_in_vars = [n for n in unique_names if n not in known_set]
            vars_without_placeholder = [
                v for v in known_variables if v not in set(unique_names)
            ]
            for name in placeholders_not_in_vars:
                first = min(start for (n, start, _) in scan.spans if n == name)
                line, column = _line_col(template, first)
                findings.append(
                    {
                        "type": "placeholders_not_in_vars",
                        "severity": "info",
                        "message": (
                            f"placeholder {{{name}}} is not in the declared "
                            "known_variables list"
                        ),
                        "line": line,
                        "column": column,
                        "name": name,
                    }
                )
            for var in vars_without_placeholder:
                findings.append(
                    {
                        "type": "vars_without_placeholder",
                        "severity": "info",
                        "message": (
                            f"declared variable '{var}' has no placeholder in "
                            "the template"
                        ),
                        "line": 0,
                        "column": 0,
                        "name": var,
                    }
                )

        severity_order = {name: index for index, name in enumerate(SEVERITY_ORDER)}
        findings.sort(key=lambda f: (f["line"], f["column"], severity_order.get(f["severity"], 99)))
        counts = {
            "error": sum(1 for f in findings if f["severity"] == "error"),
            "warning": sum(1 for f in findings if f["severity"] == "warning"),
            "info": sum(1 for f in findings if f["severity"] == "info"),
        }
        result: dict[str, Any] = {
            "mode": "lint",
            "ok": counts["error"] == 0,
            "result": (
                f"{len(findings)} finding(s): "
                f"{counts['error']} error, {counts['warning']} warning, "
                f"{counts['info']} info"
            ),
            "placeholders": unique_names,
            "counts": {**counts, "total": len(findings)},
            "findings": findings,
        }
        if known_variables:
            result["placeholders_not_in_vars"] = placeholders_not_in_vars
            result["vars_without_placeholder"] = vars_without_placeholder
        return result

    # ------------------------------------------------------------------ #
    # extract mode
    # ------------------------------------------------------------------ #

    def _run_extract(self, template: str) -> dict[str, Any]:
        """Return the ordered unique placeholder names."""
        scan = _scan(template, report_code=False)
        unique: list[str] = []
        for name in scan.placeholders:
            if name not in unique:
                unique.append(name)
        return {
            "mode": "extract",
            "result": unique,
            "count": len(unique),
        }

    # ------------------------------------------------------------------ #
    # fill mode
    # ------------------------------------------------------------------ #

    def _run_fill(
        self, template: str, variables: dict[str, str], keep_unknown: bool
    ) -> dict[str, Any]:
        """Fill the template using the framework's resolution semantics.

        Escapes are resolved exactly like the framework's fill path
        (LangChain ``PromptTemplate`` with the default f-string format,
        i.e. Python ``str.format``): ``{{`` becomes a literal ``{``,
        ``}}`` becomes a literal ``}``, and substituted values are
        inserted verbatim without re-scanning.
        """
        context: dict[str, Any] = {
            "mode": "fill",
            "keep_unknown": keep_unknown,
        }
        scan = _scan(template, report_code=False)
        blocking = [f for f in scan.findings if f["severity"] == "error"]
        if blocking:
            return self._error_result(
                context,
                error_type="malformed_template",
                message=(
                    "template has malformed braces and cannot be filled: "
                    + "; ".join(
                        f"line {f['line']}, column {f['column']}: {f['message']}"
                        for f in blocking
                    )
                ),
            )

        needed = []
        for name in scan.placeholders:
            if name not in needed:
                needed.append(name)
        missing = [name for name in needed if name not in variables]
        if missing and not keep_unknown:
            return self._error_result(
                context,
                error_type="missing_variables",
                message=(
                    "missing values for placeholder(s): "
                    + ", ".join(f"{{{name}}}" for name in missing)
                ),
            )

        extra = [key for key in variables if key not in set(needed)]
        warnings = [
            f"variable '{key}' has no placeholder in the template" for key in extra
        ]

        pieces: list[str] = []
        filled: list[str] = []
        unfilled: list[str] = []
        cursor = 0
        for name, start, end in scan.spans:
            pieces.append(self._resolve_escapes(template[cursor:start]))
            if name in variables:
                # Substituted values are verbatim: braces inside a
                # value are never re-scanned or escaped.
                pieces.append(variables[name])
                if name not in filled:
                    filled.append(name)
            else:
                pieces.append(template[start:end])
                if name not in unfilled:
                    unfilled.append(name)
            cursor = end
        pieces.append(self._resolve_escapes(template[cursor:]))
        filled_text = "".join(pieces)

        result: dict[str, Any] = {
            **context,
            "result": filled_text,
            "filled": filled,
            "unfilled": unfilled,
            "extra_variables": extra,
            "warnings": warnings,
        }
        return result

    @staticmethod
    def _resolve_escapes(segment: str) -> str:
        """Resolve ``{{`` / ``}}`` escapes in a literal template segment.

        Doubled braces are consumed strictly left-to-right in pairs,
        mirroring how the scanner (and Python ``str.format``) consume
        them; segments come from a template that already passed a
        clean scan, so every brace in a literal segment belongs to an
        escape pair.
        """
        out: list[str] = []
        i = 0
        n = len(segment)
        while i < n:
            char = segment[i]
            if char == "{" and i + 1 < n and segment[i + 1] == "{":
                out.append("{")
                i += 2
            elif char == "}" and i + 1 < n and segment[i + 1] == "}":
                out.append("}")
                i += 2
            else:
                out.append(char)
                i += 1
        return "".join(out)

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: dict[str, Any], error_type: str, message: str
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
