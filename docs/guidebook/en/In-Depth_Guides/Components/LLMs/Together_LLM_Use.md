# Together LLM Use

`TogetherLLM` integrates the [Together AI](https://www.together.ai) hosted inference platform into agentUniverse. Together AI serves **200+ open-source large language models** - including Meta Llama, Mistral/Mixtral, Qwen, DeepSeek, DBRX, Falcon and many others - behind a single, fully **OpenAI-compatible** Chat Completions API exposed at `https://api.together.xyz/v1`.

Because the API is OpenAI-compatible, the `TogetherLLM` component simply extends `OpenAIStyleLLM` and only wires up the Together credentials, API base URL and a per-model context-length table. Streaming, tool/function calling, the async interface and the LangChain bridge all work out of the box without any extra code.

---

## 1. Create the configuration file

Create a YAML file, for example `user_together_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_together_llm'
description: 'user together llm hosted on the Together AI platform'
model_name: 'meta-llama/Llama-3.3-70B-Instruct-Turbo'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${TOGETHER_API_KEY}'
api_base: 'https://api.together.xyz/v1'
organization: '${TOGETHER_ORGANIZATION}'
proxy: '${TOGETHER_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.together_llm'
  class: 'TogetherLLM'
```

**Note:** Model parameters such as `api_key`, `api_base`, `organization` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'a1b2c3***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${TOGETHER_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="together"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Together AI hosts an ever-growing catalogue of models. Below are some of the most commonly used ones together with their context window (input + output tokens). The same values are hard-coded inside `TogetherLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                                            | Context length |
| ----------------------------------------------------- | -------------- |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo`             | 131072 (128k)  |
| `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`         | 131072 (128k)  |
| `meta-llama/Meta-Llama-3-70B-Instruct-Lite`           | 8192           |
| `mistralai/Mixtral-8x7B-Instruct-v0.1`                | 32768          |
| `mistralai/Mistral-7B-Instruct-v0.2`                  | 32768          |
| `mistralai/Mistral-Large-Instruct-2411`               | 131072         |
| `Qwen/Qwen2.5-72B-Instruct-Turbo`                     | 131072         |
| `Qwen/Qwen1.5-72B-Chat`                               | 32768          |
| `deepseek-ai/DeepSeek-V3`                             | 131072         |
| `deepseek-ai/DeepSeek-R1`                             | 131072         |
| `databricks/dbrx-instruct`                            | 32768          |

Always confirm the latest list on the [Together AI models documentation](https://docs.together.ai/docs/inference-models) page. If a model is not present in the table above, `TogetherLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `TOGETHER_API_KEY`
Optional: `TOGETHER_API_BASE`, `TOGETHER_PROXY`, `TOGETHER_ORGANIZATION`

### 3.1 Configure through Python code

```python
import os
os.environ['TOGETHER_API_KEY'] = 'a1b2c3***'
os.environ['TOGETHER_API_BASE'] = 'https://api.together.xyz/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
TOGETHER_API_KEY="a1b2c3******"
TOGETHER_API_BASE="https://api.together.xyz/v1"
TOGETHER_ORGANIZATION=""
TOGETHER_PROXY=""
```

---

## 4. Obtaining the Together AI API key

1. Sign in at [https://api.together.ai](https://api.together.ai).
2. Navigate to **Settings** -> **API Keys** and click **Create API Key**.
3. Copy the generated key (e.g. `a1b2c3...`) and assign it to `TOGETHER_API_KEY`.

New accounts receive free credits to get started; pricing for each model is listed at [https://www.together.ai/pricing](https://www.together.ai/pricing).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.together_llm import TogetherLLM

llm = TogetherLLM(model_name='meta-llama/Llama-3.3-70B-Instruct-Turbo')

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

Because Together AI is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use instance named `default_together_llm`. After configuring the `TOGETHER_API_KEY` environment variable you can reference it directly from your agents.
- Together AI's key advantage is breadth: a single API key unlocks hundreds of open-source models, which makes it easy to A/B test different model families without changing integrations.
- Model availability and naming evolve over time. Before standardising on a particular model, check the [Together AI models page](https://docs.together.ai/docs/inference-models) for the authoritative list and any deprecation notices.
