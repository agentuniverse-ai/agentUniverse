# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/22
# @Author  : Anush008
# @Email   : anushshetty90@gmail.com
# @FileName: qdrant_memory_storage.py

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, ClassVar
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    NamedVector,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


DEFAULT_CONNECTION_ARGS: Dict[str, Any] = {
    "host": "localhost",
    "port": 6333,
    "https": False,
}


class QdrantMemoryStorage(MemoryStorage):
    """Qdrant-based memory storage.

    Stores chat messages as Qdrant points with a named vector and rich payload.

    Attributes:
        connection_args (Optional[dict]): Qdrant connection parameters. Supports either `url` or `host`/`port`.
        collection_name (Optional[str]): Qdrant collection name.
        distance (Optional[str]): Distance metric, one of "COSINE", "EUCLID", "DOT".
        embedding_model (Optional[str]): Embedding model instance key managed by `EmbeddingManager`.
    """

    class Config:
        arbitrary_types_allowed = True

    connection_args: Optional[dict] = None
    collection_name: Optional[str] = "memory"
    distance: Optional[str] = "COSINE"
    embedding_model: Optional[str] = None

    client: Optional[QdrantClient] = None

    VECTOR_NAME: ClassVar[str] = "embedding"

    def _initialize_by_component_configer(self, memory_storage_config: ComponentConfiger) -> "QdrantMemoryStorage":
        super()._initialize_by_component_configer(memory_storage_config)
        if getattr(memory_storage_config, "connection_args", None):
            self.connection_args = memory_storage_config.connection_args
        else:
            self.connection_args = DEFAULT_CONNECTION_ARGS
        if getattr(memory_storage_config, "collection_name", None):
            self.collection_name = memory_storage_config.collection_name
        if getattr(memory_storage_config, "distance", None):
            self.distance = memory_storage_config.distance
        if getattr(memory_storage_config, "embedding_model", None):
            self.embedding_model = memory_storage_config.embedding_model
        return self

    def _metric_from_str(self) -> Distance:
        return {
            "COSINE": Distance.COSINE,
            "EUCLID": Distance.EUCLID,
            "DOT": Distance.DOT,
            "MANHATTAN": Distance.MANHATTAN,
        }.get((self.distance or "COSINE").upper(), Distance.COSINE)

    def _ensure_client(self) -> QdrantClient:
        if self.client is not None:
            return self.client
        args = self.connection_args or DEFAULT_CONNECTION_ARGS
        self.client = QdrantClient(**args)
        return self.client

    def _ensure_collection(self, dim: int) -> None:
        client = self._ensure_client()
        if not client.collection_exists(self.collection_name):
            metric = self._metric_from_str()
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config={self.VECTOR_NAME: VectorParams(size=dim, distance=metric)},
            )

    @staticmethod
    def _build_filter(
        session_id: Optional[str], agent_id: Optional[str], source: Optional[str], type_value: Optional[Any]
    ) -> Optional[Filter]:
        must_conditions: List[Any] = []
        if session_id:
            must_conditions.append(FieldCondition(key="session_id", match=MatchValue(value=session_id)))
        if agent_id:
            must_conditions.append(FieldCondition(key="agent_id", match=MatchValue(value=agent_id)))
        if source:
            must_conditions.append(FieldCondition(key="source", match=MatchValue(value=source)))
        if type_value:
            must_conditions.append(FieldCondition(key="type", match=MatchValue(value=type_value[0])))
        if not must_conditions:
            return None
        return Filter(must=must_conditions)

    def delete(self, session_id: str = None, agent_id: str = None, **kwargs) -> None:
        client = self._ensure_client()
        filt = self._build_filter(session_id=session_id, agent_id=agent_id, source=None, type_value=kwargs.get("type"))
        if not filt:
            return
        client.delete(collection_name=self.collection_name, points_selector=filt)

    def add(self, message_list: List[Message], session_id: str = None, agent_id: str = None, **kwargs) -> None:
        if not message_list:
            return
        client = self._ensure_client()

        points: List[PointStruct] = []
        for message in message_list:
            metadata = dict(message.metadata or {})
            metadata.update({"gmt_created": datetime.now().isoformat()})
            if session_id:
                metadata["session_id"] = session_id
            if agent_id:
                metadata["agent_id"] = agent_id
            if message.source:
                metadata["source"] = message.source
            if message.type:
                metadata["type"] = message.type

            vector: List[float] = []
            if self.embedding_model:
                try:
                    vector = (
                        EmbeddingManager().get_instance_obj(self.embedding_model).get_embeddings([str(message.content)])
                    )[0]
                except Exception:
                    vector = []

            if vector:
                self._ensure_collection(dim=len(vector))
            else:
                raise ValueError("No vectors available for message. Cannot store message without embeddings.")

            payload = {
                "content": message.content,
                **metadata,
            }

            try:
                point_id = str(uuid.UUID(str(message.id))) if message.id else str(uuid.uuid4())
            except Exception:
                point_id = str(uuid.uuid4())

            points.append(
                PointStruct(
                    id=point_id,
                    vector={self.VECTOR_NAME: vector} if vector else {},
                    payload=payload,
                )
            )

        if points:
            client.upsert(collection_name=self.collection_name, points=points)

    def get(
        self, session_id: str = None, agent_id: str = None, top_k=10, input: str = "", source: str = None, **kwargs
    ) -> List[Message]:
        client = self._ensure_client()
        filt = self._build_filter(
            session_id=session_id, agent_id=agent_id, source=source, type_value=kwargs.get("type")
        )

        if input:
            vector: List[float] = []
            if self.embedding_model:
                try:
                    vector = (EmbeddingManager().get_instance_obj(self.embedding_model).get_embeddings([input]))[0]
                except Exception:
                    vector = []
            if vector:
                results = client.query_points(
                    collection_name=self.collection_name,
                    query=vector,
                    using=self.VECTOR_NAME,
                    limit=top_k,
                    with_payload=True,
                    with_vectors=False,
                    query_filter=filt,
                )
                messages = self.to_messages(results)
                messages.reverse()
                return messages
            else:
                return []

        scroll_result = client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filt,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
        points = scroll_result[0]
        messages = self.to_messages(points)
        messages = sorted(messages, key=lambda msg: (msg.metadata or {}).get("gmt_created", ""))
        messages.reverse()
        return messages[:top_k]

    def to_messages(self, results: Any) -> List[Message]:
        message_list: List[Message] = []
        if not results:
            return message_list
        try:
            for item in results:
                payload: Dict[str, Any] = getattr(item, "payload", None) or {}
                msg = Message(
                    id=str(getattr(item, "id", None)),
                    content=payload.get("content"),
                    metadata={k: v for k, v in payload.items() if k not in {"content"}},
                    source=payload.get("source"),
                    type=payload.get("type", ""),
                )
                message_list.append(msg)
        except Exception as e:
            print("QdrantMemoryStorage.to_messages failed, exception= " + str(e))
        return message_list
