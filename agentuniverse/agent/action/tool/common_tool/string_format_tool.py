#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: string_format_tool.py

"""Python format-template analysis tool (str.format / f-string / printf-%).

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency utility that
operates on the *grammar of Python format strings* — the template
itself, never the content being formatted. The family's template and
prompt tools operate on content: ``TemplateRenderTool`` (#3559)
substitutes placeholders safely, ``PromptTemplateLinterTool`` (#3756)
lints prompt placeholders, and ``PromptTool`` (#3369) generates and
optimizes prompt text with an LLM — none of them answers "is this
``{customer.name!r:>20}`` field a *syntactically correct* str.format
template, what does each field reference, will ``str.format_map``
render it, and what is its printf-% equivalent?" That is this tool's
single job.

Every error claim is provable: the ``lint`` mode never trusts the
static scanner alone. After parsing, it calls the real
``str.format`` machinery on inert, sandboxed dummy arguments — plain
``'x'`` / ``7`` / ``2.5`` semantics for value fields, digit-string
or single-char candidates for fields nested inside format specs
(width/precision/fill tokens), each wrapped in a permissive node
that also survives arbitrary attribute/index paths — and catches
every exception. An error finding is emitted only when the failure
is value-independent: a structural parse-stage ``ValueError``
("Single '{' encountered", "cannot switch from automatic field
numbering to manual field specification", "Unknown conversion
specifier", "expected ':' after conversion specifier", "Empty
attribute in format string", "Max string recursion exceeded",
"unmatched '{' in format spec", ...) or a failure of every dummy
combination inside the format machinery (``{:!}``, ``{:+s}``).
Conversely, whenever the real machinery renders the template with
some inert combination, *every* error finding is vetoed — a spec
that fails for ``str`` dummies but works for ``int`` dummies
(``{:d}``) is reported as *info* (``type_dependent_spec``), which
is exactly the real verdict. The runtime is the stdlib only: no
``eval``, no network, all exceptions caught.

Five modes:

* ``lint`` — template → findings ``{span, code, message, severity}``.
  Error codes (each confirmed or vetoed by the probe):
  ``unterminated_field`` / ``stray_close_brace`` /
  ``unmatched_brace_in_spec`` (unmatched ``{`` or ``}``; ``{{`` /
  ``}}`` escapes are honored), ``malformed_conversion`` /
  ``unknown_conversion`` (only ``!r`` ``!s`` ``!a`` exist; more than
  one conversion letter raises "expected ':' after conversion
  specifier"), ``mixed_numbering`` (``{0}`` and ``{}`` mixed),
  ``empty_attribute_or_index`` (``{0.}`` / ``{a[]}``),
  ``spec_recursion_exceeded`` (a nested replacement field inside a
  spec that itself carries a spec — CPython raises "Max string
  recursion exceeded"), ``value_independent_spec_error``. Info
  codes: ``nested_replacement_in_spec``, ``type_dependent_spec``
  (with the working dummy kinds listed), 
  ``locale_aware_n_specifier``, ``field_name_whitespace`` (``{ x}``
  is a *keyword* field named ``' x'``), ``duplicate_field_reference``,
  ``probe_exhausted`` (nothing rendered with any inert kind, but no
  value-independent pattern either — verify with real values).
  Warning: ``no_placeholders``.
* ``fields`` — template → one record per replacement field, in
  order, with ``{field_name, index_or_key, auto_numbered,
  attribute_chain, index_parts, conversion, format_spec,
  position_span}``; fields nested inside format specs (``{:{w}}``)
  are reported recursively, and ``{{``/``}}`` escapes are counted.
* ``render`` — template + mapping → ``str.format_map`` semantics
  with precise missing-key reporting: missing keys come back as
  structured findings naming the key and the exact field span,
  never a raised ``KeyError``; when nothing is missing the result is
  produced by the real ``format_map`` (the test suite asserts byte
  equality). Positional fields (``{}`` / ``{0}``) are rejected with
  the message the real ``format_map`` raises ("Format string
  contains positional fields"), and render-time failures of real
  mapping values are reported as findings, not crashes.
* ``translate_percent`` — printf-% ↔ str.format, both directions.
  ``to_format`` converts ``%(name)s`` forms and ``%s %r %a %d %i
  %o %x %X %e %E %f %F %g %G %c %%`` with flags ``- + <space> 0 #``,
  widths, precisions and the ignored C length modifiers (``h l L``)
  into the equivalent ``.format`` template; the flag algebra is the
  one the real machinery obeys (``-`` suppresses zero-fill, ``+``
  beats ``<space>``, ``#`` is dropped where C ignores it, ``%s``
  right-aligns on width while ``{}`` left-aligns). ``*`` widths and
  precisions, precision on ``%s``/``%r``/``%a``/``%c`` (string
  truncation), unknown conversion letters and incomplete trailing
  ``%`` are reported as findings rather than miscompiled.
  ``to_percent`` is the reverse direction with the same honesty.
  The round-trip invariant — the original %-template rendered with
  sample values equals the rendered translation with the same
  values — is enforced by the test suite on 300 seeded
  template/value pairs covering every conversion, flag, width and
  precision above.
* ``check_fstring`` — f-string source analysis: given a full
  f-string literal (``f"...{name!r:>10}..."``) or bare inner source,
  it wraps, parses with the runtime's own ``ast`` parser and
  extracts every expression with its conversion, format spec
  (including nested ``{width}`` parts) and position span; syntax
  problems — unbalanced braces or quotes, backslashes in expressions
  (pre-3.12), invalid conversions — come back as findings carrying
  the parser's own message and position. The parser is the oracle,
  so results honestly follow the runtime Python version (PEP 701
  relaxed several 3.11 restrictions).

Input validation is strict and happens before any computation:
unknown mode, non-string template, a template over 4,000 characters,
more than 200 replacement fields, a missing/non-dict mapping (or one
with non-string keys or more than 200 keys), a ``mapping`` outside
render mode, a bad ``direction``, or a rendered result over 100,000
characters raises ``ValueError``. All output is deterministic for a
given runtime version and input.
"""

import ast
import re
import sys
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Conversion letters the real machinery accepts.
_VALID_CONVERSIONS = ("r", "s", "a")

# % conversion types supported by translate_percent.
_PERCENT_TYPES = frozenset("sradi" + "oxXeEfFgGc")

# %-types for which a precision has a .format equivalent (floats only;
# C accepts precision on integers as zero-padding, format rejects it).
_PERCENT_PRECISION_TYPES = frozenset("eEfFgG")

# Mapping %-type -> str.format spec type letter ('' = no type char).
_PERCENT_TYPE_MAP = {
    "s": "", "r": "", "a": "", "c": "c",
    "d": "d", "i": "d", "o": "o", "x": "x", "X": "X",
    "e": "e", "E": "E", "f": "f", "F": "F", "g": "g", "G": "G",
}

_FSTRING_LITERAL_RE = re.compile(r"^[fF](?:'''|\"\"\"|'|\")")

# str.format spec mini-language (subset, for the to_percent direction).
_SPEC_RE = re.compile(
    r"^(?:(?P<fill>.)?(?P<align>[<>=^]))?"
    r"(?P<sign>[+\- ])?"
    r"(?P<alt>#)?"
    r"(?P<zero>0)?"
    r"(?P<width>\d+)?"
    r"(?:[,_])?"
    r"(?:\.(?P<prec>\d+))?"
    r"(?P<type>[bdeEfFgGnosxX%]?)$"
)

# Exceptions the parse stage raises before any value is touched.
_STRUCTURAL_MARKERS = (
    "Single '{' encountered",
    "Single '}' encountered",
    "cannot switch from",
    "Unknown conversion specifier",
    "expected ':' after conversion specifier",
    "Empty attribute in format string",
    "expected '}' before end of string",
    "unmatched '{' in format spec",
    "Max string recursion exceeded",
    "unexpected '{' in field name",
    "Format string contains positional fields",
)


class _ProbeNode:
    """Inert dummy value for sandboxed str.format probing.

    Wraps one plain value (``'x'``, ``7`` or ``2.5``) whose real
    ``__format__`` / ``__repr__`` / ``__str__`` machinery stays in
    charge, while any attribute or index access resolves to another
    node of the same kind — so field paths like ``{0.a[b].c}`` can be
    walked without inventing values, and spec failures surface from
    the genuine formatter.
    """

    __slots__ = ("_v",)

    def __init__(self, value: Any) -> None:
        object.__setattr__(self, "_v", value)

    def __getattr__(self, name: str) -> "_ProbeNode":
        if name == "_v":  # slot not yet set (copy/pickle edge) — never loop
            raise AttributeError(name)
        return _ProbeNode(self._v)

    def __getitem__(self, key: Any) -> "_ProbeNode":
        return _ProbeNode(self._v)

    def __repr__(self) -> str:
        return repr(self._v)

    def __str__(self) -> str:
        return str(self._v)

    def __format__(self, spec: str) -> str:
        return format(self._v, spec)


def _is_structural_message(message: str) -> bool:
    return any(marker in message for marker in _STRUCTURAL_MARKERS)


class _Scan:
    """Result of the static template scan."""

    def __init__(self) -> None:
        self.parts: list[dict[str, Any]] = []
        self.errors: list[dict[str, Any]] = []
        self.field_count = 0


def _scan_field_name(text: str, start: int) -> tuple[int, str]:
    """Scan a field name from ``start``; stop at ':', '!' or '}' at
    bracket depth zero. Returns (end_index, name)."""
    i, n, depth = start, len(text), 0
    while i < n:
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
        elif depth == 0 and ch in ":!}":
            break
        i += 1
    return i, text[start:i]


def _scan_spec(
    text: str, start: int, scan: _Scan, field_start: int
) -> tuple[int, str, list[dict[str, Any]]]:
    """Scan a format spec beginning just after ':' at ``start``.

    Returns ``(end_index, spec_text, nested)`` where ``end_index``
    points past the field's closing ``}`` (or at end of string) and
    ``nested`` holds descriptors for replacement fields found inside
    the spec. Structural problems append to ``scan.errors``.
    """
    n = len(text)
    i = start
    nested: list[dict[str, Any]] = []

    def unmatched() -> None:
        scan.errors.append({
            "span": (field_start, n), "code": "unmatched_brace_in_spec",
            "message": "unmatched '{' in format spec",
            "severity": "error",
        })

    while i < n:
        ch = text[i]
        if ch == "{":
            if text.startswith("{{", i):
                i += 2
                continue
            j, name = _scan_field_name(text, i + 1)
            if j >= n:
                unmatched()
                return n, text[start:n], nested
            conversion = None
            if text[j] == "!":
                if j + 1 >= n:
                    unmatched()
                    return n, text[start:n], nested
                conversion = text[j + 1]
                j += 2
            sub_spec = None
            if j < n and text[j] == ":":
                k = j + 1
                while k < n and text[k] != "}":
                    k += 1
                sub_spec = text[j + 1:k]
                j = k
            if j >= n or text[j] != "}":
                unmatched()
                return n, text[start:n], nested
            nested.append({
                "name": name, "conversion": conversion, "spec": sub_spec,
                "span": (i, j + 1), "nested": [],
            })
            scan.field_count += 1
            i = j + 1
            continue
        if ch == "}":
            return i + 1, text[start:i], nested
        i += 1
    scan.errors.append({
        "span": (field_start, n), "code": "unterminated_field",
        "message": "expected '}' before end of string",
        "severity": "error",
    })
    return n, text[start:n], nested


def _scan_template(template: str) -> _Scan:
    """Static scan of a str.format template into parts + errors.

    Parts are ``{'kind': 'literal'|'escape', 'text', 'span'}`` and
    ``{'kind': 'field', 'name', 'conversion', 'spec', 'has_spec',
    'span', 'nested', 'malformed'}`` in source order.
    """
    scan = _Scan()
    text, n = template, len(template)
    i = 0
    lit_start = 0

    def flush(end: int) -> None:
        if end > lit_start:
            scan.parts.append({
                "kind": "literal", "text": text[lit_start:end],
                "span": (lit_start, end),
            })

    def raw_field(start: int, end: int, name: str) -> None:
        scan.parts.append({
            "kind": "field", "name": name, "conversion": None,
            "spec": None, "has_spec": False, "span": (start, end),
            "nested": [], "malformed": True,
        })
        scan.field_count += 1

    while i < n:
        ch = text[i]
        if ch == "{":
            if text.startswith("{{", i):
                flush(i)
                scan.parts.append({
                    "kind": "escape", "text": "{", "span": (i, i + 2),
                })
                i += 2
                lit_start = i
                continue
            flush(i)
            name_end, name = _scan_field_name(text, i + 1)
            if name_end >= n:
                scan.errors.append({
                    "span": (i, n), "code": "unterminated_field",
                    "message": "expected '}' before end of string",
                    "severity": "error",
                })
                raw_field(i, n, name)
                return scan
            conversion = None
            j = name_end
            malformed = False
            if text[j] == "!":
                if j + 1 >= n:
                    scan.errors.append({
                        "span": (i, n), "code": "unterminated_field",
                        "message": "expected '}' before end of string",
                        "severity": "error",
                    })
                    raw_field(i, n, name)
                    return scan
                conversion = text[j + 1]
                j += 2
                if j >= n or text[j] not in ":}":
                    # a conversion is a single letter followed by ':' or '}'
                    k = j
                    while k < n and text[k] not in ":}":
                        k += 1
                    scan.errors.append({
                        "span": (i, min(k + 1, n)),
                        "code": "malformed_conversion",
                        "message": "expected ':' after conversion "
                                   "specifier",
                        "severity": "error",
                    })
                    malformed = True
                    j = k
            spec = None
            nested: list[dict[str, Any]] = []
            has_spec = False
            if j < n and text[j] == ":":
                has_spec = True
                # _scan_spec returns an index already past the field's
                # closing '}' (or n when unterminated)
                end, spec, nested = _scan_spec(text, j + 1, scan, i)
            else:
                j = min(j, n - 1)  # at '}' here
                end = j + 1 if j < n else n
            scan.parts.append({
                "kind": "field", "name": name, "conversion": conversion,
                "spec": spec, "has_spec": has_spec, "span": (i, end),
                "nested": nested, "malformed": malformed,
            })
            scan.field_count += 1
            i = end
            lit_start = i
            continue
        if ch == "}":
            if text.startswith("}}", i):
                flush(i)
                scan.parts.append({
                    "kind": "escape", "text": "}", "span": (i, i + 2),
                })
                i += 2
                lit_start = i
                continue
            flush(i)
            scan.errors.append({
                "span": (i, i + 1), "code": "stray_close_brace",
                "message": "Single '}' encountered in format string",
                "severity": "error",
            })
            i += 1
            lit_start = i
            continue
        i += 1
    flush(n)
    return scan


def _iter_fields(parts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every field in order, including fields nested inside specs."""
    collected: list[dict[str, Any]] = []

    def walk(nodes: list[dict[str, Any]]) -> None:
        for part in nodes:
            # top-level parts carry kind 'field'; nested spec-field
            # descriptors are fields by construction (no 'kind' key)
            if part.get("kind") not in (None, "field"):
                continue
            collected.append(part)
            walk(part["nested"])

    walk(parts)
    return collected


def _field_first_segment(name: str) -> str:
    """First identifier segment of a field name ('a' for 'a[0].b')."""
    for cut in (".", "["):
        idx = name.find(cut)
        if idx >= 0:
            return name[:idx]
    return name


def _numbering(parts: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify auto/manual numbering and keyword names (nested included)."""
    auto = 0
    manual_max = -1
    keywords: list[str] = []
    order: list[str] = []
    for field in _iter_fields(parts):
        name = field["name"]
        if name == "":
            auto += 1
            order.append("auto")
        elif name.isdigit():
            manual_max = max(manual_max, int(name))
            order.append("manual")
        else:
            key = _field_first_segment(name)
            if key not in keywords:
                keywords.append(key)
            order.append("keyword")
    return {
        "auto": auto, "manual_max": manual_max,
        "keywords": keywords, "order": order,
    }


def _nested_spec_depth(nested: list[dict[str, Any]]) -> int:
    depth = 0
    for sub in nested:
        inner = 1 + _nested_spec_depth(sub.get("nested", []))
        if sub.get("spec"):
            # a nested field carrying its own spec adds a recursion level
            inner = max(inner, 2)
        depth = max(depth, inner)
    return depth


class StringFormatTool(Tool):
    """str.format / f-string / printf-% template analysis tool.

    Attributes:
        max_template_chars (int): Upper bound on template length.
        max_fields (int): Upper bound on replacement field count.
        max_findings (int): Cap on the findings list length.
        max_mapping_keys (int): Cap on render-mapping size.
        max_render_chars (int): Cap on rendered output length.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "string_format_tool"
    description: str = (
        "String format tool — Python str.format template linting, field "
        "extraction, format_map rendering with precise missing-key reports, "
        "printf-% <-> format translation and f-string source checking, "
        "pure Python stdlib, no network required. Template and prompt "
        "family tools (TemplateRenderTool #3559, PromptTemplateLinterTool "
        "#3756, PromptTool #3369) operate on placeholder content; this "
        "tool operates on format-string grammar itself. mode='lint' checks "
        "a template for unmatched { or } ({{ }} escapes honored, error), "
        "mixed auto/manual numbering ({0} with {} — real format raises "
        "cannot switch, error), unknown or malformed conversions (!r/!s/!a "
        "only, error), empty attribute/index in field names (error), "
        "nested replacement fields in specs exceeding CPython's recursion "
        "limit (error), and value-independent spec grammar failures like "
        "{:!} or {:+s} (error); specs that only work for some value types "
        "(like {:d}) and nested-but-legal spec fields are info findings. "
        "Every error claim is confirmed by calling the real str.format "
        "with inert sandboxed dummy args (plain 'x'/7/2.5 semantics, "
        "permissive attribute/index traversal, all exceptions caught, "
        "stdlib only) and error findings are vetoed whenever the real "
        "machinery renders the template. mode='fields' returns each "
        "field's {field_name, index_or_key, auto_numbered, "
        "attribute_chain, index_parts, conversion, format_spec, "
        "position_span}, nested spec fields included. mode='render' "
        "applies str.format_map semantics to a mapping; missing keys are "
        "structured findings naming key and exact span instead of a "
        "KeyError crash, and successful renders come from the real "
        "format_map. mode='translate_percent' converts %-style templates "
        "(%(name)s plus %s %r %a %d %i %o %x %X %e %E %f %F %g %G %c %% "
        "with - + space 0 # flags, widths, precisions, ignored h/l/L "
        "length modifiers) to .format equivalents and back (direction), "
        "flag semantics matching the real machinery (- suppresses "
        "zero-fill, + beats space, # dropped where C ignores it, %s "
        "right-aligns on width); * widths and precision-on-%s are "
        "reported as not_translatable findings; round-trip equivalence "
        "to the original % rendering is test-enforced on 300 seeded "
        "cases. mode='check_fstring' parses a full f-string literal or "
        "bare inner source with the runtime ast parser, extracting "
        "expressions, conversions, format specs and spans, reporting "
        "unbalanced braces/quotes and syntax issues as findings. Strict "
        "validation, size caps, deterministic output."
    )

    MODES: ClassVar[tuple] = (
        "lint", "fields", "render", "translate_percent", "check_fstring",
    )
    DIRECTIONS: ClassVar[tuple] = ("to_format", "to_percent")
    PROBE_KINDS: ClassVar[tuple] = ("str", "int", "float")

    max_template_chars: ClassVar[int] = 4_000
    max_fields: ClassVar[int] = 200
    max_findings: ClassVar[int] = 50
    max_mapping_keys: ClassVar[int] = 200
    max_render_chars: ClassVar[int] = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any,
        template: Any = None,
        mapping: Any = None,
        direction: Any = None,
    ) -> dict[str, Any]:
        """Run one format-template analysis operation.

        Args:
            mode (str): One of ``lint`` / ``fields`` / ``render`` /
                ``translate_percent`` / ``check_fstring``.
            template (str): The format template (for ``check_fstring``,
                a full f-string literal or bare inner source).
            mapping (dict): Render mode only — the value mapping.
            direction (str): translate_percent only — ``to_format``
                (default) or ``to_percent``.

        Returns:
            Dict[str, Any]: The mode's payload.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        template_string = self._validate_template(template)
        if mode == "lint":
            self._reject_option("mapping", mapping, allowed_modes=("render",))
            self._reject_option(
                "direction", direction, allowed_modes=("translate_percent",))
            return self._run_lint(template_string)
        if mode == "fields":
            self._reject_option("mapping", mapping, allowed_modes=("render",))
            self._reject_option(
                "direction", direction, allowed_modes=("translate_percent",))
            return self._run_fields(template_string)
        if mode == "render":
            self._reject_option(
                "direction", direction, allowed_modes=("translate_percent",))
            value_map = self._validate_mapping(mapping)
            return self._run_render(template_string, value_map)
        if mode == "translate_percent":
            self._reject_option("mapping", mapping, allowed_modes=("render",))
            way = "to_format" if direction is None else direction
            if way not in self.DIRECTIONS:
                self._invalid(
                    f"direction must be one of: {', '.join(self.DIRECTIONS)} "
                    f"(got {direction!r})"
                )
            if way == "to_format":
                return self._run_percent_to_format(template_string)
            return self._run_format_to_percent(template_string)
        # check_fstring
        self._reject_option("mapping", mapping, allowed_modes=("render",))
        self._reject_option(
            "direction", direction, allowed_modes=("translate_percent",))
        return self._run_check_fstring(template_string)

    # ------------------------------------------------------------------ #
    # Validation helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _invalid(message: str) -> None:
        raise ValueError(message)

    def _validate_template(self, template: Any) -> str:
        if not isinstance(template, str):
            self._invalid(
                f"template must be a string (got {type(template).__name__})")
        if len(template) > self.max_template_chars:
            self._invalid(
                f"template exceeds {self.max_template_chars} characters "
                f"(got {len(template)})"
            )
        return template

    def _validate_mapping(self, mapping: Any) -> dict:
        if not isinstance(mapping, dict):
            self._invalid(
                f"mapping must be a dict (got {type(mapping).__name__})")
        if len(mapping) > self.max_mapping_keys:
            self._invalid(
                f"mapping exceeds {self.max_mapping_keys} keys "
                f"(got {len(mapping)})"
            )
        for key in mapping:
            if not isinstance(key, str):
                self._invalid(f"mapping keys must be strings (got {key!r})")
        return mapping

    def _reject_option(self, name: str, value: Any, allowed_modes: tuple) -> None:
        if value is not None:
            self._invalid(
                f"{name} is only accepted in mode(s): "
                f"{', '.join(allowed_modes)} (got {value!r})"
            )

    def _checked_scan(self, template: str) -> _Scan:
        scan = _scan_template(template)
        if scan.field_count > self.max_fields:
            self._invalid(
                f"template has more than {self.max_fields} replacement "
                f"fields (got {scan.field_count})"
            )
        return scan

    # ------------------------------------------------------------------ #
    # Probe engine — the real str.format machinery, sandboxed
    # ------------------------------------------------------------------ #

    def _probe_format(
        self, template: str, numbering: dict[str, Any]
    ) -> dict[str, Any]:
        """Call the real ``str.format`` with inert dummy arguments.

        Value fields get one plain kind (``'x'`` / ``7`` / ``2.5``);
        fields nested inside format specs (width/precision/fill/
        alignment tokens) get digit-string or single-char candidates,
        because that is what spec slots accept. A combination is
        "ok" when the real machinery renders with it. An
        ``IndexError`` (rendering out-ran the dummy count because
        parse and render interleave) triggers one deterministic
        count bump and retry.
        """
        roles = self._slot_roles(template, numbering)
        ok_kinds: list[str] = []
        failures: dict[str, dict[str, Any]] = {}
        bumped = False
        combos = [
            (kind, nested)
            for kind in ("str", "int", "float")
            for nested in ("7", "x")
        ]
        for kind, nested_value in combos:
            plain = {"str": "x", "int": 7, "float": 2.5}[kind]
            count = roles["count"]
            attempt = 0
            rendered = False
            while True:
                args = []
                for slot in range(count):
                    role = roles["pos_roles"].get(slot, "value")
                    args.append(
                        _ProbeNode(plain if role == "value" else nested_value)
                    )
                kwargs = {
                    key: _ProbeNode(
                        plain if role == "value" else nested_value
                    )
                    for key, role in roles["kw_roles"].items()
                }
                try:
                    template.format(*args, **kwargs)
                    rendered = True
                    break
                except IndexError:
                    if attempt == 0 and count < self.max_fields:
                        attempt += 1
                        count = count + 10
                        bumped = True
                        continue
                    failures[f"{kind}/{nested_value}"] = {
                        "exception": "IndexError",
                        "message": "replacement index beyond dummy count",
                        "family": "path_or_value",
                    }
                    break
                except Exception as exc:  # noqa: BLE001 - sandbox
                    message = str(exc)
                    failures[f"{kind}/{nested_value}"] = {
                        "exception": type(exc).__name__,
                        "message": message,
                        "family": (
                            "structural"
                            if _is_structural_message(message)
                            else "spec_or_value"
                        ),
                    }
                    break
            if rendered:
                ok_kinds.append(kind)
        return {
            "ok_kinds": sorted(set(ok_kinds)),
            "failures": failures,
            "bumped": bumped,
        }

    def _slot_roles(
        self, template: str, numbering: dict[str, Any]
    ) -> dict[str, Any]:
        """Classify every positional slot and keyword name by its
        dominant role: a slot referenced only from inside a format
        spec is a spec token slot; anything else is a value slot."""
        pos_roles: dict[int, str] = {}
        kw_roles: dict[str, str] = {}
        auto_index = 0

        def record(name: str, role: str) -> None:
            nonlocal auto_index
            if name == "":
                slot = auto_index
                auto_index += 1
                key: Any = ("pos", slot)
            elif name.isdigit():
                key = ("pos", int(name))
            else:
                key = ("kw", _field_first_segment(name))
            store = pos_roles if key[0] == "pos" else kw_roles
            slot_key = key[1]
            if store.get(slot_key) != "value":
                store[slot_key] = role

        def walk(nodes: list[dict[str, Any]], role: str) -> None:
            for part in nodes:
                if part.get("kind") not in (None, "field"):
                    continue
                record(part["name"], role)
                walk(part["nested"], "nested")

        scan = _scan_template(template)
        walk(scan.parts, "value")
        count = max(numbering["auto"], numbering["manual_max"] + 1, 1)
        # a slot referenced only after an IndexError bump stays a value
        return {
            "pos_roles": pos_roles,
            "kw_roles": kw_roles,
            "count": count,
        }

    @staticmethod
    def _value_independent_failure(
        failures: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        """A failure shared by every dummy combination: the
        value-independent proof an error claim needs.

        Every combination must have failed inside the format machinery
        (a ``ValueError``/``TypeError`` — never an ``IndexError``,
        which is a dummy-count artifact). Messages may mention the
        dummy type; a template no inert combination can render is
        unrenderable by the real machinery with plain values, which
        is an error.
        """
        expected = len(StringFormatTool.PROBE_KINDS) * 2  # kinds x spec tokens
        if len(failures) != expected:
            return None
        sample = next(iter(failures.values()))
        if sample["exception"] not in ("ValueError", "TypeError"):
            return None
        return sample

    # ------------------------------------------------------------------ #
    # lint mode
    # ------------------------------------------------------------------ #

    def _run_lint(self, template: str) -> dict[str, Any]:
        scan = self._checked_scan(template)
        numbering = _numbering(scan.parts)
        findings: list[dict[str, Any]] = []

        def add(span, code, message, severity):
            findings.append({
                "span": [span[0], span[1]], "code": code,
                "message": message, "severity": severity,
            })

        # -- static candidate findings (confirmed or vetoed below) --
        for error in scan.errors:
            add(error["span"], error["code"], error["message"], "error")

        if numbering["auto"] and numbering["manual_max"] >= 0:
            first_style = numbering["order"][0]
            for field, style in zip(
                _iter_fields(scan.parts), numbering["order"]
            ):
                if style != first_style:
                    if first_style == "auto":
                        message = (
                            "cannot switch from automatic field numbering "
                            "to manual field specification"
                        )
                    else:
                        message = (
                            "cannot switch from manual field specification "
                            "to automatic field numbering"
                        )
                    add(
                        field["span"], "mixed_numbering",
                        f"mixed automatic ({{}}) and manual ({{0}}) "
                        f"numbering — str.format raises ValueError: "
                        f"{message}",
                        "error",
                    )
                    break

        for field in _iter_fields(scan.parts):
            name = field["name"]
            span = field["span"]
            if field["conversion"] is not None and \
                    field["conversion"] not in _VALID_CONVERSIONS:
                add(
                    span, "unknown_conversion",
                    f"Unknown conversion specifier {field['conversion']!r} "
                    "— only !r, !s and !a exist",
                    "error",
                )
            if name.endswith(".") or "[]" in name or ".." in name:
                add(
                    span, "empty_attribute_or_index",
                    "Empty attribute in format string — the real machinery "
                    "raises ValueError for empty attributes and empty [] "
                    "indices",
                    "error",
                )
            if field["nested"]:
                if _nested_spec_depth(field["nested"]) >= 2:
                    add(
                        span, "spec_recursion_exceeded",
                        "a nested replacement field inside a spec carries a "
                        "spec of its own — str.format raises ValueError: "
                        "Max string recursion exceeded",
                        "error",
                    )
                else:
                    add(
                        span, "nested_replacement_in_spec",
                        "spec uses nested replacement fields — legal, but "
                        "CPython allows only one nesting level",
                        "info",
                    )
            if name and name != name.strip():
                add(
                    span, "field_name_whitespace",
                    f"field name {name!r} has leading/trailing whitespace — "
                    "it is a keyword lookup of exactly that key",
                    "info",
                )
            spec = field["spec"]
            if spec is not None and spec.endswith("n") and \
                    field["conversion"] is None:
                add(
                    span, "locale_aware_n_specifier",
                    "the 'n' format spec type uses the runtime locale for "
                    "digit grouping — output varies across locales",
                    "info",
                )

        seen_names: set[str] = set()
        for part in scan.parts:
            if part["kind"] != "field":
                continue
            name = part["name"]
            if name in seen_names:
                add(
                    part["span"], "duplicate_field_reference",
                    f"field {name!r} referenced again",
                    "info",
                )
            seen_names.add(name)

        if scan.field_count == 0:
            add(
                (0, len(template)), "no_placeholders",
                "template has no replacement fields — it renders to itself",
                "warning",
            )

        # -- the probe: confirm or veto every error claim --
        probe = self._probe_format(template, numbering)
        if probe["ok_kinds"]:
            # The real machinery renders this template with inert
            # dummies: no error claim may survive.
            findings = [f for f in findings if f["severity"] != "error"]
            failing = sorted(set(self.PROBE_KINDS) - set(probe["ok_kinds"]))
            if failing:
                first_span = next(
                    (part["span"] for part in scan.parts
                     if part["kind"] == "field"),
                    (0, len(template)),
                )
                findings.append({
                    "span": [first_span[0], first_span[1]],
                    "code": "type_dependent_spec",
                    "message": "spec renders for inert values of kind(s) "
                               f"{', '.join(probe['ok_kinds'])} but not: "
                               f"{', '.join(failing)}",
                    "severity": "info",
                })
        else:
            proof = self._value_independent_failure(probe["failures"])
            has_static_error = any(
                f["severity"] == "error" for f in findings
            )
            if proof is not None and not has_static_error:
                add(
                    (0, len(template)), "value_independent_spec_error",
                    f"str.format raises {proof['exception']} for every "
                    f"inert value kind: {proof['message']}",
                    "error",
                )
            elif proof is None and not has_static_error:
                sample = next(iter(probe["failures"].values()))
                add(
                    (0, len(template)), "probe_exhausted",
                    "template did not render with any inert dummy kind "
                    f"({sample['exception']}: {sample['message']}) — "
                    "value-shape dependent, verify with real values",
                    "info",
                )

        findings = findings[: self.max_findings]
        verdict = (
            "error" if any(f["severity"] == "error" for f in findings)
            else "ok"
        )
        return {
            "template": template,
            "verdict": verdict,
            "findings": findings,
            "probe": {
                "checked": True,
                "ok_kinds": probe["ok_kinds"],
                "positional_slots": max(
                    numbering["auto"], numbering["manual_max"] + 1
                ),
                "keyword_names": numbering["keywords"],
                "count_bumped": probe["bumped"],
            },
        }

    # ------------------------------------------------------------------ #
    # fields mode
    # ------------------------------------------------------------------ #

    @staticmethod
    def _describe_field(field: dict[str, Any]) -> dict[str, Any]:
        name = field["name"]
        attribute_chain: list[str] = []
        index_parts: list[dict[str, Any]] = []
        index_or_key: Any = None
        if name.isdigit():
            index_or_key = int(name)
        elif name != "":
            first = _field_first_segment(name)
            index_or_key = int(first) if first.isdigit() else first
        remainder = name
        cursor = 0
        while cursor < len(remainder):
            ch = remainder[cursor]
            if ch == ".":
                cursor += 1
                end = cursor
                while end < len(remainder) and remainder[end] not in ".[":
                    end += 1
                attribute_chain.append(remainder[cursor:end])
                cursor = end
            elif ch == "[":
                close = remainder.find("]", cursor)
                if close < 0:
                    index_parts.append({
                        "raw": remainder[cursor + 1:], "type": "unterminated",
                    })
                    cursor = len(remainder)
                else:
                    raw = remainder[cursor + 1:close]
                    entry: dict[str, Any] = {
                        "raw": raw,
                        "type": "int" if raw.isdigit() else "str",
                    }
                    if entry["type"] == "int":
                        entry["value"] = int(raw)
                    index_parts.append(entry)
                    cursor = close + 1
            else:
                end = cursor
                while end < len(remainder) and remainder[end] not in ".[":
                    end += 1
                cursor = end
        return {
            "field_name": name,
            "index_or_key": index_or_key,
            "auto_numbered": name == "",
            "attribute_chain": attribute_chain,
            "index_parts": index_parts,
            "conversion": field.get("conversion"),
            "format_spec": field.get("spec"),
            "has_spec": bool(field.get("has_spec")),
            "position_span": [field["span"][0], field["span"][1]],
            "nested": [
                StringFormatTool._describe_field(sub)
                for sub in field.get("nested", [])
            ],
        }

    def _run_fields(self, template: str) -> dict[str, Any]:
        scan = self._checked_scan(template)
        numbering = _numbering(scan.parts)
        fields = [
            self._describe_field(part)
            for part in scan.parts if part["kind"] == "field"
        ]
        return {
            "template": template,
            "fields": fields,
            "field_count": scan.field_count,
            "top_level_field_count": len(fields),
            "auto_field_count": numbering["auto"],
            "max_manual_index": (
                numbering["manual_max"] if numbering["manual_max"] >= 0
                else None
            ),
            "keyword_names": numbering["keywords"],
            "escape_count": sum(
                1 for part in scan.parts if part["kind"] == "escape"
            ),
            "scan_errors": [
                {
                    "span": [e["span"][0], e["span"][1]],
                    "code": e["code"], "message": e["message"],
                }
                for e in scan.errors
            ],
        }

    # ------------------------------------------------------------------ #
    # render mode
    # ------------------------------------------------------------------ #

    def _run_render(self, template: str, mapping: dict) -> dict[str, Any]:
        scan = self._checked_scan(template)
        findings: list[dict[str, Any]] = []

        positional_span = None
        for field in _iter_fields(scan.parts):
            if field["name"] == "" or field["name"].isdigit():
                positional_span = field["span"]
                break
        if positional_span is not None:
            findings.append({
                "span": [positional_span[0], positional_span[1]],
                "code": "positional_field_unsupported",
                "message": "str.format_map cannot render positional field "
                           f"{template[positional_span[0]:positional_span[1]]!r} "
                           "— it raises ValueError: Format string contains "
                           "positional fields",
                "severity": "error",
            })

        missing: list[dict[str, Any]] = []
        for field in _iter_fields(scan.parts):
            name = field["name"]
            if name == "" or name.isdigit():
                continue
            key = _field_first_segment(name)
            if key not in mapping:
                missing.append({
                    "key": key,
                    "field_span": [field["span"][0], field["span"][1]],
                    "field": template[field["span"][0]:field["span"][1]],
                })

        if missing:
            for entry in missing[: self.max_findings]:
                findings.append({
                    "span": entry["field_span"],
                    "code": "missing_key",
                    "message": f"mapping is missing key {entry['key']!r} "
                               f"for field {entry['field']!r}",
                    "severity": "error",
                    "key": entry["key"],
                })
            if len(missing) > self.max_findings:
                findings.append({
                    "span": [0, 0], "code": "more_missing_keys",
                    "message": f"{len(missing) - self.max_findings} more "
                               "missing keys not listed",
                    "severity": "info",
                })
            return {
                "template": template,
                "rendered": None,
                "ok": False,
                "findings": findings,
                "missing_keys": [entry["key"] for entry in missing],
            }

        if any(f["severity"] == "error" for f in findings):
            return {
                "template": template,
                "rendered": None,
                "ok": False,
                "findings": findings,
                "missing_keys": [],
            }

        try:
            rendered = template.format_map(mapping)
        except KeyError as exc:
            key = exc.args[0] if exc.args else None
            findings.append({
                "span": [0, len(template)],
                "code": "missing_key",
                "message": f"rendering raised KeyError for {key!r} — "
                           "a nested path key absent from the mapping",
                "severity": "error",
                "key": key,
            })
            return {
                "template": template, "rendered": None, "ok": False,
                "findings": findings, "missing_keys": [key],
            }
        except Exception as exc:  # noqa: BLE001 - report, never crash
            findings.append({
                "span": [0, len(template)],
                "code": "render_failed",
                "message": f"format_map raised {type(exc).__name__}: "
                           f"{exc}",
                "severity": "error",
            })
            return {
                "template": template, "rendered": None, "ok": False,
                "findings": findings, "missing_keys": [],
            }

        if len(rendered) > self.max_render_chars:
            self._invalid(
                f"rendered output exceeds {self.max_render_chars} "
                f"characters (got {len(rendered)})"
            )
        return {
            "template": template,
            "rendered": rendered,
            "ok": True,
            "findings": findings,
            "missing_keys": [],
        }

    # ------------------------------------------------------------------ #
    # translate_percent — % -> format
    # ------------------------------------------------------------------ #

    _PERCENT_FIELD_RE = re.compile(
        r"""%
        (?:(?P<key>\([^)\s]*\)))?
        (?P<flags>[-+ 0#]*)
        (?P<width>\*|\d+)?
        (?:\.(?P<prec>\*|\d+))?
        (?P<length>[hlL])?
        (?P<type>[a-zA-Z%])?
        """,
        re.VERBOSE,
    )

    @staticmethod
    def _escape_literal(text: str) -> str:
        return text.replace("{", "{{").replace("}", "}}")

    def _run_percent_to_format(self, template: str) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        out: list[str] = []
        fields_out: list[dict[str, Any]] = []
        i, n = 0, len(template)
        positional = 0
        keywords: list[str] = []
        has_named = has_unnamed = False

        def add(span, code, message, severity):
            findings.append({
                "span": [span[0], span[1]], "code": code,
                "message": message, "severity": severity,
            })

        while i < n:
            if template[i] != "%":
                start = i
                while i < n and template[i] != "%":
                    i += 1
                out.append(
                    template[start:i]
                    .replace("{", "{{").replace("}", "}}")
                )
                continue
            if template.startswith("%%", i):
                out.append("%")
                i += 2
                continue
            match = self._PERCENT_FIELD_RE.match(template, i)
            conv = match.group("type") if match else None
            if conv is None:
                add(
                    (i, min(i + 2, n)), "incomplete_format",
                    "incomplete format — the real % operator raises "
                    "ValueError('incomplete format') here",
                    "error",
                )
                out.append(template[i])
                i += 1
                continue
            if conv not in _PERCENT_TYPES:
                add(
                    (i, match.end()), "unsupported_format_character",
                    f"unsupported format character {conv!r}",
                    "error",
                )
                out.append(self._escape_literal(template[i:match.end()]))
                i = match.end()
                continue
            flags = match.group("flags") or ""
            width = match.group("width")
            prec = match.group("prec")
            key = match.group("key")
            span = (i, match.end())
            i = match.end()

            if "*" in (width or "") or "*" in (prec or ""):
                add(span, "not_translatable",
                    "* width/precision are computed from extra positional "
                    "arguments — no static .format equivalent", "error")
                out.append(self._escape_literal(template[span[0]:span[1]]))
                continue
            if prec is not None and conv not in _PERCENT_PRECISION_TYPES:
                add(span, "not_translatable",
                    f"precision on %{conv} has no .format equivalent "
                    "(string truncation for s/r/a/c; C-style zero-padding "
                    "for d/i/o/x/X, which format spec grammar rejects)",
                    "error")
                out.append(self._escape_literal(template[span[0]:span[1]]))
                continue

            if key is not None:
                key_name = key[1:-1]
                has_named = True
                if key_name not in keywords:
                    keywords.append(key_name)
                placeholder = "{" + key_name
            else:
                has_unnamed = True
                placeholder = "{" + str(positional)
                positional += 1

            if conv == "r":
                placeholder += "!r"
            elif conv == "a":
                placeholder += "!a"

            spec_parts: list[str] = []
            left = "-" in flags
            plus = "+" in flags
            space = " " in flags
            zero = "0" in flags
            alt = "#" in flags
            ftype = _PERCENT_TYPE_MAP[conv]
            if conv in ("s", "r", "a", "c"):
                # C ignores +, space, # and 0 for these; width aligns
                # right unless '-', while {} left-aligns by default.
                if width is not None:
                    spec_parts.append("<" if left else ">")
                    spec_parts.append(width)
            else:
                # spec grammar order: [align][sign][#][0][width][.prec]
                if left:
                    spec_parts.append("<")
                if plus:
                    spec_parts.append("+")
                elif space:
                    spec_parts.append(" ")
                if alt and conv not in ("d", "i"):
                    spec_parts.append("#")
                if zero and width is not None and not left:
                    spec_parts.append("0")
                if width is not None:
                    spec_parts.append(width)
                if prec is not None:
                    spec_parts.append("." + prec)
            spec = "".join(spec_parts) + ftype
            if spec:
                placeholder += ":" + spec
            placeholder += "}"
            out.append(placeholder)
            fields_out.append({
                "span": [span[0], span[1]],
                "percent": template[span[0]:span[1]],
                "format": placeholder,
                "mapping_key": key[1:-1] if key else None,
                "flags": flags,
                "width": width,
                "precision": prec,
                "type": conv,
            })
            if conv == "c":
                add(span, "percent_c_int_only",
                    "%c equivalence holds for int code points; a str "
                    "argument works with %c but {:c} raises ValueError",
                    "info")

        if has_named and has_unnamed:
            add((0, len(template)), "mixed_named_positional",
                "template mixes %(name)s and positional fields — the real "
                "% operator cannot take a mapping and extra positional "
                "values from one operand", "error")

        findings = findings[: self.max_findings]
        translatable = not any(f["severity"] == "error" for f in findings)
        translation = "".join(out)
        if translatable:
            check = _scan_template(translation)
            for error in check.errors:
                add(error["span"], "internal_scan_error",
                    error["message"], "error")
            translatable = not any(
                f["severity"] == "error" for f in findings
            )
        return {
            "template": template,
            "direction": "to_format",
            "translation": translation,
            "fields": fields_out,
            "positional_count": positional,
            "keyword_names": keywords,
            "findings": findings,
            "translatable": translatable,
        }

    # ------------------------------------------------------------------ #
    # translate_percent — format -> %
    # ------------------------------------------------------------------ #

    def _run_format_to_percent(self, template: str) -> dict[str, Any]:
        scan = self._checked_scan(template)
        numbering = _numbering(scan.parts)
        findings: list[dict[str, Any]] = []

        def add(span, code, message, severity):
            findings.append({
                "span": [span[0], span[1]], "code": code,
                "message": message, "severity": severity,
            })

        has_keyword = numbering["keywords"] and scan.field_count > 0
        has_positional = (
            numbering["auto"] > 0 or numbering["manual_max"] >= 0
        )
        if has_keyword and has_positional:
            add(
                (0, len(template)), "mixed_named_positional",
                "template mixes keyword and positional fields — one % "
                "operand cannot supply both a mapping and extra "
                "positional values", "error",
            )

        out: list[str] = []
        translated: list[dict[str, Any]] = []
        auto_index = 0
        expected_manual = 0
        for part in scan.parts:
            if part["kind"] == "literal":
                out.append(part["text"].replace("%", "%%"))
                continue
            if part["kind"] == "escape":
                out.append(part["text"])
                continue
            name = part["name"]
            conversion = part["conversion"]
            spec = part["spec"] if part["has_spec"] else None
            span = part["span"]
            source = template[span[0]:span[1]]
            reasons: list[str] = []

            if part["nested"]:
                reasons.append("nested replacement fields in spec")
            if conversion not in (None, "r", "s", "a"):
                reasons.append(f"conversion !{conversion}")

            flags = ""
            width = ""
            prec = ""
            ftype = "s"
            if conversion == "r":
                ftype = "r"
            elif conversion == "a":
                ftype = "a"

            if spec is not None:
                parsed = _SPEC_RE.match(spec)
                if parsed is None:
                    reasons.append(f"spec {spec!r} outside the printf subset")
                else:
                    groups = parsed.groupdict()
                    align = groups["align"]
                    fill = groups["fill"]
                    sign = groups["sign"]
                    spec_type = groups["type"] or ""
                    if groups["width"] is not None:
                        width = groups["width"]
                    if groups["prec"] is not None:
                        prec = "." + groups["prec"]
                    if "," in spec or "_" in spec:
                        reasons.append("digit grouping (,/_)")
                    if spec_type == "n":
                        reasons.append("locale-aware 'n' type")
                    elif spec_type and spec_type not in (
                            "s", "d", "o", "x", "X", "e", "E", "f", "F",
                            "g", "G", "c"):
                        reasons.append(f"spec type {spec_type!r}")
                    if fill not in (None, " ") and align is not None:
                        reasons.append(
                            f"fill character {fill!r} — % pads with spaces "
                            "only (except sign-aware zero fill)")
                    string_like = (
                        spec_type in ("", "s")
                        and conversion in (None, "s", "r", "a")
                    )
                    if string_like:
                        if conversion in ("r", "a") and spec_type == "s":
                            pass  # '{!r:s}' behaves as plain !r
                        if sign:
                            reasons.append(
                                f"sign {sign!r} with a string type — "
                                "format raises, %s ignores it")
                        if groups["alt"]:
                            reasons.append("'#' with a string type")
                        if groups["zero"] and width:
                            reasons.append(
                                "zero-fill on strings ({:05} pads zeros "
                                "right, %0s ignores the flag)")
                        if prec:
                            reasons.append("precision on strings")
                        if width and align is None:
                            reasons.append(
                                "width without align is ambiguous for "
                                "strings (format left-aligns, %s "
                                "right-aligns)")
                        if align == "<":
                            flags += "-"
                        elif align in (">", None):
                            pass
                        else:
                            reasons.append(f"align {align!r} on strings")
                    else:
                        if conversion in ("r", "a"):
                            reasons.append(
                                f"conversion !{conversion} combined with "
                                f"numeric type {spec_type!r}")
                        else:
                            ftype = spec_type
                        if align == "<":
                            flags += "-"
                        elif align in (">", None):
                            pass
                        elif align == "^":
                            reasons.append("center align (^)")
                        elif align == "=":
                            if not (groups["zero"] or fill == "0"):
                                reasons.append(
                                    "'=' align without zero fill puts the "
                                    "sign before the padding — % cannot "
                                    "express it")
                        if groups["zero"] and width:
                            if align == "<":
                                reasons.append(
                                    "zero-fill with left align — % ignores "
                                    "0 together with '-'")
                            else:
                                flags += "0"
                        if fill == "0" and align == ">":
                            reasons.append(
                                "'>' align with 0 fill puts zeros before "
                                "the sign — only %0d's sign-aware padding "
                                "matches '=' align")
                        if sign == "+":
                            flags += "+"
                        elif sign == " ":
                            flags += " "
                        if groups["alt"]:
                            flags += "#"
                        if prec and spec_type == "c":
                            reasons.append("precision on %c")

            slot: str | None = None
            percent_name: str | None = None
            if name == "":
                slot = str(auto_index)
                auto_index += 1
                percent_name = None
            elif name.isdigit():
                if int(name) != expected_manual:
                    reasons.append(
                        "manual field indices out of order — % consumes "
                        "values positionally")
                else:
                    expected_manual += 1
                slot = name
                percent_name = None
            else:
                percent_name = _field_first_segment(name)
                if name != percent_name:
                    reasons.append("attribute/index paths")
                slot = None

            if reasons:
                add(span, "not_translatable",
                    f"field {source!r}: "
                    + "; ".join(dict.fromkeys(reasons)),
                    "error")
                out.append(source)
                continue
            head = "%(" + percent_name + ")" if percent_name is not None else "%"
            percent_field = head + flags + width + prec + ftype
            out.append(percent_field)
            translated.append({
                "span": [span[0], span[1]],
                "format": source,
                "percent": percent_field,
            })

        findings = findings[: self.max_findings]
        return {
            "template": template,
            "direction": "to_percent",
            "translation": "".join(out),
            "fields": translated,
            "findings": findings,
            "translatable": not any(
                f["severity"] == "error" for f in findings
            ),
        }

    # ------------------------------------------------------------------ #
    # check_fstring mode
    # ------------------------------------------------------------------ #

    def _run_check_fstring(self, template: str) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        def add(span, code, message, severity):
            findings.append({
                "span": [span[0], span[1]], "code": code,
                "message": message, "severity": severity,
            })

        def syntax_payload(exc: SyntaxError, source: str, prefix_len: int,
                           kind: str) -> dict[str, Any]:
            line = exc.lineno or 1
            column = exc.offset or 1
            absolute = min(
                self._absolute_offset(source, line, column, prefix_len),
                len(template),
            )
            add(
                (absolute, min(absolute + 1, len(template))),
                "fstring_syntax_error",
                f"{exc.msg} (line {line}, column {column})",
                "error",
            )
            return {
                "template": template, "kind": kind,
                "expressions": [], "literal_parts": [],
                "findings": findings, "ok": False,
                "runtime_python": f"{sys.version_info.major}."
                                  f"{sys.version_info.minor}",
            }

        tree: ast.AST | None = None
        sq3, dq3 = chr(39) * 3, chr(34) * 3
        if _FSTRING_LITERAL_RE.match(template):
            quote = sq3 if template[1:4] == sq3 else (
                dq3 if template[1:4] == dq3 else template[1]
            )
            prefix_len = 1 + len(quote)
            inner = template[prefix_len:max(len(template) - len(quote), prefix_len)]
            source = template
            kind = "literal"
            try:
                tree = ast.parse(source, mode="eval")
            except SyntaxError as exc:
                return syntax_payload(exc, source, prefix_len, kind)
        else:
            candidates = [dq3, sq3]
            chosen = None
            for marker in candidates:
                if marker in template:
                    continue
                source = "f" + marker + template + marker
                try:
                    tree = ast.parse(source, mode="eval")
                    chosen = marker
                    break
                except SyntaxError:
                    continue
            if chosen is None:
                marker = next(
                    (m for m in candidates if m not in template), None
                )
                if marker is None:
                    add((0, len(template)), "unquotable_source",
                        "inner source contains both triple-quote forms — "
                        "cannot wrap for parsing", "error")
                    return {
                        "template": template, "kind": "inner_source",
                        "expressions": [], "literal_parts": [],
                        "findings": findings, "ok": False,
                    }
                source = "f" + marker + template + marker
                prefix_len = 1 + len(marker)
                try:
                    tree = ast.parse(source, mode="eval")
                except SyntaxError as exc:
                    return syntax_payload(exc, source, prefix_len,
                                          "inner_source")
            else:
                prefix_len = 1 + len(chosen)
            inner = template
            kind = "inner_source"

        assert tree is not None
        if not isinstance(tree.body, ast.JoinedStr):
            add((0, len(template)), "not_an_fstring",
                "the source parses successfully but is not an f-string "
                "literal expression", "error")
            return {
                "template": template, "kind": kind,
                "expressions": [], "literal_parts": [],
                "findings": findings, "ok": False,
                "runtime_python": f"{sys.version_info.major}."
                                  f"{sys.version_info.minor}",
            }

        expressions: list[dict[str, Any]] = []
        literal_parts: list[str] = []
        nested_seen = False

        def spec_text(spec_node: ast.expr) -> str:
            parts: list[str] = []
            for value in getattr(spec_node, "values", []):
                if isinstance(value, ast.Constant):
                    parts.append(str(value.value))
                elif isinstance(value, ast.FormattedValue):
                    inner_expr = ast.unparse(value.value)
                    conversion = ""
                    if getattr(value, "conversion", -1) > 0:
                        conversion = "!" + chr(value.conversion)
                    sub_spec = ""
                    if value.format_spec is not None:
                        sub_spec = ":" + spec_text(value.format_spec)
                    parts.append("{" + inner_expr + conversion + sub_spec + "}")
            return "".join(parts)

        # Spans: CPython 3.11 reports every FormattedValue with the
        # whole f-string's position, so exact spans come from the
        # template scanner (same replacement-field grammar), aligned
        # to the AST nodes by order of appearance.
        scan = _scan_template(inner)
        offset = prefix_len if kind == "literal" else 0

        def visit(joined: ast.JoinedStr, depth: int, outer_span: tuple,
                  own_fields: list | None, collect_literals: bool) -> None:
            nonlocal nested_seen
            fields = list(own_fields) if own_fields is not None else []
            index = 0
            for value in joined.values:
                if isinstance(value, ast.Constant):
                    if collect_literals:
                        literal_parts.append(str(value.value))
                    continue
                if not isinstance(value, ast.FormattedValue):
                    continue
                span = outer_span
                if fields and index < len(fields):
                    field = fields[index]
                    span = (field["span"][0] + offset,
                            field["span"][1] + offset)
                index += 1
                if depth > 1:
                    nested_seen = True
                conversion = None
                if getattr(value, "conversion", -1) > 0:
                    conversion = chr(value.conversion)
                spec = None
                nested_spec_fields: list[str] = []
                if value.format_spec is not None:
                    spec = spec_text(value.format_spec)
                    nested_spec_fields = [
                        ast.unparse(v.value)
                        for v in ast.walk(value.format_spec)
                        if isinstance(v, ast.FormattedValue)
                    ]
                expressions.append({
                    "expression": ast.unparse(value.value),
                    "conversion": conversion,
                    "format_spec": spec,
                    "position_span": [span[0], span[1]],
                    "depth": depth,
                    "nested_spec_fields": nested_spec_fields,
                })
                if value.format_spec is not None:
                    nested = []
                    if fields and index - 1 < len(fields):
                        nested = fields[index - 1].get("nested", [])
                    visit(value.format_spec, depth, span, nested, False)
                # expressions nested inside the expression text (an
                # inner f-string): spans fall back to this field's span
                visit_expr(value.value, depth + 1, span)

        def visit_expr(node: ast.AST, depth: int, outer_span: tuple) -> None:
            if isinstance(node, ast.JoinedStr):
                visit(node, depth, outer_span, None, False)
                return
            for child in ast.iter_child_nodes(node):
                visit_expr(child, depth, outer_span)

        top_fields = [part for part in scan.parts if part["kind"] == "field"]
        visit(tree.body, 1, (0, len(template)), top_fields, True)
        if nested_seen:
            add((0, len(template)), "nested_fstring_in_expression",
                "an f-string appears inside an expression — before "
                "Python 3.12 (PEP 701) its quotes must differ from the "
                "outer f-string's and backslashes are forbidden",
                "info")
        return {
            "template": template,
            "kind": kind,
            "expressions": expressions,
            "literal_parts": literal_parts,
            "findings": findings,
            "ok": not any(f["severity"] == "error" for f in findings),
            "runtime_python": f"{sys.version_info.major}."
                              f"{sys.version_info.minor}",
        }

    @staticmethod
    def _absolute_offset(
        source: str, line: int, column: int, prefix_len: int
    ) -> int:
        offset = 0
        current_line = 1
        for char in source:
            if current_line >= line:
                break
            offset += 1
            if char == "\n":
                current_line += 1
        offset += column - 1
        if line == 1:
            offset = max(offset - prefix_len, 0)
        return min(offset, max(len(source) - prefix_len, 0))
