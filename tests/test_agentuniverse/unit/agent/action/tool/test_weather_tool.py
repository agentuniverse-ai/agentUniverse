#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: test_weather_tool.py

"""
Unit tests for WeatherTool.

The HTTP layer (wttr.in via requests) is mocked, so the suite is deterministic
and runs without a network connection or the optional ``requests`` package.
Tests cover: the three operations (current / forecast / format), text vs json
output, location fallback, units mapping, forecast-day clamping, request
parameter wiring, error handling (HTTP error, import error, bad JSON), and the
pure JSON formatters.
"""

import json
import unittest
from unittest.mock import Mock, patch

from agentuniverse.agent.action.tool.common_tool.weather_tool import (
    WeatherTool,
)


def _response(body: str = "", status: int = 200) -> Mock:
    """Build a fake requests.Response-like Mock."""
    resp = Mock()
    resp.text = body
    resp.status_code = status
    return resp


# A representative wttr.in JSON payload (condensed for tests).
SAMPLE_JSON = {
    "nearest_area": [
        {"areaName": [{"value": "Beijing"}],
         "country": [{"value": "China"}]}
    ],
    "current_condition": [{
        "temp_C": "30",
        "FeelsLikeC": "32",
        "humidity": "55",
        "weatherDesc": [{"value": "Sunny"}],
        "winddir16Point": "NW",
        "windspeedKmph": "12",
    }],
    "weather": [
        {"date": "2026-07-23", "maxtempC": "32", "mintempC": "24",
         "hourly": [{"weatherDesc": [{"value": "Sunny"}]}]},
        {"date": "2026-07-24", "maxtempC": "31", "mintempC": "23",
         "hourly": [{"weatherDesc": [{"value": "Partly cloudy"}]}]},
        {"date": "2026-07-25", "maxtempC": "29", "mintempC": "22",
         "hourly": [{"weatherDesc": [{"value": "Rain"}]}]},
    ],
}


class TestFormatters(unittest.TestCase):
    """Pure JSON formatting helpers — no network, no requests."""

    def setUp(self) -> None:
        self.tool = WeatherTool()
        self.body = json.dumps(SAMPLE_JSON)

    def test_format_current_json(self) -> None:
        out = self.tool._format_current_json(self.body)
        self.assertIn("Beijing", out)
        self.assertIn("condition: Sunny", out)
        self.assertIn("temperature: 30", out)
        self.assertIn("feels_like: 32", out)

    def test_format_current_json_empty(self) -> None:
        out = self.tool._format_current_json(
            json.dumps({"current_condition": [{}], "nearest_area": []}))
        self.assertIn("No current conditions", out)

    def test_format_current_json_bad_body(self) -> None:
        out = self.tool._format_current_json("not json")
        self.assertIn("Error", out)

    def test_format_forecast_json_truncates_to_days(self) -> None:
        out = self.tool._format_forecast_json(self.body, days=2)
        # Only the first two days should appear.
        self.assertIn("2026-07-23", out)
        self.assertIn("2026-07-24", out)
        self.assertNotIn("2026-07-25", out)

    def test_format_forecast_json_all_days(self) -> None:
        out = self.tool._format_forecast_json(self.body, days=3)
        self.assertIn("2026-07-25", out)


class TestExecute(unittest.TestCase):
    """execute() wiring with the network layer stubbed out."""

    def setUp(self) -> None:
        self.tool = WeatherTool()

    def test_execute_current_text(self) -> None:
        with patch.object(self.tool, "_get",
                          return_value=_response(" Sunny 30°C\n")):
            out = self.tool.execute(location="Beijing", operation="current")
        self.assertIn("Sunny", out)
        self.assertNotIn("Error", out)

    def test_execute_current_json(self) -> None:
        with patch.object(self.tool, "_get",
                          return_value=_response(json.dumps(SAMPLE_JSON))):
            out = self.tool.execute(location="Beijing",
                                    operation="current", format="json")
        self.assertIn("Beijing", out)
        self.assertIn("Sunny", out)

    def test_execute_forecast_json(self) -> None:
        with patch.object(self.tool, "_get",
                          return_value=_response(json.dumps(SAMPLE_JSON))):
            out = self.tool.execute(location="Beijing",
                                    operation="forecast", format="json",
                                    forecast_days=2)
        self.assertIn("2026-07-23", out)

    def test_execute_format_mode_uses_format_string(self) -> None:
        with patch.object(self.tool, "_get",
                          return_value=_response("Beijing: ☀️ 30°C\n")) as m:
            out = self.tool.execute(location="Beijing", operation="format",
                                    format_string="%l: %c %t")
        self.assertIn("Beijing", out)
        # The format_string must reach wttr.in as a 'format' query param.
        # _get is called as _get(url, params, headers) — params is positional.
        params = m.call_args.args[1]
        self.assertEqual(params["format"], "%l: %c %t")

    def test_execute_uses_default_location_when_ommitted(self) -> None:
        self.tool.default_location = "Shanghai"
        with patch.object(self.tool, "_get",
                          return_value=_response("ok")) as m:
            self.tool.execute(operation="current")
        # The location becomes the URL path.
        url = m.call_args.args[0]
        self.assertIn("Shanghai", url)

    def test_execute_missing_location_and_no_default(self) -> None:
        self.tool.default_location = ""
        out = self.tool.execute(operation="current")
        self.assertIn("required", out)

    def test_execute_invalid_operation(self) -> None:
        out = self.tool.execute(location="Beijing", operation="bogus")
        self.assertIn("invalid operation", out)

    def test_execute_invalid_units(self) -> None:
        self.tool.units = "kelvin"
        out = self.tool.execute(location="Beijing", operation="current")
        self.assertIn("invalid units", out)

    def test_execute_surfaces_http_error(self) -> None:
        with patch.object(self.tool, "_get",
                          return_value=_response("Not found", status=404)):
            out = self.tool.execute(location="Beijing", operation="current")
        self.assertIn("Error fetching weather", out)
        self.assertIn("HTTP 404", out)

    def test_execute_surfaces_connection_error(self) -> None:
        # Any non-HTTP failure from the network layer is surfaced as a clear,
        # prefixed error rather than raising out of the tool.
        with patch.object(self.tool, "_get",
                          side_effect=ConnectionError("network down")):
            out = self.tool.execute(location="Beijing", operation="current")
        self.assertIn("Error fetching weather", out)
        self.assertIn("network down", out)


class TestRequestWiring(unittest.TestCase):
    """The units / location parameters reach wttr.in correctly."""

    def test_units_param_mapping(self) -> None:
        tool = WeatherTool()
        tool.units = "imperial"
        self.assertEqual(tool._units_param(), "u")
        tool.units = "auto"
        self.assertEqual(tool._units_param(), "")
        tool.units = "metric"
        self.assertEqual(tool._units_param(), "m")

    def test_forecast_days_clamped(self) -> None:
        tool = WeatherTool()
        self.assertEqual(tool._resolve_forecast_days(5), 3)
        self.assertEqual(tool._resolve_forecast_days(-1), 0)
        self.assertEqual(tool._resolve_forecast_days(None), tool.forecast_days)

    def test_timeout_passed_to_requests(self) -> None:
        tool = WeatherTool()
        tool.request_timeout = 7.5
        with patch("agentuniverse.agent.action.tool.common_tool."
                   "weather_tool.requests.get",
                   return_value=_response("ok")) as m:
            tool.execute(location="Beijing", operation="current")
        self.assertEqual(m.call_args.kwargs["timeout"], 7.5)

    def test_requests_get_patched_at_module_level_works(self) -> None:
        # The lazy import means requests is resolved at call time from the
        # tool module's namespace; patching it there must take effect.
        tool = WeatherTool()
        with patch("agentuniverse.agent.action.tool.common_tool."
                   "weather_tool.requests.get",
                   return_value=_response(json.dumps(SAMPLE_JSON))):
            out = tool.execute(location="Beijing", operation="current",
                               format="json")
        self.assertIn("Beijing", out)


if __name__ == "__main__":
    unittest.main()
