from unittest.mock import patch

from agentuniverse_product.service.admin_service.dto import (
    GuardrailDiagnosticsDTO,
    GuardrailScoreDTO,
    TraceNodeDTO,
    TraceResponseDTO,
)
from agentuniverse_product.service.admin_service.optimization_service import AdminOptimizationService


def test_analyze_session_detects_long_chain():
    trace = TraceResponseDTO(
        session_id="session-1",
        agent_id="demo",
        nodes=[TraceNodeDTO(id=f"n{i}", name=f"step{i}", type="llm") for i in range(10)],
    )

    with patch(
        "agentuniverse_product.service.admin_service.optimization_service.AdminTraceService.get_session_trace",
        return_value=trace,
    ):
        result = AdminOptimizationService.analyze_session("session-1")

    assert any(item.category == "performance" for item in result.suggestions)


def test_analyze_session_reports_healthy_when_no_issues():
    trace = TraceResponseDTO(
        session_id="session-2",
        agent_id="demo",
        nodes=[TraceNodeDTO(id="n1", name="step", type="agent", status="success", duration=100.0)],
        diagnostics=GuardrailDiagnosticsDTO(
            risk_level="low",
            scores=GuardrailScoreDTO(),
        ),
    )

    with patch(
        "agentuniverse_product.service.admin_service.optimization_service.AdminTraceService.get_session_trace",
        return_value=trace,
    ):
        result = AdminOptimizationService.analyze_session("session-2")

    assert any(item.category == "health" for item in result.suggestions)
