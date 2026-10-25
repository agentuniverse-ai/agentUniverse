# Perplexity（Sonar）使用

`PerplexityLLM` 将 [Perplexity](https://www.perplexity.ai) 的 API 接入 agentUniverse。Perplexity 是 **Sonar** 系列在线大模型背后的公司，其模型将大语言模型与实时联网搜索相结合，返回附带引用来源的有据可依的回答，涵盖轻量快速的 `sonar`、长上下文的 `sonar-pro`、具备思维链能力的 `sonar-reasoning` / `sonar-reasoning-pro` 以及多步深度研究模型 `sonar-deep-research`。

Perplexity 提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.perplexity.ai`），因此 `PerplexityLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置 Perplexity 的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_perplexity_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_perplexity_llm'
description: 'user perplexity llm powered by the Perplexity Sonar models'
model_name: 'sonar'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${PERPLEXITY_API_KEY}'
api_base: 'https://api.perplexity.ai'
proxy: '${PERPLEXITY_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.perplexity_llm'
  class: 'PerplexityLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/perplexity_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'pplx-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${PERPLEXITY_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="sonar"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

Perplexity 会持续发布新的 Sonar 模型。下表列出了 Perplexity API 当前提供的模型及其参考上下文窗口大小（输入 + 输出 token）。这些数值同样硬编码在 `PerplexityLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称               | 参考上下文长度       |
| ---------------------- | -------------------- |
| `sonar`                | 127072               |
| `sonar-pro`            | ~200000 (200k)       |
| `sonar-reasoning`      | 127072               |
| `sonar-reasoning-pro`  | ~128000 (128k)       |
| `sonar-deep-research`  | 127072               |

**注意：** Perplexity 官方文档为 sonar 系列标注了 127072 token 的在线上下文，并将限制描述为 sonar / sonar-pro 约 200k、sonar-reasoning-pro 约 128k。由于实际可用窗口取决于请求时注入的联网搜索上下文数量，上表仅为**参考值**，请将其视为 prompt 预算估算的辅助依据而非硬性保证。

Perplexity 为各模型同时提供离线版与 `<模型名>-online` 联网版本。`PerplexityLLM` 会自动将 `-online` 后缀（例如 `sonar-online`）解析为基础模型的上下文窗口。

请以 [Perplexity 官方模型文档](https://docs.perplexity.ai/guides/getting-started) 公布的最新列表为准。如果某个模型不在上表中，`PerplexityLLM` 会保守地回退到 8192 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`PERPLEXITY_API_KEY`
可选配置：`PERPLEXITY_API_BASE`、`PERPLEXITY_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['PERPLEXITY_API_KEY'] = 'pplx-***'
os.environ['PERPLEXITY_API_BASE'] = 'https://api.perplexity.ai'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
PERPLEXITY_API_KEY="pplx-******"
PERPLEXITY_API_BASE="https://api.perplexity.ai"
PERPLEXITY_PROXY=""
```

---

## 4. PERPLEXITY API KEY 获取

1. 登录 [https://www.perplexity.ai](https://www.perplexity.ai)。
2. 进入 **Settings -> API** 页面并生成新的 API 密钥。
3. 复制生成的 `pplx-...` 密钥，并赋值给 `PERPLEXITY_API_KEY`。

计费、速率限制与免费额度说明详见 [Perplexity 官方文档](https://docs.perplexity.ai)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.perplexity_llm import PerplexityLLM

llm = PerplexityLLM(model_name='sonar')

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

由于 Perplexity 兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_perplexity_llm` 的模板配置（`perplexity_llm.yaml.example`），用户将其重命名为 `perplexity_llm.yaml` 并配置 `PERPLEXITY_API_KEY` 之后即可直接使用。
- Sonar 的回答基于实时联网搜索结果，原始响应中带有 `citations` 引用列表（可通过 `output.raw` 获取）；当新鲜事实比私有语料更重要时，可以将该模型与 agentUniverse 知识库型智能体配合使用。
- `sonar` 是成本最低、速度最快的入门选择；`sonar-pro` 支持更长的 prompt 与更充分的搜索；`sonar-reasoning` 系列会输出思维链；`sonar-deep-research` 执行穷举式多步检索，相应地延迟与费用也更高。
