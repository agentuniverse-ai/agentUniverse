"""Oracle tests for DiffParseTool: difflib battery, real diff/git fixtures,
corruption battery, pathological inputs, and component registration.

The oracles are:
(a) 500 seeded difflib-generated diffs must validate cleanly, apply to their
    original text, and reverse round-trip back to the original.
(b) Real captured `git diff` / `diff -u` outputs (timestamps frozen) exercise
    new-file, deletion, rename, binary, quoted-path, blank-context and
    no-newline-marker forms.
(c) 300 seeded corruptions of valid diffs must each be caught by validate or
    by apply_check, with the catching layer adjudicated per mutation class.
(d) Pathological inputs stay bounded: a 10k-line diff parses in <2s, a 1MB
    single line is accepted, and cap violations return structured errors.
"""

import difflib
import os
import random
import shutil
import subprocess
import tempfile
import time
import unittest

from agentuniverse.agent.action.tool.common_tool import diff_parse_tool as diff_module
from agentuniverse.agent.action.tool.common_tool.diff_parse_tool import DiffParseTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(diff_module.__file__), "diff_parse_tool.yaml")

# ---------------------------------------------------------------------------
# (b) Real captured outputs. The git diffs are byte-deterministic for this
# content; the plain `diff -u` outputs were captured with BSD diff and the
# timestamps frozen (the parser ignores everything after the TAB anyway).
# ---------------------------------------------------------------------------

GIT_MULTI = """diff --git a/file.txt b/file.txt
index 600d48a..1663761 100644
--- a/file.txt
+++ b/file.txt
@@ -1,5 +1,5 @@
 alpha
-beta
+BETA
 gamma
 delta
-epsilon
+EPSILON
diff --git a/keep.txt b/keep.txt
deleted file mode 100644
index 4cb29ea..0000000
--- a/keep.txt
+++ /dev/null
@@ -1,3 +0,0 @@
-one
-two
-three
diff --git a/new.txt b/new.txt
new file mode 100644
index 0000000..4596d3c
--- /dev/null
+++ b/new.txt
@@ -0,0 +1,2 @@
+brand new
+content here
"""

GIT_MODIFY = GIT_MULTI.split("diff --git a/keep.txt")[0]

GIT_NEW_FILE = """diff --git a/new.txt b/new.txt
new file mode 100644
index 0000000..4596d3c
--- /dev/null
+++ b/new.txt
@@ -0,0 +1,2 @@
+brand new
+content here
"""

GIT_DELETE = """diff --git a/keep.txt b/keep.txt
deleted file mode 100644
index 4cb29ea..0000000
--- a/keep.txt
+++ /dev/null
@@ -1,3 +0,0 @@
-one
-two
-three
"""

GIT_RENAME = """diff --git a/orig.txt b/renamed.txt
similarity index 100%
rename from orig.txt
rename to renamed.txt
"""

GIT_BINARY = """diff --git a/bin.dat b/bin.dat
new file mode 100644
index 0000000..c94be36
Binary files /dev/null and b/bin.dat differ
"""

GIT_NO_NEWLINE = """diff --git a/n.txt b/n.txt
index 1c943a9..985cad8 100644
--- a/n.txt
+++ b/n.txt
@@ -1,3 +1,3 @@
 a
 b
-c
\\ No newline at end of file
+C
\\ No newline at end of file
"""

BSD_NO_NEWLINE = (
    "--- x1.txt\t2026-10-22 04:59:01\n"
    "+++ x2.txt\t2026-10-22 04:59:01\n"
    "@@ -1,3 +1,3 @@\n"
    " a\n"
    "-b\n"
    "+B\n"
    " c\n"
    "\\ No newline at end of file\n"
)

BSD_BLANK_CONTEXT = (
    "--- y1.txt\t2026-10-22 04:59:01\n"
    "+++ y2.txt\t2026-10-22 04:59:01\n"
    "@@ -1,3 +1,3 @@\n"
    " a\n"
    " \n"
    "-b\n"
    "+B\n"
)

BSD_DEV_NULL = (
    "--- /dev/null\t2026-10-22 04:59:01\n"
    "+++ z.txt\t2026-10-22 04:59:01\n"
    "@@ -0,0 +1 @@\n"
    "+hello\n"
)

# GNU diff quotes paths that contain spaces; BSD diff does not. The quoted
# form uses C-style escapes, so a tab inside a path becomes \t.
GNU_QUOTED = (
    '--- "dir with space/f\\t1.txt"\t2026-10-22 04:59:01\n'
    '+++ "dir with space/f\\t2.txt"\t2026-10-22 04:59:01\n'
    "@@ -1,2 +1,2 @@\n"
    " p\n"
    "-q\n"
    "+Q\n"
)

SPEC_COUNT_OMITTED = "--- a\n+++ b\n@@ -1 +1 @@\n-x\n+y\n"
SPEC_SECTION_HEADING = "--- a.py\n+++ b.py\n@@ -1,3 +1,3 @@ def foo():\n a\n-b\n+B\n c\n"

CRLF_TRANSPORT = (
    "--- c1.txt\r\n"
    "+++ c2.txt\r\n"
    "@@ -1,2 +1,2 @@\r\n"
    " aa\r\n"
    "-bb\r\n"
    "+BB\r\n"
)

# CRLF-content diff: the diffed file has CRLF endings but the diff text is
# transported with LF, so the CRs are honest line content.
CRLF_CONTENT = (
    "--- c1.txt\n+++ c2.txt\n@@ -1,2 +1,2 @@\n aa\r\n-bb\r\n+BB\r\n"
)


def finding_codes(result):
    return [item["code"] for item in result.get("findings", [])]


def error_codes(result):
    return [item["code"] for item in result.get("findings", []) if item["severity"] == "error"]


class ValidateGrammarTest(unittest.TestCase):
    """Checks for header pairing, hunk grammar, arithmetic, and markers."""

    def setUp(self):
        self.tool = DiffParseTool()

    def test_empty_and_type_inputs(self):
        """Non-string, blank, and unknown-mode inputs become structured errors."""
        self.assertEqual(self.tool.execute(mode="validate", diff=None)["status"], "error")
        self.assertEqual(self.tool.execute(mode="validate", diff="   ")["error_type"], "validation_error")
        self.assertEqual(self.tool.execute(mode="nope", diff="x")["error_type"], "validation_error")

    def test_empty_body_line_is_rejected_but_blank_context_is_legal(self):
        """A blank context line is ' ' + ''; a fully empty body line is not."""
        blank_ok = self.tool.execute(mode="validate", diff=BSD_BLANK_CONTEXT)
        self.assertTrue(blank_ok["valid"])
        broken = "--- a\n+++ b\n@@ -1,2 +1,2 @@\n x\n\n-y\n+z\n"
        result = self.tool.execute(mode="validate", diff=broken)
        self.assertFalse(result["valid"])
        self.assertIn("E_EMPTY_BODY_LINE", error_codes(result))

    def test_header_order_and_pairing(self):
        """Every --- needs a following +++; +++ cannot come first."""
        swapped = "+++ b/x\n--- a/x\n@@ -1 +1 @@\n-x\n+y\n"
        self.assertIn("E_HEADER_ORDER", error_codes(self.tool.execute(mode="validate", diff=swapped)))
        orphan = "--- a/x\n+++ b/x\n@@ -1 +1 @@\n-x\n+y\n+++ b/y\n--- a/y\n@@ -1 +1 @@\n-p\n+q\n"
        result = self.tool.execute(mode="validate", diff=orphan)
        self.assertFalse(result["valid"])
        self.assertIn("E_HEADER_ORDER", error_codes(result))
        missing = "--- a/x\n@@ -1 +1 @@\n-x\n+y\n"
        self.assertIn("E_HEADER_ORDER", error_codes(self.tool.execute(mode="validate", diff=missing)))

    def test_hunk_grammar_variants(self):
        """Malformed @@ headers and start-0-with-count are grammar errors."""
        for bad in (
            "@@-1,2 +1,2@@\n x\n-y\n+z\n",
            "@@ -a,2 +1,2 @@\n x\n-y\n+z\n",
            "@@ -0,3 +1,3 @@\n a\n b\n c\n",
            "@@ -1,3 +0,3 @@\n a\n b\n c\n",
        ):
            text = "--- a\n+++ b\n" + bad
            result = self.tool.execute(mode="validate", diff=text)
            self.assertFalse(result["valid"], bad)
            self.assertIn("E_HUNK_GRAMMAR", error_codes(result), bad)
        truncated = "--- a\n+++ b\n@@ -1,2 +1,2 @@\n-x\n"
        result = self.tool.execute(mode="validate", diff=truncated)
        self.assertFalse(result["valid"])
        self.assertTrue(set(error_codes(result)) & {"E_HUNK_COUNT_OLD", "E_HUNK_COUNT_NEW"})

    def test_zero_count_forms_are_legal(self):
        """-0,0 new-file and -N,0 insertion forms must validate cleanly."""
        self.assertTrue(self.tool.execute(mode="validate", diff=SPEC_COUNT_OMITTED)["valid"])
        self.assertTrue(self.tool.execute(mode="validate", diff=BSD_DEV_NULL)["valid"])
        insertion = "--- a\n+++ b\n@@ -2,0 +3,2 @@\n+x\n+y\n"
        self.assertTrue(self.tool.execute(mode="validate", diff=insertion)["valid"])

    def test_hunk_arithmetic_reports_side_and_expected_vs_actual(self):
        """Count mismatches name the side and both numbers."""
        old_short = "--- a\n+++ b\n@@ -1,3 +1,2 @@\n x\n-y\n+z\n"
        result = self.tool.execute(mode="validate", diff=old_short)
        self.assertFalse(result["valid"])
        codes = error_codes(result)
        self.assertIn("E_HUNK_COUNT_OLD", codes)
        message = [f["message"] for f in result["findings"] if f["code"] == "E_HUNK_COUNT_OLD"][0]
        self.assertIn("expects 3", message)
        self.assertIn("found 2", message)
        new_short = "--- a\n+++ b\n@@ -1,2 +1,3 @@\n x\n-y\n+z\n"
        self.assertIn("E_HUNK_COUNT_NEW", error_codes(self.tool.execute(mode="validate", diff=new_short)))

    def test_marker_placement_rules(self):
        """Markers must follow a body line and cannot repeat for one line."""
        after_header = "--- a\n+++ b\n@@ -1,3 +1,3 @@\n\\ No newline at end of file\n a\n-a\n+b\n"
        self.assertIn(
            "E_NO_NEWLINE_MARKER", error_codes(self.tool.execute(mode="validate", diff=after_header))
        )
        duplicated = (
            "--- a\n+++ b\n@@ -1,2 +1,2 @@\n-a\n\\ No newline at end of file\n"
            "\\ No newline at end of file\n+b\n"
        )
        result = self.tool.execute(mode="validate", diff=duplicated)
        self.assertFalse(result["valid"])

    def test_extra_body_line_after_satisfied_counts(self):
        """A body line beyond the declared counts is an error."""
        extra = "--- a\n+++ b\n@@ -1,2 +1,2 @@\n x\n-y\n+z\n+surprise\n"
        result = self.tool.execute(mode="validate", diff=extra)
        self.assertFalse(result["valid"])
        self.assertTrue(error_codes(result))

    def test_hunk_ordering(self):
        """Backwards or overlapping hunks are rejected."""
        backwards = (
            "--- a\n+++ b\n@@ -5,2 +5,2 @@\n e\n-f\n+F\n@@ -1,2 +1,2 @@\n a\n-b\n+B\n"
        )
        result = self.tool.execute(mode="validate", diff=backwards)
        self.assertFalse(result["valid"])
        self.assertIn("E_HUNK_ORDER", error_codes(result))

    def test_empty_diff_and_header_only_rejected(self):
        """A header pair without hunks is invalid; identical files emit nothing."""
        result = self.tool.execute(mode="validate", diff="--- a\n+++ b\n")
        self.assertFalse(result["valid"])
        self.assertIn("E_SECTION_EMPTY", error_codes(result))

    def test_eof_without_final_newline_warns_but_validates(self):
        """A diff truncated of its last newline still parses with a warning."""
        text = "--- a\n+++ b\n@@ -1 +1 @@\n-x\n+y"
        result = self.tool.execute(mode="validate", diff=text)
        self.assertTrue(result["valid"])
        self.assertIn("W_NO_EOF_NEWLINE", finding_codes(result))
        self.assertFalse(result["final_newline"])


class GitExtrasTest(unittest.TestCase):
    """git diff prelude recognition, statuses, and rejection rules."""

    def setUp(self):
        self.tool = DiffParseTool()

    def test_real_git_multi_file_output(self):
        """Captured git diff validates and classifies all three files."""
        result = self.tool.execute(mode="validate", diff=GIT_MULTI)
        self.assertTrue(result["valid"], result["findings"])
        self.assertEqual(result["files"], 3)
        self.assertEqual(result["hunks"], 3)
        self.assertEqual(result["summary"]["modified"], 1)
        self.assertEqual(result["summary"]["deleted"], 1)
        self.assertEqual(result["summary"]["added"], 1)

    def test_rename_and_binary_sections(self):
        """Rename-only and binary sections validate without hunks."""
        self.assertTrue(self.tool.execute(mode="validate", diff=GIT_RENAME)["valid"])
        result = self.tool.execute(mode="validate", diff=GIT_BINARY)
        self.assertTrue(result["valid"])
        self.assertIn("W_BINARY_SKIPPED", finding_codes(result))

    def test_binary_section_rejects_following_hunks(self):
        """Hunks after 'Binary files ... differ' are a grammar error."""
        text = GIT_BINARY + "@@ -0,0 +1 @@\n+nope\n"
        result = self.tool.execute(mode="validate", diff=text)
        self.assertFalse(result["valid"])
        self.assertIn("E_BINARY_WITH_HUNKS", error_codes(result))

    def test_git_binary_patch_payload_skipped(self):
        """'GIT binary patch' bodies are skipped up to the next git header."""
        text = (
            "diff --git a/x.bin b/x.bin\nindex 123..456 100644\nGIT binary patch\n"
            "zcmZ9hzp-=yQH5@|NV2Z\nliteral 12\nZcmYe|aWY${\n\n"
            "diff --git a/y.txt b/y.txt\n--- a/y.txt\n+++ b/y.txt\n@@ -1 +1 @@\n-a\n+b\n"
        )
        result = self.tool.execute(mode="validate", diff=text)
        self.assertEqual(result["files"], 2)
        self.assertEqual(result["summary"]["binary"], 1)
        self.assertEqual(result["summary"]["modified"], 1)
        self.assertIn("W_BINARY_SKIPPED", finding_codes(result))

    def test_apply_check_rejects_multi_file_structurally(self):
        """Multi-file apply_check fails with a structured error listing files."""
        result = self.tool.execute(mode="apply_check", diff=GIT_MULTI, original_text="alpha\n")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "multi_file_diff")
        self.assertEqual(result["files"], ["file.txt", "/dev/null", "new.txt"])


class ApplyCheckTest(unittest.TestCase):
    """apply_check context verification and no-fuzz policy."""

    def setUp(self):
        self.tool = DiffParseTool()

    def test_real_git_diff_applies(self):
        """The captured modification diff applies to its original content."""
        original = "alpha\nbeta\ngamma\ndelta\nepsilon\n"
        result = self.tool.execute(mode="apply_check", diff=GIT_MODIFY, original_text=original)
        self.assertTrue(result["applies"], result)
        self.assertEqual(len(result["per_hunk"]), 1)
        entry = result["per_hunk"][0]
        self.assertTrue(entry["context_matches"])
        self.assertIsNone(entry["first_mismatch_line"])

    def test_new_and_deleted_files_apply(self):
        """New files apply to empty text; deletions apply to full text."""
        self.assertTrue(
            self.tool.execute(mode="apply_check", diff=GIT_NEW_FILE, original_text="")["applies"]
        )
        self.assertTrue(
            self.tool.execute(
                mode="apply_check", diff=GIT_DELETE, original_text="one\ntwo\nthree\n"
            )["applies"]
        )

    def test_context_drift_is_caught_with_line_number(self):
        """Drifted context validates but fails apply_check at the drift line."""
        drifted = "--- a\n+++ b\n@@ -1,3 +1,3 @@\n aaa\n-bbb\n+BBB\n ccc\n"
        self.assertTrue(self.tool.execute(mode="validate", diff=drifted)["valid"])
        result = self.tool.execute(mode="apply_check", diff=drifted, original_text="aaa\nXXX\nccc\n")
        self.assertFalse(result["applies"])
        self.assertEqual(result["reject_reason"], "context_mismatch")
        self.assertEqual(result["per_hunk"][0]["first_mismatch_line"], 2)

    def test_no_fuzz_policy(self):
        """Context that matches one line off is rejected (no offset search)."""
        diff = "--- a\n+++ b\n@@ -1,2 +1,2 @@\n alpha\n-beta\n+BETA\n"
        shifted = "pad\nalpha\nbeta\n"
        result = self.tool.execute(mode="apply_check", diff=diff, original_text=shifted)
        self.assertFalse(result["applies"])

    def test_missing_original_text_is_an_error(self):
        """apply_check without original_text returns a structured error."""
        result = self.tool.execute(mode="apply_check", diff=GIT_MODIFY)
        self.assertEqual(result["status"], "error")

    def test_invalid_diff_short_circuits_apply(self):
        """Grammar failures are reported instead of a misleading mismatch."""
        broken = "--- a\n+++ b\n@@ -1,5 +1,2 @@\n x\n-y\n+z\n"
        result = self.tool.execute(mode="apply_check", diff=broken, original_text="x\ny\n")
        self.assertFalse(result["applies"])
        self.assertEqual(result["reject_reason"], "invalid_diff")

    def test_no_newline_marker_consistency(self):
        """Old-side markers must agree with the original's final newline."""
        applies = self.tool.execute(
            mode="apply_check", diff=BSD_NO_NEWLINE, original_text="a\nb\nc"
        )
        self.assertTrue(applies["applies"])
        wrong = self.tool.execute(
            mode="apply_check", diff=BSD_NO_NEWLINE, original_text="a\nb\nc\n"
        )
        self.assertFalse(wrong["applies"])
        self.assertIn("newline_marker_mismatch", wrong["reject_reason"])

    def test_git_no_newline_both_sides(self):
        """The captured git diff with two markers applies both directions."""
        original = "a\nb\nc"
        result = self.tool.execute(mode="apply_check", diff=GIT_NO_NEWLINE, original_text=original)
        self.assertTrue(result["applies"], result)

    def test_crlf_transport_applies_to_both_endings(self):
        """Uniform CRLF transport is tolerated against LF and CRLF originals."""
        self.assertTrue(
            self.tool.execute(
                mode="apply_check", diff=CRLF_TRANSPORT, original_text="aa\r\nbb\r\n"
            )["applies"]
        )
        self.assertTrue(
            self.tool.execute(mode="apply_check", diff=CRLF_TRANSPORT, original_text="aa\nbb\n")[
                "applies"
            ]
        )

    def test_crlf_content_compared_exactly(self):
        """CRLF content transported over LF matches only a CRLF original."""
        self.assertTrue(
            self.tool.execute(
                mode="apply_check", diff=CRLF_CONTENT, original_text="aa\r\nbb\r\n"
            )["applies"]
        )
        self.assertFalse(
            self.tool.execute(mode="apply_check", diff=CRLF_CONTENT, original_text="aa\nbb\n")[
                "applies"
            ]
        )

    def test_multi_hunk_offsets(self):
        """Later hunks apply with the accumulated offset of earlier ones."""
        original = "\n".join(f"line{i}" for i in range(1, 21)) + "\n"
        changed = [f"line{i}" for i in range(1, 21)]
        changed[2] = "CHANGED3"
        changed.insert(10, "INSERTED")
        changed.pop(17)
        new_text = "\n".join(changed) + "\n"
        diff = "".join(
            difflib.unified_diff(
                original.splitlines(True), new_text.splitlines(True), fromfile="a/f", tofile="b/f", n=1
            )
        )
        result = self.tool.execute(mode="apply_check", diff=diff, original_text=original)
        self.assertTrue(result["applies"], result)
        self.assertGreaterEqual(len(result["per_hunk"]), 2)


class ReverseTest(unittest.TestCase):
    """reverse output validity and round-trip invariant."""

    def setUp(self):
        self.tool = DiffParseTool()

    def test_reverse_is_valid_and_round_trips(self):
        """reverse(d) validates and applying it to the new text yields the old."""
        original = "alpha\nbeta\ngamma\ndelta\nepsilon\n"
        new_text = "alpha\nBETA\ngamma\ndelta\nEPSILON\n"
        result = self.tool.execute(mode="reverse", diff=GIT_MODIFY, new_text=new_text)
        self.assertTrue(result["valid"])
        self.assertTrue(result["round_trip"])
        back = self.tool.execute(mode="apply_check", diff=result["diff"], original_text=new_text)
        self.assertTrue(back["applies"])
        section = diff_module.DiffParseTool()._parse(result["diff"]).files[0]
        _ok, _entries, produced, _why = diff_module.DiffParseTool()._simulate(section, new_text)
        self.assertEqual(produced, original)

    def test_reverse_swaps_paths_ranges_and_markers(self):
        """Headers swap; -0,0 forms flip sides; markers follow their lines."""
        result = self.tool.execute(mode="reverse", diff=GIT_NEW_FILE)
        self.assertTrue(result["valid"])
        self.assertIn("--- b/new.txt", result["diff"])
        self.assertIn("+++ /dev/null", result["diff"])
        self.assertIn("@@ -1,2 +0,0 @@", result["diff"])
        self.assertIn("-brand new", result["diff"])
        no_newline = self.tool.execute(mode="reverse", diff=BSD_NO_NEWLINE)
        self.assertIn("\\ No newline at end of file\n", no_newline["diff"] + "\n")
        self.assertTrue(no_newline["valid"])

    def test_reverse_section_headings_preserved(self):
        """Trailing @@ section annotations survive reversal."""
        result = self.tool.execute(mode="reverse", diff=SPEC_SECTION_HEADING)
        self.assertIn("@@ -1,3 +1,3 @@ def foo():", result["diff"])

    def test_reverse_reports_dropped_git_headers_and_skips(self):
        """Git prelude lines are counted; rename-only sections are skipped."""
        result = self.tool.execute(mode="reverse", diff=GIT_MULTI)
        self.assertGreater(result["git_headers_dropped"], 0)
        self.assertTrue(result["valid"])
        renamed = self.tool.execute(mode="reverse", diff=GIT_RENAME)
        self.assertEqual(renamed["status"], "error")
        self.assertIn("no_hunks", renamed["error"])
        binary = self.tool.execute(mode="reverse", diff=GIT_BINARY)
        self.assertEqual(binary["status"], "error")

    def test_double_reverse_is_identity(self):
        """reverse(reverse(d)) reproduces d byte for byte (plain diffs)."""
        for d in (SPEC_SECTION_HEADING, BSD_NO_NEWLINE, SPEC_COUNT_OMITTED):
            once = self.tool.execute(mode="reverse", diff=d)["diff"]
            twice = self.tool.execute(mode="reverse", diff=once)["diff"]
            self.assertEqual(twice, d)

    def test_reverse_of_invalid_diff_is_refused(self):
        """Reversing a broken diff returns valid=False with its findings."""
        broken = "--- a\n+++ b\n@@ -1,5 +1,2 @@\n x\n-y\n+z\n"
        result = self.tool.execute(mode="reverse", diff=broken)
        self.assertFalse(result["valid"])
        self.assertIsNone(result["diff"])

    def test_crlf_transport_reverse_round_trip(self):
        """Reversed CRLF diffs stay CRLF and round-trip on CRLF text."""
        result = self.tool.execute(mode="reverse", diff=CRLF_TRANSPORT, new_text="aa\r\nBB\r\n")
        self.assertTrue(result["valid"])
        self.assertTrue(result["round_trip"])
        self.assertIn("\r\n", result["diff"])


class StatsTest(unittest.TestCase):
    """stats per-file numbers, totals, and churn hotspots."""

    def setUp(self):
        self.tool = DiffParseTool()

    def test_real_git_stats(self):
        """Captured git diff yields accurate per-file counts and statuses."""
        result = self.tool.execute(mode="stats", diff=GIT_MULTI)
        files = result["files"]
        self.assertEqual([f["status"] for f in files], ["modified", "deleted", "added"])
        self.assertEqual(files[0]["path_old"], "file.txt")
        self.assertEqual(files[0]["add_lines"], 2)
        self.assertEqual(files[0]["del_lines"], 2)
        self.assertEqual(files[0]["net"], 0)
        self.assertEqual(files[1]["path_new"], "/dev/null")
        self.assertEqual(files[2]["path_old"], "/dev/null")
        self.assertEqual(result["totals"]["add_lines"], 4)
        self.assertEqual(result["totals"]["del_lines"], 5)
        self.assertEqual(result["totals"]["net"], -1)

    def test_rename_and_binary_paths_resolve(self):
        """Rename/binary sections take paths from rename extras / git header."""
        stats = self.tool.execute(mode="stats", diff=GIT_RENAME)["files"][0]
        self.assertEqual((stats["path_old"], stats["path_new"]), ("orig.txt", "renamed.txt"))
        self.assertEqual(stats["status"], "renamed")
        binary = self.tool.execute(mode="stats", diff=GIT_BINARY)["files"][0]
        self.assertEqual(binary["status"], "binary")
        self.assertEqual(binary["path_new"], "bin.dat")

    def test_hotspots_rank_changed_hunks(self):
        """Hotspots list the three most-changed hunks, deterministically."""
        text = "\n".join(f"l{i}" for i in range(1, 61)) + "\n"
        changed = [f"l{i}" for i in range(1, 61)]
        for i in (5, 6, 7, 30, 31, 55):
            changed[i] = f"X{i}"
        new_text = "\n".join(changed) + "\n"
        diff = "".join(
            difflib.unified_diff(text.splitlines(True), new_text.splitlines(True), n=0)
        )
        result = self.tool.execute(mode="stats", diff=diff)
        self.assertEqual(result["totals"]["add_lines"], 6)
        top = result["hotspots"][0]
        self.assertGreaterEqual(top["changed_lines"], 1)
        self.assertEqual(len(result["hotspots"]), 3)
        ranges = [tuple(h["old_range"]) for h in result["hotspots"]]
        self.assertEqual(ranges, sorted(ranges, key=lambda r: r[0]))


class QuotedPathTest(unittest.TestCase):
    """GNU quoted-path headers with escapes decode correctly."""

    def setUp(self):
        self.tool = DiffParseTool()

    def test_quoted_paths_validate_and_decode(self):
        """Quoted headers validate; stats expose the decoded paths."""
        result = self.tool.execute(mode="validate", diff=GNU_QUOTED)
        self.assertTrue(result["valid"], result["findings"])
        stats = self.tool.execute(mode="stats", diff=GNU_QUOTED)["files"][0]
        self.assertEqual(stats["path_old"], "dir with space/f\t1.txt")
        self.assertEqual(stats["path_new"], "dir with space/f\t2.txt")

    def test_unclosed_quote_is_an_error(self):
        """A quoted path missing its closing quote is flagged."""
        text = '--- "unclosed\n+++ b\n@@ -1 +1 @@\n-x\n+y\n'
        result = self.tool.execute(mode="validate", diff=text)
        self.assertIn("E_ESCAPE", error_codes(result))


class DifflibOracleTest(unittest.TestCase):
    """(a) 500 seeded difflib diffs must validate, apply, and round-trip."""

    def setUp(self):
        self.tool = DiffParseTool()
        self.rng = random.Random(20261021)

    def _pair(self):
        """Build one seeded (a, b) text pair; a is sometimes empty."""
        line_count = self.rng.randint(0, 24)
        alphabet = ["alpha", "beta", "gamma", "delta", "", " x", "tab\there", "üñí", "1", "--dash", "+++plus"]
        a_lines = [self.rng.choice(alphabet) + "\n" for _ in range(line_count)]
        b_lines = list(a_lines)
        if a_lines and self.rng.random() < 0.7:
            for _ in range(self.rng.randint(1, 6)):
                op = self.rng.choice(["edit", "insert", "delete"])
                if op == "edit" and b_lines:
                    pos = self.rng.randrange(len(b_lines))
                    b_lines[pos] = self.rng.choice(alphabet) + "\n"
                elif op == "insert":
                    b_lines.insert(self.rng.randint(0, len(b_lines)), self.rng.choice(alphabet) + "\n")
                elif op == "delete" and b_lines:
                    b_lines.pop(self.rng.randrange(len(b_lines)))
        else:
            b_lines = [self.rng.choice(alphabet) + "\n" for _ in range(self.rng.randint(1, 10))]
        return a_lines, b_lines

    def test_difflib_battery(self):
        """Every generated diff validates, applies, and reverses cleanly."""
        checked = 0
        double_reverse_checked = 0
        for iteration in range(500):
            a_lines, b_lines = self._pair()
            if iteration % 2:
                a_lines, b_lines = b_lines, a_lines
            context = self.rng.choice([0, 1, 3])
            fromfile, tofile = self.rng.choice(
                [("a/x.txt", "b/x.txt"), ("old", "new"), ("a/dir/f.py", "b/dir/f.py")]
            )
            lineterm = self.rng.choice(["\n", ""])
            if lineterm == "\n":
                diff = "".join(
                    difflib.unified_diff(
                        a_lines, b_lines, fromfile=fromfile, tofile=tofile, n=context
                    )
                )
            else:
                # With lineterm='' the caller supplies newline-free lines and
                # joins the fragments itself.
                diff = "\n".join(
                    difflib.unified_diff(
                        [item[:-1] for item in a_lines],
                        [item[:-1] for item in b_lines],
                        fromfile=fromfile,
                        tofile=tofile,
                        n=context,
                        lineterm="",
                    )
                )
            if not diff.strip():
                self.assertEqual(a_lines, b_lines)
                continue
            original = "".join(a_lines)
            updated = "".join(b_lines)
            validated = self.tool.execute(mode="validate", diff=diff)
            self.assertTrue(validated["valid"], f"iter {iteration}: {validated['findings']}")
            self.assertEqual(validated["errors"], 0)
            applied = self.tool.execute(mode="apply_check", diff=diff, original_text=original)
            self.assertTrue(applied["applies"], f"iter {iteration}: {applied}")
            reversed_result = self.tool.execute(mode="reverse", diff=diff, new_text=updated)
            self.assertTrue(reversed_result["valid"], f"iter {iteration}: {reversed_result}")
            self.assertTrue(reversed_result["round_trip"], f"iter {iteration}: {reversed_result}")
            back = self.tool.execute(
                mode="apply_check", diff=reversed_result["diff"], original_text=updated
            )
            self.assertTrue(back["applies"])
            section = diff_module.DiffParseTool()._parse(reversed_result["diff"]).files[0]
            _ok, _entries, produced, _why = diff_module.DiffParseTool()._simulate(section, updated)
            self.assertEqual(produced, original, f"iter {iteration}: reverse apply mismatch")
            if iteration % 50 == 0:
                twice = self.tool.execute(mode="reverse", diff=reversed_result["diff"])["diff"]
                self.assertEqual(twice, diff, f"iter {iteration}: double reverse not identity")
                double_reverse_checked += 1
            checked += 1
        self.assertGreater(checked, 400)
        self.assertGreater(double_reverse_checked, 5)


class CorruptionOracleTest(unittest.TestCase):
    """(c) 300 seeded corruptions must be caught by validate or apply_check."""

    APPLY_LAYER = {"context_drift", "removed_line_edit"}

    def setUp(self):
        self.tool = DiffParseTool()
        self.rng = random.Random(25202525)

    def _base_pool(self):
        """Deterministic base diffs generated with difflib (context >= 1)."""
        pool = []
        rng = random.Random(998877)
        alphabet = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"]
        for _ in range(10):
            a = [rng.choice(alphabet) + "\n" for _ in range(rng.randint(4, 30))]
            b = list(a)
            for _ in range(rng.randint(1, 5)):
                op = rng.choice(["edit", "insert", "delete"])
                if op == "edit":
                    b[rng.randrange(len(b))] = rng.choice(alphabet).upper() + "\n"
                elif op == "insert":
                    b.insert(rng.randint(0, len(b)), rng.choice(alphabet) + "\n")
                elif len(b) > 1:
                    b.pop(rng.randrange(len(b)))
            diff = "".join(
                difflib.unified_diff(a, b, fromfile="a/base.txt", tofile="b/base.txt", n=3)
            )
            pool.append((diff, "".join(a), "".join(b)))
        return pool

    def _mutate(self, diff, rng):
        """Apply one seeded corruption; return (mutated, mutation_class).

        Every mutation is constructed so the result provably differs from the
        original semantics: tampered counts never reproduce the body counts,
        truncation always bites into the final hunk body, and zeroed counts
        always disagree with the surviving body lines.
        """
        lines = diff.split("\n")
        headers = [i for i, item in enumerate(lines) if item.startswith("@@ ")]
        old_lines = [i for i, item in enumerate(lines) if item.startswith("-") and not item.startswith("--- ")]
        add_lines = [i for i, item in enumerate(lines) if item.startswith("+") and not item.startswith("+++ ")]
        ctx_lines = [i for i, item in enumerate(lines) if item.startswith(" ") and item.strip()]
        choices = ["tamper_count", "drop_add", "drop_del", "drop_ctx", "swap_headers",
                   "break_grammar", "marker_after_header", "garbage_line", "truncate",
                   "double_minus", "zero_count", "context_drift", "removed_line_edit"]
        usable = list(choices)
        if not ctx_lines:
            usable.remove("drop_ctx")
            usable.remove("context_drift")
        if not old_lines:
            usable.remove("drop_del")
            usable.remove("removed_line_edit")
        if not add_lines:
            usable.remove("drop_add")
        kind = rng.choice(usable)
        if kind == "tamper_count":
            target = rng.choice(headers)
            head = lines[target]
            sign = "-" if rng.random() < 0.5 else "+"
            pos = head.find(sign, head.find("@@"))
            comma = head.find(",", pos)
            existing = int(head[comma + 1]) if comma != -1 and head[comma + 1].isdigit() else 1
            digit = str((existing + rng.randint(1, 8)) % 10)
            if comma == -1:
                lines[target] = head[: pos + 1] + f",{digit}" + head[pos + 1 :]
            else:
                lines[target] = head[: comma + 1] + digit + head[comma + 2 :]
        elif kind == "drop_add":
            del lines[rng.choice(add_lines)]
        elif kind == "drop_del":
            del lines[rng.choice(old_lines)]
        elif kind == "drop_ctx":
            del lines[rng.choice(ctx_lines)]
        elif kind == "swap_headers":
            minus = next(i for i, item in enumerate(lines) if item.startswith("--- "))
            plus = next(i for i, item in enumerate(lines) if item.startswith("+++ "))
            lines[minus], lines[plus] = lines[plus], lines[minus]
        elif kind == "break_grammar":
            target = rng.choice(headers)
            if rng.random() < 0.5:
                lines[target] = lines[target].replace("@@ -", "@@~-", 1)
            else:
                lines[target] = lines[target].replace(" @@", "", 1)
        elif kind == "marker_after_header":
            target = rng.choice(headers)
            lines.insert(target + 1, "\\ No newline at end of file")
        elif kind == "garbage_line":
            body = [i for i, item in enumerate(lines) if item[:1] in (" ", "+", "-") and i > headers[0]]
            lines.insert(rng.choice(body) + 1, "GARBAGE LINE")
        elif kind == "truncate":
            lines = lines[: max(2, len(lines) - rng.randint(2, 5))]
        elif kind == "double_minus":
            plus = next(i for i, item in enumerate(lines) if item.startswith("+++ "))
            lines[plus] = "--- " + lines[plus][4:]
        elif kind == "zero_count":
            target = rng.choice(headers)
            head = lines[target]
            comma = head.find(",", head.find("@@ -"))
            if comma != -1 and head[comma + 1].isdigit():
                lines[target] = head[: comma + 1] + "0" + head[comma + 2 :]
            else:
                lines[target] = head.replace(" +", " +1,0 ", 1)
        elif kind == "context_drift":
            target = rng.choice(ctx_lines)
            lines[target] = lines[target] + "X"
        elif kind == "removed_line_edit":
            target = rng.choice(old_lines)
            lines[target] = lines[target] + "Y"
        return "\n".join(lines), kind

    def test_corruption_battery(self):
        """All 300 corruptions are caught; the catching layer is adjudicated."""
        pool = self._base_pool()
        caught_by = {"validate": 0, "apply_check": 0}
        for step in range(300):
            diff, original, _updated = self.rng.choice(pool)
            mutated, kind = self._mutate(diff, self.rng)
            validated = self.tool.execute(mode="validate", diff=mutated)
            applied = self.tool.execute(mode="apply_check", diff=mutated, original_text=original)
            valid_flag = validated.get("valid", False)
            applies_flag = applied.get("applies", False)
            caught = (not valid_flag) or (not applies_flag)
            self.assertTrue(caught, f"step {step} ({kind}) escaped: {mutated!r}")
            if kind in self.APPLY_LAYER:
                self.assertTrue(
                    valid_flag,
                    f"step {step} ({kind}) should pass validate: {validated['findings']}",
                )
                self.assertFalse(applies_flag, f"step {step} ({kind}) should fail apply")
                caught_by["apply_check"] += 1
            else:
                self.assertFalse(
                    valid_flag,
                    f"step {step} ({kind}) should fail validate: {mutated!r}",
                )
                caught_by["validate"] += 1
        self.assertGreater(caught_by["validate"], 100)
        self.assertGreater(caught_by["apply_check"], 20)


class PathologicalTest(unittest.TestCase):
    """(d) Bounds: timing on large diffs, long lines, and cap enforcement."""

    def setUp(self):
        self.tool = DiffParseTool()

    def test_ten_thousand_line_diff_under_two_seconds(self):
        """A 10k-line diff validates and applies in under two seconds."""
        a = [f"line {i} content here\n" for i in range(10_000)]
        b = list(a)
        for i in range(0, 10_000, 3):
            b[i] = f"CHANGED {i} different content\n"
        original = "".join(a)
        diff = "".join(
            difflib.unified_diff(a, b, fromfile="a/big.txt", tofile="b/big.txt", n=1)
        )
        self.assertGreater(len(diff.splitlines()), 10_000)
        start = time.perf_counter()
        validated = self.tool.execute(mode="validate", diff=diff)
        applied = self.tool.execute(mode="apply_check", diff=diff, original_text=original)
        elapsed = time.perf_counter() - start
        self.assertTrue(validated["valid"], validated["findings"][:3])
        self.assertTrue(applied["applies"])
        self.assertLess(elapsed, 2.0, f"validate+apply took {elapsed:.2f}s")

    def test_one_megabyte_single_line_is_bounded(self):
        """A 1MB unchanged context line validates and applies (with warning)."""
        huge = "P" * 1_000_000
        original = huge + "\ntail\n"
        updated = huge + "\nTAIL\n"
        diff = "".join(
            difflib.unified_diff(
                original.splitlines(True), updated.splitlines(True), fromfile="a/h", tofile="b/h", n=1
            )
        )
        start = time.perf_counter()
        validated = self.tool.execute(mode="validate", diff=diff)
        applied = self.tool.execute(mode="apply_check", diff=diff, original_text=original)
        elapsed = time.perf_counter() - start
        self.assertTrue(validated["valid"])
        self.assertIn("W_LONG_LINE", finding_codes(validated))
        self.assertTrue(applied["applies"])
        self.assertLess(elapsed, 2.0)

    def test_cap_violations_return_structured_errors(self):
        """Byte, line, and line-length caps produce validation_error results."""
        tiny_bytes = DiffParseTool(max_input_bytes=100)
        result = tiny_bytes.execute(mode="validate", diff="x" * 200 + "\n")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("max_input_bytes", result["error"])
        tiny_line = DiffParseTool(max_input_bytes=1000, max_line_bytes=50, warn_line_bytes=20)
        long_line = "--- a\n+++ b\n@@ -1 +1 @@\n-" + "y" * 80 + "\n"
        self.assertIn("max_line_bytes", tiny_line.execute(mode="validate", diff=long_line)["error"])
        tiny_lines = DiffParseTool(max_input_bytes=2000, max_lines=10, max_line_bytes=200, warn_line_bytes=20)
        many = "--- a\n+++ b\n@@ -1,20 +1,20 @@\n" + " z\n" * 20
        self.assertIn("max_lines", tiny_lines.execute(mode="validate", diff=many)["error"])

    def test_finding_cap_truncates_gracefully(self):
        """Findings stop at max_findings and set findings_truncated."""
        capped = DiffParseTool(max_findings=5)
        lines = ["--- a", "+++ b", "@@ -1,3 +1,3 @@"]
        lines += ["GARBAGE"] * 40
        result = capped.execute(mode="validate", diff="\n".join(lines) + "\n")
        self.assertLessEqual(len(result["findings"]), 5)
        self.assertTrue(result["findings_truncated"])

    def test_stats_on_invalid_diff_reports_findings(self):
        """stats still returns counts plus the collected findings."""
        broken = "--- a\n+++ b\n@@ -1,3 +1,2 @@\n x\n-y\n+z\n"
        result = self.tool.execute(mode="stats", diff=broken)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["files"]), 1)
        self.assertTrue(error_codes(result))


class DiffParseToolRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped diff_parse_tool.yaml."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """The shipped yaml resolves to a tool component exposing DiffParseTool."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "DiffParseTool")

    def test_manager(self):
        """DiffParseTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, DiffParseTool)
        self.assertEqual(tool.input_keys, ["mode", "diff"])

    def test_package_export(self):
        """DiffParseTool is exported from the common_tool package."""
        from agentuniverse.agent.action.tool.common_tool import DiffParseTool as Exported
        from agentuniverse.agent.action.tool.common_tool import __all__ as exported_names

        self.assertIs(Exported, DiffParseTool)
        self.assertIn("DiffParseTool", exported_names)


# Real `git diff` outputs captured with core.quotePath=true (git's default):
# octal escapes are the UTF-8 bytes of the filename characters.
REAL_MODE_ONLY = "diff --git a/mfile.txt b/mfile.txt\nold mode 100644\nnew mode 100755\n"

REAL_GIT_MIXED_QUOTED = (
    'diff --git a/uni.txt "b/\\303\\274\\303\\261\\303\\255\\342\\234\\223.txt"\n'
    "similarity index 100%\n"
    "rename from uni.txt\n"
    'rename to "\\303\\274\\303\\261\\303\\255\\342\\234\\223.txt"\n'
)

REAL_GIT_UNICODE_MODIFY = (
    'diff --git "a/f\\303\\251\\302\\247\\350\\267\\257\\345\\276\\204.txt" "b/f\\303\\251\\302\\247\\350\\267\\257\\345\\276\\204.txt"\n'
    "index 7a13beb..1651ae8 100644\n"
    '--- "a/f\\303\\251\\302\\247\\350\\267\\257\\345\\276\\204.txt"\n'
    '+++ "b/f\\303\\251\\302\\247\\350\\267\\257\\345\\276\\204.txt"\n'
    "@@ -1,2 +1,2 @@\n"
    " unicode content\n"
    "-second line\n"
    "+second line changed\n"
)

# git writes paths containing spaces unquoted in the ambiguous
# `diff --git a/a b.txt b/a b.txt` form; GNU patch splits at the ' b/'.
REAL_SPACE_PATH_HEADER = "diff --git a/a b.txt b/a b.txt\nold mode 100644\nnew mode 100755\n"

REAL_SPACE_RENAME = (
    "diff --git a/plain1.txt b/plain one.txt\n"
    "similarity index 100%\n"
    "rename from plain1.txt\n"
    "rename to plain one.txt\n"
)


class HostileReviewRegressionTest(unittest.TestCase):
    """Regressions for defects found by hostile self-review (PR #4050).

    Every case below was a provable disagreement with real `git diff`,
    `diff -u`, `difflib`, or `patch(1)` behavior before the fix.
    """

    def setUp(self):
        self.tool = DiffParseTool()

    # -- real git output shapes -------------------------------------------

    def test_mode_change_only_diff_is_valid(self):
        """A pure permission change emits only old/new mode lines; no error."""
        result = self.tool.execute(mode="validate", diff=REAL_MODE_ONLY)
        self.assertTrue(result["valid"], result["findings"])
        self.assertEqual(result["files"], 1)
        self.assertEqual(result["hunks"], 0)
        stats = self.tool.execute(mode="stats", diff=REAL_MODE_ONLY)["files"][0]
        self.assertEqual((stats["path_old"], stats["path_new"]), ("mfile.txt", "mfile.txt"))
        self.assertEqual(stats["status"], "modified")
        reversed_result = self.tool.execute(mode="reverse", diff=REAL_MODE_ONLY)
        self.assertEqual(reversed_result["status"], "error")
        self.assertIn("no_hunks", reversed_result["error"])

    def test_index_only_git_section_still_rejected(self):
        """An index line alone is not a real git section and stays an error."""
        text = "diff --git a/x b/x\nindex 0123456..89abcde 100644\n"
        result = self.tool.execute(mode="validate", diff=text)
        self.assertFalse(result["valid"])
        self.assertIn("E_HEADER_MISSING", error_codes(result))

    def test_octal_quoted_paths_decode_as_utf8_bytes(self):
        """core.quotePath octal escapes are UTF-8 bytes, not latin-1 codepoints."""
        result = self.tool.execute(mode="validate", diff=REAL_GIT_UNICODE_MODIFY)
        self.assertTrue(result["valid"], result["findings"])
        stats = self.tool.execute(mode="stats", diff=REAL_GIT_UNICODE_MODIFY)["files"][0]
        self.assertEqual(stats["path_old"], "fé§路径.txt")
        self.assertEqual(stats["path_new"], "fé§路径.txt")
        applied = self.tool.execute(
            mode="apply_check",
            diff=REAL_GIT_UNICODE_MODIFY,
            original_text="unicode content\nsecond line\n",
        )
        self.assertTrue(applied["applies"])

    def test_mixed_quoted_git_header_and_rename_extras_decode(self):
        """Quoted b-side and quoted rename-to values decode; unquoted a-side wins."""
        result = self.tool.execute(mode="validate", diff=REAL_GIT_MIXED_QUOTED)
        self.assertTrue(result["valid"], result["findings"])
        stats = self.tool.execute(mode="stats", diff=REAL_GIT_MIXED_QUOTED)["files"][0]
        self.assertEqual((stats["path_old"], stats["path_new"]), ("uni.txt", "üñí✓.txt"))
        self.assertEqual(stats["status"], "renamed")

    def test_space_in_git_header_paths_split_at_b_slash(self):
        """`diff --git a/a b.txt b/a b.txt` resolves to ('a b.txt', 'a b.txt')."""
        stats = self.tool.execute(mode="stats", diff=REAL_SPACE_PATH_HEADER)["files"][0]
        self.assertEqual((stats["path_old"], stats["path_new"]), ("a b.txt", "a b.txt"))
        rename = self.tool.execute(mode="stats", diff=REAL_SPACE_RENAME)["files"][0]
        self.assertEqual((rename["path_old"], rename["path_new"]), ("plain1.txt", "plain one.txt"))
        self.assertTrue(self.tool.execute(mode="validate", diff=REAL_SPACE_RENAME)["valid"])

    # -- '\ No newline' semantics ------------------------------------------

    def test_duplicate_marker_with_balanced_counts_is_rejected(self):
        """Two markers for one body line are malformed even when counts balance."""
        text = (
            "--- a\n+++ b\n@@ -1,2 +1,2 @@\n a\n-b\n"
            "\\ No newline at end of file\n\\ No newline at end of file\n+C\n"
        )
        result = self.tool.execute(mode="validate", diff=text)
        self.assertFalse(result["valid"])
        self.assertIn("E_NO_NEWLINE_MARKER", error_codes(result))

    def test_marker_above_a_line_that_is_not_last_of_its_side(self):
        """A no-newline line can never be followed by same-side lines."""
        context_form = (
            "--- a\n+++ b\n@@ -1,4 +1,4 @@\n a\n b\n"
            "\\ No newline at end of file\n-c\n+C\n d\n"
        )
        result = self.tool.execute(mode="validate", diff=context_form)
        self.assertFalse(result["valid"])
        self.assertIn("E_NO_NEWLINE_MARKER", error_codes(result))
        minus_form = (
            "--- a\n+++ b\n@@ -1,4 +1,4 @@\n a\n-b\n"
            "\\ No newline at end of file\n-c\n+C\n+D\n d\n"
        )
        result = self.tool.execute(mode="validate", diff=minus_form)
        self.assertFalse(result["valid"])
        self.assertIn("E_NO_NEWLINE_MARKER", error_codes(result))

    def test_marker_in_earlier_hunk_with_later_hunk_rejected(self):
        """The old side continues into a later hunk, so its marker is impossible."""
        text = (
            "--- a\n+++ b\n@@ -1,2 +1,2 @@\n a\n-b\n+B\n"
            "\\ No newline at end of file\n@@ -4,3 +4,3 @@\n d\n-e\n+E\n f\n"
        )
        result = self.tool.execute(mode="validate", diff=text)
        self.assertFalse(result["valid"])
        self.assertIn("E_NO_NEWLINE_MARKER", error_codes(result))

    def test_legal_marker_placements_still_validate(self):
        """Final-line markers (one per side, context end, both sides) stay legal."""
        both_sides = (
            "--- a\n+++ b\n@@ -1 +1 @@\n-old\n\\ No newline at end of file\n"
            "+new\n\\ No newline at end of file\n"
        )
        self.assertTrue(self.tool.execute(mode="validate", diff=both_sides)["valid"])
        final_context = "--- a\n+++ b\n@@ -1,3 +1,3 @@\n a\n b\n c\n\\ No newline at end of file\n"
        result = self.tool.execute(mode="validate", diff=final_context)
        self.assertTrue(result["valid"], result["findings"])
        # old-side marker while the new side gains lines afterwards is fine
        old_only = (
            "--- a\n+++ b\n@@ -1,2 +1,3 @@\n a\n-b\n\\ No newline at end of file\n+B\n+C\n"
        )
        result = self.tool.execute(mode="validate", diff=old_only)
        self.assertTrue(result["valid"], result["findings"])

    # -- hunk start arithmetic ---------------------------------------------

    def test_tampered_new_start_is_rejected(self):
        """patch(1) fails these; the offset invariant must catch them statically."""
        tampered_second = (
            "--- a\n+++ b\n@@ -1,3 +1,3 @@\n a\n-b\n+B\n c\n"
            "@@ -4,3 +5,3 @@\n d\n-e\n+E\n f\n"
        )
        result = self.tool.execute(mode="validate", diff=tampered_second)
        self.assertFalse(result["valid"])
        self.assertIn("E_HUNK_OFFSET", error_codes(result))
        tampered_first = "--- a\n+++ b\n@@ -1,3 +2,3 @@\n a\n-b\n+B\n c\n"
        self.assertIn(
            "E_HUNK_OFFSET",
            error_codes(self.tool.execute(mode="validate", diff=tampered_first)),
        )

    def test_tampered_old_start_forward_is_rejected(self):
        """A forward old-start shift escapes E_HUNK_ORDER; offsets still catch it.

        Hunk 2 claims the unchanged gap between the hunks is one line on the
        old side but zero lines on the new side, which no real diff produces.
        """
        text = (
            "--- a\n+++ b\n@@ -1,2 +1,2 @@\n a\n-b\n+B\n"
            "@@ -4,2 +3,2 @@\n c\n-d\n+D\n"
        )
        result = self.tool.execute(mode="validate", diff=text)
        self.assertFalse(result["valid"])
        self.assertIn("E_HUNK_OFFSET", error_codes(result))

    def test_consistent_zero_count_offsets_still_validate(self):
        """Insertion/deletion/new-file zero-count forms keep exact arithmetic."""
        for text in (
            "--- a\n+++ b\n@@ -2,0 +3,2 @@\n+x\n+y\n",
            "--- a\n+++ b\n@@ -1,2 +0,0 @@\n-a\n-b\n",
            "--- a\n+++ b\n@@ -0,0 +1,3 @@\n+1\n+2\n+3\n",
            "--- a\n+++ b\n@@ -1,3 +1,4 @@\n x\n-a\n+A\n y\n+z\n@@ -6,3 +7,3 @@\n p\n-q\n+Q\n r\n",
        ):
            result = self.tool.execute(mode="validate", diff=text)
            self.assertTrue(result["valid"], (text, result["findings"]))

    # -- bounded echo -------------------------------------------------------

    def test_multi_file_paths_echo_is_bounded(self):
        """The structured multi-file error lists at most 20 paths plus a total."""
        lines = []
        for i in range(30):
            lines.append(f"--- a/f{i}.txt")
            lines.append(f"+++ b/f{i}.txt")
            lines.append("@@ -1 +1 @@")
            lines.append(f"-x{i}")
            lines.append(f"+y{i}")
        result = self.tool.execute(mode="apply_check", diff="\n".join(lines) + "\n", original_text="x\n")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "multi_file_diff")
        self.assertEqual(len(result["files"]), 20)
        self.assertEqual(result["files_total"], 30)

    # -- fresh-seed differential batteries -----------------------------------

    def test_fresh_difflib_battery_new_seed(self):
        """150 fresh seeded difflib pairs validate, apply, and reverse exactly."""
        rng = random.Random(777001)
        words = ["alpha", "beta", "", " ", "üñí", "tab\there", "-dash", "+plus", "+++ t", "@@fake"]
        checked = 0
        for iteration in range(150):
            a = [rng.choice(words) + "\n" for _ in range(rng.randint(0, 20))]
            b = list(a)
            for _ in range(rng.randint(1, 6)):
                op = rng.choice(["edit", "ins", "del"])
                if op == "edit" and b:
                    b[rng.randrange(len(b))] = rng.choice(words) + "\n"
                elif op == "ins":
                    b.insert(rng.randint(0, len(b)), rng.choice(words) + "\n")
                elif op == "del" and b:
                    b.pop(rng.randrange(len(b)))
            if iteration % 2:
                a, b = b, a
            diff = "".join(
                difflib.unified_diff(a, b, fromfile="a/s.txt", tofile="b/s.txt", n=rng.choice([0, 1, 3]))
            )
            if not diff.strip():
                continue
            original, updated = "".join(a), "".join(b)
            validated = self.tool.execute(mode="validate", diff=diff)
            self.assertTrue(validated["valid"], f"iter {iteration}: {validated['findings']}")
            applied = self.tool.execute(mode="apply_check", diff=diff, original_text=original)
            self.assertTrue(applied["applies"], f"iter {iteration}: {applied}")
            reversed_result = self.tool.execute(mode="reverse", diff=diff, new_text=updated)
            self.assertTrue(reversed_result["valid"], f"iter {iteration}: {reversed_result}")
            self.assertTrue(reversed_result["round_trip"], f"iter {iteration}: {reversed_result}")
            twice = self.tool.execute(mode="reverse", diff=reversed_result["diff"])["diff"]
            self.assertEqual(twice, diff, f"iter {iteration}: double reverse not identity")
            checked += 1
        self.assertGreater(checked, 100)

    def test_real_diff_battery_with_no_newline_and_crlf(self):
        """60 fresh real `diff -u` outputs (markers included) all pass."""
        diff_bin = shutil.which("diff")
        if diff_bin is None:  # pragma: no cover - diff ships everywhere
            self.skipTest("system diff not available")
        rng = random.Random(515253)
        words = ["alpha", "beta", "gamma", "", "üñí", "tab\t", "line"]
        with tempfile.TemporaryDirectory() as tmp:
            path_a = os.path.join(tmp, "a.txt")
            path_b = os.path.join(tmp, "b.txt")
            checked = 0
            for iteration in range(60):
                a = [rng.choice(words) for _ in range(rng.randint(0, 14))]
                b = list(a)
                for _ in range(rng.randint(1, 4)):
                    op = rng.choice(["edit", "ins", "del"])
                    if op == "edit" and b:
                        b[rng.randrange(len(b))] = rng.choice(words)
                    elif op == "ins":
                        b.insert(rng.randint(0, len(b)), rng.choice(words))
                    elif op == "del" and b:
                        b.pop(rng.randrange(len(b)))
                if iteration % 2:
                    a, b = b, a
                style = rng.choice(["lf", "nonl", "nonl_a", "nonl_b", "crlf"])

                def render(lines, sep, terminated):
                    if not lines:
                        return ""
                    text = sep.join(lines)
                    return text + sep if terminated else text

                sep = "\r\n" if style == "crlf" else "\n"
                a_text = render(a, sep, style in ("lf", "crlf"))
                b_text = render(b, sep, style in ("lf", "crlf") and style != "nonl_b")
                if style == "nonl":
                    b_text = render(b, sep, False)
                if a_text == b_text:
                    continue
                with open(path_a, "w", newline="") as handle:
                    handle.write(a_text)
                with open(path_b, "w", newline="") as handle:
                    handle.write(b_text)
                proc = subprocess.run([diff_bin, "-u", path_a, path_b], capture_output=True)  # noqa: S603
                if proc.returncode != 1:
                    continue
                diff = proc.stdout.decode("utf-8")
                checked += 1
                validated = self.tool.execute(mode="validate", diff=diff)
                self.assertTrue(validated["valid"], f"iter {iteration} ({style}): {validated['findings']}")
                applied = self.tool.execute(mode="apply_check", diff=diff, original_text=a_text)
                self.assertTrue(applied["applies"], f"iter {iteration} ({style}): {applied}")
                reversed_result = self.tool.execute(mode="reverse", diff=diff, new_text=b_text)
                self.assertTrue(reversed_result["valid"], f"iter {iteration} ({style}): {reversed_result}")
                self.assertTrue(reversed_result["round_trip"], f"iter {iteration} ({style}): {reversed_result}")
                twice = self.tool.execute(mode="reverse", diff=reversed_result["diff"])["diff"]
                self.assertEqual(twice, diff, f"iter {iteration}: double reverse not identity")
            self.assertGreater(checked, 30)

    def test_fresh_corruption_battery_new_seed(self):
        """150 fresh corruptions are all caught by the correct layer."""
        rng = random.Random(886688)
        pool = []
        base = random.Random(13579)
        words = ["alpha", "beta", "gamma", "delta", "eps", "zeta"]
        for _ in range(10):
            a = [base.choice(words) + "\n" for _ in range(base.randint(8, 26))]
            b = list(a)
            for _ in range(base.randint(1, 5)):
                op = base.choice(["edit", "ins", "del"])
                if op == "edit" and b:
                    b[base.randrange(len(b))] = base.choice(words).upper() + "\n"
                elif op == "ins":
                    b.insert(base.randint(0, len(b)), base.choice(words) + "\n")
                elif len(b) > 1:
                    b.pop(base.randrange(len(b)))
            diff = "".join(difflib.unified_diff(a, b, fromfile="a/c.txt", tofile="b/c.txt", n=3))
            if diff.strip():
                pool.append((diff, "".join(a)))
        caught = {"validate": 0, "apply_check": 0}
        for step in range(150):
            diff, original = rng.choice(pool)
            lines = diff.split("\n")
            headers = [i for i, item in enumerate(lines) if item.startswith("@@ ")]
            minus = [i for i, item in enumerate(lines) if item.startswith("-") and not item.startswith("--- ")]
            plus = [i for i, item in enumerate(lines) if item.startswith("+") and not item.startswith("+++ ")]
            ctx = [i for i, item in enumerate(lines) if item.startswith(" ")]
            kind = rng.choice(
                ["new_start", "old_start", "count", "dup_marker", "marker_mid", "marker_early",
                 "drop", "garbage", "drift"]
            )
            if kind in ("new_start", "old_start") and headers:
                target = rng.choice(headers)
                head = lines[target]
                sign_pos = head.find("-" if kind == "old_start" else "+", head.find("@@"))
                digit_pos = sign_pos + 1
                while digit_pos < len(head) and head[digit_pos].isdigit():
                    digit_pos += 1
                value = int(head[sign_pos + 1 : digit_pos])
                lines[target] = head[: sign_pos + 1] + str(max(0, value + 1)) + head[digit_pos:]
            elif kind == "count" and headers:
                target = rng.choice(headers)
                head = lines[target]
                comma = head.find(",", head.find("@@ -"))
                if comma != -1 and head[comma + 1].isdigit():
                    lines[target] = head[: comma + 1] + str((int(head[comma + 1]) + 1) % 10) + head[comma + 2 :]
                else:
                    lines[target] = head.replace(" +", " +1,0 ", 1)
            elif kind == "dup_marker" and minus:
                lines.insert(rng.choice(minus) + 1, "\\ No newline at end of file")
                lines.insert(rng.choice(minus) + 2, "\\ No newline at end of file")
            elif kind == "marker_mid" and ctx and headers:
                candidates = [i for i in ctx if any(j > i for j in ctx + minus + plus)]
                if not candidates:
                    continue
                lines.insert(rng.choice(candidates) + 1, "\\ No newline at end of file")
            elif kind == "marker_early" and len(headers) >= 2:
                lines.insert(headers[1], "\\ No newline at end of file")
            elif kind == "drop" and (minus + plus + ctx):
                del lines[rng.choice(minus + plus + ctx)]
            elif kind == "garbage":
                anchor = rng.choice(headers)
                lines.insert(anchor + 1, "GARBAGE")
            elif kind == "drift" and ctx:
                target = rng.choice(ctx)
                lines[target] = lines[target] + "?"
            else:
                continue
            mutated = "\n".join(lines)
            validated = self.tool.execute(mode="validate", diff=mutated)
            applied = self.tool.execute(mode="apply_check", diff=mutated, original_text=original)
            caught_layer = None
            if not validated.get("valid", False):
                caught_layer = "validate"
            elif not applied.get("applies", False):
                caught_layer = "apply_check"
            self.assertIsNotNone(
                caught_layer, f"step {step} ({kind}) escaped both layers: {mutated[:200]!r}"
            )
            if kind == "drift":
                self.assertEqual(caught_layer, "apply_check", f"step {step} ({kind}): {validated}")
                caught["apply_check"] += 1
            else:
                self.assertEqual(caught_layer, "validate", f"step {step} ({kind}): {mutated[:200]!r}")
                caught["validate"] += 1
        self.assertGreater(caught["validate"], 80)
        self.assertGreater(caught["apply_check"], 3)

    def test_twenty_thousand_hunk_diff_validates_fast(self):
        """A 19,999-hunk diff (at the cap) validates well under two seconds."""
        hunks = [f"@@ -{i} +{i} @@\n-l{i}\n+m{i}\n" for i in range(1, 20_000)]
        diff = "--- a/h.txt\n+++ b/h.txt\n" + "".join(hunks)
        start = time.perf_counter()
        validated = self.tool.execute(mode="validate", diff=diff)
        elapsed = time.perf_counter() - start
        self.assertTrue(validated["valid"], validated["findings"][:3])
        self.assertEqual(validated["hunks"], 19_999)
        self.assertLess(elapsed, 2.0, f"validate took {elapsed:.2f}s")
        oversized = diff + "@@ -20000 +20000 @@\n-lx\n+mx\n@@ -20001 +20001 @@\n-ly\n+my\n"
        start = time.perf_counter()
        rejected = self.tool.execute(mode="validate", diff=oversized)
        elapsed = time.perf_counter() - start
        self.assertEqual(rejected["status"], "error")
        self.assertIn("max_hunks", rejected["error"])
        self.assertLess(elapsed, 2.0)


class SecondPassReviewTest(unittest.TestCase):
    """Second-pass hostile battery (fresh seed 20261023): wider difflib corpus,
    new real-diff fixture shapes, fresh corruptions, git re-captures, stats
    arithmetic, and file-level /dev/null application semantics.
    """

    SEED = 20261023

    def setUp(self):
        self.tool = DiffParseTool()

    # -- file-level /dev/null semantics ---------------------------------

    def test_dev_null_sections_apply_only_to_exact_sides(self):
        """New-file diffs need an empty original; delete diffs must consume it.

        patch(1) refuses a ``--- /dev/null`` patch when the target already
        exists ("Patch creates file that already exists!"); reporting
        applies=True for non-empty text produced a chimera that matched
        neither the diff's new file nor any patch result. A ``+++ /dev/null``
        diff asserts the result is empty, so trailing unconsumed lines are a
        mismatch, not a success.
        """
        new_file = "--- /dev/null\n+++ b/new.txt\n@@ -0,0 +1,2 @@\n+alpha\n+beta\n"
        rejected = self.tool.execute(mode="apply_check", diff=new_file, original_text="existing\n")
        self.assertFalse(rejected["applies"])
        self.assertIn("old_side_empty_mismatch", rejected["reject_reason"])
        self.assertTrue(self.tool.execute(mode="apply_check", diff=new_file, original_text="")["applies"])
        delete = "--- a/old.txt\n+++ /dev/null\n@@ -1,3 +0,0 @@\n-one\n-two\n-three\n"
        kept = self.tool.execute(mode="apply_check", diff=delete, original_text="one\ntwo\nthree\nEXTRA\n")
        self.assertFalse(kept["applies"])
        self.assertIn("new_side_empty_mismatch", kept["reject_reason"])
        self.assertTrue(
            self.tool.execute(mode="apply_check", diff=delete, original_text="one\ntwo\nthree\n")["applies"]
        )
        git_new = (
            "diff --git a/n.txt b/n.txt\nnew file mode 100644\nindex 0000000..1111111\n"
            "--- /dev/null\n+++ b/n.txt\n@@ -0,0 +1 @@\n+x\n"
        )
        wrong = self.tool.execute(mode="apply_check", diff=git_new, original_text="nope\n")
        self.assertFalse(wrong["applies"])
        self.assertIn("old_side_empty_mismatch", wrong["reject_reason"])
        self.assertTrue(self.tool.execute(mode="apply_check", diff=git_new, original_text="")["applies"])
        # Real-path empty originals (plain `diff -u empty full`) stay line-level.
        plain = "--- empty.txt\t2026-01-01 00:00:00\n+++ full.txt\t2026-01-01 00:00:00\n@@ -0,0 +1 @@\n+x\n"
        self.assertTrue(self.tool.execute(mode="apply_check", diff=plain, original_text="")["applies"])
        # Reverse round trips are unaffected.
        rv = self.tool.execute(mode="reverse", diff=new_file, new_text="alpha\nbeta\n")
        self.assertTrue(rv["valid"])
        self.assertTrue(rv["round_trip"])

    # -- (a) fresh difflib battery: n=7 and spacey/unicode paths ---------

    def test_fresh_difflib_battery_wider_paths_and_contexts(self):
        """500 fresh pairs validate, apply, reverse, and double-reverse exactly."""
        rng = random.Random(self.SEED)
        words = ["alpha", "beta", "gamma", "", " x", "tab\there", "üñí", "中文行", "1", "--d", "+++p", "@@fake"]
        paths = [("my file.txt", "my file.txt"), ("p täble ünï.txt", "p täble ünï.txt"),
                 ("a/dir with space/f.py", "b/dir with space/f.py"), ("文件 名.txt", "文件 名.txt")]
        checked = 0
        for iteration in range(500):
            a = [rng.choice(words) + "\n" for _ in range(rng.randint(0, 24))]
            b = list(a)
            if a and rng.random() < 0.75:
                for _ in range(rng.randint(1, 6)):
                    op = rng.choice(["edit", "ins", "del"])
                    if op == "edit" and b:
                        b[rng.randrange(len(b))] = rng.choice(words) + "\n"
                    elif op == "ins":
                        b.insert(rng.randint(0, len(b)), rng.choice(words) + "\n")
                    elif b:
                        b.pop(rng.randrange(len(b)))
            else:
                b = [rng.choice(words) + "\n" for _ in range(rng.randint(1, 10))]
            if iteration % 2:
                a, b = b, a
            fromfile, tofile = rng.choice(paths)
            n = rng.choice([0, 1, 3, 7])
            if iteration % 3 == 0:
                diff = "\n".join(
                    difflib.unified_diff([x[:-1] for x in a], [x[:-1] for x in b],
                                         fromfile=fromfile, tofile=tofile, n=n, lineterm="")
                )
            else:
                diff = "".join(difflib.unified_diff(a, b, fromfile=fromfile, tofile=tofile, n=n))
            if not diff.strip():
                continue
            checked += 1
            original, updated = "".join(a), "".join(b)
            validated = self.tool.execute(mode="validate", diff=diff)
            self.assertTrue(validated["valid"], f"iter {iteration}: {validated['findings'][:2]}")
            applied = self.tool.execute(mode="apply_check", diff=diff, original_text=original)
            self.assertTrue(applied["applies"], f"iter {iteration}: {applied.get('reject_reason')}")
            rv = self.tool.execute(mode="reverse", diff=diff, new_text=updated)
            self.assertTrue(rv["valid"] and rv["round_trip"], f"iter {iteration}: {rv}")
            twice = self.tool.execute(mode="reverse", diff=rv["diff"])["diff"]
            self.assertEqual(twice, diff, f"iter {iteration}: double reverse not byte-identical")
        self.assertGreater(checked, 400)

    # -- (b) real diff -u with new fixture shapes -------------------------

    def test_real_diff_battery_new_fixture_shapes(self):
        """100 fresh real `diff -u` captures incl. empty/identical/CRLF shapes.

        apply_check verdicts are hand-verified: the simulation must reproduce
        the new text byte-for-byte, not merely report success.
        """
        diff_bin = shutil.which("diff")
        if diff_bin is None:  # pragma: no cover
            self.skipTest("system diff not available")
        rng = random.Random(self.SEED + 11)
        words = ["alpha", "beta", "gamma", "delta", "", "üñí", "中文", "tab\tline"]
        shapes = {"empty_to_content": 0, "content_to_empty": 0, "no_trailing_newline": 0,
                  "crlf_content": 0, "identical": 0, "plain": 0}
        checked = 0
        with tempfile.TemporaryDirectory() as tmp:
            path_a, path_b = os.path.join(tmp, "a.txt"), os.path.join(tmp, "b.txt")
            for iteration in range(100):
                a = [rng.choice(words) for _ in range(rng.randint(0, 15))]
                b = list(a)
                for _ in range(rng.randint(1, 4)):
                    op = rng.choice(["edit", "ins", "del"])
                    if op == "edit" and b:
                        b[rng.randrange(len(b))] = rng.choice(words)
                    elif op == "ins":
                        b.insert(rng.randint(0, len(b)), rng.choice(words))
                    elif b:
                        b.pop(rng.randrange(len(b)))
                if iteration % 2:
                    a, b = b, a
                shape = rng.choice(["plain", "plain", "no_trailing_newline", "crlf_content",
                                    "empty_to_content", "content_to_empty", "identical"])
                if shape == "empty_to_content":
                    a_text, b_text = "", "\n".join(b) + ("\n" if b else "")
                elif shape == "content_to_empty":
                    a_text, b_text = "\n".join(a) + ("\n" if a else ""), ""
                elif shape == "identical":
                    a_text = b_text = "\n".join(a) + ("\n" if a else "")
                elif shape == "no_trailing_newline":
                    a_text = "\n".join(a) + ("\n" if a and rng.random() < 0.5 else "")
                    b_text = "\n".join(b) + ("\n" if b and rng.random() < 0.5 else "")
                elif shape == "crlf_content":
                    a_text = "\r\n".join(a) + ("\r\n" if a else "")
                    b_text = "\r\n".join(b) + ("\r\n" if b else "")
                else:
                    a_text = "\n".join(a) + ("\n" if a else "")
                    b_text = "\n".join(b) + ("\n" if b else "")
                for path, text in ((path_a, a_text), (path_b, b_text)):
                    with open(path, "w", newline="") as handle:
                        handle.write(text)
                proc = subprocess.run([diff_bin, "-u", path_a, path_b], capture_output=True)  # noqa: S603
                shapes[shape] += 1
                if proc.returncode == 0:
                    self.assertEqual(a_text, b_text)
                    continue  # identical files: real diff emits nothing at all
                diff = proc.stdout.decode("utf-8")
                checked += 1
                validated = self.tool.execute(mode="validate", diff=diff)
                self.assertTrue(validated["valid"], f"iter {iteration} ({shape}): {validated['findings'][:2]}")
                applied = self.tool.execute(mode="apply_check", diff=diff, original_text=a_text)
                self.assertTrue(applied["applies"], f"iter {iteration} ({shape}): {applied.get('reject_reason')}")
                parsed = diff_module.DiffParseTool()._parse(diff)
                ok, _entries, produced, why = diff_module.DiffParseTool()._simulate(
                    parsed.files[0], a_text, crlf_transport=parsed.newline_style == "crlf"
                )
                self.assertTrue(ok and produced == b_text,
                                f"iter {iteration} ({shape}): {why} {produced!r} != {b_text!r}")
                rv = self.tool.execute(mode="reverse", diff=diff, new_text=b_text)
                self.assertTrue(rv["valid"] and rv["round_trip"], f"iter {iteration} ({shape}): {rv}")
        self.assertGreater(checked, 40)
        for name, count in shapes.items():
            self.assertGreater(count, 0, f"fixture shape {name} never occurred")

    # -- (c) fresh corruptions --------------------------------------------

    def test_fresh_corruption_battery_third_seed(self):
        """300 fresh corruptions across 12 mutation classes, layer-adjudicated."""
        rng = random.Random(self.SEED + 22)
        pool = []
        base = random.Random(self.SEED + 33)
        words = ["alpha", "beta", "gamma", "delta", "eps", "zeta", "eta"]
        for _ in range(12):
            a = [base.choice(words) + "\n" for _ in range(base.randint(6, 26))]
            b = list(a)
            for _ in range(base.randint(1, 5)):
                op = base.choice(["edit", "ins", "del"])
                if op == "edit" and b:
                    b[base.randrange(len(b))] = base.choice(words).upper() + "\n"
                elif op == "ins":
                    b.insert(base.randint(0, len(b)), base.choice(words) + "\n")
                elif len(b) > 1:
                    b.pop(base.randrange(len(b)))
            diff = "".join(difflib.unified_diff(a, b, fromfile="a/p.txt", tofile="b/p.txt", n=3))
            if diff.strip():
                pool.append((diff, "".join(a)))
        caught = {"validate": 0, "apply_check": 0}
        for step in range(300):
            diff, original = rng.choice(pool)
            lines = diff.split("\n")
            headers = [i for i, x in enumerate(lines) if x.startswith("@@ ")]
            minus = [i for i, x in enumerate(lines) if x.startswith("-") and not x.startswith("--- ")]
            plus = [i for i, x in enumerate(lines) if x.startswith("+") and not x.startswith("+++ ")]
            ctx = [i for i, x in enumerate(lines) if x.startswith(" ") and x.strip()]
            kind = rng.choice(["tamper_count", "drop_line", "swap_header", "bad_grammar",
                               "marker_after_header", "garbage", "truncate", "zero_count",
                               "context_drift", "removed_line_edit", "dup_marker", "section_merge"])
            if kind == "tamper_count" and headers:
                target = rng.choice(headers)
                head = lines[target]
                sign = "-" if rng.random() < 0.5 else "+"
                pos = head.find(sign, head.find("@@"))
                comma = head.find(",", pos)
                existing = int(head[comma + 1]) if comma != -1 and head[comma + 1].isdigit() else 1
                digit = str((existing + rng.randint(1, 8)) % 10)
                lines[target] = (head[: pos + 1] + f",{digit}" + head[pos + 1 :]) if comma == -1 else (
                    head[: comma + 1] + digit + head[comma + 2 :])
            elif kind == "drop_line":
                del lines[rng.choice(minus + plus + ctx)]
            elif kind == "swap_header":
                m = next(i for i, x in enumerate(lines) if x.startswith("--- "))
                p = next(i for i, x in enumerate(lines) if x.startswith("+++ "))
                lines[m], lines[p] = lines[p], lines[m]
            elif kind == "bad_grammar" and headers:
                target = rng.choice(headers)
                lines[target] = lines[target].replace("@@ -", "@@~-", 1)
            elif kind == "marker_after_header" and headers:
                lines.insert(rng.choice(headers) + 1, "\\ No newline at end of file")
            elif kind == "garbage" and headers:
                lines.insert(rng.choice(headers) + 1, "GARBAGE LINE")
            elif kind == "truncate":
                lines = lines[: max(2, len(lines) - rng.randint(2, 5))]
            elif kind == "zero_count" and headers:
                target = rng.choice(headers)
                head = lines[target]
                comma = head.find(",", head.find("@@ -"))
                if comma != -1 and head[comma + 1].isdigit():
                    lines[target] = head[: comma + 1] + "0" + head[comma + 2 :]
                else:
                    lines[target] = head.replace(" +", " +1,0 ", 1)
            elif kind == "context_drift" and ctx:
                lines[rng.choice(ctx)] += "X"
            elif kind == "removed_line_edit" and minus:
                lines[rng.choice(minus)] += "Y"
            elif kind == "dup_marker" and minus:
                anchor = rng.choice(minus)
                lines.insert(anchor + 1, "\\ No newline at end of file")
                lines.insert(anchor + 2, "\\ No newline at end of file")
            elif kind == "section_merge" and headers:
                lines.insert(rng.choice(headers) + 1, "--- sneak/p.txt")
            else:
                continue
            mutated = "\n".join(lines)
            validated = self.tool.execute(mode="validate", diff=mutated)
            applied = self.tool.execute(mode="apply_check", diff=mutated, original_text=original)
            layer = None
            if not validated.get("valid", False):
                layer = "validate"
            elif not applied.get("applies", False):
                layer = "apply_check"
            self.assertIsNotNone(layer, f"step {step} ({kind}) escaped: {mutated[:180]!r}")
            if kind in ("context_drift", "removed_line_edit"):
                self.assertEqual(layer, "apply_check", f"step {step} ({kind}): {validated}")
            else:
                self.assertEqual(layer, "validate", f"step {step} ({kind}): {mutated[:180]!r}")
            caught[layer] += 1
        self.assertGreater(caught["validate"], 150)
        self.assertGreater(caught["apply_check"], 10)

    # -- (d) git re-captures ----------------------------------------------

    def test_git_re_capture_shapes(self):
        """Fresh real git outputs: R100 rename, binary patch, --cc, --stat, chmod."""
        if shutil.which("git") is None:  # pragma: no cover
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                       GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t", HOME=tmp)

            def git(*args):
                return subprocess.run(["git", "-C", tmp, *args], capture_output=True, text=True, env=env)

            git("init", "-q")
            git("config", "user.email", "t@t")
            git("config", "user.name", "t")
            trunk = git("symbolic-ref", "--short", "HEAD").stdout.strip()
            with open(os.path.join(tmp, "orig name.txt"), "w") as handle:
                handle.write("line one\nline two\nline three\n")
            git("add", "-A")
            git("commit", "-qm", "one")
            git("mv", "orig name.txt", "renamed name.txt")
            rename_diff = git("diff", "--cached", "-M").stdout
            result = self.tool.execute(mode="validate", diff=rename_diff)
            self.assertTrue(result["valid"], result["findings"][:2])
            self.assertEqual(result["summary"]["renamed"], 1)
            with open(os.path.join(tmp, "renamed name.txt"), "a") as handle:
                handle.write("line four\n")
            git("add", "-A")
            rename_edit = git("diff", "--cached", "-M").stdout
            result = self.tool.execute(mode="validate", diff=rename_edit)
            self.assertTrue(result["valid"], result["findings"][:2])
            self.assertEqual(result["summary"]["renamed"], 1)
            self.assertEqual(result["hunks"], 1)
            git("add", "-A")
            git("commit", "-qm", "two")
            with open(os.path.join(tmp, "blob.bin"), "wb") as handle:
                handle.write(b"\x00\x01\x02binary\x00data\x7f\n")
            git("add", "-A")
            binary_diff = git("diff", "--cached", "--binary").stdout
            self.assertIn("GIT binary patch", binary_diff)
            result = self.tool.execute(mode="validate", diff=binary_diff)
            self.assertTrue(result["valid"], result["findings"][:2])
            self.assertEqual(result["summary"]["binary"], 1)
            git("commit", "-qm", "three")
            # Conflicted merge resolved by hand: `git show --cc` emits @@@ hunks,
            # which the tool documents and rejects as malformed body lines.
            git("checkout", "-q", "-b", "side")
            with open(os.path.join(tmp, "merge.txt"), "w") as handle:
                handle.write("base A\nbase B\n")
            git("add", "-A")
            git("commit", "-qm", "side-base")
            git("checkout", "-q", trunk)
            with open(os.path.join(tmp, "merge.txt"), "w") as handle:
                handle.write("master A\nbase B\n")
            git("add", "-A")
            git("commit", "-qm", "master-edit")
            git("merge", "--no-edit", "side")
            with open(os.path.join(tmp, "merge.txt"), "w") as handle:
                handle.write("master A\nRESOLVED B\n")  # differs from both parents
            git("add", "-A")
            git("commit", "-qm", "resolved")
            combined = git("show", "--cc", "--format=", "HEAD").stdout
            self.assertIn("@@@", combined)
            result = self.tool.execute(mode="validate", diff=combined)
            self.assertFalse(result["valid"])
            self.assertTrue(any(f["code"].startswith("E_") for f in result["findings"]))
            # --stat graphs are not unified diffs and must not validate.
            with open(os.path.join(tmp, "wide.txt"), "w") as handle:
                handle.write("".join(f"line {i}\n" for i in range(400)))
            git("add", "-A")
            git("commit", "-qm", "four")
            with open(os.path.join(tmp, "wide.txt"), "w") as handle:
                handle.write("".join(f"LINE {i}\n" for i in range(400)))
            stat = git("diff", "--stat", "HEAD^").stdout
            self.assertIn("|", stat)
            self.assertFalse(self.tool.execute(mode="validate", diff=stat)["valid"])
            result = self.tool.execute(mode="validate", diff=git("diff", "HEAD^").stdout)
            self.assertTrue(result["valid"], result["findings"][:2])
            self.assertGreaterEqual(result["hunks"], 1)
            git("commit", "-qam", "five")
            # Mode-only change (chmod) validates as a hunk-less section.
            os.chmod(os.path.join(tmp, "wide.txt"), 0o755)
            mode_diff = git("diff").stdout
            self.assertIn("old mode", mode_diff)
            result = self.tool.execute(mode="validate", diff=mode_diff)
            self.assertTrue(result["valid"], result["findings"][:2])
            self.assertEqual(result["files"], 1)
            os.chmod(os.path.join(tmp, "wide.txt"), 0o644)

    # -- (e) stats hotspot arithmetic -------------------------------------

    def test_stats_hotspot_arithmetic_fresh(self):
        """80 fresh hand cases: totals, ranges, ordering, and the top-3 cap."""
        rng = random.Random(self.SEED + 44)
        for case in range(80):
            a = [f"l{i}" for i in range(rng.randint(0, 30))]
            b = list(a)
            for _ in range(rng.randint(1, 6)):
                op = rng.choice(["edit", "ins", "del"])
                if op == "edit" and b:
                    b[rng.randrange(len(b))] = f"L{rng.randint(0, 99)}"
                elif op == "ins":
                    b.insert(rng.randint(0, len(b)), f"N{rng.randint(0, 99)}")
                elif b:
                    b.pop(rng.randrange(len(b)))
            diff = "".join(
                difflib.unified_diff([x + "\n" for x in a], [x + "\n" for x in b],
                                     fromfile="a/h.txt", tofile="b/h.txt", n=rng.choice([0, 1, 3]))
            )
            if not diff.strip():
                continue
            result = self.tool.execute(mode="stats", diff=diff)
            self.assertEqual(result["status"], "success")
            parsed = diff_module.DiffParseTool()._parse(diff)
            expected = []
            adds = dels = 0
            for hunk_index, hunk in enumerate(parsed.files[0].hunks):
                changed = sum(1 for item in hunk.lines if item.origin in ("+", "-"))
                adds += sum(1 for item in hunk.lines if item.origin == "+")
                dels += sum(1 for item in hunk.lines if item.origin == "-")
                expected.append({
                    "file": "h.txt", "hunk_index": hunk_index + 1, "changed_lines": changed,
                    "old_range": [hunk.old_start, hunk.old_start + hunk.old_count - 1] if hunk.old_count
                    else [hunk.old_start + 1, hunk.old_start],
                    "new_range": [hunk.new_start, hunk.new_start + hunk.new_count - 1] if hunk.new_count
                    else [hunk.new_start + 1, hunk.new_start],
                })
            expected.sort(key=lambda item: (-item["changed_lines"], item["file"], item["hunk_index"]))
            self.assertEqual(result["hotspots"], expected[:3], f"case {case}")
            self.assertEqual(result["totals"]["add_lines"], adds, f"case {case}")
            self.assertEqual(result["totals"]["del_lines"], dels, f"case {case}")
            self.assertEqual(result["totals"]["net"], adds - dels, f"case {case}")

    # -- (f) pathological second pass --------------------------------------

    def test_pathological_byte_and_file_caps(self):
        """Oversized hunks/lines/files fail fast with structured errors."""
        hunks = "".join(f"@@ -{i} +{i} @@\n-x\n+y\n" for i in range(1, 100_001))
        huge = "--- a/big.txt\n+++ b/big.txt\n" + hunks
        start = time.perf_counter()
        result = self.tool.execute(mode="validate", diff=huge)
        self.assertLess(time.perf_counter() - start, 2.0)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_input_bytes", result["error"])
        hunks2 = "".join(f"@@ -{i} +{i} @@\n-x\n+y\n" for i in range(1, 21_002))
        over_hunks = "--- a/big.txt\n+++ b/big.txt\n" + hunks2
        start = time.perf_counter()
        result = self.tool.execute(mode="validate", diff=over_hunks)
        self.assertLess(time.perf_counter() - start, 2.0)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_hunks", result["error"])
        two_mb = "x" * (2 * 1024 * 1024)
        start = time.perf_counter()
        result = self.tool.execute(mode="validate", diff=f"--- a\n+++ b\n@@ -1 +1 @@\n-q\n+{two_mb}\n")
        self.assertLess(time.perf_counter() - start, 2.0)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_input_bytes", result["error"])
        at_cap = "y" * (1024 * 1024 - 50)
        result = self.tool.execute(mode="validate", diff=f"--- a\n+++ b\n@@ -1 +1 @@\n-q\n+{at_cap}\n")
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["valid"])
        files = "".join(f"--- a/f{i}.txt\n+++ b/f{i}.txt\n@@ -1 +1 @@\n-x\n+z\n" for i in range(2_100))
        start = time.perf_counter()
        result = self.tool.execute(mode="validate", diff=files)
        self.assertLess(time.perf_counter() - start, 2.0)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_files", result["error"])


if __name__ == "__main__":
    unittest.main()
