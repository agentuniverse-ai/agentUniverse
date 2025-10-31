# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 10:30
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: prompt_optimizer.py
"""Advanced Prompt Optimizer module for intelligent prompt optimization."""

import re
import json
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
from agentuniverse.prompt.prompt_model import AgentPromptModel


class OptimizationStrategy(Enum):
    """Enumeration of optimization strategies."""
    
    CLARITY = "clarity"
    STRUCTURE = "structure"
    SPECIFICITY = "specificity"
    EFFICIENCY = "efficiency"
    COMPREHENSIVENESS = "comprehensiveness"


class PromptQualityMetric(Enum):
    """Enumeration of prompt quality metrics."""
    
    CLARITY = "clarity"
    SPECIFICITY = "specificity"
    COMPLETENESS = "completeness"
    STRUCTURE = "structure"
    TONE = "tone"


@dataclass
class OptimizationRule:
    """Represents an optimization rule.
    
    Attributes:
        name: The name of the rule.
        pattern: The regex pattern to match.
        replacement: The replacement text.
        description: Description of what the rule does.
        priority: Priority level (1-10, higher is more important).
        conditions: Additional conditions for applying the rule.
    """
    
    name: str
    pattern: str
    replacement: str
    description: str
    priority: int = 5
    conditions: Optional[Dict[str, Any]] = None


@dataclass
class QualityScore:
    """Represents a quality score for a prompt.
    
    Attributes:
        metric: The quality metric being scored.
        score: The score value (0-1).
        feedback: Feedback on the metric.
        suggestions: Suggestions for improvement.
    """
    
    metric: PromptQualityMetric
    score: float
    feedback: str
    suggestions: List[str]


@dataclass
class OptimizationResult:
    """Result of prompt optimization.
    
    Attributes:
        original_prompt: The original prompt text.
        optimized_prompt: The optimized prompt text.
        quality_scores: Quality scores for different metrics.
        improvements: List of improvements made.
        confidence_score: Overall confidence score (0-1).
        suggestions: Additional suggestions for improvement.
        optimization_strategies: Strategies used for optimization.
    """
    
    original_prompt: str
    optimized_prompt: str
    quality_scores: List[QualityScore]
    improvements: List[str]
    confidence_score: float
    suggestions: List[str]
    optimization_strategies: List[OptimizationStrategy]


class PromptOptimizer:
    """Advanced prompt optimizer with intelligent analysis and optimization.
    
    This class provides sophisticated prompt optimization capabilities including
    quality assessment, intelligent rule application, and context-aware improvements.
    """
    
    def __init__(self):
        """Initialize the PromptOptimizer."""
        self._optimization_rules = self._initialize_optimization_rules()
        self._quality_patterns = self._initialize_quality_patterns()
        self._context_keywords = self._initialize_context_keywords()
    
    def optimize_prompt(
        self, 
        prompt: AgentPromptModel,
        strategies: Optional[List[OptimizationStrategy]] = None,
        custom_rules: Optional[List[OptimizationRule]] = None
    ) -> OptimizationResult:
        """Optimize a prompt using specified strategies.
        
        Args:
            prompt: The prompt model to optimize.
            strategies: List of optimization strategies to apply.
            custom_rules: Custom optimization rules to apply.
            
        Returns:
            OptimizationResult: The optimization result.
        """
        if strategies is None:
            strategies = [OptimizationStrategy.CLARITY, OptimizationStrategy.STRUCTURE]
        
        # Analyze current quality
        quality_scores = self._analyze_prompt_quality(prompt)
        
        # Apply optimization rules
        optimized_intro = self._optimize_section(
            prompt.introduction, strategies, custom_rules
        )
        optimized_target = self._optimize_section(
            prompt.target, strategies, custom_rules
        )
        optimized_instruction = self._optimize_section(
            prompt.instruction, strategies, custom_rules
        )
        
        # Generate improvements list
        improvements = self._generate_improvements(
            prompt, optimized_intro, optimized_target, optimized_instruction
        )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(quality_scores, strategies)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            quality_scores, improvements
        )
        
        # Format results
        original_prompt = self._format_prompt(prompt)
        optimized_prompt = self._format_optimized_prompt(
            optimized_intro, optimized_target, optimized_instruction
        )
        
        return OptimizationResult(
            original_prompt=original_prompt,
            optimized_prompt=optimized_prompt,
            quality_scores=quality_scores,
            improvements=improvements,
            confidence_score=confidence_score,
            suggestions=suggestions,
            optimization_strategies=strategies
        )
    
    def analyze_prompt_quality(self, prompt: AgentPromptModel) -> List[QualityScore]:
        """Analyze the quality of a prompt.
        
        Args:
            prompt: The prompt model to analyze.
            
        Returns:
            List[QualityScore]: Quality scores for different metrics.
        """
        return self._analyze_prompt_quality(prompt)
    
    def suggest_improvements(self, prompt: AgentPromptModel) -> List[str]:
        """Suggest improvements for a prompt.
        
        Args:
            prompt: The prompt model to analyze.
            
        Returns:
            List[str]: List of improvement suggestions.
        """
        quality_scores = self._analyze_prompt_quality(prompt)
        suggestions = []
        
        for score in quality_scores:
            suggestions.extend(score.suggestions)
        
        return suggestions
    
    def _initialize_optimization_rules(self) -> List[OptimizationRule]:
        """Initialize optimization rules.
        
        Returns:
            List[OptimizationRule]: List of optimization rules.
        """
        return [
            # Clarity rules
            OptimizationRule(
                name="enhance_professional_tone",
                pattern=r"你是一个(.+?)",
                replacement=r"你是一位专业的\1",
                description="Enhance professional tone in role description",
                priority=8
            ),
            OptimizationRule(
                name="add_structure_to_instructions",
                pattern=r"请(.+?)(?=。|$)",
                replacement=r"请按照以下步骤\1",
                description="Add structure to instructions",
                priority=7
            ),
            OptimizationRule(
                name="improve_specificity",
                pattern=r"帮助(.+?)(?=。|$)",
                replacement=r"帮助\1，提供具体、可操作的解决方案",
                description="Improve specificity in target description",
                priority=6
            ),
            
            # Structure rules
            OptimizationRule(
                name="add_numbering",
                pattern=r"^(\d+\.\s*)?(.+?)(?=\n|$)",
                replacement=r"\1\2",
                description="Ensure proper numbering for list items",
                priority=5,
                conditions={"section": "instruction"}
            ),
            OptimizationRule(
                name="improve_formatting",
                pattern=r"(.+?)(?=\n\n)",
                replacement=r"\1",
                description="Improve text formatting",
                priority=4
            ),
            
            # Specificity rules
            OptimizationRule(
                name="add_examples_placeholder",
                pattern=r"(.+?)(?=。|$)",
                replacement=r"\1。例如：{example}",
                description="Add examples placeholder for better specificity",
                priority=6,
                conditions={"section": "instruction"}
            ),
            OptimizationRule(
                name="enhance_constraints",
                pattern=r"约束条件：(.+?)(?=\n|$)",
                replacement=r"约束条件：\n\1",
                description="Improve constraint formatting",
                priority=5
            ),
            
            # Efficiency rules
            OptimizationRule(
                name="remove_redundancy",
                pattern=r"(.+?)\1",
                replacement=r"\1",
                description="Remove redundant text",
                priority=7
            ),
            OptimizationRule(
                name="simplify_language",
                pattern=r"请确保(.+?)",
                replacement=r"请\1",
                description="Simplify language for better efficiency",
                priority=4
            ),
            
            # Comprehensiveness rules
            OptimizationRule(
                name="add_quality_assurance",
                pattern=r"(.+?)。$",
                replacement=r"\1。请确保回答准确、相关且易于理解。",
                description="Add quality assurance to instructions",
                priority=6
            ),
            OptimizationRule(
                name="add_context_awareness",
                pattern=r"根据(.+?)(?=。|$)",
                replacement=r"根据\1，结合具体场景和用户需求",
                description="Add context awareness",
                priority=5
            )
        ]
    
    def _initialize_quality_patterns(self) -> Dict[PromptQualityMetric, Dict[str, Any]]:
        """Initialize quality assessment patterns.
        
        Returns:
            Dict[PromptQualityMetric, Dict[str, Any]]: Quality patterns.
        """
        return {
            PromptQualityMetric.CLARITY: {
                "positive_patterns": [
                    r"明确|清晰|具体|详细",
                    r"请按照|请确保|请遵循",
                    r"步骤|方法|流程"
                ],
                "negative_patterns": [
                    r"可能|也许|大概|或许",
                    r"不清楚|模糊|不明确"
                ],
                "weight": 0.3
            },
            PromptQualityMetric.SPECIFICITY: {
                "positive_patterns": [
                    r"具体|详细|明确|精确",
                    r"例如|比如|举例",
                    r"步骤|方法|流程|规则"
                ],
                "negative_patterns": [
                    r"一般|通常|大概|可能",
                    r"简单|基础|基本"
                ],
                "weight": 0.25
            },
            PromptQualityMetric.COMPLETENESS: {
                "positive_patterns": [
                    r"介绍|目标|指令",
                    r"完整|全面|详细",
                    r"包括|涵盖|涉及"
                ],
                "negative_patterns": [
                    r"不完整|缺失|缺少"
                ],
                "weight": 0.2
            },
            PromptQualityMetric.STRUCTURE: {
                "positive_patterns": [
                    r"步骤|顺序|流程",
                    r"第一|第二|第三",
                    r"首先|然后|最后"
                ],
                "negative_patterns": [
                    r"混乱|无序|随意"
                ],
                "weight": 0.15
            },
            PromptQualityMetric.TONE: {
                "positive_patterns": [
                    r"专业|友好|礼貌",
                    r"请|谢谢|感谢"
                ],
                "negative_patterns": [
                    r"命令|强制|必须",
                    r"粗鲁|不礼貌"
                ],
                "weight": 0.1
            }
        }
    
    def _initialize_context_keywords(self) -> Dict[str, List[str]]:
        """Initialize context-specific keywords.
        
        Returns:
            Dict[str, List[str]]: Context keywords.
        """
        return {
            "technical": ["代码", "编程", "开发", "技术", "算法", "系统"],
            "business": ["商业", "管理", "营销", "销售", "客户", "市场"],
            "educational": ["教育", "学习", "教学", "培训", "知识", "课程"],
            "creative": ["创意", "设计", "艺术", "创作", "创新", "灵感"],
            "analytical": ["分析", "数据", "统计", "研究", "报告", "洞察"]
        }
    
    def _analyze_prompt_quality(self, prompt: AgentPromptModel) -> List[QualityScore]:
        """Analyze the quality of a prompt.
        
        Args:
            prompt: The prompt model to analyze.
            
        Returns:
            List[QualityScore]: Quality scores for different metrics.
        """
        quality_scores = []
        full_text = self._format_prompt(prompt)
        
        for metric, patterns in self._quality_patterns.items():
            score = self._calculate_metric_score(full_text, patterns)
            feedback = self._generate_feedback(metric, score)
            suggestions = self._generate_suggestions_for_metric(metric, score)
            
            quality_scores.append(QualityScore(
                metric=metric,
                score=score,
                feedback=feedback,
                suggestions=suggestions
            ))
        
        return quality_scores
    
    def _calculate_metric_score(self, text: str, patterns: Dict[str, Any]) -> float:
        """Calculate score for a specific quality metric.
        
        Args:
            text: The text to analyze.
            patterns: The patterns for the metric.
            
        Returns:
            float: Score between 0 and 1.
        """
        positive_score = 0
        negative_score = 0
        
        # Count positive patterns
        for pattern in patterns["positive_patterns"]:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            positive_score += matches
        
        # Count negative patterns
        for pattern in patterns["negative_patterns"]:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            negative_score += matches
        
        # Calculate final score
        total_patterns = positive_score + negative_score
        if total_patterns == 0:
            return 0.5  # Neutral score if no patterns found
        
        score = positive_score / total_patterns
        return min(max(score, 0), 1)  # Clamp between 0 and 1
    
    def _generate_feedback(self, metric: PromptQualityMetric, score: float) -> str:
        """Generate feedback for a quality metric.
        
        Args:
            metric: The quality metric.
            score: The score for the metric.
            
        Returns:
            str: Feedback text.
        """
        if score >= 0.8:
            return f"{metric.value}表现优秀，符合高质量prompt标准"
        elif score >= 0.6:
            return f"{metric.value}表现良好，有改进空间"
        elif score >= 0.4:
            return f"{metric.value}表现一般，需要改进"
        else:
            return f"{metric.value}表现较差，需要重点改进"
    
    def _generate_suggestions_for_metric(
        self, 
        metric: PromptQualityMetric, 
        score: float
    ) -> List[str]:
        """Generate suggestions for a specific metric.
        
        Args:
            metric: The quality metric.
            score: The score for the metric.
            
        Returns:
            List[str]: List of suggestions.
        """
        suggestions = []
        
        if metric == PromptQualityMetric.CLARITY and score < 0.7:
            suggestions.extend([
                "使用更清晰、具体的语言",
                "避免模糊或歧义的表达",
                "提供明确的指导步骤"
            ])
        
        if metric == PromptQualityMetric.SPECIFICITY and score < 0.7:
            suggestions.extend([
                "添加具体的示例和说明",
                "提供详细的执行步骤",
                "明确约束条件和要求"
            ])
        
        if metric == PromptQualityMetric.COMPLETENESS and score < 0.7:
            suggestions.extend([
                "确保包含所有必要的部分",
                "添加缺失的介绍、目标或指令",
                "提供完整的上下文信息"
            ])
        
        if metric == PromptQualityMetric.STRUCTURE and score < 0.7:
            suggestions.extend([
                "使用有序的步骤和流程",
                "添加编号或列表格式",
                "确保逻辑结构清晰"
            ])
        
        if metric == PromptQualityMetric.TONE and score < 0.7:
            suggestions.extend([
                "使用更专业、友好的语调",
                "避免命令式语言",
                "添加礼貌用语"
            ])
        
        return suggestions
    
    def _optimize_section(
        self, 
        section: Optional[str], 
        strategies: List[OptimizationStrategy],
        custom_rules: Optional[List[OptimizationRule]]
    ) -> str:
        """Optimize a specific section of the prompt.
        
        Args:
            section: The section text to optimize.
            strategies: Optimization strategies to apply.
            custom_rules: Custom rules to apply.
            
        Returns:
            str: Optimized section text.
        """
        if not section:
            return ""
        
        optimized = section
        
        # Apply standard rules
        applicable_rules = self._get_applicable_rules(strategies, custom_rules)
        
        for rule in applicable_rules:
            if re.search(rule.pattern, optimized):
                optimized = re.sub(rule.pattern, rule.replacement, optimized)
        
        return optimized
    
    def _get_applicable_rules(
        self, 
        strategies: List[OptimizationStrategy],
        custom_rules: Optional[List[OptimizationRule]]
    ) -> List[OptimizationRule]:
        """Get applicable optimization rules.
        
        Args:
            strategies: Optimization strategies.
            custom_rules: Custom rules.
            
        Returns:
            List[OptimizationRule]: Applicable rules.
        """
        applicable_rules = []
        
        # Add custom rules first
        if custom_rules:
            applicable_rules.extend(custom_rules)
        
        # Add standard rules based on strategies
        for rule in self._optimization_rules:
            if self._rule_applies_to_strategies(rule, strategies):
                applicable_rules.append(rule)
        
        # Sort by priority
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        return applicable_rules
    
    def _rule_applies_to_strategies(
        self, 
        rule: OptimizationRule, 
        strategies: List[OptimizationStrategy]
    ) -> bool:
        """Check if a rule applies to the given strategies.
        
        Args:
            rule: The optimization rule.
            strategies: The optimization strategies.
            
        Returns:
            bool: True if the rule applies.
        """
        # Simple mapping based on rule names
        strategy_mapping = {
            "clarity": OptimizationStrategy.CLARITY,
            "structure": OptimizationStrategy.STRUCTURE,
            "specificity": OptimizationStrategy.SPECIFICITY,
            "efficiency": OptimizationStrategy.EFFICIENCY,
            "comprehensiveness": OptimizationStrategy.COMPREHENSIVENESS
        }
        
        for strategy in strategies:
            if strategy in strategy_mapping.values():
                return True
        
        return False
    
    def _generate_improvements(
        self, 
        original: AgentPromptModel,
        optimized_intro: str,
        optimized_target: str,
        optimized_instruction: str
    ) -> List[str]:
        """Generate list of improvements made.
        
        Args:
            original: Original prompt model.
            optimized_intro: Optimized introduction.
            optimized_target: Optimized target.
            optimized_instruction: Optimized instruction.
            
        Returns:
            List[str]: List of improvements.
        """
        improvements = []
        
        if original.introduction != optimized_intro:
            improvements.append("优化了介绍部分，增强了专业性和清晰度")
        
        if original.target != optimized_target:
            improvements.append("改进了目标描述，提高了具体性和可操作性")
        
        if original.instruction != optimized_instruction:
            improvements.append("重构了指令部分，改善了结构和可读性")
        
        return improvements
    
    def _generate_suggestions(
        self, 
        quality_scores: List[QualityScore],
        strategies: List[OptimizationStrategy]
    ) -> List[str]:
        """Generate optimization suggestions.
        
        Args:
            quality_scores: Quality scores for the prompt.
            strategies: Applied optimization strategies.
            
        Returns:
            List[str]: List of suggestions.
        """
        suggestions = []
        
        # Add suggestions based on quality scores
        for score in quality_scores:
            if score.score < 0.7:
                suggestions.extend(score.suggestions)
        
        # Add strategy-specific suggestions
        if OptimizationStrategy.CLARITY in strategies:
            suggestions.append("考虑使用更简洁明了的语言表达")
        
        if OptimizationStrategy.STRUCTURE in strategies:
            suggestions.append("建议使用编号或列表来组织信息")
        
        if OptimizationStrategy.SPECIFICITY in strategies:
            suggestions.append("添加具体示例和详细说明")
        
        return list(set(suggestions))  # Remove duplicates
    
    def _calculate_confidence_score(
        self, 
        quality_scores: List[QualityScore],
        improvements: List[str]
    ) -> float:
        """Calculate overall confidence score.
        
        Args:
            quality_scores: Quality scores for the prompt.
            improvements: List of improvements made.
            
        Returns:
            float: Confidence score between 0 and 1.
        """
        if not quality_scores:
            return 0.5
        
        # Calculate average quality score
        avg_quality = sum(score.score for score in quality_scores) / len(quality_scores)
        
        # Factor in number of improvements
        improvement_factor = min(len(improvements) * 0.1, 0.3)
        
        # Calculate final confidence score
        confidence = (avg_quality * 0.7) + (improvement_factor * 0.3)
        
        return min(max(confidence, 0), 1)  # Clamp between 0 and 1
    
    def _format_prompt(self, prompt: AgentPromptModel) -> str:
        """Format prompt model as string.
        
        Args:
            prompt: The prompt model.
            
        Returns:
            str: Formatted prompt string.
        """
        parts = []
        if prompt.introduction:
            parts.append(f"介绍：{prompt.introduction}")
        if prompt.target:
            parts.append(f"目标：{prompt.target}")
        if prompt.instruction:
            parts.append(f"指令：{prompt.instruction}")
        
        return "\n\n".join(parts)
    
    def _format_optimized_prompt(
        self, 
        introduction: str, 
        target: str, 
        instruction: str
    ) -> str:
        """Format optimized prompt as string.
        
        Args:
            introduction: Optimized introduction.
            target: Optimized target.
            instruction: Optimized instruction.
            
        Returns:
            str: Formatted optimized prompt string.
        """
        parts = []
        if introduction:
            parts.append(f"介绍：{introduction}")
        if target:
            parts.append(f"目标：{target}")
        if instruction:
            parts.append(f"指令：{instruction}")
        
        return "\n\n".join(parts)
