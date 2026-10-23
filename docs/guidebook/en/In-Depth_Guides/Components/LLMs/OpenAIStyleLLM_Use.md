# OpenAIStyleLLM Usage
## 1. Create the relevant file.
Create a YAML file, for example, user_openai_style_llm.yaml
Paste the following content into your user_openai_style_llm.yaml file.
```yaml
name: 'deep_seek_llm'
description: 'demo deep_seek llm with spi'
model_name: 'deepseek-chat'
max_tokens: 4000
max_context_length: 32000
api_key_env: 'DEEPSEEK_API_KEY'
api_base_env: 'DEEPSEEK_API_BASE'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.openai_style_llm'
  class: 'OpenAIStyleLLM'
```
Parameter Description:
max_context_length: The context length that the model can handle.
api_key_env: The name of the environment variable for the API key.
api_base_env: The name of the environment variable for the API base.
These parameters must be configured, and upon service startup, the corresponding values will be loaded from the environment variables.
## Per-call endpoint selection

`OpenAIStyleLLM` accepts `api_base` for one call. An omitted, `None`, or empty
value uses the configured `api_base`. Both synchronous/asynchronous and
streaming/non-streaming requests consume this option before invoking the SDK.
Request-local SDK `with_options()` clients select the endpoint while preserving
the cached client's base URL, HTTP transport, headers, query and other options.
Concurrent calls can therefore select different endpoints without changing the
shared SDK client's configuration.

##  2. Environment Setup
Mandatory Configuration: $api_key_env, $api_base_env.
In the configuration file, api_key_env and api_base_env are set as DEEPSEEK_API_KEY and DEEPSEEK_API_BASE respectively. Therefore, the configuration should be as follows:
### 2.1 Configure through Python code
```python
import os
os.environ['DEEPSEEK_API_KEY'] = 'sk-***'
os.environ['DEEPSEEK_API_BASE'] = 'https://xxxxxx'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
DEEPSEEK_API_KEY="DEEPSEEK_API_KEY"
DEEPSEEK_API_BASE="https://xxxxxx"
```
