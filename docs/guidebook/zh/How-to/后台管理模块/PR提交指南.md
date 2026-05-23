# 后台管理模块 PR 提交指南

建议将 Admin 模块拆分为 **3 个可独立 Review 的 PR**，降低官方维护者 review 成本。

## PR 1：Phase 1 资源聚合（后端）

**标题建议：** `feat(admin): add zero-invasive resource aggregation APIs`

**包含文件：**

- `agentuniverse_product/service/admin_service/admin_blueprint.py`
- `agentuniverse_product/service/admin_service/resource_service.py`
- `agentuniverse_product/service/admin_service/dto.py`（Resource 相关 DTO）
- `agentuniverse/agent_serve/web/flask_server.py`（注册 admin_bp）
- `tests/test_agentuniverse/unit/agent_serve/test_admin_resource_service.py`
- `docs/guidebook/zh/How-to/后台管理模块/Phase1_资源聚合API.md`

**验收：**

- [ ] `pytest test_admin_resource_service.py` 通过
- [ ] `GET /api/v1/admin/resources/summary` 返回资源计数 + system_health
- [ ] 不修改核心 Agent 执行链路

---

## PR 2：Phase 2 链路追踪（后端）

**标题建议：** `feat(admin): add session trace graph API`

**依赖：** PR 1 合并后基于最新 master rebase

**包含文件：**

- `trace_service.py` / `trace_blueprint.py`
- `dto.py`（Trace DTO 扩展）
- `flask_server.py`（注册 admin_trace_bp）
- `tests/.../test_admin_trace_service.py`
- `Phase2_链路追踪API.md`

**验收：**

- [ ] 任意 session_id 返回 nodes/edges/timeline
- [ ] 空 session 返回空图，不 500

---

## PR 3：Phase 3 监控 + Guardrail（后端）

**标题建议：** `feat(admin): add LLM metrics and guardrail diagnostics APIs`

**包含文件：**

- `monitoring_service.py` / `monitoring_blueprint.py`
- `guardrail_service.py` / `guardrail_blueprint.py`
- `dto.py`（Metrics / Guardrail DTO）
- `resource_service.py`（summary 扩展 today metrics + health）
- 对应 tests + Phase3 文档

**验收：**

- [ ] `GET /metrics/llm` 返回 series + alerts
- [ ] Trace 响应附带 `diagnostics`
- [ ] `GET /guardrail/sessions/<id>` 可独立调用

---

## 前端仓库（au-admin-dashboard）

**标题建议：** `feat: add agentUniverse admin ops center dashboard`

可作为独立仓库 PR 或后续合入 `examples/admin-dashboard`（需与维护者确认归属）。

**页面清单：**

- Overview / Resources / Trace / Monitoring
- Pinia stores + API adapter + Vitest

**联调说明：** 引用后端 PR 合并版本，附 [E2E联调指南](./E2E联调指南.md) 链接。

---

## PR Description 模板

```markdown
## Summary
- 为 agentUniverse 增加零侵入 Admin Blueprint（OSPP #568）
- 提供资源聚合 / 链路追踪 / 监控指标 / Guardrail 诊断能力

## Test plan
- [ ] pytest admin service tests
- [ ] 本地 curl 探活 summary / trace / metrics
- [ ] au-admin-dashboard E2E 演示（Overview → Resources → Monitoring → Trace）

## Notes
- Token 统计当前为 message 估算，后续可接 OTEL
- Guardrail 为启发式 MVP，DTO 稳定后可换真实 LPP 模型
```

---

## 提交前 Checklist

- [ ] 所有 admin 单测通过
- [ ] 前端 `npm run test && npm run build` 通过
- [ ] 文档 Phase1–3 + E2E 指南已更新
- [ ] 无 `.env` / 密钥文件进入 commit
- [ ] commit message 符合仓库 conventional 风格
