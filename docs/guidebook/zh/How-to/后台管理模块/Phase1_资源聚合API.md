# Phase 1 资源聚合 API（后台管理模块）

本文档描述 OSPP `#568` Phase 1 提交的后台资源聚合接口，便于前端联调与后续扩展（Trace/Guardrail）。

## 接口前缀

所有接口统一挂载在：

`/api/v1/admin/resources`

## 接口清单

- `GET /summary`：返回资源统计摘要
- `GET /agents`：返回智能体列表
- `GET /tools`：返回工具列表
- `GET /knowledge`：返回知识库列表
- `GET /workflows`：返回工作流列表
- `GET /sessions/<agent_id>`：返回指定智能体的会话列表

## 响应格式

所有接口均复用框架标准响应包装：

```json
{
  "success": true,
  "result": {},
  "message": null,
  "request_id": null
}
```

### `GET /summary` 示例

```json
{
  "success": true,
  "result": {
    "total_agents": 2,
    "total_tools": 5,
    "total_knowledge": 1,
    "total_workflows": 1,
    "system_health": "OK"
  },
  "message": null,
  "request_id": null
}
```

### `GET /agents` 示例

```json
{
  "success": true,
  "result": {
    "total": 2,
    "data": [
      {
        "id": "demo_agent",
        "name": "demo_agent",
        "description": "demo agent",
        "component_type": "AGENT",
        "status": "ACTIVE",
        "diagnostics": null
      }
    ]
  },
  "message": null,
  "request_id": null
}
```

## 联调建议

- 开发环境可通过 Vite 代理将 `/api` 转发到本地 aU 网关。
- `diagnostics` 字段当前预留，Phase 3 Guardrail 启用后可写入风险评分。

## 测试

本次 Phase 1 使用以下命令验证新增逻辑：

```bash
conda run -n au-ospp pytest tests/test_agentuniverse/unit/agent_serve/test_admin_resource_service.py -q
```

结果：`4 passed`（其余 warning 为仓库现有告警，不由本次提交引入）。

