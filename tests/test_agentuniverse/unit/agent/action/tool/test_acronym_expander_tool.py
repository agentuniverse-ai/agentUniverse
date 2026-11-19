#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_acronym_expander_tool.py

"""Offline unit tests for AcronymExpanderTool.

The tool is built purely on the standard library and never touches
the network, so this suite runs fully offline. Every assertion is
deterministic: detection results (acronyms, counts, first-occurrence
spans) are checked against hand-computed ground truths including
boundary, digit, caps-lock-guard and mixed-case cases; glossary
resolution is checked against literal expansions with user-glossary
precedence and unknown marking; replacement is checked against exact
expected strings including the first-occurrence-only rule and the
idempotent second-pass guard.
"""

import os
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import (
    AcronymExpanderTool,
    acronym_expander_tool as acronym_expander_module,
)
from agentuniverse.agent.action.tool.common_tool.acronym_expander_tool import (
    _BUILTIN_GLOSSARY,
    _BUILTIN_LOOKUP,
    AcronymExpanderTool as DirectAcronymExpanderTool,
)

YAML_PATH = os.path.join(
    os.path.dirname(os.path.abspath(acronym_expander_module.__file__)),
    "acronym_expander_tool.yaml",
)


class AcronymExpanderToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib AcronymExpanderTool."""

    def setUp(self) -> None:
        self.tool = AcronymExpanderTool()

    # ------------------------------------------------------------------ #
    # detect mode — ground truths
    # ------------------------------------------------------------------ #

    def test_detect_basic_spans_and_payload(self) -> None:
        result = self.tool.execute(
            mode="detect", text="The API talks to the LLM over HTTP."
        )
        self.assertEqual(
            result,
            {
                "mode": "detect",
                "result": ["API", "LLM", "HTTP"],
                "acronyms": [
                    {
                        "acronym": "API",
                        "count": 1,
                        "first_span": {"start": 4, "end": 7},
                    },
                    {
                        "acronym": "LLM",
                        "count": 1,
                        "first_span": {"start": 21, "end": 24},
                    },
                    {
                        "acronym": "HTTP",
                        "count": 1,
                        "first_span": {"start": 30, "end": 34},
                    },
                ],
                "acronym_count": 3,
                "caps_lock_paragraphs_skipped": 0,
            },
        )

    def test_detect_counts_and_first_span_with_repeats(self) -> None:
        result = self.tool.execute(
            mode="detect", text="RAG helps. More RAG, more RAG."
        )
        self.assertEqual(result["result"], ["RAG"])
        self.assertEqual(result["acronym_count"], 1)
        self.assertEqual(
            result["acronyms"][0],
            {
                "acronym": "RAG",
                "count": 3,
                "first_span": {"start": 0, "end": 3},
            },
        )

    def test_detect_letters_with_digits(self) -> None:
        result = self.tool.execute(
            mode="detect",
            text="A9, GPT4 and MP3 players use A1234567 rarely.",
        )
        # A1234567 is rejected: 1 letter + 7 digits exceeds the
        # 6-character total-length cap.
        self.assertEqual(result["result"], ["A9", "GPT4", "MP3"])

    def test_detect_length_bounds(self) -> None:
        result = self.tool.execute(
            mode="detect", text="ABCDEF ok but ABCDEFG is too long."
        )
        # Exactly six uppercase letters match; seven do not (and the
        # truncated 6-letter prefix is suppressed as well).
        self.assertEqual(result["result"], ["ABCDEF"])
        self.assertEqual(result["acronyms"][0]["first_span"], {"start": 0, "end": 6})

    def test_detect_single_letters_ignored(self) -> None:
        result = self.tool.execute(mode="detect", text="I saw a B movie.")
        self.assertEqual(result["result"], [])
        self.assertEqual(result["acronym_count"], 0)

    def test_detect_boundary_rules(self) -> None:
        # "USAir": the USA run is followed by a lowercase letter.
        # "theAPI" / "macOSAPI": camelCase tails produce no partial
        # matches (a preceding letter of any case disqualifies).
        # "APIs": a lowercase plural tail disqualifies the run.
        for text in (
            "USAir merged long ago.",
            "theAPI is camelCase.",
            "macOSAPI as well.",
            "APIs are plural.",
        ):
            with self.subTest(text=text):
                result = self.tool.execute(mode="detect", text=text)
                self.assertEqual(result["result"], [])
                self.assertEqual(result["acronym_count"], 0)

    def test_detect_underscore_identifiers_skipped(self) -> None:
        result = self.tool.execute(
            mode="detect", text="Set API_KEY and NEXT_TOKEN vars."
        )
        self.assertEqual(result["result"], [])
        self.assertEqual(result["acronym_count"], 0)

    def test_detect_mixed_case_short_forms_not_detected(self) -> None:
        result = self.tool.execute(
            mode="detect", text="K8s, OAuth, SaaS, NoSQL and GraphQL rock."
        )
        self.assertEqual(result["result"], [])
        self.assertEqual(result["acronym_count"], 0)

    def test_detect_caps_lock_guard(self) -> None:
        text = "THE API IS GREAT\nThe API is fine\nANOTHER SHOUTING LINE"
        result = self.tool.execute(mode="detect", text=text)
        # Paragraphs (lines) 0 and 2 are shouting (>60% uppercase
        # letters) and are skipped entirely; only line 1 contributes.
        self.assertEqual(result["result"], ["API"])
        self.assertEqual(result["caps_lock_paragraphs_skipped"], 2)
        self.assertEqual(
            result["acronyms"][0]["first_span"], {"start": 21, "end": 24}
        )

    def test_detect_caps_lock_threshold_is_strict(self) -> None:
        # 3 of 5 letters uppercase = exactly 60%: NOT guarded.
        result = self.tool.execute(mode="detect", text="ABC de")
        self.assertEqual(result["result"], ["ABC"])
        self.assertEqual(result["caps_lock_paragraphs_skipped"], 0)
        # 4 of 5 letters uppercase = 80%: guarded.
        guarded = self.tool.execute(mode="detect", text="ABCD e")
        self.assertEqual(guarded["result"], [])
        self.assertEqual(guarded["caps_lock_paragraphs_skipped"], 1)

    def test_detect_sees_inside_parentheticals(self) -> None:
        # detect reports every acronym, including those inside
        # parentheticals (in contrast to the replace-mode guard).
        result = self.tool.execute(
            mode="detect", text="The JWT (JSON Web Token) is standard."
        )
        self.assertEqual(result["result"], ["JWT", "JSON"])
        self.assertEqual(
            [entry["first_span"] for entry in result["acronyms"]],
            [{"start": 4, "end": 7}, {"start": 9, "end": 13}],
        )

    # ------------------------------------------------------------------ #
    # expand mode — glossary resolution
    # ------------------------------------------------------------------ #

    def test_expand_builtin_payload(self) -> None:
        result = self.tool.execute(mode="expand", acronyms=["API"])
        self.assertEqual(
            result,
            {
                "mode": "expand",
                "result": [
                    {
                        "acronym": "API",
                        "canonical": "API",
                        "expansion": "Application Programming Interface",
                        "source": "builtin",
                    }
                ],
                "expansion_count": 1,
                "unknown_count": 0,
                "user_glossary_size": 0,
            },
        )

    def test_expand_builtin_common_terms(self) -> None:
        result = self.tool.execute(
            mode="expand", acronyms=["HTTP", "LLM", "RAG", "ETL", "CRUD"]
        )
        expected = {
            "HTTP": "Hypertext Transfer Protocol",
            "LLM": "Large Language Model",
            "RAG": "Retrieval-Augmented Generation",
            "ETL": "Extract, Transform, Load",
            "CRUD": "Create, Read, Update, Delete",
        }
        for entry in result["result"]:
            self.assertEqual(entry["source"], "builtin")
            self.assertEqual(entry["expansion"], expected[entry["acronym"]])
        self.assertEqual(result["unknown_count"], 0)

    def test_expand_case_insensitive_canonical_forms(self) -> None:
        result = self.tool.execute(
            mode="expand", acronyms=["k8s", "K8S", "oauth", "NOSQL", "rag"]
        )
        by_acronym = {entry["acronym"]: entry for entry in result["result"]}
        self.assertEqual(by_acronym["k8s"]["canonical"], "K8s")
        self.assertEqual(by_acronym["K8S"]["canonical"], "K8s")
        self.assertEqual(by_acronym["k8s"]["expansion"], "Kubernetes")
        self.assertEqual(by_acronym["oauth"]["canonical"], "OAuth")
        self.assertEqual(by_acronym["NOSQL"]["canonical"], "NoSQL")
        self.assertEqual(by_acronym["rag"]["canonical"], "RAG")
        self.assertEqual(by_acronym["rag"]["expansion"], "Retrieval-Augmented Generation")

    def test_expand_cd_is_flagged_ambiguous(self) -> None:
        result = self.tool.execute(mode="expand", acronyms=["CD", "CI"])
        cd_entry, ci_entry = result["result"]
        self.assertEqual(cd_entry["expansion"], "Continuous Delivery")
        self.assertTrue(cd_entry["ambiguous"])
        self.assertEqual(
            cd_entry["alternatives"],
            ["Continuous Deployment", "Compact Disc"],
        )
        # Only ambiguous entries carry the flag / alternatives keys.
        self.assertNotIn("ambiguous", ci_entry)
        self.assertNotIn("alternatives", ci_entry)
        self.assertEqual(ci_entry["expansion"], "Continuous Integration")

    def test_expand_user_glossary_wins(self) -> None:
        result = self.tool.execute(
            mode="expand",
            acronyms=["API", "RAG", "ZZQQ"],
            glossary={
                "API": "American Petroleum Institute",
                "zzqq": "Zone Quotient",
            },
        )
        by_acronym = {entry["acronym"]: entry for entry in result["result"]}
        self.assertEqual(
            by_acronym["API"],
            {
                "acronym": "API",
                "expansion": "American Petroleum Institute",
                "source": "user_glossary",
            },
        )
        self.assertEqual(
            by_acronym["ZZQQ"],
            {
                "acronym": "ZZQQ",
                "expansion": "Zone Quotient",
                "source": "user_glossary",
            },
        )
        # Untouched by the user glossary: still the builtin answer.
        self.assertEqual(by_acronym["RAG"]["source"], "builtin")
        self.assertEqual(by_acronym["RAG"]["expansion"], "Retrieval-Augmented Generation")
        self.assertEqual(result["user_glossary_size"], 2)
        self.assertEqual(result["unknown_count"], 0)

    def test_expand_unknown_marking(self) -> None:
        result = self.tool.execute(
            mode="expand", acronyms=["ZZQQ", "RAGs", "GraphQL", "IoT"]
        )
        # ZZQQ is simply absent from both glossaries; RAGs is unknown
        # because plural stripping is deliberately not performed;
        # GraphQL and IoT are deliberately not in the builtin glossary.
        self.assertEqual(result["unknown_count"], 4)
        for entry in result["result"]:
            self.assertEqual(entry["source"], "unknown")
            self.assertIsNone(entry["expansion"])
            self.assertNotIn("canonical", entry)

    def test_expand_accepts_separator_string(self) -> None:
        result = self.tool.execute(mode="expand", acronyms="API, LLM JSON")
        self.assertEqual(
            [entry["acronym"] for entry in result["result"]],
            ["API", "LLM", "JSON"],
        )
        self.assertEqual(result["expansion_count"], 3)

    # ------------------------------------------------------------------ #
    # replace mode — first occurrence only + idempotence
    # ------------------------------------------------------------------ #

    def test_replace_first_occurrence_only(self) -> None:
        text = "The API is nice. The API is stable."
        result = self.tool.execute(mode="replace", text=text)
        self.assertEqual(
            result["result"],
            "The API (Application Programming Interface) is nice. "
            "The API is stable.",
        )
        self.assertEqual(result["replacement_count"], 1)
        self.assertEqual(
            result["replacements"],
            [
                {
                    "acronym": "API",
                    "expansion": "Application Programming Interface",
                    "paragraph": 0,
                    "start": 4,
                }
            ],
        )

    def test_replace_is_idempotent(self) -> None:
        text = "The API is nice. The API is stable."
        first = self.tool.execute(mode="replace", text=text)
        second = self.tool.execute(mode="replace", text=first["result"])
        self.assertEqual(second["result"], first["result"])
        self.assertEqual(second["replacement_count"], 0)

    def test_replace_multiple_acronyms(self) -> None:
        result = self.tool.execute(mode="replace", text="API meets LLM")
        self.assertEqual(
            result["result"],
            "API (Application Programming Interface) meets "
            "LLM (Large Language Model)",
        )
        self.assertEqual(result["replacement_count"], 2)

    def test_replace_idempotent_when_expansion_contains_acronyms(self) -> None:
        # "JSON Web Token" itself contains the acronym JSON; the
        # parenthetical guard keeps the second pass stable.  (The
        # prose around the acronyms keeps the caps ratio low enough
        # to stay clear of the caps-lock guard.)
        first = self.tool.execute(mode="replace", text="The JWT and the JSON")
        self.assertEqual(
            first["result"],
            "The JWT (JSON Web Token) and the JSON "
            "(JavaScript Object Notation)",
        )
        second = self.tool.execute(mode="replace", text=first["result"])
        self.assertEqual(second["result"], first["result"])
        self.assertEqual(second["replacement_count"], 0)

    def test_replace_unknown_acronyms_left_alone(self) -> None:
        result = self.tool.execute(
            mode="replace", text="The API and the ZZQQ walk in."
        )
        self.assertEqual(
            result["result"],
            "The API (Application Programming Interface) and the ZZQQ "
            "walk in.",
        )
        self.assertEqual(result["replacement_count"], 1)

    def test_replace_user_glossary_wins(self) -> None:
        result = self.tool.execute(
            mode="replace",
            text="API here",
            glossary={"API": "American Petroleum Institute"},
        )
        self.assertEqual(
            result["result"], "API (American Petroleum Institute) here"
        )

    def test_replace_skips_caps_lock_paragraph(self) -> None:
        text = "THE API IS GREAT\nThe API is fine."
        result = self.tool.execute(mode="replace", text=text)
        self.assertEqual(
            result["result"],
            "THE API IS GREAT\n"
            "The API (Application Programming Interface) is fine.",
        )
        self.assertEqual(result["caps_lock_paragraphs_skipped"], 1)
        self.assertEqual(result["replacements"][0]["paragraph"], 1)

    def test_replace_already_annotated_acronym_is_untouched(self) -> None:
        # An acronym immediately followed by a parenthetical counts
        # as already expanded, so nothing is replaced anywhere.
        text = "The API (v2) and API docs"
        result = self.tool.execute(mode="replace", text=text)
        self.assertEqual(result["result"], text)
        self.assertEqual(result["replacement_count"], 0)

    def test_replace_plural_forms_untouched(self) -> None:
        # No plural stripping: APIs / RAGs are not detected and not
        # replaced.
        text = "The APIs and RAGs stay as they are."
        result = self.tool.execute(mode="replace", text=text)
        self.assertEqual(result["result"], text)
        self.assertEqual(result["replacement_count"], 0)

    def test_replace_detect_consistent_boundaries(self) -> None:
        # USAir / API_KEY / mixed-case forms are neither detected
        # nor replaced, mirroring the detect rules.
        text = "USAir and API_KEY plus K8s remain unchanged."
        result = self.tool.execute(mode="replace", text=text)
        self.assertEqual(result["result"], text)
        self.assertEqual(result["replacement_count"], 0)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="detective", text="hello")
        self.assert_invalid(mode=None, text="hello")
        self.assert_invalid(mode=123, text="hello")
        self.assert_invalid(mode="DETECT", text="hello")

    def test_invalid_text(self) -> None:
        for bad in (None, 123, True, b"hello", ["hello"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="detect", text=bad)
                self.assert_invalid(mode="replace", text=bad)
        self.assert_invalid(mode="detect", text="")
        self.assert_invalid(mode="replace", text="")

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(mode="detect", text=oversized)
        self.assert_invalid(mode="replace", text=oversized)
        ok = self.tool.execute(mode="detect", text="a" * 100_000)
        self.assertEqual(ok["acronym_count"], 0)

    def test_invalid_acronyms(self) -> None:
        for bad in (
            None,
            [],
            "",
            "   ",
            123,
            {"API": 1},
            [123],
            [None],
            [True],
            [""],
            [" "],
            ["A" * 65],
        ):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="expand", acronyms=bad)
        self.assert_invalid(mode="expand", acronyms=["ok"] * 1001)

    def test_invalid_glossary(self) -> None:
        for bad in (
            ["API"],
            "API",
            123,
            True,
            {1: "x"},
            {"A": 1},
            {"A": None},
            {"A": True},
            {"": "x"},
            {" ": "x"},
            {"A": ""},
            {"A": "   "},
            {"RAG": "first", "rag": "second"},
        ):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="expand", acronyms=["API"], glossary=bad)
                self.assert_invalid(mode="replace", text="API", glossary=bad)
        self.assert_invalid(
            mode="expand",
            acronyms=["API"],
            glossary={f"KEY{i}": "value" for i in range(1001)},
        )

    def test_same_value_glossary_duplicates_accepted(self) -> None:
        result = self.tool.execute(
            mode="expand",
            acronyms=["RAG"],
            glossary={"RAG": "Red Amber Green", "rag": "Red Amber Green"},
        )
        self.assertEqual(result["user_glossary_size"], 1)
        self.assertEqual(
            result["result"][0]["expansion"], "Red Amber Green"
        )

    # ------------------------------------------------------------------ #
    # Built-in glossary integrity / packaging
    # ------------------------------------------------------------------ #

    def test_builtin_glossary_integrity(self) -> None:
        # ~60 entries, all with non-empty expansions.
        self.assertEqual(len(_BUILTIN_GLOSSARY), 62)
        self.assertEqual(len(_BUILTIN_LOOKUP), 62)
        for canonical, entry in _BUILTIN_GLOSSARY.items():
            with self.subTest(acronym=canonical):
                self.assertTrue(
                    isinstance(entry["expansion"], str) and entry["expansion"]
                )
        # Every builtin key round-trips through the expand mode.
        result = self.tool.execute(
            mode="expand", acronyms=sorted(_BUILTIN_LOOKUP)
        )
        self.assertEqual(result["unknown_count"], 0)
        self.assertEqual(result["expansion_count"], len(_BUILTIN_LOOKUP))

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectAcronymExpanderTool, AcronymExpanderTool)
        self.assertEqual(self.tool.name, "acronym_expander_tool")
        self.assertIn("detect", self.tool.description)
        self.assertIn("replace", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("AcronymExpanderTool", __all__)

    def test_yaml_registration_file(self) -> None:
        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "acronym_expander_tool")
        self.assertEqual(config["tool_type"], "api")
        self.assertEqual(config["metadata"]["type"], "TOOL")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.acronym_expander_tool",
        )
        self.assertEqual(config["metadata"]["class"], "AcronymExpanderTool")
        self.assertEqual(config["input_keys"], ["mode"])
        self.assertEqual(
            config["args_model_schema"]["properties"]["mode"]["enum"],
            ["detect", "expand", "replace"],
        )
        self.assertEqual(
            config["args_model_schema"]["required"], ["mode"]
        )


if __name__ == "__main__":
    unittest.main()
