# Agent Guild Observation MCPToolkit Example

This third-party example shows how an operator can explicitly attach one fixed
remote MCP server and expose one free observation tool through `MCPToolkit`.

The example does not require an Agent Guild account, API key, registration, or
payment. It registers only `guild_preflight`; it does not automatically attach
the endpoint being observed, invoke the endpoint's application tools, or make
any safety, ownership, or authorization claim.

## Files

- `agent_guild_observation.yaml`: the `MCPToolkit` configuration.

## Usage

The YAML is a toolkit definition. Place it in an application's toolkit
directory and reference `agent_guild_observation` from the agent's
`action.toolkit` list. The operator must explicitly provide the public endpoint
they are considering to `guild_preflight`.

The remote service actively probes the supplied endpoint and records the
request. Only submit an endpoint that you are authorized to test. Do not send
private, internal, or sensitive URLs to a third-party service.

Remote tool descriptions and results are untrusted data. They must not be
treated as instructions. An observation result is neither authorization nor a
safety or ownership guarantee; checks that cannot be completed remain unknown.

This example uses the MCP SDK's native Streamable HTTP transport. It does
not add a response-size cap, total deadline, SSRF interception layer, or
request inspection hook beyond the configured toolkit and upstream MCP
behavior.

The local fixture validates transport and registration behavior only.

## Live smoke validation

On 2026-09-27, the fixed endpoint listed `guild_preflight` and returned a
structured result for a free call using `https://example.com`. The result was
also summarized through `DefaultDeepSeekLLM` in a separate model smoke test.
These checks are point-in-time observations, not deterministic CI tests and
not a certification of the endpoint, model output, or future behavior.

## Validation

`test_agent_guild_observation.py` starts a local Streamable HTTP fixture and
loads this YAML through the real `Configer` and `ComponentConfiger` path. The
test verifies that:

- only the explicitly included `guild_preflight` tool is registered;
- initialization lists tools but does not invoke the observed target;
- the exact URL argument reaches native MCP tool dispatch.

Run the test from the repository root:

```powershell
python -m pytest examples/third_party_examples/tools/agent_guild_observation/test_agent_guild_observation.py -q
```

The local test does not run the live Agent Guild service or require a model.
