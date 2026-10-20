#!/usr/bin/env python3

"""Bounded vulnerability discovery through the NVD CVE API 2.0."""

import re
from typing import Any, ClassVar, NoReturn

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class NvdCveTool(Tool):
    """Search NVD vulnerabilities by keyword or retrieve one CVE record."""

    BASE_URL: ClassVar[str] = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    SOURCE_URL: ClassVar[str] = "https://nvd.nist.gov/developers/vulnerabilities"
    NOTICE: ClassVar[str] = "This product uses data from the NVD API but is not endorsed or certified by the NVD."
    CVE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"CVE-\d{4}-\d{4,}", re.IGNORECASE)
    MAX_QUERY_BYTES: ClassVar[int] = 500
    MAX_RESULTS: ClassVar[int] = 20
    MAX_START_INDEX: ClassVar[int] = 10_000_000
    MAX_DESCRIPTION_CHARS: ClassVar[int] = 4000
    MAX_REFERENCES: ClassVar[int] = 20
    MAX_WEAKNESSES: ClassVar[int] = 20
    MAX_AFFECTED_PRODUCTS: ClassVar[int] = 30
    MAX_TAGS: ClassVar[int] = 10
    MAX_ERROR_CHARS: ClassVar[int] = 500

    timeout: float = Field(default=20.0, gt=0, le=120, description="HTTP request timeout in seconds")
    api_key: str | None = Field(default_factory=lambda: get_from_env("NVD_API_KEY"))

    def execute(
        self,
        query: str,
        max_results: int = 5,
        start_index: int = 0,
        exact_match: bool = False,
    ) -> dict[str, Any]:
        """Search the NVD or retrieve a specific CVE.

        Args:
            query: A CVE identifier or vulnerability-description keywords.
            max_results: Number of records to return, from 1 to 20.
            start_index: Zero-based NVD pagination offset.
            exact_match: Require an exact keyword phrase. Keyword searches only.

        Returns:
            A normalized, bounded list of CVE records and pagination context.
            Network and response failures are returned in ``error``.

        Raises:
            ValueError: If an input parameter is invalid.
        """
        context, params = self._build_request_context(
            query,
            max_results,
            start_index,
            exact_match,
        )

        try:
            data = self._request(params)
            return self._parse_response(data, context)
        except requests.Timeout:
            return self._error_result(
                **context,
                error_type="request_timeout",
                message="NVD request timed out.",
            )
        except requests.HTTPError as exc:
            return self._http_error_result(context, exc.response)
        except requests.RequestException:
            return self._error_result(
                **context,
                error_type="request_error",
                message="NVD request failed.",
            )
        except (KeyError, TypeError, ValueError) as exc:
            return self._error_result(
                **context,
                error_type="invalid_response",
                message=f"Unable to parse NVD response: {exc}",
            )

    @classmethod
    def _build_request_context(
        cls,
        query: str,
        max_results: int,
        start_index: int,
        exact_match: bool,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        normalized_query = cls._normalize_query(query)
        cls._validate_max_results(max_results)
        cls._validate_start_index(start_index)
        cls._validate_bool(exact_match, "exact_match")
        is_cve_lookup = cls.CVE_PATTERN.fullmatch(normalized_query) is not None
        if is_cve_lookup and exact_match:
            cls._invalid("exact_match is only supported for keyword searches")
        if is_cve_lookup:
            normalized_query = normalized_query.upper()

        context = {
            "mode": "cve" if is_cve_lookup else "search",
            "query": normalized_query,
            "max_results": 1 if is_cve_lookup else max_results,
            "start_index": 0 if is_cve_lookup else start_index,
            "exact_match": False if is_cve_lookup else exact_match,
        }
        params: dict[str, Any] = {
            "resultsPerPage": 1 if is_cve_lookup else max_results,
            "startIndex": 0 if is_cve_lookup else start_index,
        }
        if is_cve_lookup:
            params["cveIds"] = normalized_query
        else:
            params["keywordSearch"] = normalized_query
            if exact_match:
                params["keywordExactMatch"] = ""
        return context, params

    @classmethod
    def _parse_response(cls, data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        raw_vulnerabilities = data.get("vulnerabilities")
        if not isinstance(raw_vulnerabilities, list):
            cls._invalid("invalid NVD vulnerabilities response")
        cves = [cls._parse_vulnerability(item) for item in raw_vulnerabilities]
        total_results = cls._safe_non_negative_int(data.get("totalResults"))
        response_start = cls._safe_non_negative_int(data.get("startIndex"))
        response_page_size = cls._safe_non_negative_int(data.get("resultsPerPage"))
        next_start_index = response_start + response_page_size
        if next_start_index >= total_results or not raw_vulnerabilities or response_page_size == 0:
            next_start_index = None
        return {
            **context,
            "total_results": total_results,
            "returned_results": len(cves),
            "next_start_index": next_start_index,
            "cves": cves,
            "source": cls._source_metadata(),
        }

    def _request(self, params: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "agentUniverse-NvdCveTool/1.0",
        }
        if self.api_key:
            headers["apiKey"] = self.api_key
        response = requests.get(
            self.BASE_URL,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        try:
            data = response.json()
        except requests.JSONDecodeError as exc:
            self._invalid("invalid NVD JSON response", cause=exc)
        if not isinstance(data, dict):
            self._invalid("invalid NVD response")
        return data

    @classmethod
    def _parse_vulnerability(cls, wrapper: Any) -> dict[str, Any]:
        if not isinstance(wrapper, dict) or not isinstance(wrapper.get("cve"), dict):
            cls._invalid("vulnerability must contain a CVE object")
        cve = wrapper["cve"]
        cve_id = cls._safe_string(cve.get("id"))
        status = cls._safe_string(cve.get("vulnStatus"))
        description = cls._preferred_description(cve.get("descriptions"))
        return {
            "id": cve_id,
            "source_identifier": cls._safe_string(cve.get("sourceIdentifier")),
            "published": cls._safe_string(cve.get("published")),
            "last_modified": cls._safe_string(cve.get("lastModified")),
            "status": status,
            "rejected": status.upper() == "REJECTED",
            "description": description[: cls.MAX_DESCRIPTION_CHARS],
            "description_truncated": len(description) > cls.MAX_DESCRIPTION_CHARS,
            "cvss": cls._parse_cvss(cve.get("metrics")),
            "weaknesses": cls._parse_weaknesses(cve.get("weaknesses")),
            "references": cls._parse_references(cve.get("references")),
            "affected_products": cls._parse_affected_products(cve.get("configurations")),
            "tags": cls._parse_tags(cve.get("cveTags")),
            "known_exploited": bool(cve.get("cisaExploitAdd")),
            "kev": {
                "date_added": cls._safe_string(cve.get("cisaExploitAdd")),
                "action_due": cls._safe_string(cve.get("cisaActionDue")),
                "required_action": cls._safe_string(cve.get("cisaRequiredAction")),
                "vulnerability_name": cls._safe_string(cve.get("cisaVulnerabilityName")),
            },
            "nvd_url": f"https://nvd.nist.gov/vuln/detail/{cve_id}" if cve_id else "",
        }

    @classmethod
    def _preferred_description(cls, raw_descriptions: Any) -> str:
        descriptions = raw_descriptions if isinstance(raw_descriptions, list) else []
        valid = [item for item in descriptions if isinstance(item, dict) and isinstance(item.get("value"), str)]
        for item in valid:
            if cls._safe_string(item.get("lang")).lower() == "en":
                return item["value"]
        return valid[0]["value"] if valid else ""

    @classmethod
    def _parse_cvss(cls, raw_metrics: Any) -> dict[str, Any]:
        metrics = raw_metrics if isinstance(raw_metrics, dict) else {}
        metric_groups = (
            ("cvssMetricV40", "4.0"),
            ("cvssMetricV31", "3.1"),
            ("cvssMetricV30", "3.0"),
            ("cvssMetricV2", "2.0"),
        )
        for key, fallback_version in metric_groups:
            entries = metrics.get(key)
            if not isinstance(entries, list):
                continue
            candidates = [entry for entry in entries if isinstance(entry, dict)]
            if not candidates:
                continue
            metric = next(
                (entry for entry in candidates if cls._safe_string(entry.get("type")).lower() == "primary"),
                candidates[0],
            )
            data = metric.get("cvssData")
            if not isinstance(data, dict):
                continue
            return {
                "version": cls._safe_string(data.get("version")) or fallback_version,
                "base_score": cls._safe_float(data.get("baseScore")),
                "base_severity": cls._safe_string(data.get("baseSeverity") or metric.get("baseSeverity")),
                "vector": cls._safe_string(data.get("vectorString")),
                "exploitability_score": cls._safe_float(metric.get("exploitabilityScore")),
                "impact_score": cls._safe_float(metric.get("impactScore")),
                "source": cls._safe_string(metric.get("source")),
                "type": cls._safe_string(metric.get("type")),
            }
        return {
            "version": "",
            "base_score": 0.0,
            "base_severity": "",
            "vector": "",
            "exploitability_score": 0.0,
            "impact_score": 0.0,
            "source": "",
            "type": "",
        }

    @classmethod
    def _parse_weaknesses(cls, raw_weaknesses: Any) -> list[str]:
        weaknesses = raw_weaknesses if isinstance(raw_weaknesses, list) else []
        values = []
        for weakness in weaknesses:
            if not isinstance(weakness, dict):
                continue
            descriptions = weakness.get("description")
            if not isinstance(descriptions, list):
                continue
            for item in descriptions:
                if isinstance(item, dict) and isinstance(item.get("value"), str):
                    values.append(item["value"])
        return cls._unique_strings(values, cls.MAX_WEAKNESSES)

    @classmethod
    def _parse_references(cls, raw_references: Any) -> list[dict[str, Any]]:
        references = raw_references if isinstance(raw_references, list) else []
        parsed = []
        for reference in references:
            if not isinstance(reference, dict) or not isinstance(reference.get("url"), str):
                continue
            raw_tags = reference.get("tags")
            tags = raw_tags if isinstance(raw_tags, list) else []
            parsed.append(
                {
                    "url": reference["url"],
                    "source": cls._safe_string(reference.get("source")),
                    "tags": cls._unique_strings(tags, cls.MAX_TAGS),
                }
            )
            if len(parsed) >= cls.MAX_REFERENCES:
                break
        return parsed

    @classmethod
    def _parse_affected_products(cls, raw_configurations: Any) -> list[dict[str, Any]]:
        configurations = raw_configurations if isinstance(raw_configurations, list) else []
        stack = list(reversed(configurations))
        parsed = []
        visited = 0
        while stack and len(parsed) < cls.MAX_AFFECTED_PRODUCTS and visited < 500:
            item = stack.pop()
            visited += 1
            if not isinstance(item, dict):
                continue
            for child_key in ("nodes", "children"):
                children = item.get(child_key)
                if isinstance(children, list):
                    stack.extend(reversed(children))
            matches = item.get("cpeMatch")
            if not isinstance(matches, list):
                continue
            for match in matches:
                if not isinstance(match, dict) or not isinstance(match.get("criteria"), str):
                    continue
                parsed.append(
                    {
                        "criteria": match["criteria"][:500],
                        "vulnerable": bool(match.get("vulnerable")),
                        "match_criteria_id": cls._safe_string(match.get("matchCriteriaId")),
                        "version_start_including": cls._safe_string(match.get("versionStartIncluding")),
                        "version_start_excluding": cls._safe_string(match.get("versionStartExcluding")),
                        "version_end_including": cls._safe_string(match.get("versionEndIncluding")),
                        "version_end_excluding": cls._safe_string(match.get("versionEndExcluding")),
                    }
                )
                if len(parsed) >= cls.MAX_AFFECTED_PRODUCTS:
                    break
        return parsed

    @classmethod
    def _parse_tags(cls, raw_tags: Any) -> list[str]:
        tag_groups = raw_tags if isinstance(raw_tags, list) else []
        values = []
        for group in tag_groups:
            if not isinstance(group, dict) or not isinstance(group.get("tags"), list):
                continue
            values.extend(group["tags"])
        return cls._unique_strings(values, cls.MAX_TAGS)

    @classmethod
    def _normalize_query(cls, query: Any) -> str:
        normalized = query.strip() if isinstance(query, str) else ""
        if not normalized:
            cls._invalid("query must not be empty")
        if len(normalized.encode("utf-8")) > cls.MAX_QUERY_BYTES:
            cls._invalid(f"query must be at most {cls.MAX_QUERY_BYTES} UTF-8 bytes")
        return normalized

    @classmethod
    def _validate_max_results(cls, value: Any) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= cls.MAX_RESULTS:
            cls._invalid(f"max_results must be an integer between 1 and {cls.MAX_RESULTS}")

    @classmethod
    def _validate_start_index(cls, value: Any) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= cls.MAX_START_INDEX:
            cls._invalid(f"start_index must be an integer between 0 and {cls.MAX_START_INDEX}")

    @classmethod
    def _validate_bool(cls, value: Any, field_name: str) -> None:
        if not isinstance(value, bool):
            cls._invalid(f"{field_name} must be a boolean")

    @staticmethod
    def _invalid(message: str, cause: Exception | None = None) -> NoReturn:
        if cause is None:
            raise ValueError(message)
        raise ValueError(message) from cause

    @classmethod
    def _safe_non_negative_int(cls, value: Any) -> int:
        if isinstance(value, bool):
            cls._invalid("pagination values must be non-negative integers")
        try:
            parsed = int(value)
        except (TypeError, ValueError) as exc:
            cls._invalid("pagination values must be non-negative integers", cause=exc)
        if parsed < 0:
            cls._invalid("pagination values must be non-negative integers")
        return parsed

    @staticmethod
    def _safe_string(value: Any) -> str:
        return value if isinstance(value, str) else ""

    @staticmethod
    def _safe_float(value: Any) -> float:
        if isinstance(value, bool):
            return 0.0
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    @classmethod
    def _unique_strings(cls, values: list[Any], limit: int) -> list[str]:
        result = []
        seen = set()
        for value in values:
            if not isinstance(value, str) or value in seen:
                continue
            seen.add(value)
            result.append(value)
            if len(result) >= limit:
                break
        return result

    @classmethod
    def _http_error_result(cls, context: dict[str, Any], response: Any) -> dict[str, Any]:
        status_code = getattr(response, "status_code", None)
        headers = getattr(response, "headers", {}) or {}
        detail = headers.get("message") if hasattr(headers, "get") else None
        detail = str(detail)[: cls.MAX_ERROR_CHARS] if detail else ""
        retry_after = headers.get("Retry-After") if hasattr(headers, "get") else None
        if status_code in {403, 429}:
            message = "NVD rate limit or access policy rejected the request."
            error_type = "rate_limited"
        else:
            message = f"NVD returned HTTP status {status_code}." if status_code else "NVD HTTP request failed."
            error_type = "http_error"
        if detail:
            message = f"{message} NVD message: {detail}"
        message = message[: cls.MAX_ERROR_CHARS]
        return cls._error_result(
            **context,
            error_type=error_type,
            message=message,
            status_code=status_code,
            retry_after=str(retry_after)[:100] if retry_after is not None else "",
        )

    @classmethod
    def _source_metadata(cls) -> dict[str, str]:
        return {"name": "NVD", "url": cls.SOURCE_URL, "notice": cls.NOTICE}

    @classmethod
    def _error_result(
        cls,
        mode: str,
        query: str,
        max_results: int,
        start_index: int,
        exact_match: bool,
        error_type: str,
        message: str,
        status_code: int | None = None,
        retry_after: str = "",
    ) -> dict[str, Any]:
        return {
            "mode": mode,
            "query": query,
            "max_results": max_results,
            "start_index": start_index,
            "exact_match": exact_match,
            "total_results": 0,
            "returned_results": 0,
            "next_start_index": None,
            "cves": [],
            "source": cls._source_metadata(),
            "error": {
                "type": error_type,
                "message": message,
                "status_code": status_code,
                "retry_after": retry_after,
            },
        }
