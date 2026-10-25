"""Exercise expert instructions through real prompt configuration and builders."""

from copy import deepcopy
from uuid import uuid4

import pytest
import yaml

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.plan.planner.executing_planner.executing_planner import ExecutingPlanner
from agentuniverse.agent.plan.planner.expressing_planner.expressing_planner import ExpressingPlanner
from agentuniverse.agent.plan.planner.planning_planner.planning_planner import PlanningPlanner
from agentuniverse.agent.plan.planner.reviewing_planner.reviewing_planner import ReviewingPlanner
from agentuniverse.agent.template.slave_rag_agent_template import SlaveRagAgentTemplate
from agentuniverse.base.config.component_configer.configers.prompt_configer import PromptConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager


class PromptOnlyAgent(Agent):
    """Implement abstract I/O hooks; use Agent.process_prompt unchanged."""

    def input_keys(self):
        return ["input"]

    def output_keys(self):
        return ["output"]

    def parse_input(self, input_object, agent_input):
        return agent_input

    def parse_result(self, agent_result):
        return agent_result


BUILDERS = [PromptOnlyAgent, SlaveRagAgentTemplate, PlanningPlanner,
            ReviewingPlanner, ExecutingPlanner, ExpressingPlanner]


@pytest.fixture
def register_prompt(tmp_path):
    """Load actual YAML/configer/Prompt objects into the actual prompt manager."""
    manager = PromptManager()
    registered = []

    def register(instruction):
        name = "expert-prefix-" + uuid4().hex
        values = {"introduction": "Version introduction", "target": "Version target",
                  "instruction": instruction, "metadata": {"version": name}}
        path = tmp_path / (name + ".yaml")
        path.write_text(yaml.safe_dump(values), encoding="utf-8")
        config = Configer().load_by_path(str(path))
        version = Prompt().initialize_by_component_configer(PromptConfiger().load_by_configer(config))
        manager.register(name, version)
        registered.append((name, version, deepcopy(version.__dict__)))
        return name

    yield register
    for name, version, snapshot in registered:
        assert manager.get_instance_obj(name) is version
        assert version.__dict__ == snapshot
        manager.unregister(name)


@pytest.mark.parametrize("builder", BUILDERS, ids=lambda value: value.__name__)
@pytest.mark.parametrize("inline,has_version,version,expert,expected", [
    (None, False, None, "EXPERT: ", "EXPERT: "),
    ("", False, None, "EXPERT: ", "EXPERT: "),
    (None, True, None, "EXPERT: ", "EXPERT: "),
    ("PROFILE {input}", True, None, "EXPERT: ", "EXPERT: PROFILE QUESTION"),
    ("", True, "VERSION {input}", "EXPERT: ", "EXPERT: "),
    (None, True, None, None, None),
    ("PROFILE {input}", True, "VERSION {input}", "EXPERT: ", "EXPERT: PROFILE QUESTION"),
    (None, True, "VERSION {input}", "EXPERT: ", "EXPERT: VERSION QUESTION"),
    ("PROFILE {input}", False, None, "", "PROFILE QUESTION"),
], ids=["missing-inline", "empty-inline", "null-version", "override-null-version",
        "empty-overrides-version", "null-version-no-expert", "inline-priority",
        "version-fallback", "no-expert-control"])
def test_expert_prefix_after_prompt_inheritance(
        builder, inline, has_version, version, expert, expected, register_prompt):
    profile = {"introduction": "Profile introduction", "target": "Profile target"}
    if inline is not None:
        profile["instruction"] = inline
    version_name = register_prompt(version) if has_version else None
    if version_name:
        profile["prompt_version"] = version_name
    model = AgentModel(profile=deepcopy(profile))
    values = {"input": "QUESTION", "expert_framework": expert, "prompt_name": version_name}
    instance = builder()
    if isinstance(instance, Agent):
        instance.agent_model = model
        prompt = instance.process_prompt(values)
    else:
        prompt = instance.handle_prompt(model, values)
    native = prompt.as_langchain()
    if isinstance(prompt, ChatPrompt):
        text = "\n".join(message.content for message in native.format_messages(input="QUESTION"))
    else:
        text = native.format(input="QUESTION")
    contents = text.split("\n")
    assert contents[:2] == ["Profile introduction", "Profile target"]
    if expected is None:
        assert contents == ["Profile introduction", "Profile target"]
    else:
        assert contents[2:] == [expected]
    assert "\n".join(contents).count("EXPERT:") == (1 if expert else 0)
    assert model.profile == profile
    if builder is PromptOnlyAgent:
        assert values["expert_framework"] == expert


@pytest.mark.parametrize("builder", BUILDERS, ids=lambda value: value.__name__)
def test_expert_prefix_does_not_replace_required_prompt_configuration(builder):
    model = AgentModel(profile={})
    values = {"expert_framework": "EXPERT: ", "prompt_name": None}
    instance = builder()
    with pytest.raises(Exception, match="Either the `prompt_version`"):
        if isinstance(instance, Agent):
            instance.agent_model = model
            instance.process_prompt(values)
        else:
            instance.handle_prompt(model, values)
