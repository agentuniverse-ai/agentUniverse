# Reproduction and local test evidence

![Historical local JUnit report, not hosted CI](report.png)

feat(knowledge): retrieve bounded relational schema context

This directory makes the previously reported local evidence reviewable. **It is not a GitHub CI result.** The tested implementation commit is `4cbbf82ddf5d68edfdf3f2cc9f3dce2ff92f74e2`. Subsequent evidence/documentation-only commits do not turn these historical runs into fresh executions.

## Reproduce

Install Python 3.10+ and [uv](https://docs.astral.sh/uv/getting-started/installation/), then from the repository root run:

```sh
python tests/reproduction/relational-schema-retrieval/reproduce.py --python 3.10
python tests/reproduction/relational-schema-retrieval/reproduce.py --python 3.12
```

Use `--dry-run` to inspect commands without installing or executing anything. The runner uses a scoped dependency environment, not a full-project installation. It records resolved package versions, actual pytest output and JUnit in a fresh temporary directory; `--output-dir` can select a separate directory. Do not overwrite the checked-in historical evidence. Dependencies without `==` were not fully locked in the original runs; the new environment record allows differences to be inspected, rather than pretending the old environment was hermetic.

## Prerequisites and limits

Use a disposable PostgreSQL 17 database and set AU_SCHEMA_POSTGRES_URL to its SQLAlchemy URL. The suite also creates temporary SQLite databases. PostgreSQL tests create/drop unique fixture schemas; never point this at a production database. Example: docker run -d --name au-schema-repro -e POSTGRES_PASSWORD=local_test_only -e POSTGRES_DB=au_test -p 127.0.0.1:15440:5432 postgres:17; set AU_SCHEMA_POSTGRES_URL=postgresql+psycopg2://postgres:local_test_only@127.0.0.1:15440/au_test. Remove only your disposable container after testing.

## Historical evidence

| Python | Tests | Failures | Errors | Skips | JUnit |
| --- | ---: | ---: | ---: | ---: | --- |
| 3.10 | 31 | 0 | 0 | 0 | [junit-py3.10.xml](junit-py3.10.xml) |
| 3.12 | 31 | 0 | 0 | 0 | [junit-py3.12.xml](junit-py3.12.xml) |

`evidence.json` includes the original local JUnit SHA-256 values. Shared regressions and repeated Python environments are not independent new tests. Host-name attributes were removed for privacy; case results and original timestamps are retained. The timestamp fields have no explicit timezone, so no timezone is inferred.

Open `report.html` to inspect the rendered summary. The accompanying report screenshot is a capture of that actual JUnit-derived report, not a terminal screenshot or proof of hosted CI. See the feature guide and PR for unsupported cases. Full-repository CI, merge acceptance and competition scores are not claimed.

中文：这里公开真实本地测试记录与跨目录复现入口，明确关联被测提交。历史记录不是刚重跑的结果，也不是上游CI。只有关键依赖固定版本，原环境不是完整锁文件；复现时另存实际环境与输出。未包含真实用户数据或付费模型调用。
