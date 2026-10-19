#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_csv_json_tool.py

"""Offline unit tests for CsvJsonTool.

The tool is built purely on the standard library (csv, json) and never
touches the network, so this suite runs fully offline. Every assertion
is deterministic: both directions are checked against literal ground
truths (headers, generated keys, type inference with leading-zero
protection, delimiter sniffing, quoting, ragged rows, key order,
nested values), the round-trip property is asserted on uniform
fixtures, and the error matrix covers both the ValueError parameter
checks and the structured error payloads for content failures.
"""

import json
import unittest

from agentuniverse.agent.action.tool.common_tool import CsvJsonTool
from agentuniverse.agent.action.tool.common_tool.csv_json_tool import (
    CsvJsonTool as DirectCsvJsonTool,
)

BASIC_CSV = "name,age,score,active\nAlice,30,91.5,true\nBob,25,88.0,false\n"
BASIC_RECORDS = [
    {"name": "Alice", "age": 30, "score": 91.5, "active": True},
    {"name": "Bob", "age": 25, "score": 88.0, "active": False},
]
CJK_CSV = "name,城市\nAlice,北京\nBob,上海\n"
CJK_RECORDS = [
    {"name": "Alice", "城市": "北京"},
    {"name": "Bob", "城市": "上海"},
]


class CsvJsonToJsonTest(unittest.TestCase):
    """to_json mode: parsing, inference, sniffing, quoting, edges."""

    def setUp(self) -> None:
        self.tool = CsvJsonTool()

    def test_basic_header_ground_truth(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text=BASIC_CSV)
        self.assertEqual(
            result,
            {
                "mode": "to_json",
                "delimiter": ",",
                "has_header": True,
                "type_inference": True,
                "row_count": 2,
                "result": json.dumps(BASIC_RECORDS, ensure_ascii=False, indent=2),
            },
        )

    def test_no_header_generates_column_keys(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text="Alice,30\nBob,25\n", has_header=False)
        self.assertEqual(
            json.loads(result["result"]),
            [
                {"column_1": "Alice", "column_2": 30},
                {"column_1": "Bob", "column_2": 25},
            ],
        )
        self.assertFalse(result["has_header"])

    def test_type_inference_matrix(self) -> None:
        csv_text = "a,b\n007,x\n0,y\n-3,z\n+5,w\n3.14,q\n.5,r\n1e5,s\nTRUE,t\nFalse,u\nNaN,v\nInfinity,w2\n 42,x2\n"
        records = json.loads(self.tool.execute(mode="to_json", csv_text=csv_text)["result"])
        values = [row["a"] for row in records]
        self.assertEqual(
            values,
            [
                "007",  # leading zero stays a string
                0,
                -3,
                5,
                3.14,
                0.5,
                100000.0,  # scientific notation is a canonical float
                True,
                False,
                "NaN",  # non-finite spellings stay strings
                "Infinity",
                " 42",  # never trimmed
            ],
        )

    def test_inference_off_keeps_all_strings(self) -> None:
        result = self.tool.execute(
            mode="to_json",
            csv_text="a,b\n007,1\ntrue,\n",
            type_inference=False,
        )
        self.assertEqual(
            json.loads(result["result"]),
            [
                {"a": "007", "b": "1"},
                {"a": "true", "b": ""},  # empty cell stays an empty string
            ],
        )
        self.assertFalse(result["type_inference"])

    def test_empty_cells_become_null_with_inference(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text="v,w\n1,\n,2\n")
        self.assertEqual(
            json.loads(result["result"]),
            [{"v": 1, "w": None}, {"v": None, "w": 2}],
        )

    def test_sniff_semicolon_with_quoted_semicolons(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text='"x;y";b\n"1;2";3\n')
        self.assertEqual(result["delimiter"], ";")
        self.assertEqual(json.loads(result["result"]), [{"x;y": "1;2", "b": 3}])

    def test_sniff_tab_and_pipe(self) -> None:
        tab = self.tool.execute(mode="to_json", csv_text="a\tb\n1\t2\n")
        self.assertEqual(tab["delimiter"], "\t")
        self.assertEqual(json.loads(tab["result"]), [{"a": 1, "b": 2}])
        pipe = self.tool.execute(mode="to_json", csv_text="a|b\n1|2\n")
        self.assertEqual(pipe["delimiter"], "|")
        self.assertEqual(json.loads(pipe["result"]), [{"a": 1, "b": 2}])

    def test_sniff_tie_prefers_comma(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text="a,b;c\n1,2;3\n")
        self.assertEqual(result["delimiter"], ",")
        self.assertEqual(json.loads(result["result"]), [{"a": 1, "b;c": "2;3"}])

    def test_no_delimiter_sniffs_comma(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text="abc\nxyz\n")
        self.assertEqual(result["delimiter"], ",")
        self.assertEqual(json.loads(result["result"]), [{"abc": "xyz"}])

    def test_explicit_delimiter_overrides_sniffing(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text="a;b\n1;2\n", delimiter=",")
        self.assertEqual(result["delimiter"], ",")
        self.assertEqual(json.loads(result["result"]), [{"a;b": "1;2"}])

    def test_quoted_commas_and_newlines_in_values(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text='name,note\n"A, B","line1\nline2"\n')
        self.assertEqual(
            json.loads(result["result"]),
            [{"name": "A, B", "note": "line1\nline2"}],
        )

    def test_cjk_kept_verbatim(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text=CJK_CSV)
        self.assertEqual(json.loads(result["result"]), CJK_RECORDS)
        self.assertIn("北京", result["result"])  # ensure_ascii=False

    def test_ragged_rows_and_extra_columns(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text="a,b,c\n1\n1,2,3,4\n")
        self.assertEqual(
            json.loads(result["result"]),
            [
                {"a": 1, "b": None, "c": None},  # shorter row fills null
                {"a": 1, "b": 2, "c": 3, "column_4": 4},  # extra column key
            ],
        )

    def test_duplicate_and_empty_headers(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text="id,id,name\n1,2,x\n")
        self.assertEqual(json.loads(result["result"]), [{"id": 1, "id_2": 2, "name": "x"}])
        result = self.tool.execute(mode="to_json", csv_text=",b\n1,2\n")
        self.assertEqual(json.loads(result["result"]), [{"column_1": 1, "b": 2}])

    def test_header_only_and_blank_lines(self) -> None:
        header_only = self.tool.execute(mode="to_json", csv_text="a,b\n")
        self.assertEqual(header_only["row_count"], 0)
        self.assertEqual(header_only["result"], "[]")
        blanks = self.tool.execute(mode="to_json", csv_text="a,b\n\n1,2\n\n")
        self.assertEqual(json.loads(blanks["result"]), [{"a": 1, "b": 2}])
        only_blanks = self.tool.execute(mode="to_json", csv_text="\n\n")
        self.assertEqual(only_blanks["result"], "[]")

    def test_no_header_ragged_rows(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text="a,1\nb\n", has_header=False)
        self.assertEqual(
            json.loads(result["result"]),
            [{"column_1": "a", "column_2": 1}, {"column_1": "b"}],
        )


class CsvJsonToCsvTest(unittest.TestCase):
    """to_csv mode: union keys, ragged rows, key order, rendering."""

    def setUp(self) -> None:
        self.tool = CsvJsonTool()

    def test_union_of_keys_first_seen_order(self) -> None:
        result = self.tool.execute(mode="to_csv", json_text='[{"b": 2, "a": 1}, {"a": 3, "c": 4}]')
        self.assertEqual(
            result,
            {
                "mode": "to_csv",
                "delimiter": ",",
                "row_count": 2,
                "columns": ["b", "a", "c"],
                "result": "b,a,c\n2,1,\n,3,4\n",
            },
        )

    def test_ragged_rows_fill_empty_cells(self) -> None:
        result = self.tool.execute(mode="to_csv", json_text='[{"a":1,"b":2},{"a":3},{"c":4}]')
        self.assertEqual(result["result"], "a,b,c\n1,2,\n3,,\n,,4\n")
        self.assertEqual(result["columns"], ["a", "b", "c"])

    def test_key_order_pins_leading_columns(self) -> None:
        result = self.tool.execute(
            mode="to_csv",
            json_text='[{"a": 1, "b": 2, "c": 3}]',
            key_order=["c", "a"],
        )
        self.assertEqual(result["columns"], ["c", "a", "b"])
        self.assertEqual(result["result"], "c,a,b\n3,1,2\n")

    def test_key_order_as_json_string_and_remainder_appended(self) -> None:
        result = self.tool.execute(
            mode="to_csv",
            json_text='[{"a": 1, "b": 2, "c": 3}]',
            key_order='["b"]',
        )
        self.assertEqual(result["columns"], ["b", "a", "c"])
        self.assertEqual(result["result"], "b,a,c\n2,1,3\n")

    def test_nested_values_json_stringified(self) -> None:
        result = self.tool.execute(
            mode="to_csv",
            json_text='[{"a": {"x": 1}, "b": [1, 2], "c": null}]',
        )
        self.assertEqual(
            result["result"],
            'a,b,c\n"{""x"":1}","[1,2]",\n',
        )

    def test_scalar_rendering(self) -> None:
        result = self.tool.execute(
            mode="to_csv",
            json_text='[{"t": true, "f": false, "n": null, "i": 7, "fl": 1.5, "s": "x"}]',
        )
        self.assertEqual(result["result"], "t,f,n,i,fl,s\ntrue,false,,7,1.5,x\n")

    def test_delimiter_option(self) -> None:
        result = self.tool.execute(mode="to_csv", json_text='[{"a": 1, "b": "x;y"}]', delimiter=";")
        self.assertEqual(result["delimiter"], ";")
        # "x;y" contains the active delimiter, so RFC 4180 quoting applies.
        self.assertEqual(result["result"], 'a;b\n1;"x;y"\n')

    def test_quoting_needed_values(self) -> None:
        result = self.tool.execute(
            mode="to_csv",
            json_text='[{"a": "A, B", "b": "line1\\nline2", "c": "plain"}]',
        )
        self.assertEqual(result["result"], 'a,b,c\n"A, B","line1\nline2",plain\n')

    def test_cjk_kept_verbatim(self) -> None:
        result = self.tool.execute(mode="to_csv", json_text=json.dumps(CJK_RECORDS, ensure_ascii=False))
        self.assertEqual(result["result"], CJK_CSV)

    def test_empty_array_renders_empty_string(self) -> None:
        result = self.tool.execute(mode="to_csv", json_text="[]")
        self.assertEqual(
            result,
            {
                "mode": "to_csv",
                "delimiter": ",",
                "row_count": 0,
                "columns": [],
                "result": "",
            },
        )


class CsvJsonRoundTripTest(unittest.TestCase):
    """Round-trip guarantee on rectangular, uniform fixtures."""

    def setUp(self) -> None:
        self.tool = CsvJsonTool()

    def test_csv_to_json_to_csv_exact(self) -> None:
        records = self.tool.execute(mode="to_json", csv_text=BASIC_CSV)
        back = self.tool.execute(mode="to_csv", json_text=records["result"])
        self.assertEqual(back["result"], BASIC_CSV)

    def test_quoted_values_round_trip_exactly(self) -> None:
        csv_text = '"a,b",c\n"1,2",3\n'
        records = self.tool.execute(mode="to_json", csv_text=csv_text)
        back = self.tool.execute(mode="to_csv", json_text=records["result"])
        self.assertEqual(back["result"], csv_text)

    def test_embedded_newlines_round_trip_exactly(self) -> None:
        csv_text = '"l1\nl2",x\ny,z\n'
        records = self.tool.execute(mode="to_json", csv_text=csv_text)
        back = self.tool.execute(mode="to_csv", json_text=records["result"])
        self.assertEqual(back["result"], csv_text)

    def test_cjk_round_trip_exact(self) -> None:
        records = self.tool.execute(mode="to_json", csv_text=CJK_CSV)
        back = self.tool.execute(mode="to_csv", json_text=records["result"])
        self.assertEqual(back["result"], CJK_CSV)

    def test_json_to_csv_to_json_exact(self) -> None:
        json_text = '[{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]'
        csv_text = self.tool.execute(mode="to_csv", json_text=json_text)["result"]
        records = self.tool.execute(mode="to_json", csv_text=csv_text)
        self.assertEqual(json.loads(records["result"]), json.loads(json_text))

    def test_non_canonical_numeric_normalizes(self) -> None:
        # Documented exception: 1e5 normalizes to 100000.0.
        records = self.tool.execute(mode="to_json", csv_text="a\n1e5\n")
        self.assertEqual(json.loads(records["result"]), [{"a": 100000.0}])
        back = self.tool.execute(mode="to_csv", json_text=records["result"])
        self.assertEqual(back["result"], "a\n100000.0\n")


class CsvJsonErrorTest(unittest.TestCase):
    """Error matrix: ValueError parameter checks vs structured payloads."""

    def setUp(self) -> None:
        self.tool = CsvJsonTool()

    def assert_value_error(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_unknown_mode(self) -> None:
        self.assert_value_error(mode="both", csv_text="a\n1\n")

    def test_missing_or_invalid_text(self) -> None:
        self.assert_value_error(mode="to_json")  # csv_text=None
        self.assert_value_error(mode="to_json", csv_text="")
        self.assert_value_error(mode="to_json", csv_text=123)
        self.assert_value_error(mode="to_json", csv_text=True)
        self.assert_value_error(mode="to_csv")  # json_text=None
        self.assert_value_error(mode="to_csv", json_text="")
        self.assert_value_error(mode="to_csv", json_text=["a"])

    def test_oversized_inputs(self) -> None:
        self.assert_value_error(mode="to_json", csv_text="x" * 100_001)
        self.assert_value_error(mode="to_json", csv_text="\n".join(["a"] * 10_001))
        wide = ",".join(str(i) for i in range(1_001))
        self.assert_value_error(mode="to_json", csv_text=wide + "\n" + wide + "\n")
        self.assert_value_error(mode="to_csv", json_text=json.dumps([{"a": 1}] * 10_001))

    def test_invalid_delimiter(self) -> None:
        self.assert_value_error(mode="to_json", csv_text="a,b\n1,2\n", delimiter=":")
        self.assert_value_error(mode="to_json", csv_text="a,b\n1,2\n", delimiter=";;")
        self.assert_value_error(mode="to_json", csv_text="a,b\n1,2\n", delimiter=5)

    def test_invalid_flags(self) -> None:
        self.assert_value_error(mode="to_json", csv_text="a,b\n1,2\n", has_header="yes")
        self.assert_value_error(mode="to_json", csv_text="a,b\n1,2\n", type_inference=1)

    def test_flag_string_forms_accepted(self) -> None:
        result = self.tool.execute(mode="to_json", csv_text="a,b\n1,2\n", has_header="false")
        self.assertFalse(result["has_header"])
        result = self.tool.execute(mode="to_json", csv_text="a,b\n1,2\n", type_inference="false")
        self.assertFalse(result["type_inference"])

    def test_invalid_key_order(self) -> None:
        self.assert_value_error(mode="to_csv", json_text='[{"a":1}]', key_order="b")  # not a JSON array
        self.assert_value_error(mode="to_csv", json_text='[{"a":1}]', key_order=[1, 2])  # entries must be strings
        self.assert_value_error(mode="to_csv", json_text='[{"a":1}]', key_order='["zzz"]')  # unknown key
        self.assert_value_error(mode="to_csv", json_text='[{"a":1}]', key_order=5)

    def test_invalid_json_returns_structured_error(self) -> None:
        result = self.tool.execute(mode="to_csv", json_text="not json")
        self.assertEqual(result["mode"], "to_csv")
        self.assertEqual(result["error"]["type"], "invalid_json")
        self.assertIn("not valid JSON", result["error"]["message"])

    def test_non_array_or_non_object_records(self) -> None:
        for bad in ('{"a": 1}', "[1, 2]", '["a", {"b": 1}]', '"text"', "3"):
            result = self.tool.execute(mode="to_csv", json_text=bad)
            self.assertEqual(result["error"]["type"], "invalid_records", bad)

    def test_nul_byte_treated_as_ordinary_character(self) -> None:
        # The stdlib reader does not reject NUL; it parses as a character.
        result = self.tool.execute(mode="to_json", csv_text="a,b\n1,\x00\n")
        self.assertEqual(json.loads(result["result"]), [{"a": 1, "b": "\x00"}])


class CsvJsonImportTest(unittest.TestCase):
    """The package export and the module class are the same object."""

    def test_package_export(self) -> None:
        self.assertIs(CsvJsonTool, DirectCsvJsonTool)
        tool = CsvJsonTool()
        self.assertEqual(tool.name, "csv_json_tool")
        self.assertIn("to_json", tool.description)


if __name__ == "__main__":
    unittest.main()
