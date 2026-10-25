"""Oracle tests for ZipInspectTool against stdlib zipfile and the real unzip/zipinfo binaries."""

import base64
import io
import os
import random
import re
import shutil
import stat
import struct
import subprocess
import tempfile
import time
import unittest
import warnings
import zipfile

from agentuniverse.agent.action.tool.common_tool import zip_inspect_tool as zip_module
from agentuniverse.agent.action.tool.common_tool.zip_inspect_tool import ZipInspectTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(zip_module.__file__), "zip_inspect_tool.yaml")

SANE_DATE = (2021, 6, 15, 10, 30, 0)  # a real calendar moment inside the DOS range
METHOD_NAMES = {0: "stored", 8: "deflate", 12: "bzip2", 14: "lzma"}
SYMLINK_ATTR = 0xA1FF0000  # Info-ZIP symlink: (S_IFLNK | 0o777) << 16

UNZIP_V_ROW = re.compile(
    r"^\s*(\d+)\s+(Stored|Copied|BZip2|Defl:\S+)\s+(\d+)\s+-?\d+%\s+\S+\s+\S+\s+([0-9a-f]{8})\s+(.+)$"
)
UNZIP_L_ROW = re.compile(r"^\s*(\d+)\s+\S+\s+\S+\s+(.+)$")
ZIPINFO_ROW = re.compile(r"^[dl?-][rwxsStT?-]{9}\s+")


# --------------------------------------------------------------------- helpers


def oracle_kind(info):
    """Map a zipfile entry to the tool's kind taxonomy."""
    return "dir" if info.is_dir() else "file"


def oracle_method(info):
    """Map a compress_type number the way the tool documents it."""
    return METHOD_NAMES.get(info.compress_type, f"method-{info.compress_type}")


def oracle_mode(info):
    """Symbolic mode oracle: stat.filemode over the unix bits of external_attr."""
    unix = info.external_attr >> 16
    return stat.filemode(unix) if unix else None


def add_file(archive, name, data, mode=0o644, date_time=SANE_DATE, compress_type=None):
    """Append a regular-file entry (deflated by default) to an open zipfile."""
    info = zipfile.ZipInfo(name, date_time=date_time)
    info.external_attr = (0o100000 | mode) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data, compress_type=compress_type)


def add_dir(archive, name, date_time=SANE_DATE):
    """Append a directory entry (trailing slash) to an open zipfile."""
    info = zipfile.ZipInfo(name if name.endswith("/") else name + "/", date_time=date_time)
    info.external_attr = 0o40755 << 16
    archive.writestr(info, b"")


def add_symlink(archive, name, target, date_time=SANE_DATE):
    """Append an Info-ZIP style symlink entry whose content is the target."""
    info = zipfile.ZipInfo(name, date_time=date_time)
    info.external_attr = SYMLINK_ATTR
    archive.writestr(info, target.encode("utf-8"))


def add_zip64_forced(archive, name, data, date_time=SANE_DATE):
    """Append a small entry that still carries zip64 records (force_zip64)."""
    info = zipfile.ZipInfo(name, date_time=date_time)
    info.external_attr = 0o100644 << 16
    with archive.open(info, "w", force_zip64=True) as stream:
        stream.write(data)


def eocd_info(raw):
    """Locate the EOCD and return (eocd_pos, cd_start, total_entries, comment_len)."""
    pos = raw.rfind(b"PK\x05\x06")
    if pos < 0:
        raise AssertionError("probe: no EOCD")
    _, _, _, total, cd_size, _, comment_len = struct.unpack("<HHHHIIH", raw[pos + 4 : pos + 22])
    return pos, pos - cd_size, total, comment_len


def central_records(raw):
    """Walk the central directory records and return their raw facts."""
    _, cd_start, total, _ = eocd_info(raw)
    records = []
    position = cd_start
    for _ in range(total):
        fields = struct.unpack("<4sHHHHHHIIIHHHHHII", raw[position : position + 46])
        nlen, elen, clen, offset = fields[10], fields[11], fields[12], fields[16]
        records.append(
            {
                "pos": position,
                "flags": fields[3],
                "method": fields[4],
                "crc": fields[7],
                "csize": fields[8],
                "usize": fields[9],
                "name": raw[position + 46 : position + 46 + nlen],
                "extra": raw[position + 46 + nlen : position + 46 + nlen + elen],
                "comment": raw[
                    position + 46 + nlen + elen : position + 46 + nlen + elen + clen
                ],
                "offset": offset,
            }
        )
        position += 46 + nlen + elen + clen
    return records


def has_zip64_extra(extra):
    """Whether an extra field carries the zip64 extended information record."""
    position = 0
    while position + 4 <= len(extra):
        tag, size = struct.unpack_from("<HH", extra, position)
        if tag == 0x0001:
            return True
        position += 4 + size
    return False


def record_has_zip64(raw, record):
    """Ground truth for an entry's zip64 flag: local OR central extra present."""
    offset = record["offset"]
    lnlen, lelen = struct.unpack_from("<HH", raw, offset + 26)
    local_extra = raw[offset + 30 + lnlen : offset + 30 + lnlen + lelen]
    return has_zip64_extra(local_extra) or has_zip64_extra(record["extra"])


def patched(raw, at, data):
    """Return a copy of raw with data written at the byte offset."""
    out = bytearray(raw)
    out[at : at + len(data)] = data
    return bytes(out)


def flip_data_byte(raw, name, frac=0.5):
    """Flip one byte inside an entry's compressed data (corruption-after-write)."""
    for record in central_records(raw):
        if record["name"].decode("utf-8", "replace") != name:
            continue
        offset = record["offset"]
        lnlen, lelen = struct.unpack_from("<HH", raw, offset + 26)
        data_offset = offset + 30 + lnlen + lelen
        at = data_offset + max(0, int(record["csize"] * frac))
        return patched(raw, at, bytes([raw[at] ^ 0xFF]))
    raise KeyError(name)


def splice_truncated(raw, name):
    """Cut an entry's data short while keeping the central directory and EOCD."""
    _, cd_start, _, _ = eocd_info(raw)
    for record in central_records(raw):
        if record["name"].decode("utf-8", "replace") != name:
            continue
        offset = record["offset"]
        lnlen, lelen = struct.unpack_from("<HH", raw, offset + 26)
        data_offset = offset + 30 + lnlen + lelen
        cut = data_offset + max(0, (record["csize"] * 3) // 4)
        return raw[:cut] + raw[cd_start:]
    raise KeyError(name)


def oracle_testzip_outcome(raw):
    """Oracle: 'ok', ('bad', name), or 'error' mirroring zipfile.testzip."""
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            bad = archive.testzip()
    except Exception:  # noqa: BLE001 - the oracle's own failure mode is the point
        return "error"
    return "ok" if bad is None else ("bad", bad)


# ----------------------------------------------------------------- base fixture


class ZipInspectToolTest(unittest.TestCase):
    """Shared fixture: a temp directory and a ZipInspectTool scoped to it."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.tool = ZipInspectTool(base_dir=self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def path(self, name):
        """Return an absolute path inside the temp directory."""
        return os.path.join(self.directory.name, name)

    def build(self, name, builder, compression=zipfile.ZIP_DEFLATED):
        """Build an archive via a builder callback and return its path."""
        path = self.path(name)
        with zipfile.ZipFile(path, "w", compression) as archive:
            builder(archive)
        return path

    def raw_of(self, path):
        """Read an archive's bytes back from disk."""
        with open(path, "rb") as stream:
            return stream.read()

    def inspect(self, path):
        """Run inspect on an archive path inside the sandbox."""
        return self.tool.execute(mode="inspect", file_path=os.path.basename(path))

    def audit(self, path):
        """Run audit_safety on an archive path inside the sandbox."""
        return self.tool.execute(mode="audit_safety", file_path=os.path.basename(path))

    def rules(self, result):
        """Return the {rule: severity} map of an audit result."""
        return {finding["rule"]: finding["severity"] for finding in result["findings"]}


# ------------------------------------------------------------------ (a) seeded


class SeededOracleTest(ZipInspectToolTest):
    """(a) inspect entries must match zipfile.infolist() ground truth on 200 seeded archives."""

    def test_seeded_archives_match_zipfile_ground_truth(self):
        """Compare every documented field for every entry of 200 seeded archives."""
        for seed in range(200):
            with self.subTest(seed=seed):
                path = self.build(f"seeded-{seed}.zip", self._seeded_builder(seed))
                result = self.inspect(path)
                self.assertEqual(result["status"], "success", result)
                with zipfile.ZipFile(path) as archive:
                    infos = archive.infolist()
                    expected_targets = {
                        info.filename: archive.read(info).decode("utf-8", "replace")
                        if (info.external_attr >> 16) & 0o170000 == 0o120000
                        else None
                        for info in infos
                    }
                raw = self.raw_of(path)
                records = central_records(raw)
                self.assertEqual(result["entry_count"], len(infos))
                self.assertFalse(result["entries_truncated"])
                self.assertEqual(len(result["entries"]), len(infos))
                for got, info, record in zip(result["entries"], infos, records, strict=True):
                    self.assertEqual(got["name"], info.filename)
                    self.assertEqual(got["kind"], oracle_kind(info))
                    self.assertEqual(got["size_uncompressed"], info.file_size)
                    self.assertEqual(got["size_compressed"], info.compress_size)
                    self.assertEqual(got["compression_method"], oracle_method(info))
                    self.assertEqual(got["crc32"], info.CRC)
                    self.assertEqual(got["encrypted_flag"], bool(info.flag_bits & 0x1))
                    self.assertEqual(got["date_time"], list(info.date_time))
                    self.assertEqual(got["external_attr"], oracle_mode(info))
                    self.assertEqual(
                        got["is_symlink"], (info.external_attr >> 16) & 0o170000 == 0o120000
                    )
                    self.assertEqual(got["zip64_flag"], record_has_zip64(raw, record))
                    if got["is_symlink"]:
                        self.assertEqual(got["link_target"], expected_targets[info.filename])
                    else:
                        self.assertIsNone(got["link_target"])
                total_u = sum(info.file_size for info in infos)
                total_c = sum(info.compress_size for info in infos)
                self.assertEqual(result["total_uncompressed"], total_u)
                self.assertEqual(result["total_compressed"], total_c)
                self.assertEqual(result["overall_ratio"], round(total_u / total_c, 2))

    def test_empty_archive(self):
        """A zip with zero entries inspects cleanly with a null ratio."""
        path = self.build("empty.zip", lambda archive: None)
        result = self.inspect(path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["entry_count"], 0)
        self.assertEqual(result["entries"], [])
        self.assertIsNone(result["overall_ratio"])
        self.assertEqual(result["format_detail"], "classic")

    def test_archive_comment_reported(self):
        """A short archive comment is fine; inspect exposes the zip format details."""
        def builder(archive):
            archive.writestr("a.txt", b"data")
            archive.comment = b"short note"

        path = self.build("comment.zip", builder)
        result = self.inspect(path)
        self.assertEqual(result["status"], "success")
        self.assertEqual([f["rule"] for f in result["findings"]], [])

    @staticmethod
    def _seeded_builder(seed):
        """Deterministic layout mixing dirs, files, links, unicode names, and zip64."""

        def builder(archive):
            rng = random.Random(seed)  # noqa: S311 - deterministic test data, not crypto
            add_dir(archive, "root/")
            for index in range(3):
                payload = rng.randbytes(rng.randint(0, 4096))
                add_file(
                    archive,
                    f"root/file{index}.bin",
                    payload,
                    mode=rng.choice([0o644, 0o755, 0o600]),
                    date_time=(2021, 6, 15 + index % 14, 10, index, 0),
                )
            add_file(archive, "root/zeros.bin", b"\0" * 4096)  # inspect never decompresses
            add_file(
                archive,
                "root/plain.txt",
                b"readme text\n" * 40,
                compress_type=zipfile.ZIP_STORED if seed % 2 else None,
            )
            if seed % 5 == 0:
                add_file(archive, "root/bz2.bin", rng.randbytes(300), compress_type=zipfile.ZIP_BZIP2)
            if seed % 11 == 0:
                add_file(archive, "root/lzma.bin", rng.randbytes(300), compress_type=zipfile.ZIP_LZMA)
            unicode_name = ["данные.txt", "文件.txt", "emoji🙂.txt"][seed % 3]
            add_file(archive, f"root/{unicode_name}", unicode_name.encode("utf-8") * 4)
            add_symlink(archive, "root/link", "file0.bin")
            if seed % 10 == 0:
                add_zip64_forced(archive, "root/small64.txt", b"tiny zip64 payload")
            if seed % 7 == 0:
                archive.comment = b"seeded comment"

        return builder


# --------------------------------------------------------------- (b) attacks


class AttackCorpusTest(ZipInspectToolTest):
    """(b) 25 crafted malicious archives must be flagged with the correct rules."""

    def test_zip_slip_shapes(self):
        """The classic '../evil' family must raise path_traversal_dotdot high."""
        names = ["../evil.txt", "a/../../x.txt", "a/b/c/../../../deep/evil.txt"]
        for index, name in enumerate(names):
            with self.subTest(name=name):
                path = self.build(f"dotdot-{index}.zip", lambda archive, name=name: add_file(archive, name, b"x"))
                result = self.audit(path)
                self.assertEqual(self.rules(result).get("path_traversal_dotdot"), "high")
                self.assertFalse(result["extract_safe"])

    def test_absolute_shapes(self):
        """Absolute POSIX entry names must raise path_absolute high."""
        for index, name in enumerate(["/tmp/evil.txt", "/etc/passwd", "/usr/local/bin/x"]):  # noqa: S108 - archive member names
            with self.subTest(name=name):
                path = self.build(f"abs-{index}.zip", lambda archive, name=name: add_file(archive, name, b"x"))
                result = self.audit(path)
                self.assertEqual(self.rules(result).get("path_absolute"), "high")
                self.assertFalse(result["extract_safe"])

    def test_windows_and_backslash_shapes(self):
        """Drive/UNC names and backslash traversal forms are flagged."""
        cases = [
            ("C:\\Windows\\evil.dll", {"windows_absolute", "backslash_in_name"}),
            ("\\\\server\\share\\evil", {"windows_absolute", "backslash_in_name"}),
            ("a\\..\\evil.txt", {"path_traversal_dotdot", "backslash_in_name"}),
            ("..\\top.txt", {"path_traversal_dotdot", "backslash_in_name"}),
        ]
        for index, (name, expected_rules) in enumerate(cases):
            with self.subTest(name=name):
                path = self.build(f"win-{index}.zip", lambda archive, name=name: add_file(archive, name, b"x"))
                rules = self.rules(self.audit(path))
                for rule in expected_rules:
                    self.assertEqual(rules.get(rule), "high" if rule != "backslash_in_name" else "medium")
                self.assertFalse(self.audit(path)["extract_safe"])

    def test_symlink_escape_shapes(self):
        """Escaping and absolute symlink targets are flagged high."""
        def builder_relative(archive):
            add_symlink(archive, "out_link", "../../out")
            add_file(archive, "out_link/payload.txt", b"pwn")  # written through the link

        def builder_absolute(archive):
            add_symlink(archive, "root_link", "/etc/passwd")  # noqa: S108 - archive member target

        path = self.build("sym-esc.zip", builder_relative)
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("symlink_target_escapes"), "high")
        self.assertFalse(result["extract_safe"])
        path = self.build("sym-abs.zip", builder_absolute)
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("symlink_target_absolute"), "high")
        self.assertFalse(result["extract_safe"])

    def test_single_entry_bomb(self):
        """A highly compressible 100MB entry must raise the bomb rules high."""
        path = self.build(
            "bomb.zip", lambda archive: add_file(archive, "zeros.bin", b"\0" * 100_000_000)
        )
        result = self.audit(path)
        rules = self.rules(result)
        self.assertEqual(rules.get("entry_compression_bomb"), "high")
        self.assertEqual(rules.get("total_compression_bomb"), "high")
        self.assertNotIn("nested_zip_bomb", rules)
        self.assertFalse(result["extract_safe"])
        inspected = self.inspect(path)
        self.assertGreater(inspected["overall_ratio"], 1000)

    def test_total_bomb_with_entry_ratio_below_threshold(self):
        """Total ratio can trip while each entry stays under a raised entry cap."""
        payload = random.Random(5).randbytes(1000) + b"\0" * 449_000  # noqa: S311 - deterministic test data

        def builder(archive):
            for index in range(3):
                add_file(archive, f"pad{index}.bin", payload)

        path = self.build("total-bomb.zip", builder)
        lenient = ZipInspectTool(base_dir=self.directory.name, max_entry_ratio=500, max_total_ratio=100)
        result = lenient.execute(mode="audit_safety", file_path="total-bomb.zip")
        rules = self.rules(result)
        self.assertNotIn("entry_compression_bomb", rules)
        self.assertEqual(rules.get("total_compression_bomb"), "high")
        self.assertFalse(result["extract_safe"])

    def test_entry_ratio_threshold_option(self):
        """The per-entry bomb threshold is configurable."""
        payload = b"\0" * 8192
        path = self.build("mild.zip", lambda archive: add_file(archive, "pad.bin", payload))
        strict = ZipInspectTool(base_dir=self.directory.name, max_entry_ratio=2.0)
        result = strict.execute(mode="audit_safety", file_path="mild.zip")
        self.assertEqual(self.rules(result).get("entry_compression_bomb"), "high")

    def test_nested_zip_bomb(self):
        """A .zip-named entry with a bomb-level ratio raises the nested rule."""
        def builder(archive):
            add_file(archive, "inner.zip", b"\0" * 1_000_000)
            add_file(archive, "outer.txt", b"plain")

        path = self.build("nested.zip", builder)
        result = self.audit(path)
        rules = self.rules(result)
        self.assertEqual(rules.get("nested_zip_bomb"), "high")
        self.assertEqual(rules.get("entry_compression_bomb"), "high")
        self.assertIn("inner.zip", next(f for f in result["findings"] if f["rule"] == "nested_zip_bomb")["entries"])

    def test_benign_nested_zip_not_flagged(self):
        """A .zip-named entry with incompressible content raises no nested rule."""
        payload = random.Random(6).randbytes(4096)  # noqa: S311 - deterministic test data
        path = self.build("nested-ok.zip", lambda archive: add_file(archive, "data.zip", payload))
        self.assertNotIn("nested_zip_bomb", self.rules(self.audit(path)))

    def test_forged_central_name(self):
        """Editing the central name after writing is caught as a mismatch."""
        raw = self.raw_of(self.build("forge-name.zip", lambda archive: add_file(archive, "one.txt", b"data")))
        forged = patched(raw, central_records(raw)[0]["pos"] + 46, b"evil.tx")  # same 7-byte length
        path = self.path("forge-name-2.zip")
        with open(path, "wb") as stream:
            stream.write(forged)
        result = self.audit(path)
        finding = next(f for f in result["findings"] if f["rule"] == "central_local_mismatch")
        self.assertEqual(finding["severity"], "high")
        self.assertIn("name", finding["detail"])
        self.assertFalse(result["extract_safe"])

    def test_forged_central_crc(self):
        """Editing the central CRC after writing is caught as a mismatch."""
        raw = self.raw_of(self.build("forge-crc.zip", lambda archive: add_file(archive, "one.txt", b"data")))
        record = central_records(raw)[0]
        forged = patched(raw, record["pos"] + 16, struct.pack("<I", record["crc"] ^ 0xFFFF))
        path = self.path("forge-crc-2.zip")
        with open(path, "wb") as stream:
            stream.write(forged)
        result = self.audit(path)
        finding = next(f for f in result["findings"] if f["rule"] == "central_local_mismatch")
        self.assertEqual(finding["severity"], "high")
        self.assertIn("crc", finding["detail"])

    def test_duplicate_names_last_wins(self):
        """Duplicate names are flagged high; zipfile's lookup keeps the last one."""
        def builder(archive):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                archive.writestr("dup.txt", b"first-content")
                archive.writestr("dup.txt", b"second-content!!")

        path = self.build("dup.zip", builder)
        with zipfile.ZipFile(path) as archive:
            self.assertEqual(len(archive.infolist()), 2)
            self.assertEqual(archive.read("dup.txt"), b"second-content!!")  # last wins, verified
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("duplicate_entries"), "high")
        self.assertFalse(result["extract_safe"])

    def test_encrypted_flag_entry(self):
        """A central-directory encrypted flag is reported, never a crash."""
        raw = self.raw_of(self.build("enc.zip", lambda archive: add_file(archive, "secret.txt", b"data")))
        record = central_records(raw)[0]
        forged = patched(raw, record["pos"] + 8, struct.pack("<H", record["flags"] | 0x1))
        path = self.path("enc-2.zip")
        with open(path, "wb") as stream:
            stream.write(forged)
        inspected = self.inspect(path)
        self.assertEqual(inspected["status"], "success")
        self.assertTrue(inspected["entries"][0]["encrypted_flag"])
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("encrypted_entries"), "info")
        verified = self.tool.execute(mode="verify_integrity", file_path="enc-2.zip")
        self.assertEqual(verified["status"], "success")
        self.assertEqual(verified["errors"], [{"name": "secret.txt", "reason": "encrypted"}])

    def test_zip64_sentinel_lie(self):
        """0xFFFFFFFF sizes without a zip64 extra field raise zip64_lie high."""
        raw = self.raw_of(self.build("lie.zip", lambda archive: add_file(archive, "one.txt", b"data")))
        record = central_records(raw)[0]
        forged = patched(raw, record["pos"] + 24, struct.pack("<I", 0xFFFFFFFF))
        path = self.path("lie-2.zip")
        with open(path, "wb") as stream:
            stream.write(forged)
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("zip64_lie"), "high")
        self.assertFalse(result["extract_safe"])

    def test_declared_total_over_four_gib(self):
        """Patched 0xFFFFFF00 sizes push the declared total past the 4GiB cap."""
        def builder(archive):
            add_file(archive, "one.txt", b"data")
            add_file(archive, "two.txt", b"data2")

        raw = self.raw_of(self.build("huge-declared.zip", builder))
        out = raw
        for record in central_records(raw):
            out = patched(out, record["pos"] + 24, struct.pack("<I", 0xFFFFFF00))
        path = self.path("huge-declared-2.zip")
        with open(path, "wb") as stream:
            stream.write(out)
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("total_compression_bomb"), "high")
        self.assertGreater(result["totals"]["uncompressed"], 1 << 32)

    def test_comment_overflows(self):
        """Oversized archive and entry comments raise comment_oversized medium."""
        def builder(archive):
            add_file(archive, "a.txt", b"x")
            archive.comment = b"C" * 2000

        path = self.build("comment-big.zip", builder)
        self.assertEqual(self.rules(self.audit(path)).get("comment_oversized"), "medium")

        def builder_entry(archive):
            info = zipfile.ZipInfo("b.txt", date_time=SANE_DATE)
            info.external_attr = 0o100644 << 16
            info.comment = b"E" * 2000
            archive.writestr(info, b"x")

        path = self.build("comment-entry.zip", builder_entry)
        self.assertEqual(self.rules(self.audit(path)).get("comment_oversized"), "medium")

    def test_invalid_date_times(self):
        """Month 0 and February 30 decode cleanly but raise invalid_date_time info."""
        def builder(archive):
            add_file(archive, "m0.txt", b"x", date_time=(2020, 0, 5, 10, 0, 0))
            add_file(archive, "feb30.txt", b"y", date_time=(2020, 2, 30, 10, 0, 0))

        path = self.build("dates.zip", builder)
        result = self.audit(path)
        finding = next(f for f in result["findings"] if f["rule"] == "invalid_date_time")
        self.assertEqual(finding["severity"], "info")
        self.assertEqual(set(finding["entries"]), {"m0.txt", "feb30.txt"})
        self.assertTrue(result["extract_safe"])  # info findings never block

    def test_spoofed_names(self):
        """Control characters and RTL overrides in names are flagged high."""
        def builder(archive):
            add_file(archive, "bad\x01name.txt", b"x")
            add_file(archive, "x\u202Eevil.txt", b"y")

        path = self.build("spoof.zip", builder)
        result = self.audit(path)
        rules = self.rules(result)
        self.assertEqual(rules.get("name_control_chars"), "high")
        self.assertEqual(rules.get("name_rtl_override"), "high")
        self.assertFalse(result["extract_safe"])


class BenignCorpusTest(ZipInspectToolTest):
    """(b) 200 benign archives must produce zero high findings and extract_safe=True."""

    def test_benign_corpus_zero_highs(self):
        """Audit 200 varied benign archives: no high findings anywhere."""
        for seed in range(200):
            with self.subTest(seed=seed):
                path = self.build(f"benign-{seed}.zip", self._benign_builder(seed))
                result = self.audit(path)
                self.assertEqual(result["status"], "success", result)
                highs = [finding for finding in result["findings"] if finding["severity"] == "high"]
                self.assertEqual(highs, [], f"seed {seed} produced highs: {highs}")
                self.assertTrue(result["extract_safe"])

    @staticmethod
    def _benign_builder(seed):
        """Benign layout: no '..', no backslash, no absolute names, sane dates."""

        def builder(archive):
            rng = random.Random(10_000 + seed)  # noqa: S311 - deterministic test data, not crypto
            add_dir(archive, "app/")
            add_dir(archive, "app/assets/")
            add_file(archive, "app/README.md", b"# readme\n" * 8)
            add_file(archive, "app/assets/logo.bin", rng.randbytes(rng.randint(1, 4096)))
            add_file(archive, "app/assets/deep/data.dat", rng.randbytes(2048), mode=0o600)
            add_file(archive, "app/note with space.txt", b"ok")
            if seed % 5 == 0:
                add_file(archive, "app/数据.txt", "数据".encode("utf-8") * 3)
            if seed % 3 == 0:
                add_symlink(archive, "app/latest", "README.md")
            if seed % 10 == 0:
                add_zip64_forced(archive, "app/small64.bin", b"tiny")
            if seed % 7 == 0:
                archive.comment = b"ok"

        return builder


# ----------------------------------------------------------- (c) verify mode


class VerifyIntegrityTest(ZipInspectToolTest):
    """(c) verify_integrity must agree with zipfile.testzip across 100 archives."""

    def _corpus_builder(self, seed):
        """Mixed deterministic content for the integrity corpus."""

        def builder(archive):
            rng = random.Random(30_000 + seed)  # noqa: S311 - deterministic test data, not crypto
            add_file(archive, f"case{seed}/one.bin", rng.randbytes(1500))
            add_file(archive, f"case{seed}/two.txt", b"text payload\n" * 30)
            add_dir(archive, f"case{seed}/sub/")
            add_file(archive, f"case{seed}/sub/three.log", rng.randbytes(300))

        return builder

    def test_intact_archives_agree_with_testzip(self):
        """90 intact archives: zero CRC failures exactly where testzip passes."""
        for seed in range(90):
            with self.subTest(seed=seed):
                path = self.build(f"ok-{seed}.zip", self._corpus_builder(seed))
                result = self.tool.execute(mode="verify_integrity", file_path=os.path.basename(path))
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["crc_failures"], [])
                self.assertEqual(result["errors"], [])
                self.assertEqual(result["checked"], result["entry_count"])
                self.assertFalse(result["budget_exhausted"])
                self.assertEqual(oracle_testzip_outcome(self.raw_of(path)), "ok")

    def test_corrupted_archives_flagged_like_testzip(self):
        """10 corrupted-after-write archives are detected wherever testzip detects."""
        for seed in range(10):
            with self.subTest(seed=seed):
                path = self.build(f"bad-{seed}.zip", self._corpus_builder(seed))
                frac = 0.5 if seed % 2 == 0 else 0.9
                corrupted = flip_data_byte(self.raw_of(path), f"case{seed}/one.bin", frac)
                target = self.path(f"bad-{seed}-x.zip")
                with open(target, "wb") as stream:
                    stream.write(corrupted)
                oracle = oracle_testzip_outcome(corrupted)
                self.assertNotEqual(oracle, "ok")
                result = self.tool.execute(mode="verify_integrity", file_path=os.path.basename(target))
                self.assertEqual(result["status"], "success")
                flagged = set(result["crc_failures"]) | {error["name"] for error in result["errors"]}
                self.assertIn(f"case{seed}/one.bin", flagged)
                if oracle != "error":  # exact equivalence when testzip returns a name
                    self.assertIn(oracle[1], result["crc_failures"])

    def test_budget_bounds_decompression(self):
        """A tight max_total_bytes stops verification with a partial, honest report."""
        def builder(archive):
            add_file(archive, "a.bin", b"A" * 8192)
            add_file(archive, "b.bin", b"B" * 8192)

        path = self.build("budget.zip", builder)
        result = self.tool.execute(
            mode="verify_integrity", file_path="budget.zip", max_total_bytes=10_000
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["budget_exhausted"])
        self.assertEqual(result["checked"], 1)
        self.assertEqual(result["bytes_processed"], 8192)

    def test_max_total_bytes_rejected_outside_verify(self):
        """max_total_bytes is only accepted in verify_integrity mode."""
        result = self.tool.execute(mode="inspect", file_path="whatever.zip", max_total_bytes=100)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_truncated_entry_reported_structurally(self):
        """An entry cut short mid-data surfaces as failures, never a crash."""
        def builder(archive):
            add_file(archive, "one.txt", b"1" * 2048)
            add_file(archive, "two.txt", b"2" * 2048)
            add_file(archive, "three.txt", b"3" * 2048)

        path = self.build("cut-entry.zip", builder)
        spliced = splice_truncated(self.raw_of(path), "two.txt")
        target = self.path("cut-entry-2.zip")
        with open(target, "wb") as stream:
            stream.write(spliced)
        self.assertEqual(oracle_testzip_outcome(spliced), "error")  # zipfile cannot run either
        result = self.tool.execute(mode="verify_integrity", file_path=os.path.basename(target))
        self.assertEqual(result["status"], "success")
        flagged = {error["name"]: error["reason"] for error in result["errors"]}
        self.assertIn("two.txt", flagged)
        self.assertIn(flagged["two.txt"], {"truncated", "corrupt"})
        self.assertIn("three.txt", flagged)  # its data is gone entirely after the splice

    def test_unsupported_method_reported(self):
        """A patched method 99 is reported as unsupported_method per entry."""
        def builder(archive):
            add_file(archive, "one.txt", b"data")

        raw = self.raw_of(self.build("m99.zip", builder))
        record = central_records(raw)[0]
        out = patched(patched(raw, record["pos"] + 10, struct.pack("<H", 99)), record["offset"] + 8, struct.pack("<H", 99))
        target = self.path("m99-2.zip")
        with open(target, "wb") as stream:
            stream.write(out)
        with zipfile.ZipFile(target) as archive:
            self.assertEqual(archive.infolist()[0].compress_type, 99)
        result = self.tool.execute(mode="verify_integrity", file_path=os.path.basename(target))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["errors"], [{"name": "one.txt", "reason": "unsupported_method"}])
        inspected = self.inspect(target)
        self.assertEqual(inspected["entries"][0]["compression_method"], "method-99")


# --------------------------------------------------- (d) unzip/zipinfo oracle


@unittest.skipUnless(shutil.which("unzip") and shutil.which("zipinfo"), "unzip/zipinfo binaries not available")
class UnzipCrossCheckTest(ZipInspectToolTest):
    """(d) the real unzip and zipinfo binaries must agree with inspect on 50 archives."""

    def test_unzip_v_sizes_methods_crc(self):
        """unzip -v lengths, methods, sizes, and CRC-32 match inspect entries."""
        for seed in range(50):
            with self.subTest(seed=seed):
                path = self.build(f"cross-{seed}.zip", self._cross_builder(seed))
                listing = self.run_unzip("-v", path)
                rows = [
                    line
                    for line in listing.splitlines()
                    if UNZIP_V_ROW.match(line)
                ]
                result = self.inspect(path)
                self.assertEqual(len(rows), result["entry_count"])
                for row, entry in zip(rows, result["entries"], strict=True):
                    length, method, size, crc, name = UNZIP_V_ROW.match(row).groups()
                    self.assertEqual(entry["name"], name)
                    self.assertEqual(entry["size_uncompressed"], int(length))
                    self.assertEqual(entry["size_compressed"], int(size))
                    self.assertEqual(format(entry["crc32"], "08x"), crc)
                    self.assertEqual(
                        entry["compression_method"],
                        {"Stored": "stored", "Copied": "stored", "BZip2": "bzip2"}.get(
                            method.split(":")[0], "deflate" if method.startswith("Defl") else None
                        ),
                    )

    def test_unzip_l_names_and_sizes(self):
        """unzip -l names and lengths match inspect entries on the same archives."""
        for seed in range(50):
            with self.subTest(seed=seed):
                path = self.build(f"crossl-{seed}.zip", self._cross_builder(seed))
                listing = self.run_unzip("-l", path)
                rows = [line for line in listing.splitlines() if UNZIP_L_ROW.match(line)]
                result = self.inspect(path)
                self.assertEqual(len(rows), result["entry_count"])
                for row, entry in zip(rows, result["entries"], strict=True):
                    length, name = UNZIP_L_ROW.match(row).groups()
                    self.assertEqual(entry["name"], name)
                    self.assertEqual(entry["size_uncompressed"], int(length))

    def test_zipinfo_names_and_kind_letters(self):
        """zipinfo -1 names and default-listing kind letters agree with inspect."""
        for seed in range(25):
            with self.subTest(seed=seed):
                path = self.build(f"crossz-{seed}.zip", self._cross_builder(seed))
                names = self.run_zipinfo("-1", path).splitlines()
                result = self.inspect(path)
                self.assertEqual(names, [entry["name"] for entry in result["entries"]])
                listing = self.run_zipinfo(None, path)
                letters = [line[0] for line in listing.splitlines() if ZIPINFO_ROW.match(line)]
                kinds = [entry["kind"] for entry in result["entries"]]
                self.assertEqual(len(letters), len(kinds))
                for letter, kind, entry in zip(letters, kinds, result["entries"], strict=True):
                    if entry["is_symlink"]:
                        self.assertEqual(letter, "l")
                    elif letter in {"-", "?"}:
                        self.assertEqual(kind, "file")
                    else:
                        self.assertEqual(letter, kind[0])

    def run_unzip(self, flag, path):
        """Run unzip as the fixed oracle binary."""
        completed = subprocess.run(  # noqa: S603 - fixed system unzip used as the oracle
            [  # noqa: S607 - unzip resolved from PATH is the point of this oracle
                "unzip",
                flag,
                path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout

    def run_zipinfo(self, flag, path):
        """Run zipinfo as the fixed oracle binary."""
        args = ["zipinfo"] if flag is None else ["zipinfo", flag]
        completed = subprocess.run(  # noqa: S603 - fixed system zipinfo used as the oracle
            [*args, path],  # noqa: S607 - zipinfo resolved from PATH is the point of this oracle
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout

    @staticmethod
    def _cross_builder(seed):
        """Deterministic ASCII-named layout with stored, deflated, and link entries."""

        def builder(archive):
            rng = random.Random(20_000 + seed)  # noqa: S311 - deterministic test data, not crypto
            add_dir(archive, "d0/")
            add_file(archive, "d0/f0.txt", rng.randbytes(64), compress_type=zipfile.ZIP_STORED)
            add_file(archive, "d0/f1.log", rng.randbytes(512))
            add_symlink(archive, "d0/s0", "f0.txt")
            if seed % 2 == 0:
                add_file(archive, "d0/f2.bin", rng.randbytes(128))

        return builder


# ----------------------------------------------------------- (e) pathological


class PathologicalInputTest(ZipInspectToolTest):
    """(e) corrupted archives, caps, and the 100k-entry archive must stay structured and fast."""

    def write_raw(self, name, data):
        """Write raw bytes as a file in the sandbox."""
        path = self.path(name)
        with open(path, "wb") as stream:
            stream.write(data)
        return path

    def test_empty_file_is_structured_error(self):
        """An empty file is rejected with a structured validation error."""
        result = self.inspect(self.write_raw("empty.zip", b""))
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_garbage_is_structured_error(self):
        """Random garbage bytes fail EOCD discovery without raising."""
        rng = random.Random(7)  # noqa: S311 - deterministic test data, not crypto
        result = self.inspect(self.write_raw("garbage.zip", rng.randbytes(1024)))
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("end-of-central-directory", result["error"])

    def test_truncated_eocd_is_structured_error(self):
        """Cutting the EOCD tail off is a clean validation error."""
        source = self.build("full.zip", lambda archive: add_file(archive, "f.txt", b"data" * 50))
        raw = self.raw_of(source)
        for cut in (8, 12, 21):
            with self.subTest(cut=cut):
                result = self.inspect(self.write_raw(f"cut-{cut}.zip", raw[: len(raw) - cut]))
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["error_type"], "validation_error")

    def test_corrupted_central_directory_is_structured_error(self):
        """A smashed central-directory signature is a clean validation error."""
        raw = self.raw_of(self.build("ok.zip", lambda archive: add_file(archive, "f.txt", b"data")))
        _, cd_start, _, _ = eocd_info(raw)
        result = self.inspect(self.write_raw("bad-cd.zip", patched(raw, cd_start, b"XXXX")))
        self.assertEqual(result["status"], "error")
        self.assertIn("central directory", result["error"])

    def test_multi_disk_patch_is_structured_error(self):
        """A non-zero disk number in the EOCD is rejected as multi-disk."""
        raw = self.raw_of(self.build("disk.zip", lambda archive: add_file(archive, "f.txt", b"data")))
        pos, _, _, _ = eocd_info(raw)
        result = self.inspect(self.write_raw("disk-2.zip", patched(raw, pos + 4, struct.pack("<H", 1))))
        self.assertEqual(result["status"], "error")
        self.assertIn("multi-disk", result["error"])

    def test_entry_count_cap(self):
        """Archives beyond max_scan_entries return a too_large error."""
        def builder(archive):
            for index in range(120):
                archive.writestr(f"e{index}.txt", b"")

        path = self.build("wide.zip", builder)
        strict = ZipInspectTool(base_dir=self.directory.name, max_scan_entries=100)
        result = strict.execute(mode="inspect", file_path="wide.zip")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "too_large")

    def test_reported_entries_cap(self):
        """inspect reports at most max_reported_entries and says so."""
        def builder(archive):
            for index in range(6):
                add_file(archive, f"e{index}.txt", b"x")

        path = self.build("capped.zip", builder)
        strict = ZipInspectTool(base_dir=self.directory.name, max_reported_entries=3)
        result = strict.execute(mode="inspect", file_path="capped.zip")
        self.assertEqual(len(result["entries"]), 3)
        self.assertTrue(result["entries_truncated"])
        self.assertEqual(result["entry_count"], 6)

    def test_hundred_thousand_entries_within_cap_and_time(self):
        """A 100k-entry zip64 archive stays under the cap and finishes quickly."""
        path = self.path("huge-count.zip")
        started = time.monotonic()
        with zipfile.ZipFile(path, "w") as archive:
            for index in range(100_000):
                archive.writestr(f"e{index}.txt", b"")
        build_seconds = time.monotonic() - started
        self.assertLess(build_seconds, 120)
        started = time.monotonic()
        result = self.inspect(path)
        inspect_seconds = time.monotonic() - started
        self.assertLess(inspect_seconds, 60, f"inspect took {inspect_seconds:.1f}s")
        self.assertEqual(result["entry_count"], 100_000)
        self.assertEqual(result["format_detail"], "zip64")
        self.assertEqual(len(result["entries"]), 200)
        self.assertTrue(result["entries_truncated"])
        audit = self.audit(path)
        self.assertEqual(self.rules(audit).get("excessive_entry_count"), "medium")

    def test_base64_input_round_trip(self):
        """A base64 payload inspects identically to the same archive on disk."""
        path = self.build("b64.zip", lambda archive: add_file(archive, "f.txt", b"payload"))
        payload = base64.b64encode(self.raw_of(path)).decode("ascii")
        result = self.tool.execute(mode="inspect", base64_archive=payload)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["source"], "base64")
        self.assertEqual(result["entries"][0]["name"], "f.txt")

    def test_base64_size_cap(self):
        """Oversized base64 payloads are rejected by the cap."""
        payload = base64.b64encode(b"A" * 64).decode("ascii")
        strict = ZipInspectTool(base_dir=self.directory.name, max_base64_bytes=16)
        result = strict.execute(mode="inspect", base64_archive=payload)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_base64_bytes", result["error"])

    def test_base64_validation(self):
        """Invalid base64 text is a validation error."""
        result = self.tool.execute(mode="inspect", base64_archive="!!!not-base64!!!")
        self.assertEqual(result["status"], "error")
        self.assertIn("base64", result["error"])

    def test_input_contract_errors(self):
        """Mode and XOR input validation return structured errors."""
        self.assertEqual(self.tool.execute(mode="nope")["error_type"], "validation_error")
        self.assertIn("exactly one", self.tool.execute(mode="inspect")["error"])
        both = self.tool.execute(mode="inspect", file_path="a.zip", base64_archive="AAAA")
        self.assertIn("exactly one", both["error"])
        missing = self.tool.execute(mode="inspect", file_path="missing.zip")
        self.assertEqual(missing["error_type"], "validation_error")

    def test_extension_mismatch_finding(self):
        """A zip named .dat still sniffs as zip and notes the mismatch."""
        source = self.build("real.zip", lambda archive: add_file(archive, "f.txt", b"data"))
        renamed = self.path("disguised.dat")
        os.replace(source, renamed)
        result = self.inspect(renamed)
        self.assertEqual(result["format"], "zip")
        self.assertIn("extension_mismatch", {finding["rule"] for finding in result["findings"]})

    def test_prepended_stub(self):
        """A self-extracting-style stub still inspects with a prepended_data note."""
        source = self.build("stub.zip", lambda archive: add_file(archive, "f.txt", b"data"))
        stubbed = b"#!/bin/sh\nstub-bytes\x00\x01" + self.raw_of(source)
        path = self.write_raw("sfx.zip", stubbed)
        result = self.inspect(path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["entries"][0]["name"], "f.txt")
        rules = {finding["rule"] for finding in result["findings"]}
        self.assertIn("prepended_data", rules)

    def test_audit_is_deterministic(self):
        """Repeated audits of the same archive return identical results."""
        def builder(archive):
            add_file(archive, "../evil", b"x")
            add_symlink(archive, "s", "/tmp")  # noqa: S108 - archive member target

        path = self.build("determ.zip", builder)
        self.assertEqual(self.audit(path), self.audit(path))

    def test_read_only_contract_no_writes(self):
        """Running every mode leaves the sandbox with only the archive file present."""
        path = self.build("ro.zip", lambda archive: add_file(archive, "f.txt", b"data"))
        before = sorted(os.listdir(self.directory.name))
        self.inspect(path)
        self.audit(path)
        self.tool.execute(mode="verify_integrity", file_path="ro.zip")
        self.assertEqual(sorted(os.listdir(self.directory.name)), before)

    def test_verify_decompresses_but_bomb_cannot_blow_it(self):
        """verify bounds decompression even for a bomb-sized entry."""
        path = self.build("vbomb.zip", lambda archive: add_file(archive, "zeros.bin", b"\0" * 20_000_000))
        result = self.tool.execute(
            mode="verify_integrity", file_path="vbomb.zip", max_total_bytes=1_000_000
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["budget_exhausted"])
        self.assertLessEqual(result["bytes_processed"], 1_000_000 + 64 * 1024)


# ------------------------------------------------------------------ registration


class ZipInspectRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped zip_inspect_tool.yaml as a tool component."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the current app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the shipped yaml resolves to a tool component exposing the ZipInspectTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "ZipInspectTool")

    def test_manager(self):
        """Verify the ZipInspectTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, ZipInspectTool)
        self.assertEqual(tool.input_keys, ["mode"])


if __name__ == "__main__":
    unittest.main()
