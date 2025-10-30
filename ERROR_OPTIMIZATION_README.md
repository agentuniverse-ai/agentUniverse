# AgentUniverse 错误信息优化

## 概述

本次优化旨在改善AgentUniverse项目中的错误信息，让错误原因更加直观和有用。通过统一的异常处理机制，用户可以获得更清晰的错误描述、具体的解决建议和详细的上下文信息。

## 主要改进

### 1. 统一的异常处理基类

创建了 `AgentUniverseException` 基类，提供标准化的错误信息格式：

- **错误代码系统**: 每个错误都有唯一的错误代码（如 `AU_CONFIG_1001`）
- **错误严重程度**: 低、中、高、严重四个级别
- **错误分类**: 配置、服务、工具、LLM、工作流等分类
- **详细描述**: 包含错误的具体原因和上下文
- **解决建议**: 提供具体的修复步骤和指导
- **多语言支持**: 支持中英文错误信息

### 2. 配置文件加载错误优化

**位置**: `agentuniverse/base/config/`

**改进内容**:
- 文件不存在时提供绝对路径和检查建议
- 格式不支持时列出支持的格式类型
- 解析错误时提供具体的错误行号和修复建议
- 区分不同类型的解析错误（YAML、TOML、编码等）

**示例**:
```python
# 之前
raise ValueError(f"Unsupported file format: {file_format}")

# 现在
raise UnsupportedConfigFormatError(
    file_path=path,
    file_format=file_format,
    details={"supported_formats": ["yaml", "toml"]},
    suggestions=["将文件转换为支持的格式", "参考配置文件示例"]
)
```

### 3. 服务管理错误优化

**位置**: `agentuniverse/agent_serve/`

**改进内容**:
- 服务未找到时提供可用服务列表
- 服务初始化失败时提供依赖检查建议
- 服务执行错误时提供参数验证和状态检查建议

**示例**:
```python
# 之前
raise ServiceNotFoundError(service_code)

# 现在
raise ServiceNotFoundError(
    service_code=service_code,
    available_services=available_services,
    details={"service_manager_type": type(service_manager).__name__},
    suggestions=["检查服务代码是否正确", "确认服务是否已注册"]
)
```

### 4. 工具执行错误优化

**位置**: `agentuniverse/agent/action/tool/`

**改进内容**:
- 工具未找到时提供可用工具列表
- 参数错误时列出缺失的参数和类型要求
- API工具根据HTTP状态码提供具体的错误原因
- 超时错误提供网络检查和重试建议

**示例**:
```python
# 之前
raise Exception(f"Request failed with status code {response.status_code}")

# 现在
raise ToolExecutionError(
    tool_id="API_TOOL",
    execution_error=f"HTTP请求失败，状态码: {response.status_code}",
    details={"status_code": response.status_code, "url": str(response.url)},
    suggestions=["检查API端点是否正确", "验证认证信息是否有效"]
)
```

### 5. LLM调用错误优化

**位置**: `agentuniverse/llm/`

**改进内容**:
- 连接错误提供网络和配置检查建议
- 认证错误提供API密钥验证指导
- 速率限制错误提供配额和重试建议
- 模型未找到时提供可用模型列表

**示例**:
```python
# 之前
LOGGER.error(f'Error in LLM call: {e}')
raise e

# 现在
if "connection" in str(e).lower():
    raise LLMConnectionError(
        model_name=self.model_name,
        connection_error=str(e),
        details={"model_name": self.model_name, "temperature": self.temperature},
        suggestions=["检查模型连接配置", "验证网络连接是否正常"]
    )
```

### 6. 工作流节点错误优化

**位置**: `agentuniverse/workflow/node/`

**改进内容**:
- 节点未找到时提供可用节点列表
- 工具/Agent执行失败时提供详细的上下文信息
- 输出类型错误时提供期望的类型说明

**示例**:
```python
# 之前
raise ValueError("No tool with id {} was found.".format(tool_id))

# 现在
raise ToolNotFoundError(
    tool_id=tool_id,
    available_tools=available_tools,
    details={"workflow_id": self.workflow_id, "node_id": self.id},
    suggestions=["检查工具ID是否正确", "确认工具是否已注册"]
)
```

### 7. 全局异常处理优化

**位置**: `agentuniverse/agent_serve/web/flask_server.py`

**改进内容**:
- 根据异常类型返回不同的错误信息
- 提供用户友好的错误页面
- 包含错误代码和解决建议
- 区分不同类型的系统错误

## 错误代码系统

### 配置相关错误 (1000-1999)
- `AU_CONFIG_1001`: 配置文件未找到
- `AU_CONFIG_1002`: 配置文件解析错误
- `AU_CONFIG_1003`: 不支持的配置文件格式
- `AU_CONFIG_1004`: 配置文件验证错误

### 服务相关错误 (2000-2999)
- `AU_SERVICE_2001`: 服务未找到
- `AU_SERVICE_2002`: 服务初始化错误
- `AU_SERVICE_2003`: 服务执行错误

### 工具相关错误 (3000-3999)
- `AU_TOOL_3001`: 工具未找到
- `AU_TOOL_3002`: 工具执行错误
- `AU_TOOL_3003`: 工具参数错误
- `AU_TOOL_3004`: 工具执行超时

### LLM相关错误 (4000-4999)
- `AU_LLM_4001`: LLM连接错误
- `AU_LLM_4002`: LLM认证错误
- `AU_LLM_4003`: LLM速率限制错误
- `AU_LLM_4004`: LLM模型未找到
- `AU_LLM_4005`: LLM执行错误

### 工作流相关错误 (5000-5999)
- `AU_WORKFLOW_5001`: 工作流节点未找到
- `AU_WORKFLOW_5002`: 工作流执行错误
- `AU_WORKFLOW_5003`: 工作流验证错误
- `AU_WORKFLOW_5004`: 工作流图错误

## 使用示例

### 创建自定义异常

```python
from agentuniverse.base.exception import AgentUniverseException, AgentUniverseErrorCode

# 创建自定义异常
exc = AgentUniverseException(
    error_code=AgentUniverseErrorCode.CONFIG_FILE_NOT_FOUND,
    message="配置文件未找到",
    severity=ErrorSeverity.HIGH,
    category=ErrorCategory.CONFIGURATION,
    details={"file_path": "/path/to/config.yaml"},
    suggestions=["检查文件路径是否正确", "确认文件是否存在"]
)

# 获取用户友好的错误消息
print(exc.get_user_friendly_message("zh"))
```

### 处理异常

```python
try:
    # 一些可能出错的操作
    config.load()
except ConfigFileNotFoundError as e:
    print(f"错误代码: {e.error_code.value}")
    print(f"错误消息: {e.message}")
    print(f"解决建议: {e.suggestions}")
    print(f"详细信息: {e.details}")
```

## 测试

运行测试用例验证错误信息优化：

```bash
python -m pytest tests/test_agentuniverse/unit/base/exception/test_error_optimization.py -v
```

## 贡献指南

### 添加新的异常类型

1. 在 `agentuniverse/base/exception/` 目录下创建新的异常文件
2. 继承 `AgentUniverseException` 基类
3. 在 `AgentUniverseErrorCode` 枚举中添加新的错误代码
4. 提供详细的错误描述和解决建议
5. 添加相应的测试用例

### 修改现有异常

1. 保持向后兼容性
2. 添加更详细的错误信息
3. 提供具体的解决建议
4. 更新相关的测试用例

## 总结

通过这次错误信息优化，AgentUniverse项目现在能够：

1. **提供更直观的错误信息**: 用户能够快速理解错误原因
2. **给出具体的解决建议**: 帮助用户快速修复问题
3. **包含详细的上下文信息**: 便于问题排查和调试
4. **支持多语言错误信息**: 提升国际化用户体验
5. **统一的错误处理机制**: 保持代码的一致性和可维护性

这些改进将显著提升用户体验，减少问题排查时间，让开发者能够更高效地使用AgentUniverse框架。
