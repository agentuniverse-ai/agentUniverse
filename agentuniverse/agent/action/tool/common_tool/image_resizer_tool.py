#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: image_resizer_tool.py

"""
Image Resizer Tool — resize, scale, crop, convert, and inspect images.

A bounded image-manipulation utility for agent workflows. It wraps Pillow
(the ``PIL`` package) with strict path confinement, size budgets, format
allow-listing, and structured error reporting. Pillow is imported lazily so
that the tool can be imported and configured even when the dependency is not
installed — the ``ImportError`` is surfaced as a structured ``dependency_error``
only when an operation actually needs it.

Operations (``mode``):

- **resize** — produce an image of exactly ``width`` x ``height`` pixels.
  The default resampling filter is Lanczos (high quality).
- **scale** — multiply the existing dimensions by ``factor`` (e.g. 0.5 to
  halve each axis, 2.0 to double). The factor must be strictly positive.
- **crop** — extract a rectangular region defined by ``box`` (left, top,
  right, bottom). The box must lie within the source dimensions.
- **convert** — re-encode the image in another format (jpg/png/webp) with
  an optional quality setting for lossy formats.
- **info** — report the image's format, dimensions, and byte size without
  writing anything.

All file paths are confined to ``base_dir`` via ``resolve_safe_path``, so
traversal attempts (``../``) and absolute paths outside the base are
rejected. Input and output byte sizes are bounded by ``max_input_bytes``
and ``max_output_bytes``; output formats are restricted to
``allowed_formats``. Writes are atomic: the encoded image is written to a
same-directory temporary file and size-checked before replacing the target,
so a failed write never corrupts an existing file.

Addresses #252 (common utility tools).
"""

import os
import tempfile
from typing import Any, Optional, cast

from agentuniverse.agent.action.tool.common_tool.file_path_utils import \
    resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool

# Public execute() converts validation/dependency exceptions into structured
# tool responses instead of raising.
# ruff: noqa: TRY003

# Modes exposed by the tool. Kept as a tuple for fast membership testing.
_SUPPORTED_MODES = ("resize", "scale", "crop", "convert", "info")

# Output formats Pillow can encode that we allow by default. GIF/TIFF/BMP
# are deliberately omitted to keep the surface small; users may extend
# allowed_formats in config.
_DEFAULT_ALLOWED_FORMATS = ("jpg", "jpeg", "png", "webp")

# Map canonical output tokens to (Pillow format name, file extension).
# JPEG shares the "JPEG" format name across jpg/jpeg extensions.
_FORMAT_TABLE = {
    "jpg": ("JPEG", ".jpg"),
    "jpeg": ("JPEG", ".jpeg"),
    "png": ("PNG", ".png"),
    "webp": ("WEBP", ".webp"),
}

# Sensible defaults. Inputs/outputs are capped to protect the host from
# runaway payloads.
_DEFAULT_MAX_INPUT_BYTES = 25 * 1024 * 1024   # 25 MiB
_DEFAULT_MAX_OUTPUT_BYTES = 25 * 1024 * 1024  # 25 MiB
_MAX_DIMENSION = 20_000  # Pillow's own ceiling is near here; stay below it.
_MIN_FACTOR = 0.01
_MAX_FACTOR = 100.0
_DEFAULT_QUALITY = 85


class ImageResizerTool(Tool):
    """Resize, scale, crop, convert, and inspect image files with Pillow.

    Attributes:
        base_dir: Root directory that all paths are confined to.
        max_input_bytes: Maximum size of an input image file.
        max_output_bytes: Maximum size of a generated image file.
        allowed_formats: Output formats the tool is permitted to write
            (jpg, jpeg, png, webp by default).
    """

    name: str = "image_resizer_tool"
    description: Optional[str] = (
        "Resize, scale, crop, convert, and inspect images using Pillow. "
        "Paths are confined to base_dir; input/output sizes are bounded."
    )
    input_keys: Optional[list] = ["mode", "file_path"]

    base_dir: str = "."
    max_input_bytes: int = _DEFAULT_MAX_INPUT_BYTES
    max_output_bytes: int = _DEFAULT_MAX_OUTPUT_BYTES
    allowed_formats: tuple = _DEFAULT_ALLOWED_FORMATS

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def execute(
        self,
        mode: str,
        file_path: str,
        output_path: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        factor: Optional[float] = None,
        box: Optional[list] = None,
        target_format: Optional[str] = None,
        quality: int = _DEFAULT_QUALITY,
        overwrite: bool = False,
        **_: Any,
    ) -> dict:
        """Run an image operation.

        Returns a structured dict. Successful ``resize``/``scale``/``crop``/
        ``convert`` results carry ``output_path``, the new ``width`` and
        ``height``, ``format``, and ``file_size``; ``info`` carries the same
        metadata without writing a file. Errors carry ``error_type`` and
        ``error``.
        """
        try:
            self._validate_config()
            operation = self._normalize_mode(mode)
            source = self._resolve_input(file_path)
            self._check_input_size(source)
            image = self._open(source)
            if operation == "info":
                return self._info_result(source, image)
            if operation == "resize":
                return self._resize(image, source, output_path, width, height, overwrite, target_format, quality)
            if operation == "scale":
                return self._scale(image, source, output_path, factor, overwrite, target_format, quality)
            if operation == "crop":
                return self._crop(image, source, output_path, box, overwrite, target_format, quality)
            return self._convert(image, source, output_path, target_format, quality, overwrite)
        except ImportError as exc:
            return self._error(file_path, "dependency_error",
                               "Pillow (PIL) is required. Install with: pip install Pillow", str(exc))
        except (TypeError, ValueError) as exc:
            return self._error(file_path, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error(file_path, "operation_error", f"Image operation failed: {exc}")

    # ------------------------------------------------------------------
    # Configuration / validation helpers
    # ------------------------------------------------------------------
    def _validate_config(self) -> None:
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")
        for name in ("max_input_bytes", "max_output_bytes"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.allowed_formats, (list, tuple)) or not self.allowed_formats:
            raise ValueError("allowed_formats must be a non-empty list/tuple")
        for fmt in self.allowed_formats:
            if not isinstance(fmt, str) or fmt.lower() not in _FORMAT_TABLE:
                raise ValueError(f"allowed_formats contains unsupported format: {fmt!r}")

    @staticmethod
    def _normalize_mode(mode: Any) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        operation = mode.strip().lower()
        if operation not in _SUPPORTED_MODES:
            raise ValueError(
                "mode must be one of: " + ", ".join(_SUPPORTED_MODES)
            )
        return operation

    def _resolve_input(self, file_path: Any) -> str:
        if not isinstance(file_path, str) or not file_path:
            raise ValueError("file_path must be a non-empty string")
        path = cast(str, resolve_safe_path(file_path, self.base_dir))
        if not os.path.isfile(path):
            raise ValueError(f"file_path does not exist: {path}")
        return path

    def _resolve_output(self, output_path: Any) -> str:
        if not isinstance(output_path, str) or not output_path:
            raise ValueError("output_path must be a non-empty string")
        return cast(str, resolve_safe_path(output_path, self.base_dir))

    def _check_input_size(self, path: str) -> None:
        size = os.path.getsize(path)
        if size > self.max_input_bytes:
            raise ValueError(
                f"input file size ({size}) exceeds max_input_bytes ({self.max_input_bytes})"
            )

    # ------------------------------------------------------------------
    # Pillow helpers (lazy import)
    # ------------------------------------------------------------------
    @staticmethod
    def _pil():
        """Lazily import Pillow and return the Image module."""
        try:
            from PIL import Image  # type: ignore
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise ImportError("No module named 'PIL'") from exc
        return Image

    def _open(self, path: str) -> Any:
        Image = self._pil()
        try:
            image = Image.open(path)
            image.load()  # force read so truncated files fail here
        except Exception as exc:
            raise ValueError(f"Could not read image: {exc}") from exc
        # Guard against absurdly large dimensions.
        if image.width > _MAX_DIMENSION or image.height > _MAX_DIMENSION:
            raise ValueError(
                f"image dimensions ({image.width}x{image.height}) exceed "
                f"the maximum ({_MAX_DIMENSION})"
            )
        return image

    # ------------------------------------------------------------------
    # Output encoding (shared)
    # ------------------------------------------------------------------
    def _save(
        self,
        image: Any,
        destination: str,
        target_format: Optional[str],
        quality: int,
        overwrite: bool,
        source_path: str,
    ) -> dict:
        """Encode ``image`` to ``destination`` atomically and return metadata."""
        self._check_overwrite(destination, overwrite)
        pil_format, extension = self._resolve_format(destination, target_format)
        if pil_format.lower() not in {f.lower() for f in self.allowed_formats}:
            raise ValueError(
                f"target format {pil_format!r} is not in allowed_formats "
                f"({list(self.allowed_formats)})"
            )
        if not isinstance(quality, int) or not 1 <= quality <= 100:
            raise ValueError("quality must be an integer between 1 and 100")
        # Normalize modes that JPEG cannot store (JPEG has no alpha channel).
        out_image = self._normalize_for_format(image, pil_format)
        directory = os.path.dirname(destination) or "."
        os.makedirs(directory, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=".img-", suffix=extension, dir=directory, delete=False
            ) as handle:
                temporary = handle.name
                save_kwargs = self._save_kwargs(pil_format, quality)
                out_image.save(handle, format=pil_format, **save_kwargs)
            if os.path.getsize(temporary) > self.max_output_bytes:
                raise ValueError(
                    f"generated image exceeds max_output_bytes ({self.max_output_bytes})"
                )
            os.replace(temporary, destination)
            temporary = None
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
        return {
            "status": "success",
            "output_path": destination,
            "width": out_image.width,
            "height": out_image.height,
            "format": pil_format,
            "file_size": os.path.getsize(destination),
        }

    def _resolve_format(self, destination: str, target_format: Optional[str]) -> tuple:
        if target_format is not None:
            if not isinstance(target_format, str):
                raise TypeError("target_format must be a string")
            key = target_format.strip().lower()
            if key not in _FORMAT_TABLE:
                raise ValueError(
                    f"target_format {target_format!r} is not supported. "
                    f"Allowed: {', '.join(sorted(_FORMAT_TABLE))}"
                )
            return _FORMAT_TABLE[key]
        # Infer from extension.
        ext = os.path.splitext(destination)[1].lower().lstrip(".")
        if ext in _FORMAT_TABLE:
            return _FORMAT_TABLE[ext]
        raise ValueError(
            f"Cannot infer format from output extension {ext!r}; pass target_format explicitly"
        )

    @staticmethod
    def _normalize_for_format(image: Any, pil_format: str) -> Any:
        """Return a copy of ``image`` compatible with ``pil_format``."""
        if pil_format == "JPEG":
            # Flatten alpha onto white, drop palettes -> RGB.
            if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                background = image.convert("RGBA").convert("RGB")
                return background
            if image.mode != "RGB":
                return image.convert("RGB")
        return image

    @staticmethod
    def _save_kwargs(pil_format: str, quality: int) -> dict:
        if pil_format in ("JPEG", "WEBP"):
            return {"quality": quality}
        return {}

    @staticmethod
    def _check_overwrite(path: str, overwrite: bool) -> None:
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be a boolean")
        if os.path.exists(path) and not overwrite:
            raise ValueError(f"file exists: {path}; set overwrite=true")

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------
    def _resize(self, image, source, output_path, width, height, overwrite, target_format, quality):
        if width is None or height is None:
            raise ValueError("resize requires both width and height")
        if isinstance(width, bool) or not isinstance(width, int) or width <= 0:
            raise ValueError("width must be a positive integer")
        if isinstance(height, bool) or not isinstance(height, int) or height <= 0:
            raise ValueError("height must be a positive integer")
        if width > _MAX_DIMENSION or height > _MAX_DIMENSION:
            raise ValueError(f"width/height must not exceed {_MAX_DIMENSION}")
        Image = self._pil()
        resized = image.resize((width, height), Image.LANCZOS)
        destination = self._resolve_output(output_path)
        result = self._save(resized, destination, target_format, quality, overwrite, source)
        result["mode"] = "resize"
        return result

    def _scale(self, image, source, output_path, factor, overwrite, target_format, quality):
        if factor is None:
            raise ValueError("scale requires factor")
        if isinstance(factor, bool) or not isinstance(factor, (int, float)):
            raise TypeError("factor must be a number")
        factor = float(factor)
        if factor <= 0:
            raise ValueError("factor must be strictly positive")
        if not _MIN_FACTOR <= factor <= _MAX_FACTOR:
            raise ValueError(f"factor must be between {_MIN_FACTOR} and {_MAX_FACTOR}")
        new_width = max(1, round(image.width * factor))
        new_height = max(1, round(image.height * factor))
        Image = self._pil()
        scaled = image.resize((new_width, new_height), Image.LANCZOS)
        destination = self._resolve_output(output_path)
        result = self._save(scaled, destination, target_format, quality, overwrite, source)
        result["mode"] = "scale"
        result["factor"] = factor
        return result

    def _crop(self, image, source, output_path, box, overwrite, target_format, quality):
        if box is None:
            raise ValueError("crop requires box")
        if not isinstance(box, list) or len(box) != 4:
            raise ValueError("box must be a list of four integers [left, top, right, bottom]")
        for value in box:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("box coordinates must be integers")
        left, top, right, bottom = box
        if left < 0 or top < 0 or right > image.width or bottom > image.height:
            raise ValueError(
                f"box ({left},{top},{right},{bottom}) is outside the image bounds "
                f"({image.width}x{image.height})"
            )
        if right <= left or bottom <= top:
            raise ValueError("box right must exceed left and bottom must exceed top")
        cropped = image.crop((left, top, right, bottom))
        destination = self._resolve_output(output_path)
        result = self._save(cropped, destination, target_format, quality, overwrite, source)
        result["mode"] = "crop"
        return result

    def _convert(self, image, source, output_path, target_format, quality, overwrite):
        if target_format is None:
            raise ValueError("convert requires target_format")
        destination = self._resolve_output(output_path)
        result = self._save(image, destination, target_format, quality, overwrite, source)
        result["mode"] = "convert"
        return result

    def _info_result(self, path: str, image: Any) -> dict:
        return {
            "status": "success",
            "mode": "info",
            "file_path": path,
            "format": image.format,
            "width": image.width,
            "height": image.height,
            "mode_channel": image.mode,
            "file_size": os.path.getsize(path),
        }

    # ------------------------------------------------------------------
    # Error helper
    # ------------------------------------------------------------------
    @staticmethod
    def _error(path: Any, kind: str, message: str, detail: Optional[str] = None) -> dict:
        result: dict = {"status": "error", "error_type": kind, "error": message, "file_path": path}
        if detail:
            result["detail"] = detail
        return result
