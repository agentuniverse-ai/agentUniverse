# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: xml_splitter.py

"""
XML structure splitter — a knowledge pre-processing DocProcessor.

Parses each recalled document as XML and emits one chunk per element,
recording the element path (e.g. ``root > items > item``) as metadata.
Useful for indexing structured, tag-based sources (SVG, NLM/JATS articles,
TEI, Maven POMs, sitemaps, configuration) where each element should be a
retrievable unit.

Sibling of ``JsonSplitter`` (#258): both walk a structured document and
record a path per chunk. This one targets angle-bracket markup using the
standard library ``xml.etree.ElementTree`` parser, so it has **no third-party
dependency**.

Traversal rules:

- Each element becomes a candidate chunk whose text is the concatenation of
  its own ``.text`` and the non-tag ``text``/``tail`` of its subtree (i.e. the
  element's visible text content).
- The path is the chain of tags from the root to the element, joined with
  ``" > "`` (configurable via ``path_key``).
- ``max_depth`` caps traversal: at that depth, a subtree is serialised back to
  an XML string rather than descended into, producing one chunk for the whole
  subtree.
- Leaf elements (no element children) always emit their own text chunk.
- ``include_attributes`` controls whether element attributes are rendered into
  the chunk text (``[id=42 lang=en]``) and into the path.
- Non-XML / malformed documents are passed through unchanged.
"""

import logging
import re
from typing import List, Optional, Tuple
from xml.etree import ElementTree as ET

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# Sentinel tag used for free-floating text chunks (text that sits between
# elements at the root level, or tail text of an element handled separately).
_TEXT_TAG = "#text"


def _local_tag(tag: str) -> str:
    """Strip an XML namespace prefix from ``tag``.

    ``ElementTree`` serialises namespaced tags as ``{uri}local``. We collapse
    that to just ``local`` so paths stay readable and stable across documents
    that differ only by namespace URI.
    """
    if tag and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def _attrs_to_str(attrs: dict) -> str:
    """Render an attribute mapping as ``[k=v k2=v2]`` (empty if no attrs)."""
    if not attrs:
        return ""
    return "[" + " ".join(f"{k}={v}" for k, v in attrs.items()) + "]"


class XmlSplitter(DocProcessor):
    """Split XML documents into one chunk per element, recording the path.

    Attributes:
        path_key: Metadata key under which the element path is written.
            Default ``"xml_path"``.
        max_depth: Maximum traversal depth (``None`` = unlimited). At
            ``max_depth`` a nested subtree is serialised back to an XML string
            rather than descended into. ``max_depth=1`` yields only the root.
        include_attributes: When ``True``, each element's attributes are
            rendered into the chunk text (as ``[k=v ...]``) and appended to
            the path. Default ``False``.
        drop_empty: If ``True`` (default), elements with no visible text and
            no attributes (when ``include_attributes`` is on) are not emitted
            as chunks.
        path_separator: String used to join tags in the path. Default ``" > "``.
        root_name: Name to use for the root level of the path. ``None`` (the
            default) uses the root element's own tag, so a document
            ``<items>…</items>`` produces paths starting with ``items``.
    """

    path_key: str = "xml_path"
    max_depth: Optional[int] = None
    include_attributes: bool = False
    drop_empty: bool = True
    path_separator: str = " > "
    root_name: Optional[str] = None

    def _process_docs(self, origin_docs: List[Document],
                      query=None) -> List[Document]:
        """Parse each document as XML and split it into element chunks.

        Documents that are empty or not valid XML are returned unchanged.
        """
        if not origin_docs:
            return []

        self._validate_max_depth()
        result: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            root = self._parse_xml(text)
            if root is None:
                # Not valid XML — keep the original document untouched.
                result.append(doc)
                continue

            base_meta = dict(doc.metadata or {})
            root_label = self.root_name or _local_tag(root.tag)
            for path, chunk_text in self._walk(root, depth=1, prefix=root_label):
                if self.drop_empty and not chunk_text.strip():
                    continue
                meta = dict(base_meta)
                meta[self.path_key] = path
                result.append(Document(text=chunk_text, metadata=meta))
        return result

    # ------------------------------------------------------------------ #
    # Parsing
    # ------------------------------------------------------------------ #
    def _validate_max_depth(self) -> None:
        """Validate ``max_depth`` is None or a positive integer.

        Called from ``_process_docs`` so an invalid value is caught regardless
        of how the instance was built (configer vs. direct construction).
        """
        if self.max_depth is None:
            return
        try:
            md = int(self.max_depth)
        except (TypeError, ValueError):
            raise ValueError(
                f"max_depth must be an integer or null, got {self.max_depth!r}."
            )
        if md < 1:
            raise ValueError(
                f"max_depth must be >= 1 or null, got {md}."
            )

    def _parse_xml(self, text: str) -> Optional[ET.Element]:
        """Parse ``text`` as XML, returning the root element or ``None``.

        Tolerates leading whitespace/BOM. Returns ``None`` for empty input or
        any parse error so the caller can pass the document through unchanged.
        """
        if not text or not text.strip():
            return None
        try:
            # ``fromstring`` requires a single root element; wrap defensively.
            return ET.fromstring(text)
        except ET.ParseError:
            return None

    # ------------------------------------------------------------------ #
    # Traversal
    # ------------------------------------------------------------------ #
    def _walk(self, element: ET.Element, depth: int,
              prefix: str) -> List[Tuple[str, str]]:
        """Recursively walk ``element`` yielding ``(path, text)`` chunk pairs.

        Args:
            element: The current XML element.
            depth: Current depth (root is depth 1).
            prefix: Path string of the parent level (root label for the root).

        Returns:
            List of ``(path, chunk_text)`` tuples in document order.
        """
        results: List[Tuple[str, str]] = []
        at_max = self.max_depth is not None and depth >= self.max_depth

        children = list(element)

        if at_max or not children:
            # Emit a chunk for this element: either it is a leaf, or we have
            # hit max_depth and serialise the whole subtree.
            if at_max and children:
                text = self._serialise(element)
            else:
                text = self._element_text(element)
            text = self._decorate(text, element)
            results.append((prefix, text))
            return results

        # Internal element: emit a chunk for its own direct text (if any),
        # then recurse into children. Direct text becomes a chunk under the
        # element's path so the element's own prose is still retrievable.
        own_text = self._direct_text(element)
        if own_text and own_text.strip():
            results.append((prefix, self._decorate(own_text, element)))

        for child in children:
            child_tag = _local_tag(child.tag)
            child_path = prefix + self.path_separator + child_tag
            if self.include_attributes and child.attrib:
                child_path += " " + _attrs_to_str(child.attrib)
            results.extend(self._walk(child, depth + 1, child_path))

            # The child's ``tail`` (text after the child's closing tag, before
            # the next sibling) belongs to the parent's prose scope.
            tail = (child.tail or "").strip()
            if tail:
                results.append((prefix + self.path_separator + _TEXT_TAG, tail))

        return results

    # ------------------------------------------------------------------ #
    # Text extraction helpers
    # ------------------------------------------------------------------ #
    def _element_text(self, element: ET.Element) -> str:
        """Return all visible text inside ``element`` (its full subtree).

        Joins ``element.text`` and every ``.text``/``.tail`` in the subtree in
        document order, mirroring how a browser would render the element.
        """
        parts: List[str] = []
        if element.text:
            parts.append(element.text)
        for node in element.iter():
            if node is element:
                continue
            if node.text:
                parts.append(node.text)
            if node.tail:
                parts.append(node.tail)
        return " ".join(p.strip() for p in parts if p and p.strip())

    def _direct_text(self, element: ET.Element) -> str:
        """Return only the text directly under ``element`` (not in children).

        This is ``element.text`` plus the ``tail`` of each immediate child —
        i.e. the prose that belongs to this element rather than its children.
        """
        parts: List[str] = []
        if element.text:
            parts.append(element.text)
        for child in element:
            if child.tail:
                parts.append(child.tail)
        return " ".join(p.strip() for p in parts if p and p.strip())

    def _decorate(self, text: str, element: ET.Element) -> str:
        """Optionally prepend an element's attribute string to ``text``."""
        if not self.include_attributes:
            return text
        attrs = _attrs_to_str(element.attrib)
        if not attrs:
            return text
        if text:
            return f"{attrs} {text}"
        return attrs

    def _serialise(self, element: ET.Element) -> str:
        """Serialise ``element`` back to a compact XML string.

        Used when ``max_depth`` is reached so a whole subtree becomes one
        chunk rather than being descended into.
        """
        return ET.tostring(element, encoding="unicode", method="xml")

    # ------------------------------------------------------------------ #
    # Config initialisation
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) -> "XmlSplitter":
        """Initialise the splitter from its component configuration."""
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "path_key"):
            self.path_key = doc_processor_configer.path_key

        if hasattr(doc_processor_configer, "max_depth"):
            md = doc_processor_configer.max_depth
            if md is None:
                self.max_depth = None
            else:
                md = int(md)
                if md < 1:
                    raise ValueError(
                        f"max_depth must be >= 1 or null, got {md}."
                    )
                self.max_depth = md

        if hasattr(doc_processor_configer, "include_attributes"):
            self.include_attributes = bool(
                doc_processor_configer.include_attributes)

        if hasattr(doc_processor_configer, "drop_empty"):
            self.drop_empty = bool(doc_processor_configer.drop_empty)

        if hasattr(doc_processor_configer, "path_separator"):
            self.path_separator = doc_processor_configer.path_separator

        if hasattr(doc_processor_configer, "root_name"):
            self.root_name = doc_processor_configer.root_name

        return self
