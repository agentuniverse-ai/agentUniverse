# Yi LLM Use

`YiLLM` integrates the [01.AI (零一万物)](https://www.01.ai) **Yi** family of foundation large language models into agentUniverse. The Yi series — Yi-Large, Yi-Medium, Yi-Small, Yi-Vision and friends — is developed by 01.AI, the AI company founded by Kai-Fu Lee.

01.AI exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.01.ai/v1`, so the `YiLLM` component simply extends `OpenAIStyleLLM` and only wires up the 01.AI credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the LangChain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_yi_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_yi_llm'
description: 'user yi llm powered by 01.AI Yi series models'
model_name: 'yi-large'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${YI_API_KEY}'
api_base: 'https://api.01.ai/v1'
organization: '${YI_ORGANIZATION}'
proxy: '${YI_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.yi_llm'
  class: 'YiLLM'
```

**Note:** Model parameters such as `api_key`, `api_base`, `organization` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'your-yi-key'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${YI_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="yi"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

01.AI offers several Yi models. Below are the most commonly used models together with their context window (input + output tokens). The same values are hard-coded inside `YiLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name            | Context length |
| --------------------- | -------------- |
| `yi-large`            | 32768 (32k)    |
| `yi-large-turbo`      | 32768 (32k)    |
| `yi-large-rag`        | 32768 (32k)    |
| `yi-medium`           | 16384 (16k)    |
| `yi-medium-200k`      | 204800 (200k)  |
| `yi-small`            | 16384 (16k)    |
| `yi-spark`            | 16384 (16k)    |
| `yi-vision`           | 16384 (16k)    |
| `yi-vision-plus`      | 16384 (16k)    |

Always confirm the latest list on the [01.AI platform documentation](https://platform.lingyiwanhu.com). If a model is not present in the table above, `YiLLM` falls back to a conservative default of 16384 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `YI_API_KEY`
Optional: `YI_API_BASE`, `YI_PROXY`, `YI_ORGANIZATION`

### 3.1 Configure through Python code

```python
import os
os.environ['YI_API_KEY'] = 'your-yi-key'
os.environ['YI_API_BASE'] = 'https://api.01.ai/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
YI_API_KEY="your-yi-key"
YI_API_BASE="https://api.01.ai/v1"
YI_ORGANIZATION=""
YI_PROXY=""
```

---

## 4. Obtaining the 01.AI API key

1. Sign in at [https://platform.lingyiwanhu.com](https://platform.lingyiwanhu.com).
2. Navigate to **API Key** management and create a new key.
3. Copy the generated key and assign it to `YI_API_KEY`.

Pricing, rate limits and free-tier quotas are documented on the 01.AI platform.

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.yi_llm import YiLLM

llm = YiLLM(model_name='yi-large')

# Non-streaming
output = llm.call(messages=[{"role": "user", "content": "Hello!"}])
print(output.text)

# Streaming
for chunk in llm.call(messages=[{"role": "user", "content": "Count 1 to 5."}], streaming=True):
    print(chunk.text, end='')

# Async
import asyncio
async def main():
    out = await llm.acall(messages=[{"role": "user", "content": "Hello!"}])
    print(out.text)
asyncio.run(main())
```

Because 01.AI is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use instance template named `default_yi_llm` (see `yi_llm.yaml.example`). After configuring the `YI_API_KEY` environment variable you can reference it directly from your agents.
- `yi-large` is the flagship model and is recommended for complex reasoning; `yi-medium`/`yi-small` are faster and cheaper for simpler tasks.
- For multimodal (image + text) inputs use `yi-vision` or `yi-vision-plus`.
