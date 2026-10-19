"""Configured replacement strings have identical literal semantics for all rules."""
import pytest
from agentuniverse.agent.action.knowledge.doc_processor.sensitive_data_redactor import SensitiveDataRedactor
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('replacement', [r'\1', r'\g<0>', r'C:\masked\user', '\\n', '[REDACTED]', ''])
@pytest.mark.parametrize('entity,text', [('email', 'alice@example.com'), ('ip_address', '192.168.1.1')])
def test_replacement_is_literal_for_builtin_entities(replacement, entity, text):
    doc = Document(text=text)
    result = SensitiveDataRedactor(entities=[entity], replacement=replacement).process_docs([doc])
    assert result[0].text == replacement
    assert result[0].metadata['redaction_summary'] == {entity: 1}


def test_custom_capture_cannot_reinsert_sensitive_match():
    doc = Document(text='secret-123 and secret-456')
    result = SensitiveDataRedactor(entities=[], replacement=r'\g<0>',
        custom_patterns=[{'name': 'secret', 'pattern': r'(secret-\d+)'}]).process_docs([doc])
    assert result[0].text == r'\g<0> and \g<0>'
    assert result[0].metadata['redaction_summary'] == {'secret': 2}
