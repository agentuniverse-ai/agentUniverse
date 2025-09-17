# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 20:02
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge_node.py
from typing import List, Optional

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node, NodeData
from agentuniverse.workflow.node.node_config import KnowledgeNodeInputParams, NodeInfoParams, NodeOutputParams
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class KnowledgeNodeData(NodeData):
    inputs: Optional[KnowledgeNodeInputParams] = None


class KnowledgeNode(Node):
    """The basic class of the knowledge node."""

    _data_cls = KnowledgeNodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.KNOWLEDGE

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        inputs: KnowledgeNodeInputParams = self._data.inputs

        param_map = {"top_k": None, "id": None}

        for knowledge_param in inputs.knowledge_param:
            if knowledge_param.name in param_map:
                if isinstance(knowledge_param.value, str):
                    param_map[knowledge_param.name] = knowledge_param.value
                else:
                    param_map[knowledge_param.name] = knowledge_param.value.get("content", None)

        knowledge_id_list = param_map.get("id")
        query_top_k = param_map.get("top_k")

        knowledge_list = []
        for knowledge_id in knowledge_id_list:
            knowledge: Knowledge = KnowledgeManager().get_instance_obj(knowledge_id)
            if knowledge is None:
                raise ValueError("No knowledge with id {} was found.".format(knowledge_id))
            knowledge_list.append(knowledge)

        knowledge_input_params = self._resolve_input_params(inputs.input_param, workflow_output)
        if query_top_k:
            knowledge_input_params["similarity_top_k"] = query_top_k
        if "query" in knowledge_input_params:
            knowledge_input_params["query_str"] = knowledge_input_params.pop("query")

        knowledge_res = ""
        for knowledge in knowledge_list:
            document_texts = [document.text for document in knowledge.query_knowledge(**knowledge_input_params)]
            knowledge_res += "\n".join(document_texts)
        output_params: List[NodeOutputParams] = self._data.outputs
        output_params[0].value = knowledge_res

        workflow_output.workflow_parameters[self.id] = output_params
        return NodeOutput(node_id=self.id, status=NodeStatusEnum.SUCCEEDED, result=output_params)
