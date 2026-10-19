# DeepInfra LLM Use

`DeepInfraLLM` integrates the [DeepInfra](https://deepinfra.com) API into agentUniverse. DeepInfra is a serverless inference platform that hosts a large catalog of open-weight large language models — Llama, Qwen, DeepSeek, Mistral, Gemma and many more — behind a single billable API with per-token pricing, so an agent can switch between e.g. `meta-llama/Meta-Llama-3.1-405B-Instruct` and `deepseek-ai/DeepSeek-V3` by changing a single config line.

DeepInfra exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.deepinfra.com/v1/openai`, so the `DeepInfraLLM` component simply extends `OpenAIStyleLLM` and only wires up the DeepInfra credentials, API base URL and an indicative per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_deepinfra_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_deepinfra_llm'
description: 'user deepinfra llm powered by the open-weight models hosted on DeepInfra'
model_name: 'meta-llama/Meta-Llama-3.1-405B-Instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${DEEPINFRA_API_KEY}'
api_base: 'https://api.deepinfra.com/v1/openai'
proxy: '${DEEPINFRA_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.deepinfra_llm'
  class: 'DeepInfraLLM'
```

A ready-to-use `deepinfra_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/deepinfra_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'deepinfra-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${DEEPINFRA_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="deepinfra"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

DeepInfra regularly rotates its model catalog. Below is an **indicative** selection of popular models together with their context window (input + output tokens), as published by each model's creator. The same values are hard-coded inside `DeepInfraLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                                    | Context length     |
| --------------------------------------------- | ------------------ |
| `meta-llama/Meta-Llama-3.1-405B-Instruct`     | 131072 (128k)      |
| `meta-llama/Meta-Llama-3.1-70B-Instruct`      | 131072 (128k)      |
| `meta-llama/Meta-Llama-3.1-8B-Instruct`       | 131072 (128k)      |
| `Qwen/Qwen2.5-72B-Instruct`                   | 32768 (32k)        |
| `deepseek-ai/DeepSeek-V3`                     | 65536 (64k)        |

DeepInfra identifies models by their `org/model` name (for example `Qwen/Qwen2.5-72B-Instruct`); the full catalog with live pricing and availability is listed on the [DeepInfra models page](https://deepinfra.com/models). If a model is not present in the table above, `DeepInfraLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `DEEPINFRA_API_KEY`
Optional: `DEEPINFRA_API_BASE`, `DEEPINFRA_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['DEEPINFRA_API_KEY'] = 'deepinfra-***'
os.environ['DEEPINFRA_API_BASE'] = 'https://api.deepinfra.com/v1/openai'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
DEEPINFRA_API_KEY="deepinfra-******"
DEEPINFRA_API_BASE="https://api.deepinfra.com/v1/openai"
DEEPINFRA_PROXY=""
```

---

## 4. Obtaining the DeepInfra API key

1. Sign in at [https://deepinfra.com/dashboard/settings](https://deepinfra.com/dashboard/settings).
2. In the **API Keys** section create a new key.
3. Copy the generated key and assign it to `DEEPINFRA_API_KEY`.

Pricing, rate limits and the served-model catalog are documented at [https://deepinfra.com](https://deepinfra.com).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.deepinfra_llm import DeepInfraLLM

llm = DeepInfraLLM(model_name='meta-llama/Meta-Llama-3.1-405B-Instruct')

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

Because DeepInfra is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_deepinfra_llm` (see `deepinfra_llm.yaml.example`). After configuring the `DEEPINFRA_API_KEY` environment variable you can rename it to `deepinfra_llm.yaml` and reference it directly from your agents.
- The context-length table in the component is *indicative*: DeepInfra hosts third-party open-weight models whose effective window is decided by the model publisher, so always confirm the value on the model's DeepInfra page for precise prompt budgeting, or set `max_context_length` explicitly in the YAML.
- The Llama 3.1 family offers 128k-token context windows, which makes it a good fit for agentUniverse knowledge-base agents that need to stuff long retrieved documents into a single prompt, while `meta-llama/Meta-Llama-3.1-8B-Instruct` keeps latency and cost low for high-volume tool-calling loops.
