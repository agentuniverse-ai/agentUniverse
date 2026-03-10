# SQLDB Wrapper

agentUniverse基于SQLAlchemy，提供了一个方便用户使用大多数基于SQL的数据库的`SQLDBWrapper`类，如SQLite、MySQL、Oracle等，具体请参考[SQLAlchemy官方网站](https://docs.sqlalchemy.org/en/20/dialects/)。通过`SQLDBWrapper`，您可以方便的同时管理多种不同的数据库连接对象。

## 注册方式

### 第一步：配置扫描路径
agentUniverse通过在应用启动时扫描配置路径的方式寻找SQLDBWrapper的配置文件并进行自动注册，扫描的路径配置在配置文件`config.toml`中：
```toml
[CORE_PACKAGE]
default = ['default_scan_path']
sqldb_wrapper = ['sqldb_wrapper_scan_path']
```
agentUniverse默认会扫描`default`或`sqldb_wrapper`中的所有路径，`sqldb_wrapper`下的路径配置优先级高于`default`。


### 第二步：配置文件
```yaml
name: 'demo_sql'
description: 'demo_sql'
db_uri: "sqlite:///./demo.db"
sql_database_args:
  include_tables: ["users"]
engine_args:
  pool_size: 10
metadata:
  type: 'SQLDB_WRAPPER'
```
- **`name`**:SQLDBWrapper的名称，用于标识唯一的一个实例。
- **`description`**:对SQLDBWrapper的名称功能的描述。
- **`db_uri`**:一个SQLAlchemy风的数据库uri，用于创建SQLAlchemy引擎。
- **`sql_database_args`**:可选参数，SQLDatabase类的配置参数，如`include_tables`、`max_string_length`等。
- **`engine_args`**:可选参数，用于配置SQLAlchemy的引擎参数。具体可配置内容请参考[SQLAlchemy网页](https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine)。
- **`metadata`**:表示该配置是一个SQLDB_WRAPPER配置，无需改动。

## 使用方式
SQLDBWrapper类有以下几个函数供用户使用：

### run
`run`接收一个`str`类型的参数`command`，表示一个SQL语句，并通过SQLAlchemy执行该SQL并返回结果。结果形式为一个`list`，如果`command`为查询语句则`list`中会含有查询的结果，每一个元素都是一个字典，代表一行数据库中的数据，key为列名而value为对应的值。
```python
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

demo_sqldb_wrapper:SQLDBWrapper = SQLDBWrapperManager().get_instance_obj("demo_sqldb_wrapper")
demo_sqldb_wrapper.run("select * from USERS")
```
返回结果示例:
```text
[{'age': 30, 'id': 1, 'name': 'Alice'}, {'age': 25, 'id': 2, 'name': 'Bob'}]
```

### run_with_str_return
`run`接收一个`str`类型的参数`command`，表示一个SQL语句，并通过SQLAlchemy执行该SQL并返回结果。结果形式为一个`str`，如果`command`为查询语句则`str`为所有查询结果数据的拼接，且如果在`sql_database_args`中配置了`max_string_length`参数的话，会对结果进行截断。这个函数更方便用于将结果作为llm的输入
```python
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

demo_sqldb_wrapper:SQLDBWrapper = SQLDBWrapperManager().get_instance_obj("demo_sqldb_wrapper")
demo_sqldb_wrapper.run_with_str_return("select * from USERS")
```
返回结果示例：
```text
"[(1, 'Alice', 30), (2, 'Bob', 25)]"
```

### sql_database
如果您希望使用一些SQLAlchemy或者SQLDatabase原生的功能，您可以通过访问SQLDBWrapper的`sql_database`属性获取对应对象：
```python
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

demo_sqldb_wrapper:SQLDBWrapper = SQLDBWrapperManager().get_instance_obj("demo_sqldb_wrapper")
sql_database_ins = demo_sqldb_wrapper.sql_database
sql_alchemy_engine = sql_database_ins._engine
```