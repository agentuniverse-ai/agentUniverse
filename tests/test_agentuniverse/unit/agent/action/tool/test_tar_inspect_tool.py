"""Oracle tests for TarInspectTool against stdlib tarfile, os.path.normpath, and the real tar binary."""

import base64
import io
import json
import os
import posixpath
import random
import stat
import subprocess
import tarfile
import tempfile
import time
import unittest
from typing import ClassVar

from agentuniverse.agent.action.tool.common_tool import tar_inspect_tool as tar_module
from agentuniverse.agent.action.tool.common_tool.tar_inspect_tool import TarInspectTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(tar_module.__file__), "tar_inspect_tool.yaml")

SANE_MTIME = 1_575_800_000  # 2019-12-08, inside the default mtime sanity window
COMPRESS_MODES = {None: "w", "gz": "w:gz", "bz2": "w:bz2", "xz": "w:xz"}


def oracle_kind(member):
    """Map a tarfile member to the tool's kind taxonomy."""
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


def add_file(archive, name, data, mode=0o644, mtime=SANE_MTIME):
    """Append a regular-file member to an open tarfile."""
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = mode
    info.mtime = mtime
    archive.addfile(info, io.BytesIO(data))


def add_dir(archive, name, mode=0o755, mtime=SANE_MTIME):
    """Append a directory member to an open tarfile."""
    info = tarfile.TarInfo(name)
    info.type = tarfile.DIRTYPE
    info.mode = mode
    info.mtime = mtime
    archive.addfile(info)


def add_symlink(archive, name, target, mtime=SANE_MTIME):
    """Append a symlink member to an open tarfile."""
    info = tarfile.TarInfo(name)
    info.type = tarfile.SYMTYPE
    info.linkname = target
    info.mode = 0o777
    info.mtime = mtime
    archive.addfile(info)


def add_hardlink(archive, name, target, mtime=SANE_MTIME):
    """Append a hardlink member to an open tarfile."""
    info = tarfile.TarInfo(name)
    info.type = tarfile.LNKTYPE
    info.linkname = target
    info.mode = 0o644
    info.mtime = mtime
    archive.addfile(info)


class TarInspectToolTest(unittest.TestCase):
    """Shared fixture: a temp directory and a TarInspectTool scoped to it."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.tool = TarInspectTool(base_dir=self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def path(self, name):
        """Return an absolute path inside the temp directory."""
        return os.path.join(self.directory.name, name)

    def build(self, name, builder, compression=None, tar_format=tarfile.PAX_FORMAT):
        """Build an archive via a builder callback and return its path."""
        path = self.path(name)
        with tarfile.open(path, mode=COMPRESS_MODES[compression], format=tar_format) as archive:
            builder(archive)
        return path

    def audit(self, path):
        """Run audit_safety on an archive path inside the sandbox."""
        return self.tool.execute(mode="audit_safety", file_path=os.path.basename(path))

    def inspect(self, path):
        """Run inspect on an archive path inside the sandbox."""
        return self.tool.execute(mode="inspect", file_path=os.path.basename(path))

    def rules(self, result):
        """Return the {rule: severity} map of an audit result."""
        return {finding["rule"]: finding["severity"] for finding in result["findings"]}


class SeededOracleTest(TarInspectToolTest):
    """(a) inspect entries must match tarfile.getmembers() ground truth on 200 seeded archives."""

    def test_seeded_archives_match_tarfile_ground_truth(self):
        """Compare name/kind/size/mtime/mode for every entry of 200 seeded archives."""
        formats = [tarfile.USTAR_FORMAT, tarfile.PAX_FORMAT, tarfile.GNU_FORMAT]
        compressions = [None, "gz", "bz2", "xz"]
        for seed in range(200):
            with self.subTest(seed=seed):
                tar_format = formats[seed % len(formats)]
                compression = compressions[seed % len(compressions)]
                suffix = ".tar" if compression is None else f".tar.{compression}"
                path = self.build(f"seeded-{seed}{suffix}", self._seeded_builder(seed), compression, tar_format)
                result = self.inspect(path)
                self.assertEqual(result["status"], "success", result)
                with tarfile.open(path, mode="r:*") as archive:
                    members = archive.getmembers()
                self.assertEqual(result["entry_count"], len(members))
                self.assertFalse(result["entries_truncated"])
                self.assertEqual(len(result["entries"]), len(members))
                for got, member in zip(result["entries"], members, strict=True):
                    self.assertEqual(got["name"], member.name)
                    self.assertEqual(got["kind"], oracle_kind(member))
                    self.assertEqual(got["size"], member.size)
                    self.assertEqual(got["mtime"], int(member.mtime))
                    expected_letter = {"file": "-", "dir": "d", "symlink": "l", "hardlink": "h"}[oracle_kind(member)]
                    self.assertEqual(got["mode"][0], expected_letter)
                    self.assertEqual(got["mode"][1:], stat.filemode(member.mode)[1:])
                self.assertEqual(result["format"], "tar" if compression is None else f"tar.{compression}")
                total = sum(member.size for member in members if member.isfile())
                self.assertEqual(result["total_uncompressed"], total)

    @staticmethod
    def _seeded_builder(seed):
        """Deterministic archive layout mixing dirs, files, links, and unicode names."""

        def builder(archive):
            rng = random.Random(seed)  # noqa: S311 - deterministic test data, not crypto
            add_dir(archive, "root/")
            names = ["root/file0.txt", "root/data.bin", "root/deep/nested/item.log"]
            for index, name in enumerate(names):
                size = rng.randint(0, 4096)
                payload = bytes(rng.randrange(256) for _ in range(min(size, 512))) * (size // 512 + 1)
                add_file(
                    archive, name, payload[:size], mode=rng.choice([0o644, 0o755, 0o600]), mtime=SANE_MTIME + index
                )
            add_file(archive, "root/big.bin", b"\0" * 8192, mtime=SANE_MTIME)
            unicode_name = ["данные.txt", "文件.txt", "emoji🙂.txt"][seed % 3]
            add_file(archive, f"root/{unicode_name}", unicode_name.encode("utf-8") * 4, mtime=SANE_MTIME)
            add_symlink(archive, "root/link", "file0.txt")
            add_hardlink(archive, "root/hard", "root/file0.txt")

        return builder


class AttackCorpusTest(TarInspectToolTest):
    """(b) every crafted malicious archive must be flagged high with the correct rule."""

    def test_dotdot_shapes(self):
        """The classic '../evil' family must raise path_traversal_dotdot high."""
        for index, name in enumerate(["../evil.txt", "a/../../evil.txt", "a/b/c/../../../deep/evil.txt"]):
            with self.subTest(name=name):
                path = self.build(f"dotdot-{index}.tar", lambda archive, name=name: add_file(archive, name, b"x"))
                result = self.audit(path)
                self.assertEqual(self.rules(result).get("path_traversal_dotdot"), "high")
                self.assertFalse(result["extract_safe"])

    def test_absolute_shapes(self):
        """Absolute POSIX entry names must raise path_absolute high."""
        for index, name in enumerate(["/tmp/evil.txt", "/etc/passwd", "/usr/local/bin/x"]):  # noqa: S108 - archive member names
            with self.subTest(name=name):
                path = self.build(f"abs-{index}.tar", lambda archive, name=name: add_file(archive, name, b"x"))
                result = self.audit(path)
                self.assertEqual(self.rules(result).get("path_absolute"), "high")
                self.assertFalse(result["extract_safe"])

    def test_windows_shapes(self):
        """Windows drive and UNC names must raise windows_absolute high."""
        for index, name in enumerate(["C:\\Windows\\evil.dll", "C:/evil.txt", "\\\\server\\share\\evil"]):
            with self.subTest(name=name):
                path = self.build(f"win-{index}.tar", lambda archive, name=name: add_file(archive, name, b"x"))
                result = self.audit(path)
                self.assertEqual(self.rules(result).get("windows_absolute"), "high")

    def test_symlink_then_write_shapes(self):
        """The two-step symlink redirect must raise symlink_redirect high."""
        shapes = [
            [("x", "symlink", "/tmp"), ("x/pwn", "file", None)],  # noqa: S108 - archive member names
            [("d", "symlink", ".."), ("d/evil", "file", None)],
            [("s1", "symlink", "s2"), ("s2", "symlink", "/var"), ("s1/f", "file", None)],
        ]
        for index, shape in enumerate(shapes):
            with self.subTest(shape=shape):

                def builder(archive, shape=shape):
                    for name, kind, extra in shape:
                        if kind == "symlink":
                            add_symlink(archive, name, extra)
                        else:
                            add_file(archive, name, b"pwn")

                path = self.build(f"symredir-{index}.tar", builder)
                result = self.audit(path)
                self.assertEqual(self.rules(result).get("symlink_redirect"), "high")
                self.assertFalse(result["extract_safe"])

    def test_hardlink_out_shapes(self):
        """Hardlinks to absolute or escaping targets must raise hardlink_outside high."""
        for index, target in enumerate(["/etc/shadow", "../../etc/shadow", "C:/x"]):
            with self.subTest(target=target):
                path = self.build(
                    f"hardout-{index}.tar", lambda archive, target=target: add_hardlink(archive, "hl", target)
                )
                result = self.audit(path)
                self.assertEqual(self.rules(result).get("hardlink_outside"), "high")

    def test_device_shapes(self):
        """Device nodes must raise device_special high."""
        for index, kind_type in enumerate([tarfile.CHRTYPE, tarfile.BLKTYPE]):
            with self.subTest(kind_type=kind_type):

                def builder(archive, kind_type=kind_type):
                    info = tarfile.TarInfo("dev0")
                    info.type = kind_type
                    info.devmajor = 1
                    info.devminor = 3
                    info.mtime = SANE_MTIME
                    archive.addfile(info)

                path = self.build(f"dev-{index}.tar", builder)
                result = self.audit(path)
                self.assertEqual(self.rules(result).get("device_special"), "high")
                self.assertEqual(self.inspect(path)["entries"][0]["kind"], "dev")

    def test_setuid_shapes(self):
        """setuid/setgid mode bits must raise setuid_setgid high."""
        shapes = [(tarfile.REGTYPE, 0o4755), (tarfile.REGTYPE, 0o2755), (tarfile.DIRTYPE, 0o4755)]
        for index, (kind_type, mode) in enumerate(shapes):
            with self.subTest(mode=oct(mode)):

                def builder(archive, kind_type=kind_type, mode=mode):
                    info = tarfile.TarInfo("target0" if kind_type == tarfile.REGTYPE else "targetdir/")
                    info.type = kind_type
                    info.mode = mode
                    info.mtime = SANE_MTIME
                    if kind_type == tarfile.REGTYPE:
                        info.size = 1
                        archive.addfile(info, io.BytesIO(b"x"))
                    else:
                        archive.addfile(info)

                path = self.build(f"suid-{index}.tar", builder)
                result = self.audit(path)
                self.assertEqual(self.rules(result).get("setuid_setgid"), "high")
                self.assertIn("s", self.inspect(path)["entries"][0]["mode"])

    def test_duplicate_shapes(self):
        """Duplicate names must raise duplicate_entries high with the last-wins note."""
        for index, names in enumerate([["a.txt", "a.txt"], ["a.txt", "a.txt", "a.txt"], ["a.txt", "b.txt", "a.txt"]]):
            with self.subTest(names=names):

                def builder(archive, names=names):
                    for position, name in enumerate(names):
                        add_file(archive, name, f"content-{position}".encode())

                path = self.build(f"dup-{index}.tar", builder)
                result = self.audit(path)
                finding = next(item for item in result["findings"] if item["rule"] == "duplicate_entries")
                self.assertEqual(finding["severity"], "high")
                self.assertIn("last occurrence wins", finding["detail"])
                self.assertFalse(result["extract_safe"])

    def test_backslash_traversal_shapes(self):
        """Backslash traversal names must raise path_traversal_dotdot high."""
        for index, name in enumerate(["dir\\..\\evil.txt", "a\\..\\..\\x", "x\\..\\..\\evil"]):
            with self.subTest(name=name):
                path = self.build(f"bslash-{index}.tar", lambda archive, name=name: add_file(archive, name, b"x"))
                result = self.audit(path)
                rules = self.rules(result)
                self.assertEqual(rules.get("path_traversal_dotdot"), "high")
                self.assertEqual(rules.get("backslash_in_name"), "medium")

    def test_huge_declared_size_shapes(self):
        """Entries declaring multi-GB sizes must raise entry_oversize high."""
        for index, (name, size) in enumerate([("big.bin", 2**31), ("huge.dat", 3 * 2**30), ("/abs/big", 2**32)]):
            with self.subTest(name=name):
                path = self.craft_raw_header_archive(f"huge-{index}.tar", name, size)
                result = self.audit(path)
                self.assertEqual(self.rules(result).get("entry_oversize"), "high")
                inspect = self.inspect(path)
                self.assertEqual(inspect["entries"][0]["size"], size)
                self.assertFalse(result["extract_safe"])

    def craft_raw_header_archive(self, filename, name, declared_size):
        """Hand-craft a tar header declaring a size with no data blocks behind it."""
        info = tarfile.TarInfo(name)
        info.size = declared_size
        info.mtime = SANE_MTIME
        header = info.tobuf(format=tarfile.GNU_FORMAT)
        path = self.path(filename)
        with open(path, "wb") as stream:
            stream.write(header)
            stream.write(b"\0" * 1024)
        return path


class AdditionalRuleTest(TarInspectToolTest):
    """Remaining audit rules: encoding weirdness, fifo, mtime, bombs, sparse, benign links."""

    def test_control_character_names(self):
        """Control characters in names must raise name_control_chars high."""
        path = self.build("ctrl.tar", lambda archive: add_file(archive, "ev\x07il.txt", b"x"))
        self.assertEqual(self.rules(self.audit(path)).get("name_control_chars"), "high")

    def test_rtl_override_names(self):
        """U+202E RTL override must raise name_rtl_override high."""
        path = self.build("rtlo.tar", lambda archive: add_file(archive, "ev\u202eil.txt", b"x"))
        self.assertEqual(self.rules(self.audit(path)).get("name_rtl_override"), "high")

    def test_surrogate_names(self):
        """Undecodable byte names must raise name_invalid_utf8 medium."""
        path = self.build(
            "surr.tar", lambda archive: add_file(archive, "bad\udcfe.txt", b"x"), tar_format=tarfile.GNU_FORMAT
        )
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("name_invalid_utf8"), "medium")

    def test_fifo_flagged(self):
        """FIFO entries must be reported as kind fifo with a medium finding."""
        path = self.build(
            "fifo.tar",
            lambda archive: archive.addfile(type_info(tarfile.FIFOTYPE, "pipe0")),
        )
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("fifo_special"), "medium")
        self.assertEqual(self.inspect(path)["entries"][0]["kind"], "fifo")

    def test_mtime_anomalies(self):
        """Far-past and far-future mtimes must raise mtime_anomaly medium."""
        path = self.build(
            "mtime.tar",
            lambda archive: (
                add_file(archive, "old.txt", b"x", mtime=60),
                add_file(archive, "future.txt", b"x", mtime=2**40),
            ),
            tar_format=tarfile.GNU_FORMAT,
        )
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("mtime_anomaly"), "medium")

    def test_compression_bomb_ratio(self):
        """A highly compressible archive must raise compression_bomb high."""
        path = self.build(
            "bomb.tar.gz", lambda archive: add_file(archive, "zeros.bin", b"\0" * (5 * 1024 * 1024)), "gz"
        )
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("compression_bomb"), "high")
        self.assertGreater(self.inspect(path)["compression_ratio"], 100)

    def test_compression_ratio_threshold_option(self):
        """The bomb threshold is configurable."""
        payload = (random.Random(99).randbytes(100) * 82)[:8192]  # noqa: S311 - deterministic test data, not crypto
        path = self.build("mild.tar.gz", lambda archive: add_file(archive, "pad.bin", payload), "gz")
        strict = TarInspectTool(base_dir=self.directory.name, max_compression_ratio=2.0)
        result = strict.execute(mode="audit_safety", file_path="mild.tar.gz")
        self.assertEqual(self.rules(result).get("compression_bomb"), "high")
        self.assertEqual(self.rules(self.audit(path)).get("compression_bomb"), None)

    def test_gnu_sparse_note(self):
        """GNU sparse entries stay kind file and carry an info note."""
        path = self.build(
            "sparse.tar",
            lambda archive: archive.addfile(
                type_info(tarfile.GNUTYPE_SPARSE, "sparse.bin", size=8), io.BytesIO(b"\0" * 8)
            ),
            tar_format=tarfile.GNU_FORMAT,
        )
        result = self.audit(path)
        self.assertIn("sparse_file_headers", self.rules(result))
        self.assertEqual(self.inspect(path)["entries"][0]["kind"], "file")

    def test_benign_symlink_and_hardlink_clean(self):
        """In-tree symlinks and hardlinks must not raise findings."""
        path = self.build(
            "links.tar",
            lambda archive: (
                add_file(archive, "root/file0.txt", b"data"),
                add_symlink(archive, "root/link", "file0.txt"),
                add_hardlink(archive, "root/hard", "root/file0.txt"),
            ),
        )
        result = self.audit(path)
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["extract_safe"])

    def test_extension_mismatch_finding(self):
        """A gzip archive named .tar must still sniff as tar.gz and note the mismatch."""
        source = self.build("real.tar.gz", lambda archive: add_file(archive, "file.txt", b"data"), "gz")
        renamed = self.path("disguised.tar")
        os.replace(source, renamed)
        result = self.inspect(renamed)
        self.assertEqual(result["format"], "tar.gz")
        findings = {finding["rule"] for finding in result["findings"]}
        self.assertIn("extension_mismatch", findings)

    def test_dotdot_flagged_even_when_it_lands_inside(self):
        """Policy: any '..' is high even when normpath would collapse it inside the dest."""
        path = self.build("inside.tar", lambda archive: add_file(archive, "a/../b.txt", b"x"))
        self.assertEqual(self.rules(self.audit(path)).get("path_traversal_dotdot"), "high")


def type_info(kind_type, name, size=0, mode=0o644):
    """Build a TarInfo with an explicit typeflag chip and no data payload."""
    info = tarfile.TarInfo(name)
    info.type = kind_type
    info.size = size
    info.mode = mode
    info.mtime = SANE_MTIME
    return info


class BenignCorpusTest(TarInspectToolTest):
    """(b) 200 benign archives must produce zero high findings and extract_safe=True."""

    def test_benign_corpus_zero_highs(self):
        """Audit 200 varied benign archives: no high findings anywhere."""
        formats = [tarfile.USTAR_FORMAT, tarfile.PAX_FORMAT, tarfile.GNU_FORMAT]
        compressions = [None, "gz", "bz2", "xz"]
        for seed in range(200):
            with self.subTest(seed=seed):
                compression = compressions[seed % len(compressions)]
                suffix = ".tar" if compression is None else f".tar.{compression}"
                path = self.build(f"benign-{seed}{suffix}", self._benign_builder(seed), compression, formats[seed % 3])
                result = self.audit(path)
                self.assertEqual(result["status"], "success", result)
                highs = [finding for finding in result["findings"] if finding["severity"] == "high"]
                self.assertEqual(highs, [], f"seed {seed} produced highs: {highs}")
                self.assertTrue(result["extract_safe"])

    @staticmethod
    def _benign_builder(seed):
        """A benign layout: no '..', no backslash, no absolute names, sane mtimes and modes."""

        def builder(archive):
            rng = random.Random(10_000 + seed)  # noqa: S311 - deterministic test data, not crypto
            add_dir(archive, "app/")
            add_dir(archive, "app/assets/")
            payload = rng.randbytes(rng.randint(1, 4096))
            add_file(archive, "app/README.md", b"# readme\n", mtime=SANE_MTIME + 1)
            add_file(archive, "app/assets/logo.bin", payload, mtime=SANE_MTIME + 2)
            add_file(archive, "app/assets/deep/data.dat", rng.randbytes(2048), mode=0o600, mtime=SANE_MTIME + 3)
            add_file(archive, "app/note with space.txt", b"ok", mtime=SANE_MTIME + 4)
            if seed % 5 == 0:
                add_file(archive, "app/数据.txt", "数据".encode(), mtime=SANE_MTIME + 5)
            if seed % 3 == 0:
                add_symlink(archive, "app/latest", "README.md")
            if seed % 4 == 0:
                add_hardlink(archive, "app/hard-alias", "app/README.md")

        return builder


class PlanExtractionTest(TarInspectToolTest):
    """(c) resolved paths must match os.path.normpath semantics; escapes must be detected."""

    PLAIN_NAMES: ClassVar[list[str]] = [
        "file.txt",
        "a/b/c.txt",
        "./x.txt",
        "a/./b.txt",
        "a/../b.txt",
        "a/b/../c/../d.txt",
        "../escape.txt",
        "a/../../evil.txt",
        "a/b/c/../../../../out.txt",
        "/tmp/absolute.txt",  # noqa: S108 - archive member name
        "/etc/passwd",
        "plain\\name.txt",
        "dir\\..\\evil.txt",
        "..\\top.txt",
        "deep/" + "n/" * 6 + "leaf.txt",
    ]
    DESTS: ClassVar[list[str]] = ["out", "/tmp/extract", "rel/deep", "."]  # noqa: S108 - simulated destination names

    def test_plain_resolution_matches_normpath(self):
        """140 plain cases: resolved_path equals the os.path normpath oracle."""
        cases = [(name, dest) for dest in self.DESTS for name in self.PLAIN_NAMES]
        cases = cases * (150 // len(cases) + 1)
        self.assertEqual(len(cases) >= 150, True)
        for name, dest in cases[:140]:
            with self.subTest(name=name, dest=dest):
                archive = self.plan_archive([(name, "file", None)])
                result = self.tool.execute(mode="plan_extraction", file_path=archive, dest_dir=dest)
                self.assertEqual(result["status"], "success", result)
                plan = result["plans"][0]
                posix_name = name.replace("\\", "/")
                root = os.path.normpath(dest.replace("\\", "/")) if dest.replace("\\", "/") != "." else "."
                if posix_name.startswith("/"):
                    expected = os.path.normpath(posix_name)
                else:
                    expected = os.path.normpath(os.path.join(root, posix_name))
                self.assertEqual(plan["resolved_path"], expected)
                self.assertEqual(plan["escapes_dest"], oracle_escape(expected, root))

    def test_symlink_redirect_chains(self):
        """10 redirect cases: entries written through symlinked parents land where redirected."""
        scenarios = [
            ([("x", "symlink", "/tmp"), ("x/pwn", "file", None)], "out", "/tmp/pwn", True),  # noqa: S108 - simulated paths
            ([("d", "symlink", ".."), ("d/evil", "file", None)], "out", "evil", True),
            ([("s1", "symlink", "s2"), ("s2", "symlink", "/var"), ("s1/f", "file", None)], "out", "/var/f", True),
            ([("r", "symlink", "sub"), ("r/inner.txt", "file", None)], "out", "out/sub/inner.txt", False),
            ([("q", "symlink", "s"), ("q/z", "file", None)], "out", "out/s/z", False),
        ]
        for index, (shape, dest, expected, escapes) in enumerate(scenarios):
            with self.subTest(index=index):
                archive = self.plan_archive(shape)
                result = self.tool.execute(mode="plan_extraction", file_path=archive, dest_dir=dest)
                plan = result["plans"][-1]
                self.assertEqual(plan["resolved_path"], expected)
                self.assertEqual(plan["escapes_dest"], escapes)
                if escapes:
                    self.assertIn(plan["name"], result["escaping_entries"])
                else:
                    self.assertNotIn(plan["name"], result["escaping_entries"])

    def test_dotdot_lands_where_normpath_says(self):
        """'a/../b' must resolve inside the dest while '../b' escapes it."""
        archive = self.plan_archive([("a/../b.txt", "file", None), ("../b.txt", "file", None)])
        result = self.tool.execute(mode="plan_extraction", file_path=archive, dest_dir="out")
        first, second = result["plans"]
        self.assertEqual(first["resolved_path"], os.path.normpath("out/b.txt"))
        self.assertFalse(first["escapes_dest"])
        self.assertTrue(second["escapes_dest"])

    def test_absolute_entry_ignores_relative_dest(self):
        """An absolute entry lands at its own path, escaping a relative dest."""
        archive = self.plan_archive([("/tmp/evil.txt", "file", None)])  # noqa: S108 - archive member name
        result = self.tool.execute(mode="plan_extraction", file_path=archive, dest_dir="out")
        plan = result["plans"][0]
        self.assertEqual(plan["resolved_path"], "/tmp/evil.txt")  # noqa: S108 - simulated landing path
        self.assertTrue(plan["escapes_dest"])

    def test_absolute_dest_contains_absolute_landing(self):
        """Absolute landings inside an absolute dest are not escapes."""
        archive = self.plan_archive([("/tmp/extract/keep.txt", "file", None), ("/tmp/evil.txt", "file", None)])  # noqa: S108 - archive member names
        result = self.tool.execute(mode="plan_extraction", file_path=archive, dest_dir="/tmp/extract")  # noqa: S108 - simulated destination
        keep, evil = result["plans"]
        self.assertFalse(keep["escapes_dest"])
        self.assertTrue(evil["escapes_dest"])

    def plan_archive(self, shape, filename="plan.tar"):
        """Build an archive from (name, kind, target) triples for planning tests."""

        def builder(archive):
            for name, kind, target in shape:
                if kind == "symlink":
                    add_symlink(archive, name, target)
                elif kind == "dir":
                    add_dir(archive, name)
                else:
                    add_file(archive, name, b"payload")

        return self.build(filename, builder)


def oracle_escape(resolved, root):
    """os.path.relpath-based oracle for whether resolved lands outside root."""
    if os.path.isabs(resolved) != os.path.isabs(root):
        return True
    relative = os.path.relpath(resolved, root)
    return relative == ".." or relative.startswith(".." + os.sep)


class TarBinaryCrossCheckTest(TarInspectToolTest):
    """(d) the real tar binary's -tvf kind letters must agree with our kinds on 50 archives."""

    def test_tar_tvf_kind_letters_match(self):
        """Compare per-line kind letters from tar -tvf against inspect entries."""
        formats = [tarfile.USTAR_FORMAT, tarfile.GNU_FORMAT, tarfile.PAX_FORMAT]
        compressions = [None, "gz", "bz2", "xz"]
        letter_for = {"file": "-", "dir": "d", "symlink": "l", "hardlink": "h"}
        for seed in range(50):
            with self.subTest(seed=seed):
                compression = compressions[seed % len(compressions)]
                suffix = ".tar" if compression is None else f".tar.{compression}"
                path = self.build(f"cross-{seed}{suffix}", self._cross_builder(seed), compression, formats[seed % 3])
                listing = subprocess.run(  # noqa: S603 - fixed system tar used as the oracle
                    [  # noqa: S607 - tar resolved from PATH is the point of this oracle
                        "tar",
                        "-tvf",
                        path,
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout
                lines = [line for line in listing.splitlines() if line.strip()]
                result = self.inspect(path)
                self.assertEqual(len(lines), result["entry_count"])
                for line, entry in zip(lines, result["entries"], strict=True):
                    self.assertEqual(line[0], letter_for[entry["kind"]], f"line={line!r} entry={entry}")

    @staticmethod
    def _cross_builder(seed):
        """Deterministic mixed-kind layout with short ASCII names."""

        def builder(archive):
            rng = random.Random(20_000 + seed)  # noqa: S311 - deterministic test data, not crypto
            add_dir(archive, "d0/")
            add_file(archive, "d0/f0.txt", rng.randbytes(64), mtime=SANE_MTIME)
            add_file(archive, "d0/f1.log", rng.randbytes(128), mtime=SANE_MTIME)
            add_symlink(archive, "d0/s0", "f0.txt")
            add_hardlink(archive, "d0/h0", "d0/f0.txt")
            if seed % 2 == 0:
                add_dir(archive, "d0/sub/")
                add_file(archive, "d0/sub/f2.bin", rng.randbytes(32), mtime=SANE_MTIME)

        return builder


class PathologicalInputTest(TarInspectToolTest):
    """(e) corrupted archives, caps, and the 100k-entry archive must stay structured and fast."""

    def write_raw(self, name, data):
        """Write raw bytes as a file in the sandbox."""
        path = self.path(name)
        with open(path, "wb") as stream:
            stream.write(data)
        return path

    def test_empty_file_is_structured_error(self):
        """An empty file is rejected with a structured validation error."""
        path = self.write_raw("empty.tar", b"")
        result = self.inspect(path)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_zero_block_archives_are_valid_empty(self):
        """Streams of zero blocks are valid empty archives for tarfile and tar."""
        import gzip as gzip_module

        for index, blob in enumerate([(b"\0" * 512, "plain512"), (b"\0" * 1024, "plain1024"), (gzip_module.compress(b"\0" * 1024), "gz1024")]):
            with self.subTest(case=blob[1]):
                path = self.write_raw(f"zeros-{blob[1]}.tar", blob[0])
                result = self.inspect(path)
                self.assertEqual(result["status"], "success", result)
                self.assertEqual(result["entry_count"], 0)
                self.assertEqual(result["entries"], [])
        # Truncated zero streams shorter than one block still fail structured.
        result = self.inspect(self.write_raw("short-zeros.tar", b"\0" * 300))
        self.assertEqual(result["status"], "error")
        self.assertIn("tar header", result["error"])

    def test_garbage_is_structured_error(self):
        """Random garbage bytes fail header parsing without raising."""
        rng = random.Random(7)  # noqa: S311 - deterministic test data, not crypto
        path = self.write_raw("garbage.tar", rng.randbytes(512 * 3))
        result = self.inspect(path)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_truncated_tar_is_structured_error(self):
        """A tar cut before the first header ends is rejected."""
        full = self.build("full.tar", lambda archive: add_file(archive, "file.txt", b"data" * 100))
        with open(full, "rb") as stream:
            data = stream.read()
        path = self.write_raw("cut.tar", data[:300])
        result = self.inspect(path)
        self.assertEqual(result["status"], "error")
        self.assertIn("tar header", result["error"])

    def test_truncated_mid_data_archive_stays_structured(self):
        """A tar cut mid-data either parses partially or errors, but never crashes."""
        full = self.build(
            "full2.tar",
            lambda archive: (add_file(archive, "one.txt", b"1" * 700), add_file(archive, "two.txt", b"2" * 700)),
        )
        with open(full, "rb") as stream:
            data = stream.read()
        path = self.write_raw("half.tar", data[:1024])
        result = self.inspect(path)
        self.assertIn(result["status"], {"success", "error"})
        if result["status"] == "success":
            self.assertEqual(result["entry_count"], 1)

    def test_corrupt_gzip_is_structured_error(self):
        """A gzip stream with trailing garbage fails as corrupt, not as a crash."""
        source = self.build("ok.tar.gz", lambda archive: add_file(archive, "file.txt", b"data"), "gz")
        with open(source, "rb") as stream:
            head = stream.read()
        path = self.write_raw("bad.tar.gz", head[:6] + b"\x00garbagegarbage")
        result = self.inspect(path)
        self.assertEqual(result["status"], "error")
        self.assertIn(result["error_type"], {"validation_error", "operation_error"})

    def test_scan_budget_guard(self):
        """Decompressed streams beyond max_scan_bytes return a too_large error."""
        self.build("wide.tar.gz", lambda archive: add_file(archive, "pad.bin", b"A" * 8192), "gz")
        strict = TarInspectTool(base_dir=self.directory.name, max_scan_bytes=2048)
        result = strict.execute(mode="inspect", file_path="wide.tar.gz")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "too_large")

    def test_base64_input_round_trip(self):
        """A base64 payload inspects identically to the same archive on disk."""
        path = self.build("b64.tar.gz", lambda archive: add_file(archive, "file.txt", b"payload"), "gz")
        with open(path, "rb") as stream:
            payload = base64.b64encode(stream.read()).decode("ascii")
        result = self.tool.execute(mode="inspect", base64_archive=payload)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["format"], "tar.gz")
        self.assertEqual(result["entries"][0]["name"], "file.txt")
        self.assertEqual(result["source"], "base64")

    def test_base64_size_cap(self):
        """Oversized base64 payloads are rejected by the cap."""
        payload = base64.b64encode(b"A" * 64).decode("ascii")
        strict = TarInspectTool(base_dir=self.directory.name, max_base64_bytes=16)
        result = strict.execute(mode="inspect", base64_archive=payload)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_base64_bytes", result["error"])

    def test_base64_validation(self):
        """Invalid base64 text is a validation error."""
        result = self.tool.execute(mode="inspect", base64_archive="!!!not-base64!!!")
        self.assertEqual(result["status"], "error")
        self.assertIn("base64", result["error"])

    def test_input_contract_errors(self):
        """Mode, XOR input, and dest_dir validation all return structured errors."""
        self.assertEqual(self.tool.execute(mode="nope")["error_type"], "validation_error")
        self.assertIn("exactly one", self.tool.execute(mode="inspect")["error"])
        both = self.tool.execute(mode="inspect", file_path="a.tar", base64_archive="AAAA")
        self.assertIn("exactly one", both["error"])
        missing_dest = self.tool.execute(mode="plan_extraction", file_path="a.tar")
        self.assertIn("dest_dir", missing_dest["error"])
        missing = self.tool.execute(mode="inspect", file_path="missing.tar")
        self.assertEqual(missing["error_type"], "validation_error")

    def test_audit_is_deterministic(self):
        """Repeated audits of the same archive return identical results."""
        path = self.build(
            "determ.tar",
            lambda archive: (
                add_file(archive, "../evil", b"x"),
                add_symlink(archive, "s", "/tmp"),  # noqa: S108 - archive member target
                add_file(archive, "s/f", b"y"),
            ),
        )
        first = self.audit(path)
        second = self.audit(path)
        self.assertEqual(first, second)

    def test_hundred_thousand_entries_within_cap_and_time(self):
        """A 100k-entry archive stays under max_scan_entries and finishes quickly."""
        path = self.path("huge-count.tar")
        started = time.monotonic()
        with tarfile.open(path, "w") as archive:
            for index in range(100_000):
                info = tarfile.TarInfo(f"e{index}.txt")
                info.size = 0
                info.mtime = SANE_MTIME
                archive.addfile(info)
        build_seconds = time.monotonic() - started
        self.assertLess(build_seconds, 120)
        started = time.monotonic()
        result = self.inspect(path)
        inspect_seconds = time.monotonic() - started
        self.assertLess(inspect_seconds, 60, f"inspect took {inspect_seconds:.1f}s")
        self.assertEqual(result["entry_count"], 100_000)
        self.assertEqual(len(result["entries"]), 200)
        self.assertTrue(result["entries_truncated"])
        audit = self.audit(path)
        self.assertEqual(self.rules(audit).get("excessive_entry_count"), "medium")

    def test_read_only_contract_no_writes(self):
        """Running every mode leaves the sandbox with only the archive file present."""
        path = self.build("ro.tar", lambda archive: add_file(archive, "file.txt", b"data"))
        before = sorted(os.listdir(self.directory.name))
        self.inspect(path)
        self.audit(path)
        self.tool.execute(mode="plan_extraction", file_path="ro.tar", dest_dir="out")
        self.assertEqual(sorted(os.listdir(self.directory.name)), before)


class SelfReviewRegressionTest(TarInspectToolTest):
    """Regressions for defects found by the hostile self-review differential battery."""

    def test_fractional_and_negative_pax_mtimes_match_tarfile(self):
        """PAX fractional mtimes must be reported exactly as tarfile reports them."""

        def builder(archive):
            for name, mtime in [("frac.txt", 1690000000.25), ("negfrac.txt", -12345.5), ("plain.txt", 1690000000)]:
                info = tarfile.TarInfo(name)
                info.size = 1
                info.mode = 0o644
                info.mtime = mtime
                archive.addfile(info, io.BytesIO(b"x"))

        path = self.build("frac-mtime.tar", builder, tar_format=tarfile.PAX_FORMAT)
        with tarfile.open(path) as archive:
            members = archive.getmembers()
        result = self.inspect(path)
        for got, member in zip(result["entries"], members, strict=True):
            self.assertEqual(got["mtime"], member.mtime)
        self.assertEqual(result["entries"][0]["mtime"], 1690000000.25)
        self.assertEqual(result["entries"][1]["mtime"], -12345.5)
        self.assertIsInstance(result["entries"][2]["mtime"], int)

    def test_inspect_output_json_safe_with_surrogates(self):
        """Names AND link targets with undecodable bytes must serialize to UTF-8 JSON."""

        def builder(archive):
            info = tarfile.TarInfo("bad\udcfe.txt")
            info.size = 1
            info.mode = 0o644
            info.mtime = SANE_MTIME
            archive.addfile(info, io.BytesIO(b"x"))
            add_symlink(archive, "lnk", "t\udcfeget")

        path = self.build("surr-out.tar", builder, tar_format=tarfile.GNU_FORMAT)
        result = self.inspect(path)
        json.dumps(result, ensure_ascii=False).encode("utf-8")  # must not raise
        self.assertNotIn("\udcfe", result["entries"][1]["link_target"])
        plan = self.tool.execute(mode="plan_extraction", file_path="surr-out.tar", dest_dir="out")
        json.dumps(plan, ensure_ascii=False).encode("utf-8")

    def test_deep_redirect_resolved_path_matches_normpath(self):
        """A >512-component name written through a symlink keeps its full landing path."""

        def builder(archive):
            add_symlink(archive, "r", "..")
            add_file(archive, "r/" + "n/" * 700 + "f.txt", b"x")

        path = self.build("deep-redir.tar", builder, tar_format=tarfile.PAX_FORMAT)
        result = self.tool.execute(mode="plan_extraction", file_path="deep-redir.tar", dest_dir="out")
        expected = os.path.normpath(os.path.join("out", "../" + "n/" * 700 + "f.txt"))
        self.assertEqual(result["plans"][-1]["resolved_path"], expected)
        self.assertTrue(result["plans"][-1]["escapes_dest"])
        self.assertEqual(self.rules(self.audit(path)).get("symlink_redirect"), "high")

    def test_symlink_loop_resolved_path(self):
        """A symlink loop resolves literally after the first revisited link, not to the dest root."""

        def builder(archive):
            add_symlink(archive, "loop1", "loop2")
            add_symlink(archive, "loop2", "loop1")
            add_file(archive, "loop1/x", b"x")

        path = self.build("loop.tar", builder, tar_format=tarfile.PAX_FORMAT)
        result = self.tool.execute(mode="plan_extraction", file_path="loop.tar", dest_dir="out")
        self.assertEqual(result["plans"][-1]["resolved_path"], "out/loop1/x")
        self.assertFalse(result["plans"][-1]["escapes_dest"])
        self.assertEqual(self.rules(self.audit(path)).get("symlink_redirect"), None)

    def test_absolute_name_redirect_landing(self):
        """Absolute entry names keep their absoluteness across symlink redirects."""

        def builder(archive):
            add_symlink(archive, "/tmp/s", "..")
            add_file(archive, "/tmp/s/evil.txt", b"x")  # noqa: S108 - archive member names

        path = self.build("abs-redir.tar", builder, tar_format=tarfile.PAX_FORMAT)
        result = self.tool.execute(mode="plan_extraction", file_path="abs-redir.tar", dest_dir="out")
        self.assertEqual(result["plans"][-1]["resolved_path"], "/evil.txt")
        self.assertTrue(result["plans"][-1]["escapes_dest"])

    def test_verydeep_symlink_redirect_flagged(self):
        """Redirects through symlinks named deeper than 512 components are still caught."""

        def builder(archive):
            deep = "b/" * 520
            add_symlink(archive, deep + "out", "/tmp")  # noqa: S108 - archive member target
            add_file(archive, deep + "out/pwn", b"x")

        path = self.build("verydeep.tar", builder, tar_format=tarfile.PAX_FORMAT)
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("symlink_redirect"), "high")
        self.assertFalse(result["extract_safe"])

    def test_walk_budget_fails_closed(self):
        """Paths whose redirect walk exceeds the step budget are flagged, never truncated."""

        def builder(archive):
            add_symlink(archive, "s", "real")
            add_file(archive, "s/" + "a/" * 70_000 + "f.txt", b"x")

        path = self.build("budget.tar", builder, tar_format=tarfile.PAX_FORMAT)
        result = self.audit(path)
        self.assertEqual(self.rules(result).get("resolution_budget_exceeded"), "high")
        self.assertFalse(result["extract_safe"])
        plan = self.tool.execute(mode="plan_extraction", file_path="budget.tar", dest_dir="out")
        last = plan["plans"][-1]
        self.assertTrue(last.get("resolution_incomplete"))
        self.assertTrue(last["escapes_dest"])
        self.assertIn(last["name"], plan["escaping_entries"])

    def test_duplicate_scan_is_not_quadratic(self):
        """50k entries with 25k distinct duplicate names audit in bounded time."""
        path = self.path("many-dups.tar")
        started = time.monotonic()
        with tarfile.open(path, "w") as archive:
            for repeat in range(2):
                for index in range(25_000):
                    info = tarfile.TarInfo(f"item-{index:06d}.txt")
                    info.size = 0
                    info.mtime = SANE_MTIME
                    archive.addfile(info)
        self.assertLess(time.monotonic() - started, 120)
        started = time.monotonic()
        result = self.audit(path)
        self.assertLess(time.monotonic() - started, 30, "duplicate tracking must stay near-linear")
        finding = next(item for item in result["findings"] if item["rule"] == "duplicate_entries")
        self.assertEqual(finding["count"], 25_000)

    def test_deep_name_audit_stays_fast(self):
        """Deep-named entries with a symlink present audit without a per-step rebuild blowup."""
        path = self.path("deepnames.tar")
        started = time.monotonic()
        with tarfile.open(path, "w", format=tarfile.PAX_FORMAT) as archive:
            add_symlink(archive, "r", "sub")
            for index in range(5_000):
                info = tarfile.TarInfo(f"r/n/{'d/' * 700}f{index}.txt")
                info.size = 0
                info.mtime = SANE_MTIME
                archive.addfile(info)
        self.assertLess(time.monotonic() - started, 120)
        started = time.monotonic()
        result = self.audit(path)
        self.assertLess(time.monotonic() - started, 60)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["entry_count"], 5_001)

    def test_base64_mime_wrapped_payload(self):
        """base64 wrapped in newlines (MIME style) decodes like the unwrapped form."""
        path = self.build("mime-src.tar", lambda archive: add_file(archive, "file.txt", b"data"))
        with open(path, "rb") as stream:
            encoded = base64.b64encode(stream.read()).decode("ascii")
        wrapped = "\n".join(encoded[index : index + 76] for index in range(0, len(encoded), 76))
        result = self.tool.execute(mode="inspect", base64_archive=wrapped)
        self.assertEqual(result["status"], "success", result)
        self.assertEqual(result["entries"][0]["name"], "file.txt")

    def test_deep_gnu_longname_chain_is_structured_error(self):
        """A 2000-deep GNU longname chain (stdlib raises RecursionError) stays structured."""
        long_name = "chain-target.txt"
        info = tarfile.TarInfo("real.txt")
        info.size = 0
        info.mtime = SANE_MTIME
        blob = tarfile.TarInfo("././@LongLink")
        blob.type = tarfile.GNUTYPE_LONGNAME
        blob.size = len(long_name) + 1
        blob.mtime = SANE_MTIME
        header = blob.tobuf(format=tarfile.GNU_FORMAT)
        data = long_name.encode() + b"\0"
        pad = b"\0" * ((-len(data)) % 512)
        link = header + data + pad
        path = self.path("chain.tar")
        with open(path, "wb") as stream:
            for _ in range(2000):
                stream.write(link)
            stream.write(info.tobuf(format=tarfile.GNU_FORMAT))
            stream.write(b"\0" * 1024)
        with self.assertRaises((tarfile.TarError, RecursionError)):  # stdlib oracle itself fails here
            with tarfile.open(path) as archive:
                len(archive.getmembers())
        result = self.inspect(path)
        self.assertEqual(result["status"], "error")
        self.assertIn(result["error_type"], {"validation_error", "operation_error"})


class SecondPassRegressionTest(TarInspectToolTest):
    """Second hostile pass: wider field parity, deeper attacks, corruption sweep."""

    # -- (a) 250 fresh seeded archives, full field-by-field parity -------------
    def test_seeded_field_parity_250(self):
        """uname/gname/uid/gid/link/pax_headers parity on fresh seeded archives."""
        formats = [tarfile.USTAR_FORMAT, tarfile.PAX_FORMAT, tarfile.GNU_FORMAT]
        compressions = [None, None, "gz", "bz2", "xz"]
        checked = 0
        for seed in range(250):
            with self.subTest(seed=seed):
                tar_format = formats[seed % len(formats)]
                compression = compressions[seed % len(compressions)]
                suffix = ".tar" if compression is None else f".tar.{compression}"
                try:
                    path = self.build(f"sp2-{seed}{suffix}", self._second_pass_builder(seed), compression, tar_format)
                except ValueError:
                    continue  # ustar refuses >100-char names; tarfile oracle agrees
                result = self.inspect(path)
                self.assertEqual(result["status"], "success", result)
                with tarfile.open(path, mode="r:*") as archive:
                    members = archive.getmembers()
                self.assertEqual(result["entry_count"], len(members))
                for got, member in zip(result["entries"], members, strict=True):
                    self.assertEqual(got["name"], member.name)
                    self.assertEqual(got["kind"], oracle_kind(member))
                    self.assertEqual(got["size"], member.size)
                    self.assertEqual(got["uid"], member.uid)
                    self.assertEqual(got["gid"], member.gid)
                    self.assertEqual(got["uname"], member.uname or "")
                    self.assertEqual(got["gname"], member.gname or "")
                    expected_mtime = int(member.mtime) if float(member.mtime).is_integer() else member.mtime
                    self.assertEqual(got["mtime"], expected_mtime)
                    expected_letter = {
                        "file": "-", "dir": "d", "symlink": "l", "hardlink": "h",
                        "fifo": "p", "other": "?",
                        "dev": "c" if member.ischr() else "b",
                    }[oracle_kind(member)]
                    self.assertEqual(got["mode"][0], expected_letter)
                    self.assertEqual(got["mode"][1:], stat.filemode(member.mode)[1:])
                    self.assertEqual(got["link_target"], member.linkname or None)
                    if member.pax_headers and len(member.pax_headers) <= 16:
                        bounded = {key: value[:200] for key, value in sorted(member.pax_headers.items())}
                        self.assertEqual(got.get("pax_headers"), bounded)
                    else:
                        self.assertNotIn("pax_headers", got)
                checked += 1
        self.assertGreater(checked, 150)

    @staticmethod
    def _second_pass_builder(seed):
        """Deterministic second-pass layout: pax attributes, long names, odd metadata."""

        def builder(archive):
            rng = random.Random(31000 + seed)  # noqa: S311 - deterministic test data
            for index in range(rng.randint(1, 6)):
                roll = rng.random()
                if roll < 0.4:
                    info = tarfile.TarInfo(f"file{index}.txt")
                    payload = bytes(rng.randrange(256) for _ in range(rng.randint(0, 60)))
                    info.size = len(payload)
                    info.mode = rng.choice([0o644, 0o755, 0o4755, 0o2750, 0o1777])
                    info.mtime = rng.choice([SANE_MTIME, 0, 1, 2**31 - 1])
                    info.uid = rng.randint(0, 60000)
                    info.gid = rng.randint(0, 60000)
                    info.uname = rng.choice(["root", "user 一", "", "u" * 30])
                    info.gname = rng.choice(["wheel", "", "g" * 30])
                    if rng.random() < 0.5:
                        info.pax_headers = {"atime": "1575800000.123456789", "ctime": "1575800001.5"}
                    archive.addfile(info, io.BytesIO(payload))
                elif roll < 0.6:
                    add_dir(archive, f"d{index}/")
                elif roll < 0.75:
                    add_symlink(archive, f"sym{index}", rng.choice(["t", "../up", "/abs", "a/b/c"]))
                elif roll < 0.85:
                    add_hardlink(archive, f"hard{index}", "file0.txt")
                elif roll < 0.92:
                    info = tarfile.TarInfo(f"dev{index}")
                    info.type = rng.choice([tarfile.CHRTYPE, tarfile.BLKTYPE])
                    info.devmajor, info.devminor = 1, 3
                    info.mode = rng.choice([0o644, 0o4777])
                    info.mtime = SANE_MTIME
                    archive.addfile(info)
                else:
                    info = tarfile.TarInfo("L" * 210 + f"/long{index}.txt")  # >200 chars: needs pax/gnu
                    info.size = 3
                    info.mtime = SANE_MTIME
                    archive.addfile(info, io.BytesIO(b"abc"))

        return builder

    # -- pax atime/ctime attributes are surfaced per entry ---------------------
    def test_pax_attributes_surfaced(self):
        """atime/ctime pax attributes appear on the entry as a bounded map."""
        def builder(archive):
            info = tarfile.TarInfo("f.txt")
            info.size = 4
            info.mtime = SANE_MTIME
            info.pax_headers = {"atime": "1575800000.123456789", "ctime": "1575800001.5"}
            archive.addfile(info, io.BytesIO(b"data"))

        path = self.build("pax-attrs.tar", builder)
        result = self.inspect(path)
        self.assertEqual(result["status"], "success", result)
        entry = result["entries"][0]
        self.assertEqual(entry["pax_headers"]["atime"], "1575800000.123456789")
        self.assertEqual(entry["pax_headers"]["ctime"], "1575800001.5")
        rules = {finding["rule"] for finding in result["findings"]}
        self.assertIn("pax_extensions", rules)

    # -- (b) deeper multi-hop symlink farms ------------------------------------
    def test_composing_three_hop_symlink_escape(self):
        """A composing 3-hop chain (each link lands on the next) is caught."""
        path = self.build(
            "chain3.tar",
            lambda archive: (
                add_dir(archive, "m1/"),
                add_dir(archive, "m1/m2/"),
                add_file(archive, "m1/real.txt", b"data"),
                add_file(archive, "m1/m2/real2.txt", b"data"),
                add_symlink(archive, "hop1", "m1/hop2"),
                add_symlink(archive, "m1/hop2", "m2/hop3"),
                add_symlink(archive, "m1/m2/hop3", "../../../etc"),
                add_file(archive, "hop1/pwned.txt", b"pwn!"),
            ),
        )
        result = self.audit(path)
        self.assertEqual(result["status"], "success", result)
        by_rule = {finding["rule"]: finding for finding in result["findings"]}
        self.assertIn("symlink_redirect", by_rule)
        self.assertIn("hop1/pwned.txt", by_rule["symlink_redirect"]["entries"])
        plan = self.tool.execute(mode="plan_extraction", file_path="chain3.tar", dest_dir="out")
        entry = next(item for item in plan["plans"] if item["name"] == "hop1/pwned.txt")
        self.assertTrue(entry["escapes_dest"])
        self.assertEqual(len(entry["redirect_via"]), 3)

    def test_non_composing_chain_is_not_a_redirect(self):
        """A chain whose redirect path no longer matches a real symlink stops."""
        path = self.build(
            "chain-broken.tar",
            lambda archive: (
                add_symlink(archive, "a1", "l1/a2"),
                add_symlink(archive, "l1/a2", "l2/a3"),
                add_symlink(archive, "l2/a3", "l3/a4"),
                add_symlink(archive, "l3/a4", "../../../../outside"),
                add_file(archive, "l1/f.txt", b"x"),
                add_file(archive, "a1/deep/file.txt", b"x"),
            ),
        )
        result = self.audit(path)
        rules = {finding["rule"] for finding in result["findings"]}
        # resolving a1 lands at l1/l2/a3, which is NOT a symlink entry
        self.assertNotIn("symlink_redirect", rules)

    def test_absolute_hop_chain_redirect(self):
        """A hop onto an absolute symlink target escapes immediately."""
        path = self.build(
            "chain-abs.tar",
            lambda archive: (
                add_symlink(archive, "s1", "d/s2"),
                add_symlink(archive, "d/s2", "/etc"),
                add_file(archive, "s1/x", b"x"),
            ),
        )
        result = self.audit(path)
        rules = {finding["rule"] for finding in result["findings"]}
        self.assertIn("symlink_redirect", rules)

    def test_pax_path_override_is_the_effective_name(self):
        """Traversal hidden in a pax path header is flagged on the effective name."""
        def builder(archive):
            info = tarfile.TarInfo("benign.txt")
            info.size = 4
            info.mtime = SANE_MTIME
            info.pax_headers = {"path": "../../etc/pwned"}
            archive.addfile(info, io.BytesIO(b"pwn!"))

        path = self.build("pax-trav.tar", builder)
        result = self.audit(path)
        rules = {finding["rule"] for finding in result["findings"]}
        self.assertIn("path_traversal_dotdot", rules)
        inspected = self.inspect(path)
        self.assertTrue(any("../" in entry["name"] for entry in inspected["entries"]))

    def test_duplicate_symlink_over_earlier_file(self):
        """A later symlink duplicating an earlier file name is a duplicate finding."""
        path = self.build(
            "dup-sym.tar",
            lambda archive: (
                add_file(archive, "shared", b"aaaaa"),
                add_file(archive, "helper", b"b"),
                add_symlink(archive, "shared", "helper"),
            ),
        )
        result = self.audit(path)
        by_rule = {finding["rule"]: finding for finding in result["findings"]}
        self.assertIn("duplicate_entries", by_rule)
        self.assertEqual(by_rule["duplicate_entries"]["count"], 1)

    def test_device_nodes_with_odd_modes(self):
        """Device nodes with setuid/setgid bits trigger both rules."""
        def builder(archive):
            for index, mode in enumerate([0o4777, 0o2755, 0o644]):
                info = tarfile.TarInfo(f"dev{index}")
                info.type = tarfile.CHRTYPE
                info.devmajor, info.devminor = 1, index
                info.mode = mode
                info.mtime = SANE_MTIME
                archive.addfile(info)
            blk = tarfile.TarInfo("blk0")
            blk.type = tarfile.BLKTYPE
            blk.devmajor, blk.devminor = 7, 0
            blk.mtime = SANE_MTIME
            archive.addfile(blk)

        path = self.build("dev-odd.tar", builder)
        result = self.audit(path)
        rules = {finding["rule"] for finding in result["findings"]}
        self.assertIn("device_special", rules)
        self.assertIn("setuid_setgid", rules)

    # -- (c) corrupted-archive sweep -------------------------------------------
    def test_truncation_sweep_every_five_percent(self):
        """Truncating 20 archives at every 5% boundary stays structured."""
        for seed in range(20):
            path = self.build(f"sweep-{seed}.tar", self._second_pass_builder(900 + seed))
            with open(path, "rb") as stream:
                data = stream.read()
            for percent in range(5, 100, 5):
                with self.subTest(seed=seed, percent=percent):
                    cut = max(1, len(data) * percent // 100)
                    truncated = self.path(f"sweep-cut-{seed}-{percent}.bin")
                    with open(truncated, "wb") as stream:
                        stream.write(data[:cut])
                    result = self.audit(truncated)
                    self.assertIn(result["status"], {"success", "error"}, result)
                    if result["status"] == "error":
                        self.assertNotEqual(result["error_type"], "operation_error", result)

    # -- (d) base64 round trip carries the new fields ---------------------------
    def test_base64_round_trip_uname_gname_pax(self):
        """The base64 payload path surfaces uname/gname/pax_headers identically."""
        def builder(archive):
            info = tarfile.TarInfo("f.txt")
            info.size = 4
            info.mtime = SANE_MTIME
            info.uname = "user 一"
            info.gname = "wheel"
            info.pax_headers = {"atime": "1575800000.5"}
            archive.addfile(info, io.BytesIO(b"data"))

        path = self.build("b64-attrs.tar", builder)
        with open(path, "rb") as stream:
            payload = stream.read()
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:") as archive:
            oracle = archive.getmembers()[0].pax_headers
        result = self.tool.execute(mode="inspect", base64_archive=base64.b64encode(payload).decode("ascii"))
        self.assertEqual(result["status"], "success", result)
        entry = result["entries"][0]
        self.assertEqual(entry["uname"], "user 一")
        self.assertEqual(entry["gname"], "wheel")
        # tarfile mirrors the non-ASCII uname into pax; both views agree
        self.assertEqual(entry["pax_headers"], {key: value[:200] for key, value in sorted(oracle.items())})
        self.assertEqual(entry["pax_headers"]["atime"], "1575800000.5")

    # -- (e) plan_extraction vs normpath on 300 fresh names --------------------
    def test_plan_matches_normpath_300(self):
        """Plain (non-redirect) plan resolution equals posixpath.normpath(join)."""
        pool = ["a", "b", "c", "..", ".", "x y", "m", "n"]
        rng = random.Random(424242)  # noqa: S311 - deterministic test data
        for index in range(300):
            with self.subTest(index=index):
                dest = rng.choice(["out", "./out", "out/sub", "/abs/root", "o u t"])
                name = "/".join(rng.choice(pool) for _ in range(rng.randint(1, 4)))
                path = self.build(f"plan2-{index}.tar", lambda archive, n=name: add_file(archive, n, b"z"))
                result = self.tool.execute(mode="plan_extraction", file_path=os.path.basename(path), dest_dir=dest)
                self.assertEqual(result["status"], "success", result)
                root = posixpath.normpath(dest.replace("\\", "/"))
                want = posixpath.normpath(name) if name.startswith("/") else posixpath.normpath(posixpath.join(root, name))
                self.assertEqual(result["plans"][0]["resolved_path"], want)

    # -- (f) pathological: a 10MB single name field -----------------------------
    def test_ten_megabyte_name_field(self):
        """A single entry whose pax path header is ~10MB is read and reported."""
        huge = "N" * (10 * 1024 * 1024)
        path = self.build("huge-name.tar", lambda archive: add_file(archive, huge, b""))
        result = self.inspect(path)
        self.assertEqual(result["status"], "success", result)
        self.assertEqual(result["entries"][0]["name"], huge)


class TarInspectRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped tar_inspect_tool.yaml as a tool component."""

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
        """Verify the shipped yaml resolves to a tool component exposing the TarInspectTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "TarInspectTool")

    def test_manager(self):
        """Verify the TarInspectTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, TarInspectTool)
        self.assertEqual(tool.input_keys, ["mode"])


if __name__ == "__main__":
    unittest.main()
