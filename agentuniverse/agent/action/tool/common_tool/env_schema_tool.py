#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: env_schema_tool.py

"""dotenv (``.env``) *schema validation* tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the contract-checking layer for dotenv files: given
a ``.env`` payload and a *declared schema* of what the application
needs, answer "does my .env define everything, with the right types?"
— the question neither ``EnvFileTool`` (#3727, parse / edit dotenv
text) nor ``IniConfigTool`` / ``JsonYamlTool`` (other config formats)
ask. Three modes, all offline and deterministic:

* ``check`` — validate ``.env`` *text* against a ``schema`` mapping
  ``VAR -> rule`` where each rule may declare ``required`` (default
  ``True``), ``type`` (``string`` | ``int`` | ``float`` | ``bool`` |
  ``url`` | ``email`` | ``path``, default ``string``), ``default``
  (a string, injected as the effective value when the variable is
  absent), ``min`` / ``max`` (numeric bounds, ``int``/``float`` types
  only) and ``enum`` (a non-empty list of the allowed raw values).
  The payload reports:

  - ``missing`` — schema-declared variables the file never defines.
    Each entry carries ``required``, ``has_default`` and a paste-ready
    ``suggestion`` line (``VAR=<default>`` when a default exists — the
    default injection suggestion — otherwise a ``VAR=`` skeleton).
  - ``applied_defaults`` — ``[{var, default}]`` for absent variables
    whose schema default became the effective value so the check can
    still pass; the default is itself type/enum/bounds-checked like a
    file value.
  - ``extra`` — variables defined in the file but not declared in the
    schema, each with a ``used-by-source`` note naming the defining
    line(s). Values are never shown for extras (an undeclared
    secret must not leak through the report).
  - ``type_mismatches`` — ``[{var, expected, got,
    raw_value_preview}]`` where ``got`` is the inferred type of the
    offending value and ``raw_value_preview`` is a <=24-character
    preview that is ``***`` for secret-ish names (see masking below).
  - ``violations`` — enum / min / max breaches
    (``{var, rule, expected, got}``).
  - ``passed`` — ``True`` only when no *required* variable is missing
    without a default and no mismatch or violation occurred. Missing
    optional variables and extras never fail the check.

* ``suggest_schema`` — the bootstrap mode: infer a schema from an
  existing ``.env`` text. Every variable gets
  ``{type, required: true, sample_masked}`` plus ``inferred_enum``
  when the variable is assigned 2-4 distinct values across duplicate
  occurrences (the in-file signal for an enum; 5+ distinct values or
  a single value yields no enum). The output uses exactly the
  ``check`` schema shape, so suggest -> review -> check round-trips.
* ``diff`` — compare two ``.env`` texts (e.g. prod vs staging) and
  report ``only_in_a`` / ``only_in_b`` (each entry carries the value,
  masked for secret-ish names), ``value_diffs``
  (``{var, a, b, masked}`` — secret-ish variables never expose their
  raw values, both sides become ``***``) and ``count`` (the total
  number of differing variables).

Secret masking: a variable whose *name* contains ``KEY``, ``SECRET``,
``PASSWORD`` or ``TOKEN`` (case-insensitive substring) never has its
value echoed. It becomes ``***`` in ``raw_value_preview``, diff
entries and ``sample_masked``, and ``suggest_schema`` omits
``inferred_enum`` for it entirely (enumerating observed secret values
would leak them). Numeric ``got`` fields in violations are masked the
same way.

Value parsing follows dotenv rules, consistent with ``EnvFileTool``:
blank / ``#`` lines are skipped, an optional ``export`` prefix is
accepted, the first ``=`` splits key from value, keys match
``[A-Za-z_][A-Za-z0-9_]*``, and duplicates are last-wins (all
occurrence lines and distinct values are tracked for enum
suggestion). Double-quoted values unescape ``\\n``, ``\\t``, ``\\r``,
``\\\\`` and ``\\"`` and end at the closing quote (content after it is
ignored); single-quoted values are fully literal; unquoted values end
at the first ``#`` directly preceded by whitespace (a ``#`` glued
directly after ``=`` or into text such as ``KEY=#c`` / ``a#b`` is
data), with surrounding whitespace stripped. Lines that are neither
blank, comment nor a well-formed assignment are reported in
``malformed_lines`` instead of aborting; an unterminated quote is a
structured ``unterminated_quote`` error payload with the line number.

Type coercion (documented contract, checked on the *parsed* value):
``int`` accepts ``[+-]?digits`` (plain decimal only — no
underscores, whitespace, hex or ``inf``); ``float`` accepts plain
decimal / exponent forms (``1`` ``1.5`` ``.5`` ``1.`` ``1e3``,
explicit sign allowed; ``inf`` / ``nan`` / hex rejected); ``bool``
accepts ``true`` / ``false`` / ``1`` / ``0`` / ``yes`` / ``no``,
case-insensitive (``1``/``0`` are therefore valid for both ``int``
and ``bool`` declarations); ``url`` requires a scheme and a host
(``urllib.parse``-split, e.g. ``http://h`` / ``postgres://db:5432/x``
pass, ``h:8080`` / ``http://`` fail); ``email`` uses the
``EmailValidatorTool`` family profile — dot-atom local part (RFC
5322 atext segments, no leading / trailing / consecutive dots,
<=64 chars) and dotted domain labels (``[A-Za-z0-9-]+``, no
leading / trailing hyphen, <=63 per label, <=254 total; quoted
locals and IP literals stay ``EmailValidatorTool``'s job);
``path`` requires a non-empty single-line value with no ASCII
control characters (NUL included). ``string`` accepts anything,
including empty. Type *inference* (``suggest_schema`` and the
``got`` field) tries int, then float, then bool, then url, then
email, and falls back to string — it never infers ``path``
(indistinguishable from a plain string). ``check`` additionally
tolerates the informational ``sample_masked`` / ``inferred_enum``
keys ``suggest_schema`` emits, so a suggested schema can be edited
and fed straight back in.

Malformed *parameters* (wrong types, unknown mode, non-dict schema,
schema keys that are not variable names, per-rule shape errors —
unknown keys, non-bool ``required``, unknown ``type``, non-string
``default``, non-numeric / type-inconsistent ``min``/``max``,
malformed ``enum``, oversized text / schema) raise a ``ValueError``
*before* any computation, always naming the offending variable.
Content-level failures (unterminated quotes) are structured
``error`` payloads so an agent can react without catching
exceptions. The tool never touches the filesystem or the network.
"""

import re
from typing import Any, ClassVar
from urllib.parse import urlsplit

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# --------------------------------------------------------------------- #
# dotenv line parsing (consistent with EnvFileTool's documented rules)
# --------------------------------------------------------------------- #

# A dotenv key: same identifier charset the shell accepts.
_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
# assignment := [export + whitespace] key [whitespace*] "=" rest-of-line
_ASSIGN_RE = re.compile(r"(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")
# Escape sequences unescaped inside double-quoted values.
_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"'}

# --------------------------------------------------------------------- #
# type coercion / inference
# --------------------------------------------------------------------- #

_INT_RE = re.compile(r"[+-]?[0-9]+\Z")
_FLOAT_RE = re.compile(
    r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z"
)
_SCHEME_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*\Z")
_BOOL_WORDS = frozenset(("true", "false", "1", "0", "yes", "no"))
# RFC 5322 atext — the dot-atom alphabet of an unquoted local part
# (same charset as EmailValidatorTool).
_ATEXT_RE = re.compile(r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+\Z")
_DOMAIN_LABEL_RE = re.compile(r"[A-Za-z0-9-]+\Z")
# ASCII control characters (C0 + DEL) — invalid in a declared path.
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")

# Email profile limits, mirroring EmailValidatorTool's constants.
_MAX_LOCAL_CHARS = 64
_MAX_LABEL_CHARS = 63
_MAX_EMAIL_CHARS = 254

# Types a schema rule may declare.
TYPES = ("string", "int", "float", "bool", "url", "email", "path")
# Rule keys a schema entry may use.
_RULE_KEYS = frozenset(("required", "type", "default", "min", "max", "enum"))
# Informational keys ``suggest_schema`` emits alongside the rule; the
# ``check`` mode accepts and ignores them so the suggest -> edit ->
# check round-trip works without stripping keys by hand.
_INFO_KEYS = frozenset(("sample_masked", "inferred_enum"))
# Name substrings marking a variable as secret-ish (case-insensitive).
_SECRET_MARKERS = ("KEY", "SECRET", "PASSWORD", "TOKEN")

_MASK = "***"
_PREVIEW_CHARS = 24


class _EnvParseError(Exception):
    """Content-level parse failure (carries the line number)."""

    def __init__(self, line: int, message: str) -> None:
        super().__init__(message)
        self.line = line
        self.message = message


class EnvSchemaTool(Tool):
    """dotenv (``.env``) schema validation tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on each ``.env`` text input;
            longer inputs are rejected before any work.
        max_schema_vars (int): Upper bound on the number of variables
            a ``check``-mode schema may declare.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "env_schema_tool"
    description: str = (
        "Env schema tool — validate a dotenv (.env) payload against a "
        "declared schema of required variables and types, purely on the "
        "Python stdlib, no network required. check mode reports missing "
        "variables (with default-injection suggestions), applied "
        "defaults, undeclared extras, type mismatches (string|int|float|"
        "bool|url|email|path with documented coercion rules) and enum/"
        "min/max violations, masking values of secret-ish names "
        "(KEY/SECRET/PASSWORD/TOKEN) as *** (mode='check'); "
        "suggest_schema infers a ready-to-edit schema from an existing "
        ".env text (mode='suggest_schema'); diff compares two .env "
        "texts with the same masking rules (mode='diff')."
    )

    MODES: ClassVar[tuple] = ("check", "suggest_schema", "diff")

    max_text_chars: int = 100_000
    max_schema_vars: int = 1_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        schema: Any = None,
        text_b: Any = None,
    ) -> dict[str, Any]:
        """Run one .env schema operation.

        Args:
            mode (str): One of ``check`` / ``suggest_schema`` / ``diff``.
            text (str): The primary ``.env`` text (required for every
                mode; may be empty — an empty file against a schema is
                a meaningful check, and every declared variable comes
                back missing).
            schema (dict): The declared schema mapping variable name ->
                rule dict (``required`` / ``type`` / ``default`` /
                ``min`` / ``max`` / ``enum``) — required for ``check``,
                ignored by the other modes.
            text_b (str): The second ``.env`` text — required for
                ``diff`` (A = ``text``, B = ``text_b``), ignored by the
                other modes.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string plus the call context and mode-specific fields)
                or a structured ``error`` payload for content-level
                failures (unterminated quote with its line number).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens); schema-shape errors always name
                the offending variable.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "check":
            clean_text = self._validate_text(text)
            clean_schema = self._validate_schema(schema)
            return self._run_check(clean_text, clean_schema)
        if mode == "suggest_schema":
            clean_text = self._validate_text(text)
            return self._run_suggest(clean_text)
        clean_text = self._validate_text(text)
        clean_text_b = self._validate_text(text_b)
        return self._run_diff(clean_text, clean_text_b)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"env_schema_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any, label: str = "text") -> str:
        """Validate a ``.env`` text input (may be empty, must be str)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"{label} must be a string (got {text!r})")
        if len(text) > 100_000:
            cls._invalid(
                f"{label} exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_schema(cls, schema: Any) -> dict[str, dict[str, Any]]:
        """Validate the ``check``-mode schema shape, strictly.

        Every error names the offending variable so a broken rule can
        be located immediately. Returns the schema unchanged (values
        already checked to be well-formed rules).
        """
        if schema is None or isinstance(schema, bool) or not isinstance(
            schema, dict
        ):
            cls._invalid(
                f"schema must be a dict of variable name -> rule dict "
                f"(got {schema!r})"
            )
        if len(schema) > 1_000:
            cls._invalid(
                f"schema exceeds the {1_000:,}-variable limit "
                f"(got {len(schema):,} variables)"
            )
        for var, rule in schema.items():
            if var is None or isinstance(var, bool) or not isinstance(var, str):
                cls._invalid(
                    f"schema keys must be variable name strings (got {var!r})"
                )
            if not _KEY_RE.match(var):
                cls._invalid(
                    "schema keys must match [A-Za-z_][A-Za-z0-9_]* "
                    f"(got {var!r})"
                )
            if rule is None or isinstance(rule, bool) or not isinstance(
                rule, dict
            ):
                cls._invalid(
                    f"schema rule for {var!r} must be a dict (got {rule!r})"
                )
            cls._validate_rule(var, rule)
        return schema

    @classmethod
    def _validate_rule(cls, var: str, rule: dict[str, Any]) -> None:
        """Validate one ``var`` rule dict (unknown keys are errors)."""
        unknown = sorted(set(rule) - _RULE_KEYS - _INFO_KEYS)
        if unknown:
            cls._invalid(
                f"schema rule for {var!r} has unknown key(s) {unknown} "
                f"(allowed: {sorted(_RULE_KEYS)})"
            )
        declared_type = rule.get("type", "string")
        if declared_type not in TYPES:
            cls._invalid(
                f"schema rule for {var!r} declares unknown type "
                f"{declared_type!r} (allowed: {list(TYPES)})"
            )
        if "required" in rule and not isinstance(rule["required"], bool):
            cls._invalid(
                f"schema rule for {var!r}: required must be a boolean "
                f"(got {rule['required']!r})"
            )
        default = rule.get("default")
        if default is not None and (
            isinstance(default, bool) or not isinstance(default, str)
        ):
            cls._invalid(
                f"schema rule for {var!r}: default must be a string like "
                f"every dotenv value (got {default!r} — convert it with "
                f"str() first)"
            )
        min_value = rule.get("min")
        max_value = rule.get("max")
        for key, bound in (("min", min_value), ("max", max_value)):
            if bound is not None and (
                isinstance(bound, bool) or not isinstance(bound, (int, float))
            ):
                cls._invalid(
                    f"schema rule for {var!r}: {key} must be a number "
                    f"(got {bound!r})"
                )
        if min_value is not None or max_value is not None:
            if declared_type not in ("int", "float"):
                cls._invalid(
                    f"schema rule for {var!r}: min/max only apply to int "
                    f"or float types (type is {declared_type!r})"
                )
        if (
            min_value is not None
            and max_value is not None
            and min_value > max_value
        ):
            cls._invalid(
                f"schema rule for {var!r}: min {min_value!r} is greater "
                f"than max {max_value!r}"
            )
        enum_values = rule.get("enum")
        if enum_values is not None:
            if (
                isinstance(enum_values, (str, bytes))
                or not isinstance(enum_values, (list, tuple))
                or not enum_values
            ):
                cls._invalid(
                    f"schema rule for {var!r}: enum must be a non-empty "
                    f"list of allowed raw values (got {enum_values!r})"
                )
            for entry in enum_values:
                if entry is None or isinstance(entry, bool) or not isinstance(
                    entry, str
                ):
                    cls._invalid(
                        f"schema rule for {var!r}: enum entries must be "
                        f"strings (got {entry!r})"
                    )
            if len(set(enum_values)) != len(enum_values):
                cls._invalid(
                    f"schema rule for {var!r}: enum contains duplicate "
                    f"values (got {list(enum_values)!r})"
                )

    # ------------------------------------------------------------------ #
    # dotenv parsing (self-contained; mirrors EnvFileTool semantics)
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_env(cls, text: str) -> dict[str, Any]:
        """Parse ``.env`` text into the variable table the modes use.

        Returns ``{"variables": {name: record}, "malformed_lines":
        [...]}`` where each record carries the last-wins parsed
        ``value``, the winning occurrence ``line``, every occurrence
        ``lines`` and the distinct parsed ``values`` in first-seen
        order (the enum-inference signal). Raises
        :class:`_EnvParseError` on an unterminated quote.
        """
        variables: dict[str, dict[str, Any]] = {}
        malformed_lines: list[dict[str, Any]] = []
        physical = text.split("\n")
        if physical and physical[-1] == "":
            physical.pop()  # trailing newline is a terminator, not a line
        for line_number, original in enumerate(physical, start=1):
            stripped = original.strip()
            if not stripped or stripped.startswith("#"):
                continue
            match = _ASSIGN_RE.match(stripped)
            if match is None:
                malformed_lines.append(
                    {"line": line_number, "content": stripped}
                )
                continue
            var = match.group(1)
            value_portion = stripped[match.end() :]
            value = cls._parse_value(value_portion, line_number)
            record = variables.get(var)
            if record is None:
                variables[var] = {
                    "value": value,
                    "line": line_number,
                    "lines": [line_number],
                    "values": [value],
                }
            else:
                record["value"] = value  # last-wins
                record["lines"].append(line_number)
                if value not in record["values"]:
                    record["values"].append(value)
        return {"variables": variables, "malformed_lines": malformed_lines}

    @classmethod
    def _parse_value(cls, value_part: str, line_number: int) -> str:
        """Parse one raw value portion according to dotenv quote rules."""
        probe = value_part.lstrip()
        if probe.startswith('"'):
            return cls._read_double_quoted(probe, line_number)
        if probe.startswith("'"):
            end = probe.find("'", 1)
            if end < 0:
                raise _EnvParseError(
                    line_number, "unterminated single-quoted value"
                )
            return probe[1:end]
        # Unquoted: the value ends at the first '#' directly preceded
        # by whitespace (an inline comment); a '#' glued directly after
        # '=' or into text is data.
        cut = None
        for index in range(1, len(probe)):
            if probe[index] == "#" and probe[index - 1] in " \t":
                cut = index
                break
        data = probe if cut is None else probe[:cut]
        return data.strip()

    @classmethod
    def _read_double_quoted(cls, probe: str, line_number: int) -> str:
        """Read a double-quoted value: unescape \\n \\t \\r \\\\ \\"."""
        chars: list[str] = []
        index = 1
        length = len(probe)
        while index < length:
            char = probe[index]
            if char == "\\":
                if index + 1 >= length:
                    break  # dangling backslash before end of line
                escape = probe[index + 1]
                chars.append(_ESCAPES.get(escape, "\\" + escape))
                index += 2
                continue
            if char == '"':
                return "".join(chars)  # content after the quote is ignored
            chars.append(char)
            index += 1
        raise _EnvParseError(line_number, "unterminated double-quoted value")

    # ------------------------------------------------------------------ #
    # Secret masking / previews
    # ------------------------------------------------------------------ #

    @classmethod
    def _is_secret(cls, var: str) -> bool:
        """True when the variable name marks its value as secret-ish."""
        upper = var.upper()
        return any(marker in upper for marker in _SECRET_MARKERS)

    @classmethod
    def _display(cls, var: str, value: str) -> str:
        """Render a value for a report: mask or truncate a preview."""
        if cls._is_secret(var):
            return _MASK
        if len(value) > _PREVIEW_CHARS:
            return value[:_PREVIEW_CHARS] + "..."
        return value

    # ------------------------------------------------------------------ #
    # Type coercion / inference
    # ------------------------------------------------------------------ #

    @classmethod
    def _coerce(cls, declared_type: str, value: str) -> tuple[bool, Any]:
        """Try to coerce ``value`` to the declared type.

        Returns ``(True, coerced)`` on success — ``coerced`` is the
        string unchanged for ``string``/``url``/``email``/``path`` and
        a bool / int / float for the numeric types — or ``(False,
        None)`` when the value does not satisfy the type contract.
        """
        if declared_type == "string":
            return True, value
        if not value:
            return False, None  # every non-string type requires content
        if declared_type == "int":
            if _INT_RE.match(value):
                return True, int(value)
            return False, None
        if declared_type == "float":
            if _FLOAT_RE.match(value):
                return True, float(value)
            return False, None
        if declared_type == "bool":
            if value.lower() in _BOOL_WORDS:
                return True, value.lower() in ("true", "1", "yes")
            return False, None
        if declared_type == "url":
            return (True, value) if cls._is_url(value) else (False, None)
        if declared_type == "email":
            return (True, value) if cls._is_email(value) else (False, None)
        # path: non-empty, no ASCII control characters.
        if _CONTROL_RE.search(value):
            return False, None
        return True, value

    @classmethod
    def _infer_type(cls, value: str) -> str:
        """Infer the type of a value (never returns ``path``)."""
        if _INT_RE.match(value):
            return "int"
        if _FLOAT_RE.match(value):
            return "float"
        if value.lower() in _BOOL_WORDS:
            return "bool"
        if cls._is_url(value):
            return "url"
        if cls._is_email(value):
            return "email"
        return "string"

    @classmethod
    def _is_url(cls, value: str) -> bool:
        """A URL requires a valid scheme and a non-empty host."""
        try:
            parts = urlsplit(value)
        except ValueError:
            return False
        if not parts.scheme or not parts.netloc:
            return False
        return (
            bool(_SCHEME_RE.match(parts.scheme))
            and parts.hostname is not None
            and parts.hostname != ""
        )

    @classmethod
    def _is_email(cls, value: str) -> bool:
        """EmailValidatorTool-family profile: dot-atom local + labels.

        Quoted local parts and IP-literal domains are deliberately out
        of scope here — the full RFC 5322-lite profile (and its
        verdicts) is :class:`EmailValidatorTool`'s contract; a schema
        check only needs the ubiquitous dot-atom form.
        """
        if len(value) > _MAX_EMAIL_CHARS or value.count("@") != 1:
            return False
        local, domain = value.split("@")
        if not local or len(local) > _MAX_LOCAL_CHARS:
            return False
        if local.startswith(".") or local.endswith(".") or ".." in local:
            return False
        for segment in local.split("."):
            if not _ATEXT_RE.match(segment):
                return False
        labels = domain.split(".")
        if not labels:
            return False
        for label in labels:
            if not label or len(label) > _MAX_LABEL_CHARS:
                return False
            if not _DOMAIN_LABEL_RE.match(label):
                return False
            if label.startswith("-") or label.endswith("-"):
                return False
        return True

    # ------------------------------------------------------------------ #
    # Shared payload helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _context(cls, mode: str, **extra: Any) -> dict[str, Any]:
        """Build the call-context prefix shared by every payload."""
        return {"mode": mode, **extra}

    @classmethod
    def _parse_or_error(
        cls, context: dict[str, Any], text: str
    ) -> dict[str, Any]:
        """Parse env text; on an unterminated quote return the error payload.

        The result is either the parse record (``variables`` /
        ``malformed_lines``) or a payload carrying an ``error`` key —
        callers dispatch on ``"error" in parsed``.
        """
        try:
            return cls._parse_env(text)
        except _EnvParseError as exc:
            return {
                **context,
                "error": {
                    "type": "unterminated_quote",
                    "message": f"{exc.message} at line {exc.line}",
                },
            }

    # ------------------------------------------------------------------ #
    # check mode
    # ------------------------------------------------------------------ #

    def _run_check(
        self, text: str, schema: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """Validate the env text against the declared schema."""
        context = self._context("check", variables_declared=len(schema))
        parsed = self._parse_or_error(context, text)
        if "error" in parsed:
            return parsed
        variables: dict[str, dict[str, Any]] = parsed["variables"]

        missing: list[dict[str, Any]] = []
        applied_defaults: list[dict[str, Any]] = []
        type_mismatches: list[dict[str, Any]] = []
        violations: list[dict[str, Any]] = []
        failed = False

        for var, rule in schema.items():
            required = rule.get("required", True)
            declared_type = rule.get("type", "string")
            default = rule.get("default")
            record = variables.get(var)
            if record is None:
                # Every absent variable is reported in `missing`; the
                # suggestion is the paste-ready default-injection line
                # when the schema declares one (and the default then
                # becomes the effective, fully-checked value).
                missing.append(
                    {
                        "var": var,
                        "required": required,
                        "has_default": default is not None,
                        "suggestion": (
                            f"{var}={default}"
                            if default is not None
                            else f"{var}="
                        ),
                    }
                )
                if default is not None:
                    applied_defaults.append({"var": var, "default": default})
                    effective = default
                else:
                    if required:
                        failed = True
                    continue
            else:
                effective = record["value"]

            ok, coerced = self._coerce(declared_type, effective)
            if not ok:
                type_mismatches.append(
                    {
                        "var": var,
                        "expected": declared_type,
                        "got": self._infer_type(effective),
                        "raw_value_preview": self._display(var, effective),
                    }
                )
                failed = True
            elif declared_type in ("int", "float"):
                min_value = rule.get("min")
                max_value = rule.get("max")
                if min_value is not None and coerced < min_value:
                    violations.append(
                        {
                            "var": var,
                            "rule": "min",
                            "expected": min_value,
                            "got": self._display(var, str(coerced)),
                        }
                    )
                    failed = True
                if max_value is not None and coerced > max_value:
                    violations.append(
                        {
                            "var": var,
                            "rule": "max",
                            "expected": max_value,
                            "got": self._display(var, str(coerced)),
                        }
                    )
                    failed = True

            enum_values = rule.get("enum")
            if enum_values is not None and effective not in enum_values:
                violations.append(
                    {
                        "var": var,
                        "rule": "enum",
                        "expected": list(enum_values),
                        "got": self._display(var, effective),
                    }
                )
                failed = True

        extra: list[dict[str, Any]] = []
        for var, record in variables.items():
            if var in schema:
                continue
            lines = record["lines"]
            where = ", ".join(str(n) for n in lines)
            plural = "s" if len(lines) > 1 else ""
            extra.append(
                {
                    "var": var,
                    "lines": lines,
                    "note": (
                        f"defined at line{plural} {where}; not declared in "
                        f"the schema"
                    ),
                }
            )

        problems = []
        required_missing = sum(1 for entry in missing if entry["required"])
        if required_missing:
            problems.append(f"{required_missing} missing required")
        if type_mismatches:
            problems.append(f"{len(type_mismatches)} type mismatch(es)")
        if violations:
            problems.append(f"{len(violations)} violation(s)")

        return {
            **context,
            "result": (
                "passed" if not failed else "failed: " + "; ".join(problems)
            ),
            "passed": not failed,
            "missing": missing,
            "applied_defaults": applied_defaults,
            "extra": extra,
            "type_mismatches": type_mismatches,
            "violations": violations,
            "malformed_lines": parsed["malformed_lines"],
        }

    # ------------------------------------------------------------------ #
    # suggest_schema mode
    # ------------------------------------------------------------------ #

    def _run_suggest(self, text: str) -> dict[str, Any]:
        """Infer a check-compatible schema from the env text."""
        context = self._context("suggest_schema")
        parsed = self._parse_or_error(context, text)
        if "error" in parsed:
            return parsed
        variables: dict[str, dict[str, Any]] = parsed["variables"]

        suggested: dict[str, dict[str, Any]] = {}
        for var, record in variables.items():
            secret = self._is_secret(var)
            entry: dict[str, Any] = {
                "type": self._infer_type(record["value"]),
                "required": True,
                "sample_masked": (
                    _MASK if secret else self._display(var, record["value"])
                ),
            }
            # Enum inference: 2-4 distinct values across duplicate
            # occurrences (5+ is noise, 1 proves nothing). Secret-ish
            # variables never enumerate their observed values.
            if not secret and 2 <= len(record["values"]) <= 4:
                entry["inferred_enum"] = list(record["values"])
            suggested[var] = entry

        return {
            **context,
            "result": f"{len(suggested)} variable(s) inferred",
            "schema": suggested,
            "malformed_lines": parsed["malformed_lines"],
        }

    # ------------------------------------------------------------------ #
    # diff mode
    # ------------------------------------------------------------------ #

    def _run_diff(self, text_a: str, text_b: str) -> dict[str, Any]:
        """Compare two env texts (A = ``text``, B = ``text_b``)."""
        context = self._context("diff")
        parsed_a = self._parse_or_error(context, text_a)
        if "error" in parsed_a:
            return parsed_a
        parsed_b = self._parse_or_error(context, text_b)
        if "error" in parsed_b:
            return parsed_b
        vars_a: dict[str, dict[str, Any]] = parsed_a["variables"]
        vars_b: dict[str, dict[str, Any]] = parsed_b["variables"]

        only_in_a: list[dict[str, Any]] = []
        for var, record in vars_a.items():
            if var not in vars_b:
                only_in_a.append(
                    {"var": var, "value": self._display(var, record["value"])}
                )
        only_in_b: list[dict[str, Any]] = []
        for var, record in vars_b.items():
            if var not in vars_a:
                only_in_b.append(
                    {"var": var, "value": self._display(var, record["value"])}
                )
        value_diffs: list[dict[str, Any]] = []
        for var, record_a in vars_a.items():
            record_b = vars_b.get(var)
            if record_b is None or record_b["value"] == record_a["value"]:
                continue
            if self._is_secret(var):
                value_diffs.append(
                    {"var": var, "a": _MASK, "b": _MASK, "masked": True}
                )
            else:
                value_diffs.append(
                    {
                        "var": var,
                        "a": record_a["value"],
                        "b": record_b["value"],
                        "masked": False,
                    }
                )

        count = len(only_in_a) + len(only_in_b) + len(value_diffs)
        return {
            **context,
            "result": f"{count} difference(s)",
            "only_in_a": only_in_a,
            "only_in_b": only_in_b,
            "value_diffs": value_diffs,
            "count": count,
            "malformed_lines_a": parsed_a["malformed_lines"],
            "malformed_lines_b": parsed_b["malformed_lines"],
        }
