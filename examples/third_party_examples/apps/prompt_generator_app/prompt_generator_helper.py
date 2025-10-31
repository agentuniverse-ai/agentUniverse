# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: prompt_generator_helper.py
"""Prompt generation helper module.

Provides simple prompt generation functionality for agentUniverse developers,
helping to quickly create standardized prompt configuration files.
This is a lightweight development tool focused on solving prompt creation needs during development.
"""
import json
import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union

from agentuniverse.prompt.prompt_model import AgentPromptModel


class PromptGenerationError(Exception):
    """Exception raised for prompt generation related errors."""

    def __init__(self, message: str) -> None:
        """Initialize the PromptGenerationError.

        Args:
            message: Error message describing the issue.
        """
        super().__init__(message)
        self.message = message


class UnsupportedAgentTypeError(PromptGenerationError):
    """Exception raised when an unsupported agent type is used."""

    def __init__(self, agent_type: str) -> None:
        """Initialize the UnsupportedAgentTypeError.

        Args:
            agent_type: The unsupported agent type.
        """
        message = f"Unsupported agent type: {agent_type}"
        super().__init__(message)
        self.agent_type = agent_type


class PromptTemplateHelper:
    """Prompt template helper class.

    Provides template-based prompt generation for different agent types
    in the agentUniverse framework. It focuses on generating standardized YAML
    configurations that are compatible with the existing architecture.

    Design principles: Simple, lightweight, and compatible with existing architecture.
    """

    # Agent type templates mapping
    AGENT_TEMPLATES = {
        'react': {
        'name': 'Reasoning and Acting Agent',
        'introduction_template': 'You are an AI assistant proficient in tool usage.',
        'target_template': 'Your goal is to answer user questions based on the provided background information and tools. {specific_goal}',
        'instruction_template': '''You must prioritize using the provided tools to answer user questions. If no tools are provided, you can solve problems based on your general knowledge.
You must answer questions in Chinese.
You must analyze user questions from multiple angles and dimensions to help users get comprehensive information. Based on the background and questions, decide what information to search for to answer the questions.
You must break down large problems into multiple smaller problems and plan solution steps.

{specific_requirements}

You can use the following tools:
{{tools}}

你的回答必须严格使用以下格式:

    Question: 您必须回答的问题
    Thought: 我这一步应该做什么，为什么要这么做，我现在要使用一个工具, 不允许回答Final Answer
    Action: 要使用的工具应该，值必须是 [{{tool_names}}] 之一
    Action Input: 工具的输入
    Observation: 工具的执行结果
    ... (Thought/Action/Action Input/Observation 的过程可以重复 N 次)
    Thought: 我现在知道所有问题的最终答案了
    Final Answer: 所有问题的最终答案

历史对话:
{{chat_history}}

背景信息是:
{{background}}

开始！
  注意：
    1.你的回答必须是（Thought/Action/Observation）与（Thought/Final Answer）两种格式之一
    2.你现在必须根据上一步Observation的结果（成功、失败、报错，信息不完整），判断下一步要执行的动作

Question: {{input}}
Thought: {{agent_scratchpad}}'''
        },

        'rag': {
        'name': 'Retrieval Augmented Generation Agent',
        'introduction_template': 'You are an AI assistant proficient in information analysis.',
        'target_template': 'Your goal is to provide answers based on user questions and background information. {specific_goal}',
        'instruction_template': '''You need to follow these rules:
1. You must answer user questions in Chinese.
2. Keep answers within 300 characters.
3. Do not use incorrect information from background materials.
4. Consider the relevance of the answer to the question, do not provide unhelpful responses.
5. Be concise and clear, highlight key points, avoid excessive decorative language.
6. Do not make vague speculations.
7. Use as much numerical information as possible.

{specific_requirements}

Chat history:
{{chat_history}}

Background information:
{{background}}

Today's date: {{date}}

Start!

The question to answer is: {{input}}'''
        },

        'planning': {
        'name': 'Planning Agent',
        'introduction_template': 'You are an AI assistant proficient in information analysis.',
        'target_template': 'Your goal is to break down the question into 3-5 sub-questions. {specific_goal}',
        'instruction_template': '''Based on the question to be answered, provide a logical progressive chain of thought to help users gradually master knowledge and ultimately answer the question.
The chain of thought is embodied in the form of sub-questions, each of which is a complete sentence.
The chain of thought must strictly follow the questions to be answered, cannot extend questions, and cannot directly answer questions.

{specific_requirements}

Each step in this chain of thought must be simple and singular.
Complex problems must be broken down into multiple steps.
Each step must be answerable, not open-ended.
Each step must be a complete sentence without any ambiguity.
Please break down this question into multiple steps, each step different from the original question, step by step.

Today's date is: {{date}}

Previous conversation:
{{chat_history}}

Output must be in the following formatted JSON code snippet, where the thought field represents the approach to breaking down the problem, and the framework field represents the list of sub-questions.
  ```json
  {{
"thought": "Analysis approach and logic for the problem",
"framework": ["Sub-question 1", "Sub-question 2", "Sub-question 3"]
  }}
  ```

Begin!
You must answer user questions in English.

The question to answer is: {{input}}'''
        },

        'executing': {
        'name': 'Executing Agent',
        'introduction_template': 'You are an AI assistant proficient in information analysis.',
        'target_template': 'Your goal is to integrate and correct the questions provided by users and the retrieved knowledge to answer their queries. {specific_goal}',
        'instruction_template': '''You need to answer my questions based on the background information I provide.
Your answers should be as detailed and comprehensive as possible, including sufficient data information.

{specific_requirements}

Please follow these rules:
1. Remove duplicate information.
2. Remove irrelevant information unrelated to answering the question.
3. Remove incorrect information.
4. Use only this information to answer questions.
5. Be concise, focused, and do not use excessive flowery vocabulary or phrases.
6. Do not repeat the same details in multiple places; each point should appear only once.
7. Use as much numerical information as possible.
8. Avoid using vague terms like XXX, ABC, etc.

Previous conversation:
{{chat_history}}

Background information:
{{background}}

Today's date is: {{date}}

Let's begin!
My question is: {{input}}'''
        },

        'expressing': {
            'name': 'Expressing Agent',
            'introduction_template': 'You are a professional content expression expert.',
            'target_template': 'Your goal is to conduct professional content creation and expression according to user needs. {specific_goal}',
            'instruction_template': '''You have excellent language expression and content creation abilities, able to provide high-quality content according to different scenarios and user needs.

{specific_requirements}

Working principles:
1. Ensure content accuracy and professionalism
2. Clear and fluent language expression
3. Adapt style to specific scenarios and audiences
4. Focus on logic and readability

User requirements: {{input}}'''
        },

        'reviewing': {
            'name': 'Reviewing Agent',
            'introduction_template': 'You are a professional review expert.',
            'target_template': 'Your goal is to provide professional review and improvement suggestions for the provided content. {specific_goal}',
            'instruction_template': '''You have keen review abilities, able to identify problems in content and provide constructive improvement suggestions.

{specific_requirements}

Review dimensions:
1. Content accuracy and completeness
2. Logic and coherence
3. Clarity of language expression
4. Whether it meets expected goals

Please review the following content: {{input}}'''
        },

        'workflow': {
            'name': 'Workflow Agent',
            'introduction_template': 'You are a professional workflow management expert.',
            'target_template': 'Your goal is to coordinate and manage complex workflows. {specific_goal}',
            'instruction_template': '''You have excellent workflow management and task coordination capabilities.

{specific_requirements}

Management principles:
1. Ensure process efficiency and accuracy
2. Properly coordinate all links
3. Handle exceptions and problems promptly
4. Maintain process traceability

Current task: {{input}}'''
        }
    }

    @classmethod
    def generate_prompt_template(cls,
                                task_description: str,
                                agent_type: str = 'react',
                                scenario: Optional[str] = None,
                                specific_requirements: Optional[str] = None) -> AgentPromptModel:
        """Generate prompt template for specified agent type.

        Creates a customized prompt template based on the provided parameters,
        tailored to the specific agent type and use case scenario.

        Args:
            task_description (str): Task description detailing what the agent should accomplish.
            agent_type (str): Type of agent (react, rag, planning, etc.). Defaults to 'react'.
            scenario (Optional[str]): Application scenario for context-specific prompts.
            specific_requirements (Optional[str]): Additional requirements for customization.

        Returns:
            AgentPromptModel: Generated prompt template object with introduction, target, and instruction.

        Raises:
            UnsupportedAgentTypeError: If the specified agent type is not supported.

        Example:
            >>> prompt_model = PromptTemplateHelper.generate_prompt_template(
            ...     task_description="Customer service assistant",
            ...     agent_type="react",
            ...     scenario="E-commerce platform"
            ... )
        """
        if agent_type not in cls.AGENT_TEMPLATES:
            raise UnsupportedAgentTypeError(agent_type)

        template = cls.AGENT_TEMPLATES[agent_type]

        # Build specific goals
        specific_goal = ""
        if scenario:
            specific_goal = f"Particularly suitable for {scenario} scenarios."
        if task_description:
            specific_goal += f"Specific task: {task_description}"

        # Build specific requirements
        if not specific_requirements:
            specific_requirements = "Please adjust specific implementation methods according to actual conditions."

        # Generate prompt content
        introduction = template['introduction_template']
        if task_description and "assistant" in introduction.lower():
            domain = cls._extract_domain(task_description)
            if domain:
                introduction = introduction.replace("AI assistant", f"{domain} AI assistant")

        target = template['target_template'].format(specific_goal=specific_goal)
        instruction = template['instruction_template'].format(specific_requirements=specific_requirements)

        return AgentPromptModel(
            introduction=introduction,
            target=target,
            instruction=instruction
        )

    @classmethod
    def generate_yaml_config(cls,
                           prompt_model: AgentPromptModel,
                           version_name: str = None,
                           agent_type: str = 'react') -> str:
        """Generate YAML configuration from prompt model.

        Converts the prompt model into a standardized YAML configuration
        format that can be used directly in agentUniverse applications.

        Args:
            prompt_model (AgentPromptModel): The prompt model to convert.
            version_name (Optional[str]): Version identifier for the configuration.
            agent_type (str): Agent type for metadata. Defaults to 'react'.

        Returns:
            str: YAML configuration string ready for use.
        """
        yaml_content = ""

        if prompt_model.introduction:
            yaml_content += f"introduction: {prompt_model.introduction}\n"

        if prompt_model.target:
            yaml_content += f"target: {prompt_model.target}\n"

        if prompt_model.instruction:
            # Process multi-line instruction
            if '\n' in prompt_model.instruction:
                yaml_content += "instruction: |\n"
                for line in prompt_model.instruction.split('\n'):
                    yaml_content += f"  {line}\n"
            else:
                yaml_content += f"instruction: {prompt_model.instruction}\n"

        # Add metadata
        yaml_content += "metadata:\n"
        yaml_content += "  type: 'PROMPT'\n"

        if not version_name:
            version_name = f"custom_{agent_type}_prompt.cn"

        yaml_content += f"  version: '{version_name}'\n"

        return yaml_content

    @classmethod
    def _extract_domain(cls, task_description: str) -> Optional[str]:
        """Extract domain information from task description."""
        domain_keywords = {
            'medical': 'medical', 'diagnosis': 'medical', 'symptom': 'medical', 'healthcare': 'medical',
            'financial': 'financial', 'finance': 'financial', 'stock': 'financial', 'investment': 'financial', 'bank': 'financial',
            'education': 'education', 'learning': 'education', 'teaching': 'education', 'academic': 'education',
            'customer_service': 'customer_service', 'service': 'service', 'support': 'customer_service',
            'legal': 'legal', 'contract': 'legal', 'law': 'legal',
            'sales': 'sales', 'marketing': 'marketing',
            'technical': 'technical', 'development': 'technical', 'programming': 'technical', 'technology': 'technical'
        }

        for keyword, domain in domain_keywords.items():
            if keyword in task_description:
                return domain
        return None

    @classmethod
    def get_supported_agent_types(cls) -> Dict[str, str]:
        """Get supported agent types."""
        return {k: v['name'] for k, v in cls.AGENT_TEMPLATES.items()}


def optimize_existing_prompt(existing_prompt_text: str,
                             optimization_goal: str,
                             agent_type: Optional[str] = None,
                             scenario: Optional[str] = None) -> AgentPromptModel:
    """Optimize existing prompt configuration.

    Analyze existing prompt content and improve it based on optimization goals and scenario requirements.
    This is one of the core functionalities required by the issue: optimizing existing prompts.

    Args:
        existing_prompt_text (str): Existing prompt content (can be YAML or plain text)
        optimization_goal (str): Optimization goal, such as "improve accuracy", "enhance professionalism", etc.
        agent_type (str, optional): Agent type for targeted optimization
        scenario (str, optional): Application scenario for scenario-based optimization

    Returns:
        AgentPromptModel: Optimized prompt model

    Example:
        >>> optimized = optimize_existing_prompt(
        ...     existing_prompt_text="You are an AI assistant",
        ...     optimization_goal="Improve professionalism and accuracy",
        ...     agent_type="react",
        ...     scenario="Financial investment"
        ... )
    """
    # Analyze the structure and content of existing prompt
    analysis_result = _analyze_existing_prompt(existing_prompt_text)

    # Provide improvement suggestions based on optimization goals
    improvement_suggestions = _generate_improvement_suggestions(
        analysis_result, optimization_goal, agent_type, scenario
    )

    # Generate optimized prompt
    optimized_prompt = _apply_optimizations(
        analysis_result, improvement_suggestions, agent_type
    )

    return optimized_prompt


def _analyze_existing_prompt(prompt_text: str) -> Dict[str, Any]:
    """Analyze the structure and quality of existing prompts."""
    analysis = {
        'has_clear_role': False,
        'has_specific_goal': False,
        'has_detailed_instructions': False,
        'includes_variables': False,
        'language': 'zh' if any(ord(char) > 127 for char in prompt_text) else 'en',
        'estimated_type': None,
        'strengths': [],
        'weaknesses': [],
        'content_sections': {}
    }

    # Check if it contains role definition
    role_keywords = ['you are', 'i am', 'as a', 'acting as']
    if any(keyword in prompt_text for keyword in role_keywords):
        analysis['has_clear_role'] = True
        analysis['strengths'].append('Contains clear role definition')
    else:
        analysis['weaknesses'].append('Lacks clear role definition')

    # Check if it contains target description
    goal_keywords = ['goal', 'objective', 'task', 'purpose', 'aim']
    if any(keyword in prompt_text for keyword in goal_keywords):
        analysis['has_specific_goal'] = True
        analysis['strengths'].append('Contains target description')
    else:
        analysis['weaknesses'].append('Lacks clear target description')

    # Check variable placeholders
    import re
    variables = re.findall(r'\{(\w+)\}', prompt_text)
    if variables:
        analysis['includes_variables'] = True
        analysis['strengths'].append(f'Contains variable placeholders: {", ".join(variables)}')
    else:
        analysis['weaknesses'].append('Lacks dynamic variable placeholders')

    # Estimate agent type
    if any(keyword in prompt_text.lower() for keyword in ['tool', 'action', 'thought', 'observation']):
        analysis['estimated_type'] = 'react'
    elif any(keyword in prompt_text.lower() for keyword in ['background', 'retrieve', 'knowledge']):
        analysis['estimated_type'] = 'rag'
    elif any(keyword in prompt_text.lower() for keyword in ['plan', 'step', 'framework']):
        analysis['estimated_type'] = 'planning'

    return analysis


def _generate_improvement_suggestions(analysis: Dict[str, Any], optimization_goal: str,
                                    agent_type: Optional[str], scenario: Optional[str]) -> Dict[str, Any]:
    """Generate improvement suggestions based on analysis results."""
    suggestions = {
        'role_optimization': [],
        'goal_optimization': [],
        'instruction_optimization': [],
        'variable_optimization': [],
        'scenario_optimization': []
    }

    # Provide suggestions based on analysis results
    if not analysis['has_clear_role']:
        suggestions['role_optimization'].append('Add clear role definition')

    if not analysis['has_specific_goal']:
        suggestions['goal_optimization'].append('Add specific target description')

    if not analysis['includes_variables']:
        suggestions['variable_optimization'].append('Add necessary variable placeholders')

    # Suggestions based on optimization goals
    if 'professional' in optimization_goal.lower():
        suggestions['role_optimization'].append('Enhance professional role description')
        suggestions['instruction_optimization'].append('Add professional terminology and standards')

    if 'accuracy' in optimization_goal.lower() or 'accurate' in optimization_goal.lower():
        suggestions['instruction_optimization'].append('Add accuracy requirements and verification steps')

    if 'efficiency' in optimization_goal.lower():
        suggestions['instruction_optimization'].append('Optimize workflow and procedures')

    # Scenario-based suggestions
    if scenario:
        suggestions['scenario_optimization'].append(f'Customize for {scenario} scenario')

    return suggestions


def _apply_optimizations(analysis: Dict[str, Any], suggestions: Dict[str, Any], agent_type: Optional[str]) -> AgentPromptModel:
    """Apply optimization suggestions to generate new prompt."""
    # Here we can generate optimized prompts based on analysis results and suggestions combined with templates
    # For simplicity, we use templates to generate an improved version

    optimized_introduction = "You are a professional intelligent assistant with rich professional knowledge and experience."
    optimized_target = "Your goal is to provide accurate, professional, and useful services to meet users' specific needs."
    optimized_instruction = """Please follow these working principles:
1. Accurately understand user needs and background
2. Provide professional, accurate information and recommendations
3. Maintain friendly and patient service attitude
4. Ensure relevance and practicality of responses
5. Adjust response style according to specific scenarios

User requirements: {input}"""

    return AgentPromptModel(
        introduction=optimized_introduction,
        target=optimized_target,
        instruction=optimized_instruction
    )


def generate_prompt_config(task_description: str,
                          agent_type: str = 'react',
                          scenario: Optional[str] = None,
                          specific_requirements: Optional[str] = None,
                          version_name: Optional[str] = None,
                          output_file: Optional[str] = None) -> str:
    """Generate prompt configuration for agentUniverse agents.

    This is the core functionality: automatically generate prompts based on
    user-provided scenarios and content.

    Args:
        task_description (str): Task description detailing the work the agent needs to complete
        agent_type (str): Agent type, supports react/rag/planning/executing/expressing/reviewing/workflow
        scenario (str, optional): Application scenario for generating targeted prompts
        specific_requirements (str, optional): Specific requirements for customizing prompt content
        version_name (str, optional): Version name for the YAML configuration version field
        output_file (str, optional): Output file path, automatically saves to file if provided

    Returns:
        str: Generated YAML configuration content

    Example:
        >>> yaml_config = generate_prompt_config(
        ...     task_description="Customer service assistant",
        ...     agent_type="react",
        ...     scenario="E-commerce platform",
        ...     output_file="customer_service.yaml"
        ... )
    """
    # Generate prompt template
    prompt_model = PromptTemplateHelper.generate_prompt_template(
        task_description=task_description,
        agent_type=agent_type,
        scenario=scenario,
        specific_requirements=specific_requirements
    )

    # Generate YAML configuration
    yaml_config = PromptTemplateHelper.generate_yaml_config(
        prompt_model=prompt_model,
        version_name=version_name,
        agent_type=agent_type
    )

    # Save to file
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_config)
        print(f"Prompt configuration saved to: {output_file}")

    return yaml_config


# Usage example
if __name__ == "__main__":
    # Example 1: Generate ReAct agent prompt
    yaml_config = generate_prompt_config(
        task_description="智能客服助手，处理用户咨询和订单问题",
        agent_type="react",
        scenario="电商平台",
        version_name="customer_service.cn",
        output_file="customer_service_prompt.yaml"
    )
    print("Generated configuration:\n", yaml_config)

    # Example 2: Generate RAG agent prompt
    generate_prompt_config(
        task_description="保险产品咨询专家，基于产品知识库回答用户问题",
        agent_type="rag",
        scenario="保险行业",
        version_name="insurance_consultant.cn",
        output_file="insurance_consultant_prompt.yaml"
    )
