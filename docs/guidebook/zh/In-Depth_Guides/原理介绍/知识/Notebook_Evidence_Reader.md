# Notebook 证据读取

`NotebookEvidenceReader` 将本地 `.ipynb` 的单元格源码与明确选择的缓存输出拆成独立 Document。适合实验记录的检索与引用，不把旧输出冒充重新运行后的结果。组件不启动内核、不渲染 HTML、不访问链接，也不提取附件。

这是可选 Reader，不是 Notebook lint 或执行服务，不修改默认扩展名路由。

```sh
pip install 'agentUniverse[notebook_ext]'
```

```python
from agentuniverse.agent.action.knowledge.reader.file.notebook_evidence_reader import NotebookEvidenceReader

reader = NotebookEvidenceReader()  # 默认只读取源码
docs, report = reader.load_notebook(
    "experiment.ipynb", notebook_id="research/project-a/experiment-7"
)
print(report["omitted_outputs"])

# 显式选择缓存文本；仍会标记为“未验证”，不意味着正确/新鲜。
with_outputs = NotebookEvidenceReader(include_text_outputs=True)
docs = with_outputs.load_data("experiment.ipynb")
```

将组件目录中的 `notebook_evidence_reader.yaml.example` 复制到应用配置的 Reader 包下，改为 `.yaml`，保留 metadata 的模块/类配置。在 Knowledge 配置中添加：

```yaml
readers:
  ipynb: notebook_evidence_reader
```

随后正常调用 `knowledge.insert_knowledge(source_path="experiment.ipynb")` 与 `query_knowledge(...)`。测试覆盖真实 YAML 注册、Knowledge 入库和 SQLite 查询，不调用模型。

## 行为边界

- 支持 nbformat 4.0–4.5，复用 nbformat 校验。其他版本直接拒绝，不升级/修复文件；4.5 的缺失、非法或重复 cell ID 在校验前拒绝，避免库自动修复污染证据。
- 每个单元格生成一条源码 Document，包括空单元格和 raw 单元格。源文本保持原内容，字符串数组直接连接。保持文件顺序，不把 execution_count 当作时间顺序或成功证明。
- `include_text_outputs` 默认关闭。开启后读取 stream 和 `text/plain`；不会将 HTML 图片或 JSON bundle 随意转换成文本。`include_error_outputs` 单独控制错误名称、值和 traceback，默认关闭。
- 输出与源码分开；输出正文有未验证缓存提示，并通过 `source_document_id` 关联源码。文件中即使声明 trusted，也不会变成已验证；缓存与源码可能来自不同运行。输出可能含私密内容，开启选项不等于脱敏；traceback 中的终端控制字符不会清洗。
- 记录文件 SHA-256、namespace、cell ID/序号、JSON pointer、源码/输出类型、执行编号、语言和文本摘要；不导出任意 Notebook metadata。保留附件名称与可用 MIME 类型，但不提取其内容。`report` 列出被省略的输出及原因。
- Document ID 包含命名空间、**原始文件摘要**与单元格/输出定位。相同快照重复读取稳定；任意文件字节变化都会产生新快照。显式 `notebook_id` 可让异地的相同副本获得相同 ID，默认使用绝对文件 URI。旧版本无 cell ID 时用位置标识，不生成伪稳定 ID。旧快照清理由调用方管理，本组件不删除或同步 Store。

## 资源限制

默认文件上限 20 MB、5000 个单元格、10000 个输出（含未选择输出）；每个源单元格/被选择输出 20 万字符，总文本含提示语 200 万字符。YAML/Python 均可配置，严格校验类型及上限，详见[英文完整参数表](../../../../en/In-Depth_Guides/Tutorials/Knowledge/Notebook_Evidence_Reader.md)。超限、格式错误、重复 JSON 字段、非有限数字或无法读取会整次失败，不返回半份结果，也不静默截断。文件有界后仍在内存中解析，不是流式读取器或不可信文件沙箱。

专项包含六种版本、60 个种子 Notebook 的 nbformat 文本对照、旧输出与执行乱序、类型/资源边界、来源哈希及元数据隔离。另有真实本地 ipykernel 生成样本的集成测试：只有该受控测试主动执行预定义代码，Reader 本身不导入内核执行栈。测试不证明真实用户实验结论正确，也不承诺检索得分。
