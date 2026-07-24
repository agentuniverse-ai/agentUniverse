# MarkdownTableExtractorTool

`MarkdownTableExtractorTool` 从 Markdown 文本中提取 GFM 风格的表格并转为结构化数据，支持 CSV、JSON 输出。仅使用 Python 标准库（`re`、`csv`、`json`），零第三方依赖。

## 功能特性

- 四种模式：`extract`（全部表格）、`extract_first`（首个表格）、`to_csv`（CSV 字符串）、`to_json`（JSON 对象列表）
- 解析遵循 GitHub Flavored Markdown 表格语法：表头行 + 分隔行（`---`、`:--`、`--:`、`:--:`）+ 数据行
- 支持有/无首尾管道符 `|` 的写法
- 支持单元格内转义管道符 `\|`
- 自动保留空单元格；分隔行缺少连字符会被识别为非表格
- `to_csv` / `to_json` 可通过 `table_index` 只处理指定表格
- 校验失败均以结构化 `error` 返回，不会抛出未捕获异常

## 使用方式

```python
from agentuniverse.agent.action.tool.common_tool.markdown_table_extractor_tool import MarkdownTableExtractorTool

tool = MarkdownTableExtractorTool()

md = """
# 报告

| 姓名 | 年龄 | 城市 |
|------|-----|------|
| Alice | 30 | Beijing |
| Bob | 25 | Shanghai |
"""

# 提取所有表格
r = tool.execute(text=md, mode="extract")
print(r["table_count"], r["tables"][0]["header"], r["tables"][0]["rows"])

# 只要第一个表格
r = tool.execute(text=md, mode="extract_first")
print(r["table"])

# 转 CSV
r = tool.execute(text=md, mode="to_csv")
print(r["csv"])

# 转 JSON（每行变成一个对象）
r = tool.execute(text=md, mode="to_json")
print(r["json"])
```

## YAML 配置

```yaml
name: markdown_table_extractor_tool
description: Extract Markdown tables into structured data and convert them to CSV or JSON. Pure-Python regex parsing, zero dependencies.
tool_type: api
metadata:
  type: TOOL
  module: agentuniverse.agent.action.tool.common_tool.markdown_table_extractor_tool
  class: MarkdownTableExtractorTool
input_keys:
  - text
```

## 参数说明

`execute()` 方法接受以下参数：

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `text` | `str` | - | Markdown 文本，最长 2,000,000 字符 |
| `mode` | `str` | `extract` | `extract` / `extract_first` / `to_csv` / `to_json` |
| `table_index` | `int` | - | `to_csv` / `to_json` 时指定表格下标（从 0 开始） |

返回值：

- `extract`：`table_count` 与 `tables`（每个含 `header`、`rows`、`row_count`、`column_count`、`start_line`）
- `extract_first`：`table`（无表格时为 `null`）与 `table_count`
- `to_csv`：`csv` 字符串（多表以空行分隔）；无表格时为 `""`
- `to_json`：`json` 字符串（数据行转为以表头为键的对象列表）；无表格时为 `"[]"`

失败时返回 `status='error'` 与 `error_type`（`validation_error` / `operation_error`）。

## 解析规则说明

- 表头行与数据行必须满足「两端被管道符包围」或「至少包含一个管道符」
- 分隔行的每个单元格必须至少含两个连字符 `--`，可带冒号表示对齐
- 仅含冒号/竖线而无连字符的行不会被识别为分隔行
- 表格之间会被普通文本自然分隔

## 依赖

仅依赖 Python 标准库（`re`、`csv`、`json`、`io`），无需安装任何第三方包。
