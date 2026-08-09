# Auditable financial research workspace

This sample is an offline-first financial research application built on agentUniverse's native
`Tool`, `DocProcessor`, `Document`, `Query`, and `WorkPattern` contracts. It adds the operational
boundaries commonly missing from a notebook demo:

- tenant-isolated SQLite ingestion and jobs;
- bounded deterministic retrieval with stable citation and source hashes;
- a persisted retrieval checkpoint, so interrupted jobs resume without changing evidence;
- built-in `FinancialIndicatorExtractor` and `MMRProcessor` execution;
- optional registered `WorkPattern` execution (including a configured PEER pattern);
- citation precision/recall helpers and network-free fixtures/tests.

## Architecture

```text
local reports -> FinancialResearchWorkspace -> cited evidence
                                               |
                                               v
                          agentUniverse Document / Query
                                               |
                         FinancialIndicatorExtractor -> MMRProcessor
                                               |
                              optional registered WorkPattern (PEER)
```

`FinancialEvidenceTool` exposes ingestion and research through the normal agentUniverse tool
interface. Its YAML lives in `intelligence/agentic/tool/financial_evidence_tool.yaml`.

## Offline quick start

No model key or network call is needed:

```bash
python -m examples.sample_apps.financial_research_app.cli \
  --db /tmp/financial-research.db \
  --tenant demo \
  --ingest examples/sample_apps/financial_research_app/data/sample_company_report.txt \
  --question 'How did revenue and margin change?'
```

The JSON output includes the original citations/provenance and the documents enhanced by the
native financial indicator processor and MMR reranker.

## Registered component mode

Start agentUniverse with the included configuration and resolve the processors through their
managers:

```bash
python -m examples.sample_apps.financial_research_app.cli \
  --config examples/sample_apps/financial_research_app/config/config.toml \
  --db /tmp/financial-research.db --tenant demo \
  --ingest examples/sample_apps/financial_research_app/data/sample_company_report.txt \
  --question 'How did revenue and margin change?'
```

A project that configures planning/executing/expressing/reviewing agents can additionally pass its
registered work-pattern name with `--work-pattern`. The evidence and stable citations are inserted
into the pattern's `InputObject`.

## Tests

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
  examples/sample_apps/financial_research_app/intelligence/test/test_workspace.py
```

Tests cover tenant isolation, bounds, checkpoint resume, metric extraction, MMR, work-pattern
input, YAML component configuration, and the `FinancialEvidenceTool` adapter. They never call a
hosted model or market-data service.

For production, replace the local retriever with an agentUniverse `Store`, keep the citation and
tenant boundaries, use an authenticated service, and configure a PEER work pattern plus approved
market-data tools such as `YahooFinanceTool`.
