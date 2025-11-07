# Prompt Toolkit Demo App

这是一个展示智能prompt生成与优化工具功能的示例应用。

## 功能特性

### 1. 智能Prompt生成
- 基于用户场景自动生成高质量的prompt模板
- 支持多种场景类型：对话、任务导向、推理、创意、分析等
- 自动分析用户需求并推荐最适合的prompt类型
- 支持自定义复杂度级别和特殊要求

### 2. Prompt优化
- 智能分析和优化现有prompt
- 提供质量评估和改进建议
- 支持多种优化策略：清晰度、结构、特异性、效率等
- 自动检测和修复常见问题

### 3. 场景分析
- 智能分析用户提供的场景描述
- 自动提取上下文信息：领域、用户角色、目标受众等
- 推荐最适合的prompt场景和复杂度
- 提供详细的置信度评分和建议

### 4. 批量处理
- 支持批量生成多个prompt
- 并行处理提高效率
- 错误处理和恢复机制

### 5. 质量分析
- 多维度质量评估：清晰度、特异性、完整性、结构、语调
- 详细的反馈和改进建议
- 置信度评分

### 6. 导出功能
- 支持YAML和JSON格式导出
- 兼容AgentUniverse的prompt配置格式
- 便于集成到现有系统

## 使用方法

### 基本使用

```python
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_toolkit import PromptToolkit,
    PromptGenerationRequest

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

print(f"生成的prompt:")
print(f"介绍: {result.generated_prompt.introduction}")
print(f"目标: {result.generated_prompt.target}")
print(f"指令: {result.generated_prompt.instruction}")
```

### 优化现有Prompt

```python
from agentuniverse.prompt.prompt_model import AgentPromptModel
from agentuniverse.prompt.prompt_optimizer import OptimizationStrategy

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
print(f"改进建议: {result.suggestions}")
```

### 场景分析

```python
from agentuniverse.prompt.scenario_analyzer import ScenarioAnalyzer

# 初始化分析器
analyzer = ScenarioAnalyzer()

# 分析场景
result = analyzer.analyze_scenario("我需要一个数据分析助手")

print(f"推荐场景: {result.recommended_scenario}")
print(f"复杂度: {result.complexity_level}")
print(f"置信度: {result.confidence_score}")
```

## 配置选项

### PromptToolkitConfig

```python
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_toolkit import PromptToolkitConfig
from agentuniverse.prompt.prompt_generator import PromptScenario, PromptComplexity
from agentuniverse.prompt.prompt_optimizer import OptimizationStrategy

config = PromptToolkitConfig(
    enable_auto_optimization=True,
    default_scenario=PromptScenario.CONVERSATIONAL,
    default_complexity=PromptComplexity.MEDIUM,
    optimization_strategies=[
        OptimizationStrategy.CLARITY,
        OptimizationStrategy.STRUCTURE
    ],
    confidence_threshold=0.6
)

toolkit = PromptToolkit(config)
```

## 支持的场景类型

- **CONVERSATIONAL**: 对话型助手
- **TASK_ORIENTED**: 任务导向型助手
- **REASONING**: 推理型助手
- **CREATIVE**: 创意型助手
- **ANALYTICAL**: 分析型助手
- **TECHNICAL**: 技术型助手
- **CUSTOMER_SERVICE**: 客服型助手
- **EDUCATIONAL**: 教育型助手
- **RESEARCH**: 研究型助手
- **CODE_GENERATION**: 代码生成型助手

## 优化策略

- **CLARITY**: 提高清晰度
- **STRUCTURE**: 改善结构
- **SPECIFICITY**: 增强特异性
- **EFFICIENCY**: 提高效率
- **COMPREHENSIVENESS**: 增强全面性

## 运行示例

```bash
# 运行演示脚本
python demo_prompt_toolkit.py
```

## 集成到AgentUniverse

1. 将prompt工具包集成到你的AgentUniverse应用中
2. 配置相应的组件路径
3. 使用生成的prompt配置创建agent

```yaml
# config.toml
[CORE_PACKAGE]
prompt = ['your_app.intelligence.agentic.prompt']
```

## 最佳实践

1. **明确场景描述**: 提供详细、具体的场景描述以获得更好的结果
2. **设置合适的复杂度**: 根据实际需求选择合适的复杂度级别
3. **使用约束条件**: 明确指定约束条件以确保生成的prompt符合要求
4. **提供示例**: 提供输入输出示例有助于生成更准确的prompt
5. **定期优化**: 使用优化功能持续改进prompt质量

## 注意事项

- 生成的prompt需要根据实际使用情况进行调整
- 建议在使用前进行测试和验证
- 可以根据具体需求自定义优化规则
- 批量处理时注意资源使用情况

## 扩展功能

- 支持自定义优化规则
- 支持多语言prompt生成
- 支持模板化prompt生成
- 支持prompt版本管理
- 支持A/B测试和效果评估
