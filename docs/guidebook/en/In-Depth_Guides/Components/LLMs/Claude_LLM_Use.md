# Calude Usage
## 1. Create the relevant file.
Create a YAML file, for example, user_claude.yaml
Paste the following content into your user_claude.yaml file.
```yaml
name: 'user_claude_llm'
description: 'user claude llm with spi'
model_name: 'claude-3-7-sonnet-latest'
max_tokens: 2000
temperature: 0.5
api_key: '${ANTHROPIC_API_KEY}'
api_base: 'https://api.anthropic.com'
proxy: '${ANTHROPIC_PROXY}'
streaming: True
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.claude_llm'
  class: 'ClaudeLLM'
```

**Note:**

The model parameters such as `api_key`, `api_base`, `organization`, and `proxy` can be configured in three ways:

1. Direct String Value: Enter the API key string directly in the configuration file.

    ```yaml
    api_key: 'sk-xxx'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables. When `agentUniverse` is launched, it will automatically read the corresponding value from the environment variables.

    ```yaml
    api_key: '${ANTHROPIC_API_KEY}'
    ```

3. Custom Function Loading: Use the `@FUNC` annotation to dynamically load the API key via a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="claude"))'
    ```

    The function needs to be defined in the `YamlFuncExtension` class within the `yaml_func_extension.py` file. You can refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When `agentUniverse` loads this configuration:
   - It parses the `@FUNC` annotation.
   - Executes the `load_api_key` function with the corresponding parameters.
   - Replaces the annotation content with the function's return value.

## 2. Environment Setup
In the example YAML, model keys and other parameters are configured using environment variable placeholders. The following section will introduce methods for setting environment variables.

Must be configured: ANTHROPIC_API_KEY  
Optional: ANTHROPIC_API_URL, ANTHROPIC_ORGANIZATION, ANTHROPIC_PROXY
### 2.1 Configure through Python code
```python
import os
os.environ['ANTHROPIC_API_KEY'] = 'sk-***'
os.environ['ANTHROPIC_API_URL'] = 'https://xxxxxx'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
ANTHROPIC_API_KEY="sk-******"
ANTHROPIC_API_URL="https://xxxxxx"
ANTHROPIC_PROXY='xxxx'
```
## 3. Obtaining the ANTHROPIC API KEY
Reference Claude Official Documentation: https://docs.anthropic.com/zh-CN/docs/getting-access-to-claude

## 4. Note
In agentuniverse, we have already created an llm with the name default_claude_llm. After configuring the ANTHROPIC_API_KEY, users can directly use it.