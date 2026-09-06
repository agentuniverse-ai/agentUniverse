import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from ruamel.yaml import YAML

from agentuniverse_product.service.model.workflow_dto import WorkflowDTO
from agentuniverse_product.service.workflow_service.workflow_service import WorkflowService

WORKFLOW_CONFIG = {
    'id': 'workflow_123',
    'name': 'old name',
    'description': 'old description',
    'graph': {
        'nodes': [{'id': 'start', 'type': 'START'}],
        'edges': [{'source': 'start', 'target': 'end'}],
    },
    'metadata': {
        'class': 'Workflow',
        'module': 'agentuniverse.workflow.workflow',
        'type': 'WORKFLOW'
    },
}


class WorkflowServiceUpdateWorkflowTest(unittest.TestCase):
    """Regression tests for the YAML written by WorkflowService.update_workflow."""

    def setUp(self):
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self._tmp_dir.name, 'workflow_123.yaml')
        yaml = YAML()
        with open(self.config_path, 'w', encoding='utf-8') as file:
            yaml.dump(WORKFLOW_CONFIG, file)
        self.workflow = SimpleNamespace(
            id='workflow_123',
            name='old name',
            description='old description',
            graph_config=WORKFLOW_CONFIG['graph'],
            component_config_path=self.config_path,
        )

    def tearDown(self):
        self._tmp_dir.cleanup()

    def _update_workflow(self, workflow_dto: WorkflowDTO) -> str:
        with patch('agentuniverse_product.service.workflow_service.workflow_service.WorkflowManager') as manager_cls:
            manager_cls.return_value.get_instance_obj.return_value = self.workflow
            return WorkflowService.update_workflow(workflow_dto)

    def _read_config(self) -> dict:
        yaml = YAML()
        with open(self.config_path, 'r', encoding='utf-8') as file:
            return yaml.load(file)

    def test_update_without_graph_preserves_graph_in_yaml(self):
        # A metadata-only edit (the DTO leaves graph at its None default) must
        # not overwrite the persisted graph in the workflow YAML file.
        self._update_workflow(WorkflowDTO(id='workflow_123', name='new name'))
        config = self._read_config()
        self.assertEqual('new name', config.get('name'))
        self.assertEqual(WORKFLOW_CONFIG['graph'], config.get('graph'))

    def test_update_with_graph_writes_graph_to_yaml(self):
        new_graph = {'nodes': [{'id': 'llm', 'type': 'LLM'}], 'edges': []}
        self._update_workflow(
            WorkflowDTO(id='workflow_123', name='new name', graph=new_graph))
        config = self._read_config()
        self.assertEqual('new name', config.get('name'))
        self.assertEqual(new_graph, config.get('graph'))


if __name__ == '__main__':
    unittest.main()
