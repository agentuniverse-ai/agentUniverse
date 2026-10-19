#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_vcf_tool.py

"""Offline unit tests for VcfTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: the main fixture is a realistic multi-contact address
book (vCard 3.0, 2.1 quoted-printable CJK, a card missing FN, and 4.0)
checked against hand-computed ground-truth contact dicts, the filter
and summary modes against exact expected payloads, and the error
matrix against fixed structured error types. UTF-8 / quoted-printable
vectors were computed from the code points of 李 (U+674E), 四 (U+56DB),
王 (U+738B), 小 (U+5C0F) and 明 (U+660E).
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import VcfTool
from agentuniverse.agent.action.tool.common_tool.vcf_tool import (
    VcfTool as DirectVcfTool,
)

# --------------------------------------------------------------------- #
# Ground-truth fixture: four contacts covering vCard 3.0, 2.1
# quoted-printable (plain and soft-line-broken CJK), a missing FN and
# 4.0 quoted TYPE lists / PREF=1.
# --------------------------------------------------------------------- #
MAIN_VCARD = """BEGIN:VCARD
VERSION:3.0
FN:Dr. Alice Wang
N:Wang;Alice;Qiang;Dr.;Jr.
NICKNAME:Ace
ORG:Acme\\, Inc.;Research;Robotics
TITLE:Principal Engineer
TEL;TYPE=WORK,VOICE:+1-202-555-0100
TEL;TYPE=CELL;TYPE=PREF:+1-202-555-0199
item1.TEL:+1-202-555-0166
EMAIL;TYPE=INTERNET,PREF:alice.wang@acme-corp.com
EMAIL;TYPE=HOME:ace@example.net
ADR;TYPE=WORK:;Suite 900;100 Main Street;Springfield;IL;62704;United States
URL:https://alice.example.com/
NOTE:Loves hiking\\, climbing\\;
  and kayaking
BDAY:1985-04-12
CATEGORIES:Work,Friends,VIP
REV:2026-01-02T03:04:05Z
X-SOCIAL:alicew
END:VCARD
BEGIN:VCARD
VERSION:2.1
N;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:=E6=9D=8E;=E5=9B=9B;;;;
FN;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:=E6=9D=8E=E5=9B=9B
TEL;CELL;PREF:+8613800138000
TEL;WORK:+861058887777
EMAIL;INTERNET:lisi@example.cn
ORG:Beijing Tech Co\\, Ltd.;Mobile Division
ADR;WORK:;;2 Haidian Street;Beijing;Beijing;100080;China
URL:http://lisi.example.cn/
BDAY:19700101
END:VCARD
BEGIN:VCARD
VERSION:2.1
N;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:=E7=8E=8B;=
=E5=B0=8F=E6=98=8E;;;;
TEL;CELL:13800138000
END:VCARD
BEGIN:VCARD
VERSION:4.0
FN:Bob Chen
N:Chen;Bob;;;
TEL;TYPE=CELL;PREF=1:+1-202-555-0144
TEL;TYPE="CELL,WORK":+1-202-555-0177
EMAIL;TYPE=work:bob@example.org
CATEGORIES:community
END:VCARD
"""

ALICE = {
    "index": 1,
    "version": "3.0",
    "fn": "Dr. Alice Wang",
    "n": {
        "family": "Wang",
        "given": "Alice",
        "additional": "Qiang",
        "prefix": "Dr.",
        "suffix": "Jr.",
    },
    "nickname": "Ace",
    "org": {"name": "Acme, Inc.", "units": ["Research", "Robotics"]},
    "title": "Principal Engineer",
    "tel": [
        {"value": "+1-202-555-0100", "types": ["WORK", "VOICE"]},
        {"value": "+1-202-555-0199", "types": ["CELL", "PREF"]},
        {"value": "+1-202-555-0166", "types": []},
    ],
    "email": [
        {"value": "alice.wang@acme-corp.com", "types": ["INTERNET", "PREF"]},
        {"value": "ace@example.net", "types": ["HOME"]},
    ],
    "adr": [
        {
            "pobox": "",
            "ext": "Suite 900",
            "street": "100 Main Street",
            "locality": "Springfield",
            "region": "IL",
            "postal_code": "62704",
            "country": "United States",
            "types": ["WORK"],
        }
    ],
    "url": "https://alice.example.com/",
    "note": "Loves hiking, climbing; and kayaking",
    "bday": "1985-04-12",
    "categories": ["Work", "Friends", "VIP"],
    "raw": {"REV": ["2026-01-02T03:04:05Z"], "X-SOCIAL": ["alicew"]},
}

LISI = {
    "index": 2,
    "version": "2.1",
    "fn": "李四",
    "n": {
        "family": "李",
        "given": "四",
        "additional": "",
        "prefix": "",
        "suffix": "",
    },
    "nickname": None,
    "org": {"name": "Beijing Tech Co, Ltd.", "units": ["Mobile Division"]},
    "title": None,
    "tel": [
        {"value": "+8613800138000", "types": ["CELL", "PREF"]},
        {"value": "+861058887777", "types": ["WORK"]},
    ],
    "email": [{"value": "lisi@example.cn", "types": ["INTERNET"]}],
    "adr": [
        {
            "pobox": "",
            "ext": "",
            "street": "2 Haidian Street",
            "locality": "Beijing",
            "region": "Beijing",
            "postal_code": "100080",
            "country": "China",
            "types": ["WORK"],
        }
    ],
    "url": "http://lisi.example.cn/",
    "note": None,
    "bday": "19700101",
    "categories": [],
    "raw": {},
}

WANG = {
    "index": 3,
    "version": "2.1",
    "fn": None,
    "n": {
        "family": "王",
        "given": "小明",
        "additional": "",
        "prefix": "",
        "suffix": "",
    },
    "nickname": None,
    "org": None,
    "title": None,
    "tel": [{"value": "13800138000", "types": ["CELL"]}],
    "email": [],
    "adr": [],
    "url": None,
    "note": None,
    "bday": None,
    "categories": [],
    "raw": {},
}

BOB = {
    "index": 4,
    "version": "4.0",
    "fn": "Bob Chen",
    "n": {
        "family": "Chen",
        "given": "Bob",
        "additional": "",
        "prefix": "",
        "suffix": "",
    },
    "nickname": None,
    "org": None,
    "title": None,
    "tel": [
        {"value": "+1-202-555-0144", "types": ["CELL", "PREF"]},
        {"value": "+1-202-555-0177", "types": ["CELL", "WORK"]},
    ],
    "email": [{"value": "bob@example.org", "types": ["WORK"]}],
    "adr": [],
    "url": None,
    "note": None,
    "bday": None,
    "categories": ["community"],
    "raw": {},
}

MAIN_CONTACTS = [ALICE, LISI, WANG, BOB]

# 王小明 encoded as UTF-8 quoted-printable, split across a soft break.
WANG_XIAOMING_QP = "王小明"

MINIMAL_CARD = "BEGIN:VCARD\nFN:C{}\nEND:VCARD\n"


class VcfToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib VcfTool."""

    def setUp(self) -> None:
        self.tool = VcfTool()

    def assert_content_error(self, result: dict, error_type: str) -> None:
        """Assert a structured content error payload with its type."""
        self.assertEqual(set(result), {"mode", "error"})
        self.assertEqual(result["error"]["type"], error_type)
        self.assertTrue(result["error"]["message"])

    # ------------------------------------------------------------------ #
    # parse mode — full ground truth
    # ------------------------------------------------------------------ #

    def test_parse_main_fixture_ground_truth(self) -> None:
        result = self.tool.execute(mode="parse", text=MAIN_VCARD)
        self.assertEqual(
            result,
            {"mode": "parse", "count": 4, "contacts": MAIN_CONTACTS},
        )

    def test_parse_is_deterministic(self) -> None:
        first = self.tool.execute(mode="parse", text=MAIN_VCARD)
        second = self.tool.execute(mode="parse", text=MAIN_VCARD)
        self.assertEqual(first, second)

    def test_parse_crlf_line_endings(self) -> None:
        result = self.tool.execute(
            mode="parse", text=MAIN_VCARD.replace("\n", "\r\n")
        )
        self.assertEqual(
            result,
            {"mode": "parse", "count": 4, "contacts": MAIN_CONTACTS},
        )

    def test_parse_lowercase_begin_end_markers(self) -> None:
        result = self.tool.execute(
            mode="parse", text="begin:vcard\nfn:Zed\nend:vcard\n"
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["contacts"][0]["fn"], "Zed")

    def test_parse_value_escapes(self) -> None:
        card = (
            "BEGIN:VCARD\n"
            "FN:Comma\\, Semi\\; New\\nline Back\\\\slash\n"
            "END:VCARD\n"
        )
        result = self.tool.execute(mode="parse", text=card)
        self.assertEqual(
            result["contacts"][0]["fn"],
            "Comma, Semi; New\nline Back\\slash",
        )

    def test_parse_n_component_escapes(self) -> None:
        card = "BEGIN:VCARD\nN:last\\, name;first\\;name;;;\nEND:VCARD\n"
        result = self.tool.execute(mode="parse", text=card)
        self.assertEqual(
            result["contacts"][0]["n"],
            {
                "family": "last, name",
                "given": "first;name",
                "additional": "",
                "prefix": "",
                "suffix": "",
            },
        )

    def test_parse_quoted_printable_plain_cjk(self) -> None:
        # 李四 → UTF-8 E6 9D 8E E5 9B 9B, declared with the ENCODING= form.
        card = (
            "BEGIN:VCARD\n"
            "VERSION:2.1\n"
            "FN;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:=E6=9D=8E=E5=9B=9B\n"
            "END:VCARD\n"
        )
        result = self.tool.execute(mode="parse", text=card)
        self.assertEqual(result["contacts"][0]["fn"], "李四")

    def test_parse_quoted_printable_soft_break_cjk(self) -> None:
        # 王小明 with a soft line break after 王 (E7 8E 8B).
        card = (
            "BEGIN:VCARD\n"
            "VERSION:2.1\n"
            "FN;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:=E7=8E=8B=\n"
            "=E5=B0=8F=E6=98=8E\n"
            "END:VCARD\n"
        )
        result = self.tool.execute(mode="parse", text=card)
        self.assertEqual(result["contacts"][0]["fn"], WANG_XIAOMING_QP)

    def test_parse_quoted_printable_bare_2_1_param(self) -> None:
        # 2.1 exports often use a bare QUOTED-PRINTABLE token.
        card = (
            "BEGIN:VCARD\n"
            "VERSION:2.1\n"
            "FN;QUOTED-PRINTABLE;CHARSET=UTF-8:=E6=9D=8E=E5=9B=9B\n"
            "END:VCARD\n"
        )
        result = self.tool.execute(mode="parse", text=card)
        self.assertEqual(result["contacts"][0]["fn"], "李四")

    def test_parse_scalar_first_occurrence_wins(self) -> None:
        card = (
            "BEGIN:VCARD\n"
            "VERSION:3.0\nVERSION:4.0\n"
            "FN:First\nFN:Second\n"
            "END:VCARD\n"
        )
        result = self.tool.execute(mode="parse", text=card)
        contact = result["contacts"][0]
        self.assertEqual(contact["fn"], "First")
        self.assertEqual(contact["version"], "3.0")

    def test_parse_categories_accumulate_across_properties(self) -> None:
        card = "BEGIN:VCARD\nCATEGORIES:a,b\nCATEGORIES:c\nEND:VCARD\n"
        result = self.tool.execute(mode="parse", text=card)
        self.assertEqual(result["contacts"][0]["categories"], ["a", "b", "c"])

    def test_parse_unsupported_properties_kept_in_raw(self) -> None:
        card = (
            "BEGIN:VCARD\n"
            "PHOTO:https://example.com/me.png\n"
            "X-CUSTOM:one\nX-CUSTOM:two\n"
            "END:VCARD\n"
        )
        result = self.tool.execute(mode="parse", text=card)
        self.assertEqual(
            result["contacts"][0]["raw"],
            {
                "PHOTO": ["https://example.com/me.png"],
                "X-CUSTOM": ["one", "two"],
            },
        )

    # ------------------------------------------------------------------ #
    # summary mode
    # ------------------------------------------------------------------ #

    def test_summary_ground_truth(self) -> None:
        result = self.tool.execute(mode="summary", text=MAIN_VCARD)
        self.assertEqual(
            result,
            {
                "mode": "summary",
                "count": 4,
                "missing_fn_count": 1,
                "contacts": [
                    {
                        "index": 1,
                        "fn": "Dr. Alice Wang",
                        "phones": 3,
                        "emails": 2,
                        "missing_fn": False,
                    },
                    {
                        "index": 2,
                        "fn": "李四",
                        "phones": 2,
                        "emails": 1,
                        "missing_fn": False,
                    },
                    {
                        "index": 3,
                        "fn": None,
                        "phones": 1,
                        "emails": 0,
                        "missing_fn": True,
                    },
                    {
                        "index": 4,
                        "fn": "Bob Chen",
                        "phones": 2,
                        "emails": 1,
                        "missing_fn": False,
                    },
                ],
            },
        )

    def test_summary_blank_fn_counts_as_missing(self) -> None:
        card = "BEGIN:VCARD\nFN:   \nEND:VCARD\n"
        result = self.tool.execute(mode="summary", text=card)
        self.assertEqual(result["missing_fn_count"], 1)
        self.assertTrue(result["contacts"][0]["missing_fn"])

    # ------------------------------------------------------------------ #
    # filter mode
    # ------------------------------------------------------------------ #

    def test_filter_match_on_fn_email_and_n(self) -> None:
        # "alice" hits the FN, the email local part and the N given name.
        result = self.tool.execute(mode="filter", text=MAIN_VCARD, query="alice")
        self.assertEqual(result["mode"], "filter")
        self.assertEqual(result["query"], "alice")
        self.assertEqual(result["count"], 1)
        self.assertEqual(
            result["contacts"],
            [{**ALICE, "matched_fields": ["fn", "email", "n"]}],
        )

    def test_filter_match_on_email_and_org(self) -> None:
        result = self.tool.execute(mode="filter", text=MAIN_VCARD, query="acme")
        self.assertEqual(result["count"], 1)
        self.assertEqual(
            result["contacts"][0]["matched_fields"], ["email", "org"]
        )

    def test_filter_match_on_n_component_case_insensitive(self) -> None:
        # "WANG" hits the FN, the email domain and the N family name.
        result = self.tool.execute(mode="filter", text=MAIN_VCARD, query="WANG")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["contacts"][0]["index"], 1)
        self.assertEqual(
            result["contacts"][0]["matched_fields"], ["fn", "email", "n"]
        )

    def test_filter_cjk_substring_on_n_and_fn(self) -> None:
        result = self.tool.execute(mode="filter", text=MAIN_VCARD, query="李")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["contacts"][0]["index"], 2)
        self.assertEqual(
            result["contacts"][0]["matched_fields"], ["fn", "n"]
        )

    def test_filter_matches_across_contacts(self) -> None:
        result = self.tool.execute(
            mode="filter", text=MAIN_VCARD, query="example"
        )
        self.assertEqual(
            [contact["index"] for contact in result["contacts"]],
            [1, 2, 4],
        )

    def test_filter_no_match(self) -> None:
        result = self.tool.execute(mode="filter", text=MAIN_VCARD, query="zzz")
        self.assertEqual(
            result,
            {"mode": "filter", "query": "zzz", "count": 0, "contacts": []},
        )

    # ------------------------------------------------------------------ #
    # Content error matrix (structured payloads, not exceptions)
    # ------------------------------------------------------------------ #

    def test_error_end_without_begin(self) -> None:
        result = self.tool.execute(
            mode="parse", text="END:VCARD\nBEGIN:VCARD\nFN:A\nEND:VCARD\n"
        )
        self.assert_content_error(result, "malformed_vcard")

    def test_error_unterminated_card(self) -> None:
        result = self.tool.execute(mode="parse", text="BEGIN:VCARD\nFN:A\n")
        self.assert_content_error(result, "malformed_vcard")

    def test_error_nested_begin(self) -> None:
        result = self.tool.execute(
            mode="parse",
            text="BEGIN:VCARD\nBEGIN:VCARD\nEND:VCARD\nEND:VCARD\n",
        )
        self.assert_content_error(result, "malformed_vcard")

    def test_error_non_vcard_block(self) -> None:
        result = self.tool.execute(
            mode="parse", text="BEGIN:VCALENDAR\nEND:VCALENDAR\n"
        )
        self.assert_content_error(result, "malformed_vcard")

    def test_error_end_marker_mismatch(self) -> None:
        result = self.tool.execute(
            mode="parse", text="BEGIN:VCARD\nEND:ADDRESS\nEND:VCARD\n"
        )
        self.assert_content_error(result, "malformed_vcard")

    def test_error_property_line_without_colon(self) -> None:
        result = self.tool.execute(
            mode="parse", text="BEGIN:VCARD\nGIBBERISH\nEND:VCARD\n"
        )
        self.assert_content_error(result, "malformed_vcard")

    def test_error_invalid_property_name(self) -> None:
        result = self.tool.execute(
            mode="parse", text="BEGIN:VCARD\nBAD NAME:x\nEND:VCARD\n"
        )
        self.assert_content_error(result, "malformed_vcard")

    def test_error_no_vcard_blocks(self) -> None:
        result = self.tool.execute(
            mode="parse", text="just some text\nno cards here\n"
        )
        self.assert_content_error(result, "no_vcard_blocks")

    def test_error_quoted_printable_bad_hex(self) -> None:
        result = self.tool.execute(
            mode="parse",
            text="BEGIN:VCARD\nFN;ENCODING=QUOTED-PRINTABLE:=E6=ZZ\nEND:VCARD\n",
        )
        self.assert_content_error(result, "invalid_quoted_printable")

    def test_error_quoted_printable_not_utf8(self) -> None:
        result = self.tool.execute(
            mode="parse",
            text="BEGIN:VCARD\nFN;ENCODING=QUOTED-PRINTABLE:=FF\nEND:VCARD\n",
        )
        self.assert_content_error(result, "invalid_quoted_printable")

    def test_error_quoted_printable_truncated_sequence(self) -> None:
        # =E6=9D is an incomplete 3-byte UTF-8 sequence.
        result = self.tool.execute(
            mode="parse",
            text="BEGIN:VCARD\nFN;ENCODING=QUOTED-PRINTABLE:=E6=9D\nEND:VCARD\n",
        )
        self.assert_content_error(result, "invalid_quoted_printable")

    def test_error_quoted_printable_dangling_soft_break(self) -> None:
        # The dangling '=' folds the END:VCARD line into the value, so the
        # card is never closed — documented behavior, still an error.
        result = self.tool.execute(
            mode="parse",
            text="BEGIN:VCARD\nFN;ENCODING=QUOTED-PRINTABLE:=E6=\nEND:VCARD\n",
        )
        self.assert_content_error(result, "malformed_vcard")

    def test_error_too_many_contacts(self) -> None:
        text = MINIMAL_CARD.format(1) + MINIMAL_CARD.format(2) + MINIMAL_CARD.format(3)
        capped = VcfTool(max_contacts=2)
        result = capped.execute(mode="parse", text=text)
        self.assert_content_error(result, "too_many_contacts")
        self.assertIn("3 contacts", result["error"]["message"])

    def test_contact_cap_boundary_allows_exact_limit(self) -> None:
        text = MINIMAL_CARD.format(1) + MINIMAL_CARD.format(2) + MINIMAL_CARD.format(3)
        capped = VcfTool(max_contacts=3)
        result = capped.execute(mode="parse", text=text)
        self.assertEqual(result["count"], 3)

    def test_content_error_in_summary_and_filter_modes(self) -> None:
        result = self.tool.execute(mode="summary", text="nothing here")
        self.assert_content_error(result, "no_vcard_blocks")
        result = self.tool.execute(mode="filter", text="nothing here", query="x")
        self.assert_content_error(result, "no_vcard_blocks")

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="vcf", text="BEGIN:VCARD\nEND:VCARD\n")
        self.assert_invalid(mode=None, text="BEGIN:VCARD\nEND:VCARD\n")
        self.assert_invalid(mode=123, text="BEGIN:VCARD\nEND:VCARD\n")
        self.assert_invalid(mode="PARSE", text="BEGIN:VCARD\nEND:VCARD\n")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"BEGIN:VCARD", ["BEGIN:VCARD"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="parse", text=bad)
                self.assert_invalid(mode="summary", text=bad)

    def test_empty_text_rejected(self) -> None:
        self.assert_invalid(mode="parse", text="")
        self.assert_invalid(mode="filter", text="", query="x")

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(mode="parse", text=oversized)
        boundary = self.tool.execute(mode="parse", text="a" * 100_000)
        self.assertEqual(boundary["error"]["type"], "no_vcard_blocks")

    def test_invalid_query(self) -> None:
        self.assert_invalid(mode="filter", text=MAIN_VCARD)
        self.assert_invalid(mode="filter", text=MAIN_VCARD, query="")
        self.assert_invalid(mode="filter", text=MAIN_VCARD, query=None)
        self.assert_invalid(mode="filter", text=MAIN_VCARD, query=123)
        self.assert_invalid(mode="filter", text=MAIN_VCARD, query=True)
        self.assert_invalid(
            mode="filter", text=MAIN_VCARD, query="a" * 257
        )

    def test_query_rejected_outside_filter_mode(self) -> None:
        self.assert_invalid(mode="parse", text=MAIN_VCARD, query="x")
        self.assert_invalid(mode="summary", text=MAIN_VCARD, query="x")

    def test_invalid_caps(self) -> None:
        for kwargs in (
            {"max_contacts": 0},
            {"max_contacts": True},
            {"max_text_chars": -1},
            {"max_query_chars": "5"},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    VcfTool(**kwargs).execute(
                        mode="parse", text=MINIMAL_CARD.format(1)
                    )

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectVcfTool, VcfTool)
        self.assertEqual(self.tool.name, "vcf_tool")
        self.assertIn("vCard", self.tool.description)
        self.assertEqual(self.tool.max_text_chars, 100_000)
        self.assertEqual(self.tool.max_contacts, 1_000)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("VcfTool", __all__)


if __name__ == "__main__":
    unittest.main()
