#!/usr/bin/env python3
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.gitlab_tool import GitLabTool
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer


def response_mock(data, total=None):
    response = Mock()
    response.json.return_value = data
    response.raise_for_status.return_value = None
    response.headers = {"X-Total": str(total)} if total is not None else {}
    return response


class GitLabToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = GitLabTool(access_token="secret")  # noqa: S106

    @patch("agentuniverse.agent.action.tool.common_tool.gitlab_tool.requests.get")
    def test_projects_search(self, get):
        get.return_value = response_mock(
            [
                {
                    "id": 1,
                    "name": "Demo",
                    "path": "demo",
                    "path_with_namespace": "group/demo",
                    "web_url": "https://gitlab.com/group/demo",
                    "namespace": {"full_path": "group"},
                    "star_count": 3,
                }
            ],
            total=12,
        )
        result = self.tool.execute(query="agent", max_results=2, page=2, sort="star_count")
        self.assertEqual(result["total_results"], 12)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["projects"][0]["name"], "Demo")
        self.assertEqual(
            get.call_args.kwargs["params"],
            {"search": "agent", "page": 2, "per_page": 2, "order_by": "star_count", "sort": "desc"},
        )
        self.assertEqual(get.call_args.kwargs["headers"]["PRIVATE-TOKEN"], "secret")

    @patch("agentuniverse.agent.action.tool.common_tool.gitlab_tool.requests.get")
    def test_project_and_issue_modes(self, get):
        get.return_value = response_mock({"id": 4, "name": "Demo", "path": "demo"})
        project = self.tool.execute(query="group/demo", mode="project")
        self.assertEqual(project["page"], 1)
        self.assertEqual(get.call_args.args[0], "https://gitlab.com/api/v4/projects/group%2Fdemo")
        project_encoded = self.tool.execute(query="group%2Fdemo", mode="project")
        self.assertEqual(project_encoded["page"], 1)
        self.assertEqual(get.call_args.args[0], "https://gitlab.com/api/v4/projects/group%2Fdemo")
        get.return_value = response_mock(
            [{"id": 8, "iid": 2, "title": "Bug", "state": "opened", "labels": ["bug"], "author": {"username": "u"}}],
            total=7,
        )
        issues = self.tool.execute(
            query="4", mode="issues", state="all", labels="bug", issue_search="Bug", sort="updated_at"
        )
        self.assertEqual(issues["issues"][0]["title"], "Bug")
        self.assertEqual(issues["total_results"], 7)
        self.assertEqual(get.call_args.kwargs["params"]["labels"], "bug")
        self.assertEqual(get.call_args.kwargs["params"]["search"], "Bug")

    def test_validation(self):
        with self.assertRaisesRegex(ValueError, "query must not be empty"):
            self.tool.execute(query="")
        with self.assertRaisesRegex(ValueError, "mode must be one of"):
            self.tool.execute(query="x", mode="users")
        with self.assertRaisesRegex(ValueError, "state must be one of"):
            self.tool.execute(query="x", mode="issues", state="new")
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            self.tool.execute(query="x", max_results=21)

    @patch("agentuniverse.agent.action.tool.common_tool.gitlab_tool.requests.get")
    def test_irrelevant_state_is_not_validated_for_project_modes(self, get):
        get.return_value = response_mock({"id": 1, "name": "Demo", "path": "demo"})
        result = self.tool.execute(query="1", mode="project", state="not-applicable")
        self.assertEqual(result["returned_results"], 1)

    @patch("agentuniverse.agent.action.tool.common_tool.gitlab_tool.requests.get")
    def test_errors(self, get):
        get.side_effect = requests.Timeout()
        self.assertEqual(self.tool.execute(query="x")["error"]["type"], "request_timeout")
        response = Mock(status_code=404)
        get.side_effect = requests.HTTPError(response=response)
        self.assertEqual(self.tool.execute(query="x")["error"]["type"], "http_error")

    @patch("agentuniverse.agent.action.tool.common_tool.gitlab_tool.requests.get")
    def test_malformed_nested_response_is_structured(self, get):
        get.return_value = response_mock({"id": 1, "name": "Demo", "namespace": "invalid"})
        result = self.tool.execute(query="1", mode="project")
        self.assertEqual(result["error"]["type"], "invalid_response")

    def test_yaml_config(self):
        path = (
            Path(__file__).resolve().parents[6]
            / "examples/sample_standard_app/intelligence/agentic/tool/buildin/gitlab_tool.yaml"
        )
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(config["metadata"]["class"], "GitLabTool")
        tool_config = ToolConfiger(Configer(str(path)).load()).load()
        tool = GitLabTool().initialize_by_component_configer(tool_config)
        self.assertEqual(tool.input_keys, ["query"])


if __name__ == "__main__":
    unittest.main()
