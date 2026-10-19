# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/16
# @FileName: test_context_budget_compressor.py

"""Tests for the ContextBudgetCompressor doc processor."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import agentuniverse.agent.action.knowledge.doc_processor.\
    context_budget_compressor as cbc_module
from agentuniverse.agent.action.knowledge.doc_processor.\
    context_budget_compressor import ContextBudgetCompressor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(cbc_module.__file__),
                          "context_budget_compressor.yaml")


def _run(docs, **kwargs):
    return ContextBudgetCompressor(**kwargs).process_docs(
        [Document(text=d) if isinstance(d, str) else d for d in docs])


class TestContextBudgetSelection(unittest.TestCase):
    """Cumulative budget selection and boundary truncation."""

    def test_empty_input_returns_empty(self) -> None:
        self.assertEqual(_run([], budget=10, counter="char"), [])

    def test_non_positive_budget_returns_empty(self) -> None:
        self.assertEqual(_run(["abc"], budget=0, counter="char"), [])
        self.assertEqual(_run(["abc"], budget=-5, counter="char"), [])

    def test_keeps_whole_docs_within_budget(self) -> None:
        out = _run(["aa", "bb", "cc"], budget=4, counter="char", truncate=False)
        self.assertEqual([d.text for d in out], ["aa", "bb"])

    def test_stops_at_first_overflow_without_truncate(self) -> None:
        out = _run(["aa", "bb", "cc"], budget=4, counter="char", truncate=False)
        self.assertEqual(len(out), 2)

    def test_truncates_boundary_doc_to_fit(self) -> None:
        out = _run(["aaa", "bbbb"], budget=5, counter="char", truncate=True)
        self.assertEqual([d.text for d in out], ["aaa", "bb"])
        self.assertTrue(out[1].metadata.get("truncated"))

    def test_single_doc_exceeding_budget_is_truncated(self) -> None:
        out = _run(["abcdefghij"], budget=3, counter="char", truncate=True)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].text, "abc")
        self.assertTrue(out[0].metadata.get("truncated"))

    def test_single_doc_exceeding_budget_without_truncate_is_empty(self) -> None:
        out = _run(["abcdefghij"], budget=3, counter="char", truncate=False)
        self.assertEqual(out, [])

    def test_input_order_preserved(self) -> None:
        out = _run(["xx", "yy", "zz"], budget=6, counter="char", truncate=False)
        self.assertEqual([d.text for d in out], ["xx", "yy", "zz"])

    def test_truncated_doc_preserves_id_and_metadata(self) -> None:
        original = Document(text="bbbb", metadata={"source": "readme.md"})
        out = ContextBudgetCompressor(budget=3, counter="char").process_docs(
            [original])
        self.assertEqual(out[0].text, "bbb")
        self.assertEqual(out[0].metadata.get("source"), "readme.md")
        self.assertTrue(out[0].metadata.get("truncated"))
        self.assertEqual(out[0].id, original.id)


class TestContextBudgetCounters(unittest.TestCase):
    """The counter choice changes how size is measured."""

    def test_char_counter_counts_characters(self) -> None:
        proc = ContextBudgetCompressor(budget=5, counter="char")
        self.assertEqual(proc._count("hello"), 5)

    def test_word_counter_truncates_by_words(self) -> None:
        out = _run(["one two three four"], budget=3, counter="word",
                   truncate=True)
        self.assertEqual(out[0].text, "one two three")

    def test_word_counter_counts_words(self) -> None:
        proc = ContextBudgetCompressor(counter="word")
        self.assertEqual(proc._count("a b c"), 3)

    def test_estimate_counter_uses_chars_div_four(self) -> None:
        proc = ContextBudgetCompressor(counter="estimate")
        self.assertEqual(proc._count("x" * 12), 3)   # 12 // 4
        self.assertEqual(proc._count(""), 1)         # at least 1

    def test_tiktoken_counter_counts_real_tokens(self) -> None:
        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
        except Exception:  # noqa: BLE001 - optional dependency
            self.skipTest("tiktoken not installed")
        proc = ContextBudgetCompressor(counter="tiktoken")
        text = "hello world"
        self.assertEqual(proc._count(text), len(enc.encode(text)))

    def test_tiktoken_counter_truncates_by_tokens(self) -> None:
        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
        except Exception:  # noqa: BLE001 - optional dependency
            self.skipTest("tiktoken not installed")
        # "hello world" is two tokens ('hello', ' world'); keep one.
        out = _run(["hello world"], budget=1, counter="tiktoken", truncate=True)
        self.assertEqual(out[0].text, enc.decode(enc.encode("hello world")[:1]))


class TestContextBudgetTiktokenCache(unittest.TestCase):
    """Encoders are cached per encoding name; bad encodings raise.

    Guards the regression where a single module-global cache slot meant the
    first compressor instance fixed the encoder for every later instance, and
    an invalid first encoding silently forced every later instance onto the
    estimate counter.
    """

    # cl100k_base and p50k_base disagree on this string (6 vs 7 tokens), so a
    # later instance reusing the first instance's encoder would miscount.
    _PROBE = "def __init__(self):"

    def setUp(self) -> None:
        cbc_module._TIKTOKEN_ENCODERS.clear()

    def tearDown(self) -> None:
        cbc_module._TIKTOKEN_ENCODERS.clear()

    def test_each_instance_uses_its_configured_encoding(self) -> None:
        import tiktoken
        cl100k = ContextBudgetCompressor(counter="tiktoken",
                                         tiktoken_encoding="cl100k_base")
        p50k = ContextBudgetCompressor(counter="tiktoken",
                                       tiktoken_encoding="p50k_base")
        self.assertEqual(
            cl100k._count(self._PROBE),
            len(tiktoken.get_encoding("cl100k_base").encode(self._PROBE)))
        self.assertEqual(
            p50k._count(self._PROBE),
            len(tiktoken.get_encoding("p50k_base").encode(self._PROBE)))
        # The two encoders must be cached as distinct objects keyed by name.
        self.assertIn("cl100k_base", cbc_module._TIKTOKEN_ENCODERS)
        self.assertIn("p50k_base", cbc_module._TIKTOKEN_ENCODERS)
        self.assertIsNot(
            cbc_module._TIKTOKEN_ENCODERS["cl100k_base"],
            cbc_module._TIKTOKEN_ENCODERS["p50k_base"])

    def test_invalid_encoding_raises_configuration_error(self) -> None:
        proc = ContextBudgetCompressor(
            counter="tiktoken", tiktoken_encoding="not_a_real_encoding")
        with self.assertRaises(ValueError) as ctx:
            proc._count(self._PROBE)
        self.assertIn("not_a_real_encoding", str(ctx.exception))

    def test_invalid_encoding_before_valid_does_not_poison(self) -> None:
        # The core regression: an invalid encoding on one instance must not
        # silently push a later valid instance onto the estimate counter.
        bad = ContextBudgetCompressor(
            counter="tiktoken", tiktoken_encoding="not_a_real_encoding")
        with self.assertRaises(ValueError):
            bad._count(self._PROBE)
        # Invalid lookups are not cached, so the cache stays clean.
        self.assertNotIn("not_a_real_encoding", cbc_module._TIKTOKEN_ENCODERS)

        good = ContextBudgetCompressor(
            counter="tiktoken", tiktoken_encoding="cl100k_base")
        import tiktoken
        self.assertEqual(
            good._count(self._PROBE),
            len(tiktoken.get_encoding("cl100k_base").encode(self._PROBE)))

    def test_missing_dependency_degrades_instead_of_raising(self) -> None:
        # A missing optional dependency must degrade to the estimate counter,
        # in contrast with an invalid encoding (which raises). Setting a
        # sys.modules key to None makes `import tiktoken` raise ImportError.
        import sys
        proc = ContextBudgetCompressor(
            counter="tiktoken", tiktoken_encoding="cl100k_base")
        with patch.dict(sys.modules, {"tiktoken": None}):
            estimate = proc._count(self._PROBE)
        self.assertEqual(estimate, max(1, len(self._PROBE) // 4))


class TestContextBudgetConfig(unittest.TestCase):
    """Initialization and configuration."""

    def test_invalid_counter_raises(self) -> None:
        configer = SimpleNamespace(name="cbc", description="d", counter="bytes")
        with self.assertRaises(ValueError):
            ContextBudgetCompressor()._initialize_by_component_configer(configer)

    def test_attributes_loaded_from_configer(self) -> None:
        configer = SimpleNamespace(
            name="cbc", description="d",
            budget=128, counter="word", truncate=False,
            tiktoken_encoding="p50k_base")
        proc = ContextBudgetCompressor()._initialize_by_component_configer(configer)
        self.assertEqual(proc.budget, 128)
        self.assertEqual(proc.counter, "word")
        self.assertFalse(proc.truncate)
        self.assertEqual(proc.tiktoken_encoding, "p50k_base")


class TestContextBudgetRegistration(unittest.TestCase):
    """The shipped yaml resolves through the real framework loader."""

    def test_yaml_resolves_to_doc_processor_type(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.get_component_config_type(),
            ComponentEnum.DOC_PROCESSOR.value)

    def test_yaml_exposes_module_and_class(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.metadata_module,
            "agentuniverse.agent.action.knowledge.doc_processor."
            "context_budget_compressor")
        self.assertEqual(component_configer.metadata_class,
                         "ContextBudgetCompressor")


class TestContextBudgetThroughKnowledgePipeline(unittest.TestCase):
    """The compressor runs as a real post_processor through query_knowledge."""

    def test_compresses_in_the_pipeline(self) -> None:
        from agentuniverse.agent.action.knowledge import knowledge as \
            knowledge_module
        from agentuniverse.agent.action.knowledge.knowledge import Knowledge
        import agentuniverse.base.annotation.trace as trace_module

        class _FakeStore:
            def query(self, query):
                return [Document(text="aaaa"),
                        Document(text="bbb"),
                        Document(text="cc")]

        compressor = ContextBudgetCompressor(budget=5, counter="char")
        knowledge = Knowledge(
            name="cbc_knowledge",
            stores=["only_store"],
            rag_router="base_router",
            post_processors=["context_budget_compressor"],
        )
        router = MagicMock()
        router.rag_route.return_value = [(Query(query_str="q"), "only_store")]

        with patch.object(trace_module, "ConversationMemoryModule"), \
                patch.object(trace_module, "Monitor") as monitor, \
                patch.object(knowledge_module, "RagRouterManager") as router_mgr, \
                patch.object(knowledge_module, "StoreManager") as store_mgr, \
                patch.object(knowledge_module, "DocProcessorManager") as proc_mgr:
            monitor.get_invocation_chain.return_value = []
            router_mgr.return_value.get_instance_obj.return_value = router
            store_mgr.return_value.get_instance_obj.side_effect = \
                lambda code, **_: _FakeStore()
            proc_mgr.return_value.get_instance_obj.return_value = compressor
            out = knowledge.query_knowledge(query_str="q")

        # "aaaa" (4) fits; "bbb" would overflow -> truncated to 1 char "b".
        self.assertEqual([d.text for d in out], ["aaaa", "b"])
        self.assertTrue(out[1].metadata.get("truncated"))


if __name__ == '__main__':
    unittest.main()
