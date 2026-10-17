"""Load real configuration files by their final extension, regardless of directory names."""

import pytest

from agentuniverse.base.config.configer import Configer


@pytest.mark.parametrize('entry_point', ['load', 'load_by_path'])
@pytest.mark.parametrize(
    ('relative_path', 'content'),
    [
        ('config.yaml', 'service:\n  name: yaml-agent\n  retries: 3\n'),
        ('backup.toml/config.yaml', 'service:\n  name: yaml-agent\n  retries: 3\n'),
        ('config.toml.yaml', 'service:\n  name: yaml-agent\n  retries: 3\n'),
        ('config.toml', '[service]\nname = "yaml-agent"\nretries = 3\n'),
        ('backup.yaml/config.toml', '[service]\nname = "yaml-agent"\nretries = 3\n'),
    ],
)
def test_load_config_uses_final_file_extension(tmp_path, entry_point, relative_path, content):
    """Both entry points preserve the parsed data when a path contains another format name."""
    path = tmp_path / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    configer = Configer(str(path))

    loaded = configer.load() if entry_point == 'load' else configer.load_by_path(str(path))

    assert loaded is configer
    assert loaded.value == {'service': {'name': 'yaml-agent', 'retries': 3}}


@pytest.mark.parametrize('entry_point', ['load', 'load_by_path'])
def test_load_config_rejects_unsupported_final_extension(tmp_path, entry_point):
    """An earlier supported suffix does not make an unsupported file loadable."""
    path = tmp_path / 'config.toml.txt'
    path.write_text('[service]\nname = "agent"\n', encoding='utf-8')
    configer = Configer(str(path))

    with pytest.raises(ValueError, match='Unsupported file format: txt'):
        if entry_point == 'load':
            configer.load()
        else:
            configer.load_by_path(str(path))
