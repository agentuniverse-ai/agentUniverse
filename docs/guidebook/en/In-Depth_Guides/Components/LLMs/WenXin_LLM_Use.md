# WenXin Usage
## 1. Create the relevant file.
Create a YAML file, for example, user_wenxin.yaml
Paste the following content into your user_wenxin.yaml file.
```yaml
name: 'user_wenxin_llm'
description: 'user wenxin llm with spi'
model_name: 'ERNIE-3.5-8K'
max_tokens: 1000
streaming: true
temperature: 0.5
api_key: '${QIANFAN_AK}'
secret_key: '${QIANFAN_SK}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.wenxin_llm'
  class: 'WenXinLLM'
```

**Note:**

The model parameters such as `api_key`, `secret_key` can be configured in two ways:

1. Direct String Value: Enter the API key string directly in the configuration file.

    ```yaml
    api_key: 'sk-xxx'
    ```

2. Environment Variable Placeholder: Use the `${VARIABLE_NAME}` syntax to load from environment variables. When `agentUniverse` is launched, it will automatically read the corresponding value from the environment variables.

    ```yaml
    api_key: '${QIANFAN_AK}'
    ```


## 2. Environment Setup
In the example YAML, model keys and other parameters are configured using environment variable placeholders. The following section will introduce methods for setting environment variables.

Must be configured: QIANFAN_AK、QIANFAN_SK
### 2.1 Configure through Python code
```python
import os
os.environ['QIANFAN_AK'] = '*****'
os.environ['QIANFAN_SK'] = 'xxxxx'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
QIANFAN_AK="sk-******"
QIANFAN_SK="https://xxxxxx"
```
## 3. Obtaining the WenXin API KEY 
Reference QianFan Official Documentation: https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Dlkm79mnx

## 4. Tips
In agentuniverse, we have already created an llm with the name default_wenxin_llm. After configuring the QIANFAN_AK、QIANFAN_SK, users can directly use it.




