# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 13:15
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: prompt_optimization_action.py
"""Prompt optimization action for the prompt toolkit demo."""

from typing import Dict, Any
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_toolkit import PromptToolkit
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_optimizer import OptimizationStrategy
from agentuniverse.prompt.prompt_model import AgentPromptModel
from agentuniverse.agent.action.tool.tool import Tool


class PromptOptimizationAction(Tool):
    """Action for optimizing existing prompts using the prompt toolkit.
    
    This action demonstrates how to use the PromptToolkit to optimize
    existing prompts and improve their quality.
    """
    
    def __init__(self):
        """Initialize the PromptOptimizationAction."""
        super().__init__()
        self.toolkit = PromptToolkit()
    
    def run(
        self, 
        introduction: str, 
        target: str, 
        instruction: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Optimize an existing prompt.
        
        Args:
            introduction: The introduction section of the prompt.
            target: The target section of the prompt.
            instruction: The instruction section of the prompt.
            **kwargs: Additional parameters including:
                - strategies: List of optimization strategies to apply
                - custom_rules: Custom optimization rules
        
        Returns:
            Dict[str, Any]: Optimization result and suggestions.
        """
        try:
            # Create prompt model from input
            prompt = AgentPromptModel(
                introduction=introduction,
                target=target,
                instruction=instruction
            )
            
            # Get optimization strategies
            strategies = kwargs.get('strategies', [OptimizationStrategy.CLARITY, OptimizationStrategy.STRUCTURE])
            if isinstance(strategies, list):
                # Convert string strategies to enum if needed
                strategy_enums = []
                for strategy in strategies:
                    if isinstance(strategy, str):
                        strategy_enums.append(OptimizationStrategy(strategy))
                    else:
                        strategy_enums.append(strategy)
                strategies = strategy_enums
            
            # Optimize prompt using toolkit
            result = self.toolkit.optimize_existing_prompt(prompt, strategies)
            
            # Analyze quality
            quality_analysis = self.toolkit.analyze_prompt_quality(prompt)
            
            # Format response
            response = {
                "success": True,
                "original_prompt": {
                    "introduction": prompt.introduction,
                    "target": prompt.target,
                    "instruction": prompt.instruction
                },
                "optimized_prompt": {
                    "introduction": self._extract_section(result.optimized_prompt, "介绍："),
                    "target": self._extract_section(result.optimized_prompt, "目标："),
                    "instruction": self._extract_section(result.optimized_prompt, "指令：")
                },
                "optimization_result": {
                    "improvements": result.improvements,
                    "suggestions": result.suggestions,
                    "confidence_score": result.confidence_score,
                    "strategies_used": [s.value for s in result.optimization_strategies]
                },
                "quality_analysis": {
                    "overall_score": quality_analysis["overall_score"],
                    "quality_scores": quality_analysis["quality_scores"],
                    "recommendations": quality_analysis["recommendations"]
                }
            }
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to optimize prompt"
            }
    
    def _extract_section(self, formatted_prompt: str, section_name: str) -> str:
        """Extract a specific section from formatted prompt.
        
        Args:
            formatted_prompt: The formatted prompt string.
            section_name: The name of the section to extract.
            
        Returns:
            str: The extracted section content.
        """
        try:
            if section_name in formatted_prompt:
                # Find the section and extract content
                start_idx = formatted_prompt.find(section_name) + len(section_name)
                # Find the next section or end of string
                next_section_idx = len(formatted_prompt)
                for next_section in ["介绍：", "目标：", "指令："]:
                    if next_section != section_name:
                        idx = formatted_prompt.find(next_section, start_idx)
                        if idx != -1 and idx < next_section_idx:
                            next_section_idx = idx
                
                content = formatted_prompt[start_idx:next_section_idx].strip()
                return content
            return ""
        except Exception:
            return ""
    
    def get_description(self) -> str:
        """Get description of the action.
        
        Returns:
            str: Description of the action.
        """
        return "Optimize existing prompts to improve their quality, clarity, and effectiveness."
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get parameters for the action.
        
        Returns:
            Dict[str, Any]: Parameter definitions.
        """
        return {
            "introduction": {
                "type": "string",
                "description": "The introduction section of the prompt",
                "required": True
            },
            "target": {
                "type": "string",
                "description": "The target section of the prompt",
                "required": True
            },
            "instruction": {
                "type": "string",
                "description": "The instruction section of the prompt",
                "required": True
            },
            "strategies": {
                "type": "array",
                "description": "List of optimization strategies to apply",
                "required": False,
                "default": ["clarity", "structure"]
            }
        }
