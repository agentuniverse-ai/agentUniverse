# XBRL事实上下文Reader

`XbrlContextReader` 将本地XBRL实例XML中的平面事实逐条转为Document，每条都带主体、期间、单位和维度。同概念不同期间/币种不合并，不计算、不汇总、不作财务判断。安装 `pip install "agentUniverse[xbrl_ext]"`。

```python
from agentuniverse.agent.action.knowledge.reader.file.xbrl_context_reader import XbrlContextReader
documents, report = XbrlContextReader().load_instance("report.xbrl")
print(report["unsupported"])
```

复制 `xbrl_context_reader.yaml.example` 到应用Reader包并改名 `.yaml`，Knowledge配置 `readers: {xbrl: xbrl_context_reader}`。需要路由XML时显式加xml映射。正常insert/query链路已用真实SQLite验证。`load_data`仅返回Documents，遗漏报告使用`load_instance`。

正文为确定性JSON：展开QName、原始值、fact ID、context主体/期间/显式及类型化维度、unit分子分母、nil、decimals/precision及继承语言。数值和日期保留原始字符串，nil不变成0。类型化维度与其他segment/scenario内容保留XML字符串，不解释；命名空间声明可能被lxml规范化。

元数据`xbrl_evidence`另含原文件hash、路径、源行号、元素XPath和序号。ID由文件hash+XPath确定，异地相同字节不变；任意字节变化产生新快照，不自动清理旧Store数据。调用方metadata深拷贝，保留字段不能覆盖。

**不执行taxonomy验证**，每条事实及报告明确标记。schema引用只列出，不加载本地/远程schema；不验证数据类型、计算、维度默认值、日期词法或taxonomy标签。精度字段是原始声明。tuple/复杂事实和linkbase内容显式报告，不展平。iXBRL拒绝，不猜缩放/符号/转换。DTD拒绝，关闭外部解析与网络加载；不是完整XBRL验证器或XML沙箱。缺context/unit、重复ID/维度、无效nil及冲突精度失败。

默认/上限：文件20M/100M字节、事实20000/100000、单篇200000/2M字符、总文本10M/40M字符，M为十进制；参数须正整数。失败不返回部分数据。XML有界但整体解析，不保证固定内存/延迟。

测试采用真实XML，并通过离线Arelle2.36.20对照事实、主体、期间、单位及维度；本地最小schema用于抽取分类，不宣称taxonomy合规验证。另覆盖YAML→Knowledge→SQLite及失败边界。完整测试命令与限制见[英文说明](../../../../en/In-Depth_Guides/Tutorials/Knowledge/XBRL_Context_Reader.md)。
