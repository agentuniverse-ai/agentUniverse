# 离线 ColBERT 逐 token 重排

`ColbertReranker` 是显式注册的 DocProcessor，对已召回的有限文本候选逐 token 编码，
将每个查询 token 与文档 token 的最大点积分数求和。它不是均值池化、CrossEncoder、
BM25、RRF 或新的向量库，不会把二维 token 矩阵放进 Document.embedding。

首版固定使用 Answer.AI 的英文小模型 `answerdotai/answerai-colbert-small-v1`，
revision `934fa8bb4ce2284f4c2baa232d81aca4d076fa5e`，Apache-2.0。
可选依赖 `colbert_ext`：Sentence Transformers 6.2.0、torch>=2.6,<3；实际测试 torch 2.6.0 CPU。
先按[英文指南](../../../../en/In-Depth_Guides/Tutorials/Knowledge/ColBERT_Reranker.md)单独缓存模型。
运行时只读本地缓存，不携带 Hub 令牌、不下载、不执行远程自定义代码；缓存不全会报错。

将随附 `colbert_reranker.yaml.example` 复制为应用 doc_processor 包中的 `.yaml` 并注册，
再给现有 Knowledge 配置 `post_processors: [colbert_reranker]`。
组件不会自动注册、创建索引或补回未召回的文档。也可直接调用 `rerank(docs, Query(...))`，
得到结果和包含模型版本、token 数、分数、是否截断等信息的回执。

默认最多 32 个候选、batch 4、返回前 5 个，查询最多 1000 字符、单文档 4000 字符、
总输入 64000 字符。固定模型含特殊 token/前缀的查询上限 32、文档上限 300；超限在编码前
明确拒绝，不静默截断。查询扩展由模型实现，输出 32 个向量；每篇最多 9600 个交互单元。
这是工作量约束，不是整个 Python 进程的内存上限。只支持该英文文本模型和 CPU，
不承诺中文、GPU、任意模型、图片、向量索引或大规模吞吐效果。

结果深拷贝原文档，保留 ID、文本、keywords 和原普通 embedding，写入组件自用的
`colbert_rerank` 元数据；相同分数保持候选顺序。共享实例串行执行编码，首次载入后模型常驻。

测试包含真实模型分数与官方 similarity/独立标量 MaxSim 对照、YAML→组件管理器→
真实 SQLite→Knowledge 公共查询、输入不变性和边界失败，以及 9 项已有处理流水线回归。
另用自写英文 3 查询/12 文档小样本比较 BM25，详细数值保存在 JUnit。
这只是可控实验，不代表真实业务提升：其中一题相关文档仅排第二，不宣称满分检索。
复现入口及证据在 `tests/reproduction/colbert-late-interaction/`；没有 CI、合并或比赛得分承诺。
