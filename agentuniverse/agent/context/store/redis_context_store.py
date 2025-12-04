# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 19:00
# @Author  : kaichuan
# @FileName: redis_context_store.py
"""Redis-based context store for warm tier storage.

RedisContextStore provides persistent, TTL-based storage for context segments
that need to survive longer than RAM but don't require long-term archival.

Use cases:
- Recent session context (last 24-72 hours)
- Cross-session persistence
- Shared context across multiple agents
- Warm storage tier between hot (RAM) and cold (vector DB)
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from agentuniverse.agent.context.context_store import ContextStore
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextType,
    ContextPriority,
)


class RedisContextStore(ContextStore):
    """Redis-based warm tier context storage.

    Stores context segments in Redis with TTL-based expiration, providing
    persistence and sharing across processes/agents.

    Attributes:
        redis_host: Redis server host
        redis_port: Redis server port
        redis_db: Redis database number
        redis_password: Optional Redis password
        key_prefix: Prefix for all Redis keys
        default_ttl_seconds: Default TTL for segments
    """

    storage_tier: str = "warm"

    # Redis connection parameters
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    key_prefix: str = "agentuniverse:context:"
    default_ttl_seconds: int = 86400  # 24 hours

    def __init__(self, **kwargs):
        """Initialize Redis context store."""
        super().__init__(**kwargs)
        self._redis = None

    def initialize_by_component_configer(self, component_configer) -> 'RedisContextStore':
        """Initialize from YAML configuration."""
        super().initialize_by_component_configer(component_configer)

        # Initialize Redis connection
        try:
            import redis
            self._redis = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=False  # We'll handle encoding
            )
            # Test connection
            self._redis.ping()
        except ImportError:
            raise RuntimeError(
                "Redis library not installed. Install with: pip install redis"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Redis: {e}")

        return self

    def add(
        self,
        segments: List[ContextSegment],
        session_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Store segments in Redis with TTL.

        Args:
            segments: List of segments to store
            session_id: Session identifier (required)
            **kwargs: Additional parameters (ttl_seconds)

        Raises:
            ValueError: If session_id is not provided
        """
        if not session_id:
            raise ValueError("session_id is required for Redis storage")

        if not self._redis:
            raise RuntimeError("Redis not initialized")

        ttl_seconds = kwargs.get("ttl_seconds", self.default_ttl_seconds)

        for segment in segments:
            # Serialize segment to JSON
            segment_data = self._serialize_segment(segment)

            # Store in Redis hash: session_id -> segment_id -> data
            key = self._make_session_key(session_id)
            self._redis.hset(key, segment.id, segment_data)

            # Set TTL on the session key
            self._redis.expire(key, ttl_seconds)

            # Also maintain a sorted set for time-based queries
            # Score is timestamp for ordering
            index_key = self._make_index_key(session_id)
            timestamp = segment.metadata.created_at.timestamp()
            self._redis.zadd(index_key, {segment.id: timestamp})
            self._redis.expire(index_key, ttl_seconds)

    def get(
        self,
        session_id: str,
        context_type: Optional[ContextType] = None,
        priority: Optional[ContextPriority] = None,
        limit: int = 100,
        **kwargs
    ) -> List[ContextSegment]:
        """Retrieve segments from Redis.

        Args:
            session_id: Session identifier
            context_type: Optional type filter
            priority: Optional priority filter
            limit: Maximum number of segments to return
            **kwargs: Additional parameters

        Returns:
            List of matching segments
        """
        if not self._redis:
            return []

        key = self._make_session_key(session_id)

        # Get all segments for the session
        segment_data_dict = self._redis.hgetall(key)

        if not segment_data_dict:
            return []

        segments = []
        for segment_id, segment_data in segment_data_dict.items():
            try:
                segment = self._deserialize_segment(segment_data)

                # Apply filters
                if context_type and segment.type != context_type:
                    continue
                if priority and segment.priority != priority:
                    continue

                segments.append(segment)

            except Exception as e:
                # Skip corrupted segments
                continue

        # Sort by created_at (newest first) and apply limit
        segments.sort(key=lambda s: s.metadata.created_at, reverse=True)
        return segments[:limit]

    def search(
        self,
        query: str,
        session_id: str,
        top_k: int = 10,
        **kwargs
    ) -> List[ContextSegment]:
        """Search segments using keyword matching.

        Args:
            query: Search query
            session_id: Session identifier
            top_k: Number of results to return
            **kwargs: Additional parameters

        Returns:
            List of matching segments ranked by relevance
        """
        # Get all segments and do in-memory search
        # For production, consider Redis full-text search module
        segments = self.get(session_id, limit=1000)

        query_lower = query.lower()
        query_terms = query_lower.split()

        # Score segments
        scored = []
        for segment in segments:
            content_lower = segment.content.lower()

            score = 0.0

            # Exact phrase match
            if query_lower in content_lower:
                score += 10.0

            # Term matches
            for term in query_terms:
                if term in content_lower:
                    score += 2.0

            # Priority bonus
            priority_bonus = {
                ContextPriority.CRITICAL: 10.0,
                ContextPriority.HIGH: 5.0,
                ContextPriority.MEDIUM: 2.0,
                ContextPriority.LOW: 1.0,
                ContextPriority.EPHEMERAL: 0.5,
            }
            score += priority_bonus.get(segment.priority, 2.0)

            # Decay factor
            score *= segment.calculate_decay()

            if score > 0:
                scored.append((segment, score))

        # Sort by score and return top_k
        scored.sort(key=lambda x: x[1], reverse=True)
        return [seg for seg, _ in scored[:top_k]]

    def delete(
        self,
        session_id: str,
        segment_ids: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """Delete segments from Redis.

        Args:
            session_id: Session identifier
            segment_ids: Optional list of segment IDs (None = delete all)
            **kwargs: Additional parameters
        """
        if not self._redis:
            return

        key = self._make_session_key(session_id)
        index_key = self._make_index_key(session_id)

        if segment_ids:
            # Delete specific segments
            self._redis.hdel(key, *segment_ids)
            self._redis.zrem(index_key, *segment_ids)
        else:
            # Delete entire session
            self._redis.delete(key)
            self._redis.delete(index_key)

    def prune(
        self,
        session_id: str,
        min_priority: Optional[ContextPriority] = None,
        **kwargs
    ) -> int:
        """Prune expired or low-priority segments.

        Args:
            session_id: Session identifier
            min_priority: Minimum priority to keep
            **kwargs: Additional parameters

        Returns:
            Number of segments pruned
        """
        if not self._redis:
            return 0

        segments = self.get(session_id, limit=10000)

        to_remove = []
        now = datetime.now()

        for segment in segments:
            # Check TTL expiration (handled by Redis)
            # Check priority filter
            if min_priority:
                priority_order = {
                    ContextPriority.EPHEMERAL: 0,
                    ContextPriority.LOW: 1,
                    ContextPriority.MEDIUM: 2,
                    ContextPriority.HIGH: 3,
                    ContextPriority.CRITICAL: 4,
                }
                min_level = priority_order.get(min_priority, 2)
                seg_level = priority_order.get(segment.priority, 2)

                if seg_level < min_level:
                    to_remove.append(segment.id)
                    continue

            # Check manual TTL (from metadata)
            age_hours = (now - segment.metadata.created_at).total_seconds() / 3600
            if age_hours > self.ttl_hours:
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
        if not self._redis or not segment_ids:
            return []

        key = self._make_session_key(session_id)
        segment_data_list = self._redis.hmget(key, segment_ids)

        segments = []
        for segment_data in segment_data_list:
            if segment_data:
                try:
                    segment = self._deserialize_segment(segment_data)
                    segments.append(segment)
                except Exception:
                    continue

        return segments

    def count(self, session_id: str, **kwargs) -> int:
        """Count segments for a session.

        Args:
            session_id: Session identifier
            **kwargs: Additional parameters

        Returns:
            Number of segments
        """
        if not self._redis:
            return 0

        key = self._make_session_key(session_id)
        return self._redis.hlen(key)

    def get_all_sessions(self) -> List[str]:
        """Get all session IDs.

        Returns:
            List of session IDs
        """
        if not self._redis:
            return []

        # Scan for all session keys
        pattern = f"{self.key_prefix}session:*"
        session_keys = []

        cursor = 0
        while True:
            cursor, keys = self._redis.scan(
                cursor, match=pattern, count=100
            )
            session_keys.extend(keys)
            if cursor == 0:
                break

        # Extract session IDs from keys
        prefix_len = len(f"{self.key_prefix}session:")
        session_ids = [
            key.decode('utf-8')[prefix_len:]
            for key in session_keys
        ]

        return session_ids

    def clear_all(self) -> None:
        """Clear all stored context (use with caution).

        This removes all context data from Redis.
        """
        if not self._redis:
            return

        # Delete all keys with our prefix
        pattern = f"{self.key_prefix}*"
        cursor = 0

        while True:
            cursor, keys = self._redis.scan(
                cursor, match=pattern, count=1000
            )
            if keys:
                self._redis.delete(*keys)
            if cursor == 0:
                break

    def _make_session_key(self, session_id: str) -> str:
        """Generate Redis key for session data."""
        return f"{self.key_prefix}session:{session_id}"

    def _make_index_key(self, session_id: str) -> str:
        """Generate Redis key for time-based index."""
        return f"{self.key_prefix}index:{session_id}"

    def _serialize_segment(self, segment: ContextSegment) -> bytes:
        """Serialize segment to JSON bytes.

        Args:
            segment: Segment to serialize

        Returns:
            JSON bytes
        """
        data = segment.model_dump(mode='json')
        return json.dumps(data).encode('utf-8')

    def _deserialize_segment(self, data: bytes) -> ContextSegment:
        """Deserialize segment from JSON bytes.

        Args:
            data: JSON bytes

        Returns:
            ContextSegment instance
        """
        json_data = json.loads(data.decode('utf-8'))
        return ContextSegment.model_validate(json_data)
