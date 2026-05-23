# 向官方仓库提交 PR

Fork：`bosprimigenious/agentUniverse`  
Upstream：`agentuniverse-ai/agentUniverse`

已按 [PR提交指南](./PR提交指南.md) 拆分为 **3 个可独立 Review 的分支**，建议按顺序合并。

## 分支与 Compare 链接

| 顺序 | 分支 | 目标 |
|------|------|------|
| 1 | `feat/admin-phase1-only` | 资源聚合 API |
| 2 | `feat/admin-phase2-trace` | 链路追踪（基于 PR1） |
| 3 | `feat/admin-phase3-monitoring-guardrail` | 监控 + Guardrail + CI + 文档 |

### PR 1 — Phase 1 资源聚合

**Compare（在 GitHub 网页打开）：**

https://github.com/agentuniverse-ai/agentUniverse/compare/master...bosprimigenious:agentUniverse:feat/admin-phase1-only

**标题：** `feat(admin): add zero-invasive resource aggregation APIs`

**Test plan：**

- `pytest tests/test_agentuniverse/unit/agent_serve/test_admin_resource_service.py`
- `GET /api/v1/admin/resources/summary`

---

### PR 2 — Phase 2 链路追踪

**Compare：**

https://github.com/agentuniverse-ai/agentUniverse/compare/feat/admin-phase1-only...bosprimigenious:agentUniverse:feat/admin-phase2-trace

> 若 PR1 已合并到官方 master，将 compare 左侧改为 `master`。

**标题：** `feat(admin): add session trace graph API`

**Test plan：**

- `pytest tests/test_agentuniverse/unit/agent_serve/test_admin_trace_service.py`
- `GET /api/v1/admin/trace/sessions/<session_id>`

---

### PR 3 — Phase 3 监控 + Guardrail

**Compare：**

https://github.com/agentuniverse-ai/agentUniverse/compare/feat/admin-phase2-trace...bosprimigenious:agentUniverse:feat/admin-phase3-monitoring-guardrail

**标题：** `feat(admin): add LLM metrics and guardrail diagnostics APIs`

**Test plan：**

- `pytest tests/test_agentuniverse/unit/agent_serve/test_admin_*.py`（4 个文件，20 用例）
- `GET /api/v1/admin/metrics/llm`
- `GET /api/v1/admin/guardrail/sessions/<session_id>`
- Trace 响应含 `diagnostics`

---

## 一键合并分支（可选）

若维护者接受单 PR，仍可使用原分支：

https://github.com/agentuniverse-ai/agentUniverse/compare/master...bosprimigenious:agentUniverse:feat/admin-resource-phase1

---

## 前端 Dashboard

仓库：`bosprimigenious/au-admin-dashboard`  
分支：`feat-admin-dashboard-task2`

https://github.com/bosprimigenious/au-admin-dashboard/compare/master...feat-admin-dashboard-task2

---

## 本地 upstream 配置

```bash
git remote add upstream https://github.com/agentuniverse-ai/agentUniverse.git
git fetch upstream master
```

## PR 描述模板

见 [PR提交指南.md](./PR提交指南.md) 文末模板；勾选官方 `.github/pull-request-template.md` 检查项并附 pytest 通过说明。
