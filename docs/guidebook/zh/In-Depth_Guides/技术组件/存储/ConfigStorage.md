# **ConfigStorage 模块**

ConfigStorage 是agentUniverse框架中的配置持久化与加载组件，支持将智能体应用的元信息统一存储到关系型数据库，并在需要时自动恢复。

## **特性**

- **启动落库**：框架启动时会将本地配置文件持久化到数据库，保证一致性。
- **延迟加载**：本地文件中不存在的组件，不会立即从数据库加载，而是在首次调用 get_instance_obj 时延迟恢复。
- **可插拔加载器**：
  - 用户可通过配置文件选择不同存储方式（目前只支持DB ）。
  - 也可继承 BaseConfigLoader 实现自定义逻辑（如 REST API、KV 存储）。
- **版本管理**：内置 ConfigVersionManager，支持配置历史追踪。

## **快速开始**

在全局配置文件中指定存储方式：

```yaml
CONFIG_STORAGE:
  type: "DB"          # 默认：DB 
  persist: true       # 决定是否启用存储，默认False
  db_uri: "sqlite:///agent.db"
  namespace: "dev"
```

### **持久化配置**

```python
from agentuniverse.base.storage.storage_context import StorageContext

ctx = StorageContext(
    instance_code="app.agent.my_component",
    configer=configer,
    configer_type=ComponentEnum.AGENT,
    root_package_name=ConfigStorage().root_package_name
)

ConfigStorage().persist_to_storage(ctx)
```

### **从数据库加载**

```python
ctx = StorageContext(
    instance_code="app.agent.my_component",
    configer_type=ComponentEnum.AGENT
)

configer = ConfigStorage().load_from_storage(ctx)
print("Loaded config:", configer.value)
```

## **配置说明**

### **使用自定义 Loader**

1. 编写一个自定义类继承 BaseConfigLoader：

```python
from agentuniverse.base.storage.loader.base_config_loader import BaseConfigLoader

class CustomConfigLoader(BaseConfigLoader):
    def load(self, ctx):
        # 实现自定义加载逻辑
        ...
    def save(self, ctx):
        ...
    def delete(self, ctx):
        ...
```

1. 在配置文件中注册：

```yaml
EXTENSION_MODULES:
  class_list:
    - "your_package.custom_loader.CustomConfigLoader"
```

这样，ConfigStorage 会自动识别并使用你的自定义实现。



## **注意事项**

- 数据库 Schema 会在首次运行时自动创建；
- 建议在生产环境中使用持久化数据库（MySQL / PostgreSQL），而非内存数据库。

