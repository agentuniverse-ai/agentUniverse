# Protocol history reproduction

From the repository root, with Python and [uv](https://docs.astral.sh/uv/) installed:

```sh
python tests/reproduction/protocol-history-bridge/reproduce.py --python 3.10
python tests/reproduction/protocol-history-bridge/reproduce.py --python 3.12
```

The runner uses a scoped dependency environment, captures the actual resolved
versions, logs, JUnit and summary in a fresh temporary output directory. Use
`--dry-run` for inspection or `--output-dir` to select a new separate directory.
Some transitive inputs are not locked; this is not a full-project hermetic lock.
No external model provider or real user data is used. Tests create a disposable
SQLite file and a loopback HTTP server, preserving the existing default adapters.

## Results and platform baseline

Linux Python 3.10 and 3.12: **61 passed**, zero failed/errors/skipped. Includes the
new protocol/SQLite/SDK integration and existing LLM configuration/image prompt
regressions. Windows Python 3.10 and 3.12: **49 passed** for the protocol/LLM subset.

The expanded same 61-test selection on Windows is **55 passed / 6 failed**. The six
failures concern existing plain Windows drive-letter image paths, not history.
The identical two image modules on unmodified upstream ChatPrompt produce the
same six failures (6 passed / 6 failed); file-URI and remote URL cases pass. The
old parser treats the drive letter as a URL scheme. This PR leaves that unrelated
behavior unchanged and does not hide or skip the failures. The baseline and
expanded Windows JUnit are included alongside passing Linux reports.

The equivalent Linux checks used the official
`ghcr.io/astral-sh/uv:python3.12-bookworm-slim` image with repository mounted
read-only at `/repo` and a separate writable `/evidence` directory:

```sh
uv run --no-project --python 3.12 python tests/reproduction/protocol-history-bridge/reproduce.py --python 3.12 --output-dir /evidence/history-py312
uv run --no-project --python 3.10 python tests/reproduction/protocol-history-bridge/reproduce.py --python 3.10 --output-dir /evidence/history-py310
```

Report screenshots show actual JUnit-derived summaries, not hosted CI. Raw
machine hostnames are removed from checked-in JUnit only; original hashes are
recorded. Package deprecation/mixed Pydantic warnings and read-only pytest-cache
warnings remain visible in local logs. No full-repository or paid-provider test,
merge acceptance, or competition score is claimed.
