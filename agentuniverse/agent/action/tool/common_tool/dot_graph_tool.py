#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: dot_graph_tool.py

"""Graphviz DOT source generation tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency Graphviz DOT source
generator aimed at visualization agents. The tool never renders and
never shells out to the ``dot`` binary — it only *generates* DOT
source text from small structured specifications, plus a basic syntax
lint and a parse-back stats pass, so agents can hand the output to any
Graphviz-compatible renderer (``dot``, GraphvizOnline, Gephi import,
CI diagram pipelines, ...).

Supported modes:

* ``digraph`` — build ``digraph <name> { ... }`` source from a list of
  ``nodes`` (``{id, label?, shape?, style?, fillcolor?, fontsize?}``),
  ``edges`` (``{from, to, label?, style?, dir?, weight?}``) and
  optional ``clusters`` (``{name, label?, node_ids}`` → ``subgraph
  cluster_*`` blocks). Edge endpoints accept the ``node:port`` compass
  / record-field syntax (``{"from": "tbl:port1"}``).
* ``graph`` — the undirected variant (``--`` operators, no ``dir``).
* ``validate`` — run a *basic sanity check* over a DOT source string:
  graph declaration keyword, balanced ``{}`` / ``[]``, unterminated
  double quotes, statement lines missing the (optional but checked)
  trailing semicolon, edge operators that contradict the declared
  graph kind (``--`` inside a digraph, ``->`` inside an undirected
  graph), and edge endpoints referencing nodes that are
  never declared. This is deliberately NOT a full DOT parser — it is
  a cheap line-oriented heuristic pass that catches the most common
  breakages; a clean validate result does not guarantee ``dot``
  renders the file.
* ``stats`` — parse a DOT source back and report ``node_count`` /
  ``edge_count`` / ``cluster_count`` / ``graph_type`` using the same
  honest line-oriented heuristic.

Determinism and escaping conventions (documented contract):

* Node / graph / cluster identifiers are sanitized to
  ``[A-Za-z0-9_]``: every invalid character becomes ``_`` (one per
  character). A sanitized id that *starts with a digit* is prefixed
  with ``_`` (the DOT lexer would read a leading digit as a numeral);
  a sanitized id that equals a reserved DOT keyword (``digraph``,
  ``graph``, ``subgraph``, ``node``, ``edge``, ``strict``) gets a
  trailing ``_``. Changed ids are reported in an ``id_mapping`` dict
  (original -> sanitized), mirroring the MermaidFlowTool reporting.
  Duplicate raw ids and distinct raw ids that collide after
  sanitization are errors — silently renaming would render the wrong
  graph.
* Cluster names additionally follow the Graphviz rule that only
  ``cluster*`` names draw a box: a cluster name that does not already
  start with ``cluster`` is prefixed with ``cluster_`` and the rename
  is reported in ``id_mapping`` too.
* Labels are always emitted double-quoted; inside the quotes a
  literal backslash becomes ``\\\\``, a double quote becomes ``\\"``
  and every newline form (``\\n``, ``\\r\\n``, ``\\r``) becomes the
  two characters ``\\n`` so Graphviz breaks the line. Other control
  characters are rejected up-front by validation.
* Attributes are emitted in a stable documented order — nodes:
  ``label, shape, style, fillcolor, fontsize``; edges: ``label,
  style, dir, weight`` — so the same spec always yields
  byte-identical DOT source. ``label`` and ``fillcolor`` values are
  always emitted double-quoted (a ``#``-hex color is not a valid
  bare DOT token). ``shape`` is always emitted (the tool
  default ``box`` deliberately differs from Graphviz's own default);
  the other attributes are emitted only when provided. Every node /
  edge / cluster-label statement is terminated with ``;`` so the
  generated source passes the tool's own ``validate`` mode cleanly.

Input validation is strict and happens before any generation:
malformed parameters (wrong types, empty node lists, unknown mode /
shape / style / dir, bad colors or font sizes, duplicate ids, unknown
edge endpoints, oversized inputs) raise a ``ValueError``, mirroring
the other common tools. Edge endpoints (the node part of ``from`` /
``to``) must reference *declared* node ids; unknown endpoints produce
one error listing every one of them.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Characters that may appear in a sanitized DOT identifier.
_INVALID_ID_CHARS = re.compile(r"[^A-Za-z0-9_]")
# Valid bare port reference (identifier form is required).
_VALID_PORT = re.compile(r"^[A-Za-z0-9_]+$")
# Control characters rejected in every id / name / label field (the
# newline / carriage-return label forms are normalized separately).
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
# Node label newline forms accepted and normalized to the two
# characters '\' 'n' (plain str.replace — re.sub replacement
# templates would re-interpret the backslash escape).
_NEWLINE_FORMS = ("\r\n", "\r", "\n")
# A color value: #rgb / #rrggbb / #rrggbbaa hex or an alphabetic name.
_COLOR = re.compile(
    r"^(#[0-9A-Fa-f]{3}|#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{8}|[A-Za-z]+)$"
)
# A graph declaration line (the file header).
_GRAPH_DECL = re.compile(r"(?i)^\s*(strict\s+)?(digraph|graph)\b")
# A subgraph header whose name starts with 'cluster'.
_SUBGRAPH_CLUSTER = re.compile(r"(?i)^\s*subgraph\s+cluster[A-Za-z0-9_]*")
# A bare node statement: 'id' or 'id [attrs]' with an optional ';'.
_BARE_STATEMENT = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)(\s*\[[^\]]*\])?\s*;?\s*$"
)
# An attribute-assignment line (label=..., shape=..., ...).
_ATTR_KEYWORD_LINE = re.compile(
    r"(?i)^\s*(label|shape|style|fillcolor|fontsize|color|weight|dir|rank)"
    r"\s*="
)
# A trailing '[attrs]' block (with an optional ';') on an edge line.
_EDGE_ATTRS = re.compile(r"\[[^\]]*\]\s*;?\s*$")
# A closing-brace-only line.
_CLOSING_LINE = re.compile(r"^\s*\}\s*;?\s*$")


class DotGraphTool(Tool):
    """Graphviz DOT source generator built purely on the stdlib.

    The tool generates ``digraph`` / ``graph`` DOT source from
    structured specifications, lints DOT source strings and parses
    basic counts back out of DOT source; it never renders anything
    and has no dependency on the Graphviz binaries.

    Class attributes:
        MAX_NODES (int): Upper bound on the ``nodes`` list length.
        MAX_EDGES (int): Upper bound on the ``edges`` list length.
        MAX_CLUSTERS (int): Upper bound on the ``clusters`` list.
        MAX_ID_CHARS (int): Upper bound on any single id / name.
        MAX_TEXT_CHARS (int): Upper bound on any single label.
        MAX_SOURCE_CHARS (int): Upper bound on validate / stats
            ``source``.
        MAX_FONT_SIZE (float): Upper bound on ``fontsize``.
        MAX_ABS_WEIGHT (float): Upper bound on ``abs(weight)``.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "dot_graph_tool"
    description: str = (
        "Graphviz DOT source generation tool — pure Python stdlib, "
        "no rendering and no Graphviz binary dependency. Builds "
        "directed-graph DOT source from nodes/edges/clusters specs "
        "(mode='digraph'), the undirected variant (mode='graph'), "
        "runs a basic sanity lint (declaration keyword, balanced "
        "braces/brackets, unterminated quotes, missing optional "
        "semicolons, edge operators that contradict the declared "
        "graph kind, unknown edge endpoints) over DOT source "
        "(mode='validate'), and parses node/edge/cluster counts "
        "back out of DOT source (mode='stats')."
    )

    MODES: ClassVar[tuple] = ("digraph", "graph", "validate", "stats")
    SHAPES: ClassVar[tuple] = (
        "box", "ellipse", "diamond", "circle", "hexagon", "cylinder",
        "record",
    )
    NODE_STYLES: ClassVar[tuple] = (
        "filled", "dotted", "dashed", "bold", "rounded",
    )
    EDGE_STYLES: ClassVar[tuple] = ("solid", "dashed", "dotted", "bold")
    DIRS: ClassVar[tuple] = ("none", "both", "back")
    # Reserved DOT keywords that must not survive as bare identifiers.
    RESERVED: ClassVar[tuple] = (
        "digraph", "graph", "subgraph", "node", "edge", "strict",
    )
    # Attribute emission order — part of the documented contract.
    NODE_KEYS: ClassVar[tuple] = (
        "id", "label", "shape", "style", "fillcolor", "fontsize",
    )
    EDGE_KEYS: ClassVar[tuple] = (
        "from", "to", "label", "style", "dir", "weight",
    )
    CLUSTER_KEYS: ClassVar[tuple] = ("name", "label", "node_ids")
    DEFAULT_GRAPH_NAME: ClassVar[str] = "G"
    CLUSTER_PREFIX: ClassVar[str] = "cluster_"

    MAX_NODES: ClassVar[int] = 500
    MAX_EDGES: ClassVar[int] = 1000
    MAX_CLUSTERS: ClassVar[int] = 100
    MAX_ID_CHARS: ClassVar[int] = 200
    MAX_TEXT_CHARS: ClassVar[int] = 2000
    MAX_SOURCE_CHARS: ClassVar[int] = 100_000
    MAX_FONT_SIZE: ClassVar[float] = 1000.0
    MAX_ABS_WEIGHT: ClassVar[float] = 10_000.0

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        name: Any = None,
        nodes: Any = None,
        edges: Any = None,
        clusters: Any = None,
        source: Any = None,
    ) -> dict[str, Any]:
        """Generate, validate or stat Graphviz DOT source.

        Args:
            mode (str): One of ``digraph``, ``graph``, ``validate``
                or ``stats``.
            name (str): Graph name (sanitized like node ids; defaults
                to ``G``). Generation modes only.
            nodes (list[dict]): Nodes, each ``{id, label?, shape?,
                style?, fillcolor?, fontsize?}``; ``id`` is required,
                ``shape`` defaults to ``box`` and is always emitted.
                Required for the generation modes.
            edges (list[dict]): Edges, each ``{from, to, label?,
                style?, dir?, weight?}``; ``from`` / ``to`` reference
                declared node ids and accept the ``node:port`` form,
                ``dir`` (digraph only) is none/both/back. Optional.
            clusters (list[dict]): Optional clusters, each ``{name,
                label?, node_ids}``; the name is prefixed with
                ``cluster_`` when needed so Graphviz draws the box,
                and ``node_ids`` must reference declared nodes (each
                node in at most one cluster).
            source (str): The DOT source to validate / stat.

        Returns:
            Dict[str, Any]: For the generation modes, a ``result``
                string with the DOT source plus ``graph_name``,
                counts and ``id_mapping`` whenever any id was
                sanitized or renamed. For ``validate``, ``ok``,
                ``lines_checked`` and a list of ``issues`` (each
                ``{line, check, severity, message}``). For ``stats``,
                ``node_count`` / ``edge_count`` / ``cluster_count`` /
                ``graph_type``.

        Raises:
            ValueError: If any parameter is malformed (before any
                generation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode in ("digraph", "graph"):
            return self._run_generate(mode, name, nodes, edges, clusters)
        if mode == "validate":
            return self._run_validate(source)
        return self._run_stats(source)

    # ------------------------------------------------------------------ #
    # Input validation helpers (pure — raise before any generation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"dot_graph_tool: {message}")

    @classmethod
    def _validate_id_like(cls, value: Any, what: str) -> str:
        """Validate a raw identifier (node id / graph / cluster name)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{what} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{what} must be a non-empty string (got '')")
        if len(value) > cls.MAX_ID_CHARS:
            cls._invalid(
                f"{what} exceeds the {cls.MAX_ID_CHARS}-character limit "
                f"(got {len(value)} characters)"
            )
        if _CONTROL_CHARS.search(value) or "\n" in value or "\r" in value:
            cls._invalid(
                f"{what} must not contain control characters such as "
                "newlines or tabs"
            )
        return value

    @classmethod
    def _validate_label(cls, value: Any, what: str) -> str:
        """Validate a label field (newlines allowed and normalized)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{what} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{what} must be a non-empty string (got '')")
        if len(value) > cls.MAX_TEXT_CHARS:
            cls._invalid(
                f"{what} exceeds the {cls.MAX_TEXT_CHARS}-character limit "
                f"(got {len(value)} characters)"
            )
        if _CONTROL_CHARS.search(value):
            cls._invalid(
                f"{what} must not contain control characters other than "
                "newlines"
            )
        return value

    @classmethod
    def _validate_number(cls, value: Any, what: str, upper: float) -> None:
        """Validate a numeric attribute (finite, within the abs cap)."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            cls._invalid(f"{what} must be a number (got {value!r})")
        number = float(value)
        if number != number or number in (float("inf"), float("-inf")):
            cls._invalid(f"{what} must be a finite number (got {value!r})")
        if abs(number) > upper:
            cls._invalid(f"{what} exceeds the {upper} limit (got {value!r})")

    @classmethod
    def _validate_color(cls, value: Any, what: str) -> None:
        """Validate a color attribute (hex form or alphabetic name)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{what} must be a color string (got {value!r})")
        if not _COLOR.match(value):
            cls._invalid(
                f"{what} must be a hex color like #2196f3 / #f00 / "
                "#2196f380 or an alphabetic color name (got {value!r})"
            )

    @classmethod
    def _check_spec_keys(cls, spec: Any, keys: tuple, index: int, what: str) -> None:
        """Reject non-dict specs and unknown keys (strict validation)."""
        if not isinstance(spec, dict):
            cls._invalid(f"{what}[{index}] must be a dict (got {spec!r})")
        unknown = sorted(set(spec) - set(keys))
        if unknown:
            cls._invalid(
                f"{what}[{index}] has unknown key(s): {', '.join(unknown)} "
                f"(allowed: {', '.join(keys)})"
            )

    @classmethod
    def _require_key(cls, spec: dict, key: str, index: int, what: str) -> None:
        """Reject specs missing a required key."""
        if key not in spec:
            cls._invalid(f"{what}[{index}].{key} is required")

    @classmethod
    def _validate_list(
        cls, value: Any, what: str, upper: int, required: bool
    ) -> list:
        """Validate a spec list parameter."""
        if value is None:
            if required:
                cls._invalid(f"{what} is required (a list of specs)")
            return []
        if isinstance(value, dict) or not isinstance(value, (list, tuple)):
            cls._invalid(f"{what} must be a list of specs (got {value!r})")
        if len(value) > upper:
            cls._invalid(
                f"{what} exceeds the {upper}-item limit (got {len(value)} items)"
            )
        if required and not value:
            cls._invalid(f"{what} must contain at least one spec")
        return list(value)

    @classmethod
    def _parse_endpoint(cls, value: Any, what: str) -> tuple:
        """Split a raw ``node:port`` endpoint into (node, port or None)."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"{what} must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid(f"{what} must be a non-empty string (got '')")
        node, sep, port = value.partition(":")
        if sep:
            if not port:
                cls._invalid(
                    f"{what} has an empty port after ':' (got {value!r})"
                )
            if len(port) > cls.MAX_ID_CHARS:
                cls._invalid(
                    f"{what} port exceeds the {cls.MAX_ID_CHARS}-character "
                    f"limit (got {len(port)} characters)"
                )
            if not _VALID_PORT.match(port):
                cls._invalid(
                    f"{what} port must match [A-Za-z0-9_]+ (got {value!r})"
                )
        cls._validate_id_like(node, f"{what} node part")
        return node, (port if sep else None)

    # ------------------------------------------------------------------ #
    # Deterministic id sanitization (mirrors MermaidFlowTool reporting)
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
        if sanitized in cls.RESERVED:
            sanitized = sanitized + "_"
        return sanitized

    @classmethod
    def _build_id_map(cls, raw_ids: list) -> dict:
        """Sanitize node identifiers deterministically, or error.

        Returns the original -> sanitized mapping. Distinct raw ids
        that collide after sanitization are an error: silently
        renaming one of them would render the wrong graph.
        """
        mapping: dict = {}
        for raw in raw_ids:
            sanitized = cls._sanitize_id(raw)
            for other, other_sanitized in mapping.items():
                if sanitized == other_sanitized:
                    cls._invalid(
                        f"ids collide after sanitization: {other!r} and "
                        f"{raw!r} both become {sanitized!r}"
                    )
            mapping[raw] = sanitized
        return mapping

    # ------------------------------------------------------------------ #
    # Label rendering (DOT escaping conventions)
    # ------------------------------------------------------------------ #

    @classmethod
    def _render_label(cls, label: str) -> str:
        """Escape a label for a double-quoted DOT attribute value.

        Backslash becomes ``\\\\`` (an escaped backslash), the double
        quote becomes ``\\"`` and every newline form becomes the
        two-character ``\\n`` line break; the result is wrapped in
        double quotes.
        """
        escaped = label.replace("\\", "\\\\").replace('"', '\\"')
        for form in _NEWLINE_FORMS:
            escaped = escaped.replace(form, "\\n")
        return f'"{escaped}"'

    @classmethod
    def _format_number(cls, value: Any) -> str:
        """Render a numeric attribute deterministically (int stays int)."""
        if isinstance(value, int):
            return str(value)
        text = f"{float(value):.6f}".rstrip("0").rstrip(".")
        return text if text else "0"

    @staticmethod
    def _mask_quotes(line: str) -> str:
        """Blank out the contents of balanced double-quoted spans.

        Backslash-escaped characters (``\\"``, ``\\n``) inside the
        span are consumed so an escaped quote does not end the span.
        The quotes themselves are kept so later checks can still see
        them; anything inside a quoted label (braces, brackets, //,
        arrow-looking text) becomes spaces and cannot confuse the
        structural heuristics.
        """
        def _blank(match: re.Match) -> str:
            return '"' + " " * (len(match.group(0)) - 2) + '"'

        return re.sub(r'"(?:[^"\\\n]|\\.)*"', _blank, line)

    # ------------------------------------------------------------------ #
    # digraph / graph generation
    # ------------------------------------------------------------------ #

    def _run_generate(
        self,
        mode: str,
        name: Any,
        nodes: Any,
        edges: Any,
        clusters: Any,
    ) -> dict:
        """Build DOT source for the directed / undirected modes."""
        directed = mode == "digraph"
        arrow = "->" if directed else "--"

        if name is None:
            raw_name = self.DEFAULT_GRAPH_NAME
        else:
            self._validate_id_like(name, "name")
            raw_name = name

        node_specs = self._validate_list(nodes, "nodes", self.MAX_NODES, True)
        edge_specs = self._validate_list(edges, "edges", self.MAX_EDGES, False)
        cluster_specs = self._validate_list(
            clusters, "clusters", self.MAX_CLUSTERS, False
        )

        # --- nodes (validated first, in input order) -------------------- #
        parsed_nodes: list = []
        for index, spec in enumerate(node_specs):
            self._check_spec_keys(spec, self.NODE_KEYS, index, "nodes")
            self._require_key(spec, "id", index, "nodes")
            self._validate_id_like(spec["id"], f"nodes[{index}].id")
            if "label" in spec:
                self._validate_label(spec["label"], f"nodes[{index}].label")
            if spec.get("shape", "box") not in self.SHAPES:
                self._invalid(
                    f"nodes[{index}].shape must be one of: "
                    f"{', '.join(self.SHAPES)} (got {spec.get('shape')!r})"
                )
            if "style" in spec and spec["style"] not in self.NODE_STYLES:
                self._invalid(
                    f"nodes[{index}].style must be one of: "
                    f"{', '.join(self.NODE_STYLES)} (got {spec['style']!r})"
                )
            if "fillcolor" in spec:
                self._validate_color(
                    spec["fillcolor"], f"nodes[{index}].fillcolor"
                )
            if "fontsize" in spec:
                self._validate_number(
                    spec["fontsize"], f"nodes[{index}].fontsize",
                    self.MAX_FONT_SIZE,
                )
                if float(spec["fontsize"]) <= 0:
                    self._invalid(
                        f"nodes[{index}].fontsize must be > 0 "
                        f"(got {spec['fontsize']!r})"
                    )
            if any(spec["id"] == seen["id"] for seen in parsed_nodes):
                self._invalid(f"duplicate node id: {spec['id']!r}")
            parsed_nodes.append(spec)

        raw_ids = [spec["id"] for spec in parsed_nodes]
        node_id_set = set(raw_ids)
        id_map = self._build_id_map(raw_ids)
        sanitized_node_ids = set(id_map.values())
        if raw_name != self.DEFAULT_GRAPH_NAME:
            graph_name = self._sanitize_id(raw_name)
            id_map[raw_name] = graph_name
        else:
            graph_name = raw_name

        # --- clusters ---------------------------------------------------- #
        parsed_clusters: list = []
        clustered: dict = {}
        cluster_names: dict = {}
        for index, spec in enumerate(cluster_specs):
            self._check_spec_keys(spec, self.CLUSTER_KEYS, index, "clusters")
            self._require_key(spec, "name", index, "clusters")
            self._validate_id_like(spec["name"], f"clusters[{index}].name")
            if "label" in spec:
                self._validate_label(spec["label"], f"clusters[{index}].label")
            member_ids = spec.get("node_ids")
            if (
                member_ids is None
                or isinstance(member_ids, (str, dict))
                or not isinstance(member_ids, (list, tuple))
                or not member_ids
            ):
                self._invalid(
                    f"clusters[{index}].node_ids must be a non-empty list "
                    f"of declared node ids (got {member_ids!r})"
                )
            cluster_name = self._sanitize_id(spec["name"])
            if not cluster_name.startswith("cluster"):
                cluster_name = self.CLUSTER_PREFIX + cluster_name
            if cluster_name in cluster_names:
                self._invalid(
                    "cluster names collide after sanitization: "
                    f"{cluster_names[cluster_name]!r} and {spec['name']!r} "
                    f"both become {cluster_name!r}"
                )
            if cluster_name in sanitized_node_ids:
                self._invalid(
                    f"cluster name {spec['name']!r} collides with a node id "
                    f"after sanitization (both become {cluster_name!r})"
                )
            cluster_names[cluster_name] = spec["name"]
            id_map[spec["name"]] = cluster_name
            for position, member in enumerate(member_ids):
                if member not in node_id_set:
                    self._invalid(
                        f"clusters[{index}].node_ids[{position}] is not a "
                        f"declared node id (got {member!r})"
                    )
                if member in clustered:
                    self._invalid(
                        f"clusters[{index}].node_ids[{position}] ({member!r}) "
                        "is already in another cluster"
                    )
                clustered[member] = index
            parsed_clusters.append((spec, cluster_name))

        # --- edges -------------------------------------------------------- #
        parsed_edges: list = []
        for index, spec in enumerate(edge_specs):
            self._check_spec_keys(spec, self.EDGE_KEYS, index, "edges")
            for key in ("from", "to"):
                self._require_key(spec, key, index, "edges")
            endpoints = []
            for key in ("from", "to"):
                node, _port = self._parse_endpoint(
                    spec[key], f"edges[{index}].{key}"
                )
                endpoints.append(node)
            unknown = sorted({node for node in endpoints if node not in node_id_set})
            if unknown:
                self._invalid(
                    f"edges[{index}] references unknown node id(s): "
                    f"{', '.join(repr(u) for u in unknown)} — every edge "
                    "endpoint must be declared in nodes"
                )
            if "label" in spec:
                self._validate_label(spec["label"], f"edges[{index}].label")
            if spec.get("style", "solid") not in self.EDGE_STYLES:
                self._invalid(
                    f"edges[{index}].style must be one of: "
                    f"{', '.join(self.EDGE_STYLES)} (got {spec.get('style')!r})"
                )
            if "dir" in spec:
                if not directed:
                    self._invalid(
                        f"edges[{index}].dir is only valid in the digraph "
                        "mode (undirected edges have no arrowheads)"
                    )
                if spec["dir"] not in self.DIRS:
                    self._invalid(
                        f"edges[{index}].dir must be one of: "
                        f"{', '.join(self.DIRS)} (got {spec['dir']!r})"
                    )
            if "weight" in spec:
                self._validate_number(
                    spec["weight"], f"edges[{index}].weight",
                    self.MAX_ABS_WEIGHT,
                )
            parsed_edges.append(spec)

        # --- emission (deterministic order) ------------------------------- #
        def node_statement(spec: dict, indent: str) -> str:
            attrs = []
            if "label" in spec:
                attrs.append(f"label={self._render_label(spec['label'])}")
            attrs.append(f"shape={spec.get('shape', 'box')}")
            if "style" in spec:
                attrs.append(f"style={spec['style']}")
            if "fillcolor" in spec:
                attrs.append(f'fillcolor="{spec["fillcolor"]}"')
            if "fontsize" in spec:
                attrs.append(
                    f"fontsize={self._format_number(spec['fontsize'])}"
                )
            return f"{indent}{id_map[spec['id']]} [{', '.join(attrs)}];"

        def edge_statement(spec: dict) -> str:
            parts = []
            for key in ("from", "to"):
                node, port = self._parse_endpoint(spec[key], key)
                rendered = id_map[node]
                if port:
                    rendered = f"{rendered}:{port}"
                parts.append(rendered)
            attrs = []
            if "label" in spec:
                attrs.append(f"label={self._render_label(spec['label'])}")
            if "style" in spec:
                attrs.append(f"style={spec['style']}")
            if "dir" in spec:
                attrs.append(f"dir={spec['dir']}")
            if "weight" in spec:
                attrs.append(
                    f"weight={self._format_number(spec['weight'])}"
                )
            middle = f" {arrow} ".join(parts)
            if attrs:
                return f"    {middle} [{', '.join(attrs)}];"
            return f"    {middle};"

        lines = [f"{mode} {graph_name} {{"]
        for spec in parsed_nodes:
            if spec["id"] not in clustered:
                lines.append(node_statement(spec, "    "))
        for spec, cluster_name in parsed_clusters:
            lines.append(f"    subgraph {cluster_name} {{")
            if "label" in spec:
                lines.append(
                    f"        label={self._render_label(spec['label'])};"
                )
            for member in spec["node_ids"]:
                member_spec = next(
                    n for n in parsed_nodes if n["id"] == member
                )
                lines.append(node_statement(member_spec, "        "))
            lines.append("    }")
        for spec in parsed_edges:
            lines.append(edge_statement(spec))
        lines.append("}")

        result: dict = {
            "mode": mode,
            "graph_name": graph_name,
            "result": "\n".join(lines),
            "node_count": len(parsed_nodes),
            "edge_count": len(parsed_edges),
            "cluster_count": len(parsed_clusters),
        }
        changed = {raw: san for raw, san in id_map.items() if raw != san}
        if changed:
            result["id_mapping"] = changed
        return result

    # ------------------------------------------------------------------ #
    # validate mode — basic DOT lint (honest subset, see module docstring)
    # ------------------------------------------------------------------ #

    def _run_validate(self, source: Any) -> dict:
        """Run the basic line-oriented DOT sanity checks."""
        if source is None or isinstance(source, bool) or not isinstance(source, str):
            self._invalid(f"source must be a non-empty string (got {source!r})")
        if not source:
            self._invalid("source must be a non-empty string (got '')")
        if len(source) > self.MAX_SOURCE_CHARS:
            self._invalid(
                f"source exceeds the {self.MAX_SOURCE_CHARS}-character "
                f"limit (got {len(source)} characters)"
            )

        issues: list = []
        raw_lines = source.split("\n")
        declared: set = set()
        warned: set = set()
        depth = 0
        bracket_depth = 0
        saw_declaration = False
        graph_directed = None

        for number, raw_line in enumerate(raw_lines, start=1):
            masked = self._mask_quotes(raw_line)
            stripped = re.sub(r"//.*$", "", masked).strip()

            if stripped.count('"') % 2 == 1:
                issues.append({
                    "line": number,
                    "check": "quotes",
                    "severity": "error",
                    "message": "unterminated double quote (quotes do not "
                               "span lines in this lint)",
                })
                continue

            if not stripped:
                continue

            is_declaration_line = not saw_declaration
            if is_declaration_line:
                saw_declaration = True
                declaration = _GRAPH_DECL.match(stripped)
                if not declaration:
                    issues.append({
                        "line": number,
                        "check": "declaration",
                        "severity": "error",
                        "message": "DOT source must start with a "
                                   "'digraph' or 'graph' (optionally "
                                   "'strict') declaration",
                    })
                else:
                    graph_directed = declaration.group(2).lower() == "digraph"

            depth += stripped.count("{") - stripped.count("}")
            if depth < 0:
                issues.append({
                    "line": number,
                    "check": "balanced_braces",
                    "severity": "error",
                    "message": "unbalanced braces: more '}' than '{'",
                })
                depth = 0
            bracket_depth += stripped.count("[") - stripped.count("]")
            if bracket_depth < 0:
                issues.append({
                    "line": number,
                    "check": "balanced_brackets",
                    "severity": "error",
                    "message": "unbalanced brackets: more ']' than '['",
                })
                bracket_depth = 0

            if _CLOSING_LINE.match(stripped):
                continue

            is_edge = ("->" in stripped) or ("--" in stripped)
            if (
                not is_declaration_line
                and graph_directed is not None
                and "<" not in stripped
            ):
                if graph_directed and "--" in stripped:
                    issues.append({
                        "line": number,
                        "check": "edge_operator",
                        "severity": "error",
                        "message": "undirected edge operator '--' in a "
                                   "digraph (digraph statements must use "
                                   "'->')",
                    })
                elif not graph_directed and "->" in stripped:
                    issues.append({
                        "line": number,
                        "check": "edge_operator",
                        "severity": "error",
                        "message": "directed edge operator '->' in an "
                                   "undirected graph (undirected statements "
                                   "must use '--')",
                    })
            bare = None if is_edge else _BARE_STATEMENT.match(stripped)
            if is_edge:
                statement = _EDGE_ATTRS.sub("", stripped).rstrip(";").strip()
                for endpoint in re.split(r"->|--", statement):
                    node = endpoint.strip().split(":")[0].strip()
                    if (
                        node
                        and _VALID_PORT.match(node)
                        and node not in self.RESERVED
                        and node not in declared
                        and node not in warned
                    ):
                        issues.append({
                            "line": number,
                            "check": "edge_endpoints",
                            "severity": "warning",
                            "message": f"edge references node {node!r} "
                                       "that is never declared",
                        })
                        warned.add(node)
            elif (
                bare
                and bare.group(1) not in self.RESERVED
                and not _ATTR_KEYWORD_LINE.match(stripped)
            ):
                declared.add(bare.group(1))

            looks_statement = bool(
                is_edge or bare is not None or "[" in stripped
            )
            if (
                looks_statement
                and not stripped.endswith(";")
                and not stripped.endswith("{")
                and not stripped.endswith("}")
            ):
                issues.append({
                    "line": number,
                    "check": "semicolons",
                    "severity": "warning",
                    "message": "statement does not end with ';' "
                               "(optional in DOT, but consistent use "
                               "is checked)",
                })

        if depth != 0:
            issues.append({
                "line": len(raw_lines),
                "check": "balanced_braces",
                "severity": "error",
                "message": f"unbalanced braces: {depth} '{{' never closed",
            })
        if bracket_depth != 0:
            issues.append({
                "line": len(raw_lines),
                "check": "balanced_brackets",
                "severity": "error",
                "message": "unbalanced brackets: "
                           f"{bracket_depth} '[' never closed",
            })

        return {
            "mode": "validate",
            "ok": not any(issue["severity"] == "error" for issue in issues),
            "lines_checked": len(raw_lines),
            "issues": issues,
        }

    # ------------------------------------------------------------------ #
    # stats mode — parse node/edge/cluster counts back out of DOT source
    # ------------------------------------------------------------------ #

    def _run_stats(self, source: Any) -> dict:
        """Count nodes / edges / clusters with the same heuristic."""
        if source is None or isinstance(source, bool) or not isinstance(source, str):
            self._invalid(f"source must be a non-empty string (got {source!r})")
        if not source:
            self._invalid("source must be a non-empty string (got '')")
        if len(source) > self.MAX_SOURCE_CHARS:
            self._invalid(
                f"source exceeds the {self.MAX_SOURCE_CHARS}-character "
                f"limit (got {len(source)} characters)"
            )

        node_count = 0
        edge_count = 0
        cluster_count = 0
        graph_type = None
        for raw_line in source.split("\n"):
            masked = self._mask_quotes(raw_line)
            stripped = re.sub(r"//.*$", "", masked).strip()
            if not stripped:
                continue
            if graph_type is None:
                declaration = _GRAPH_DECL.match(stripped)
                if declaration:
                    graph_type = declaration.group(2).lower()
            if _SUBGRAPH_CLUSTER.match(stripped):
                cluster_count += 1
                continue
            if "->" in stripped or "--" in stripped:
                edge_count += 1
                continue
            if _ATTR_KEYWORD_LINE.match(stripped):
                continue
            if _CLOSING_LINE.match(stripped):
                continue
            bare = _BARE_STATEMENT.match(stripped)
            if bare and bare.group(1) not in self.RESERVED:
                node_count += 1

        return {
            "mode": "stats",
            "node_count": node_count,
            "edge_count": edge_count,
            "cluster_count": cluster_count,
            "graph_type": graph_type,
        }
