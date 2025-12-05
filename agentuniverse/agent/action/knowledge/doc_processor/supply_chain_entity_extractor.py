# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @Email   : ai@example.com
# @FileName: supply_chain_entity_extractor.py

import json
import logging
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from datetime import datetime

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an entity in the supply chain.

    Attributes:
        name: Entity name.
        entity_type: Type of entity (supplier, manufacturer, etc.).
        attributes: Additional attributes.
        confidence: Extraction confidence score.
    """
    name: str
    entity_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class Relationship:
    """Represents a relationship between entities.

    Attributes:
        source: Source entity name.
        target: Target entity name.
        relationship_type: Type of relationship.
        attributes: Additional attributes.
        confidence: Extraction confidence score.
    """
    source: str
    target: str
    relationship_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


class SupplyChainEntityExtractor(DocProcessor):
    """Extract supply chain entities and relationships from documents.

    This processor uses both pattern matching and LLM-based extraction to identify:
    1. Supply chain entities (suppliers, manufacturers, distributors, products)
    2. Relationships between entities (supplies, manufactures, ships_to)
    3. Knowledge graph structure for supply networks

    Attributes:
        entity_types: List of entity types to extract.
        relationship_types: List of relationship types to extract.
        use_llm: Whether to use LLM for entity extraction.
        llm_name: Name of the LLM to use.
        confidence_threshold: Minimum confidence for entity extraction.
        extract_attributes: Whether to extract entity attributes.
        skip_on_error: Whether to skip documents that fail processing.
    """

    entity_types: List[str] = None
    relationship_types: List[str] = None
    use_llm: bool = True
    llm_name: Optional[str] = None
    confidence_threshold: float = 0.7
    extract_attributes: bool = True
    skip_on_error: bool = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.entity_types is None:
            self.entity_types = [
                'supplier',
                'manufacturer',
                'distributor',
                'retailer',
                'product',
                'warehouse',
                'logistics_provider',
                'customer',
            ]
        if self.relationship_types is None:
            self.relationship_types = [
                'supplies',
                'manufactures',
                'distributes',
                'ships_to',
                'stores',
                'depends_on',
                'partners_with',
            ]

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Extract supply chain entities and relationships from documents.

        Args:
            origin_docs: List of supply chain documents.
            query: Optional query object (not used in this processor).

        Returns:
            List of documents with extracted entities and relationships.
        """
        if not origin_docs:
            return []

        logger.info(f"Starting supply chain entity extraction from {len(origin_docs)} documents")

        processed_docs = []

        for doc in origin_docs:
            try:
                enhanced_doc = self._extract_from_document(doc)
                processed_docs.append(enhanced_doc)
                logger.info(f"Extracted entities from document {doc.id}")
            except Exception as e:
                logger.error(f"Failed to extract from document {doc.id}: {e}")
                if not self.skip_on_error:
                    raise
                processed_docs.append(doc)

        logger.info(f"Entity extraction complete for {len(processed_docs)} documents")
        return processed_docs

    def _extract_from_document(self, doc: Document) -> Document:
        """Extract entities and relationships from a single document.

        Args:
            doc: Supply chain document.

        Returns:
            Document with extracted entities and relationships in metadata.
        """
        text = doc.text

        # Step 1: Extract entities
        entities = []
        if self.use_llm and self.llm_name:
            entities = self._extract_entities_with_llm(text)
        else:
            entities = self._extract_entities_with_patterns(text)

        logger.debug(f"Extracted {len(entities)} entities")

        # Step 2: Extract relationships
        relationships = []
        if len(entities) > 1:
            if self.use_llm and self.llm_name:
                relationships = self._extract_relationships_with_llm(text, entities)
            else:
                relationships = self._extract_relationships_with_patterns(text, entities)

        logger.debug(f"Extracted {len(relationships)} relationships")

        # Step 3: Build knowledge graph
        graph = self._build_knowledge_graph(entities, relationships)

        # Step 4: Create enhanced document
        enhanced_doc = self._create_enhanced_document(doc, entities, relationships, graph)

        return enhanced_doc

    def _extract_entities_with_llm(self, text: str) -> List[Entity]:
        """Extract entities using LLM.

        Args:
            text: Document text.

        Returns:
            List of Entity objects.
        """
        try:
            llm_manager = LLMManager()
            llm = llm_manager.get_instance_obj(self.llm_name)

            # Construct prompt
            prompt = self._build_entity_extraction_prompt(text)

            # Call LLM
            messages = [{"role": "user", "content": prompt}]
            response = llm.call(messages=messages)

            # Parse response
            entities = self._parse_llm_entity_response(response)

            # Filter by confidence
            entities = [e for e in entities if e.confidence >= self.confidence_threshold]

            return entities

        except Exception as e:
            logger.error(f"LLM entity extraction failed: {e}")
            # Fallback to pattern-based extraction
            return self._extract_entities_with_patterns(text)

    def _build_entity_extraction_prompt(self, text: str) -> str:
        """Build prompt for LLM entity extraction.

        Args:
            text: Document text.

        Returns:
            Prompt string.
        """
        entity_types_str = ', '.join(self.entity_types)

        prompt = f"""Extract supply chain entities from the following text.

Entity types to extract: {entity_types_str}

For each entity, provide:
1. Entity name
2. Entity type
3. Confidence score (0.0-1.0)

Text:
{text[:2000]}

Return results in JSON format:
{{
  "entities": [
    {{"name": "Entity Name", "type": "entity_type", "confidence": 0.9}}
  ]
}}
"""
        return prompt

    def _parse_llm_entity_response(self, response: str) -> List[Entity]:
        """Parse LLM response for entities.

        Args:
            response: LLM response text.

        Returns:
            List of Entity objects.
        """
        entities = []

        try:
            # Try to parse as JSON
            data = json.loads(response)
            entity_list = data.get('entities', [])

            for item in entity_list:
                entity = Entity(
                    name=item.get('name', ''),
                    entity_type=item.get('type', 'unknown'),
                    confidence=float(item.get('confidence', 0.5))
                )
                entities.append(entity)

        except json.JSONDecodeError:
            # Fallback: parse text format
            logger.warning("Failed to parse JSON response, using text parsing")
            entities = self._parse_text_entity_response(response)

        return entities

    def _parse_text_entity_response(self, response: str) -> List[Entity]:
        """Parse text format entity response.

        Args:
            response: Response text.

        Returns:
            List of Entity objects.
        """
        entities = []
        lines = response.split('\n')

        for line in lines:
            # Look for patterns like "- EntityName (type)"
            if line.strip().startswith('-') or line.strip().startswith('*'):
                # Simple parsing
                parts = line.strip().lstrip('-*').strip().split('(')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    entity_type = parts[1].split(')')[0].strip()
                    entities.append(Entity(name=name, entity_type=entity_type, confidence=0.7))

        return entities

    def _extract_entities_with_patterns(self, text: str) -> List[Entity]:
        """Extract entities using pattern matching (fallback method).

        Args:
            text: Document text.

        Returns:
            List of Entity objects.
        """
        entities = []

        # Comprehensive pattern-based entity extraction for all 8 entity types
        # Use strict patterns that match specific entity formats
        # Separate case-sensitive patterns (company names) from case-insensitive (verbs)
        case_sensitive_patterns = {
            'supplier': [
                # Company name patterns - capture full name INCLUDING suffix
                r'\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Z][A-Za-z]{2,15}){0,2}\s+Supplier)\b',  # "ABC Supplier"
                r'\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Z][A-Za-z]{2,15}){0,2}\s+(?:Components|Materials))\b',  # "ABC Components", "DEF Materials"
                r'\b([A-Z][A-Za-z]+公司)\b',  # "ABC公司"
            ],
            'manufacturer': [
                r'\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Z][A-Za-z]{2,15}){0,2}\s+(?:Manufacturing|Factory))\b',  # "XYZ Manufacturing"
                r'\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Z][A-Za-z]{2,15}){0,2}\s+Manufacturer)\b',
            ],
            'distributor': [
                r'\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Z][A-Za-z]{2,15}){0,2}\s+(?:Distributor|Distribution))\b',
            ],
            'warehouse': [
                r'\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Z][A-Za-z]{2,15}){0,2}\s+(?:Warehouse|Storage))\b',
                r'\b([A-Z][A-Za-z\u4e00-\u9fa5]{2,15}\s*仓库)\b',
            ],
            'retailer': [
                r'\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Z][A-Za-z]{2,15}){0,2}\s+(?:Store|Retail|Shop|Market))\b',
            ],
            'logistics_provider': [
                r'\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Z][A-Za-z]{2,15}){0,2}\s+(?:Logistics|Shipping|Transport|Freight))\b',
            ],
            'customer': [
                r'\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Z][A-Za-z]{2,15}){0,2}\s+(?:Inc\.|Ltd\.|Corp\.|Co\.))\b',
            ],
        }

        case_insensitive_patterns = {
            'supplier': [
                r'supplier[s]?:\s*\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,3})\b',
                r'supplied\s+by\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
            ],
            'manufacturer': [
                r'manufactured\s+(?:by|at)\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
                r'produced\s+by\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
            ],
            'distributor': [
                r'distributed\s+by\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
                r'regional\s+(distributors?)\b',
            ],
            'warehouse': [
                r'\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,3})\s+distribution\s+center\b',
            ],
            'retailer': [
                r'retailer[s]?:\s*\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,3})\b',
                r'零售商:\s*\b([A-Z一-龥][A-Za-z一-龥]{2,15}(?:\s+[A-Za-z一-龥]{2,15}){0,2})\b',
                r'sold\s+(?:by|at|through)\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
                r'retail\s+(?:through|at)\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
            ],
            'logistics_provider': [
                r'logistics\s+provider[s]?:\s*\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,3})\b',
                r'物流商:\s*\b([A-Z一-龥][A-Za-z一-龥]{2,15}(?:\s+[A-Za-z一-龥]{2,15}){0,2})\b',
                r'shipped\s+by\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
                r'delivery\s+by\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
                r'transported\s+by\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
            ],
            'product': [
                r'product[s]?:\s*\b([A-Z][A-Za-z0-9]{2,15}(?:\s+[A-Za-z0-9\-]{2,15}){0,3})\b',
                r'产品:\s*\b([A-Z一-龥][A-Za-z一-龥0-9]{2,15}(?:\s+[A-Za-z一-龥0-9\-]{2,15}){0,2})\b',
                r'(?:produces?|manufactures?)\s+\b([A-Z][A-Za-z0-9]{2,15}(?:\s+[A-Za-z0-9\-]{2,15}){0,3})\b',
                r'item[s]?:\s*\b([A-Z][A-Za-z0-9]{2,15}(?:\s+[A-Za-z0-9\-]{2,15}){0,3})\b',
            ],
            'customer': [
                r'customer[s]?:\s*\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,3})\b',
                r'客户:\s*\b([A-Z一-龥][A-Za-z一-龥]{2,15}(?:\s+[A-Za-z一-龥]{2,15}){0,2})\b',
                r'sold\s+to\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
                r'delivered\s+to\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
                r'ordered\s+by\s+\b([A-Z][A-Za-z]{2,15}(?:\s+[A-Za-z]{2,15}){0,2})\b',
            ],
        }

        import re

        # Process case-sensitive patterns (no re.IGNORECASE)
        for entity_type, pattern_list in case_sensitive_patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text)
                for match in matches:
                    name = match.group(1).strip()
                    if len(name) >= 3 and not name.lower() in ['the', 'and', 'for', 'from', 'with', 'are', 'was', 'not']:
                        name = name.rstrip('.,;:')


                        entities.append(Entity(
                            name=name,
                            entity_type=entity_type,
                            confidence=0.75  # Pattern-based extraction has moderate confidence
                        ))

        # Process case-insensitive patterns (with re.IGNORECASE)
        for entity_type, pattern_list in case_insensitive_patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    name = match.group(1).strip()
                    if len(name) >= 3 and not name.lower() in ['the', 'and', 'for', 'from', 'with', 'are', 'was', 'not', 'provides', 'supplies']:
                        name = name.rstrip('.,;:')

                        entities.append(Entity(
                            name=name,
                            entity_type=entity_type,
                            confidence=0.75
                        ))

        # Deduplicate by name (keep first occurrence with highest confidence)
        seen = {}
        for entity in entities:
            if entity.name not in seen or entity.confidence > seen[entity.name].confidence:
                seen[entity.name] = entity

        unique_entities = list(seen.values())

        # Extract attributes for entities if enabled
        if self.extract_attributes:
            for entity in unique_entities:
                entity.attributes = self._extract_entity_attributes(entity.name, text)

        return unique_entities

    def _extract_entity_attributes(self, entity_name: str, text: str) -> Dict[str, Any]:
        """Extract attributes for an entity from the text.

        Args:
            entity_name: Name of the entity to extract attributes for.
            text: Full document text.

        Returns:
            Dictionary of extracted attributes.
        """
        attributes = {}
        import re

        # Escape entity name for regex
        safe_name = re.escape(entity_name)

        # Location extraction patterns
        location_patterns = [
            rf'{safe_name}.*?(?:located in|based in|in)\s+([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*)',
            rf'(?:located in|based in|in)\s+([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*?).*?{safe_name}',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                attributes['location'] = match.group(1).strip()
                break

        # Founded year extraction
        founded_pattern = rf'{safe_name}.*?founded\s+(\d{{4}})'
        match = re.search(founded_pattern, text, re.IGNORECASE)
        if match:
            attributes['founded'] = match.group(1)

        # Revenue extraction
        revenue_patterns = [
            rf'{safe_name}.*?revenue[:\s]+\$(\d+(?:\.\d+)?[MBK]?)',
            rf'revenue[:\s]+\$(\d+(?:\.\d+)?[MBK]?).*?{safe_name}',
        ]
        for pattern in revenue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                attributes['revenue'] = f"${match.group(1)}"
                break

        return attributes

    def _extract_relationships_with_llm(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """Extract relationships using LLM.

        Args:
            text: Document text.
            entities: Extracted entities.

        Returns:
            List of Relationship objects.
        """
        try:
            llm_manager = LLMManager()
            llm = llm_manager.get_instance_obj(self.llm_name)

            # Construct prompt
            prompt = self._build_relationship_extraction_prompt(text, entities)

            # Call LLM
            messages = [{"role": "user", "content": prompt}]
            response = llm.call(messages=messages)

            # Parse response
            relationships = self._parse_llm_relationship_response(response)

            # Filter by confidence
            relationships = [r for r in relationships if r.confidence >= self.confidence_threshold]

            return relationships

        except Exception as e:
            logger.error(f"LLM relationship extraction failed: {e}")
            return self._extract_relationships_with_patterns(text, entities)

    def _build_relationship_extraction_prompt(self, text: str, entities: List[Entity]) -> str:
        """Build prompt for LLM relationship extraction.

        Args:
            text: Document text.
            entities: Extracted entities.

        Returns:
            Prompt string.
        """
        entity_names = [e.name for e in entities]
        entity_names_str = ', '.join(entity_names)
        relationship_types_str = ', '.join(self.relationship_types)

        prompt = f"""Extract supply chain relationships between entities in the following text.

Entities: {entity_names_str}

Relationship types: {relationship_types_str}

For each relationship, provide:
1. Source entity
2. Target entity
3. Relationship type
4. Confidence score (0.0-1.0)

Text:
{text[:2000]}

Return results in JSON format:
{{
  "relationships": [
    {{"source": "Entity1", "target": "Entity2", "type": "supplies", "confidence": 0.9}}
  ]
}}
"""
        return prompt

    def _parse_llm_relationship_response(self, response: str) -> List[Relationship]:
        """Parse LLM response for relationships.

        Args:
            response: LLM response text.

        Returns:
            List of Relationship objects.
        """
        relationships = []

        try:
            data = json.loads(response)
            relationship_list = data.get('relationships', [])

            for item in relationship_list:
                relationship = Relationship(
                    source=item.get('source', ''),
                    target=item.get('target', ''),
                    relationship_type=item.get('type', 'related_to'),
                    confidence=float(item.get('confidence', 0.5))
                )
                relationships.append(relationship)

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response for relationships")

        return relationships

    def _extract_relationships_with_patterns(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """Extract relationships using pattern matching (fallback method).

        Args:
            text: Document text.
            entities: Extracted entities.

        Returns:
            List of Relationship objects.
        """
        relationships = []
        entity_names = {e.name for e in entities}
        entity_map = {e.name: e for e in entities}

        import re

        # Define relationship patterns with specific verbs
        relationship_patterns = {
            'supplies': [
                r'{entity1}\s+supplies?\s+.{{0,50}}\s+(?:to\s+)?{entity2}',  # Allow 0-50 chars between
                r'{entity1}\s+supplied\s+.{{0,50}}\s+(?:to\s+)?{entity2}',
                r'{entity2}\s+receives?\s+.{{0,30}}\s+(?:from\s+)?{entity1}',
                r'{entity2}\s+(?:sources?|sourced)\s+.{{0,30}}\s+from\s+{entity1}',
                r'{entity1}\s+provides?\s+.{{0,50}}\s+(?:to\s+)?{entity2}',
            ],
            'manufactures': [
                r'{entity1}\s+(?:manufactures?|produces?|makes?)\s+.{{0,30}}\s+{entity2}',
                r'{entity2}\s+(?:manufactured|produced|made)\s+.{{0,20}}\s+(?:by\s+)?{entity1}',
                r'{entity1}\s+production\s+of\s+{entity2}',
            ],
            'distributes': [
                r'{entity1}\s+distributes?\s+.{{0,30}}\s+(?:to\s+)?{entity2}',
                r'{entity2}\s+receives?\s+distribution\s+from\s+{entity1}',
                r'{entity1}\s+ships?\s+.{{0,30}}\s+(?:to\s+)?{entity2}',
            ],
            'stores': [
                r'{entity1}\s+stores?\s+{entity2}',
                r'{entity2}\s+stored\s+(?:at|in)\s+{entity1}',
                r'{entity1}\s+inventory\s+(?:of|includes)\s+{entity2}',
            ],
            'ships_to': [
                r'{entity1}\s+ships?\s+.{{0,30}}\s+(?:to\s+)?{entity2}',
                r'{entity1}\s+delivers?\s+.{{0,30}}\s+(?:to\s+)?{entity2}',
                r'{entity2}\s+receives?\s+(?:delivery|shipment)\s+from\s+{entity1}',
                r'{entity1}\s+transports?\s+.{{0,30}}\s+(?:to\s+)?{entity2}',
                r'shipped\s+to\s+(?:the\s+)?{entity2}',  # "shipped to the Los Angeles distribution center"
            ],
            'sells_to': [
                r'{entity1}\s+sells?\s+.{{0,30}}\s+(?:to\s+)?{entity2}',
                r'{entity2}\s+buys?\s+from\s+{entity1}',
                r'{entity2}\s+purchases?\s+from\s+{entity1}',
            ],
            'depends_on': [
                r'{entity1}\s+depends?\s+on\s+{entity2}(?:\s+for\s+.{{0,30}})?',  # "depends on ABC for components"
                r'{entity1}\s+(?:is\s+)?dependent\s+on\s+{entity2}',
                r'{entity1}\s+reliant\s+on\s+{entity2}',
                r'{entity1}\s+relies\s+on\s+{entity2}',
            ],
        }

        # Try explicit relationship patterns first
        for e1 in entities:
            for e2 in entities:
                if e1.name == e2.name:
                    continue

                # Try each relationship pattern
                for rel_type, patterns in relationship_patterns.items():
                    for pattern_template in patterns:
                        pattern = pattern_template.format(
                            entity1=re.escape(e1.name),
                            entity2=re.escape(e2.name)
                        )
                        if re.search(pattern, text, re.IGNORECASE):
                            relationships.append(Relationship(
                                source=e1.name,
                                target=e2.name,
                                relationship_type=rel_type,
                                confidence=0.85  # High confidence for explicit patterns
                            ))
                            break  # Found explicit relationship, no need to check other patterns

        # Fallback: entities mentioned close together with inferred relationship
        found_pairs = {(r.source, r.target) for r in relationships}
        for e1 in entities:
            for e2 in entities:
                if e1.name == e2.name or (e1.name, e2.name) in found_pairs:
                    continue

                # Check if both entities appear in same sentence (proximity heuristic)
                pattern = f"{re.escape(e1.name)}.{{0,150}}{re.escape(e2.name)}"
                if re.search(pattern, text, re.IGNORECASE):
                    # Infer relationship type based on entity types
                    rel_type = self._infer_relationship_type(e1.entity_type, e2.entity_type)

                    relationships.append(Relationship(
                        source=e1.name,
                        target=e2.name,
                        relationship_type=rel_type,
                        confidence=0.60  # Lower confidence for inferred relationships
                    ))

        # Deduplicate relationships
        seen = set()
        unique_relationships = []
        for rel in relationships:
            key = (rel.source, rel.target, rel.relationship_type)
            if key not in seen:
                seen.add(key)
                unique_relationships.append(rel)

        return unique_relationships

    def _infer_relationship_type(self, source_type: str, target_type: str) -> str:
        """Infer relationship type based on entity types.

        Args:
            source_type: Source entity type.
            target_type: Target entity type.

        Returns:
            Relationship type.
        """
        # Simple heuristics
        if source_type == 'supplier' and target_type == 'manufacturer':
            return 'supplies'
        elif source_type == 'manufacturer' and target_type == 'product':
            return 'manufactures'
        elif source_type == 'distributor' and target_type in ['retailer', 'customer']:
            return 'ships_to'
        else:
            return 'related_to'

    def _build_knowledge_graph(self, entities: List[Entity],
                               relationships: List[Relationship]) -> Dict[str, Any]:
        """Build knowledge graph from entities and relationships.

        Args:
            entities: List of entities.
            relationships: List of relationships.

        Returns:
            Knowledge graph as dictionary.
        """
        graph = {
            'nodes': [],
            'edges': [],
            'stats': {
                'node_count': len(entities),
                'edge_count': len(relationships),
            }
        }

        # Add nodes
        for entity in entities:
            graph['nodes'].append({
                'id': entity.name,
                'type': entity.entity_type,
                'confidence': entity.confidence,
                'attributes': entity.attributes,
            })

        # Add edges
        for rel in relationships:
            graph['edges'].append({
                'source': rel.source,
                'target': rel.target,
                'type': rel.relationship_type,
                'confidence': rel.confidence,
                'attributes': rel.attributes,
            })

        return graph

    def _create_enhanced_document(self, original_doc: Document,
                                  entities: List[Entity],
                                  relationships: List[Relationship],
                                  graph: Dict[str, Any]) -> Document:
        """Create enhanced document with entity and relationship metadata.

        Args:
            original_doc: Original document.
            entities: Extracted entities.
            relationships: Extracted relationships.
            graph: Knowledge graph.

        Returns:
            Enhanced document.
        """
        metadata = original_doc.metadata.copy() if original_doc.metadata else {}

        # Save original metadata
        original_metadata_backup = original_doc.metadata.copy() if original_doc.metadata else {}

        metadata.update({
            'processor_name': self.name,
            'processor_version': '1.0',
            'processing_timestamp': datetime.now().isoformat(),
            'source_document_id': original_doc.id,
            'original_metadata': original_metadata_backup,
        })

        # Add entities
        entity_list = []
        for entity in entities:
            entity_list.append({
                'name': entity.name,
                'type': entity.entity_type,
                'confidence': entity.confidence,
                'attributes': entity.attributes,
            })
        metadata['entities'] = entity_list
        metadata['entity_count'] = len(entities)

        # Add relationships
        relationship_list = []
        for rel in relationships:
            relationship_list.append({
                'source': rel.source,
                'target': rel.target,
                'type': rel.relationship_type,
                'confidence': rel.confidence,
            })
        metadata['relationships'] = relationship_list
        metadata['relationship_count'] = len(relationships)

        # Add knowledge graph
        metadata['knowledge_graph'] = graph

        # Add keywords
        keywords = original_doc.keywords.copy() if original_doc.keywords else set()
        for entity in entities:
            keywords.add(entity.name)
            keywords.add(entity.entity_type)
        keywords.add('supply_chain')

        # Create enhanced document
        enhanced_doc = Document(
            id=original_doc.id,
            text=original_doc.text,
            metadata=metadata,
            embedding=original_doc.embedding,
            keywords=keywords
        )

        return enhanced_doc

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'SupplyChainEntityExtractor':
        """Initialize extractor parameters from configuration.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            Initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "entity_types"):
            self.entity_types = doc_processor_configer.entity_types
        if hasattr(doc_processor_configer, "relationship_types"):
            self.relationship_types = doc_processor_configer.relationship_types
        if hasattr(doc_processor_configer, "use_llm"):
            self.use_llm = doc_processor_configer.use_llm
        if hasattr(doc_processor_configer, "llm_name"):
            self.llm_name = doc_processor_configer.llm_name
        if hasattr(doc_processor_configer, "confidence_threshold"):
            self.confidence_threshold = doc_processor_configer.confidence_threshold
        if hasattr(doc_processor_configer, "extract_attributes"):
            self.extract_attributes = doc_processor_configer.extract_attributes
        if hasattr(doc_processor_configer, "skip_on_error"):
            self.skip_on_error = doc_processor_configer.skip_on_error

        return self
