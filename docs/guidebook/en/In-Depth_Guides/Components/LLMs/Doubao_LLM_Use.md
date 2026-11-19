# Doubao LLM Use

`DoubaoLLM` integrates the [Doubao](https://www.volcengine.com/product/doubao) (豆包) models developed by **ByteDance** into agentUniverse. Doubao models are served through **Volcengine Ark** (火山方舟), ByteDance's managed model platform, and span the general-purpose `doubao-pro` models, the newer `doubao-1.5-pro` generation and the cost-optimised `doubao-lite` models.

Ark exposes a fully **OpenAI-compatible** Chat Completions API at `https://ark.cn-beijing.volces.com/api/v3`, so the `DoubaoLLM` component simply extends `OpenAIStyleLLM` and only wires up the Ark credentials, API base URL and an indicative per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_doubao_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_doubao_llm'
description: 'user doubao llm powered by the ByteDance Doubao models on Volcengine Ark'
model_name: 'doubao-pro-32k'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${ARK_API_KEY}'
api_base: 'https://ark.cn-beijing.volces.com/api/v3'
proxy: '${DOUBAO_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.doubao_llm'
  class: 'DoubaoLLM'
```

A ready-to-use `doubao_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/doubao_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'ark-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${ARK_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="doubao"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Volcengine Ark continuously adds new Doubao generations and regional variants. Below are popular models available on the Ark API together with their indicative context window (input + output tokens). The same values are hard-coded inside `DoubaoLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name            | Context length   |
| --------------------- | ---------------- |
| `doubao-pro-32k`      | 32768 (32k)      |
| `doubao-pro-128k`     | 131072 (128k)    |
| `doubao-1.5-pro-256k` | 262144 (256k)    |
| `doubao-lite-32k`     | 32768 (32k)      |

Ark model IDs often carry a trailing version-date suffix (e.g. `doubao-pro-32k-250527` for the 2025-05-27 snapshot); such suffixes are stripped automatically and resolve to their family's context window.

The table is **indicative rather than exhaustive**: regional variants, freshly announced models and Ark inference endpoints (the `ep-...` endpoint IDs shown in the Ark console) can have very different windows, so any model that is not listed falls back to a conservative default of 8192 tokens. To state the exact limit for such a model, set the `max_context_length` field explicitly in the YAML configuration — an explicitly configured value always wins over the built-in table.

Always confirm the current model catalogue and windows on the [Volcengine Ark console](https://console.volcengine.com/ark) / [API reference](https://www.volcengine.com/docs/82379/1330310).

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `ARK_API_KEY` (or its alias `DOUBAO_API_KEY`)
Optional: `DOUBAO_API_BASE`, `DOUBAO_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['ARK_API_KEY'] = 'ark-***'
os.environ['DOUBAO_API_BASE'] = 'https://ark.cn-beijing.volces.com/api/v3'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
ARK_API_KEY="ark-******"
DOUBAO_API_BASE="https://ark.cn-beijing.volces.com/api/v3"
DOUBAO_PROXY=""
```

> `ARK_API_KEY` is the canonical variable used across the Volcengine ecosystem — the bundled `DoubaoEmbedding` component reads it as well — so it is consulted first. `DOUBAO_API_KEY` is honoured as an explicit Doubao-LLM-only alias when `ARK_API_KEY` is not set.

---

## 4. Obtaining the Ark API key

1. Sign in at [https://console.volcengine.com/ark](https://console.volcengine.com/ark).
2. Navigate to **API Key Management** (API Key 管理) and create a new API key.
3. Copy the generated key and assign it to `ARK_API_KEY`.

Pricing, rate limits and the available model catalogue are documented in the [Volcengine Ark documentation](https://www.volcengine.com/docs/82379).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.doubao_llm import DoubaoLLM

llm = DoubaoLLM(model_name='doubao-pro-32k')

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

Because the Ark API is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_doubao_llm` (see `doubao_llm.yaml.example`). After configuring the `ARK_API_KEY` environment variable you can rename it to `doubao_llm.yaml` and reference it directly from your agents.
- Use `doubao-1.5-pro-256k` (256k window) for long-document workloads, `doubao-pro-32k` for balanced everyday agents, and `doubao-lite-32k` for high-volume, latency-sensitive tasks.
- If you reference an Ark inference endpoint (`ep-...`) as `model_name`, remember to set `max_context_length` explicitly in the YAML — endpoint IDs cannot be resolved through the built-in table and fall back to a conservative 8192.
