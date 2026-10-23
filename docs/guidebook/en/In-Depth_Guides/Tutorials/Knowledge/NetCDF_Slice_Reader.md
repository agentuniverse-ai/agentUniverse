# NetCDF coordinate slice reader

`NetcdfSliceReader` reads explicitly selected local numeric variables as labelled array tiles. Each tile retains dimension order, coordinates, units, fill/scale metadata and time calendar. Install `pip install "agentUniverse[netcdf_ext]"`.

```python
from agentuniverse.agent.action.knowledge.reader.file.netcdf_slice_reader import NetcdfSliceReader
reader = NetcdfSliceReader(
    variables=["temperature"],
    coordinate_ranges={"latitude": [10, 30]},
    index_slices={"time": [0, 2]},
    max_chunk_values=1000,
)
documents, report = reader.load_slice("climate.nc")
```

Variable names are mandatory and distinct. Coordinate ranges are inclusive numeric decoded source-coordinate units, supporting strictly monotonic ascending/descending coordinates. Time bounds `[30, 59]` mean those numbers in the file's units/calendar, not date strings. Index slices use nonnegative `[start, stop, optional_step]` with exclusive stop and positive step. A dimension cannot use both forms. Unspecified dimensions retain their extent, subject to budgets; empty selections yield no tiles.

Copy `netcdf_slice_reader.yaml.example` into your Reader package as `.yaml`, adjust its variables/selections, and configure Knowledge `readers: {nc: netcdf_slice_reader}` (optionally nc4/cdf). Normal insert/query is tested with real SQLite. No global routing changes. `load_data` returns Documents; `load_slice` also reports counts and excluded variables.

## Evidence

Text is deterministic JSON with variable, ordered dimensions, coordinates/selected attributes, variable attributes and nested decoded values. Reserved metadata `netcdf_evidence` also contains shape, original-file index slices, source path/hash and decoding markers. Missing/NaN values become null, never zero; infinities become signed strings. CF mask/scale applies through xarray, retaining original fill/scale attributes. Source NaN and decoded missing values are not distinguished.

Time uses cftime ISO-like strings with original units/calendar. February 30 is valid in a 360_day calendar and must not be treated as Gregorian. Missing calendar follows xarray/CF defaults. No unit conversion, interpolation, aggregation or scientific validation. Only selected descriptive/decoding attributes are copied; arbitrary global metadata, cell bounds, grid mappings and ancillary variables are not interpreted.

IDs use file hash, variable and original tile indices. Same bytes and tiles retain IDs after relocation; repacking or different tiles change identity. No Store cleanup. Metadata is deep-copied and its reserved key cannot be replaced. Hashing is repeated before return to detect changed source bytes; this is not a filesystem lock.

## Read behavior and limits

netCDF4 preflight checks metadata and coordinate/value budgets before xarray creates indexes. xarray opens only selected variables and dimension coordinates. Coordinates can be loaded into indexes after the coordinate budget check; data variables are sliced/tiled before values are requested. No Dask service. Logical tiles obey max_chunk_values, but storage libraries can decompress larger on-disk chunks. Hashing reads the entire file in blocks without loading its arrays.

Scope: local nc/nc4/cdf, root-only NetCDF3/4 real numeric variables, numeric 1-D dimension coordinates and scalar variables. Remote URLs, groups, string/compound data, missing dimension coordinates and auxiliary/curvilinear coordinates fail explicitly. No nearest-neighbour fallback.

| Setting | Default | Maximum configuration |
| --- | ---: | ---: |
| max_file_bytes | 512,000,000 | 2,000,000,000 |
| max_coordinate_values | 100,000 | 1,000,000 |
| max_values | 100,000 | 1,000,000 |
| max_chunk_values | 1,000 | 10,000 |
| max_documents | 1,000 | 10,000 |
| max_document_chars | 200,000 | 2,000,000 |
| max_total_chars | 10,000,000 | 40,000,000 |

Settings are positive integers, not booleans. Budget/format/decoding failures return no partial Documents. Limits are not a native NetCDF/HDF5 parser sandbox or fixed-memory guarantee.

## Verification

Real NetCDF3 classic and NetCDF4 fixtures are independently compared through netCDF4 masked/scaled reads. Tests cover descending coordinates, 360_day February 30, fill values, stride endpoints, scalars/infinities, projection and budgets. A transparent wrapper records actual xarray backend reads while calling the real backend: no excluded-variable reads, bounded selected tiles, and over-budget rejection before data reads. YAML to Knowledge to SQLite and source hashes are tested.

```sh
pip install xarray==2024.11.0 netCDF4==1.7.2 cftime==1.6.4.post1 pandas==2.2.3
python -m pytest -q --import-mode=importlib tests/test_agentuniverse/unit/agent/action/knowledge/reader/test_netcdf_slice_reader.py
```

References: [xarray I/O](https://docs.xarray.dev/en/stable/user-guide/io.html), [open_dataset](https://docs.xarray.dev/en/stable/generated/xarray.open_dataset.html).
