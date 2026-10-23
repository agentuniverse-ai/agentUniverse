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

### 多线程共享实例

同一个 `SQLiteStore` 实例的 `insert_document`、`upsert_document`、
`delete_document` 和 `query` 共享连接并串行执行，避免查询或其他写入提前提交
仍在提取关键词的写事务，也保证召回、评分和读取结果期间不会被同实例的写入打断。
查询辅助方法不会提交事务；关键词处理器在当前线程读取同一实例时，也不会提前提交
外层写入。因此，写入失败后仍能回滚尚未提交的数据。

锁只属于当前实例，独立实例可以并行运行。直接访问 `conn` 或让多个实例共用同一个
连接会绕过这项保护。关键词处理器在串行操作内执行，应避免等待另一个线程访问
当前实例后再返回。

### 使用方式
[知识定义与使用](../../原理介绍/知识/知识定义与使用.md)
