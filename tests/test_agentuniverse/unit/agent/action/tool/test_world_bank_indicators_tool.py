#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.world_bank_indicators_tool import (
    WorldBankIndicatorsTool,
)


SERIES_PAYLOAD = [
    {"page": 1, "pages": 1, "per_page": 5, "total": 2, "lastupdated": "2026-09-01"},
    [
        {
            "indicator": {"id": "NY.GDP.MKTP.KD.ZG", "value": "GDP growth (annual %)"},
            "country": {"id": "CN", "value": "China"},
            "countryiso3code": "CHN",
            "date": "2024",
            "value": 5.0,
            "unit": "",
            "decimal": 1,
            "obs_status": "",
        },
        {
            "indicator": {"id": "NY.GDP.MKTP.KD.ZG", "value": "GDP growth (annual %)"},
            "country": {"id": "CN", "value": "China"},
            "countryiso3code": "CHN",
            "date": "2023",
            "value": None,
            "unit": "",
            "decimal": 1,
            "obs_status": "",
        },
    ],
]

COUNTRY_PAYLOAD = [
    {"page": 1, "pages": 1, "per_page": 10, "total": 1},
    [
        {
            "id": "CHN",
            "iso2Code": "CN",
            "name": "China",
            "region": {"value": "East Asia & Pacific"},
            "incomeLevel": {"value": "Upper middle income"},
            "lendingType": {"value": "IBRD"},
            "capitalCity": "Beijing",
            "longitude": "116.286",
            "latitude": "40.0495",
        }
    ],
]

CATALOG_PAYLOAD = [
    {"page": 2, "pages": 500, "per_page": 2, "total": 1000},
    [
        {
            "id": "NY.GDP.MKTP.KD.ZG",
            "name": "GDP growth (annual %)",
            "source": {"value": "World Development Indicators"},
            "unit": "",
            "sourceNote": "Annual percentage growth rate of GDP.",
        }
    ],
]


def response_mock(json_data):
    response = Mock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class WorldBankIndicatorsToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = WorldBankIndicatorsTool()

    @patch("agentuniverse.agent.action.tool.common_tool.world_bank_indicators_tool.requests.get")
    def test_series_resolves_alias_and_normalizes_observations(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(SERIES_PAYLOAD)

        result = self.tool.execute(
            mode="series",
            country="chn, usa",
            indicator="gdp_growth",
            start_year=2023,
            end_year=2024,
            max_results=5,
        )

        self.assertEqual(result["countries"], ["CHN", "USA"])
        self.assertEqual(result["indicator"], "NY.GDP.MKTP.KD.ZG")
        self.assertEqual(result["indicator_alias"], "gdp_growth")
        self.assertEqual(result["start_year"], 2023)
        self.assertEqual(result["end_year"], 2024)
        self.assertEqual(result["total_results"], 2)
        self.assertEqual(result["returned_results"], 2)
        self.assertEqual(result["last_updated"], "2026-09-01")
        self.assertEqual(
            result["observations"][0],
            {
                "country_code": "CHN",
                "country": "China",
                "indicator_code": "NY.GDP.MKTP.KD.ZG",
                "indicator": "GDP growth (annual %)",
                "year": "2024",
                "value": 5.0,
                "unit": "",
                "decimal": 1,
                "observation_status": "",
            },
        )
        request = mock_get.call_args
        self.assertEqual(
            request.args[0],
            "https://api.worldbank.org/v2/country/CHN;USA/indicator/NY.GDP.MKTP.KD.ZG",
        )
        self.assertEqual(
            request.kwargs["params"],
            {"format": "json", "per_page": 5, "page": 1, "source": 2, "date": "2023:2024"},
        )
        self.assertEqual(request.kwargs["timeout"], 15.0)
        self.assertEqual(request.kwargs["headers"]["Accept"], "application/json")

    @patch("agentuniverse.agent.action.tool.common_tool.world_bank_indicators_tool.requests.get")
    def test_series_accepts_custom_indicator_and_single_year(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(SERIES_PAYLOAD)

        result = self.tool.execute(country="USA", indicator="sp.pop.totl", start_year=2020)

        self.assertEqual(result["indicator"], "SP.POP.TOTL")
        self.assertEqual(result["indicator_alias"], "")
        self.assertEqual(result["start_year"], 2020)
        self.assertEqual(result["end_year"], 2020)
        self.assertEqual(mock_get.call_args.kwargs["params"]["date"], "2020:2020")

    @patch("agentuniverse.agent.action.tool.common_tool.world_bank_indicators_tool.requests.get")
    def test_catalog_returns_page_and_common_aliases(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(CATALOG_PAYLOAD)

        result = self.tool.execute(mode="catalog", max_results=2, page=2)

        self.assertEqual(result["total_results"], 1000)
        self.assertEqual(result["total_pages"], 500)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["common_aliases"]["inflation"], "FP.CPI.TOTL.ZG")
        self.assertEqual(result["indicators"][0]["id"], "NY.GDP.MKTP.KD.ZG")
        self.assertEqual(mock_get.call_args.args[0], "https://api.worldbank.org/v2/source/2/indicator")
        self.assertEqual(mock_get.call_args.kwargs["params"], {"format": "json", "per_page": 2, "page": 2})

    @patch("agentuniverse.agent.action.tool.common_tool.world_bank_indicators_tool.requests.get")
    def test_country_returns_normalized_metadata(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(COUNTRY_PAYLOAD)

        result = self.tool.execute(mode="country", country="CHN")

        self.assertEqual(result["total_results"], 1)
        self.assertEqual(
            result["countries"],
            [
                {
                    "id": "CHN",
                    "iso2_code": "CN",
                    "name": "China",
                    "region": "East Asia & Pacific",
                    "income_level": "Upper middle income",
                    "lending_type": "IBRD",
                    "capital_city": "Beijing",
                    "longitude": "116.286",
                    "latitude": "40.0495",
                }
            ],
        )
        self.assertEqual(mock_get.call_args.args[0], "https://api.worldbank.org/v2/country/CHN")
        self.assertNotIn("source", mock_get.call_args.kwargs["params"])

    @patch("agentuniverse.agent.action.tool.common_tool.world_bank_indicators_tool.requests.get")
    def test_empty_collection_returns_empty_results(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock([{"page": 1, "pages": 0, "total": 0}, []])

        result = self.tool.execute(country="CHN", indicator="inflation")

        self.assertEqual(result["total_results"], 0)
        self.assertEqual(result["observations"], [])

    @patch("agentuniverse.agent.action.tool.common_tool.world_bank_indicators_tool.requests.get")
    def test_api_error_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            [{"message": [{"id": "120", "key": "Invalid value", "value": "Invalid country code"}]}]
        )

        result = self.tool.execute(country="CHN", indicator="population")

        self.assertEqual(result["error"]["type"], "api_error")
        self.assertIn("Invalid country code", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.world_bank_indicators_tool.requests.get")
    def test_timeout_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("slow")

        result = self.tool.execute(country="CHN", indicator="population")

        self.assertEqual(result["error"]["type"], "request_timeout")

    @patch("agentuniverse.agent.action.tool.common_tool.world_bank_indicators_tool.requests.get")
    def test_request_error_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.ConnectionError("offline")

        result = self.tool.execute(country="CHN", indicator="population")

        self.assertEqual(result["error"]["type"], "request_error")
        self.assertIn("offline", result["error"]["message"])

    def test_invalid_local_arguments_fail_before_request(self) -> None:
        with self.assertRaisesRegex(ValueError, "mode must be one of"):
            self.tool.execute(mode="search")
        with self.assertRaisesRegex(ValueError, "country must"):
            self.tool.execute(country="CN", indicator="population")
        with self.assertRaisesRegex(ValueError, "duplicates"):
            self.tool.execute(country="CHN;CHN", indicator="population")
        with self.assertRaisesRegex(ValueError, "indicator is required"):
            self.tool.execute(country="CHN")
        with self.assertRaisesRegex(ValueError, "indicator must be"):
            self.tool.execute(country="CHN", indicator="bad value!")
        with self.assertRaisesRegex(ValueError, "between 1 and 50"):
            self.tool.execute(mode="catalog", max_results=0)
        with self.assertRaisesRegex(ValueError, "between 1 and 1000"):
            self.tool.execute(mode="catalog", page=1001)
        with self.assertRaisesRegex(ValueError, "not be later"):
            self.tool.execute(country="CHN", indicator="population", start_year=2025, end_year=2024)
        with self.assertRaisesRegex(ValueError, "must not exceed 20 years"):
            self.tool.execute(country="CHN", indicator="population", start_year=2000, end_year=2020)

    def test_component_yaml_describes_the_implementation(self) -> None:
        config_path = Path(__file__).parents[6] / "agentuniverse" / "agent" / "action" / "tool" / "common_tool" / "world_bank_indicators_tool.yaml"
        with config_path.open(encoding="utf-8") as stream:
            config = yaml.safe_load(stream)

        self.assertEqual(config["name"], "world_bank_indicators_tool")
        self.assertEqual(config["metadata"]["class"], "WorldBankIndicatorsTool")
        self.assertEqual(config["input_keys"], ["mode"])
        self.assertEqual(config["args_model_schema"]["properties"]["mode"]["enum"], ["series", "country", "catalog"])


if __name__ == "__main__":
    unittest.main()
