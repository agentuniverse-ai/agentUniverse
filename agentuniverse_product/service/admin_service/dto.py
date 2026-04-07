# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import Any

from pydantic import BaseModel, Field


class ResourceItemDTO(BaseModel):
    """Unified resource item for dashboard lists."""

    id: str = Field(..., description="Resource unique identifier.")
    name: str = Field(..., description="Resource display name.")
    description: str = Field(default="", description="Resource description.")
    component_type: str = Field(
        ...,
        description="Resource type enum: AGENT/TOOL/KNOWLEDGE/WORKFLOW/SESSION/MESSAGE.",
    )
    status: str = Field(default="ACTIVE", description="Runtime status.")
    diagnostics: dict[str, Any] | None = Field(
        default=None,
        description="Reserved diagnostics fields for future guardrail integration.",
    )


class ResourceListResponse(BaseModel):
    """Generic list response for resource dashboard."""

    total: int = Field(..., description="Total number of records.")
    data: list[ResourceItemDTO] = Field(..., description="Resource list.")


class DashboardSummaryResponse(BaseModel):
    """Summary data for dashboard cards."""

    total_agents: int
    total_tools: int
    total_knowledge: int
    total_workflows: int
    system_health: str = "OK"
