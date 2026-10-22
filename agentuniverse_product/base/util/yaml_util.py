# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/29 12:14
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: yaml_util.py
import os
import stat
import tempfile

from ruamel.yaml import YAML
from typing import Any, Dict


def _write_yaml_atomically(file_path: str, config_data: dict, yaml: YAML) -> None:
    """Replace a config only after serialization has completed successfully."""
    target = os.path.realpath(file_path)
    directory = os.path.dirname(target)
    os.makedirs(directory, exist_ok=True)
    descriptor, temporary_path = tempfile.mkstemp(
        prefix=f".{os.path.basename(target)}.", suffix=".tmp", dir=directory
    )
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as temporary_file:
            yaml.dump(config_data, temporary_file)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        if os.path.exists(target):
            os.chmod(temporary_path, stat.S_IMODE(os.stat(target).st_mode))
        os.replace(temporary_path, target)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)


def update_nested_yaml_value(config_path: str, updates: dict) -> None:
    """Update nested values in YAML

    Args:
        config_path(str): The path to the YAML file.

        updates(dict): A dictionary of key-value pairs to update in the YAML file.
        The keys should be dot-separated paths to the target values,
        and the values should be the new values to set.

    Examples:
        update_nested_yaml_value(
        config_path='/xxx/agentUniverse/sample_standard_app/intelligence/agentic/agent/agent_instance/rag_agent_case/demo_rag_agent.yaml',
        updates={'info.description': 'demo rag agent',
          'profile.llm_model.name': 'qwen_llm',
          'profile.llm_model.temperature': 0.5,
           'profile.llm_model.model_name': 'qwen2-72b-instruct',
           'action.tool': ['google_search_tool']
           })
    """
    yaml = YAML()
    # read an existing YAML file
    with open(config_path, 'r', encoding='utf-8') as file:
        config_data = yaml.load(file)

    # batch update the value of the target key
    for path, new_value in updates.items():
        keys = path.split('.')
        d = config_data
        try:
            for key in keys[:-1]:
                if key not in d:
                    raise KeyError(f"Key '{key}' not found in the configuration")
                d = d[key]
            # modify the value of the target key
            d[keys[-1]] = new_value
        except Exception as e:
            print(f"Skipping update for '{path}': {e}")

    _write_yaml_atomically(config_path, config_data, yaml)


def write_yaml_file(file_path, config_data) -> None:
    """Writes the dictionary to a YAML file with the specified file path.
    
    Args:
        file_path (str): The path to the YAML file.
        config_data (dict): The dictionary to write to the YAML file.
    """
    yaml = YAML()
    _write_yaml_atomically(file_path, config_data, yaml)


def delete_yaml_file(file_path: str) -> None:
    """Delete a YAML file, allowing an already-absent file but not I/O failures.

    Args:
        file_path (str): The path to the YAML file.
    """
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


def read_yaml_file(file_path) -> Dict[str, Any]:
    """Reads the YAML file and returns the data as a dictionary.

    Args:
        file_path (str): The path to the YAML file.

    Returns:
        dict: The data from the YAML file as a dictionary.
    """
    yaml = YAML()

    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.load(file)

    return data
