# !/usr/bin/env python3

# @Time    : 2026/10/02
# @FileName: test_hyde_query_paraphraser.py

"""Tests for the HyDEQueryParaphraser query paraphraser."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import agentuniverse.agent.action.knowledge.query_paraphraser.hyde_query_paraphraser as hyde_module
import agentuniverse.llm.llm_manager as llm_manager_module
from agentuniverse.agent.action.knowledge.query_paraphraser.hyde_query_paraphraser import HyDEQueryParaphraser
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(hyde_module.__file__), "hyde_query_paraphraser.yaml")
_LOGGER_NAME = hyde_module.__name__


def _fake_llm(*texts):
    """Build a MagicMock LLM returning the given passage texts in order."""
    llm = MagicMock()
    outputs = [SimpleNamespace(text=t) for t in texts]
    llm.call.side_effect = outputs if len(outputs) > 1 else None
    if len(outputs) == 1:
        llm.call.return_value = outputs[0]
    return llm


def _paraphrase(query_str, llm, **kwargs):
    """Run one expansion with the LLM manager mocked out."""
    with patch.object(llm_manager_module, "LLMManager") as manager:
        manager.return_value.get_instance_obj.return_value = llm
        paraphraser = HyDEQueryParaphraser(llm_model="fake_llm", **kwargs)
        return paraphraser.query_paraphrase(Query(query_str=query_str))


class TestHyDEExpansion(unittest.TestCase):
    """Passage generation rewrites the query and records provenance."""

    def test_append_mode_keeps_original_and_adds_passage(self) -> None:
        query = _paraphrase("What is PEER?", _fake_llm("PEER is a pattern."))
        self.assertEqual(query.query_str, "What is PEER?\n\nPEER is a pattern.")

    def test_replace_mode_uses_passages_only(self) -> None:
        query = _paraphrase("What is PEER?", _fake_llm("PEER is a pattern."), mode="replace")
        self.assertEqual(query.query_str, "PEER is a pattern.")

    def test_ext_info_records_original_and_passages(self) -> None:
        query = _paraphrase("What is PEER?", _fake_llm("PEER is a pattern."))
        self.assertEqual(query.ext_info["hyde_origin_query_str"], "What is PEER?")
        self.assertEqual(query.ext_info["hyde_documents"], ["PEER is a pattern."])

    def test_passages_appended_to_text_bundles(self) -> None:
        query = _paraphrase("q", _fake_llm("passage one"))
        self.assertEqual(query.query_text_bundles, ["passage one"])

    def test_existing_bundles_are_preserved_and_not_duplicated(self) -> None:
        llm = _fake_llm("passage one")
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = llm
            paraphraser = HyDEQueryParaphraser(llm_model="fake_llm")
            query = Query(query_str="q", query_text_bundles=["earlier", "passage one"])
            paraphraser.query_paraphrase(query)
        self.assertEqual(query.query_text_bundles, ["earlier", "passage one"])

    def test_passage_truncated_to_max_doc_chars(self) -> None:
        query = _paraphrase("q", _fake_llm("x" * 500), max_doc_chars=100)
        self.assertEqual(len(query.ext_info["hyde_documents"][0]), 100)
        self.assertEqual(len(query.query_str), len("q\n\n") + 100)

    def test_num_docs_generates_multiple_passages(self) -> None:
        llm = _fake_llm("first passage", "second passage")
        query = _paraphrase("q", llm, num_docs=2)
        self.assertEqual(llm.call.call_count, 2)
        self.assertEqual(query.ext_info["hyde_documents"], ["first passage", "second passage"])
        self.assertEqual(query.query_text_bundles, ["first passage", "second passage"])
        self.assertEqual(query.query_str, "q\n\nfirst passage\n\nsecond passage")

    def test_duplicate_passages_are_deduplicated(self) -> None:
        query = _paraphrase("q", _fake_llm("same", "same"), num_docs=2)
        self.assertEqual(query.ext_info["hyde_documents"], ["same"])
        self.assertEqual(query.query_text_bundles, ["same"])

    def test_custom_prompt_template_substitution(self) -> None:
        llm = _fake_llm("answer passage")
        _paraphrase("my query", llm, prompt_template="Answer {query} — keep {json} braces.")
        messages = llm.call.call_args.kwargs["messages"]
        user_content = messages[1]["content"]
        self.assertIn("Answer my query", user_content)
        # str.replace substitution leaves unrelated braces untouched.
        self.assertIn("{json}", user_content)
        self.assertEqual(llm.call.call_args.kwargs["streaming"], False)

    def test_other_query_fields_untouched(self) -> None:
        llm = _fake_llm("passage")
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = llm
            paraphraser = HyDEQueryParaphraser(llm_model="fake_llm")
            query = Query(query_str="q", keywords={"k"}, similarity_top_k=3, embeddings=[[0.1]])
            paraphraser.query_paraphrase(query)
        self.assertEqual(query.keywords, {"k"})
        self.assertEqual(query.similarity_top_k, 3)
        self.assertEqual(query.embeddings, [[0.1]])


class TestHyDEFallback(unittest.TestCase):
    """Expansion is best-effort: anything unusable degrades to pass-through."""

    def test_empty_query_skips_llm_entirely(self) -> None:
        llm = _fake_llm("passage")
        query = _paraphrase("", llm)
        self.assertEqual(query.query_str, "")
        llm.call.assert_not_called()
        self.assertEqual(query.ext_info, {})

    def test_none_query_str_is_safe(self) -> None:
        llm = _fake_llm("passage")
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = llm
            paraphraser = HyDEQueryParaphraser(llm_model="fake_llm")
            query = paraphraser.query_paraphrase(Query())
        self.assertIsNone(query.query_str)
        llm.call.assert_not_called()

    def test_whitespace_query_unchanged(self) -> None:
        query = _paraphrase("   ", _fake_llm("passage"))
        self.assertEqual(query.query_str, "   ")

    def test_no_llm_model_passes_through_with_warning(self) -> None:
        with self.assertLogs(_LOGGER_NAME, level="WARNING") as logs:
            query = HyDEQueryParaphraser().query_paraphrase(Query(query_str="q"))
        self.assertEqual(query.query_str, "q")
        self.assertIn("no llm_model", "\n".join(logs.output))

    def test_llm_call_failure_falls_back_to_original(self) -> None:
        llm = MagicMock()
        llm.call.side_effect = RuntimeError("boom")
        with self.assertLogs(_LOGGER_NAME, level="WARNING") as logs:
            query = _paraphrase("q", llm)
        self.assertEqual(query.query_str, "q")
        self.assertEqual(query.query_text_bundles, [])
        self.assertIn("HyDE expansion failed", "\n".join(logs.output))

    def test_unresolvable_llm_component_falls_back(self) -> None:
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = None
            with self.assertLogs(_LOGGER_NAME, level="WARNING"):
                paraphraser = HyDEQueryParaphraser(llm_model="missing_llm")
                query = paraphraser.query_paraphrase(Query(query_str="q"))
        self.assertEqual(query.query_str, "q")

    def test_empty_generation_falls_back(self) -> None:
        with self.assertLogs(_LOGGER_NAME, level="WARNING") as logs:
            query = _paraphrase("q", _fake_llm("   "))
        self.assertEqual(query.query_str, "q")
        self.assertIn("no usable passage", "\n".join(logs.output))

    def test_partial_empty_generation_keeps_usable_passage(self) -> None:
        query = _paraphrase("q", _fake_llm("", "kept passage"), num_docs=2)
        self.assertEqual(query.ext_info["hyde_documents"], ["kept passage"])


class TestHyDEConfigValidation(unittest.TestCase):
    """Invalid configuration fails loudly instead of silently misbehaving."""

    def test_unknown_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            _paraphrase("q", _fake_llm("p"), mode="rewrite")

    def test_num_docs_out_of_range_raises(self) -> None:
        for bad in (0, 6, -1):
            with self.assertRaises(ValueError):
                _paraphrase("q", _fake_llm("p"), num_docs=bad)

    def test_non_positive_max_doc_chars_raises(self) -> None:
        with self.assertRaises(ValueError):
            _paraphrase("q", _fake_llm("p"), max_doc_chars=0)

    def test_template_without_placeholder_raises(self) -> None:
        with self.assertRaises(ValueError):
            _paraphrase("q", _fake_llm("p"), prompt_template="no placeholder")

    def test_empty_ext_info_keys_raise(self) -> None:
        with self.assertRaises(ValueError):
            _paraphrase("q", _fake_llm("p"), origin_query_key="")
        with self.assertRaises(ValueError):
            _paraphrase("q", _fake_llm("p"), documents_key="")

    def test_bad_config_raises_at_configer_load_time(self) -> None:
        for bad in (
            SimpleNamespace(name="hyde", description="d", mode="rewrite"),
            SimpleNamespace(name="hyde", description="d", num_docs=9),
            SimpleNamespace(name="hyde", description="d", max_doc_chars=0),
            SimpleNamespace(name="hyde", description="d", prompt_template="missing placeholder"),
        ):
            with self.assertRaises(ValueError):
                HyDEQueryParaphraser()._initialize_by_component_configer(bad)

    def test_attributes_loaded_from_configer(self) -> None:
        configer = SimpleNamespace(
            name="hyde",
            description="d",
            llm_model="my_llm",
            num_docs=3,
            mode="replace",
            max_doc_chars=500,
            prompt_template="answer {query}",
            origin_query_key="orig",
            documents_key="docs",
        )
        proc = HyDEQueryParaphraser()._initialize_by_component_configer(configer)
        self.assertEqual(proc.llm_model, "my_llm")
        self.assertEqual(proc.num_docs, 3)
        self.assertEqual(proc.mode, "replace")
        self.assertEqual(proc.max_doc_chars, 500)
        self.assertEqual(proc.prompt_template, "answer {query}")
        self.assertEqual(proc.origin_query_key, "orig")
        self.assertEqual(proc.documents_key, "docs")


class TestHyDERegistration(unittest.TestCase):
    """The shipped yaml resolves through the real framework loader."""

    def test_yaml_resolves_to_query_paraphraser_type(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(component_configer.get_component_config_type(), ComponentEnum.QUERY_PARAPHRASER.value)

    def test_yaml_exposes_module_and_class(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.metadata_module,
            "agentuniverse.agent.action.knowledge.query_paraphraser." "hyde_query_paraphraser",
        )
        self.assertEqual(component_configer.metadata_class, "HyDEQueryParaphraser")

    def test_shipped_yaml_defaults_initialize_cleanly(self) -> None:
        # The package-shipped yaml must load at framework start without
        # raising even though llm_model is empty (pass-through + warning).
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        proc = HyDEQueryParaphraser()._initialize_by_component_configer(component_configer)
        self.assertEqual(proc.llm_model, "")
        self.assertEqual(proc.mode, "append")
        self.assertEqual(proc.num_docs, 1)


class TestHyDEThroughKnowledgePipeline(unittest.TestCase):
    """The paraphraser expands the query before the store ever sees it."""

    def test_store_receives_expanded_query(self) -> None:
        import agentuniverse.base.annotation.trace as trace_module
        from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
        from agentuniverse.agent.action.knowledge.knowledge import Knowledge

        captured = {}

        class _FakeStore:
            def query(self, query):
                captured["query"] = query
                return [Document(text="recalled")]

        knowledge = Knowledge(
            name="hyde_knowledge",
            stores=["only_store"],
            rag_router="base_router",
            query_paraphrasers=["hyde_query_paraphraser"],
        )
        router = MagicMock()
        # The base router passes the (already paraphrased) query through to
        # each store; mirror that so the test observes the rewritten object.
        router.rag_route.side_effect = lambda q, stores: [(q, "only_store")]
        paraphraser = HyDEQueryParaphraser(llm_model="fake_llm")

        with (
            patch.object(trace_module, "ConversationMemoryModule"),
            patch.object(trace_module, "Monitor") as monitor,
            patch.object(knowledge_module, "RagRouterManager") as router_mgr,
            patch.object(knowledge_module, "StoreManager") as store_mgr,
            patch.object(knowledge_module, "QueryParaphraserManager") as paraphraser_mgr,
            patch.object(llm_manager_module, "LLMManager") as llm_mgr,
        ):
            monitor.get_invocation_chain.return_value = []
            router_mgr.return_value.get_instance_obj.return_value = router
            store_mgr.return_value.get_instance_obj.side_effect = lambda code, **_: _FakeStore()
            paraphraser_mgr.return_value.get_instance_obj.return_value = paraphraser
            llm_mgr.return_value.get_instance_obj.return_value = _fake_llm("hypothetical answer")
            out = knowledge.query_knowledge(query_str="What is PEER?")

        self.assertEqual([d.text for d in out], ["recalled"])
        seen = captured["query"]
        self.assertEqual(seen.query_str, "What is PEER?\n\nhypothetical answer")
        self.assertEqual(seen.ext_info["hyde_origin_query_str"], "What is PEER?")
        self.assertIn("hypothetical answer", seen.query_text_bundles)


if __name__ == "__main__":
    unittest.main()
