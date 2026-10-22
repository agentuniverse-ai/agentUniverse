# SenseNova（日日新）使用

`SenseNovaLLM` 将商汤科技 [SenseNova](https://platform.sensenova.cn)（日日新）的 API 接入 agentUniverse。SenseNova 是商汤 **SenseChat（日日新）** 系列大模型背后的平台，涵盖旗舰对话模型 **SenseChat-5**、低延迟的 **SenseChat-Turbo** 变体以及 **SenseNova-V6-Pro** 世代模型。

SenseNova 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.sensenova.cn/compatible-mode/v1`），因此 `SenseNovaLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 SenseNova 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_sensenova_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_sensenova_llm'
description: 'user sensenova llm powered by the SenseTime SenseNova SenseChat models'
model_name: 'SenseChat-5'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${SENSENOVA_API_KEY}'
api_base: 'https://api.sensenova.cn/compatible-mode/v1'
proxy: '${SENSENOVA_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.sensenova_llm'
  class: 'SenseNovaLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/sensenova_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'sensenova-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${SENSENOVA_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="sensenova"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

商汤会持续发布新的 SenseChat 模型。下表列出了 SenseNova OpenAI 兼容接口常用的模型及其上下文窗口大小（输入 + 输出 token）。这些数值同样硬编码在 `SenseNovaLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称            | 上下文长度        |
| ------------------- | ----------------- |
| `SenseChat-5`       | 131072 (128k)     |
| `SenseChat-Turbo`  | 32768 (32k)       |
| `SenseNova-V6-Pro` | 131072 (128k)     |

上表数值为参考值，请以 [SenseNova 官方文档](https://platform.sensenova.cn) 公布的最新列表为准。如果某个模型不在上表中，`SenseNovaLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`SENSENOVA_API_KEY`
可选配置：`SENSENOVA_API_BASE`、`SENSENOVA_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['SENSENOVA_API_KEY'] = 'sensenova-***'
os.environ['SENSENOVA_API_BASE'] = 'https://api.sensenova.cn/compatible-mode/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
SENSENOVA_API_KEY="sensenova-******"
SENSENOVA_API_BASE="https://api.sensenova.cn/compatible-mode/v1"
SENSENOVA_PROXY=""
```

---

## 4. SenseNova API KEY 获取

1. 登录 [SenseCore 商汤大装置控制台](https://console.sensecore.cn)。
2. 进入 **Model as a Service / 日日新 SenseNova** 板块，在密钥管理页面创建 API 密钥。
3. 复制生成的密钥，并赋值给 `SENSENOVA_API_KEY`。

计费、速率限制与模型目录详见 [SenseNova 平台文档](https://platform.sensenova.cn)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.sensenova_llm import SenseNovaLLM

llm = SenseNovaLLM(model_name='SenseChat-5')

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

由于 SenseNova 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_sensenova_llm` 的模板配置（`sensenova_llm.yaml.example`），用户将其重命名为 `sensenova_llm.yaml` 并配置 `SENSENOVA_API_KEY` 之后即可直接使用。
- `SenseChat-Turbo` 用更小的上下文窗口换取更低延迟，适合高频调用的智能体步骤；`SenseChat-5` 与 `SenseNova-V6-Pro` 提供 128k 上下文窗口，非常适合需要将大量检索文档一次性填入 prompt 的 agentUniverse 知识库型智能体。
- 如果您的账户使用其他区域端点，可通过 `SENSENOVA_API_BASE` 环境变量覆盖，无需修改组件代码。
