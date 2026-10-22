#!/usr/bin/env python3
"""Read-only ZIP archive inspection and safety auditing for agents."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import base64
import binascii
import calendar
import io
import os
import re
import struct
import zipfile
import zlib
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool

_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")
_SURROGATE_RANGE = re.compile(r"[\udc80-\udcff]")
_MAX_NAMES_PER_FINDING = 20

_LOCAL_SIG = b"PK\x03\x04"
_CENTRAL_SIG = b"PK\x01\x02"
_EOCD_SIG = b"PK\x05\x06"
_ZIP64_EOCD_SIG = b"PK\x06\x06"
_ZIP64_LOCATOR_SIG = b"PK\x06\x07"
_EOCD_STRUCT = struct.Struct("<4sHHHHIIH")
_ZIP64_EOCD_STRUCT = struct.Struct("<4sQHHIIQQQQ")
_ZIP64_LOCATOR_STRUCT = struct.Struct("<4sIQI")
_CENTRAL_STRUCT = struct.Struct("<4sHHHHHHIIIHHHHHII")
_LOCAL_STRUCT = struct.Struct("<4sHHHHHIIIHH")

_METHOD_NAMES = {0: "stored", 8: "deflate", 12: "bzip2", 14: "lzma"}
_ZIP64_SENTINEL = 0xFFFFFFFF
_DOS_YEAR_FLOOR = 1980
_KIB = 1024


class _ScanBudgetExceeded(Exception):
    """Raised when entry counts or verification bytes grow past the configured budget."""


class ZipInspectTool(Tool):
    """Inspect ZIP archives, audit extraction safety, and verify entry integrity.

    The tool NEVER extracts and never writes to the filesystem: `inspect` and
    `audit_safety` are metadata-only analysis of the archive records (the only
    bounded reads are tiny symlink targets), while `verify_integrity`
    decompresses every entry in memory to CRC-check it — still without a
    single filesystem write. An archive is supplied either as a file path
    (read once, inside the configured base_dir sandbox) or as a base64 payload
    (size capped). Besides the entry metadata the tool cross-validates the
    dual-record ZIP structure: the central directory is parsed from the raw
    bytes and every record is compared against its local file header, so
    forged archives that disagree between the two records are detected.
    """

    base_dir: str = "."
    max_read_bytes: int = 64 * 1024 * 1024
    max_base64_bytes: int = 16 * 1024 * 1024
    max_reported_entries: int = 200
    max_scan_entries: int = 200_000
    excessive_entry_count: int = 10_000
    max_entry_ratio: float = 100.0
    max_total_ratio: float = 200.0
    bomb_total_bytes: int = 1 << 32
    max_symlink_target_bytes: int = 4096
    max_comment_bytes: int = 1024
    max_verify_bytes: int = 256 * 1024 * 1024

    _MODES: ClassVar[set[str]] = {"inspect", "audit_safety", "verify_integrity"}

    def execute(
        self,
        mode: str,
        file_path: str | None = None,
        base64_archive: str | None = None,
        max_total_bytes: int | None = None,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            if max_total_bytes is not None and operation != "verify_integrity":
                raise ValueError("max_total_bytes is only accepted in verify_integrity mode")
            budget = self._verify_budget(max_total_bytes) if operation == "verify_integrity" else None
            source, raw, origin = self._load_archive(file_path, base64_archive)
            if operation == "verify_integrity":
                return self._verify(source, origin, raw, budget)
            structure = self._parse_structure(raw)
            entries, notes = self._build_entries(raw, structure)
            if operation == "inspect":
                return self._inspect(source, origin, raw, structure, entries, notes)
            return self._audit(raw, structure, entries, notes)
        except _ScanBudgetExceeded as exc:
            return self._error(mode, "too_large", str(exc))
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:
            return self._error(mode, "operation_error", f"Archive inspection failed: {exc}")

    # ------------------------------------------------------------------ input

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode}

    def _validate_config(self) -> None:
        for name in (
            "max_read_bytes",
            "max_base64_bytes",
            "max_reported_entries",
            "max_scan_entries",
            "excessive_entry_count",
            "bomb_total_bytes",
            "max_symlink_target_bytes",
            "max_comment_bytes",
            "max_verify_bytes",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        for name in ("max_entry_ratio", "max_total_ratio"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(f"{name} must be positive")
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")

    def _mode(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        operation = value.strip().lower()
        if operation not in self._MODES:
            raise ValueError("mode must be inspect, audit_safety, or verify_integrity")
        return operation

    def _verify_budget(self, value: Any) -> int:
        """Resolve the verify_integrity decompression budget (bytes or cap name)."""
        if value is None:
            return self.max_verify_bytes
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("max_total_bytes must be a positive integer")
        return value

    def _load_archive(self, file_path: Any, payload: Any) -> tuple[str, bytes, str]:
        """Return (source kind, archive bytes, origin label) for exactly one input."""
        if (file_path is None) == (payload is None):
            raise ValueError("provide exactly one of file_path or base64_archive")
        if file_path is not None:
            if not isinstance(file_path, str) or not file_path:
                raise ValueError("file_path must be a non-empty string")
            path = resolve_safe_path(file_path, self.base_dir)
            if not os.path.isfile(path):
                raise ValueError(f"file_path does not exist: {file_path}")
            size = os.path.getsize(path)
            if size > self.max_read_bytes:
                raise ValueError(f"archive exceeds max_read_bytes ({self.max_read_bytes})")
            with open(path, "rb") as stream:
                raw = stream.read(self.max_read_bytes + 1)
            if len(raw) > self.max_read_bytes:
                raise ValueError(f"archive exceeds max_read_bytes ({self.max_read_bytes})")
            return "file", raw, file_path
        if not isinstance(payload, str) or not payload:
            raise ValueError("base64_archive must be a non-empty string")
        try:
            raw = base64.b64decode(payload.strip().encode("ascii"), validate=True)
        except (binascii.Error, UnicodeEncodeError) as exc:
            raise ValueError(f"base64_archive is not valid base64: {exc}") from exc
        if len(raw) > self.max_base64_bytes:
            raise ValueError(f"decoded payload exceeds max_base64_bytes ({self.max_base64_bytes})")
        return "base64", raw, "base64 payload"

    # -------------------------------------------------------- raw structure

    @staticmethod
    def _parse_eocd(raw: bytes) -> dict[str, Any]:
        """Locate and decode the end-of-central-directory record (zip64 aware)."""
        eocd_pos = raw.rfind(_EOCD_SIG)
        if eocd_pos < 0:
            raise ValueError("data is not a zip archive (no end-of-central-directory record found)")
        record = raw[eocd_pos : eocd_pos + _EOCD_STRUCT.size]
        if len(record) < _EOCD_STRUCT.size:
            raise ValueError("end-of-central-directory record is truncated")
        _, disk, cd_disk, _, total_entries, cd_size, cd_offset, comment_len = _EOCD_STRUCT.unpack(record)
        if disk != 0 or cd_disk != 0:
            raise ValueError("multi-disk zip archives are not supported")
        comment = raw[eocd_pos + _EOCD_STRUCT.size :]
        if len(comment) != comment_len:
            raise ValueError("archive comment is truncated by the end of the file")
        if (
            total_entries == _ZIP64_SENTINEL
            or cd_size == _ZIP64_SENTINEL
            or cd_offset == _ZIP64_SENTINEL
            or (
                eocd_pos >= _ZIP64_LOCATOR_STRUCT.size
                and raw[eocd_pos - _ZIP64_LOCATOR_STRUCT.size : eocd_pos - _ZIP64_LOCATOR_STRUCT.size + 4]
                == _ZIP64_LOCATOR_SIG
            )
        ):
            return ZipInspectTool._parse_zip64_eocd(raw, eocd_pos, comment)
        return {
            "total_entries": total_entries,
            "cd_size": cd_size,
            "cd_offset": cd_offset,
            "cd_start": eocd_pos - cd_size,
            "comment": comment,
            "zip64": False,
        }

    @staticmethod
    def _parse_zip64_eocd(raw: bytes, eocd_pos: int, comment: bytes) -> dict[str, Any]:
        """Decode the zip64 EOCD via the locator that precedes the classic EOCD."""
        locator_pos = eocd_pos - _ZIP64_LOCATOR_STRUCT.size
        if locator_pos < 0 or raw[locator_pos : locator_pos + 4] != _ZIP64_LOCATOR_SIG:
            raise ValueError("zip64 sentinel values without a zip64 locator record")
        _, _, z64_offset, _ = _ZIP64_LOCATOR_STRUCT.unpack(raw[locator_pos:eocd_pos])
        record = raw[z64_offset : z64_offset + _ZIP64_EOCD_STRUCT.size]
        if len(record) < _ZIP64_EOCD_STRUCT.size or record[:4] != _ZIP64_EOCD_SIG:
            raise ValueError("zip64 end-of-central-directory record is missing or truncated")
        # Field order: signature, record size, version made by, version needed,
        # this disk, disk of central directory, entries this disk, total entries,
        # central-directory size, central-directory offset.
        (
            _,
            _,
            _,
            _,
            disk,
            _,
            _,
            total_entries,
            cd_size,
            cd_offset,
        ) = _ZIP64_EOCD_STRUCT.unpack(record)
        if disk != 0:
            raise ValueError("multi-disk zip archives are not supported")
        return {
            "total_entries": total_entries,
            "cd_size": cd_size,
            "cd_offset": cd_offset,
            "cd_start": z64_offset - cd_size,
            "comment": comment,
            "zip64": True,
        }

    @staticmethod
    def _parse_zip64_extra(extra: bytes, csize: int, usize: int, offset: int, disk: int) -> dict[str, Any]:
        """Extract the zip64 sizes/offset a record's extra field advertises."""
        values: dict[str, int] = {}
        has_extra = False
        position = 0
        while position + 4 <= len(extra):
            tag, size = struct.unpack_from("<HH", extra, position)
            payload = extra[position + 4 : position + 4 + size]
            if len(payload) < size:
                raise ValueError("zip64 extra field is truncated")
            if tag == 0x0001:
                has_extra = True
                cursor = 0
                for field, sentinel in (("usize", usize), ("csize", csize), ("offset", offset), ("disk", disk)):
                    if sentinel != _ZIP64_SENTINEL:
                        continue
                    width = 4 if field == "disk" else 8
                    if cursor + width > len(payload):
                        raise ValueError("zip64 extra field is truncated")
                    values[field] = int.from_bytes(payload[cursor : cursor + width], "little")
                    cursor += width
            position += 4 + size
        return {"has_zip64_extra": has_extra, "values": values}

    @classmethod
    def _parse_central(cls, raw: bytes, structure: dict[str, Any]) -> list[dict[str, Any]]:
        """Walk every central-directory record and keep the raw field values."""
        records: list[dict[str, Any]] = []
        position = structure["cd_start"]
        remaining = structure["total_entries"]
        while remaining > 0:
            fixed = raw[position : position + _CENTRAL_STRUCT.size]
            if len(fixed) < _CENTRAL_STRUCT.size or fixed[:4] != _CENTRAL_SIG:
                raise ValueError(f"central directory is corrupt at offset {position}")
            (
                _,
                _,
                _,
                flags,
                method,
                _,
                _,
                crc,
                csize,
                usize,
                name_len,
                extra_len,
                comment_len,
                disk_start,
                _,
                external_attr,
                offset,
            ) = _CENTRAL_STRUCT.unpack(fixed)
            name = raw[position + 46 : position + 46 + name_len]
            extra = raw[position + 46 + name_len : position + 46 + name_len + extra_len]
            entry_comment = raw[
                position + 46 + name_len + extra_len : position + 46 + name_len + extra_len + comment_len
            ]
            if len(name) != name_len or len(extra) != extra_len or len(entry_comment) != comment_len:
                raise ValueError("central directory is truncated inside a record")
            zip64 = cls._parse_zip64_extra(extra, csize, usize, offset, disk_start)
            values = zip64["values"]
            records.append(
                {
                    "position": position,
                    "flags": flags,
                    "method": method,
                    "crc": crc,
                    "csize": csize,
                    "usize": usize,
                    "external_attr": external_attr,
                    "offset": values.get("offset", offset) + structure["prepended"],
                    "name_bytes": name,
                    "comment": entry_comment,
                    "has_zip64_extra": zip64["has_zip64_extra"],
                    "declares_sentinel": _ZIP64_SENTINEL in (csize, usize, offset),
                }
            )
            position += 46 + name_len + extra_len + comment_len
            remaining -= 1
        if structure["total_entries"] and position != structure["cd_start"] + structure["cd_size"]:
            raise ValueError("central directory size disagrees with the end-of-central-directory record")
        return records

    @staticmethod
    def _parse_local(raw: bytes, offset: int) -> dict[str, Any] | None:
        """Decode the local file header stored at a recorded offset (zip64 aware)."""
        if offset < 0 or offset + _LOCAL_STRUCT.size > len(raw):
            return None
        fixed = raw[offset : offset + _LOCAL_STRUCT.size]
        if fixed[:4] != _LOCAL_SIG:
            return None
        (
            _,
            _,
            flags,
            method,
            _,
            _,
            crc,
            csize,
            usize,
            name_len,
            extra_len,
        ) = _LOCAL_STRUCT.unpack(fixed)
        start = offset + _LOCAL_STRUCT.size
        end = start + name_len + extra_len
        if end > len(raw):
            return None
        extra = raw[start + name_len : end]
        effective_csize, effective_usize = csize, usize
        has_zip64_extra = False
        position = 0
        while position + 4 <= len(extra):
            tag, size = struct.unpack_from("<HH", extra, position)
            payload = extra[position + 4 : position + 4 + size]
            if tag == 0x0001:
                # Local zip64 order: original size, then compressed size.
                has_zip64_extra = True
                cursor = 0
                if usize == _ZIP64_SENTINEL and cursor + 8 <= len(payload):
                    effective_usize = int.from_bytes(payload[cursor : cursor + 8], "little")
                    cursor += 8
                if csize == _ZIP64_SENTINEL and cursor + 8 <= len(payload):
                    effective_csize = int.from_bytes(payload[cursor : cursor + 8], "little")
            position += 4 + size
        return {
            "flags": flags,
            "method": method,
            "crc": crc,
            "csize": effective_csize,
            "usize": effective_usize,
            "sentinel_sizes": csize == _ZIP64_SENTINEL or usize == _ZIP64_SENTINEL,
            "has_zip64_extra": has_zip64_extra,
            "name_bytes": raw[start : start + name_len],
            "data_offset": end,
        }

    def _parse_structure(self, raw: bytes) -> dict[str, Any]:
        """Parse EOCD and central directory straight from the bytes."""
        structure = self._parse_eocd(raw)
        if structure["cd_start"] < 0:
            raise ValueError("central directory size disagrees with the end-of-central-directory record")
        # Archives with prepended data (self-extracting stubs) record offsets
        # relative to the real zip start; shift them by the detected prefix.
        structure["prepended"] = max(0, structure["cd_start"] - structure["cd_offset"])
        if structure["total_entries"]:
            if raw[structure["cd_start"] : structure["cd_start"] + 4] != _CENTRAL_SIG:
                raise ValueError("central directory signature not found at the recorded offset")
            records = self._parse_central(raw, structure)
        else:
            records = []
        if len(records) > self.max_scan_entries:
            raise _ScanBudgetExceeded(f"archive exceeds max_scan_entries ({self.max_scan_entries})")
        structure["records"] = records
        return structure

    # ---------------------------------------------------------------- entries

    @staticmethod
    def _kind(info: zipfile.ZipInfo) -> str:
        return "dir" if info.is_dir() else "file"

    @staticmethod
    def _entry_letter(mode_bits: int, kind: str) -> str:
        if (mode_bits & 0o170000) == 0o120000:
            return "l"
        return "d" if kind == "dir" else "-"

    @staticmethod
    def _symbolic_mode(mode: int, letter: str) -> str:
        """Render a numeric mode as a 10-character symbolic string via bit math."""
        chars: list[str] = []
        for shift in (6, 3, 0):
            for index, char in enumerate(("r", "w", "x")):
                chars.append(char if mode & (1 << (shift + 2 - index)) else "-")
        if mode & 0o4000:
            chars[2] = "s" if mode & 0o0100 else "S"
        if mode & 0o2000:
            chars[5] = "s" if mode & 0o0010 else "S"
        if mode & 0o1000:
            chars[8] = "t" if mode & 0o0001 else "T"
        return letter + "".join(chars)

    @staticmethod
    def _display(name: str) -> str:
        """Return a JSON-safe rendering, escaping undecodable surrogate bytes."""
        try:
            name.encode("utf-8")
        except UnicodeEncodeError:
            return name.encode("utf-8", "backslashreplace").decode("utf-8")
        return name

    def _read_link_target(self, archive: zipfile.ZipFile, info: zipfile.ZipInfo) -> str | None:
        """Bounded, best-effort read of a symlink entry's target from its content."""
        if info.flag_bits & 0x1 or info.file_size > self.max_symlink_target_bytes:
            return None
        if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA):
            return None
        try:
            with archive.open(info) as stream:
                data = stream.read(self.max_symlink_target_bytes + 1)
        except (RuntimeError, NotImplementedError, zipfile.BadZipFile, zlib.error, EOFError, OSError):
            return None
        if len(data) != info.file_size or len(data) > self.max_symlink_target_bytes:
            return None
        return self._display(data.decode("utf-8", "backslashreplace"))

    @classmethod
    def _cross_check_local(cls, raw: bytes, structure: dict[str, Any]) -> tuple[list[dict[str, Any]], list[bool]]:
        """Compare every central record against its local file header.

        Returns (findings, local_zip64_flags) aligned with the record order.
        """
        findings: list[dict[str, Any]] = []
        local_zip64: list[bool] = []
        for record in structure["records"]:
            name = record["name_bytes"].decode("utf-8", "backslashreplace")
            local = cls._parse_local(raw, record["offset"])
            if local is None:
                local_zip64.append(False)
                findings.append(
                    {
                        "rule": "central_local_mismatch",
                        "severity": "high",
                        "detail": f"no local file header found at the recorded offset {record['offset']}",
                        "entries": [cls._display(name)],
                        "count": 1,
                    }
                )
                continue
            local_zip64.append(local["has_zip64_extra"])
            field = None
            if local["name_bytes"] != record["name_bytes"]:
                field = "name"
            elif local["method"] != record["method"]:
                field = "compression method"
            else:
                descriptor = bool(local["flags"] & 0x8)
                for label, local_value, central_value in (
                    ("crc-32", local["crc"], record["crc"]),
                    ("compressed size", local["csize"], record["csize"]),
                    ("uncompressed size", local["usize"], record["usize"]),
                ):
                    if local_value == central_value:
                        continue
                    if descriptor and local_value == 0:
                        continue  # data-descriptor streams keep real values after the data
                    field = label
                    break
            if field is not None:
                findings.append(
                    {
                        "rule": "central_local_mismatch",
                        "severity": "high",
                        "detail": f"central directory and local header disagree about the {field}",
                        "entries": [cls._display(name)],
                        "count": 1,
                    }
                )
        if len(findings) > _MAX_NAMES_PER_FINDING:
            return findings[:_MAX_NAMES_PER_FINDING], local_zip64
        return findings, local_zip64

    def _build_entries(
        self, raw: bytes, structure: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Build the canonical entry list from zipfile and enrich it with raw-record facts."""
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                infos = archive.infolist()
                archive_comment = archive.comment
                entries: list[dict[str, Any]] = []
                cross_findings, local_zip64 = self._cross_check_local(raw, structure)
                notes: list[dict[str, Any]] = list(cross_findings)
                if len(infos) != len(structure["records"]):
                    notes.append(
                        {
                            "rule": "record_count_mismatch",
                            "severity": "medium",
                            "detail": (
                                f"zipfile reports {len(infos)} entries but the central directory "
                                f"holds {len(structure['records'])} records"
                            ),
                        }
                    )
                for index, info in enumerate(infos):
                    record = structure["records"][index] if index < len(structure["records"]) else None
                    has_local_zip64 = local_zip64[index] if index < len(local_zip64) else False
                    unix_mode = info.external_attr >> 16
                    is_symlink = (unix_mode & 0o170000) == 0o120000
                    kind = self._kind(info)
                    link_target = None
                    if is_symlink:
                        link_target = self._read_link_target(archive, info)
                    entries.append(
                        {
                            "name": self._display(info.filename),
                            "raw_name": info.filename,
                            "kind": kind,
                            "size_uncompressed": int(info.file_size),
                            "size_compressed": int(info.compress_size),
                            "method_int": int(info.compress_type),
                            "crc32": int(info.CRC),
                            "encrypted_flag": bool(info.flag_bits & 0x1),
                            "zip64_flag": bool(record["has_zip64_extra"] or has_local_zip64) if record else False,
                            "date_time": list(info.date_time),
                            "external_attr": self._symbolic_mode(
                                unix_mode & 0o7777, self._entry_letter(unix_mode, kind)
                            )
                            if unix_mode
                            else None,
                            "is_symlink": is_symlink,
                            "link_target": link_target,
                            "entry_comment_length": len(record["comment"]),
                        }
                    )
        except zipfile.BadZipFile as exc:
            raise ValueError(f"data is not a readable zip archive: {exc}") from exc
        if len(entries) > self.max_scan_entries:
            raise _ScanBudgetExceeded(f"archive exceeds max_scan_entries ({self.max_scan_entries})")
        if len(archive_comment) > self.max_comment_bytes:
            notes.append(
                {
                    "rule": "comment_oversized",
                    "severity": "medium",
                    "detail": f"archive comment is {len(archive_comment)} bytes (>{self.max_comment_bytes})",
                }
            )
        return entries, notes

    @staticmethod
    def _public_entry(entry: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": entry["name"],
            "kind": entry["kind"],
            "size_uncompressed": entry["size_uncompressed"],
            "size_compressed": entry["size_compressed"],
            "compression_method": _METHOD_NAMES.get(entry["method_int"], f"method-{entry['method_int']}"),
            "crc32": entry["crc32"],
            "encrypted_flag": entry["encrypted_flag"],
            "zip64_flag": entry["zip64_flag"],
            "date_time": entry["date_time"],
            "external_attr": entry["external_attr"],
            "is_symlink": entry["is_symlink"],
            "link_target": entry["link_target"],
        }

    # ------------------------------------------------------------- inspection

    def _inspect(
        self,
        source: str,
        origin: str,
        raw: bytes,
        structure: dict[str, Any],
        entries: list[dict[str, Any]],
        notes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        findings = list(notes)
        mismatch = self._extension_mismatch(source, origin)
        if mismatch:
            findings.append(mismatch)
        if raw[:4] not in (_LOCAL_SIG, _EOCD_SIG):
            findings.append(
                {
                    "rule": "prepended_data",
                    "severity": "info",
                    "detail": "archive does not start with a zip signature; prepended data (e.g. a self-extracting stub) is present",
                }
            )
        total_uncompressed = sum(entry["size_uncompressed"] for entry in entries)
        total_compressed = sum(entry["size_compressed"] for entry in entries)
        reported = entries[: self.max_reported_entries]
        return {
            "status": "success",
            "source": source,
            "file_path": origin if source == "file" else None,
            "format": "zip",
            "format_detail": "zip64" if structure["zip64"] else "classic",
            "entry_count": len(entries),
            "entries": [self._public_entry(entry) for entry in reported],
            "entries_truncated": len(entries) > len(reported),
            "archive_size": len(raw),
            "total_uncompressed": total_uncompressed,
            "total_compressed": total_compressed,
            "overall_ratio": round(total_uncompressed / total_compressed, 2) if total_compressed else None,
            "findings": findings,
        }

    @staticmethod
    def _extension_mismatch(source: str, origin: str) -> dict[str, Any] | None:
        if source != "file":
            return None  # base64 payloads carry no filename to cross-check
        if origin.lower().endswith(".zip"):
            return None
        return {
            "rule": "extension_mismatch",
            "severity": "info",
            "detail": "sniffed format zip but the name does not end with .zip",
        }

    # ------------------------------------------------------------------ audit

    def _audit(
        self,
        raw: bytes,
        structure: dict[str, Any],
        entries: list[dict[str, Any]],
        notes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        findings = self._audit_findings(structure, entries)
        known = {finding["rule"] for finding in findings}
        findings.extend(note for note in notes if note["rule"] not in known)
        blocking = [finding for finding in findings if finding["severity"] == "high"]
        total_uncompressed = sum(entry["size_uncompressed"] for entry in entries)
        total_compressed = sum(entry["size_compressed"] for entry in entries)
        return {
            "status": "success",
            "format": "zip",
            "entry_count": len(entries),
            "findings": findings,
            "extract_safe": not blocking,
            "blocking": blocking,
            "totals": {
                "uncompressed": total_uncompressed,
                "compressed": total_compressed,
                "ratio": round(total_uncompressed / total_compressed, 2) if total_compressed else None,
            },
        }

    def _audit_findings(self, structure: dict[str, Any], entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        buckets: dict[str, dict[str, Any]] = {}

        def add(rule: str, severity: str, name: str, detail: str) -> None:
            bucket = buckets.setdefault(
                rule, {"rule": rule, "severity": severity, "detail": detail, "entries": [], "count": 0}
            )
            bucket["count"] += 1
            if len(bucket["entries"]) < _MAX_NAMES_PER_FINDING:
                bucket["entries"].append(self._display(name))

        seen_names: set[str] = set()
        duplicate_firsts: list[str] = []
        oversized_comment = False
        for index, entry in enumerate(entries):
            name = entry["raw_name"]
            self._audit_entry_paths(entry, add)
            self._audit_entry_attributes(entry, add)
            if name in seen_names and name not in duplicate_firsts:
                duplicate_firsts.append(name)
                add(
                    "duplicate_entries",
                    "high",
                    name,
                    "duplicate entry name; the last occurrence wins when extractors look names up",
                )
            seen_names.add(name)
            if entry["entry_comment_length"] > self.max_comment_bytes:
                oversized_comment = True
                add(
                    "comment_oversized",
                    "medium",
                    name,
                    f"entry comment is {entry['entry_comment_length']} bytes (>{self.max_comment_bytes})",
                )
            record = structure["records"][index] if index < len(structure["records"]) else None
            if record is not None:
                if record["declares_sentinel"] and not record["has_zip64_extra"]:
                    add(
                        "zip64_lie",
                        "high",
                        name,
                        "record claims the 0xFFFFFFFF sentinel without a zip64 extra field; sizes or offsets are forged",
                    )
                elif entry["zip64_flag"] and max(entry["size_uncompressed"], entry["size_compressed"]) < 0xFFF00000:
                    add(
                        "zip64_unnecessary",
                        "info",
                        name,
                        "small entry carries zip64 records (padding or a crafted archive)",
                    )
            if not self._valid_date_time(entry["date_time"]):
                add(
                    "invalid_date_time",
                    "info",
                    name,
                    f"date_time {tuple(entry['date_time'])} is not a real timestamp",
                )
            if entry["is_symlink"]:
                target = entry["link_target"] or ""
                if target.startswith("/") or _WINDOWS_DRIVE.match(target) or target.startswith("\\\\"):
                    add("symlink_target_absolute", "high", name, f"symlink target is absolute: {self._display(target)}")
                if any(part == ".." for part in target.replace("\\", "/").split("/")):
                    add(
                        "symlink_target_escapes",
                        "high",
                        name,
                        f"symlink target contains '..': {self._display(target)}",
                    )
            if entry["encrypted_flag"]:
                add(
                    "encrypted_entries",
                    "info",
                    name,
                    "entry is flagged encrypted; a metadata-only audit cannot verify its contents",
                )
        self._audit_bombs(entries, add, buckets)
        if len(entries) > self.excessive_entry_count:
            buckets.setdefault(
                "excessive_entry_count",
                {
                    "rule": "excessive_entry_count",
                    "severity": "medium",
                    "detail": f"archive has {len(entries)} entries (> {self.excessive_entry_count})",
                    "entries": [],
                    "count": len(entries),
                },
            )
        if entries:
            buckets.setdefault(
                "integrity_not_verified",
                {
                    "rule": "integrity_not_verified",
                    "severity": "info",
                    "detail": "audit reads metadata only; run verify_integrity to CRC-check every entry",
                    "entries": [],
                    "count": 1,
                },
            )
        order = [
            "path_absolute",
            "path_traversal_dotdot",
            "windows_absolute",
            "name_control_chars",
            "name_rtl_override",
            "name_invalid_utf8",
            "backslash_in_name",
            "symlink_target_absolute",
            "symlink_target_escapes",
            "entry_oversize",
            "entry_compression_bomb",
            "total_compression_bomb",
            "nested_zip_bomb",
            "central_local_mismatch",
            "duplicate_entries",
            "zip64_lie",
            "comment_oversized",
            "excessive_entry_count",
            "encrypted_entries",
            "zip64_unnecessary",
            "invalid_date_time",
            "integrity_not_verified",
        ]
        ordered = [buckets[rule] for rule in order if rule in buckets]
        ordered.extend(bucket for rule, bucket in buckets.items() if rule not in order)
        return ordered

    def _audit_entry_paths(self, entry: dict[str, Any], add: Any) -> None:
        """Path-shape checks: traversal, absolute, Windows, and backslash names."""
        name = entry["raw_name"]
        win_parts = name.replace("\\", "/").split("/")
        if name.startswith("/"):
            add("path_absolute", "high", name, "entry name is an absolute path")
        if any(part == ".." for part in win_parts):
            add(
                "path_traversal_dotdot",
                "high",
                name,
                "'..' path component (zip-slip); flagged regardless of whether it currently escapes",
            )
        if _WINDOWS_DRIVE.match(name) or name.startswith("\\\\"):
            add("windows_absolute", "high", name, "Windows drive/UNC absolute path")
        if "\\" in name:
            add(
                "backslash_in_name",
                "medium",
                name,
                "backslash in entry name (separator confusion: Windows extractors treat it as a path separator)",
            )

    def _audit_entry_attributes(self, entry: dict[str, Any], add: Any) -> None:
        """Per-entry attribute checks: names, sizes, and encoding."""
        name = entry["raw_name"]
        if entry["size_uncompressed"] > self.bomb_total_bytes:
            add("entry_oversize", "high", name, f"single entry declares {entry['size_uncompressed']} bytes")
        if any(ord(char) < 0x20 or ord(char) == 0x7F for char in name):
            add("name_control_chars", "high", name, "control characters in entry name")
        if "\u202e" in name or "\u202d" in name:
            add("name_rtl_override", "high", name, "RTL override character in entry name (spoofing)")
        if _SURROGATE_RANGE.search(name):
            add("name_invalid_utf8", "medium", name, "name contains undecodable bytes")

    def _audit_bombs(self, entries: list[dict[str, Any]], add: Any, buckets: dict[str, dict[str, Any]]) -> None:
        """Bomb analysis: per-entry ratios, totals, and nested-zip risk."""
        total_uncompressed = 0
        total_compressed = 0
        for entry in entries:
            total_uncompressed += entry["size_uncompressed"]
            total_compressed += entry["size_compressed"]
            compressed = entry["size_compressed"]
            uncompressed = entry["size_uncompressed"]
            if not compressed or uncompressed == 0:
                continue
            ratio = uncompressed / compressed
            if ratio > self.max_entry_ratio:
                add(
                    "entry_compression_bomb",
                    "high",
                    entry["raw_name"],
                    f"entry ratio {ratio:.0f}:1 exceeds the {self.max_entry_ratio}:1 threshold",
                )
                if entry["raw_name"].lower().endswith(".zip"):
                    add(
                        "nested_zip_bomb",
                        "high",
                        entry["raw_name"],
                        "entry looks like a nested zip with a bomb-level ratio (nested-zip bomb risk)",
                    )
        total_ratio = total_uncompressed / total_compressed if total_compressed else 0
        if total_ratio > self.max_total_ratio or total_uncompressed > self.bomb_total_bytes:
            buckets.setdefault(
                "total_compression_bomb",
                {
                    "rule": "total_compression_bomb",
                    "severity": "high",
                    "detail": (
                        f"declared uncompressed total {total_uncompressed} bytes vs compressed "
                        f"{total_compressed} bytes (ratio {total_ratio:.0f}:1) exceeds the "
                        f"{self.max_total_ratio}:1 threshold or the {self.bomb_total_bytes}-byte cap"
                    ),
                    "entries": [],
                    "count": 1,
                },
            )

    @staticmethod
    def _valid_date_time(parts: list[int]) -> bool:
        """Whether a DOS-decoded timestamp names a real calendar moment."""
        if len(parts) != 6:
            return False
        year, month, day, hour, minute, second = parts
        if year < _DOS_YEAR_FLOOR or not 1 <= month <= 12 or not 1 <= day <= 31:
            return False
        if hour > 23 or minute > 59 or second > 59:
            return False
        try:
            return day <= calendar.monthrange(year, month)[1]
        except ValueError:
            return False

    # ---------------------------------------------------------------- verify

    def _verify(self, source: str, origin: str, raw: bytes, budget: int) -> dict[str, Any]:
        """Decompress every entry in memory and CRC-check it (zipfile.testzip loop)."""
        checked = 0
        crc_failures: list[str] = []
        errors: list[dict[str, Any]] = []
        processed = 0
        exhausted = False
        entry_count = 0
        try:
            archive = zipfile.ZipFile(io.BytesIO(raw))
        except zipfile.BadZipFile as exc:
            raise ValueError(f"data is not a readable zip archive: {exc}") from exc
        with archive:
            infos = archive.infolist()
            entry_count = len(infos)
            if entry_count > self.max_scan_entries:
                raise _ScanBudgetExceeded(f"archive exceeds max_scan_entries ({self.max_scan_entries})")
            for info in infos:
                display = self._display(info.filename)
                if info.flag_bits & 0x1:
                    errors.append({"name": display, "reason": "encrypted"})
                    continue
                if processed + info.file_size > budget:
                    exhausted = True
                    break
                try:
                    with archive.open(info) as stream:
                        complete = True
                        while True:
                            chunk = stream.read(64 * _KIB)
                            if not chunk:
                                break
                            processed += len(chunk)
                            if processed > budget:
                                exhausted = True
                                complete = False
                                break
                    if complete:
                        checked += 1
                except zipfile.BadZipFile as exc:
                    message = str(exc)
                    if "Bad CRC-32" in message:
                        crc_failures.append(display)
                    elif "truncat" in message.lower():
                        errors.append({"name": display, "reason": "truncated"})
                    else:
                        errors.append({"name": display, "reason": "corrupt", "detail": message})
                except NotImplementedError:
                    errors.append({"name": display, "reason": "unsupported_method"})
                except RuntimeError as exc:
                    message = str(exc)
                    errors.append(
                        {"name": display, "reason": "encrypted" if "password" in message.lower() else "corrupt"}
                    )
                except (zlib.error, EOFError, OSError) as exc:
                    errors.append({"name": display, "reason": "corrupt", "detail": str(exc)})
                except ValueError as exc:
                    # zipfile raises bare ValueErrors (e.g. negative seeks) on cut-short data.
                    message = str(exc)
                    reason = "truncated" if "seek" in message.lower() else "corrupt"
                    errors.append({"name": display, "reason": reason, "detail": message})
                if exhausted:
                    break
        result: dict[str, Any] = {
            "status": "success",
            "source": source,
            "file_path": origin if source == "file" else None,
            "format": "zip",
            "entry_count": entry_count,
            "checked": checked,
            "crc_failures": crc_failures,
            "errors": errors,
            "bytes_processed": processed,
            "budget_exhausted": exhausted,
            "writes": "none — entries are decompressed in memory only",
        }
        return result
