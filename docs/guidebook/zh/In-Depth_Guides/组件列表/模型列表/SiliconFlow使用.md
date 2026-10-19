# SiliconFlow 使用
SiliconFlow（硅基流动）通过OpenAI兼容API提供主流开源模型（Qwen、DeepSeek、GLM、Llama等）的推理服务。

## 1. 创建相关文件
创建一个YAML文件，例如 user_siliconflow.yaml
将以下内容粘贴到您的 user_siliconflow.yaml 文件中。
```yaml
name: 'user_siliconflow_llm'
description: 'user siliconflow llm with spi'
model_name: 'Qwen/Qwen2.5-72B-Instruct'
api_key: '${SILICONFLOW_API_KEY}'
max_tokens: 2048
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.siliconflow_openai_style_llm'
  class: 'DefaultSiliconFlowLLM'
```
`model_name` 支持 https://siliconflow.cn/models 列出的任意模型标识，例如 `deepseek-ai/DeepSeek-V3`。

## 2. 环境配置
### 2.1 通过python代码配置
```python
import os
os.environ['SILICONFLOW_API_KEY'] = 'sk-xxxxxx'
```
### 2.2 通过配置文件配置
在项目config目录下的custom_key.toml文件中，添加配置：
```toml
SILICONFLOW_API_KEY="sk-xxxxxx"
SILICONFLOW_API_BASE="https://api.siliconflow.cn/v1"   # 可选，默认即为此值
```

## 3. Tips
agentuniverse中已经创建好了名为default_siliconflow_llm的llm，配置好SILICONFLOW_API_KEY后即可直接使用。
参考：https://docs.siliconflow.cn
