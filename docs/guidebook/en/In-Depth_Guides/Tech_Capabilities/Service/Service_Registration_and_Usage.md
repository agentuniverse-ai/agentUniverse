# Service

agentUniverse enables developers to register completed Agents as services using a straightforward template definition. This functionality allows for the utilization of the corresponding Agent services via Web API calls once the built-in web server has been launched.

## Registration Method

### Step1: Configure Scan Path
agentUniverse automatically registers service configuration files by scanning configured paths during application startup. The scanning paths are specified in the `config.toml` file:
```toml
[CORE_PACKAGE]
default = ['default_scan_path']
service = ['service_scan_path']
```
By default, agentUniverse scans all paths under both default and service directories, with the path configuration under service having higher priority than that under default.

### Step2: Configuration File
```yaml
name: 'service_name'
description: 'description of the service'
agent: 'agent_name'
metadata:
  type: 'SERVICE'
```
- **`name`**: The name of the Service, which must be provided when invoking the service through the Web API.
- **`description`**: A description of the Service's functionality.
- **`agent`**: The name of the Agent associated with this Service. For more information about Agents, please refer to the Agent documentation.
- **`metadata`**: This field indicates that this configuration is intended for a Service; no modifications are required.

## Usage
Please refer to [Web API](Web_Api.md).

For programmatic registration after application configuration is loaded,
`service.service_code` returns the same qualified identifier as
`service.get_instance_code()`, for example `my_app.service.chat`. It derives
the identifier from the current application and service name when accessed,
including a name assigned by service YAML initialization. Constructing a
`Service` object does not require application configuration to be loaded yet.
