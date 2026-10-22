# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 19:18
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow.py
from collections.abc import Mapping
from typing import Any, Callable, Optional

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.workflow_configer import WorkflowConfiger
from agentuniverse.workflow.graph.graph import Graph
from agentuniverse.workflow.workflow_output import WorkflowOutput


class Workflow(ComponentBase):
    """The basic class of the workflow."""

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

    def _identity(self) -> str:
        """Return the workflow identifier used in error messages."""
        return self.id or self.name or "<unnamed>"

    def build(self) -> 'Workflow':
        if self.graph_config is None:
            message = (
                f"Workflow '{self._identity()}' cannot be built because "
                "its graph configuration is missing. "
                "Please check the 'graph' field in the workflow configuration."
            )
            raise ValueError(message)
        self.graph = Graph().build(self.id, self.graph_config)
        return self

    def run(self, input_params: Optional[dict] = None, *,
            resume_from: Optional[WorkflowOutput | str | bytes | Mapping[str, Any]] = None,
            checkpoint_callback: Optional[Callable[[WorkflowOutput], None]] = None) -> WorkflowOutput:
        """Run a new workflow or resume one from a durable checkpoint.

        ``checkpoint_callback`` receives a deep-copied snapshot after every
        successful node. The snapshot can be serialized with
        :meth:`WorkflowOutput.to_checkpoint_json` and passed back through
        ``resume_from`` without re-running completed nodes.
        """
        if self.graph is None:
            message = (
                f"Workflow '{self._identity()}' has not been built. "
                "Call build() successfully before run()."
            )
            raise ValueError(message)
        if resume_from is None:
            workflow_output = WorkflowOutput(
                workflow_id=self.id,
                workflow_start_params=input_params or {},
            )
        else:
            workflow_output = self._restore_checkpoint(resume_from)
            if workflow_output.workflow_id != self.id:
                raise ValueError(
                    f'Checkpoint workflow id {workflow_output.workflow_id!r} '
                    f'does not match workflow id {self.id!r}.'
                )
            if input_params is not None and input_params != workflow_output.workflow_start_params:
                raise ValueError('Input parameters do not match the workflow checkpoint.')

        self.graph.run(workflow_output, checkpoint_callback=checkpoint_callback)
        return workflow_output

    def resume(self, checkpoint: WorkflowOutput | str | bytes | Mapping[str, Any], *,
               checkpoint_callback: Optional[Callable[[WorkflowOutput], None]] = None) -> WorkflowOutput:
        """Resume this workflow from an object, mapping, or JSON checkpoint."""
        return self.run(
            resume_from=checkpoint,
            checkpoint_callback=checkpoint_callback,
        )

    @staticmethod
    def _restore_checkpoint(
            checkpoint: WorkflowOutput | str | bytes | Mapping[str, Any]) -> WorkflowOutput:
        if isinstance(checkpoint, WorkflowOutput):
            return checkpoint.model_copy(deep=True)
        if isinstance(checkpoint, (str, bytes)):
            return WorkflowOutput.from_checkpoint_json(checkpoint)
        if isinstance(checkpoint, Mapping):
            return WorkflowOutput.model_validate(dict(checkpoint))
        raise TypeError('checkpoint must be a WorkflowOutput, mapping, JSON string, or bytes.')

    def initialize_by_component_configer(self, component_configer: WorkflowConfiger) -> 'Workflow':
        """Initialize the Workflow by the ComponentConfiger object.

        Args:
            component_configer(WorkflowConfiger): the ComponentConfiger object
        Returns:
            Workflow: the Workflow object
        """
        super().initialize_by_component_configer(component_configer)
        if component_configer.id:
            self.id = component_configer.id
        if component_configer.name:
            self.name = component_configer.name
        if component_configer.description:
            self.description = component_configer.description
        if component_configer.graph:
            self.graph_config = component_configer.graph
        return self
