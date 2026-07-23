#!/usr/bin/env python3

"""Bounded QR code generation and decoding tool."""

# Validation failures are converted to structured tool responses at the public
# execute boundary, so bespoke exception subclasses would add no useful signal.
# ruff: noqa: TRY003, TRY004

import base64
import os
import tempfile
from typing import Any, ClassVar, cast

from agentuniverse.agent.action.tool.common_tool.file_path_utils import (
    resolve_safe_path,
)
from agentuniverse.agent.action.tool.tool import Tool


class QRCodeTool(Tool):
    """Generate and decode QR codes within ``base_dir``.

    ``qrcode`` and ``Pillow`` are loaded lazily so importing this tool never
    fails on environments without the optional imaging stack. Every file path
    is confined to ``base_dir`` (including resolved symlinks) and writes use a
    temporary file followed by ``os.replace`` so a failed save cannot corrupt
    an existing image.

    Supported modes:

    * ``generate`` — encode text into a PNG (or another Pillow format) file.
    * ``decode`` — read a QR code from an existing image file.
    * ``generate_base64`` — encode text and return the image as a base64 string.
    """

    base_dir: str = "."
    max_input_chars: int = 2_000
    default_size: int = 10
    default_border: int = 4
    error_correction: str = "M"
    box_size_min: int = 1
    box_size_max: int = 100
    border_min: int = 0
    border_max: int = 20
    max_read_bytes: int = 20 * 1024 * 1024
    max_write_bytes: int = 20 * 1024 * 1024

    _ERROR_LEVELS: ClassVar[dict[str, str]] = {
        "L": "ERROR_CORRECT_L",
        "M": "ERROR_CORRECT_M",
        "Q": "ERROR_CORRECT_Q",
        "H": "ERROR_CORRECT_H",
    }
    _IMAGE_EXTENSIONS: ClassVar[set[str]] = {
        ".png",
        ".bmp",
        ".gif",
        ".tiff",
        ".tif",
        ".jpeg",
        ".jpg",
    }

    def execute(
        self,
        mode: str,
        data: str | None = None,
        file_path: str | None = None,
        box_size: int | None = None,
        border: int | None = None,
        size: int | None = None,
        error_correction: str | None = None,
        output_format: str | None = None,
        overwrite: bool = False,
        fill_color: str = "black",
        back_color: str = "white",
    ) -> dict[str, Any]:
        """Run a QR code operation.

        Args:
            mode: One of ``generate``, ``decode``, or ``generate_base64``.
            data: Text to encode. Required for the generate modes.
            file_path: Image path underneath ``base_dir``. Required for
                ``generate`` (destination) and ``decode`` (source).
            box_size: Pixels per QR module. Defaults to ``default_size``.
            border: Quiet-zone width in modules. Defaults to ``default_border``.
            size: Alias for ``box_size`` kept for convenience.
            error_correction: Error correction level (L/M/Q/H).
            output_format: Pillow image format for ``generate_base64``
                (e.g. ``PNG``). Defaults to ``PNG``.
            overwrite: Allow ``generate`` to replace an existing image.
            fill_color: Foreground (module) color.
            back_color: Background color.

        Returns:
            A structured success or error dictionary.
        """
        try:
            self._validate_configuration()
            normalized_mode = self._normalize_mode(mode)

            if normalized_mode == "generate":
                if file_path is None:
                    raise ValueError("file_path is required for generate mode")
                return self._generate(
                    data,
                    file_path,
                    box_size,
                    border,
                    size,
                    error_correction,
                    overwrite,
                    fill_color,
                    back_color,
                )
            if normalized_mode == "decode":
                if file_path is None:
                    raise ValueError("file_path is required for decode mode")
                return self._decode(file_path)
            return self._generate_base64(
                data,
                box_size,
                border,
                size,
                error_correction,
                output_format,
                fill_color,
                back_color,
            )
        except ImportError as exc:
            message = str(exc)
            if "pyzbar" in message or "decoding requires" in message:
                hint = (
                    "QR code decoding requires the optional pyzbar package and "
                    "the zbar native library. Install with: pip install pyzbar"
                )
            else:
                hint = (
                    "qrcode and Pillow are required for QR code operations. "
                    "Install them with: pip install qrcode[pil]"
                )
            return self._error(
                file_path,
                "dependency_error",
                hint,
                detail=message,
            )
        except (TypeError, ValueError) as exc:
            return self._error(file_path, "validation_error", str(exc))
        except Exception as exc:  # library-specific parse/write failures
            return self._error(
                file_path,
                "operation_error",
                f"QR code operation failed: {exc}",
            )

    # ------------------------------------------------------------------ public

    @staticmethod
    def _error(path: Any, kind: str, message: str, detail: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": "error",
            "error_type": kind,
            "error": message,
        }
        if detail:
            payload["detail"] = detail
        if path is not None:
            payload["file_path"] = path
        return payload

    def _validate_configuration(self) -> None:
        for name in ("max_input_chars", "max_read_bytes", "max_write_bytes"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        for name in ("box_size_min", "box_size_max", "border_min", "border_max"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.box_size_min > self.box_size_max:
            raise ValueError("box_size_min cannot exceed box_size_max")
        if self.border_min > self.border_max:
            raise ValueError("border_min cannot exceed border_max")
        for name in ("default_size", "default_border"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")
        if self.error_correction not in self._ERROR_LEVELS:
            allowed = ", ".join(sorted(self._ERROR_LEVELS))
            raise ValueError(
                f"error_correction must be one of {allowed}, got {self.error_correction!r}"
            )
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")

    @staticmethod
    def _normalize_mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in {"generate", "decode", "generate_base64"}:
            raise ValueError("mode must be generate, decode, or generate_base64")
        return mode

    def _resolve_image_path(self, file_path: str) -> str:
        if not isinstance(file_path, str) or not file_path:
            raise ValueError("file_path must be a non-empty string")
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self._IMAGE_EXTENSIONS:
            raise ValueError(
                "file_path must end with a supported image extension "
                f"({', '.join(sorted(self._IMAGE_EXTENSIONS))})"
            )
        return cast(str, resolve_safe_path(file_path, self.base_dir))

    # ------------------------------------------------------------ generation

    def _build_qr(
        self,
        data: Any,
        box_size: int | None,
        border: int | None,
        size: int | None,
        error_correction: str | None,
    ) -> Any:
        if not isinstance(data, str):
            raise TypeError("data must be a string")
        if not data:
            raise ValueError("data must be a non-empty string")
        if len(data) > self.max_input_chars:
            raise ValueError(
                f"data length ({len(data)}) exceeds max_input_chars "
                f"({self.max_input_chars})"
            )

        resolved_box = self._resolve_box_size(box_size, size)
        resolved_border = self._resolve_border(border)
        resolved_correction = self._resolve_correction(error_correction)

        qrcode = self._load_qrcode()
        constants = self._load_qrcode_constants()
        correction_constant = getattr(constants, self._ERROR_LEVELS[resolved_correction])
        qr = qrcode.QRCode(
            version=None,
            error_correction=correction_constant,
            box_size=resolved_box,
            border=resolved_border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr

    def _resolve_box_size(self, box_size: int | None, size: int | None) -> int:
        candidate = box_size if box_size is not None else size
        if candidate is None:
            candidate = self.default_size
        if isinstance(candidate, bool) or not isinstance(candidate, int):
            raise TypeError("box_size must be an integer")
        if candidate < self.box_size_min or candidate > self.box_size_max:
            raise ValueError(
                f"box_size must be between {self.box_size_min} and {self.box_size_max}"
            )
        return candidate

    def _resolve_border(self, border: int | None) -> int:
        if border is None:
            border = self.default_border
        if isinstance(border, bool) or not isinstance(border, int):
            raise TypeError("border must be an integer")
        if border < self.border_min or border > self.border_max:
            raise ValueError(
                f"border must be between {self.border_min} and {self.border_max}"
            )
        return border

    def _resolve_correction(self, error_correction: str | None) -> str:
        if error_correction is None:
            error_correction = self.error_correction
        if not isinstance(error_correction, str):
            raise TypeError("error_correction must be a string")
        normalized = error_correction.strip().upper()
        if normalized not in self._ERROR_LEVELS:
            allowed = ", ".join(sorted(self._ERROR_LEVELS))
            raise ValueError(
                f"error_correction must be one of {allowed}, got {error_correction!r}"
            )
        return normalized

    def _generate(
        self,
        data: str | None,
        file_path: str,
        box_size: int | None,
        border: int | None,
        size: int | None,
        error_correction: str | None,
        overwrite: bool,
        fill_color: str,
        back_color: str,
    ) -> dict[str, Any]:
        qr = self._build_qr(data, box_size, border, size, error_correction)
        destination = self._resolve_image_path(file_path)
        if os.path.exists(destination) and not overwrite:
            raise ValueError(
                f"file_path already exists: {destination} (set overwrite=true to replace)"
            )
        image = self._render_image(qr, fill_color, back_color)
        self._atomic_save(image, destination)
        return {
            "status": "success",
            "file_path": destination,
            "data_length": len(data) if isinstance(data, str) else 0,
            "box_size": qr.box_size,
            "border": qr.border,
            "error_correction": self._correction_label(qr.error_correction),
        }

    def _generate_base64(
        self,
        data: str | None,
        box_size: int | None,
        border: int | None,
        size: int | None,
        error_correction: str | None,
        output_format: str | None,
        fill_color: str,
        back_color: str,
    ) -> dict[str, Any]:
        qr = self._build_qr(data, box_size, border, size, error_correction)
        image = self._render_image(qr, fill_color, back_color)
        image_format = self._normalize_image_format(output_format)
        encoded = self._encode_image(image, image_format)
        if len(encoded) > self.max_write_bytes:
            raise ValueError(
                f"encoded image length ({len(encoded)}) exceeds max_write_bytes "
                f"({self.max_write_bytes})"
            )
        return {
            "status": "success",
            "image_base64": encoded,
            "image_format": image_format,
            "data_length": len(data) if isinstance(data, str) else 0,
            "box_size": qr.box_size,
            "border": qr.border,
            "error_correction": self._correction_label(qr.error_correction),
        }

    # --------------------------------------------------------------- decoding

    def _decode(self, file_path: str) -> dict[str, Any]:
        source = self._resolve_image_path(file_path)
        if not os.path.isfile(source):
            raise ValueError(f"file_path does not exist: {source}")
        if os.path.getsize(source) > self.max_read_bytes:
            raise ValueError(
                f"file_path exceeds max_read_bytes ({self.max_read_bytes})"
            )
        texts = self._read_qr(source)
        if not texts:
            return {
                "status": "success",
                "file_path": source,
                "decoded": [],
                "text": None,
                "found": False,
            }
        return {
            "status": "success",
            "file_path": source,
            "decoded": texts,
            "text": texts[0],
            "found": True,
        }

    # ------------------------------------------------------------- dependency

    def _load_qrcode(self):
        try:
            import qrcode  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised via patch
            raise ImportError("qrcode library is not installed") from exc
        return qrcode

    def _load_qrcode_constants(self):
        return self._load_qrcode().constants

    def _load_image(self):
        try:
            from PIL import Image  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised via patch
            raise ImportError("Pillow is not installed") from exc
        return Image

    def _render_image(self, qr: Any, fill_color: str, back_color: str) -> Any:
        if not isinstance(fill_color, str) or not fill_color:
            raise ValueError("fill_color must be a non-empty string")
        if not isinstance(back_color, str) or not back_color:
            raise ValueError("back_color must be a non-empty string")
        return qr.make_image(fill_color=fill_color, back_color=back_color)

    @staticmethod
    def _normalize_image_format(output_format: str | None) -> str:
        if output_format is None or output_format == "":
            return "PNG"
        if not isinstance(output_format, str):
            raise TypeError("output_format must be a string")
        normalized = output_format.strip().upper()
        if not normalized:
            return "PNG"
        if normalized == "JPG":
            return "JPEG"
        return normalized

    def _encode_image(self, image: Any, image_format: str) -> str:
        Image = self._load_image()
        buffer = self._io_bytes()
        image.save(buffer, format=image_format)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        if not encoded:
            raise ValueError("failed to encode image to base64")
        return encoded

    def _read_qr(self, source: str) -> list[str]:
        try:
            from pyzbar import pyzbar  # type: ignore[import-not-found]
        except ImportError:
            return self._read_qr_pillow(source)
        image = self._load_image().open(source)
        try:
            decoded = pyzbar.decode(image)
        finally:
            try:
                image.close()
            except Exception:  # pragma: no cover - defensive close
                pass
        texts: list[str] = []
        for item in decoded:
            value = item.data.decode("utf-8", errors="replace") if item.data else ""
            if value:
                texts.append(value)
        return texts

    def _read_qr_pillow(self, source: str) -> list[str]:
        # Pillow alone cannot decode QR codes, but the qrcode library cannot
        # decode images either. Surface a helpful error so callers install the
        # optional decoder instead of silently receiving an empty result.
        raise ImportError(
            "decoding requires the pyzbar package (pip install pyzbar) and the "
            "zbar native library"
        )

    @staticmethod
    def _io_bytes():
        import io

        return io.BytesIO()

    def _atomic_save(self, image: Any, destination: str) -> None:
        directory = os.path.dirname(destination) or "."
        os.makedirs(directory, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=".qrcode-",
            suffix=os.path.splitext(destination)[1] or ".png",
            dir=directory,
        )
        os.close(fd)
        try:
            image.save(temp_name)
            if os.path.getsize(temp_name) > self.max_write_bytes:
                raise ValueError(
                    f"generated image exceeds max_write_bytes ({self.max_write_bytes})"
                )
            os.replace(temp_name, destination)
        except BaseException:
            if os.path.exists(temp_name):
                try:
                    os.remove(temp_name)
                except OSError:  # pragma: no cover - best-effort cleanup
                    pass
            raise

    @staticmethod
    def _correction_label(constant: int) -> str:
        # qrcode exposes the correction levels as module-level integers.
        try:
            from qrcode.constants import (  # type: ignore[import-not-found]
                ERROR_CORRECT_H,
                ERROR_CORRECT_L,
                ERROR_CORRECT_M,
                ERROR_CORRECT_Q,
            )
        except ImportError:  # pragma: no cover - exercised via patch
            return "M"
        mapping = {
            ERROR_CORRECT_L: "L",
            ERROR_CORRECT_M: "M",
            ERROR_CORRECT_Q: "Q",
            ERROR_CORRECT_H: "H",
        }
        return mapping.get(constant, "M")
