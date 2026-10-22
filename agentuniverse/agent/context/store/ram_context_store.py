# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: ram_context_store.py
"""In-memory context store with LRU eviction."""

from collections import OrderedDict
from functools import wraps
from threading import RLock
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import re

from pydantic import PrivateAttr

from agentuniverse.agent.context.context_store import ContextStore
from agentuniverse.agent.context.context_model import ContextSegment, ContextType, ContextPriority


def _synchronized(method):
    """Keep each storage operation, including access tracking, under one lock."""
    @wraps(method)
    def locked(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)

    return locked


class RamContextStore(ContextStore):
    """In-memory context storage with LRU eviction.

    Features:
    - Fast access (O(1) for get by ID)
    - LRU eviction when max_segments exceeded
    - Keyword-based search
    - TTL-based automatic pruning
    - Thread-safe storage operations, access tracking, and metric snapshots

    Storage Structure:
    - _storage: Dict[session_id, OrderedDict[segment_id, ContextSegment]]
    - OrderedDict maintains insertion order for LRU

    Concurrency:
    - Operations on one store are serialized by a reentrant lock, including
      multi-session batch_add. Sequences of separate calls are not transactions.
    - Returned segments are live references, as before. Callers must synchronize
      external mutations and must not change configuration during operations.
    - Deep copies have independent storage, metrics, and locks. Explicit shallow
      copies share storage and its lock. This is not a process-shared store.
    """

    storage_tier: str = "hot"
    _lock = PrivateAttr(default_factory=RLock)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Storage: session_id -> OrderedDict[segment_id -> ContextSegment]
        self._storage: Dict[str, OrderedDict] = {}

        if self.enable_metrics:
            self.initialize_metrics()

    def __deepcopy__(self, memo=None):
        """Copy a consistent snapshot without trying to deepcopy the RLock."""
        with self._lock:
            if memo is None:
                memo = {}
            # Preserve deep-copy isolation instead of the base's shallow fallback.
            memo.setdefault(id(self._lock), RLock())
            return super().__deepcopy__(memo)

    @_synchronized
    def add(self, segments: List[ContextSegment], **kwargs) -> None:
        """Store context segments with LRU eviction.

        Args:
            segments: List of context segments to store
            **kwargs: Must include 'session_id'
        """
        start_time = time.time() if self.enable_metrics else None

        session_id = kwargs.get('session_id')
        if not session_id:
            raise ValueError("session_id is required for add()")

        # Initialize session storage if not exists
        if session_id not in self._storage:
            self._storage[session_id] = OrderedDict()

        session_storage = self._storage[session_id]

        for segment in segments:
            # Update session_id if not set
            if not segment.session_id:
                segment.session_id = session_id

            # Add or update segment (move to end for LRU)
            if segment.id in session_storage:
                session_storage.move_to_end(segment.id)

            session_storage[segment.id] = segment

            # LRU eviction if exceeded max_segments
            if len(session_storage) > self.max_segments:
                self._evict_lru(session_storage)

        if self.enable_metrics:
            elapsed_ms = (time.time() - start_time) * 1000
            self._metrics["add_count"] += 1
            self._metrics["total_add_time_ms"] += elapsed_ms

    @_synchronized
    def get(
        self,
        session_id: str,
        context_type: Optional[ContextType] = None,
        limit: int = 100,
        **kwargs
    ) -> List[ContextSegment]:
        """Retrieve segments with filtering.

        Args:
            session_id: Session identifier
            context_type: Optional filter by context type
            limit: Maximum number of segments to return
            **kwargs: Additional filters (priority, min_decay_score, etc.)

        Returns:
            List[ContextSegment]: Retrieved segments (sorted by last_accessed desc)
        """
        start_time = time.time() if self.enable_metrics else None

        if session_id not in self._storage:
            return []

        session_storage = self._storage[session_id]
        segments = list(session_storage.values())

        # Apply filters
        if context_type:
            segments = [s for s in segments if s.type == context_type]

        priority_filter = kwargs.get('priority')
        if priority_filter:
            segments = [s for s in segments if s.priority == priority_filter]

        min_decay_score = kwargs.get('min_decay_score', 0.0)
        if min_decay_score > 0:
            segments = [s for s in segments if s.calculate_decay() >= min_decay_score]

        # Remove expired segments
        segments = [s for s in segments if not self._is_expired(s)]

        # Sort by last_accessed (most recent first)
        segments.sort(key=lambda s: s.metadata.last_accessed, reverse=True)

        # Update access tracking
        for segment in segments[:limit]:
            segment.mark_accessed()
            # Move to end in OrderedDict (LRU)
            session_storage.move_to_end(segment.id)

        if self.enable_metrics:
            elapsed_ms = (time.time() - start_time) * 1000
            self._metrics["get_count"] += 1
            self._metrics["total_get_time_ms"] += elapsed_ms

        return segments[:limit]

    @_synchronized
    def search(
        self,
        query: str,
        session_id: str,
        top_k: int = 10,
        **kwargs
    ) -> List[ContextSegment]:
        """Keyword-based search for relevant context.

        Simple implementation using keyword matching.
        Priority and decay only rank segments that match the query; priority
        alone does not qualify an unrelated segment for retrieval.
        Future enhancement: BM25, TF-IDF, or embedding-based search.

        Args:
            query: Search query string
            session_id: Session identifier
            top_k: Number of top results to return
            **kwargs: Additional parameters (context_type filter, etc.)

        Returns:
            List[ContextSegment]: Top-k relevant segments
        """
        start_time = time.time() if self.enable_metrics else None

        if session_id not in self._storage:
            return []

        session_storage = self._storage[session_id]
        segments = list(session_storage.values())

        # Apply context_type filter if provided
        context_type_filter = kwargs.get('context_type')
        if context_type_filter:
            segments = [s for s in segments if s.type == context_type_filter]

        # Remove expired segments
        segments = [s for s in segments if not self._is_expired(s)]

        # Score each segment
        scored_segments = []
        query_lower = query.lower()
        query_terms = set(re.findall(r'\w+', query_lower))

        for segment in segments:
            score = self._calculate_keyword_score(segment, query_lower, query_terms)
            if score > 0:
                scored_segments.append((segment, score))

        # Sort by score (descending) then by last_accessed (descending)
        scored_segments.sort(key=lambda x: (x[1], x[0].metadata.last_accessed), reverse=True)

        # Update access tracking for top results
        top_segments = []
        for segment, score in scored_segments[:top_k]:
            segment.mark_accessed()
            session_storage.move_to_end(segment.id)
            top_segments.append(segment)

        if self.enable_metrics:
            elapsed_ms = (time.time() - start_time) * 1000
            self._metrics["search_count"] += 1
            self._metrics["total_search_time_ms"] += elapsed_ms

        return top_segments

    @_synchronized
    def delete(
        self,
        session_id: str,
        segment_ids: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """Delete segments.

        Args:
            session_id: Session identifier
            segment_ids: Optional list of specific segment IDs to delete
                         If None, deletes all segments for session
        """
        if session_id not in self._storage:
            return

        if segment_ids is None:
            # Delete entire session
            del self._storage[session_id]
        else:
            # Delete specific segments
            session_storage = self._storage[session_id]
            for segment_id in segment_ids:
                if segment_id in session_storage:
                    del session_storage[segment_id]

            # Clean up empty session
            if len(session_storage) == 0:
                del self._storage[session_id]

        if self.enable_metrics:
            self._metrics["delete_count"] += 1

    @_synchronized
    def prune(self, session_id: str, **kwargs) -> int:
        """Prune expired/low-priority segments.

        Args:
            session_id: Session identifier
            **kwargs: Pruning parameters
                - min_priority: ContextPriority
                - max_age_hours: float
                - min_decay_score: float (default 0.1)

        Returns:
            int: Number of segments pruned
        """
        if session_id not in self._storage:
            return 0

        session_storage = self._storage[session_id]

        min_priority = kwargs.get('min_priority')
        max_age_hours = kwargs.get('max_age_hours')
        min_decay_score = kwargs.get('min_decay_score', 0.1)

        # Identify segments to prune
        to_prune = []
        for segment_id, segment in session_storage.items():
            if self._should_prune(segment, min_priority, max_age_hours, min_decay_score):
                to_prune.append(segment_id)

        # Remove pruned segments
        for segment_id in to_prune:
            del session_storage[segment_id]

        # Clean up empty session
        if len(session_storage) == 0:
            del self._storage[session_id]

        if self.enable_metrics:
            self._metrics["prune_count"] += 1

        return len(to_prune)

    @_synchronized
    def get_by_ids(
        self,
        session_id: str,
        segment_ids: List[str],
        **kwargs
    ) -> List[ContextSegment]:
        """Retrieve specific segments by IDs (optimized O(1) lookup).

        Args:
            session_id: Session identifier
            segment_ids: List of segment IDs to retrieve

        Returns:
            List[ContextSegment]: Retrieved segments
        """
        if session_id not in self._storage:
            return []

        session_storage = self._storage[session_id]
        segments = []

        for segment_id in segment_ids:
            if segment_id in session_storage:
                segment = session_storage[segment_id]
                segment.mark_accessed()
                session_storage.move_to_end(segment_id)  # LRU update
                segments.append(segment)

        return segments

    @_synchronized
    def count(self, session_id: str, **kwargs) -> int:
        """Count total segments for session (O(1) operation).

        Args:
            session_id: Session identifier
            **kwargs: Additional filters (ignored for efficiency)

        Returns:
            int: Number of segments
        """
        if session_id not in self._storage:
            return 0

        return len(self._storage[session_id])

    @_synchronized
    def get_all_sessions(self) -> List[str]:
        """Get list of all session IDs in storage.

        Returns:
            List[str]: Session IDs
        """
        return list(self._storage.keys())

    @_synchronized
    def clear_all(self) -> None:
        """Clear all storage (use with caution)."""
        self._storage.clear()

    @_synchronized
    def batch_add(self, segments_by_session: dict[str, list[ContextSegment]], **kwargs) -> None:
        """Add a multi-session batch without interleaving other store operations."""
        super().batch_add(segments_by_session, **kwargs)

    @_synchronized
    def initialize_metrics(self) -> None:
        """Reset metrics without interleaving storage operations."""
        super().initialize_metrics()

    @_synchronized
    def get_metrics(self) -> dict[str, Any]:
        """Return a consistent metrics snapshot independent of future updates."""
        return super().get_metrics()

    # Private helper methods

    def _evict_lru(self, session_storage: OrderedDict) -> None:
        """Evict least recently used segment.

        Priority order (evict first):
        1. EPHEMERAL
        2. LOW priority with low decay score
        3. MEDIUM priority with low decay score
        4. Oldest by last_accessed (from beginning of OrderedDict)

        Args:
            session_storage: Session's OrderedDict storage
        """
        # Try to evict EPHEMERAL first
        for segment_id, segment in session_storage.items():
            if segment.priority == ContextPriority.EPHEMERAL:
                del session_storage[segment_id]
                return

        # Try to evict LOW priority with low decay score
        for segment_id, segment in session_storage.items():
            if segment.priority == ContextPriority.LOW and segment.calculate_decay() < 0.3:
                del session_storage[segment_id]
                return

        # Try to evict MEDIUM priority with low decay score
        for segment_id, segment in session_storage.items():
            if segment.priority == ContextPriority.MEDIUM and segment.calculate_decay() < 0.5:
                del session_storage[segment_id]
                return

        # Fallback: evict oldest (first in OrderedDict)
        if len(session_storage) > 0:
            session_storage.popitem(last=False)

    def _calculate_keyword_score(
        self,
        segment: ContextSegment,
        query_lower: str,
        query_terms: set
    ) -> float:
        """Calculate keyword matching score for search.

        Scoring:
        - Exact phrase match: 10.0
        - Content term match: 2.0 per term
        - Keyword match: 5.0 per keyword
        - Priority bonus for matches only: CRITICAL=2.0, HIGH=1.5, MEDIUM=1.0, LOW=0.5
        - Decay factor: multiply by decay score

        Args:
            segment: Context segment to score
            query_lower: Lowercase query string
            query_terms: Set of query terms

        Returns:
            float: Relevance score
        """
        score = 0.0

        content_lower = segment.content.lower()

        # Exact phrase match
        if query_lower in content_lower:
            score += 10.0

        # Term matching in content
        content_terms = set(re.findall(r'\w+', content_lower))
        matching_terms = query_terms & content_terms
        score += len(matching_terms) * 2.0

        # Keyword matching
        segment_keywords = set(k.lower() for k in segment.metadata.keywords)
        matching_keywords = query_terms & segment_keywords
        score += len(matching_keywords) * 5.0

        if score == 0.0:
            return 0.0

        # Priority bonus
        priority_bonus = {
            ContextPriority.CRITICAL: 2.0,
            ContextPriority.HIGH: 1.5,
            ContextPriority.MEDIUM: 1.0,
            ContextPriority.LOW: 0.5,
            ContextPriority.EPHEMERAL: 0.2,
        }
        score += priority_bonus.get(segment.priority, 1.0)

        # Apply decay factor
        score *= max(0.1, segment.calculate_decay())

        return score
