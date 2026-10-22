#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Regression tests for financial event summary modes and LLM output."""

import unittest
from unittest.mock import Mock, patch

from agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator import (
    EventCluster, FinancialEventAggregator,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.llm.llm_output import LLMOutput


class TestFinancialEventSummarization(unittest.TestCase):
    def setUp(self) -> None:
        self.docs = [
            Document(text="Acme reports revenue growth in its quarterly results. First source."),
            Document(text="Acme reports revenue growth in its quarterly results. Second source."),
        ]
        self.processor = FinancialEventAggregator(
            name="financial_event_aggregator",
            use_embeddings=False,
            similarity_threshold=0.5,
            llm_name="test_llm",
            use_llm=True,
            summarization_mode="map_reduce",
        )

    def test_map_reduce_uses_both_sources_and_llm_output_text(self) -> None:
        llm = Mock()
        llm.call.side_effect = [
            LLMOutput(text="Acme revenue grew, according to source one."),
            LLMOutput(text="Source two confirms Acme revenue growth."),
            LLMOutput(text="Both sources report Acme revenue growth."),
        ]
        with patch.object(FinancialEventAggregator, "_get_llm", return_value=llm):
            output = self.processor._process_docs(self.docs)

        self.assertEqual(len(output), 1)
        self.assertEqual(output[0].text, "Both sources report Acme revenue growth.")
        self.assertEqual(output[0].metadata["source_count"], 2)
        self.assertEqual(llm.call.call_count, 3)
        final_prompt = llm.call.call_args.kwargs["messages"][0]["content"]
        self.assertIn("source one", final_prompt)
        self.assertIn("Source two", final_prompt)

    def test_extractive_mode_does_not_call_configured_llm(self) -> None:
        self.processor.summarization_mode = "extractive"
        with patch.object(FinancialEventAggregator, "_get_llm") as get_llm:
            output = self.processor._process_docs(self.docs)

        self.assertEqual(len(output), 1)
        self.assertIn("Acme reports", output[0].text)
        get_llm.assert_not_called()

    def test_empty_llm_output_falls_back_to_extractive_summary(self) -> None:
        llm = Mock()
        llm.call.return_value = LLMOutput(text="")
        with patch.object(FinancialEventAggregator, "_get_llm", return_value=llm):
            output = self.processor._process_docs(self.docs)

        self.assertEqual(len(output), 1)
        self.assertIn("Acme reports", output[0].text)

    def test_large_cluster_reduces_all_source_batches(self) -> None:
        docs = [Document(text=f"Article {index}") for index in range(1, 10)]
        llm = Mock()
        llm.call.side_effect = [
            LLMOutput(text=f"Mapped {index}") for index in range(1, 10)
        ] + [
            LLMOutput(text="Sources 1 through 8"),
            LLMOutput(text="All nine sources"),
        ]
        cluster = EventCluster(event_id="test", event_type="earnings")
        with patch.object(FinancialEventAggregator, "_get_llm", return_value=llm):
            summary = self.processor._generate_llm_summary(docs, cluster)

        self.assertEqual(summary, "All nine sources")
        self.assertEqual(llm.call.call_count, 11)
        final_prompt = llm.call.call_args.kwargs["messages"][0]["content"]
        self.assertIn("Sources 1-8", final_prompt)
        self.assertIn("Sources 9-9: Mapped 9", final_prompt)

    def test_unknown_mode_reports_configuration_error(self) -> None:
        self.processor.summarization_mode = "unknown"
        with self.assertRaisesRegex(ValueError, "Unknown summarization mode"):
            self.processor._process_docs(self.docs)

    def test_nonpositive_source_limit_reports_configuration_error(self) -> None:
        self.processor.max_sources_per_event = 0
        with self.assertRaisesRegex(ValueError, "max_sources_per_event must be positive"):
            self.processor._process_docs(self.docs)


if __name__ == "__main__":
    unittest.main()
