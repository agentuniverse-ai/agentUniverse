# 后台管理模块 E2E 联调指南

本文档说明如何在本地同时启动 agentUniverse 后端与 `au-admin-dashboard` 前端，完成端到端演示。

## 1. 仓库与分支

| 仓库 | 建议分支 | 说明 |
|------|----------|------|
| `agentUniverse` | `feat/admin-resource-phase1` | Admin Blueprint（resources / trace / metrics / guardrail） |
| `au-admin-dashboard` | `feat-admin-dashboard-task2` | Vue3 Ops Center 前端 |

## 2. 环境要求

- Python 3.10+
- Node.js 20+
- 已安装并可运行的 agentUniverse 示例应用（含 Product 注册与可选 Session DB）

## 3. 启动后端

在 agentUniverse 示例工程目录中启动 Flask 网关（端口默认 `8000`）：

```bash
# 示例：sample_standard_app 或你的业务工程
python bootstrap/intelligence/server_application.py
```

确认以下 Blueprint 已注册（`flask_server.py`）：

- `/api/v1/admin/resources/*`
- `/api/v1/admin/trace/*`
- `/api/v1/admin/metrics/*`
- `/api/v1/admin/guardrail/*`

### 快速探活

```bash
curl http://127.0.0.1:8000/api/v1/admin/resources/summary
curl http://127.0.0.1:8000/api/v1/admin/metrics/llm
```

期望响应包装：

```json
{ "success": true, "result": { ... }, "message": null, "request_id": null }
```

## 4. 启动前端

```bash
cd au-admin-dashboard
npm install
npm run dev
```

Vite 已将 `/api` 代理到 `http://127.0.0.1:8000`（见 `vite.config.ts`）。

浏览器访问：`http://127.0.0.1:5173`

## 5. 演示路径（建议 5 分钟）

| 步骤 | 页面 | 验证点 |
|------|------|--------|
| 1 | `/overview` | 6 张卡片数字与 `GET /resources/summary` 一致 |
| 2 | `/resources` | Agents/Tools/Knowledge/Workflows 四类筛选均有数据 |
| 3 | `/monitoring` | LLM 趋势图 + 告警流来自 `GET /metrics/llm` |
| 4 | `/trace/<agentId>` | 左侧 sessions 列表来自 `GET /resources/sessions/<agentId>` |
| 5 | 选中 session | G6 拓扑 + Timeline + LPP 雷达来自 trace `diagnostics` |

## 6. 全量 API 清单

### Resources（Phase 1）

- `GET /api/v1/admin/resources/summary`
- `GET /api/v1/admin/resources/agents`
- `GET /api/v1/admin/resources/tools`
- `GET /api/v1/admin/resources/knowledge`
- `GET /api/v1/admin/resources/workflows`
- `GET /api/v1/admin/resources/sessions/<agent_id>`

### Trace（Phase 2）

- `GET /api/v1/admin/trace/sessions/<session_id>`

### Monitoring（Phase 3）

- `GET /api/v1/admin/metrics/llm?start=&end=`

### Guardrail（Phase 3）

- `GET /api/v1/admin/guardrail/sessions/<session_id>`

> Trace 响应中的 `diagnostics` 字段与 Guardrail 独立接口结构一致。

## 7. system_health 规则

| 条件 | 返回值 |
|------|--------|
| 至少 1 个 Agent | `OK` |
| 无 Agent 但有其他资源 | `WARNING` |
| 无任何资源 | `DEGRADED` |

前端会将 `OK/WARNING/DEGRADED` 规范化为 `healthy/degraded/unknown` 展示。

## 8. OpenTelemetry Span 接入（可选）

当应用启用 `SpanJsonExporter`（默认目录 `./monitor`）时，Admin 模块优先读取 OTEL Span：

| 环境变量 | 说明 | 默认 |
|----------|------|------|
| `ADMIN_OTEL_SPAN_DIR` | Span JSON 根目录 | `./monitor` |
| `ADMIN_OTEL_SPAN_ENABLED` | 设为 `0` 强制回退 message 估算 | `1` |

- 监控响应 `data_source: "otel"` 时使用 `au.llm.usage.total_tokens`
- 链路响应 `data_source: "otel"` 时按 Span 父子关系建图

## 9. 测试命令

### 后端

```bash
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_resource_service.py -q
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_trace_service.py -q
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_monitoring_service.py -q
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_otel_span_reader.py -q
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_guardrail_service.py -q
```

### 前端

```bash
cd au-admin-dashboard
npm run test
npm run type-check
npm run build
```

## 9. 常见问题

**Q: Overview 全是 0？**  
A: 确认后端示例应用已启动且 ProductManager 已扫描到 Agent/Tool 等资源。

**Q: Trace 页 sessions 为空？**  
A: 需要先对目标 Agent 产生会话数据（Session DB 未初始化时会返回空列表，不会报错）。

**Q: Monitoring 无趋势？**  
A: 无 OTEL Span 且无 message 时显示 info 告警；启用 SpanJsonExporter 后检查 `data_source` 是否为 `otel`。

**Q: 前端报 Network Error？**  
A: 检查后端 `:8000` 是否存活，或 `.env` 中 `VITE_API_BASE_URL` 是否配置正确。

## 10. 相关文档

- [Phase1_资源聚合API](./Phase1_资源聚合API.md)
- [Phase2_链路追踪API](./Phase2_链路追踪API.md)
- [Phase3_监控指标API](./Phase3_监控指标API.md)
- [Phase3_Guardrail诊断API](./Phase3_Guardrail诊断API.md)
- [PR提交指南](./PR提交指南.md)
