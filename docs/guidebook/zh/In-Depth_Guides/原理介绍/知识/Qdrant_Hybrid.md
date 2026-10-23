# Qdrant 原生稀疏＋稠密检索

`QdrantHybridStore` 是独立可选 Store，旧 `QdrantStore` 不变。每条文档同时写入两个命名向量，通过服务端 prefetch + RRF 融合检索。它不提供稀疏编码模型，也不承诺融合一定提高相关性。完整配置、示例和复现命令见[英文说明](../../../../en/In-Depth_Guides/Tutorials/Knowledge/Qdrant_Hybrid.md)。

## 配置与接入

Python 3.10–3.12 安装 `agentuniverse[qdrant_hybrid_ext]`，可选客户端版本为 >=1.14.3,<1.15。项目当前 NumPy 1.26 约束与较新客户端/Python 组合冲突，因此此 extra 不支持 Python 3.13。真实测试组合为服务端 1.14.1、客户端 1.14.3，不代表所有版本兼容。

将 `qdrant_hybrid_store.yaml.example` 复制到应用的 Store 扫描目录，配置授权服务 URL、collection 和维度。凭证通过应用配置机制提供，不能放入文档元数据。部署使用认证与 TLS；示例的 HTTP 回环地址只用于本地测试。

独占一个新 collection，先单线程 `create_collection: true` 完成创建，再切为 false 启动并发工作。已有结构必须只有 `au_dense`（cosine、匹配维度、非 multivector）和 `au_sparse`（不加 IDF modifier）。不会删除、重建或迁移旧 collection；创建竞争直接报错。结构检查、标记字段和过滤都不是访问权限控制。

## 输入输出约定

- 文档的 `embedding` 为稠密向量；`metadata.qdrant_sparse` 为 `{"indices": [...], "values": [...]}`。稠密向量有限、非零并归一化；稀疏下标为不重复 uint32，权重为有限非零 float32 normal 值。两种编码在文档与查询之间必须使用同一版本模型/词表。
- hybrid 查询显式传 `Query.embeddings` 中唯一向量以及 `ext_info.sparse_vector`。dense/sparse 模式分别只需要对应向量。`query_str` 不会自动编码。Knowledge 入库需要显式 processor 提供两种向量；不能把测试中的固定向量当成真实模型。
- `candidate_k` 控制每路候选，最终 top-k 不大于它；查询 top-k=0 无 I/O。融合分数不是概率，不能与 cosine 分数混比；并列顺序由引擎决定，不保证截断边界稳定。
- `ext_info.filters` 支持最多 64 个顶层标量等值条件，AND 同时应用于两路和最终查询。布尔、整数、浮点、字符串和 null 严格区分。不支持嵌套、区间、OR；业务过滤不等于租户安全隔离。
- 稳定字符串 ID 统一映射 UUID5，payload 保留原 ID。insert/update/upsert 均为完整幂等替换，非“仅新增/仅更新”。更新同时替换两种向量及全部 metadata。空批次无操作。
- 返回 `metadata.qdrant_retrieval` 包含模式、分数和候选上限。`with_vectors` 可返回归一化 dense 和 sparse。该诊断字段为保留字段，回写检索结果前须显式去掉它。输入不被修改。

## 确认与边界

写入前验证批次重复 ID、向量、数量、文本及编码字节限制。检索有返回文本字符总量限制，但不保证传输/进程内存硬上限。写入使用 `wait=True`，只有 COMPLETED 返回确认；ACK-only 抛错。超时、取消和网络错误后的远端状态可能不明，重试前查询受影响 ID 对账。无自动重试、无跨操作事务、无批次回滚承诺。

写操作使用客户端超时；query/create 还使用其支持的服务端超时参数。超时不代表远端停止。原生异步取消向上传递，异步客户端不能跨 event loop 复用；关闭前等待操作结束，分别调用 `close()`/`await aclose()`。继承的 Knowledge 入库入口目前会记录 Store 异常；需要严格确认时检查 Store 回执/异常，不将完成日志视作事务成功。

真实服务测试覆盖服务端直接融合对照、单双路行为、双向量更新、重开与删除、标量过滤、结构不兼容、批次预检、异步 CRUD、YAML 注册和公开 Knowledge 链路。取消为客户端 mock 测试，不证明服务端回滚。尚未做真实编码模型相关性、生产数据召回率或延迟基准。
