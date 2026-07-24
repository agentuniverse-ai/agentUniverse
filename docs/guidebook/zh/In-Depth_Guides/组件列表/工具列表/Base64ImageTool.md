# Base64ImageTool

`Base64ImageTool` 提供图片与 base64 之间的转换：将图片文件编码为 base64（可选 `data:` URI 形式）、将 base64 解码为图片文件、以及从 base64 读取图片元信息。仅依赖 Python 标准库（`base64`），`info` 操作的尺寸/格式识别会懒加载 Pillow。

## 功能特性

- 三种模式：`encode`（图片→base64）、`decode`（base64→图片）、`info`（base64→元信息）
- `encode` 可选 `as_data_uri` 输出完整的 `data:image/png;base64,...` URI
- `decode` 支持 base64 字符串或 `data:` URI 形式的输入
- `info` 返回解码后字节大小；若安装 Pillow 还会返回 `format`、`width`、`height`
- 所有文件路径经 `resolve_safe_path` 限制在 `base_dir` 下，防止路径穿越
- 写入采用原子替换，未设置 `overwrite=true` 时不覆盖已有文件
- 支持 png / jpg / jpeg / gif / bmp / webp / tiff / ico / svg 等常见扩展名
- 校验失败均以结构化 `error` 返回

## 使用方式

```python
from agentuniverse.agent.action.tool.common_tool.base64_image_tool import Base64ImageTool

tool = Base64ImageTool(base_dir="/srv/agent-images")

# 编码为 base64
r = tool.execute(mode="encode", file_path="logo.png")
print(r["base64"], r["mime_type"])

# 编码为 data URI（可直接嵌入 HTML/JSON）
r = tool.execute(mode="encode", file_path="logo.png", as_data_uri=True)
print(r["data_uri"])

# 解码为图片文件
tool.execute(mode="decode", data=r["base64"], output_path="copy.png")

# 读取 base64 图片元信息（需要 Pillow 才能拿到宽高/格式）
r = tool.execute(mode="info", data=r["base64"])
print(r["size"], r.get("width"), r.get("height"), r.get("format"))
```

## YAML 配置

```yaml
name: base64_image_tool
description: Encode image files to base64 (optionally as data URIs), decode base64 back to image files, and inspect base64 image metadata. All paths are sandboxed under base_dir.
tool_type: api
metadata:
  type: TOOL
  module: agentuniverse.agent.action.tool.common_tool.base64_image_tool
  class: Base64ImageTool
input_keys:
  - mode
base_dir: .
max_read_bytes: 26214400
max_write_bytes: 52428800
```

## 参数说明

`execute()` 方法接受以下参数：

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `mode` | `str` | - | 操作模式：`encode` / `decode` / `info` |
| `file_path` | `str` | - | 待编码图片路径（encode） |
| `data` | `str` | - | base64 字符串或 data URI（decode / info） |
| `output_path` | `str` | - | 输出图片路径（decode） |
| `as_data_uri` | `bool` | `False` | encode 时是否输出 data URI |
| `overwrite` | `bool` | `False` | decode 时是否覆盖已有文件 |

工具字段：`base_dir`（工作根目录）、`max_read_bytes`（单文件读取上限，默认 25MB）、`max_write_bytes`（单次写入上限，默认 50MB）。

返回值：

- `encode`：`base64`、`data_uri`（`as_data_uri=True` 时）、`mime_type`、`size`、`file_path`
- `decode`：`output_path`、`size`、`mime_type`
- `info`：`size`、`format`、`width`、`height`（后三项需 Pillow；未安装时 `info` 中含 `note` 说明）

失败时返回 `status='error'` 与 `error_type`（`validation_error` / `operation_error`）。

## 安全说明

- 所有路径限制在 `base_dir` 内，拒绝 `../` 路径穿越与绝对路径越界
- 仅接受图片扩展名，非图片扩展名会返回校验错误
- 解码写入使用临时文件 + 原子 `os.replace`，崩溃不会产生半成品
- 默认不覆盖已有文件，需显式 `overwrite=true`

## 依赖

核心功能仅依赖 Python 标准库（`base64`、`mimetypes`、`os`、`tempfile`）。`info` 操作获取宽高/格式需要 Pillow（`pip install Pillow`）；未安装时 `info` 仍返回字节大小并附带提示。
