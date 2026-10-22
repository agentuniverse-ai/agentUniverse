# Fireworks LLM Use

`FireworksLLM` integrates the [Fireworks AI](https://fireworks.ai) inference platform into agentUniverse. Fireworks hosts a large catalogue of open-weight and fine-tuned large language models (Meta Llama 3.x, Mistral Mixtral, DeepSeek and many community fine-tunes) on managed GPU infrastructure, with a focus on low-latency, high-throughput token generation. Models are addressed by their full serverless identifier, e.g. `accounts/fireworks/models/llama-v3p1-70b-instruct`.

Fireworks exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.fireworks.ai/inference/v1`, so the `FireworksLLM` component simply extends `OpenAIStyleLLM` and only wires up the Fireworks credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_fireworks_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_fireworks_llm'
description: 'user fireworks llm powered by the Fireworks AI models'
model_name: 'accounts/fireworks/models/llama-v3p1-70b-instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${FIREWORKS_API_KEY}'
api_base: 'https://api.fireworks.ai/inference/v1'
proxy: '${FIREWORKS_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.fireworks_llm'
  class: 'FireworksLLM'
```

A ready-to-use `fireworks_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/fireworks_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'fw_***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${FIREWORKS_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="fireworks"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Fireworks continuously adds new models to its serverless catalogue. Below are popular models currently available on the Fireworks API together with their context window (input + output tokens). The same values are hard-coded inside `FireworksLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                                                  | Context length    |
| ----------------------------------------------------------- | ----------------- |
| `accounts/fireworks/models/llama-v3p1-405b-instruct`        | 131072 (128k)     |
| `accounts/fireworks/models/llama-v3p1-70b-instruct`         | 131072 (128k)     |
| `accounts/fireworks/models/llama-v3p1-8b-instruct`          | 131072 (128k)     |
| `accounts/fireworks/models/mixtral-8x7b-instruct`           | 32768 (32k)       |
| `accounts/fireworks/models/deepseek-v3`                     | 131072 (128k)     |

This table is indicative rather than exhaustive. Always confirm the latest list and the exact limits on the [Fireworks models documentation](https://fireworks.ai/models) page.

Fireworks also serves fine-tuned deployments under user accounts (`accounts/<your-account>/models/<base-model>`). `FireworksLLM` automatically resolves such identifiers to the bare base model's context window. If a model cannot be resolved at all, `FireworksLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `FIREWORKS_API_KEY`
Optional: `FIREWORKS_API_BASE`, `FIREWORKS_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['FIREWORKS_API_KEY'] = 'fw_***'
os.environ['FIREWORKS_API_BASE'] = 'https://api.fireworks.ai/inference/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
FIREWORKS_API_KEY="fw_******"
FIREWORKS_API_BASE="https://api.fireworks.ai/inference/v1"
FIREWORKS_PROXY=""
```

---

## 4. Obtaining the Fireworks API key

1. Sign in at [https://fireworks.ai](https://fireworks.ai).
2. Navigate to **Account -> API Keys** ([https://fireworks.ai/account/api-keys](https://fireworks.ai/account/api-keys)) and create a new key.
3. Copy the generated `fw_...` key and assign it to `FIREWORKS_API_KEY`.

Pricing, rate limits and the free-trial terms are documented at [https://docs.fireworks.ai](https://docs.fireworks.ai).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.fireworks_llm import FireworksLLM

llm = FireworksLLM(model_name='accounts/fireworks/models/llama-v3p1-70b-instruct')

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

Because Fireworks is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_fireworks_llm` (see `fireworks_llm.yaml.example`). After configuring the `FIREWORKS_API_KEY` environment variable you can rename it to `fireworks_llm.yaml` and reference it directly from your agents.
- Serverless model identifiers are full paths (`accounts/fireworks/models/...`). If you deploy your own fine-tune, reference it as `accounts/<your-account>/models/<base-model>`; the context window of the known base model is resolved automatically.
- The Llama 3.1 family offers 128k-token context windows, which makes it a good fit for agentUniverse knowledge-base agents that need to stuff long retrieved documents into a single prompt, while `mixtral-8x7b-instruct` is a cost-efficient 32k alternative for high-volume workflows.
