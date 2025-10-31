# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 11:30
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: prompt_toolkit.py
"""Prompt Toolkit module for comprehensive prompt management and optimization."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from agentuniverse.prompt.prompt_generator import (
    PromptGenerator, 
    PromptScenario, 
    PromptComplexity, 
    ScenarioContext
)
from agentuniverse.prompt.prompt_optimizer import (
    PromptOptimizer, 
    OptimizationStrategy, 
    OptimizationResult
)
from agentuniverse.prompt.scenario_analyzer import (
    ScenarioAnalyzer, 
    ScenarioAnalysisResult
)
from agentuniverse.prompt.prompt_model import AgentPromptModel


@dataclass
class PromptToolkitConfig:
    """Configuration for the Prompt Toolkit.
    
    Attributes:
        enable_auto_optimization: Whether to enable automatic optimization.
        default_scenario: Default scenario if none is detected.
        default_complexity: Default complexity level.
        optimization_strategies: Default optimization strategies.
        confidence_threshold: Minimum confidence threshold for recommendations.
    """
    
    enable_auto_optimization: bool = True
    default_scenario: PromptScenario = PromptScenario.CONVERSATIONAL
    default_complexity: PromptComplexity = PromptComplexity.MEDIUM
    optimization_strategies: List[OptimizationStrategy] = None
    confidence_threshold: float = 0.6
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.optimization_strategies is None:
            self.optimization_strategies = [
                OptimizationStrategy.CLARITY,
                OptimizationStrategy.STRUCTURE
            ]


@dataclass
class PromptGenerationRequest:
    """Request for prompt generation.
    
    Attributes:
        scenario_description: Description of the scenario.
        content: Additional content or requirements.
        target_audience: Target audience for the prompt.
        domain: Domain or field of application.
        constraints: List of constraints or requirements.
        examples: List of example inputs and outputs.
        tone: Desired tone for the prompt.
        complexity: Desired complexity level.
        custom_requirements: Additional custom requirements.
    """
    
    scenario_description: str
    content: Optional[str] = None
    target_audience: Optional[str] = None
    domain: Optional[str] = None
    constraints: Optional[List[str]] = None
    examples: Optional[List[Dict[str, str]]] = None
    tone: Optional[str] = None
    complexity: Optional[PromptComplexity] = None
    custom_requirements: Optional[str] = None


@dataclass
class PromptToolkitResult:
    """Result from the Prompt Toolkit.
    
    Attributes:
        generated_prompt: The generated prompt model.
        analysis_result: Scenario analysis result.
        optimization_result: Optimization result if applied.
        recommendations: List of recommendations.
        confidence_score: Overall confidence score.
        metadata: Additional metadata about the generation process.
    """
    
    generated_prompt: AgentPromptModel
    analysis_result: Optional[ScenarioAnalysisResult] = None
    optimization_result: Optional[OptimizationResult] = None
    recommendations: List[str] = None
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.recommendations is None:
            self.recommendations = []
        if self.metadata is None:
            self.metadata = {}


class PromptToolkit:
    """Comprehensive prompt management and optimization toolkit.
    
    This class provides a unified interface for prompt generation, analysis,
    and optimization, combining the capabilities of PromptGenerator,
    PromptOptimizer, and ScenarioAnalyzer.
    """
    
    def __init__(self, config: Optional[PromptToolkitConfig] = None):
        """Initialize the Prompt Toolkit.
        
        Args:
            config: Configuration for the toolkit.
        """
        self.config = config or PromptToolkitConfig()
        self.generator = PromptGenerator()
        self.optimizer = PromptOptimizer()
        self.analyzer = ScenarioAnalyzer()
    
    def generate_prompt_from_request(
        self, 
        request: PromptGenerationRequest
    ) -> PromptToolkitResult:
        """Generate a prompt from a request.
        
        Args:
            request: The prompt generation request.
            
        Returns:
            PromptToolkitResult: The generation result.
        """
        # Analyze the scenario
        analysis_result = self.analyzer.analyze_scenario(
            request.scenario_description,
            {
                "content": request.content,
                "target_audience": request.target_audience,
                "domain": request.domain
            }
        )
        
        # Extract context from analysis
        context = self.analyzer.extract_context_from_content(
            request.scenario_description
        )
        
        # Override with explicit request values
        if request.target_audience:
            context.target_audience = request.target_audience
        if request.domain:
            context.domain = request.domain
        if request.constraints:
            context.constraints = request.constraints
        if request.examples:
            context.examples = request.examples
        if request.tone:
            context.tone = request.tone
        
        # Determine scenario and complexity
        scenario = analysis_result.recommended_scenario
        complexity = request.complexity or analysis_result.complexity_level
        
        # Generate the prompt
        generated_prompt = self.generator.generate_prompt(
            scenario=scenario,
            context=context,
            complexity=complexity,
            custom_requirements=request.custom_requirements
        )
        
        # Apply optimization if enabled
        optimization_result = None
        if self.config.enable_auto_optimization:
            optimization_result = self.optimizer.optimize_prompt(
                generated_prompt,
                strategies=self.config.optimization_strategies
            )
            # Update the generated prompt with optimized version
            generated_prompt = AgentPromptModel(
                introduction=optimization_result.optimized_prompt.split("介绍：")[1].split("\n\n")[0] if "介绍：" in optimization_result.optimized_prompt else generated_prompt.introduction,
                target=optimization_result.optimized_prompt.split("目标：")[1].split("\n\n")[0] if "目标：" in optimization_result.optimized_prompt else generated_prompt.target,
                instruction=optimization_result.optimized_prompt.split("指令：")[1] if "指令：" in optimization_result.optimized_prompt else generated_prompt.instruction
            )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            analysis_result, optimization_result, generated_prompt
        )
        
        # Calculate overall confidence score
        confidence_score = self._calculate_overall_confidence(
            analysis_result, optimization_result
        )
        
        # Prepare metadata
        metadata = {
            "scenario": scenario.value,
            "complexity": complexity.value,
            "optimization_applied": self.config.enable_auto_optimization,
            "strategies_used": [s.value for s in self.config.optimization_strategies] if self.config.enable_auto_optimization else []
        }
        
        return PromptToolkitResult(
            generated_prompt=generated_prompt,
            analysis_result=analysis_result,
            optimization_result=optimization_result,
            recommendations=recommendations,
            confidence_score=confidence_score,
            metadata=metadata
        )
    
    def optimize_existing_prompt(
        self, 
        prompt: AgentPromptModel,
        strategies: Optional[List[OptimizationStrategy]] = None
    ) -> OptimizationResult:
        """Optimize an existing prompt.
        
        Args:
            prompt: The prompt to optimize.
            strategies: Optimization strategies to apply.
            
        Returns:
            OptimizationResult: The optimization result.
        """
        return self.optimizer.optimize_prompt(
            prompt, 
            strategies or self.config.optimization_strategies
        )
    
    def analyze_prompt_quality(self, prompt: AgentPromptModel) -> Dict[str, Any]:
        """Analyze the quality of a prompt.
        
        Args:
            prompt: The prompt to analyze.
            
        Returns:
            Dict[str, Any]: Quality analysis results.
        """
        quality_scores = self.optimizer.analyze_prompt_quality(prompt)
        
        return {
            "quality_scores": [
                {
                    "metric": score.metric.value,
                    "score": score.score,
                    "feedback": score.feedback,
                    "suggestions": score.suggestions
                }
                for score in quality_scores
            ],
            "overall_score": sum(score.score for score in quality_scores) / len(quality_scores),
            "recommendations": self.optimizer.suggest_improvements(prompt)
        }
    
    def batch_generate_prompts(
        self, 
        requests: List[PromptGenerationRequest]
    ) -> List[PromptToolkitResult]:
        """Generate multiple prompts in batch.
        
        Args:
            requests: List of prompt generation requests.
            
        Returns:
            List[PromptToolkitResult]: List of generation results.
        """
        results = []
        
        for request in requests:
            try:
                result = self.generate_prompt_from_request(request)
                results.append(result)
            except Exception as e:
                # Create error result
                error_result = PromptToolkitResult(
                    generated_prompt=AgentPromptModel(),
                    recommendations=[f"生成失败: {str(e)}"],
                    confidence_score=0.0,
                    metadata={"error": str(e)}
                )
                results.append(error_result)
        
        return results
    
    def compare_prompts(
        self, 
        prompt1: AgentPromptModel, 
        prompt2: AgentPromptModel
    ) -> Dict[str, Any]:
        """Compare two prompts.
        
        Args:
            prompt1: First prompt to compare.
            prompt2: Second prompt to compare.
            
        Returns:
            Dict[str, Any]: Comparison results.
        """
        # Analyze both prompts
        analysis1 = self.analyze_prompt_quality(prompt1)
        analysis2 = self.analyze_prompt_quality(prompt2)
        
        # Compare quality scores
        comparison = {
            "prompt1_score": analysis1["overall_score"],
            "prompt2_score": analysis2["overall_score"],
            "better_prompt": "prompt1" if analysis1["overall_score"] > analysis2["overall_score"] else "prompt2",
            "score_difference": abs(analysis1["overall_score"] - analysis2["overall_score"]),
            "detailed_comparison": {
                "prompt1": analysis1,
                "prompt2": analysis2
            }
        }
        
        return comparison
    
    def export_prompt_config(
        self, 
        prompt: AgentPromptModel, 
        format_type: str = "yaml"
    ) -> str:
        """Export prompt as configuration file.
        
        Args:
            prompt: The prompt to export.
            format_type: Export format (yaml, json).
            
        Returns:
            str: Exported configuration.
        """
        if format_type.lower() == "yaml":
            return self._export_as_yaml(prompt)
        elif format_type.lower() == "json":
            return self._export_as_json(prompt)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _generate_recommendations(
        self,
        analysis_result: ScenarioAnalysisResult,
        optimization_result: Optional[OptimizationResult],
        generated_prompt: AgentPromptModel
    ) -> List[str]:
        """Generate recommendations based on analysis and optimization.
        
        Args:
            analysis_result: Scenario analysis result.
            optimization_result: Optimization result if applied.
            generated_prompt: The generated prompt.
            
        Returns:
            List[str]: List of recommendations.
        """
        recommendations = []
        
        # Add analysis-based recommendations
        if analysis_result.confidence_score < self.config.confidence_threshold:
            recommendations.append("建议提供更多上下文信息以提高prompt质量")
        
        recommendations.extend(analysis_result.suggestions)
        
        # Add optimization-based recommendations
        if optimization_result:
            recommendations.extend(optimization_result.suggestions)
        
        # Add prompt-specific recommendations
        if not generated_prompt.introduction:
            recommendations.append("建议添加清晰的介绍部分")
        
        if not generated_prompt.target:
            recommendations.append("建议添加明确的目标描述")
        
        if not generated_prompt.instruction:
            recommendations.append("建议添加详细的执行指令")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_overall_confidence(
        self,
        analysis_result: ScenarioAnalysisResult,
        optimization_result: Optional[OptimizationResult]
    ) -> float:
        """Calculate overall confidence score.
        
        Args:
            analysis_result: Scenario analysis result.
            optimization_result: Optimization result if applied.
            
        Returns:
            float: Overall confidence score.
        """
        base_confidence = analysis_result.confidence_score
        
        if optimization_result:
            # Combine analysis and optimization confidence
            optimization_confidence = optimization_result.confidence_score
            return (base_confidence * 0.6) + (optimization_confidence * 0.4)
        
        return base_confidence
    
    def _export_as_yaml(self, prompt: AgentPromptModel) -> str:
        """Export prompt as YAML configuration.
        
        Args:
            prompt: The prompt to export.
            
        Returns:
            str: YAML configuration.
        """
        yaml_content = []
        
        if prompt.introduction:
            yaml_content.append(f"introduction: {prompt.introduction}")
        
        if prompt.target:
            yaml_content.append(f"target: {prompt.target}")
        
        if prompt.instruction:
            yaml_content.append(f"instruction: |\n  {prompt.instruction.replace(chr(10), chr(10) + '  ')}")
        
        yaml_content.append("metadata:")
        yaml_content.append("  type: 'PROMPT'")
        yaml_content.append("  version: 'auto_generated'")
        
        return "\n".join(yaml_content)
    
    def _export_as_json(self, prompt: AgentPromptModel) -> str:
        """Export prompt as JSON configuration.
        
        Args:
            prompt: The prompt to export.
            
        Returns:
            str: JSON configuration.
        """
        import json
        
        config = {
            "introduction": prompt.introduction,
            "target": prompt.target,
            "instruction": prompt.instruction,
            "metadata": {
                "type": "PROMPT",
                "version": "auto_generated"
            }
        }
        
        return json.dumps(config, ensure_ascii=False, indent=2)
