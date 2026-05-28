import pytest
from pydantic import ValidationError

from agentuniverse_product.service.admin_service.dto import (
    AlertItemDTO,
    AlertsResponseDTO,
    DashboardSummaryResponse,
    OptimizationResponseDTO,
    OptimizationSuggestionDTO,
)


def test_dashboard_summary_accepts_float_health():
    summary = DashboardSummaryResponse(
        total_agents=1,
        total_tools=0,
        total_knowledge=0,
        total_workflows=0,
        total_llms=2,
        total_memories=1,
        system_health=100.0,
    )
    assert summary.system_health == 100.0
    assert summary.total_llms == 2


def test_dashboard_summary_rejects_invalid_health():
    with pytest.raises(ValidationError):
        DashboardSummaryResponse(
            total_agents=0,
            total_tools=0,
            total_knowledge=0,
            total_workflows=0,
            system_health=150.0,
        )


def test_alerts_response_total_matches_items():
    payload = AlertsResponseDTO(
        alerts=[
            AlertItemDTO(level="info", message="ok"),
            AlertItemDTO(level="warning", message="check"),
        ],
        total=2,
    )
    assert payload.total == len(payload.alerts)


def test_optimization_response_shape():
    payload = OptimizationResponseDTO(
        session_id="session-1",
        suggestions=[
            OptimizationSuggestionDTO(
                category="performance",
                severity="warning",
                message="Long chain",
                action="Split workflow",
            )
        ],
    )
    assert payload.session_id == "session-1"
    assert payload.suggestions[0].category == "performance"
