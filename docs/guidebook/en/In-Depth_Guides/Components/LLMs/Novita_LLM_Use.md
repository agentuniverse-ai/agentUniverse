# Novita AI LLM Use

`NovitaLLM` integrates the [Novita AI](https://novita.ai) model API into agentUniverse. Novita AI is a full-stack inference platform that serves a broad catalogue of **open-weight** models from many vendors under a single pay-as-you-go API: Meta Llama (`meta-llama/llama-3.1-70b-instruct`), DeepSeek (`deepseek/deepseek_v3`), Qwen (`qwen/qwen-2.5-32b-instruct`) and Mistral (`mistralai/mistral-nemo`) among others.

Novita exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.novita.ai/v3/openai`, so the `NovitaLLM` component simply extends `OpenAIStyleLLM` and only wires up the Novita credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_novita_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_novita_llm'
description: 'user novita llm powered by the Novita AI open models'
model_name: 'meta-llama/llama-3.1-70b-instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${NOVITA_API_KEY}'
api_base: 'https://api.novita.ai/v3/openai'
proxy: '${NOVITA_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.novita_llm'
  class: 'NovitaLLM'
```

A ready-to-use `novita_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/novita_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'novita-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${NOVITA_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="novita"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Novita identifies models by their lowercase `organization/model` name, e.g. `meta-llama/llama-3.1-70b-instruct`. Below is an indicative selection of the models commonly available on Novita together with their context window (input + output tokens). The same values are hard-coded inside `NovitaLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                                | Context length    |
| ----------------------------------------- | ----------------- |
| `meta-llama/llama-3.1-405b-instruct`      | 131072 (128k)     |
| `meta-llama/llama-3.1-70b-instruct`       | 131072 (128k)     |
| `meta-llama/llama-3.1-8b-instruct`        | 131072 (128k)     |
| `meta-llama/llama-3.3-70b-instruct`       | 131072 (128k)     |
| `meta-llama/llama-3.2-3b-instruct`        | 131072 (128k)     |
| `deepseek/deepseek_v3`                    | 131072 (128k)     |
| `deepseek/deepseek_r1`                    | 131072 (128k)     |
| `qwen/qwen-2.5-72b-instruct`              | 32768 (32k)       |
| `qwen/qwen-2.5-32b-instruct`              | 32768 (32k)       |
| `mistralai/mistral-nemo`                  | 131072 (128k)     |

Always confirm the current catalogue on the [Novita AI models page](https://novita.ai/models). Novita continuously adds and rotates models, so the table above is indicative. If a model is not present in the table, `NovitaLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `NOVITA_API_KEY`
Optional: `NOVITA_API_BASE`, `NOVITA_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['NOVITA_API_KEY'] = 'novita-***'
os.environ['NOVITA_API_BASE'] = 'https://api.novita.ai/v3/openai'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
NOVITA_API_KEY="novita-******"
NOVITA_API_BASE="https://api.novita.ai/v3/openai"
NOVITA_PROXY=""
```

---

## 4. Obtaining the Novita AI API key

1. Sign up / sign in at [https://novita.ai](https://novita.ai).
2. Open the console and navigate to **Key Management** (`https://novita.ai/dashboard/keys`).
3. Create a new API key, copy the generated value and assign it to `NOVITA_API_KEY`.

Pricing, rate limits and the free-tier terms are documented at [https://novita.ai/pricing](https://novita.ai/pricing) and [https://novita.ai/docs](https://novita.ai/docs).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.novita_llm import NovitaLLM

llm = NovitaLLM(model_name='meta-llama/llama-3.1-70b-instruct')

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

Because the Novita API is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_novita_llm` (see `novita_llm.yaml.example`). After configuring the `NOVITA_API_KEY` environment variable you can rename it to `novita_llm.yaml` and reference it directly from your agents.
- Novita serves many open models under one endpoint, so switching between Llama, DeepSeek and Qwen is only a `model_name` change - no separate account or SDK per vendor is needed.
- The Llama 3.1/3.3 and DeepSeek-V3 families offer 128k-token context windows, which makes them a good fit for agentUniverse knowledge-base agents that need to stuff long retrieved documents into a single prompt.
