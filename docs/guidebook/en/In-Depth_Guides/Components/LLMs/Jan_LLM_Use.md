# Jan LLM Use

`JanLLM` integrates [Jan](https://jan.ai) into agentUniverse. Jan is an open-source desktop AI assistant for Windows, macOS and Linux that runs large language models **fully locally and offline**: it downloads GGUF weights (Llama, Qwen, Mistral, Gemma, ...) from Hugging Face through its built-in model hub, loads them onto your CPU/GPU and serves them through a built-in local API server.

That server speaks a fully **OpenAI-compatible** Chat Completions dialect at `http://127.0.0.1:1337/v1` by default, so the `JanLLM` component simply extends `OpenAIStyleLLM` and only wires up the local endpoint and credential plumbing. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

Jan is a great fit for agentUniverse when you want a completely offline, privacy-preserving agent runtime with zero API cost. It is distinct from the bundled [ollama](Ollama_LLM_Use.md) integration: Jan is a desktop runtime with a different default port (1337 vs ollama's 11434) and a GUI-first, ChatGPT-style model management experience.

---

## 1. Create the configuration file

Create a YAML file, for example `user_jan_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_jan_llm'
description: 'user jan llm powered by locally served GGUF models'
model_name: 'llama3.1-8b-instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
max_context_length: 131072
api_key: '${JAN_API_KEY}'
api_base: '${JAN_API_BASE}'
proxy: '${JAN_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.jan_llm'
  class: 'JanLLM'
```

A ready-to-use `jan_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/jan_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'jan'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${JAN_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="jan"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Unlike cloud vendors, Jan has **no fixed model catalogue**: you download GGUF models from Hugging Face inside the app and serve them under whatever identifier the model folder uses (e.g. `llama3.1-8b-instruct`, `qwen2.5-7b-instruct`, `mistral-7b`). Typical context windows for popular downloads:

| Model name (as shown in Jan)      | Context length    |
| ---------------------------------- | ----------------- |
| `llama3.1-8b-instruct`             | 131072            |
| `qwen2.5-7b-instruct`              | 32768             |
| `mistral-7b`                       | 32768             |
| any private GGUF fine-tune         | model-dependent   |

Because the model names are arbitrary, `JanLLM` ships **no hard-coded context-length table**. Instead:

- **Set `max_context_length` in your YAML** to the real window of the downloaded model (see the example above). This value wins over everything else.
- If nothing is configured, `JanLLM` falls back to a conservative 8192-token default so prompt-budget checks stay on the safe side.

You can list the identifiers your Jan instance actually serves via `curl http://127.0.0.1:1337/v1/models` or in the app's model list.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Optional: `JAN_API_KEY`, `JAN_API_BASE`, `JAN_PROXY`

All three variables are optional. When unset, `JanLLM` uses `http://127.0.0.1:1337/v1`, a harmless placeholder API key and no proxy.

### 3.1 Configure through Python code

```python
import os
os.environ['JAN_API_BASE'] = 'http://127.0.0.1:1337/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
JAN_API_KEY=""
JAN_API_BASE="http://127.0.0.1:1337/v1"
JAN_PROXY=""
```

---

## 4. No API key required

A local Jan server does not authenticate requests — it accepts any bearer token. However, the underlying OpenAI client refuses to be constructed without a key, so `JanLLM` defaults `api_key` to the harmless placeholder `jan`.

You only need to set `JAN_API_KEY` (or the `api_key` YAML field) to a real token when an authenticating gateway sits in front of your Jan server.

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.jan_llm import JanLLM

llm = JanLLM(model_name='llama3.1-8b-instruct')

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

Because Jan is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_jan_llm` (see `jan_llm.yaml.example`). Start Jan's local API server (Settings -> **Local API Server**, default port 1337), download a model, rename the example to `jan_llm.yaml` and you are done — no credentials needed.
- Set `max_context_length` in the YAML to match your downloaded model; modern Llama 3.1 and Qwen2.5 builds support 32k-128k windows, which agentUniverse uses for prompt-budget checks.
- Jan and ollama can run side by side: they use different default ports (1337 vs 11434), so you can expose both runtimes to your agents simultaneously through `JAN_API_BASE` / ollama's base URL.
- For remote machines running Jan on your LAN, point `JAN_API_BASE` at `http://<host>:1337/v1`; open the server to your network in Jan's settings first.
