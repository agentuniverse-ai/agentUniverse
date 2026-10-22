#!/usr/bin/env python3
"""Offline unit tests for GitLogTool.

Oracle: the real `git` binary. A fixture repository is built with fixed
authors/dates/messages, every `git log` variant is run for real, and the
tool's parse is compared field-by-field against `git log --pretty` with
explicit format specifiers (the plumbing ground truth). Hand-embedded
format fixtures pin the exact output shapes (merge headers, stat tables,
binary entries, rename lines).
"""

import os
import shutil
import subprocess
import tempfile
import unittest

from agentuniverse.agent.action.tool.common_tool.git_log_tool import GitLogTool

GIT = shutil.which("git")


def _run(cwd, *args, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run([GIT, *args], cwd=cwd, capture_output=True, text=True, env=env)


def _commit(cwd, date, author, email, msg, files):
    for path, content in files.items():
        os.makedirs(os.path.dirname(os.path.join(cwd, path)) or cwd, exist_ok=True)
        with open(os.path.join(cwd, path), "w") as fh:
            fh.write(content)
    _run(cwd, "add", "-A")
    env = {
        "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
        "GIT_AUTHOR_NAME": author, "GIT_AUTHOR_EMAIL": email,
        "GIT_COMMITTER_NAME": author, "GIT_COMMITTER_EMAIL": email,
    }
    _run(cwd, "commit", "-m", msg, env_extra=env)


def _build_repo():
    root = tempfile.mkdtemp(prefix="gitlog-oracle-")
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.name", "Test User")
    _run(root, "config", "user.email", "test@example.com")
    _commit(root, "2026-01-02T10:00:00+08:00", "Alice Dev", "alice@example.com",
            "first: add core\n\nbody line", {"src/a.py": "a\n", "src/b.py": "b\n"})
    _commit(root, "2026-02-03T11:00:00+08:00", "Bob Dev", "bob@example.com",
            "second: modify a", {"src/a.py": "a2\na3\na4\n"})
    _commit(root, "2026-03-04T12:00:00+08:00", "Alice Dev", "alice@example.com",
            "third: add test and rename", {"tests/t_a.py": "t\n"})
    _run(root, "mv", "src/b.py", "src/renamed.py")
    env = {
        "GIT_AUTHOR_DATE": "2026-04-05T13:00:00+08:00",
        "GIT_COMMITTER_DATE": "2026-04-05T13:00:00+08:00",
        "GIT_AUTHOR_NAME": "Alice Dev", "GIT_AUTHOR_EMAIL": "alice@example.com",
        "GIT_COMMITTER_NAME": "Alice Dev", "GIT_COMMITTER_EMAIL": "alice@example.com",
    }
    _run(root, "commit", "-m", "fourth: rename b", env_extra=env)
    return root


@unittest.skipIf(GIT is None, "git binary not available")
class GitLogToolOracleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = _build_repo()
        cls.tool = GitLogTool()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def _plumbing(self, *args):
        r = _run(self.root, "log", *args)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_default_format_fields(self):
        text = self._plumbing("--no-color")
        out = self.tool.execute(mode="parse", log_text=text)
        self.assertEqual(out["commit_count"], 4)
        shas = self._plumbing("--pretty=%H").split()
        for i, c in enumerate(out["commits"]):
            self.assertEqual(c["sha"], shas[i])
        subjects = self._plumbing("--pretty=%s").splitlines()
        self.assertEqual([c["message"].splitlines()[0] for c in out["commits"]], subjects)
        authors = self._plumbing("--pretty=%an").splitlines()
        self.assertEqual([c["author"] for c in out["commits"]], authors)
        emails = self._plumbing("--pretty=%ae").splitlines()
        self.assertEqual([c["author_email"] for c in out["commits"]], emails)
        dates = self._plumbing("--pretty=%aI").splitlines()
        self.assertEqual([c["date_iso"] for c in out["commits"]], dates)
        self.assertEqual(out["commits"][-1]["message"], "first: add core\n\nbody line")

    def test_numstat(self):
        text = self._plumbing("--no-color", "--numstat")
        out = self.tool.execute(mode="parse", log_text=text)
        for c in out["commits"]:
            plumbing = self._plumbing("--pretty=%H", "-1", c["sha"], "--numstat").splitlines()
            expected = [line for line in plumbing if "\t" in line]
            got = [f"{n['added'] if n['added'] is not None else '-'}\t"
                   f"{n['deleted'] if n['deleted'] is not None else '-'}\t{n['path']}"
                   for n in c["numstat"]]
            self.assertEqual(got, expected, c["sha"])

    def test_name_status_with_rename(self):
        text = self._plumbing("--no-color", "--name-status")
        out = self.tool.execute(mode="parse", log_text=text)
        rename_commit = out["commits"][0]  # newest first: the rename commit
        self.assertEqual(rename_commit["name_status"][0]["status"], "R")
        self.assertEqual(rename_commit["name_status"][0]["old_path"], "src/b.py")
        self.assertEqual(rename_commit["name_status"][0]["path"], "src/renamed.py")

    def test_stat_summary(self):
        text = self._plumbing("--no-color", "--stat")
        out = self.tool.execute(mode="parse", log_text=text)
        for c in out["commits"]:
            if c["merge_parents"] and c["stat_summary"] is None:
                continue  # merge commits show no stat table by default
            summary = self._plumbing("--pretty=", "-1", c["sha"], "--shortstat").strip()
            files = summary.split()[0] if summary else "0"
            self.assertIsNotNone(c["stat_summary"], c["sha"])
            self.assertEqual(str(c["stat_summary"]["files_changed"]), files, c["sha"])

    def test_oneline(self):
        text = self._plumbing("--no-color", "--oneline")
        out = self.tool.execute(mode="parse", log_text=text)
        self.assertEqual(out["commit_count"], 4)
        shas = self._plumbing("--pretty=%h").split()
        self.assertEqual([c["sha"] for c in out["commits"]], shas)

    def test_summarize(self):
        text = self._plumbing("--no-color", "--numstat")
        out = self.tool.execute(mode="summarize", log_text=text)
        self.assertEqual(out["commit_count"], 4)
        alice = next(a for a in out["authors"] if a["author"] == "Alice Dev")
        bob = next(a for a in out["authors"] if a["author"] == "Bob Dev")
        self.assertEqual(alice["commits"], 3)
        self.assertEqual(bob["commits"], 1)
        self.assertEqual(out["totals"]["insertions"], 6)  # a2/a3/a4 + t
        self.assertEqual(out["totals"]["deletions"], 1)   # a replaced

    def test_detect(self):
        out = self.tool.execute(mode="detect", log_text=self._plumbing("--no-color", "--stat"))
        self.assertIn("--stat", out["styles"])
        out = self.tool.execute(mode="detect", log_text=self._plumbing("--no-color", "--numstat"))
        self.assertIn("--numstat", out["styles"])

    def test_decorations_and_merges(self):
        # a separate fixture so the shared repo is never mutated
        root = _build_repo()
        try:
            _run(root, "checkout", "-q", "-b", "feature")
            _commit(root, "2026-05-06T14:00:00+08:00", "Carol Dev",
                    "carol@example.com", "feature work", {"src/feat.py": "f\n"})
            _run(root, "checkout", "-q", "main")
            env = {
                "GIT_AUTHOR_DATE": "2026-05-07T15:00:00+08:00",
                "GIT_COMMITTER_DATE": "2026-05-07T15:00:00+08:00",
                "GIT_AUTHOR_NAME": "Alice Dev", "GIT_AUTHOR_EMAIL": "alice@example.com",
                "GIT_COMMITTER_NAME": "Alice Dev", "GIT_COMMITTER_EMAIL": "alice@example.com",
            }
            _run(root, "merge", "-q", "--no-ff", "-m", "merge feature", "feature", env_extra=env)
            text = _run(root, "log", "--no-color").stdout
            out = self.tool.execute(mode="parse", log_text=text)
            head = out["commits"][0]
            self.assertEqual(len(head["merge_parents"]), 2)
            self.assertEqual(head["message"], "merge feature")
        finally:
            shutil.rmtree(root, ignore_errors=True)


class GitLogToolFormatFixturesTest(unittest.TestCase):
    """Hand-embedded format shapes, no git needed."""

    def setUp(self):
        self.tool = GitLogTool()

    def test_default_format_fixture(self):
        text = (
            "commit 280a9913597ddbf1f48ee9c8cc811adb82f3e463 (HEAD -> master)\n"
            "Merge: 605d52881 d0a8c2d65\n"
            "Author: hxbszyy <167101124+hxbszyy@users.noreply.github.com>\n"
            "Date:   Thu Jul 9 16:46:23 2026 +0800\n"
            "\n"
            "    Merge pull request #596 from itxaiohanglover/fix/request-do-query-type\n"
            "    \n"
            "    fix: support list and dict types in service request query param\n"
        )
        out = self.tool.execute(mode="parse", log_text=text)
        self.assertEqual(out["commit_count"], 1)
        c = out["commits"][0]
        self.assertEqual(c["decoration"], "HEAD -> master")
        self.assertEqual(c["merge_parents"], ["605d52881", "d0a8c2d65"])
        self.assertEqual(c["author"], "hxbszyy")
        self.assertEqual(c["date_iso"], "2026-07-09T16:46:23+08:00")
        self.assertIn("Merge pull request #596", c["message"])

    def test_stat_table_fixture(self):
        text = (
            "commit d0a8c2d656\n"
            " .../web/dal/entity/request_do.py       |  4 +-\n"
            " tests/.../test_request_do.py          | 57 ++++++++++++++++++++++\n"
            " img/logo.png                          | Bin 0 -> 1234 bytes\n"
            " 3 files changed, 68 insertions(+), 5 deletions(-)\n"
        )
        out = self.tool.execute(mode="parse", log_text=text)
        c = out["commits"][0]
        self.assertEqual(c["stat_summary"],
                         {"files_changed": 3, "insertions": 68, "deletions": 5})
        self.assertTrue(c["stat"][2]["binary"])
        self.assertEqual(c["stat"][2]["bytes"], 1234)
        self.assertEqual(c["stat"][0]["plus"], 1)
        self.assertEqual(c["stat"][0]["minus"], 1)

    def test_numstat_binary_fixture(self):
        text = "commit abc1234\n5\t2\tsrc/a.py\n-\t-\tbin/blob.dat\n"
        out = self.tool.execute(mode="parse", log_text=text)
        self.assertEqual(out["commits"][0]["numstat"][1],
                         {"added": None, "deleted": None, "path": "bin/blob.dat"})

    def test_validation(self):
        with self.assertRaises(ValueError):
            self.tool.execute(mode="nope", log_text="")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="parse", log_text=123)
        out = self.tool.execute(mode="parse", log_text="random text\nno commits")
        self.assertEqual(out["commit_count"], 0)
        self.assertTrue(out["warnings"])

    def test_empty(self):
        out = self.tool.execute(mode="parse", log_text="")
        self.assertEqual(out["commit_count"], 0)
        self.assertEqual(self.tool.execute(mode="summarize", log_text="")["commit_count"], 0)


if __name__ == "__main__":
    unittest.main()
