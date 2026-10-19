# Groq LLM Use

`GroqLLM` integrates the [Groq Cloud](https://groq.com) inference engine into agentUniverse. Groq runs a curated set of popular open-weight large language models (Meta Llama 3.x, Google Gemma 2, Mistral Mixtral, ...) on its custom **LPU (Language Processing Unit)** hardware, which delivers order-of-magnitude faster token generation than typical GPU based endpoints.

Groq exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.groq.com/openai/v1`, so the `GroqLLM` component simply extends `OpenAIStyleLLM` and only wires up the Groq credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the LangChain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_groq_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_groq_llm'
description: 'user groq llm powered by the Groq LPU inference engine'
model_name: 'llama-3.3-70b-versatile'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${GROQ_API_KEY}'
api_base: 'https://api.groq.com/openai/v1'
organization: '${GROQ_ORGANIZATION}'
proxy: '${GROQ_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.groq_llm'
  class: 'GroqLLM'
```

**Note:** Model parameters such as `api_key`, `api_base`, `organization` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'gsk_***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${GROQ_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="groq"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Groq regularly rotates its model catalogue. Below are the most commonly used models together with their context window (input + output tokens). The same values are hard-coded inside `GroqLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name                       | Context length |
| -------------------------------- | -------------- |
| `llama-3.3-70b-versatile`        | 131072 (128k)  |
| `llama-3.1-8b-instant`           | 131072 (128k)  |
| `llama-3.1-70b-versatile`        | 131072 (128k)  |
| `llama3-70b-8192`                | 8192           |
| `llama3-8b-8192`                 | 8192           |
| `mixtral-8x7b-32768`             | 32768          |
| `gemma2-9b-it`                   | 8192           |
| `gemma-7b-it`                    | 8192           |

Always confirm the latest list on the [Groq models documentation](https://console.groq.com/docs/models) page. If a model is not present in the table above, `GroqLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `GROQ_API_KEY`
Optional: `GROQ_API_BASE`, `GROQ_PROXY`, `GROQ_ORGANIZATION`

### 3.1 Configure through Python code

```python
import os
os.environ['GROQ_API_KEY'] = 'gsk_***'
os.environ['GROQ_API_BASE'] = 'https://api.groq.com/openai/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
GROQ_API_KEY="gsk_******"
GROQ_API_BASE="https://api.groq.com/openai/v1"
GROQ_ORGANIZATION=""
GROQ_PROXY=""
```

---

## 4. Obtaining the Groq API key

1. Sign in at [https://console.groq.com](https://console.groq.com).
2. Navigate to **API Keys** -> **Create API Key**.
3. Copy the generated `gsk_...` key and assign it to `GROQ_API_KEY`.

Groq offers a generous free tier for development; rate limits and pricing for production usage are documented at [https://console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.groq_llm import GroqLLM

llm = GroqLLM(model_name='llama-3.3-70b-versatile')

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

Because Groq is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use instance named `default_groq_llm`. After configuring the `GROQ_API_KEY` environment variable you can reference it directly from your agents.
- Groq's standout feature is latency: a 70B model can stream hundreds of tokens per second, which makes it an excellent choice for interactive agents and rapid prototyping.
- Groq does not yet support every model offered by upstream providers, so before standardising on a particular model check the [Groq models page](https://console.groq.com/docs/models) for availability and deprecation notices.
