#!/usr/bin/env python3
"""Read-only tar archive inspection and safety auditing for agents."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import base64
import binascii
import bz2
import gzip
import io
import lzma
import os
import posixpath
import re
import tarfile
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool

_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")
_SURROGATE_RANGE = re.compile(r"[\udc80-\udcff]")
_MAX_NAMES_PER_FINDING = 20


class _ScanBudgetExceeded(Exception):
    """Raised when a decompressed stream grows past the configured budget."""


class TarInspectTool(Tool):
    """Inspect tar archives, audit extraction safety, and plan extraction paths.

    The tool NEVER extracts and never writes to the filesystem: every mode is
    pure read-only analysis of the archive bytes. An archive is supplied either
    as a file path (read once, inside the configured base_dir sandbox) or as a
    base64 payload (size capped). The format is detected from magic bytes, not
    from the file extension, and any extension mismatch is reported as a
    finding.
    """

    base_dir: str = "."
    max_read_bytes: int = 64 * 1024 * 1024
    max_base64_bytes: int = 16 * 1024 * 1024
    max_scan_bytes: int = 256 * 1024 * 1024
    max_reported_entries: int = 200
    max_scan_entries: int = 200_000
    huge_entry_bytes: int = 1 << 30
    max_compression_ratio: float = 100.0
    excessive_entry_count: int = 10_000
    mtime_floor: int = 315532800
    mtime_ceiling: int = 2**31 - 1

    _MODES: ClassVar[set[str]] = {"inspect", "audit_safety", "plan_extraction"}

    def execute(
        self,
        mode: str,
        file_path: str | None = None,
        base64_archive: str | None = None,
        dest_dir: str | None = None,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            destination = self._dest_dir(dest_dir) if operation == "plan_extraction" else None
            source, raw, origin = self._load_archive(file_path, base64_archive)
            sniffed = self._sniff(raw)
            sniffed["archive_size"] = len(raw)
            members, truncated = self._read_members(sniffed, raw)
            entries, notes = self._build_entries(members)
            if truncated:
                notes.append(
                    {
                        "rule": "archive_truncated",
                        "severity": "medium",
                        "detail": "archive data ends early; the parsed entry prefix is reported",
                    }
                )
            if operation == "inspect":
                return self._inspect(source, origin, sniffed, entries, notes)
            if operation == "audit_safety":
                return self._audit(sniffed, entries, notes)
            return self._plan(destination, sniffed, entries)
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
            "max_scan_bytes",
            "max_reported_entries",
            "max_scan_entries",
            "huge_entry_bytes",
            "excessive_entry_count",
            "mtime_floor",
            "mtime_ceiling",
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
        if self.mtime_floor >= self.mtime_ceiling:
            raise ValueError("mtime_floor must be below mtime_ceiling")

    def _mode(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        operation = value.strip().lower()
        if operation not in self._MODES:
            raise ValueError("mode must be inspect, audit_safety, or plan_extraction")
        return operation

    def _dest_dir(self, value: Any) -> str:
        """Validate the planning destination as plain text (never touched on disk)."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("dest_dir must be a non-empty string for plan_extraction")
        if "\x00" in value:
            raise ValueError("dest_dir must not contain null bytes")
        return value.strip()

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

    # ------------------------------------------------------------------ sniff

    @staticmethod
    def _sniff(raw: bytes) -> dict[str, Any]:
        """Detect compression from magic bytes and the tar variant from the header."""
        if raw.startswith(b"\x1f\x8b"):
            compression = "gz"
        elif raw.startswith(b"BZh"):
            compression = "bz2"
        elif raw.startswith(b"\xfd7zXZ\x00"):
            compression = "xz"
        else:
            compression = None
        header = TarInspectTool._header_block(TarInspectTool._open_stream(raw, compression))
        if len(header) < 512 or header == b"\x00" * 512:
            raise ValueError("data is not a tar archive (no tar header block found)")
        magic = header[257:265]
        if magic == b"ustar\x0000":
            variant = "ustar"
        elif magic == b"ustar  \x00":
            variant = "gnu"
        else:
            variant = "v7"
        return {
            "format": "tar" if compression is None else f"tar.{compression}",
            "compression": compression,
            "variant": variant,
        }

    @staticmethod
    def _open_stream(raw: bytes, compression: str | None) -> Any:
        """Wrap the raw bytes in the decompressing stream matching the sniffed magic."""
        source = io.BytesIO(raw)
        if compression == "gz":
            return gzip.GzipFile(fileobj=source)
        if compression == "bz2":
            return bz2.BZ2File(source)
        if compression == "xz":
            return lzma.LZMAFile(source)
        return source

    @staticmethod
    def _header_block(stream: Any) -> bytes:
        """Read the first 512-byte header block from a (decompressed) stream."""
        try:
            with stream as handle:
                return handle.read(512)
        except (OSError, EOFError, lzma.LZMAError) as exc:
            raise ValueError(f"compressed stream is corrupt: {exc}") from exc

    def _read_members(self, sniffed: dict[str, Any], raw: bytes) -> tuple[list[tarfile.TarInfo], bool]:
        """Fully decode the archive into memory (bounded) and parse members.

        Returns (members, truncated): a data stream cut short after at least
        one parsed member yields the parsed prefix plus truncated=True instead
        of failing the whole inspection.
        """
        if sniffed["compression"] is None:
            tar_bytes = raw
        else:
            try:
                with self._open_stream(raw, sniffed["compression"]) as stream:
                    tar_bytes = stream.read(self.max_scan_bytes + 1)
            except (OSError, EOFError, lzma.LZMAError) as exc:
                raise ValueError(f"compressed stream is corrupt: {exc}") from exc
            if len(tar_bytes) > self.max_scan_bytes:
                raise _ScanBudgetExceeded(f"decompressed stream exceeds max_scan_bytes ({self.max_scan_bytes})")
        members: list[tarfile.TarInfo] = []
        truncated = False
        try:
            with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:") as archive:
                while True:
                    try:
                        member = archive.next()
                    except tarfile.TarError as exc:
                        if members and "end of data" in str(exc).lower():
                            truncated = True
                            break
                        raise
                    if member is None:
                        break
                    members.append(member)
        except tarfile.TarError as exc:
            raise ValueError(f"data is not a readable tar archive: {exc}") from exc
        if len(members) > self.max_scan_entries:
            raise _ScanBudgetExceeded(f"archive exceeds max_scan_entries ({self.max_scan_entries})")
        return members, truncated

    # ---------------------------------------------------------------- entries

    @staticmethod
    def _kind(member: tarfile.TarInfo) -> str:
        if member.isdir():
            return "dir"
        if member.issym():
            return "symlink"
        if member.islnk():
            return "hardlink"
        if member.ischr() or member.isblk():
            return "dev"
        if member.isfifo():
            return "fifo"
        if member.isfile() or member.type == tarfile.GNUTYPE_SPARSE:
            return "file"
        return "other"

    @staticmethod
    def _entry_letter(member: tarfile.TarInfo, kind: str) -> str:
        if kind == "dir":
            return "d"
        if kind == "symlink":
            return "l"
        if kind == "hardlink":
            return "h"
        if member.ischr():
            return "c"
        if member.isblk():
            return "b"
        if kind == "fifo":
            return "p"
        if kind == "other":
            return "?"
        return "-"

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

    def _build_entries(self, members: list[tarfile.TarInfo]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        entries: list[dict[str, Any]] = []
        notes: list[dict[str, Any]] = []
        pax_seen = False
        for index, member in enumerate(members):
            kind = self._kind(member)
            entry = {
                "index": index,
                "name": self._display(member.name),
                "raw_name": member.name,
                "kind": kind,
                "size": int(member.size),
                "mode": self._symbolic_mode(member.mode, self._entry_letter(member, kind)),
                "mode_int": int(member.mode),
                "uid": member.uid,
                "gid": member.gid,
                "mtime": int(member.mtime),
                "link_target": member.linkname if member.linkname else None,
                "pax": bool(getattr(member, "pax_headers", None)),
            }
            entries.append(entry)
            if entry["pax"]:
                pax_seen = True
                if any(key.startswith("GNU.sparse") for key in member.pax_headers):
                    notes.append(
                        {
                            "rule": "sparse_file_headers",
                            "severity": "info",
                            "detail": f"PAX sparse header on entry {entry['name']}",
                        }
                    )
            if member.type == tarfile.GNUTYPE_SPARSE:
                notes.append(
                    {
                        "rule": "sparse_file_headers",
                        "severity": "info",
                        "detail": f"GNU sparse file entry {entry['name']}",
                    }
                )
        if pax_seen:
            notes.append({"rule": "pax_extensions", "severity": "info", "detail": "PAX extended headers present"})
        return entries, notes

    @staticmethod
    def _public_entry(entry: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": entry["name"],
            "kind": entry["kind"],
            "size": entry["size"],
            "mode": entry["mode"],
            "uid": entry["uid"],
            "gid": entry["gid"],
            "mtime": entry["mtime"],
            "link_target": entry["link_target"],
        }

    # ------------------------------------------------------------- inspection

    def _inspect(
        self,
        source: str,
        origin: str,
        sniffed: dict[str, Any],
        entries: list[dict[str, Any]],
        notes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        total = sum(entry["size"] for entry in entries if entry["kind"] == "file")
        archive_size = sniffed["archive_size"]
        compressed = sniffed["compression"] is not None
        ratio = round(total / archive_size, 2) if compressed and archive_size else None
        findings = list(notes)
        mismatch = self._extension_mismatch(source, origin, sniffed["format"])
        if mismatch:
            findings.append(mismatch)
        reported = entries[: self.max_reported_entries]
        variant = (
            "pax" if sniffed["variant"] != "gnu" and any(entry["pax"] for entry in entries) else sniffed["variant"]
        )
        return {
            "status": "success",
            "source": source,
            "file_path": origin if source == "file" else None,
            "format": sniffed["format"],
            "format_detail": variant,
            "entry_count": len(entries),
            "entries": [self._public_entry(entry) for entry in reported],
            "entries_truncated": len(entries) > len(reported),
            "archive_size": archive_size,
            "total_uncompressed": total,
            "compression_ratio": ratio,
            "findings": findings,
        }

    @staticmethod
    def _extension_mismatch(source: str, origin: str, fmt: str) -> dict[str, Any] | None:
        if source != "file":
            return None  # base64 payloads carry no filename to cross-check
        lowered = origin.lower()
        expected = {
            "tar": (".tar",),
            "tar.gz": (".tar.gz", ".tgz"),
            "tar.bz2": (".tar.bz2", ".tbz2", ".tbz"),
            "tar.xz": (".tar.xz", ".txz"),
        }[fmt]
        if lowered.endswith(expected):
            return None
        return {
            "rule": "extension_mismatch",
            "severity": "info",
            "detail": f"sniffed format {fmt} but the name does not end with {' or '.join(expected)}",
        }

    # ------------------------------------------------------------------ audit

    def _audit(
        self, sniffed: dict[str, Any], entries: list[dict[str, Any]], notes: list[dict[str, Any]]
    ) -> dict[str, Any]:
        findings = self._audit_findings(sniffed, entries)
        known = {finding["rule"] for finding in findings}
        findings.extend(note for note in notes if note["rule"] not in known)
        blocking = [finding for finding in findings if finding["severity"] == "high"]
        return {
            "status": "success",
            "format": sniffed["format"],
            "entry_count": len(entries),
            "findings": findings,
            "extract_safe": not blocking,
            "blocking": blocking,
        }

    def _audit_findings(self, sniffed: dict[str, Any], entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
        symlinks: dict[str, str] = {}
        total = 0
        for entry in entries:
            name = entry["raw_name"]
            self._audit_entry_paths(entry, add)
            self._audit_link_targets(entry, add)
            self._audit_entry_attributes(entry, add)
            if name in seen_names and name not in duplicate_firsts:
                duplicate_firsts.append(name)
                add(
                    "duplicate_entries",
                    "high",
                    name,
                    "duplicate entry name; the last occurrence wins on sequential extraction",
                )
            seen_names.add(name)
            if entry["kind"] == "file":
                total += entry["size"]
            # Simulate extraction order: only symlinks created EARLIER can redirect.
            landing = self._resolve_through_symlinks(name.replace("\\", "/"), symlinks)
            if landing is not None:
                resolved, chain = landing
                if self._escapes_root(resolved, "."):
                    via = " -> ".join(f"{self._display(step[0])}=>{self._display(step[1])}" for step in chain)
                    add(
                        "symlink_redirect",
                        "high",
                        name,
                        f"entry writes through earlier symlink(s) {via} and lands at {self._display(resolved)}",
                    )
            if entry["kind"] == "symlink":
                symlinks[posixpath.normpath(name.replace("\\", "/"))] = entry["link_target"] or ""

        self._audit_aggregates(sniffed, entries, total, buckets)
        order = [
            "path_absolute",
            "path_traversal_dotdot",
            "windows_absolute",
            "backslash_in_name",
            "symlink_target_absolute",
            "symlink_target_escapes",
            "symlink_redirect",
            "hardlink_outside",
            "device_special",
            "fifo_special",
            "setuid_setgid",
            "entry_oversize",
            "compression_bomb",
            "duplicate_entries",
            "excessive_entry_count",
            "mtime_anomaly",
            "name_control_chars",
            "name_rtl_override",
            "name_invalid_utf8",
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
                "'..' path component (tar-slip); flagged regardless of whether it currently escapes",
            )
        if _WINDOWS_DRIVE.match(name) or name.startswith("\\\\"):
            add("windows_absolute", "high", name, "Windows drive/UNC absolute path")
        if "\\" in name:
            add("backslash_in_name", "medium", name, "backslash in entry name (separator confusion)")

    def _audit_entry_attributes(self, entry: dict[str, Any], add: Any) -> None:
        """Per-entry attribute checks: special kinds, mode, mtime, size, encoding."""
        name = entry["raw_name"]
        kind = entry["kind"]
        if kind == "dev":
            add("device_special", "high", name, "character/block device node in archive")
        elif kind == "fifo":
            add("fifo_special", "medium", name, "FIFO special file in archive")
        if entry["mode_int"] & 0o6000:
            add("setuid_setgid", "high", name, "setuid or setgid mode bit set")
        if entry["mtime"] < self.mtime_floor or entry["mtime"] > self.mtime_ceiling:
            add("mtime_anomaly", "medium", name, "mtime far in the past or future (bomb-like)")
        if entry["size"] > self.huge_entry_bytes:
            add("entry_oversize", "high", name, f"single entry declares {entry['size']} bytes")
        if any(ord(char) < 0x20 or ord(char) == 0x7F for char in name):
            add("name_control_chars", "high", name, "control characters in entry name")
        if "\u202e" in name or "\u202d" in name:
            add("name_rtl_override", "high", name, "RTL override character in entry name (spoofing)")
        if _SURROGATE_RANGE.search(name):
            add("name_invalid_utf8", "medium", name, "name contains undecodable bytes (surrogateescape)")

    def _audit_link_targets(self, entry: dict[str, Any], add: Any) -> None:
        """Link-target checks: absolute or escaping symlink targets, outside hardlinks."""
        name = entry["raw_name"]
        kind = entry["kind"]
        target = entry["link_target"] or ""
        if kind not in ("symlink", "hardlink"):
            return
        outside = target.startswith("/") or _WINDOWS_DRIVE.match(target) or target.startswith("\\\\")
        escaping = any(part == ".." for part in target.replace("\\", "/").split("/"))
        if kind == "symlink":
            if outside:
                add("symlink_target_absolute", "high", name, f"symlink target is absolute: {self._display(target)}")
            if escaping:
                add("symlink_target_escapes", "high", name, f"symlink target contains '..': {self._display(target)}")
        elif outside or escaping:
            add(
                "hardlink_outside",
                "high",
                name,
                f"hardlink points outside the archive tree: {self._display(target)}",
            )

    def _audit_aggregates(
        self,
        sniffed: dict[str, Any],
        entries: list[dict[str, Any]],
        total: int,
        buckets: dict[str, dict[str, Any]],
    ) -> None:
        """Whole-archive checks: entry-count excess and bomb-level compression ratio."""
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
        archive_size = sniffed["archive_size"]
        if sniffed["compression"] is not None and archive_size and total / archive_size > self.max_compression_ratio:
            buckets.setdefault(
                "compression_bomb",
                {
                    "rule": "compression_bomb",
                    "severity": "high",
                    "detail": (
                        f"uncompressed total {total} bytes vs archive size {archive_size} bytes "
                        f"exceeds the {self.max_compression_ratio}:1 ratio threshold"
                    ),
                    "entries": [],
                    "count": 1,
                },
            )

    # -------------------------------------------------------------- path math

    @staticmethod
    def _resolve_through_symlinks(name: str, symlinks: dict[str, str]) -> tuple[str, list[tuple[str, str]]] | None:
        """Walk an entry path component by component, redirecting through symlinks.

        Redirected components are pushed back onto the walk so multi-hop chains
        (s1 -> s2 -> /var) resolve fully. Returns (final path, redirect chain)
        when at least one component passed through a symlink created earlier,
        otherwise None. The final path may be absolute or start with '..' when
        the walk escapes the extraction root.
        """
        queue = [part for part in name.split("/") if part not in ("", ".")]
        current: list[str] = []
        chain: list[tuple[str, str]] = []
        redirected = False
        absolute = False
        steps = 0
        while queue:
            steps += 1
            if steps > 512:  # symlink farms and loops must not wedge the walk
                break
            part = queue.pop(0)
            if part == ".":
                continue
            if part == "..":
                TarInspectTool._apply_up_segment(current, absolute)
                continue
            key = posixpath.normpath("/".join([*current, part]))
            if key in symlinks:
                target = symlinks[key]
                if not target:
                    continue
                chain.append((key, target))
                redirected = True
                if target.startswith("/"):
                    absolute = True
                    current = []
                queue = [piece for piece in target.replace("\\", "/").split("/") if piece and piece != "."] + queue
                continue
            current.append(part)
        if not redirected:
            return None
        final = ("/" + "/".join(current)) if absolute else "/".join(current)
        return final, chain

    @staticmethod
    def _apply_up_segment(current: list[str], absolute: bool) -> None:
        """Apply a '..' segment in place: pop one level, or track the climb above the root."""
        if absolute:
            if current:
                current.pop()  # '..' at an absolute root cannot escape it
        elif current and current[0] != "..":
            current.pop()
        else:
            current.append("..")

    @staticmethod
    def _escapes_root(resolved: str, root: str) -> bool:
        """Whether a normalized resolved path lands outside the extraction root."""
        if resolved.startswith("/") or _WINDOWS_DRIVE.match(resolved):
            return not (root.startswith("/") and (resolved == root or resolved.startswith(root + "/")))
        if root == ".":
            return resolved == ".." or resolved.startswith("../")
        return not (resolved == root or resolved.startswith(root + "/"))

    # ------------------------------------------------------------------- plan

    def _plan(self, dest: str, sniffed: dict[str, Any], entries: list[dict[str, Any]]) -> dict[str, Any]:
        root = posixpath.normpath(dest.replace("\\", "/")) if dest else "."
        symlinks: dict[str, str] = {}
        plans: list[dict[str, Any]] = []
        escaping: list[str] = []
        for entry in entries:
            posix_name = entry["raw_name"].replace("\\", "/")
            landing = self._resolve_through_symlinks(posix_name, symlinks)
            if landing is not None:
                relative, chain = landing
                resolved = (
                    posixpath.normpath(relative)
                    if relative.startswith("/")
                    else posixpath.normpath(posixpath.join(root, relative))
                )
                via = [f"{self._display(step[0])}=>{self._display(step[1])}" for step in chain]
            else:
                resolved = (
                    posixpath.normpath(posix_name)
                    if posix_name.startswith("/")
                    else posixpath.normpath(posixpath.join(root, posix_name))
                )
                via = None
            escapes = self._escapes_root(resolved, root)
            plan = {
                "name": entry["name"],
                "kind": entry["kind"],
                "resolved_path": self._display(resolved),
                "escapes_dest": escapes,
                "redirect_via": via,
            }
            if entry["kind"] in ("symlink", "hardlink") and entry["link_target"]:
                target = entry["link_target"]
                if target.startswith("/") or _WINDOWS_DRIVE.match(target) or target.startswith("\\\\"):
                    plan["link_target_resolved"] = target
                elif entry["kind"] == "hardlink":
                    plan["link_target_resolved"] = self._display(
                        posixpath.normpath(posixpath.join(root, target.replace("\\", "/")))
                    )
                else:
                    plan["link_target_resolved"] = self._display(
                        posixpath.normpath(posixpath.join(posixpath.dirname(resolved), target.replace("\\", "/")))
                    )
            plans.append(plan)
            if escapes:
                escaping.append(entry["name"])
            if entry["kind"] == "symlink":
                symlinks[posixpath.normpath(posix_name)] = entry["link_target"] or ""
        reported = plans[: self.max_reported_entries]
        return {
            "status": "success",
            "dest_dir": dest,
            "format": sniffed["format"],
            "entry_count": len(entries),
            "plans": reported,
            "plans_truncated": len(plans) > len(reported),
            "escaping_count": len(escaping),
            "escaping_entries": escaping[:_MAX_NAMES_PER_FINDING],
            "note": "pure path simulation; the tool never extracts and performs no filesystem writes",
        }
