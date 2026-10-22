# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/10 19:10
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: chroma_memory_storage.py
import uuid
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional, List, Any

import chromadb
from pydantic import SkipValidation
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class ChromaMemoryStorage(MemoryStorage):
    """The chroma memory storage class.

    Attributes:
        collection_name (str): The name of the ChromaDB collection.
        persist_path (str): The path to persist the collection.
        embedding_model (str): The name of the embedding model instance to use.
        _collection (Collection): The collection object.
    """
    collection_name: Optional[str] = 'memory'
    persist_path: Optional[str] = None
    embedding_model: Optional[str] = None
    _collection: SkipValidation[Collection] = None

    def _initialize_by_component_configer(self,
                                          memory_storage_config: ComponentConfiger) -> 'ChromaMemoryStorage':
        """Initialize the ChromaMemoryStorage by the ComponentConfiger object.

        Args:
            memory_storage_config(ComponentConfiger): A configer contains chroma_memory_storage basic info.
        Returns:
            ChromaMemoryStorage: A ChromaMemoryStorage instance.
        """
        super()._initialize_by_component_configer(memory_storage_config)
        if getattr(memory_storage_config, 'collection_name', None):
            self.collection_name = memory_storage_config.collection_name
        if getattr(memory_storage_config, 'persist_path', None):
            self.persist_path = memory_storage_config.persist_path
        if getattr(memory_storage_config, 'embedding_model', None):
            self.embedding_model = memory_storage_config.embedding_model
        return self

    def _init_collection(self) -> Any:
        """Initialize the ChromaDB collection."""
        if self.persist_path.startswith('http') or self.persist_path.startswith('https'):
            parsed_url = urlparse(self.persist_path)
            settings = Settings(
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_server_host=parsed_url.hostname,
                chroma_server_http_port=str(parsed_url.port)
            )
        else:
            settings = Settings(
                is_persistent=True,
                persist_directory=self.persist_path
            )
        client = chromadb.Client(settings)
        self._collection = client.get_or_create_collection(name=self.collection_name)
        return client

    def delete(self, session_id: str = None, agent_id: str = None, **kwargs) -> None:
        """Delete the memory from the database.

        Args:
            session_id (str): The session id of the memory to delete.
            agent_id (str): The agent id of the memory to delete.
        """
        if self._collection is None:
            self._init_collection()
        filters = {}
        if session_id is None and agent_id is None:
            return
        if session_id is not None:
            filters['session_id'] = session_id
        if agent_id is not None:
            filters['agent_id'] = agent_id
        self._collection.delete(where=filters)

    def add(self, message_list: List[Message], session_id: str = None, agent_id: str = None, **kwargs) -> None:
        """Add messages to the memory db.

        Args:
            message_list (List[Message]): The list of messages to add.
            session_id (str): The session id of the memory to add.
            agent_id (str): The agent id of the memory to add.
        """
        if self._collection is None:
            self._init_collection()
        if not message_list:
            return
        metadata = {'gmt_created': datetime.now().isoformat()}
        if session_id:
            metadata['session_id'] = session_id
        if agent_id:
            metadata['agent_id'] = agent_id
        for message in message_list:
            embedding = []
            if self.embedding_model:
                embedding = EmbeddingManager().get_instance_obj(
                    self.embedding_model
                ).get_embeddings([message.content])[0]
            if message.source:
                metadata['source'] = message.source
            metadata['type'] = message.type if message.type else ''
            self._collection.add(
                ids=[message.id if message.id else str(uuid.uuid4())],
                documents=[message.content],
                metadatas=[metadata],
                embeddings=[embedding] if len(embedding) > 0 else None,
            )

    def get(self, session_id: str = None, agent_id: str = None, top_k=10, input: str = '', source: str = None,
            **kwargs) -> \
            List[Message]:
        """Get messages from the memory db.

        Args:
            session_id (str): The session id of the memory to get.
            agent_id (str): The agent id of the memory to get.
            top_k (int): The number of messages to return.
            input (str): The input text to search for in the memory.
            source (str): The source of the message to get.
        Returns:
            List[Message]: A list of messages retrieved from the memory db.
        """
        if self._collection is None:
            self._init_collection()
        filters = {"$and": []}
        if session_id:
            filters["$and"].append({'session_id': session_id})
        if agent_id:
            filters["$and"].append({'agent_id': agent_id})
        if source:
            filters["$and"].append({'source': source})
        if kwargs.get('type'):
            if isinstance(kwargs.get('type'), list):
                types = kwargs.get('type')
            elif isinstance(kwargs.get('type'), str):
                types = [kwargs.get('type')]
            filters["$and"].append({'type': {'$in': types}})
        if len(filters["$and"]) < 2:
            filters = filters["$and"][0] if len(filters["$and"]) == 1 else {}
        if input:
            embedding = []
            if self.embedding_model:
                embedding = EmbeddingManager().get_instance_obj(
                    self.embedding_model
                ).get_embeddings([input])[0]
            if len(embedding) > 0:
                results = self._collection.query(
                    query_embeddings=embedding, where=filters, n_results=top_k
                )
            else:
                results = self._collection.query(query_texts=[input], where=filters, n_results=top_k)
            messages = self.to_messages(result=results)
            messages.reverse()
            return messages
        else:
            results = self._collection.get(where=filters)
            messages = self.to_messages(result=results, sort_by_time=True)
            messages.reverse()
            return messages[-top_k:]

    def to_messages(self, result: dict, sort_by_time: bool = False) -> List[Message]:
        """Convert the result from ChromaDB to a list of aU messages.

        Args:
            result (dict): The result from ChromaDB.
            sort_by_time (bool): Whether to sort the messages by time.
        Returns:
            List[Message]: A list of aU messages.
        """
        message_list = []
        if not result or not result['ids']:
            return message_list
        try:
            if self.is_nested_list(result['ids']):
                metadatas = result.get('metadatas', [[]])
                documents = result.get('documents', [[]])
                ids = result.get('ids', [[]])
                message_list = [
                    Message(
                        id=ids[0][i],
                        content=documents[0][i],
                        metadata=metadatas[0][i] if metadatas[0] else None,
                        source=metadatas[0][i].get('source', None) if metadatas[0] else None,
                        type=metadatas[0][i].get('type', '') if metadatas[0] else ''
                    )
                    for i in range(len(result['ids'][0]))
                ]
            else:
                metadatas = result.get('metadatas', [])
                documents = result.get('documents', [])
                ids = result.get('ids', [])
                message_list = [
                    Message(
                        id=ids[i],
                        content=documents[i],
                        metadata=metadatas[i] if metadatas[i] else None,
                        source=metadatas[i].get('source', None) if metadatas[i] else None,
                        type=metadatas[i].get('type', '') if metadatas[i] else ''
                    )
                    for i in range(len(result['ids']))
                ]
            if sort_by_time:
                # order by gmt_created asc
                message_list = sorted(
                    message_list,
                    key=lambda msg: msg.metadata.get('gmt_created', ''),
                )
        except Exception as e:
            print('ChromaMemory.to_messages failed, exception= ' + str(e))
        return message_list

    @staticmethod
    def is_nested_list(variable: List) -> bool:
        return isinstance(variable, list) and len(variable) > 0 and isinstance(variable[0], list)
