#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Offline ground-truth tests for XmlLintTool (stdlib-only, no network).

Every expectation in this file was derived by hand from the source
documents (positions counted character-by-character) or, for the
expat mapping matrix, cross-checked against real expat through
``xml.etree.ElementTree.fromstring`` at test time.
"""

import unittest
import xml.etree.ElementTree as ET

import yaml

from agentuniverse.agent.action.tool.common_tool import XmlLintTool
from agentuniverse.agent.action.tool.common_tool.xml_lint_tool import (
    _RULES,
)


CLEAN_DOC = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    "<catalog>\n"
    "  <book>\n"
    "    <title>agentUniverse</title>\n"
    "    <author>Yan</author>\n"
    "  </book>\n"
    "</catalog>\n"
)


def codes(result):
    return [finding["code"] for finding in result["findings"]]


def by_code(result, code):
    matches = [f for f in result["findings"] if f["code"] == code]
    assert matches, f"no {code} in {codes(result)}"
    return matches


class XmlLintToolLintRuleGroundTruthsTest(unittest.TestCase):
    """One focused test per rule, plus the clean control."""

    def setUp(self) -> None:
        self.tool = XmlLintTool()

    # -- control ----------------------------------------------------------

    def test_clean_document_lints_ok(self) -> None:
        result = self.tool.execute(mode="lint", xml_text=CLEAN_DOC)
        self.assertEqual(codes(result), [])
        self.assertTrue(result["ok"])
        self.assertTrue(result["parsed"])
        self.assertEqual(result["finding_count"], 0)
        self.assertFalse(result["findings_truncated"])

    def test_envelope_and_finding_shape(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="<a><b/></a>")
        self.assertEqual(result["mode"], "lint")
        self.assertIn("ok", result)
        self.assertIn("parsed", result)
        self.assertIn("finding_count", result)
        self.assertIn("findings_truncated", result)
        self.assertIn("findings", result)
        for finding in result["findings"]:
            self.assertEqual(
                sorted(finding),
                ["code", "col", "hint", "line", "message", "severity"],
            )
            self.assertIsInstance(finding["line"], int)
            self.assertIsInstance(finding["col"], int)
            self.assertGreaterEqual(finding["line"], 1)
            self.assertGreaterEqual(finding["col"], 1)
            self.assertIn(finding["severity"], ("error", "info"))
            slug, severity, hint = _RULES[finding["code"]]
            self.assertEqual(finding["severity"], severity)
            self.assertEqual(finding["hint"], hint)

    # -- XML001 syntax_error ------------------------------------------------

    def test_syntax_error_carries_expat_position_and_message(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="<a><b></a>")
        finding = by_code(result, "XML001")[0]
        self.assertEqual(finding["line"], 1)
        self.assertEqual(finding["col"], 9)  # expat 0-based 8 + 1
        self.assertEqual(finding["message"], "mismatched tag")
        self.assertFalse(result["ok"])

    def test_multiline_syntax_error_position(self) -> None:
        text = "<a>\n  <b>\n    <c>\n  </b>\n</a>"
        result = self.tool.execute(mode="lint", xml_text=text)
        finding = by_code(result, "XML001")[0]
        self.assertEqual(finding["line"], 4)
        self.assertEqual(finding["col"], 5)
        self.assertEqual(finding["message"], "mismatched tag")

    def test_junk_after_document_element(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="<a/><b/>")
        finding = by_code(result, "XML001")[0]
        self.assertEqual((finding["line"], finding["col"]), (1, 5))
        self.assertEqual(finding["message"], "junk after document element")

    def test_structure_rules_skipped_when_parse_fails(self) -> None:
        # duplicate attrs keep the parse alive failure; this doc both
        # fails parsing and would otherwise fire empty_element
        result = self.tool.execute(mode="lint", xml_text="<a><b>")
        self.assertEqual(codes(result), ["XML001"])

    # -- XML002 dtd_or_entity (XXE guard) -----------------------------------

    def test_doctype_is_a_hard_security_error(self) -> None:
        text = (
            "<!DOCTYPE foo [\n"
            "  <!ENTITY xxe SYSTEM \"file:///etc/passwd\">\n"
            "]>\n"
            "<foo>&xxe;</foo>"
        )
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertFalse(result["ok"])
        self.assertFalse(result["parsed"])
        finding = by_code(result, "XML002")[0]
        self.assertEqual(finding["line"], 1)
        self.assertEqual(finding["col"], 1)
        self.assertIn("XXE", finding["message"])

    def test_billion_laughs_shape_rejected_before_parsing(self) -> None:
        text = (
            "<!DOCTYPE lolz [\n"
            "  <!ENTITY lol \"lol\">\n"
            "  <!ENTITY lol2 \"&lol;&lol;&lol;&lol;&lol;\">\n"
            "]>\n"
            "<lolz>&lol2;</lolz>"
        )
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertEqual(codes(result), ["XML002"])
        self.assertFalse(result["parsed"])

    def test_entity_marker_in_comment_still_rejected(self) -> None:
        result = self.tool.execute(
            mode="lint", xml_text="<!-- <!ENTITY e 'x'> --><a/>"
        )
        finding = by_code(result, "XML002")[0]
        # '<!-- ' is 5 characters: the marker starts at column 6
        self.assertEqual((finding["line"], finding["col"]), (1, 6))

    def test_doctype_marker_in_cdata_still_rejected(self) -> None:
        result = self.tool.execute(
            mode="lint", xml_text="<a><![CDATA[<!DOCTYPE x>]]></a>"
        )
        finding = by_code(result, "XML002")[0]
        # '<a><![CDATA[' is 12 characters: marker at column 13
        self.assertEqual((finding["line"], finding["col"]), (1, 13))

    def test_parameter_entity_marker_rejected(self) -> None:
        text = "<!DOCTYPE a [<!ENTITY % pe \"x\">]><a/>"
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertIn("XML002", codes(result))

    def test_lowercase_doctype_is_syntax_not_guard(self) -> None:
        # only the exact spellings <!DOCTYPE / <!ENTITY are guard hits
        result = self.tool.execute(mode="lint", xml_text="<!doctype a><a/>")
        self.assertEqual(codes(result), ["XML001"])
        self.assertNotIn("XML002", codes(result))

    def test_guard_location_across_lines(self) -> None:
        text = "<a>\n  <b/>\n</a>\n<!DOCTYPE x>"
        result = self.tool.execute(mode="lint", xml_text=text)
        finding = by_code(result, "XML002")[0]
        self.assertEqual(finding["line"], 4)
        self.assertEqual(finding["col"], 1)

    def test_disabling_xml002_keeps_the_document_unparsed(self) -> None:
        result = self.tool.execute(
            mode="lint", xml_text="<!DOCTYPE a><a/>", rules={"XML002": False}
        )
        self.assertEqual(result["findings"], [])
        # security policy: the DTD document is never parsed, even
        # with the rule suppressed — no structure findings appear
        self.assertFalse(result["parsed"])

    def test_raw_line_rules_still_run_behind_the_guard(self) -> None:
        text = "<!DOCTYPE a><a>" + "x" * 5001 + "</a>"
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertEqual(codes(result), ["XML002", "XML008"])

    # -- XML003 undeclared_entity -------------------------------------------

    def test_undeclared_entity_in_text(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="<a>&foo;</a>")
        finding = by_code(result, "XML003")[0]
        self.assertEqual(finding["line"], 1)
        self.assertEqual(finding["col"], 4)  # the '&'
        self.assertIn("&foo;", finding["message"])
        self.assertFalse(result["ok"])

    def test_undeclared_entity_in_attribute_reports_generic_message(
        self,
    ) -> None:
        # expat reports column 0 (1-based col 1) for attribute values;
        # no name can be extracted there — the message stays generic
        result = self.tool.execute(mode="lint", xml_text='<a x="&foo;"/>')
        finding = by_code(result, "XML003")[0]
        self.assertEqual((finding["line"], finding["col"]), (1, 1))
        self.assertEqual(finding["message"], "undefined entity")

    def test_predefined_entities_are_fine(self) -> None:
        text = "<a>&amp;&lt;&gt;&apos;&quot;&#65;&#x42;</a>"
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertEqual(codes(result), [])

    def test_entity_in_cdata_is_literal_text_not_a_reference(self) -> None:
        result = self.tool.execute(
            mode="lint", xml_text="<a><![CDATA[&foo;]]></a>"
        )
        # the CDATA content becomes ordinary text: no entity finding,
        # and <a> is not empty because it carries that text
        self.assertEqual(codes(result), [])

    # -- XML004 duplicate_attribute ------------------------------------------

    def test_duplicate_attribute_with_name_extraction(self) -> None:
        result = self.tool.execute(mode="lint", xml_text='<a x="1" x="2"/>')
        finding = by_code(result, "XML004")[0]
        self.assertEqual(finding["line"], 1)
        self.assertEqual(finding["col"], 10)  # expat 0-based 9 + 1
        self.assertEqual(finding["message"], "duplicate attribute 'x'")

    def test_duplicate_namespaced_attribute(self) -> None:
        text = '<a p:x="1" p:x="2" xmlns:p="urn:p"/>'
        result = self.tool.execute(mode="lint", xml_text=text)
        finding = by_code(result, "XML004")[0]
        self.assertEqual(finding["col"], 12)
        self.assertEqual(finding["message"], "duplicate attribute 'p:x'")

    # -- XML005 root_missing ---------------------------------------------------

    def test_empty_document(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="")
        finding = by_code(result, "XML005")[0]
        self.assertEqual((finding["line"], finding["col"]), (1, 1))
        self.assertFalse(result["ok"])
        self.assertFalse(result["parsed"])

    def test_whitespace_only_document(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="  \n\t \n")
        self.assertEqual(codes(result), ["XML005"])

    # -- XML006 pi_or_comment_only --------------------------------------------

    def test_comment_only_document(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="<!-- hello -->")
        finding = by_code(result, "XML006")[0]
        self.assertEqual((finding["line"], finding["col"]), (1, 1))

    def test_pi_only_document(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="<?pi data?>")
        self.assertEqual(codes(result), ["XML006"])

    def test_comment_and_pi_only_document(self) -> None:
        result = self.tool.execute(
            mode="lint", xml_text="<!-- c -->\n<?pi d?>\n"
        )
        self.assertEqual(codes(result), ["XML006"])

    def test_whitespace_then_comment_only(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="  \n <!-- c -->")
        self.assertEqual(codes(result), ["XML006"])

    def test_comment_after_root_is_legal(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="<a/><!-- ok -->")
        self.assertEqual(codes(result), ["XML010"])

    # -- XML007 bom -------------------------------------------------------------

    def test_bom_is_info_and_positions_shift(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="\ufeff<a><b/></a>")
        bom = by_code(result, "XML007")[0]
        self.assertEqual((bom["line"], bom["col"]), (1, 1))
        self.assertEqual(bom["severity"], "info")
        # empty-element position refers to the post-BOM text: <b/> at
        # line 1 column 4 (expat 0-based column 3)
        empty = by_code(result, "XML010")[0]
        self.assertEqual((empty["line"], empty["col"]), (1, 4))
        # info-only findings keep the document ok
        self.assertTrue(result["ok"])
        self.assertTrue(result["parsed"])

    def test_no_bom_no_finding(self) -> None:
        result = self.tool.execute(mode="lint", xml_text="<a/>")
        self.assertNotIn("XML007", codes(result))

    # -- XML008 very_long_line ----------------------------------------------------

    def test_line_over_threshold(self) -> None:
        text = "<a>\n" + "x" * 5001 + "\n</a>"
        result = self.tool.execute(mode="lint", xml_text=text)
        finding = by_code(result, "XML008")[0]
        self.assertEqual(finding["line"], 2)
        self.assertEqual(finding["col"], 5001)
        self.assertIn("5,001", finding["message"])
        self.assertTrue(result["ok"])  # info only

    def test_line_at_threshold_is_clean(self) -> None:
        text = "<a>\n" + "x" * 5000 + "\n</a>"
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertNotIn("XML008", codes(result))

    def test_multiple_long_lines_each_reported(self) -> None:
        text = "<a>\n" + ("y" * 5002 + "\n") * 3 + "</a>"
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertEqual(len(by_code(result, "XML008")), 3)

    # -- XML009 non_utf8_declared ---------------------------------------------------

    def test_foreign_encoding_with_non_ascii_content(self) -> None:
        text = '<?xml version="1.0" encoding="ISO-8859-1"?><a>\u4f60\u597d</a>'
        result = self.tool.execute(mode="lint", xml_text=text)
        finding = by_code(result, "XML009")[0]
        # the declared value starts after 'encoding="' (column 31)
        self.assertEqual((finding["line"], finding["col"]), (1, 31))
        self.assertIn("ISO-8859-1", finding["message"])
        self.assertTrue(result["ok"])

    def test_foreign_encoding_with_ascii_only_content_is_clean(self) -> None:
        text = '<?xml version="1.0" encoding="ISO-8859-1"?><a>hello</a>'
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertNotIn("XML009", codes(result))

    def test_utf8_label_variants_are_clean(self) -> None:
        for label in ("UTF-8", "utf-8", "utf8", "UTF8"):
            text = (
                f'<?xml version="1.0" encoding="{label}"?>'
                f"<a>\u4f60\u597d</a>"
            )
            result = self.tool.execute(mode="lint", xml_text=text)
            self.assertNotIn("XML009", codes(result))

    def test_encoding_mention_outside_declaration_ignored(self) -> None:
        # the declaration regex is anchored at offset 0
        text = "<a encoding='ISO-8859-1'>\u4f60\u597d</a>"
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertNotIn("XML009", codes(result))

    def test_stylesheet_pi_is_not_a_declaration(self) -> None:
        # a PI whose target merely starts with 'xml' is not an XML
        # declaration: its encoding text must not fire XML009 even
        # with non-ASCII content
        text = (
            '<?xml-stylesheet type="text/xsl" encoding="ISO-8859-1"?>'
            "<r>h\u00e9llo w\u00f6rld</r>"
        )
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertNotIn("XML009", codes(result))
        self.assertTrue(result["ok"])

    # -- XML010 empty_element ---------------------------------------------------------

    def test_empty_element_with_and_without_whitespace_text(self) -> None:
        text = "<r><a/><b>   </b><c>word</c><d><e/></d></r>"
        result = self.tool.execute(mode="lint", xml_text=text)
        findings = by_code(result, "XML010")
        self.assertEqual([f["col"] for f in findings], [4, 8, 32])
        self.assertIn("whitespace-only text", findings[1]["message"])
        self.assertNotIn("whitespace-only", findings[0]["message"])
        # <c> has text, <d> has a child — neither fires
        self.assertTrue(result["ok"])

    def test_attributes_do_not_make_an_element_non_empty(self) -> None:
        result = self.tool.execute(
            mode="lint", xml_text='<r><a x="1" y="2"/></r>'
        )
        self.assertEqual(len(by_code(result, "XML010")), 1)

    def test_comment_or_pi_children_do_not_make_an_element_non_empty(
        self,
    ) -> None:
        # the trigger is "no child elements and no text beyond
        # whitespace" — comments and PIs are neither
        result = self.tool.execute(
            mode="lint", xml_text="<r><a><!-- c --></a><b><?pi d?></b></r>"
        )
        findings = by_code(result, "XML010")
        # <r> col 1, <a> col 4, <b> col 21 (after </a> ends at col 20)
        self.assertEqual([f["col"] for f in findings], [4, 21])

    # -- XML011 mixed_content_element ------------------------------------------------------

    def test_mixed_content_variants(self) -> None:
        text = (
            "<r>"
            "<a>lead<b/></a>"          # leading text
            "<c><b/>tail</c>"          # child tail
            "<d>   <b/></d>"           # whitespace only: clean
            "<e>text</e>"              # no children: clean
            "</r>"
        )
        result = self.tool.execute(mode="lint", xml_text=text)
        findings = by_code(result, "XML011")
        # <a> at column 4; <c> at column 19 (after 3+4+4+4=15 chars
        # of <a>lead<b/></a> plus the 3 of <r>)
        self.assertEqual([f["col"] for f in findings], [4, 19])
        self.assertEqual(findings[0]["line"], 1)

    def test_cdata_counts_as_text_for_mixed_content(self) -> None:
        result = self.tool.execute(
            mode="lint", xml_text="<a>x<![CDATA[y]]>z<b/></a>"
        )
        self.assertEqual(len(by_code(result, "XML011")), 1)

    def test_text_around_a_comment_is_not_mixed_content(self) -> None:
        # the trigger requires child ELEMENTS mixed with text; a
        # comment child plus text is not mixed content
        result = self.tool.execute(
            mode="lint", xml_text="<a>x<!-- c --></a>"
        )
        self.assertNotIn("XML011", codes(result))

    # -- XML012 deeply_nested -------------------------------------------------------------

    def test_deep_nesting_fires_once_with_path(self) -> None:
        text = "".join(f"<l{i}>" for i in range(14)) + "leaf"
        text += "".join(f"</l{i}>" for i in reversed(range(14)))
        result = self.tool.execute(mode="lint", xml_text=text)
        findings = by_code(result, "XML012")
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding["line"], 1)
        # first offender is l12 (depth 13 > 12): 12 tags precede it
        # (l0..l11 = 10*4 + 2*5 = 50 characters), so '<l12>' is at
        # column 51
        self.assertEqual(finding["col"], 51)
        self.assertIn("13 levels", finding["message"])
        self.assertIn("l0/l1/l2/l3/l4/l5/l6/l7/l8/l9/l10/l11/l12",
                      finding["message"])

    def test_depth_twelve_is_clean(self) -> None:
        text = "".join(f"<l{i}>" for i in range(12)) + "leaf"
        text += "".join(f"</l{i}>" for i in reversed(range(12)))
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertNotIn("XML012", codes(result))

    def test_max_depth_option_gates_the_rule(self) -> None:
        text = "<a><b><c><d/></c></b></a>"  # depth 4
        strict = self.tool.execute(mode="lint", xml_text=text, max_depth=3)
        relaxed = self.tool.execute(mode="lint", xml_text=text, max_depth=4)
        self.assertIn("XML012", codes(strict))
        self.assertNotIn("XML012", codes(relaxed))

    # -- XML013 namespace_heavy ------------------------------------------------------------

    def test_namespace_heavy_fires_at_the_crossing_element(self) -> None:
        decls = " ".join(
            f'xmlns:n{i}="urn:{i}" n{i}:a="v"' for i in range(11)
        )
        text = f"<r {decls}><n0:k n10:b='x'/></r>"
        result = self.tool.execute(mode="lint", xml_text=text)
        findings = by_code(result, "XML013")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["line"], 1)
        self.assertEqual(findings[0]["col"], 1)  # <r> crosses the limit
        self.assertIn("past 10 distinct namespaces", findings[0]["message"])

    def test_ten_namespaces_are_clean_eleven_fire(self) -> None:
        def build(count: int) -> str:
            # namespaces count when USED: one namespaced element per
            # distinct URI (xmlns declarations alone are invisible to
            # ElementTree and do not count)
            inner = "".join(
                f'<n{i}:k xmlns:n{i}="urn:{i}"/>' for i in range(count)
            )
            return f"<r>{inner}</r>"

        self.assertNotIn(
            "XML013", codes(self.tool.execute(mode="lint",
                                              xml_text=build(10)))
        )
        result = self.tool.execute(mode="lint", xml_text=build(11))
        self.assertIn("XML013", codes(result))

    def test_default_namespace_and_attribute_namespaces_count(self) -> None:
        # 11 distinct URIs: 1 default + 10 prefixed on elements/attrs
        parts = ['xmlns="urn:default"']
        for i in range(10):
            parts.append(f'xmlns:p{i}="urn:{i}"')
        text = "<r " + " ".join(parts) + ">" + "".join(
            f'<p{i}:k p{i}:a="1" xmlns:p{i}="urn:{i}"/>' for i in range(10)
        ) + "</r>"
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertIn("XML013", codes(result))


class XmlLintToolExpatMappingMatrixTest(unittest.TestCase):
    """30 malformed documents, differentially checked against expat.

        For every document the test first re-derives the reference
        position from ``ET.fromstring`` itself, then asserts the
        tool's finding matches expat's own line and 0-based column
        + 1 — the mapping claim is verified, not trusted. XML001
        cases also carry expat's message verbatim; XML003/XML004
        keep expat's position and add the documented name detail;
        XML005/XML006 are document-level and report (1, 1) instead
        of expat's stream-end pointer.
    """

    def setUp(self) -> None:
        self.tool = XmlLintTool()

    # (name, document, expected rule, expected message or None)
    MATRIX = [
        ("mismatched", "<a><b></a>", "XML001", None),
        ("unclosed_element", "<a><b>text", "XML001", None),
        ("bare_lt_in_text", "<a>1 < 2</a>", "XML001", None),
        ("invalid_char_ref", "<a>&#xFFFF;</a>", "XML001", None),
        ("invalid_hex_ref", "<a>&#xZZ;</a>", "XML001", None),
        ("bare_ampersand", "<a>AT&T</a>", "XML001", None),
        ("undefined_entity_text", "<a>&foo;</a>", "XML003",
         "undefined entity &foo; — only the five predefined entities "
         "and character references are available (DTDs are rejected "
         "before parsing)"),
        ("undefined_entity_attr", '<a x="&foo;"/>', "XML003",
         "undefined entity"),
        ("multiple_roots", "<a/><b/>", "XML001", None),
        ("trailing_junk", "<a/>junk", "XML001", None),
        ("empty_document", "", "XML005",
         "no root element: the document is empty or whitespace-only "
         "(expat: no element found)"),
        ("whitespace_only", "   \n  ", "XML005",
         "no root element: the document is empty or whitespace-only "
         "(expat: no element found)"),
        ("comment_only", "<!-- hello -->", "XML006",
         "no root element: the document contains only comments "
         "and/or processing instructions (expat: no element found)"),
        ("pi_only", "<?pi data?>", "XML006",
         "no root element: the document contains only comments "
         "and/or processing instructions (expat: no element found)"),
        ("comment_pi_only", "<!-- c -->\n<?pi d?>", "XML006",
         "no root element: the document contains only comments "
         "and/or processing instructions (expat: no element found)"),
        ("duplicate_attribute", '<a x="1" x="2"/>', "XML004",
         "duplicate attribute 'x'"),
        ("bad_element_name", "<1a/>", "XML001", None),
        ("unclosed_token", "<a", "XML001", None),
        ("attr_unquoted", "<a x=1/>", "XML001", None),
        ("attr_without_value", "<a x/>", "XML001", None),
        ("nested_mismatch", "<a><b><c></b></c></a>", "XML001", None),
        ("unclosed_cdata", "<a><![CDATA[unclosed</a>", "XML001", None),
        ("decl_not_first", '<a/><?xml version="1.0"?>', "XML001", None),
        ("text_before_root", "text<a/>", "XML001", None),
        ("char_ref_missing_semi", "<a>&#38</a>", "XML001", None),
        ("empty_tag_name", "</>", "XML001", None),
        ("unterminated_comment", "<!-- bad", "XML001", None),
        ("cdata_end_sequence", "<a>]]></a>", "XML001", None),
        ("lt_inside_attr", '<a x="a<b"/>', "XML001", None),
        ("multiline_mismatch", "<a>\n  <b>\n    <c>\n  </b>\n</a>",
         "XML001", None),
    ]

    def test_matrix_matches_real_expat(self) -> None:
        self.assertEqual(len(self.MATRIX), 30)
        for name, document, expected_code, expected_message in (
            self.MATRIX
        ):
            with self.subTest(case=name):
                reference = self._reference(document)
                result = self.tool.execute(mode="lint", xml_text=document)
                self.assertEqual(
                    codes(result), [expected_code],
                    f"{name}: expat said {reference}",
                )
                finding = result["findings"][0]
                if expected_code in ("XML005", "XML006"):
                    # document-level findings: line 1, col 1
                    self.assertEqual(
                        (finding["line"], finding["col"]), (1, 1)
                    )
                else:
                    self.assertEqual(
                        finding["line"], reference["line"],
                        f"{name}: line mismatch",
                    )
                    self.assertEqual(
                        finding["col"], reference["col"],
                        f"{name}: column mismatch",
                    )
                if expected_message is None:
                    self.assertEqual(
                        finding["message"], reference["message"],
                        f"{name}: message mismatch",
                    )
                else:
                    self.assertEqual(finding["message"], expected_message)
                self.assertFalse(result["parsed"])

    @staticmethod
    def _reference(document: str) -> dict:
        """The tool-independent expat expectation for one document."""
        try:
            ET.fromstring(document.encode("utf-8"))
        except ET.ParseError as exc:
            position = exc.position
            return {
                "line": position[0] or 1,
                "col": (position[1] or 0) + 1,
                "message": (exc.msg or str(exc)).rsplit(": line ", 1)[0],
                "code": exc.code,
            }
        raise AssertionError("matrix document unexpectedly parsed")

    def test_every_matrix_document_actually_fails_expat(self) -> None:
        # the differential is honest: every entry really is malformed
        for name, document, _code, _message in self.MATRIX:
            with self.subTest(case=name):
                self.assertIsNotNone(self._reference(document))

    def test_root_level_mappings_report_document_position(self) -> None:
        # XML005 / XML006 are document-level: line 1, col 1 regardless
        # of where expat's stream-end pointer landed
        for document, code in (("", "XML005"),
                               ("<!-- x -->", "XML006")):
            result = self.tool.execute(mode="lint", xml_text=document)
            finding = result["findings"][0]
            self.assertEqual((finding["line"], finding["col"]), (1, 1))


class XmlLintToolProfileTest(unittest.TestCase):
    """Profile mode against hand-computed topology statistics."""

    def setUp(self) -> None:
        self.tool = XmlLintTool()

    PROFILE_DOC = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<catalog count="3">\n'
        '  <book id="1">\n'
        "    <title>Python</title>\n"
        "    <author>Yan</author>\n"
        "  </book>\n"
        '  <book id="2">\n'
        "    <title>XML</title>\n"
        "  </book>\n"
        '  <magazine id="3"/>\n'
        "</catalog>"
    )

    def test_profile_ground_truth(self) -> None:
        result = self.tool.execute(mode="profile",
                                   xml_text=self.PROFILE_DOC)
        self.assertEqual(result["mode"], "profile")
        self.assertEqual(result["root_tag"], "catalog")
        # catalog, book x2, title x2, author, magazine
        self.assertEqual(result["element_count"], 7)
        self.assertEqual(result["max_depth"], 3)
        self.assertEqual(result["deepest_path"], "catalog/book/title")
        # first deepest element: <title> on line 4, column 5
        self.assertEqual(result["deepest_element"]["tag"], "title")
        self.assertEqual(result["deepest_element"]["line"], 4)
        self.assertEqual(result["deepest_element"]["col"], 5)
        self.assertEqual(
            result["top_tags"],
            [
                # ties break by tag ascending: book before title
                {"tag": "book", "count": 2},
                {"tag": "title", "count": 2},
                {"tag": "author", "count": 1},
                {"tag": "catalog", "count": 1},
                {"tag": "magazine", "count": 1},
            ],
        )
        # count attr + 3 id attrs
        self.assertEqual(result["attribute_count"], 4)
        # text nodes: catalog.text, book.text x2, title.text x2,
        # title.tail x2, author.text, author.tail, book.tail x2,
        # magazine.tail -> 12 non-empty nodes, 43 characters (three
        # '\n  ' lead-ins, three '\n  ' tails, two '\n    ' book
        # bodies and title tails, 'Python', 'Yan', 'XML', final '\n'),
        # the longest being 'Python' (6)
        self.assertEqual(result["text_node_count"], 12)
        self.assertEqual(result["text_length_total"], 43)
        self.assertEqual(result["text_length_max"], 6)
        self.assertEqual(result["namespaces"], [])
        self.assertEqual(result["namespace_count"], 0)
        self.assertEqual(result["pi_count"], 0)
        self.assertEqual(result["comment_count"], 0)

    def test_profile_counts_comments_pis_and_namespaces(self) -> None:
        text = (
            '<?xml version="1.0"?>\n'
            "<root xmlns:p=\"urn:p\" xmlns=\"urn:d\">\n"
            "  <!-- first -->\n"
            "  <?target data?>\n"
            "  <p:kid p:attr='1'/>\n"
            "  <!-- second -->\n"
            "  <plain/>\n"
            "</root>"
        )
        result = self.tool.execute(mode="profile", xml_text=text)
        self.assertEqual(result["comment_count"], 2)
        self.assertEqual(result["pi_count"], 1)  # declaration is not a PI
        self.assertEqual(result["namespace_count"], 2)
        self.assertEqual(result["namespaces"], ["urn:d", "urn:p"])
        self.assertEqual(result["element_count"], 3)
        # text nodes: root.text plus the five whitespace tails after
        # the comment, PI, kid and second comment -> 6 nodes / 16
        # characters, the longest whitespace tail being 3
        self.assertEqual(result["text_node_count"], 6)
        self.assertEqual(result["text_length_total"], 16)
        self.assertEqual(result["text_length_max"], 3)

    def test_profile_cjk_text_length(self) -> None:
        text = "<r><a>\u667a\u80fd\u4f53\u5b87\u5b99</a><b/>\r</r>"
        result = self.tool.execute(mode="profile", xml_text=text)
        # five CJK characters in <a>, '\r' as the <b/> tail
        self.assertEqual(result["text_length_max"], 5)
        self.assertEqual(result["text_length_total"], 6)
        self.assertEqual(result["text_node_count"], 2)

    def test_profile_bom_document(self) -> None:
        result = self.tool.execute(mode="profile", xml_text="\ufeff<a/>")
        self.assertEqual(result["element_count"], 1)

    def test_profile_counts_document_level_comments_and_pis(self) -> None:
        # comments and PIs outside the root element are dropped by a
        # tree parse; the raw-expat pass counts them document-wide
        text = "<!-- lead --><?pi d?><r><!-- in --></r><!-- trail -->"
        result = self.tool.execute(mode="profile", xml_text=text)
        self.assertEqual(result["comment_count"], 3)
        self.assertEqual(result["pi_count"], 1)

    def test_profile_does_not_count_the_declaration_as_a_pi(self) -> None:
        result = self.tool.execute(
            mode="profile", xml_text="<?xml version='1.0'?><r/><?pi?>"
        )
        self.assertEqual(result["pi_count"], 1)

    def test_profile_deep_document_does_not_recursion_overflow(self) -> None:
        depth = 5000
        text = "<a>" * depth + "</a>" * depth
        result = self.tool.execute(mode="profile", xml_text=text)
        self.assertEqual(result["max_depth"], depth)
        self.assertTrue(result["deepest_path"].startswith("a/a/a/a/a/a"))
        # the path is capped at 100 characters for display
        self.assertEqual(len(result["deepest_path"]), 100)
        self.assertTrue(result["deepest_path"].endswith("..."))
        self.assertEqual(result["element_count"], depth)

    def test_profile_top_tags_tie_break_and_cap(self) -> None:
        parts = "".join(f"<t{i}/>" for i in range(15))
        text = f"<r>{parts}<dup/><dup/><dup/></r>"
        result = self.tool.execute(mode="profile", xml_text=text)
        top = result["top_tags"]
        self.assertEqual(len(top), 10)
        self.assertEqual(top[0], {"tag": "dup", "count": 3})
        self.assertEqual(top[1], {"tag": "r", "count": 1})
        self.assertEqual(top[2], {"tag": "t0", "count": 1})
        # string ordering among ties: t10 sorts before t2
        self.assertEqual(top[9], {"tag": "t2", "count": 1})

    def test_profile_raises_on_unparseable(self) -> None:
        for document, fragment in (
            ("<a><b></a>", "mismatched tag"),
            ("<a>&foo;</a>", "undefined entity"),
        ):
            with self.subTest(document=document):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(mode="profile", xml_text=document)
                self.assertIn(fragment, str(ctx.exception))

    def test_profile_raises_on_dtd_document(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="profile", xml_text="<!DOCTYPE a><a/>"
            )
        self.assertIn("DTD-free", str(ctx.exception))

    def test_profile_raises_on_surrogates(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="profile", xml_text="<a>\ud800</a>")
        self.assertIn("surrogates", str(ctx.exception))


class XmlLintToolFixHintsTest(unittest.TestCase):
    """fix_hints: BOM note and pretty-print suggestion, never applied."""

    def setUp(self) -> None:
        self.tool = XmlLintTool()

    def test_canonical_two_space_suggestion_with_diff(self) -> None:
        text = "<a><b x='1'/><c/></a>"
        result = self.tool.execute(mode="fix_hints", xml_text=text)
        self.assertEqual(result["mode"], "fix_hints")
        self.assertFalse(result["applied"])
        self.assertFalse(result["parse_failed"])
        self.assertIsNone(result["bom_suggestion"])
        pretty = result["pretty_print"]
        self.assertTrue(pretty["applicable"])
        self.assertFalse(pretty["applied"])  # never applied
        self.assertTrue(pretty["changed"])
        self.assertEqual(
            pretty["suggested_text"],
            '<a>\n  <b x="1" />\n  <c />\n</a>',
        )
        self.assertEqual(pretty["summary"]["lines_before"], 1)
        self.assertEqual(pretty["summary"]["lines_after"], 4)
        self.assertEqual(pretty["summary"]["added_lines"], 4)
        self.assertEqual(pretty["summary"]["removed_lines"], 1)
        self.assertEqual(
            pretty["unified_diff"][:3],
            ["--- original", "+++ suggested", "@@ -1 +1,4 @@"],
        )
        self.assertFalse(pretty["diff_truncated"])
        # the input was never modified: re-running is stable
        again = self.tool.execute(mode="fix_hints", xml_text=text)
        self.assertEqual(again, result)

    def test_already_canonical_document_reports_changed_false(self) -> None:
        text = "<a>\n  <b x=\"1\" />\n  <c />\n</a>"
        result = self.tool.execute(mode="fix_hints", xml_text=text)
        pretty = result["pretty_print"]
        self.assertFalse(pretty["changed"])
        self.assertEqual(pretty["unified_diff"], [])
        self.assertNotIn("suggested_text", pretty)
        self.assertFalse(result["applied"])

    def test_bom_suggestion_is_a_note_not_an_edit(self) -> None:
        result = self.tool.execute(mode="fix_hints",
                                   xml_text="\ufeff<a><b/></a>")
        suggestion = result["bom_suggestion"]
        self.assertEqual(suggestion["action"], "strip_utf8_bom")
        self.assertEqual((suggestion["line"], suggestion["col"]), (1, 1))
        self.assertIn("never applied", suggestion["note"])
        self.assertFalse(result["applied"])

    def test_parse_failure_blocks_the_suggestion(self) -> None:
        result = self.tool.execute(mode="fix_hints", xml_text="<a><b></a>")
        self.assertTrue(result["parse_failed"])
        self.assertIn("mismatched tag", result["parse_error"])
        self.assertIsNone(result["pretty_print"])
        self.assertFalse(result["applied"])

    def test_dtd_document_blocks_the_suggestion(self) -> None:
        result = self.tool.execute(
            mode="fix_hints", xml_text="<!DOCTYPE a><a><b/></a>"
        )
        self.assertTrue(result["parse_failed"])
        self.assertIn("XXE", result["parse_error"])
        self.assertIsNone(result["pretty_print"])

    def test_mixed_content_text_is_preserved_by_the_suggestion(self) -> None:
        text = "<a>keep<b/>this</a>"
        result = self.tool.execute(mode="fix_hints", xml_text=text)
        suggested = result["pretty_print"]["suggested_text"]
        self.assertIn("keep", suggested)
        self.assertIn("this", suggested)
        # ET.indent only touches whitespace-only nodes
        self.assertEqual(suggested, "<a>keep<b />this</a>")

    def test_comments_and_pis_survive_the_suggestion(self) -> None:
        text = "<a><!-- c --><?pi d?><b/></a>"
        result = self.tool.execute(mode="fix_hints", xml_text=text)
        suggested = result["pretty_print"]["suggested_text"]
        self.assertIn("<!-- c -->", suggested)
        self.assertIn("<?pi d?>", suggested)

    def test_namespace_documents_carry_the_prefix_note(self) -> None:
        text = '<r xmlns:p="urn:p"><p:k/></r>'
        result = self.tool.execute(mode="fix_hints", xml_text=text)
        notes = " ".join(result["pretty_print"]["notes"])
        self.assertIn("ns0", notes)
        self.assertIn("equivalent", notes)
        suggested = result["pretty_print"]["suggested_text"]
        self.assertIn("ns0:", suggested)

    def test_declaration_documents_carry_the_declaration_note(self) -> None:
        text = '<?xml version="1.0"?><a><b/></a>'
        result = self.tool.execute(mode="fix_hints", xml_text=text)
        notes = " ".join(result["pretty_print"]["notes"])
        self.assertIn("XML declaration", notes)

    def test_suggestions_never_apply_back_into_the_input(self) -> None:
        text = "<a>  <b/>  </a>"
        before = text
        self.tool.execute(mode="fix_hints", xml_text=text)
        self.assertEqual(text, before)  # str is immutable; sanity only
        lint = self.tool.execute(mode="lint", xml_text=text)
        self.assertTrue(lint["parsed"])

    def test_diff_is_capped_at_forty_lines(self) -> None:
        parts = "".join(f"<e{i}/>" for i in range(60))
        text = f"<r>{parts}</r>"
        result = self.tool.execute(mode="fix_hints", xml_text=text)
        pretty = result["pretty_print"]
        self.assertEqual(len(pretty["unified_diff"]), 40)
        self.assertTrue(pretty["diff_truncated"])
        self.assertGreater(pretty["summary"]["added_lines"], 60)

    def test_no_whitespace_stripping_is_ever_offered(self) -> None:
        # trailing whitespace inside text content is literal in XML;
        # the tool must not suggest stripping it — the pretty-print
        # suggestion only reformats around <c/> and keeps every
        # interior space exactly as written
        text = "<r><a>kept   <b>inner  </b>tail   </a><c/></r>"
        result = self.tool.execute(mode="fix_hints", xml_text=text)
        blob = str(result)
        self.assertNotIn("strip_trailing", blob)
        self.assertNotIn("strip_whitespace", blob)
        suggested = result["pretty_print"]["suggested_text"]
        self.assertIn("kept   ", suggested)
        self.assertIn("inner  ", suggested)
        self.assertIn("tail   ", suggested)

    def test_thousand_deep_document_never_recursion_errors(self) -> None:
        # ET.indent and ET.tostring recurse per level; the tool's
        # serializer is iterative so the deep documents XML012 exists
        # for still get a suggestion instead of a RecursionError
        depth = 5000
        text = "<a>" * depth + "</a>" * depth
        result = self.tool.execute(mode="fix_hints", xml_text=text)
        self.assertFalse(result["parse_failed"])
        pretty = result["pretty_print"]
        self.assertTrue(pretty["changed"])
        reparsed = ET.fromstring(pretty["suggested_text"])
        seen = 0
        node = reparsed
        while node is not None:
            seen += 1
            node = node[0] if len(node) else None
        self.assertEqual(seen, depth)

    def test_iterative_serializer_matches_the_stdlib_output(self) -> None:
        from agentuniverse.agent.action.tool.common_tool.xml_lint_tool \
            import _indent_tree, _serialize_tree

        documents = [
            "<a><b x='1'/><c/></a>",
            '<r xmlns:p="urn:p"><p:k p:a="1">t</p:k><k/></r>',
            '<r xmlns="urn:d"><k/><k2>t</k2></r>',
            "<a><!-- c --><?pi d?><b/>tail</a>",
            "<a>keep<b/>this</a>",
            '<a q="&quot;hi&quot;&amp;&lt;x&gt;" t="a&#10;b&#13;c&#9;d">'
            "1 &lt; 2 &amp; 3</a>",
            '<r xmlns:xhtml="http://www.w3.org/1999/xhtml">'
            "<xhtml:div/></r>",
            '<r xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            ' xmlns:xs="http://www.w3.org/2001/XMLSchema">'
            '<xs:a xsi:b="1"/></r>',
            "<r><xml:a xml:l='1'/></r>",
            "<empty/>",
            "<a>text</a>",
            "<a><?pi?></a>",
        ]
        for document in documents:
            with self.subTest(document=document):
                stdlib_tree = ET.fromstring(document.encode("utf-8"))
                own_tree = ET.fromstring(document.encode("utf-8"))
                ET.indent(stdlib_tree, space="  ")
                expected = ET.tostring(stdlib_tree, encoding="unicode")
                _indent_tree(own_tree, space="  ")
                self.assertEqual(_serialize_tree(own_tree), expected)

    def test_no_declaration_note_for_stylesheet_pi(self) -> None:
        # only a real XML declaration at offset 0 earns the
        # declaration note; an xml-stylesheet PI is not one
        result = self.tool.execute(
            mode="fix_hints",
            xml_text='<?xml-stylesheet href="a.xsl"?><r><k/></r>',
        )
        notes = " ".join(result["pretty_print"]["notes"])
        self.assertNotIn("XML declaration", notes)

    def test_document_level_comment_loss_is_disclosed(self) -> None:
        # comments and PIs outside the root are not carried into any
        # re-serialization; the notes must say so
        result = self.tool.execute(
            mode="fix_hints",
            xml_text="<!-- lead --><r><k/></r><!-- trail -->",
        )
        notes = " ".join(result["pretty_print"]["notes"])
        self.assertIn("document-level", notes)
        self.assertNotIn("<!-- lead -->",
                         result["pretty_print"]["suggested_text"])


class XmlLintToolValidationMatrixTest(unittest.TestCase):
    """The option/argument error matrix."""

    def setUp(self) -> None:
        self.tool = XmlLintTool()

    def test_unknown_mode(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="format", xml_text="<a/>")
        self.assertIn("mode must be one of", str(ctx.exception))

    def test_non_string_xml_text(self) -> None:
        for bad in (None, 42, b"<a/>", ["<a/>"]):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(mode="lint", xml_text=bad)
                self.assertIn("xml_text must be a string",
                              str(ctx.exception))

    def test_oversized_xml_text(self) -> None:
        huge = "<a>" + "x" * 1_000_003 + "</a>"
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="lint", xml_text=huge)
        self.assertIn("1,000,000-character limit", str(ctx.exception))

    def test_max_input_chars_boundary(self) -> None:
        # exactly 1,000,000 characters passes validation (then lints)
        doc = "<a>" + "x" * 999_993 + "</a>"
        self.assertEqual(len(doc), 1_000_000)
        result = self.tool.execute(mode="lint", xml_text=doc)
        self.assertIn("XML008", codes(result))

    def test_option_rejected_for_wrong_mode(self) -> None:
        for mode in ("profile", "fix_hints"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(mode=mode, xml_text="<a/>",
                                      max_depth=8)
                self.assertIn("is not a", str(ctx.exception))
                self.assertIn("mode option", str(ctx.exception))
                with self.assertRaises(ValueError):
                    self.tool.execute(mode=mode, xml_text="<a/>",
                                      rules={"XML010": False})

    def test_max_depth_type_and_range(self) -> None:
        for bad in (True, "8", 3.5, 0, -1, 129):
            with self.subTest(max_depth=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="lint", xml_text="<a/>",
                                      max_depth=bad)

    def test_max_depth_boundaries_accepted(self) -> None:
        self.tool.execute(mode="lint", xml_text="<a/>", max_depth=1)
        self.tool.execute(mode="lint", xml_text="<a/>", max_depth=128)

    def test_rules_validation(self) -> None:
        for bad in ("XML010", ["XML010"], {"XML999": False},
                    {"XML010": "no"}, {"XML010": None}):
            with self.subTest(rules=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="lint", xml_text="<a/>",
                                      rules=bad)

    def test_rules_disable_is_per_call_only(self) -> None:
        text = "<a><b/></a>"
        disabled = self.tool.execute(
            mode="lint", xml_text=text, rules={"XML010": False}
        )
        enabled = self.tool.execute(mode="lint", xml_text=text)
        self.assertEqual(codes(disabled), [])
        self.assertEqual(codes(enabled), ["XML010"])

    def test_all_rules_individually_disableable(self) -> None:
        text = "\ufeff<!DOCTYPE a><a>&foo;</a>"
        for code in _RULES:
            with self.subTest(code=code):
                result = self.tool.execute(
                    mode="lint", xml_text=text, rules={code: False}
                )
                self.assertNotIn(code, codes(result))


class XmlLintToolBehaviourTest(unittest.TestCase):
    """Cross-cutting guarantees: sorting, caps, determinism, family."""

    def setUp(self) -> None:
        self.tool = XmlLintTool()

    def test_findings_sorted_by_line_col_code(self) -> None:
        text = "\ufeff<a>line\n<b/>&foo;</a>"
        result = self.tool.execute(mode="lint", xml_text=text)
        keys = [
            (f["line"], f["col"], f["code"]) for f in result["findings"]
        ]
        self.assertEqual(keys, sorted(keys))

    def test_finding_cap_at_two_hundred(self) -> None:
        text = "<r>" + "".join(f"<e{i}/>" for i in range(250)) + "</r>"
        result = self.tool.execute(mode="lint", xml_text=text)
        self.assertEqual(result["finding_count"], 250)
        self.assertEqual(len(result["findings"]), 200)
        self.assertTrue(result["findings_truncated"])
        self.assertTrue(result["ok"])  # info-only stays ok

    def test_ok_false_only_for_errors(self) -> None:
        error_doc = self.tool.execute(mode="lint", xml_text="<a><b></a>")
        info_doc = self.tool.execute(mode="lint", xml_text="<a><b/></a>")
        self.assertFalse(error_doc["ok"])
        self.assertTrue(info_doc["ok"])

    def test_determinism(self) -> None:
        text = (
            "\ufeff<?xml version='1.0' encoding='latin1'?>\n"
            "<r>\u4f60\u597d<x/>\n<!-- c -->\n</r>"
        )
        first = self.tool.execute(mode="lint", xml_text=text)
        for _ in range(3):
            self.assertEqual(
                self.tool.execute(mode="lint", xml_text=text), first
            )
        profile = self.tool.execute(mode="profile", xml_text=text)
        self.assertEqual(
            self.tool.execute(mode="profile", xml_text=text), profile
        )
        hints = self.tool.execute(mode="fix_hints", xml_text=text)
        self.assertEqual(
            self.tool.execute(mode="fix_hints", xml_text=text), hints
        )

    def test_cjk_document_full_cycle(self) -> None:
        text = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<\u8ba2\u5355 id='1'>\n"
            "  <\u5546\u54c1>\u4e66\u7c4d\u300a\u667a\u80fd\u4f53\u5b87\u5b99\u300b</\u5546\u54c1>\n"
            "  <\u5907\u6ce8/>\n"
            "</\u8ba2\u5355>"
        )
        lint = self.tool.execute(mode="lint", xml_text=text)
        self.assertTrue(lint["ok"])
        self.assertEqual(codes(lint), ["XML010"])  # <\u5907\u6ce8/> is empty
        profile = self.tool.execute(mode="profile", xml_text=text)
        self.assertEqual(profile["element_count"], 3)
        self.assertEqual(profile["root_tag"], "\u8ba2\u5355")
        self.assertEqual(profile["text_length_max"], 9)
        hints = self.tool.execute(mode="fix_hints", xml_text=text)
        self.assertFalse(hints["parse_failed"])
        self.assertIn("\u4e66\u7c4d", hints["pretty_print"]["suggested_text"])

    def test_exported_from_common_tool_package(self) -> None:
        from agentuniverse.agent.action.tool.common_tool import (
            XmlLintTool as Exported,
        )

        self.assertIs(Exported, XmlLintTool)

    def test_registration_yaml_declares_the_tool(self) -> None:
        import pathlib

        path = (
            pathlib.Path(__file__).parents[6]
            / "agentuniverse" / "agent" / "action" / "tool"
            / "common_tool" / "xml_lint_tool.yaml"
        )
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(config["name"], "xml_lint_tool")
        self.assertEqual(config["tool_type"], "api")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.xml_lint_tool",
        )
        self.assertEqual(config["metadata"]["class"], "XmlLintTool")
        self.assertEqual(config["input_keys"], ["mode", "xml_text"])
        schema = config["args_model_schema"]
        self.assertEqual(
            schema["properties"]["mode"]["enum"],
            ["lint", "profile", "fix_hints"],
        )
        self.assertEqual(schema["required"], ["mode", "xml_text"])


if __name__ == "__main__":
    unittest.main()
