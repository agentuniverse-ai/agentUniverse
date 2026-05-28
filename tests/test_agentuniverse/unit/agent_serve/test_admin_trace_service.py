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
    assert trace.data_source == "message"


def test_get_session_trace_from_otel_spans():
    session = SessionDTO(
        id="session-1",
        agent_id="demo_agent",
        gmt_created="2026-04-01 10:00:00",
        gmt_modified="2026-04-01 10:05:00",
        messages=[],
    )
    otel_spans = [
        {
            "span_id": "agent001",
            "parent_span_id": None,
            "name": "au.agent.demo",
            "start_unix_nano": 1_000_000_000,
            "end_unix_nano": 2_000_000_000,
            "status": "OK",
            "attributes": {"au.span.kind": "agent", "au.agent.name": "demo_agent"},
        },
        {
            "span_id": "llm001",
            "parent_span_id": "agent001",
            "name": "au.llm.demo",
            "start_unix_nano": 2_000_000_000,
            "end_unix_nano": 3_000_000_000,
            "status": "OK",
            "attributes": {"au.span.kind": "llm", "au.llm.name": "demo_llm"},
        },
    ]

    with patch(
        "agentuniverse_product.service.admin_service.trace_service.SessionService.get_session_detail",
        return_value=session,
    ), patch(
        "agentuniverse_product.service.admin_service.trace_service.AdminOtelSpanReader.load_session_spans",
        return_value=otel_spans,
    ):
        trace = AdminTraceService.get_session_trace("session-1")

    assert trace.data_source == "otel"
    assert len(trace.nodes) == 2
    assert len(trace.edges) == 1
    assert trace.edges[0].source == "agent001"
    assert trace.edges[0].target == "llm001"


@pytest.mark.parametrize("session_id", ["", None])
def test_get_session_trace_requires_session_id(session_id):
    with pytest.raises(ValueError):
        AdminTraceService.get_session_trace(session_id)
