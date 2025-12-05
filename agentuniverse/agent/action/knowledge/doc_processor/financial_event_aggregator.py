# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @Email   : ai@example.com
# @FileName: financial_event_aggregator.py

import hashlib
import logging
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)


@dataclass
class EventCluster:
    """Represents a cluster of related news articles about the same event.

    Attributes:
        event_id: Unique identifier for the event.
        event_type: Type of event (merger, acquisition, earnings, etc.).
        documents: List of document IDs in this cluster.
        representative_doc: Most representative document in cluster.
        entities_involved: Key entities mentioned across documents.
        publication_dates: List of publication dates.
    """
    event_id: str
    event_type: str
    documents: List[str] = field(default_factory=list)
    representative_doc: Optional[Document] = None
    entities_involved: Set[str] = field(default_factory=set)
    publication_dates: List[str] = field(default_factory=list)


class FinancialEventAggregator(DocProcessor):
    """Aggregate related financial news articles into unified event reports.

    This processor:
    1. Clusters semantically similar articles using embeddings
    2. Identifies event types (merger, acquisition, earnings, etc.)
    3. Generates multi-document summaries
    4. Tracks source attribution and credibility

    Attributes:
        similarity_threshold: Similarity threshold for clustering (0.0-1.0).
        use_embeddings: Whether to use embeddings for similarity.
        embedding_name: Name of embedding model to use.
        clustering_method: Clustering algorithm ('dbscan', 'hierarchical').
        summarization_mode: Summarization mode ('extractive', 'map_reduce').
        use_llm: Whether to use LLM for summarization.
        llm_name: Name of LLM to use.
        max_sources_per_event: Maximum number of sources to include per event.
        preserve_sources: Whether to preserve source document references.
        skip_on_error: Whether to skip documents that fail processing.
    """

    similarity_threshold: float = 0.85
    use_embeddings: bool = True
    embedding_name: Optional[str] = None
    clustering_method: str = 'dbscan'  # 'dbscan' or 'hierarchical'
    summarization_mode: str = 'map_reduce'  # 'extractive' or 'map_reduce'
    use_llm: bool = True
    llm_name: Optional[str] = None
    max_sources_per_event: int = 20
    preserve_sources: bool = True
    skip_on_error: bool = True

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Aggregate related financial news into event documents.

        Args:
            origin_docs: List of news article documents.
            query: Optional query object (not used in this processor).

        Returns:
            List of aggregated event documents.
        """
        if not origin_docs:
            return []

        logger.info(f"Starting financial event aggregation for {len(origin_docs)} documents")

        # Step 1: Compute similarity matrix
        similarity_matrix = self._compute_similarity_matrix(origin_docs)

        # Step 2: Cluster related documents
        clusters = self._cluster_related_documents(origin_docs, similarity_matrix)
        logger.info(f"Identified {len(clusters)} event clusters")

        # Step 3: Process each cluster
        aggregated_docs = []
        for cluster in clusters:
            try:
                event_doc = self._aggregate_cluster(cluster, origin_docs)
                aggregated_docs.append(event_doc)
            except Exception as e:
                logger.error(f"Failed to aggregate cluster {cluster.event_id}: {e}")
                if not self.skip_on_error:
                    raise

        logger.info(f"Created {len(aggregated_docs)} aggregated event documents")
        return aggregated_docs

    def _compute_similarity_matrix(self, docs: List[Document]) -> np.ndarray:
        """Compute pairwise similarity matrix for documents.

        Args:
            docs: List of documents.

        Returns:
            Similarity matrix (n x n numpy array).
        """
        n = len(docs)
        similarity_matrix = np.zeros((n, n))

        if not self.use_embeddings or not self.embedding_name:
            logger.warning("Embeddings not enabled, using text overlap similarity")
            return self._compute_text_similarity_matrix(docs)

        try:
            # Get embedding model
            embedding_manager = EmbeddingManager()
            embedding_model = embedding_manager.get_instance_obj(self.embedding_name)

            # Compute embeddings
            texts = [doc.text for doc in docs]
            embeddings = embedding_model.get_embeddings(texts)

            # Update document embeddings
            for doc, embedding in zip(docs, embeddings):
                doc.embedding = embedding

            # Compute similarity matrix
            for i in range(n):
                for j in range(i, n):
                    if i == j:
                        similarity_matrix[i][j] = 1.0
                    else:
                        sim = self._cosine_similarity(embeddings[i], embeddings[j])
                        similarity_matrix[i][j] = sim
                        similarity_matrix[j][i] = sim

        except Exception as e:
            logger.error(f"Failed to compute embeddings: {e}")
            # Fallback to text similarity
            return self._compute_text_similarity_matrix(docs)

        return similarity_matrix

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            vec1: First vector.
            vec2: Second vector.

        Returns:
            Cosine similarity score.
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _compute_text_similarity_matrix(self, docs: List[Document]) -> np.ndarray:
        """Compute similarity matrix using text overlap (fallback method).

        Args:
            docs: List of documents.

        Returns:
            Similarity matrix.
        """
        n = len(docs)
        similarity_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i, n):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    # Simple word overlap similarity
                    words_i = set(docs[i].text.lower().split())
                    words_j = set(docs[j].text.lower().split())
                    overlap = len(words_i & words_j)
                    union = len(words_i | words_j)
                    sim = overlap / union if union > 0 else 0.0
                    similarity_matrix[i][j] = sim
                    similarity_matrix[j][i] = sim

        return similarity_matrix

    def _cluster_related_documents(self, docs: List[Document],
                                   similarity_matrix: np.ndarray) -> List[EventCluster]:
        """Cluster related documents based on similarity.

        Args:
            docs: List of documents.
            similarity_matrix: Pairwise similarity matrix.

        Returns:
            List of EventCluster objects.
        """
        if self.clustering_method == 'dbscan':
            return self._cluster_with_dbscan(docs, similarity_matrix)
        elif self.clustering_method == 'hierarchical':
            return self._cluster_with_hierarchical(docs, similarity_matrix)
        else:
            logger.warning(f"Unknown clustering method: {self.clustering_method}, using dbscan")
            return self._cluster_with_dbscan(docs, similarity_matrix)

    def _cluster_with_dbscan(self, docs: List[Document],
                             similarity_matrix: np.ndarray) -> List[EventCluster]:
        """Cluster documents using DBSCAN.

        Args:
            docs: List of documents.
            similarity_matrix: Similarity matrix.

        Returns:
            List of EventCluster objects.
        """
        # Convert similarity to distance
        distance_matrix = 1 - similarity_matrix

        # Simple DBSCAN-like clustering
        n = len(docs)
        clusters = []
        visited = set()
        eps = 1 - self.similarity_threshold

        for i in range(n):
            if i in visited:
                continue

            # Find neighbors
            neighbors = [j for j in range(n) if distance_matrix[i][j] < eps and j != i]

            if len(neighbors) < 1:
                # Singleton cluster
                cluster = self._create_cluster([docs[i]])
                clusters.append(cluster)
                visited.add(i)
            else:
                # Expand cluster
                cluster_docs = [docs[i]]
                visited.add(i)
                queue = neighbors.copy()

                while queue:
                    j = queue.pop(0)
                    if j in visited:
                        continue

                    visited.add(j)
                    cluster_docs.append(docs[j])

                    # Find neighbors of j
                    j_neighbors = [k for k in range(n) if distance_matrix[j][k] < eps and k != j]
                    queue.extend([k for k in j_neighbors if k not in visited])

                cluster = self._create_cluster(cluster_docs)
                clusters.append(cluster)

        return clusters

    def _cluster_with_hierarchical(self, docs: List[Document],
                                   similarity_matrix: np.ndarray) -> List[EventCluster]:
        """Cluster documents using hierarchical clustering.

        Args:
            docs: List of documents.
            similarity_matrix: Similarity matrix.

        Returns:
            List of EventCluster objects.
        """
        # Simple agglomerative clustering
        n = len(docs)
        clusters_list = [[i] for i in range(n)]  # Start with each doc in its own cluster

        while len(clusters_list) > 1:
            # Find most similar pair of clusters
            max_sim = -1
            merge_i, merge_j = -1, -1

            for i in range(len(clusters_list)):
                for j in range(i + 1, len(clusters_list)):
                    # Average linkage
                    sim = np.mean([similarity_matrix[doc_i][doc_j]
                                  for doc_i in clusters_list[i]
                                  for doc_j in clusters_list[j]])

                    if sim > max_sim:
                        max_sim = sim
                        merge_i, merge_j = i, j

            # Stop if similarity below threshold
            if max_sim < self.similarity_threshold:
                break

            # Merge clusters
            clusters_list[merge_i].extend(clusters_list[merge_j])
            del clusters_list[merge_j]

        # Create EventCluster objects
        clusters = []
        for cluster_indices in clusters_list:
            cluster_docs = [docs[i] for i in cluster_indices]
            cluster = self._create_cluster(cluster_docs)
            clusters.append(cluster)

        return clusters

    def _create_cluster(self, cluster_docs: List[Document]) -> EventCluster:
        """Create EventCluster from list of documents.

        Args:
            cluster_docs: Documents in the cluster.

        Returns:
            EventCluster object.
        """
        # Generate event ID
        event_id = self._generate_event_id(cluster_docs)

        # Identify event type
        event_type = self._identify_event_type(cluster_docs)

        # Extract entities
        entities = self._extract_entities(cluster_docs)

        # Find representative document (longest or most central)
        representative_doc = max(cluster_docs, key=lambda d: len(d.text))

        # Extract publication dates
        pub_dates = []
        for doc in cluster_docs:
            if doc.metadata and 'publication_date' in doc.metadata:
                pub_dates.append(doc.metadata['publication_date'])

        cluster = EventCluster(
            event_id=event_id,
            event_type=event_type,
            documents=[doc.id for doc in cluster_docs],
            representative_doc=representative_doc,
            entities_involved=entities,
            publication_dates=pub_dates
        )

        return cluster

    def _generate_event_id(self, docs: List[Document]) -> str:
        """Generate unique event ID for a cluster.

        Args:
            docs: Documents in cluster.

        Returns:
            Event ID string.
        """
        # Create hash from sorted document IDs
        doc_ids = sorted([doc.id for doc in docs])
        hash_input = '|'.join(doc_ids)
        event_hash = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        return f"event_{event_hash}"

    def _identify_event_type(self, docs: List[Document]) -> str:
        """Identify the type of financial event.

        Args:
            docs: Documents in cluster.

        Returns:
            Event type string.
        """
        # Combine text from all documents
        combined_text = ' '.join([doc.text[:500] for doc in docs])  # Use first 500 chars
        text_lower = combined_text.lower()

        # Event type patterns
        event_patterns = {
            'merger': ['merger', 'merge', 'acquisition', 'acquire', '并购', '收购'],
            'earnings': ['earnings', 'quarterly results', 'financial results', '财报', '业绩'],
            'ipo': ['ipo', 'initial public offering', 'going public', '上市'],
            'lawsuit': ['lawsuit', 'litigation', 'sued', '诉讼'],
            'bankruptcy': ['bankruptcy', 'chapter 11', 'insolvency', '破产'],
            'partnership': ['partnership', 'collaboration', 'joint venture', '合作'],
            'product_launch': ['product launch', 'new product', 'release', '发布'],
            'leadership_change': ['ceo', 'cfo', 'resignation', 'appointed', '任命'],
        }

        # Count matches for each event type
        type_scores = {}
        for event_type, keywords in event_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                type_scores[event_type] = score

        # Return type with highest score
        if type_scores:
            return max(type_scores, key=type_scores.get)
        else:
            return 'general_news'

    def _extract_entities(self, docs: List[Document]) -> Set[str]:
        """Extract key entities mentioned across documents.

        Args:
            docs: Documents in cluster.

        Returns:
            Set of entity names.
        """
        entities = set()

        # Simple extraction: look for capitalized words
        import re
        for doc in docs:
            # Extract capitalized phrases (potential company/person names)
            matches = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', doc.text)
            entities.update(matches[:10])  # Limit to avoid too many

        return entities

    def _aggregate_cluster(self, cluster: EventCluster, all_docs: List[Document]) -> Document:
        """Aggregate a cluster into a single event document.

        Args:
            cluster: EventCluster to aggregate.
            all_docs: All original documents.

        Returns:
            Aggregated event document.
        """
        # Get cluster documents
        cluster_docs = [doc for doc in all_docs if doc.id in cluster.documents]

        # Limit sources if needed
        if len(cluster_docs) > self.max_sources_per_event:
            cluster_docs = cluster_docs[:self.max_sources_per_event]

        # Generate summary
        if self.use_llm and self.llm_name:
            summary = self._generate_llm_summary(cluster_docs, cluster)
        else:
            summary = self._generate_extractive_summary(cluster_docs)

        # Detect conflicts
        conflicts = self._detect_conflicts(cluster_docs)

        # Score credibility
        credibility_scores = self._score_credibility(cluster_docs)

        # Create aggregated document
        aggregated_doc = self._create_aggregated_document(
            cluster, cluster_docs, summary, conflicts, credibility_scores
        )

        return aggregated_doc

    def _generate_llm_summary(self, docs: List[Document], cluster: EventCluster) -> str:
        """Generate summary using LLM.

        Args:
            docs: Documents to summarize.
            cluster: Event cluster information.

        Returns:
            Summary text.
        """
        try:
            llm_manager = LLMManager()
            llm = llm_manager.get_instance_obj(self.llm_name)

            # Combine document texts
            combined_text = '\n\n---\n\n'.join([doc.text[:1000] for doc in docs])

            # Build prompt
            prompt = f"""Summarize the following news articles about a {cluster.event_type} event.

Create a comprehensive summary that:
1. Describes the main event
2. Includes key facts and figures
3. Mentions main entities involved
4. Notes any conflicting information

Articles:
{combined_text[:5000]}

Summary:"""

            messages = [{"role": "user", "content": prompt}]
            summary = llm.call(messages=messages)

            return summary

        except Exception as e:
            logger.error(f"LLM summarization failed: {e}")
            return self._generate_extractive_summary(docs)

    def _generate_extractive_summary(self, docs: List[Document]) -> str:
        """Generate extractive summary (fallback method).

        Args:
            docs: Documents to summarize.

        Returns:
            Summary text.
        """
        # Simple extractive: concatenate first sentences from each document
        summary_parts = []
        for doc in docs[:5]:  # Limit to first 5 docs
            # Extract first sentence
            first_sentence = doc.text.split('.')[0] + '.'
            if len(first_sentence) > 20:
                summary_parts.append(first_sentence)

        summary = ' '.join(summary_parts)
        return summary[:1000]  # Limit length

    def _detect_conflicts(self, docs: List[Document]) -> List[Dict[str, Any]]:
        """Detect conflicting information across documents.

        Args:
            docs: Documents to analyze.

        Returns:
            List of detected conflicts.
        """
        # Simplified conflict detection
        conflicts = []

        # Check for contradictory statements (future enhancement)
        # For now, just note if there are multiple sources
        if len(docs) > 3:
            conflicts.append({
                'type': 'multiple_sources',
                'description': f'{len(docs)} different sources report on this event',
                'severity': 'info'
            })

        return conflicts

    def _score_credibility(self, docs: List[Document]) -> Dict[str, float]:
        """Score credibility of source documents.

        Args:
            docs: Documents to score.

        Returns:
            Dictionary mapping document IDs to credibility scores.
        """
        scores = {}

        for doc in docs:
            # Simple heuristic: longer documents are more credible
            score = min(1.0, len(doc.text) / 1000)

            # Boost score if metadata indicates verified source
            if doc.metadata and doc.metadata.get('verified_source'):
                score = min(1.0, score * 1.2)

            scores[doc.id] = score

        return scores

    def _create_aggregated_document(self, cluster: EventCluster,
                                   source_docs: List[Document],
                                   summary: str,
                                   conflicts: List[Dict[str, Any]],
                                   credibility_scores: Dict[str, float]) -> Document:
        """Create aggregated event document.

        Args:
            cluster: Event cluster.
            source_docs: Source documents.
            summary: Generated summary.
            conflicts: Detected conflicts.
            credibility_scores: Credibility scores.

        Returns:
            Aggregated document.
        """
        # Build metadata
        metadata = {
            'processor_name': self.name,
            'processor_version': '1.0',
            'processing_timestamp': datetime.now().isoformat(),
            'event_id': cluster.event_id,
            'event_type': cluster.event_type,
            'entities_involved': list(cluster.entities_involved),
            'source_count': len(source_docs),
            'aggregated_summary': summary,
        }

        # Add source references if enabled
        if self.preserve_sources:
            source_refs = []
            for doc in source_docs:
                source_refs.append({
                    'id': doc.id,
                    'credibility_score': credibility_scores.get(doc.id, 0.5),
                    'publication_date': doc.metadata.get('publication_date') if doc.metadata else None
                })
            metadata['source_documents'] = source_refs

        # Add conflicts
        if conflicts:
            metadata['conflicting_info'] = conflicts

        # Add publication dates
        if cluster.publication_dates:
            metadata['publication_dates'] = cluster.publication_dates

        # Create keywords
        keywords = set(['financial_event', cluster.event_type])
        keywords.update(cluster.entities_involved)

        # Create aggregated document
        aggregated_doc = Document(
            text=summary,
            metadata=metadata,
            keywords=keywords
        )

        return aggregated_doc

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'FinancialEventAggregator':
        """Initialize aggregator parameters from configuration.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            Initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "similarity_threshold"):
            self.similarity_threshold = doc_processor_configer.similarity_threshold
        if hasattr(doc_processor_configer, "use_embeddings"):
            self.use_embeddings = doc_processor_configer.use_embeddings
        if hasattr(doc_processor_configer, "embedding_name"):
            self.embedding_name = doc_processor_configer.embedding_name
        if hasattr(doc_processor_configer, "clustering_method"):
            self.clustering_method = doc_processor_configer.clustering_method
        if hasattr(doc_processor_configer, "summarization_mode"):
            self.summarization_mode = doc_processor_configer.summarization_mode
        if hasattr(doc_processor_configer, "use_llm"):
            self.use_llm = doc_processor_configer.use_llm
        if hasattr(doc_processor_configer, "llm_name"):
            self.llm_name = doc_processor_configer.llm_name
        if hasattr(doc_processor_configer, "max_sources_per_event"):
            self.max_sources_per_event = doc_processor_configer.max_sources_per_event
        if hasattr(doc_processor_configer, "preserve_sources"):
            self.preserve_sources = doc_processor_configer.preserve_sources
        if hasattr(doc_processor_configer, "skip_on_error"):
            self.skip_on_error = doc_processor_configer.skip_on_error

        return self
