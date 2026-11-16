# 使用 Chatbox/CherryStudio 连接 agentUniverse 指南

本文档指导开发者通过 ChatBox 或 CherryStudio 工具，快速接入遵循 OpenAI 协议的 agentUniverse 智能体服务

## 一、环境准备

### 1. 安装客户端工具
选择以下任意一款工具安装：
* ChatBox  
  [下载链接](https://chatboxai.app/zh#download)
* CherryStudio  
  [下载链接](https://cherry-ai.com/download)

### 2. 准备agentUniverse项目
参考aU[快速开始](https://github.com/agentuniverse-ai/agentUniverse/blob/master/README_zh.md)文档，创建一个agentUniverse项目, 并成功启动 demo_agent 示例应用。


## 二、创建 OpenAI 协议兼容智能体
### 1. 定义智能体逻辑
在项目路径 intelligence/agentic/agent/agent_template/ 下创建 openai_protocol_agent.py：

```python

from agentuniverse.agent.input_object import InputObject

from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate


class DemoOpenAIProtocolAgent(OpenAIProtocolTemplate):

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}
```
为了让智能体的输出遵循 OpenAI 协议，必须要继承 OpenAIProtocolTemplate 类。
### 2. 配置智能体实例
在 intelligence/agentic/agent/agent_instance/ 目录创建 openai_protocol_agent.yaml：
```yaml
info:
  #  Please fill in the basic info of your agent. The following is a sample.
  name: 'openai_protocol_agent'
  description: 'demo agent'
profile:
  # Please fill in the profile of your agent. The following is a sample.
  prompt_version: demo_agent.cn
  # Please select the llm.
  llm_model:
    # you can change this config to a customized LLM
    # e.g. demo_llm, which defined in /intelligence/agentic/llm/demo_llm.yaml
    name: 'qwen_25_72b_llm'
action:
  # Please select the tools and knowledge base.
  tool:
    # here we use a mock_search_tool to mock a search result
    # you can change to customized search tool
    # e.g. demo_search_tool, to do a real internet search
    # for using demo_search_tool, you need to get either /Google/Bing/search.io search API key
    # and config it into /config/custom_key.toml
    - 'mock_search_tool'
  knowledge:
  # advantage feature，please refer to doc
memory:
  name: 'demo_memory'
metadata:
  type: AGENT
  class: DemoOpenAIProtocolAgent
```

### 3.创建服务接口
在 intelligence/service/agent_service/ 目录创建 openai_agent_service.yaml：

```yaml
name: 'openai_service'
description: 'demo service of demo agent'
agent: 'openai_protocol_agent'
metadata:
  type: 'SERVICE'
```

### 4. 启动agentUniverse服务
使用bootstrap/intelligence/server_application.py启动agentUniverse服务。 服务启动成功，使用curl命令测试agentUniverse服务。命令为：
```shell
curl -X POST http://127.0.0.1:8888/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "openai_service",
    "messages": [{
      "role": "user",
      "content": "巴菲特抛售比亚迪的原因"
    }],
    "stream": true
  }'
```
响应结果如图：  
<img src="../../../_picture/openai_curl_result.png" width="600" />

## 三、配置客户端工具
1. 启动chatbox，并打开一个会话窗口。打开后的主界面如图：  
  <img src="../../../_picture/chatbox_main_page.png" width="600" />
2. 点击主页中设置按钮，进入设置页面进行配置。  
  <img src= "../../../_picture/chatbox_setting_page.png" width="600" />
  * 配置注意：
    * 配置API域名：http://127.0.0.1:8888
    * 配置API路径：/chat/completions
    * 配置模型：openai_service,即你所创建的agent service
    * API密钥：随意配置
    * 名称：可以任意配置
3. 点击保存
## 4. 测试
* 在chatbox中输入任意内容，点击发送按钮，即可看到agent的输出。如图:  
<img src="../../../_picture/chatbox_test_result.png" width="600" />




