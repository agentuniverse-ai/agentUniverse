# Hugging Face Hub LLM Usage

`HuggingFaceHubLLM` is an LLM component backed by the Hugging Face Inference API. Through the `InferenceClient` from `huggingface_hub`, it supports 100k+ models hosted on the Hugging Face Hub, as well as dedicated Inference Endpoints (TEI / TGI). Install the SDK with `pip install huggingface_hub`.

## 1. Create the relevant file.
Create a YAML file, for example, `user_huggingface_hub_llm.yaml`. Paste the following content into it.

```yaml
name: 'user_huggingface_hub_llm'
description: 'Hugging Face Hub LLM via Inference API'
model_name: 'meta-llama/Meta-Llama-3-8B-Instruct'
api_key: '${HUGGINGFACE_API_KEY}'
inference_endpoint: ''
timeout: 30
max_tokens: 1024
temperature: 0.7
streaming: false
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.huggingface_hub_llm'
  class: 'HuggingFaceHubLLM'
```

Alternatively, copy `agentuniverse/llm/default/huggingface_hub_llm.yaml.example` into your application configuration directory and edit the values in place.

**Note:**

The model parameters such as `api_key` and `inference_endpoint` can be configured in three ways:

1. Direct String Value: Enter the value directly in the configuration file.
    ```yaml
    api_key: 'hf_xxxxx'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables.
    ```yaml
    api_key: '${HUGGINGFACE_API_KEY}'
    ```

3. Custom Function Loading: Use the `@FUNC` annotation to dynamically load the value via a custom function at runtime.

## 2. Environment Setup
Must be configured: `HUGGINGFACE_API_KEY` (or `HF_TOKEN`)
Optional: `HUGGINGFACE_INFERENCE_ENDPOINT` (for dedicated TEI / TGI endpoints)

### 2.1 Configure through Python code
```python
import os
os.environ['HUGGINGFACE_API_KEY'] = 'hf_xxxxx'
# Optional: dedicated inference endpoint
os.environ['HUGGINGFACE_INFERENCE_ENDPOINT'] = 'https://<your-endpoint>.endpoints.huggingface.cloud'
```

### 2.2 Configure through a `.env` file
```
HUGGINGFACE_API_KEY=hf_xxxxx
HUGGINGFACE_INFERENCE_ENDPOINT=https://<your-endpoint>.endpoints.huggingface.cloud
```

## 3. Configuration Parameters

- `model_name`: The Hugging Face model repo ID (e.g. `meta-llama/Meta-Llama-3-8B-Instruct`).
- `api_key`: Hugging Face API token (env: `HUGGINGFACE_API_KEY` or `HF_TOKEN`).
- `inference_endpoint`: Optional custom inference endpoint URL for dedicated endpoints (TEI / TGI); env: `HUGGINGFACE_INFERENCE_ENDPOINT`. When set, it takes precedence over `model_name`.
- `timeout`: Request timeout in seconds (default 30).
- `max_tokens`, `temperature`, `streaming`: Standard generation parameters.
