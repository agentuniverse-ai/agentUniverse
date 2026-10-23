"""Summary metadata must not mutate retrieved source documents."""
from copy import deepcopy
from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.summarization_processor import SummarizationProcessor
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.fixture(params=['extractive', 'llm'])
def processor(request, monkeypatch):
    processor = SummarizationProcessor(llm_name='test_llm' if request.param == 'llm' else None)
    monkeypatch.setattr(SummarizationProcessor, '_get_llm',
                        lambda self: SimpleNamespace(call=lambda **kwargs: SimpleNamespace(text='Summary.')))
    return processor


def source_document():
    return Document(text='A useful source sentence.', metadata={
        'provenance': {'pages': [1, 2], 'attributes': {'reviewed': False}},
        'labels': [{'name': 'original'}],
        'source_doc_count': 999,
        'summarization_mode': 'source',
        'llm_name': 'source_llm',
    })


def test_summary_mutations_do_not_modify_source(processor):
    source = source_document()
    original = deepcopy(source.metadata)
    summary = processor.process_docs([source])[0]
    summary.metadata['provenance']['pages'].append(3)
    summary.metadata['provenance']['attributes']['reviewed'] = True
    summary.metadata['labels'][0]['name'] = 'edited'
    assert source.metadata == original


def test_source_mutations_do_not_modify_summary(processor):
    source = source_document()
    summary = processor.process_docs([source])[0]
    original = deepcopy(summary.metadata)
    source.metadata['provenance']['pages'].clear()
    source.metadata['labels'][0]['name'] = 'changed'
    assert summary.metadata == original


def test_repeated_summaries_have_independent_metadata(processor):
    source = source_document()
    first = processor.process_docs([source])[0]
    second = processor.process_docs([source])[0]
    first.metadata['provenance']['pages'].append(42)
    assert second.metadata['provenance']['pages'] == [1, 2]


def test_metadata_values_and_reserved_keys_preserved(processor):
    source = source_document()
    result = processor.process_docs([source])[0]
    assert result.metadata['provenance'] == source.metadata['provenance']
    assert result.metadata['source_doc_count'] == 1
    assert result.metadata['summarization_mode'] == ('llm' if processor.llm_name else 'extractive')
    assert result.metadata['llm_name'] == processor.llm_name


@pytest.mark.parametrize('metadata', [None, {}])
def test_empty_metadata(processor, metadata):
    result = processor.process_docs([Document(text='Source sentence.', metadata=metadata)])[0]
    assert set(result.metadata) == {'source_doc_count', 'summarization_mode', 'llm_name'}
