# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse_product.service.admin_service.dto import OptimizationResponseDTO, OptimizationSuggestionDTO
from agentuniverse_product.service.admin_service.trace_service import AdminTraceService


class AdminOptimizationService:
    """Rule-driven optimization suggestions from session traces."""

    LONG_CHAIN_THRESHOLD = 8
    SLOW_STEP_MS = 5000.0

    @staticmethod
    def analyze_session(session_id: str) -> OptimizationResponseDTO:
        trace = AdminTraceService.get_session_trace(session_id)
        suggestions: list[OptimizationSuggestionDTO] = []

        if len(trace.nodes) > AdminOptimizationService.LONG_CHAIN_THRESHOLD:
            suggestions.append(
                OptimizationSuggestionDTO(
                    category="performance",
                    severity="warning",
                    message=f"Execution chain has {len(trace.nodes)} steps — consider splitting the agent workflow.",
                    action="Refactor into smaller sub-agents or cache intermediate results.",
                )
            )

        slow_nodes = [node for node in trace.nodes if node.duration >= AdminOptimizationService.SLOW_STEP_MS]
        if slow_nodes:
            suggestions.append(
                OptimizationSuggestionDTO(
                    category="latency",
                    severity="warning",
                    message=f"{len(slow_nodes)} step(s) exceed {AdminOptimizationService.SLOW_STEP_MS:.0f} ms.",
                    action="Inspect slow LLM/tool nodes and enable streaming or shorter prompts.",
                )
            )

        failed_nodes = [node for node in trace.nodes if node.status == "failed"]
        if failed_nodes:
            suggestions.append(
                OptimizationSuggestionDTO(
                    category="reliability",
                    severity="critical",
                    message=f"{len(failed_nodes)} node(s) failed in this session.",
                    action="Review error details and add guardrails or retries on failing tools.",
                )
            )

        if trace.diagnostics and trace.diagnostics.risk_level in {"medium", "high"}:
            suggestions.append(
                OptimizationSuggestionDTO(
                    category="guardrail",
                    severity="warning",
                    message=f"Guardrail risk level is {trace.diagnostics.risk_level}.",
                    action="Review LPP radar warnings and tighten prompt or tool policies.",
                )
            )

        if not suggestions:
            suggestions.append(
                OptimizationSuggestionDTO(
                    category="health",
                    severity="info",
                    message="No optimization issues detected for this session.",
                    action="Continue monitoring token usage and latency trends.",
                )
            )

        return OptimizationResponseDTO(session_id=session_id, suggestions=suggestions)
