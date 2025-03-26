# DeepSeek  Usage
## 1. Create the relevant file.
Create a YAML file, for example, user_deepseek_llm.yaml
Paste the following content into your user_deepseek_llm.yaml file.
```yaml
name: 'user_deepseek_llm'
description: 'default default_deepseek_llm llm with spi'
model_name: 'deepseek-chat'
max_tokens: 1000
temperature: 0.5
api_key: '${DEEPSEEK_API_KEY}'
api_base: 'https://api.deepseek.com/v1'
organization: '${DEEPSEEK_ORGANIZATION}'
proxy: '${DEEPSEEK_PROXY}'
streaming: True
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.deep_seek_openai_style_llm'
  class: 'DefaultDeepSeekLLM'
```

**Note:**

The model parameters such as `api_key`, `api_base`, `organization`, and `proxy` can be configured in three ways:

1. Direct String Value: Enter the API key string directly in the configuration file.

    ```yaml
    api_key: 'sk-xxx'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables. When `agentUniverse` is launched, it will automatically read the corresponding value from the environment variables.

    ```yaml
    api_key: '${DEEPSEEK_API_KEY}'
    ```

3. Custom Function Loading: Use the `@FUNC` annotation to dynamically load the API key via a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="deepseek"))'
    ```

    The function needs to be defined in the `YamlFuncExtension` class within the `yaml_func_extension.py` file. You can refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When `agentUniverse` loads this configuration:
   - It parses the `@FUNC` annotation.
   - Executes the `load_api_key` function with the corresponding parameters.
   - Replaces the annotation content with the function's return value.
   
##  2. Environment Setup
In the example YAML, model keys and other parameters are configured using environment variable placeholders. The following section will introduce methods for setting environment variables.

Must be configured: DEEPSEEK_API_KEY  
Optional: DEEPSEEK_API_BASE, DEEPSEEK_PROXY, DEEPSEEK_ORGANIZATION
### 2.1 Configure through Python code
```python
import os
os.environ['DEEPSEEK_API_KEY'] = 'sk-***'
os.environ['DEEPSEEK_API_BASE'] = 'https://xxxxxx'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
DEEPSEEK_API_KEY="sk-******"
DEEPSEEK_API_BASE="https://xxxxxx"
DEEPSEEK_ORGANIZATION = ''
DEEPSEEK_PROXY = ''
```
## 3. Obtaining the DeepSeek API KEY 
Please refer to the official documentation of DEEPSEEK:https://platform.deepseek.com/api_keys

## 4. Tips
In the agentuniverse, we have established an LLM named default_deepseek_llm. Users can directly utilize it after configuring their DEEPSEEK_API_KEY.

