# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/21 18:46
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: end_node.py
import re
from typing import List, Optional

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node, NodeData
from agentuniverse.workflow.node.node_config import EndNodeInputParams, NodeOutputParams, NodeInfoParams
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class EndNodeData(NodeData):
    """NodeData subclass holding the end node input configuration.
    """
    inputs: Optional[EndNodeInputParams] = None


class EndNode(Node):
    """The basic class of the end node."""
    _data_cls = EndNodeData

    def __init__(self, **kwargs):
        """Initialize the end node and set its type to the end node enum.

        Args:
            **kwargs: Field values for the node.
        """
        super().__init__(**kwargs)
        self.type = NodeEnum.END

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        """Resolve the template variables of the end prompt with the resolved input parameters and store the final output.

        Args:
            workflow_output(WorkflowOutput): The workflow execution output.

        Returns:
            NodeOutput: The node output holding the final prompt value.

        Raises:
            ValueError: If a template variable can not be resolved.
        """
        inputs: EndNodeInputParams = self._data.inputs
        prompt: NodeInfoParams = inputs.prompt
        if isinstance(prompt.value, dict):
            prompt_val = prompt.value.get('content', '')
        else:
            prompt_val = prompt.value

        # Extract variables from the prompt template
        template_variables = re.findall(r'\{\{(.*?)\}\}', prompt_val)
        # Resolve the input parameters
        end_node_input_params = self._resolve_input_params(inputs.input_param, workflow_output)

        # Replace variables in the prompt
        try:
            for var in template_variables:
                if var not in end_node_input_params:
                    raise KeyError(f"The variable '{var}' is not found in the input params.")
                prompt_val = prompt_val.replace(f'{{{{{var}}}}}',
                                                str(end_node_input_params[var]) if end_node_input_params[var] else '')
        except KeyError as e:
            raise ValueError(f"Error processing template variables: {e}")

        output_params: List[NodeOutputParams] = self._data.outputs
        output_param: NodeOutputParams = output_params[0]
        output_param.value = prompt_val

        workflow_output.workflow_parameters[self.id] = output_params
        workflow_output.workflow_end_params = {output_param.name: output_param.value}
        return NodeOutput(node_id=self.id, status=NodeStatusEnum.SUCCEEDED, result=output_params)
