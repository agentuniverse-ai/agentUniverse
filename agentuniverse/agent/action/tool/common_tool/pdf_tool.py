#!/usr/bin/env python3
"""Bounded PDF manipulation tool."""

import os
import tempfile
from typing import Any, cast

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool

# Public execute() converts validation exceptions to structured tool responses.
# ruff: noqa: TRY003


class PDFTool(Tool):
    """Merge, split, rotate, extract, and inspect PDF files."""

    base_dir: str = "."
    max_read_bytes: int = 50 * 1024 * 1024
    max_write_bytes: int = 50 * 1024 * 1024
    max_pages: int = 1_000
    max_text_chars: int = 100_000
    max_input_files: int = 100

    def execute(
        self,
        mode: str,
        file_path: str,
        input_paths: list[str] | None = None,
        output_path: str | None = None,
        output_dir: str | None = None,
        pages: list[int] | None = None,
        rotation: int = 90,
        overwrite: bool = False,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            path = self._pdf_path(file_path, "file_path")
            if operation == "merge":
                return self._merge(path, input_paths, overwrite, metadata)
            if operation == "split":
                return self._split(path, output_dir, pages, overwrite)
            if operation == "rotate":
                return self._rotate(path, output_path, pages, rotation, overwrite)
            if operation == "extract":
                return self._extract(path, pages)
            return self._info(path)
        except ImportError as exc:
            return self._error(
                file_path, "dependency_error", "pypdf is required. Install with: pip install pypdf", str(exc)
            )
        except (TypeError, ValueError) as exc:
            return self._error(file_path, "validation_error", str(exc))
        except Exception as exc:
            return self._error(file_path, "operation_error", f"PDF operation failed: {exc}")

    @staticmethod
    def _error(path: Any, kind: str, message: str, detail: str | None = None) -> dict[str, Any]:
        result = {"status": "error", "error_type": kind, "error": message, "file_path": path}
        if detail:
            result["detail"] = detail
        return result

    def _validate_config(self) -> None:
        for name in ("max_read_bytes", "max_write_bytes", "max_pages", "max_text_chars", "max_input_files"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")

    @staticmethod
    def _mode(mode: str) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")
        operation = mode.strip().lower()
        if operation not in {"merge", "split", "rotate", "extract", "info"}:
            raise ValueError("mode must be merge, split, rotate, extract, or info")
        return operation

    def _pdf_path(self, value: str, field: str) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError(f"{field} must be a non-empty string")
        if os.path.splitext(value)[1].lower() != ".pdf":
            raise ValueError(f"{field} must have a .pdf extension")
        return cast(str, resolve_safe_path(value, self.base_dir))

    def _directory(self, value: str) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError("output_dir must be a non-empty string")
        return cast(str, resolve_safe_path(value, self.base_dir))

    def _check_file(self, path: str, field: str = "file_path") -> None:
        if not os.path.isfile(path):
            raise ValueError(f"{field} does not exist: {path}")
        if os.path.getsize(path) > self.max_read_bytes:
            raise ValueError(f"{field} exceeds max_read_bytes ({self.max_read_bytes})")
        with open(path, "rb") as stream:
            if stream.read(5) != b"%PDF-":
                raise ValueError(f"{field} is not a PDF file")

    @staticmethod
    def _classes() -> tuple[Any, Any]:
        try:
            from pypdf import PdfReader, PdfWriter
        except ImportError as exc:
            raise ImportError("No module named 'pypdf'") from exc
        return PdfReader, PdfWriter

    def _reader(self, path: str) -> Any:
        self._check_file(path)
        Reader, _ = self._classes()
        reader = Reader(path)
        if reader.is_encrypted:
            raise ValueError("encrypted PDFs are not supported")
        if len(reader.pages) > self.max_pages:
            raise ValueError(f"PDF exceeds max_pages ({self.max_pages})")
        return reader

    def _page_indexes(self, pages: Any, count: int) -> list[int]:
        if pages is None:
            return list(range(count))
        if not isinstance(pages, list) or not pages:
            raise ValueError("pages must be a non-empty list of 1-based page numbers")
        indexes = []
        for page in pages:
            if isinstance(page, bool) or not isinstance(page, int) or not 1 <= page <= count:
                raise ValueError(f"page numbers must be between 1 and {count}")
            if page - 1 not in indexes:
                indexes.append(page - 1)
        return indexes

    def _metadata(self, value: Any) -> dict[str, str]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise TypeError("metadata must be an object")
        result = {}
        for key, item in value.items():
            if not isinstance(key, str) or not isinstance(item, str) or len(item) > 2_000:
                raise ValueError("metadata keys and values must be bounded strings")
            result[key if key.startswith("/") else f"/{key}"] = item
        return result

    def _merge(self, output: str, inputs: Any, overwrite: bool, metadata: Any) -> dict[str, Any]:
        if not isinstance(inputs, list) or not inputs:
            raise ValueError("input_paths must be a non-empty list")
        if len(inputs) > self.max_input_files:
            raise ValueError(f"input_paths exceed max_input_files ({self.max_input_files})")
        self._check_overwrite(output, overwrite)
        _, Writer = self._classes()
        writer = Writer()
        total = 0
        safe_inputs = []
        for index, value in enumerate(inputs):
            path = self._pdf_path(value, f"input_paths[{index}]")
            reader = self._reader(path)
            safe_inputs.append(path)
            total += len(reader.pages)
            if total > self.max_pages:
                raise ValueError(f"merged PDF exceeds max_pages ({self.max_pages})")
            for page in reader.pages:
                writer.add_page(page)
        properties = self._metadata(metadata)
        if properties:
            writer.add_metadata(properties)
        self._save(writer, output)
        return {
            "status": "success",
            "mode": "merge",
            "file_path": output,
            "input_paths": safe_inputs,
            "page_count": total,
            "file_size": os.path.getsize(output),
        }

    def _split(self, source: str, output_dir: Any, pages: Any, overwrite: bool) -> dict[str, Any]:
        reader = self._reader(source)
        indexes = self._page_indexes(pages, len(reader.pages))
        directory = self._directory(output_dir)
        _, Writer = self._classes()
        os.makedirs(directory, exist_ok=True)
        stem = os.path.splitext(os.path.basename(source))[0]
        outputs = []
        for index in indexes:
            destination = os.path.join(directory, f"{stem}-page-{index + 1}.pdf")
            self._check_overwrite(destination, overwrite)
            writer = Writer()
            writer.add_page(reader.pages[index])
            self._save(writer, destination)
            outputs.append(destination)
        return {
            "status": "success",
            "mode": "split",
            "file_path": source,
            "output_paths": outputs,
            "page_count": len(outputs),
        }

    def _rotate(self, source: str, output: Any, pages: Any, rotation: Any, overwrite: bool) -> dict[str, Any]:
        if isinstance(rotation, bool) or not isinstance(rotation, int) or rotation not in {90, 180, 270}:
            raise ValueError("rotation must be 90, 180, or 270")
        destination = self._pdf_path(output, "output_path")
        self._check_overwrite(destination, overwrite)
        reader = self._reader(source)
        indexes = set(self._page_indexes(pages, len(reader.pages)))
        _, Writer = self._classes()
        writer = Writer()
        for index, page in enumerate(reader.pages):
            if index in indexes:
                page.rotate(rotation)
            writer.add_page(page)
        self._save(writer, destination)
        return {
            "status": "success",
            "mode": "rotate",
            "file_path": source,
            "output_path": destination,
            "rotated_pages": [i + 1 for i in sorted(indexes)],
            "rotation": rotation,
        }

    def _extract(self, source: str, pages: Any) -> dict[str, Any]:
        reader = self._reader(source)
        indexes = self._page_indexes(pages, len(reader.pages))
        remaining = self.max_text_chars
        truncated = False
        output = []
        for index in indexes:
            text = (reader.pages[index].extract_text() or "").strip()
            if len(text) > remaining:
                text = (text[: max(0, remaining - 1)] + "…") if remaining else ""
                remaining = 0
                truncated = True
            else:
                remaining -= len(text)
            output.append({"page": index + 1, "text": text})
        return {
            "status": "success",
            "mode": "extract",
            "file_path": source,
            "pages": output,
            "truncated": truncated,
            "max_text_chars": self.max_text_chars,
        }

    def _info(self, source: str) -> dict[str, Any]:
        reader = self._reader(source)
        return {
            "status": "success",
            "mode": "info",
            "file_path": source,
            "file_size": os.path.getsize(source),
            "page_count": len(reader.pages),
            "metadata": {str(key): str(value) for key, value in (reader.metadata or {}).items()},
        }

    @staticmethod
    def _check_overwrite(path: str, overwrite: bool) -> None:
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be a boolean")
        if os.path.exists(path) and not overwrite:
            raise ValueError(f"file exists: {path}; set overwrite=true")

    def _save(self, writer: Any, destination: str) -> None:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=".pdf-", suffix=".pdf", dir=os.path.dirname(destination), delete=False
            ) as output:
                temporary = output.name
                writer.write(output)
            if os.path.getsize(temporary) > self.max_write_bytes:
                raise ValueError("generated PDF exceeds max_write_bytes")
            os.replace(temporary, destination)
            temporary = None
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
