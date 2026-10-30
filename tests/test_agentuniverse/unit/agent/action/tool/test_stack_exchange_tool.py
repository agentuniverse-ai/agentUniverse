#!/usr/bin/env python3

"""Offline tests for the bounded Stack Exchange research tool."""

import json
import os
import unittest
from unittest.mock import Mock, patch

import requests

from agentuniverse.agent.action.tool.common_tool import stack_exchange_tool as stack_module
from agentuniverse.agent.action.tool.common_tool.stack_exchange_tool import StackExchangeTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(stack_module.__file__), "stack_exchange_tool.yaml")


def response_mock(*, json_data=None, status_code=200, json_error=None):
    """Build a requests.Response-like mock."""
    response = Mock()
    response.status_code = status_code
    if json_error is not None:
        response.json.side_effect = json_error
    else:
        response.json.return_value = json_data
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(response=response)
    else:
        response.raise_for_status.return_value = None
    return response


def envelope(items, *, has_more=False, quota_remaining=300, quota_max=10000, backoff=None):
    """Build a valid Stack Exchange API wrapper."""
    payload = {
        "items": items,
        "has_more": has_more,
        "quota_remaining": quota_remaining,
        "quota_max": quota_max,
    }
    if backoff is not None:
        payload["backoff"] = backoff
    return payload


QUESTION = {
    "question_id": 42,
    "title": "How to parse &lt;b&gt;JSON&lt;/b&gt; safely?",
    "link": "https://stackoverflow.com/questions/42/example",
    "tags": ["python", "json"],
    "score": 25,
    "view_count": 1000,
    "answer_count": 2,
    "is_answered": True,
    "accepted_answer_id": 1001,
    "creation_date": 1_700_000_000,
    "last_activity_date": 1_700_000_100,
    "content_license": "CC BY-SA 4.0",
    "owner": {
        "user_id": 7,
        "display_name": "Alice &amp; Bob",
        "reputation": 1234,
        "link": "https://stackoverflow.com/users/7/alice",
    },
    "body": "<p>Use <code>json.loads</code>.</p><script>do-not-emit()</script>",
}

ACCEPTED_ANSWER = {
    "answer_id": 1001,
    "question_id": 42,
    "is_accepted": True,
    "score": 10,
    "link": "https://stackoverflow.com/a/1001",
    "creation_date": 1_700_000_010,
    "last_activity_date": 1_700_000_020,
    "content_license": "CC BY-SA 4.0",
    "owner": {
        "user_id": 8,
        "display_name": "Accepted User",
        "reputation": 999,
        "link": "https://stackoverflow.com/users/8/accepted",
    },
    "body": "<p>Validate first, then call <code>json.loads</code>.</p>",
}

TOP_ANSWER = {
    "answer_id": 1002,
    "question_id": 42,
    "is_accepted": False,
    "score": 50,
    "link": "https://stackoverflow.com/a/1002",
    "creation_date": 1_700_000_030,
    "last_activity_date": 1_700_000_040,
    "content_license": "CC BY-SA 4.0",
    "owner": {
        "user_id": 9,
        "display_name": "Top User",
        "reputation": 5000,
        "link": "https://stackoverflow.com/users/9/top",
    },
    "body": "<p>A higher-voted alternative.</p>",
}


class StackExchangeToolTest(unittest.TestCase):
    """HTTP, normalization, validation, and error behavior."""

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_search_returns_questions_and_bounded_answers(self, mock_get: Mock) -> None:
        tool = StackExchangeTool(api_key="test-key", access_token="test-token")  # noqa: S106 - fixture credential
        mock_get.side_effect = [
            response_mock(json_data=envelope([QUESTION], has_more=True, quota_remaining=299)),
            response_mock(json_data=envelope([ACCEPTED_ANSWER], quota_remaining=298)),
            response_mock(
                json_data=envelope(
                    [TOP_ANSWER, ACCEPTED_ANSWER],
                    quota_remaining=297,
                )
            ),
        ]

        result = tool.execute(
            query="  parse \n JSON safely ",
            site="StackOverflow",
            tags=["Python", "json"],
            sort="Votes",
            order="DESC",
            page=2,
            page_size=1,
            from_date="2024-01-01",
            to_date="2024-01-31",
            answers_per_question=2,
        )

        self.assertEqual(result["query"], "parse JSON safely")
        self.assertEqual(result["site"], "stackoverflow")
        self.assertEqual(result["tags"], ["python", "json"])
        self.assertEqual(result["returned_results"], 1)
        self.assertTrue(result["has_more"])
        self.assertEqual(result["quota_remaining"], 297)
        self.assertEqual(result["quota_max"], 10000)
        self.assertEqual(result["answer_fetch_status"], "complete")
        self.assertFalse(result["answers_has_more"])

        question = result["questions"][0]
        self.assertEqual(question["question_id"], 42)
        self.assertEqual(question["title"], "How to parse <b>JSON</b> safely?")
        self.assertIn("json.loads", question["body_excerpt"])
        self.assertNotIn("script", question["body_excerpt"])
        self.assertNotIn("do-not-emit", question["body_excerpt"])
        self.assertEqual(question["owner"]["display_name"], "Alice & Bob")
        self.assertEqual([answer["answer_id"] for answer in question["answers"]], [1001, 1002])
        self.assertTrue(question["answers"][0]["is_accepted"])
        self.assertEqual(question["content_license"], "CC BY-SA 4.0")

        search_call = mock_get.call_args_list[0]
        self.assertEqual(search_call.args[0], "https://api.stackexchange.com/2.3/search/advanced")
        params = search_call.kwargs["params"]
        self.assertEqual(params["q"], "parse JSON safely")
        self.assertEqual(params["site"], "stackoverflow")
        self.assertEqual(params["tagged"], "python;json")
        self.assertEqual(params["sort"], "votes")
        self.assertEqual(params["order"], "desc")
        self.assertEqual(params["page"], 2)
        self.assertEqual(params["pagesize"], 1)
        self.assertEqual(params["filter"], "withbody")
        self.assertEqual(params["key"], "test-key")
        self.assertEqual(params["access_token"], "test-token")
        self.assertEqual(params["fromdate"], StackExchangeTool._date_timestamp("2024-01-01", upper=False))
        self.assertEqual(params["todate"], StackExchangeTool._date_timestamp("2024-01-31", upper=True))
        self.assertEqual(search_call.kwargs["timeout"], 15.0)

        serialized = json.dumps(result)
        self.assertNotIn("test-key", serialized)
        self.assertNotIn("test-token", serialized)

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_empty_search_uses_one_request(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=envelope([], quota_remaining=250))

        result = StackExchangeTool().execute(query="no matching question", tags="python;pytest")

        self.assertEqual(result["questions"], [])
        self.assertEqual(result["returned_results"], 0)
        self.assertEqual(result["answer_fetch_status"], "not_needed")
        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(mock_get.call_args.kwargs["params"]["tagged"], "python;pytest")

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_no_accepted_answer_fetches_top_answers_once(self, mock_get: Mock) -> None:
        question = {**QUESTION, "accepted_answer_id": None}
        mock_get.side_effect = [
            response_mock(json_data=envelope([question], quota_remaining=20)),
            response_mock(json_data=envelope([TOP_ANSWER], quota_remaining=19)),
        ]

        result = StackExchangeTool().execute(query="json", page_size=1)

        self.assertEqual(mock_get.call_count, 2)
        self.assertIn("/questions/42/answers", mock_get.call_args_list[1].args[0])
        self.assertEqual(result["questions"][0]["answers"][0]["answer_id"], 1002)

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_answer_has_more_marks_result_partial(self, mock_get: Mock) -> None:
        question = {**QUESTION, "accepted_answer_id": None}
        mock_get.side_effect = [
            response_mock(json_data=envelope([question], quota_remaining=20)),
            response_mock(
                json_data=envelope(
                    [TOP_ANSWER],
                    has_more=True,
                    quota_remaining=19,
                )
            ),
        ]

        result = StackExchangeTool().execute(query="json", page_size=1)

        self.assertTrue(result["answers_has_more"])
        self.assertEqual(result["answer_fetch_status"], "partial")

    def test_rejects_invalid_inputs_before_network(self) -> None:
        tool = StackExchangeTool()
        invalid_cases = [
            ({"query": ""}, "query must not be empty"),
            ({"query": "x" * 301}, "query must not exceed"),
            ({"query": "x", "site": "https://stackoverflow.com"}, "site must be"),
            ({"query": "x", "site": "bad..site"}, "site must be"),
            ({"query": "x", "tags": ["one", "two", "three", "four", "five", "six"]}, "at most 5"),
            ({"query": "x", "tags": ["python/sql"]}, "tags may contain"),
            ({"query": "x", "tags": 123}, "tags must be"),
            ({"query": "x", "sort": "newest"}, "sort must be"),
            ({"query": "x", "order": "sideways"}, "order must be"),
            ({"query": "x", "page": True}, "page must be"),
            ({"query": "x", "page": 101}, "page must be"),
            ({"query": "x", "page_size": 9}, "page_size must be"),
            ({"query": "x", "answers_per_question": 4}, "answers_per_question must be"),
            ({"query": "x", "from_date": "2024-02-30"}, "from_date must be a valid date"),
            ({"query": "x", "to_date": "2024-01"}, "to_date must use"),
            (
                {"query": "x", "from_date": "2024-02-01", "to_date": "2024-01-01"},
                "from_date must not be later",
            ),
        ]
        with patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get") as mock_get:
            for kwargs, message in invalid_cases:
                with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ValueError, message):
                    tool.execute(**kwargs)
            mock_get.assert_not_called()

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_access_token_requires_key(self, mock_get: Mock) -> None:
        tool = StackExchangeTool(access_token="token-only")  # noqa: S106 - fixture credential

        with self.assertRaisesRegex(ValueError, "requires STACKEXCHANGE_KEY"):
            tool.execute(query="python")

        mock_get.assert_not_called()

    def test_credentials_are_excluded_from_model_dump_and_repr(self) -> None:
        tool = StackExchangeTool(
            api_key="private-key",
            access_token="private-token",  # noqa: S106 - fixture credential
        )

        self.assertNotIn("api_key", tool.model_dump())
        self.assertNotIn("access_token", tool.model_dump())
        self.assertNotIn("private-key", repr(tool))
        self.assertNotIn("private-token", repr(tool))

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_search_backoff_skips_answer_fetch_and_blocks_next_call(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=envelope([QUESTION], quota_remaining=100, backoff=5))
        tool = StackExchangeTool()

        with patch(
            "agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.time.monotonic",
            side_effect=[100.0, 100.0, 101.0],
        ):
            first = tool.execute(query="json", page_size=1)
            second = tool.execute(query="json", page_size=1)

        self.assertEqual(first["answer_fetch_status"], "backoff")
        self.assertEqual(first["backoff_seconds"], 5)
        self.assertEqual(second["error"]["type"], "backoff_active")
        self.assertEqual(second["backoff_seconds"], 4)
        self.assertEqual(mock_get.call_count, 1)

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_exhausted_quota_skips_answer_fetch(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=envelope([QUESTION], quota_remaining=0))

        result = StackExchangeTool().execute(query="json", page_size=1)

        self.assertEqual(result["quota_remaining"], 0)
        self.assertEqual(result["answer_fetch_status"], "quota_exhausted")
        self.assertEqual(result["questions"][0]["answers"], [])
        self.assertEqual(mock_get.call_count, 1)

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_answer_timeout_preserves_question_and_hides_request_details(self, mock_get: Mock) -> None:
        question = {**QUESTION, "accepted_answer_id": None}
        mock_get.side_effect = [
            response_mock(json_data=envelope([question], quota_remaining=100)),
            requests.Timeout("https://api.stackexchange.com?key=private-key"),
        ]
        tool = StackExchangeTool(api_key="private-key")

        result = tool.execute(query="json", page_size=1)

        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["answer_fetch_status"], "error")
        self.assertEqual(result["answer_error"]["type"], "request_timeout")
        self.assertNotIn("private-key", json.dumps(result))

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_request_timeout_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("secret URL details")

        result = StackExchangeTool().execute(query="json")

        self.assertEqual(result["error"]["type"], "request_timeout")
        self.assertEqual(result["questions"], [])
        self.assertNotIn("secret URL details", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_http_error_returns_status_without_request_url(self, mock_get: Mock) -> None:
        response = Mock(status_code=429)
        mock_get.side_effect = requests.HTTPError(
            "429 for https://api.stackexchange.com?key=private-key",
            response=response,
        )

        result = StackExchangeTool(api_key="private-key").execute(query="json")

        self.assertEqual(result["error"]["type"], "http_error")
        self.assertIn("429", result["error"]["message"])
        self.assertNotIn("private-key", json.dumps(result))

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_api_error_is_structured_and_credentials_are_redacted(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            status_code=400,
            json_data={
                "error_id": 400,
                "error_name": "bad_parameter",
                "error_message": "private-token is invalid",
            },
        )

        result = StackExchangeTool(
            api_key="private-key",
            access_token="private-token",  # noqa: S106 - fixture credential
        ).execute(query="json")

        self.assertEqual(result["error"]["type"], "api_error")
        self.assertIn("bad_parameter", result["error"]["message"])
        self.assertIn("[redacted]", result["error"]["message"])
        self.assertNotIn("private-token", json.dumps(result))

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_invalid_json_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            status_code=200,
            json_error=requests.JSONDecodeError("bad JSON", "not-json", 0),
        )

        result = StackExchangeTool().execute(query="json")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid Stack Exchange JSON", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_malformed_envelope_is_rejected(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "items": [],
                "has_more": "false",
                "quota_remaining": 100,
            }
        )

        result = StackExchangeTool().execute(query="json")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("has_more", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_excerpts_and_serialized_output_are_bounded(self, mock_get: Mock) -> None:
        question = {
            **QUESTION,
            "body": "<p>" + ("question " * 1000) + "</p>",
        }
        accepted_answer = {
            **ACCEPTED_ANSWER,
            "body": "<pre>" + ("accepted " * 1000) + "</pre>",
        }
        top_answer = {
            **TOP_ANSWER,
            "body": "<p>" + ("alternative " * 1000) + "</p>",
        }
        mock_get.side_effect = [
            response_mock(json_data=envelope([question], quota_remaining=100)),
            response_mock(json_data=envelope([accepted_answer], quota_remaining=99)),
            response_mock(json_data=envelope([accepted_answer, top_answer], quota_remaining=98)),
        ]

        result = StackExchangeTool().execute(
            query="json",
            page_size=1,
            answers_per_question=2,
        )

        normalized_question = result["questions"][0]
        self.assertLessEqual(
            len(normalized_question["body_excerpt"]),
            StackExchangeTool.MAX_QUESTION_EXCERPT_LENGTH,
        )
        for answer in normalized_question["answers"]:
            self.assertLessEqual(
                len(answer["body_excerpt"]),
                StackExchangeTool.MAX_ANSWER_EXCERPT_LENGTH,
            )
        self.assertLessEqual(
            StackExchangeTool._serialized_size(result),
            StackExchangeTool.MAX_OUTPUT_BYTES,
        )

    def test_html_cleaner_rejects_unsafe_links_and_script_text(self) -> None:
        self.assertEqual(
            StackExchangeTool._clean_markup(
                "<p>Hello<br>world</p><style>hidden</style><script>bad()</script>",
                100,
            ),
            "Hello world",
        )
        self.assertEqual(StackExchangeTool._safe_url("javascript:alert(1)"), "")
        self.assertEqual(StackExchangeTool._safe_url("https://user:pass@example.com/x"), "")


class StackExchangeRegistrationTest(unittest.TestCase):
    """Load the shipped YAML through the real component registration pipeline."""

    def setUp(self) -> None:
        self.configer = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous_app_configer = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous_app_configer = None

    def tearDown(self) -> None:
        ApplicationConfigManager().app_configer = self.previous_app_configer

    def test_yaml_resolves_to_tool_component(self) -> None:
        component_configer = ComponentConfiger().load_by_configer(self.configer)

        self.assertEqual(component_configer.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(
            component_configer.metadata_module,
            "agentuniverse.agent.action.tool.common_tool.stack_exchange_tool",
        )
        self.assertEqual(component_configer.metadata_class, "StackExchangeTool")

    def test_tool_manager_initializes_shipped_yaml(self) -> None:
        tool_configer = ToolConfiger().load_by_configer(self.configer)
        app_configer = AppConfiger()
        app_configer.tool_configer_map = {tool_configer.name: tool_configer}
        ApplicationConfigManager().app_configer = app_configer

        tool = ToolManager().get_instance_obj(tool_configer.name)

        self.assertIsInstance(tool, StackExchangeTool)
        self.assertEqual(tool.name, "stack_exchange_tool")
        self.assertEqual(tool.component_type, ComponentEnum.TOOL)
        self.assertEqual(tool.input_keys, ["query"])
        schema = tool.args_model_schema
        self.assertEqual(schema["properties"]["page_size"]["maximum"], 8)
        self.assertEqual(
            schema["properties"]["sort"]["enum"],
            ["relevance", "activity", "creation", "votes"],
        )

    @patch("agentuniverse.agent.action.tool.common_tool.stack_exchange_tool.requests.get")
    def test_registered_tool_executes_without_network(self, mock_get: Mock) -> None:
        tool_configer = ToolConfiger().load_by_configer(self.configer)
        app_configer = AppConfiger()
        app_configer.tool_configer_map = {tool_configer.name: tool_configer}
        ApplicationConfigManager().app_configer = app_configer
        tool = ToolManager().get_instance_obj(tool_configer.name)
        mock_get.return_value = response_mock(json_data=envelope([], quota_remaining=50))

        result = tool.run(query="configuration pipeline")

        self.assertEqual(result["query"], "configuration pipeline")
        self.assertEqual(result["site"], "stackoverflow")
        self.assertEqual(result["questions"], [])
        self.assertEqual(mock_get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
