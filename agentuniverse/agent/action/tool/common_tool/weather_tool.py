# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @Author  : contributor
# @FileName: weather_tool.py

"""
Weather query tool backed by the free wttr.in API.

This tool fetches current conditions or a short-term forecast for any location
from ``https://wttr.in``. wttr.in is a free, console-oriented weather service
that requires **no API key and no account**, which makes the tool usable out of
the box — addressing the *weather* item of issue #252 (tool plug-in
integration).

Three operating modes are supported:

* ``current``  — the current conditions for a location (temperature, "feels
  like", wind, humidity, description).
* ``forecast`` — a multi-day forecast (defaults to the next 3 days).
* ``format``   — a one-line, custom-format current snapshot, e.g.
  ``%l: %c %t %w`` (see the wttr.in ``?format`` documentation).

The result can be returned as human-readable ``text`` (the default, wttr.in's
console output) or parsed ``json`` (the structured wttr.in payload). The HTTP
layer is isolated in :meth:`_request` and :meth:`_get`, so the whole tool is
unit-testable without a network connection: tests patch ``requests.get`` (or
the thinner ``_get`` helper) and feed fixed payloads to the pure formatters.

``requests`` is imported at module top level, matching the other HTTP-backed
common tools in agentUniverse (crossref, github, jina_ai, ...). It is already a
core framework dependency, so no extra install is required.
"""

import json as _json
from typing import Any, Dict, Optional

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool


class WeatherTool(Tool):
    """wttr.in-backed weather tool.

    Attributes:
        default_location (str): Location used when the caller omits
            ``location``. Any free-form string wttr.in accepts: a city name
            (``Beijing``), an IATA/ICAO airport code (``PEK``), a zip code, or
            ``lat,long``.
        units (str): Measurement system — ``metric`` (Celsius, km/h, default),
            ``imperial`` (Fahrenheit, mph), or ``auto`` (let wttr.in decide
            from the location).
        request_timeout (float): Per-request HTTP timeout in seconds.
        base_url (str): wttr.in base URL (overridable for tests / self-hosted).
        forecast_days (int): Number of days requested in ``forecast`` mode.
            wttr.in supports 0 (today only), 1, 2, or 3.
    """

    name: str = "weather_tool"
    description: str = (
        "Weather tool backed by the free wttr.in API (no API key required). "
        "Fetch the current conditions, a multi-day forecast, or a custom "
        "one-line format for any location."
    )

    default_location: str = Field(
        "Beijing",
        description="Location used when the caller omits 'location'.",
    )
    units: str = Field(
        "metric",
        description="Measurement system: metric | imperial | auto.",
    )
    request_timeout: float = Field(
        10.0,
        description="Per-request HTTP timeout in seconds.",
    )
    base_url: str = "https://wttr.in"
    forecast_days: int = Field(
        3,
        description="Days requested in forecast mode (0-3).",
    )

    _VALID_UNITS = {"metric", "imperial", "auto"}

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #
    def execute(self,
                location: Optional[str] = None,
                operation: str = "current",
                format: str = "text",
                forecast_days: Optional[int] = None,
                format_string: Optional[str] = None) -> str:
        """Run a weather query against wttr.in.

        Args:
            location (str): Free-form location (city, airport code, zip, or
                ``lat,long``). Falls back to ``default_location`` when empty.
            operation (str): One of ``current`` / ``forecast`` / ``format``.
            format (str): Output format — ``text`` (human-readable) or
                ``json`` (structured). Ignored in ``format`` mode.
            forecast_days (int): Override ``forecast_days`` for this call
                (0-3). Only used in ``forecast`` mode.
            format_string (str): A wttr.in ``?format`` string, e.g.
                ``%l: %c %t``. Only used in ``format`` mode.

        Returns:
            str: The weather result (human-readable text, a JSON string, or an
            error message beginning with ``Error:``).
        """
        loc = self._resolve_location(location)
        if not loc:
            return "Error: 'location' is required and no default_location is set."

        if operation not in ("current", "forecast", "format"):
            return (f"Error: invalid operation '{operation}'. "
                    "Must be one of: current, forecast, format.")

        if self.units not in self._VALID_UNITS:
            return (f"Error: invalid units '{self.units}'. "
                    f"Must be one of: {', '.join(sorted(self._VALID_UNITS))}.")

        try:
            if operation == "format":
                return self._fetch_format(loc, format_string)
            if operation == "forecast":
                return self._fetch_forecast(loc, format, forecast_days)
            return self._fetch_current(loc, format)
        except Exception as exc:  # noqa: BLE001 - surface any fetch error to the agent
            return f"Error fetching weather for '{loc}': {exc}"

    # ------------------------------------------------------------------ #
    # Network layer — lazy requests import, isolated for testing
    # ------------------------------------------------------------------ #
    def _get(self, url: str, params: Dict[str, Any], headers: Dict[str, str]):
        """Perform a GET request.

        Isolated as its own method so tests can patch it (or patch
        ``requests.get`` at the module level) without touching the network.
        """
        return requests.get(url, params=params, headers=headers,
                            timeout=self.request_timeout)

    def _request(self, path: str, params: Dict[str, Any],
                 accept: str) -> str:
        """Issue a single wttr.in request and return the decoded body text."""
        url = f"{self.base_url}/{path}"
        headers = {"Accept": accept}
        response = self._get(url, params, headers)
        self._raise_for_status(response)
        return response.text

    @staticmethod
    def _raise_for_status(response) -> None:
        """Raise on an HTTP error, including the body for diagnostics."""
        status = getattr(response, "status_code", 200)
        if status >= 400:
            body = ""
            try:
                body = response.text or ""
            except Exception:  # noqa: BLE001
                body = ""
            snippet = body[:200].replace("\n", " ")
            raise RuntimeError(f"HTTP {status} from wttr.in: {snippet}".rstrip())

    # ------------------------------------------------------------------ #
    # Mode implementations
    # ------------------------------------------------------------------ #
    def _fetch_current(self, location: str, format: str) -> str:
        """Fetch current conditions in text or json form."""
        params = {self._units_param(): ""}
        if format == "json":
            body = self._request(location, params, accept="application/json")
            return self._format_current_json(body)
        # text mode: wttr.in returns a compact console block with ?0 (today
        # only, no forecast) for a concise current snapshot.
        params["0"] = ""
        params["T"] = ""  # no terminal colours
        return self._request(location, params, accept="text/plain").strip()

    def _fetch_forecast(self, location: str, format: str,
                        forecast_days: Optional[int]) -> str:
        """Fetch a multi-day forecast in text or json form."""
        days = self._resolve_forecast_days(forecast_days)
        if format == "json":
            params = {self._units_param(): ""}
            body = self._request(location, params, accept="application/json")
            return self._format_forecast_json(body, days)
        params = {self._units_param(): "", "T": ""}
        return self._request(location, params,
                             accept="text/plain").strip()

    def _fetch_format(self, location: str,
                      format_string: Optional[str]) -> str:
        """Fetch a one-line custom-format snapshot."""
        if not format_string:
            # A sensible default one-liner: location + condition + temp.
            format_string = "%l: %c %t"
        params = {self._units_param(): "", "format": format_string}
        return self._request(location, params, accept="text/plain").strip()

    # ------------------------------------------------------------------ #
    # JSON formatting (pure) — fully testable without a network
    # ------------------------------------------------------------------ #
    def _format_current_json(self, body: str) -> str:
        """Render the wttr.in JSON payload as a readable current-weather block."""
        try:
            data = _json.loads(body)
        except (ValueError, TypeError) as exc:
            return f"Error: could not parse wttr.in JSON response: {exc}"

        current = (data or {}).get("current_condition", [{}])[0]
        if not current:
            return "No current conditions available."
        area = self._nearest_area_name(data)
        lines = [f"{area or 'Location'} — current weather"]
        desc = self._weather_description(current)
        if desc:
            lines.append(f"  condition: {desc}")
        for key, label in (("temp_C", "temperature"),
                           ("FeelsLikeC", "feels_like"),
                           ("humidity", "humidity"),
                           ("winddir16Point", "wind_direction"),
                           ("windspeedKmph", "wind_speed_kmph")):
            if key in current and current[key] not in (None, ""):
                lines.append(f"  {label}: {current[key]}")
        return "\n".join(lines)

    def _format_forecast_json(self, body: str, days: int) -> str:
        """Render the wttr.in JSON payload as a multi-day forecast block."""
        try:
            data = _json.loads(body)
        except (ValueError, TypeError) as exc:
            return f"Error: could not parse wttr.in JSON response: {exc}"

        weather = (data or {}).get("weather", [])
        if not weather:
            return "No forecast available."
        area = self._nearest_area_name(data)
        lines = [f"{area or 'Location'} — forecast"]
        for day in weather[:max(0, days)]:
            date = day.get("date", "?")
            max_t = day.get("maxtempC", "?")
            min_t = day.get("mintempC", "?")
            hourly = day.get("hourly", [])
            desc = ""
            if hourly:
                noon = (hourly[len(hourly) // 2]
                        if hourly else hourly)
                desc = self._weather_description(noon)
            lines.append(
                f"  {date}: {desc or 'n/a'}, "
                f"{min_t}°C – {max_t}°C")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Small helpers
    # ------------------------------------------------------------------ #
    def _resolve_location(self, location: Optional[str]) -> str:
        """Return the cleaned location, falling back to default_location."""
        if location and str(location).strip():
            return str(location).strip()
        return (self.default_location or "").strip()

    def _resolve_forecast_days(self, forecast_days: Optional[int]) -> int:
        """Clamp the forecast-day count to the wttr.in-supported range."""
        if forecast_days is None:
            forecast_days = self.forecast_days
        try:
            days = int(forecast_days)
        except (TypeError, ValueError):
            days = self.forecast_days
        return max(0, min(3, days))

    def _units_param(self) -> str:
        """Map the ``units`` setting to the wttr.in query parameter."""
        return {"metric": "m", "imperial": "u", "auto": ""}[self.units]

    @staticmethod
    def _weather_description(bucket: Dict[str, Any]) -> str:
        """Pull a human-readable description out of a wttr.in condition bucket."""
        desc = bucket.get("weatherDesc")
        if isinstance(desc, list) and desc and isinstance(desc[0], dict):
            return str(desc[0].get("value", "")).strip()
        if isinstance(desc, dict):
            return str(desc.get("value", "")).strip()
        return ""

    @staticmethod
    def _nearest_area_name(data: Dict[str, Any]) -> str:
        """Best-effort area name from the wttr.in JSON payload."""
        areas = (data or {}).get("nearest_area") or []
        if areas and isinstance(areas[0], dict):
            name = areas[0].get("areaName")
            if isinstance(name, list) and name and isinstance(name[0], dict):
                return str(name[0].get("value", "")).strip()
        return ""
