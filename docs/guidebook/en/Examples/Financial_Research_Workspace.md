# Financial research workspace example

See `examples/sample_apps/financial_research_app`. It demonstrates reproducible local ingestion,
bounded retrieval, citations, provenance, tenant isolation and resumable jobs. The evidence is
converted into native `Document`/`Query` objects, processed by `FinancialIndicatorExtractor` and
`MMRProcessor`, and can be passed to a registered PEER `WorkPattern`. The included YAML also
registers the workspace as `FinancialEvidenceTool`; all automated tests run without network calls.
