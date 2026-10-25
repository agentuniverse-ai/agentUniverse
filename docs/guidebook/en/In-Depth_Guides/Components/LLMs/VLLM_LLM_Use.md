# vLLM LLM Use

`VLLMOpenAIStyleLLM` integrates self-hosted [vLLM](https://docs.vllm.ai/) inference servers into agentUniverse. vLLM is a high-throughput LLM inference and serving engine, and is a popular choice for running open-weight models on your own infrastructure:

- **High throughput** - up to tens of times the throughput of naive HuggingFace Transformers serving, thanks to PagedAttention and continuous batching.
- **Memory efficiency** - PagedAttention reduces KV-cache memory waste significantly.
- **Any open-weight model** - Llama, Qwen, Mistral, DeepSeek, GLM, Gemma and thousands of other models from the HuggingFace hub.
- **Data privacy** - prompts never leave your own servers.

vLLM exposes a fully **OpenAI-compatible** Chat Completions API (default address `http://localhost:8000/v1`), so the `VLLMOpenAIStyleLLM` component simply extends `OpenAIStyleLLM` and only wires up the server address, the optional credential and a per-model context-length table. Streaming, tool calling, the async interface and the LangChain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_vllm_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_vllm_llm'
description: 'user llm served by a local vLLM OpenAI-compatible server'
model_name: 'meta-llama/Llama-3.1-8B-Instruct'
max_tokens: 2048
temperature: 0.7
streaming: True
api_key: 'EMPTY'
api_base: '${VLLM_API_BASE}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.vllm_openai_style_llm'
  class: 'VLLMOpenAIStyleLLM'
```

`model_name` must be the model identifier your vLLM server was started with (the `--model` argument, e.g. `meta-llama/Llama-3.1-8B-Instruct`). Ready-to-use examples also ship with the sample projects in
`examples/sample_standard_app/intelligence/agentic/llm/buildin/vllm/` and
`examples/sample_apps/toolkit_demo_app/intelligence/agentic/llm/buildin/vllm/`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the value directly in the configuration file.

    ```yaml
    api_base: 'http://localhost:8000/v1'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_base: '${VLLM_API_BASE}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the value through a custom function at runtime.

    ```yaml
    api_base: '@FUNC(load_api_base(model_name="vllm"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_base` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Unlike cloud providers, a vLLM server can host **any** model from the HuggingFace hub, so the table below only lists commonly served models together with their maximum context window (input + output tokens). The same values are hard-coded in the `VLLM_MAX_CONTEXT_LENGTH` table consulted by `VLLMOpenAIStyleLLM.max_context_length()`, so agentUniverse can budget prompts correctly even without querying the server.

| Model name (HuggingFace id) | Context length |
| --------------------------- | -------------- |
| `meta-llama/Llama-2-7b-chat-hf` | 4096 |
| `meta-llama/Llama-2-70b-chat-hf` | 4096 |
| `meta-llama/Meta-Llama-3-8B-Instruct` | 8192 |
| `meta-llama/Meta-Llama-3-70B-Instruct` | 8192 |
| `meta-llama/Llama-3.1-8B-Instruct` | 131072 (128k) |
| `meta-llama/Llama-3.1-70B-Instruct` | 131072 (128k) |
| `meta-llama/Llama-3.1-405B-Instruct` | 131072 (128k) |
| `meta-llama/Llama-3.3-70B-Instruct` | 131072 (128k) |
| `Qwen/Qwen2-7B-Instruct` | 32768 |
| `Qwen/Qwen2.5-7B-Instruct` | 32768 |
| `Qwen/Qwen2.5-72B-Instruct` | 32768 |
| `Qwen/Qwen3-8B` | 32768 |
| `Qwen/Qwen3-32B` | 32768 |
| `mistralai/Mistral-7B-Instruct-v0.2` | 32768 |
| `mistralai/Mixtral-8x7B-Instruct-v0.1` | 32768 |
| `mistralai/Mixtral-8x22B-Instruct-v0.1` | 65536 |
| `google/gemma-2-9b-it` | 8192 |

**Important:** the context window actually available is determined by the `--max-model-len` flag used when starting the vLLM server, which may be smaller than the model's native maximum. If your model is not present in the table above, or you started the server with a reduced `--max-model-len`, simply set the value explicitly in the YAML:

```yaml
max_context_length: 32768
```

An explicitly configured `max_context_length` always wins over the built-in table, and unknown models fall back to a conservative default of 4096 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Optional: `VLLM_API_BASE` (defaults to `http://localhost:8000/v1`), `VLLM_API_KEY`

A locally started vLLM server does **not** require an API key; the OpenAI client still expects a non-empty value, so the component defaults `api_key` to the placeholder string `'EMPTY'`. Only set `VLLM_API_KEY` when your server is deployed behind an authenticating gateway.

### 3.1 Configure through Python code

```python
import os
os.environ['VLLM_API_BASE'] = 'http://localhost:8000/v1'
os.environ['VLLM_API_KEY'] = 'EMPTY'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
VLLM_API_BASE="http://localhost:8000/v1"
VLLM_API_KEY="EMPTY"
```

---

## 4. Starting a vLLM server

1. Install vLLM (see the [official installation guide](https://docs.vllm.ai/en/latest/getting_started/installation.html)):

    ```bash
    pip install vllm
    ```

2. Start the OpenAI-compatible server with the model of your choice:

    ```bash
    python -m vllm.entrypoints.openai.api_server \
        --model meta-llama/Llama-3.1-8B-Instruct \
        --port 8000
    ```

3. (Optional) Deploy through Docker, useful for production machines:

    ```bash
    docker run --gpus all -p 8000:8000 --ipc=host \
        -v ~/.cache/huggingface:/root/.cache/huggingface \
        vllm/vllm-openai:latest \
        --model meta-llama/Llama-3.1-8B-Instruct
    ```

4. Verify the server is reachable before wiring it into agentUniverse:

    ```bash
    curl http://localhost:8000/v1/models
    ```

For large models add `--tensor-parallel-size <num_gpus>`; to cap memory-hungry long contexts add `--max-model-len 32768` (and mirror the value in `max_context_length`).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.vllm_openai_style_llm import VLLMOpenAIStyleLLM

llm = VLLMOpenAIStyleLLM(model_name='meta-llama/Llama-3.1-8B-Instruct')

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

Because vLLM is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- vLLM-specific sampling extensions offered by the server (for example beam-search controls) should be forwarded through `ext_params` in the YAML or the `extra_body` keyword argument of `call`/`acall`, which the base `OpenAIStyleLLM` merges into the request body.
- Prefer starting the server with an explicit `--max-model-len` and setting the same value as `max_context_length` in the component YAML; this keeps agentUniverse's prompt budgeting in sync with what the server actually accepts.
- `Qwen/Qwen2.5-7B-Instruct` is a solid default for bilingual (Chinese/English) agent workloads on a single consumer GPU, while `meta-llama/Llama-3.1-8B-Instruct` is a common general-purpose starting point.
- Ready-to-use configurations for the `vllm` buildin instances (e.g. `vllm-llama-3.1-8b`, `vllm-qwen-2.5-7b`) ship with the sample projects; reference them from your agents by name after setting `VLLM_API_BASE`.
