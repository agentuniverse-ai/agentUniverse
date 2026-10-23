# xAI (Grok) LLM Use

`XaiLLM` integrates the [xAI](https://x.ai) API into agentUniverse. xAI is the company behind the **Grok** family of large language models: flagship reasoning models (grok-4.x), fast tool-calling and multi-agent variants (grok-4.20-0309) and a dedicated coding model (grok-build-0.1), all trained on xAI's Colossus supercomputer and tightly integrated with X.

xAI exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.x.ai/v1`, so the `XaiLLM` component simply extends `OpenAIStyleLLM` and only wires up the xAI credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_xai_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_xai_llm'
description: 'user xai llm powered by the xAI Grok models'
model_name: 'grok-4.7'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${XAI_API_KEY}'
api_base: 'https://api.x.ai/v1'
proxy: '${XAI_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.xai_llm'
  class: 'XaiLLM'
```

A ready-to-use `xai_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/xai_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'xai-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${XAI_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="xai"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

xAI regularly ships new Grok models. Below are the models currently available on the xAI API together with their context window (input + output tokens). The same values are hard-coded inside `XaiLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                        | Context length    |
| --------------------------------- | ----------------- |
| `grok-4.7`                        | 500000 (500k)     |
| `grok-4.6`                        | 500000 (500k)     |
| `grok-4.5`                        | 500000 (500k)     |
| `grok-4.3`                        | 1000000 (1M)      |
| `grok-4.20-0309-reasoning`        | 1000000 (1M)      |
| `grok-4.20-0309-non-reasoning`    | 1000000 (1M)      |
| `grok-4.20-multi-agent-0309`      | 1000000 (1M)      |
| `grok-build-0.1`                  | 256000 (256k)     |

xAI documents alias conventions for every release: the plain name points to the latest stable version, `<modelname>-latest` to the newest features and `<modelname>-<date>` pins a specific release. `XaiLLM` resolves a trailing `-latest` suffix (e.g. `grok-4.7-latest`) to the base model's context window automatically.

Always confirm the latest list on the [xAI models documentation](https://docs.x.ai/docs/models) page. If a model is not present in the table above, `XaiLLM` falls back to a conservative default of 32768 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `XAI_API_KEY`
Optional: `XAI_API_BASE`, `XAI_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['XAI_API_KEY'] = 'xai-***'
os.environ['XAI_API_BASE'] = 'https://api.x.ai/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
XAI_API_KEY="xai-******"
XAI_API_BASE="https://api.x.ai/v1"
XAI_PROXY=""
```

---

## 4. Obtaining the xAI API key

1. Sign in at [https://console.x.ai](https://console.x.ai).
2. Navigate to **API Keys** and create a new key.
3. Copy the generated `xai-...` key and assign it to `XAI_API_KEY`.

Pricing, rate limits and the free-tier terms are documented at [https://docs.x.ai](https://docs.x.ai).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.xai_llm import XaiLLM

llm = XaiLLM(model_name='grok-4.7')

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

Because xAI is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_xai_llm` (see `xai_llm.yaml.example`). After configuring the `XAI_API_KEY` environment variable you can rename it to `xai_llm.yaml` and reference it directly from your agents.
- Grok reasoning models expose their chain of thought through the API's reasoning fields; for lightweight workflows the `grok-4.20-0309-non-reasoning` variant skips reasoning for lower latency, while `grok-build-0.1` is tuned for coding agents.
- The `grok-4.3` / `grok-4.20-0309` families offer 1M-token context windows, which makes them a good fit for agentUniverse knowledge-base agents that need to stuff long retrieved documents into a single prompt.
