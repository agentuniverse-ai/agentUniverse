"""Several patterns for one entity contribute to one accurate audit count."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.sensitive_data_redactor import SensitiveDataRedactor
from agentuniverse.agent.action.knowledge.store.document import Document

A = {'name': 'account', 'pattern': r'A-\d+'}
B = {'name': 'account', 'pattern': r'B-\d+'}


@pytest.mark.parametrize('log_key', ['redaction_summary', 'audit'])
def test_custom_patterns_with_shared_name_accumulate_counts(log_key):
    document = Document(text='A-1 A-2 B-3 B-4 B-5', metadata={'source': 'report'})
    result = SensitiveDataRedactor(entities=[], custom_patterns=[A, B], log_key=log_key).process_docs([document])
    assert result[0] is document
    assert document.text == ' '.join(['[REDACTED]'] * 5)
    assert document.metadata[log_key] == {'account': 5}
    assert document.metadata['source'] == 'report'


def test_builtin_validated_pattern_and_custom_extension_share_count():
    document = Document(text='4111111111111111 CARD-1234')
    SensitiveDataRedactor(entities=['credit_card'], custom_patterns=[
        {'name': 'credit_card', 'pattern': r'CARD-\d+'}]).process_docs([document])
    assert document.text == '[REDACTED] [REDACTED]'
    assert document.metadata['redaction_summary'] == {'credit_card': 2}


def test_counts_are_independent_for_each_document():
    documents = [Document(text='A-1 A-2 B-3'), Document(text='A-4')]
    SensitiveDataRedactor(entities=[], custom_patterns=[A, B]).process_docs(documents)
    assert [doc.metadata['redaction_summary'] for doc in documents] == [{'account': 3}, {'account': 1}]


def test_distinct_entity_names_keep_separate_counts():
    document = Document(text='A-1 A-2 B-3')
    SensitiveDataRedactor(entities=[], custom_patterns=[A, {'name': 'other', 'pattern': B['pattern']}]).process_docs([document])
    assert document.metadata['redaction_summary'] == {'account': 2, 'other': 1}


def test_second_pattern_with_no_remaining_matches_does_not_double_count():
    document = Document(text='A-1 A-2')
    SensitiveDataRedactor(entities=[], custom_patterns=[A, A]).process_docs([document])
    assert document.metadata['redaction_summary'] == {'account': 2}
