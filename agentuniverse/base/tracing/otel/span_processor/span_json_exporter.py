# per_span_file_exporter.py
import datetime
import json
import pathlib
import typing

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult


class SpanJsonExporter(SpanExporter):
    """SpanExporter writing each exported span to its own JSON file.

    Files are stored under base_dir in folders keyed by the span kind attribute
    and are written atomically through a temporary file.
    """
    span_kind_attr_name = "au.span.kind"

    def __init__(self, base_dir: str = "./monitor") -> None:
        """Create the exporter and ensure its output directory exists.

        Args:
        base_dir: root directory for the span JSON files.
        """
        self.base_dir = pathlib.Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def export(self,
               spans: typing.Sequence[ReadableSpan]) -> "SpanExportResult":
        """Export the given spans, one JSON file per span.

        Args:
        spans: sequence of readable spans to export.

        Returns:
        SpanExportResult: SUCCESS, or FAILURE when an exception occurs.
        """
        try:
            for span in spans:
                folder = self._folder_for(span)
                if not folder:
                    continue
                folder.mkdir(parents=True, exist_ok=True)
                file_path = folder / self._filename_for(span)
                tmp_path = file_path.with_suffix(".tmp")

                with tmp_path.open("w", encoding="utf-8") as f:
                    json.dump(self._span_to_dict(span), f,
                              ensure_ascii=False, indent=2, default=str)
                tmp_path.replace(file_path)
            return SpanExportResult.SUCCESS
        except Exception:
            return SpanExportResult.FAILURE

    def shutdown(self):
        """Finalize the exporter; a no-op because files are written during export."""
        ...

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        """Flush any pending spans.

        Args:
        timeout_millis: allowed flush time in milliseconds.

        Returns:
        bool: True, as all spans are written synchronously during export.
        """
        return True

    def _folder_for(self, span: ReadableSpan) -> pathlib.Path | None:
        """Folder that should contain the span's JSON file.

        Args:
        span: the readable span to locate.

        Returns:
        pathlib.Path or None: the sub folder, or None when no span kind attribute is set.
        """
        val = span.attributes.get(self.span_kind_attr_name, None)
        return self.base_dir / str(val) if val else val


    def _filename_for(self, span: ReadableSpan) -> str:
        """Build the JSON file name for a span.

        Args:
        span: the span to name.

        Returns:
        str: file name combining the start timestamp, trace id and span id.
        """
        t  = datetime.datetime.utcfromtimestamp(span.start_time / 1e9)
        ts = t.strftime("%Y%m%dT%H%M%S%f")
        return f"{ts}_{span.context.trace_id:032x}_{span.context.span_id:016x}.json"

    def _span_to_dict(self, span: ReadableSpan) -> dict:
        """Serialize a span into a JSON-compatible dict.

        Args:
        span: the readable span to convert.

        Returns:
        dict: trace/span/parent ids, name, kind, timestamps, status and attributes.
        """
        ctx = span.context
        return {
            "trace_id": f"{ctx.trace_id:032x}",
            "span_id":  f"{ctx.span_id:016x}",
            "parent_span_id": (
                f"{span.parent.span_id:016x}" if span.parent else None),
            "name": span.name,
            "kind": span.kind.name,
            "start_unix_nano": span.start_time,
            "end_unix_nano":   span.end_time,
            "status": span.status.status_code.name,
            "attributes": dict(span.attributes),
        }
