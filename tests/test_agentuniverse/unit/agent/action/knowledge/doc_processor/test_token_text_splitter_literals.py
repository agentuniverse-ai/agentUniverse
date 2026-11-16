"""Literal tokenizer spellings are document content, not control tokens."""
from pathlib import Path

import pytest
import tiktoken

from agentuniverse.agent.action.knowledge.doc_processor.token_text_splitter import TokenTextSplitter
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


@pytest.mark.parametrize('encoding,model,marker', [
    ('gpt2', None, '<|endoftext|>'),
    ('cl100k_base', None, '<|endoftext|>'),
    ('cl100k_base', None, '<|fim_prefix|>'),
    ('cl100k_base', None, '<|fim_middle|>'),
    ('cl100k_base', None, '<|fim_suffix|>'),
    ('cl100k_base', None, '<|endofprompt|>'),
    ('gpt2', 'gpt-4', '<|fim_prefix|>'),
])
@pytest.mark.parametrize('overlap', [0, 3])
def test_literal_markers_follow_ordinary_token_windows(encoding, model, marker, overlap):
    tokenizer = tiktoken.encoding_for_model(model) if model else tiktoken.get_encoding(encoding)
    text = f'Tokenizer documentation quotes {marker} as an example. ' * 5
    tokens = tokenizer.encode_ordinary(text)
    processor = TokenTextSplitter(encoding_name=encoding, model_name=model,
                                  chunk_size=13, chunk_overlap=overlap)
    result = processor.process_docs([Document(text=text, metadata={'source': 'tokenizer.md'})])
    # Assert actual text windows, not merely that processing avoids an exception.
    expected = []
    for start in range(0, len(tokens), 13 - overlap):
        expected.append(tokenizer.decode(tokens[start:start + 13]))
        if start + 13 >= len(tokens):
            break
    assert [doc.text for doc in result] == expected
    assert all(doc.metadata == {'source': 'tokenizer.md'} for doc in result)
    assert not (set(tokens) & set(tokenizer._special_tokens.values()))
    if overlap == 0:
        assert ''.join(doc.text for doc in result) == text


@pytest.mark.parametrize('text', ['', 'ordinary text without a marker'])
def test_ordinary_and_empty_documents_are_unchanged(text):
    result = TokenTextSplitter().process_docs([Document(text=text)])
    assert [doc.text for doc in result] == ([text] if text else [])


@pytest.mark.parametrize('operation', ['insert_knowledge', 'update_knowledge'])
def test_shipped_component_can_ingest_a_local_tokenizer_document(tmp_path, monkeypatch, operation):
    import agentuniverse.agent.action.knowledge.doc_processor.token_text_splitter as module

    class RecordingStore(Store):
        received: list = []

        def insert_document(self, documents, **kwargs):
            self.received.extend(documents)

        def update_document(self, documents, **kwargs):
            self.received.extend(documents)

    config = Configer().load_by_path(str(Path(module.__file__).with_suffix('.yaml')))
    processor = TokenTextSplitter().initialize_by_component_configer(ComponentConfiger(config).load())
    application = AppConfiger()
    monkeypatch.setattr(ApplicationConfigManager(), '_ApplicationConfigManager__app_configer', application)
    appname = application.base_info_appname
    store = RecordingStore()
    monkeypatch.setattr(DocProcessorManager(), '_instance_obj_map',
                        {f'{appname}.doc_processor.token_text_splitter': processor})
    monkeypatch.setattr(StoreManager(), '_instance_obj_map', {f'{appname}.store.recording': store})
    monkeypatch.setattr(ReaderManager(), '_instance_obj_map', {f'{appname}.reader.local_text': TxtReader()})
    path = tmp_path / 'tokenizer.txt'
    text = 'The literal marker <|endoftext|> appears in exported training examples.'
    path.write_text(text, encoding='utf-8')
    knowledge = Knowledge(stores=['recording'], readers={'txt': 'local_text'}, insert_processors=['token_text_splitter'],
                          update_processors=['token_text_splitter'])
    try:
        getattr(knowledge, operation)(source_path=str(path))
    finally:
        knowledge.insert_executor.shutdown(wait=True)
        knowledge.query_executor.shutdown(wait=True)
    assert [doc.text for doc in store.received] == [text]
