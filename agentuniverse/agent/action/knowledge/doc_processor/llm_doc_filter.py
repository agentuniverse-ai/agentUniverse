#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/9 22:00
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: llm_doc_filter.py

import json
from typing import List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager


class LLMDocFilter(DocProcessor):
    """Document filter using LLM to filter documents based on custom rules.

    This processor uses an LLM to filter documents according to specified rules,
    such as filtering content by date, removing politically sensitive content, etc.
    """
    
    filter_llm: Optional[str] = None
    filter_rules: Optional[str] = None
    filter_prompt: Optional[str] = None
    batch_size: int = 5

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Filter documents using LLM based on configured rules.

        Args:
            origin_docs: List of documents to be filtered.
            query: Query object containing the search query string (optional).

        Returns:
            List[Document]: Filtered documents that pass the filter rules.

        Raises:
            Exception: If the LLM configuration is missing or the API call fails.
        """
        if not origin_docs:
            return []

        if not self.filter_llm:
            raise Exception("LLM configuration is required for document filtering.")

        if not self.filter_rules:
            LOGGER.warn("No filter rules configured, returning all documents.")
            return origin_docs

        # Get LLM instance
        llm: LLM = LLMManager().get_instance_obj(self.filter_llm)
        if not llm:
            raise Exception(f"LLM instance '{self.filter_llm}' not found.")

        filtered_docs = []
        
        # Process documents in batches to avoid overwhelming the LLM
        for i in range(0, len(origin_docs), self.batch_size):
            batch = origin_docs[i:i + self.batch_size]
            batch_index = i // self.batch_size  # Calculate batch index
            batch_filtered = self._filter_batch(llm, batch, query, batch_index)
            filtered_docs.extend(batch_filtered)

        LOGGER.info(f"Filtered {len(origin_docs)} documents to {len(filtered_docs)} documents")
        return filtered_docs

    def _filter_batch(self, llm: LLM, docs: List[Document], query: Query = None, batch_index: int = 0) -> List[Document]:
        """Filter a batch of documents using LLM.

        Args:
            llm: LLM instance for filtering.
            docs: List of documents to filter.
            query: Optional query for context.
            batch_index: Index of the current batch (starting from 0).

        Returns:
            List[Document]: Filtered documents.
        """
        try:
            # Log batch processing info
            batch_info = f"Processing batch {batch_index + 1} with {len(docs)} documents"
            if query and query.query_str:
                batch_info += f" for query: {query.query_str}"
            LOGGER.info(batch_info)
            
            # Build prompt for batch processing
            prompt = self._build_filter_prompt(docs, query)
            
            # Call LLM
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
            
            output = llm.call(messages=messages, streaming=False)
            result_text = output.text
            
            # Parse LLM response
            filtered_indices = self._parse_filter_response(result_text, len(docs))
            
            # Log batch result
            LOGGER.info(f"Batch {batch_index + 1} filtered: {len(docs)} documents -> {len(filtered_indices)} documents kept")
            
            # Return filtered documents
            return [docs[i] for i in filtered_indices]
            
        except (json.JSONDecodeError, KeyError, ValueError, Exception) as e:
            LOGGER.error(f"Error filtering document batch {batch_index + 1}: {e}")
            # In case of error, return all documents to avoid data loss
            return docs

    def _build_filter_prompt(self, docs: List[Document], query: Query = None) -> str:
        """Build the prompt for document filtering.

        Args:
            docs: Documents to filter.
            query: Optional query for context.

        Returns:
            str: The constructed prompt.
        """
        # Use custom prompt if provided, otherwise use default
        if self.filter_prompt:
            base_prompt = self.filter_prompt
        else:
            base_prompt = self._get_default_prompt()
        
        # Build documents text
        docs_text = "\n\n".join(
            f"Document {i+1}:\n{doc.text}" 
            for i, doc in enumerate(docs)
        )
        
        # Build query context if available
        query_context = ""
        if query and query.query_str:
            query_context = f"Query context: {query.query_str}\n\n"
        
        prompt = base_prompt.format(
            filter_rules=self.filter_rules,
            query_context=query_context,
            documents=docs_text.strip()
        )
        
        return prompt

    def _get_default_prompt(self) -> str:
        """Get the default filtering prompt.

        Returns:
            str: Default prompt template.
        """
        return """
You are a document filtering assistant. Your task is to filter documents based on the specified rules.

Filter Rules:
{filter_rules}

{query_context}

Documents to filter:
{documents}

Please analyze each document and determine if it should be kept or filtered out based on the rules.

Return your response in JSON format with the following structure:
{{
    "filtered_documents": [
        {{
            "document_index": 0,
            "should_keep": true,
            "reason": "Brief explanation"
        }},
        ...
    ]
}}

Document indices start from 0. Only include documents that should be kept (should_keep: true)."""

    def _parse_filter_response(self, response_text: str, total_docs: int) -> List[int]:
        """Parse the LLM response to extract filtered document indices.

        Args:
            response_text: LLM response text.
            total_docs: Total number of documents in the batch.

        Returns:
            List[int]: List of indices of documents to keep.
        """
        try:
            # Clean response text
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json') and cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[7:-3].strip()
            elif cleaned_text.startswith('```') and cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[3:-3].strip()
            
            # Parse JSON
            result = json.loads(cleaned_text)
            filtered_docs = result.get("filtered_documents", [])
            
            # Extract indices of documents to keep
            keep_indices = []
            for item in filtered_docs:
                index = item.get("document_index")
                should_keep = item.get("should_keep", False)
                
                if should_keep and 0 <= index < total_docs:
                    keep_indices.append(index)
            
            return keep_indices
            
        except Exception as e:
            LOGGER.error(f"Error parsing LLM filter response: {e}")
            LOGGER.debug(f"Response text: {response_text}")
            # If parsing fails, return all indices (keep all documents)
            return list(range(total_docs))

    def _initialize_by_component_configer(self, doc_processor_configer: ComponentConfiger) -> 'DocProcessor':
        """Initialize filter parameters from component configuration.

        Args:
            doc_processor_configer: Configuration object for the doc processor.

        Returns:
            DocProcessor: The initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        # Initialize from configuration
        if hasattr(doc_processor_configer, "filter_llm"):
            self.filter_llm = doc_processor_configer.filter_llm
        if hasattr(doc_processor_configer, "filter_rules"):
            self.filter_rules = doc_processor_configer.filter_rules
        if hasattr(doc_processor_configer, "filter_prompt"):
            self.filter_prompt = doc_processor_configer.filter_prompt
        if hasattr(doc_processor_configer, "batch_size"):
            self.batch_size = doc_processor_configer.batch_size

        return self
