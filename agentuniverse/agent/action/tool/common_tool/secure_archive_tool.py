#!/usr/bin/env python3
"""Bounded ZIP and TAR archive operations for agents."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import os
import shutil
import stat
import tarfile
import tempfile
import zipfile
from pathlib import PurePosixPath
from typing import Any, ClassVar, cast

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool


class SecureArchiveTool(Tool):
    """Create, list, inspect, and safely extract ZIP/TAR archives."""

    base_dir: str = "."
    max_read_bytes: int = 100 * 1024 * 1024
    max_write_bytes: int = 100 * 1024 * 1024
    max_entries: int = 5_000
    max_member_bytes: int = 100 * 1024 * 1024
    max_uncompressed_bytes: int = 500 * 1024 * 1024
    max_compression_ratio: float = 200.0
    max_input_files: int = 1_000

    _FORMATS: ClassVar[tuple[str, ...]] = (".zip", ".tar", ".tar.gz", ".tgz")

    def execute(
        self,
        mode: str,
        file_path: str,
        input_paths: list[str] | None = None,
        output_dir: str | None = None,
        members: list[str] | None = None,
        overwrite: bool = False,
        compression: str = "deflated",
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            archive = self._archive_path(file_path)
            if operation == "create":
                return self._create(archive, input_paths, overwrite, compression)
            self._check_archive_file(archive)
            entries = self._entries(archive)
            if operation == "list":
                return self._list(archive, entries)
            if operation == "info":
                return self._info(archive, entries)
            return self._extract(archive, entries, output_dir, members, overwrite)
        except (TypeError, ValueError) as exc:
            return self._error(file_path, "validation_error", str(exc))
        except Exception as exc:
            return self._error(file_path, "operation_error", f"Archive operation failed: {exc}")

    @staticmethod
    def _error(path: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "file_path": path}

    def _validate_config(self) -> None:
        for name in (
            "max_read_bytes",
            "max_write_bytes",
            "max_entries",
            "max_member_bytes",
            "max_uncompressed_bytes",
            "max_input_files",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if (
            isinstance(self.max_compression_ratio, bool)
            or not isinstance(self.max_compression_ratio, (int, float))
            or self.max_compression_ratio <= 0
        ):
            raise ValueError("max_compression_ratio must be positive")
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in {"create", "list", "extract", "info"}:
            raise ValueError("mode must be create, list, extract, or info")
        return mode

    def _archive_path(self, value: Any) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError("file_path must be a non-empty string")
        if not value.lower().endswith(self._FORMATS):
            raise ValueError("file_path must end with .zip, .tar, .tar.gz, or .tgz")
        return cast(str, resolve_safe_path(value, self.base_dir))

    def _directory(self, value: Any) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError("output_dir must be a non-empty string")
        return cast(str, resolve_safe_path(value, self.base_dir))

    def _check_archive_file(self, path: str) -> None:
        if not os.path.isfile(path):
            raise ValueError(f"file_path does not exist: {path}")
        if os.path.getsize(path) > self.max_read_bytes:
            raise ValueError(f"archive exceeds max_read_bytes ({self.max_read_bytes})")

    @staticmethod
    def _kind(path: str) -> str:
        return "zip" if path.lower().endswith(".zip") else "tar"

    @staticmethod
    def _safe_member_name(raw: str) -> str:
        if not isinstance(raw, str) or not raw or "\x00" in raw:
            raise ValueError("archive contains an invalid member name")
        normalized = raw.replace("\\", "/")
        path = PurePosixPath(normalized)
        if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            raise ValueError(f"unsafe archive member path: {raw}")
        if path.parts and path.parts[0].endswith(":"):
            raise ValueError(f"unsafe archive member path: {raw}")
        return path.as_posix().rstrip("/")

    def _entries(self, path: str) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        if self._kind(path) == "zip":
            try:
                with zipfile.ZipFile(path) as archive:
                    for item in archive.infolist():
                        mode = item.external_attr >> 16
                        if stat.S_ISLNK(mode):
                            raise ValueError(f"archive symlink is not supported: {item.filename}")
                        if item.flag_bits & 0x1:
                            raise ValueError("encrypted archives are not supported")
                        entries.append(
                            {
                                "name": self._safe_member_name(item.filename),
                                "size": item.file_size,
                                "compressed_size": item.compress_size,
                                "is_dir": item.is_dir(),
                            }
                        )
            except zipfile.BadZipFile as exc:
                raise ValueError("file_path is not a valid ZIP archive") from exc
        else:
            try:
                with tarfile.open(path, mode="r:*") as archive:
                    for item in archive.getmembers():
                        if not (item.isfile() or item.isdir()):
                            raise ValueError(f"archive links and special files are not supported: {item.name}")
                        entries.append(
                            {
                                "name": self._safe_member_name(item.name),
                                "size": item.size,
                                "compressed_size": None,
                                "is_dir": item.isdir(),
                            }
                        )
            except tarfile.TarError as exc:
                raise ValueError("file_path is not a valid TAR archive") from exc
        self._validate_entries(entries, os.path.getsize(path))
        return entries

    def _validate_entries(self, entries: list[dict[str, Any]], archive_size: int) -> None:
        if len(entries) > self.max_entries:
            raise ValueError(f"archive exceeds max_entries ({self.max_entries})")
        names: set[str] = set()
        total = 0
        for entry in entries:
            if entry["name"] in names:
                raise ValueError(f"archive contains duplicate member: {entry['name']}")
            names.add(entry["name"])
            if entry["size"] > self.max_member_bytes:
                raise ValueError(f"archive member exceeds max_member_bytes: {entry['name']}")
            total += entry["size"]
            compressed = entry["compressed_size"]
            if not entry["is_dir"] and compressed is not None:
                ratio = entry["size"] / max(compressed, 1)
                if ratio > self.max_compression_ratio:
                    raise ValueError(f"archive member exceeds max_compression_ratio: {entry['name']}")
        if total > self.max_uncompressed_bytes:
            raise ValueError(f"archive exceeds max_uncompressed_bytes ({self.max_uncompressed_bytes})")
        if total and total / max(archive_size, 1) > self.max_compression_ratio:
            raise ValueError("archive exceeds max_compression_ratio")

    def _collect_inputs(self, values: Any, archive_path: str) -> list[tuple[str, str]]:  # noqa: C901
        if not isinstance(values, list) or not values:
            raise ValueError("input_paths must be a non-empty list")
        base = os.path.realpath(os.path.abspath(self.base_dir))
        files: list[tuple[str, str]] = []
        seen: set[str] = set()
        for index, value in enumerate(values):
            if not isinstance(value, str) or not value:
                raise ValueError(f"input_paths[{index}] must be a non-empty string")
            path = cast(str, resolve_safe_path(value, self.base_dir))
            if not os.path.exists(path):
                raise ValueError(f"input path does not exist: {path}")
            candidates = [path]
            if os.path.isdir(path):
                candidates = [os.path.join(root, name) for root, _, names in os.walk(path) for name in names]
            for candidate in candidates:
                resolved = os.path.realpath(candidate)
                if resolved == archive_path:
                    raise ValueError("archive output cannot also be an input")
                if not os.path.isfile(resolved) or resolved in seen:
                    continue
                seen.add(resolved)
                arcname = os.path.relpath(resolved, base).replace(os.sep, "/")
                files.append((resolved, self._safe_member_name(arcname)))
                if len(files) > self.max_input_files:
                    raise ValueError(f"inputs exceed max_input_files ({self.max_input_files})")
        total = sum(os.path.getsize(path) for path, _ in files)
        if not files:
            raise ValueError("input_paths contain no regular files")
        if total > self.max_uncompressed_bytes:
            raise ValueError(f"inputs exceed max_uncompressed_bytes ({self.max_uncompressed_bytes})")
        if any(os.path.getsize(path) > self.max_member_bytes for path, _ in files):
            raise ValueError("an input exceeds max_member_bytes")
        return files

    def _create(self, path: str, values: Any, overwrite: Any, compression: Any) -> dict[str, Any]:
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be a boolean")
        if os.path.exists(path) and not overwrite:
            raise ValueError("file exists; set overwrite=true to replace it")
        if not isinstance(compression, str) or compression not in {"deflated", "stored"}:
            raise ValueError("compression must be deflated or stored")
        files = self._collect_inputs(values, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        temporary = None
        try:
            suffix = ".zip" if self._kind(path) == "zip" else ".tar"
            with tempfile.NamedTemporaryFile(
                prefix=".archive-", suffix=suffix, dir=os.path.dirname(path), delete=False
            ) as out:
                temporary = out.name
            if self._kind(path) == "zip":
                method = zipfile.ZIP_DEFLATED if compression == "deflated" else zipfile.ZIP_STORED
                with zipfile.ZipFile(temporary, "w", compression=method, allowZip64=True) as archive:
                    for source, name in files:
                        archive.write(source, name)
            else:
                mode = "w:gz" if path.lower().endswith((".tar.gz", ".tgz")) else "w"
                with tarfile.open(temporary, mode=mode) as archive:
                    for source, name in files:
                        archive.add(source, arcname=name, recursive=False)
            if os.path.getsize(temporary) > self.max_write_bytes:
                raise ValueError(f"generated archive exceeds max_write_bytes ({self.max_write_bytes})")
            entries = self._entries(temporary)
            os.replace(temporary, path)
            temporary = None
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
        return {
            "status": "success",
            "mode": "create",
            "file_path": path,
            "entry_count": len(entries),
            "uncompressed_size": sum(item["size"] for item in entries),
            "file_size": os.path.getsize(path),
        }

    @staticmethod
    def _list(path: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
        return {"status": "success", "mode": "list", "file_path": path, "entries": entries, "entry_count": len(entries)}

    def _info(self, path: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "status": "success",
            "mode": "info",
            "file_path": path,
            "format": self._kind(path),
            "entry_count": len(entries),
            "file_count": sum(not item["is_dir"] for item in entries),
            "uncompressed_size": sum(item["size"] for item in entries),
            "file_size": os.path.getsize(path),
        }

    def _selected(self, entries: list[dict[str, Any]], members: Any) -> list[dict[str, Any]]:
        if members is None:
            return entries
        if not isinstance(members, list) or not members or any(not isinstance(item, str) for item in members):
            raise ValueError("members must be a non-empty list of strings")
        requested = {self._safe_member_name(item) for item in members}
        available = {item["name"] for item in entries}
        missing = requested - available
        if missing:
            raise ValueError(f"archive members not found: {', '.join(sorted(missing))}")
        return [item for item in entries if item["name"] in requested]

    def _extract(
        self,
        path: str,
        entries: list[dict[str, Any]],
        output_dir: Any,
        members: Any,
        overwrite: Any,
    ) -> dict[str, Any]:
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be a boolean")
        directory = self._directory(output_dir)
        selected = self._selected(entries, members)
        destinations = [(item, cast(str, resolve_safe_path(item["name"], directory))) for item in selected]
        for item, destination in destinations:
            if not item["is_dir"] and os.path.exists(destination) and not overwrite:
                raise ValueError(f"file exists: {destination}; set overwrite=true")
        os.makedirs(directory, exist_ok=True)
        extracted: list[str] = []
        if self._kind(path) == "zip":
            with zipfile.ZipFile(path) as archive:
                for item, destination in destinations:
                    if item["is_dir"]:
                        os.makedirs(destination, exist_ok=True)
                        continue
                    with archive.open(item["name"]) as source:
                        self._atomic_copy(source, destination, item["size"])
                    extracted.append(destination)
        else:
            with tarfile.open(path, mode="r:*") as archive:
                for item, destination in destinations:
                    if item["is_dir"]:
                        os.makedirs(destination, exist_ok=True)
                        continue
                    source = archive.extractfile(item["name"])
                    if source is None:
                        raise ValueError(f"unable to read archive member: {item['name']}")
                    with source:
                        self._atomic_copy(source, destination, item["size"])
                    extracted.append(destination)
        return {
            "status": "success",
            "mode": "extract",
            "file_path": path,
            "output_dir": directory,
            "output_paths": extracted,
            "entry_count": len(selected),
        }

    @staticmethod
    def _atomic_copy(source: Any, destination: str, expected_size: int) -> None:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=".extract-", dir=os.path.dirname(destination), delete=False
            ) as output:
                temporary = output.name
                shutil.copyfileobj(source, output, length=1024 * 1024)
            if os.path.getsize(temporary) != expected_size:
                raise ValueError(f"archive member size changed while extracting: {destination}")
            os.replace(temporary, destination)
            temporary = None
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
