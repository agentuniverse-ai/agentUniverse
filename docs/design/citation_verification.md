# Exact citation verification against supplied snapshots

Register `citation_verifier_tool.yaml` as a normal tool. The real ToolManager
loads its config/class and supports run, async_run and LangChain JSON input.
Example:

```python
from agentuniverse.agent.action.tool.common_tool import CitationVerifierTool

result = CitationVerifierTool().execute(
    sources={"manual-v1": "Voltage: 12 V."},
    citations=[{"source_id": "manual-v1", "start": 9, "end": 13,
                "quote": "12 V"}],
)
assert result["all_verified"]
```

Supply an optional `source_sha256` on each citation to detect a changed source
snapshot. The digest is SHA-256 over the exact source string encoded as UTF-8.
Offsets are zero-based Unicode-codepoint indices, end-exclusive. Preserve
newlines and normalization from the source used to create offsets; UTF-16
browser offsets and byte offsets must be converted by the caller. No fuzzy
matching, Unicode normalization, whitespace correction or offset search occurs.

The ordered result codes are `verified`, `invalid_citation`, `source_missing`,
`source_changed`, `span_out_of_bounds` and `quote_mismatch`. Malformed records
remain counted. Empty citation lists are not reported as all verified. Invalid
top-level input and resource limits raise ValueError before checking citations.
The output contains indexes/statuses only, not source text or quote copies.
Framework tracing can still record tool inputs: configure logging appropriately
before passing sensitive source material.

The four capacity settings must be positive integers (not booleans or numeric
strings). The public configuration initializer validates them before modifying
the tool instance; invalid reconfiguration leaves its existing settings intact.

This is **provenance consistency**, not a factuality/entailment judge. A quote
can match and still be false, outdated or irrelevant. Caller-supplied fabricated
sources can also match: the tool does not fetch/authenticate sources, read URLs,
verify publication ownership or independently establish source credibility.
It verifies character spans, not PDF page-number assertions. One JSON mapping
key identifies one snapshot; use distinct source IDs for distinct versions.

The existing CitationExtractor extracts markers from text; this tool instead
checks externally supplied quotations against explicit source snapshots.
No network, filesystem access, LLM call or new dependency is introduced.

## 中文
本工具核对引文、来源 ID 和字符区间是否一致，可选用原文哈希识别来源变更。
它不证明事实正确、来源可信或引文支持结论，也不把无引用的结果判为验证成功。
重复出现的引文必须分别提供准确位置。输出不复制原文，但框架追踪仍可能
记录输入，因此敏感材料要配合日志策略。通过真实 ToolManager 注册及同步、
异步、LangChain 入口验证，而不是只测试内部字符串比较函数。
