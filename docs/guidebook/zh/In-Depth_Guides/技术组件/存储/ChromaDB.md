## ChromaDB

agentUniverse中已集成ChromaDB相关依赖，您无需额外安装包即可使用ChromaDB的相关功能。
如果您想学习ChromaDB相关的底层原理，您可以查阅ChromaDB的[官方网站](https://www.trychroma.com/)。

### 如何配置Chromadb组件
```yaml
name: 'chroma_store'
description: 'store based on chroma db'
persist_path: '../../DB/criminal_law.db'
embedding_model: 'dashscope_embedding'
similarity_top_k: 100
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.chroma_store'
  class: 'ChromaStore'
```
- persist_path: 数据库的持久化存储路径，用于存储和加载向量数据。
- embedding_model: 用于生成嵌入向量的模型名称，这里指定为 dashscope_embedding。
- similarity_top_k: 在相似度搜索中返回最相似结果的数量。

### [ChromaHierarchicalStore](../../../../../../agentuniverse/agent/action/knowledge/store/chroma_hierarchical_store.py)
ChromaHierarchicalStore是ChromaStore的子类，用于存储包含层级信息的文档内容。  
一个ChromaHierarchicalStore的定义文件示例如下：
```yaml
name: 'chroma_hierarchical_store'
description: 'sample chroma hierarchical store'
persist_path: '../../DB/civil_law_hierarchical.db'
embedding_model: 'dashscope_embedding'
search_depth: 2
similarity_top_k_list:
  - 2
  - 10
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.chroma_hierarchical_store'
  class: 'ChromaHierarchicalStore'
```
- search_depth: 表示检索深度，检索会从最上层的文档开始逐级搜索
- similarity_top_k_list: 表示检索时不同深度返回的文本数。需注意，如果第一层配置数量为2，第二层为10，最终返回数量为2 * 10 = 20份文档。


### 使用方式
[知识定义与使用](../../原理介绍/知识/知识定义与使用.md)