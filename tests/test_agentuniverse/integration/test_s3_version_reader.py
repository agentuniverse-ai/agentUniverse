"""Real local S3-compatible service; explicitly opt in with AU_S3_TEST_URL."""

import json
import os
import shutil
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit
from uuid import uuid4

import pytest

from agentuniverse.agent.action.knowledge.reader.cloud.s3_version_reader import S3ImportError, S3VersionReader
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.configer import Configer


@pytest.fixture
def source(monkeypatch):
    endpoint = os.environ.get("AU_S3_TEST_URL")
    if not endpoint:
        pytest.skip("set AU_S3_TEST_URL to a disposable loopback S3 service")
    if urlsplit(endpoint).hostname not in ("127.0.0.1", "localhost", "::1"):
        pytest.fail("integration tests only accept a loopback service")
    boto3 = pytest.importorskip("boto3")
    from botocore.config import Config

    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost,::1")
    args = dict(
        endpoint_url=endpoint,
        region_name="us-east-1",
        aws_access_key_id="au_test_only",
        aws_secret_access_key="au_test_only_password",
    )
    client = boto3.client("s3", config=Config(proxies={}, s3={"addressing_style": "path"}), **args)
    bucket = "au-test-" + uuid4().hex
    client.create_bucket(Bucket=bucket)
    client.put_bucket_versioning(Bucket=bucket, VersioningConfiguration={"Status": "Enabled"})
    reader = S3VersionReader(
        bucket=bucket, source_name="local-minio-test", readers={"txt": "s3_test_txt"}, client_args=args, page_size=1
    )
    manager = ReaderManager()
    pool = dict(manager._instance_obj_map)
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    app = Configer()
    app.value = {"BASE_INFO": {"appname": "s3-integration"}}
    apps.app_configer = AppConfiger().load_by_configer(app)
    delegate = TxtReader(name="s3_test_txt")
    manager.register(delegate.get_instance_code(), delegate)
    try:
        yield client, reader
    finally:
        reader.close()
        # Only this fixture's newly-created bucket is ever deleted.
        pages = client.get_paginator("list_object_versions").paginate(Bucket=bucket)
        versions = [
            dict(Key=item["Key"], VersionId=item["VersionId"])
            for page in pages
            for field in ("Versions", "DeleteMarkers")
            for item in page.get(field, [])
        ]
        for offset in range(0, len(versions), 1000):
            client.delete_objects(Bucket=bucket, Delete={"Objects": versions[offset : offset + 1000]})
        client.delete_bucket(Bucket=bucket)
        client.close()
        manager._instance_obj_map.clear()
        manager._instance_obj_map.update(pool)
        apps.app_configer = previous


def test_real_pagination_pins_old_versions_after_overwrite_and_delete(source, tmp_path):
    client, reader = source
    first = client.put_object(Bucket=reader.bucket, Key="docs/a.txt", Body=b"alpha old")
    client.put_object(Bucket=reader.bucket, Key="docs/b.txt", Body=b"beta old")
    manifest = reader.capture_prefix("docs/")
    assert len(manifest["objects"]) == 2
    assert manifest["objects"][0]["version_id"] == first["VersionId"]
    client.put_object(Bucket=reader.bucket, Key="docs/a.txt", Body=b"alpha new")
    client.delete_object(Bucket=reader.bucket, Key="docs/b.txt")
    path = tmp_path / "archive.s3manifest"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    before = path.read_bytes()
    docs = reader.load_data(path)
    assert [doc.text for doc in docs] == ["alpha old", "beta old"]
    assert docs[0].metadata["s3_source"]["version_id"] == first["VersionId"]
    assert [doc.id for doc in reader.load_data(path)] == [doc.id for doc in docs]
    assert path.read_bytes() == before


def test_real_mutable_null_version_requires_opt_in_and_detects_overwrite(source, tmp_path):
    client, reader = source
    client.put_bucket_versioning(Bucket=reader.bucket, VersioningConfiguration={"Status": "Suspended"})
    client.put_object(Bucket=reader.bucket, Key="mutable.txt", Body=b"old")
    with pytest.raises(ValueError, match="immutable"):
        reader.capture_prefix("mutable")
    reader.allow_unversioned = True
    manifest = reader.capture_prefix("mutable")
    assert manifest["objects"][0]["version_id"] in (None, "null")
    docs, report = reader.read_manifest_with_report(manifest)
    assert report["complete"] and docs[0].text == "old"
    manifest["objects"][0]["version_id"] = "null"
    explicit, explicit_report = reader.read_manifest_with_report(manifest)
    assert explicit_report["complete"] and explicit[0].text == "old"
    client.put_object(Bucket=reader.bucket, Key="mutable.txt", Body=b"new")
    docs, report = reader.read_manifest_with_report(manifest)
    assert not docs and report["objects"][0]["service_code"] == "PreconditionFailed"
    path = tmp_path / "mutable.s3manifest"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(S3ImportError):
        reader.load_data(path)


def test_real_partial_missing_version_checksum_and_budget(source, tmp_path):
    client, reader = source
    for name in ("a", "b"):
        client.put_object(Bucket=reader.bucket, Key=name + ".txt", Body=name.encode())
    manifest = reader.capture_prefix("")
    missing = manifest["objects"][1]
    client.delete_object(Bucket=reader.bucket, Key=missing["key"], VersionId=missing["version_id"])
    docs, report = reader.read_manifest_with_report(manifest)
    assert [doc.text for doc in docs] == ["a"]
    assert [item["status"] for item in report["objects"]] == ["read", "failed"]
    manifest["objects"] = manifest["objects"][:1]
    manifest["objects"][0]["sha256"] = "0" * 64
    docs, report = reader.read_manifest_with_report(manifest)
    assert docs == [] and not report["complete"]
    reader.max_objects = 1
    client.put_object(Bucket=reader.bucket, Key="c.txt", Body=b"c")
    with pytest.raises(ValueError, match="max_objects"):
        reader.capture_prefix("")


def test_real_yaml_public_knowledge_sqlite_provenance(source, tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

    client, reader = source
    version = client.put_object(Bucket=reader.bucket, Key="nested/manual.txt", Body=b"alpha manual")["VersionId"]
    manifest = reader.capture_prefix("nested/")
    client.put_object(Bucket=reader.bucket, Key="nested/manual.txt", Body=b"new unrelated")
    managers = [ReaderManager(), StoreManager(), RagRouterManager(), DocProcessorManager()]
    pools = [dict(manager._instance_obj_map) for manager in managers]
    knowledge, store = None, None
    try:
        root = next(parent for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file())
        config_path = tmp_path / "reader.yaml"
        shutil.copyfile(
            root / "agentuniverse/agent/action/knowledge/reader/cloud/s3_version_reader.yaml.example", config_path
        )
        config = ComponentConfiger().load_by_configer(Configer(str(config_path)).load())
        config.bucket, config.source_name, config.client_args, config.readers = (
            reader.bucket,
            reader.source_name,
            reader.client_args,
            reader.readers,
        )
        configured = S3VersionReader().initialize_by_component_configer(config)
        store = SQLiteStore(name="s3_store", db_path=str(tmp_path / "knowledge.db"), keyword_extractor="s3_keywords")
        store._new_client()
        components = [
            configured,
            store,
            BaseRouter(name="base_router"),
            JiebaKeywordExtractor(name="s3_keywords", top_k=20),
        ]
        for manager, component in zip(managers, components):
            manager.register(component.get_instance_code(), component)
        path = tmp_path / "source.s3manifest"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        knowledge = Knowledge(stores=["s3_store"], readers={"s3manifest": "s3_version_reader"})
        knowledge.insert_knowledge(source_path=str(path))
        assert store.conn.execute("SELECT count(*) FROM documents").fetchone()[0] == 1
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="alpha")
        assert len(result) == 1 and result[0].text == "alpha manual"
        assert result[0].metadata["s3_source"]["version_id"] == version
        assert result[0].metadata["s3_source"]["key"] == "nested/manual.txt"
        assert configured._client is None
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if store is not None and store.conn is not None:
            store.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
