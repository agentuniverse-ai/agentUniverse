# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/04 15:30
# @Author  : kaichuan
# @FileName: test_context_router.py
"""Unit tests for ContextRouter routing logic (offline)."""

import pytest

from agentuniverse.agent.context.context_model import ContextPriority, ContextType
from agentuniverse.agent.context.router.context_router import (
    ContextRouter, RoutingRule)


class TestContextRouter:
    """Test ContextRouter tier routing, archiving and search order."""

    @pytest.fixture
    def router(self):
        """Router with warm and cold tiers enabled."""
        return ContextRouter(enable_warm_tier=True, enable_cold_tier=True)

    @pytest.fixture
    def hot_only(self):
        """Router with only the hot tier enabled (default)."""
        return ContextRouter()

    def test_default_rules(self, router):
        assert router.enable_warm_tier is True and router.enable_cold_tier is True
        assert router.default_rule.write_tier == "hot"
        assert router.default_rule.search_tiers == ["hot"]
        assert router.default_rule.compression_strategy == "adaptive"
        assert router.routing_rules["code_generation"].search_tiers == ["hot", "warm"]
        assert router.routing_rules["code_generation"].compression_strategy == "selective"
        assert router.routing_rules["dialogue"].archive_after_hours == 72

    def test_get_routing_rule(self, router):
        assert router.get_routing_rule("dialogue") is router.routing_rules["dialogue"]
        assert router.get_routing_rule("unknown_task") is router.default_rule
        assert router.get_routing_rule(None) is router.default_rule

    def test_route_read_tier_filtering(self, router, hot_only):
        assert router.route_read("code_generation") == ["hot", "warm"]
        assert router.route_read("data_analysis") == ["hot", "warm", "cold"]
        assert router.route_read("dialogue") == ["hot"]
        assert hot_only.route_read("data_analysis") == ["hot"]
        assert hot_only.route_read("code_generation") == ["hot"]

    def test_route_read_special_cases(self, router):
        assert router.route_read("data_analysis",
                                 priority=ContextPriority.CRITICAL) == ["hot"]
        assert router.route_read("data_analysis",
                                 context_type=ContextType.SYSTEM) == ["hot"]
        assert router.route_read("data_analysis",
                                 context_type=ContextType.TASK) == ["hot"]
        assert router.route_read("data_analysis", max_age_hours=12) == ["hot", "warm"]
        assert router.route_read("data_analysis", max_age_hours=48) == [
            "hot", "warm", "cold"]

    def test_route_write(self, router):
        assert router.route_write("code_generation") == "hot"
        assert router.route_write("dialogue") == "hot"
        assert router.route_write("unknown") == "hot"

    def test_should_archive(self, router):
        assert router.should_archive(100.0, "code_generation",
                                     priority=ContextPriority.CRITICAL) is False
        assert router.should_archive(10.0, "dialogue", access_count=3) is False
        assert router.should_archive(100.0, "code_generation") is True
        assert router.should_archive(100.0, "code_generation", access_count=5) is False
        assert router.should_archive(10.0, "code_generation") is False

    def test_compression_and_priority_types(self, router):
        assert router.get_compression_strategy("code_generation") == "selective"
        assert router.get_compression_strategy("data_analysis") == "summarize"
        assert router.get_compression_strategy("unknown") == "adaptive"
        assert router.get_priority_types("dialogue") == [
            ContextType.CONVERSATION, ContextType.SYSTEM, ContextType.BACKGROUND]
        assert router.get_priority_types("unknown") == []

    def test_optimize_search_order(self):
        rule = RoutingRule(search_tiers=["cold", "warm", "hot"])
        router = ContextRouter(enable_warm_tier=True, enable_cold_tier=True,
                               routing_rules={"custom": rule})
        assert router.optimize_search_order("show recent data", "custom") == [
            "hot", "cold", "warm"]
        assert router.optimize_search_order("events in the past", "custom") == [
            "warm", "hot", "cold"]
        assert router.optimize_search_order("plain query", "custom") == [
            "cold", "warm", "hot"]
