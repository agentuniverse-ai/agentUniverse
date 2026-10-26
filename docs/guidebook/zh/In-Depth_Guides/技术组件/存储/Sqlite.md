## Sqlite

Store组件中的sqlite用于保存`Document`中的文本内容，并基于Jieba的关键词提取功能构建对应的倒排索引，在检索阶段通过关键词召回相关文档，并通过BM25算法计算Query与召回文本的相关度，最终返回最相似的Top k文档。

### 如何配置Sqlite组件

您可以在[知识组件](../../原理介绍/知识/知识.md)中使用ChromaDB来存储和查询知识，你可以使用以下方式来创建一个使用ChromaDB的存储组件:
```yaml
name: 'sqlite_store'
description: 'a store based on sqlite'
db_path: '../../DB/civil_law_sqlite.db'
k1: 1.5
b: 0.75
keyword_extractor: 'jieba_keyword_extractor'
similarity_top_k: 10
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.sqlite_store'
  class: 'SQLiteStore'
```
- db_path: SQLite 数据库文件的路径，用于存储和管理文本数据。
- k1: BM25 算法中的参数 k1，控制词频对得分的影响。
- b: BM25 算法中的参数 b，控制文档长度对得分的影响。
- keyword_extractor: 用于提取关键词的工具名称，这里指定为 jieba_keyword_extractor。
- similarity_top_k: 根据BM25分数返回的最相关的top k。

### 关键词提取器配置错误

`keyword_extractor` 必须填写已注册的 `DOC_PROCESSOR` 组件名称，例如
`jieba_keyword_extractor`。在插入、更新插入文档或未显式提供关键词的查询之前，
请先加载该组件的配置。未配置提取器或组件名称未注册时会抛出 `ValueError`；
名称未注册的错误信息会包含 SQLite 存储名称和配置的 `keyword_extractor` 值。
请检查名称拼写，并确认处理器配置已包含在应用的组件扫描路径中。
显式提供非空关键词的查询无需调用提取器。

### 使用方式
[知识定义与使用](../../原理介绍/知识/知识定义与使用.md)
