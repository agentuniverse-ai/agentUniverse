"""Clause provenance must not alias the source or sibling clause metadata."""
from copy import deepcopy

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.contract_clause_fragmenter import ContractClauseFragmenter
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.fixture(params=[True, False], ids=['structured', 'unstructured'])
def source(request):
    text = ('Section 1 Scope\nThis agreement covers service delivery.\n'
            'Section 2 Payment\nPayment is due within thirty days.') if request.param else 'This agreement covers service delivery and payment.'
    return Document(text=text, metadata={'provenance': {'pages': [1, 2]},
                    'review': [{'approved': False}]}, keywords={'contract'})


def process(source):
    return ContractClauseFragmenter(skip_on_error=False).process_docs([source])


def test_clause_metadata_mutations_do_not_change_source(source):
    original = deepcopy(source.metadata)
    clauses = process(source)
    clauses[0].metadata['original_metadata']['provenance']['pages'].append(3)
    clauses[0].metadata['original_metadata']['review'][0]['approved'] = True
    assert source.metadata == original
    for other in clauses[1:]:
        assert other.metadata['original_metadata'] == original


def test_source_mutations_do_not_change_clause_metadata(source):
    original = deepcopy(source.metadata)
    clauses = process(source)
    source.metadata['provenance']['pages'].clear()
    source.metadata['review'][0]['approved'] = True
    assert all(clause.metadata['original_metadata'] == original for clause in clauses)


def test_repeated_processing_has_independent_metadata(source):
    first = process(source)
    second = process(source)
    first[0].metadata['original_metadata']['provenance']['pages'].append(42)
    assert all(clause.metadata['original_metadata']['provenance']['pages'] == [1, 2]
               for clause in second)


def test_metadata_values_and_clause_fields_preserved(source):
    clauses = process(source)
    assert len(clauses) == (2 if source.text.startswith('Section') else 1)
    for clause in clauses:
        assert clause.metadata['original_metadata'] == source.metadata
        assert clause.metadata['source_document_id'] == source.id
        assert clause.text in source.text
        assert clause.keywords == source.keywords
