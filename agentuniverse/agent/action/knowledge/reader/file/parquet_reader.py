"""Opt-in projected Parquet ingestion with row-level source provenance."""
import base64
import hashlib
import io
import json
import math
from copy import deepcopy
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import List, Optional
from zoneinfo import ZoneInfoNotFoundError

from pydantic import Field, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


def _json_value(value):
    if value is None or type(value) in (bool, int, str):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite Parquet numbers are not silently converted")
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return {"days": value.days, "seconds": value.seconds, "microseconds": value.microseconds}
    if isinstance(value, bytes):
        return {"base64": base64.b64encode(value).decode("ascii")}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, dict) and all(isinstance(key, str) for key in value):
        return {key: _json_value(item) for key, item in value.items()}
    raise ValueError("unsupported Parquet value type: " + type(value).__name__)


def _json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def _arrow_value(scalar, pa):
    """Preserve nanoseconds that ordinary Python datetime/time cannot represent."""
    if not scalar.is_valid:
        return None
    dtype = scalar.type
    if pa.types.is_timestamp(dtype) and dtype.unit == "ns":
        return {"epoch_nanoseconds": scalar.cast(pa.int64()).as_py(), "timezone": dtype.tz}
    if pa.types.is_time64(dtype) and dtype.unit == "ns":
        return {"nanoseconds_since_midnight": scalar.cast(pa.int64()).as_py()}
    if pa.types.is_duration(dtype) and dtype.unit == "ns":
        return {"nanoseconds": scalar.cast(pa.int64()).as_py()}
    if pa.types.is_struct(dtype):
        names = [field.name for field in dtype]
        if len(names) != len(set(names)):
            raise ValueError("duplicate nested Parquet fields are ambiguous")
        return {name: _arrow_value(scalar[name], pa) for name in names}
    if pa.types.is_list(dtype) or pa.types.is_large_list(dtype) or pa.types.is_fixed_size_list(dtype):
        return [_arrow_value(item, pa) for item in scalar.values]
    if pa.types.is_map(dtype):
        return [[_arrow_value(item["key"], pa), _arrow_value(item["value"], pa)] for item in scalar.values]
    return _json_value(scalar.as_py())


class ParquetReader(Reader):
    """One Document per row, with optional top-level column projection.

    Reads one bounded immutable file snapshot, then decodes projected batches.
    Does not load pandas, execute SQL or traverse partitioned directory datasets.
    """
    text_columns: List[StrictStr] = Field(default_factory=list)
    metadata_columns: List[StrictStr] = Field(default_factory=list)
    id_column: Optional[StrictStr] = None
    batch_size: StrictInt = Field(default=256, ge=1)
    max_file_bytes: StrictInt = Field(default=32 * 1024 * 1024, ge=1)
    max_rows: StrictInt = Field(default=10_000, ge=1)
    max_row_chars: StrictInt = Field(default=100_000, ge=1)
    max_output_chars: StrictInt = Field(default=10_000_000, ge=1)

    def _validate_options(self):
        for name in ("batch_size", "max_file_bytes", "max_rows", "max_row_chars", "max_output_chars"):
            value = getattr(self, name)
            if type(value) is not int or value <= 0:
                raise ValueError(name + " must be a positive integer")
        for values in (self.text_columns, self.metadata_columns):
            if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values) or len(set(values)) != len(values):
                raise ValueError("column selections must be lists of distinct nonempty names")
        if self.id_column is not None and (not isinstance(self.id_column, str) or not self.id_column):
            raise ValueError("id_column must be a nonempty name or None")

    def _load_data(self, fpath, ext_info=None):
        self._validate_options()
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError as error:
            raise ImportError("ParquetReader requires pyarrow; install the project dependency") from error
        if not isinstance(fpath, (str, Path)):
            raise TypeError("ParquetReader requires a local file path")
        path = Path(fpath).resolve(strict=True)
        if ext_info is not None and not isinstance(ext_info, dict):
            raise ValueError("ext_info must be a mapping")
        extra = deepcopy(ext_info or {})
        reserved = {"source", "file_name", "file_sha256", "parquet_row", "parquet_row_group",
                    "parquet_column_types", "parquet_values", "parquet_original_id"}
        if reserved.intersection(extra):
            raise ValueError("ext_info cannot override Parquet provenance fields")
        _json(extra)  # Validate before expensive parsing.
        with path.open("rb") as stream:
            raw = stream.read(self.max_file_bytes + 1)
        if len(raw) > self.max_file_bytes:
            raise ValueError("Parquet file exceeds max_file_bytes")
        digest = hashlib.sha256(raw).hexdigest()
        result = []
        output_chars = 0
        seen = set()
        with io.BytesIO(raw) as stream:
            parquet = pq.ParquetFile(stream)
            try:
                names = parquet.schema_arrow.names
                if len(names) != len(set(names)):
                    raise ValueError("duplicate top-level Parquet columns are ambiguous")
                text_columns = self.text_columns or names
                selected = list(dict.fromkeys(text_columns + self.metadata_columns + ([self.id_column] if self.id_column else [])))
                if not selected or any(name not in names for name in selected):
                    raise ValueError("requested columns must be existing top-level fields")
                if parquet.metadata.num_rows > self.max_rows:
                    raise ValueError("Parquet file exceeds max_rows; no partial import")
                types = {name: str(parquet.schema_arrow.field(name).type) for name in selected}
                row_index = 0
                for group in range(parquet.num_row_groups):
                    for batch in parquet.iter_batches(batch_size=self.batch_size, row_groups=[group], columns=selected,
                                                      use_threads=False):
                        if set(batch.schema.names) != set(selected):
                            raise ValueError("Parquet projection is ambiguous")
                        for offset in range(batch.num_rows):
                            if row_index >= self.max_rows:
                                raise ValueError("decoded rows exceed max_rows")
                            converted = {name: _arrow_value(batch.column(name)[offset], pa) for name in selected}
                            content = _json({name: converted[name] for name in text_columns})
                            original_id = batch.column(self.id_column)[offset].as_py() if self.id_column else None
                            if self.id_column and (type(original_id) not in (str, int) or original_id == ""):
                                raise ValueError("id_column requires nonempty strings or integers, not null/bool")
                            identity = [path.as_uri(), "column", self.id_column, original_id] if self.id_column else [path.as_uri(), digest, row_index]
                            identity_key = _json(identity)
                            if identity_key in seen:
                                raise ValueError("duplicate values in id_column")
                            seen.add(identity_key)
                            metadata = deepcopy(extra)
                            metadata.update({"source": path.as_uri(), "file_name": path.name,
                                             "file_sha256": digest, "parquet_row": row_index,
                                             "parquet_row_group": group, "parquet_column_types": dict(types),
                                             "parquet_values": {name: converted[name] for name in self.metadata_columns}})
                            if self.id_column:
                                metadata["parquet_original_id"] = original_id
                            row_chars = len(content) + len(_json(metadata))
                            if row_chars > self.max_row_chars:
                                raise ValueError("row exceeds max_row_chars")
                            output_chars += row_chars
                            if output_chars > self.max_output_chars:
                                raise ValueError("decoded output exceeds max_output_chars")
                            result.append(Document(id=hashlib.sha256(identity_key.encode("utf-8")).hexdigest(),
                                                   text=content, metadata=metadata))
                            row_index += 1
                if row_index != parquet.metadata.num_rows:
                    raise ValueError("decoded row count differs from Parquet metadata")
            except ZoneInfoNotFoundError as error:
                raise ValueError("timezone database unavailable; install tzdata for timezone-aware Parquet values") from error
            finally:
                parquet.close()
        return result

    def _initialize_by_component_configer(self, config):
        names = ("text_columns", "metadata_columns", "id_column", "batch_size", "max_file_bytes",
                 "max_rows", "max_row_chars", "max_output_chars")
        validated = ParquetReader(**{name: getattr(config, name, getattr(self, name)) for name in names})
        validated._validate_options()
        super()._initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(validated, name))
        return self
