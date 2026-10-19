# Hunyuan LLM Use

`HunyuanLLM` integrates the [Tencent Hunyuan](https://hunyuan.tencent.com) API into agentUniverse. Hunyuan is Tencent's family of large language models: deep-thinking reasoning models (the T1 series), fast-thinking flagship models (the TurboS series), the Hy3 generation Mixture-of-Experts models (295B total / 21B active parameters) and long-running workhorses such as hunyuan-lite / hunyuan-standard / hunyuan-large.

Hunyuan exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.hunyuan.cloud.tencent.com/v1`, so the `HunyuanLLM` component simply extends `OpenAIStyleLLM` and only wires up the Hunyuan credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_hunyuan_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_hunyuan_llm'
description: 'user hunyuan llm powered by the Tencent Hunyuan models'
model_name: 'hunyuan-turbos-latest'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${HUNYUAN_API_KEY}'
api_base: 'https://api.hunyuan.cloud.tencent.com/v1'
proxy: '${HUNYUAN_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.hunyuan_llm'
  class: 'HunyuanLLM'
```

A ready-to-use `hunyuan_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/hunyuan_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'hunyuan-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${HUNYUAN_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="hunyuan"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Tencent regularly ships new Hunyuan models. Below are the models commonly available on the Hunyuan OpenAI-compatible API together with their context window (input + output tokens). The same values are hard-coded inside `HunyuanLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                      | Context length    |
| ------------------------------- | ----------------- |
| `hunyuan-t1`                    | 32768 (32k)       |
| `hunyuan-t1-latest`             | 32768 (32k)       |
| `hunyuan-turbos`                | 32768 (32k)       |
| `hunyuan-turbos-latest`         | 262144 (256k)     |
| `hunyuan-turbos-20250630`       | 262144 (256k)     |
| `hy3`                           | 262144 (256k)     |
| `hunyuan-a13b`                  | 262144 (256k)     |
| `hunyuan-lite`                  | 262144 (256k)     |
| `hunyuan-standard`              | 32768 (32k)       |
| `hunyuan-standard-256K`         | 262144 (256k)     |
| `hunyuan-large`                 | 32768 (32k)       |
| `hunyuan-large-longcontext`     | 262144 (256k)     |

`HunyuanLLM` resolves model names case-insensitively (so the documented `hunyuan-standard-256K` capitalisation resolves too) and maps a trailing `-latest` suffix that is not itself a table entry to the base model's context window automatically.

Always confirm the latest list in the [Tencent Cloud Hunyuan documentation](https://cloud.tencent.com/document/product/1729). If a model is not present in the table above, `HunyuanLLM` falls back to a conservative default of 32768 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `HUNYUAN_API_KEY`
Optional: `HUNYUAN_API_BASE`, `HUNYUAN_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['HUNYUAN_API_KEY'] = 'hunyuan-***'
os.environ['HUNYUAN_API_BASE'] = 'https://api.hunyuan.cloud.tencent.com/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
HUNYUAN_API_KEY="hunyuan-******"
HUNYUAN_API_BASE="https://api.hunyuan.cloud.tencent.com/v1"
HUNYUAN_PROXY=""
```

International users can point `HUNYUAN_API_BASE` at the global TokenHub gateway, e.g. `https://tokenhub-intl.tencentcloudmaas.com/v1`.

---

## 4. Obtaining the Hunyuan API key

1. Sign in to the Tencent Cloud console at [https://console.cloud.tencent.com/hunyuan](https://console.cloud.tencent.com/hunyuan).
2. Open the **API Key Management** page (hunyuan / TokenHub) and create a new key.
3. Copy the generated key and assign it to `HUNYUAN_API_KEY`.

Pricing, rate limits and free-tier terms are documented in the [Tencent Cloud Hunyuan docs](https://cloud.tencent.com/document/product/1729).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.hunyuan_llm import HunyuanLLM

llm = HunyuanLLM(model_name='hunyuan-turbos-latest')

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

Because Hunyuan is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_hunyuan_llm` (see `hunyuan_llm.yaml.example`). After configuring the `HUNYUAN_API_KEY` environment variable you can rename it to `hunyuan_llm.yaml` and reference it directly from your agents.
- `hunyuan-turbos-latest` is the fast-thinking flagship and a good default for agent workloads; use `hunyuan-t1-latest` when you need deep reasoning, and `hy3` / `hunyuan-a13b` for the newest MoE generation.
- The `-latest` / `-256K` families offer 256K-token context windows, which makes them a good fit for agentUniverse knowledge-base agents that need to stuff long retrieved documents into a single prompt.
