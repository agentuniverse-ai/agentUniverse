# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/12/13 11:19
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: es_conversation_memory_storage.py
import json
import datetime

import httpx
from typing import Optional, List, Any
from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage import BaseMemoryConverter
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class ElasticsearchMemoryStorage(MemoryStorage):
    """ElasticsearchMemoryStorage class that stores messages via HTTP in an Elasticsearch index.

    Attributes:
        es_url (str): The base URL of the Elasticsearch server.
        index_name (str): The name of the Elasticsearch index to store messages.
        memory_converter (BaseMemoryConverter): The memory converter to use for the memory.
    """

    es_url: Optional[str] = "http://localhost:9200"  # The base URL of your Elasticsearch instance
    index_name: Optional[str] = "memory"
    memory_converter: BaseMemoryConverter = None
    user: Optional[str] = None
    password: Optional[str] = None
    timeout: Optional[int] = 60
    client: Optional[httpx.Client] = None

    model_config = {
        "arbitrary_types_allowed": True,  # Allow arbitrary types
    }

    def _new_client(self):
        """Initialize the Elasticsearch HTTP client (via requests)."""
        self.client = self._client()
        self._init_es_index()

    def _initialize_by_component_configer(
        self, memory_storage_config: ComponentConfiger
    ) -> "ElasticsearchMemoryStorage":
        """Initialize the ElasticsearchMemoryStorage by the ComponentConfiger object."""
        super()._initialize_by_component_configer(memory_storage_config)
        if getattr(memory_storage_config, "es_url", None):
            self.es_url = memory_storage_config.es_url
        if getattr(memory_storage_config, "es_index_name", None):
            self.index_name = memory_storage_config.es_index_name
        if getattr(memory_storage_config, "es_user", None):
            self.user = memory_storage_config.es_user
        if getattr(memory_storage_config, "es_password", None):
            self.password = memory_storage_config.es_password
        if getattr(memory_storage_config, "es_timeout", None):
            self.timeout = memory_storage_config.es_timeout
        if self.es_url is None:
            raise Exception("`es_url` is not set")
        # initialize the memory converter if not set
        if self.memory_converter is None:
            self.memory_converter = DefaultMemoryConverter(self.index_name)
        self._new_client()
        return self

    def _init_es_index(self):
        """Create the Elasticsearch index if it does not exist."""
        response = self.client.get(f"/{self.index_name}")
        if response.status_code == 404:  # Index does not exist, create it
            settings = {
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                "mappings": {
                    "properties": {
                        "session_id": {"type": "keyword"},
                        "content": {"type": "text"},
                        "trace_id": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "source_type": {"type": "keyword"},
                        "target": {"type": "keyword"},
                        "target_type": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "prefix": {"type": "text"},
                        "timestamp": {"type": "date"},
                        "params": {"type": "text"},
                        "pair_id": {"type": "keyword"},
                        "additional_args": {"type": "object"},
                    }
                },
            }
            response = self.client.put(f"/{self.index_name}", json=settings)
            if response.status_code != 200:
                raise Exception(f"Failed to create index: {response.text}")

    def delete(self, session_id: str = None, agent_id: str = None, trace_id: str = None, **kwargs) -> None:
        """Delete the memory from Elasticsearch.

        Args:
            session_id (str): The session id of the memory to delete.
            agent_id (str): The agent id of the memory to delete.
        """
        url = f"{self.es_url}/{self.index_name}/_delete_by_query"
        query = {"query": {"bool": {"must": []}}}

        if session_id:
            query["query"]["bool"]["must"].append({"term": {"session_id": session_id}})
        if agent_id:
            query["query"]["bool"]["must"].append(
                {"bool": {"should": [{"term": {"source": agent_id}}, {"term": {"target": agent_id}}]}}
            )
        if trace_id:
            query["query"]["bool"]["must"].append({"term": {"trace_id": trace_id}})
        response = self.client.post(url, json=query)
        if response.status_code != 200:
            raise Exception(f"Failed to delete documents: {response.text}")

    def add(
        self, message_list: List[ConversationMessage], session_id: str = None, agent_id: str = None, **kwargs
    ) -> None:
        """Add messages to the Elasticsearch index.

        Args:
            message_list (List[Message]): The list of messages to add.
            session_id (str): The session id of the memory to add.
            agent_id (str): The agent id of the memory to add.
        """
        message_list = ConversationMessage.check_and_convert_message(message_list, session_id)
        actions = []
        for message in message_list:
            action = self.memory_converter.to_es_action(message, session_id=session_id, agent_id=agent_id, **kwargs)
            actions.append(action)

        bulk_data = "\n".join(actions) + "\n"  # Elasticsearch bulk data format requires newlines between actions
        response = self.client.post(
            f"/{self.index_name}/_bulk", content=bulk_data, headers={"Content-Type": "application/x-ndjson"}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to add documents: {response.text}")

    def get(
        self, session_id: str = None, agent_id: str = None, top_k=50, trace_id: str = None, **kwargs
    ) -> List[ConversationMessage]:
        """Get messages from the Elasticsearch index.

        Args:
            session_id (str): The session id of the memory to get.
            agent_id (str): The agent id of the memory to get.
            top_k (int): The number of messages to get.

        Returns:
            List[Message]: The list of messages retrieved from Elasticsearch.
        """
        query = {
            "query": {"bool": {"must": []}},
            "size": top_k,
            "sort": [
                {"timestamp": {"order": "desc"}}  # Sorting by timestamp in ascending order
            ],
        }
        if session_id:
            query["query"]["bool"]["must"].append({"term": {"session_id": session_id}})
        if "type" in kwargs:
            if isinstance(kwargs["type"], list):
                memory_types = kwargs["type"]
            elif isinstance(kwargs["type"], str):
                memory_types = [kwargs["type"]]
            else:
                raise ValueError("type must be a list or a string")
            query["query"]["bool"]["must"].append({"terms": {"type": memory_types}})
        if agent_id:
            condition = {"bool": {"must": [{"match": {"target": agent_id}}, {"match": {"target_type": "agent"}}]}}
            if kwargs.get("memory_types") and len(kwargs["memory_types"]) > 0:
                types_condition = {
                    "bool": {
                        "must": [
                            {"match": {"source": agent_id}},
                            {"match": {"source_type": "agent"}},
                            {"terms": {"target_type": kwargs["memory_types"]}},
                        ]
                    }
                }
                query["query"]["bool"]["must"].append({"bool": {"should": [condition, types_condition]}})
            else:
                query["query"]["bool"]["must"].append(condition)

        if trace_id:
            query["query"]["bool"]["must"].append({"term": {"trace_id": trace_id}})
        response = self.client.post(f"/{self.index_name}/_search", json=query)
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve documents: {response.text}")

        hits = response.json()["hits"]["hits"]
        messages = []
        for hit in hits:
            messages.append(self.memory_converter.from_es_hit(hit))
        messages.reverse()
        return messages

    def _client(self):
        transport = httpx.HTTPTransport(retries=3)
        if self.user and self.password:
            return httpx.Client(
                base_url=self.es_url,
                transport=transport,
                timeout=self.timeout,
                auth=(self.user, self.password),
            )
        return httpx.Client(
            base_url=self.es_url,
            transport=transport,
            timeout=self.timeout,
        )


class DefaultMemoryConverter:
    """The default memory converter for ElasticsearchMemoryStorage."""

    def __init__(self, index_name: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.index_name = index_name

    def from_es_hit(self, es_hit: dict) -> Message:
        """Convert an Elasticsearch hit to a Message instance."""
        return ConversationMessage.from_dict(
            {
                "id": es_hit["_id"],
                "conversation_id": es_hit["_source"]["session_id"],
                "source": es_hit["_source"]["source"],
                "source_type": es_hit["_source"]["source_type"],
                "target": es_hit["_source"]["target"],
                "target_type": es_hit["_source"]["target_type"],
                "content": es_hit["_source"]["content"],
                "metadata": {
                    "prefix": es_hit["_source"].get("prefix"),
                    "timestamp": datetime.datetime.fromisoformat(es_hit["_source"]["timestamp"]),
                    "params": es_hit["_source"].get("params"),
                    "pair_id": es_hit["_source"].get("pair_id"),
                    "gmt_created": datetime.datetime.fromisoformat(es_hit["_source"]["timestamp"]).isoformat(),
                },
                "type": es_hit["_source"]["type"],
                "trace_id": es_hit["_source"]["trace_id"],
                "additional_args": es_hit["_source"].get("additional_args"),
            }
        )

    def to_es_action(self, message: ConversationMessage, session_id: str = None, agent_id: str = None, **kwargs) -> str:
        """Convert a message to an Elasticsearch action (index operation)."""
        document = {
            "session_id": session_id,
            "content": message.content,
            "trace_id": message.trace_id,
            "source": message.source,
            "source_type": message.source_type,
            "target": message.target,
            "target_type": message.target_type,
            "type": message.type,
            "prefix": message.metadata.get("prefix"),
            "timestamp": message.metadata.get("timestamp", datetime.datetime.now()).isoformat(),
            "params": message.metadata.get("params"),
            "pair_id": message.metadata.get("pair_id"),
            "additional_args": message.metadata.get("additional_args"),
        }
        index_info = {"index": {"_index": self.index_name, "_id": message.id}}
        return f"{json.dumps(index_info)}\n{json.dumps(document)}"  # Format for Elasticsearch bulk requests
