"""Exercise public document processing with real framework output envelopes."""
import json
from unittest.mock import Mock, patch

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.supply_chain_entity_extractor import SupplyChainEntityExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.llm.llm_output import LLMOutput

MODULE = 'agentuniverse.agent.action.knowledge.doc_processor.supply_chain_entity_extractor'
ENTITIES = json.dumps({'entities': [
    {'name': 'Acme', 'type': 'supplier', 'confidence': .95},
    {'name': 'Orion', 'type': 'manufacturer', 'confidence': .96},
    {'name': 'Rejected', 'type': 'supplier', 'confidence': .1},
]})
RELATIONS = json.dumps({'relationships': [
    {'source': 'Acme', 'target': 'Orion', 'type': 'partners_with', 'confidence': .97},
    {'source': 'Acme', 'target': 'Orion', 'type': 'supplies', 'confidence': .1},
]})


def process(responses):
    llm = Mock()
    llm.call.side_effect = responses
    with patch(MODULE + '.LLMManager') as manager:
        manager.return_value.get_instance_obj.return_value = llm
        doc = SupplyChainEntityExtractor(llm_name='offline', use_llm=True).process_docs(
            [Document(text='Acme and Orion agreed to collaborate on battery research.')]
        )[0]
    return doc, llm


@pytest.mark.parametrize('wrap_entities,wrap_relationships', [(True, True), (True, False), (False, True), (False, False)])
def test_framework_outputs_and_legacy_strings(wrap_entities, wrap_relationships):
    doc, llm = process([
        LLMOutput(text=ENTITIES) if wrap_entities else ENTITIES,
        LLMOutput(text=RELATIONS) if wrap_relationships else RELATIONS,
    ])
    assert [e['name'] for e in doc.metadata['entities']] == ['Acme', 'Orion']
    assert len(doc.metadata['relationships']) == 1
    relation = doc.metadata['relationships'][0]
    assert relation['type'] == 'partners_with'
    assert relation['confidence'] == .97
    assert llm.call.call_count == 2
    for call in llm.call.call_args_list:
        assert set(call.kwargs) == {'messages'}


@pytest.mark.parametrize('response', ['', LLMOutput(text=''), RuntimeError('offline failure')])
def test_empty_or_failed_entity_response_preserves_fallback(response):
    doc, llm = process([response])
    assert doc.metadata['entities'] == []
    assert doc.metadata['relationships'] == []
    assert llm.call.call_count == 1


@pytest.mark.parametrize('response', ['', LLMOutput(text='')])
def test_empty_relationship_response_stays_empty(response):
    doc, _ = process([ENTITIES, response])
    assert len(doc.metadata['entities']) == 2
    assert doc.metadata['relationships'] == []


def test_failed_relationship_call_keeps_existing_pattern_fallback():
    doc, _ = process([ENTITIES, RuntimeError('offline failure')])
    assert doc.metadata['relationships'][0]['type'] == 'supplies'
    assert doc.metadata['relationships'][0]['confidence'] == .6


@pytest.mark.parametrize('entity_response,relationship_response', [
    (True, False), (False, True),
])
def test_streaming_iterator_keeps_existing_pattern_fallback(entity_response, relationship_response):
    doc, _ = process([
        iter([LLMOutput(text=ENTITIES)]) if entity_response else ENTITIES,
        iter([LLMOutput(text=RELATIONS)]) if relationship_response else RELATIONS,
    ])
    if entity_response:
        assert doc.metadata['entities'] == []
        assert doc.metadata['relationships'] == []
    else:
        assert doc.metadata['relationships'][0]['type'] == 'supplies'
        assert doc.metadata['relationships'][0]['confidence'] == .6
