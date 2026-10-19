#!/usr/bin/env python3
"""Bounded concurrent batch reader orchestration."""

# Public load_data validates user-controlled batch specifications.
# ruff: noqa: C901, TRY003, TRY301

import os
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any, ClassVar, cast
from urllib.parse import urlparse

from pydantic import Field, PrivateAttr

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.utils.url_safety import validate_public_http_url
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class BatchKnowledgeReader(Reader):
    """Load many heterogeneous sources with bounded concurrency and isolation."""

    base_dir: str = "."
    max_inputs: int = 100
    max_workers: int = 4
    max_documents: int = 10_000
    max_total_chars: int = 10_000_000
    max_documents_per_source: int = 1_000
    max_chars_per_source: int = 1_000_000
    max_source_bytes: int = 100 * 1024 * 1024
    allow_urls: bool = False
    default_continue_on_error: bool = True
    default_deduplicate: bool = True
    allowed_reader_names: list[str] = Field(default_factory=list)

    _last_report: dict[str, Any] = PrivateAttr(default_factory=dict)
    _INPUT_FIELDS: ClassVar[set[str]] = {"source", "reader", "ext_info", "reader_kwargs"}

    @property
    def last_report(self) -> dict[str, Any]:
        """Return a copy of the most recent batch execution report."""
        return {
            **self._last_report,
            "errors": list(self._last_report.get("errors", [])),
            "sources": list(self._last_report.get("sources", [])),
        }

    def _initialize_by_component_configer(self, configer: ComponentConfiger) -> "BatchKnowledgeReader":
        super()._initialize_by_component_configer(configer)
        for field in (
            "base_dir",
            "max_inputs",
            "max_workers",
            "max_documents",
            "max_total_chars",
            "max_documents_per_source",
            "max_chars_per_source",
            "max_source_bytes",
            "allow_urls",
            "default_continue_on_error",
            "default_deduplicate",
            "allowed_reader_names",
        ):
            if hasattr(configer, field):
                setattr(self, field, getattr(configer, field))
        self._validate_config()
        return self

    def _validate_config(self) -> None:
        for name in (
            "max_inputs",
            "max_workers",
            "max_documents",
            "max_total_chars",
            "max_documents_per_source",
            "max_chars_per_source",
            "max_source_bytes",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")
        for name in ("allow_urls", "default_continue_on_error", "default_deduplicate"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a boolean")
        if not isinstance(self.allowed_reader_names, list) or any(
            not isinstance(item, str) or not item for item in self.allowed_reader_names
        ):
            raise ValueError("allowed_reader_names must be a list of non-empty strings")

    def _load_data(
        self,
        inputs: list[str | dict[str, Any]],
        continue_on_error: bool | None = None,
        deduplicate: bool | None = None,
        deduplicate_by: str = "id",
        max_workers: int | None = None,
        ext_info: dict[str, Any] | None = None,
    ) -> list[Document]:
        """Load all sources and return documents in input order."""
        self._validate_config()
        specs = self._inputs(inputs, ext_info)
        continue_on_error = self._boolean_default(
            continue_on_error, self.default_continue_on_error, "continue_on_error"
        )
        deduplicate = self._boolean_default(deduplicate, self.default_deduplicate, "deduplicate")
        if deduplicate_by not in {"id", "text"}:
            raise ValueError("deduplicate_by must be id or text")
        workers = self.max_workers if max_workers is None else max_workers
        if isinstance(workers, bool) or not isinstance(workers, int) or not 1 <= workers <= self.max_workers:
            raise ValueError(f"max_workers must be an integer from 1 to {self.max_workers}")

        results = self._collect_sources(specs, min(workers, len(specs)), continue_on_error)

        documents = []
        errors = []
        seen = set()
        total_chars = 0
        source_reports = []
        for index, (spec, result) in enumerate(zip(specs, results, strict=True)):
            if isinstance(result, Exception):
                error = {
                    "input_index": index,
                    "source": spec["source_display"],
                    "reader": spec["reader_name"],
                    "error_type": type(result).__name__,
                    "error": str(result),
                }
                errors.append(error)
                source_reports.append({**error, "status": "error", "document_count": 0})
                if not continue_on_error:
                    self._set_report(specs, documents, errors, source_reports, deduplicate_by)
                    raise RuntimeError(f"batch input {index} failed with {type(result).__name__}: {result}") from result
                continue
            source_count = 0
            for document in result:
                if not isinstance(document, Document):
                    raise TypeError(f"reader {spec['reader_name']} returned a non-Document value")
                copy = document.model_copy(deep=True)
                copy.metadata = dict(copy.metadata or {})
                copy.metadata.update(
                    {
                        "batch_source": spec["source_display"],
                        "batch_input_index": index,
                        "batch_reader": spec["reader_name"],
                    }
                )
                marker = copy.id if deduplicate_by == "id" else copy.text
                if deduplicate and marker in seen:
                    continue
                if deduplicate:
                    seen.add(marker)
                text_length = len(copy.text or "")
                if len(documents) + 1 > self.max_documents:
                    raise ValueError(f"batch exceeds max_documents ({self.max_documents})")
                if total_chars + text_length > self.max_total_chars:
                    raise ValueError(f"batch exceeds max_total_chars ({self.max_total_chars})")
                documents.append(copy)
                source_count += 1
                total_chars += text_length
            source_reports.append(
                {
                    "input_index": index,
                    "source": spec["source_display"],
                    "reader": spec["reader_name"],
                    "status": "success",
                    "document_count": source_count,
                }
            )
        self._set_report(specs, documents, errors, source_reports, deduplicate_by)
        return documents

    def _collect_sources(
        self,
        specs: list[dict[str, Any]],
        workers: int,
        continue_on_error: bool,
    ) -> list[list[Document] | Exception]:
        """Admit bounded work and validate each result as soon as it completes."""
        pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="au-batch-reader")
        results: list[list[Document] | Exception | None] = [None] * len(specs)
        pending: dict[Future[list[Document]], int] = {}
        next_index = 0
        raw_documents = 0
        raw_chars = 0
        nonblocking_shutdown = False

        def submit_available() -> None:
            nonlocal next_index
            while next_index < len(specs) and len(pending) < workers:
                pending[pool.submit(self._load_one, specs[next_index])] = next_index
                next_index += 1

        submit_available()
        try:
            while pending:
                completed, _ = wait(pending, return_when=FIRST_COMPLETED)
                for future in completed:
                    index = pending.pop(future)
                    try:
                        raw_result = future.result()
                    except Exception as exc:
                        results[index] = exc
                        if not continue_on_error:
                            nonblocking_shutdown = True
                            for queued in pending:
                                queued.cancel()
                            pool.shutdown(wait=False, cancel_futures=True)
                            self._last_report = {
                                "input_count": len(specs),
                                "successful_input_count": sum(isinstance(item, list) for item in results),
                                "failed_input_count": 1,
                                "document_count": 0,
                                "total_chars": 0,
                                "errors": [
                                    {
                                        "input_index": index,
                                        "source": specs[index]["source_display"],
                                        "reader": specs[index]["reader_name"],
                                        "error_type": type(exc).__name__,
                                        "error": str(exc),
                                    }
                                ],
                                "sources": [],
                            }
                            raise RuntimeError(
                                f"batch input {index} failed with {type(exc).__name__}: {exc}"
                            ) from exc
                        continue
                    try:
                        source_documents = self._validate_source_result(specs[index], raw_result)
                        raw_documents += len(source_documents)
                        raw_chars += sum(len(document.text or "") for document in source_documents)
                        if raw_documents > self.max_documents:
                            raise ValueError(f"batch exceeds max_documents ({self.max_documents})")
                        if raw_chars > self.max_total_chars:
                            raise ValueError(f"batch exceeds max_total_chars ({self.max_total_chars})")
                        results[index] = source_documents
                    except (TypeError, ValueError):
                        nonblocking_shutdown = True
                        for queued in pending:
                            queued.cancel()
                        pool.shutdown(wait=False, cancel_futures=True)
                        raise
                submit_available()
        finally:
            # The fail-fast branch already requested non-blocking shutdown.
            if nonblocking_shutdown:
                pass
            elif pending or next_index < len(specs):
                for queued in pending:
                    queued.cancel()
                pool.shutdown(wait=False, cancel_futures=True)
            else:
                pool.shutdown(wait=True)
        return cast(list[list[Document] | Exception], results)

    def _validate_source_result(self, spec: dict[str, Any], documents: Any) -> list[Document]:
        if not isinstance(documents, list):
            raise TypeError(f"reader {spec['reader_name']} must return a list")
        if len(documents) > self.max_documents_per_source:
            raise ValueError(
                f"reader {spec['reader_name']} exceeds max_documents_per_source "
                f"({self.max_documents_per_source})"
            )
        total_chars = 0
        for document in documents:
            if not isinstance(document, Document):
                raise TypeError(f"reader {spec['reader_name']} returned a non-Document value")
            total_chars += len(document.text or "")
            if total_chars > self.max_chars_per_source:
                raise ValueError(
                    f"reader {spec['reader_name']} exceeds max_chars_per_source ({self.max_chars_per_source})"
                )
        return documents

    def _set_report(
        self,
        specs: list[dict[str, Any]],
        documents: list[Document],
        errors: list[dict[str, Any]],
        source_reports: list[dict[str, Any]],
        deduplicate_by: str,
    ) -> None:
        self._last_report = {
            "input_count": len(specs),
            "successful_input_count": len(specs) - len(errors),
            "failed_input_count": len(errors),
            "document_count": len(documents),
            "total_chars": sum(len(document.text or "") for document in documents),
            "deduplicate_by": deduplicate_by,
            "errors": errors,
            "sources": source_reports,
        }

    @staticmethod
    def _boolean_default(value: Any, default: bool, field: str) -> bool:
        if value is None:
            return default
        if not isinstance(value, bool):
            raise TypeError(f"{field} must be a boolean")
        return value

    def _inputs(self, value: Any, shared_ext_info: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list) or not value:
            raise ValueError("inputs must be a non-empty list")
        if len(value) > self.max_inputs:
            raise ValueError(f"inputs exceeds max_inputs ({self.max_inputs})")
        if shared_ext_info is not None and not isinstance(shared_ext_info, dict):
            raise TypeError("ext_info must be an object")
        output = []
        for index, raw in enumerate(value):
            if isinstance(raw, str):
                raw = {"source": raw}
            if not isinstance(raw, dict):
                raise TypeError(f"inputs[{index}] must be a string or object")
            unknown = set(raw) - self._INPUT_FIELDS
            if unknown:
                raise ValueError(f"inputs[{index}] has unknown fields: {', '.join(sorted(unknown))}")
            source = raw.get("source")
            if not isinstance(source, str) or not source.strip():
                raise ValueError(f"inputs[{index}].source must be a non-empty string")
            source = source.strip()
            is_url = self._is_url(source)
            if is_url:
                if not self.allow_urls:
                    raise ValueError("URL inputs are disabled; set allow_urls=true to enable them")
                resolved: str | Path = validate_public_http_url(source)
                default_reader = "default_web_page_reader"
            else:
                safe_path = cast(str, resolve_safe_path(source, self.base_dir))
                if not os.path.isfile(safe_path):
                    raise ValueError(f"inputs[{index}].source does not exist: {safe_path}")
                if os.path.getsize(safe_path) > self.max_source_bytes:
                    raise ValueError(f"inputs[{index}].source exceeds max_source_bytes ({self.max_source_bytes})")
                extension = Path(safe_path).suffix.lower().lstrip(".")
                default_reader = ReaderManager.DEFAULT_READER.get(extension)
                if not default_reader:
                    raise ValueError(f"inputs[{index}] has no default reader for .{extension or '(none)'}")
                resolved = Path(safe_path)
            reader_name = raw.get("reader", default_reader)
            if not isinstance(reader_name, str) or not reader_name:
                raise ValueError(f"inputs[{index}].reader must be a non-empty string")
            if self.allowed_reader_names and reader_name not in self.allowed_reader_names:
                raise ValueError(f"inputs[{index}].reader is not in allowed_reader_names")
            if is_url and reader_name != "default_web_page_reader":
                raise ValueError("URL inputs require default_web_page_reader so redirect safety can be enforced")
            item_ext_info = raw.get("ext_info")
            if item_ext_info is not None and not isinstance(item_ext_info, dict):
                raise TypeError(f"inputs[{index}].ext_info must be an object")
            combined_ext_info = dict(shared_ext_info or {})
            combined_ext_info.update(item_ext_info or {})
            reader_kwargs = raw.get("reader_kwargs", {})
            if not isinstance(reader_kwargs, dict) or len(reader_kwargs) > 20:
                raise TypeError(f"inputs[{index}].reader_kwargs must be a bounded object")
            if any(not isinstance(key, str) or key.startswith("_") for key in reader_kwargs):
                raise ValueError(f"inputs[{index}].reader_kwargs contains an invalid key")
            output.append(
                {
                    "source": resolved,
                    "source_display": source,
                    "reader_name": reader_name,
                    "ext_info": combined_ext_info,
                    "reader_kwargs": reader_kwargs,
                }
            )
        return output

    def _load_one(self, spec: dict[str, Any]) -> list[Document]:
        reader = ReaderManager().get_instance_obj(spec["reader_name"])
        if reader is None:
            raise ValueError(f"reader is not registered: {spec['reader_name']}")
        kwargs = dict(spec["reader_kwargs"])
        if spec["ext_info"]:
            kwargs["ext_info"] = spec["ext_info"]
        documents = reader.load_data(spec["source"], **kwargs)
        if not isinstance(documents, list):
            raise TypeError(f"reader {spec['reader_name']} must return a list")
        return documents

    @staticmethod
    def _is_url(value: str) -> bool:
        parsed = urlparse(value)
        return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)
