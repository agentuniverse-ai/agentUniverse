#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for SummarizationProcessor.

Covers the extractive fallback (deterministic, no LLM), query-aware boosting,
CJK handling, input bounding, metadata, and the LLM mode via a mocked LLM.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from agentuniverse.agent.action.knowledge.doc_processor.summarization_processor import (
    SummarizationProcessor,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class TestExtractiveSummarization(unittest.TestCase):
    """Tests for the dependency-free extractive summarizer."""

    def test_empty_input_returns_empty(self) -> None:
        """No documents → no output documents."""
        proc = SummarizationProcessor()
        self.assertEqual(proc._process_docs([]), [])

    def test_short_input_returned_unchanged(self) -> None:
        """Text with at most max_sentences is returned (stripped) as-is."""
        proc = SummarizationProcessor(max_sentences=5)
        docs = [Document(text="One sentence. Two sentence.")]
        out = proc._process_docs(docs)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].text, "One sentence. Two sentence.")

    def test_extractive_reduces_length(self) -> None:
        """More sentences than max_sentences are compressed to fewer."""
        text = ". ".join(f"sentence number {i}" for i in range(20))
        proc = SummarizationProcessor(max_sentences=3, query_aware=False)
        out = proc._process_docs([Document(text=text)])
        self.assertEqual(len(out), 1)
        # The summary should be materially shorter than the original.
        self.assertLess(len(out[0].text), len(text))

    def test_high_frequency_sentence_is_kept(self) -> None:
        """Sentences dense in a repeated term survive the cut."""
        text = (
            "alpha alpha alpha alpha."
            " irrelevant filler line one."
            " irrelevant filler line two."
            " irrelevant filler line three."
            " irrelevant filler line four."
        )
        proc = SummarizationProcessor(max_sentences=2, query_aware=False)
        out = proc._process_docs([Document(text=text)])
        self.assertIn("alpha alpha alpha alpha", out[0].text)

    def test_query_aware_boost(self) -> None:
        """A query term boosts an otherwise low-frequency sentence."""
        text = (
            "alpha alpha alpha alpha."
            " the climate report is long."
            " filler line one."
            " filler line two."
            " filler line three."
        )
        proc = SummarizationProcessor(max_sentences=2, query_aware=True)
        out = proc._process_docs([Document(text=text)], Query(query_str="climate"))
        # High-frequency sentence is kept.
        self.assertIn("alpha alpha alpha alpha", out[0].text)
        # Query-relevant sentence is kept even though its terms are rare.
        self.assertIn("the climate report is long", out[0].text)

    def test_cjk_handling(self) -> None:
        """CJK text is summarized by single-ideograph frequency."""
        text = (
            "苹果非常好吃。"
            "苹果富含营养。"
            "我喜欢吃苹果。"
            "香蕉是黄色的。"
            "葡萄是紫色的。"
            "橙子是橙色的。"
            "西瓜很大。"
        )
        proc = SummarizationProcessor(max_sentences=2, query_aware=True)
        out = proc._process_docs([Document(text=text)], Query(query_str="苹果"))
        # At least one 苹果-bearing sentence is kept.
        self.assertTrue("苹果" in out[0].text)

    def test_metadata_records_mode_and_count(self) -> None:
        """Output metadata records the mode, source count, and llm_name."""
        docs = [Document(text="a. b. c. d. e. f. g.")]
        proc = SummarizationProcessor(max_sentences=2)
        out = proc._process_docs(docs)
        self.assertEqual(out[0].metadata["summarization_mode"], "extractive")
        self.assertEqual(out[0].metadata["source_doc_count"], 1)
        self.assertIsNone(out[0].metadata["llm_name"])

    def test_metadata_carryover_from_source(self) -> None:
        """Non-conflicting metadata from the first source doc is carried over."""
        docs = [Document(text="a. b. c. d. e. f. g.", metadata={"knowledge": "kb1", "src": "web"})]
        proc = SummarizationProcessor(max_sentences=2)
        out = proc._process_docs(docs)
        self.assertEqual(out[0].metadata["knowledge"], "kb1")
        self.assertEqual(out[0].metadata["src"], "web")

    def test_max_input_docs_caps_sources(self) -> None:
        """Only the first max_input_docs documents are counted as sources."""
        docs = [Document(text=f"sentence {i}." + " filler." * 10) for i in range(15)]
        proc = SummarizationProcessor(max_input_docs=4, max_sentences=2)
        out = proc._process_docs(docs)
        self.assertEqual(out[0].metadata["source_doc_count"], 4)

    def test_order_preserved_in_output(self) -> None:
        """Kept sentences appear in their original document order."""
        text = (
            "zzz zzz zzz zzz."
            " a low importance line here."
            " yyy yyy yyy yyy."
            " another low line here."
            " yet another low line here."
        )
        proc = SummarizationProcessor(max_sentences=2, query_aware=False)
        out = proc._process_docs([Document(text=text)])
        summary = out[0].text
        # The two high-frequency sentences (idx 0 and idx 2) are selected, and
        # idx 0 must appear before idx 2 in the output.
        self.assertLess(summary.index("zzz"), summary.index("yyy"))


class TestLLMSummarization(unittest.TestCase):
    """Tests for the LLM (abstractive) summarizer mode."""

    def test_llm_mode_uses_model_output(self) -> None:
        """With llm_name set, the summary text comes from the LLM call."""
        mock_llm = Mock()
        mock_llm.call.return_value = Mock(text="A concise LLM summary.")
        proc = SummarizationProcessor(llm_name="fake_llm", query_aware=True)
        with patch.object(proc, "_get_llm", return_value=mock_llm):
            out = proc._process_docs([Document(text="doc one. doc two.")])
        self.assertEqual(out[0].text, "A concise LLM summary.")
        self.assertEqual(out[0].metadata["summarization_mode"], "llm")
        self.assertEqual(out[0].metadata["llm_name"], "fake_llm")

    def test_llm_mode_injects_query_focus(self) -> None:
        """A query is injected into the prompt when query_aware is set."""
        mock_llm = Mock()
        mock_llm.call.return_value = Mock(text="summary")
        proc = SummarizationProcessor(llm_name="fake_llm", query_aware=True)
        with patch.object(proc, "_get_llm", return_value=mock_llm):
            proc._process_docs([Document(text="some retrieved text.")], Query(query_str="climate"))
        _, kwargs = mock_llm.call.call_args
        prompt_content = " ".join(m["content"] for m in kwargs["messages"])
        self.assertIn("climate", prompt_content)

    def test_llm_mode_custom_instruction_used(self) -> None:
        """A custom summary_instruction is passed through to the prompt."""
        mock_llm = Mock()
        mock_llm.call.return_value = Mock(text="summary")
        proc = SummarizationProcessor(
            llm_name="fake_llm",
            summary_instruction="Produce bullet points only.",
            query_aware=False,
        )
        with patch.object(proc, "_get_llm", return_value=mock_llm):
            proc._process_docs([Document(text="text.")])
        _, kwargs = mock_llm.call.call_args
        prompt_content = " ".join(m["content"] for m in kwargs["messages"])
        self.assertIn("Produce bullet points only.", prompt_content)

    def test_get_llm_raises_when_missing(self) -> None:
        """A clear error is raised when the named LLM cannot be resolved."""
        from agentuniverse.llm.llm_manager import LLMManager
        proc = SummarizationProcessor(llm_name="does_not_exist")
        with patch.object(LLMManager, "get_instance_obj", return_value=None):
            with self.assertRaises(ValueError):
                proc._get_llm()


class TestConfigLoading(unittest.TestCase):
    """Tests for _initialize_by_component_configer."""

    def test_config_fields_loaded(self) -> None:
        """Configer attributes are mapped onto the processor fields."""
        proc = SummarizationProcessor()
        configer = SimpleNamespace(
            name="my_summarizer",
            description="desc",
            llm_name="my_llm",
            max_input_docs=7,
            max_sentences=9,
            query_aware=False,
            summary_instruction="custom",
            language="Chinese",
        )
        proc._initialize_by_component_configer(configer)
        self.assertEqual(proc.name, "my_summarizer")
        self.assertEqual(proc.llm_name, "my_llm")
        self.assertEqual(proc.max_input_docs, 7)
        self.assertEqual(proc.max_sentences, 9)
        self.assertFalse(proc.query_aware)
        self.assertEqual(proc.summary_instruction, "custom")
        self.assertEqual(proc.language, "Chinese")

    def test_config_defaults_when_absent(self) -> None:
        """Missing optional attributes leave the defaults intact."""
        proc = SummarizationProcessor()
        configer = SimpleNamespace(name="n", description="d")
        proc._initialize_by_component_configer(configer)
        self.assertEqual(proc.max_sentences, 5)
        self.assertTrue(proc.query_aware)
        self.assertIsNone(proc.llm_name)


if __name__ == '__main__':
    unittest.main()
