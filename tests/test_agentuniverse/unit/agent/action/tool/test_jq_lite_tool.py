"""Unit tests for JqLiteTool.

The semantic batteries use the REAL jq binary as the oracle: outputs must
match `jq -c` line by line (including jq's number formatting and key order),
and evaluation errors must mirror jq's exact error text.  The jq-dependent
tests are skipped when no jq >= 1.6 binary is available; every other test
runs with the standard library alone.
"""

import asyncio
import json
import os
import random
import re
import shutil
import subprocess
import time
import unittest

from agentuniverse.agent.action.tool.common_tool import jq_lite_tool as jq_lite_module
from agentuniverse.agent.action.tool.common_tool.jq_lite_tool import JqLiteTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(jq_lite_module.__file__), "jq_lite_tool.yaml")


def _jq_version():
    binary = shutil.which("jq")
    if not binary:
        return None
    try:
        output = subprocess.run([binary, "--version"], capture_output=True, timeout=10)  # noqa: S603
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = re.search(rb"jq-(\d+)\.(\d+)", output.stdout)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


JQ_VERSION = _jq_version()
JQ_AVAILABLE = JQ_VERSION is not None and JQ_VERSION >= (1, 6)
JQ_BINARY = shutil.which("jq") or "jq"


def run_jq(query, json_text):
    """Run the real jq binary; return (returncode, stdout lines, core error)."""
    process = subprocess.run(  # noqa: S603 (fixed jq binary, no shell)
        [JQ_BINARY, "-c", query],
        input=json_text.encode("utf-8"),
        capture_output=True,
        timeout=30,
    )
    lines = process.stdout.decode("utf-8", errors="replace").splitlines()
    stderr = process.stderr.decode("utf-8", errors="replace")
    core = ""
    for prefix in ("jq: error (at <stdin>:0): ", "jq: error (at <stdin>:1): ", "jq: error: "):
        if stderr.startswith(prefix):
            core = stderr[len(prefix) :].splitlines()[0]
            break
    if not core and stderr:
        core = stderr.splitlines()[0]
    return process.returncode, lines, core


# ---------------------------------------------------------------------------
# Seeded generators for the differential corpus (subset grammar x JSON corpus)
# ---------------------------------------------------------------------------

KEYS = ["a", "b", "c", "name", "x", "id", "val"]
STRINGS = ["hello", "", "值", "a b", 'quote"s', "tab\there", "é"]
INTS = [0, 1, 2, 3, 7, -1, -3, 42]
FLOAT_LEXEMES = ["1.0", "2.50", "0.5", "3.5", "1e2", "1e-4", "1.50e1", "10.0", "-0.5"]
NUM_LITERALS = ["0", "1", "2", "3", "5", "10", "-1", "-2", "true", "false", "null", '"s"', '"aa"', "1.0", "2.50"]


def gen_value(rnd, depth=3, prefer=None):
    kinds = ["int", "float", "str", "bool", "null"]
    if depth > 0:
        kinds += ["obj", "arr", "obj", "arr"]
    if prefer:
        kinds = [prefer]
    kind = rnd.choice(kinds)
    if kind == "int":
        return rnd.choice(INTS)
    if kind == "float":
        return json.loads(rnd.choice(FLOAT_LEXEMES))
    if kind == "str":
        return rnd.choice(STRINGS)
    if kind == "bool":
        return rnd.choice([True, False])
    if kind == "null":
        return None
    if kind == "obj":
        keys = rnd.sample(["a", "b", "c", "name", "x", "val", "key with space", "键"], rnd.randint(0, 4))
        return {key: gen_value(rnd, depth - 1) for key in keys}
    return [gen_value(rnd, depth - 1) for _ in range(rnd.randint(0, 5))]


def gen_arr_of_obj(rnd):
    rows = []
    for _ in range(rnd.randint(0, 5)):
        row = {}
        for key in rnd.sample(["a", "b", "c", "name", "x", "val"], rnd.randint(1, 4)):
            roll = rnd.random()
            if roll < 0.5:
                row[key] = rnd.choice([0, 1, 2, 3, 10, -2, 7])
            elif roll < 0.7:
                row[key] = rnd.choice(["aa", "bb", "cc", ""])
            elif roll < 0.85:
                row[key] = None
            else:
                row[key] = rnd.choice([True, False])
        rows.append(row)
    return rows


def cmp_expr(rnd, key):
    op = rnd.choice(["==", "!=", "<", "<=", ">", ">="])
    return f".{key} {op} {rnd.choice(NUM_LITERALS)}"


def gen_query(rnd, tag, depth=2):  # noqa: C901
    """Generate a subset query whose expected input kind is `tag`."""
    if tag == "obj":
        choices = [
            "field",
            "field_chain",
            "quoted",
            "bracket_str",
            "opt",
            "keys",
            "has",
            "type",
            "length",
            "alt",
            "objlit",
            "pipe_field",
            "iterate_field",
        ]
    elif tag == "arr_of_obj":
        choices = [
            "iterate",
            "idx",
            "slice",
            "iterate_field",
            "map",
            "sort_by",
            "select_all",
            "first",
            "last",
            "add",
            "arr_collect",
            "unique",
            "minmax",
            "reverse",
            "join",
            "length",
            "iterate_select",
            "objlit",
            "alt_field",
        ]
    elif tag == "arr_scalar":
        choices = [
            "iterate",
            "idx",
            "slice",
            "first",
            "last",
            "add",
            "sort",
            "unique",
            "minmax",
            "reverse",
            "arr_collect",
            "length",
            "alt_field",
            "iterate_alt",
        ]
    elif tag == "arr_str":
        choices = [
            "iterate",
            "idx",
            "slice",
            "join",
            "add",
            "first",
            "last",
            "unique",
            "sort",
            "reverse",
            "arr_collect",
            "length",
        ]
    else:
        choices = ["identity", "type", "length", "lit", "cmp_lit", "alt_lit", "notlit", "empty"]
    if depth <= 0:
        if tag == "obj":
            choices = ["field", "quoted"]
        elif tag in ("arr_of_obj", "arr_scalar", "arr_str"):
            choices = ["iterate", "idx"]
        else:
            choices = ["identity", "type"]
    choice = rnd.choice(choices)
    key = rnd.choice(KEYS)
    second = rnd.choice(KEYS)
    if choice == "identity":
        return "."
    if choice == "field":
        return f".{key}"
    if choice == "field_chain":
        return f".{key}.{second}"
    if choice == "quoted":
        quoted = rnd.choice(['"key with space"', '"键"']) if rnd.random() < 0.5 else f'"{key}"'
        return ".[" + quoted + "]" if rnd.random() < 0.3 else "." + quoted
    if choice == "bracket_str":
        return f'.["{key}"]'
    if choice == "opt":
        return f".{key}?"
    if choice == "keys":
        return "keys"
    if choice == "has":
        return f'has("{key}")'
    if choice == "type":
        return "type"
    if choice == "length":
        return "length"
    if choice == "lit":
        return rnd.choice(NUM_LITERALS)
    if choice == "notlit":
        return ". | not"
    if choice == "empty":
        return "empty"
    if choice == "cmp_lit":
        return f"{rnd.choice(NUM_LITERALS)} {rnd.choice(['==', '!=', '<', '>', '<=', '>='])} {rnd.choice(NUM_LITERALS)}"
    if choice == "alt_lit":
        return f"{rnd.choice(NUM_LITERALS)} // {rnd.choice(NUM_LITERALS)}"
    if choice == "alt_field":
        return f".{key} // {rnd.choice(NUM_LITERALS)}"
    if choice == "iterate":
        return ".[]"
    if choice == "idx":
        return f".[{rnd.choice([0, 1, 2, 5, -1, -3])}]"
    if choice == "slice":
        start, end = rnd.choice([(0, 2), (1, 3), (2, 5), (0, 0), (-2, None), (None, 2), (3, 1), (-5, -2)])
        return f".[{'' if start is None else start}:{'' if end is None else end}]"
    if choice == "iterate_field":
        return f".[] | .{key}?"
    if choice == "iterate_alt":
        return f".[]? | .{key} // {rnd.choice(NUM_LITERALS)}"
    if choice == "iterate_select":
        return f".[] | select({cmp_expr(rnd, key)})"
    if choice == "select_all":
        return f".[] | select({cmp_expr(rnd, key)})"
    if choice == "map":
        inner = rnd.choice([f".{key}", f".{key}?", f"(.{key}, .{key})", "select(.a != null)"])
        return f"map({inner})"
    if choice == "sort_by":
        return f"sort_by(.{key})"
    if choice == "arr_collect":
        inner = gen_query(rnd, "arr_of_obj" if tag == "arr_of_obj" else "arr_scalar", depth - 1)
        return f"[{inner}]"
    if choice == "first":
        return "first"
    if choice == "last":
        return "last"
    if choice == "add":
        return "add"
    if choice == "unique":
        return "unique"
    if choice == "minmax":
        return rnd.choice(["min", "max"])
    if choice == "reverse":
        return "reverse"
    if choice == "join":
        separator = rnd.choice([",", "-", ";"])
        return 'join("' + separator + '")'
    if choice == "objlit":
        return rnd.choice(
            [
                "{a: ." + key + "}",
                "{" + key + "}",
                '{"k": .' + key + ", b: ." + second + "}",
                "{a: (." + key + ", ." + second + ")}",
                "{a: (." + key + ' // "d")}',
            ]
        )
    if choice == "pipe_field":
        return f"{gen_query(rnd, 'obj', depth - 1)} | .{key}"
    return "."


def gen_pair(rnd):
    """Generate one (query, json_text) pair over the corpus."""
    kind = rnd.choice(["obj", "arr_of_obj", "arr_scalar", "arr_str", "scalar"])
    if kind == "obj":
        doc, tag = gen_value(rnd, prefer="obj"), "obj"
    elif kind == "arr_of_obj":
        doc, tag = gen_arr_of_obj(rnd), "arr_of_obj"
    elif kind == "arr_scalar":
        doc, tag = [gen_value(rnd, depth=0) for _ in range(rnd.randint(0, 6))], "arr_scalar"
    elif kind == "arr_str":
        doc, tag = [rnd.choice(STRINGS) for _ in range(rnd.randint(0, 5))], "arr_str"
    else:
        doc, tag = gen_value(rnd, depth=0), "any"
    return gen_query(rnd, tag, depth=2), json.dumps(doc, ensure_ascii=False)


def gen_multi_output_query(rnd):
    """Generate a comma/iteration composition exercising jq's stream order."""
    key = rnd.choice(KEYS)
    second = rnd.choice(KEYS)
    templates = [
        "(.<k>, .<k2>)",
        ".[] | (., .<k>?)",
        "[.[0], .[1]]",
        "(.[], .<k>?) | .<k2>?",
        ".[] | (.<k>, .<k2>)",
        "[(., .) ]",
        "(.[] | .<k>?, .<k2>?)",
        "(.[]? | select(.<k> != null), .<k2>?)",
        '.[] | .<k>? // "d"',
        "(first, last)",
        "(.[0:2], .[2:]) | (.[]? | .<k>?)",
        '((.<k>, .<k2>) // "d")',
        "map((.<k>, .<k2>))",
        "{a: (1, 2), b: (3, 4)}",
        ".[] | {<k>}",
        "((., .) | .<k>?)",
        "([.[]? | .<k>] , [.[]? | .<k2>] )",
        "(keys, length)",
    ]
    template = rnd.choice(templates)
    query = template.replace("<k>", key).replace("<k2>", second)
    doc_kind = rnd.choice(["obj", "arr_of_obj", "arr_scalar"])
    if doc_kind == "obj":
        doc = gen_value(rnd, prefer="obj")
    elif doc_kind == "arr_of_obj":
        doc = gen_arr_of_obj(rnd)
    else:
        doc = [gen_value(rnd, depth=1) for _ in range(rnd.randint(0, 4))]
    return query, json.dumps(doc, ensure_ascii=False)


# Queries that real jq accepts but this subset deliberately rejects.
# Slice steps predate jq 1.7.1-apple's grammar, so jq itself rejects them too.
NOT_PARSEABLE_BY_OLD_JQ = {".[::2]", ".[1:2:3]", ".[:2:1]"}

OUT_OF_SUBSET = [
    "..",
    ".[..]",
    "[..] | length",
    "reduce .[] as $x (0; .)",
    "reduce .[] as $x (null; .)",
    "foreach .[] as $x (0; .)",
    "def f: .; f",
    "def f(x): x; f(.)",
    "if .a then 1 else 2 end",
    '.a | if . then "t" else "f" end',
    "try .a",
    'try .a catch "x"',
    "label $out | .[]",
    ". as $x | $x",
    ".a as $x | .b",
    "$ENV.PATH",
    "env.HOME",
    "@base64",
    "@text",
    '"x" | @base64d',
    "limit(2; .[])",
    "first(.[])",
    "input",
    "inputs",
    "[inputs]",
    'test("a")',
    'match("a")',
    'capture("a")',
    'sub("a";"b")',
    'gsub("a";"b")',
    'split("a")',
    'getpath(["a", 0])',
    'setpath(["a"]; 1)',
    'delpaths([["a"]])',
    "paths",
    "path(.a)",
    "to_entries",
    "with_entries(.)",
    "tostream",
    "tostring",
    "tonumber",
    "tojson",
    "fromjson",
    "ascii_downcase",
    "ascii_upcase",
    "explode",
    "implode",
    'ltrimstr("a")',
    'rtrimstr("a")',
    'startswith("a")',
    'endswith("a")',
    'contains("a")',
    "inside({})",
    "range(3)",
    "floor",
    "ceil",
    "sqrt",
    "fabs",
    "pow(2; 3)",
    "log",
    "exp",
    "now",
    "todate",
    'strftime("%Y")',
    "walk(.)",
    "until(true; .)",
    "recurse",
    'splits("a")',
    "input_line_number",
    "debug",
    "stderr",
    "$__loc__",
    "halt",
    "halt_error",
    ".a + 1",
    "1 - 2",
    "3 * 4",
    "5 / 2",
    "7 % 3",
    "- .a",
    ".a + .b",
    ".a |= .b",
    ".a = 1",
    ".a += 1",
    '"interp \\(.name) end"',
    '"\\(.)"',
    ".[::2]",
    ".[1:2:3]",
    ".[:2:1]",
    ".a // 3 | .b as $x | $x",
    ".. | numbers",
    "[limit(3; .[])]",
]


class JqLiteToolTest(unittest.TestCase):
    """Unit tests for JqLiteTool modes, caps and subset boundaries."""

    def setUp(self):
        self.tool = JqLiteTool()

    # -- battery (a): 400 seeded pairs vs the real jq oracle -----------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_oracle_seeded_corpus_400(self):
        """Every seeded (query, JSON) pair must match `jq -c` exactly."""
        rnd = random.Random(252)  # noqa: S311 (deterministic test corpus)
        checked = 0
        for index in range(400):
            query, json_text = gen_pair(rnd)
            with self.subTest(case=index, query=query, input=json_text):
                self._assert_matches_jq(query, json_text)
            checked += 1
        self.assertEqual(checked, 400)

    # -- battery (d): 150 multi-output compositions in jq's stream order ----
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_oracle_multi_output_stream_150(self):
        """Comma/iteration compositions must reproduce the full output stream."""
        rnd = random.Random(2520)  # noqa: S311 (deterministic test corpus)
        for index in range(150):
            query, json_text = gen_multi_output_query(rnd)
            with self.subTest(case=index, query=query, input=json_text):
                self._assert_matches_jq(query, json_text)

    def _assert_matches_jq(self, query, json_text):
        returncode, lines, core = run_jq(query, json_text)
        result = self.tool.execute(mode="execute", query=query, json_text=json_text)
        if returncode == 0:
            self.assertEqual(result.get("status"), "success", result)
            self.assertEqual(result["outputs"], lines)
            self.assertEqual(result["output_count"], len(lines))
            self.assertFalse(result["truncated"])
        else:
            self.assertEqual(result.get("status"), "error", result)
            self.assertEqual(result.get("error_type"), "jq_error", result)
            self.assertEqual(result.get("message"), core)
            self.assertEqual(result.get("outputs"), lines)

    # -- battery (c): error semantics and the documented quirks -------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_error_semantics_match_jq(self):
        """Type errors mirror jq's messages; ? and // follow jq exactly."""
        table = [
            (".a", "[1]", 'Cannot index array with string "a"'),
            (".a", '"s"', 'Cannot index string with string "a"'),
            (".a", "3", 'Cannot index number with string "a"'),
            (".a", "true", 'Cannot index boolean with string "a"'),
            (".[0]", "{}", "Cannot index object with number"),
            (".[0]", '"s"', "Cannot index string with number"),
            (".[0]", "3", "Cannot index number with number"),
            (".[0]", "true", "Cannot index boolean with number"),
            (".[1:2]", "{}", "Cannot index object with object"),
            (".[1:2]", "3", "Cannot index number with object"),
            (".[1:2]", "true", "Cannot index boolean with object"),
            (".[]", "null", "Cannot iterate over null (null)"),
            (".[]", '"s"', 'Cannot iterate over string ("s")'),
            (".[]", "3", "Cannot iterate over number (3)"),
            (".[]", "true", "Cannot iterate over boolean (true)"),
            (".a[]", "{}", "Cannot iterate over null (null)"),
            ("length", "true", "boolean (true) has no length"),
            ("keys", '"s"', 'string ("s") has no keys'),
            ("keys", "3", "number (3) has no keys"),
            ('has("a")', "[1]", "Cannot check whether array has a string key"),
            ('has("a")', "3", "Cannot check whether number has a string key"),
            ("has(1)", '{"a":1}', "Cannot check whether object has a number key"),
            ("has(true)", '{"a":1}', "Cannot check whether object has a boolean key"),
            ("sort", '"ab"', 'string ("ab") cannot be sorted, as it is not an array'),
            ("unique", '"ab"', 'Cannot iterate over string ("ab")'),
            ("add", '[1,"a"]', 'number (1) and string ("a") cannot be added'),
            ("add", '"ab"', 'Cannot iterate over string ("ab")'),
            ('join(",")', "[[1]]", 'string ("") and array ([1]) cannot be added'),
            ('join(",")', "3", "Cannot iterate over number (3)"),
            ("min", "3", "number (3) and number (3) cannot be iterated over"),
            ("reverse", '"ab"', "Cannot index string with number"),
        ]
        for query, json_text, expected in table:
            with self.subTest(query=query, input=json_text):
                returncode, lines, core = run_jq(query, json_text)
                self.assertNotEqual(returncode, 0, "oracle table entry must fail in jq")
                self.assertEqual(core, expected)
                result = self.tool.execute(mode="execute", query=query, json_text=json_text)
                self.assertEqual(result["status"], "error", result)
                self.assertEqual(result["error_type"], "jq_error")
                self.assertEqual(result["message"], expected)
                self.assertEqual(result["outputs"], lines)

    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_optional_suppression_matches_jq(self):
        """`?` suppresses only the annotated step, exactly like jq."""
        table = [
            (".a?", "[1]"),
            (".a.b?", "[1]"),
            ("(.a.b)?", "[1]"),
            ("(.a, 1)?", "[1]"),
            ("(1, .a)?", "[1]"),
            (".[]?", "null"),
            (".[0]?", "{}"),
            (".[1:2]?", "{}"),
            (".b[]?", "3"),
            (".a[]?", '{"a":[1]}'),
            (".[]?|.", '[1,{"a":2}]'),
            (".a?.b", '{"a":{"b":1}}'),
            (".a?.b", "[1]"),
            (".b?.c", '{"b":3}'),
            ("[.[] | .a?]", '[1,{"a":2},[3]]'),
            ('.["k"]?', "[1]"),
        ]
        for query, json_text in table:
            with self.subTest(query=query, input=json_text):
                self._assert_matches_jq(query, json_text)

    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_alternative_operator_quirks(self):
        """`//` treats only null/false as falsy; errors still propagate."""
        table = [
            ("false // 5", "null", ["5"]),  # jq quirk: false is falsy for //
            ("null // 5", "null", ["5"]),
            ("0 // 5", "null", ["0"]),  # 0 is truthy
            ('"" // 5', "null", ['""']),
            ("[] // 5", "null", ["[]"]),
            ("{} // 5", "null", ["{}"]),
            ("empty // 5", "null", ["5"]),
            ("(1,2,null,3) // 5", "null", ["1", "2", "3"]),
            ("(null,false) // 5", "null", ["5"]),
            ('.a // "d"', '{"a":false}', ['"d"']),
            ('.a // "d"', '{"a":0}', ["0"]),
            ('(.a, 1) // "d"', '{"a":null}', ["1"]),
        ]
        for query, json_text, expected in table:
            with self.subTest(query=query):
                returncode, lines, _ = run_jq(query, json_text)
                self.assertEqual(returncode, 0)
                self.assertEqual(lines, expected)
                result = self.tool.execute(mode="execute", query=query, json_text=json_text)
                self.assertEqual(result["status"], "success", result)
                self.assertEqual(result["outputs"], expected)
        # Errors on the left side propagate, and outputs already produced stay.
        for query, json_text in [('.a // "d"', "[1]"), ('(.a, 1) // "d"', "[1]"), ('(1, .a) // "d"', "[1]")]:
            with self.subTest(propagates=query):
                self._assert_matches_jq(query, json_text)

    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_partial_outputs_before_error(self):
        """jq prints the partial stream before an error; the tool keeps it."""
        query, json_text = "(1, .a) | .", "[1]"
        returncode, lines, core = run_jq(query, json_text)
        self.assertNotEqual(returncode, 0)
        self.assertEqual(lines, ["1"])
        result = self.tool.execute(mode="execute", query=query, json_text=json_text)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["outputs"], ["1"])
        self.assertEqual(result["message"], core)

    # -- number formatting battery -------------------------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_number_formatting_matches_jq(self):
        """jq 1.7 literal preservation must round-trip exactly."""
        lexemes = [
            "0",
            "-0",
            "1",
            "1.0",
            "1.50",
            "1e2",
            "1E2",
            "1e+02",
            "1e-4",
            "1e-6",
            "1e-7",
            "0.0001",
            "0.5",
            "0.50",
            "2.50",
            "1.5e-6",
            "12e-7",
            "123e-1",
            "1e0",
            "1e1",
            "10e1",
            "100e1",
            "1.5e1",
            "1.5e2",
            "-1e2",
            "-0.0",
            "-0e0",
            "0.0",
            "0.5e1",
            "0.50e1",
            "0.05e1",
            "2.0e0",
            "0e0",
            "9007199254740993",
            "12345678901234567890123",
            "100000000000000000000000000000",
            "3.5",
            "0.1",
            "1e-3",
            "5e-2",
            "2.5e-1",
            "123.456",
            "42",
            "-42",
        ]
        for lexeme in lexemes:
            for query, json_text in [(".", '{"a": ' + lexeme + "}"), (".a", '{"a": ' + lexeme + "}"), (".", lexeme)]:
                with self.subTest(lexeme=lexeme, query=query):
                    self._assert_matches_jq(query, json_text)

    # -- battery (b): outside-subset constructs are rejected, never mis-run --
    def test_subset_boundary_rejection(self):
        """Every out-of-subset construct yields a structured not-in-subset error."""
        for query in OUT_OF_SUBSET:
            with self.subTest(query=query):
                result = self.tool.execute(mode="validate", query=query)
                self.assertEqual(result["status"], "success", result)
                self.assertFalse(result["valid"], query)
                constructs = result.get("unsupported_constructs") or []
                if not constructs:
                    self.fail(f"query {query!r} rejected without a not-in-subset construct: {result}")
                entry = constructs[0]
                self.assertIn(entry["construct"].lower(), json.dumps(entry).lower())
                self.assertTrue(entry["message"])
                executed = self.tool.execute(mode="execute", query=query, json_text="{}")
                self.assertEqual(executed["status"], "error", query)
                self.assertEqual(executed["error_type"], "not_in_subset")

    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_boundary_queries_are_genuine_jq(self):
        """The rejected constructs must really parse in jq (they are jq features)."""
        checked = 0
        for query in OUT_OF_SUBSET:
            if query in NOT_PARSEABLE_BY_OLD_JQ:
                continue
            returncode, _, _ = run_jq(query, "{}")
            with self.subTest(query=query):
                self.assertNotEqual(returncode, 3, f"jq also rejects {query!r}")
            checked += 1
        self.assertGreater(checked, 85)

    # -- validate mode --------------------------------------------------------
    def test_validate_decomposes_pipeline(self):
        result = self.tool.execute(mode="validate", query=".[] | .b | select(.x > 3)")
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["valid"])
        self.assertEqual(result["unsupported_constructs"], [])
        ops = [step["op"] for step in result["steps"]]
        self.assertIn("iterate", ops)
        self.assertIn("field_access", ops)
        self.assertIn("pipe", ops)
        self.assertIn("builtin", ops)
        self.assertIn("compare", ops)
        for step in result["steps"]:
            self.assertIn("op", step)
            self.assertIn("detail", step)
            self.assertIsInstance(step["detail"], str)
        self.assertEqual(result["canonical_query"], ".[] | .b | select(.x > 3)")

    def test_validate_reports_parse_and_subset_failures(self):
        broken = self.tool.execute(mode="validate", query=".a |")
        self.assertFalse(broken["valid"])
        self.assertIn("parse_error", broken)
        outside = self.tool.execute(mode="validate", query="reduce .[] as $x (0; .)")
        self.assertFalse(outside["valid"])
        entry = outside["unsupported_constructs"][0]
        self.assertEqual(entry["construct"], "reduce")
        self.assertGreaterEqual(entry["position"], 0)

    # -- execute mode ----------------------------------------------------------
    def test_execute_outputs_and_trace(self):
        json_text = '[{"a": 1, "b": 2}, {"a": 3, "b": 4}]'
        result = self.tool.execute(mode="execute", query=".[] | .b", json_text=json_text)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["outputs"], ["2", "4"])
        self.assertEqual(result["output_count"], 2)
        self.assertFalse(result["truncated"])
        trace = result["execution_trace"]
        self.assertEqual(trace[0]["stage"], 1)
        self.assertEqual(trace[0]["value_count"], 2)
        self.assertEqual(trace[0]["values"], ['{"a":1,"b":2}', '{"a":3,"b":4}'])
        self.assertEqual(trace[1]["query"], ".b")

    def test_execute_preserves_key_order_and_unicode(self):
        json_text = '{"b": 1, "a": {"键": "值"}, "c": [1.0, 2.50]}'
        result = self.tool.execute(mode="execute", query=".", json_text=json_text)
        self.assertEqual(result["outputs"], ['{"b":1,"a":{"键":"值"},"c":[1.0,2.50]}'])

    def test_execute_truncates_outputs_at_cap(self):
        capped = JqLiteTool(max_outputs=3)
        result = capped.execute(mode="execute", query=".[]", json_text="[1,2,3,4,5]")
        self.assertEqual(result["outputs"], ["1", "2", "3"])
        self.assertTrue(result["truncated"])
        self.assertEqual(result["output_count"], 3)

    def test_execute_rejects_bad_json_and_mode(self):
        result = self.tool.execute(mode="execute", query=".a", json_text="{nope}")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "json_error")
        missing = self.tool.execute(mode="execute", query=".a")
        self.assertEqual(missing["error_type"], "validation_error")
        bad_mode = self.tool.execute(mode="run", query=".")
        self.assertEqual(bad_mode["error_type"], "validation_error")

    def test_execute_requires_strict_json(self):
        """Documented divergence: jq tolerates some invalid JSON; this tool does not."""
        result = self.tool.execute(mode="execute", query=".", json_text="00.1")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "json_error")

    # -- explain mode -----------------------------------------------------------
    def test_explain_walkthrough(self):
        result = self.tool.execute(mode="explain", query=".[] | .b | select(.x > 3)")
        self.assertEqual(result["status"], "success")
        text = result["explanation"]
        self.assertIn('field "b"', text)
        self.assertIn("element or value", text)
        self.assertIn("condition", text)
        deeper = self.tool.execute(mode="explain", query='.a[1:2] // "d"')
        self.assertIn("//", deeper["explanation"])

    # -- transpile_check mode -----------------------------------------------------
    def test_transpile_round_trip_corpus(self):
        rnd = random.Random(99)  # noqa: S311 (deterministic test corpus)
        for _ in range(120):
            query, _json = gen_pair(rnd)
            result = self.tool.execute(mode="transpile_check", query=query)
            self.assertEqual(result["status"], "success", query)
            self.assertTrue(result["valid"], query)
            self.assertTrue(result["round_trip"], f"{query} -> {result.get('canonical_query')}")
        for query in [
            ".",
            ".a",
            ".a.b?",
            '."quoted key"[0]',
            ".[1:]",
            ".[:2]",
            ".[]?",
            "[.[] | .a]",
            '{a: .b, "k": (.x, .y)}',
            "{name}",
            ".a // 5",
            "(.a, .b) | .c",
            "select(.x != null and .y > 3)",
            "map(.a) | sort_by(.b) | first",
            'join(",")',
            "keys_unsorted",
            'has("k")',
            ".a? // false // null",
        ]:
            result = self.tool.execute(mode="transpile_check", query=query)
            self.assertTrue(result["round_trip"], query)
            reparsed = self.tool.execute(mode="transpile_check", query=result["canonical_query"])
            self.assertEqual(reparsed["canonical_query"], result["canonical_query"])
        invalid = self.tool.execute(mode="transpile_check", query="..")
        self.assertFalse(invalid["valid"])
        self.assertEqual(invalid["unsupported_constructs"][0]["construct"], "recursive descent")

    # -- battery (e): pathological inputs and caps -------------------------------
    def test_ten_thousand_elements_under_two_seconds(self):
        payload = json.dumps([{"a": i, "b": "x" * 3} for i in range(10_000)], ensure_ascii=False)
        roomy = JqLiteTool(max_outputs=20_000)
        start = time.monotonic()
        result = roomy.execute(mode="execute", query=".[] | .a", json_text=payload)
        elapsed = time.monotonic() - start
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["output_count"], 10_000)
        self.assertLess(elapsed, 2.0, f"10k-element array took {elapsed:.2f}s")

    def test_one_megabyte_json_is_bounded(self):
        within = JqLiteTool(max_input_bytes=1000)
        ok = within.execute(mode="execute", query=".", json_text="[" + "1," * 400 + "1]")
        self.assertEqual(ok["status"], "success")
        oversized = within.execute(mode="execute", query=".", json_text="[" + "1," * 600 + "1]")
        self.assertEqual(oversized["status"], "error")
        self.assertEqual(oversized["error_type"], "validation_error")
        self.assertIn("max_input_bytes", oversized["message"])

    def test_long_query_chains_rejected_by_node_cap(self):
        chained = "1" + ", 1" * 3_000  # ~6001 AST nodes, under the length cap
        result = self.tool.execute(mode="validate", query=chained)
        self.assertFalse(result["valid"])
        executed = self.tool.execute(mode="execute", query=chained, json_text="null")
        self.assertEqual(executed["error_type"], "validation_error")

    def test_query_length_and_nesting_caps(self):
        too_long = self.tool.execute(mode="validate", query=".a" * 6_000)
        self.assertEqual(too_long["error_type"], "validation_error")
        deep = self.tool.execute(mode="validate", query="(" * 400 + "." + ")" * 400)
        self.assertFalse(deep["valid"])

    def test_empty_and_invalid_queries(self):
        for bad in ["", "   ", 123, None]:
            result = self.tool.execute(mode="validate", query=bad)
            self.assertEqual(result["error_type"], "validation_error")

    def test_config_validation(self):
        bad = JqLiteTool(max_outputs=0)
        result = bad.execute(mode="validate", query=".")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("max_outputs", result["message"])

    def test_async_execute(self):
        result = asyncio.run(self.tool.async_execute(mode="execute", query=".a", json_text='{"a": [1.0, null]}'))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["outputs"], ["[1.0,null]"])

    # -- stream conventions ---------------------------------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_output_per_line_convention(self):
        """Each result is one compact JSON line, exactly jq's serialization."""
        json_text = '{"list": [1, 2, 3], "s": "héllo", "t": true}'
        query = ".list[] | select(. >= 2)"
        _returncode, lines, _ = run_jq(query, json_text)
        result = self.tool.execute(mode="execute", query=query, json_text=json_text)
        self.assertEqual(result["outputs"], lines)
        self.assertEqual(result["outputs"], ["2", "3"])


class JqLiteRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped jq_lite_tool.yaml as a tool component."""

    def setUp(self):
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "JqLiteTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, JqLiteTool)
        self.assertEqual(tool.input_keys, ["mode", "query"])


if __name__ == "__main__":
    unittest.main()
