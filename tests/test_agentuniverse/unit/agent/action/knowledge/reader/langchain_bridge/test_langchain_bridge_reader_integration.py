#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/12 14:25
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: test_langchain_bridge_reader_integration.py
"""
Integration tests for LangchainBridgeReader with actual configurations
"""

import os
import unittest

from agentuniverse.agent.action.knowledge.reader.langchain_bridge.langchain_bridge_reader import LangchainBridgeReader
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class TestLangchainBridgeReaderIntegration(unittest.TestCase):
    """Integration tests for LangchainBridgeReader"""

    def setUp(self) -> None:
        # enable real integration test need real token setup
        # Note: These are example tokens for demonstration only
        # For real testing, set actual valid tokens as environment variables
        os.environ['GITHUB_ACCESS_TOKEN'] = ''

    def test_yuque_loader_configuration_with_configer(self):
        """Test YuqueLoader configuration using ComponentConfiger (simulating bridge_yuque_reader.yaml)"""
        # Create configer with YuqueLoader configuration
        cfg = Configer()
        cfg.value = {
            'name': 'langchain_yuque_reader',
            'description': 'Use langchain yuque reader to read yuque document',
            'loader_class': 'YuqueLoader',
            'loader_module': 'langchain_community.document_loaders.yuque',
            'loader_params': {
                'access_token': 'test_yuque_token'
            },
            'metadata': {
                'type': 'READER',
                'module': 'agentuniverse.agent.action.knowledge.reader.langchain_bridge.langchain_bridge_reader',
                'class': 'LangchainBridgeReader'
            }
        }

        configer = ComponentConfiger()
        configer.load_by_configer(cfg)

        # Create reader and initialize with configer
        reader = LangchainBridgeReader()
        reader._initialize_by_component_configer(configer)

        # Verify configuration
        self.assertEqual(reader.name, 'langchain_yuque_reader')
        self.assertEqual(reader.description, 'Use langchain yuque reader to read yuque document')
        self.assertEqual(reader.loader_class, 'YuqueLoader')
        self.assertEqual(reader.loader_module, 'langchain_community.document_loaders.yuque')
        self.assertEqual(reader.loader_params['access_token'], 'test_yuque_token')

    def test_github_issues_loader_configuration_with_configer(self):
        """Test GitHubIssuesLoader configuration using ComponentConfiger (simulating bridge_github_issue_reader.yaml)"""
        # Create configer with GitHubIssuesLoader configuration
        cfg = Configer()
        cfg.value = {
            'name': 'langchain_github_reader',
            'description': 'Use langchain github reader to read github content',
            'loader_class': 'GitHubIssuesLoader',
            'loader_module': 'langchain_community.document_loaders.github',
            'loader_params': {
                'repo': 'owner/repo',
                'access_token': 'test_github_token',
                'include_prs': True,
                'state': 'all',
                'assignee': None,
                'creator': None,
                'mentioned': None,
                'labels': None,
                'sort': None,
                'direction': None,
                'since': None,
                'page': None,
                'per_page': None
            },
            'metadata': {
                'type': 'READER',
                'module': 'agentuniverse.agent.action.knowledge.reader.langchain_bridge.langchain_bridge_reader',
                'class': 'LangchainBridgeReader'
            }
        }

        configer = ComponentConfiger()
        configer.load_by_configer(cfg)

        # Create reader and initialize with configer
        reader = LangchainBridgeReader()
        reader._initialize_by_component_configer(configer)

        # Verify configuration
        self.assertEqual(reader.name, 'langchain_github_reader')
        self.assertEqual(reader.description, 'Use langchain github reader to read github content')
        self.assertEqual(reader.loader_class, 'GitHubIssuesLoader')
        self.assertEqual(reader.loader_module, 'langchain_community.document_loaders.github')
        self.assertEqual(reader.loader_params['repo'], 'owner/repo')
        self.assertEqual(reader.loader_params['access_token'], 'test_github_token')
        self.assertEqual(reader.loader_params['include_prs'], True)
        self.assertEqual(reader.loader_params['state'], 'all')

    def test_missing_loader_configuration_in_configer(self):
        """Test error handling for missing loader configuration in configer"""
        # Create configer without loader configuration
        cfg = Configer()
        cfg.value = {
            'name': 'test_reader',
            'description': 'Test reader'
        }

        configer = ComponentConfiger()
        configer.load_by_configer(cfg)

        # Create reader and initialize with configer
        reader = LangchainBridgeReader()
        reader._initialize_by_component_configer(configer)

        # Should raise error when trying to load data
        with self.assertRaises(ValueError) as context:
            reader.load_data()

        self.assertIn("LangchainReader requires loader_class and loader_module configuration",
                      str(context.exception))

    def test_github_issues_loader_real_call(self):
        """Test GitHubIssuesLoader with real configuration and mock loader"""
        # Check if token is set, skip if not
        if not os.environ.get('GITHUB_ACCESS_TOKEN'):
            self.skipTest("GITHUB_ACCESS_TOKEN environment variable not set")

        # Create configer with real token from environment
        github_token = os.environ.get('GITHUB_ACCESS_TOKEN', 'test_github_token')
        cfg = Configer()
        cfg.value = {
            'name': 'langchain_github_reader',
            'loader_class': 'GitHubIssuesLoader',
            'loader_module': 'langchain_community.document_loaders.github',
            'loader_params': {
                'repo': 'kaysonx/agentUniverse',
                'access_token': github_token,
                'include_prs': True,
                'state': 'open'
            }
        }

        configer = ComponentConfiger()
        configer.load_by_configer(cfg)

        # Create reader and initialize with configer
        reader = LangchainBridgeReader()
        reader._initialize_by_component_configer(configer)

        # Test actual data loading
        result = reader.load_data()

        # Assertions
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
