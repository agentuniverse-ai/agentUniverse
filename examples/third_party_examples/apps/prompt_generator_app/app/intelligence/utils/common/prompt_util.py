# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/16 23:00
# @Author  : Libres-coder
# @Email   : liudi1366@gmail.com
# @FileName: prompt_util.py
"""Prompt Utility Functions.

Provides practical utility functions for prompt processing in app.
This utility module focuses on prompt content analysis, validation, and transformation.
"""
import re
import json
from typing import Dict, Any, List, Optional, Tuple


class PromptUtil:
    """Prompt utility class for content processing and validation."""

    @staticmethod
    def extract_prompt_variables(prompt_text: str) -> List[str]:
        """Extract variable placeholders from prompt text.

        Args:
            prompt_text: Prompt text to analyze.

        Returns:
            List of variable names found in the prompt.
        """
        # Find all {variable_name} patterns
        pattern = r'\{([^}]+)\}'
        variables = re.findall(pattern, prompt_text)
        return list(set(variables))  # Remove duplicates

    @staticmethod
    def validate_prompt_format(prompt_text: str) -> Dict[str, Any]:
        """Validate prompt format validity.

        Args:
            prompt_text: Prompt text to validate.

        Returns:
            Validation results with details.
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {}
        }

        # Basic checks
        if not prompt_text or not prompt_text.strip():
            result["errors"].append("Prompt text is empty")
            result["is_valid"] = False
            return result

        # Check for unmatched braces
        open_braces = prompt_text.count('{')
        close_braces = prompt_text.count('}')
        if open_braces != close_braces:
            result["errors"].append(f"Unmatched braces: {open_braces} open, {close_braces} close")
            result["is_valid"] = False

        # Check for nested braces (not allowed in simple templates)
        if re.search(r'\{[^}]*\{', prompt_text):
            result["warnings"].append("Nested braces detected - may cause issues")

        # Statistics
        variables = PromptUtil.extract_prompt_variables(prompt_text)
        result["statistics"] = {
            "character_count": len(prompt_text),
            "word_count": len(prompt_text.split()),
            "line_count": len(prompt_text.split('\n')),
            "variable_count": len(variables),
            "variables": variables
        }

        return result

    @staticmethod
    def substitute_variables(prompt_text: str, variables: Dict[str, str]) -> str:
        """Substitute variables in prompt text.

        Args:
            prompt_text: Prompt text with variables.
            variables: Dictionary mapping variable names to values.

        Returns:
            Prompt text with variables substituted.

        Raises:
            ValueError: If required variables are missing.
        """
        required_vars = PromptUtil.extract_prompt_variables(prompt_text)
        missing_vars = [var for var in required_vars if var not in variables]

        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        result = prompt_text
        for var_name, var_value in variables.items():
            result = result.replace(f"{{{var_name}}}", str(var_value))

        return result

    @staticmethod
    def analyze_prompt_complexity(prompt_text: str) -> Dict[str, Any]:
        """Analyze prompt complexity metrics.

        Args:
            prompt_text: Prompt text to analyze.

        Returns:
            Complexity analysis results.
        """
        words = prompt_text.split()
        sentences = re.split(r'[.!?]+', prompt_text)
        sentences = [s.strip() for s in sentences if s.strip()]

        variables = PromptUtil.extract_prompt_variables(prompt_text)

        # Calculate complexity scores
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        complexity_score = (
            min(avg_word_length / 10, 1.0) * 0.3 +
            min(avg_sentence_length / 20, 1.0) * 0.4 +
            min(len(variables) / 10, 1.0) * 0.3
        )

        return {
            "complexity_score": complexity_score,
            "word_count": len(words),
            "sentence_count": len(sentences),
            "variable_count": len(variables),
            "avg_word_length": avg_word_length,
            "avg_sentence_length": avg_sentence_length,
            "readability": "high" if complexity_score < 0.3 else "medium" if complexity_score < 0.7 else "low"
        }

    @staticmethod
    def extract_instructions(prompt_text: str) -> List[str]:
        """Extract instruction sentences from prompt text.

        Args:
            prompt_text: Prompt text to analyze.

        Returns:
            List of instruction sentences.
        """
        # Common instruction patterns
        instruction_patterns = [
            r'(?:Please|Kindly|You should|You must|Make sure to|Be sure to|Remember to)[^.!?]*[.!?]',
            r'(?:Follow these|Use the following|Apply these)[^.!?]*[.!?]',
            r'(?:Do not|Don\'t|Never|Avoid)[^.!?]*[.!?]',
            r'(?:Always|Ensure that|Make certain)[^.!?]*[.!?]'
        ]

        instructions = []
        for pattern in instruction_patterns:
            matches = re.findall(pattern, prompt_text, re.IGNORECASE)
            instructions.extend(matches)

        return [inst.strip() for inst in instructions]

    @staticmethod
    def format_prompt_for_display(prompt_text: str, line_width: int = 80) -> str:
        """Format prompt for better display.

        Args:
            prompt_text: Prompt text to format.
            line_width: Maximum line width for wrapping.

        Returns:
            Formatted prompt text.
        """
        import textwrap

        # Split into paragraphs
        paragraphs = prompt_text.split('\n\n')
        formatted_paragraphs = []

        for paragraph in paragraphs:
            if paragraph.strip():
                # Wrap each paragraph
                wrapped = textwrap.fill(paragraph.strip(), width=line_width)
                formatted_paragraphs.append(wrapped)

        return '\n\n'.join(formatted_paragraphs)

    @staticmethod
    def generate_prompt_preview(prompt_text: str, sample_variables: Optional[Dict[str, str]] = None) -> str:
        """Generate a preview of the prompt with sample variables.

        Args:
            prompt_text: Prompt text to preview.
            sample_variables: Optional sample variables for substitution.

        Returns:
            Preview text with sample substitutions.
        """
        variables = PromptUtil.extract_prompt_variables(prompt_text)

        if sample_variables is None:
            sample_variables = {}

        # Generate default sample values for missing variables
        for var in variables:
            if var not in sample_variables:
                sample_variables[var] = f"[{var.upper()}]"

        try:
            preview = PromptUtil.substitute_variables(prompt_text, sample_variables)
            return preview
        except ValueError:
            # If substitution fails, return original with variable markers
            return prompt_text

    @staticmethod
    def compare_prompts(prompt1: str, prompt2: str) -> Dict[str, Any]:
        """Compare two prompts for similarities and differences.

        Args:
            prompt1: First prompt text.
            prompt2: Second prompt text.

        Returns:
            Comparison results.
        """
        vars1 = set(PromptUtil.extract_prompt_variables(prompt1))
        vars2 = set(PromptUtil.extract_prompt_variables(prompt2))

        words1 = set(prompt1.lower().split())
        words2 = set(prompt2.lower().split())

        common_words = words1 & words2
        unique_words1 = words1 - words2
        unique_words2 = words2 - words1

        similarity_score = len(common_words) / len(words1 | words2) if (words1 | words2) else 0

        return {
            "similarity_score": similarity_score,
            "common_variables": list(vars1 & vars2),
            "unique_variables_1": list(vars1 - vars2),
            "unique_variables_2": list(vars2 - vars1),
            "common_words_count": len(common_words),
            "unique_words_1_count": len(unique_words1),
            "unique_words_2_count": len(unique_words2),
            "length_difference": abs(len(prompt1) - len(prompt2))
        }
