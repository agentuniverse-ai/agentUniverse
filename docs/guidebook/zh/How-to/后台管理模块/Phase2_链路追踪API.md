# Phase 2 链路追踪 API（后台管理模块）

本文档描述 Trace MVP 接口，基于 Session 消息构建会话级拓扑图，供前端 G6 渲染。

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
    "timeline": []
  },
  "message": null,
  "request_id": null
}
```

## 数据来源

- 会话详情：`SessionService.get_session_detail`
- 节点构建：Agent 入口节点 + 消息序列节点（message/llm 交替类型）
- 后续可替换为 OpenTelemetry Span 解析，无需变更前端 DTO

## 测试

```bash
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_trace_service.py -q
```
