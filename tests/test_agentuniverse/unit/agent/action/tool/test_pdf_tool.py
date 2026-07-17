import os
import tempfile
import unittest
from unittest.mock import patch

from pypdf import PdfReader, PdfWriter

from agentuniverse.agent.action.tool.common_tool import pdf_tool as pdf_module
from agentuniverse.agent.action.tool.common_tool.pdf_tool import PDFTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(pdf_module.__file__), "pdf_tool.yaml")


class PDFToolTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.tool = PDFTool(base_dir=self.directory.name)
        self.make_pdf("one.pdf", 1)
        self.make_pdf("two.pdf", 2)

    def tearDown(self):
        self.directory.cleanup()

    def make_pdf(self, name, pages):
        writer = PdfWriter()
        for _ in range(pages):
            writer.add_blank_page(width=100, height=200)
        writer.add_metadata({"/Title": name})
        with open(os.path.join(self.directory.name, name), "wb") as output:
            writer.write(output)

    def test_info(self):
        result = self.tool.execute(mode="info", file_path="two.pdf")
        self.assertEqual(result["page_count"], 2)
        self.assertEqual(result["metadata"]["/Title"], "two.pdf")

    def test_merge(self):
        result = self.tool.execute(
            mode="merge", file_path="merged.pdf", input_paths=["one.pdf", "two.pdf"], metadata={"Title": "Merged"}
        )
        self.assertEqual(result["page_count"], 3)
        self.assertEqual(len(PdfReader(result["file_path"]).pages), 3)

    def test_split_selected_pages(self):
        result = self.tool.execute(mode="split", file_path="two.pdf", output_dir="parts", pages=[2])
        self.assertEqual(result["page_count"], 1)
        self.assertTrue(result["output_paths"][0].endswith("two-page-2.pdf"))

    def test_rotate(self):
        result = self.tool.execute(
            mode="rotate", file_path="two.pdf", output_path="rotated.pdf", pages=[1], rotation=90
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(PdfReader(result["output_path"]).pages[0].rotation, 90)

    def test_extract_blank_pages(self):
        result = self.tool.execute(mode="extract", file_path="two.pdf", pages=[1])
        self.assertEqual(result["pages"], [{"page": 1, "text": ""}])

    def test_refuses_overwrite(self):
        result = self.tool.execute(mode="merge", file_path="one.pdf", input_paths=["two.pdf"])
        self.assertIn("overwrite=true", result["error"])

    def test_invalid_page(self):
        result = self.tool.execute(mode="extract", file_path="one.pdf", pages=[2])
        self.assertIn("between 1 and 1", result["error"])

    def test_invalid_rotation(self):
        result = self.tool.execute(mode="rotate", file_path="one.pdf", output_path="r.pdf", rotation=45)
        self.assertIn("90, 180, or 270", result["error"])

    def test_path_escape(self):
        result = self.tool.execute(mode="info", file_path="../one.pdf")
        self.assertIn("escapes the allowed directory", result["error"])

    def test_non_pdf_signature(self):
        with open(os.path.join(self.directory.name, "bad.pdf"), "wb") as output:
            output.write(b"hello")
        result = self.tool.execute(mode="info", file_path="bad.pdf")
        self.assertIn("not a PDF", result["error"])

    def test_page_limit(self):
        self.tool.max_pages = 1
        result = self.tool.execute(mode="info", file_path="two.pdf")
        self.assertIn("max_pages", result["error"])

    def test_missing_dependency_hint(self):
        with patch.object(self.tool, "_classes", side_effect=ImportError("missing")):
            result = self.tool.execute(mode="info", file_path="one.pdf")
        self.assertIn("pip install pypdf", result["error"])


class PDFToolRegistrationTest(unittest.TestCase):
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
        self.assertEqual(component.metadata_class, "PDFTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, PDFTool)
        self.assertEqual(tool.input_keys, ["mode", "file_path"])


if __name__ == "__main__":
    unittest.main()
