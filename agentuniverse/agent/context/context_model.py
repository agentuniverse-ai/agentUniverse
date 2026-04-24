# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan

# @FileName: context_model.py
"""Core data models for context engineering system."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid
import hashlib


class ContextType(str, Enum):
    """Types of context segments for categorization and routing."""
    SYSTEM = "system"              # System prompts, instructions
    TASK = "task"                  # Current task description
    BACKGROUND = "background"      # Knowledge base, domain info
    CONVERSATION = "conversation"  # Chat history, dialogue
    WORKSPACE = "workspace"        # Code files, documents
    REFERENCE = "reference"        # Documentation, examples
    SUMMARY = "summary"            # Compressed summaries
    TOOL_RESULT = "tool_result"    # Tool execution results


class ContextPriority(str, Enum):
    """Priority levels for context segments determining compression behavior."""
    CRITICAL = "critical"    # Never compress (e.g., system prompts)
    HIGH = "high"           # Compress only when necessary
    MEDIUM = "medium"       # Normal compression
    LOW = "low"             # Aggressive compression
    EPHEMERAL = "ephemeral" # Can be discarded freely


class ContextMetadata(BaseModel):
    """Rich metadata for context segment tracking and management."""

    # Temporal tracking
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = Field(default=0, ge=0)

    # Relevance and decay
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    decay_rate: float = Field(default=0.1, ge=0.0, le=1.0)

    # Source tracking
    source_type: str = Field(default="user_input")  # user_input, agent_output, knowledge_base, tool
    source_id: Optional[str] = None

    # Semantic metadata
    embedding_id: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    entities: Dict[str, Any] = Field(default_factory=dict)

    # Compression tracking
    compressed: bool = Field(default=False)
    compression_ratio: Optional[float] = None
    original_tokens: Optional[int] = None
    compression_method: Optional[str] = None

    # Version control (for knowledge updates)
    version: int = Field(default=1, ge=1)
    superseded_by: Optional[str] = None  # segment ID that replaces this
    valid_until: Optional[datetime] = None

    # Additional custom metadata
    custom: Dict[str, Any] = Field(default_factory=dict)

    def calculate_decay(self) -> float:
        """Calculate time-based decay score.

        Returns:
            float: Decayed relevance score (0.0-1.0)
        """
        if self.relevance_score == 0.0:
            return 0.0

        time_since_access = (datetime.now() - self.last_accessed).total_seconds() / 3600  # hours
        decay_factor = max(0.0, 1.0 - (time_since_access * self.decay_rate / 24))  # 24 hours baseline

        return self.relevance_score * decay_factor

    def update_access(self) -> None:
        """Update access tracking."""
        self.last_accessed = datetime.now()
        self.access_count += 1


class ContextSegment(BaseModel):
    """Individual context unit with type, priority, and rich metadata."""

    # Core identification
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    # Classification
    type: ContextType
    priority: ContextPriority = ContextPriority.MEDIUM

    # Content
    content: str
    tokens: int = Field(ge=0)

    # Metadata
    metadata: ContextMetadata = Field(default_factory=ContextMetadata)

    # Relationships
    parent_id: Optional[str] = None
    related_ids: List[str] = Field(default_factory=list)

    # Scope
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None

    # Content hash for change detection
    _content_hash: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self._content_hash = self._calculate_content_hash()

    def _calculate_content_hash(self) -> str:
        """Calculate MD5 hash of content for change detection."""
        return hashlib.md5(self.content.encode('utf-8')).hexdigest()

    def update_content(self, new_content: str, new_tokens: int) -> bool:
        """Update content and detect changes.

        Args:
            new_content: New content string
            new_tokens: Token count for new content

        Returns:
            bool: True if content changed
        """
        new_hash = hashlib.md5(new_content.encode('utf-8')).hexdigest()

        if new_hash != self._content_hash:
            self.content = new_content
            self.tokens = new_tokens
            self._content_hash = new_hash
            self.metadata.version += 1
            return True

        return False

    def calculate_decay(self) -> float:
        """Calculate current decay score (delegates to metadata)."""
        return self.metadata.calculate_decay()

    def mark_accessed(self) -> None:
        """Mark segment as accessed (updates metadata)."""
        self.metadata.update_access()


class ContextWindow(BaseModel):
    """Unified token budget container for session-scoped context management."""

    # Session identification
    session_id: str
    agent_id: Optional[str] = None
    task_id: Optional[str] = None

    # Budget configuration
    max_tokens: int = Field(default=8000, gt=0)
    reserved_tokens: int = Field(default=1000, ge=0)  # For output
    system_tokens: int = Field(default=500, ge=0)     # For system prompts

    # Component allocation (proactive budget management)
    component_budgets: Dict[str, int] = Field(default_factory=dict)
    # Example: {"memory": 2000, "knowledge": 3000, "workspace": 2500}

    # Current state
    segment_ids: List[str] = Field(default_factory=list)  # Lightweight: only IDs
    total_tokens: int = Field(default=0, ge=0)

    # Task-specific configuration
    task_type: Optional[str] = None  # code_generation, data_analysis, dialogue
    compression_strategy: str = Field(default="adaptive")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

    def calculate_available_tokens(self) -> int:
        """Calculate tokens available for new context.

        Returns:
            int: Available token budget
        """
        return max(0, self.max_tokens - self.reserved_tokens - self.total_tokens)

    def calculate_input_tokens(self) -> int:
        """Calculate maximum tokens for input (excluding reserved for output).

        Returns:
            int: Maximum input token budget
        """
        return max(0, self.max_tokens - self.reserved_tokens)

    def update_total_tokens(self, segment_tokens: int, operation: str = "add") -> None:
        """Update total token count.

        Args:
            segment_tokens: Number of tokens to add/remove
            operation: "add" or "remove"
        """
        if operation == "add":
            self.total_tokens += segment_tokens
        elif operation == "remove":
            self.total_tokens = max(0, self.total_tokens - segment_tokens)

        self.last_updated = datetime.now()

    def is_over_budget(self) -> bool:
        """Check if context window exceeds budget.

        Returns:
            bool: True if over budget
        """
        return self.total_tokens > self.calculate_input_tokens()

    def get_budget_utilization(self) -> float:
        """Calculate budget utilization percentage.

        Returns:
            float: Utilization (0.0-1.0+, can exceed 1.0 if over budget)
        """
        input_budget = self.calculate_input_tokens()
        if input_budget == 0:
            return 0.0

        return self.total_tokens / input_budget

    def add_segment_id(self, segment_id: str) -> None:
        """Add segment ID to window."""
        if segment_id not in self.segment_ids:
            self.segment_ids.append(segment_id)
            self.last_updated = datetime.now()

    def remove_segment_id(self, segment_id: str) -> None:
        """Remove segment ID from window."""
        if segment_id in self.segment_ids:
            self.segment_ids.remove(segment_id)
            self.last_updated = datetime.now()
