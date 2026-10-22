# Cerebras 使用

`CerebrasLLM` 将 [Cerebras Inference](https://inference-docs.cerebras.ai) 推理服务接入 agentUniverse。Cerebras 基于其 **Wafer-Scale Engine（晶圆级引擎，WSE）** —— 迄今为止最大的芯片 —— 运行一批主流开源大模型（Meta Llama 3.x / Llama 4、Qwen 3、gpt-oss 等），其 token 生成速度通常达到每秒数百乃至上千 token，为业界最快的推理服务之一。

Cerebras 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.cerebras.ai/v1`），因此 `CerebrasLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 Cerebras 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_cerebras_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_cerebras_llm'
description: 'user cerebras llm powered by the Cerebras Wafer-Scale Engine inference service'
model_name: 'llama-3.3-70b'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${CEREBRAS_API_KEY}'
api_base: 'https://api.cerebras.ai/v1'
proxy: '${CEREBRAS_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.cerebras_llm'
  class: 'CerebrasLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/cerebras_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'csk-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${CEREBRAS_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="cerebras"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

Cerebras 会不定期轮换其支持的模型列表。下表列出了常用模型及其上下文窗口大小（输入 + 输出 token）。这些数值同样硬编码在 `CerebrasLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                          | 上下文长度      |
| --------------------------------- | --------------- |
| `llama-3.3-70b`                   | 131072 (128k)   |
| `llama3.1-8b`                     | 131072 (128k)   |
| `llama4-scout-17b-16e-instruct`   | 131072 (128k)   |
| `qwen-3-32b`                      | 131072 (128k)   |
| `qwen-3-235b-a22b-instruct-2507`  | 131072 (128k)   |
| `gpt-oss-120b`                    | 131072 (128k)   |

请以 [Cerebras 官方模型文档](https://inference-docs.cerebras.ai/models/overview) 公布的最新列表为准。如果某个模型不在上表中，`CerebrasLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`CEREBRAS_API_KEY`
可选配置：`CEREBRAS_API_BASE`、`CEREBRAS_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['CEREBRAS_API_KEY'] = 'csk-***'
os.environ['CEREBRAS_API_BASE'] = 'https://api.cerebras.ai/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
CEREBRAS_API_KEY="csk-******"
CEREBRAS_API_BASE="https://api.cerebras.ai/v1"
CEREBRAS_PROXY=""
```

---

## 4. CEREBRAS API KEY 获取

1. 登录 [https://cloud.cerebras.ai](https://cloud.cerebras.ai)。
2. 进入 **API Keys** 页面并创建新的密钥。
3. 复制生成的 `csk-...` 密钥，并赋值给 `CEREBRAS_API_KEY`。

Cerebras 为开发阶段提供了每日免费额度，生产环境的速率限制与计费规则详见 [Cerebras 官方文档](https://inference-docs.cerebras.ai/support/pricing)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.cerebras_llm import CerebrasLLM

llm = CerebrasLLM(model_name='llama-3.3-70b')

# 非流式
output = llm.call(messages=[{"role": "user", "content": "你好！"}])
print(output.text)

# 流式
for chunk in llm.call(messages=[{"role": "user", "content": "从 1 数到 5。"}], streaming=True):
    print(chunk.text, end='')

# 异步
import asyncio
async def main():
    out = await llm.acall(messages=[{"role": "user", "content": "你好！"}])
    print(out.text)
asyncio.run(main())
```

由于 Cerebras 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_cerebras_llm` 的模板配置（`cerebras_llm.yaml.example`），用户将其重命名为 `cerebras_llm.yaml` 并配置 `CEREBRAS_API_KEY` 之后即可直接使用。
- Cerebras 最大的特点是速度极快：即使是 70B 级别的模型也能以每秒数百 token 的速度流式输出，非常适合对端到端延迟敏感的交互式 Agent、多 Agent 协作以及快速原型验证。
- Cerebras 只提供精选的开源模型而非上游厂商的全部模型，在正式选型前请先到 [Cerebras 模型页面](https://inference-docs.cerebras.ai/models/overview) 确认可用模型及废弃公告。
