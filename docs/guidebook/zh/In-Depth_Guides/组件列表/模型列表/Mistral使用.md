# Mistral 使用

## Mistral AI LLM

`MistralLLM` 连接 Mistral AI 提供的 OpenAI 兼容 API 端点（La Plateforme）。支持 Mistral Large（128k 上下文）、Nemo、Codestral 以及 La Plateforme 上的全部模型。环境变量：`MISTRAL_API_KEY`、`MISTRAL_API_BASE`（默认 `https://api.mistral.ai/v1`）。复制 `mistral_llm.yaml.example` 进行配置。

## 1. 创建相关文件
创建一个 yaml 文件，例如 `user_mistral_llm.yaml`，将以下内容粘贴到您的 `user_mistral_llm.yaml` 文件当中。

```yaml
name: 'user_mistral_llm'
description: 'default mistral llm with spi'
model_name: 'mistral-large-latest'
max_tokens: 4096
temperature: 0.7
api_key: '${MISTRAL_API_KEY}'
api_base: '${MISTRAL_API_BASE}'
proxy: '${MISTRAL_PROXY}'
streaming: False
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.mistral_llm'
  class: 'MistralLLM'
```

**note:** api_key/api_base/proxy 等模型参数有三种配置方法

1. 直接字符串值：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'xxx'
    ```

2. 环境变量占位符：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。
    ```yaml
    api_key: '${MISTRAL_API_KEY}'
    ```

3. 自定义函数加载：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。
    ```yaml
    api_key: '@FUNC(load_api_key(model_name="mistral"))'
    ```
    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)，当 agentUniverse 加载此配置时：
   - 解析 `@FUNC` 注解
   - 执行 `load_api_key` 函数并传入相应参数
   - 用函数返回值替换注解内容

## 2. 环境设置
示例 yaml 中模型密钥等参数使用环境变量占位符，下面将介绍环境变量设置方法。

必须配置：`MISTRAL_API_KEY`
可选配置：`MISTRAL_API_BASE`（默认 `https://api.mistral.ai/v1`）、`MISTRAL_PROXY`

### 2.1 通过 python 代码配置
```python
import os
os.environ['MISTRAL_API_KEY'] = 'xxx'
os.environ['MISTRAL_API_BASE'] = 'https://api.mistral.ai/v1'
```

### 2.2 通过配置文件配置
在项目的 config 目录下的 `custom_key.toml` 当中，添加配置：
```toml
MISTRAL_API_KEY="xxx"
MISTRAL_API_BASE="https://api.mistral.ai/v1"
MISTRAL_PROXY=""
```

## 3. MISTRAL API KEY 获取
参考 Mistral AI 官方文档：https://console.mistral.ai/api-keys

## 4. Tips
在 agentuniverse 中，已经提供了 `mistral_llm.yaml.example`。将其复制为 `mistral_llm.yaml`，配置好 `MISTRAL_API_KEY` 后，即可直接加载 `mistral_llm` 组件使用。
