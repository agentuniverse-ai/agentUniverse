# How to Define a Tool Component
In accordance with the design characteristics of agentUniverse domain components, like other components, creating a Tool definition consists of two parts:
* tool_xx.yaml
* tool_xx.py

The `tool_xx.yaml` contains important attribute information about the Tool component such as its name, description, inputs, outputs, etc.; `tool_xx.py` includes the specific definition of the tool. Having understood this principle, let's take a closer look at how to create these two parts.

## Creating Tool Configuration - tool_xx.yaml
We will provide a detailed introduction to each component within the configuration.

### Setting Basic Properties of the Tool
* `name`:  The name of the tool, you can set any name you desire.
* `description`:  A description of the tool, fill in according to your actual requirements.
* `input_keys`: A `list` type, list of input parameters.

### Setting Tool Component Metadata
**`metadata` - metadata of component**
* `type`: The component type, 'TOOL'
* `module`: Path to the Tool entity package
* `class`: Name of the Tool entity class

### An actual example of a Tool definition configuration.
```yaml
name: 'google_search_tool'
description: 'demo google search tool'
input_keys: ['input']
metadata:
  type: 'TOOL'
  module: 'xxx.tool.google_search_tool'
  class: 'GoogleSearchTool'
```

The above is an actual example of a Tool configuration sample. 

In addition to the standard configuration items introduced above, you can find more examples of tool configuration YAML files in the `sample_standard_app.intelligence.agentic.tool` directory of our sample project.

Moreover, agentUniverse does not restrict users from extending the Tool YAML configuration content. You can create any custom configuration keys according to your own requirements, but please be careful not to duplicate the names of the default configuration keywords mentioned above.

## Creating Tool Domain Behavior Definition - tool_xx.py

### Creating Tool Class Object
Create the corresponding Tool class object and inherit from the agentUniverse framework base class `Tool`.

### Writing the Tool Class Object's execute Method
Write the actual logic snippet of the tool in the `execute` method.

```text
@abstractmethod
def execute(self, tool_input: ToolInput):
    raise NotImplementedError
```

#### An actual example of a tool object definition.
```python
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from agentuniverse.agent.action.tool.tool import Tool, ToolInput

class GoogleSearchTool(Tool):
    """The demo google search tool.

    Implement the execute method of demo google search tool, using the `GoogleSerperAPIWrapper` to implement a simple Google search.

    Note:
        You need to sign up for a free account at https://serper.dev and get the serper api key (2500 free queries).
    """

    def execute(self, tool_input: ToolInput):
        query = tool_input.get_data("input")
        # get top3 results from Google search.
        search = GoogleSerperAPIWrapper(serper_api_key='', k=3, type="search")
        return search.run(query=query)
```
In this example, we integrated Google's search tool, which retrieves and returns the three most relevant pieces of content related to the search query.

## Pay attention to the package path where your defined Tool is located.
With the Tool configuration and definition covered above, you have mastered all the steps of creating tools. Next, we will use these Tools, but before using them, please ensure that the created Tool is within the correct package scan path.

In the config.toml of the agentUniverse project, you need to configure the package corresponding to the Tool configuration. Please confirm again if the package path where your created file is located is under the `CORE_PACKAGE` in the `tool` path or its subpaths.

Taking the configuration in the example project as an example, it is as follows.
```yaml
[CORE_PACKAGE]
# Scan and register tool components for all paths under this list, with priority over the default.
tool = ['sample_standard_app.intelligence.agentic.tool']
```

# How to Use the Tool Component
## Configure for use in an Agent
You can set up any tool you have created in the tool of your agent according to the contents of [Agent Creation and Usage section](../Agent/Agent_Create_And_Use.md).

For examples of tool definitions, please refer to [python_runner](../../../../../../examples/sample_apps/toolkit_demo_app/intelligence/agentic/tool/python_runner.yaml)

For examples of tool calls, please refer to [demo_agent_with_basic_tool.yaml](../../../../../../examples/sample_apps/toolkit_demo_app/intelligence/agentic/agent/agent_instance/demo_agent_with_basic_tool.yaml)

## Using the Tool Manager
You can obtain the instance of the tool with the corresponding name through the `.get_instance_obj(xx_tool_name)` method in the Tool manager, and call it using the `run` method.

```python
from agentuniverse.agent.action.tool.tool_manager import ToolManager

tool = ToolManager().get_instance_obj('your_tool_name')
tool_input = {'your_input_key': 'input_values'}
tool.run(**tool_input)
```

# Learn More About Existing Tools
More examples of tools provided by the framework can be found in the `sample_standard_app.intelligence.agentic.tool` package path, where you can further explore the corresponding tools.

# Conclusion
By now, you have mastered the definition and usage of Tool components. Go ahead and try creating and using tools.
