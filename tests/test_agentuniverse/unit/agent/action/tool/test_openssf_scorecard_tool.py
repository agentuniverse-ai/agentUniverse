#!/usr/bin/env python3

import copy
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.openssf_scorecard_tool import OpenSsfScorecardTool
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

SAMPLE_RESULT = {
    "date": "2026-08-08T02:15:39Z",
    "repo": {
        "name": "github.com/ossf/scorecard",
        "commit": "40c1e35996730d4fdcbdb2e6a23917a2467e29b7",
    },
    "scorecard": {
        "version": "v5.5.0",
        "commit": "c395761df6afe1a69e476bc60a013a94bcbc153f",
    },
    "score": 9.0,
    "checks": [
        {
            "name": "Maintained",
            "score": 10,
            "reason": "recent activity detected",
            "details": None,
            "documentation": {
                "short": "Determines whether the project is actively maintained.",
                "url": "https://github.com/ossf/scorecard/blob/main/docs/checks.md#maintained",
            },
        },
        {
            "name": "Token-Permissions",
            "score": 9,
            "reason": "some workflow tokens have excessive permissions",
            "details": ["Info: contents permission set to read"],
            "documentation": {
                "short": "Checks workflow token permissions.",
                "url": "javascript:alert(1)",
            },
        },
    ],
    "metadata": "analysis metadata",
}


def response_mock(*, json_data=None, status_code=200):
    response = Mock(status_code=status_code)
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class OpenSsfScorecardToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = OpenSsfScorecardTool()

    @patch("agentuniverse.agent.action.tool.common_tool.openssf_scorecard_tool.requests.get")
    def test_lookup_returns_normalized_scorecard(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=SAMPLE_RESULT)

        result = self.tool.execute(repository="ossf/scorecard")

        self.assertEqual(result["repository"], "ossf/scorecard")
        scorecard = result["scorecard_result"]
        self.assertEqual(scorecard["score"], 9.0)
        self.assertEqual(scorecard["repository"]["name"], "github.com/ossf/scorecard")
        self.assertEqual(scorecard["check_count"], 2)
        self.assertEqual(scorecard["checks"][0]["details"], [])
        self.assertEqual(scorecard["checks"][1]["details"][0], "Info: contents permission set to read")
        self.assertEqual(scorecard["checks"][1]["documentation"]["url"], "")
        self.assertTrue(scorecard["checks"][1]["documentation"]["url_omitted"])
        self.assertIn("not proof", result["source"]["interpretation_warning"])
        self.assertIn("untrusted", result["source"]["content_warning"])

        request = mock_get.call_args
        self.assertEqual(
            request.args[0],
            "https://api.securityscorecards.dev/projects/github.com/ossf/scorecard",
        )
        self.assertIsNone(request.kwargs["params"])
        self.assertEqual(request.kwargs["timeout"], 20.0)
        self.assertIn("agentUniverse", request.kwargs["headers"]["User-Agent"])

    @patch("agentuniverse.agent.action.tool.common_tool.openssf_scorecard_tool.requests.get")
    def test_github_url_and_commit_are_normalized(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=SAMPLE_RESULT)
        commit = "ABCDEF0123456789ABCDEF0123456789ABCDEF01"

        result = self.tool.execute(
            repository="https://www.github.com/ossf/scorecard.git",
            commit=commit,
        )

        self.assertEqual(result["repository"], "ossf/scorecard")
        self.assertEqual(result["commit"], commit.lower())
        self.assertEqual(mock_get.call_args.kwargs["params"], {"commit": commit.lower()})

    def test_repository_forms_are_normalized(self) -> None:
        context = OpenSsfScorecardTool._build_context(
            "github.com/ossf/scorecard",
            None,
            30,
            20,
        )
        self.assertEqual(context["repository"], "ossf/scorecard")

    def test_invalid_inputs_are_rejected_before_network_access(self) -> None:
        invalid_repositories = (
            "",
            "owner",
            "owner/..",
            "owner/repo/extra",
            "http://github.com/owner/repo",
            "https://example.com/owner/repo",
            "https://user:pass@github.com/owner/repo",
            "https://github.com/owner/repo?tab=readme",
        )
        for repository in invalid_repositories:
            with self.subTest(repository=repository), self.assertRaises(ValueError):
                self.tool.execute(repository=repository)
        with self.assertRaisesRegex(ValueError, "40-character"):
            self.tool.execute(repository="owner/repo", commit="abc")
        with self.assertRaisesRegex(ValueError, "between 1 and 50"):
            self.tool.execute(repository="owner/repo", max_checks=True)
        with self.assertRaisesRegex(ValueError, "between 0 and 50"):
            self.tool.execute(repository="owner/repo", max_details_per_check=51)

    def test_checks_and_details_are_bounded_with_visible_truncation(self) -> None:
        data = copy.deepcopy(SAMPLE_RESULT)
        data["checks"] = [
            {
                "name": f"Check-{index}",
                "score": index % 11,
                "reason": "r" * 4000,
                "details": ["d" * 4000 for _ in range(5)],
                "documentation": {"short": "s" * 4000, "url": "https://example.com"},
            }
            for index in range(6)
        ]

        parsed = OpenSsfScorecardTool._parse_result(data, max_checks=3, max_details_per_check=2)

        self.assertEqual(parsed["check_count"], 6)
        self.assertEqual(parsed["returned_check_count"], 3)
        self.assertTrue(parsed["checks_truncated"])
        first = parsed["checks"][0]
        self.assertEqual(len(first["reason"]), 3000)
        self.assertTrue(first["reason_truncated"])
        self.assertEqual(first["detail_count"], 5)
        self.assertEqual(len(first["details"]), 2)
        self.assertTrue(first["details_truncated"])
        self.assertTrue(first["documentation"]["short_truncated"])

    def test_metadata_is_bounded(self) -> None:
        data = copy.deepcopy(SAMPLE_RESULT)
        data["metadata"] = "m" * 6000

        parsed = OpenSsfScorecardTool._parse_result(data, 30, 20)

        self.assertEqual(len(parsed["metadata"]), 5000)
        self.assertTrue(parsed["metadata_truncated"])

    def test_invalid_numeric_and_detail_shapes_are_rejected(self) -> None:
        data = copy.deepcopy(SAMPLE_RESULT)
        data["score"] = "9"
        with self.assertRaisesRegex(ValueError, "score must be a number"):
            OpenSsfScorecardTool._parse_result(data, 30, 20)

        data = copy.deepcopy(SAMPLE_RESULT)
        data["score"] = float("nan")
        with self.assertRaisesRegex(ValueError, "score must be between 0 and 10"):
            OpenSsfScorecardTool._parse_result(data, 30, 20)

        data = copy.deepcopy(SAMPLE_RESULT)
        data["checks"][0]["score"] = True
        with self.assertRaisesRegex(ValueError, r"checks\[\]\.score must be a number"):
            OpenSsfScorecardTool._parse_result(data, 30, 20)

        data = copy.deepcopy(SAMPLE_RESULT)
        data["checks"][0]["details"] = "not-a-list"
        with self.assertRaisesRegex(ValueError, "details must be a list"):
            OpenSsfScorecardTool._parse_result(data, 30, 20)

    @patch("agentuniverse.agent.action.tool.common_tool.openssf_scorecard_tool.requests.get")
    def test_timeout_and_connection_errors_are_structured(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")
        timed_out = self.tool.execute(repository="ossf/scorecard")
        self.assertEqual(timed_out["error"]["type"], "request_timeout")

        mock_get.side_effect = requests.ConnectionError("internal endpoint")
        failed = self.tool.execute(repository="ossf/scorecard")
        self.assertEqual(failed["error"]["type"], "request_error")
        self.assertNotIn("internal endpoint", str(failed))

    @patch("agentuniverse.agent.action.tool.common_tool.openssf_scorecard_tool.requests.get")
    def test_http_errors_are_structured(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.HTTPError(response=Mock(status_code=404))
        missing = self.tool.execute(repository="ossf/missing")
        self.assertEqual(missing["error"]["type"], "not_found")

        mock_get.side_effect = requests.HTTPError(response=Mock(status_code=429))
        limited = self.tool.execute(repository="ossf/missing")
        self.assertEqual(limited["error"]["type"], "rate_limited")

        mock_get.side_effect = requests.HTTPError(response=Mock(status_code=503))
        unavailable = self.tool.execute(repository="ossf/missing")
        self.assertEqual(unavailable["error"]["type"], "http_error")

    @patch("agentuniverse.agent.action.tool.common_tool.openssf_scorecard_tool.requests.get")
    def test_invalid_json_and_response_shapes_are_structured(self, mock_get: Mock) -> None:
        invalid_json = response_mock()
        invalid_json.json.side_effect = requests.JSONDecodeError("invalid JSON", "", 0)
        mock_get.return_value = invalid_json
        result = self.tool.execute(repository="ossf/scorecard")
        self.assertEqual(result["error"]["type"], "invalid_response")

        mock_get.return_value = response_mock(json_data={"repo": {}, "scorecard": {}, "score": 9})
        result = self.tool.execute(repository="ossf/scorecard")
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("checks must be a list", result["error"]["message"])

    def test_shipped_config_loads_and_initializes_contract(self) -> None:
        config_path = (
            Path(__file__).resolve().parents[6]
            / "examples"
            / "sample_standard_app"
            / "intelligence"
            / "agentic"
            / "tool"
            / "buildin"
            / "openssf_scorecard_tool.yaml"
        )
        with config_path.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.assertEqual(config["input_keys"], ["repository"])
        description = config["description"]
        for parameter in ("repository", "commit", "max_checks", "max_details_per_check"):
            self.assertIn(parameter, description)
        for field in ("score", "checks", "reasons", "evidence", "documentation"):
            self.assertIn(field, description)

        configer = Configer(str(config_path)).load()
        tool_configer = ToolConfiger(configer).load_by_configer(configer)
        tool = OpenSsfScorecardTool().initialize_by_component_configer(tool_configer)
        self.assertEqual(tool.name, "openssf_scorecard_tool")
        self.assertEqual(tool.input_keys, ["repository"])


if __name__ == "__main__":
    unittest.main()
