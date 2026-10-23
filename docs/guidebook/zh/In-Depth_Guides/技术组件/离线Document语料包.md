# 可校验离线 Document 语料包

`corpus_bundle.export_bundle` 将用户选定的 Documents、显式来源文本和文档到来源的关联写入新 `.auc` 文件；`load_bundle` 全包校验成功后才返回 Documents。不会提取文件或修改 Store。

```python
from agentuniverse.agent.action.knowledge.corpus_bundle import export_bundle, load_bundle
from agentuniverse.agent.action.knowledge.store.document import Document

sha = export_bundle("research.auc", [Document(id="chunk-1", text="证据")],
                    sources={"paper-1": "证据"}, document_sources={"chunk-1": ["paper-1"]})
documents = load_bundle("research.auc", expected_sha256=sha)
```

默认不导出向量或任何 metadata。需要时用 `metadata_keys=["page"]` 显式选择 JSON 元数据；文本、ID、关键词本身仍可能敏感，导出前应检查。不是自动脱敏、加密或身份认证。

复制 `corpus_bundle_reader.yaml.example` 到应用组件目录，Knowledge 配置 `readers: {auc: corpus_bundle_reader}`，再调用 `insert_knowledge(source_path="research.auc")`。Reader 在返回首批文档前验证所有成员；包尾损坏不会部分入库，但不改变现有 Store 写入失败或跨 Store 事务语义。

V1 使用未压缩、未加密 ZIP。manifest.json 保存版本、来源和文档清单；sources/N.txt 保存 UTF-8 来源；documents/N.json 保存 ID、正文、JSON metadata 和关键词。所有内容成员均有 SHA-256，来源使用稳定逻辑 ID，与机器路径无关。来源关联由调用者声明，不证明正文真实性或分块推导关系。内部摘要不防整体恶意替换，应单独可信保存整个包摘要。

重复/缺失/额外成员、非规范路径、版本不兼容、重复 ID/JSON 键、不匹配摘要、非有限 JSON 数字等均拒绝。加载后注入保留字段 `_corpus_bundle`，记录包摘要、文档摘要、来源 ID/摘要及版本。用户元数据不能伪造此字段。

输出目录需存在；临时文件写完并 flush 后用硬链接原子发布，禁止覆盖。文件系统不支持硬链接时失败并清理临时文件；不保证断电后的目录持久性。归档大小、展开大小、来源数、文档数均有上限，整个有界包保存在内存中。完整格式和限制见英文 Offline_Document_Bundles.md。
