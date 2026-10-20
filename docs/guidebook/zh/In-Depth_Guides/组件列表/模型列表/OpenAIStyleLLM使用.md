# OpenAIStyleLLM 使用
通过该配置，您可以连接任何遵守OpenAI标准的模型服务
## 1. 创建相关文件
创建一个yaml文件，例如 user_openai_style_llm.yaml
将以下内容粘贴到您的user_openai_style_llm.yaml文件当中
```yaml
name: 'deep_seek_llm'
description: 'demo deep_seek llm with spi'
model_name: 'deepseek-chat'
max_tokens: 4000
max_context_length: 32000
api_key_env: 'DEEPSEEK_API_KEY'
api_base_env: 'DEEPSEEK_API_BASE'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.openai_style_llm'
  class: 'OpenAIStyleLLM'
```
参数说明：
    max_context_length: 模型所能承接的上下文
    api_key_env: api key的env变量名
    api_base_env: api base的env变量名
上述参数必须配置,服务启动时会从环境变量中加载相关的值
## 单次调用接口地址

`OpenAIStyleLLM` 的 `api_base` 参数只指定本次调用的接口地址。不传、传入
`None` 或空字符串时，使用模型配置的 `api_base`。同步、异步以及流式、非流式
请求都会在调用 SDK 前消耗这一参数。请求使用 SDK `with_options()` 选择地址，
缓存客户端的地址、HTTP 传输、请求头、查询参数和其他配置保持不变，并发调用
可以分别选择不同地址。

## 2. 环境设置
必须配置：$api_key_env, $api_base_env
配置文件中api_key_env与api_base_env分别为DEEPSEEK_API_KEY、DEEPSEEK_API_BASE，所以配置如下：
### 2.1 通过python代码配置
```python
import os
os.environ['DEEPSEEK_API_KEY'] = 'sk-***'
os.environ['DEEPSEEK_API_BASE'] = 'https://xxxxxx'
```
### 2.2 通过配置文件配置
在项目的config目录下的custom_key.toml当中，添加配置：
```toml
DEEPSEEK_API_KEY="DEEPSEEK_API_KEY"
DEEPSEEK_API_BASE="https://xxxxxx"
```
注意，这里必须与配置文件中锁配置的api_key_env、api_base_env一致
