# Fireworks 使用

`FireworksLLM` 将 [Fireworks AI](https://fireworks.ai) 推理平台接入 agentUniverse。Fireworks 在托管 GPU 集群上提供了大量开源权重与微调大模型（Meta Llama 3.x、Mistral Mixtral、DeepSeek 以及众多社区微调模型），主打低延迟、高吞吐的 token 生成。模型通过完整的 Serverless 标识符寻址，例如 `accounts/fireworks/models/llama-v3p1-70b-instruct`。

Fireworks 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.fireworks.ai/inference/v1`），因此 `FireworksLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 Fireworks 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_fireworks_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_fireworks_llm'
description: 'user fireworks llm powered by the Fireworks AI models'
model_name: 'accounts/fireworks/models/llama-v3p1-70b-instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${FIREWORKS_API_KEY}'
api_base: 'https://api.fireworks.ai/inference/v1'
proxy: '${FIREWORKS_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.fireworks_llm'
  class: 'FireworksLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/fireworks_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'fw_***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${FIREWORKS_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="fireworks"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

Fireworks 会持续向 Serverless 模型目录添加新模型。下表列出了 Fireworks API 上的常用模型及其上下文窗口大小（输入 + 输出 token）。这些数值同样硬编码在 `FireworksLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                                        | 上下文长度        |
| ----------------------------------------------- | ----------------- |
| `accounts/fireworks/models/llama-v3p1-405b-instruct` | 131072 (128k) |
| `accounts/fireworks/models/llama-v3p1-70b-instruct`  | 131072 (128k) |
| `accounts/fireworks/models/llama-v3p1-8b-instruct`   | 131072 (128k) |
| `accounts/fireworks/models/mixtral-8x7b-instruct`    | 32768 (32k)   |
| `accounts/fireworks/models/deepseek-v3`              | 131072 (128k) |

该表为参考性列表，并非穷举。请以 [Fireworks 官方模型文档](https://fireworks.ai/models) 公布的最新列表与确切限制为准。

Fireworks 还支持在用户账号下部署微调模型（`accounts/<你的账号>/models/<基础模型>`），`FireworksLLM` 会自动将此类标识符解析为基础模型的上下文窗口。如果模型完全无法解析，`FireworksLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`FIREWORKS_API_KEY`
可选配置：`FIREWORKS_API_BASE`、`FIREWORKS_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['FIREWORKS_API_KEY'] = 'fw_***'
os.environ['FIREWORKS_API_BASE'] = 'https://api.fireworks.ai/inference/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
FIREWORKS_API_KEY="fw_******"
FIREWORKS_API_BASE="https://api.fireworks.ai/inference/v1"
FIREWORKS_PROXY=""
```

---

## 4. Fireworks API KEY 获取

1. 登录 [https://fireworks.ai](https://fireworks.ai)。
2. 进入 **Account -> API Keys**（[https://fireworks.ai/account/api-keys](https://fireworks.ai/account/api-keys)）页面并创建新的密钥。
3. 复制生成的 `fw_...` 密钥，并赋值给 `FIREWORKS_API_KEY`。

计费、速率限制与免费试用说明详见 [Fireworks 官方文档](https://docs.fireworks.ai)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.fireworks_llm import FireworksLLM

llm = FireworksLLM(model_name='accounts/fireworks/models/llama-v3p1-70b-instruct')

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

由于 Fireworks 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_fireworks_llm` 的模板配置（`fireworks_llm.yaml.example`），用户将其重命名为 `fireworks_llm.yaml` 并配置 `FIREWORKS_API_KEY` 之后即可直接使用。
- Serverless 模型标识符是完整路径（`accounts/fireworks/models/...`）。如果您部署了自己的微调模型，请以 `accounts/<你的账号>/models/<基础模型>` 的方式引用，组件会自动解析已知基础模型的上下文窗口。
- Llama 3.1 系列提供 128k token 的上下文窗口，非常适合需要将大量检索文档一次性填入 prompt 的 agentUniverse 知识库型智能体；而 `mixtral-8x7b-instruct` 则是面向高并发场景的高性价比 32k 选择。
