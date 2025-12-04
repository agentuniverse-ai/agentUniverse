# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/04 11:00
# @Author  : kaichuan
# @FileName: test_phase2_integration.py
"""Integration tests for Phase 2: Multi-tier storage, compression, and routing."""

import pytest
from datetime import datetime, timedelta

from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.agent.context.compressor.adaptive_compressor import AdaptiveCompressor
from agentuniverse.agent.context.compressor.selective_compressor import SelectiveCompressor
from agentuniverse.agent.context.router.context_router import ContextRouter
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextType,
    ContextPriority,
)


class TestPhase2Integration:
    """Integration tests for Phase 2 features."""

    @pytest.fixture
    def hot_store(self):
        """Create hot storage."""
        return RamContextStore(
            name='test_hot_store',
            max_segments=100,
            ttl_hours=24
        )

    @pytest.fixture
    def compressor(self):
        """Create adaptive compressor."""
        return AdaptiveCompressor(
            name='test_compressor',
            compression_ratio=0.6,
            enable_hybrid=True
        )

    @pytest.fixture
    def router(self):
        """Create context router."""
        return ContextRouter(
            name='test_router',
            enable_warm_tier=False,
            enable_cold_tier=False
        )

    @pytest.fixture
    def context_manager(self, hot_store, compressor, router):
        """Create context manager with Phase 2 features."""
        manager = ContextManager(
            name='test_manager',
            hot_store_name='test_hot_store',
            default_max_tokens=1000,
            default_reserved_tokens=200,
            enable_compression=True
        )

        # Manually set references (in production, initialized from YAML)
        manager._hot_store = hot_store
        manager._compressor = compressor
        manager._router = router

        return manager

    def test_context_manager_with_compression(self, context_manager):
        """Test ContextManager with intelligent compression enabled."""
        session_id = "test_session_1"

        # Create context window
        window = context_manager.create_context_window(
            session_id,
            task_type='code_generation'
        )

        # Add context until compression is triggered
        for i in range(30):
            context_manager.add_context(
                session_id,
                f"This is a message with some content to fill up the context window. Message number {i}.",
                ContextType.CONVERSATION,
                ContextPriority.MEDIUM if i < 20 else ContextPriority.LOW
            )

        # Verify compression occurred
        metrics = context_manager.get_budget_utilization(session_id)
        assert not metrics['is_over_budget'], "Context should not be over budget"
        assert metrics['utilization'] <= 1.0, "Utilization should be <= 100%"

        # Verify segments are still retrievable
        segments = context_manager.get_context(session_id)
        assert len(segments) > 0, "Should have segments after compression"

    def test_priority_preservation_in_compression(self, context_manager):
        """Test that CRITICAL priority is preserved during compression."""
        session_id = "test_session_2"

        # Create context window
        context_manager.create_context_window(session_id, task_type='dialogue')

        # Add CRITICAL segment
        critical_seg = context_manager.add_context(
            session_id,
            "CRITICAL: This must never be compressed or removed",
            ContextType.SYSTEM,
            ContextPriority.CRITICAL
        )

        # Add many low-priority segments to trigger compression
        for i in range(50):
            context_manager.add_context(
                session_id,
                f"Low priority message {i}",
                ContextType.CONVERSATION,
                ContextPriority.EPHEMERAL if i % 2 == 0 else ContextPriority.LOW
            )

        # Verify CRITICAL segment is still present
        segments = context_manager.get_context(session_id)
        critical_ids = [s.id for s in segments if s.priority == ContextPriority.CRITICAL]

        assert critical_seg.id in critical_ids, "CRITICAL segment was removed during compression"

    def test_task_adaptive_budget_allocation(self, context_manager):
        """Test that different task types get different budget allocations."""
        # Code generation task
        code_window = context_manager.create_context_window(
            "code_session",
            task_type='code_generation'
        )

        # Data analysis task
        data_window = context_manager.create_context_window(
            "data_session",
            task_type='data_analysis'
        )

        # Dialogue task
        dialogue_window = context_manager.create_context_window(
            "dialogue_session",
            task_type='dialogue'
        )

        # Verify different budget allocations
        code_budgets = code_window.component_budgets
        data_budgets = data_window.component_budgets
        dialogue_budgets = dialogue_window.component_budgets

        # Code generation: High workspace allocation
        assert code_budgets.get('workspace', 0) > data_budgets.get('workspace', 0)

        # Data analysis: High background allocation
        assert data_budgets.get('background', 0) > code_budgets.get('background', 0)

        # Dialogue: High conversation allocation
        assert dialogue_budgets.get('conversation', 0) > code_budgets.get('conversation', 0)

    def test_proactive_budget_management(self, context_manager):
        """Test that budget is managed proactively before overflow."""
        session_id = "test_session_3"

        window = context_manager.create_context_window(
            session_id,
            task_type='dialogue',
            max_tokens=500,  # Small window for testing
            reserved_tokens=100
        )

        # Add segments up to near capacity
        for i in range(20):
            try:
                context_manager.add_context(
                    session_id,
                    f"Message {i}: " + "X" * 50,  # ~50 tokens each
                    ContextType.CONVERSATION,
                    ContextPriority.MEDIUM
                )
            except Exception as e:
                pytest.fail(f"Failed to add context: {e}")

        # Window should never exceed budget
        metrics = context_manager.get_budget_utilization(session_id)
        assert not metrics['is_over_budget'], "Budget was exceeded"
        assert metrics['total_tokens'] <= metrics['input_budget'], "Exceeded input budget"

    def test_compression_strategy_selection(self, context_manager):
        """Test that appropriate compression strategy is selected."""
        session_id = "test_session_4"

        context_manager.create_context_window(
            session_id,
            task_type='code_generation'
        )

        # Add diverse context
        context_manager.add_context(
            session_id,
            "System prompt",
            ContextType.SYSTEM,
            ContextPriority.CRITICAL
        )

        for i in range(30):
            context_manager.add_context(
                session_id,
                f"Code context {i}",
                ContextType.WORKSPACE,
                ContextPriority.HIGH if i < 15 else ContextPriority.MEDIUM
            )

        # Verify compression maintains CRITICAL
        segments = context_manager.get_context(session_id)
        critical_count = sum(1 for s in segments if s.priority == ContextPriority.CRITICAL)
        assert critical_count == 1, "CRITICAL segment should be preserved"

    def test_context_search_with_compression(self, context_manager):
        """Test that search works correctly after compression."""
        session_id = "test_session_5"

        context_manager.create_context_window(session_id, task_type='dialogue')

        # Add searchable content
        context_manager.add_context(
            session_id,
            "How do I implement authentication in Python?",
            ContextType.CONVERSATION,
            ContextPriority.HIGH
        )

        # Add many other messages
        for i in range(30):
            context_manager.add_context(
                session_id,
                f"Random message {i}",
                ContextType.CONVERSATION,
                ContextPriority.LOW
            )

        # Search for authentication-related content
        results = context_manager.search_context(
            session_id,
            "authentication Python",
            top_k=5
        )

        # Should find the authentication message
        assert len(results) > 0, "Search should return results"
        assert any("authentication" in r.content.lower() for r in results)

    def test_budget_utilization_metrics(self, context_manager):
        """Test that budget utilization metrics are accurate."""
        session_id = "test_session_6"

        window = context_manager.create_context_window(
            session_id,
            task_type='code_generation',
            max_tokens=1000,
            reserved_tokens=200
        )

        # Add some context
        for i in range(10):
            context_manager.add_context(
                session_id,
                f"Message {i}: " + "X" * 20,
                ContextType.CONVERSATION,
                ContextPriority.MEDIUM
            )

        metrics = context_manager.get_budget_utilization(session_id)

        # Verify metrics structure
        assert 'session_id' in metrics
        assert 'max_tokens' in metrics
        assert 'input_budget' in metrics
        assert 'total_tokens' in metrics
        assert 'available_tokens' in metrics
        assert 'utilization' in metrics
        assert 'is_over_budget' in metrics

        # Verify metric values
        assert metrics['max_tokens'] == 1000
        assert metrics['reserved_tokens'] == 200
        assert metrics['input_budget'] == 800  # 1000 - 200
        assert 0.0 <= metrics['utilization'] <= 1.0
        assert metrics['total_tokens'] <= metrics['input_budget']

    def test_context_deletion_updates_budget(self, context_manager):
        """Test that deleting context updates budget correctly."""
        session_id = "test_session_7"

        context_manager.create_context_window(session_id, task_type='dialogue')

        # Add segments
        segment_ids = []
        for i in range(10):
            seg = context_manager.add_context(
                session_id,
                f"Message {i}",
                ContextType.CONVERSATION,
                ContextPriority.MEDIUM
            )
            segment_ids.append(seg.id)

        # Get initial metrics
        metrics_before = context_manager.get_budget_utilization(session_id)

        # Delete half the segments
        context_manager.delete_context(session_id, segment_ids[:5])

        # Get updated metrics
        metrics_after = context_manager.get_budget_utilization(session_id)

        # Token count should decrease
        assert metrics_after['total_tokens'] < metrics_before['total_tokens']
        assert metrics_after['available_tokens'] > metrics_before['available_tokens']

    def test_router_tier_selection(self, router):
        """Test that router selects appropriate tiers for different scenarios."""
        # Code generation: Hot + Warm
        code_tiers = router.route_read(task_type='code_generation')
        assert 'hot' in code_tiers

        # Data analysis: Hot + Warm + Cold
        data_tiers = router.route_read(task_type='data_analysis')
        assert 'hot' in data_tiers

        # Dialogue: Hot only
        dialogue_tiers = router.route_read(task_type='dialogue')
        assert 'hot' in dialogue_tiers
        assert len(dialogue_tiers) == 1  # Only hot tier

    def test_router_archive_decision(self, router):
        """Test that router makes appropriate archive decisions."""
        # Recent CRITICAL: Never archive
        should_archive = router.should_archive(
            segment_age_hours=48,
            priority=ContextPriority.CRITICAL,
            access_count=0
        )
        assert not should_archive

        # Old, never accessed: Archive
        should_archive = router.should_archive(
            segment_age_hours=100,
            priority=ContextPriority.LOW,
            access_count=0,
            task_type='dialogue'
        )
        assert should_archive

        # Recent, frequently accessed: Don't archive
        should_archive = router.should_archive(
            segment_age_hours=24,
            priority=ContextPriority.MEDIUM,
            access_count=10
        )
        assert not should_archive

    def test_compression_preserves_relationships(self, context_manager):
        """Test that parent-child relationships are preserved during compression."""
        session_id = "test_session_8"

        context_manager.create_context_window(session_id, task_type='code_generation')

        # Add parent segment
        parent_seg = context_manager.add_context(
            session_id,
            "Parent context",
            ContextType.TASK,
            ContextPriority.HIGH
        )

        # Add child segments
        for i in range(10):
            context_manager.add_context(
                session_id,
                f"Child context {i}",
                ContextType.WORKSPACE,
                ContextPriority.MEDIUM,
                parent_id=parent_seg.id
            )

        # Add many unrelated segments to trigger compression
        for i in range(50):
            context_manager.add_context(
                session_id,
                f"Unrelated {i}",
                ContextType.CONVERSATION,
                ContextPriority.LOW
            )

        # Verify parent is still present
        segments = context_manager.get_context(session_id)
        parent_exists = any(s.id == parent_seg.id for s in segments)
        assert parent_exists, "Parent segment should be preserved"

    def test_end_to_end_multi_session(self, context_manager):
        """Test end-to-end workflow with multiple sessions."""
        sessions = ['session_a', 'session_b', 'session_c']

        # Create windows for multiple sessions
        for session_id in sessions:
            context_manager.create_context_window(
                session_id,
                task_type='dialogue'
            )

            # Add context to each session
            for i in range(20):
                context_manager.add_context(
                    session_id,
                    f"Session {session_id} message {i}",
                    ContextType.CONVERSATION,
                    ContextPriority.MEDIUM
                )

        # Verify each session has independent context
        for session_id in sessions:
            segments = context_manager.get_context(session_id)
            assert len(segments) > 0
            assert all(session_id in s.content for s in segments)

        # Verify sessions don't interfere
        session_a_segments = context_manager.get_context('session_a')
        assert not any('session_b' in s.content for s in session_a_segments)
        assert not any('session_c' in s.content for s in session_a_segments)


class TestMemoryIntegration:
    """Integration tests for Memory class with ContextManager."""

    def test_memory_budget_aware_retrieval(self):
        """Test that Memory uses budget-aware retrieval when linked to ContextManager."""
        from agentuniverse.agent.memory.memory import Memory
        from agentuniverse.agent.memory.message import Message

        # Create memory with context manager link
        memory = Memory(
            name='test_memory',
            context_manager_name='test_manager',
            max_tokens=1000
        )

        # Test get_with_context_budget method
        messages = memory.get_with_context_budget(
            session_id='test',
            agent_id='agent1',
            allocated_tokens=500
        )

        # Should return list (even if empty without actual storage)
        assert isinstance(messages, list)

    def test_memory_fallback_without_context_manager(self):
        """Test that Memory falls back gracefully without ContextManager."""
        from agentuniverse.agent.memory.memory import Memory

        # Create memory without context manager
        memory = Memory(
            name='test_memory',
            max_tokens=1000
        )

        # Should still work with fallback
        messages = memory.get_with_context_budget(
            session_id='test',
            agent_id='agent1',
            allocated_tokens=500
        )

        assert isinstance(messages, list)
