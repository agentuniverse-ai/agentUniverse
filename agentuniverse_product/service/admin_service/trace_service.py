# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from datetime import datetime

from agentuniverse_product.service.admin_service.dto import (
    TraceEdgeDTO,
    TraceNodeDTO,
    TraceResponseDTO,
)
from agentuniverse_product.service.admin_service.guardrail_service import AdminGuardrailService
from agentuniverse_product.service.admin_service.otel_span_reader import AdminOtelSpanReader
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
    def _nano_to_iso(nano: int | None) -> str:
        if nano is None:
            return ""
        try:
            return datetime.fromtimestamp(int(nano) / 1e9).strftime("%Y-%m-%d %H:%M:%S")
        except (TypeError, ValueError, OSError):
            return ""

    @staticmethod
    def _span_duration_ms(span: dict) -> float:
        try:
            start = int(span.get("start_unix_nano") or 0)
            end = int(span.get("end_unix_nano") or start)
            return max((end - start) / 1e6, 0.0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _span_display_name(span: dict) -> str:
        attributes = span.get("attributes") or {}
        kind = AdminOtelSpanReader.span_kind(span, "span")
        for key in ("au.llm.name", "au.agent.name", "au.tool.name"):
            if attributes.get(key):
                return str(attributes[key])
        name = span.get("name")
        if name:
            return str(name)
        return f"{kind}-{span.get('span_id', 'unknown')}"

    @staticmethod
    def _span_status(span: dict) -> str:
        attributes = span.get("attributes") or {}
        for key in ("au.llm.status", "au.agent.status", "au.tool.status"):
            status = attributes.get(key)
            if status:
                return "failed" if str(status).lower() == "error" else "success"
        span_status = str(span.get("status", "OK")).upper()
        return "failed" if span_status == "ERROR" else "success"

    @staticmethod
    def _build_from_otel_spans(session: SessionDTO, spans: list[dict]) -> TraceResponseDTO:
        nodes = [
            TraceNodeDTO(
                id=str(span.get("span_id")),
                name=AdminTraceService._span_display_name(span),
                type=AdminOtelSpanReader.span_kind(span, "span"),
                start_time=AdminTraceService._nano_to_iso(span.get("start_unix_nano")),
                end_time=AdminTraceService._nano_to_iso(span.get("end_unix_nano")),
                duration=AdminTraceService._span_duration_ms(span),
                status=AdminTraceService._span_status(span),
            )
            for span in spans
            if span.get("span_id")
        ]
        node_ids = {node.id for node in nodes}
        edges: list[TraceEdgeDTO] = []
        for span in spans:
            span_id = span.get("span_id")
            parent_id = span.get("parent_span_id")
            if span_id and parent_id and parent_id in node_ids and span_id in node_ids:
                edges.append(TraceEdgeDTO(source=str(parent_id), target=str(span_id), label="invoke"))

        return TraceResponseDTO(
            session_id=session.id,
            agent_id=session.agent_id,
            nodes=nodes,
            edges=edges,
            timeline=nodes,
            data_source="otel",
            diagnostics=AdminGuardrailService.analyze_session(session),
        )

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
            data_source="message",
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

        otel_spans = AdminOtelSpanReader.load_session_spans(session_id)
        if otel_spans:
            return AdminTraceService._build_from_otel_spans(session, otel_spans)

        return AdminTraceService._build_from_session(session)
