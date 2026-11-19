# Reproduction and local test evidence

![Historical local JUnit report, not hosted CI](report.png)

feat(embedding): add pinned local CPU CLIP image and text vectors

This directory makes the previously reported local evidence reviewable. **It is not a GitHub CI result.** The tested implementation commit is `aa112046713df2c9fa225147e86c92fd76e37330`. Subsequent evidence/documentation-only commits do not turn these historical runs into fresh executions.

## Reproduce

Install Python 3.10+ and [uv](https://docs.astral.sh/uv/getting-started/installation/), then from the repository root run:

```sh
python tests/reproduction/local-clip-embedding/reproduce.py --python 3.10
python tests/reproduction/local-clip-embedding/reproduce.py --python 3.12
```

Use `--dry-run` to inspect commands without installing or executing anything. The runner uses a scoped dependency environment, not a full-project installation. It records resolved package versions, actual pytest output and JUnit in a fresh temporary directory; `--output-dir` can select a separate directory. Do not overwrite the checked-in historical evidence. Dependencies without `==` were not fully locked in the original runs; the new environment record allows differences to be inspected, rather than pretending the old environment was hermetic.

## Prerequisites and limits

Download the approved openai/clip-vit-base-patch32 snapshot at revision 3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268 using the instructions in docs/design/local_clip_embedding.md. Set HF_HUB_OFFLINE=1 for validation. Torch 2.6.0 CPU was used. A model cache and substantial RAM are prerequisites; no paid service or GPU is required. The 3-image fixture is not a relevance benchmark.

## Historical evidence

| Python | Tests | Failures | Errors | Skips | JUnit |
| --- | ---: | ---: | ---: | ---: | --- |
| 3.12 | 21 | 0 | 0 | 0 | [junit-py3.12.xml](junit-py3.12.xml) |
| 3.10 | 21 | 0 | 0 | 0 | [junit-py3.10.xml](junit-py3.10.xml) |

`evidence.json` includes the original local JUnit SHA-256 values. Shared regressions and repeated Python environments are not independent new tests. Host-name attributes were removed for privacy; case results and original timestamps are retained. The timestamp fields have no explicit timezone, so no timezone is inferred.

Open `report.html` to inspect the rendered summary. The accompanying report screenshot is a capture of that actual JUnit-derived report, not a terminal screenshot or proof of hosted CI. See the feature guide and PR for unsupported cases. Full-repository CI, merge acceptance and competition scores are not claimed.

中文：这里公开真实本地测试记录与跨目录复现入口，明确关联被测提交。历史记录不是刚重跑的结果，也不是上游CI。只有关键依赖固定版本，原环境不是完整锁文件；复现时另存实际环境与输出。未包含真实用户数据或付费模型调用。
