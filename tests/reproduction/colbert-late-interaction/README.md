# ColBERT reproduction

Prepare the public fixed-revision model cache as described in
[the guide](../../../docs/guidebook/en/In-Depth_Guides/Tutorials/Knowledge/ColBERT_Reranker.md).
No weights are checked into this repository. Then from the repository root:

```sh
python tests/reproduction/colbert-late-interaction/reproduce.py --python 3.10
python tests/reproduction/colbert-late-interaction/reproduce.py --python 3.12
```

Install Python and [uv](https://docs.astral.sh/uv/) first. The runner records the
actual resolved environment, pytest log, JUnit and summary in a fresh temporary
directory (`--output-dir` can select another); `--dry-run` only shows commands.
It uses scoped dependencies, not the full repository installation or a complete
transitive lock. `HF_HUB_OFFLINE=1` is set for tests; missing model/dependencies
fail rather than silently skipping the real-model tests.

Expected current scope: **35 tests** per Python version, including 26 new cases
and 9 existing processor-pipeline regressions. Real weights, actual token tensors,
official/scalar arithmetic oracles, concurrent copies, budgets, YAML/manager,
SQLite reopen and public Knowledge query are exercised. This is CPU/Windows local
evidence, not hosted CI, full-project validation, GPU or multilingual validation.

## Controlled retrieval smoke experiment

Three authored English queries and twelve authored documents, one designated
relevant document per query, are compared against rank-bm25 and input order.
JUnit stores each reciprocal rank and NDCG@10; it also records warm-model elapsed
time, actual matrix bounds and whole-process RSS before/after calls. RSS snapshots
are not peak or component-only memory. Timing excludes download/load and depends
on hardware and other work. The first query does not rank its target first.

This tiny fixture checks reproducibility, not general superiority, real-business
quality or competition value. Tests do not assert an improvement over BM25.
Screenshots render these real JUnit summaries; they are not fabricated terminal
captures. Only machine hostnames are removed; original hashes are recorded.

## Checked-in evidence

[Machine-readable results and original hashes](evidence.json) · [rendered report](report.html) · [actual report screenshot](report.png)

| Environment / scope | Passed | Failed | Errors | Skipped | Raw JUnit | Resolved environment |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Windows 3.10 real model + pipeline | 35 | 0 | 0 | 0 | [XML](junit-windows-py310.xml) | [versions](environment-windows-py310.json) |
| Windows 3.12 real model + pipeline | 35 | 0 | 0 | 0 | [XML](junit-windows-py312.xml) | [versions](environment-windows-py312.json) |

Implementation source snapshot: `a3b675311af74ea47e3a945af32969d15e3b146a`. This commit was recorded after the runs, with the tested production and test contents unchanged. Evidence files are added in a later documentation commit.
