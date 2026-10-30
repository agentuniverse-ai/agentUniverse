from agentuniverse.base.config.configer import Configer


def test_configer_accepts_uppercase_yaml_extension(tmp_path):
    config_path = tmp_path / "config.YAML"
    config_path.write_text("answer: 42\n", encoding="utf-8")

    config = Configer().load_by_path(str(config_path))

    assert config.value == {"answer": 42}
