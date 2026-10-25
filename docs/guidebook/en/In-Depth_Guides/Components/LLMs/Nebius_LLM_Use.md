# Nebius AI Studio LLM Use

`NebiusLLM` integrates the [Nebius AI Studio](https://nebius.com/ai-studio) API into agentUniverse. AI Studio is the inference platform of Nebius Group and serves a broad catalogue of **open-weight** models from many vendors under a single pay-as-you-go API: Meta Llama (`meta-llama/Meta-Llama-3.1-70B-Instruct`), DeepSeek (`deepseek-ai/DeepSeek-V3`), Qwen (`Qwen/Qwen2.5-32B-Instruct`) and Mistral (`mistralai/Mistral-Nemo-Instruct-2407`) among others.

AI Studio exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.studio.nebius.com/v1`, so the `NebiusLLM` component simply extends `OpenAIStyleLLM` and only wires up the Nebius credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_nebius_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_nebius_llm'
description: 'user nebius llm powered by the Nebius AI Studio open models'
model_name: 'meta-llama/Meta-Llama-3.1-70B-Instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${NEBIUS_API_KEY}'
api_base: 'https://api.studio.nebius.com/v1'
proxy: '${NEBIUS_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.nebius_llm'
  class: 'NebiusLLM'
```

A ready-to-use `nebius_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/nebius_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'nebius-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${NEBIUS_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="nebius"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Nebius AI Studio identifies models by their full `organization/model` name, e.g. `meta-llama/Meta-Llama-3.1-70B-Instruct`. Below is an indicative selection of the models commonly available on AI Studio together with their context window (input + output tokens). The same values are hard-coded inside `NebiusLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                                       | Context length    |
| ------------------------------------------------ | ----------------- |
| `meta-llama/Meta-Llama-3.1-405B-Instruct`        | 131072 (128k)     |
| `meta-llama/Meta-Llama-3.1-70B-Instruct`         | 131072 (128k)     |
| `meta-llama/Meta-Llama-3.1-8B-Instruct`          | 131072 (128k)     |
| `meta-llama/Llama-3.3-70B-Instruct`              | 131072 (128k)     |
| `meta-llama/Llama-3.2-3B-Instruct`               | 131072 (128k)     |
| `deepseek-ai/DeepSeek-V3`                        | 131072 (128k)     |
| `deepseek-ai/DeepSeek-V3-0324`                   | 131072 (128k)     |
| `deepseek-ai/DeepSeek-R1`                        | 131072 (128k)     |
| `Qwen/Qwen2.5-32B-Instruct`                      | 131072 (128k)     |
| `Qwen/Qwen2.5-Coder-32B-Instruct`                | 131072 (128k)     |
| `Qwen/QwQ-32B`                                   | 131072 (128k)     |
| `mistralai/Mistral-Nemo-Instruct-2407`           | 131072 (128k)     |
| `mistralai/Mixtral-8x22B-Instruct-v0.1`          | 65536 (64k)       |
| `microsoft/Phi-3.5-MoE-Instruct`                 | 131072 (128k)     |
| `google/gemma-2-27b-it`                          | 8192 (8k)         |

Always confirm the current catalogue on the [Nebius AI Studio documentation](https://docs.nebius.com/studio). Nebius continuously adds and rotates models, so the table above is indicative. If a model is not present in the table, `NebiusLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `NEBIUS_API_KEY`
Optional: `NEBIUS_API_BASE`, `NEBIUS_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['NEBIUS_API_KEY'] = 'nebius-***'
os.environ['NEBIUS_API_BASE'] = 'https://api.studio.nebius.com/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
NEBIUS_API_KEY="nebius-******"
NEBIUS_API_BASE="https://api.studio.nebius.com/v1"
NEBIUS_PROXY=""
```

---

## 4. Obtaining the Nebius AI Studio API key

1. Sign in at [https://studio.nebius.ai](https://studio.nebius.ai) (or through the Nebius console).
2. Navigate to **API Keys** and create a new key.
3. Copy the generated key and assign it to `NEBIUS_API_KEY`.

Pricing, rate limits and the free-tier terms are documented at [https://docs.nebius.com](https://docs.nebius.com).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.nebius_llm import NebiusLLM

llm = NebiusLLM(model_name='meta-llama/Meta-Llama-3.1-70B-Instruct')

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

Because Nebius AI Studio is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_nebius_llm` (see `nebius_llm.yaml.example`). After configuring the `NEBIUS_API_KEY` environment variable you can rename it to `nebius_llm.yaml` and reference it directly from your agents.
- AI Studio serves many open models under one endpoint, so switching between Llama, DeepSeek and Qwen is only a `model_name` change - no separate account or SDK per vendor is needed.
- The Llama 3.1/3.3, DeepSeek-V3 and Qwen2.5 families offer 128k-token context windows, which makes them a good fit for agentUniverse knowledge-base agents that need to stuff long retrieved documents into a single prompt.
