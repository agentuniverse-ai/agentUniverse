# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 10:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: prompt_generator.py
"""Prompt Generator module for automatic prompt generation and optimization."""

import re
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from agentuniverse.prompt.prompt_model import AgentPromptModel


class PromptScenario(Enum):
    """Enumeration of supported prompt scenarios."""
    
    CONVERSATIONAL = "conversational"
    TASK_ORIENTED = "task_oriented"
    REASONING = "reasoning"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    TECHNICAL = "technical"
    CUSTOMER_SERVICE = "customer_service"
    EDUCATIONAL = "educational"
    RESEARCH = "research"
    CODE_GENERATION = "code_generation"


class PromptComplexity(Enum):
    """Enumeration of prompt complexity levels."""
    
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


@dataclass
class ScenarioContext:
    """Context information for prompt generation.
    
    Attributes:
        domain: The domain or field of application.
        user_role: The role of the user (e.g., student, developer, analyst).
        target_audience: The intended audience for the response.
        constraints: Any specific constraints or requirements.
        examples: Example inputs and expected outputs.
        tone: The desired tone (formal, casual, technical, etc.).
    """
    
    domain: str
    user_role: str
    target_audience: str
    constraints: List[str]
    examples: List[Dict[str, str]]
    tone: str = "professional"


@dataclass
class PromptOptimizationResult:
    """Result of prompt optimization.
    
    Attributes:
        original_prompt: The original prompt text.
        optimized_prompt: The optimized prompt text.
        improvements: List of improvements made.
        confidence_score: Confidence score for the optimization (0-1).
        suggestions: Additional suggestions for further improvement.
    """
    
    original_prompt: str
    optimized_prompt: str
    improvements: List[str]
    confidence_score: float
    suggestions: List[str]


class PromptGenerator:
    """Intelligent prompt generator and optimizer.
    
    This class provides functionality to automatically generate and optimize
    prompts based on user scenarios and content requirements.
    """
    
    def __init__(self):
        """Initialize the PromptGenerator."""
        self._scenario_templates = self._initialize_scenario_templates()
        self._optimization_rules = self._initialize_optimization_rules()
    
    def generate_prompt(
        self,
        scenario: PromptScenario,
        context: ScenarioContext,
        complexity: PromptComplexity = PromptComplexity.MEDIUM,
        custom_requirements: Optional[str] = None
    ) -> AgentPromptModel:
        """Generate a prompt based on scenario and context.
        
        Args:
            scenario: The type of scenario for the prompt.
            context: Context information including domain, user role, etc.
            complexity: The complexity level of the prompt.
            custom_requirements: Additional custom requirements.
            
        Returns:
            AgentPromptModel: Generated prompt model.
            
        Raises:
            ValueError: If scenario or context is invalid.
        """
        if not isinstance(scenario, PromptScenario):
            raise ValueError(f"Invalid scenario: {scenario}")
        
        if not isinstance(context, ScenarioContext):
            raise ValueError(f"Invalid context: {context}")
        
        # Get base template for the scenario
        base_template = self._scenario_templates.get(scenario)
        if not base_template:
            raise ValueError(f"No template found for scenario: {scenario}")
        
        # Generate introduction
        introduction = self._generate_introduction(scenario, context, complexity)
        
        # Generate target
        target = self._generate_target(scenario, context, complexity)
        
        # Generate instruction
        instruction = self._generate_instruction(
            scenario, context, complexity, base_template, custom_requirements
        )
        
        return AgentPromptModel(
            introduction=introduction,
            target=target,
            instruction=instruction
        )
    
    def optimize_prompt(self, prompt: AgentPromptModel) -> PromptOptimizationResult:
        """Optimize an existing prompt.
        
        Args:
            prompt: The prompt model to optimize.
            
        Returns:
            PromptOptimizationResult: The optimization result.
        """
        improvements = []
        suggestions = []
        
        # Optimize introduction
        optimized_introduction = self._optimize_introduction(prompt.introduction)
        if optimized_introduction != prompt.introduction:
            improvements.append("Improved introduction clarity and structure")
        
        # Optimize target
        optimized_target = self._optimize_target(prompt.target)
        if optimized_target != prompt.target:
            improvements.append("Enhanced target specificity and focus")
        
        # Optimize instruction
        optimized_instruction = self._optimize_instruction(prompt.instruction)
        if optimized_instruction != prompt.instruction:
            improvements.append("Refined instruction structure and clarity")
        
        # Generate suggestions
        suggestions = self._generate_optimization_suggestions(prompt)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            prompt, optimized_introduction, optimized_target, optimized_instruction
        )
        
        return PromptOptimizationResult(
            original_prompt=self._format_prompt(prompt),
            optimized_prompt=self._format_optimized_prompt(
                optimized_introduction, optimized_target, optimized_instruction
            ),
            improvements=improvements,
            confidence_score=confidence_score,
            suggestions=suggestions
        )
    
    def analyze_scenario(self, content: str, context: ScenarioContext) -> PromptScenario:
        """Analyze content and context to determine the best scenario.
        
        Args:
            content: The content to analyze.
            context: The context information.
            
        Returns:
            PromptScenario: The recommended scenario type.
        """
        # Simple keyword-based analysis (can be enhanced with ML models)
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ['代码', '编程', '开发', 'code', 'programming']):
            return PromptScenario.CODE_GENERATION
        elif any(keyword in content_lower for keyword in ['分析', '数据', '统计', 'analysis', 'data']):
            return PromptScenario.ANALYTICAL
        elif any(keyword in content_lower for keyword in ['创意', '创作', 'creative', 'design']):
            return PromptScenario.CREATIVE
        elif any(keyword in content_lower for keyword in ['推理', '逻辑', 'reasoning', 'logic']):
            return PromptScenario.REASONING
        elif any(keyword in content_lower for keyword in ['客服', '服务', 'customer', 'service']):
            return PromptScenario.CUSTOMER_SERVICE
        elif any(keyword in content_lower for keyword in ['教育', '学习', 'education', 'learning']):
            return PromptScenario.EDUCATIONAL
        elif any(keyword in content_lower for keyword in ['研究', '调查', 'research', 'investigation']):
            return PromptScenario.RESEARCH
        else:
            return PromptScenario.CONVERSATIONAL
    
    def _initialize_scenario_templates(self) -> Dict[PromptScenario, Dict[str, str]]:
        """Initialize scenario-specific templates.
        
        Returns:
            Dict[PromptScenario, Dict[str, str]]: Template dictionary.
        """
        return {
            PromptScenario.CONVERSATIONAL: {
                "introduction_pattern": "你是一个{role}，专门帮助{audience}解决{domain}相关的问题。",
                "target_pattern": "你的目标是提供准确、有用的信息，帮助用户解决他们的问题。",
                "instruction_pattern": "请以{tone}的语气回答用户的问题，确保回答准确、相关且易于理解。"
            },
            PromptScenario.TASK_ORIENTED: {
                "introduction_pattern": "你是一个专业的{domain}专家，擅长处理各种{domain}相关的任务。",
                "target_pattern": "你的目标是高效、准确地完成用户指定的任务。",
                "instruction_pattern": "请按照以下步骤完成任务：1. 理解任务要求 2. 制定执行计划 3. 逐步执行 4. 验证结果。"
            },
            PromptScenario.REASONING: {
                "introduction_pattern": "你是一个逻辑推理专家，擅长分析和解决复杂问题。",
                "target_pattern": "你的目标是通过系统性的推理过程，为用户提供清晰、逻辑严密的解决方案。",
                "instruction_pattern": "请使用结构化思维，逐步分析问题，展示你的推理过程，并得出合理的结论。"
            },
            PromptScenario.CREATIVE: {
                "introduction_pattern": "你是一个创意专家，拥有丰富的{domain}经验和创新思维。",
                "target_pattern": "你的目标是激发创意，提供新颖、有价值的想法和解决方案。",
                "instruction_pattern": "请发挥你的创造力，从多个角度思考问题，提供独特且实用的创意方案。"
            },
            PromptScenario.ANALYTICAL: {
                "introduction_pattern": "你是一个数据分析专家，擅长从数据中提取洞察。",
                "target_pattern": "你的目标是通过深入分析，为用户提供基于数据的专业见解。",
                "instruction_pattern": "请使用数据分析方法，提供结构化的分析结果，包括关键发现和建议。"
            },
            PromptScenario.TECHNICAL: {
                "introduction_pattern": "你是一个{domain}技术专家，拥有深厚的技术背景。",
                "target_pattern": "你的目标是提供准确、专业的技术解决方案。",
                "instruction_pattern": "请使用专业术语，提供详细的技术说明和实现方案。"
            },
            PromptScenario.CUSTOMER_SERVICE: {
                "introduction_pattern": "你是一个专业的客服代表，专门处理{domain}相关的客户咨询。",
                "target_pattern": "你的目标是提供优质的服务，解决客户问题，提升客户满意度。",
                "instruction_pattern": "请以友好、专业的态度回答客户问题，确保客户得到满意的解决方案。"
            },
            PromptScenario.EDUCATIONAL: {
                "introduction_pattern": "你是一个{domain}教育专家，擅长将复杂概念简化为易懂的内容。",
                "target_pattern": "你的目标是帮助{audience}学习和理解{domain}相关知识。",
                "instruction_pattern": "请使用清晰、易懂的语言，提供结构化的教学内容，确保学习者能够有效理解。"
            },
            PromptScenario.RESEARCH: {
                "introduction_pattern": "你是一个{domain}研究专家，擅长深入分析和研究。",
                "target_pattern": "你的目标是提供全面、深入的研究分析，帮助用户获得专业见解。",
                "instruction_pattern": "请提供详细的研究分析，包括背景、方法、发现和结论。"
            },
            PromptScenario.CODE_GENERATION: {
                "introduction_pattern": "你是一个专业的软件工程师，擅长编写高质量的代码。",
                "target_pattern": "你的目标是生成清晰、高效、可维护的代码。",
                "instruction_pattern": "请提供完整的代码实现，包括注释和文档，确保代码质量和可读性。"
            }
        }
    
    def _initialize_optimization_rules(self) -> List[Dict[str, Any]]:
        """Initialize optimization rules for prompt improvement.
        
        Returns:
            List[Dict[str, Any]]: List of optimization rules.
        """
        return [
            {
                "pattern": r"你是一个(.+?)",
                "replacement": r"你是一位专业的\1",
                "description": "Enhance professional tone"
            },
            {
                "pattern": r"请(.+?)",
                "replacement": r"请按照以下要求\1",
                "description": "Add structure to instructions"
            },
            {
                "pattern": r"(.+?)。$",
                "replacement": r"\1。请确保回答准确、相关且易于理解。",
                "description": "Add quality assurance"
            }
        ]
    
    def _generate_introduction(
        self, 
        scenario: PromptScenario, 
        context: ScenarioContext, 
        complexity: PromptComplexity
    ) -> str:
        """Generate introduction based on scenario and context.
        
        Args:
            scenario: The prompt scenario.
            context: The context information.
            complexity: The complexity level.
            
        Returns:
            str: Generated introduction.
        """
        template = self._scenario_templates[scenario]["introduction_pattern"]
        
        # Adjust based on complexity
        if complexity == PromptComplexity.SIMPLE:
            role = f"{context.domain}助手"
        elif complexity == PromptComplexity.COMPLEX:
            role = f"资深{context.domain}专家"
        else:
            role = f"{context.domain}专家"
        
        return template.format(
            role=role,
            audience=context.target_audience,
            domain=context.domain
        )
    
    def _generate_target(
        self, 
        scenario: PromptScenario, 
        context: ScenarioContext, 
        complexity: PromptComplexity
    ) -> str:
        """Generate target based on scenario and context.
        
        Args:
            scenario: The prompt scenario.
            context: The context information.
            complexity: The complexity level.
            
        Returns:
            str: Generated target.
        """
        template = self._scenario_templates[scenario]["target_pattern"]
        
        # Add complexity-specific enhancements
        if complexity == PromptComplexity.COMPLEX:
            template += " 请提供深入、全面的分析和解决方案。"
        elif complexity == PromptComplexity.SIMPLE:
            template += " 请提供简洁、易懂的回答。"
        
        return template
    
    def _generate_instruction(
        self, 
        scenario: PromptScenario, 
        context: ScenarioContext, 
        complexity: PromptComplexity,
        base_template: Dict[str, str],
        custom_requirements: Optional[str]
    ) -> str:
        """Generate instruction based on scenario and context.
        
        Args:
            scenario: The prompt scenario.
            context: The context information.
            complexity: The complexity level.
            base_template: Base template for the scenario.
            custom_requirements: Custom requirements.
            
        Returns:
            str: Generated instruction.
        """
        template = base_template["instruction_pattern"]
        
        # Format with context
        instruction = template.format(
            tone=context.tone,
            domain=context.domain,
            audience=context.target_audience
        )
        
        # Add constraints
        if context.constraints:
            instruction += "\n\n约束条件：\n"
            for constraint in context.constraints:
                instruction += f"- {constraint}\n"
        
        # Add examples
        if context.examples:
            instruction += "\n\n示例：\n"
            for i, example in enumerate(context.examples, 1):
                instruction += f"{i}. 输入：{example.get('input', '')}\n"
                instruction += f"   输出：{example.get('output', '')}\n"
        
        # Add custom requirements
        if custom_requirements:
            instruction += f"\n\n特殊要求：\n{custom_requirements}"
        
        return instruction
    
    def _optimize_introduction(self, introduction: Optional[str]) -> str:
        """Optimize the introduction section.
        
        Args:
            introduction: The original introduction.
            
        Returns:
            str: Optimized introduction.
        """
        if not introduction:
            return ""
        
        # Apply optimization rules
        optimized = introduction
        for rule in self._optimization_rules:
            if re.search(rule["pattern"], optimized):
                optimized = re.sub(rule["pattern"], rule["replacement"], optimized)
        
        return optimized
    
    def _optimize_target(self, target: Optional[str]) -> str:
        """Optimize the target section.
        
        Args:
            target: The original target.
            
        Returns:
            str: Optimized target.
        """
        if not target:
            return ""
        
        # Add specificity if missing
        if "目标" not in target and "goal" not in target.lower():
            target = f"你的目标是：{target}"
        
        return target
    
    def _optimize_instruction(self, instruction: Optional[str]) -> str:
        """Optimize the instruction section.
        
        Args:
            instruction: The original instruction.
            
        Returns:
            str: Optimized instruction.
        """
        if not instruction:
            return ""
        
        # Structure the instruction better
        lines = instruction.split('\n')
        structured_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Add numbering for list items
                if line.startswith(('-', '•', '1.', '2.', '3.')):
                    if not line.startswith(('1.', '2.', '3.')):
                        line = f"• {line.lstrip('-• ')}"
                structured_lines.append(line)
        
        return '\n'.join(structured_lines)
    
    def _generate_optimization_suggestions(self, prompt: AgentPromptModel) -> List[str]:
        """Generate optimization suggestions for a prompt.
        
        Args:
            prompt: The prompt model to analyze.
            
        Returns:
            List[str]: List of optimization suggestions.
        """
        suggestions = []
        
        # Check introduction
        if not prompt.introduction:
            suggestions.append("考虑添加一个清晰的介绍，说明AI助手的角色和专长")
        elif len(prompt.introduction) < 20:
            suggestions.append("介绍部分可以更详细，增加专业性和可信度")
        
        # Check target
        if not prompt.target:
            suggestions.append("建议添加明确的目标描述，让AI知道要达成什么")
        elif "目标" not in prompt.target:
            suggestions.append("目标描述可以更明确，使用'目标'等关键词")
        
        # Check instruction
        if not prompt.instruction:
            suggestions.append("指令部分是必需的，请添加具体的执行指导")
        elif len(prompt.instruction) < 50:
            suggestions.append("指令部分可以更详细，提供更多具体的执行步骤")
        
        return suggestions
    
    def _calculate_confidence_score(
        self, 
        original: AgentPromptModel, 
        optimized_intro: str, 
        optimized_target: str, 
        optimized_instruction: str
    ) -> float:
        """Calculate confidence score for optimization.
        
        Args:
            original: Original prompt model.
            optimized_intro: Optimized introduction.
            optimized_target: Optimized target.
            optimized_instruction: Optimized instruction.
            
        Returns:
            float: Confidence score between 0 and 1.
        """
        score = 0.0
        
        # Check if all sections exist
        if optimized_intro:
            score += 0.3
        if optimized_target:
            score += 0.3
        if optimized_instruction:
            score += 0.4
        
        # Check for improvements
        if original.introduction != optimized_intro:
            score += 0.1
        if original.target != optimized_target:
            score += 0.1
        if original.instruction != optimized_instruction:
            score += 0.1
        
        return min(score, 1.0)
    
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
