#!/usr/bin/env python3

import copy
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool import DepsDevPackageTool
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

VERSION_RESPONSE = {
    "versionKey": {"system": "NPM", "name": "@colors/colors", "version": "1.5.0"},
    "publishedAt": "2022-01-10T06:37:39Z",
    "isDefault": False,
    "isDeprecated": True,
    "deprecatedReason": "Package maintainer deprecated this release.",
    "licenses": ["MIT"],
    "advisoryKeys": [{"id": "GHSA-qqw9-vg9x-7gx8"}],
    "links": [
        {"label": "SOURCE_REPO", "url": "https://github.com/Marak/colors.js"},
        {"label": "UNSAFE", "url": "javascript:alert(1)"},
    ],
    "slsaProvenances": [
        {
            "sourceRepository": "github.com/Marak/colors.js",
            "commit": "abc123",
            "url": "https://example.com/provenance",
            "verified": True,
        }
    ],
    "attestations": [
        {
            "type": "https://slsa.dev/provenance/v1",
            "url": "https://example.com/attestation",
            "verified": True,
            "sourceRepository": "github.com/Marak/colors.js",
            "commit": "abc123",
        }
    ],
    "registries": ["https://registry.npmjs.org", "file:///tmp/registry"],
    "relatedProjects": [
        {
            "projectKey": {"id": "github.com/Marak/colors.js"},
            "relationProvenance": "UNVERIFIED_METADATA",
            "relationType": "SOURCE_REPO",
        }
    ],
    "projectStatus": {"status": "archived", "reason": "No longer maintained."},
}

DEPENDENCY_RESPONSE = {
    "nodes": [
        {
            "versionKey": {"system": "NPM", "name": "root", "version": "1.0.0"},
            "bundled": False,
            "relation": "SELF",
            "errors": [],
        },
        {
            "versionKey": {"system": "NPM", "name": "direct", "version": "2.0.0"},
            "bundled": False,
            "relation": "DIRECT",
            "errors": ["metadata warning"],
        },
        {
            "versionKey": {"system": "NPM", "name": "indirect", "version": "3.0.0"},
            "bundled": False,
            "relation": "INDIRECT",
            "errors": [],
        },
    ],
    "edges": [
        {"fromNode": 0, "toNode": 1, "requirement": "^2.0.0"},
        {"fromNode": 1, "toNode": 2, "requirement": "~3.0.0"},
        {"fromNode": 0, "toNode": 2, "requirement": ">=3"},
    ],
    "error": "partial graph warning",
}


def response_mock(*, json_data=None, status_code=200):
    response = Mock(status_code=status_code)
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class DepsDevPackageToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = DepsDevPackageTool()

    @patch("agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool.requests.get")
    def test_version_mode_returns_normalized_metadata(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=VERSION_RESPONSE)

        result = self.tool.execute(
            name="@colors/colors",
            system="npm",
            version="1.5.0+build",
        )

        self.assertEqual(result["mode"], "version")
        version_info = result["version_info"]
        self.assertEqual(version_info["package"]["name"], "@colors/colors")
        self.assertTrue(version_info["is_deprecated"])
        self.assertEqual(version_info["licenses"], ["MIT"])
        self.assertEqual(version_info["advisories"][0]["id"], "GHSA-qqw9-vg9x-7gx8")
        self.assertEqual(len(version_info["links"]), 1)
        self.assertTrue(version_info["slsa_provenances"][0]["verified"])
        self.assertTrue(version_info["attestations"][0]["verified"])
        self.assertEqual(version_info["registries"], ["https://registry.npmjs.org"])
        self.assertEqual(version_info["related_projects"][0]["relation_type"], "SOURCE_REPO")
        self.assertEqual(version_info["project_status"]["status"], "archived")
        self.assertIn("untrusted", result["source"]["content_warning"])
        self.assertEqual(result["dependency_graph"], {})

        request = mock_get.call_args
        self.assertEqual(
            request.args[0],
            "https://api.deps.dev/v3/systems/NPM/packages/%40colors%2Fcolors/versions/1.5.0%2Bbuild",
        )
        self.assertEqual(request.kwargs["timeout"], 20.0)
        self.assertIn("agentUniverse", request.kwargs["headers"]["User-Agent"])

    @patch("agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool.requests.get")
    def test_malformed_link_preserves_other_version_metadata(self, mock_get: Mock) -> None:
        data = copy.deepcopy(VERSION_RESPONSE)
        data["links"].insert(0, {"label": "BROKEN", "url": "https://[broken"})
        mock_get.return_value = response_mock(json_data=data)

        result = self.tool.execute(name="@colors/colors", system="NPM", version="1.5.0")

        self.assertNotIn("error", result)
        info = result["version_info"]
        self.assertEqual(info["package"]["name"], "@colors/colors")
        self.assertEqual(info["licenses"], ["MIT"])
        self.assertEqual(
            info["links"],
            [{"label": "SOURCE_REPO", "label_truncated": False, "url": "https://github.com/Marak/colors.js"}],
        )
        self.assertEqual(info["link_count"], 3)
        self.assertTrue(info["links_truncated"])

    @patch("agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool.requests.get")
    def test_malformed_optional_urls_preserve_provenance_and_registry_metadata(self, mock_get: Mock) -> None:
        for url in ("https://[broken", "https://[not-an-ip]/", "https://example.com\uff0fpath"):
            with self.subTest(url=url):
                data = copy.deepcopy(VERSION_RESPONSE)
                data["slsaProvenances"][0]["url"] = url
                data["attestations"][0]["type"] = url
                data["attestations"][0]["url"] = url
                data["registries"].insert(0, url)
                mock_get.return_value = response_mock(json_data=data)

                result = self.tool.execute(name="@colors/colors", system="NPM", version="1.5.0")

                self.assertNotIn("error", result)
                info = result["version_info"]
                self.assertEqual(info["licenses"], ["MIT"])
                for field in ("slsa_provenances", "attestations"):
                    self.assertEqual(info[field][0]["url"], "")
                    self.assertEqual(info[field][0]["commit"], "abc123")
                    self.assertTrue(info[field][0]["verified"])
                self.assertEqual(info["attestations"][0]["type"], "")
                self.assertEqual(info["registries"], ["https://registry.npmjs.org"])
                self.assertEqual(info["registry_count"], 3)
                self.assertTrue(info["registries_truncated"])

    @patch("agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool.requests.get")
    def test_valid_metadata_urls_are_preserved_verbatim(self, mock_get: Mock) -> None:
        urls = [
            "http://example.org/docs",
            "https://[2001:db8::1]/package",
            "HTTPS://example.org/docs",
            "https://example.org:443/p?q=a%2Fb#fragment",
        ]
        data = copy.deepcopy(VERSION_RESPONSE)
        data["links"] = [{"label": "WEB", "url": url} for url in urls]
        mock_get.return_value = response_mock(json_data=data)

        result = self.tool.execute(name="@colors/colors", system="NPM", version="1.5.0")

        self.assertNotIn("error", result)
        info = result["version_info"]
        self.assertEqual([link["url"] for link in info["links"]], urls)
        self.assertEqual(info["link_count"], len(urls))
        self.assertFalse(info["links_truncated"])

    @patch("agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool.requests.get")
    def test_dependency_mode_preserves_indices_and_omits_dangling_edges(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=DEPENDENCY_RESPONSE)

        result = self.tool.execute(
            name="root",
            system="NPM",
            version="1.0.0",
            mode="dependencies",
            max_nodes=2,
            max_edges=10,
        )

        graph = result["dependency_graph"]
        self.assertEqual(graph["node_count"], 3)
        self.assertEqual(graph["returned_node_count"], 2)
        self.assertTrue(graph["nodes_truncated"])
        self.assertEqual([node["index"] for node in graph["nodes"]], [0, 1])
        self.assertEqual(graph["edge_count"], 3)
        self.assertEqual(graph["returned_edge_count"], 1)
        self.assertEqual(graph["edges_omitted_for_unreturned_nodes"], 2)
        self.assertEqual(graph["edges"][0]["to_node"], 1)
        self.assertEqual(graph["root_package"]["name"], "root")
        self.assertEqual(result["version_info"], {})
        self.assertTrue(mock_get.call_args.args[0].endswith("/versions/1.0.0:dependencies"))

    @patch("agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool.requests.get")
    def test_dependency_edges_respect_independent_limit(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=DEPENDENCY_RESPONSE)

        result = self.tool.execute(
            name="root",
            system="NPM",
            version="1.0.0",
            mode="dependencies",
            max_nodes=3,
            max_edges=1,
        )

        graph = result["dependency_graph"]
        self.assertEqual(graph["eligible_edge_count"], 3)
        self.assertEqual(graph["returned_edge_count"], 1)
        self.assertTrue(graph["edges_truncated"])
        self.assertEqual(graph["error_text"], "partial graph warning")

    def test_invalid_inputs_are_rejected_before_network_access(self) -> None:
        with self.assertRaisesRegex(ValueError, "name must not be empty"):
            self.tool.execute(name=" ", system="PYPI", version="1")
        with self.assertRaisesRegex(ValueError, "500 UTF-8 bytes"):
            self.tool.execute(name="x" * 501, system="PYPI", version="1")
        with self.assertRaisesRegex(ValueError, "control characters"):
            self.tool.execute(name="bad\nname", system="PYPI", version="1")
        with self.assertRaisesRegex(ValueError, "system must be one of"):
            self.tool.execute(name="pkg", system="APT", version="1")
        with self.assertRaisesRegex(ValueError, "mode must be one of"):
            self.tool.execute(name="pkg", system="PYPI", version="1", mode="requirements")
        with self.assertRaisesRegex(ValueError, "supports only"):
            self.tool.execute(name="pkg", system="GO", version="1", mode="dependencies")
        with self.assertRaisesRegex(ValueError, "between 1 and 200"):
            self.tool.execute(name="pkg", system="PYPI", version="1", max_nodes=True)
        with self.assertRaisesRegex(ValueError, "between 1 and 500"):
            self.tool.execute(name="pkg", system="PYPI", version="1", max_edges=501)

    def test_version_collections_are_bounded_and_unsafe_links_are_omitted(self) -> None:
        data = copy.deepcopy(VERSION_RESPONSE)
        data["licenses"] = [f"License-{index}" for index in range(35)]
        data["advisoryKeys"] = [{"id": f"GHSA-{index}"} for index in range(105)]
        data["links"] = [
            {"label": "UNSAFE", "url": "data:text/plain,hello"},
            *[{"label": "WEB", "url": f"https://example.com/{index}"} for index in range(35)],
        ]

        parsed = DepsDevPackageTool._parse_version_info(data)

        self.assertEqual(parsed["license_count"], 35)
        self.assertEqual(len(parsed["licenses"]), 30)
        self.assertTrue(parsed["licenses_truncated"])
        self.assertEqual(parsed["advisory_count"], 105)
        self.assertEqual(len(parsed["advisories"]), 100)
        self.assertTrue(parsed["advisories_truncated"])
        self.assertEqual(parsed["link_count"], 36)
        self.assertEqual(len(parsed["links"]), 30)
        self.assertTrue(parsed["links_truncated"])
        self.assertTrue(all(link["url"].startswith("https://") for link in parsed["links"]))

    def test_scalar_text_and_version_keys_are_bounded(self) -> None:
        data = copy.deepcopy(VERSION_RESPONSE)
        data["deprecatedReason"] = "d" * 3000
        data["versionKey"]["name"] = "n" * 3000

        parsed = DepsDevPackageTool._parse_version_info(data)

        self.assertEqual(len(parsed["deprecated_reason"]), 2000)
        self.assertTrue(parsed["deprecated_reason_truncated"])
        self.assertEqual(len(parsed["package"]["name"]), 2000)
        self.assertEqual(parsed["package"]["truncated_fields"], ["name"])
        self.assertEqual(parsed["deps_dev_url"], "")

    def test_invalid_boolean_response_field_is_rejected(self) -> None:
        data = copy.deepcopy(VERSION_RESPONSE)
        data["isDefault"] = "false"

        with self.assertRaisesRegex(ValueError, "isDefault must be a boolean"):
            DepsDevPackageTool._parse_version_info(data)

    @patch("agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool.requests.get")
    def test_timeout_and_connection_errors_are_structured(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")
        timeout_result = self.tool.execute(name="jinja2", system="PYPI", version="2.4.1")
        self.assertEqual(timeout_result["error"]["type"], "request_timeout")

        mock_get.side_effect = requests.ConnectionError("internal endpoint details")
        connection_result = self.tool.execute(name="jinja2", system="PYPI", version="2.4.1")
        self.assertEqual(connection_result["error"]["type"], "request_error")
        self.assertNotIn("internal endpoint", str(connection_result))

    @patch("agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool.requests.get")
    def test_not_found_rate_limit_and_http_errors_are_structured(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.HTTPError(response=Mock(status_code=404))
        missing = self.tool.execute(name="missing", system="PYPI", version="1")
        self.assertEqual(missing["error"]["type"], "not_found")

        mock_get.side_effect = requests.HTTPError(response=Mock(status_code=429))
        limited = self.tool.execute(name="missing", system="PYPI", version="1")
        self.assertEqual(limited["error"]["type"], "rate_limited")

        mock_get.side_effect = requests.HTTPError(response=Mock(status_code=503))
        unavailable = self.tool.execute(name="missing", system="PYPI", version="1")
        self.assertEqual(unavailable["error"]["type"], "http_error")

    @patch("agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool.requests.get")
    def test_invalid_json_and_version_shapes_are_structured(self, mock_get: Mock) -> None:
        invalid_json = response_mock()
        invalid_json.json.side_effect = requests.JSONDecodeError("invalid JSON", "", 0)
        mock_get.return_value = invalid_json
        json_result = self.tool.execute(name="jinja2", system="PYPI", version="2.4.1")
        self.assertEqual(json_result["error"]["type"], "invalid_response")

        mock_get.return_value = response_mock(json_data={"versionKey": {"system": "PYPI"}})
        shape_result = self.tool.execute(name="jinja2", system="PYPI", version="2.4.1")
        self.assertEqual(shape_result["error"]["type"], "invalid_response")
        self.assertIn("versionKey", shape_result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool.requests.get")
    def test_invalid_dependency_shapes_are_structured(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"nodes": "not-a-list", "edges": []})

        result = self.tool.execute(
            name="jinja2",
            system="PYPI",
            version="2.4.1",
            mode="dependencies",
        )

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("nodes must be a list", result["error"]["message"])

    def test_shipped_config_loads_and_initializes_contract(self) -> None:
        config_path = (
            Path(__file__).resolve().parents[6]
            / "examples"
            / "sample_standard_app"
            / "intelligence"
            / "agentic"
            / "tool"
            / "buildin"
            / "deps_dev_package_tool.yaml"
        )
        with config_path.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.assertEqual(config["input_keys"], ["name", "system", "version"])
        description = config["description"]
        for parameter in ("name", "system", "version", "mode", "max_nodes", "max_edges"):
            self.assertIn(parameter, description)
        for field in ("licenses", "OSV", "SLSA", "attestations", "dependency"):
            self.assertIn(field, description)

        configer = Configer(str(config_path)).load()
        tool_configer = ToolConfiger(configer).load_by_configer(configer)
        tool = DepsDevPackageTool().initialize_by_component_configer(tool_configer)
        self.assertEqual(tool.name, "deps_dev_package_tool")
        self.assertEqual(tool.input_keys, ["name", "system", "version"])


if __name__ == "__main__":
    unittest.main()
