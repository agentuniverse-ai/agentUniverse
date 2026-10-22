# !/usr/bin/env python3

# @Time    : 2026/10/07
# @Author  : Robert Tidball
# @FileName: fxmacrodata_tool.py

"""
FXMacroData macroeconomic and FX data tool.

Looks up official central-bank and statistics-office data for 22 currencies
through the FXMacroData REST API, addressing the finance-data side of issue
#252 (tool plug-in integration). Four modes are supported:

* ``history``   - release history of one indicator (CPI, policy rate, payrolls,
  GDP...) with the value, previous value, reference period and publication
  time of each release.
* ``calendar``  - upcoming scheduled releases for a currency.
* ``catalogue`` - the indicators published for a currency.
* ``fx``        - daily FX rates for a currency pair.

USD releases from the last 90 days (15-minute delay), the USD calendar and
every currency's catalogue answer without an API key. Other currencies, full
history and FX rates need ``FXMACRODATA_API_KEY``.

The tool only uses ``requests``, which is already a core dependency. Results
are plain dicts with a ``status`` field, so errors reach the agent as data
instead of exceptions.
"""

import re
from collections.abc import Callable
from datetime import date
from typing import Any
from urllib.parse import urlsplit

import requests
from pydantic import Field, SecretStr, field_validator

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env

_CURRENCY = re.compile(r"^[A-Za-z]{3}$")
_SLUG = re.compile(r"^[a-z0-9_]{1,64}$")
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MAX_LIMIT = 100
_STATUS_DETAILS = {
    400: "the request was invalid",
    401: "an API key is required for this request, or the key was rejected",
    403: "the API key does not cover this request",
    404: "the currency or indicator was not found",
    422: "the request parameters were rejected",
    429: "the rate limit was exceeded",
}


class FXMacroDataError(Exception):
    """A credential-safe error raised inside the tool."""


def _env_key() -> SecretStr | None:
    value = (get_from_env("FXMACRODATA_API_KEY") or "").strip()
    return SecretStr(value) if value else None


def _currency(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _CURRENCY.fullmatch(value.strip()):
        raise FXMacroDataError(f"'{field}' must be a three-letter currency code such as USD.")
    return value.strip().lower()


def _slug(value: Any) -> str:
    text = value.strip().lower() if isinstance(value, str) else ""
    if not _SLUG.fullmatch(text):
        raise FXMacroDataError(
            "'indicator' must be a slug such as 'inflation' or 'policy_rate'; use mode 'catalogue' to list them."
        )
    return text


def _iso_date(value: Any, field: str) -> date | None:
    if value is None:
        return None
    text = value.strip() if isinstance(value, str) else ""
    if not _ISO_DATE.fullmatch(text):
        raise FXMacroDataError(f"'{field}' must be a date in YYYY-MM-DD form.")
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise FXMacroDataError(f"'{field}' is not a real calendar date.") from None


def _limit(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= _MAX_LIMIT:
        raise FXMacroDataError(f"'limit' must be an integer from 1 to {_MAX_LIMIT}.")
    return value


def _date_window(start_date: Any, end_date: Any) -> dict[str, str]:
    start = _iso_date(start_date, "start_date")
    end = _iso_date(end_date, "end_date")
    if start and end and start > end:
        raise FXMacroDataError("'start_date' must be on or before 'end_date'.")
    window = {}
    if start:
        window["start_date"] = start.isoformat()
    if end:
        window["end_date"] = end.isoformat()
    return window


def _rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise FXMacroDataError("FXMacroData returned no data list.")
    return [row for row in rows if isinstance(row, dict)]


def _has_more(payload: dict[str, Any]) -> bool | None:
    """Return pagination.has_more, rejecting a present but malformed object."""
    if "pagination" not in payload:
        return None
    page = payload["pagination"]
    if not isinstance(page, dict) or not isinstance(page.get("has_more"), bool):
        raise FXMacroDataError("FXMacroData returned malformed pagination.")
    return page["has_more"]


def _notices(payload: dict[str, Any]) -> list[str]:
    """Keyless responses say when history is cut to 90 days or delayed."""
    notices = []
    for field in ("freemium_window", "freemium_delay"):
        block = payload.get(field)
        if isinstance(block, dict) and block.get("applied") is True:
            message = block.get("message")
            if isinstance(message, str) and message.strip():
                notices.append(message.strip())
    return notices


class FXMacroDataTool(Tool):
    """FXMacroData macroeconomic release, calendar and FX rate tool.

    Attributes:
        api_key (Optional[SecretStr]): FXMacroData API key, read from the
            ``FXMACRODATA_API_KEY`` environment variable by default. Optional.
        base_url (str): API root. Must be an https URL with a host.
        timeout (float): Request timeout in seconds.
        default_limit (int): Rows returned when the caller gives no limit.
    """

    name: str = "fxmacrodata_tool"
    description: str = (
        "Official macroeconomic data for 22 currencies from FXMacroData: an "
        "indicator's release history (mode 'history'), upcoming releases "
        "(mode 'calendar'), the indicator list (mode 'catalogue') and daily "
        "FX rates (mode 'fx')."
    )
    api_key: SecretStr | None = Field(default_factory=_env_key)
    base_url: str = Field("https://api.fxmacrodata.com/v1", description="FXMacroData API root.")
    timeout: float = Field(30.0, description="Request timeout in seconds.")
    default_limit: int = Field(20, description="Rows returned when no limit is given.")

    @field_validator("base_url")
    @classmethod
    def _check_base_url(cls, value: str) -> str:
        parts = urlsplit(value.strip())
        if parts.scheme != "https" or not parts.hostname:
            raise ValueError("base_url must be an https URL with a host")
        return value.strip().rstrip("/")

    def execute(
        self,
        mode: str,
        currency: str | None = None,
        indicator: str | None = None,
        base: str | None = None,
        quote: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Run one FXMacroData lookup.

        Args:
            mode (str): One of ``history`` / ``calendar`` / ``catalogue`` / ``fx``.
            currency (str): Three-letter currency code (all modes but ``fx``).
            indicator (str): Indicator slug, required for ``history`` and an
                optional filter for ``calendar``.
            base (str): Base currency for ``fx``.
            quote (str): Quote currency for ``fx``.
            start_date (str): Optional ``YYYY-MM-DD`` start for history and fx.
            end_date (str): Optional ``YYYY-MM-DD`` end for history and fx.
            limit (int): Rows to return, 1 to 100.

        Returns:
            Dict: ``{"status": "success", ...}`` or ``{"status": "error", "error": ...}``.
        """
        handlers: dict[str, Callable[..., dict[str, Any]]] = {
            "history": self._history,
            "calendar": self._calendar,
            "catalogue": self._catalogue,
            "fx": self._fx,
        }
        handler = handlers.get(mode)
        if handler is None:
            return {"status": "error", "error": "'mode' must be one of: history, calendar, catalogue, fx."}
        args = {
            "currency": currency,
            "indicator": indicator,
            "base": base,
            "quote": quote,
            "start_date": start_date,
            "end_date": end_date,
            "limit": self.default_limit if limit is None else limit,
        }
        try:
            result = handler(args)
        except FXMacroDataError as exc:
            return {"status": "error", "error": self._redact(str(exc))}
        except Exception:
            return {"status": "error", "error": "FXMacroData lookup failed unexpectedly."}
        return self._redact_value({"status": "success", "mode": mode, **result})

    # ------------------------------------------------------------------ #
    # Modes
    # ------------------------------------------------------------------ #

    def _history(self, args: dict[str, Any]) -> dict[str, Any]:
        currency = _currency(args["currency"], "currency")
        indicator = _slug(args["indicator"])
        params = {**_date_window(args["start_date"], args["end_date"]), "limit": str(_limit(args["limit"]))}
        payload = self._get(f"/announcements/{currency}/{indicator}", params)
        releases = [
            {
                "period": row.get("date"),
                "value": row.get("val"),
                "previous_value": row.get("previous_value"),
                "announced_at_utc": row.get("announcement_datetime"),
                "announced_at_local": row.get("announcement_datetime_local"),
                "source_url": row.get("source_url"),
            }
            for row in _rows(payload)
        ]
        return {
            "currency": currency.upper(),
            "indicator": indicator,
            "name": payload.get("name"),
            "releases": releases,
            "has_more": _has_more(payload),
            "notices": _notices(payload),
        }

    def _calendar(self, args: dict[str, Any]) -> dict[str, Any]:
        currency = _currency(args["currency"], "currency")
        params = {} if args["indicator"] is None else {"indicator": _slug(args["indicator"])}
        limit = _limit(args["limit"])
        payload = self._get(f"/calendar/{currency}", params)
        events = [
            {
                "release": row.get("release"),
                "name": row.get("name"),
                "release_time_utc": row.get("announcement_datetime_utc"),
                "reference_period": row.get("reference_period") or row.get("date"),
                "importance": row.get("event_importance"),
            }
            for row in _rows(payload)[:limit]
        ]
        return {"currency": currency.upper(), "events": events}

    def _catalogue(self, args: dict[str, Any]) -> dict[str, Any]:
        currency = _currency(args["currency"], "currency")
        payload = self._get(f"/data_catalogue/{currency}", {})
        indicators = []
        for slug, meta in payload.items():
            if not isinstance(meta, dict):
                continue
            coverage = meta.get("coverage") if isinstance(meta.get("coverage"), dict) else {}
            indicators.append(
                {
                    "indicator": slug,
                    "name": meta.get("name"),
                    "unit": meta.get("unit"),
                    "latest_available_date": coverage.get("latest_available_date"),
                    "requires_api_key": coverage.get("requires_api_key"),
                }
            )
        if not indicators:
            raise FXMacroDataError("FXMacroData returned an empty catalogue.")
        return {"currency": currency.upper(), "indicators": indicators}

    def _fx(self, args: dict[str, Any]) -> dict[str, Any]:
        base = _currency(args["base"], "base")
        quote = _currency(args["quote"], "quote")
        params = {**_date_window(args["start_date"], args["end_date"]), "limit": str(_limit(args["limit"]))}
        payload = self._get(f"/forex/{base}/{quote}", params)
        rates = [{"date": row.get("date"), "rate": row.get("val")} for row in _rows(payload)]
        return {"pair": f"{base.upper()}/{quote.upper()}", "rates": rates, "has_more": _has_more(payload)}

    # ------------------------------------------------------------------ #
    # HTTP and redaction
    # ------------------------------------------------------------------ #

    def _get(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        """GET one API path. Redirects are refused so the key header never moves."""
        headers = {"Accept": "application/json"}
        key = self._key()
        if key:
            headers["X-API-Key"] = key
        try:
            response = requests.get(
                f"{self.base_url}{path}", params=params, headers=headers, timeout=self.timeout, allow_redirects=False
            )
        except requests.Timeout:
            raise FXMacroDataError("FXMacroData did not answer in time.") from None
        except requests.RequestException:
            # Transport errors can format the request; never interpolate them.
            raise FXMacroDataError("FXMacroData could not be reached.") from None
        if response.is_redirect or 300 <= response.status_code < 400:
            raise FXMacroDataError("FXMacroData answered with an unexpected redirect.")
        if response.status_code != 200:
            detail = _STATUS_DETAILS.get(response.status_code, "the request failed")
            raise FXMacroDataError(f"FXMacroData returned HTTP {response.status_code}: {detail}.")
        try:
            payload = response.json()
        except ValueError:
            raise FXMacroDataError("FXMacroData returned a non-JSON response.") from None
        if not isinstance(payload, dict):
            raise FXMacroDataError("FXMacroData returned an unexpected response shape.")
        if "detail" in payload and "data" not in payload:
            raise FXMacroDataError("FXMacroData returned an error response.")
        return payload

    def _key(self) -> str | None:
        if self.api_key is None:
            return None
        return self.api_key.get_secret_value().strip() or None

    def _redact(self, text: str) -> str:
        key = self._key()
        return text.replace(key, "[REDACTED]") if key else text

    def _redact_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return self._redact(value)
        if isinstance(value, dict):
            return {self._redact(str(k)): self._redact_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._redact_value(item) for item in value]
        return value
