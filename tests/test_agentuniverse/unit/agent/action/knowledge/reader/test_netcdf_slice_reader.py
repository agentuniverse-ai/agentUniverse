"""Real NetCDF3/4 files, independent netCDF4 values and instrumented lazy reads."""

import hashlib
import json
import shutil
from pathlib import Path
from unittest.mock import patch

import netCDF4
import numpy as np
import pytest

from agentuniverse.agent.action.knowledge.reader.file.netcdf_slice_reader import NetcdfSliceReader


def fixture(tmp_path, format="NETCDF4"):
    path = tmp_path / "climate.nc"
    with netCDF4.Dataset(path, "w", format=format) as dataset:
        for name, size in [("time", 4), ("latitude", 4), ("longitude", 2), ("unused", 10000)]:
            dataset.createDimension(name, size)
        time = dataset.createVariable("time", "f8", ("time",))
        time[:] = [0, 30, 59, 60]
        time.units, time.calendar = "days since 2000-01-01", "360_day"
        latitude = dataset.createVariable("latitude", "f8", ("latitude",))
        latitude[:] = [30, 20, 10, 0]
        latitude.units = "degrees_north"
        longitude = dataset.createVariable("longitude", "f8", ("longitude",))
        longitude[:] = [100, 110]
        longitude.units = "degrees_east"
        data = dataset.createVariable("temperature", "i2", ("time", "latitude", "longitude"), fill_value=-9999)
        raw = np.arange(32).reshape(4, 4, 2)
        raw[1, 1, 0] = -9999
        data[:] = raw
        data.scale_factor, data.add_offset, data.units = 0.5, 273.15, "K"
        data.long_name = "temperature evidence"
        # An unselected dimension coordinate must not be indexed by xarray.
        dataset.createVariable("unused", "f8", ("unused",))[:] = np.arange(10000)
        dataset.createVariable("unselected", "f8", ("unused",))[:] = np.arange(10000)
    return path


def reader(**kwargs):
    settings = dict(
        variables=["temperature"], coordinate_ranges={"latitude": [10, 20], "time": [30, 59]}, max_chunk_values=4
    )
    settings.update(kwargs)
    return NetcdfSliceReader(**settings)


@pytest.mark.parametrize("format", ["NETCDF4", "NETCDF3_CLASSIC"])
def test_real_formats_selection_mask_scale_calendar_and_hash(tmp_path, format):
    path = fixture(tmp_path, format)
    before = path.read_bytes()
    docs, report = reader().load_slice(path)
    assert report["selected_values"] == 8 and len(docs) == 2
    assert report["excluded_variables"] == ["unused", "unselected"]
    first, second = [json.loads(d.text) for d in docs]
    assert first["coordinates"]["latitude"]["values"] == [20, 10]
    assert first["coordinates"]["time"]["values"] == ["2000-02-01T00:00:00"]
    assert second["coordinates"]["time"]["values"] == ["2000-02-30T00:00:00"]
    assert first["coordinates"]["time"]["attributes"]["calendar"] == "360_day"
    assert first["attributes"]["units"] == "K" and first["values"][0][0][0] is None
    with netCDF4.Dataset(path) as independent:
        expected = independent["temperature"][1:3, 1:3, :].filled(np.nan)
        actual = np.array([first["values"][0], second["values"][0]], dtype=float)
        np.testing.assert_allclose(actual, expected, equal_nan=True)
    assert docs[0].metadata["netcdf_evidence"]["source_index_slices"] == {
        "time": [1, 2, 1],
        "latitude": [1, 3, 1],
        "longitude": [0, 2, 1],
    }
    assert path.read_bytes() == before and report["file_sha256"] == hashlib.sha256(before).hexdigest()


def test_projection_and_bounded_real_backend_reads(tmp_path, monkeypatch):
    from xarray.backends.netCDF4_ import NetCDF4ArrayWrapper

    path = fixture(tmp_path)
    original = NetCDF4ArrayWrapper.__getitem__
    reads = []

    def observed(self, key):
        reads.append((self.variable_name, key.tuple, self.shape))
        return original(self, key)

    monkeypatch.setattr(NetCDF4ArrayWrapper, "__getitem__", observed)
    docs = reader(max_coordinate_values=10).load_data(path)
    assert len(docs) == 2
    assert not any(name in {"unused", "unselected"} for name, _, _ in reads)
    data_reads = [(key, shape) for name, key, shape in reads if name == "temperature"]
    assert len(data_reads) == 2
    for key, shape in data_reads:
        counts = [len(range(*part.indices(size))) if isinstance(part, slice) else 1 for part, size in zip(key, shape)]
        assert np.prod(counts) <= 4
        assert key[0].start >= 1 and key[1].start >= 1


def test_budget_rejected_before_data_reads(tmp_path, monkeypatch):
    from xarray.backends.netCDF4_ import NetCDF4ArrayWrapper

    original = NetCDF4ArrayWrapper.__getitem__
    reads = []

    def observed(self, key):
        reads.append(self.variable_name)
        return original(self, key)

    monkeypatch.setattr(NetCDF4ArrayWrapper, "__getitem__", observed)
    with pytest.raises(ValueError, match="max_values"):
        reader(max_values=7).load_data(fixture(tmp_path))
    assert reads == []


@pytest.mark.parametrize(
    "settings,match",
    [
        ({"variables": []}, "explicitly"),
        ({"variables": ["missing"]}, "missing"),
        ({"max_file_bytes": 1}, "max_file_bytes"),
        ({"max_coordinate_values": 9}, "max_coordinate"),
        ({"max_documents": 1}, "max_documents"),
        ({"max_document_chars": 10}, "text budget"),
        ({"max_total_chars": 10}, "text budget"),
        ({"max_values": True}, "integer"),
        ({"index_slices": {"latitude": [0, 1]}}, "both"),
        ({"coordinate_ranges": {"bad": [0, 1]}}, "dimensions"),
        ({"coordinate_ranges": {"latitude": [20, 10]}}, "inclusive"),
        ({"index_slices": {"longitude": [0, 9]}}, "exceeds"),
        ({"index_slices": {"longitude": [0, 2, 0]}}, "positive"),
    ],
)
def test_invalid_settings_and_limits(tmp_path, settings, match):
    with pytest.raises(ValueError, match=match):
        reader(**settings).load_data(fixture(tmp_path))


def test_nonmonotonic_auxiliary_missing_coordinates_and_groups(tmp_path):
    path = fixture(tmp_path)
    with netCDF4.Dataset(path, "a") as dataset:
        dataset["latitude"][:] = [30, 10, 20, 0]
    with pytest.raises(ValueError, match="monotonic"):
        reader().load_data(path)
    with netCDF4.Dataset(path, "a") as dataset:
        dataset["temperature"].coordinates = "curvilinear_lat"
    with pytest.raises(ValueError, match="Auxiliary"):
        reader().load_data(path)
    with netCDF4.Dataset(path, "a") as dataset:
        dataset.createGroup("nested")
    with pytest.raises(ValueError, match="Grouped"):
        reader().load_data(path)


def test_empty_selection_index_stride_and_isolation(tmp_path):
    path = fixture(tmp_path)
    docs, report = reader(coordinate_ranges={"latitude": [80, 90]}).load_slice(path)
    assert docs == [] and report["selected_values"] == 0
    selected = reader(coordinate_ranges={}, index_slices={"time": [0, 4, 2]}, max_chunk_values=4)
    docs = selected.load_data(path, {"team": ["science"]})
    assert sum(np.prod(d.metadata["netcdf_evidence"]["shape"]) for d in docs) == 16
    assert docs[0].metadata["netcdf_evidence"]["source_index_slices"]["time"] == [0, 2, 2]
    docs[0].metadata["team"].append("changed")
    assert docs[1].metadata["team"] == ["science"]
    copy = tmp_path / "copy.nc"
    copy.write_bytes(path.read_bytes())
    assert [d.id for d in docs] == [d.id for d in selected.load_data(copy)]
    with pytest.raises(ValueError, match="reserved"):
        selected.load_data(path, {"netcdf_evidence": {}})


def test_remote_urls_rejected():
    with pytest.raises(ValueError, match="local"):
        reader().load_data("https://example.invalid/data.nc")


def test_real_yaml_public_knowledge_sqlite_roundtrip(tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.configer import Configer

    path = fixture(tmp_path)
    managers = [ReaderManager(), StoreManager(), RagRouterManager(), DocProcessorManager()]
    pools = [dict(manager._instance_obj_map) for manager in managers]
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    knowledge, store = None, None
    try:
        app = Configer()
        app.value = {"BASE_INFO": {"appname": "netcdf-evidence-test"}}
        apps.app_configer = AppConfiger().load_by_configer(app)
        root = next(parent for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file())
        copied = tmp_path / "reader.yaml"
        shutil.copyfile(
            root / "agentuniverse/agent/action/knowledge/reader/file/netcdf_slice_reader.yaml.example", copied
        )
        config = ComponentConfiger().load_by_configer(Configer(str(copied)).load())
        reader = NetcdfSliceReader().initialize_by_component_configer(config)
        store = SQLiteStore(
            name="netcdf_store", db_path=str(tmp_path / "knowledge.db"), keyword_extractor="netcdf_keywords"
        )
        store._new_client()
        components = [
            reader,
            store,
            BaseRouter(name="base_router"),
            JiebaKeywordExtractor(name="netcdf_keywords", top_k=20),
        ]
        for manager, component in zip(managers, components):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["netcdf_store"], readers={"nc": "netcdf_slice_reader"})
        knowledge.insert_knowledge(source_path=str(path))
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="temperature")
        assert len(result) == 1
        assert result[0].metadata["netcdf_evidence"]["variable"] == "temperature"
        assert result[0].metadata["netcdf_evidence"]["file_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if store is not None and store.conn is not None:
            store.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = previous


def test_scalar_nonfinite_and_stride_end(tmp_path):
    path = tmp_path / "scalar.nc"
    with netCDF4.Dataset(path, "w") as dataset:
        dataset.createDimension("x", 5)
        dataset.createVariable("x", "i4", ("x",))[:] = np.arange(5)
        dataset.createVariable("data", "f8", ("x",))[:] = [1, 2, np.inf, 4, np.nan]
        dataset.createVariable("scalar", "f8")[:] = 7
    docs = NetcdfSliceReader(variables=["data", "scalar"], index_slices={"x": [0, 5, 2]}, max_chunk_values=2).load_data(
        path
    )
    assert [json.loads(d.text)["values"] for d in docs] == [[1, "Infinity"], [None], 7]
    assert docs[1].metadata["netcdf_evidence"]["source_index_slices"] == {"x": [4, 5, 2]}
    assert docs[2].metadata["netcdf_evidence"]["shape"] == []


def test_missing_dimension_coordinate_and_string_variable(tmp_path):
    path = tmp_path / "missing.nc"
    with netCDF4.Dataset(path, "w") as dataset:
        dataset.createDimension("x", 2)
        dataset.createVariable("data", "f8", ("x",))[:] = [1, 2]
    with pytest.raises(ValueError, match="explicit coordinate"):
        NetcdfSliceReader(variables=["data"]).load_data(path)
    with netCDF4.Dataset(path, "a") as dataset:
        dataset.createVariable("x", "i4", ("x",))[:] = [0, 1]
        dataset.createVariable("labels", str, ("x",))[:] = np.array(["a", "b"], dtype=object)
    with pytest.raises(ValueError, match="numeric"):
        NetcdfSliceReader(variables=["labels"]).load_data(path)


def test_enum_semantics_not_silently_discarded(tmp_path):
    path = tmp_path / "enum.nc"
    with netCDF4.Dataset(path, "w") as dataset:
        dataset.createDimension("x", 2)
        dataset.createVariable("x", "i4", ("x",))[:] = [0, 1]
        enumeration = dataset.createEnumType(np.uint8, "quality_type", {"good": 1, "bad": 2})
        dataset.createVariable("quality", enumeration, ("x",))[:] = [1, 2]
    with pytest.raises(ValueError, match="numeric"):
        NetcdfSliceReader(variables=["quality"]).load_data(path)
