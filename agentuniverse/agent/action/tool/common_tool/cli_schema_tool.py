#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: cli_schema_tool.py

"""CLI argument-schema validation and usage generation — contract only,
never execution.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency command-line
*contract* layer an agent can call before handing an argument vector to
a program: does this ``argv`` match what the command ACCEPTS — its
flags, positionals, types and choices — and what would its usage line
look like?

The tool is the third member of the shell-argument family and builds
on the other two: ``CommandArgLexerTool`` *tokenizes* a command line
into ``argv`` (and classifies flags versus operands), and
``ContextEscapeTool`` *quotes* text for safe embedding into a shell.
Neither of them knows which arguments a command accepts; this tool is
that missing contract layer. A typical chain is
``CommandArgLexerTool.lex`` → ``CliSchemaTool.check``: split first,
then validate the words against the program's declared schema. Pure
standard library, no execution, no filesystem or network access — a
``path`` value is validated as *text* (see below), never opened.

Three modes, all deterministic:

* ``check`` — ``argv`` (program included as ``argv[0]``) + declared
  ``schema`` → structured verdict. The schema is a JSON-style dict::

      {"program": "grep",
       "arguments": [
         {"name": "color", "kind": "flag", "type": "string",
          "choices": ["auto", "always", "never"], "default": "auto"},
         {"name": "ignore-case", "kind": "flag", "alias": "i",
          "has_value": false},
         {"name": "count", "kind": "flag", "alias": "c",
          "type": "int", "multiple": true},
         {"name": "pattern", "kind": "positional", "type": "string"},
         {"name": "file", "kind": "positional", "type": "path",
          "required": false, "multiple": true}
       ],
       "epilog": "..."}

  Argument fields: ``name`` (``[A-Za-z][A-Za-z0-9_-]*``, unique,
  ``_args`` reserved), ``kind`` (``flag`` | ``positional``), ``type``
  (``string`` | ``int`` | ``float`` | ``bool`` | ``path``, default
  ``string``; switches are forced to ``bool``), ``required`` (flags
  default ``False``, positionals default ``True``), ``default``,
  ``choices`` (list of raw string tokens), ``has_value`` (flags only;
  default ``True`` — a flag takes a value unless declared a switch),
  ``alias`` (flags only; matched as ``-{alias}`` — single characters
  are the usual case, but a longer alias such as ``la`` may be
  declared for tools like ``ls -la``, and ``alias`` may equal the
  name so that both ``--name`` and ``-name`` match), ``multiple`` (a
  repeated flag
  collects a list / a trailing positional consumes the rest) and
  ``help`` (single-line usage text).

  The result is
  ``{"passed": bool, "parsed": {...}, "missing": [...],
  "unknown": [...], "type_mismatches": [...],
  "defaults_applied": [...], "separator_seen": bool}``:

  - Flags accept both value forms, ``--flag value`` and
    ``--flag=value`` (same for ``-{alias}``); a switch
    (``has_value=False``) takes no value and parses as ``True``
    (``--switch=value`` matches nothing and is reported unknown).
  - Short-flag *bundles are NOT expanded*: ``-abc`` is looked up as
    one token (alias ``abc``) and is *unknown* unless exactly that
    alias is declared. Single-character flags map to their long names
    through the ``alias`` field instead.
  - ``--`` terminates flag parsing; the remaining tokens fill
    declared positional slots in order and the overflow is collected
    under the reserved key ``parsed["_args"]`` (present only when
    non-empty). Stray extra positionals *before* ``--`` are reported
    as ``unknown`` tokens instead.
  - Repeated flags: last value wins, unless ``multiple=True`` which
    collects every occurrence into a list (an absent ``multiple``
    argument parses as ``[]``; an absent switch as ``False``).
  - Flag-like negative numbers are NOT flags: ``-5``, ``-3.14``,
    ``-.5``, ``-1e-3`` and the lone ``-`` (stdin marker) are
    positional values, and a value-taking flag consumes them from the
    next token (``--offset -5`` works).
  - A value-taking flag that finds no value — end of ``argv``, a
    following flag-like token or ``--`` — falls back to its declared
    ``default`` if it has one (the default is used only when no value
    was collected; it never overrides one), otherwise the flag name
    is reported in ``missing``.
  - Types follow the family rules: ``int`` / ``float`` / ``bool``
    coerce with the same regexes and boolean words
    (``true/false/1/0/yes/no``, case-insensitive) as
    ``EnvSchemaTool``; ``path`` requires a non-empty value with no
    ASCII control characters (text validation only, the path is never
    opened); ``string`` accepts anything. ``choices`` membership is
    checked on the raw token, before coercion.
  - ``missing`` holds required arguments that never received a value
    (and value-less flag occurrences); ``unknown`` holds tokens that
    matched no argument; each type or choices violation adds
    ``{"name", "expected", "got"}`` to ``type_mismatches``
    (``expected`` is the type name, or ``"one of: a, b"`` for
    choices). ``passed`` is ``True`` only when all three lists are
    empty; ``defaults_applied`` names arguments whose declared
    default was injected.

  ``argv[0]`` must match the declared ``program`` exactly or by
  basename (``/usr/bin/grep`` matches ``grep``); anything else is a
  structured ``error`` payload with ``passed=False``.

* ``usage`` — schema → the one-line usage string
  ``program [--flag VALUE] POS1 [POS2] ...`` (optional arguments in
  brackets, required ones bare, ``...`` after repeatable arguments,
  positional placeholders upper-cased) plus the full help text: the
  usage line, an ``arguments:`` section with one aligned
  per-argument line (label, optional ``help`` text, and a
  parenthesized summary of type / choices / default / required /
  multiple) and the schema's ``epilog`` when present.

* ``suggested_schema`` — a list of sample ``argv`` invocations
  (program included) → an inferred schema merged across the samples:
  the bootstrap mode. Flags are inferred value-taking when every
  occurrence carries a value, switches when none does; mixed
  occurrences without any ``--flag=value`` form infer a *switch* and
  their stray values become positionals (noted), while a mixed flag
  that ever used ``=`` stays value-taking and gets the first observed
  value injected as its default so value-less occurrences still
  validate (noted). Types are inferred with the family rules (never
  ``path``), ``choices`` when a string-typed argument shows 2–3
  distinct values, ``required`` when an argument appears in every
  sample, ``multiple`` when it repeats within one sample, and
  positionals are inferred per slot (``arg1``, ``arg2``, …) with the
  last slot repeatable when sample counts vary. Short-only tokens
  (``-v``, ``-la``) become arguments whose name is the token text
  with that alias set — correlating them with a separate long form is
  deliberately left to the human reviewing the suggestion. The
  suggestion is round-trip safe: every input sample passes ``check``
  against it.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, ``argv``/``samples`` not lists of
plain strings or empty where a program is required, NUL characters, a
``schema`` that is not a dict, unknown schema or argument keys,
missing ``program``/``name``/``kind``, bad names, aliases or types,
duplicate names or aliases, an alias colliding with an argument name,
``alias``/``has_value`` on positionals, a repeatable positional that
is not last, ``choices`` that is empty or contains non-strings or
duplicates, defaults that do not satisfy the declared type or
``choices``, ``required=True`` combined with a default, a switch with
a non-bool type or with ``choices``, multi-line ``help``, parameters
supplied to a mode that does not accept them, inputs over the size
caps) raise a ``ValueError``, mirroring the other common tools.
Errors that depend on the *content being processed* — a program token
that does not match the schema — are returned as a structured
``error`` payload so an agent can react without catching exceptions.
"""

import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# --------------------------------------------------------------------- #
# Family type rules (shared with EnvSchemaTool / CommandArgLexerTool)
# --------------------------------------------------------------------- #

_INT_RE = re.compile(r"[+-]?[0-9]+\Z")
_FLOAT_RE = re.compile(
    r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z"
)
_BOOL_TRUE = frozenset(("true", "1", "yes"))
_BOOL_WORDS = frozenset(("true", "false", "1", "0", "yes", "no"))
# ASCII control characters (C0 + DEL) — invalid in a declared path.
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
# Long names and aliases: must start with a letter (an alias like "5"
# would collide with negative-number tokens).
_NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]*\Z")

# Argument kinds, value types and the keys a schema may use.
KINDS = ("flag", "positional")
TYPES = ("string", "int", "float", "bool", "path")
_SCHEMA_KEYS = frozenset(("program", "arguments", "epilog"))
_ARGUMENT_KEYS = frozenset(
    ("name", "kind", "type", "required", "default", "choices",
     "has_value", "alias", "multiple", "help")
)
_RESERVED_NAME = "_args"

# Input size caps (module-level so classmethods can read them).
_MAX_PROGRAM_CHARS = 200
_MAX_NAME_CHARS = 64
_MAX_HELP_CHARS = 200
_MAX_EPILOG_CHARS = 500
_MAX_ARGUMENTS = 100
_MAX_CHOICES = 50
_MAX_ARGV_ITEMS = 10_000
_MAX_ARGV_TOTAL_CHARS = 100_000
_MAX_SAMPLES = 200


class CliSchemaTool(Tool):
    """CLI argument-schema checker / usage generator (no execution).

    Attributes:
        max_program_chars (int): Upper bound for the schema ``program``.
        max_arguments (int): Upper bound on schema arguments.
        max_choices (int): Upper bound on a ``choices`` list.
        max_argv_items (int): Upper bound on ``argv`` items.
        max_argv_total_chars (int): Upper bound on total ``argv`` chars.
        max_samples (int): Upper bound on ``samples`` for
            ``suggested_schema``.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "cli_schema_tool"
    description: str = (
        "CLI schema tool — validate an argv list against a declared "
        "command schema and generate usage text, pure Python stdlib, "
        "no network, no execution. mode='check' matches argv[1:] "
        "against the schema's flags (--flag value and --flag=value "
        "forms, short aliases without bundle expansion, -- terminator "
        "into _args, repeated/multiple flags, negative-number edge) "
        "and returns parsed values, missing/unknown/type-mismatch "
        "reports and a passed verdict; mode='usage' renders the "
        "one-line usage string plus per-argument help and epilog; "
        "mode='suggested_schema' infers a merged schema from sample "
        "invocations (the bootstrap mode, round-trip safe). "
        "Complements CommandArgLexerTool (tokenize) and "
        "ContextEscapeTool (quote): neither knows what a command "
        "ACCEPTS — this tool is that contract layer."
    )

    MODES: ClassVar[tuple] = ("check", "usage", "suggested_schema")

    max_program_chars: int = _MAX_PROGRAM_CHARS
    max_arguments: int = _MAX_ARGUMENTS
    max_choices: int = _MAX_CHOICES
    max_argv_items: int = _MAX_ARGV_ITEMS
    max_argv_total_chars: int = _MAX_ARGV_TOTAL_CHARS
    max_samples: int = _MAX_SAMPLES

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        argv: Any = None,
        schema: Any = None,
        samples: Any = None,
    ) -> Dict[str, Any]:
        """Run one schema operation.

        Args:
            mode (str): One of ``check`` / ``usage`` /
                ``suggested_schema``.
            argv (List[str]): The full argument vector including the
                program as ``argv[0]``; required for ``check``.
            schema (Dict[str, Any]): The declared command schema;
                required for ``check`` and ``usage``.
            samples (List[List[str]]): Sample argv invocations for
                schema inference; required for ``suggested_schema``.

        Returns:
            Dict[str, Any]: The verdict for ``check``, the usage line
                and help text for ``usage``, or the inferred schema
                for ``suggested_schema`` — or a structured ``error``
                payload for the program-mismatch content error.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "check":
            if schema is None:
                self._invalid("mode 'check' requires a schema")
            if samples is not None:
                self._invalid("samples is not accepted in mode 'check'")
            clean_argv = self._validate_argv(argv)
            program, arguments, _ = self._validate_schema(schema)
            return self._run_check(clean_argv, program, arguments)
        if mode == "usage":
            if argv is not None:
                self._invalid("argv is not accepted in mode 'usage'")
            if samples is not None:
                self._invalid("samples is not accepted in mode 'usage'")
            if schema is None:
                self._invalid("mode 'usage' requires a schema")
            program, arguments, epilog = self._validate_schema(schema)
            return self._run_usage(program, arguments, epilog)
        # suggested_schema
        if argv is not None:
            self._invalid("argv is not accepted in mode 'suggested_schema'")
        if schema is not None:
            self._invalid("schema is not accepted in mode 'suggested_schema'")
        clean_samples = self._validate_samples(samples)
        return self._run_suggested_schema(clean_samples)

    # ------------------------------------------------------------------ #
    # Input validation (strict — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"cli_schema_tool: {message}")

    @classmethod
    def _validate_argv(cls, argv: Any) -> List[str]:
        """Validate an argv list (non-empty, strings, no NUL, caps)."""
        if argv is None or isinstance(argv, (str, bool)) or not isinstance(argv, (list, tuple)):
            cls._invalid(f"argv must be a list of strings (got {argv!r})")
        if not argv:
            cls._invalid(
                "argv must include the program as argv[0] (got an empty list)"
            )
        if argv[0] == "":
            cls._invalid("argv[0] (the program) must not be empty")
        if len(argv) > _MAX_ARGV_ITEMS:
            cls._invalid(
                f"argv exceeds the {_MAX_ARGV_ITEMS:,}-item limit "
                f"(got {len(argv):,} items)"
            )
        total = 0
        for item in argv:
            if isinstance(item, bool) or not isinstance(item, str):
                cls._invalid(f"every argv item must be a string (got {item!r})")
            if "\x00" in item:
                cls._invalid("argv items must not contain NUL characters")
            total += len(item)
        if total > _MAX_ARGV_TOTAL_CHARS:
            cls._invalid(
                f"argv items total more than {_MAX_ARGV_TOTAL_CHARS:,} "
                f"characters (got {total:,})"
            )
        return list(argv)

    @classmethod
    def _validate_samples(cls, samples: Any) -> List[List[str]]:
        """Validate the ``samples`` input (suggested_schema mode)."""
        if samples is None or isinstance(samples, (str, bool)) or not isinstance(samples, (list, tuple)):
            cls._invalid(
                f"samples must be a list of argv lists (got {samples!r})"
            )
        if not samples:
            cls._invalid("samples must contain at least one invocation")
        if len(samples) > _MAX_SAMPLES:
            cls._invalid(
                f"samples exceeds the {_MAX_SAMPLES:,}-invocation limit "
                f"(got {len(samples):,})"
            )
        return [cls._validate_argv(sample) for sample in samples]

    @classmethod
    def _validate_schema(
        cls, schema: Any
    ) -> Tuple[str, List[Dict[str, Any]], Optional[str]]:
        """Validate the schema and normalize every argument.

        Returns ``(program, arguments, epilog)`` where each argument is
        normalized to all semantic fields.
        """
        if schema is None or isinstance(schema, (str, bool, list, tuple)) or not isinstance(schema, dict):
            cls._invalid(f"schema must be a dict (got {schema!r})")
        for key in schema:
            if key not in _SCHEMA_KEYS:
                cls._invalid(
                    f"unknown schema key {key!r} (allowed: "
                    f"{', '.join(sorted(_SCHEMA_KEYS))})"
                )
        program = schema.get("program")
        if program is None or isinstance(program, bool) or not isinstance(program, str):
            cls._invalid(f"schema program must be a string (got {program!r})")
        if not program or any(
            ch in " \t\r\n" or _CONTROL_RE.match(ch) for ch in program
        ):
            cls._invalid(
                "schema program must be a non-empty single token without "
                f"whitespace or control characters (got {program!r})"
            )
        if len(program) > _MAX_PROGRAM_CHARS:
            cls._invalid(
                f"schema program exceeds the {_MAX_PROGRAM_CHARS}-character "
                f"limit (got {len(program)} characters)"
            )
        epilog = schema.get("epilog")
        if epilog is not None:
            if isinstance(epilog, bool) or not isinstance(epilog, str):
                cls._invalid(
                    f"schema epilog must be a string (got {epilog!r})"
                )
            if len(epilog) > _MAX_EPILOG_CHARS:
                cls._invalid(
                    f"schema epilog exceeds the {_MAX_EPILOG_CHARS}-character "
                    f"limit (got {len(epilog)} characters)"
                )
        raw_arguments = schema.get("arguments", [])
        if raw_arguments is None:
            raw_arguments = []
        if isinstance(raw_arguments, bool) or not isinstance(raw_arguments, (list, tuple)):
            cls._invalid(
                f"schema arguments must be a list (got {raw_arguments!r})"
            )
        if len(raw_arguments) > _MAX_ARGUMENTS:
            cls._invalid(
                f"schema exceeds the {_MAX_ARGUMENTS}-argument limit "
                f"(got {len(raw_arguments)} arguments)"
            )
        arguments: List[Dict[str, Any]] = []
        seen_names: Dict[str, str] = {}
        seen_aliases: Dict[str, str] = {}
        for raw in raw_arguments:
            arguments.append(
                cls._validate_argument(raw, seen_names, seen_aliases)
            )
        for index, arg in enumerate(arguments):
            if arg["kind"] == "positional" and arg["multiple"] and index != len(arguments) - 1:
                cls._invalid(
                    f"positional {arg['name']!r} has multiple=true and must "
                    "be the last positional (it consumes every remaining "
                    "positional token)"
                )
        for arg in arguments:
            if (
                arg["alias"] is not None
                and arg["alias"] in seen_names
                and seen_names[arg["alias"]] != arg["name"]
            ):
                cls._invalid(
                    f"alias {arg['alias']!r} of argument {arg['name']!r} "
                    f"collides with the argument name of "
                    f"{seen_names[arg['alias']]!r}"
                )
        return program, arguments, epilog

    @classmethod
    def _validate_argument(
        cls, raw: Any, seen_names: Dict[str, str], seen_aliases: Dict[str, str]
    ) -> Dict[str, Any]:
        """Validate one schema argument and normalize its fields."""
        if raw is None or isinstance(raw, (str, bool, list, tuple)) or not isinstance(raw, dict):
            cls._invalid(
                f"every schema argument must be a dict (got {raw!r})"
            )
        for key in raw:
            if key not in _ARGUMENT_KEYS:
                cls._invalid(
                    f"unknown argument key {key!r} on argument "
                    f"{raw.get('name')!r} (allowed: "
                    f"{', '.join(sorted(_ARGUMENT_KEYS))})"
                )
        name = raw.get("name")
        if name is None:
            cls._invalid(f"argument is missing its name (got {raw!r})")
        if isinstance(name, bool) or not isinstance(name, str) or not _NAME_RE.fullmatch(name):
            cls._invalid(
                f"argument name must match [A-Za-z][A-Za-z0-9_-]* (got {name!r})"
            )
        if len(name) > _MAX_NAME_CHARS:
            cls._invalid(
                f"argument name exceeds the {_MAX_NAME_CHARS}-character "
                f"limit (got {len(name)} characters)"
            )
        if name == _RESERVED_NAME:
            cls._invalid("argument name '_args' is reserved")
        if name in seen_names:
            cls._invalid(
                f"duplicate argument name {name!r} (already used by the "
                f"{seen_names[name]!r} argument)"
            )
        kind = raw.get("kind")
        if kind is None:
            cls._invalid(
                f"argument {name!r} is missing its kind (flag or positional)"
            )
        if kind not in KINDS:
            cls._invalid(
                f"argument {name!r} kind must be 'flag' or 'positional' "
                f"(got {kind!r})"
            )

        has_value = raw.get("has_value")
        alias = raw.get("alias")
        if kind == "positional":
            if has_value is not None:
                cls._invalid(
                    f"positional {name!r} cannot declare has_value (only "
                    "flags can)"
                )
            if alias is not None:
                cls._invalid(
                    f"positional {name!r} cannot declare an alias (only "
                    "flags can)"
                )
            has_value = True
            alias = None
        else:
            if has_value is None:
                has_value = True
            if not isinstance(has_value, bool):
                cls._invalid(
                    f"argument {name!r} has_value must be a boolean "
                    f"(got {has_value!r})"
                )
            if alias is not None:
                if isinstance(alias, bool) or not isinstance(alias, str) or not _NAME_RE.fullmatch(alias):
                    cls._invalid(
                        f"argument {name!r} alias must match "
                        f"[A-Za-z][A-Za-z0-9_-]* (got {alias!r})"
                    )
                if len(alias) > _MAX_NAME_CHARS:
                    cls._invalid(
                        f"argument {name!r} alias exceeds the "
                        f"{_MAX_NAME_CHARS}-character limit"
                    )
                # alias == name is allowed: it makes both --name and
                # -name match, which is exactly what a short-only flag
                # (ls -la) needs.
                if alias in seen_aliases:
                    cls._invalid(
                        f"duplicate alias {alias!r} (already used by the "
                        f"{seen_aliases[alias]!r} argument)"
                    )
                seen_aliases[alias] = name

        declared_type = raw.get("type")
        if declared_type is None:
            declared_type = "bool" if has_value is False else "string"
        if declared_type not in TYPES:
            cls._invalid(
                f"argument {name!r} type must be one of: {', '.join(TYPES)} "
                f"(got {declared_type!r})"
            )
        if has_value is False and declared_type != "bool":
            cls._invalid(
                f"switch {name!r} (has_value=false) must declare type 'bool' "
                f"or omit type (got {raw.get('type')!r})"
            )

        required = raw.get("required")
        if required is None:
            required = kind == "positional"
        if not isinstance(required, bool):
            cls._invalid(
                f"argument {name!r} required must be a boolean "
                f"(got {required!r})"
            )

        multiple = raw.get("multiple", False)
        if not isinstance(multiple, bool):
            cls._invalid(
                f"argument {name!r} multiple must be a boolean "
                f"(got {multiple!r})"
            )

        choices = raw.get("choices")
        if choices is not None:
            if has_value is False:
                cls._invalid(
                    f"switch {name!r} cannot declare choices (it takes no "
                    "value)"
                )
            if isinstance(choices, bool) or not isinstance(choices, (list, tuple)):
                cls._invalid(
                    f"argument {name!r} choices must be a list of strings "
                    f"(got {choices!r})"
                )
            if not choices:
                cls._invalid(
                    f"argument {name!r} choices must not be empty (declare "
                    "at least one allowed token)"
                )
            if len(choices) > _MAX_CHOICES:
                cls._invalid(
                    f"argument {name!r} exceeds the {_MAX_CHOICES}-choice "
                    f"limit (got {len(choices)} choices)"
                )
            seen_choices = set()
            for choice in choices:
                if isinstance(choice, bool) or not isinstance(choice, str):
                    cls._invalid(
                        f"every choice of {name!r} must be a string (got "
                        f"{choice!r}; choices are matched against raw tokens)"
                    )
                if choice in seen_choices:
                    cls._invalid(
                        f"duplicate choice {choice!r} in argument {name!r}"
                    )
                seen_choices.add(choice)
            choices = list(choices)

        default = raw.get("default")
        if default is not None:
            if required:
                cls._invalid(
                    f"argument {name!r} is required and cannot also declare "
                    "a default (a required argument can never be absent)"
                )
            cls._validate_default(
                name, declared_type, default, choices, multiple
            )

        help_text = raw.get("help")
        if help_text is not None:
            if isinstance(help_text, bool) or not isinstance(help_text, str):
                cls._invalid(
                    f"argument {name!r} help must be a string "
                    f"(got {help_text!r})"
                )
            if len(help_text) > _MAX_HELP_CHARS:
                cls._invalid(
                    f"argument {name!r} help exceeds the "
                    f"{_MAX_HELP_CHARS}-character limit"
                )
            if "\n" in help_text or "\r" in help_text:
                cls._invalid(f"argument {name!r} help must be a single line")

        seen_names[name] = name
        return {
            "name": name,
            "kind": kind,
            "type": declared_type,
            "required": required,
            "default": default,
            "choices": choices,
            "has_value": has_value,
            "alias": alias,
            "multiple": multiple,
            "help": help_text,
        }

    @classmethod
    def _validate_default(
        cls,
        name: str,
        declared_type: str,
        default: Any,
        choices: Optional[List[str]],
        multiple: bool,
    ) -> None:
        """Validate a declared default against the type and choices."""

        def check_scalar(value: Any) -> None:
            if declared_type == "string":
                if isinstance(value, bool) or not isinstance(value, str):
                    cls._invalid(
                        f"default of string argument {name!r} must be a "
                        f"string (got {value!r})"
                    )
            elif declared_type == "int":
                if isinstance(value, bool) or not isinstance(value, int):
                    cls._invalid(
                        f"default of int argument {name!r} must be an int "
                        f"(got {value!r})"
                    )
            elif declared_type == "float":
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    cls._invalid(
                        f"default of float argument {name!r} must be a float "
                        f"or int (got {value!r})"
                    )
            elif declared_type == "bool":
                if not isinstance(value, bool):
                    cls._invalid(
                        f"default of bool argument {name!r} must be a "
                        f"boolean (got {value!r})"
                    )
            else:  # path
                if isinstance(value, bool) or not isinstance(value, str):
                    cls._invalid(
                        f"default of path argument {name!r} must be a string "
                        f"(got {value!r})"
                    )
                if not value or _CONTROL_RE.search(value):
                    cls._invalid(
                        f"default of path argument {name!r} must be a "
                        "non-empty value without control characters"
                    )
            if choices is not None and cls._render_scalar(value) not in choices:
                cls._invalid(
                    f"default of argument {name!r} must be one of its "
                    f"choices (got {cls._render_scalar(value)!r}; choices: "
                    f"{', '.join(choices)})"
                )

        if multiple:
            if isinstance(default, bool) or not isinstance(default, (list, tuple)):
                cls._invalid(
                    f"default of multiple argument {name!r} must be a list "
                    f"(got {default!r})"
                )
            for item in default:
                check_scalar(item)
        else:
            check_scalar(default)

    # ------------------------------------------------------------------ #
    # Shared helpers (types, tokens)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _render_scalar(value: Any) -> str:
        """Render a scalar for choices comparison and usage text."""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            return value
        return str(value)

    @classmethod
    def _coerce(cls, declared_type: str, raw: str) -> Tuple[bool, Any]:
        """Coerce one raw token to the declared type (family rules).

        Returns ``(True, value)`` or ``(False, None)`` — ``string``
        accepts anything (including the empty string); every other
        type requires content.
        """
        if declared_type == "string":
            return True, raw
        if not raw:
            return False, None
        if declared_type == "int":
            if _INT_RE.match(raw):
                return True, int(raw)
            return False, None
        if declared_type == "float":
            if _FLOAT_RE.match(raw):
                return True, float(raw)
            return False, None
        if declared_type == "bool":
            lowered = raw.lower()
            if lowered in _BOOL_WORDS:
                return True, lowered in _BOOL_TRUE
            return False, None
        # path: non-empty, no ASCII control characters (text only).
        if _CONTROL_RE.search(raw):
            return False, None
        return True, raw

    @staticmethod
    def _is_valueish(token: str) -> bool:
        """Could this token be a flag VALUE (space form)?

        Anything not starting with ``-``, the lone ``-`` stdin marker,
        or a token that parses as a negative number — the flag-like
        negative-number edge.
        """
        if not token.startswith("-"):
            return True
        if token == "-":
            return True
        return bool(_INT_RE.match(token) or _FLOAT_RE.match(token))

    @staticmethod
    def _basename(program_token: str) -> str:
        """The program token's basename (segment after the last /)."""
        head = program_token.rsplit("/", 1)[-1]
        return head if head else program_token

    @staticmethod
    def _content_error(expected: str, got: str) -> Dict[str, Any]:
        """Build the structured program-mismatch error payload."""
        return {
            "type": "program_mismatch",
            "message": (
                f"argv[0] {got!r} does not match the declared program "
                f"{expected!r} (exact or basename match required)"
            )[:500],
            "expected": expected,
            "got": got,
        }

    # ------------------------------------------------------------------ #
    # check mode
    # ------------------------------------------------------------------ #

    def _run_check(
        self, argv: List[str], program: str, arguments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Match argv[1:] against the declared schema."""
        context = {"mode": "check"}
        program_token = argv[0]
        if program_token != program and self._basename(program_token) != program:
            return {
                **context,
                "error": self._content_error(program, program_token),
                "passed": False,
            }
        by_long = {
            f"--{arg['name']}": arg for arg in arguments if arg["kind"] == "flag"
        }
        by_alias = {
            f"-{arg['alias']}": arg
            for arg in arguments
            if arg["kind"] == "flag" and arg["alias"] is not None
        }
        positionals = [arg for arg in arguments if arg["kind"] == "positional"]

        flag_state: Dict[str, Dict[str, Any]] = {
            arg["name"]: {
                "good": [],          # successfully coerced values
                "any_value": False,  # an occurrence consumed a value token
                "switch_seen": 0,    # switch occurrences
                "valueless": False,  # an occurrence found no value at all
                "default_needed": False,  # a valueless occurrence
            }
            for arg in arguments if arg["kind"] == "flag"
        }
        pos_good: Dict[str, List[Any]] = {arg["name"]: [] for arg in positionals}
        pos_attempted: Dict[str, bool] = {arg["name"]: False for arg in positionals}
        unknown: List[str] = []
        mismatches: List[Dict[str, Any]] = []
        extra_args: List[str] = []
        separator_seen = False

        def record_value(arg: Dict[str, Any], raw: str) -> None:
            """Choices-check then coerce one value token for ``arg``."""
            state = flag_state[arg["name"]]
            state["any_value"] = True
            if arg["choices"] is not None and raw not in arg["choices"]:
                mismatches.append({
                    "name": arg["name"],
                    "expected": "one of: " + ", ".join(arg["choices"]),
                    "got": raw,
                })
                return
            ok, value = self._coerce(arg["type"], raw)
            if not ok:
                mismatches.append({
                    "name": arg["name"],
                    "expected": arg["type"],
                    "got": raw,
                })
                return
            state["good"].append(value)

        pointer = 0
        tokens = argv[1:]
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if separator_seen:
                # After --: every token is positional data; overflow
                # lands in _args instead of being reported unknown.
                if pointer < len(positionals):
                    self._fill_positional(
                        positionals[pointer], token, pos_good,
                        pos_attempted, mismatches,
                    )
                    if not positionals[pointer]["multiple"]:
                        pointer += 1
                else:
                    extra_args.append(token)
                i += 1
                continue
            if token == "--":
                separator_seen = True
                i += 1
                continue

            matched = None
            value: Optional[str] = None
            have_value = False
            eq = False
            if token.startswith("--") and len(token) > 2:
                name_part, eq, value_part = token[2:].partition("=")
                matched = by_long.get("--" + name_part)
                if matched is not None and eq:
                    value, have_value = value_part, True
            elif (
                token.startswith("-") and len(token) > 1 and token != "-"
                and not _INT_RE.match(token) and not _FLOAT_RE.match(token)
            ):
                alias_part, eq, value_part = token[1:].partition("=")
                matched = by_alias.get("-" + alias_part)
                if matched is not None and eq:
                    value, have_value = value_part, True

            if matched is None:
                if (
                    token.startswith("-") and len(token) > 1 and token != "-"
                    and not _INT_RE.match(token)
                    and not _FLOAT_RE.match(token)
                ):
                    # A flag-like token that matched nothing: unknown
                    # flags, unexpanded bundles like -abc, long forms
                    # with no declared argument, --switch=value.
                    unknown.append(token)
                elif pointer < len(positionals):
                    self._fill_positional(
                        positionals[pointer], token, pos_good,
                        pos_attempted, mismatches,
                    )
                    if not positionals[pointer]["multiple"]:
                        pointer += 1
                else:
                    unknown.append(token)
                i += 1
                continue

            # A declared flag was matched.
            if matched["has_value"] is False:
                if eq:
                    # --switch=value / -s=value matches no argument form.
                    unknown.append(token)
                else:
                    flag_state[matched["name"]]["switch_seen"] += 1
                i += 1
                continue
            if not have_value:
                # Space form: the next token, when value-ish, is the value.
                if i + 1 < len(tokens) and self._is_valueish(tokens[i + 1]):
                    value = tokens[i + 1]
                    i += 2
                else:
                    state = flag_state[matched["name"]]
                    state["valueless"] = True
                    if matched["default"] is not None:
                        state["default_needed"] = True
                    i += 1
                    continue
            else:
                i += 1
            record_value(matched, value)

        # ---- assemble the verdict ------------------------------------- #
        parsed: Dict[str, Any] = {}
        missing: List[str] = []
        defaults_applied: List[str] = []
        for arg in arguments:
            name = arg["name"]
            state = flag_state.get(name)
            if state is not None:
                present = state["any_value"] or state["switch_seen"] > 0
                if arg["required"] and not present and not state["default_needed"]:
                    missing.append(name)
                if state["valueless"] and name not in missing and not state["default_needed"]:
                    missing.append(name)
                if state["switch_seen"] > 0:
                    parsed[name] = (
                        [True] * state["switch_seen"]
                        if arg["multiple"] else True
                    )
                elif state["good"]:
                    parsed[name] = (
                        list(state["good"]) if arg["multiple"]
                        else state["good"][-1]
                    )
                elif state["default_needed"] or not present:
                    if arg["default"] is not None:
                        parsed[name] = arg["default"]
                        defaults_applied.append(name)
                    elif arg["multiple"]:
                        parsed[name] = []
                    elif arg["has_value"] is False:
                        parsed[name] = False
                continue
            # Positional.
            good = pos_good[name]
            if good:
                parsed[name] = good if arg["multiple"] else good[0]
            elif arg["default"] is not None:
                parsed[name] = arg["default"]
                defaults_applied.append(name)
            elif arg["required"] and not pos_attempted[name]:
                missing.append(name)
        if extra_args:
            parsed[_RESERVED_NAME] = extra_args
        passed = not (missing or unknown or mismatches)
        return {
            **context,
            "passed": passed,
            "parsed": parsed,
            "missing": missing,
            "unknown": unknown,
            "type_mismatches": mismatches,
            "defaults_applied": defaults_applied,
            "separator_seen": separator_seen,
        }

    def _fill_positional(
        self,
        slot: Dict[str, Any],
        raw: str,
        pos_good: Dict[str, List[Any]],
        pos_attempted: Dict[str, bool],
        mismatches: List[Dict[str, Any]],
    ) -> None:
        """Choices-check then coerce one positional token into its slot."""
        pos_attempted[slot["name"]] = True
        if slot["choices"] is not None and raw not in slot["choices"]:
            mismatches.append({
                "name": slot["name"],
                "expected": "one of: " + ", ".join(slot["choices"]),
                "got": raw,
            })
            return
        ok, value = self._coerce(slot["type"], raw)
        if not ok:
            mismatches.append({
                "name": slot["name"],
                "expected": slot["type"],
                "got": raw,
            })
            return
        pos_good[slot["name"]].append(value)

    # ------------------------------------------------------------------ #
    # usage mode
    # ------------------------------------------------------------------ #

    def _run_usage(
        self,
        program: str,
        arguments: List[Dict[str, Any]],
        epilog: Optional[str],
    ) -> Dict[str, Any]:
        """Render the usage line and the full help text."""
        parts = [program]
        for arg in arguments:
            if arg["kind"] != "flag":
                continue
            piece = "--" + arg["name"]
            if arg["has_value"]:
                piece += " VALUE"
            if arg["multiple"]:
                piece += " ..."
            parts.append(piece if arg["required"] else f"[{piece}]")
        for arg in arguments:
            if arg["kind"] != "positional":
                continue
            piece = arg["name"].upper()
            if arg["multiple"]:
                piece += " ..."
            parts.append(piece if arg["required"] else f"[{piece}]")
        usage_line = " ".join(parts)

        lines: List[str] = []
        if arguments:
            labels = []
            for arg in arguments:
                if arg["kind"] == "flag":
                    label = "--" + arg["name"]
                    if arg["has_value"]:
                        label += " VALUE"
                    if arg["alias"] is not None:
                        label += f", -{arg['alias']}"
                else:
                    label = arg["name"].upper()
                    if arg["multiple"]:
                        label += " ..."
                labels.append(label)
            width = max(len(label) for label in labels) + 2
            for arg, label in zip(arguments, labels):
                attrs = [f"type: {arg['type']}"]
                if arg["choices"] is not None:
                    attrs.append("choices: " + "|".join(arg["choices"]))
                if arg["default"] is not None and not (
                    arg["has_value"] is False and arg["default"] is False
                ):
                    attrs.append(
                        "default: " + self._render_default(arg["default"])
                    )
                if arg["required"]:
                    attrs.append("required")
                if arg["multiple"]:
                    attrs.append("multiple")
                annotation = "(" + ", ".join(attrs) + ")"
                if arg["help"]:
                    annotation = arg["help"] + " " + annotation
                lines.append("  " + label.ljust(width) + annotation)
        sections = [usage_line]
        if lines:
            sections.append("arguments:\n" + "\n".join(lines))
        if epilog:
            sections.append(epilog)
        help_text = "\n\n".join(sections)
        return {"mode": "usage", "usage": usage_line, "help_text": help_text}

    @staticmethod
    def _render_default(default: Any) -> str:
        """Render a default (scalar or list) for the help text."""
        if isinstance(default, (list, tuple)):
            return "[" + ", ".join(
                CliSchemaTool._render_scalar(item) for item in default
            ) + "]"
        return CliSchemaTool._render_scalar(default)

    # ------------------------------------------------------------------ #
    # suggested_schema mode
    # ------------------------------------------------------------------ #

    def _run_suggested_schema(
        self, samples: List[List[str]]
    ) -> Dict[str, Any]:
        """Infer a merged schema from sample invocations."""
        program = self._basename(samples[0][0])
        for sample in samples:
            if self._basename(sample[0]) != program:
                self._invalid(
                    "samples disagree on the program: "
                    f"{samples[0][0]!r} vs {sample[0]!r} (every sample's "
                    "argv[0] must share the same basename)"
                )

        # Pass 1 — classify every flag token with greedy value
        # consumption to collect per-name occurrence statistics.
        stats: Dict[str, Dict[str, Any]] = {}  # name -> merged statistics
        name_order: List[str] = []
        for sample in samples:
            tokens = sample[1:]
            per_name_counts: Dict[str, int] = {}
            i = 0
            separator = False
            while i < len(tokens):
                token = tokens[i]
                if separator:
                    i += 1
                    continue
                if token == "--":
                    separator = True
                    i += 1
                    continue
                name = None
                is_alias = False
                value = None
                eq = False
                if token.startswith("--") and len(token) > 2:
                    name_part, eq, value_part = token[2:].partition("=")
                    name = name_part
                    if eq:
                        value = value_part
                elif (
                    token.startswith("-") and len(token) > 1 and token != "-"
                    and not _INT_RE.match(token) and not _FLOAT_RE.match(token)
                ):
                    alias_part, eq, value_part = token[1:].partition("=")
                    name = alias_part
                    is_alias = True
                    if eq:
                        value = value_part
                if name is None:
                    i += 1
                    continue
                if value is None and i + 1 < len(tokens) and self._is_valueish(tokens[i + 1]):
                    value = tokens[i + 1]
                    i += 1
                if name not in stats:
                    stats[name] = {
                        "eq": False, "values": [], "per_sample": [],
                        "alias": None, "order": len(name_order),
                    }
                    name_order.append(name)
                if is_alias:
                    stats[name]["alias"] = name
                per_name_counts[name] = per_name_counts.get(name, 0) + 1
                if eq:
                    stats[name]["eq"] = True
                if value is not None:
                    stats[name]["values"].append(value)
                i += 1
            for name, count in per_name_counts.items():
                stats[name]["per_sample"].append(count)

        # Decide has_value per name, then build the flag arguments.
        notes: List[str] = []
        flag_args: List[Dict[str, Any]] = []
        has_value_map: Dict[str, bool] = {}
        for name in name_order:
            entry = stats[name]
            occurrence_count = sum(entry["per_sample"])
            with_value = len(entry["values"])
            if occurrence_count > 0 and with_value >= occurrence_count:
                has_value = True
            elif with_value == 0:
                has_value = False
            elif entry["eq"]:
                # Ever used --name=value: value-taking, with the first
                # observed value injected as the default so value-less
                # occurrences still validate.
                has_value = True
                notes.append(
                    f"flag --{name}: occurrences disagree on taking a "
                    f"value; default {entry['values'][0]!r} inferred so "
                    "value-less occurrences fall back to it — review"
                )
            else:
                # Mixed without any '=' form: infer a switch; the stray
                # values become positional tokens (pass 2 reclassifies).
                has_value = False
                notes.append(
                    f"flag --{name}: some occurrences carry no value; "
                    "inferred as a switch and their values re-absorbed as "
                    "positionals — review"
                )
            has_value_map[name] = has_value
            required = len(entry["per_sample"]) == len(samples)
            multiple = any(count >= 2 for count in entry["per_sample"])
            arg: Dict[str, Any] = {
                "name": name,
                "kind": "flag",
                "type": self._infer_type(entry["values"]) if has_value else "bool",
                "required": required,
                "has_value": has_value,
            }
            if entry["alias"] is not None:
                arg["alias"] = entry["alias"]
            if multiple:
                arg["multiple"] = True
            if has_value:
                if entry["eq"] and with_value < occurrence_count:
                    # The rescue default: coerced to the inferred type so
                    # the suggestion is itself a valid schema, and the
                    # argument becomes optional (a defaulted flag is
                    # never required).
                    arg["default"] = self._coerce(
                        arg["type"], entry["values"][0]
                    )[1]
                    arg["required"] = False
                choices = self._infer_choices(arg["type"], entry["values"])
                if choices is not None:
                    arg["choices"] = choices
            flag_args.append(arg)

        # Pass 2 — re-walk with the final has_value decisions to
        # collect the residual positional token streams.
        positional_streams = [
            self._residual_positionals(sample[1:], has_value_map)
            for sample in samples
        ]
        max_len = max((len(stream) for stream in positional_streams), default=0)
        distinct_lengths = {len(stream) for stream in positional_streams}
        positional_args: List[Dict[str, Any]] = []
        used_names = {arg["name"] for arg in flag_args}
        for index in range(max_len):
            slot_name = f"arg{index + 1}"
            while slot_name in used_names:
                slot_name += "_"
            used_names.add(slot_name)
            values = [
                stream[index] for stream in positional_streams
                if index < len(stream)
            ]
            is_last = index == max_len - 1
            arg = {
                "name": slot_name,
                "kind": "positional",
                "type": self._infer_type(values),
                "required": len(values) == len(samples),
            }
            if is_last and len(distinct_lengths) > 1 and max_len >= 2:
                arg["multiple"] = True
            choices = self._infer_choices(arg["type"], values)
            if choices is not None:
                arg["choices"] = choices
            positional_args.append(arg)

        arguments = flag_args + positional_args
        return {
            "mode": "suggested_schema",
            "program": program,
            "schema": {"program": program, "arguments": arguments},
            "notes": notes,
        }

    def _residual_positionals(
        self, tokens: List[str], has_value_map: Dict[str, bool]
    ) -> List[str]:
        """Walk one sample with final flag semantics; return bare tokens.

        Value-taking flags consume the next value-ish token (or just
        themselves when none follows); switches stand alone; everything
        else — including every token after ``--`` — is positional.
        """
        residual: List[str] = []
        separator = False
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if separator:
                residual.append(token)
                i += 1
                continue
            if token == "--":
                separator = True
                i += 1
                continue
            name = None
            eq = False
            if token.startswith("--") and len(token) > 2:
                name_part, eq, _value = token[2:].partition("=")
                name = name_part
            elif (
                token.startswith("-") and len(token) > 1 and token != "-"
                and not _INT_RE.match(token) and not _FLOAT_RE.match(token)
            ):
                alias_part, eq, _value = token[1:].partition("=")
                name = alias_part
            if name is not None:
                if eq or not has_value_map.get(name, False):
                    # --name=value consumed here; a switch stands alone.
                    i += 1
                    continue
                if i + 1 < len(tokens) and self._is_valueish(tokens[i + 1]):
                    i += 2
                    continue
                i += 1
                continue
            residual.append(token)
            i += 1
        return residual

    @classmethod
    def _infer_type(cls, values: List[str]) -> str:
        """Infer a type from observed raw values (never ``path``)."""
        if values and all(_INT_RE.match(v) for v in values):
            return "int"
        if values and all(
            _INT_RE.match(v) or _FLOAT_RE.match(v) for v in values
        ):
            return "float"
        if values and all(v.lower() in _BOOL_WORDS for v in values):
            return "bool"
        return "string"

    @staticmethod
    def _infer_choices(
        inferred_type: str, values: List[str]
    ) -> Optional[List[str]]:
        """choices when a string-typed argument shows 2-3 distinct values."""
        if inferred_type != "string":
            return None
        distinct: List[str] = []
        for value in values:
            if value not in distinct:
                distinct.append(value)
        if 2 <= len(distinct) <= 3:
            return distinct
        return None
