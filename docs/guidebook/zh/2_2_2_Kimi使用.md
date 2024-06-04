# Qwen 使用
## 1. 创建相关文件
创建一个yaml文件，例如 user_kimi.yaml
将以下内容粘贴到您的user_kimi.yaml文件当中
```yaml
name: 'user_kimi_llm'
description: 'user kimi llm with spi'
model_name: 'moonshot-v1-8k'
max_tokens: 1000
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.kimi_openai_style_llm'
  class: 'KIMIOpenAIStyleLLM'
```
### 配置字段说明
*    name 该全局唯一的名称
*    description 描述信息
*    model_name 模型名称
*    max_tokens 模型输出的最大token数
*    max_context_length: 所配置模型的最大上下文
*    metadata 元数据
*    type 类型，必须为'LLM'
*    module 模块
*    class 类名
## 2. 环境设置
必须配置：KIMI_API_KEY
选配：KIMI_PROXY
### 2.1 通过python代码配置
```python
import os
os.environ['KIMI_API_KEY'] = 'sk-***'
os.environ['KIMI_PROXY'] = 'https://xxxxxx'
```
### 2.2 通过配置文件配置
在项目的config目录下的custom_key.toml当中，添加配置：
```toml
KIMI_API_KEY="sk-******"
KIMI_PROXY="https://xxxxxx" 
```
## 3. KIMI API KEY 获取
参考 KIMI 官方文档：https://platform.moonshot.cn/console/api-keys

## 4. 注意
在agentuniverse中，我们已经创建了一个name为default_kimi_llm的llm,用户在配置KIMI_API_KEY之后可以直接使用
