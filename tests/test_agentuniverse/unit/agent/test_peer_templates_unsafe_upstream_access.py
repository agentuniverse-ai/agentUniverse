from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.executing_agent_template import (
    ExecutingAgentTemplate,
)
from agentuniverse.agent.template.expressing_agent_template import (
    ExpressingAgentTemplate,
)
from agentuniverse.agent.template.planning_agent_template import (
    PlanningAgentTemplate,
)
from agentuniverse.agent.template.reviewing_agent_template import (
    ReviewingAgentTemplate,
)


def test_planning_parse_result_without_framework_falls_back_to_empty_list():
    # an LLM answer that carries no 'framework' key must not crash the
    # logging loop (enumerate(None)) nor leak None downstream
    final_result = PlanningAgentTemplate().parse_result(
        {"output": '{"thought": "I will answer the question directly."}'})
    assert final_result["framework"] == []
    assert final_result["thought"] == "I will answer the question directly."


def test_planning_parse_result_with_framework_unchanged():
    final_result = PlanningAgentTemplate().parse_result(
        {"output": '{"framework": ["subtask A", "subtask B"], "thought": "ok"}'})
    assert final_result["framework"] == ["subtask A", "subtask B"]
    assert final_result["thought"] == "ok"


def test_executing_parse_input_without_planning_result():
    agent_input = ExecutingAgentTemplate().parse_input(
        InputObject({"input": "demo question"}), {})
    assert agent_input["framework"] is None


def test_executing_parse_input_with_planning_result():
    agent_input = ExecutingAgentTemplate().parse_input(
        InputObject({"input": "demo question",
                     "planning_result": OutputObject({"framework": ["subtask A"]})}), {})
    assert agent_input["framework"] == ["subtask A"]


def test_executing_execute_tasks_with_none_framework_returns_empty_result():
    # 'framework' key present but None: get('framework', []) default never
    # applied, len(None) used to raise TypeError
    template = ExecutingAgentTemplate()
    result = template._execute_tasks(InputObject({}),
                                     {"input": "demo", "framework": None},
                                     None, None, None)
    assert result == {"executing_result": [], "output_stream": None}


def test_expressing_build_execution_context_without_executing_result():
    context = ExpressingAgentTemplate().build_execution_context(
        InputObject({"input": "demo question"}))
    assert context == ""


def test_expressing_build_execution_context_with_executing_result():
    context = ExpressingAgentTemplate().build_execution_context(
        InputObject({"executing_result": OutputObject({"executing_result": [
            {"index": 0, "input": "Question 1: A", "output": "Answer 1"}]})}))
    assert "question:Question 1: A" in context
    assert "answer:Answer 1" in context


def test_reviewing_parse_input_without_expressing_result():
    agent_input = ReviewingAgentTemplate().parse_input(
        InputObject({"input": "demo question"}), {})
    assert agent_input["expressing_result"] is None


def test_reviewing_parse_input_with_expressing_result():
    agent_input = ReviewingAgentTemplate().parse_input(
        InputObject({"input": "demo question",
                     "expressing_result": OutputObject({"output": "the answer"})}), {})
    assert agent_input["expressing_result"] == "the answer"
