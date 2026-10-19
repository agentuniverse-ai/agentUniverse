"""Exercise public discovery with real SDK sessions and stdio subprocesses."""
import asyncio
import json
import os
from pathlib import Path
import sys

import pytest

from agentuniverse.agent.action.tool.mcp_tool import MCPTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.action.toolkit.mcp_toolkit import MCPToolkit
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager

SERVER = Path(__file__).parent / 'fixtures' / 'paginated_mcp_server.py'
MODES = ('pages', 'empty_middle', 'empty_cursor', 'single')


@pytest.fixture(autouse=True)
def isolate_registry():
    manager = ToolManager()
    previous_tools = manager._instance_obj_map.copy()
    config = ApplicationConfigManager()
    try:
        previous_config = config.app_configer
    except ValueError:
        previous_config = None
    config.app_configer = AppConfiger()
    try:
        yield
    finally:
        manager._instance_obj_map.clear()
        manager._instance_obj_map.update(previous_tools)
        config.app_configer = previous_config


def connection(tmp_path, mode):
    log = tmp_path / 'requests.jsonl'
    return {'transport': 'stdio', 'command': sys.executable,
            'args': [str(SERVER), mode, str(log)],
            'env': {'PYTHONPATH': os.pathsep.join(sys.path)}}, log


def cursors(log):
    return [json.loads(line) for line in log.read_text(encoding='utf-8').splitlines()]


def run_discovery(operation):
    async def bounded():
        return await asyncio.wait_for(operation, timeout=10)
    return asyncio.run(bounded())


def expected_cursors(mode, *, lookup=False):
    if mode == 'single':
        return [None]
    if mode == 'empty_cursor':
        return [None, '']
    if lookup and mode == 'pages':
        return [None, 'opaque+/=1']
    return [None, 'opaque+/=1', 'opaque/end2']


@pytest.mark.parametrize('mode', MODES)
def test_tool_finds_remote_name_beyond_first_page(tmp_path, mode):
    args, log = connection(tmp_path, mode)
    instance = MCPTool(name='local_alias', origin_tool_name='target', **args)
    run_discovery(instance.get_tool_info())
    assert instance.input_keys == ['value']
    assert instance.args_model_schema['properties'] == {'value': {'type': 'string'}}
    assert instance.description.startswith('description target')
    assert instance.name == 'local_alias'
    assert cursors(log) == expected_cursors(mode, lookup=True)


@pytest.mark.parametrize('mode', ('cycle', 'error'))
def test_tool_stops_when_first_page_contains_target(tmp_path, mode):
    args, log = connection(tmp_path, mode)
    instance = MCPTool(name='first', **args)
    run_discovery(instance.get_tool_info())
    assert instance.input_keys == ['value']
    assert cursors(log) == [None]


@pytest.mark.parametrize('mode', MODES)
@pytest.mark.parametrize('include', ([], ['target']))
def test_toolkit_registers_all_pages_before_applying_include(tmp_path, mode, include):
    args, log = connection(tmp_path, mode)
    instance = MCPToolkit(name='paged', server_name='fixture', include=include.copy(), **args)
    run_discovery(instance.get_all_tools())
    names = include or ['first', 'target', 'last']
    assert instance.tool_names == ['paged@' + name for name in names]
    for name in names:
        registered = ToolManager().get_instance_obj('paged@' + name, new_instance=False)
        assert registered is not None
        assert registered.origin_tool_name == name
        assert registered.server_name == 'fixture'
        assert registered.input_keys == ['value']
        assert registered.command == args['command'] and registered.args == args['args']
    if include:
        assert ToolManager().get_instance_obj('paged@first', new_instance=False) is None
    assert cursors(log) == expected_cursors(mode)


def test_missing_tool_searches_every_page_then_reports_name(tmp_path):
    args, log = connection(tmp_path, 'pages')
    instance = MCPTool(name='missing', server_name='fixture', **args)
    with pytest.raises(Exception, match='No tool named missing in mcp server fixture'):
        run_discovery(instance.get_tool_info())
    assert cursors(log) == expected_cursors('pages')


def error_leaves(error):
    children = getattr(error, 'exceptions', ())
    return [leaf for child in children for leaf in error_leaves(child)] if children else [error]


@pytest.mark.parametrize('mode,message', [('cycle', 'repeated pagination cursor'),
                                        ('error', 'fixture cursor expired')])
@pytest.mark.parametrize('kind', ('tool', 'toolkit'))
def test_pagination_errors_do_not_publish_partial_metadata(tmp_path, mode, message, kind):
    args, log = connection(tmp_path, mode)
    before = ToolManager()._instance_obj_map.copy()
    if kind == 'tool':
        instance = MCPTool(name='missing', description='original', **args)
        operation = instance.get_tool_info()
    else:
        instance = MCPToolkit(name='paged', include=['target'], **args)
        operation = instance.get_all_tools()
    with pytest.raises(Exception) as raised:
        run_discovery(operation)
    assert any(message in str(error) for error in error_leaves(raised.value))
    assert ToolManager()._instance_obj_map == before
    if kind == 'tool':
        assert instance.description == 'original'
    else:
        assert instance.include == ['target']
    assert cursors(log) == [None, 'opaque+/=1']


def test_empty_catalogue_registers_nothing(tmp_path):
    args, log = connection(tmp_path, 'empty')
    before = ToolManager()._instance_obj_map.copy()
    instance = MCPToolkit(name='empty', **args)
    run_discovery(instance.get_all_tools())
    assert instance.include == []
    assert ToolManager()._instance_obj_map == before
    assert cursors(log) == [None]
