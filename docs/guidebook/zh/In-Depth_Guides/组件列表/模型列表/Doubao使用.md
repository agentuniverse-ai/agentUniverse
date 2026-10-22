# Doubao 使用

`DoubaoLLM` 将字节跳动研发的 [Doubao](https://www.volcengine.com/product/doubao)（豆包）大模型接入 agentUniverse。Doubao 模型通过字节跳动的托管模型平台 **火山方舟**（Volcengine Ark）对外提供服务，涵盖通用的 `doubao-pro` 系列、更新一代的 `doubao-1.5-pro` 系列以及高性价比的 `doubao-lite` 系列。

火山方舟提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://ark.cn-beijing.volces.com/api/v3`），因此 `DoubaoLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置方舟的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_doubao_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_doubao_llm'
description: 'user doubao llm powered by the ByteDance Doubao models on Volcengine Ark'
model_name: 'doubao-pro-32k'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${ARK_API_KEY}'
api_base: 'https://ark.cn-beijing.volces.com/api/v3'
proxy: '${DOUBAO_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.doubao_llm'
  class: 'DoubaoLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/doubao_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'ark-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${ARK_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="doubao"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

火山方舟会持续上线新的 Doubao 模型与区域化版本。下表列出了方舟 API 上的常用模型及其上下文窗口大小（输入 + 输出 token，为参考值）。这些数值同样硬编码在 `DoubaoLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称               | 上下文长度         |
| ---------------------- | ------------------ |
| `doubao-pro-32k`       | 32768 (32k)        |
| `doubao-pro-128k`      | 131072 (128k)      |
| `doubao-1.5-pro-256k`  | 262144 (256k)      |
| `doubao-lite-32k`      | 32768 (32k)        |

方舟的模型 ID 通常带有版本日期后缀（例如 `doubao-pro-32k-250527` 表示 2025-05-27 快照），组件会自动剥掉该后缀并按所属系列解析上下文窗口。

该表为 **参考值而非穷尽列表**：区域化版本、最新上线模型以及方舟推理接入点（控制台中展示的 `ep-...` 接入点 ID）的上下文窗口可能差异较大，因此不在表中的模型会保守地回退到 8192 token。如需为这类模型声明精确上限，请在 yaml 中显式设置 `max_context_length` 字段——显式配置的值始终优先于内置表格。

请以 [火山方舟控制台](https://console.volcengine.com/ark) / [官方 API 文档](https://www.volcengine.com/docs/82379/1330310) 公布的最新模型列表为准。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`ARK_API_KEY`（或别名 `DOUBAO_API_KEY`）
可选配置：`DOUBAO_API_BASE`、`DOUBAO_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['ARK_API_KEY'] = 'ark-***'
os.environ['DOUBAO_API_BASE'] = 'https://ark.cn-beijing.volces.com/api/v3'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
ARK_API_KEY="ark-******"
DOUBAO_API_BASE="https://ark.cn-beijing.volces.com/api/v3"
DOUBAO_PROXY=""
```

> `ARK_API_KEY` 是火山引擎生态通用的变量名（agentUniverse 内置的 `DoubaoEmbedding` 组件同样读取该变量），因此优先级最高；未设置时回退使用 Doubao LLM 专属的别名变量 `DOUBAO_API_KEY`。

---

## 4. 方舟 API KEY 获取

1. 登录 [https://console.volcengine.com/ark](https://console.volcengine.com/ark)。
2. 进入 **API Key 管理** 页面并创建新的 API Key。
3. 复制生成的密钥，并赋值给 `ARK_API_KEY`。

计费、速率限制与可用模型说明详见 [火山方舟官方文档](https://www.volcengine.com/docs/82379)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.doubao_llm import DoubaoLLM

llm = DoubaoLLM(model_name='doubao-pro-32k')

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

由于火山方舟兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentUniverse 源码中内置了一个 name 为 `default_doubao_llm` 的模板配置（`doubao_llm.yaml.example`），用户将其重命名为 `doubao_llm.yaml` 并配置 `ARK_API_KEY` 之后即可直接使用。
- 长文档任务可选择 256k 窗口的 `doubao-1.5-pro-256k`，日常智能体场景选择 `doubao-pro-32k`，高并发、低延迟场景选择 `doubao-lite-32k`。
- 若 `model_name` 使用方舟推理接入点（`ep-...`），建议在 yaml 中显式设置 `max_context_length`——接入点 ID 无法通过内置表格解析，会保守地回退到 8192。
