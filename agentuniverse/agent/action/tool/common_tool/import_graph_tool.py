#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: import_graph_tool.py

"""Python import dependency mapping tool built purely on the stdlib ``ast``.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency source-analysis
layer: given Python source text — one file or a batch of files — the
tool EXTRACTS the import graph out of the source and analyzes
import-specific anomalies (conditional imports, star imports,
self-imports, dependency cycles, orphan modules). It is deliberately
the source-extraction layer of the diagram stack, not another edge
algebra or renderer.

Supported modes:

* ``scan`` — parse one Python source text (single-file contract) and
  return every import statement as ``{module, names, aliases, level,
  line, is_star, is_future, conditional}`` sorted by line.
  ``module`` is the dotted module as written (empty string for a
  bare ``from . import x`` whose target is the package itself);
  ``level`` is 0 for absolute and 1+ for relative imports; ``names``
  are the names actually bound in the importing namespace (the
  ``asname`` when aliased, the top-level package for a plain
  ``import a.b``, ``["*"]`` for star imports); ``aliases`` maps the
  original name to the alias for aliased imports (``{}`` otherwise).
  Imports guarded by ``try`` / ``except`` blocks are flagged with
  ``conditional`` — the except-clause exception label, the try and
  handler line numbers, and a ``fallback`` marker for imports in a
  handler body — and every such block is additionally summarized in
  a ``conditional_blocks`` list (try-body imports only; the label is
  the first handler's except-clause, or ``bare`` for a bare
  ``except:``).
* ``deps`` — classify one source text's absolute imports into
  ``stdlib`` (top-level name in ``sys.stdlib_module_names``),
  ``external`` (absolute modules whose top-level name is not in that
  set) and ``internal`` (relative imports, rendered with their
  leading dots: ``.mod``, ``..pkg.mod``, ``.`` for a bare package
  import). Classification is by top-level component — ``os.path``
  reports under stdlib because ``os`` is the stdlib name — while the
  ``stdlib`` / ``external`` lists keep the full dotted module names
  as written, deduplicated and sorted. The stdlib list source is
  reported alongside (``sys.stdlib_module_names`` on Python >= 3.10;
  on older interpreters the tool falls back to
  ``sys.builtin_module_names`` and says so — the fallback is
  documented, coarser, and only compiled-in modules classify as
  stdlib there).
* ``analyze`` — import-anomaly analysis. Single-file form (``source``
  plus optional ``filename``): self-import detection (an absolute
  import whose top-level name equals the file's module stem),
  star-import warnings and conditional-import chains (a guarded
  import whose handler body also imports — the classic
  ``try: import ujson / except ImportError: import json`` fallback;
  reported with primary / fallback modules, except-clause labels and
  the union of bound names). Multi-file form (``files``, a ``{filename: source}``
  dict): builds the cross-file import graph by filename-stem
  resolution — every file is one flat sibling module, file A imports
  file B when A contains a level-0 absolute import whose top-level
  name (or a level-1 relative ``from . import x`` name) matches B's
  stem — then reports deduplicated ``edges`` (keeping the first
  import line that established each edge), cycles via Tarjan
  strongly-connected components (SCCs of size > 1 plus self-loop
  singletons), and ``orphans`` (modules with no incoming and no
  outgoing edges among the set), plus the same per-file warnings.
  Documented filename-based resolution limits: package structure is
  ignored (``pkg/mod.py`` is the module ``mod``), deeper relative
  imports (level >= 2) cannot be resolved in the flat model and are
  skipped, and two files with the same stem are rejected instead of
  silently merged.
* ``to_dot`` — render the multi-file graph (same ``files`` input,
  same resolution rules) as Graphviz DOT source following the
  DotGraphTool emission conventions implemented standalone:
  identifiers sanitized to ``[A-Za-z0-9_]`` (invalid characters
  become ``_`` one-for-one, a leading digit gains a ``_`` prefix, a
  reserved DOT keyword gains a trailing ``_``, changes are reported
  in ``id_mapping``), node labels always double-quoted with backslash
  / quote / newline escaping, every statement terminated with ``;``,
  attribute order ``label, shape, style`` (nodes) / ``label, style``
  (edges) and alphabetical node / edge order, so the same input
  always yields byte-identical DOT. Cycle-participating edges are
  emitted ``style=dashed`` and cycle-member nodes ``style=dotted``.

Input validation is strict and happens before any analysis:
malformed parameters (unknown mode, empty or oversized source, a
``files`` dict that is not a mapping of ``.py`` / ``.pyi`` filenames
to non-empty source strings, duplicate module stems, more than
``MAX_FILES`` files or ``MAX_IMPORTS_PER_FILE`` imports in one file,
giving both ``source`` and ``files`` or neither) raise a
``ValueError``, mirroring the other common tools. A source text that
is not syntactically valid Python also raises ``ValueError`` (the
``ast`` syntax-error message is preserved) — the tool analyzes
source, it does not repair it.
"""

import ast
import re
import sys
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Filename suffixes accepted for the multi-file modes.
_PY_SUFFIXES = (".py", ".pyi")
# Characters that may appear in a sanitized DOT identifier (the
# DotGraphTool emission convention this tool mirrors for to_dot).
_INVALID_ID_CHARS = re.compile(r"[^A-Za-z0-9_]")
# Control characters rejected in filenames (newlines included).
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
# Reserved DOT keywords that must not survive as bare identifiers.
_RESERVED_DOT = (
    "digraph",
    "graph",
    "subgraph",
    "node",
    "edge",
    "strict",
)
# The stdlib name set used for deps classification. On Python
# >= 3.10 sys.stdlib_module_names is the authoritative list; the
# documented fallback for older interpreters is the (much coarser)
# compiled-in module list.
_STDLIB_NAMES: frozenset = frozenset(getattr(sys, "stdlib_module_names", ()))
if not _STDLIB_NAMES:
    _STDLIB_NAMES = frozenset(sys.builtin_module_names)
    _STDLIB_SOURCE = "sys.builtin_module_names (fallback; sys.stdlib_module_names unavailable on this interpreter)"
else:
    _STDLIB_SOURCE = "sys.stdlib_module_names"
# Newline forms normalized to the two characters '\n' inside DOT
# labels (plain str.replace — re.sub templates would re-interpret
# the backslash escape).
_NEWLINE_FORMS = ("\r\n", "\r", "\n")


class ImportGraphTool(Tool):
    """Python import dependency mapper built purely on the stdlib ``ast``.

    The tool extracts imports out of Python source text (one file or
    a batch), classifies dependencies (stdlib / external / internal
    relative), analyzes import-specific anomalies (conditional
    imports, star imports, self-imports, cycles, orphans) and emits
    the multi-file graph as Graphviz DOT source. It never imports,
    executes or resolves the analyzed code — it only parses text.

    Class attributes:
        MAX_SOURCE_CHARS (int): Upper bound on one source text.
        MAX_FILES (int): Upper bound on the ``files`` mapping size.
        MAX_FILENAME_CHARS (int): Upper bound on one filename key.
        MAX_IMPORTS_PER_FILE (int): Upper bound on imports in one
            file before the input is rejected.
        MAX_ID_CHARS (int): Upper bound on the ``to_dot`` graph name.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "import_graph_tool"
    description: str = (
        "Python import dependency mapping tool — pure stdlib ast, no "
        "execution and no network. Extracts every import statement "
        "from Python source text with line numbers, aliasing, "
        "relative levels, star/future flags and try/except "
        "conditional-import info (mode='scan'), classifies "
        "dependencies into stdlib (sys.stdlib_module_names), external "
        "and internal relative (mode='deps'), detects self-imports, "
        "star imports and conditional fallback chains per file and — "
        "over a {filename: source} batch — builds the filename-stem "
        "import graph with Tarjan cycle detection and orphan modules "
        "(mode='analyze'), and renders that graph as Graphviz DOT "
        "source with cycles highlighted dashed (mode='to_dot')."
    )

    MODES: ClassVar[tuple] = ("scan", "deps", "analyze", "to_dot")
    DEFAULT_GRAPH_NAME: ClassVar[str] = "imports"

    MAX_SOURCE_CHARS: ClassVar[int] = 100_000
    MAX_FILES: ClassVar[int] = 100
    MAX_FILENAME_CHARS: ClassVar[int] = 200
    MAX_IMPORTS_PER_FILE: ClassVar[int] = 1000
    MAX_ID_CHARS: ClassVar[int] = 200

    STDLIB_NAMES: ClassVar[frozenset] = _STDLIB_NAMES
    STDLIB_SOURCE: ClassVar[str] = _STDLIB_SOURCE

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        source: Any = None,
        files: Any = None,
        filename: Any = None,
        name: Any = None,
    ) -> dict[str, Any]:
        """Extract and analyze the import graph of Python source text.

        Args:
            mode (str): One of ``scan``, ``deps``, ``analyze`` or
                ``to_dot``.
            source (str): The Python source text. Required for
                ``scan`` / ``deps`` and for the single-file
                ``analyze`` form; must be omitted for the multi-file
                forms.
            files (dict): Mapping of ``.py`` / ``.pyi`` filenames to
                Python source text. Required for ``to_dot`` and the
                multi-file ``analyze`` form; must be omitted for the
                single-file forms.
            filename (str): Optional filename for the single-file
                ``analyze`` form (default ``source.py``); its stem is
                the module name used for self-import detection.
            name (str): Optional ``to_dot`` graph name (default
                ``imports``; sanitized like node ids).

        Returns:
            Dict[str, Any]: Mode-dependent result — the ``scan``
                import list, the ``deps`` classification, the
                ``analyze`` anomaly report (single-file or cross-file
                graph) or the ``to_dot`` DOT source with counts.

        Raises:
            ValueError: If any parameter is malformed (before any
                analysis happens) or the source is not valid Python.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode in ("scan", "deps"):
            return self._run_text_mode(mode, source)
        if mode == "analyze":
            return self._run_analyze(source, files, filename)
        return self._run_to_dot(files, name)

    # ------------------------------------------------------------------ #
    # Input validation helpers (pure — raise before any analysis)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"import_graph_tool: {message}")

    @classmethod
    def _validate_source(cls, value: Any, what: str) -> str:
        """Validate one Python source text parameter."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{what} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{what} must be a non-empty string (got '')")
        if not value.strip():
            cls._invalid(f"{what} must not be empty or whitespace-only")
        if len(value) > cls.MAX_SOURCE_CHARS:
            cls._invalid(
                f"{what} exceeds the {cls.MAX_SOURCE_CHARS}-character "
                f"limit (got {len(value)} characters)"
            )
        return value

    @classmethod
    def _validate_filename(cls, value: Any) -> tuple:
        """Validate one ``files`` key; return (filename, stem)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"files keys must be filenames (got {value!r})")
        if not value or len(value) > cls.MAX_FILENAME_CHARS:
            cls._invalid(
                f"filename must be a non-empty string of at most "
                f"{cls.MAX_FILENAME_CHARS} characters (got {value!r})"
            )
        if _CONTROL_CHARS.search(value) or "\n" in value or "\r" in value:
            cls._invalid(f"filename must not contain control characters (got {value!r})")
        if not value.endswith(_PY_SUFFIXES):
            cls._invalid(
                f"filename must end with .py or .pyi (got {value!r})"
            )
        stem = value[:-3] if value.endswith(".py") else value[:-4]
        stem = stem.rsplit("/", 1)[-1]
        if not stem.isidentifier():
            cls._invalid(
                f"filename stem must be a Python identifier (got {stem!r} "
                f"from {value!r})"
            )
        return value, stem

    @classmethod
    def _validate_files(cls, value: Any) -> dict:
        """Validate the ``files`` mapping; return {stem: filename}."""
        if value is None or isinstance(value, bool) or not isinstance(value, dict):
            cls._invalid(f"files must be a dict of {{filename: source}} (got {value!r})")
        if not value:
            cls._invalid("files must not be empty")
        if len(value) > cls.MAX_FILES:
            cls._invalid(f"files exceeds the {cls.MAX_FILES}-file limit (got {len(value)})")
        stems: dict = {}
        for raw_name, raw_source in value.items():
            filename, stem = cls._validate_filename(raw_name)
            if stem in stems:
                cls._invalid(
                    f"filename stems collide after flattening: "
                    f"{stems[stem]!r} and {filename!r} both resolve to "
                    f"module {stem!r}; the flat filename-stem model cannot "
                    "hold both"
                )
            cls._validate_source(raw_source, f"files[{filename!r}]")
            stems[stem] = filename
        return stems

    @classmethod
    def _parse(cls, source: str, what: str) -> ast.Module:
        """Parse one source text; syntax errors become ValueError."""
        try:
            return ast.parse(source)
        except SyntaxError as exc:
            cls._invalid(
                f"{what} must be syntactically valid Python 3 "
                f"(line {exc.lineno}: {exc.msg})"
            )

    @classmethod
    def _validate_graph_name(cls, value: Any) -> str:
        """Validate the ``to_dot`` graph name (sanitized later)."""
        if value is None:
            return cls.DEFAULT_GRAPH_NAME
        if isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"name must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid("name must be a non-empty string (got '')")
        if len(value) > cls.MAX_ID_CHARS:
            cls._invalid(
                f"name exceeds the {cls.MAX_ID_CHARS}-character limit "
                f"(got {len(value)} characters)"
            )
        if _CONTROL_CHARS.search(value) or "\n" in value or "\r" in value:
            cls._invalid("name must not contain control characters")
        return value

    # ------------------------------------------------------------------ #
    # ast walking — the extraction core shared by every mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _extract_imports(cls, tree: ast.Module) -> tuple:
        """Walk ``tree`` in source order and extract import records.

        Returns ``(imports, conditional_blocks)``. Every import
        record is a plain dict; conditional-context tracking follows
        the nearest enclosing ``try`` statement that has handlers —
        imports in its body are conditional on the first handler's
        except-clause, imports in a handler body are fallbacks (the
        outer try's context applies inside them).
        """
        imports: list = []
        blocks: list = []
        # context stack entries: None or (kind, label, handler_line)
        # kind 'try' = inside a try body, 'except' = inside a handler body.
        context: list = [None]

        def emit(record: dict) -> None:
            ctx = context[-1]
            if ctx is not None:
                kind, label, try_line, handler_line = ctx
                conditional = {
                    "exception": label,
                    "try_line": try_line,
                    "handler_line": handler_line,
                }
                if kind == "except":
                    conditional["fallback"] = True
                record["conditional"] = conditional
            else:
                record["conditional"] = None
            imports.append(record)

        def handler_label(handler: Any) -> str:
            if handler.type is None:
                return "bare"
            try:
                return ast.unparse(handler.type)
            except Exception:  # pragma: no cover - ast.unparse is stable
                return "Exception"

        def walk_body(stmts: Any) -> None:
            for stmt in stmts:
                if isinstance(stmt, ast.Import):
                    for alias in stmt.names:
                        bound = alias.asname or alias.name.split(".")[0]
                        aliases = {}
                        if alias.asname and alias.asname != alias.name:
                            aliases[alias.name] = alias.asname
                        emit(
                            {
                                "module": alias.name,
                                "names": [bound],
                                "aliases": aliases,
                                "level": 0,
                                "line": stmt.lineno,
                                "is_star": False,
                                "is_future": False,
                            }
                        )
                elif isinstance(stmt, ast.ImportFrom):
                    module = stmt.module or ""
                    aliases = {}
                    names = []
                    for alias in stmt.names:
                        if alias.name == "*":
                            names.append("*")
                            continue
                        names.append(alias.asname or alias.name)
                        if alias.asname and alias.asname != alias.name:
                            aliases[alias.name] = alias.asname
                    emit(
                        {
                            "module": module,
                            "names": names,
                            "aliases": aliases,
                            "level": stmt.level,
                            "line": stmt.lineno,
                            "is_star": any(a.name == "*" for a in stmt.names),
                            "is_future": module == "__future__" and stmt.level == 0,
                        }
                    )
                elif isinstance(stmt, (ast.Try, getattr(ast, "TryStar", ast.Try))):
                    before = len(imports)
                    label = handler_label(stmt.handlers[0]) if stmt.handlers else None
                    context.append(
                        ("try", label, stmt.lineno, stmt.handlers[0].lineno)
                        if stmt.handlers
                        else None
                    )
                    walk_body(stmt.body)
                    context.pop()
                    new_imports = imports[before:]
                    if stmt.handlers and new_imports:
                        blocks.append(
                            {
                                "start_line": stmt.lineno,
                                "end_line": stmt.end_lineno,
                                "handler_line": stmt.handlers[0].lineno,
                                "exception": label,
                                "import_lines": sorted(
                                    {rec["line"] for rec in new_imports}
                                ),
                            }
                        )
                    for handler in stmt.handlers:
                        context.append(
                            ("except", handler_label(handler), stmt.lineno, handler.lineno)
                        )
                        walk_body(handler.body)
                        context.pop()
                    walk_body(stmt.orelse)
                    walk_body(stmt.finalbody)
                elif isinstance(stmt, ast.Match):
                    # ast.Match.cases holds ast.match_case nodes, not plain
                    # statements, so the generic field walk below never
                    # reaches the case bodies.
                    for case in stmt.cases:
                        walk_body(case.body)
                else:
                    # Recurse into any nested statement lists (if/for/
                    # with/def/class/...) preserving the context.
                    for field in stmt._fields:
                        value = getattr(stmt, field, None)
                        if isinstance(value, list) and value and isinstance(value[0], ast.stmt):
                            walk_body(value)

        walk_body(tree.body)
        if len(imports) > cls.MAX_IMPORTS_PER_FILE:
            cls._invalid(
                f"source has more than {cls.MAX_IMPORTS_PER_FILE} imports "
                f"(got {len(imports)}); refusing to analyze oversized input"
            )
        imports.sort(key=lambda rec: rec["line"])
        blocks.sort(key=lambda block: block["start_line"])
        return imports, blocks

    @classmethod
    def _relative_target(cls, record: dict) -> str:
        """Render a relative import target with its leading dots."""
        return "." * record["level"] + record["module"]

    # ------------------------------------------------------------------ #
    # scan / deps — single-source-text modes
    # ------------------------------------------------------------------ #

    @classmethod
    def _run_text_mode(cls, mode: str, source: Any) -> dict:
        text = cls._validate_source(source, "source")
        tree = cls._parse(text, "source")
        imports, blocks = cls._extract_imports(tree)
        result: dict = {"mode": mode, "import_count": len(imports)}
        if mode == "scan":
            result["imports"] = imports
            result["conditional_blocks"] = blocks
            result["conditional_block_count"] = len(blocks)
            return result
        internal = sorted({cls._relative_target(rec) for rec in imports if rec["level"] > 0})
        stdlib = set()
        external = set()
        for rec in imports:
            if rec["level"] > 0:
                continue
            if rec["module"].split(".")[0] in cls.STDLIB_NAMES:
                stdlib.add(rec["module"])
            else:
                external.add(rec["module"])
        result.update(
            {
                "internal": internal,
                "external": sorted(external),
                "stdlib": sorted(stdlib),
                "counts": {
                    "internal": len(internal),
                    "external": len(external),
                    "stdlib": len(stdlib),
                },
                "stdlib_list_source": cls.STDLIB_SOURCE,
            }
        )
        return result

    # ------------------------------------------------------------------ #
    # analyze — single-file anomalies and the multi-file graph
    # ------------------------------------------------------------------ #

    @classmethod
    def _conditional_chains(cls, imports: list, blocks: list) -> list:
        """Detect try-import / fallback-import chains.

        A chain is a recorded try block (imports in the try body,
        handlers present) where at least one handler body also
        contains an import — the classic conditional-dependency
        fallback (``try: import ujson`` / ``except ImportError:``
        ``import json``). The chain reports the primary (try-body)
        and fallback (handler-body) modules in source order, the
        except-clause labels and the union of bound names.
        """
        primary: dict = {}
        fallback: dict = {}
        for rec in imports:
            ctx = rec["conditional"]
            if ctx is None:
                continue
            bucket = fallback if ctx.get("fallback") else primary
            entry = bucket.setdefault(
                ctx["try_line"], {"modules": [], "names": set(), "lines": []}
            )
            if rec["module"] and rec["module"] not in entry["modules"]:
                entry["modules"].append(rec["module"])
            entry["names"].update(n for n in rec["names"] if n != "*")
            entry["lines"].append(rec["line"])
        chains: list = []
        for block in blocks:
            try_line = block["start_line"]
            if try_line not in primary or try_line not in fallback:
                continue
            chains.append(
                {
                    "start_line": block["start_line"],
                    "end_line": block["end_line"],
                    "exception": block["exception"],
                    "primary_modules": primary[try_line]["modules"],
                    "fallback_modules": fallback[try_line]["modules"],
                    "primary_lines": sorted(set(primary[try_line]["lines"])),
                    "fallback_lines": sorted(set(fallback[try_line]["lines"])),
                    "names": sorted(primary[try_line]["names"] | fallback[try_line]["names"]),
                }
            )
        return chains

    @classmethod
    def _single_file_warnings(
        cls, module_name: str, imports: list, blocks: list
    ) -> dict:
        """Build the per-file anomaly warnings for one module."""
        self_imports = [
            {"line": rec["line"], "module": rec["module"]}
            for rec in imports
            if rec["level"] == 0
            and rec["module"].split(".")[0] == module_name
            and module_name != ""
        ]
        star_imports = [
            {"line": rec["line"], "module": cls._relative_target(rec)}
            for rec in imports
            if rec["is_star"]
        ]
        chains = cls._conditional_chains(imports, blocks)
        return {
            "self_imports": self_imports,
            "star_imports": star_imports,
            "conditional_chains": chains,
            "warning_count": len(self_imports)
            + len(star_imports)
            + len(chains),
        }

    @classmethod
    def _run_analyze(
        cls, source: Any, files: Any, filename: Any
    ) -> dict:
        if source is not None and files is not None:
            cls._invalid(
                "analyze accepts either source (single file) or files "
                "(multi-file), not both"
            )
        if files is not None:
            return cls._run_analyze_files(files)
        text = cls._validate_source(source, "source")
        module_name = "source"
        if filename is not None:
            if isinstance(filename, bool) or not isinstance(filename, str):
                cls._invalid(f"filename must be a string (got {filename!r})")
            validated = cls._validate_filename(filename)
            module_name = validated[1]
        tree = cls._parse(text, "source")
        imports, blocks = cls._extract_imports(tree)
        return {
            "mode": "analyze",
            "scope": "single_file",
            "module_name": module_name,
            **cls._single_file_warnings(module_name, imports, blocks),
        }

    @classmethod
    def _build_graph(cls, files: Any) -> dict:
        """Parse every file and resolve filename-stem edges.

        Returns the shared graph payload used by analyze / to_dot:
        modules (stems), the stem -> original filename map used for
        DOT labels, per-module imports and blocks, deduplicated
        edges sorted by (from, to) — each edge keeps the first import
        line that established it — plus warnings per module.
        """
        stems = cls._validate_files(files)
        modules = sorted(stems)
        parsed: dict = {}
        for stem in modules:
            tree = cls._parse(files[stems[stem]], f"files[{stems[stem]!r}]")
            parsed[stem] = cls._extract_imports(tree)
        edges: dict = {}
        warnings: dict = {}
        for stem in modules:
            imports, blocks = parsed[stem]
            for rec in imports:
                targets: list = []
                if rec["level"] == 0:
                    root = rec["module"].split(".")[0]
                    if root in stems:
                        targets.append((root, root))
                elif rec["level"] == 1:
                    # Flat sibling model: `from . import x` binds
                    # sibling modules by name; `from .mod import y`
                    # targets the sibling module mod.
                    if rec["module"]:
                        root = rec["module"].split(".")[0]
                        if root in stems:
                            targets.append((root, root))
                    else:
                        for bound in rec["names"]:
                            if bound in stems:
                                targets.append((bound, bound))
                for target, label in targets:
                    if target == stem:
                        continue  # self-import recorded as a warning only
                    key = (stem, target)
                    if key not in edges:
                        edges[key] = {
                            "from": stem,
                            "to": target,
                            "module": label,
                            "line": rec["line"],
                        }
            warnings[stem] = cls._single_file_warnings(stem, imports, blocks)
        # Self-imports create self-loop cycles: record self-edges for
        # cycle detection without emitting them as dependency edges.
        self_loops = sorted(
            stem
            for stem in modules
            if warnings[stem]["self_imports"]
        )
        return {
            "modules": modules,
            "module_count": len(modules),
            "filenames": stems,
            "edges": [edges[key] for key in sorted(edges)],
            "edge_count": len(edges),
            "self_loops": self_loops,
            "warnings": warnings,
            "resolution": "filename-stem (flat sibling model; see module docstring for the documented limits)",
        }

    @classmethod
    def _tarjan_scc(cls, modules: list, adjacency: dict) -> list:
        """Iterative Tarjan strongly-connected components."""
        index_counter = [0]
        indices: dict = {}
        lowlink: dict = {}
        on_stack: dict = {}
        stack: list = []
        components: list = []
        for root in modules:
            if root in indices:
                continue
            work = [(root, iter(adjacency.get(root, ())))]
            indices[root] = lowlink[root] = index_counter[0]
            index_counter[0] += 1
            stack.append(root)
            on_stack[root] = True
            while work:
                node, neighbours = work[-1]
                advanced = False
                for nxt in neighbours:
                    if nxt not in indices:
                        indices[nxt] = lowlink[nxt] = index_counter[0]
                        index_counter[0] += 1
                        stack.append(nxt)
                        on_stack[nxt] = True
                        work.append((nxt, iter(adjacency.get(nxt, ()))))
                        advanced = True
                        break
                    if on_stack.get(nxt):
                        lowlink[node] = min(lowlink[node], indices[nxt])
                if advanced:
                    continue
                work.pop()
                if work:
                    parent = work[-1][0]
                    lowlink[parent] = min(lowlink[parent], lowlink[node])
                if lowlink[node] == indices[node]:
                    component = []
                    while True:
                        member = stack.pop()
                        on_stack[member] = False
                        component.append(member)
                        if member == node:
                            break
                    components.append(sorted(component))
        return components

    @classmethod
    def _graph_cycles(cls, graph: dict) -> list:
        """SCCs of size > 1 plus self-loop singletons, sorted."""
        adjacency: dict = {m: set() for m in graph["modules"]}
        for edge in graph["edges"]:
            adjacency[edge["from"]].add(edge["to"])
        for stem in graph["self_loops"]:
            adjacency[stem].add(stem)
        cycles = [
            component
            for component in cls._tarjan_scc(graph["modules"], adjacency)
            if len(component) > 1
            or (component[0] in adjacency[component[0]])
        ]
        return sorted(cycles)

    @classmethod
    def _run_analyze_files(cls, files: Any) -> dict:
        graph = cls._build_graph(files)
        cycles = cls._graph_cycles(graph)
        linked = set()
        for edge in graph["edges"]:
            linked.add(edge["from"])
            linked.add(edge["to"])
        for stem in graph["self_loops"]:
            linked.add(stem)
        orphans = [m for m in graph["modules"] if m not in linked]
        per_file_warnings = {
            stem: graph["warnings"][stem] for stem in graph["modules"]
        }
        total_warnings = sum(
            w["warning_count"] for w in per_file_warnings.values()
        )
        return {
            "mode": "analyze",
            "scope": "files",
            "module_count": graph["module_count"],
            "modules": graph["modules"],
            "edges": graph["edges"],
            "edge_count": graph["edge_count"],
            "cycles": cycles,
            "cycle_count": len(cycles),
            "orphans": orphans,
            "orphan_count": len(orphans),
            "self_loops": graph["self_loops"],
            "warnings": per_file_warnings,
            "warning_count": total_warnings,
            "resolution": graph["resolution"],
        }

    # ------------------------------------------------------------------ #
    # to_dot — DOT emission (DotGraphTool conventions, standalone)
    # ------------------------------------------------------------------ #

    @classmethod
    def _sanitize_id(cls, raw: str) -> str:
        """Sanitize one identifier deterministically.

        Every character outside ``[A-Za-z0-9_]`` becomes ``_`` (one
        per character); a leading digit gains a ``_`` prefix (the DOT
        lexer would otherwise read a numeral); a reserved DOT keyword
        gains a trailing ``_``.
        """
        sanitized = _INVALID_ID_CHARS.sub("_", raw)
        if sanitized[:1].isdigit():
            sanitized = "_" + sanitized
        if sanitized in _RESERVED_DOT:
            sanitized = sanitized + "_"
        return sanitized

    @classmethod
    def _render_label(cls, label: str) -> str:
        """Escape a label for a double-quoted DOT attribute value."""
        escaped = label.replace("\\", "\\\\").replace('"', '\\"')
        for form in _NEWLINE_FORMS:
            escaped = escaped.replace(form, "\\n")
        return f'"{escaped}"'

    @classmethod
    def _run_to_dot(cls, files: Any, name: Any) -> dict:
        graph_name = cls._validate_graph_name(name)
        graph = cls._build_graph(files)
        cycles = cls._graph_cycles(graph)
        cycle_nodes = {m for cycle in cycles for m in cycle}
        # A dependency edge is a cycle edge when both endpoints sit in
        # the SAME cycle (SCC), not merely both being cycle members.
        cycle_edges = set()
        for cycle in cycles:
            for edge in graph["edges"]:
                if edge["from"] in cycle and edge["to"] in cycle:
                    cycle_edges.add((edge["from"], edge["to"]))
            for stem in graph["self_loops"]:
                if stem in cycle:
                    cycle_edges.add((stem, stem))

        id_mapping: dict = {}
        id_map: dict = {}
        for module in graph["modules"]:
            sanitized = cls._sanitize_id(module)
            for other, other_sanitized in id_map.items():
                if sanitized == other_sanitized:
                    cls._invalid(
                        f"module stems collide after DOT sanitization: "
                        f"{other!r} and {module!r} both become {sanitized!r}"
                    )
            id_map[module] = sanitized
            if sanitized != module:
                id_mapping[module] = sanitized
        sanitized_graph_name = cls._sanitize_id(graph_name)
        if sanitized_graph_name != graph_name:
            id_mapping[graph_name] = sanitized_graph_name

        # Self-loop edges (self-imports) join the regular edges and
        # the merged list is re-sorted so emission stays deterministic.
        dot_edges = list(graph["edges"])
        for stem in graph["self_loops"]:
            dot_edges.append(
                {"from": stem, "to": stem, "module": stem, "line": 0}
            )
        dot_edges.sort(key=lambda edge: (edge["from"], edge["to"]))

        lines = [f"digraph {sanitized_graph_name} {{"]
        for module in graph["modules"]:
            attrs = [f"label={cls._render_label(graph['filenames'][module])}"]
            attrs.append("shape=box")
            if module in cycle_nodes:
                attrs.append("style=dotted")
            lines.append(f"    {id_map[module]} [{', '.join(attrs)}];")
        for edge in dot_edges:
            attrs = [f"label={cls._render_label(edge['module'])}"]
            if (edge["from"], edge["to"]) in cycle_edges:
                attrs.append("style=dashed")
            lines.append(
                f"    {id_map[edge['from']]} -> {id_map[edge['to']]} "
                f"[{', '.join(attrs)}];"
            )
        lines.append("}")
        result: dict = {
            "mode": "to_dot",
            "graph_name": graph_name,
            "result": "\n".join(lines),
            "node_count": graph["module_count"],
            "edge_count": len(dot_edges),
            "cycle_count": len(cycles),
            "cycles": cycles,
        }
        if id_mapping:
            result["id_mapping"] = id_mapping
        return result
