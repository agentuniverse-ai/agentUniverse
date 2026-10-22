# !/usr/bin/env python3

# @Time    : 2026/10/03
# @FileName: test_multi_query_paraphraser.py

"""Tests for the MultiQueryParaphraser query paraphraser."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import agentuniverse.agent.action.knowledge.query_paraphraser.multi_query_paraphraser as mqp_module
import agentuniverse.llm.llm_manager as llm_manager_module
from agentuniverse.agent.action.knowledge.query_paraphraser.multi_query_paraphraser import (
    MultiQueryParaphraser,
    _normalize_variant,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(mqp_module.__file__), "multi_query_paraphraser.yaml")
_LOGGER_NAME = mqp_module.__name__


def _fake_llm(text):
    """Build a MagicMock LLM returning the given completion text."""
    llm = MagicMock()
    llm.call.return_value = SimpleNamespace(text=text)
    return llm


def _paraphrase(query_str, llm, **kwargs):
    """Run one expansion with the LLM manager mocked out."""
    with patch.object(llm_manager_module, "LLMManager") as manager:
        manager.return_value.get_instance_obj.return_value = llm
        paraphraser = MultiQueryParaphraser(llm_model="fake_llm", **kwargs)
        return paraphraser.query_paraphrase(Query(query_str=query_str))


class TestMultiQueryParsing(unittest.TestCase):
    """One LLM call is parsed into a clean variant list."""

    def test_numbered_lines_parsed(self) -> None:
        llm = _fake_llm("1. how to reset\n2. reset procedure\n3. resetting steps")
        query = _paraphrase("reset", llm)
        self.assertEqual(query.ext_info["multi_query_variants"], ["how to reset", "reset procedure", "resetting steps"])

    def test_paren_and_chinese_numbering_and_bullets(self) -> None:
        for prefix in ("1)", "1、", "- ", "* ", "• "):
            with self.subTest(prefix=prefix):
                llm = _fake_llm(f"{prefix}variant one")
                query = _paraphrase("q", llm)
                self.assertEqual(query.ext_info["multi_query_variants"], ["variant one"])

    def test_wrapping_quotes_stripped(self) -> None:
        llm = _fake_llm('1. "quoted variant"\n2. “smart quoted”')
        query = _paraphrase("q", llm)
        self.assertEqual(query.ext_info["multi_query_variants"], ["quoted variant", "smart quoted"])

    def test_empty_lines_skipped(self) -> None:
        llm = _fake_llm("1. first\n\n   \n2. second\n")
        query = _paraphrase("q", llm)
        self.assertEqual(query.ext_info["multi_query_variants"], ["first", "second"])

    def test_num_queries_caps_output(self) -> None:
        llm = _fake_llm("1. a\n2. b\n3. c\n4. d\n5. e")
        query = _paraphrase("q", llm, num_queries=3)
        self.assertEqual(query.ext_info["multi_query_variants"], ["a", "b", "c"])

    def test_duplicates_dropped(self) -> None:
        llm = _fake_llm("1. same\n2. same\n3. Same\n4. other")
        query = _paraphrase("q", llm)
        # Case/whitespace-folded duplicates collapse; first spelling wins.
        self.assertEqual(query.ext_info["multi_query_variants"], ["same", "other"])

    def test_variant_equal_to_original_dropped(self) -> None:
        llm = _fake_llm("1. How do I reset X?\n2. reset X procedure")
        query = _paraphrase("how do i reset x?", llm)
        self.assertEqual(query.ext_info["multi_query_variants"], ["reset X procedure"])

    def test_variants_truncated_to_max_chars(self) -> None:
        llm = _fake_llm("1. " + "x" * 200)
        query = _paraphrase("q", llm, max_query_chars=50)
        self.assertEqual(len(query.ext_info["multi_query_variants"][0]), 50)

    def test_variants_deduplicated_after_truncation(self) -> None:
        query = _paraphrase("q", _fake_llm("1. Same prefix one\n2. SAME prefix two\n3. other"), max_query_chars=11)
        self.assertEqual(query.ext_info["multi_query_variants"], ["Same prefix", "other"])

    def test_variant_equal_to_original_after_truncation_dropped(self) -> None:
        query = _paraphrase("reset", _fake_llm("1. RESET extra\n2. other"), max_query_chars=5)
        self.assertEqual(query.ext_info["multi_query_variants"], ["other"])

    def test_normalize_variant_helper(self) -> None:
        self.assertEqual(_normalize_variant("  3、  'hello'  "), "hello")
        self.assertEqual(_normalize_variant("no decoration"), "no decoration")
        self.assertEqual(_normalize_variant("   "), "")

    def test_custom_template_num_and_query_substituted(self) -> None:
        llm = _fake_llm("1. v")
        _paraphrase("my query", llm, num_queries=4, prompt_template="Give {num} rewrites of {query} as {json}.")
        user_content = llm.call.call_args.kwargs["messages"][1]["content"]
        self.assertIn("Give 4 rewrites of my query", user_content)
        # {num} is replaced before {query}, so a literal {num} inside the
        # query text cannot be re-expanded; unrelated braces stay intact.
        self.assertIn("{json}", user_content)


class TestMultiQueryExpansion(unittest.TestCase):
    """Query contract: bundles, query_str rewrite, provenance."""

    def test_append_mode_keeps_original(self) -> None:
        query = _paraphrase("origin q", _fake_llm("1. v1\n2. v2"))
        self.assertEqual(query.query_str, "origin q\nv1\nv2")

    def test_replace_mode_uses_variants_only(self) -> None:
        query = _paraphrase("origin q", _fake_llm("1. v1\n2. v2"), mode="replace")
        self.assertEqual(query.query_str, "v1\nv2")

    def test_ext_info_records_original(self) -> None:
        query = _paraphrase("origin q", _fake_llm("1. v1"))
        self.assertEqual(query.ext_info["multi_query_origin_query_str"], "origin q")

    def test_variants_appended_to_text_bundles(self) -> None:
        query = _paraphrase("q", _fake_llm("1. v1\n2. v2"))
        self.assertEqual(query.query_text_bundles, ["v1", "v2"])

    def test_existing_bundles_preserved_and_not_duplicated(self) -> None:
        llm = _fake_llm("1. v1")
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = llm
            paraphraser = MultiQueryParaphraser(llm_model="fake_llm")
            query = Query(query_str="q", query_text_bundles=["earlier", "v1"])
            paraphraser.query_paraphrase(query)
        self.assertEqual(query.query_text_bundles, ["earlier", "v1"])

    def test_other_query_fields_untouched(self) -> None:
        llm = _fake_llm("1. v1")
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = llm
            paraphraser = MultiQueryParaphraser(llm_model="fake_llm")
            query = Query(query_str="q", keywords={"k"}, similarity_top_k=3, embeddings=[[0.1]])
            paraphraser.query_paraphrase(query)
        self.assertEqual(query.keywords, {"k"})
        self.assertEqual(query.similarity_top_k, 3)
        self.assertEqual(query.embeddings, [[0.1]])

    def test_single_llm_call_per_expansion(self) -> None:
        llm = _fake_llm("1. a\n2. b\n3. c")
        _paraphrase("q", llm, num_queries=3)
        self.assertEqual(llm.call.call_count, 1)


class TestMultiQueryFallback(unittest.TestCase):
    """Expansion is best-effort: anything unusable degrades to pass-through."""

    def test_empty_query_skips_llm(self) -> None:
        llm = _fake_llm("1. v")
        query = _paraphrase("", llm)
        self.assertEqual(query.query_str, "")
        llm.call.assert_not_called()

    def test_none_query_str_is_safe(self) -> None:
        llm = _fake_llm("1. v")
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = llm
            query = MultiQueryParaphraser(llm_model="fake_llm").query_paraphrase(Query())
        self.assertIsNone(query.query_str)
        llm.call.assert_not_called()

    def test_no_llm_model_passes_through_with_warning(self) -> None:
        with self.assertLogs(_LOGGER_NAME, level="WARNING") as logs:
            query = MultiQueryParaphraser().query_paraphrase(Query(query_str="q"))
        self.assertEqual(query.query_str, "q")
        self.assertIn("no llm_model", "\n".join(logs.output))

    def test_llm_call_failure_falls_back(self) -> None:
        llm = MagicMock()
        llm.call.side_effect = RuntimeError("boom")
        with self.assertLogs(_LOGGER_NAME, level="WARNING") as logs:
            query = _paraphrase("q", llm)
        self.assertEqual(query.query_str, "q")
        self.assertIn("expansion failed", "\n".join(logs.output))

    def test_unresolvable_llm_component_falls_back(self) -> None:
        with patch.object(llm_manager_module, "LLMManager") as manager:
            manager.return_value.get_instance_obj.return_value = None
            with self.assertLogs(_LOGGER_NAME, level="WARNING"):
                query = MultiQueryParaphraser(llm_model="missing").query_paraphrase(Query(query_str="q"))
        self.assertEqual(query.query_str, "q")

    def test_empty_generation_falls_back(self) -> None:
        with self.assertLogs(_LOGGER_NAME, level="WARNING") as logs:
            query = _paraphrase("q", _fake_llm("   "))
        self.assertEqual(query.query_str, "q")
        self.assertIn("no usable variant", "\n".join(logs.output))

    def test_all_lines_equal_original_falls_back(self) -> None:
        with self.assertLogs(_LOGGER_NAME, level="WARNING"):
            query = _paraphrase("same", _fake_llm("1. same\n2. Same"))
        self.assertEqual(query.query_str, "same")
        self.assertEqual(query.query_text_bundles, [])


class TestMultiQueryConfig(unittest.TestCase):
    """Component-configer initialization is eager and complete."""

    def test_bad_config_raises_at_load_time(self) -> None:
        for bad in (
            SimpleNamespace(name="mqp", description="d", mode="rewrite"),
            SimpleNamespace(name="mqp", description="d", num_queries=0),
            SimpleNamespace(name="mqp", description="d", num_queries=11),
            SimpleNamespace(name="mqp", description="d", max_query_chars=0),
            SimpleNamespace(name="mqp", description="d", prompt_template="no placeholder"),
            SimpleNamespace(name="mqp", description="d", variants_key=""),
        ):
            with self.assertRaises(ValueError):
                MultiQueryParaphraser()._initialize_by_component_configer(bad)

    def test_attributes_loaded_from_configer(self) -> None:
        configer = SimpleNamespace(
            name="mqp",
            description="d",
            llm_model="my_llm",
            num_queries=5,
            mode="replace",
            max_query_chars=100,
            prompt_template="rewrite {num}x: {query}",
            origin_query_key="orig",
            variants_key="vars",
        )
        proc = MultiQueryParaphraser()._initialize_by_component_configer(configer)
        self.assertEqual(proc.llm_model, "my_llm")
        self.assertEqual(proc.num_queries, 5)
        self.assertEqual(proc.mode, "replace")
        self.assertEqual(proc.max_query_chars, 100)
        self.assertEqual(proc.prompt_template, "rewrite {num}x: {query}")
        self.assertEqual(proc.origin_query_key, "orig")
        self.assertEqual(proc.variants_key, "vars")


class TestMultiQueryRegistration(unittest.TestCase):
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
            "agentuniverse.agent.action.knowledge.query_paraphraser." "multi_query_paraphraser",
        )
        self.assertEqual(component_configer.metadata_class, "MultiQueryParaphraser")

    def test_shipped_yaml_defaults_initialize_cleanly(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        proc = MultiQueryParaphraser()._initialize_by_component_configer(component_configer)
        self.assertEqual(proc.llm_model, "")
        self.assertEqual(proc.num_queries, 3)
        self.assertEqual(proc.mode, "append")


class TestMultiQueryThroughKnowledgePipeline(unittest.TestCase):
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
            name="mqp_knowledge",
            stores=["only_store"],
            rag_router="base_router",
            query_paraphrasers=["multi_query_paraphraser"],
        )
        router = MagicMock()
        router.rag_route.side_effect = lambda q, stores: [(q, "only_store")]
        paraphraser = MultiQueryParaphraser(llm_model="fake_llm")

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
            llm_mgr.return_value.get_instance_obj.return_value = _fake_llm("1. variant one\n2. variant two")
            out = knowledge.query_knowledge(query_str="How do I reset X?")

        self.assertEqual([d.text for d in out], ["recalled"])
        seen = captured["query"]
        self.assertEqual(seen.query_str, "How do I reset X?\nvariant one\nvariant two")
        self.assertEqual(seen.ext_info["multi_query_origin_query_str"], "How do I reset X?")
        self.assertEqual(seen.query_text_bundles, ["variant one", "variant two"])


if __name__ == "__main__":
    unittest.main()
