#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_path_lint_tool.py

r"""Offline unit tests for PathLintTool.

The tool lints filesystem path strings for portability and safety
on the standard library only and never touches the filesystem, so
this suite runs fully offline. Assertions are deterministic
hand-computed ground truths plus two stdlib oracle differentials:

* Normalization oracle — the compare mode's normalized forms must
  equal ``posixpath.normpath`` / ``ntpath.normpath`` verbatim on a
  300-seed generated corpus (the stdlib modules are the normative
  oracle), and the Windows equality flag must equal an independent
  ``ntpath.normcase(ntpath.normpath(...))`` comparison recomputed
  inside the test.
* Reserved-knowledge oracle — the Windows reserved-name matrix
  (CON PRN AUX NUL COM1-COM9 LPT1-LPT9, case-insensitive, with and
  without extension, in file and directory position, and the
  COM0 / LPT0 / CONSOLE negatives) and the reserved-character set
  ``<>:"|?*`` are hand-embedded from the Microsoft "Naming Files,
  Paths, and Namespaces" documentation and asserted in full.

The lint vectors walk every check code (null bytes, control
characters and lone surrogates, separator homoglyphs, non-NFC
Unicode, mixed separators, UNC and ``\\?\`` prefix validation,
device namespace, drive-relative forms, reserved characters and
names, trailing dots/spaces, '.'/'..' semantics with parent
escapes, empty segments with UNC tolerance, tilde prefixes, the
MAX_PATH 260 and 255-character component limits), the ordering
contract (fixed check order, at most one finding per code,
``line`` always 1 — the single-text contract) and the summary
arithmetic. The compare vectors cover alias analysis on each
platform, the case-only rename-collision hint and the documented
reasons; the validate vectors cover per-platform verdicts, the
platform attribution of every code, the auto-inference rule and
the both option. Parameter-level mistakes are ``ValueError``
(wrong types, missing required parameters, over-cap inputs, bad
mode / platform values).
"""

import ntpath
import posixpath
import random
import unittest

from agentuniverse.agent.action.tool.common_tool import PathLintTool
from agentuniverse.agent.action.tool.common_tool.path_lint_tool import (
    _RESERVED_NAMES,
    PathLintTool as DirectPathLintTool,
)

TOOL = PathLintTool()


def lint(path, tool=None):
    return (tool or TOOL).execute(mode="lint", path=path)


def codes(result):
    return [f["code"] for f in result["findings"]]


def compare(path_a, path_b):
    return TOOL.execute(mode="compare", path_a=path_a, path_b=path_b)


def validate(path, platform=None):
    if platform is None:
        return TOOL.execute(mode="validate", path=path)
    return TOOL.execute(mode="validate", path=path, platform=platform)


# ------------------------------------------------------------------ #
# lint mode — clean paths
# ------------------------------------------------------------------ #


class LintCleanPathsTest(unittest.TestCase):
    def test_portable_posix_paths_are_clean(self):
        for path in ["a/b/c.txt", "/usr/local/bin", "reports/2026/q4.xlsx",
                     "src/lib/__pycache__", "a/b/c/d/e/f.txt"]:
            result = lint(path)
            self.assertEqual(result["findings"], [], path)
            self.assertEqual(result["summary"],
                             {"total": 0, "error": 0, "warning": 0, "info": 0})

    def test_windows_absolute_paths_are_clean(self):
        for path in ["C:\\Users\\me\\file.txt", "C:\\logs\\app.log",
                     "D:\\data\\reports\\2026", "C:/Users/me/file.txt"]:
            self.assertEqual(lint(path)["findings"], [], path)

    def test_unc_paths_are_clean(self):
        for path in ["\\\\server\\share\\file.txt", "\\\\server\\share\\sub\\x",
                     "\\\\?\\C:\\very\\long\\path", "\\\\?\\UNC\\server\\share\\x"]:
            self.assertEqual(lint(path)["findings"], [], path)

    def test_tolerated_forms_are_silent(self):
        # One trailing separator, a leading POSIX pair, dot-free
        # relative paths, plain Unicode NFC names: no findings.
        for path in ["a/b/", "//posix_root_form", "café", "目录/文件.txt",
                     "C:\\x\\", "a/b/c/."[:0] or "plain"]:
            self.assertEqual(lint(path)["findings"], [], repr(path))


# ------------------------------------------------------------------ #
# lint mode — the check matrix
# ------------------------------------------------------------------ #


class LintCheckMatrixTest(unittest.TestCase):
    def test_null_byte(self):
        result = lint("a\x00b/c")
        self.assertEqual(codes(result), ["null_byte"])
        finding = result["findings"][0]
        self.assertEqual(finding["severity"], "error")
        self.assertEqual(finding["line"], 1)
        self.assertIn("null byte", finding["message"])

    def test_control_characters(self):
        result = lint("a\x01b\x7f")
        self.assertEqual(codes(result), ["control_char"])
        self.assertEqual(result["findings"][0]["severity"], "error")
        self.assertIn("U+0001", result["findings"][0]["message"])

    def test_c1_range_and_surrogates_are_control(self):
        result = lint("ab\udc80")
        self.assertEqual(codes(result), ["control_char"])
        self.assertIn("U+009F", result["findings"][0]["message"])
        self.assertIn("surrogate", result["findings"][0]["message"])

    def test_confusable_separators(self):
        for ch in ["\uFF0F", "\uFF3C", "\u2044", "\u2215", "\u29F5", "\uFE68"]:
            result = lint("a" + ch + "b")
            self.assertEqual(codes(result), ["confusable_char"], repr(ch))
            self.assertEqual(result["findings"][0]["severity"], "warning")
            self.assertIn(f"U+{ord(ch):04X}", result["findings"][0]["message"])

    def test_non_nfc(self):
        result = lint("cafe\u0301")  # e + combining acute
        self.assertEqual(codes(result), ["non_nfc"])
        self.assertEqual(result["findings"][0]["severity"], "warning")
        # The precomposed NFC form is clean.
        self.assertEqual(lint("café")["findings"], [])

    def test_mixed_separators(self):
        result = lint("a/b\\c")
        self.assertEqual(codes(result), ["mixed_separators"])
        self.assertEqual(result["findings"][0]["severity"], "warning")

    def test_invalid_extended_prefixes(self):
        for path in ["\\\\?\\relative\\path", "//?/C:/x", "\\\\?\\", "\\\\?\\C:"]:
            self.assertEqual(codes(lint(path)), ["unc_prefix"], repr(path))
            self.assertEqual(lint(path)["findings"][0]["severity"], "error")

    def test_extended_prefix_with_forward_slashes(self):
        result = lint("\\\\?\\C:/x")
        self.assertIn("unc_prefix", codes(result))
        self.assertIn("mixed_separators", codes(result))

    def test_valid_extended_prefixes_are_clean(self):
        self.assertEqual(lint("\\\\?\\C:\\x")["findings"], [])
        self.assertEqual(lint("\\\\?\\UNC\\srv\\share\\x")["findings"], [])

    def test_extended_prefix_raises_the_length_budget(self):
        long_body = "\\".join(["x" * 40] * 8)  # well over MAX_PATH 260
        over = "\\\\?\\" + "C:\\" + long_body
        plain = "C:\\" + long_body
        self.assertNotIn("path_length", codes(lint(over)))
        self.assertIn("path_length", codes(lint(plain)))

    def test_unc_missing_share(self):
        for path in ["\\\\server", "\\\\", "\\\\server\\"]:
            self.assertEqual(codes(lint(path)), ["unc_prefix"], repr(path))

    def test_device_namespace(self):
        result = lint("\\\\.\\PhysicalDisk0")
        self.assertEqual(codes(result), ["device_namespace"])
        self.assertEqual(result["findings"][0]["severity"], "info")

    def test_drive_relative_quirk(self):
        for path in ["C:x", "C:", "d:file.txt", "Z:"]:
            result = lint(path)
            self.assertEqual(codes(result), ["drive_relative"], repr(path))
            self.assertEqual(result["findings"][0]["severity"], "warning")
        # The absolute forms are clean.
        self.assertEqual(lint("C:\\x")["findings"], [])
        self.assertEqual(lint("C:/x")["findings"], [])

    def test_reserved_characters(self):
        result = lint("a<b>c|d*e?f\"g")
        self.assertEqual(codes(result), ["reserved_char"])
        self.assertEqual(result["findings"][0]["severity"], "error")
        for ch in "<>\"|?*":
            self.assertIn(f"'{ch}'", result["findings"][0]["message"], ch)

    def test_colon_outside_drive_slot(self):
        result = lint("a/b:c")
        self.assertEqual(codes(result), ["reserved_char"])
        self.assertIn("alternate data stream", result["findings"][0]["message"])

    def test_lowercase_drive_is_not_reserved_char(self):
        # The colon directly after a single leading letter is the
        # legal drive slot even lowercase.
        self.assertNotIn("reserved_char", codes(lint("c:\\x")))
        self.assertNotIn("reserved_char", codes(lint("c:/x")))

    def test_multi_letter_segment_with_colon_is_reserved(self):
        result = lint("ab:c/d")
        self.assertEqual(codes(result), ["reserved_char"])

    def test_trailing_dot_and_space(self):
        for path in ["foo.", "foo ", "foo. /bar", "dir./x", "b ./c",
                     "report .txt ", "x/y/z."]:
            self.assertIn("trailing_dot_space", codes(lint(path)), repr(path))
            finding = [f for f in lint(path)["findings"]
                       if f["code"] == "trailing_dot_space"][0]
            self.assertEqual(finding["severity"], "error")
        # Interior dots and spaces are fine — only segments that
        # truly END in '.' or space are stripped by Win32.
        for path in ["my report.v2.txt", "foo .txt", "a . b", "v1.2/config.yaml"]:
            self.assertNotIn("trailing_dot_space", codes(lint(path)), repr(path))

    def test_dot_segments_are_info(self):
        result = lint("a/./b")
        self.assertEqual(codes(result), ["dot_segment"])
        self.assertEqual(result["findings"][0]["severity"], "info")

    def test_benign_dot_dot_is_info(self):
        result = lint("a/../b")
        self.assertEqual(codes(result), ["dot_dot_segment"])
        self.assertEqual(result["findings"][0]["severity"], "info")

    def test_dot_dot_beyond_absolute_root_is_info(self):
        result = lint("/..")
        self.assertEqual(codes(result), ["dot_dot_segment"])
        result = lint("C:\\..\\..")
        self.assertEqual(codes(result), ["dot_dot_segment"])

    def test_parent_escape_in_relative_paths(self):
        for path in ["../x", "a/../..", "..", "../..", "a/b/../../.."]:
            result = lint(path)
            self.assertIn("parent_escape", codes(result), repr(path))
            finding = [f for f in result["findings"]
                       if f["code"] == "parent_escape"][0]
            self.assertEqual(finding["severity"], "warning")
        # One .. inside stays benign.
        self.assertNotIn("parent_escape", codes(lint("a/../b")))

    def test_empty_segments_with_unc_tolerance(self):
        result = lint("a//b")
        self.assertEqual(codes(result), ["empty_segment"])
        self.assertEqual(result["findings"][0]["severity"], "info")
        # Leading pair tolerated, extra leading reported.
        self.assertEqual(lint("//x")["findings"], [])
        self.assertIn("empty_segment", codes(lint("///x")))
        # One trailing separator silent, doubled reported.
        self.assertEqual(lint("a/b/")["findings"], [])
        self.assertIn("empty_segment", codes(lint("a/b//")))
        # UNC lead pair with backslashes tolerated.
        self.assertNotIn("empty_segment", codes(lint("\\\\srv\\share\\x")))

    def test_tilde_prefix(self):
        for path in ["~/x", "~user/proj", "~"]:
            result = lint(path)
            self.assertEqual(codes(result), ["tilde_prefix"], repr(path))
            self.assertEqual(result["findings"][0]["severity"], "info")
        # Interior tilde is an ordinary character.
        self.assertEqual(lint("a~b/c")["findings"], [])

    def test_segment_length_limit(self):
        result = lint("a/" + "y" * 256)
        self.assertIn("segment_length", codes(result))
        self.assertNotIn("segment_length", codes(lint("a/" + "y" * 255)))
        finding = [f for f in result["findings"]
                   if f["code"] == "segment_length"][0]
        self.assertEqual(finding["severity"], "warning")
        self.assertIn("255", finding["message"])

    def test_path_length_limit(self):
        path = "/".join(["x" * 40] * 7)  # 287 chars
        self.assertGreater(len(path), 260)
        result = lint(path)
        self.assertIn("path_length", codes(result))
        finding = [f for f in result["findings"] if f["code"] == "path_length"][0]
        self.assertEqual(finding["severity"], "warning")
        self.assertIn("MAX_PATH", finding["message"])
        short = "/".join(["x" * 20] * 5)
        self.assertLess(len(short), 260)
        self.assertNotIn("path_length", codes(lint(short)))

    def test_long_segment_and_long_path_reported_once_each(self):
        path = "z" * 300
        self.assertEqual(codes(lint(path)), ["segment_length", "path_length"])


# ------------------------------------------------------------------ #
# lint mode — the reserved-name oracle (Microsoft naming docs)
# ------------------------------------------------------------------ #


class ReservedNameOracleTest(unittest.TestCase):
    def test_embedded_reserved_set_matches_microsoft_docs(self):
        expected = {"CON", "PRN", "AUX", "NUL"} \
            | {f"COM{i}" for i in range(1, 10)} \
            | {f"LPT{i}" for i in range(1, 10)}
        self.assertEqual(set(_RESERVED_NAMES), expected)
        self.assertEqual(len(expected), 22)

    def test_every_reserved_name_flagged(self):
        for name in _RESERVED_NAMES:
            self.assertEqual(codes(lint(name)), ["reserved_name"], name)

    def test_case_insensitive(self):
        for spelling in ["con", "Con", "cON", "nUl", "com3", "Lpt9", "aux"]:
            self.assertEqual(codes(lint(spelling)), ["reserved_name"], spelling)

    def test_with_extension(self):
        for path in ["CON.txt", "con.log", "COM3.tar.gz", "NUL.", "PRN .dat"]:
            self.assertIn("reserved_name", codes(lint(path)), repr(path))

    def test_directory_position_counts(self):
        for path in ["logs/NUL", "CON/readme.txt", "a/b/Aux/x", "\\\\srv\\COM1\\y"]:
            self.assertIn("reserved_name", codes(lint(path)), repr(path))

    def test_negatives_not_flagged(self):
        for path in ["CONSOLE", "console.txt", "com0", "lpt0", "COM10",
                     "LPT10", "aux1", "nul0", "control", "connect/x", "CONCEPT"]:
            self.assertNotIn("reserved_name", codes(lint(path)), repr(path))

    def test_com9_boundary(self):
        self.assertIn("reserved_name", codes(lint("COM9")))
        self.assertIn("reserved_name", codes(lint("LPT1")))
        self.assertNotIn("reserved_name", codes(lint("COM0")))
        self.assertNotIn("reserved_name", codes(lint("LPT0")))


# ------------------------------------------------------------------ #
# lint mode — the ordering and payload contracts
# ------------------------------------------------------------------ #


class LintContractTest(unittest.TestCase):
    def test_fixed_check_order(self):
        # A kitchen-sink path: the findings must appear in the
        # documented check order regardless of input order.
        path = "CON/\x00a/../~/／x?" + "y" * 300
        result = lint(path)
        expected_order = [c for c in [
            "null_byte", "control_char", "confusable_char", "non_nfc",
            "mixed_separators", "unc_prefix", "device_namespace",
            "drive_relative", "reserved_char", "reserved_name",
            "trailing_dot_space", "dot_segment", "dot_dot_segment",
            "parent_escape", "empty_segment", "tilde_prefix",
            "segment_length", "path_length"] if c in codes(result)]
        self.assertEqual(codes(result), expected_order)

    def test_at_most_one_finding_per_code(self):
        path = "CON/NUL/COM1/a<b>c<d|e/a./b./c "
        result = lint(path)
        got = codes(result)
        self.assertEqual(len(got), len(set(got)))
        # The message aggregates all three reserved segments.
        message = [f for f in result["findings"]
                   if f["code"] == "reserved_name"][0]["message"]
        self.assertIn("1", message)
        self.assertIn("2", message)
        self.assertIn("3", message)

    def test_line_is_always_one(self):
        for path in ["a\x00b", "CON", "a//b", "x" * 300, "／x", "e\u0301"]:
            for finding in lint(path)["findings"]:
                self.assertEqual(finding["line"], 1)

    def test_finding_shape(self):
        result = lint("CON")
        finding = result["findings"][0]
        self.assertEqual(set(finding), {"line", "code", "message", "severity"})
        self.assertIsInstance(finding["message"], str)
        self.assertIn(finding["severity"], ("error", "warning", "info"))

    def test_summary_arithmetic(self):
        result = lint("CON/a\x00b/~/x" + "y" * 300)
        error = sum(1 for f in result["findings"] if f["severity"] == "error")
        warning = sum(1 for f in result["findings"] if f["severity"] == "warning")
        info = sum(1 for f in result["findings"] if f["severity"] == "info")
        self.assertEqual(result["summary"],
                         {"total": error + warning + info,
                          "error": error, "warning": warning, "info": info})
        self.assertEqual(result["summary"]["total"], len(result["findings"]))

    def test_checked_length_field(self):
        self.assertEqual(lint("abc")["checked_length"], 3)

    def test_determinism(self):
        path = "a/b\\c/CON/／~"
        self.assertEqual(lint(path), lint(path))

    def test_one_finding_per_code_on_random_corpus(self):
        rng = random.Random(1234)
        alphabet = "ab./\\~／CON\x01 *?:"
        for _ in range(300):
            path = "".join(rng.choice(alphabet)
                           for _ in range(rng.randint(1, 60)))
            got = codes(lint(path))
            self.assertEqual(len(got), len(set(got)), repr(path))


# ------------------------------------------------------------------ #
# compare mode
# ------------------------------------------------------------------ #


class CompareTest(unittest.TestCase):
    def test_identical_paths_alias_everywhere(self):
        result = compare("a/b/c.txt", "a/b/c.txt")
        self.assertTrue(result["posix_normalized"]["equal"])
        self.assertTrue(result["windows_normalized"]["equal"])
        self.assertTrue(result["alias_possible"])

    def test_dot_resolution_aliases(self):
        result = compare("a/b/../c", "a/c")
        self.assertEqual(result["posix_normalized"]["a"], "a/c")
        self.assertEqual(result["posix_normalized"]["b"], "a/c")
        self.assertTrue(result["alias_possible"])
        self.assertTrue(result["posix_normalized"]["equal"])
        self.assertTrue(result["windows_normalized"]["equal"])

    def test_separator_style_aliases_on_windows_only(self):
        result = compare("a/b", "a\\b")
        # POSIX: 'a\b' is one filename containing a backslash.
        self.assertFalse(result["posix_normalized"]["equal"])
        # Windows: both separators normalize to backslash.
        self.assertTrue(result["windows_normalized"]["equal"])
        self.assertTrue(result["alias_possible"])
        self.assertIn("can alias on Windows but not on POSIX",
                      " ".join(result["reasons"]))

    def test_case_only_difference_is_the_rename_collision_hint(self):
        result = compare("Foo/Bar.txt", "foo/bar.txt")
        self.assertFalse(result["posix_normalized"]["equal"])
        self.assertTrue(result["windows_normalized"]["equal"])
        self.assertTrue(result["case_only_difference"])
        self.assertTrue(result["alias_possible"])
        self.assertIn("rename collision", " ".join(result["reasons"]))

    def test_windows_normalization_is_case_insensitive(self):
        result = compare("C:\\Users\\Me", "c:/users/me")
        self.assertTrue(result["windows_normalized"]["equal"])
        self.assertEqual(result["windows_normalized"]["a"], "C:\\Users\\Me")
        self.assertEqual(result["windows_normalized"]["b"], "c:\\users\\me")

    def test_genuinely_different_paths_do_not_alias(self):
        result = compare("a/b", "a/c")
        self.assertFalse(result["alias_possible"])
        self.assertFalse(result["posix_normalized"]["equal"])
        self.assertFalse(result["windows_normalized"]["equal"])

    def test_relative_resolution_is_textual(self):
        result = compare("./a/b", "a/b")
        self.assertTrue(result["posix_normalized"]["equal"])
        self.assertEqual(result["posix_normalized"]["a"], "a/b")

    def test_reasons_content(self):
        result = compare("a/b", "a/c")
        self.assertTrue(any("posix" in r for r in result["reasons"]))
        self.assertTrue(any("windows" in r for r in result["reasons"]))
        self.assertIn("text-level analysis only", result["reasons"][-1])
        self.assertIn("8.3", result["reasons"][-1])

    def test_payload_shape(self):
        result = compare("x", "y")
        self.assertEqual(result["mode"], "compare")
        for key in ("posix_normalized", "windows_normalized",
                    "case_only_difference", "alias_possible", "reasons"):
            self.assertIn(key, result)
        for side in ("a", "b", "equal"):
            self.assertIn(side, result["posix_normalized"])
            self.assertIn(side, result["windows_normalized"])


# ------------------------------------------------------------------ #
# validate mode
# ------------------------------------------------------------------ #


class ValidateTest(unittest.TestCase):
    def test_reserved_name_blocks_windows_but_not_posix(self):
        result = validate("CON", "both")
        self.assertFalse(result["platforms"]["windows"]["valid"])
        self.assertTrue(result["platforms"]["posix"]["valid"])
        self.assertEqual(result["platforms"]["windows"]["error_codes"],
                         ["reserved_name"])
        self.assertEqual(result["platforms"]["posix"]["error_codes"], [])

    def test_reserved_char_platform_attribution(self):
        result = validate("a<b|c*", "both")
        self.assertFalse(result["platforms"]["windows"]["valid"])
        self.assertTrue(result["platforms"]["posix"]["valid"])

    def test_null_byte_blocks_both_platforms(self):
        result = validate("a\x00b", "both")
        self.assertFalse(result["platforms"]["windows"]["valid"])
        self.assertFalse(result["platforms"]["posix"]["valid"])

    def test_drive_relative_warns_windows_only(self):
        result = validate("C:x", "both")
        self.assertTrue(result["platforms"]["windows"]["valid"])  # warning only
        self.assertEqual(result["platforms"]["windows"]["warning_codes"],
                         ["drive_relative"])
        self.assertEqual(result["platforms"]["posix"]["warning_codes"], [])

    def test_tilde_attributed_to_posix(self):
        result = validate("~/x", "both")
        self.assertEqual(result["platforms"]["posix"]["info_codes"],
                         ["tilde_prefix"])
        self.assertEqual(result["platforms"]["windows"]["info_codes"], [])

    def test_path_length_attributed_to_windows(self):
        path = "/".join(["x" * 40] * 7)
        result = validate(path, "both")
        self.assertIn("path_length", result["platforms"]["windows"]["warning_codes"])
        self.assertNotIn("path_length", result["platforms"]["posix"]["warning_codes"])

    def test_codes_partition_matches_findings(self):
        result = validate("CON/a//b/x" + "y" * 300, "both")
        for platform, verdict in result["platforms"].items():
            merged = (verdict["error_codes"] + verdict["warning_codes"]
                      + verdict["info_codes"])
            # codes stays in the fixed check order; the severity
            # groups are the same multiset.
            self.assertEqual(sorted(merged), sorted(verdict["codes"]))
            self.assertEqual(len(verdict["findings"]), len(verdict["codes"]))
            for finding, code in zip(verdict["findings"], verdict["codes"]):
                self.assertEqual(finding["code"], code)

    def test_auto_infers_windows_from_backslash(self):
        result = validate("a\\b\\c", "auto")
        self.assertEqual(result["inferred_platform"], "windows")
        self.assertIn("windows", result["platforms"])
        self.assertNotIn("posix", result["platforms"])

    def test_auto_infers_windows_from_drive_letter(self):
        for path in ["C:\\x", "C:/x", "C:x", "C:"]:
            result = validate(path, "auto")
            self.assertEqual(result["inferred_platform"], "windows", path)

    def test_auto_infers_posix_otherwise(self):
        for path in ["a/b", "/usr/bin", "//x", "~/home"]:
            result = validate(path, "auto")
            self.assertEqual(result["inferred_platform"], "posix", path)

    def test_platform_option_values(self):
        self.assertIn("posix", validate("a", "posix")["platforms"])
        self.assertIn("windows", validate("a", "windows")["platforms"])
        both = validate("a", "both")["platforms"]
        self.assertEqual(set(both), {"posix", "windows"})

    def test_default_platform_is_auto(self):
        result = validate("C:\\x")
        self.assertEqual(result["inferred_platform"], "windows")

    def test_validate_findings_use_lint_codes(self):
        result = validate("CON", "windows")
        finding = result["platforms"]["windows"]["findings"][0]
        self.assertEqual(set(finding), {"line", "code", "message", "severity"})
        self.assertEqual(finding["code"], "reserved_name")


# ------------------------------------------------------------------ #
# The stdlib normalization oracle — 300-seed differential
# ------------------------------------------------------------------ #


def _corpus(seed, count):
    """Seeded path-soup generator for the oracle differential."""
    rng = random.Random(seed)
    parts = ["a", "b", "cc", "dir name", "..", ".", "x.txt", "CON", "NUL",
             "~", "~user", "C:", "c:", "Z:", "", "con.t", "／x", "e\u0301",
             "nfc-é", "a<b", "sp ace", "end.", "e" * 300, "sh" * 130]
    seps = ["/", "\\", "//", "\\\\", "/\\", ""]
    prefixes = ["", "", "", "", "//", "\\\\", "\\\\?\\", "\\\\?\\UNC\\",
                "\\\\.", "C:", "C:\\", "C:/", "q:", "//?/"]
    out = []
    for _ in range(count):
        chunks = [rng.choice(prefixes)]
        for _ in range(rng.randint(0, 6)):
            chunks.append(rng.choice(parts))
            chunks.append(rng.choice(seps))
        out.append("".join(chunks))
    return out


class NormalizationOracleTest(unittest.TestCase):
    def test_normalized_forms_equal_stdlib_on_300_seeds(self):
        for path in _corpus(20261021, 300):
            result = compare(path, path)
            self.assertEqual(
                result["posix_normalized"]["a"],
                posixpath.normpath(path),
                repr(path),
            )
            self.assertEqual(
                result["posix_normalized"]["b"],
                posixpath.normpath(path),
                repr(path),
            )
            self.assertEqual(
                result["windows_normalized"]["a"],
                ntpath.normpath(path),
                repr(path),
            )
            self.assertEqual(
                result["windows_normalized"]["b"],
                ntpath.normpath(path),
                repr(path),
            )

    def test_windows_equality_matches_normcase_recomputation(self):
        paths = _corpus(97531, 200)
        for i in range(0, len(paths) - 1, 2):
            a, b = paths[i], paths[i + 1]
            result = compare(a, b)
            independent = (
                ntpath.normcase(ntpath.normpath(a))
                == ntpath.normcase(ntpath.normpath(b))
            )
            self.assertEqual(result["windows_normalized"]["equal"],
                             independent, (a, b))
            self.assertEqual(
                result["alias_possible"],
                posixpath.normpath(a) == posixpath.normpath(b) or independent,
                (a, b),
            )

    def test_posix_equality_recomputed(self):
        paths = _corpus(86420, 100)
        for i in range(0, len(paths) - 1, 2):
            a, b = paths[i], paths[i + 1]
            result = compare(a, b)
            self.assertEqual(
                result["posix_normalized"]["equal"],
                posixpath.normpath(a) == posixpath.normpath(b),
                (a, b),
            )

    def test_lint_never_crashes_on_corpus(self):
        for path in _corpus(24680, 300):
            result = lint(path)
            for finding in result["findings"]:
                self.assertEqual(finding["line"], 1)
                self.assertIn(finding["severity"], ("error", "warning", "info"))
            got = codes(result)
            self.assertEqual(len(got), len(set(got)), repr(path))


# ------------------------------------------------------------------ #
# Input validation — strict, before any computation
# ------------------------------------------------------------------ #


class InputValidationTest(unittest.TestCase):
    def test_bad_mode(self):
        for mode in [None, "", "run", "LINT", 1, b"lint"]:
            with self.assertRaises(ValueError):
                TOOL.execute(mode=mode, path="a")

    def test_lint_requires_string_path(self):
        for bad in [None, True, False, 7, 3.5, ["a"], ("a",), {"a": 1}, b"a"]:
            with self.assertRaises(ValueError):
                TOOL.execute(mode="lint", path=bad)

    def test_compare_requires_both_strings(self):
        with self.assertRaises(ValueError):
            TOOL.execute(mode="compare", path_a="a")
        with self.assertRaises(ValueError):
            TOOL.execute(mode="compare", path_b="a")
        for bad in [None, True, 7, ["a"]]:
            with self.assertRaises(ValueError):
                TOOL.execute(mode="compare", path_a=bad, path_b="a")
            with self.assertRaises(ValueError):
                TOOL.execute(mode="compare", path_a="a", path_b=bad)

    def test_validate_requires_string_path(self):
        with self.assertRaises(ValueError):
            TOOL.execute(mode="validate", path=None)

    def test_bad_platform(self):
        for bad in [None if False else "mac", "dos", "Both", 1, "", "auto "]:
            with self.assertRaises(ValueError):
                TOOL.execute(mode="validate", path="a", platform=bad)

    def test_path_cap(self):
        tool = PathLintTool()
        long_path = "x" * (tool.max_path_chars + 1)
        with self.assertRaises(ValueError):
            tool.execute(mode="lint", path=long_path)
        with self.assertRaises(ValueError):
            tool.execute(mode="compare", path_a=long_path, path_b="a")
        with self.assertRaises(ValueError):
            tool.execute(mode="compare", path_a="a", path_b=long_path)
        with self.assertRaises(ValueError):
            tool.execute(mode="validate", path=long_path)

    def test_cap_is_overridable(self):
        tool = PathLintTool(max_path_chars=10)
        with self.assertRaises(ValueError):
            tool.execute(mode="lint", path="x" * 11)
        result = tool.execute(mode="lint", path="x" * 10)
        self.assertEqual(result["findings"], [])

    def test_cap_must_be_positive(self):
        with self.assertRaises(ValueError):
            PathLintTool(max_path_chars=0)

    def test_error_messages_name_the_parameter(self):
        with self.assertRaises(ValueError) as ctx:
            TOOL.execute(mode="lint", path=7)
        self.assertIn("path", str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            TOOL.execute(mode="compare", path_a="a", path_b=False)
        self.assertIn("path_b", str(ctx.exception))

    def test_error_preview_is_bounded(self):
        with self.assertRaises(ValueError) as ctx:
            TOOL.execute(mode="lint", path=list(range(10_000)))
        self.assertLess(len(str(ctx.exception)), 400)

    def test_wrong_extra_types_do_not_crash_other_modes(self):
        # path is ignored by compare; platform defaults for validate.
        result = TOOL.execute(mode="compare", path_a="a", path_b="b", path=None)
        self.assertEqual(result["mode"], "compare")
        result = TOOL.execute(mode="validate", path="a", platform="both")
        self.assertEqual(set(result["platforms"]), {"posix", "windows"})


# ------------------------------------------------------------------ #
# Packaging / registration
# ------------------------------------------------------------------ #


class PackagingTest(unittest.TestCase):
    def test_exported_from_package_init(self):
        from agentuniverse.agent.action.tool.common_tool import (
            PathLintTool as Exported,
        )
        self.assertIs(Exported, DirectPathLintTool)

    def test_tool_identity(self):
        tool = DirectPathLintTool()
        self.assertEqual(tool.name, "path_lint_tool")
        self.assertIn("path", tool.description.lower())
        self.assertIn("lint", tool.description.lower())
        self.assertIsInstance(tool.MODES, tuple)
        self.assertEqual(set(tool.MODES), {"lint", "compare", "validate"})
        self.assertEqual(
            set(tool.PLATFORMS), {"posix", "windows", "auto", "both"}
        )

    def test_yaml_exists(self):
        import os
        module_dir = os.path.dirname(DirectPathLintTool.__module__.replace(
            ".", "/") + ".py") if False else os.path.abspath(
            os.path.join(os.path.dirname(__import__(
                DirectPathLintTool.__module__, fromlist=["x"]).__file__
            ), "path_lint_tool.yaml"))
        self.assertTrue(os.path.exists(module_dir), module_dir)


if __name__ == "__main__":
    unittest.main()
