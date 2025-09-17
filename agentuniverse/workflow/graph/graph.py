# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 19:39
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: graph.py
from typing import Optional, Any

import networkx as nx

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node
from agentuniverse.workflow.node.node_constant import NODE_CLS_MAPPING
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class Graph(nx.DiGraph):
    """The basic class of the graph."""

    def build(self, workflow_id: str, config: dict) -> "Graph":
        """Build the graph."""
        nodes_config = config.get("nodes")
        if not nodes_config:
            raise ValueError("The nodes configuration is empty")
        for node_config in nodes_config:
            self._add_graph_node(workflow_id, node_config)
        edges_config = config.get("edges")
        if not edges_config:
            raise ValueError("The edges configuration is empty")
        for edge_config in edges_config:
            self._add_graph_edge(edge_config)
        if not nx.is_directed_acyclic_graph(self):
            raise ValueError("The provided configuration does not form a DAG.")
        return self

    def _add_graph_node(self, workflow_id: str, node_config: dict) -> None:
        """Add a node to the graph.

        Args:
            workflow_id: The workflow id.
            node_config: The node configuration.
        """
        if node_config.get("type") not in NodeEnum.to_value_list():
            raise ValueError("The node type is not supported")
        node_id = node_config.get("id")
        if self.has_node(node_id):
            return
        node_cls = NODE_CLS_MAPPING[node_config.get("type")]
        node_type = node_config.pop("type")
        node_instance = node_cls(type=NodeEnum.from_value(node_type), workflow_id=workflow_id, **node_config)
        node_config["type"] = node_type
        self.add_node(node_id, instance=node_instance, type=node_type)

    def _add_graph_edge(self, edge_config: dict) -> None:
        """Add a edge to the graph.

        Args:
            edge_config: The edge configuration.
        """
        self.add_edge(
            edge_config.get("source_node_id"),
            edge_config.get("target_node_id"),
            source_handler=edge_config.get("source_handler"),
        )

    def run(self, workflow_output: WorkflowOutput) -> None:
        """Run the graph.

        Args:
            workflow_output: The workflow output.
        """
        sorted_nodes = list(nx.topological_sort(self))
        predecessor_node: Node | None = None
        while True:
            next_node = self._get_next_node(workflow_output, sorted_nodes, predecessor_node)
            if not next_node:
                break
            if self._has_node_been_executed(workflow_output, next_node.id):
                predecessor_node = next_node
                continue
            self._run_node(cur_node=next_node, workflow_output=workflow_output)
            if next_node.type == NodeEnum.END:
                break
            predecessor_node = next_node

    def _get_next_node(
        self, workflow_output: WorkflowOutput, nodes: Any, predecessor_node: Optional[Node] = None
    ) -> Optional[Node]:
        """Get the next node in the graph.

        Args:
            workflow_output: The workflow output.
            nodes: The nodes in the graph.
            predecessor_node: The predecessor node.
        Returns:
            The next node in the graph.
        """
        if not predecessor_node:
            for node_id in nodes:
                if self.nodes[node_id]["type"] == NodeEnum.START.value:
                    return self.nodes[node_id]["instance"]
        else:
            predecessor_node_output: NodeOutput = workflow_output.workflow_node_results.get(predecessor_node.id, None)
            source_handler = predecessor_node_output.edge_source_handler if predecessor_node_output else None
            successors = self.successors(predecessor_node.id)
            if not successors:
                return None
            successors = list(successors)
            if source_handler:
                for s in successors:
                    if self.get_edge_data(predecessor_node.id, s).get("source_handler") == source_handler:
                        return self.nodes[s]["instance"]
            else:
                return self.nodes[successors[0]]["instance"]

    @staticmethod
    def _has_node_been_executed(workflow_output: WorkflowOutput, node_id: str) -> bool:
        """Check if the node has been executed.

        Args:
            workflow_output: The workflow output.
            node_id: The node id.
        Returns:
            True if the node has been executed, False otherwise.
        """
        return node_id in workflow_output.workflow_node_results

    @staticmethod
    def _run_node(cur_node: Node = None, workflow_output: WorkflowOutput = None) -> None:
        """Run the node in the graph.

        Args:
            cur_node: The current node in the graph.
            workflow_output: The workflow output.
        """
        node_output = cur_node.run(workflow_output)
        workflow_output.workflow_node_results[cur_node.id] = node_output
