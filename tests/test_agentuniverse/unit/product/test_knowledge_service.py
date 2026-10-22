import io
import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


if "ruamel.yaml" not in sys.modules:
    ruamel_module = types.ModuleType("ruamel")
    yaml_module = types.ModuleType("ruamel.yaml")
    yaml_module.YAML = MagicMock
    ruamel_module.yaml = yaml_module
    sys.modules["ruamel"] = ruamel_module
    sys.modules["ruamel.yaml"] = yaml_module

from agentuniverse_product.service.knowledge_service import knowledge_service


class KnowledgeServiceUploadTest(unittest.TestCase):
    def test_repeated_upload_does_not_duplicate_store(self):
        knowledge_id = "test-knowledge"
        store_name = f"{knowledge_id}_chroma_store"
        knowledge = SimpleNamespace(
            stores=[store_name],
            insert_knowledge=MagicMock(),
        )
        manager = MagicMock()
        manager.get_instance_obj.return_value = knowledge
        upload = SimpleNamespace(filename="notes.txt", file=io.BytesIO(b"notes"))

        with patch.object(knowledge_service, "get_core_path", return_value=Path("/core")), patch.object(
            knowledge_service, "get_resources_path", return_value="/uploads"
        ), patch.object(knowledge_service.os.path, "exists", return_value=True), patch.object(
            knowledge_service.os.path, "isfile", return_value=True
        ), patch.object(knowledge_service, "open", MagicMock()), patch.object(
            knowledge_service.shutil, "copyfileobj"
        ), patch.object(knowledge_service, "KnowledgeManager", return_value=manager):
            result = knowledge_service.KnowledgeService.upload_knowledge_file(
                knowledge_id, upload
            )

        self.assertTrue(result)
        self.assertEqual(knowledge.stores, [store_name])
        knowledge.insert_knowledge.assert_called_once_with(
            source_path="/uploads/notes.txt", stores=[store_name]
        )


if __name__ == "__main__":
    unittest.main()
