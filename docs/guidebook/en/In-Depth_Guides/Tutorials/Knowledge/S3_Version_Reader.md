# Version-pinned S3 knowledge import

`S3VersionReader` separates **capturing object identities** from downloading and parsing them. A reusable manifest pins each version, and resulting Documents retain the bucket/key/version, opaque ETag, observed SHA-256, namespace and delegate Reader. This avoids quietly importing the newest object after the object used to prepare an ingestion job has changed.

It is opt-in and leaves existing cloud/local Readers unchanged. Format parsing is delegated to registered local file Readers, not reimplemented. A manifest is **not an atomic bucket-wide snapshot**: objects may be added or removed while listing/HEAD requests run.

## Configuration and public Knowledge integration

Install `agentuniverse[s3_reader_ext]` (boto3 >=1.35.99,<2; tested with 1.35.99). Configure normal AWS credentials outside manifests and document metadata. Copy `agentuniverse/agent/action/knowledge/reader/cloud/s3_version_reader.yaml.example` into the application Reader scan path; set an authorized bucket, a stable `source_name` namespace and an explicit suffix-to-Reader mapping. Bootstrap the application so the delegated Readers are registered. Use a distinct namespace for another account/service, including local S3-compatible endpoints.

`client_args` is passed to `boto3.client('s3', ...)`, for example `region_name`, `endpoint_url` or a TLS verification configuration. Prefer normal credential providers over keys embedded in YAML. `client_args` is excluded from the model's standard representation/dump. This does not sanitize caller-supplied document text/metadata or logs produced by another component. The manifest cannot select credentials, endpoint, a different configured bucket or a different Reader implementation.

```python
import json
from pathlib import Path
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager

# After application bootstrap loads the Reader YAML and the configured TxtReader:
reader = ReaderManager().get_instance_obj("s3_version_reader", strict=True)
try:
    manifest = reader.capture_prefix("manuals/")
    Path("manuals.s3manifest").write_text(json.dumps(manifest), encoding="utf-8")
    documents = reader.load_data(Path("manuals.s3manifest"))
finally:
    reader.close()
```

In a Knowledge configuration, map `readers: {s3manifest: s3_version_reader}` and call `knowledge.insert_knowledge(source_path='manuals.s3manifest')`. Capturing is an explicit prior step, not an automatic refresh on every load. The Reader performs GET/HEAD/list operations only, and never modifies S3 objects. Public `load_data` closes its SDK client even on an import failure; explicit capture/partial-result users should call `close()` themselves. Component copies do not share SDK clients or mutable configuration.

## Manifest version 1

```json
{
  "schema_version": 1,
  "source_name": "aws-s3",
  "bucket": "your-authorized-bucket",
  "objects": [{
    "key": "manuals/manual.txt",
    "version_id": "the-actual-version-returned-by-s3",
    "etag": "\"the-actual-opaque-etag\"",
    "size": 1234
  }]
}
```

Use actual HEAD results, not these placeholders. Each entry may additionally specify a lowercase SHA-256 to verify. Duplicate JSON keys, duplicate object keys, unknown fields, wrong namespace/bucket, invalid version/ETag/size and configured resource-limit violations fail before reads. Multiple versions of the same key require separate manifests.

`capture_prefix` pages ListObjectsV2, HEADs each key to capture its then-current identity, sorts the resulting entries, and rejects page/token/count/byte overflows without returning a truncated manifest. An empty prefix deliberately selects the whole configured bucket; narrow it for large buckets. Unsupported suffixes are reported at import, not silently filtered out of a capture. Captured old versions may later become unavailable due to lifecycle deletion or access changes.

## Versions, conditional reads and provenance

The default `allow_unversioned: false` requires a non-null immutable VersionId. Each download sends that VersionId and `IfMatch`, checks response identity/length, consumes the body with a bounded byte count and computes SHA-256. ETag is an opaque condition, **not assumed to be MD5**. A short/long stream, mismatched version/ETag/length or optional SHA-256 mismatch fails before parsing. Bodies and temporary files are closed/removed on failures.

Explicitly enable `allow_unversioned` for non-versioned/suspended objects. Missing VersionId and the literal `"null"` are mutable; these use conditional ETag reads and are labeled `identity_mode: conditional-etag`. Compatible services may omit the null-version response header. This weaker mode detects differing ETags but **does not prove immutable identity**, metadata-only change detection, or protection against replacement with identical content/ETag. A provider that ignores conditions is still checked for returned ETag/size, not assumed fully AWS-compatible.

Each output has `metadata.s3_source`, including the exact key/version, observed content hash, delegate name and identity mode; `file_name` is the S3 key rather than the temporary basename. Document IDs hash provenance, output ordinal and text. Repeated imports with the same object/Reader output are stable; this does not deduplicate a Store automatically, fingerprint the entire parser environment, or replace application-level source synchronization. Reserve `s3_source`: callers cannot overwrite it via `ext_info`. Remote metadata headers and credentials are not copied into provenance. User-controlled source content can of course itself contain sensitive data.

## Errors and limits

`load_data` raises `S3ImportError` when **any** object fails, exposing `error.report` and returning no partial list. The report identifies the key, stage (`reader_lookup`, `download`, `parse`, `output_validation`), exception class, and a sanitized service error code when available. It intentionally omits raw exception messages that can contain URLs/headers/credentials.

For a deliberate partial workflow, call `documents, report = reader.read_manifest_with_report(manifest)` and inspect `report['complete']` before deciding what to ingest. Successful entries include the document count and SHA-256, including zero-output parses. This API makes partial ingestion the caller's explicit choice; it is not a transactional Store commit. Knowledge's downstream Store acknowledgements remain governed by the existing Store API.

Count, declared/downloaded bytes, manifest size, output Document count and text-character limits are configurable. Temporary object filenames are generated locally, not built from object paths. Registered parsers run in-process: output limits are checked after parsing and do not sandbox parser CPU/memory, prevent decompression bombs, or make arbitrary parsers safe. Use trusted, appropriately bounded file Readers for your content. Connect/read timeouts are socket timeouts, not a whole-job deadline. SDK retry attempts are limited to one; no application retry, automatic bucket creation, async import or resumable ingestion ledger is included.

Ordinary buckets/path-style requests only. Directory buckets, access-point ARNs, requester-pays options and SSE-C headers are not supported by this component. AWS IAM, KMS, Object Lock, multipart edge cases and all S3-compatible vendors have not been live-tested; configure permissions for list/HEAD/version GET as appropriate.

## Actual validation and reproduction

Real integration tests use a local MinIO service built from official source commit `9e49d5e7a648f00e26f2246f4dc28e6b07f8c84a` (release tag `RELEASE.2025-10-15T17-29-55Z`) with Go 1.27.1. The binary labels itself DEVELOPMENT.GOGET because it is source-built; it is not claimed to be an official release image. No AWS account was used.

```sh
docker build -t au-s3-test tests/test_agentuniverse/integration/s3_service
docker run --name au-s3-test -p 127.0.0.1:19000:9000 -e MINIO_ROOT_USER=au_test_only -e MINIO_ROOT_PASSWORD=au_test_only_password au-s3-test server /data --console-address :9001
AU_S3_TEST_URL=http://127.0.0.1:19000 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest --import-mode=importlib tests/test_agentuniverse/unit/agent/action/knowledge/reader/test_s3_version_reader.py tests/test_agentuniverse/integration/test_s3_version_reader.py
```

Install project runtime/test dependencies and the extra first. This disposable fixture uses documented test-only credentials, binds only loopback, and is **not production deployment guidance**. Building downloads dependencies and requires disk space. Each test creates/removes its own unique bucket and versions; the fixture rejects non-loopback URLs. Tests cover multipage capture, overwrite/delete-marker old-version reads, mutable conditional failures, missing versions, checksum/output limits, sanitized reports, client-copy isolation and registered Reader → real MinIO → real SQLite → public Knowledge retrieval with version provenance.

Protocol references: [GetObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html), [HeadObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_HeadObject.html), [ListObjectsV2](https://docs.aws.amazon.com/boto3/latest/reference/services/s3/paginator/ListObjectsV2.html).
