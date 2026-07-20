#!/usr/bin/env python3
"""Tests for BatchKnowledgeReader."""

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.knowledge.reader.batch_reader import BatchKnowledgeReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import WebPageReader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = Path(__file__).parents[7] / "agentuniverse/agent/action/knowledge/reader/batch_reader.yaml"


class FakeReader:
    def __init__(self, documents=None, error=None, delay=0, capture=None):
        self.documents = documents or []
        self.error = error
        self.delay = delay
        self.capture = capture

    def load_data(self, source, **kwargs):
        if self.capture is not None:
            self.capture.append((source, kwargs))
        if self.delay:
            time.sleep(self.delay)
        if self.error:
            raise self.error
        return [document.model_copy(deep=True) for document in self.documents]


class FakeManagerFactory:
    DEFAULT_READER = ReaderManager.DEFAULT_READER

    def __init__(self, readers):
        self.readers = readers

    def __call__(self):
        return self

    def get_instance_obj(self, name):
        return self.readers.get(name)


class BatchReaderTestCase(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory()
        self.base_dir = self.context.name
        self.reader = BatchKnowledgeReader(base_dir=self.base_dir)

    def tearDown(self):
        self.context.cleanup()

    def file(self, name, content="content"):
        path = Path(self.base_dir, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    @staticmethod
    def manager(readers):
        return patch(
            "agentuniverse.agent.action.knowledge.reader.batch_reader.ReaderManager",
            new=FakeManagerFactory(readers),
        )


class TestBatchReaderOperations(BatchReaderTestCase):
    def test_auto_dispatch_preserves_order_and_adds_provenance(self):
        self.file("slow.txt")
        self.file("fast.md")
        readers = {
            "default_txt_reader": FakeReader([Document(id="1", text="slow")], delay=0.02),
            "default_markdown_reader": FakeReader([Document(id="2", text="fast")]),
        }
        with self.manager(readers):
            documents = self.reader.load_data(["slow.txt", "fast.md"])
        self.assertEqual([document.text for document in documents], ["slow", "fast"])
        self.assertEqual(documents[0].metadata["batch_source"], "slow.txt")
        self.assertEqual(documents[1].metadata["batch_input_index"], 1)
        self.assertEqual(self.reader.last_report["successful_input_count"], 2)

    def test_custom_reader_receives_kwargs_and_combined_ext_info(self):
        source = self.file("data.csv")
        capture = []
        readers = {"custom_csv": FakeReader([Document(text="csv")], capture=capture)}
        with self.manager(readers):
            self.reader.load_data(
                [
                    {
                        "source": "data.csv",
                        "reader": "custom_csv",
                        "ext_info": {"source_type": "finance"},
                        "reader_kwargs": {"delimiter": ";"},
                    }
                ],
                ext_info={"tenant": "acme"},
            )
        self.assertEqual(capture[0][0].resolve(), source.resolve())
        self.assertEqual(capture[0][1]["delimiter"], ";")
        self.assertEqual(capture[0][1]["ext_info"], {"tenant": "acme", "source_type": "finance"})

    def test_continue_on_error_isolates_failed_input(self):
        self.file("bad.txt")
        self.file("good.md")
        readers = {
            "default_txt_reader": FakeReader(error=ValueError("cannot parse")),
            "default_markdown_reader": FakeReader([Document(text="good")]),
        }
        with self.manager(readers):
            documents = self.reader.load_data(["bad.txt", "good.md"], continue_on_error=True)
        self.assertEqual([document.text for document in documents], ["good"])
        report = self.reader.last_report
        self.assertEqual(report["failed_input_count"], 1)
        self.assertEqual(report["errors"][0]["error_type"], "ValueError")

    def test_fail_fast_mode_raises_descriptive_error(self):
        self.file("bad.txt")
        with (
            self.manager({"default_txt_reader": FakeReader(error=RuntimeError("boom"))}),
            self.assertRaisesRegex(RuntimeError, "batch input 0 failed.*boom"),
        ):
            self.reader.load_data(["bad.txt"], continue_on_error=False)

    def test_fail_fast_does_not_wait_for_unrelated_slow_work(self):
        self.file("slow.txt")
        self.file("bad.md")
        readers = {
            "default_txt_reader": FakeReader([Document(text="slow")], delay=0.25),
            "default_markdown_reader": FakeReader(error=RuntimeError("boom")),
        }
        started = time.monotonic()
        with self.manager(readers), self.assertRaisesRegex(RuntimeError, "boom"):
            self.reader.load_data(["slow.txt", "bad.md"], continue_on_error=False, max_workers=2)
        self.assertLess(time.monotonic() - started, 0.15)

    def test_deduplicate_by_id(self):
        self.file("one.txt")
        self.file("two.txt")
        reader = FakeReader([Document(id="same", text="same text")])
        with self.manager({"default_txt_reader": reader}):
            documents = self.reader.load_data(["one.txt", "two.txt"], deduplicate=True)
        self.assertEqual(len(documents), 1)

    def test_deduplicate_can_be_disabled(self):
        self.file("one.txt")
        self.file("two.txt")
        reader = FakeReader([Document(id="same", text="same text")])
        with self.manager({"default_txt_reader": reader}):
            documents = self.reader.load_data(["one.txt", "two.txt"], deduplicate=False)
        self.assertEqual(len(documents), 2)

    def test_deduplicate_by_text(self):
        self.file("one.txt")
        self.file("two.txt")
        readers = {
            "default_txt_reader": FakeReader([Document(id="1", text="same")]),
            "default_markdown_reader": FakeReader([Document(id="2", text="same")]),
        }
        Path(self.base_dir, "two.txt").rename(Path(self.base_dir, "two.md"))
        with self.manager(readers):
            documents = self.reader.load_data(["one.txt", "two.md"], deduplicate_by="text")
        self.assertEqual(len(documents), 1)

    def test_url_requires_explicit_opt_in(self):
        with self.assertRaisesRegex(ValueError, "URL inputs are disabled"):
            self.reader.load_data(["https://example.com/article"])

    def test_url_dispatch_when_enabled(self):
        self.reader.allow_urls = True
        readers = {"default_web_page_reader": FakeReader([Document(text="web")])}
        with (
            self.manager(readers),
            patch(
                "agentuniverse.agent.action.knowledge.reader.batch_reader.validate_public_http_url",
                side_effect=lambda value: value,
            ),
        ):
            documents = self.reader.load_data(["https://example.com/article"])
        self.assertEqual(documents[0].metadata["batch_source"], "https://example.com/article")

    def test_url_rejects_private_and_link_local_destinations(self):
        self.reader.allow_urls = True
        for url in ("http://127.0.0.1/", "http://169.254.169.254/latest/meta-data/", "http://[::1]/"):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, "non-public"):
                self.reader.load_data([url])


class TestBatchReaderValidation(BatchReaderTestCase):
    def test_rejects_empty_and_oversized_input_list(self):
        with self.assertRaisesRegex(ValueError, "non-empty list"):
            self.reader.load_data([])
        self.reader.max_inputs = 1
        with self.assertRaisesRegex(ValueError, "max_inputs"):
            self.reader.load_data(["one.txt", "two.txt"])

    def test_rejects_path_escape_and_missing_file(self):
        with self.assertRaisesRegex(ValueError, "escapes the allowed directory"):
            self.reader.load_data(["../outside.txt"])
        with self.assertRaisesRegex(ValueError, "does not exist"):
            self.reader.load_data(["missing.txt"])

    def test_rejects_unknown_extension(self):
        self.file("data.unknown")
        with self.assertRaisesRegex(ValueError, "no default reader"):
            self.reader.load_data(["data.unknown"])

    def test_source_size_limit(self):
        self.file("large.txt", "x" * 20)
        self.reader.max_source_bytes = 10
        with self.assertRaisesRegex(ValueError, "max_source_bytes"):
            self.reader.load_data(["large.txt"])

    def test_reader_allowlist(self):
        self.file("data.txt")
        self.reader.allowed_reader_names = ["approved_reader"]
        with self.assertRaisesRegex(ValueError, "allowed_reader_names"):
            self.reader.load_data(["data.txt"])

    def test_worker_limit(self):
        self.file("data.txt")
        with self.assertRaisesRegex(ValueError, "max_workers"):
            self.reader.load_data(["data.txt"], max_workers=self.reader.max_workers + 1)

    def test_document_and_character_limits(self):
        self.file("data.txt")
        self.reader.max_documents = 1
        fake = FakeReader([Document(text="one"), Document(text="two")])
        with self.manager({"default_txt_reader": fake}), self.assertRaisesRegex(ValueError, "max_documents"):
            self.reader.load_data(["data.txt"], deduplicate=False)
        self.reader.max_documents = 10
        self.reader.max_total_chars = 2
        with self.manager({"default_txt_reader": fake}), self.assertRaisesRegex(ValueError, "max_total_chars"):
            self.reader.load_data(["data.txt"], deduplicate=False)

    def test_per_source_limits_are_enforced_at_completion(self):
        self.file("data.txt")
        fake = FakeReader([Document(text="one"), Document(text="two")])
        self.reader.max_documents_per_source = 1
        with self.manager({"default_txt_reader": fake}), self.assertRaisesRegex(
            ValueError, "max_documents_per_source"
        ):
            self.reader.load_data(["data.txt"], continue_on_error=False)

    def test_non_document_reader_result_is_rejected(self):
        self.file("data.txt")

        class InvalidReader:
            @staticmethod
            def load_data(_source, **_kwargs):
                return ["not a document"]

        with self.manager({"default_txt_reader": InvalidReader()}), self.assertRaisesRegex(TypeError, "non-Document"):
            self.reader.load_data(["data.txt"])

    def test_invalid_configuration(self):
        self.reader.max_workers = True
        with self.assertRaisesRegex(ValueError, "max_workers must be a positive integer"):
            self.reader.load_data(["data.txt"])


class TestBatchReaderRegistration(unittest.TestCase):
    def test_yaml_component_schema(self):
        component = ComponentConfiger().load_by_configer(Configer(path=str(YAML_PATH)).load())
        self.assertEqual(component.get_component_config_type(), ComponentEnum.READER.value)
        self.assertEqual(component.metadata_class, "BatchKnowledgeReader")
        self.assertEqual(component.max_workers, 4)


class TestSafeWebRedirects(unittest.TestCase):
    def test_redirect_destination_is_revalidated(self):
        class RedirectResponse:
            def __init__(self):
                self.is_redirect = True
                self.headers = {"location": "http://127.0.0.1/admin"}

        client = MagicMock()
        client.__enter__.return_value.get.return_value = RedirectResponse()
        checked = []

        def validate(url):
            checked.append(url)
            if "127.0.0.1" in url:
                raise ValueError("non-public")
            return url

        with (
            patch("httpx.Client", return_value=client),
            patch(
                "agentuniverse.agent.action.knowledge.reader.web.web_page_reader.validate_public_http_url",
                side_effect=validate,
            ),
            self.assertRaisesRegex(ValueError, "non-public"),
        ):
            WebPageReader()._fetch_html("https://example.com/start")
        self.assertEqual(checked[-1], "http://127.0.0.1/admin")


if __name__ == "__main__":
    unittest.main()
