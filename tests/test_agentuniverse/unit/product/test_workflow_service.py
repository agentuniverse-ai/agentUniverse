import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch


if "ruamel.yaml" not in sys.modules:
    ruamel_module = types.ModuleType("ruamel")
    yaml_module = types.ModuleType("ruamel.yaml")
    yaml_module.YAML = MagicMock
    ruamel_module.yaml = yaml_module
    sys.modules["ruamel"] = ruamel_module
    sys.modules["ruamel.yaml"] = yaml_module

from agentuniverse_product.service.model.workflow_dto import WorkflowDTO
from agentuniverse_product.service.workflow_service import workflow_service


class WorkflowServiceTest(unittest.TestCase):
    def test_create_workflow_retries_when_generated_id_file_exists(self):
        with TemporaryDirectory() as directory:
            core_path = Path(directory)
            workflow_dir = core_path / "workflow"
            workflow_dir.mkdir()
            existing_path = workflow_dir / "workflow_123.yaml"
            existing_path.write_text("existing", encoding="utf-8")

            with patch.object(
                workflow_service, "get_core_path", return_value=core_path
            ), patch.object(
                workflow_service.random, "randint", side_effect=[123, 456]
            ), patch.object(workflow_service, "write_yaml_file") as write_yaml, patch.object(
                workflow_service, "register_workflow"
            ):
                workflow_id = workflow_service.WorkflowService.create_workflow(
                    WorkflowDTO(name="new workflow", graph={})
                )

        self.assertEqual(workflow_id, "workflow_456")
        self.assertEqual(Path(write_yaml.call_args.args[0]).name, "workflow_456.yaml")
        self.assertNotEqual(Path(write_yaml.call_args.args[0]), existing_path)


if __name__ == "__main__":
    unittest.main()
