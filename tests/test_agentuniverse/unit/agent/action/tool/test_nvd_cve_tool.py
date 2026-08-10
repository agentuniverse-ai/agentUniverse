#!/usr/bin/env python3

import copy
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.nvd_cve_tool import NvdCveTool
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

SAMPLE_CVE = {
    "cve": {
        "id": "CVE-2021-44228",
        "sourceIdentifier": "security@apache.org",
        "published": "2021-12-10T10:15:09.143",
        "lastModified": "2025-10-21T17:00:00.000",
        "vulnStatus": "Analyzed",
        "descriptions": [
            {"lang": "es", "value": "Descripcion"},
            {"lang": "en", "value": "A remote code execution vulnerability."},
        ],
        "metrics": {
            "cvssMetricV31": [
                {
                    "source": "nvd@nist.gov",
                    "type": "Primary",
                    "cvssData": {
                        "version": "3.1",
                        "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                        "baseScore": 10.0,
                        "baseSeverity": "CRITICAL",
                    },
                    "exploitabilityScore": 3.9,
                    "impactScore": 6.0,
                }
            ]
        },
        "weaknesses": [
            {"description": [{"lang": "en", "value": "CWE-917"}]},
        ],
        "references": [
            {
                "url": "https://logging.apache.org/log4j/2.x/security.html",
                "source": "security@apache.org",
                "tags": ["Vendor Advisory", "Patch"],
            }
        ],
        "configurations": [
            {
                "nodes": [
                    {
                        "operator": "OR",
                        "cpeMatch": [
                            {
                                "vulnerable": True,
                                "criteria": "cpe:2.3:a:apache:log4j:2.14.1:*:*:*:*:*:*:*",
                                "matchCriteriaId": "MATCH-1",
                                "versionEndExcluding": "2.15.0",
                            }
                        ],
                    }
                ]
            }
        ],
        "cveTags": [{"sourceIdentifier": "security@apache.org", "tags": ["disputed"]}],
        "cisaExploitAdd": "2021-12-10",
        "cisaActionDue": "2021-12-24",
        "cisaRequiredAction": "Apply updates per vendor instructions.",
        "cisaVulnerabilityName": "Apache Log4j2 Remote Code Execution",
    }
}


def response_mock(*, json_data=None, status_code=200, headers=None):
    response = Mock(status_code=status_code, headers=headers or {})
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class NvdCveToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = NvdCveTool(api_key="test-nvd-key")

    @patch("agentuniverse.agent.action.tool.common_tool.nvd_cve_tool.requests.get")
    def test_keyword_search_returns_normalized_metadata(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "resultsPerPage": 5,
                "startIndex": 0,
                "totalResults": 12,
                "vulnerabilities": [SAMPLE_CVE],
            }
        )

        result = self.tool.execute(query="remote code execution", max_results=5)

        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["total_results"], 12)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["next_start_index"], 5)
        self.assertIn("not endorsed", result["source"]["notice"])
        cve = result["cves"][0]
        self.assertEqual(cve["id"], "CVE-2021-44228")
        self.assertEqual(cve["description"], "A remote code execution vulnerability.")
        self.assertEqual(cve["cvss"]["version"], "3.1")
        self.assertEqual(cve["cvss"]["base_score"], 10.0)
        self.assertEqual(cve["weaknesses"], ["CWE-917"])
        self.assertEqual(cve["references"][0]["tags"], ["Vendor Advisory", "Patch"])
        self.assertTrue(cve["affected_products"][0]["vulnerable"])
        self.assertEqual(cve["affected_products"][0]["version_end_excluding"], "2.15.0")
        self.assertEqual(cve["tags"], ["disputed"])
        self.assertTrue(cve["known_exploited"])
        self.assertEqual(cve["kev"]["date_added"], "2021-12-10")
        self.assertEqual(cve["nvd_url"], "https://nvd.nist.gov/vuln/detail/CVE-2021-44228")

        request = mock_get.call_args
        self.assertEqual(request.args[0], NvdCveTool.BASE_URL)
        self.assertEqual(request.kwargs["params"]["keywordSearch"], "remote code execution")
        self.assertEqual(request.kwargs["params"]["resultsPerPage"], 5)
        self.assertEqual(request.kwargs["params"]["startIndex"], 0)
        self.assertEqual(request.kwargs["headers"]["apiKey"], "test-nvd-key")
        self.assertEqual(request.kwargs["timeout"], 20.0)

    @patch("agentuniverse.agent.action.tool.common_tool.nvd_cve_tool.requests.get")
    def test_exact_keyword_search_and_pagination(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "resultsPerPage": 10,
                "startIndex": 10,
                "totalResults": 11,
                "vulnerabilities": [SAMPLE_CVE],
            }
        )

        result = self.tool.execute(
            query="Apache HTTP Server",
            max_results=10,
            start_index=10,
            exact_match=True,
        )

        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["keywordExactMatch"], "")
        self.assertEqual(params["startIndex"], 10)
        self.assertIsNone(result["next_start_index"])

    @patch("agentuniverse.agent.action.tool.common_tool.nvd_cve_tool.requests.get")
    def test_cve_lookup_normalizes_identifier_and_requests_one_record(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "resultsPerPage": 1,
                "startIndex": 0,
                "totalResults": 1,
                "vulnerabilities": [SAMPLE_CVE],
            }
        )

        result = self.tool.execute(query="cve-2021-44228", max_results=20, start_index=40)

        self.assertEqual(result["mode"], "cve")
        self.assertEqual(result["query"], "CVE-2021-44228")
        self.assertEqual(result["max_results"], 1)
        self.assertEqual(result["start_index"], 0)
        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["cveIds"], "CVE-2021-44228")
        self.assertEqual(params["resultsPerPage"], 1)
        self.assertEqual(params["startIndex"], 0)
        self.assertNotIn("keywordSearch", params)

    @patch("agentuniverse.agent.action.tool.common_tool.nvd_cve_tool.requests.get")
    def test_anonymous_request_omits_api_key(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "resultsPerPage": 5,
                "startIndex": 0,
                "totalResults": 0,
                "vulnerabilities": [],
            }
        )

        result = NvdCveTool(api_key=None).execute(query="linux kernel")

        self.assertNotIn("apiKey", mock_get.call_args.kwargs["headers"])
        self.assertEqual(result["cves"], [])
        self.assertIsNone(result["next_start_index"])

    def test_invalid_input_is_rejected_before_network_access(self) -> None:
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            self.tool.execute(query=" ")
        with self.assertRaisesRegex(ValueError, "500 UTF-8 bytes"):
            self.tool.execute(query="x" * 501)
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            self.tool.execute(query="linux", max_results=0)
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            self.tool.execute(query="linux", max_results=True)
        with self.assertRaisesRegex(ValueError, "start_index"):
            self.tool.execute(query="linux", start_index=-1)
        with self.assertRaisesRegex(ValueError, "must be a boolean"):
            self.tool.execute(query="linux", exact_match="true")
        with self.assertRaisesRegex(ValueError, "keyword searches"):
            self.tool.execute(query="CVE-2021-44228", exact_match=True)

    def test_cvss_prefers_primary_v4_metric(self) -> None:
        cve = copy.deepcopy(SAMPLE_CVE)
        cve["cve"]["metrics"]["cvssMetricV40"] = [
            {
                "source": "other@example.com",
                "type": "Secondary",
                "cvssData": {"version": "4.0", "baseScore": 5.0, "baseSeverity": "MEDIUM"},
            },
            {
                "source": "nvd@nist.gov",
                "type": "Primary",
                "cvssData": {
                    "version": "4.0",
                    "baseScore": 9.3,
                    "baseSeverity": "CRITICAL",
                    "vectorString": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N",
                },
            },
        ]

        parsed = NvdCveTool._parse_vulnerability(cve)

        self.assertEqual(parsed["cvss"]["version"], "4.0")
        self.assertEqual(parsed["cvss"]["base_score"], 9.3)
        self.assertEqual(parsed["cvss"]["type"], "Primary")

    def test_rejected_record_and_missing_optional_metadata_are_safe(self) -> None:
        parsed = NvdCveTool._parse_vulnerability({"cve": {"id": "CVE-2026-9999", "vulnStatus": "Rejected"}})

        self.assertTrue(parsed["rejected"])
        self.assertEqual(parsed["description"], "")
        self.assertEqual(parsed["cvss"]["version"], "")
        self.assertEqual(parsed["weaknesses"], [])
        self.assertEqual(parsed["references"], [])
        self.assertEqual(parsed["affected_products"], [])
        self.assertFalse(parsed["known_exploited"])

    def test_nested_output_is_bounded_and_description_reports_truncation(self) -> None:
        cve = copy.deepcopy(SAMPLE_CVE)
        cve["cve"]["descriptions"] = [{"lang": "en", "value": "x" * 5000}]
        cve["cve"]["weaknesses"] = [{"description": [{"value": f"CWE-{index}"}]} for index in range(30)]
        cve["cve"]["references"] = [{"url": f"https://example.com/{index}"} for index in range(30)]
        cve["cve"]["configurations"] = [
            {
                "nodes": [
                    {
                        "cpeMatch": [
                            {"criteria": f"cpe:2.3:a:vendor:product:{index}:*:*:*:*:*:*:*"} for index in range(40)
                        ]
                    }
                ]
            }
        ]

        parsed = NvdCveTool._parse_vulnerability(cve)

        self.assertEqual(len(parsed["description"]), 4000)
        self.assertTrue(parsed["description_truncated"])
        self.assertEqual(len(parsed["weaknesses"]), 20)
        self.assertEqual(len(parsed["references"]), 20)
        self.assertEqual(len(parsed["affected_products"]), 30)

    @patch("agentuniverse.agent.action.tool.common_tool.nvd_cve_tool.requests.get")
    def test_timeout_and_connection_errors_are_structured(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")
        timeout_result = self.tool.execute(query="linux", start_index=25)
        self.assertEqual(timeout_result["error"]["type"], "request_timeout")
        self.assertEqual(timeout_result["start_index"], 25)

        mock_get.side_effect = requests.ConnectionError("failed with key test-nvd-key at https://services.nvd.nist.gov")
        connection_result = self.tool.execute(query="linux")
        self.assertEqual(connection_result["error"]["type"], "request_error")
        self.assertNotIn("test-nvd-key", str(connection_result))

    @patch("agentuniverse.agent.action.tool.common_tool.nvd_cve_tool.requests.get")
    def test_rate_limit_error_uses_safe_nvd_headers(self, mock_get: Mock) -> None:
        response = Mock(
            status_code=429,
            headers={"message": "Rate limit exceeded", "Retry-After": "30"},
        )
        mock_get.side_effect = requests.HTTPError(response=response)

        result = self.tool.execute(query="linux")

        self.assertEqual(result["error"]["type"], "rate_limited")
        self.assertEqual(result["error"]["status_code"], 429)
        self.assertEqual(result["error"]["retry_after"], "30")
        self.assertIn("Rate limit exceeded", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.nvd_cve_tool.requests.get")
    def test_http_error_message_is_bounded(self, mock_get: Mock) -> None:
        response = Mock(status_code=400, headers={"message": "x" * 1000})
        mock_get.side_effect = requests.HTTPError(response=response)

        result = self.tool.execute(query="linux")

        self.assertEqual(result["error"]["type"], "http_error")
        self.assertLessEqual(len(result["error"]["message"]), 500)

    @patch("agentuniverse.agent.action.tool.common_tool.nvd_cve_tool.requests.get")
    def test_invalid_json_and_response_shapes_are_structured(self, mock_get: Mock) -> None:
        invalid_json = response_mock()
        invalid_json.json.side_effect = requests.JSONDecodeError("invalid JSON", "", 0)
        mock_get.return_value = invalid_json
        json_result = self.tool.execute(query="linux")
        self.assertEqual(json_result["error"]["type"], "invalid_response")
        self.assertIn("invalid NVD JSON response", json_result["error"]["message"])

        mock_get.return_value = response_mock(json_data={"vulnerabilities": "bad"})
        shape_result = self.tool.execute(query="linux")
        self.assertEqual(shape_result["error"]["type"], "invalid_response")

        mock_get.return_value = response_mock(
            json_data={
                "resultsPerPage": 5,
                "startIndex": 0,
                "totalResults": 1,
                "vulnerabilities": [{}],
            }
        )
        cve_result = self.tool.execute(query="linux")
        self.assertIn("must contain a CVE object", cve_result["error"]["message"])

    def test_shipped_config_documents_and_initializes_contract(self) -> None:
        config_path = (
            Path(__file__).resolve().parents[6]
            / "examples"
            / "sample_standard_app"
            / "intelligence"
            / "agentic"
            / "tool"
            / "buildin"
            / "nvd_cve_tool.yaml"
        )
        with config_path.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.assertEqual(config["input_keys"], ["query"])
        description = config["description"]
        for parameter in ("query", "max_results", "start_index", "exact_match"):
            self.assertIn(parameter, description)
        for field in ("CVSS", "CWE", "CPE", "KEV", "NVD_API_KEY", "description_truncated"):
            self.assertIn(field, description)

        configer = Configer(str(config_path)).load()
        tool_configer = ToolConfiger(configer).load_by_configer(configer)
        tool = NvdCveTool(api_key=None).initialize_by_component_configer(tool_configer)
        self.assertEqual(tool.name, "nvd_cve_tool")
        self.assertEqual(tool.input_keys, ["query"])


if __name__ == "__main__":
    unittest.main()
