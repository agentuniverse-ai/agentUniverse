# StepFun LLM Use

`StepFunLLM` integrates the [StepFun](https://www.stepfun.com) (阶跃星辰) API into agentUniverse. StepFun is a Chinese large model company whose Step model family covers the flagship text model `step-2-16k`, the multimodal vision-language models `step-1v-8k` and `step-1o-turbo-vision`, and the general-purpose `step-1-8k`.

StepFun exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.stepfun.com/v1`, so the `StepFunLLM` component simply extends `OpenAIStyleLLM` and only wires up the StepFun credentials, API base URL and an indicative per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_stepfun_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_stepfun_llm'
description: 'user stepfun llm powered by the StepFun models'
model_name: 'step-2-16k'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${STEPFUN_API_KEY}'
api_base: 'https://api.stepfun.com/v1'
proxy: '${STEPFUN_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.stepfun_llm'
  class: 'StepFunLLM'
```

A ready-to-use `stepfun_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/stepfun_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'stepfun-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${STEPFUN_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="stepfun"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

StepFun continuously adds new models. Below are popular models available on the StepFun API together with their indicative context window (input + output tokens). The same values are hard-coded inside `StepFunLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name             | Context length |
| ---------------------- | -------------- |
| `step-2-16k`           | 16384 (16k)    |
| `step-1v-8k`           | 8192 (8k)      |
| `step-1-8k`            | 8192 (8k)      |
| `step-1o-turbo-vision` | 32768 (32k)    |

The table is **indicative rather than exhaustive**: freshly announced or aliased models can have very different windows, so any model that is not listed falls back to a conservative default of 8192 tokens. To state the exact limit for such a model, set the `max_context_length` field explicitly in the YAML configuration — an explicitly configured value always wins over the built-in table.

Always confirm the current model catalogue and windows on the StepFun platform / [API reference](https://platform.stepfun.com/docs).

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `STEPFUN_API_KEY`
Optional: `STEPFUN_API_BASE`, `STEPFUN_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['STEPFUN_API_KEY'] = 'stepfun-***'
os.environ['STEPFUN_API_BASE'] = 'https://api.stepfun.com/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
STEPFUN_API_KEY="stepfun-******"
STEPFUN_API_BASE="https://api.stepfun.com/v1"
STEPFUN_PROXY=""
```

---

## 4. Obtaining the StepFun API key

1. Sign in at [https://platform.stepfun.com](https://platform.stepfun.com).
2. Navigate to the **API Key** (密钥管理) page and create a new API key.
3. Copy the generated key and assign it to `STEPFUN_API_KEY`.

Pricing, rate limits and the available model catalogue are documented in the [StepFun API reference](https://platform.stepfun.com/docs).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.stepfun_llm import StepFunLLM

llm = StepFunLLM(model_name='step-2-16k')

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

Because StepFun is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_stepfun_llm` (see `stepfun_llm.yaml.example`). After configuring the `STEPFUN_API_KEY` environment variable you can rename it to `stepfun_llm.yaml` and reference it directly from your agents.
- Use `step-2-16k` for heavier text reasoning workloads and `step-1-8k` for low-latency, high-throughput agents; `step-1v-8k` and `step-1o-turbo-vision` add image understanding with an 8k and 32k window respectively.
- For models that are not yet in the built-in context table, set `max_context_length` explicitly in the YAML so prompt budgeting stays accurate.
