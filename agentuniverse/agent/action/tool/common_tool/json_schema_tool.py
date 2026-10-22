#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: json_schema_tool.py

"""JSON *Schema* validation tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with the schema layer for JSON documents: given a
document and a schema, answer "does this document have the required
fields with the right types, ranges, patterns and enums?" — the
question neither ``JsonPathTool`` (#3477, *query* values out of a
document) nor ``JsonPatchTool`` (#4004, *mutate* a document) ask, and
one a plain required-keys checker cannot answer once constraints go
deeper than the top level. Three modes, all offline and deterministic:

* ``validate`` — check ``document`` (a native JSON value, or a string
  parsed as JSON text) against ``schema`` (a draft 2020-12 *subset*
  schema; the honest scope is documented below). The payload reports:

  - ``valid`` — ``False`` exactly when ``errors`` is non-empty.
  - ``errors`` — ``[{path, schema_rule, message, actual}]`` where
    ``path`` is a dot-path with ``[index]`` for array elements
    (``""`` = the root, ``user.email``, ``tags[2].id``),
    ``schema_rule`` names the violated keyword (``type``,
    ``required``, ``minLength``, ``pattern``, ``format``, ``enum``,
    ``const``, ``additionalProperties``, ``uniqueItems``, ...) and
    ``actual`` carries the offending value (the JSON *type name* for
    type errors, the value itself otherwise — truncated to 120
    characters, and ``***`` when the path's property name is
    secret-ish; see masking below).
  - ``applied_rules`` — how many keyword assertions were evaluated
    against matching instance types (passed or failed); container
    keywords (``properties`` / ``items`` / ``$ref``) count through
    their children, ``required`` counts once per evaluated list.
  - ``unsupported_keywords`` — ``[{keyword, path, note}]`` for every
    keyword outside the subset (``anyOf`` / ``allOf`` / ``oneOf`` /
    ``not`` / ``patternProperties`` / ``multipleOf`` / ...), with the
    JSON-pointer-style schema location (``#/properties/user``).
    Unsupported keywords are *tolerated*: they are skipped — the rest
    of the schema is still fully validated — and never crash.
  - ``defaults_declared`` — ``[{schema_path, default}]`` for every
    ``default`` found while checking the schema. ``default`` is
    report-only: it is never applied to the document (JSON Schema
    treats it as an annotation), so a missing property stays missing
    even when a default exists.
  - ``truncated`` — present and ``True`` when the error list hit the
    cap (``max_errors``, default 200) and further errors were dropped.

* ``infer_schema`` — the bootstrap mode: infer a skeleton *subset*
  schema from a document. Objects yield ``type`` / ``properties`` /
  ``required`` (all observed keys required), arrays yield ``type`` /
  ``items`` (the merged schema of the elements — identical element
  schemas are kept verbatim, uniform objects merge by
  union-of-properties / intersection-of-required, anything else
  collapses to a bare type union), scalars yield their type, and
  strings additionally get a ``format`` when they match the family
  date / date-time / uuid / email / ipv4 / url profiles. Every scalar
  node carries ``examples`` (one sample, truncated to 24 characters)
  so the skeleton is reviewable — except under secret-ish keys, where
  the example is ``***``. ``validate(infer_schema(d), d)`` is valid
  for every document ``d`` (asserted by tests over 200 seeded
  documents).

* ``simplify_errors`` — condense a long ``errors`` list (the exact
  shape ``validate`` emits) into a grouped-by-path summary:
  ``groups`` (``[{path, count, rules, messages}]``, highest count
  first then by path, messages deduplicated), ``rule_totals`` (error
  count per keyword) and ``unparseable`` (entries that do not match
  the error shape, passed through with a note instead of crashing).

Supported subset (draft 2020-12 core, documented honestly): ``type``
(``string`` | ``number`` | ``integer`` | ``boolean`` | ``null`` |
``array`` | ``object``; a non-empty duplicate-free list allows
several), ``properties`` / ``required`` (a non-empty duplicate-free
name list) / ``additionalProperties`` (boolean only), ``items`` (a
single schema), ``minItems`` / ``maxItems`` / ``uniqueItems``,
``minimum`` / ``maximum`` / ``exclusiveMinimum`` / ``exclusiveMaximum``,
``minLength`` / ``maxLength``, ``pattern`` (Python ``re.search``
semantics — an unanchored pattern matches anywhere in the string —
documented, not implicit), ``enum`` / ``const``, ``format``
(``email`` | ``date`` | ``date-time`` | ``uuid`` | ``url`` | ``ipv4``
family profiles), nested ``$defs`` / ``$ref`` (local ``#/$defs/<name>``
pointers only, resolved against the *root* schema's ``$defs`` as JSON
Pointers do, cycle-guarded), ``default`` (report-only), and the
annotations ``title`` / ``description`` / ``examples`` / ``$schema`` /
``$id`` / ``$comment`` / ``deprecated`` / ``readOnly`` / ``writeOnly``
(accepted and ignored). Boolean subschemas (``true`` = accept
anything, ``false`` = reject everything) are honored anywhere a
schema is expected; the root schema itself must be an object.
Everything else lands in ``unsupported_keywords`` — including the
tuple form of ``items``, a schema value for ``additionalProperties``
and non-local ``$ref`` pointers (external URLs, ``#/properties/...``
deep pointers).

Semantics decisions (documented, deterministic): ``integer`` follows
draft 2020-12 — any number with a zero fractional part, so JSON
``1.0`` IS an integer while ``1.5`` is not; ``integer`` also
satisfies ``number``; ``true`` is never a number or integer.
Equality (``enum``, ``const``, ``uniqueItems``) is deep JSON
equality: numbers compare numerically (``1`` equals ``1.0``), ``true``
never equals ``1``, and object key order is irrelevant. Numeric
bounds apply to numbers only; lengths and patterns to strings; item
rules to arrays — a keyword whose instance type does not match
simply does not apply (and is not counted). ``$ref`` may sit beside
sibling keywords (2020-12 behavior). The recursion guard cuts a
``$ref`` cycle that would re-enter the same definition for the same
instance (recorded in ``cycle_stops``); recursive schemas over
*distinct* nested instances (trees) validate normally.

Secret masking (the ``EnvSchemaTool`` rule): a property whose *name*
contains ``KEY``, ``SECRET``, ``PASSWORD`` or ``TOKEN``
(case-insensitive substring) never has its value echoed — error
``actual`` fields, ``defaults_declared`` values and inferred
``examples`` under such keys become ``***`` (numbers included).

Strict schema checking happens *before* any validation: the schema
must be an object, ``type`` must name known types, bounds must be
numbers, lengths non-negative integers, ``pattern`` a compilable
regex (<=512 characters), ``enum`` a non-empty list of JSON values,
``required`` a non-empty duplicate-free string list,
``additionalProperties`` a boolean, ``$defs`` an object of schemas,
``items`` a schema — invalid values raise ``ValueError`` naming the
schema location, while merely *unsupported* keywords are collected
with a note and never raise. Malformed *documents* (a string that is
not valid JSON, or nesting deeper than 64 levels) are structured
``error`` payloads so an agent can react without catching exceptions.
The tool never touches the filesystem or the network.
"""

import json
import math
import re
from typing import Any, ClassVar
from urllib.parse import urlsplit

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# --------------------------------------------------------------------- #
# type names / keyword sets
# --------------------------------------------------------------------- #

TYPE_NAMES = (
    "string",
    "number",
    "integer",
    "boolean",
    "null",
    "array",
    "object",
)

# Validation keywords the subset implements.
_KEYWORDS = frozenset(
    (
        "type",
        "properties",
        "required",
        "additionalProperties",
        "items",
        "minItems",
        "maxItems",
        "uniqueItems",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "minLength",
        "maxLength",
        "pattern",
        "enum",
        "const",
        "format",
        "$ref",
        "$defs",
    )
)

# Annotation keywords: accepted anywhere, never evaluated.
_ANNOTATION_KEYWORDS = frozenset(
    (
        "title",
        "description",
        "default",
        "examples",
        "$schema",
        "$id",
        "$comment",
        "deprecated",
        "readOnly",
        "writeOnly",
    )
)

FORMATS = ("email", "date", "date-time", "uuid", "url", "ipv4")

# Name substrings marking a property as secret-ish (the EnvSchemaTool
# rule, case-insensitive).
_SECRET_MARKERS = ("KEY", "SECRET", "PASSWORD", "TOKEN")

_MASK = "***"
_PREVIEW_CHARS = 24
_ACTUAL_CHARS = 120

# --------------------------------------------------------------------- #
# family format profiles
# --------------------------------------------------------------------- #

_DATE_RE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})\Z")
_DATETIME_RE = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2})T"
    r"([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?"
    r"(Z|[+-][0-9]{2}:[0-9]{2})\Z"
)
_UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\Z"
)
_IPV4_RE = re.compile(r"([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\Z")
# RFC 5322 atext — the dot-atom alphabet of an unquoted local part
# (same charset as EmailValidatorTool / EnvSchemaTool).
_ATEXT_RE = re.compile(r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+\Z")
_DOMAIN_LABEL_RE = re.compile(r"[A-Za-z0-9-]+\Z")
_SCHEME_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*\Z")

_DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


class JsonSchemaTool(Tool):
    """JSON Schema (draft 2020-12 subset) validation tool, stdlib-only.

    Attributes:
        max_document_chars (int): Upper bound on a JSON *text* document.
        max_schema_nodes (int): Upper bound on the number of schema
            (sub)schema objects walked while checking the schema.
        max_errors (int): Error cap for one ``validate`` run; further
            errors are dropped and ``truncated`` becomes ``True``.
        max_document_depth (int): Nesting cap for documents.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "json_schema_tool"
    description: str = (
        "Json schema tool — validate a JSON document against a "
        "practical subset of JSON Schema (draft 2020-12 core: "
        "type/properties/required/additionalProperties/items/"
        "minItems/maxItems/uniqueItems/numeric bounds/lengths/pattern/"
        "enum/const/format/nested $defs+$ref), purely on the Python "
        "stdlib, no network required. validate reports dot-path "
        "errors {path, schema_rule, message, actual} with an "
        "applied_rules count and collects out-of-subset keywords "
        "(anyOf/allOf/oneOf/not/...) in unsupported_keywords instead "
        "of failing (mode='validate'); infer_schema derives a skeleton "
        "subset schema from a document, masking example values of "
        "secret-ish keys (KEY/SECRET/PASSWORD/TOKEN) as *** "
        "(mode='infer_schema'); simplify_errors condenses a long error "
        "list into a grouped-by-path summary (mode='simplify_errors')."
    )

    MODES: ClassVar[tuple] = ("validate", "infer_schema", "simplify_errors")

    max_document_chars: int = 200_000
    max_schema_nodes: int = 5_000
    max_errors: int = 200
    max_document_depth: int = 64

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        document: Any = None,
        schema: Any = None,
        errors: Any = None,
    ) -> dict[str, Any]:
        """Run one JSON schema operation.

        Args:
            mode (str): One of ``validate`` / ``infer_schema`` /
                ``simplify_errors``.
            document (Any): The document — a JSON value (``None`` is
                the JSON ``null`` document), or a string which is
                parsed as JSON text. Required by ``validate`` and
                ``infer_schema``.
            schema (dict): The subset schema — an object (or a string
                parsed as JSON which must then be an object).
                Required by ``validate``.
            errors (list): The error list to condense — required by
                ``simplify_errors`` (entries use the shape ``validate``
                emits; off-shape entries are passed through).

        Returns:
            Dict[str, Any]: The operation result — always a ``mode``
            and a ``result`` string plus mode-specific fields — or a
            structured ``error`` payload for content-level failures
            (unparseable JSON text, document nesting too deep).

        Raises:
            ValueError: If any parameter is malformed — in particular
                invalid *values* of supported schema keywords (always
                naming the schema location); merely unsupported
                keywords never raise.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "validate":
            document, failure = self._load_document(document)
            if failure is not None:
                return {
                    "mode": "validate",
                    "error": failure,
                }
            schema, report = self._load_schema(schema)
            return self._run_validate(document, schema, report)
        if mode == "infer_schema":
            document, failure = self._load_document(document)
            if failure is not None:
                return {"mode": "infer_schema", "error": failure}
            return self._run_infer(document)
        return self._run_simplify(self._validate_errors(errors))

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"json_schema_tool: {message}")

    # -- documents ------------------------------------------------------ #

    def _load_document(self, document: Any) -> tuple[Any, Any]:
        """Normalize the document: JSON text in, JSON value out.

        A string is parsed as JSON text; any other value must already
        be a JSON value and is checked recursively (tuples become
        arrays; non-string dict keys, sets and non-finite floats are
        rejected). Returns ``(value, None)`` or ``(None, error_dict)``
        for content-level failures (unparseable text, nesting too
        deep); shape failures raise ``ValueError``.
        """
        if isinstance(document, str):
            if len(document) > self.max_document_chars:
                self._invalid(
                    f"document exceeds the {self.max_document_chars:,}"
                    f"-character limit (got {len(document):,} characters)"
                )
            try:
                document = json.loads(document)
            except ValueError as exc:
                return None, {
                    "type": "invalid_json",
                    "message": f"document is not valid JSON: {exc}",
                }
        self._check_json_value(document, "", 0)
        depth = self._depth(document, 0)
        if depth > self.max_document_depth:
            return None, {
                "type": "document_too_deep",
                "message": (
                    f"document nests {depth} levels deep; the limit is "
                    f"{self.max_document_depth}"
                ),
            }
        return document, None

    @classmethod
    def _check_json_value(cls, value: Any, where: str, depth: int) -> None:
        """Verify a native value is JSON-shaped; tuples count as arrays."""
        if depth > 128:  # native input recursion guard
            cls._invalid(
                f"document value at {where or 'the root'} is too deep"
            )
        if value is None or isinstance(value, (bool, int, str)):
            return
        if isinstance(value, float):
            if not math.isfinite(value):
                cls._invalid(
                    f"document value at {where or 'the root'} is not "
                    f"finite (got {value!r}); JSON has no NaN/Infinity"
                )
            return
        if isinstance(value, (list, tuple)):
            for index, item in enumerate(value):
                cls._check_json_value(item, f"{where}[{index}]", depth + 1)
            return
        if isinstance(value, dict):
            for key, item in value.items():
                if not isinstance(key, str):
                    cls._invalid(
                        f"document object at {where or 'the root'} has a "
                        f"non-string key (got {key!r})"
                    )
                cls._check_json_value(
                    item, f"{where}.{key}" if where else key, depth + 1
                )
            return
        cls._invalid(
            f"document value at {where or 'the root'} is not a JSON value "
            f"(got {type(value).__name__})"
        )

    @classmethod
    def _depth(cls, value: Any, current: int) -> int:
        """Measure container nesting depth of a JSON value."""
        if isinstance(value, (list, tuple)):
            return max(
                (cls._depth(item, current + 1) for item in value),
                default=current,
            )
        if isinstance(value, dict):
            return max(
                (cls._depth(item, current + 1) for item in value.values()),
                default=current,
            )
        return current

    # -- schemas --------------------------------------------------------- #

    def _load_schema(
        self, schema: Any
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Load and strictly check the schema (must be an object).

        Returns the schema plus the walk report (unsupported keywords,
        declared defaults) the validate mode embeds in its payload.
        """
        if isinstance(schema, str):
            if len(schema) > self.max_document_chars:
                self._invalid(
                    f"schema exceeds the {self.max_document_chars:,}"
                    f"-character limit (got {len(schema):,} characters)"
                )
            try:
                schema = json.loads(schema)
            except ValueError as exc:
                self._invalid(f"schema is not valid JSON: {exc}")
        if schema is None or isinstance(schema, bool) or not isinstance(
            schema, dict
        ):
            self._invalid(
                f"schema must be an object (draft 2020-12 subset; got "
                f"{schema!r})"
            )
        report = self._walk_schema(schema)
        if report["nodes"] > self.max_schema_nodes:
            self._invalid(
                f"schema exceeds the {self.max_schema_nodes:,}-schema "
                f"limit (got {report['nodes']:,})"
            )
        return schema, report

    def _walk_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Walk every subschema, strictly checking supported keywords.

        Collects unsupported keywords (name + JSON-pointer path) and
        every declared ``default``; raises ``ValueError`` on invalid
        values of supported keywords. Local ``$ref`` targets are
        verified to exist in the root schema's ``$defs``.
        """
        report: dict[str, Any] = {
            "nodes": 0,
            "unsupported": [],
            "defaults": [],
            "seen": set(),
        }
        root_defs = schema.get("$defs")
        root_defs = root_defs if isinstance(root_defs, dict) else {}

        def note(keyword: str, pointer: str, text: str) -> None:
            if not self._noted(report["unsupported"], keyword, pointer):
                report["unsupported"].append(
                    {
                        "keyword": keyword,
                        "path": pointer,
                        "note": text,
                    }
                )

        def walk(node: Any, pointer: str) -> None:
            if isinstance(node, bool):
                return  # boolean subschema: true/false, nothing to check
            if not isinstance(node, dict):
                self._invalid(
                    f"schema at {pointer} must be an object or boolean "
                    f"(got {node!r})"
                )
            if id(node) in report["seen"]:
                return
            report["seen"].add(id(node))
            report["nodes"] += 1
            self._check_keyword_values(node, pointer)
            self._collect_unsupported(node, pointer, report, note)
            if "default" in node:
                self._check_json_value(node["default"], pointer, 0)
                report["defaults"].append(
                    {
                        "schema_path": pointer,
                        "default": self._mask_default(
                            pointer, node["default"]
                        ),
                    }
                )
            # structural children: $ref target, properties, items, $defs
            ref = node.get("$ref")
            if (
                isinstance(ref, str)
                and ref.startswith("#/$defs/")
                and "/" not in ref[len("#/$defs/") :]
            ):
                name = ref[len("#/$defs/") :]
                if name not in root_defs:
                    self._invalid(
                        f"$ref at {pointer} names missing $defs entry "
                        f"{name!r}"
                    )
                walk(root_defs[name], f"#/$defs/{name}")
            properties = node.get("properties")
            if isinstance(properties, dict):
                for key, child in properties.items():
                    walk(child, f"{pointer}/properties/{key}")
            items = node.get("items")
            if isinstance(items, (dict, bool)):
                walk(items, f"{pointer}/items")
            defs = node.get("$defs")
            if isinstance(defs, dict):
                for name, child in defs.items():
                    walk(child, f"{pointer}/$defs/{name}")

        walk(schema, "#")
        report["unsupported"].sort(
            key=lambda entry: (entry["path"], entry["keyword"])
        )
        report["defaults"].sort(key=lambda entry: entry["schema_path"])
        return report

    @staticmethod
    def _noted(unsupported: list, keyword: str, pointer: str) -> bool:
        """True when (keyword, pointer) is already collected."""
        return any(
            entry["keyword"] == keyword and entry["path"] == pointer
            for entry in unsupported
        )

    def _check_keyword_values(
        self, node: dict[str, Any], pointer: str
    ) -> None:
        """Strictly check the values of every supported keyword."""
        where = f"schema at {pointer}"

        if "type" in node:
            declared = node["type"]
            if isinstance(declared, str):
                candidates = [declared]
            elif (
                isinstance(declared, list)
                and declared
                and all(isinstance(item, str) for item in declared)
            ):
                candidates = declared
            else:
                self._invalid(
                    f"{where}: type must be a known type name or a "
                    f"non-empty list of them (got {declared!r})"
                )
                return  # unreachable; keeps type checkers content
            unknown = [t for t in candidates if t not in TYPE_NAMES]
            if unknown:
                self._invalid(
                    f"{where}: type names unknown type(s) {unknown} "
                    f"(allowed: {list(TYPE_NAMES)})"
                )
            if len(set(candidates)) != len(candidates):
                self._invalid(
                    f"{where}: type list contains duplicates "
                    f"(got {declared!r})"
                )

        if "properties" in node and not isinstance(node["properties"], dict):
            self._invalid(
                f"{where}: properties must be an object of property name "
                f"-> schema (got {node['properties']!r})"
            )

        if "required" in node:
            value = node["required"]
            if (
                isinstance(value, str)
                or not isinstance(value, (list, tuple))
                or not value
            ):
                self._invalid(
                    f"{where}: required must be a non-empty list of "
                    f"property names (got {value!r})"
                )
            for name in value:
                if not isinstance(name, str):
                    self._invalid(
                        f"{where}: required entries must be strings "
                        f"(got {name!r})"
                    )
            if len(set(value)) != len(value):
                self._invalid(
                    f"{where}: required contains duplicate names "
                    f"(got {list(value)!r})"
                )

        if "additionalProperties" in node:
            value = node["additionalProperties"]
            if not isinstance(value, bool) and not isinstance(value, dict):
                self._invalid(
                    f"{where}: additionalProperties must be a boolean in "
                    f"this subset (got {value!r}; a schema value is "
                    f"tolerated but unsupported)"
                )

        for keyword in ("minItems", "maxItems", "minLength", "maxLength"):
            if keyword in node:
                value = node[keyword]
                if isinstance(value, bool) or not isinstance(value, int):
                    self._invalid(
                        f"{where}: {keyword} must be a non-negative integer "
                        f"(got {value!r})"
                    )
                if value < 0:
                    self._invalid(
                        f"{where}: {keyword} must be a non-negative integer "
                        f"(got {value!r})"
                    )

        if "uniqueItems" in node and not isinstance(
            node["uniqueItems"], bool
        ):
            self._invalid(
                f"{where}: uniqueItems must be a boolean "
                f"(got {node['uniqueItems']!r})"
            )

        for keyword in (
            "minimum",
            "maximum",
            "exclusiveMinimum",
            "exclusiveMaximum",
        ):
            if keyword in node:
                value = node[keyword]
                if isinstance(value, bool) or not isinstance(
                    value, (int, float)
                ):
                    self._invalid(
                        f"{where}: {keyword} must be a number "
                        f"(got {value!r})"
                    )
                if isinstance(value, float) and not math.isfinite(value):
                    self._invalid(
                        f"{where}: {keyword} must be finite (got {value!r})"
                    )

        if "pattern" in node:
            value = node["pattern"]
            if not isinstance(value, str):
                self._invalid(
                    f"{where}: pattern must be a string (got {value!r})"
                )
            if len(value) > 512:
                self._invalid(
                    f"{where}: pattern exceeds the 512-character limit "
                    f"(got {len(value):,} characters)"
                )
            try:
                re.compile(value)
            except re.error as exc:
                self._invalid(f"{where}: pattern does not compile ({exc})")

        if "enum" in node:
            value = node["enum"]
            if (
                isinstance(value, str)
                or not isinstance(value, (list, tuple))
                or not value
            ):
                self._invalid(
                    f"{where}: enum must be a non-empty list of JSON values "
                    f"(got {value!r})"
                )
            for index, entry in enumerate(value):
                self._check_json_value(entry, f"{where} enum[{index}]", 0)

        if "items" in node:
            value = node["items"]
            if not isinstance(value, (dict, bool, list)):
                self._invalid(
                    f"{where}: items must be a single schema (object or "
                    f"boolean) in this subset (got {value!r}; the draft-07 "
                    f"array form is tolerated but unsupported)"
                )

        if "format" in node and not isinstance(node["format"], str):
            self._invalid(
                f"{where}: format must be a string (got {node['format']!r})"
            )

        if "$defs" in node and not isinstance(node["$defs"], dict):
            self._invalid(
                f"{where}: $defs must be an object of definition name -> "
                f"schema (got {node['$defs']!r})"
            )

        if "$ref" in node and not isinstance(node["$ref"], str):
            self._invalid(
                f"{where}: $ref must be a string (got {node['$ref']!r})"
            )

    def _collect_unsupported(
        self,
        node: dict[str, Any],
        pointer: str,
        report: dict[str, Any],
        note,
    ) -> None:
        """Collect keywords / usages outside the subset (skipped)."""
        for keyword in node:
            if keyword in _KEYWORDS or keyword in _ANNOTATION_KEYWORDS:
                continue
            note(
                keyword,
                pointer,
                f"{keyword} is outside the supported subset; it was "
                f"skipped (the rest of the schema was still validated)",
            )
        format_value = node.get("format")
        if isinstance(format_value, str) and format_value not in FORMATS:
            note(
                f"format:{format_value}",
                pointer,
                f"format {format_value!r} is not one of {list(FORMATS)}; "
                f"it was skipped",
            )
        if isinstance(node.get("items"), list):
            note(
                "items(array form)",
                pointer,
                "items as an array (draft-07 tuple form) is unsupported; "
                "only a single schema is applied",
            )
        if isinstance(node.get("additionalProperties"), dict):
            note(
                "additionalProperties(schema)",
                pointer,
                "additionalProperties as a schema is unsupported; only "
                "the boolean form is applied",
            )
        ref = node.get("$ref")
        if isinstance(ref, str):
            payload = ref[len("#/$defs/") :] if ref.startswith("#/$defs/") else None
            deep = payload is not None and "/" in payload
            if not ref.startswith("#/$defs/") or deep:
                note(
                    "$ref(non-local)",
                    pointer,
                    f"$ref {ref!r} is not a local #/$defs/<name> pointer; "
                    f"it was skipped",
                )

    # ------------------------------------------------------------------ #
    # JSON semantics helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _json_type(value: Any) -> str:
        """The JSON type name of a value (bools are never numbers)."""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "number"
        if isinstance(value, str):
            return "string"
        if isinstance(value, (list, tuple)):
            return "array"
        return "object"

    @classmethod
    def _matches_type(cls, value: Any, declared: str) -> bool:
        """Type matching with the documented integer/number policy."""
        actual = cls._json_type(value)
        if actual == declared:
            return True
        if declared == "number":
            return actual == "integer"
        if declared == "integer":
            # draft 2020-12: a number with a zero fractional part is an
            # integer, so JSON 1.0 IS an integer; 1.5 is not. Booleans
            # never are (handled by _json_type).
            return actual == "number" and value.is_integer()
        return False

    @staticmethod
    def _is_number(value: Any) -> bool:
        """True for JSON numbers (integers included, booleans never)."""
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    @classmethod
    def _equal_key(cls, value: Any) -> tuple:
        """A hashable canonical form implementing deep JSON equality.

        Numbers compare numerically (1 equals 1.0); ``true`` never
        equals ``1``; object key order is irrelevant.
        """
        if value is None:
            return ("null",)
        if isinstance(value, bool):
            return ("boolean", value)
        if isinstance(value, (int, float)):
            return ("number", float(value))
        if isinstance(value, str):
            return ("string", value)
        if isinstance(value, (list, tuple)):
            return ("array", tuple(cls._equal_key(item) for item in value))
        return (
            "object",
            tuple(
                sorted(
                    (key, cls._equal_key(item))
                    for key, item in value.items()
                )
            ),
        )

    @classmethod
    def _deep_equal(cls, left: Any, right: Any) -> bool:
        """Deep JSON equality (see :meth:`_equal_key`)."""
        return cls._equal_key(left) == cls._equal_key(right)

    # ------------------------------------------------------------------ #
    # Secret masking (the EnvSchemaTool rule)
    # ------------------------------------------------------------------ #

    @classmethod
    def _is_secret(cls, key: str) -> bool:
        """True when the property name marks its value secret-ish."""
        upper = key.upper()
        return any(marker in upper for marker in _SECRET_MARKERS)

    @staticmethod
    def _path_key(path: str) -> str:
        """The governing property name of a dot-path (last segment)."""
        segment = path.rsplit(".", 1)[-1]
        return re.sub(r"\[\d+\]$", "", segment)

    @classmethod
    def _actual(cls, path: str, value: Any) -> Any:
        """Render an error ``actual``: masked / truncated / bare."""
        if cls._is_secret(cls._path_key(path)):
            return _MASK
        if isinstance(value, str) and len(value) > _ACTUAL_CHARS:
            return value[:_ACTUAL_CHARS] + "..."
        return value

    @classmethod
    def _mask_default(cls, pointer: str, value: Any) -> Any:
        """Mask a declared default when its property name is secret."""
        name = pointer.rsplit("/", 1)[-1]
        if name and cls._is_secret(name):
            return _MASK
        if isinstance(value, str) and len(value) > _ACTUAL_CHARS:
            return value[:_ACTUAL_CHARS] + "..."
        return value

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def _run_validate(
        self, document: Any, schema: dict[str, Any], report: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate the document against the (pre-checked) schema."""
        context: dict[str, Any] = {
            "errors": [],
            "applied": 0,
            "truncated": False,
            "cycle_stops": [],
            "ref_stack": set(),
            "defs": schema.get("$defs")
            if isinstance(schema.get("$defs"), dict)
            else {},
        }
        self._validate_node(document, schema, "", context)
        errors = context["errors"]
        payload: dict[str, Any] = {
            "mode": "validate",
            "result": (
                "valid" if not errors else f"invalid: {len(errors)} error(s)"
            ),
            "valid": not errors,
            "applied_rules": context["applied"],
            "errors": errors,
            "unsupported_keywords": report["unsupported"],
            "defaults_declared": report["defaults"],
        }
        if context["truncated"]:
            payload["truncated"] = True
        if context["cycle_stops"]:
            payload["cycle_stops"] = context["cycle_stops"][:20]
        return payload

    def _error(
        self,
        context: dict[str, Any],
        path: str,
        rule: str,
        message: str,
        actual: Any,
    ) -> None:
        """Record one validation error (capped at ``max_errors``)."""
        if len(context["errors"]) >= self.max_errors:
            context["truncated"] = True
            return
        context["errors"].append(
            {
                "path": path,
                "schema_rule": rule,
                "message": message,
                "actual": actual,
            }
        )

    def _validate_node(
        self, value: Any, schema: Any, path: str, context: dict[str, Any]
    ) -> None:
        """Apply one schema (object or boolean) to a value, recursively."""
        if schema is True:
            return
        if schema is False:
            context["applied"] += 1
            self._error(
                context,
                path,
                "false",
                "schema is false: no value is valid",
                self._json_type(value),
            )
            return

        # $ref first (2020-12: refs apply alongside sibling keywords);
        # resolved against the ROOT schema's $defs, cycle-guarded on
        # (definition, instance) pairs.
        ref = schema.get("$ref")
        if isinstance(ref, str):
            payload = (
                ref[len("#/$defs/") :]
                if ref.startswith("#/$defs/")
                else None
            )
            if payload is not None and "/" not in payload:
                name = payload
                target = context["defs"].get(name)
                if isinstance(target, (dict, bool)):
                    guard = (name, id(value))
                    if guard in context["ref_stack"]:
                        if not any(
                            stop["ref"] == name and stop["path"] == path
                            for stop in context["cycle_stops"]
                        ):
                            context["cycle_stops"].append(
                                {"ref": name, "path": path}
                            )
                    else:
                        context["ref_stack"].add(guard)
                        try:
                            self._validate_node(value, target, path, context)
                        finally:
                            context["ref_stack"].discard(guard)
            # else: non-local / deep pointer — noted as unsupported by
            # the walk, nothing to apply.

        self._apply_keywords(value, schema, path, context)

    def _apply_keywords(
        self, value: Any, schema: dict[str, Any], path: str,
        context: dict[str, Any],
    ) -> None:
        """Apply every supported keyword of one object schema."""

        def child(name: str) -> str:
            return f"{path}.{name}" if path else name

        # -- type -------------------------------------------------------- #
        declared = schema.get("type")
        if declared is not None:
            candidates = (
                [declared] if isinstance(declared, str) else list(declared)
            )
            context["applied"] += 1
            if not any(self._matches_type(value, t) for t in candidates):
                expected = (
                    candidates[0]
                    if len(candidates) == 1
                    else "one of " + ", ".join(candidates)
                )
                self._error(
                    context,
                    path,
                    "type",
                    f"expected type {expected}, got "
                    f"{self._json_type(value)}",
                    self._json_type(value),
                )

        # -- enum / const ------------------------------------------------- #
        if "enum" in schema:
            context["applied"] += 1
            if not any(
                self._deep_equal(value, entry) for entry in schema["enum"]
            ):
                self._error(
                    context,
                    path,
                    "enum",
                    "value is not one of the allowed enum values",
                    self._actual(path, value),
                )
        if "const" in schema:
            context["applied"] += 1
            if not self._deep_equal(value, schema["const"]):
                self._error(
                    context,
                    path,
                    "const",
                    "value does not equal the const value",
                    self._actual(path, value),
                )

        # -- string keywords ---------------------------------------------- #
        if isinstance(value, str):
            if "minLength" in schema:
                context["applied"] += 1
                if len(value) < schema["minLength"]:
                    self._error(
                        context,
                        path,
                        "minLength",
                        f"string length {len(value)} is shorter than "
                        f"minLength {schema['minLength']}",
                        len(value),
                    )
            if "maxLength" in schema:
                context["applied"] += 1
                if len(value) > schema["maxLength"]:
                    self._error(
                        context,
                        path,
                        "maxLength",
                        f"string length {len(value)} exceeds maxLength "
                        f"{schema['maxLength']}",
                        len(value),
                    )
            if "pattern" in schema:
                context["applied"] += 1
                if not re.search(schema["pattern"], value):
                    self._error(
                        context,
                        path,
                        "pattern",
                        f"string does not match pattern "
                        f"{schema['pattern']!r} (re.search semantics)",
                        self._actual(path, value),
                    )
            if schema.get("format") in FORMATS:
                context["applied"] += 1
                if not self._check_format(schema["format"], value):
                    self._error(
                        context,
                        path,
                        "format",
                        f"not a valid {schema['format']} (family profile)",
                        self._actual(path, value),
                    )

        # -- number keywords ---------------------------------------------- #
        if self._is_number(value):
            for keyword, violation in (
                ("minimum", lambda v, b: v < b),
                ("maximum", lambda v, b: v > b),
                ("exclusiveMinimum", lambda v, b: v <= b),
                ("exclusiveMaximum", lambda v, b: v >= b),
            ):
                if keyword in schema:
                    context["applied"] += 1
                    bound = schema[keyword]
                    if violation(value, bound):
                        verb = {
                            "minimum": "is below",
                            "maximum": "is above",
                            "exclusiveMinimum": "is at or below",
                            "exclusiveMaximum": "is at or above",
                        }[keyword]
                        self._error(
                            context,
                            path,
                            keyword,
                            f"value {verb} {keyword} {bound}",
                            self._actual(path, value),
                        )

        # -- object keywords ----------------------------------------------- #
        if isinstance(value, dict):
            properties = schema.get("properties")
            properties = properties if isinstance(properties, dict) else {}
            for name in properties:
                if name in value:
                    self._validate_node(
                        value[name], properties[name], child(name), context
                    )
            if "required" in schema and isinstance(
                schema["required"], (list, tuple)
            ):
                context["applied"] += 1
                for name in schema["required"]:
                    if name not in value:
                        self._error(
                            context,
                            path,
                            "required",
                            f"required property {name!r} is missing",
                            name,
                        )
            if schema.get("additionalProperties") is False:
                context["applied"] += 1
                for name in value:
                    if name not in properties:
                        self._error(
                            context,
                            child(name),
                            "additionalProperties",
                            f"property {name!r} is not declared in "
                            f"properties and additionalProperties is false",
                            name,
                        )

        # -- array keywords -------------------------------------------------- #
        if isinstance(value, (list, tuple)):
            length = len(value)
            if "minItems" in schema:
                context["applied"] += 1
                if length < schema["minItems"]:
                    self._error(
                        context,
                        path,
                        "minItems",
                        f"array has {length} item(s), minItems is "
                        f"{schema['minItems']}",
                        length,
                    )
            if "maxItems" in schema:
                context["applied"] += 1
                if length > schema["maxItems"]:
                    self._error(
                        context,
                        path,
                        "maxItems",
                        f"array has {length} item(s), maxItems is "
                        f"{schema['maxItems']}",
                        length,
                    )
            if schema.get("uniqueItems") is True:
                context["applied"] += 1
                seen = set()
                for item in value:
                    key = self._equal_key(item)
                    if key in seen:
                        self._error(
                            context,
                            path,
                            "uniqueItems",
                            "array items are not unique (deep JSON "
                            "equality)",
                            self._actual(path, item),
                        )
                        break
                    seen.add(key)
            items = schema.get("items")
            if isinstance(items, (dict, bool)):
                for index, element in enumerate(value):
                    self._validate_node(
                        element, items, f"{path}[{index}]", context
                    )

    # ------------------------------------------------------------------ #
    # format profiles (family regexes)
    # ------------------------------------------------------------------ #

    @classmethod
    def _check_format(cls, fmt: str, value: str) -> bool:
        """Assert one family format profile on a string."""
        if fmt == "email":
            return cls._is_email(value)
        if fmt == "date":
            return cls._is_date(value)
        if fmt == "date-time":
            return cls._is_datetime(value)
        if fmt == "uuid":
            return bool(_UUID_RE.match(value))
        if fmt == "url":
            return cls._is_url(value)
        if fmt == "ipv4":
            return cls._is_ipv4(value)
        return False

    @classmethod
    def _is_email(cls, value: str) -> bool:
        """EmailValidatorTool-family profile: dot-atom local + labels."""
        if len(value) > 254 or value.count("@") != 1:
            return False
        local, domain = value.split("@")
        if not local or len(local) > 64:
            return False
        if local.startswith(".") or local.endswith(".") or ".." in local:
            return False
        for segment in local.split("."):
            if not _ATEXT_RE.match(segment):
                return False
        for label in domain.split("."):
            if not label or len(label) > 63:
                return False
            if not _DOMAIN_LABEL_RE.match(label):
                return False
            if label.startswith("-") or label.endswith("-"):
                return False
        return True

    @classmethod
    def _is_date(cls, value: str) -> bool:
        """Calendar-true YYYY-MM-DD (leap years included)."""
        match = _DATE_RE.match(value)
        if not match:
            return False
        year, month, day = (int(part) for part in match.groups())
        if not 1 <= month <= 12:
            return False
        limit = _DAYS_IN_MONTH[month - 1]
        if (
            month == 2
            and year % 4 == 0
            and (year % 100 != 0 or year % 400 == 0)
        ):
            limit = 29
        return 1 <= day <= limit

    @classmethod
    def _is_datetime(cls, value: str) -> bool:
        """Strict ISO-8601 subset: YYYY-MM-DDTHH:MM:SS(.frac)?(Z|±HH:MM)."""
        match = _DATETIME_RE.match(value)
        if not match:
            return False
        year, month, day, hour, minute, second = (
            int(part) for part in match.groups()[:6]
        )
        offset = match.group(8)
        if not cls._is_date(value[:10]):
            return False
        if hour > 23 or minute > 59 or second > 59:
            return False
        if offset != "Z" and (
            int(offset[1:3]) > 23 or int(offset[4:6]) > 59
        ):
            return False
        return True

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
    def _is_ipv4(cls, value: str) -> bool:
        """Dotted quad, 0-255 per octet, no leading zeros."""
        match = _IPV4_RE.match(value)
        if not match:
            return False
        for octet in match.groups():
            if len(octet) > 1 and octet.startswith("0"):
                return False
            if int(octet) > 255:
                return False
        return True

    # ------------------------------------------------------------------ #
    # infer_schema mode
    # ------------------------------------------------------------------ #

    def _run_infer(self, document: Any) -> dict[str, Any]:
        """Infer a skeleton subset schema from the document."""
        return {
            "mode": "infer_schema",
            "result": "schema inferred (draft 2020-12 subset)",
            "document_type": self._json_type(document),
            "schema": self._infer_node(document, None),
        }

    @classmethod
    def _example(cls, value: Any, secret: bool) -> Any:
        """One reviewable example for a scalar node (masked/truncated)."""
        if secret:
            return _MASK
        if isinstance(value, str):
            return (
                value
                if len(value) <= _PREVIEW_CHARS
                else value[:_PREVIEW_CHARS] + "..."
            )
        return value

    @classmethod
    def _infer_node(cls, value: Any, key: Any) -> dict[str, Any]:
        """Infer one schema node; ``key`` is the governing property name."""
        secret = isinstance(key, str) and cls._is_secret(key)
        kind = cls._json_type(value)
        if kind == "object":
            node: dict[str, Any] = {"type": "object"}
            if value:
                node["properties"] = {
                    name: cls._infer_node(item, name)
                    for name, item in value.items()
                }
                node["required"] = sorted(value)
            return node
        if kind == "array":
            node = {"type": "array"}
            if value:
                node["items"] = cls._merge_schemas(
                    [cls._infer_node(item, key) for item in value]
                )
            return node
        node = {"type": kind}
        if kind == "string":
            for fmt in ("date-time", "date", "uuid", "email", "ipv4", "url"):
                if cls._check_format(fmt, value):
                    node["format"] = fmt
                    break
        node["examples"] = [cls._example(value, secret)]
        return node

    @classmethod
    def _merge_schemas(cls, schemas: list) -> dict[str, Any]:
        """Merge sibling schemas into one that accepts every sibling."""
        first = schemas[0]
        if all(schema == first for schema in schemas):
            return first
        if all(schema.get("type") == "object" for schema in schemas):
            merged: dict[str, Any] = {"type": "object"}
            names: list = []
            for schema in schemas:
                for name in schema.get("properties", {}):
                    if name not in names:
                        names.append(name)
            properties: dict[str, Any] = {}
            required: list = []
            for name in names:
                holders = [
                    schema["properties"][name]
                    for schema in schemas
                    if name in schema.get("properties", {})
                ]
                properties[name] = cls._merge_schemas(holders)
                if len(holders) == len(schemas) and all(
                    name in schema.get("required", []) for schema in schemas
                ):
                    required.append(name)
            merged["properties"] = properties
            if required:
                merged["required"] = sorted(required)
            return merged
        return cls._type_union(schemas)

    @classmethod
    def _type_union(cls, schemas: list) -> dict[str, Any]:
        """A constraint-free schema accepting every sibling's values."""
        kinds: list = []
        for schema in schemas:
            declared = schema.get("type")
            candidates = (
                [declared]
                if isinstance(declared, str)
                else list(declared or [])
            )
            for candidate in candidates:
                if candidate not in kinds:
                    kinds.append(candidate)
        if not kinds:
            return {}  # empty schema: accepts anything
        if "number" in kinds:  # integer is a subset of number
            kinds = [kind for kind in kinds if kind != "integer"]
        kinds.sort()
        return {"type": kinds if len(kinds) > 1 else kinds[0]}

    # ------------------------------------------------------------------ #
    # simplify_errors mode
    # ------------------------------------------------------------------ #

    def _validate_errors(self, errors: Any) -> list:
        """Check the ``errors`` parameter (a bounded list)."""
        if errors is None or isinstance(errors, (str, bytes)) or not (
            isinstance(errors, (list, tuple))
        ):
            self._invalid(
                f"errors must be a list of error entries as emitted by "
                f"the validate mode (got {errors!r})"
            )
        if len(errors) > 10_000:
            self._invalid(
                f"errors exceeds the 10,000-entry limit "
                f"(got {len(errors):,} entries)"
            )
        return list(errors)

    def _run_simplify(self, errors: list) -> dict[str, Any]:
        """Condense an error list into a grouped-by-path summary."""
        groups: dict[str, dict[str, Any]] = {}
        rule_totals: dict[str, int] = {}
        unparseable: list = []
        for entry in errors:
            if (
                not isinstance(entry, dict)
                or not isinstance(entry.get("path"), str)
                or not isinstance(entry.get("schema_rule"), str)
            ):
                unparseable.append(entry)
                continue
            path = entry["path"]
            rule = entry["schema_rule"]
            message = entry.get("message")
            if not isinstance(message, str):
                message = json.dumps(message, default=str)
            rule_totals[rule] = rule_totals.get(rule, 0) + 1
            group = groups.setdefault(
                path,
                {"path": path, "count": 0, "rules": [], "messages": []},
            )
            group["count"] += 1
            if rule not in group["rules"]:
                group["rules"].append(rule)
            if message not in group["messages"]:
                group["messages"].append(message)
        ordered = sorted(
            groups.values(), key=lambda group: (-group["count"], group["path"])
        )
        for group in ordered:
            group["rules"] = sorted(group["rules"])
        return {
            "mode": "simplify_errors",
            "result": (
                f"{len(errors) - len(unparseable)} error(s) across "
                f"{len(ordered)} path(s)"
            ),
            "total_errors": len(errors),
            "groups": ordered,
            "rule_totals": dict(sorted(rule_totals.items())),
            "unparseable": unparseable,
        }
