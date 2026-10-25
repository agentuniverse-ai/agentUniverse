# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_bounded_query_paraphraser.py

"""Known-answer and discipline tests for BoundedQueryParaphraser.

Mirrors the union of the public surfaces the two competitor paraphrasers
(#3322 HyDE, #3325 multi-query) expose: both strategies, provenance keys,
bundle discipline, best-effort fallback, and loud ValueError-quoted
configuration errors — including through the real component-configer loader
and the Knowledge._paraphrase_query manager seam.
"""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import agentuniverse.agent.action.knowledge.knowledge as knowledge_module
import agentuniverse.agent.action.knowledge.query_paraphraser.bounded_query_paraphraser as bqp_module
import agentuniverse.llm.llm_manager as llm_manager_module
from agentuniverse.agent.action.knowledge.query_paraphraser.bounded_query_paraphraser import (
    BoundedQueryParaphraser,
)
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

_LOGGER_NAME = "agentuniverse.agent.action.knowledge.query_paraphraser.bounded_query_paraphraser"
_YAML_PATH = os.path.join(os.path.dirname(bqp_module.__file__),
                          "bounded_query_paraphraser.yaml")


def _fake_llm(*texts: str):
    llm = MagicMock()
    llm.call.side_effect = [SimpleNamespace(text=t) for t in texts]
    return llm


def _paraphrase(query_str, llm, **kwargs) -> Query:
    fields = {"llm_model": "fake_llm"}
    fields.update(kwargs)
    paraphraser = BoundedQueryParaphraser(**fields)
    with patch.object(llm_manager_module, "LLMManager") as manager:
        manager.return_value.get_instance_obj.return_value = llm
        return paraphraser.query_paraphrase(Query(query_str=query_str))


class TestHyDEStrategy(unittest.TestCase):
    """strategy='hyde': passages, blank-line join, one call per passage."""

    def test_append_keeps_original_then_passage(self) -> None:
        query = _paraphrase("What is PEER?", _fake_llm("PEER is a pattern."))
        self.assertEqual(query.query_str, "What is PEER?\nPEER is a pattern.")

    def test_replace_uses_passages_only(self) -> None:
        query = _paraphrase("What is PEER?", _fake_llm("PEER is a pattern."),
                            mode="replace")
        self.assertEqual(query.query_str, "PEER is a pattern.")

    def test_two_passages_joined_by_blank_line(self) -> None:
        query = _paraphrase("q", _fake_llm("first passage", "second passage"),
                            num_docs=2)
        self.assertEqual(query.query_str, "q\nfirst passage\n\nsecond passage")

    def test_ext_info_records_original_and_passages(self) -> None:
        query = _paraphrase("What is PEER?", _fake_llm("PEER is a pattern."))
        self.assertEqual(query.ext_info["paraphrase_origin_query_str"], "What is PEER?")
        self.assertEqual(query.ext_info["paraphrase_hyde_documents"], ["PEER is a pattern."])

    def test_origin_key_is_setdefault_first_expansion_wins(self) -> None:
        original = Query(query_str="What is PEER?",
                         ext_info={"paraphrase_origin_query_str": "already there"})
        paraphraser = BoundedQueryParaphraser(llm_model="fake_llm")
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = _fake_llm("PEER is a pattern.")
            out = paraphraser.query_paraphrase(original)
        self.assertEqual(out.ext_info["paraphrase_origin_query_str"], "already there")

    def test_passages_appended_to_bundles_without_duplicates(self) -> None:
        original = Query(query_str="q", query_text_bundles=["PEER is a pattern."])
        paraphraser = BoundedQueryParaphraser(llm_model="fake_llm", num_docs=2)
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = _fake_llm(
                "PEER is a pattern.", "second passage")
            out = paraphraser.query_paraphrase(original)
        self.assertEqual(out.query_text_bundles, ["PEER is a pattern.", "second passage"])

    def test_passage_truncated_to_max_doc_chars(self) -> None:
        query = _paraphrase("q", _fake_llm("a" * 50), max_doc_chars=10)
        self.assertEqual(query.ext_info["paraphrase_hyde_documents"], ["a" * 10])

    def test_duplicate_passages_are_deduplicated(self) -> None:
        query = _paraphrase("q", _fake_llm("same passage", "same passage"), num_docs=2)
        self.assertEqual(query.ext_info["paraphrase_hyde_documents"], ["same passage"])

    def test_partial_failure_keeps_usable_passage(self) -> None:
        llm = MagicMock()
        llm.call.side_effect = [RuntimeError("boom"), SimpleNamespace(text="kept passage")]
        query = _paraphrase("q", llm, num_docs=2)
        self.assertEqual(query.ext_info["paraphrase_hyde_documents"], ["kept passage"])

    def test_other_query_fields_untouched(self) -> None:
        original = Query(query_str="q", keywords={"k"}, similarity_top_k=7)
        paraphraser = BoundedQueryParaphraser(llm_model="fake_llm")
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = _fake_llm("passage")
            out = paraphraser.query_paraphrase(original)
        self.assertEqual(out.keywords, {"k"})
        self.assertEqual(out.similarity_top_k, 7)
        self.assertEqual(out.embeddings, [])


class TestMultiStrategy(unittest.TestCase):
    """strategy='multi': ONE call, decoration stripped, folded dedupe, capped."""

    def test_one_llm_call_variants_stripped_and_capped(self) -> None:
        llm = _fake_llm("1. variant one\n2) variant two\n3、 variant three\n"
                        "- variant four\n* variant five\n• variant six\n“quoted”")
        query = _paraphrase("How do I reset X?", llm, strategy="multi", num_queries=4)
        llm.call.assert_called_once()
        self.assertEqual(query.ext_info["paraphrase_multi_variants"],
                         ["variant one", "variant two", "variant three", "variant four"])
        self.assertEqual(query.query_str,
                         "How do I reset X?\nvariant one\nvariant two\nvariant three\nvariant four")

    def test_lines_equal_to_original_are_dropped_casefolded(self) -> None:
        query = _paraphrase("Same", _fake_llm("1. same\n2. SAME\n3. other"),
                            strategy="multi")
        self.assertEqual(query.ext_info["paraphrase_multi_variants"], ["other"])

    def test_iso_dates_survive_the_numbering_stripper(self) -> None:
        query = _paraphrase("q", _fake_llm("2026-01-01), noting\nOK, fine"),
                            strategy="multi")
        self.assertEqual(query.ext_info["paraphrase_multi_variants"],
                         ["2026-01-01), noting", "OK, fine"])

    def test_duplicate_variants_folded_and_deduplicated(self) -> None:
        query = _paraphrase("q", _fake_llm("  One 2 3\none 2 3\nTwo 3 4"),
                            strategy="multi")
        self.assertEqual(query.ext_info["paraphrase_multi_variants"],
                         ["One 2 3", "Two 3 4"])

    def test_variant_truncated_to_max_query_chars(self) -> None:
        query = _paraphrase("q", _fake_llm("b" * 40), strategy="multi",
                            max_query_chars=5)
        self.assertEqual(query.ext_info["paraphrase_multi_variants"], ["bbbbb"])

    def test_custom_prompt_template_gets_num_and_query(self) -> None:
        seen = {}

        def _capture(**kwargs) -> SimpleNamespace:
            seen.update(kwargs)
            return SimpleNamespace(text="1. one")

        llm = MagicMock()
        llm.call.side_effect = _capture
        _paraphrase("the query", llm, strategy="multi", num_queries=7,
                    prompt_template="rewrite {num}x: {query}")
        self.assertEqual(seen["messages"][1]["content"], "rewrite 7x: the query")


class TestFallback(unittest.TestCase):
    """Best-effort degradation: the original query, plus a warning, survives."""

    def test_empty_query_skips_llm_entirely(self) -> None:
        with patch.object(llm_manager_module, "LLMManager") as manager:
            untouched = manager.return_value.get_instance_obj.return_value
            out = _paraphrase("   ", untouched)
        self.assertEqual(out.query_str, "   ")
        untouched.call.assert_not_called()

    def test_none_query_str_is_safe(self) -> None:
        out = _paraphrase(None, _fake_llm("p"))
        self.assertEqual(out.query_str, None)

    def test_no_llm_model_passes_through_with_warning(self) -> None:
        with self.assertLogs(_LOGGER_NAME, level="WARNING") as logs:
            out = BoundedQueryParaphraser().query_paraphrase(Query(query_str="q"))
        self.assertEqual(out.query_str, "q")
        self.assertIn("has no llm_model configured", "\n".join(logs.output))
        self.assertNotIn("Query expansion failed", "\n".join(logs.output))

    def test_llm_call_failure_falls_back_to_original(self) -> None:
        llm = MagicMock()
        llm.call.side_effect = RuntimeError("rate limited")
        # strategy="multi": the single expansion call fails, so the failure
        # escapes the per-call isolation and the outer catch logs it.
        with self.assertLogs(_LOGGER_NAME, level="WARNING") as logs:
            out = _paraphrase("q", llm, strategy="multi")
        self.assertEqual(out.query_str, "q")
        self.assertIn("Query expansion failed", "\n".join(logs.output))

    def test_unresolvable_llm_component_falls_back(self) -> None:
        paraphraser = BoundedQueryParaphraser(llm_model="missing_llm")
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = None
            with self.assertLogs(_LOGGER_NAME, level="WARNING") as logs:
                out = paraphraser.query_paraphrase(Query(query_str="q"))
        self.assertEqual(out.query_str, "q")
        # the ValueError quoting the unresolved name survives into the warning
        self.assertIn("'missing_llm'", "\n".join(logs.output))

    def test_empty_generation_falls_back(self) -> None:
        with self.assertLogs(_LOGGER_NAME, level="WARNING") as logs:
            out = _paraphrase("q", _fake_llm("   "))
        self.assertEqual(out.query_str, "q")
        self.assertIn("no usable expansion", "\n".join(logs.output))

    def test_all_multi_lines_equal_original_falls_back(self) -> None:
        with self.assertLogs(_LOGGER_NAME, level="WARNING"):
            out = _paraphrase("same", _fake_llm("1. same\n2. Same"), strategy="multi")
        self.assertEqual(out.query_str, "same")
        self.assertEqual(out.query_text_bundles, [])


class TestConfigValidation(unittest.TestCase):
    """Configuration errors fail loudly, quoting the offending value."""

    def test_unknown_strategy_and_mode_raise(self) -> None:
        for bad in (dict(strategy="rewrite"), dict(mode="expand")):
            with self.assertRaises(ValueError) as context:
                _paraphrase("q", _fake_llm("p"), **bad)
            self.assertIn("rewrite" if "strategy" in bad else "expand",
                          str(context.exception))

    def test_counts_and_bounds_out_of_range_raise(self) -> None:
        for bad in (dict(num_docs=0), dict(num_docs=6), dict(num_queries=0),
                    dict(num_queries=11), dict(max_doc_chars=0),
                    dict(max_query_chars=0)):
            with self.assertRaises(ValueError):
                _paraphrase("q", _fake_llm("p"), **bad)

    def test_template_without_placeholder_raises(self) -> None:
        with self.assertRaises(ValueError) as context:
            _paraphrase("q", _fake_llm("p"), prompt_template="no placeholder here")
        self.assertIn("no placeholder here", str(context.exception))

    def test_empty_ext_info_keys_raise(self) -> None:
        for bad in (dict(origin_query_key=""), dict(documents_key=""),
                    dict(variants_key="")):
            with self.assertRaises(ValueError):
                _paraphrase("q", _fake_llm("p"), **bad)

    def test_bad_config_raises_at_configer_load_time(self) -> None:
        for bad in (SimpleNamespace(name="b", description="d", strategy="rewrite"),
                    SimpleNamespace(name="b", description="d", num_docs=9),
                    SimpleNamespace(name="b", description="d", num_queries=0),
                    SimpleNamespace(name="b", description="d", max_doc_chars=0),
                    SimpleNamespace(name="b", description="d",
                                    prompt_template="missing placeholder"),
                    SimpleNamespace(name="b", description="d", variants_key="")):
            with self.assertRaises(ValueError):
                BoundedQueryParaphraser()._initialize_by_component_configer(bad)

    def test_attributes_loaded_from_configer(self) -> None:
        configer = SimpleNamespace(
            name="b", description="d", llm_model="my_llm", strategy="multi",
            num_docs=3, num_queries=5, mode="replace", max_doc_chars=500,
            max_query_chars=100, prompt_template="rewrite {num}x: {query}",
            origin_query_key="orig", documents_key="docs", variants_key="vars")
        proc = BoundedQueryParaphraser()._initialize_by_component_configer(configer)
        self.assertEqual(proc.llm_model, "my_llm")
        self.assertEqual(proc.strategy, "multi")
        self.assertEqual(proc.num_docs, 3)
        self.assertEqual(proc.num_queries, 5)
        self.assertEqual(proc.mode, "replace")
        self.assertEqual(proc.max_doc_chars, 500)
        self.assertEqual(proc.max_query_chars, 100)
        self.assertEqual(proc.prompt_template, "rewrite {num}x: {query}")
        self.assertEqual(proc.origin_query_key, "orig")
        self.assertEqual(proc.documents_key, "docs")
        self.assertEqual(proc.variants_key, "vars")


class TestRegistrationAndDispatch(unittest.TestCase):
    """The shipped yaml loads through the real machinery; the manager seam
    dispatches to the component (mirrors the competitor pipeline contract)."""

    def test_yaml_resolves_to_query_paraphraser_type(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(component_configer.get_component_config_type(),
                         ComponentEnum.QUERY_PARAPHRASER.value)

    def test_yaml_exposes_resolvable_module_and_class(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        module = component_configer.metadata.get("module")
        cls_name = component_configer.metadata.get("class")
        self.assertEqual(module, bqp_module.__name__)
        self.assertEqual(getattr(bqp_module, cls_name), BoundedQueryParaphraser)

    def test_knowledge_paraphrase_query_dispatches_to_component(self) -> None:
        knowledge = knowledge_module.Knowledge(
            name="demo_bounded_paraphraser", stores=[],
            query_paraphrasers=["bounded_query_paraphraser"])
        with patch.object(knowledge_module, "QueryParaphraserManager") as paraphraser_mgr, \
                patch.object(llm_manager_module, "LLMManager") as llm_mgr:
            paraphraser_mgr.return_value.get_instance_obj.return_value = (
                BoundedQueryParaphraser(llm_model="fake_llm", strategy="multi"))
            llm_mgr.return_value.get_instance_obj.return_value = _fake_llm(
                "1. variant one\n2. variant two")
            out = knowledge._paraphrase_query(Query(query_str="How do I reset X?"))
        self.assertEqual(out.query_str,
                         "How do I reset X?\nvariant one\nvariant two")
        self.assertEqual(out.ext_info["paraphrase_origin_query_str"], "How do I reset X?")
        self.assertEqual(out.query_text_bundles, ["variant one", "variant two"])


if __name__ == "__main__":
    unittest.main()
