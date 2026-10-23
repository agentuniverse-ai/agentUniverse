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

## 3. 提前结束流式读取

OpenAI、OpenAI 风格模型及 LLM 通道在读取完成或迭代出错时会释放响应。
如果提前结束读取，请显式调用 `close()` 或 `aclose()`；尚未读取任何片段时
也可以关闭。这会释放本次响应，共享 API 客户端仍可供后续调用使用。

假设已有初始化后的 `llm` 和消息列表 `messages`，以下示例有意只读取第一个片段：

```python
stream = llm.call(messages=messages, stream=True)
try:
    first_chunk = next(stream, None)
finally:
    stream.close()
```

```python
stream = await llm.acall(messages=messages, stream=True)
try:
    first_chunk = await anext(stream, None)
finally:
    await stream.aclose()
```
