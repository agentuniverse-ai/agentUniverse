#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_bibtex_tool.py

"""Offline unit tests for BibtexTool.

The tool is built purely on the standard library (a hand-written
character-level scanner, no third-party BibTeX library) and never
touches the network, so this suite runs fully offline. Every
assertion is deterministic: the parser is checked against literal
ground-truth entry structures built from a realistic .bib fixture
(@string macros, nested-brace title protection, quoted and
'#'-concatenated values, both author name orders, @comment/@preamble
skipping), the summary arithmetic against hand-computed counts, and
the error matrix against exact error types and character positions
(offset/line/column) computed from the fixture strings themselves.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import BibtexTool
from agentuniverse.agent.action.tool.common_tool.bibtex_tool import (
    BibtexTool as DirectBibtexTool,
)


def person(first: str, last: str, raw: str, jr: str = "") -> dict:
    """Shorthand for an expected person object."""
    return {"first": first, "last": last, "jr": jr, "raw": raw}


# --------------------------------------------------------------------- #
# Ground-truth fixture: realistic .bib covering every documented rule.
# --------------------------------------------------------------------- #
SAMPLE_BIB = """\
% contact: admin@example.com (email '@'s in comments are skipped)
leading free text between entries is an implicit comment

@comment{this block is ignored, even with {nested} braces}

@string{acm = "Association for Computing Machinery"}
@string{tocs = acm # " Transactions on Computer Systems"}

@preamble{ "\\makeatletter" }

@article{knuth1984,
  author = {Knuth, Donald E.},
  title = {Literate Programming},
  journal = tocs,
  year = 1984,
  volume = 12,
  number = 2,
  pages = {97--111}
}

@book{lamport1994,
  author = "Leslie Lamport",
  title = "{LaTeX}: A Document Preparation System",
  publisher = "Addison " # "Wesley",
  year = "1994",
  address = "Reading,   Massachusetts"
}

@inproceedings{berners2001,
  author = "Tim Berners-Lee and {Barnes and Noble} and Hendler, James",
  title = "The {"}Semantic{"} Web",
  booktitle = {Scientific American},
  year = {2001}
}

@misc{bibtex2024,
  title = {The {B}ib{T}e{X} companion},
  howpublished = "\\url{https://example.com}",
  note = "quoted value with a {nested {deep}} brace group",
  year = {2024}
}

@article(nologic,
  author = {No Year Here},
  title = {Paren-delimited entry without a year},
  journal = {J. Arbitrary}
)
"""

SAMPLE_ENTRIES = [
    {
        "type": "article",
        "key": "knuth1984",
        "fields": {
            "author": [person("Donald E.", "Knuth", "Knuth, Donald E.")],
            "title": "Literate Programming",
            # @string macro expansion inside a '#'-concatenation.
            "journal": (
                "Association for Computing Machinery Transactions on "
                "Computer Systems"
            ),
            "year": "1984",  # bare number value
            "volume": "12",
            "number": "2",
            "pages": "97--111",
        },
    },
    {
        "type": "book",
        "key": "lamport1994",
        "fields": {
            "author": [person("Leslie", "Lamport", "Leslie Lamport")],
            # Protective braces survive parsing.
            "title": "{LaTeX}: A Document Preparation System",
            # '"Addison " # "Wesley"' concatenation.
            "publisher": "Addison Wesley",
            "year": "1994",
            # Runs of whitespace collapse to single spaces.
            "address": "Reading, Massachusetts",
        },
    },
    {
        "type": "inproceedings",
        "key": "berners2001",
        "fields": {
            "author": [
                person("Tim", "Berners-Lee", "Tim Berners-Lee"),
                person("", "{Barnes and Noble}", "{Barnes and Noble}"),
                person("James", "Hendler", "Hendler, James"),
            ],
            # Brace groups inside a quoted value protect literal quotes.
            "title": 'The {"}Semantic{"} Web',
            "booktitle": "Scientific American",
            "year": "2001",
        },
    },
    {
        "type": "misc",
        "key": "bibtex2024",
        "fields": {
            "title": "The {B}ib{T}e{X} companion",
            "howpublished": "\\url{https://example.com}",
            "note": "quoted value with a {nested {deep}} brace group",
            "year": "2024",
        },
    },
    {
        "type": "article",
        "key": "nologic",
        "fields": {
            "author": [person("No Year", "Here", "No Year Here")],
            "title": "Paren-delimited entry without a year",
            "journal": "J. Arbitrary",
        },
    },
]


def expected_position(bib: str, offset: int) -> dict:
    """Compute the ground-truth position dict for a fixture offset."""
    line = bib.count("\n", 0, offset) + 1
    column = offset - (bib.rfind("\n", 0, offset) + 1) + 1
    return {"offset": offset, "line": line, "column": column}


class BibtexToolParseTest(unittest.TestCase):
    """Offline deterministic test cases for the parse mode."""

    def setUp(self) -> None:
        self.tool = BibtexTool()

    def test_parse_full_ground_truth(self) -> None:
        result = self.tool.execute(mode="parse", bib=SAMPLE_BIB)
        self.assertEqual(
            result, {"mode": "parse", "count": 5, "entries": SAMPLE_ENTRIES}
        )

    def test_parse_field_order_preserved(self) -> None:
        fields = self.tool.execute(mode="parse", bib=SAMPLE_BIB)["entries"][
            0
        ]["fields"]
        self.assertEqual(
            list(fields),
            ["author", "title", "journal", "year", "volume", "number", "pages"],
        )

    def test_string_macros_case_insensitive_and_chainable(self) -> None:
        bib = (
            '@string{AA = "Alpha"}\n'
            '@string{bb = aa # "-Beta"}\n'
            '@article{m, title = BB, year = 2000}\n'
        )
        result = self.tool.execute(mode="parse", bib=bib)
        self.assertEqual(
            result["entries"][0]["fields"]["title"], "Alpha-Beta"
        )

    def test_macro_must_be_defined_before_use(self) -> None:
        # A macro defined *after* the entry that references it fails,
        # exactly as in BibTeX, which processes files in one pass.
        bib = (
            '@article{m, title = aa, year = 2000}\n@string{aa = "Alpha"}\n'
        )
        result = self.tool.execute(mode="parse", bib=bib)
        self.assertEqual(result["error"]["type"], "undefined_macro")

    def test_comment_preamble_and_implicit_text_skipped(self) -> None:
        bib = (
            "free text with an email bob@host.domain here\n"
            "@comment{skip me}\n"
            '@preamble{"\\relax"}\n'
            "@article{only, year = 2001}\n"
        )
        result = self.tool.execute(mode="to_keys", bib=bib)
        self.assertEqual(result, {"mode": "to_keys", "count": 1, "keys": ["only"]})

    def test_file_with_no_entries(self) -> None:
        bib = '@comment{nothing}\n@string{x = "y"}\n@preamble{"z"}\n'
        result = self.tool.execute(mode="parse", bib=bib)
        self.assertEqual(
            result, {"mode": "parse", "count": 0, "entries": []}
        )

    def test_repeated_field_keeps_last_value(self) -> None:
        bib = "@article{r, year = 2000, year = 2001}\n"
        fields = self.tool.execute(mode="parse", bib=bib)["entries"][0]["fields"]
        self.assertEqual(fields["year"], "2001")

    def test_entry_without_fields(self) -> None:
        bib = "@misc{bare}\n@misc{withcomma,}\n"
        result = self.tool.execute(mode="parse", bib=bib)
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["entries"][0]["fields"], {})
        self.assertEqual(result["entries"][1]["fields"], {})

    def test_whitespace_only_bib_yields_zero_entries(self) -> None:
        result = self.tool.execute(mode="parse", bib="   \n\t\n")
        self.assertEqual(result["count"], 0)

    def test_editor_split_like_author(self) -> None:
        bib = '@book{ed, editor = {Smith, Alice and Bob Brown}, year = 1999}\n'
        fields = self.tool.execute(mode="parse", bib=bib)["entries"][0]["fields"]
        self.assertEqual(
            fields["editor"],
            [
                person("Alice", "Smith", "Smith, Alice"),
                person("Bob", "Brown", "Bob Brown"),
            ],
        )

    def test_three_comma_name_form(self) -> None:
        bib = '@book{jr, author = "Knuth, Jr., Donald E.", year = 1990}\n'
        fields = self.tool.execute(mode="parse", bib=bib)["entries"][0]["fields"]
        self.assertEqual(
            fields["author"],
            [person("Donald E.", "Knuth", "Knuth, Jr., Donald E.", jr="Jr.")],
        )

    def test_case_insensitive_and_separator(self) -> None:
        bib = (
            "@ARTICLE{Mixed, AUTHOR = {X Y AND Z W}, Year = 2005}\n"
        )
        fields = self.tool.execute(mode="parse", bib=bib)["entries"][0]["fields"]
        self.assertEqual(
            fields["author"],
            [person("X", "Y", "X Y"), person("Z", "W", "Z W")],
        )
        self.assertEqual(fields["year"], "2005")


class BibtexToolSummaryTest(unittest.TestCase):
    """Offline deterministic test cases for the summary mode."""

    def setUp(self) -> None:
        self.tool = BibtexTool()

    def test_summary_ground_truth(self) -> None:
        result = self.tool.execute(mode="summary", bib=SAMPLE_BIB)
        self.assertEqual(
            result,
            {
                "mode": "summary",
                "count": 5,
                "types": {
                    "article": 2,
                    "book": 1,
                    "inproceedings": 1,
                    "misc": 1,
                },
                "year_range": [1984, 2024],
                "entries": [
                    "Knuth, 1984, Literate Programming (Association for "
                    "Computing Machinery Transactions on Computer Systems)",
                    "Lamport, 1994, {LaTeX}: A Document Preparation System "
                    "(Addison Wesley)",
                    'Berners-Lee et al., 2001, The {"}Semantic{"} Web '
                    "(Scientific American)",
                    "Anonymous, 2024, The {B}ib{T}e{X} companion",
                    "Here, Paren-delimited entry without a year (J. Arbitrary)",
                ],
            },
        )

    def test_summary_no_years_yields_null_range(self) -> None:
        bib = "@misc{a, title = {No Year}}\n@misc{b, title = {Also None}}\n"
        result = self.tool.execute(mode="summary", bib=bib)
        self.assertIsNone(result["year_range"])
        self.assertEqual(result["count"], 2)

    def test_summary_editor_fallback_and_braced_organisation(self) -> None:
        bib = (
            "@book{b, editor = {{World Health Organization}}, "
            "title = {Guidelines}, year = 2020}\n"
        )
        result = self.tool.execute(mode="summary", bib=bib)
        self.assertEqual(
            result["entries"],
            ["World Health Organization, 2020, Guidelines"],
        )

    def test_summary_single_author_has_no_et_al(self) -> None:
        bib = "@article{one, author = {Jane Roe}, title = {Solo}, year = 2010}\n"
        result = self.tool.execute(mode="summary", bib=bib)
        self.assertEqual(result["entries"], ["Roe, 2010, Solo"])


class BibtexToolFilterTest(unittest.TestCase):
    """Offline deterministic test cases for the filter mode."""

    def setUp(self) -> None:
        self.tool = BibtexTool()

    def _keys(self, **matchers) -> list:
        result = self.tool.execute(mode="filter", bib=SAMPLE_BIB, **matchers)
        self.assertNotIn("error", result)
        return [entry["key"] for entry in result["entries"]]

    def test_filter_by_entry_type_case_insensitive(self) -> None:
        result = self.tool.execute(
            mode="filter", bib=SAMPLE_BIB, entry_type="ARTICLE"
        )
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["matchers"], {"entry_type": "article"})
        self.assertEqual(
            [entry["key"] for entry in result["entries"]],
            ["knuth1984", "nologic"],
        )

    def test_filter_by_query_against_key(self) -> None:
        self.assertEqual(self._keys(query="knuth"), ["knuth1984"])

    def test_filter_by_query_against_field_value(self) -> None:
        # 'latex' matches inside the *protected* title "{LaTeX}: ...".
        self.assertEqual(self._keys(query="latex"), ["lamport1994"])
        self.assertEqual(self._keys(query="scientific"), ["berners2001"])

    def test_filter_by_query_against_person_name(self) -> None:
        # Person names are matched via their raw form.
        self.assertEqual(self._keys(query="Hendler"), ["berners2001"])

    def test_filter_by_year_range(self) -> None:
        result = self.tool.execute(
            mode="filter", bib=SAMPLE_BIB, year_from=1990, year_to=2010
        )
        self.assertEqual(
            [entry["key"] for entry in result["entries"]],
            ["lamport1994", "berners2001"],
        )
        self.assertEqual(
            result["matchers"], {"year_from": 1990, "year_to": 2010}
        )

    def test_filter_year_bounds_are_inclusive(self) -> None:
        self.assertEqual(self._keys(year_from=1984, year_to=1984), ["knuth1984"])

    def test_filter_year_range_excludes_entries_without_year(self) -> None:
        self.assertEqual(self._keys(year_from=1984, year_to=2024),
                         ["knuth1984", "lamport1994", "berners2001", "bibtex2024"])

    def test_filter_matchers_combine_with_and(self) -> None:
        self.assertEqual(
            self._keys(entry_type="article", year_to=2000), ["knuth1984"]
        )

    def test_filter_no_match_yields_empty_result(self) -> None:
        result = self.tool.execute(mode="filter", bib=SAMPLE_BIB, query="zzz")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["entries"], [])

    def test_filter_year_bound_accepts_digit_string(self) -> None:
        result = self.tool.execute(
            mode="filter", bib=SAMPLE_BIB, year_from="2000"
        )
        self.assertEqual(
            [entry["key"] for entry in result["entries"]],
            ["berners2001", "bibtex2024"],
        )


class BibtexToolToKeysTest(unittest.TestCase):
    """Offline deterministic test cases for the to_keys mode."""

    def setUp(self) -> None:
        self.tool = BibtexTool()

    def test_to_keys_ground_truth_order(self) -> None:
        result = self.tool.execute(mode="to_keys", bib=SAMPLE_BIB)
        self.assertEqual(
            result,
            {
                "mode": "to_keys",
                "count": 5,
                "keys": [
                    "knuth1984",
                    "lamport1994",
                    "berners2001",
                    "bibtex2024",
                    "nologic",
                ],
            },
        )


class BibtexToolErrorMatrixTest(unittest.TestCase):
    """Content-level failures return structured errors with positions."""

    def setUp(self) -> None:
        self.tool = BibtexTool()

    def _error(self, bib: str, mode: str = "parse") -> dict:
        result = self.tool.execute(mode=mode, bib=bib)
        self.assertIn("error", result, msg=str(result))
        return result["error"]

    def test_unterminated_braced_value_position(self) -> None:
        bib = "@article{x,\n  author = {A},\n  title = {Unclosed\n"
        # The '{' opening the title value is the reported position.
        offset = bib.index("= {Unclosed") + 2
        error = self._error(bib)
        self.assertEqual(error["type"], "unbalanced_braces")
        self.assertEqual(error["position"], expected_position(bib, offset))
        self.assertIn("'}'", error["message"])

    def test_unterminated_quoted_value_position(self) -> None:
        # The quote never closes, so the '}' on the next line sits inside
        # the quoted value and is reported as an unbalanced brace.
        bib = '@article{y,\n  title = "no closing quote\n}\n'
        offset = bib.index("\n}") + 1
        error = self._error(bib)
        self.assertEqual(error["type"], "unbalanced_braces")
        self.assertEqual(error["position"], expected_position(bib, offset))

    def test_unbalanced_closer_inside_quoted_value(self) -> None:
        bib = '@article{z, title = "a } b", year = 2000}\n'
        offset = bib.index("a }") + 2
        error = self._error(bib)
        self.assertEqual(error["type"], "unbalanced_braces")
        self.assertEqual(error["position"], expected_position(bib, offset))

    def test_unterminated_entry_body(self) -> None:
        bib = "@article{open,\n  year = 2000,\n"
        # EOF inside the entry body: the entry's opening '{' is reported.
        offset = bib.index("{open")
        error = self._error(bib)
        self.assertEqual(error["type"], "unbalanced_braces")
        self.assertEqual(error["position"], expected_position(bib, offset))

    def test_undefined_macro_position(self) -> None:
        bib = "@article{u,\n  journal = nosuchmacro,\n  year = 2000}\n"
        offset = bib.index("nosuchmacro")
        error = self._error(bib)
        self.assertEqual(error["type"], "undefined_macro")
        self.assertIn("nosuchmacro", error["message"])
        self.assertEqual(error["position"], expected_position(bib, offset))

    def test_duplicate_key_position(self) -> None:
        bib = "@article{a, year = 2000}\n@book{a, title = {X}}\n"
        offset = bib.rindex("a,")  # the second, duplicated key
        error = self._error(bib)
        self.assertEqual(error["type"], "duplicate_key")
        self.assertIn("'a'", error["message"])
        self.assertEqual(error["position"], expected_position(bib, offset))

    def test_syntax_missing_equals_after_field_name(self) -> None:
        bib = "@article{m, year 2000}\n"
        offset = bib.index("2000")
        error = self._error(bib)
        self.assertEqual(error["type"], "syntax")
        self.assertEqual(error["position"], expected_position(bib, offset))

    def test_syntax_junk_after_citation_key(self) -> None:
        bib = "@article{s author = 1}\n"
        offset = bib.index("author")
        error = self._error(bib)
        self.assertEqual(error["type"], "syntax")
        self.assertEqual(error["position"], expected_position(bib, offset))

    def test_syntax_missing_field_value(self) -> None:
        bib = "@article{v, year = }\n"
        offset = bib.index("}")
        error = self._error(bib)
        self.assertEqual(error["type"], "syntax")
        self.assertEqual(error["position"], expected_position(bib, offset))

    def test_stray_at_word_is_skipped_not_an_error(self) -> None:
        bib = "contact bob@host.domain for details\n@article{ok, year = 2000}\n"
        result = self.tool.execute(mode="to_keys", bib=bib)
        self.assertEqual(result["keys"], ["ok"])

    def test_errors_surface_in_every_mode(self) -> None:
        bib = "@article{x, title = {Unclosed\n"
        for mode in ("parse", "summary", "filter", "to_keys"):
            kwargs = {"query": "x"} if mode == "filter" else {}
            result = self.tool.execute(mode=mode, bib=bib, **kwargs)
            self.assertEqual(result["mode"], mode)
            self.assertEqual(result["error"]["type"], "unbalanced_braces")


class BibtexToolValidationTest(unittest.TestCase):
    """Malformed parameters raise ValueError before any parsing."""

    def setUp(self) -> None:
        self.tool = BibtexTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="convert", bib=SAMPLE_BIB)
        self.assert_invalid(mode=None, bib=SAMPLE_BIB)
        self.assert_invalid(mode=123, bib=SAMPLE_BIB)

    def test_invalid_bib_type(self) -> None:
        for bad in (None, 123, True, b"@article{x}", ["@article{x}"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="parse", bib=bad)

    def test_empty_bib_rejected(self) -> None:
        self.assert_invalid(mode="parse", bib="")
        self.assert_invalid(mode="to_keys", bib="")

    def test_bib_length_limit(self) -> None:
        oversized = "@" + "a" * 1_000_001
        self.assert_invalid(mode="parse", bib=oversized)
        ok = self.tool.execute(mode="parse", bib="@a" + "a" * 999_998)
        self.assertEqual(ok["count"], 0)

    def test_filter_requires_at_least_one_matcher(self) -> None:
        self.assert_invalid(mode="filter", bib=SAMPLE_BIB)

    def test_filter_args_rejected_outside_filter_mode(self) -> None:
        self.assert_invalid(mode="parse", bib=SAMPLE_BIB, query="x")
        self.assert_invalid(mode="parse", bib=SAMPLE_BIB, entry_type="article")
        self.assert_invalid(mode="summary", bib=SAMPLE_BIB, year_from=2000)
        self.assert_invalid(mode="to_keys", bib=SAMPLE_BIB, year_to=2000)

    def test_filter_arg_types(self) -> None:
        self.assert_invalid(mode="filter", bib=SAMPLE_BIB, entry_type=123)
        self.assert_invalid(mode="filter", bib=SAMPLE_BIB, entry_type="")
        self.assert_invalid(mode="filter", bib=SAMPLE_BIB, query=True)
        self.assert_invalid(mode="filter", bib=SAMPLE_BIB, query="")
        self.assert_invalid(mode="filter", bib=SAMPLE_BIB, year_from="abc")
        self.assert_invalid(mode="filter", bib=SAMPLE_BIB, year_from=True)
        self.assert_invalid(mode="filter", bib=SAMPLE_BIB, year_to=1.5)


class BibtexToolPackagingTest(unittest.TestCase):
    """Class defaults and package registration."""

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectBibtexTool, BibtexTool)
        tool = BibtexTool()
        self.assertEqual(tool.name, "bibtex_tool")
        self.assertIn("BibTeX", tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("BibtexTool", __all__)


if __name__ == "__main__":
    unittest.main()
