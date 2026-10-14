# PromptTool Usage
`PromptTool` generates and optimizes agent prompts with the help of an LLM component, following the agentUniverse prompt conventions (`introduction` / `target` / `instruction` sections with `{placeholder}` input variables).

## 1. Generate a prompt from a scenario
```python
from agentuniverse.prompt.prompt_tool import PromptTool

tool = PromptTool(llm_name='default_openai_llm')
result = tool.generate(
    scenario='customer service agent for an airline',
    content='FAQ pages about baggage rules and refunds',  # optional reference material
    target='answer traveler questions accurately and briefly',  # optional goal
)
print(result.introduction)
print(result.target)
print(result.instruction)
print(result.input_variables)
```

## 2. Optimize an existing prompt
```python
result = tool.optimize(
    introduction='You are an airline customer service agent.',
    target='Answer traveler questions.',
    instruction='Answer the {user_question}.',
    feedback='answers drift off topic and miss baggage rules',  # optional problems to fix
)
```

## 3. Use the result
```python
# feed an agent directly
agent_prompt_model = result.as_agent_prompt_model()

# or save it as a prompt component YAML
yaml_config = result.to_yaml_config(name='airline_service_prompt')
with open('intelligence/agentic/prompt/airline_service/airline_service.cn_v1.yaml', 'w') as f:
    f.write(yaml_config)
```

## 4. Notes
- `PromptTool(llm=...)` accepts a ready-made LLM instance, which takes precedence over `llm_name`; any component implementing `call(messages, streaming)` works.
- `language='中文'` asks the tool to write the prompt in a specific language; by default it follows the scenario language.
- The LLM answer is parsed as strict JSON; fenced JSON blocks and JSON embedded in prose are also accepted. When nothing parses, an empty `GeneratedPrompt` is returned rather than an error.
- `agenerate` / `aoptimize` are the asynchronous counterparts of `generate` / `optimize`.
