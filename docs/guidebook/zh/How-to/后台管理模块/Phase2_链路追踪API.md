# Phase 2 链路追踪 API（后台管理模块）

本文档描述 Trace 接口，优先从 OpenTelemetry Span 构建会话拓扑，无 Span 时回退 Session 消息序列。

## 接口前缀

`/api/v1/admin/trace`

## 接口清单

- `GET /sessions/<session_id>`：返回指定会话的执行拓扑（nodes / edges / timeline）

## 响应格式

与 Phase 1 相同，复用框架标准响应包装：

```json
{
  "success": true,
  "result": {},
  "message": null,
  "request_id": null
}
```

### `GET /sessions/<session_id>` 示例

```json
{
  "success": true,
  "result": {
    "session_id": "session-1",
    "agent_id": "demo_agent",
    "nodes": [
      {
        "id": "agent-demo_agent",
        "name": "demo_agent",
        "type": "agent",
        "start_time": "2026-04-01 10:00:00",
        "end_time": "2026-04-01 10:05:00",
        "duration": 300000.0,
        "status": "success",
        "error": null
      }
    ],
    "edges": [],
    "timeline": [],
    "data_source": "otel"
  },
  "message": null,
  "request_id": null
}
```

## 数据来源

1. **OTEL（优先）**：读取 `ADMIN_OTEL_SPAN_DIR` 下 span，按 `parent_span_id` 建边，`data_source: "otel"`
2. **Message（回退）**：`SessionService.get_session_detail` + 消息序列节点，`data_source: "message"`

Trace 响应附带 `diagnostics`（Guardrail LPP 雷达数据）。

## 测试

```bash
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_trace_service.py -q
```
