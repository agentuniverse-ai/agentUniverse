# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/20 10:00
# @Author  : au_qa
# @FileName: test_reader_manager.py
"""Unit tests for the singleton ReaderManager."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.reader.reader_manager import \
    ReaderManager


@pytest.fixture
def manager():
    """Return the process-wide ReaderManager singleton."""
    return ReaderManager()


@pytest.fixture
def component():
    """Return a lightweight storable reader object."""
    return SimpleNamespace(default_symbol=False)


class TestReaderManager:
    """Test the registry behavior of ReaderManager."""

    @pytest.fixture(autouse=True)
    def restore_registry(self):
        """Unregister only the names added during each test."""
        mgr = ReaderManager()
        before = set(mgr.get_instance_name_list())
        yield
        for name in set(mgr.get_instance_name_list()) - before:
            mgr.unregister(name)

    def test_singleton_identity(self, manager):
        """ReaderManager() always returns the same instance."""
        assert ReaderManager() is manager

    def test_default_reader_mapping(self, manager):
        """Each documented file type maps to its default reader name."""
        expected = dict(pdf='default_pdf_reader', pptx='default_pptx_reader',
                        docx='default_docx_reader', txt='default_txt_reader',
                        md='default_markdown_reader',
                        markdown='default_markdown_reader',
                        csv='default_csv_reader', json='default_json_reader',
                        rar='default_rar_reader', zip='default_zip_reader',
                        sevenzip='default_sevenzip_reader', url='default_web_page_reader',
                        png='default_image_ocr_reader', jpg='default_image_ocr_reader',
                        jpeg='default_image_ocr_reader', bmp='default_image_ocr_reader',
                        tiff='default_image_ocr_reader', webp='default_image_ocr_reader')
        assert manager.DEFAULT_READER == expected

    def test_unknown_file_type_returns_none(self, manager):
        """An unknown file type resolves to None without a lookup."""
        assert manager.get_file_default_reader('unknown_type_xyz') is None

    def test_register_adds_instance_to_list(self, manager, component):
        """A registered reader name appears in the instance list."""
        manager.register('ut_reader_alice', component)
        assert 'ut_reader_alice' in manager.get_instance_name_list()

    def test_duplicate_register_keeps_first(self, manager, component):
        """Re-registering an existing name keeps the original object."""
        second = SimpleNamespace(default_symbol=False)
        manager.register('ut_reader_dup', component)
        manager.register('ut_reader_dup', second)
        assert manager._instance_obj_map['ut_reader_dup'] is component

    def test_unregister_removes_instance(self, manager, component):
        """Unregistering removes the name from the instance list."""
        manager.register('ut_reader_remove', component)
        manager.unregister('ut_reader_remove')
        assert manager.get_instance_name_list() == []

    def test_register_default_symbol_adds_default_instance(self, manager):
        """A default-symbol reader becomes the default instance."""
        default_comp = SimpleNamespace(default_symbol=True)
        manager.register('ut_reader_default', default_comp)
        assert '__default_instance__' in manager.get_instance_name_list()
        assert manager._instance_obj_map['__default_instance__'] is default_comp
