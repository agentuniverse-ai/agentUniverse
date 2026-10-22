#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_case_converter_tool.py

"""Offline unit tests for CaseConverterTool.

The tool is built purely on the standard library (re, unicodedata and
plain str methods) and never touches the network, so this suite runs
fully offline. Every assertion is deterministic: each mode is checked
against hand-written ground-truth conversions, the tokenizer against
known camel-hump / acronym / mixed-separator inputs, the title mode
against the small-word rule, and the slug mode against NFKD
diacritic-folding vectors. Validation failures are asserted against
the exact ValueError contract.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import CaseConverterTool
from agentuniverse.agent.action.tool.common_tool.case_converter_tool import (
    CaseConverterTool as DirectCaseConverterTool,
)

# A multi-word input mixing a camel hump, an acronym, a dash and an
# space; every identifier mode is asserted against this same input.
MIXED = "getHTTPResponse-code and more"


class CaseConverterToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib CaseConverterTool."""

    def setUp(self) -> None:
        self.tool = CaseConverterTool()

    # ------------------------------------------------------------------ #
    # Result shape and direct-module import
    # ------------------------------------------------------------------ #

    def test_direct_module_import_is_the_same_class(self) -> None:
        self.assertIs(CaseConverterTool, DirectCaseConverterTool)

    def test_result_shape(self) -> None:
        result = self.tool.execute(mode="upper", text="hello")
        self.assertEqual(result, {"mode": "upper", "result": "HELLO"})

    def test_tool_metadata(self) -> None:
        self.assertEqual(self.tool.name, "case_converter_tool")
        self.assertIn("HTTPServer", self.tool.description)
        self.assertIn("slug", self.tool.description)
        self.assertEqual(self.tool.max_text_chars, 100_000)

    # ------------------------------------------------------------------ #
    # upper / lower (unicode-aware, every character preserved)
    # ------------------------------------------------------------------ #

    def test_upper(self) -> None:
        result = self.tool.execute(mode="upper", text="hello World")
        self.assertEqual(result["result"], "HELLO WORLD")

    def test_lower(self) -> None:
        result = self.tool.execute(mode="lower", text="HELLO World")
        self.assertEqual(result["result"], "hello world")

    def test_upper_lower_unicode(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="lower", text="éTUDIANT ÅNGSTRÖM")["result"],
            "étudiant ångström",
        )
        self.assertEqual(
            self.tool.execute(mode="upper", text="étudiant ångström")["result"],
            "ÉTUDIANT ÅNGSTRÖM",
        )

    def test_cjk_passes_through_untouched_in_case_modes(self) -> None:
        # The fullwidth comma is deliberate test data for CJK text.
        for mode in ("upper", "lower", "title", "sentence"):
            result = self.tool.execute(mode=mode, text="你好，世界")  # noqa: RUF001
            self.assertEqual(result["result"], "你好，世界", msg=mode)  # noqa: RUF001

    def test_case_modes_preserve_separators(self) -> None:
        result = self.tool.execute(mode="upper", text="a-b_c  d.e/f")
        self.assertEqual(result["result"], "A-B_C  D.E/F")

    # ------------------------------------------------------------------ #
    # title mode (small words lowercase unless first or last)
    # ------------------------------------------------------------------ #

    def test_title_basic(self) -> None:
        result = self.tool.execute(mode="title", text="the lord of the rings")
        self.assertEqual(result["result"], "The Lord of the Rings")

    def test_title_small_words(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="title", text="war and peace")["result"],
            "War and Peace",
        )
        self.assertEqual(
            self.tool.execute(
                mode="title", text="a tale of two cities and an orphan"
            )["result"],
            "A Tale of Two Cities and an Orphan",
        )

    def test_title_small_word_last_is_capitalized(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="title", text="the state of")["result"],
            "The State Of",
        )

    def test_title_small_word_comparison_is_case_insensitive(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="title", text="THE CODE OF THE RING")["result"],
            "The Code of the Ring",
        )

    def test_title_preserves_punctuation_and_whitespace(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="title", text="hello, world! (again)")["result"],
            "Hello, World! (Again)",
        )
        self.assertEqual(
            self.tool.execute(mode="title", text="line one\nline\ttwo")["result"],
            "Line One\nLine\tTwo",
        )

    def test_title_uppercase_input_is_relowered(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="title", text="HELLO WORLD")["result"],
            "Hello World",
        )

    def test_title_unicode_and_cjk(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="title", text="éTUDIANT lazy")["result"],
            "Étudiant Lazy",
        )
        self.assertEqual(
            self.tool.execute(mode="title", text="hello 世界 test")["result"],
            "Hello 世界 Test",
        )

    def test_title_single_word(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="title", text="world")["result"], "World"
        )
        self.assertEqual(
            self.tool.execute(mode="title", text="the")["result"], "The"
        )

    # ------------------------------------------------------------------ #
    # sentence mode
    # ------------------------------------------------------------------ #

    def test_sentence_basic(self) -> None:
        result = self.tool.execute(mode="sentence", text="hello WORLD")
        self.assertEqual(result["result"], "Hello world")

    def test_sentence_leading_caseless_characters_pass_through(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="sentence", text='"quoted text" HERE')["result"],
            '"Quoted text" here',
        )
        self.assertEqual(
            self.tool.execute(mode="sentence", text="123 hello")["result"],
            "123 Hello",
        )

    def test_sentence_no_cased_character_is_unchanged(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="sentence", text="123 你好 !!!")["result"],
            "123 你好 !!!",
        )

    def test_sentence_preserves_separators(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="sentence", text="  SPACES   and\tTABS\n")["result"],
            "  Spaces   and\ttabs\n",
        )

    # ------------------------------------------------------------------ #
    # Identifier modes: ground truth on one mixed input
    # ------------------------------------------------------------------ #

    def test_snake_mixed_input(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="snake", text=MIXED)["result"],
            "get_http_response_code_and_more",
        )

    def test_kebab_mixed_input(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="kebab", text=MIXED)["result"],
            "get-http-response-code-and-more",
        )

    def test_camel_mixed_input(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="camel", text=MIXED)["result"],
            "getHttpResponseCodeAndMore",
        )

    def test_pascal_mixed_input(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="pascal", text=MIXED)["result"],
            "GetHttpResponseCodeAndMore",
        )

    def test_constant_mixed_input(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="constant", text=MIXED)["result"],
            "GET_HTTP_RESPONSE_CODE_AND_MORE",
        )

    def test_slug_mixed_input(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="slug", text=MIXED)["result"],
            "gethttpresponse-code-and-more",
        )

    # ------------------------------------------------------------------ #
    # Acronym / camel-hump handling
    # ------------------------------------------------------------------ #

    def test_acronym_hump_splitting(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="snake", text="HTTPServer")["result"],
            "http_server",
        )
        self.assertEqual(
            self.tool.execute(mode="camel", text="HTTPServer")["result"],
            "httpServer",
        )
        self.assertEqual(
            self.tool.execute(mode="pascal", text="HTTPServer")["result"],
            "HttpServer",
        )
        self.assertEqual(
            self.tool.execute(mode="constant", text="HTTPServer")["result"],
            "HTTP_SERVER",
        )
        self.assertEqual(
            self.tool.execute(mode="kebab", text="HTTPServer")["result"],
            "http-server",
        )

    def test_classic_xml_http_request(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="snake", text="XMLHttpRequest")["result"],
            "xml_http_request",
        )
        self.assertEqual(
            self.tool.execute(mode="camel", text="XMLHttpRequest")["result"],
            "xmlHttpRequest",
        )

    def test_lower_to_upper_hump_after_acronym(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="snake", text="getHTTPResponseCode")["result"],
            "get_http_response_code",
        )
        self.assertEqual(
            self.tool.execute(mode="snake", text="parseJSONData")["result"],
            "parse_json_data",
        )

    def test_digits_attach_to_the_preceding_word(self) -> None:
        # Boundaries exist only at lower->upper and acronym->word
        # transitions; digits never create a hump boundary.
        self.assertEqual(
            self.tool.execute(mode="snake", text="model2vec")["result"],
            "model2vec",
        )
        self.assertEqual(
            self.tool.execute(mode="snake", text="sha256Sum of file")["result"],
            "sha256sum_of_file",
        )
        self.assertEqual(
            self.tool.execute(mode="camel", text="model2vec rocks")["result"],
            "model2vecRocks",
        )

    def test_all_uppercase_single_concept_stays_one_word(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="snake", text="HTTP")["result"], "http"
        )

    # ------------------------------------------------------------------ #
    # Separator autodetection and already-delimited inputs
    # ------------------------------------------------------------------ #

    def test_already_snake_case_is_idempotent(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="snake", text="hello_world")["result"],
            "hello_world",
        )

    def test_already_kebab_case_is_idempotent(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="kebab", text="hello-world")["result"],
            "hello-world",
        )

    def test_already_camel_case_is_idempotent(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="camel", text="helloWorld")["result"],
            "helloWorld",
        )

    def test_already_pascal_case_is_idempotent(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="pascal", text="HelloWorld")["result"],
            "HelloWorld",
        )

    def test_already_constant_case_is_idempotent(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="constant", text="HELLO_WORLD")["result"],
            "HELLO_WORLD",
        )

    def test_already_slug_is_idempotent(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="slug", text="hello-world-2")["result"],
            "hello-world-2",
        )

    def test_delimited_to_camel_and_back(self) -> None:
        camel = self.tool.execute(mode="camel", text="hello_world")["result"]
        self.assertEqual(camel, "helloWorld")
        self.assertEqual(
            self.tool.execute(mode="snake", text=camel)["result"], "hello_world"
        )
        kebab = self.tool.execute(mode="kebab", text=camel)["result"]
        self.assertEqual(kebab, "hello-world")

    def test_spaces_to_snake(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="snake", text="Hello World Example")["result"],
            "hello_world_example",
        )

    def test_repeated_and_mixed_separators_collapse(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="snake", text="  Mixed__input--with   spaces  "
            )["result"],
            "mixed_input_with_spaces",
        )

    def test_other_punctuation_is_a_separator_in_identifier_modes(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="snake", text="Hello, World!")["result"],
            "hello_world",
        )
        self.assertEqual(
            self.tool.execute(mode="kebab", text="a.b/c")["result"], "a-b-c"
        )

    def test_identifier_mode_without_alphanumerics(self) -> None:
        for mode in ("snake", "kebab", "camel", "pascal", "constant", "slug"):
            result = self.tool.execute(mode=mode, text="--- !!! ???")
            self.assertEqual(result["result"], "", msg=mode)

    def test_cjk_words_are_kept_in_identifier_modes(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="snake", text="你好 world")["result"],
            "你好_world",
        )
        self.assertEqual(
            self.tool.execute(mode="camel", text="你好 world")["result"],
            "你好World",
        )

    def test_unicode_word_casing_in_identifier_modes(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="snake", text="José Müller")["result"],
            "josé_müller",
        )
        self.assertEqual(
            self.tool.execute(mode="pascal", text="josé müller")["result"],
            "JoséMüller",
        )

    # ------------------------------------------------------------------ #
    # slug mode (NFKD ascii-fold)
    # ------------------------------------------------------------------ #

    def test_slug_folds_diacritics(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="slug", text="José")["result"], "jose"
        )
        self.assertEqual(
            self.tool.execute(mode="slug", text="Café con Leché")["result"],
            "cafe-con-leche",
        )
        self.assertEqual(
            self.tool.execute(mode="slug", text="José MÜLLER")["result"],
            "jose-muller",
        )

    def test_slug_non_alnum_to_single_trimmed_dash(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="slug", text="Hello, World!!!")["result"],
            "hello-world",
        )
        self.assertEqual(
            self.tool.execute(mode="slug", text="-- leading and trailing --")["result"],
            "leading-and-trailing",
        )
        self.assertEqual(
            self.tool.execute(mode="slug", text="a_b c")["result"], "a-b-c"
        )

    def test_slug_keeps_cjk(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="slug", text="Hello 世界!")["result"],
            "hello-世界",
        )

    def test_slug_folds_fullwidth_ascii(self) -> None:
        # NFKD maps fullwidth latin to their ASCII counterparts; the
        # fullwidth letters are deliberate test data.
        self.assertEqual(
            self.tool.execute(mode="slug", text="ＨＥＬＬＯ")["result"],  # noqa: RUF001
            "hello",
        )

    def test_slug_digits_and_mixed(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="slug", text="Top 10 café bars (2026)")["result"],
            "top-10-cafe-bars-2026",
        )

    # ------------------------------------------------------------------ #
    # Validation error matrix
    # ------------------------------------------------------------------ #

    def test_unknown_mode_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="Title", text="hello")
        self.assertIn("case_converter_tool:", str(ctx.exception))
        self.assertIn("mode must be one of", str(ctx.exception))
        self.assertIn("'Title'", str(ctx.exception))

    def test_empty_text_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="snake", text="")
        self.assertIn("text must be a non-empty string", str(ctx.exception))

    def test_missing_text_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="snake")
        self.assertIn("text must be a non-empty string", str(ctx.exception))

    def test_non_string_text_raises(self) -> None:
        for bad in (None, 123, 4.5, True, ["a"], {"a": 1}):
            with self.assertRaises(ValueError, msg=repr(bad)):
                self.tool.execute(mode="upper", text=bad)

    def test_bool_text_is_rejected(self) -> None:
        # bool is an int subclass; it must not slip through as "True".
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="upper", text=True)
        self.assertIn("text must be a non-empty string", str(ctx.exception))

    def test_oversized_text_raises(self) -> None:
        big = "a" * 100_001
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="snake", text=big)
        self.assertIn("100,000-character limit", str(ctx.exception))
        self.assertIn("100,001", str(ctx.exception))

    def test_boundary_length_is_accepted(self) -> None:
        result = self.tool.execute(mode="lower", text="A" * 100_000)
        self.assertEqual(len(result["result"]), 100_000)

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_conversions_are_deterministic(self) -> None:
        for mode in CaseConverterTool.MODES:
            first = self.tool.execute(mode=mode, text=MIXED)
            second = self.tool.execute(mode=mode, text=MIXED)
            self.assertEqual(first, second, msg=mode)


if __name__ == "__main__":
    unittest.main()
