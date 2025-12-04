# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: context_manager.py
"""Context Manager - Central orchestrator for context engineering.

The ContextManager is responsible for:
- Token budget allocation across components (memory, knowledge, workspace, etc.)
- Context window management (session-scoped)
- Proactive compression triggers
- Multi-tier storage coordination
- Task-adaptive configuration
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextWindow,
    ContextType,
    ContextPriority,
)
from agentuniverse.agent.context.context_store import ContextStore


class ContextManager(ComponentBase):
    """Central orchestrator for context engineering.

    Manages context windows, token budgets, and storage coordination with
    proactive compression and task-adaptive strategies.

    Attributes:
        hot_store_name: Name of hot storage (RAM) for fast access
        warm_store_name: Optional name of warm storage (Redis) for persistence
        cold_store_name: Optional name of cold storage (Vector DB) for archival
        llm_name: Name of LLM for token counting
        default_max_tokens: Default context window size
        default_reserved_tokens: Default tokens reserved for output
        task_configs: Task-specific configuration overrides
    """

    component_type: ComponentEnum = ComponentEnum.CONTEXT_MANAGER

    hot_store_name: str = "ram_context_store"
    warm_store_name: Optional[str] = None
    cold_store_name: Optional[str] = None
    llm_name: str = "default_llm"
    compressor_name: Optional[str] = None  # NEW: Optional compressor
    router_name: Optional[str] = None      # NEW: Optional router
    default_max_tokens: int = 8000
    default_reserved_tokens: int = 1000
    enable_compression: bool = True         # NEW: Enable compression in _make_room()

    # Task-specific configurations
    task_configs: Dict[str, Dict[str, Any]] = {
        "code_generation": {
            "max_tokens": 10000,
            "reserved_tokens": 1500,
            "budget_ratios": {
                "workspace": 0.5,   # 50% for code files
                "knowledge": 0.2,   # 20% for documentation
                "memory": 0.15,     # 15% for conversation
                "system": 0.05,     # 5% for system prompts
                "task": 0.1,        # 10% for current task
            },
            "compression_strategy": "selective",
        },
        "data_analysis": {
            "max_tokens": 12000,
            "reserved_tokens": 2000,
            "budget_ratios": {
                "background": 0.4,  # 40% for data context
                "workspace": 0.3,   # 30% for notebooks/scripts
                "knowledge": 0.15,  # 15% for documentation
                "memory": 0.1,      # 10% for conversation
                "system": 0.05,     # 5% for system prompts
            },
            "compression_strategy": "summarize",
        },
        "dialogue": {
            "max_tokens": 8000,
            "reserved_tokens": 1000,
            "budget_ratios": {
                "conversation": 0.5,  # 50% for chat history
                "background": 0.25,   # 25% for context
                "system": 0.15,       # 15% for system prompts
                "memory": 0.1,        # 10% for long-term memory
            },
            "compression_strategy": "adaptive",
        },
    }

    def __init__(self, **kwargs):
        """Initialize ContextManager.

        Sets up storage references and context window tracking.
        """
        super().__init__(**kwargs)
        self._hot_store: Optional[ContextStore] = None
        self._warm_store: Optional[ContextStore] = None
        self._cold_store: Optional[ContextStore] = None
        self._llm = None
        self._compressor = None  # NEW: Compression strategy
        self._router = None      # NEW: Context router

        # Session context windows: session_id -> ContextWindow
        self._windows: Dict[str, ContextWindow] = {}

    def initialize_by_component_configer(self, component_configer) -> 'ContextManager':
        """Initialize from YAML configuration."""
        super().initialize_by_component_configer(component_configer)

        # Initialize storage backends
        if self.hot_store_name:
            from agentuniverse.agent.context.context_store_manager import ContextStoreManager
            self._hot_store = ContextStoreManager().get_instance_obj(self.hot_store_name)

        if self.warm_store_name:
            from agentuniverse.agent.context.context_store_manager import ContextStoreManager
            self._warm_store = ContextStoreManager().get_instance_obj(self.warm_store_name)

        if self.cold_store_name:
            from agentuniverse.agent.context.context_store_manager import ContextStoreManager
            self._cold_store = ContextStoreManager().get_instance_obj(self.cold_store_name)

        # Initialize LLM for token counting
        if self.llm_name:
            from agentuniverse.llm.llm_manager import LLMManager
            self._llm = LLMManager().get_instance_obj(self.llm_name)

        # NEW: Initialize compressor if specified
        if self.compressor_name:
            from agentuniverse.agent.context.compressor.adaptive_compressor import AdaptiveCompressor
            # For now, use AdaptiveCompressor as default
            # In production, would load from component manager
            self._compressor = AdaptiveCompressor(
                name=f"{self.name}_compressor",
                llm_name=self.llm_name,
                compression_ratio=0.6,  # Target 40% reduction
                enable_hybrid=True
            )
            if hasattr(self._compressor, 'initialize_by_component_configer'):
                self._compressor.initialize_by_component_configer(component_configer)

        # NEW: Initialize router if specified
        if self.router_name:
            from agentuniverse.agent.context.router.context_router import ContextRouter
            self._router = ContextRouter(
                name=f"{self.name}_router",
                enable_warm_tier=(self._warm_store is not None),
                enable_cold_tier=(self._cold_store is not None)
            )

        return self

    def create_context_window(
        self,
        session_id: str,
        agent_id: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs
    ) -> ContextWindow:
        """Create a new context window for a session.

        Args:
            session_id: Unique session identifier
            agent_id: Optional agent identifier
            task_type: Optional task type for adaptive configuration
            **kwargs: Additional window configuration

        Returns:
            Created ContextWindow instance
        """
        # Get task-specific configuration
        task_config = self.task_configs.get(task_type or "dialogue", {})

        max_tokens = kwargs.get("max_tokens") or task_config.get("max_tokens", self.default_max_tokens)
        reserved_tokens = kwargs.get("reserved_tokens") or task_config.get("reserved_tokens", self.default_reserved_tokens)

        # Calculate component budgets based on task ratios
        input_budget = max_tokens - reserved_tokens
        budget_ratios = task_config.get("budget_ratios", {})
        component_budgets = {
            component: int(input_budget * ratio)
            for component, ratio in budget_ratios.items()
        }

        # Create window
        window = ContextWindow(
            session_id=session_id,
            agent_id=agent_id,
            task_id=kwargs.get("task_id"),
            max_tokens=max_tokens,
            reserved_tokens=reserved_tokens,
            component_budgets=component_budgets,
            task_type=task_type,
            compression_strategy=task_config.get("compression_strategy", "adaptive"),
        )

        self._windows[session_id] = window
        return window

    def add_context(
        self,
        session_id: str,
        content: str,
        context_type: ContextType,
        priority: ContextPriority = ContextPriority.MEDIUM,
        **kwargs
    ) -> ContextSegment:
        """Add context with proactive budget management.

        This is the core innovation: we check budget BEFORE adding and
        make room if needed through compression/eviction.

        Args:
            session_id: Session identifier
            content: Context content to add
            context_type: Type of context
            priority: Priority level
            **kwargs: Additional segment metadata

        Returns:
            Created ContextSegment

        Raises:
            ValueError: If session has no context window
        """
        # Get or create window
        window = self._windows.get(session_id)
        if not window:
            # Auto-create with defaults if not exists
            window = self.create_context_window(session_id)

        # Count tokens for new content
        tokens = self._count_tokens(content)

        # Proactive budget check - make room BEFORE adding
        if window.total_tokens + tokens > window.calculate_input_tokens():
            self._make_room(window, tokens)

        # Create segment
        segment = ContextSegment(
            type=context_type,
            priority=priority,
            content=content,
            tokens=tokens,
            session_id=session_id,
            parent_id=kwargs.get("parent_id"),
            related_ids=kwargs.get("related_ids", []),
        )

        # Store in hot storage
        if self._hot_store:
            self._hot_store.add([segment], session_id=session_id)

        # Update window tracking
        window.add_segment_id(segment.id)
        window.update_total_tokens(tokens, operation="add")

        return segment

    def get_context(
        self,
        session_id: str,
        context_type: Optional[ContextType] = None,
        priority: Optional[ContextPriority] = None,
        limit: Optional[int] = None,
        **kwargs
    ) -> List[ContextSegment]:
        """Retrieve context segments with filtering.

        Args:
            session_id: Session identifier
            context_type: Optional type filter
            priority: Optional priority filter
            limit: Optional limit on results
            **kwargs: Additional filter parameters

        Returns:
            List of matching ContextSegments
        """
        if not self._hot_store:
            return []

        # Get segments from hot storage
        segments = self._hot_store.get(
            session_id=session_id,
            context_type=context_type,
            priority=priority,
            limit=limit,
            **kwargs
        )

        # Mark as accessed for LRU tracking
        for segment in segments:
            segment.mark_accessed()

        return segments

    def search_context(
        self,
        session_id: str,
        query: str,
        top_k: int = 10,
        **kwargs
    ) -> List[ContextSegment]:
        """Search context using keyword or semantic search.

        Args:
            session_id: Session identifier
            query: Search query
            top_k: Number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of matching ContextSegments ranked by relevance
        """
        if not self._hot_store:
            return []

        results = self._hot_store.search(
            query=query,
            session_id=session_id,
            top_k=top_k,
            **kwargs
        )

        # Mark as accessed
        for segment in results:
            segment.mark_accessed()

        return results

    def get_context_window(self, session_id: str) -> Optional[ContextWindow]:
        """Get context window for a session.

        Args:
            session_id: Session identifier

        Returns:
            ContextWindow if exists, None otherwise
        """
        return self._windows.get(session_id)

    def delete_context(
        self,
        session_id: str,
        segment_ids: Optional[List[str]] = None
    ) -> None:
        """Delete context segments.

        Args:
            session_id: Session identifier
            segment_ids: Optional list of segment IDs to delete (None = all)
        """
        if not self._hot_store:
            return

        # Get window to update token count
        window = self._windows.get(session_id)

        if segment_ids and window:
            # Calculate tokens to remove
            segments = self._hot_store.get_by_ids(session_id, segment_ids)
            tokens_removed = sum(seg.tokens for seg in segments)
            window.update_total_tokens(tokens_removed, operation="remove")

            # Remove from window tracking
            for seg_id in segment_ids:
                window.remove_segment_id(seg_id)
        elif not segment_ids and window:
            # Deleting all - reset window
            window.update_total_tokens(window.total_tokens, operation="remove")
            window.segment_ids.clear()

        # Delete from storage
        self._hot_store.delete(session_id, segment_ids=segment_ids)

    def _make_room(self, window: ContextWindow, needed_tokens: int) -> None:
        """Proactively make room through intelligent compression/eviction.

        This is called BEFORE adding new context when budget would be exceeded.
        Phase 2: Now uses intelligent compression strategies.

        Args:
            window: Context window that needs space
            needed_tokens: Number of tokens needed
        """
        if not self._hot_store:
            return

        current_available = window.calculate_available_tokens()
        if current_available >= needed_tokens:
            return  # Already have space

        tokens_to_free = needed_tokens - current_available

        # Strategy 1: Quick prune of expired and EPHEMERAL segments
        pruned = self._hot_store.prune(
            window.session_id,
            min_priority=ContextPriority.LOW  # Remove LOW and EPHEMERAL
        )

        if pruned > 0:
            # Recalculate window tokens after pruning
            remaining = self._hot_store.get(window.session_id)
            new_total = sum(seg.tokens for seg in remaining)
            window.total_tokens = new_total
            window.segment_ids = [seg.id for seg in remaining]

        # Check if pruning freed enough space
        if window.calculate_available_tokens() >= needed_tokens:
            return

        # Strategy 2: Intelligent compression (NEW in Phase 2)
        if self.enable_compression and self._compressor:
            segments = self._hot_store.get(window.session_id)

            if not segments:
                return  # Nothing to compress

            # Calculate target tokens for compression
            target_tokens = window.calculate_input_tokens()

            try:
                # Use compressor to intelligently compress segments
                compressed, metrics = self._compressor.compress(
                    segments,
                    target_tokens,
                    time_limit_ms=500,  # 500ms max for compression
                    min_quality=0.9,    # Target 90% preservation
                    preserve_types=[ContextType.SYSTEM, ContextType.TASK]  # Never compress these
                )

                # Replace segments in storage
                self._hot_store.delete(window.session_id)  # Clear old segments
                self._hot_store.add(compressed, session_id=window.session_id)  # Add compressed

                # Update window tracking
                window.total_tokens = sum(seg.tokens for seg in compressed)
                window.segment_ids = [seg.id for seg in compressed]

                # Log compression metrics (optional - for debugging/monitoring)
                # print(f"Compression: {metrics.compression_ratio:.2%}, Loss: {metrics.information_loss_estimate:.2%}")

                return  # Compression successful

            except Exception as e:
                # Compression failed, fall back to simple eviction
                pass

        # Strategy 3: Fallback - Simple eviction by priority and decay
        segments = self._hot_store.get(window.session_id)

        # Sort by: priority (lower first), decay score (lower first), last_accessed (older first)
        def eviction_key(seg):
            priority_order = {
                ContextPriority.EPHEMERAL: 0,
                ContextPriority.LOW: 1,
                ContextPriority.MEDIUM: 2,
                ContextPriority.HIGH: 3,
                ContextPriority.CRITICAL: 4,
            }
            return (
                priority_order.get(seg.priority, 2),
                seg.calculate_decay(),
                seg.metadata.last_accessed
            )

        eviction_candidates = sorted(segments, key=eviction_key)

        # Remove segments until we have enough space
        freed_tokens = 0
        to_remove = []

        for seg in eviction_candidates:
            if seg.priority == ContextPriority.CRITICAL:
                continue  # Never evict CRITICAL

            to_remove.append(seg.id)
            freed_tokens += seg.tokens

            if freed_tokens >= tokens_to_free:
                break

        if to_remove:
            self.delete_context(window.session_id, segment_ids=to_remove)

    def _count_tokens(self, content: str) -> int:
        """Count tokens in content using LLM tokenizer.

        Args:
            content: Text content to count

        Returns:
            Number of tokens
        """
        if self._llm and hasattr(self._llm, 'get_num_tokens'):
            return self._llm.get_num_tokens(content)

        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(content) // 4

    def get_budget_utilization(self, session_id: str) -> Dict[str, Any]:
        """Get detailed budget utilization metrics.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with utilization metrics
        """
        window = self._windows.get(session_id)
        if not window:
            return {}

        return {
            "session_id": session_id,
            "max_tokens": window.max_tokens,
            "reserved_tokens": window.reserved_tokens,
            "input_budget": window.calculate_input_tokens(),
            "total_tokens": window.total_tokens,
            "available_tokens": window.calculate_available_tokens(),
            "utilization": window.get_budget_utilization(),
            "is_over_budget": window.is_over_budget(),
            "segment_count": len(window.segment_ids),
            "component_budgets": window.component_budgets,
        }
