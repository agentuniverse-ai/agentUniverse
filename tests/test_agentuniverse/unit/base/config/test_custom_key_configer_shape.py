from pathlib import Path

from agentuniverse.base.config.custom_configer.custom_key_configer import CustomKeyConfiger


def test_non_mapping_key_list_is_ignored(tmp_path: Path):
    config_path = tmp_path / "custom_key.yaml"
    config_path.write_text("KEY_LIST: []\n", encoding="utf-8")

    # The singleton is initialized once in this test process; an empty list
    # must not make initialization call .items() on a non-mapping value.
    CustomKeyConfiger(str(config_path))
