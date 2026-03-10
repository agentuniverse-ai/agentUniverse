# MemoryStorage

MemoryStorage is responsible for the temporary or persistent storage of memories within the memory component.

## How to Define a MemoryStorage Component

Following the design characteristics of agentUniverse domain components, like other components, creating a memory
storage (memory_storage) definition consists of two parts:

- xx_memory_storage.yaml
- xx_memory_storage.py

xx_memory_storage.yaml contains important information such as the name, description, etc., of the memory_storage
component; xx_memory_storage.py contains the specific definition of the memory storage. After understanding this
principle, let's take a look at how to create these two parts.

## How to Use the MemoryStorage Component

### Creating a MemoryStorage Configuration - xx_memory_storage.yaml

#### An Actual Example of a Memory Storage Definition Configuration

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

- name: The name of the memory storage, used to identify the memory storage.
- description: The description of the memory storage, used to indicate the purpose of the memory storage.
- collection_name: The name of the collection in ChromaDB.
- persist_path: The persistence path of ChromaDB.
- embedding_model: The name of the embedding model domain component.
- metadata: Component metadata, used to identify the type of memory storage, the package path it is in, and the class
  name.

### Creating MemoryStorage Domain Behavior Definition - xx_memory_storage.py

agentUniverse provides a base MemoryStorage class. You need to inherit it and override the add/delete/get functions to
complete the storage, deletion, and retrieval of memory information.

#### [Definition of MemoryStorage Class:](../../../../../../agentuniverse/agent/memory/memory_storage/memory_storage.py)

- add(self, message_list: List[Message], session_id: str = '', agent_id: str = '', **kwargs) -> None:
  : Memory information storage, stores the memory message list, agent ID (agent_id), session ID (session_id), source (
  memory source), and other information in a specific storage repository.

- delete(self, session_id: str = None, agent_id: str = None, **kwargs) -> None:
  : Memory information deletion, deletes the corresponding memory data in a specific storage repository, filtered by
  session ID (session_id), agent ID (agent_id), source (memory source), and other conditions.

- get(self, session_id: str = '', agent_id: str = '', top_k=10, **kwargs) -> List[Message]:
  : Memory information retrieval, obtains the corresponding memory data in a specific storage repository, filtered by
  agent ID (agent_id), session ID (session_id), source (memory source), and other conditions.

### Configuring and Using in Memory

As with the `chroma_memory_storage` instance created in the previous text, you can set it up in the memory like this:

```yaml
name: 'demo_memory'
# omitted part
memory_storages:
  - chroma_memory_storage
memory_retrieval_storage: chroma_memory_storage
# omitted part
```

### Pay Attention to the Package Path of Your Defined MEMORY_STORAGE

In the `config.toml` of the agentUniverse project, you need to configure the package corresponding to the MEMORY_STORAGE
configuration. Please confirm again that the package path where you created the file is under the `memory_storage` path
in `CORE_PACKAGE` or its sub-path.

For example, the configuration in the sample project is as follows:

```yaml
[CORE_PACKAGE]
memory_storage = ['sample_standard_app.intelligence.agentic.memory.memory_storage']
```

## agentUniverse currently has the following built-in MemoryStorage components:

### [ram_memory_storage](../../../../../../agentuniverse/agent/memory/memory_storage/ram_memory_storage.py)

Ram memory storage, the system's built-in component configuration file is as follows:

```yaml
name: 'ram_memory_storage'
description: 'ram memory storage'
metadata:
  type: 'MEMORY_STORAGE'
  module: 'agentuniverse.agent.memory.memory_storage.ram_memory_storage'
  class: 'RamMemoryStorage'
```

### [chroma_memory_storage](../../../../../../agentuniverse/agent/memory/memory_storage/chroma_memory_storage.py)

ChromaDB Memory Storage, which includes vector retrieval and conditional retrieval when retrieving memories. The **example** component configuration file in the sample project is as follows:

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

Here, `collection_name` is the name of the Chroma collection, `persist_path` is the persistence path for Chroma, and `embedding_model` is the name of the embedding domain component used for vector retrieval.

### [sql_alchemy_memory_storage](../../../../../../agentuniverse/agent/memory/memory_storage/sql_alchemy_memory_storage.py)

SqlAlchemy Memory Storage, which includes another domain component of aU, [SQLDB_WRAPPER](../../Tech_Capabilities/Storage/SQLDB_WRAPPER.md). The **example** component configuration file in the sample project is as follows:

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

Here, `sqldb_table_name` is the table name for SqlAlchemy, and `sqldb_wrapper_name` is the instance name of the sqldb_wrapper domain component.

An example configuration for mysql_sqldb_wrapper is as follows:

```yaml
name: 'mysql_sqldb_wrapper'
description: 'mysql_sqldb_wrapper'
db_uri: "mysql+pymysql://root:root123456@127.0.0.1:3306/test"
engine_args:
  pool_size: 5
metadata:
  type: 'SQLDB_WRAPPER'
```

### [hybrid_memory_storage](../../../../../../agentuniverse/agent/memory/memory_storage/hybrid_memory_storage.py)

A composite memory storage that delegates operations to multiple child storage backends. All write operations are executed in parallel across all child storages, and read operations return the first non-empty result.

```yaml
name: 'my_hybrid_storage'
description: 'vector + kv hybrid memory storage'
storage_names:
  - chroma_memory_storage
  - mysql_memory_storage
metadata:
  type: 'MEMORY_STORAGE'
  module: 'agentuniverse.agent.memory.memory_storage.hybrid_memory_storage'
  class: 'HybridMemoryStorage'
```

The `storage_names` field lists the names of child storage instances. Add and delete operations are fanned out to all child storages in parallel, while get operations return data from the first child storage that has results.

### [qdrant_memory_storage](../../../../../../agentuniverse/agent/memory/memory_storage/qdrant_memory_storage.py)

Qdrant vector database memory storage, supporting vector-based memory retrieval.

Here, `db_uri` is the database connection address, and `engine_args` are the engine parameters for SqlAlchemy.
