#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for ProfanityFilter DocProcessor."""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.profanity_filter \
    import ProfanityFilter
from agentuniverse.agent.action.knowledge.store.document import Document


class TestProfanityFilter(unittest.TestCase):

    def _filter(self, docs, **kwargs):
        proc = ProfanityFilter(**kwargs)
        return proc.process_docs(docs, None)

    # ------------------------------------------------------------------ #
    # drop action
    # ------------------------------------------------------------------ #
    def test_drop_removes_profane_document(self):
        # "shit" is 1 of 2 words -> ratio 0.5 >= 0.05 -> dropped.
        docs = [Document(text="this shit")]
        result = self._filter(docs, action="drop")
        self.assertEqual(len(result), 0)

    def test_drop_keeps_clean_document(self):
        docs = [Document(text="a clean sentence about programming")]
        result = self._filter(docs, action="drop")
        self.assertEqual(len(result), 1)

    def test_drop_threshold_respected(self):
        # 1 profane word of 20 total -> ratio 0.05. threshold 0.5 keeps it.
        text = "damn " + "word " * 19
        docs = [Document(text=text.strip())]
        result = self._filter(docs, action="drop", threshold=0.5)
        self.assertEqual(len(result), 1)
        # Same text with a low threshold drops it.
        result2 = self._filter(docs, action="drop", threshold=0.01)
        self.assertEqual(len(result2), 0)

    # ------------------------------------------------------------------ #
    # mask action
    # ------------------------------------------------------------------ #
    def test_mask_replaces_profane_word(self):
        docs = [Document(text="what the fuck")]
        result = self._filter(docs, action="mask", replacement="***")
        self.assertEqual(len(result), 1)
        self.assertNotIn("fuck", result[0].text)
        self.assertIn("***", result[0].text)
        self.assertIn("what the", result[0].text)

    def test_mask_custom_replacement(self):
        docs = [Document(text="you bastard")]
        result = self._filter(docs, action="mask", replacement="[BLEEP]")
        self.assertIn("[BLEEP]", result[0].text)
        self.assertNotIn("bastard", result[0].text)

    def test_mask_preserves_clean_text(self):
        original = "a perfectly clean sentence"
        docs = [Document(text=original)]
        result = self._filter(docs, action="mask")
        self.assertEqual(result[0].text, original)

    # ------------------------------------------------------------------ #
    # redact action
    # ------------------------------------------------------------------ #
    def test_redact_keeps_text_but_stamps_summary(self):
        original = "this is bullshit"
        docs = [Document(text=original)]
        result = self._filter(docs, action="redact")
        self.assertEqual(len(result), 1)
        # Text unchanged.
        self.assertEqual(result[0].text, original)
        # Summary stamped.
        summary = result[0].metadata["profanity_summary"]
        self.assertIn("bullshit", summary["words"])
        self.assertGreater(summary["count"], 0)

    # ------------------------------------------------------------------ #
    # matching behaviour
    # ------------------------------------------------------------------ #
    def test_whole_word_only_avoids_substring_false_positive(self):
        # "class" and "glass" contain "ass" but must NOT match.
        docs = [Document(text="the glass and class are clean")]
        result = self._filter(docs, action="mask")
        self.assertEqual(result[0].text, "the glass and class are clean")

    def test_case_insensitive_matching(self):
        docs = [Document(text="WHAT THE FUCK")]
        result = self._filter(docs, action="mask")
        self.assertNotIn("FUCK", result[0].text)
        self.assertIn("***", result[0].text)

    def test_leet_substitution_matched(self):
        # "sh1t" style obfuscation -> "1" normalises to "i" -> "shit".
        docs = [Document(text="you sh1t")]
        result = self._filter(docs, action="mask")
        self.assertNotIn("sh1t", result[0].text)
        self.assertIn("***", result[0].text)

    def test_substring_mode_matches_inside_words(self):
        # With whole_word_only off, "ass" matches inside "class".
        docs = [Document(text="the class is nice")]
        result = self._filter(docs, action="mask", whole_word_only=False,
                              extra_words=["ass"])
        self.assertIn("***", result[0].text)

    def test_extra_words_merged(self):
        docs = [Document(text="you are a zorbot")]
        result = self._filter(docs, action="mask",
                              extra_words=["zorbot"])
        self.assertNotIn("zorbot", result[0].text)

    # ------------------------------------------------------------------ #
    # edge cases / metadata
    # ------------------------------------------------------------------ #
    def test_empty_input(self):
        proc = ProfanityFilter(action="mask")
        self.assertEqual(proc.process_docs([], None), [])

    def test_empty_text_kept(self):
        docs = [Document(text="")]
        result = self._filter(docs, action="drop")
        self.assertEqual(len(result), 1)

    def test_preserves_original_metadata(self):
        doc = Document(text="clean text", metadata={"source": "wiki"})
        result = self._filter([doc], action="mask")
        self.assertEqual(result[0].metadata["source"], "wiki")

    def test_summary_ratio_and_count(self):
        docs = [Document(text="fuck shit damn")]  # 3 profane of 3 -> ratio 1.0
        result = self._filter(docs, action="redact")
        summary = result[0].metadata["profanity_summary"]
        self.assertEqual(summary["count"], 3)
        self.assertAlmostEqual(summary["ratio"], 1.0)

    def test_summary_key_omitted_when_empty(self):
        docs = [Document(text="clean text")]
        result = self._filter(docs, action="redact", summary_key="")
        self.assertNotIn("profanity_summary", result[0].metadata or {})

    def test_invalid_action_raises(self):
        proc = ProfanityFilter(action="nonsense")
        with self.assertRaises(ValueError):
            proc.process_docs([Document(text="hi")], None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
