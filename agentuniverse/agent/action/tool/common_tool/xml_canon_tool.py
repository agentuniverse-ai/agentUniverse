#!/usr/bin/env python3
"""XML canonicalization (W3C C14N 1.0 / Exclusive C14N core subset) for agents.

The tool canonicalizes XML text, compares two documents for canonical
equality, and explains which cosmetic transformations a document needs.

Implemented canonicalization subset (document order serialization):

1.  Parsing uses ``xml.parsers.expat`` with raw qualified names; namespace
    bindings are resolved by hand so prefixes survive serialization. XML 1.0
    well-formedness is enforced by the parser, including line-end
    normalization (CR/CRLF to LF) and attribute-value normalization (literal
    TAB/LF/CR inside attribute values become spaces; character references
    survive).
2.  Documents carrying a DTD/DOCTYPE, entity declarations, relative namespace
    URIs, an ``xmlns:xml`` redefinition, an ``xmlns:xmlns`` declaration, or an
    empty URI for a prefixed namespace are rejected with ``not_supported``
    (they are outside this subset; reference implementations such as libxml2
    refuse several of them as well).
3.  The XML declaration is dropped; comments are removed and adjacent text
    nodes merge; whitespace outside the root element is dropped; document
    level processing instructions are kept, separated by single newlines.
4.  Namespace declarations are rendered before attributes at every element,
    sorted by prefix (default namespace first). A declaration is rendered only
    when its prefix-to-URI binding differs from the nearest binding rendered
    by an ancestor output, so redundant re-declarations are suppressed while
    re-bindings and ``xmlns=""`` undeclarations are materialized.
5.  Attributes are sorted by (namespace URI, local name); unprefixed
    attributes carry no namespace and sort first. Values are double quoted
    with ``& < "`` escaped plus character references for TAB/LF/CR.
6.  Text (including CDATA sections) is escaped as ``&amp; &lt; &gt;`` with CR
    written as ``&#xD;``; CDATA markers disappear.
7.  Processing instructions serialize as ``<?target data?>`` (a single
    separator space; no data yields ``<?target?>``).
8.  Childless elements serialize with an explicit end tag ``<t></t>``.
9.  Predefined entities and numeric character references are resolved and
    re-escaped canonically; non-ASCII characters stay literal.
10. The ``exclusive`` variant renders only visibly utilized prefixes (the
    element name prefix, its attribute prefixes) and the optional
    ``inclusive_prefixes`` list (``#default`` names the default namespace per
    the Exclusive C14N specification), at the element that utilizes them, with
    the same nearest-binding dedupe; inherited but unused declarations are
    dropped.
"""

# Public execute() converts validation exceptions into structured tool errors.

import re
import xml.parsers.expat
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

_XML_NS = "http://www.w3.org/XML/1998/namespace"
_ABSOLUTE_URI = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")
_ENTITY_REF = re.compile(r"&(amp|lt|gt|quot|apos|#x[0-9a-fA-F]+|#[0-9]+);")
_PREDEFINED = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}
_MODES = ("canonicalize", "compare", "explain")
_VARIANTS = ("c14n10", "exclusive")


class _CanonError(Exception):
    """Internal control-flow error carrying a structured tool error payload."""

    def __init__(self, error_type: str, message: str):
        super().__init__(message)
        self.error_type = error_type
        self.message = message


class _Element:
    """Parsed element node holding source order metadata."""

    __slots__ = ("attrs", "children", "decls", "local", "prefix", "qname", "scope", "uri")

    def __init__(self, qname: str, prefix: str, local: str, uri: str):
        self.qname = qname
        self.prefix = prefix
        self.local = local
        self.uri = uri
        self.attrs: list[tuple[str, str, str, str, str]] = []
        self.decls: list[tuple[str, str]] = []
        self.scope: dict[str, str] = {}
        self.children: list[Any] = []


class _Document:
    """Parsed document: root element, document level PIs, and counters."""

    __slots__ = ("attributes", "elements", "max_depth", "post_pis", "pre_pis", "root")

    def __init__(self) -> None:
        self.root: _Element | None = None
        self.pre_pis: list[tuple[str, str]] = []
        self.post_pis: list[tuple[str, str]] = []
        self.elements = 0
        self.attributes = 0
        self.max_depth = 0


class _SourceScan:
    """Bounded raw-source statistics used for transformation reporting."""

    __slots__ = (
        "attr_whitespace",
        "cdata_sections",
        "comments",
        "entity_ref_count",
        "entity_refs",
        "first_attr_ws",
        "first_cdata",
        "first_comment",
        "first_entity_ref",
        "first_self_closing",
        "first_single_quoted",
        "self_closing",
        "single_quoted",
        "text_cr",
    )

    def __init__(self) -> None:
        self.self_closing = 0
        self.single_quoted = 0
        self.attr_whitespace = 0
        self.cdata_sections = 0
        self.comments = 0
        self.entity_refs: list[str] = []
        self.entity_ref_count = 0
        self.first_self_closing: str | None = None
        self.first_cdata: str | None = None
        self.first_comment: str | None = None
        self.first_single_quoted: str | None = None
        self.first_attr_ws: str | None = None
        self.first_entity_ref: str | None = None
        self.text_cr = 0


def _escape_text(value: str) -> str:
    """Escape a text node per C14N: ampersand, less-than, greater-than, CR."""
    chunks: list[str] = []
    for char in value:
        if char == "&":
            chunks.append("&amp;")
        elif char == "<":
            chunks.append("&lt;")
        elif char == ">":
            chunks.append("&gt;")
        elif char == "\r":
            chunks.append("&#xD;")
        else:
            chunks.append(char)
    return "".join(chunks)


def _escape_attribute(value: str) -> str:
    """Escape an attribute value per C14N: ampersand, less-than, quote, ws refs."""
    chunks: list[str] = []
    for char in value:
        if char == "&":
            chunks.append("&amp;")
        elif char == "<":
            chunks.append("&lt;")
        elif char == '"':
            chunks.append("&quot;")
        elif char == "\t":
            chunks.append("&#x9;")
        elif char == "\n":
            chunks.append("&#xA;")
        elif char == "\r":
            chunks.append("&#xD;")
        else:
            chunks.append(char)
    return "".join(chunks)


def _split_qname(qname: str) -> tuple[str, str]:
    """Split a raw qualified name into (prefix, local name); prefix '' if none."""
    if ":" in qname:
        prefix, local = qname.split(":", 1)
        return prefix, local
    return "", qname


def _render_pi(target: str, data: str) -> str:
    """Serialize a processing instruction per C14N."""
    return f"<?{target} {data}?>" if data else f"<?{target}?>"


def _resolve_entity_ref(match_text: str) -> str:
    """Resolve one predefined or numeric entity reference to its characters."""
    name = match_text[1:-1]
    if name in _PREDEFINED:
        return _PREDEFINED[name]
    if name.startswith("#x") or name.startswith("#X"):
        return chr(int(name[2:], 16))
    return chr(int(name[1:]))


def _nearest_rendered(stack: list[dict[str, str]], prefix: str) -> str | None:
    """Return the URI most recently rendered for the prefix, if any."""
    for level in reversed(stack):
        if prefix in level:
            return level[prefix]
    return None


def _bounded(value: str, limit: int) -> str:
    """Clip a snippet to the limit with an explicit truncation marker."""
    if len(value) <= limit:
        return value
    return value[: limit - 1] + "\u2026"


def _attr_name_before(raw: str, position: int) -> str:
    """Best-effort attribute name ending right before the '=' at position."""
    equals = raw.rfind("=", 0, position)
    if equals <= 0:
        return "?"
    start = max(raw.rfind(" ", 0, equals), raw.rfind("\t", 0, equals), raw.rfind("\n", 0, equals)) + 1
    return raw[start:equals] or "?"


def _namespace_declarations(attrs: dict[str, str]) -> list[tuple[str, str]]:
    """Extract (prefix, uri) namespace declarations in source order."""
    decls: list[tuple[str, str]] = []
    for attr_name, attr_value in attrs.items():
        if attr_name == "xmlns":
            decls.append(("", attr_value))
        elif attr_name.startswith("xmlns:"):
            prefix = attr_name[6:]
            if prefix == "xmlns":
                raise _CanonError("not_supported", "the xmlns prefix cannot be redeclared")
            if prefix == "xml" and attr_value != _XML_NS:
                raise _CanonError("not_supported", "the xml prefix cannot be bound to another URI")
            if attr_value == "":
                raise _CanonError("not_supported", "a prefixed namespace cannot be undeclared with an empty URI")
            decls.append((prefix, attr_value))
    return decls


def _scope_with_declarations(parent_scope: dict[str, str], decls: list[tuple[str, str]]) -> dict[str, str]:
    """Extend a scope with validated declarations; the xml binding stays implicit."""
    scope = dict(parent_scope)
    for prefix, uri in decls:
        if prefix == "xml":
            continue
        if uri and not _ABSOLUTE_URI.match(uri):
            raise _CanonError(
                "not_supported",
                f"namespace URI for prefix {prefix or 'default'!r} must be absolute "
                "(relative namespace URIs are outside the subset)",
            )
        scope[prefix] = uri
    return scope


def _resolve_expanded_name(qname: str, scope: dict[str, str], kind: str) -> tuple[str, str, str]:
    """Resolve a raw qualified name to (prefix, local name, namespace URI).

    Unprefixed element names fall under the default namespace, while
    unprefixed attribute names never do (XML Namespaces 1.0).
    """
    prefix, local = _split_qname(qname)
    if prefix == "xml":
        return prefix, local, _XML_NS
    if prefix:
        if prefix not in scope:
            raise _CanonError("parse_error", f"unbound namespace prefix {prefix!r} on {kind} {qname!r}")
        return prefix, local, scope[prefix]
    if kind == "attribute":
        return prefix, local, ""
    return prefix, local, scope.get("", "")


def _element_attributes(attrs: dict[str, str], scope: dict[str, str]) -> list[tuple[str, str, str, str, str]]:
    """Resolve attributes (namespace declarations excluded) in source order."""
    resolved: list[tuple[str, str, str, str, str]] = []
    seen_expanded: set[tuple[str, str]] = set()
    for attr_name, attr_value in attrs.items():
        if attr_name == "xmlns" or attr_name.startswith("xmlns:"):
            continue
        attr_prefix, attr_local, attr_uri = _resolve_expanded_name(attr_name, scope, "attribute")
        expanded = (attr_uri, attr_local)
        if expanded in seen_expanded:
            raise _CanonError("parse_error", f"attribute {attr_name!r} duplicates an expanded name")
        seen_expanded.add(expanded)
        resolved.append((attr_name, attr_prefix, attr_local, attr_uri, attr_value))
    return resolved


class XmlCanonTool(Tool):
    """Canonicalize XML text, compare documents canonically, and explain changes.

    The runtime is standard-library only and deterministic: identical inputs
    always produce identical outputs, and inputs, nodes, depth, and every
    reported list are bounded.
    """

    max_xml_chars: int = 1_000_000
    max_nodes: int = 50_000
    max_depth: int = 64
    max_example_chars: int = 80
    max_difference_context: int = 48
    max_reported_namespaces: int = 32
    max_reported_entity_refs: int = 16

    _TRANSFORMATION_ORDER: ClassVar[tuple[str, ...]] = (
        "attribute_reordering",
        "namespace_materialization",
        "cdata_unescaping",
        "comment_removal",
        "empty_element_expansion",
        "entity_normalization",
        "quote_normalization",
        "whitespace_normalization",
    )

    def execute(
        self,
        mode: str,
        xml_text: str | None = None,
        xml_text_b: str | None = None,
        variant: str = "c14n10",
        inclusive_prefixes: list[str] | None = None,
    ) -> dict[str, Any]:
        mode_name = mode if isinstance(mode, str) else None
        try:
            return self._execute_checked(mode, xml_text, xml_text_b, variant, inclusive_prefixes)
        except _CanonError as exc:
            return {
                "status": "error",
                "error_type": exc.error_type,
                "error": exc.message,
                "mode": mode_name,
            }
        except xml.parsers.expat.ExpatError as exc:
            return {
                "status": "error",
                "error_type": "parse_error",
                "error": f"xml_text is not well-formed XML: {exc}",
                "mode": mode_name,
            }

    def _execute_checked(
        self,
        mode: Any,
        xml_text: Any,
        xml_text_b: Any,
        variant: Any,
        inclusive_prefixes: Any,
    ) -> dict[str, Any]:
        self._validate_config()
        operation = self._mode(mode)
        prefixes = self._prefixes(inclusive_prefixes)
        chosen_variant = self._variant(variant, prefixes)
        if operation == "compare":
            return self._compare(xml_text, xml_text_b, chosen_variant, prefixes)
        if xml_text is None:
            raise _CanonError("validation_error", "xml_text is required")
        result = self._canonicalize(xml_text, chosen_variant, prefixes)
        if operation == "canonicalize":
            return {
                "status": "success",
                "mode": "canonicalize",
                "variant": chosen_variant,
                "canonical": result["canonical"],
                "canonical_length": len(result["canonical"]),
                "transformations": result["transformations"],
                "stats": result["stats"],
            }
        return self._explain(xml_text, chosen_variant, prefixes)

    # ------------------------------------------------------------------
    # Argument validation
    # ------------------------------------------------------------------

    def _validate_config(self) -> None:
        for name in (
            "max_xml_chars",
            "max_nodes",
            "max_depth",
            "max_example_chars",
            "max_difference_context",
            "max_reported_namespaces",
            "max_reported_entity_refs",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise _CanonError("validation_error", f"{name} must be a positive integer")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise _CanonError("validation_error", "mode must be a string")
        mode = value.strip().lower()
        if mode not in _MODES:
            raise _CanonError("validation_error", "mode must be canonicalize, compare, or explain")
        return mode

    @staticmethod
    def _variant(value: Any, prefixes: list[str]) -> str:
        if not isinstance(value, str):
            raise _CanonError("validation_error", "variant must be a string")
        variant = value.strip().lower()
        if variant not in _VARIANTS:
            raise _CanonError("validation_error", "variant must be c14n10 or exclusive")
        if prefixes and variant != "exclusive":
            raise _CanonError("validation_error", "inclusive_prefixes requires variant=exclusive")
        return variant

    @staticmethod
    def _prefixes(value: Any) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
            raise _CanonError("validation_error", "inclusive_prefixes must be a list of non-empty strings")
        return list(value)

    def _xml_text(self, value: Any, name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise _CanonError("validation_error", f"{name} must be a non-empty string")
        if len(value) > self.max_xml_chars:
            raise _CanonError("limit_exceeded", f"{name} exceeds max_xml_chars ({self.max_xml_chars})")
        return value

    # ------------------------------------------------------------------
    # Raw source scan (bounded, for transformation reporting only)
    # ------------------------------------------------------------------

    def _scan_source(self, raw: str) -> _SourceScan:
        stats = _SourceScan()
        limit = self.max_example_chars
        length = len(raw)
        index = 0
        while index < length:
            if raw[index] != "<":
                next_tag = raw.find("<", index)
                if next_tag == -1:
                    next_tag = length
                self._scan_text(raw[index:next_tag], stats)
                index = next_tag
            elif raw.startswith("<!--", index):
                end = raw.find("-->", index + 4)
                end = length if end == -1 else end
                stats.comments += 1
                if stats.first_comment is None:
                    stats.first_comment = _bounded(raw[index + 4 : end], limit)
                index = min(end + 3, length)
            elif raw.startswith("<![CDATA[", index):
                end = raw.find("]]>", index + 9)
                end = length if end == -1 else end
                stats.cdata_sections += 1
                if stats.first_cdata is None:
                    stats.first_cdata = _bounded(raw[index + 9 : end], limit)
                index = min(end + 3, length)
            elif raw.startswith("<?", index):
                end = raw.find("?>", index)
                index = length if end == -1 else min(end + 2, length)
            elif raw.startswith("<!", index):
                end = raw.find(">", index)
                index = length if end == -1 else min(end + 1, length)
            else:
                index = self._scan_tag(raw, index, stats, limit)
        return stats

    def _scan_text(self, segment: str, stats: _SourceScan) -> None:
        """Count entity references and literal CR characters in a text region."""
        stats.text_cr += segment.count("\r")
        for match in _ENTITY_REF.finditer(segment):
            self._count_entity_ref(match.group(0), stats)

    def _scan_attribute_value(self, value: str, stats: _SourceScan) -> None:
        """Count entity references inside an attribute value."""
        for match in _ENTITY_REF.finditer(value):
            self._count_entity_ref(match.group(0), stats)

    def _count_entity_ref(self, reference: str, stats: _SourceScan) -> None:
        stats.entity_ref_count += 1
        if len(stats.entity_refs) < self.max_reported_entity_refs:
            stats.entity_refs.append(reference)
        if stats.first_entity_ref is None:
            stats.first_entity_ref = reference

    def _scan_tag(self, raw: str, start: int, stats: _SourceScan, limit: int) -> int:  # noqa: C901
        """Scan one tag, honoring quoted attribute values, then mine it."""
        length = len(raw)
        index = start + 1
        quote: str | None = None
        value_start = -1
        values: list[tuple[int, int]] = []
        while index < length:
            char = raw[index]
            if quote is not None:
                if char == quote:
                    quote = None
                    values.append((value_start, index))
                elif char in "\t\n\r":
                    stats.attr_whitespace += 1
                    if stats.first_attr_ws is None:
                        attr_name = _attr_name_before(raw, index)
                        stats.first_attr_ws = _bounded(
                            f"attribute {attr_name!r} literal whitespace becomes a space", limit
                        )
                index += 1
                continue
            if char in "\"'":
                quote = char
                value_start = index + 1
                if char == "'":
                    stats.single_quoted += 1
                    if stats.first_single_quoted is None:
                        attr_name = _attr_name_before(raw, index)
                        stats.first_single_quoted = _bounded(
                            f"attribute {attr_name!r} single quotes become double quotes", limit
                        )
            elif char == ">":
                break
            index += 1
        tag_text = raw[start : index + 1]
        if tag_text.endswith("/>"):
            stats.self_closing += 1
            if stats.first_self_closing is None:
                stats.first_self_closing = _bounded(tag_text, limit)
        for value_start, value_end in values:
            self._scan_attribute_value(raw[value_start:value_end], stats)
        return index + 1 if index < length else length

    # ------------------------------------------------------------------
    # Parsing (expat + hand-rolled namespace resolution)
    # ------------------------------------------------------------------

    def _parse(self, raw: str) -> tuple[_Document, _SourceScan]:  # noqa: C901
        stats = self._scan_source(raw)
        document = _Document()
        stack: list[_Element] = []
        counter = {"nodes": 0}

        def on_doctype(*_args: Any) -> None:
            raise _CanonError("not_supported", "DTD/DOCTYPE declarations are outside the canonicalization subset")

        def on_entity_decl(*_args: Any) -> None:
            raise _CanonError("not_supported", "entity declarations require a DTD and are outside the subset")

        def on_pi(target: str, data: str | None) -> None:
            payload = data or ""
            if document.root is None:
                document.pre_pis.append((target, payload))
            elif stack:
                stack[-1].children.append(("pi", target, payload))
            else:
                document.post_pis.append((target, payload))

        def on_chars(data: str) -> None:
            if not stack:
                return  # whitespace (or junk) outside the root element is dropped
            parent = stack[-1]
            last = parent.children[-1] if parent.children else None
            if isinstance(last, tuple) and last[0] == "text":
                parent.children[-1] = ("text", last[1] + data)
            else:
                parent.children.append(("text", data))

        def on_start(name: str, attrs: dict[str, str]) -> None:
            counter["nodes"] += 1
            if counter["nodes"] > self.max_nodes:
                raise _CanonError("limit_exceeded", f"document exceeds max_nodes ({self.max_nodes})")
            if len(stack) >= self.max_depth:
                raise _CanonError("limit_exceeded", f"document exceeds max_depth ({self.max_depth})")
            decls = _namespace_declarations(attrs)
            scope = _scope_with_declarations(stack[-1].scope if stack else {"xml": _XML_NS}, decls)
            prefix, local, uri = _resolve_expanded_name(name, scope, "element")
            element = _Element(name, prefix, local, uri)
            element.scope = scope
            element.decls = decls
            element.attrs = _element_attributes(attrs, scope)
            document.attributes += len(element.attrs)
            if stack:
                stack[-1].children.append(element)
            elif document.root is not None:
                raise _CanonError("parse_error", "multiple root elements")
            else:
                document.root = element
            stack.append(element)
            document.elements += 1
            document.max_depth = max(document.max_depth, len(stack))

        def on_end(_name: str) -> None:
            stack.pop()

        parser = xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = on_start
        parser.EndElementHandler = on_end
        parser.CharacterDataHandler = on_chars
        parser.ProcessingInstructionHandler = on_pi
        parser.StartDoctypeDeclHandler = on_doctype
        parser.EntityDeclHandler = on_entity_decl
        try:
            parser.Parse(raw, True)
        except xml.parsers.expat.ExpatError as exc:
            raise _CanonError("parse_error", f"xml_text is not well-formed XML: {exc}") from exc
        if document.root is None:
            raise _CanonError("parse_error", "xml_text has no root element")
        return document, stats

    # ------------------------------------------------------------------
    # Canonical serialization
    # ------------------------------------------------------------------

    def _candidates(self, element: _Element, variant: str, prefixes: list[str]) -> list[tuple[str, str]]:
        """Namespace (prefix, uri) candidates to consider at this element."""
        if variant == "c14n10":
            return sorted((prefix, uri) for prefix, uri in element.scope.items() if prefix != "xml")
        utilized: set[str] = set()
        # The element's own name prefix is visibly utilized as written: the
        # default prefix counts for unprefixed names (an xmlns="" undeclaration
        # or inherited default binding is therefore rendered when physical).
        utilized.add(element.prefix)
        for _qname, attr_prefix, _local, attr_uri, _value in element.attrs:
            if attr_uri:
                utilized.add(attr_prefix)
        for listed in prefixes:
            utilized.add("" if listed == "#default" else listed)
        return sorted(
            (prefix, element.scope[prefix])
            for prefix in sorted(utilized)
            if prefix != "xml" and prefix in element.scope
        )

    def _serialize(  # noqa: C901
        self, document: _Document, variant: str, prefixes: list[str]
    ) -> tuple[str, dict[str, Any]]:
        out: list[str] = []
        rendered: list[dict[str, str]] = []
        events = {
            "namespaces_rendered": 0,
            "namespace_materialized": 0,
            "attribute_reordered": 0,
            "reorder_example": None,
            "materialize_example": None,
        }
        if document.root is None:
            raise _CanonError("parse_error", "xml_text has no root element")

        def emit_namespaces(element: _Element) -> None:
            level: dict[str, str] = {}
            for prefix, uri in self._candidates(element, variant, prefixes):
                if _nearest_rendered(rendered, prefix) == uri:
                    continue
                rendered_name = "xmlns" if prefix == "" else f"xmlns:{prefix}"
                out.append(f' {rendered_name}="{_escape_attribute(uri)}"')
                level[prefix] = uri
                events["namespaces_rendered"] += 1
                if variant == "exclusive" and (prefix, uri) not in element.decls:
                    events["namespace_materialized"] += 1
                    if events["materialize_example"] is None:
                        events["materialize_example"] = {
                            "element": element.qname,
                            "declaration": f'{rendered_name}="{uri}"',
                        }
            rendered.append(level)

        def visit(element: _Element) -> None:
            out.append(f"<{element.qname}")
            ordered = sorted(element.attrs, key=lambda item: (item[3], item[2]))
            emit_namespaces(element)
            for qname, _prefix, _local, _uri, value in ordered:
                out.append(f' {qname}="{_escape_attribute(value)}"')
            if [item[0] for item in element.attrs] != [item[0] for item in ordered]:
                events["attribute_reordered"] += 1
                if events["reorder_example"] is None:
                    events["reorder_example"] = {
                        "element": element.qname,
                        "before": _bounded(" ".join(item[0] for item in element.attrs), self.max_example_chars),
                        "after": _bounded(" ".join(item[0] for item in ordered), self.max_example_chars),
                    }
            out.append(">")
            for child in element.children:
                if isinstance(child, _Element):
                    visit(child)
                elif child[0] == "text":
                    out.append(_escape_text(child[1]))
                else:
                    out.append(_render_pi(child[1], child[2]))
            out.append(f"</{element.qname}>")
            rendered.pop()

        for target, data in document.pre_pis:
            out.append(_render_pi(target, data))
            out.append("\n")
        visit(document.root)
        for target, data in document.post_pis:
            out.append("\n")
            out.append(_render_pi(target, data))
        canonical = "".join(out)
        text_chars = 0
        pending = [document.root]
        while pending:
            node = pending.pop()
            for child in node.children:
                if isinstance(child, _Element):
                    pending.append(child)
                elif child[0] == "text":
                    text_chars += len(child[1])
        stats = {
            "elements": document.elements,
            "attributes": document.attributes,
            "namespaces_rendered": events["namespaces_rendered"],
            "text_chars": text_chars,
            "max_depth": document.max_depth,
        }
        return canonical, {"events": events, "stats": stats}

    # ------------------------------------------------------------------
    # Transformation reporting
    # ------------------------------------------------------------------

    def _transformations(self, scan: _SourceScan, events: dict[str, Any]) -> list[dict[str, Any]]:
        """Build the bounded transformation log from scan stats and events."""
        limit = self.max_example_chars
        entries: dict[str, dict[str, Any]] = {}
        if events["attribute_reordered"]:
            entries["attribute_reordering"] = {
                "count": events["attribute_reordered"],
                "example": events["reorder_example"],
                "note": "attributes are sorted by (namespace URI, local name)",
            }
        if events["namespace_materialized"]:
            entries["namespace_materialization"] = {
                "count": events["namespace_materialized"],
                "example": events["materialize_example"],
                "note": "exclusive variant renders utilized prefixes at the utilizing element",
            }
        if scan.cdata_sections:
            entries["cdata_unescaping"] = {
                "count": scan.cdata_sections,
                "example": {
                    "before": _bounded(f"<![CDATA[{scan.first_cdata}]]>", limit),
                    "after": _bounded(_escape_text(scan.first_cdata or ""), limit),
                },
                "note": "CDATA sections become escaped text",
            }
        if scan.comments:
            entries["comment_removal"] = {
                "count": scan.comments,
                "example": {"before": _bounded(f"<!--{scan.first_comment}-->", limit)},
                "note": "comments are removed from the canonical form",
            }
        if scan.self_closing:
            entries["empty_element_expansion"] = {
                "count": scan.self_closing,
                "example": {"before": _bounded(scan.first_self_closing, limit)},
                "note": "self-closing tags become <tag ...></tag>",
            }
        if scan.entity_ref_count:
            first = scan.first_entity_ref or ""
            entries["entity_normalization"] = {
                "count": scan.entity_ref_count,
                "example": {
                    "before": first,
                    "after": _bounded(_escape_text(_resolve_entity_ref(first)), limit),
                },
                "note": "entity and character references are resolved then re-escaped",
            }
        if scan.single_quoted:
            entries["quote_normalization"] = {
                "count": scan.single_quoted,
                "example": {"before": _bounded(scan.first_single_quoted, limit)},
                "note": "attribute values are re-quoted with double quotes",
            }
        whitespace = scan.attr_whitespace + scan.text_cr
        if whitespace:
            entries["whitespace_normalization"] = {
                "count": whitespace,
                "example": {
                    "before": _bounded(scan.first_attr_ws or "literal CR in text is normalized to LF on parse", limit)
                },
                "note": "attribute TAB/LF/CR become spaces on parse; text CR becomes LF or &#xD;",
            }
        return [{"type": name, **entries[name]} for name in self._TRANSFORMATION_ORDER if name in entries]

    # ------------------------------------------------------------------
    # Modes
    # ------------------------------------------------------------------

    def _canonicalize(self, xml_text: str, variant: str, prefixes: list[str]) -> dict[str, Any]:
        raw = self._xml_text(xml_text, "xml_text")
        document, scan = self._parse(raw)
        canonical, payload = self._serialize(document, variant, prefixes)
        return {
            "canonical": canonical,
            "transformations": self._transformations(scan, payload["events"]),
            "stats": payload["stats"],
        }

    def _compare(self, xml_text: Any, xml_text_b: Any, variant: str, prefixes: list[str]) -> dict[str, Any]:
        left = self._canonicalize(self._xml_text(xml_text, "xml_text"), variant, prefixes)
        right = self._canonicalize(self._xml_text(xml_text_b, "xml_text_b"), variant, prefixes)
        result: dict[str, Any] = {
            "status": "success",
            "mode": "compare",
            "variant": variant,
            "canonically_equal": left["canonical"] == right["canonical"],
            "canonical_a_length": len(left["canonical"]),
            "canonical_b_length": len(right["canonical"]),
            "erased_differences": self._erased(left["transformations"], right["transformations"]),
        }
        if not result["canonically_equal"]:
            result["first_difference"] = self._first_difference(left["canonical"], right["canonical"])
        return result

    @staticmethod
    def _erased(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Merge both documents' transformation logs, labeled by document."""
        return [{"document": doc, **entry} for doc, entries in (("a", left), ("b", right)) for entry in entries]

    def _first_difference(self, left: str, right: str) -> dict[str, Any]:
        """Locate the first differing character with bounded context."""
        span = min(len(left), len(right))
        offset = span
        for index in range(span):
            if left[index] != right[index]:
                offset = index
                break
        context = self.max_difference_context
        if offset < span:
            reason = "the canonical forms first differ at this offset"
        else:
            reason = "one canonical form is a prefix of the other"
        return {
            "offset": offset,
            "context_a": _bounded(left[max(0, offset - context) : offset + context], context * 2 + 1),
            "context_b": _bounded(right[max(0, offset - context) : offset + context], context * 2 + 1),
            "reason": reason,
        }

    def _explain(self, xml_text: str, variant: str, prefixes: list[str]) -> dict[str, Any]:
        raw = self._xml_text(xml_text, "xml_text")
        document, scan = self._parse(raw)
        canonical, payload = self._serialize(document, variant, prefixes)
        applied = {entry["type"]: entry for entry in self._transformations(scan, payload["events"])}
        notes = {
            "attribute_reordering": "attributes are re-sorted by (namespace URI, local name)",
            "namespace_materialization": (
                "only the exclusive variant materializes utilized prefixes at each element"
                if variant == "c14n10"
                else "visibly utilized prefixes are rendered at the element that uses them"
            ),
            "cdata_unescaping": "CDATA sections serialize as escaped text",
            "comment_removal": "comments never appear in the canonical form",
            "empty_element_expansion": "childless elements gain explicit end tags",
            "entity_normalization": "entity and character references are resolved then re-escaped",
            "quote_normalization": "attribute values are always double quoted",
            "whitespace_normalization": "attribute whitespace normalizes to spaces; text CR becomes LF or &#xD;",
        }
        transformations = [
            {
                "type": name,
                "applicable": name in applied,
                "count": applied[name]["count"] if name in applied else 0,
                "example": applied[name]["example"] if name in applied else None,
                "note": notes[name],
            }
            for name in self._TRANSFORMATION_ORDER
        ]
        namespaces: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for element in _iter_elements(document.root):
            for prefix, uri in element.decls:
                seen.add((prefix, uri))
        for prefix, uri in sorted(seen, key=lambda item: item[0]):
            if len(namespaces) >= self.max_reported_namespaces:
                break
            namespaces.append(
                {
                    "prefix": prefix,
                    "uri": uri,
                    "declaration": ("xmlns" if prefix == "" else f"xmlns:{prefix}") + f'="{uri}"',
                }
            )
        return {
            "status": "success",
            "mode": "explain",
            "variant": variant,
            "applicable_transformations": transformations,
            "canonical_preview": _bounded(canonical, self.max_example_chars * 4),
            "namespaces": namespaces,
            "namespaces_truncated": len(seen) > len(namespaces),
            "stats": payload["stats"],
        }


def _iter_elements(element: _Element) -> list[_Element]:
    """Collect the elements of the whole tree in document order."""
    collected: list[_Element] = []
    stack = [element]
    while stack:
        node = stack.pop()
        collected.append(node)
        for child in reversed(node.children):
            if isinstance(child, _Element):
                stack.append(child)
    return collected
