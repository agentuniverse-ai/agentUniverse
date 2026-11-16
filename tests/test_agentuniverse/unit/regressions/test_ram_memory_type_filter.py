"""RAM summary reads must not substitute ordinary conversation messages."""
from types import SimpleNamespace

import pytest

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.memory_storage.memory_storage_manager import MemoryStorageManager
from agentuniverse.agent.memory.memory_storage.ram_memory_storage import RamMemoryStorage
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.configer import Configer


@pytest.fixture
def store(monkeypatch):
    config = Configer()
    config.value = {'BASE_INFO': {'appname': 'ram_type_filter'}}
    monkeypatch.setattr(ApplicationConfigManager(), '_ApplicationConfigManager__app_configer',
                        AppConfiger().load_by_configer(config))
    instance = RamMemoryStorage(name='typed_history', messages={})
    manager = MemoryStorageManager()
    code = instance.get_instance_code()
    manager.register(code, instance)
    try:
        yield instance
    finally:
        manager.unregister(code)


@pytest.mark.parametrize('kind,limit,expected', [
    ('summarize', 1, ['new summary']),
    ('summarize', 2, ['old summary', 'new summary']),
    (['human', 'ai'], 2, ['question', 'answer']),
    ([], 10, []), ('missing', 10, []),
    (None, 2, ['new summary', 'answer']),
])
def test_type_filter_precedes_recent_window(store, kind, limit, expected):
    messages = [Message(type=kind, content=text) for kind, text in [
        ('summarize', 'old summary'), ('human', 'question'),
        ('summarize', 'new summary'), ('ai', 'answer')]]
    store.add(messages, session_id='session', agent_id='agent')
    store.add([Message(type='summarize', content='other session')], session_id='other', agent_id='agent')
    store.add([Message(type='summarize', content='other agent')], session_id='session', agent_id='other')
    before = [message.model_dump() for message in messages]
    result = store.get('session', 'agent', top_k=limit, type=kind)
    assert [message.content for message in result] == expected
    assert [message.model_dump() for message in messages] == before
    assert store.get('missing', 'agent', type=kind) == []


@pytest.mark.parametrize('has_summary', [True, False])
def test_memory_summarizer_receives_only_previous_summary(store, monkeypatch, has_summary):
    messages = [Message(type='summarize', content='previous summary')] if has_summary else []
    messages += [Message(type='ai', content=f'ordinary reply {i}') for i in range(12)]
    store.add(messages, session_id='session', agent_id='agent')
    calls = []

    def run(**kwargs):
        calls.append(kwargs)
        return OutputObject({'output': 'updated summary'})

    monkeypatch.setattr(AgentManager(), 'get_instance_obj', lambda name: SimpleNamespace(run=run))
    memory = Memory(memory_retrieval_storage=store.name)
    assert memory.summarize_memory(session_id='session', agent_id='agent') == 'updated summary'
    assert calls[0]['summarize_content'] == ('previous summary' if has_summary else '')
    assert 'ordinary reply 11' in calls[0]['input']
