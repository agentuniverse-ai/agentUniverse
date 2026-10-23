"""Synthetic numeric identifiers are redacted next to multilingual prose."""

from unittest.mock import MagicMock, patch

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.sensitive_data_redactor import SensitiveDataRedactor
from agentuniverse.agent.action.knowledge.store.document import Document

# Test-only values, including the standard China ID checksum example and a
# payment-card test number. No personal records or live services are loaded.
NUMERIC_ENTITIES = [
    ("credit_card", "4111111111111111"),
    ("id_card", "11010519491231002X"),
    ("ssn", "123-45-6789"),
    ("ip_address", "192.0.2.1"),
    ("phone", "13800000000"),
]


def _redact(text, entity):
    doc = Document(text=text)
    SensitiveDataRedactor(entities=[entity]).process_docs([doc])
    return doc


@pytest.mark.parametrize(("entity", "value"), NUMERIC_ENTITIES)
@pytest.mark.parametrize(
    ("prefix", "suffix"),
    [("联系", ""), ("", "已确认"), ("联系", "已确认")],
    ids=["Chinese-before", "Chinese-after", "Chinese-both-sides"],
)
def test_redacts_numeric_entities_touching_chinese_prose(entity, value, prefix, suffix):
    doc = _redact(prefix + value + suffix, entity)

    assert doc.text == prefix + "[REDACTED]" + suffix
    assert doc.metadata["redaction_summary"] == {entity: 1}


@pytest.mark.parametrize(("entity", "value"), NUMERIC_ENTITIES)
def test_does_not_extract_entities_from_ascii_identifiers_or_longer_digit_runs(entity, value):
    # Extending the final IPv4 octet by one digit can produce another valid
    # address. Use an overlong octet to test protection against partial matches.
    digit_suffix = "0000" if entity == "ip_address" else "0"
    unicode_digit_suffix = "\uff10000" if entity == "ip_address" else "\uff10"
    embedded = [
        "A" + value,
        value + "z",
        "_" + value,
        value + "_",
        "0" + value,
        value + digit_suffix,
        "\u0660" + value,
        value + unicode_digit_suffix,
    ]

    for text in embedded:
        doc = _redact(text, entity)
        assert doc.text == text, text
        assert doc.metadata["redaction_summary"] == {}, text


@pytest.mark.parametrize(
    ("entity", "value"),
    [
        ("credit_card", "1234567890123456"),
        ("id_card", "110105194912310020"),
        ("ssn", "000-12-3456"),
        ("ip_address", "999.999.999.999"),
    ],
)
def test_chinese_prose_does_not_bypass_semantic_validation(entity, value):
    text = "联系" + value + "已确认"

    doc = _redact(text, entity)

    assert doc.text == text
    assert doc.metadata["redaction_summary"] == {}


def test_phone_remains_opt_in_for_chinese_prose():
    text = "电话13800000000已确认"
    doc = Document(text=text)

    SensitiveDataRedactor().process_docs([doc])

    assert doc.text == text
    assert doc.metadata["redaction_summary"] == {}


def test_custom_word_boundaries_keep_unicode_semantics():
    doc = Document(text="编号EMP-123456已登记; EMP-123456")
    processor = SensitiveDataRedactor(
        entities=[],
        custom_patterns=[{"name": "employee", "pattern": r"\bEMP-\d{6}\b"}],
    )

    processor.process_docs([doc])

    assert doc.text == "编号EMP-123456已登记; [REDACTED]"
    assert doc.metadata["redaction_summary"] == {"employee": 1}


def test_non_ascii_prose_can_touch_numeric_entities():
    doc = _redact("é11010519491231002XΩ", "id_card")

    assert doc.text == "é[REDACTED]Ω"
    assert doc.metadata["redaction_summary"] == {"id_card": 1}


@pytest.mark.parametrize("prefix", ["", "Call", "电话"])
def test_parenthesized_us_phone_is_redacted_completely(prefix):
    # The 555-0100 through 555-0199 range is reserved for fictional use.
    doc = _redact(prefix + "(202) 555-0100", "phone")

    assert doc.text == prefix + "[REDACTED]"
    assert doc.metadata["redaction_summary"] == {"phone": 1}


def test_knowledge_pipeline_redacts_chinese_source_before_llm_conversion():
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.store.query import Query

    source = Document(
        text="身份证11010519491231002X已确认\uff0c电话13800000000已登记。",
        metadata={"source": "synthetic-profile", "document_type": "fixture"},
    )

    class FakeStore:
        def query(self, query):
            return [source]

    processor = SensitiveDataRedactor(entities=["id_card", "phone"])
    knowledge = Knowledge(
        name="prose-boundary-knowledge",
        stores=["synthetic_store"],
        post_processors=["sensitive_data_redactor"],
    )
    router = MagicMock()
    router.rag_route.return_value = [(Query(query_str="profile"), "synthetic_store")]

    try:
        with (
            patch.object(trace_module, "ConversationMemoryModule"),
            patch.object(trace_module, "Monitor") as monitor,
            patch.object(knowledge_module, "RagRouterManager") as router_manager,
            patch.object(knowledge_module, "StoreManager") as store_manager,
            patch.object(knowledge_module, "DocProcessorManager") as processor_manager,
        ):
            monitor.get_invocation_chain.return_value = []
            router_manager.return_value.get_instance_obj.return_value = router
            store_manager.return_value.get_instance_obj.return_value = FakeStore()
            processor_manager.return_value.get_instance_obj.return_value = processor

            docs = knowledge.query_knowledge(query_str="profile")
            llm_text = knowledge.to_llm(docs)
    finally:
        knowledge.query_executor.shutdown(wait=True)
        knowledge.insert_executor.shutdown(wait=True)

    assert len(docs) == 1
    assert docs[0] is source
    assert llm_text == "身份证[REDACTED]已确认\uff0c电话[REDACTED]已登记。"
    assert docs[0].metadata == {
        "source": "synthetic-profile",
        "document_type": "fixture",
        "redaction_summary": {"id_card": 1, "phone": 1},
    }
