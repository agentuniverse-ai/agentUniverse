#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: bullets_to_prose_tool.py

"""Bullet / numbered list to flowing prose converter tool.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency helper for doc
agents: rewrite every bullet or numbered list of a markdown document
into a flowing prose paragraph, deterministically, with template
stitching only — this is explicitly NOT an LLM call, no token of the
item text is ever reworded.  The ecosystem can already DETECT list
structure (``ListStructureExtractor``, PR #3663, whose recognition
rules this tool shares verbatim), but nothing REWRITES lists; this
tool closes that gap for pipelines that must feed prose (narrative
reports, TTS scripts, summarizer inputs) without losing item content.

The tool is built purely on the standard library and supports three
modes:

* ``convert`` — rewrite ``text`` so that every consecutive
  bullet/numbered block becomes one prose paragraph.
* ``paragraphs_only`` — preview mode: report which line-ranges would
  convert, without rewriting anything.
* ``stats`` — count blocks found, items converted and nesting levels
  seen.

Recognition rules (the ListStructureExtractor family rules)
-----------------------------------------------------------

A line is a list item when it matches one of the families below;
anything else is prose and closes the current block.  A marker must be
followed by a separating whitespace run, so ``--force``, ``**bold**``
and ``---`` rules stay prose:

* bullets: ``-``, ``*``, ``•``, ``·``, en dash and em dash;
* numbered items in four families — ``1.`` (arabic-dot), ``1)``
  (arabic-paren), ``(a)`` (letter-paren, any case) and ``(一)``
  (cjk-paren); the digit run is bounded to nine digits and sequence
  continuity is NOT enforced, only family;
* task checkboxes (tried first): an optional bullet plus a bracket
  box — ``- [ ]`` / ``- [x]`` / bare ``[ ]``.

Consecutive items sharing one marker style (kind plus family) group
into a single block; a non-list line OR a style change (``-`` to ``*``,
``1.`` to ``1)``) starts a new block.  Nesting is derived from leading
indentation: one tab or every two spaces counts as one level, clamped
to depth 4 (a single stray space stays level 0).

Code fence immunity — lines inside a ````` ``` ````` or ``~~~`` fence
(three or more of the same character; the fence closes on a fence line
of the same character, and an unclosed fence runs to the end of input)
are never converted, so sample markdown quoted inside a document
survives byte-exact.  All non-list text outside converted blocks is
preserved byte-exact as well.

Conversion semantics (documented behaviour)
-------------------------------------------

Item text is taken verbatim after the marker (trailing whitespace
stripped; a marker standing alone yields an empty item — empty items
are preserved as empty segments, never dropped).  Top-level items of a
block are joined with connector words cycling by discourse role:

* first item — no connector by default, or ``First, `` when the
  ``lead_connector`` flag is on (default off);
* middle items — ``, and then ``;
* last item — ``, and finally ``.

A custom ``connectors`` dict ``{first, middle, last}`` (any subset)
overrides the defaults; provided connector strings are honored
EXACTLY as given (no case munging, no stripping).  Special cases: a
single-item block uses no connectors at all (not even the lead — a
lone item is not an enumeration), and a two-item block uses only the
last connector.  An explicit ``connectors['first']`` always wins over
the ``lead_connector`` flag.

Nested sub-lists are flattened inline: an item with children renders
as ``item (namely: a; b; c)`` — children joined by ``; ``, recursively
(a child with its own sub-list gains its own parenthetical, e.g.
``a (namely: b (namely: c))``).  Checkbox items keep their semantics:
``[x]``/``[X]`` appends `` (completed)`` and ``[ ]`` appends
`` (pending)`` to the item text.  The converted paragraph preserves
the block's original first-item indentation.

Idempotence — the converted prose contains no list markers, so
running ``convert`` over its own output finds no blocks and returns
the text unchanged.  The one pathological escape: when the FIRST
item's text itself looks like a bare list line after stitching (say a
single-item block ``- 1. example``), the tool inserts a markdown
backslash escape before the leading marker (``1\\. example`` /
``\\- example`` / ``\\[x] example``) so the second pass also sees no
list; such escapes are counted in the result payload.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, missing/empty/oversized ``text``,
non-boolean ``lead_connector``, a ``connectors`` mapping with unknown
keys, non-string, empty or oversized connector values) raise a
``ValueError``, mirroring the other common tools.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Bullet marker characters accepted at the start of an item: ASCII
# hyphen and asterisk, the typographic bullets U+2022 / U+00B7, and
# en / em dashes frequently left behind by scraped text.
_BULLET_CLASS = r'[-*•·–—]'

# Task checkbox: an optional bullet (marker plus separator) followed
# by a bracket box holding a space (unchecked) or x/X (checked).  The
# box may stand bare at line start ("[x] done") or ride on a bullet
# ("- [x] done"); the checked state is captured per item.
_CHECKBOX_RE = re.compile(
    r'^(?P<indent>[ \t]*)(?P<bullet>' + _BULLET_CLASS + r'[ \t]+)?'
    r'\[(?P<box>[ xX])\](?:[ \t]+(?P<rest>.*))?$'
)

# Plain bullet item: marker plus a separating whitespace run (so
# "--force", "**bold**" and "---" rules stay prose).  The rest is
# optional to the end of line for empty items.
_BULLET_RE = re.compile(
    r'^(?P<indent>[ \t]*)(?P<marker>' + _BULLET_CLASS +
    r')(?:[ \t]+(?P<rest>.*))?$'
)

# Numbered item families.  The digit run is bounded to nine digits so
# oversized numbers inside prose ("1234567890. hello") are not
# misread as enumerations.
_NUMBERED_PATTERNS = [
    (re.compile(r'^(?P<indent>[ \t]*)(?P<marker>\d{1,9}\.)'
                r'(?:[ \t]+(?P<rest>.*))?$'), 'arabic-dot'),
    (re.compile(r'^(?P<indent>[ \t]*)(?P<marker>\d{1,9}\))'
                r'(?:[ \t]+(?P<rest>.*))?$'), 'arabic-paren'),
    (re.compile(r'^(?P<indent>[ \t]*)(?P<marker>\([a-zA-Z]\))'
                r'(?:[ \t]+(?P<rest>.*))?$'), 'letter-paren'),
    (re.compile(r'^(?P<indent>[ \t]*)(?P<marker>\([一二三四五六七八九十百千零两]+\))'
                r'(?:[ \t]+(?P<rest>.*))?$'), 'cjk-paren'),
]

# Code fence opener/closer: three or more backticks or tildles after
# optional indentation.  A fence closes on a fence line built from the
# SAME character; fence lines and the lines between them are immune.
_FENCE_RE = re.compile(r'^(?P<lead>[ \t]*)(?P<fence>`{3,}|~{3,})')

# Maximum nesting level reported / used for tree building.
_MAX_DEPTH = 4

# Hard input limits (mirrored as pydantic attributes on the class).
_MAX_TEXT_CHARS = 100_000
_MAX_CONNECTOR_CHARS = 64

# Default discourse-role connectors (documented in the module
# docstring).  The default "first" connector is empty: no connector.
_DEFAULT_FIRST = ''
_DEFAULT_MIDDLE = ', and then '
_DEFAULT_LAST = ', and finally '

# Lead connector used when the lead_connector flag is on and no
# explicit "first" connector was provided.
_LEAD_CONNECTOR = 'First, '


def _indent_level(indent: str) -> int:
    """Nesting level of a leading whitespace run (family rule).

    One tab or every two spaces counts as one level; a single stray
    space stays level 0.  Clamped to ``_MAX_DEPTH``.
    """
    tabs = indent.count('\t')
    spaces = len(indent) - tabs
    return min(tabs + spaces // 2, _MAX_DEPTH)


def _parse_line(line: str):
    """Classify one line as a list item (or ``None`` for non-items).

    Checkbox patterns are tried first because "- [x] done" would
    otherwise parse as a bullet carrying bracket text; numbered
    families come next, plain bullets last.  Every recognized item
    reports its kind (bullet / numbered / checkbox), the marker style
    used for grouping consecutive items into blocks, the literal
    marker string, the nesting level, the item text (trailing
    whitespace stripped) and — for checkboxes — the checked state.
    """
    match = _CHECKBOX_RE.match(line)
    if match:
        bullet = match.group('bullet') or ''
        return {
            'kind': 'checkbox',
            'family': bullet[:1],
            'marker': f'{bullet[:1]} [{match.group("box")}]'.strip(),
            'indent': match.group('indent'),
            'level': _indent_level(match.group('indent')),
            'text': (match.group('rest') or '').rstrip(),
            'checked': match.group('box') != ' ',
        }
    match = _BULLET_RE.match(line)
    if match:
        return {
            'kind': 'bullet',
            'family': match.group('marker'),
            'marker': match.group('marker'),
            'indent': match.group('indent'),
            'level': _indent_level(match.group('indent')),
            'text': (match.group('rest') or '').rstrip(),
            'checked': None,
        }
    for pattern, family in _NUMBERED_PATTERNS:
        match = pattern.match(line)
        if match:
            return {
                'kind': 'numbered',
                'family': family,
                'marker': match.group('marker'),
                'indent': match.group('indent'),
                'level': _indent_level(match.group('indent')),
                'text': (match.group('rest') or '').rstrip(),
                'checked': None,
            }
    return None


def _fence_mask(lines: list) -> list:
    """Boolean per line: True when the line sits inside a code fence.

    A fence opens with ``` or ~~~ (three or more of one character,
    indentation allowed) and closes on a later fence line of the same
    character; the fence lines themselves are immune too.  An unclosed
    fence immunizes everything up to the end of the input.
    """
    mask = [False] * len(lines)
    open_char = None
    for index, line in enumerate(lines):
        match = _FENCE_RE.match(line)
        if open_char is None:
            if match:
                open_char = match.group('fence')[0]
                mask[index] = True
        elif match and match.group('fence')[0] == open_char:
            mask[index] = True
            open_char = None
        else:
            mask[index] = True
    return mask


def _find_blocks(lines: list) -> list:
    """Find every convertible list block in the given lines.

    Returns a list of ``(start, end, items)`` triples where ``start``
    and ``end`` are 0-based line indices of the block (inclusive) and
    ``items`` the parsed item dicts.  Consecutive items sharing one
    marker style (kind plus family) group into a block; a non-list
    line, a style change or a fenced line closes it.
    """
    immune = _fence_mask(lines)
    blocks = []
    index = 0
    total = len(lines)
    while index < total:
        if immune[index]:
            index += 1
            continue
        first = _parse_line(lines[index])
        if first is None:
            index += 1
            continue
        key = (first['kind'], first['family'])
        items = [first]
        end = index + 1
        while end < total and not immune[end]:
            parsed = _parse_line(lines[end])
            if parsed is None or (parsed['kind'], parsed['family']) != key:
                break
            items.append(parsed)
            end += 1
        blocks.append((index, end - 1, items))
        index = end
    return blocks


def _build_tree(items: list) -> list:
    """Build the item tree of one block from nesting levels.

    Returns the list of top-level nodes; every node is a dict with the
    parsed ``item`` and its ``children`` (deeper items that directly
    follow it while no shallower item intervenes).
    """
    roots: list = []
    stack: list = []
    for item in items:
        node = {'item': item, 'children': []}
        while stack and stack[-1]['item']['level'] >= item['level']:
            stack.pop()
        (stack[-1]['children'] if stack else roots).append(node)
        stack.append(node)
    return roots


def _render_item(node: dict) -> str:
    """Render one item node to its prose fragment.

    Checkbox semantics: the checked state is appended as
    `` (completed)`` / `` (pending)``.  Nested sub-lists are flattened
    inline with the ``(namely: a; b; c)`` parenthetical style,
    recursively.  Item text is used verbatim apart from that.
    """
    item = node['item']
    text = item['text']
    if item['kind'] == 'checkbox':
        text = (text + ' ') if text else ''
        text += '(completed)' if item['checked'] else '(pending)'
    if node['children']:
        flattened = '; '.join(_render_item(child) for child in node['children'])
        text = ((text + ' ') if text else '') + f'(namely: {flattened})'
    return text


def _assemble(rendered: list, first: str, middle: str, last: str) -> str:
    """Stitch rendered top-level items with discourse-role connectors.

    Single item — no connectors at all (not even the lead).  Two
    items — only the last connector.  Three or more — the first
    connector (when set) prefixes the first item, every middle item is
    preceded by the middle connector and the final item by the last
    connector.
    """
    if len(rendered) == 1:
        return rendered[0]
    parts = [first + rendered[0]] if first else [rendered[0]]
    for fragment in rendered[1:-1]:
        parts.append(middle + fragment)
    parts.append(last + rendered[-1])
    return ''.join(parts)


def _escape_leading_marker(paragraph: str) -> str:
    """Backslash-escape a paragraph that would re-parse as a list.

    When the stitched paragraph itself starts like a bare list line
    (only possible when the first item's own text looks like a
    marker), a markdown backslash escape is inserted before the
    leading marker so a second ``convert`` pass also finds no list
    (idempotence guard).  Ordinary prose never matches.
    """
    match = _CHECKBOX_RE.match(paragraph)
    if match:
        cut = match.start('box') - 1  # position of the '[' bracket
        return paragraph[:cut] + '\\' + paragraph[cut:]
    match = _BULLET_RE.match(paragraph)
    if match:
        cut = match.start('marker')
        return paragraph[:cut] + '\\' + paragraph[cut:]
    for pattern, _family in _NUMBERED_PATTERNS:
        match = pattern.match(paragraph)
        if match:
            marker = match.group('marker')
            # "(a)"-style markers escape the opening bracket, digit
            # markers escape the trailing '.' or ')'.
            cut = match.start('marker') if marker.startswith('(') \
                else match.end('marker') - 1
            return paragraph[:cut] + '\\' + paragraph[cut:]
    return paragraph


class BulletsToProseTool(Tool):
    """Bullet / numbered list to flowing prose converter tool.

    Deterministic list rewriting for doc agents — pure template
    stitching, never an LLM call.  Shares the recognition rules of
    ``ListStructureExtractor`` (PR #3663) and adds the rewrite the
    ecosystem was missing.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input
            length; longer inputs are rejected before any work.
        max_connector_chars (int): Upper bound on the length of each
            user-provided connector string.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "bullets_to_prose_tool"
    description: str = (
        "Bullets to prose tool — pure Python stdlib template stitching, "
        "no network and no LLM required. Convert every consecutive "
        "bullet/numbered block of a markdown text into a flowing prose "
        "paragraph with discourse-role connectors (first/middle/last, "
        "customizable), nested sub-lists flattened inline with "
        "'(namely: a; b; c)' parentheticals and checkboxes mapped to "
        "'(completed)'/'(pending)' (mode='convert'); preview which "
        "line-ranges would convert without rewriting (mode="
        "'paragraphs_only'); report blocks found, items converted and "
        "nesting levels seen (mode='stats'). Non-list text is preserved "
        "byte-exact and code fences are immune; the rewrite is "
        "idempotent."
    )

    MODES: ClassVar[tuple] = ("convert", "paragraphs_only", "stats")

    max_text_chars: int = 100_000
    max_connector_chars: int = 64

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        text: Any = None,
        lead_connector: Any = None,
        connectors: Any = None,
    ) -> dict:
        """Run one bullets-to-prose operation.

        Args:
            mode (str): One of ``convert`` / ``paragraphs_only`` /
                ``stats``.
            text (str): The markdown text to process; required for
                every mode.
            lead_connector (bool): When True, the first item of each
                multi-item block is prefixed with ``First, `` (unless
                an explicit ``connectors['first']`` overrides it).
                Default off.  Only affects ``convert``.
            connectors (dict[str, str] | None): Optional subset of
                ``{first, middle, last}`` custom connector strings,
                honored exactly as provided.  Only affects ``convert``.

        Returns:
            Dict[str, Any]: The operation result (a ``result`` key
                plus the call context) — see the mode docstrings for
                the exact payload shapes.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        validated_text = self._validate_text(text)
        lead = self._validate_lead_connector(lead_connector)
        custom = self._validate_connectors(connectors)
        blocks = _find_blocks(validated_text.split('\n'))
        if mode == 'convert':
            return self._run_convert(validated_text, lead, custom, blocks)
        if mode == 'paragraphs_only':
            return self._run_preview(blocks)
        return self._run_stats(blocks)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"bullets_to_prose_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input (all modes)."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > _MAX_TEXT_CHARS:
            cls._invalid(
                f"text exceeds the {_MAX_TEXT_CHARS:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_lead_connector(cls, lead_connector: Any) -> bool:
        """Validate the ``lead_connector`` flag (convert mode)."""
        if lead_connector is None:
            return False
        if isinstance(lead_connector, bool):
            return lead_connector
        cls._invalid(
            "lead_connector must be a boolean (got "
            f"{lead_connector!r})"
        )

    @classmethod
    def _validate_connectors(cls, connectors: Any) -> dict:
        """Validate the custom ``connectors`` mapping.

        Accepts ``None`` or a dict whose keys are a subset of
        ``{first, middle, last}`` and whose values are non-empty
        strings of at most ``max_connector_chars`` characters, honored
        exactly as provided (no stripping, no case changes).
        """
        if connectors is None:
            return {}
        if isinstance(connectors, bool) or not isinstance(connectors, dict):
            cls._invalid(
                "connectors must be a dict with any of the keys "
                f"'first', 'middle', 'last' mapped to connector strings "
                f"or None (got {connectors!r})"
            )
        cleaned: dict = {}
        for key, value in connectors.items():
            if key not in ('first', 'middle', 'last'):
                cls._invalid(
                    f"connectors keys must be one of 'first', 'middle', "
                    f"'last' (got {key!r})"
                )
            if value is None or isinstance(value, bool) \
                    or not isinstance(value, str):
                cls._invalid(
                    f"connector {key!r} must be a non-empty string "
                    f"(got {value!r})"
                )
            if not value:
                cls._invalid(
                    f"connector {key!r} must be a non-empty string "
                    f"(got {value!r})"
                )
            if len(value) > _MAX_CONNECTOR_CHARS:
                cls._invalid(
                    f"connector {key!r} exceeds the "
                    f"{_MAX_CONNECTOR_CHARS:,}-character limit (got "
                    f"{len(value):,} characters)"
                )
            cleaned[key] = value
        return cleaned

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _resolved_connectors(cls, lead: bool, custom: dict) -> dict:
        """Merge defaults, the lead flag and custom connectors.

        Precedence: an explicit ``connectors['first']`` always wins
        over the ``lead_connector`` flag; the flag is a shortcut for
        the default lead ``First, ``.
        """
        return {
            'first': custom.get('first', _LEAD_CONNECTOR if lead
                                else _DEFAULT_FIRST),
            'middle': custom.get('middle', _DEFAULT_MIDDLE),
            'last': custom.get('last', _DEFAULT_LAST),
        }

    @classmethod
    def _block_metadata(cls, start: int, end: int, items: list) -> dict:
        """Metadata describing one detected block (0-based indices)."""
        levels = [item['level'] for item in items]
        roots = _build_tree(items)
        return {
            'kind': items[0]['kind'],
            'family': items[0]['family'],
            'start_line': start + 1,
            'end_line': end + 1,
            'item_count': len(items),
            'top_level_item_count': len(roots),
            'nesting_depth': max(levels) - min(levels) + 1,
        }

    @staticmethod
    def _checkbox_totals(items: list) -> tuple:
        """(completed, pending) counts over every checkbox item."""
        completed = sum(
            1 for item in items if item['kind'] == 'checkbox' and item['checked']
        )
        pending = sum(
            1 for item in items if item['kind'] == 'checkbox'
            and not item['checked']
        )
        return completed, pending

    # ------------------------------------------------------------------ #
    # convert mode
    # ------------------------------------------------------------------ #

    def _run_convert(
        self, text: str, lead: bool, custom: dict, blocks: list
    ) -> dict:
        """Rewrite every detected list block into a prose paragraph.

        Non-list lines (and everything inside code fences) pass
        through byte-exact; each block is replaced by a single
        paragraph line preserving the block's first-item indentation.
        """
        connectors = self._resolved_connectors(lead, custom)
        lines = text.split('\n')
        rebuilt: list = []
        metadata: list = []
        cursor = 0
        escaped_paragraphs = 0
        completed_total = 0
        pending_total = 0
        for start, end, items in blocks:
            rebuilt.extend(lines[cursor:start])
            cursor = end + 1
            completed, pending = self._checkbox_totals(items)
            completed_total += completed
            pending_total += pending
            rendered = [_render_item(node) for node in _build_tree(items)]
            paragraph = items[0]['indent'] + _assemble(
                rendered, connectors['first'], connectors['middle'],
                connectors['last']
            )
            guarded = _escape_leading_marker(paragraph)
            if guarded != paragraph:
                escaped_paragraphs += 1
            rebuilt.append(guarded)
            metadata.append(self._block_metadata(start, end, items))
        rebuilt.extend(lines[cursor:])
        item_count = sum(block['item_count'] for block in metadata)
        return {
            'mode': 'convert',
            'result': '\n'.join(rebuilt),
            'blocks': metadata,
            'block_count': len(metadata),
            'item_count': item_count,
            'top_level_item_count': sum(
                block['top_level_item_count'] for block in metadata
            ),
            'max_nesting_depth': max(
                (block['nesting_depth'] for block in metadata), default=0
            ),
            'checkbox_counts': {
                'completed': completed_total,
                'pending': pending_total,
            },
            'escaped_paragraph_count': escaped_paragraphs,
        }

    # ------------------------------------------------------------------ #
    # paragraphs_only mode (preview)
    # ------------------------------------------------------------------ #

    def _run_preview(self, blocks: list) -> dict:
        """Report which line-ranges would convert — no rewriting."""
        metadata = [
            self._block_metadata(start, end, items)
            for start, end, items in blocks
        ]
        return {
            'mode': 'paragraphs_only',
            'result': metadata,
            'block_count': len(metadata),
            'item_count': sum(block['item_count'] for block in metadata),
            'max_nesting_depth': max(
                (block['nesting_depth'] for block in metadata), default=0
            ),
        }

    # ------------------------------------------------------------------ #
    # stats mode
    # ------------------------------------------------------------------ #

    def _run_stats(self, blocks: list) -> dict:
        """Count blocks found, items converted and nesting levels."""
        metadata = [
            self._block_metadata(start, end, items)
            for start, end, items in blocks
        ]
        completed_total = 0
        pending_total = 0
        for _start, _end, items in blocks:
            completed, pending = self._checkbox_totals(items)
            completed_total += completed
            pending_total += pending
        nesting_levels = sorted(
            {block['nesting_depth'] for block in metadata}
        )
        return {
            'mode': 'stats',
            'result': {
                'blocks': len(metadata),
                'items': sum(block['item_count'] for block in metadata),
                'top_level_items': sum(
                    block['top_level_item_count'] for block in metadata
                ),
                'nesting_levels': nesting_levels,
                'max_nesting_depth': max(nesting_levels, default=0),
                'checkbox_counts': {
                    'completed': completed_total,
                    'pending': pending_total,
                },
            },
            'block_count': len(metadata),
            'item_count': sum(block['item_count'] for block in metadata),
            'max_nesting_depth': max(nesting_levels, default=0),
        }
