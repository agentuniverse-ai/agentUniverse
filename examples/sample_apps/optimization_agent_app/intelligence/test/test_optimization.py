import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject

# Initialize AgentUniverse
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'config.toml')
print(f"Loading config from: {config_path}")
AgentUniverse().start(config_path=config_path)

def test_prompt_optimization():
    agent_name = 'demo_optimization_agent'
    agent: Agent = AgentManager().get_instance_obj(agent_name)
    
    if not agent:
        print(f"Agent '{agent_name}' not found.")
        return

    print(f"Running agent: {agent_name}")
    
    input_object = InputObject({
        "input": "Explain the concept of quantum entanglement.",
        "samples": [
            "Explain gravity.",
            "Explain black holes."
        ],
        "initial_prompt": "You are a physics teacher.",
        "batch_size": 2,
        "max_iterations": 2
    })
    
    result = agent.run(input_object=input_object)
    print("Optimization Result:")
    print(result.get_data('output'))

if __name__ == "__main__":
    test_prompt_optimization()
