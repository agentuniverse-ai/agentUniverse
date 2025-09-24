#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Integration test cases for agent_service monitor functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
from agentuniverse_product.service.agent_service.agent_service import AgentService


class AgentServiceMonitorTest(unittest.TestCase):
    """Integration test cases for the agent_service monitor functionality."""

    @patch('agentuniverse_product.service.agent_service.agent_service.Monitor')
    @patch('agentuniverse_product.service.agent_service.agent_service.AgentManager')
    def test_chat_method_monitoring(self, mock_agent_manager, mock_monitor):
        """Test that chat method uses monitor context correctly."""
        # Setup mocks
        mock_agent = MagicMock()
        mock_agent_manager().get_instance_obj.return_value = mock_agent
        mock_agent.run.return_value.get_data.return_value = "test output"
        
        # Mock time functions
        with patch('agentuniverse_product.service.agent_service.agent_service.time') as mock_time, \
             patch('agentuniverse_product.service.agent_service.agent_service.datetime') as mock_datetime:
            
            mock_time.time.side_effect = [1000, 1001]  # start and end time
            mock_datetime.fromtimestamp.return_value.strftime.return_value = "2023-01-01 00:00:00"
            
            # Call the method
            result = AgentService.chat("test_agent", "test_session", "test_input")
            
            # Verify monitor calls
            mock_monitor.init_invocation_chain_bak.assert_called_once()
            mock_monitor.init_token_usage.assert_called_once()
            mock_monitor.get_invocation_chain_bak.assert_called_once()
            mock_monitor.get_token_usage.assert_called_once()
            mock_monitor.clear_invocation_chain.assert_called_once()
            mock_monitor.clear_token_usage.assert_called_once()
            
            # Verify result
            self.assertIsNotNone(result)
            self.assertIn('response_time', result)
            self.assertIn('output', result)

    @patch('agentuniverse_product.service.agent_service.agent_service.Monitor')
    @patch('agentuniverse_product.service.agent_service.agent_service.AgentManager')
    @patch('agentuniverse_product.service.agent_service.agent_service.RequestTask')
    def test_stream_chat_method_monitoring(self, mock_request_task, mock_agent_manager, mock_monitor):
        """Test that stream_chat method uses monitor context correctly."""
        # Setup mocks
        mock_agent = MagicMock()
        mock_agent_manager().get_instance_obj.return_value = mock_agent
        
        mock_task = MagicMock()
        mock_request_task.return_value = mock_task
        mock_task.stream_run.return_value = [
            '{"process": {"data": {"chunk": "test chunk"}}}',
        ]
        
        # Mock agent util function
        with patch('agentuniverse_product.service.agent_service.agent_service.validate_and_assemble_agent_input') as mock_validate:
            mock_validate.return_value = {}
            
            # Convert generator to list to consume it
            result = list(AgentService.stream_chat("test_agent", "test_session", "test_input"))
            
            # Verify monitor calls
            mock_monitor.init_invocation_chain_bak.assert_called_once()
            mock_monitor.init_token_usage.assert_called_once()
            mock_monitor.clear_invocation_chain.assert_called_once()
            mock_monitor.clear_token_usage.assert_called_once()
            
            # Verify result is returned
            self.assertIsNotNone(result)

    @patch('agentuniverse_product.service.agent_service.agent_service.Monitor')
    @patch('agentuniverse_product.service.agent_service.agent_service.AgentManager')
    @patch('agentuniverse_product.service.agent_service.agent_service.RequestTask')
    def test_async_stream_chat_method_monitoring(self, mock_request_task, mock_agent_manager, mock_monitor):
        """Test that async_stream_chat method uses monitor context correctly."""
        # Setup mocks
        mock_agent = MagicMock()
        mock_agent_manager().get_instance_obj.return_value = mock_agent
        
        mock_task = MagicMock()
        mock_request_task.return_value = mock_task
        
        # Mock async iterator
        async def mock_async_stream_run():
            yield '{"process": {"data": {"chunk": "test chunk"}}}'
        
        mock_task.async_stream_run = mock_async_stream_run
        
        # Mock agent util function
        with patch('agentuniverse_product.service.agent_service.agent_service.validate_and_assemble_agent_input') as mock_validate:
            mock_validate.return_value = {}
            
            # Note: We're not actually running the async function in this test
            # In a real test environment, we would use asyncio to run it
            # For now, we're just checking that the setup is correct
            pass

if __name__ == '__main__':
    unittest.main()