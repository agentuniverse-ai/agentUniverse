#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: indent_tree_tool.py

"""Indentation-based hierarchy utility tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency parser for the
plain-text hierarchies agents keep meeting: file-explorer outlines,
org charts, work-breakdown structures, nested checklists — any
outline whose structure lives in leading whitespace. The existing
``OutlineExtractor`` knowledge component extracts markdown *heading*
structure; nothing in the common tool set parses *indentation* trees,
which is exactly the gap this tool fills.

Five modes are supported:

* ``parse`` — convert indented plain text into a nested tree of
  ``{"text": str, "level": int, "children": []}`` nodes. ``level`` is
  the 1-based indent-unit depth: a line starting at column 0 is level
  1 and every additional indent unit adds one level. The unit is the
  ``indent_unit`` option: ``auto`` (default — the smallest observed
  indent width of at least 2 columns that every other observed indent
  width is a multiple of; tabs count as ``TAB_WIDTH`` = 4 columns each,
  with no tab-stop alignment), an explicit ``2`` / ``4`` / ``8``
  space unit, or ``tab`` (equivalent to a 4-column unit). Dedenting
  makes a line a sibling of the shallower entry. Malformed input is
  tolerated, never fatal: an indent that is not a multiple of the unit
  is floored to the nearest shallower level, a line jumping more than
  one level below its predecessor is clamped to ``parent + 1``, and a
  first line that is already indented is treated as level 1 — each
  with a structured warning entry describing the line, the indent and
  the level applied. As a documented convenience so the tool can
  re-ingest its own ``to_markdown`` output, ``parse`` also accepts
  input consisting purely of ATX headings (``#`` to ``######`` at
  column 0): heading ranks are normalized so the smallest rank present
  maps to level 1, and the same jump clamping applies.
* ``flatten`` — convert a tree into the flat outline table: one
  ``{"text", "level", "path", "order"}`` row per node in document
  order (pre-order depth-first), where ``path`` is the slash-joined
  ``"/A/B/C"`` route from the root and ``order`` is the 0-based row
  index.
* ``paths`` — just the leaf paths (nodes without children) whose level
  is within the inclusive ``min_depth`` / ``max_depth`` filters
  (defaults 1 and unbounded).
* ``depth_stats`` — ``node_count``, ``max_depth``, the per-level
  ``level_counts`` mapping, and the ``widest_level`` (ties resolved to
  the smallest level).
* ``to_markdown`` — render the tree as ATX markdown nested by level:
  a level ``L`` node becomes a heading of rank ``L + min_level - 1``
  (``min_level`` defaults to 1). Ranks are clamped at the markdown
  maximum of six with a warning per clamped node, so trees deeper
  than six levels lose level information in the rendering.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode / ``indent_unit``,
out-of-range ``min_depth`` / ``max_depth`` / ``min_level``,
``min_depth`` greater than ``max_depth``, an empty ``tree`` list,
a node without non-blank ``text``, ``children`` that is not a list,
cyclic or shared node references, more than ``max_nodes`` nodes,
trees deeper than ``max_depth_levels`` levels, text over
``max_text_chars`` characters) raise a ``ValueError``, mirroring the
other common tools. Structure-level problems in the text being parsed
are never exceptions — they produce the tolerant clamps and warning
entries described above.
"""

import re
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# 1-6 '#' at column 0, at least one space/tab, then non-empty text.
_ATX_HEADING = re.compile(r"\A(#{1,6})[ \t]+(\S.*?)[ \t]*\Z")


class IndentTreeTool(Tool):
    """Indentation-based hierarchy tool built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length
            for the ``parse`` mode; longer inputs are rejected before
            any work.
        max_nodes (int): Upper bound on the number of tree nodes the
            tool will build or accept.
        max_depth_levels (int): Upper bound on tree depth in levels.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "indent_tree_tool"
    description: str = (
        "Indentation tree tool — pure Python stdlib, no network "
        "required. Parses indentation-based hierarchies (file-explorer "
        "outlines, org charts, plain-text trees) into nested "
        "{text, level, children} structures (mode='parse', with "
        "auto-detected or explicit 2/4/8/tab indent units and tolerant "
        "clamping of malformed indents), flattens a tree into "
        "{text, level, path, order} outline rows (mode='flatten'), "
        "lists leaf paths with depth filters (mode='paths'), reports "
        "max depth / per-level counts / widest level (mode='depth_stats'), "
        "and renders a tree as ATX markdown nested by level "
        "(mode='to_markdown')."
    )

    MODES: ClassVar[tuple] = (
        "parse",
        "flatten",
        "paths",
        "depth_stats",
        "to_markdown",
    )
    SPACE_UNITS: ClassVar[tuple] = (2, 4, 8)
    # Each tab counts as 4 columns; there is no tab-stop alignment.
    TAB_WIDTH: ClassVar[int] = 4
    ATX_MAX_RANK: ClassVar[int] = 6
    # Upper bounds, enforced before any computation.
    max_text_chars: ClassVar[int] = 100_000
    max_nodes: ClassVar[int] = 10_000
    max_depth_levels: ClassVar[int] = 256
    max_warnings: ClassVar[int] = 100

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        tree: Any = None,
        indent_unit: Any = None,
        min_depth: Any = None,
        max_depth: Any = None,
        min_level: Any = None,
    ) -> Dict[str, Any]:
        """Run one indentation-tree operation.

        Args:
            mode (str): One of ``parse`` / ``flatten`` / ``paths`` /
                ``depth_stats`` / ``to_markdown``.
            text (str): The indented plain text — required for the
                ``parse`` mode. Blank or all-whitespace input yields an
                empty tree; input made purely of ATX headings is parsed
                by heading rank.
            tree (list): The nested ``[{text, level, children}]``
                structure — required for the ``flatten``, ``paths``,
                ``depth_stats`` and ``to_markdown`` modes. ``level`` is
                validated when present but always recomputed from the
                nesting position; unknown extra keys are ignored.
            indent_unit (str | int): ``parse`` only — ``auto`` (default),
                ``2`` / ``4`` / ``8`` (spaces) or ``tab``.
            min_depth (int): ``paths`` only — smallest leaf level kept
                (inclusive); defaults to 1.
            max_depth (int): ``paths`` only — largest leaf level kept
                (inclusive); defaults to unbounded.
            min_level (int): ``to_markdown`` only — heading rank of
                level-1 nodes (1-6); defaults to 1.

        Returns:
            Dict[str, Any]: The operation result. The ``parse`` result
                carries the nested ``tree`` plus ``input_format``,
                ``indent_unit``, ``node_count``, ``max_depth`` and the
                tolerant ``warnings`` list; the other modes carry the
                structure described in the module docstring.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "parse":
            return self._run_parse(text, indent_unit)
        return self._run_tree_mode(mode, tree, min_depth, max_depth, min_level)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"indent_tree_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input of the parse mode.

        Unlike the codec-style tools the parser has a well-defined
        result for blank input (an empty tree), so only the type and
        the size are checked here.
        """
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a string (got {text!r})")
        if len(text) > cls.max_text_chars:
            cls._invalid(
                f"text exceeds the {cls.max_text_chars:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_indent_unit(cls, indent_unit: Any) -> Tuple[str, int]:
        """Validate the ``indent_unit`` option; return (label, columns)."""
        if indent_unit is None:
            return "auto", 0
        if isinstance(indent_unit, bool):
            cls._invalid(
                f"indent_unit must be one of: auto, tab, 2, 4, 8 "
                f"(got {indent_unit!r})"
            )
        if isinstance(indent_unit, int):
            indent_unit = str(indent_unit)
        space_labels = tuple(str(unit) for unit in cls.SPACE_UNITS)
        if indent_unit == "auto":
            return "auto", 0
        if indent_unit == "tab":
            return "tab", cls.TAB_WIDTH
        if indent_unit in space_labels:
            return indent_unit, int(indent_unit)
        cls._invalid(
            f"indent_unit must be one of: auto, tab, {', '.join(space_labels)} "
            f"(got {indent_unit!r})"
        )

    @classmethod
    def _validate_depth_filter(cls, min_depth: Any, max_depth: Any) -> Tuple[int, Optional[int]]:
        """Validate the ``paths``-mode depth filters."""
        for label, value in (("min_depth", min_depth), ("max_depth", max_depth)):
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int):
                cls._invalid(f"{label} must be a positive integer or None (got {value!r})")
            if value < 1:
                cls._invalid(f"{label} must be a positive integer or None (got {value})")
        clean_min = 1 if min_depth is None else min_depth
        if max_depth is not None and clean_min > max_depth:
            cls._invalid(
                f"min_depth must not exceed max_depth (got {clean_min} > {max_depth})"
            )
        return clean_min, max_depth

    @classmethod
    def _validate_min_level(cls, min_level: Any) -> int:
        """Validate the ``to_markdown``-mode ``min_level`` option."""
        if min_level is None:
            return 1
        if isinstance(min_level, bool) or not isinstance(min_level, int):
            cls._invalid(f"min_level must be an integer between 1 and 6 (got {min_level!r})")
        if not 1 <= min_level <= cls.ATX_MAX_RANK:
            cls._invalid(f"min_level must be an integer between 1 and 6 (got {min_level})")
        return min_level

    @classmethod
    def _normalize_tree(cls, tree: Any) -> List[Dict[str, Any]]:
        """Validate a user-supplied ``tree`` and normalize its nodes.

        Returns the list of root nodes as ``{"text": str, "children":
        [...]}`` dicts with ``level`` recomputed from the nesting
        position. Validation is iterative (no recursion) so deep or
        adversarial structures cannot overflow the interpreter stack;
        cyclic or shared node references are rejected because a tree
        must present each node exactly once.
        """
        if tree is None or isinstance(tree, bool) or not isinstance(tree, list):
            cls._invalid(f"tree must be a non-empty list of node objects (got {tree!r})")
        if not tree:
            cls._invalid("tree must be a non-empty list of node objects (got [])")
        roots: List[Dict[str, Any]] = []
        # Stack of (target_children_list, source_iterator).
        stack: List[Tuple[List[Dict[str, Any]], Any]] = [(roots, iter(tree))]
        seen: Dict[int, bool] = {}
        count = 0
        while stack:
            target, source = stack[-1]
            raw = next(source, None)
            if raw is None:
                stack.pop()
                continue
            if isinstance(raw, bool) or not isinstance(raw, dict):
                cls._invalid(f"each tree node must be an object (got {raw!r})")
            node_id = id(raw)
            if node_id in seen:
                cls._invalid(
                    "tree must be a strict tree: cyclic or shared node "
                    f"references are rejected (first repeated node text: "
                    f"{str(raw.get('text'))[:50]!r})"
                )
            seen[node_id] = True
            node_text = raw.get("text")
            if (
                node_text is None
                or isinstance(node_text, bool)
                or not isinstance(node_text, str)
                or not node_text.strip()
            ):
                cls._invalid(
                    f"each tree node must have a non-blank string 'text' (got {node_text!r})"
                )
            level_field = raw.get("level")
            if level_field is not None and (
                isinstance(level_field, bool) or not isinstance(level_field, int) or level_field < 1
            ):
                cls._invalid(
                    f"tree node 'level' must be a positive integer or absent (got {level_field!r})"
                )
            children = raw.get("children", [])
            if children is None or isinstance(children, bool) or not isinstance(children, list):
                cls._invalid(
                    f"tree node 'children' must be a list (got {children!r})"
                )
            count += 1
            if count > cls.max_nodes:
                cls._invalid(
                    f"tree exceeds the {cls.max_nodes:,}-node limit "
                    f"(got more than {cls.max_nodes:,} nodes)"
                )
            if len(stack) > cls.max_depth_levels:
                cls._invalid(
                    f"tree exceeds the {cls.max_depth_levels}-level depth limit"
                )
            node = {"text": node_text.strip(), "children": []}
            target.append(node)
            if children:
                stack.append((node["children"], iter(children)))
        return roots

    # ------------------------------------------------------------------ #
    # parse mode
    # ------------------------------------------------------------------ #

    def _run_parse(self, text: Any, indent_unit: Any) -> Dict[str, Any]:
        """Parse indented plain text (or pure ATX headings) into a tree."""
        clean_text = self._validate_text(text)
        requested_unit, _ = self._validate_indent_unit(indent_unit)

        # Collect non-blank lines as (lineno, raw, columns, body).
        entries: List[Tuple[int, str, int, str]] = []
        for lineno, raw in enumerate(clean_text.splitlines(), start=1):
            columns, rest = self._measure_indent(raw)
            if not rest.strip():
                continue
            entries.append((lineno, raw, columns, rest.rstrip()))
        if not entries:
            return {
                "mode": "parse",
                "input_format": "indentation",
                "indent_unit": {"requested": requested_unit, "unit_columns": self.TAB_WIDTH},
                "node_count": 0,
                "max_depth": 0,
                "warning_count": 0,
                "warnings": [],
                "tree": [],
            }

        if _ATX_HEADING.match(entries[0][1]):
            items, pre_warnings = self._parse_atx_entries(entries)
            unit_report: Optional[Dict[str, Any]] = None
            input_format = "atx_headings"
        else:
            items, pre_warnings, unit_columns = self._parse_indent_entries(
                entries, requested_unit
            )
            unit_report = {"requested": requested_unit, "unit_columns": unit_columns}
            input_format = "indentation"

        roots, warnings, node_count, max_depth = self._build_tree(items)
        # Report warnings in line order; the stable sort keeps the
        # measurement warnings of a line before its build warnings and
        # the global auto-detect warning (no line) first.
        warnings = sorted(
            pre_warnings + warnings, key=lambda w: w.get("line", 0)
        )
        warning_count = len(warnings)
        if warning_count > self.max_warnings:
            warnings = warnings[: self.max_warnings]
            warnings.append(
                {
                    "type": "warnings_truncated",
                    "message": (
                        f"{warning_count} warnings occurred; only the first "
                        f"{self.max_warnings} are reported"
                    ),
                }
            )
        return {
            "mode": "parse",
            "input_format": input_format,
            "indent_unit": unit_report,
            "node_count": node_count,
            "max_depth": max_depth,
            "warning_count": warning_count,
            "warnings": warnings,
            "tree": roots,
        }

    @classmethod
    def _measure_indent(cls, line: str) -> Tuple[int, str]:
        """Return (indent columns, remainder) for one raw line.

        A space adds one column and a tab adds ``TAB_WIDTH`` columns;
        there is no tab-stop alignment. All other characters end the
        indent, even unicode whitespace.
        """
        columns = 0
        index = 0
        while index < len(line) and line[index] in (" ", "\t"):
            columns += 1 if line[index] == " " else cls.TAB_WIDTH
            index += 1
        return columns, line[index:]

    def _parse_atx_entries(
        self, entries: List[Tuple[int, str, int, str]]
    ) -> Tuple[List[Tuple[int, int, str]], List[Dict[str, Any]]]:
        """Convert pure ATX-heading input into (lineno, depth, text) items.

        Heading ranks are normalized so the smallest rank present maps
        to level 1, which is exactly what ``to_markdown(min_level=k)``
        emits; a leading line above the minimum rank is clamped by the
        shared tree builder with a warning.
        """
        ranks: List[Tuple[int, int, str]] = []
        for lineno, raw, _columns, _body in entries:
            match = _ATX_HEADING.match(raw)
            if match is None:
                self._invalid(
                    f"line {lineno}: input starts with an ATX heading but "
                    f"this line is not one — mixtures are not supported "
                    f"(got {raw[:64]!r})"
                )
            ranks.append((lineno, len(match.group(1)), match.group(2)))
        min_rank = min(rank for _lineno, rank, _text in ranks)
        return [
            (lineno, rank - min_rank, heading_text)
            for lineno, rank, heading_text in ranks
        ], []

    def _parse_indent_entries(
        self, entries: List[Tuple[int, str, int, str]], requested_unit: str
    ) -> Tuple[List[Tuple[int, int, str]], List[Dict[str, Any]], int]:
        """Convert indentation input into (lineno, depth, text) items."""
        warnings: List[Dict[str, Any]] = []
        if requested_unit == "auto":
            positive = sorted({columns for _l, _r, columns, _b in entries if columns > 0})
            if not positive:
                unit_columns = self.TAB_WIDTH
            else:
                unit_columns = 0
                for candidate in positive:
                    if candidate >= 2 and all(value % candidate == 0 for value in positive):
                        unit_columns = candidate
                        break
                if unit_columns == 0:
                    unit_columns = self.TAB_WIDTH
                    warnings.append(
                        {
                            "type": "auto_unit_fallback",
                            "message": (
                                "no observed indent width consistently "
                                f"divides the others ({positive}); falling "
                                f"back to the default {self.TAB_WIDTH}-column "
                                "unit and per-line tolerance"
                            ),
                        }
                    )
        else:
            unit_columns = self._validate_indent_unit(requested_unit)[1]

        items: List[Tuple[int, int, str]] = []
        for lineno, _raw, columns, body in entries:
            depth = columns // unit_columns
            if columns % unit_columns != 0:
                warnings.append(
                    {
                        "line": lineno,
                        "text": body[:50],
                        "type": "indent_not_multiple",
                        "message": (
                            f"line {lineno}: indent of {columns} columns is "
                            f"not a multiple of the {unit_columns}-column "
                            f"indent unit; treated as depth {depth} "
                            f"(level {depth + 1})"
                        ),
                    }
                )
            items.append((lineno, depth, body))
        return items, warnings, unit_columns

    def _build_tree(
        self, items: List[Tuple[int, int, str]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int, int]:
        """Build the nested tree from (lineno, ideal_depth, text) items.

        Dedent makes a sibling; an ideal depth more than one below the
        predecessor is clamped to ``parent + 1``; the first item is
        always level 1. Every clamp appends a structured warning.
        """
        roots: List[Dict[str, Any]] = []
        # Stack of [depth, node] for the current ancestry.
        stack: List[List[Any]] = []
        warnings: List[Dict[str, Any]] = []
        node_count = 0
        max_depth = 0
        for lineno, ideal_depth, node_text in items:
            if not stack:
                depth = 0
                if ideal_depth > 0:
                    warnings.append(
                        {
                            "line": lineno,
                            "text": node_text[:50],
                            "type": "leading_indent_ignored",
                            "message": (
                                f"line {lineno}: the first entry is indented "
                                f"by {ideal_depth} unit(s); treated as "
                                "level 1"
                            ),
                        }
                    )
            else:
                previous_depth = stack[-1][0]
                if ideal_depth > previous_depth + 1:
                    depth = previous_depth + 1
                    warnings.append(
                        {
                            "line": lineno,
                            "text": node_text[:50],
                            "type": "level_jump_clamped",
                            "message": (
                                f"line {lineno}: jumps from level "
                                f"{previous_depth + 1} to level "
                                f"{ideal_depth + 1}; clamped to parent + 1 "
                                f"(level {depth + 1})"
                            ),
                        }
                    )
                else:
                    depth = ideal_depth
            if depth + 1 > self.max_depth_levels:
                self._invalid(
                    f"tree exceeds the {self.max_depth_levels}-level depth "
                    f"limit (line {lineno})"
                )
            while stack and stack[-1][0] >= depth:
                stack.pop()
            node_count += 1
            if node_count > self.max_nodes:
                self._invalid(
                    f"text exceeds the {self.max_nodes:,}-node limit "
                    f"(got more than {self.max_nodes:,} lines)"
                )
            node = {"text": node_text, "level": depth + 1, "children": []}
            if stack:
                stack[-1][1]["children"].append(node)
            else:
                roots.append(node)
            stack.append([depth, node])
            if depth + 1 > max_depth:
                max_depth = depth + 1
        return roots, warnings, node_count, max_depth

    # ------------------------------------------------------------------ #
    # flatten / paths / depth_stats / to_markdown modes
    # ------------------------------------------------------------------ #

    def _run_tree_mode(
        self,
        mode: str,
        tree: Any,
        min_depth: Any,
        max_depth: Any,
        min_level: Any,
    ) -> Dict[str, Any]:
        """Run one of the tree-consuming modes on a validated tree."""
        roots = self._normalize_tree(tree)
        rows = self._flatten_rows(roots)
        if mode == "flatten":
            return {
                "mode": "flatten",
                "row_count": len(rows),
                "rows": rows,
            }
        if mode == "paths":
            clean_min, clean_max = self._validate_depth_filter(min_depth, max_depth)
            leaf_paths = self._leaf_paths(roots, clean_min, clean_max)
            return {
                "mode": "paths",
                "min_depth": clean_min,
                "max_depth": clean_max,
                "count": len(leaf_paths),
                "paths": leaf_paths,
            }
        if mode == "depth_stats":
            counts: Dict[int, int] = {}
            for row in rows:
                counts[row["level"]] = counts.get(row["level"], 0) + 1
            widest_level, widest_count = max(
                counts.items(), key=lambda item: (item[1], -item[0])
            )
            return {
                "mode": "depth_stats",
                "node_count": len(rows),
                "max_depth": max(counts),
                "level_counts": {str(level): counts[level] for level in sorted(counts)},
                "widest_level": widest_level,
                "widest_level_count": widest_count,
            }
        return self._run_to_markdown(rows, min_level)

    @classmethod
    def _leaf_paths(
        cls, roots: List[Dict[str, Any]], min_depth: int, max_depth: Optional[int]
    ) -> List[str]:
        """Collect document-order paths of leaves within the depth window.

        A leaf is a node without children; only leaves whose level is
        at least ``min_depth`` and (when given) at most ``max_depth``
        are kept.
        """
        leaf_paths: List[str] = []
        stack: List[Tuple[Dict[str, Any], List[str]]] = [
            (node, []) for node in reversed(roots)
        ]
        while stack:
            node, path = stack.pop()
            parts = path + [node["text"]]
            level = len(parts)
            if (
                not node["children"]
                and level >= min_depth
                and (max_depth is None or level <= max_depth)
            ):
                leaf_paths.append("/" + "/".join(parts))
            for child in reversed(node["children"]):
                stack.append((child, parts))
        return leaf_paths

    @classmethod
    def _flatten_rows(cls, roots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Flatten a normalized tree into document-order outline rows."""
        rows: List[Dict[str, Any]] = []
        stack: List[Tuple[Dict[str, Any], List[str]]] = [
            (node, []) for node in reversed(roots)
        ]
        order = 0
        while stack:
            node, path = stack.pop()
            parts = path + [node["text"]]
            rows.append(
                {
                    "text": node["text"],
                    "level": len(parts),
                    "path": "/" + "/".join(parts),
                    "order": order,
                }
            )
            order += 1
            for child in reversed(node["children"]):
                stack.append((child, parts))
        return rows

    def _run_to_markdown(self, rows: List[Dict[str, Any]], min_level: Any) -> Dict[str, Any]:
        """Render outline rows as ATX markdown nested by level."""
        clean_min_level = self._validate_min_level(min_level)
        lines: List[str] = []
        warnings: List[Dict[str, Any]] = []
        for row in rows:
            rank = row["level"] + clean_min_level - 1
            if rank > self.ATX_MAX_RANK:
                warnings.append(
                    {
                        "type": "heading_rank_clamped",
                        "path": row["path"],
                        "message": (
                            f"node {row['path']} is level {row['level']}; "
                            f"heading rank {row['level'] + clean_min_level - 1} "
                            f"exceeds the markdown maximum of "
                            f"{self.ATX_MAX_RANK} and was clamped"
                        ),
                    }
                )
                rank = self.ATX_MAX_RANK
            lines.append("#" * rank + " " + row["text"])
        warning_count = len(warnings)
        if warning_count > self.max_warnings:
            warnings = warnings[: self.max_warnings]
            warnings.append(
                {
                    "type": "warnings_truncated",
                    "message": (
                        f"{warning_count} warnings occurred; only the first "
                        f"{self.max_warnings} are reported"
                    ),
                }
            )
        return {
            "mode": "to_markdown",
            "min_level": clean_min_level,
            "line_count": len(lines),
            "warning_count": warning_count,
            "warnings": warnings,
            "markdown": "\n".join(lines) + ("\n" if lines else ""),
        }
