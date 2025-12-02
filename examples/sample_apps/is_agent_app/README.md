# IS Agent Application

IS (Implementation-Supervision) 模式演示应用

## 概述

IS (Implementation-Supervision) 是一种双智能体协作模式,通过持续监督确保任务执行符合用户目标。该模式特别适合需要质量控制和进度监督的复杂任务执行场景。

### 核心特性

- **双智能体协作**: 实施智能体负责执行,监督智能体负责监控
- **检查点机制**: 在关键节点进行监督评估
- **反馈修正**: 基于监督反馈的自动修正机制
- **上下文跟踪**: 完整的执行历史和上下文管理
- **可配置参数**: 灵活的检查点数量和修正次数配置

## 工作流程

```
用户输入
  ↓
循环执行(按检查点):
  1. 实施智能体执行任务
  2. 监督智能体评估质量
  3. 如需修正且未超限 → 修正执行
  4. 记录执行历史
  ↓
返回最终结果
```

### 三阶段循环

每个检查点包含三个阶段:

1. **Implementation (实施)**: 执行当前检查点的任务
2. **Supervision (监督)**: 评估执行质量,决定是否需要修正
3. **Correction (修正)**: 如果需要,根据反馈进行修正

## 快速开始

### 1. 安装依赖

```bash
pip install agentuniverse
```

### 2. 配置环境

设置您的LLM API密钥(以通义千问为例):

```bash
export DASHSCOPE_API_KEY="your_api_key_here"
```

### 3. 运行示例

```bash
cd examples/sample_apps/is_agent_app
python simple_example.py
```

### 4. 运行测试

```bash
cd examples/sample_apps/is_agent_app/intelligence/test
python test_is_agent.py
```

## 使用示例

### 基础用法

```python
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

# 初始化
AgentUniverse().start(config_path='config/config.toml')

# 获取IS智能体
agent: Agent = AgentManager().get_instance_obj('demo_is_agent')

# 执行任务
result = agent.run(
    input='编写一个Python函数,实现二分查找算法',
    checkpoint_count=3,      # 3个检查点
    max_corrections=2        # 最多修正2次
)

# 获取结果
output = result.get('output', '')
print(output)
```

### 查看完整执行详情

```python
# 获取包含所有检查点详情的完整输出
full_output = result.get('full_output', '')
print(full_output)

# 获取执行上下文
execution_context = result.get('execution_context', {})
print(f"总检查点数: {len(result.get('checkpoint_results', []))}")
print(f"修正次数: {execution_context.get('corrections_made', 0)}")
```

### 自定义配置

```python
# 调整检查点和修正参数
result = agent.run(
    input='实现一个复杂的数据结构',
    checkpoint_count=5,      # 增加检查点数量
    max_corrections=3        # 允许更多修正
)
```

## 应用场景

### 1. 代码开发

```python
result = agent.run(
    input='实现一个RESTful API端点,包括参数验证、错误处理和文档',
    checkpoint_count=4,
    max_corrections=2
)
```

**适用于**:
- 需要质量保证的代码实现
- 复杂的算法开发
- API设计和实现

### 2. 文档编写

```python
result = agent.run(
    input='编写产品使用手册,包括安装、配置和常见问题',
    checkpoint_count=3,
    max_corrections=2
)
```

**适用于**:
- 技术文档编写
- 用户手册创建
- API文档生成

### 3. 数据处理

```python
result = agent.run(
    input='设计并实现一个数据清洗流程,处理CSV文件中的缺失值和异常值',
    checkpoint_count=4,
    max_corrections=2
)
```

**适用于**:
- 数据清洗脚本
- ETL流程设计
- 数据验证逻辑

## 项目结构

```
is_agent_app/
├── README.md                          # 本文件
├── simple_example.py                  # 快速开始示例
├── config/
│   └── config.toml                    # 应用配置
└── intelligence/
    ├── agentic/
    │   ├── agent/
    │   │   └── agent_instance/
    │   │       └── is_agent_case/
    │   │           ├── demo_is_agent.yaml              # IS协调器配置
    │   │           ├── demo_implementation_agent.yaml   # 实施智能体配置
    │   │           └── demo_supervision_agent.yaml      # 监督智能体配置
    │   ├── llm/
    │   │   └── qwen_llm.yaml          # LLM配置
    │   ├── memory/
    │   │   └── demo_memory.yaml       # 记忆配置
    │   └── prompt/
    │       └── is_agent_case/
    │           ├── demo_implementation_agent/
    │           │   └── cn.yaml        # 实施智能体中文提示词
    │           └── demo_supervision_agent/
    │               └── cn.yaml        # 监督智能体中文提示词
    └── test/
        └── test_is_agent.py           # 单元测试
```

## 配置说明

### IS智能体配置

```yaml
info:
  name: 'demo_is_agent'
  description: 'Demo IS agent for supervised task execution'

profile:
  # 子智能体配置
  implementation: 'demo_implementation_agent'
  supervision: 'demo_supervision_agent'

  # 检查点配置
  checkpoint_count: 3        # 默认检查点数量
  max_corrections: 2         # 最大修正次数

  # 专家框架(可选)
  expert_framework_enabled: false
```

### 实施智能体配置

```yaml
info:
  name: 'demo_implementation_agent'
  description: 'Demo implementation agent'

profile:
  prompt_version: 'demo_implementation_agent.cn'
  llm_model:
    name: 'qwen_llm'
    temperature: 0.7        # 较高的创造性
```

### 监督智能体配置

```yaml
info:
  name: 'demo_supervision_agent'
  description: 'Demo supervision agent'

profile:
  prompt_version: 'demo_supervision_agent.cn'
  llm_model:
    name: 'qwen_llm'
    temperature: 0.3        # 较低的温度保证评估一致性
```

## 核心参数

### checkpoint_count (检查点数量)

- **默认值**: 3
- **范围**: 1-10
- **说明**: 将任务分成多少个检查点执行
- **建议**:
  - 简单任务: 2-3个检查点
  - 中等复杂度: 3-5个检查点
  - 复杂任务: 5-7个检查点

### max_corrections (最大修正次数)

- **默认值**: 2
- **范围**: 0-5
- **说明**: 每个检查点最多允许修正多少次
- **建议**:
  - 质量要求高: 2-3次
  - 平衡模式: 1-2次
  - 快速模式: 0-1次

## 监督评估标准

监督智能体使用以下维度评估执行质量:

1. **目标符合度** (40%): 是否符合用户目标
2. **质量完整性** (30%): 结果的完整性和准确性
3. **进度合理性** (20%): 当前进度是否合理
4. **可持续性** (10%): 是否有利于后续工作

### 评分标准

- **90-100分**: 优秀,完全符合要求
- **75-89分**: 良好,基本符合要求
- **60-74分**: 及格,存在问题但可接受
- **0-59分**: 不及格,需要修正

### 修正触发条件

- 评分 < 75分,或
- 存在明显的质量问题

## 最佳实践

### 1. 任务分解

将大任务分解成合适的检查点:

```python
# 不推荐: 检查点过少
result = agent.run(
    input='开发完整的Web应用',
    checkpoint_count=2  # 太少
)

# 推荐: 合理分解
result = agent.run(
    input='开发完整的Web应用',
    checkpoint_count=5  # 合理: 设计、后端、前端、测试、部署
)
```

### 2. 明确任务要求

提供清晰的任务描述:

```python
# 不推荐: 模糊的要求
result = agent.run(input='写个排序函数')

# 推荐: 明确的要求
result = agent.run(
    input='编写Python快速排序函数,包括文档字符串、类型注解、输入验证和使用示例'
)
```

### 3. 合理配置修正次数

根据任务复杂度调整:

```python
# 简单任务
result = agent.run(input='...', max_corrections=1)

# 复杂任务
result = agent.run(input='...', max_corrections=3)

# 质量要求极高的任务
result = agent.run(input='...', max_corrections=5)
```

## 与其他模式对比

### IS vs GRR

| 维度 | IS | GRR |
|-----|-----|-----|
| 智能体数 | 2 (实施+监督) | 3 (生成+评审+重写) |
| 适用场景 | 任务执行监督 | 内容生成优化 |
| 工作方式 | 检查点监督 | 迭代优化 |
| 修正机制 | 基于监督反馈 | 基于评审建议 |

### IS vs PEER

| 维度 | IS | PEER |
|-----|-----|-----|
| 智能体数 | 2 | 4 |
| 适用场景 | 任务执行 | 问题分析 |
| 执行方式 | 顺序执行 | 部分并行 |
| 输出类型 | 任务结果 | 分析报告 |

## 故障排除

### 问题1: 修正次数用尽但质量仍不达标

**解决方案**:
1. 增加max_corrections参数
2. 优化实施智能体的提示词
3. 调整监督标准(降低阈值)
4. 使用更强大的LLM模型

### 问题2: 所有检查点都需要修正

**解决方案**:
1. 简化任务复杂度
2. 减少检查点数量
3. 优化提示词,提供更多示例
4. 检查LLM配置是否合适

### 问题3: 监督评估不准确

**解决方案**:
1. 降低监督智能体的temperature参数
2. 优化监督提示词中的评分标准
3. 在提示词中添加更多评估示例
4. 使用更强大的LLM模型

## 性能优化

### 1. 使用异步执行

```python
import asyncio

async def run_async():
    result = await agent.async_run(
        input='...',
        checkpoint_count=3
    )
    return result

result = asyncio.run(run_async())
```

### 2. 调整LLM参数

```yaml
llm_model:
  name: 'qwen_llm'
  max_tokens: 2048      # 根据需要调整
  temperature: 0.7      # 平衡创造性和一致性
```

### 3. 优化检查点数量

找到任务复杂度和执行效率的平衡点:
- 检查点太少: 监督不充分
- 检查点太多: 执行效率低

## 扩展开发

### 自定义实施智能体

创建专门的实施智能体:

```yaml
info:
  name: 'custom_implementation_agent'

profile:
  prompt_version: 'custom_implementation.cn'
  # ... 其他配置
```

### 自定义监督标准

修改监督智能体的评估标准:

```yaml
# 在prompt中定义自定义评估维度
instruction: |
  评估维度:
  - 代码质量 (50%)
  - 性能效率 (30%)
  - 可维护性 (20%)
```

## 许可证

本示例应用遵循 agentUniverse 项目的开源许可证。

## 贡献

欢迎提交Issue和Pull Request来改进本示例应用!

## 支持

- GitHub Issues: https://github.com/agentuniverse-ai/agentUniverse/issues
- 文档: https://github.com/agentuniverse-ai/agentUniverse
