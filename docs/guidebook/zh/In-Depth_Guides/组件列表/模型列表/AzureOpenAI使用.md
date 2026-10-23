# Azure OpenAI 使用
## 1. 创建相关文件
创建一个YAML文件，例如 user_azure_openai.yaml
将以下内容粘贴到您的 user_azure_openai.yaml 文件中。
```yaml
name: 'user_azure_openai_llm'
description: 'user azure openai llm'
model_name: 'gpt-4o'   # Azure门户中创建的部署名称
api_base: 'https://your-resource.openai.azure.com/'
api_key: '${AZURE_OPENAI_API_KEY}'
api_version: '2024-08-01-preview'
max_tokens: 1000
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.azure_openai_llm'
  class: 'AzureOpenAIStyleLLM'
```
说明：
- `model_name` 填写Azure OpenAI资源的部署名称，而非上游模型名称。
- 若部署名称与模型名称不同，可通过 `azure_deployment` 单独指定部署名称。
- `api_version` 为Azure请求携带的API版本号，例如 `2024-08-01-preview`。

## 2. 环境配置
### 2.1 通过python代码配置
必须配置：AZURE_OPENAI_ENDPOINT、AZURE_OPENAI_API_KEY
```python
import os
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://your-resource.openai.azure.com/'
os.environ['AZURE_OPENAI_API_KEY'] = 'xxxxxx'
```
可选地，API版本与部署名称也支持通过环境变量提供：
```python
os.environ['AZURE_OPENAI_API_VERSION'] = '2024-08-01-preview'
os.environ['AZURE_OPENAI_DEPLOYMENT'] = 'your-deployment-name'
```
### 2.2 通过配置文件配置
在项目config目录下的custom_key.toml文件中，添加配置：
```toml
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="xxxxxx"
AZURE_OPENAI_API_VERSION="2024-08-01-preview"
```

## 3. Tips
agentuniverse中已经创建好了名为default_azure_openai_llm的llm，配置好上述环境变量后即可直接使用。
参考：https://learn.microsoft.com/azure/ai-services/openai/
