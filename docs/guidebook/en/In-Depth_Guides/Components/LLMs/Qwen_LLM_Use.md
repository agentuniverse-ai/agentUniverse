# Qwen Use
## 1. Create the relevant file.
Create a YAML file, for example, user_qwen.yaml
Paste the following content into your user_qwen.yaml file.
```yaml
name: 'user_qwen_llm'
description: 'user qwen llm with spi'
model_name: 'qwen-turbo'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${DASHSCOPE_API_KEY}'
api_base: 'https://dashscope.aliyuncs.com/compatible-mode/v1'
organization: '${DASHSCOPE_ORGANIZATION}'
proxy: '${DASHSCOPE_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.qwen_openai_style_llm'
  class: 'QWenOpenAIStyleLLM'
```

**Note:**

The model parameters such as `api_key`, `api_base`, `organization`, and `proxy` can be configured in three ways:

1. Direct String Value: Enter the API key string directly in the configuration file.

    ```yaml
    api_key: 'sk-xxx'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables. When `agentUniverse` is launched, it will automatically read the corresponding value from the environment variables.

    ```yaml
    api_key: '${DASHSCOPE_API_KEY}'
    ```

3. Custom Function Loading: Use the `@FUNC` annotation to dynamically load the API key via a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="qwen"))'
    ```

    The function needs to be defined in the `YamlFuncExtension` class within the `yaml_func_extension.py` file. You can refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When `agentUniverse` loads this configuration:
   - It parses the `@FUNC` annotation.
   - Executes the `load_api_key` function with the corresponding parameters.
   - Replaces the annotation content with the function's return value.
   
## 2. Environment Setup
In the example YAML, model keys and other parameters are configured using environment variable placeholders. The following section will introduce methods for setting environment variables.

Must be configured:DASHSCOPE_API_KEY  
Optional: DASHSCOPE_PROXY, DASHSCOPE_ORGANIZATION, DASHSCOPE_API_BASE
### 2.1 Configure through Python code
```python
import os
os.environ['DASHSCOPE_API_KEY'] = 'sk-***'
os.environ['DASHSCOPE_PROXY'] = 'https://xxxxxx'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
DASHSCOPE_API_KEY="sk-******"
DASHSCOPE_PROXY="https://xxxxxx"
DASHSCOPE_API_BASE = ''
DASHSCOPE_ORGANIZATION = ''
```
## 3. Obtaining the DASHSCOPE API KEY 
Reference Dashscope Official Documentation：https://dashscope.console.aliyun.com/apiKey

## 4. Tips
In agentuniverse, we have already created an llm with the name default_qwen_llm. After configuring the DASHSCOPE_API_KEY, users can directly use it.


