# GLM Usage
## 1. Create the relevant file.
Create a YAML file, for example, user_glm.yaml
Paste the following content into your user_glm.yaml file.
```yaml
name: 'user_zhipu_llm'
description: 'default default_zhipu_llm llm with spi'
model_name: 'glm-4-flash'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${ZHIPU_API_KEY}'
api_base: '${ZHIPU_API_BASE}'
organization: '${ZHIPU_ORGANIZATION}'
proxy: '${ZHIPU_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.zhipu_openai_style_llm'
  class: 'DefaultZhiPuLLM'
```

**Note:**

The model parameters such as `api_key`, `api_base`, `organization`, and `proxy` can be configured in three ways:

1. Direct String Value: Enter the API key string directly in the configuration file.

    ```yaml
    api_key: 'sk-xxx'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables. When `agentUniverse` is launched, it will automatically read the corresponding value from the environment variables.

    ```yaml
    api_key: '${ZHIPU_API_KEY}'
    ```

3. Custom Function Loading: Use the `@FUNC` annotation to dynamically load the API key via a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="zhipu"))'
    ```

    The function needs to be defined in the `YamlFuncExtension` class within the `yaml_func_extension.py` file. You can refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When `agentUniverse` loads this configuration:
   - It parses the `@FUNC` annotation.
   - Executes the `load_api_key` function with the corresponding parameters.
   - Replaces the annotation content with the function's return value.
   
## 2. Environment Setup
In the example YAML, model keys and other parameters are configured using environment variable placeholders. The following section will introduce methods for setting environment variables.

Must be configured: ZHIPU_API_KEY
Optional: ZHIPU_API_BASE, ZHIPU_PROXY, ZHIPU_ORGANIZATION
### 2.1 Configure through Python code
```python
import os
os.environ['ZHIPU_API_KEY'] = '*****'
os.environ['ZHIPU_API_BASE'] = 'xxxxx'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
ZHIPU_API_KEY='xxxxxx'
ZHIPU_API_BASE='https://open.bigmodel.cn/api/paas/v4/'
ZHIPU_PROXY=''
ZHIPU_ORGANIZATION=''
```
## 3. Obtaining the GLM API KEY 
Reference GLM Official Documentation: https://maas.aminer.cn

## 4. Tips
In agentuniverse, we have already created a llm with the name default_zhipu_llm. After configuring the ZHIPU_API_KEY, users can directly use it.



