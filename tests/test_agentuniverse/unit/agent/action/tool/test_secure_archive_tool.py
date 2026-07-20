import os
import stat
import tempfile
import unittest
import zipfile

from agentuniverse.agent.action.tool.common_tool import secure_archive_tool as archive_module
from agentuniverse.agent.action.tool.common_tool.secure_archive_tool import SecureArchiveTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(archive_module.__file__), "secure_archive_tool.yaml")


class SecureArchiveToolTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.tool = SecureArchiveTool(base_dir=self.directory.name)
        self.write("a.txt", b"alpha")
        self.write("nested/b.txt", b"beta")

    def tearDown(self):
        self.directory.cleanup()

    def write(self, name, data):
        path = os.path.join(self.directory.name, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as output:
            output.write(data)
        return path

    def test_zip_round_trip(self):
        created = self.tool.execute(mode="create", file_path="bundle.zip", input_paths=["a.txt", "nested"])
        self.assertEqual(created["status"], "success")
        self.assertEqual(created["entry_count"], 2)
        listed = self.tool.execute(mode="list", file_path="bundle.zip")
        self.assertEqual({item["name"] for item in listed["entries"]}, {"a.txt", "nested/b.txt"})
        extracted = self.tool.execute(mode="extract", file_path="bundle.zip", output_dir="out")
        self.assertEqual(extracted["status"], "success")
        with open(os.path.join(self.directory.name, "out/nested/b.txt"), "rb") as stream:
            self.assertEqual(stream.read(), b"beta")

    def test_tar_gz_round_trip(self):
        result = self.tool.execute(mode="create", file_path="bundle.tar.gz", input_paths=["nested"])
        self.assertEqual(result["status"], "success")
        info = self.tool.execute(mode="info", file_path="bundle.tar.gz")
        self.assertEqual(info["format"], "tar")
        self.assertEqual(info["file_count"], 1)
        extracted = self.tool.execute(mode="extract", file_path="bundle.tar.gz", output_dir="tar-out")
        self.assertEqual(extracted["entry_count"], 1)

    def test_selective_extract(self):
        self.tool.execute(mode="create", file_path="bundle.zip", input_paths=["a.txt", "nested/b.txt"])
        result = self.tool.execute(mode="extract", file_path="bundle.zip", output_dir="out", members=["nested/b.txt"])
        self.assertEqual(len(result["output_paths"]), 1)
        self.assertFalse(os.path.exists(os.path.join(self.directory.name, "out/a.txt")))

    def test_create_refuses_overwrite(self):
        self.tool.execute(mode="create", file_path="bundle.zip", input_paths=["a.txt"])
        result = self.tool.execute(mode="create", file_path="bundle.zip", input_paths=["nested/b.txt"])
        self.assertIn("overwrite=true", result["error"])

    def test_extract_preflights_destinations(self):
        self.tool.execute(mode="create", file_path="bundle.zip", input_paths=["a.txt", "nested/b.txt"])
        self.write("out/nested/b.txt", b"existing")
        result = self.tool.execute(mode="extract", file_path="bundle.zip", output_dir="out")
        self.assertIn("overwrite=true", result["error"])
        self.assertFalse(os.path.exists(os.path.join(self.directory.name, "out/a.txt")))

    def test_rejects_zip_slip(self):
        with zipfile.ZipFile(os.path.join(self.directory.name, "evil.zip"), "w") as archive:
            archive.writestr("../escape.txt", "bad")
        result = self.tool.execute(mode="list", file_path="evil.zip")
        self.assertIn("unsafe archive member", result["error"])

    def test_rejects_zip_symlink(self):
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(os.path.join(self.directory.name, "link.zip"), "w") as archive:
            archive.writestr(info, "target")
        result = self.tool.execute(mode="list", file_path="link.zip")
        self.assertIn("symlink", result["error"])

    def test_rejects_duplicate_members(self):
        with zipfile.ZipFile(os.path.join(self.directory.name, "duplicate.zip"), "w") as archive:
            archive.writestr("same.txt", "one")
            archive.writestr("same.txt", "two")
        result = self.tool.execute(mode="info", file_path="duplicate.zip")
        self.assertIn("duplicate", result["error"])

    def test_rejects_compression_bomb_ratio(self):
        with zipfile.ZipFile(os.path.join(self.directory.name, "ratio.zip"), "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("large.txt", "x" * 100_000)
        self.tool.max_compression_ratio = 2
        result = self.tool.execute(mode="info", file_path="ratio.zip")
        self.assertIn("max_compression_ratio", result["error"])

    def test_rejects_too_many_entries(self):
        with zipfile.ZipFile(os.path.join(self.directory.name, "many.zip"), "w") as archive:
            archive.writestr("one", "1")
            archive.writestr("two", "2")
        self.tool.max_entries = 1
        result = self.tool.execute(mode="list", file_path="many.zip")
        self.assertIn("max_entries", result["error"])

    def test_input_and_output_path_escape(self):
        result = self.tool.execute(mode="create", file_path="../bundle.zip", input_paths=["a.txt"])
        self.assertIn("escapes the allowed directory", result["error"])
        self.tool.execute(mode="create", file_path="bundle.zip", input_paths=["a.txt"])
        result = self.tool.execute(mode="extract", file_path="bundle.zip", output_dir="../out")
        self.assertIn("escapes the allowed directory", result["error"])

    def test_invalid_extension(self):
        result = self.tool.execute(mode="info", file_path="bundle.rar")
        self.assertIn(".zip", result["error"])

    def test_generated_size_limit_preserves_destination(self):
        self.write("bundle.zip", b"existing")
        self.tool.max_write_bytes = 1
        result = self.tool.execute(mode="create", file_path="bundle.zip", input_paths=["a.txt"], overwrite=True)
        self.assertIn("max_write_bytes", result["error"])
        with open(os.path.join(self.directory.name, "bundle.zip"), "rb") as stream:
            self.assertEqual(stream.read(), b"existing")

    def test_missing_member(self):
        self.tool.execute(mode="create", file_path="bundle.zip", input_paths=["a.txt"])
        result = self.tool.execute(mode="extract", file_path="bundle.zip", output_dir="out", members=["missing.txt"])
        self.assertIn("not found", result["error"])


class SecureArchiveRegistrationTest(unittest.TestCase):
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
        self.assertEqual(component.metadata_class, "SecureArchiveTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, SecureArchiveTool)
        self.assertEqual(tool.input_keys, ["mode", "file_path"])


if __name__ == "__main__":
    unittest.main()
