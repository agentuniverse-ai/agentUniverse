#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_import_graph_tool.py

"""Offline unit tests for ImportGraphTool.

The tool is built purely on the standard library ``ast`` and never
imports, executes or resolves the analyzed code, so this suite runs
fully offline. Every assertion is deterministic: the scan mode is
checked against an exact ground-truth import matrix (plain / dotted /
aliased / multi-alias / redundant-alias imports, from-imports with
multiple and aliased names, relative levels 1 and 2, star imports,
__future__ imports, try/except conditional marking with fallback
roles, bare and tuple except labels, try/finally non-conditionality,
imports nested in if / for / def / class bodies), the deps mode
against the exact stdlib / external / internal classification, the
analyze mode against exact single-file anomaly payloads and exact
multi-file graphs (2-cycle, 3-cycle, SCC-sharing merged cycle,
self-loop singleton cycle, orphans, `from . import x` sibling
resolution, edge deduplication), the to_dot mode against exact DOT
source strings (dashed cycle edges, dotted cycle nodes, graph-name
sanitization with the reported id_mapping), and the error matrix
covers every strict-validation branch.
"""

import asyncio
import unittest

from agentuniverse.agent.action.tool.common_tool import ImportGraphTool
from agentuniverse.agent.action.tool.common_tool.import_graph_tool import (
    ImportGraphTool as DirectImportGraphTool,
)


class ImportGraphToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib ImportGraphTool."""

    def setUp(self) -> None:
        self.tool = ImportGraphTool()

    def _expect_value_error(self, fragment: str, **kwargs) -> None:
        """Assert execute raises ValueError whose message contains fragment."""
        with self.assertRaises(ValueError) as caught:
            self.tool.execute(**kwargs)
        self.assertIn(fragment, str(caught.exception))

    # ------------------------------------------------------------------ #
    # scan mode — exact ground-truth import matrix
    # ------------------------------------------------------------------ #

    def test_scan_import_matrix_exact(self) -> None:
        source = (
            "from __future__ import annotations\n"      # 1 future
            "import os\n"                               # 2 plain
            "import os.path as osp\n"                   # 3 aliased
            "import sys, json\n"                        # 4 multi-alias
            "from collections import OrderedDict as OD, defaultdict\n"  # 5
            "from . import sibling\n"                   # 6 rel level1 bare
            "from .mod import thing\n"                  # 7 rel level1
            "from ..pkg.mod import other\n"             # 8 rel level2
            "from badmodule import *\n"                 # 9 star
            "import json as json\n"                     # 10 redundant alias
        )
        self.assertEqual(
            self.tool.execute(mode="scan", source=source),
            {
                "mode": "scan",
                "import_count": 11,
                "imports": [
                    {
                        "module": "__future__",
                        "names": ["annotations"],
                        "aliases": {},
                        "level": 0,
                        "line": 1,
                        "is_star": False,
                        "is_future": True,
                        "conditional": None,
                    },
                    {
                        "module": "os",
                        "names": ["os"],
                        "aliases": {},
                        "level": 0,
                        "line": 2,
                        "is_star": False,
                        "is_future": False,
                        "conditional": None,
                    },
                    {
                        "module": "os.path",
                        "names": ["osp"],
                        "aliases": {"os.path": "osp"},
                        "level": 0,
                        "line": 3,
                        "is_star": False,
                        "is_future": False,
                        "conditional": None,
                    },
                    {
                        "module": "sys",
                        "names": ["sys"],
                        "aliases": {},
                        "level": 0,
                        "line": 4,
                        "is_star": False,
                        "is_future": False,
                        "conditional": None,
                    },
                    {
                        "module": "json",
                        "names": ["json"],
                        "aliases": {},
                        "level": 0,
                        "line": 4,
                        "is_star": False,
                        "is_future": False,
                        "conditional": None,
                    },
                    {
                        "module": "collections",
                        "names": ["OD", "defaultdict"],
                        "aliases": {"OrderedDict": "OD"},
                        "level": 0,
                        "line": 5,
                        "is_star": False,
                        "is_future": False,
                        "conditional": None,
                    },
                    {
                        "module": "",
                        "names": ["sibling"],
                        "aliases": {},
                        "level": 1,
                        "line": 6,
                        "is_star": False,
                        "is_future": False,
                        "conditional": None,
                    },
                    {
                        "module": "mod",
                        "names": ["thing"],
                        "aliases": {},
                        "level": 1,
                        "line": 7,
                        "is_star": False,
                        "is_future": False,
                        "conditional": None,
                    },
                    {
                        "module": "pkg.mod",
                        "names": ["other"],
                        "aliases": {},
                        "level": 2,
                        "line": 8,
                        "is_star": False,
                        "is_future": False,
                        "conditional": None,
                    },
                    {
                        "module": "badmodule",
                        "names": ["*"],
                        "aliases": {},
                        "level": 0,
                        "line": 9,
                        "is_star": True,
                        "is_future": False,
                        "conditional": None,
                    },
                    {
                        "module": "json",
                        "names": ["json"],
                        "aliases": {},
                        "level": 0,
                        "line": 10,
                        "is_star": False,
                        "is_future": False,
                        "conditional": None,
                    },
                ],
                "conditional_blocks": [],
                "conditional_block_count": 0,
            },
        )

    def test_scan_relative_future_is_not_future_flag(self) -> None:
        # A `from .__future__ import x` is a relative import of a
        # module literally named __future__ — not the future contract.
        result = self.tool.execute(
            mode="scan", source="from .__future__ import x\n"
        )
        record = result["imports"][0]
        self.assertEqual(record["module"], "__future__")
        self.assertEqual(record["level"], 1)
        self.assertFalse(record["is_future"])

    def test_scan_try_except_conditional_marking_exact(self) -> None:
        source = (
            "try:\n"                # 1
            "    import ujson\n"    # 2 conditional (try body)
            "except ImportError:\n" # 3
            "    import json\n"     # 4 conditional fallback
            "try:\n"                # 5
            "    import ntpath\n"   # 6
            "except:\n"             # 7 bare
            "    import posixpath\n" # 8 fallback
            "try:\n"                # 9
            "    import nt\n"       # 10
            "except (OSError, KeyError):\n"  # 11 tuple
            "    pass\n"            # 12
        )
        result = self.tool.execute(mode="scan", source=source)
        imports = result["imports"]
        self.assertEqual(
            imports[0]["conditional"],
            {"exception": "ImportError", "try_line": 1, "handler_line": 3},
        )
        self.assertEqual(
            imports[1]["conditional"],
            {
                "exception": "ImportError",
                "try_line": 1,
                "handler_line": 3,
                "fallback": True,
            },
        )
        self.assertEqual(
            imports[2]["conditional"],
            {"exception": "bare", "try_line": 5, "handler_line": 7},
        )
        self.assertEqual(
            imports[3]["conditional"],
            {
                "exception": "bare",
                "try_line": 5,
                "handler_line": 7,
                "fallback": True,
            },
        )
        self.assertEqual(
            imports[4]["conditional"],
            {
                "exception": "(OSError, KeyError)",
                "try_line": 9,
                "handler_line": 11,
            },
        )
        self.assertEqual(
            result["conditional_blocks"],
            [
                {
                    "start_line": 1,
                    "end_line": 4,
                    "handler_line": 3,
                    "exception": "ImportError",
                    "import_lines": [2],
                },
                {
                    "start_line": 5,
                    "end_line": 8,
                    "handler_line": 7,
                    "exception": "bare",
                    "import_lines": [6],
                },
                {
                    "start_line": 9,
                    "end_line": 12,
                    "handler_line": 11,
                    "exception": "(OSError, KeyError)",
                    "import_lines": [10],
                },
            ],
        )
        self.assertEqual(result["conditional_block_count"], 3)

    def test_scan_try_finally_not_conditional(self) -> None:
        source = "try:\n    import os\nfinally:\n    import sys\n"
        result = self.tool.execute(mode="scan", source=source)
        self.assertEqual(result["import_count"], 2)
        self.assertTrue(all(r["conditional"] is None for r in result["imports"]))
        self.assertEqual(result["conditional_blocks"], [])

    def test_scan_nested_contexts(self) -> None:
        # An import inside if/for/def/class bodies is still found; a
        # try nested inside a def still marks its body conditional,
        # and the outer def import stays unconditional.
        source = (
            "import os\n"                                    # 1 plain
            "def f():\n"                                    # 2
            "    import json\n"                              # 3 nested plain
            "    try:\n"                                    # 4
            "        import yaml\n"                          # 5 conditional
            "    except ImportError:\n"                     # 6
            "        yaml = None\n"                          # 7
            "class C:\n"                                    # 8
            "    import re\n"                                # 9 class-body import
            "for _ in range(1):\n"                          # 10
            "    import math\n"                              # 11
        )
        result = self.tool.execute(mode="scan", source=source)
        self.assertEqual(
            [r["module"] for r in result["imports"]],
            ["os", "json", "yaml", "re", "math"],
        )
        self.assertEqual([r["line"] for r in result["imports"]], [1, 3, 5, 9, 11])
        self.assertEqual(
            result["imports"][2]["conditional"],
            {"exception": "ImportError", "try_line": 4, "handler_line": 6},
        )
        for index in (0, 1, 3, 4):
            self.assertIsNone(result["imports"][index]["conditional"])

    def test_scan_imports_sorted_by_line(self) -> None:
        source = "import b\nimport a\nimport c\n"
        result = self.tool.execute(mode="scan", source=source)
        self.assertEqual(
            [(r["line"], r["module"]) for r in result["imports"]],
            [(1, "b"), (2, "a"), (3, "c")],
        )

    def test_scan_no_imports(self) -> None:
        result = self.tool.execute(mode="scan", source="x = 1\nprint(x)\n")
        self.assertEqual(
            result,
            {
                "mode": "scan",
                "import_count": 0,
                "imports": [],
                "conditional_blocks": [],
                "conditional_block_count": 0,
            },
        )

    def test_scan_match_case_bodies_walked(self) -> None:
        # ast.Match.cases holds ast.match_case nodes, not plain statements;
        # imports inside case bodies must still be reported (the compiler
        # emits IMPORT_NAME for them, so the bytecode oracle sees them).
        source = (
            "import json\n"
            "match json.load({}):\n"
            "    case {'kind': 'csv'}:\n"
            "        import csv\n"
            "        from io import StringIO\n"
            "    case _:\n"
            "        from pathlib import Path\n"
        )
        result = self.tool.execute(mode="scan", source=source)
        self.assertEqual(
            [(r["line"], r["module"]) for r in result["imports"]],
            [(1, "json"), (4, "csv"), (5, "io"), (7, "pathlib")],
        )

    def test_analyze_match_case_dependency_graph(self) -> None:
        files = {
            "a.py": (
                "def pick(x):\n"
                "    match x:\n"
                "        case 1:\n"
                "            import b\n"
                "        case _:\n"
                "            import c\n"
                "    return None\n"
            ),
            "b.py": "import c\n",
            "c.py": "VALUE = 1\n",
        }
        result = self.tool.execute(mode="analyze", files=files)
        self.assertEqual(
            [(e["from"], e["to"]) for e in result["edges"]],
            [("a", "b"), ("a", "c"), ("b", "c")],
        )
        self.assertEqual(result["orphans"], [])
        self.assertEqual(result["cycles"], [])


    # ------------------------------------------------------------------ #
    # deps mode — stdlib / external / internal classification
    # ------------------------------------------------------------------ #

    def test_deps_classification_exact(self) -> None:
        source = (
            "from __future__ import annotations\n"
            "import os\n"
            "import os.path\n"          # dup of the os root
            "import sys\n"
            "import requests\n"
            "from agentuniverse.agent.action.tool.tool import Tool\n"
            "from . import sibling\n"
            "from .mod import thing\n"
            "from ..pkg.mod import other\n"
        )
        self.assertEqual(
            self.tool.execute(mode="deps", source=source),
            {
                "mode": "deps",
                "import_count": 9,
                "internal": [".", "..pkg.mod", ".mod"],
                "external": [
                    "agentuniverse.agent.action.tool.tool",
                    "requests",
                ],
                "stdlib": ["__future__", "os", "os.path", "sys"],
                "counts": {
                    "internal": 3,
                    "external": 2,
                    "stdlib": 4,
                },
                "stdlib_list_source": "sys.stdlib_module_names",
            },
        )

    def test_deps_conditional_imports_classified_too(self) -> None:
        source = (
            "try:\n"
            "    import ujson\n"
            "except ImportError:\n"
            "    import json\n"
        )
        result = self.tool.execute(mode="deps", source=source)
        self.assertEqual(result["external"], ["ujson"])
        self.assertEqual(result["stdlib"], ["json"])

    def test_deps_stdlib_source_attribute_documented(self) -> None:
        self.assertEqual(
            ImportGraphTool.STDLIB_SOURCE, "sys.stdlib_module_names"
        )
        self.assertIn("os", ImportGraphTool.STDLIB_NAMES)
        self.assertIn("__future__", ImportGraphTool.STDLIB_NAMES)

    # ------------------------------------------------------------------ #
    # analyze mode — single-file anomalies
    # ------------------------------------------------------------------ #

    def test_analyze_single_file_exact(self) -> None:
        source = (
            "import alpha\n"        # 1 self-import (stem match)
            "import alpha.sub\n"    # 2 self-import (root match)
            "import beta\n"         # 3 normal
            "from gamma import *\n" # 4 star absolute
            "from .delta import *\n" # 5 star relative
            "try:\n"                # 6
            "    import ujson\n"    # 7
            "except ImportError:\n" # 8
            "    import json\n"     # 9
        )
        self.assertEqual(
            self.tool.execute(
                mode="analyze", source=source, filename="alpha.py"
            ),
            {
                "mode": "analyze",
                "scope": "single_file",
                "module_name": "alpha",
                "self_imports": [
                    {"line": 1, "module": "alpha"},
                    {"line": 2, "module": "alpha.sub"},
                ],
                "star_imports": [
                    {"line": 4, "module": "gamma"},
                    {"line": 5, "module": ".delta"},
                ],
                "conditional_chains": [
                    {
                        "start_line": 6,
                        "end_line": 9,
                        "exception": "ImportError",
                        "primary_modules": ["ujson"],
                        "fallback_modules": ["json"],
                        "primary_lines": [7],
                        "fallback_lines": [9],
                        "names": ["json", "ujson"],
                    }
                ],
                "warning_count": 5,
            },
        )

    def test_analyze_single_file_default_module_name(self) -> None:
        source = "import source\n"
        result = self.tool.execute(mode="analyze", source=source)
        self.assertEqual(result["module_name"], "source")
        self.assertEqual(
            result["self_imports"], [{"line": 1, "module": "source"}]
        )

    def test_analyze_single_file_relative_not_self_import(self) -> None:
        # `from . import alpha` names a *sibling* package-relative
        # module, not the file itself — documented limitation: single
        # file self-import detection matches absolute imports only.
        result = self.tool.execute(
            mode="analyze", source="from . import alpha\n", filename="alpha.py"
        )
        self.assertEqual(result["self_imports"], [])

    def test_analyze_single_file_chain_requires_fallback_import(self) -> None:
        # A guarded import whose handler only assigns (no import) is
        # not a fallback chain.
        source = (
            "try:\n"
            "    import ujson\n"
            "except ImportError:\n"
            "    ujson = None\n"
        )
        result = self.tool.execute(mode="analyze", source=source)
        self.assertEqual(result["conditional_chains"], [])
        self.assertEqual(result["warning_count"], 0)

    # ------------------------------------------------------------------ #
    # analyze mode — multi-file graph
    # ------------------------------------------------------------------ #

    def test_analyze_files_two_cycle_and_orphan(self) -> None:
        files = {
            "a.py": "import b\nimport os\n",
            "b.py": "import a\n",
            "o.py": "import sys\n",
        }
        self.assertEqual(
            self.tool.execute(mode="analyze", files=files),
            {
                "mode": "analyze",
                "scope": "files",
                "module_count": 3,
                "modules": ["a", "b", "o"],
                "edges": [
                    {"from": "a", "to": "b", "module": "b", "line": 1},
                    {"from": "b", "to": "a", "module": "a", "line": 1},
                ],
                "edge_count": 2,
                "cycles": [["a", "b"]],
                "cycle_count": 1,
                "orphans": ["o"],
                "orphan_count": 1,
                "self_loops": [],
                "warnings": {
                    "a": {
                        "self_imports": [],
                        "star_imports": [],
                        "conditional_chains": [],
                        "warning_count": 0,
                    },
                    "b": {
                        "self_imports": [],
                        "star_imports": [],
                        "conditional_chains": [],
                        "warning_count": 0,
                    },
                    "o": {
                        "self_imports": [],
                        "star_imports": [],
                        "conditional_chains": [],
                        "warning_count": 0,
                    },
                },
                "warning_count": 0,
                "resolution": (
                    "filename-stem (flat sibling model; see module "
                    "docstring for the documented limits)"
                ),
            },
        )

    def test_analyze_files_three_cycle(self) -> None:
        files = {
            "x.py": "import y\n",
            "y.py": "import z\n",
            "z.py": "import x\n",
        }
        result = self.tool.execute(mode="analyze", files=files)
        self.assertEqual(result["cycles"], [["x", "y", "z"]])
        self.assertEqual(result["orphans"], [])
        self.assertEqual(result["edge_count"], 3)

    def test_analyze_files_scc_sharing_merges(self) -> None:
        # a<->b is a 2-cycle and b->c->d->b a 3-cycle sharing node b:
        # Tarjan SCC merges them into the single component {a,b,c,d}.
        files = {
            "a.py": "import b\n",
            "b.py": "import a\nimport c\n",
            "c.py": "import d\n",
            "d.py": "import b\n",
        }
        result = self.tool.execute(mode="analyze", files=files)
        self.assertEqual(result["cycles"], [["a", "b", "c", "d"]])
        self.assertEqual(result["cycle_count"], 1)

    def test_analyze_files_self_loop_singleton_cycle(self) -> None:
        files = {
            "s.py": "import s\n",
            "t.py": "import s\n",
        }
        result = self.tool.execute(mode="analyze", files=files)
        self.assertEqual(result["cycles"], [["s"]])
        self.assertEqual(result["self_loops"], ["s"])
        self.assertEqual(
            result["warnings"]["s"]["self_imports"],
            [{"line": 1, "module": "s"}],
        )
        # The self-import is a warning, not a dependency edge.
        self.assertEqual(
            result["edges"], [{"from": "t", "to": "s", "module": "s", "line": 1}]
        )

    def test_analyze_files_relative_sibling_resolution(self) -> None:
        files = {
            "m.py": "from . import n\nfrom .p import q\nfrom ..deep import r\n",
            "n.py": "import m\n",
            "p.py": "pass\n",
        }
        result = self.tool.execute(mode="analyze", files=files)
        self.assertEqual(
            [(e["from"], e["to"], e["line"]) for e in result["edges"]],
            [("m", "n", 1), ("m", "p", 2), ("n", "m", 1)],
        )
        # Level-2 relative imports cannot be resolved in the flat
        # sibling model and are skipped (documented limit).
        self.assertNotIn("deep", result["modules"])

    def test_analyze_files_edges_deduplicated_keep_first_line(self) -> None:
        files = {
            "a.py": "import b\nimport b\nfrom b import x\n",
            "b.py": "pass\n",
        }
        result = self.tool.execute(mode="analyze", files=files)
        self.assertEqual(result["edge_count"], 1)
        self.assertEqual(result["edges"][0]["line"], 1)

    def test_analyze_files_ignores_non_stem_imports(self) -> None:
        files = {
            "a.py": "import os\nimport requests\n",
        }
        result = self.tool.execute(mode="analyze", files=files)
        self.assertEqual(result["edges"], [])
        self.assertEqual(result["orphans"], ["a"])

    def test_analyze_files_nested_path_uses_stem(self) -> None:
        files = {
            "pkg/mod.py": "import other\n",
            "other.py": "pass\n",
        }
        result = self.tool.execute(mode="analyze", files=files)
        self.assertEqual(result["modules"], ["mod", "other"])
        self.assertEqual(result["edge_count"], 1)

    def test_analyze_files_aggregates_per_file_warnings(self) -> None:
        files = {
            "a.py": "from os import *\n",
            "b.py": "try:\n    import ujson\nexcept ImportError:\n    import json\n",
        }
        result = self.tool.execute(mode="analyze", files=files)
        self.assertEqual(result["warnings"]["a"]["star_imports"][0]["line"], 1)
        self.assertEqual(
            result["warnings"]["b"]["conditional_chains"][0]["names"],
            ["json", "ujson"],
        )
        self.assertEqual(result["warning_count"], 2)

    # ------------------------------------------------------------------ #
    # to_dot mode — exact DOT emission
    # ------------------------------------------------------------------ #

    def test_to_dot_two_cycle_exact(self) -> None:
        files = {
            "a.py": "import b\n",
            "b.py": "import a\nimport c\n",
            "c.py": "import sys\n",
        }
        self.assertEqual(
            self.tool.execute(mode="to_dot", files=files),
            {
                "mode": "to_dot",
                "graph_name": "imports",
                "result": (
                    "digraph imports {\n"
                    '    a [label="a.py", shape=box, style=dotted];\n'
                    '    b [label="b.py", shape=box, style=dotted];\n'
                    '    c [label="c.py", shape=box];\n'
                    '    a -> b [label="b", style=dashed];\n'
                    '    b -> a [label="a", style=dashed];\n'
                    '    b -> c [label="c"];\n'
                    "}"
                ),
                "node_count": 3,
                "edge_count": 3,
                "cycle_count": 1,
                "cycles": [["a", "b"]],
            },
        )

    def test_to_dot_acyclic_exact(self) -> None:
        files = {"a.py": "import b\n", "b.py": "import c\n", "c.py": "pass\n"}
        result = self.tool.execute(mode="to_dot", files=files)
        self.assertEqual(
            result["result"],
            "digraph imports {\n"
            '    a [label="a.py", shape=box];\n'
            '    b [label="b.py", shape=box];\n'
            '    c [label="c.py", shape=box];\n'
            '    a -> b [label="b"];\n'
            '    b -> c [label="c"];\n'
            "}",
        )
        self.assertEqual(result["cycle_count"], 0)
        self.assertNotIn("id_mapping", result)

    def test_to_dot_self_loop_and_solid_exit_edge(self) -> None:
        files = {
            "s.py": "import s\nimport t\n",
            "t.py": "pass\n",
        }
        result = self.tool.execute(mode="to_dot", files=files)
        self.assertEqual(
            result["result"],
            "digraph imports {\n"
            '    s [label="s.py", shape=box, style=dotted];\n'
            '    t [label="t.py", shape=box];\n'
            '    s -> s [label="s", style=dashed];\n'
            '    s -> t [label="t"];\n'
            "}",
        )
        self.assertEqual(result["edge_count"], 2)
        self.assertEqual(result["cycles"], [["s"]])

    def test_to_dot_graph_name_sanitized_with_mapping(self) -> None:
        files = {"a.py": "import b\n", "b.py": "pass\n"}
        result = self.tool.execute(mode="to_dot", files=files, name="import-graph")
        self.assertTrue(result["result"].startswith("digraph import_graph {"))
        self.assertEqual(
            result["id_mapping"], {"import-graph": "import_graph"}
        )
        self.assertEqual(result["graph_name"], "import-graph")

    def test_to_dot_reserved_graph_name_gets_suffix(self) -> None:
        files = {"a.py": "pass\n"}
        result = self.tool.execute(mode="to_dot", files=files, name="graph")
        self.assertTrue(result["result"].startswith("digraph graph_ {"))
        self.assertEqual(result["id_mapping"], {"graph": "graph_"})

    def test_to_dot_label_escaping(self) -> None:
        # Directory names may hold quotes and backslashes (the stem
        # stays a valid identifier), which exercises the DOT label
        # escaping: backslash -> \\, quote -> \".
        files = {'we"i\\rd/name.py': "pass\n"}
        result = self.tool.execute(mode="to_dot", files=files)
        self.assertEqual(
            result["result"],
            "digraph imports {\n"
            '    name [label="we\\"i\\\\rd/name.py", shape=box];\n'
            "}",
        )
        self.assertNotIn("id_mapping", result)

    # ------------------------------------------------------------------ #
    # async delegation (base-class async_execute -> execute)
    # ------------------------------------------------------------------ #

    def test_async_execute_matches_execute(self) -> None:
        kwargs = {
            "mode": "analyze",
            "files": {"a.py": "import b\n", "b.py": "import a\n"},
        }
        sync_result = self.tool.execute(**kwargs)
        async_result = asyncio.run(self.tool.async_execute(**kwargs))
        self.assertEqual(sync_result, async_result)

    def test_direct_module_import_matches_package_import(self) -> None:
        self.assertIs(DirectImportGraphTool, ImportGraphTool)

    # ------------------------------------------------------------------ #
    # error matrix — strict validation
    # ------------------------------------------------------------------ #

    def test_error_unknown_mode(self) -> None:
        self._expect_value_error(
            "mode must be one of", mode="render", source="import os\n"
        )

    def test_error_mode_missing(self) -> None:
        self._expect_value_error("mode must be one of", source="import os\n")

    def test_error_source_required_nonempty_string(self) -> None:
        self._expect_value_error("source must be a non-empty string", mode="scan")
        self._expect_value_error(
            "source must be a non-empty string", mode="scan", source=""
        )
        self._expect_value_error(
            "source must be a non-empty string", mode="scan", source=42
        )
        self._expect_value_error(
            "must not be empty or whitespace-only", mode="scan", source="   \n"
        )

    def test_error_source_oversized(self) -> None:
        self._expect_value_error(
            "exceeds the 100000-character limit",
            mode="scan",
            source="import os\n" + "#" * 100_000,
        )

    def test_error_source_syntax_error(self) -> None:
        self._expect_value_error(
            "must be syntactically valid Python 3",
            mode="scan",
            source="def broken(:\n    pass\n",
        )

    def test_error_analyze_source_and_files_conflict(self) -> None:
        self._expect_value_error(
            "either source (single file) or files (multi-file), not both",
            mode="analyze",
            source="import os\n",
            files={"a.py": "pass\n"},
        )

    def test_error_analyze_requires_source_or_files(self) -> None:
        self._expect_value_error(
            "source must be a non-empty string", mode="analyze"
        )

    def test_error_files_must_be_dict(self) -> None:
        self._expect_value_error(
            "files must be a dict", mode="to_dot", files=["a.py"]
        )
        self._expect_value_error("files must be a dict", mode="to_dot", files="a.py")
        self._expect_value_error(
            "files must not be empty", mode="to_dot", files={}
        )

    def test_error_files_too_many(self) -> None:
        files = {f"m{i}.py": "pass\n" for i in range(101)}
        self._expect_value_error(
            "exceeds the 100-file limit", mode="to_dot", files=files
        )

    def test_error_files_bad_keys(self) -> None:
        self._expect_value_error(
            "files keys must be filenames", mode="to_dot", files={42: "pass\n"}
        )
        self._expect_value_error(
            "must end with .py or .pyi",
            mode="to_dot",
            files={"a.txt": "pass\n"},
        )
        self._expect_value_error(
            "filename stem must be a Python identifier",
            mode="to_dot",
            files={"123bad.py": "pass\n"},
        )
        self._expect_value_error(
            "must not contain control characters",
            mode="to_dot",
            files={"a\n.py": "pass\n"},
        )

    def test_error_files_duplicate_stems(self) -> None:
        self._expect_value_error(
            "filename stems collide after flattening",
            mode="to_dot",
            files={"pkg/a.py": "pass\n", "a.py": "pass\n"},
        )

    def test_error_files_bad_values(self) -> None:
        self._expect_value_error(
            "must be a non-empty string", mode="to_dot", files={"a.py": 5}
        )
        self._expect_value_error(
            "must not be empty or whitespace-only",
            mode="to_dot",
            files={"a.py": "   "},
        )

    def test_error_to_dot_requires_files(self) -> None:
        self._expect_value_error("files must be a dict", mode="to_dot")

    def test_error_analyze_bad_filename(self) -> None:
        self._expect_value_error(
            "filename must be a string",
            mode="analyze",
            source="import os\n",
            filename=3,
        )
        self._expect_value_error(
            "must end with .py or .pyi",
            mode="analyze",
            source="import os\n",
            filename="readme.txt",
        )

    def test_error_too_many_imports_in_one_file(self) -> None:
        source = "".join(f"import m{i}\n" for i in range(1001))
        self._expect_value_error(
            "more than 1000 imports", mode="scan", source=source
        )

    def test_error_bad_graph_name(self) -> None:
        self._expect_value_error(
            "name must be a non-empty string", mode="to_dot", files={"a.py": "pass\n"}, name=""
        )
        self._expect_value_error(
            "name must not contain control characters",
            mode="to_dot",
            files={"a.py": "pass\n"},
            name="im\nport",
        )


if __name__ == "__main__":
    unittest.main()
