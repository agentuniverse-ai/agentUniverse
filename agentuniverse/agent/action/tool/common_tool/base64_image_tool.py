#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Base64 image encoder/decoder tool backed on the Python standard library.

The tool encodes image files to base64 (with an optional ``data:`` URI prefix),
decodes base64 data back to image files, and reports metadata about a base64
image (format, dimensions, size). All file access is sandboxed under
``base_dir`` via :func:`resolve_safe_path`. Pillow (``PIL``) is loaded lazily
and only required for the ``info`` operation's dimension reporting.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import base64
import mimetypes
import os
import tempfile
from typing import Any, ClassVar, Dict, Optional

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.logging.logging_util import LOGGER

# Image extensions accepted by encode/decode plus their mime types.
IMAGE_EXTENSIONS: ClassVar[tuple[str, ...]] = (
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".ico", ".svg",
)
# Map common image MIME types (mimetypes does not know all of them by default).
EXTRA_MIME: ClassVar[Dict[str, str]] = {
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
}

MAX_READ_BYTES: ClassVar[int] = 25 * 1024 * 1024   # 25 MB
MAX_WRITE_BYTES: ClassVar[int] = 50 * 1024 * 1024   # 50 MB
DATA_URI_PREFIX: ClassVar[str] = "data:"


def _lazy_pil():
    """Import Pillow lazily; raise a helpful error if it is unavailable."""
    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:  # pragma: no cover - exercised when Pillow missing
        raise ImportError(
            "Pillow is required for base64 image info. "
            "Install it with `pip install Pillow`."
        ) from exc
    return Image


class Base64ImageTool(Tool):
    """Encode, decode and inspect images using base64.

    Modes:

    * ``encode`` - read an image file under ``base_dir`` and return base64.
    * ``decode`` - write base64 payload to an image file under ``base_dir``.
    * ``info``   - report format/dimensions/size for a base64 image.

    All paths are resolved with :func:`resolve_safe_path` so they cannot
    escape ``base_dir``. Pillow is only required for ``info``.
    """

    description: str = (
        "Encode image files to base64 (optionally as data URIs), decode "
        "base64 back to image files, and inspect base64 image metadata. "
        "All paths are sandboxed under base_dir."
    )

    base_dir: str = "."
    max_read_bytes: int = MAX_READ_BYTES
    max_write_bytes: int = MAX_WRITE_BYTES

    def execute(
        self,
        mode: str,
        file_path: Optional[str] = None,
        data: Optional[str] = None,
        output_path: Optional[str] = None,
        as_data_uri: bool = False,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Run the requested operation and return a structured result."""
        try:
            self._validate_config()
            operation = self._mode(mode)
            if operation == "encode":
                return self._encode(file_path, as_data_uri)
            if operation == "decode":
                return self._decode(data, output_path, overwrite)
            return self._info(data)
        except (TypeError, ValueError) as exc:
            LOGGER.error(f"Base64ImageTool validation error: {exc}")
            return self._error("validation_error", str(exc))
        except Exception as exc:
            LOGGER.error(f"Base64ImageTool operation failed: {exc}")
            return self._error("operation_error", f"Image operation failed: {exc}")

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _error(kind: str, message: str) -> Dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message}

    def _validate_config(self) -> None:
        for name in ("max_read_bytes", "max_write_bytes"):
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
        if mode not in {"encode", "decode", "info"}:
            raise ValueError("mode must be encode, decode, or info")
        return mode

    def _image_path(self, value: Any) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError("file_path must be a non-empty string")
        ext = os.path.splitext(value)[1].lower()
        if ext not in IMAGE_EXTENSIONS:
            raise ValueError(
                f"file_path must be an image ({', '.join(IMAGE_EXTENSIONS)})"
            )
        return str(resolve_safe_path(value, self.base_dir))

    def _output_path(self, value: Any) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError("output_path must be a non-empty string")
        ext = os.path.splitext(value)[1].lower()
        if ext not in IMAGE_EXTENSIONS:
            raise ValueError(
                f"output_path must be an image ({', '.join(IMAGE_EXTENSIONS)})"
            )
        return str(resolve_safe_path(value, self.base_dir))

    @staticmethod
    def _mime_for(path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext in EXTRA_MIME:
            return EXTRA_MIME[ext]
        guessed = mimetypes.guess_type(path)[0]
        return guessed or "application/octet-stream"

    # ----------------------------------------------------------------- encode
    def _encode(self, file_path: Any, as_data_uri: Any) -> Dict[str, Any]:
        if not isinstance(as_data_uri, bool):
            raise TypeError("as_data_uri must be a boolean")
        path = self._image_path(file_path)
        if not os.path.isfile(path):
            raise ValueError(f"file_path does not exist: {path}")
        size = os.path.getsize(path)
        if size > self.max_read_bytes:
            raise ValueError(f"file_path exceeds max_read_bytes ({self.max_read_bytes})")
        with open(path, "rb") as stream:
            raw = stream.read()
        encoded = base64.b64encode(raw).decode("ascii")
        mime = self._mime_for(path)
        data_uri = f"{DATA_URI_PREFIX}{mime};base64,{encoded}" if as_data_uri else None
        return {
            "status": "success",
            "mode": "encode",
            "file_path": path,
            "base64": encoded,
            "data_uri": data_uri,
            "mime_type": mime,
            "size": size,
        }

    # ----------------------------------------------------------------- decode
    def _decode(self, data: Any, output_path: Any, overwrite: Any) -> Dict[str, Any]:
        if not isinstance(data, str) or not data.strip():
            raise ValueError("data must be a non-empty base64 string")
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be a boolean")
        destination = self._output_path(output_path)
        payload = self._strip_data_uri(data)
        try:
            raw = base64.b64decode(payload, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise ValueError(f"data is not valid base64: {exc}") from exc
        if not raw:
            raise ValueError("decoded payload is empty")
        if len(raw) > self.max_write_bytes:
            raise ValueError(f"decoded payload exceeds max_write_bytes ({self.max_write_bytes})")
        if os.path.exists(destination) and not overwrite:
            raise ValueError(f"file exists: {destination}; set overwrite=true")
        self._atomic_write(destination, raw)
        mime = self._mime_for(destination)
        return {
            "status": "success",
            "mode": "decode",
            "output_path": destination,
            "size": len(raw),
            "mime_type": mime,
        }

    @staticmethod
    def _strip_data_uri(data: str) -> str:
        """Return the base64 portion, dropping an optional ``data:`` prefix."""
        stripped = data.strip()
        if stripped.startswith(DATA_URI_PREFIX):
            # Format: data:<mime>;base64,<payload>  or  data:<mime>,<payload>
            comma = stripped.find(",")
            if comma == -1:
                raise ValueError("data URI is missing the comma separator")
            return stripped[comma + 1:]
        return stripped

    # -------------------------------------------------------------------- info
    def _info(self, data: Any) -> Dict[str, Any]:
        if not isinstance(data, str) or not data.strip():
            raise ValueError("data must be a non-empty base64 string")
        payload = self._strip_data_uri(data)
        try:
            raw = base64.b64decode(payload, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise ValueError(f"data is not valid base64: {exc}") from exc
        info: Dict[str, Any] = {
            "status": "success",
            "mode": "info",
            "size": len(raw),
            "format": None,
            "width": None,
            "height": None,
        }
        # Pillow is optional; degrade gracefully when it is unavailable.
        try:
            image = _lazy_pil()
        except ImportError as exc:
            info["note"] = str(exc)
            return info
        with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name
        try:
            with image.open(tmp_path) as img:
                info["format"] = img.format.lower() if img.format else None
                info["width"], info["height"] = img.size
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        return info

    @staticmethod
    def _atomic_write(destination: str, content: bytes) -> None:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=".img-", dir=os.path.dirname(destination), delete=False
            ) as output:
                temporary = output.name
                output.write(content)
            os.replace(temporary, destination)
            temporary = None
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
