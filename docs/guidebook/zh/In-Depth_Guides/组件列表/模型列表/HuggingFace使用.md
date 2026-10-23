# Hugging Face 使用
## 1. 创建相关文件
创建一个YAML文件，例如 user_huggingface.yaml
将以下内容粘贴到您的 user_huggingface.yaml 文件中。
```yaml
name: 'user_huggingface_llm'
description: 'user hugging face hub llm'
model_name: 'meta-llama/Llama-3.1-8B-Instruct'
provider: 'together'
api_key: '${HF_TOKEN}'
max_tokens: 2048
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.huggingface_hub_llm'
  class: 'HuggingFaceHubLLM'
```
说明：
- 该组件对接Hugging Face Inference Providers路由的OpenAI兼容端点（`https://router.huggingface.co/v1`），一个令牌即可访问所有支持该模型的推理服务商。
- `provider` 为可选配置；设置后请求使用 `{model_name}:{provider}` 的路由形式，例如 `meta-llama/Llama-3.1-8B-Instruct:together`。不设置时由路由自动选择服务商。
- 如需使用专属Inference Endpoint而非路由，请将 `api_base` 设置为该端点的OpenAI兼容地址，例如 `https://xxx.endpoints.huggingface.cloud/v1`。

## 2. 环境配置
### 2.1 通过python代码配置
必须配置：HF_TOKEN
```python
import os
os.environ['HF_TOKEN'] = 'hf_xxxxxx'
```
### 2.2 通过配置文件配置
在项目config目录下的custom_key.toml文件中，添加配置：
```toml
HF_TOKEN="hf_xxxxxx"
HF_API_BASE="https://router.huggingface.co/v1"   # 可选，默认即为此值
```

## 3. Tips
agentuniverse中已经创建好了名为default_huggingface_hub_llm的llm，配置好HF_TOKEN后即可直接使用。
参考：https://huggingface.co/docs/inference-providers
