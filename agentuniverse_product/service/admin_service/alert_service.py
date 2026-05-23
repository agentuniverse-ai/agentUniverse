# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from agentuniverse_product.service.admin_service.dto import AlertItemDTO, AlertsResponseDTO
from agentuniverse_product.service.admin_service.monitoring_service import AdminMonitoringService
from agentuniverse_product.service.admin_service.resource_service import AdminResourceService


class AdminAlertService:
    """Aggregate monitoring and resource alerts for admin dashboards."""

    @staticmethod
    def get_active_alerts() -> AlertsResponseDTO:
        alerts: list[AlertItemDTO] = []

        metrics = AdminMonitoringService.get_llm_metrics()
        alerts.extend(metrics.alerts)

        summary = AdminResourceService.get_dashboard_summary()
        if summary.system_health < 50:
            alerts.append(
                AlertItemDTO(
                    level="critical",
                    message="System health score is below 50 — no active agents detected.",
                )
            )
        elif summary.system_health < 80:
            alerts.append(
                AlertItemDTO(
                    level="warning",
                    message="System health score is degraded — review agent registration.",
                )
            )

        if summary.total_llms == 0:
            alerts.append(
                AlertItemDTO(
                    level="info",
                    message="No LLM components registered in ProductManager.",
                )
            )

        deduped: list[AlertItemDTO] = []
        seen: set[tuple[str, str]] = set()
        for alert in alerts:
            key = (alert.level, alert.message)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(alert)

        return AlertsResponseDTO(alerts=deduped, total=len(deduped))
