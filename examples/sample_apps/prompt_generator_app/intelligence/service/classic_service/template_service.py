# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: template_service.py
"""Prompt Template Service.

Provides template management and generation functionality for prompt_generator_app.
This service layer focuses on template storage, retrieval, and management.
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root directory to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agentuniverse.prompt.prompt_generator_helper import PromptTemplateHelper


class PromptTemplateService:
    """Prompt Template Service class.

    Provides template management, retrieval, and generation functionality.
    Suitable for template-related business logic in this sample application.
    """

    def __init__(self):
        """Initialize the template service."""
        self.template_helper = PromptTemplateHelper
        self.preset_templates = self._load_preset_templates()

    def _load_preset_templates(self) -> Dict[str, Dict]:
        """Load preset templates.

        Returns:
            Dictionary of preset template configurations.
        """
        return {
            "customer_service": {
                "name": "Customer Service Template",
                "description": "Suitable for e-commerce and service industry customer service scenarios",
                "agent_type": "react",
                "scenario": "customer service",
                "base_prompt": "You are a professional AI customer service assistant, skilled at handling customer inquiries and problem solving."
            },
            "data_analyst": {
                "name": "Data Analyst Template",
                "description": "Suitable for data analysis and business intelligence scenarios",
                "agent_type": "rag",
                "scenario": "data analysis",
                "base_prompt": "You are a professional data analyst, skilled at discovering insights from data."
            },
            "content_creator": {
                "name": "Content Creator Template",
                "description": "Suitable for content creation and creative writing scenarios",
                "agent_type": "planning",
                "scenario": "content creation",
                "base_prompt": "You are a creative content creator, skilled at producing engaging and high-quality content."
            }
        }

    def get_template_by_type(self, agent_type: str) -> Dict[str, Any]:
        """Get template by agent type.

        Args:
            agent_type: Type of the agent.

        Returns:
            Template data for the specified agent type.

        Raises:
            ValueError: If agent_type is not supported.
        """
        if agent_type not in self.template_helper.AGENT_TEMPLATES:
            raise ValueError(f"Unsupported agent type: {agent_type}")

        return self.template_helper.AGENT_TEMPLATES[agent_type]

    def get_preset_template(self, template_name: str) -> Dict[str, Any]:
        """Get preset template by name.

        Args:
            template_name: Name of the preset template.

        Returns:
            Preset template configuration.

        Raises:
            KeyError: If template_name is not found.
        """
        if template_name not in self.preset_templates:
            raise KeyError(f"Preset template not found: {template_name}")

        return self.preset_templates[template_name]

    def list_preset_templates(self) -> List[str]:
        """List all available preset template names.

        Returns:
            List of preset template names.
        """
        return list(self.preset_templates.keys())

    def list_agent_types(self) -> List[str]:
        """List all supported agent types.

        Returns:
            List of supported agent types.
        """
        return list(self.template_helper.AGENT_TEMPLATES.keys())

    def create_custom_template(self, template_name: str, template_config: Dict[str, Any]) -> bool:
        """Create a custom template.

        Args:
            template_name: Name for the custom template.
            template_config: Configuration for the custom template.

        Returns:
            True if template was created successfully.

        Raises:
            ValueError: If template configuration is invalid.
        """
        # Validate required fields
        required_fields = ["name", "description", "agent_type", "scenario"]
        for field in required_fields:
            if field not in template_config:
                raise ValueError(f"Missing required field: {field}")

        # Validate agent type
        if template_config["agent_type"] not in self.template_helper.AGENT_TEMPLATES:
            raise ValueError(f"Unsupported agent type: {template_config['agent_type']}")

        # Add to preset templates
        self.preset_templates[template_name] = template_config
        return True

    def update_template(self, template_name: str, updates: Dict[str, Any]) -> bool:
        """Update an existing template.

        Args:
            template_name: Name of the template to update.
            updates: Dictionary of fields to update.

        Returns:
            True if template was updated successfully.

        Raises:
            KeyError: If template_name is not found.
        """
        if template_name not in self.preset_templates:
            raise KeyError(f"Template not found: {template_name}")

        # Validate agent type if being updated
        if "agent_type" in updates:
            if updates["agent_type"] not in self.template_helper.AGENT_TEMPLATES:
                raise ValueError(f"Unsupported agent type: {updates['agent_type']}")

        # Apply updates
        self.preset_templates[template_name].update(updates)
        return True

    def delete_template(self, template_name: str) -> bool:
        """Delete a custom template.

        Args:
            template_name: Name of the template to delete.

        Returns:
            True if template was deleted successfully.

        Raises:
            KeyError: If template_name is not found.
        """
        if template_name not in self.preset_templates:
            raise KeyError(f"Template not found: {template_name}")

        del self.preset_templates[template_name]
        return True

    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """Search templates by keyword.

        Args:
            query: Search query string.

        Returns:
            List of matching template configurations.
        """
        results = []
        query_lower = query.lower()

        for name, config in self.preset_templates.items():
            if (query_lower in name.lower() or
                query_lower in config.get("name", "").lower() or
                query_lower in config.get("description", "").lower() or
                query_lower in config.get("scenario", "").lower()):
                results.append({
                    "template_name": name,
                    **config
                })

        return results

    def get_template_stats(self) -> Dict[str, Any]:
        """Get template statistics.

        Returns:
            Dictionary with template statistics.
        """
        agent_type_counts = {}
        for config in self.preset_templates.values():
            agent_type = config.get("agent_type", "unknown")
            agent_type_counts[agent_type] = agent_type_counts.get(agent_type, 0) + 1

        return {
            "total_templates": len(self.preset_templates),
            "agent_type_distribution": agent_type_counts,
            "available_agent_types": len(self.template_helper.AGENT_TEMPLATES)
        }
