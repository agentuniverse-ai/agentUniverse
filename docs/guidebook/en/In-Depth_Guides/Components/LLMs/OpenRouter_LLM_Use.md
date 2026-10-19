# OpenRouter LLM Use

`OpenRouterLLM` integrates [OpenRouter](https://openrouter.ai) into agentUniverse. OpenRouter is a unified gateway that exposes **hundreds of large language models** from dozens of providers (OpenAI, Anthropic, Google, Meta, Mistral, DeepSeek, Qwen, xAI and many more) through a single **OpenAI-compatible** Chat Completions API, billed through one account and one API key. Models are addressed with their prefixed routing name, e.g. `openai/gpt-4o-mini` or `anthropic/claude-3.5-sonnet`.

Because the OpenRouter API is OpenAI-compatible, the `OpenRouterLLM` component simply extends `OpenAIStyleLLM` and only wires up the OpenRouter credentials, API base URL and optional attribution headers. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_openrouter_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_openrouter_llm'
description: 'user llm routing to OpenRouter models'
model_name: 'openai/gpt-4o-mini'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${OPENROUTER_API_KEY}'
api_base: 'https://openrouter.ai/api/v1'
proxy: '${OPENROUTER_PROXY}'
http_referer: 'https://your-app.example.com'
app_title: 'Your App Name'
max_context_length: 128000
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.openrouter_llm'
  class: 'OpenRouterLLM'
```

A ready-to-use `openrouter_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/openrouter_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'sk-or-v1-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${OPENROUTER_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="openrouter"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

OpenRouter routes to hundreds of models from many providers, therefore there is no fixed model table hard-coded in this component. Browse the full catalogue with pricing and context windows on the [OpenRouter models page](https://openrouter.ai/models) and use the prefixed routing name as `model_name`, for example:

| Model name                             | Context length |
| -------------------------------------- | -------------- |
| `openai/gpt-4o-mini`                   | 128000         |
| `openai/gpt-4o`                        | 128000         |
| `anthropic/claude-3.5-sonnet`          | 200000         |
| `google/gemini-flash-1.5`              | 1000000        |
| `meta-llama/llama-3.1-70b-instruct`    | 131072         |
| `deepseek/deepseek-chat`               | 64000          |

**Important:** because the context window differs per routed model, set the `max_context_length` field in the YAML to the documented window of your model (as in the example above). When the field is omitted `OpenRouterLLM` falls back to a conservative default of 8192 tokens, which keeps prompt-budget checks on the safe side but may under-use large-context models.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `OPENROUTER_API_KEY`
Optional: `OPENROUTER_API_BASE`, `OPENROUTER_PROXY`, `OPENROUTER_HTTP_REFERER`, `OPENROUTER_APP_TITLE`

### 3.1 Configure through Python code

```python
import os
os.environ['OPENROUTER_API_KEY'] = 'sk-or-v1-***'
os.environ['OPENROUTER_API_BASE'] = 'https://openrouter.ai/api/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
OPENROUTER_API_KEY="sk-or-v1-******"
OPENROUTER_API_BASE="https://openrouter.ai/api/v1"
OPENROUTER_PROXY=""
OPENROUTER_HTTP_REFERER="https://your-app.example.com"
OPENROUTER_APP_TITLE="Your App Name"
```

---

## 4. Obtaining the OpenRouter API key

1. Sign in at [https://openrouter.ai](https://openrouter.ai).
2. Open **Settings -> Keys** (https://openrouter.ai/settings/keys) and create a new key.
3. Copy the generated `sk-or-v1-...` key and assign it to `OPENROUTER_API_KEY`.

Pricing, rate limits and the credit terms are documented at [https://openrouter.ai/docs](https://openrouter.ai/docs).

---

## 5. Attribution headers (optional)

OpenRouter can attribute your API traffic to your application on its public [rankings page](https://openrouter.ai/rankings). To opt in, configure the two optional fields (or their environment variables):

- `http_referer` - sent as the `HTTP-Referer` header, usually the URL of your site or app.
- `app_title` - sent as the `X-Title` header, the human-readable name of your app.

Both are optional; when neither is set no extra headers are sent. Arbitrary additional headers can still be supplied through the generic `extra_headers` YAML key of `OpenAIStyleLLM`, whose entries take precedence over the dedicated fields.

---

## 6. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.openrouter_llm import OpenRouterLLM

llm = OpenRouterLLM(model_name='openai/gpt-4o-mini', max_context_length=128000)

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

Because OpenRouter is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 7. Tips

- agentUniverse ships with a ready-to-use template named `default_openrouter_llm` (see `openrouter_llm.yaml.example`). After configuring the `OPENROUTER_API_KEY` environment variable you can rename it to `openrouter_llm.yaml` and reference it directly from your agents.
- Switching a whole agent between providers often only requires changing `model_name` (e.g. from `openai/gpt-4o-mini` to `anthropic/claude-3.5-sonnet`) plus the matching `max_context_length` - credentials and base URL stay the same.
- Remember to raise `max_context_length` for large-context models (e.g. `google/gemini-flash-1.5` with 1M tokens); with the default 8192 fallback agentUniverse will assume a much smaller prompt budget than the model actually accepts.
