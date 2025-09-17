# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: prompt_service.py
"""Prompt Generation Service.

Provides core prompt generation service functionality for prompt_generator_app.
This service layer encapsulates the core logic for prompt generation, optimization,
and configuration management.
"""
import os
import sys
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root directory to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agentuniverse.prompt.prompt_generator_helper import (
    PromptTemplateHelper,
    generate_prompt_config,
    optimize_existing_prompt
)


class PromptGenerationService:
    """Prompt Generation Service class.

    Provides comprehensive prompt generation, optimization and management functionality.
    Suitable for business logic encapsulation in this sample application.
    """

    def __init__(self):
        """Initialize the prompt generation service."""
        self.supported_types = list(PromptTemplateHelper.AGENT_TEMPLATES.keys())

    def generate_agent_prompt(self, agent_type: str, task_description: str,
                             scenario: Optional[str] = None) -> Dict[str, Any]:
        """Generate agent prompt configuration.

        Args:
            agent_type: Type of the agent.
            task_description: Description of the task.
            scenario: Optional scenario description.

        Returns:
            Generated prompt configuration.

        Raises:
            ValueError: If agent_type is not supported.
            Exception: If generation fails.
        """
        try:
            # Call core generation function
            config = generate_prompt_config(
                task_description=task_description,
                agent_type=agent_type,
                scenario=scenario,
                output_file=None  # Do not write to file, return config directly
            )

            return {
                "status": "success",
                "config": config,
                "agent_type": agent_type,
                "task_description": task_description,
                "scenario": scenario
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_type": agent_type,
                "task_description": task_description
            }

    def optimize_prompt(self, existing_prompt: str, optimization_goal: str,
                       agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Optimize existing prompt.

        Args:
            existing_prompt: Existing prompt content.
            optimization_goal: Optimization goal.
            agent_type: Optional agent type.

        Returns:
            Optimized prompt and analysis results.

        Raises:
            ValueError: If input parameters are invalid.
            Exception: If optimization fails.
        """
        try:
            # Call core optimization function
            result = optimize_existing_prompt(
                existing_prompt_text=existing_prompt,
                optimization_goal=optimization_goal,
                agent_type=agent_type
            )

            return {
                "status": "success",
                "result": result,
                "original_prompt": existing_prompt,
                "optimization_goal": optimization_goal
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "original_prompt": existing_prompt,
                "optimization_goal": optimization_goal
            }

    def get_supported_agent_types(self) -> List[str]:
        """Get list of supported agent types.

        Returns:
            List of supported agent types.
        """
        return self.supported_types

    def validate_prompt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate prompt configuration validity.

        Args:
            config: Prompt configuration to validate.

        Returns:
            Validation results with details.
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        # Check required fields
        required_fields = ["introduction", "target", "instruction", "metadata"]
        for field in required_fields:
            if field not in config:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False

        # Check field types
        if "metadata" in config:
            if not isinstance(config["metadata"], dict):
                validation_result["errors"].append("metadata must be a dictionary")
                validation_result["is_valid"] = False
            elif "type" not in config["metadata"]:
                validation_result["warnings"].append("metadata.type field recommended")

        return validation_result

    def save_prompt_config(self, config: Dict[str, Any], output_path: str) -> str:
        """Save prompt configuration to file.

        Args:
            config: Prompt configuration to save.
            output_path: Output file path.

        Returns:
            Path of the saved file.

        Raises:
            IOError: If file writing fails.
            ValueError: If config is invalid.
        """
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # Validate config before saving
            validation = self.validate_prompt_config(config)
            if not validation["is_valid"]:
                raise ValueError(f"Invalid config: {validation['errors']}")

            # Write YAML file
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)

            return output_path
        except Exception as e:
            raise IOError(f"Failed to save config to {output_path}: {str(e)}")

    def batch_generate_prompts(self, tasks: List[Dict[str, str]]) -> Dict[str, Any]:
        """Batch generate prompts.

        Args:
            tasks: List of task configurations for batch processing.

        Returns:
            Batch processing results with statistics.
        """
        results = []

        for i, task in enumerate(tasks):
            try:
                result = self.generate_agent_prompt(
                    agent_type=task.get("agent_type", "react"),
                    task_description=task.get("task_description", ""),
                    scenario=task.get("scenario")
                )
                results.append({
                    "index": i,
                    "task": task,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "task": task,
                    "result": {
                        "status": "error",
                        "error": str(e)
                    }
                })

        successful = sum(1 for r in results if r["result"]["status"] == "success")

        return {
            "total": len(tasks),
            "successful": successful,
            "failed": len(tasks) - successful,
            "results": results
        }
