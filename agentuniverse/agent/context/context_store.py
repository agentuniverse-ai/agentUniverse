# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: context_store.py
"""Base class for context storage backends."""

from abc import abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.agent.context.context_model import ContextSegment, ContextType, ContextPriority


class ContextStore(ComponentBase):
    """Base class for context storage backends.

    Provides unified interface for hot/warm/cold storage tiers.
    Implementations: RamContextStore, RedisContextStore, ChromaContextStore.
    """

    component_type: ComponentEnum = ComponentEnum.CONTEXT_STORE

    # Storage configuration
    storage_tier: str = "warm"  # hot, warm, cold
    max_segments: int = 1000    # Maximum segments per session
    ttl_hours: int = 24         # Time to live in hours

    # Performance tracking
    enable_metrics: bool = False
    _metrics: Dict[str, Any] = {}

    def initialize_metrics(self) -> None:
        """Initialize performance metrics tracking."""
        self._metrics = {
            "add_count": 0,
            "get_count": 0,
            "search_count": 0,
            "delete_count": 0,
            "prune_count": 0,
            "total_add_time_ms": 0.0,
            "total_get_time_ms": 0.0,
            "total_search_time_ms": 0.0,
        }

    @abstractmethod
    def add(self, segments: List[ContextSegment], **kwargs) -> None:
        """Store context segments.

        Args:
            segments: List of context segments to store
            **kwargs: Additional parameters (session_id, etc.)

        Raises:
            ValueError: If segments validation fails
            StorageError: If storage operation fails
        """
        pass

    @abstractmethod
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
            **kwargs: Additional filters (priority, time range, etc.)

        Returns:
            List[ContextSegment]: Retrieved segments (sorted by relevance/time)
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        session_id: str,
        top_k: int = 10,
        **kwargs
    ) -> List[ContextSegment]:
        """Semantic/keyword search for relevant context.

        Args:
            query: Search query string
            session_id: Session identifier
            top_k: Number of top results to return
            **kwargs: Additional search parameters (filters, etc.)

        Returns:
            List[ContextSegment]: Top-k relevant segments
        """
        pass

    @abstractmethod
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
            **kwargs: Additional parameters
        """
        pass

    @abstractmethod
    def prune(self, session_id: str, **kwargs) -> int:
        """Prune expired/low-priority segments.

        Args:
            session_id: Session identifier
            **kwargs: Pruning parameters (max_age, min_priority, etc.)

        Returns:
            int: Number of segments pruned
        """
        pass

    def get_by_ids(
        self,
        session_id: str,
        segment_ids: List[str],
        **kwargs
    ) -> List[ContextSegment]:
        """Retrieve specific segments by IDs.

        Default implementation filters get() results. Override for efficiency.

        Args:
            session_id: Session identifier
            segment_ids: List of segment IDs to retrieve

        Returns:
            List[ContextSegment]: Retrieved segments
        """
        all_segments = self.get(session_id, **kwargs)
        segment_id_set = set(segment_ids)
        return [s for s in all_segments if s.id in segment_id_set]

    def batch_add(
        self,
        segments_by_session: Dict[str, List[ContextSegment]],
        **kwargs
    ) -> None:
        """Batch add segments for multiple sessions.

        Default implementation loops over sessions. Override for efficiency.

        Args:
            segments_by_session: Dict mapping session_id to segment list
            **kwargs: Additional parameters
        """
        for session_id, segments in segments_by_session.items():
            self.add(segments, session_id=session_id, **kwargs)

    def count(self, session_id: str, **kwargs) -> int:
        """Count total segments for session.

        Default implementation uses len(get()). Override for efficiency.

        Args:
            session_id: Session identifier
            **kwargs: Additional filters

        Returns:
            int: Number of segments
        """
        return len(self.get(session_id, **kwargs))

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics.

        Returns:
            Dict[str, Any]: Metrics dictionary
        """
        if not self.enable_metrics:
            return {}

        metrics = self._metrics.copy()

        # Calculate averages
        if metrics["add_count"] > 0:
            metrics["avg_add_time_ms"] = metrics["total_add_time_ms"] / metrics["add_count"]
        if metrics["get_count"] > 0:
            metrics["avg_get_time_ms"] = metrics["total_get_time_ms"] / metrics["get_count"]
        if metrics["search_count"] > 0:
            metrics["avg_search_time_ms"] = metrics["total_search_time_ms"] / metrics["search_count"]

        return metrics

    def _is_expired(self, segment: ContextSegment) -> bool:
        """Check if segment has expired based on TTL.

        Args:
            segment: Context segment to check

        Returns:
            bool: True if expired
        """
        if self.ttl_hours <= 0:
            return False

        age_hours = (datetime.now() - segment.metadata.created_at).total_seconds() / 3600
        return age_hours > self.ttl_hours

    def _should_prune(
        self,
        segment: ContextSegment,
        min_priority: Optional[ContextPriority] = None,
        max_age_hours: Optional[float] = None,
        min_decay_score: float = 0.1
    ) -> bool:
        """Determine if segment should be pruned.

        Args:
            segment: Context segment to evaluate
            min_priority: Segments below this priority are pruned
            max_age_hours: Segments older than this are pruned
            min_decay_score: Segments with decay score below this are pruned

        Returns:
            bool: True if segment should be pruned
        """
        # Never prune CRITICAL priority
        if segment.priority == ContextPriority.CRITICAL:
            return False

        # Check TTL expiration
        if self._is_expired(segment):
            return True

        # Check priority
        if min_priority:
            priority_order = [
                ContextPriority.EPHEMERAL,
                ContextPriority.LOW,
                ContextPriority.MEDIUM,
                ContextPriority.HIGH,
                ContextPriority.CRITICAL,
            ]
            if priority_order.index(segment.priority) < priority_order.index(min_priority):
                return True

        # Check age
        if max_age_hours:
            age_hours = (datetime.now() - segment.metadata.created_at).total_seconds() / 3600
            if age_hours > max_age_hours:
                return True

        # Check decay score
        if segment.calculate_decay() < min_decay_score:
            return True

        return False
