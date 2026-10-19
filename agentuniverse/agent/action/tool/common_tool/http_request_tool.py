#!/usr/bin/env python3
"""Bounded HTTP request tool.

Provides a general-purpose HTTP client tool (GET/POST/PUT/DELETE) with
configurable timeout, response size limit, and SSRF redirect opt-in.
Unlike APITool (which requires an OpenAPI spec), this tool accepts a URL
and method directly — useful for ad-hoc API calls, webhooks, and simple
data fetching.

Follows the same bounded contract as APITool (#701): redirects are opt-in
and bounded, response body is size-limited, and all requests carry a
timeout.
"""

# ruff: noqa: TRY003, TRY004

import json
import logging
from typing import Any, Optional

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.utils import ssrf_proxy
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

_ALLOWED_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"}


class HttpRequestTool(Tool):
    """Bounded HTTP request tool with SSRF-safe defaults.

    Attributes:
        default_timeout: Request timeout in seconds (default 30).
        max_response_bytes: Maximum response body size in bytes (default 1 MB).
        allow_redirects: Whether to follow redirects (default False — opt-in,
            same contract as APITool #701).
        max_redirects: Maximum redirect chain length when redirects are on.
        default_headers: Default headers applied to every request.
    """

    default_timeout: float = 30.0
    max_response_bytes: int = 1024 * 1024  # 1 MB
    allow_redirects: bool = False
    max_redirects: int = 5
    default_headers: Optional[dict] = None

    def execute(self, url: str, method: str = "GET",
                headers: Optional[dict] = None,
                params: Optional[dict] = None,
                body: Optional[Any] = None,
                **kwargs) -> dict:
        try:
            self._validate(url, method)
            resolved_headers = dict(self.default_headers or {})
            if headers:
                resolved_headers.update(headers)

            req_timeout = kwargs.get("timeout", self.default_timeout)

            # Build body for non-GET.
            data = None
            if body is not None and method.upper() not in ("GET", "HEAD"):
                if isinstance(body, (dict, list)):
                    data = json.dumps(body)
                    resolved_headers.setdefault("Content-Type", "application/json")
                elif isinstance(body, str):
                    data = body
                else:
                    data = str(body)

            http_method = method.lower()
            response = getattr(ssrf_proxy, http_method)(
                url,
                params=params,
                headers=resolved_headers,
                data=data,
                timeout=req_timeout,
                follow_redirects=self.allow_redirects,
                max_redirects=self.max_redirects if self.allow_redirects else 0,
            )

            # Bound the response body.
            text = response.text or ""
            truncated = False
            if len(text.encode("utf-8", errors="replace")) > self.max_response_bytes:
                text = text[:self.max_response_bytes] + "\n…[truncated]"
                truncated = True

            return {
                "status": "success",
                "status_code": response.status_code,
                "headers": dict(response.headers) if hasattr(response, "headers") else {},
                "body": text,
                "truncated": truncated,
                "url": str(response.url) if hasattr(response, "url") else url,
            }
        except ValueError as exc:
            return self._error("validation_error", str(exc))
        except Exception as exc:
            return self._error("request_error", f"HTTP request failed: {exc}")

    def _validate(self, url: str, method: str) -> None:
        if not isinstance(url, str) or not url.strip():
            raise ValueError("url must be a non-empty string")
        if not url.lower().startswith(("http://", "https://")):
            raise ValueError("url must start with http:// or https://")
        upper = method.upper()
        if upper not in _ALLOWED_METHODS:
            raise ValueError(
                f"method must be one of: {', '.join(sorted(_ALLOWED_METHODS))}")

    def _initialize_by_component_configer(self, configer: ComponentConfiger) -> "HttpRequestTool":
        super()._initialize_by_component_configer(configer)
        if hasattr(configer, "default_timeout"):
            self.default_timeout = configer.default_timeout
        if hasattr(configer, "max_response_bytes"):
            self.max_response_bytes = configer.max_response_bytes
        if hasattr(configer, "allow_redirects"):
            self.allow_redirects = configer.allow_redirects
        if hasattr(configer, "max_redirects"):
            self.max_redirects = configer.max_redirects
        if hasattr(configer, "default_headers"):
            self.default_headers = configer.default_headers
        return self

    @staticmethod
    def _error(error_type: str, message: str) -> dict:
        return {"status": "error", "error_type": error_type, "error": message}
