# LiteLLM Usage
LiteLLM is an AI gateway that routes to 100+ LLM providers (OpenAI, Anthropic, AWS Bedrock, Google Vertex AI, Gemini, Cohere, Mistral, Groq, Together AI, Ollama, and more) through a single unified interface. The provider is selected by the `model_name` string, for example `openai/gpt-4o`, `anthropic/claude-sonnet-4-20250514`, or `bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0`.

## 1. Install the optional dependency
The `litellm` package is an optional extra. Install it with:
```shell
pip install 'agentuniverse[litellm_ext]'
```

## 2. Create the relevant file.
Create a YAML file, for example, user_litellm.yaml
Paste the following content into your user_litellm.yaml file.
```yaml
name: 'user_litellm_llm'
description: 'user litellm llm with spi'
model_name: 'openai/gpt-4o'
max_tokens: 1000
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.litellm'
  class: 'LiteLLM'
```

## 3. Environment Setup
LiteLLM reads provider credentials from the standard provider environment variables based on the `model_name` prefix. For example, an `openai/*` model uses `OPENAI_API_KEY`, an `anthropic/*` model uses `ANTHROPIC_API_KEY`, and a `bedrock/*` model uses the AWS credentials.

### 3.1 Configure through Python code
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-xxxxxx'
```

### 3.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
OPENAI_API_KEY="sk-xxxxxx"
```

### 3.3 Using a LiteLLM proxy
To route through a LiteLLM proxy instead of calling providers directly, set `LITELLM_API_KEY` and `LITELLM_API_BASE` (or the `api_key` and `api_base` fields in the YAML). The `model_name` then refers to a model alias configured on your proxy.
```toml
LITELLM_API_KEY="sk-litellm-xxxxxx"
LITELLM_API_BASE="http://localhost:4000"
```

## 4. Tips
In agentUniverse, an LLM named `default_litellm` is already registered. After configuring the provider environment variables, users can use it directly, or point `model_name` at any provider LiteLLM supports.

Reference: https://docs.litellm.ai/docs/providers
