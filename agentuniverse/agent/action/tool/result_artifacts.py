"""Opt-in local artifact references for large text/JSON Tool results."""

import base64
import hashlib
import json
import os
import re
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool


def _serialize(value):
    if isinstance(value, str):
        return value.encode("utf-8"), "text/plain; charset=utf-8"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        if json.loads(text) != value:
            raise ValueError("artifact JSON must round-trip without coercion")
        return text.encode("utf-8"), "application/json"
    raise ValueError("artifact results must be text, JSON objects or arrays")


class ArtifactExpiredError(ValueError):
    """The stored artifact exists but its retention deadline has passed."""


class LocalToolArtifactStore:
    """Bounded local artifacts in an explicitly chosen private directory.

    No encryption or multi-tenant authorization is provided. Use a directory owned
    by the application/session; do not expose this store to unrelated principals.
    Expired artifacts are unreadable but remain on disk until explicitly removed.
    """

    def __init__(self, directory, *, max_bytes=16_777_216, max_page_chars=4096, ttl_seconds=3600):
        for limit in (max_bytes, max_page_chars, ttl_seconds):
            if type(limit) is not int or limit <= 0:
                raise ValueError("limits must be positive integers")
        self.root = Path(directory).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.max_bytes, self.max_page_chars, self.ttl_seconds = max_bytes, max_page_chars, ttl_seconds

    def _path(self, artifact_id):
        if not isinstance(artifact_id, str) or re.fullmatch(r"[0-9a-f]{32}", artifact_id) is None:
            raise ValueError("invalid artifact ID")
        path = self.root / f"{artifact_id}.json"
        if path.is_symlink():
            raise ValueError("artifact symlinks are not supported")
        return path

    def put(self, value):
        """Persist a complete result atomically and return a content-free reference.

        Raises ValueError for unsupported/oversize results, OSError on write or
        publication failures. Temporary files are cleaned on ordinary failures.
        """
        data, media_type = _serialize(value)
        if len(data) > self.max_bytes:
            raise ValueError("artifact byte limit exceeded")
        artifact_id = uuid.uuid4().hex
        descriptor = dict(
            kind="tool_artifact",
            version=1,
            id=artifact_id,
            sha256=hashlib.sha256(data).hexdigest(),
            bytes=len(data),
            media_type=media_type,
            expires_at=int(time.time()) + self.ttl_seconds,
            summary=f"Complete tool result stored ({len(data)} bytes); read pages by artifact ID.",
        )
        envelope = dict(reference=descriptor, payload=base64.b64encode(data).decode("ascii"))
        encoded = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode("utf-8")
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=self.root, prefix=".artifact-", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            # Never overwrite, even if an ID collision is forced.
            os.link(temporary, self._path(artifact_id))
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return descriptor

    def read_page(self, artifact_id, *, offset=0, limit=4096, expected_sha256=None):
        """Read at most limit Unicode characters after validating the full payload.

        JSON pages are fragments of canonical JSON text, not independently parsed
        objects. Concatenate pages before json.loads. Offsets count characters,
        not bytes. Missing, expired, corrupt and out-of-range reads fail explicitly.
        """
        if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= self.max_page_chars:
            raise ValueError("invalid page bounds")
        with self._path(artifact_id).open("rb") as stream:
            raw = stream.read(self.max_bytes * 2 + 4097)
        if len(raw) > self.max_bytes * 2 + 4096:
            raise ValueError("artifact envelope byte limit exceeded")
        try:
            envelope = json.loads(raw)
            if not isinstance(envelope, dict) or set(envelope) != {"reference", "payload"}:
                raise ValueError("invalid artifact envelope")
            descriptor = envelope["reference"]
            if not isinstance(descriptor, dict) or set(descriptor) != {
                "kind",
                "version",
                "id",
                "sha256",
                "bytes",
                "media_type",
                "expires_at",
                "summary",
            }:
                raise ValueError("invalid artifact reference")
            if (
                descriptor["id"] != artifact_id
                or descriptor["kind"] != "tool_artifact"
                or type(descriptor["version"]) is not int
                or descriptor["version"] != 1
            ):
                raise ValueError("artifact identity/version mismatch")
            if type(descriptor["expires_at"]) is not int or type(descriptor["bytes"]) is not int:
                raise ValueError("invalid artifact reference fields")
            if descriptor["media_type"] not in ("text/plain; charset=utf-8", "application/json"):
                raise ValueError("unsupported artifact media type")
            if time.time() >= descriptor["expires_at"]:
                raise ArtifactExpiredError("artifact expired")
            data = base64.b64decode(envelope["payload"], validate=True)
            digest = hashlib.sha256(data).hexdigest()
            if len(data) > self.max_bytes or len(data) != descriptor["bytes"] or digest != descriptor["sha256"]:
                raise ValueError("artifact size/digest mismatch")
            if expected_sha256 is not None and digest != expected_sha256:
                raise ValueError("artifact reference digest mismatch")
            text = data.decode("utf-8")
        except (KeyError, TypeError, UnicodeError) as exc:
            raise ValueError("invalid artifact") from exc
        if offset > len(text):
            raise ValueError("offset beyond artifact end")
        end = min(offset + limit, len(text))
        return dict(
            id=artifact_id,
            sha256=digest,
            media_type=descriptor["media_type"],
            text=text[offset:end],
            offset=offset,
            next_offset=end if end < len(text) else None,
            complete=end == len(text),
            total_chars=len(text),
        )

    def remove(self, artifact_id):
        """Explicitly remove one artifact; no automatic retention scan occurs."""
        self._path(artifact_id).unlink()


class ArtifactResultTool(Tool):
    """Wrap a selected Tool; persistence is disabled until enabled=True.

    Configure programmatically with a target Tool and private artifact store. Both
    sync/async paths call the target's public run method before considering spill.
    Failures propagate; incomplete results are never stored or silently truncated.
    """

    name: str = "artifact_result_tool"
    description: str = "Run a selected tool and optionally store oversized complete results"
    target: Tool
    artifact_store: Any
    enabled: bool = False
    threshold_bytes: int = Field(default=65_536, gt=0, strict=True)

    def _finish(self, result):
        if not self.enabled or not isinstance(result, (str, dict, list)):
            return result
        data, _ = _serialize(result)
        if len(data) <= self.threshold_bytes:
            return result
        return self.artifact_store.put(result)

    def execute(self, **kwargs):
        return self._finish(self.target.run(**kwargs))

    async def async_execute(self, **kwargs):
        return self._finish(await self.target.async_run(**kwargs))


class ArtifactReadTool(Tool):
    """Expose bounded pages from the same explicit store to a planner."""

    name: str = "artifact_read_tool"
    description: str = "Read a page of a tool artifact by ID, offset and character limit"
    artifact_store: Any
    input_keys: list = ["artifact_id"]

    def execute(self, artifact_id, offset=0, limit=4096, expected_sha256=None):
        return self.artifact_store.read_page(artifact_id, offset=offset, limit=limit, expected_sha256=expected_sha256)
