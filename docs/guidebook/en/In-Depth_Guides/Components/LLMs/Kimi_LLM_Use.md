# KIMI Usage
## 1. Create the relevant file.
Create a YAML file, for example, user_kimi.yaml
Paste the following content into your user_kimi.yaml file.
```yaml
name: 'user_kimi_llm'
description: 'user kimi llm with spi'
model_name: 'moonshot-v1-128k'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${KIMI_API_KEY}'
api_base: 'https://api.moonshot.cn/v1'
organization: '${KIMI_ORGANIZATION}'
proxy: '${KIMI_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.kimi_openai_style_llm'
  class: 'KIMIOpenAIStyleLLM'
```

**Note:**

The model parameters such as `api_key`, `api_base`, `organization`, and `proxy` can be configured in three ways:

1. Direct String Value: Enter the API key string directly in the configuration file.

    ```yaml
    api_key: 'sk-xxx'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables. When `agentUniverse` is launched, it will automatically read the corresponding value from the environment variables.

    ```yaml
    api_key: '${KIMI_API_KEY}'
    ```

3. Custom Function Loading: Use the `@FUNC` annotation to dynamically load the API key via a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="kimi"))'
    ```

    The function needs to be defined in the `YamlFuncExtension` class within the `yaml_func_extension.py` file. You can refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When `agentUniverse` loads this configuration:
   - It parses the `@FUNC` annotation.
   - Executes the `load_api_key` function with the corresponding parameters.
   - Replaces the annotation content with the function's return value.
   
## 2. Environment Setup
In the example YAML, model keys and other parameters are configured using environment variable placeholders. The following section will introduce methods for setting environment variables.

Must be configured: KIMI_API_KEY
Optional: KIMI_PROXY, KIMI_ORGANIZATION, KIMI_API_BASE

### 2.1 Configure through Python code
```python
import os
os.environ['KIMI_API_KEY'] = 'sk-***'
os.environ['KIMI_PROXY'] = 'https://xxxxxx'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
KIMI_API_KEY="sk-******"
KIMI_PROXY="https://xxxxxx" 
KIMI_API_BASE='https://api.moonshot.cn/v1'
KIMI_ORGANIZATION = ''
```
## 3. Obtaining the KIMI API KEY 
Reference KIMI Official Documentation:https://platform.moonshot.cn/console/api-keys

## 4. Tips
In agentuniverse, we have already created an llm with the name default_kimi_llm. After configuring the KIMI_API_KEY, users can directly use it.
