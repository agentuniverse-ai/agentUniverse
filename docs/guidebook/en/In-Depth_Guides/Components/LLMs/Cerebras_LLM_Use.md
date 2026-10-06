# Cerebras LLM Use

`CerebrasLLM` integrates the [Cerebras Inference](https://inference-docs.cerebras.ai) service into agentUniverse. Cerebras runs a curated set of popular open-weight large language models (Meta Llama 3.x / Llama 4, Qwen 3, gpt-oss, ...) on its **Wafer-Scale Engine (WSE)** — the largest chip ever built — which delivers the fastest token generation available on the market, typically hundreds to thousands of tokens per second.

Cerebras exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.cerebras.ai/v1`, so the `CerebrasLLM` component simply extends `OpenAIStyleLLM` and only wires up the Cerebras credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the LangChain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_cerebras_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_cerebras_llm'
description: 'user cerebras llm powered by the Cerebras Wafer-Scale Engine inference service'
model_name: 'llama-3.3-70b'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${CEREBRAS_API_KEY}'
api_base: 'https://api.cerebras.ai/v1'
proxy: '${CEREBRAS_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.cerebras_llm'
  class: 'CerebrasLLM'
```

A ready-to-use `cerebras_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/cerebras_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'csk-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${CEREBRAS_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="cerebras"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Cerebras regularly rotates its model catalogue. Below are the most commonly used models together with their context window (input + output tokens). The same values are hard-coded inside `CerebrasLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                       | Context length |
| -------------------------------- | -------------- |
| `llama-3.3-70b`                  | 131072 (128k)  |
| `llama3.1-8b`                    | 131072 (128k)  |
| `llama4-scout-17b-16e-instruct`  | 131072 (128k)  |
| `qwen-3-32b`                     | 131072 (128k)  |
| `qwen-3-235b-a22b-instruct-2507` | 131072 (128k)  |
| `gpt-oss-120b`                   | 131072 (128k)  |

Always confirm the latest list on the [Cerebras models documentation](https://inference-docs.cerebras.ai/models/overview) page. If a model is not present in the table above, `CerebrasLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `CEREBRAS_API_KEY`
Optional: `CEREBRAS_API_BASE`, `CEREBRAS_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['CEREBRAS_API_KEY'] = 'csk-***'
os.environ['CEREBRAS_API_BASE'] = 'https://api.cerebras.ai/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
CEREBRAS_API_KEY="csk-******"
CEREBRAS_API_BASE="https://api.cerebras.ai/v1"
CEREBRAS_PROXY=""
```

---

## 4. Obtaining the Cerebras API key

1. Sign in at [https://cloud.cerebras.ai](https://cloud.cerebras.ai).
2. Navigate to **API Keys** and create a new key.
3. Copy the generated `csk-...` key and assign it to `CEREBRAS_API_KEY`.

Cerebras offers a free daily tier for development; rate limits and pricing for production usage are documented at [https://inference-docs.cerebras.ai](https://inference-docs.cerebras.ai/support/pricing).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.cerebras_llm import CerebrasLLM

llm = CerebrasLLM(model_name='llama-3.3-70b')

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

Because Cerebras is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_cerebras_llm` (see `cerebras_llm.yaml.example`). After configuring the `CEREBRAS_API_KEY` environment variable you can rename it to `cerebras_llm.yaml` and reference it directly from your agents.
- Cerebras's standout feature is raw speed: even 70B-scale models stream at hundreds of tokens per second, which makes it an excellent choice for interactive agents, agent swarms and rapid prototyping where wall-clock latency dominates.
- Cerebras serves a curated set of open-weight models rather than the full upstream catalogues, so before standardising on a particular model check the [Cerebras models page](https://inference-docs.cerebras.ai/models/overview) for availability and deprecation notices.
