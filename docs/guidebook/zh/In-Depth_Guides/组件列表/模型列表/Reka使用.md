# Reka 使用

`RekaLLM` 将 [Reka AI](https://www.reka.ai) 模型家族接入 agentUniverse。Reka AI 是一家多模态大模型公司，其模型原生支持理解 **文本、图像与视频**，非常适合需要对混合媒体输入进行推理的 Agent：

- **Reka Core**：旗舰模型，多模态能力达到前沿水准。
- **Reka Flash**：速度与能力均衡的模型，面向高吞吐生产场景。
- **Reka Edge**：轻量紧凑模型，面向延迟与成本敏感场景。

Reka 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.reka.ai/v1`），因此 `RekaLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 Reka 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_reka_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_reka_llm'
description: 'user reka llm powered by the Reka AI multimodal model family'
model_name: 'reka-flash'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${REKA_API_KEY}'
api_base: 'https://api.reka.ai/v1'
proxy: '${REKA_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.reka_llm'
  class: 'RekaLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/reka_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'reka-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${REKA_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="reka"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

下表列出了 Reka 各模型及其上下文窗口大小（输入 + 输出 token）。这些数值同样硬编码在 `RekaLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称     | 上下文长度      |
| ------------ | --------------- |
| `reka-core`  | 65536 (64k)     |
| `reka-flash` | 131072 (128k)   |
| `reka-edge`  | 131072 (128k)   |

请以 [Reka 官方文档](https://docs.reka.ai) 公布的最新列表为准。如果某个模型不在上表中，`RekaLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`REKA_API_KEY`
可选配置：`REKA_API_BASE`、`REKA_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['REKA_API_KEY'] = 'reka-***'
os.environ['REKA_API_BASE'] = 'https://api.reka.ai/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
REKA_API_KEY="reka-******"
REKA_API_BASE="https://api.reka.ai/v1"
REKA_PROXY=""
```

---

## 4. REKA API KEY 获取

1. 登录 [https://platform.reka.ai](https://platform.reka.ai)。
2. 进入 **API Keys** 页面并创建新的密钥。
3. 复制生成的密钥，并赋值给 `REKA_API_KEY`。

速率限制与计费规则详见 [Reka 平台文档](https://platform.reka.ai)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.reka_llm import RekaLLM

llm = RekaLLM(model_name='reka-flash')

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

由于 Reka 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_reka_llm` 的模板配置（`reka_llm.yaml.example`），用户将其重命名为 `reka_llm.yaml` 并配置 `REKA_API_KEY` 之后即可直接使用。
- Reka 模型原生支持多模态；当端点支持更丰富的媒体载荷时，可通过 OpenAI 风格的消息内容块直接传递，无需修改本组件。
- Agent 场景推荐默认使用 `reka-flash`：推理质量强、吞吐高且拥有 128k 上下文窗口；`reka-core` 面向最复杂的多模态推理任务，`reka-edge` 面向延迟与成本敏感的调用。
