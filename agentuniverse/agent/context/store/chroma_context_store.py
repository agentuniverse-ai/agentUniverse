# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 20:00
# @Author  : kaichuan
# @FileName: chroma_context_store.py
"""Chroma-based context store for cold tier storage with vector search.

ChromaContextStore provides long-term archival storage with semantic search
capabilities using vector embeddings and Chroma vector database.

Use cases:
- Long-term context archival (>72 hours)
- Semantic search across historical context
- Cross-session knowledge retrieval
- Cold storage tier for rarely accessed context
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from agentuniverse.agent.context.context_store import ContextStore
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextType,
    ContextPriority,
)


class ChromaContextStore(ContextStore):
    """Chroma-based cold tier context storage with vector search.

    Stores context segments in Chroma vector database with embeddings for
    semantic search. Designed for long-term archival and historical retrieval.

    Attributes:
        collection_name: Chroma collection name
        embedding_model_name: Name of embedding model to use
        persist_directory: Directory for Chroma persistence
        similarity_threshold: Minimum similarity score for search results
    """

    storage_tier: str = "cold"

    # Chroma configuration
    collection_name: str = "agentuniverse_context"
    embedding_model_name: Optional[str] = None  # Use LLM's embedding if available
    persist_directory: str = "./chroma_db"
    similarity_threshold: float = 0.7

    def __init__(self, **kwargs):
        """Initialize Chroma context store."""
        super().__init__(**kwargs)
        self._chroma_client = None
        self._collection = None
        self._embedding_function = None

    def initialize_by_component_configer(self, component_configer) -> 'ChromaContextStore':
        """Initialize from YAML configuration."""
        super().initialize_by_component_configer(component_configer)

        # Initialize Chroma client
        try:
            import chromadb
            from chromadb.config import Settings

            # Create persistent client
            self._chroma_client = chromadb.Client(Settings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=False
            ))

            # Get or create collection with embedding function
            self._setup_embedding_function()
            self._collection = self._chroma_client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self._embedding_function,
                metadata={"description": "agentUniverse context storage"}
            )

        except ImportError:
            raise RuntimeError(
                "Chroma library not installed. Install with: pip install chromadb"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Chroma: {e}")

        return self

    def _setup_embedding_function(self):
        """Setup embedding function for Chroma.

        Uses LLM's embedding model if available, otherwise falls back to
        Chroma's default embedding function.
        """
        if self.embedding_model_name:
            # Try to use specified embedding model
            try:
                from agentuniverse.llm.llm_manager import LLMManager
                llm = LLMManager().get_instance_obj(self.embedding_model_name)

                if hasattr(llm, 'get_embeddings'):
                    # Custom wrapper for LLM embeddings
                    class LLMEmbeddingFunction:
                        def __init__(self, llm_instance):
                            self.llm = llm_instance

                        def __call__(self, texts: List[str]) -> List[List[float]]:
                            return [self.llm.get_embeddings(text) for text in texts]

                    self._embedding_function = LLMEmbeddingFunction(llm)
                    return
            except Exception:
                pass  # Fall back to default

        # Use Chroma's default embedding function
        from chromadb.utils import embedding_functions
        self._embedding_function = embedding_functions.DefaultEmbeddingFunction()

    def add(
        self,
        segments: List[ContextSegment],
        session_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Store segments in Chroma with vector embeddings.

        Args:
            segments: List of segments to store
            session_id: Session identifier
            **kwargs: Additional parameters

        Raises:
            ValueError: If session_id is not provided
        """
        if not session_id:
            raise ValueError("session_id is required for Chroma storage")

        if not self._collection:
            raise RuntimeError("Chroma collection not initialized")

        if not segments:
            return

        # Prepare data for Chroma
        ids = []
        documents = []
        metadatas = []

        for segment in segments:
            # Generate unique ID: session:segment_id
            doc_id = f"{session_id}:{segment.id}"
            ids.append(doc_id)

            # Document is the content (will be embedded)
            documents.append(segment.content)

            # Metadata for filtering
            metadata = {
                "session_id": session_id,
                "segment_id": segment.id,
                "type": segment.type.value,
                "priority": segment.priority.value,
                "tokens": segment.tokens,
                "created_at": segment.metadata.created_at.isoformat(),
                "last_accessed": segment.metadata.last_accessed.isoformat(),
                "access_count": segment.metadata.access_count,
                "relevance_score": segment.metadata.relevance_score,
                "decay_rate": segment.metadata.decay_rate,
            }

            # Add optional fields
            if segment.parent_id:
                metadata["parent_id"] = segment.parent_id
            if segment.task_id:
                metadata["task_id"] = segment.task_id
            if segment.agent_id:
                metadata["agent_id"] = segment.agent_id

            metadatas.append(metadata)

        # Add to Chroma collection
        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def get(
        self,
        session_id: str,
        context_type: Optional[ContextType] = None,
        priority: Optional[ContextPriority] = None,
        limit: int = 100,
        **kwargs
    ) -> List[ContextSegment]:
        """Retrieve segments from Chroma.

        Args:
            session_id: Session identifier
            context_type: Optional type filter
            priority: Optional priority filter
            limit: Maximum number of segments to return
            **kwargs: Additional parameters (e.g., min_created_at)

        Returns:
            List of matching segments
        """
        if not self._collection:
            return []

        # Build where clause for filtering
        where = {"session_id": session_id}

        if context_type:
            where["type"] = context_type.value
        if priority:
            where["priority"] = priority.value

        # Add time filter if provided
        min_created_at = kwargs.get("min_created_at")
        if min_created_at:
            where["created_at"] = {"$gte": min_created_at.isoformat()}

        # Query Chroma
        try:
            results = self._collection.get(
                where=where,
                limit=limit,
            )

            if not results or not results["ids"]:
                return []

            # Convert to ContextSegment objects
            segments = []
            for i in range(len(results["ids"])):
                try:
                    segment = self._metadata_to_segment(
                        results["documents"][i],
                        results["metadatas"][i]
                    )
                    segments.append(segment)
                except Exception:
                    continue  # Skip corrupted entries

            # Sort by created_at (newest first)
            segments.sort(key=lambda s: s.metadata.created_at, reverse=True)
            return segments[:limit]

        except Exception:
            return []

    def search(
        self,
        query: str,
        session_id: str,
        top_k: int = 10,
        **kwargs
    ) -> List[ContextSegment]:
        """Semantic search using vector similarity.

        Args:
            query: Search query (will be embedded)
            session_id: Session identifier
            top_k: Number of results to return
            **kwargs: Additional parameters (context_type, priority, min_similarity)

        Returns:
            List of matching segments ranked by semantic similarity
        """
        if not self._collection:
            return []

        # Build where clause
        where = {"session_id": session_id}

        context_type = kwargs.get("context_type")
        if context_type:
            where["type"] = context_type.value

        priority = kwargs.get("priority")
        if priority:
            where["priority"] = priority.value

        # Perform semantic search
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where,
            )

            if not results or not results["ids"] or not results["ids"][0]:
                return []

            # Convert to ContextSegment objects with similarity scores
            segments = []
            min_similarity = kwargs.get("min_similarity", self.similarity_threshold)

            for i in range(len(results["ids"][0])):
                distance = results["distances"][0][i]
                # Convert distance to similarity (1 - normalized_distance)
                similarity = 1.0 - distance

                if similarity < min_similarity:
                    continue  # Skip low similarity results

                try:
                    segment = self._metadata_to_segment(
                        results["documents"][0][i],
                        results["metadatas"][0][i]
                    )
                    # Store similarity score in metadata for ranking
                    segment.metadata.relevance_score = similarity
                    segments.append(segment)
                except Exception:
                    continue

            return segments

        except Exception:
            return []

    def delete(
        self,
        session_id: str,
        segment_ids: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """Delete segments from Chroma.

        Args:
            session_id: Session identifier
            segment_ids: Optional list of segment IDs (None = delete all for session)
            **kwargs: Additional parameters
        """
        if not self._collection:
            return

        if segment_ids:
            # Delete specific segments
            ids_to_delete = [f"{session_id}:{seg_id}" for seg_id in segment_ids]
            self._collection.delete(ids=ids_to_delete)
        else:
            # Delete entire session
            self._collection.delete(where={"session_id": session_id})

    def prune(
        self,
        session_id: str,
        min_priority: Optional[ContextPriority] = None,
        **kwargs
    ) -> int:
        """Prune low-priority or old segments.

        Args:
            session_id: Session identifier
            min_priority: Minimum priority to keep
            **kwargs: Additional parameters (max_age_hours)

        Returns:
            Number of segments pruned
        """
        if not self._collection:
            return 0

        # Get all segments for session
        segments = self.get(session_id, limit=10000)

        to_remove = []
        now = datetime.now()
        max_age_hours = kwargs.get("max_age_hours", self.ttl_hours)

        priority_order = {
            ContextPriority.EPHEMERAL: 0,
            ContextPriority.LOW: 1,
            ContextPriority.MEDIUM: 2,
            ContextPriority.HIGH: 3,
            ContextPriority.CRITICAL: 4,
        }

        min_level = priority_order.get(min_priority, 0) if min_priority else 0

        for segment in segments:
            seg_level = priority_order.get(segment.priority, 2)

            # Remove if below priority threshold
            if seg_level < min_level:
                to_remove.append(segment.id)
                continue

            # Remove if too old
            age_hours = (now - segment.metadata.created_at).total_seconds() / 3600
            if age_hours > max_age_hours:
                to_remove.append(segment.id)

        if to_remove:
            self.delete(session_id, segment_ids=to_remove)

        return len(to_remove)

    def get_by_ids(
        self,
        session_id: str,
        segment_ids: List[str],
        **kwargs
    ) -> List[ContextSegment]:
        """Retrieve specific segments by IDs.

        Args:
            session_id: Session identifier
            segment_ids: List of segment IDs
            **kwargs: Additional parameters

        Returns:
            List of segments
        """
        if not self._collection or not segment_ids:
            return []

        # Build full IDs
        full_ids = [f"{session_id}:{seg_id}" for seg_id in segment_ids]

        try:
            results = self._collection.get(ids=full_ids)

            if not results or not results["ids"]:
                return []

            segments = []
            for i in range(len(results["ids"])):
                try:
                    segment = self._metadata_to_segment(
                        results["documents"][i],
                        results["metadatas"][i]
                    )
                    segments.append(segment)
                except Exception:
                    continue

            return segments

        except Exception:
            return []

    def count(self, session_id: str, **kwargs) -> int:
        """Count segments for a session.

        Args:
            session_id: Session identifier
            **kwargs: Additional parameters

        Returns:
            Number of segments
        """
        if not self._collection:
            return 0

        try:
            results = self._collection.get(
                where={"session_id": session_id},
                limit=1  # We only need count, not data
            )
            return self._collection.count()
        except Exception:
            return 0

    def get_all_sessions(self) -> List[str]:
        """Get all session IDs stored in Chroma.

        Returns:
            List of unique session IDs
        """
        if not self._collection:
            return []

        try:
            # Get all documents (this could be expensive for large collections)
            results = self._collection.get()

            if not results or not results["metadatas"]:
                return []

            # Extract unique session IDs
            session_ids = set()
            for metadata in results["metadatas"]:
                session_ids.add(metadata["session_id"])

            return list(session_ids)

        except Exception:
            return []

    def clear_all(self) -> None:
        """Clear all stored context (use with caution).

        This removes all context data from Chroma collection.
        """
        if not self._collection:
            return

        try:
            # Delete the entire collection and recreate
            self._chroma_client.delete_collection(name=self.collection_name)
            self._collection = self._chroma_client.create_collection(
                name=self.collection_name,
                embedding_function=self._embedding_function,
                metadata={"description": "agentUniverse context storage"}
            )
        except Exception:
            pass  # Silently fail if collection doesn't exist

    def _metadata_to_segment(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> ContextSegment:
        """Convert Chroma metadata to ContextSegment.

        Args:
            content: Document content
            metadata: Chroma metadata dictionary

        Returns:
            ContextSegment instance
        """
        from agentuniverse.agent.context.context_model import ContextMetadata

        # Parse metadata
        segment_id = metadata["segment_id"]
        context_type = ContextType(metadata["type"])
        priority = ContextPriority(metadata["priority"])
        tokens = metadata["tokens"]

        # Reconstruct ContextMetadata
        ctx_metadata = ContextMetadata(
            created_at=datetime.fromisoformat(metadata["created_at"]),
            last_accessed=datetime.fromisoformat(metadata["last_accessed"]),
            access_count=metadata["access_count"],
            relevance_score=metadata["relevance_score"],
            decay_rate=metadata["decay_rate"],
        )

        # Create segment
        segment = ContextSegment(
            id=segment_id,
            type=context_type,
            priority=priority,
            content=content,
            tokens=tokens,
            metadata=ctx_metadata,
            session_id=metadata["session_id"],
            parent_id=metadata.get("parent_id"),
            task_id=metadata.get("task_id"),
            agent_id=metadata.get("agent_id"),
        )

        return segment
