# SSRF 代理环境变量

`APITool` 等基于 HTTP 的工具在发起外网请求时会经过 `agentuniverse.agent.action.tool.utils.ssrf_proxy`，便于在部署侧通过 HTTP 代理约束 SSRF（服务端请求伪造）风险。

## 环境变量

| 变量 | 说明 |
|------|------|
| `SSRF_PROXY_ALL_URL` | 全协议共用的代理地址（如 `http://127.0.0.1:3128`），对应 httpx 的 `proxy=` 参数。 |
| `SSRF_PROXY_HTTP_URL` | 仅用于 `http://` 的代理，须与 `SSRF_PROXY_HTTPS_URL` 同时配置才启用分协议模式。 |
| `SSRF_PROXY_HTTPS_URL` | 仅用于 `https://` 的代理，须与 `SSRF_PROXY_HTTP_URL` 同时配置才启用分协议模式。 |

若设置了 `SSRF_PROXY_ALL_URL`，则优先于分协议变量。

## 行为说明

- 默认超时 **20 秒**，调用方可在请求中传入 `timeout` 覆盖。
- 未配置任何代理变量时，请求直连目标地址。
- 分协议模式要求 `SSRF_PROXY_HTTP_URL` 与 `SSRF_PROXY_HTTPS_URL` **均非空**；否则不会启用分协议代理。

## 示例

```bash
export SSRF_PROXY_HTTP_URL=http://127.0.0.1:3128
export SSRF_PROXY_HTTPS_URL=http://127.0.0.1:3128
```

配置后，经 `ssrf_proxy` 访问外部 API 的插件工具会走上述代理。

## 相关代码

- 实现：`agentuniverse/agent/action/tool/utils/ssrf_proxy.py`
- 主要调用方：`agentuniverse/agent/action/tool/api_tool.py`
