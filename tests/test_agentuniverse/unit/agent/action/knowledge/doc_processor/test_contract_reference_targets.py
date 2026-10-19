"""Resolve reference identifiers, never mentions in unrelated clause bodies."""
from agentuniverse.agent.action.knowledge.doc_processor.contract_clause_fragmenter import ClauseNode, ContractClauseFragmenter
from agentuniverse.agent.action.knowledge.store.document import Document


def node(identifier, text):
    return ClauseNode(identifier, text, 'section', 1)


def test_exact_identifier_excludes_prefixes_and_incidental_mentions():
    clauses = [node('section_1', 'Section 1 Rules'), node('section_10', 'Section 10 Payment'),
               node('section_2', 'Section 2 As provided in Section 1, perform duties.')]
    assert ContractClauseFragmenter()._extract_references('See Section 1.', clauses) == ['section_1']


def test_reference_aliases_order_deduplication_and_missing_targets():
    clauses = [node('article_IV', 'Article IV'), node('section_1.2', 'Section 1.2'),
               node('clause_3.1', '3.1 Duties'), node('article_一', '第一条')]
    text = 'Section 1.2, Article iv, clause 3.1, 第一条. Section 1.2 and Section 99.'
    assert ContractClauseFragmenter()._extract_references(text, clauses) == [
        'article_IV', 'section_1.2', 'clause_3.1', 'article_一',
    ]


def test_pipeline_uses_clause_identity_for_numbered_references():
    text = '1. Main obligations refer to clause 2.\n2. Secondary obligations are binding.'
    result = ContractClauseFragmenter(min_clause_length=1).process_docs([Document(text=text)])
    assert result[0].metadata['clause_references'] == ['clause_2']


def test_duplicate_local_identifiers_are_not_arbitrarily_resolved():
    clauses = [node('section_1', 'Section 1 A'), node('section_1', 'Section 1 B')]
    assert ContractClauseFragmenter()._extract_references('Section 1', clauses) == ['section_1']
