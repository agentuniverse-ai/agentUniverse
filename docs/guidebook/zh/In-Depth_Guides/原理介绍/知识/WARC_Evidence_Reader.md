# WARC历史网页证据Reader

`WarcEvidenceReader` 从本地 `.warc` / `.warc.gz` 提取归档HTTP文本，不重新访问URL。安装 `pip install "agentUniverse[warc_ext]"`。

```python
from agentuniverse.agent.action.knowledge.reader.file.warc_evidence_reader import WarcEvidenceReader
documents, report = WarcEvidenceReader().load_archive("snapshot.warc.gz")
print(report["omitted_records"])
```

将包内 `warc_evidence_reader.yaml.example` 复制到应用Reader配置目录并改名为 `.yaml`，Knowledge设置 `readers: {warc: warc_evidence_reader}`。正常使用 `insert_knowledge` / `query_knowledge`。Knowledge按最后扩展名路由，压缩文件须显式映射 `gz`；这也会把其他gz文件路由至本Reader并可能拒绝。直接调用 `load_archive` 可避免歧义。`load_data` 只返回Documents；需要遗漏说明时用 `load_archive`。

每条响应单独成Document，保留归档SHA-256、record ID、URL、原始捕获日期、摘要验证状态、正文hash与解压后记录偏移/长度（不含4字节分隔符）。日期/URL只是归档声明，不证明真实性。ID由归档hash和record ID决定；相同字节异地副本ID一致，重新打包会产生新快照，不自动清理Store。

支持WARC1.0/1.1、完整2xx HTTP文本响应，plain/HTML/XHTML、声明字符集（默认UTF-8）、identity/chunked传输和identity/gzip内容编码。HTML用BeautifulSoup移除script/style/template后抽取派生文本。不会复制Cookie和任意HTTP头。缺少摘要不标为已验证；hash不证明来源。

Revisit仅支持identical-payload profile、同文件精确Record-ID引用与相同且已验证的源payload摘要。引用日期/URL若存在必须一致。不按URL猜测、不跟引用链、不联网补缺；保留revisit日期并单独记录payload源日期。不支持的类型/profile、缺源、非成功/部分HTTP、非文本/不支持编码、分段/截断记录均进入遗漏报告。

长度/摘要错误、重复ID、缺失/多余CRLF分隔符、选中文本解码失败、预算耗尽均失败且不返回部分结果。这是受限Reader，不是完整WARC合规验证器；不支持chunk trailers。原文件不变。

默认/配置上限：文件32M/128M字节，解压128M/256M字节，记录10000/50000，记录和payload各8M/32M字节，单篇2M/8M字符，总文本10M/40M字符。M为十进制。参数须正整数；布尔不接受。文件有界但整体缓存在内存，不承诺HTML解析内存/延迟上限。调用方metadata深拷贝，不能覆盖保留字段warc_evidence。

验证采用warcio1.7.5真实WARCWriter文件、双版本/gzip、HTTP gzip/chunked、revisit、摘要与预算失败，及真实本地HTTP捕获和YAML→Knowledge→SQLite。无外网站点或付费模型。测试命令、完整参数与参考规范见[英文说明](../../../../en/In-Depth_Guides/Tutorials/Knowledge/WARC_Evidence_Reader.md)。
