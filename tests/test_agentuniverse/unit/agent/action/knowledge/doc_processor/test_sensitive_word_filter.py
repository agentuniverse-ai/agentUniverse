"""Tests for the operator-owned SensitiveWordFilter DocProcessor."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import agentuniverse.agent.action.knowledge.doc_processor.sensitive_word_filter as filter_module
from agentuniverse.agent.action.knowledge.doc_processor.sensitive_word_filter import (
    SensitiveWordDetectedError,
    SensitiveWordFilter,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.config_type_enum import ConfigTypeEnum
from agentuniverse.base.config.configer import Configer

_YAML_PATH = Path(filter_module.__file__).with_suffix(".yaml")


def _run(text: str, words: list[str], **kwargs) -> Document:
    processor = SensitiveWordFilter(words=words, **kwargs)
    return processor.process_docs([Document(text=text)])[0]


class TestSensitiveWordMatching(unittest.TestCase):
    """Literal, multilingual, normalized, leftmost-longest matching."""

    def test_chinese_terms_use_substring_matching(self) -> None:
        doc = _run("这段敏感内容并非不敏感", ["敏感"], replacement="[已过滤]")
        self.assertEqual(doc.text, "这段[已过滤]内容并非不[已过滤]")
        self.assertEqual(
            doc.metadata["sensitive_word_filter"],
            {"action": "mask", "match_count": 2},
        )

    def test_ascii_terms_are_case_insensitive_whole_words(self) -> None:
        doc = _run("BAD badger bad", ["bad"])
        self.assertEqual(doc.text, "[FILTERED] badger [FILTERED]")
        self.assertEqual(doc.metadata["sensitive_word_filter"]["match_count"], 2)

    def test_ascii_boundaries_can_be_disabled(self) -> None:
        doc = _run("badger", ["bad"], ascii_word_boundary=False)
        self.assertEqual(doc.text, "[FILTERED]ger")

    def test_literal_metacharacters_are_not_regular_expressions(self) -> None:
        doc = _run("a+b and [x] but axb", ["a+b", "[x]"])
        self.assertEqual(doc.text, "[FILTERED] and [FILTERED] but axb")
        self.assertEqual(doc.metadata["sensitive_word_filter"]["match_count"], 2)

    def test_longest_term_wins_regardless_of_vocabulary_order(self) -> None:
        for words in (["敏感", "敏感词"], ["敏感词", "敏感"]):
            with self.subTest(words=words):
                doc = _run("包含敏感词", words)
                self.assertEqual(doc.text, "包含[FILTERED]")
                self.assertEqual(doc.metadata["sensitive_word_filter"]["match_count"], 1)

    def test_unicode_compatibility_casefold_and_offsets(self) -> None:
        text = "☃ \uff33\uff25\uff23\uff32\uff25\uff34 cafe\u0301 STRAẞE end"
        doc = _run(text, ["secret", "café", "strasse"], replacement="<X>")
        self.assertEqual(doc.text, "☃ <X> <X> <X> end")
        self.assertEqual(doc.metadata["sensitive_word_filter"]["match_count"], 3)

    def test_canonically_reordered_combining_marks_cannot_bypass_matching(self) -> None:
        doc = _run("before s\u0307\u0323 after", ["\u1e69"], replacement="<X>")
        self.assertEqual(doc.text, "before <X> after")
        self.assertEqual(doc.metadata["sensitive_word_filter"]["match_count"], 1)

    def test_reordered_individual_marks_mask_each_original_span(self) -> None:
        doc = _run("a\u0307\u0323", ["\u0323", "\u0307"], replacement="<X>")
        self.assertEqual(doc.text, "a<X><X>")
        self.assertEqual(doc.metadata["sensitive_word_filter"]["match_count"], 2)

    def test_invisible_format_characters_do_not_bypass_matching(self) -> None:
        doc = _run("se\u200bcret and 敏\u200b感", ["secret", "敏感"])
        self.assertEqual(doc.text, "[FILTERED] and [FILTERED]")

    def test_case_sensitive_mode(self) -> None:
        doc = _run("Secret secret", ["Secret"], case_sensitive=True)
        self.assertEqual(doc.text, "[FILTERED] secret")

    def test_empty_and_none_text_are_preserved(self) -> None:
        processor = SensitiveWordFilter(words=["blocked"])
        empty = Document(text="")
        none = Document(id="none", text=None)
        result = processor.process_docs([empty, none])
        self.assertEqual([doc.text for doc in result], ["", None])
        self.assertEqual(
            [doc.metadata["sensitive_word_filter"]["match_count"] for doc in result],
            [0, 0],
        )


class TestSensitiveWordActions(unittest.TestCase):
    """Each action has strict any-match semantics and safe metadata."""

    def test_drop_document_removes_every_matching_document(self) -> None:
        clean_one = Document(text="clean one", metadata={"order": 1})
        blocked = Document(text="one restricted term", metadata={"order": 2})
        clean_two = Document(text="clean two", metadata={"order": 3})
        processor = SensitiveWordFilter(words=["restricted"], action="drop_document")
        result = processor.process_docs([clean_one, blocked, clean_two])
        self.assertEqual([doc.metadata["order"] for doc in result], [1, 3])
        self.assertEqual(
            [doc.metadata["sensitive_word_filter"] for doc in result],
            [
                {"action": "drop_document", "match_count": 0},
                {"action": "drop_document", "match_count": 0},
            ],
        )
        self.assertEqual(blocked.text, "one restricted term")
        self.assertNotIn("sensitive_word_filter", blocked.metadata)

    def test_raise_is_atomic_and_does_not_disclose_vocabulary(self) -> None:
        clean = Document(text="clean", metadata={"source": "a"})
        blocked = Document(text="contains private-policy-term", metadata={"source": "b"})
        processor = SensitiveWordFilter(words=["private-policy-term"], action="raise")
        with self.assertRaises(SensitiveWordDetectedError) as context:
            processor.process_docs([clean, blocked])
        self.assertEqual(context.exception.match_count, 1)
        self.assertEqual(context.exception.document_count, 1)
        self.assertNotIn("private-policy-term", str(context.exception))
        self.assertEqual(clean.metadata, {"source": "a"})
        self.assertEqual(blocked.metadata, {"source": "b"})

    def test_raise_clean_batch_records_only_aggregate_metadata(self) -> None:
        result = SensitiveWordFilter(words=["blocked"], action="raise").process_docs([Document(text="clean")])
        self.assertEqual(
            result[0].metadata["sensitive_word_filter"],
            {"action": "raise", "match_count": 0},
        )

    def test_mask_preserves_all_document_fields(self) -> None:
        document = Document(
            id="stable-id",
            text="restricted",
            metadata={"source": "policy.pdf"},
            embedding=[0.1, 0.2],
            keywords={"policy"},
        )
        result = SensitiveWordFilter(words=["restricted"]).process_docs([document])
        self.assertIs(result[0], document)
        self.assertEqual(document.id, "stable-id")
        self.assertEqual(document.embedding, [0.1, 0.2])
        self.assertEqual(document.keywords, {"policy"})
        self.assertEqual(document.metadata["source"], "policy.pdf")
        self.assertNotIn("restricted", str(document.metadata))

    def test_metadata_can_be_omitted(self) -> None:
        doc = _run("restricted", ["restricted"], metadata_key=None)
        self.assertEqual(doc.text, "[FILTERED]")
        self.assertIsNone(doc.metadata)


class TestSensitiveWordConfiguration(unittest.TestCase):
    """Configuration is loaded once, path-relative, and fails closed."""

    @staticmethod
    def _write_component_yaml(directory: Path, **overrides) -> Path:
        values = {
            "enabled": True,
            "words": [],
            "word_list_paths": [],
            "action": "mask",
            "replacement": "[FILTERED]",
            "case_sensitive": False,
            "ascii_word_boundary": True,
            "metadata_key": "sensitive_word_filter",
        }
        values.update(overrides)
        yaml_path = directory / "filter.yaml"
        yaml_path.write_text(
            "name: test_sensitive_word_filter\n"
            "description: test filter\n"
            f"enabled: {str(values['enabled']).lower()}\n"
            f"words: {values['words']!r}\n"
            f"word_list_paths: {values['word_list_paths']!r}\n"
            f"action: {values['action']!r}\n"
            f"replacement: {values['replacement']!r}\n"
            f"case_sensitive: {str(values['case_sensitive']).lower()}\n"
            f"ascii_word_boundary: {str(values['ascii_word_boundary']).lower()}\n"
            f"metadata_key: {values['metadata_key']!r}\n"
            "metadata:\n"
            "  type: DOC_PROCESSOR\n"
            "  module: agentuniverse.agent.action.knowledge.doc_processor.sensitive_word_filter\n"
            "  class: SensitiveWordFilter\n",
            encoding="utf-8",
        )
        return yaml_path

    @staticmethod
    def _load_processor(yaml_path: Path) -> SensitiveWordFilter:
        configer = Configer(path=str(yaml_path)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        return SensitiveWordFilter().initialize_by_component_configer(component_configer)

    def test_relative_utf8_word_lists_merge_with_inline_terms_and_load_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            first = directory / "first.txt"
            second = directory / "second.txt"
            first.write_bytes("\ufeff# comment\r\n外部词\r\n\r\n".encode())
            second.write_text("External\n重复词\n", encoding="utf-8")
            yaml_path = self._write_component_yaml(
                directory,
                words=["内联词", "重复词"],
                word_list_paths=["first.txt", "second.txt"],
            )

            with patch.object(
                filter_module.Path,
                "cwd",
                side_effect=AssertionError("relative word lists must resolve from the component YAML"),
            ):
                processor = self._load_processor(yaml_path)
            first.unlink()
            second.unlink()
            result = processor.process_docs([Document(text="内联词 外部词 EXTERNAL 重复词")])

        self.assertEqual(result[0].text, "[FILTERED] [FILTERED] [FILTERED] [FILTERED]")
        self.assertEqual(result[0].metadata["sensitive_word_filter"]["match_count"], 4)

    def test_missing_directory_and_invalid_utf8_fail_during_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            cases = ["missing.txt", "directory"]
            (directory / "directory").mkdir()
            for configured_path in cases:
                with self.subTest(configured_path=configured_path):
                    yaml_path = self._write_component_yaml(
                        directory,
                        word_list_paths=[configured_path],
                    )
                    with self.assertRaises(ValueError):
                        self._load_processor(yaml_path)

            invalid = directory / "invalid.txt"
            invalid.write_bytes(b"\xff\xfe\xfa")
            yaml_path = self._write_component_yaml(
                directory,
                word_list_paths=["invalid.txt"],
            )
            with self.assertRaises(ValueError):
                self._load_processor(yaml_path)

    def test_empty_vocabulary_and_invalid_action_fail_during_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            empty_yaml = self._write_component_yaml(directory)
            with self.assertRaises(ValueError):
                self._load_processor(empty_yaml)
            bad_action_yaml = self._write_component_yaml(
                directory,
                words=["hidden-policy-term"],
                action="inspect",
            )
            with self.assertRaises(ValueError) as context:
                self._load_processor(bad_action_yaml)
            self.assertNotIn("hidden-policy-term", str(context.exception))

    def test_invalid_term_error_does_not_echo_term(self) -> None:
        processor = SensitiveWordFilter(words=["hidden\nterm"])
        with self.assertRaises(ValueError) as context:
            processor.process_docs([Document(text="clean")])
        self.assertNotIn("hidden", str(context.exception))

    def test_malformed_vocabulary_does_not_leak_through_validation(self) -> None:
        for words in ("private-policy-term", [{"private-policy-term": True}]):
            with self.subTest(words=type(words).__name__):
                processor = SensitiveWordFilter(words=words)
                with self.assertRaises((TypeError, ValueError)) as context:
                    processor.process_docs([Document(text="clean")])
                self.assertNotIn("private-policy-term", str(context.exception))

    def test_matcher_configuration_cannot_be_mutated_after_compilation(self) -> None:
        processor = SensitiveWordFilter(words=["original"])
        clean = Document(text="new-policy-term")
        processor.process_docs([clean])
        processor.words.append("new-policy-term")
        with self.assertRaisesRegex(ValueError, "changed after initialization"):
            processor.process_docs([clean])
        self.assertEqual(clean.text, "new-policy-term")

    def test_invalid_mutated_action_fails_before_documents_are_changed(self) -> None:
        processor = SensitiveWordFilter(words=["restricted"])
        processor.process_docs([Document(text="clean")])
        processor.action = []
        document = Document(text="restricted")
        with self.assertRaisesRegex(TypeError, "action must be"):
            processor.process_docs([document])
        self.assertEqual(document.text, "restricted")

    def test_vocabulary_is_hidden_from_repr_and_model_dump(self) -> None:
        processor = SensitiveWordFilter(
            words=["private-policy-term"],
            word_list_paths=["secret-policy-file.txt"],
        )
        self.assertNotIn("private-policy-term", repr(processor))
        self.assertNotIn("secret-policy-file.txt", repr(processor))
        self.assertNotIn("words", processor.model_dump())
        self.assertNotIn("word_list_paths", processor.model_dump())


class TestSensitiveWordRegistration(unittest.TestCase):
    """The shipped disabled YAML is discoverable without inventing a policy."""

    def test_yaml_is_scanned_and_resolves_to_the_component(self) -> None:
        configs = AgentUniverse().scan(
            ["agentuniverse.agent.action.knowledge.doc_processor"],
            ConfigTypeEnum.YAML,
            ComponentEnum.DOC_PROCESSOR,
        )
        component_configer = next(
            config for config in configs if getattr(config, "name", None) == "sensitive_word_filter"
        )
        component_class = ComponentConfigerUtil.get_component_object_clz_by_component_configer(component_configer)
        instance = component_class().initialize_by_component_configer(component_configer)
        self.assertIsInstance(instance, SensitiveWordFilter)
        self.assertFalse(instance.enabled)
        with self.assertRaisesRegex(ValueError, "disabled"):
            instance.process_docs([Document(text="clean")])

    def test_shipped_yaml_contains_no_policy_vocabulary(self) -> None:
        configer = Configer(path=str(_YAML_PATH)).load()
        self.assertEqual(configer.value["words"], [])
        self.assertEqual(configer.value["word_list_paths"], [])
        self.assertFalse(configer.value["enabled"])


class TestSensitiveWordKnowledgePipeline(unittest.TestCase):
    """Only the configured Knowledge post-processing path invokes the filter."""

    def test_query_knowledge_masks_recalled_document_text(self) -> None:
        import agentuniverse.base.annotation.trace as trace_module
        from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
        from agentuniverse.agent.action.knowledge.knowledge import Knowledge

        class _FakeStore:
            def query(self, query):
                return [Document(text="public restricted material")]

        processor = SensitiveWordFilter(words=["restricted"])
        knowledge = Knowledge(
            name="sensitive_word_knowledge",
            stores=["only_store"],
            rag_router="base_router",
            post_processors=["sensitive_word_filter"],
        )
        router = MagicMock()
        router.rag_route.return_value = [(Query(query_str="restricted query"), "only_store")]

        with (
            patch.object(trace_module, "ConversationMemoryModule"),
            patch.object(trace_module, "Monitor") as monitor,
            patch.object(knowledge_module, "RagRouterManager") as router_manager,
            patch.object(knowledge_module, "StoreManager") as store_manager,
            patch.object(knowledge_module, "DocProcessorManager") as processor_manager,
        ):
            monitor.get_invocation_chain.return_value = []
            router_manager.return_value.get_instance_obj.return_value = router
            store_manager.return_value.get_instance_obj.return_value = _FakeStore()
            processor_manager.return_value.get_instance_obj.return_value = processor
            result = knowledge.query_knowledge(query_str="restricted query")

        self.assertEqual(result[0].text, "public [FILTERED] material")
        self.assertEqual(
            result[0].metadata["sensitive_word_filter"],
            {"action": "mask", "match_count": 1},
        )
        router.rag_route.assert_called_once()


if __name__ == "__main__":
    unittest.main()
