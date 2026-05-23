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
    total_llm_calls_today: int = 0
    total_tokens_today: int = 0


class MetricPointDTO(BaseModel):
    """Single LLM metrics data point."""

    ts: str = Field(..., description="Bucket timestamp, usually YYYY-MM-DD.")
    calls: int = Field(default=0, description="LLM call count in bucket.")
    tokens: int = Field(default=0, description="Token usage in bucket.")


class AlertItemDTO(BaseModel):
    """Simple monitoring alert item."""

    level: str = Field(..., description="Alert level: info/warning/critical.")
    message: str = Field(..., description="Human readable alert message.")


class LlmMetricsResponseDTO(BaseModel):
    """LLM monitoring metrics payload."""

    series: list[MetricPointDTO] = Field(default_factory=list)
    total_calls: int = Field(default=0)
    total_tokens: int = Field(default=0)
    alerts: list[AlertItemDTO] = Field(default_factory=list)
    data_source: str = Field(
        default="message_estimate",
        description="Metrics origin: otel or message_estimate.",
    )


class TraceNodeDTO(BaseModel):
    """Trace graph node for session execution topology."""

    id: str = Field(..., description="Node unique identifier.")
    name: str = Field(..., description="Node display name.")
    type: str = Field(..., description="Node type: agent/llm/message/tool/etc.")
    start_time: str = Field(default="", description="Node start timestamp.")
    end_time: str = Field(default="", description="Node end timestamp.")
    duration: float = Field(default=0.0, description="Duration in milliseconds.")
    status: str = Field(default="success", description="Node status: success/failed/running.")
    error: str | None = Field(default=None, description="Error message when failed.")


class TraceEdgeDTO(BaseModel):
    """Trace graph edge between two nodes."""

    source: str = Field(..., description="Source node id.")
    target: str = Field(..., description="Target node id.")
    label: str | None = Field(default=None, description="Optional edge label.")


class TraceResponseDTO(BaseModel):
    """Trace payload for a single session."""

    session_id: str = Field(..., description="Session identifier.")
    agent_id: str = Field(default="", description="Owning agent identifier.")
    nodes: list[TraceNodeDTO] = Field(default_factory=list, description="Graph nodes.")
    edges: list[TraceEdgeDTO] = Field(default_factory=list, description="Graph edges.")
    timeline: list[TraceNodeDTO] = Field(default_factory=list, description="Ordered execution steps.")
    data_source: str = Field(
        default="message",
        description="Trace origin: otel or message.",
    )
    diagnostics: "GuardrailDiagnosticsDTO | None" = Field(
        default=None,
        description="Session-level guardrail diagnostics for LPP radar rendering.",
    )


class GuardrailScoreDTO(BaseModel):
    """Normalized guardrail score dimensions (0-100)."""

    logic_consistency: float = Field(default=0.0, ge=0.0, le=100.0)
    info_entropy: float = Field(default=0.0, ge=0.0, le=100.0)
    diversity_ttr: float = Field(default=0.0, ge=0.0, le=100.0)
    lpp_feature: float = Field(default=0.0, ge=0.0, le=100.0)
    safety_score: float = Field(default=0.0, ge=0.0, le=100.0)


class GuardrailDiagnosticsDTO(BaseModel):
    """Guardrail diagnostics payload for admin dashboards."""

    guardrail_enabled: bool = Field(default=True)
    risk_level: str = Field(default="low", description="Risk level: low/medium/high.")
    scores: GuardrailScoreDTO = Field(default_factory=GuardrailScoreDTO)
    warnings: list[AlertItemDTO] = Field(default_factory=list)
