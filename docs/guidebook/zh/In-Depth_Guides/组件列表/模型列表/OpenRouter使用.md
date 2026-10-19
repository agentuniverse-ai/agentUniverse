# OpenRouter 使用
OpenRouter 将数十家模型厂商聚合在一个OpenAI兼容API之后；模型名同时指定厂商与模型，例如 `openai/gpt-4o`、`anthropic/claude-3.5-sonnet`。

## 1. 创建相关文件
创建一个YAML文件，例如 user_openrouter.yaml
将以下内容粘贴到您的 user_openrouter.yaml 文件中。
```yaml
name: 'user_openrouter_llm'
description: 'user openrouter llm with spi'
model_name: 'openai/gpt-4o'
api_key: '${OPENROUTER_API_KEY}'
max_tokens: 2048
extra_headers:
  HTTP-Referer: 'https://your-app-site'   # 可选，应用归属
  X-Title: 'Your App Name'                # 可选，应用归属
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.openrouter_openai_style_llm'
  class: 'DefaultOpenRouterLLM'
```
`model_name` 支持 https://openrouter.ai/models 列出的任意"厂商/模型"标识。

## 2. 环境配置
### 2.1 通过python代码配置
```python
import os
os.environ['OPENROUTER_API_KEY'] = 'sk-or-xxxxxx'
```
### 2.2 通过配置文件配置
在项目config目录下的custom_key.toml文件中，添加配置：
```toml
OPENROUTER_API_KEY="sk-or-xxxxxx"
OPENROUTER_API_BASE="https://openrouter.ai/api/v1"   # 可选，默认即为此值
```

## 3. Tips
agentuniverse中已经创建好了名为default_openrouter_llm的llm，配置好OPENROUTER_API_KEY后即可直接使用。
参考：https://openrouter.ai/docs
