# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 11:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: scenario_analyzer.py
"""Scenario Analyzer module for intelligent scenario analysis and context extraction."""

import re
import json
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
from examples.third_party_examples.apps.prompt_toolkit_app.prompt.prompt_generator import ScenarioContext, PromptScenario, PromptComplexity


class ContextType(Enum):
    """Enumeration of context types."""
    
    DOMAIN = "domain"
    USER_ROLE = "user_role"
    TARGET_AUDIENCE = "target_audience"
    TONE = "tone"
    COMPLEXITY = "complexity"
    CONSTRAINTS = "constraints"
    EXAMPLES = "examples"


class AnalysisConfidence(Enum):
    """Enumeration of analysis confidence levels."""
    
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ExtractedContext:
    """Represents extracted context information.
    
    Attributes:
        context_type: The type of context extracted.
        value: The extracted value.
        confidence: Confidence level of the extraction.
        source: The source text that led to this extraction.
        suggestions: Suggestions for improvement.
    """
    
    context_type: ContextType
    value: str
    confidence: AnalysisConfidence
    source: str
    suggestions: List[str]


@dataclass
class ScenarioAnalysisResult:
    """Result of scenario analysis.
    
    Attributes:
        recommended_scenario: The recommended prompt scenario.
        extracted_contexts: List of extracted context information.
        confidence_score: Overall confidence score (0-1).
        suggestions: Suggestions for improvement.
        complexity_level: Recommended complexity level.
    """
    
    recommended_scenario: PromptScenario
    extracted_contexts: List[ExtractedContext]
    confidence_score: float
    suggestions: List[str]
    complexity_level: PromptComplexity


class ScenarioAnalyzer:
    """Intelligent scenario analyzer for prompt generation.
    
    This class analyzes user-provided scenarios and content to extract
    context information and recommend appropriate prompt scenarios.
    """
    
    def __init__(self):
        """Initialize the ScenarioAnalyzer."""
        self._domain_patterns = self._initialize_domain_patterns()
        self._role_patterns = self._initialize_role_patterns()
        self._audience_patterns = self._initialize_audience_patterns()
        self._tone_patterns = self._initialize_tone_patterns()
        self._complexity_indicators = self._initialize_complexity_indicators()
        self._constraint_patterns = self._initialize_constraint_patterns()
        self._example_patterns = self._initialize_example_patterns()
    
    def analyze_scenario(
        self, 
        content: str, 
        additional_context: Optional[Dict[str, Any]] = None
    ) -> ScenarioAnalysisResult:
        """Analyze a scenario and extract context information.
        
        Args:
            content: The scenario content to analyze.
            additional_context: Additional context information.
            
        Returns:
            ScenarioAnalysisResult: The analysis result.
        """
        # Extract various context information
        extracted_contexts = []
        
        # Extract domain
        domain_context = self._extract_domain(content)
        if domain_context:
            extracted_contexts.append(domain_context)
        
        # Extract user role
        role_context = self._extract_user_role(content)
        if role_context:
            extracted_contexts.append(role_context)
        
        # Extract target audience
        audience_context = self._extract_target_audience(content)
        if audience_context:
            extracted_contexts.append(audience_context)
        
        # Extract tone
        tone_context = self._extract_tone(content)
        if tone_context:
            extracted_contexts.append(tone_context)
        
        # Extract constraints
        constraint_contexts = self._extract_constraints(content)
        extracted_contexts.extend(constraint_contexts)
        
        # Extract examples
        example_contexts = self._extract_examples(content)
        extracted_contexts.extend(example_contexts)
        
        # Determine recommended scenario
        recommended_scenario = self._determine_scenario(content, extracted_contexts)
        
        # Determine complexity level
        complexity_level = self._determine_complexity(content, extracted_contexts)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(extracted_contexts)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(extracted_contexts, confidence_score)
        
        return ScenarioAnalysisResult(
            recommended_scenario=recommended_scenario,
            extracted_contexts=extracted_contexts,
            confidence_score=confidence_score,
            suggestions=suggestions,
            complexity_level=complexity_level
        )
    
    def extract_context_from_content(self, content: str) -> ScenarioContext:
        """Extract context information from content.
        
        Args:
            content: The content to analyze.
            
        Returns:
            ScenarioContext: Extracted context information.
        """
        analysis_result = self.analyze_scenario(content)
        
        # Extract values from analysis result
        domain = self._get_context_value(analysis_result.extracted_contexts, ContextType.DOMAIN, "通用")
        user_role = self._get_context_value(analysis_result.extracted_contexts, ContextType.USER_ROLE, "用户")
        target_audience = self._get_context_value(analysis_result.extracted_contexts, ContextType.TARGET_AUDIENCE, "用户")
        tone = self._get_context_value(analysis_result.extracted_contexts, ContextType.TONE, "专业")
        
        # Extract constraints
        constraints = [
            ctx.value for ctx in analysis_result.extracted_contexts 
            if ctx.context_type == ContextType.CONSTRAINTS
        ]
        
        # Extract examples
        examples = []
        for ctx in analysis_result.extracted_contexts:
            if ctx.context_type == ContextType.EXAMPLES:
                try:
                    example_data = json.loads(ctx.value)
                    examples.append(example_data)
                except json.JSONDecodeError:
                    # Handle simple text examples
                    examples.append({"input": ctx.value, "output": ""})
        
        return ScenarioContext(
            domain=domain,
            user_role=user_role,
            target_audience=target_audience,
            constraints=constraints,
            examples=examples,
            tone=tone
        )
    
    def _initialize_domain_patterns(self) -> Dict[str, List[str]]:
        """Initialize domain-specific patterns.
        
        Returns:
            Dict[str, List[str]]: Domain patterns.
        """
        return {
            "技术": ["编程", "代码", "开发", "软件", "技术", "算法", "系统", "架构"],
            "商业": ["商业", "管理", "营销", "销售", "客户", "市场", "业务", "财务"],
            "教育": ["教育", "学习", "教学", "培训", "知识", "课程", "学校", "学生"],
            "医疗": ["医疗", "健康", "医学", "医生", "患者", "治疗", "诊断", "药物"],
            "法律": ["法律", "律师", "法规", "合同", "诉讼", "法院", "法律咨询"],
            "金融": ["金融", "投资", "银行", "保险", "财务", "经济", "股票", "基金"],
            "创意": ["设计", "艺术", "创作", "创意", "广告", "媒体", "内容", "品牌"],
            "科学": ["科学", "研究", "实验", "数据", "分析", "统计", "发现", "理论"]
        }
    
    def _initialize_role_patterns(self) -> Dict[str, List[str]]:
        """Initialize user role patterns.
        
        Returns:
            Dict[str, List[str]]: Role patterns.
        """
        return {
            "学生": ["学生", "学习者", "初学者", "新手", "学员"],
            "专业人士": ["专家", "专业人士", "从业者", "工程师", "分析师"],
            "管理者": ["经理", "主管", "领导", "管理者", "决策者"],
            "开发者": ["开发者", "程序员", "工程师", "架构师", "技术专家"],
            "研究人员": ["研究员", "学者", "科学家", "分析师", "调查员"],
            "客户": ["客户", "用户", "消费者", "购买者", "使用者"]
        }
    
    def _initialize_audience_patterns(self) -> Dict[str, List[str]]:
        """Initialize target audience patterns.
        
        Returns:
            Dict[str, List[str]]: Audience patterns.
        """
        return {
            "初学者": ["初学者", "新手", "入门", "基础", "初级"],
            "专业人士": ["专业人士", "专家", "从业者", "高级", "资深"],
            "管理者": ["管理者", "决策者", "领导", "主管", "经理"],
            "技术人员": ["技术人员", "开发者", "工程师", "架构师"],
            "一般用户": ["用户", "客户", "消费者", "大众", "普通用户"]
        }
    
    def _initialize_tone_patterns(self) -> Dict[str, List[str]]:
        """Initialize tone patterns.
        
        Returns:
            Dict[str, List[str]]: Tone patterns.
        """
        return {
            "正式": ["正式", "专业", "官方", "严肃", "严谨"],
            "友好": ["友好", "亲切", "温和", "友善", "热情"],
            "技术": ["技术", "专业", "精确", "详细", "严谨"],
            "教育": ["教育", "教学", "指导", "启发", "引导"],
            "创意": ["创意", "创新", "灵活", "开放", "自由"]
        }
    
    def _initialize_complexity_indicators(self) -> Dict[str, List[str]]:
        """Initialize complexity indicators.
        
        Returns:
            Dict[str, List[str]]: Complexity indicators.
        """
        return {
            "简单": ["简单", "基础", "入门", "初级", "基本", "容易"],
            "复杂": ["复杂", "高级", "深入", "专业", "详细", "全面", "系统"],
            "中等": ["中等", "中级", "适中", "标准", "常规"]
        }
    
    def _initialize_constraint_patterns(self) -> List[str]:
        """Initialize constraint patterns.
        
        Returns:
            List[str]: Constraint patterns.
        """
        return [
            r"必须(.+?)(?=。|$)",
            r"要求(.+?)(?=。|$)",
            r"限制(.+?)(?=。|$)",
            r"约束(.+?)(?=。|$)",
            r"不能(.+?)(?=。|$)",
            r"禁止(.+?)(?=。|$)"
        ]
    
    def _initialize_example_patterns(self) -> List[str]:
        """Initialize example patterns.
        
        Returns:
            List[str]: Example patterns.
        """
        return [
            r"例如(.+?)(?=。|$)",
            r"比如(.+?)(?=。|$)",
            r"举例(.+?)(?=。|$)",
            r"示例(.+?)(?=。|$)",
            r"例子(.+?)(?=。|$)"
        ]
    
    def _extract_domain(self, content: str) -> Optional[ExtractedContext]:
        """Extract domain information from content.
        
        Args:
            content: The content to analyze.
            
        Returns:
            Optional[ExtractedContext]: Extracted domain context.
        """
        content_lower = content.lower()
        
        for domain, patterns in self._domain_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    confidence = AnalysisConfidence.HIGH if len(patterns) > 3 else AnalysisConfidence.MEDIUM
                    return ExtractedContext(
                        context_type=ContextType.DOMAIN,
                        value=domain,
                        confidence=confidence,
                        source=pattern,
                        suggestions=[f"考虑添加更多{domain}相关的专业术语"]
                    )
        
        return None
    
    def _extract_user_role(self, content: str) -> Optional[ExtractedContext]:
        """Extract user role from content.
        
        Args:
            content: The content to analyze.
            
        Returns:
            Optional[ExtractedContext]: Extracted user role context.
        """
        content_lower = content.lower()
        
        for role, patterns in self._role_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    confidence = AnalysisConfidence.HIGH if len(patterns) > 3 else AnalysisConfidence.MEDIUM
                    return ExtractedContext(
                        context_type=ContextType.USER_ROLE,
                        value=role,
                        confidence=confidence,
                        source=pattern,
                        suggestions=[f"考虑针对{role}的具体需求定制prompt"]
                    )
        
        return None
    
    def _extract_target_audience(self, content: str) -> Optional[ExtractedContext]:
        """Extract target audience from content.
        
        Args:
            content: The content to analyze.
            
        Returns:
            Optional[ExtractedContext]: Extracted target audience context.
        """
        content_lower = content.lower()
        
        for audience, patterns in self._audience_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    confidence = AnalysisConfidence.HIGH if len(patterns) > 3 else AnalysisConfidence.MEDIUM
                    return ExtractedContext(
                        context_type=ContextType.TARGET_AUDIENCE,
                        value=audience,
                        confidence=confidence,
                        source=pattern,
                        suggestions=[f"考虑调整语言复杂度以适应{audience}"]
                    )
        
        return None
    
    def _extract_tone(self, content: str) -> Optional[ExtractedContext]:
        """Extract tone from content.
        
        Args:
            content: The content to analyze.
            
        Returns:
            Optional[ExtractedContext]: Extracted tone context.
        """
        content_lower = content.lower()
        
        for tone, patterns in self._tone_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    confidence = AnalysisConfidence.MEDIUM
                    return ExtractedContext(
                        context_type=ContextType.TONE,
                        value=tone,
                        confidence=confidence,
                        source=pattern,
                        suggestions=[f"确保prompt的语调与{tone}风格一致"]
                    )
        
        return None
    
    def _extract_constraints(self, content: str) -> List[ExtractedContext]:
        """Extract constraints from content.
        
        Args:
            content: The content to analyze.
            
        Returns:
            List[ExtractedContext]: List of extracted constraint contexts.
        """
        constraints = []
        
        for pattern in self._constraint_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                constraints.append(ExtractedContext(
                    context_type=ContextType.CONSTRAINTS,
                    value=match,
                    confidence=AnalysisConfidence.HIGH,
                    source=pattern,
                    suggestions=["确保约束条件在prompt中得到明确体现"]
                ))
        
        return constraints
    
    def _extract_examples(self, content: str) -> List[ExtractedContext]:
        """Extract examples from content.
        
        Args:
            content: The content to analyze.
            
        Returns:
            List[ExtractedContext]: List of extracted example contexts.
        """
        examples = []
        
        for pattern in self._example_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                examples.append(ExtractedContext(
                    context_type=ContextType.EXAMPLES,
                    value=match,
                    confidence=AnalysisConfidence.MEDIUM,
                    source=pattern,
                    suggestions=["考虑在prompt中包含更多具体示例"]
                ))
        
        return examples
    
    def _determine_scenario(
        self, 
        content: str, 
        extracted_contexts: List[ExtractedContext]
    ) -> PromptScenario:
        """Determine the recommended prompt scenario.
        
        Args:
            content: The content to analyze.
            extracted_contexts: List of extracted contexts.
            
        Returns:
            PromptScenario: Recommended scenario.
        """
        content_lower = content.lower()
        
        # Check for specific scenario indicators
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
        elif any(keyword in content_lower for keyword in ['任务', '工作', 'task', 'work']):
            return PromptScenario.TASK_ORIENTED
        else:
            return PromptScenario.CONVERSATIONAL
    
    def _determine_complexity(
        self, 
        content: str, 
        extracted_contexts: List[ExtractedContext]
    ) -> PromptComplexity:
        """Determine the complexity level.
        
        Args:
            content: The content to analyze.
            extracted_contexts: List of extracted contexts.
            
        Returns:
            PromptComplexity: Recommended complexity level.
        """
        content_lower = content.lower()
        
        # Check for complexity indicators
        simple_indicators = self._complexity_indicators.get("简单", [])
        complex_indicators = self._complexity_indicators.get("复杂", [])
        
        simple_count = sum(1 for indicator in simple_indicators if indicator in content_lower)
        complex_count = sum(1 for indicator in complex_indicators if indicator in content_lower)
        
        if complex_count > simple_count:
            return PromptComplexity.COMPLEX
        elif simple_count > complex_count:
            return PromptComplexity.SIMPLE
        else:
            return PromptComplexity.MEDIUM
    
    def _calculate_confidence_score(self, extracted_contexts: List[ExtractedContext]) -> float:
        """Calculate overall confidence score.
        
        Args:
            extracted_contexts: List of extracted contexts.
            
        Returns:
            float: Confidence score between 0 and 1.
        """
        if not extracted_contexts:
            return 0.3
        
        # Calculate weighted confidence score
        total_weight = 0
        weighted_score = 0
        
        for context in extracted_contexts:
            weight = 1.0
            if context.confidence == AnalysisConfidence.HIGH:
                weight = 1.0
            elif context.confidence == AnalysisConfidence.MEDIUM:
                weight = 0.7
            else:
                weight = 0.4
            
            weighted_score += weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.3
    
    def _generate_suggestions(
        self, 
        extracted_contexts: List[ExtractedContext],
        confidence_score: float
    ) -> List[str]:
        """Generate suggestions based on analysis.
        
        Args:
            extracted_contexts: List of extracted contexts.
            confidence_score: Overall confidence score.
            
        Returns:
            List[str]: List of suggestions.
        """
        suggestions = []
        
        if confidence_score < 0.5:
            suggestions.append("考虑提供更多上下文信息以提高分析准确性")
        
        # Check for missing context types
        context_types = {ctx.context_type for ctx in extracted_contexts}
        
        if ContextType.DOMAIN not in context_types:
            suggestions.append("建议明确指定应用领域")
        
        if ContextType.USER_ROLE not in context_types:
            suggestions.append("建议明确用户角色")
        
        if ContextType.TARGET_AUDIENCE not in context_types:
            suggestions.append("建议明确目标受众")
        
        # Add context-specific suggestions
        for context in extracted_contexts:
            suggestions.extend(context.suggestions)
        
        return list(set(suggestions))  # Remove duplicates
    
    def _get_context_value(
        self, 
        contexts: List[ExtractedContext], 
        context_type: ContextType, 
        default: str
    ) -> str:
        """Get value for a specific context type.
        
        Args:
            contexts: List of extracted contexts.
            context_type: The context type to get.
            default: Default value if not found.
            
        Returns:
            str: The context value.
        """
        for context in contexts:
            if context.context_type == context_type:
                return context.value
        
        return default
