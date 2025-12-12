import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse


class OptimizationAgentTest(unittest.TestCase):
    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_optimization_agent(self):
        instance: Agent = AgentManager().get_instance_obj('demo_optimization_agent')
        input_data = {
            "samples": [
                "具有美白功效的防蛀牙膏",
                "多功能微波炉"
            ],
            "initial_prompt": "为以下商品撰写推荐广告语。商品信息如下：{input}",
            "batch_size": 1,
            "max_iterations": 2,
            "scoring_standard": "总分100分，吸引力占50分，易懂易记程度占50分。",
            "avg_score_threshold": 90
        }
        instance.run(**input_data)


if __name__ == '__main__':
    unittest.main()
