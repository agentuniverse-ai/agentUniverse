from unittest.mock import patch

from agentuniverse_product.service.admin_service.alert_service import AdminAlertService
from agentuniverse_product.service.admin_service.dto import AlertItemDTO, DashboardSummaryResponse


def test_get_active_alerts_merges_monitoring_and_health():
    metrics = type(
        "Metrics",
        (),
        {"alerts": [AlertItemDTO(level="warning", message="Spike detected")]},
    )()
    summary = DashboardSummaryResponse(
        total_agents=0,
        total_tools=1,
        total_knowledge=0,
        total_workflows=0,
        total_llms=0,
        total_memories=0,
        system_health=60.0,
    )

    with patch(
        "agentuniverse_product.service.admin_service.alert_service.AdminMonitoringService.get_llm_metrics",
        return_value=metrics,
    ), patch(
        "agentuniverse_product.service.admin_service.alert_service.AdminResourceService.get_dashboard_summary",
        return_value=summary,
    ), patch(
        "agentuniverse_product.service.admin_service.alert_service.AdminNotificationService.notify_async"
    ):
        response = AdminAlertService.get_active_alerts()

    assert response.total >= 2
    assert any(alert.level == "warning" for alert in response.alerts)


def test_get_active_alerts_deduplicates_messages():
    metrics = type(
        "Metrics",
        (),
        {
            "alerts": [
                AlertItemDTO(level="info", message="same"),
                AlertItemDTO(level="info", message="same"),
            ]
        },
    )()
    summary = DashboardSummaryResponse(
        total_agents=1,
        total_tools=0,
        total_knowledge=0,
        total_workflows=0,
        total_llms=1,
        system_health=100.0,
    )

    with patch(
        "agentuniverse_product.service.admin_service.alert_service.AdminMonitoringService.get_llm_metrics",
        return_value=metrics,
    ), patch(
        "agentuniverse_product.service.admin_service.alert_service.AdminResourceService.get_dashboard_summary",
        return_value=summary,
    ), patch(
        "agentuniverse_product.service.admin_service.alert_service.AdminNotificationService.notify_async"
    ):
        response = AdminAlertService.get_active_alerts()

    assert response.total == 1
