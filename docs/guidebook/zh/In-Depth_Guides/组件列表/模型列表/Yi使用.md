# Yi（零一万物）模型使用

`YiLLM` 将 [01.AI（零一万物）](https://www.01.ai) 的 **Yi** 系列基础大语言模型接入 agentUniverse。Yi 系列（Yi-Large、Yi-Medium、Yi-Small、Yi-Vision 等）由李开复创办的 01.AI 公司研发。

01.AI 提供完全 **OpenAI 兼容** 的 Chat Completions API，地址为 `https://api.01.ai/v1`，因此 `YiLLM` 组件只需继承 `OpenAIStyleLLM`，配置好 01.AI 的凭证、API 地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接均可直接使用。

---

## 1. 创建配置文件

新建一个 YAML 文件，例如 `user_yi_llm.yaml`，填入以下内容。

```yaml
name: 'user_yi_llm'
description: 'user yi llm powered by 01.AI Yi series models'
model_name: 'yi-large'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${YI_API_KEY}'
api_base: 'https://api.01.ai/v1'
organization: '${YI_ORGANIZATION}'
proxy: '${YI_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.yi_llm'
  class: 'YiLLM'
```

**说明：** `api_key`、`api_base`、`organization`、`proxy` 等模型参数支持三种配置方式：

1. **直接填写字符串** —— 在配置文件中直接写入 API Key。

    ```yaml
    api_key: 'your-yi-key'
    ```

2. **环境变量占位符** —— 使用 `${VARIABLE_NAME}` 语法从环境变量读取，agentUniverse 启动时会自动读取对应值。

    ```yaml
    api_key: '${YI_API_KEY}'
    ```

3. **自定义函数加载** —— 使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API Key。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="yi"))'
    ```

    该函数需定义在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中，可参考示例项目中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。agentUniverse 加载配置时会解析 `@FUNC` 注解，使用传入参数执行 `load_api_key` 函数，并用返回值替换注解。

---

## 2. 选择模型

01.AI 提供多个 Yi 模型。下表列出常用模型及其上下文窗口（输入 + 输出 token）。相同的值已硬编码在 `YiLLM.max_context_length` 中，因此 agentUniverse 即使不发起真实 API 调用也能正确预估 prompt 预算。

| 模型名称              | 上下文长度     |
| --------------------- | -------------- |
| `yi-large`            | 32768 (32k)    |
| `yi-large-turbo`      | 32768 (32k)    |
| `yi-large-rag`        | 32768 (32k)    |
| `yi-medium`           | 16384 (16k)    |
| `yi-medium-200k`      | 204800 (200k)  |
| `yi-small`            | 16384 (16k)    |
| `yi-spark`            | 16384 (16k)    |
| `yi-vision`           | 16384 (16k)    |
| `yi-vision-plus`      | 16384 (16k)    |

请以 [01.AI 平台文档](https://platform.lingyiwanhu.com) 上的最新列表为准。若使用的模型不在上表中，`YiLLM` 会回退到默认的 16384 token。

---

## 3. 环境配置

示例 YAML 使用了环境变量占位符，以下说明如何设置这些变量。

必填：`YI_API_KEY`
选填：`YI_API_BASE`、`YI_PROXY`、`YI_ORGANIZATION`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['YI_API_KEY'] = 'your-yi-key'
os.environ['YI_API_BASE'] = 'https://api.01.ai/v1'
```

### 3.2 通过配置文件配置

在项目 `config` 目录下的 `custom_key.toml` 文件中加入以下内容：

```toml
YI_API_KEY="your-yi-key"
YI_API_BASE="https://api.01.ai/v1"
YI_ORGANIZATION=""
YI_PROXY=""
```

---

## 4. 获取 01.AI API Key

1. 登录 [https://platform.lingyiwanhu.com](https://platform.lingyiwanhu.com)。
2. 进入 **API Key** 管理页面，创建新的 Key。
3. 复制生成的 Key，赋值给 `YI_API_KEY`。

计费、限流及免费额度说明请参见 01.AI 平台。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，即可获取 LLM 实例并直接调用：

```python
from agentuniverse.llm.default.yi_llm import YiLLM

llm = YiLLM(model_name='yi-large')

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

由于 01.AI 与 OpenAI 完全兼容，`OpenAIStyleLLM` 支持的所有特性（工具调用、LangChain 集成、链路追踪）均可直接使用，无需额外开发。

---

## 6. 使用建议

- agentUniverse 内置了名为 `default_yi_llm` 的实例模板（见 `yi_llm.yaml.example`），配置好 `YI_API_KEY` 环境变量后即可在 Agent 中直接引用。
- `yi-large` 为旗舰模型，适合复杂推理；`yi-medium`/`yi-small` 速度更快、成本更低，适合简单任务。
- 涉及多模态（图文）输入时，请使用 `yi-vision` 或 `yi-vision-plus`。
