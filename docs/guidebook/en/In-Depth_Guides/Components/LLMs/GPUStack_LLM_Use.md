# GPUStack LLM Use

`GPUStackLLM` integrates [GPUStack](https://gpustack.ai) into agentUniverse. GPUStack is an open-source GPU cluster manager for running large language models: it aggregates the GPUs of your machines — servers, workstations, Apple-silicon Macs — into a single cluster, schedules model deployments onto the available devices, and serves every deployed model through the GPUStack server's gateway.

That gateway speaks a fully **OpenAI-compatible** Chat Completions dialect at `http://localhost:80/v1` by default, so the `GPUStackLLM` component simply extends `OpenAIStyleLLM` and only wires up the gateway endpoint and credential plumbing. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

GPUStack is a great fit for agentUniverse when you want a self-hosted, scalable multi-GPU inference platform with zero API cost: agents can consume whichever models the cluster operator deploys (Llama, Qwen, DeepSeek, ...) through one stable OpenAI-style endpoint, regardless of which worker GPU actually runs the model.

---

## 1. Create the configuration file

Create a YAML file, for example `user_gpustack_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_gpustack_llm'
description: 'user gpustack llm powered by models deployed on a self-hosted GPUStack gateway'
model_name: 'llama3.1-8b'
max_tokens: 1000
temperature: 0.5
streaming: True
max_context_length: 131072
api_key: '${GPUSTACK_API_KEY}'
api_base: '${GPUSTACK_API_BASE}'
proxy: '${GPUSTACK_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.gpustack_llm'
  class: 'GPUStackLLM'
```

A ready-to-use `gpustack_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/gpustack_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'gpustack'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${GPUSTACK_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="gpustack"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Unlike cloud vendors, GPUStack has **no fixed model catalogue**: the cluster operator deploys models into the cluster and serves them under whatever deployment name was chosen (e.g. `llama3.1-8b`, `qwen2.5-72b`, `deepseek-r1`). Typical context windows for popular deployments:

| Model name (as deployed in GPUStack) | Context length    |
| ------------------------------------ | ----------------- |
| `llama3.1-8b`                        | 131072            |
| `qwen2.5-72b`                        | 32768             |
| `deepseek-r1`                        | model-dependent   |
| any privately deployed fine-tune     | model-dependent   |

Because the deployed model names are arbitrary, `GPUStackLLM` ships **no hard-coded context-length table**. Instead:

- **Set `max_context_length` in your YAML** to the real window of the deployed model (see the example above). This value wins over everything else.
- If nothing is configured, `GPUStackLLM` falls back to a conservative 8192-token default so prompt-budget checks stay on the safe side.

You can list the models your GPUStack cluster actually serves via `curl http://localhost:80/v1/models` (with the appropriate `Authorization: Bearer <API key>` header when authentication is enabled) or in the GPUStack UI under "Models".

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Optional: `GPUSTACK_API_KEY`, `GPUSTACK_API_BASE`, `GPUSTACK_PROXY`

All three variables are optional. When unset, `GPUStackLLM` uses `http://localhost:80/v1`, a harmless placeholder API key and no proxy.

### 3.1 Configure through Python code

```python
import os
os.environ['GPUSTACK_API_BASE'] = 'http://localhost:80/v1'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
GPUSTACK_API_KEY=""
GPUSTACK_API_BASE="http://localhost:80/v1"
GPUSTACK_PROXY=""
```

---

## 4. API key handling

GPUStack gateways commonly enforce authentication with API keys created in the GPUStack UI ("API Keys" page); set `GPUSTACK_API_KEY` (or the `api_key` YAML field) to such a key in that case.

A GPUStack gateway can also run keyless (e.g. an isolated lab cluster). Because the underlying OpenAI client refuses to be constructed without a key, `GPUStackLLM` then defaults `api_key` to the harmless placeholder `gpustack` — a keyless gateway accepts any bearer token, so no configuration is needed.

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.gpustack_llm import GPUStackLLM

llm = GPUStackLLM(model_name='llama3.1-8b')

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

Because the GPUStack gateway is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_gpustack_llm` (see `gpustack_llm.yaml.example`). Deploy a model in your GPUStack cluster, create an API key when authentication is enabled, rename the example to `gpustack_llm.yaml` and you are done.
- Set `max_context_length` in the YAML to match the deployed model; modern Llama 3.1 and Qwen2.5 builds support 32k-128k windows, which agentUniverse uses for prompt-budget checks.
- Point `GPUSTACK_API_BASE` at your gateway when the GPUStack server is not on localhost or serves on a non-default port, e.g. `http://gpustack.internal:80/v1`.
- GPUStack and other local runtimes (ollama, LM Studio, vLLM) can run side by side; each component keeps its own `*_API_BASE`, so your agents can consume several inference platforms simultaneously.
