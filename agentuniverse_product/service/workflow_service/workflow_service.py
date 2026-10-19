# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/21 20:52
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow_service.py
import os
import random

from agentuniverse.workflow.workflow import Workflow
from agentuniverse.workflow.workflow_manager import WorkflowManager
from agentuniverse_product.base.util.yaml_util import write_yaml_file, update_nested_yaml_value
from agentuniverse_product.service.model.workflow_dto import WorkflowDTO
from agentuniverse_product.service.util.common_util import get_core_path
from agentuniverse_product.service.util.workflow_util import register_workflow


class WorkflowService:
    """Workflow Service for aU-product."""

    @staticmethod
    def create_workflow(workflow_dto: WorkflowDTO) -> str:
        """Creates a workflow and returns its ID.

        Args:
            workflow_dto (WorkflowDTO): The workflow DTO containing the workflow attributes.

        Returns:
            str: The ID of the created workflow.
        """
        workflow_id = f"workflow_{random.randint(100, 999)}"
        workflow_config = {
            'id': workflow_id,
            'name': workflow_dto.name,
            'description': workflow_dto.description,
            'graph': workflow_dto.graph,
            'metadata': {
                'class': 'Workflow',
                'module': 'agentuniverse.workflow.workflow',
                'type': 'WORKFLOW'
            }
        }
        # write workflow YAML file
        path = get_core_path()
        workflow_file_path = path / 'workflow' / f"{workflow_id}.yaml" if path \
            else os.path.join('..', '..', 'platform', 'difizen', 'workflow', f"{workflow_id}.yaml")
        write_yaml_file(str(workflow_file_path), workflow_config)
        # register workflow instance
        register_workflow(str(workflow_file_path))
        return workflow_id

    @staticmethod
    def update_workflow(workflow_dto: WorkflowDTO) -> str:
        """Update workflow attributes.

        Args:
            workflow_dto (WorkflowDTO): The workflow DTO containing the workflow attributes.

        Returns:
            str: The ID of the updated workflow.
        """
        if workflow_dto.id is None:
            raise ValueError("workflow_id is None.")
        workflow: Workflow = WorkflowManager().get_instance_obj(component_instance_name=workflow_dto.id, new_instance=False)
        if workflow is None:
            raise ValueError("The workflow instance corresponding to the workflow_id cannot be found.")
        workflow_update_config = {
            'name': workflow_dto.name,
            'description': workflow_dto.description,
            'graph_config': workflow_dto.graph
        }
        # Update the workflow attributes if they are provided
        updated_fields = {key: value for key, value in workflow_update_config.items() if value is not None}

        # set workflow attributes
        for key, value in updated_fields.items():
            setattr(workflow, key, value)

        if updated_fields:
            # only persist the graph when the update actually carries one,
            # otherwise the None default would wipe the stored graph
            if 'graph_config' in updated_fields:
                updated_fields['graph'] = updated_fields.pop('graph_config')
            update_nested_yaml_value(workflow.component_config_path, updated_fields)
        return workflow_dto.id

    @staticmethod
    def get_workflow_detail(id: str) -> WorkflowDTO | None:
        """Get workflow detail by workflow id.

        Args:
            id (str): The ID of the workflow.

        Returns:
            WorkflowDTO | None: WorkflowDTO or None.
        """
        workflow: Workflow = WorkflowManager().get_instance_obj(component_instance_name=id, new_instance=False)
        if workflow is None:
            raise ValueError("The workflow instance corresponding to the workflow_id cannot be found.")
        return WorkflowDTO(id=workflow.id, name=workflow.name, description=workflow.description,
                           graph=workflow.graph_config)
