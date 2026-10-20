#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_xml_path_tool.py

"""Offline unit tests for XmlPathTool.

The tool is built purely on the standard library (xml.etree.
ElementTree) and never touches the network, so this suite runs fully
offline. Every assertion is deterministic: selections are checked
against hand-counted ground truths on fixed fixtures (a 19-element
nested catalog, a namespaced RSS document, a two-shelf grouping
fixture), index / last() / attribute-predicate boundaries are pinned
exactly, malformed-XML positions reuse the expat line numbers of the
fixtures, and the error matrix (ValueError vs structured payloads)
is enumerated case by case.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import XmlPathTool
from agentuniverse.agent.action.tool.common_tool.xml_path_tool import (
    XmlPathTool as DirectXmlPathTool,
)

# --------------------------------------------------------------------- #
# Fixtures (hand-counted ground truths)
# --------------------------------------------------------------------- #

# 19 elements in total, max depth 4 (catalog -> book -> tags -> tag):
# catalog; 3 book (b1..b3); 4 title; 3 author; 3 price; tags; 2 tag;
# note; magazine. The prolog carries an encoding declaration, which the
# tool must accept because it parses UTF-8 bytes, not the raw str.
CATALOG_XML = """<?xml version="1.0" encoding="UTF-8"?>
<catalog version="2.0" lang="en">
  <book id="b1" category="fiction">
    <title lang="en">Dune</title>
    <author>Frank Herbert</author>
    <price currency="USD">19.99</price>
    <tags>
      <tag>scifi</tag>
      <tag>epic</tag>
    </tags>
  </book>
  <book id="b2" category="tech">
    <title lang="de">Einf\u00fchrung in XML</title>
    <author>Some Author</author>
    <price currency="EUR"/>
    <note/>
  </book>
  <book id="b3" category="fiction">
    <title lang="en">Foundation</title>
    <author>Isaac Asimov</author>
    <price currency="USD">12.50</price>
  </book>
  <magazine id="m1">
    <title>XML Today</title>
  </magazine>
</catalog>
"""

# Namespace-stripped matching: dc:creator and atom:link carry URIs that
# ElementTree reports as {uri}local; paths use plain local names.
NS_XML = (
    '<rss xmlns:dc="http://purl.org/dc/elements/1.1/" '
    'xmlns:atom="http://www.w3.org/2005/Atom">\n'
    "  <channel>\n"
    "    <title>Feed</title>\n"
    "    <item><dc:creator>alice</dc:creator></item>\n"
    "    <item><dc:creator>bob</dc:creator></item>\n"
    '    <atom:link href="/feed"/>\n'
    "  </channel>\n"
    "</rss>"
)

# Per-parent positional predicate fixture: two shelves, each holding
# its own book children.
SHELF_XML = (
    "<root>"
    "<shelf><book id='s1a'/><book id='s1b'/></shelf>"
    "<shelf><book id='s2a'/></shelf>"
    "</root>"
)

# Attribute quoting / escaping / empty-value fixture.
QUOTE_XML = "<r><item v=\"it's\"/><item v='say \"hi\"'/><item v=\"\"/></r>"

# Mixed content: p's own text is only the block before <b>.
MIXED_XML = "<p>hello <b>bold</b> world</p>"

DOCTYPE_ENTITY_XML = (
    '<?xml version="1.0"?><!DOCTYPE catalog [<!ENTITY x "boom">]>'
    "<catalog>&x;</catalog>"
)
DOCTYPE_ONLY_XML = "<!DOCTYPE catalog><catalog/>"
DOCTYPE_IN_COMMENT_XML = "<!-- <!DOCTYPE catalog> --><catalog/>"
ENTITY_IN_COMMENT_XML = '<!-- <!ENTITY x "y"> --><catalog/>'

# expat reports the mismatched </catalog> on line 3.
MISMATCHED_XML = "<catalog>\n  <book>\n</catalog>"
UNCLOSED_XML = "<catalog><book></book>"
WHITESPACE_ONLY_XML = "   "


class XmlPathToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib XmlPathTool."""

    def setUp(self) -> None:
        self.tool = XmlPathTool()

    # -- helpers ------------------------------------------------------- #

    def ids(self, path: str, xml_text: str = CATALOG_XML) -> list:
        """Query a path and return the id attribute of each match."""
        result = self.tool.execute(mode="query", xml_text=xml_text, path=path)
        assert "error" not in result, result.get("error")
        return [m["attributes"].get("id") for m in result["matches"]]

    # ------------------------------------------------------------------ #
    # query mode — path syntax elements
    # ------------------------------------------------------------------ #

    def test_direct_import_matches_package_export(self) -> None:
        self.assertIs(DirectXmlPathTool, XmlPathTool)

    def test_query_root_element(self) -> None:
        result = self.tool.execute(mode="query", xml_text=CATALOG_XML, path="/catalog")
        self.assertEqual(result["found"], True)
        self.assertEqual(result["count"], 1)
        self.assertEqual(
            result["matches"],
            [
                {
                    "tag": "catalog",
                    "attributes": {"version": "2.0", "lang": "en"},
                    "text": None,
                    "child_count": 4,
                }
            ],
        )

    def test_query_child_nesting(self) -> None:
        result = self.tool.execute(
            mode="query", xml_text=CATALOG_XML, path="/catalog/book"
        )
        self.assertEqual(result["count"], 3)
        self.assertTrue(all(m["tag"] == "book" for m in result["matches"]))
        self.assertEqual(
            [m["attributes"]["id"] for m in result["matches"]], ["b1", "b2", "b3"]
        )

    def test_query_match_record_structure(self) -> None:
        result = self.tool.execute(
            mode="query", xml_text=CATALOG_XML, path="/catalog/book[1]"
        )
        self.assertEqual(
            result["matches"],
            [
                {
                    "tag": "book",
                    "attributes": {"id": "b1", "category": "fiction"},
                    "text": None,  # whitespace-only text strips to empty
                    "child_count": 4,
                }
            ],
        )

    def test_query_descendant_axis(self) -> None:
        for path, expected in (
            ("//title", 4),
            ("//tag", 2),
            ("//book", 3),
            ("//*", 19),
            ("/catalog//tag", 2),
            ("//book/price", 3),
        ):
            result = self.tool.execute(mode="query", xml_text=CATALOG_XML, path=path)
            self.assertEqual(result["count"], expected, path)

    def test_query_double_star_alias(self) -> None:
        plain = self.tool.execute(mode="query", xml_text=CATALOG_XML, path="//title")
        starred = self.tool.execute(
            mode="query", xml_text=CATALOG_XML, path="/catalog/**/title"
        )
        self.assertEqual(starred["count"], 4)
        self.assertEqual(plain["matches"], starred["matches"])
        # A trailing /** selects every strict descendant of catalog.
        tail = self.tool.execute(mode="query", xml_text=CATALOG_XML, path="/catalog/**")
        self.assertEqual(tail["count"], 18)
        # A path of exactly /** selects every element.
        whole = self.tool.execute(mode="query", xml_text=CATALOG_XML, path="/**")
        self.assertEqual(whole["count"], 19)

    def test_query_wildcard_one_level(self) -> None:
        result = self.tool.execute(mode="query", xml_text=CATALOG_XML, path="/catalog/*")
        self.assertEqual(result["count"], 4)
        self.assertEqual(
            [m["tag"] for m in result["matches"]], ["book", "book", "book", "magazine"]
        )
        deep = self.tool.execute(
            mode="query", xml_text=CATALOG_XML, path="/catalog/book/*"
        )
        # 4 + 4 + 3 children across the three books.
        self.assertEqual(deep["count"], 11)

    def test_query_index_boundaries(self) -> None:
        self.assertEqual(self.ids("/catalog/book[1]"), ["b1"])
        self.assertEqual(self.ids("/catalog/book[2]"), ["b2"])
        self.assertEqual(self.ids("/catalog/book[3]"), ["b3"])
        result = self.tool.execute(
            mode="query", xml_text=CATALOG_XML, path="/catalog/book[4]"
        )
        self.assertEqual(
            (result["found"], result["count"], result["matches"]), (False, 0, [])
        )

    def test_query_last(self) -> None:
        self.assertEqual(self.ids("/catalog/book[last()]"), ["b3"])
        # last() of the tags list (flat descendant step, document order).
        result = self.tool.execute(
            mode="text", xml_text=CATALOG_XML, path="//tag[last()]"
        )
        self.assertEqual(result["values"], [{"tag": "tag", "text": "epic"}])

    def test_query_index_is_per_parent_after_slash(self) -> None:
        # XPath-style: book[1] inside each shelf.
        self.assertEqual(self.ids("/root/shelf/book[1]", SHELF_XML), ["s1a", "s2a"])
        self.assertEqual(self.ids("/root/shelf/book[2]", SHELF_XML), ["s1b"])
        self.assertEqual(self.ids("/root/shelf/book[last()]", SHELF_XML), ["s1b", "s2a"])

    def test_query_index_is_flat_after_double_slash(self) -> None:
        # Documented deviation: after // the index numbers the whole
        # de-duplicated document-order candidate list.
        self.assertEqual(self.ids("//book[2]", SHELF_XML), ["s1b"])
        self.assertEqual(self.ids("//book[last()]", SHELF_XML), ["s2a"])

    def test_query_attribute_equality_single_quotes(self) -> None:
        self.assertEqual(self.ids("//book[@category='fiction']"), ["b1", "b3"])
        self.assertEqual(self.ids("//book[@category='tech']"), ["b2"])
        self.assertEqual(self.ids("//book[@category='nope']"), [])

    def test_query_attribute_equality_double_quotes(self) -> None:
        self.assertEqual(self.ids('//book[@category="fiction"]'), ["b1", "b3"])

    def test_query_has_attribute_predicate(self) -> None:
        self.assertEqual(self.ids("//book[@id]"), ["b1", "b2", "b3"])
        result = self.tool.execute(
            mode="query", xml_text=CATALOG_XML, path="//*[@id='m1']"
        )
        self.assertEqual(
            [m["tag"] for m in result["matches"]], ["magazine"]
        )

    def test_query_chained_predicates(self) -> None:
        self.assertEqual(self.ids("//book[@category='fiction'][2]"), ["b3"])
        self.assertEqual(self.ids("/catalog/book[2][@category='tech']"), ["b2"])
        self.assertEqual(self.ids("/catalog/book[1][@category='tech']"), [])

    def test_query_whitespace_inside_predicates(self) -> None:
        self.assertEqual(self.ids("//book[ @category = 'fiction' ]"), ["b1", "b3"])
        self.assertEqual(self.ids("//book[ 1 ]"), ["b1"])
        self.assertEqual(self.ids("//book[ last() ]"), ["b3"])

    def test_query_attribute_quoting_counts(self) -> None:
        # The three item elements differ exactly by their v attribute.
        for path, expected in (
            ('//item[@v="it\'s"]', 1),
            ('//item[@v=\'say "hi"\']', 1),
            ("//item[@v='it\\'s']", 1),
            ("//item[@v='']", 1),
            ("//item[@v]", 3),
            ("//item[@v='nope']", 0),
        ):
            result = self.tool.execute(mode="query", xml_text=QUOTE_XML, path=path)
            self.assertEqual(result["count"], expected, path)

    def test_query_namespace_stripped_tag_matching(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="query", xml_text=NS_XML, path="/rss/channel/item/creator"
            )["count"],
            2,
        )
        self.assertEqual(
            self.tool.execute(mode="query", xml_text=NS_XML, path="//creator")["count"],
            2,
        )
        link = self.tool.execute(mode="query", xml_text=NS_XML, path="//link")
        self.assertEqual(link["count"], 1)
        self.assertEqual(link["matches"][0]["attributes"], {"href": "/feed"})

    def test_query_no_match_is_not_an_error(self) -> None:
        result = self.tool.execute(
            mode="query", xml_text=CATALOG_XML, path="/catalog/podcast"
        )
        self.assertEqual(
            result,
            {
                "mode": "query",
                "path": "/catalog/podcast",
                "found": False,
                "total": 0,
                "count": 0,
                "truncated": False,
                "matches": [],
            },
        )

    def test_query_accepts_encoding_declaration(self) -> None:
        # The fixture prolog declares encoding="UTF-8"; the tool parses
        # UTF-8 bytes so the declaration is honored, not fatal.
        result = self.tool.execute(
            mode="query", xml_text=CATALOG_XML, path="/catalog"
        )
        self.assertEqual(result["count"], 1)

    def test_query_is_deterministic(self) -> None:
        first = self.tool.execute(mode="query", xml_text=CATALOG_XML, path="//*")
        second = self.tool.execute(mode="query", xml_text=CATALOG_XML, path="//*")
        self.assertEqual(first, second)

    def test_query_text_snippet_is_capped(self) -> None:
        long_text = "<r><x>" + "a" * 300 + "</x></r>"
        result = self.tool.execute(mode="query", xml_text=long_text, path="/r/x")
        snippet = result["matches"][0]["text"]
        self.assertEqual(snippet, "a" * 200 + "...")
        self.assertEqual(len(snippet), 203)

    # ------------------------------------------------------------------ #
    # attrs mode
    # ------------------------------------------------------------------ #

    def test_attrs_mode(self) -> None:
        result = self.tool.execute(mode="attrs", xml_text=CATALOG_XML, path="/catalog")
        self.assertEqual(result["attributes"], [{"version": "2.0", "lang": "en"}])
        prices = self.tool.execute(mode="attrs", xml_text=CATALOG_XML, path="//price")
        self.assertEqual(
            prices["attributes"],
            [{"currency": "USD"}, {"currency": "EUR"}, {"currency": "USD"}],
        )
        # Attribute-less elements yield empty dicts, not omissions.
        note = self.tool.execute(mode="attrs", xml_text=CATALOG_XML, path="//note")
        self.assertEqual(note["attributes"], [{}])
        self.assertEqual(note["found"], True)

    # ------------------------------------------------------------------ #
    # text mode
    # ------------------------------------------------------------------ #

    def test_text_mode_values(self) -> None:
        result = self.tool.execute(mode="text", xml_text=CATALOG_XML, path="//title")
        self.assertEqual(
            result["values"],
            [
                {"tag": "title", "text": "Dune"},
                {"tag": "title", "text": "Einf\u00fchrung in XML"},
                {"tag": "title", "text": "Foundation"},
                {"tag": "title", "text": "XML Today"},
            ],
        )
        self.assertEqual(result["empty_text_count"], 0)

    def test_text_mode_reports_empty_text_elements(self) -> None:
        result = self.tool.execute(mode="text", xml_text=CATALOG_XML, path="//price")
        self.assertEqual(
            result["values"],
            [
                {"tag": "price", "text": "19.99"},
                {"tag": "price", "text": None},  # <price currency="EUR"/> has no text
                {"tag": "price", "text": "12.50"},
            ],
        )
        self.assertEqual(result["empty_text_count"], 1)
        note = self.tool.execute(mode="text", xml_text=CATALOG_XML, path="//note")
        self.assertEqual(note["values"], [{"tag": "note", "text": None}])
        self.assertEqual(note["empty_text_count"], 1)

    def test_text_mode_own_text_only_for_mixed_content(self) -> None:
        # Documented subset behavior: only the element's own text block
        # is returned; tails and nested text are not concatenated.
        result = self.tool.execute(mode="text", xml_text=MIXED_XML, path="/p")
        self.assertEqual(result["values"], [{"tag": "p", "text": "hello"}])
        bold = self.tool.execute(mode="text", xml_text=MIXED_XML, path="/p/b")
        self.assertEqual(bold["values"], [{"tag": "b", "text": "bold"}])

    def test_text_mode_returns_full_text_not_snippet(self) -> None:
        long_text = "<r><x>" + "a" * 300 + "</x></r>"
        result = self.tool.execute(mode="text", xml_text=long_text, path="/r/x")
        self.assertEqual(result["values"], [{"tag": "x", "text": "a" * 300}])

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def test_validate_well_formed_document(self) -> None:
        result = self.tool.execute(mode="validate", xml_text=CATALOG_XML)
        self.assertEqual(
            result,
            {
                "mode": "validate",
                "valid": True,
                "root_tag": "catalog",
                "element_count": 19,
                "max_depth": 4,
            },
        )

    def test_validate_reports_local_root_tag_with_namespaces(self) -> None:
        result = self.tool.execute(mode="validate", xml_text=NS_XML)
        self.assertEqual(result["valid"], True)
        self.assertEqual(result["root_tag"], "rss")

    def test_validate_ignores_path_parameter(self) -> None:
        result = self.tool.execute(
            mode="validate", xml_text=CATALOG_XML, path="/not/used"
        )
        self.assertEqual(result["valid"], True)

    def test_validate_malformed_reports_line_and_column(self) -> None:
        result = self.tool.execute(mode="validate", xml_text=MISMATCHED_XML)
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["type"], "not_well_formed")
        self.assertEqual(result["error"]["line"], 3)
        self.assertIsInstance(result["error"]["column"], int)
        self.assertGreaterEqual(result["error"]["column"], 1)
        self.assertIn("mismatched", result["error"]["message"])

    def test_validate_unclosed_element(self) -> None:
        result = self.tool.execute(mode="validate", xml_text=UNCLOSED_XML)
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["type"], "not_well_formed")
        self.assertIsInstance(result["error"]["line"], int)

    def test_validate_whitespace_only_document(self) -> None:
        result = self.tool.execute(mode="validate", xml_text=WHITESPACE_ONLY_XML)
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["type"], "not_well_formed")

    # ------------------------------------------------------------------ #
    # XXE protection: DTD / ENTITY rejection before any parsing
    # ------------------------------------------------------------------ #

    def test_doctype_with_entity_rejected_in_all_modes(self) -> None:
        for mode in ("query", "attrs", "text"):
            result = self.tool.execute(
                mode=mode, xml_text=DOCTYPE_ENTITY_XML, path="/catalog"
            )
            self.assertEqual(result["error"]["type"], "dtd_not_allowed", mode)
            self.assertIn("XXE", result["error"]["message"])
            self.assertIn("line", result["error"])
            self.assertIn("column", result["error"])
        validation = self.tool.execute(mode="validate", xml_text=DOCTYPE_ENTITY_XML)
        self.assertEqual(validation["valid"], False)
        self.assertEqual(validation["error"]["type"], "dtd_not_allowed")

    def test_bare_doctype_rejected(self) -> None:
        result = self.tool.execute(
            mode="validate", xml_text=DOCTYPE_ONLY_XML
        )
        self.assertEqual(result["valid"], False)
        self.assertEqual(result["error"]["type"], "dtd_not_allowed")

    def test_dtd_guard_is_conservative_inside_comments(self) -> None:
        # Mentions inside comments are rejected too — documented as a
        # deliberate false-positive direction (safe over sorry).
        for xml_text in (DOCTYPE_IN_COMMENT_XML, ENTITY_IN_COMMENT_XML):
            result = self.tool.execute(mode="validate", xml_text=xml_text)
            self.assertEqual(result["error"]["type"], "dtd_not_allowed")

    def test_dtd_guard_reports_location(self) -> None:
        result = self.tool.execute(mode="validate", xml_text=DOCTYPE_ONLY_XML)
        # <!DOCTYPE starts at line 1, column 1.
        self.assertEqual((result["error"]["line"], result["error"]["column"]), (1, 1))
        multiline = "<catalog>\n  <!DOCTYPE x>\n</catalog>"
        located = self.tool.execute(mode="validate", xml_text=multiline)
        self.assertEqual(located["error"]["line"], 2)

    def test_dtd_guard_column_counts_characters(self) -> None:
        # The marker column must count characters, not UTF-8 bytes, so it
        # stays consistent with the expat columns of not_well_formed errors
        # ('<!DOCTYPE' starts at 0-based character index 5 -> column 6).
        result = self.tool.execute(mode="validate", xml_text="<北京>x<!DOCTYPE y>")
        self.assertEqual((result["error"]["line"], result["error"]["column"]), (1, 6))

    def test_dtd_guard_rejects_entity_marker_in_attribute_value(self) -> None:
        # Conservative direction: the literal '<!ENTITY' inside an attribute
        # value is refused before any parsing rather than risk parsing it.
        result = self.tool.execute(
            mode="validate", xml_text='<a title="<!ENTITY x SYSTEM \'e\'>">t</a>'
        )
        self.assertEqual(result["error"]["type"], "dtd_not_allowed")

    def test_size_caps_driven_by_fields(self) -> None:
        # The limits come from the max_xml_chars / max_path_chars fields,
        # not hardcoded constants.
        class TunedXmlPathTool(XmlPathTool):
            max_xml_chars: int = 20
            max_path_chars: int = 8

        tuned = TunedXmlPathTool()
        self.assertEqual(
            tuned.execute(mode="query", xml_text="<a><b/></a>", path="/a/b")["total"],
            1,
        )
        with self.assertRaises(ValueError):
            tuned.execute(mode="query", xml_text="<a>" + "x" * 20 + "</a>", path="/a")
        with self.assertRaises(ValueError):
            tuned.execute(mode="query", xml_text="<a><b/></a>", path="/a/b[1]/*")

    # ------------------------------------------------------------------ #
    # Structured error payloads: encoding, malformed XML, invalid paths
    # ------------------------------------------------------------------ #

    def test_unpaired_surrogate_returns_invalid_unicode(self) -> None:
        result = self.tool.execute(mode="query", xml_text="\ud800", path="/a")
        self.assertEqual(result["error"]["type"], "invalid_unicode")

    def test_malformed_xml_in_query_modes(self) -> None:
        for mode in ("query", "attrs", "text"):
            result = self.tool.execute(
                mode=mode, xml_text=MISMATCHED_XML, path="/catalog"
            )
            self.assertEqual(result["error"]["type"], "not_well_formed", mode)
            self.assertEqual(result["error"]["line"], 3)

    def test_invalid_path_matrix(self) -> None:
        bad_paths = [
            "catalog/book",            # relative, not absolute
            "/catalog/",               # trailing separator
            "//",                      # separator without a step
            "/",                       # root slash without a step
            "/catalog//",              # trailing descendant separator
            "/catalog/book[0]",        # 0 index (indexes are 1-based)
            "/catalog/book[-1]",       # negative index
            "/catalog/book[01]",       # leading zero
            "/catalog/book[x]",        # neither index, last() nor @attr
            "/catalog/book[last",      # unterminated last()
            "/catalog/book[last()x]",  # junk after last()
            "/catalog/book[]",         # empty predicate
            "/catalog/book[@]",        # missing attribute name
            "/catalog/book[@id=]",     # missing quoted value
            "/catalog/book[@id='b1]",  # unterminated quote
            "/catalog/book[@id=='b1']",  # '==' is not supported
            "/catalog/book[@id!='b1']",  # '!=' is not supported
            "/catalog/**book",         # '**' must be a whole step
            "/catalog/book extra",     # junk after a step
            "/2book",                  # names cannot start with a digit
        ]
        for path in bad_paths:
            result = self.tool.execute(
                mode="query", xml_text=CATALOG_XML, path=path
            )
            self.assertEqual(
                result.get("error", {}).get("type"),
                "invalid_path",
                f"path {path!r} should be rejected",
            )
            # Syntax errors carry the position of the offender.
            self.assertIn("position", result["error"]["message"], path)

    def test_invalid_path_position_is_reported(self) -> None:
        result = self.tool.execute(
            mode="query", xml_text=CATALOG_XML, path="catalog/book"
        )
        self.assertIn("position 0", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # Strict input validation (ValueError before any work)
    # ------------------------------------------------------------------ #

    def test_unknown_mode_raises(self) -> None:
        for mode in (None, "xquery", "QUERY", 1, True):
            with self.assertRaises(ValueError):
                self.tool.execute(mode=mode, xml_text=CATALOG_XML, path="/catalog")

    def test_bad_xml_text_raises(self) -> None:
        for xml_text in (None, "", 123, True, b"<catalog/>", ["<a/>"]):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="query", xml_text=xml_text, path="/catalog")

    def test_bad_path_raises(self) -> None:
        for path in (None, "", 123, True, ["/catalog"]):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="query", xml_text=CATALOG_XML, path=path)

    def test_missing_xml_text_in_validate_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="validate")

    def test_oversized_xml_text_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="query", xml_text="<r>" + "x" * 100_001 + "</r>", path="/r"
            )

    def test_oversized_path_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="query", xml_text=CATALOG_XML, path="/catalog/" + "a" * 2_000
            )

    # ------------------------------------------------------------------ #
    # Caps
    # ------------------------------------------------------------------ #

    def test_match_cap_truncates_with_flag(self) -> None:
        capped = XmlPathTool(max_matches=3)
        result = capped.execute(mode="query", xml_text=CATALOG_XML, path="//*")
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["total"], 19)
        self.assertEqual(result["truncated"], True)

    def test_default_cap_does_not_truncate_small_documents(self) -> None:
        result = self.tool.execute(mode="query", xml_text=CATALOG_XML, path="//*")
        self.assertEqual((result["count"], result["total"], result["truncated"]), (19, 19, False))


if __name__ == "__main__":
    unittest.main()
