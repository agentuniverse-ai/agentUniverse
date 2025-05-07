# Store

`Store`负责对`Document`进行存储，并在知识的检索阶段提供查询能力。`Store`的具体形式可以是多样的，包括关系型数据库、向量数据库、图数据库等形式。因此同一份`Document`也能在不同的`Store`中以不同的形式存储，而具体的检索方式也和`Store`的能力相绑定。

Store定义如下：
```python
from typing import Any, List, Optional

from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent_serve.web.post_fork_queue import add_post_fork

class Store(ComponentBase):
    component_type: ComponentEnum = ComponentEnum.STORE
    name: Optional[str] = None
    description: Optional[str] = None
    client: Any = None
    async_client: Any = None

    def _new_client(self) -> Any:
        pass

    def _new_async_client(self) -> Any:
        pass

    def _initialize_by_component_configer(self,
                                         store_configer: ComponentConfiger) \
            -> 'Store':
        if store_configer.name:
            self.name = store_configer.name
        if store_configer.description:
            self.description = store_configer.description
        add_post_fork(self._new_client)
        add_post_fork(self._new_async_client)
        return self

    def query(self, query: Query, **kwargs) -> List[Document]:
        raise NotImplementedError

    def insert_document(self, documents: List[Document], **kwargs):
        raise NotImplementedError

    def delete_document(self, document_id: str, **kwargs):
        raise NotImplementedError

    def upsert_document(self, documents: List[Document], **kwargs):
        raise NotImplementedError

    def update_document(self, documents: List[Document], **kwargs):
        raise NotImplementedError
```
- `_new_client`和`_new_async_client`用于创建数据库链接，在组件注册阶段会被添加到[post_fork](../../技术组件/服务化/Web_Server.md)执行列表中，保证创建的数据库连接在Gunicorn模式下的子进程中是独立的。
- `query`函数是知识组件在查询时调用的函数，负责根据传入的Query实例在store中查找相关的内容并以document的形式返回
- `Store`的还包括对`Document`类型数据的增删改查，作为知识存储的管理接口。

在编写完对应代码后，可以参考下面的yaml将你的Store注册为aU组件：
```yaml
name: 'sample_store'
description: 'a sample store'
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.sample_store'
  class: 'SampleStore'
```
其中metadata的type固定为STORE.

### 关注您定义的Store所在的包路径
在agentUniverse项目的config.toml中需要配置Store配置对应的package, 请再次确认您创建的文件所在的包路径是否在`CORE_PACKAGE`中`store`路径或其子路径下。

以示例工程中的配置为例，如下：
```yaml
[CORE_PACKAGE]
store = ['sample_standard_app.intelligence.agentic.knowledge.store']
```

## agentUniverse目前内置Store：
- [Chroma](../../技术组件/存储/ChromaDB.md)
- [Milvus](../../技术组件/存储/Milvus.md)
- [Sqlite](../../技术组件/存储/Sqlite.md)