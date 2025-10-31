# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 13:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: prompt_generation_action.py
"""Prompt generation action for the prompt toolkit demo."""

from typing import Dict, Any, Optional
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_toolkit import (
    PromptToolkit,
    PromptToolkitConfig,
    PromptGenerationRequest
)
from agentuniverse.agent.action.tool.tool import Tool


class PromptGenerationAction(Tool):
    """Action for generating prompts using the prompt toolkit.
    
    This action demonstrates how to use the PromptToolkit to generate
    high-quality prompts based on user scenarios and requirements.
    """
    
    def __init__(self):
        """Initialize the PromptGenerationAction."""
        super().__init__()
        self.toolkit = PromptToolkit()
    
    def run(self, scenario_description: str, **kwargs) -> Dict[str, Any]:
        """Generate a prompt based on scenario description.
        
        Args:
            scenario_description: Description of the scenario for prompt generation.
            **kwargs: Additional parameters including:
                - content: Additional content or requirements
                - target_audience: Target audience for the prompt
                - domain: Domain or field of application
                - constraints: List of constraints or requirements
                - examples: List of example inputs and outputs
                - tone: Desired tone for the prompt
                - complexity: Desired complexity level
                - custom_requirements: Additional custom requirements
        
        Returns:
            Dict[str, Any]: Generated prompt information and metadata.
        """
        try:
            # Create prompt generation request
            request = PromptGenerationRequest(
                scenario_description=scenario_description,
                content=kwargs.get('content'),
                target_audience=kwargs.get('target_audience'),
                domain=kwargs.get('domain'),
                constraints=kwargs.get('constraints'),
                examples=kwargs.get('examples'),
                tone=kwargs.get('tone'),
                complexity=kwargs.get('complexity'),
                custom_requirements=kwargs.get('custom_requirements')
            )
            
            # Generate prompt using toolkit
            result = self.toolkit.generate_prompt_from_request(request)
            
            # Format response
            response = {
                "success": True,
                "generated_prompt": {
                    "introduction": result.generated_prompt.introduction,
                    "target": result.generated_prompt.target,
                    "instruction": result.generated_prompt.instruction
                },
                "analysis_result": {
                    "recommended_scenario": result.analysis_result.recommended_scenario.value if result.analysis_result else None,
                    "complexity_level": result.analysis_result.complexity_level.value if result.analysis_result else None,
                    "confidence_score": result.analysis_result.confidence_score if result.analysis_result else 0.0
                },
                "optimization_result": {
                    "improvements": result.optimization_result.improvements if result.optimization_result else [],
                    "suggestions": result.optimization_result.suggestions if result.optimization_result else [],
                    "confidence_score": result.optimization_result.confidence_score if result.optimization_result else 0.0
                },
                "recommendations": result.recommendations,
                "overall_confidence": result.confidence_score,
                "metadata": result.metadata
            }
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate prompt"
            }
    
    def get_description(self) -> str:
        """Get description of the action.
        
        Returns:
            str: Description of the action.
        """
        return "Generate high-quality prompts based on user scenarios and requirements using the prompt toolkit."
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get parameters for the action.
        
        Returns:
            Dict[str, Any]: Parameter definitions.
        """
        return {
            "scenario_description": {
                "type": "string",
                "description": "Description of the scenario for prompt generation",
                "required": True
            },
            "content": {
                "type": "string",
                "description": "Additional content or requirements",
                "required": False
            },
            "target_audience": {
                "type": "string",
                "description": "Target audience for the prompt",
                "required": False
            },
            "domain": {
                "type": "string",
                "description": "Domain or field of application",
                "required": False
            },
            "constraints": {
                "type": "array",
                "description": "List of constraints or requirements",
                "required": False
            },
            "examples": {
                "type": "array",
                "description": "List of example inputs and outputs",
                "required": False
            },
            "tone": {
                "type": "string",
                "description": "Desired tone for the prompt",
                "required": False
            },
            "complexity": {
                "type": "string",
                "description": "Desired complexity level (simple, medium, complex)",
                "required": False
            },
            "custom_requirements": {
                "type": "string",
                "description": "Additional custom requirements",
                "required": False
            }
        }
