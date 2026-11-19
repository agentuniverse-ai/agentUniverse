# LM Studio LLM Use

`LMStudioLLM` integrates [LM Studio](https://lmstudio.ai) into agentUniverse. LM Studio is a desktop application for Windows, macOS and Linux that runs large language models **fully locally**: it downloads GGUF weights (Llama, Qwen, Mistral, Gemma, ...) from Hugging Face, loads them onto your CPU/GPU and serves them through a built-in local API server.

That server speaks a fully **OpenAI-compatible** Chat Completions dialect at `http://localhost:1234/v1` by default, so the `LMStudioLLM` component simply extends `OpenAIStyleLLM` and only wires up the local endpoint and credential plumbing. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

LM Studio is a great fit for agentUniverse when you want a completely offline, privacy-preserving agent runtime with zero API cost. It is distinct from the bundled [ollama](Ollama_LLM_Use.md) integration: LM Studio is a different desktop runtime with a different default port (1234 vs ollama's 11434) and a GUI-first model management experience.

---

## 1. Create the configuration file

Create a YAML file, for example `user_lmstudio_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_lmstudio_llm'
description: 'user lm studio llm powered by locally served GGUF models'
model_name: 'qwen2.5-7b-instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
max_context_length: 32768
api_key: '${LMSTUDIO_API_KEY}'
api_base: '${LMSTUDIO_API_BASE}'
proxy: '${LMSTUDIO_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.lmstudio_llm'
  class: 'LMStudioLLM'
```

A ready-to-use `lmstudio_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/lmstudio_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'lm-studio'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${LMSTUDIO_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="lmstudio"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Unlike cloud vendors, LM Studio has **no fixed model catalogue**: you download GGUF models from Hugging Face inside the app and serve them under whatever identifier LM Studio assigns (e.g. `qwen2.5-7b-instruct`, `llama-3.1-8b-instruct`, `mistral-7b`). Typical context windows for popular downloads:

| Model name (as shown in LM Studio) | Context length    |
| ---------------------------------- | ----------------- |
| `qwen2.5-7b-instruct`              | 32768             |
| `llama-3.1-8b-instruct`            | 131072            |
| `mistral-7b`                       | 32768             |
| any private GGUF fine-tune         | model-dependent   |

Because the model names are arbitrary, `LMStudioLLM` ships **no hard-coded context-length table**. Instead:

- **Set `max_context_length` in your YAML** to the real window of the downloaded model (see the example above). This value wins over everything else.
- If nothing is configured, `LMStudioLLM` falls back to a conservative 8192-token default so prompt-budget checks stay on the safe side.

You can list the identifiers your LM Studio instance actually serves via `curl http://localhost:1234/v1/models` or in the app's **Local Server** tab.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Optional: `LMSTUDIO_API_KEY`, `LMSTUDIO_API_BASE`, `LMSTUDIO_PROXY`

All three variables are optional. When unset, `LMStudioLLM` uses `http://localhost:1234/v1`, a harmless placeholder API key and no proxy.

### 3.1 Configure through Python code

```python
import os
os.environ['LMSTUDIO_API_BASE'] = 'http://localhost:1234/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
LMSTUDIO_API_KEY=""
LMSTUDIO_API_BASE="http://localhost:1234/v1"
LMSTUDIO_PROXY=""
```

---

## 4. No API key required

A local LM Studio server does not authenticate requests — it accepts any bearer token. However, the underlying OpenAI client refuses to be constructed without a key, so `LMStudioLLM` defaults `api_key` to the harmless placeholder `lm-studio`.

You only need to set `LMSTUDIO_API_KEY` (or the `api_key` YAML field) to a real token when an authenticating gateway sits in front of your LM Studio server.

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.lmstudio_llm import LMStudioLLM

llm = LMStudioLLM(model_name='qwen2.5-7b-instruct')

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

Because LM Studio is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_lmstudio_llm` (see `lmstudio_llm.yaml.example`). Start LM Studio's local server (**Developer -> Start Server**, default port 1234), download a model, rename the example to `lmstudio_llm.yaml` and you are done — no credentials needed.
- Set `max_context_length` in the YAML to match your downloaded model; modern Llama 3.1 and Qwen2.5 builds support 32k-128k windows, which agentUniverse uses for prompt-budget checks.
- LM Studio and ollama can run side by side: they use different default ports (1234 vs 11434), so you can expose both runtimes to your agents simultaneously through `LMSTUDIO_API_BASE` / ollama's base URL.
- For remote machines running LM Studio on your LAN, point `LMSTUDIO_API_BASE` at `http://<host>:1234/v1`; enable "Serve on Local Network" in the app first.
