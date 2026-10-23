"""Explicit local NetCDF variable projection and coordinate-preserving tiles."""

import hashlib
import itertools
import json
import math
from copy import deepcopy
from pathlib import Path
from typing import ClassVar

from pydantic import Field, StrictInt

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


def _json_value(value):
    if hasattr(value, "tolist"):
        return _json_value(value.tolist())
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None if math.isnan(value) else ("Infinity" if value > 0 else "-Infinity")
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise ValueError(f"Unsupported NetCDF value type: {type(value).__name__}")


def _digest(path, limit):
    digest, count = hashlib.sha256(), 0
    with path.open("rb") as stream:
        while block := stream.read(1048576):
            count += len(block)
            if count > limit:
                raise ValueError("max_file_bytes exceeded")
            digest.update(block)
    return digest.hexdigest()


class NetcdfSliceReader(Reader):
    """Read selected numeric root variables as bounded, labelled array tiles.

    Coordinate ranges are inclusive, expressed in decoded numeric source units;
    time bounds are numbers in the file's time units/calendar, not date strings.
    Index slices use nonnegative Python start/stop/step with exclusive stop.
    """

    variables: list[str] = Field(default_factory=list)
    coordinate_ranges: dict = Field(default_factory=dict)
    index_slices: dict = Field(default_factory=dict)
    max_file_bytes: StrictInt = 512000000
    max_coordinate_values: StrictInt = 100000
    max_values: StrictInt = 100000
    max_chunk_values: StrictInt = 1000
    max_documents: StrictInt = 1000
    max_document_chars: StrictInt = 200000
    max_total_chars: StrictInt = 10000000
    _LIMITS: ClassVar[dict] = {
        "max_file_bytes": 2000000000,
        "max_coordinate_values": 1000000,
        "max_values": 1000000,
        "max_chunk_values": 10000,
        "max_documents": 10000,
        "max_document_chars": 2000000,
        "max_total_chars": 40000000,
    }
    _ATTRS: ClassVar[tuple] = (
        "units",
        "calendar",
        "long_name",
        "standard_name",
        "_FillValue",
        "missing_value",
        "scale_factor",
        "add_offset",
        "_Unsigned",
    )

    def _settings(self):
        for key, maximum in self._LIMITS.items():
            value = getattr(self, key)
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError(f"Invalid {key}; expected integer in 1..{maximum}")
        if (
            not self.variables
            or any(not isinstance(v, str) or not v or "/" in v for v in self.variables)
            or len(set(self.variables)) != len(self.variables)
        ):
            raise ValueError("Select distinct root variable names explicitly")
        if set(self.coordinate_ranges) & set(self.index_slices):
            raise ValueError("A dimension cannot have both coordinate range and index slice")
        for value in self.coordinate_ranges.values():
            if (
                not isinstance(value, (list, tuple))
                or len(value) != 2
                or any(type(v) not in (int, float) or not math.isfinite(v) for v in value)
                or value[0] > value[1]
            ):
                raise ValueError("coordinate_ranges require finite inclusive [lower, upper]")
        for value in self.index_slices.values():
            if (
                not isinstance(value, (list, tuple))
                or len(value) not in (2, 3)
                or any(type(v) is not int or v < 0 for v in value)
                or (len(value) == 3 and value[2] == 0)
                or value[0] > value[1]
            ):
                raise ValueError("index_slices require nonnegative [start, stop, optional positive step]")

    def _initialize_by_component_configer(self, config):
        candidate = self.model_copy(deep=True)
        for key in (*self._LIMITS, "variables", "coordinate_ranges", "index_slices"):
            if key in config.configer.value:
                setattr(candidate, key, deepcopy(config.configer.value[key]))
        candidate._settings()
        super()._initialize_by_component_configer(config)
        for key in (*self._LIMITS, "variables", "coordinate_ranges", "index_slices"):
            setattr(self, key, deepcopy(getattr(candidate, key)))
        return self

    def load_slice(self, file, ext_info=None):
        """Return Documents and projection report; reject over-budget reads upfront.

        Numeric one-dimensional dimension coordinates are required. Auxiliary /
        curvilinear coordinates, groups and string/compound variables are outside
        this reader's scope. Data variables load only after selection and tiling.
        """
        self._settings()
        if ext_info is not None and (not isinstance(ext_info, dict) or "netcdf_evidence" in ext_info):
            raise ValueError("ext_info must be a dictionary without reserved netcdf_evidence")
        if "://" in str(file):
            raise ValueError("Only local NetCDF paths are supported")
        path = Path(file).resolve()
        if path.suffix.lower() not in {".nc", ".nc4", ".cdf"} or not path.is_file():
            raise ValueError("Expected local .nc, .nc4 or .cdf file")
        if path.stat().st_size > self.max_file_bytes:
            raise ValueError("max_file_bytes exceeded")
        digest = _digest(path, self.max_file_bytes)
        try:
            import netCDF4
            import numpy as np
            import xarray as xr
        except ImportError as error:
            raise ImportError("NetcdfSliceReader requires agentUniverse[netcdf_ext]") from error
        # Preflight dimensions/coordinate budgets before xarray creates indexes.
        with netCDF4.Dataset(str(path), "r") as source:
            if source.groups:
                raise ValueError("Grouped NetCDF is unsupported; supply a root-only file")
            if any(name not in source.variables for name in self.variables):
                raise ValueError("Selected variable is missing")
            dims = set()
            for name in self.variables:
                variable = source.variables[name]
                if (
                    isinstance(variable.datatype, (netCDF4.EnumType, netCDF4.CompoundType, netCDF4.VLType))
                    or np.dtype(variable.dtype).kind not in "iuf"
                ):
                    raise ValueError("Only real numeric variables are supported")
                dims.update(variable.dimensions)
                auxiliary = getattr(variable, "coordinates", "").split()
                if any(coord not in variable.dimensions for coord in auxiliary):
                    raise ValueError("Auxiliary/curvilinear coordinates are unsupported")
            if not (set(self.coordinate_ranges) | set(self.index_slices)) <= dims:
                raise ValueError("Selection names must be dimensions of selected variables")
            if sum(len(source.dimensions[dim]) for dim in dims) > self.max_coordinate_values:
                raise ValueError("max_coordinate_values exceeded before loading indexes")
            selectors, attrs, dimensions = {}, {}, {}
            keep = set(self.variables) | dims
            for name in keep:
                if name not in source.variables:
                    raise ValueError("Every dimension must have an explicit coordinate variable")
                variable = source.variables[name]
                attrs[name] = {
                    key: _json_value(variable.getncattr(key)) for key in self._ATTRS if key in variable.ncattrs()
                }
                dimensions[name] = list(variable.dimensions)
            for dim in sorted(dims):
                coordinate = source.variables[dim]
                if (
                    coordinate.dimensions != (dim,)
                    or isinstance(coordinate.datatype, (netCDF4.EnumType, netCDF4.CompoundType, netCDF4.VLType))
                    or np.dtype(coordinate.dtype).kind not in "iuf"
                ):
                    raise ValueError("Expected numeric one-dimensional dimension coordinate")
                size = len(source.dimensions[dim])
                selector = slice(0, size, 1)
                if dim in self.index_slices:
                    spec = self.index_slices[dim]
                    if spec[1] > size:
                        raise ValueError("Index slice exceeds dimension")
                    selector = slice(spec[0], spec[1], spec[2] if len(spec) == 3 else 1)
                elif dim in self.coordinate_ranges:
                    values = coordinate[:]
                    if np.ma.is_masked(values) or not np.all(np.isfinite(values)):
                        raise ValueError("Coordinate range requires finite nonmissing coordinates")
                    delta = np.diff(values.astype(float))
                    if not (np.all(delta > 0) or np.all(delta < 0)):
                        raise ValueError("Coordinate ranges require strictly monotonic coordinates")
                    low, high = self.coordinate_ranges[dim]
                    hits = np.flatnonzero((values >= low) & (values <= high))
                    selector = slice(int(hits[0]), int(hits[-1]) + 1, 1) if len(hits) else slice(0, 0, 1)
                selectors[dim] = selector
            sizes = {dim: len(range(s.start, s.stop, s.step)) for dim, s in selectors.items()}
            count = sum(math.prod(sizes[dim] for dim in dimensions[name]) for name in self.variables)
            if count > self.max_values:
                raise ValueError("max_values exceeded before data-variable reads")
            drop = [name for name in source.variables if name not in keep]
        documents, total = [], 0
        with xr.open_dataset(
            path,
            engine="netcdf4",
            chunks=None,
            cache=False,
            drop_variables=drop,
            decode_cf=True,
            decode_coords=False,
            use_cftime=True,
        ) as dataset:
            for name in self.variables:
                selected = dataset[name].isel({dim: selectors[dim] for dim in dimensions[name]})
                shape, dims_order = selected.shape, list(selected.dims)
                if selected.size == 0:
                    continue
                remaining, block_sizes = self.max_chunk_values, []
                for size in reversed(shape):
                    width = min(size, remaining)
                    block_sizes.insert(0, width)
                    remaining = max(1, remaining // width)
                starts = itertools.product(*(range(0, size, width) for size, width in zip(shape, block_sizes)))
                for start in starts:
                    if len(documents) >= self.max_documents:
                        raise ValueError("max_documents exceeded; no partial result returned")
                    tile_slices = {
                        dim: slice(offset, min(offset + width, size))
                        for dim, offset, width, size in zip(dims_order, start, block_sizes, shape)
                    }
                    tile = selected.isel(tile_slices)
                    values = _json_value(tile.values)
                    coordinates = {
                        dim: {"values": _json_value(tile.coords[dim].values), "attributes": attrs[dim]}
                        for dim in dims_order
                    }
                    indices = {
                        dim: [
                            selectors[dim].start + tile_slices[dim].start * selectors[dim].step,
                            min(
                                selectors[dim].stop, selectors[dim].start + tile_slices[dim].stop * selectors[dim].step
                            ),
                            selectors[dim].step,
                        ]
                        for dim in dims_order
                    }
                    evidence = {
                        "variable": name,
                        "dimensions": dims_order,
                        "shape": list(tile.shape),
                        "coordinates": coordinates,
                        "attributes": attrs[name],
                        "source_index_slices": indices,
                        "mask_and_scale": True,
                        "time_decoding": "cftime",
                        "missing_values": "null",
                        "nonfinite_infinity": "signed_string",
                        "file_sha256": digest,
                        "file_path": str(path),
                    }
                    text = json.dumps(
                        {
                            "variable": name,
                            "dimensions": dims_order,
                            "coordinates": coordinates,
                            "attributes": attrs[name],
                            "values": values,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                        allow_nan=False,
                    )
                    total += len(text)
                    if len(text) > self.max_document_chars or total > self.max_total_chars:
                        raise ValueError("NetCDF text budget exceeded; no partial result returned")
                    identity = json.dumps([digest, name, indices], sort_keys=True)
                    metadata = deepcopy(ext_info) if ext_info else {}
                    metadata["netcdf_evidence"] = deepcopy(evidence)
                    documents.append(
                        Document(id=hashlib.sha256(identity.encode()).hexdigest(), text=text, metadata=metadata)
                    )
        if _digest(path, self.max_file_bytes) != digest:
            raise ValueError("NetCDF changed during extraction")
        return documents, {
            "file_sha256": digest,
            "selected_variables": list(self.variables),
            "selected_values": count,
            "document_count": len(documents),
            "coordinate_ranges": deepcopy(self.coordinate_ranges),
            "index_slices": deepcopy(self.index_slices),
            "excluded_variables": drop,
        }

    def _load_data(self, file, ext_info=None):
        return self.load_slice(file, ext_info)[0]
