import os
import tempfile
import unittest
from email import policy
from email.message import EmailMessage

from agentuniverse.agent.action.tool.common_tool import email_document_tool as email_module
from agentuniverse.agent.action.tool.common_tool.email_document_tool import EmailDocumentTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(email_module.__file__), "email_document_tool.yaml")


class EmailDocumentToolTest(unittest.TestCase):
    """Unit tests for the create/read/extract/info modes of EmailDocumentTool."""
    def setUp(self):
        """Set up a temporary directory and an EmailDocumentTool instance backed by it, seeded with a sample attachment file."""
        self.directory = tempfile.TemporaryDirectory()
        self.tool = EmailDocumentTool(base_dir=self.directory.name)
        self.write("files/report.txt", b"quarterly data")

    def tearDown(self):
        """Clean up the temporary directory created in setUp."""
        self.directory.cleanup()

    def write(self, name, content):
        """Write the given bytes to the named file inside the temporary directory, creating parent directories as needed."""
        path = os.path.join(self.directory.name, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as output:
            output.write(content)
        return path

    def create(self, name="message.eml", **kwargs):
        """Execute the tool in create mode with default headers/body, letting keyword arguments override any parameter."""
        params = {
            "mode": "create",
            "file_path": name,
            "headers": {"from": "sender@example.com", "to": "user@example.com", "subject": "Report"},
            "text_body": "Hello 世界",
        }
        params.update(kwargs)
        return self.tool.execute(**params)

    def save_message(self, name, message):
        """Serialize an EmailMessage with the default email policy and write it to the named file inside the temporary directory."""
        self.write(name, message.as_bytes(policy=policy.default))

    def test_create_read_info_round_trip(self):
        """Verify a created message can be read back with headers/body/attachment intact and info reports the attachment count."""
        result = self.create(html_body="<p>Hello</p>", attachments=["files/report.txt"])
        self.assertEqual(result["status"], "success")
        read = self.tool.execute(mode="read", file_path="message.eml")
        self.assertEqual(read["headers"]["subject"], "Report")
        self.assertIn("Hello 世界", read["text_body"])
        self.assertIn("<p>Hello</p>", read["html_body"])
        self.assertEqual(read["attachments"][0]["name"], "report.txt")
        info = self.tool.execute(mode="info", file_path="message.eml")
        self.assertEqual(info["attachment_count"], 1)

    def test_extract_attachment(self):
        """Verify extract mode writes the message attachment into the output directory."""
        self.create(attachments=["files/report.txt"])
        result = self.tool.execute(mode="extract", file_path="message.eml", output_dir="out")
        self.assertEqual(result["status"], "success")
        with open(os.path.join(self.directory.name, "out/report.txt"), "rb") as stream:
            self.assertEqual(stream.read(), b"quarterly data")

    def test_selective_extract(self):
        """Verify extract mode honors attachment_names and only extracts the requested attachment."""
        self.write("files/other.bin", b"other")
        self.create(attachments=["files/report.txt", "files/other.bin"])
        result = self.tool.execute(
            mode="extract", file_path="message.eml", output_dir="out", attachment_names=["other.bin"]
        )
        self.assertEqual(len(result["output_paths"]), 1)
        self.assertTrue(result["output_paths"][0].endswith("other.bin"))

    def test_extract_preflights_overwrite(self):
        """Verify extract mode refuses to overwrite an existing output file unless overwrite is set, leaving no partial output."""
        self.write("files/other.bin", b"other")
        self.create(attachments=["files/report.txt", "files/other.bin"])
        self.write("out/other.bin", b"existing")
        result = self.tool.execute(mode="extract", file_path="message.eml", output_dir="out")
        self.assertIn("overwrite=true", result["error"])
        self.assertFalse(os.path.exists(os.path.join(self.directory.name, "out/report.txt")))

    def test_rejects_unsafe_attachment_filename(self):
        """Verify reading a message with a path-traversing attachment filename is rejected."""
        message = EmailMessage()
        message["From"] = "a@example.com"
        message["To"] = "b@example.com"
        message.set_content("hello")
        message.add_attachment(b"bad", maintype="application", subtype="octet-stream", filename="../evil.txt")
        self.save_message("evil.eml", message)
        result = self.tool.execute(mode="read", file_path="evil.eml")
        self.assertIn("unsafe attachment filename", result["error"])

    def test_rejects_duplicate_attachment_names(self):
        """Verify messages whose attachments share a filename are rejected in info mode."""
        message = EmailMessage()
        message["From"] = "a@example.com"
        message["To"] = "b@example.com"
        message.set_content("hello")
        for payload in (b"one", b"two"):
            message.add_attachment(payload, maintype="application", subtype="octet-stream", filename="same.bin")
        self.save_message("duplicate.eml", message)
        result = self.tool.execute(mode="info", file_path="duplicate.eml")
        self.assertIn("duplicate attachment", result["error"])

    def test_rejects_header_injection(self):
        """Verify headers containing newline characters are rejected as invalid."""
        result = self.create(headers={"from": "a@example.com\nBcc: x@example.com", "to": "b@example.com"})
        self.assertIn("invalid characters", result["error"])

    def test_requires_sender_and_recipient(self):
        """Verify create mode requires both the from and to headers."""
        result = self.create(headers={"from": "a@example.com"})
        self.assertIn("headers.to is required", result["error"])

    def test_requires_a_body(self):
        """Verify create mode requires a text or html body."""
        result = self.create(text_body=None, html_body=None)
        self.assertIn("text_body or html_body", result["error"])

    def test_read_truncates_body(self):
        """Verify read mode truncates the body to max_body_chars and flags the result as truncated."""
        self.create(text_body="abcdefgh")
        self.tool.max_body_chars = 4
        result = self.tool.execute(mode="read", file_path="message.eml")
        self.assertTrue(result["truncated"])
        self.assertEqual(result["text_body"], "abcd")

    def test_attachment_size_limit(self):
        """Verify create mode rejects attachments larger than max_attachment_bytes."""
        self.tool.max_attachment_bytes = 3
        result = self.create(attachments=["files/report.txt"])
        self.assertIn("max_attachment_bytes", result["error"])

    def test_create_refuses_overwrite(self):
        """Verify create mode refuses to overwrite an existing file unless overwrite is set."""
        self.create()
        result = self.create(text_body="replacement")
        self.assertIn("overwrite=true", result["error"])

    def test_write_limit_preserves_existing(self):
        """Verify exceeding max_write_bytes fails without modifying the existing destination file."""
        self.write("message.eml", b"existing")
        self.tool.max_write_bytes = 1
        result = self.create(overwrite=True)
        self.assertIn("max_write_bytes", result["error"])
        with open(os.path.join(self.directory.name, "message.eml"), "rb") as stream:
            self.assertEqual(stream.read(), b"existing")

    def test_path_and_extension_validation(self):
        """Verify path escapes and non-.eml file names are rejected in info mode."""
        self.assertIn("escapes", self.tool.execute(mode="info", file_path="../message.eml")["error"])
        self.assertIn(".eml", self.tool.execute(mode="info", file_path="message.txt")["error"])

    def test_missing_requested_attachment(self):
        """Verify extract mode reports an error when a requested attachment is not present in the message."""
        self.create(attachments=["files/report.txt"])
        result = self.tool.execute(
            mode="extract", file_path="message.eml", output_dir="out", attachment_names=["missing.bin"]
        )
        self.assertIn("not found", result["error"])


class EmailDocumentRegistrationTest(unittest.TestCase):
    """Tests that the email_document_tool.yaml configuration registers an EmailDocumentTool component."""
    def setUp(self):
        """Load the email_document_tool.yaml config and stash the current application configer so it can be restored."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the application configer saved in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the yaml loads as a TOOL component whose metadata class is EmailDocumentTool."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "EmailDocumentTool")

    def test_manager(self):
        """Verify ToolManager instantiates an EmailDocumentTool from the yaml config with the expected input keys."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, EmailDocumentTool)
        self.assertEqual(tool.input_keys, ["mode", "file_path"])


if __name__ == "__main__":
    unittest.main()
