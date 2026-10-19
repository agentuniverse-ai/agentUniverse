#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for EmailSenderTool."""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.tool.common_tool.email_sender_tool \
    import EmailSenderTool


class TestEmailSenderToolOptIn(unittest.TestCase):

    def test_disabled_by_default(self):
        tool = EmailSenderTool()
        result = tool.execute(to="a@b.com", subject="test", body="hello")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "permission_error")

    def test_enabled_sends(self):
        tool = EmailSenderTool(
            allow_send=True, smtp_host="smtp.test.com",
            sender_email="bot@test.com")
        with patch("smtplib.SMTP") as mock_smtp:
            server = MagicMock()
            mock_smtp.return_value = server
            result = tool.execute(to="a@b.com", subject="test", body="hello")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["recipients"], ["a@b.com"])


class TestEmailSenderValidation(unittest.TestCase):

    def _tool(self):
        return EmailSenderTool(
            allow_send=True, smtp_host="smtp.test.com",
            sender_email="bot@test.com")

    def test_missing_smtp_host(self):
        tool = EmailSenderTool(allow_send=True, sender_email="b@t.com")
        result = tool.execute(to="a@b.com", body="x")
        self.assertEqual(result["status"], "error")

    def test_missing_recipient(self):
        tool = self._tool()
        result = tool.execute(to="", body="x")
        self.assertEqual(result["status"], "error")

    def test_missing_sender(self):
        tool = EmailSenderTool(allow_send=True, smtp_host="smtp.test.com")
        result = tool.execute(to="a@b.com", body="x")
        self.assertEqual(result["status"], "error")

    def test_too_many_recipients(self):
        tool = self._tool()
        tool.max_recipients = 2
        result = tool.execute(to="a@b.com,c@d.com,e@f.com", body="x")
        self.assertEqual(result["status"], "error")
        self.assertIn("max_recipients", result["error"])

    def test_unknown_mode(self):
        tool = self._tool()
        result = tool.execute(mode="receive")
        self.assertEqual(result["status"], "error")


class TestEmailSenderSend(unittest.TestCase):

    def _tool(self):
        return EmailSenderTool(
            allow_send=True, smtp_host="smtp.test.com",
            sender_email="bot@test.com", smtp_username="user",
            smtp_password="pass", use_tls=True)

    def test_send_with_cc_and_bcc(self):
        tool = self._tool()
        with patch("smtplib.SMTP") as mock_smtp:
            server = MagicMock()
            mock_smtp.return_value = server
            result = tool.execute(
                to="a@b.com", cc="c@d.com", bcc="e@f.com",
                subject="test", body="hello")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["cc"]), 1)
        self.assertEqual(len(result["bcc"]), 1)

    def test_send_html(self):
        tool = self._tool()
        with patch("smtplib.SMTP") as mock_smtp:
            server = MagicMock()
            mock_smtp.return_value = server
            result = tool.execute(
                to="a@b.com", subject="test", body="<b>hello</b>", html=True)
        self.assertEqual(result["status"], "success")

    def test_send_with_attachment(self):
        import tempfile, os
        tool = self._tool()
        # Set base_dir to system temp so resolve_safe_path accepts the temp file.
        tmp_dir = tempfile.mkdtemp()
        tool.base_dir = tmp_dir
        att_path = os.path.join(tmp_dir, "test.txt")
        with open(att_path, "w") as f:
            f.write("attachment content")
        try:
            with patch("smtplib.SMTP") as mock_smtp:
                server = MagicMock()
                mock_smtp.return_value = server
                result = tool.execute(
                    to="a@b.com", subject="test", body="hello",
                    attachments=[att_path])
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["attachments"], 1)
        finally:
            import shutil; shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_attachment_too_large(self):
        import tempfile, os
        tool = self._tool()
        tool.max_attachment_bytes = 5
        tmp_dir = tempfile.mkdtemp()
        tool.base_dir = tmp_dir
        att_path = os.path.join(tmp_dir, "big.txt")
        with open(att_path, "w") as f:
            f.write("x" * 100)
        try:
            result = tool.execute(
                to="a@b.com", subject="test", body="hello",
                attachments=[att_path])
            self.assertEqual(result["status"], "error")
            self.assertIn("max_attachment_bytes", result["error"])
        finally:
            import shutil; shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_smtp_error_returns_structured(self):
        import smtplib
        tool = self._tool()
        with patch("smtplib.SMTP") as mock_smtp:
            server = MagicMock()
            server.login.side_effect = smtplib.SMTPAuthenticationError(
                code=535, msg=b"auth failed")
            mock_smtp.return_value = server
            result = tool.execute(to="a@b.com", body="x")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "operation_error")

    def test_socket_timeout_passed_to_smtp(self):
        tool = self._tool()
        tool.timeout = 7.5
        with patch("smtplib.SMTP") as mock_smtp:
            mock_smtp.return_value = MagicMock()
            result = tool.execute(to="a@b.com", body="x")
        self.assertEqual(result["status"], "success")
        self.assertEqual(mock_smtp.call_args.kwargs.get("timeout"), 7.5)

    def test_whitespace_only_recipients_rejected(self):
        tool = self._tool()
        result = tool.execute(to=" , , ", body="x")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("recipient", result["error"])


class TestEmailSenderComponentConfig(unittest.TestCase):
    """YAML-driven configuration must reach the tool instance."""

    def _tool_from_config(self, extra: dict) -> EmailSenderTool:
        import tempfile
        import os
        import yaml
        from agentuniverse.base.config.configer import Configer
        from agentuniverse.base.config.component_configer.configers.tool_configer \
            import ToolConfiger
        payload = {
            "name": "email_sender_tool_cfgtest",
            "description": "test instance",
            "tool_type": "api",
            "metadata": {
                "type": "TOOL",
                "module": "agentuniverse.agent.action.tool.common_tool.email_sender_tool",
                "class": "EmailSenderTool",
            },
        }
        payload.update(extra)
        tmp_dir = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp_dir, "email_sender_tool_cfgtest.yaml")
            with open(path, "w", encoding="utf-8") as handle:
                yaml.safe_dump(payload, handle)
            config = Configer(path=path).load()
            component = ToolConfiger().load_by_configer(config)
            tool = EmailSenderTool()
            tool.initialize_by_component_configer(component)
            return tool
        finally:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_yaml_fields_applied(self):
        tool = self._tool_from_config({
            "smtp_host": "smtp.example.com",
            "smtp_port": 465,
            "use_ssl": True,
            "use_tls": False,
            "sender_email": "bot@example.com",
            "allow_send": True,
            "timeout": 12,
            "max_recipients": 3,
        })
        self.assertEqual(tool.smtp_host, "smtp.example.com")
        self.assertEqual(tool.smtp_port, 465)
        self.assertTrue(tool.use_ssl)
        self.assertFalse(tool.use_tls)
        self.assertEqual(tool.sender_email, "bot@example.com")
        self.assertTrue(tool.allow_send)
        self.assertEqual(tool.timeout, 12)
        self.assertEqual(tool.max_recipients, 3)

    def test_empty_string_placeholders_fall_back_to_none(self):
        tool = self._tool_from_config({
            "smtp_host": "",
            "smtp_username": "   ",
            "smtp_password": "${SMTP_PASSWORD}",
            "sender_email": "",
        })
        self.assertIsNone(tool.smtp_host)
        self.assertIsNone(tool.smtp_username)
        self.assertIsNone(tool.smtp_password)
        self.assertIsNone(tool.sender_email)

    def test_absent_fields_keep_defaults(self):
        tool = self._tool_from_config({})
        self.assertIsNone(tool.smtp_host)
        self.assertFalse(tool.allow_send)
        self.assertEqual(tool.timeout, 30.0)
        self.assertEqual(tool.max_recipients, 50)


if __name__ == "__main__":
    unittest.main(verbosity=2)
