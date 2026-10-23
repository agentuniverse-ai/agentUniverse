"""Exercise ZIP limits through the framework's YAML configuration path."""
import io
import zipfile

import pytest
import yaml
from pydantic import ValidationError

from agentuniverse.agent.action.knowledge.reader.file.zip_reader import ZipReader
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def configured_reader(tmp_path, **settings):
    path = tmp_path / 'reader.yaml'
    path.write_text(yaml.safe_dump(dict(name='limited_zip', description='test', **settings)))
    config = ComponentConfiger().load_by_configer(Configer().load_by_path(str(path)))
    return ZipReader().initialize_by_component_configer(config)


def archive_bytes(entries, compression=zipfile.ZIP_STORED):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=compression) as archive:
        for name, content in entries:
            archive.writestr(name, content)
    return output.getvalue()


@pytest.mark.parametrize('settings,entries,compression', [
    ({'max_files': 1}, [('a.json', 'abc'), ('b.json', 'def')], zipfile.ZIP_STORED),
    ({'max_total_size': 5}, [('a.json', 'abc'), ('b.json', 'def')], zipfile.ZIP_STORED),
    ({'max_file_size': 3}, [('a.json', 'abcd')], zipfile.ZIP_STORED),
    ({'max_depth': 0}, [('inner.zip', archive_bytes([('a.json', 'abc')]))], zipfile.ZIP_STORED),
    ({'max_compression_ratio': 2}, [('a.json', 'a' * 1000)], zipfile.ZIP_DEFLATED),
])
def test_yaml_limits_reject_archive(tmp_path, settings, entries, compression):
    reader = configured_reader(tmp_path, **settings)
    path = tmp_path / 'input.zip'
    path.write_bytes(archive_bytes(entries, compression))
    with pytest.raises(ValueError):
        reader.load_data(path)


def test_yaml_chunk_size_and_numeric_conversion(tmp_path):
    reader = configured_reader(tmp_path, stream_chunk_size='3', max_files='2')
    assert reader.stream_chunk_size == 3
    assert reader.max_files == 2
    assert reader.name == 'limited_zip'
    path = tmp_path / 'input.zip'
    path.write_bytes(archive_bytes([('a.json', '你好世界')]))
    assert reader.load_data(path)[0].text == '你好世界'


def test_omitted_limits_preserve_defaults(tmp_path):
    reader = configured_reader(tmp_path)
    default = ZipReader()
    for field in ('max_total_size', 'max_file_size', 'max_depth', 'max_files',
                  'max_compression_ratio', 'stream_chunk_size'):
        assert getattr(reader, field) == getattr(default, field)


def test_invalid_yaml_limit_rejected(tmp_path):
    with pytest.raises(ValidationError):
        configured_reader(tmp_path, max_files='invalid')
