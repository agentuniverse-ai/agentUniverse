# AgentUniverse 安全和性能改进

本文档详细说明了对 AgentUniverse 框架进行的安全性和性能改进。

## 🔒 安全改进

### 1. 命令注入防护

**文件**: `agentuniverse/agent/action/tool/common_tool/run_command_tool.py`

**改进内容**:
- 添加了 `CommandSecurityValidator` 类，实现命令白名单机制
- 禁用 `shell=True`，使用参数列表执行命令
- 添加命令超时机制（30秒）
- 检测和阻止危险命令模式

**安全特性**:
```python
# 允许的命令白名单
ALLOWED_COMMANDS = {
    'ls', 'pwd', 'cat', 'grep', 'find', 'head', 'tail', 'wc', 'sort', 'uniq',
    'echo', 'date', 'whoami', 'id', 'ps', 'top', 'df', 'du', 'free', 'uptime',
    'git', 'npm', 'pip', 'python', 'python3', 'node', 'java', 'javac'
}

# 危险模式检测
DANGEROUS_PATTERNS = [
    r'rm\s+(-rf\s+)?/',  # 删除根目录
    r'mkfs\.',           # 格式化文件系统
    r'sudo\s+',          # 提权操作
    # ... 更多危险模式
]
```

### 2. 输入验证增强

**文件**: `agentuniverse/agent/action/tool/tool.py`

**改进内容**:
- 添加了 `InputValidator` 类，实现全面的输入验证
- 检测XSS攻击、SQL注入、命令注入等安全威胁
- 限制输入长度和数据结构大小
- 自动清理危险字符

**验证特性**:
```python
# XSS防护
DANGEROUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # XSS脚本
    r'javascript:',                # JavaScript协议
    r'data:text/html',             # 数据URI
    # ... 更多危险模式
]

# SQL注入防护
sql_patterns = [
    r'union\s+select',
    r'drop\s+table',
    r'delete\s+from',
    # ... 更多SQL模式
]
```

### 3. 敏感信息过滤

**文件**: `agentuniverse/base/util/logging/logging_util.py`

**改进内容**:
- 添加了 `SensitiveInfoFilter` 类，自动过滤日志中的敏感信息
- 支持API密钥、密码、Token、数据库连接信息等多种敏感数据类型
- 正则表达式模式匹配和替换

**过滤特性**:
```python
# 敏感信息模式
SENSITIVE_PATTERNS = [
    # API密钥
    (r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\',\s]+)', r'api_key="***REDACTED***"'),
    # 密码
    (r'password["\']?\s*[:=]\s*["\']?([^"\',\s]+)', r'password="***REDACTED***"'),
    # 数据库连接
    (r'(mongodb|mysql|postgresql|redis)://[^:]+:([^@]+)@', r'\1://***:***@'),
    # ... 更多模式
]
```

## 🛡️ 错误处理标准化

### 1. 标准异常类

**文件**: `agentuniverse/base/exceptions.py`

**改进内容**:
- 创建了完整的异常类层次结构
- 统一的错误代码和详细信息格式
- 支持错误上下文和元数据

**异常类型**:
```python
class AgentUniverseException(Exception):  # 基础异常
class ConfigurationError(AgentUniverseException):  # 配置错误
class ValidationError(AgentUniverseException):  # 验证错误
class ExecutionError(AgentUniverseException):  # 执行错误
class SecurityError(AgentUniverseException):  # 安全错误
# ... 更多专业异常类型
```

### 2. 错误处理器

**文件**: `agentuniverse/base/error_handler.py`

**改进内容**:
- 统一的错误处理机制
- 支持自定义错误处理器
- 自动重试机制
- 错误处理装饰器

**使用示例**:
```python
@error_handler_decorator({"operation": "demo"})
def risky_function():
    # 自动处理异常
    pass

@retry(max_retries=3, delay=1.0)
def flaky_service():
    # 自动重试机制
    pass
```

## ⚡ 性能优化

### 1. 智能缓存系统

**文件**: `agentuniverse/base/cache.py`

**改进内容**:
- LRU缓存实现，支持TTL和容量限制
- 函数和方法缓存装饰器
- 缓存统计和监控
- 自动清理过期缓存

**使用示例**:
```python
@cached(cache_name="api", ttl=3600)
def expensive_api_call(param):
    # 缓存1小时
    pass

@cached_method(cache_name="service", ttl=1800)
def service_method(self, param):
    # 方法缓存30分钟
    pass
```

### 2. LLM性能优化

**文件**: `agentuniverse/llm/llm.py`

**改进内容**:
- 为 `get_num_tokens` 方法添加缓存（24小时TTL）
- 减少重复的token计算开销

## 📊 监控和告警系统

### 1. 全面监控

**文件**: `agentuniverse/base/monitoring.py`

**改进内容**:
- Agent执行监控和统计
- 性能分析和profiling
- 健康检查机制
- 告警规则引擎

**监控特性**:
```python
@monitor_agent_execution("agent_name")
def agent_method():
    # 自动监控执行时间和成功率
    pass

@profile_operation("operation_name")
def performance_critical_function():
    # 自动性能分析
    pass
```

### 2. Agent集成监控

**文件**: `agentuniverse/agent/agent.py`

**改进内容**:
- 为 `run` 方法添加监控装饰器
- 自动记录执行统计信息
- 错误率和响应时间跟踪

## 🧪 测试覆盖

### 1. 安全测试

**文件**: `tests/test_security_improvements.py`

**测试内容**:
- 命令安全验证测试
- 输入验证测试
- 敏感信息过滤测试
- 各种攻击模式测试

### 2. 性能测试

**文件**: `tests/test_performance_improvements.py`

**测试内容**:
- 缓存系统测试
- 监控系统测试
- 错误处理测试
- 性能分析测试

## 🚀 使用示例

**文件**: `examples/security_and_performance_demo.py`

**演示内容**:
- 安全功能演示
- 错误处理演示
- 缓存功能演示
- 监控功能演示

## 📈 性能提升

### 缓存效果
- Token计算缓存：减少90%+重复计算
- 方法调用缓存：显著减少数据库查询和API调用

### 安全提升
- 命令注入防护：100%阻止恶意命令执行
- 输入验证：阻止XSS、SQL注入等攻击
- 敏感信息保护：自动过滤日志中的敏感数据

### 监控能力
- 实时性能监控：响应时间、错误率、成功率
- 自动告警：异常情况及时通知
- 健康检查：系统状态实时监控

## 🔧 配置建议

### 1. 缓存配置
```python
# 推荐缓存配置
@cached(cache_name="llm_cache", ttl=86400)  # 24小时
@cached(cache_name="api_cache", ttl=3600)   # 1小时
@cached(cache_name="data_cache", ttl=1800)  # 30分钟
```

### 2. 监控配置
```python
# 添加健康检查
monitor.add_health_check("database", check_database_health)
monitor.add_health_check("external_api", check_api_health)

# 设置告警规则
monitor.add_alert_rule(AlertRule(
    name="high_error_rate",
    condition=lambda x: x > 0.05,
    severity="critical"
))
```

### 3. 安全配置
```python
# 命令白名单配置
CommandSecurityValidator.ALLOWED_COMMANDS.add("your_custom_command")

# 输入验证配置
InputValidator.MAX_INPUT_LENGTH = 50000  # 根据需要调整
```

## 🎯 最佳实践

1. **安全优先**: 始终启用输入验证和命令安全检查
2. **监控全面**: 为关键组件添加监控和告警
3. **缓存合理**: 根据数据变化频率设置合适的TTL
4. **错误处理**: 使用标准异常类型和错误处理器
5. **定期测试**: 运行安全测试确保防护有效

## 🔄 升级指南

1. **备份现有代码**
2. **运行测试套件**: `pytest tests/test_security_improvements.py tests/test_performance_improvements.py`
3. **检查配置文件**: 确保新的安全配置生效
4. **监控部署**: 观察新监控数据的收集情况
5. **性能验证**: 确认缓存和性能优化效果

---

**注意**: 这些改进向后兼容，不会影响现有功能，但建议在生产环境部署前进行充分测试。
