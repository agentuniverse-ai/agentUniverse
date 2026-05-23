# Phase 3 监控指标 API（后台管理模块 MVP）

本文档描述 LLM 监控接口的首版实现，基于 Session 消息聚合估算调用量与 Token 消耗。

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

- 消息表 `message` 按 `gmt_created` 分桶
- `calls` = 消息条数
- `tokens` = 内容长度估算（chars / 4）
- `summary` 接口额外返回 `total_llm_calls_today` 与 `total_tokens_today`

## 测试

```bash
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_monitoring_service.py -q
```
