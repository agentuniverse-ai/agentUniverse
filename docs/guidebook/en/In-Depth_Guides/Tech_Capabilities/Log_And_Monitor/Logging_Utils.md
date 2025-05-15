# Logging Utils

The log component of agentUniverse is implemented based on loguru, offering a well-packaged global log component and customizable log components. This tutorial will first introduce the usage of the log configuration file within agentUniverse, then sequentially explain the utilization of the global log component and customizable log components, and finally describe how to integrate with external log service components.
    
## Log Configuration

### Configuration File Path
The configuration path of the log file is specified in the main configuration of AgentUniverse, config.toml.
```toml
[SUB_CONFIG_PATH]
# Log config file path, an absolute path or a relative path based on the dir where the current config file is located.
log_config_path = './log_config.toml'
```
  If this parameter is a relative path, it refers to the directory that contains the main configuration file, config.toml. If this parameter does not exist, agentUniverse will use the default log configuration, see [default configuration](#default-configuration).

### Configuration File Options
The configuration file for logs is in the toml file format. An example configuration is as follows:
```toml
[LOG_CONFIG]
[LOG_CONFIG.BASIC_CONFIG]
log_level = "INFO"
log_path = "~/.agent_universe_log"
log_rotation = "100 MB"
log_retention = "7 days"
```
- **`log_level`**: The default log level, possible values include "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL". The global log component's level will default to this value. When creating a custom log component and a log level is not specified, this default level will be utilized.
- **`log_path`**: The log storage path, if this value is empty, a {workdir}/../../logs folder will be created as the log storage path.
- **`log_rotation`**: This parameter accepts a duration (e.g., "1 week") or file size (e.g., "100 MB"), indicating the condition for log file rotation.
- **`log_retention`**: This parameter accepts a duration (e.g., "7 days") specifying the retention period for old log files, which will be deleted after they expire.

### Default Configuration
Configuration setting not specified in the log configuration file will default to the following values:
- **`log_level`**: "INFO"
- **`log_rotation`**: "10MB"
- **`log_retention`**: "3 days"

Two default log files, `au_all.log` and `au_error.log`, will be located in the log storage path. The au_all.logfile records all logs above the default log level specified in the log configuration file, while the au_error.log file records only logs at the ERROR level and above. The format for log component is:
```python
log_format: str = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
                       "| <level>{level: <8}</level> "
                       "| {extra[context_prefix]} "
                       "| <cyan>{name}</cyan>"
                       ":<cyan>{function}</cyan>"
                       ":<cyan>{line}</cyan> "
                       "| <level>{message}</level>")
```
Where `{extra[context_prefix]}` defaults to `default`, and if `LOG_CONTEXT` exists in the framework context, its contents will be used to replaced the default contents.  For more information related to the framework context, please refer to  the  [Framework_Context](../Others/Framework_Context.md) documentation.

## Global Log Component
agentUniverse provides a directly usable log component  `logging_util.Logger`, which you can integrate into your project as follows:
```python
from agentuniverse.base.util.logging.logging_util import LOGGER
```
You can utilize this object's various member functions to record logs of different severity levels:
```python
from agentuniverse.base.util.logging.logging_util import LOGGER

LOGGER.info("This is an info log.")
LOGGER.debug("This is a debug log.")
LOGGER.warn("This is a warn log.")
LOGGER.error("This is an error log.")
```

## Custom Log Components
If you wish to output and save specific logs separately, you can create a customized log component by utilizing the `get_module_logger` function:
```python
from agentuniverse.base.util.logging.logging_util import get_module_logger
new_logger = get_module_logger("new_module")
```
Logs recorded by this newly created component will be stored in the designated log storage path, within a log file named `au_{module_name}.log`. Here, `{module_name}` represents the module name you provided to the `get_module_logger`function. For instance,  in the example provided above, the corresponding log file would be named `au_new_module.log`.

## External Log Service

If you want to use more log utils, please refer to [extension logging utils](Alibaba_Cloud_SLS.md).
