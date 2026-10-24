# SiliconFlow LLM Use

`SiliconFlowLLM` integrates the [SiliconFlow](https://siliconflow.cn) API into agentUniverse. SiliconFlow is a Chinese **model-aggregation cloud platform** that hosts third-party open-source large language models — DeepSeek (`deepseek-ai/DeepSeek-V3`, `deepseek-ai/DeepSeek-R1`), Alibaba's Qwen family (`Qwen/Qwen2.5-72B-Instruct`, ...) and Zhipu's GLM open-weight releases (`THUDM/glm-4-9b-chat`), among many others — behind one unified billing and one unified API.

SiliconFlow exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.siliconflow.cn/v1`, so the `SiliconFlowLLM` component simply extends `OpenAIStyleLLM` and only wires up the SiliconFlow credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_siliconflow_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_siliconflow_llm'
description: 'user siliconflow llm powered by the models hosted on the SiliconFlow platform'
model_name: 'deepseek-ai/DeepSeek-V3'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${SILICONFLOW_API_KEY}'
api_base: 'https://api.siliconflow.cn/v1'
proxy: '${SILICONFLOW_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.siliconflow_llm'
  class: 'SiliconFlowLLM'
```

A ready-to-use `siliconflow_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/siliconflow_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'sk-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${SILICONFLOW_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="siliconflow"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

SiliconFlow rotates its hosted catalogue frequently. Below are common models currently available on the SiliconFlow platform together with their context window (input + output tokens). The same values are hard-coded inside `SiliconFlowLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                        | Context length    |
| --------------------------------- | ----------------- |
| `deepseek-ai/DeepSeek-V3`         | 65536 (64k)       |
| `deepseek-ai/DeepSeek-R1`         | 65536 (64k)       |
| `Qwen/Qwen2.5-72B-Instruct`       | 32768 (32k)       |
| `Qwen/Qwen2.5-7B-Instruct`        | 32768 (32k)       |
| `THUDM/glm-4-9b-chat`             | 131072 (128k)     |

The table is **indicative**: the values are conservative snapshots of the vendors' documentation / the SiliconFlow model cards, and the effective window of a given model can change with the serving deployment. Always confirm the latest list on the [SiliconFlow model plaza](https://siliconflow.cn/models). If a model is not present in the table above, `SiliconFlowLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `SILICONFLOW_API_KEY`
Optional: `SILICONFLOW_API_BASE`, `SILICONFLOW_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['SILICONFLOW_API_KEY'] = 'sk-***'
os.environ['SILICONFLOW_API_BASE'] = 'https://api.siliconflow.cn/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
SILICONFLOW_API_KEY="sk-******"
SILICONFLOW_API_BASE="https://api.siliconflow.cn/v1"
SILICONFLOW_PROXY=""
```

---

## 4. Obtaining the SiliconFlow API key

1. Sign in at [https://cloud.siliconflow.cn](https://cloud.siliconflow.cn).
2. Navigate to **API Keys** (左侧菜单「API 密钥」) and create a new key.
3. Copy the generated `sk-...` key and assign it to `SILICONFLOW_API_KEY`.

Pricing, rate limits and the free-tier models are documented at [https://docs.siliconflow.cn](https://docs.siliconflow.cn).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.siliconflow_llm import SiliconFlowLLM

llm = SiliconFlowLLM(model_name='deepseek-ai/DeepSeek-V3')

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

Because SiliconFlow is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_siliconflow_llm` (see `siliconflow_llm.yaml.example`). After configuring the `SILICONFLOW_API_KEY` environment variable you can rename it to `siliconflow_llm.yaml` and reference it directly from your agents.
- SiliconFlow model ids are **namespaced by the upstream vendor** (`deepseek-ai/...`, `Qwen/...`, `THUDM/...`); make sure you pass the full id including the namespace as `model_name`.
- Many popular models are also offered as `:free` or quantized variants (e.g. `Qwen/Qwen2.5-7B-Instruct:free`) which are not listed in the context table; those safely fall back to the conservative 8192 default, or you can set `max_context_length` explicitly in the YAML.
- `deepseek-ai/DeepSeek-R1` is a reasoning model: its answers may include a chain-of-thought segment before the final response, which is returned as part of the message content.
- Using one SiliconFlow API key gives your agents access to the whole aggregated catalogue, which makes it easy to benchmark DeepSeek / Qwen / GLM against each other by only switching `model_name`.
