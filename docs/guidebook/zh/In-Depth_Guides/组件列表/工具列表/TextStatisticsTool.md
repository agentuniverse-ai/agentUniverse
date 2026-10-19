# TextStatisticsTool

`TextStatisticsTool` 对一段文本进行结构与可读性分析，返回字符数、单词数、句子数、段落数、音节数、各类平均值、阅读时间估算以及复杂度评分。仅依赖 Python 标准库，零第三方依赖。

## 功能特性

- 计数：字符总数、不含空格字符数、字母数、数字数、空白字符数、单词数、唯一单词数（不区分大小写）、句子数、段落数、音节数
- 平均值：每句单词数、每段句子数、每段单词数、每单词音节数、每单词字符数
- 阅读时间估算：基于可配置的阅读速度（默认 200 词/分钟）
- 复杂度评分：Flesch 阅读容易度、Flesch-Kincaid 年级、0-100 难度分数与中文标签（very easy / easy / moderate / difficult / very difficult）
- 支持中英文标点切句（`.` `。` `!` `！` `?` `？`）
- 音节计数采用英文启发式（元音组 + 词尾静音 `e` 处理）
- 最长单词、校验失败均以结构化 `error` 返回

## 使用方式

```python
from agentuniverse.agent.action.tool.common_tool.text_statistics_tool import TextStatisticsTool

tool = TextStatisticsTool()

r = tool.execute(text="Hello world. This is a readability test for the agent.")
print(r["counts"])        # 字符/单词/句子/段落/音节计数
print(r["averages"])      # 每句词数、每段句数等
print(r["reading_time"])  # 例: "0m 3s"
print(r["complexity"])    # flesch_reading_ease / flesch_kincaid_grade / difficulty_score

# 自定义阅读速度
r = tool.execute(text="...", words_per_minute=150)
```

## YAML 配置

```yaml
name: text_statistics_tool
description: Analyze text to compute character/word/sentence/paragraph counts, average lengths, estimated reading time and a readability complexity score. Zero dependencies.
tool_type: api
metadata:
  type: TOOL
  module: agentuniverse.agent.action.tool.common_tool.text_statistics_tool
  class: TextStatisticsTool
input_keys:
  - text
words_per_minute: 200
min_syllables: 1
```

## 参数说明

`execute()` 方法接受以下参数：

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `text` | `str` | - | 待分析文本，最长 1,000,000 字符 |
| `words_per_minute` | `int` | `200` | 阅读速度，范围 1-2000，仅本次调用生效 |

工具字段：`words_per_minute`（阅读速度默认值）、`min_syllables`（每个单词返回的最小音节数，默认 1）。

返回值（`status='success'` 时）：

- `counts`：`characters`、`characters_no_spaces`、`letters`、`digits`、`whitespace`、`words`、`unique_words`、`sentences`、`paragraphs`、`syllables`
- `averages`：`words_per_sentence`、`sentences_per_paragraph`、`words_per_paragraph`、`syllables_per_word`、`chars_per_word`
- `reading_time_seconds`、`reading_time`（形如 `0m 3s`）、`words_per_minute`
- `complexity`：`flesch_reading_ease`、`flesch_kincaid_grade`、`difficulty_score`、`difficulty_label`（空文本时为 `n/a`）
- `longest_word`

失败时返回 `status='error'` 与 `error_type`（`validation_error` / `operation_error`）。

## 算法说明

- 单词切分保留撇号与连字符（`don't`、`well-known` 视为单个词）
- 句子切分支持英文 `.!?` 与中文 `。！？`
- 段落由两个及以上换行分隔
- Flesch 公式：`206.835 - 84.6 × (音节/词) - 1.015 × (词/句)`，结果限制在 0-100
- 难度分数为 `100 - Flesch 容易度`，越高表示越难

## 依赖

仅依赖 Python 标准库（`re`、`math`），无需安装任何第三方包。
