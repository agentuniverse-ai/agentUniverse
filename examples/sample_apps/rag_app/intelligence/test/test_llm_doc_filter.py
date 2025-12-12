#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/9 22:00
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: test_llm_doc_filter.py

"""
Integration test for LLMDocFilter document filtering functionality.

This test demonstrates how to use the LLM-based document filter to filter
documents based on custom rules such as content relevance, date filtering,
and content sensitivity.

Usage:
- Configure the LLM filter in your YAML configuration
- Run this script to see the filtering results
- Expected output shows original vs filtered document counts
"""

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.agentuniverse import AgentUniverse

# Initialize AgentUniverse with configuration
AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)

def test_llm_doc_filter():
    """Example demonstrating LLM document filtering with sample data.
    
    This function creates sample documents with different characteristics
    and applies the LLM document filter to demonstrate the filtering process.
    
    Steps:
    1. Create sample documents with varied content
    2. Create a query for context filtering
    3. Load the configured LLM document filter
    4. Apply filtering and display results
    
    Returns:
        None: Results are printed to console
    """
    
    # Create sample documents with different characteristics for testing
    documents = [
        # Document 1: Technology-related content (should be kept)
        Document(
            text="""This is a great article about AI technology advancements in 2024.
            It discusses the latest breakthroughs in machine learning and their applications.
            The content is well-researched and up-to-date.""",
            metadata={"source": "tech_journal", "date": "2024-03-15"}
        ),
        # Document 2: Political content (should be filtered out)
        Document(
            text="""Political analysis of recent government policies and their impact on the economy.
            This document contains sensitive political content that should be filtered out.""",
            metadata={"source": "political_blog", "date": "2023-11-20"}
        ),
        # Document 3: Outdated content (should be filtered)
        Document(
            text="""Outdated information about software development from 2020.
            This content is no longer relevant and should be filtered.""",
            metadata={"source": "old_blog", "date": "2020-05-10"}
        ),
        # Document 4: Scientific research (should be kept)
        Document(
            text="""Latest research on neural networks and deep learning architectures.
            Published in a reputable scientific journal in 2024.""",
            metadata={"source": "research_paper", "date": "2024-01-30"}
        )
    ]
    
    # Create a query for context (optional)
    query = Query(query_str="AI technology advancements")
    
    # Get the LLM document filter instance
    filter_name = "llm_doc_filter"  # Use the name from your YAML configuration
    doc_filter = DocProcessorManager().get_instance_obj(filter_name)
    
    if not doc_filter:
        print(f"Document filter '{filter_name}' not found. Please check your configuration.")
        return
    
    # Apply the filter
    print(f"Original documents: {len(documents)}")
    filtered_docs = doc_filter.process_docs(documents, query)
    print(f"Filtered documents: {len(filtered_docs)}")
    
    # Display filtering results with detailed formatting
    print("\nFiltered Documents:")
    for i, doc in enumerate(filtered_docs):
        print(f"\nDocument {i+1}:")
        # Show first 100 characters of content for brevity
        print(f"Content: {doc.text[:100]}...")
        print(f"Metadata: {doc.metadata}")


if __name__ == "__main__":
    test_llm_doc_filter()
