# Token Usage 日志功能增强总结

## 概述
为 AgentUniverse 的监控系统增加了详细的 LLM Token Usage 日志记录功能，使开发者能够更好地追踪和分析 LLM 调用的成本和使用情况。

## 实现的功能

### 1. 新增 LogTypeEnum 枚举值
- **文件**: `agentuniverse/base/util/logging/log_type_enum.py`
- **新增**: `llm_token_usage = 'llm_token_usage'`
- **作用**: 为 token usage 日志提供专门的日志类型标识

### 2. 增强 Monitor.trace_llm_token_usage() 方法
- **文件**: `agentuniverse/base/util/monitor/monitor.py`
- **功能**: 在每次 LLM token usage 更新时输出详细日志
- **日志内容**:
  - 当前调用的 token usage
  - 累积的 token usage
  - 格式化的摘要信息

### 3. 增强 Monitor.trace_llm_invocation() 方法
- **文件**: `agentuniverse/base/util/monitor/monitor.py`
- **功能**: 在 LLM 调用完成时输出包含 token usage 的详细日志
- **日志内容**:
  - 调用来源
  - 当前 token usage 统计
  - 详细的 token usage 分解信息
  - 执行耗时

### 4. 新增格式化方法

#### `_format_token_usage_summary(token_usage: dict) -> str`
- **功能**: 将 token usage 数据格式化为简洁的摘要字符串
- **格式**: `"Input: X, Output: Y, Total: Z"`
- **兼容性**: 支持新格式 (`prompt_tokens`/`completion_tokens`) 和旧格式 (`text_in`/`text_out`)

#### `_format_token_usage_details(token_usage: dict) -> dict`
- **功能**: 将 token usage 数据格式化为详细的结构化字典
- **返回内容**:
  ```json
  {
    "input_tokens": 100,
    "output_tokens": 50,
    "total_tokens": 150,
    "raw_usage": {...}
  }
  ```

## 日志输出示例

### LLM Token Usage 更新日志
```
INFO - LLM Token Usage Updated: Input: 100, Output: 50, Total: 150
```
**绑定的结构化数据**:
- `log_type`: `llm_token_usage`
- `current_token_usage`: 当前调用的 token 使用情况
- `cumulative_token_usage`: 累积的 token 使用情况
- `context_prefix`: 上下文前缀信息

### LLM 调用日志
```
INFO - LLM Invocation - Source: openai_llm, Token Usage: Input: 100, Output: 50, Total: 150
```
**绑定的结构化数据**:
- `log_type`: `llm_invocation`
- `used_token`: 当前累积的 token 使用情况
- `token_details`: 详细的 token 分解信息
- `cost_time`: 调用耗时
- `llm_output`: LLM 输出内容

## 技术特性

### 1. 数据格式兼容性
- 自动识别并支持两种 token usage 数据格式
- 向前兼容旧版本的数据结构

### 2. 条件日志记录
- 只在 `log_activate=True` 时输出日志
- 遵循现有的日志配置系统

### 3. 结构化日志
- 使用 loguru 的 bind 机制提供结构化数据
- 便于日志分析和监控系统集成

### 4. 性能友好
- 轻量级的格式化方法
- 不影响现有的监控流程性能

## 配置说明

### 启用/禁用日志记录
```python
# 在配置文件中设置
MONITOR = {
    'log_activate': True,  # 启用详细日志记录
    'activate': False      # 文件监控功能（独立配置）
}
```

### 使用方式
无需额外配置，功能会在以下情况自动触发：
1. LLM 调用完成时（通过 `trace_llm_invocation`）
2. Token usage 更新时（通过 `trace_llm_token_usage`）

## 测试验证

已通过测试验证的功能：
- ✅ 格式化方法的正确性
- ✅ 空数据处理
- ✅ 新旧格式兼容性
- ✅ Monitor 类的实例化
- ✅ LLM token usage 计算集成

## 使用场景

1. **成本监控**: 实时追踪 LLM API 调用的 token 消耗
2. **性能优化**: 分析不同 LLM 调用的 token 效率
3. **调试分析**: 快速定位 token 使用异常的调用
4. **审计合规**: 记录详细的 LLM 使用日志供审计使用

## 注意事项

1. **日志量**: 启用详细日志后会增加日志输出量，建议在生产环境中合理配置日志级别
2. **存储空间**: 结构化日志数据相对占用更多存储空间
3. **依赖项**: 确保 `jsonlines` 包已正确安装（项目依赖中已包含）
