# Scholarly Evidence Research Agent

This sample application shows how to compose agentUniverse's built-in PubMed,
Crossref, and Semantic Scholar tools into one traceable evidence-research workflow.
It performs query-time retrieval only: no crawler, vector database, or local corpus
is required.

## Why this sample is useful

The three sources expose different identifiers and metadata shapes. Passing their
raw responses directly to an LLM creates duplicate papers, inconsistent citations,
and hidden coverage gaps. `ScholarlyEvidenceTool` provides a small orchestration
layer that:

- searches all three sources concurrently and isolates source failures;
- normalizes DOI, PMID, Semantic Scholar paper ID, authors, dates, and URLs;
- deduplicates by DOI, then PMID, with normalized title as a fallback;
- preserves every contributing source and its record URL;
- caps source results, evidence count, text lengths, and author count; and
- assigns stable `E1`, `E2`, ... identifiers for grounded synthesis.

Title-only records cannot bridge two works with conflicting DOI or PMID values.
Identifier compatibility is checked again after each merge. A malformed source or
PDF URL is omitted without discarding otherwise usable evidence; a valid DOI or
PMID can still provide a fallback source URL.

The agent prompt requires source-status disclosure, evidence-ID citations, explicit
uncertainty, and a warning that metadata or abstracts are not full-text appraisal.

## Architecture

```text
research question
       |
       v
ScholarlyEvidenceTool
  |-- PubMedTool ---------|
  |-- CrossrefTool -------|--> normalize --> deduplicate --> bounded evidence
  `-- SemanticScholarTool-|
                                              |
                                              v
                                  ReAct evidence synthesis agent
```

## Setup

From the repository root, install agentUniverse following the main project guide.
Set `DASHSCOPE_API_KEY` in the environment or replace the placeholder in
`config/custom_key.toml`. The scholarly sources work without keys. Optional
`NCBI_EMAIL`, `NCBI_API_KEY`, `CROSSREF_EMAIL`, and `S2_API_KEY` values improve
request identification or rate limits.

Do not commit real credentials.

## Run the offline tests

The tests mock network retrieval and need no API key:

```bash
cd examples/sample_apps
python -m unittest scholarly_research_app.intelligence.test.test_scholarly_evidence_tool
```

## Run an interactive evidence brief

```bash
cd examples/sample_apps
python -m scholarly_research_app.intelligence.test.scholarly_research_agent_demo
```

Enter a complete question, for example:

```text
What evidence links sleep duration with cognitive decline in older adults?
```

## Start the web server

```bash
cd examples/sample_apps
python -m scholarly_research_app.bootstrap.intelligence.server_application
```

The default agentUniverse web server listens on `http://localhost:8888`.

## Tool output contract

`source_status` distinguishes `ok`, `empty`, and `error` for every source.
`evidence` contains only bounded, deduplicated records. Each record includes an
`evidence_id`, normalized metadata, `identifiers`, `sources`, and `source_urls`.
`truncated` signals that additional deduplicated records were omitted.

This is a discovery and synthesis example, not a systematic-review pipeline. A
real review still needs protocol design, reproducible source-specific search
strategies, screening, full-text retrieval, risk-of-bias assessment, and domain
expert judgment. Health-related output is informational, not medical advice.

Chinese documentation: [README_zh.md](README_zh.md)
