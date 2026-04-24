# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_context_manager.py
"""Unit tests for ContextManager."""

import pytest
from datetime import datetime, timedelta

from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.agent.context.context_model import (
    ContextType,
    ContextPriority,
)


class TestContextManager:
    """Test ContextManager orchestrator."""

    @pytest.fixture
    def store(self):
        """Create a RamContextStore instance."""
        return RamContextStore(
            name="test_ram_store",
            max_segments=100,
            ttl_hours=24,
        )

    @pytest.fixture
    def manager(self, store):
        """Create a ContextManager instance."""
        manager = ContextManager(
            name="test_context_manager",
            hot_store_name="test_ram_store",
            default_max_tokens=8000,
            default_reserved_tokens=1000,
        )
        # Manually inject store for testing (bypass YAML initialization)
        manager._hot_store = store
        return manager

    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager.name == "test_context_manager"
        assert manager.default_max_tokens == 8000
        assert manager.default_reserved_tokens == 1000
        assert manager._hot_store is not None
        assert len(manager.task_configs) >= 3  # code_generation, data_analysis, dialogue

    def test_create_context_window_default(self, manager):
        """Test creating context window with defaults."""
        window = manager.create_context_window(
            session_id="session_1",
            agent_id="test_agent"
        )

        assert window.session_id == "session_1"
        assert window.agent_id == "test_agent"
        assert window.max_tokens == 8000
        assert window.reserved_tokens == 1000
        assert window.total_tokens == 0

    def test_create_context_window_code_generation(self, manager):
        """Test creating context window for code generation task."""
        window = manager.create_context_window(
            session_id="session_1",
            task_type="code_generation"
        )

        assert window.task_type == "code_generation"
        assert window.max_tokens == 10000  # From task_configs
        assert window.reserved_tokens == 1500
        assert window.compression_strategy == "selective"

        # Check budget allocation
        input_budget = 10000 - 1500  # 8500
        assert "workspace" in window.component_budgets
        assert window.component_budgets["workspace"] == int(8500 * 0.5)  # 50%
        assert window.component_budgets["knowledge"] == int(8500 * 0.2)  # 20%

    def test_add_context_basic(self, manager):
        """Test adding context to a session."""
        manager.create_context_window("session_1")

        segment = manager.add_context(
            session_id="session_1",
            content="Test system prompt",
            context_type=ContextType.SYSTEM,
            priority=ContextPriority.CRITICAL
        )

        assert segment.id is not None
        assert segment.type == ContextType.SYSTEM
        assert segment.priority == ContextPriority.CRITICAL
        assert segment.content == "Test system prompt"
        assert segment.tokens > 0

        # Check window updated
        window = manager.get_context_window("session_1")
        assert window.total_tokens > 0
        assert len(window.segment_ids) == 1

    def test_add_context_auto_create_window(self, manager):
        """Test that add_context auto-creates window if not exists."""
        segment = manager.add_context(
            session_id="session_2",
            content="Auto-created window",
            context_type=ContextType.TASK,
            priority=ContextPriority.HIGH
        )

        assert segment.id is not None

        # Window should be auto-created
        window = manager.get_context_window("session_2")
        assert window is not None
        assert window.session_id == "session_2"

    def test_get_context_all(self, manager):
        """Test retrieving all context for a session."""
        manager.create_context_window("session_1")

        # Add multiple segments
        manager.add_context(
            "session_1",
            "System prompt",
            ContextType.SYSTEM,
            ContextPriority.CRITICAL
        )
        manager.add_context(
            "session_1",
            "User message",
            ContextType.CONVERSATION,
            ContextPriority.HIGH
        )
        manager.add_context(
            "session_1",
            "Background info",
            ContextType.BACKGROUND,
            ContextPriority.MEDIUM
        )

        # Get all
        segments = manager.get_context("session_1")
        assert len(segments) == 3

    def test_get_context_filtered_by_type(self, manager):
        """Test retrieving context filtered by type."""
        manager.create_context_window("session_1")

        manager.add_context(
            "session_1",
            "User: Hello",
            ContextType.CONVERSATION,
            ContextPriority.HIGH
        )
        manager.add_context(
            "session_1",
            "Assistant: Hi!",
            ContextType.CONVERSATION,
            ContextPriority.HIGH
        )
        manager.add_context(
            "session_1",
            "Background context",
            ContextType.BACKGROUND,
            ContextPriority.MEDIUM
        )

        # Get only conversations
        conversations = manager.get_context(
            "session_1",
            context_type=ContextType.CONVERSATION
        )

        assert len(conversations) == 2
        assert all(s.type == ContextType.CONVERSATION for s in conversations)

    def test_get_context_filtered_by_priority(self, manager):
        """Test retrieving context filtered by priority."""
        manager.create_context_window("session_1")

        manager.add_context(
            "session_1",
            "Critical",
            ContextType.SYSTEM,
            ContextPriority.CRITICAL
        )
        manager.add_context(
            "session_1",
            "High",
            ContextType.TASK,
            ContextPriority.HIGH
        )
        manager.add_context(
            "session_1",
            "Low",
            ContextType.BACKGROUND,
            ContextPriority.LOW
        )

        # Get only HIGH priority
        high_priority = manager.get_context(
            "session_1",
            priority=ContextPriority.HIGH
        )

        assert len(high_priority) == 1
        assert high_priority[0].priority == ContextPriority.HIGH

    def test_search_context(self, manager):
        """Test searching context."""
        manager.create_context_window("session_1")

        manager.add_context(
            "session_1",
            "Python is a programming language",
            ContextType.BACKGROUND,
            ContextPriority.MEDIUM
        )
        manager.add_context(
            "session_1",
            "JavaScript is also a programming language",
            ContextType.BACKGROUND,
            ContextPriority.MEDIUM
        )
        manager.add_context(
            "session_1",
            "Cooking recipes",
            ContextType.BACKGROUND,
            ContextPriority.LOW
        )

        # Search for "programming"
        results = manager.search_context("session_1", "programming", top_k=10)

        assert len(results) == 2
        assert all("programming" in s.content.lower() for s in results)

    def test_delete_context_specific(self, manager):
        """Test deleting specific segments."""
        manager.create_context_window("session_1")

        seg1 = manager.add_context(
            "session_1", "Segment 1", ContextType.TASK, ContextPriority.HIGH
        )
        seg2 = manager.add_context(
            "session_1", "Segment 2", ContextType.TASK, ContextPriority.HIGH
        )
        seg3 = manager.add_context(
            "session_1", "Segment 3", ContextType.TASK, ContextPriority.HIGH
        )

        # Delete seg1 and seg2
        manager.delete_context("session_1", segment_ids=[seg1.id, seg2.id])

        # Only seg3 should remain
        remaining = manager.get_context("session_1")
        assert len(remaining) == 1
        assert remaining[0].id == seg3.id

        # Window should be updated
        window = manager.get_context_window("session_1")
        assert len(window.segment_ids) == 1

    def test_delete_context_all(self, manager):
        """Test deleting all segments for a session."""
        manager.create_context_window("session_1")

        manager.add_context("session_1", "Seg 1", ContextType.TASK, ContextPriority.HIGH)
        manager.add_context("session_1", "Seg 2", ContextType.TASK, ContextPriority.HIGH)

        manager.delete_context("session_1")

        # All should be deleted
        remaining = manager.get_context("session_1")
        assert len(remaining) == 0

        # Window should be cleared
        window = manager.get_context_window("session_1")
        assert window.total_tokens == 0
        assert len(window.segment_ids) == 0

    def test_proactive_budget_management(self, manager):
        """Test that budget management is proactive (makes room before adding)."""
        # Create small window
        window = manager.create_context_window(
            "session_1",
            max_tokens=1000,
            reserved_tokens=200
        )

        # Input budget: 800 tokens
        # Add segments that approach the limit
        for i in range(10):
            content = "A" * 320  # ~80 tokens each
            manager.add_context(
                "session_1",
                content,
                ContextType.BACKGROUND,
                ContextPriority.LOW if i < 5 else ContextPriority.MEDIUM
            )

        # Window should not exceed budget
        window = manager.get_context_window("session_1")
        assert not window.is_over_budget()
        assert window.total_tokens <= window.calculate_input_tokens()

    def test_make_room_eviction(self, manager):
        """Test that _make_room evicts low-priority segments."""
        window = manager.create_context_window(
            "session_1",
            max_tokens=1000,
            reserved_tokens=200
        )

        # Fill with LOW and CRITICAL segments
        critical_seg = manager.add_context(
            "session_1",
            "Critical information " * 50,  # Large content
            ContextType.SYSTEM,
            ContextPriority.CRITICAL
        )

        for i in range(5):
            manager.add_context(
                "session_1",
                "Low priority " * 30,
                ContextType.BACKGROUND,
                ContextPriority.LOW
            )

        # Try to add more content (should trigger eviction)
        new_seg = manager.add_context(
            "session_1",
            "New content " * 50,
            ContextType.TASK,
            ContextPriority.HIGH
        )

        # CRITICAL should still be present
        all_segments = manager.get_context("session_1")
        assert any(s.id == critical_seg.id for s in all_segments)

        # Some LOW priority should have been evicted
        low_count = sum(1 for s in all_segments if s.priority == ContextPriority.LOW)
        assert low_count < 5  # Some were evicted

        # Window should not exceed budget
        window = manager.get_context_window("session_1")
        assert not window.is_over_budget()

    def test_get_budget_utilization(self, manager):
        """Test budget utilization metrics."""
        manager.create_context_window("session_1", max_tokens=8000, reserved_tokens=1000)

        manager.add_context(
            "session_1",
            "Content " * 100,
            ContextType.TASK,
            ContextPriority.HIGH
        )

        metrics = manager.get_budget_utilization("session_1")

        assert metrics["session_id"] == "session_1"
        assert metrics["max_tokens"] == 8000
        assert metrics["reserved_tokens"] == 1000
        assert metrics["input_budget"] == 7000
        assert metrics["total_tokens"] > 0
        assert metrics["available_tokens"] >= 0
        assert 0.0 <= metrics["utilization"] <= 1.0
        assert "is_over_budget" in metrics
        assert "segment_count" in metrics

    def test_multiple_sessions(self, manager):
        """Test managing multiple sessions independently."""
        # Create windows for multiple sessions
        manager.create_context_window("session_1")
        manager.create_context_window("session_2")

        # Add context to each
        manager.add_context("session_1", "Session 1 content", ContextType.TASK, ContextPriority.HIGH)
        manager.add_context("session_2", "Session 2 content", ContextType.TASK, ContextPriority.HIGH)

        # Each session should have its own context
        seg1 = manager.get_context("session_1")
        seg2 = manager.get_context("session_2")

        assert len(seg1) == 1
        assert len(seg2) == 1
        assert seg1[0].content == "Session 1 content"
        assert seg2[0].content == "Session 2 content"

    def test_task_configs_all_present(self, manager):
        """Test that all task types have configurations."""
        assert "code_generation" in manager.task_configs
        assert "data_analysis" in manager.task_configs
        assert "dialogue" in manager.task_configs

        # Check each config has required fields
        for task_type, config in manager.task_configs.items():
            assert "max_tokens" in config
            assert "reserved_tokens" in config
            assert "budget_ratios" in config
            assert "compression_strategy" in config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
