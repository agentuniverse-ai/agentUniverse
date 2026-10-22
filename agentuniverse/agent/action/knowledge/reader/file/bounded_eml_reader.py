# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: bounded_eml_reader.py

"""Bounded RFC 822 / MIME email (.eml) reader.

Reads at most ``max_file_bytes`` plus one probe byte (no stat/read TOCTOU),
prefers the ``text/plain`` body part, falls back to the first ``text/html``
part rendered through the shared stdlib stripper, records the Subject/From/To/
Cc/Date/Message-ID headers into metadata (whitespace-collapsed, truncated to
2000 chars) and attachment *names* only (payloads are never decoded). Charset
failures degrade to replacement characters instead of failing the load.

Metadata keys (``email_*``, ``attachment_*``) match #3324's, so downstream
filters survive the swap.

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003
"""

import email
import email.policy
from pathlib import Path
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.reader.file.bounded_html_reader import (
    html_to_text,
)
from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

_DEFAULT_MAX_FILE_BYTES = 20 * 1024 * 1024
_MAX_HEADER_CHARS = 2000
_MAX_ATTACHMENT_NAMES = 50
_HEADERS = (
    ("email_subject", "Subject"),
    ("email_from", "From"),
    ("email_to", "To"),
    ("email_cc", "Cc"),
    ("email_date", "Date"),
    ("email_message_id", "Message-ID"),
)


class BoundedEmlReader(Reader):
    """Bounded, stdlib-only .eml reader (supersedes #3324's EmlReader)."""

    max_file_bytes: int = _DEFAULT_MAX_FILE_BYTES

    def _load_data(self, file: Path, ext_info: Optional[Dict] = None) -> List[Document]:
        self._validate_config()
        with file.open("rb") as handle:
            data = handle.read(self.max_file_bytes + 1)
        if len(data) > self.max_file_bytes:
            raise ValueError(
                f"EML file is {len(data)!r} bytes, exceeding max_file_bytes="
                f"{self.max_file_bytes!r}: {file!s}")
        message = email.message_from_bytes(data, policy=email.policy.default)
        text = self._body_text(message)
        metadata: Dict = {"file_name": file.name}
        for key, header in _HEADERS:
            collapsed = " ".join(str(message.get(header, "")).split())[:_MAX_HEADER_CHARS]
            if collapsed:
                metadata[key] = collapsed
        names = [name for part in message.iter_attachments()
                 if (name := part.get_filename())][:_MAX_ATTACHMENT_NAMES]
        if names:
            metadata["attachment_names"] = names
            metadata["attachment_count"] = len(names)
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text, metadata=metadata)]

    @staticmethod
    def _body_text(message) -> str:
        try:
            part = (message.get_body(preferencelist=("plain",))
                    or message.get_body(preferencelist=("html",)))
            if part is None:
                return ""
            content = part.get_content()
            if not isinstance(content, str):
                return ""
            if part.get_content_type() == "text/html":
                return html_to_text(content)
            return content
        except Exception:  # charset/structure failures degrade, never crash the load
            return ""

    def _validate_config(self) -> None:
        bound = self.max_file_bytes
        if not isinstance(bound, int) or isinstance(bound, bool) or bound <= 0:
            raise ValueError(f"max_file_bytes must be a positive int, got {bound!r}")

    def _initialize_by_component_configer(
            self, reader_configer: ComponentConfiger) -> "BoundedEmlReader":
        super()._initialize_by_component_configer(reader_configer)
        if hasattr(reader_configer, "max_file_bytes"):
            self.max_file_bytes = reader_configer.max_file_bytes
        self._validate_config()
        return self
