# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.admin_service.dto import (
    DashboardSummaryResponse,
    ResourceItemDTO,
    ResourceListResponse,
)
from agentuniverse_product.service.admin_service.monitoring_service import AdminMonitoringService
from agentuniverse_product.service.model.session_dto import SessionDTO
from agentuniverse_product.service.session_service.session_service import SessionService


class AdminResourceService:
    """Admin resource aggregation service for dashboard APIs."""

    @staticmethod
    def _list_by_product_type(product_type: str) -> ResourceListResponse:
        products: list[Product] = ProductManager().get_instance_obj_list()
        filtered = [p for p in products if p.type == product_type]
        data = [
            ResourceItemDTO(
                id=product.id,
                name=product.nickname or product.id,
                description=product.description or "",
                component_type=product_type,
            )
            for product in filtered
        ]
        return ResourceListResponse(total=len(data), data=data)

    @staticmethod
    def get_all_agents() -> ResourceListResponse:
        return AdminResourceService._list_by_product_type(ComponentEnum.AGENT.value)

    @staticmethod
    def get_all_tools() -> ResourceListResponse:
        return AdminResourceService._list_by_product_type(ComponentEnum.TOOL.value)

    @staticmethod
    def get_all_knowledge() -> ResourceListResponse:
        return AdminResourceService._list_by_product_type(ComponentEnum.KNOWLEDGE.value)

    @staticmethod
    def get_all_workflows() -> ResourceListResponse:
        return AdminResourceService._list_by_product_type(ComponentEnum.WORKFLOW.value)

    @staticmethod
    def get_agent_sessions(agent_id: str) -> ResourceListResponse:
        try:
            sessions: list[SessionDTO] = SessionService.get_session_list(agent_id)
        except ValueError:
            # In unit-test or uninitialized runtime, app config/db may not be ready yet.
            sessions = []
        data = [
            ResourceItemDTO(
                id=session.id,
                name=session.id,
                description=f"messages={len(session.messages or [])}",
                component_type="SESSION",
            )
            for session in sessions
        ]
        return ResourceListResponse(total=len(data), data=data)

    @staticmethod
    def _calculate_system_health(
        total_agents: int,
        total_tools: int,
        total_knowledge: int,
        total_workflows: int,
    ) -> str:
        total_resources = total_agents + total_tools + total_knowledge + total_workflows
        if total_agents > 0:
            return "OK"
        if total_resources > 0:
            return "WARNING"
        return "DEGRADED"

    @staticmethod
    def get_dashboard_summary() -> DashboardSummaryResponse:
        calls_today, tokens_today = AdminMonitoringService.get_today_usage()
        total_agents = AdminResourceService.get_all_agents().total
        total_tools = AdminResourceService.get_all_tools().total
        total_knowledge = AdminResourceService.get_all_knowledge().total
        total_workflows = AdminResourceService.get_all_workflows().total
        return DashboardSummaryResponse(
            total_agents=total_agents,
            total_tools=total_tools,
            total_knowledge=total_knowledge,
            total_workflows=total_workflows,
            total_llm_calls_today=calls_today,
            total_tokens_today=tokens_today,
            system_health=AdminResourceService._calculate_system_health(
                total_agents,
                total_tools,
                total_knowledge,
                total_workflows,
            ),
        )
