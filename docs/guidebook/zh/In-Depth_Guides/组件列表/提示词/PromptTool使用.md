# PromptTool 使用
`PromptTool` 借助LLM组件生成与优化智能体提示词，产出遵循agentUniverse的提示词规范（`introduction` / `target` / `instruction` 三段式结构与 `{placeholder}` 输入变量）。

## 1. 根据场景生成提示词
```python
from agentuniverse.prompt.prompt_tool import PromptTool

tool = PromptTool(llm_name='default_openai_llm')
result = tool.generate(
    scenario='航空公司客服智能体',
    content='关于行李规则与退票的FAQ页面',   # 可选参考资料
    target='准确而简短地回答旅客问题',       # 可选目标
)
print(result.introduction)
print(result.target)
print(result.instruction)
print(result.input_variables)
```

## 2. 优化已有提示词
```python
result = tool.optimize(
    introduction='你是一名航空公司客服智能体。',
    target='回答旅客问题。',
    instruction='回答{user_question}。',
    feedback='回答容易跑题且遗漏行李规则',   # 可选待修复问题
)
```

## 3. 使用生成结果
```python
# 直接交给智能体
agent_prompt_model = result.as_agent_prompt_model()

# 或保存为提示词组件YAML
yaml_config = result.to_yaml_config(name='airline_service_prompt')
with open('intelligence/agentic/prompt/airline_service/airline_service.cn_v1.yaml', 'w') as f:
    f.write(yaml_config)
```

## 4. 说明
- `PromptTool(llm=...)` 可直接传入现成的LLM实例，优先级高于 `llm_name`；任何实现了 `call(messages, streaming)` 的组件均可。
- `language='中文'` 指定生成提示词的语言；默认跟随场景描述的语言。
- LLM回答按严格JSON解析，同时兼容代码块包裹的JSON与散落在自然语言中的JSON；完全无法解析时返回空的 `GeneratedPrompt` 而不抛错。
- `agenerate` / `aoptimize` 是 `generate` / `optimize` 的异步版本。
