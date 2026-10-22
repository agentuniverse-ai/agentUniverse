# Cohere LLM Use

`CohereLLM` integrates the [Cohere](https://cohere.com) API into agentUniverse. Cohere is the enterprise-LLM company behind the **Command** family of models: the flagship **command-a-03-2025** generation with a 256k-token context window, the workhorse retrieval-augmented **command-r-plus** and **command-r**, and the cost-efficient **command-r7b** - all with a strong focus on agentic workflows, tool use and multilingual RAG.

Cohere exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.cohere.com/compatibility/v1`, so the `CohereLLM` component simply extends `OpenAIStyleLLM` and only wires up the Cohere credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

Note: this endpoint is the OpenAI-style *compatibility* surface of Cohere and is independent from the native Cohere platform API used by other Cohere components (e.g. the Cohere rerank document processor). The `COHERE_API_BASE` variable configured for this LLM only affects this component.

---

## 1. Create the configuration file

Create a YAML file, for example `user_cohere_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_cohere_llm'
description: 'user cohere llm powered by the Cohere Command models'
model_name: 'command-a-03-2025'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${COHERE_API_KEY}'
api_base: 'https://api.cohere.com/compatibility/v1'
proxy: '${COHERE_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.cohere_llm'
  class: 'CohereLLM'
```

A ready-to-use `cohere_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/cohere_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'cohere-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${COHERE_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="cohere"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Cohere regularly ships new Command models. Below are the chat models currently available on the Cohere compatibility API together with their context window (input + output tokens; indicative values from the Cohere docs). The same values are hard-coded inside `CohereLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name              | Context length    |
| ----------------------- | ----------------- |
| `command-a-03-2025`     | 256000 (256k)     |
| `command-r-plus`        | 128000 (128k)     |
| `command-r`             | 128000 (128k)     |
| `command-r7b`           | 128000 (128k)     |

Cohere publishes dated releases of every family (`<modelname>-<month>-<year>`, e.g. `command-r-plus-08-2024`, `command-r7b-12-2024`). `CohereLLM` resolves a trailing date suffix to the base family's context window automatically.

Always confirm the latest list on the [Cohere models documentation](https://docs.cohere.com/docs/models) page. If a model is not present in the table above, `CohereLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `COHERE_API_KEY`
Optional: `COHERE_API_BASE`, `COHERE_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['COHERE_API_KEY'] = 'cohere-***'
os.environ['COHERE_API_BASE'] = 'https://api.cohere.com/compatibility/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
COHERE_API_KEY="cohere-******"
COHERE_API_BASE="https://api.cohere.com/compatibility/v1"
COHERE_PROXY=""
```

---

## 4. Obtaining the Cohere API key

1. Sign in at [https://dashboard.cohere.com](https://dashboard.cohere.com).
2. Navigate to **API keys** and create a new key.
3. Copy the generated key and assign it to `COHERE_API_KEY`.

Pricing, rate limits and trial-key terms are documented at [https://docs.cohere.com](https://docs.cohere.com).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.cohere_llm import CohereLLM

llm = CohereLLM(model_name='command-a-03-2025')

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

Because the Cohere compatibility API is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_cohere_llm` (see `cohere_llm.yaml.example`). After configuring the `COHERE_API_KEY` environment variable you can rename it to `cohere_llm.yaml` and reference it directly from your agents.
- `command-a-03-2025` offers a 256k-token context window and is the strongest model for complex agentic workflows; `command-r-plus` / `command-r` are tuned for RAG and tool use, while `command-r7b` trades some quality for lower latency and cost.
- The Command models are multilingual by design (23+ languages trained in), which makes them a good fit for agentUniverse agents that need to answer outside the English-only world.
- This LLM component talks to the OpenAI-compatible endpoint (`https://api.cohere.com/compatibility/v1`) and is independent from the Cohere rerank document processor, which uses the native Cohere platform API - both can be configured side by side in the same project.
