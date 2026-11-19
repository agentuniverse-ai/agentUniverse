#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_graph_tool.py

"""Offline unit tests for GraphTool.

The tool is built purely on the standard library (collections,
statistics, math) and never touches the network, so this suite runs
fully offline. Every assertion is deterministic: adjacency, degree
arithmetic (including directed in/out splits), hub flagging, BFS depths
and visit order, shortest paths (including ties and the all-shortest
cap), and component layouts are all checked against hand-computed
ground truths on small fixed graphs.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import GraphTool
from agentuniverse.agent.action.tool.common_tool.graph_tool import (
    GraphTool as DirectGraphTool,
)

# --------------------------------------------------------------------- #
# Fixed graphs used across several modes
# --------------------------------------------------------------------- #
# Undirected star: hub-a, hub-b, hub-c, hub-d -> degrees [4, 1, 1, 1, 1].
STAR = [
    {"source": "hub", "target": "a"},
    {"source": "hub", "target": "b"},
    {"source": "hub", "target": "c"},
    {"source": "hub", "target": "d"},
]
# Diamond: a-b, a-c, b-d, c-d -> two shortest paths a..d of length 2.
DIAMOND = [
    {"source": "a", "target": "b"},
    {"source": "a", "target": "c"},
    {"source": "b", "target": "d"},
    {"source": "c", "target": "d"},
]
# Two disjoint pairs plus a self-loop-only node.
DISCONNECTED = [
    {"source": "a", "target": "b"},
    {"source": "c", "target": "d"},
    {"source": "e", "target": "e"},
]
# One undirected edge b-a plus one directed edge x->y: the graph as a
# whole is directed, but the undirected edge must contribute in BOTH
# directions (traversal, degrees, adjacency).
MIXED = [
    {"source": "b", "target": "a"},
    {"source": "x", "target": "y", "directed": True},
]


class GraphToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib GraphTool."""

    def setUp(self) -> None:
        self.tool = GraphTool()

    def assert_invalid(self, **kwargs) -> None:
        """Assert the call is rejected before any computation."""
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    # ------------------------------------------------------------------ #
    # build mode
    # ------------------------------------------------------------------ #

    def test_build_undirected_merges_reverse_edges(self) -> None:
        result = self.tool.execute(
            mode="build",
            edges=[
                {"source": "a", "target": "b", "weight": 2},
                {"source": "b", "target": "a", "weight": 3},
            ],
        )
        self.assertFalse(result["directed"])
        self.assertEqual(
            result["adjacency"], {"a": {"b": 5}, "b": {"a": 5}}
        )
        self.assertEqual(result["node_count"], 2)
        self.assertEqual(result["edge_count"], 1)
        self.assertEqual(
            result["duplicate_edges"],
            [{"source": "a", "target": "b", "count": 2, "weight": 5}],
        )

    def test_build_directed_keeps_direction_distinct(self) -> None:
        result = self.tool.execute(
            mode="build",
            directed=True,
            edges=[
                {"source": "a", "target": "b"},
                {"source": "b", "target": "a"},
            ],
        )
        self.assertTrue(result["directed"])
        self.assertEqual(result["edge_count"], 2)
        self.assertEqual(
            result["adjacency"], {"a": {"b": 1}, "b": {"a": 1}}
        )
        self.assertEqual(result["duplicate_edges"], [])

    def test_build_per_edge_directed_override(self) -> None:
        result = self.tool.execute(
            mode="build",
            edges=[
                {"source": "a", "target": "b"},
                {"source": "b", "target": "a", "directed": True},
            ],
        )
        # One directed edge anywhere makes the whole graph directed.
        self.assertTrue(result["directed"])
        self.assertEqual(result["edge_count"], 2)

    def test_build_self_loop_and_isolated_report(self) -> None:
        result = self.tool.execute(
            mode="build",
            edges=[
                {"source": "a", "target": "b"},
                {"source": "c", "target": "c"},
            ],
        )
        self.assertEqual(result["adjacency"]["c"], {"c": 1})
        self.assertEqual(result["self_loops"], ["c"])
        # A node whose only incident edges are self-loops is isolated.
        self.assertEqual(result["isolated_nodes"], ["c"])
        self.assertEqual(result["node_count"], 3)
        self.assertEqual(result["edge_count"], 2)

    def test_build_adjacency_keys_sorted(self) -> None:
        result = self.tool.execute(
            mode="build",
            edges=[{"source": "z", "target": "a"}, {"source": "z", "target": "m"}],
        )
        # Nodes a, m, z: outer keys sorted, inner neighbour keys sorted.
        self.assertEqual(list(result["adjacency"]), ["a", "m", "z"])
        self.assertEqual(list(result["adjacency"]["z"]), ["a", "m"])

    def test_build_is_deterministic(self) -> None:
        edges = [
            {"source": "b", "target": "a"},
            {"source": "c", "target": "b", "weight": 2.5},
            {"source": "a", "target": "c", "directed": False},
        ]
        first = self.tool.execute(mode="build", edges=edges)
        second = self.tool.execute(mode="build", edges=edges)
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # degree mode
    # ------------------------------------------------------------------ #

    def test_degree_undirected_star(self) -> None:
        result = self.tool.execute(mode="degree", edges=STAR)
        # Degrees [4, 1, 1, 1, 1]: mean 1.6, pstdev 1.2, threshold 2.8.
        self.assertEqual(result["mean_degree"], 1.6)
        self.assertEqual(result["stdev_degree"], 1.2)
        self.assertEqual(result["hub_threshold"], 2.8)
        self.assertEqual(
            result["degrees"],
            [
                {"node": "hub", "degree": 4, "is_hub": True},
                {"node": "a", "degree": 1, "is_hub": False},
                {"node": "b", "degree": 1, "is_hub": False},
                {"node": "c", "degree": 1, "is_hub": False},
                {"node": "d", "degree": 1, "is_hub": False},
            ],
        )

    def test_degree_hub_boundary_exactly_at_threshold(self) -> None:
        # K4 minus the c-d edge: degrees [3, 3, 2, 2] -> mean 2.5,
        # pstdev 0.5, threshold exactly 3.0. degree > threshold is
        # strict, so the two degree-3 nodes are NOT hubs.
        result = self.tool.execute(
            mode="degree",
            edges=[
                {"source": "a", "target": "b"},
                {"source": "a", "target": "c"},
                {"source": "a", "target": "d"},
                {"source": "b", "target": "c"},
                {"source": "b", "target": "d"},
            ],
        )
        self.assertEqual(result["hub_threshold"], 3.0)
        self.assertTrue(
            all(entry["is_hub"] is False for entry in result["degrees"])
        )

    def test_degree_ties_broken_by_node_name(self) -> None:
        result = self.tool.execute(
            mode="degree",
            edges=[{"source": "d", "target": "c"}, {"source": "b", "target": "a"}],
        )
        self.assertEqual(
            [entry["node"] for entry in result["degrees"]],
            ["a", "b", "c", "d"],
        )

    def test_degree_top_n(self) -> None:
        result = self.tool.execute(mode="degree", edges=STAR, top_n=2)
        self.assertEqual(
            [entry["node"] for entry in result["degrees"]], ["hub", "a"]
        )
        # The statistics still cover every node, not just the top_n.
        self.assertEqual(result["mean_degree"], 1.6)
        self.assertEqual(result["node_count"], 5)

    def test_degree_undirected_self_loop_counts_two(self) -> None:
        result = self.tool.execute(
            mode="degree",
            edges=[{"source": "a", "target": "a"}, {"source": "a", "target": "b"}],
        )
        self.assertEqual(result["degrees"][0], {"node": "a", "degree": 3, "is_hub": False})

    def test_degree_directed_in_out_split(self) -> None:
        # a->b, a->c, b->c, c->a:
        # in:  a=1, b=1, c=2 / out: a=2, b=1, c=1 / total: a=3, b=2, c=3.
        result = self.tool.execute(
            mode="degree",
            directed=True,
            edges=[
                {"source": "a", "target": "b"},
                {"source": "a", "target": "c"},
                {"source": "b", "target": "c"},
                {"source": "c", "target": "a"},
            ],
        )
        self.assertTrue(result["directed"])
        by_node = {entry["node"]: entry for entry in result["degrees"]}
        self.assertEqual(by_node["a"]["in_degree"], 1)
        self.assertEqual(by_node["a"]["out_degree"], 2)
        self.assertEqual(by_node["a"]["total_degree"], 3)
        self.assertEqual(by_node["b"]["in_degree"], 1)
        self.assertEqual(by_node["b"]["out_degree"], 1)
        self.assertEqual(by_node["c"]["in_degree"], 2)
        self.assertEqual(by_node["c"]["out_degree"], 1)
        self.assertEqual(by_node["c"]["total_degree"], 3)
        # Sorted by total degree desc: a and c (3) before b (2).
        self.assertEqual(
            [entry["node"] for entry in result["degrees"]], ["a", "c", "b"]
        )

    def test_degree_directed_self_loop_one_in_one_out(self) -> None:
        result = self.tool.execute(
            mode="degree",
            directed=True,
            edges=[{"source": "a", "target": "a"}, {"source": "a", "target": "b"}],
        )
        by_node = {entry["node"]: entry for entry in result["degrees"]}
        self.assertEqual(by_node["a"]["in_degree"], 1)
        self.assertEqual(by_node["a"]["out_degree"], 2)
        self.assertEqual(by_node["a"]["total_degree"], 3)
        self.assertEqual(by_node["b"]["out_degree"], 0)

    def test_degree_counts_merged_duplicates_once(self) -> None:
        result = self.tool.execute(
            mode="degree",
            edges=[
                {"source": "a", "target": "b"},
                {"source": "b", "target": "a"},
                {"source": "a", "target": "b"},
            ],
        )
        by_node = {entry["node"]: entry for entry in result["degrees"]}
        self.assertEqual(by_node["a"]["degree"], 1)

    # ------------------------------------------------------------------ #
    # bfs mode
    # ------------------------------------------------------------------ #

    def test_bfs_depths_and_visit_order(self) -> None:
        result = self.tool.execute(mode="bfs", edges=DIAMOND, start="a")
        self.assertEqual(result["depths"], {"a": 0, "b": 1, "c": 1, "d": 2})
        self.assertEqual(result["visit_order"], ["a", "b", "c", "d"])
        self.assertEqual(result["reachable_count"], 4)
        self.assertIsNone(result["max_depth"])

    def test_bfs_max_depth_zero_visits_only_start(self) -> None:
        result = self.tool.execute(mode="bfs", edges=DIAMOND, start="a", max_depth=0)
        self.assertEqual(result["depths"], {"a": 0})
        self.assertEqual(result["visit_order"], ["a"])

    def test_bfs_max_depth_cutoff(self) -> None:
        result = self.tool.execute(mode="bfs", edges=DIAMOND, start="a", max_depth=1)
        self.assertEqual(result["depths"], {"a": 0, "b": 1, "c": 1})
        self.assertEqual(result["visit_order"], ["a", "b", "c"])

    def test_bfs_directed_follows_out_edges_only(self) -> None:
        # a->b and c->a: from a the traversal cannot go back to c.
        result = self.tool.execute(
            mode="bfs",
            directed=True,
            edges=[{"source": "a", "target": "b"}, {"source": "c", "target": "a"}],
            start="a",
        )
        self.assertEqual(result["depths"], {"a": 0, "b": 1})
        self.assertEqual(result["visit_order"], ["a", "b"])

    def test_bfs_stops_at_component_border(self) -> None:
        result = self.tool.execute(mode="bfs", edges=DISCONNECTED, start="a")
        self.assertEqual(result["depths"], {"a": 0, "b": 1})
        self.assertEqual(result["reachable_count"], 2)

    def test_bfs_self_loop_is_harmless(self) -> None:
        result = self.tool.execute(mode="bfs", edges=DISCONNECTED, start="e")
        self.assertEqual(result["depths"], {"e": 0})
        self.assertEqual(result["visit_order"], ["e"])

    # ------------------------------------------------------------------ #
    # path mode
    # ------------------------------------------------------------------ #

    def test_path_shortest_over_longer_alternative(self) -> None:
        # a-b, b-c plus a three-hop detour: BFS must pick the 2-hop route.
        edges = DIAMOND + [
            {"source": "a", "target": "x"},
            {"source": "x", "target": "y"},
            {"source": "y", "target": "d"},
        ]
        result = self.tool.execute(mode="path", edges=edges, start="a", end="d")
        self.assertTrue(result["found"])
        self.assertEqual(result["length"], 2)
        self.assertEqual(result["path"], ["a", "b", "d"])

    def test_path_weights_are_ignored(self) -> None:
        # Direct edge weighs 100, the two-hop route weighs 2 in total —
        # the unweighted BFS still returns the single direct edge.
        edges = [
            {"source": "a", "target": "c", "weight": 100},
            {"source": "a", "target": "b", "weight": 1},
            {"source": "b", "target": "c", "weight": 1},
        ]
        result = self.tool.execute(mode="path", edges=edges, start="a", end="c")
        self.assertEqual(result["path"], ["a", "c"])
        self.assertEqual(result["length"], 1)

    def test_path_start_equals_end(self) -> None:
        result = self.tool.execute(mode="path", edges=DIAMOND, start="a", end="a")
        self.assertTrue(result["found"])
        self.assertEqual(result["path"], ["a"])
        self.assertEqual(result["length"], 0)

    def test_path_no_path_verdict(self) -> None:
        result = self.tool.execute(mode="path", edges=DISCONNECTED, start="a", end="d")
        self.assertFalse(result["found"])
        self.assertIsNone(result["path"])
        self.assertIsNone(result["length"])
        self.assertIn("no path", result["message"])

    def test_path_directed_asymmetry(self) -> None:
        # Only a->b exists, so b->a is unreachable.
        edges = [{"source": "a", "target": "b"}]
        result = self.tool.execute(
            mode="path", directed=True, edges=edges, start="b", end="a"
        )
        self.assertFalse(result["found"])
        forward = self.tool.execute(
            mode="path", directed=True, edges=edges, start="a", end="b"
        )
        self.assertEqual(forward["path"], ["a", "b"])

    def test_path_all_shortest_ties_lexicographic(self) -> None:
        result = self.tool.execute(
            mode="path", edges=DIAMOND, start="a", end="d", all_shortest=True
        )
        self.assertEqual(
            result["all_shortest"],
            {"paths": [["a", "b", "d"], ["a", "c", "d"]], "path_count": 2, "truncated": False},
        )

    def test_path_all_shortest_capped_at_ten(self) -> None:
        # Three layers a / m0-m3 / n0-n2 / z: 4*3 = 12 shortest paths.
        edges = [{"source": "a", "target": f"m{i}"} for i in range(4)]
        edges += [
            {"source": f"m{i}", "target": f"n{j}"}
            for i in range(4)
            for j in range(3)
        ]
        edges += [{"source": f"n{j}", "target": "z"} for j in range(3)]
        result = self.tool.execute(
            mode="path", edges=edges, start="a", end="z", all_shortest=True
        )
        all_shortest = result["all_shortest"]
        self.assertTrue(all_shortest["truncated"])
        self.assertEqual(len(all_shortest["paths"]), 10)
        self.assertEqual(all_shortest["path_count"], 11)
        self.assertEqual(all_shortest["paths"][0], ["a", "m0", "n0", "z"])
        self.assertEqual(all_shortest["paths"][-1], ["a", "m3", "n0", "z"])

    def test_path_single_path_is_first_of_all_shortest(self) -> None:
        single = self.tool.execute(mode="path", edges=DIAMOND, start="a", end="d")
        every = self.tool.execute(
            mode="path", edges=DIAMOND, start="a", end="d", all_shortest=True
        )
        self.assertEqual(single["path"], every["all_shortest"]["paths"][0])

    # ------------------------------------------------------------------ #
    # components mode
    # ------------------------------------------------------------------ #

    def test_components_disconnected_sizes_sorted_desc(self) -> None:
        edges = [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "c"},
            {"source": "d", "target": "e"},
            {"source": "f", "target": "g"},
        ]
        result = self.tool.execute(mode="components", edges=edges)
        self.assertEqual(result["component_count"], 3)
        self.assertEqual(result["largest_component_size"], 3)
        self.assertEqual(
            [component["size"] for component in result["components"]],
            [3, 2, 2],
        )
        self.assertEqual(result["components"][0]["members"], ["a", "b", "c"])

    def test_components_members_sorted_and_ties_by_first_member(self) -> None:
        result = self.tool.execute(mode="components", edges=DISCONNECTED)
        self.assertEqual(result["component_count"], 3)
        self.assertEqual(
            [component["members"] for component in result["components"]],
            [["a", "b"], ["c", "d"], ["e"]],
        )

    def test_components_max_members_cap(self) -> None:
        edges = [{"source": "n0", "target": f"n{i}"} for i in range(1, 6)]
        result = self.tool.execute(mode="components", edges=edges, max_members=3)
        component = result["components"][0]
        self.assertEqual(component["size"], 6)
        self.assertEqual(component["members"], ["n0", "n1", "n2"])
        self.assertTrue(component["truncated"])
        self.assertEqual(result["max_members"], 3)

    def test_components_default_member_cap_is_fifty(self) -> None:
        # n0 plus n1..n49: exactly 50 members, right at the default cap.
        edges = [{"source": "n0", "target": f"n{i}"} for i in range(1, 50)]
        result = self.tool.execute(mode="components", edges=edges)
        self.assertEqual(result["max_members"], 50)
        self.assertEqual(len(result["components"][0]["members"]), 50)
        self.assertFalse(result["components"][0]["truncated"])

    def test_components_directed_is_weakly_connected(self) -> None:
        # a->b->c is not strongly connected but forms one weak component.
        edges = [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "c"},
        ]
        result = self.tool.execute(mode="components", directed=True, edges=edges)
        self.assertEqual(result["component_count"], 1)
        self.assertEqual(result["components"][0]["members"], ["a", "b", "c"])
        self.assertTrue(result["directed"])

    def test_components_self_loop_only_node_is_own_component(self) -> None:
        result = self.tool.execute(
            mode="components", edges=[{"source": "solo", "target": "solo"}]
        )
        self.assertEqual(result["component_count"], 1)
        self.assertEqual(result["components"][0]["members"], ["solo"])

    # ------------------------------------------------------------------ #
    # Mixed directed/undirected graphs (per-edge direction handling)
    # ------------------------------------------------------------------ #

    def test_mixed_undirected_edge_traversable_both_directions(self) -> None:
        forward = self.tool.execute(mode="bfs", edges=MIXED, start="a")
        self.assertEqual(forward["depths"], {"a": 0, "b": 1})
        backward = self.tool.execute(mode="bfs", edges=MIXED, start="b")
        self.assertEqual(backward["depths"], {"a": 1, "b": 0})
        path = self.tool.execute(mode="path", edges=MIXED, start="b", end="a")
        self.assertEqual(path["path"], ["b", "a"])
        # The directed edge stays one-way: from y nothing is reachable.
        sink = self.tool.execute(mode="bfs", edges=MIXED, start="y")
        self.assertEqual(sink["depths"], {"y": 0})

    def test_mixed_degree_counts_undirected_edge_in_and_out(self) -> None:
        # totals: a=2, b=2, x=1, y=1 -> mean 1.5, pstdev 0.5, threshold 2.0;
        # degree > threshold is strict, so nobody is a hub.
        result = self.tool.execute(mode="degree", edges=MIXED)
        by_node = {entry["node"]: entry for entry in result["degrees"]}
        self.assertEqual(
            by_node["b"],
            {"node": "b", "in_degree": 1, "out_degree": 1, "total_degree": 2, "is_hub": False},
        )
        self.assertEqual(by_node["x"]["out_degree"], 1)
        self.assertEqual(by_node["x"]["in_degree"], 0)
        self.assertEqual(by_node["y"]["in_degree"], 1)
        self.assertEqual(by_node["y"]["out_degree"], 0)

    def test_per_edge_directed_false_overrides_global_directed(self) -> None:
        edges = [{"source": "a", "target": "b", "directed": False}]
        # The per-edge flag overrides the global option, so the edge is
        # undirected and traversable from b back to a.
        result = self.tool.execute(mode="bfs", edges=edges, directed=True, start="b")
        self.assertEqual(result["depths"], {"a": 1, "b": 0})
        build = self.tool.execute(mode="build", edges=edges, directed=True)
        self.assertFalse(build["directed"])  # no edge resolves to directed
        self.assertEqual(build["adjacency"], {"a": {"b": 1}, "b": {"a": 1}})

    def test_directed_adjacency_keeps_both_direction_weights(self) -> None:
        # a->b (weight 1) and b->a (weight 2) are distinct directed edges;
        # the adjacency must not clobber one direction's weight with the
        # other's.
        result = self.tool.execute(
            mode="build",
            directed=True,
            edges=[
                {"source": "a", "target": "b", "weight": 1},
                {"source": "b", "target": "a", "weight": 2},
            ],
        )
        self.assertEqual(result["adjacency"], {"a": {"b": 1}, "b": {"a": 2}})
        self.assertEqual(result["edge_count"], 2)

    def test_directed_and_undirected_edges_on_same_pair_are_distinct_groups(self) -> None:
        edges = [
            {"source": "a", "target": "b", "weight": 1},
            {"source": "a", "target": "b", "directed": True, "weight": 4},
        ]
        result = self.tool.execute(mode="build", edges=edges)
        self.assertTrue(result["directed"])
        self.assertEqual(result["edge_count"], 2)
        # The a->b adjacency cell aggregates both parallel edges; the
        # reverse cell only carries the undirected edge.
        self.assertEqual(result["adjacency"], {"a": {"b": 5}, "b": {"a": 1}})

    def test_directed_build_includes_sink_nodes_with_empty_adjacency(self) -> None:
        result = self.tool.execute(
            mode="build", directed=True, edges=[{"source": "a", "target": "b"}]
        )
        self.assertEqual(result["node_count"], 2)
        self.assertEqual(result["adjacency"], {"a": {"b": 1}, "b": {}})

    def test_mixed_graph_deterministic_across_runs(self) -> None:
        first = self.tool.execute(mode="build", edges=MIXED)
        second = self.tool.execute(mode="build", edges=MIXED)
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # Input validation (error matrix — all raise before computation)
    # ------------------------------------------------------------------ #

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="spanning_tree", edges=STAR)
        self.assert_invalid(mode=None, edges=STAR)
        self.assert_invalid(mode="BUILD", edges=STAR)

    def test_invalid_edges_container(self) -> None:
        self.assert_invalid(mode="build")
        self.assert_invalid(mode="build", edges="a-b")
        self.assert_invalid(mode="build", edges={})
        self.assert_invalid(mode="build", edges=[])

    def test_invalid_edge_shapes(self) -> None:
        self.assert_invalid(mode="build", edges=["a-b"])
        self.assert_invalid(mode="build", edges=[{"source": "a"}])
        self.assert_invalid(mode="build", edges=[{"target": "b"}])
        self.assert_invalid(mode="build", edges=[{"source": "a", "target": ""}])
        self.assert_invalid(mode="build", edges=[{"source": 1, "target": "b"}])
        self.assert_invalid(mode="build", edges=[{"source": True, "target": "b"}])

    def test_invalid_weights(self) -> None:
        self.assert_invalid(
            mode="build", edges=[{"source": "a", "target": "b", "weight": True}]
        )
        self.assert_invalid(
            mode="build", edges=[{"source": "a", "target": "b", "weight": "2"}]
        )
        self.assert_invalid(
            mode="build", edges=[{"source": "a", "target": "b", "weight": float("inf")}]
        )
        self.assert_invalid(
            mode="build", edges=[{"source": "a", "target": "b", "weight": float("nan")}]
        )

    def test_invalid_directed_flags(self) -> None:
        self.assert_invalid(mode="build", edges=STAR, directed="yes")
        self.assert_invalid(mode="build", edges=STAR, directed=1)
        self.assert_invalid(
            mode="build",
            edges=[{"source": "a", "target": "b", "directed": "true"}],
        )

    def test_edge_count_limit(self) -> None:
        edges = [{"source": "a", "target": "b"}] * 10_001
        self.assert_invalid(mode="build", edges=edges)
        ok = self.tool.execute(
            mode="build", edges=[{"source": "a", "target": "b"}] * 10_000
        )
        # 10,000 duplicates merge into a single edge with count 10,000.
        self.assertEqual(ok["edge_count"], 1)
        self.assertEqual(ok["duplicate_edges"][0]["count"], 10_000)

    def test_invalid_top_n(self) -> None:
        self.assert_invalid(mode="degree", edges=STAR, top_n=0)
        self.assert_invalid(mode="degree", edges=STAR, top_n=-1)
        self.assert_invalid(mode="degree", edges=STAR, top_n=True)
        self.assert_invalid(mode="degree", edges=STAR, top_n="3")

    def test_invalid_max_depth(self) -> None:
        self.assert_invalid(mode="bfs", edges=STAR, start="hub", max_depth=-1)
        self.assert_invalid(mode="bfs", edges=STAR, start="hub", max_depth=True)
        self.assert_invalid(mode="bfs", edges=STAR, start="hub", max_depth="1")

    def test_invalid_max_members_and_all_shortest(self) -> None:
        self.assert_invalid(mode="components", edges=STAR, max_members=0)
        self.assert_invalid(mode="components", edges=STAR, max_members="5")
        self.assert_invalid(
            mode="path", edges=STAR, start="hub", end="a", all_shortest="yes"
        )

    def test_unknown_start_and_end_nodes(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="bfs", edges=STAR, start="zzz")
        self.assertIn("not in the graph", str(ctx.exception))
        self.assertIn("5 available nodes", str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="path", edges=STAR, start="hub", end="zzz")
        self.assertIn("not in the graph", str(ctx.exception))
        # A missing start/end is also rejected (None is not a node id).
        self.assert_invalid(mode="bfs", edges=STAR)
        self.assert_invalid(mode="path", edges=STAR, start="hub")

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectGraphTool, GraphTool)
        self.assertEqual(self.tool.name, "graph_tool")
        self.assertIn("edge lists", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("GraphTool", __all__)


if __name__ == "__main__":
    unittest.main()
