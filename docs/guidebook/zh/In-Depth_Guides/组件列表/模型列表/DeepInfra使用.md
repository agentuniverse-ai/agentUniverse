# DeepInfra使用

`DeepInfraLLM` 将 [DeepInfra](https://deepinfra.com) 的 API 接入 agentUniverse。DeepInfra 是一个无服务器推理平台，托管了大量开源权重的大模型（Llama、Qwen、DeepSeek、Mistral、Gemma 等），并通过统一的按 token 计费 API 提供服务，只需修改一行配置即可在 `meta-llama/Meta-Llama-3.1-405B-Instruct` 与 `deepseek-ai/DeepSeek-V3` 等模型之间自由切换。

DeepInfra 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.deepinfra.com/v1/openai`），因此 `DeepInfraLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 DeepInfra 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_deepinfra_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_deepinfra_llm'
description: 'user deepinfra llm powered by the open-weight models hosted on DeepInfra'
model_name: 'meta-llama/Meta-Llama-3.1-405B-Instruct'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${DEEPINFRA_API_KEY}'
api_base: 'https://api.deepinfra.com/v1/openai'
proxy: '${DEEPINFRA_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.deepinfra_llm'
  class: 'DeepInfraLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/deepinfra_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'deepinfra-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${DEEPINFRA_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="deepinfra"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

DeepInfra 的模型目录会持续更新。下表列出了部分热门模型及其上下文窗口大小（输入 + 输出 token），数值来自各模型发布方公布的规格，**仅供参考**。这些数值同样硬编码在 `DeepInfraLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                                      | 上下文长度         |
| --------------------------------------------- | ------------------ |
| `meta-llama/Meta-Llama-3.1-405B-Instruct`     | 131072 (128k)      |
| `meta-llama/Meta-Llama-3.1-70B-Instruct`      | 131072 (128k)      |
| `meta-llama/Meta-Llama-3.1-8B-Instruct`       | 131072 (128k)      |
| `Qwen/Qwen2.5-72B-Instruct`                   | 32768 (32k)        |
| `deepseek-ai/DeepSeek-V3`                     | 65536 (64k)        |

DeepInfra 使用 `组织/模型` 的形式标识模型（例如 `Qwen/Qwen2.5-72B-Instruct`），完整的模型目录与实时价格见 [DeepInfra 模型页面](https://deepinfra.com/models)。如果某个模型不在上表中，`DeepInfraLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`DEEPINFRA_API_KEY`
可选配置：`DEEPINFRA_API_BASE`、`DEEPINFRA_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['DEEPINFRA_API_KEY'] = 'deepinfra-***'
os.environ['DEEPINFRA_API_BASE'] = 'https://api.deepinfra.com/v1/openai'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
DEEPINFRA_API_KEY="deepinfra-******"
DEEPINFRA_API_BASE="https://api.deepinfra.com/v1/openai"
DEEPINFRA_PROXY=""
```

---

## 4. DeepInfra API KEY 获取

1. 登录 [https://deepinfra.com/dashboard/settings](https://deepinfra.com/dashboard/settings)。
2. 在 **API Keys** 区域创建新的密钥。
3. 复制生成的密钥，并赋值给 `DEEPINFRA_API_KEY`。

计费、速率限制与托管模型目录详见 [DeepInfra 官网](https://deepinfra.com)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.deepinfra_llm import DeepInfraLLM

llm = DeepInfraLLM(model_name='meta-llama/Meta-Llama-3.1-405B-Instruct')

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

由于 DeepInfra 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_deepinfra_llm` 的模板配置（`deepinfra_llm.yaml.example`），用户将其重命名为 `deepinfra_llm.yaml` 并配置 `DEEPINFRA_API_KEY` 之后即可直接使用。
- 组件中的上下文长度表**仅供参考**：DeepInfra 托管的是第三方开源权重模型，实际窗口大小由模型发布方决定，精确预算 prompt 时请以 DeepInfra 模型页面为准，或在 yaml 中显式设置 `max_context_length`。
- Llama 3.1 系列提供 128k token 的上下文窗口，非常适合需要将大量检索文档一次性填入 prompt 的 agentUniverse 知识库型智能体；而 `meta-llama/Meta-Llama-3.1-8B-Instruct` 延迟与成本更低，适合高频工具调用场景。
