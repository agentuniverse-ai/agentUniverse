# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/16
# @FileName: test_sensitive_data_redactor.py

"""Tests for the SensitiveDataRedactor doc processor."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import agentuniverse.agent.action.knowledge.doc_processor.\
    sensitive_data_redactor as sdr_module
from agentuniverse.agent.action.knowledge.doc_processor.\
    sensitive_data_redactor import SensitiveDataRedactor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(sdr_module.__file__),
                          "sensitive_data_redactor.yaml")


def _run(text, **kwargs):
    out = SensitiveDataRedactor(**kwargs).process_docs([Document(text=text)])
    return out[0]


class TestSensitiveDataEntities(unittest.TestCase):
    """Each built-in entity is detected and replaced."""

    def test_redacts_email(self) -> None:
        doc = _run("contact alice@example.com please")
        self.assertNotIn("alice@example.com", doc.text)
        self.assertIn("[REDACTED]", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"], {"email": 1})

    def test_redacts_credit_card(self) -> None:
        doc = _run("card 4111111111111111 done")
        self.assertNotIn("4111111111111111", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"], {"credit_card": 1})

    def test_redacts_china_id_card(self) -> None:
        doc = _run("id 110101199003073917 end")
        self.assertNotIn("110101199003073917", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"], {"id_card": 1})

    def test_redacts_ssn(self) -> None:
        doc = _run("ssn 123-45-6789 here")
        self.assertNotIn("123-45-6789", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"], {"ssn": 1})

    def test_redacts_ip_address(self) -> None:
        doc = _run("server 10.0.0.1 ready")
        self.assertNotIn("10.0.0.1", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"], {"ip_address": 1})

    def test_redacts_api_key(self) -> None:
        doc = _run("key sk-abcdefghijklmnopqrstuvwxyz end")
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"], {"api_key": 1})

    def test_phone_not_redacted_by_default(self) -> None:
        # phone is opt-in: absent from the default entity set.
        doc = _run("call 13812345678 now")
        self.assertIn("13812345678", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"], {})

    def test_phone_redacted_when_enabled(self) -> None:
        doc = _run("call 13812345678 now", entities=["phone"])
        self.assertNotIn("13812345678", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"], {"phone": 1})

    def test_multiple_entities_in_one_doc(self) -> None:
        text = "mail alice@example.com or ip 10.0.0.1"
        doc = _run(text)
        self.assertNotIn("alice@example.com", doc.text)
        self.assertNotIn("10.0.0.1", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"],
                         {"email": 1, "ip_address": 1})

    def test_no_pii_leaves_text_unchanged_but_stamps_empty_summary(self) -> None:
        doc = _run("just a plain sentence with nothing sensitive")
        self.assertEqual(doc.text, "just a plain sentence with nothing sensitive")
        self.assertEqual(doc.metadata["redaction_summary"], {})


class TestSensitiveDataConfig(unittest.TestCase):
    """Replacement, custom patterns, summary, and graceful degradation."""

    def test_custom_replacement(self) -> None:
        doc = _run("mail alice@example.com", replacement="[HIDDEN]")
        self.assertIn("[HIDDEN]", doc.text)
        self.assertNotIn("alice@example.com", doc.text)

    def test_custom_pattern_redacts(self) -> None:
        doc = _run("emp EMP-123456 here", custom_patterns=[
            {"name": "employee_id", "pattern": r"\bEMP-\d{6}\b"}])
        self.assertNotIn("EMP-123456", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"],
                         {"employee_id": 1})

    def test_invalid_custom_regex_is_skipped(self) -> None:
        # An invalid regex must not crash processing; valid ones still apply.
        doc = _run("mail alice@example.com", custom_patterns=[
            {"name": "bad", "pattern": "("}])
        self.assertNotIn("alice@example.com", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"], {"email": 1})

    def test_custom_pattern_missing_fields_is_skipped(self) -> None:
        doc = _run("mail alice@example.com", custom_patterns=[
            {"name": "no_pattern"}])
        self.assertNotIn("alice@example.com", doc.text)

    def test_unknown_entity_is_skipped(self) -> None:
        doc = _run("mail alice@example.com", entities=["email", "mystery"])
        self.assertNotIn("alice@example.com", doc.text)
        self.assertEqual(doc.metadata["redaction_summary"], {"email": 1})

    def test_log_key_none_omits_summary(self) -> None:
        doc = _run("mail alice@example.com", log_key=None)
        self.assertNotIn("alice@example.com", doc.text)
        self.assertNotIn("redaction_summary", doc.metadata or {})

    def test_preserves_existing_metadata(self) -> None:
        original = Document(text="ip 10.0.0.1", metadata={"source": "log.txt"})
        out = SensitiveDataRedactor().process_docs([original])
        self.assertEqual(out[0].metadata["source"], "log.txt")
        self.assertEqual(out[0].metadata["redaction_summary"],
                         {"ip_address": 1})

    def test_attributes_loaded_from_configer(self) -> None:
        configer = SimpleNamespace(
            name="sdr", description="d",
            entities=["email"], replacement="<H>",
            custom_patterns=[{"name": "x", "pattern": r"x"}], log_key=None)
        proc = SensitiveDataRedactor() \
            ._initialize_by_component_configer(configer)
        self.assertEqual(proc.entities, ["email"])
        self.assertEqual(proc.replacement, "<H>")
        self.assertEqual(proc.custom_patterns, [{"name": "x", "pattern": "x"}])
        self.assertIsNone(proc.log_key)


class TestSensitiveDataRegistration(unittest.TestCase):
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
            "sensitive_data_redactor")
        self.assertEqual(component_configer.metadata_class,
                         "SensitiveDataRedactor")


class TestSensitiveDataThroughKnowledgePipeline(unittest.TestCase):
    """The redactor runs as a real post_processor through query_knowledge."""

    def test_redacts_in_the_pipeline(self) -> None:
        from agentuniverse.agent.action.knowledge import knowledge as \
            knowledge_module
        from agentuniverse.agent.action.knowledge.knowledge import Knowledge
        import agentuniverse.base.annotation.trace as trace_module

        class _FakeStore:
            def query(self, query):
                return [Document(text="reach alice@example.com or 10.0.0.1")]

        redactor = SensitiveDataRedactor()
        knowledge = Knowledge(
            name="sdr_knowledge",
            stores=["only_store"],
            rag_router="base_router",
            post_processors=["sensitive_data_redactor"],
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
            proc_mgr.return_value.get_instance_obj.return_value = redactor
            out = knowledge.query_knowledge(query_str="q")

        self.assertNotIn("alice@example.com", out[0].text)
        self.assertNotIn("10.0.0.1", out[0].text)
        self.assertEqual(out[0].metadata["redaction_summary"],
                         {"email": 1, "ip_address": 1})


if __name__ == '__main__':
    unittest.main()
