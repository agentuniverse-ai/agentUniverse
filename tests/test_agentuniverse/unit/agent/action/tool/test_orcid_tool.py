#!/usr/bin/env python3

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.orcid_tool import OrcidTool
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

ORCID = "0000-0002-1825-0097"


def response_mock(json_data=None):
    response = Mock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class OrcidToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = OrcidTool(access_token="test-secret")  # noqa: S106

    @patch("agentuniverse.agent.action.tool.common_tool.orcid_tool.requests.get")
    def test_search_returns_normalized_researchers(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            {
                "num-found": 12,
                "expanded-result": [
                    {
                        "orcid-id": ORCID,
                        "given-names": "Josiah",
                        "family-names": "Carberry",
                        "credit-name": "J. Carberry",
                        "other-name": ["Joe Carberry"],
                        "email": ["public@example.org"],
                        "institution-name": ["Brown University"],
                        "past-institution-name": ["Example Institute"],
                    }
                ],
            }
        )

        result = self.tool.execute(query='family-name:Carberry', max_results=3, page=2)

        self.assertEqual(result["total_results"], 12)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["works"], [])
        self.assertEqual(
            result["researchers"][0],
            {
                "orcid": ORCID,
                "given_names": "Josiah",
                "family_name": "Carberry",
                "credit_name": "J. Carberry",
                "other_names": ["Joe Carberry"],
                "emails": ["public@example.org"],
                "current_institutions": ["Brown University"],
                "past_institutions": ["Example Institute"],
                "profile_url": f"https://orcid.org/{ORCID}",
            },
        )
        request = mock_get.call_args
        self.assertEqual(request.args[0], "https://pub.orcid.org/v3.0/expanded-search/")
        self.assertEqual(request.kwargs["params"], {"q": "family-name:Carberry", "start": 3, "rows": 3})
        self.assertEqual(request.kwargs["headers"]["Accept"], "application/json")
        self.assertEqual(request.kwargs["headers"]["Authorization"], "Bearer test-secret")
        self.assertEqual(request.kwargs["timeout"], 15.0)

    @patch("agentuniverse.agent.action.tool.common_tool.orcid_tool.requests.get")
    def test_person_accepts_orcid_url_and_normalizes_profile(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            {
                "name": {
                    "given-names": {"value": "Josiah"},
                    "family-name": {"value": "Carberry"},
                    "credit-name": {"value": "J. Carberry"},
                },
                "biography": {"content": "Researcher biography"},
                "other-names": {"other-name": [{"content": "Joe Carberry"}]},
                "keywords": {"keyword": [{"content": "psychoceramics"}]},
                "addresses": {"address": [{"country": {"value": "US"}}]},
                "researcher-urls": {
                    "researcher-url": [
                        {"url-name": {"value": "Homepage"}, "url": {"value": "https://example.org"}}
                    ]
                },
                "external-identifiers": {
                    "external-identifier": [
                        {
                            "external-id-type": "Scopus Author ID",
                            "external-id-value": "123",
                            "external-id-url": {"value": "https://example.org/123"},
                        }
                    ]
                },
            }
        )

        result = self.tool.execute(query=f"https://orcid.org/{ORCID}", mode="PERSON")

        profile = result["researchers"][0]
        self.assertEqual(result["query"], ORCID)
        self.assertEqual(profile["given_names"], "Josiah")
        self.assertEqual(profile["keywords"], ["psychoceramics"])
        self.assertEqual(profile["countries"], ["US"])
        self.assertEqual(profile["researcher_urls"][0]["name"], "Homepage")
        self.assertEqual(profile["external_identifiers"][0]["value"], "123")
        self.assertEqual(mock_get.call_args.args[0], f"https://pub.orcid.org/v3.0/{ORCID}/person")

    @patch("agentuniverse.agent.action.tool.common_tool.orcid_tool.requests.get")
    def test_person_normalizes_pagination_to_single_record(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock({"name": None})

        result = self.tool.execute(query=ORCID, mode="person", max_results=20, page=25)

        self.assertEqual(result["max_results"], 1)
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["offset"], 0)
        self.assertEqual(result["returned_results"], 1)

    @patch("agentuniverse.agent.action.tool.common_tool.orcid_tool.requests.get")
    def test_works_are_normalized_and_locally_paginated(self, mock_get: Mock) -> None:
        groups = []
        for index in range(3):
            groups.append(
                {
                    "external-ids": {
                        "external-id": [
                            {
                                "external-id-type": "doi",
                                "external-id-value": f"10.1000/{index}",
                                "external-id-url": {"value": f"https://doi.org/10.1000/{index}"},
                                "external-id-relationship": "self",
                            }
                        ]
                    },
                    "work-summary": [
                        {
                            "put-code": index + 10,
                            "title": {
                                "title": {"value": f"Work {index}"},
                                "subtitle": {"value": "A subtitle"},
                                "translated-title": {"value": "Translated"},
                            },
                            "journal-title": {"value": "Example Journal"},
                            "type": "journal-article",
                            "publication-date": {
                                "year": {"value": "2025"},
                                "month": {"value": "08"},
                            },
                            "url": {"value": f"https://example.org/work/{index}"},
                            "visibility": "public",
                            "source": {"source-name": {"value": "Crossref"}},
                        }
                    ],
                }
            )
        mock_get.return_value = response_mock({"group": groups})

        result = self.tool.execute(query=ORCID, mode="works", max_results=1, page=2)

        self.assertEqual(result["total_results"], 3)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["pagination"], "local")
        self.assertEqual(result["api_fetched_results"], 3)
        self.assertEqual(result["researchers"], [])
        work = result["works"][0]
        self.assertEqual(work["title"], "Work 1")
        self.assertEqual(work["publication_date"], "2025-08")
        self.assertEqual(work["external_ids"][0]["value"], "10.1000/1")
        self.assertEqual(work["source"], "Crossref")
        self.assertEqual(work["record_url"], f"https://orcid.org/{ORCID}/work/11")

    def test_input_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "query must not be empty"):
            self.tool.execute(query=" ")
        with self.assertRaisesRegex(ValueError, "mode must be one of"):
            self.tool.execute(query="name", mode="record")
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            self.tool.execute(query="name", max_results=0)
        with self.assertRaisesRegex(ValueError, "integer"):
            self.tool.execute(query="name", max_results=True)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            self.tool.execute(query="name", page=0)
        with self.assertRaisesRegex(ValueError, "offset below 10000"):
            self.tool.execute(query="name", max_results=20, page=502)
        with self.assertRaisesRegex(ValueError, "valid ORCID"):
            self.tool.execute(query="0000-0002-1825-0098", mode="person")

    @patch("agentuniverse.agent.action.tool.common_tool.orcid_tool.requests.get")
    def test_timeout_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("secret-bearing diagnostic")

        result = self.tool.execute(query="machine learning")

        self.assertEqual(result["error"]["type"], "request_timeout")
        self.assertNotIn("test-secret", str(result))

    @patch("agentuniverse.agent.action.tool.common_tool.orcid_tool.requests.get")
    def test_http_error_reports_only_status(self, mock_get: Mock) -> None:
        response = Mock(status_code=429)
        mock_get.side_effect = requests.HTTPError("request with token test-secret", response=response)

        result = self.tool.execute(query="machine learning")

        self.assertEqual(result["error"], {"type": "http_error", "message": "ORCID returned HTTP status 429."})
        self.assertNotIn("test-secret", str(result))

    @patch("agentuniverse.agent.action.tool.common_tool.orcid_tool.requests.get")
    def test_invalid_json_and_shape_return_structured_errors(self, mock_get: Mock) -> None:
        response = response_mock()
        response.json.side_effect = requests.JSONDecodeError("bad", "", 0)
        mock_get.return_value = response
        invalid_json = self.tool.execute(query="machine learning")
        self.assertEqual(invalid_json["error"]["type"], "invalid_response")

        mock_get.return_value = response_mock({"num-found": 1, "expanded-result": {}})
        invalid_shape = self.tool.execute(query="machine learning")
        self.assertIn("expanded search results", invalid_shape["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.orcid_tool.requests.get")
    def test_malformed_nested_objects_return_structured_errors(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock({"name": []})
        invalid_person = self.tool.execute(query=ORCID, mode="person")
        self.assertEqual(invalid_person["error"]["type"], "invalid_response")
        self.assertIn("name object", invalid_person["error"]["message"])

        mock_get.return_value = response_mock(
            {"group": [{"work-summary": [{"title": "not-an-object", "source": {}}]}]}
        )
        invalid_work = self.tool.execute(query=ORCID, mode="works")
        self.assertEqual(invalid_work["error"]["type"], "invalid_response")
        self.assertIn("title object", invalid_work["error"]["message"])

    def test_empty_optional_metadata_is_stable(self) -> None:
        researcher = OrcidTool._parse_search_result({"orcid-id": ORCID})
        self.assertEqual(researcher["other_names"], [])
        self.assertEqual(researcher["current_institutions"], [])
        person = OrcidTool._parse_person(ORCID, {})
        self.assertEqual(person["keywords"], [])
        self.assertEqual(person["biography"], "")

    def test_shipped_yaml_registers_tool_and_documents_contract(self) -> None:
        config_path = (
            Path(__file__).resolve().parents[6]
            / "examples"
            / "sample_standard_app"
            / "intelligence"
            / "agentic"
            / "tool"
            / "buildin"
            / "orcid_tool.yaml"
        )
        with config_path.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.assertEqual(config["input_keys"], ["query"])
        self.assertEqual(config["metadata"]["class"], "OrcidTool")
        description = config["description"]
        for term in ("query", "search", "person", "works", "max_results", "page", "ORCID_ACCESS_TOKEN"):
            self.assertIn(term, description)
        self.assertIn("local pagination", description)
        self.assertIn("api_fetched_results", description)

    @patch("agentuniverse.agent.action.tool.common_tool.orcid_tool.requests.get")
    def test_shipped_config_initializes_tool(self, mock_get: Mock) -> None:
        config_path = (
            Path(__file__).resolve().parents[6]
            / "examples"
            / "sample_standard_app"
            / "intelligence"
            / "agentic"
            / "tool"
            / "buildin"
            / "orcid_tool.yaml"
        )
        configer = Configer(str(config_path)).load()
        tool_configer = ToolConfiger(configer).load_by_configer(configer)
        tool = OrcidTool(access_token=None).initialize_by_component_configer(tool_configer)
        mock_get.return_value = response_mock({"num-found": 0, "expanded-result": []})

        result = tool.execute(query="configuration pipeline")

        self.assertEqual(tool.name, "orcid_tool")
        self.assertEqual(tool.input_keys, ["query"])
        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["researchers"], [])


if __name__ == "__main__":
    unittest.main()
