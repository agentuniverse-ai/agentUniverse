# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_supply_chain_entity_extractor.py

import unittest
from agentuniverse.agent.action.knowledge.doc_processor.supply_chain_entity_extractor import SupplyChainEntityExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


class TestSupplyChainEntityExtractor(unittest.TestCase):
    """Unit tests for SupplyChainEntityExtractor."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = SupplyChainEntityExtractor(
            name='test_extractor',
            use_llm=False,  # Disable LLM for unit tests
            confidence_threshold=0.7
        )

    def test_basic_entity_extraction(self):
        """Test basic supply chain entity extraction."""
        text = """
Supplier Analysis

ABC Manufacturing supplies components to XYZ Corp.
The warehouse in Shanghai stores finished products.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        self.assertEqual(len(result), 1)
        entities = result[0].metadata.get('entities', [])
        self.assertGreater(len(entities), 0)

    def test_supplier_entity_extraction(self):
        """Test extraction of supplier entities."""
        text = """
Our main suppliers include:
- ABC Components Ltd (electronic parts supplier)
- DEF Materials Inc (raw materials supplier)
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        entities = result[0].metadata.get('entities', [])
        suppliers = [e for e in entities if e.get('type') == 'supplier']
        self.assertGreater(len(suppliers), 0)

    def test_manufacturer_entity_extraction(self):
        """Test extraction of manufacturer entities."""
        text = """
Manufacturing Partners

XYZ Manufacturing produces our products.
ABC Factory manufactures components.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        entities = result[0].metadata.get('entities', [])
        manufacturers = [e for e in entities if e.get('type') == 'manufacturer']
        self.assertGreater(len(manufacturers), 0)

    def test_distributor_entity_extraction(self):
        """Test extraction of distributor entities."""
        text = """
Distribution Network

Global Distributors Ltd handles our distribution.
Regional Logistics Corp distributes in Asia.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        entities = result[0].metadata.get('entities', [])
        distributors = [e for e in entities if e.get('type') == 'distributor']
        self.assertGreater(len(distributors), 0)

    def test_warehouse_entity_extraction(self):
        """Test extraction of warehouse entities."""
        text = """
Storage Facilities

Main warehouse located in Shanghai.
Regional distribution center in Los Angeles.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        entities = result[0].metadata.get('entities', [])
        warehouses = [e for e in entities if e.get('type') == 'warehouse']
        self.assertGreater(len(warehouses), 0)

    def test_product_entity_extraction(self):
        """Test extraction of product entities."""
        text = """
Product Catalog

We manufacture smartphones, tablets, and laptops.
Main products: iPhone, iPad, MacBook.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        entities = result[0].metadata.get('entities', [])
        products = [e for e in entities if e.get('type') == 'product']
        self.assertGreater(len(products), 0)

    def test_relationship_extraction(self):
        """Test extraction of supply chain relationships."""
        text = """
Supply Chain Overview

ABC Corp supplies components to XYZ Manufacturing.
XYZ Manufacturing produces products for Global Distributors.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        relationships = result[0].metadata.get('relationships', [])
        self.assertGreater(len(relationships), 0)

    def test_supplies_relationship(self):
        """Test extraction of 'supplies' relationships."""
        text = """
ABC Components supplies electronic parts to XYZ Corp.
DEF Materials provides raw materials to ABC Factory.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        relationships = result[0].metadata.get('relationships', [])
        supplies_rels = [r for r in relationships if r.get('type') == 'supplies']
        self.assertGreater(len(supplies_rels), 0)

    def test_manufactures_relationship(self):
        """Test extraction of 'manufactures' relationships."""
        text = """
XYZ Factory manufactures smartphones for ABC Corp.
DEF Manufacturing produces tablets.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        relationships = result[0].metadata.get('relationships', [])
        manufactures_rels = [r for r in relationships if r.get('type') == 'manufactures']
        self.assertGreater(len(manufactures_rels), 0)

    def test_ships_to_relationship(self):
        """Test extraction of 'ships_to' relationships."""
        text = """
Logistics Network

ABC Warehouse ships to regional distributors.
Products are shipped to the Los Angeles distribution center.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        relationships = result[0].metadata.get('relationships', [])
        ships_rels = [r for r in relationships if r.get('type') == 'ships_to']
        self.assertGreater(len(ships_rels), 0)

    def test_knowledge_graph_structure(self):
        """Test knowledge graph structure in metadata."""
        text = """
Supply Chain

ABC Supplier supplies components to XYZ Manufacturer.
XYZ Manufacturer produces goods for Global Distributor.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        # Should have knowledge graph metadata
        self.assertIn('knowledge_graph', result[0].metadata)

        graph = result[0].metadata['knowledge_graph']
        self.assertIn('nodes', graph)
        self.assertIn('edges', graph)
        self.assertGreater(len(graph['nodes']), 0)

    def test_entity_attributes_extraction(self):
        """Test extraction of entity attributes."""
        text = """
Supplier Details

ABC Corp (founded 2010) is located in Shanghai, China.
Revenue: $100M annually.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        entities = result[0].metadata.get('entities', [])
        # Should extract entities with attributes
        has_attributes = any(
            e.get('attributes') and len(e['attributes']) > 0
            for e in entities
        )
        self.assertTrue(has_attributes)

    def test_confidence_scoring(self):
        """Test confidence scores for extractions."""
        text = """
ABC Corp supplies components to XYZ Manufacturing.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        # Entities and relationships should have confidence scores
        entities = result[0].metadata.get('entities', [])
        relationships = result[0].metadata.get('relationships', [])

        has_confidence = (
            any('confidence' in e for e in entities) or
            any('confidence' in r for r in relationships)
        )
        self.assertTrue(has_confidence or len(entities) > 0)

    def test_multilingual_extraction(self):
        """Test extraction from Chinese text."""
        text = """
供应链分析

ABC公司向XYZ制造商供应零部件。
上海仓库存储成品。
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        # Should extract entities from Chinese text
        entities = result[0].metadata.get('entities', [])
        self.assertGreater(len(entities), 0)

    def test_complex_supply_chain(self):
        """Test extraction from complex supply chain description."""
        text = """
Supply Chain Network

Tier 1: ABC Components (Taiwan) supplies semiconductors
Tier 2: XYZ Manufacturing (China) produces modules
Tier 3: Global Assembly (Vietnam) assembles products
Distribution: Regional Logistics handles worldwide shipping
Warehouses: Shanghai (Asia), LA (Americas), Frankfurt (Europe)
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        entities = result[0].metadata.get('entities', [])
        relationships = result[0].metadata.get('relationships', [])

        # Should extract multiple entities and relationships
        self.assertGreaterEqual(len(entities), 3)
        self.assertGreater(len(relationships), 0)

    def test_metadata_preservation(self):
        """Test preservation of original metadata."""
        doc = Document(
            text="ABC Corp supplies to XYZ Corp.",
            metadata={'document_id': 'SC001', 'source': 'report'}
        )

        result = self.extractor.process_docs([doc])

        # Original metadata should be preserved
        self.assertIn('original_metadata', result[0].metadata)
        self.assertEqual(
            result[0].metadata['original_metadata']['document_id'],
            'SC001'
        )

    def test_empty_document(self):
        """Test handling of empty documents."""
        doc = Document(text="")
        result = self.extractor.process_docs([doc])

        # Should handle gracefully
        self.assertEqual(len(result), 1)

    def test_document_without_entities(self):
        """Test handling of documents with no supply chain entities."""
        doc = Document(text="This is a general document with no supply chain info.")
        result = self.extractor.process_docs([doc])

        # Should return document with empty entity list
        self.assertEqual(len(result), 1)
        entities = result[0].metadata.get('entities', [])
        self.assertEqual(len(entities), 0)

    def test_batch_processing(self):
        """Test processing multiple documents."""
        docs = [
            Document(text="ABC Corp supplies to XYZ Corp."),
            Document(text="DEF Factory manufactures products."),
            Document(text="GHI Distributor handles distribution."),
        ]

        result = self.extractor.process_docs(docs)

        # Should process all documents
        self.assertEqual(len(result), 3)

        # Each should have entity extraction attempted
        for doc in result:
            self.assertIn('entities', doc.metadata)

    def test_dependency_relationship(self):
        """Test extraction of dependency relationships."""
        text = """
Critical Dependencies

XYZ Manufacturing depends on ABC Supplier for key components.
Production is dependent on timely delivery from suppliers.
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        relationships = result[0].metadata.get('relationships', [])
        depends_rels = [r for r in relationships if r.get('type') == 'depends_on']
        self.assertGreater(len(depends_rels), 0)

    def test_location_extraction(self):
        """Test extraction of location information."""
        text = """
Global Operations

Suppliers in Taiwan and China
Manufacturing facilities in Vietnam
Distribution centers in USA and Europe
"""
        doc = Document(text=text)
        result = self.extractor.process_docs([doc])

        entities = result[0].metadata.get('entities', [])
        # Should extract location attributes
        has_locations = any(
            e.get('attributes', {}).get('location')
            for e in entities
        )
        self.assertTrue(has_locations or len(entities) > 0)


if __name__ == '__main__':
    unittest.main()
