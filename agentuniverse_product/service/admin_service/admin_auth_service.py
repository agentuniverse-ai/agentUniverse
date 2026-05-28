# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

import os
from dataclasses import dataclass

from flask import request

ROLE_ORDER = {
    "viewer": 1,
    "developer": 2,
    "admin": 3,
    "super_admin": 4,
}


@dataclass(frozen=True)
class AdminAuthContext:
    """Authenticated admin caller context."""

    role: str
    auth_enabled: bool


class AdminAuthService:
    """Bearer token RBAC for admin APIs (opt-in via ADMIN_AUTH_ENABLED)."""

    @staticmethod
    def is_enabled() -> bool:
        flag = os.environ.get("ADMIN_AUTH_ENABLED", "0").strip().lower()
        return flag in {"1", "true", "yes", "on"}

    @staticmethod
    def _parse_tokens() -> dict[str, str]:
        raw = os.environ.get("ADMIN_API_TOKENS", "").strip()
        if raw:
            tokens: dict[str, str] = {}
            for part in raw.split(","):
                item = part.strip()
                if not item:
                    continue
                if ":" in item:
                    token, role = item.rsplit(":", 1)
                    tokens[token.strip()] = role.strip().lower()
                else:
                    tokens[item] = "admin"
            return tokens

        single = os.environ.get("ADMIN_API_TOKEN", "").strip()
        if single:
            return {single: "admin"}
        return {}

    @staticmethod
    def extract_bearer_token() -> str | None:
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None
        token = header[7:].strip()
        return token or None

    @staticmethod
    def authenticate() -> AdminAuthContext | None:
        if not AdminAuthService.is_enabled():
            return AdminAuthContext(role="super_admin", auth_enabled=False)

        token = AdminAuthService.extract_bearer_token()
        if not token:
            return None

        role = AdminAuthService._parse_tokens().get(token)
        if not role:
            return None
        return AdminAuthContext(role=role, auth_enabled=True)

    @staticmethod
    def role_allows(role: str, min_role: str) -> bool:
        return ROLE_ORDER.get(role, 0) >= ROLE_ORDER.get(min_role, 99)

    @staticmethod
    def required_role_for_request(method: str) -> str:
        if method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            return "admin"
        return "viewer"
