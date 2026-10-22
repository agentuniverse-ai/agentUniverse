"""Article numbers must be captured after the heading keyword."""
import pytest
from agentuniverse.agent.action.knowledge.doc_processor.contract_clause_fragmenter import ContractClauseFragmenter
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('header,expected', [
    ('ARTICLE II Payment', 'article_II'), ('ARTICLE 12 Payment', 'article_12'),
    ('Article IV Duties', 'article_IV'), ('article ix Duties', 'article_IX'),
])
def test_article_header_captures_number(header, expected):
    assert ContractClauseFragmenter()._parse_clause_header(header) == ('article', expected)


def test_uppercase_articles_have_distinct_parent_links():
    text = 'ARTICLE I Duties\nSection 1.1 First obligation\nARTICLE II Payment\nSection 2.1 Second obligation'
    docs = ContractClauseFragmenter(min_clause_length=1).process_docs([Document(text=text)])
    assert [doc.metadata['clause_id'] for doc in docs] == ['article_I', 'section_1.1', 'article_II', 'section_2.1']
    assert docs[1].metadata['parent_clause'] == 'article_I'
    assert docs[3].metadata['parent_clause'] == 'article_II'
    assert docs[0].metadata['children_clauses'] == ['section_1.1']
    assert docs[2].metadata['children_clauses'] == ['section_2.1']
