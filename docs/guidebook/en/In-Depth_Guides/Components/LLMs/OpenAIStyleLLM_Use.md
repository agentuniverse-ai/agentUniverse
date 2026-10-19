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

## 3. Stopping a stream early

OpenAI, OpenAI-style, and LLM channel streams release their response when
exhausted or when iteration fails. If you stop early, call `close()` or
`aclose()` explicitly, including when no chunk has been read yet. This closes
the response and leaves the shared API client available for later calls.

Given an initialized `llm` and a `messages` list, these examples deliberately
read only the first chunk:

```python
stream = llm.call(messages=messages, stream=True)
try:
    first_chunk = next(stream, None)
finally:
    stream.close()
```

```python
stream = await llm.acall(messages=messages, stream=True)
try:
    first_chunk = await anext(stream, None)
finally:
    await stream.aclose()
```
