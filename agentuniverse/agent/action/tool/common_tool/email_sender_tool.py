#!/usr/bin/env python3
"""Email sender tool with bounded safety.

Sends plain-text or HTML emails via SMTP. Supports TLS, authentication,
and optional file attachments. All operations are gated behind an explicit
``allow_send`` opt-in (default False) so the tool cannot send emails
without the integrator's knowledge — same spirit as RunCommandTool (#657)
and PythonREPL (#608).

Uses Python's built-in ``smtplib`` and ``email`` modules — zero third-party
dependency. Addresses #252.
"""

# ruff: noqa: TRY003, TRY004

import logging
import mimetypes
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, ClassVar, List, Optional

from agentuniverse.agent.action.tool.common_tool.file_path_utils import \
    resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)


class EmailSenderTool(Tool):
    """Bounded email sender tool gated behind ``allow_send`` opt-in.

    Attributes:
        smtp_host: SMTP server hostname.
        smtp_port: SMTP server port (default 587 for STARTTLS).
        smtp_username: SMTP username.
        smtp_password: SMTP password.
        use_tls: Whether to use STARTTLS (default True).
        use_ssl: Whether to use SSL (default False; mutually exclusive with TLS).
        sender_email: Default sender email address.
        allow_send: Opt-in gate. If False (default), the tool refuses to send
            and returns a clear error. Set to True to enable.
        max_attachment_bytes: Maximum total attachment size in bytes (default 10 MB).
        max_recipients: Maximum number of recipients (default 50).
        base_dir: Base directory for resolving attachment paths.
    """

    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    use_tls: bool = True
    use_ssl: bool = False
    sender_email: Optional[str] = None
    allow_send: bool = False
    max_attachment_bytes: int = 10 * 1024 * 1024
    max_recipients: int = 50
    base_dir: str = "."

    def execute(self, mode: str = "send", to: str = "", subject: str = "",
                body: str = "", html: bool = False,
                attachments: Optional[List[str]] = None,
                cc: str = "", bcc: str = "",
                **kwargs) -> dict:
        try:
            op = self._normalize_mode(mode)
            if op == "send":
                return self._send(to, subject, body, html, attachments, cc, bcc)
            return self._error("validation_error", f"Unknown mode: {mode}")
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc))
        except Exception as exc:
            return self._error("operation_error", str(exc))

    @staticmethod
    def _normalize_mode(mode: str) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        normalized = mode.strip().lower()
        if normalized != "send":
            raise ValueError("mode must be 'send'")
        return normalized

    @staticmethod
    def _error(error_type: str, message: str) -> dict:
        return {"status": "error", "error_type": error_type, "error": message}

    @staticmethod
    def _ok(**kwargs) -> dict:
        return {"status": "success", **kwargs}

    def _send(self, to: str, subject: str, body: str,
              html: bool, attachments: Optional[List[str]],
              cc: str, bcc: str) -> dict:
        if not self.allow_send:
            return self._error(
                "permission_error",
                "EmailSenderTool is disabled by default. Set allow_send: true "
                "on the component to enable email sending.")
        if not self.smtp_host:
            return self._error("validation_error",
                               "smtp_host must be configured")
        if not to:
            return self._error("validation_error",
                               "at least one recipient (to) is required")
        if not self.sender_email:
            return self._error("validation_error",
                               "sender_email must be configured")

        # Parse and bound recipients.
        recipients = [r.strip() for r in to.split(",") if r.strip()]
        cc_list = [r.strip() for r in cc.split(",") if cc and r.strip()]
        bcc_list = [r.strip() for r in bcc.split(",") if bcc and r.strip()]
        all_recipients = recipients + cc_list + bcc_list
        if len(all_recipients) > self.max_recipients:
            return self._error("validation_error",
                               f"Total recipients ({len(all_recipients)}) exceed "
                               f"max_recipients ({self.max_recipients})")

        # Build message.
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = ", ".join(recipients)
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        msg["Subject"] = subject or "(no subject)"

        content_type = "html" if html else "plain"
        msg.attach(MIMEText(body or "", content_type))

        # Attachments.
        total_attach_size = 0
        if attachments:
            for path_str in attachments:
                safe_path = resolve_safe_path(path_str, self.base_dir)
                if not os.path.isfile(safe_path):
                    return self._error("validation_error",
                                       f"Attachment not found: {path_str}")
                file_size = os.path.getsize(safe_path)
                total_attach_size += file_size
                if total_attach_size > self.max_attachment_bytes:
                    return self._error(
                        "validation_error",
                        f"Total attachment size ({total_attach_size} bytes) exceeds "
                        f"max_attachment_bytes ({self.max_attachment_bytes})")
                with open(safe_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(safe_path))
                part["Content-Disposition"] = (
                    f'attachment; filename="{os.path.basename(safe_path)}"')
                msg.attach(part)

        # Send via SMTP.
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            try:
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender_email, all_recipients, msg.as_string())
            finally:
                server.quit()
        except smtplib.SMTPException as exc:
            return self._error("operation_error",
                               f"SMTP error: {exc}")

        return self._ok(
            mode="send",
            recipients=recipients,
            cc=cc_list,
            bcc=bcc_list,
            subject=subject,
            attachments=len(attachments) if attachments else 0,
        )

    def _initialize_by_component_configer(self, configer: ComponentConfiger) \
            -> "EmailSenderTool":
        super()._initialize_by_component_configer(configer)
        for field in ("smtp_host", "smtp_port", "smtp_username", "smtp_password",
                      "use_tls", "use_ssl", "sender_email", "allow_send",
                      "max_attachment_bytes", "max_recipients", "base_dir"):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        return self
