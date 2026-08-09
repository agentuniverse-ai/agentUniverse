# Azure OpenAI Usage

`AzureOpenAILLM` connects agentUniverse to the Azure OpenAI Service using the Azure-specific endpoint and deployment model. It is an `OpenAIStyleLLM` subclass, so it inherits streaming, async, and tool-calling behaviour, and only adds the Azure-specific client construction (`azure_endpoint`, `api_version`, `deployment_name`). Install the OpenAI SDK with `pip install 'agentUniverse[chat_model_ext]'` (or `pip install openai`).

## 1. Create the relevant file.
Create a YAML file, for example, `user_azure_openai.yaml`. Paste the following content into it.

```yaml
name: 'user_azure_openai_llm'
description: 'user define azure openai llm'
model_name: 'gpt-4o'
api_key: '${AZURE_OPENAI_API_KEY}'
api_base: '${AZURE_OPENAI_ENDPOINT}'
deployment_name: '${AZURE_OPENAI_DEPLOYMENT_NAME}'
api_version: '2024-02-15-preview'
proxy: '${AZURE_OPENAI_PROXY}'
max_tokens: 4096
temperature: 0.7
streaming: false
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.azure_openai_llm'
  class: 'AzureOpenAILLM'
```

Alternatively, copy `agentuniverse/llm/default/azure_openai_llm.yaml.example` into your application configuration directory and edit the values in place.

**Note:**

The model parameters such as `api_key`, `api_base`, `deployment_name`, `api_version`, and `proxy` can be configured in three ways:

1. Direct String Value: Enter the value directly in the configuration file.
    ```yaml
    api_key: 'xxxxx'
    deployment_name: 'my-deployment'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables. When `agentUniverse` is launched, it will automatically read the corresponding value from the environment variables.
    ```yaml
    api_key: '${AZURE_OPENAI_API_KEY}'
    ```

3. Custom Function Loading: Use the `@FUNC` annotation to dynamically load the value via a custom function at runtime.
    ```yaml
    api_key: '@FUNC(load_api_key(model_name="azure_openai"))'
    ```

## 2. Environment Setup
In the example YAML, model keys and other parameters are configured using environment variable placeholders.

Must be configured: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT_NAME`
Optional: `AZURE_OPENAI_API_VERSION` (defaults to `2024-02-15-preview`), `AZURE_OPENAI_PROXY`

### 2.1 Configure through Python code
```python
import os
os.environ['AZURE_OPENAI_API_KEY'] = 'xxxxx'
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://<your-resource>.openai.azure.com'
os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'] = '<your-deployment-name>'
os.environ['AZURE_OPENAI_API_VERSION'] = '2024-02-15-preview'
```

### 2.2 Configure through a `.env` file
```
AZURE_OPENAI_API_KEY=xxxxx
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## 3. Configuration Parameters

- `model_name`: The underlying Azure OpenAI model (e.g. `gpt-4o`, `gpt-4o-mini`).
- `api_key`: Azure OpenAI API key (env: `AZURE_OPENAI_API_KEY`).
- `api_base` / `azure_endpoint`: The Azure endpoint URL, e.g. `https://my-resource.openai.azure.com` (env: `AZURE_OPENAI_ENDPOINT`).
- `deployment_name`: The deployment name configured in Azure OpenAI Studio (env: `AZURE_OPENAI_DEPLOYMENT_NAME`).
- `api_version`: Azure API version (env: `AZURE_OPENAI_API_VERSION`, default `2024-02-15-preview`).
- `proxy`: Optional HTTP(S) proxy (env: `AZURE_OPENAI_PROXY`).
- `max_tokens`, `temperature`, `streaming`: Standard generation parameters.
