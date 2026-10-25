# Lepton AI LLM Use

`LeptonLLM` integrates the [Lepton AI](https://lepton.ai) API into agentUniverse. Lepton AI (now part of NVIDIA DGX Cloud Lepton) is a managed AI platform that serves both open-source models it deploys itself (e.g. `llama3.1-8b`, `llama3.1-70b`, `mistral-7b`) and third-party marketplace models (e.g. `gpt-4o-mini`) behind a single API surface, billing and workspace token.

Lepton exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.lepton.run/api/v1`, so the `LeptonLLM` component simply extends `OpenAIStyleLLM` and only wires up the Lepton credentials, API base URL and an indicative per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_lepton_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_lepton_llm'
description: 'user lepton llm powered by the Lepton AI models'
model_name: 'llama3.1-8b'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${LEPTON_API_KEY}'
api_base: 'https://api.lepton.run/api/v1'
proxy: '${LEPTON_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.lepton_llm'
  class: 'LeptonLLM'
```

A ready-to-use `lepton_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/lepton_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'lepton-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${LEPTON_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="lepton"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Lepton continuously adds new deployments and marketplace models. Below are popular models available on the Lepton API together with their indicative context window (input + output tokens). The same values are hard-coded inside `LeptonLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name      | Context length   |
| --------------- | ---------------- |
| `llama3.1-8b`   | 131072 (128k)    |
| `llama3.1-70b`  | 131072 (128k)    |
| `mistral-7b`    | 32768 (32k)      |
| `gpt-4o-mini`   | 131072 (128k)    |

The table is **indicative rather than exhaustive**: marketplace and freshly announced models can have very different windows, so any model that is not listed falls back to a conservative default of 8192 tokens. To state the exact limit for such a model, set the `max_context_length` field explicitly in the YAML configuration — an explicitly configured value always wins over the built-in table.

Always confirm the current model catalogue and windows on the Lepton dashboard / [API reference](https://docs.nvidia.com/dgx-cloud/lepton/reference/api).

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `LEPTON_API_KEY`
Optional: `LEPTON_API_BASE`, `LEPTON_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['LEPTON_API_KEY'] = 'lepton-***'
os.environ['LEPTON_API_BASE'] = 'https://api.lepton.run/api/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
LEPTON_API_KEY="lepton-******"
LEPTON_API_BASE="https://api.lepton.run/api/v1"
LEPTON_PROXY=""
```

---

## 4. Obtaining the Lepton API key

1. Sign in at [https://dashboard.lepton.ai](https://dashboard.lepton.ai).
2. Navigate to **Settings -> API Tokens** (or **Secret Keys**) and create a new workspace token.
3. Copy the generated key and assign it to `LEPTON_API_KEY`.

Pricing, rate limits and the available model catalogue are documented in the [Lepton API reference](https://docs.nvidia.com/dgx-cloud/lepton/reference/api).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.lepton_llm import LeptonLLM

llm = LeptonLLM(model_name='llama3.1-8b')

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

Because Lepton is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_lepton_llm` (see `lepton_llm.yaml.example`). After configuring the `LEPTON_API_KEY` environment variable you can rename it to `lepton_llm.yaml` and reference it directly from your agents.
- Use `llama3.1-70b` for heavier reasoning workloads and `llama3.1-8b` / `mistral-7b` for low-latency, high-throughput agents; both Llama 3.1 deployments offer 128k context windows.
- For marketplace models (e.g. `gpt-4o-mini`) that are not yet in the built-in context table, set `max_context_length` explicitly in the YAML so prompt budgeting stays accurate.
