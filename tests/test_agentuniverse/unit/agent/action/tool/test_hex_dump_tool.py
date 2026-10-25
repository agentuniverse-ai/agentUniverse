#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_hex_dump_tool.py

"""Offline unit tests for HexDumpTool.

The tool is built purely on the standard library (base64, binascii,
re) and never touches the network, so this suite runs fully offline.
Every assertion is deterministic: dump output is checked against
hand-built xxd-style ground-truth lines (offset column, hex byte
pairs, blank-padded short lines, ASCII column) for "Hello, World!\\n"
and multi-line inputs at every supported width, the printable-column
rule (0x20-0x7E kept, everything else '.') against the full 256-byte
range, find results against literal match-offset lists including the
documented overlapping-match policy, and patch results against known
Base64 vectors. Error handling is covered by a full matrix of
ValueError parameter cases and structured error payloads.
"""

import base64
import unittest

from agentuniverse.agent.action.tool.common_tool import HexDumpTool
from agentuniverse.agent.action.tool.common_tool.hex_dump_tool import (
    HexDumpTool as DirectHexDumpTool,
)

# --------------------------------------------------------------------- #
# Hand-built ground truths (literal expected values)
# --------------------------------------------------------------------- #
# "Hello, World!\n" -> 48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21 0a (14 bytes)
HELLO_B64 = "SGVsbG8sIFdvcmxkIQo="
JELLO_B64 = "SmVsbG8sIFdvcmxkIQo="
JJJ_HELLO_B64 = "SkpKbG8sIFdvcmxkIQo="
JELLO_XORLD_B64 = "SmVsbG8sIFhvcmxkIQo="
JELLO5_B64 = "SmVsbG8="
ABCDEF_B64 = base64.b64encode(b"abcdef").decode("ascii")
XZBREF_B64 = "WFpbZGVm"  # base64 of b"XZ[def" (overlapping patch order)

HELLO_W16 = (
    "00000000  48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21 0a"
    + " " * 8
    + "|Hello, World!.|"
)
HELLO_W8_L0 = "00000000  48 65 6c 6c 6f 2c 20 57  |Hello, W|"
HELLO_W8_L1 = "00000008  6f 72 6c 64 21 0a" + " " * 8 + "|orld!.|"
HELLO_W8 = HELLO_W8_L0 + "\n" + HELLO_W8_L1
HELLO_W32 = (
    "00000000  48 65 6c 6c 6f 2c 20 57 6f 72 6c 64 21 0a"
    + " " * 56
    + "|Hello, World!.|"
)

MULTILINE = "line one\nline two\nline three\n"  # 29 bytes
MULTILINE_W16 = (
    "00000000  6c 69 6e 65 20 6f 6e 65 0a 6c 69 6e 65 20 74 77  "
    "|line one.line tw|\n"
    "00000010  6f 0a 6c 69 6e 65 20 74 68 72 65 65 0a"
    + " " * 11
    + "|o.line three.|"
)
MULTILINE_W8 = (
    "00000000  6c 69 6e 65 20 6f 6e 65  |line one|\n"
    "00000008  0a 6c 69 6e 65 20 74 77  |.line tw|\n"
    "00000010  6f 0a 6c 69 6e 65 20 74  |o.line t|\n"
    "00000018  68 72 65 65 0a"
    + " " * 11
    + "|hree.|"
)
MULTILINE_W32 = (
    "00000000  6c 69 6e 65 20 6f 6e 65 0a 6c 69 6e 65 20 74 77 6f 0a "
    "6c 69 6e 65 20 74 68 72 65 65 0a"
    + " " * 11
    + "|line one.line two.line three.|"
)

# "你好" -> e4 bd a0 e5 a5 bd (6 UTF-8 bytes, none printable as ASCII).
CJK_W16 = "00000000  e4 bd a0 e5 a5 bd" + " " * 32 + "|......|"
CJK_W8 = "00000000  e4 bd a0 e5 a5 bd" + " " * 8 + "|......|"

# Full 256-byte value range at width 32: eight lines.
ALL_BYTES_B64 = base64.b64encode(bytes(range(256))).decode("ascii")
ALL_BYTES_HEX_00_1F = " ".join(f"{b:02x}" for b in range(0x00, 0x20))
ALL_BYTES_LINE0 = f"00000000  {ALL_BYTES_HEX_00_1F}  |{'.' * 32}|"
ASCII_20_3F = " !\"#$%&'()*+,-./0123456789:;<=>?"
ASCII_40_5F = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_"
ASCII_60_7F = "`abcdefghijklmnopqrstuvwxyz{|}~."


class HexDumpToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib HexDumpTool."""

    def setUp(self) -> None:
        self.tool = HexDumpTool()

    # ------------------------------------------------------------------ #
    # dump mode — exact ground truths
    # ------------------------------------------------------------------ #

    def test_package_and_direct_import_expose_same_class(self) -> None:
        self.assertIs(HexDumpTool, DirectHexDumpTool)

    def test_dump_hello_width_16_default(self) -> None:
        result = self.tool.execute(mode="dump", data="Hello, World!\n")
        self.assertEqual(
            result,
            {
                "mode": "dump",
                "input_encoding": "utf8-text",
                "size": 14,
                "width": 16,
                "result": HELLO_W16,
            },
        )

    def test_dump_hello_width_8(self) -> None:
        result = self.tool.execute(mode="dump", data="Hello, World!\n", width=8)
        self.assertEqual(result["width"], 8)
        self.assertEqual(result["result"], HELLO_W8)

    def test_dump_hello_width_32(self) -> None:
        result = self.tool.execute(mode="dump", data="Hello, World!\n", width=32)
        self.assertEqual(result["width"], 32)
        self.assertEqual(result["result"], HELLO_W32)

    def test_dump_multiline_width_16(self) -> None:
        result = self.tool.execute(mode="dump", data=MULTILINE)
        self.assertEqual(result["size"], 29)
        self.assertEqual(result["result"], MULTILINE_W16)

    def test_dump_multiline_width_8(self) -> None:
        result = self.tool.execute(mode="dump", data=MULTILINE, width=8)
        self.assertEqual(result["result"], MULTILINE_W8)

    def test_dump_multiline_width_32(self) -> None:
        result = self.tool.execute(mode="dump", data=MULTILINE, width=32)
        self.assertEqual(result["result"], MULTILINE_W32)

    def test_dump_cjk_utf8_bytes(self) -> None:
        result = self.tool.execute(mode="dump", data="你好")
        self.assertEqual(result["size"], 6)
        self.assertEqual(result["result"], CJK_W16)
        result = self.tool.execute(mode="dump", data="你好", width=8)
        self.assertEqual(result["result"], CJK_W8)

    def test_dump_width_accepts_digit_string(self) -> None:
        result = self.tool.execute(mode="dump", data="Hello, World!\n", width="8")
        self.assertEqual(result["width"], 8)
        self.assertEqual(result["result"], HELLO_W8)

    def test_dump_base64_input_path(self) -> None:
        result = self.tool.execute(
            mode="dump", data=HELLO_B64, input_encoding="base64"
        )
        self.assertEqual(
            result,
            {
                "mode": "dump",
                "input_encoding": "base64",
                "size": 14,
                "width": 16,
                "result": HELLO_W16,
            },
        )

    def test_dump_printable_column_rule_over_full_byte_range(self) -> None:
        result = self.tool.execute(
            mode="dump", data=ALL_BYTES_B64, input_encoding="base64", width=32
        )
        lines = result["result"].split("\n")
        self.assertEqual(result["size"], 256)
        self.assertEqual(len(lines), 8)
        # Control bytes 0x00-0x1F all render as '.'.
        self.assertEqual(lines[0], ALL_BYTES_LINE0)
        # 0x20-0x3F, 0x40-0x5F and 0x60-0x7E are kept; 0x7F becomes '.'.
        self.assertTrue(lines[1].endswith(f"|{ASCII_20_3F}|"))
        self.assertTrue(lines[2].endswith(f"|{ASCII_40_5F}|"))
        self.assertTrue(lines[3].endswith(f"|{ASCII_60_7F}|"))
        # All high bytes 0x80-0xFF render as '.'.
        for line in lines[4:]:
            self.assertTrue(line.endswith("|" + "." * 32 + "|"))
        # Offsets advance by the width; hex pairs are lowercase and aligned.
        self.assertTrue(lines[1].startswith("00000020  20 21 22 23 24 25 26 27"))
        self.assertTrue(lines[7].startswith("000000e0  e0 e1 e2 e3 e4 e5 e6 e7"))
        # The hex area is exactly 3 * width - 1 characters wide, so the
        # ASCII column always starts at the same position.
        for line in lines:
            self.assertEqual(line[10 + 95 : 10 + 95 + 3], "  |")

    # ------------------------------------------------------------------ #
    # find mode
    # ------------------------------------------------------------------ #

    def test_find_simple_offset_and_context(self) -> None:
        result = self.tool.execute(mode="find", data="Hello, World!\n", pattern="0a")
        self.assertEqual(
            result,
            {
                "mode": "find",
                "input_encoding": "utf8-text",
                "size": 14,
                "width": 16,
                "pattern": "0a",
                "matches": [{"offset": 13, "context": [HELLO_W16]}],
                "total_matches": 1,
                "truncated": False,
                "result": "1 match(es) at byte offset(s): 13",
            },
        )

    def test_find_literal_multibyte_pattern(self) -> None:
        result = self.tool.execute(mode="find", data="Hello, World!\n", pattern="6c6c")
        self.assertEqual([m["offset"] for m in result["matches"]], [2])

    def test_find_wildcard_bytes(self) -> None:
        # 'o??d' is 6f ?? ?? 64 — it matches "orld" (6f 72 6c 64) at 8.
        result = self.tool.execute(
            mode="find", data="Hello, World!\n", pattern="6f????64"
        )
        self.assertEqual([m["offset"] for m in result["matches"]], [8])
        # Each '??' is exactly one wildcard byte: 6f ?? 64 (o-any-d)
        # has no occurrence in "Hello, World!\n".
        result = self.tool.execute(mode="find", data="Hello, World!\n", pattern="6f??64")
        self.assertEqual(result["total_matches"], 0)

    def test_find_pattern_case_insensitive_and_normalized(self) -> None:
        result = self.tool.execute(
            mode="find", data="Hello, World!\n", pattern="6F????64"
        )
        self.assertEqual(result["pattern"], "6f????64")
        self.assertEqual([m["offset"] for m in result["matches"]], [8])

    def test_find_all_wildcard_pattern(self) -> None:
        result = self.tool.execute(mode="find", data="abc", pattern="????")
        self.assertEqual([m["offset"] for m in result["matches"]], [0, 1])
        self.assertEqual(result["total_matches"], 2)

    def test_find_overlapping_matches_all_reported(self) -> None:
        # Documented policy: every start position matches, overlapping
        # included — "6161" in "aaaa" hits offsets 0, 1 and 2.
        result = self.tool.execute(mode="find", data="aaaa", pattern="6161")
        self.assertEqual([m["offset"] for m in result["matches"]], [0, 1, 2])
        self.assertEqual(result["total_matches"], 3)
        self.assertFalse(result["truncated"])

    def test_find_full_length_pattern_single_match(self) -> None:
        result = self.tool.execute(mode="find", data="aaaa", pattern="61616161")
        self.assertEqual([m["offset"] for m in result["matches"]], [0])

    def test_find_no_match(self) -> None:
        result = self.tool.execute(mode="find", data="Hello, World!\n", pattern="ffff")
        self.assertEqual(result["matches"], [])
        self.assertEqual(result["total_matches"], 0)
        self.assertFalse(result["truncated"])
        self.assertEqual(
            result["result"], "0 match(es) found — the pattern does not occur in the input"
        )

    def test_find_context_spans_two_lines(self) -> None:
        # "Wo" (57 6f) sits at bytes 7-8, crossing the width-8 line break.
        result = self.tool.execute(
            mode="find", data="Hello, World!\n", pattern="576f", width=8
        )
        self.assertEqual(
            result["matches"], [{"offset": 7, "context": [HELLO_W8_L0, HELLO_W8_L1]}]
        )

    def test_find_base64_input_path(self) -> None:
        result = self.tool.execute(
            mode="find", data=HELLO_B64, input_encoding="base64", pattern="2c20"
        )
        self.assertEqual(result["size"], 14)
        self.assertEqual([m["offset"] for m in result["matches"]], [5])

    def test_find_truncates_reported_matches_beyond_cap(self) -> None:
        # 1100 'a' bytes: "6161" matches at every offset 0..1098 = 1099
        # overlapping matches; only the first 1000 carry context.
        result = self.tool.execute(mode="find", data="a" * 1100, pattern="6161")
        self.assertEqual(result["total_matches"], 1099)
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["matches"]), 1000)
        self.assertEqual(result["matches"][0]["offset"], 0)
        self.assertEqual(
            result["matches"][0]["context"],
            ["00000000  " + " ".join(["61"] * 16) + "  |" + "a" * 16 + "|"],
        )
        self.assertEqual(
            result["result"],
            "1,099 match(es) at byte offset(s): "
            + ", ".join(str(offset) for offset in range(100))
            + ", ... (first 1,000 of 1,099 matches reported)",
        )

    # ------------------------------------------------------------------ #
    # patch mode
    # ------------------------------------------------------------------ #

    def test_patch_single_byte_known_vector(self) -> None:
        result = self.tool.execute(
            mode="patch",
            data=HELLO_B64,
            input_encoding="base64",
            patches=[{"offset": 0, "hex": "4a"}],
        )
        self.assertEqual(
            result,
            {
                "mode": "patch",
                "input_encoding": "base64",
                "size": 14,
                "patches_applied": 1,
                "result": JELLO_B64,
            },
        )

    def test_patch_multibyte_known_vector(self) -> None:
        result = self.tool.execute(
            mode="patch",
            data=HELLO_B64,
            input_encoding="base64",
            patches=[{"offset": 0, "hex": "4a4a4a"}],
        )
        self.assertEqual(result["result"], JJJ_HELLO_B64)

    def test_patch_multiple_patches_and_string_offset(self) -> None:
        result = self.tool.execute(
            mode="patch",
            data=HELLO_B64,
            input_encoding="base64",
            patches=[{"offset": 0, "hex": "4a"}, {"offset": "7", "hex": "58"}],
        )
        self.assertEqual(result["patches_applied"], 2)
        self.assertEqual(result["result"], JELLO_XORLD_B64)

    def test_patch_overlapping_patches_applied_in_list_order(self) -> None:
        # Documented policy: patches apply sequentially, so the later
        # patch overwrites the overlapping region of the earlier one.
        result = self.tool.execute(
            mode="patch",
            data=ABCDEF_B64,
            input_encoding="base64",
            patches=[{"offset": 0, "hex": "5859"}, {"offset": 1, "hex": "5a5b"}],
        )
        self.assertEqual(result["result"], XZBREF_B64)

    def test_patch_utf8_text_input(self) -> None:
        result = self.tool.execute(
            mode="patch", data="Hello", patches=[{"offset": 0, "hex": "4a"}]
        )
        self.assertEqual(
            result,
            {
                "mode": "patch",
                "input_encoding": "utf8-text",
                "size": 5,
                "patches_applied": 1,
                "result": JELLO5_B64,
            },
        )

    def test_patch_result_round_trips_through_dump(self) -> None:
        patched = self.tool.execute(
            mode="patch",
            data=HELLO_B64,
            input_encoding="base64",
            patches=[{"offset": 0, "hex": "4a"}],
        )["result"]
        dumped = self.tool.execute(
            mode="dump", data=patched, input_encoding="base64"
        )["result"]
        self.assertTrue(dumped.startswith("00000000  4a 65 6c 6c"))
        self.assertTrue(dumped.endswith("|Jello, World!.|"))

    def test_patch_offset_at_end_is_out_of_range(self) -> None:
        result = self.tool.execute(
            mode="patch",
            data=HELLO_B64,
            input_encoding="base64",
            patches=[{"offset": 14, "hex": "41"}],
        )
        self.assertEqual(result["error"]["type"], "offset_out_of_range")
        self.assertIn("14-byte", result["error"]["message"])

    def test_patch_writing_past_end_is_out_of_range(self) -> None:
        result = self.tool.execute(
            mode="patch",
            data=HELLO_B64,
            input_encoding="base64",
            patches=[{"offset": 13, "hex": "4142"}],
        )
        self.assertEqual(result["error"]["type"], "offset_out_of_range")
        self.assertIn("patch #0", result["error"]["message"])
        self.assertIn("14", result["error"]["message"])

    def test_patch_out_of_range_error_reports_offending_index(self) -> None:
        result = self.tool.execute(
            mode="patch",
            data=ABCDEF_B64,
            input_encoding="base64",
            patches=[
                {"offset": 0, "hex": "41"},
                {"offset": 5, "hex": "4243"},  # 5 + 2 > 6
            ],
        )
        self.assertEqual(result["error"]["type"], "offset_out_of_range")
        self.assertIn("patch #1", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # Content-level error payloads
    # ------------------------------------------------------------------ #

    def test_invalid_base64_input_returns_error_payload(self) -> None:
        result = self.tool.execute(
            mode="dump", data="not valid base64!", input_encoding="base64"
        )
        self.assertEqual(result["mode"], "dump")
        self.assertEqual(result["input_encoding"], "base64")
        self.assertEqual(result["error"]["type"], "invalid_base64")
        self.assertIn("Base64", result["error"]["message"])

    def test_invalid_base64_padding_returns_error_payload(self) -> None:
        result = self.tool.execute(
            mode="dump", data="SGVsbG8", input_encoding="base64"
        )
        self.assertEqual(result["error"]["type"], "invalid_base64")

    def test_find_invalid_base64_input_returns_error_payload(self) -> None:
        result = self.tool.execute(
            mode="find", data="??", input_encoding="base64", pattern="00"
        )
        self.assertEqual(result["error"]["type"], "invalid_base64")

    def test_patch_invalid_base64_input_returns_error_payload(self) -> None:
        result = self.tool.execute(
            mode="patch", data="%%%%", input_encoding="base64", patches=[{"offset": 0, "hex": "41"}]
        )
        self.assertEqual(result["error"]["type"], "invalid_base64")

    # ------------------------------------------------------------------ #
    # Parameter validation matrix (ValueError before any computation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs: object) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode_rejected(self) -> None:
        self.assert_invalid(mode="hexdump", data="hello")
        self.assert_invalid(mode=None, data="hello")

    def test_invalid_data_rejected(self) -> None:
        self.assert_invalid(mode="dump", data=None)
        self.assert_invalid(mode="dump", data="")
        self.assert_invalid(mode="dump", data=123)
        self.assert_invalid(mode="dump", data=b"bytes")
        self.assert_invalid(mode="dump", data=True)

    def test_invalid_input_encoding_rejected(self) -> None:
        self.assert_invalid(mode="dump", data="hello", input_encoding="hex")
        self.assert_invalid(mode="dump", data="hello", input_encoding="utf8")
        self.assert_invalid(mode="dump", data="hello", input_encoding=True)
        self.assert_invalid(mode="dump", data="hello", input_encoding=16)

    def test_invalid_width_rejected(self) -> None:
        self.assert_invalid(mode="dump", data="hello", width=12)
        self.assert_invalid(mode="dump", data="hello", width="12")
        self.assert_invalid(mode="dump", data="hello", width=True)
        self.assert_invalid(mode="dump", data="hello", width=16.5)
        self.assert_invalid(mode="dump", data="hello", width=0)

    def test_invalid_pattern_rejected(self) -> None:
        cases = [
            None,
            "",
            "484",  # odd length
            "?4",  # half wildcard
            "48 65",  # embedded whitespace
            "0x48",  # prefix
            "48??4",  # odd length with wildcard
            "48zz",
            42,
            True,
            "41" * 4097,  # over the 4096-byte pattern cap
        ]
        for pattern in cases:
            self.assert_invalid(mode="find", data="hello", pattern=pattern)

    def test_find_requires_pattern(self) -> None:
        self.assert_invalid(mode="find", data="hello")

    def test_invalid_patches_rejected(self) -> None:
        base = {"mode": "patch", "data": ABCDEF_B64, "input_encoding": "base64"}
        bad_patches = [
            None,
            [],
            "not-a-list",
            ["not-a-dict"],
            [{"offset": 0}],  # missing 'hex'
            [{"hex": "41"}],  # missing 'offset'
            [{"offset": 0, "hex": "41", "extra": 1}],  # unexpected key
            [{"offset": -1, "hex": "41"}],
            [{"offset": 1.5, "hex": "41"}],
            [{"offset": True, "hex": "41"}],
            [{"offset": "abc", "hex": "41"}],
            [{"offset": 0, "hex": ""}],
            [{"offset": 0, "hex": "4"}],  # odd length
            [{"offset": 0, "hex": "4g"}],
            [{"offset": 0, "hex": "4a??"}],  # wildcards not allowed
            [{"offset": 0, "hex": 123}],
            [{"offset": 0, "hex": True}],
            [{"offset": 0, "hex": "41"}] * 1001,  # over the 1000-patch cap
        ]
        for patches in bad_patches:
            self.assert_invalid(**base, patches=patches)

    def test_decoded_size_cap_enforced(self) -> None:
        with self.assertRaises(ValueError) as raised:
            self.tool.execute(mode="dump", data="a" * (1_048_576 + 1))
        self.assertIn("1,048,576", str(raised.exception))
        # Exactly at the cap is allowed.
        result = self.tool.execute(mode="dump", data="a" * 1_048_576, width=32)
        self.assertEqual(result["size"], 1_048_576)

    def test_validation_error_messages_are_prefixed(self) -> None:
        with self.assertRaises(ValueError) as raised:
            self.tool.execute(mode="dump", data="hello", width=12)
        self.assertTrue(str(raised.exception).startswith("hex_dump_tool: "))


if __name__ == "__main__":
    unittest.main()
