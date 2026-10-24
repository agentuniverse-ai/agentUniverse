# SiliconFlow Usage
SiliconFlow serves popular open source models (Qwen, DeepSeek, GLM, Llama, ...) through an OpenAI-compatible API.

## 1. Create the relevant file.
Create a YAML file, for example, user_siliconflow.yaml
Paste the following content into your user_siliconflow.yaml file.
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
`model_name` accepts any model id listed at https://siliconflow.cn/models, e.g. `deepseek-ai/DeepSeek-V3`.

## 2. Environment Setup
### 2.1 Configure through Python code
```python
import os
os.environ['SILICONFLOW_API_KEY'] = 'sk-xxxxxx'
```
### 2.2 Configure through the configuration file
In the custom_key.toml file under the config directory of the project, add the configuration:
```toml
SILICONFLOW_API_KEY="sk-xxxxxx"
SILICONFLOW_API_BASE="https://api.siliconflow.cn/v1"   # optional, this is the default
```

## 3. Tips
In agentuniverse, we have already created an llm with the name default_siliconflow_llm. After configuring the SILICONFLOW_API_KEY, users can directly use it.
Reference: https://docs.siliconflow.cn
