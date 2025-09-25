from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='test_app/config.toml', core_mode=True)
instance: Agent = AgentManager().get_instance_obj('demo_agent')
print(instance)
print(instance.output_keys())
if __name__ == '__main__':
    print("Agent Universe started successfully.")
