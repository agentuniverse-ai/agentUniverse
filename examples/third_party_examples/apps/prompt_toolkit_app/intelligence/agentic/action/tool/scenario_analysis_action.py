# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 13:30
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: scenario_analysis_action.py
"""Scenario analysis action for the prompt toolkit demo."""

from typing import Any

from agentuniverse.agent.action.tool.tool import Tool
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.scenario_analyzer import (
    ScenarioAnalyzer,
)


class ScenarioAnalysisAction(Tool):
    """Action for analyzing user scenarios and extracting context information.
    
    This action demonstrates how to use the ScenarioAnalyzer to analyze
    user scenarios and extract relevant context information for prompt generation.
    """
    
    def execute(
        self,
        scenario_description: str,
        content: str | None = None,
        target_audience: str | None = None,
        domain: str | None = None,
        user_role: str | None = None,
    ) -> dict[str, Any]:
        """Analyze a scenario and extract context information.
        
        Args:
            scenario_description: Description of the scenario to analyze.
            content: Additional content to analyze.
            target_audience: Target audience information.
            domain: Domain or field information.
            user_role: User role information.
        
        Returns:
            Dict[str, Any]: Analysis result and extracted context.
        """
        try:
            analyzer = ScenarioAnalyzer()

            # Prepare additional context
            additional_context = {}
            if content:
                additional_context["content"] = content
            if target_audience:
                additional_context["target_audience"] = target_audience
            if domain:
                additional_context["domain"] = domain
            if user_role:
                additional_context["user_role"] = user_role
            
            # Analyze scenario
            analysis_result = analyzer.analyze_scenario(
                scenario_description, 
                additional_context if additional_context else None
            )
            
            # Extract context
            context = analyzer.extract_context_from_content(scenario_description)
            
            # Format response
            response = {
                "success": True,
                "analysis_result": {
                    "recommended_scenario": analysis_result.recommended_scenario.value,
                    "complexity_level": analysis_result.complexity_level.value,
                    "confidence_score": analysis_result.confidence_score,
                    "suggestions": analysis_result.suggestions
                },
                "extracted_context": {
                    "domain": context.domain,
                    "user_role": context.user_role,
                    "target_audience": context.target_audience,
                    "tone": context.tone,
                    "constraints": context.constraints,
                    "examples": context.examples
                },
                "extracted_contexts": [
                    {
                        "context_type": ctx.context_type.value,
                        "value": ctx.value,
                        "confidence": ctx.confidence.value,
                        "source": ctx.source,
                        "suggestions": ctx.suggestions
                    }
                    for ctx in analysis_result.extracted_contexts
                ]
            }
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to analyze scenario"
            }
    
    def get_description(self) -> str:
        """Get description of the action.
        
        Returns:
            str: Description of the action.
        """
        return "Analyze user scenarios and extract context information for prompt generation."
    
    def get_parameters(self) -> dict[str, Any]:
        """Get parameters for the action.
        
        Returns:
            Dict[str, Any]: Parameter definitions.
        """
        return {
            "scenario_description": {
                "type": "string",
                "description": "Description of the scenario to analyze",
                "required": True
            },
            "content": {
                "type": "string",
                "description": "Additional content to analyze",
                "required": False
            },
            "target_audience": {
                "type": "string",
                "description": "Target audience information",
                "required": False
            },
            "domain": {
                "type": "string",
                "description": "Domain or field information",
                "required": False
            },
            "user_role": {
                "type": "string",
                "description": "User role information",
                "required": False
            }
        }
