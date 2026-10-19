# Together 使用

`TogetherLLM` 将 [Together AI](https://www.together.ai) 托管推理平台接入 agentUniverse。Together AI 提供了 **200+ 开源大模型** 的统一托管服务，涵盖 Meta Llama、Mistral/Mixtral、Qwen、DeepSeek、DBRX、Falcon 等，并对外暴露完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.together.xyz/v1`）。

由于 API 兼容 OpenAI 协议，`TogetherLLM` 组件只需继承 `OpenAIStyleLLM`，并配置 Together 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具/函数调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_together_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_together_llm'
description: 'user together llm hosted on the Together AI platform'
model_name: 'meta-llama/Llama-3.3-70B-Instruct-Turbo'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${TOGETHER_API_KEY}'
api_base: 'https://api.together.xyz/v1'
organization: '${TOGETHER_ORGANIZATION}'
proxy: '${TOGETHER_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.together_llm'
  class: 'TogetherLLM'
```

**note:** `api_key` / `api_base` / `organization` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'a1b2c3***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${TOGETHER_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="together"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

Together AI 的模型列表会持续更新。下表列出了常用模型及其上下文窗口大小（输入 + 输出 token）。这些数值同样硬编码在 `TogetherLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                                               | 上下文长度      |
| ----------------------------------------------------- | --------------- |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo`             | 131072 (128k)   |
| `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`         | 131072 (128k)   |
| `meta-llama/Meta-Llama-3-70B-Instruct-Lite`           | 8192            |
| `mistralai/Mixtral-8x7B-Instruct-v0.1`                | 32768           |
| `mistralai/Mistral-7B-Instruct-v0.2`                  | 32768           |
| `mistralai/Mistral-Large-Instruct-2411`               | 131072          |
| `Qwen/Qwen2.5-72B-Instruct-Turbo`                     | 131072          |
| `Qwen/Qwen1.5-72B-Chat`                               | 32768           |
| `deepseek-ai/DeepSeek-V3`                             | 131072          |
| `deepseek-ai/DeepSeek-R1`                             | 131072          |
| `databricks/dbrx-instruct`                            | 32768           |

请以 [Together AI 官方模型文档](https://docs.together.ai/docs/inference-models) 公布的最新列表为准。如果某个模型不在上表中，`TogetherLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`TOGETHER_API_KEY`
可选配置：`TOGETHER_API_BASE`、`TOGETHER_PROXY`、`TOGETHER_ORGANIZATION`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['TOGETHER_API_KEY'] = 'a1b2c3***'
os.environ['TOGETHER_API_BASE'] = 'https://api.together.xyz/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
TOGETHER_API_KEY="a1b2c3******"
TOGETHER_API_BASE="https://api.together.xyz/v1"
TOGETHER_ORGANIZATION=""
TOGETHER_PROXY=""
```

---

## 4. TOGETHER API KEY 获取

1. 登录 [https://api.together.ai](https://api.together.ai)。
2. 进入 **Settings** -> **API Keys**，点击 **Create API Key**。
3. 复制生成的密钥（例如 `a1b2c3...`），并赋值给 `TOGETHER_API_KEY`。

新账号注册后会赠送一定免费额度，各模型的具体计费详见 [https://www.together.ai/pricing](https://www.together.ai/pricing)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.together_llm import TogetherLLM

llm = TogetherLLM(model_name='meta-llama/Llama-3.3-70B-Instruct-Turbo')

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

由于 Together AI 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 已经内置了一个 name 为 `default_together_llm` 的 llm，用户在配置 `TOGETHER_API_KEY` 之后可以直接使用。
- Together AI 最大的特点是模型覆盖广：一把 API 密钥即可访问数百个开源模型，方便在不改动集成代码的前提下对不同模型家族进行 A/B 测试。
- 模型的可用性和命名会随时间变化，在正式选型前请先到 [Together AI 模型页面](https://docs.together.ai/docs/inference-models) 确认可用模型及废弃公告。
