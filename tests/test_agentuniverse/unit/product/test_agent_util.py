import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


if "ruamel.yaml" not in sys.modules:
    ruamel_module = types.ModuleType("ruamel")
    yaml_module = types.ModuleType("ruamel.yaml")
    yaml_module.YAML = MagicMock
    ruamel_module.yaml = yaml_module
    sys.modules["ruamel"] = ruamel_module
    sys.modules["ruamel.yaml"] = yaml_module

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse_product.service.model.agent_dto import AgentDTO
from agentuniverse_product.service.model.llm_dto import LlmDTO
from agentuniverse_product.service.model.planner_dto import PlannerDTO
from agentuniverse_product.service.util import agent_util


class AgentUtilTemperatureTest(unittest.TestCase):
    def test_assemble_agent_config_preserves_zero_temperature(self):
        agent_dto = AgentDTO(
            id="zero-temperature-agent",
            planner=PlannerDTO(id="workflow_planner"),
            llm=LlmDTO(id="test-llm", temperature=0.0),
        )
        llm_manager = MagicMock()
        llm_manager.get_instance_obj.return_value = SimpleNamespace()

        with patch.object(agent_util, "LLMManager", return_value=llm_manager):
            config = agent_util.assemble_agent_config_data(agent_dto)

        self.assertEqual(config["profile"]["llm_model"]["temperature"], 0.0)

    def test_get_llm_dto_preserves_configured_zero_temperature(self):
        agent_model = AgentModel(
            profile={"llm_model": {"name": "test-llm", "temperature": 0.0}},
        )
        llm_manager = MagicMock()
        llm_manager.get_instance_obj.return_value = SimpleNamespace(
            model_name="default-model", temperature=0.7
        )

        with patch.object(agent_util, "LLMManager", return_value=llm_manager), patch.object(
            agent_util, "ProductManager", return_value=MagicMock(get_instance_obj=MagicMock(return_value=None))
        ):
            llm_dto = agent_util.get_llm_dto(agent_model)

        self.assertEqual(llm_dto.temperature, 0.0)

    def test_update_agent_config_preserves_zero_temperature(self):
        agent = SimpleNamespace(
            agent_model=AgentModel(profile={"llm_model": {"name": "test-llm"}})
        )
        agent_dto = AgentDTO(
            id="zero-temperature-agent",
            llm=LlmDTO(id="test-llm", temperature=0.0, model_name=["test-model"]),
        )

        with patch.object(agent_util, "update_nested_yaml_value") as update_yaml:
            agent_util.update_agent_config(agent, agent_dto, "agent.yaml")

        self.assertEqual(agent.agent_model.profile["llm_model"]["temperature"], 0.0)
        self.assertEqual(
            update_yaml.call_args.args[1]["profile.llm_model.temperature"], 0.0
        )


if __name__ == "__main__":
    unittest.main()
