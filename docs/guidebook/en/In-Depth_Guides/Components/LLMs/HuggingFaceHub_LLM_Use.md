# Hugging Face Hub Usage
## 1. Create the relevant file.
Create a YAML file, for example, user_huggingface.yaml
Paste the following content into your user_huggingface.yaml file.
```yaml
name: 'user_huggingface_llm'
description: 'user hugging face hub llm'
model_name: 'meta-llama/Llama-3.1-8B-Instruct'
provider: 'together'
api_key: '${HF_TOKEN}'
max_tokens: 2048
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.huggingface_hub_llm'
  class: 'HuggingFaceHubLLM'
```
Notes:
- The component talks to the OpenAI-compatible endpoint of the Hugging Face Inference Providers router (`https://router.huggingface.co/v1`), so one token reaches every provider serving the model.
- `provider` is optional; when set, requests use the `{model_name}:{provider}` routing form, e.g. `meta-llama/Llama-3.1-8B-Instruct:together`. Remove it to let the router pick the provider automatically.
- To use a dedicated Inference Endpoint instead of the router, set `api_base` to the endpoint's OpenAI-compatible URL, e.g. `https://xxx.endpoints.huggingface.cloud/v1`.

## 2. Environment Setup
### 2.1 Configure through Python code
Must be configured: HF_TOKEN
```python
import os
os.environ['HF_TOKEN'] = 'hf_xxxxxx'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
HF_TOKEN="hf_xxxxxx"
HF_API_BASE="https://router.huggingface.co/v1"   # optional, this is the default
```

## 3. Tips
In agentuniverse, we have already created an llm with the name default_huggingface_hub_llm. After configuring the HF_TOKEN, users can directly use it.
Reference: https://huggingface.co/docs/inference-providers
