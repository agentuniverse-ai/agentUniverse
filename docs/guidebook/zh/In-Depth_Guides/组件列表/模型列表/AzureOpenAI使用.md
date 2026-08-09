# Azure OpenAI 使用

`AzureOpenAILLM` 使用 Azure 专属的 endpoint 与 deployment 模型，将 agentUniverse 接入 Azure OpenAI Service。它是 `OpenAIStyleLLM` 的子类，因此继承了流式、异步与工具调用能力，只新增了 Azure 专属的客户端构造（`azure_endpoint`、`api_version`、`deployment_name`）。安装 OpenAI SDK：`pip install 'agentUniverse[chat_model_ext]'`（或 `pip install openai`）。

## 1. 创建相关文件
创建一个 YAML 文件，例如 `user_azure_openai.yaml`，粘贴以下内容。

```yaml
name: 'user_azure_openai_llm'
description: 'user define azure openai llm'
model_name: 'gpt-4o'
api_key: '${AZURE_OPENAI_API_KEY}'
api_base: '${AZURE_OPENAI_ENDPOINT}'
deployment_name: '${AZURE_OPENAI_DEPLOYMENT_NAME}'
api_version: '2024-02-15-preview'
proxy: '${AZURE_OPENAI_PROXY}'
max_tokens: 4096
temperature: 0.7
streaming: false
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.azure_openai_llm'
  class: 'AzureOpenAILLM'
```

也可以将 `agentuniverse/llm/default/azure_openai_llm.yaml.example` 复制到应用配置目录后直接修改其中取值。

**说明：**

`api_key`、`api_base`、`deployment_name`、`api_version`、`proxy` 等模型参数支持三种配置方式：

1. 直接字符串：在配置文件中直接填写取值。
    ```yaml
    api_key: 'xxxxx'
    deployment_name: 'my-deployment'
    ```

2. 环境变量占位符：使用 `${VARIABLE_NAME}` 语法从环境变量加载。`agentUniverse` 启动时会自动读取对应取值。
    ```yaml
    api_key: '${AZURE_OPENAI_API_KEY}'
    ```

3. 自定义函数加载：使用 `@FUNC` 注解在运行时通过自定义函数动态加载取值。
    ```yaml
    api_key: '@FUNC(load_api_key(model_name="azure_openai"))'
    ```

## 2. 环境配置
示例 YAML 使用环境变量占位符配置模型密钥等参数。

必须配置：`AZURE_OPENAI_API_KEY`、`AZURE_OPENAI_ENDPOINT`、`AZURE_OPENAI_DEPLOYMENT_NAME`
可选：`AZURE_OPENAI_API_VERSION`（默认 `2024-02-15-preview`）、`AZURE_OPENAI_PROXY`

### 2.1 通过 Python 代码配置
```python
import os
os.environ['AZURE_OPENAI_API_KEY'] = 'xxxxx'
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://<your-resource>.openai.azure.com'
os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'] = '<your-deployment-name>'
os.environ['AZURE_OPENAI_API_VERSION'] = '2024-02-15-preview'
```

### 2.2 通过 `.env` 文件配置
```
AZURE_OPENAI_API_KEY=xxxxx
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## 3. 配置参数

- `model_name`：底层 Azure OpenAI 模型（如 `gpt-4o`、`gpt-4o-mini`）。
- `api_key`：Azure OpenAI API Key（环境变量 `AZURE_OPENAI_API_KEY`）。
- `api_base` / `azure_endpoint`：Azure endpoint 地址，如 `https://my-resource.openai.azure.com`（环境变量 `AZURE_OPENAI_ENDPOINT`）。
- `deployment_name`：在 Azure OpenAI Studio 中配置的部署名（环境变量 `AZURE_OPENAI_DEPLOYMENT_NAME`）。
- `api_version`：Azure API 版本（环境变量 `AZURE_OPENAI_API_VERSION`，默认 `2024-02-15-preview`）。
- `proxy`：可选的 HTTP(S) 代理（环境变量 `AZURE_OPENAI_PROXY`）。
- `max_tokens`、`temperature`、`streaming`：标准生成参数。
