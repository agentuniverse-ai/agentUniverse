## FAISS

本页介绍如何在 agentUniverse 中使用 FAISS 作为向量存储组件。

### 安装
```bash
pip install faiss-cpu   # CPU 环境
# 或
pip install faiss-gpu   # GPU 环境
```

### 组件配置示例
```yaml
name: 'faiss_store'
description: 'a store based on faiss'
index_path: './DB/faiss/index.ivf'   # 可选；为空则仅在内存
embedding_model: 'dashscope_embedding'
similarity_top_k: 20
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.faiss_store'
  class: 'FaissStore'
```

### 说明
- `index_path`: 索引持久化路径；配置后可在重启后加载同一索引。
- `embedding_model`: 当插入/检索未提供向量时，自动调用该嵌入模型生成向量。
- `similarity_top_k`: 默认召回条数。

### 使用
与 `ChromaStore`/`MilvusStore` 使用方式一致：通过知识导入或 `Store` API 写入 `Document`，使用 `Query` 进行相似搜索。


