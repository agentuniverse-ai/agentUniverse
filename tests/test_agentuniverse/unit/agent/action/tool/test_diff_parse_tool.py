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


if __name__ == "__main__":
    unittest.main()
