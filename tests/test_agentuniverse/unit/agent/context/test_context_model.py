# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_context_model.py
"""Unit tests for context data models."""

import pytest
from datetime import datetime, timedelta

from agentuniverse.agent.context.context_model import (
    ContextType,
    ContextPriority,
    ContextMetadata,
    ContextSegment,
    ContextWindow,
)


class TestContextType:
    """Test ContextType enum."""

    def test_context_types(self):
        """Test all context types are defined."""
        assert ContextType.SYSTEM == "system"
        assert ContextType.TASK == "task"
        assert ContextType.BACKGROUND == "background"
        assert ContextType.CONVERSATION == "conversation"
        assert ContextType.WORKSPACE == "workspace"
        assert ContextType.REFERENCE == "reference"
        assert ContextType.SUMMARY == "summary"
        assert ContextType.TOOL_RESULT == "tool_result"


class TestContextPriority:
    """Test ContextPriority enum."""

    def test_context_priorities(self):
        """Test all priority levels are defined."""
        assert ContextPriority.CRITICAL == "critical"
        assert ContextPriority.HIGH == "high"
        assert ContextPriority.MEDIUM == "medium"
        assert ContextPriority.LOW == "low"
        assert ContextPriority.EPHEMERAL == "ephemeral"


class TestContextMetadata:
    """Test ContextMetadata model."""

    def test_default_values(self):
        """Test default metadata values."""
        metadata = ContextMetadata()

        assert metadata.created_at is not None
        assert metadata.last_accessed is not None
        assert metadata.access_count == 0
        assert metadata.relevance_score == 1.0
        assert metadata.decay_rate == 0.1
        assert metadata.source_type == "user_input"
        assert not metadata.compressed
        assert metadata.version == 1

    def test_calculate_decay_no_decay(self):
        """Test decay calculation when just created."""
        metadata = ContextMetadata()
        decay_score = metadata.calculate_decay()

        # Should be close to 1.0 (just created)
        assert decay_score >= 0.95

    def test_calculate_decay_with_time(self):
        """Test decay calculation with time passage."""
        metadata = ContextMetadata(
            created_at=datetime.now() - timedelta(hours=24),
            last_accessed=datetime.now() - timedelta(hours=24),
            relevance_score=1.0,
            decay_rate=0.1
        )

        decay_score = metadata.calculate_decay()

        # After 24 hours with decay_rate=0.1, should decay
        assert 0.0 < decay_score < 1.0

    def test_update_access(self):
        """Test access tracking update."""
        metadata = ContextMetadata(access_count=5)
        old_time = metadata.last_accessed

        metadata.update_access()

        assert metadata.access_count == 6
        assert metadata.last_accessed > old_time


class TestContextSegment:
    """Test ContextSegment model."""

    def test_create_segment(self):
        """Test basic segment creation."""
        segment = ContextSegment(
            type=ContextType.CONVERSATION,
            priority=ContextPriority.HIGH,
            content="User: Hello, how are you?",
            tokens=10,
            session_id="test_session",
        )

        assert segment.id is not None
        assert segment.type == ContextType.CONVERSATION
        assert segment.priority == ContextPriority.HIGH
        assert segment.content == "User: Hello, how are you?"
        assert segment.tokens == 10
        assert segment.session_id == "test_session"
        assert segment.metadata is not None

    def test_update_content_detection(self):
        """Test content change detection."""
        segment = ContextSegment(
            type=ContextType.TASK,
            content="Original content",
            tokens=5,
        )

        # Update with different content
        changed = segment.update_content("New content", 8)

        assert changed is True
        assert segment.content == "New content"
        assert segment.tokens == 8
        assert segment.metadata.version == 2

    def test_update_content_no_change(self):
        """Test no change detection."""
        segment = ContextSegment(
            type=ContextType.TASK,
            content="Same content",
            tokens=5,
        )

        # Update with same content
        changed = segment.update_content("Same content", 5)

        assert changed is False
        assert segment.metadata.version == 1

    def test_mark_accessed(self):
        """Test access tracking."""
        segment = ContextSegment(
            type=ContextType.BACKGROUND,
            content="Test content",
            tokens=10,
        )

        initial_count = segment.metadata.access_count
        initial_time = segment.metadata.last_accessed

        segment.mark_accessed()

        assert segment.metadata.access_count == initial_count + 1
        assert segment.metadata.last_accessed > initial_time

    def test_calculate_decay(self):
        """Test decay calculation delegation."""
        segment = ContextSegment(
            type=ContextType.CONVERSATION,
            content="Test",
            tokens=5,
        )

        decay_score = segment.calculate_decay()

        assert 0.0 <= decay_score <= 1.0


class TestContextWindow:
    """Test ContextWindow model."""

    def test_create_window(self):
        """Test basic window creation."""
        window = ContextWindow(
            session_id="test_session",
            agent_id="test_agent",
            max_tokens=8000,
        )

        assert window.session_id == "test_session"
        assert window.agent_id == "test_agent"
        assert window.max_tokens == 8000
        assert window.reserved_tokens == 1000
        assert window.total_tokens == 0
        assert len(window.segment_ids) == 0

    def test_calculate_available_tokens(self):
        """Test available tokens calculation."""
        window = ContextWindow(
            session_id="test",
            max_tokens=8000,
            reserved_tokens=1000,
            total_tokens=3000,
        )

        available = window.calculate_available_tokens()

        # 8000 - 1000 - 3000 = 4000
        assert available == 4000

    def test_calculate_input_tokens(self):
        """Test input tokens calculation."""
        window = ContextWindow(
            session_id="test",
            max_tokens=8000,
            reserved_tokens=1000,
        )

        input_tokens = window.calculate_input_tokens()

        # 8000 - 1000 = 7000
        assert input_tokens == 7000

    def test_update_total_tokens_add(self):
        """Test adding tokens to total."""
        window = ContextWindow(
            session_id="test",
            total_tokens=100,
        )

        window.update_total_tokens(50, operation="add")

        assert window.total_tokens == 150

    def test_update_total_tokens_remove(self):
        """Test removing tokens from total."""
        window = ContextWindow(
            session_id="test",
            total_tokens=100,
        )

        window.update_total_tokens(30, operation="remove")

        assert window.total_tokens == 70

    def test_update_total_tokens_remove_floor(self):
        """Test removing more tokens than available (floor at 0)."""
        window = ContextWindow(
            session_id="test",
            total_tokens=50,
        )

        window.update_total_tokens(100, operation="remove")

        assert window.total_tokens == 0

    def test_is_over_budget(self):
        """Test budget check."""
        window = ContextWindow(
            session_id="test",
            max_tokens=8000,
            reserved_tokens=1000,
            total_tokens=7500,  # Over input budget (7000)
        )

        assert window.is_over_budget() is True

    def test_is_not_over_budget(self):
        """Test not over budget."""
        window = ContextWindow(
            session_id="test",
            max_tokens=8000,
            reserved_tokens=1000,
            total_tokens=5000,
        )

        assert window.is_over_budget() is False

    def test_get_budget_utilization(self):
        """Test budget utilization calculation."""
        window = ContextWindow(
            session_id="test",
            max_tokens=8000,
            reserved_tokens=1000,
            total_tokens=3500,
        )

        utilization = window.get_budget_utilization()

        # 3500 / 7000 = 0.5
        assert utilization == 0.5

    def test_add_segment_id(self):
        """Test adding segment ID."""
        window = ContextWindow(session_id="test")

        window.add_segment_id("seg_1")
        window.add_segment_id("seg_2")

        assert len(window.segment_ids) == 2
        assert "seg_1" in window.segment_ids
        assert "seg_2" in window.segment_ids

    def test_add_duplicate_segment_id(self):
        """Test adding duplicate segment ID (should not duplicate)."""
        window = ContextWindow(session_id="test")

        window.add_segment_id("seg_1")
        window.add_segment_id("seg_1")  # Duplicate

        assert len(window.segment_ids) == 1

    def test_remove_segment_id(self):
        """Test removing segment ID."""
        window = ContextWindow(session_id="test")
        window.add_segment_id("seg_1")
        window.add_segment_id("seg_2")

        window.remove_segment_id("seg_1")

        assert len(window.segment_ids) == 1
        assert "seg_2" in window.segment_ids
        assert "seg_1" not in window.segment_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
