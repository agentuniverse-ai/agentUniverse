from datetime import datetime
from unittest.mock import patch

from agentuniverse_product.service.admin_service.monitoring_service import AdminMonitoringService


def test_get_llm_metrics_empty_window():
    with patch.object(AdminMonitoringService, "_load_messages", return_value=[]):
        metrics = AdminMonitoringService.get_llm_metrics(
            start="2026-04-01",
            end="2026-04-03",
        )

    assert len(metrics.series) == 3
    assert metrics.total_calls == 0
    assert metrics.total_tokens == 0
    assert metrics.alerts
    assert metrics.alerts[0].level == "info"


def test_get_llm_metrics_groups_messages_by_day():
    messages = [
        (datetime(2026, 4, 1, 10, 0, 0), "hello world"),
        (datetime(2026, 4, 1, 11, 0, 0), "again"),
        (datetime(2026, 4, 2, 9, 0, 0), "token estimate"),
    ]

    with patch.object(AdminMonitoringService, "_load_messages", return_value=messages):
        metrics = AdminMonitoringService.get_llm_metrics(
            start="2026-04-01",
            end="2026-04-02",
        )

    assert metrics.total_calls == 3
    assert metrics.series[0].calls == 2
    assert metrics.series[1].calls == 1
    assert metrics.series[0].tokens > 0


def test_detect_alerts_for_spike():
    from agentuniverse_product.service.admin_service.dto import MetricPointDTO

    series = [
        MetricPointDTO(ts="2026-04-01", calls=2, tokens=100),
        MetricPointDTO(ts="2026-04-02", calls=2, tokens=120),
        MetricPointDTO(ts="2026-04-03", calls=10, tokens=800),
    ]
    alerts = AdminMonitoringService._detect_alerts(series)
    assert any(alert.level == "warning" for alert in alerts)


def test_get_today_usage():
    with patch.object(
        AdminMonitoringService,
        "_load_messages",
        return_value=[(datetime.now(), "abcd"), (datetime.now(), "efgh")],
    ), patch(
        "agentuniverse_product.service.admin_service.monitoring_service.AdminOtelSpanReader.is_enabled",
        return_value=False,
    ):
        calls, tokens = AdminMonitoringService.get_today_usage()

    assert calls == 2
    assert tokens == 2


def test_get_llm_metrics_uses_otel_when_available():
    otel_records = [(datetime(2026, 4, 1, 10, 0, 0), 256)]

    with patch(
        "agentuniverse_product.service.admin_service.monitoring_service.AdminOtelSpanReader.is_enabled",
        return_value=True,
    ), patch(
        "agentuniverse_product.service.admin_service.monitoring_service.AdminOtelSpanReader.load_llm_metrics",
        return_value=otel_records,
    ):
        metrics = AdminMonitoringService.get_llm_metrics(
            start="2026-04-01",
            end="2026-04-01",
        )

    assert metrics.data_source == "otel"
    assert metrics.total_calls == 1
    assert metrics.total_tokens == 256
