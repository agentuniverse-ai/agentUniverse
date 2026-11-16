"""Configured Azure API versions must reach both SDK clients."""
import asyncio
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock, patch
import pytest
from agentuniverse.agent.action.knowledge.embedding.azureopenai_embedding import AzureOpenAIEmbedding
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

MODULE = 'agentuniverse.agent.action.knowledge.embedding.azureopenai_embedding'


@pytest.mark.parametrize('initial', [None, 'environment-version'])
def test_yaml_version_overrides_default_and_reaches_both_clients(tmp_path, initial):
    path = tmp_path / 'azure.yaml'
    path.write_text('''name: test
description: test configuration
embedding_model_name: deployment
azure_api_key: test-key
resource_name: sample-resource
azure_api_version: 2024-02-01
metadata:
  type: EMBEDDING
  module: agentuniverse.agent.action.knowledge.embedding.azureopenai_embedding
  class: AzureOpenAIEmbedding
'''.replace('azure_api_version: 2024-02-01', 'azure_api_version: "2024-02-01"'))
    config = ComponentConfiger().load_by_configer(Configer(str(path)).load())
    embedding = AzureOpenAIEmbedding(azure_api_version=initial)
    embedding.initialize_by_component_configer(config)
    sync, asynchronous = Mock(), Mock()
    response = SimpleNamespace(data=[SimpleNamespace(embedding=[1., 2.])])
    sync.embeddings.create.return_value = response
    asynchronous.embeddings.create = AsyncMock(return_value=response)
    with patch(MODULE + '.AzureOpenAI', return_value=sync) as sync_factory, \
         patch(MODULE + '.AsyncAzureOpenAI', return_value=asynchronous) as async_factory:
        assert embedding.get_embeddings(['hello']) == [[1., 2.]]
        assert asyncio.run(embedding.async_get_embeddings(['hello'])) == [[1., 2.]]
    assert embedding.azure_api_version == '2024-02-01'
    expected = dict(api_key='test-key', api_version='2024-02-01',
                    azure_endpoint='https://sample-resource.openai.azure.com')
    sync_factory.assert_called_once_with(**expected)
    async_factory.assert_called_once_with(**expected)


def test_absent_version_preserves_existing_default():
    embedding = AzureOpenAIEmbedding(azure_api_version='environment-version')
    embedding._initialize_by_component_configer(SimpleNamespace(name='test', description=''))
    assert embedding.azure_api_version == 'environment-version'
