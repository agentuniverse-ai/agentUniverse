"""Corpus impact fixtures cover source identity, chunking and citation anchors."""

import copy
import hashlib
import json
import subprocess
import sys

import pytest

from agentuniverse.agent.action.knowledge.corpus_impact import compare_corpora, source_record


def manifest(*rows):
    return {"version": 1, "sources": list(rows)}


def source(text="one\ntwo\nthree\n", key="s", location="old.txt", chunks=()):
    return source_record(key, text, location=location, chunks=chunks)


def ref(**kwargs):
    return {"id": "citation", "source_id": "s", **kwargs}


def test_source_edit_and_affected_line_anchor():
    before, after = manifest(source()), manifest(source("one\nchanged\nthree\n"))
    report = compare_corpora(before, after, [ref(start_line=2, end_line=2)])
    assert report["sources"][0]["content_changed"]
    assert report["sources"][0]["line_diff"] == [
        {"operation": "replace", "old_start": 1, "old_end": 2, "new_start": 1, "new_end": 2}
    ]
    assert report["references"][0]["reasons"] == ["source_content_changed", "anchor_changed"]


@pytest.mark.parametrize(
    "text,start,end,reason",
    [
        ("zero\none\ntwo\nthree\n", 2, 2, "anchor_shifted"),
        ("one\ntwo\nchanged\n", 1, 2, "anchor_unchanged"),
        ("one\nthree\n", 2, 2, "anchor_changed"),
        ("one\ninserted\ntwo\nthree\n", 1, 2, "anchor_changed"),
        ("one\ntwo\nthree", 3, 3, "anchor_changed"),
        ("one\r\ntwo\r\nthree\r\n", 1, 1, "anchor_changed"),
    ],
)
def test_line_mapping(text, start, end, reason):
    report = compare_corpora(manifest(source()), manifest(source(text)), [ref(start_line=start, end_line=end)])
    assert report["references"][0]["status"] == "affected"
    assert reason in report["references"][0]["reasons"]


def test_chunk_boundary_change_does_not_claim_source_changed():
    before = manifest(source(chunks=[{"id": "c", "text": "one\ntwo\nthree\n"}]))
    after = manifest(source(chunks=[{"id": "c1", "text": "one\n"}, {"id": "c2", "text": "two\nthree\n"}]))
    report = compare_corpora(before, after, [ref(chunk_id="c"), {"id": "source-only", "source_id": "s"}])
    assert report["sources"][0]["content_changed"] is False
    assert report["sources"][0]["chunks_changed"] is True
    assert report["references"][0]["reasons"] == ["chunk_removed"]
    assert report["references"][1]["status"] == "unchanged"


def test_path_rename_and_identity_hints_are_separate():
    old = manifest(source())
    moved = manifest(source(location="renamed.txt"))
    report = compare_corpora(old, moved, [ref()])
    assert report["added"] == report["removed"] == []
    assert report["references"][0]["reasons"] == ["source_location_changed"]
    new_id = manifest(source(key="new"))
    report = compare_corpora(old, new_id, [ref()])
    assert report["added"] == ["new"] and report["removed"] == ["s"]
    assert report["references"][0]["reasons"] == ["source_removed"]
    assert report["possible_identity_matches"] == [
        {"old_source_id": "s", "new_source_id": "new", "evidence": "equal_content_hash_only"}
    ]


def test_unknown_references_and_budget_are_explicit():
    a, b = manifest(source()), manifest(source("changed\ntext\n"))
    report = compare_corpora(
        a,
        b,
        [
            ref(start_line=1, end_line=1),
            {"id": "unknown", "source_id": "absent"},
            {"id": "bad-chunk", "source_id": "s", "chunk_id": "absent"},
        ],
        max_line_pairs=1,
    )
    assert report["sources"][0]["line_diff_status"] == "budget_exceeded"
    assert report["references"][1]["reasons"] == ["source_content_changed", "line_mapping_unavailable"]
    assert sum(r["status"] == "unresolved" for r in report["references"]) == 2


@pytest.mark.parametrize(
    "mutation",
    [
        lambda m: m.update(version=2),
        lambda m: m.update(version=True),
        lambda m: m["sources"].append(copy.deepcopy(m["sources"][0])),
        lambda m: m["sources"][0].update(text="tampered"),
        lambda m: m["sources"][0].update(sha256="0" * 64),
        lambda m: m["sources"][0].update(id=[]),
        lambda m: m["sources"][0].update(extra="unsupported"),
        lambda m: m["sources"][0]["chunks"].append(copy.deepcopy(m["sources"][0]["chunks"][0])),
        lambda m: m["sources"][0]["chunks"][0].update(text="tampered"),
    ],
)
def test_validate_both_manifests_before_comparison(mutation):
    good = manifest(source(chunks=[{"id": "c", "text": "one"}]))
    bad = copy.deepcopy(good)
    mutation(bad)
    for a, b in [(good, bad), (bad, good)]:
        with pytest.raises(ValueError):
            compare_corpora(a, b)


@pytest.mark.parametrize(
    "reference",
    [
        ref(start_line=0, end_line=1),
        ref(start_line=True, end_line=2),
        ref(start_line=1),
        ref(start_line=2, end_line=1),
        ref(start_line=1, end_line=4),
        ref(extra=1),
    ],
)
def test_invalid_references(reference):
    with pytest.raises(ValueError):
        compare_corpora(manifest(source()), manifest(source()), [reference])


def test_deterministic_no_mutation_and_limits():
    a = manifest(source(key="b"), source(key="a"))
    b = manifest(source(key="a", location="moved"), source(key="b"))
    saved = copy.deepcopy((a, b))
    report = compare_corpora(a, b)
    assert (a, b) == saved
    a["sources"].reverse()
    b["sources"].reverse()
    assert compare_corpora(a, b) == report
    for kwargs in [{"max_sources": 1}, {"max_bytes": 1}, {"max_line_pairs": True}]:
        with pytest.raises(ValueError):
            compare_corpora(a, b, **kwargs)
    with pytest.raises(ValueError):
        compare_corpora(a, b, [ref(), ref()])


def test_real_documents_and_cli(tmp_path):
    from agentuniverse.agent.action.knowledge.store.document import Document

    docs = [Document(id="c", text="one\ntwo\nthree\n")]
    a = manifest(source(chunks=[{"id": d.id, "text": d.text} for d in docs]))
    b = manifest(source("one\nmodified\nthree\n", chunks=[{"id": "c", "text": "one\nmodified\nthree\n"}]))
    old_path, new_path, ref_path = [tmp_path / name for name in ["old.json", "new.json", "refs.json"]]
    for path, data in [(old_path, a), (new_path, b), (ref_path, [ref(chunk_id="c")])]:
        path.write_text(json.dumps(data), encoding="utf-8")
    hashes = [hashlib.sha256(p.read_bytes()).hexdigest() for p in [old_path, new_path, ref_path]]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "agentuniverse.agent.action.knowledge.corpus_impact",
            str(old_path),
            str(new_path),
            "--references",
            str(ref_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(result.stdout)
    assert report == compare_corpora(a, b, [ref(chunk_id="c")])
    assert report["references"][0]["reasons"] == ["source_content_changed", "chunk_content_changed"]
    assert hashes == [hashlib.sha256(p.read_bytes()).hexdigest() for p in [old_path, new_path, ref_path]]


def test_cli_rejects_duplicate_json_keys(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"version":1,"version":1,"sources":[]}', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "agentuniverse.agent.action.knowledge.corpus_impact", str(path), str(path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0 and "duplicate JSON key" in result.stderr


def test_ambiguous_hash_candidates_have_output_budget():
    a = manifest(source(key="old-a"), source(key="old-b"))
    b = manifest(source(key="new-a"), source(key="new-b"))
    report = compare_corpora(a, b, max_identity_matches=1)
    assert len(report["possible_identity_matches"]) == 1
    assert report["identity_matches_truncated"] is True
    assert report["added"] == ["new-a", "new-b"]
    assert report["removed"] == ["old-a", "old-b"]
