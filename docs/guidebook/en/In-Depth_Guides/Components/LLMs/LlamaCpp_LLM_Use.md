# llama.cpp LLM Use

`LlamaCppLLM` integrates [llama.cpp](https://github.com/ggml-org/llama.cpp) into agentUniverse. llama.cpp is the reference C/C++ inference engine for **GGUF** large language models: its `llama-server` binary loads a local `.gguf` file (Llama, Qwen, Mistral, Gemma, ...) onto your CPU/GPU and serves it through a built-in local API server.

That server speaks a fully **OpenAI-compatible** Chat Completions dialect at `http://localhost:8080/v1` by default, so the `LlamaCppLLM` component simply extends `OpenAIStyleLLM` and only wires up the local endpoint and credential plumbing. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

llama.cpp is a great fit for agentUniverse when you want a completely offline, privacy-preserving agent runtime with zero API cost and full control over inference parameters. It is distinct from the bundled [ollama](Ollama_LLM_Use.md) integration and from the LM Studio component: llama-server is a different runtime (a plain CLI server with no GUI or model marketplace) with a different default port (8080 vs ollama's 11434 and LM Studio's 1234).

---

## 1. Start llama-server

Build or download llama.cpp, then start `llama-server` with any local GGUF model:

```bash
# From the llama.cpp repository root (after building with make/cmake)
./llama-server -m models/qwen2.5-7b-instruct-q4_k_m.gguf -c 32768 --alias qwen2.5-7b-instruct --port 8080
```

- `-m` points at the GGUF file to serve.
- `-c` sets the context window the server will allocate — pass the same value as `max_context_length` in your YAML below.
- `--alias` sets the model identifier reported by the OpenAI-compatible API; without it the file name is used.
- `--port` defaults to 8080; use a different one together with `LLAMACPP_API_BASE`.

Verify the endpoint with `curl http://localhost:8080/v1/models`.

---

## 2. Create the configuration file

Create a YAML file, for example `user_llamacpp_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_llamacpp_llm'
description: 'user llama.cpp llama-server llm powered by locally served GGUF models'
model_name: 'qwen2.5-7b-instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
max_context_length: 32768
api_key: '${LLAMACPP_API_KEY}'
api_base: '${LLAMACPP_API_BASE}'
proxy: '${LLAMACPP_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.llamacpp_llm'
  class: 'LlamaCppLLM'
```

A ready-to-use `llamacpp_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/llamacpp_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'no-key'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${LLAMACPP_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="llamacpp"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 3. Pick a model

Unlike cloud vendors, llama-server has **no fixed model catalogue**: you point it at any local GGUF file and serve it under whatever `--alias` you choose (e.g. `qwen2.5-7b-instruct`, `llama-3.1-8b-instruct`, `mistral-7b`). Typical context windows for popular models:

| Model alias (passed via `--alias`) | Context length    |
| ---------------------------------- | ----------------- |
| `qwen2.5-7b-instruct`              | 32768             |
| `llama-3.1-8b-instruct`            | 131072            |
| `mistral-7b`                       | 32768             |
| any private GGUF fine-tune         | model-dependent   |

Because the model aliases are arbitrary, `LlamaCppLLM` ships **no hard-coded context-length table**. Instead:

- **Set `max_context_length` in your YAML** to the window the server was started with (the `-c` flag). This value wins over everything else.
- If nothing is configured, `LlamaCppLLM` falls back to a conservative 8192-token default so prompt-budget checks stay on the safe side.

You can list the aliases your llama-server instance actually serves via `curl http://localhost:8080/v1/models`.

---

## 4. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Optional: `LLAMACPP_API_KEY`, `LLAMACPP_API_BASE`, `LLAMACPP_PROXY`

All three variables are optional. When unset, `LlamaCppLLM` uses `http://localhost:8080/v1`, a harmless placeholder API key and no proxy.

### 4.1 Configure through Python code

```python
import os
os.environ['LLAMACPP_API_BASE'] = 'http://localhost:8080/v1'
```

### 4.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
LLAMACPP_API_KEY=""
LLAMACPP_API_BASE="http://localhost:8080/v1"
LLAMACPP_PROXY=""
```

---

## 5. No API key required

A local llama-server does not authenticate requests — it accepts any bearer token. However, the underlying OpenAI client refuses to be constructed without a key, so `LlamaCppLLM` defaults `api_key` to the harmless placeholder `no-key`.

You only need to set `LLAMACPP_API_KEY` (or the `api_key` YAML field) to a real token when an authenticating gateway sits in front of your llama-server.

---

## 6. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.llamacpp_llm import LlamaCppLLM

llm = LlamaCppLLM(model_name='qwen2.5-7b-instruct')

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

Because llama-server is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 7. Tips

- agentUniverse ships with a ready-to-use template named `default_llamacpp_llm` (see `llamacpp_llm.yaml.example`). Start `llama-server` with your GGUF model (default port 8080), rename the example to `llamacpp_llm.yaml` and you are done — no credentials needed.
- Set `max_context_length` in the YAML to the same value as the server's `-c` flag; modern Llama 3.1 and Qwen2.5 builds support 32k-128k windows, which agentUniverse uses for prompt-budget checks.
- llama-server, ollama and LM Studio can run side by side: they use different default ports (8080 vs 11434 vs 1234), so you can expose several runtimes to your agents simultaneously through `LLAMACPP_API_BASE` / ollama's base URL / LM Studio's base URL.
- For remote machines running llama-server on your LAN, start it with `--host 0.0.0.0` and point `LLAMACPP_API_BASE` at `http://<host>:8080/v1`.
