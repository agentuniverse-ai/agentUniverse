# Changelog

All notable changes to the Debate Agent Application will be documented in this file.

## [1.0.0] - 2026-10-18

### Added - 初始发布

#### 核心框架
- ✅ 实现 `DebateWorkPattern` 类，支持多轮辩论式共识决策
  - 同步执行 (`invoke` 方法)
  - 异步执行 (`async_invoke` 方法)
  - 可配置的辩论轮数 (debate_rounds)
  - 可配置的共识阈值 (consensus_threshold)
  - 达到阈值后提前结束
  - 完整的每轮提案、批评与评审记录

- ✅ 实现 `ProposerAgentTemplate` 类
  - 方案生成功能
  - 轮次索引跟踪
  - 上一轮批评意见输入
  - 执行上下文管理
  - Expert framework 支持

- ✅ 实现 `CriticAgentTemplate` 类
  - 提案审查功能
  - 多维度问题识别
  - 结构化改进建议
  - 执行上下文管理
  - Expert framework 支持

- ✅ 实现 `JudgeAgentTemplate` 类
  - 综合评审功能
  - 0-100 分量化评分
  - JSON 结构化输出解析
  - 最终答案生成
  - Expert framework 支持

- ✅ 实现 `DebateAgentTemplate` 协调器
  - 子智能体管理
  - 工作模式协调
  - Expert framework 构建
  - Memory 集成
  - Stream output 支持

#### 配置系统
- ✅ YAML 配置支持
  - `debate_work_pattern.yaml` - 工作模式配置
  - Agent 配置文件 (Debate/Proposer/Critic/Judge)
  - LLM 配置文件
  - Memory 配置文件

- ✅ 灵活的参数配置
  - Profile 级别默认值
  - 运行时参数覆盖
  - Expert framework 可选启用

#### 示例应用
- ✅ 完整的 `debate_agent_app` 应用
  - 标准化目录结构
  - 4 个 Agent YAML 配置
  - 3 个中文 Prompt 模板
  - LLM 和 Memory 配置
  - 应用配置文件 (config.toml)

- ✅ 中文 Prompt 模板
  - `demo_proposer_agent/cn.yaml` - 提案指令
  - `demo_critic_agent/cn.yaml` - 批评标准
  - `demo_judge_agent/cn.yaml` - 评审与评分标准

#### 测试与演示
- ✅ 单元测试套件 (`test_debate_agent.py`)
  - 基础辩论测试
  - 多轮辩论测试
  - 架构设计场景测试

- ✅ 快速开始脚本 (`simple_example.py`)
  - 最小化示例代码
  - 清晰的步骤说明
  - 输出展示

#### 文档
- ✅ 完整的 README.md
  - 概述和核心特性
  - 快速开始指南
  - 详细使用示例
  - 应用场景说明
  - 配置参数文档
  - 最佳实践与故障排除

- ✅ CHANGELOG.md (本文件)
  - 版本历史记录
  - 详细的变更说明

### Features

#### 多轮辩论机制
- 可配置的辩论轮数 (1-10 轮)
- 每轮依次执行提案、批评、评审
- 自动记录每轮结果
- 支持轮次间的上下文传递

#### 共识收敛
- 基于评审评分的共识判断
- 达到阈值提前结束，避免无效轮次
- 未达成共识时输出最后一轮结果
- 完整的共识状态记录

#### 多角色协作
- **Proposer**: 结合用户目标与历史批评生成方案
- **Critic**: 识别错误、遗漏与可执行性问题
- **Judge**: 综合提案与批评，输出评分与最终答案

#### 评分系统
- 0-100 分的量化评分
- 可配置的共识阈值
- JSON 结构化评审输出
- 分数解析容错处理

#### 上下文管理
- 完整的执行上下文跟踪
- 每轮提案与批评记录
- 用户目标保持
- 历史结果传递

#### Expert Framework 支持
- 可选的专家框架指导
- 针对提案、批评与评审的独立配置
- 领域特定知识集成

#### Memory 集成
- 对话历史管理
- 跨轮次的记忆共享
- 自动化的记忆更新

#### Stream Output 支持
- 实时输出流
- 分阶段结果推送
- 智能体信息标记

### Configuration

#### 默认配置
```yaml
debate_rounds: 2          # 默认 2 轮辩论
consensus_threshold: 60   # 默认 60 分共识阈值
```

#### LLM 配置
```yaml
Proposer Agent:
  temperature: 0.7        # 较高创造性
Critic Agent:
  temperature: 0.7        # 较高创造性，便于发现问题
Judge Agent:
  temperature: 0.3        # 较低温度保证评审一致性
```

### Architecture

Debate 模式采用三角色顺序协作架构:

```
User Input
    ↓
┌─────────────────────────────────┐
│ Round 1..N                      │
│  Proposer → Critic → Judge      │
│  评分 ≥ 阈值 → 提前结束          │
└─────────────────────────────────┘
    ↓
Final Output
```
