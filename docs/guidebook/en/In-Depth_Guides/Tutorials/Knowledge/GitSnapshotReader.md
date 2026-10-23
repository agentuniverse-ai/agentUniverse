# Pinned Git snapshot Reader

`GitSnapshotReader` reads UTF-8 text from a **full commit object ID** in an
explicitly selected local repository. It does not read the current checkout,
stage changes, checkout a revision or clone/fetch. Unlike `CodeReader` (one current
file) or a Git-log parser (history text), it produces retrievable Documents with
commit, blob, path and line provenance. No default Reader routing is changed.

## Requirements and opt-in setup

Use an installed, trusted Git that supports `--no-lazy-fetch` and Python >=3.10.
Local validation uses Git 2.54.0.windows.1 and Python 3.10/3.12. Unsupported older
Git fails instead of silently allowing on-demand fetch. No new Python dependency
is required. Repository ownership checks are not bypassed.

Copy `agentuniverse/agent/action/knowledge/reader/file/git_snapshot_reader.yaml.example`
to the application's component directory as `.yaml`. This example is not enabled
by default. Set `include`, `exclude` and the resource limits for the desired corpus.

Create a small JSON manifest `manuals.gitsnapshot`:

```json
{
  "repository_path": "./local-checkout",
  "commit": "REPLACE_WITH_THE_FULL_COMMIT_OBJECT_ID",
  "repository_id": "team/project"
}
```

The placeholder is intentionally invalid: obtain the full commit ID from the
chosen repository (`git rev-parse HEAD`) and review it before ingestion. Branch
names, abbreviated IDs and annotated tag objects are not accepted. Relative
repository paths resolve against the manifest directory. The manifest is limited
to 8,192 bytes and exactly these three string fields; duplicate/unknown keys fail.
Treat manifests as trusted local configuration: they select filesystem access.

Register the Reader and your Store, then configure:

```python
from agentuniverse.agent.action.knowledge.knowledge import Knowledge

knowledge = Knowledge(
    readers={"gitsnapshot": "git_snapshot_reader"},
    stores=["your_registered_store"],
)
knowledge.insert_knowledge(source_path="/absolute/path/manuals.gitsnapshot")
documents = knowledge.query_knowledge(query_str="maintenance")
```

If using the existing SQLiteStore, configure its keyword extractor as usual.
Tests exercise real YAML registration, a real Git repository, JiebaKeywordExtractor,
SQLiteStore and the public Knowledge insert/query path (only tracing is isolated).
At this base revision Knowledge logs Store errors rather than guaranteeing batch
success; that behavior is unchanged. Reading a new commit does **not** remove old
Store documents. Use a separate corpus/index or an explicit source-sync policy.

## Direct API and audit report

```python
from agentuniverse.agent.action.knowledge.reader.file.git_snapshot_reader import GitSnapshotReader

reader = GitSnapshotReader(include=["docs/*.md", "src/*.py"], lines_per_document=100)
report = reader.read_snapshot("/local/repo", full_commit_id, "team/project")
documents = report.documents
skipped = report.skipped  # path/reason, or path_hex for a non-UTF-8 path
# Alternatively: documents = reader.load_data("manuals.gitsnapshot")
```

Each Document has `file_name` and `metadata.git_snapshot` with:

- `repository_id`: caller-chosen stable nonsecret label, never a remote URL/token
  or absolute repository path. Keep it unique across repositories.
- `commit`, `blob`, repository-relative `path`, one-based inclusive `start_line`
  and `end_line`, and `encoding="utf-8"`.
- `skipped_counts`: counts by exclusion reason for this read. For full paths/reasons,
  use `read_snapshot`; `load_data` returns just the Reader-compatible Document list.

IDs are SHA-256 of repository label, commit, path, blob and line range. They are
stable for repeated reads with the same boundaries, distinct for renamed paths
or other commits, and independent of the checkout's absolute location. Blob bytes
are checked against Git's SHA-1/SHA-256 object digest; this is content integrity,
not commit-signature verification or proof of authorship. Git replacement refs are
ignored so they cannot redefine the selected object.

Chunks preserve original CRLF/LF and final-newline state. Line numbers count LF
bytes, as Git does; Unicode paragraph separators do not create extra line numbers.
The reader does not parse programming-language syntax or execute selected files.
Preserve this metadata if subsequent processors split/rewrite content; processors
must update line ranges if they change their meaning.

## Selection, failure and resource boundaries

Default include patterns are `*.md`, `*.txt`, `*.py`. Matching is case-sensitive
`fnmatchcase` against the entire repository-relative path; `*` **can cross `/`**,
and excludes win. This is not `.gitignore`/Git pathspec semantics. Defaults exclude
common `.env`/key paths, but they are **not a secret scanner**. Review the selected
committed content before sending it to external Stores/models.

Regular blobs only: symlinks/submodules are reported as skipped, never followed;
NUL-containing content, non-UTF-8 text/paths, empty files and Git LFS pointers are
also reported. LFS contents are not downloaded. A UTF-8-decodable file without NUL
may still be a non-text format: choose explicit includes. Entirely excluded
snapshots return no Documents; inspect the direct report when completeness matters.

Defaults: 200 lines/document, 5,000 Documents, 2,000 tree entries (including excluded
ones), 2 MB tree listing, 2 MB/selected blob and 20 MB total selected raw bytes.
Byte and time bounds fail the complete read rather than returning a partial corpus.
Per-command timeout is 10 seconds and total read budget is 60 seconds. Git output
is bounded while being read; timed-out processes are killed/reaped. These are
application limits, not an OS resource sandbox or exact process-memory guarantee.
Very large repositories may exceed tree limits even when include patterns are narrow.
This implementation starts a Git process per selected blob, so benchmark your corpus
before raising limits. It is synchronous, matching the Reader base API.

The implementation uses `rev-parse`, NUL-delimited `ls-tree` and raw `cat-file blob`,
never textconv/smudge filters or repository hooks. Global/system Git config and
inherited Git routing environment are excluded; protocol access and lazy fetching
are disabled. Missing local objects fail and must be fetched **explicitly outside
this reader**. Local repository config/object databases remain trusted inputs;
this is not a sandbox for hostile repositories. No branch/index/worktree writes
are performed by the reader.

## Verify

With project test dependencies and a recent Git installed:

```sh
python -m pytest -q --import-mode=importlib \
  tests/test_agentuniverse/unit/agent/action/knowledge/reader/test_git_snapshot_reader.py
```

Tests build disposable real repositories with multiple commits, renames, dirty
worktrees, a bare clone, symlink/gitlink entries, SHA-256 objects, mixed line endings
and missing objects. They check deterministic IDs, original index/HEAD/worktree
preservation, bounded failures and Knowledge retrieval provenance. Timer cleanup
uses a controlled process double; it is not a claim of an OS-wide sandbox test.

References: [Git ls-tree](https://git-scm.com/docs/git-ls-tree),
[Git cat-file](https://git-scm.com/docs/git-cat-file),
[Git command options](https://git-scm.com/docs/git).
