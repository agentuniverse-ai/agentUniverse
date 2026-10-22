#!/usr/bin/env python3

"""Oracle-backed tests for GitRefNameTool.

Every verdict is compared against the real ``git check-ref-format``
binary (plain, ``--allow-onelevel``, ``--refspec-pattern``, ``--branch``,
and ``--normalize`` variants) on a deterministic corpus of 800+ seeded
reference names: valid walks plus a mutation battery covering each
forbidden character at each position class, dot and slash rules, the
``.lock`` suffix family, ``@``/``@{`` forms, control characters
(including DEL), Unicode (CJK, emoji, fullwidth, NFC/NFD), single vs
two-level names, deep paths, and very long names.

Suggested repairs are re-verified through the binary, and ``compare``
collision flags are checked on crafted NFC/NFD and case pairs.
"""

import subprocess
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
import yaml

from agentuniverse.agent.action.tool.common_tool import GitRefNameTool
from agentuniverse.agent.action.tool.common_tool.git_ref_name_tool import GitRefNameTool as DirectTool
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

FORBIDDEN = [" ", "~", "^", ":", "?", "*", "[", "\\", "\x01", "\x7f", "\n"]

BASES = [
    "main",
    "master",
    "develop",
    "feature/x",
    "feature/login-form",
    "bugfix/ABC-123-null-crash",
    "hotfix/v1.2.3",
    "release/2024-01",
    "refs/heads/main",
    "refs/tags/v1.2.3",
    "refs/remotes/origin/main",
    "v1.2.3",
    "v10.0.0-rc.1",
    "2024-01-15",
    "a/b/c/d/e",
    "user/name/with/deep/nesting",
    "foo@bar",
    "x/@",
    "a./b",
    "foo.LOCK",
]

UNICODE_NAMES = [
    "修复分支",
    "修复/分支",
    "fix/🚀",
    "café",
    unicodedata.normalize("NFD", "café"),
    "ＡＢ",
    "fix／feature",  # fullwidth slash U+FF0F, not the ASCII slash
    "分支。",
    "a—b",
    "\u200bx",  # zero-width space
    "\ufeffx",  # BOM
];

EXTRA_CASES = [
    "",
    "@",
    "@{1}",
    "a@{b",
    "foo@{",
    "@{-1}",
    "@{u}",
    "@{upstream}",
    "foo@",
    "@foo",
    "@/x",
    "*",
    "a*",
    "*a",
    "a*b",
    "a*b*c",
    "foo/*",
    "*/foo",
    "*/*",
    "refs/heads/*",
    "**",
    "-",
    "-x",
    "-x/y",
    "HEAD",
    "head",
    "HEAD/x",
    "refs/heads/HEAD",
    "a//b",
    "a/",
    "/a",
    "/",
    "//",
    "///",
    "...",
    ".",
    "..",
    "foo.",
    ".foo",
    "a/.b",
    "x/.y/z",
    "foo.lock",
    "foo.LOCK",
    "foo.lOcK",
    "foo.lock.x",
    "a/b.lock/c",
    "foo..bar",
    "a/../b",
    "refs/heads/",
    "refs/heads/x/",
    "a" * 100,
    "a" * 250,
    "a" * 1000,
    "ab/" * 300,
    "x/" + "y" * 200,
    "refs/heads/refs/heads/x",
    "refs/tags/",
]


def _dedupe(names):
    seen = set()
    out = []
    for name in names:
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def build_corpus():
    """Deterministic seeded corpus: 800+ names built from bases + mutations."""
    names = list(BASES) + list(UNICODE_NAMES) + list(EXTRA_CASES)

    # Each forbidden character inserted at start / middle / end of each base.
    for base in BASES:
        middle = len(base) // 2
        for char in FORBIDDEN:
            names.append(char + base)
            names.append(base[:middle] + char + base[middle:])
            names.append(base + char)

    # Every ASCII control character plus DEL in the middle of a branch path.
    for code in range(0x20):
        names.append("feature" + chr(code) + "x")
    names.append("feature\x7fx")

    # Dot, slash, and lock-suffix battery.
    for base in ("feature/x", "v1.2.3", "main", "refs/heads/main", "a/b/c"):
        names.extend(
            [
                base + ".",
                "." + base,
                base + "..x",
                base + "/." + "x",
                base + ".lock",
                base + ".LOCK",
                base + ".Lock",
                base + ".lock.x",
                base.replace("/", "//", 1) if "/" in base else base + "//x",
                "/" + base,
                base + "/",
            ]
        )

    return _dedupe(names)


CORPUS = build_corpus()


@pytest.fixture(scope="session")
def oracle_cwd(tmp_path_factory):
    """A directory outside any git repository.

    Running the oracle here keeps stateful forms like ``@{-1}``
    deterministic: without repository history git cannot expand them and
    rejects them, matching the stateless tool.
    """
    return str(tmp_path_factory.mktemp("refname-oracle"))


def git_rc(oracle_cwd, *args):
    completed = subprocess.run(
        ["git", "check-ref-format", *args],
        cwd=oracle_cwd,
        capture_output=True,
        text=True,
    )
    return completed.returncode, completed.stdout.rstrip("\n")


@pytest.fixture(scope="session")
def tool():
    return GitRefNameTool()


def run_parallel(jobs, workers=8):
    """Deterministically map (func, arg) jobs through a thread pool."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda job: job[0](*job[1:]), jobs))


# --------------------------------------------------------------------- #
# (a) verdict parity: tool verdict == binary exit code on every case    #
# --------------------------------------------------------------------- #

def test_corpus_is_large_enough():
    assert len(CORPUS) >= 800


def test_verdict_parity_plain_and_onelevel(oracle_cwd, tool):
    jobs = []
    for name in CORPUS:
        if name.startswith("-") or "\x00" in name:
            continue  # cannot pass as argv to the binary
        for extra in ([], ["--allow-onelevel"]):
            jobs.append((git_rc, oracle_cwd, *extra, name))
    binary = run_parallel(jobs)

    index = 0
    checked = 0
    for name in CORPUS:
        if name.startswith("-") or "\x00" in name:
            continue
        for allow_onelevel in (False, True):
            rc, _ = binary[index]
            index += 1
            result = tool.execute(mode="validate", name=name, allow_onelevel=allow_onelevel)
            assert result["valid"] == (rc == 0), (
                f"name={name!r} allow_onelevel={allow_onelevel} "
                f"tool={result['valid']} git_rc={rc} violations={result['violations']}"
            )
            checked += 1
    assert checked > 1500


def test_verdict_parity_refspec_pattern(oracle_cwd, tool):
    subset = _dedupe(
        [n for n in CORPUS if "*" in n] + [n for i, n in enumerate(CORPUS) if i % 5 == 0]
    )
    jobs = [(git_rc, oracle_cwd, "--refspec-pattern", "--allow-onelevel", n) for n in subset if not n.startswith("-")]
    binary = run_parallel(jobs)

    index = 0
    for name in subset:
        if name.startswith("-"):
            continue
        rc, _ = binary[index]
        index += 1
        result = tool.execute(mode="validate", name=name, allow_onelevel=True, refspec_pattern=True)
        assert result["valid"] == (rc == 0), f"name={name!r} tool={result['valid']} git_rc={rc}"


def test_verdict_parity_branch_shorthand(oracle_cwd, tool):
    jobs = [
        (git_rc, oracle_cwd, "--branch", name)
        for name in CORPUS
        if not name.startswith("--") and "\x00" not in name
    ]
    binary = run_parallel(jobs)

    index = 0
    for name in CORPUS:
        if name.startswith("--") or "\x00" in name:
            continue
        rc, _ = binary[index]
        index += 1
        result = tool.execute(mode="validate", name=name, ref_type="branch")
        assert result["valid"] == (rc == 0), (
            f"branch name={name!r} tool={result['valid']} git_rc={rc} violations={result['violations']}"
        )


def test_verdict_parity_tag_namespace(oracle_cwd, tool):
    subset = [n for i, n in enumerate(CORPUS) if i % 3 == 0 and "\x00" not in n]
    jobs = [(git_rc, oracle_cwd, "refs/tags/" + name) for name in subset]
    binary = run_parallel(jobs)

    index = 0
    for name in subset:
        rc, _ = binary[index]
        index += 1
        result = tool.execute(mode="validate", name=name, ref_type="tag")
        assert result["valid"] == (rc == 0), f"tag name={name!r} tool={result['valid']} git_rc={rc}"


def test_nul_and_dash_leading_tool_verdicts(tool):
    """NUL and leading-dash inputs cannot cross argv; assert tool-side rules."""
    for name in ("feature\x00x", "\x00"):
        result = tool.execute(mode="validate", name=name, allow_onelevel=True)
        assert result["valid"] is False
        assert any(v["rule"] == "control_char" for v in result["violations"])
    plain = tool.execute(mode="validate", name="-foo", allow_onelevel=True)
    assert plain["valid"] is True  # dash is legal in a refname body
    branch = tool.execute(mode="validate", name="-foo", ref_type="branch")
    assert branch["valid"] is False
    assert any(v["rule"] == "branch_leading_dash" for v in branch["violations"])


# --------------------------------------------------------------------- #
# (b) normalize parity with git check-ref-format --normalize            #
# --------------------------------------------------------------------- #

def test_normalize_parity(oracle_cwd, tool):
    jobs = [
        (git_rc, oracle_cwd, "--normalize", "--allow-onelevel", name)
        for name in CORPUS
        if not name.startswith("-") and "\x00" not in name
    ]
    binary = run_parallel(jobs)

    index = 0
    for name in CORPUS:
        if name.startswith("-") or "\x00" in name:
            continue
        rc, stdout = binary[index]
        index += 1
        result = tool.execute(mode="normalize", name=name, allow_onelevel=True)
        assert result["valid"] == (rc == 0), (
            f"normalize name={name!r} tool={result['valid']} git_rc={rc}"
        )
        if rc == 0:
            assert result["normalized"] == stdout, (
                f"normalize name={name!r} tool={result['normalized']!r} git={stdout!r}"
            )


def test_normalize_behavior_fixed_cases(tool):
    result = tool.execute(mode="normalize", name="a//b", allow_onelevel=True)
    assert result["normalized"] == "a/b" and result["valid"] is True
    result = tool.execute(mode="normalize", name="//a//b/", allow_onelevel=True)
    assert result["normalized"] == "a/b/" and result["valid"] is False  # trailing slash survives
    result = tool.execute(mode="normalize", name="///", allow_onelevel=True)
    assert result["normalized"] == "" and result["valid"] is False
    result = tool.execute(mode="normalize", name="/master", allow_onelevel=False)
    assert result["normalized"] == "master" and result["valid"] is False  # one level needs the option


# --------------------------------------------------------------------- #
# (c) suggest: every suggested name re-verified through the binary      #
# --------------------------------------------------------------------- #

def test_suggestions_reverified_by_binary_any(oracle_cwd, tool):
    invalid_names = [
        name
        for i, name in enumerate(CORPUS)
        if i % 4 == 0 and not name.startswith("-") and "\x00" not in name
        and not tool.execute(mode="validate", name=name)["valid"]
    ]
    jobs = []
    proposed = []
    for name in invalid_names:
        result = tool.execute(mode="suggest", name=name)
        assert result["input_valid"] is False
        for suggestion in result["suggestions"]:
            if suggestion["valid_now"]:
                jobs.append((git_rc, oracle_cwd, suggestion["name"]))
                proposed.append((name, suggestion["name"]))

    binary = run_parallel(jobs)
    for (original, suggestion), (rc, _) in zip(proposed, binary):
        assert rc == 0, f"original={original!r} suggestion={suggestion!r} git_rc={rc}"
    assert len(proposed) > 100


def test_suggestions_reverified_by_binary_branch(oracle_cwd, tool):
    invalid_names = [
        name
        for i, name in enumerate(CORPUS)
        if i % 6 == 0 and not name.startswith("-") and "\x00" not in name
        and not tool.execute(mode="validate", name=name, ref_type="branch")["valid"]
    ]
    jobs = []
    proposed = []
    for name in invalid_names:
        result = tool.execute(mode="suggest", name=name, ref_type="branch")
        for suggestion in result["suggestions"]:
            if suggestion["valid_now"]:
                jobs.append((git_rc, oracle_cwd, "--branch", suggestion["name"]))
                proposed.append((name, suggestion["name"]))

    binary = run_parallel(jobs)
    for (original, suggestion), (rc, _) in zip(proposed, binary):
        assert rc == 0, f"original={original!r} suggestion={suggestion!r} git_rc={rc}"
    assert len(proposed) > 15


def test_suggest_valid_input_returns_no_suggestions(tool):
    result = tool.execute(mode="suggest", name="feature/x")
    assert result["input_valid"] is True
    assert result["suggestions"] == []
    assert result["best"] is None


def test_suggest_repairs_are_deterministic(tool):
    for name in ("feature//x", "-nope", "foo.lock", "release/..", "@", "has space/x", "bad~1"):
        first = tool.execute(mode="suggest", name=name, ref_type="branch")
        second = tool.execute(mode="suggest", name=name, ref_type="branch")
        assert first == second


def test_suggest_minimal_change_shape(tool):
    result = tool.execute(mode="suggest", name="feature/log~in", ref_type="branch")
    assert result["suggestions"][0]["changes"]
    assert all(set(s) == {"name", "changes", "valid_now"} for s in result["suggestions"])
    assert result["best"] == next(s["name"] for s in result["suggestions"] if s["valid_now"])


# --------------------------------------------------------------------- #
# (d) compare: equivalence, case collisions, NFC/NFD collisions         #
# --------------------------------------------------------------------- #

def test_compare_prefix_equivalence(tool):
    result = tool.execute(mode="compare", name="refs/heads/x", other_name="x")
    assert result["same_ref_if_branch"] is True
    assert result["equivalent"] is True
    result = tool.execute(mode="compare", name="refs/tags/v1", other_name="v1")
    assert result["same_ref_if_tag"] is True
    result = tool.execute(mode="compare", name="refs/heads/x", other_name="refs/tags/x")
    assert result["equivalent"] is False  # different namespaces


def test_compare_case_collision_battery(tool):
    for a, b in (("Feature", "feature"), ("MAIN", "main"), ("refs/heads/Fix", "refs/heads/fix"), ("A-1", "a-1")):
        result = tool.execute(mode="compare", name=a, other_name=b)
        assert result["differ_only_by_case"] is True, a
        assert any("core.ignoreCase" in note for note in result["notes"])
        assert result["equivalent"] is False or result["same_ref_if_branch"]
    same = tool.execute(mode="compare", name="feature", other_name="feature")
    assert same["differ_only_by_case"] is False


def test_compare_nfc_nfd_collision(tool):
    nfc = "café"
    nfd = unicodedata.normalize("NFD", "café")
    assert nfc != nfd
    result = tool.execute(mode="compare", name=nfc, other_name=nfd)
    assert result["differ_only_by_unicode_normalization"] is True
    assert result["nfc_forms"][0] == result["nfc_forms"][1] == nfc
    assert any("normalization" in note for note in result["notes"])

    ascii_pair = tool.execute(mode="compare", name="cafe", other_name="café")
    assert ascii_pair["differ_only_by_unicode_normalization"] is False


def test_compare_fullwidth_confusables(tool):
    result = tool.execute(mode="compare", name="fix／x", other_name="fix/x")  # U+FF0F vs '/'
    assert result["unicode_confusables"] is True
    assert any("confusables" in note for note in result["notes"])


# --------------------------------------------------------------------- #
# analyze, config contract, errors, caps                                #
# --------------------------------------------------------------------- #

def test_analyze_reports_parts_patterns_and_tickets(tool):
    result = tool.execute(mode="analyze", name="hotfix/ABC-123-crash")
    assert result["parts"] == ["hotfix", "ABC-123-crash"]
    assert result["ticket_refs"] == ["ABC-123"]
    assert result["suggested_type"] == "branch"

    result = tool.execute(mode="analyze", name="refs/tags/v2.1.0")
    assert result["prefixed_kind"] == "tag"
    assert "semver" in result["looks_like"]

    result = tool.execute(mode="analyze", name="HEAD")
    assert result["prefixed_kind"] == "ref"
    assert result["suggested_type"] == "HEAD"

    result = tool.execute(mode="analyze", name="release/2024-01-15")
    assert "date-based" in result["looks_like"]
    assert result["suggested_type"] == "branch"


def test_analyze_style_findings(tool):
    result = tool.execute(mode="analyze", name="ＦＥＡＴＵＲＥ/Ｘ")
    findings = {f["finding"] for f in result["style_findings"]}
    assert "unicode_confusables" in findings
    assert "uppercase_heavy" in findings

    result = tool.execute(mode="analyze", name="fix/🚀-logo")
    assert any(f["finding"] == "emoji_or_symbol" for f in result["style_findings"])

    result = tool.execute(mode="analyze", name="\u200bhidden/branch")
    assert any(f["finding"] == "invisible_chars" for f in result["style_findings"])

    long_name = "branch/" + "x" * 250
    result = tool.execute(mode="analyze", name=long_name)
    assert any(f["finding"] == "very_long" for f in result["style_findings"])


def test_shipped_config_documents_and_initializes_contract():
    config_path = (
        Path(__file__).resolve().parents[6]
        / "agentuniverse"
        / "agent"
        / "action"
        / "tool"
        / "common_tool"
        / "git_ref_name_tool.yaml"
    )
    with config_path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    assert config["input_keys"] == ["mode", "name"]
    description = config["description"]
    for parameter in ("mode", "name", "other_name", "ref_type", "allow_onelevel", "refspec_pattern", "violations"):
        assert parameter in description

    configer = Configer(str(config_path)).load()
    tool_configer = ToolConfiger(configer).load_by_configer(configer)
    loaded = DirectTool().initialize_by_component_configer(tool_configer)
    assert loaded.name == "git_ref_name_tool"
    assert loaded.input_keys == ["mode", "name"]
    assert loaded.max_name_chars == 1024


def test_package_export_matches_direct_import():
    assert GitRefNameTool is DirectTool


def test_invalid_arguments_raise(tool):
    with pytest.raises(ValueError, match="mode must be one of"):
        tool.execute(mode="lint", name="x")
    with pytest.raises(ValueError, match="ref_type must be one of"):
        tool.execute(name="x", ref_type="commit")
    with pytest.raises(ValueError, match="refspec_pattern applies to"):
        tool.execute(name="x", ref_type="branch", refspec_pattern=True)
    with pytest.raises(ValueError, match="name must be a string"):
        tool.execute(name=123)
    with pytest.raises(ValueError, match="name must be a string"):
        tool.execute(name=None)
    with pytest.raises(ValueError, match="compare mode requires other_name"):
        tool.execute(mode="compare", name="x")
    with pytest.raises(ValueError, match="at most"):
        tool.execute(name="x" * 2000)
    with pytest.raises(ValueError, match="must be booleans"):
        tool.execute(name="x", allow_onelevel="yes")


def test_violation_reporting_is_bounded_and_positional(tool):
    capped = GitRefNameTool(max_violations=2)
    result = capped.execute(mode="validate", name="a b~c^d")
    assert len(result["violations"]) == 2

    result = tool.execute(mode="validate", name="feature~x")
    violation = result["violations"][0]
    assert violation == {"rule": "forbidden_char", "position": 7, "char": "~"}

    result = tool.execute(mode="validate", name="feature\x01x", allow_onelevel=True)
    assert result["violations"][0]["rule"] == "control_char"
    assert result["violations"][0]["char"] == "\\x01"


def test_lock_suffix_is_case_sensitive_like_git(tool):
    assert tool.execute(mode="validate", name="foo.lock", allow_onelevel=True)["valid"] is False
    assert tool.execute(mode="validate", name="foo.LOCK", allow_onelevel=True)["valid"] is True
    assert tool.execute(mode="validate", name="a/b.lock/c")["valid"] is False


def test_component_dot_asymmetry_like_git(tool):
    assert tool.execute(mode="validate", name="a./b")["valid"] is True
    assert tool.execute(mode="validate", name="a./b.")["valid"] is False
    assert tool.execute(mode="validate", name=".a/b")["valid"] is False


def test_branch_mode_documented_subsemantics(tool):
    # '@' alone is a valid branch shorthand even though it is never a valid full ref.
    assert tool.execute(mode="validate", name="@", ref_type="branch")["valid"] is True
    # Stateful revision shorthands are rejected by the grammar (@{ rule).
    for shorthand in ("@{-1}", "@{u}", "@{upstream}"):
        result = tool.execute(mode="validate", name=shorthand, ref_type="branch")
        assert result["valid"] is False
        assert any(v["rule"] == "at_brace" for v in result["violations"])
