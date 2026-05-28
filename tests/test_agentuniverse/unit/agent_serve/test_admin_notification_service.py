from pathlib import Path
from unittest.mock import MagicMock, patch

from agentuniverse_product.service.admin_service.admin_notification_service import AdminNotificationService
from agentuniverse_product.service.admin_service.dto import AlertItemDTO


def test_load_config_from_yaml(tmp_path: Path):
    config_path = tmp_path / 'notification.yaml'
    config_path.write_text(
        """
webhook:
  enabled: true
  url: https://example.com/hook
email:
  enabled: true
  smtp_host: smtp.example.com
  smtp_port: 587
  username: demo
  password: secret
  from_addr: noreply@example.com
  to_addrs:
    - ops@example.com
  use_tls: true
""",
        encoding='utf-8',
    )

    with patch.dict('os.environ', {'ADMIN_NOTIFICATION_CONFIG_PATH': str(config_path)}, clear=False):
        config = AdminNotificationService.load_config()

    assert config.webhook.enabled is True
    assert config.webhook.url == 'https://example.com/hook'
    assert config.email.enabled is True
    assert config.email.smtp_host == 'smtp.example.com'
    assert config.email.to_addrs == ['ops@example.com']


def test_notify_sends_webhook_and_email():
    alerts = [AlertItemDTO(level='warning', message='check')]

    config = MagicMock()
    config.webhook.enabled = True
    config.webhook.url = 'https://example.com/hook'
    config.email.enabled = True
    config.email.smtp_host = 'smtp.example.com'
    config.email.smtp_port = 587
    config.email.username = 'demo'
    config.email.password = 'secret'
    config.email.from_addr = 'noreply@example.com'
    config.email.to_addrs = ['ops@example.com']
    config.email.use_tls = True

    with patch(
        'agentuniverse_product.service.admin_service.admin_notification_service.AdminNotificationService.load_config',
        return_value=config,
    ), patch(
        'agentuniverse_product.service.admin_service.admin_notification_service.AdminNotificationService._send_webhook'
    ) as mock_webhook, patch(
        'agentuniverse_product.service.admin_service.admin_notification_service.AdminNotificationService._send_email'
    ) as mock_email:
        AdminNotificationService.notify(alerts)

    mock_webhook.assert_called_once()
    mock_email.assert_called_once()
