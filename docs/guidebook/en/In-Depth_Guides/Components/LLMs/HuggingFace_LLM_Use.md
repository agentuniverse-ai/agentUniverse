# HuggingFace LLM Use

The agentUniverse HuggingFace components are built entirely on the **native `huggingface_hub`
interfaces** (`InferenceClient` / `AsyncInferenceClient`) rather than on the OpenAI compatible
protocol, which is already covered by `OpenAIStyleLLM`. This gives direct access to the native
HuggingFace capabilities such as the Inference Providers router, the TGI specific sampling
parameters of `text_generation` and the TEI `feature_extraction` route.

Supported deployments:

- **HF Inference Providers Router**: set `model_name`, optionally set `provider`
- **Inference Endpoints**: set `huggingface_base_url`
- **Self hosted TGI / TEI**: set `huggingface_base_url`, e.g. `http://localhost:8080`

## 0. Install the dependency
`huggingface_hub` is an optional dependency:

```shell
pip install huggingface_hub
# or
poetry install --extras huggingface_ext
```

## 1. LLM component

Component class: `agentuniverse.llm.default.huggingface_llm.HuggingFaceLLM`

### 1.1 The two tasks

| task                | Underlying interface              | Use case                                                            |
|---------------------|-----------------------------------|---------------------------------------------------------------------|
| `chat` (default)    | `InferenceClient.chat_completion` | Conversational models, applies the chat template, provider routing   |
| `text_generation`   | `InferenceClient.text_generation` | Native TGI completion route, supports parameters absent from chat    |

### 1.2 The chat task

Create a yaml file, for example `user_huggingface_llm.yaml`:

```yaml
name: 'user_huggingface_llm'
description: 'huggingface chat llm via huggingface_hub'
model_name: 'meta-llama/Llama-3.1-8B-Instruct'
task: 'chat'
huggingface_api_key: '${HUGGINGFACE_API_KEY}'
# provider: 'auto'                                  # optional inference provider
# huggingface_base_url: 'http://localhost:8080'     # optional endpoint or self hosted TGI
max_tokens: 2048
temperature: 0.7
seed: 42
streaming: True
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.huggingface_llm'
  class: 'HuggingFaceLLM'
```

**note:** `huggingface_api_key`, `huggingface_base_url` and `provider` can be configured in three ways

1. A plain string value:
    ```yaml
    huggingface_api_key: 'hf_***'
    ```
2. An environment variable placeholder:
    ```yaml
    huggingface_api_key: '${HUGGINGFACE_API_KEY}'
    ```
3. A custom loader function:
    ```yaml
    huggingface_api_key: '@FUNC(load_api_key(model_name="huggingface"))'
    ```

### 1.3 The text_generation task and the native sampling parameters

`top_k`, `repetition_penalty`, `do_sample`, `best_of`, `typical_p` and `watermark` are **not**
part of the chat completions protocol, they do not exist in the TGI `ChatRequest` schema. Strict
backends such as TGI or `transformers serve` reject them in a chat request with
**HTTP 422 Unexpected fields**, this was reproduced against a real server. They belong to the
native TGI `/generate` route, so use `task: 'text_generation'` instead:

```yaml
name: 'user_huggingface_tg_llm'
description: 'huggingface native text generation'
model_name: 'meta-llama/Llama-3.1-8B-Instruct'
task: 'text_generation'
huggingface_base_url: 'http://localhost:8080'
max_tokens: 512
temperature: 0.7
top_p: 0.9
top_k: 40
repetition_penalty: 1.1
do_sample: true
seed: 42
streaming: True
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.huggingface_llm'
  class: 'HuggingFaceLLM'
```

Parameter compatibility:

| Parameter            | Description                     | `task: 'chat'`                      | `task: 'text_generation'`        |
|----------------------|---------------------------------|-------------------------------------|----------------------------------|
| `max_tokens`         | Maximum generated length        | ✅                                   | ✅ (mapped to `max_new_tokens`)   |
| `temperature`        | Sampling temperature            | ✅                                   | ✅                                |
| `top_p`              | Nucleus sampling                | ✅                                   | ✅                                |
| `seed`               | Random seed for reproducibility | ✅                                   | ✅                                |
| `top_k`              | Keep the top k tokens           | ⚠️ sent via `extra_body`, 422 risk  | ✅                                |
| `repetition_penalty` | Repetition penalty              | ⚠️ sent via `extra_body`, 422 risk  | ✅                                |
| `do_sample`          | Sampling instead of greedy      | ⚠️ sent via `extra_body`, 422 risk  | ✅                                |
| `best_of`            | Generate n and keep the best    | ⚠️ sent via `extra_body`, 422 risk  | ✅                                |
| `typical_p`          | Typical decoding                | ⚠️ sent via `extra_body`, 422 risk  | ✅                                |
| `watermark`          | Watermark the output            | ⚠️ sent via `extra_body`, 422 risk  | ✅                                |

> **Note**: `model_name` and `huggingface_base_url` can be set together. The request is then sent
> to `huggingface_base_url` while `model_name` is still sent as the payload model field. Without
> it `huggingface_hub` falls back to using the url itself as the model name, which makes strict
> backends answer with a HTTP 400.

The LLM component supports `call` / `acall`, sync and async streaming, and `as_langchain()` which
returns a langchain `BaseChatModel` (`HuggingFaceLangchainInstance`).

## 2. Embedding component

Component class:
`agentuniverse.agent.action.knowledge.embedding.huggingface_embedding.HuggingFaceEmbedding`,
backed by the native `huggingface_hub` `feature_extraction` interface.

Create a yaml file, for example `user_huggingface_embedding.yaml`:

```yaml
name: 'user_huggingface_embedding'
description: 'embedding use huggingface_hub feature extraction'
embedding_model_name: 'sentence-transformers/all-MiniLM-L6-v2'
huggingface_api_key: '${HUGGINGFACE_API_KEY}'
metadata:
  type: 'EMBEDDING'
  module: 'agentuniverse.agent.action.knowledge.embedding.huggingface_embedding'
  class: 'HuggingFaceEmbedding'
```

To use a self hosted TEI (Text Embeddings Inference) server or a dedicated inference endpoint,
set `huggingface_base_url` instead, `embedding_model_name` is then not part of the request:

```yaml
name: 'user_tei_embedding'
description: 'embedding use self-hosted text embeddings inference'
huggingface_base_url: 'http://localhost:8080'
metadata:
  type: 'EMBEDDING'
  module: 'agentuniverse.agent.action.knowledge.embedding.huggingface_embedding'
  class: 'HuggingFaceEmbedding'
```

The embedding component supports the sync `get_embeddings`, the async `async_get_embeddings` and
the `as_langchain()` conversion. When the model returns token level vectors, the component applies
mean pooling to obtain the sentence vector.

> **note**: `as_langchain()` prefers `langchain_huggingface` and falls back to a built-in adapter
> when it is not installed. It never uses `langchain_community.HuggingFaceHubEmbeddings`, which
> relies on `InferenceClient.post`, removed in `huggingface_hub` 1.x, and raises an
> `AttributeError` at runtime.

## 3. Environment setup

Required: `HUGGINGFACE_API_KEY` (`HF_TOKEN` is also accepted)
Optional: `HUGGINGFACE_BASE_URL`, `HUGGINGFACE_PROVIDER`

| Environment variable    | Purpose                                                                |
|-------------------------|------------------------------------------------------------------------|
| `HUGGINGFACE_API_KEY`   | HuggingFace access token, falls back to `HF_TOKEN` when unset           |
| `HF_TOKEN`              | The standard token variable of the official HuggingFace SDK             |
| `HUGGINGFACE_BASE_URL`  | Inference endpoint url (Inference Endpoints or self hosted TGI / TEI)   |
| `HUGGINGFACE_PROVIDER`  | Inference provider of the HF router, e.g. `auto`, `hf-inference`        |

### 3.1 Configure through python code
```python
import os
os.environ['HUGGINGFACE_API_KEY'] = 'hf_***'
os.environ['HUGGINGFACE_PROVIDER'] = 'auto'
```

### 3.2 Configure through the configuration file
In the custom_key.toml file under the config directory of your project, add:
```toml
HUGGINGFACE_API_KEY="hf_******"
HUGGINGFACE_BASE_URL=""
HUGGINGFACE_PROVIDER=""
```

## 4. Get a HuggingFace API key
See the official HuggingFace documentation: https://huggingface.co/settings/tokens
