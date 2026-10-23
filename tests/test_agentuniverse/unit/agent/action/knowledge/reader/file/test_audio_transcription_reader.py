# !/usr/bin/env python3

# @Time    : 2026/10/03
# @FileName: test_audio_transcription_reader.py

"""Tests for the AudioTranscriptionReader (local Whisper) reader.

faster-whisper is never installed here: a fake module is injected through
sys.modules, which also proves the dependency import is lazy. The
class-level model cache is cleared between tests.
"""

import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import agentuniverse.agent.action.knowledge.reader.file.audio_transcription_reader as atr_module
from agentuniverse.agent.action.knowledge.reader.file.audio_transcription_reader import AudioTranscriptionReader
from agentuniverse.agent.action.knowledge.reader.file.file_reader import DEFAULT_FILE_READERS, FileReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(atr_module.__file__), "audio_transcription_reader.yaml")


def _info(language="en", probability=0.97123456, duration=12.3456):
    return SimpleNamespace(language=language, language_probability=probability, duration=duration)


def _segments(*texts):
    return [SimpleNamespace(text=t, start=0.0, end=1.0) for t in texts]


class _FakeWhisperModel:
    """Consumes a per-call script of (segments, info) results."""

    def __init__(self, script=None):
        self.script = list(script or [])
        self.transcribe_calls = []

    def transcribe(self, source, language=None):
        self.transcribe_calls.append((source, language))
        if self.script:
            segments, info = self.script.pop(0)
        else:
            segments, info = [], _info()
        return iter(segments), info


def _fake_fw(fake_model):
    """Wrap a fake model instance into an injected faster_whisper module."""
    model_cls = MagicMock(return_value=fake_model)
    return SimpleNamespace(WhisperModel=model_cls), model_cls


def _write_audio(tmp_dir, name="speech.wav", payload=b"RIFFdummyaudio"):
    path = Path(tmp_dir) / name
    path.write_bytes(payload)
    return path


def _read(path, script=None, **kwargs):
    fake_model = _FakeWhisperModel(script)
    module, model_cls = _fake_fw(fake_model)
    with patch.dict(sys.modules, {"faster_whisper": module}):
        docs = AudioTranscriptionReader(**kwargs).load_data(file=Path(path))
    return docs[0], fake_model, model_cls


class TestAudioTranscriptionBasics(unittest.TestCase):
    def setUp(self) -> None:
        AudioTranscriptionReader._model_cache.clear()

    def test_segments_joined_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            doc, _, _ = _read(path, script=[(_segments(" hello", "world ", "!"), _info())])
        self.assertEqual(doc.text, "hello world !")
        self.assertEqual(doc.metadata["file_name"], "speech.wav")
        self.assertEqual(doc.metadata["audio_model"], "base")
        self.assertEqual(doc.metadata["audio_language"], "en")
        self.assertEqual(doc.metadata["audio_language_probability"], 0.9712)
        self.assertEqual(doc.metadata["audio_duration"], 12.346)
        self.assertEqual(doc.metadata["segment_count"], 3)

    def test_blank_segments_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            doc, _, _ = _read(path, script=[(_segments("  ", "kept", ""), _info())])
        self.assertEqual(doc.text, "kept")
        self.assertEqual(doc.metadata["segment_count"], 1)

    def test_empty_transcription_yields_empty_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            doc, _, _ = _read(path, script=[([], _info(duration=0.0))])
        self.assertEqual(doc.text, "")
        self.assertEqual(doc.metadata["segment_count"], 0)

    def test_missing_duration_info_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            info = SimpleNamespace(language="zh", language_probability=None, duration=None)
            doc, _, _ = _read(path, script=[(_segments("你好"), info)])
        self.assertEqual(doc.metadata["audio_duration"], 0.0)
        self.assertEqual(doc.metadata["audio_language_probability"], 0.0)

    def test_language_hint_forwarded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            _, fake_model, _ = _read(path, script=[(_segments("x"), _info())], language="zh")
        self.assertEqual(fake_model.transcribe_calls[0][1], "zh")

    def test_language_default_is_auto(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            _, fake_model, _ = _read(path, script=[(_segments("x"), _info())])
        self.assertIsNone(fake_model.transcribe_calls[0][1])

    def test_ext_info_merged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            fake_model = _FakeWhisperModel([(_segments("x"), _info())])
            module, _ = _fake_fw(fake_model)
            with patch.dict(sys.modules, {"faster_whisper": module}):
                doc = AudioTranscriptionReader().load_data(file=Path(path), ext_info={"batch": 7})[0]
        self.assertEqual(doc.metadata["batch"], 7)

    def test_str_path_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            fake_model = _FakeWhisperModel([(_segments("ok"), _info())])
            module, _ = _fake_fw(fake_model)
            with patch.dict(sys.modules, {"faster_whisper": module}):
                doc = AudioTranscriptionReader().load_data(file=str(path))[0]
        self.assertEqual(doc.text, "ok")

    def test_binary_stream_accepted_with_unknown_name(self) -> None:
        fake_model = _FakeWhisperModel([(_segments("streamed"), _info())])
        module, _ = _fake_fw(fake_model)
        with patch.dict(sys.modules, {"faster_whisper": module}):
            doc = AudioTranscriptionReader().load_data(file=io.BytesIO(b"RIFFdummy"))[0]
        self.assertEqual(doc.text, "streamed")
        self.assertEqual(doc.metadata["file_name"], "unknown")

    def test_unsupported_input_type_raises(self) -> None:
        with self.assertRaises(TypeError):
            AudioTranscriptionReader().load_data(file=12345)

    def test_text_stream_rejected(self) -> None:
        with self.assertRaises(TypeError):
            AudioTranscriptionReader().load_data(file=io.StringIO("not binary"))


class TestAudioTranscriptionModelLifecycle(unittest.TestCase):
    def setUp(self) -> None:
        AudioTranscriptionReader._model_cache.clear()

    def test_constructor_args_and_device_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            _, _, model_cls = _read(path, script=[(_segments("x"), _info())])
        model_cls.assert_called_once_with("base", compute_type="default")

    def test_device_forwarded_when_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            _, _, model_cls = _read(path, script=[(_segments("x"), _info())], device="cpu", compute_type="int8")
        model_cls.assert_called_once_with("base", compute_type="int8", device="cpu")

    def test_model_cached_across_instances(self) -> None:
        # FileReader builds a fresh reader per file: without the class-level
        # cache every file would reload the weights.
        shared_model = _FakeWhisperModel([(_segments("one"), _info()), (_segments("two"), _info())])
        module, model_cls = _fake_fw(shared_model)
        with tempfile.TemporaryDirectory() as tmp:
            p1 = _write_audio(tmp, "a.wav")
            p2 = _write_audio(tmp, "b.wav")
            with patch.dict(sys.modules, {"faster_whisper": module}):
                d1 = AudioTranscriptionReader().load_data(file=p1)[0]
                d2 = AudioTranscriptionReader().load_data(file=p2)[0]
        self.assertEqual(model_cls.call_count, 1)
        self.assertEqual((d1.text, d2.text), ("one", "two"))

    def test_cache_keyed_by_configuration(self) -> None:
        shared_model = _FakeWhisperModel()
        module, model_cls = _fake_fw(shared_model)
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            with patch.dict(sys.modules, {"faster_whisper": module}):
                AudioTranscriptionReader(model_size="base").load_data(file=path)
                AudioTranscriptionReader(model_size="tiny").load_data(file=path)
        self.assertEqual(model_cls.call_count, 2)

    def test_missing_dependency_raises_with_install_hint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            with patch.dict(sys.modules, {"faster_whisper": None}), self.assertRaises(ImportError) as ctx:
                AudioTranscriptionReader().load_data(file=Path(path))
        self.assertIn("audio_ext", str(ctx.exception))

    def test_transcribe_failure_raises_value_error(self) -> None:
        broken = MagicMock()
        broken.transcribe.side_effect = RuntimeError("codec exploded")
        module, _ = _fake_fw(broken)
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            with patch.dict(sys.modules, {"faster_whisper": module}), self.assertRaises(ValueError) as ctx:
                AudioTranscriptionReader().load_data(file=Path(path))
        self.assertIn("codec exploded", str(ctx.exception))


class TestAudioTranscriptionSafety(unittest.TestCase):
    def setUp(self) -> None:
        AudioTranscriptionReader._model_cache.clear()

    def test_missing_file_raises(self) -> None:
        with self.assertRaises(ValueError):
            AudioTranscriptionReader().load_data(file=Path("/nonexistent/a.wav"))

    def test_oversized_path_rejected_before_model_load(self) -> None:
        shared_model = _FakeWhisperModel()
        module, model_cls = _fake_fw(shared_model)
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp, payload=b"x" * 100)
            with patch.dict(sys.modules, {"faster_whisper": module}), self.assertRaises(ValueError) as ctx:
                AudioTranscriptionReader(max_file_bytes=50).load_data(file=path)
        self.assertIn("max_file_bytes", str(ctx.exception))
        model_cls.assert_not_called()

    def test_oversized_stream_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AudioTranscriptionReader(max_file_bytes=10).load_data(file=io.BytesIO(b"x" * 100))

    def test_overlong_duration_rejected_before_transcription(self) -> None:
        long_info = _info(duration=99.0)
        shared_model = _FakeWhisperModel([(_segments("never consumed"), long_info)])
        module, _ = _fake_fw(shared_model)
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp)
            with patch.dict(sys.modules, {"faster_whisper": module}), self.assertRaises(ValueError) as ctx:
                AudioTranscriptionReader(max_duration_seconds=10.0).load_data(file=path)
        self.assertIn("max_duration_seconds", str(ctx.exception))


class TestAudioTranscriptionConfig(unittest.TestCase):
    def setUp(self) -> None:
        AudioTranscriptionReader._model_cache.clear()

    def test_attributes_loaded_from_configer(self) -> None:
        configer = SimpleNamespace(
            name="audio",
            description="d",
            model_size="small",
            language="ja",
            device="cpu",
            compute_type="int8",
            max_file_bytes=999,
            max_duration_seconds=60.0,
        )
        reader = AudioTranscriptionReader()._initialize_by_component_configer(configer)
        self.assertEqual(reader.model_size, "small")
        self.assertEqual(reader.language, "ja")
        self.assertEqual(reader.device, "cpu")
        self.assertEqual(reader.compute_type, "int8")
        self.assertEqual(reader.max_file_bytes, 999)
        self.assertEqual(reader.max_duration_seconds, 60.0)

    def test_bad_values_raise_at_configer_load(self) -> None:
        for bad in (
            SimpleNamespace(name="a", description="d", model_size="  "),
            SimpleNamespace(name="a", description="d", language=""),
            SimpleNamespace(name="a", description="d", compute_type=""),
            SimpleNamespace(name="a", description="d", max_file_bytes=0),
            SimpleNamespace(name="a", description="d", max_duration_seconds=0),
        ):
            with self.assertRaises(ValueError):
                AudioTranscriptionReader()._initialize_by_component_configer(bad)

    def test_bad_types_raise_at_configer_load(self) -> None:
        for bad in (
            SimpleNamespace(name="a", description="d", model_size=3),
            SimpleNamespace(name="a", description="d", device=3),
            SimpleNamespace(name="a", description="d", max_file_bytes="1MB"),
            SimpleNamespace(name="a", description="d", max_duration_seconds="60"),
        ):
            with self.assertRaises(TypeError):
                AudioTranscriptionReader()._initialize_by_component_configer(bad)


class TestAudioTranscriptionRegistration(unittest.TestCase):
    def setUp(self) -> None:
        AudioTranscriptionReader._model_cache.clear()

    def test_yaml_resolves_to_reader_type(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(component_configer.get_component_config_type(), ComponentEnum.READER.value)

    def test_yaml_exposes_module_and_class(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.metadata_module,
            "agentuniverse.agent.action.knowledge.reader.file." "audio_transcription_reader",
        )
        self.assertEqual(component_configer.metadata_class, "AudioTranscriptionReader")

    def test_shipped_yaml_initializes_without_dependency(self) -> None:
        # No faster-whisper in this venv: clean init proves the lazy import.
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        reader = AudioTranscriptionReader()._initialize_by_component_configer(component_configer)
        self.assertEqual(reader.model_size, "base")
        self.assertIsNone(reader.language)

    def test_default_file_readers_routes_audio_suffixes(self) -> None:
        for suffix in (".wav", ".mp3", ".m4a", ".flac", ".ogg"):
            self.assertIs(DEFAULT_FILE_READERS[suffix], AudioTranscriptionReader, suffix)

    def test_reader_manager_maps_audio_types(self) -> None:
        for file_type in ("wav", "mp3", "m4a", "flac", "ogg"):
            self.assertEqual(ReaderManager.DEFAULT_READER[file_type], "default_audio_transcription_reader", file_type)

    def test_file_reader_dispatches_wav_end_to_end(self) -> None:
        shared_model = _FakeWhisperModel([(_segments("dispatched audio"), _info())])
        module, _ = _fake_fw(shared_model)
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_audio(tmp, "note.wav")
            with patch.dict(sys.modules, {"faster_whisper": module}):
                docs = FileReader().load_data(file_paths=[Path(path)])
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].text, "dispatched audio")
        self.assertEqual(docs[0].metadata["file_name"], "note.wav")


if __name__ == "__main__":
    unittest.main()
