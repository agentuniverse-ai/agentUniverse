# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: list_structure_extractor.py

import re
from typing import Any, Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Nesting levels are clamped to this depth: real documents rarely nest
# lists deeper, and the clamp keeps metadata bounded when pathological
# indentation (copy-paste artefacts, quoted forwards) shows up.
_MAX_DEPTH = 4

# Bullet marker characters accepted at the start of an item: ASCII
# hyphen and asterisk, the typographic bullets U+2022 / U+00B7, and the
# en / em dashes frequently left behind by scraped text.
_BULLET_CLASS = r'[-*•·–—]'

# Task checkbox: an optional bullet (marker plus separator) followed by
# a bracket box holding a space (unchecked) or x/X (checked). The box
# may stand bare at line start ("[x] done") or ride on a bullet
# ("- [x] done"); the checked state is captured per item.
_CHECKBOX_RE = re.compile(
    r'^(?P<indent>[ \t]*)(?P<bullet>' + _BULLET_CLASS + r'[ \t]+)?'
    r'\[(?P<box>[ xX])\](?:[ \t]+(?P<rest>.*))?$')

# Plain bullet: marker plus at least one separating whitespace run (or
# end of line for empty items). Requiring the separator keeps
# hyphenated words ("--force", "**bold**") and horizontal rules ("---")
# out of the results.
_BULLET_RE = re.compile(
    r'^(?P<indent>[ \t]*)(?P<marker>' + _BULLET_CLASS +
    r')(?:[ \t]+(?P<rest>.*))?$')

# Numbered marker families, tried in order; the family name doubles as
# the grouping key. The digit run is bounded so oversized numbers inside
# prose ("1234567890. hello") are not misread as enumerations.
_NUMBERED_PATTERNS: List[Tuple[Any, str]] = [
    (re.compile(r'^(?P<indent>[ \t]*)(?P<marker>\d{1,9}\.)'
                r'(?:[ \t]+(?P<rest>.*))?$'), 'arabic-dot'),
    (re.compile(r'^(?P<indent>[ \t]*)(?P<marker>\d{1,9}\))'
                r'(?:[ \t]+(?P<rest>.*))?$'), 'arabic-paren'),
    (re.compile(r'^(?P<indent>[ \t]*)(?P<marker>\([a-zA-Z]\))'
                r'(?:[ \t]+(?P<rest>.*))?$'), 'letter-paren'),
    (re.compile(r'^(?P<indent>[ \t]*)(?P<marker>\([一二三四五六七八九十百千零两]+\))'
                r'(?:[ \t]+(?P<rest>.*))?$'), 'cjk-paren'),
]


def _indent_level(indent: str) -> int:
    """Convert a leading whitespace run into a nesting level.

    One tab counts as one level and every two spaces as one level, so
    the common two-space and four-space Markdown indents map to one and
    two levels respectively. A single stray space keeps level 0. The
    result is clamped to ``_MAX_DEPTH``.

    Args:
        indent: The leading whitespace run of the line (spaces/tabs).

    Returns:
        int: Nesting level in [0, _MAX_DEPTH].
    """
    tabs = indent.count('\t')
    spaces = len(indent) - tabs
    return min(tabs + spaces // 2, _MAX_DEPTH)


def _parse_line(line: str) -> Optional[Dict[str, Any]]:
    """Classify one line as a list item (or None for non-items).

    Checkbox patterns are tried first because "- [x] done" would
    otherwise parse as a bullet carrying bracket text; numbered families
    come next, plain bullets last. Every recognized item reports its
    kind (bullet / numbered / checkbox), the marker style used for
    grouping consecutive items into blocks, the literal marker string,
    the nesting level, and the payload text (whitespace-stripped; a
    marker standing alone yields an empty item).

    Args:
        line: One line of document text, without the newline.

    Returns:
        Optional[Dict[str, Any]]: Parsed item fields, or None when the
        line is not a list item.
    """
    match = _CHECKBOX_RE.match(line)
    if match:
        bullet = match.group('bullet') or ''
        box = match.group('box')
        return {
            'kind': 'checkbox',
            'style': bullet[:1],
            'marker': f'{bullet[:1]} [{box}]'.strip(),
            'level': _indent_level(match.group('indent')),
            'text': (match.group('rest') or '').rstrip(),
            'checked': box != ' ',
        }

    match = _BULLET_RE.match(line)
    if match:
        return {
            'kind': 'bullet',
            'style': match.group('marker'),
            'marker': match.group('marker'),
            'level': _indent_level(match.group('indent')),
            'text': (match.group('rest') or '').rstrip(),
        }

    for pattern, family in _NUMBERED_PATTERNS:
        match = pattern.match(line)
        if match:
            return {
                'kind': 'numbered',
                'style': family,
                'marker': match.group('marker'),
                'level': _indent_level(match.group('indent')),
                'text': (match.group('rest') or '').rstrip(),
            }
    return None


class ListStructureExtractor(DocProcessor):
    """Detect bullet / numbered / checkbox lists and record their
    structure into document metadata.

    A large share of knowledge sources — release notes, policies,
    specs, scraped pages — carry their content in lists, yet the
    existing doc processors only ever FRAGMENT text (character, token
    and recursive splitters, the hierarchical regex splitter): none of
    them RECORD what the list structure was, so downstream consumers
    cannot tell a three-item checklist from a wall of prose. This
    processor scans each document line by line and stamps a faithful,
    deterministic description of every list into metadata. It
    complements ``OutlineExtractor`` (heading skeleton, PR #3531) and
    ``QAPairExtractor`` (Q&A mining, PR #3485) on the structure axis of
    issue #258, and leaves the text itself untouched.

    Recognition is deliberately conservative and offline:

    1. bullets: ``-``, ``*``, ``•``, ``·``, en dash and em dash, each
       followed by a separating whitespace run (so ``--force``,
       ``**bold**`` and ``---`` rules stay prose);
    2. numbered items in four families — ``1.`` (arabic-dot), ``1)``
       (arabic-paren), ``(a)`` (letter-paren, any case) and ``(一)``
       (cjk-paren); sequence continuity is not enforced, only family;
    3. task checkboxes: an optional bullet plus a bracket box —
       ``- [ ]`` / ``- [x]`` / bare ``[ ]`` — with the checked state
       captured per item.

    Consecutive items sharing one marker style (kind plus family) group
    into a single list block; any non-list line — prose or blank —
    closes the block, and a style change (``-`` to ``*``, ``1.`` to
    ``1)``) starts a new one, mirroring how readers perceive list
    boundaries. Nesting is derived from leading indentation: one tab or
    every two spaces counts as one level, clamped to depth 4, so a
    document's visual hierarchy survives into metadata.

    Bookkeeping lands in three keys: ``metadata['lists']`` holds one
    entry per detected block — ``kind`` (bullet | numbered | checkbox),
    ``span`` (character offsets of the whole block), ``item_count`` and
    the ``items`` list of ``{text, span, level, marker}`` (plus
    ``checked`` for checkboxes), where item spans cover their raw line
    including indentation and marker. The payload is capped at
    ``max_lists`` blocks and ``max_items_per_list`` items per block to
    bound metadata size on list-heavy documents, while
    ``metadata['list_count']``, each block's ``item_count`` and
    ``metadata['checkbox_summary']`` (``{total, checked}``, stamped
    only when checkbox items exist) always report the uncapped totals.
    Documents without any list pass through completely untouched. The
    whole pipeline is pure Python, deterministic and dependency-free.

    Attributes:
        max_lists: Maximum number of list blocks recorded in
            ``metadata['lists']``; must be >= 1. Detected blocks beyond
            the cap are omitted from the payload but still counted.
        max_items_per_list: Maximum number of items recorded per block;
            must be >= 1. ``item_count`` keeps the true total.
    """

    max_lists: int = 20
    max_items_per_list: int = 100

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp list structure metadata onto every document.

        Args:
            origin_docs: Documents to scan, in batch order.
            query: Query object (unused; list structure depends only on
                the documents' own text).

        Returns:
            List[Document]: The same documents in the same order; each
            document carrying at least one list is stamped with
            'lists', 'list_count' and (when checkboxes exist)
            'checkbox_summary', all others pass through untouched.
        """
        if not origin_docs:
            return []

        for doc in origin_docs:
            blocks = self._extract_blocks(doc.text or '')
            if not blocks:
                continue

            lists: List[Dict[str, Any]] = []
            checkbox_total = 0
            checkbox_checked = 0
            for index, block in enumerate(blocks):
                items = block['items']
                if block['kind'] == 'checkbox':
                    checkbox_total += len(items)
                    checkbox_checked += \
                        sum(1 for item in items if item['checked'])
                if index < self.max_lists:
                    lists.append({
                        'kind': block['kind'],
                        'span': [block['start'], block['end']],
                        'item_count': len(items),
                        'items': items[:self.max_items_per_list],
                    })

            meta = dict(doc.metadata or {})
            meta['lists'] = lists
            meta['list_count'] = len(blocks)
            if checkbox_total:
                meta['checkbox_summary'] = {
                    'total': checkbox_total,
                    'checked': checkbox_checked,
                }
            doc.metadata = meta
        return origin_docs

    # ------------------------------------------------------------------ #
    # Structure extraction helpers
    # ------------------------------------------------------------------ #

    def _extract_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Scan text line by line and group list items into blocks.

        Offsets are character positions in the original text; a block
        spans from the first character of its first item line to the
        end of its last item line, and a carriage return belonging to a
        CRLF pair is excluded from spans so offsets stay meaningful on
        Windows-style input.

        Args:
            text: Document text (None treated as empty).

        Returns:
            List[Dict[str, Any]]: Detected blocks in document order,
            each with kind, style key, start/end offsets and items.
        """
        blocks: List[Dict[str, Any]] = []
        current: Optional[Dict[str, Any]] = None
        offset = 0
        for raw_line in (text or '').split('\n'):
            line = raw_line[:-1] if raw_line.endswith('\r') else raw_line
            end = offset + len(line)
            parsed = _parse_line(line)
            if parsed is None:
                # Non-list lines — prose or blank — close the open
                # block; list structure is never carried across them.
                current = None
            else:
                style = (parsed['kind'], parsed['style'])
                if current is not None and current['style'] == style:
                    current['items'].append(
                        self._item(parsed, offset, end))
                    current['end'] = end
                else:
                    current = {
                        'kind': parsed['kind'],
                        'style': style,
                        'start': offset,
                        'end': end,
                        'items': [self._item(parsed, offset, end)],
                    }
                    blocks.append(current)
            offset += len(raw_line) + 1
        return blocks

    @staticmethod
    def _item(parsed: Dict[str, Any], start: int, end: int) \
            -> Dict[str, Any]:
        """Materialize one item record from a parsed line.

        Args:
            parsed: Fields produced by ``_parse_line``.
            start: First character offset of the item's line.
            end: End character offset (exclusive) of the item's line.

        Returns:
            Dict[str, Any]: ``{text, span, level, marker}`` plus
            ``checked`` for checkbox items.
        """
        item = {
            'text': parsed['text'],
            'span': [start, end],
            'level': parsed['level'],
            'marker': parsed['marker'],
        }
        if parsed['kind'] == 'checkbox':
            item['checked'] = parsed['checked']
        return item

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'ListStructureExtractor':
        """Initialize and validate the extractor from component
        configuration.

        Validation happens eagerly at load time: a silently ignored
        typo in a cap (say ``max_lists: 0``) would be far harder to
        notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            ListStructureExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid parameter value.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_lists") and \
                doc_processor_configer.max_lists is not None:
            cap = doc_processor_configer.max_lists
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_lists must be an integer")
            self.max_lists = cap
            if self.max_lists < 1:
                raise ValueError("max_lists must be >= 1")

        if hasattr(doc_processor_configer, "max_items_per_list") and \
                doc_processor_configer.max_items_per_list is not None:
            cap = doc_processor_configer.max_items_per_list
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_items_per_list must be an integer")
            self.max_items_per_list = cap
            if self.max_items_per_list < 1:
                raise ValueError("max_items_per_list must be >= 1")

        return self
