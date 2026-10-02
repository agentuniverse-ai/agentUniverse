# !/usr/bin/env python3

# @Time    : 2026/10/03
# @FileName: audio_transcription_reader.py

"""
Audio transcription reader (local Whisper, via faster-whisper).

Meeting recordings, voice memos, podcast and call-center exports are a
large body of knowledge that the file readers could not ingest: the
family covered text and document formats (txt/pdf/office/csv/archives)
but had no audio path. This reader transcribes local audio files
(``.wav`` / ``.mp3`` / ``.m4a`` / ``.flac`` / ``.ogg``) into text
Documents with a **local** Whisper model through the optional
``faster-whisper`` backend — no cloud speech API, no credentials, and the
audio never leaves the machine (the same offline/private-deployment
stance as the local CrossEncoder reranker).

Each file produces one Document:

* text — the transcribed segments joined in order (each stripped, single
  spaces between);
* metadata — ``file_name``, detected ``audio_language`` (with
  probability), ``audio_duration`` seconds, ``segment_count``, the
  ``audio_model`` size used, plus caller ``ext_info``.

The heavy dependency is optional and lazily imported: the shipped yaml
loads at framework start without ``faster-whisper`` installed, and a
missing package raises ``ImportError`` carrying the exact install command
(``pip install 'agentuniverse[audio_ext]'``). Loaded Whisper models are
cached **per class** under a lock, keyed by (model_size, device,
compute_type), so many readers or many files in one ingestion never
reload weights — important because ``FileReader`` constructs a fresh
reader instance per file.

Safety bounds (audio files are large and hostile inputs exist):

* ``max_file_bytes`` (default 200 MiB) is enforced via ``stat`` before
  reading a path, and via a bounded read for file-like objects;
* ``max_duration_seconds`` (default 4 h) is checked against the container
  metadata *before* any segment is transcribed, so an over-long recording
  is rejected without burning minutes of compute;
* transcription treats audio strictly as data — nothing is executed;
* misconfiguration (wrong types, non-positive bounds, empty model size)
  fails loudly at component-load time rather than silently weakening a
  bound.

Unreadable or untranscribable input raises ``ValueError`` (same
convention as the other file readers).
"""

import logging
import threading
from io import BytesIO
from pathlib import Path
from typing import Any, ClassVar

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)

_DEFAULT_MAX_FILE_BYTES = 200 * 1024 * 1024
_DEFAULT_MAX_DURATION_SECONDS = 4 * 60 * 60.0


class AudioTranscriptionReader(Reader):
    """Local Whisper transcription reader for audio files.

    Accepts a path string, ``Path``, or a binary file-like object, and
    returns exactly one Document per audio file.

    Attributes:
        model_size: faster-whisper model size or local model path
            (``tiny`` / ``base`` / ``small`` / ``medium`` / ``large-v3``, ...).
        language: Language hint passed to the model; ``None`` (default)
            enables automatic detection.
        device: Device string (``"cpu"``, ``"cuda"``, ...); empty (default)
            lets faster-whisper decide.
        compute_type: faster-whisper compute type (``"default"``,
            ``"int8"``, ``"float16"``, ...).
        max_file_bytes: Maximum accepted file size, enforced before the
            content is fully read.
        max_duration_seconds: Maximum accepted audio duration, enforced
            from container metadata before transcription starts.
    """

    model_size: str = "base"
    language: str | None = None
    device: str = ""
    compute_type: str = "default"
    max_file_bytes: int = _DEFAULT_MAX_FILE_BYTES
    max_duration_seconds: float = _DEFAULT_MAX_DURATION_SECONDS

    # Class-level model cache: FileReader builds a fresh reader instance per
    # file, so an instance-level cache would reload the weights every time.
    # Keyed by (model_size, device, compute_type); guarded by a lock so
    # concurrent ingestions load each configuration at most once.
    _model_cache: ClassVar[dict[tuple[str, str, str], Any]] = {}
    _model_cache_lock: ClassVar[threading.Lock] = threading.Lock()

    def _load_data(self, file: str | Path | object, ext_info: dict | None = None) -> list[Document]:
        """Transcribe one audio file into a single Document.

        Args:
            file: Path string, ``Path``, or binary file-like audio object.
            ext_info: Extra metadata merged onto the produced Document.

        Returns:
            A one-element list with the transcribed Document.

        Raises:
            ValueError: If the input is missing, oversized, too long, or
                cannot be transcribed.
            TypeError: If ``file`` is neither a path nor a file-like object.
            ImportError: With the install command when ``faster-whisper``
                is not installed.
        """
        self._validate_config()
        source, file_name = self._prepare_source(file)
        model = self._get_model()
        try:
            segments, info = model.transcribe(source, language=self.language)
        except Exception as e:
            raise ValueError(f"Failed to transcribe audio file {file_name}: {e}") from e
        duration = float(getattr(info, "duration", 0.0) or 0.0)
        # Bound checked from container metadata BEFORE consuming any segment,
        # so an over-long recording is rejected without burning compute.
        if duration > self.max_duration_seconds:
            raise ValueError(
                f"Audio {file_name} is {duration:.1f}s long, exceeding "
                f"max_duration_seconds={self.max_duration_seconds}."
            )
        try:
            texts = []
            for segment in segments:
                text = (getattr(segment, "text", "") or "").strip()
                if text:
                    texts.append(text)
        except Exception as e:
            raise ValueError(f"Failed while reading transcription segments of {file_name}: {e}") from e
        metadata: dict[str, Any] = {
            "file_name": file_name,
            "audio_model": self.model_size,
            "audio_language": getattr(info, "language", None),
            "audio_language_probability": round(float(getattr(info, "language_probability", 0.0) or 0.0), 4),
            "audio_duration": round(duration, 3),
            "segment_count": len(texts),
        }
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=" ".join(texts), metadata=metadata)]

    # ------------------------------------------------------------------ #
    # Input handling
    # ------------------------------------------------------------------ #
    def _prepare_source(self, file: str | Path | object) -> tuple[Any, str]:
        """Validate size bounds and return ``(transcribe_source, file_name)``.

        Paths are checked via ``stat`` before any read; file-like objects are
        drained through a bounded read into memory so the cap holds for
        streams of unknown length.

        Raises:
            ValueError: When the input is missing or exceeds max_file_bytes.
            TypeError: When ``file`` is not a path or file-like object.
        """
        if isinstance(file, str):
            file = Path(file)
        if isinstance(file, Path):
            if not file.exists():
                raise ValueError(f"Audio file not found: {file}")
            size = file.stat().st_size
            if size > self.max_file_bytes:
                raise ValueError(
                    f"Audio file {file.name} is {size} bytes, exceeding max_file_bytes={self.max_file_bytes}."
                )
            return str(file), file.name
        if hasattr(file, "read"):
            raw = file.read(self.max_file_bytes + 1)
            if isinstance(raw, str):
                raise TypeError("Audio input must be opened in binary mode")
            if not isinstance(raw, bytes | bytearray):
                raise TypeError("Unsupported file object type")
            if len(raw) > self.max_file_bytes:
                raise ValueError(f"Audio content exceeds max_file_bytes={self.max_file_bytes}.")
            name_attr = getattr(file, "name", None)
            file_name = Path(name_attr).name if isinstance(name_attr, str) else "unknown"
            return BytesIO(bytes(raw)), file_name
        raise TypeError("file must be a path string, Path, or file-like object")

    # ------------------------------------------------------------------ #
    # Model loading
    # ------------------------------------------------------------------ #
    def _get_model(self):
        """Load (once per configuration, class-wide) and cache the model.

        Raises:
            ImportError: With the exact install command when the optional
                ``faster-whisper`` dependency is missing.
        """
        key = (self.model_size, self.device, self.compute_type)
        with self._model_cache_lock:
            model = self._model_cache.get(key)
            if model is None:
                try:
                    from faster_whisper import WhisperModel
                except ImportError as exc:
                    raise ImportError(
                        "AudioTranscriptionReader requires the faster-whisper package. "
                        "Install it with: pip install 'agentuniverse[audio_ext]' "
                        "(or pip install faster-whisper)."
                    ) from exc
                kwargs: dict[str, Any] = {"compute_type": self.compute_type}
                if self.device:
                    kwargs["device"] = self.device
                logger.info("AudioTranscriptionReader loading Whisper model %r", self.model_size)
                model = WhisperModel(self.model_size, **kwargs)
                self._model_cache[key] = model
            return model

    # ------------------------------------------------------------------ #
    # Configuration validation
    # ------------------------------------------------------------------ #
    def _validate_config(self) -> None:
        """Fail loudly on configuration that would weaken a safety bound.

        Raises:
            TypeError: On wrong field types.
            ValueError: On empty model_size, non-positive bounds, or an
                empty-string language.
        """
        if not isinstance(self.model_size, str):
            raise TypeError(f"model_size must be a string, got {self.model_size!r}.")
        if not self.model_size.strip():
            raise ValueError("model_size must be a non-empty string.")
        if self.language is not None and (not isinstance(self.language, str) or not self.language.strip()):
            raise ValueError("language must be None or a non-empty string.")
        if not isinstance(self.device, str):
            raise TypeError(f"device must be a string ('' for auto), got {self.device!r}.")
        if not isinstance(self.compute_type, str) or not self.compute_type.strip():
            raise ValueError("compute_type must be a non-empty string.")
        if not isinstance(self.max_file_bytes, int) or isinstance(self.max_file_bytes, bool):
            raise TypeError(f"max_file_bytes must be an integer, got {self.max_file_bytes!r}.")
        if self.max_file_bytes < 1:
            raise ValueError(f"max_file_bytes must be a positive integer, got {self.max_file_bytes!r}.")
        if not isinstance(self.max_duration_seconds, int | float) or isinstance(self.max_duration_seconds, bool):
            raise TypeError(f"max_duration_seconds must be a number, got {self.max_duration_seconds!r}.")
        if self.max_duration_seconds <= 0:
            raise ValueError(f"max_duration_seconds must be positive, got {self.max_duration_seconds!r}.")

    def _initialize_by_component_configer(self, reader_configer: ComponentConfiger) -> "AudioTranscriptionReader":
        """Initialize the reader from its component config."""
        super()._initialize_by_component_configer(reader_configer)
        for attr in ("model_size", "language", "device", "compute_type", "max_file_bytes", "max_duration_seconds"):
            if hasattr(reader_configer, attr):
                setattr(self, attr, getattr(reader_configer, attr))
        # Validate eagerly so a misconfigured bound fails at component-load
        # time rather than silently at read time. The model itself stays
        # lazy: the shipped yaml must load without faster-whisper installed.
        self._validate_config()
        return self
