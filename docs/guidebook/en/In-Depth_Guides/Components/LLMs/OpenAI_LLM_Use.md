# OpenAI Usage
## 1. Create the relevant file.
Create a YAML file, for example, user_openai.yaml
Paste the following content into your user_openai.yaml file.
```yaml
name: 'user_openai_llm'
description: 'user define openai llm'
model_name: 'gpt-3.5-turbo'
temperature: 0.5
max_tokens: 2000
streaming: True
api_key: '${OPENAI_API_KEY}'
api_base: 'https://api.openai.com/v1'
organization: '${OPENAI_ORGANIZATION}'
proxy: '${OPENAI_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.default_openai_llm'
  class: 'DefaultOpenAILLM'
```

**Note:**

The model parameters such as `api_key`, `api_base`, `organization`, and `proxy` can be configured in three ways:

1. Direct String Value: Enter the API key string directly in the configuration file.

    ```yaml
    api_key: 'sk-xxx'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables. When `agentUniverse` is launched, it will automatically read the corresponding value from the environment variables.

    ```yaml
    api_key: '${OPENAI_API_KEY}'
    ```

3. Custom Function Loading: Use the `@FUNC` annotation to dynamically load the API key via a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="openai"))'
    ```

    The function needs to be defined in the `YamlFuncExtension` class within the `yaml_func_extension.py` file. You can refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When `agentUniverse` loads this configuration:
   - It parses the `@FUNC` annotation.
   - Executes the `load_api_key` function with the corresponding parameters.
   - Replaces the annotation content with the function's return value.
   
## 2. Environment Setup
In the example YAML, model keys and other parameters are configured using environment variable placeholders. The following section will introduce methods for setting environment variables.

Must be configured: OPENAI_API_KEY    
Optional: OPENAI_PROXY, OPENAI_API_BASE, OPENAI_ORGANIZATION
### 2.1 Configure through Python code
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-***'
os.environ['OPENAI_PROXY'] = 'https://xxxxxx'
os.environ['OPENAI_API_BASE'] = 'https://api.openai.com/v1'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
OPENAI_API_KEY="sk-******"
OPENAI_PROXY="https://xxxxxx"
OPENAI_API_BASE="https://api.openai.com/v1"
OPENAI_ORGANIZATION = ''
```
## 3. Obtaining the OpenAI API KEY 
[Reference](https://platform.openai.com/account/api-keys)

## 4. Tips
In agentuniverse, we have already created an llm with the name default_openai_llm. After configuring the OPENAI_API_KEY, users can directly use it.


