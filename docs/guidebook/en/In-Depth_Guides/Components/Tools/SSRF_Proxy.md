# SSRF proxy environment variables

`APITool` and related HTTP-based tools route outbound requests through `agentuniverse.agent.action.tool.utils.ssrf_proxy`. This helps deployments enforce an SSRF (Server-Side Request Forgery) guardrail by forcing traffic through a controlled HTTP proxy.

## Variables

| Variable | Purpose |
|----------|---------|
| `SSRF_PROXY_ALL_URL` | Single proxy URL for all schemes (for example `http://127.0.0.1:3128`). Uses httpx `proxy=`. |
| `SSRF_PROXY_HTTP_URL` | Proxy for `http://` requests. Must be set together with `SSRF_PROXY_HTTPS_URL` for split-scheme mode. |
| `SSRF_PROXY_HTTPS_URL` | Proxy for `https://` requests. Must be set together with `SSRF_PROXY_HTTP_URL` for split-scheme mode. |

If `SSRF_PROXY_ALL_URL` is set, it takes precedence over the per-scheme pair.

## Behavior

- Default request timeout is **20 seconds** unless the caller passes `timeout` in the tool request.
- When no proxy variables are set, requests go directly to the target URL.
- Split-scheme configuration requires **both** `SSRF_PROXY_HTTP_URL` and `SSRF_PROXY_HTTPS_URL` to be non-empty; otherwise per-scheme proxies are not enabled.

## Example

```bash
export SSRF_PROXY_HTTP_URL=http://127.0.0.1:3128
export SSRF_PROXY_HTTPS_URL=http://127.0.0.1:3128
```

After this, plugin tools that call external APIs through `ssrf_proxy` use the proxy for both HTTP and HTTPS.

## Related code

- Implementation: `agentuniverse/agent/action/tool/utils/ssrf_proxy.py`
- Primary consumer: `agentuniverse/agent/action/tool/api_tool.py`
