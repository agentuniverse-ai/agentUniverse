# Debate Agent Application

Debate 模式演示应用

## 概述

Debate (辩论) 是一种多智能体协作模式，通过提案、批评和评审三个角色的多轮协作，逐步收敛到高质量结论。该模式特别适合需要多视角分析和严格质量把关的复杂决策场景。

### 核心特性

- **三角色协作**: 提案智能体负责给出方案，批评智能体负责发现问题，评审智能体负责综合裁决
- **多轮辩论**: 支持配置辩论轮数，逐轮改进方案
- **共识收敛**: 基于评分的共识阈值判断，达到阈值后提前结束
- **过程可追溯**: 完整记录每轮的提案、批评与评审结果
- **可配置参数**: 灵活的辩论轮数和共识阈值配置

## 工作流程

```
用户输入
  ↓
循环执行(按轮次):
  1. 提案智能体给出方案
  2. 批评智能体指出问题与改进建议
  3. 评审智能体综合评分并给出最终答案
  4. 评分达到共识阈值 → 提前结束
  5. 记录本轮结果
  ↓
返回最终结果
```

### 三阶段循环

每一轮包含三个阶段:

1. **Proposal (提案)**: 给出针对用户问题的初始或改进方案
2. **Critique (批评)**: 从正确性、完整性、可执行性等角度指出问题
3. **Judgment (评审)**: 综合提案与批评，给出 0-100 分、修改建议和最终答案

## 快速开始

### 1. 安装依赖

```bash
pip install agentuniverse
```

### 2. 配置环境

设置您的 LLM API 密钥:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

### 3. 运行示例

```bash
cd examples/sample_apps/debate_agent_app
python simple_example.py
```

### 4. 运行测试

```bash
cd examples/sample_apps/debate_agent_app
python intelligence/test/test_debate_agent.py
```

## 使用示例

### 基础用法

```python
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

# 初始化
AgentUniverse().start(config_path='config/config.toml')

# 获取 Debate 智能体
agent: Agent = AgentManager().get_instance_obj('demo_debate_agent')

# 执行任务
result = agent.run(
    input='设计一个高并发场景下的短链接生成服务',
    debate_rounds=3,         # 最多辩论 3 轮
    consensus_threshold=80   # 评分达到 80 分提前结束
)

# 获取结果
output = result.get('output', '')
print(output)
```

### 查看完整执行详情

```python
# 获取包含每轮辩论过程的完整输出
full_output = result.get('full_output', '')
print(full_output)
```

### 自定义配置

```python
# 更多轮次、更严格的共识标准
result = agent.run(
    input='为一个图书馆管理系统设计核心数据模型',
    debate_rounds=5,
    consensus_threshold=90
)
```

## 应用场景

### 1. 架构设计

```python
result = agent.run(
    input='设计一个高并发场景下的短链接生成服务，要求给出核心架构、关键数据结构与容错方案',
    debate_rounds=3,
    consensus_threshold=80
)
```

**适用于**:
- 系统架构评审
- 技术方案选型
- 容错与扩展性设计

### 2. 数据模型设计

```python
result = agent.run(
    input='为一个图书馆管理系统设计核心数据模型，并说明主要实体之间的关系',
    debate_rounds=3,
    consensus_threshold=80
)
```

**适用于**:
- 数据库建模
- 实体关系梳理
- 数据一致性方案

### 3. 算法与实现方案

```python
result = agent.run(
    input='判断一个字符串是否为回文串，并说明你的思路',
    debate_rounds=2,
    consensus_threshold=60
)
```

**适用于**:
- 算法思路论证
- 实现方案对比
- 边界条件检查

## 项目结构

```
debate_agent_app/
├── README.md                          # 本文件
├── CHANGELOG.md                       # 版本变更记录
├── simple_example.py                  # 快速开始示例
├── config/
│   ├── config.toml                    # 应用配置
│   └── log_config.toml                # 日志配置
└── intelligence/
    ├── agentic/
    │   ├── agent/
    │   │   └── agent_instance/
    │   │       └── debate_case/
    │   │           ├── demo_debate_agent.yaml      # Debate 协调器配置
    │   │           ├── demo_proposer_agent.yaml    # 提案智能体配置
    │   │           ├── demo_critic_agent.yaml      # 批评智能体配置
    │   │           └── demo_judge_agent.yaml       # 评审智能体配置
    │   ├── llm/
    │   │   └── default_openai_llm.yaml # LLM 配置
    │   ├── memory/
    │   │   └── demo_memory.yaml        # 记忆配置
    │   └── prompt/
    │       └── debate_case/
    │           ├── demo_proposer_agent/
    │           │   └── cn.yaml         # 提案智能体中文提示词
    │           ├── demo_critic_agent/
    │           │   └── cn.yaml         # 批评智能体中文提示词
    │           └── demo_judge_agent/
    │               └── cn.yaml         # 评审智能体中文提示词
    └── test/
        └── test_debate_agent.py        # 单元测试
```

## 配置说明

### Debate 智能体配置

```yaml
name: 'demo_debate_agent'
description: 'Debate agent for consensus-driven problem solving'
agent_type: 'AGENT'
profile:
  proposer: 'demo_proposer_agent'   # 提案智能体
  critic: 'demo_critic_agent'       # 批评智能体
  judge: 'demo_judge_agent'         # 评审智能体
  debate_rounds: 2                  # 默认辩论轮数
  consensus_threshold: 60           # 默认共识阈值
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `debate_rounds` | int | 2 | 最大辩论轮数，运行时可通过 `agent.run` 覆盖 |
| `consensus_threshold` | int | 60 | 评审评分达到该阈值即提前结束 |

### 角色分工

- **Proposer**: 根据用户目标与上一轮批评意见给出方案
- **Critic**: 审查提案的正确性、完整性与可执行性
- **Judge**: 综合提案与批评，输出评分、修改建议与最终答案

## 最佳实践

1. **明确目标**: 在 `input` 中给出清晰的目标和约束，便于三个角色聚焦
2. **合理设置轮数**: 简单任务 1-2 轮即可，复杂设计建议 3 轮以上
3. **调整阈值**: 对质量要求高的场景可提高 `consensus_threshold`
4. **关注过程**: 通过 `full_output` 查看每轮提案与批评，便于人工复核

## 故障排除

- **提示词版本错误**: 确认 `prompt_version` 与 `prompt/debate_case/` 下的文件名一致
- **API 密钥未配置**: 确认已设置 `OPENAI_API_KEY` 环境变量
- **共识未达成**: 属于正常情况，可增加轮数或降低阈值后重试
