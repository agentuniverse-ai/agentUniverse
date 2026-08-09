# Hugging Face Hub LLM 使用

`HuggingFaceHubLLM` 是基于 Hugging Face Inference API 的 LLM 组件。通过 `huggingface_hub` 的 `InferenceClient`，它支持 Hugging Face Hub 上托管的 10 万+ 模型，以及专用的 Inference Endpoints（TEI / TGI）。安装 SDK：`pip install huggingface_hub`。

## 1. 创建相关文件
创建一个 YAML 文件，例如 `user_huggingface_hub_llm.yaml`，粘贴以下内容。

```yaml
name: 'user_huggingface_hub_llm'
description: 'Hugging Face Hub LLM via Inference API'
model_name: 'meta-llama/Meta-Llama-3-8B-Instruct'
api_key: '${HUGGINGFACE_API_KEY}'
inference_endpoint: ''
timeout: 30
max_tokens: 1024
temperature: 0.7
streaming: false
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.huggingface_hub_llm'
  class: 'HuggingFaceHubLLM'
```

也可以将 `agentuniverse/llm/default/huggingface_hub_llm.yaml.example` 复制到应用配置目录后直接修改其中取值。

**说明：**

`api_key`、`inference_endpoint` 等模型参数支持三种配置方式：

1. 直接字符串：在配置文件中直接填写取值。
    ```yaml
    api_key: 'hf_xxxxx'
    ```

2. 环境变量占位符：使用 `${VARIABLE_NAME}` 语法从环境变量加载。
    ```yaml
    api_key: '${HUGGINGFACE_API_KEY}'
    ```

3. 自定义函数加载：使用 `@FUNC` 注解在运行时通过自定义函数动态加载取值。

## 2. 环境配置
必须配置：`HUGGINGFACE_API_KEY`（或 `HF_TOKEN`）
可选：`HUGGINGFACE_INFERENCE_ENDPOINT`（用于专用 TEI / TGI endpoint）

### 2.1 通过 Python 代码配置
```python
import os
os.environ['HUGGINGFACE_API_KEY'] = 'hf_xxxxx'
# 可选：专用推理 endpoint
os.environ['HUGGINGFACE_INFERENCE_ENDPOINT'] = 'https://<your-endpoint>.endpoints.huggingface.cloud'
```

### 2.2 通过 `.env` 文件配置
```
HUGGINGFACE_API_KEY=hf_xxxxx
HUGGINGFACE_INFERENCE_ENDPOINT=https://<your-endpoint>.endpoints.huggingface.cloud
```

## 3. 配置参数

- `model_name`：Hugging Face 模型 repo ID（如 `meta-llama/Meta-Llama-3-8B-Instruct`）。
- `api_key`：Hugging Face API token（环境变量 `HUGGINGFACE_API_KEY` 或 `HF_TOKEN`）。
- `inference_endpoint`：可选的自定义推理 endpoint URL，用于专用 endpoint（TEI / TGI）；环境变量 `HUGGINGFACE_INFERENCE_ENDPOINT`。设置后优先于 `model_name`。
- `timeout`：请求超时秒数（默认 30）。
- `max_tokens`、`temperature`、`streaming`：标准生成参数。
