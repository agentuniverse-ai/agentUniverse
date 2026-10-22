# !/usr/bin/env python3

# @Time    : 2026/10/02
# @FileName: eml_reader.py

"""
RFC 822 / MIME email (.eml) file reader.

Email archives (support threads, notification exports, correspondence
dumps) are a common knowledge source, but until now the file readers
covered txt/pdf/office/csv/archive formats only — an exported ``.eml``
had no way into a knowledge base. This reader fills that gap with the
battle-tested stdlib ``email`` parser: **no new runtime dependency**.

Each ``.eml`` file produces one Document:

* text — an optional header block (Subject / From / To / Date, so
  retrieval can match on them) followed by the message body. Body
  extraction prefers ``text/plain`` parts; HTML-only messages fall back
  to ``text/html`` with tags, ``<script>`` and ``<style>`` stripped
  (BeautifulSoup is already a core dependency). Multipart bodies are
  concatenated in order.
* metadata — ``file_name`` plus sanitized ``email_subject`` /
  ``email_from`` / ``email_to`` / ``email_cc`` / ``email_date`` /
  ``email_message_id``, and ``attachment_count`` /
  ``attachment_names`` when attachments are present.

Safety bounds (email is hostile input by nature):

* ``max_file_bytes`` (default 20 MiB) is enforced via ``stat`` *before*
  reading a path, and via a bounded read for file-like objects, so an
  oversized message never lands fully in memory;
* ``max_parts`` (default 200) caps MIME-part traversal against
  part-bomb style messages;
* attachment payloads are **never decoded** — only names are recorded —
  so a malicious attachment cannot reach a parser through this reader;
* header values are whitespace-collapsed (no newline injection into
  metadata) and truncated;
* charset failures degrade to replacement characters instead of
  crashing the whole load.

Malformed messages raise ``ValueError`` (same convention as the other
file readers); the stdlib parser itself is deliberately lenient, so
non-conforming-but-readable messages still load.
"""

import contextlib
import email
import email.policy
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)

_DEFAULT_MAX_FILE_BYTES = 20 * 1024 * 1024
_DEFAULT_MAX_PARTS = 200
_MAX_HEADER_CHARS = 2000
_MAX_ATTACHMENT_NAMES = 50

# Header fields copied into metadata, in output order.
_HEADER_FIELDS = (
    ("email_subject", "Subject"),
    ("email_from", "From"),
    ("email_to", "To"),
    ("email_cc", "Cc"),
    ("email_date", "Date"),
    ("email_message_id", "Message-ID"),
)
# Header fields prepended to the document text (retrieval-visible).
_TEXT_HEADER_FIELDS = (
    ("Subject", "email_subject"),
    ("From", "email_from"),
    ("To", "email_to"),
    ("Date", "email_date"),
)


class EmlReader(Reader):
    """RFC 822 / MIME email (.eml) file reader.

    Accepts a path string, ``Path``, or a file-like object (binary or
    text), and returns exactly one Document per message.

    Attributes:
        max_file_bytes: Maximum accepted message size in bytes; enforced
            before the content is fully read.
        max_parts: Maximum number of MIME parts traversed; guards against
            part-bomb style messages.
        include_headers_in_text: When True (default), a Subject/From/To/Date
            block is prepended to the document text so retrieval can match
            on it; metadata always carries the full sanitized headers.
    """

    max_file_bytes: int = _DEFAULT_MAX_FILE_BYTES
    max_parts: int = _DEFAULT_MAX_PARTS
    include_headers_in_text: bool = True

    def _load_data(self, file: str | Path | object, ext_info: dict | None = None) -> list[Document]:
        """Parse one .eml message into a single Document.

        Args:
            file: Path string, ``Path``, or file-like object of the message.
            ext_info: Extra metadata merged onto the produced Document.

        Returns:
            A one-element list with the parsed message Document.

        Raises:
            ValueError: If the input is missing, oversized, part-bomb-shaped,
                unreadable, or otherwise unparsable.
            TypeError: If ``file`` is neither a path nor a file-like object.
        """
        try:
            raw, file_name = self._read_bytes(file)
            message = email.message_from_bytes(raw, policy=email.policy.default)
            headers = self._extract_headers(message)
            body, attachment_names, attachment_count = self._walk_message(message)
            text = self._compose_text(headers, body)
            metadata: dict[str, object] = {"file_name": file_name}
            metadata.update(headers)
            metadata["attachment_count"] = attachment_count
            if attachment_names:
                metadata["attachment_names"] = attachment_names
            if ext_info:
                metadata.update(ext_info)
            return [Document(text=text, metadata=metadata)]
        except (ValueError, TypeError):
            raise
        except Exception as e:
            raise ValueError(f"Failed to read EML file: {e}") from e

    # ------------------------------------------------------------------ #
    # Input handling
    # ------------------------------------------------------------------ #
    def _read_bytes(self, file: str | Path | object) -> tuple[bytes, str]:
        """Read the raw message with the size bound enforced up front.

        Raises:
            ValueError: When the file is missing or exceeds max_file_bytes.
            TypeError: When ``file`` is not a path or file-like object.
        """
        if isinstance(file, str):
            file = Path(file)
        if isinstance(file, Path):
            if not file.exists():
                raise ValueError(f"EML file not found: {file}")
            size = file.stat().st_size
            if size > self.max_file_bytes:
                raise ValueError(
                    f"EML file {file.name} is {size} bytes, exceeding max_file_bytes={self.max_file_bytes}."
                )
            return file.read_bytes(), file.name
        if hasattr(file, "read"):
            with contextlib.suppress(AttributeError, OSError):
                file.seek(0)
            # Bounded read: never pull more than the cap into memory.
            raw = file.read(self.max_file_bytes + 1)
            if isinstance(raw, str):
                raw = raw.encode("utf-8", errors="replace")
            if not isinstance(raw, bytes | bytearray):
                raise TypeError("Unsupported file object type")
            if len(raw) > self.max_file_bytes:
                raise ValueError(f"EML content exceeds max_file_bytes={self.max_file_bytes}.")
            name_attr = getattr(file, "name", None)
            file_name = Path(name_attr).name if isinstance(name_attr, str) else "unknown"
            return bytes(raw), file_name
        raise TypeError("file must be a path string, Path, or file-like object")

    # ------------------------------------------------------------------ #
    # Parsing
    # ------------------------------------------------------------------ #
    def _extract_headers(self, message) -> dict[str, str]:
        """Copy the standard headers into metadata, sanitized and truncated.

        Values are whitespace-collapsed so a crafted header cannot inject
        newlines (or fake keys) into downstream metadata consumers.
        """
        headers: dict[str, str] = {}
        for meta_key, header_name in _HEADER_FIELDS:
            value = message.get(header_name)
            if value is None:
                continue
            text = " ".join(str(value).split())
            headers[meta_key] = text[:_MAX_HEADER_CHARS]
        return headers

    def _walk_message(self, message) -> tuple[str, list[str], int]:
        """Single capped walk collecting body text and attachment names.

        Returns:
            ``(body_text, attachment_names, attachment_count)`` where body
            text prefers text/plain parts and falls back to tag-stripped
            text/html. Attachment payloads are never decoded.

        Raises:
            ValueError: When the message has more than ``max_parts`` MIME
                parts (part-bomb guard).
        """
        plain_parts: list[str] = []
        html_parts: list[str] = []
        attachment_names: list[str] = []
        attachment_count = 0
        parts_seen = 0
        for part in message.walk():
            parts_seen += 1
            if parts_seen > self.max_parts:
                raise ValueError(f"EML has more than max_parts={self.max_parts} MIME parts; refusing to parse.")
            if part.is_multipart():
                continue
            disposition = (part.get_content_disposition() or "").lower()
            filename = part.get_filename()
            if disposition == "attachment" or (filename and disposition != "inline"):
                attachment_count += 1
                if filename and len(attachment_names) < _MAX_ATTACHMENT_NAMES:
                    attachment_names.append(" ".join(str(filename).split())[:_MAX_HEADER_CHARS])
                # Attachment payloads are never decoded: a malicious binary
                # must not reach any parser through this reader.
                continue
            content_type = part.get_content_type()
            if content_type not in ("text/plain", "text/html"):
                continue
            payload = self._decode_part(part)
            if not payload:
                continue
            (plain_parts if content_type == "text/plain" else html_parts).append(payload)
        if plain_parts:
            body = "\n\n".join(plain_parts)
        elif html_parts:
            body = self._html_to_text("\n\n".join(html_parts))
        else:
            body = ""
        return body.strip(), attachment_names, attachment_count

    def _decode_part(self, part) -> str:
        """Decode one text part, degrading to replacement chars on charset errors."""
        try:
            content = part.get_content()
            if isinstance(content, str):
                return content
        except Exception:
            pass
        try:
            payload = part.get_payload(decode=True)
        except Exception:
            return ""
        if not payload:
            return ""
        charset = part.get_content_charset() or "utf-8"
        try:
            return payload.decode(charset, errors="replace")
        except (LookupError, UnicodeDecodeError):
            return payload.decode("utf-8", errors="replace")

    @staticmethod
    def _html_to_text(html_text: str) -> str:
        """Strip tags, scripts and styles from an HTML body."""
        soup = BeautifulSoup(html_text, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return soup.get_text("\n", strip=True)

    def _compose_text(self, headers: dict[str, str], body: str) -> str:
        """Prepend the retrieval-visible header block to the body."""
        if not self.include_headers_in_text:
            return body
        lines = [f"{label}: {headers[key]}" for label, key in _TEXT_HEADER_FIELDS if headers.get(key)]
        if not lines:
            return body
        return ("\n".join(lines) + "\n\n" + body).strip()

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #
    def _validate_config(self) -> None:
        """Fail loudly on bounds that would disable the safety guards.

        Raises:
            TypeError: On non-integer bounds or a non-boolean flag.
            ValueError: On non-positive bounds.
        """
        for attr in ("max_file_bytes", "max_parts"):
            value = getattr(self, attr)
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{attr} must be an integer, got {value!r}.")
            if value < 1:
                raise ValueError(f"{attr} must be a positive integer, got {value!r}.")
        if not isinstance(self.include_headers_in_text, bool):
            raise TypeError(f"include_headers_in_text must be a boolean, got {self.include_headers_in_text!r}.")

    def _initialize_by_component_configer(self, reader_configer: ComponentConfiger) -> "EmlReader":
        """Initialize the reader from its component config."""
        super()._initialize_by_component_configer(reader_configer)
        for attr in ("max_file_bytes", "max_parts", "include_headers_in_text"):
            if hasattr(reader_configer, attr):
                setattr(self, attr, getattr(reader_configer, attr))
        # Validate eagerly so a misconfigured bound fails at component-load
        # time rather than silently disabling a safety guard at read time.
        self._validate_config()
        return self
