import json
import os
import unittest
from unittest import mock

import requests

from agentuniverse.agent.action.tool.common_tool import fxmacrodata_tool as fx_module
from agentuniverse.agent.action.tool.common_tool.fxmacrodata_tool import FXMacroDataTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(fx_module.__file__), "fxmacrodata_tool.yaml")
KEY = "fxmd-secret-key-123456"
GET = "agentuniverse.agent.action.tool.common_tool.fxmacrodata_tool.requests.get"


def response(status=200, body=None, text=None, location=None):
    resp = requests.Response()
    resp.status_code = status
    resp._content = (text if text is not None else json.dumps(body)).encode()
    resp.headers["Content-Type"] = "application/json"
    if location:
        resp.headers["Location"] = location
    return resp


def history_payload(**extra):
    payload = {
        "name": "Inflation (CPI)",
        "pagination": {"has_more": False, "total_count": 1},
        "freemium_window": {"applied": True, "message": "Anonymous access returns the most recent 90 days."},
        "freemium_delay": {"applied": True, "message": "Free access is delayed by 15 minutes."},
        "data": [
            {
                "date": "2026-08-31",
                "val": 3.4,
                "previous_value": 3.4,
                "announcement_datetime": 1789129800,
                "announcement_datetime_local": "2026-09-11T08:30:00-04:00",
                "source_url": "https://www.bls.gov/",
            }
        ],
    }
    payload.update(extra)
    return payload


class FXMacroDataToolTest(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.dict(os.environ, {}, clear=False)
        patcher.start()
        os.environ.pop("FXMACRODATA_API_KEY", None)
        self.addCleanup(patcher.stop)

    def test_keyless_history_sends_no_key_and_refuses_redirects(self):
        with mock.patch(GET, return_value=response(body=history_payload())) as get:
            result = FXMacroDataTool().execute(
                mode="history",
                currency=" usd ",
                indicator="Inflation",
                start_date="2026-07-01",
                end_date="2026-09-30",
                limit=5,
            )
        self.assertEqual(result["status"], "success", result)
        args, kwargs = get.call_args
        self.assertEqual(args[0], "https://api.fxmacrodata.com/v1/announcements/usd/inflation")
        self.assertNotIn("X-API-Key", kwargs["headers"])
        self.assertIs(kwargs["allow_redirects"], False)
        self.assertEqual(kwargs["params"], {"start_date": "2026-07-01", "end_date": "2026-09-30", "limit": "5"})
        self.assertEqual(result["releases"][0]["value"], 3.4)
        self.assertEqual(result["releases"][0]["period"], "2026-08-31")
        self.assertIs(result["has_more"], False)
        self.assertEqual(len(result["notices"]), 2)

    def test_env_key_is_a_secret_header_and_redacted_from_results(self):
        os.environ["FXMACRODATA_API_KEY"] = f" {KEY} "
        tool = FXMacroDataTool()
        self.assertNotIn(KEY, repr(tool.api_key))
        body = history_payload()
        body["data"][0]["source_url"] = f"https://example.test/?k={KEY}"
        with mock.patch(GET, return_value=response(body=body)) as get:
            result = tool.execute(mode="history", currency="EUR", indicator="policy_rate")
        self.assertEqual(get.call_args.kwargs["headers"]["X-API-Key"], KEY)
        self.assertNotIn(KEY, str(result))
        self.assertIn("[REDACTED]", str(result))

    def test_redirects_are_errors(self):
        for status in (301, 302, 307, 308):
            with mock.patch(GET, return_value=response(status, text="", location="http://evil.test/")):
                result = FXMacroDataTool(api_key=KEY).execute(mode="calendar", currency="USD")
            self.assertEqual(result["status"], "error")
            self.assertIn("redirect", result["error"])

    def test_http_errors_do_not_echo_the_body(self):
        for status in (401, 403, 404, 422, 429, 500):
            with mock.patch(GET, return_value=response(status, body={"detail": f"bad {KEY}"})):
                result = FXMacroDataTool(api_key=KEY).execute(mode="fx", base="EUR", quote="USD")
            self.assertIn(f"HTTP {status}", result["error"])
            self.assertNotIn(KEY, str(result))

    def test_transport_errors_are_never_interpolated(self):
        cases = [
            (requests.ConnectionError(f"X-API-Key: {KEY}"), "could not be reached"),
            (requests.ReadTimeout(f"slow {KEY}"), "did not answer in time"),
            (requests.exceptions.InvalidHeader(f"Invalid header value {KEY}"), "could not be reached"),
        ]
        for error, message in cases:
            with mock.patch(GET, side_effect=error):
                result = FXMacroDataTool(api_key=KEY).execute(mode="catalogue", currency="USD")
            self.assertIn(message, result["error"])
            self.assertNotIn(KEY, str(result))
        with mock.patch(GET, side_effect=RuntimeError(KEY)):
            result = FXMacroDataTool(api_key=KEY).execute(mode="catalogue", currency="USD")
        self.assertEqual(result["error"], "FXMacroData lookup failed unexpectedly.")

    def test_bad_200_bodies_are_errors(self):
        bodies = [
            response(text="<html>oops</html>"),
            response(body=[1, 2]),
            response(body={"detail": "This endpoint requires an API key"}),
            response(body={"data": {"not": "a list"}}),
            response(body=history_payload(pagination=[])),
            response(body=history_payload(pagination={"has_more": "no"})),
        ]
        for body in bodies:
            with mock.patch(GET, return_value=body):
                result = FXMacroDataTool().execute(mode="history", currency="USD", indicator="inflation")
            self.assertEqual(result["status"], "error", result)

    def test_invalid_input_never_calls_the_api(self):
        cases = [
            ({"mode": "nope"}, "'mode' must be one of"),
            ({"mode": "history", "currency": "US", "indicator": "cpi"}, "three-letter"),
            ({"mode": "history", "currency": "USD", "indicator": "c p i"}, "slug"),
            ({"mode": "history", "currency": "USD"}, "slug"),
            ({"mode": "history", "currency": "USD", "indicator": "cpi", "start_date": "2026/01/01"}, "YYYY-MM-DD"),
            ({"mode": "history", "currency": "USD", "indicator": "cpi", "start_date": "2026-02-30"}, "real calendar"),
            (
                {
                    "mode": "history",
                    "currency": "USD",
                    "indicator": "cpi",
                    "start_date": "2026-05-01",
                    "end_date": "2026-04-01",
                },
                "on or before",
            ),
            ({"mode": "history", "currency": "USD", "indicator": "cpi", "limit": 101}, "1 to 100"),
            ({"mode": "history", "currency": "USD", "indicator": "cpi", "limit": True}, "1 to 100"),
            ({"mode": "fx", "base": "EUR"}, "'quote'"),
        ]
        for params, message in cases:
            with mock.patch(GET) as get:
                result = FXMacroDataTool().execute(**params)
            self.assertEqual(result["status"], "error")
            self.assertIn(message, result["error"])
            get.assert_not_called()

    def test_base_url_is_validated_at_creation(self):
        for bad in ("http://api.fxmacrodata.com/v1", "https://", "ftp://example.com"):
            with self.assertRaises(ValueError):
                FXMacroDataTool(base_url=bad)
        self.assertEqual(FXMacroDataTool(base_url="https://example.com/v1/").base_url, "https://example.com/v1")

    def test_calendar_filters_and_truncates(self):
        rows = [
            {
                "release": f"r{i}",
                "name": "Payrolls",
                "announcement_datetime_utc": "2026-11-06T13:30:00+00:00",
                "reference_period": "October 2026",
                "date": "2026-10-31",
                "event_importance": "high",
            }
            for i in range(5)
        ]
        with mock.patch(GET, return_value=response(body={"data": rows})) as get:
            result = FXMacroDataTool().execute(mode="calendar", currency="USD", indicator="non_farm_payrolls", limit=2)
        self.assertEqual(get.call_args.kwargs["params"], {"indicator": "non_farm_payrolls"})
        self.assertEqual([e["release"] for e in result["events"]], ["r0", "r1"])
        self.assertEqual(result["events"][0]["reference_period"], "October 2026")

    def test_catalogue_summary_and_empty_catalogue(self):
        body = {
            "inflation": {
                "name": "Inflation (CPI)",
                "unit": "%",
                "coverage": {"latest_available_date": "2026-08-31", "requires_api_key": False},
            }
        }
        with mock.patch(GET, return_value=response(body=body)):
            result = FXMacroDataTool().execute(mode="catalogue", currency="usd")
        self.assertEqual(
            result["indicators"],
            [
                {
                    "indicator": "inflation",
                    "name": "Inflation (CPI)",
                    "unit": "%",
                    "latest_available_date": "2026-08-31",
                    "requires_api_key": False,
                }
            ],
        )
        with mock.patch(GET, return_value=response(body={})):
            self.assertEqual(FXMacroDataTool().execute(mode="catalogue", currency="usd")["status"], "error")

    def test_fx_rows(self):
        body = {"data": [{"date": "2026-10-06", "val": 1.0931}], "pagination": {"has_more": True}}
        with mock.patch(GET, return_value=response(body=body)) as get:
            result = FXMacroDataTool(api_key=KEY).execute(mode="fx", base="eur", quote="usd", limit=1)
        self.assertTrue(get.call_args.args[0].endswith("/forex/eur/usd"))
        self.assertEqual(result["pair"], "EUR/USD")
        self.assertEqual(result["rates"], [{"date": "2026-10-06", "rate": 1.0931}])
        self.assertIs(result["has_more"], True)


class FXMacroDataRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "FXMacroDataTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, FXMacroDataTool)
        self.assertEqual(tool.input_keys, ["mode"])


if __name__ == "__main__":
    unittest.main()
