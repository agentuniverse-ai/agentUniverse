# Product Platform Quick Start
In this section, we will show you how to:

● Initiate the productized service of agentUniverse
● Configure the modules within the agentUniverse framework
● Quickly begin utilizing the productized features
● Debug and test agents online, optimizing agent performance

## Environment and Application Engineering Preparation
### Application Engineering Preparation
We have placed the sample of product module within the sample_standard_app project of agentUniverse. You can access and view them [here](../../../../../examples/sample_apps/difizen_app). These modules can be configured in the background using YAML file, and additionally, the functions can be automatically created and managed via the product page.


### Installing Dependencies
**Using pip**
```shell
pip install magent-ui ruamel.yaml
```

### Configuration File
If you have previously used agentUniverse’s sample project, please add the following information to the `config.toml`  file  to include the product module path as configured in sample_standard_app:
```toml
# Ignore the context content.
[CORE_PACKAGE]
# Scan and register product components for all paths under this list, with priority over the default.
product = ['sample_standard_app.platform.difizen.product']
# Ignore the context content.
```
If you are using agentUniverse for the first time, you can directly adopt the latest sample project’s `config.toml` file.

#### Private Configuration File
Of course, when utilizing the agent, you need to preconfigure the various LLM model keys/Tool keys; otherwise, the agent's overall process will fail to connect. Currently, this configuration is not available in the product page's configuration management. Please continue to use agentUniverse’s original key configuration method. In future versions, we will directly provide key management capabilities for each model within the product.


## Using the agentUniverse Product Platform
### Starting the Product Service
To start the product service with a single click, run the [product_application](../../../../../examples/sample_apps/difizen_app/bootstrap/platform/product_application.py) file located in `sample_standard_app/bootstrap/platform` .
![img.png](../../../_picture/product_start.png)

Upon successful initiation, it will automatically redirect you to the product homepage, which features system presets as well as your customized Agent, Tool and Knowledge product modules.
![agentuniverse_product_homepage](../../../_picture/agentuniverse_product_homepage.png)

### Experience the Agent
As shown in the image above, click the chat button positioned on the right side of the peer multi-agent group to access the conversation page.
The conversation management system incorporates the last 10 conversation history records from agents, enabling you to engage in multi-turn dialogues seamlessly and experience the capabilities of the peer multi-agent group (by default, it is set to streaming dialogue, and the multi-agent group showcases the intermediate thinking process).
![agentuniverse_product_agent_chat](../../../_picture/agentuniverse_product_agent_chat.png)

### Debugging the Agent
On the product homepage, click the edit button on the left of the agent to access the online debugging page.
You have the ability to debug the agent's Prompt, Tool, Knowledge, and LLM online. Simply click the save button, and the aU-product (AgentUniverse framework) will automatically save the configuration to the corresponding YAML file.
![agentuniverse_product_agent_editor](../../../_picture/agentuniverse_product_agent_editor.png)

To view the Trace information, including token consumption, call chain, and latency of the agent's specific invocation process, click the debug button located in the upper right corner of the image provided above.
![agentuniverse_product_agent_trace](../../../_picture/agentuniverse_product_agent_trace.png)

## Configuring agentUniverse Product Modules
### Creating Product Modules
```yaml
id: demo_rag_agent
nickname: rag智能体
type: AGENT
opening_speech: |
  欢迎使用rag chatbot！根据您的提问，我将结合实时信息及我个人掌握的知识，给您提供合理的解答。
  你可以这样问我：
  问题1: 巴黎奥运会中国获得了几块奖牌
  问题2: 巴菲特为什么减持苹果股票
avatar: ../../../resources/rag_agent_logo.png
metadata:
  class: AgentProduct
  module: agentuniverse_product.base.agent_product
  type: PRODUCT
```

As shown in the yaml file above:

- `product id` corresponds to `name` in the agent yaml
- `type` corresponds to `AGENT`
- `metadata` is configured as the value shown above
- Other parameters can be configured as needed (the same applies to tool/knowledge modules)

### Configuring Global Config
In the `config.toml`file for global settings, configure the package scan path that corresponds to the product module. With a single click, you can launch the product platform and view the corresponding agent, tool, and knowledge information.

## More
The AgentUniverse product platform is undergoing continuous iteration, and in the future, even more convenient and useful features will be available for community users to experience. We warmly welcome your valuable suggestions and feedback.
This feature has been jointly launched by [difizen](https://github.com/difizen/magent) and agentUniverse.
Let's explore and make progress together!