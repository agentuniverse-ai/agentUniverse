"""Versioned, bounded offline Document bundles; no extraction or store mutation."""

import hashlib
import io
import json
import os
import tempfile
import zipfile
from pathlib import Path

from agentuniverse.agent.action.knowledge.store.document import Document

FORMAT = "agentuniverse-document-bundle"
VERSION = 1
DEFAULT_MAX_BYTES = 64 * 1024 * 1024


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _parse(data):
    def reject(value):
        raise ValueError("non-finite JSON number")

    return json.loads(data.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=reject)


def _keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError("invalid bundle object fields")


def _id(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 1024:
        raise ValueError("IDs must be nonempty strings of at most 1024 characters")
    return value


def _limit(value):
    if type(value) is not int or value <= 0:
        raise ValueError("limits must be positive integers")
    return value


def export_bundle(
    path,
    documents,
    *,
    sources,
    document_sources,
    metadata_keys=(),
    max_bytes=DEFAULT_MAX_BYTES,
    max_documents=10_000,
    max_sources=1000,
):
    """Create a new portable bundle without overwriting an existing path.

    Args:
        path: New local destination (parent must exist).
        documents: Selected Documents; IDs must be unique.
        sources: Stable source ID -> explicitly supplied source text, not paths.
        document_sources: Document ID -> nonempty list of source IDs. These are
            caller-asserted associations, not proof of textual derivation.
        metadata_keys: Explicit top-level metadata allowlist; default exports none.
            Review selected metadata and text before exporting sensitive content.
        max_bytes: Maximum final archive bytes and total uncompressed bytes.
        max_documents: Document count limit.
        max_sources: Source count limit.

    Returns:
        SHA-256 of the complete written archive. Keep this separately to detect
        substitution; internal hashes alone do not authenticate an author.

    Raises:
        ValueError: Invalid input or exceeded limits.
        OSError: Publication failed or destination already exists.
    """
    for limit in (max_bytes, max_documents, max_sources):
        _limit(limit)
    if not isinstance(sources, dict) or len(sources) > max_sources:
        raise ValueError("sources must be a bounded ID-to-text mapping")
    if not isinstance(document_sources, dict):
        raise ValueError("document_sources must be a mapping")
    if isinstance(metadata_keys, str):
        raise ValueError("metadata_keys must be a collection")
    allowed = set(metadata_keys)
    if any(not isinstance(key, str) or key == "_corpus_bundle" for key in allowed):
        raise ValueError("invalid or reserved metadata key")
    entries, source_rows, doc_rows = {}, [], []
    total = 0

    def add(member, data):
        nonlocal total
        total += len(data)
        if total > max_bytes:
            raise ValueError("bundle byte limit exceeded")
        entries[member] = data
        return dict(member=member, sha256=_digest(data))

    for source_id in sources:
        _id(source_id)
    for index, source_id in enumerate(sorted(sources)):
        _id(source_id)
        text = sources[source_id]
        if not isinstance(text, str):
            raise ValueError("source text must be a string")
        source_rows.append(dict(id=source_id, **add(f"sources/{index}.txt", text.encode("utf-8"))))
    seen = set()
    for index, doc in enumerate(documents):
        if index >= max_documents or not isinstance(doc, Document):
            raise ValueError("invalid Document or document count limit exceeded")
        doc_id = _id(doc.id)
        if doc_id in seen:
            raise ValueError("duplicate document ID")
        seen.add(doc_id)
        links = document_sources.get(doc_id)
        if not isinstance(links, list) or not links or any(not isinstance(link, str) for link in links):
            raise ValueError("each document requires source IDs")
        if len(set(links)) != len(links) or not set(links) <= set(sources):
            raise ValueError("duplicate or missing source reference")
        if not isinstance(doc.text, str):
            raise ValueError("document text must be a string")
        payload = dict(
            id=doc_id,
            text=doc.text,
            keywords=sorted(doc.keywords),
            metadata={key: value for key, value in (doc.metadata or {}).items() if key in allowed},
        )
        data = _json(payload)
        # Verify JSON metadata round-trip without silently coercing mapping keys.
        if _parse(data) != payload:
            raise ValueError("selected metadata must be lossless JSON values")
        doc_rows.append(dict(id=doc_id, sources=links, **add(f"documents/{index}.json", data)))
    if set(document_sources) != seen:
        raise ValueError("document_sources must exactly match the document IDs")
    manifest = dict(format=FORMAT, version=VERSION, sources=source_rows, documents=doc_rows)
    add("manifest.json", _json(manifest))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in entries.items():
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            archive.writestr(entry, data)
    raw = buffer.getvalue()
    if len(raw) > max_bytes:
        raise ValueError("archive byte limit exceeded")
    destination = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".au-bundle-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        # An atomic no-clobber publication on supported local filesystems.
        # Fail rather than falling back to an incomplete destination write.
        os.link(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return _digest(raw)


def load_bundle(path, *, expected_sha256=None, max_bytes=DEFAULT_MAX_BYTES, max_documents=10_000, max_sources=1000):
    """Validate the whole bundle before returning Documents for explicit insertion.

    No archive member is extracted or opened as a filesystem path. Embeddings,
    runtime objects and credentials are not interpreted. Metadata is plain JSON.
    An optional externally retained archive hash detects whole-bundle replacement.
    Returns a list only after every source/document/member has passed validation.
    Raises ValueError for invalid bundles/limits and OSError for local read errors.
    """
    for limit in (max_bytes, max_documents, max_sources):
        _limit(limit)
    with Path(path).open("rb") as stream:
        raw = stream.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError("archive byte limit exceeded")
    archive_hash = _digest(raw)
    if expected_sha256 is not None and expected_sha256 != archive_hash:
        raise ValueError("archive digest mismatch")
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = archive.infolist()
            names = [entry.filename for entry in infos]
            if len(infos) > 1 + max_documents + max_sources or len(set(names)) != len(names):
                raise ValueError("duplicate members or member count limit exceeded")
            if sum(entry.file_size for entry in infos) > max_bytes:
                raise ValueError("uncompressed byte limit exceeded")
            if any(entry.compress_type != zipfile.ZIP_STORED or entry.flag_bits & 1 for entry in infos):
                raise ValueError("only unencrypted stored ZIP members are supported")
            manifest = _parse(archive.read("manifest.json"))
            _keys(manifest, ["format", "version", "sources", "documents"])
            if manifest["format"] != FORMAT or type(manifest["version"]) is not int or manifest["version"] != VERSION:
                raise ValueError("unsupported bundle format/version")
            source_rows, doc_rows = manifest["sources"], manifest["documents"]
            if not isinstance(source_rows, list) or len(source_rows) > max_sources:
                raise ValueError("invalid source list")
            if not isinstance(doc_rows, list) or len(doc_rows) > max_documents:
                raise ValueError("invalid document list")
            expected = {"manifest.json"}
            source_hashes, doc_ids, documents = {}, set(), []

            def member(row, name):
                if row["member"] != name:
                    raise ValueError("noncanonical member name")
                expected.add(name)
                data = archive.read(name)
                if row["sha256"] != _digest(data):
                    raise ValueError("member digest mismatch")
                return data

            for index, row in enumerate(source_rows):
                _keys(row, ["id", "member", "sha256"])
                source_id = _id(row["id"])
                if source_id in source_hashes:
                    raise ValueError("duplicate source ID")
                member(row, f"sources/{index}.txt").decode("utf-8")
                source_hashes[source_id] = row["sha256"]
            for index, row in enumerate(doc_rows):
                _keys(row, ["id", "member", "sha256", "sources"])
                doc_id = _id(row["id"])
                if doc_id in doc_ids:
                    raise ValueError("duplicate document ID")
                doc_ids.add(doc_id)
                links = row["sources"]
                if not isinstance(links, list) or not links or any(not isinstance(link, str) for link in links):
                    raise ValueError("invalid document source references")
                if len(set(links)) != len(links) or not set(links) <= set(source_hashes):
                    raise ValueError("missing or duplicate document source references")
                payload = _parse(member(row, f"documents/{index}.json"))
                _json(payload)  # Reject exponent overflow to infinity as well as NaN.
                _keys(payload, ["id", "text", "metadata", "keywords"])
                if payload["id"] != doc_id or not isinstance(payload["text"], str):
                    raise ValueError("invalid document identity/text")
                metadata, keywords = payload["metadata"], payload["keywords"]
                if not isinstance(metadata, dict) or "_corpus_bundle" in metadata:
                    raise ValueError("invalid or reserved metadata")
                if not isinstance(keywords, list) or any(not isinstance(word, str) for word in keywords):
                    raise ValueError("invalid keywords")
                if len(set(keywords)) != len(keywords):
                    raise ValueError("duplicate keywords")
                metadata["_corpus_bundle"] = dict(
                    sha256=archive_hash,
                    document_sha256=row["sha256"],
                    sources={key: source_hashes[key] for key in links},
                    version=VERSION,
                )
                documents.append(Document(id=doc_id, text=payload["text"], metadata=metadata, keywords=set(keywords)))
            if expected != set(names):
                raise ValueError("unexpected or missing archive members")
            return documents
    except (zipfile.BadZipFile, KeyError, UnicodeError, TypeError, RecursionError, NotImplementedError) as exc:
        raise ValueError("invalid document bundle") from exc
