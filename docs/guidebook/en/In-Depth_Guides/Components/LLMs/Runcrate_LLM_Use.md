# Runcrate Usage
Runcrate is an AI cloud that serves open models through an OpenAI-compatible API at `https://api.runcrate.ai/v1`. The model ids are listed at `https://api.runcrate.ai/v1/models`; for agents that call tools, pick a model that lists `tools` in its `supported_features`.
## 1. Create the relevant file.
Create a YAML file, for example, user_runcrate_llm.yaml
Paste the following content into your user_runcrate_llm.yaml file.
```yaml
name: 'user_runcrate_llm'
description: 'default default_runcrate_llm llm with spi'
model_name: 'deepseek-ai/DeepSeek-V4.1-Flash'
max_tokens: 1000
temperature: 0.5
api_key: '${RUNCRATE_API_KEY}'
api_base: 'https://api.runcrate.ai/v1'
proxy: '${RUNCRATE_PROXY}'
organization: '${RUNCRATE_ORGANIZATION}'
streaming: True
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.runcrate_openai_style_llm'
  class: 'DefaultRuncrateLLM'
```

**Note:**

The model parameters such as `api_key`, `api_base`, `organization`, and `proxy` can be configured in the same three ways as for the other LLMs: a direct string value, an environment variable placeholder such as `'${RUNCRATE_API_KEY}'`, or a custom function loaded with the `@FUNC` annotation. See the [DeepSeek usage instructions](DeepSeek_LLM_Use.md) for the details.

The context length is not looked up per model. Set `max_context_length` in the YAML file to the `context_length` that `GET https://api.runcrate.ai/v1/models` reports for your model.

##  2. Environment Setup
Must be configured: RUNCRATE_API_KEY  
Optional: RUNCRATE_API_BASE, RUNCRATE_PROXY, RUNCRATE_ORGANIZATION
### 2.1 Configure through Python code
```python
import os
os.environ['RUNCRATE_API_KEY'] = 'your-api-key'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
RUNCRATE_API_KEY="your-api-key"
RUNCRATE_API_BASE="https://api.runcrate.ai/v1"
RUNCRATE_PROXY = ''
RUNCRATE_ORGANIZATION = ''
```
## 3. Obtaining the Runcrate API KEY
Get your API key from your Runcrate account: https://runcrate.ai

## 4. Tips
In agentUniverse, we have established an LLM named default_runcrate_llm. Users can directly utilize it after configuring their RUNCRATE_API_KEY.
