#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/10
# @FileName: test_yahoo_finance_tool.py

"""
Unit tests for YahooFinanceTool.

The data-fetching layer (yfinance) is mocked, so the suite is deterministic and
runs without a network connection or the optional ``yfinance`` package. The pure
formatting helpers are exercised directly; the ``execute`` wiring is exercised
through a stubbed ``_get_ticker`` / fetch methods. A dedicated registration test
loads the shipped ``yahoo_finance_tool.yaml`` through the real framework loader
(``Configer`` -> ``ComponentConfiger`` -> ``ToolManager``) so a component-schema
regression is caught at test time rather than at agent runtime.
"""

import os
import unittest
from unittest.mock import Mock, patch

from agentuniverse.agent.action.tool.common_tool import yahoo_finance_tool as yf_module
from agentuniverse.agent.action.tool.common_tool.yahoo_finance_tool import (
    YahooFinanceTool,
)
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.component_configer.component_configer import (
    ComponentConfiger,
)
from agentuniverse.base.config.component_configer.configers.tool_configer import (
    ToolConfiger,
)
from agentuniverse.base.config.configer import Configer

# The shipped component config sits next to the tool implementation module.
YAML_PATH = os.path.join(os.path.dirname(yf_module.__file__),
                         "yahoo_finance_tool.yaml")


class TestFormatters(unittest.TestCase):
    """Pure formatting helpers — no network, no yfinance."""

    def setUp(self) -> None:
        self.tool = YahooFinanceTool()

    def test_format_quote_with_data(self) -> None:
        quote = {
            "regularMarketPrice": 150.0,
            "regularMarketChange": 1.25,
            "regularMarketChangePercent": 0.84,
            "marketCap": 2_500_000_000_000,
            "regularMarketVolume": 55_000_000,
            "currency": "USD",
        }
        out = self.tool._format_quote("AAPL", quote)
        self.assertIn("AAPL", out)
        self.assertIn("regularMarketPrice: 150.00", out)
        self.assertIn("USD", out)
        # marketCap is abbreviated compactly.
        self.assertIn("2.50T", out)
        # Volume uses thousands separators.
        self.assertIn("55,000,000", out)

    def test_format_quote_skips_missing_fields(self) -> None:
        out = self.tool._format_quote("XYZ", {"regularMarketPrice": 12.3})
        self.assertIn("regularMarketPrice", out)
        self.assertNotIn("fiftyTwoWeekHigh", out)

    def test_format_quote_empty(self) -> None:
        out = self.tool._format_quote("XYZ", {})
        self.assertIn("no quote data", out)

    def test_format_history_with_rows(self) -> None:
        rows = [
            {"date": "2024-01-02", "open": 100.0, "high": 102.0,
             "low": 99.0, "close": 101.0, "volume": 1000},
            {"date": "2024-01-01", "open": 98.0, "high": 100.0,
             "low": 97.0, "close": 99.0, "volume": 2000},
        ]
        out = self.tool._format_history("AAPL", rows)
        self.assertIn("AAPL", out)
        self.assertIn("newest first", out)
        # Header columns present.
        self.assertIn("open", out)
        self.assertIn("close", out)
        # Prices formatted to two decimals.
        self.assertIn("101.00", out)
        # Volumes with thousands separators.
        self.assertIn("1,000", out)

    def test_format_history_empty(self) -> None:
        out = self.tool._format_history("AAPL", [])
        self.assertIn("no historical data", out)

    def test_format_info_with_data(self) -> None:
        info = {
            "longName": "Apple Inc.",
            "sector": "Technology",
            "marketCap": 2_500_000_000_000,
            "website": "https://www.apple.com",
        }
        out = self.tool._format_info("AAPL", info)
        self.assertIn("Apple Inc.", out)
        self.assertIn("Technology", out)
        self.assertIn("2.50T", out)

    def test_format_info_empty(self) -> None:
        out = self.tool._format_info("AAPL", {})
        self.assertIn("no company info", out)

    def test_format_info_drops_unstable_extra_fields(self) -> None:
        # Unknown / unstable ticker.info keys must NOT leak into the output —
        # the info payload is curated to keep the agent context compact.
        info = {
            "longName": "Apple Inc.",
            "marketCap": 2_500_000_000_000,
            "quoteType": "EQUITY",
            "someUnstableInternalField": "x" * 500,
            "uuid": "do-not-emit",
        }
        out = self.tool._format_info("AAPL", info)
        self.assertIn("Apple Inc.", out)
        self.assertIn("2.50T", out)
        self.assertNotIn("someUnstableInternalField", out)
        self.assertNotIn("uuid", out)

    def test_format_info_only_emits_known_fields(self) -> None:
        # Every emitted key must be a member of the curated info_fields list.
        info = {
            "longName": "Apple Inc.",
            "sector": "Technology",
            "marketCap": 2_500_000_000_000,
        }
        out = self.tool._format_info("AAPL", info)
        emitted_keys = {
            line.split(":", 1)[0].strip()
            for line in out.splitlines()
            if line.startswith("  ") and ":" in line
        }
        self.assertTrue(emitted_keys)
        self.assertTrue(emitted_keys.issubset(set(self.tool.info_fields)))

    def test_format_info_caps_long_business_summary(self) -> None:
        # longBusinessSummary is a curated field but still an unbounded
        # free-text description, so it must be truncated to the configured cap.
        long_summary = "Apple designs and sells consumer electronics. " * 60
        self.assertGreater(len(long_summary), self.tool.max_business_summary_chars)
        info = {"longName": "Apple Inc.", "longBusinessSummary": long_summary}
        out = self.tool._format_info("AAPL", info)
        cap = self.tool.max_business_summary_chars
        for line in out.splitlines():
            if line.strip().startswith("longBusinessSummary:"):
                # Emitted value body (after the key) must stay within the cap
                # plus the single ellipsis marker.
                body = line.split(":", 1)[1].strip()
                self.assertLessEqual(len(body), cap + 1)
                break
        else:
            self.fail("longBusinessSummary line not emitted")

    def test_format_info_respects_custom_summary_cap(self) -> None:
        long_summary = "x" * 500
        tool = YahooFinanceTool()
        tool.max_business_summary_chars = 50
        out = tool._format_info("AAPL", {"longBusinessSummary": long_summary})
        body = next(
            line.split(":", 1)[1].strip()
            for line in out.splitlines()
            if line.strip().startswith("longBusinessSummary:")
        )
        self.assertLessEqual(len(body), 51)
        self.assertTrue(body.endswith("…"))

    def test_compact_number_suffixes(self) -> None:
        self.assertEqual(self.tool._compact_number(2.5e12), "2.50T")
        self.assertEqual(self.tool._compact_number(3.4e9), "3.40B")
        self.assertEqual(self.tool._compact_number(5.6e6), "5.60M")
        self.assertEqual(self.tool._compact_number(7.8e3), "7.80K")
        self.assertEqual(self.tool._compact_number(123.4), "123.40")

    def test_normalize_symbol(self) -> None:
        self.assertEqual(self.tool._normalize_symbol("aapl"), "AAPL")
        self.assertEqual(self.tool._normalize_symbol("  aapl  "), "AAPL")
        self.assertEqual(self.tool._normalize_symbol(None), "")
        self.assertEqual(self.tool._normalize_symbol("   "), "")


class TestExecute(unittest.TestCase):
    """execute() wiring with the network layer stubbed out."""

    def setUp(self) -> None:
        self.tool = YahooFinanceTool()

    def _mock_ticker(self, info: dict) -> Mock:
        ticker = Mock()
        ticker.info = info
        return ticker

    def test_execute_quote_via_mock_ticker(self) -> None:
        info = {"regularMarketPrice": 150.0, "currency": "USD"}
        ticker = self._mock_ticker(info)
        with patch.object(self.tool, "_get_ticker", return_value=ticker):
            out = self.tool.execute(mode="quote", symbol="aapl")
        self.assertIn("AAPL", out)
        self.assertIn("150.00", out)

    def test_execute_info_via_mock_ticker(self) -> None:
        info = {"longName": "Apple Inc.", "sector": "Technology"}
        ticker = self._mock_ticker(info)
        with patch.object(self.tool, "_get_ticker", return_value=ticker):
            out = self.tool.execute(mode="info", symbol="AAPL")
        self.assertIn("Apple Inc.", out)
        self.assertIn("Technology", out)

    def test_execute_history_via_mocked_fetch(self) -> None:
        # A minimal DataFrame-like stub so the real _fetch_history runs
        # end-to-end (reset_index → rename(lower) → to_dict) without pandas.
        class _FakeHistory:
            empty = False

            def __init__(self, records):
                self._records = records

            def reset_index(self):
                return self

            def rename(self, columns=None):
                return self

            def to_dict(self, orient="records"):
                return list(self._records)

        records = [
            {"date": "2024-01-01", "open": 98.0, "high": 100.0,
             "low": 97.0, "close": 99.0, "volume": 2000},
            {"date": "2024-01-02", "open": 100.0, "high": 102.0,
             "low": 99.0, "close": 101.0, "volume": 1000},
        ]
        ticker = Mock()
        ticker.history.return_value = _FakeHistory(records)
        with patch.object(self.tool, "_get_ticker", return_value=ticker):
            out = self.tool.execute(
                mode="history", symbol="AAPL", period="1mo", interval="1d")
        self.assertIn("AAPL", out)
        self.assertIn("101.00", out)
        # newest first → the 01-02 row precedes the 01-01 row.
        self.assertLess(out.index("2024-01-02"), out.index("2024-01-01"))

    def test_execute_symbol_uppercased_before_fetch(self) -> None:
        ticker = self._mock_ticker({"regularMarketPrice": 1.0})
        with patch.object(self.tool, "_get_ticker", return_value=ticker) as m:
            self.tool.execute(mode="quote", symbol="aapl")
        m.assert_called_once_with("AAPL")

    def test_execute_invalid_mode(self) -> None:
        out = self.tool.execute(mode="frobnicate", symbol="AAPL")
        self.assertIn("invalid mode", out)

    def test_execute_missing_symbol(self) -> None:
        out = self.tool.execute(mode="quote", symbol="")
        self.assertIn("required", out)

    def test_execute_missing_yfinance_reports_install_hint(self) -> None:
        def _no_yfinance(_symbol):
            raise ImportError("yfinance")
        with patch.object(self.tool, "_get_ticker", side_effect=_no_yfinance):
            out = self.tool.execute(mode="quote", symbol="AAPL")
        self.assertIn("yfinance", out)
        self.assertIn("pip install", out)

    def test_execute_surfaces_fetch_errors(self) -> None:
        def _boom(_symbol):
            raise RuntimeError("network down")
        with patch.object(self.tool, "_get_ticker", side_effect=_boom):
            out = self.tool.execute(mode="quote", symbol="AAPL")
        self.assertIn("Error fetching data", out)
        self.assertIn("network down", out)


class TestRegistration(unittest.TestCase):
    """Config / registration through the real framework loader.

    Loads the shipped ``yahoo_finance_tool.yaml`` with the same pipeline the
    component scanner uses (``Configer`` -> ``ComponentConfiger`` ->
    ``ToolManager``) and asserts the tool is resolvable and initializable.
    This guards the component-schema contract: an unrecognised ``class_path``
    (or any other field outside ``metadata`` / ``meta_class``) would leave
    ``component_type`` as ``None`` and silently skip registration.
    """

    def setUp(self) -> None:
        self._configer = Configer(path=os.path.abspath(YAML_PATH)).load()
        # Snapshot the global ApplicationConfigManager state. The registration
        # tests below install their own AppConfiger to drive the real
        # ToolManager pipeline; without restoring it they would leak that
        # synthetic state into unrelated tests that run later in the suite.
        # The getter raises when no AppConfiger has been set yet, so fall back
        # to None — restoring None reproduces that exact unset state.
        try:
            self._prev_app_configer = ApplicationConfigManager().app_configer
        except ValueError:
            self._prev_app_configer = None

    def tearDown(self) -> None:
        ApplicationConfigManager().app_configer = self._prev_app_configer

    def test_yaml_resolves_to_tool_component_type(self) -> None:
        component_configer = ComponentConfiger().load_by_configer(self._configer)
        self.assertEqual(
            component_configer.get_component_config_type(),
            ComponentEnum.TOOL.value,
        )

    def test_yaml_exposes_module_and_class(self) -> None:
        component_configer = ComponentConfiger().load_by_configer(self._configer)
        self.assertEqual(component_configer.metadata_module,
                         "agentuniverse.agent.action.tool.common_tool.yahoo_finance_tool")
        self.assertEqual(component_configer.metadata_class, "YahooFinanceTool")

    def test_tool_is_resolvable_through_tool_manager(self) -> None:
        tool_configer = ToolConfiger().load_by_configer(self._configer)
        app_configer = AppConfiger()
        app_configer.tool_configer_map = {tool_configer.name: tool_configer}
        ApplicationConfigManager().app_configer = app_configer

        tool = ToolManager().get_instance_obj(tool_configer.name)

        self.assertIsInstance(tool, YahooFinanceTool)
        self.assertEqual(tool.name, "yahoo_finance_tool")
        self.assertEqual(tool.component_type, ComponentEnum.TOOL)
        self.assertEqual(tool.input_keys, ["mode", "symbol"])
        self.assertEqual(tool.args_model_schema["properties"]["mode"]["enum"],
                         ["quote", "history", "info"])

    def test_registered_tool_executes_without_network(self) -> None:
        tool_configer = ToolConfiger().load_by_configer(self._configer)
        app_configer = AppConfiger()
        app_configer.tool_configer_map = {tool_configer.name: tool_configer}
        ApplicationConfigManager().app_configer = app_configer

        tool = ToolManager().get_instance_obj(tool_configer.name)
        ticker = Mock()
        ticker.info = {"regularMarketPrice": 150.0, "currency": "USD"}
        with patch.object(tool, "_get_ticker", return_value=ticker):
            out = tool.run(mode="quote", symbol="aapl")
        self.assertIn("AAPL", out)
        self.assertIn("150.00", out)


if __name__ == '__main__':
    unittest.main()
