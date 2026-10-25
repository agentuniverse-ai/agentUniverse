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


class JqLiteSelfReviewRegressionTest(unittest.TestCase):
    """Regressions found by hostile differential probing against jq 1.7.1.

    Each test pins a behaviour where the tool previously disagreed with the
    real jq binary (jq is the specification here).
    """

    def setUp(self):
        self.tool = JqLiteTool()

    def _run(self, query, json_text):
        return self.tool.execute(mode="execute", query=query, json_text=json_text)

    def _assert_matches_jq(self, query, json_text):
        returncode, lines, core = run_jq(query, json_text)
        result = self._run(query, json_text)
        if returncode == 0:
            self.assertEqual(result.get("status"), "success", result)
            self.assertEqual(result.get("outputs"), lines)
        else:
            self.assertEqual(result.get("status"), "error", result)
            self.assertEqual(result.get("error_type"), "jq_error", result)
            self.assertEqual(result.get("message"), core)
            self.assertEqual(result.get("outputs"), lines)

    # -- surrogate pairs in query string literals ---------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_surrogate_pairs_in_query_literals(self):
        cases = [
            ('"\\ud83d\\ude00"', "null", ['"\U0001F600"']),
            ('["\\ud83d\\ude00"]', "null", ['["\U0001F600"]']),
            ('"a\\ud83d\\ude00b"', "null", ['"a\U0001F600b"']),
            ('"\\ud83d\\udc00\\ud83d\\udc00"', "null", ['"\U0001F400\U0001F400"']),
            ('"\\ude00\\ud83d\\ude00"', "null", ['"\ufffd\U0001F600"']),
            ('"\\ude00 alone"', "null", ['"\ufffd alone"']),
            ('.["\\ud83d\\ude00"]', '{"\\ud83d\\ude00": 1}', ["1"]),
        ]
        for query, json_text, expected in cases:
            with self.subTest(query=query):
                self._assert_matches_jq(query, json_text)
                self.assertEqual(self._run(query, json_text)["outputs"], expected)

    def test_lone_high_surrogate_literal_is_parse_error(self):
        for query in ('"\\ud83d"', '"\\ud83d\\ud83d"', '"\\ud83dx"', '"\\ud83d\\u0041"'):
            with self.subTest(query=query):
                result = self.tool.execute(mode="execute", query=query, json_text="null")
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["error_type"], "parse_error")
                self.assertIn("surrogate pair", result["message"])

    # -- surrogate escapes inside the JSON input -----------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_surrogates_in_json_input(self):
        for json_text in ('"\\ud83d\\ude00"', '"\\ude00 lone"', '{"\\ude00": 1}'):
            with self.subTest(input=json_text):
                self._assert_matches_jq(".", json_text)
        # jq rejects these with a parse error; the tool maps input problems
        # to its json_error classification (documented mapping).
        for bad in ('"\\ud800"', '"\\ud83d\\ud83d"', '"\\ud83dx"', '{"\\ud800": 1}', '{"a": "\\ud800"}'):
            with self.subTest(input=bad):
                returncode, _lines, _core = run_jq(".", bad)
                self.assertNotEqual(returncode, 0)
                result = self._run(".", bad)
                self.assertEqual(result["status"], "error", result)
                self.assertEqual(result["error_type"], "json_error", result)
                self.assertIn("surrogate pair", result["message"])

    def test_lone_high_surrogate_input_is_json_error(self):
        result = self._run(".", '"\\ud800"')
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "json_error")
        self.assertIn("surrogate pair", result["message"])

    # -- NaN / Infinity inputs ----------------------------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_nan_and_infinity_inputs(self):
        cases = [
            (".", "NaN"),
            (".", '{"a": NaN}'),
            (".", "Infinity"),
            (".", '{"a": -Infinity}'),
            (".", "[NaN, Infinity]"),
            ("type", "NaN"),
            (". == .", "NaN"),
            (". == 1", "NaN"),
            ("1 == .", "NaN"),
            (". < 1", "NaN"),
            ("1 < .", "NaN"),
            (". < .", "NaN"),
            ("[.] == [.]", "NaN"),
            ("sort", "[1, NaN, -5]"),
            ("unique", "[NaN, NaN, 1]"),
            ("min", "[1, NaN, -5]"),
            ("max", "[1, NaN, -5]"),
            ("length", "NaN"),
            ("length", "Infinity"),
            ("add", "[NaN, 1]"),
            ('join(",")', "[NaN]"),
            ("keys", "NaN"),
        ]
        for query, json_text in cases:
            with self.subTest(query=query, input=json_text):
                self._assert_matches_jq(query, json_text)

    # -- computed double formatting (g_fmt rule) ------------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_computed_double_formatting_matches_jq(self):
        literals = [
            "1e14", "1e15", "1.5e15", "1.234567890123456e15", "9e15", "9.9e15",
            "1e16", "1.1e16", "1.2e16", "1.5e16", "1.23e16", "1.2345678901234567e16",
            "1e17", "1.5e17", "1.23e17", "1e18", "1e20", "1e21", "1e100",
            "123456789012345678", "1234567890123456789", "12345678901234567890",
            "9007199254740993", "18446744073709551616",
            "1.7976931348623157e308", "5e-324", "2.2250738585072014e-308",
            "1e-1", "1e-4", "1e-5", "1.5e-5", "1.23e-5", "1e-6", "1e-7", "1.5e-7", "1.23e-8",
            "0.0001", "0.000015", "0.00015", "0.1", "3.141592653589793",
            "123456789.123456789", "0.30000000000000004", "-1.5e16", "-1e-7", "-0.0", "-0",
        ]
        for literal in literals:
            with self.subTest(literal=literal):
                self._assert_matches_jq("length", literal)
                self._assert_matches_jq(".", literal)

    # -- DEL and control-character string escaping ---------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_del_character_escaped_like_jq(self):
        for json_text in ('"\\u007f"', '"del\\u007fchar"', '["\\u0001\\u001f\\u007f"]', '"\\b\\f\\n\\r\\t\\u0000"'):
            with self.subTest(input=json_text):
                self._assert_matches_jq(".", json_text)

    # -- min/max/sort_by/unique on objects ------------------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_min_max_sort_by_unique_on_objects_error_like_jq(self):
        cases = [
            ("min", '{"a":3,"b":1}'),
            ("max", '{"a":3,"b":1}'),
            ("min", "{}"),
            ("sort_by(.)", '{"a":2,"b":1}'),
            ("sort_by(.x)", '{"a":2,"b":1}'),
            ("unique", '{"a":1}'),
            ("unique", '{"a":1,"b":2,"c":3}'),
        ]
        for query, json_text in cases:
            with self.subTest(query=query, input=json_text):
                self._assert_matches_jq(query, json_text)

    # -- object keys: keywords, logic words, string shorthand -----------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_object_keyword_and_string_keys(self):
        cases = [
            ("{and: 1}", "null", ['{"and":1}']),
            ("{or: 1}", "null", ['{"or":1}']),
            ("{null: 1, false: 2}", "null", ['{"null":1,"false":2}']),
            ("{true: .a}", '{"a": 5}', ['{"true":5}']),
            ("{and}", "null", ['{"and":null}']),
            ("{or}", "null", ['{"or":null}']),
            ("{true}", '{"true": 9}', ['{"true":9}']),
            ('{"a b"}', '{"a b": 3}', ['{"a b":3}']),
            ('{a, "b"}', '{"a":1,"b":2}', ['{"a":1,"b":2}']),
            ("{a: 1, and: 2}", "null", ['{"a":1,"and":2}']),
        ]
        for query, json_text, expected in cases:
            with self.subTest(query=query):
                self._assert_matches_jq(query, json_text)
                self.assertEqual(self._run(query, json_text)["outputs"], expected)
        # canonical queries stay re-parseable (transpile_check round trip)
        for query, _json, _expected in cases:
            with self.subTest(round_trip=query):
                result = self.tool.execute(mode="transpile_check", query=query)
                self.assertTrue(result["valid"], result)
                self.assertTrue(result["round_trip"], result)

    # -- join(null) concatenates without a separator --------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_join_null_and_empty_separator(self):
        cases = [
            ("join(null)", '["a","b"]', ['"ab"']),
            ("join(null)", '["a"]', ['"a"']),
            ("join(null)", "[]", ['""']),
            ("join(null)", '[null,"b"]', ['"b"']),
            ("join(null)", "[1,2]", ['"12"']),
            ("join(empty)", '["a","b"]', []),
        ]
        for query, json_text, expected in cases:
            with self.subTest(query=query, input=json_text):
                self._assert_matches_jq(query, json_text)
                self.assertEqual(self._run(query, json_text).get("outputs"), expected)

    # -- postfix '?' after builtin calls and constructions --------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_postfix_question_after_calls(self):
        cases = [
            ("add?", '{"a":1}', ["1"]),
            ("keys?", "[1]", ["[0]"]),
            ('join(",")?', "[1,2,3]", ['"1,2,3"']),
            ("length?", "5", ["5"]),
            ("unique?", "[1,1]", ["[1]"]),
            ("[.a]?", "5", []),
        ]
        for query, json_text, expected in cases:
            with self.subTest(query=query, input=json_text):
                self._assert_matches_jq(query, json_text)
                self.assertEqual(self._run(query, json_text)["outputs"], expected)

    # -- redundant '.' before index/iterate brackets ---------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_dotted_bracket_forms(self):
        cases = [
            (".a.[1]", '{"a":[1,2,3]}', ["2"]),
            (".a.[]", '{"a":[1,2,3]}', ["1", "2", "3"]),
            (".a.[1]?", '{"a":5}', []),
        ]
        for query, json_text, expected in cases:
            with self.subTest(query=query):
                self._assert_matches_jq(query, json_text)
                self.assertEqual(self._run(query, json_text)["outputs"], expected)
        # jq (and the tool) reject a slice in the dotted-bracket position
        result = self._run(".a.[1:2]", '{"a":[1,2,3]}')
        self.assertEqual(result["status"], "error")
        jq_rc, _lines, _core = run_jq(".a.[1:2]", '{"a":[1,2,3]}')
        self.assertNotEqual(jq_rc, 0)

    # -- object construction streams partial outputs ---------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_object_construction_partial_outputs_before_error(self):
        doc = '{"list": [3, 1, 2], "flag": false, "name": "x"}'
        for query in ('{"c": .[][-1]}', '{"foo": .c, c: .[][-1]}'):
            with self.subTest(query=query):
                self._assert_matches_jq(query, doc)
        result = self._run('{"foo": .c, c: .[][-1]}', doc)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "jq_error")
        self.assertEqual(result["outputs"], ['{"foo":null,"c":2}'])

    # -- deep documents get correctly-labelled errors ---------------------------
    def test_deep_json_error_labels(self):
        deep = "[" * 5000 + "1" + "]" * 5000
        result = self._run(".", deep)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "json_error")
        self.assertIn("nesting is too deep", result["message"])
        deep2 = "[" * 500 + "1" + "]" * 500
        result = self._run(".[]?" * 100, deep2)
        self.assertEqual(result["status"], "error")
        self.assertIn(result["error_type"], ("resource_limit", "json_error"))
        self.assertIn("nesting is too deep", result["message"])


# ---------------------------------------------------------------------------
# Second-pass hostile review battery (fresh seeds, wider grammar)
# ---------------------------------------------------------------------------

_WIDE_KEYS = ["a", "b", "c", "name", "x", "id", "val", "key with space", "键", "A", "Z", "é", "ü"]
_WIDE_LITS = ["0", "1", "2", "3", "-1", "true", "false", "null", '"s"', '"aa"', "1.0", "2.50", "1e2", "1e-4"]


def _gen_wide_value(rnd, depth=3):
    kinds = ["int", "str", "bool", "null", "neg"]
    if depth > 0:
        kinds += ["obj", "arr", "obj", "arr"]
    kind = rnd.choice(kinds)
    if kind == "int":
        return rnd.choice([0, 1, 2, 3, 7, 42])
    if kind == "neg":
        return rnd.choice([-1, -3, -10])
    if kind == "str":
        return rnd.choice(["hello", "", "值", "é", "a b", 'q"s', "tab\there"])
    if kind == "bool":
        return rnd.choice([True, False])
    if kind == "null":
        return None
    if kind == "obj":
        keys = rnd.sample(_WIDE_KEYS, rnd.randint(0, 4))
        return {key: _gen_wide_value(rnd, depth - 1) for key in keys}
    return [_gen_wide_value(rnd, depth - 1) for _ in range(rnd.randint(0, 5))]


def _gen_wide_query(rnd, tag, depth=2):  # noqa: C901
    """Generate an in-subset query over the widened grammar (fresh shapes)."""
    if tag == "obj":
        choices = ["nestedobj", "field", "altchain", "sel", "objkey", "dupkey",
                   "unicode_keys", "optalt", "deepcompact", "keys"]
    elif tag == "arr":
        choices = ["slice", "idx", "sel", "map_sel", "altchain", "arr3",
                   "deepcompact", "join", "firstlast", "cartesian3", "nestedobj"]
    else:
        choices = ["cmp", "altchain", "lits"]
    if depth <= 0:
        choices = ["field", "idx"] if tag != "scalar" else ["lits"]
    choice = rnd.choice(choices)
    key = rnd.choice(_WIDE_KEYS)
    if choice == "nestedobj":
        multi = rnd.choice([f"({rnd.choice(_WIDE_LITS)}, {rnd.choice(_WIDE_LITS)})", "(., .)", "[.[]?][0:2]"])
        inner2 = "{b: %s, c: %s}" % (multi, multi)
        return rnd.choice([
            "{lvl1: {lvl2: %s}, other: %s}" % (inner2, multi),
            "{a: {b: {c: %s}}}" % multi,
            "{x: %s, y: {z: %s}}" % (multi, multi),
            "{a: (%s, {b: %s})}" % (inner2, multi),
        ])
    if choice == "altchain":
        parts = []
        for _ in range(rnd.randint(2, 4)):
            parts.append(rnd.choice([".a", ".b?", "null", "false", "0", '""', "(.a, .b?)", ".[0]?", "empty"]))
        return " // ".join(parts)
    if choice == "sel":
        lit = rnd.choice(_WIDE_LITS)
        op = rnd.choice(["==", "!=", "<", ">", "<=", ">="])
        return rnd.choice([
            f"select(.{key} {op} {lit})",
            f"select(.{key} != null and .{key} != false)",
            f"select((.{key}, .{rnd.choice(['a', 'b'])}) | not)",
            f"select(.{key} == null // false)",
            f"select(.{key}? // false)",
            f"select((.{key} == {lit}) or (.{key} == {rnd.choice(_WIDE_LITS)}))",
        ])
    if choice == "map_sel":
        return f"map(select(.{key} != null))"
    if choice == "objkey":
        return rnd.choice([f'{{"{key}": ., x: (.a, .b?)}}', f"{{{key}}}", '{"a b"}', "{true: 1}", "{and: 2}", "{null: .}"])
    if choice == "dupkey":
        return rnd.choice(["{a: .x, a: .y}", "{a: 1, a: (1, 2)}", '{"k": 1, k: 2}'])
    if choice == "unicode_keys":
        return rnd.choice(["keys", "keys_unsorted", ".é"])
    if choice == "optalt":
        return rnd.choice([".a? // 5", "(.a, .b)? // 7", ".[]? // 1", ".a?.b? // .c? // 0", "[.[]?][0] // null"])
    if choice == "deepcompact":
        return rnd.choice(["[[[.]]]", "{a: {b: {c: [[[.]]]}}}", "[[[[.a?]]]]", "{a: [{b: [{c: .}]}]}"])
    if choice == "keys":
        return rnd.choice(["keys", "keys_unsorted"])
    if choice == "slice":
        combos = ["", ":2", "1:", "1:3", ":-1", "-2:", "0:0", "-5:-2", "3:1", "-1:1", "0:-1"]
        return ".[%s]" % rnd.choice(combos)
    if choice == "idx":
        return f".[{rnd.choice([0, 1, 2, 5, -1, -3, -100, 100])}]"
    if choice == "join":
        return rnd.choice(['join(",")', 'join("")', "join(null)"])
    if choice == "firstlast":
        return rnd.choice(["first", "last", "(first, last)", "first // last"])
    if choice == "arr3":
        return rnd.choice(["[.[]?, .[0]?, .[-1]?]", "[., ., .]", "[.[] | (.a?, .b?)]"])
    if choice == "cartesian3":
        return "{a: (1, 2), b: (3, 4), c: (5, 6)}"
    if choice == "cmp":
        return f"{rnd.choice(_WIDE_LITS)} {rnd.choice(['==', '!=', '<', '<=', '>', '>='])} {rnd.choice(_WIDE_LITS)}"
    return rnd.choice(_WIDE_LITS + ["[1, 2.0, 1e2, 1e-4, -0.0]"])


def _gen_wide_pair(rnd):
    """Generate one (query, json_text) pair; JSON text keeps duplicate keys."""
    kind = rnd.choice(["obj", "arr", "arr_obj", "scalar", "dupjson", "unicode"])
    if kind == "obj":
        keys = rnd.sample(_WIDE_KEYS, rnd.randint(1, 5))
        doc, tag = {key: _gen_wide_value(rnd, 2) for key in keys}, "obj"
    elif kind == "arr":
        doc, tag = [_gen_wide_value(rnd, 1) for _ in range(rnd.randint(0, 6))], "arr"
    elif kind == "arr_obj":
        doc, tag = (
            [
                {key: rnd.choice([0, 1, 2, -2, "aa", "", None, True, False])
                 for key in rnd.sample(["a", "b", "c", "name", "x"], rnd.randint(1, 3))}
                for _ in range(rnd.randint(0, 5))
            ],
            "arr",
        )
    elif kind == "dupjson":
        # jq takes the last value for duplicate object keys in the input
        return _gen_wide_query(rnd, "obj", 2), '{"a": 1, "b": 2, "a": 3, "c": {"x": 1, "x": 2}}'
    elif kind == "unicode":
        doc, tag = {"é": 1, "z": 2, "a": 3, "Z": 4, "ü": 5, "A": 6, "中": 7, "€": 8}, "obj"
    else:
        doc, tag = _gen_wide_value(rnd, depth=0), "scalar"
    return _gen_wide_query(rnd, tag, 2), json.dumps(doc, ensure_ascii=False)


# Real-jq constructs the subset deliberately rejects; jq 1.7.1 supports them
# (each entry pairs the query with an input on which the real jq succeeds).
SECOND_PASS_OUT_OF_SUBSET = [
    ("while(false; .)", "null"),
    ("from_entries", '[{"key":"a","value":1}]'),
    ("until(true; .)", "null"),
    ("nan", "null"),
    ("infinite", "null"),
    ("getpath([])", "null"),
    ("tostream", "null"),
    ("tojson", "null"),
    ("ltrimstr(\"\")", '"ab"'),
    ("tostring", "null"),
    ('tonumber', '"5"'),
    ("walk(.)", "null"),
    ("env.PATH", "null"),
    ("builtins", "null"),
    ("input_filename", "null"),
]


class JqLiteSecondPassRegressionTest(unittest.TestCase):
    """Second-pass regressions found by a wider-grammar differential battery."""

    def setUp(self):
        self.tool = JqLiteTool()

    def _run(self, query, json_text):
        return self.tool.execute(mode="execute", query=query, json_text=json_text)

    def _assert_matches_jq(self, query, json_text):
        returncode, lines, core = run_jq(query, json_text)
        result = self._run(query, json_text)
        if returncode == 0:
            self.assertEqual(result.get("status"), "success", result)
            self.assertEqual(result.get("outputs"), lines, result)
        elif "syntax error" in core or "compile error" in core:
            # jq refused to compile the query (e.g. raw unicode identifiers
            # like `.键`); the tool must reject it too, at the parse level.
            self.assertEqual(result.get("status"), "error", result)
            self.assertIn(result.get("error_type"), ("parse_error", "not_in_subset", "validation_error"), result)
        else:
            self.assertEqual(result.get("status"), "error", result)
            self.assertEqual(result.get("error_type"), "jq_error", result)
            self.assertEqual(result.get("message"), core, result)
            self.assertEqual(result.get("outputs"), lines, result)

    # -- '?//' adjacent token: jq's destructuring alternative is rejected ----
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_adjacent_qslashslash_rejected_like_jq(self):
        for query in (".a?//5", ".a?// 5", ".a ?//5", "(.a)?//5", ".a[]?//3", ".a?//empty", ".a?//[1]", ".a?//3 | .b"):
            with self.subTest(query=query):
                returncode, _lines, _core = run_jq(query, "3")
                self.assertNotEqual(returncode, 0, "jq must reject the adjacent ?// token")
                result = self._run(query, "3")
                self.assertEqual(result["status"], "error", result)
                self.assertIn(result["error_type"], ("not_in_subset", "parse_error"), result)
        for query in (".a? //5", ".a ? //5", ".a? // 5", ".a ? // 5"):
            with self.subTest(query=query):
                self._assert_matches_jq(query, "3")

    # -- plain decimal literals are canonicalized (decNumber rule) -----------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_plain_decimal_literals_canonicalized_like_jq(self):
        json_inputs = [
            "0.0000001", "0.000000000000000000001", "0.000001", "0.00001",
            "10.0000001", "0.123456", "99999999999999999999.0",
            "1.000000000000000000000001", "123.4500", "0.10", "100.0", "0.0", "-0.0",
        ]
        for literal in json_inputs:
            with self.subTest(input=literal):
                self._assert_matches_jq(".", literal)
        # positive query literals canonicalize identically
        for query in ("[0.0000001]", "[2.50]", "[123.4500]", "[10.0000001]", "[0.1]", "[100.0]"):
            with self.subTest(query=query):
                self._assert_matches_jq(query, "null")

    # -- zero coefficients keep their written exponent ------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_zero_exponent_literals_like_jq(self):
        literals = [
            "0e2", "0e-2", "0e0", "-0e0", "-0e2", "-0e-2",
            "0.0e1", "0.0e0", "0.0e-1", "-0.0e-1", "0.00", "-0.00", "0.000", "0e-0", "-0e-0",
        ]
        for literal in literals:
            with self.subTest(input=literal):
                self._assert_matches_jq(".", literal)
                self._assert_matches_jq("[" + literal + "]", "null")
        self.assertEqual(self._run(".", "0e2")["outputs"], ["0E+2"])
        self.assertEqual(self._run(".", "0e-2")["outputs"], ["0.00"])
        self.assertEqual(self._run(".", "0.0e1")["outputs"], ["0"])
        self.assertEqual(self._run(".", "0.0e0")["outputs"], ["0.0"])
        self.assertEqual(self._run(".", "-0e2")["outputs"], ["-0E+2"])

    # -- negative query literals are computed doubles (unary minus) -----------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_negative_query_literals_are_computed_doubles(self):
        cases = [
            ("[-0.0]", ["[-0]"]),
            ("[-2.50]", ["[-2.5]"]),
            ("[-1e2]", ["[-100]"]),
            ("[-1.0]", ["[-1]"]),
            ("[-123.4500]", ["[-123.45]"]),
            ("[-1e16]", ["[-1e+16]"]),
            ("[-1e-5]", ["[-1e-05]"]),
            ("[-0]", ["[-0]"]),
            ("[-0.1e1]", ["[-1]"]),
            ("[-0.0000001]", ["[-1e-07]"]),
            ("[1, -2.50, 3]", ["[1,-2.5,3]"]),
            ("[-1, -2]", ["[-1,-2]"]),
            ("select(.a < -1)", ['{"a":-2}']),
        ]
        for query, expected in cases:
            with self.subTest(query=query):
                self._assert_matches_jq(query, '{"a": -2}' if "select" in query else "null")
                self.assertEqual(self._run(query, '{"a": -2}' if "select" in query else "null")["outputs"], expected)
        # JSON-input negatives stay canonical literals (not computed)
        json_cases = [
            ("-1e2", ["-1E+2"]),
            ("-1e21", ["-1E+21"]),
            ("-1.5e2", ["-1.5E+2"]),
            ("-2.5e-3", ["-0.0025"]),
            ("-0.0", ["-0.0"]),
            ("-2.50", ["-2.50"]),
        ]
        for literal, expected in json_cases:
            with self.subTest(input=literal):
                self._assert_matches_jq(".", literal)
                self.assertEqual(self._run(".", literal)["outputs"], expected)

    # -- has() on null input is false, not an error ----------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_has_on_null_input_is_false(self):
        cases = [
            ('has("a")', "null", ["false"]),
            ("has(0)", "null", ["false"]),
            ("has(true)", "null", ["false"]),
            ("has(null)", "null", ["false"]),
            ('has("a")', '{"a": 1}', ["true"]),
            ('has("a")', "3", ["Cannot check whether number has a string key"]),
        ]
        for query, json_text, expected in cases:
            with self.subTest(query=query, input=json_text):
                self._assert_matches_jq(query, json_text)
                outputs = self._run(query, json_text)
                if outputs["status"] == "success":
                    self.assertEqual(outputs["outputs"], expected)
                else:
                    self.assertEqual(outputs["message"], expected[0])

    # -- wider grammar battery: 600 fresh seeded pairs vs the oracle ----------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_oracle_wider_grammar_corpus_600(self):
        rnd = random.Random(777001)  # noqa: S311 (deterministic corpus)
        for index in range(600):
            query, json_text = _gen_wide_pair(rnd)
            with self.subTest(case=index, query=query, input=json_text[:120]):
                self._assert_matches_jq(query, json_text)

    # -- 150 hostile error-message parities ------------------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_hostile_error_parity_150(self):
        cases = []
        for base in (".a", ".a.b", ".[0]", ".[]", ".[1:2]", ".a[]", ".a[0]", ".a[1:]", ".[:1]", ".a[0:3]"):
            for doc in ("3", '"s"', "true", "false", "null", "[]", "{}", "[1]", '{"a":1}', "1.5", "-0.0", '"中文"', "[[[1]]]"):
                cases.append((base, doc))
        for query in ("keys", "keys_unsorted", "length", "add", "first", "last", "reverse", "sort", "unique",
                      "min", "max", 'join(",")', "join(null)", "join(1)", "has(0)", 'has("a")', "has(null)",
                      "has(true)", "sort_by(.a)", "map(.a)", "select(.a)"):
            for doc in ("3", '"s"', "true", "null", "{}", "[]", '{"a":1}', "[1]", '[1,"a"]', "[[1]]",
                        "[{},[]]", '{"a":{"b":2}}'):
                cases.append((query, doc))
        rnd = random.Random(777003)  # noqa: S311 (deterministic corpus)
        rnd.shuffle(cases)
        for index, (query, json_text) in enumerate(cases[:150]):
            with self.subTest(case=index, query=query, input=json_text):
                self._assert_matches_jq(query, json_text)

    # -- 150 fresh numeric formatting cases ------------------------------------
    @unittest.skipUnless(JQ_AVAILABLE, "jq binary >= 1.6 required")
    def test_numeric_formatting_150(self):
        literals = [
            "0", "-0", "1", "-1", "42", "-42", "1000", "1024", "65535", "65536", "1048576",
            "9007199254740991", "9007199254740992", "9007199254740993", "123456789012345678",
            "-123456789012345678", "123456789012345678901234567890",
            "0.0", "-0.0", "1.0", "0.1", "0.5", "1.5", "2.50", "3.14159", "123.456",
            "1e2", "1e16", "1.5e16", "1e-4", "1e-5", "1e-7", "1e100", "1e-100", "1e308", "1e-308",
            "1.7976931348623157e308", "5e-324", "1e309", "-1e309", "0.000001", "0.0000001",
            "0.000000000000000000001", "12345678901234567890", "1.0e2", "1000000000000000000000",
            "0e2", "0e-2", "0.0e1", "0.0e0", "-0e2", "-0e-2", "0.1e1", "1.0e-5", "0.5e-6",
            "12.34e-8", "123.4500", "0.10", "10.0000001", "-1e2", "-1.5e2", "-2.5e-3",
            "1234567890123456.0", "12345678901234567.0", "0.30000000000000004",
            "7", "-7", "99", "-99", "123456", "-123456", "999999999", "1000000000",
            "0.25", "0.75", "-0.25", "-0.75", "2.0", "-2.0", "10.5", "-10.5", "100.50",
            "1e1", "1e3", "1e6", "1e9", "1e12", "2e16", "9e15", "9.9e15", "1.1e16", "1.23e16",
            "1e17", "1.5e17", "1e18", "1e20", "1e21", "1e22", "1e-1", "1e-2", "1e-3", "1.5e-4",
            "1.23e-5", "1e-6", "1.5e-7", "1.23e-8", "1e-9", "1e-20", "1e-100", "1e-200",
            "2.2250738585072014e-308", "4.9e-324", "1.1e308", "1.5e308", "-1e308",
            "0.001", "0.0001", "0.00001", "0.000000000001", "20.25", "-20.25",
            "1.0000000000000002", "0.9999999999999999", "-1.0000000000000002",
            "3.0e5", "7.5e-2", "-7.5e-2", "1e5", "1e-5", "1.5e-5",
            "12345.6789", "-12345.6789", "99999999.99999999", "0.1234567890123456789",
            "5000000000000000000000", "-5000000000000000000000", "1.23e45", "-1.23e-45",
        ]
        self.assertGreaterEqual(len(literals), 125)
        computed = [
            ("length", "[1]"),
            ("3 | length", "null"),
            ("-3 | length", "null"),
            ("1e300 | length", "null"),
            ("123456789012345678 | length", "null"),
            ("-123456789012345678 | length", "null"),
            ("0.5 | length", "null"),
            ("-0.0 | length", "null"),
            ("1e-320 | length", "null"),
            ("9007199254740993 | length", "null"),
            ("1e15 | length", "null"),
            ("1e16 | length", "null"),
            ("1.5e16 | length", "null"),
            ("[.[0]] | add", "[1]"),
            (".[0] | length", "[1e300]"),
            ("[.[0], .[1]] | add", "[1e308, 1]"),
            ("[.[0], .[1]] | add", "[0.1, 0.2]"),
            ("[.[0], .[1]] | add", "[1, 2.5]"),
            ("[.[0], .[1]] | unique", "[1, NaN]"),
            ("[.[0], .[1]] | min", "[NaN, 1]"),
            ("[.[0], .[1]] | max", "[NaN, 1]"),
            ("[.[0], .[1]] | sort", "[NaN, 1]"),
            ("[.[0], .[1], .[2]] | add", "[0.1, 0.1, 0.1]"),
            ("add", "[1e308, -1e308, 1]"),
            ("add", "[1, 2, 3.0, 4.50]"),
        ]
        checked = 0
        for literal in literals:
            with self.subTest(input=literal):
                self._assert_matches_jq(".", literal)
                checked += 1
        for query, doc in computed:
            with self.subTest(query=query, input=doc):
                self._assert_matches_jq(query, doc)
                checked += 1
        self.assertGreaterEqual(checked, 150)

    # -- 200k-element iteration stays bounded and truncates ---------------------
    def test_two_hundred_thousand_elements_bounded(self):
        big = "[" + ",".join(str(i % 10) for i in range(200000)) + "]"
        self.assertLess(len(big.encode()), self.tool.max_input_bytes)
        result = self._run(".[]", big)
        self.assertEqual(result["status"], "success", result)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["output_count"], self.tool.max_outputs)
        result = self._run("[.[]] | length", big)
        self.assertEqual(result["status"], "success", result)
        self.assertEqual(result["outputs"], ["200000"])
        result = self._run("add", big)
        self.assertEqual(result["status"], "success", result)

    # -- second-pass out-of-subset pins (jq supports, tool rejects) -------------
    def test_second_pass_out_of_subset_pins(self):
        for query, json_text in SECOND_PASS_OUT_OF_SUBSET:
            with self.subTest(query=query):
                returncode, _lines, _core = run_jq(query, json_text)
                self.assertEqual(returncode, 0, "oracle table entries must be real jq constructs")
                result = self.tool.execute(mode="execute", query=query, json_text=json_text)
                self.assertEqual(result["status"], "error", result)
                self.assertEqual(result["error_type"], "not_in_subset", result)
                validate = self.tool.execute(mode="validate", query=query)
                self.assertTrue(validate["valid"] is False, validate)
                self.assertEqual(validate["unsupported_constructs"][0]["construct"], "function call")


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
