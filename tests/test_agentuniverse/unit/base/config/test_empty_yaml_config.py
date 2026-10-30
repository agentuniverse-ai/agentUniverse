from agentuniverse.base.config.configer import Configer


def test_empty_yaml_file_loads_as_empty_mapping(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")

    config = Configer().load_by_path(str(path))

    assert config.value == {}
    assert config.get("missing") is None
