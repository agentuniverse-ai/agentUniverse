# How to Define a Planner Component (Deprecated)

> **Note:** The Planner component has been deprecated in the new version. Please use Agent Templates instead. See the migration guide on the [Planner](Planner.md) page.

Based on the design features of agentUniverse domain components, creating a Planner definition involves two parts, similar to other components:

* planner_xx.yaml
* planner_xx.py
The `planner_xx.yaml` file contains important information about the Planner component, such as its name, description, input, output, etc. The `planner_xx.py` file contains the specific behavior definitions of the Planner. With this understanding, let's see how to create these two parts in detail.

## Creating the Planner Configuration - planner_xx.yaml
We will detail the various components in the configuration.

### Setting Basic Attributes of the Planner
* `name`:  The name of the Planner, which can be set to any unique identifier you prefer.
* `description`:  A description of the Planner
* `input_key`: Defaults to "input," represents the key for actual input
* `output_key`: Defaults to "output," represents the key for actual output

### Setting Planner Component Metadata
**`metadata` - Component Metadata**
* `type` : Component type, 'PLANNER'
* `module`: The package path of the Planner entity
* `class`: The class name of the Planner entity

### A Sample Planner Configuration
```yaml
name: 'expressing_planner'
description: 'expressing planner'
metadata:
  type: 'PLANNER'
  module: 'agentuniverse.agent.plan.planner.expressing_planner.expressing_planner'
  class: 'ExpressingPlanner'
```

The above is an actual sample of a Planner configuration. 

Besides, the standard configuration items mentioned above, you can find more planner configuration YAML samples in the `agentuniverse.agent.plan.planner` path in the project. 

Additionally, agentUniverse does not restrict users from extending the Planner YAML configuration content. You can create any custom configuration keys according to your requirements, but please be mindful not to use the same names as the default configuration keywords mentioned above.

## Creating the Planner Domain Behavior Definition - planner_xx.py

### Create the Planner Class Object
Create the corresponding Planner class object and inherit the base class Planner from the agentUniverse framework.

### Implement the Invoke Method in the Planner Class Object
Write the actual logic fragments for the plan in the `invoke` method.

```text
def invoke(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
    """Invoke the planner.

    Args:
        agent_model (AgentModel): Agent model object.
        planner_input (dict): Planner input object.
        input_object (InputObject): The input parameters passed by the user.
    Returns:
        dict: The planner result.
    """
    planner_config = agent_model.plan.get('planner')
    sub_agents = self.generate_sub_agents(planner_config)
    return self.agents_run(sub_agents, planner_config, planner_input, input_object)
```

The above example uses a peer planner to illustrate, where it selects the various sub-agents in PEER mode and runs them accordingly. We will elaborate further on the working principles of PEER in its respective section.

Similarly, the following non-mandatory methods will not be elaborated here. It is recommended to refer to an actual planner source code for a comprehensive understanding, such as `agentuniverse.agent.plan.planner.planning_planner.planning_planner`.

### Implement the handle_prompt Method
The `handle_prompt` method handles prompt processing within the planner. It is optional.

### Implement the handle_memory Method
The `handle_memory` method handles memory processing within the planner. It is optional.

### Implement the handle_all_actions Method
The `handle_all_actions` method handles all action processing within the planner. It is optional.

### Implement the handle_llm Method
The `handle_llm` method handles LLM processing within the planner. It is optional.

#### A Sample Planner Object Definition
```python
import asyncio

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.memory_util import generate_memories
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel


class RagPlanner(Planner):
    """Rag planner class."""

    def invoke(self, agent_model: AgentModel, planner_input: dict,
               input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """
        memory: ChatMemory = self.handle_memory(agent_model, planner_input)

        self.run_all_actions(agent_model, planner_input, input_object)

        llm: LLM = self.handle_llm(agent_model)

        prompt: ChatPrompt = self.handle_prompt(agent_model, planner_input)
        process_llm_token(llm, prompt.as_langchain(), agent_model.profile, planner_input)

        chat_history = memory.as_langchain().chat_memory if memory else InMemoryChatMessageHistory()

        chain_with_history = RunnableWithMessageHistory(
            prompt.as_langchain() | llm.as_langchain(),
            lambda session_id: chat_history,
            history_messages_key="chat_history",
            input_messages_key=self.input_key,
        )
        res = asyncio.run(
            chain_with_history.ainvoke(input=planner_input, config={"configurable": {"session_id": "unused"}}))
        return {**planner_input, self.output_key: res.content}

    def handle_prompt(self, agent_model: AgentModel, planner_input: dict) -> ChatPrompt:
        """Prompt module processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
        Returns:
            ChatPrompt: The chat prompt instance.
        """
        profile: dict = agent_model.profile

        profile_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                                  target=profile.get('target'),
                                                                  instruction=profile.get('instruction'))

        # get the prompt by the prompt version
        prompt_version: str = profile.get('prompt_version')
        version_prompt: Prompt = PromptManager().get_instance_obj(prompt_version)

        if version_prompt is None and not profile_prompt_model:
            raise Exception("Either the `prompt_version` or `introduction & target & instruction`"
                            " in agent profile configuration should be provided.")
        if version_prompt:
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(version_prompt, 'introduction', ''),
                target=getattr(version_prompt, 'target', ''),
                instruction=getattr(version_prompt, 'instruction', ''))
            profile_prompt_model = profile_prompt_model + version_prompt_model

        chat_prompt = ChatPrompt().build_prompt(profile_prompt_model, self.prompt_assemble_order)
        image_urls: list = planner_input.pop('image_urls', []) or []
        if image_urls:
            chat_prompt.generate_image_prompt(image_urls)
        return chat_prompt
```

The above is an actual sample based on the Rag planner. Further details will be provided in the section introducing the Rag planner.

## Make Sure Your Planner is in the Correct Package Path
With the above Planner configuration and definition, you have learned all the steps for creating a Planner. Next, we will use these Planners. Before using them, ensure the created Planner is in the correct package scan path.

In the config.toml file of the agentUniverse project, you need to configure the package corresponding to the Planner configuration. Please confirm whether the package path of the created file is under the `CORE_PACKAGE`'s `planner` path or its subpaths. 

Here is an example configuration from the sample project:

```yaml
[CORE_PACKAGE]
# Scan and register planner components for all paths under this list, with priority over the default.
planner = ['sample_standard_app.app.core.planner']
```

# How to Use the Planner Component
## Configuring Use in the Agent
Following the [Creating and Using Agents guide](../Agent/Agent_Create_And_Use.md), you can set up any created Planner component in the agent's planner section. Refer to the example: `demo_rag_agent`, with the specific file path `sample_standard_app/intelligence/agentic/agent/agent_instance/rag_agent_case/demo_rag_agent.yaml`.

## Using the Planner Manager
You can get the Planner instance corresponding to its name using the `.get_instance_obj(xx_planner_name)` method in the Planner Manager and call it using the `invoke` method.

```python
from agentuniverse.agent.plan.planner.planner_manager import PlannerManager

planner_base = PlannerManager().get_instance_obj('xx_planner_name')
planner_result = planner_base.invoke(self.agent_model, agent_input, input_object)
```

# Learn More About Existing Planner Components
You can find more Planner components in the `agentuniverse.agent.plan.planner` package path. You can further check the corresponding code or learn more about them in our extension component introduction section. For more integrated Planners, you can refer to the Planner list chapter.

# Conclusion
Now you have mastered the definition and use of Planners. Go ahead and try defining and using your own Planners.