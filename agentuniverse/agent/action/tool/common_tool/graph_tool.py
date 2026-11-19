#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: graph_tool.py

"""Graph analysis tool over edge lists, built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency graph utility agents
can call on arbitrary edge lists. A natural pairing is knowledge-graph
pipelines — e.g. the ``CooccurrenceRelationExtractor`` pre-processing
component (PR #3554) stamps co-occurrence edges into document metadata —
while this tool accepts *any* ``[{source, target, weight?, directed?}]``
edge list, not only extracted metadata.

Five modes are supported:

* ``build`` — validate an edge list and build the adjacency structure:
  an adjacency dict (``{node: {neighbor: summed_weight}}``, keys sorted
  for determinism), node / unique-edge counts, and reports for isolated
  nodes, self-loops and duplicate edges. Undirected (the default) merges
  ``a-b`` and ``b-a`` into one edge, summing weights.
* ``degree`` — per-node degree sorted descending (ties broken by node
  name ascending), with ``in`` / ``out`` / ``total`` degrees when the
  graph is directed. An optional ``top_n`` truncates the list. Nodes
  whose total degree exceeds ``mean + stdev`` (population stdev) are
  flagged as hubs.
* ``bfs`` — breadth-first traversal from a ``start`` node with an
  optional ``max_depth``: the reachable set with per-node depth plus the
  deterministic visit order (neighbours explored in sorted order).
* ``path`` — shortest path between ``start`` and ``end`` via
  unweighted BFS (edge weights are deliberately ignored, as
  documented); a start that equals the end yields the trivial path, an
  unreachable end yields a ``found: false`` verdict instead of an
  error. The ``all_shortest`` option enumerates every shortest path
  (lexicographically sorted, capped at 10, ``truncated`` flag when more
  exist).
* ``components`` — connected components sorted by size (desc); for a
  directed graph the weakly-connected components (direction ignored).
  Member lists are sorted and capped per component via ``max_members``.

Direction semantics: the global ``directed`` option (default ``false``)
applies to every edge unless the edge carries its own boolean
``directed`` field. If *any* edge resolves to directed the graph is
treated as directed: ``a->b`` and ``b->a`` are then distinct edges, an
undirected edge contributes in both directions, degree reports split
into in/out, and BFS / shortest-path traversal follows out-edges only.

Duplicate handling: repeated edges (after direction normalisation) are
merged into a single edge whose weight is the sum of the occurrences;
``build`` reports every merged group and ``degree`` counts merged
edges. A self-loop counts as degree 2 (undirected) or 1 in + 1 out
(directed).

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty or oversized edge lists,
malformed edge shapes, non-string node ids, non-numeric / non-finite /
boolean weights, unknown mode, non-positive ``top_n`` / ``max_members``,
negative ``max_depth``, unknown ``start`` / ``end`` nodes — the error
lists how many nodes are available) raise a ``ValueError``, mirroring
the other common tools. The only content-level outcome returned as data
instead of raising is the ``path`` mode's no-path verdict.
"""

import math
import statistics
from collections import deque
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class GraphTool(Tool):
    """Graph analysis tool over edge lists, pure Python stdlib.

    Attributes:
        max_edges (int): Upper bound on the number of input edges;
            longer edge lists are rejected before any computation.
        max_all_shortest_paths (int): Cap on the number of shortest
            paths returned (and enumerated) by the ``path`` mode with
            ``all_shortest=true``.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "graph_tool"
    description: str = (
        "Graph analysis tool — pure Python stdlib, no network required. "
        "Analyzes arbitrary edge lists [{source, target, weight?, "
        "directed?}] with five modes: build (adjacency dict + node/edge "
        "counts + isolated/self-loop/duplicate-edge reports, undirected "
        "by default and merging a-b with b-a), degree (per-node degree "
        "sorted descending, in/out/total for directed graphs, top_n "
        "option, hubs flagged at degree > mean + stdev), bfs (reachable "
        "set with per-node depths and deterministic visit order, "
        "max_depth option), path (unweighted BFS shortest path between "
        "two nodes or a no-path verdict, all_shortest option capped at "
        "10), and components (connected components sorted by size, "
        "weakly-connected for directed graphs, capped member lists)."
    )

    MODES: ClassVar[tuple] = ("build", "degree", "bfs", "path", "components")

    max_edges: int = 10_000
    max_all_shortest_paths: int = 10

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        edges: Any = None,
        directed: Any = None,
        start: Any = None,
        end: Any = None,
        top_n: Any = None,
        max_depth: Any = None,
        all_shortest: Any = None,
        max_members: Any = None,
    ) -> dict[str, Any]:
        """Run one graph analysis over an edge list.

        Args:
            mode (str): One of ``build`` / ``degree`` / ``bfs`` /
                ``path`` / ``components``.
            edges (list[dict]): The edge list — dicts with required
                non-empty string ``source`` / ``target`` and optional
                numeric ``weight`` (default 1, summed when duplicates
                merge) and boolean ``directed`` (overrides the global
                option for that edge). Between 1 and 10,000 edges.
            directed (bool): Global direction flag (default ``false``).
                When any edge resolves to directed the graph is treated
                as directed throughout.
            start (str): Required for ``bfs`` and ``path`` — the node to
                start from (must exist in the edge list).
            end (str): Required for ``path`` — the node to reach (must
                exist in the edge list).
            top_n (int): ``degree`` mode only — return only the first
                ``top_n`` degree entries (positive integer).
            max_depth (int): ``bfs`` mode only — stop expanding beyond
                this depth (non-negative integer; the start node is
                depth 0). ``None`` means unbounded.
            all_shortest (bool): ``path`` mode only — enumerate every
                shortest path (lexicographic order, capped at 10)
                instead of just the first one.
            max_members (int): ``components`` mode only — cap on the
                member list reported per component (positive integer,
                default 50; the full size is always reported).

        Returns:
            Dict[str, Any]: The analysis result for the requested mode.
                The ``path`` mode returns ``found: false`` when no path
                exists instead of raising.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens), including unknown ``start`` /
                ``end`` nodes.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        is_directed = self._validate_directed(directed)
        graph = self._build_graph(edges, is_directed)

        if mode == "build":
            return self._run_build(graph)
        if mode == "degree":
            return self._run_degree(graph, top_n)
        if mode == "bfs":
            return self._run_bfs(graph, start, max_depth)
        if mode == "path":
            return self._run_path(graph, start, end, all_shortest)
        return self._run_components(graph, max_members)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"graph_tool: {message}")

    @classmethod
    def _validate_directed(cls, directed: Any) -> bool:
        """Validate the global ``directed`` flag."""
        if directed is None:
            return False
        if isinstance(directed, bool):
            return directed
        cls._invalid(f"directed must be a boolean or None (got {directed!r})")

    @classmethod
    def _validate_node_id(cls, node: Any, label: str) -> str:
        """Validate a node identifier (edge endpoint or start/end)."""
        if node is None or isinstance(node, bool) or not isinstance(node, str):
            cls._invalid(f"{label} must be a non-empty string (got {node!r})")
        if not node:
            cls._invalid(f"{label} must be a non-empty string (got '')")
        return node

    @classmethod
    def _validate_count_option(
        cls, value: Any, name: str, minimum: int
    ) -> int:
        """Validate an integer counting option (top_n, max_members...)."""
        if value is None:
            cls._invalid(f"{name} is required and must be an integer")
        if isinstance(value, bool) or not isinstance(value, int):
            cls._invalid(f"{name} must be an integer (got {value!r})")
        if value < minimum:
            cls._invalid(f"{name} must be >= {minimum} (got {value})")
        return value

    @classmethod
    def _validate_optional_count(
        cls, value: Any, name: str, minimum: int
    ) -> Any:
        """Validate an optional integer option, letting ``None`` pass."""
        if value is None:
            return None
        return cls._validate_count_option(value, name, minimum)

    @classmethod
    def _validate_weight(cls, weight: Any, index: int) -> float:
        """Validate one edge weight (finite number, booleans rejected)."""
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            cls._invalid(
                f"edges[{index}]: weight must be a number "
                f"(got {weight!r})"
            )
        if not math.isfinite(weight):
            cls._invalid(
                f"edges[{index}]: weight must be a finite number "
                f"(got {weight!r})"
            )
        return weight

    # ------------------------------------------------------------------ #
    # Graph construction (shared by every mode)
    # ------------------------------------------------------------------ #

    def _build_graph(self, edges: Any, is_directed: bool) -> dict[str, Any]:
        """Validate the edge list and build the merged graph structure.

        Returns a dict with:

        * ``directed`` — whether any edge resolves to directed;
        * ``directed_weights`` / ``directed_counts`` — merged weights and
          occurrence counts keyed by the directed ``(source, target)``
          pair, for edges that resolve to directed;
        * ``undirected_weights`` / ``undirected_counts`` — merged weights
          and occurrence counts keyed by the sorted pair, for edges that
          resolve to undirected;
        * ``out`` / ``sym`` — the direction-respecting adjacency (a
          directed edge contributes one direction, an undirected edge
          both) and its symmetric closure, both
          ``{node: {neighbor: weight}}`` with sorted keys;
        * ``nodes`` — every node id, sorted.
        """
        if edges is None or isinstance(edges, (str, bytes)) or not isinstance(
            edges, (list, tuple)
        ):
            self._invalid(f"edges must be a list of edge dicts (got {edges!r})")
        if len(edges) < 1:
            self._invalid("edges must contain at least one edge (got 0)")
        if len(edges) > self.max_edges:
            self._invalid(
                f"edges exceed the {self.max_edges:,}-edge limit "
                f"(got {len(edges):,})"
            )

        # Directed and undirected edges are merged separately: a directed
        # ``a->b`` and an undirected ``{a, b}`` are distinct edge groups,
        # so they must never share a key (summing them would silently
        # drop one direction and clobber the other's weight).
        directed_weights: dict[tuple[str, str], Any] = {}
        directed_counts: dict[tuple[str, str], int] = {}
        undirected_weights: dict[tuple[str, str], Any] = {}
        undirected_counts: dict[tuple[str, str], int] = {}
        any_directed = False
        for index, edge in enumerate(edges):
            if edge is None or isinstance(edge, (str, bytes)) or not isinstance(
                edge, dict
            ):
                self._invalid(
                    f"edges[{index}] must be a dict with 'source' and "
                    f"'target' keys (got {edge!r})"
                )
            if "source" not in edge or "target" not in edge:
                self._invalid(
                    f"edges[{index}] must contain 'source' and 'target' "
                    f"keys (got keys {sorted(map(repr, edge.keys()))})"
                )
            source = self._validate_node_id(edge["source"], f"edges[{index}].source")
            target = self._validate_node_id(edge["target"], f"edges[{index}].target")
            weight = edge.get("weight", 1)
            self._validate_weight(weight, index)
            edge_directed = edge.get("directed")
            if edge_directed is not None and not isinstance(edge_directed, bool):
                self._invalid(
                    f"edges[{index}]: directed must be a boolean "
                    f"(got {edge_directed!r})"
                )
            # A per-edge ``directed`` flag overrides the global option.
            effective_directed = (
                bool(edge_directed) if edge_directed is not None else is_directed
            )
            any_directed = any_directed or effective_directed
            if effective_directed:
                key = (source, target)
                directed_weights[key] = directed_weights.get(key, 0) + weight
                directed_counts[key] = directed_counts.get(key, 0) + 1
            else:
                key = (source, target) if source <= target else (target, source)
                undirected_weights[key] = undirected_weights.get(key, 0) + weight
                undirected_counts[key] = undirected_counts.get(key, 0) + 1

        # ``out`` is the direction-respecting adjacency: a directed edge
        # contributes its single direction, an undirected edge contributes
        # both (so it stays traversable both ways even when the graph as a
        # whole is directed). ``sym`` is the symmetric closure used for
        # weak connectivity and undirected degrees.
        out: dict[str, dict[str, Any]] = {}
        sym: dict[str, dict[str, Any]] = {}
        for (source, target), weight in directed_weights.items():
            out.setdefault(source, {})[target] = (
                out.setdefault(source, {}).get(target, 0) + weight
            )
            sym.setdefault(source, {})[target] = (
                sym.setdefault(source, {}).get(target, 0) + weight
            )
            if source != target:
                sym.setdefault(target, {})[source] = (
                    sym.setdefault(target, {}).get(source, 0) + weight
                )
        for (source, target), weight in undirected_weights.items():
            out.setdefault(source, {})[target] = (
                out.setdefault(source, {}).get(target, 0) + weight
            )
            sym.setdefault(source, {})[target] = (
                sym.setdefault(source, {}).get(target, 0) + weight
            )
            if source != target:
                out.setdefault(target, {})[source] = (
                    out.setdefault(target, {}).get(source, 0) + weight
                )
                sym.setdefault(target, {})[source] = (
                    sym.setdefault(target, {}).get(source, 0) + weight
                )
        nodes = sorted(sym)
        return {
            "directed": any_directed,
            "directed_weights": directed_weights,
            "directed_counts": directed_counts,
            "undirected_weights": undirected_weights,
            "undirected_counts": undirected_counts,
            "out": {node: dict(sorted(out.get(node, {}).items())) for node in nodes},
            "sym": {node: dict(sorted(sym[node].items())) for node in nodes},
            "nodes": nodes,
        }

    # ------------------------------------------------------------------ #
    # build mode
    # ------------------------------------------------------------------ #

    def _run_build(self, graph: dict[str, Any]) -> dict[str, Any]:
        """Adjacency dict plus counts and isolated/self-loop/duplicate reports."""
        directed_weights = graph["directed_weights"]
        directed_counts = graph["directed_counts"]
        undirected_weights = graph["undirected_weights"]
        undirected_counts = graph["undirected_counts"]
        sym = graph["sym"]

        isolated = [
            node
            for node in graph["nodes"]
            if not any(neighbor != node for neighbor in sym[node])
        ]
        self_loops = sorted(
            {source for (source, target) in directed_weights if source == target}
            | {source for (source, target) in undirected_weights if source == target}
        )
        # One merged group per (pair, direction-kind); an undirected {a, b}
        # and a directed a->b are distinct edge groups. Deterministic order:
        # by (source, target), undirected group before the directed one.
        merged_groups: list[tuple[str, str, bool, int, Any]] = []
        for (source, target), count in undirected_counts.items():
            merged_groups.append(
                (source, target, False, count, undirected_weights[(source, target)])
            )
        for (source, target), count in directed_counts.items():
            merged_groups.append(
                (source, target, True, count, directed_weights[(source, target)])
            )
        merged_groups.sort(key=lambda group: (group[0], group[1], group[2]))
        duplicates = [
            {
                "source": source,
                "target": target,
                "count": count,
                "weight": weight,
            }
            for (source, target, is_directed, count, weight) in merged_groups
            if count > 1
        ]
        # Direction-respecting adjacency: out-edges per node (for an
        # undirected graph this is identical to the symmetric view; for a
        # directed graph it keeps each direction's own merged weight).
        adjacency = {
            node: dict(sorted(graph["out"].get(node, {}).items()))
            for node in graph["nodes"]
        }
        return {
            "mode": "build",
            "directed": graph["directed"],
            "adjacency": adjacency,
            "node_count": len(graph["nodes"]),
            "edge_count": len(merged_groups),
            "isolated_nodes": isolated,
            "self_loops": self_loops,
            "duplicate_edges": duplicates,
        }

    # ------------------------------------------------------------------ #
    # degree mode
    # ------------------------------------------------------------------ #

    def _run_degree(self, graph: dict[str, Any], top_n: Any) -> dict[str, Any]:
        """Per-node degrees sorted descending, with hub flagging."""
        clean_top_n = self._validate_optional_count(top_n, "top_n", 1)
        out = graph["out"]
        sym = graph["sym"]
        directed = graph["directed"]

        entries: list[dict[str, Any]] = []
        for node in graph["nodes"]:
            if directed:
                # A directed self-loop adds 1 in + 1 out (total 2).
                out_degree = len(out.get(node, {}))
                in_degree = sum(
                    1 for source in out if node in out[source]
                )
                entries.append(
                    {
                        "node": node,
                        "in_degree": in_degree,
                        "out_degree": out_degree,
                        "total_degree": in_degree + out_degree,
                    }
                )
            else:
                # An undirected self-loop adds 2 (one at each end).
                degree = sum(
                    2 if neighbor == node else 1 for neighbor in sym[node]
                )
                entries.append({"node": node, "degree": degree})

        degree_values = [
            entry.get("total_degree", entry.get("degree")) for entry in entries
        ]
        mean = statistics.mean(degree_values)
        stdev = statistics.pstdev(degree_values)
        threshold = mean + stdev
        for entry in entries:
            entry["is_hub"] = (
                entry.get("total_degree", entry.get("degree")) > threshold
            )
        entries.sort(
            key=lambda entry: (
                -entry.get("total_degree", entry.get("degree")),
                entry["node"],
            )
        )
        if clean_top_n is not None:
            entries = entries[:clean_top_n]
        return {
            "mode": "degree",
            "directed": directed,
            "node_count": len(graph["nodes"]),
            "mean_degree": mean,
            "stdev_degree": stdev,
            "hub_threshold": threshold,
            "degrees": entries,
        }

    # ------------------------------------------------------------------ #
    # bfs mode
    # ------------------------------------------------------------------ #

    def _validate_graph_node(self, graph: dict[str, Any], node: Any, label: str) -> str:
        """Validate that a start/end node exists in the graph."""
        clean_node = self._validate_node_id(node, label)
        if clean_node not in graph["sym"]:
            self._invalid(
                f"{label} node {clean_node!r} is not in the graph "
                f"({len(graph['nodes'])} available nodes)"
            )
        return clean_node

    def _run_bfs(self, graph: dict[str, Any], start: Any, max_depth: Any) -> dict[str, Any]:
        """Breadth-first traversal with per-node depths and visit order."""
        clean_start = self._validate_graph_node(graph, start, "start")
        clean_max_depth = self._validate_optional_count(max_depth, "max_depth", 0)
        adjacency = graph["out"] if graph["directed"] else graph["sym"]

        depths = {clean_start: 0}
        visit_order = [clean_start]
        queue: deque[str] = deque([clean_start])
        while queue:
            node = queue.popleft()
            if clean_max_depth is not None and depths[node] >= clean_max_depth:
                continue
            for neighbor in sorted(adjacency.get(node, {})):
                if neighbor not in depths:
                    depths[neighbor] = depths[node] + 1
                    visit_order.append(neighbor)
                    queue.append(neighbor)
        return {
            "mode": "bfs",
            "directed": graph["directed"],
            "start": clean_start,
            "max_depth": clean_max_depth,
            "reachable_count": len(depths),
            "depths": dict(sorted(depths.items())),
            "visit_order": visit_order,
        }

    # ------------------------------------------------------------------ #
    # path mode
    # ------------------------------------------------------------------ #

    def _bfs_distances(
        self, adjacency: dict[str, dict[str, Any]], start: str
    ) -> dict[str, int]:
        """Unweighted BFS distances from ``start`` over ``adjacency``."""
        distances = {start: 0}
        queue: deque[str] = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor in adjacency.get(node, {}):
                if neighbor not in distances:
                    distances[neighbor] = distances[node] + 1
                    queue.append(neighbor)
        return distances

    def _run_path(
        self,
        graph: dict[str, Any],
        start: Any,
        end: Any,
        all_shortest: Any,
    ) -> dict[str, Any]:
        """Unweighted shortest path (BFS); weights are ignored by design."""
        clean_start = self._validate_graph_node(graph, start, "start")
        clean_end = self._validate_graph_node(graph, end, "end")
        if all_shortest is None:
            clean_all_shortest = False
        elif isinstance(all_shortest, bool):
            clean_all_shortest = all_shortest
        else:
            self._invalid(
                f"all_shortest must be a boolean or None (got {all_shortest!r})"
            )

        adjacency = graph["out"] if graph["directed"] else graph["sym"]
        context: dict[str, Any] = {
            "mode": "path",
            "directed": graph["directed"],
            "start": clean_start,
            "end": clean_end,
        }
        distances = self._bfs_distances(adjacency, clean_start)
        if clean_end not in distances:
            return {
                **context,
                "found": False,
                "path": None,
                "length": None,
                "message": (
                    f"no path from {clean_start!r} to {clean_end!r}"
                ),
            }

        goal = distances[clean_end]
        context["found"] = True
        context["length"] = goal
        # The single-path variant and the all-shortest enumeration share
        # the same lexicographic DFS, so `path` always equals the first
        # entry of `all_shortest.paths`.
        paths: list[list[str]] = []
        truncated = self._enumerate_shortest_paths(
            adjacency,
            distances,
            clean_start,
            clean_end,
            goal,
            paths,
            stop_after=(
                1
                if not clean_all_shortest
                else self.max_all_shortest_paths + 1
            ),
        )
        if clean_all_shortest:
            context["all_shortest"] = {
                "paths": paths[: self.max_all_shortest_paths],
                # Exact unless truncated is true, in which case at least
                # `path_count` shortest paths exist.
                "path_count": len(paths),
                "truncated": truncated,
            }
        else:
            context["path"] = paths[0]
        return context

    def _enumerate_shortest_paths(
        self,
        adjacency: dict[str, dict[str, Any]],
        distances: dict[str, int],
        start: str,
        end: str,
        goal: int,
        paths: list[list[str]],
        stop_after: int = 10,
    ) -> bool:
        """Collect shortest paths in lexicographic order.

        Depth-first traversal over the distance-layered DAG, expanding
        neighbours in sorted order so paths are produced lexicographically.
        Stops once ``stop_after`` paths have been found; returns whether
        the enumeration was cut short (i.e. more paths exist).
        """
        stack: list[tuple[str, list[str]]] = [(start, [start])]
        while stack:
            node, path = stack.pop()
            if node == end:
                paths.append(path)
                if len(paths) >= stop_after:
                    return True
                continue
            depth = distances[node]
            if depth >= goal:
                continue
            for neighbor in sorted(adjacency.get(node, {}), reverse=True):
                if distances.get(neighbor) == depth + 1:
                    stack.append((neighbor, path + [neighbor]))
        return False

    # ------------------------------------------------------------------ #
    # components mode
    # ------------------------------------------------------------------ #

    def _run_components(
        self, graph: dict[str, Any], max_members: Any
    ) -> dict[str, Any]:
        """Connected components (weakly-connected when directed)."""
        default_members = 50
        if max_members is None:
            clean_max_members = default_members
        else:
            clean_max_members = self._validate_count_option(
                max_members, "max_members", 1
            )
        sym = graph["sym"]

        seen: set[str] = set()
        component_members: list[list[str]] = []
        for node in graph["nodes"]:
            if node in seen:
                continue
            members: list[str] = []
            queue: deque[str] = deque([node])
            seen.add(node)
            while queue:
                current = queue.popleft()
                members.append(current)
                for neighbor in sym[current]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        queue.append(neighbor)
            component_members.append(sorted(members))
        component_members.sort(key=lambda members: (-len(members), members[0]))

        components: list[dict[str, Any]] = [
            {
                "size": len(members),
                "members": members[:clean_max_members],
                "truncated": len(members) > clean_max_members,
            }
            for members in component_members
        ]
        return {
            "mode": "components",
            "directed": graph["directed"],
            "component_count": len(components),
            "largest_component_size": components[0]["size"],
            "max_members": clean_max_members,
            "components": components,
        }
