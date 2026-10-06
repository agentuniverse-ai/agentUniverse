# Reka LLM Use

`RekaLLM` integrates the [Reka AI](https://www.reka.ai) model family into agentUniverse. Reka AI is a multimodal large language model company; its model lineup natively understands **text, images and video**, which makes it a good fit for agents that reason over mixed-media inputs:

- **Reka Core** - the flagship model with frontier-level multimodal quality.
- **Reka Flash** - a fast, balanced model tuned for high-throughput production use.
- **Reka Edge** - a compact model designed for latency- and cost-sensitive scenarios.

Reka exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.reka.ai/v1`, so the `RekaLLM` component simply extends `OpenAIStyleLLM` and only wires up the Reka credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the LangChain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_reka_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_reka_llm'
description: 'user reka llm powered by the Reka AI multimodal model family'
model_name: 'reka-flash'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${REKA_API_KEY}'
api_base: 'https://api.reka.ai/v1'
proxy: '${REKA_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.reka_llm'
  class: 'RekaLLM'
```

A ready-to-use `reka_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/reka_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'reka-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${REKA_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="reka"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Below are the Reka models together with their context window (input + output tokens). The same values are hard-coded inside `RekaLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name   | Context length |
| ------------ | -------------- |
| `reka-core`  | 65536 (64k)    |
| `reka-flash` | 131072 (128k)  |
| `reka-edge`  | 131072 (128k)  |

Always confirm the latest list on the [Reka documentation](https://docs.reka.ai) page. If a model is not present in the table above, `RekaLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `REKA_API_KEY`
Optional: `REKA_API_BASE`, `REKA_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['REKA_API_KEY'] = 'reka-***'
os.environ['REKA_API_BASE'] = 'https://api.reka.ai/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
REKA_API_KEY="reka-******"
REKA_API_BASE="https://api.reka.ai/v1"
REKA_PROXY=""
```

---

## 4. Obtaining the Reka API key

1. Sign in at [https://platform.reka.ai](https://platform.reka.ai).
2. Navigate to **API Keys** and create a new key.
3. Copy the generated key and assign it to `REKA_API_KEY`.

Rate limits and pricing are documented on the [Reka platform](https://platform.reka.ai).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.reka_llm import RekaLLM

llm = RekaLLM(model_name='reka-flash')

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

Because Reka is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_reka_llm` (see `reka_llm.yaml.example`). After configuring the `REKA_API_KEY` environment variable you can rename it to `reka_llm.yaml` and reference it directly from your agents.
- Reka models are natively multimodal; when richer media payloads are supported by the endpoint they can be passed through the OpenAI-style message content blocks without changing this component.
- `reka-flash` is the recommended default for agent workloads: it combines strong reasoning quality with high throughput and a 128k context window, while `reka-core` targets the most demanding multimodal reasoning tasks and `reka-edge` targets latency- and cost-sensitive calls.
