#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: xml_path_tool.py

"""Compact XML path query tool built purely on the stdlib ElementTree.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency XML query helper
agents can call to pull values out of XML documents — API response
snapshots, configuration files, RSS feeds — without shipping a
third-party XPath engine. It complements XmlReader (structured
ingestion of XML documents) the way JsonPathTool complements JSON
readers: a small query language over already-loaded text.

The tool is a strictly-validated façade over
``xml.etree.ElementTree`` and supports four modes:

* ``query`` — take XML text and a path and return every element the
  path selects; each match carries its (namespace-stripped) tag,
  attributes, a capped own-text snippet and its child count.
* ``attrs`` — same selection, returning each matched element's
  attribute dictionary (empty for attribute-less elements).
* ``text`` — same selection, returning each matched element's own
  stripped text; elements whose stripped text is empty are reported
  as ``null`` entries plus an ``empty_text_count`` total.
* ``validate`` — check XML well-formedness and report the expat
  error line / 1-based column on failure, plus a small structural
  summary (root tag, element count, maximum depth) on success.

Supported path syntax — an honest SUBSET of XPath 1.0, not full
XPath:

* absolute paths only: a path must start with ``/`` or ``//``;
  ``/catalog/book`` selects the ``book`` children of ``catalog``;
* ``//`` descendant axis at any depth (``//title`` selects every
  ``title`` in the document), implemented via ``Element.iter()``;
* ``**`` as an alias of ``//`` between steps (``/catalog/**/title``
  equals ``/catalog//title``); a trailing ``/catalog/**`` selects
  every descendant of ``catalog``;
* ``*`` wildcard matching any one-level name (``/catalog/*`` selects
  the root element's children);
* ``[n]`` 1-based positional index and ``[last()]``. Positional
  predicates number the candidate list *per parent element* after a
  ``/`` step — like XPath, ``/root/shelf/book[1]`` is the first
  ``book`` child of each ``shelf`` — and number the de-duplicated
  document-order candidate list after a ``//`` step;
* ``[@attr='value']`` attribute equality and ``[@attr]``
  has-attribute predicates, with single- or double-quoted values and
  ``\\'`` / ``\\\\`` / ``\\"`` escapes; several predicates may be
  chained left to right (``//book[@category='fiction'][2]``).

Deliberately NOT supported (rejected with a positioned syntax error
rather than silently approximated): relative paths, ``.`` / ``..``,
namespace prefixes in paths, ``text()`` / ``node()`` tests, ``|``
unions, ranges, functions other than ``last()``, and comparisons
other than ``=``. Element and attribute names are matched
namespace-blind: ``<dc:creator>`` and a plain ``<creator>`` both
match the path name ``creator`` (matching compares local names after
stripping the ``{uri}`` prefix ElementTree assigns), so two
namespaces reusing one local name are indistinguishable, and
attribute keys are reported namespace-stripped with the first
document-order value winning a collision. ``text`` mode returns the
element's own text block only — mixed-content tails and nested
elements' text are not concatenated, unlike XPath ``string()``.

Security — XXE protection: before ANY parsing, a character-level
pre-scan of the input text rejects documents containing ``<!DOCTYPE``
or ``<!ENTITY`` markup, mirroring the DTD guard used by XmlReader —
DTDs and entities are the vehicle for XXE and entity-expansion
(billion laughs) attacks. The scan is case-sensitive (those are the
only spellings valid XML allows) and safe against UTF-8 smuggling:
ASCII byte sequences never occur inside multi-byte UTF-8 sequences,
so scanning the decoded text finds exactly the occurrences a byte
scan would. It is also conservative: input that merely mentions those
tokens inside comments or CDATA is rejected too. No external
entities, DTDs or network fetches are ever processed.

Input validation is strict and happens before any work: malformed
parameters (unknown mode, missing / empty / over-long ``xml_text`` or
``path``, non-string inputs) raise a ``ValueError``, mirroring the
other common tools. Errors that depend on the *content being
processed* — forbidden DTD / ENTITY markup (with its located line /
column), XML that is not well-formed (with the expat error line /
column), text that cannot be encoded to UTF-8, and path syntax
errors (with the position of the offending character) — are returned
as a structured ``error`` payload so an agent can react without
catching exceptions. A path that selects nothing is a normal empty
result (``found: false``), not an error.

Cost is bounded by caps, not timeouts: ``max_xml_chars`` (default
100,000) bounds the document, ``max_path_chars`` (default 2,000)
bounds the path, and ``max_matches`` (default 1,000) caps the
returned match list with a ``truncated`` flag. Evaluation is
iterative (``iter()``-based, no recursion) and never mutates or
re-serializes the parsed document; results are deterministic and in
document order.
"""

import string
import xml.etree.ElementTree as ET
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


# --------------------------------------------------------------------- #
# Internal markers / exceptions (never escape the tool)
# --------------------------------------------------------------------- #

class _PathSyntaxError(ValueError):
    """Marker for path syntax problems (returned as a payload)."""


class _ContentError(Exception):
    """Marker for content-level failures (returned as a payload)."""

    def __init__(
        self,
        error_type: str,
        message: str,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.line = line
        self.column = column

    def payload(self) -> dict[str, Any]:
        """Render the structured error payload."""
        data = {"type": self.error_type, "message": self.message[:500]}
        if self.line is not None:
            data["line"] = self.line
        if self.column is not None:
            data["column"] = self.column
        return data


class _VirtualDocument:
    """Sentinel context node standing for the document itself.

    Its "children" are the top-level elements (the root element); its
    "descendants" are every element in the document, root included —
    matching the XPath meaning of a leading ``/`` or ``//``.
"""


_VIRTUAL_DOCUMENT = _VirtualDocument()


def _local_name(tag: Any) -> Any:
    """Strip the ``{uri}`` namespace prefix ElementTree assigns."""
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def _local_attrs(element: ET.Element) -> dict[str, str]:
    """Attribute dict with namespace-stripped keys (first wins)."""
    attrs: dict[str, str] = {}
    for key, value in element.attrib.items():
        local = _local_name(key)
        if local not in attrs:
            attrs[local] = value
    return attrs


def _max_depth(root: ET.Element) -> int:
    """Iteratively compute the maximum element depth (root = 1)."""
    depth, stack = 0, [(root, 1)]
    while stack:
        element, level = stack.pop()
        if level > depth:
            depth = level
        stack.extend((child, level + 1) for child in element)
    return depth


class _XmlPathParser:
    """Strict tokenizer/parser for the supported path subset.

    Produces a list of steps; each step is a tuple
    ``(axis, name, predicates)`` where ``axis`` is ``'child'`` or
    ``'descendant'``, ``name`` is an element name or ``'*'``, and
    ``predicates`` is a (possibly empty) list of predicate tuples:
    ``('index', n)``, ``('last',)``, ``('has_attr', name)`` or
    ``('eq_attr', name, value)``. Raises :class:`_PathSyntaxError`
    with the position of the offending character on any problem.
    """

    _NAME_START = frozenset(string.ascii_letters + "_")
    _NAME_CHARS = frozenset(string.ascii_letters + string.digits + "_-.")

    def __init__(self, path: str) -> None:
        self._path = path
        self._pos = 0
        self._len = len(path)

    # -- helpers ------------------------------------------------------- #

    def _fail(self, message: str) -> None:
        raise _PathSyntaxError(
            f"{message} (at position {self._pos} in {self._path[:64]!r})"
        )

    def _skip_ws(self) -> None:
        while self._pos < self._len and self._path[self._pos] in " \t":
            self._pos += 1

    def _expect(self, token: str) -> None:
        if not self._path.startswith(token, self._pos):
            self._fail(f"expected {token!r}")
        self._pos += len(token)

    def _read_name(self, what: str) -> str:
        start = self._pos
        if self._pos >= self._len or self._path[self._pos] not in self._NAME_START:
            self._fail(f"expected a {what}: a letter or '_', then letters, digits, '_', '-' or '.'")
        while self._pos < self._len and self._path[self._pos] in self._NAME_CHARS:
            self._pos += 1
        return self._path[start:self._pos]

    # -- grammar ------------------------------------------------------- #

    def parse(self) -> list[tuple[str, str, list[tuple[Any, ...]]]]:
        """Parse the whole path into steps."""
        steps: list[tuple[str, str, list[tuple[Any, ...]]]] = []
        if not self._path.startswith("/"):
            self._fail("path must be absolute: start with '/' or '//'")
        if self._path.startswith("//"):
            axis = "descendant"
            self._pos = 2
        elif self._path.startswith("/**"):
            if self._len > 3 and self._path[3] != "/":
                self._pos = 3
                self._fail("expected '/' after '**'")
            if self._len == 3:
                # A path of exactly '/**' selects every element.
                return [("descendant", "*", [])]
            axis = "descendant"
            self._pos = 4
        else:
            axis = "child"
            self._pos = 1
        while True:
            steps.append(self._step(axis))
            if self._pos >= self._len:
                break
            axis = self._separator(steps)
            if axis == "done":
                break
        return steps

    def _separator(self, steps: list) -> str:
        """Consume the separator between steps, return the next axis.

        A trailing ``/**`` is consumed here as a final descendant
        wildcard step and signals ``'done'``.
        """
        rest = self._path[self._pos:]
        if rest.startswith("/**/"):
            self._pos += 4
            return "descendant"
        if rest == "/**":
            steps.append(("descendant", "*", []))
            self._pos = self._len
            return "done"
        if rest.startswith("//"):
            self._pos += 2
            if self._pos >= self._len:
                self._fail("path must not end with '/'")
            return "descendant"
        if rest.startswith("/"):
            self._pos += 1
            if self._pos >= self._len:
                self._fail("path must not end with '/'")
            return "child"
        self._fail("expected '/' or '//' between steps")

    def _step(self, axis: str) -> tuple[str, str, list]:
        if self._pos >= self._len:
            self._fail("expected an element name or '*' after '/'")
        char = self._path[self._pos]
        if char == "*":
            if self._path.startswith("**", self._pos):
                self._fail("'**' is only valid as a whole step between '/' separators")
            self._pos += 1
            name = "*"
        else:
            name = self._read_name("element name")
        predicates: list[tuple[Any, ...]] = []
        while self._pos < self._len and self._path[self._pos] == "[":
            predicates.append(self._predicate())
        return (axis, name, predicates)

    def _predicate(self) -> tuple[Any, ...]:
        self._pos += 1  # consume '['
        self._skip_ws()
        if self._pos >= self._len:
            self._fail(
                "unterminated predicate: expected an index ([n]), last() "
                "or an attribute test ([@attr] or [@attr='value'])"
            )
        char = self._path[self._pos]
        if char in string.digits:
            start = self._pos
            while self._pos < self._len and self._path[self._pos] in string.digits:
                self._pos += 1
            digits = self._path[start:self._pos]
            if len(digits) > 1 and digits[0] == "0":
                self._fail("index must not have leading zeros")
            index = int(digits)
            if index < 1:
                self._fail("index is 1-based and must be at least 1 (got 0)")
            self._skip_ws()
            self._expect("]")
            return ("index", index)
        if self._path.startswith("last", self._pos):
            self._pos += 4
            self._skip_ws()
            self._expect("(")
            self._skip_ws()
            self._expect(")")
            self._skip_ws()
            self._expect("]")
            return ("last",)
        if char == "@":
            self._pos += 1
            attr = self._read_name("attribute name after '@'")
            self._skip_ws()
            if self._pos < self._len and self._path[self._pos] == "=":
                if self._path.startswith("==", self._pos):
                    self._fail("'==' is not supported; use '=' for attribute equality")
                self._pos += 1
                self._skip_ws()
                value = self._quoted()
                self._skip_ws()
                self._expect("]")
                return ("eq_attr", attr, value)
            if self._pos < self._len and self._path[self._pos] == "!":
                self._fail("'!=' comparisons are not supported; only '=' equality")
            self._expect("]")
            return ("has_attr", attr)
        self._fail(
            "predicate must be an index ([n]), last() or an attribute "
            "test ([@attr] or [@attr='value'])"
        )

    def _quoted(self) -> str:
        if self._pos >= self._len:
            self._fail("expected a quoted attribute value")
        quote = self._path[self._pos]
        if quote not in ("'", '"'):
            self._fail(f"attribute value must be quoted with ' or \" (got {quote!r})")
        self._pos += 1
        chars: list[str] = []
        while self._pos < self._len and self._path[self._pos] != quote:
            char = self._path[self._pos]
            if char == "\\":
                self._pos += 1
                if self._pos >= self._len:
                    self._fail("dangling backslash in attribute value")
                escaped = self._path[self._pos]
                if escaped not in (quote, "\\"):
                    self._fail(
                        f"unsupported escape '\\{escaped}' in attribute value "
                        f"(only \\{quote} and \\\\ are supported)"
                    )
                chars.append(escaped)
            else:
                chars.append(char)
            self._pos += 1
        if self._pos >= self._len:
            self._fail(f"unterminated attribute value: missing closing {quote}")
        self._pos += 1
        return "".join(chars)


class XmlPathTool(Tool):
    """Compact XML path query tool built purely on the stdlib.

    Attributes:
        max_xml_chars (int): Upper bound on the ``xml_text`` input
            length; longer inputs are rejected before any work.
        max_path_chars (int): Upper bound on the ``path`` length.
        max_matches (int): Upper bound on the returned match list;
            excess matches are cut with a ``truncated`` flag.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "xml_path_tool"
    description: str = (
        "XML path query tool — pure Python stdlib ElementTree, no XPath "
        "engine dependency. Query XML elements with a compact path subset "
        "(absolute /root/child paths, // descendants, ** alias, * wildcard, "
        "[n]/[last()] positions, [@attr='value']/[@attr] attribute tests): "
        "mode='query' returns matches with tag/attributes/text snippet, "
        "mode='attrs' returns each match's attribute dict, mode='text' "
        "returns stripped own-text values, and mode='validate' checks "
        "well-formedness with expat error line/column. DOCTYPE/ENTITY "
        "markup is rejected before any parsing (XXE protection)."
    )

    MODES: ClassVar[tuple] = ("query", "attrs", "text", "validate")
    # The maximum length of the per-match text snippet in query mode.
    MAX_TEXT_SNIPPET: ClassVar[int] = 200

    max_xml_chars: int = 100_000
    max_path_chars: int = 2_000
    max_matches: int = 1_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        xml_text: Any = None,
        path: Any = None,
    ) -> dict[str, Any]:
        """Run one XML path operation.

        Args:
            mode (str): One of ``query`` / ``attrs`` / ``text`` /
                ``validate``.
            xml_text (str): The XML document as text. Required for every
                mode; bytes are rejected (pass text).
            path (str): The compact path selecting elements. Required
                for the ``query``, ``attrs`` and ``text`` modes; not
                used by ``validate``.

        Returns:
            Dict[str, Any]: The operation result — for the selection
                modes a ``found`` / ``total`` / ``count`` /
                ``truncated`` status plus the per-mode payload
                (``matches`` / ``attributes`` / ``values``), for
                ``validate`` a ``valid`` flag with a structural summary
                or the located error — or a structured ``error``
                payload for content-level failures (DOCTYPE/ENTITY
                rejection, malformed XML, path syntax errors,
                unencodable text).

        Raises:
            ValueError: If any parameter is malformed (before any work
                happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_xml = self._validate_xml_text(xml_text)
        if mode == "validate":
            return self._run_validate(clean_xml)
        clean_path = self._validate_path(path)
        return self._run_query(mode, clean_xml, clean_path)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any work)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"xml_path_tool: {message}")

    def _validate_xml_text(self, xml_text: Any) -> str:
        """Validate the ``xml_text`` input."""
        if (
            xml_text is None
            or isinstance(xml_text, bool)
            or not isinstance(xml_text, str)
        ):
            self._invalid(f"xml_text must be a non-empty string (got {xml_text!r})")
        if not xml_text:
            self._invalid("xml_text must be a non-empty string (got '')")
        if len(xml_text) > self.max_xml_chars:
            self._invalid(
                f"xml_text exceeds the {self.max_xml_chars:,}-character limit "
                f"(got {len(xml_text):,} characters)"
            )
        return xml_text

    def _validate_path(self, path: Any) -> str:
        """Validate the ``path`` input (syntax is checked later)."""
        if path is None or isinstance(path, bool) or not isinstance(path, str):
            self._invalid(f"path must be a non-empty string (got {path!r})")
        if not path:
            self._invalid("path must be a non-empty string (got '')")
        if len(path) > self.max_path_chars:
            self._invalid(
                f"path exceeds the {self.max_path_chars:,}-character limit "
                f"(got {len(path):,} characters)"
            )
        return path

    # ------------------------------------------------------------------ #
    # Content-level stages: encode, DTD guard, parse (raise _ContentError)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _encode(xml_text: str) -> bytes:
        """UTF-8 encode the document, guarding against bad surrogates."""
        try:
            return xml_text.encode("utf-8")
        except UnicodeEncodeError:
            raise _ContentError(
                "invalid_unicode",
                "xml_text contains unpaired surrogates and cannot be "
                "encoded to UTF-8",
            )

    @staticmethod
    def _reject_dtd(xml_text: str) -> None:
        """Reject DTD / ENTITY markup BEFORE any parsing (XXE guard).

        The scan is character-level and case-sensitive — ``<!DOCTYPE``
        and ``<!ENTITY`` are the only spellings valid XML allows — and
        conservative: mentions inside comments or CDATA are rejected
        too. Scanning the decoded text (not the UTF-8 bytes) is
        equivalent for detection — ASCII byte sequences never occur
        inside multi-byte UTF-8 sequences — and keeps the reported
        column counting characters, consistent with the expat columns
        of :meth:`_parse`.
        """
        for marker in ("<!DOCTYPE", "<!ENTITY"):
            index = xml_text.find(marker)
            if index < 0:
                continue
            line = xml_text.count("\n", 0, index) + 1
            column = index - (xml_text.rfind("\n", 0, index) + 1) + 1
            raise _ContentError(
                "dtd_not_allowed",
                "the tool refuses XML containing '<!DOCTYPE' or "
                "'<!ENTITY' markup: DTDs and entities are the vehicle "
                "for XXE and entity-expansion attacks, so they are "
                "rejected before any parsing",
                line=line,
                column=column,
            )

    @staticmethod
    def _parse(payload: bytes) -> ET.Element:
        """Parse the (already guarded) UTF-8 bytes with ElementTree.

        Parsing bytes — not the original text — lets documents carry
        an ``encoding=`` declaration in their XML prolog.
        """
        try:
            return ET.fromstring(payload)
        except ET.ParseError as exc:
            position = getattr(exc, "position", None) or (None, None)
            line = position[0]
            # expat reports a 0-based column offset; report 1-based.
            column = position[1] + 1 if position[1] is not None else None
            raise _ContentError(
                "not_well_formed",
                f"XML is not well-formed: {exc}",
                line=line,
                column=column,
            )

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def _run_validate(self, xml_text: str) -> dict[str, Any]:
        """Check well-formedness and summarize the document shape."""
        context = {"mode": "validate"}
        try:
            payload = self._encode(xml_text)
            self._reject_dtd(xml_text)
            root = self._parse(payload)
        except _ContentError as exc:
            return {**context, "valid": False, "error": exc.payload()}
        return {
            "mode": "validate",
            "valid": True,
            "root_tag": _local_name(root.tag),
            "element_count": sum(1 for _ in root.iter()),
            "max_depth": _max_depth(root),
        }

    # ------------------------------------------------------------------ #
    # query / attrs / text modes
    # ------------------------------------------------------------------ #

    def _run_query(self, mode: str, xml_text: str, path: str) -> dict[str, Any]:
        """Select elements by path and build the per-mode payload."""
        context = {"mode": mode, "path": path}
        try:
            payload = self._encode(xml_text)
            self._reject_dtd(xml_text)
            root = self._parse(payload)
            steps = _XmlPathParser(path).parse()
        except _ContentError as exc:
            return {**context, "error": exc.payload()}
        except _PathSyntaxError as exc:
            return {
                **context,
                "error": {"type": "invalid_path", "message": str(exc)[:500]},
            }

        matches = self._evaluate(root, steps)
        total = len(matches)
        truncated = total > self.max_matches
        kept = matches[: self.max_matches]
        status = {
            "path": path,
            "found": total > 0,
            "total": total,
            "count": len(kept),
            "truncated": truncated,
        }
        if mode == "query":
            return {
                "mode": "query",
                **status,
                "matches": [self._match_summary(element) for element in kept],
            }
        if mode == "attrs":
            return {
                "mode": "attrs",
                **status,
                "attributes": [_local_attrs(element) for element in kept],
            }
        values: list[dict[str, Any]] = []
        empty_text_count = 0
        for element in kept:
            text = self._own_text(element)
            if text is None:
                empty_text_count += 1
            values.append({"tag": _local_name(element.tag), "text": text})
        return {
            "mode": "text",
            **status,
            "values": values,
            "empty_text_count": empty_text_count,
        }

    # ------------------------------------------------------------------ #
    # Evaluation (iterative, deterministic, document order)
    # ------------------------------------------------------------------ #

    def _evaluate(self, root: ET.Element, steps: list) -> list:
        """Run the parsed steps over the document, document order."""
        current: list = [_VIRTUAL_DOCUMENT]
        for axis, name, predicates in steps:
            if not current:
                return []
            current = self._apply_step(root, current, axis, name, predicates)
        return current

    def _apply_step(
        self,
        root: ET.Element,
        contexts: list,
        axis: str,
        name: str,
        predicates: list,
    ) -> list:
        """Apply one step (axis + name test + predicates) to a context set.

        Positional predicates number the candidates per parent element
        for the child axis (XPath-style) and the de-duplicated
        document-order candidate list for the descendant axis.
        """
        if axis == "child":
            picked: list = []
            for context in contexts:
                children = [root] if context is _VIRTUAL_DOCUMENT else list(context)
                group = [
                    element
                    for element in children
                    if self._name_matches(element, name)
                ]
                picked.extend(self._apply_predicates(group, predicates))
            return picked

        reachable: set[int] = set()
        for context in contexts:
            if context is _VIRTUAL_DOCUMENT:
                for element in root.iter():
                    reachable.add(id(element))
            else:
                for offset, element in enumerate(context.iter()):
                    if offset > 0:  # a '//' step selects strict descendants
                        reachable.add(id(element))
        candidates = [
            element
            for element in root.iter()
            if id(element) in reachable and self._name_matches(element, name)
        ]
        return self._apply_predicates(candidates, predicates)

    @staticmethod
    def _name_matches(element: ET.Element, name: str) -> bool:
        """Namespace-blind local-name test; ``*`` matches any element."""
        return name == "*" or _local_name(element.tag) == name

    @staticmethod
    def _apply_predicates(group: list, predicates: list) -> list:
        """Filter one candidate group by its predicate list, in order."""
        for predicate in predicates:
            kind = predicate[0]
            if kind == "index":
                group = group[predicate[1] - 1 : predicate[1]]
            elif kind == "last":
                group = group[-1:]
            elif kind == "has_attr":
                group = [el for el in group if predicate[1] in _local_attrs(el)]
            else:  # 'eq_attr'
                group = [
                    el
                    for el in group
                    if _local_attrs(el).get(predicate[1]) == predicate[2]
                ]
            if not group:
                break
        return group

    # ------------------------------------------------------------------ #
    # Per-match rendering
    # ------------------------------------------------------------------ #

    @classmethod
    def _own_text(cls, element: ET.Element) -> str | None:
        """The element's own text block, stripped; ``None`` when empty.

        Only the text before the first child element is considered —
        mixed-content tails and nested text are not concatenated.
        """
        text = element.text.strip() if isinstance(element.text, str) else None
        return text or None

    @classmethod
    def _match_summary(cls, element: ET.Element) -> dict[str, Any]:
        """Build one query-mode match record."""
        snippet = cls._own_text(element)
        if snippet and len(snippet) > cls.MAX_TEXT_SNIPPET:
            snippet = snippet[: cls.MAX_TEXT_SNIPPET] + "..."
        return {
            "tag": _local_name(element.tag),
            "attributes": _local_attrs(element),
            "text": snippet,
            "child_count": len(element),
        }
