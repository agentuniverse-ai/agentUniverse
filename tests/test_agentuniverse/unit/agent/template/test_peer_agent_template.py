"""Tests for peer-agent result parsing."""

from agentuniverse.agent.template.peer_agent_template import PeerAgentTemplate


def test_parse_result_returns_empty_output_when_no_expression_exists():
    template = PeerAgentTemplate()

    assert template.parse_result({"result": []}) == {"output": ""}
    assert template.parse_result(
        {"result": [{"expressing_result": {}}]}
    ) == {"output": ""}
