# Admin API 鉴权与 RBAC

Admin 模块默认**不启用**鉴权（本地联调零配置）。生产环境通过环境变量开启 Bearer Token RBAC。

## 环境变量

| 变量 | 说明 | 默认 |
|------|------|------|
| `ADMIN_AUTH_ENABLED` | 设为 `1` 启用鉴权 | `0` |
| `ADMIN_API_TOKENS` | `token:role` 逗号分隔，如 `abc:admin,xyz:viewer` | 空 |
| `ADMIN_API_TOKEN` | 单 Token 快捷配置（角色为 `admin`） | 空 |

## 角色层级

`viewer` < `developer` < `admin` < `super_admin`

当前所有 Admin 路由均为 `GET`，最低需要 `viewer`。后续写操作将要求 `admin`。

## 接口

- `GET /api/v1/admin/auth/me` — 返回 `{ role, auth_enabled }`

## 状态码

| 场景 | HTTP |
|------|------|
| 未携带 Token（鉴权开启） | 401 |
| Token 无效 | 401 |
| 角色不足 | 403 |

## 前端

在浏览器 localStorage 设置 `admin_token`，或通过 Dashboard 顶栏 Token 输入框保存；请求层自动附加 `Authorization: Bearer <token>`。

## 测试

```bash
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_auth_service.py -q
```
