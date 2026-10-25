"""Offline unit tests for ConsoleAnsiTool (ECMA-48 + xterm escape analysis)."""

import os
import random
import time
import unittest

from agentuniverse.agent.action.tool.common_tool import console_ansi_tool as ansi_module
from agentuniverse.agent.action.tool.common_tool.console_ansi_tool import ConsoleAnsiTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(ansi_module.__file__), "console_ansi_tool.yaml")

# ---------------------------------------------------------------------------
# Hand-embedded ground truth: ECMA-48 5.4 / 5.5 tables + xterm ctlseqs.
# Each entry: (sequence, expected category, expected human fragment).
# ---------------------------------------------------------------------------
GROUND_TRUTH = [
    # SGR: resets, styles, style-clears
    ("\x1b[0m", "sgr", "Reset all attributes"),
    ("\x1b[m", "sgr", "Reset all attributes"),
    ("\x1b[1m", "sgr", "Set bold"),
    ("\x1b[2m", "sgr", "Set dim/faint"),
    ("\x1b[3m", "sgr", "Set italic"),
    ("\x1b[4m", "sgr", "Set underline"),
    ("\x1b[5m", "sgr", "Set slow blink"),
    ("\x1b[6m", "sgr", "Set rapid blink"),
    ("\x1b[7m", "sgr", "Set reverse video"),
    ("\x1b[8m", "sgr", "Set conceal/hidden"),
    ("\x1b[9m", "sgr", "Set crossed-out"),
    ("\x1b[10m", "sgr", "Select primary font"),
    ("\x1b[12m", "sgr", "Select alternative font 2"),
    ("\x1b[20m", "sgr", "Select fraktur/Gothic font"),
    ("\x1b[21m", "sgr", "Set double underline"),
    ("\x1b[22m", "sgr", "Normal intensity"),
    ("\x1b[23m", "sgr", "Not italic"),
    ("\x1b[24m", "sgr", "Not underlined"),
    ("\x1b[25m", "sgr", "Not blinking"),
    ("\x1b[27m", "sgr", "Not reversed"),
    ("\x1b[28m", "sgr", "Reveal, not concealed"),
    ("\x1b[29m", "sgr", "Not crossed out"),
    # SGR: basic foreground 30-37 (xterm/PC naming convention)
    ("\x1b[30m", "sgr", "Set foreground color 30 (black)"),
    ("\x1b[31m", "sgr", "Set foreground color 31 (red)"),
    ("\x1b[32m", "sgr", "Set foreground color 32 (green)"),
    ("\x1b[33m", "sgr", "Set foreground color 33 (yellow)"),
    ("\x1b[34m", "sgr", "Set foreground color 34 (blue)"),
    ("\x1b[35m", "sgr", "Set foreground color 35 (magenta)"),
    ("\x1b[36m", "sgr", "Set foreground color 36 (cyan)"),
    ("\x1b[37m", "sgr", "Set foreground color 37 (white)"),
    ("\x1b[39m", "sgr", "Set default foreground color"),
    # SGR: basic background 40-47 and default
    ("\x1b[40m", "sgr", "Set background color 40 (black)"),
    ("\x1b[43m", "sgr", "Set background color 43 (yellow)"),
    ("\x1b[47m", "sgr", "Set background color 47 (white)"),
    ("\x1b[49m", "sgr", "Set default background color"),
    # SGR: aixterm bright colors
    ("\x1b[90m", "sgr", "Set foreground color 90 (bright black (gray))"),
    ("\x1b[91m", "sgr", "Set foreground color 91 (bright red)"),
    ("\x1b[97m", "sgr", "Set foreground color 97 (bright white)"),
    ("\x1b[100m", "sgr", "Set background color 100 (bright black (gray))"),
    ("\x1b[107m", "sgr", "Set background color 107 (bright white)"),
    # SGR: 256-color indexed (xterm palette arithmetic is the oracle)
    ("\x1b[38;5;0m", "sgr", "38;5;0 (black)"),
    ("\x1b[38;5;1m", "sgr", "38;5;1 (red)"),
    ("\x1b[38;5;9m", "sgr", "38;5;9 (bright red)"),
    ("\x1b[38;5;16m", "sgr", "38;5;16 (RGB 0,0,0"),
    ("\x1b[38;5;196m", "sgr", "38;5;196 (RGB 255,0,0"),
    ("\x1b[38;5;208m", "sgr", "38;5;208 (RGB 255,135,0"),
    ("\x1b[38;5;231m", "sgr", "38;5;231 (RGB 255,255,255"),
    ("\x1b[38;5;232m", "sgr", "38;5;232 (RGB 8,8,8"),
    ("\x1b[38;5;255m", "sgr", "38;5;255 (RGB 238,238,238"),
    ("\x1b[38;5;300m", "sgr", "out of range"),
    ("\x1b[48;5;196m", "sgr", "48;5;196 (RGB 255,0,0"),
    ("\x1b[58;5;10m", "sgr", "underline color 58;5;10 (bright green)"),
    # SGR: 24-bit RGB and colon subparameters
    ("\x1b[38;2;12;34;56m", "sgr", "38;2;12;34;56 (RGB 12,34,56)"),
    ("\x1b[38:5:196m", "sgr", "38:5:196 (RGB 255,0,0"),
    ("\x1b[38:2:1:2:3m", "sgr", "38:2:1:2:3 (RGB 1,2,3)"),
    ("\x1b[1;31m", "sgr", "Set foreground color 31 (red)"),
    ("\x1b[1;33;44m", "sgr", "Set background color 44 (blue)"),
    ("\x1b[38m", "sgr", "malformed parameters"),
    ("\x1b[99m", "sgr", "unassigned/proprietary"),
    # Cursor movement (ECMA-48 CCS)
    ("\x1b[5A", "cursor", "Cursor up 5"),
    ("\x1b[A", "cursor", "Cursor up 1"),
    ("\x1b[2B", "cursor", "Cursor down 2"),
    ("\x1b[3C", "cursor", "Cursor forward 3"),
    ("\x1b[7D", "cursor", "Cursor back 7"),
    ("\x1b[2E", "cursor", "Cursor next line"),
    ("\x1b[3F", "cursor", "Cursor previous line"),
    ("\x1b[10G", "cursor", "Cursor to column 10 (CHA)"),
    ("\x1b[2;5H", "cursor", "row 2, column 5 (CUP)"),
    ("\x1b[H", "cursor", "row 1, column 1"),
    ("\x1b[3;4f", "cursor", "row 3, column 4 (HVP)"),
    ("\x1b[s", "cursor", "Save cursor position (SCOSC)"),
    ("\x1b[u", "cursor", "Restore cursor position (SCORC)"),
    ("\x1b[5`", "cursor", "column 5 (HPA)"),
    ("\x1b[4d", "cursor", "row 4 (VPA)"),
    ("\x1b[2e", "cursor", "down 2 rows (VPR)"),
    ("\x1b[9a", "cursor", "forward 9 columns (HPR)"),
    ("\x1b[2Z", "cursor", "Cursor back 2 tab stops (CBT)"),
    ("\x1b7", "cursor", "Save cursor position and attributes (DECSC)"),
    ("\x1b8", "cursor", "Restore cursor position and attributes (DECRC)"),
    ("\x1bD", "cursor", "Index: cursor down one line"),
    ("\x1bM", "cursor", "Reverse index: cursor up one line"),
    ("\x1bE", "cursor", "Next line: cursor down to column 1"),
    ("\x1b[2 q", "cursor", "steady block (DECSCUSR)"),
    ("\x1b[5 q", "cursor", "blinking bar (DECSCUSR)"),
    # Erase (ED / EL / ECH)
    ("\x1b[J", "erase", "end of screen (ED 0)"),
    ("\x1b[0J", "erase", "end of screen (ED 0)"),
    ("\x1b[1J", "erase", "start of screen to cursor (ED 1)"),
    ("\x1b[2J", "erase", "Erase entire display (ED 2)"),
    ("\x1b[3J", "erase", "scrollback buffer (ED 3"),
    ("\x1b[?2J", "erase", "(DECSED)"),
    ("\x1b[K", "erase", "end of line (EL 0)"),
    ("\x1b[0K", "erase", "end of line (EL 0)"),
    ("\x1b[1K", "erase", "start of line to cursor (EL 1)"),
    ("\x1b[2K", "erase", "Erase entire line (EL 2)"),
    ("\x1b[?1K", "erase", "(DECSEL)"),
    ("\x1b[5X", "erase", "Erase 5 characters"),
    # Scrolling / line shift
    ("\x1b[3S", "scroll", "Scroll display up 3 lines (SU)"),
    ("\x1b[2T", "scroll", "Scroll display down 2 lines (SD)"),
    ("\x1b[5;20r", "scroll", "scrolling region rows 5-20 (DECSTBM)"),
    ("\x1b[r", "scroll", "rows 1-end"),
    ("\x1b[2L", "scroll", "Insert 2 blank lines"),
    ("\x1b[4M", "scroll", "Delete 4 lines"),
    # Modes (SM/RM, DEC private)
    ("\x1b[4h", "mode", "Set insert mode (IRM 4)"),
    ("\x1b[4l", "mode", "Reset insert mode"),
    ("\x1b[20h", "mode", "Set newline mode (LNM 20)"),
    ("\x1b[?25h", "mode", "Show cursor (DECTCEM ?25 set)"),
    ("\x1b[?25l", "mode", "Hide cursor (DECTCEM ?25 reset)"),
    ("\x1b[?7h", "mode", "Enable autowrap (DECAWM ?7)"),
    ("\x1b[?7l", "mode", "Disable autowrap"),
    ("\x1b[?1049h", "mode", "alternate screen buffer with cursor save"),
    ("\x1b[?1049l", "mode", "Switch back to primary screen buffer"),
    ("\x1b[?1000h", "mode", "X10 mouse reporting"),
    ("\x1b[?1002h", "mode", "button-event mouse tracking"),
    ("\x1b[?1006h", "mode", "SGR extended mouse mode"),
    ("\x1b[?2004h", "mode", "Enable bracketed paste mode"),
    ("\x1b[?999h", "mode", "Set DEC private mode 999"),
    # OSC 8 hyperlinks: URL + label extraction, close marker, unclosed
    ("\x1b]8;;https://example.com\x07Search\x1b]8;;\x07", "osc-link", 'Open hyperlink to https://example.com (label "Search")'),
    ("\x1b]8;id=1;https://a.dev\x07go\x1b]8;;\x07", "osc-link", "Open hyperlink to https://a.dev"),
    ("\x1b]8;;https://x.dev\x1b\\go\x1b]8;;\x1b\\", "osc-link", "Open hyperlink to https://x.dev"),
    ("\x1b]8;;\x07", "osc-link", "Close hyperlink"),
    ("\x1b]8;;https://unclosed.dev\x07tail", "osc-link", "(unclosed)"),
    # OSC titles and other commands
    ("\x1b]0;my shell\x07", "osc-title", 'Set window and icon title "my shell"'),
    ("\x1b]2;build log\x07", "osc-title", 'Set window title "build log"'),
    ("\x1b]1;icon\x07", "osc-title", 'Set icon name "icon"'),
    ("\x1b]52;c;base64=\x07", "other", "clipboard"),
    ("\x1b]7;file://host/home\x07", "other", "Set working directory"),
    ("\x1b]4;1;rgb:ff/00/00\x07", "other", "palette color"),
    ("\x1b]133;A\x07", "other", "Shell integration"),
    # Simple escapes, charsets, resets, DCS/PM/APC/SOS strings, queries
    ("\x1b(B", "other", "Select G0 character set B (US-ASCII)"),
    ("\x1b(0", "other", "DEC special graphics"),
    ("\x1b)B", "other", "Select G1 character set B"),
    ("\x1b=", "other", "application keypad mode (DECKPAM)"),
    ("\x1b>", "other", "numeric keypad mode (DECKPnm)"),
    ("\x1bc", "other", "Reset terminal to initial state (RIS)"),
    ("\x1b\\", "other", "String terminator (ST)"),
    ("\x1bP1;2q data \x1b\\", "other", "Device control string"),
    ("\x1b^privacy\x1b\\", "other", "Privacy message"),
    ("\x1b_app\x1b\\", "other", "Application program command"),
    ("\x1bXstart\x1b\\", "other", "Start of string"),
    ("\x1b[6n", "other", "device status report (DSR)"),
    ("\x1b[c", "other", "primary device attributes (DA)"),
    ("\x1b[5t", "other", "window manipulation"),
    ("\x1b[3@", "other", "insert blank characters (ICH)"),
    ("\x1b[4P", "other", "delete characters (DCH)"),
    ("\x1b[0g", "other", "tab clearance (TBC)"),
    ("\x1b9", "other", "Two-character escape ESC 9"),
    # 8-bit C1 CSI parsed per ECMA-48
    ("\x9b31m", "sgr", "Set foreground color 31 (red)"),
]
def _find(inventory, category, fragment):
    """Return the first inventory entry matching category and human fragment."""
    for entry in inventory:
        if entry["category"] == category and (not fragment or fragment in entry["human"]):
            return entry
    return None


class ConsoleAnsiGroundTruthTest(unittest.TestCase):
    """ECMA-48 + xterm ctlseqs ground truths asserted through classify."""

    def setUp(self):
        """Fresh tool per test."""
        self.tool = ConsoleAnsiTool()

    def test_ground_truth_table(self):
        """Every canonical sequence classifies with the right category and meaning."""
        for sequence, category, fragment in GROUND_TRUTH:
            with self.subTest(sequence=sequence):
                result = self.tool.execute(mode="classify", text=sequence)
                self.assertEqual(result["status"], "success", result)
                entry = _find(result["inventory"], category, fragment)
                self.assertIsNotNone(entry, f"no {category}/{fragment!r} entry in {result['inventory']}")
                self.assertEqual(entry["occurrences"], 1)
                self.assertTrue(entry["span_samples"])
                sample = entry["span_samples"][0]
                self.assertTrue(sample["text"])

    def test_inventory_collapses_repeats(self):
        """Repeated identical sequences collapse into one entry with occurrences."""
        text = ("\x1b[31m" * 7) + "hi" + ("\x1b[0m" * 3)
        result = self.tool.execute(mode="classify", text=text)
        by_code = {e["code"]: e for e in result["inventory"]}
        self.assertEqual(by_code["CSI 31m"]["occurrences"], 7)
        self.assertEqual(by_code["CSI 0m"]["occurrences"], 3)
        self.assertEqual(len(by_code["CSI 31m"]["span_samples"]), 7)
        self.assertEqual(len(by_code["CSI 0m"]["span_samples"]), 3)
        self.assertEqual(result["total_sequences"], 10)
        self.assertEqual(result["total_text_chars"], 2)

    def test_explain_csi_decomposition(self):
        """Explain decomposes grammar parts of a DEC private mode sequence."""
        result = self.tool.execute(mode="explain", sequence="\x1b[?25h")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["category"], "mode")
        self.assertEqual(result["decomposition"]["introducer"], "ESC [")
        self.assertEqual(result["decomposition"]["private_parameter"], "?")
        self.assertEqual(result["decomposition"]["parameters"], "25")
        self.assertEqual(result["decomposition"]["intermediates"], "")
        self.assertEqual(result["decomposition"]["final_byte"], "h")
        self.assertEqual(result["human"], "Show cursor (DECTCEM ?25 set)")
        self.assertIn("DEC private modes", result["spec_note"])

    def test_explain_spec_notes_divergences(self):
        """Explain carries xterm-vs-ECMA-48 notes where the two differ."""
        cases = {
            "\x1b[21m": "double underline",
            "\x1b[3X": "ECH",
            "\x1b[38;5;196m": "postdate ECMA-48",
            "\x1b[91m": "aixterm",
            "\x1b]8;;https://x.dev\x07": "xterm/iTerm2 extension",
            "\x1b]0;title\x07": "BEL termination",
            "\x1b7": "DECSC/DECRC",
            "\x1b[2 q": "",  # DECSCUSR: no divergence note required
        }
        for sequence, fragment in cases.items():
            with self.subTest(sequence=sequence):
                result = self.tool.execute(mode="explain", sequence=sequence)
                self.assertEqual(result["status"], "success", result)
                if fragment:
                    self.assertIn(fragment, result["spec_note"])
                else:
                    self.assertEqual(result["spec_note"], "")

    def test_explain_osc8_and_c1(self):
        """Explain shows OSC 8 payload/terminator and flags C1 origin."""
        result = self.tool.execute(mode="explain", sequence="\x1b]8;;https://a.dev\x07")
        self.assertEqual(result["decomposition"]["command"], "8")
        self.assertEqual(result["decomposition"]["payload"], "https://a.dev")
        self.assertEqual(result["decomposition"]["terminator"], "BEL (0x07)")
        self.assertIn("hyperlink", result["human"])
        c1 = self.tool.execute(mode="explain", sequence="\x9b31m")
        self.assertEqual(c1["decomposition"]["introducer"], "C1 CSI (U+009B)")
        self.assertTrue(c1["c1_8bit_detected"])
        self.assertIn("UTF-8", c1["spec_note"])


class ConsoleAnsiStripSanitizeTest(unittest.TestCase):
    """strip and sanitize mode behavior."""

    def setUp(self):
        """Fresh tool per test."""
        self.tool = ConsoleAnsiTool()

    def test_strip_removes_all_sequences(self):
        """Strip removes every escape run but keeps visible chars and bare C0."""
        text = "\x1b[1;31mERR\x1b[0m: \x1b]8;;https://x\x07link\x1b]8;;\x07\r\n\x1b[2Kdone"
        result = self.tool.execute(mode="strip", text=text)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["clean"], "ERR: link\r\ndone")
        self.assertEqual(result["classes_removed"], {"sgr": 2, "osc-link": 2, "erase": 1})
        self.assertEqual(result["removed_count"], 5)
        self.assertEqual(result["bytes_removed"], len(text) - len(result["clean"]))
        self.assertFalse(result["truncated_at_eof"])

    def test_strip_empty_and_plain(self):
        """Empty and plain inputs strip to themselves with zero removals."""
        self.assertEqual(self.tool.execute(mode="strip", text="")["clean"], "")
        result = self.tool.execute(mode="strip", text="plain text only")
        self.assertEqual(result["clean"], "plain text only")
        self.assertEqual(result["removed_count"], 0)
        self.assertEqual(result["classes_removed"], {})

    def test_sanitize_policies(self):
        """Policies keep only their categories, byte-preserved."""
        text = "\x1b[31mred\x1b[?25l\x1b]8;;https://x\x07go\x1b]8;;\x07\x1b[0m"
        none = self.tool.execute(mode="sanitize", text=text, keep="none")
        self.assertEqual(none["output"], "redgo")
        self.assertEqual(none["kept_count"], 0)
        self.assertEqual(none["removed"], {"sgr": 2, "mode": 1, "osc-link": 2})
        sgr = self.tool.execute(mode="sanitize", text=text, keep="sgr-only")
        self.assertEqual(sgr["output"], "\x1b[31mredgo\x1b[0m")
        self.assertEqual(sgr["kept_count"], 2)
        self.assertEqual(sgr["removed"], {"mode": 1, "osc-link": 2})
        safe = self.tool.execute(mode="sanitize", text=text, keep="safe")
        self.assertEqual(safe["output"], "\x1b[31mred\x1b]8;;https://x\x07go\x1b]8;;\x07\x1b[0m")
        self.assertEqual(safe["kept_count"], 4)

    def test_sanitize_kept_sequences_are_byte_preserved(self):
        """Kept sequences pass through as their original bytes (no rewriting)."""
        original = "\x1b[38;2;10;20;30m\x1b]8;;https://ex.dev/p?q=1\x07label\x1b]8;;\x07\x1b[0m"
        result = self.tool.execute(mode="sanitize", text=original + "\x1b[2J", keep="safe")
        self.assertEqual(result["output"], original)
        self.assertTrue(result["output"].endswith("\x1b[0m"))


class ConsoleAnsiIncompleteBatteryTest(unittest.TestCase):
    """Incomplete / invalid / C1 edge cases (documented deterministic rules)."""

    def setUp(self):
        """Fresh tool per test."""
        self.tool = ConsoleAnsiTool()

    def test_truncated_csi_at_eof(self):
        """A CSI run cut off at EOF is removed and flagged with pending bytes."""
        result = self.tool.execute(mode="strip", text="ok\x1b[31")
        self.assertEqual(result["clean"], "ok")
        self.assertTrue(result["truncated_at_eof"])
        self.assertEqual(result["pending"], "\x1b[31")
        self.assertEqual(result["incomplete_removed"], 1)
        self.assertEqual(result["invalid_removed"], 0)
        self.assertEqual(result["classes_removed"], {})
        self.assertFalse(result["pending_truncated"])

    def test_osc_without_terminator_consumes_to_eof(self):
        """OSC lacking BEL/ST is consumed to EOF, flagged, and noted."""
        result = self.tool.execute(mode="strip", text="x\x1b]0;title")
        self.assertEqual(result["clean"], "x")
        self.assertTrue(result["truncated_at_eof"])
        self.assertTrue(any("OSC" in note for note in result["info"]))
        classified = self.tool.execute(mode="classify", text="x\x1b]0;title")
        self.assertEqual(classified["total_sequences"], 0)
        self.assertEqual(classified["inventory"], [])

    def test_lone_esc_at_eof(self):
        """A trailing ESC alone is an incomplete run with pending byte."""
        result = self.tool.execute(mode="strip", text="abc\x1b")
        self.assertEqual(result["clean"], "abc")
        self.assertTrue(result["truncated_at_eof"])
        self.assertEqual(result["pending"], "\x1b")

    def test_c1_9b_uncompletable_is_text_plus_info(self):
        """C1 CSI that cannot complete in UTF-8 text stays as text + info flag."""
        result = self.tool.execute(mode="strip", text="prix \x9b élevé")
        self.assertEqual(result["clean"], "prix \x9b élevé")
        self.assertTrue(result["c1_8bit_detected"])
        self.assertEqual(result["removed_count"], 0)
        self.assertTrue(any("UTF-8" in note for note in result["info"]))

    def test_c1_9b_completing_is_parsed(self):
        """A completing 8-bit CSI parses and strips like its 7-bit form."""
        result = self.tool.execute(mode="strip", text="\x9b31mred")
        self.assertEqual(result["clean"], "red")
        self.assertEqual(result["classes_removed"], {"sgr": 1})
        self.assertTrue(result["c1_8bit_detected"])

    def test_abandoned_runs_rescan_at_offender(self):
        """Runs abandoned by ESC keep the offending byte scannable."""
        result = self.tool.execute(mode="strip", text="\x1b]0;t\x1b[31mx")
        self.assertEqual(result["clean"], "x")
        self.assertEqual(result["invalid_removed"], 1)
        self.assertEqual(result["classes_removed"], {"sgr": 1})

    def test_dcs_consumed_to_st(self):
        """DCS data is consumed to ST; BEL inside DCS is data, not a terminator."""
        self.assertEqual(self.tool.execute(mode="strip", text="\x1bP1;2q\x07data\x1b\\ok")["clean"], "ok")

    def test_stray_esc_kept_as_text(self):
        """ESC followed by a non-grammar byte is kept as literal text."""
        result = self.tool.execute(mode="strip", text="a\x1béb")
        self.assertEqual(result["clean"], "a\x1béb")
        self.assertTrue(any("stray ESC" in note for note in result["info"]))

    def test_charset_intermediate_run_invalid(self):
        """ESC + intermediates + invalid byte drops only the escape prefix."""
        result = self.tool.execute(mode="strip", text="\x1b(éok")
        self.assertEqual(result["clean"], "éok")
        self.assertEqual(result["invalid_removed"], 1)

    def test_explain_incomplete_sequence(self):
        """Explain reports an incomplete sequence without erroring."""
        result = self.tool.execute(mode="explain", sequence="\x1b[38;5")
        self.assertEqual(result["status"], "success")
        self.assertFalse(result["complete"])
        self.assertEqual(result["category"], "incomplete")
        self.assertEqual(result["decomposition"]["pending"], "\x1b[38;5")


class ConsoleAnsiPropertyFuzzTest(unittest.TestCase):
    """Seeded grammar fuzz: strip/classify/sanitize cross-mode invariants."""

    def setUp(self):
        """Fresh tool and word pool per test."""
        self.tool = ConsoleAnsiTool()
        self.words = ["deploy", "cache", "matrix", "kernel", "signal", "queue", "delta", "vector", "étoile", "naïve"]

    def _sgr(self, rng):
        """A random well-formed SGR sequence."""
        return rng.choice(
            [
                "\x1b[%dm" % rng.randint(30, 37),
                "\x1b[1m",
                "\x1b[0m",
                "\x1b[%d;%dm" % (rng.choice([1, 2, 4]), rng.randint(30, 37)),
                "\x1b[38;5;%dm" % rng.randint(0, 255),
                "\x1b[38;2;%d;%d;%dm" % (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255)),
                "\x1b[38:5:%dm" % rng.randint(0, 255),
            ]
        )

    def _gen(self, rng):
        """A terminal-noise text: colored CLI output, progress bars, prompts."""
        parts = []
        for _ in range(rng.randint(1, 24)):
            roll = rng.random()
            if roll < 0.28:
                parts.append(rng.choice(self.words))
            elif roll < 0.46:
                parts.append(self._sgr(rng))
            elif roll < 0.56:
                parts.append(rng.choice(["\x1b[2K", "\x1b[1K", "\x1b[J", "\x1b[2J", "\x1b[5X"]))
            elif roll < 0.70:
                width = rng.randint(3, 12)
                filled = rng.randint(0, width)
                parts.append(
                    "[" + "=" * filled + ">" + "." * (width - filled) + "] %d%%\r\x1b[2K\r\x1b[1G" % rng.randint(0, 100)
                )
            elif roll < 0.80:
                url = "https://example.invalid/" + rng.choice(self.words)
                parts.append("\x1b]8;;" + url + "\x07" + rng.choice(self.words) + "\x1b]8;;\x07")
            elif roll < 0.88:
                parts.append("\x1b]2;" + rng.choice(self.words) + "\x07")
            else:
                parts.append(
                    rng.choice(
                        [
                            "\x1b7",
                            "\x1b8",
                            "\x1b(B",
                            "\x1b[6n",
                            "\x1bP1$q\x1b\\",
                            "\x1b[?1049h",
                            "\x1b[?25l",
                            "\x1b[3J",
                            "\x1b[2;10r",
                            "\x1b[3B\x1b[5C",
                        ]
                    )
                )
        return "".join(parts)

    def test_strip_classify_sanitize_consistency(self):
        """500 seeded texts: counts agree, sanitize(none) equals strip clean."""
        master = random.Random(20261021)
        for i in range(500):
            text = self._gen(master)
            with self.subTest(index=i):
                stripped = self.tool.execute(mode="strip", text=text)
                classified = self.tool.execute(mode="classify", text=text)
                self.assertEqual(stripped["status"], "success")
                self.assertEqual(classified["status"], "success")
                expected_classes = {}
                for entry in classified["inventory"]:
                    expected_classes[entry["category"]] = expected_classes.get(entry["category"], 0) + entry["occurrences"]
                self.assertEqual(stripped["classes_removed"], expected_classes)
                self.assertEqual(
                    stripped["removed_count"],
                    classified["total_sequences"] + stripped["incomplete_removed"] + stripped["invalid_removed"],
                )
                none_policy = self.tool.execute(mode="sanitize", text=text, keep="none")
                self.assertEqual(none_policy["output"], stripped["clean"])
                expected_removed = dict(stripped["classes_removed"])
                if stripped["invalid_removed"]:
                    expected_removed["invalid"] = stripped["invalid_removed"]
                if stripped["incomplete_removed"]:
                    expected_removed["incomplete"] = stripped["incomplete_removed"]
                self.assertEqual(none_policy["removed"], expected_removed)
                # Determinism: identical repeat run.
                self.assertEqual(self.tool.execute(mode="strip", text=text), stripped)

    def test_sanitize_identity_when_all_categories_kept(self):
        """Passthrough is byte-identical when the corpus is only kept kinds."""
        master = random.Random(0xC0FFEE)
        for i in range(200):
            text = "".join(
                master.choice([self._sgr(master), master.choice(self.words), " "])
                for _ in range(master.randint(1, 12))
            )
            with self.subTest(index=i):
                result = self.tool.execute(mode="sanitize", text=text, keep="sgr-only")
                self.assertEqual(result["output"], text)
                self.assertEqual(result["removed"], {})
                self.assertEqual(result["kept_count"], text.count("\x1b"))

    def test_sanitize_safe_identity_with_hyperlinks(self):
        """keep=safe round-trips SGR + OSC 8 + text corpora unchanged."""
        master = random.Random(0x05C8)
        for i in range(200):
            url = "https://example.invalid/" + str(master.randint(0, 999))
            pieces = [self._sgr(master), "\x1b]8;;" + url + "\x07", master.choice(self.words), "\x1b]8;;\x07", self._sgr(master)]
            text = "".join(pieces)
            with self.subTest(index=i):
                result = self.tool.execute(mode="sanitize", text=text, keep="safe")
                self.assertEqual(result["output"], text)
                self.assertEqual(result["kept_count"], 4)


class ConsoleAnsiPathologicalTest(unittest.TestCase):
    """Pathological inputs: linear runtime and bounded output."""

    def setUp(self):
        """Fresh tool per test."""
        self.tool = ConsoleAnsiTool()

    def test_one_megabyte_sgr_repetition_under_two_seconds(self):
        """1MB of repeated SGR sequences strips in under 2 seconds (no quadratic)."""
        text = "\x1b[31m" * 209715  # 1048575 bytes, just under 1 MiB
        self.assertLess(len(text), 2_000_000)
        start = time.monotonic()
        result = self.tool.execute(mode="strip", text=text)
        elapsed = time.monotonic() - start
        self.assertEqual(result["clean"], "")
        self.assertEqual(result["removed_count"], 209715)
        self.assertEqual(result["classes_removed"], {"sgr": 209715})
        self.assertLess(elapsed, 2.0, "strip must stay linear: %.3fs" % elapsed)

    def test_100k_distinct_sequences_bounded_inventory(self):
        """100k distinct codes collapse to a capped, flagged inventory."""
        text = "".join("\x1b[%dm" % i for i in range(100_000))
        result = self.tool.execute(mode="classify", text=text)
        self.assertEqual(result["total_sequences"], 100_000)
        self.assertLessEqual(len(result["inventory"]), 200)
        self.assertTrue(result["inventory_truncated"])
        self.assertEqual(result["omitted_codes"], 100_000 - 200)
        for entry in result["inventory"]:
            self.assertLessEqual(len(entry["span_samples"]), 8)
            for sample in entry["span_samples"]:
                self.assertLessEqual(len(sample["text"]), 48)
        stripped = self.tool.execute(mode="strip", text=text)
        self.assertEqual(stripped["classes_removed"], {"sgr": 100_000})

    def test_determinism_on_mixed_corpus(self):
        """Repeat runs over a mixed corpus return byte-identical results."""
        master = random.Random(7)
        words = ["a", "b", "longer word", "\xe9"]
        text = "".join(
            master.choice(["\x1b[31m", "\x1b[0m", "\x1b]8;;https://x\x07k\x1b]8;;\x07", "\x1b[2K", master.choice(words)])
            for _ in range(2000)
        )
        first = self.tool.execute(mode="classify", text=text)
        second = self.tool.execute(mode="classify", text=text)
        self.assertEqual(first, second)


class ConsoleAnsiValidationTest(unittest.TestCase):
    """Mode/option validation and structured errors."""

    def setUp(self):
        """Fresh tool per test."""
        self.tool = ConsoleAnsiTool()

    def test_invalid_mode(self):
        """Unknown modes return structured validation errors."""
        result = self.tool.execute(mode="paint", text="x")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_text_type_required(self):
        """strip/classify/sanitize require a string text."""
        self.assertEqual(self.tool.execute(mode="strip")["status"], "error")
        self.assertEqual(self.tool.execute(mode="strip", text=7)["status"], "error")
        self.assertEqual(self.tool.execute(mode="classify", text=None)["status"], "error")

    def test_keep_only_for_sanitize(self):
        """keep is rejected outside sanitize and validated inside it."""
        self.assertEqual(self.tool.execute(mode="strip", text="x", keep="safe")["status"], "error")
        self.assertEqual(self.tool.execute(mode="sanitize", text="x", keep="everything")["status"], "error")

    def test_input_caps(self):
        """Oversized input is rejected with the configured cap."""
        small = ConsoleAnsiTool(max_input_chars=8)
        self.assertEqual(small.execute(mode="strip", text="x" * 9)["status"], "error")
        self.assertEqual(small.execute(mode="strip", text="x" * 8)["status"], "success")

    def test_explain_requires_single_sequence(self):
        """Explain rejects multiple sequences or surrounding text."""
        self.assertEqual(self.tool.execute(mode="explain", sequence="a\x1b[31mb")["status"], "error")
        self.assertEqual(self.tool.execute(mode="explain", sequence="\x1b[31m\x1b[0m")["status"], "error")
        self.assertEqual(self.tool.execute(mode="explain")["status"], "error")

    def test_config_tuning_validation(self):
        """Non-positive tunables fail validation."""
        broken = ConsoleAnsiTool(max_codes=0)
        self.assertEqual(broken.execute(mode="classify", text="\x1b[31m")["status"], "error")
        broken2 = ConsoleAnsiTool(max_input_chars=-1)
        self.assertEqual(broken2.execute(mode="strip", text="x")["status"], "error")


class ConsoleAnsiRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped console_ansi_tool.yaml."""

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
        """The shipped yaml resolves to a tool component exposing ConsoleAnsiTool."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "ConsoleAnsiTool")

    def test_manager(self):
        """ConsoleAnsiTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, ConsoleAnsiTool)
        self.assertEqual(tool.input_keys, ["mode", "text"])

    def test_exported_from_package(self):
        """ConsoleAnsiTool is exported by the common_tool package."""
        from agentuniverse.agent.action.tool.common_tool import ConsoleAnsiTool as Exported
        from agentuniverse.agent.action.tool.common_tool import __all__ as exported_all

        self.assertIs(Exported, ConsoleAnsiTool)
        self.assertIn("ConsoleAnsiTool", exported_all)


if __name__ == "__main__":
    unittest.main()
