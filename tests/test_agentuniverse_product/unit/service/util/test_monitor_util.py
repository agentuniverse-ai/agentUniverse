#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Test cases for monitor_util module.
"""

import unittest
from unittest.mock import patch, MagicMock
from agentuniverse_product.service.util.monitor_util import monitor_context, get_monitor_data


class MonitorUtilTest(unittest.TestCase):
    """Test cases for the monitor_util module."""

    @patch('agentuniverse_product.service.util.monitor_util.Monitor')
    def test_monitor_context_initialization(self, mock_monitor):
        """Test that monitor_context initializes monitoring correctly."""
        with monitor_context():
            # Code block to test
            pass

        # Verify that initialization methods are called
        mock_monitor.init_invocation_chain_bak.assert_called_once()
        mock_monitor.init_token_usage.assert_called_once()

    @patch('agentuniverse_product.service.util.monitor_util.Monitor')
    def test_monitor_context_cleanup(self, mock_monitor):
        """Test that monitor_context cleans up monitoring correctly."""
        with monitor_context():
            # Code block to test
            pass

        # Verify that cleanup methods are called
        mock_monitor.clear_invocation_chain.assert_called_once()
        mock_monitor.clear_token_usage.assert_called_once()

    @patch('agentuniverse_product.service.util.monitor_util.Monitor')
    def test_monitor_context_cleanup_on_exception(self, mock_monitor):
        """Test that monitor_context cleans up even when exception occurs."""
        try:
            with monitor_context():
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Verify that cleanup methods are still called even after exception
        mock_monitor.clear_invocation_chain.assert_called_once()
        mock_monitor.clear_token_usage.assert_called_once()

    @patch('agentuniverse_product.service.util.monitor_util.Monitor')
    def test_get_monitor_data(self, mock_monitor):
        """Test that get_monitor_data retrieves monitor information correctly."""
        # Setup mock return values
        mock_invocation_chain = {'test': 'invocation_chain'}
        mock_token_usage = {'test': 'token_usage'}
        mock_monitor.get_invocation_chain_bak.return_value = mock_invocation_chain
        mock_monitor.get_token_usage.return_value = mock_token_usage

        # Call the function
        invocation_chain, token_usage = get_monitor_data()

        # Verify results
        self.assertEqual(invocation_chain, mock_invocation_chain)
        self.assertEqual(token_usage, mock_token_usage)
        mock_monitor.get_invocation_chain_bak.assert_called_once()
        mock_monitor.get_token_usage.assert_called_once()


if __name__ == '__main__':
    unittest.main()