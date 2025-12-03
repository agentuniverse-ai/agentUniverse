# PR 信息 / PR Information

## 测试文件路径和测试结果 / Test Files and Results

### 测试文件路径 / Test File Paths

- `tests/test_agentuniverse/unit/base/util/test_monitor.py`

### 测试覆盖范围 / Test Coverage

新增的测试文件包含以下测试用例：

1. **`test_get_llm_statistics_empty`** - 测试空数据情况下的LLM统计查询
2. **`test_get_agent_statistics_empty`** - 测试空数据情况下的Agent统计查询
3. **`test_get_llm_statistics_with_data`** - 测试带数据的LLM统计查询
4. **`test_get_agent_statistics_with_data`** - 测试带数据的Agent统计查询
5. **`test_get_llm_statistics_with_date_filter`** - 测试带日期过滤的LLM统计查询
6. **`test_get_llm_statistics_with_source_filter`** - 测试带source过滤的LLM统计查询
7. **`test_estimate_cost`** - 测试成本估算功能
8. **`test_get_daily_summary`** - 测试每日汇总功能
9. **`test_trace_agent_invocation_with_token_usage`** - 测试Agent调用记录中的token使用量

### 运行测试 / Running Tests

```bash
# 运行所有监控相关测试
python -m pytest tests/test_agentuniverse/unit/base/util/test_monitor.py -v

# 运行特定测试
python -m pytest tests/test_agentuniverse/unit/base/util/test_monitor.py::MonitorTest::test_estimate_cost -v
```

### 测试结果说明 / Test Results Note

**注意**: 测试需要安装项目依赖（包括 `jsonlines` 和 `loguru`）。如果环境中缺少依赖，部分测试会自动跳过（使用 `skipTest`）。

测试使用临时目录来隔离测试数据，不会影响实际的监控数据目录。

---

## 新增或修改的文档 / Added or Modified Documentation

### 修改的文档 / Modified Documents

1. **`docs/guidebook/zh/token_usage_monitor.md`**
   - 新增了"Agent 调用记录增强"章节
   - 新增了"内置统计查询功能"章节，包含：
     - LLM 调用统计 (`get_llm_statistics`)
     - Agent 调用统计 (`get_agent_statistics`)
     - 每日汇总 (`get_daily_summary`)
   - 新增了"成本估算功能"章节
   - 新增了"完整示例：生成每日统计报告"章节
   - 更新了"推荐的使用姿势"章节

### 文档内容概览 / Documentation Overview

文档详细说明了以下新功能：

1. **统计查询功能**
   - `Monitor.get_llm_statistics()` - 按时间、模型等维度统计LLM调用
   - `Monitor.get_agent_statistics()` - 按时间、Agent等维度统计Agent调用
   - `Monitor.get_daily_summary()` - 获取每日汇总

2. **成本估算功能**
   - `Monitor.estimate_cost()` - 基于token价格估算成本

3. **增强的监控记录**
   - Agent调用记录现在包含token使用量和性能指标

4. **完整示例代码**
   - 提供了生成每日统计报告的完整示例代码

---

## 代码变更摘要 / Code Changes Summary

### 修改的文件 / Modified Files

1. **`agentuniverse/base/util/monitor/monitor.py`**
   - 增强了 `trace_agent_invocation` 方法，添加了token使用量和性能指标记录
   - 新增 `get_llm_statistics()` 方法：LLM调用统计查询
   - 新增 `get_agent_statistics()` 方法：Agent调用统计查询
   - 新增 `estimate_cost()` 方法：成本估算
   - 新增 `get_daily_summary()` 方法：每日汇总

### 新增的功能 / New Features

1. **统计查询功能**
   - 支持按时间范围过滤
   - 支持按source（模型/Agent）过滤
   - 自动计算平均响应时间等性能指标
   - 按source分组统计

2. **成本估算功能**
   - 支持分别设置prompt和completion的token价格
   - 基于token使用量计算成本

3. **增强的监控记录**
   - Agent调用记录包含完整的token使用信息
   - Agent调用记录包含性能指标（响应时间）

---

## 使用示例 / Usage Examples

### 统计查询示例

```python
from agentuniverse.base.util.monitor.monitor import Monitor

monitor = Monitor()

# 查询所有LLM调用统计
stats = monitor.get_llm_statistics()

# 按时间范围查询
stats = monitor.get_llm_statistics(
    start_date="2025-12-01",
    end_date="2025-12-03"
)

# 查询特定模型的统计
stats = monitor.get_llm_statistics(source="openai_gpt_4o")
```

### 成本估算示例

```python
token_usage = {
    "prompt_tokens": 1000,
    "completion_tokens": 500
}

cost = monitor.estimate_cost(
    token_usage,
    prompt_price_per_1k=0.01,
    completion_price_per_1k=0.03
)
```

### 每日汇总示例

```python
# 获取今天的汇总
summary = monitor.get_daily_summary()

# 获取指定日期的汇总
summary = monitor.get_daily_summary("2025-12-01")
```

