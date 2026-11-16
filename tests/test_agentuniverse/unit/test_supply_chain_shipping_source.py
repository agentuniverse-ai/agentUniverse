"""Regression coverage for source-bound shipping relationships."""

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.supply_chain_entity_extractor import (
    Entity, SupplyChainEntityExtractor,
)


@pytest.mark.parametrize('shipping_clause', [
    'Acme shipped to Depot.',
    'Acme was shipped to the Depot.',
    'Acme were shipped to Depot.',
    'Acme SHIPPED TO THE Depot.',
])
def test_shipping_requires_the_actual_source(shipping_clause):
    processor = SupplyChainEntityExtractor(use_llm=False)
    entities = [Entity(name=name, entity_type='supplier')
                for name in ('Acme', 'Unrelated', 'Depot')]

    relationships = processor._extract_relationships_with_patterns(
        f'{shipping_clause} Unrelated is a separate company.', entities)
    shipping_pairs = {(item.source, item.target) for item in relationships
                      if item.relationship_type == 'ships_to'}

    assert shipping_pairs == {('Acme', 'Depot')}


def test_shipping_without_named_source_does_not_invent_one():
    processor = SupplyChainEntityExtractor(use_llm=False)
    entities = [Entity(name=name, entity_type='supplier')
                for name in ('Unrelated', 'Depot')]

    relationships = processor._extract_relationships_with_patterns(
        'Goods were shipped to the Depot. Unrelated is a separate company.',
        entities)

    assert not any(item.relationship_type == 'ships_to'
                   for item in relationships)


def test_existing_active_shipping_pattern_is_preserved():
    processor = SupplyChainEntityExtractor(use_llm=False)
    entities = [Entity(name=name, entity_type='supplier')
                for name in ('Acme', 'Depot')]
    relationships = processor._extract_relationships_with_patterns(
        'Acme ships components to Depot.', entities)
    assert any(item.source == 'Acme' and item.target == 'Depot'
               and item.relationship_type == 'ships_to'
               for item in relationships)
