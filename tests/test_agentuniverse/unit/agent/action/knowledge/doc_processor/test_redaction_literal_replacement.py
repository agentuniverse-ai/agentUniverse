"""Configured replacement text must never expand a regex backreference."""

import pytest
from types import SimpleNamespace

from agentuniverse.agent.action.knowledge.doc_processor.sensitive_data_redactor import SensitiveDataRedactor
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize("replacement", [r"\g<0>", r"\1", r"C:\redacted\unknown", r"\n", "", "[MASK]"])
@pytest.mark.parametrize("custom", [False, True])
def test_replacement_is_literal_for_builtin_and_custom_patterns(replacement, custom):
    processor = SensitiveDataRedactor(
        entities=[] if custom else ["email"],
        replacement=replacement,
        custom_patterns=[{"name": "contact", "pattern": r"([a-z]+)@example\.com"}] if custom else [],
    )
    doc = Document(text="alice@example.com; bob@example.com", metadata={"source": "fixture"})
    result = processor.process_docs([doc])
    assert result[0] is doc
    assert doc.text == f"{replacement}; {replacement}"
    assert "alice" not in doc.text and "bob" not in doc.text
    assert doc.metadata == {"source": "fixture", "redaction_summary": {"contact" if custom else "email": 2}}


def test_validated_and_unvalidated_entities_use_the_same_literal_policy():
    replacement = r"\g<0>"
    doc = Document(text="alice@example.com 192.0.2.1 999.999.999.999")
    SensitiveDataRedactor(entities=["email", "ip_address"], replacement=replacement).process_docs([doc])
    assert doc.text == replacement + " " + replacement + " 999.999.999.999"
    assert doc.metadata["redaction_summary"] == {"email": 1, "ip_address": 1}


@pytest.mark.parametrize("text", ["alice@example.com", "ordinary text without a match", ""])
def test_unknown_backreference_is_literal_even_without_matches(text):
    doc = Document(text=text)
    SensitiveDataRedactor(entities=["email"], replacement=r"\g<missing>").process_docs([doc])
    assert doc.text == (r"\g<missing>" if "@" in text else text)


def test_configured_named_backreference_is_not_expanded():
    processor = SensitiveDataRedactor()
    processor._initialize_by_component_configer(
        SimpleNamespace(
            name="literal",
            description="fixture",
            entities=[],
            replacement=r"\g<contact>",
            custom_patterns=[{"name": "contact", "pattern": r"(?P<contact>[a-z]+@example\.com)"}],
            log_key=None,
        )
    )
    doc = Document(text="alice@example.com", metadata={"source": "original"})
    assert processor.process_docs([doc])[0].text == r"\g<contact>"
    assert doc.metadata == {"source": "original"}


def test_multiple_documents_keep_independent_counts_and_metadata():
    docs = [
        Document(text="alice@example.com", metadata={"source": "one"}),
        Document(text="ordinary text", metadata={"source": "two"}),
    ]
    result = SensitiveDataRedactor(entities=["email"], replacement=r"\1").process_docs(docs)
    assert result is docs
    assert [doc.text for doc in docs] == [r"\1", "ordinary text"]
    assert [doc.metadata for doc in docs] == [
        {"source": "one", "redaction_summary": {"email": 1}},
        {"source": "two", "redaction_summary": {}},
    ]
