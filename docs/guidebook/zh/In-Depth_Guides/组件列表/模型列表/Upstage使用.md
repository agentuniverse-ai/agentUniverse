# Upstage（Solar）使用

`UpstageLLM` 将 [Upstage](https://upstage.ai) 的 Solar API 接入 agentUniverse。Upstage 是一家位于韩国首尔的 AI 公司，也是 **Solar** 系列大模型背后的团队，其模型针对韩语和多语言场景深度优化，涵盖旗舰前沿模型（solar-pro-2）、高性价比通用模型（solar-pro、solar-mini）以及专门的文档理解模型（solar-docvision）。

Upstage 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.upstage.ai/v1/solar`），因此 `UpstageLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 Upstage 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 Langchain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_upstage_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_upstage_llm'
description: 'user upstage llm powered by the Upstage Solar models'
model_name: 'solar-pro-2'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${UPSTAGE_API_KEY}'
api_base: 'https://api.upstage.ai/v1/solar'
proxy: '${UPSTAGE_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.upstage_llm'
  class: 'UpstageLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/upstage_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'up-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${UPSTAGE_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="upstage"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

Upstage 会持续发布新的 Solar 模型。下表列出了 Solar API 上常用的模型及其上下文窗口大小（输入 + 输出 token）。这些数值同样硬编码在 `UpstageLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。表中数值仅供参考，请以 [Upstage 官方文档](https://developers.upstage.ai) 公布的最新列表和限制为准。

| 模型名称            | 上下文长度        |
| ------------------- | ----------------- |
| `solar-pro-2`       | 65536 (64k)       |
| `solar-pro`         | 65536 (64k)       |
| `solar-mini`        | 65536 (64k)       |
| `solar-docvision`   | 65536 (64k)       |

如果某个模型不在上表中，`UpstageLLM` 会保守地回退到 8192 token。

模型选择建议：

- `solar-pro-2` 是旗舰推理模型，适合作为高强度智能体任务的首选。
- `solar-pro` / `solar-mini` 在能力与延迟、成本之间取得平衡，适合工作流中大批量的路由或分类步骤。
- `solar-docvision` 专为文档理解（OCR / 版面感知抽取）优化，与需要处理扫描件或结构化文档的 agentUniverse 知识库型智能体配合尤为出色。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`UPSTAGE_API_KEY`
可选配置：`UPSTAGE_API_BASE`、`UPSTAGE_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['UPSTAGE_API_KEY'] = 'up-***'
os.environ['UPSTAGE_API_BASE'] = 'https://api.upstage.ai/v1/solar'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
UPSTAGE_API_KEY="up-******"
UPSTAGE_API_BASE="https://api.upstage.ai/v1/solar"
UPSTAGE_PROXY=""
```

---

## 4. Upstage API KEY 获取

1. 登录 [https://console.upstage.ai](https://console.upstage.ai)。
2. 进入 **API Keys** 页面并创建新的密钥。
3. 复制生成的 `up_...` 密钥，并赋值给 `UPSTAGE_API_KEY`。

计费、速率限制与免费额度说明详见 [Upstage 官方文档](https://developers.upstage.ai)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.upstage_llm import UpstageLLM

llm = UpstageLLM(model_name='solar-pro-2')

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

由于 Solar API 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_upstage_llm` 的模板配置（`upstage_llm.yaml.example`），用户将其重命名为 `upstage_llm.yaml` 并配置 `UPSTAGE_API_KEY` 之后即可直接使用。
- Solar 模型在韩语任务上表现尤为突出；如果您的智能体主要服务韩语用户，可以将 Upstage 作为主力 LLM，其他兼容 OpenAI 协议的服务商作为备选。
- `UpstageLLM` 中的上下文长度表仅供参考，可能滞后于最新发布的 Solar 模型。长上下文场景请以 Upstage 官方文档为准，或在 yaml 配置中显式设置 `max_context_length`——该配置始终优先于内置表格。
