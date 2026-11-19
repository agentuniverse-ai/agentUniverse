"""Read committed text without checking out, executing or fetching repository code."""

import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from pydantic import Field, StrictInt

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


@dataclass
class GitSnapshotResult:
    """One immutable-commit read; exclusions are reported, never counted as indexed."""

    commit: str
    documents: list[Document]
    skipped: list[dict[str, str]]


class GitSnapshotReader(Reader):
    """An opt-in local, trusted-repository reader; not a Git security sandbox."""

    include: list[str] = Field(default_factory=lambda: ["*.md", "*.txt", "*.py"])
    exclude: list[str] = Field(default_factory=lambda: [".env", ".env.*", "**/.env", "**/.env.*", "*.pem", "*.key"])
    lines_per_document: StrictInt = 200
    max_documents: StrictInt = 5000
    max_files: StrictInt = 2000
    max_tree_bytes: StrictInt = 2000000
    max_blob_bytes: StrictInt = 2000000
    max_total_bytes: StrictInt = 20000000
    command_timeout_seconds: StrictInt = 10
    total_timeout_seconds: StrictInt = 60

    _OPTIONS: ClassVar[tuple] = (
        "include",
        "exclude",
        "lines_per_document",
        "max_documents",
        "max_files",
        "max_tree_bytes",
        "max_blob_bytes",
        "max_total_bytes",
        "command_timeout_seconds",
        "total_timeout_seconds",
    )

    def _validate(self):
        for key in self._OPTIONS[2:]:
            value = getattr(self, key)
            upper = 300 if "timeout" in key else 100000000
            if type(value) is not int or not 1 <= value <= upper:
                raise ValueError(key + " must be a positive bounded integer")
        for patterns in (self.include, self.exclude):
            if (
                not isinstance(patterns, list)
                or len(patterns) > 100
                or any(
                    not isinstance(pattern, str) or not pattern or len(pattern) > 512 or "\x00" in pattern
                    for pattern in patterns
                )
            ):
                raise ValueError("include/exclude must be bounded lists of nonempty glob patterns")
        if not self.include:
            raise ValueError("at least one include pattern is required")

    def _initialize_by_component_configer(self, config):
        values = {key: getattr(config, key, getattr(self, key)) for key in self._OPTIONS}
        candidate = GitSnapshotReader(**values)
        candidate._validate()
        for key in self._OPTIONS:
            value = getattr(candidate, key)
            setattr(self, key, list(value) if isinstance(value, list) else value)
        return super()._initialize_by_component_configer(config)

    def _run_git(self, repository, arguments, limit, deadline):
        remaining = min(self.command_timeout_seconds, deadline - time.monotonic())
        if remaining <= 0:
            raise TimeoutError("Git snapshot total time budget exceeded")
        executable = shutil.which("git")
        if not executable:
            raise RuntimeError("GitSnapshotReader requires Git on PATH")
        environment = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
        environment.update(
            {
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_TERMINAL_PROMPT": "0",
                "GIT_OPTIONAL_LOCKS": "0",
                "GIT_NO_LAZY_FETCH": "1",
                "GIT_ALLOW_PROTOCOL": "",
            }
        )
        command = [
            executable,
            "--no-pager",
            "--no-replace-objects",
            "--no-lazy-fetch",
            "-c",
            "protocol.allow=never",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "core.hooksPath=" + os.devnull,
            "-C",
            str(repository),
            *arguments,
        ]
        timed_out = threading.Event()
        with subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=environment,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        ) as process:

            def expire():
                timed_out.set()
                try:
                    process.kill()
                except ProcessLookupError:
                    pass

            timer = threading.Timer(remaining, expire)
            timer.daemon = True
            timer.start()
            try:
                data = process.stdout.read(limit + 1)
                if len(data) > limit:
                    process.kill()
                    raise ValueError("Git command output exceeds configured byte budget")
                code = process.wait()
                if timed_out.is_set():
                    raise TimeoutError("Git snapshot command timed out")
                if code:
                    # Raw stderr may contain local paths or configuration secrets.
                    raise RuntimeError(
                        "Git snapshot read failed; verify local repository/commit availability "
                        "and Git support for --no-lazy-fetch"
                    )
                return data
            finally:
                timer.cancel()
                if process.poll() is None:
                    process.kill()
                process.wait()

    def read_snapshot(self, repository_path, commit, repository_id) -> GitSnapshotResult:
        """Return Documents plus explicit exclusions from a full commit object ID.

        Paths are repository-relative UTF-8 names. Glob matching uses fnmatchcase
        on the complete path (so '*' can cross '/'). Excludes take precedence.
        No content from the worktree, index, symlink targets or submodules is read.
        """
        self._validate()
        if not isinstance(commit, str) or not re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", commit):
            raise ValueError("commit must be a full 40/64-hex commit ID, not a branch or tag")
        if not isinstance(repository_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,127}", repository_id):
            raise ValueError("repository_id must be a stable, nonsecret repository label")
        repository = Path(repository_path).resolve(strict=True)
        if not repository.is_dir():
            raise ValueError("repository_path must be a local repository directory")
        deadline = time.monotonic() + self.total_timeout_seconds
        resolved = (
            self._run_git(
                repository, ["rev-parse", "--verify", "--end-of-options", commit + "^{commit}"], 128, deadline
            )
            .decode("ascii")
            .strip()
        )
        if resolved != commit.lower():
            raise ValueError("the supplied object must itself be a commit, not an annotated tag")
        tree = self._run_git(
            repository, ["ls-tree", "-r", "-l", "-z", "--full-tree", resolved], self.max_tree_bytes, deadline
        )
        entries = tree.split(b"\x00")[:-1]
        if tree and not tree.endswith(b"\x00"):
            raise RuntimeError("incomplete Git tree listing")
        if len(entries) > self.max_files:
            raise ValueError("snapshot tree exceeds max_files; no partial documents returned")
        documents, skipped = [], []
        total = 0
        for entry in entries:
            if time.monotonic() >= deadline:
                raise TimeoutError("Git snapshot total time budget exceeded")
            header, raw_path = entry.split(b"\t", 1)
            mode, kind, blob, raw_size = header.split()
            try:
                path = raw_path.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                skipped.append({"path_hex": raw_path.hex(), "reason": "non_utf8_path"})
                continue
            if not any(fnmatch.fnmatchcase(path, p) for p in self.include) or any(
                fnmatch.fnmatchcase(path, p) for p in self.exclude
            ):
                skipped.append({"path": path, "reason": "excluded"})
                continue
            if kind != b"blob" or mode not in (b"100644", b"100755"):
                skipped.append({"path": path, "reason": "symlink_or_submodule"})
                continue
            if not raw_size.isdigit():
                raise RuntimeError("selected Git blob is unavailable locally; fetch it explicitly before reading")
            size = int(raw_size)
            if size > self.max_blob_bytes:
                raise ValueError("selected blob exceeds max_blob_bytes; no partial documents returned")
            total += size
            if total > self.max_total_bytes:
                raise ValueError("snapshot content exceeds max_total_bytes; no partial documents returned")
            oid = blob.decode("ascii")
            content = self._run_git(repository, ["cat-file", "blob", oid], self.max_blob_bytes, deadline)
            algorithm = "sha1" if len(oid) == 40 else "sha256"
            digest = hashlib.new(
                algorithm, b"blob " + str(len(content)).encode() + b"\x00" + content, usedforsecurity=False
            ).hexdigest()
            if len(content) != size or digest != oid:
                raise RuntimeError("Git blob integrity/length mismatch")
            if b"\x00" in content:
                skipped.append({"path": path, "reason": "binary"})
                continue
            if content.startswith(
                (b"version https://git-lfs.github.com/spec/v1\n", b"version https://git-lfs.github.com/spec/v1\r\n")
            ):
                skipped.append({"path": path, "reason": "lfs_pointer"})
                continue
            try:
                text = content.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                skipped.append({"path": path, "reason": "non_utf8_content"})
                continue
            if not text:
                skipped.append({"path": path, "reason": "empty"})
                continue
            # Count Git's LF-delimited lines, preserving CRLF and final-newline state.
            pieces = text.split("\n")
            lines = [part + "\n" for part in pieces[:-1]] + ([pieces[-1]] if pieces[-1] else [])
            for offset in range(0, len(lines), self.lines_per_document):
                end = min(offset + self.lines_per_document, len(lines))
                identity = json.dumps([repository_id, resolved, path, oid, offset + 1, end], ensure_ascii=True)
                documents.append(
                    Document(
                        id="git:" + hashlib.sha256(identity.encode()).hexdigest(),
                        text="".join(lines[offset:end]),
                        metadata={
                            "file_name": path.rsplit("/", 1)[-1],
                            "git_snapshot": {
                                "repository_id": repository_id,
                                "commit": resolved,
                                "path": path,
                                "blob": oid,
                                "start_line": offset + 1,
                                "end_line": end,
                                "encoding": "utf-8",
                            },
                        },
                    )
                )
                if len(documents) > self.max_documents:
                    raise ValueError("snapshot exceeds max_documents; no partial documents returned")
        counts = dict(Counter(item["reason"] for item in skipped))
        for document in documents:
            document.metadata["git_snapshot"]["skipped_counts"] = counts.copy()
        if time.monotonic() >= deadline:
            raise TimeoutError("Git snapshot total time budget exceeded")
        return GitSnapshotResult(resolved, documents, skipped)

    def _load_data(self, manifest_path, ext_info=None) -> list[Document]:
        """Read a small .gitsnapshot JSON manifest for the public Knowledge path."""
        if ext_info:
            raise ValueError("ext_info is unsupported: snapshot provenance cannot be overridden")
        path = Path(manifest_path).resolve(strict=True)
        with path.open("rb") as stream:
            raw = stream.read(8193)
        if len(raw) > 8192:
            raise ValueError("Git snapshot manifest exceeds 8192 bytes")

        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate manifest field")
                result[key] = value
            return result

        spec = json.loads(raw, object_pairs_hook=unique_object)
        if not isinstance(spec, dict) or set(spec) != {"repository_path", "commit", "repository_id"}:
            raise ValueError("manifest requires exactly repository_path, commit, repository_id")
        if not all(isinstance(value, str) for value in spec.values()):
            raise ValueError("manifest values must be strings")
        repo = Path(spec["repository_path"])
        if not repo.is_absolute():
            repo = path.parent / repo
        return self.read_snapshot(repo, spec["commit"], spec["repository_id"]).documents
