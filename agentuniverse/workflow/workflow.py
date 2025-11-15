# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 19:18
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow.py
from typing import Optional

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.workflow_configer import WorkflowConfiger
from agentuniverse.workflow.graph.graph import Graph
from agentuniverse.workflow.workflow_output import WorkflowOutput


class Workflow(ComponentBase):
    """Workflow abstraction that encapsulates graph construction and execution.

    - `build()`: Construct a `Graph` instance from `graph_config`.
    - `run()`: Execute the graph and accumulate results into `WorkflowOutput`.
    """

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    graph: Optional[Graph] = None
    graph_config: Optional[dict] = None

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.WORKFLOW, **kwargs)

    def get_instance_code(self) -> str:
        """Return the full instance code of the workflow."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.id}'

    def build(self) -> 'Workflow':
        """Build the graph instance from `graph_config`."""
        if self.graph_config is None:
            raise ValueError('The graph config is None.')
        self.graph = Graph().build(self.id, self.graph_config)
        return self

    def run(self, input_params: dict) -> WorkflowOutput:
        """Run the workflow.

        Args:
            input_params (dict): Start parameters recorded into `WorkflowOutput`.
        """
        if self.graph is None:
            raise ValueError('The graph of the workflow is None.')
        workflow_output = WorkflowOutput(workflow_id=self.id, workflow_start_params=input_params)
        self.graph.run(workflow_output)
        return workflow_output

    def initialize_by_component_configer(self, component_configer: WorkflowConfiger) -> 'Workflow':
        """Initialize the Workflow by the ComponentConfiger object.

        Args:
            component_configer(WorkflowConfiger): the ComponentConfiger object
        Returns:
            Workflow: the Workflow object
        """
        if component_configer.id:
            self.id = component_configer.id
        if component_configer.name:
            self.name = component_configer.name
        if component_configer.description:
            self.description = component_configer.description
        if component_configer.graph:
            self.graph_config = component_configer.graph
        return self
