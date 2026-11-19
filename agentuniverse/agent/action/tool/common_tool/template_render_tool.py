#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: template_render_tool.py

"""Safe string template substitution tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency template utility
agents can call for prompt / message / payload assembly: fill named
placeholders, discover which placeholders a template needs, and check a
template for malformed placeholders before using it.

The substitution engine is the standard library's ``string.Template``
grammar — and nothing else:

* ``placeholder_style='dollar'`` (default) — ``${name}`` and ``$name``
  placeholders; ``$$`` is the escape for a literal ``$``.
* ``placeholder_style='brace'`` — a ``$``-free alternative for
  templates where ``$`` is common literal text (currency, shell
  snippets): ``{{name}}`` placeholders only; ``{{{{`` is the escape for
  a literal ``{{``; every ``$`` is plain literal text.

Three modes are supported:

* ``render`` — substitute a variables mapping into the template. The
  missing-variable policy is selectable: ``strict`` (default — a
  structured error payload listing every missing name), ``keep`` (leave
  the placeholder exactly as written, ``$name`` vs ``${name}``
  preserved) or ``default`` (fill every missing placeholder from the
  ``default_value`` option). Variables that do not appear in the
  template are reported back as ``unused_variables``.
* ``extract`` — list the placeholder names a template needs (unique,
  in order of first appearance).
* ``validate`` — check the template for malformed placeholders (an
  unclosed ``${``, a trailing ``$``, ``$`` followed by a non-identifier
  character, nested braces, an empty or non-identifier name) and report
  the position (index, line, column) of the first offender.

Security: this tool performs ``$``-placeholder substitution only, and
that choice is deliberate. ``str.format``-style ``{...}`` sequences are
never interpreted — braces are plain literal text unless they are part
of ``${...}`` (dollar style) — so attribute / index access expressions
such as ``{user.__class__}`` have no effect. The tool never calls
``eval``, ``exec`` or ``str.format``, and substituted values are
inserted literally and are never re-scanned for placeholders.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode / policy / style, a
``default_value`` used with a policy other than ``default``, a missing
``default_value`` when the policy is ``default``, oversized templates
or values) raise a ``ValueError``, mirroring the other common tools.
Errors that depend on the *content being processed* — a malformed
template, or missing variables under the ``strict`` policy — are
returned as a structured ``error`` payload so an agent can react
without catching exceptions.
"""

import re
import string
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class _BraceTemplate(string.Template):
    """``string.Template`` subclass whose grammar is ``{{name}}``.

    The placeholder pattern is overridden so ``{{`` introduces a
    placeholder, ``{{{{`` is the escape for a literal ``{{``, and any
    other ``{{`` run (unclosed, empty or non-identifier name) is an
    invalid placeholder. A lone ``$`` is plain literal text in this
    style. Substitution still runs through ``string.Template``'s own
    compiled pattern machinery.
    """

    delimiter = "{{"
    # __init_subclass__ compiles this string with re.VERBOSE; it
    # contains no whitespace or '#' so VERBOSE is a no-op here.
    pattern = (
        r"\{\{(?:(?P<escaped>\{\{)"
        r"|(?P<braced>[A-Za-z_][A-Za-z0-9_]*)\}\}"
        r"|(?P<invalid>))"
    )
    flags = 0


class TemplateRenderTool(Tool):
    """Safe string template substitution tool built purely on the stdlib.

    Attributes:
        max_template_chars (int): Upper bound on the ``template`` input
            length; longer inputs are rejected before any work.
        max_variables (int): Upper bound on the number of entries in
            the ``variables`` mapping.
        max_value_chars (int): Upper bound on the length of each
            (coerced) variable value.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "template_render_tool"
    description: str = (
        "Template render tool — safe string.Template-based placeholder "
        "substitution, pure Python stdlib, no network required. Renders "
        "${name}/$name placeholders from a variables dict with a "
        "missing-variable policy (mode='render': strict error listing "
        "missing names, keep placeholders as written, or fill from "
        "default_value; unused variables reported), lists the "
        "placeholder names a template needs (mode='extract'), and "
        "validates templates reporting malformed placeholders with "
        "line/column position (mode='validate'). '$$' escapes a literal "
        "'$'; placeholder_style='brace' offers a $-free {{name}} "
        "grammar. Never interprets str.format braces, never evals."
    )

    MODES: ClassVar[tuple] = ("render", "extract", "validate")
    MISSING_POLICIES: ClassVar[tuple] = ("strict", "keep", "default")
    PLACEHOLDER_STYLES: ClassVar[tuple] = ("dollar", "brace")

    max_template_chars: int = 100_000
    max_variables: int = 500
    max_value_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        template: Any = None,
        variables: Any = None,
        missing_policy: Any = None,
        default_value: Any = None,
        placeholder_style: Any = None,
    ) -> Dict[str, Any]:
        """Run one template operation.

        Args:
            mode (str): One of ``render`` / ``extract`` / ``validate``.
            template (str): The template text. Required for every mode
                (the empty string is a valid, placeholder-free
                template).
            variables (dict): Mapping of placeholder name to value for
                the ``render`` mode. Values may be ``str`` / ``int`` /
                ``float`` / ``bool`` and are coerced with ``str()``;
                keys must be non-empty strings. Ignored content-wise by
                ``extract`` / ``validate``.
            missing_policy (str): Render mode only — ``strict``
                (default; a structured error payload lists every
                missing name), ``keep`` (leave the placeholder exactly
                as written) or ``default`` (fill from ``default_value``).
            default_value (str | int | float | bool): Render mode only
                — the fill value for every missing placeholder when
                ``missing_policy='default'`` (coerced with ``str()``).
                Required with that policy, rejected with any other.
            placeholder_style (str): ``dollar`` (default) for
                ``${name}`` / ``$name`` with ``$$`` escaping, or
                ``brace`` for the ``$``-free ``{{name}}`` grammar with
                ``{{{{`` escaping.

        Returns:
            Dict[str, Any]: The operation result (a ``result`` string
                for ``render``, a ``placeholders`` list for
                ``extract``, a ``valid`` flag for ``validate``) plus
                the call context, or a structured ``error`` payload for
                content-level failures (malformed template, missing
                variables under the ``strict`` policy).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        style = self._validate_style(placeholder_style)
        clean_template = self._validate_template(template)
        clean_variables = self._validate_variables(variables)
        policy = self._validate_policy(missing_policy)
        clean_default = self._validate_default_value(
            default_value, policy, missing_policy
        )

        names, invalid_mo = self._scan(clean_template, style)
        if invalid_mo is not None:
            return self._malformed_result(mode, style, clean_template, invalid_mo)
        if mode == "validate":
            return {
                "mode": "validate",
                "placeholder_style": style,
                "valid": True,
                "placeholders": names,
                "count": len(names),
            }
        if mode == "extract":
            return {
                "mode": "extract",
                "placeholder_style": style,
                "placeholders": names,
                "count": len(names),
            }
        return self._render(mode, style, clean_template, names, clean_variables, policy, clean_default)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"template_render_tool: {message}")

    @classmethod
    def _validate_style(cls, placeholder_style: Any) -> str:
        """Validate the ``placeholder_style`` selector."""
        if placeholder_style is None:
            return "dollar"
        if placeholder_style not in cls.PLACEHOLDER_STYLES:
            cls._invalid(
                "placeholder_style must be one of: "
                f"{', '.join(cls.PLACEHOLDER_STYLES)} "
                f"(got {placeholder_style!r})"
            )
        return placeholder_style

    def _validate_template(self, template: Any) -> str:
        """Validate the ``template`` input (every mode needs it)."""
        if template is None or isinstance(template, bool) or not isinstance(template, str):
            self._invalid(f"template must be a string (got {template!r})")
        if len(template) > self.max_template_chars:
            self._invalid(
                f"template exceeds the {self.max_template_chars:,}-character "
                f"limit (got {len(template):,} characters)"
            )
        return template

    def _validate_variables(self, variables: Any) -> Dict[str, str]:
        """Validate and coerce the ``variables`` mapping.

        Keys must be non-empty strings; values may be ``str`` / ``int``
        / ``float`` / ``bool`` and are coerced to ``str``. Anything
        else — ``None`` values, lists, dicts — is rejected so that no
        ambiguous value ever reaches the substitution engine.
        """
        if variables is None:
            return {}
        if isinstance(variables, bool) or not isinstance(variables, dict):
            self._invalid(f"variables must be a dict of name -> value (got {variables!r})")
        if len(variables) > self.max_variables:
            self._invalid(
                f"variables exceed the {self.max_variables:,}-entry limit "
                f"(got {len(variables):,} entries)"
            )
        coerced: Dict[str, str] = {}
        for key, value in variables.items():
            if isinstance(key, bool) or not isinstance(key, str) or not key:
                self._invalid(
                    f"variable names must be non-empty strings (got {key!r})"
                )
            if value is None or not isinstance(value, (str, int, float, bool)):
                self._invalid(
                    "variable values must be str, int, float or bool "
                    f"(variable {key!r} got {value!r})"
                )
            text = str(value)
            if len(text) > self.max_value_chars:
                self._invalid(
                    f"value of variable {key!r} exceeds the "
                    f"{self.max_value_chars:,}-character limit "
                    f"(got {len(text):,} characters)"
                )
            coerced[key] = text
        return coerced

    @classmethod
    def _validate_policy(cls, missing_policy: Any) -> str:
        """Validate the ``missing_policy`` selector."""
        if missing_policy is None:
            return "strict"
        if missing_policy not in cls.MISSING_POLICIES:
            cls._invalid(
                "missing_policy must be one of: "
                f"{', '.join(cls.MISSING_POLICIES)} (got {missing_policy!r})"
            )
        return missing_policy

    def _validate_default_value(
        self, default_value: Any, policy: str, missing_policy: Any
    ) -> Optional[str]:
        """Validate the ``default_value`` fill option.

        Required (a scalar, coerced with ``str()`) when the policy is
        ``default``; explicitly rejected with any other policy so a
        silently-ignored fill value cannot go unnoticed.
        """
        if policy != "default":
            if default_value is not None:
                self._invalid(
                    "default_value is only allowed with "
                    f"missing_policy='default' (missing_policy="
                    f"{missing_policy!r})"
                )
            return None
        if default_value is None or not isinstance(default_value, (str, int, float, bool)):
            self._invalid(
                "default_value is required when missing_policy='default' "
                "and must be a str, int, float or bool "
                f"(got {default_value!r})"
            )
        default_text = str(default_value)
        if len(default_text) > self.max_value_chars:
            self._invalid(
                f"default_value exceeds the {self.max_value_chars:,}-character "
                f"limit (got {len(default_text):,} characters)"
            )
        return default_text

    # ------------------------------------------------------------------ #
    # Placeholder scanning (string.Template's own compiled grammar)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _template_class(style: str) -> type:
        """Return the ``string.Template`` subclass for the style."""
        return string.Template if style == "dollar" else _BraceTemplate

    @classmethod
    def _literal_delimiter(cls, style: str) -> str:
        """Return the text a doubled escape inserts (``$`` or ``{{``)."""
        return "$" if style == "dollar" else "{{"

    @classmethod
    def _grammar_help(cls, style: str) -> str:
        """Return the human-readable grammar description for errors."""
        if style == "dollar":
            return (
                "expected '$$' (escaped dollar), '$name' or '${name}' "
                "with an ASCII identifier name ([A-Za-z_][A-Za-z0-9_]*)"
            )
        return (
            "expected '{{{{' (escaped '{{'), or '{{name}}' with an ASCII "
            "identifier name ([A-Za-z_][A-Za-z0-9_]*)"
        )

    def _scan(
        self, template: str, style: str
    ) -> Tuple[List[str], Any]:
        """Scan a template with ``string.Template``'s compiled pattern.

        Returns the unique placeholder names in order of first
        appearance and the first invalid match object (``None`` when
        the template is well-formed).
        """
        pattern = self._template_class(style)("").pattern
        names: List[str] = []
        seen = set()
        for mo in pattern.finditer(template):
            groups = mo.groupdict()
            if groups["invalid"] is not None:
                return names, mo
            if groups["escaped"] is not None:
                continue
            name = groups.get("named") or groups.get("braced")
            if name not in seen:
                seen.add(name)
                names.append(name)
        return names, None

    @classmethod
    def _position(cls, template: str, index: int) -> Dict[str, int]:
        """Compute 1-based line/column for a 0-based template index."""
        line = template.count("\n", 0, index) + 1
        column = index - (template.rfind("\n", 0, index) + 1) + 1
        return {"index": index, "line": line, "col": column}

    # ------------------------------------------------------------------ #
    # Mode implementations
    # ------------------------------------------------------------------ #

    def _render(
        self,
        mode: str,
        style: str,
        template: str,
        names: List[str],
        variables: Dict[str, str],
        policy: str,
        default_value: Optional[str],
    ) -> Dict[str, Any]:
        """Substitute the variables into the (already validated) template."""
        missing = sorted(name for name in names if name not in variables)
        context: Dict[str, Any] = {
            "mode": mode,
            "placeholder_style": style,
            "missing_policy": policy,
            "placeholders": names,
            "missing_variables": missing,
        }
        if missing and policy == "strict":
            return self._error_result(
                context,
                error_type="missing_variables",
                message=(
                    "template requires variables that were not provided: "
                    f"{', '.join(missing)} (missing_policy='strict'; "
                    "provide them or choose missing_policy 'keep' or "
                    "'default')"
                ),
                missing=missing,
            )

        literal_delimiter = self._literal_delimiter(style)

        def convert(mo: Any) -> str:
            groups = mo.groupdict()
            # Escaped delimiter: '$$' -> '$', '{{{{' -> '{{'.
            if groups["escaped"] is not None:
                return literal_delimiter
            name = groups.get("named") or groups.get("braced")
            if name in variables:
                return variables[name]
            if policy == "keep":
                # Leave the placeholder exactly as written, preserving
                # the $name vs ${name} spelling of this occurrence.
                return mo.group(0)
            return default_value  # policy == 'default'

        pattern = self._template_class(style)("").pattern
        result = pattern.sub(convert, template)
        unused = sorted(key for key in variables if key not in set(names))
        return {
            **context,
            "unused_variables": unused,
            "result": result,
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    def _malformed_result(
        self, mode: str, style: str, template: str, invalid_mo: Any
    ) -> Dict[str, Any]:
        """Build the structured payload for a malformed template."""
        position = self._position(template, invalid_mo.start())
        context: Dict[str, Any] = {
            "mode": mode,
            "placeholder_style": style,
        }
        if mode == "validate":
            context["valid"] = False
        return self._error_result(
            context,
            error_type="malformed_template",
            message=(
                "invalid placeholder in template at line "
                f"{position['line']}, column {position['col']} "
                f"(index {position['index']}): "
                f"{self._grammar_help(style)}"
            ),
            **position,
        )

    @staticmethod
    def _error_result(
        context: Dict[str, Any], error_type: str, message: str, **extra: Any
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {
                "type": error_type,
                "message": str(message)[:500],
                **extra,
            },
        }
