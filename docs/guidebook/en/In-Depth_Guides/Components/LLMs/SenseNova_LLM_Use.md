# SenseNova LLM Use

`SenseNovaLLM` integrates the [SenseNova](https://platform.sensenova.cn) API from **SenseTime** into agentUniverse. SenseNova is the large model platform behind the **SenseChat** family: the flagship **SenseChat-5** dialogue model, the low-latency **SenseChat-Turbo** variant and the **SenseNova-V6-Pro** generation.

SenseNova exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.sensenova.cn/compatible-mode/v1`, so the `SenseNovaLLM` component simply extends `OpenAIStyleLLM` and only wires up the SenseNova credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_sensenova_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_sensenova_llm'
description: 'user sensenova llm powered by the SenseTime SenseNova SenseChat models'
model_name: 'SenseChat-5'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${SENSENOVA_API_KEY}'
api_base: 'https://api.sensenova.cn/compatible-mode/v1'
proxy: '${SENSENOVA_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.sensenova_llm'
  class: 'SenseNovaLLM'
```

A ready-to-use `sensenova_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/sensenova_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'sensenova-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${SENSENOVA_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="sensenova"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

SenseTime regularly ships new SenseChat models. Below are the models commonly used through the SenseNova OpenAI-compatible endpoint together with their context window (input + output tokens). The same values are hard-coded inside `SenseNovaLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name          | Context length    |
| ------------------- | ----------------- |
| `SenseChat-5`       | 131072 (128k)     |
| `SenseChat-Turbo`  | 32768 (32k)       |
| `SenseNova-V6-Pro` | 131072 (128k)     |

The values above are indicative — always confirm the latest list and exact limits in the [SenseNova documentation](https://platform.sensenova.cn). If a model is not present in the table above, `SenseNovaLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `SENSENOVA_API_KEY`
Optional: `SENSENOVA_API_BASE`, `SENSENOVA_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['SENSENOVA_API_KEY'] = 'sensenova-***'
os.environ['SENSENOVA_API_BASE'] = 'https://api.sensenova.cn/compatible-mode/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
SENSENOVA_API_KEY="sensenova-******"
SENSENOVA_API_BASE="https://api.sensenova.cn/compatible-mode/v1"
SENSENOVA_PROXY=""
```

---

## 4. Obtaining the SenseNova API key

1. Sign in at the [SenseCore console](https://console.sensecore.cn).
2. Open the **Model as a Service / SenseNova** section and create an API access key in the key management page.
3. Copy the generated key and assign it to `SENSENOVA_API_KEY`.

Pricing, rate limits and the model catalogue are documented on the [SenseNova platform](https://platform.sensenova.cn).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.sensenova_llm import SenseNovaLLM

llm = SenseNovaLLM(model_name='SenseChat-5')

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

Because SenseNova is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_sensenova_llm` (see `sensenova_llm.yaml.example`). After configuring the `SENSENOVA_API_KEY` environment variable you can rename it to `sensenova_llm.yaml` and reference it directly from your agents.
- `SenseChat-Turbo` trades context window for latency and is a good pick for high-frequency agent steps, while `SenseChat-5` and `SenseNova-V6-Pro` offer 128k windows suited for knowledge-base agents that need to stuff long retrieved documents into a single prompt.
- If your account routes through a different regional endpoint, override it with `SENSENOVA_API_BASE` instead of editing the component.
