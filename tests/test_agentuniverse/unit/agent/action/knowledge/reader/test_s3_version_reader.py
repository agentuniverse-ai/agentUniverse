import io
import json
from copy import deepcopy
from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.knowledge.reader.cloud.s3_version_reader import S3ImportError, S3VersionReader
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.configer import Configer


def manifest(**changes):
    obj = {"key": "docs/a.txt", "version_id": "v1", "etag": '"opaque-multipart-2"', "size": 5}
    obj.update(changes)
    return {"schema_version": 1, "source_name": "test", "bucket": "test-bucket", "objects": [obj]}


@pytest.fixture
def reader():
    reader = S3VersionReader(bucket="test-bucket", source_name="test", readers={"txt": "test_txt"})
    reader._client = Mock()
    manager = ReaderManager()
    prior = dict(manager._instance_obj_map)
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    app = Configer()
    app.value = {"BASE_INFO": {"appname": "s3-reader-unit"}}
    apps.app_configer = AppConfiger().load_by_configer(app)
    delegate = TxtReader(name="test_txt")
    manager.register(delegate.get_instance_code(), delegate)
    try:
        yield reader
    finally:
        manager._instance_obj_map.clear()
        manager._instance_obj_map.update(prior)
        apps.app_configer = previous


def response(body=b"hello", **changes):
    result = {"Body": io.BytesIO(body), "ETag": '"opaque-multipart-2"', "ContentLength": 5, "VersionId": "v1"}
    result.update(changes)
    return result


def test_stream_delegation_identity_no_mutation_and_no_credentials(reader, tmp_path):
    original = manifest()
    before = deepcopy(original)
    metadata = {"labels": [1]}
    reader.client_args = {"aws_secret_access_key": "do-not-export"}
    reader._client.get_object.side_effect = [response(), response()]
    docs, report = reader.read_manifest_with_report(original, metadata)
    again, _ = reader.read_manifest_with_report(original, metadata)
    assert report["complete"] and docs[0].text == "hello"
    assert docs[0].id == again[0].id
    assert docs[0].metadata["file_name"] == "docs/a.txt"
    assert docs[0].metadata["s3_source"]["identity_mode"] == "version"
    docs[0].metadata["labels"].append(2)
    assert metadata == {"labels": [1]} and original == before
    assert "do-not-export" not in json.dumps([docs[0].model_dump(mode="json"), report, reader.model_dump(mode="json")])
    reader._client.get_object.assert_called_with(
        Bucket="test-bucket", Key="docs/a.txt", VersionId="v1", IfMatch='"opaque-multipart-2"'
    )


@pytest.mark.parametrize(
    "change",
    [
        {"version_id": None},
        {"version_id": "null"},
        {"version_id": True},
        {"size": -1},
        {"size": True},
        {"size": 10000001},
        {"etag": "unquoted"},
        {"key": ""},
        {"key": "文" * 400},
        {"sha256": "wrong"},
        {"extra": 1},
    ],
)
def test_manifest_rejected_before_io(reader, change):
    with pytest.raises(ValueError):
        reader.read_manifest_with_report(manifest(**change))
    reader._client.get_object.assert_not_called()


@pytest.mark.parametrize(
    "data",
    [
        {"schema_version": True},
        {"bucket": "other-bucket"},
        {"source_name": "other"},
        {"objects": [manifest()["objects"][0]] * 2},
        {"objects": {}},
        {"secret": "x"},
    ],
)
def test_manifest_structure(reader, data):
    request = manifest()
    request.update(data)
    with pytest.raises(ValueError):
        reader.read_manifest_with_report(request)


@pytest.mark.parametrize(
    "body,changes",
    [
        (b"hello!", {}),
        (b"hell", {}),
        (b"hello", {"VersionId": "new"}),
        (b"hello", {"ETag": '"new"'}),
        (b"hello", {"ContentLength": 8}),
        (b"hello", {"DeleteMarker": True}),
    ],
)
def test_changed_or_truncated_response_closes_stream(reader, body, changes):
    result = response(body, **changes)
    reader._client.get_object.return_value = result
    docs, report = reader.read_manifest_with_report(manifest())
    assert docs == [] and not report["complete"]
    assert result["Body"].closed


def test_public_reader_fails_closed_and_report_sanitizes_errors(reader, tmp_path):
    reader._client.get_object.side_effect = RuntimeError("secret-token-in-url")
    path = tmp_path / "test.s3manifest"
    path.write_text(json.dumps(manifest()), encoding="utf-8")
    with pytest.raises(S3ImportError) as error:
        reader.load_data(path)
    assert error.value.report["objects"][0]["error_type"] == "RuntimeError"
    assert "secret-token" not in str(error.value) + json.dumps(error.value.report)


def test_pagination_caps_and_repeated_tokens(reader):
    reader._client.list_objects_v2.return_value = {"IsTruncated": True, "NextContinuationToken": "same"}
    with pytest.raises(ValueError, match="token"):
        reader.capture_prefix("docs/")
    assert reader._client.list_objects_v2.call_count == 2
    reader.max_pages = 1
    with pytest.raises(ValueError, match="max_pages"):
        reader.capture_prefix("docs/")


def test_manifest_json_duplicate_and_budget(reader, tmp_path):
    path = tmp_path / "test.s3manifest"
    path.write_text('{"schema_version": 1, "schema_version": 1}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        reader.load_data(path)
    reader.max_manifest_bytes = 1
    with pytest.raises(ValueError, match="byte"):
        reader.load_data(path)


def test_explicit_null_version_uses_conditional_get(reader):
    reader.allow_unversioned = True
    reader._client.get_object.return_value = response(VersionId="null")
    docs, report = reader.read_manifest_with_report(manifest(version_id="null"))
    assert report["complete"]
    assert docs[0].metadata["s3_source"]["identity_mode"] == "conditional-etag"
    assert reader._client.get_object.call_args.kwargs["IfMatch"] == '"opaque-multipart-2"'


def test_partial_results_are_explicit_and_unsupported_types_do_not_download(reader):
    request = manifest()
    request["objects"].append({**request["objects"][0], "key": "b.exe"})
    reader._client.get_object.return_value = response()
    docs, report = reader.read_manifest_with_report(request)
    assert len(docs) == 1 and not report["complete"]
    assert [item["status"] for item in report["objects"]] == ["read", "failed"]
    assert reader._client.get_object.call_count == 1


def test_component_copy_has_independent_configuration_and_client(reader):
    copy = reader.create_copy()
    assert copy._client is None
    copy.readers["md"] = "other"
    copy.client_args["region_name"] = "other"
    assert "md" not in reader.readers and "region_name" not in reader.client_args
    assert reader._client is not None


def test_output_budget_and_reserved_metadata(reader):
    reader.max_output_chars = 4
    reader._client.get_object.return_value = response()
    docs, report = reader.read_manifest_with_report(manifest())
    assert docs == [] and report["objects"][0]["stage"] == "output_validation"
    for metadata in ([], {"s3_source": "override"}):
        with pytest.raises(ValueError, match="ext_info"):
            reader.read_manifest_with_report(manifest(), metadata)


def test_total_download_budget_preflight(reader):
    reader.max_total_bytes = 4
    with pytest.raises(ValueError, match="budget"):
        reader.read_manifest_with_report(manifest())
    reader._client.get_object.assert_not_called()
