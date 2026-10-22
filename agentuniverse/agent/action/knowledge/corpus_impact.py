"""Read-only corpus version impact reports with verified text and chunk hashes."""

import argparse
import difflib
import hashlib
import json
from pathlib import Path


def text_digest(text):
    """Hash exact UTF-8 text; newline/Unicode normalization is never implicit."""
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_record(source_id, text, *, location="", chunks=()):
    """Build one source record from explicit text and {id, text} chunk records.

    Chunk associations are caller assertions, not a claim of verified derivation.
    Stable source IDs establish identity independently of filesystem locations.
    """
    return dict(
        id=source_id,
        text=text,
        sha256=text_digest(text),
        location=location,
        chunks=[dict(id=chunk["id"], text=chunk["text"], sha256=text_digest(chunk["text"])) for chunk in chunks],
    )


def _validate(manifest, max_sources, max_bytes, max_chunks):
    if not isinstance(manifest, dict) or set(manifest) != {"version", "sources"}:
        raise ValueError("manifest requires only version and sources")
    if type(manifest["version"]) is not int or manifest["version"] != 1:
        raise ValueError("unsupported manifest version")
    rows = manifest["sources"]
    if not isinstance(rows, list) or len(rows) > max_sources:
        raise ValueError("invalid source list or source count limit")
    index, chunk_ids, size = {}, set(), 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "text", "sha256", "location", "chunks"}:
            raise ValueError("invalid source fields")
        key = row["id"]
        if not isinstance(key, str) or not key or len(key) > 1024 or key in index:
            raise ValueError("invalid or duplicate source ID")
        if not isinstance(row["location"], str) or len(row["location"]) > 4096:
            raise ValueError("invalid location label")
        if row["sha256"] != text_digest(row["text"]):
            raise ValueError("source digest mismatch")
        size += len(row["text"].encode("utf-8"))
        chunks = row["chunks"]
        if not isinstance(chunks, list):
            raise ValueError("invalid chunks")
        for chunk in chunks:
            if not isinstance(chunk, dict) or set(chunk) != {"id", "text", "sha256"}:
                raise ValueError("invalid chunk fields")
            chunk_id = chunk["id"]
            if not isinstance(chunk_id, str) or not chunk_id or len(chunk_id) > 1024 or chunk_id in chunk_ids:
                raise ValueError("invalid or duplicate chunk ID")
            chunk_ids.add(chunk_id)
            if len(chunk_ids) > max_chunks or chunk["sha256"] != text_digest(chunk["text"]):
                raise ValueError("chunk limit or digest mismatch")
            size += len(chunk["text"].encode("utf-8"))
        if size > max_bytes:
            raise ValueError("text byte limit exceeded")
        index[key] = row
    return index


def compare_corpora(
    before,
    after,
    references=(),
    *,
    max_sources=1000,
    max_bytes=16_777_216,
    max_chunks=10_000,
    max_references=10_000,
    max_line_pairs=1_000_000,
    max_identity_matches=1000,
):
    """Verify both V1 manifests and report source/chunk/reference impact.

    References are {id, source_id} with optional chunk_id and paired start_line /
    end_line (one-based inclusive bounds in the OLD source). Unknown targets are
    reported unresolved. Every reference with changed source content needs review;
    line mapping only narrows whether its old anchor changed, shifted or survived.
    It cannot establish semantic validity. Matching hashes across different IDs
    are reported as possible identity matches, never silently merged.

    Inputs remain untouched. No Store operations, imports, model calls or network
    access occur. Raises ValueError for invalid manifests, references or limits.
    """
    for limit in (max_sources, max_bytes, max_chunks, max_references, max_line_pairs, max_identity_matches):
        if type(limit) is not int or limit <= 0:
            raise ValueError("limits must be positive integers")
    old = _validate(before, max_sources, max_bytes, max_chunks)
    new = _validate(after, max_sources, max_bytes, max_chunks)
    added, removed = sorted(new.keys() - old.keys()), sorted(old.keys() - new.keys())
    changes, operations = {}, {}
    for key in sorted(old.keys() & new.keys()):
        a, b = old[key], new[key]
        content_changed = a["sha256"] != b["sha256"]
        chunks_a = {c["id"]: c["sha256"] for c in a["chunks"]}
        chunks_b = {c["id"]: c["sha256"] for c in b["chunks"]}
        change = dict(
            source_id=key,
            content_changed=content_changed,
            location_changed=a["location"] != b["location"],
            chunks_changed=chunks_a != chunks_b,
            line_diff=[],
            line_diff_status="unchanged",
        )
        if content_changed:
            lines_a, lines_b = a["text"].splitlines(keepends=True), b["text"].splitlines(keepends=True)
            if len(lines_a) * len(lines_b) > max_line_pairs:
                change["line_diff_status"] = "budget_exceeded"
            else:
                ops = difflib.SequenceMatcher(None, lines_a, lines_b, autojunk=False).get_opcodes()
                operations[key] = ops
                change["line_diff_status"] = "computed"
                change["line_diff"] = [
                    dict(operation=tag, old_start=i, old_end=j, new_start=k, new_end=new_end)
                    for tag, i, j, k, new_end in ops
                    if tag != "equal"
                ]
        changes[key] = change
    impacts, seen = [], set()
    for index, ref in enumerate(references):
        if index >= max_references or not isinstance(ref, dict):
            raise ValueError("reference count limit or invalid reference")
        if not {"id", "source_id"} <= ref.keys() or not set(ref) <= {
            "id",
            "source_id",
            "chunk_id",
            "start_line",
            "end_line",
        }:
            raise ValueError("invalid reference fields")
        for field in ("id", "source_id", "chunk_id"):
            if field in ref and (not isinstance(ref[field], str) or not ref[field] or len(ref[field]) > 1024):
                raise ValueError("reference IDs must be nonempty strings")
        if ref["id"] in seen:
            raise ValueError("duplicate reference ID")
        seen.add(ref["id"])
        if ("start_line" in ref) != ("end_line" in ref):
            raise ValueError("line bounds must be paired")
        key = ref["source_id"]
        if "start_line" in ref:
            start, end = ref["start_line"], ref["end_line"]
            if type(start) is not int or type(end) is not int or not 1 <= start <= end:
                raise ValueError("invalid line bounds")
            if key in old and end > len(old[key]["text"].splitlines(keepends=True)):
                raise ValueError("reference exceeds old source lines")
        reasons, status = [], "unchanged"
        if key not in old:
            reasons, status = ["unknown_old_source"], "unresolved"
        elif "chunk_id" in ref and ref["chunk_id"] not in {c["id"] for c in old[key]["chunks"]}:
            reasons, status = ["unknown_old_chunk"], "unresolved"
        elif key not in new:
            reasons, status = ["source_removed"], "affected"
        else:
            change = changes[key]
            if change["content_changed"]:
                reasons.append("source_content_changed")
                if "start_line" in ref:
                    anchor = "line_mapping_unavailable"
                    if key in operations:
                        anchor = "anchor_changed"
                        for tag, i, j, k, new_end in operations[key]:
                            if tag == "equal" and i <= start - 1 and end <= j:
                                anchor = "anchor_shifted" if i != k else "anchor_unchanged"
                                break
                    reasons.append(anchor)
            if change["location_changed"]:
                reasons.append("source_location_changed")
            if "chunk_id" in ref:
                chunk_id = ref["chunk_id"]
                a_chunks = {c["id"]: c["sha256"] for c in old[key]["chunks"]}
                b_chunks = {c["id"]: c["sha256"] for c in new[key]["chunks"]}
                if chunk_id not in b_chunks:
                    reasons.append("chunk_removed")
                elif a_chunks[chunk_id] != b_chunks[chunk_id]:
                    reasons.append("chunk_content_changed")
            if reasons:
                status = "affected"
        impacts.append(dict(reference_id=ref["id"], source_id=key, status=status, reasons=reasons))
    # Hash-equivalent candidates are only hints: identical boilerplate is common.
    candidates = (
        dict(old_source_id=a, new_source_id=b, evidence="equal_content_hash_only")
        for a in removed
        for b in added
        if old[a]["sha256"] == new[b]["sha256"]
    )
    bounded_candidates = []
    matches_truncated = False
    for candidate in candidates:
        if len(bounded_candidates) >= max_identity_matches:
            matches_truncated = True
            break
        bounded_candidates.append(candidate)
    return dict(
        version=1,
        added=added,
        removed=removed,
        sources=[changes[key] for key in sorted(changes)],
        references=sorted(impacts, key=lambda row: row["reference_id"]),
        possible_identity_matches=bounded_candidates,
        identity_matches_truncated=matches_truncated,
        line_coordinates="zero-based half-open; reference bounds are one-based inclusive",
    )


def _read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    with Path(path).open("rb") as stream:
        raw = stream.read(32 * 1024 * 1024 + 1)
    if len(raw) > 32 * 1024 * 1024:
        raise ValueError("JSON input byte limit exceeded")
    return json.loads(raw, object_pairs_hook=unique)


def main():
    """Compare local JSON manifests without modifying either file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--references")
    args = parser.parse_args()
    report = compare_corpora(
        _read_json(args.before), _read_json(args.after), _read_json(args.references) if args.references else ()
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
