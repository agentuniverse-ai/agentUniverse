# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @Email   : ai@example.com
# @FileName: semantic_deduplicator.py

import hashlib
import logging
from typing import List, Optional, Set, Dict, Tuple
from datetime import datetime

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)


class SemanticDeduplicator(DocProcessor):
    """Remove duplicate or near-duplicate documents using semantic similarity.

    This processor identifies and removes duplicate documents using multiple strategies:
    1. Exact match: Content hashing for identical documents
    2. Semantic match: Embedding-based similarity for near-duplicates
    3. Configurable merge strategies for handling duplicates

    Attributes:
        similarity_threshold: Similarity score threshold (0.0-1.0) for considering documents as duplicates.
        exact_match_threshold: Threshold for exact matching (default 1.0).
        merge_strategy: Strategy for handling duplicates ('keep_first', 'keep_best', 'merge').
        use_embeddings: Whether to use embeddings for semantic similarity.
        embedding_name: Name of the embedding model to use.
        preserve_metadata: Whether to preserve metadata from deduplicated sources.
        skip_on_error: Whether to skip documents that fail processing.
    """

    similarity_threshold: float = 0.95
    exact_match_threshold: float = 1.0
    merge_strategy: str = 'keep_first'  # 'keep_first', 'keep_best', 'merge'
    use_embeddings: bool = True
    embedding_name: Optional[str] = None
    preserve_metadata: bool = True
    skip_on_error: bool = True

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Remove duplicate documents from the input list.

        Args:
            origin_docs: List of documents to deduplicate.
            query: Optional query object (not used in this processor).

        Returns:
            List of deduplicated documents.
        """
        if not origin_docs:
            return []

        logger.info(f"Starting deduplication of {len(origin_docs)} documents")

        # Step 1: Exact duplicate removal using content hash
        unique_docs, hash_map = self._remove_exact_duplicates(origin_docs)
        logger.info(f"After exact match: {len(unique_docs)} unique documents")

        # Step 2: Semantic duplicate removal using embeddings
        if self.use_embeddings and len(unique_docs) > 1:
            try:
                unique_docs = self._remove_semantic_duplicates(unique_docs)
                logger.info(f"After semantic match: {len(unique_docs)} unique documents")
            except Exception as e:
                logger.error(f"Semantic deduplication failed: {e}")
                if not self.skip_on_error:
                    raise

        # Step 3: Update metadata
        for doc in unique_docs:
            self._update_metadata(doc)

        logger.info(f"Deduplication complete: {len(origin_docs)} -> {len(unique_docs)} documents")
        return unique_docs

    def _remove_exact_duplicates(self, docs: List[Document]) -> Tuple[List[Document], Dict[str, List[Document]]]:
        """Remove exact duplicates using content hashing.

        Args:
            docs: List of documents to process.

        Returns:
            Tuple of (unique documents, hash map of duplicates).
        """
        hash_map: Dict[str, List[Document]] = {}
        seen_hashes: Set[str] = set()
        unique_docs: List[Document] = []

        for doc in docs:
            try:
                content_hash = self._compute_hash(doc.text)

                if content_hash not in hash_map:
                    hash_map[content_hash] = []
                hash_map[content_hash].append(doc)

                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    unique_docs.append(doc)
                else:
                    # Handle duplicate based on merge strategy
                    if self.merge_strategy == 'keep_best':
                        # Replace if current doc is "better" (e.g., has more metadata)
                        existing_idx = next(i for i, d in enumerate(unique_docs)
                                          if self._compute_hash(d.text) == content_hash)
                        if self._is_better_doc(doc, unique_docs[existing_idx]):
                            unique_docs[existing_idx] = doc
                    elif self.merge_strategy == 'merge':
                        # Merge metadata from duplicate
                        existing_idx = next(i for i, d in enumerate(unique_docs)
                                          if self._compute_hash(d.text) == content_hash)
                        unique_docs[existing_idx] = self._merge_docs(unique_docs[existing_idx], doc)
            except Exception as e:
                logger.error(f"Failed to process document {doc.id}: {e}")
                if not self.skip_on_error:
                    raise
                # Keep the document if skip_on_error is True
                unique_docs.append(doc)

        return unique_docs, hash_map

    def _remove_semantic_duplicates(self, docs: List[Document]) -> List[Document]:
        """Remove semantic duplicates using embeddings.

        Args:
            docs: List of documents to process.

        Returns:
            List of documents with semantic duplicates removed.
        """
        if not self.embedding_name:
            logger.warning("No embedding model specified, skipping semantic deduplication")
            return docs

        try:
            # Get embedding model
            embedding_manager = EmbeddingManager()
            embedding_model = embedding_manager.get_instance_obj(self.embedding_name)

            # Compute embeddings for all documents
            texts = [doc.text for doc in docs]
            embeddings = embedding_model.get_embeddings(texts)

            # Update document embeddings
            for doc, embedding in zip(docs, embeddings):
                doc.embedding = embedding

            # Find and remove semantic duplicates
            unique_docs = []
            seen_indices = set()

            for i, doc in enumerate(docs):
                if i in seen_indices:
                    continue

                # Add document to unique set
                unique_docs.append(doc)
                seen_indices.add(i)

                # Check for semantic duplicates
                for j in range(i + 1, len(docs)):
                    if j in seen_indices:
                        continue

                    similarity = self._compute_similarity(embeddings[i], embeddings[j])
                    if similarity >= self.similarity_threshold:
                        seen_indices.add(j)

                        # Handle duplicate based on merge strategy
                        if self.merge_strategy == 'keep_best':
                            if self._is_better_doc(docs[j], doc):
                                # Replace with better document
                                unique_docs[-1] = docs[j]
                        elif self.merge_strategy == 'merge':
                            # Merge metadata
                            unique_docs[-1] = self._merge_docs(unique_docs[-1], docs[j])

            return unique_docs

        except Exception as e:
            logger.error(f"Semantic deduplication error: {e}")
            raise

    def _compute_hash(self, text: str) -> str:
        """Compute SHA-256 hash of text content.

        Args:
            text: Text content to hash.

        Returns:
            Hex string of hash.
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def _compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector.
            embedding2: Second embedding vector.

        Returns:
            Cosine similarity score (0.0-1.0).
        """
        # Compute dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))

        # Compute magnitudes
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5

        # Handle zero magnitude
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        # Compute cosine similarity
        return dot_product / (magnitude1 * magnitude2)

    def _is_better_doc(self, doc1: Document, doc2: Document) -> bool:
        """Determine if doc1 is "better" than doc2.

        Currently uses metadata richness as the criterion.

        Args:
            doc1: First document.
            doc2: Second document.

        Returns:
            True if doc1 is better than doc2.
        """
        metadata1 = doc1.metadata or {}
        metadata2 = doc2.metadata or {}

        # Compare metadata richness
        score1 = len(metadata1) + len(doc1.keywords)
        score2 = len(metadata2) + len(doc2.keywords)

        return score1 > score2

    def _merge_docs(self, doc1: Document, doc2: Document) -> Document:
        """Merge two documents, combining their metadata.

        Args:
            doc1: First document (base).
            doc2: Second document to merge.

        Returns:
            Merged document.
        """
        if not self.preserve_metadata:
            return doc1

        # Merge metadata
        merged_metadata = doc1.metadata.copy() if doc1.metadata else {}
        if doc2.metadata:
            for key, value in doc2.metadata.items():
                if key not in merged_metadata:
                    merged_metadata[key] = value
                elif isinstance(value, list) and isinstance(merged_metadata[key], list):
                    # Merge lists
                    merged_metadata[key] = list(set(merged_metadata[key] + value))

        # Merge keywords
        merged_keywords = doc1.keywords.union(doc2.keywords)

        # Track merged sources
        if 'merged_sources' not in merged_metadata:
            merged_metadata['merged_sources'] = []
        merged_metadata['merged_sources'].append({
            'id': doc2.id,
            'merge_time': datetime.now().isoformat()
        })

        # Create merged document
        merged_doc = Document(
            id=doc1.id,
            text=doc1.text,
            metadata=merged_metadata,
            embedding=doc1.embedding,
            keywords=merged_keywords
        )

        return merged_doc

    def _update_metadata(self, doc: Document) -> None:
        """Update document metadata with processing information.

        Args:
            doc: Document to update.
        """
        if doc.metadata is None:
            doc.metadata = {}

        doc.metadata['processor_name'] = self.name
        doc.metadata['processor_version'] = '1.0'
        doc.metadata['processing_timestamp'] = datetime.now().isoformat()
        doc.metadata['deduplication_strategy'] = self.merge_strategy

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'SemanticDeduplicator':
        """Initialize deduplicator parameters from configuration.

        Args:
            doc_processor_configer: Configuration object containing deduplicator parameters.

        Returns:
            Initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "similarity_threshold"):
            self.similarity_threshold = doc_processor_configer.similarity_threshold
        if hasattr(doc_processor_configer, "exact_match_threshold"):
            self.exact_match_threshold = doc_processor_configer.exact_match_threshold
        if hasattr(doc_processor_configer, "merge_strategy"):
            self.merge_strategy = doc_processor_configer.merge_strategy
        if hasattr(doc_processor_configer, "use_embeddings"):
            self.use_embeddings = doc_processor_configer.use_embeddings
        if hasattr(doc_processor_configer, "embedding_name"):
            self.embedding_name = doc_processor_configer.embedding_name
        if hasattr(doc_processor_configer, "preserve_metadata"):
            self.preserve_metadata = doc_processor_configer.preserve_metadata
        if hasattr(doc_processor_configer, "skip_on_error"):
            self.skip_on_error = doc_processor_configer.skip_on_error

        return self
