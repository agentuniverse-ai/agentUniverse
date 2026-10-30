import json
from queue import Queue
from unittest.mock import MagicMock, patch

import pytest

from agentuniverse.agent.template.planning_agent_template import PlanningAgentTemplate


def _template_with_stream() -> tuple[PlanningAgentTemplate, Queue]:
    template = PlanningAgentTemplate()
    template.agent_model = MagicMock()
    template.agent_model.info = {"name": "test-planning"}
    return template, Queue()


@patch("agentuniverse.agent.template.planning_agent_template.stream_output")
@patch("agentuniverse.agent.template.planning_agent_template.parse_json_markdown")
def test_add_output_stream_falls_back_on_json_decode_error(parse_json_markdown, stream_output):
    template, output_stream = _template_with_stream()
    parse_json_markdown.side_effect = json.JSONDecodeError("bad", "doc", 0)

    template.add_output_stream(output_stream, "not-json")

    parse_json_markdown.assert_called_once_with("not-json")
    stream_output.assert_called_once()
    assert stream_output.call_args[0][1]["data"]["output"] == "not-json"


@patch("agentuniverse.agent.template.planning_agent_template.stream_output")
@patch("agentuniverse.agent.template.planning_agent_template.parse_json_markdown")
def test_add_output_stream_falls_back_on_value_error(parse_json_markdown, stream_output):
    template, output_stream = _template_with_stream()
    parse_json_markdown.side_effect = ValueError("invalid markdown")

    template.add_output_stream(output_stream, "broken")

    stream_output.assert_called_once()
    assert stream_output.call_args[0][1]["data"]["output"] == "broken"


@patch("agentuniverse.agent.template.planning_agent_template.stream_output")
@patch("agentuniverse.agent.template.planning_agent_template.parse_json_markdown")
def test_add_output_stream_propagates_unexpected_type_error(parse_json_markdown, stream_output):
    template, output_stream = _template_with_stream()
    parse_json_markdown.side_effect = TypeError("unexpected")

    with pytest.raises(TypeError):
        template.add_output_stream(output_stream, "broken")

    stream_output.assert_not_called()


@patch("agentuniverse.agent.template.planning_agent_template.stream_output")
@patch("agentuniverse.agent.template.planning_agent_template.parse_json_markdown")
def test_add_output_stream_uses_framework_from_parsed_json(parse_json_markdown, stream_output):
    template, output_stream = _template_with_stream()
    parse_json_markdown.return_value = {"framework": ["step-1"]}

    template.add_output_stream(output_stream, '{"framework": ["step-1"]}')

    stream_output.assert_called_once()
    assert stream_output.call_args[0][1]["data"]["output"] == ["step-1"]
