#!/usr/bin/env python3
"""Offline HTML table extraction to structured data with span expansion."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import csv
import io
from html import unescape
from html.parser import HTMLParser
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

# Void elements never get children and contribute no cell text.
_VOID_ELEMENTS = frozenset(
    "area base br col embed hr img input link meta param source track wbr".split()
)
# Starts that implicitly close an open cell or row in lenient parsing. A nested
# <table> never closes its own cell: it belongs inside that cell per the HTML parser.
_IMPLIED_END_FOR_CELL = frozenset({"td", "th", "tr", "thead", "tbody", "tfoot", "caption", "colgroup"})
_IMPLIED_END_FOR_ROW = frozenset({"tr", "thead", "tbody", "tfoot", "caption", "colgroup"})
_DROPPED_SUBTREES = frozenset({"script", "style"})
_WHATWG_MAX_COLSPAN = 1000
_WHATWG_MAX_ROWSPAN = 65534


class _Node:
    """Minimal DOM node built by the stdlib HTMLParser."""

    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag: str, attrs: dict[str, str], parent: "_Node | None") -> None:
        self.tag = tag
        self.attrs = attrs
        self.children: list[Any] = []
        self.parent = parent


class _TreeBuilder(HTMLParser):
    """Builds a lightweight element tree, tolerating omitted end tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("#document", {}, None)
        self.stack: list[_Node] = [self.root]

    def handle_starttag(self, tag, attrs):
        current = self.stack[-1]
        if tag in _IMPLIED_END_FOR_CELL and current.tag in ("td", "th"):
            self.stack.pop()
            current = self.stack[-1]
        if tag in _IMPLIED_END_FOR_ROW and current.tag == "tr":
            self.stack.pop()
            current = self.stack[-1]
        decoded = {key: unescape(value) if isinstance(value, str) else "" for key, value in attrs}
        node = _Node(tag, decoded, current)
        current.children.append(node)
        if tag not in _VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        current = self.stack[-1]
        decoded = {key: unescape(value) if isinstance(value, str) else "" for key, value in attrs}
        current.children.append(_Node(tag, decoded, current))

    def handle_endtag(self, tag):
        if tag in _VOID_ELEMENTS:
            return
        for position in range(len(self.stack) - 1, 0, -1):
            if self.stack[position].tag == tag:
                del self.stack[position:]
                return

    def handle_data(self, data):
        if data:
            self.stack[-1].children.append(data)

    # Comments, doctypes, declarations and processing instructions are ignored.
    def handle_comment(self, data):
        pass

    def handle_decl(self, decl):
        pass

    def unknown_decl(self, data):
        pass

    def handle_pi(self, data):
        pass


class _Cell:
    """One td/th with declared span values, pre-computed text and source node."""

    __slots__ = ("text", "rowspan", "colspan", "is_header", "node")

    def __init__(self, text: str, rowspan: int, colspan: int, is_header: bool, node: _Node) -> None:
        self.text = text
        self.rowspan = rowspan
        self.colspan = colspan
        self.is_header = is_header
        self.node = node


class _ParsedTable:
    """Intermediate representation of one table before grid expansion."""

    __slots__ = ("element", "depth", "index", "caption", "summary", "presentation",
                 "rows", "direct_children", "descendants")

    def __init__(self, element: _Node, depth: int, index: int) -> None:
        self.element = element
        self.depth = depth
        self.index = index
        self.caption: str | None = None
        self.summary: str | None = None
        self.presentation = False
        # Each row: (cells, section_first_row, section_last_row) in document order.
        self.rows: list[tuple[list[_Cell], int, int]] = []
        # Directly nested tables (nearest enclosing table is this one).
        self.direct_children: list[tuple[int, _Node]] = []
        # Every descendant table element, for depth reporting and truncation counts.
        self.descendants: list[_Node] = []


class HtmlTableTool(Tool):
    """Extract HTML tables to structured data with rowspan/colspan expansion.

    Modes: ``extract`` (tables with expanded grids and header detection),
    ``analyze`` (per-table findings), ``to_csv`` (one table as CSV text) and
    ``compare`` (cell-level diff of two tables). Runtime is stdlib-only.

    Expansion follows the WHATWG fixed table-processing semantics: a rowspan
    fills downward copies and a colspan fills rightward copies of the cell
    text (copies, not merged markers). colspan=0 is expanded per the
    historical HTML4 "span to the end of the row" rule and flagged;
    rowspan=0 spans to the end of its row group per the HTML Standard;
    a rowspan past the last row is clamped to the remaining rows and flagged.

    Cell text rules: character references are decoded, script/style subtrees
    are dropped, nested tables are reported as child references instead of
    inlined text, and runs of Unicode whitespace (non-breaking spaces
    included) collapse to a single space. <br> contributes one space.
    """

    max_input_bytes: int = 4 * 1024 * 1024
    max_tables: int = 50_000
    max_rows_per_table: int = 100_000
    max_cell_chars: int = 1_000_000
    max_table_depth: int = 3
    max_changed_cells: int = 10_000

    _MODES: ClassVar[tuple[str, ...]] = ("extract", "analyze", "to_csv", "compare")

    def execute(
        self,
        mode: str,
        html: str | None = None,
        html2: str | None = None,
        table_index: int = 0,
        table_index2: int = 0,
        table_a: dict[str, Any] | None = None,
        table_b: dict[str, Any] | None = None,
        raw_spans: bool = False,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            if operation == "compare":
                return self._compare(html, html2, table_index, table_index2, table_a, table_b)
            if not isinstance(html, str) or not html:
                raise ValueError("html must be a non-empty string")
            tables = self._collect(html)
            if operation == "extract":
                return self._extract(tables, table_index, raw_spans)
            if operation == "analyze":
                return self._analyze(tables)
            return self._to_csv(tables, table_index)
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except RecursionError as exc:
            return self._error(mode, "operation_error", f"HTML table operation failed: nesting too deep ({exc})")
        except Exception as exc:
            return self._error(mode, "operation_error", f"HTML table operation failed: {exc}")

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode}

    def _validate_config(self) -> None:
        for name in ("max_input_bytes", "max_tables", "max_rows_per_table", "max_cell_chars",
                     "max_table_depth", "max_changed_cells"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

    @staticmethod
    def _mode(mode: Any) -> str:
        if not isinstance(mode, str) or mode not in HtmlTableTool._MODES:
            raise ValueError(f"mode must be one of {list(HtmlTableTool._MODES)}")
        return mode

    def _check_input_size(self, html: str) -> None:
        size = len(html.encode("utf-8", errors="replace"))
        if size > self.max_input_bytes:
            raise ValueError(f"html exceeds max_input_bytes ({size} > {self.max_input_bytes} bytes)")

    @staticmethod
    def _parse(html: str) -> _Node:
        builder = _TreeBuilder()
        builder.feed(html)
        builder.close()
        return builder.root

    # ------------------------------------------------------------------ #
    # Table collection                                                    #
    # ------------------------------------------------------------------ #

    def _collect(self, html: str) -> list[_ParsedTable]:
        self._check_input_size(html)
        root = self._parse(html)
        # Pass one: assign document-order indexes and depths to every table.
        ordered: list[tuple[_Node, int]] = []
        stack: list[tuple[_Node | Any, int]] = [(root, 0)]
        while stack:
            node, depth = stack.pop()
            if not isinstance(node, _Node):
                continue
            for child in reversed(node.children):
                if isinstance(child, _Node):
                    if child.tag == "table":
                        ordered.append((child, depth))
                        stack.append((child, depth + 1))
                    else:
                        stack.append((child, depth))
        if len(ordered) > self.max_tables:
            raise ValueError(f"document exceeds max_tables ({len(ordered)} > {self.max_tables})")
        # The stack walk discovers children before later siblings get popped;
        # restore strict document order by re-walking with pre-order recursion.
        tables: list[_ParsedTable] = []
        by_element: dict[int, _ParsedTable] = {}
        counter = 0

        def visit(node: _Node, depth: int) -> None:
            nonlocal counter
            for child in node.children:
                if not isinstance(child, _Node):
                    continue
                if child.tag == "table":
                    table = _ParsedTable(child, depth, counter)
                    counter += 1
                    tables.append(table)
                    by_element[id(child)] = table
                visit(child, depth + (1 if child.tag == "table" else 0))

        visit(root, 0)
        if counter != len(ordered):
            # Defensive: both walks must agree on the table count.
            raise ValueError("internal table count mismatch")
        for table in tables:
            table.descendants = self._descendant_tables(table.element)
            table.direct_children = [
                (by_element[id(element)].index, element)
                for element in table.descendants
                if by_element[id(element)].depth == table.depth + 1
            ]
            self._fill_table(table)
        return tables

    @staticmethod
    def _descendant_tables(element: _Node) -> list[_Node]:
        """Return nested table elements (any depth) in document order."""
        found: list[_Node] = []
        queue: list[Any] = list(element.children)
        while queue:
            node = queue.pop(0)
            if not isinstance(node, _Node):
                continue
            if node.tag == "table":
                found.append(node)
                queue = list(node.children) + queue
            else:
                queue = list(node.children) + queue
        return found

    def _fill_table(self, table: _ParsedTable) -> None:
        element = table.element
        table.presentation = element.attrs.get("role", "").strip().lower() == "presentation"
        summary = element.attrs.get("summary")
        table.summary = self._normalize(summary) if summary else None
        row_index = 0
        for child in element.children:
            if not isinstance(child, _Node):
                continue
            if child.tag == "caption" and table.caption is None:
                table.caption = self._subtree_text(child)
            elif child.tag in ("thead", "tbody", "tfoot"):
                section_rows = [kid for kid in child.children if isinstance(kid, _Node) and kid.tag == "tr"]
                for row_element in section_rows:
                    table.rows.append((self._row_cells(row_element), row_index, row_index + len(section_rows) - 1))
                    row_index += 1
            elif child.tag == "tr":
                table.rows.append((self._row_cells(child), row_index, row_index))
                row_index += 1
        if len(table.rows) > self.max_rows_per_table:
            raise ValueError(f"table {table.index} exceeds max_rows_per_table ({self.max_rows_per_table})")

    def _row_cells(self, row_element: _Node) -> list[_Cell]:
        cells: list[_Cell] = []
        for child in row_element.children:
            if isinstance(child, _Node) and child.tag in ("td", "th"):
                cells.append(
                    _Cell(
                        self._subtree_text(child),
                        self._attr_span(child, "rowspan"),
                        self._attr_span(child, "colspan"),
                        child.tag == "th",
                        child,
                    )
                )
        return cells

    @staticmethod
    def _attr_span(cell: _Node, attribute: str) -> int:
        """Parse a span attribute per the rules for non-negative integers."""
        raw = cell.attrs.get(attribute)
        if raw is None:
            return 1
        digits = ""
        for character in raw.strip():
            if character.isdigit():
                digits += character
            else:
                break
        if not digits:
            return 1
        limit = _WHATWG_MAX_ROWSPAN if attribute == "rowspan" else _WHATWG_MAX_COLSPAN
        return min(int(digits), limit)

    def _subtree_text(self, node: _Node) -> str:
        """Normalized text: entities decoded by the parser, script/style dropped.

        Nested tables are skipped (reported as child references, not inlined),
        comments and <br> handling: comments contribute nothing, <br> one space.
        """
        pieces: list[str] = []
        stack: list[Any] = list(reversed(node.children))
        while stack:
            item = stack.pop()
            if isinstance(item, str):
                pieces.append(item)
                continue
            if item.tag in _DROPPED_SUBTREES or item.tag == "table":
                continue
            if item.tag == "br":
                pieces.append(" ")
            stack.extend(reversed(item.children))
        text = "".join(pieces)
        if len(text) > self.max_cell_chars:
            text = text[: self.max_cell_chars]
        return self._normalize(text)

    @staticmethod
    def _normalize(text: str) -> str:
        """Collapse runs of Unicode whitespace (non-breaking spaces included)."""
        return " ".join(text.split())

    @staticmethod
    def _contains(outer: _Node, target: _Node) -> bool:
        stack: list[Any] = list(outer.children)
        while stack:
            item = stack.pop()
            if isinstance(item, _Node):
                if item is target:
                    return True
                stack.extend(item.children)
        return False

    # ------------------------------------------------------------------ #
    # Grid expansion (WHATWG fixed processing semantics: span copies)     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _effective_spans(rows: list[tuple[list[_Cell], int, int]], total_rows: int) -> list[list[tuple[int, int]]]:
        """Resolve declared spans to effective (rowspan, colspan) per cell.

        colspan=0 expands per the historical HTML4 span-to-end rule against the
        width learned in pass one; rowspan=0 spans to the end of its row group;
        rowspans past the last row are clamped to the remaining rows.
        """
        width = 0
        occupied: list[set[int]] = [set() for _ in range(total_rows)]
        for row_index, (cells, _first, section_last) in enumerate(rows):
            cursor = 0
            for cell in cells:
                colspan = max(1, cell.colspan)
                rowspan = cell.rowspan
                if rowspan <= 0:
                    rowspan = max(1, section_last - row_index + 1)
                # The whole footprint must fit without overlapping placed cells.
                while any(slot in occupied[row_index] for slot in range(cursor, cursor + colspan)):
                    cursor += 1
                for delta_y in range(rowspan):
                    target = row_index + delta_y
                    if target < total_rows:
                        occupied[target].update(range(cursor, cursor + colspan))
                cursor += colspan
            width = max(width, cursor)
        resolved: list[list[tuple[int, int]]] = []
        for row_index, (cells, _first, section_last) in enumerate(rows):
            others = sum(cell.colspan for cell in cells if cell.colspan > 0)
            row_spans: list[tuple[int, int]] = []
            for cell in cells:
                colspan = cell.colspan
                if colspan <= 0:
                    colspan = max(1, width - others)
                rowspan = cell.rowspan
                if rowspan <= 0:
                    rowspan = max(1, section_last - row_index + 1)
                rowspan = min(rowspan, total_rows - row_index)
                row_spans.append((rowspan, colspan))
            resolved.append(row_spans)
        return resolved

    def _expand(self, table: _ParsedTable) -> dict[str, Any]:
        rows = table.rows
        total = len(rows)
        spans = self._effective_spans(rows, total)
        occupied: list[set[int]] = [set() for _ in range(total)]
        grid_rows: list[dict[int, str]] = [dict() for _ in range(total)]
        anchors: list[dict[str, int]] = []
        flags = {
            "colspan_zero": [],
            "rowspan_zero": [],
            "rowspan_clamped": [],
        }
        for row_index, (cells, _first, _last) in enumerate(rows):
            cursor = 0
            for position, cell in enumerate(cells):
                rowspan, colspan = spans[row_index][position]
                # The whole footprint must fit without overlapping placed cells.
                while any(slot in occupied[row_index] for slot in range(cursor, cursor + colspan)):
                    cursor += 1
                if cell.colspan <= 0:
                    flags["colspan_zero"].append({"row": row_index, "col": cursor, "expanded_to": colspan})
                if cell.rowspan <= 0:
                    flags["rowspan_zero"].append({"row": row_index, "col": cursor, "expanded_to": rowspan})
                if rowspan < cell.rowspan:
                    flags["rowspan_clamped"].append(
                        {"row": row_index, "col": cursor, "declared": cell.rowspan, "effective": rowspan}
                    )
                for delta_y in range(rowspan):
                    occupied[row_index + delta_y].update(range(cursor, cursor + colspan))
                    # Rowspan fills downward copies, colspan rightward copies.
                    for delta_x in range(colspan):
                        grid_rows[row_index + delta_y][cursor + delta_x] = cell.text
                if table.direct_children:
                    for child_index, child_element in table.direct_children:
                        if self._contains(cell.node, child_element):
                            anchors.append({"index": child_index, "row": row_index, "col": cursor})
                cursor += colspan
        col_count = 0
        for placed in grid_rows:
            if placed:
                col_count = max(col_count, max(placed) + 1)
        grid = [[placed.get(column, "") for column in range(col_count)] for placed in grid_rows]
        extents = [max(placed) + 1 if placed else 0 for placed in grid_rows]
        dom_cells = [len(cells) for cells, _first, _last in rows]
        declared = [
            [
                {"text": cell.text, "rowspan": cell.rowspan, "colspan": cell.colspan}
                for cell in cells
            ]
            for cells, _first, _last in rows
        ]
        header_rows = [
            row_index for row_index, (cells, _first, _last) in enumerate(rows) if any(cell.is_header for cell in cells)
        ]
        return {
            "grid": grid,
            "col_count": col_count,
            "extents": extents,
            "dom_cells": dom_cells,
            "declared": declared,
            "anchors": anchors,
            "header_rows": header_rows,
            **flags,
        }

    # ------------------------------------------------------------------ #
    # Header detection                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _looks_numeric(text: str) -> bool:
        candidate = text.strip()
        if candidate.endswith("%"):
            candidate = candidate[:-1].strip()
        if not candidate:
            return False
        try:
            float(candidate.replace(",", ""))
        except ValueError:
            return False
        return True

    def _detect_headers(self, expansion: dict[str, Any]) -> tuple[list[str] | None, str]:
        grid = expansion["grid"]
        if not grid:
            return None, "none"
        # Trailing padding of the header row (cells the row never reaches) is
        # not part of the header; genuinely empty th cells within it remain.
        first_row = grid[0][: expansion["extents"][0]] if expansion["extents"] else []
        if 0 in expansion["header_rows"]:
            return first_row, "th-elements"
        if len(grid) >= 2 and expansion["extents"][0] == expansion["col_count"]:
            first = first_row
            if first and not any(cell == "" for cell in first):
                lowered = [cell.lower() for cell in first]
                if len(set(lowered)) == len(lowered) and not any(self._looks_numeric(cell) for cell in first):
                    later_numeric = sum(
                        1 for row in grid[1:] if any(cell != "" and self._looks_numeric(cell) for cell in row)
                    )
                    if later_numeric >= max(1, (len(grid) - 1) // 2):
                        return list(grid[0]), "first-row-strong"
        return None, "none"

    # ------------------------------------------------------------------ #
    # Modes                                                               #
    # ------------------------------------------------------------------ #

    def _table_payload(self, table: _ParsedTable, tables: list[_ParsedTable], raw_spans: bool) -> dict[str, Any]:
        expansion = self._expand(table)
        grid = expansion["grid"]
        headers, detection = self._detect_headers(expansion)
        rows = grid[1:] if headers is not None else grid
        irregular = []
        for row_index, extent in enumerate(expansion["extents"]):
            if extent != expansion["col_count"]:
                irregular.append(
                    {
                        "row": row_index,
                        "dom_cells": expansion["dom_cells"][row_index],
                        "expanded_cells": extent,
                        "col_count": expansion["col_count"],
                        "detail": (
                            "missing td/th per DOM"
                            if extent < expansion["col_count"]
                            else "more cells than col_count after expansion"
                        ),
                    }
                )
        child_tables = [
            {"index": anchor["index"], "row": anchor["row"], "col": anchor["col"],
             "depth": tables[anchor["index"]].depth}
            for anchor in expansion["anchors"]
        ]
        child_tables.sort(key=lambda entry: entry["index"])
        payload: dict[str, Any] = {
            "index": table.index,
            "depth": table.depth,
            "caption": table.caption,
            "summary": table.summary,
            "presentation": table.presentation,
            "headers": headers,
            "header_detection": detection,
            "rows": rows,
            "row_count": len(rows),
            "col_count": expansion["col_count"],
            "irregular_rows": irregular,
            "child_tables": child_tables,
        }
        deeper = sum(1 for element in table.descendants if self._depth_of(tables, element) > self.max_table_depth)
        if deeper:
            payload["truncated_child_tables"] = deeper
        if raw_spans:
            payload["raw_spans"] = expansion["declared"]
        return payload

    def _depth_of(self, tables: list[_ParsedTable], element: _Node) -> int:
        current = element.parent
        depth = 0
        while current is not None:
            if isinstance(current, _Node) and current.tag == "table":
                depth += 1
            current = current.parent
        return depth

    def _checked_index(self, tables: list[_ParsedTable], table_index: Any, label: str) -> int:
        if isinstance(table_index, bool) or not isinstance(table_index, int):
            raise ValueError(f"{label} must be an integer")
        if not 0 <= table_index < len(tables):
            bound = f"0..{len(tables) - 1}" if tables else "empty document"
            raise ValueError(f"{label} {table_index} out of range ({bound})")
        if tables[table_index].depth > self.max_table_depth:
            raise ValueError(
                f"table {table_index} nesting depth {tables[table_index].depth} exceeds max_table_depth "
                f"({self.max_table_depth})"
            )
        return table_index

    def _extract(self, tables: list[_ParsedTable], table_index: Any, raw_spans: bool) -> dict[str, Any]:
        if table_index:
            index = self._checked_index(tables, table_index, "table_index")
            return {
                "status": "success",
                "mode": "extract",
                "table_count": 1,
                "tables": [self._table_payload(tables[index], tables, raw_spans)],
            }
        payloads = [self._table_payload(table, tables, raw_spans) for table in tables if table.depth == 0]
        return {"status": "success", "mode": "extract", "table_count": len(payloads), "tables": payloads}

    def _analyze(self, tables: list[_ParsedTable]) -> dict[str, Any]:
        reports = []
        for table in tables:
            if table.depth != 0:
                continue
            expansion = self._expand(table)
            payload = self._table_payload(table, tables, False)
            findings: list[dict[str, Any]] = []
            if not any(isinstance(child, _Node) and child.tag == "tbody" for child in table.element.children):
                findings.append(
                    {"level": "info", "code": "no_tbody", "detail": "no tbody section; rows read in document order"}
                )
            if table.presentation:
                findings.append(
                    {
                        "level": "info",
                        "code": "presentation_role",
                        "detail": "role=presentation layout table, not a data table",
                    }
                )
            scattered = [row for row in expansion["header_rows"] if row != 0]
            if scattered:
                findings.append(
                    {
                        "level": "warning",
                        "code": "scattered_th",
                        "detail": "th cells outside the first row",
                        "rows": scattered,
                    }
                )
            if expansion["colspan_zero"]:
                findings.append(
                    {
                        "level": "warning",
                        "code": "colspan_zero",
                        "detail": "colspan=0 expanded per the historical HTML4 span-to-end rule",
                        "cells": expansion["colspan_zero"],
                    }
                )
            if expansion["rowspan_zero"]:
                findings.append(
                    {
                        "level": "info",
                        "code": "rowspan_zero",
                        "detail": "rowspan=0 expanded to the end of its row group per the HTML Standard",
                        "cells": expansion["rowspan_zero"],
                    }
                )
            if expansion["rowspan_clamped"]:
                findings.append(
                    {
                        "level": "warning",
                        "code": "rowspan_clamped",
                        "detail": "rowspan exceeds the remaining rows; clamped",
                        "cells": expansion["rowspan_clamped"],
                    }
                )
            headers = payload["headers"]
            if headers is not None:
                empty_positions = [position for position, name in enumerate(headers) if name == ""]
                if empty_positions:
                    findings.append(
                        {
                            "level": "warning",
                            "code": "empty_header_cells",
                            "detail": "empty header cells",
                            "positions": empty_positions,
                        }
                    )
                seen: dict[str, int] = {}
                for name in headers:
                    seen[name] = seen.get(name, 0) + 1
                duplicates = sorted(name for name, count in seen.items() if count > 1)
                if duplicates:
                    findings.append(
                        {
                            "level": "warning",
                            "code": "duplicate_headers",
                            "detail": "duplicate header names",
                            "names": duplicates,
                        }
                    )
            drift = [
                {"row": row, "dom_cells": expansion["dom_cells"][row], "expanded_cells": expansion["extents"][row]}
                for row in range(len(expansion["grid"]))
                if expansion["extents"][row] != expansion["col_count"]
            ]
            if drift:
                findings.append(
                    {
                        "level": "warning",
                        "code": "row_cell_count_drift",
                        "detail": "expanded row width differs from col_count",
                        "rows": drift,
                    }
                )
            if not expansion["grid"]:
                findings.append({"level": "warning", "code": "zero_rows", "detail": "table has no rows"})
            nested_depth = 0
            for element in table.descendants:
                nested_depth = max(nested_depth, self._depth_of(tables, element) - table.depth)
            reports.append(
                {
                    "index": table.index,
                    "caption": table.caption,
                    "summary": table.summary,
                    "presentation": table.presentation,
                    "row_count": payload["row_count"],
                    "col_count": payload["col_count"],
                    "headers": headers,
                    "header_detection": payload["header_detection"],
                    "nested_table_depth": nested_depth,
                    "findings": findings,
                }
            )
        return {"status": "success", "mode": "analyze", "table_count": len(reports), "tables": reports}

    def _to_csv(self, tables: list[_ParsedTable], table_index: Any) -> dict[str, Any]:
        index = self._checked_index(tables, table_index, "table_index")
        payload = self._table_payload(tables[index], tables, False)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        if payload["headers"] is not None:
            writer.writerow(payload["headers"])
        for row in payload["rows"]:
            writer.writerow(row)
        return {
            "status": "success",
            "mode": "to_csv",
            "table_index": index,
            "csv": buffer.getvalue(),
            "header_count": len(payload["headers"]) if payload["headers"] is not None else 0,
            "row_count": payload["row_count"],
            "col_count": payload["col_count"],
        }

    def _grid_from_html(self, html: Any, table_index: int, label: str) -> dict[str, Any]:
        if not isinstance(html, str) or not html:
            raise ValueError(f"{label} must be a non-empty html string (or pass table_a/table_b structures)")
        tables = self._collect(html)
        index = self._checked_index(tables, table_index, "table_index")
        payload = self._table_payload(tables[index], tables, False)
        return {"headers": payload["headers"], "rows": payload["rows"], "col_count": payload["col_count"]}

    def _compare(
        self,
        html: str | None,
        html2: str | None,
        table_index: int,
        table_index2: int,
        table_a: dict[str, Any] | None,
        table_b: dict[str, Any] | None,
    ) -> dict[str, Any]:
        left = table_a if table_a is not None else self._grid_from_html(html, table_index, "html")
        right = table_b if table_b is not None else self._grid_from_html(html2, table_index2, "html2")
        for structure, label in ((left, "table_a"), (right, "table_b")):
            if not isinstance(structure, dict) or not isinstance(structure.get("rows"), list):
                raise ValueError(f"{label} must be an extract-mode table structure with a rows list")
        headers_a = list(left.get("headers") or [])
        headers_b = list(right.get("headers") or [])
        rows_a = [list(row) for row in left["rows"]]
        rows_b = [list(row) for row in right["rows"]]
        col_a = left.get("col_count") or max((len(row) for row in rows_a), default=0)
        col_b = right.get("col_count") or max((len(row) for row in rows_b), default=0)
        width = max(col_a, col_b)
        header_changes = []
        for position in range(min(len(headers_a), len(headers_b))):
            if headers_a[position] != headers_b[position]:
                header_changes.append(
                    {"position": position, "a": headers_a[position], "b": headers_b[position]}
                )
        added_headers = [
            {"position": position, "value": headers_b[position]}
            for position in range(len(headers_a), len(headers_b))
        ]
        removed_headers = [
            {"position": position, "value": headers_a[position]}
            for position in range(len(headers_b), len(headers_a))
        ]
        common_rows = min(len(rows_a), len(rows_b))
        added_rows = list(range(common_rows, len(rows_b)))
        removed_rows = list(range(common_rows, len(rows_a)))
        changed_cells = []
        truncated = False
        for row in range(common_rows):
            left_row = rows_a[row] + [""] * (width - len(rows_a[row]))
            right_row = rows_b[row] + [""] * (width - len(rows_b[row]))
            for column in range(width):
                if left_row[column] != right_row[column]:
                    if len(changed_cells) >= self.max_changed_cells:
                        truncated = True
                        break
                    changed_cells.append({"row": row, "col": column, "a": left_row[column], "b": right_row[column]})
            if truncated:
                break
        same = not (header_changes or added_headers or removed_headers or added_rows or removed_rows
                    or changed_cells or col_a != col_b)
        result: dict[str, Any] = {
            "status": "success",
            "mode": "compare",
            "same": same,
            "a": {"row_count": len(rows_a), "col_count": col_a, "headers": headers_a},
            "b": {"row_count": len(rows_b), "col_count": col_b, "headers": headers_b},
            "header_changes": header_changes,
            "added_headers": added_headers,
            "removed_headers": removed_headers,
            "added_rows": added_rows,
            "removed_rows": removed_rows,
            "added_cols": max(0, col_b - col_a),
            "removed_cols": max(0, col_a - col_b),
            "changed_cells": changed_cells,
        }
        if truncated:
            result["changed_cells_truncated"] = True
        return result
