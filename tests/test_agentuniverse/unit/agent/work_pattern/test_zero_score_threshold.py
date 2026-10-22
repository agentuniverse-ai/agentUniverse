import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.grr_agent_template import GRRAgentTemplate
from agentuniverse.agent.template.peer_agent_template import PeerAgentTemplate
from agentuniverse.agent.work_pattern.grr_work_pattern import GRRWorkPattern
from agentuniverse.agent.work_pattern.peer_work_pattern import PeerWorkPattern


@pytest.mark.parametrize("template_class", [GRRAgentTemplate, PeerAgentTemplate])
def test_agent_template_preserves_zero_threshold(template_class):
    template = template_class()
    template.agent_model = AgentModel(
        profile={"eval_threshold": 0},
        plan={"planner": {}},
        memory={},
    )

    with patch.object(
        AgentTemplate,
        "initialize_by_component_configer",
        return_value=template,
    ):
        template.initialize_by_component_configer(MagicMock())

    assert template.eval_threshold == 0


def _grr_pattern():
    pattern = GRRWorkPattern()
    pattern._validate_work_pattern_members = MagicMock()
    pattern._invoke_generating = MagicMock(return_value={"output": "draft"})
    pattern._invoke_reviewing = MagicMock(return_value={"score": 0})
    pattern._invoke_rewriting = MagicMock(return_value={"output": "rewrite"})
    pattern._async_invoke_generating = AsyncMock(return_value={"output": "draft"})
    pattern._async_invoke_reviewing = AsyncMock(return_value={"score": 0})
    pattern._async_invoke_rewriting = AsyncMock(return_value={"output": "rewrite"})
    return pattern


def test_grr_stops_on_zero_score_at_zero_threshold():
    sync_pattern = _grr_pattern()
    async_pattern = _grr_pattern()
    work_pattern_input = {"retry_count": 2, "eval_threshold": 0}

    sync_pattern.invoke(InputObject({}), work_pattern_input)
    asyncio.run(async_pattern.async_invoke(InputObject({}), work_pattern_input))

    assert sync_pattern._invoke_reviewing.call_count == 1
    assert sync_pattern._invoke_rewriting.call_count == 0
    assert async_pattern._async_invoke_reviewing.await_count == 1
    assert async_pattern._async_invoke_rewriting.await_count == 0


def _peer_pattern():
    pattern = PeerWorkPattern()
    pattern._validate_work_pattern_members = MagicMock()
    pattern._invoke_planning = MagicMock(return_value={"framework": []})
    pattern._invoke_executing = MagicMock(return_value={"output": "draft"})
    pattern._invoke_expressing = MagicMock(return_value={"output": "answer"})
    pattern._invoke_reviewing = MagicMock(return_value={"score": 0})
    pattern._async_invoke_planning = AsyncMock(return_value={"framework": []})
    pattern._async_invoke_executing = AsyncMock(return_value={"output": "draft"})
    pattern._async_invoke_expressing = AsyncMock(return_value={"output": "answer"})
    pattern._async_invoke_reviewing = AsyncMock(return_value={"score": 0})
    return pattern


def test_peer_stops_on_zero_score_at_zero_threshold():
    sync_pattern = _peer_pattern()
    async_pattern = _peer_pattern()
    work_pattern_input = {
        "retry_count": 2,
        "eval_threshold": 0,
        "jump_step": "reviewing",
    }

    sync_pattern.invoke(InputObject({}), work_pattern_input)
    asyncio.run(async_pattern.async_invoke(InputObject({}), work_pattern_input))

    assert sync_pattern._invoke_reviewing.call_count == 1
    assert async_pattern._async_invoke_reviewing.await_count == 1
