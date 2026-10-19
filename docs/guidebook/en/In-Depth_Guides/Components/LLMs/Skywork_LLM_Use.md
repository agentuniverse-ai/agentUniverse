# Skywork LLM Use

`SkyworkLLM` integrates the [Skywork](https://www.skywork.ai) API into agentUniverse. Skywork (天工) is the large language model family of Kunlun Tech (昆仑万维), covering deep reasoning models (`skywork-reasoner`, `skywork-t1`) and a general-purpose chat/text model with a long context window (`skywork-text`).

Skywork exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.skywork.ai/v1`, so the `SkyworkLLM` component simply extends `OpenAIStyleLLM` and only wires up the Skywork credentials, API base URL and an indicative per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_skywork_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_skywork_llm'
description: 'user skywork llm powered by the Skywork models'
model_name: 'skywork-text'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${SKYWORK_API_KEY}'
api_base: 'https://api.skywork.ai/v1'
proxy: '${SKYWORK_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.skywork_llm'
  class: 'SkyworkLLM'
```

A ready-to-use `skywork_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/skywork_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'skywork-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${SKYWORK_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="skywork"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Below are the models currently served on the Skywork API together with their indicative context window (input + output tokens). The same values are hard-coded inside `SkyworkLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name         | Context length   |
| ------------------ | ---------------- |
| `skywork-reasoner` | 32768 (32k)      |
| `skywork-text`     | 131072 (128k)    |
| `skywork-t1`       | 65536 (64k)      |

The table is **indicative rather than exhaustive**: freshly announced or aliased Skywork models can have very different windows, so any model that is not listed falls back to a conservative default of 8192 tokens. To state the exact limit for such a model, set the `max_context_length` field explicitly in the YAML configuration — an explicitly configured value always wins over the built-in table.

Always confirm the current model catalogue and windows on the Skywork platform / [API reference](https://platform.skywork.ai).

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `SKYWORK_API_KEY`
Optional: `SKYWORK_API_BASE`, `SKYWORK_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['SKYWORK_API_KEY'] = 'skywork-***'
os.environ['SKYWORK_API_BASE'] = 'https://api.skywork.ai/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
SKYWORK_API_KEY="skywork-******"
SKYWORK_API_BASE="https://api.skywork.ai/v1"
SKYWORK_PROXY=""
```

---

## 4. Obtaining the Skywork API key

1. Sign in to the Skywork platform at [https://platform.skywork.ai](https://platform.skywork.ai).
2. Open the **API Key** management page and create a new key.
3. Copy the generated key and assign it to `SKYWORK_API_KEY`.

Pricing, rate limits and the available model catalogue are documented in the [Skywork API reference](https://platform.skywork.ai).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.skywork_llm import SkyworkLLM

llm = SkyworkLLM(model_name='skywork-text')

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

Because Skywork is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_skywork_llm` (see `skywork_llm.yaml.example`). After configuring the `SKYWORK_API_KEY` environment variable you can rename it to `skywork_llm.yaml` and reference it directly from your agents.
- Use `skywork-reasoner` for heavy reasoning workloads, `skywork-t1` for fast turbo reasoning, and `skywork-text` for general chat and long-context tasks (128k window).
- For models that are not yet in the built-in context table, set `max_context_length` explicitly in the YAML so prompt budgeting stays accurate.
