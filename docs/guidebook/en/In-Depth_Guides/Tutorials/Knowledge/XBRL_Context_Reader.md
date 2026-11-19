# XBRL fact context reader

`XbrlContextReader` ingests local XBRL 2.1 **instance XML** as one Document per flat fact. It keeps entity, period, units and dimensions beside every value, including duplicate concepts from different contexts/currencies. It does not calculate, round, aggregate, convert currencies or provide financial conclusions.

Install `pip install "agentUniverse[xbrl_ext]"` (lxml). Direct use:

```python
from agentuniverse.agent.action.knowledge.reader.file.xbrl_context_reader import XbrlContextReader
documents, report = XbrlContextReader().load_instance("report.xbrl")
print(report["taxonomy_validation"], report["unsupported"])
```

Copy `xbrl_context_reader.yaml.example` into your application Reader package as `.yaml`, retaining metadata. Configure Knowledge `readers: {xbrl: xbrl_context_reader}` (add `xml` only when that routing is intended). Then call normal `insert_knowledge(source_path=...)` / `query_knowledge(...)`. The tests exercise YAML → Knowledge → SQLite. `load_data` returns only Documents; use `load_instance` for unsupported-content reporting.

## Evidence contract

Document text is deterministic JSON including expanded concept QName, original value, fact ID, context ID/entity identifier+scheme/period, explicit and typed dimensions, unit numerator/denominator, nil, decimals/precision and inherited language. Numeric values and dates remain lexical strings: no float conversion or implicit rounding. A nil value remains empty and is explicitly flagged, never zero. Typed dimension XML and non-dimensional segment/scenario XML are preserved as strings, not interpreted; namespace declarations may be normalized by lxml.

Reserved metadata `xbrl_evidence` also contains raw file SHA-256, absolute source path, source line, element XPath and fact index. IDs use file digest plus XPath; byte-identical relocated copies retain IDs, any byte change creates a new snapshot. No Store cleanup/synchronization. Caller metadata is deep-copied and cannot overwrite the reserved key.

## Supported boundary

Flat simple-content facts in `.xbrl` / `.xml` with an XBRL instance root are supported. Contexts include instant/duration/forever, segment/scenario, explicit and typed dimensions. Units include products and divisions. Missing context/unit references, duplicate IDs/dimensions, invalid nil and conflicting accuracy fields fail explicitly.

**Taxonomy validation is not performed**, recorded in both report and each fact. Schema references are listed but never loaded, including local files. There is no schema/type validation, dimension-default expansion, calculation/linkbase validation, date lexical validation, taxonomy labels or inferred numeric type. Decimals/precision are recorded claims. Tuple/complex content and linkbase content are reported as unsupported, not flattened. Inline XBRL is rejected; scaling, sign and transformations are not guessed. DTDs are rejected and XML external resolution/network loading are disabled. This is extraction, not a complete XBRL validator or XML sandbox.

## Bounds and verification

Positive integer defaults / maximum settings: `max_file_bytes` 20M/100M, `max_facts` 20,000/100,000, `max_document_chars` 200,000/2M and `max_total_chars` 10M/40M. M is decimal. Limits fail without partial results; XML is bounded but parsed in memory. Limits do not guarantee fixed parser memory or latency.

Tests use real multi-context/multi-currency XML with nil, divided units and typed/explicit dimensions. Arelle 2.36.20 in offline mode independently compares fact names, values, entity, period interpretation, units and dimensions. Its local minimal schemas support extraction classification; this is **not** a standards-conformance/taxonomy-validation test. Tests also cover malformed input, resource bounds, metadata isolation and actual SQLite retrieval. No model or external taxonomy is used.

```sh
pip install lxml==5.4.0 arelle-release==2.36.20
python -m pytest -q --import-mode=importlib tests/test_agentuniverse/unit/agent/action/knowledge/reader/test_xbrl_context_reader.py
```

Reference: [XBRL 2.1 specification](https://specifications.xbrl.org/work-product-index-group-base-spec-base-spec.html).
