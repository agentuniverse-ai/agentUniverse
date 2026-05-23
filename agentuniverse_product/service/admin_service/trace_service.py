# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from datetime import datetime

from agentuniverse_product.service.admin_service.dto import (
    TraceEdgeDTO,
    TraceNodeDTO,
    TraceResponseDTO,
)
from agentuniverse_product.service.admin_service.guardrail_service import AdminGuardrailService
from agentuniverse_product.service.model.message_dto import MessageDTO
from agentuniverse_product.service.model.session_dto import SessionDTO
from agentuniverse_product.service.session_service.session_service import SessionService


class AdminTraceService:
    """Build session-level trace graphs from persisted session messages."""

    @staticmethod
    def _parse_timestamp(value: str | None) -> datetime | None:
        if not value:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def _duration_ms(start: str | None, end: str | None) -> float:
        start_dt = AdminTraceService._parse_timestamp(start)
        end_dt = AdminTraceService._parse_timestamp(end)
        if not start_dt or not end_dt:
            return 0.0
        return max((end_dt - start_dt).total_seconds() * 1000, 0.0)

    @staticmethod
    def _message_preview(message: MessageDTO) -> str:
        content = (message.content or "").strip().replace("\n", " ")
        if not content:
            return "empty message"
        return content[:48] + ("..." if len(content) > 48 else "")

    @staticmethod
    def _message_node_type(index: int) -> str:
        return "llm" if index % 2 else "message"

    @staticmethod
    def _build_from_session(session: SessionDTO) -> TraceResponseDTO:
        agent_node = TraceNodeDTO(
            id=f"agent-{session.agent_id}",
            name=session.agent_id,
            type="agent",
            start_time=session.gmt_created or "",
            end_time=session.gmt_modified or session.gmt_created or "",
            duration=AdminTraceService._duration_ms(session.gmt_created, session.gmt_modified),
            status="success",
        )
        nodes = [agent_node]
        timeline = [agent_node]
        edges: list[TraceEdgeDTO] = []
        prev_id = agent_node.id

        messages = session.messages or []
        for index, message in enumerate(messages):
            node_id = f"message-{message.id}"
            node = TraceNodeDTO(
                id=node_id,
                name=f"Step {index + 1}: {AdminTraceService._message_preview(message)}",
                type=AdminTraceService._message_node_type(index),
                start_time=message.gmt_created or "",
                end_time=message.gmt_modified or message.gmt_created or "",
                duration=AdminTraceService._duration_ms(message.gmt_created, message.gmt_modified),
                status="success",
            )
            nodes.append(node)
            timeline.append(node)
            edges.append(TraceEdgeDTO(source=prev_id, target=node_id, label="invoke"))
            prev_id = node_id

        return TraceResponseDTO(
            session_id=session.id,
            agent_id=session.agent_id,
            nodes=nodes,
            edges=edges,
            timeline=timeline,
            diagnostics=AdminGuardrailService.analyze_session(session),
        )

    @staticmethod
    def get_session_trace(session_id: str) -> TraceResponseDTO:
        if not session_id:
            raise ValueError("session_id is required parameter.")

        try:
            session = SessionService.get_session_detail(session_id)
        except ValueError:
            session = None

        if session is None:
            return TraceResponseDTO(
                session_id=session_id,
                agent_id="",
                nodes=[],
                edges=[],
                timeline=[],
            )

        return AdminTraceService._build_from_session(session)
