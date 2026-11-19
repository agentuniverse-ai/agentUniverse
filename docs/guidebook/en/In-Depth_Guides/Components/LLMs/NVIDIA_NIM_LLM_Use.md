# NVIDIA NIM LLM Use

`NvidiaNimLLM` integrates the [NVIDIA NIM](https://build.nvidia.com) API into agentUniverse. NVIDIA NIM (NVIDIA Inference Microservices) is NVIDIA's hosted model catalogue on NVIDIA AI Foundation, serving flagship open and community models such as `meta/llama-3.1-405b-instruct`, `nvidia/nemotron-4-340b-instruct` and `deepseek-ai/deepseek-r1` with accelerated inference.

NIM exposes a fully **OpenAI-compatible** Chat Completions API at `https://integrate.api.nvidia.com/v1`, so the `NvidiaNimLLM` component simply extends `OpenAIStyleLLM` and only wires up the NIM credentials, API base URL and an indicative per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_nvidia_nim_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_nvidia_nim_llm'
description: 'user nvidia nim llm powered by the NVIDIA NIM models'
model_name: 'meta/llama-3.1-405b-instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${NVIDIA_API_KEY}'
api_base: 'https://integrate.api.nvidia.com/v1'
proxy: '${NVIDIA_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.nvidia_nim_llm'
  class: 'NvidiaNimLLM'
```

A ready-to-use `nvidia_nim_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/nvidia_nim_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'nvapi-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${NVIDIA_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="nvidia_nim"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

NVIDIA continuously adds new NIM endpoints. Below are popular models available on the NIM API together with their indicative context window (input + output tokens). The same values are hard-coded inside `NvidiaNimLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                        | Context length   |
| --------------------------------- | ---------------- |
| `meta/llama-3.1-405b-instruct`    | 131072 (128k)    |
| `meta/llama-3.1-70b-instruct`     | 131072 (128k)    |
| `nvidia/nemotron-4-340b-instruct` | 4096 (4k)        |
| `deepseek-ai/deepseek-r1`         | 131072 (128k)    |

The table is **indicative rather than exhaustive**: freshly announced NIM models can have very different windows (note how Nemotron-4 340B is limited to 4k), so any model that is not listed falls back to a conservative default of 8192 tokens. To state the exact limit for such a model, set the `max_context_length` field explicitly in the YAML configuration — an explicitly configured value always wins over the built-in table.

Always confirm the current model catalogue and windows on the [build.nvidia.com](https://build.nvidia.com) model pages.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `NVIDIA_API_KEY` (the `NVAPI_KEY` alias used by NVIDIA tooling is honoured as a fallback)
Optional: `NVIDIA_API_BASE`, `NVIDIA_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['NVIDIA_API_KEY'] = 'nvapi-***'
os.environ['NVIDIA_API_BASE'] = 'https://integrate.api.nvidia.com/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
NVIDIA_API_KEY="nvapi-******"
NVIDIA_API_BASE="https://integrate.api.nvidia.com/v1"
NVIDIA_PROXY=""
```

---

## 4. Obtaining the NVIDIA NIM API key

1. Sign in at [https://build.nvidia.com](https://build.nvidia.com).
2. Pick any model and click **Get API Key** (or navigate to your profile) to generate a personal key.
3. Copy the generated key (it usually starts with `nvapi-`) and assign it to `NVIDIA_API_KEY`.

New accounts receive free credits for trying the API; pricing, rate limits and the available model catalogue are documented on the [NVIDIA NIM pages](https://docs.nvidia.com/nim/).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.nvidia_nim_llm import NvidiaNimLLM

llm = NvidiaNimLLM(model_name='meta/llama-3.1-405b-instruct')

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

Because the NIM API is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_nvidia_nim_llm` (see `nvidia_nim_llm.yaml.example`). After configuring the `NVIDIA_API_KEY` environment variable you can rename it to `nvidia_nim_llm.yaml` and reference it directly from your agents.
- Use `meta/llama-3.1-405b-instruct` or `deepseek-ai/deepseek-r1` for heavy reasoning workloads (both with 128k context windows) and `meta/llama-3.1-70b-instruct` for lower-latency agents.
- Keep in mind that `nvidia/nemotron-4-340b-instruct` only exposes a 4k context window despite its size; for NIM models that are not yet in the built-in context table, set `max_context_length` explicitly in the YAML so prompt budgeting stays accurate.
