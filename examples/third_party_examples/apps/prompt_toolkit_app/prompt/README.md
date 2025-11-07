# Prompt Toolkit - 智能Prompt生成与优化工具

## 概述

Prompt Toolkit是一个强大的智能prompt生成与优化工具，能够根据用户提供的场景和内容自动生成高质量的prompt模板，并提供智能优化功能。

## 核心功能

### 1. 智能Prompt生成 (`PromptGenerator`)
- **场景识别**: 自动识别用户场景类型（对话、任务导向、推理、创意等）
- **上下文分析**: 智能分析用户需求，提取关键信息
- **模板生成**: 基于场景和上下文生成结构化的prompt模板
- **复杂度控制**: 支持简单、中等、复杂三个复杂度级别

### 2. 高级Prompt优化 (`PromptOptimizer`)
- **质量评估**: 多维度评估prompt质量（清晰度、特异性、完整性等）
- **智能优化**: 基于规则和策略自动优化prompt
- **改进建议**: 提供具体的改进建议和优化方向
- **置信度评分**: 评估优化效果和可靠性

### 3. 场景分析器 (`ScenarioAnalyzer`)
- **场景分析**: 深度分析用户提供的场景描述
- **上下文提取**: 自动提取领域、用户角色、目标受众等信息
- **推荐系统**: 推荐最适合的prompt场景和复杂度
- **置信度评估**: 评估分析结果的可靠性

### 4. 统一工具包 (`PromptToolkit`)
- **一站式服务**: 集成所有功能，提供统一的API接口
- **批量处理**: 支持批量生成和优化多个prompt
- **质量对比**: 对比不同prompt的质量和效果
- **导出功能**: 支持YAML和JSON格式导出

## 架构设计

```
PromptToolkit
├── PromptGenerator (生成器)
│   ├── 场景模板管理
│   ├── 上下文处理
│   └── 复杂度控制
├── PromptOptimizer (优化器)
│   ├── 质量评估
│   ├── 规则引擎
│   └── 策略管理
├── ScenarioAnalyzer (分析器)
│   ├── 场景识别
│   ├── 上下文提取
│   └── 推荐系统
└── 统一接口
    ├── 批量处理
    ├── 质量对比
    └── 导出功能
```

## 使用示例

### 基本使用

```python
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_toolkit import PromptToolkit, PromptGenerationRequest

# 初始化工具包
toolkit = PromptToolkit()

# 创建生成请求
request = PromptGenerationRequest(
    scenario_description="我需要一个编程助手来帮助我写Python代码",
    target_audience="初学者",
    domain="技术",
    constraints=["必须使用中文", "提供代码示例"],
    tone="友好"
)

# 生成prompt
result = toolkit.generate_prompt_from_request(request)
print(f"生成的prompt: {result.generated_prompt}")
```

### 优化现有Prompt

```python
from agentuniverse.prompt.prompt_model import AgentPromptModel
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_optimizer import OptimizationStrategy

# 创建要优化的prompt
prompt = AgentPromptModel(
    introduction="你是一个助手",
    target="帮助用户",
    instruction="回答问题"
)

# 优化prompt
result = toolkit.optimize_existing_prompt(
    prompt,
    strategies=[OptimizationStrategy.CLARITY, OptimizationStrategy.STRUCTURE]
)
print(f"优化结果: {result.optimized_prompt}")
```

### 场景分析

```python
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.scenario_analyzer import ScenarioAnalyzer

analyzer = ScenarioAnalyzer()
result = analyzer.analyze_scenario("我需要一个数据分析助手")
print(f"推荐场景: {result.recommended_scenario}")
```

## 支持的场景类型

| 场景类型 | 描述 | 适用场景 |
|---------|------|----------|
| CONVERSATIONAL | 对话型 | 日常对话、客服咨询 |
| TASK_ORIENTED | 任务导向型 | 具体任务执行、工作流程 |
| REASONING | 推理型 | 逻辑分析、问题解决 |
| CREATIVE | 创意型 | 设计、创作、创新 |
| ANALYTICAL | 分析型 | 数据分析、研究报告 |
| TECHNICAL | 技术型 | 编程、技术咨询 |
| CUSTOMER_SERVICE | 客服型 | 客户服务、售后支持 |
| EDUCATIONAL | 教育型 | 教学、培训、学习 |
| RESEARCH | 研究型 | 学术研究、调查分析 |
| CODE_GENERATION | 代码生成型 | 编程、代码开发 |

## 优化策略

| 策略 | 描述 | 效果 |
|------|------|------|
| CLARITY | 清晰度优化 | 提高语言表达的清晰度和准确性 |
| STRUCTURE | 结构优化 | 改善prompt的逻辑结构和组织 |
| SPECIFICITY | 特异性优化 | 增强prompt的具体性和针对性 |
| EFFICIENCY | 效率优化 | 提高prompt的执行效率 |
| COMPREHENSIVENESS | 全面性优化 | 增强prompt的完整性和全面性 |

## 质量评估指标

| 指标 | 描述 | 评估标准 |
|------|------|----------|
| 清晰度 (Clarity) | 语言表达的清晰程度 | 明确性、准确性、易理解性 |
| 特异性 (Specificity) | 内容的具体程度 | 详细性、针对性、精确性 |
| 完整性 (Completeness) | 内容的完整程度 | 全面性、完整性、覆盖性 |
| 结构 (Structure) | 逻辑结构的合理性 | 组织性、逻辑性、层次性 |
| 语调 (Tone) | 语言风格和语调 | 专业性、友好性、一致性 |

## 配置选项

### PromptToolkitConfig

```python
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_toolkit import PromptToolkitConfig
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_generator import PromptScenario, PromptComplexity
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_optimizer import OptimizationStrategy

config = PromptToolkitConfig(
    enable_auto_optimization=True,  # 启用自动优化
    default_scenario=PromptScenario.CONVERSATIONAL,  # 默认场景
    default_complexity=PromptComplexity.MEDIUM,  # 默认复杂度
    optimization_strategies=[  # 优化策略
        OptimizationStrategy.CLARITY,
        OptimizationStrategy.STRUCTURE
    ],
    confidence_threshold=0.6  # 置信度阈值
)
```

## 最佳实践

### 1. 场景描述
- 提供详细、具体的场景描述
- 明确指定目标受众和使用场景
- 包含相关的约束条件和要求

### 2. 复杂度选择
- **简单**: 基础功能、入门级应用
- **中等**: 标准功能、常规应用
- **复杂**: 高级功能、专业应用

### 3. 优化策略
- 根据实际需求选择合适的优化策略
- 结合多种策略获得最佳效果
- 定期评估和调整优化策略

### 4. 质量监控
- 定期分析prompt质量
- 关注置信度评分
- 根据反馈持续改进

## 扩展功能

### 自定义优化规则

```python
from agentuniverse.prompt.prompt_optimizer import OptimizationRule

custom_rule = OptimizationRule(
    name="custom_rule",
    pattern=r"助手",
    replacement="专业助手",
    description="自定义优化规则",
    priority=8
)

result = toolkit.optimize_existing_prompt(
    prompt,
    custom_rules=[custom_rule]
)
```

### 批量处理

```python
requests = [
    PromptGenerationRequest(scenario_description="场景1"),
    PromptGenerationRequest(scenario_description="场景2"),
    PromptGenerationRequest(scenario_description="场景3")
]

results = toolkit.batch_generate_prompts(requests)
```

### 导出功能

```python
# 导出为YAML格式
yaml_config = toolkit.export_prompt_config(prompt, "yaml")

# 导出为JSON格式
json_config = toolkit.export_prompt_config(prompt, "json")
```

## 性能优化

- 使用批量处理提高效率
- 合理设置置信度阈值
- 选择合适的优化策略
- 定期清理和优化规则

## 注意事项

1. 生成的prompt需要根据实际使用情况进行调整
2. 建议在使用前进行测试和验证
3. 可以根据具体需求自定义优化规则
4. 批量处理时注意资源使用情况
5. 定期评估和更新优化策略

## 未来规划

- 支持多语言prompt生成
- 集成机器学习模型
- 支持模板化prompt生成
- 支持prompt版本管理
- 支持A/B测试和效果评估
- 支持实时优化和自适应调整
