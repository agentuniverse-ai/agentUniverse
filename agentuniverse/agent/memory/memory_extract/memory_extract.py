#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 13:55
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: memory_extract.py

import asyncio
import json
import queue
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Set
from collections import defaultdict
from threading import Lock
from queue import Queue

from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.memory_storage.memory_storage_manager import MemoryStorageManager
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.configers.memory_extract_configer import MemoryExtractConfiger
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager


class MemoryCategoryEnum(Enum):
    """Memory category enumeration."""
    FACTUAL = "FACTUAL"  # Factual memory
    EPISODIC = "EPISODIC"  # Episodic memory
    SEMANTIC = "SEMANTIC"  # Semantic memory
    EXPERT = "EXPERT"  # Expert experience
    DEFAULT = "DEFAULT"  # Default category


class MemoryOperationEnum(Enum):
    """Memory operation enumeration."""
    ADD = "ADD"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    NONE = "NONE"

class MemoryOwnerEnum(Enum):
    """Memory owner enumeration."""
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    DEFAULT = "DEFAULT"


class LongTermMemoryMessage(Message):
    """Memory entity."""
    category: MemoryCategoryEnum
    related_role: MemoryOwnerEnum
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)  # Memory confidence
    update: bool = False

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True


class MemoryOperation(BaseModel):
    """Memory operation."""
    id: Optional[str] = None
    text: Optional[str] = None
    event: MemoryOperationEnum
    category: MemoryCategoryEnum
    related_role: MemoryOwnerEnum
    old_memory: Optional[str] = None

    class Config:
        use_enum_values = True


class MemoryOperations(BaseModel):
    """Memory operations collection."""
    memory: List[MemoryOperation] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class MemoryExtract(ComponentBase):
    """Memory extraction component.
    
    Responsible for extracting key information from short-term memory 
    and storing it in MemoryStorage as long-term memory.
    """

    name: str = ""
    description: Optional[str] = None
    memory_storage: str = None
    extract_prompt_version: str = None
    operation_prompt_version: str = None

    # Configuration attributes
    enabled: bool = True
    top_k: int = 5
    extraction_llm: str = None
    operation_llm: str = None
    max_workers: int = 20

    max_memories_per_user: int = 1000
    max_memories_per_agent: int = 1000

    # Thread pool for asynchronous processing
    _executor: Optional[ThreadPoolExecutor] = None
    # Session task queues to ensure ordered execution
    _session_queues: Dict[str, Queue] = defaultdict(Queue)
    _queue_locks: Dict[str, Lock] = defaultdict(Lock)
    _queue_processors: Set[str] = set()

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.MEMORY_EXTRACTOR, **kwargs)
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="MemoryExtract")

    def extract_and_store(self, messages: List[Message], session_id: str = None, agent_id: str = None,
                          user_id: str = None, **kwargs) -> None:
        """Extract and store memories from messages.
        
        Args:
            messages (List[Message]): List of messages.
            session_id (str, optional): Session ID.
            agent_id (str, optional): Agent ID.
            user_id (str, optional): User ID.
            **kwargs: Additional parameters.
        """
        if not self.enabled:
            return

        # Use default session if no session_id provided
        effective_session_id = session_id or "default_session"
        
        # Submit task to session-specific queue
        self._submit_to_session_queue(messages, effective_session_id, user_id, agent_id)

    def _submit_to_session_queue(self, messages: List[Message], session_id: str, user_id: str, agent_id: str) -> None:
        """Submit memory extraction task to session-specific queue.
        
        Args:
            messages (List[Message]): List of messages.
            session_id (str): Session ID.
            user_id (str): User ID.
            agent_id (str): Agent ID.
        """
        # Add task to session queue
        task_data = (messages, session_id, user_id, agent_id)
        self._session_queues[session_id].put(task_data)
        
        # Start queue processor if not already running
        with self._queue_locks[session_id]:
            if session_id not in self._queue_processors:
                self._queue_processors.add(session_id)
                self._executor.submit(self._process_session_queue, session_id)

    def _process_session_queue(self, session_id: str) -> None:
        """Process tasks in session queue sequentially.

        Args:
            session_id (str): Session ID.
        """
        # Session processor idle timeout (5 minutes)
        idle_timeout = 300  # 5 minutes in seconds
        
        try:
            last_activity_time = datetime.now()
            
            while True:
                # Calculate remaining timeout
                current_time = datetime.now()
                time_since_last_activity = (current_time - last_activity_time).total_seconds()
                remaining_timeout = max(0, idle_timeout - time_since_last_activity)
                
                # Get next task from queue with timeout
                try:
                    task_data = self._session_queues[session_id].get(timeout=remaining_timeout)
                    last_activity_time = datetime.now()  # Reset activity timer
                except queue.Empty:
                    # Queue empty for timeout period, exit gracefully
                    LOGGER.info(f"Session queue processor for session {session_id} exiting due to inactivity")
                    break
                
                # Execute the task
                try:
                    messages, session_id, user_id, agent_id = task_data
                    self._run_extract_and_store(messages, session_id, user_id, agent_id)
                except Exception as e:
                    LOGGER.error(f"Memory extraction task failed for session {session_id}: {e}")

        except Exception as e:
            LOGGER.error(f"Session queue processor failed for session {session_id}: {e}")
        finally:
            # Clean up queue processor
            with self._queue_locks[session_id]:
                self._queue_processors.discard(session_id)
                # Clean up empty queue to avoid memory leaks
                if session_id in self._session_queues and self._session_queues[session_id].empty():
                    del self._session_queues[session_id]
                    del self._queue_locks[session_id]

    def _run_extract_and_store(self, messages: List[Message], session_id: str, user_id: str, agent_id: str) -> None:
        """Synchronous wrapper method to run async tasks in thread pool."""
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._extract_and_store_memory(messages, session_id, user_id, agent_id))
        except Exception as e:
            LOGGER.error(f"Memory extraction task failed: {e}")
        finally:
            loop.close()

    async def _extract_and_store_memory(self, messages: List['Message'],
                                        session_id: str, user_id: str, agent_id: str) -> None:
        """Extract and store memory."""
        try:
            # 1. Extract factual information
            facts = await self._extract_facts(messages)

            if not facts:
                return

            # 2. Recall related historical memories
            facts_query = " ".join([fact.get("fact", "") for fact in facts])
            related_memories = self.search_memories(
                query=facts_query,
                session_id=session_id,
                user_id=user_id,
                agent_id=agent_id,
                top_k=self.top_k
            )

            if related_memories:
                # 3. Let LLM determine memory operations
                operations = await self._determine_memory_operations(facts, related_memories)
            else:
                # If no related historical memories, directly convert facts to add operations
                operations = self._convert_facts_to_add_operations(facts)

            if not operations.memory:
                return
            # 4. Execute memory operations
            await self._execute_memory_operations(operations, user_id, agent_id, session_id)

            LOGGER.info(f"Successfully extracted and stored {len(facts)} memories")

        except Exception as e:
            LOGGER.error(f"Memory extraction and storage failed: {e}")

    async def _extract_facts(self, messages: List['Message']) -> List[dict]:
        """Extract factual information using LLM."""

        try:
            # Build extraction prompt - only use the latest 2 messages
            recent_messages = messages[-2:] if len(messages) >= 2 else messages
            conversation_text = "\n".join([
                f"{msg.content}" for msg in recent_messages if msg.content
            ])

            # Load prompt from yaml file
            prompt_template = self._load_prompt(self.extract_prompt_version)
            prompt = prompt_template.format(conversation_text=conversation_text, date=datetime.now().strftime("%Y-%m-%d"))

            llm: LLM = LLMManager().get_instance_obj(self.extraction_llm)
            if llm:
                result = await self._call_llm(llm, prompt)
                return result.get("facts", [])

            return []

        except Exception as e:
            LOGGER.error(f"Memory extraction and storage failed: {e}")
            return []

    async def _call_llm(self, llm: LLM, prompt: str) -> dict:
        """Call LLM with prompt and parse JSON response.
        
        Args:
            llm (LLM): The LLM instance to call.
            prompt (str): The prompt to send to LLM.
            
        Returns:
            dict: Parsed JSON response from LLM.
        """
        messages = [
            {
                "role": ChatMessageEnum.USER.value,
                "content": prompt,
            }
        ]
        output = llm.call(messages=messages, streaming=False)
        result_text = output.text
        if result_text.strip().startswith('```json') and result_text.strip().endswith('```'):
            result_text = result_text.strip()[7:-3].strip()
        elif result_text.strip().startswith('```') and result_text.strip().endswith('```'):
            result_text = result_text.strip()[3:-3].strip()
        result = json.loads(result_text)
        return result

    async def _determine_memory_operations(self, facts: List[dict],
                                           related_memories: List[Message]) -> MemoryOperations:
        """Let LLM determine memory operations."""
        try:
            # Build related memory text
            facts_text = "\n".join([
                f"Fact: {fact.get('fact', '')}, Category: {fact.get('category', '')}, Role: {fact.get('related_role', '')}"
                for fact in facts
            ])

            memories_text = "\n".join([
                f"ID: {mem.id}, Content: {mem.content}" for mem in related_memories
            ])

            # Load prompt from yaml file
            prompt_template = self._load_prompt(self.operation_prompt_version)
            prompt = prompt_template.format(new_facts=facts_text, related_memories=memories_text, date=datetime.now().strftime("%Y-%m-%d"))

            llm: LLM = LLMManager().get_instance_obj(self.operation_llm)
            if llm:
                result = await self._call_llm(llm, prompt)
                return MemoryOperations(**result)

            return MemoryOperations()

        except Exception as e:
            LOGGER.error(f"Memory operation determination failed: {e}")
            return MemoryOperations()

    async def _execute_memory_operations(self, operations: MemoryOperations,
                                         user_id: str, agent_id: str, session_id: str) -> None:
        """Execute memory operations (batch processing)."""
        # Group operations
        add_memories = []
        update_memories = []
        delete_ids = []

        for operation in operations.memory:
            if operation.event == MemoryOperationEnum.ADD.name:
                # Create MemoryEntity for batch addition
                memory_agent_id, memory_user_id = await self.determine_memory_related_info(agent_id, operation, user_id)
                memory_entity = LongTermMemoryMessage(
                    content=operation.text,
                    category=operation.category or MemoryCategoryEnum.DEFAULT.value,
                    related_role=operation.related_role or MemoryOwnerEnum.DEFAULT.value,
                    user_id=memory_user_id,
                    agent_id=memory_agent_id,
                    session_id=session_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                add_memories.append(memory_entity)
            elif operation.event == MemoryOperationEnum.UPDATE.name:
                # Create MemoryEntity for batch update
                memory_agent_id, memory_user_id = await self.determine_memory_related_info(agent_id, operation, user_id)
                if operation.id and operation.text:
                    memory_entity = LongTermMemoryMessage(
                        id=operation.id,
                        content=operation.text,
                        category=operation.category,
                        related_role=operation.related_role,
                        user_id=memory_user_id,
                        agent_id=memory_agent_id,
                        session_id=session_id,
                        update=True,
                        updated_at=datetime.now()
                    )
                    update_memories.append(memory_entity)
            elif operation.event == MemoryOperationEnum.DELETE.name:
                # Collect deletion IDs
                if operation.id:
                    delete_ids.append(operation.id)

        # Batch addition
        if add_memories:
            await self._upsert_memory(add_memories)

        # Batch update
        if update_memories:
            await self._upsert_memory(update_memories)

        # Batch deletion
        if delete_ids:
            await self._delete_memory(delete_ids)

    async def determine_memory_related_info(self, agent_id, operation, user_id):
        # Determine user_id and agent_id based on related_role
        memory_user_id = None
        memory_agent_id = None
        if operation.related_role == MemoryOwnerEnum.USER.name:
            memory_user_id = user_id
            memory_agent_id = None
        elif operation.related_role == MemoryOwnerEnum.ASSISTANT.name:
            memory_user_id = None
            memory_agent_id = agent_id
        else:  # DEFAULT or other cases
            memory_user_id = user_id
            memory_agent_id = agent_id
        return memory_agent_id, memory_user_id

    async def _delete_memory(self, memory_id: List[str]) -> bool:
        """Delete memory."""
        try:
            if not self.memory_storage:
                LOGGER.warning("MemoryStorage not initialized, cannot delete memory")
                return False

            memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(self.memory_storage)
            if memory_storage:
                memory_storage.delete(ids=memory_id)
            return True

        except Exception as e:
            LOGGER.error(f"Delete memory failed: {e}")
            return False

    async def _upsert_memory(self, memories: List[LongTermMemoryMessage]) -> bool:
        """Store single memory to MemoryStorage."""
        try:
            if not self.memory_storage:
                LOGGER.warning("MemoryStorage not initialized, cannot store memory")
                return False

            memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(self.memory_storage)
            if memory_storage:
                memory_storage.add(memories)
            return True

        except Exception as e:
            LOGGER.error(f"Store memory failed: {e}")
            return False

    def search_memories(self, query: str = None, top_k: int = 10, session_id: str = None, agent_id: str = None,
                              user_id: str = None, tags: List[str] = None, time_range: tuple = None) -> List[Message]:
        """Search memories.
        
        Args:
            query (str, optional): Query string for embedding retrieval.
            top_k (int, optional): Return count.
            session_id (str, optional): Session ID.
            agent_id (str, optional): Agent ID.
            user_id (str, optional): User ID.
            tags (List[str], optional): Tags for filtering.
            time_range (tuple, optional): Time range.

        Returns:
            List[Message]: List of memory entities.
        """
        if not self.memory_storage:
            LOGGER.warning("MemoryStorage not initialized, cannot store memory")
            return []

        try:
            memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(self.memory_storage)
            # Use the unified get method which now supports all search parameters via kwargs
            return memory_storage.get(
                session_id=session_id,
                agent_id=agent_id,
                top_k=top_k,
                query=query,
                user_id=user_id,
                tags=tags,
                time_range=time_range
            )
        except Exception as e:
            LOGGER.error(f"Memory search failed: {e}")
            return []

    async def delete_memory_by_session_id(self, session_id: str = None, **kwargs) -> bool:
        """Delete memories by session_id.
        
        Args:
            session_id (str, optional): Session ID.
            **kwargs: Additional parameters.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            if not self.memory_storage:
                LOGGER.warning("MemoryStorage not initialized, cannot delete memory")
                return False

            # Use MemoryStorage for deletion
            memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(self.memory_storage)
            if memory_storage:
                memory_storage.delete(session_id=session_id)

        except Exception as e:
            LOGGER.error(f"Soft delete memory failed: {e}")
            return False

    def _load_prompt(self, prompt_version: str) -> PromptTemplate:
        """Load prompt template from yaml file.
        
        Args:
            prompt_version (str): The prompt version identifier.
            
        Returns:
            PromptTemplate: The loaded prompt template.
            
        Raises:
            Exception: If the prompt version is not found.
        """
        version_prompt: Prompt = PromptManager().get_instance_obj(prompt_version)

        if version_prompt is None:
            raise Exception("The`prompt_version` in profile configuration should be provided.")
        return version_prompt.build_simple_prompt().as_langchain()

    def initialize_by_component_configer(self, component_configer: MemoryExtractConfiger) -> 'MemoryExtract':
        """Initialize the MemoryExtract by the MemoryExtractConfiger object.

        Args:
            component_configer (MemoryExtractConfiger): The ComponentConfiger object.
            
        Returns:
            MemoryExtract: The MemoryExtract object.
        """
        memory_extract_config: Optional[MemoryExtractConfiger] = component_configer.load()

        # Set basic attributes
        if memory_extract_config.name:
            self.name = memory_extract_config.name
        if memory_extract_config.description:
            self.description = memory_extract_config.description

        # Set configuration attributes
        if memory_extract_config.enabled is not None:
            self.enabled = memory_extract_config.enabled
        if memory_extract_config.top_k is not None:
            self.top_k = memory_extract_config.top_k
        if memory_extract_config.max_workers is not None:
            self.max_workers = memory_extract_config.max_workers
        if memory_extract_config.memory_storage:
            self.memory_storage = memory_extract_config.memory_storage
        if memory_extract_config.extract_prompt_version:
            self.extract_prompt_version = memory_extract_config.extract_prompt_version
        if memory_extract_config.operation_prompt_version:
            self.operation_prompt_version = memory_extract_config.operation_prompt_version
        if memory_extract_config.extraction_llm:
            self.extraction_llm = memory_extract_config.extraction_llm
        if memory_extract_config.operation_llm:
            self.operation_llm = memory_extract_config.operation_llm
        if memory_extract_config.max_memories_per_user is not None:
            self.max_memories_per_user = memory_extract_config.max_memories_per_user
        if memory_extract_config.max_memories_per_agent is not None:
            self.max_memories_per_agent = memory_extract_config.max_memories_per_agent

        return self

    def _convert_facts_to_add_operations(self, facts: List[dict]) -> MemoryOperations:
        """Convert facts to ADD memory operations."""
        operations = MemoryOperations()
        
        for fact in facts:
            # Filter out empty facts
            fact_text = fact.get("fact", "").strip()
            if not fact_text:
                continue
                
            # Create an add memory operation for each fact
            operation = MemoryOperation(
                id=None,  # Add operation doesn't need ID
                text=fact_text,
                event=MemoryOperationEnum.ADD,
                category=MemoryCategoryEnum(fact.get("category", MemoryCategoryEnum.DEFAULT.name)),
                related_role=MemoryOwnerEnum(fact.get("related_role", MemoryOwnerEnum.DEFAULT.name)),
                old_memory=None  # Add operation doesn't need original memory content
            )
            operations.memory.append(operation)
        
        return operations

    def create_copy(self):
        """Create a copy."""
        copied = self.model_copy()
        # Since configuration is now direct attributes, no need for separate config copying
        return copied