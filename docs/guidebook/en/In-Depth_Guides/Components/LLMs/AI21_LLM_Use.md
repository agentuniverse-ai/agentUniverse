# AI21 (Jamba) LLM Use

`AI21LLM` integrates the [AI21 Labs](https://www.ai21.com) API into agentUniverse. AI21 is the company behind the **Jamba** family of large language models, built on a hybrid SSM-Transformer architecture (Mamba + Transformer + MoE) that serves very long contexts with a fraction of the memory a pure Transformer needs: `jamba-1.5-mini` / `jamba-1.5-large` and the newer `jamba-mini-1.6` / `jamba-large-1.6`, all with a 256k-token context window.

AI21 exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.ai21.com/studio/v1`, so the `AI21LLM` component simply extends `OpenAIStyleLLM` and only wires up the AI21 credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_ai21_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_ai21_llm'
description: 'user ai21 llm powered by the AI21 Labs Jamba models'
model_name: 'jamba-1.5-mini'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${AI21_API_KEY}'
api_base: 'https://api.ai21.com/studio/v1'
proxy: '${AI21_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.ai21_llm'
  class: 'AI21LLM'
```

A ready-to-use `ai21_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/ai21_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'ai21-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${AI21_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="ai21"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

AI21 regularly ships new Jamba models. Below are the models currently available on the AI21 API together with their context window (input + output tokens). The same values are hard-coded inside `AI21LLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name       | Context length    |
| ---------------- | ----------------- |
| `jamba-1.5-mini` | 256000 (256k)     |
| `jamba-1.5-large`| 256000 (256k)     |
| `jamba-mini-1.6` | 256000 (256k)     |
| `jamba-large-1.6`| 256000 (256k)     |

AI21 documents dated snapshot ids alongside the stable aliases (e.g. `jamba-mini-1.6-20250310`). `AI21LLM` strips a trailing `-YYYYMMDD` date suffix automatically, so dated snapshots resolve to the base model's context window.

Always confirm the latest list on the [AI21 models documentation](https://docs.ai21.com) page. If a model is not present in the table above, `AI21LLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `AI21_API_KEY`
Optional: `AI21_API_BASE`, `AI21_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['AI21_API_KEY'] = 'ai21-***'
os.environ['AI21_API_BASE'] = 'https://api.ai21.com/studio/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
AI21_API_KEY="ai21-******"
AI21_API_BASE="https://api.ai21.com/studio/v1"
AI21_PROXY=""
```

---

## 4. Obtaining the AI21 API key

1. Sign in at [https://platform.ai21.com](https://platform.ai21.com).
2. Navigate to **API Keys** and create a new key.
3. Copy the generated key and assign it to `AI21_API_KEY`.

Pricing, rate limits and the free-tier terms are documented at [https://docs.ai21.com](https://docs.ai21.com).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.ai21_llm import AI21LLM

llm = AI21LLM(model_name='jamba-1.5-mini')

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

Because AI21 is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_ai21_llm` (see `ai21_llm.yaml.example`). After configuring the `AI21_API_KEY` environment variable you can rename it to `ai21_llm.yaml` and reference it directly from your agents.
- `jamba-mini-1.6` / `jamba-1.5-mini` are the fast and affordable variants, while `jamba-large-1.6` / `jamba-1.5-large` are the flagship versions tuned for complex reasoning and generation tasks.
- All Jamba models offer a 256k-token context window, which makes them a good fit for agentUniverse knowledge-base agents that need to stuff long retrieved documents into a single prompt.
