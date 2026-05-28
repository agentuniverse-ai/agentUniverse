# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

import json
import os
import smtplib
import ssl
import threading
import urllib.request
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import yaml

from agentuniverse_product.service.admin_service.dto import AlertItemDTO


@dataclass
class WebhookNotificationConfig:
    enabled: bool = False
    url: str = ""


@dataclass
class EmailNotificationConfig:
    enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 25
    username: str = ""
    password: str = ""
    from_addr: str = ""
    to_addrs: list[str] = field(default_factory=list)
    use_tls: bool = True


@dataclass
class AdminNotificationConfig:
    webhook: WebhookNotificationConfig = field(default_factory=WebhookNotificationConfig)
    email: EmailNotificationConfig = field(default_factory=EmailNotificationConfig)


class AdminNotificationService:
    """Send admin alert notifications through optional webhook and email channels."""

    @staticmethod
    def _load_yaml_config(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as config_file:
            payload = yaml.safe_load(config_file) or {}
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _load_config_from_env() -> AdminNotificationConfig:
        webhook = WebhookNotificationConfig(
            enabled=os.getenv("ADMIN_NOTIFICATION_WEBHOOK_ENABLED", "false").lower() in {"1", "true", "yes"},
            url=os.getenv("ADMIN_NOTIFICATION_WEBHOOK_URL", ""),
        )
        email = EmailNotificationConfig(
            enabled=os.getenv("ADMIN_NOTIFICATION_EMAIL_ENABLED", "false").lower() in {"1", "true", "yes"},
            smtp_host=os.getenv("ADMIN_NOTIFICATION_SMTP_HOST", ""),
            smtp_port=int(os.getenv("ADMIN_NOTIFICATION_SMTP_PORT", "25")),
            username=os.getenv("ADMIN_NOTIFICATION_SMTP_USERNAME", ""),
            password=os.getenv("ADMIN_NOTIFICATION_SMTP_PASSWORD", ""),
            from_addr=os.getenv("ADMIN_NOTIFICATION_EMAIL_FROM", ""),
            to_addrs=[
                item.strip()
                for item in os.getenv("ADMIN_NOTIFICATION_EMAIL_TO", "").split(",")
                if item.strip()
            ],
            use_tls=os.getenv("ADMIN_NOTIFICATION_SMTP_TLS", "true").lower() in {"1", "true", "yes"},
        )
        return AdminNotificationConfig(webhook=webhook, email=email)

    @staticmethod
    def load_config() -> AdminNotificationConfig:
        config_path = os.getenv("ADMIN_NOTIFICATION_CONFIG_PATH", "").strip()
        config = AdminNotificationService._load_config_from_env()
        if not config_path:
            return config

        payload = AdminNotificationService._load_yaml_config(Path(config_path))
        webhook_payload = payload.get("webhook") if isinstance(payload.get("webhook"), dict) else {}
        email_payload = payload.get("email") if isinstance(payload.get("email"), dict) else {}

        if webhook_payload:
            config.webhook.enabled = bool(webhook_payload.get("enabled", config.webhook.enabled))
            config.webhook.url = str(webhook_payload.get("url", config.webhook.url))

        if email_payload:
            config.email.enabled = bool(email_payload.get("enabled", config.email.enabled))
            config.email.smtp_host = str(email_payload.get("smtp_host", config.email.smtp_host))
            config.email.smtp_port = int(email_payload.get("smtp_port", config.email.smtp_port))
            config.email.username = str(email_payload.get("username", config.email.username))
            config.email.password = str(email_payload.get("password", config.email.password))
            config.email.from_addr = str(email_payload.get("from_addr", config.email.from_addr))
            to_addrs = email_payload.get("to_addrs", config.email.to_addrs)
            if isinstance(to_addrs, list):
                config.email.to_addrs = [str(item) for item in to_addrs if str(item).strip()]
            elif isinstance(to_addrs, str):
                config.email.to_addrs = [item.strip() for item in to_addrs.split(",") if item.strip()]
            config.email.use_tls = bool(email_payload.get("use_tls", config.email.use_tls))

        return config

    @staticmethod
    def _send_webhook(url: str, payload: dict[str, Any]) -> None:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(request, timeout=10).read()

    @staticmethod
    def _send_email(config: EmailNotificationConfig, payload: dict[str, Any]) -> None:
        if not config.from_addr or not config.to_addrs or not config.smtp_host:
            return

        message = EmailMessage()
        message["From"] = config.from_addr
        message["To"] = ", ".join(config.to_addrs)
        message["Subject"] = "agentUniverse admin alert notification"
        message.set_content(json.dumps(payload, ensure_ascii=False, indent=2))

        with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=10) as client:
            if config.use_tls:
                client.starttls(context=ssl.create_default_context())
            if config.username:
                client.login(config.username, config.password)
            client.send_message(message)

    @staticmethod
    def notify(alerts: list[AlertItemDTO]) -> None:
        if not alerts:
            return

        config = AdminNotificationService.load_config()
        payload = {"alerts": [alert.model_dump() for alert in alerts]}

        if config.webhook.enabled and config.webhook.url:
            AdminNotificationService._send_webhook(config.webhook.url, payload)

        if config.email.enabled:
            AdminNotificationService._send_email(config.email, payload)

    @staticmethod
    def notify_async(alerts: list[AlertItemDTO]) -> None:
        if not alerts:
            return

        thread = threading.Thread(target=AdminNotificationService.notify, args=(alerts,), daemon=True)
        thread.start()
