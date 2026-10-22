import csv
import io
import math
import os
import random
import statistics
import unittest
from collections import Counter
from datetime import datetime

from agentuniverse.agent.action.tool.common_tool import ColumnStatsTool as ExportedColumnStatsTool
from agentuniverse.agent.action.tool.common_tool import column_stats_tool as column_stats_module
from agentuniverse.agent.action.tool.common_tool.column_stats_tool import ColumnStatsTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(column_stats_module.__file__), "column_stats_tool.yaml")

ASCII_DIGITS = set("0123456789")
TYPE_PRIORITY = ("integer", "float", "boolean", "datetime", "uuid")
BOOLEAN_WORDS = {"true", "false", "True", "False", "TRUE", "FALSE"}
# The documented, ordered datetime contract (mirrored for the oracle).
DATETIME_FORMATS = (
    "%Y-%m-%d",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%d.%m.%Y",
)


# ---------------------------------------------------------------------------
# Independent reference implementation of the documented grammar.  This is a
# character-scanner (the tool uses compiled regexes) so the oracle does not
# share code paths with the implementation under test.


def reference_is_integer(value):
    body = value[1:] if value[:1] in ("+", "-") else value
    return bool(body) and all(ch in ASCII_DIGITS for ch in body)


def _reference_exponent_ok(exponent):
    if not exponent:
        return True
    ebody = exponent[1:] if exponent[:1] in ("+", "-") else exponent
    return bool(ebody) and all(ch in ASCII_DIGITS for ch in ebody)


def _reference_mantissa_ok(mantissa):
    if not mantissa:
        return False
    if "." not in mantissa:
        return all(ch in ASCII_DIGITS for ch in mantissa)
    left, _, right = mantissa.partition(".")
    if "." in right or not right:  # a second dot, or a trailing dot ("1.")
        return False
    return (not left or all(ch in ASCII_DIGITS for ch in left)) and all(ch in ASCII_DIGITS for ch in right)


def reference_is_float(value):
    body = value[1:] if value[:1] in ("+", "-") else value
    if "e" in body and "E" in body:
        return False
    if "e" in body:
        mantissa, exponent = body.split("e", 1)
    elif "E" in body:
        mantissa, exponent = body.split("E", 1)
    else:
        mantissa, exponent = body, ""
    return _reference_mantissa_ok(mantissa) and _reference_exponent_ok(exponent)


def reference_is_uuid(value):
    groups = value.split("-")
    if [len(g) for g in groups] != [8, 4, 4, 4, 12]:
        return False
    hexdigits = set("0123456789abcdef")
    return all(all(ch in hexdigits for ch in group) for group in groups)


def reference_parse_datetime(value):
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(candidate, fmt)
        except ValueError:
            continue
    return None


def reference_classify(value):
    """Return the documented verdict for one cell ('' means null -> None)."""
    if value == "":
        return None
    if reference_is_integer(value):
        return "integer"
    if reference_is_float(value):
        try:
            if math.isfinite(float(value)):
                return "float"
        except ValueError:
            pass
        return "text"
    if value in BOOLEAN_WORDS:
        return "boolean"
    if reference_is_uuid(value):
        return "uuid"
    if (
        6 <= len(value) <= 35
        and value[0] in ASCII_DIGITS
        and any(ch in value for ch in "-/.:")
        and reference_parse_datetime(value) is not None
    ):
        return "datetime"
    return "text"


def reference_verdict(values):
    """Return (inferred_type, type_ratio, winning_type) per the documented rules."""
    kinds = [reference_classify(v) for v in values if v != ""]
    non_null = len(kinds)
    if non_null == 0:
        return "empty", 0.0, None
    counts = Counter(kinds)
    best, best_count = None, 0
    for kind in TYPE_PRIORITY:
        if counts.get(kind, 0) > best_count:
            best, best_count = kind, counts[kind]
    if best_count == non_null:
        return best, 1.0, best
    if best_count == 0:
        return "text", 1.0, None
    return "mixed", best_count / non_null, best


def mirror_histogram(ordered, bins=10):
    low, high = ordered[0], ordered[-1]
    counts = [0] * bins
    width = (high - low) / bins
    if width > 0:
        for value in ordered:
            slot = int((value - low) / width)
            counts[min(max(slot, 0), bins - 1)] += 1
    else:
        counts[0] = len(ordered)
    return counts


def read_rows(text, delimiter=",", quotechar='"'):
    """Independent csv.reader enumeration used as the parsing oracle."""
    return list(csv.reader(io.StringIO(text, newline=""), delimiter=delimiter, quotechar=quotechar))


# ---------------------------------------------------------------------------
# Seeded CSV generators.


INTEGER_POOL = ["0", "-7", "900", "007", "-042", "+15", "12", "3"]
FLOAT_POOL = ["1.5", ".5", "-.5", "1e5", "1E-5", "2.5e+3", "0.0", "-0.0", "00.12", "3.25"]
NOT_NUMBER_POOL = ["NaN", "nan", "inf", "-inf", "Infinity", "-NaN", "1.", ".", "1e999", "-1e999", "٣", "١٢٣"]
BOOLEAN_POOL = ["true", "false", "True", "False", "TRUE", "FALSE", "tRuE", "0", "1"]
DATETIME_POOL = [
    "2024-01-02", "2024-01-02T03:04:05", "2024-01-02T03:04:05.123", "2024-01-02 03:04:05",
    "2024-01-02T03:04:05Z", "2024-01-02T03:04:05+02:00", "2024/05/06", "05/06/2024",
    "02.05.2024", "2024-13-45", "2024-02-30", "20240102", "2024-1-2", "999999999",
]
UUID_POOL = [
    "123e4567-e89b-12d3-a456-426614174000",
    "00000000-0000-0000-0000-000000000000",
    "123E4567-E89B-12D3-A456-426614174000",
    "123e4567e89b12d3a456426614174000",
    "123e4567-e89b-12d3-a456-42661417400",
]
TEXT_POOL = ["hello", "a-b", "2024-13-45-x", "some sentence", "b", "zz"]


def generate_value_set(rng):
    """One seeded column value-set biased to a category with occasional mixing."""
    category = rng.choice(["integer", "float", "not_number", "boolean", "datetime", "uuid", "text", "mixed"])
    pools = {
        "integer": INTEGER_POOL,
        "float": FLOAT_POOL,
        "not_number": NOT_NUMBER_POOL,
        "boolean": BOOLEAN_POOL,
        "datetime": DATETIME_POOL,
        "uuid": UUID_POOL,
        "text": TEXT_POOL,
        "mixed": INTEGER_POOL + FLOAT_POOL + DATETIME_POOL + TEXT_POOL + BOOLEAN_POOL,
    }
    pool = pools[category]
    size = rng.randint(3, 12)
    values = [rng.choice(pool) for _ in range(size)]
    if category != "mixed" and rng.random() < 0.35:
        values[rng.randrange(size)] = rng.choice(INTEGER_POOL + FLOAT_POOL + TEXT_POOL + [""])
    if rng.random() < 0.2:
        values[rng.randrange(size)] = ""
    return values


def csv_from_columns(columns, header=True, delimiter=",", quotechar='"'):
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=delimiter, quotechar=quotechar, lineterminator="\n")
    if header:
        writer.writerow([f"c{index}" for index in range(len(columns))])
    for row in zip(*columns, strict=True):
        writer.writerow(row)
    return buffer.getvalue()


def csv_from_named_columns(named, header=True, delimiter=",", quotechar='"'):
    """Write a CSV whose header is the dict keys (order preserved)."""
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=delimiter, quotechar=quotechar, lineterminator="\n")
    if header:
        writer.writerow(list(named))
    for row in zip(*named.values(), strict=True):
        writer.writerow(row)
    return buffer.getvalue()


def generate_random_csv(rng):
    """A seeded CSV with quoting edge cases: embedded delimiters, quotes, newlines."""
    rows = rng.randint(3, 30)
    cols = rng.randint(2, 7)
    header = rng.random() < 0.8
    delimiter = rng.choice([",", ";", "\t"])
    quotechar = '"'
    nasty = ['has,comma', 'has"quote', "has\nnewline", " has space ", 'mix,"\n"']
    plain = ["1", "-2.5", "2024-01-02", "true", "", "word", "007", ".5"]
    matrix = [[rng.choice(nasty + plain) for _ in range(rows)] for _ in range(cols)]
    if header and rng.random() < 0.25:  # occasionally duplicate/empty headers
        names = [f"c{i}" for i in range(cols)]
        names[0] = ""
        if cols > 1:
            names[1] = names[0] or "c0"
        if cols > 2:
            names[2] = "c2"
        buffer = io.StringIO(newline="")
        writer = csv.writer(buffer, delimiter=delimiter, quotechar=quotechar, lineterminator="\n")
        writer.writerow(names)
        for row in zip(*matrix, strict=True):
            writer.writerow(row)
        return buffer.getvalue(), delimiter, quotechar, header, names
    return csv_from_columns(matrix, header, delimiter, quotechar), delimiter, quotechar, header, None


class ColumnStatsToolTest(unittest.TestCase):
    """Unit tests for ColumnStatsTool profile / column_detail / compare / sample."""

    def test_profile_basic_fields(self):
        """Profile reports row/col counts and per-column structure for a known CSV."""
        text = "id,score,when,flag,note\n1,1.5,2024-01-02,true,hello\n2,.5,2024-01-03T04:05:06Z,FALSE,world\n,0.25,,true,\n"
        result = self.tool().execute(mode="profile", csv_text=text)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["row_count"], 3)
        self.assertEqual(result["col_count"], 5)
        by_name = {column["name"]: column for column in result["columns"]}
        self.assertEqual(by_name["id"]["inferred_type"], "integer")
        self.assertEqual(by_name["score"]["inferred_type"], "float")
        self.assertEqual(by_name["when"]["inferred_type"], "datetime")
        self.assertEqual(by_name["flag"]["inferred_type"], "boolean")
        self.assertEqual(by_name["note"]["inferred_type"], "text")
        self.assertEqual(by_name["id"]["nulls"], 1)
        self.assertEqual(by_name["id"]["non_null"], 2)
        # '2024-01-02' (Y-m-d) and '2024-01-03T04:05:06Z' (iso-T-tz) tie on
        # count, so the fixed format order breaks the tie deterministically.
        self.assertEqual(by_name["when"]["stats"]["format"], "Y-m-d")
        self.assertEqual(by_name["note"]["stats"]["top_values"][0]["value"], "hello")

    def test_datetime_stats_min_max_and_formats(self):
        """Datetime stats report min/max ISO bounds and deterministic format guesses."""
        text = "d\n2024-01-02\n2024-12-31T23:59:59\n05/06/2024\n"
        stats = self.tool().execute(mode="profile", csv_text=text)["columns"][0]["stats"]
        self.assertEqual(stats["min"], "2024-01-02T00:00:00")
        self.assertEqual(stats["max"], "2024-12-31T23:59:59")
        self.assertEqual(stats["format"], "Y-m-d")
        self.assertEqual([guess["format"] for guess in stats["format_guesses"]], ["Y-m-d", "iso-T", "m/d/Y"])

    def test_boolean_and_uuid_columns(self):
        """Booleans are word forms only; uuids are canonical lowercase only."""
        text = "b,u\ntrue,123e4567-e89b-12d3-a456-426614174000\nFALSE,00000000-0000-0000-0000-000000000001\n1,123E4567-E89B-12D3-A456-426614174000\n"
        result = self.tool().execute(mode="profile", csv_text=text)
        self.assertEqual(result["columns"][0]["inferred_type"], "mixed")  # '1' is an integer among booleans
        self.assertEqual(result["columns"][0]["winning_type"], "boolean")
        self.assertEqual(result["columns"][1]["inferred_type"], "mixed")  # lowercase canonical + uppercase hex
        self.assertEqual(result["columns"][1]["winning_type"], "uuid")
        upper = self.tool().execute(mode="profile", csv_text="u\n123E4567-E89B-12D3-A456-426614174000\n")
        self.assertEqual(upper["columns"][0]["inferred_type"], "text")  # uppercase hex alone is text

    def test_no_header_uses_col_n_names(self):
        """Without header=True the columns are named col-0, col-1, ..."""
        result = self.tool().execute(mode="profile", csv_text="1,a\n2,b\n", header=False)
        self.assertEqual([column["name"] for column in result["columns"]], ["col-0", "col-1"])

    def test_duplicate_and_empty_header_names_fall_back(self):
        """Duplicate or empty header cells fall back to col-N names."""
        text = "a,,a\n1,2,3\n"
        result = self.tool().execute(mode="profile", csv_text=text)
        self.assertEqual([column["name"] for column in result["columns"]], ["a", "col-1", "col-2"])

    def test_type_conflict_warning_lines(self):
        """Mixed columns produce a type_conflict warning with capped sample lines."""
        text = "v\n1\n2\nabc\n3\nxyz\n"
        result = self.tool().execute(mode="profile", csv_text=text)
        column = result["columns"][0]
        self.assertEqual(column["inferred_type"], "mixed")
        self.assertEqual(column["winning_type"], "integer")
        self.assertAlmostEqual(column["type_ratio"], 3 / 5)
        warnings = [w for w in result["warnings"] if w["kind"] == "type_conflict"]
        self.assertEqual(warnings[0]["sample_lines"], [4, 6])  # physical lines, header is line 1

    def test_ragged_rows_reported_with_lines(self):
        """Rows shorter or longer than the header are flagged with physical line numbers."""
        text = "a,b,c\n1,2,3\n4,5\n6,7,8,9\n"
        result = self.tool().execute(mode="profile", csv_text=text)
        ragged = [w for w in result["warnings"] if w["kind"] == "ragged_row"]
        self.assertEqual([(w["line"], w["length"]) for w in ragged], [(3, 2), (4, 4)])
        self.assertEqual(result["columns"][2]["nulls"], 1)  # padded short row counts a null in the last column

    def test_bom_is_stripped(self):
        """A UTF-8 BOM does not corrupt the first header name."""
        result = self.tool().execute(mode="profile", csv_text="﻿id,v\n1,2\n")
        self.assertEqual(result["columns"][0]["name"], "id")

    def test_quoted_newline_coordinates(self):
        """Cells with embedded newlines keep csv.reader physical line numbers."""
        text = 'a,b\n"x\ny",2\n3,4\n'
        sample = self.tool().execute(mode="sample", csv_text=text, n=10)
        rows = [(row["index"], row["line"], row["cells"]) for row in sample["rows"]]
        self.assertEqual(rows, [(0, 3, ["x\ny", "2"]), (1, 4, ["3", "4"])])
        self.assertEqual(read_rows(text)[1], ["x\ny", "2"])

    def test_leading_zero_flag_and_huge_integers(self):
        """'007' is an integer with a leading_zero_suspicious note; huge ints stay exact."""
        huge = "1" + "0" * 99
        text = f"v\n007\n-042\n{huge}\n"
        column = self.tool().execute(mode="profile", csv_text=text)["columns"][0]
        self.assertEqual(column["inferred_type"], "integer")
        self.assertIn("leading_zero_suspicious", column["notes"])
        self.assertEqual(column["stats"]["sum"], 7 - 42 + int(huge))  # arbitrary precision, no float coercion
        self.assertEqual(column["stats"]["max"], int(huge))

    def test_nan_and_inf_are_text(self):
        """NaN/inf spellings are text (documented), and 1e999 float overflow demotes to text."""
        for value in ("NaN", "nan", "inf", "-inf", "Infinity", "1e999", "-1e999"):
            result = self.tool().execute(mode="profile", csv_text=f"v\n{value}\n")
            self.assertEqual(result["columns"][0]["inferred_type"], "text", value)

    def test_negative_zero_and_unicode_digits(self):
        """'-0' is an integer and '-0.0' a float; unicode digits are text."""
        text = "a,b,c\n-0,-0.0,٣\n"
        result = self.tool().execute(mode="profile", csv_text=text)
        self.assertEqual(result["columns"][0]["inferred_type"], "integer")
        self.assertEqual(result["columns"][1]["inferred_type"], "float")
        self.assertEqual(result["columns"][2]["inferred_type"], "text")

    def test_datetime_failures_become_text(self):
        """Impossible calendar dates fail every format and are typed text."""
        for value in ("2024-13-45", "2024-02-30"):
            result = self.tool().execute(mode="profile", csv_text=f"d\n{value}\n")
            self.assertEqual(result["columns"][0]["inferred_type"], "text", value)

    def test_dot_dates_parse_and_dotted_non_dates_stay_text(self):
        """DD.MM.YYYY reaches the documented format list; other dotted forms stay text."""
        cases = {
            "02.01.2024": "datetime",
            "31.12.2024": "datetime",
            "2.1.2024": "datetime",
            "32.13.2024": "text",  # month 13 is impossible
            "1.2.3": "text",  # too short for a 4-digit year
            "192.168.1.1": "text",  # four dots, matches no format
        }
        for value, expected in cases.items():
            result = self.tool().execute(mode="profile", csv_text=f"d\n{value}\n")
            self.assertEqual(result["columns"][0]["inferred_type"], expected, value)
        dot = self.tool().execute(mode="profile", csv_text="d\n02.01.2024\n31.12.2024\n")
        self.assertEqual(dot["columns"][0]["stats"]["format_guesses"], [{"format": "d.m.Y", "count": 2}])

    def test_column_detail_breakdown(self):
        """column_detail returns frequency, previews, and failed cells with line numbers."""
        text = "v\n10\n20\nabc\n20\n"
        result = self.tool().execute(mode="column_detail", csv_text=text, column="v")
        self.assertEqual(result["column"]["inferred_type"], "mixed")  # one text cell among integers
        self.assertEqual(result["column"]["winning_type"], "integer")
        self.assertEqual(result["value_frequency"][0], {"value": "20", "count": 2})
        self.assertEqual([p["parsed"] for p in result["parsed_previews"]], [10, 20, 20])
        self.assertEqual(result["failed_cells"], [{"line": 4, "value": "abc", "classified_as": "text"}])
        by_index = self.tool().execute(mode="column_detail", csv_text=text, column_index=0)
        self.assertEqual(by_index["column"]["name"], "v")

    def test_column_detail_errors(self):
        """Unknown columns, disagreeing selectors, and missing selectors are rejected."""
        text = "a,b\n1,2\n"
        self.assertIn("not found", self.tool().execute(mode="column_detail", csv_text=text, column="zzz")["error"])
        self.assertIn("disagree", self.tool().execute(mode="column_detail", csv_text=text, column="a", column_index=1)["error"])
        self.assertIn("required", self.tool().execute(mode="column_detail", csv_text=text)["error"])
        self.assertIn("out of range", self.tool().execute(mode="column_detail", csv_text=text, column_index=5)["error"])

    def test_compare_schema_drift_and_flags(self):
        """compare reports added/removed columns, rename guesses, type changes and drift."""
        a = "id,score,label\n1,10,x\n2,20,y\n3,30,z\n"
        b = "id,points,note\n1,11,x\n2,22,y\n"
        result = self.tool().execute(mode="compare", csv_text_a=a, csv_text_b=b)
        self.assertEqual(result["columns_removed"], ["score", "label"])
        self.assertEqual(result["columns_added"], ["points", "note"])
        # Position-based rename heuristics pair both removed columns with the
        # added columns that took their indices.
        self.assertEqual(
            result["rename_guesses"],
            [{"from": "score", "to": "points", "index": 1}, {"from": "label", "to": "note", "index": 2}],
        )
        self.assertEqual(result["row_count"], {"a": 3, "b": 2, "delta": -1})
        drift = {entry["column"]: entry for entry in result["numeric_drift"]}
        self.assertTrue(drift["id"]["drift"])  # mean 2 -> 1.5 is a 25% shift
        self.assertAlmostEqual(drift["id"]["mean_shift_ratio"], 0.25)
        b2 = "id,score,label\n1,10,x\n2,20,y\n3,31,z\n"
        result2 = self.tool().execute(mode="compare", csv_text_a=a, csv_text_b=b2)
        drift2 = {entry["column"]: entry for entry in result2["numeric_drift"]}
        self.assertFalse(drift2["score"]["drift"])  # mean 20 -> 20.333 is below 10%
        b3 = "id,score\nx,10\ny,20\n"
        result3 = self.tool().execute(mode="compare", csv_text_a=a, csv_text_b=b3)
        self.assertIn({"column": "id", "from": "integer", "to": "text"}, result3["type_changes"])

    def test_sample_modes(self):
        """first/last/random sampling is deterministic and documented."""
        text = "v\n" + "".join(f"{i}\n" for i in range(10))
        tool = self.tool()
        first = tool.execute(mode="sample", csv_text=text, n=3, sample_mode="first")
        last = tool.execute(mode="sample", csv_text=text, n=3, sample_mode="last")
        random_a = tool.execute(mode="sample", csv_text=text, n=4, sample_mode="random", seed=42)
        random_b = tool.execute(mode="sample", csv_text=text, n=4, sample_mode="random", seed=42)
        self.assertEqual([row["index"] for row in first["rows"]], [0, 1, 2])
        self.assertEqual([row["index"] for row in last["rows"]], [7, 8, 9])
        self.assertEqual(random_a, random_b)
        self.assertEqual([row["index"] for row in random_a["rows"]], sorted(row["index"] for row in random_a["rows"]))
        expected = sorted(random.Random(42).sample(range(10), 4))  # noqa: S311
        self.assertEqual([row["index"] for row in random_a["rows"]], expected)
        capped = tool.execute(mode="sample", csv_text=text, n=99)
        self.assertEqual(capped["n_returned"], 10)

    def test_validation_errors(self):
        """Mode, dialect, size, and cross-mode parameter misuse return structured errors."""
        tool = self.tool()
        self.assertEqual(tool.execute(mode="nope", csv_text="a\n1\n")["error_type"], "validation_error")
        self.assertIn("non-empty", tool.execute(mode="profile")["error"])
        self.assertIn("delimiter", tool.execute(mode="profile", csv_text="a\n1\n", delimiter=",,")["error"])
        self.assertIn("delimiter", tool.execute(mode="profile", csv_text="a\n1\n", delimiter='"', quotechar='"')["error"])
        self.assertIn("not accepted in profile", tool.execute(mode="profile", csv_text="a\n1\n", n=3)["error"])
        self.assertIn("not accepted in compare", tool.execute(mode="compare", csv_text_a="a\n1\n", csv_text_b="a\n1\n", csv_text="a\n1\n")["error"])
        self.assertIn("not accepted in profile", tool.execute(mode="profile", csv_text="a\n1\n", column="a")["error"])
        self.assertIn("between 1 and", tool.execute(mode="sample", csv_text="a\n1\n", n=0)["error"])
        self.assertIn("sample_mode", tool.execute(mode="sample", csv_text="a\n1\n", n=1, sample_mode="middle")["error"])
        self.assertIn("seed", tool.execute(mode="sample", csv_text="a\n1\n", n=1, sample_mode="random", seed=-1)["error"])
        self.assertIn("no columns", tool.execute(mode="profile", csv_text="\n")["error"])
        self.assertIn("max_rows", tool.execute(mode="profile", csv_text="a\n" + "1\n" * 200001)["error"])
        wide = ",".join(f"c{i}" for i in range(4097)) + "\n"
        self.assertIn("max_columns", tool.execute(mode="profile", csv_text=wide)["error"])

    def test_determinism_across_calls(self):
        """Identical inputs produce deep-equal outputs, including warnings order."""
        text = 'a,b\n1,x\n2,y\n,z\nabc,3\n"q\nz",4\n'
        tool = self.tool()
        first = tool.execute(mode="profile", csv_text=text)
        second = tool.execute(mode="profile", csv_text=text)
        self.assertEqual(first, second)

    @staticmethod
    def tool():
        return ColumnStatsTool()


class ColumnStatsTypeMatrixTest(unittest.TestCase):
    """Type-inference matrix oracle: 400 seeded value-sets vs the reference scanner."""

    def test_type_matrix_against_reference(self):
        """Every seeded set's verdict, ratio, winning type and counts match the reference."""
        rng = random.Random(20240252)  # noqa: S311
        for case in range(400):
            values = generate_value_set(rng)
            text = csv_from_columns([values])
            column = ColumnStatsTool().execute(mode="profile", csv_text=text)["columns"][0]
            inferred, ratio, winning = reference_verdict(values)
            self.assertEqual(column["inferred_type"], inferred, f"case {case}: {values}")
            if inferred == "mixed":
                self.assertEqual(column["type_ratio"], ratio, f"case {case}: {values}")
            else:
                self.assertEqual(column["type_ratio"], ratio)
            self.assertEqual(column["winning_type"], winning, f"case {case}: {values}")
            counts = Counter(k for k in (reference_classify(v) for v in values) if k is not None)
            self.assertEqual(
                {k: v for k, v in column["type_counts"].items() if v},
                dict(counts),
                f"case {case}: {values}",
            )
            self.assertEqual(column["non_null"], counts.total())
            self.assertEqual(column["nulls"], values.count(""))

    def test_verdict_edge_table(self):
        """Hand-written verdicts for the documented edge cases."""
        table = [
            (["007"], "integer", "leading_zero_suspicious"),
            (["1e5"], "float", None),
            (["NaN"], "text", None),
            (["nan"], "text", None),
            (["-0"], "integer", None),
            (["-0.0"], "float", None),
            (["1" + "0" * 99], "integer", None),
            (["2024-13-45"], "text", None),
            (["2024-02-30"], "text", None),
            (["20240102"], "integer", None),  # bare digits are integers, never dates
            (["2024-1-2"], "datetime", None),  # strptime accepts unpadded parts
            (["true", "false", "TRUE"], "boolean", None),
            (["0", "1"], "integer", None),  # 0/1 are integers, not booleans
            (["123e4567-e89b-12d3-a456-426614174000"], "uuid", None),
            (["123E4567-E89B-12D3-A456-426614174000"], "text", None),  # uppercase uuid hex is text
            (["٣"], "text", None),  # unicode digits are text
            (["", "", ""], "empty", None),
            (["hello", "world"], "text", None),
            (["1", "abc"], "mixed", "stats_scope=winning_type_subset"),
        ]
        for values, expected, note in table:
            column = ColumnStatsTool().execute(mode="profile", csv_text=csv_from_columns([values]))["columns"][0]
            self.assertEqual(column["inferred_type"], expected, values)
            if note is None:
                self.assertEqual(column["notes"], [], values)
            else:
                self.assertIn(note, column["notes"], values)

class ColumnStatsCsvParityTest(unittest.TestCase):
    """csv-module parity oracle: 300 seeded CSVs match csv.reader enumeration."""

    def test_cells_rows_and_stats_parity(self):
        """Rows, counts, distinct values and exact statistics match independent enumeration."""
        rng = random.Random(2520)  # noqa: S311
        for case in range(300):
            text, delimiter, quotechar, header, _names = generate_random_csv(rng)
            tool = ColumnStatsTool()
            result = tool.execute(mode="profile", csv_text=text, delimiter=delimiter, quotechar=quotechar, header=header)
            self.assertEqual(result["status"], "success", f"case {case}")
            reader_rows = read_rows(text, delimiter, quotechar)
            body = reader_rows[1:] if header else reader_rows
            width = len(reader_rows[0]) if reader_rows else 0
            self.assertEqual(result["row_count"], len(body), f"case {case}")
            self.assertEqual(result["col_count"], width, f"case {case}")
            sample = tool.execute(mode="sample", csv_text=text, delimiter=delimiter, quotechar=quotechar, header=header, n=1000)
            self.assertEqual([row["cells"] for row in sample["rows"]], [row[:width] + [""] * (width - len(row)) for row in body], f"case {case} cells")
            for index, column in enumerate(result["columns"]):
                values = [(row[index] if index < len(row) else "") for row in body]
                self.assertEqual(column["nulls"], values.count(""), f"case {case} col {index}")
                self.assertEqual(column["non_null"], len(values) - values.count(""), f"case {case} col {index}")
                self.assertEqual(column["distinct"], len({v for v in values if v != ""}), f"case {case} col {index}")
                inferred, _ratio, _winning = reference_verdict(values)
                self.assertEqual(column["inferred_type"], inferred, f"case {case} col {index}: {values}")
                if inferred in ("integer", "float"):
                    parsed = [int(v) if reference_classify(v) == "integer" else float(v) for v in values if v != ""]
                    ordered = sorted(parsed)
                    stats = column["stats"]
                    self.assertEqual(stats["min"], min(ordered), f"case {case} col {index} min")
                    self.assertEqual(stats["max"], max(ordered), f"case {case} col {index} max")
                    expected_sum = sum(ordered) if inferred == "integer" else statistics.fsum(ordered)
                    self.assertEqual(stats["sum"], expected_sum, f"case {case} col {index} sum")
                    self.assertEqual(stats["mean"], statistics.mean(ordered), f"case {case} col {index} mean")
                    self.assertEqual(stats["median"], statistics.median(ordered), f"case {case} col {index} median")
                    if len(ordered) >= 2:
                        cuts = statistics.quantiles(ordered, n=100, method="inclusive")
                        self.assertEqual(stats["p50"], cuts[49], f"case {case} col {index} p50")
                        self.assertEqual(stats["p90"], cuts[89], f"case {case} col {index} p90")
                        self.assertEqual(stats["stdev_sample"], statistics.stdev(ordered))
                        self.assertEqual(stats["stdev_population"], statistics.pstdev(ordered))
                    else:
                        self.assertIsNone(stats["stdev_sample"])
                    self.assertEqual(stats["histogram"]["counts"], mirror_histogram(ordered), f"case {case} col {index} histogram")

    def test_single_value_statistics(self):
        """A single numeric value yields that value everywhere and a null sample stdev."""
        stats = ColumnStatsTool().execute(mode="profile", csv_text="v\n42\n")["columns"][0]["stats"]
        self.assertEqual((stats["min"], stats["max"], stats["sum"], stats["mean"], stats["median"], stats["p50"], stats["p90"]), (42, 42, 42, 42, 42, 42, 42))
        self.assertIsNone(stats["stdev_sample"])
        self.assertEqual(stats["stdev_population"], 0.0)

    def test_median_of_even_matches_statistics_module(self):
        """Median of an even-length integer column equals the statistics module."""
        values = [3, 4, 1, 2]
        text = "v\n" + "".join(f"{v}\n" for v in values)
        stats = ColumnStatsTool().execute(mode="profile", csv_text=text)["columns"][0]["stats"]
        self.assertEqual(stats["median"], statistics.median(values))
        self.assertEqual(stats["median"], 2.5)


def apply_compare_mutation(base, rng):
    """Apply one seeded mutation; returns (mutated, renamed_pair_or_None, mutation_name)."""
    rows = len(next(iter(base.values())))
    mutation = rng.choice(["add", "remove", "rename", "scale", "retype", "drop_rows", "none"])
    mutated = {name: list(values) for name, values in base.items()}
    renamed = None
    if mutation == "add":
        mutated["extra"] = [str(rng.randint(0, 9)) for _ in range(rows)]
    elif mutation == "remove":
        mutated.pop(rng.choice(list(mutated)))
    elif mutation == "rename":
        old_name = rng.choice(list(mutated))
        renamed = (old_name, "renamed_col")
        mutated = {("renamed_col" if name == old_name else name): values for name, values in mutated.items()}
    elif mutation == "scale":
        mutated["score"] = [f"{float(v) * rng.uniform(1.5, 3.0):.3f}" for v in mutated["score"]]
    elif mutation == "retype":
        mutated["id"] = [f"user-{v}" for v in mutated["id"]]
    elif mutation == "drop_rows":
        keep = max(1, rows - rng.randint(1, 3))
        for name in mutated:
            mutated[name] = mutated[name][:keep]
    return mutated, renamed, mutation


class ColumnStatsCompareOracleTest(unittest.TestCase):
    """compare oracle: 100 seeded pairs plus 20 hand-verified drift expectations."""

    def test_seeded_pairs_against_reference(self):
        """Seeded mutations are adjudicated with csv.reader and the reference classifier."""
        rng = random.Random(252252)  # noqa: S311
        for case in range(100):
            rows = rng.randint(4, 20)
            base = {
                "id": [str(rng.randint(1, 1000)) for _ in range(rows)],
                "score": [f"{rng.uniform(0, 100):.3f}" for _ in range(rows)],
                "label": [rng.choice(["x", "y", "z"]) for _ in range(rows)],
                "when": [rng.choice(["2024-01-02", "2024-05-06"]) for _ in range(rows)],
            }
            text_a = csv_from_named_columns(base)
            mutated, renamed, mutation = apply_compare_mutation(base, rng)
            text_b = csv_from_named_columns(mutated)
            result = ColumnStatsTool().execute(mode="compare", csv_text_a=text_a, csv_text_b=text_b)
            self.assertEqual(result["status"], "success", f"case {case} {mutation}")
            names_a = list(base)
            names_b = list(mutated)
            self.assertEqual(result["columns_removed"], [n for n in names_a if n not in names_b], f"case {case} {mutation}")
            self.assertEqual(result["columns_added"], [n for n in names_b if n not in names_a], f"case {case} {mutation}")
            self.assertEqual(result["row_count"]["delta"], len(next(iter(mutated.values()))) - rows, f"case {case} {mutation}")
            if renamed is not None:
                self.assertIn({"from": renamed[0], "to": renamed[1], "index": names_a.index(renamed[0])}, result["rename_guesses"])
            for entry in result["type_changes"]:
                column = entry["column"]
                verdict_a = reference_verdict(base[column])[0]
                verdict_b = reference_verdict(mutated[column])[0]
                self.assertEqual((entry["from"], entry["to"]), (verdict_a, verdict_b), f"case {case} {column}")
            for entry in result["numeric_drift"]:
                values_a = [float(v) for v in base[entry["column"]]]
                values_b = [float(v) for v in mutated[entry["column"]]]
                mean_a, mean_b = statistics.mean(values_a), statistics.mean(values_b)
                expected_drift = abs(mean_b - mean_a) / max(abs(mean_a), 1e-12) > 0.1
                self.assertEqual(entry["drift"], expected_drift, f"case {case} {entry['column']} drift")
                self.assertEqual(entry["mean_a"], mean_a)
                self.assertEqual(entry["mean_b"], mean_b)

    def test_twenty_hand_verified_pairs(self):
        """Twenty hand-constructed comparisons with literal expected outcomes."""
        cases = [
            ("a\n1\n", "a\n1\n", {"removed": [], "added": [], "delta": 0, "drift": {"a": False}}),
            ("a\n1\n", "a\n2\n", {"removed": [], "added": [], "delta": 0, "drift": {"a": True}}),
            ("a,b\n1,2\n", "a\n1\n", {"removed": ["b"], "added": [], "delta": 0, "drift": {"a": False}}),
            ("a\n1\n", "a,b\n1,2\n", {"removed": [], "added": ["b"], "delta": 0, "drift": {"a": False}}),
            ("a,b\n1,2\n", "b,a\n2,1\n", {"removed": [], "added": [], "delta": 0, "drift": {"a": False, "b": False}}),
            ("old\n1\n", "new\n1\n", {"removed": ["old"], "added": ["new"], "renames": [("old", "new", 0)], "delta": 0}),
            ("a\n1\n2\n", "a\n1\n", {"removed": [], "added": [], "delta": -1, "drift": {"a": True}}),
            ("a\n1\n", "a\n1\n2\n", {"removed": [], "added": [], "delta": 1, "drift": {"a": True}}),
            ("a\n1\n2\n3\n", "a\n2\n4\n6\n", {"removed": [], "added": [], "delta": 0, "drift": {"a": True}}),
            ("a\n10\n20\n30\n", "a\n10\n21\n30\n", {"removed": [], "added": [], "delta": 0, "drift": {"a": False}}),
            ("a\nx\ny\n", "a\n1\n2\n", {"removed": [], "added": [], "delta": 0, "changes": [("a", "text", "integer")]}),
            ("a\n1\n2\n", "a\nx\ny\n", {"removed": [], "added": [], "delta": 0, "changes": [("a", "integer", "text")]}),
            ("a\n1.5\n2.5\n", "a\n1.5\n2.75\n", {"removed": [], "added": [], "delta": 0, "drift": {"a": False}}),
            ("a,b\n1,x\n", "b\nx\n", {"removed": ["a"], "added": [], "delta": 0}),
            ("a,b\n1,x\n", "a\n1\n", {"removed": ["b"], "added": [], "delta": 0, "drift": {"a": False}}),
            ("a\n-5\n5\n", "a\n-50\n50\n", {"removed": [], "added": [], "delta": 0, "drift": {"a": False}}),  # both means are 0
            ("a\n1\n2\n", "a,b,c\n1,2,3\n", {"removed": [], "added": ["b", "c"], "delta": -1, "drift": {"a": True}}),
            ("a\n0\n0\n", "a\n0\n5\n", {"removed": [], "added": [], "delta": 0, "drift": {"a": True}}),  # 0-mean baseline: any change flags
            ("a\n1e3\n2e3\n", "a\n1000\n2000\n", {"removed": [], "added": [], "delta": 0, "changes": [("a", "float", "integer")]}),  # same values, different inferred type; type change preempts drift
            ("a\n2024-01-02\n", "a\n2024-01-03\n", {"removed": [], "added": [], "delta": 0, "changes": []}),  # datetimes produce no numeric drift rows
        ]
        for text_a, text_b, expected in cases:
            result = ColumnStatsTool().execute(mode="compare", csv_text_a=text_a, csv_text_b=text_b)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["columns_removed"], expected["removed"], (text_a, text_b))
            self.assertEqual(result["columns_added"], expected["added"], (text_a, text_b))
            self.assertEqual(result["row_count"]["delta"], expected["delta"], (text_a, text_b))
            drift = {entry["column"]: entry["drift"] for entry in result["numeric_drift"]}
            for column, flagged in expected.get("drift", {}).items():
                self.assertEqual(drift.get(column), flagged, (text_a, text_b, column))
            if "renames" in expected:
                self.assertEqual(result["rename_guesses"], [{"from": f, "to": t, "index": i} for f, t, i in expected["renames"]])
            if "changes" in expected:
                self.assertEqual([(c["column"], c["from"], c["to"]) for c in result["type_changes"]], expected["changes"])


class ColumnStatsPathologicalTest(unittest.TestCase):
    """Pathological inputs: 100k cells under 2s and a bounded 1 MB cell."""

    def test_hundred_thousand_cells_under_two_seconds(self):
        """Profiling a 10,000 x 10 CSV (100k cells) completes in under 2 seconds."""
        rng = random.Random(99)  # noqa: S311
        rows = 10_000
        lines = [",".join(f"c{i}" for i in range(10))]
        for _ in range(rows):
            lines.append(",".join(str(rng.randint(0, 100000)) if i % 3 else f"{rng.uniform(0, 1000):.2f}" for i in range(10)))
        text = "\n".join(lines) + "\n"
        self.assertLess(len(text), 8 * 1024 * 1024)
        import time

        start = time.monotonic()
        result = ColumnStatsTool().execute(mode="profile", csv_text=text)
        elapsed = time.monotonic() - start
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["row_count"], rows)
        self.assertLess(elapsed, 2.0, f"profiling 100k cells took {elapsed:.2f}s")

    def test_one_megabyte_cell_is_bounded(self):
        """A 1 MB single cell profiles and samples with bounded echoed values."""
        big = "a" * (1024 * 1024)
        text = f"h1,h2\nshort,\"{big}\"\n"
        tool = ColumnStatsTool()
        result = tool.execute(mode="profile", csv_text=text)
        self.assertEqual(result["status"], "success")
        column = result["columns"][1]
        self.assertEqual(column["stats"]["max_len"], 1024 * 1024)
        self.assertTrue(column["stats"]["top_values"][0]["value"].endswith("[truncated]"))
        sampled = tool.execute(mode="sample", csv_text=text, n=1)
        self.assertEqual(sampled["rows"][0]["cells"][1], big)
        over = tool.execute(mode="profile", csv_text=f"h1,h2\nshort,\"{'a' * (1024 * 1024 + 1)}\"\n")
        self.assertEqual(over["error_type"], "validation_error")
        self.assertIn("max_cell_bytes", over["error"])

    def test_oversized_text_rejected(self):
        """CSV text above max_csv_bytes is rejected deterministically."""
        text = "h\n" + ("x" * 100 + "\n") * 90_000
        self.assertGreater(len(text.encode("utf-8")), 8 * 1024 * 1024)
        result = ColumnStatsTool().execute(mode="profile", csv_text=text)
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("max_csv_bytes", result["error"])


class ColumnStatsExportTest(unittest.TestCase):
    """The package __init__ exports ColumnStatsTool."""

    def test_export(self):
        """common_tool exports ColumnStatsTool in __init__ and __all__."""
        self.assertIs(ExportedColumnStatsTool, ColumnStatsTool)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("ColumnStatsTool", __all__)


class ColumnStatsRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped column_stats_tool.yaml as a tool component."""

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
        """Verify the shipped yaml resolves to a tool component exposing the ColumnStatsTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "ColumnStatsTool")

    def test_manager(self):
        """Verify the ColumnStatsTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, ColumnStatsTool)
        self.assertEqual(tool.input_keys, ["mode"])

    def test_yaml_args_model_schema(self):
        """The args model enumerates modes, requires only mode, and forbids extra properties."""
        schema = self.config.get("args_model_schema")
        self.assertEqual(schema["properties"]["mode"]["enum"], ["profile", "column_detail", "compare", "sample"])
        self.assertEqual(schema["properties"]["sample_mode"]["enum"], ["first", "last", "random"])
        self.assertEqual(schema["required"], ["mode"])
        self.assertFalse(schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
