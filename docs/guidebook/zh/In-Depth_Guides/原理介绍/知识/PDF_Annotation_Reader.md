# PDF批注证据Reader

`PdfAnnotationReader` 为Text、FreeText、Highlight、Underline、Squiggly和StrikeOut批注逐条生成Document，空评论也保留。安装 `pip install "agentUniverse[pdf_ext]"`。

```python
from agentuniverse.agent.action.knowledge.reader.file.pdf_annotation_reader import PdfAnnotationReader
documents, report = PdfAnnotationReader().load_annotations("review.pdf")
print(report["omitted_annotations"])
```

复制 `pdf_annotation_reader.yaml.example` 至应用Reader目录并改名`.yaml`，在目标Knowledge配置 `readers: {pdf: pdf_annotation_reader}`，正常insert/query。此映射显式选择批注模式，不修改全局默认PDF Reader。真实YAML→Knowledge→SQLite已有测试；`load_data`只返回Documents，需要遗漏报告时用`load_annotations`。

正文突出评论及批注类型/页码。保留元数据`pdf_annotation`含源hash/路径、页码/批注序号、对象引用、作者/主题/名称、原始日期、Rect/QuadPoints、flags、MediaBox/CropBox/旋转/UserUnit与回复关系。作者/日期只是文件声明。富文本只记录存在性，不解释。调用方metadata深拷贝，不能覆盖保留字段。

坐标保持未旋转PDF默认用户空间，不转换像素，使用时须结合页面框、旋转及UserUnit（默认1/72英寸）。Rect与每8个数的QuadPoints不是同一锚点，均保留。高亮坐标不等于精确引文：首版不提取/匹配页面文本，anchor_text_extracted始终false。隐藏/不可见标记保留，不承诺所有批注可见。

回复只按页批注数组中的精确间接对象引用解析一跳，区分resolved、不支持目标、重复目标歧义、孤立/直接引用。不跟循环、不推断时间顺序；NM不当唯一ID。Document ID由文件hash+页/批注位置决定，异地相同文件不变，修改生成新快照，不清理旧Store。

仅本地未加密PDF。不抽取/执行附件、动作、链接或表单；不支持类型进入报告。生产Reader不渲染、不抽取appearance；缺QuadPoints保留null。格式/选中字段错误和预算耗尽失败且不返回部分结果，不是完整PDF验证器或解析沙箱。

默认/上限：文件32M/128M字节、页面2000/10000、所有批注20000/100000、单篇200000/2M字符、总文本10M/40M字符。单篇另检查选中字符串元数据，参数须正整数。文件有界但整体解析；对象流/页面树可能消耗远大于文件体积的内存，不保证解析内存/时间上限。

真实ReportLab/pypdf导出文件经PyMuPDF独立核对评论/回复/坐标，覆盖裁剪旋转、空评论、孤立/歧义回复、UserUnit、多个quad、加密/预算失败与文件hash不变。Poppler渲染检查了测试夹具。测试依赖不进入生产代码；完整命令见[英文说明](../../../../en/In-Depth_Guides/Tutorials/Knowledge/PDF_Annotation_Reader.md)。
