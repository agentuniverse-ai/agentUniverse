# 后台管理模块文档索引

基于 agentUniverse 的多智能体后台管理模块（OSPP #568）。

## 快速入口

- [E2E 联调指南](./E2E联调指南.md) — 本地启动与 5 分钟演示路径
- [PR 提交指南](./PR提交指南.md) — 分批 PR 策略与 Checklist
- [提交官方 PR](./提交官方PR.md) — upstream Compare 链接与描述模板

## 分阶段 API 文档

| 阶段 | 文档 | 能力 |
|------|------|------|
| Phase 1 | [资源聚合 API](./Phase1_资源聚合API.md) | Resources / Summary / Sessions 列表 |
| Phase 2 | [链路追踪 API](./Phase2_链路追踪API.md) | Session 拓扑图 |
| Phase 3 | [监控指标 API](./Phase3_监控指标API.md) | LLM metrics + 告警 |
| Phase 3 | [Guardrail 诊断 API](./Phase3_Guardrail诊断API.md) | LPP 雷达 diagnostics |
| Phase 4 | [鉴权 RBAC](./Phase4_鉴权RBAC.md) | Bearer Token + 角色层级 |

## 前端仓库

独立前端：`au-admin-dashboard`（Vue 3 Ops Center），详见该仓库 README。
