# BaiChuan Usage
## 1. Create the relevant file.
Create a YAML file, for example, user_claude.yaml
Paste the following content into your user_claude.yaml file.
```yaml
name: 'user_baichuan_llm'
description: 'user baichuan llm with spi'
model_name: 'Baichuan2-Turbo'
max_tokens: 1000
streaming: True
api_key: '${BAICHUAN_API_KEY}'
api_base: '${BAICHUAN_API_BASE}'
organization: '${BAICHUAN_ORGANIZATION}'
proxy: '${BAICHUAN_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.baichuan_openai_style_llm'
  class: 'BAICHUANOpenAIStyleLLM'
```

**Note:**

The model parameters such as `api_key`, `api_base`, `organization`, and `proxy` can be configured in three ways:

1. Direct String Value: Enter the API key string directly in the configuration file.

    ```yaml
    api_key: 'sk-xxx'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables. When `agentUniverse` is launched, it will automatically read the corresponding value from the environment variables.

    ```yaml
    api_key: '${BAICHUAN_API_KEY}'
    ```

3. Custom Function Loading: Use the `@FUNC` annotation to dynamically load the API key via a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="baichuan"))'
    ```

    The function needs to be defined in the `YamlFuncExtension` class within the `yaml_func_extension.py` file. You can refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When `agentUniverse` loads this configuration:
   - It parses the `@FUNC` annotation.
   - Executes the `load_api_key` function with the corresponding parameters.
   - Replaces the annotation content with the function's return value.


## 2. Environment Setup
### 2.1 Configure through Python code
In the example YAML, model keys and other parameters are configured using environment variable placeholders. The following section will introduce methods for setting environment variables.

Must be configured: BAICHUAN_API_KEY  
Optional: BAICHUAN_API_BASE, BAICHUAN_PROXY, BAICHUAN_ORGANIZATION
```python
import os
os.environ['BAICHUAN_API_KEY'] = 'sk-***'
os.environ['BAICHUAN_PROXY'] = 'https://xxxxxx'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
BAICHUAN_API_KEY="sk-******"
BAICHUAN_PROXY="https://xxxxxx"
BAICHUAN_API_BASE='https://api.baichuan-ai.com/v1'
BAICHUAN_ORGANIZATION=''
```
## 3. Obtaining the BAICHUAN API KEY
Reference BaiChuan Official Documentation: https://platform.baichuan-ai.com/console/apikey

## 4. Tips
In agentuniverse, we have already created an llm with the name default_baichuan_llm. After configuring the BAICHUAN_API_KEY, users can directly use it.

