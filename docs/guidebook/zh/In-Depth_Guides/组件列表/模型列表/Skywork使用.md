# Skywork 使用

`SkyworkLLM` 将 [Skywork](https://www.skywork.ai) 的 API 接入 agentUniverse。Skywork（天工）是昆仑万维（Kunlun Tech）推出的大模型系列，既包含深度推理模型（`skywork-reasoner`、`skywork-t1`），也提供具备长上下文窗口的通用对话 / 文本模型（`skywork-text`）。

Skywork 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.skywork.ai/v1`），因此 `SkyworkLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 Skywork 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_skywork_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_skywork_llm'
description: 'user skywork llm powered by the Skywork models'
model_name: 'skywork-text'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${SKYWORK_API_KEY}'
api_base: 'https://api.skywork.ai/v1'
proxy: '${SKYWORK_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.skywork_llm'
  class: 'SkyworkLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/skywork_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'skywork-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${SKYWORK_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="skywork"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

下表列出了 Skywork API 上的模型及其上下文窗口大小（输入 + 输出 token，为参考值）。这些数值同样硬编码在 `SkyworkLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称           | 上下文长度       |
| ------------------ | ---------------- |
| `skywork-reasoner` | 32768 (32k)      |
| `skywork-text`     | 131072 (128k)    |
| `skywork-t1`       | 65536 (64k)      |

该表为 **参考值而非穷尽列表**：最新上线或别名模型的上下文窗口可能差异较大，因此不在表中的模型会保守地回退到 8192 token。如需为这类模型声明精确上限，请在 yaml 中显式设置 `max_context_length` 字段——显式配置的值始终优先于内置表格。

请以 Skywork 平台 / [官方 API 文档](https://platform.skywork.ai) 公布的最新模型列表为准。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`SKYWORK_API_KEY`
可选配置：`SKYWORK_API_BASE`、`SKYWORK_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['SKYWORK_API_KEY'] = 'skywork-***'
os.environ['SKYWORK_API_BASE'] = 'https://api.skywork.ai/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
SKYWORK_API_KEY="skywork-******"
SKYWORK_API_BASE="https://api.skywork.ai/v1"
SKYWORK_PROXY=""
```

---

## 4. Skywork API KEY 获取

1. 登录 Skywork 平台 [https://platform.skywork.ai](https://platform.skywork.ai)。
2. 进入 **API Key** 管理页面并创建新的密钥。
3. 复制生成的密钥，并赋值给 `SKYWORK_API_KEY`。

计费、速率限制与可用模型说明详见 [Skywork 官方 API 文档](https://platform.skywork.ai)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.skywork_llm import SkyworkLLM

llm = SkyworkLLM(model_name='skywork-text')

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

由于 Skywork 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_skywork_llm` 的模板配置（`skywork_llm.yaml.example`），用户将其重命名为 `skywork_llm.yaml` 并配置 `SKYWORK_API_KEY` 之后即可直接使用。
- 较重的推理任务可选择 `skywork-reasoner`，追求更低延迟的快速推理场景可选择 `skywork-t1`，通用对话与长文本任务可选择提供 128k 上下文窗口的 `skywork-text`。
- 对于尚未纳入内置上下文表的模型，建议在 yaml 中显式设置 `max_context_length`，以保证 prompt 预算估算准确。
