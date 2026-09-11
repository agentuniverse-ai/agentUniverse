#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""World Bank Indicators API integration for agent workflows.

The World Bank's public V2 Indicators API needs no credentials.  This tool
keeps responses useful for an LLM by exposing a small, bounded surface:
country metadata, a browsable indicator catalogue, and time-series values.
"""

import re
from datetime import date
from typing import Any, ClassVar, Dict, List, Optional, Tuple
from urllib.parse import quote

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool


class _WorldBankAPIError(Exception):
    """Raised when the World Bank API returns a structured error response."""


class WorldBankIndicatorsTool(Tool):
    """Browse World Development Indicators and retrieve country time series.

    ``series`` accepts either a World Bank indicator code or one of the common
    aliases in :attr:`INDICATOR_ALIASES`.  The API's unbounded historical
    output is deliberately constrained by result, page, country, and year
    limits before a request is made.
    """

    MODES: ClassVar[set[str]] = {"series", "country", "catalog"}
    INDICATOR_ALIASES: ClassVar[Dict[str, str]] = {
        "gdp_growth": "NY.GDP.MKTP.KD.ZG",
        "gdp_current_usd": "NY.GDP.MKTP.CD",
        "inflation": "FP.CPI.TOTL.ZG",
        "unemployment": "SL.UEM.TOTL.ZS",
        "population": "SP.POP.TOTL",
        "life_expectancy": "SP.DYN.LE00.IN",
        "co2_emissions": "EN.ATM.CO2E.KT",
        "trade_percent_gdp": "NE.TRD.GNFS.ZS",
    }
    MAX_RESULTS: ClassVar[int] = 50
    MAX_PAGE: ClassVar[int] = 1000
    MAX_COUNTRIES: ClassVar[int] = 5
    MAX_YEAR_SPAN: ClassVar[int] = 20
    _COUNTRY_CODE_RE: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z]{3}$")
    _INDICATOR_CODE_RE: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._-]{3,80}$")

    name: str = "world_bank_indicators_tool"
    description: str = (
        "Query World Bank World Development Indicators without an API key. "
        "Use series for GDP, inflation, unemployment and other country time "
        "series; use country for country metadata; use catalog to browse "
        "indicator codes."
    )
    base_url: str = "https://api.worldbank.org/v2"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    user_agent: str = "agentUniverse-World-Bank-Indicators-Tool/1.0"

    def execute(
        self,
        mode: str = "series",
        country: Optional[str] = None,
        indicator: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        max_results: int = 10,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Run a bounded World Bank indicator operation.

        Args:
            mode: ``series`` (indicator values), ``country`` (country metadata),
                or ``catalog`` (World Development Indicator definitions).
            country: One ISO-3 country code, or up to five codes separated with
                commas or semicolons. Required for ``series`` and ``country``.
            indicator: An indicator code such as ``NY.GDP.MKTP.KD.ZG`` or a
                supported alias such as ``gdp_growth``. Required for ``series``.
            start_year: Inclusive start year. When only one year is supplied it
                is treated as a single-year query.
            end_year: Inclusive end year. A requested range may span 20 years.
            max_results: Results per API page, from 1 through 50.
            page: One-based API page, from 1 through 1000.

        Returns:
            A normalized dictionary. Network and remote API failures are
            returned as a structured ``error`` field; invalid local arguments
            raise ``ValueError`` before any request is sent.
        """
        normalized_mode = self._normalize_mode(mode)
        self._validate_paging(max_results, page)
        context: Dict[str, Any] = {
            "mode": normalized_mode,
            "max_results": max_results,
            "page": page,
        }

        try:
            if normalized_mode == "catalog":
                return self._catalog(context)

            countries = self._normalize_countries(country)
            context["countries"] = countries
            if normalized_mode == "country":
                return self._country(context, countries)

            indicator_code, indicator_alias = self._normalize_indicator(indicator)
            start, end = self._normalize_years(start_year, end_year)
            context.update(
                {
                    "indicator": indicator_code,
                    "indicator_alias": indicator_alias,
                    "start_year": start,
                    "end_year": end,
                }
            )
            return self._series(context, countries, indicator_code, start, end)
        except _WorldBankAPIError as exc:
            return self._error_result(context, "api_error", str(exc))
        except requests.Timeout:
            return self._error_result(context, "request_timeout", "World Bank request timed out.")
        except requests.RequestException as exc:
            return self._error_result(context, "request_error", f"World Bank request failed: {exc}")

    def _series(
        self,
        context: Dict[str, Any],
        countries: List[str],
        indicator: str,
        start_year: Optional[int],
        end_year: Optional[int],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = self._base_params(context)
        params["source"] = 2
        if start_year is not None:
            params["date"] = f"{start_year}:{end_year}"
        path = f"/country/{quote(';'.join(countries), safe=';')}/indicator/{quote(indicator, safe='.')}"
        metadata, rows = self._unpack_collection(self._get(path, params))
        observations = [self._parse_observation(row) for row in rows]
        return {
            **context,
            "total_results": self._as_int(metadata.get("total"), len(observations)),
            "total_pages": self._as_int(metadata.get("pages"), 1),
            "returned_results": len(observations),
            "last_updated": str(metadata.get("lastupdated") or ""),
            "observations": observations,
        }

    def _country(self, context: Dict[str, Any], countries: List[str]) -> Dict[str, Any]:
        path = f"/country/{quote(';'.join(countries), safe=';')}"
        metadata, rows = self._unpack_collection(self._get(path, self._base_params(context)))
        values = [self._parse_country(row) for row in rows]
        return {
            **context,
            "total_results": self._as_int(metadata.get("total"), len(values)),
            "total_pages": self._as_int(metadata.get("pages"), 1),
            "returned_results": len(values),
            "countries": values,
        }

    def _catalog(self, context: Dict[str, Any]) -> Dict[str, Any]:
        metadata, rows = self._unpack_collection(
            self._get("/source/2/indicator", self._base_params(context))
        )
        indicators = [
            {
                "id": str(row.get("id") or ""),
                "name": str(row.get("name") or ""),
                "source": str((row.get("source") or {}).get("value") or ""),
                "unit": str(row.get("unit") or ""),
                "source_note": str(row.get("sourceNote") or ""),
            }
            for row in rows
            if isinstance(row, dict)
        ]
        return {
            **context,
            "total_results": self._as_int(metadata.get("total"), len(indicators)),
            "total_pages": self._as_int(metadata.get("pages"), 1),
            "returned_results": len(indicators),
            "common_aliases": dict(self.INDICATOR_ALIASES),
            "indicators": indicators,
        }

    def _get(self, path: str, params: Dict[str, Any]) -> Any:
        response = requests.get(
            f"{self.base_url}{path}",
            params={"format": "json", **params},
            headers={"Accept": "application/json", "User-Agent": self.user_agent},
            timeout=self.timeout,
        )
        response.raise_for_status()
        try:
            return response.json()
        except ValueError as exc:
            raise _WorldBankAPIError("World Bank returned an invalid JSON response.") from exc

    @staticmethod
    def _unpack_collection(payload: Any) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        if not isinstance(payload, list) or not payload:
            raise _WorldBankAPIError("World Bank returned an unexpected response format.")
        metadata = payload[0]
        if not isinstance(metadata, dict):
            raise _WorldBankAPIError("World Bank returned invalid response metadata.")
        if metadata.get("message"):
            messages = metadata["message"]
            if isinstance(messages, list):
                detail = "; ".join(
                    str(item.get("value") or item.get("message") or item)
                    for item in messages
                    if isinstance(item, dict)
                )
            else:
                detail = str(messages)
            raise _WorldBankAPIError(detail or "World Bank rejected the request.")
        rows = payload[1] if len(payload) > 1 else []
        if rows is None:
            rows = []
        if not isinstance(rows, list):
            raise _WorldBankAPIError("World Bank returned invalid collection data.")
        return metadata, rows

    @staticmethod
    def _parse_observation(row: Any) -> Dict[str, Any]:
        if not isinstance(row, dict):
            return {}
        indicator = row.get("indicator") or {}
        country = row.get("country") or {}
        return {
            "country_code": str(row.get("countryiso3code") or country.get("id") or ""),
            "country": str(country.get("value") or ""),
            "indicator_code": str(indicator.get("id") or ""),
            "indicator": str(indicator.get("value") or ""),
            "year": str(row.get("date") or ""),
            "value": row.get("value"),
            "unit": str(row.get("unit") or ""),
            "decimal": row.get("decimal"),
            "observation_status": str(row.get("obs_status") or ""),
        }

    @staticmethod
    def _parse_country(row: Any) -> Dict[str, Any]:
        if not isinstance(row, dict):
            return {}
        return {
            "id": str(row.get("id") or ""),
            "iso2_code": str(row.get("iso2Code") or ""),
            "name": str(row.get("name") or ""),
            "region": str((row.get("region") or {}).get("value") or ""),
            "income_level": str((row.get("incomeLevel") or {}).get("value") or ""),
            "lending_type": str((row.get("lendingType") or {}).get("value") or ""),
            "capital_city": str(row.get("capitalCity") or ""),
            "longitude": str(row.get("longitude") or ""),
            "latitude": str(row.get("latitude") or ""),
        }

    @staticmethod
    def _base_params(context: Dict[str, Any]) -> Dict[str, Any]:
        return {"per_page": context["max_results"], "page": context["page"]}

    @classmethod
    def _normalize_mode(cls, mode: Any) -> str:
        value = mode.strip().lower() if isinstance(mode, str) else ""
        if value not in cls.MODES:
            raise ValueError("mode must be one of: series, country, catalog")
        return value

    @classmethod
    def _normalize_countries(cls, country: Any) -> List[str]:
        if not isinstance(country, str) or not country.strip():
            raise ValueError("country must contain at least one ISO-3 country code")
        values = [item.strip().upper() for item in re.split(r"[;,]", country) if item.strip()]
        if not values or len(values) > cls.MAX_COUNTRIES:
            raise ValueError(f"country must contain between 1 and {cls.MAX_COUNTRIES} ISO-3 codes")
        if len(set(values)) != len(values):
            raise ValueError("country codes must not contain duplicates")
        if any(not cls._COUNTRY_CODE_RE.fullmatch(value) for value in values):
            raise ValueError("country must use ISO-3 alphabetic codes, for example CHN or USA")
        return values

    @classmethod
    def _normalize_indicator(cls, indicator: Any) -> Tuple[str, str]:
        if not isinstance(indicator, str) or not indicator.strip():
            raise ValueError("indicator is required for series mode")
        value = indicator.strip()
        alias = value.lower()
        if alias in cls.INDICATOR_ALIASES:
            return cls.INDICATOR_ALIASES[alias], alias
        if not cls._INDICATOR_CODE_RE.fullmatch(value):
            raise ValueError("indicator must be a supported alias or a valid World Bank indicator code")
        return value.upper(), ""

    @classmethod
    def _normalize_years(cls, start_year: Any, end_year: Any) -> Tuple[Optional[int], Optional[int]]:
        if start_year is None and end_year is None:
            return None, None
        if start_year is None:
            start_year = end_year
        if end_year is None:
            end_year = start_year
        for label, value in (("start_year", start_year), ("end_year", end_year)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{label} must be a whole year")
            if value < 1960 or value > date.today().year:
                raise ValueError(f"{label} must be between 1960 and {date.today().year}")
        if start_year > end_year:
            raise ValueError("start_year must not be later than end_year")
        if end_year - start_year + 1 > cls.MAX_YEAR_SPAN:
            raise ValueError(f"year range must not exceed {cls.MAX_YEAR_SPAN} years")
        return start_year, end_year

    @classmethod
    def _validate_paging(cls, max_results: Any, page: Any) -> None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError("max_results must be an integer")
        if not 1 <= max_results <= cls.MAX_RESULTS:
            raise ValueError(f"max_results must be between 1 and {cls.MAX_RESULTS}")
        if isinstance(page, bool) or not isinstance(page, int):
            raise ValueError("page must be an integer")
        if not 1 <= page <= cls.MAX_PAGE:
            raise ValueError(f"page must be between 1 and {cls.MAX_PAGE}")

    @staticmethod
    def _as_int(value: Any, fallback: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return fallback

    @staticmethod
    def _error_result(context: Dict[str, Any], error_type: str, message: str) -> Dict[str, Any]:
        return {**context, "error": {"type": error_type, "message": message}}
