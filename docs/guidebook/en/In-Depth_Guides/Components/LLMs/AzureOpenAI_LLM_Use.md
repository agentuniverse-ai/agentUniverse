# Azure OpenAI Usage
## 1. Create the relevant file.
Create a YAML file, for example, user_azure_openai.yaml
Paste the following content into your user_azure_openai.yaml file.
```yaml
name: 'user_azure_openai_llm'
description: 'user azure openai llm'
model_name: 'gpt-4o'   # the deployment name created in the Azure portal
api_base: 'https://your-resource.openai.azure.com/'
api_key: '${AZURE_OPENAI_API_KEY}'
api_version: '2024-08-01-preview'
max_tokens: 1000
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.azure_openai_llm'
  class: 'AzureOpenAIStyleLLM'
```
Notes:
- `model_name` is the deployment name of your Azure OpenAI resource, not the upstream model id.
- If your deployment name differs from the model name, set it explicitly through `azure_deployment`.
- `api_version` is the Azure API version applied to every request, e.g. `2024-08-01-preview`.

## 2. Environment Setup
### 2.1 Configure through Python code
Must be configured: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY
```python
import os
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://your-resource.openai.azure.com/'
os.environ['AZURE_OPENAI_API_KEY'] = 'xxxxxx'
```
Optionally, the API version and the deployment name can also be provided through environment variables:
```python
os.environ['AZURE_OPENAI_API_VERSION'] = '2024-08-01-preview'
os.environ['AZURE_OPENAI_DEPLOYMENT'] = 'your-deployment-name'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="xxxxxx"
AZURE_OPENAI_API_VERSION="2024-08-01-preview"
```

## 3. Tips
In agentuniverse, we have already created an llm with the name default_azure_openai_llm. After configuring the environment variables above, users can directly use it.
Reference: https://learn.microsoft.com/azure/ai-services/openai/
