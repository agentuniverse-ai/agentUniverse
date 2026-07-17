import os
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool import word_document_tool as word_module
from agentuniverse.agent.action.tool.common_tool.word_document_tool import WordDocumentTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(word_module.__file__), "word_document_tool.yaml")


class WordDocumentToolTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.tool = WordDocumentTool(base_dir=self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def blocks(self):
        return [
            {"type": "heading", "text": "Report", "level": 1},
            {"type": "paragraph", "text": "Quarterly results"},
            {"type": "bullet", "text": "Revenue grew", "level": 0},
            {"type": "table", "rows": [["Metric", "Value"], ["Revenue", 123]], "style": "Table Grid"},
            {"type": "page_break"},
        ]

    def test_round_trip(self):
        created = self.tool.execute(
            mode="create", file_path="report.docx", blocks=self.blocks(), metadata={"title": "Q2", "author": "aU"}
        )
        self.assertEqual(created["status"], "success")
        read = self.tool.execute(mode="read", file_path="report.docx")
        self.assertIn("Report", [item["text"] for item in read["paragraphs"]])
        self.assertEqual(read["tables"][0][1], ["Revenue", "123"])
        info = self.tool.execute(mode="info", file_path="report.docx")
        self.assertEqual(info["metadata"]["title"], "Q2")
        self.assertEqual(info["table_count"], 1)

    def test_append(self):
        self.tool.execute(mode="create", file_path="report.docx", blocks=[{"type": "paragraph", "text": "first"}])
        result = self.tool.execute(
            mode="append", file_path="report.docx", blocks=[{"type": "paragraph", "text": "second"}]
        )
        self.assertEqual(result["status"], "success")
        read = self.tool.execute(mode="read", file_path="report.docx")
        self.assertEqual([p["text"] for p in read["paragraphs"]], ["first", "second"])

    def test_template(self):
        self.tool.execute(mode="create", file_path="template.docx", blocks=[{"type": "heading", "text": "Template"}])
        result = self.tool.execute(
            mode="create",
            file_path="output.docx",
            template_path="template.docx",
            blocks=[{"type": "paragraph", "text": "Generated"}],
        )
        self.assertEqual(result["status"], "success")
        read = self.tool.execute(mode="read", file_path="output.docx")
        self.assertEqual([p["text"] for p in read["paragraphs"]], ["Template", "Generated"])

    def test_refuses_overwrite(self):
        self.tool.execute(mode="create", file_path="report.docx", blocks=[{"type": "paragraph", "text": "first"}])
        result = self.tool.execute(
            mode="create", file_path="report.docx", blocks=[{"type": "paragraph", "text": "second"}]
        )
        self.assertIn("overwrite=true", result["error"])

    def test_explicit_overwrite(self):
        self.tool.execute(mode="create", file_path="report.docx", blocks=[{"type": "paragraph", "text": "first"}])
        result = self.tool.execute(
            mode="create", file_path="report.docx", blocks=[{"type": "paragraph", "text": "second"}], overwrite=True
        )
        self.assertEqual(result["status"], "success")

    def test_path_escape(self):
        result = self.tool.execute(mode="info", file_path="../report.docx")
        self.assertIn("escapes the allowed directory", result["error"])

    def test_extension(self):
        result = self.tool.execute(mode="info", file_path="report.txt")
        self.assertIn(".docx extension", result["error"])

    def test_unknown_block_field(self):
        result = self.tool.execute(
            mode="create", file_path="report.docx", blocks=[{"type": "paragraph", "text": "x", "code": "bad"}]
        )
        self.assertIn("unknown fields", result["error"])

    def test_invalid_heading_level(self):
        result = self.tool.execute(
            mode="create", file_path="report.docx", blocks=[{"type": "heading", "text": "x", "level": 0}]
        )
        self.assertIn("between 1 and 9", result["error"])

    def test_text_budget(self):
        self.tool.max_text_chars = 3
        result = self.tool.execute(
            mode="create", file_path="report.docx", blocks=[{"type": "paragraph", "text": "long"}]
        )
        self.assertIn("max_text_chars", result["error"])

    def test_read_truncates(self):
        self.tool.execute(mode="create", file_path="report.docx", blocks=[{"type": "paragraph", "text": "long text"}])
        self.tool.max_text_chars = 4
        result = self.tool.execute(mode="read", file_path="report.docx")
        self.assertTrue(result["truncated"])

    def test_rejects_invalid_docx_archive(self):
        with open(os.path.join(self.directory.name, "bad.docx"), "wb") as output:
            output.write(b"not-a-zip")
        result = self.tool.execute(mode="info", file_path="bad.docx")
        self.assertIn("not a valid DOCX archive", result["error"])

    def test_rejects_archive_expansion_over_limit(self):
        path = os.path.join(self.directory.name, "large.docx")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("word/document.xml", "x" * 100)
        self.tool.max_uncompressed_bytes = 32
        result = self.tool.execute(mode="info", file_path="large.docx")
        self.assertIn("max_uncompressed_bytes", result["error"])

    def test_generated_document_uses_write_not_read_limit(self):
        self.tool.max_read_bytes = 1
        self.tool.max_write_bytes = 1024 * 1024
        result = self.tool.execute(
            mode="create", file_path="report.docx", blocks=[{"type": "paragraph", "text": "works"}]
        )
        self.assertEqual(result["status"], "success")

    def test_missing_dependency_hint(self):
        with patch.object(self.tool, "_document_class", side_effect=ImportError("missing")):
            result = self.tool.execute(
                mode="create", file_path="report.docx", blocks=[{"type": "paragraph", "text": "x"}]
            )
        self.assertIn("pip install python-docx", result["error"])


class WordDocumentRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "WordDocumentTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, WordDocumentTool)
        self.assertEqual(tool.input_keys, ["mode", "file_path"])


if __name__ == "__main__":
    unittest.main()
