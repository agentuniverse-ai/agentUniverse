"""Source-backed text extraction from bounded, local WARC snapshots."""

import gzip
import hashlib
import io
from copy import deepcopy
from email.message import Message
from pathlib import Path
from typing import ClassVar

from pydantic import StrictInt

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


def _sha(value):
    return hashlib.sha256(value).hexdigest()


def _one(headers, name, required=False):
    values = [value for key, value in headers.headers if key.lower() == name.lower()]
    if len(values) > 1 or (required and (not values or not values[0])):
        raise ValueError(f"Missing or repeated {name}")
    return values[0] if values else None


class WarcEvidenceReader(Reader):
    """Read archived HTTP text without fetching current URLs.

    A limited identical-payload revisit may resolve to a full response in the
    same archive, by exact Record-ID and matching verified digest only. Missing
    or unsupported records appear in the report, never invented text.
    """

    max_file_bytes: StrictInt = 32000000
    max_archive_bytes: StrictInt = 128000000
    max_records: StrictInt = 10000
    max_record_bytes: StrictInt = 8000000
    max_payload_bytes: StrictInt = 8000000
    max_text_chars: StrictInt = 2000000
    max_total_chars: StrictInt = 10000000

    _OPTIONS: ClassVar[tuple] = (
        "max_file_bytes",
        "max_archive_bytes",
        "max_records",
        "max_record_bytes",
        "max_payload_bytes",
        "max_text_chars",
        "max_total_chars",
    )
    _PROFILES: ClassVar[set] = {
        "http://netpreserve.org/warc/1.0/revisit/identical-payload-digest",
        "http://netpreserve.org/warc/1.1/revisit/identical-payload-digest",
    }

    def _settings(self):
        for key, maximum in zip(self._OPTIONS, (128000000, 256000000, 50000, 32000000, 32000000, 8000000, 40000000)):
            value = getattr(self, key)
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError(f"{key} must be an integer between 1 and {maximum}")

    def _initialize_by_component_configer(self, config):
        candidate = self.model_copy(deep=True)
        for key in self._OPTIONS:
            if key in config.configer.value:
                setattr(candidate, key, config.configer.value[key])
        candidate._settings()
        super()._initialize_by_component_configer(config)
        for key in self._OPTIONS:
            setattr(self, key, getattr(candidate, key))
        return self

    @staticmethod
    def _gunzip(raw, limit):
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            value = stream.read(limit + 1)
        if len(value) > limit:
            raise ValueError("Decompressed data exceeds configured byte limit")
        return value

    def _response_text(self, record, payload):
        from bs4 import BeautifulSoup
        from warcio.bufferedreaders import ChunkedDataReader

        headers = record.http_headers
        if headers is None:
            return None, {}, "missing_http_headers"
        status = headers.get_statuscode()
        if not status or not status.isdigit() or not 200 <= int(status) < 300:
            return None, {"http_status": status}, "non_success_http_status"
        if status == "206" or _one(headers, "Content-Range"):
            return None, {"http_status": status}, "partial_http_response"
        transfer = (_one(headers, "Transfer-Encoding") or "identity").strip().lower()
        encoding = (_one(headers, "Content-Encoding") or "identity").strip().lower()
        if transfer not in {"identity", "chunked"} or encoding not in {"identity", "gzip", "x-gzip"}:
            return None, {}, "unsupported_http_encoding"
        content_type = _one(headers, "Content-Type")
        if not content_type:
            return None, {}, "missing_content_type"
        mime = Message()
        mime["Content-Type"] = content_type
        # Message.get_content_type() defaults malformed values to text/plain.
        # Do not turn unknown archived bytes into inferred plain text.
        media = content_type.split(";", 1)[0].strip().lower()
        if media not in {"text/plain", "text/html", "application/xhtml+xml"}:
            return None, {"media_type": media}, "unsupported_media_type"
        content_length = _one(headers, "Content-Length")
        if transfer == "identity" and content_length is not None:
            if not content_length.isdecimal() or int(content_length) != len(payload):
                raise ValueError("Archived HTTP Content-Length does not match the stored body")
        if transfer == "chunked":
            # Strict mode: never fall back to best-guess unchunked data.
            stream = io.BytesIO(payload)
            decoder = ChunkedDataReader(stream, raise_exceptions=True)
            payload = decoder.read(self.max_payload_bytes + 1)
            if not decoder.all_chunks_read or stream.tell() != len(stream.getvalue()):
                raise ValueError("Incomplete chunked body or unsupported trailers")
        if encoding != "identity":
            payload = self._gunzip(payload, self.max_payload_bytes)
        if len(payload) > self.max_payload_bytes:
            raise ValueError("Response exceeds max_payload_bytes")
        charset = mime.get_content_charset() or "utf-8"
        try:
            text = payload.decode(charset, errors="strict")
        except (LookupError, UnicodeError, TypeError) as error:
            raise ValueError("Archived text does not decode with its declared/default charset") from error
        representation = "plain_text"
        if media != "text/plain":
            soup = BeautifulSoup(text, "html.parser")
            for element in soup(["script", "style", "template"]):
                element.decompose()
            text = soup.get_text("\n", strip=True)
            representation = "html_derived_text"
        if len(text) > self.max_text_chars:
            raise ValueError("Response exceeds max_text_chars")
        return (
            text,
            {
                "http_status": status,
                "media_type": media,
                "charset": charset,
                "charset_source": "http_header" if mime.get_content_charset() else "utf8_default",
                "representation": representation,
                "decoded_payload_sha256": _sha(payload),
            },
            None,
        )

    def load_archive(self, file, ext_info=None):
        """Return Documents and a report; malformed input fails without partial return.

        Supports local .warc / .warc.gz, WARC 1.0/1.1 HTTP text responses.
        Selected metadata omits cookies and arbitrary HTTP/request headers.
        """
        self._settings()
        if ext_info is not None and not isinstance(ext_info, dict):
            raise ValueError("ext_info must be a dictionary")
        if ext_info and "warc_evidence" in ext_info:
            raise ValueError("warc_evidence is reserved source metadata")
        path = Path(file).resolve()
        if not (path.name.lower().endswith(".warc") or path.name.lower().endswith(".warc.gz")):
            raise ValueError("Expected a local .warc or .warc.gz archive")
        with path.open("rb") as stream:
            raw = stream.read(self.max_file_bytes + 1)
        if len(raw) > self.max_file_bytes:
            raise ValueError("Archive exceeds max_file_bytes")
        archive_sha = _sha(raw)
        expanded = self._gunzip(raw, self.max_archive_bytes) if raw.startswith(b"\x1f\x8b") else raw
        if len(expanded) > self.max_archive_bytes:
            raise ValueError("Archive exceeds max_archive_bytes")
        if not expanded.startswith((b"WARC/1.0\r\n", b"WARC/1.1\r\n")):
            raise ValueError("Only WARC 1.0/1.1 archives are supported")
        try:
            from warcio.archiveiterator import ArchiveIterator
        except ImportError as error:
            raise ImportError("WarcEvidenceReader requires agentUniverse[warc_ext]") from error
        entries, ids, extracted_chars = [], set(), 0
        next_offset = 0
        iterator = ArchiveIterator(io.BytesIO(expanded), verify_http=True, check_digests="raise")
        try:
            for index, record in enumerate(iterator):
                if index >= self.max_records:
                    raise ValueError("Archive exceeds max_records")
                headers = record.rec_headers
                if record.format != "warc" or headers.protocol not in {"WARC/1.0", "WARC/1.1"}:
                    raise ValueError("Mixed/unsupported archive format")
                length = _one(headers, "Content-Length", required=True)
                if not length.isdecimal() or int(length) > self.max_record_bytes:
                    raise ValueError("Invalid Content-Length or max_record_bytes exceeded")
                identifier = _one(headers, "WARC-Record-ID", required=True)
                if identifier in ids:
                    raise ValueError("Duplicate WARC-Record-ID; cannot resolve source unambiguously")
                ids.add(identifier)
                payload = record.raw_stream.read(self.max_record_bytes + 1)
                expected = record.payload_length if record.payload_length >= 0 else int(length)
                if len(payload) != expected:
                    raise ValueError("Truncated WARC record body")
                offset = iterator.get_record_offset()
                record_length = iterator.get_record_length()
                boundary = offset + record_length
                if offset != next_offset or expanded[boundary : boundary + 4] != b"\r\n\r\n":
                    raise ValueError("Invalid WARC record separator")
                next_offset = boundary + 4
                info = {
                    "uncompressed_record_offset": offset,
                    "uncompressed_record_length": record_length,
                    "archive_sha256": archive_sha,
                    "file_path": str(path),
                    "record_index": index,
                    "record_id": identifier,
                    "record_type": _one(headers, "WARC-Type", required=True),
                    "capture_date": _one(headers, "WARC-Date", required=True),
                    "target_uri": _one(headers, "WARC-Target-URI"),
                    "payload_digest": _one(headers, "WARC-Payload-Digest"),
                    "block_digest": _one(headers, "WARC-Block-Digest"),
                    "digest_verification": "passed" if record.digest_checker.passed is True else "not_available",
                    "stored_payload_sha256": _sha(payload),
                    "refers_to": _one(headers, "WARC-Refers-To"),
                    "revisit_profile": _one(headers, "WARC-Profile"),
                    "refers_to_target_uri": _one(headers, "WARC-Refers-To-Target-URI"),
                    "refers_to_date": _one(headers, "WARC-Refers-To-Date"),
                }
                text, reason = None, None
                if (
                    _one(headers, "WARC-Truncated")
                    or _one(headers, "WARC-Segment-Number")
                    or record.rec_type == "continuation"
                ):
                    reason = "truncated_or_segmented_record"
                elif record.rec_type == "response":
                    text, detail, reason = self._response_text(record, payload)
                    info.update(detail)
                    if text is not None:
                        extracted_chars += len(text)
                        if extracted_chars > self.max_total_chars:
                            raise ValueError("Archive extraction exceeds max_total_chars")
                        info["payload_source_record_id"] = identifier
                elif record.rec_type != "revisit":
                    reason = "unsupported_record_type"
                elif payload:
                    reason = "revisit_has_unexpected_payload"
                entries.append({"text": text, "info": info, "reason": reason})
            if iterator.err_count or next_offset != len(expanded):
                raise ValueError("Invalid WARC record boundary")
        finally:
            iterator.close()
        full_responses = {
            entry["info"]["record_id"]: entry
            for entry in entries
            if entry["info"]["record_type"] == "response" and entry["text"] is not None
        }
        for entry in entries:
            info = entry["info"]
            if info["record_type"] != "revisit" or entry["reason"]:
                continue
            if info["revisit_profile"] not in self._PROFILES:
                entry["reason"] = "unsupported_revisit_profile"
                continue
            source = full_responses.get(info["refers_to"])
            if source is None:
                entry["reason"] = "revisit_source_unavailable"
                continue
            source_info = source["info"]
            if (
                not info["payload_digest"]
                or info["payload_digest"] != source_info["payload_digest"]
                or source_info["digest_verification"] != "passed"
            ):
                entry["reason"] = "revisit_digest_not_verified"
                continue
            if (info["refers_to_target_uri"] and info["refers_to_target_uri"] != source_info["target_uri"]) or (
                info["refers_to_date"] and info["refers_to_date"] != source_info["capture_date"]
            ):
                entry["reason"] = "revisit_reference_disagrees"
                continue
            entry["text"] = source["text"]
            info["payload_source_record_id"] = source_info["record_id"]
            info["payload_source_capture_date"] = source_info["capture_date"]
            info["revisit_resolution"] = "exact_record_id_and_verified_digest"
            for key in ("decoded_payload_sha256", "media_type", "charset", "charset_source", "representation"):
                info[key] = source_info[key]
        documents, omitted, total = [], [], 0
        for entry in entries:
            info, text = entry["info"], entry["text"]
            if text is None:
                omitted.append(
                    {"record_id": info["record_id"], "record_index": info["record_index"], "reason": entry["reason"]}
                )
                continue
            total += len(text)
            if total > self.max_total_chars:
                raise ValueError("Archive extraction exceeds max_total_chars; no partial result returned")
            info["text_sha256"] = _sha(text.encode("utf-8"))
            metadata = deepcopy(ext_info) if ext_info else {}
            metadata["warc_evidence"] = deepcopy(info)
            identifier = _sha((archive_sha + ":" + info["record_id"]).encode("utf-8"))
            documents.append(Document(id=identifier, text=text, metadata=metadata))
        return documents, {
            "record_count": len(entries),
            "document_count": len(documents),
            "archive_sha256": archive_sha,
            "omitted_records": omitted,
        }

    def _load_data(self, file, ext_info=None):
        return self.load_archive(file, ext_info)[0]
