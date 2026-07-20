#!/usr/bin/env python3
"""Bounded RFC 5322 email document operations."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import mimetypes
import os
import tempfile
from email import policy
from email.message import EmailMessage, Message
from email.parser import BytesParser
from typing import Any, ClassVar, cast

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool


class EmailDocumentTool(Tool):
    """Create, read, inspect, and extract attachments from EML files."""

    base_dir: str = "."
    max_read_bytes: int = 25 * 1024 * 1024
    max_write_bytes: int = 25 * 1024 * 1024
    max_body_chars: int = 200_000
    max_headers: int = 100
    max_attachments: int = 50
    max_attachment_bytes: int = 20 * 1024 * 1024
    max_total_attachment_bytes: int = 50 * 1024 * 1024

    _CREATE_HEADERS: ClassVar[dict[str, str]] = {
        "from": "From",
        "to": "To",
        "cc": "Cc",
        "bcc": "Bcc",
        "subject": "Subject",
        "reply_to": "Reply-To",
        "date": "Date",
        "message_id": "Message-ID",
    }
    _READ_HEADERS: ClassVar[tuple[str, ...]] = (
        "From",
        "To",
        "Cc",
        "Bcc",
        "Subject",
        "Reply-To",
        "Date",
        "Message-ID",
    )

    def execute(
        self,
        mode: str,
        file_path: str,
        headers: dict[str, str] | None = None,
        text_body: str | None = None,
        html_body: str | None = None,
        attachments: list[str] | None = None,
        output_dir: str | None = None,
        attachment_names: list[str] | None = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            path = self._eml_path(file_path, "file_path")
            if operation == "create":
                return self._create(path, headers, text_body, html_body, attachments, overwrite)
            message = self._message(path)
            if operation == "read":
                return self._read(path, message)
            if operation == "info":
                return self._info(path, message)
            return self._extract(path, message, output_dir, attachment_names, overwrite)
        except (TypeError, ValueError) as exc:
            return self._error(file_path, "validation_error", str(exc))
        except Exception as exc:
            return self._error(file_path, "operation_error", f"Email operation failed: {exc}")

    @staticmethod
    def _error(path: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "file_path": path}

    def _validate_config(self) -> None:
        for name in (
            "max_read_bytes",
            "max_write_bytes",
            "max_body_chars",
            "max_headers",
            "max_attachments",
            "max_attachment_bytes",
            "max_total_attachment_bytes",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in {"create", "read", "info", "extract"}:
            raise ValueError("mode must be create, read, info, or extract")
        return mode

    def _eml_path(self, value: Any, field: str) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError(f"{field} must be a non-empty string")
        if os.path.splitext(value)[1].lower() != ".eml":
            raise ValueError(f"{field} must have a .eml extension")
        return cast(str, resolve_safe_path(value, self.base_dir))

    def _directory(self, value: Any) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError("output_dir must be a non-empty string")
        return cast(str, resolve_safe_path(value, self.base_dir))

    def _message(self, path: str) -> EmailMessage:
        if not os.path.isfile(path):
            raise ValueError(f"file_path does not exist: {path}")
        if os.path.getsize(path) > self.max_read_bytes:
            raise ValueError(f"file_path exceeds max_read_bytes ({self.max_read_bytes})")
        with open(path, "rb") as stream:
            message = BytesParser(policy=policy.default).parse(stream)
        if len(message.items()) > self.max_headers:
            raise ValueError(f"email exceeds max_headers ({self.max_headers})")
        self._attachment_parts(message)
        return cast(EmailMessage, message)

    @staticmethod
    def _safe_header(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"headers.{field} must be a non-empty string")
        if "\r" in value or "\n" in value or len(value) > 2_000:
            raise ValueError(f"headers.{field} contains invalid characters or is too long")
        return value.strip()

    def _headers(self, value: Any) -> dict[str, str]:
        if not isinstance(value, dict):
            raise TypeError("headers must be an object")
        unknown = set(value) - set(self._CREATE_HEADERS)
        if unknown:
            raise ValueError(f"headers contain unknown fields: {', '.join(sorted(unknown))}")
        output = {key: self._safe_header(item, key) for key, item in value.items()}
        for required in ("from", "to"):
            if required not in output:
                raise ValueError(f"headers.{required} is required")
        return output

    def _body(self, value: Any, field: str) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError(f"{field} must be a string")
        if len(value) > self.max_body_chars:
            raise ValueError(f"{field} exceeds max_body_chars ({self.max_body_chars})")
        return value

    @staticmethod
    def _safe_filename(value: Any) -> str:
        if not isinstance(value, str) or not value or "\x00" in value:
            raise ValueError("attachment has an invalid filename")
        if value in {".", ".."} or os.path.basename(value) != value or "/" in value or "\\" in value:
            raise ValueError(f"unsafe attachment filename: {value}")
        return value

    def _attachment_inputs(self, values: Any) -> list[tuple[str, str, str, str]]:
        if values is None:
            return []
        if not isinstance(values, list):
            raise TypeError("attachments must be a list")
        if len(values) > self.max_attachments:
            raise ValueError(f"attachments exceed max_attachments ({self.max_attachments})")
        output: list[tuple[str, str, str, str]] = []
        names: set[str] = set()
        total = 0
        for index, value in enumerate(values):
            if not isinstance(value, str) or not value:
                raise ValueError(f"attachments[{index}] must be a non-empty string")
            path = cast(str, resolve_safe_path(value, self.base_dir))
            if not os.path.isfile(path):
                raise ValueError(f"attachment does not exist: {path}")
            size = os.path.getsize(path)
            if size > self.max_attachment_bytes:
                raise ValueError(f"attachment exceeds max_attachment_bytes: {path}")
            total += size
            name = self._safe_filename(os.path.basename(path))
            if name in names:
                raise ValueError(f"duplicate attachment filename: {name}")
            names.add(name)
            content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
            maintype, subtype = content_type.split("/", 1)
            output.append((path, name, maintype, subtype))
        if total > self.max_total_attachment_bytes:
            raise ValueError("attachments exceed max_total_attachment_bytes")
        return output

    def _create(
        self,
        path: str,
        headers: Any,
        text_body: Any,
        html_body: Any,
        attachments: Any,
        overwrite: Any,
    ) -> dict[str, Any]:
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be a boolean")
        if os.path.exists(path) and not overwrite:
            raise ValueError("file exists; set overwrite=true to replace it")
        normalized_headers = self._headers(headers)
        text = self._body(text_body, "text_body")
        html = self._body(html_body, "html_body")
        if text is None and html is None:
            raise ValueError("text_body or html_body is required")
        files = self._attachment_inputs(attachments)
        message = EmailMessage(policy=policy.default)
        for key, value in normalized_headers.items():
            message[self._CREATE_HEADERS[key]] = value
        message.set_content(text or "")
        if html is not None:
            message.add_alternative(html, subtype="html")
        for source, name, maintype, subtype in files:
            with open(source, "rb") as stream:
                message.add_attachment(stream.read(), maintype=maintype, subtype=subtype, filename=name)
        self._atomic_write(path, message.as_bytes())
        return {
            "status": "success",
            "mode": "create",
            "file_path": path,
            "attachment_count": len(files),
            "file_size": os.path.getsize(path),
        }

    def _attachment_parts(self, message: Message) -> list[dict[str, Any]]:
        output = []
        total = 0
        names: set[str] = set()
        for part in message.walk():
            filename = part.get_filename()
            if not filename:
                continue
            name = self._safe_filename(str(filename))
            payload = part.get_payload(decode=True) or b""
            size = len(payload)
            if size > self.max_attachment_bytes:
                raise ValueError(f"attachment exceeds max_attachment_bytes: {name}")
            if name in names:
                raise ValueError(f"duplicate attachment filename: {name}")
            names.add(name)
            total += size
            output.append({"name": name, "size": size, "content_type": part.get_content_type(), "part": part})
        if len(output) > self.max_attachments:
            raise ValueError(f"email exceeds max_attachments ({self.max_attachments})")
        if total > self.max_total_attachment_bytes:
            raise ValueError("email attachments exceed max_total_attachment_bytes")
        return output

    def _body_parts(self, message: Message) -> tuple[str, str, bool]:
        text_parts: list[str] = []
        html_parts: list[str] = []
        for part in message.walk():
            if part.get_filename() or part.get_content_maintype() == "multipart":
                continue
            if part.get_content_type() not in {"text/plain", "text/html"}:
                continue
            try:
                content = part.get_content()
            except (KeyError, LookupError, UnicodeError) as exc:
                raise ValueError(f"unable to decode email body: {exc}") from exc
            (html_parts if part.get_content_type() == "text/html" else text_parts).append(str(content))
        text = "\n".join(text_parts).strip()
        html = "\n".join(html_parts).strip()
        total = len(text) + len(html)
        if total <= self.max_body_chars:
            return text, html, False
        remaining = self.max_body_chars
        text, remaining = text[:remaining], max(0, remaining - len(text))
        html = html[:remaining]
        return text, html, True

    def _header_output(self, message: Message) -> dict[str, str]:
        return {name.lower().replace("-", "_"): str(message.get(name, "")) for name in self._READ_HEADERS}

    def _read(self, path: str, message: Message) -> dict[str, Any]:
        text, html, truncated = self._body_parts(message)
        attachments = self._attachment_parts(message)
        return {
            "status": "success",
            "mode": "read",
            "file_path": path,
            "headers": self._header_output(message),
            "text_body": text,
            "html_body": html,
            "truncated": truncated,
            "attachments": [{key: item[key] for key in ("name", "size", "content_type")} for item in attachments],
        }

    def _info(self, path: str, message: Message) -> dict[str, Any]:
        text, html, truncated = self._body_parts(message)
        attachments = self._attachment_parts(message)
        return {
            "status": "success",
            "mode": "info",
            "file_path": path,
            "file_size": os.path.getsize(path),
            "headers": self._header_output(message),
            "header_count": len(message.items()),
            "attachment_count": len(attachments),
            "attachment_bytes": sum(item["size"] for item in attachments),
            "text_chars": len(text),
            "html_chars": len(html),
            "truncated": truncated,
        }

    def _extract(
        self,
        path: str,
        message: Message,
        output_dir: Any,
        names: Any,
        overwrite: Any,
    ) -> dict[str, Any]:
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be a boolean")
        directory = self._directory(output_dir)
        attachments = self._attachment_parts(message)
        if names is not None:
            if not isinstance(names, list) or not names or any(not isinstance(item, str) for item in names):
                raise ValueError("attachment_names must be a non-empty list of strings")
            requested = {self._safe_filename(item) for item in names}
            missing = requested - {item["name"] for item in attachments}
            if missing:
                raise ValueError(f"attachments not found: {', '.join(sorted(missing))}")
            attachments = [item for item in attachments if item["name"] in requested]
        destinations = [(item, cast(str, resolve_safe_path(item["name"], directory))) for item in attachments]
        for _, destination in destinations:
            if os.path.exists(destination) and not overwrite:
                raise ValueError(f"file exists: {destination}; set overwrite=true")
        os.makedirs(directory, exist_ok=True)
        outputs = []
        for item, destination in destinations:
            self._atomic_write(destination, item["part"].get_payload(decode=True) or b"")
            outputs.append(destination)
        return {
            "status": "success",
            "mode": "extract",
            "file_path": path,
            "output_dir": directory,
            "output_paths": outputs,
            "attachment_count": len(outputs),
        }

    def _atomic_write(self, destination: str, content: bytes) -> None:
        if len(content) > self.max_write_bytes:
            raise ValueError(f"generated file exceeds max_write_bytes ({self.max_write_bytes})")
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=".email-", dir=os.path.dirname(destination), delete=False
            ) as output:
                temporary = output.name
                output.write(content)
            os.replace(temporary, destination)
            temporary = None
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
