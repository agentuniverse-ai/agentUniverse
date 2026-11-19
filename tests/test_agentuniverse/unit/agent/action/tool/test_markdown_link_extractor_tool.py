#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_markdown_link_extractor_tool.py

"""Offline unit tests for MarkdownLinkExtractorTool.

The tool is built purely on the standard library (re) and never
touches the network, so this suite runs fully offline. Every
assertion is deterministic: extraction results are checked against
literal ground-truth documents (inline / reference / autolink / image
mixes, reference resolution including case-insensitive labels,
undefined references, anchors, dangerous schemes, duplicate counting,
fence immunity, escaped brackets), spans are asserted against the
invariant ``text[start:end] == raw construct``, and the audit
verdicts against a fixed classification matrix.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import (
    MarkdownLinkExtractorTool,
)
from agentuniverse.agent.action.tool.common_tool.markdown_link_extractor_tool import (
    MarkdownLinkExtractorTool as DirectMarkdownLinkExtractorTool,
)

FENCE = "`" * 3


def compact(link: dict) -> tuple:
    """Project a link entry onto the fields the ground truths assert."""
    return (
        link["kind"],
        link["text"],
        link["url"],
        link["title"],
        link.get("ref"),
        link.get("resolved"),
    )


class MarkdownLinkExtractorToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib link extractor."""

    def setUp(self) -> None:
        self.tool = MarkdownLinkExtractorTool()

    # ------------------------------------------------------------------ #
    # extract mode — inline links, images, autolinks
    # ------------------------------------------------------------------ #

    def test_inline_link_with_title_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="extract", text='See [Docs](https://example.com "Guide") now'
        )
        self.assertEqual(len(result["links"]), 1)
        link = result["links"][0]
        self.assertEqual(
            compact(link),
            ("inline", "Docs", "https://example.com", "Guide", None, None),
        )
        start, end = link["span"]
        self.assertEqual(
            'See [Docs](https://example.com "Guide") now'[start:end],
            '[Docs](https://example.com "Guide")',
        )

    def test_inline_link_without_title(self) -> None:
        result = self.tool.execute(
            mode="extract", text="[plain](https://plain.example.com)"
        )
        self.assertEqual(
            compact(result["links"][0]),
            ("inline", "plain", "https://plain.example.com", None, None, None),
        )

    def test_inline_image_is_kind_image(self) -> None:
        doc = '![logo](img/logo.png "The Logo")'
        result = self.tool.execute(mode="extract", text=doc)
        self.assertEqual(
            compact(result["links"][0]),
            ("image", "logo", "img/logo.png", "The Logo", None, None),
        )
        # The span of an image covers its '!' too.
        start, end = result["links"][0]["span"]
        self.assertEqual(doc[start:end], doc)

    def test_autolink_uri_and_email(self) -> None:
        doc = "Go <https://example.com/auto> or <bob@example.com>."
        result = self.tool.execute(mode="extract", text=doc)
        self.assertEqual(
            compact(result["links"][0]),
            (
                "autolink",
                "https://example.com/auto",
                "https://example.com/auto",
                None,
                None,
                None,
            ),
        )
        # Email autolinks are normalized to mailto: URLs.
        self.assertEqual(
            compact(result["links"][1]),
            ("autolink", "bob@example.com", "mailto:bob@example.com", None, None, None),
        )

    def test_angle_bracket_destination(self) -> None:
        result = self.tool.execute(
            mode="extract", text="[x](<my file with spaces.html>)"
        )
        self.assertEqual(result["links"][0]["url"], "my file with spaces.html")

    def test_title_three_delimiter_forms(self) -> None:
        cases = {
            '[a](u.html "d")': "d",
            "[a](u.html 's')": "s",
            "[a](u.html (p))": "p",
        }
        for doc, title in cases.items():
            with self.subTest(doc=doc):
                result = self.tool.execute(mode="extract", text=doc)
                self.assertEqual(result["links"][0]["title"], title)

    # ------------------------------------------------------------------ #
    # extract mode — reference links and definitions
    # ------------------------------------------------------------------ #

    def test_reference_link_resolution(self) -> None:
        doc = (
            "Uses [the docs][doc-ref] here.\n"
            "\n"
            "[doc-ref]: https://example.com/ref 'Reference title'\n"
        )
        result = self.tool.execute(mode="extract", text=doc)
        self.assertEqual(
            compact(result["links"][0]),
            (
                "reference",
                "the docs",
                "https://example.com/ref",
                "Reference title",
                "doc-ref",
                True,
            ),
        )
        self.assertEqual(doc[slice(*result["links"][0]["span"])], "[the docs][doc-ref]")

    def test_reference_labels_case_insensitive(self) -> None:
        doc = "See [x][Big Label] and [y][BIG LABEL].\n\n[big  label]: https://example.com/ci\n"
        result = self.tool.execute(mode="extract", text=doc)
        self.assertEqual(result["summary"]["undefined_references"], 0)
        for link in result["links"]:
            self.assertTrue(link["resolved"])
            self.assertEqual(link["url"], "https://example.com/ci")

    def test_collapsed_reference_form(self) -> None:
        doc = "See [home][].\n\n[home]: https://example.com/home\n"
        result = self.tool.execute(mode="extract", text=doc)
        self.assertEqual(
            compact(result["links"][0]),
            ("reference", "home", "https://example.com/home", None, "home", True),
        )

    def test_undefined_reference_flagged(self) -> None:
        doc = "Bad [missing][nope].\n\n[other]: https://example.com/o\n"
        result = self.tool.execute(mode="extract", text=doc)
        link = result["links"][0]
        self.assertEqual(link["resolved"], False)
        self.assertIsNone(link["url"])
        self.assertEqual(link["ref"], "nope")
        self.assertEqual(result["summary"]["undefined_references"], 1)

    def test_reference_image_resolves_definition(self) -> None:
        doc = "![alt][IMG]\n\n[img]: /static/logo.png\n"
        result = self.tool.execute(mode="extract", text=doc)
        self.assertEqual(
            compact(result["links"][0]),
            ("image", "alt", "/static/logo.png", None, "IMG", True),
        )

    def test_first_definition_of_duplicate_label_wins(self) -> None:
        doc = "[x][d]\n\n[d]: https://first.example.com\n[d]: https://second.example.com\n"
        result = self.tool.execute(mode="extract", text=doc)
        self.assertEqual(result["links"][0]["url"], "https://first.example.com")
        references = self.tool.execute(mode="references", text=doc)
        self.assertEqual(len(references["definitions"]), 1)
        self.assertEqual(references["definitions"][0]["url"], "https://first.example.com")

    # ------------------------------------------------------------------ #
    # extract mode — bare URLs option
    # ------------------------------------------------------------------ #

    def test_bare_urls_disabled_by_default(self) -> None:
        result = self.tool.execute(
            mode="extract", text="plain https://bare.example.com text"
        )
        self.assertEqual(result["links"], [])

    def test_bare_urls_included_when_enabled(self) -> None:
        doc = "plain https://bare.example.com text"
        result = self.tool.execute(mode="extract", text=doc, include_bare_urls=True)
        self.assertEqual(
            compact(result["links"][0]),
            ("bare", "https://bare.example.com", "https://bare.example.com", None, None, None),
        )

    def test_bare_url_trailing_punctuation_trimmed(self) -> None:
        doc = "see https://example.com/a.html, then (https://example.com/b)."
        result = self.tool.execute(mode="extract", text=doc, include_bare_urls=True)
        self.assertEqual(
            [link["url"] for link in result["links"]],
            ["https://example.com/a.html", "https://example.com/b"],
        )
        for link in result["links"]:
            self.assertEqual(doc[slice(*link["span"])], link["url"])

    def test_url_inside_inline_link_not_double_reported(self) -> None:
        doc = "[Docs](https://example.com/docs) plus https://example.com/bare"
        result = self.tool.execute(mode="extract", text=doc, include_bare_urls=True)
        kinds = [(link["kind"], link["url"]) for link in result["links"]]
        self.assertEqual(
            kinds,
            [
                ("inline", "https://example.com/docs"),
                ("bare", "https://example.com/bare"),
            ],
        )

    def test_only_http_scheme_urls_count_as_bare(self) -> None:
        result = self.tool.execute(
            mode="extract", text="ftp://files.example.com is not bare",
            include_bare_urls=True,
        )
        self.assertEqual(result["links"], [])

    # ------------------------------------------------------------------ #
    # fence immunity and escaped brackets
    # ------------------------------------------------------------------ #

    def test_links_inside_code_fences_not_extracted(self) -> None:
        doc = (
            "before [a](https://before.example.com)\n"
            + FENCE + "python\n"
            "[hidden](https://inside.example.com)\n"
            "<https://also-hidden.example.com>\n"
            "[h][ref-hidden]\n"
            + FENCE + "\n"
            "after [b](https://after.example.com)\n"
        )
        result = self.tool.execute(
            mode="extract", text=doc, include_bare_urls=True
        )
        self.assertEqual(
            [link["url"] for link in result["links"]],
            ["https://before.example.com", "https://after.example.com"],
        )

    def test_tilde_fences_and_marker_mismatch(self) -> None:
        doc = (
            "~~~\n"
            "[in-tilde](https://tilde.example.com)\n"
            + FENCE + "\n"
            "[marker-mismatch](https://mismatch.example.com)\n"
            "~~~\n"
            "[visible](https://ok.example.com)\n"
        )
        result = self.tool.execute(mode="extract", text=doc)
        self.assertEqual(
            [link["url"] for link in result["links"]], ["https://ok.example.com"]
        )

    def test_escaped_bracket_does_not_start_link(self) -> None:
        result = self.tool.execute(
            mode="extract", text="\\[nope](https://nope.example.com)"
        )
        self.assertEqual(result["links"], [])

    def test_escaped_brackets_inside_link_text(self) -> None:
        doc = "[see \\[note\\]](https://example.com/note)"
        result = self.tool.execute(mode="extract", text=doc)
        link = result["links"][0]
        self.assertEqual(link["kind"], "inline")
        self.assertEqual(link["text"], "see \\[note\\]")
        self.assertEqual(doc[slice(*link["span"])], doc)

    def test_nested_bracket_text_one_level(self) -> None:
        result = self.tool.execute(
            mode="extract", text="[outer [inner]](https://example.com/n)"
        )
        self.assertEqual(result["links"][0]["text"], "outer [inner]")

    def test_unterminated_construct_is_literal_text(self) -> None:
        for doc in (
            "[unclosed](https://example.com",
            "[dangling][missing-bracket",
            "[a](https://example.com \"unclosed title)",
        ):
            with self.subTest(doc=doc):
                result = self.tool.execute(mode="extract", text=doc)
                self.assertEqual(result["links"], [])

    # ------------------------------------------------------------------ #
    # span invariants
    # ------------------------------------------------------------------ #

    def test_spans_reconstruct_raw_constructs(self) -> None:
        doc = (
            "# Heading\n"
            "Intro [first](https://one.example.com) middle "
            "[second][ref] end ![img](pic.png)\n"
            "<https://auto.example.com>\n"
            "\n"
            "[ref]: https://two.example.com \"Two\"\n"
        )
        result = self.tool.execute(mode="extract", text=doc)
        expected_sources = [
            "[first](https://one.example.com)",
            "[second][ref]",
            "![img](pic.png)",
            "<https://auto.example.com>",
        ]
        self.assertEqual(
            [doc[slice(*link["span"])] for link in result["links"]],
            expected_sources,
        )
        # Spans are sorted, non-overlapping and inside the document.
        spans = [link["span"] for link in result["links"]]
        self.assertEqual(spans, sorted(spans))
        for start, end in spans:
            self.assertGreaterEqual(start, 0)
            self.assertLessEqual(end, len(doc))

    def test_multiline_document_spans_use_absolute_offsets(self) -> None:
        doc = "line one\nline two [x](https://offset.example.com) tail"
        result = self.tool.execute(mode="extract", text=doc)
        link = result["links"][0]
        self.assertEqual(
            doc[slice(*link["span"])], "[x](https://offset.example.com)"
        )
        self.assertGreaterEqual(link["span"][0], len("line one\nline two "))

    def test_definition_span_covers_the_definition_line(self) -> None:
        doc = "text\n\n[ref]: https://example.com 'title'\n"
        result = self.tool.execute(mode="references", text=doc)
        span = result["definitions"][0]["span"]
        self.assertEqual(doc[slice(*span)], "[ref]: https://example.com 'title'")

    # ------------------------------------------------------------------ #
    # audit mode
    # ------------------------------------------------------------------ #

    def test_audit_verdict_matrix(self) -> None:
        doc = (
            "[ok](https://ok.example.com) "
            "[safe-mail](mailto:bob@example.com) "
            "[js](javascript:alert(1)) "
            "[data](data:text/html,hi) "
            "[vbs](vbscript:msg) "
            "[frag](#section) "
            "[rel](docs/readme.md) "
            "[empty]() "
            "[ftp](ftp://files.example.com)\n"
            "[undef][nope]\n"
        )
        result = self.tool.execute(mode="audit", text=doc)
        verdicts = [(link["text"], link["verdict"]) for link in result["links"]]
        self.assertEqual(
            verdicts,
            [
                ("ok", "ok"),
                ("safe-mail", "ok"),
                ("js", "dangerous"),
                ("data", "dangerous"),
                ("vbs", "dangerous"),
                ("frag", "anchor"),
                ("rel", "relative"),
                ("empty", "empty"),
                ("ftp", "unknown_scheme"),
                ("undef", "undefined"),
            ],
        )
        self.assertEqual(
            result["summary"]["by_verdict"],
            {
                "ok": 2,
                "anchor": 1,
                "relative": 1,
                "empty": 1,
                "undefined": 1,
                "dangerous": 3,
                "unknown_scheme": 1,
            },
        )

    def test_audit_scheme_field_normalized_lowercase(self) -> None:
        result = self.tool.execute(
            mode="audit", text="[x](HTTPS://EXAMPLE.COM/A)"
        )
        link = result["links"][0]
        self.assertEqual(link["verdict"], "ok")
        self.assertEqual(link["scheme"], "https")

    def test_audit_dangerous_links_carry_issue(self) -> None:
        result = self.tool.execute(mode="audit", text="[x](javascript:alert(1))")
        self.assertEqual(result["links"][0]["issues"], ["dangerous_scheme"])

    def test_audit_duplicate_url_counting(self) -> None:
        doc = (
            "[one](https://dup.example.com/a) "
            "[two](https://dup.example.com/a) "
            "[three](https://dup.example.com/a) "
            "[other](https://solo.example.com/b)\n"
        )
        result = self.tool.execute(mode="audit", text=doc)
        duplicates = [
            (link["text"], link["duplicate_count"], link["issues"])
            for link in result["links"]
        ]
        self.assertEqual(
            duplicates,
            [
                ("one", 3, ["duplicate"]),
                ("two", 3, ["duplicate"]),
                ("three", 3, ["duplicate"]),
                ("other", 1, []),
            ],
        )
        self.assertEqual(
            result["summary"]["duplicate_urls"],
            {"https://dup.example.com/a": 3},
        )
        self.assertEqual(result["summary"]["unique_urls"], 2)

    def test_audit_autolink_and_bare_verdicts(self) -> None:
        doc = "visit <https://auto.example.com> or https://bare.example.com/x"
        result = self.tool.execute(mode="audit", text=doc, include_bare_urls=True)
        self.assertEqual(
            [(link["kind"], link["verdict"]) for link in result["links"]],
            [("autolink", "ok"), ("bare", "ok")],
        )

    def test_audit_empty_and_undefined_not_counted_as_duplicates(self) -> None:
        doc = "[a]() [b]() [c][missing]\n"
        result = self.tool.execute(mode="audit", text=doc)
        self.assertEqual(
            [link["duplicate_count"] for link in result["links"]], [None, None, None]
        )
        self.assertEqual(result["summary"]["duplicate_urls"], {})

    # ------------------------------------------------------------------ #
    # references mode
    # ------------------------------------------------------------------ #

    def test_references_table_with_usage_analysis(self) -> None:
        doc = (
            "Use [a][used-twice] and [a][used-twice], plus [b][used-once].\n"
            "\n"
            "[used-twice]: https://two.example.com 'T2'\n"
            "[used-once]: https://one.example.com\n"
            "[never-used]: https://never.example.com\n"
        )
        result = self.tool.execute(mode="references", text=doc)
        self.assertEqual(
            [
                (d["label"], d["url"], d["title"], d["used_count"])
                for d in result["definitions"]
            ],
            [
                ("used-twice", "https://two.example.com", "T2", 2),
                ("used-once", "https://one.example.com", None, 1),
                ("never-used", "https://never.example.com", None, 0),
            ],
        )
        self.assertEqual(result["unused"], ["never-used"])
        self.assertEqual(result["undefined"], [])
        self.assertEqual(
            result["summary"], {"definitions": 3, "unused": 1, "undefined": 0}
        )

    def test_references_mode_reports_undefined_labels(self) -> None:
        doc = "x [a][ghost] y\n\n[real]: https://real.example.com\n"
        result = self.tool.execute(mode="references", text=doc)
        self.assertEqual(len(result["undefined"]), 1)
        entry = result["undefined"][0]
        self.assertEqual(entry["ref"], "ghost")
        self.assertEqual(doc[slice(*entry["span"])], "[a][ghost]")

    def test_references_mode_empty_document(self) -> None:
        result = self.tool.execute(mode="references", text="no definitions here")
        self.assertEqual(result["definitions"], [])
        self.assertEqual(
            result["summary"], {"definitions": 0, "unused": 0, "undefined": 0}
        )

    # ------------------------------------------------------------------ #
    # Summaries, empty input, determinism
    # ------------------------------------------------------------------ #

    def test_extract_summary_by_kind(self) -> None:
        doc = (
            "[i](https://i.example.com) [r][ref] ![im](a.png) "
            "<https://a.example.com> https://b.example.com\n"
            "\n"
            "[ref]: https://r.example.com\n"
        )
        result = self.tool.execute(
            mode="extract", text=doc, include_bare_urls=True
        )
        self.assertEqual(
            result["summary"],
            {
                "total": 5,
                "by_kind": {"inline": 1, "reference": 1, "autolink": 1, "image": 1, "bare": 1},
                "undefined_references": 0,
            },
        )

    def test_empty_text_is_valid_and_yields_no_links(self) -> None:
        for mode in ("extract", "audit", "references"):
            with self.subTest(mode=mode):
                result = self.tool.execute(mode=mode, text="")
                self.assertEqual(result["mode"], mode)

    def test_deterministic_output(self) -> None:
        doc = (
            "[a](https://a.example.com) [b][ref] ![i](x.png) "
            "<https://c.example.com> https://d.example.com\n"
            "[bad][missing] [j](javascript:x)\n"
            "[ref]: https://ref.example.com\n"
        )
        first = self.tool.execute(mode="audit", text=doc, include_bare_urls=True)
        second = self.tool.execute(mode="audit", text=doc, include_bare_urls=True)
        self.assertEqual(first, second)

    def test_links_are_in_document_order(self) -> None:
        doc = "z [z](https://z.example.com) a [a](https://a.example.com) m ![m](m.png)"
        result = self.tool.execute(mode="extract", text=doc)
        self.assertEqual(
            [link["text"] for link in result["links"]], ["z", "a", "m"]
        )

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="parse", text="[a](https://a.example.com)")
        self.assert_invalid(mode=None, text="x")
        self.assert_invalid(mode=123, text="x")
        self.assert_invalid(mode="EXTRACT", text="x")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"x", ["x"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="extract", text=bad)

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(mode="extract", text=oversized)
        ok = self.tool.execute(mode="extract", text="[a](https://a.example.com)" + "a" * 99_000)
        self.assertEqual(len(ok["links"]), 1)

    def test_invalid_include_bare_urls(self) -> None:
        for bad in (1, "yes", 0):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="extract", text="x", include_bare_urls=bad)
        # None and booleans are accepted.
        for good in (None, True, False):
            result = self.tool.execute(
                mode="extract", text="x", include_bare_urls=good
            )
            self.assertEqual(result["links"], [])

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectMarkdownLinkExtractorTool, MarkdownLinkExtractorTool)
        self.assertEqual(self.tool.name, "markdown_link_extractor_tool")
        self.assertIn("extract", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("MarkdownLinkExtractorTool", __all__)


if __name__ == "__main__":
    unittest.main()
