#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 12:55
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: chroma_long_term_memory_storage.py

import uuid
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional, List, Any

import chromadb
from pydantic import SkipValidation
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.memory.memory_extract.memory_extract import LongTermMemoryMessage, MemoryCategoryEnum, \
    MemoryOwnerEnum
from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.logging.logging_util import LOGGER


class ChromaLongTermMemoryStorage(MemoryStorage):
    """ChromaDB-based long-term memory storage implementation.

    Attributes:
        collection_name (Optional[str]): The name of the ChromaDB collection.
        persist_path (Optional[str]): The path to persist the collection.
        embedding_model (Optional[str]): The name of the embedding model instance to use.
        _collection (SkipValidation[Collection]): The collection object.
    """
    collection_name: Optional[str] = 'long_term_memory'
    persist_path: Optional[str] = None
    embedding_model: Optional[str] = None
    _collection: SkipValidation[Collection] = None

    def _initialize_by_component_configer(self,
                                          memory_storage_config: ComponentConfiger) -> 'ChromaLongTermMemoryStorage':
        """Initialize the ChromaLongTermMemoryStorage by the ComponentConfiger object.

        Args:
            memory_storage_config (ComponentConfiger): A configer contains chroma_memory_storage basic info.
            
        Returns:
            ChromaLongTermMemoryStorage: A ChromaLongTermMemoryStorage instance.
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
        """Initialize the ChromaDB collection.
        
        Returns:
            Any: The ChromaDB client instance.
        """
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

    def delete(self, session_id: str = None, agent_id: str = None, user_id: str = None, **kwargs) -> None:
        """Delete memories from the database.

        Args:
            session_id (str, optional): The session id of the memory to delete.
            agent_id (str, optional): The agent id of the memory to delete.
            user_id (str, optional): The user id of the memory to delete.
            **kwargs: Additional parameters including:
                ids (List[str]): The list of memory ids to delete.
        """
        if self._collection is None:
            self._init_collection()
            
        # Support deletion by IDs
        if 'ids' in kwargs and kwargs['ids']:
            self._collection.delete(ids=kwargs['ids'])
            return
            
        filters = {}
        if session_id is None and agent_id is None and user_id is None:
            return
        if session_id is not None:
            filters['session_id'] = session_id
        if agent_id is not None:
            filters['agent_id'] = agent_id
        if user_id is not None:
            filters['user_id'] = user_id
        self._collection.delete(where=filters)

    def add(self, message_list: List[LongTermMemoryMessage], session_id: str = None, agent_id: str = None, **kwargs) -> None:
        """Batch add messages to the memory database.

        Args:
            message_list (List[LongTermMemoryMessage]): The list of messages to add.
            session_id (str, optional): The session ID.
            agent_id (str, optional): The agent ID.
            **kwargs: Additional parameters.
        """
        if self._collection is None:
            self._init_collection()
        if not message_list:
            return
        
        # Generate embeddings for all messages
        embeddings = self._generate_embeddings_for_messages(message_list)
        
        # Prepare batch data
        ids, documents, metadatas  = self._prepare_batch_data(message_list, session_id, agent_id)
        
        # Execute batch addition
        self._execute_batch_addition(ids, documents, metadatas, embeddings)

    def _generate_embeddings_for_messages(self, message_list: List[LongTermMemoryMessage]) -> List[List[float]]:
        """Generate embeddings for messages.
        
        Args:
            message_list (List[LongTermMemoryMessage]): List of messages to process.
            
        Returns:
            List[List[float]]: List of embeddings for each message.
        """
        embeddings = []
        
        if not self.embedding_model:
            # Return empty embeddings for all messages if no embedding model
            return None
            
        # Collect texts that need embedding generation
        texts_to_embed = []
        
        for message in message_list:
            # Always generate embeddings for all messages
            texts_to_embed.append(message.content)
        
        # Batch generate embeddings
        if texts_to_embed:
            try:
                embedding_instance = EmbeddingManager().get_instance_obj(self.embedding_model)
                batch_embeddings = embedding_instance.get_embeddings(texts_to_embed, text_type="document")
                
                # Return the generated embeddings
                return batch_embeddings if batch_embeddings else [[] for _ in message_list]
                
            except Exception as e:
                LOGGER.warn(f"Batch embedding generation failed: {e}")
                return None
        
        return None

    def _prepare_batch_data(self, message_list: List[LongTermMemoryMessage], 
                           session_id: str = None, agent_id: str = None) -> tuple:
        """Prepare batch data for ChromaDB addition.
        
        Args:
            message_list (List[LongTermMemoryMessage]): List of messages to add.
            session_id (str, optional): Session ID.
            agent_id (str, optional): Agent ID.
            
        Returns:
            tuple: Tuple of (ids, documents, metadatas).
        """
        ids = []
        documents = []
        metadatas = []
        
        for message in message_list:
            # Generate ID
            message_id = message.id if message.id else str(uuid.uuid4())
            ids.append(message_id)
            
            # Document content
            documents.append(message.content)
            
            # Metadata
            metadata = self._build_metadata(message, session_id, agent_id)
            metadatas.append(metadata)
        
        return ids, documents, metadatas

    def _build_metadata(self, message: LongTermMemoryMessage, 
                       session_id: str = None, agent_id: str = None) -> dict:
        """Build metadata dictionary for a message.
        
        Args:
            message (LongTermMemoryMessage): The message to build metadata for.
            session_id (str, optional): Session ID.
            agent_id (str, optional): Agent ID.
            
        Returns:
            dict: Metadata dictionary.
        """
        if message.update:
            update_metadata =  {
                'timestamp': datetime.now().isoformat(),
                'category': message.category if message.category else None,
                'related_role': message.related_role if message.related_role else None,
                'user_id': message.user_id or None,
                'agent_id': message.agent_id or agent_id or None,
                'session_id': message.session_id or session_id or None,
                'confidence': message.confidence or None,
                'tags': ",".join(message.tags) if message.tags else None,
                'created_at': message.created_at.isoformat() if message.created_at else None,
                'updated_at':datetime.now().isoformat()
            }
            for key, value in update_metadata.items():
                if value is None:
                    del update_metadata[key]
            return update_metadata
        else:
            return {
                'timestamp': datetime.now().isoformat(),
                'category': message.category if message.category else MemoryCategoryEnum.DEFAULT.name,
                'related_role': message.related_role if message.related_role else MemoryOwnerEnum.DEFAULT.name,
                'user_id': message.user_id or '',
                'agent_id': message.agent_id or agent_id or '',
                'session_id': message.session_id or session_id or '',
                'confidence': message.confidence,
                'tags': ",".join(message.tags) if message.tags else "",
                'created_at': message.created_at.isoformat() if message.created_at else datetime.now().isoformat(),
                'updated_at': message.updated_at.isoformat() if message.updated_at else datetime.now().isoformat()
            }



    def _execute_batch_addition(self, ids: List[str], documents: List[str], 
                               metadatas: List[dict], embeddings: List[List[float]]) -> None:
        """Execute batch addition to ChromaDB.
        
        Args:
            ids (List[str]): List of IDs.
            documents (List[str]): List of documents.
            metadatas (List[dict]): List of metadata.
            embeddings (List[List[float]]): List of embeddings (can be empty, ChromaDB will auto-generate).
        """
        try:
            # ChromaDB can handle empty embeddings by auto-generating them
            # We pass embeddings regardless of whether they're empty or not
            self._collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings if embeddings else None,  # Pass None if empty list
            )
            
            LOGGER.info(f"Successfully batch added {len(ids)} memories")
            
        except Exception as e:
            LOGGER.error(f"Batch memory addition failed: {e}")
            self._fallback_to_single_addition(ids, documents, metadatas, embeddings)

    def _fallback_to_single_addition(self, ids: List[str], documents: List[str], 
                                    metadatas: List[dict], embeddings: List[List[float]]) -> None:
        """Fallback to single addition when batch addition fails.
        
        Args:
            ids (List[str]): List of IDs.
            documents (List[str]): List of documents.
            metadatas (List[dict]): List of metadata.
            embeddings (List[List[float]]): List of embeddings (can be empty).
        """
        LOGGER.info("Attempting to add memories one by one...")
        success_count = 0
        
        for i in range(len(ids)):
            try:
                # ChromaDB handles empty embeddings automatically
                embedding_to_use = embeddings[i] if i < len(embeddings) else None
                self._collection.upsert(
                    ids=[ids[i]],
                    documents=[documents[i]],
                    metadatas=[metadatas[i]],
                    embeddings=[embedding_to_use] if embedding_to_use else None,
                )
                success_count += 1
            except Exception as single_error:
                LOGGER.error(f"Failed to add single memory (ID: {ids[i]}): {single_error}")
        
        LOGGER.info(f"One-by-one addition completed, {success_count}/{len(ids)} successful")

    def to_messages(self, result: dict, sort_by_time: bool = False) -> List[LongTermMemoryMessage]:
        """Convert the result from ChromaDB to a list of LongTermMemoryMessage.

        Args:
            result (dict): The result from ChromaDB.
            sort_by_time (bool, optional): Whether to sort the messages by time.
            
        Returns:
            List[LongTermMemoryMessage]: A list of LongTermMemoryMessage.
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
                    LongTermMemoryMessage(
                        id=ids[0][i],
                        content=documents[0][i],
                        metadata=metadatas[0][i],
                        category=MemoryCategoryEnum(metadatas[0][i].get('category', MemoryCategoryEnum.DEFAULT.name)) if metadatas[0] else MemoryCategoryEnum.DEFAULT,
                        related_role=MemoryOwnerEnum(metadatas[0][i].get('related_role', MemoryOwnerEnum.DEFAULT.name)) if metadatas[0] else MemoryOwnerEnum.DEFAULT,
                        user_id=metadatas[0][i].get('user_id', None) if metadatas[0] else None,
                        agent_id=metadatas[0][i].get('agent_id', None) if metadatas[0] else None,
                        session_id=metadatas[0][i].get('session_id', None) if metadatas[0] else None,
                        tags=self._parse_tags_from_string(metadatas[0][i].get('tags', '')) if metadatas[0] else [],
                        created_at=datetime.fromisoformat(metadatas[0][i].get('created_at', datetime.now().isoformat())) if metadatas[0] else datetime.now(),
                        updated_at=datetime.fromisoformat(metadatas[0][i].get('updated_at', datetime.now().isoformat())) if metadatas[0] else datetime.now(),
                        confidence=metadatas[0][i].get('confidence', 1.0) if metadatas[0] else 1.0
                    )
                    for i in range(len(result['ids'][0]))
                ]
            else:
                metadatas = result.get('metadatas', [])
                documents = result.get('documents', [])
                ids = result.get('ids', [])
                message_list = [
                    LongTermMemoryMessage(
                        id=ids[i],
                        content=documents[i],
                        metadata=metadatas[i],
                        category=MemoryCategoryEnum(metadatas[i].get('category', MemoryCategoryEnum.DEFAULT.name)) if metadatas[i] else MemoryCategoryEnum.DEFAULT,
                        related_role=MemoryOwnerEnum(metadatas[i].get('related_role', MemoryOwnerEnum.DEFAULT.name)) if metadatas[i] else MemoryOwnerEnum.DEFAULT,
                        user_id=metadatas[i].get('user_id', None) if metadatas[i] else None,
                        agent_id=metadatas[i].get('agent_id', None) if metadatas[i] else None,
                        session_id=metadatas[i].get('session_id', None) if metadatas[i] else None,
                        tags=self._parse_tags_from_string(metadatas[i].get('tags', '')) if metadatas[i] else [],
                        created_at=datetime.fromisoformat(metadatas[i].get('created_at', datetime.now().isoformat())) if metadatas[i] else datetime.now(),
                        updated_at=datetime.fromisoformat(metadatas[i].get('updated_at', datetime.now().isoformat())) if metadatas[i] else datetime.now(),
                        confidence=metadatas[i].get('confidence', 1.0) if metadatas[i] else 1.0,
                    )
                    for i in range(len(result['ids']))
                ]
            if sort_by_time:
                # Order by timestamp ascending
                message_list = sorted(
                    message_list,
                    key=lambda msg: msg.created_at,
                )
        except Exception as e:
            LOGGER.error('ChromaMemory.to_messages failed, exception= ' + str(e))
        return message_list


    def _get_embedding(self, text: str, text_type: str = "document") -> List[float]:
        """Get embedding for a text using the configured embedding model.

        Args:
            text (str): The text to embed.
            text_type (str, optional): Type of text ("document" or "query").

        Returns:
            List[float]: The embedding vector.
            
        Raises:
            ValueError: If no embedding model is configured.
        """
        if not self.embedding_model:
            raise ValueError("No embedding model configured. Please specify an embedding_model.")

        try:
            embedding_instance = EmbeddingManager().get_instance_obj(self.embedding_model)
            embeddings = embedding_instance.get_embeddings([text], text_type=text_type)
            return embeddings[0] if embeddings else []
        except Exception as e:
            # For testing purposes, if embedding manager fails, return empty list
            LOGGER.error(f"Failed to get embeddings: {e}")
            return []


    def get(self, session_id: str = None, agent_id: str = None, top_k: int = 10, 
            query: str = None, user_id: str = None, tags: List[str] = None, 
            time_range: tuple = None, **kwargs) -> List[LongTermMemoryMessage]:
        """Get messages from the memory database (compatible with base class interface).
        
        Args:
            session_id (str, optional): The session ID.
            agent_id (str, optional): The agent ID.
            top_k (int, optional): The number of messages to return.
            query (str, optional): Query text for similarity search.
            user_id (str, optional): User ID for filtering.
            tags (List[str], optional): List of tags for filtering.
            time_range (tuple, optional): Time range tuple (start_time, end_time).
            **kwargs: Additional parameters passed to search method.
            
        Returns:
            List[LongTermMemoryMessage]: List of memory messages.
        """
        # Pass all parameters explicitly to the search method
        return self.search(
            query=query,
            top_k=top_k,
            session_id=session_id,
            agent_id=agent_id,
            user_id=user_id,
            tags=tags,
            time_range=time_range,
            **kwargs
        )
    
    def search(self, query: str = None, top_k: int = 10, session_id: str = None, agent_id: str = None, 
               user_id: str = None, tags: List[str] = None, time_range: tuple = None, 
               **kwargs) -> List[LongTermMemoryMessage]:
        """Advanced search method for long-term memory with extended parameters.
        
        Args:
            query (str, optional): Query text for similarity search.
            top_k (int, optional): Return top k most similar results (only for similarity search).
            session_id (str, optional): Session ID.
            agent_id (str, optional): Agent ID.
            user_id (str, optional): User ID.
            tags (List[str], optional): List of tags for filtering.
            time_range (tuple, optional): Time range tuple (start_time, end_time).
            **kwargs: Other filter conditions.
            
        Returns:
            List[LongTermMemoryMessage]: List of search result memories.
            
        Raises:
            ValueError: Raised when both query and all condition parameters are empty.
        """
        # Validation: cannot be empty simultaneously
        has_query = query is not None and query.strip() != ""
        has_conditions = any([
            agent_id is not None and agent_id.strip() != "",
            user_id is not None and user_id.strip() != "",
            tags is not None and len(tags) > 0,
            time_range is not None,
            any(kwargs.values())
        ])
        
        if not has_query and not has_conditions:
            raise ValueError("Search parameters cannot be empty simultaneously. Please provide query text or at least one search condition (agent_id, user_id, tags, time_range, etc.)")
        
        if self._collection is None:
            self._init_collection()
            
        # Build filter conditions
        filters = {"$and": []}
        
        # Build conditional filters
        if agent_id:
            filters["$and"].append({'agent_id': agent_id})

        if session_id:
            filters["$and"].append({'session_id': session_id})
            
        if user_id:
            filters["$and"].append({'user_id': user_id})
            
        if tags:
            # Search for memories containing any of the tags
            tag_filters = []
            for tag in tags:
                # Use string matching instead of list contains
                tag_filters.append({'tags': {'$like': f'%{tag}%'}})
            if tag_filters:
                filters["$and"].append({'$or': tag_filters})
        if time_range:
            start_time, end_time = time_range
            if start_time:
                filters["$and"].append({'created_at': {'$gte': start_time}})
            if end_time:
                filters["$and"].append({'created_at': {'$lte': end_time}})
                
        # Handle other filter conditions
        for key, value in kwargs.items():
            if key in ['category']:
                filters["$and"].append({key: value})
                
        # Simplify filters
        if len(filters["$and"]) == 1:
            filters = filters["$and"][0]
        elif not filters["$and"]:
            filters = {}

        return self._query_memories(filters, query, top_k)

    def _query_memories(self, filters: dict, query: str, top_k: int) -> List[LongTermMemoryMessage]:
        """Execute memory query with filters and optional query text.
        
        Args:
            filters (dict): Filter conditions for the query
            query (str): Query text for similarity search
            top_k (int): Number of results to return
            
        Returns:
            List[LongTermMemoryMessage]: List of memory messages
        """
        try:
            if query:
                # When query text is provided, use query method for vector search (supports conditional filtering)
                embedding = self._get_embedding(query, text_type="query")
                if len(embedding) > 0:
                    results = self._collection.query(
                        query_embeddings=embedding,
                        where=filters,
                        n_results=top_k
                    )
                else:
                    results = self._collection.query(
                        query_texts=[query],
                        where=filters,
                        n_results=top_k
                    )
                messages = self.to_messages(result=results)
                return messages
            else:
                # No query text, only conditional search
                results = self._collection.get(where=filters)
                messages = self.to_messages(result=results, sort_by_time=True)
                # If top_k is specified, limit return count
                if top_k > 0:
                    return messages[:top_k]
                return messages

        except Exception as e:
            LOGGER.error(f'ChromaMemory.search failed, exception= {str(e)}')
            return []

    def _parse_tags_from_string(self, tags_str: str) -> List[str]:
        """Parse comma-separated tags string into a list.
        
        Args:
            tags_str (str): The comma-separated tags string
            
        Returns:
            List[str]: List of parsed tags
        """
        if not tags_str:
            return []
        # Split string and remove whitespace
        return [tag.strip() for tag in tags_str.split(",") if tag.strip()]

    @staticmethod
    def is_nested_list(variable: List) -> bool:
        """Check if a variable is a nested list."""
        return isinstance(variable, list) and len(variable) > 0 and isinstance(variable[0], list)