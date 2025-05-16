# SQLDB Wrapper

Based on SQLAlchemy and Langchain's SQLDatabase, agentUniverse offers a `SQLDBWrapper` class that allows users to conveniently utilize most SQL-based databases, such as SQLite, MySQL, Oracle, and more. For detailed information, please refer to the [SQLAlchemy official website](https://docs.sqlalchemy.org/en/20/dialects/). With SQLDBWrapper, users can easily manage multiple different database connection objects simultaneously.

## Registration Method

### Step One: Configure Scan Path
agentUniverse automatically registers SQLDBWrapper configuration files by scanning the configured paths during application startup. The paths to be scanned are specified in the `config.toml` file:
```toml
[CORE_PACKAGE]
default = ['default_scan_path']
sqldb_wrapper = ['sqldb_wrapper_scan_path']
```
By default, AgentUniverse scans all paths under either `default` or `sqldb_wrapper`sections in the configuration, with paths under `sqldb_wrapper` having a higher priority than those under `default`.


### Step Two: Configuration File
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
- **`name`**: The name of the SQLDBWrapper, used to uniquely identify an instance.
- **`description`**: A brief description of the functionality of the SQLDBWrapper's.
- **`db_uri`**: A SQLAlchemy-style database URI, which is used to create a SQLAlchemy engine.
- **`sql_database_args`**: Optional parameters for the SQLDatabase class in `LangChain`. For specific details, refer to [LangChain's official website](https://python.langchain.com/v0.1/docs/integrations/toolkits/sql_database/).
- **`engine_args`**:  Optional parameters used to configure SQLAlchemy engine settings. For specific configurable options, please refer to [SQLAlchemy's webpage](https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine).
- **`metadata`**: Indicates that this configuration is specific to the `SQLDB_WRAPPER`and should not be changed.

## Usage
The SQLDBWrapper class offers the following functions for users:

### run
The `run` function accepts a `str` type parameter command, which represents an SQL statement. It executes this SQL statement via SQLAlchemy and returns the results. If the command is a query statement, the result will be a list, where each element is a dictionary representing a row in the database. The dictionary keys correspond to column names, and the values correspond to the respective data in those columns.
```python
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

demo_sqldb_wrapper:SQLDBWrapper = SQLDBWrapperManager().get_instance_obj("demo_sqldb_wrapper")
demo_sqldb_wrapper.run("select * from USERS")
```
Example of returned result:
```text
[{'age': 30, 'id': 1, 'name': 'Alice'}, {'age': 25, 'id': 2, 'name': 'Bob'}]
```

### run_with_str_return
The `run_with_str_return` function accepts a `str` type parameter command, which represents an SQL statement. It executes this SQL statement via SQLAlchemy and returns the results as a `str`. If the command is a query statement, the returned string consists of all the query results concatenated together. If the `max_string_length` parameter was configured in `sql_database_args`, the result will be truncated to this length. This function is particularly convenient for using the concatenated results as input for an LLM.
```python
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

demo_sqldb_wrapper:SQLDBWrapper = SQLDBWrapperManager().get_instance_obj("demo_sqldb_wrapper")
demo_sqldb_wrapper.run_with_str_return("select * from USERS")
```
Example of returned result:
```text
"[(1, 'Alice', 30), (2, 'Bob', 25)]"
```

### sql_database
If you wish to utilize some of the native features of SQLAlchemy or the SQLDatabase, you can access the corresponding objects through the `sql_database` property of the SQLDBWrapper class in the AgentUniverse framework.
```python
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager

demo_sqldb_wrapper:SQLDBWrapper = SQLDBWrapperManager().get_instance_obj("demo_sqldb_wrapper")
sql_database_ins = demo_sqldb_wrapper.sql_database
sql_alchemy_engine = sql_database_ins._engine
```