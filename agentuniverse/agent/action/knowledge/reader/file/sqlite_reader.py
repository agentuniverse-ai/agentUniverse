"""Read a bounded, consistent SQLite table snapshot into row Documents."""
import base64
import hashlib
import json
import math
import sqlite3
import time
from contextlib import closing
from copy import deepcopy
from pathlib import Path
from typing import List

from pydantic import Field, StrictFloat, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


def _identifier(name):
    return '"' + name.replace('"', '""') + '"'


def _value(value):
    if value is None or type(value) in (str, int):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if isinstance(value, bytes):
        return {"base64": base64.b64encode(value).decode("ascii")}
    raise ValueError("unsupported or non-finite SQLite value")


def _json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


class SQLiteTableReader(Reader):
    """Opt-in row ingestion, not arbitrary SQL execution or schema inspection.

    Ordinary main-schema tables only. Use declared primary-key columns or explicit
    nonnull unique id_columns. A single read transaction spans schema and all rows.
    """
    table_name: StrictStr = ""
    text_columns: List[StrictStr] = Field(default_factory=list)
    metadata_columns: List[StrictStr] = Field(default_factory=list)
    id_columns: List[StrictStr] = Field(default_factory=list)
    batch_size: StrictInt = Field(default=256, ge=1)
    max_rows: StrictInt = Field(default=10_000, ge=1)
    max_file_bytes: StrictInt = Field(default=128 * 1024 * 1024, ge=1)
    max_row_chars: StrictInt = Field(default=100_000, ge=1)
    max_output_chars: StrictInt = Field(default=10_000_000, ge=1)
    max_vm_steps: StrictInt = Field(default=5_000_000, ge=1000)
    max_seconds: StrictFloat = Field(default=5.0, gt=0, le=300)

    def _validate_options(self):
        if not isinstance(self.table_name, str) or not self.table_name or "\x00" in self.table_name:
            raise ValueError("table_name must be an explicit nonempty identifier")
        for name in ("text_columns", "metadata_columns", "id_columns"):
            values = getattr(self, name)
            if not isinstance(values, list) or any(not isinstance(v, str) or not v or "\x00" in v for v in values) or len(set(values)) != len(values):
                raise ValueError(name + " requires distinct nonempty column names")
        for name in ("batch_size", "max_rows", "max_file_bytes", "max_row_chars", "max_output_chars", "max_vm_steps"):
            value = getattr(self, name)
            if type(value) is not int or value < (1000 if name == "max_vm_steps" else 1):
                raise ValueError("invalid limit: " + name)
        if isinstance(self.max_seconds, bool) or not isinstance(self.max_seconds, (int, float)) or not math.isfinite(self.max_seconds) or not 0 < self.max_seconds <= 300:
            raise ValueError("max_seconds must be finite and between 0 and 300")

    def _load_data(self, fpath, ext_info=None):
        self._validate_options()
        if sqlite3.sqlite_version_info < (3, 37, 0):
            raise RuntimeError("SQLiteTableReader requires SQLite 3.37+ for ordinary-table classification")
        if not isinstance(fpath, (str, Path)):
            raise TypeError("SQLiteTableReader requires a local database path")
        path = Path(fpath).resolve(strict=True)
        if path.stat().st_size > self.max_file_bytes:
            raise ValueError("SQLite main file exceeds max_file_bytes")
        if ext_info is not None and not isinstance(ext_info, dict):
            raise ValueError("ext_info must be a mapping")
        extra = deepcopy(ext_info or {})
        reserved = {"source", "file_name", "sqlite_table", "sqlite_key", "sqlite_row",
                    "sqlite_values", "sqlite_declared_types", "sqlite_projection_sha256"}
        if reserved.intersection(extra):
            raise ValueError("ext_info cannot override SQLite provenance")
        _json(extra)
        started = time.monotonic()
        steps = 0
        interrupted = False
        def progress():
            nonlocal steps, interrupted
            steps += 1000
            interrupted = steps >= self.max_vm_steps or time.monotonic() - started >= self.max_seconds
            return int(interrupted)

        result = []
        total_chars = 0
        seen = set()
        with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True,
                                     timeout=min(5.0, self.max_seconds))) as connection:
            connection.execute("PRAGMA query_only=ON")
            connection.set_progress_handler(progress, 1000)
            connection.execute("BEGIN")
            try:
                tables = connection.execute("PRAGMA table_list").fetchall()
                if not any(row[0] == "main" and row[1] == self.table_name and row[2] == "table" for row in tables) or self.table_name.startswith("sqlite_"):
                    raise ValueError("table_name must select an ordinary main-schema user table")
                columns = connection.execute("PRAGMA table_info(" + _identifier(self.table_name) + ")").fetchall()
                names = [row[1] for row in columns]
                text_columns = self.text_columns or names
                keys = self.id_columns or [row[1] for row in sorted(columns, key=lambda row: row[5]) if row[5]]
                if not keys:
                    raise ValueError("table requires a primary key or explicit unique id_columns")
                selected = list(dict.fromkeys(text_columns + self.metadata_columns + keys))
                if not selected or any(name not in names for name in selected):
                    raise ValueError("column selections must name existing stored columns")
                declared = {row[1]: row[2] for row in columns if row[1] in selected}
                digest = hashlib.sha256(_json([self.table_name, selected, keys, declared]).encode("utf-8"))
                # Encoded identities distinguish text case and integer/real keys.
                # Resolve SQLite collation/numeric ties explicitly rather than
                # letting insertion order change row positions and fingerprints.
                ordering = [(_identifier(name) + " COLLATE BINARY") for name in keys]
                ordering += ["typeof(" + _identifier(name) + ")" for name in keys]
                sql = ("SELECT " + ",".join(_identifier(name) for name in selected)
                       + " FROM " + _identifier(self.table_name) + " ORDER BY "
                       + ",".join(ordering) + " LIMIT ?")
                cursor = connection.execute(sql, (self.max_rows + 1,))
                while True:
                    batch = cursor.fetchmany(self.batch_size)
                    if not batch:
                        break
                    for values in batch:
                        if len(result) >= self.max_rows:
                            raise ValueError("table exceeds max_rows; no partial import")
                        if time.monotonic() - started >= self.max_seconds:
                            raise ValueError("SQLite read exceeds max_seconds")
                        row = dict(zip(selected, (_value(v) for v in values)))
                        if any(row[key] is None for key in keys):
                            raise ValueError("identity columns must not contain null")
                        key = {name: row[name] for name in keys}
                        encoded_key = _json(key)
                        if encoded_key in seen:
                            raise ValueError("identity columns are not unique")
                        seen.add(encoded_key)
                        content = _json({name: row[name] for name in text_columns})
                        metadata = deepcopy(extra)
                        metadata.update({"source": path.as_uri(), "file_name": path.name,
                                         "sqlite_table": self.table_name, "sqlite_key": key,
                                         "sqlite_row": len(result), "sqlite_declared_types": dict(declared),
                                         "sqlite_values": {name: row[name] for name in self.metadata_columns}})
                        # Reserve the exact fingerprint field footprint before attaching it.
                        metadata["sqlite_projection_sha256"] = "0" * 64
                        row_chars = len(content) + len(_json(metadata))
                        if row_chars > self.max_row_chars:
                            raise ValueError("row exceeds max_row_chars")
                        total_chars += row_chars
                        if total_chars > self.max_output_chars:
                            raise ValueError("output exceeds max_output_chars")
                        encoded = _json(row).encode("utf-8")
                        digest.update(len(encoded).to_bytes(8, "big") + encoded)
                        identity = _json([path.as_uri(), self.table_name, key]).encode("utf-8")
                        result.append(Document(id=hashlib.sha256(identity).hexdigest(), text=content, metadata=metadata))
                for document in result:
                    document.metadata["sqlite_projection_sha256"] = digest.hexdigest()
            except sqlite3.OperationalError as error:
                if interrupted:
                    raise ValueError("SQLite query exceeded VM/time budget") from error
                raise
            finally:
                connection.set_progress_handler(None, 0)
                connection.rollback()
        return result

    def _initialize_by_component_configer(self, config):
        names = ("table_name", "text_columns", "metadata_columns", "id_columns", "batch_size",
                 "max_rows", "max_file_bytes", "max_row_chars", "max_output_chars", "max_vm_steps", "max_seconds")
        validated = SQLiteTableReader(**{name: getattr(config, name, getattr(self, name)) for name in names})
        validated._validate_options()
        super()._initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(validated, name))
        return self
