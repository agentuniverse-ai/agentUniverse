import pytest

from agentuniverse.base.config.configer import Configer


@pytest.mark.parametrize("contents", ["", "# comment-only configuration\n"])
def test_empty_yaml_loads_as_mutable_mapping(tmp_path, contents):
    config_path = tmp_path / "empty.yaml"
    config_path.write_text(contents, encoding="utf-8")

    configer = Configer(str(config_path)).load()

    assert configer.to_dict() == {}
    configer.set("enabled", True)
    assert configer.get("enabled") is True
