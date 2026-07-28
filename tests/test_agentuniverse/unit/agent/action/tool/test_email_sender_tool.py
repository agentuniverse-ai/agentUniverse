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


if __name__ == "__main__":
    unittest.main(verbosity=2)
