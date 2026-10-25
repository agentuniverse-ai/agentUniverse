# OpenRouter Usage
OpenRouter aggregates dozens of model providers behind one OpenAI-compatible API; the model name selects both the model and the vendor, e.g. `openai/gpt-4o` or `anthropic/claude-3.5-sonnet`.

## 1. Create the relevant file.
Create a YAML file, for example, user_openrouter.yaml
Paste the following content into your user_openrouter.yaml file.
```yaml
name: 'user_openrouter_llm'
description: 'user openrouter llm with spi'
model_name: 'openai/gpt-4o'
api_key: '${OPENROUTER_API_KEY}'
max_tokens: 2048
extra_headers:
  HTTP-Referer: 'https://your-app-site'   # optional attribution
  X-Title: 'Your App Name'                # optional attribution
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.openrouter_openai_style_llm'
  class: 'DefaultOpenRouterLLM'
```
`model_name` accepts any model id listed at https://openrouter.ai/models, prefixed with the vendor.

## 2. Environment Setup
### 2.1 Configure through Python code
```python
import os
os.environ['OPENROUTER_API_KEY'] = 'sk-or-xxxxxx'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
OPENROUTER_API_KEY="sk-or-xxxxxx"
OPENROUTER_API_BASE="https://openrouter.ai/api/v1"   # optional, this is the default
```

## 3. Tips
In agentuniverse, we have already created an llm with the name default_openrouter_llm. After configuring the OPENROUTER_API_KEY, users can directly use it.
Reference: https://openrouter.ai/docs
