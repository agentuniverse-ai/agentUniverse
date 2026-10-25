"""Offline unit tests for HtmlTableTool.

Oracle strategy (lxml is installed in the test venv only; the tool itself is
stdlib-only):

(a) Extraction parity: 300 seeded HTML tables with random spans (including
    rowspan=0 in sections and stray-row runs, colspan=0, spans colliding on
    the same cell), duplicate attributes, invalid non-ASCII span digits,
    headers, nesting, empty cells, entities (incl. &#x1F600; and invalid
    numeric refs), <br>, block elements, captions (incl. nested markup),
    colgroups (incl. col span pre-allocation), cell attributes and
    thead/tbody/tfoot mixes in document order. The tool's expanded grid must equal an
    INDEPENDENT lxml.etree-based expansion implemented below. Both
    implementations walk the same DOM semantics through different code paths
    (tool: html.parser + occupied-set cursor; reference: lxml.etree + dense
    matrix with a free-footprint scan), so agreement proves the span math.
(b) Hand-computed ground truths for the classic span patterns.
(c) Cell text parity on 200 tables against an independent lxml traversal
    implementing the documented text rules (entities decoded, script/style
    dropped, nested tables skipped, <br> -> one space, Unicode whitespace
    collapsed); plain tables are additionally pinned against raw
    lxml ``itertext()``.
(d) to_csv round-trips: parsing the CSV back yields the expanded rows.
(e) No browser is used: the expansion semantics follow the WHATWG HTML
    Standard section 4.9.13 "Forming a table" processing model, hand-embedded
    as the fixed expected grids in (b).
(f) Pathological inputs stay bounded and fast.
"""

import csv
import io
import json
import os
import random
import time
import unittest

from lxml import etree

from agentuniverse.agent.action.tool.common_tool import html_table_tool as html_table_module
from agentuniverse.agent.action.tool.common_tool.html_table_tool import HtmlTableTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(html_table_module.__file__), "html_table_tool.yaml")

WORDS = ["alpha", "beta", "gamma", "delta", "omega", "zeta", "sigma", "kappa", "north", "south"]
ENTITY_SAMPLES = [
    "A&amp;B", "x&lt;y", "y&gt;x", "&#233;cole", "caf&eacute;", "a&nbsp;b",
    "&quot;q&quot;", "&#39;edge&#39;", "tab&#9;char", "mix&amp;mix",
    "&#x1F600;grin", "&#0;null", "&#x110000;over", "&#xD800;sur", "&#38;#60;esc",
]
BLOCK_SAMPLES = ["<div>blk %d</div>", "<p>para %d</p>", "<span>sp %d</span>"]
CELL_ATTR_SAMPLES = [' class="c%d"', ' title="t%d"', ' style="color:red"', ' data-x="v%d"']


# --------------------------------------------------------------------------- #
# Independent lxml.etree-based reference implementation                        #
# --------------------------------------------------------------------------- #


def _ref_parse(html_text):
    parser = etree.HTMLParser(recover=False)
    root = etree.fromstring(html_text, parser=parser)
    return root


def _ref_normalize(text):
    return " ".join(text.split())


def _ref_cell_text(element):
    """Documented text rules via an independent lxml traversal."""
    parts = []

    def visit(element):
        tag = element.tag if isinstance(element.tag, str) else ""
        if tag == "br":
            parts.append(" ")
        if tag not in ("script", "style") and element.text:
            parts.append(element.text)
        for child in element:
            if isinstance(child.tag, str) and child.tag not in ("script", "style", "table"):
                visit(child)
            if child.tail:
                parts.append(child.tail)

    visit(element)
    return _ref_normalize("".join(parts))


def _ref_span(element, attribute):
    raw = element.get(attribute)
    if raw is None:
        return 1
    digits = ""
    for character in raw.strip():
        if character in "0123456789":  # WHATWG non-negative integers: ASCII digits only
            digits += character
        else:
            break
    return min(int(digits), 65534 if attribute == "rowspan" else 1000) if digits else 1


def _ref_tables(root):
    """Return document-order (table_element, depth) pairs; top-level depth 0."""
    result = []

    def visit(element, depth):
        for child in element:
            if not isinstance(child.tag, str):
                continue
            if child.tag == "table":
                result.append((child, depth))
                visit(child, depth + 1)
            else:
                visit(child, depth)

    visit(root, 0)
    return result


def _ref_rows(table_element):
    """Rows in document order; each entry is a list of cell dicts."""
    rows = []
    for child in table_element:
        if not isinstance(child.tag, str):
            continue
        if child.tag == "tr":
            rows.append(_ref_row_cells(child))
        elif child.tag in ("thead", "tbody", "tfoot"):
            for tr in child:
                if isinstance(tr.tag, str) and tr.tag == "tr":
                    rows.append(_ref_row_cells(tr))
    return rows


def _ref_row_cells(tr):
    cells = []
    for child in tr:
        if isinstance(child.tag, str) and child.tag in ("td", "th"):
            cells.append(
                {
                    "text": _ref_cell_text(child),
                    "rowspan": _ref_span(child, "rowspan"),
                    "colspan": _ref_span(child, "colspan"),
                    "is_header": child.tag == "th",
                    "element": child,
                }
            )
    return cells


def _ref_place(rows, colspan_zero_width):
    """Dense-matrix placement: cursor floor plus free-footprint scan.

    Cells are slotted left to right in document order (the cursor never moves
    backward within a row, matching the WHATWG forming-a-table model), and a
    cell lands at the first cursor position whose whole footprint is free.
    """
    total = len(rows)
    grid: list[list[str | None]] = []
    cursors = [0] * total

    def grow(y, x):
        while len(grid) <= y:
            grid.append([])
        for row in grid:
            while len(row) <= x:
                row.append(None)

    def free(y, x, rowspan, colspan):
        for yy in range(y, y + rowspan):
            if yy >= len(grid):
                continue
            row = grid[yy]
            for xx in range(x, x + colspan):
                if xx < len(row) and row[xx] is not None:
                    return False
        return True

    for y, cells in enumerate(rows):
        for cell in cells:
            colspan = cell["colspan"]
            if colspan <= 0:
                others = sum(other["colspan"] for other in cells if other["colspan"] > 0)
                colspan = max(1, colspan_zero_width - others)
            rowspan = min(max(1, cell["rowspan"]), total - y)
            x = cursors[y]
            while not free(y, x, rowspan, colspan):
                x += 1
            for yy in range(y, y + rowspan):
                grow(yy, x + colspan - 1)
                for xx in range(x, x + colspan):
                    grid[yy][xx] = cell["text"]
            cursors[y] = x + colspan
            cell.setdefault("origin", (y, x))
    extents = [
        max((index for index, value in enumerate(row) if value is not None), default=-1) + 1 for row in grid
    ]
    return grid, extents


def _ref_extract_table(table_element, depth):  # noqa: C901
    """Full independent extraction of one table element."""
    raw_rows = _ref_rows(table_element)
    total = len(raw_rows)
    # Rewrite rowspan=0 to the end of its row group per the HTML Standard:
    # thead/tbody/tfoot sections are groups, and a maximal run of consecutive
    # stray tr children forms one implicit group (implicit tbody).
    section_last = {}
    index = 0
    run_start = None
    for child in table_element:
        if not isinstance(child.tag, str):
            continue
        if child.tag == "tr":
            if run_start is None:
                run_start = index
            section_last[index] = None
            index += 1
            continue
        if run_start is not None:
            for i in range(run_start, index):
                section_last[i] = index - 1
            run_start = None
        if child.tag in ("thead", "tbody", "tfoot"):
            count = sum(1 for tr in child if isinstance(tr.tag, str) and tr.tag == "tr")
            for i in range(index, index + count):
                section_last[i] = index + count - 1
            index += count
    if run_start is not None:
        for i in range(run_start, index):
            section_last[i] = index - 1
    prepared = []
    for y, cells in enumerate(raw_rows):
        prepared_row = []
        for cell in cells:
            rowspan = cell["rowspan"]
            if rowspan == 0:
                rowspan = max(1, section_last.get(y, total - 1) - y + 1)
            prepared_row.append({**cell, "rowspan": rowspan})
        prepared.append(prepared_row)

    pass_one, _extents = _ref_place([[{**cell} for cell in cells] for cells in prepared], 0)
    width = max((len(row) for row in pass_one), default=0)
    grid_raw, extents = _ref_place(prepared, width)
    final_width = max((len(row) for row in grid_raw), default=0)
    grid = [[(value or "") for value in (row + [None] * (final_width - len(row)))] for row in grid_raw]
    caption = None
    for child in table_element:
        if isinstance(child.tag, str) and child.tag == "caption":
            caption = _ref_cell_text(child)
            break
    return {
        "grid": grid,
        "extents": extents,
        "rows": prepared,
        "width": final_width,
        "depth": depth,
        "caption": caption,
        "element": table_element,
    }


def _ref_headers(item):
    grid, extents, rows = item["grid"], item["extents"], item["rows"]
    if not grid:
        return None, "none"
    first_row = grid[0][: extents[0]] if extents else []
    if rows and any(cell["is_header"] for cell in rows[0]):
        return first_row, "th-elements"
    if len(grid) >= 2 and extents[0] == item["width"]:
        first = [cell.lower() for cell in first_row]
        if first_row and "" not in first_row and len(set(first)) == len(first) and not any(
            _ref_numeric(cell) for cell in first_row
        ):
            later = sum(1 for row in grid[1:] if any(cell != "" and _ref_numeric(cell) for cell in row))
            if later >= max(1, (len(grid) - 1) // 2):
                return first_row, "first-row-strong"
    return None, "none"


def _ref_numeric(text):
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


def _ref_extract(html_text):
    """Independent full-document extraction mirroring the tool's contract."""
    root = _ref_parse(html_text)
    tables = _ref_tables(root)
    extracted = [_ref_extract_table(element, depth) for element, depth in tables]
    results = []
    for position, item in enumerate(extracted):
        headers, detection = _ref_headers(item)
        child_refs = []
        for other_position, (element, depth) in enumerate(tables):
            if depth != item["depth"] + 1:
                continue
            for y, cells in enumerate(item["rows"]):
                for cell in cells:
                    if any(descendant is element for descendant in cell["element"].iter("table")):
                        child_refs.append(
                            {
                                "index": other_position,
                                "row": y,
                                "col": cell.get("origin", (0, 0))[1],
                                "depth": depth,
                            }
                        )
        results.append(
            {
                "index": position,
                "depth": item["depth"],
                "caption": item["caption"],
                "headers": headers,
                "header_detection": detection,
                "rows": item["grid"][1:] if headers is not None else item["grid"],
                "col_count": item["width"],
                "child_tables": sorted(child_refs, key=lambda entry: entry["index"]),
            }
        )
    return results, extracted


# --------------------------------------------------------------------------- #
# Seeded corpus generator (shared spec -> html rendered once for both sides)   #
# --------------------------------------------------------------------------- #


def _gen_cell_text(rng, allow_br):
    if rng.random() < 0.12:
        return ""
    text = " ".join(rng.choice(WORDS) for _ in range(rng.randint(1, 3)))
    if rng.random() < 0.45:
        text = rng.choice(ENTITY_SAMPLES)
    if rng.random() < 0.12:
        text = rng.choice(BLOCK_SAMPLES) % rng.randint(0, 9) + text
    if rng.random() < 0.08:
        text = text + ' "q, %s";' % rng.choice(WORDS)
    if allow_br and rng.random() < 0.25:
        text = text + "<br>" + rng.choice(WORDS)
    return text


def _gen_inner(rng, allow_br):
    inner = _gen_cell_text(rng, allow_br)
    extras = ""
    if rng.random() < 0.1:
        extras += "<script>var x = 'ignored';</script>"
    if rng.random() < 0.1:
        extras += "<style>.a{color:red}</style>"
    if rng.random() < 0.1:
        extras += "<!-- comment -->"
    return inner + extras


def _gen_table(rng, depth=0):  # noqa: C901
    columns = rng.randint(1, 7)
    row_count = rng.randint(1, 10)
    style = rng.choice(["th", "none", "scattered", "first-row"])
    parts = ["<table"]
    if rng.random() < 0.35:
        parts.append(' summary="sum %d"' % rng.randint(1, 9))
    if rng.random() < 0.1:
        parts.append(' role="presentation"')
    parts.append(">")
    if rng.random() < 0.4:
        parts.append("<caption>Cap&amp;tion %d</caption>" % rng.randint(1, 9))
    if rng.random() < 0.15:
        parts.append(f"<caption><b>Nested</b> <i>cap {rng.randint(1, 9)}</i></caption>")
    if rng.random() < 0.3:
        parts.append("<colgroup>" + "<col>" * columns + "</colgroup>")
    if rng.random() < 0.15:  # col span pre-allocation: extractors ignore it
        parts.append(f'<colgroup><col span="{rng.randint(1, 3)}">' + "<col>" * rng.randint(0, 2) + "</colgroup>")
    layout = rng.choice(["none", "sections", "tfoot_first", "two_tbody", "stray_mixed", "thead_late"])
    body_rows = []
    for row_index in range(row_count):
        cells = []
        for _ in range(rng.randint(1, max(1, columns))):
            attributes = ""
            if rng.random() < 0.10:
                pick = rng.choice(CELL_ATTR_SAMPLES)
                attributes += pick % rng.randint(0, 9) if "%d" in pick else pick
            if rng.random() < 0.04:  # duplicate attribute: the first occurrence wins
                attributes += f' colspan="{rng.randint(1, 3)}" colspan="0"'
            elif rng.random() < 0.30:
                attributes += ' colspan="%d"' % rng.randint(1, 3)
            elif rng.random() < 0.05:
                attributes += ' colspan="0"'
            if rng.random() < 0.04:  # non-ASCII digits: invalid, span defaults to 1
                attributes += f' rowspan="{rng.choice(["²", "１２", "٣"])}"'  # noqa: RUF001
            elif rng.random() < 0.30:
                attributes += ' rowspan="%d"' % rng.randint(1, 4)
            elif rng.random() < 0.05:
                attributes += ' rowspan="0"'
            if style == "th" and row_index == 0:
                tag = "th"
            elif style == "scattered" and row_index == 1 and rng.random() < 0.5:
                tag = "th"
            else:
                tag = "td"
            cells.append("<%s%s>%s</%s>" % (tag, attributes, _gen_inner(rng, allow_br=True), tag))
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    if style == "first-row":
        body_rows[0] = "<tr><th>Name</th><th>Amount</th></tr>" if columns >= 2 else "<tr><th>Name</th></tr>"
        for replacement in range(1, len(body_rows)):
            body_rows[replacement] = "<tr><td>item %d</td><td>%d</td></tr>" % (replacement, replacement)
    if layout == "sections" and row_count >= 2:
        split = max(1, len(body_rows) - 1)
        parts.append("<thead>" + body_rows[0] + "</thead>")
        if len(body_rows) > 1:
            parts.append("<tbody>" + "".join(body_rows[1:split]) + "".join(body_rows[split:]) + "</tbody>")
    elif layout == "tfoot_first" and row_count >= 2:
        parts.append("<tfoot>" + body_rows[0] + "</tfoot><tbody>" + "".join(body_rows[1:]) + "</tbody>")
    elif layout == "two_tbody" and row_count >= 3:
        split = rng.randint(1, len(body_rows) - 2)
        parts.append("<tbody>" + "".join(body_rows[:split]) + "</tbody><tbody>" + "".join(body_rows[split:]) + "</tbody>")
    elif layout == "stray_mixed" and row_count >= 3:
        split = rng.randint(1, len(body_rows) - 1)
        parts.extend(body_rows[:split])
        parts.append("<tbody>" + "".join(body_rows[split:]) + "</tbody>")
    elif layout == "thead_late" and row_count >= 2:
        parts.append("<tbody>" + "".join(body_rows[1:]) + "</tbody><thead>" + body_rows[0] + "</thead>")
    else:
        parts.extend(body_rows)
    if depth < 2 and rng.random() < 0.22:
        nested = _gen_table(rng, depth + 1)
        parts.append("<tr><td>outer %s<table>%s</table> tail</td></tr>" % (_gen_inner(rng, False), nested))
    parts.append("</table>")
    separator = "\n  " if rng.random() < 0.5 else " "
    return separator.join(parts)


def _gen_document(seed, count):
    rng = random.Random(seed)
    tables = [_gen_table(rng) for _ in range(count)]
    chunks = []
    for table in tables:
        wrapper = rng.choice(["div", "section", "plain"])
        if wrapper == "div":
            chunks.append('<div><p>para %d</p>%s</div>' % (rng.randint(1, 99), table))
        elif wrapper == "section":
            chunks.append("<section>%s</section>" % table)
        else:
            chunks.append(table)
    return "<html><body>" + "\n".join(chunks) + "</body></html>"


# --------------------------------------------------------------------------- #
# Unit tests                                                                   #
# --------------------------------------------------------------------------- #


class HtmlTableToolParityTest(unittest.TestCase):
    """Oracle parity: the tool grid equals the independent lxml expansion."""

    def test_seeded_extraction_parity_300(self):
        """300 seeded tables: grids, headers, captions and child refs agree."""
        for seed in range(300):
            with self.subTest(seed=seed):
                document = _gen_document(seed, 3)
                result = HtmlTableTool().execute(mode="extract", html=document)
                self.assertEqual(result["status"], "success", result.get("error"))
                reference, _extracted = _ref_extract(document)
                top_level = [entry for entry in reference if entry["depth"] == 0]
                self.assertEqual(result["table_count"], len(top_level))
                for payload, expected in zip(result["tables"], top_level):
                    self.assertEqual(
                        payload["rows"], expected["rows"], f"rows differ (seed {seed}, table {payload['index']})"
                    )
                    self.assertEqual(payload["col_count"], expected["col_count"])
                    self.assertEqual(payload["headers"], expected["headers"])
                    self.assertEqual(payload["header_detection"], expected["header_detection"])
                    self.assertEqual(payload["caption"], expected["caption"])
                    self.assertEqual(payload["child_tables"], expected["child_tables"])

    def test_seeded_text_parity_200(self):
        """200 seeded tables: cell text matches the lxml text rules."""
        for seed in range(1000, 1200):
            with self.subTest(seed=seed):
                document = _gen_document(seed, 2)
                result = HtmlTableTool().execute(mode="extract", html=document)
                self.assertEqual(result["status"], "success", result.get("error"))
                root = _ref_parse(document)
                reference, extracted = _ref_extract(document)
                tool_cells = [cell for payload in result["tables"] for row in payload["rows"] for cell in row]
                reference_cells = [
                    cell
                    for entry, item in zip(reference, extracted)
                    if entry["depth"] == 0
                    for row in entry["rows"]
                    for cell in row
                ]
                self.assertEqual(tool_cells, reference_cells)
                # Pin the documented text rules to the raw lxml primitive on
                # plain cells (no br/script/style/comments/nesting involved).
                plain = (
                    "<script" not in document
                    and "<style" not in document
                    and "<br>" not in document
                    and "<!--" not in document
                    and all(not entry["child_tables"] for entry in reference)
                )
                if plain:
                    for item in extracted:
                        if item["depth"] != 0:
                            continue
                        for row in item["rows"]:
                            for cell in row:
                                itertext = _ref_normalize("".join(cell["element"].itertext()))
                                self.assertEqual(cell["text"], itertext)

    def test_deterministic_output(self):
        """Same input twice yields byte-identical structure."""
        document = _gen_document(4242, 4)
        first = HtmlTableTool().execute(mode="extract", html=document)
        second = HtmlTableTool().execute(mode="extract", html=document)
        self.assertEqual(first, second)


class HtmlTableToolGroundTruthTest(unittest.TestCase):
    """Hand-computed ground truths for the classic span patterns (WHATWG 4.9.13)."""

    def setUp(self):
        self.tool = HtmlTableTool()

    def rows(self, html, index=None):
        result = self.tool.execute(mode="extract", html=html, table_index=index or 0)
        self.assertEqual(result["status"], "success", result.get("error"))
        return result["tables"][0]

    def test_simple_2x2(self):
        table = self.rows("<table><tr><td>a</td><td>b</td></tr><tr><td>c</td><td>d</td></tr></table>")
        self.assertEqual(table["rows"], [["a", "b"], ["c", "d"]])
        self.assertEqual(table["col_count"], 2)
        self.assertIsNone(table["headers"])
        self.assertEqual(table["header_detection"], "none")

    def test_rowspan_basic(self):
        table = self.rows("<table><tr><td rowspan=2>A</td><td>B</td></tr><tr><td>C</td></tr></table>")
        self.assertEqual(table["rows"], [["A", "B"], ["A", "C"]])

    def test_colspan_basic(self):
        table = self.rows("<table><tr><td colspan=2>A</td></tr><tr><td>1</td><td>2</td></tr></table>")
        self.assertEqual(table["rows"], [["A", "A"], ["1", "2"]])

    def test_rowspan_colspan_overlap_ordering(self):
        html = (
            "<table><tr><td rowspan=2 colspan=2>A</td><td>B</td></tr>"
            "<tr><td>C</td></tr><tr><td>1</td><td>2</td><td>3</td></tr></table>"
        )
        table = self.rows(html)
        self.assertEqual(table["rows"], [["A", "A", "B"], ["A", "A", "C"], ["1", "2", "3"]])

    def test_rowspan_past_end_clamped(self):
        html = "<table><tr><td rowspan=5>A</td><td>B</td></tr><tr><td>C</td></tr></table>"
        table = self.rows(html)
        self.assertEqual(table["rows"], [["A", "B"], ["A", "C"]])
        analysis = self.tool.execute(mode="analyze", html=html)
        codes = {finding["code"] for finding in analysis["tables"][0]["findings"]}
        self.assertIn("rowspan_clamped", codes)
        clamped = [f for f in analysis["tables"][0]["findings"] if f["code"] == "rowspan_clamped"][0]
        self.assertEqual(clamped["cells"], [{"row": 0, "col": 0, "declared": 5, "effective": 2}])

    def test_colspan_zero_historical(self):
        html = (
            "<table><tr><td colspan=0>A</td><td>B</td></tr>"
            "<tr><td>1</td><td>2</td><td>3</td></tr></table>"
        )
        table = self.rows(html)
        self.assertEqual(table["rows"], [["A", "A", "B"], ["1", "2", "3"]])
        analysis = self.tool.execute(mode="analyze", html=html)
        codes = {finding["code"] for finding in analysis["tables"][0]["findings"]}
        self.assertIn("colspan_zero", codes)

    def test_rowspan_zero_row_group(self):
        html = (
            "<table><tbody><tr><td rowspan=0>A</td><td>B</td></tr><tr><td>C</td></tr></tbody>"
            "<tbody><tr><td>x</td><td>y</td></tr></tbody></table>"
        )
        table = self.rows(html)
        self.assertEqual(table["rows"], [["A", "B"], ["A", "C"], ["x", "y"]])

    def test_overlapping_spans_grow_width(self):
        html = "<table><tr><td rowspan=2>A</td><td>B</td></tr><tr><td colspan=2>C</td></tr></table>"
        table = self.rows(html)
        self.assertEqual(table["rows"], [["A", "B", ""], ["A", "C", "C"]])
        self.assertEqual(table["col_count"], 3)

    def test_th_headers(self):
        table = self.rows("<table><tr><th>H1</th><th>H2</th></tr><tr><td>1</td><td>2</td></tr></table>")
        self.assertEqual(table["headers"], ["H1", "H2"])
        self.assertEqual(table["header_detection"], "th-elements")
        self.assertEqual(table["rows"], [["1", "2"]])

    def test_first_row_strong_detection(self):
        html = (
            "<table><tr><td>Name</td><td>Qty</td></tr>"
            "<tr><td>apple</td><td>3</td></tr><tr><td>pear</td><td>4</td></tr></table>"
        )
        table = self.rows(html)
        self.assertEqual(table["headers"], ["Name", "Qty"])
        self.assertEqual(table["header_detection"], "first-row-strong")

    def test_numeric_first_row_is_not_header(self):
        table = self.rows("<table><tr><td>1</td><td>2</td></tr><tr><td>3</td><td>4</td></tr></table>")
        self.assertIsNone(table["headers"])
        self.assertEqual(table["rows"], [["1", "2"], ["3", "4"]])

    def test_empty_and_duplicate_headers_flagged(self):
        html = "<table><tr><th>H</th><th></th><th>H</th></tr><tr><td>1</td><td>2</td><td>3</td></tr></table>"
        analysis = self.tool.execute(mode="analyze", html=html)
        codes = {finding["code"] for finding in analysis["tables"][0]["findings"]}
        self.assertIn("empty_header_cells", codes)
        self.assertIn("duplicate_headers", codes)

    def test_scattered_th_flagged(self):
        html = "<table><tr><td>a</td></tr><tr><th>late</th></tr></table>"
        analysis = self.tool.execute(mode="analyze", html=html)
        scattered = [f for f in analysis["tables"][0]["findings"] if f["code"] == "scattered_th"][0]
        self.assertEqual(scattered["rows"], [1])

    def test_caption_and_summary(self):
        html = '<table summary="fin"><caption>Q1 &amp; Q2</caption><tr><td>1</td></tr></table>'
        table = self.rows(html)
        self.assertEqual(table["caption"], "Q1 & Q2")
        self.assertEqual(table["summary"], "fin")

    def test_presentation_role(self):
        html = '<table role="presentation"><tr><td>lay</td><td>out</td></tr></table>'
        analysis = self.tool.execute(mode="analyze", html=html)
        codes = {finding["code"] for finding in analysis["tables"][0]["findings"]}
        self.assertIn("presentation_role", codes)

    def test_no_tbody_info(self):
        analysis = self.tool.execute(mode="analyze", html="<table><tr><td>a</td></tr></table>")
        codes = {finding["code"] for finding in analysis["tables"][0]["findings"]}
        self.assertIn("no_tbody", codes)
        analysis = self.tool.execute(mode="analyze", html="<table><tbody><tr><td>a</td></tr></tbody></table>")
        codes = {finding["code"] for finding in analysis["tables"][0]["findings"]}
        self.assertNotIn("no_tbody", codes)

    def test_zero_rows(self):
        table = self.rows("<table><caption>empty</caption></table>")
        self.assertEqual(table["rows"], [])
        self.assertEqual(table["row_count"], 0)
        analysis = self.tool.execute(mode="analyze", html="<table></table>")
        codes = {finding["code"] for finding in analysis["tables"][0]["findings"]}
        self.assertIn("zero_rows", codes)

    def test_nested_table_child_ref(self):
        html = "<table><tr><td>before <table><tr><td>in</td></tr></table> after</td><td>side</td></tr></table>"
        table = self.rows(html)
        # Nested tables are not inlined: surrounding cell text is kept and the
        # table is reported as a child reference anchored at its cell.
        self.assertEqual(table["rows"], [["before after", "side"]])
        self.assertEqual(table["child_tables"], [{"index": 1, "row": 0, "col": 0, "depth": 1}])
        nested = self.rows(html, index=1)
        self.assertEqual(nested["rows"], [["in"]])
        self.assertEqual(nested["depth"], 1)
        tight = self.rows("<table><tr><td>x<table><tr><td>in</td></tr></table>y</td></tr></table>")
        self.assertEqual(tight["rows"], [["xy"]])

    def test_irregular_rows_reported(self):
        html = "<table><tr><td>a</td><td>b</td></tr><tr><td>c</td></tr></table>"
        table = self.rows(html)
        self.assertEqual(table["irregular_rows"], [
            {"row": 1, "dom_cells": 1, "expanded_cells": 1, "col_count": 2, "detail": "missing td/th per DOM"}
        ])
        self.assertEqual(table["rows"], [["a", "b"], ["c", ""]])

    def test_thead_tbody_tfoot_document_order(self):
        html = (
            "<table>"
            "<thead><tr><th>H</th></tr></thead>"
            "<tbody><tr><td>b1</td></tr></tbody>"
            "<tfoot><tr><td>f1</td></tr></tfoot>"
            "</table>"
        )
        table = self.rows(html)
        self.assertEqual(table["rows"], [["b1"], ["f1"]])
        self.assertEqual(table["headers"], ["H"])

    def test_cell_text_rules(self):
        html = (
            "<table><tr>"
            "<td>A&amp;B</td><td>x&nbsp;y</td><td>line<br>break</td>"
            "<td><script>drop()</script>kept</td><td>  spaced\t out  </td><td>caf&eacute;</td>"
            "</tr></table>"
        )
        table = self.rows(html)
        self.assertEqual(table["rows"], [[
            "A&B", "x y", "line break", "kept", "spaced out", "café",
        ]])

    def test_raw_spans_option(self):
        html = "<table><tr><td rowspan=2 colspan=0>A</td></tr><tr><td>B</td></tr></table>"
        result = self.tool.execute(mode="extract", html=html, raw_spans=True)
        self.assertEqual(
            result["tables"][0]["raw_spans"],
            [
                [{"text": "A", "rowspan": 2, "colspan": 0}],
                [{"text": "B", "rowspan": 1, "colspan": 1}],
            ],
        )


class HtmlTableToolCsvTest(unittest.TestCase):
    """to_csv rendering and round-trips."""

    def setUp(self):
        self.tool = HtmlTableTool()

    def test_basic_csv_with_header(self):
        html = "<table><tr><th>Name</th><th>Qty</th></tr><tr><td>a,b</td><td>1</td></tr></table>"
        result = self.tool.execute(mode="to_csv", html=html)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["csv"].splitlines(), ["Name,Qty", '"a,b",1'])

    def test_csv_round_trip_150(self):
        """CSV parsed back equals the expanded rows on 150 seeded tables."""
        for seed in range(200, 350):
            with self.subTest(seed=seed):
                document = _gen_document(seed, 1)
                extracted = self.tool.execute(mode="extract", html=document)
                self.assertEqual(extracted["status"], "success")
                payload = extracted["tables"][0]
                result = self.tool.execute(mode="to_csv", html=document)
                self.assertEqual(result["status"], "success", result.get("error"))
                parsed = list(csv.reader(io.StringIO(result["csv"])))
                expected = ([payload["headers"]] if payload["headers"] is not None else []) + payload["rows"]
                self.assertEqual(parsed, expected)

    def test_csv_quote_escaping(self):
        html = '<table><tr><td>say "hi"</td><td>x</td></tr></table>'
        result = self.tool.execute(mode="to_csv", html=html)
        parsed = list(csv.reader(io.StringIO(result["csv"])))
        self.assertEqual(parsed, [['say "hi"', "x"]])

    def test_table_index_selection(self):
        html = "<table><tr><td>one</td></tr></table><table><tr><td>two</td></tr></table>"
        result = self.tool.execute(mode="to_csv", html=html, table_index=1)
        self.assertEqual(result["csv"].splitlines(), ["two"])
        out_of_range = self.tool.execute(mode="to_csv", html=html, table_index=2)
        self.assertEqual(out_of_range["status"], "error")
        self.assertIn("out of range", out_of_range["error"])


class HtmlTableToolCompareTest(unittest.TestCase):
    """compare mode diffs."""

    def setUp(self):
        self.tool = HtmlTableTool()

    def test_compare_identical(self):
        html = "<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>"
        result = self.tool.execute(mode="compare", html=html, html2=html)
        self.assertTrue(result["same"])
        self.assertEqual(result["changed_cells"], [])

    def test_compare_changed_cell_and_header(self):
        left = "<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>"
        right = "<table><tr><th>A</th><th>C</th></tr><tr><td>1</td><td>9</td></tr></table>"
        result = self.tool.execute(mode="compare", html=left, html2=right)
        self.assertFalse(result["same"])
        self.assertEqual(result["header_changes"], [{"position": 1, "a": "B", "b": "C"}])
        self.assertEqual(result["changed_cells"], [{"row": 0, "col": 1, "a": "2", "b": "9"}])

    def test_compare_added_removed_rows(self):
        left = "<table><tr><td>1</td></tr></table>"
        right = "<table><tr><td>1</td></tr><tr><td>2</td></tr><tr><td>3</td></tr></table>"
        result = self.tool.execute(mode="compare", html=left, html2=right)
        self.assertEqual(result["added_rows"], [1, 2])
        self.assertEqual(result["removed_rows"], [])
        self.assertEqual(result["b"]["row_count"], 3)
        swapped = self.tool.execute(mode="compare", html=right, html2=left)
        self.assertEqual(swapped["removed_rows"], [1, 2])

    def test_compare_column_growth(self):
        left = "<table><tr><td>1</td></tr></table>"
        right = "<table><tr><td>1</td><td>2</td></tr></table>"
        result = self.tool.execute(mode="compare", html=left, html2=right)
        self.assertEqual(result["added_cols"], 1)
        self.assertFalse(result["same"])

    def test_compare_structures_and_indexes(self):
        html_a = "<table><tr><td>a</td></tr></table><table><tr><td>x</td></tr></table>"
        html_b = "<table><tr><td>b</td></tr><tr><td>c</td></tr></table>"
        via_structures = HtmlTableTool().execute(
            mode="compare",
            table_a={"headers": None, "rows": [["a"]], "col_count": 1},
            table_b={"headers": None, "rows": [["b"], ["c"]], "col_count": 1},
        )
        via_html = self.tool.execute(mode="compare", html=html_a, html2=html_b, table_index=1, table_index2=0)
        self.assertEqual(via_structures["same"], via_html["same"])
        self.assertEqual(via_structures["added_rows"], [1])

    def test_compare_requires_second_source(self):
        result = self.tool.execute(mode="compare", html="<table><tr><td>a</td></tr></table>")
        self.assertEqual(result["status"], "error")
        self.assertIn("html2", result["error"])


class HtmlTableToolValidationTest(unittest.TestCase):
    """Error handling, caps and bounds."""

    def setUp(self):
        self.tool = HtmlTableTool()

    def test_invalid_mode(self):
        result = self.tool.execute(mode="render", html="<table></table>")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_missing_html(self):
        result = self.tool.execute(mode="extract")
        self.assertEqual(result["status"], "error")
        self.assertIn("html", result["error"])

    def test_oversized_input(self):
        result = HtmlTableTool(max_input_bytes=100).execute(
            mode="extract", html="<table><tr><td>" + "x" * 200 + "</td></tr></table>"
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("max_input_bytes", result["error"])

    def test_depth_cap(self):
        html = (
            "<table><tr><td><table><tr><td><table><tr><td><table><tr><td>"
            "<table><tr><td>deep</td></tr></table>"
            "</td></tr></table></td></tr></table></td></tr></table></td></tr></table>"
        )
        result = self.tool.execute(mode="extract", html=html, table_index=4)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_table_depth", result["error"])

    def test_no_tables(self):
        result = self.tool.execute(mode="extract", html="<div>no tables</div>")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["table_count"], 0)
        csv_result = self.tool.execute(mode="to_csv", html="<div>none</div>")
        self.assertEqual(csv_result["status"], "error")
        self.assertIn("empty document", csv_result["error"])

    def test_malformed_html_recovers(self):
        html = "<table><tr><td>a<td>b<tr><td>c</table>"
        result = self.tool.execute(mode="extract", html=html)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tables"][0]["rows"], [["a", "b"], ["c", ""]])

    def test_config_validation(self):
        with self.assertRaises(ValueError):
            HtmlTableTool(max_tables=0)._validate_config()


class HtmlTableToolPathologicalTest(unittest.TestCase):
    """Bounded behavior on pathological inputs (no browser involved)."""

    def test_ten_thousand_rows_under_two_seconds(self):
        parts = [
            "<table><thead><tr><th>ID</th><th>Name</th><th>Value</th><th>Flag</th><th>Note</th></tr></thead><tbody>"
        ]
        for index in range(10_000):
            parts.append(
                "<tr><td>%d</td><td>n%d</td><td>%d</td><td>t</td><td>note %d</td></tr>"
                % (index, index, index * 3, index)
            )
        parts.append("</tbody></table>")
        html = "".join(parts)
        started = time.monotonic()
        result = HtmlTableTool().execute(mode="extract", html=html)
        elapsed = time.monotonic() - started
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tables"][0]["row_count"], 10_000)
        self.assertLess(elapsed, 2.0, f"10k-row table took {elapsed:.2f}s")

    def test_one_megabyte_cell_bounded(self):
        html = "<table><tr><td>" + "a" * 2_000_100 + "</td><td>x</td></tr></table>"
        result = HtmlTableTool().execute(mode="extract", html=html)
        self.assertEqual(result["status"], "success")
        cell = result["tables"][0]["rows"][0][0]
        self.assertLessEqual(len(cell), 1_000_000)
        self.assertEqual(cell, "a" * len(cell))

    def test_fifty_thousand_tables_cap(self):
        html = "<table><tr><td>x</td></tr></table>" * 50_001
        result = HtmlTableTool().execute(mode="extract", html=html)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_tables", result["error"])
        html = "<table><tr><td>x</td></tr></table>" * 50_000
        result = HtmlTableTool().execute(mode="extract", html=html)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["table_count"], 50_000)

    def test_deep_nesting_structured_error(self):
        html = "<table><tr><td>" * 1500 + "deep" + "</td></tr>" * 1500
        result = HtmlTableTool().execute(mode="extract", html=html)
        self.assertEqual(result["status"], "error")
        self.assertIn("nesting", result["error"])


class HtmlTableToolSelfReviewRegressionTest(unittest.TestCase):
    """Regressions for defects found by the hostile self-review (PR #4079)."""

    def setUp(self):
        self.tool = HtmlTableTool()

    def rows(self, html, index=None):
        result = self.tool.execute(mode="extract", html=html, table_index=index)
        self.assertEqual(result["status"], "success", result.get("error"))
        return result["tables"][0]

    def test_rowspan_zero_spans_implicit_row_group_run(self):
        """rowspan=0 spans the whole run of consecutive stray trs (implicit tbody)."""
        html = "<table><tr><td rowspan=0>A</td><td>B</td></tr><tr><td>C</td></tr><tr><td>D</td></tr></table>"
        table = self.rows(html)
        self.assertEqual(table["rows"], [["A", "B"], ["A", "C"], ["A", "D"]])

    def test_rowspan_zero_run_bounded_by_section_and_split_runs(self):
        """A stray run ends at a section; runs on either side are separate groups."""
        html = "<table><tr><td rowspan=0>A</td></tr><tbody><tr><td>x</td></tr></tbody><tr><td>B</td></tr></table>"
        table = self.rows(html)
        self.assertEqual(table["rows"], [["A"], ["x"], ["B"]])

    def test_rowspan_zero_non_first_section_row(self):
        """rowspan=0 on a non-first row spans the section, never the next one."""
        html = (
            "<table><tbody><tr><td>x</td></tr><tr><td rowspan=0>A</td></tr></tbody>"
            "<tbody><tr><td>y</td></tr></tbody></table>"
        )
        table = self.rows(html)
        self.assertEqual(table["rows"], [["x"], ["A"], ["y"]])
        analysis = self.tool.execute(mode="analyze", html=html)
        finding = next(f for f in analysis["tables"][0]["findings"] if f["code"] == "rowspan_zero")
        self.assertEqual(finding["cells"], [{"row": 1, "col": 0, "expanded_to": 1}])

    def test_duplicate_attribute_first_occurrence_wins(self):
        """WHATWG: on duplicate attributes the first occurrence wins."""
        html = '<table><tr><th colspan="3" colspan="0">H</th></tr><tr><td>1</td><td>2</td><td>3</td></tr></table>'
        table = self.rows(html)
        self.assertEqual(table["headers"], ["H", "H", "H"])
        self.assertEqual(table["rows"], [["1", "2", "3"]])
        self.assertEqual(self.rows(
            '<table><tr><td rowspan="2" rowspan="5">A</td><td>B</td></tr><tr><td>C</td></tr></table>'
        )["rows"], [["A", "B"], ["A", "C"]])

    def test_span_non_ascii_digits_are_invalid(self):
        """Only ASCII digits parse; superscripts crash-free default to 1."""
        table = self.rows('<table><tr><td rowspan="²">A</td><td>B</td></tr><tr><td>C</td></tr></table>')
        self.assertEqual(table["rows"], [["A", "B"], ["C", ""]])
        table = self.rows('<table><tr><td rowspan="１２">A</td><td>B</td></tr><tr><td>C</td></tr></table>')  # noqa: RUF001
        self.assertEqual(table["rows"], [["A", "B"], ["C", ""]])
        table = self.rows('<table><tr><td colspan="٣">A</td><td>B</td></tr></table>')
        self.assertEqual(table["rows"], [["A", "B"]])

    def test_unclosed_inline_element_does_not_swallow_next_cell(self):
        """Implied end tags close open cells/rows through inline elements."""
        table = self.rows("<table><tr><td><b>x<td>y</table>")
        self.assertEqual(table["rows"], [["x", "y"]])
        table = self.rows("<table><tr><td><b>x<tr><td>y</table>")
        self.assertEqual(table["rows"], [["x"], ["y"]])
        table = self.rows("<table><tr><td><b>x<tbody><tr><td>y</table>")
        self.assertEqual(table["rows"], [["x"], ["y"]])
        table = self.rows("<table><tr><p>para<td>c</table>")
        self.assertEqual(table["rows"], [["c"]])
        table = self.rows("<table><tr><td><b>x</td><td>y</td></tr></table>")
        self.assertEqual(table["rows"], [["x", "y"]])

    def test_extract_table_index_semantics(self):
        """Omitted index -> all top-level tables; an explicit index (0 included)
        selects exactly one table, consistent with to_csv and compare."""
        html = "<table><tr><td>one</td></tr></table><table><tr><td>two</td></tr></table>"
        all_tables = self.tool.execute(mode="extract", html=html)
        self.assertEqual(all_tables["table_count"], 2)
        first = self.tool.execute(mode="extract", html=html, table_index=0)
        self.assertEqual(first["table_count"], 1)
        self.assertEqual(first["tables"][0]["rows"], [["one"]])
        second = self.tool.execute(mode="extract", html=html, table_index=1)
        self.assertEqual(second["tables"][0]["rows"], [["two"]])
        csv_first = self.tool.execute(mode="to_csv", html=html, table_index=0)
        self.assertEqual(csv_first["csv"].splitlines(), ["one"])
        compared = self.tool.execute(mode="compare", html=html, html2=html, table_index=0, table_index2=1)
        self.assertEqual(compared["status"], "success")
        self.assertEqual(compared["changed_cells"], [{"row": 0, "col": 0, "a": "one", "b": "two"}])
        out_of_range = self.tool.execute(mode="extract", html=html, table_index=2)
        self.assertEqual(out_of_range["status"], "error")
        bad_type = self.tool.execute(mode="extract", html=html, table_index="0")
        self.assertEqual(bad_type["status"], "error")

    def test_invalid_numeric_references_become_replacement(self):
        """&#0;, surrogates and out-of-range refs decode to U+FFFD (JSON-safe)."""
        table = self.rows("<table><tr><td>&#0; &#xD800; &#x110000;</td></tr></table>")
        self.assertEqual(table["rows"], [["\ufffd \ufffd \ufffd"]])
        json.dumps(table)  # must not raise
        grin = self.rows("<table><tr><td>&#x1F600; ok</td></tr></table>")
        self.assertEqual(grin["rows"], [["\U0001f600 ok"]])

    def test_c0_control_character_reference_pinned(self):
        """Pinned divergence: the stdlib decoder drops C0 control char refs
        (lxml keeps them); the tool follows the stdlib deterministically."""
        table = self.rows("<table><tr><td>a&#3;b</td></tr></table>")
        self.assertEqual(table["rows"], [["ab"]])

    def test_colgroup_span_preallocation_ignored(self):
        """Pinned: colgroup/col span pre-allocation is ignored; cells set the grid."""
        table = self.rows('<table><colgroup><col span="3"><col></colgroup><tr><td>1</td><td>2</td></tr></table>')
        self.assertEqual(table["rows"], [["1", "2"]])
        self.assertEqual(table["col_count"], 2)

    def test_compare_changed_cells_cap_flags_truncation(self):
        left = [[f"k{i}" for i in range(5)] for _ in range(3000)]
        right = [[f"v{i}" for i in range(5)] for _ in range(3000)]
        result = self.tool.execute(
            mode="compare",
            table_a={"headers": None, "rows": left},
            table_b={"headers": None, "rows": right},
        )
        self.assertEqual(len(result["changed_cells"]), 10_000)
        self.assertTrue(result["changed_cells_truncated"])
        self.assertFalse(result["same"])

    def test_extract_thirty_k_rows_bounded(self):
        """Quadratic regressions (descendant walk, nested anchors) stay linear."""
        html = "<table><tbody>" + "".join(
            f"<tr><td>{i}</td><td>a{i}</td><td>b{i}</td><td>c{i}</td><td>d{i}</td></tr>"
            for i in range(30_000)
        ) + "</tbody></table>"
        started = time.monotonic()
        result = self.tool.execute(mode="extract", html=html)
        elapsed = time.monotonic() - started
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tables"][0]["row_count"], 30_000)
        self.assertLess(elapsed, 4.0, f"30k-row table took {elapsed:.2f}s")

    def test_nested_table_anchors_stay_linear(self):
        html = "<table>" + "".join(
            f"<tr><td>cell {i}<table><tr><td>n{i}</td></tr></table></td></tr>" for i in range(6_000)
        ) + "</table>"
        started = time.monotonic()
        result = self.tool.execute(mode="extract", html=html)
        elapsed = time.monotonic() - started
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["tables"][0]["child_tables"]), 6_000)
        self.assertLess(elapsed, 3.0, f"6k nested tables took {elapsed:.2f}s")

    def test_one_hundred_k_cells_bounded(self):
        html = "<table><tbody>" + "".join(
            f"<tr><td>{i}</td><td>a{i}</td><td>b{i}</td><td>c{i}</td><td>d{i}</td></tr>"
            for i in range(20_000)
        ) + "</tbody></table>"
        started = time.monotonic()
        result = self.tool.execute(mode="extract", html=html)
        elapsed = time.monotonic() - started
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["tables"][0]["rows"][0]), 5)
        self.assertLess(elapsed, 4.0, f"100k cells took {elapsed:.2f}s")


class HtmlTableToolRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped html_table_tool.yaml as a tool component."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the current app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the shipped yaml resolves to a tool component exposing the HtmlTableTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "HtmlTableTool")

    def test_manager(self):
        """Verify the HtmlTableTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, HtmlTableTool)
        self.assertEqual(tool.input_keys, ["mode", "html"])


if __name__ == "__main__":
    unittest.main()
