# MemoryStorage

MemoryStorage负责在记忆组件中，做记忆的临时/持久化存储。


## 如何定义MemoryStorage组件

根据agentUniverse领域组件的设计特性，同其他组件一样，创建一个记忆存储器memory_storage定义由2部分组成:

- xx_memory_storage.yaml
- xx_memory_storage.py

xx_memory_storage.yaml包含了memory_storage组件的名称、描述等重要信息；xx_memory_storage.py包含了记忆存储器的具体定义。理解这一原理后，让我们具体看看该如何创建这两部分内容。

## 如何使用MemoryStorage组件

### 创建MemoryStorage配置 - xx_memory_storage.yaml

#### 一个记忆存储器定义配置的实际样例

```yaml
name: 'chroma_memory_storage'
description: 'demo chroma memory storage'
collection_name: 'memory'
persist_path: '../../DB/memory.db'
embedding_model: 'dashscope_embedding'
metadata:
  type: 'MEMORY_STORAGE'
  module: 'agentuniverse.agent.memory.memory_storage.chroma_memory_storage'
  class: 'ChromaMemoryStorage'
```

- name: 记忆存储器名称，用于标识记忆存储器
- description: 记忆存储器描述信息，用于标识记忆存储器的用途
- collection_name: ChromaDB中collection的名称
- persist_path: ChromaDB的持久化路径
- embedding_model: 嵌入模型的领域组件名称
- metadata: 组件元数据，用于标识记忆存储器类型、所在包路径和类名

### 创建MemoryStorage领域行为定义 - xx_memory_storage.py

agentUniverse提供了一个MemoryStorage基础类，您需要继承它并重写add/delete/get函数，完成对记忆信息的存储/删除/获取。

#### [MemoryStorage类的定义:](../../../../../../agentuniverse/agent/memory/memory_storage/memory_storage.py)

- add(self, message_list: List[Message], session_id: str = '', agent_id: str = '', **kwargs) -> None:
  : 记忆信息存储，将记忆的消息列表、智能体id（agent_id）、会话id（session_id）、source（记忆来源）等信息，在特定存储仓库中完成存储。

- delete(self, session_id: str = None, agent_id: str = None, **kwargs) -> None:
  : 记忆信息删除，在特定存储仓库中，根据会话id（session_id）、智能体id（agent_id）、source（记忆来源）等条件过滤，删除对应的记忆数据。

- get(self, session_id: str = '', agent_id: str = '', top_k=10, **kwargs) -> List[Message]:
  : 记忆信息获取，获在特定存储仓库中，根据智能体id（agent_id）、会话id（session_id）、source（记忆来源）等条件过滤，获取对应的记忆数据。

### 在Memory中配置使用

如上文中创建的`chroma_memory_storage`实例，在memory中您可以这样设置：

```yaml
name: 'demo_memory'
# omitted part
memory_storages:
  - chroma_memory_storage
memory_retrieval_storage: chroma_memory_storage
# omitted part
```

### 关注您定义的MEMORY_STORAGE所在的包路径

在agentUniverse项目的config.toml中需要配置MEMORY_STORAGE配置对应的package,
请再次确认您创建的文件所在的包路径是否在`CORE_PACKAGE`中`memory_storage`路径或其子路径下。

以示例工程中的配置为例，如下：

```yaml
[CORE_PACKAGE]
memory_storage = ['sample_standard_app.intelligence.agentic.memory.memory_storage']
```

## agentUniverse目前内置有以下MemoryStorage组件:

### [ram_memory_storage](../../../../../../agentuniverse/agent/memory/memory_storage/ram_memory_storage.py)

本地内存记忆存储器，系统内置组件配置文件如下：

```yaml
name: 'ram_memory_storage'
description: 'ram memory storage'
metadata:
  type: 'MEMORY_STORAGE'
  module: 'agentuniverse.agent.memory.memory_storage.ram_memory_storage'
  class: 'RamMemoryStorage'
```

### [chroma_memory_storage](../../../../../../agentuniverse/agent/memory/memory_storage/chroma_memory_storage.py)

ChromaDB记忆存储器，记忆获取时包含向量检索和条件检索两种方式，sample工程中**示例**组件配置文件如下：

```yaml
name: 'chroma_memory_storage'
description: 'demo chroma memory storage'
collection_name: 'memory'
persist_path: '../../DB/memory.db'
embedding_model: 'dashscope_embedding'
metadata:
  type: 'MEMORY_STORAGE'
  module: 'agentuniverse.agent.memory.memory_storage.chroma_memory_storage'
  class: 'ChromaMemoryStorage'
```

其中`collection_name`为chroma的collection名称，`persist_path`为chroma的持久化路径，`embedding_model`
为用于向量检索的embedding领域组件名称。

### [sql_alchemy_memory_storage](../../../../../../agentuniverse/agent/memory/memory_storage/sql_alchemy_memory_storage.py)

SqlAlchemy记忆存储器，内部成员包含aU另一领域组件[SQLDB_WRAPPER](../../技术组件/存储/SQLDB_WRAPPER.md)，sample工程中**示例**组件配置文件如下：

```yaml
name: 'mysql_memory_storage'
description: 'demo mysql memory storage'
sqldb_table_name: 'memory'
sqldb_wrapper_name: 'mysql_sqldb_wrapper'
metadata:
  type: 'MEMORY_STORAGE'
  module: 'agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage'
  class: 'SqlAlchemyMemoryStorage'
```

其中`sqldb_table_name`为sqlalchemy的table名称，`sqldb_wrapper_name`为sqldb_wrapper领域组件的实例名称。

mysql_sqldb_wrapper的示例配置如下：

```yaml
name: 'mysql_sqldb_wrapper'
description: 'mysql_sqldb_wrapper'
db_uri: "mysql+pymysql://root:root123456@127.0.0.1:3306/test"
engine_args:
  pool_size: 5
metadata:
  type: 'SQLDB_WRAPPER'
```

其中db_uri为数据库连接地址，engine_args为sqlalchemy的engine参数。

### 限量读取 SQL 记忆

对话记忆实现
`agentuniverse.agent.memory.conversation_memory.memory_storage.sqlite_conversation_memory_storage`
中的 `SqliteMemoryStorage` 会按时间顺序返回最近的消息。对于正整数 `top_k`，
数据库查询会先限制返回的行数，再由 SQLAlchemy 创建消息行对象。例如，调用
`storage.get(session_id="chat", top_k=20)` 时，即使该会话包含数千条消息，也最多
加载 20 个匹配的消息行对象。时间戳相同的消息按映射表的主键排序，默认转换器使用
数据库行 id，自定义转换器可以使用其他主键或复合主键。已有的会话、智能体、链路
和消息类型条件均在限制数量前生效。

上文介绍的通用 `SqlAlchemyMemoryStorage` 也使用同一条限量查询路径，按其
`gmt_created` 字段排序，保留已有的会话、智能体和来源筛选条件。该存储器默认
读取 10 条消息，SQLite 对话存储器默认读取 20 条。
