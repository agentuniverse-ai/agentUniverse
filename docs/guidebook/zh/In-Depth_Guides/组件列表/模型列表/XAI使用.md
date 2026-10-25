# xAI（Grok）使用

`XaiLLM` 将 [xAI](https://x.ai) 的 API 接入 agentUniverse。xAI 是 **Grok** 系列大模型背后的公司，其模型在自研超算 **Colossus** 上训练，与 X 平台深度集成，涵盖旗舰推理模型（grok-4.x）、高速工具调用与多智能体变体（grok-4.20-0309）以及专门的代码模型（grok-build-0.1）。

xAI 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.x.ai/v1`），因此 `XaiLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 xAI 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_xai_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_xai_llm'
description: 'user xai llm powered by the xAI Grok models'
model_name: 'grok-4.7'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${XAI_API_KEY}'
api_base: 'https://api.x.ai/v1'
proxy: '${XAI_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.xai_llm'
  class: 'XaiLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/xai_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'xai-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${XAI_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="xai"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

xAI 会持续发布新的 Grok 模型。下表列出了 xAI API 当前提供的模型及其上下文窗口大小（输入 + 输出 token）。这些数值同样硬编码在 `XaiLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                          | 上下文长度        |
| --------------------------------- | ----------------- |
| `grok-4.7`                        | 500000 (500k)     |
| `grok-4.6`                        | 500000 (500k)     |
| `grok-4.5`                        | 500000 (500k)     |
| `grok-4.3`                        | 1000000 (1M)      |
| `grok-4.20-0309-reasoning`        | 1000000 (1M)      |
| `grok-4.20-0309-non-reasoning`    | 1000000 (1M)      |
| `grok-4.20-multi-agent-0309`      | 1000000 (1M)      |
| `grok-build-0.1`                  | 256000 (256k)     |

xAI 为每个模型都定义了别名规则：不带后缀的名称指向最新稳定版，`<模型名>-latest` 指向最新功能版本，`<模型名>-<日期>` 则固定到具体发布版本。`XaiLLM` 会自动将 `-latest` 后缀（例如 `grok-4.7-latest`）解析为基础模型的上下文窗口。

请以 [xAI 官方模型文档](https://docs.x.ai/docs/models) 公布的最新列表为准。如果某个模型不在上表中，`XaiLLM` 会保守地回退到 32768 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`XAI_API_KEY`
可选配置：`XAI_API_BASE`、`XAI_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['XAI_API_KEY'] = 'xai-***'
os.environ['XAI_API_BASE'] = 'https://api.x.ai/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
XAI_API_KEY="xai-******"
XAI_API_BASE="https://api.x.ai/v1"
XAI_PROXY=""
```

---

## 4. XAI API KEY 获取

1. 登录 [https://console.x.ai](https://console.x.ai)。
2. 进入 **API Keys** 页面并创建新的密钥。
3. 复制生成的 `xai-...` 密钥，并赋值给 `XAI_API_KEY`。

计费、速率限制与免费额度说明详见 [xAI 官方文档](https://docs.x.ai)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.xai_llm import XaiLLM

llm = XaiLLM(model_name='grok-4.7')

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

由于 xAI 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_xai_llm` 的模板配置（`xai_llm.yaml.example`），用户将其重命名为 `xai_llm.yaml` 并配置 `XAI_API_KEY` 之后即可直接使用。
- Grok 推理模型会通过 API 的 reasoning 字段输出思维链；如果追求更低延迟，可以选择 `grok-4.20-0309-non-reasoning` 跳过推理过程，而 `grok-build-0.1` 则专为编码类智能体优化。
- `grok-4.3` / `grok-4.20-0309` 系列提供 1M token 的上下文窗口，非常适合需要将大量检索文档一次性填入 prompt 的 agentUniverse 知识库型智能体。
