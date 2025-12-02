# GRR Agent App - Generate-Review-Rewrite Pattern

## 概述

GRR (Generate-Review-Rewrite) 是一个用于内容生成任务的多智能体协作模式。该模式通过三个不同职责的智能体实现内容的迭代式优化：

- **Generating Agent (生成智能体)**: 根据用户需求生成初始内容
- **Reviewing Agent (评审智能体)**: 评估生成内容的质量并提供改进建议
- **Rewriting Agent (重写智能体)**: 基于评审反馈优化和重写内容

## 架构设计

### Work Pattern 层

**GRRWorkPattern** (`agentuniverse/agent/work_pattern/grr_work_pattern.py`)
- 继承自 `WorkPattern` 基类
- 实现同步和异步调用方法
- 支持可配置的迭代次数和质量阈值
- 自动进行质量评估和迭代优化

### Agent Template 层

1. **GRRAgentTemplate** (协调器)
   - 文件：`agentuniverse/agent/template/grr_agent_template.py`
   - 职责：协调三个子智能体的执行
   - 管理expert framework和memory

2. **GeneratingAgentTemplate** (生成智能体)
   - 文件：`agentuniverse/agent/template/generating_agent_template.py`
   - 职责：根据用户需求创建内容
   - 输入：用户需求
   - 输出：生成的内容

3. **ReviewingAgentTemplate** (评审智能体)
   - 文件：复用现有的 `agentuniverse/agent/template/reviewing_agent_template.py`
   - 职责：评估内容质量，提供分数和改进建议
   - 输入：原始需求 + 生成的内容
   - 输出：评分 (0-100) + 评审意见 + 改进建议

4. **RewritingAgentTemplate** (重写智能体)
   - 文件：`agentuniverse/agent/template/rewriting_agent_template.py`
   - 职责：基于评审反馈改进内容
   - 输入：原始需求 + 生成内容 + 评审反馈
   - 输出：改进后的内容

## 工作流程

```
用户输入
    ↓
生成内容 (Generating Agent)
    ↓
评审内容 (Reviewing Agent)
    ↓
评分 >= 阈值? ──→ 是 ──→ 输出结果
    ↓ 否
重写内容 (Rewriting Agent)
    ↓
(重复评审和重写，直到达到阈值或最大迭代次数)
```

## 配置参数

在 GRR Agent 配置中可以设置以下参数：

- **retry_count**: 最大迭代次数 (默认: 2)
- **eval_threshold**: 质量评分阈值 (默认: 60，范围 0-100)
- **generating**: 生成智能体的名称
- **reviewing**: 评审智能体的名称
- **rewriting**: 重写智能体的名称

### 示例配置

```yaml
info:
  name: 'demo_grr_agent'
  description: 'Demo GRR agent for content generation'
profile:
  generating: 'demo_generating_agent'
  reviewing: 'demo_reviewing_agent'
  rewriting: 'demo_rewriting_agent'
  eval_threshold: 60
  retry_count: 2
memory:
  name: 'demo_memory'
metadata:
  type: 'AGENT'
  module: 'agentuniverse.agent.template.grr_agent_template'
  class: 'GRRAgentTemplate'
```

## 快速开始

### 1. 安装依赖

确保已安装 agentUniverse 框架。

### 2. 配置 LLM

在 `intelligence/agentic/llm/qwen_llm.yaml` 中配置您的 LLM：

```yaml
name: 'qwen_llm'
description: 'Qwen LLM configuration'
model_name: 'qwen-max'
max_tokens: 4096
temperature: 0.7
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.default_openai_llm'
  class: 'DefaultOpenAILLM'
```

### 3. 配置 API Keys

在 `config/custom_key.toml` 中添加您的 API keys（该文件应添加到 .gitignore）。

### 4. 运行测试

```bash
cd examples/sample_apps/grr_agent_app
python -m intelligence.test.test_grr_agent
```

### 5. 使用示例

```python
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

# 启动 AgentUniverse
AgentUniverse().start(config_path='config/config.toml')

# 获取 GRR agent 实例
grr_agent: Agent = AgentManager().get_instance_obj('demo_grr_agent')

# 运行 agent
result = grr_agent.run(input='写一篇关于人工智能的短文')

# 获取结果
output = result.get('output')
print(output)
```

## 目录结构

```
grr_agent_app/
├── config/
│   ├── config.toml          # 主配置文件
│   ├── log_config.toml      # 日志配置
│   └── custom_key.toml      # API密钥 (不提交到git)
├── intelligence/
│   ├── agentic/
│   │   ├── agent/
│   │   │   └── agent_instance/
│   │   │       └── grr_agent_case/
│   │   │           ├── demo_grr_agent.yaml
│   │   │           ├── demo_generating_agent.yaml
│   │   │           ├── demo_reviewing_agent.yaml
│   │   │           └── demo_rewriting_agent.yaml
│   │   ├── llm/
│   │   │   └── qwen_llm.yaml
│   │   ├── memory/
│   │   │   └── demo_memory.yaml
│   │   └── prompt/
│   │       └── grr_agent_case/
│   │           ├── demo_generating_agent/
│   │           │   └── cn.yaml
│   │           ├── demo_reviewing_agent/
│   │           │   └── cn.yaml
│   │           └── demo_rewriting_agent/
│   │               └── cn.yaml
│   └── test/
│       └── test_grr_agent.py
└── README.md
```

## 使用场景

GRR 模式特别适合以下场景：

1. **内容创作**: 文章、报告、文案等需要多次迭代优化的内容
2. **创意写作**: 故事、剧本等需要反复推敲的创作任务
3. **技术文档**: API文档、用户手册等需要准确性的文档
4. **营销文案**: 产品介绍、广告文案等需要吸引力的内容
5. **学术写作**: 论文摘要、研究报告等需要严谨性的内容

## 扩展和定制

### 自定义 Prompt

您可以通过修改 `intelligence/agentic/prompt/grr_agent_case/` 下的 YAML 文件来定制各个智能体的提示词。

### 调整质量阈值

根据您的具体需求，可以在 agent 配置中调整 `eval_threshold` 参数：
- 较高阈值 (70-90): 要求更高的内容质量，可能需要更多迭代
- 中等阈值 (50-70): 平衡质量和效率
- 较低阈值 (30-50): 快速生成，适合对质量要求不太严格的场景

### Expert Framework

GRR 模式支持 expert framework，允许您为不同领域提供专门的指导：

```yaml
expert_framework:
  context:
    generating: "针对医疗领域内容，确保使用准确的医学术语..."
    reviewing: "从医学准确性、患者理解度等维度评估..."
    rewriting: "保持医学专业性的同时提升可读性..."
```

## 与 PEER 模式的对比

| 特性 | PEER 模式 | GRR 模式 |
|-----|---------|---------|
| 智能体数量 | 4 个 | 3 个 |
| 主要用途 | 复杂问题分析和推理 | 内容生成和优化 |
| 核心流程 | Plan → Execute → Express → Review | Generate → Review → Rewrite |
| 并行执行 | 支持 (Execute阶段) | 不支持 |
| 迭代方式 | 全流程迭代 | 生成-评审-重写循环 |
| 适用场景 | 研究分析、问题求解 | 内容创作、文档生成 |

## 贡献

欢迎为 GRR 模式贡献代码和文档！请查看项目的主 CONTRIBUTING.md 文件了解贡献指南。

## 问题反馈

如果您遇到问题或有改进建议，请在 GitHub Issues 中提交：
https://github.com/agentuniverse-ai/agentUniverse/issues

## 许可证

本项目遵循 agentUniverse 主项目的许可证。

## 参考资料

- [agentUniverse 官方文档](https://github.com/agentuniverse-ai/agentUniverse)
- [PEER 模式文档](https://github.com/agentuniverse-ai/agentUniverse/tree/master/examples/sample_apps/peer_agent_app)
- [GitHub Issue #257](https://github.com/agentuniverse-ai/agentUniverse/issues/257)
