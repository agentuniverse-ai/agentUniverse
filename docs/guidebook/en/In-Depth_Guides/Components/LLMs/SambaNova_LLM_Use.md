# SambaNova LLM Use

`SambaNovaLLM` integrates the [SambaNova Cloud](https://cloud.sambanova.ai) model API into agentUniverse. SambaNova Cloud is the model-serving platform of SambaNova Systems, running open-weight flagship models on purpose-built RDU hardware: Meta Llama (`Meta-Llama-3.3-70B-Instruct`, `Meta-Llama-3.1-405B-Instruct`), Alibaba's `Qwen3-32B` and the `DeepSeek-R1` reasoning model among others.

SambaNova exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.sambanova.ai/v1`, so the `SambaNovaLLM` component simply extends `OpenAIStyleLLM` and only wires up the SambaNova credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_sambanova_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_sambanova_llm'
description: 'user sambanova llm powered by the SambaNova Cloud open models'
model_name: 'Meta-Llama-3.3-70B-Instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${SAMBANOVA_API_KEY}'
api_base: 'https://api.sambanova.ai/v1'
proxy: '${SAMBANOVA_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.sambanova_llm'
  class: 'SambaNovaLLM'
```

A ready-to-use `sambanova_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/sambanova_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'sambanova-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${SAMBANOVA_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="sambanova"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

SambaNova identifies models by their exact model identifier, e.g. `Meta-Llama-3.3-70B-Instruct`. Below is an indicative selection of the models commonly available on SambaNova Cloud together with their context window (input + output tokens). The same values are hard-coded inside `SambaNovaLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                       | Context length    |
| -------------------------------- | ----------------- |
| `Meta-Llama-3.3-70B-Instruct`    | 131072 (128k)     |
| `Meta-Llama-3.1-405B-Instruct`   | 131072 (128k)     |
| `Meta-Llama-3.1-70B-Instruct`    | 131072 (128k)     |
| `Meta-Llama-3.1-8B-Instruct`     | 16384 (16k)       |
| `DeepSeek-R1`                    | 131072 (128k)     |
| `Qwen3-32B`                      | 32768 (32k)       |

Always confirm the current catalogue on the [SambaNova Cloud models page](https://cloud.sambanova.ai/models). SambaNova continuously adds and rotates models, so the table above is indicative. If a model is not present in the table, `SambaNovaLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `SAMBANOVA_API_KEY`
Optional: `SAMBANOVA_API_BASE`, `SAMBANOVA_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['SAMBANOVA_API_KEY'] = 'sambanova-***'
os.environ['SAMBANOVA_API_BASE'] = 'https://api.sambanova.ai/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
SAMBANOVA_API_KEY="sambanova-******"
SAMBANOVA_API_BASE="https://api.sambanova.ai/v1"
SAMBANOVA_PROXY=""
```

---

## 4. Obtaining the SambaNova API key

1. Sign up / sign in at [https://cloud.sambanova.ai](https://cloud.sambanova.ai).
2. Open the dashboard and navigate to **API Keys**.
3. Create a new API key, copy the generated value and assign it to `SAMBANOVA_API_KEY`.

Pricing, rate limits and the model catalogue are documented at [https://docs.sambanova.ai](https://docs.sambanova.ai).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.sambanova_llm import SambaNovaLLM

llm = SambaNovaLLM(model_name='Meta-Llama-3.3-70B-Instruct')

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

Because the SambaNova API is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_sambanova_llm` (see `sambanova_llm.yaml.example`). After configuring the `SAMBANOVA_API_KEY` environment variable you can rename it to `sambanova_llm.yaml` and reference it directly from your agents.
- SambaNova serves many open models under one endpoint, so switching between Llama, DeepSeek-R1 and Qwen3 is only a `model_name` change - no separate account or SDK per vendor is needed.
- SambaNova's RDU hardware delivers very high tokens-per-second throughput, which pairs well with agentUniverse multi-agent workflows where several LLM calls run in sequence; the Llama 3.1/3.3 and DeepSeek-R1 deployments also offer 128k-token context windows for knowledge-base agents that stuff long retrieved documents into a single prompt.
