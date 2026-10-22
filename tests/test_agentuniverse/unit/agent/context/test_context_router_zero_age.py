#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse.agent.context.router.context_router import ContextRouter


def test_zero_max_age_excludes_cold_storage():
    router = ContextRouter(
        name="test_router",
        enable_warm_tier=True,
        enable_cold_tier=True,
    )

    assert router.route_read(
        task_type="data_analysis", max_age_hours=0
    ) == ["hot", "warm"]
