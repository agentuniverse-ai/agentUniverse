# Phase 3 监控指标 API（后台管理模块 MVP）

本文档描述 LLM 监控接口，优先从 OpenTelemetry LLM Span 读取真实 Token，无 Span 时回退 Session 消息估算。

## 接口前缀

`/api/v1/admin/metrics`

## 接口清单

- `GET /llm?start=&end=`：返回 LLM 调用趋势、汇总统计与简单告警

## 响应示例

```json
{
  "success": true,
  "result": {
    "series": [
      { "ts": "2026-04-01", "calls": 12, "tokens": 480 },
      { "ts": "2026-04-02", "calls": 8, "tokens": 320 }
    ],
    "total_calls": 20,
    "total_tokens": 800,
    "data_source": "otel",
    "alerts": [
      {
        "level": "warning",
        "message": "Today's token usage is more than 2x the recent daily average."
      }
    ]
  }
}
```

## 数据来源

1. **OTEL（优先）**：读取 `ADMIN_OTEL_SPAN_DIR` 下 `llm/*.json`，使用 `au.llm.usage.total_tokens`
2. **Message 估算（回退）**：消息表按 `gmt_created` 分桶，`tokens ≈ chars / 4`

响应字段 `data_source` 为 `otel` 或 `message_estimate`。环境变量 `ADMIN_OTEL_SPAN_ENABLED=0` 可强制回退。

- `summary` 接口额外返回 `total_llm_calls_today` 与 `total_tokens_today`

## 测试

```bash
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_monitoring_service.py -q
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_otel_span_reader.py -q
```
