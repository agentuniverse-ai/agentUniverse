#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: ip_geo_tool.py

"""IP geolocation tool backed by the keyless ipapi.co API.

Resolves the city, region, country, network operator, and timezone of an
IP address, addressing the *other tools* item of issue #252 (tool
plug-in integration).

The tool talks to the public ``https://ipapi.co`` JSON API over
``httpx`` — already a core agentUniverse dependency — so no API key, no
account, and no extra install is required. It supports two operating
modes:

* ``lookup`` — geolocate one specific public IPv4 or IPv6 address via
  ``/{ip}/json/``. The address is parsed with the stdlib ``ipaddress``
  module *before* any request is made; private, loopback, link-local,
  multicast, reserved, and other non-routable ranges are rejected
  upfront with a structured ``reserved_ip`` payload and never sent to
  the API.
* ``self`` — geolocate the caller's own address via ``/json/`` (the
  API infers it from the request).

An optional ``reverse`` flag asks the parser to keep the ``hostname``
field of the response (reverse DNS), which ipapi.co returns when the
looked-up address has a PTR record.

Every request goes to a fixed https-only ``ipapi.co`` endpoint built
from an ``ipaddress``-validated address (the URL path can therefore
only contain digits, dots, colons, and hex letters). Timeout,
connection, HTTP, and malformed response failures — including
ipapi.co's HTTP-200 ``{"error": true, ...}`` bodies — are returned as
a structured ``error`` payload instead of raising.
"""

import ipaddress
from typing import Any, ClassVar, Dict, Optional

import httpx
from pydantic import ConfigDict, Field

from agentuniverse.agent.action.tool.tool import Tool

_SOURCE = "ipapi.co IP Geolocation API (https://ipapi.co/api/)"


class IPGeoTool(Tool):
    """IP geolocation tool backed by the keyless ipapi.co API.

    Attributes:
        timeout (float): HTTP request timeout in seconds.
        transport (Optional[httpx.BaseTransport]): Injectable httpx
            transport; used by tests to run fully offline. Production use
            leaves it unset (the default httpx transport is used).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "ip_geo_tool"
    description: str = (
        "IP geolocation tool (ipapi.co) — no API key required. Resolves "
        "the city, region, country, network operator, and timezone of a "
        "specific public IPv4/IPv6 address (mode='lookup') or of the "
        "caller's own IP (mode='self'); optionally keeps the reverse "
        "DNS hostname (reverse=True)."
    )

    # Fixed, https-only endpoints; requests never go anywhere else.
    LOOKUP_URL_TEMPLATE: ClassVar[str] = "https://ipapi.co/{ip}/json/"
    SELF_URL: ClassVar[str] = "https://ipapi.co/json/"
    SOURCE: ClassVar[str] = _SOURCE

    MODES: ClassVar[tuple] = ("lookup", "self")
    # The response is trimmed to these fields (plus the reported ip and,
    # on request, the hostname) — ipapi.co returns ~25 more.
    USEFUL_FIELDS: ClassVar[tuple] = (
        "city",
        "region",
        "country_name",
        "org",
        "asn",
        "timezone",
    )
    MAX_FIELD_CHARS: ClassVar[int] = 300
    MAX_ERROR_CHARS: ClassVar[int] = 500

    timeout: float = Field(
        default=10.0, gt=0, le=120, description="HTTP request timeout in seconds"
    )
    transport: Optional[httpx.BaseTransport] = Field(
        default=None,
        exclude=True,
        repr=False,
        description="Injectable httpx transport for offline testing.",
    )

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        ip: Any = None,
        reverse: bool = False,
    ) -> Dict[str, Any]:
        """Run one ipapi.co geolocation query.

        Args:
            mode (str): One of ``lookup`` / ``self``.
            ip (str | int): ``lookup`` mode only — the IPv4 or IPv6
                address to geolocate, as a string or an integer
                (``ipaddress`` semantics). Private, reserved, and other
                non-routable addresses are rejected before any request.
            reverse (bool): Keep the ``hostname`` (reverse DNS) field of
                the response when the API provides one. Default False.

        Returns:
            Dict[str, Any]: Trimmed geolocation result (``ip``, ``city``,
                ``region``, ``country_name``, ``org``, ``asn``,
                ``timezone``, and ``source``); or a structured ``error``
                payload on non-routable addresses and network / HTTP /
                response failures.

        Raises:
            ValueError: If any input is invalid (raised before any network
                request is made).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        wants_hostname = self._validate_reverse(reverse)

        if mode == "lookup":
            address = self._normalize_ip(ip)
            scope = self._non_routable_scope(address)
            if scope is not None:
                return self._error_result(
                    {"mode": "lookup", "ip": str(address)},
                    error_type="reserved_ip",
                    message=(
                        f"{address} is a {scope} address; IPGeoTool only "
                        "looks up public, globally-routable IP addresses."
                    ),
                    reason=scope,
                )
            context: Dict[str, Any] = {"mode": "lookup", "ip": str(address)}
            request_url = self._https_only(
                self.LOOKUP_URL_TEMPLATE.format(ip=str(address))
            )
        else:
            context = {"mode": "self"}
            request_url = self._https_only(self.SELF_URL)

        try:
            data = self._request_json(request_url)
            return self._parse_geo(data, context, wants_hostname)
        except httpx.TimeoutException:
            return self._error_result(
                context,
                error_type="request_timeout",
                message="ipapi.co request timed out.",
            )
        except httpx.HTTPStatusError as exc:
            return self._http_error_result(context, exc.response)
        except httpx.RequestError:
            return self._error_result(
                context,
                error_type="request_error",
                message="ipapi.co request failed.",
            )
        except ValueError as exc:
            return self._error_result(
                context,
                error_type="invalid_response",
                message=f"Unable to parse ipapi.co response: {exc}",
            )

    # ------------------------------------------------------------------ #
    # Input validation (pure — runs strictly before any request)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"ip_geo_tool: {message}")

    @classmethod
    def _validate_reverse(cls, reverse: Any) -> bool:
        """Validate the ``reverse`` (hostname) flag."""
        if not isinstance(reverse, bool):
            cls._invalid(f"reverse must be a boolean (got {reverse!r})")
        return reverse

    @classmethod
    def _normalize_ip(cls, ip: Any) -> Any:
        """Validate a ``lookup`` mode address with the stdlib ipaddress module.

        Accepts an IPv4/IPv6 string (surrounding whitespace is stripped;
        anything the strict ``ipaddress`` parser refuses — dotted quads
        with missing or out-of-range octets, prefixes, ports, URLs,
        leading-zero octets — is rejected) or a non-negative integer
        (``ipaddress`` semantics: values up to 2**32-1 are IPv4, larger
        ones IPv6). Returns the parsed address object; the caller uses
        its canonical compressed text for the URL path.
        """
        if ip is None or isinstance(ip, bool) or not isinstance(ip, (str, int)):
            cls._invalid(
                "ip is required in lookup mode and must be an IPv4 or "
                "IPv6 address given as a string or an integer "
                f"(got {ip!r})"
            )
        normalized = ip.strip() if isinstance(ip, str) else ip
        if isinstance(normalized, str) and not normalized:
            cls._invalid("ip is required in lookup mode and must be a non-empty string")
        try:
            return ipaddress.ip_address(normalized)
        except ValueError:
            cls._invalid(f"ip is not a valid IPv4 or IPv6 address (got {ip!r})")
            raise AssertionError("unreachable")  # pragma: no cover

    @classmethod
    def _non_routable_scope(cls, address: Any) -> Optional[str]:
        """Classify a parsed address as non-routable, if it is one.

        Returns a short scope label (``loopback``, ``link_local``,
        ``multicast``, ``unspecified``, ``reserved``, ``private``,
        ``non_global``) for addresses ipapi.co cannot geolocate, or
        ``None`` for a public, globally-routable address.
        """
        if address.is_loopback:
            return "loopback"
        if address.is_link_local:
            return "link_local"
        if address.is_multicast:
            return "multicast"
        if address.is_unspecified:
            return "unspecified"
        if address.is_reserved:
            return "reserved"
        if address.is_private:
            return "private"
        if not address.is_global:
            return "non_global"
        return None

    # ------------------------------------------------------------------ #
    # HTTP (single request per execution, https-only fixed endpoints)
    # ------------------------------------------------------------------ #

    @classmethod
    def _https_only(cls, url: str) -> str:
        """Refuse any endpoint that is not an https ipapi.co URL."""
        if not url.startswith("https://"):
            cls._invalid(f"refusing non-https endpoint: {url!r}")
        return url

    def _request_json(self, url: str) -> Dict[str, Any]:
        """Issue one GET request to ipapi.co and return its JSON."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "agentUniverse-IPGeoTool/1.0 "
            "(https://github.com/agentuniverse-ai/agentUniverse)",
        }
        with httpx.Client(
            timeout=self.timeout,
            transport=self.transport,
            headers=headers,
        ) as client:
            response = client.get(url)
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            raise ValueError("response body is not valid JSON") from None
        if not isinstance(data, dict):
            raise ValueError("expected a JSON object")
        return data

    # ------------------------------------------------------------------ #
    # Response parsing (pure — fully testable without a network)
    # ------------------------------------------------------------------ #

    def _parse_geo(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any],
        wants_hostname: bool,
    ) -> Dict[str, Any]:
        """Trim an ipapi.co lookup response to its useful fields."""
        # ipapi.co reports some lookup failures inside HTTP 200 bodies,
        # e.g. {"error": true, "reason": "Invalid IP Address", ...}.
        if data.get("error"):
            reason = self._safe_str(data.get("reason"))
            detail = self._safe_str(data.get("message")) or reason
            message = (
                f"ipapi.co rejected the lookup: {detail}"
                if detail
                else "ipapi.co rejected the lookup."
            )
            return self._error_result(
                context,
                error_type="api_error",
                message=message,
                reason=reason or None,
            )

        reported_ip = self._safe_str(data.get("ip")) or context.get("ip", "")
        if not reported_ip:
            return self._error_result(
                context,
                error_type="invalid_response",
                message="invalid ipapi.co response: missing 'ip' field",
            )

        result: Dict[str, Any] = {**context, "ip": reported_ip}
        for field in self.USEFUL_FIELDS:
            result[field] = self._bound_text(data.get(field), self.MAX_FIELD_CHARS)
        if wants_hostname:
            result["hostname"] = self._bound_text(
                data.get("hostname"), self.MAX_FIELD_CHARS
            )
        result["source"] = self.SOURCE
        return result

    # ------------------------------------------------------------------ #
    # Error payloads (structured, no secrets involved — the API is keyless)
    # ------------------------------------------------------------------ #

    def _error_result(
        self,
        context: Dict[str, Any],
        error_type: str,
        message: str,
        status_code: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        error: Dict[str, Any] = {
            "type": error_type,
            "message": str(message)[: self.MAX_ERROR_CHARS],
        }
        if status_code is not None:
            error["status_code"] = status_code
        if reason:
            error["reason"] = str(reason)[: self.MAX_ERROR_CHARS]
        return {**context, "error": error, "source": self.SOURCE}

    def _http_error_result(
        self, context: Dict[str, Any], response: httpx.Response
    ) -> Dict[str, Any]:
        """Turn a non-2xx response into a structured error."""
        message = f"ipapi.co returned HTTP {response.status_code}."
        reason = None
        try:
            body = response.json()
        except ValueError:
            body = None
        if isinstance(body, dict):
            api_reason = body.get("reason")
            if isinstance(api_reason, str) and api_reason:
                reason = api_reason
                detail = self._safe_str(body.get("message"))
                message = (
                    f"ipapi.co returned HTTP {response.status_code}: "
                    f"{detail or api_reason}"
                )
        return self._error_result(
            context,
            error_type="http_error",
            message=message,
            status_code=response.status_code,
            reason=reason,
        )

    # ------------------------------------------------------------------ #
    # Small helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _safe_str(value: Any) -> str:
        """Coerce an API response scalar to a clean string."""
        return value.strip() if isinstance(value, str) else ""

    @classmethod
    def _bound_text(cls, value: Any, limit: int) -> str:
        """Bound a free-text API field to ``limit`` characters."""
        text = cls._safe_str(value)
        return text if len(text) <= limit else text[:limit].rstrip() + "…"
