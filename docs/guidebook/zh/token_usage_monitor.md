## Token 使用量监控与统计说明

本篇文档介绍 AgentUniverse 中 **LLM Token 使用量** 的监控方案，包括：

- **在线调用返回中的 token 统计结果**
- **落盘到 `monitor` 目录下的调用明细 jsonl 文件**
- **内置的统计查询与成本估算功能**
- **如何基于这些数据做简单的离线统计分析**

---

### 一、整体机制概览

框架在 LLM 调用链路中已经内置了以下能力：

- **调用链跟踪**：通过 `Monitor.init_invocation_chain_bak()` / `Monitor.get_invocation_chain_bak()` 等方法，在一次 agent 对话中记录完整的调用链。
- **Token 使用量聚合**：`Monitor.init_token_usage()` 初始化上下文中本次请求的 token 统计，通过 `Monitor.add_token_usage()` 逐次累加；调用结束时可通过 `Monitor.get_token_usage()` 拿到最终结果。
- **OTel 指标**：`agentuniverse.base.tracing.otel.instrumentation.llm.LLMInstrumentor` 中已经对 token 使用量暴露了多项 metrics，便于通过 Prometheus / 其他后端系统统一采集。

本次扩展在此基础上做了以下优化：

1. **统一在 LLM 调用日志中带出 token 使用量**（字段 `used_token`）。
2. **在开启 Monitor 的情况下，将 LLM 调用明细（含 token 使用量）按小时写入 jsonl 文件**，方便后续离线统计。
3. **增强 Agent 调用记录**：Agent 调用记录中也包含 token 使用量和性能指标。
4. **内置统计查询功能**：提供 `get_llm_statistics()` 和 `get_agent_statistics()` 方法，支持按时间、模型、Agent 等维度聚合统计。
5. **成本估算功能**：提供 `estimate_cost()` 方法，基于 token 价格估算使用成本。
6. **每日汇总功能**：提供 `get_daily_summary()` 方法，快速获取指定日期的统计汇总。

---

### 二、Monitor 配置与开关

`Monitor` 的核心实现位于：

- `agentuniverse/base/util/monitor/monitor.py`

关键配置字段：

- **`dir`**：监控数据落盘目录，默认 `./monitor`
- **`activate`**：是否开启落盘到 jsonl 文件的能力（包括 agent 与 llm）
- **`log_activate`**：是否在日志系统中输出结构化日志

通常通过框架的 `Configer` 来注入配置，例如（伪代码）：

```python
MONITOR = {
    "dir": "./monitor",
    "activate": True,
    "log_activate": True,
}
```

只要 `activate=True`，则本次新增的 LLM 调用明细也会一并落盘。

---

### 三、在线调用返回中的 Token 使用量

在产品层的 `AgentService` 中，已经对 token 使用量做了一次聚合，并回传给调用方：

- 代码位置：`agentuniverse_product/service/agent_service/agent_service.py`
- 相关方法：
  - `chat(...)`
  - `stream_chat(...)`
  - `async_stream_chat(...)`

调用 `chat` 时的典型返回结构（简化）：

```python
result = AgentService.chat(agent_id, session_id, input)

print(result.keys())
# dict_keys(['response_time', 'message_id', 'session_id', 'output',
#            'start_time', 'end_time', 'invocation_chain', 'token_usage'])

token_usage = result["token_usage"]
```

其中：

- **`token_usage`** 为一个字典，来源于 `LLMOutput.usage.to_dict()` 的统计结果，主要字段包括：
  - `prompt_tokens`
  - `completion_tokens`
  - `total_tokens`
  - 以及 `prompt_tokens_details` / `completion_tokens_details` 中的细分字段

在不依赖任何落盘文件的前提下，你可以直接在业务层拿到本次对话整体的 token 使用量。

---

### 四、LLM 调用明细 jsonl 文件

为支持更灵活的 **离线统计与分析**，`Monitor.trace_llm_invocation` 做了增强：

- 代码位置：`agentuniverse/base/util/monitor/monitor.py`
- 方法签名：

```python
@staticmethod
def trace_llm_invocation(
    source: str,
    llm_input: Union[str, dict],
    llm_output: Union[str, dict],
    cost_time: float = None,
) -> None:
    ...
```

增强后的行为包括两部分：

1. **输出结构化日志**

   日志中会包含：

   - `log_type=LogTypeEnum.llm_invocation`
   - `used_token=Monitor.get_token_usage()` —— 当前 trace 下聚合后的 token 使用量
   - `cost_time`：本次 LLM 调用耗时
   - `llm_output`：模型输出文本/数据

2. **在 Monitor.activate=True 时写入 jsonl 文件**

   - 子目录：`{monitor.dir}/llm_invocation`
   - 文件命名：`llm_{source}_YYYY-MM-DD-HH.jsonl`
   - 每条记录的结构示例：

   ```json
   {
     "source": "openai_gpt_4o",
     "date": "2025-12-03 10:23:45",
     "llm_input": { "...": "..." },
     "llm_output": "模型返回的文本或结构化结果",
     "token_usage": {
       "prompt_tokens": 123,
       "completion_tokens": 456,
       "total_tokens": 579,
       "prompt_tokens_details": {
         "text_tokens": 123
       },
       "completion_tokens_details": {
         "text_tokens": 456
       }
     },
     "cost_time": 1.234
   }
   ```

这样，你可以非常方便地：

- 按 **模型/时间/业务 source** 做 token 使用量统计
- 对比不同模型或 prompt 策略下的 token 成本与响应耗时

> 注意：写入 jsonl 依赖 `jsonlines` 包，如未安装会抛出：
> `jsonlines is required to trace llm invocation: pip install jsonlines`

---

### 五、Agent 调用记录增强

从本次优化开始，`Monitor.trace_agent_invocation` 方法也会记录 token 使用量和性能指标：

- 代码位置：`agentuniverse/base/util/monitor/monitor.py`
- Agent 调用记录的文件结构示例：

```json
{
  "source": "my_agent",
  "date": "2025-12-03 10:23:45",
  "agent_input": { "...": "..." },
  "agent_output": { "...": "..." },
  "token_usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  },
  "cost_time": 2.345
}
```

这样，你可以同时追踪 Agent 和 LLM 两个层面的 token 使用情况。

---

### 六、内置统计查询功能

框架提供了便捷的统计查询方法，无需手动解析 jsonl 文件。

#### 6.1 LLM 调用统计

```python
from agentuniverse.base.util.monitor.monitor import Monitor

monitor = Monitor()

# 查询所有 LLM 调用的统计
stats = monitor.get_llm_statistics()

# 按时间范围查询
stats = monitor.get_llm_statistics(
    start_date="2025-12-01",
    end_date="2025-12-03"
)

# 查询特定模型的统计
stats = monitor.get_llm_statistics(source="openai_gpt_4o")

# 返回结果示例
{
    "total_calls": 200,
    "total_tokens": 100000,
    "total_prompt_tokens": 60000,
    "total_completion_tokens": 40000,
    "avg_cost_time": 1.234,
    "by_source": {
        "openai_gpt_4o": {
            "calls": 120,
            "tokens": 60000,
            "prompt_tokens": 36000,
            "completion_tokens": 24000,
            "avg_cost_time": 1.5
        },
        "zhipu_glm_4": {
            "calls": 80,
            "tokens": 40000,
            "prompt_tokens": 24000,
            "completion_tokens": 16000,
            "avg_cost_time": 0.9
        }
    }
}
```

#### 6.2 Agent 调用统计

```python
# 查询所有 Agent 调用的统计
agent_stats = monitor.get_agent_statistics()

# 按时间范围查询
agent_stats = monitor.get_agent_statistics(
    start_date="2025-12-01 00:00:00",
    end_date="2025-12-01 23:59:59"
)

# 查询特定 Agent 的统计
agent_stats = monitor.get_agent_statistics(source="my_agent")

# 返回结果示例
{
    "total_calls": 50,
    "total_tokens": 50000,
    "avg_cost_time": 2.5,
    "by_source": {
        "my_agent": {
            "calls": 50,
            "tokens": 50000,
            "avg_cost_time": 2.5
        }
    }
}
```

#### 6.3 每日汇总

```python
# 获取今天的汇总
summary = monitor.get_daily_summary()

# 获取指定日期的汇总
summary = monitor.get_daily_summary("2025-12-01")

# 返回结果示例
{
    "date": "2025-12-01",
    "llm": {
        "total_calls": 200,
        "total_tokens": 100000,
        ...
    },
    "agent": {
        "total_calls": 50,
        "total_tokens": 50000,
        ...
    }
}
```

---

### 七、成本估算功能

框架提供了基于 token 价格的成本估算方法：

```python
# 假设 token 使用量
token_usage = {
    "prompt_tokens": 1000,
    "completion_tokens": 500,
    "total_tokens": 1500
}

# 估算成本（假设 prompt 每 1k tokens 0.01 元，completion 每 1k tokens 0.03 元）
cost = monitor.estimate_cost(
    token_usage,
    prompt_price_per_1k=0.01,    # 每 1000 个 prompt tokens 的价格
    completion_price_per_1k=0.03  # 每 1000 个 completion tokens 的价格
)

print(f"估算成本: {cost:.4f} 元")
# 输出: 估算成本: 0.0250 元
```

结合统计查询功能，可以计算一段时间内的总成本：

```python
# 获取统计结果
stats = monitor.get_llm_statistics(start_date="2025-12-01", end_date="2025-12-03")

# 计算总成本（假设使用 GPT-4 的价格）
total_cost = 0.0
for source, source_stats in stats["by_source"].items():
    token_usage = {
        "prompt_tokens": source_stats["prompt_tokens"],
        "completion_tokens": source_stats["completion_tokens"]
    }
    # 根据不同的模型设置不同的价格
    if "gpt_4" in source:
        cost = monitor.estimate_cost(token_usage, 0.03, 0.06)
    else:
        cost = monitor.estimate_cost(token_usage, 0.01, 0.03)
    total_cost += cost

print(f"总成本: {total_cost:.2f} 元")
```

---

### 八、简单的离线统计示例

下面给出一个独立脚本示例，展示如何基于 `monitor/llm_invocation/*.jsonl` 做按模型聚合的 token 统计。

> 该脚本不在框架内置，只是一个使用参考。你可以将它保存为项目中的 `scripts/token_usage_report.py` 或自行调整。

```python
import glob
import json
from collections import defaultdict
from pathlib import Path

MONITOR_DIR = Path("./monitor/llm_invocation")


def load_records():
    for path in glob.glob(str(MONITOR_DIR / "llm_*.jsonl")):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue


def aggregate_by_source():
    stats = defaultdict(lambda: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "count": 0})

    for record in load_records():
        source = record.get("source", "unknown")
        usage = record.get("token_usage") or {}

        prompt = usage.get("prompt_tokens", 0)
        completion = usage.get("completion_tokens", 0)
        total = usage.get("total_tokens", prompt + completion)

        stats[source]["prompt_tokens"] += prompt
        stats[source]["completion_tokens"] += completion
        stats[source]["total_tokens"] += total
        stats[source]["count"] += 1

    return stats


if __name__ == "__main__":
    result = aggregate_by_source()
    for source, s in result.items():
        print(f"[{source}] calls={s['count']}, "
              f"prompt_tokens={s['prompt_tokens']}, "
              f"completion_tokens={s['completion_tokens']}, "
              f"total_tokens={s['total_tokens']}")
```

运行示例：

```bash
python scripts/token_usage_report.py
```

输出示例：

```text
[openai_gpt_4o] calls=120, prompt_tokens=34567, completion_tokens=8910, total_tokens=43477
[zhipu_glm_4]  calls=80,  prompt_tokens=21000, completion_tokens=5600, total_tokens=26600
```

---

### 九、推荐的使用姿势

- **在线监控**：
  - 通过现有的 OTel 指标（`LLM_TOTAL_TOKENS` / `LLM_PROMPT_TOKENS` / `LLM_COMPLETION_TOKENS` 等）接入 Prometheus / Grafana 做实时监控与告警。
- **快速统计查询**：
  - 使用 `Monitor.get_llm_statistics()` 和 `Monitor.get_agent_statistics()` 方法，无需手动解析 jsonl 文件，即可获取聚合统计结果。
- **成本核算**：
  - 开启 `Monitor.activate=True`，使用 `get_llm_statistics()` 获取统计结果，结合 `estimate_cost()` 方法计算成本。
  - 使用 `get_daily_summary()` 快速生成每日成本报告。
- **业务优化**：
  - 对比不同 Agent/Workflow/Prompt 版本在 token 使用量和响应耗时上的差异，优化整体性价比。
  - 通过 `by_source` 字段分析不同模型或 Agent 的使用情况。

如果你有更个性化的统计需求（例如：按用户 ID / 业务线 / 场景标签等维度拆分），可以在业务调用时通过：

- 自定义 `source` 字段（不同的 agent 或场景定义不同的 source）
- 在 `llm_input` 中附带额外的业务标识

然后在离线统计脚本中根据这些字段做更细粒度的聚合分析，或者扩展 `Monitor` 类添加自定义的统计方法。

---

### 十、完整示例：生成每日统计报告

下面是一个完整的示例，展示如何使用新增的统计功能生成每日报告：

```python
from agentuniverse.base.util.monitor.monitor import Monitor
from datetime import datetime, timedelta

def generate_daily_report(date_str: str = None):
    """生成指定日期的统计报告"""
    monitor = Monitor()
    
    # 获取每日汇总
    summary = monitor.get_daily_summary(date_str)
    
    print("=" * 60)
    print(f"日期: {summary['date']}")
    print("=" * 60)
    
    # LLM 统计
    llm_stats = summary['llm']
    print("\n【LLM 调用统计】")
    print(f"  总调用次数: {llm_stats['total_calls']}")
    print(f"  总 Token 数: {llm_stats['total_tokens']:,}")
    print(f"  Prompt Tokens: {llm_stats['total_prompt_tokens']:,}")
    print(f"  Completion Tokens: {llm_stats['total_completion_tokens']:,}")
    print(f"  平均响应时间: {llm_stats['avg_cost_time']:.2f} 秒")
    
    print("\n  按模型分组:")
    for source, stats in llm_stats['by_source'].items():
        print(f"    [{source}]")
        print(f"      调用次数: {stats['calls']}")
        print(f"      Token 数: {stats['tokens']:,}")
        print(f"      平均响应时间: {stats['avg_cost_time']:.2f} 秒")
    
    # Agent 统计
    agent_stats = summary['agent']
    print("\n【Agent 调用统计】")
    print(f"  总调用次数: {agent_stats['total_calls']}")
    print(f"  总 Token 数: {agent_stats['total_tokens']:,}")
    print(f"  平均响应时间: {agent_stats['avg_cost_time']:.2f} 秒")
    
    print("\n  按 Agent 分组:")
    for source, stats in agent_stats['by_source'].items():
        print(f"    [{source}]")
        print(f"      调用次数: {stats['calls']}")
        print(f"      Token 数: {stats['tokens']:,}")
        print(f"      平均响应时间: {stats['avg_cost_time']:.2f} 秒")
    
    # 成本估算（示例）
    print("\n【成本估算】")
    total_cost = 0.0
    for source, stats in llm_stats['by_source'].items():
        token_usage = {
            "prompt_tokens": stats['prompt_tokens'],
            "completion_tokens": stats['completion_tokens']
        }
        # 根据模型类型设置价格（示例）
        if "gpt_4" in source:
            cost = monitor.estimate_cost(token_usage, 0.03, 0.06)
        elif "gpt_3" in source:
            cost = monitor.estimate_cost(token_usage, 0.0015, 0.002)
        else:
            cost = monitor.estimate_cost(token_usage, 0.01, 0.03)
        total_cost += cost
        print(f"  [{source}]: {cost:.4f} 元")
    
    print(f"\n  总成本: {total_cost:.2f} 元")
    print("=" * 60)


if __name__ == "__main__":
    # 生成今天的报告
    generate_daily_report()
    
    # 生成指定日期的报告
    # generate_daily_report("2025-12-01")
```

运行示例：

```bash
python scripts/daily_report.py
```

输出示例：

```text
============================================================
日期: 2025-12-03
============================================================

【LLM 调用统计】
  总调用次数: 200
  总 Token 数: 100,000
  Prompt Tokens: 60,000
  Completion Tokens: 40,000
  平均响应时间: 1.23 秒

  按模型分组:
    [openai_gpt_4o]
      调用次数: 120
      Token 数: 60,000
      平均响应时间: 1.50 秒
    [zhipu_glm_4]
      调用次数: 80
      Token 数: 40,000
      平均响应时间: 0.90 秒

【Agent 调用统计】
  总调用次数: 50
  总 Token 数: 50,000
  平均响应时间: 2.50 秒

  按 Agent 分组:
    [my_agent]
      调用次数: 50
      Token 数: 50,000
      平均响应时间: 2.50 秒

【成本估算】
  [openai_gpt_4o]: 4.2000 元
  [zhipu_glm_4]: 1.3000 元

  总成本: 5.50 元
============================================================
```


