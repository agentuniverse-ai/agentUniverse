# 腾讯混元使用

`HunyuanLLM` 将 [腾讯混元](https://hunyuan.tencent.com) 的 API 接入 agentUniverse。混元是腾讯的全链路自研大模型系列，涵盖深度思考推理模型（T1 系列）、快思考旗舰模型（TurboS 系列）、Hy3 代 MoE 混合专家模型（总参数 295B / 激活 21B）以及 hunyuan-lite / hunyuan-standard / hunyuan-large 等长生命周期模型。

混元提供了完全 **兼容 OpenAI** 的 Chat Completions API（地址为 `https://api.hunyuan.cloud.tencent.com/v1`），因此 `HunyuanLLM` 组件只需继承 `OpenAIStyleLLM`，并在其基础上配置混元的鉴权信息、API 基础地址以及各模型的上下文长度表即可。流式输出、工具调用、异步接口以及 LangChain 桥接等能力均可直接复用，无需额外开发。

---

## 1. 创建相关文件

创建一个 yaml 文件，例如 `user_hunyuan_llm.yaml`，将以下内容粘贴进去：

```yaml
name: 'user_hunyuan_llm'
description: 'user hunyuan llm powered by the Tencent Hunyuan models'
model_name: 'hunyuan-turbos-latest'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${HUNYUAN_API_KEY}'
api_base: 'https://api.hunyuan.cloud.tencent.com/v1'
proxy: '${HUNYUAN_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.hunyuan_llm'
  class: 'HunyuanLLM'
```

源码目录中同时附带了一个开箱即用的模板 `agentuniverse/llm/default/hunyuan_llm.yaml.example`。

**note:** `api_key` / `api_base` / `proxy` 等模型参数有三种配置方法：

1. **直接字符串值**：直接在配置文件中输入 API 密钥字符串。

    ```yaml
    api_key: 'hunyuan-***'
    ```

2. **环境变量占位符**：使用 `${VARIABLE_NAME}` 语法从环境变量中加载。当 agentUniverse 启动时，会自动从环境变量读取相应的值。

    ```yaml
    api_key: '${HUNYUAN_API_KEY}'
    ```

3. **自定义函数加载**：使用 `@FUNC` 注解在运行时通过自定义函数动态加载 API 密钥。

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="hunyuan"))'
    ```

    该函数需要在 `yaml_func_extension.py` 文件的 `YamlFuncExtension` 类中定义，可参考样例工程中的 [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py)。当 agentUniverse 加载此配置时：
    - 解析 `@FUNC` 注解
    - 执行 `load_api_key` 函数并传入相应参数
    - 用函数返回值替换注解内容

---

## 2. 选择模型

腾讯会持续发布新的混元模型。下表列出了混元 OpenAI 兼容 API 上常用的模型及其上下文窗口大小（输入 + 输出 token）。这些数值同样硬编码在 `HunyuanLLM.max_context_length` 中，这样 agentUniverse 即使不发起真实请求也能正确估算 prompt 预算。

| 模型名称                        | 上下文长度        |
| ------------------------------- | ----------------- |
| `hunyuan-t1`                    | 32768 (32k)       |
| `hunyuan-t1-latest`             | 32768 (32k)       |
| `hunyuan-turbos`                | 32768 (32k)       |
| `hunyuan-turbos-latest`         | 262144 (256k)     |
| `hunyuan-turbos-20250630`       | 262144 (256k)     |
| `hy3`                           | 262144 (256k)     |
| `hunyuan-a13b`                  | 262144 (256k)     |
| `hunyuan-lite`                  | 262144 (256k)     |
| `hunyuan-standard`              | 32768 (32k)       |
| `hunyuan-standard-256K`         | 262144 (256k)     |
| `hunyuan-large`                 | 32768 (32k)       |
| `hunyuan-large-longcontext`     | 262144 (256k)     |

`HunyuanLLM` 对模型名称的大小写不敏感（因此文档中的 `hunyuan-standard-256K` 大写写法同样可以解析），并会自动将不在表中的 `-latest` 后缀解析为基础模型的上下文窗口。

请以 [腾讯云混元官方文档](https://cloud.tencent.com/document/product/1729) 公布的最新列表为准。如果某个模型不在上表中，`HunyuanLLM` 会保守地回退到 32768 token。

---

## 3. 环境设置

示例 yaml 中模型密钥等参数使用了环境变量占位符，下面介绍环境变量的设置方法。

必须配置：`HUNYUAN_API_KEY`
可选配置：`HUNYUAN_API_BASE`、`HUNYUAN_PROXY`

### 3.1 通过 Python 代码配置

```python
import os
os.environ['HUNYUAN_API_KEY'] = 'hunyuan-***'
os.environ['HUNYUAN_API_BASE'] = 'https://api.hunyuan.cloud.tencent.com/v1'
```

### 3.2 通过配置文件配置

在项目的 `config` 目录下的 `custom_key.toml` 当中，添加配置：

```toml
HUNYUAN_API_KEY="hunyuan-******"
HUNYUAN_API_BASE="https://api.hunyuan.cloud.tencent.com/v1"
HUNYUAN_PROXY=""
```

海外用户可以将 `HUNYUAN_API_BASE` 指向国际版 TokenHub 网关，例如 `https://tokenhub-intl.tencentcloudmaas.com/v1`。

---

## 4. 混元 API KEY 获取

1. 登录腾讯云控制台 [https://console.cloud.tencent.com/hunyuan](https://console.cloud.tencent.com/hunyuan)。
2. 进入 **API Key 管理** 页面并创建新的密钥。
3. 复制生成的密钥，并赋值给 `HUNYUAN_API_KEY`。

计费、速率限制与免费额度说明详见 [腾讯云混元文档](https://cloud.tencent.com/document/product/1729)。

---

## 5. 在代码中使用

配置被 agentUniverse 加载后，您可以直接获取 LLM 实例并调用：

```python
from agentuniverse.llm.default.hunyuan_llm import HunyuanLLM

llm = HunyuanLLM(model_name='hunyuan-turbos-latest')

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

由于混元兼容 OpenAI 协议，`OpenAIStyleLLM` 支持的所有能力（工具调用、LangChain 集成、链路追踪等）都可以直接使用。

---

## 6. Tips

- agentuniverse 源码中内置了一个 name 为 `default_hunyuan_llm` 的模板配置（`hunyuan_llm.yaml.example`），用户将其重命名为 `hunyuan_llm.yaml` 并配置 `HUNYUAN_API_KEY` 之后即可直接使用。
- `hunyuan-turbos-latest` 是快思考旗舰模型，适合作为智能体工作负载的默认选择；需要深度推理时可选用 `hunyuan-t1-latest`，新一代 MoE 模型可选择 `hy3` / `hunyuan-a13b`。
- `-latest` / `-256K` 系列提供 256K token 的上下文窗口，非常适合需要将大量检索文档一次性填入 prompt 的 agentUniverse 知识库型智能体。
