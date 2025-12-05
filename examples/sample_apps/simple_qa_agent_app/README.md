# Simple Q&A Agent | 简单问答智能体

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

### Overview

The **Simple Q&A Agent** is a minimal demonstration application built with the agentUniverse framework. It showcases the core functionality of creating an intelligent conversational agent with just a few configuration files.

This application is designed as a learning resource for developers new to agentUniverse, demonstrating:
- Basic agent configuration
- LLM integration (Qwen/Alibaba DashScope)
- Prompt engineering
- Simple testing workflows

**Perfect for**: Beginners, educational purposes, and as a starting template for more complex applications.

### Features

✅ **Minimal Setup** - Only essential files, no unnecessary complexity
✅ **Bilingual Support** - Responds in Chinese or English based on user input
✅ **Clear Documentation** - Extensive inline comments and examples
✅ **Easy to Extend** - Simple architecture makes it easy to add tools, knowledge bases, or memory
✅ **Test Scripts** - Includes both automated and interactive testing modes

### Architecture

```
simple_qa_agent_app/
├── README.md                           # This file
├── bootstrap/
│   └── intelligence/
│       └── server_application.py      # Application entry point
├── config/
│   ├── config.toml                    # Main configuration
│   ├── log_config.toml                # Logging settings
│   └── custom_key.toml                # API keys (DO NOT commit!)
└── intelligence/
    └── agentic/
        ├── agent/
        │   └── agent_instance/
        │       └── simple_qa_agent.yaml    # Agent definition
        ├── llm/
        │   └── qwen_llm.yaml              # LLM configuration
        ├── prompt/
        │   └── simple_qa_prompt.yaml      # Prompt template
        └── test/
            └── simple_qa_agent_test.py    # Test script
```

### Prerequisites

- Python 3.10 or higher
- agentUniverse framework installed
- Alibaba DashScope API key (or configure alternative LLM)

### Installation & Setup

#### Step 1: Install agentUniverse

```bash
# Install from PyPI
pip install agentUniverse

# Or install from source
git clone https://github.com/agentuniverse-ai/agentUniverse.git
cd agentUniverse
pip install -e .
```

#### Step 2: Configure API Key

1. Get your API key from [Alibaba DashScope](https://dashscope.console.aliyun.com/)

2. Edit `config/custom_key.toml`:
```toml
[KEY_LIST]
DASHSCOPE_API_KEY = 'your-actual-api-key-here'
```

3. **Important**: Add to `.gitignore` (if not already):
```bash
echo "config/custom_key.toml" >> .gitignore
```

#### Step 3: Verify Installation

```bash
cd examples/sample_apps/simple_qa_agent_app
python intelligence/test/simple_qa_agent_test.py
```

### Usage

#### Method 1: Web Server (Recommended)

Start the web server:
```bash
cd examples/sample_apps/simple_qa_agent_app
python bootstrap/intelligence/server_application.py
```

The server will start at `http://localhost:8888`

Test with curl:
```bash
curl -X POST http://localhost:8888/agent_run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "simple_qa_agent",
    "input": "What is machine learning?"
  }'
```

#### Method 2: Python API

```python
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent_manager import AgentManager

# Initialize framework
AgentUniverse().start(config_path='config/config.toml', core_mode=True)

# Get agent instance
agent = AgentManager().get_instance_obj('simple_qa_agent')

# Ask a question
result = agent.run(input="Explain quantum computing")
print(result.get('output'))
```

#### Method 3: Interactive Test Mode

```bash
python intelligence/test/simple_qa_agent_test.py -i
```

### Customization

#### Use a Different LLM

To use OpenAI instead of Qwen:

1. Update `config/custom_key.toml`:
```toml
[KEY_LIST]
OPENAI_API_KEY = 'your-openai-api-key'
```

2. Update `intelligence/agentic/llm/qwen_llm.yaml`:
```yaml
name: 'openai_llm'
model_name: 'gpt-4'
api_key: '${OPENAI_API_KEY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.default_openai_llm'
  class: 'DefaultOpenAILLM'
```

3. Update agent reference in `intelligence/agentic/agent/agent_instance/simple_qa_agent.yaml`:
```yaml
profile:
  llm_model:
    name: 'openai_llm'
```

#### Adjust Response Style

Modify `intelligence/agentic/prompt/simple_qa_prompt.yaml` to change the agent's personality and behavior.

#### Add Tools

1. Create a tool YAML in `intelligence/agentic/tool/`
2. Create tool implementation Python file
3. Add tool reference to agent YAML:
```yaml
action:
  tool:
    - 'your_tool_name'
```

### Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'agentuniverse'`
**Solution**: Install agentUniverse: `pip install agentUniverse`

**Problem**: `API key not found`
**Solution**: Make sure `config/custom_key.toml` contains your API key

**Problem**: `Agent not found`
**Solution**: Verify `config/config.toml` has correct package paths

**Problem**: Web server won't start
**Solution**: Check if port 8888 is already in use

### Contributing

This application is part of agentUniverse's community examples (Issue #254). Contributions are welcome!

- Report bugs or suggest improvements via GitHub Issues
- Submit pull requests with enhancements
- Share your customizations with the community

### License

Same as agentUniverse project license.

### Learn More

- [agentUniverse Documentation](https://github.com/agentuniverse-ai/agentUniverse)
- [agentUniverse Examples](https://github.com/agentuniverse-ai/agentUniverse/tree/master/examples)
- [Issue #254 - Community Examples](https://github.com/agentuniverse-ai/agentUniverse/issues/254)

---

<a name="中文"></a>
## 中文

### 概述

**简单问答智能体**是使用 agentUniverse 框架构建的极简演示应用程序。它仅用几个配置文件就展示了创建智能对话代理的核心功能。

此应用程序被设计为 agentUniverse 新手开发者的学习资源，演示了：
- 基本智能体配置
- LLM集成（通义千问/阿里云灵积）
- 提示词工程
- 简单的测试工作流

**适合**: 初学者、教育目的，以及作为更复杂应用程序的起始模板。

### 功能特性

✅ **极简设置** - 只包含必需文件，没有不必要的复杂性
✅ **双语支持** - 根据用户输入自动使用中文或英文回答
✅ **清晰文档** - 大量内联注释和示例
✅ **易于扩展** - 简单的架构使其易于添加工具、知识库或记忆
✅ **测试脚本** - 包含自动化和交互式测试模式

### 架构

```
simple_qa_agent_app/
├── README.md                           # 本文件
├── bootstrap/
│   └── intelligence/
│       └── server_application.py      # 应用程序入口点
├── config/
│   ├── config.toml                    # 主配置
│   ├── log_config.toml                # 日志设置
│   └── custom_key.toml                # API密钥（请勿提交！）
└── intelligence/
    └── agentic/
        ├── agent/
        │   └── agent_instance/
        │       └── simple_qa_agent.yaml    # 智能体定义
        ├── llm/
        │   └── qwen_llm.yaml              # LLM配置
        ├── prompt/
        │   └── simple_qa_prompt.yaml      # 提示词模板
        └── test/
            └── simple_qa_agent_test.py    # 测试脚本
```

### 先决条件

- Python 3.10 或更高版本
- 已安装 agentUniverse 框架
- 阿里云灵积 API 密钥（或配置替代 LLM）

### 安装与设置

#### 步骤 1：安装 agentUniverse

```bash
# 从 PyPI 安装
pip install agentUniverse

# 或从源码安装
git clone https://github.com/agentuniverse-ai/agentUniverse.git
cd agentUniverse
pip install -e .
```

#### 步骤 2：配置 API 密钥

1. 从[阿里云灵积](https://dashscope.console.aliyun.com/)获取您的 API 密钥

2. 编辑 `config/custom_key.toml`:
```toml
[KEY_LIST]
DASHSCOPE_API_KEY = '您的实际api密钥'
```

3. **重要**: 添加到 `.gitignore`（如果尚未添加）:
```bash
echo "config/custom_key.toml" >> .gitignore
```

#### 步骤 3：验证安装

```bash
cd examples/sample_apps/simple_qa_agent_app
python intelligence/test/simple_qa_agent_test.py
```

### 使用方法

#### 方法 1：Web 服务器（推荐）

启动 Web 服务器：
```bash
cd examples/sample_apps/simple_qa_agent_app
python bootstrap/intelligence/server_application.py
```

服务器将在 `http://localhost:8888` 启动

使用 curl 测试：
```bash
curl -X POST http://localhost:8888/agent_run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "simple_qa_agent",
    "input": "什么是机器学习？"
  }'
```

#### 方法 2：Python API

```python
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent_manager import AgentManager

# 初始化框架
AgentUniverse().start(config_path='config/config.toml', core_mode=True)

# 获取智能体实例
agent = AgentManager().get_instance_obj('simple_qa_agent')

# 提出问题
result = agent.run(input="解释一下量子计算")
print(result.get('output'))
```

#### 方法 3：交互式测试模式

```bash
python intelligence/test/simple_qa_agent_test.py -i
```

### 自定义

#### 使用不同的 LLM

要使用 OpenAI 代替通义千问：

1. 更新 `config/custom_key.toml`:
```toml
[KEY_LIST]
OPENAI_API_KEY = '您的openai密钥'
```

2. 更新 `intelligence/agentic/llm/qwen_llm.yaml`:
```yaml
name: 'openai_llm'
model_name: 'gpt-4'
api_key: '${OPENAI_API_KEY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.default_openai_llm'
  class: 'DefaultOpenAILLM'
```

3. 更新 `intelligence/agentic/agent/agent_instance/simple_qa_agent.yaml` 中的智能体引用:
```yaml
profile:
  llm_model:
    name: 'openai_llm'
```

#### 调整响应风格

修改 `intelligence/agentic/prompt/simple_qa_prompt.yaml` 来改变智能体的个性和行为。

#### 添加工具

1. 在 `intelligence/agentic/tool/` 中创建工具 YAML
2. 创建工具实现的 Python 文件
3. 在智能体 YAML 中添加工具引用:
```yaml
action:
  tool:
    - '您的工具名称'
```

### 故障排除

**问题**: `ModuleNotFoundError: No module named 'agentuniverse'`
**解决方案**: 安装 agentUniverse: `pip install agentUniverse`

**问题**: `找不到 API 密钥`
**解决方案**: 确保 `config/custom_key.toml` 包含您的 API 密钥

**问题**: `找不到智能体`
**解决方案**: 验证 `config/config.toml` 具有正确的包路径

**问题**: Web 服务器无法启动
**解决方案**: 检查端口 8888 是否已被占用

### 贡献

此应用程序是 agentUniverse 社区示例的一部分（Issue #254）。欢迎贡献！

- 通过 GitHub Issues 报告错误或提出改进建议
- 提交带有增强功能的拉取请求
- 与社区分享您的自定义

### 许可证

与 agentUniverse 项目许可证相同。

### 了解更多

- [agentUniverse 文档](https://github.com/agentuniverse-ai/agentUniverse)
- [agentUniverse 示例](https://github.com/agentuniverse-ai/agentUniverse/tree/master/examples)
- [Issue #254 - 社区示例](https://github.com/agentuniverse-ai/agentUniverse/issues/254)
