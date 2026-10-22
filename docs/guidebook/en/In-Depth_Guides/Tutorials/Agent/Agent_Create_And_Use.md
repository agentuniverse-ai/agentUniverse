# How to create agents.
You may have already learned how to quickly create an agent from the [Quick Guide to Building Single Agent](../../../Get_Start/3.Quick_Guide_to_Build_Single_Agent.md) chapter, or you may have grasped the essential components of an agent from the [Principles of Agents](../../../In-Depth_Guides/Tutorials/Agent/Agent.md) section.

Based on the design features of the agentUniverse framework's domain components, the creation process of an agent involves two main parts.
* agent_xx.yaml
* agent_xx.py

Among them, the `agent_xx.yaml` file must be created, which contains crucial attribute information for the agent, such as Introduction, Target, Instruction, LLM, and so forth. The `agent_xx.py` file, on the other hand, is created as needed and includes specific behaviors of the agent, allowing users to inject custom domain-specific behaviors into the agent. With this understanding, let's delve deeper into the creation of these two essential parts.

## Creating Agent Configuration - agent_xx.yaml
We will provide detailed descriptions of each component within the configuration file.

### Setting the basic information of the agent.
**`info` - basic information of the agent**
* `name`:  the name of the agent
* `description`:  a description of the agent's purpose or function 

### Setting the global configurations for the agent.
**`profile` - Agent global settings.**
* `introduction`:  an introduction to the agent's role and responsibilities
* `target`:  the agent's target or intended purpose
* `instruction`: instruction or guidelines for the agent;s behavior
* `llm_model`: the LLM used by the agent
  * `name`: the name of the LLM
  * `model_name`: the specific model name of the LLM

  Note: You can choose any existing LLM or connect to any LLM of your choice. We will not elaborate on this part here; for more details, please refer to the [LLM section](../../../In-Depth_Guides/Tutorials/LLM/LLM.md) .

### Setting the agent's action
**`action` - action of agent**
* `Tool` : Tools available for the agent's use.
  * tool_name_list，list of tool names, for example:  
    \- tool_name_a  
    \- tool_name_b  
    \- tool_name_c  

  Note: You can choose any existing tool or connect to any tool of your choice. We will not elaborate on this part here; you can refer to the [Tool section](../../../In-Depth_Guides/Tutorials/Tool/Tool.md) for more details.

* `Knowledge` : Knowledge available for the agent's use.
  * knowledge_name_list，list of knowledge names, for example:   
    \- knowledge_name_a  
    \- knowledge_name_b  
    \- knowledge_name_c
  
  Note: You can choose any existing Knowledge or connect to any knowledge of your choice. We will not elaborate on this part here; you can refer to the knowledge section for more details.

### Setting up the agent's memory.
**`memory` - memory of agent**

### Setting up component metadata.
**`metadata` - metadata of component**
* `type` : the type of component，use 'AGENT'
* `module`: the package path for the agent entity
* `class`: the class name of the agent entity

All provided Agent components will have their corresponding `module` and `class` details copied into this section. This section serves to integrate all configurations and behaviors of the agent into a cohesive whole. If you have extended the behavior of the agent, you need to fill in this section according to the actual path and class name. We will further elaborate on this  in the "Creating from an Existing Agent Object" section later in the document.

### An actual example of an agent configuration.
```yaml
info:
  name: 'demo_agent'
  description: 'demo agent'
profile:
  introduction: You are an AI assistant proficient in information analysis.
  target: Your goal is to determine whether the answer to a question provides valuable information and to make suggestions and evaluations about the answer.
  instruction: |
    The rules you need to follow are:

    1.Must answer the question posed by the user in Chinese, combining the background information and your knowledge.
    2.Generate structured answers, and when necessary, use blank lines to enhance the reading experience.
    3.Do not adopt incorrect information from the background.
    4.Consider the relevance of the answer to the question, and do not provide answers that are not helpful to the question.
    5.Answer the question comprehensively, with emphasis on the main points, without excessive fancy wording.
    6.Do not make vague speculations.
    7.Use numerical information as much as possible. 
    
    Background information is: {background} 
    
    Begin! 
    
    The question to answer is: {input}
  llm_model:
    name: 'demo_llm'
    model_name: 'gpt-4o'
action:
  tool:
    - 'google_search_tool'
#  knowledge:
#    - 'knowledge_a'
metadata:
  type: 'AGENT'
  module: 'sample_standard_app.intelligence.agentic.agent.agent_instance.demo_agent'
  class: 'DemoAgent'
```
The above is an actual example of an agent configuration. Besides the standard configuration items introduced above, those of you who are observant may have noticed variables in the prompt, such as `{background}` and `{input}`. This is a very practical prompt replacement feature, which we will explain further in the section titled "[How to dynamically adjust settings based on user input](#How to dynamically adjust settings based on user input)".

In addition, agentUniverse does not restrict users from extending the YAML configuration content for agents. You can create any custom configuration keys according to your own requirements, but please ensure that you do not duplicate the default configuration keywords mentioned above.

## Creating Agent Domain Behavior Definition agent_xx.py
In this section, you can orchestrate and customize the behavior of any agent. Of course, if you are solely utilizing existing agent capabilities, this section may not be mandatory.

In this section, we will focus on commonly used definitions for agent domain behavior and the techniques you may employ in the actual process of defining these behaviors.

### Create an Agent class object.
Create the corresponding agent class object by inheriting from the base class agent provided by the agentUniverse framework.

### Customize the corresponding agent domain behaviors.
Common customizable agent behaviors include the  follows:

#### input_keys method
This method represents the list of input key parameters from users during the agent's execution process. It must be implemented by each custom Agent class. 

For instance, if the agent operates with only one parameter passed in, such as question=xxx, then the input_keys method should return ['question'].

#### output_keys method
This method represents the list of output key parameters when the agent's execution completes. It must be implemented by each custom Agent class. 

For example, if the agent produces an output that contains a response, then the output_keys method should return ['response'].

#### parse_input method
The parse_input method serves as the input processing stage before agent execution. An agent's input can be in the form of natural language or structured data such as JSON. This part allows you to process any user input, and it must be implemented by each custom Agent class.

This method has two input parameters:

* `input_object`: The raw data inputted to the agent.
  * You can retrieve corresponding data from input_object using the `input_object.get_data('input_key')` method.
  
    For instance, if a user inputs `question=xxx` to the agent, you can obtain the user's current question by using `input_object.get_data('question')`.

* `agent_input`: The data processed by the agent's input handler, which is of type `dict`.
  * By default, `agent_input` includes the following key parameters and data:
    * `chat_history`:  Contains historical chat data.
    * `background`: Contains background information.
    * `date`: Contains the current date.
  * Append the user input to agent_input.
    * For example: `agent_input['input'] = input_object.get_data('question')`.
  
The output object for the `parse_input` method is typically the modified `agent_input`.

#### parse_result method
The parse_result method serves as the output processing node before agent execution. An agent's output can be in the form of natural language or structured data such as JSON. This part allows you to manage any content that needs to be outputted, and it must be implemented by each custom Agent class.

This method has one input parameter:
* `agent_result`: Agent output data, of type `dict`.  
  The output object for the `parse_result` method is typically used `agent_result`.

#### execute method
This method is the core entry point for the agent's execution flow. Users can override this method to customize the execution method for any agent.

##### Custom execute implementation.
You can customize the execution flow of the agent by overriding the execute method. 

Below is an example of a custom execute method implementation:
```text
def execute(self, input_object: InputObject, agent_input: dict) -> dict:
    # Do anything, as exemplified below.
    
    # Invoke tool A to get data.
    
    # Analyze the data and determine whether it can answer the user's questions.
    
    # Organize language to answer questions.
    
    # Output the answer.
    
    return {'output': 'xxx'}
```

#### Get the properties of the agent object.
Through `self.agent_model`, the agent object can access its properties. In the definition of agent domain behaviors, you can read all the properties configured in the agent's configuration section.

A specific example is as follows:
```text
def process_llm(self, **kwargs) -> LLM:
    llm_name = kwargs.get('llm_name') or self.agent_model.profile.get('llm_model', {}).get('name')
    return LLMManager().get_instance_obj(llm_name)
```

In this example, within the execution method, the `profile` section from the agent's configuration attributes is accessed using `self.agent_model.profile`, and further, the actual name of the `llm_model` is obtained through the get method.


The properties and domain behaviors of the agent are both dependent on the Agent base class in the agentUniverse framework, which is located at `agentuniverse.agent.agent.Agent`. We will also delve into the underlying objects in the sections discussing agents and related domain objects. If you are interested in the underlying technical implementation, you can further refer to the corresponding code and documentation.

#### An actual example of an agent domain behavior definition.
```python
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class DemoAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        llm: LLM = self.process_llm()
        prompt: Prompt = self.process_prompt(agent_input)
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object)
        return {**agent_input, 'output': res}
```
The above provides an actual example of an agent domain behavior definition.


## Pay attention to the package path where your defined agent is located
With the agent configuration and domain definition provided above, you have now mastered all the steps required to create an agent. Next, we will proceed to use these agents. Before doing so, please ensure that the created agents are located within the correct package scanning path.

In the `config.toml` file of the agentUniverse project, you need to configure the package that corresponds to your agent file. Please confirm once again that the package path where your created file is located falls under the `CORE_PACKAGE` in the `agent` path or one of its subpaths.

Taking the configuration of the example project as a reference, it would look something like this:

```yaml
[CORE_PACKAGE]
# Scan and register agent components for all paths under this list, with priority over the default.
agent = ['sample_standard_app.intelligence.agentic.agent']
```

## Other techniques for agent development
### Customize and orchestrate the execution process of agents freely
In the [Creating Agent Domain Behavior Definitions](#Creating Agent Domain Behavior Definition-agent_xx.py) section of this document, we have already detailed how to customize an execute method. This method is often used in practice to customize processes and inject SOPs (Standard Operating Procedures) according to user demands.

### How to dynamically adjust settings based on user input

**Method 1 (Recommended): Through the standard prompt template variable replacement method.**  

In the [An actual example of an agent configuration](#An actual example of an agent configuration.) section of this document, the prompt includes variables like `{background}`,`{input}`, etc. This feature is the prompt variable template replacement function, aimed at dynamically influencing the prompt based on the user's input. One only needs to define the text using  `{variable}` format in the agent configuration settings section and then define the corresponding variables in the `agent_input` method's agent_input to dynamically replace the prompt based on the input portion.

For example, in the sample agent `sample_standard_app.intelligence.agentic.agent.agent_instance.demo_agent.py`, there is the following `parse_input` method.

```text
def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
    agent_input['input'] = input_object.get_data('input')
    return agent_input
```

In its agent settings file `sample_standard_app.intelligence.agentic.agent.agent_instance.demo_agent.yaml`, in the `instruction` section, we can see the following configuration.

```text
instruction: |
    The rules you need to follow are:

    1.Must answer the question posed by the user in Chinese, combining the background information and your knowledge.
    2.Generate structured answers, and when necessary, use blank lines to enhance the reading experience.
    3.Do not adopt incorrect information from the background.
    4.Consider the relevance of the answer to the question, and do not provide answers that are not helpful to the question.
    5.Answer the question comprehensively, with emphasis on the main points, without excessive fancy wording.
    6.Do not make vague speculations.
    7.Use numerical information as much as possible. 
    
    Background information is: {background} 
    
    Begin! 
    
    The question to answer is: {input}
```

Through this process, we can incorporate each input, memory or background knowledge, and any other information you care about into the interaction between the agent and the LLM using this method.

**Method 2: Adjust the prompt within the parse_input method or the execute method**

Through the agent's `parse_input` method or `execute` method, we can customize the agent's  data or behavior. Additionally, by combining the get method in `self.agent_model` with the agent input parameter `input_object`, this means that you can modify any of your settings content through these customization methods.

### Create an agent from an existing agent object

In the actual process of creating applications, we may have many agents of the same type. For instance, we might want to create several Retrieval Augmented Generation (RAG) type agents for use in various question-answering scenarios. By analyzing their similarities and differences, it is not difficult to discern that most RAG type agents share certain commonalities while also exhibiting distinct differences:

* Main similarity: They often need to retrieve multiple types of knowledge simultaneously.
* Main difference: RAG agents deployed in different scenarios require the use of different retrieval tools and may have distinct global agent settings.

Upon further analysis, we realize that we can achieve this differentiation through the use of a common domain behavior definition coupled with differentiated attribute configurations. This underscores the importance of configuring settings in YAML during the agent creation process, while domain behavior customization should be based on actual needs.

Fortunately, we have a substantial number of effective agent types available, and this list is continually expanding. As illustrated in this case, by leveraging the agent domain component setting process, we simply need to create different types of agent configuration YAMLs and set the appropriate metadata to accomplish our goals.


For example:

**Financial RAG Agent Settings**
```yaml
info:
  name: 'financial_RAG_agent'
  description: 'demo financial rag agent'
profile:
  introduction:  Demo introduction, such as you are a financial RAG agent.
  target: Demo target, such as use financial tools to retrieve and enhance answer performance.
  instruction: |
    demo instruction, xxx, {input}
  llm_model:
    name: 'demo_llm'
    model_name: 'gpt-4o'
action:
  tool:
    - 'financial_data_tool'
metadata:
  type: 'AGENT'
  module: 'agentuniverse.agent.default.rag_agent.rag_agent'
  class: 'RagAgent'
```

**Tech RAG Agent Settings**
```yaml
info:
  name: 'tech_RAG_agent'
  description: 'demo tech rag agent'
profile:
  introduction:  Demo introduction, such as you are a tech RAG agent.
  target: Demo target, such as use tech tools to retrieve and enhance answer performance.
  instruction: |
    demo instruction, xxx, {input}
  llm_model:
    name: 'demo_llm'
    model_name: 'gpt-4o'
action:
  tool:
    - 'tech_data_tool'
metadata:
  type: 'AGENT'
  module: 'agentuniverse.agent.default.rag_agent.rag_agent'
  class: 'RagAgent'
```

You can find more information about existing agents and understand their roles in the [Learn more about agents](#Learn more about agents) section of this document.

# How to Use an Agent
In the agentUniverse, all agent entities are managed by a global agent manager. If you need to utilize an agent during any framework execution process, you can do so through the agent manager. Additionally, by leveraging the framework's service capabilities, you can quickly turn an agent into a service and make network calls to it using standard HTTP or RPC protocols.

## Solution 1: Use the agent manager

Through the `get_instance_obj('agent_name_xxx')` method in the agent manager, you can obtain the agent instance with the corresponding name. 
Furthermore, the agent can be utilized through its own `run(input='xxx')` method. The `test_demo_agent(self)` method in the test class below demonstrates how to debug the agent using this approach.

```python
import unittest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse


class DemoAgentTest(unittest.TestCase):
    """
    Test cases for the demo agent
    """

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')

    def test_demo_agent(self):
        """Test demo agent."""
        instance: Agent = AgentManager().get_instance_obj('demo_agent')
        output_object: OutputObject = instance.run(input="What is the reason for the sharp rise in Nvidia's stock?")
        print(output_object.get_data('output'))

if __name__ == '__main__':
    unittest.main()
```

## Solution 2: Utilize the service capabilities of agent_serve

The agentUniverse offers a variety of standard web server capabilities, along with standard HTTP and RPC protocols. You can further refer to the documentation sections on [Service Registration and Usage](../../../In-Depth_Guides/Tech_Capabilities/Service/Service_Registration_and_Usage.md) , as well as  [Web_Server](../../../In-Depth_Guides/Tech_Capabilities/Service/Web_Server.md) section.

# Learn more about agents
The agents provided by the framework can be found under the `agentuniverse.agent.default` package path. You can further explore the corresponding code or learn more about them in our extension component introduction section.

# Conclusion
By now, you have mastered all the content related to the creation and use of agents. Let's use this knowledge to customize your own exclusive agent.