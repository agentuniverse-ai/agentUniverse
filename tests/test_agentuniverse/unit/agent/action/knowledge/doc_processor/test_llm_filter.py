#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/9 22:40
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: test_llm_filter.py

import json
import unittest
from unittest.mock import Mock, patch, MagicMock

from agentuniverse.agent.action.knowledge.doc_processor.llm_doc_filter import LLMDocFilter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.llm.llm import LLM


class MockLLMOutput:
    """Mock LLM output class for testing."""
    
    def __init__(self, text: str):
        self.text = text


class TestLLMFilter(unittest.TestCase):
    """Unit tests for LLMDocFilter class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.doc_filter = LLMDocFilter()
        
        # Create sample documents for testing
        self.sample_documents = [
            Document(
                text="This is a great article about AI technology advancements in 2024.",
                metadata={"source": "tech_journal", "date": "2024-03-15"}
            ),
            Document(
                text="Political analysis of recent government policies and their impact on the economy.",
                metadata={"source": "political_blog", "date": "2023-11-20"}
            ),
            Document(
                text="Outdated information about software development from 2020.",
                metadata={"source": "old_blog", "date": "2020-05-10"}
            ),
            Document(
                text="Latest research on neural networks and deep learning architectures.",
                metadata={"source": "research_paper", "date": "2024-01-30"}
            )
        ]
        
        # Create a sample query
        self.sample_query = Query(query_str="AI technology advancements")

    def test_initialization(self):
        """Test that LLMDocFilter initializes correctly."""
        self.assertIsInstance(self.doc_filter, LLMDocFilter)
        self.assertIsNone(self.doc_filter.filter_llm)
        self.assertIsNone(self.doc_filter.filter_rules)
        self.assertIsNone(self.doc_filter.filter_prompt)
        self.assertEqual(self.doc_filter.batch_size, 5)

    def test_process_docs_empty_list(self):
        """Test processing empty document list."""
        result = self.doc_filter._process_docs([])
        self.assertEqual(result, [])

    def test_process_docs_no_llm_configuration(self):
        """Test processing documents without LLM configuration."""
        with self.assertRaises(Exception) as context:
            self.doc_filter._process_docs(self.sample_documents)
        
        self.assertIn("LLM configuration is required", str(context.exception))

    def test_process_docs_no_filter_rules(self):
        """Test processing documents without filter rules."""
        self.doc_filter.filter_llm = "test_llm"
        
        # Mock LLM manager to avoid actual LLM calls
        with patch('agentuniverse.agent.action.knowledge.doc_processor.llm_doc_filter.LLMManager') as mock_manager:
            # Create a mock LLM that returns empty output
            mock_llm = Mock(spec=LLM)
            mock_output = MockLLMOutput("")
            mock_llm.call.return_value = mock_output
            mock_manager.return_value.get_instance_obj.return_value = mock_llm
            
            result = self.doc_filter._process_docs(self.sample_documents)
            
            # Should return all documents when no filter rules are configured
            self.assertEqual(len(result), len(self.sample_documents))

    @patch('agentuniverse.agent.action.knowledge.doc_processor.llm_doc_filter.LLMManager')
    def test_process_docs_with_valid_configuration(self, mock_manager):
        """Test processing documents with valid configuration."""
        # Setup filter configuration
        self.doc_filter.filter_llm = "test_llm"
        self.doc_filter.filter_rules = "Filter out political content and keep technology-related documents."
        
        # Mock LLM response that keeps documents 0 and 3
        llm_response = {
            "filtered_documents": [
                {"document_index": 0, "should_keep": True, "reason": "Technology-related content"},
                {"document_index": 3, "should_keep": True, "reason": "AI research content"}
            ]
        }
        
        # Create a mock LLM that returns the response
        mock_llm = Mock(spec=LLM)
        mock_output = MockLLMOutput(json.dumps(llm_response))
        mock_llm.call.return_value = mock_output
        mock_manager.return_value.get_instance_obj.return_value = mock_llm
        
        result = self.doc_filter._process_docs(self.sample_documents)
        
        # Should return 2 documents based on LLM response
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].text, self.sample_documents[0].text)
        self.assertEqual(result[1].text, self.sample_documents[3].text)

    @patch('agentuniverse.agent.action.knowledge.doc_processor.llm_doc_filter.LLMManager')
    def test_process_docs_with_query_context(self, mock_manager):
        """Test processing documents with query context."""
        self.doc_filter.filter_llm = "test_llm"
        self.doc_filter.filter_rules = "Filter documents based on relevance to query."
        
        llm_response = {
            "filtered_documents": [
                {"document_index": 0, "should_keep": True, "reason": "Relevant to AI technology"}
            ]
        }
        
        mock_llm = Mock(spec=LLM)
        mock_output = MockLLMOutput(json.dumps(llm_response))
        mock_llm.call.return_value = mock_output
        mock_manager.return_value.get_instance_obj.return_value = mock_llm
        
        result = self.doc_filter._process_docs(self.sample_documents, self.sample_query)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, self.sample_documents[0].text)

    @patch('agentuniverse.agent.action.knowledge.doc_processor.llm_doc_filter.LLMManager')
    def test_process_docs_batch_processing(self, mock_manager):
        """Test batch processing of documents."""
        self.doc_filter.filter_llm = "test_llm"
        self.doc_filter.filter_rules = "Test batch processing"
        self.doc_filter.batch_size = 2  # Process 2 documents per batch
        
        # Create more documents to test batching
        many_documents = self.sample_documents * 3  # 12 documents total
        
        llm_response = {
            "filtered_documents": [
                {"document_index": 0, "should_keep": True, "reason": "Keep first document"},
                {"document_index": 1, "should_keep": True, "reason": "Keep second document"}
            ]
        }
        
        mock_llm = Mock(spec=LLM)
        mock_output = MockLLMOutput(json.dumps(llm_response))
        mock_llm.call.return_value = mock_output
        mock_manager.return_value.get_instance_obj.return_value = mock_llm
        
        result = self.doc_filter._process_docs(many_documents)
        
        # Should process all batches and return filtered results
        self.assertEqual(len(result), 12)  # All documents kept in this mock

    @patch('agentuniverse.agent.action.knowledge.doc_processor.llm_doc_filter.LLMManager')
    def test_process_docs_llm_error_handling(self, mock_manager):
        """Test error handling when LLM call fails."""
        self.doc_filter.filter_llm = "test_llm"
        self.doc_filter.filter_rules = "Test error handling"
        
        # Mock LLM that raises an exception
        mock_llm = Mock(spec=LLM)
        mock_llm.call.side_effect = Exception("LLM API error")
        mock_manager.return_value.get_instance_obj.return_value = mock_llm
        
        # Should handle error gracefully and return all documents
        result = self.doc_filter._process_docs(self.sample_documents)
        
        self.assertEqual(len(result), len(self.sample_documents))

    def test_build_filter_prompt_default(self):
        """Test building filter prompt with default template."""
        self.doc_filter.filter_rules = "Test filter rules"
        
        prompt = self.doc_filter._build_filter_prompt(self.sample_documents[:2], self.sample_query)
        
        self.assertIn("Test filter rules", prompt)
        self.assertIn("AI technology advancements", prompt)  # Query context
        self.assertIn("Document 1", prompt)
        self.assertIn("Document 2", prompt)

    def test_build_filter_prompt_custom(self):
        """Test building filter prompt with custom template."""
        self.doc_filter.filter_rules = "Test rules"
        self.doc_filter.filter_prompt = "Custom prompt template with {filter_rules} and {documents}"
        
        prompt = self.doc_filter._build_filter_prompt(self.sample_documents[:1])
        
        self.assertIn("Custom prompt template", prompt)
        self.assertIn("Test rules", prompt)
        self.assertIn("Document 1", prompt)

    def test_parse_filter_response_valid_json(self):
        """Test parsing valid LLM response."""
        llm_response = {
            "filtered_documents": [
                {"document_index": 0, "should_keep": True, "reason": "Good content"},
                {"document_index": 2, "should_keep": True, "reason": "Relevant"}
            ]
        }
        
        response_text = json.dumps(llm_response)
        indices = self.doc_filter._parse_filter_response(response_text, 4)
        
        self.assertEqual(indices, [0, 2])

    def test_parse_filter_response_with_code_blocks(self):
        """Test parsing LLM response with code blocks."""
        llm_response = {
            "filtered_documents": [
                {"document_index": 1, "should_keep": True, "reason": "Keep this"}
            ]
        }
        
        # Test with JSON code block
        response_text = f"```json\n{json.dumps(llm_response)}\n```"
        indices = self.doc_filter._parse_filter_response(response_text, 3)
        
        self.assertEqual(indices, [1])
        
        # Test with generic code block
        response_text = f"```\n{json.dumps(llm_response)}\n```"
        indices = self.doc_filter._parse_filter_response(response_text, 3)
        
        self.assertEqual(indices, [1])

    def test_parse_filter_response_invalid_json(self):
        """Test parsing invalid LLM response."""
        invalid_response = "This is not valid JSON"
        
        # Should handle parsing error and return all indices
        indices = self.doc_filter._parse_filter_response(invalid_response, 3)
        
        self.assertEqual(indices, [0, 1, 2])

    def test_parse_filter_response_out_of_bounds_indices(self):
        """Test parsing response with out-of-bounds indices."""
        llm_response = {
            "filtered_documents": [
                {"document_index": 0, "should_keep": True, "reason": "Valid"},
                {"document_index": 5, "should_keep": True, "reason": "Out of bounds"},  # Only 3 documents
                {"document_index": -1, "should_keep": True, "reason": "Invalid"}
            ]
        }
        
        response_text = json.dumps(llm_response)
        indices = self.doc_filter._parse_filter_response(response_text, 3)
        
        # Should only include valid indices
        self.assertEqual(indices, [0])

    def test_parse_filter_response_false_should_keep(self):
        """Test parsing response with should_keep set to false."""
        llm_response = {
            "filtered_documents": [
                {"document_index": 0, "should_keep": True, "reason": "Keep"},
                {"document_index": 1, "should_keep": False, "reason": "Filter out"},
                {"document_index": 2, "should_keep": True, "reason": "Keep"}
            ]
        }
        
        response_text = json.dumps(llm_response)
        indices = self.doc_filter._parse_filter_response(response_text, 3)
        
        # Should only include documents with should_keep=True
        self.assertEqual(indices, [0, 2])

    def test_initialize_by_component_configer(self):
        """Test initialization from component configer."""
        # Create a mock configer with the required attributes
        configer = MagicMock()
        configer.filter_llm = "test_llm"
        configer.filter_rules = "Test rules"
        configer.filter_prompt = "Custom prompt"
        
        result = self.doc_filter._initialize_by_component_configer(configer)
        
        self.assertEqual(result.filter_llm, "test_llm")
        self.assertEqual(result.filter_rules, "Test rules")
        self.assertEqual(result.filter_prompt, "Custom prompt")
        self.assertIs(result, self.doc_filter)

    def test_get_default_prompt(self):
        """Test getting default prompt template."""
        prompt = self.doc_filter._get_default_prompt()
        
        self.assertIn("You are a document filtering assistant", prompt)
        self.assertIn("Filter Rules", prompt)
        self.assertIn("filtered_documents", prompt)
        self.assertIn("document_index", prompt)
        self.assertIn("should_keep", prompt)

    @patch('agentuniverse.agent.action.knowledge.doc_processor.llm_doc_filter.LLMManager')
    def test_filter_batch_success(self, mock_manager):
        """Test successful batch filtering."""
        self.doc_filter.filter_llm = "test_llm"
        self.doc_filter.filter_rules = "Test rules"
        
        llm_response = {
            "filtered_documents": [
                {"document_index": 0, "should_keep": True, "reason": "Keep first"},
                {"document_index": 1, "should_keep": False, "reason": "Filter second"}
            ]
        }
        
        mock_llm = Mock(spec=LLM)
        mock_output = MockLLMOutput(json.dumps(llm_response))
        mock_llm.call.return_value = mock_output
        mock_manager.return_value.get_instance_obj.return_value = mock_llm
        
        batch = self.sample_documents[:2]
        result = self.doc_filter._filter_batch(mock_llm, batch)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, batch[0].text)

    @patch('agentuniverse.agent.action.knowledge.doc_processor.llm_doc_filter.LLMManager')
    def test_filter_batch_error_handling(self, mock_manager):
        """Test batch filtering error handling."""
        self.doc_filter.filter_llm = "test_llm"
        self.doc_filter.filter_rules = "Test rules"
        
        # Mock LLM that raises exception
        mock_llm = Mock(spec=LLM)
        mock_llm.call.side_effect = Exception("Batch processing error")
        mock_manager.return_value.get_instance_obj.return_value = mock_llm
        
        batch = self.sample_documents[:2]
        result = self.doc_filter._filter_batch(mock_llm, batch)
        
        # Should return all documents on error
        self.assertEqual(len(result), len(batch))


if __name__ == "__main__":
    unittest.main()
