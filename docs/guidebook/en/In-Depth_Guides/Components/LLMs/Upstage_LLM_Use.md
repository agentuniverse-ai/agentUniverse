# Upstage (Solar) LLM Use

`UpstageLLM` integrates the [Upstage](https://upstage.ai) Solar API into agentUniverse. Upstage is a Korean AI company based in Seoul and the team behind the **Solar** family of large language models: the flagship frontier model (solar-pro-2), the cost-efficient general-purpose variants (solar-pro, solar-mini) and a dedicated document understanding model (solar-docvision), all optimised for Korean and multilingual workloads.

Upstage exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.upstage.ai/v1/solar`, so the `UpstageLLM` component simply extends `OpenAIStyleLLM` and only wires up the Upstage credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_upstage_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_upstage_llm'
description: 'user upstage llm powered by the Upstage Solar models'
model_name: 'solar-pro-2'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${UPSTAGE_API_KEY}'
api_base: 'https://api.upstage.ai/v1/solar'
proxy: '${UPSTAGE_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.upstage_llm'
  class: 'UpstageLLM'
```

A ready-to-use `upstage_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/upstage_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'up-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${UPSTAGE_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="upstage"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Upstage regularly ships new Solar models. Below are the Solar models commonly available on the Solar API together with their context window (input + output tokens). The same values are hard-coded inside `UpstageLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call. The numbers are indicative; always confirm the current list and limits on the [Upstage documentation](https://developers.upstage.ai) page.

| Model name          | Context length    |
| ------------------- | ----------------- |
| `solar-pro-2`       | 65536 (64k)       |
| `solar-pro`         | 65536 (64k)       |
| `solar-mini`        | 65536 (64k)       |
| `solar-docvision`   | 65536 (64k)       |

If a model is not present in the table above, `UpstageLLM` falls back to a conservative default of 8192 tokens.

Model selection tips:

- `solar-pro-2` is the flagship reasoning model and the best default choice for demanding agent workloads.
- `solar-pro` / `solar-mini` trade some capability for lower latency and cost, which makes them a good fit for high-volume routing or classification steps inside a workflow.
- `solar-docvision` is tuned for document understanding (OCR / layout-aware extraction) and pairs well with agentUniverse knowledge-base agents that ingest scanned or structured documents.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `UPSTAGE_API_KEY`
Optional: `UPSTAGE_API_BASE`, `UPSTAGE_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['UPSTAGE_API_KEY'] = 'up-***'
os.environ['UPSTAGE_API_BASE'] = 'https://api.upstage.ai/v1/solar'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
UPSTAGE_API_KEY="up-******"
UPSTAGE_API_BASE="https://api.upstage.ai/v1/solar"
UPSTAGE_PROXY=""
```

---

## 4. Obtaining the Upstage API key

1. Sign in at [https://console.upstage.ai](https://console.upstage.ai).
2. Navigate to **API Keys** and create a new key.
3. Copy the generated `up_...` key and assign it to `UPSTAGE_API_KEY`.

Pricing, rate limits and the free-tier terms are documented at [https://developers.upstage.ai](https://developers.upstage.ai).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.upstage_llm import UpstageLLM

llm = UpstageLLM(model_name='solar-pro-2')

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

Because the Solar API is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_upstage_llm` (see `upstage_llm.yaml.example`). After configuring the `UPSTAGE_API_KEY` environment variable you can rename it to `upstage_llm.yaml` and reference it directly from your agents.
- Solar models are particularly strong in Korean; if your agents serve Korean users, Upstage is a natural primary LLM with the other OpenAI-compatible providers as fallbacks.
- The context-length table in `UpstageLLM` is indicative and may lag behind newly released Solar models. For long-context workflows, verify the limit in the Upstage documentation or set `max_context_length` explicitly in your YAML configuration, which always takes precedence over the built-in table.
