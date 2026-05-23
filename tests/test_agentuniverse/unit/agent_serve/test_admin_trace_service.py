from unittest.mock import patch

import pytest

from agentuniverse_product.service.admin_service.trace_service import AdminTraceService
from agentuniverse_product.service.model.message_dto import MessageDTO
from agentuniverse_product.service.model.session_dto import SessionDTO


def test_get_session_trace_not_found():
    with patch(
        "agentuniverse_product.service.admin_service.trace_service.SessionService.get_session_detail",
        return_value=None,
    ):
        trace = AdminTraceService.get_session_trace("missing-session")

    assert trace.session_id == "missing-session"
    assert trace.agent_id == ""
    assert trace.nodes == []
    assert trace.edges == []


def test_get_session_trace_from_messages():
    session = SessionDTO(
        id="session-1",
        agent_id="demo_agent",
        gmt_created="2026-04-01 10:00:00",
        gmt_modified="2026-04-01 10:05:00",
        messages=[
            MessageDTO(
                id=1,
                session_id="session-1",
                content="hello",
                gmt_created="2026-04-01 10:01:00",
                gmt_modified="2026-04-01 10:01:30",
            ),
            MessageDTO(
                id=2,
                session_id="session-1",
                content="world",
                gmt_created="2026-04-01 10:02:00",
                gmt_modified="2026-04-01 10:02:20",
            ),
        ],
    )

    with patch(
        "agentuniverse_product.service.admin_service.trace_service.SessionService.get_session_detail",
        return_value=session,
    ):
        trace = AdminTraceService.get_session_trace("session-1")

    assert trace.agent_id == "demo_agent"
    assert len(trace.nodes) == 3
    assert len(trace.edges) == 2
    assert trace.nodes[0].type == "agent"
    assert trace.nodes[1].type == "message"
    assert trace.nodes[2].type == "llm"
    assert trace.timeline[0].id == trace.nodes[0].id


@pytest.mark.parametrize("session_id", ["", None])
def test_get_session_trace_requires_session_id(session_id):
    with pytest.raises(ValueError):
        AdminTraceService.get_session_trace(session_id)
