from unittest.mock import patch

import pytest

from agentuniverse_product.service.admin_service.guardrail_service import AdminGuardrailService
from agentuniverse_product.service.model.message_dto import MessageDTO
from agentuniverse_product.service.model.session_dto import SessionDTO


def test_analyze_session_empty_messages():
    session = SessionDTO(
        id="session-1",
        agent_id="demo_agent",
        gmt_created="2026-04-01 10:00:00",
        gmt_modified="2026-04-01 10:05:00",
        messages=[],
    )
    diagnostics = AdminGuardrailService.analyze_session(session)

    assert diagnostics.guardrail_enabled is True
    assert diagnostics.scores.safety_score >= 0
    assert diagnostics.warnings
    assert diagnostics.warnings[0].level == "info"


def test_analyze_session_detects_repeated_messages():
    session = SessionDTO(
        id="session-1",
        agent_id="demo_agent",
        gmt_created="2026-04-01 10:00:00",
        gmt_modified="2026-04-01 10:05:00",
        messages=[
            MessageDTO(
                id=1,
                session_id="session-1",
                content="same answer",
                gmt_created="2026-04-01 10:01:00",
                gmt_modified="2026-04-01 10:01:30",
            ),
            MessageDTO(
                id=2,
                session_id="session-1",
                content="same answer",
                gmt_created="2026-04-01 10:02:00",
                gmt_modified="2026-04-01 10:02:20",
            ),
        ],
    )
    diagnostics = AdminGuardrailService.analyze_session(session)

    assert any("Repeated message content" in warning.message for warning in diagnostics.warnings)
    assert diagnostics.risk_level in {"medium", "high"}


def test_get_session_diagnostics_not_found():
    with patch(
        "agentuniverse_product.service.admin_service.guardrail_service.SessionService.get_session_detail",
        return_value=None,
    ):
        diagnostics = AdminGuardrailService.get_session_diagnostics("missing")

    assert diagnostics.warnings[0].level == "info"


@pytest.mark.parametrize("session_id", ["", None])
def test_get_session_diagnostics_requires_session_id(session_id):
    with pytest.raises(ValueError):
        AdminGuardrailService.get_session_diagnostics(session_id)
