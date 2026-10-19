# SiliconFlow 使用

`SiliconFlowLLM` 将 [SiliconFlow](https://siliconflow.cn)（硅基流动）的 API 接入 agentUniverse。SiliconFlow 是国内的**模型聚合云平台**，将第三方开源大模型——DeepSeek（`deepseek-ai/DeepSeek-V3`、`deepseek-ai/DeepSeek-R1`）、阿里 Qwen 系列（`Qwen/Qwen2.5-72B-Instruct` 等）、智谱 GLM 开源权重模型（`THUDM/glm-4-9b-chat`）等——聚合在统一的计费与统一的 API 之后。

SiliconFlow 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.siliconflow.cn/v1`），因此 `SiliconFlowLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 SiliconFlow 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_siliconflow_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_siliconflow_llm'
description: 'user siliconflow llm powered by the models hosted on the SiliconFlow platform'
model_name: 'deepseek-ai/DeepSeek-V3'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${SILICONFLOW_API_KEY}'
api_base: 'https://api.siliconflow.cn/v1'
proxy: '${SILICONFLOW_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.siliconflow_llm'
  class: 'SiliconFlowLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/siliconflow_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'sk-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${SILICONFLOW_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="siliconflow"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

SiliconFlow 的模型目录会频繁更新。下表列出了平台上常见的托管模型及其上下文窗口大小（输入 + 输出 token）。这些数值同样硬编码在 `SiliconFlowLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                          | 上下文长度        |
| --------------------------------- | ----------------- |
| `deepseek-ai/DeepSeek-V3`         | 65536 (64k)       |
| `deepseek-ai/DeepSeek-R1`         | 65536 (64k)       |
| `Qwen/Qwen2.5-72B-Instruct`       | 32768 (32k)       |
| `Qwen/Qwen2.5-7B-Instruct`        | 32768 (32k)       |
| `THUDM/glm-4-9b-chat`             | 131072 (128k)     |

该表仅为**参考值**：数值来自各模型官方文档 / SiliconFlow 模型卡片的保守快照，同一模型的实际窗口可能随部署版本变化。请以 [SiliconFlow 模型广场](https://siliconflow.cn/models) 公布的最新列表为准。如果某个模型不在上表中，`SiliconFlowLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 使用了环境变量占位符的方式，以下为环境变量的设置说明。

必须设置：`SILICONFLOW_API_KEY`
可选设置：`SILICONFLOW_API_BASE`、`SILICONFLOW_PROXY`

### 3.1 通过 Python 代码设置

```python
import os
os.environ['SILICONFLOW_API_KEY'] = 'sk-***'
os.environ['SILICONFLOW_API_BASE'] = 'https://api.siliconflow.cn/v1'
```

### 3.2 通过配置文件设置

在项目 `config` 目录下的 `custom_key.toml` 文件中添加如下配置：

```toml
SILICONFLOW_API_KEY="sk-******"
SILICONFLOW_API_BASE="https://api.siliconflow.cn/v1"
SILICONFLOW_PROXY=""
```

---

## 4. 获取 SiliconFlow API KEY

1. 登录 [https://cloud.siliconflow.cn](https://cloud.siliconflow.cn)。
2. 进入左侧菜单 **API 密钥**，新建一个密钥。
3. 复制生成的 `sk-...` 密钥并赋值给 `SILICONFLOW_API_KEY`。

计费、限流以及免费模型说明详见 [https://docs.siliconflow.cn](https://docs.siliconflow.cn)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，你可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.siliconflow_llm import SiliconFlowLLM

llm = SiliconFlowLLM(model_name='deepseek-ai/DeepSeek-V3')

# 非流式
output = llm.call(messages=[{"role": "user", "content": "Hello!"}])
print(output.text)

# 流式
for chunk in llm.call(messages=[{"role": "user", "content": "Count 1 to 5."}], streaming=True):
    print(chunk.text, end='')

# 异步
import asyncio
async def main():
    out = await llm.acall(messages=[{"role": "user", "content": "Hello!"}])
    print(out.text)
asyncio.run(main())
```

由于 SiliconFlow 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力——工具调用、LangChain 集成、链路追踪——均无需额外开发即可使用。

---

## 6. 使用建议

- agentUniverse 内置了名为 `default_siliconflow_llm` 的模板（见 `siliconflow_llm.yaml.example`）。配置好 `SILICONFLOW_API_KEY` 环境变量后，将其重命名为 `siliconflow_llm.yaml` 即可直接在智能体中引用。
- SiliconFlow 的模型 ID 按**上游厂商命名空间**组织（`deepseek-ai/...`、`Qwen/...`、`THUDM/...`），传入 `model_name` 时请务必带上命名空间的完整 ID。
- 许多热门模型提供 `:free` 或量化变体（如 `Qwen/Qwen2.5-7B-Instruct:free`），它们不在上下文长度表中，会安全地回退到保守的 8192 默认值；也可以在 yaml 中显式设置 `max_context_length`。
- `deepseek-ai/DeepSeek-R1` 是推理模型：回答中可能先输出思维链再给出最终答案，思维链会作为消息内容的一部分返回。
- 使用一个 SiliconFlow API 密钥即可访问整个聚合模型目录，只需切换 `model_name` 就可以方便地对比 DeepSeek / Qwen / GLM 的效果。
