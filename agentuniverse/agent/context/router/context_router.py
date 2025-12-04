# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 18:00
# @Author  : kaichuan
# @FileName: context_router.py
"""Context Router - Task-specific routing for multi-tier storage.

The ContextRouter determines which storage tier (hot/warm/cold) to use
for different context operations based on task type, context type,
and access patterns.

Routing Rules:
- code_generation: Hot (workspace, reference), Warm (knowledge)
- data_analysis: Hot + Warm (background), Cold (historical data)
- dialogue: Hot (conversation), Warm (recent), Cold (old sessions)
"""

from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.agent.context.context_model import ContextType, ContextPriority


class RoutingRule(BaseModel):
    """Routing rule for context operations.

    Defines which storage tiers to search and their priority order.
    """

    priority_types: List[ContextType] = Field(
        default_factory=list,
        description="Context types to prioritize for this task"
    )
    search_tiers: List[str] = Field(
        default=["hot", "warm"],
        description="Storage tiers to search in order"
    )
    write_tier: str = Field(
        default="hot",
        description="Primary tier for writing new context"
    )
    archive_after_hours: Optional[int] = Field(
        default=None,
        description="Hours after which to archive to cold tier"
    )
    compression_strategy: str = Field(
        default="adaptive",
        description="Compression strategy for this task type"
    )


class ContextRouter(ComponentBase):
    """Router for multi-tier context storage operations.

    Routes context operations (read/write/search) to appropriate storage
    tiers based on task type, context characteristics, and access patterns.

    Attributes:
        routing_rules: Task-specific routing configurations
        default_rule: Default routing when no task-specific rule exists
        enable_warm_tier: Whether warm tier is available
        enable_cold_tier: Whether cold tier is available
    """

    component_type: ComponentEnum = ComponentEnum.CONTEXT_ROUTER

    enable_warm_tier: bool = False
    enable_cold_tier: bool = False

    # Task-specific routing rules
    routing_rules: Dict[str, RoutingRule] = {
        "code_generation": RoutingRule(
            priority_types=[
                ContextType.WORKSPACE,
                ContextType.REFERENCE,
                ContextType.TASK,
            ],
            search_tiers=["hot", "warm"],
            write_tier="hot",
            archive_after_hours=48,
            compression_strategy="selective",
        ),
        "data_analysis": RoutingRule(
            priority_types=[
                ContextType.BACKGROUND,
                ContextType.WORKSPACE,
                ContextType.REFERENCE,
            ],
            search_tiers=["hot", "warm", "cold"],
            write_tier="hot",
            archive_after_hours=24,
            compression_strategy="summarize",
        ),
        "dialogue": RoutingRule(
            priority_types=[
                ContextType.CONVERSATION,
                ContextType.SYSTEM,
                ContextType.BACKGROUND,
            ],
            search_tiers=["hot"],
            write_tier="hot",
            archive_after_hours=72,
            compression_strategy="adaptive",
        ),
    }

    default_rule: RoutingRule = RoutingRule(
        priority_types=[],
        search_tiers=["hot"],
        write_tier="hot",
        archive_after_hours=48,
        compression_strategy="adaptive",
    )

    def get_routing_rule(self, task_type: Optional[str] = None) -> RoutingRule:
        """Get routing rule for a task type.

        Args:
            task_type: Task type (e.g., 'code_generation', 'dialogue')

        Returns:
            RoutingRule for the task type or default rule
        """
        if task_type and task_type in self.routing_rules:
            return self.routing_rules[task_type]
        return self.default_rule

    def route_read(
        self,
        task_type: Optional[str] = None,
        context_type: Optional[ContextType] = None,
        priority: Optional[ContextPriority] = None,
        **kwargs
    ) -> List[str]:
        """Determine which storage tiers to search for read operations.

        Args:
            task_type: Task type
            context_type: Context type filter
            priority: Priority filter
            **kwargs: Additional routing parameters

        Returns:
            List of storage tier names in search order
        """
        rule = self.get_routing_rule(task_type)
        tiers = rule.search_tiers.copy()

        # Filter based on available tiers
        available_tiers = ["hot"]
        if self.enable_warm_tier:
            available_tiers.append("warm")
        if self.enable_cold_tier:
            available_tiers.append("cold")

        tiers = [tier for tier in tiers if tier in available_tiers]

        # Optimize based on context characteristics
        if priority == ContextPriority.CRITICAL:
            # CRITICAL should always be in hot tier
            return ["hot"]

        if context_type in [ContextType.SYSTEM, ContextType.TASK]:
            # System and task context in hot tier
            return ["hot"]

        # Check for recency hint
        max_age_hours = kwargs.get("max_age_hours")
        if max_age_hours and max_age_hours <= 24:
            # Recent context likely in hot/warm
            return [t for t in tiers if t in ["hot", "warm"]]

        return tiers

    def route_write(
        self,
        task_type: Optional[str] = None,
        context_type: Optional[ContextType] = None,
        priority: Optional[ContextPriority] = None,
        **kwargs
    ) -> str:
        """Determine which storage tier to use for write operations.

        Args:
            task_type: Task type
            context_type: Context type
            priority: Priority level
            **kwargs: Additional routing parameters

        Returns:
            Storage tier name for writing
        """
        rule = self.get_routing_rule(task_type)

        # Always write to hot tier initially
        # Archive operations will move to cold tier later
        return rule.write_tier

    def should_archive(
        self,
        segment_age_hours: float,
        task_type: Optional[str] = None,
        priority: Optional[ContextPriority] = None,
        access_count: int = 0,
    ) -> bool:
        """Determine if a segment should be archived to cold tier.

        Args:
            segment_age_hours: Hours since segment creation
            task_type: Task type
            priority: Segment priority
            access_count: Number of times accessed

        Returns:
            True if segment should be archived
        """
        # Never archive CRITICAL priority
        if priority == ContextPriority.CRITICAL:
            return False

        # Don't archive if accessed recently
        if access_count > 0 and segment_age_hours < 24:
            return False

        rule = self.get_routing_rule(task_type)

        if rule.archive_after_hours is None:
            return False

        # Archive if older than threshold
        if segment_age_hours >= rule.archive_after_hours:
            # Consider access frequency
            if access_count == 0:
                return True  # Never accessed, archive

            # Archive if infrequently accessed
            access_rate = access_count / (segment_age_hours / 24)  # Accesses per day
            return access_rate < 0.1  # Less than 0.1 accesses per day

        return False

    def get_compression_strategy(
        self,
        task_type: Optional[str] = None
    ) -> str:
        """Get compression strategy for a task type.

        Args:
            task_type: Task type

        Returns:
            Compression strategy name
        """
        rule = self.get_routing_rule(task_type)
        return rule.compression_strategy

    def get_priority_types(
        self,
        task_type: Optional[str] = None
    ) -> List[ContextType]:
        """Get priority context types for a task.

        Args:
            task_type: Task type

        Returns:
            List of context types to prioritize
        """
        rule = self.get_routing_rule(task_type)
        return rule.priority_types

    def optimize_search_order(
        self,
        query: str,
        task_type: Optional[str] = None,
        context_type: Optional[ContextType] = None,
        **kwargs
    ) -> List[str]:
        """Optimize search order based on query characteristics.

        Args:
            query: Search query
            task_type: Task type
            context_type: Context type filter
            **kwargs: Additional parameters

        Returns:
            Optimized list of storage tiers to search
        """
        tiers = self.route_read(task_type, context_type, **kwargs)

        # Keyword-based optimization
        query_lower = query.lower()

        # Recent context indicators
        recent_keywords = ["recent", "latest", "current", "now", "today"]
        if any(kw in query_lower for kw in recent_keywords):
            # Prioritize hot tier
            if "hot" in tiers:
                tiers.remove("hot")
                tiers.insert(0, "hot")

        # Historical context indicators
        historical_keywords = ["history", "past", "old", "previous", "archive"]
        if any(kw in query_lower for kw in historical_keywords):
            # Prioritize cold tier if available
            if "cold" in tiers:
                tiers.remove("cold")
                tiers.append("cold")  # Search last (but include)

        return tiers
