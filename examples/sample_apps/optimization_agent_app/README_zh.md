# agentUniverse - 优化智能体示例应用

## 项目介绍

本项目是agentUniverse框架的优化智能体示例应用，展示了如何使用优化工作模式来自动改进智能体性能。通过迭代优化过程，只需要给出非常简单的起始prompt和评价标准,系统就能自动迭代出更完整复杂、更高质量的适用于特定任务的智能体提示词。

## 核心功能

### 1. 智能提示词优化
- **自动迭代改进**：系统通过多轮迭代自动优化提示词
- **评分反馈机制**：内置评分智能体对每次生成的结果进行质量评估
- **策略学习**：从优化过程中学习有效的提示词构建策略

### 2. 灵活的优化配置
- **批量处理**：支持批量样本处理，提高优化效率
- **自定义评分标准**：用户可定义专门的评分标准和通过阈值
- **迭代控制**：可配置最大迭代次数、批次大小等参数

## 快速开始

### 运行示例

#### 方式1：运行基金推荐优化示例
```python
python intelligence/test/optimization_agent.py
```

该示例将：
- 使用基金产品数据作为优化样本
- 自动优化推荐文案的生成提示词
- 基于金融合规性、说服力等维度进行评分
- 目标平均分达到95分以上

#### 方式2：运行知识问答优化示例
修改 `optimization_agent.py` 文件，使用 `input_data2`：
```python
result = instance.run(**input_data2)
```

该示例将：
- 优化解释类问题的回答质量
- 确保回答准确且通俗易懂
- 目标平均分达到90分以上

## 核心组件

### 1. 优化智能体 (demo_optimization_agent)
- **类型**：OptimizationAgent
- **功能**：协调整个优化过程

### 2. 执行智能体 (demo_answer_agent)
- **类型**：AnswerAgent
- **功能**：根据当前提示词生成回答

### 3. 评分智能体 (demo_scoring_agent)
- **类型**：ScoringAgent
- **功能**：对生成的回答进行质量评分
- **标准**：基于用户定义的评分标准进行评估

### 4. 反馈智能体 (demo_feedback_agent)
- **类型**：FeedbackAgent
- **功能**：分析评分结果，生成优化建议
- **作用**：指导下一次迭代的提示词改进

## 使用指南

### 自定义优化任务
1. **给出初始prompt**
   可以在入参中指定initial_prompt或者指定已存在的agent名称作为agent_name_for_optimization.

2. **准备样本数据**
   ```python
   samples = [
       "您的任务样本1",
       "您的任务样本2", 
       # ... 更多样本
   ]
   ```
   如果待优化的prompt存在多个入参，以字典列表形式定义，每个字典为一个测试样本
   ```python
   samples = [
       {"input_key1": "入参1", "input_key2": "入参2"},
       {"input_key1": "入参1", "input_key2": "入参2"},
       # ... 更多样本
   ]
   ```

3. **定义评分标准**
   ```python
   scoring_standard = "您的评分标准描述"
   ```

#### 调整优化策略
通过修改智能体配置文件，可以调整：
- 迭代次数和批次大小
- 评分标准和阈值
- 反馈和优化逻辑

## 最佳实践

### 1. 样本选择
- 选择具有代表性的任务样本
- 确保样本覆盖主要的使用场景


### 2. 评分标准设计
- 标准要具体、可量化
- 避免过于主观的标准

## 相关文档

- [agentUniverse快速开始指南](https://github.com/agentuniverse-ai/agentUniverse/blob/master/docs/guidebook/zh/Get_Start/Quick_Start.md)
- [agentUniverse完整指南](https://github.com/agentuniverse-ai/agentUniverse/blob/master/docs/guidebook/zh/Contents.md)

