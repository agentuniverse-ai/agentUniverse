"""A failed YAML serialization must not destroy the last valid config."""

import pytest

from agentuniverse_product.base.util import yaml_util


@pytest.mark.parametrize("operation", ["create", "update"])
def test_failed_serialization_preserves_existing_file(tmp_path, monkeypatch, operation):
    config = tmp_path / "config.yaml"
    config.write_text("name: original\n", encoding="utf-8")
    real_yaml = yaml_util.YAML()

    class FailingYAML:
        def load(self, stream):
            return real_yaml.load(stream)

        def dump(self, _data, stream):
            stream.write("name: truncated")
            raise RuntimeError("serialization failed")

    monkeypatch.setattr(yaml_util, "YAML", FailingYAML)
    with pytest.raises(RuntimeError, match="serialization failed"):
        if operation == "create":
            yaml_util.write_yaml_file(str(config), {"name": "replacement"})
        else:
            yaml_util.update_nested_yaml_value(str(config), {"name": "replacement"})

    assert config.read_text(encoding="utf-8") == "name: original\n"
    assert list(tmp_path.iterdir()) == [config]


def test_successful_updates_preserve_yaml_and_replace_content(tmp_path):
    config = tmp_path / "nested" / "config.yaml"
    yaml_util.write_yaml_file(str(config), {"name": "original", "other": 7})
    yaml_util.update_nested_yaml_value(str(config), {"name": "replacement"})

    assert yaml_util.read_yaml_file(str(config)) == {"name": "replacement", "other": 7}
    assert list(config.parent.iterdir()) == [config]


def test_failed_replace_keeps_existing_file_and_cleans_temporary_file(tmp_path, monkeypatch):
    config = tmp_path / "config.yaml"
    config.write_text("name: original\n", encoding="utf-8")

    def fail_replace(_source, _target):
        raise OSError("replace failed")

    monkeypatch.setattr(yaml_util.os, "replace", fail_replace)
    with pytest.raises(OSError, match="replace failed"):
        yaml_util.write_yaml_file(str(config), {"name": "replacement"})

    assert config.read_text(encoding="utf-8") == "name: original\n"
    assert list(tmp_path.iterdir()) == [config]


def test_failed_new_write_does_not_publish_partial_config(tmp_path, monkeypatch):
    config = tmp_path / "new.yaml"

    class FailingYAML:
        def dump(self, _data, stream):
            stream.write("partial")
            raise RuntimeError("serialization failed")

    monkeypatch.setattr(yaml_util, "YAML", FailingYAML)
    with pytest.raises(RuntimeError):
        yaml_util.write_yaml_file(str(config), {"name": "replacement"})

    assert list(tmp_path.iterdir()) == []
