"""Read an explicit S3 object manifest through registered local file Readers."""

import hashlib
import json
import re
import tempfile
from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any, ClassVar

from pydantic import Field, PrivateAttr, StrictBool, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.agent.action.knowledge.store.document import Document


class S3ImportError(RuntimeError):
    """An import has failures; inspect the sanitized per-object report."""

    def __init__(self, report):
        super().__init__("S3 import incomplete; inspect error.report before ingesting any partial result")
        self.report = report


class S3VersionReader(Reader):
    """Capture per-object versions, then read without silently following newer data.

    A manifest is not an atomic bucket snapshot. The caller owns the client and
    delegated Reader configuration; neither is supplied by remote object content.
    """

    bucket: StrictStr = ""
    source_name: StrictStr = "aws-s3"
    readers: dict[str, str] = Field(default_factory=dict)
    client_args: dict = Field(default_factory=dict, repr=False, exclude=True)
    allow_unversioned: StrictBool = False
    page_size: StrictInt = 100
    max_objects: StrictInt = 1000
    max_pages: StrictInt = 1000
    max_object_bytes: StrictInt = 10000000
    max_total_bytes: StrictInt = 100000000
    max_manifest_bytes: StrictInt = 1000000
    max_documents: StrictInt = 10000
    max_output_chars: StrictInt = 10000000
    timeout_seconds: StrictInt = 30

    _client: Any = PrivateAttr(default=None)
    _OPTIONS: ClassVar[tuple] = (
        "bucket",
        "source_name",
        "readers",
        "client_args",
        "allow_unversioned",
        "page_size",
        "max_objects",
        "max_pages",
        "max_object_bytes",
        "max_total_bytes",
        "max_manifest_bytes",
        "max_documents",
        "max_output_chars",
        "timeout_seconds",
    )

    def _validate(self):
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]", self.bucket):
            raise ValueError("configure an ordinary S3 bucket name; access point/directory buckets are unsupported")
        if not self.source_name or len(self.source_name) > 128:
            raise ValueError("source_name must be a nonempty namespace of at most 128 characters")
        if not self.readers or any(
            not re.fullmatch(r"[a-z0-9]{1,16}", key) or not value for key, value in self.readers.items()
        ):
            raise ValueError("readers must map lowercase file suffixes to registered Reader names")
        if type(self.allow_unversioned) is not bool:
            raise ValueError("allow_unversioned must be Boolean")
        for key, upper in (
            ("page_size", 1000),
            ("max_objects", 100000),
            ("max_pages", 100000),
            ("max_object_bytes", 1000000000),
            ("max_total_bytes", 10000000000),
            ("max_manifest_bytes", 100000000),
            ("max_documents", 1000000),
            ("max_output_chars", 1000000000),
            ("timeout_seconds", 300),
        ):
            value = getattr(self, key)
            if type(value) is not int or not 1 <= value <= upper:
                raise ValueError(key + " must be a positive bounded integer")
        if "config" in self.client_args or "service_name" in self.client_args:
            raise ValueError("client_args must not override service_name/config")

    def _initialize_by_component_configer(self, config):
        candidate = S3VersionReader(
            **{key: deepcopy(getattr(config, key, getattr(self, key))) for key in self._OPTIONS}
        )
        candidate._validate()
        for key in self._OPTIONS:
            setattr(self, key, getattr(candidate, key))
        return super()._initialize_by_component_configer(config)

    def _get_client(self):
        self._validate()
        if self._client is None:
            try:
                import boto3
                from botocore.config import Config
            except ImportError as error:
                raise ImportError("Install agentuniverse[s3_reader_ext]") from error
            self._client = boto3.client(
                "s3",
                config=Config(
                    connect_timeout=self.timeout_seconds,
                    read_timeout=self.timeout_seconds,
                    retries={"total_max_attempts": 1},
                    s3={"addressing_style": "path"},
                ),
                **self.client_args,
            )
        return self._client

    def close(self):
        if self._client is not None:
            self._client.close()
            self._client = None

    def create_copy(self):
        copied = self.model_copy()
        for key in self._OPTIONS:
            setattr(copied, key, deepcopy(getattr(self, key)))
        copied._client = None
        return copied

    @staticmethod
    def _json_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def _manifest(self, manifest):
        self._validate()
        if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "source_name", "bucket", "objects"}:
            raise ValueError("manifest requires schema_version, source_name, bucket and objects only")
        if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
            raise ValueError("unsupported manifest schema version")
        if manifest["bucket"] != self.bucket or manifest["source_name"] != self.source_name:
            raise ValueError("manifest source must match the configured bucket/namespace")
        objects = manifest["objects"]
        if not isinstance(objects, list) or len(objects) > self.max_objects:
            raise ValueError("manifest object count exceeds limit")
        seen, total = set(), 0
        for obj in objects:
            if (
                not isinstance(obj, dict)
                or not {"key", "version_id", "etag", "size"} <= set(obj)
                or set(obj) - {"key", "version_id", "etag", "size", "sha256"}
            ):
                raise ValueError("invalid manifest object fields")
            key = obj["key"]
            if not isinstance(key, str) or not key or len(key.encode("utf-8")) > 1024 or key in seen:
                raise ValueError("object keys must be nonempty, unique and at most 1024 UTF-8 bytes")
            seen.add(key)
            version = obj["version_id"]
            if version is not None and (not isinstance(version, str) or not version or len(version) > 1024):
                raise ValueError("invalid version ID")
            if version in (None, "null") and not self.allow_unversioned:
                raise ValueError("immutable version ID required; explicitly opt into conditional unversioned reads")
            if not isinstance(obj["etag"], str) or not re.fullmatch(r'"[^"\r\n]{1,1024}"', obj["etag"]):
                raise ValueError("a quoted opaque ETag is required")
            if type(obj["size"]) is not int or not 0 <= obj["size"] <= self.max_object_bytes:
                raise ValueError("object size exceeds limit")
            total += obj["size"]
            if "sha256" in obj and (
                not isinstance(obj["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", obj["sha256"])
            ):
                raise ValueError("invalid sha256")
        if (
            total > self.max_total_bytes
            or len(json.dumps(manifest, allow_nan=False).encode()) > self.max_manifest_bytes
        ):
            raise ValueError("manifest byte budget exceeded")
        return deepcopy(manifest)

    def capture_prefix(self, prefix: str):
        """List current keys, HEAD each, and return a reusable explicit manifest.

        New/deleted keys during traversal are not a bucket-wide consistent view.
        Any listing/HEAD failure raises; never return a silently truncated manifest.
        """
        self._validate()
        if not isinstance(prefix, str) or len(prefix.encode()) > 1024:
            raise ValueError("prefix must be a string of at most 1024 UTF-8 bytes")
        client, objects, token, seen_tokens, seen_keys = self._get_client(), [], None, set(), set()
        total = 0
        for _ in range(self.max_pages):
            args = {"Bucket": self.bucket, "Prefix": prefix, "MaxKeys": self.page_size}
            if token is not None:
                args["ContinuationToken"] = token
            page = client.list_objects_v2(**args)
            for listed in page.get("Contents", []):
                key = listed["Key"]
                if not key.startswith(prefix) or key in seen_keys:
                    raise ValueError("listing contains duplicate or out-of-prefix keys")
                seen_keys.add(key)
                if len(seen_keys) > self.max_objects:
                    raise ValueError("prefix exceeds max_objects; narrow the prefix")
                head = client.head_object(Bucket=self.bucket, Key=key)
                obj = {
                    "key": key,
                    "version_id": head.get("VersionId"),
                    "etag": head["ETag"],
                    "size": head["ContentLength"],
                }
                # Validate each object immediately, not after an unbounded listing.
                self._manifest(
                    {"schema_version": 1, "source_name": self.source_name, "bucket": self.bucket, "objects": [obj]}
                )
                objects.append(obj)
                total += obj["size"]
                if total > self.max_total_bytes:
                    raise ValueError("prefix exceeds max_total_bytes")
            if not page.get("IsTruncated", False):
                return self._manifest(
                    {
                        "schema_version": 1,
                        "source_name": self.source_name,
                        "bucket": self.bucket,
                        "objects": sorted(objects, key=lambda obj: obj["key"]),
                    }
                )
            token = page.get("NextContinuationToken")
            if not isinstance(token, str) or not token or token in seen_tokens:
                raise ValueError("invalid or repeated pagination token")
            seen_tokens.add(token)
        raise ValueError("listing exceeds max_pages; no partial manifest returned")

    def _download(self, obj, target):
        args = {"Bucket": self.bucket, "Key": obj["key"], "IfMatch": obj["etag"]}
        if obj["version_id"] is not None:
            args["VersionId"] = obj["version_id"]
        response = self._get_client().get_object(**args)
        body = response["Body"]
        try:
            # Compatible services may omit the null-version response header.
            expected_version = None if obj["version_id"] == "null" else obj["version_id"]
            actual_version = response.get("VersionId")
            actual_version = None if actual_version == "null" else actual_version
            if (
                response.get("DeleteMarker")
                or response.get("ETag") != obj["etag"]
                or response.get("ContentLength") != obj["size"]
                or actual_version != expected_version
            ):
                raise ValueError("response no longer matches the captured object identity")
            digest, count = hashlib.sha256(), 0
            with target.open("wb") as output:
                while True:
                    chunk = body.read(min(65536, obj["size"] - count + 1))
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > obj["size"]:
                        raise ValueError("object stream exceeds captured size")
                    digest.update(chunk)
                    output.write(chunk)
            if count != obj["size"]:
                raise ValueError("object stream shorter than captured size")
            checksum = digest.hexdigest()
            if "sha256" in obj and obj["sha256"] != checksum:
                raise ValueError("object checksum mismatch")
            return checksum
        finally:
            body.close()

    def read_manifest_with_report(self, manifest, ext_info=None):
        """Explicit partial-result API. Public load_data instead fails on any error."""
        manifest = self._manifest(manifest)
        metadata = deepcopy({} if ext_info is None else ext_info)
        if not isinstance(metadata, dict) or "s3_source" in metadata:
            raise ValueError("ext_info must be a mapping without reserved s3_source")
        documents, entries, chars = [], [], 0
        for obj in manifest["objects"]:
            stage = "reader_lookup"
            try:
                suffix = PurePosixPath(obj["key"]).suffix.lower().lstrip(".")
                reader_name = self.readers.get(suffix)
                if reader_name is None:
                    raise ValueError("object suffix has no configured Reader")
                reader = ReaderManager().get_instance_obj(reader_name)
                if reader is None or isinstance(reader, S3VersionReader):
                    raise ValueError("local delegate Reader is absent or recursively refers to S3")
                with tempfile.TemporaryDirectory(prefix="au-s3-") as folder:
                    target = Path(folder) / ("object." + suffix)
                    stage = "download"
                    checksum = self._download(obj, target)
                    stage = "parse"
                    parsed = reader.load_data(target)
                stage = "output_validation"
                if not isinstance(parsed, list) or any(not isinstance(doc, Document) for doc in parsed):
                    raise ValueError("delegate must return a list of Documents")
                count = sum(len(doc.text or "") for doc in parsed)
                if len(documents) + len(parsed) > self.max_documents or chars + count > self.max_output_chars:
                    raise ValueError("parsed output exceeds configured document/text limits")
                provenance = {
                    "source_name": self.source_name,
                    "bucket": self.bucket,
                    **obj,
                    "sha256": checksum,
                    "reader": reader_name,
                    "identity_mode": "version" if obj["version_id"] not in (None, "null") else "conditional-etag",
                }
                pending = []
                for index, original in enumerate(parsed):
                    doc = deepcopy(original)
                    identity = json.dumps([provenance, index, doc.text], sort_keys=True, ensure_ascii=False)
                    doc.id = hashlib.sha256(identity.encode()).hexdigest()
                    doc.metadata = {
                        **(doc.metadata or {}),
                        **deepcopy(metadata),
                        "file_name": obj["key"],
                        "s3_source": deepcopy(provenance),
                    }
                    pending.append(doc)
                documents.extend(pending)
                chars += count
                entries.append({"key": obj["key"], "status": "read", "documents": len(pending), "sha256": checksum})
            except Exception as error:
                # Error messages can contain request headers, URLs or credentials.
                # Retain only the class and a service error code when available.
                detail = {"key": obj["key"], "status": "failed", "stage": stage, "error_type": type(error).__name__}
                response = getattr(error, "response", None)
                if isinstance(response, dict):
                    code = response.get("Error", {}).get("Code")
                    if isinstance(code, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", code):
                        detail["service_code"] = code
                entries.append(detail)
        report = {
            "schema_version": 1,
            "source_name": self.source_name,
            "bucket": self.bucket,
            "complete": all(entry["status"] == "read" for entry in entries),
            "objects": entries,
        }
        return documents, report

    def _load_data(self, fpath: Path, ext_info=None):
        self._validate()
        with Path(fpath).open("rb") as source:
            raw = source.read(self.max_manifest_bytes + 1)
        if len(raw) > self.max_manifest_bytes:
            raise ValueError("manifest exceeds byte limit")
        manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=self._json_pairs)
        try:
            documents, report = self.read_manifest_with_report(manifest, ext_info)
        finally:
            self.close()
        if not report["complete"]:
            raise S3ImportError(report)
        return documents
