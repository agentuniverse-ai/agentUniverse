# PasswordGeneratorTool

`PasswordGeneratorTool` 使用 Python 标准库的 `secrets` 模块生成密码学安全的随机密码，并评估已有密码的强度。零第三方依赖，适合在智能体工作流中创建或校验凭证。

## 功能特性

- 三种模式：`generate`（单个）、`generate_batch`（批量）、`check_strength`（强度评分）
- 可控字符集：大写字母 `A-Z`、小写字母 `a-z`、数字 `0-9` 以及精选符号集
- 支持 `exclude_similar` 排除易混淆字符（`Il1O0o`、`` ` ``、`'`、`"`、`|`）
- 基于字符池大小和长度的熵估算（bits）
- 生成时保证每个启用的字符类至少出现一个字符，并打乱顺序避免前置聚集
- 强度评分结合熵值与缺失类别给出 0-100 分及评级（very weak / weak / moderate / strong / very strong）
- 校验失败均以结构化 `error` 返回，不会抛出未捕获异常

## 使用方式

```python
from agentuniverse.agent.action.tool.common_tool.password_generator_tool import PasswordGeneratorTool

tool = PasswordGeneratorTool()

# 生成单个 16 位强密码
r = tool.execute(mode="generate")
print(r["password"], r["entropy_bits"], r["score"] if "score" in r else "")

# 批量生成 5 个 24 位、排除易混淆字符的密码
batch = tool.execute(mode="generate_batch", length=24, count=5, exclude_similar=True)
print(batch["passwords"])

# 评估已有密码强度
s = tool.execute(mode="check_strength", password="my-old-pass")
print(s["score"], s["rating"], s["issues"])
```

## YAML 配置

```yaml
name: password_generator_tool
description: Generate cryptographically strong passwords (secrets-based) and check password strength. Zero third-party dependencies.
tool_type: api
metadata:
  type: TOOL
  module: agentuniverse.agent.action.tool.common_tool.password_generator_tool
  class: PasswordGeneratorTool
input_keys:
  - mode
default_length: 16
include_uppercase: true
include_lowercase: true
include_digits: true
include_symbols: true
exclude_similar: false
```

## 参数说明

`execute()` 方法接受以下参数：

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `mode` | `str` | `generate` | 操作模式：`generate` / `generate_batch` / `check_strength` |
| `length` | `int` | `default_length` | 密码长度，范围 4-256（generate / generate_batch） |
| `count` | `int` | `1` | 批量生成数量，范围 1-1000（generate_batch） |
| `password` | `str` | - | 待评分密码（check_strength） |
| `include_uppercase` | `bool` | `True` | 是否包含大写字母 |
| `include_lowercase` | `bool` | `True` | 是否包含小写字母 |
| `include_digits` | `bool` | `True` | 是否包含数字 |
| `include_symbols` | `bool` | `True` | 是否包含符号 |
| `exclude_similar` | `bool` | `False` | 是否排除易混淆字符 |

工具字段：`default_length`、`include_uppercase`、`include_lowercase`、`include_digits`、`include_symbols`、`exclude_similar`。调用时传入的同名参数仅在本次调用生效，不会修改工具默认值。

返回值：`generate` 返回 `password`、`length`、`entropy_bits`、`pool_size`、`composition`；`generate_batch` 返回 `passwords` 列表与 `count`；`check_strength` 返回 `length`、`pool_size`、`entropy_bits`、`score`、`rating`、`issues`。失败时返回 `status='error'` 与 `error_type`（`validation_error` / `operation_error`）。

## 依赖

仅依赖 Python 标准库（`secrets`、`string`、`math`），无需安装任何第三方包。
