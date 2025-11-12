# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/11 11:38
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: data_analysis_tool.py

import math
import re
from typing import Optional, Any, List, Dict, Callable

import numpy as np
import pandas as pd

from agentuniverse.agent.action.tool.tool import Tool


class DataAnalysisTool(Tool):
    name: str = "DataAnalysisTool"
    description: str = """
        Data analysis tool that supports various mathematical operations, including formula calculation, statistical analysis, and data comparison.

        Supported calculation capabilities:
        1. Batch formula calculation - Calculate multiple related formulas at once
        2. Statistical analysis suite - Predefined combinations of statistical calculations
        3. Data comparison analysis - Comparative calculations of multiple datasets
        4. Formula chain calculation - Using the result of one formula as input for the next
        5. Single formula calculation - Simple mathematical formula calculation

        Available statistical suites:
        - descriptive_stats: Descriptive statistics - Basic characteristics of data (count, mean, median, min, max, range)
        - five_number_summary: Five-number summary - Key quantiles of data distribution (min, q1, median, q3, max)
        - variability_analysis: Variability analysis - Dispersion of data (variance, std_dev, range, iqr)
        - distribution_analysis: Distribution analysis - Shape characteristics of data distribution (skewness, kurtosis, mean, median)
        - basic_overview: Basic overview - Quick understanding of basic data situation (count, mean, std_dev, min, max)

        Supported safe mathematical functions:
        - Basic operations: +, -, *, /, **(power), sqrt, abs, round
        - Trigonometric functions: sin, cos, tan
        - Logarithmic functions: log, log10, exp
        - Statistical functions: mean, median, min, max, sum, std, var, q1, q3, iqr, skewness, kurtosis, count
        - Constants: pi, e

        Unified parameter format:
        {"operation": "operation type","data": [data content],"config": {configuration parameters}}

        Operation types and parameter descriptions:
        - batch_formula: Batch formula calculation
          data: [{"name": "name", "formula": "formula", "variables": {variables}}]
          Example: {"operation": "batch_formula", "data": [{"name": "area", "formula": "length * width", "variables": {"length": 5, "width": 3}}, {"name": "perimeter", "formula": "2 * (length + width)", "variables": {"length": 5, "width": 3}}]}

        - statistical_suite: Statistical analysis suite
          data: [numeric list]
          config: {"suite_name": "suite name"}  // Optional values: descriptive_stats, five_number_summary, variability_analysis, distribution_analysis, basic_overview
          Example: {"operation": "statistical_suite", "data": [1, 2, 3, 4, 5], "config": {"suite_name": "descriptive_stats"}}

        - data_comparison: Data comparison analysis
          data: [[dataset1], [dataset2], ...]
          Example: {"operation": "data_comparison", "data": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}

        - formula_chain: Formula chain calculation
          data: [{"name": "name", "formula": "formula", "variables": {variables}}]
          Example: {"operation": "formula_chain", "data": [{"name": "step1", "formula": "a + b", "variables": {"a": 10, "b": 5}}, {"name": "step2", "formula": "step1 * 2"}]}

        - single_formula: Single formula calculation
          data: "formula string"
          config: {"variables": {variables}}
          Example: {"operation": "single_formula", "data": "sqrt(a**2 + b**2)", "config": {"variables": {"a": 3, "b": 4}}}

        Data format description:
        - Variable names in formulas must be alphanumeric characters
        - Numeric lists should be numeric arrays
        - Datasets should be arrays of multiple numeric lists
        - Formulas support basic mathematical operators and predefined functions
        """
    safe_functions: Dict[str, Callable] = None
    stat_suites: Dict[str, List[str]] = None
    supported_operations: List[str] = None

    def __init__(self, name: str = None, description: str = None):
        super().__init__()
        if name:
            self.name = name
        if description:
            self.description = description

        # Supported analysis operations
        self.supported_operations = ['batch_formula', 'statistical_suite', 'data_comparison', 'formula_chain',
                                     'single_formula']

        # Supported statistical functions
        self.safe_functions = {
            'sqrt': math.sqrt, 'log': math.log, 'log10': math.log10, 'exp': math.exp,
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'abs': abs, 'round': round,
            'max': max, 'min': min, 'sum': sum, 'pow': math.pow, 'pi': math.pi, 'e': math.e,
            'mean': np.mean, 'std': np.std, 'var': np.var, 'median': np.median,
            'count': len, 'range': lambda arr: float(np.max(arr) - np.min(arr)),
            'q1': lambda arr: float(np.percentile(arr, 25)),
            'q3': lambda arr: float(np.percentile(arr, 75)),
            'std_dev': lambda arr: float(np.std(arr, ddof=1)),
            'iqr': lambda arr: float(np.percentile(arr, 75) - np.percentile(arr, 25)),
            'skewness': lambda arr: float(pd.Series(arr).skew()),
            'kurtosis': lambda arr: float(pd.Series(arr).kurtosis()),
            'variance': lambda arr: float(np.var(arr, ddof=1))
        }

        # Predefined statistical calculation suites
        self.stat_suites = {
            "descriptive_stats": ["count", "mean", "median", "min", "max", "range"],
            "five_number_summary": ["min", "q1", "median", "q3", "max"],
            "variability_analysis": ["variance", "std_dev", "range", "iqr"],
            "distribution_analysis": ["skewness", "kurtosis", "mean", "median"],
            "basic_overview": ["count", "mean", "std_dev", "min", "max"]
        }

    def execute(self, operation: str, data: Any = None, config: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[
        str, Any]:
        try:
            # Basic parameter validation
            if not operation:
                return {"error": "Operation type cannot be empty"}

            if not data and data != []:  # Allow empty list but not None
                return {"error": "Data cannot be empty"}

            # Supported operation type validation
            if operation not in self.supported_operations:
                return {"error": f"Unsupported operation type: {operation}, supported operation types: {self.supported_operations}"}

            # Execute corresponding calculation based on operation type
            if operation == 'batch_formula':
                return self._batch_calculate_formulas(data)
            elif operation == 'statistical_suite':
                suite_name = (config or {}).get('suite_name') if config else None
                return self._calculate_stat_suite(data, suite_name)
            elif operation == 'data_comparison':
                return self._compare_datasets(data)
            elif operation == 'formula_chain':
                return self._chain_calculate_formulas(data)
            elif operation == 'single_formula':
                variables = (config or {}).get('variables', {}) if config else {}
                return self._calculate_single_formula(data, variables)
            else:
                return {"error": f"Unsupported operation type: {operation}"}

        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"}

    def _batch_calculate_formulas(self, formulas: List[Dict]) -> Dict[str, Any]:
        """Batch calculate formulas"""
        # Parameter validation
        if not isinstance(formulas, list):
            return {"error": "Data for batch formula calculation must be in list format"}

        if len(formulas) == 0:
            return {"error": "Data list for batch formula calculation cannot be empty"}

        results = {}

        for i, formula_config in enumerate(formulas):
            # Validate that each formula configuration is a dictionary
            if not isinstance(formula_config, dict):
                results[f"Formula {i + 1}"] = {"error": f"Formula configuration {i + 1} must be a dictionary"}
                continue

            formula = formula_config.get('formula', '')
            variables = formula_config.get('variables', {})
            name = formula_config.get('name', f'formula_{i + 1}')

            # Validate that formula exists
            if not formula:
                results[name] = {"error": "Formula cannot be empty"}
                continue

            # Validate that variables is a dictionary
            if not isinstance(variables, dict):
                results[name] = {"error": "Variables must be in dictionary format"}
                continue

            try:
                result = self._calculate_single_formula(formula, variables)
                # Check if error message was returned
                if isinstance(result, dict) and "error" in result:
                    results[name] = {"error": result['error']}
                    continue
                results[name] = result
            except Exception as e:
                results[name] = {"error": str(e)}

        return {
            "result": results,
            "success_count": len([r for r in results.values() if 'error' not in r]),
            "total_count": len(formulas)
        }

    def _chain_calculate_formulas(self, formulas: List[Dict]) -> Dict[str, Any]:
        """Chain calculate formulas - Using the result of one formula as input for the next"""
        # Parameter validation
        if not isinstance(formulas, list):
            return {"error": "Data for chain formula calculation must be in list format"}

        if len(formulas) == 0:
            return {"error": "Data list for chain formula calculation cannot be empty"}

        results = {}
        current_variables = {}

        for i, formula_config in enumerate(formulas):
            # Validate that each formula configuration is a dictionary
            if not isinstance(formula_config, dict):
                results[f'step_{i + 1}'] = {"error": f"Formula configuration {i + 1} must be a dictionary"}
                break

            formula = formula_config.get('formula', '')
            base_variables = formula_config.get('variables', {})
            name = formula_config.get('name', f'step_{i + 1}')

            # Validate that formula exists
            if not formula:
                results[name] = {"error": "Formula cannot be empty"}
                break

            # Validate that variables is a dictionary
            if not isinstance(base_variables, dict):
                results[name] = {"error": "Variables must be in dictionary format"}
                break

            # Merge base variables and results from previous steps
            all_variables = {**base_variables, **current_variables}

            try:
                result = self._calculate_single_formula(formula, all_variables)
                results[name] = result
                # Check if error message was returned
                if isinstance(result, dict) and "error" in result:
                    break  # Stop if error occurs in chain calculation
                # Use current result as available variable for next formula
                current_variables[name] = result["result"]

            except Exception as e:
                results[name] = {"error": str(e)}
                break  # Stop if error occurs in chain calculation

        return {
            "result": results,
            "success_count": len([r for r in results.values() if 'error' not in r]),
            "total_count": len(results)
        }

    def _calculate_stat_suite(self, data: List[float], suite_name: str) -> Dict[str, Any]:
        """Calculate predefined statistical suite"""
        # Parameter validation
        if not isinstance(data, list):
            return {"error": "Data for statistical suite calculation must be in list format"}

        if len(data) == 0:
            return {"error": "Data list for statistical suite calculation cannot be empty"}

        if not suite_name:
            return {"error": "Statistical suite name cannot be empty"}

        if suite_name not in self.stat_suites:
            available_suites = list(self.stat_suites.keys())
            return {"error": f"Unknown statistical suite: {suite_name}, available suites: {available_suites}"}

        # Validate that all data are numeric
        for i, item in enumerate(data):
            if not isinstance(item, (int, float)):
                return {"error": f"Element {i + 1} in data list must be numeric, current type: {type(item)}"}

        arr = np.array(data)
        stats_to_calculate = self.stat_suites[suite_name]
        results = {}

        for stat_name in stats_to_calculate:
            try:
                stat_func = self.safe_functions.get(stat_name, None)
                if stat_func:
                    results[stat_name] = stat_func(arr)
                else:
                    results[stat_name] = f"Unknown statistical indicator: {stat_name}"
            except Exception as e:
                results[stat_name] = f"Calculation error: {str(e)}"

        return {
            "result": results,
            "suite_description": self._get_suite_description(suite_name)
        }

    def _perform_dataset_comparison(self, datasets: List[List[float]]) -> Dict[str, Any]:
        """Compare statistical characteristics of multiple datasets"""
        means = [np.mean(data) for data in datasets]
        stds = [np.std(data, ddof=1) for data in datasets]

        return {
            "mean_comparison": {
                "means": means,
                "mean_differences": [abs(means[i] - means[j])
                                     for i in range(len(means))
                                     for j in range(i + 1, len(means))],
                "max_mean": max(means),
                "min_mean": min(means)
            }
            ,
            "variability_comparison": {
                "std_devs": stds,
                "max_std": max(stds),
                "min_std": min(stds)
            }
        }
    def _calculate_single_formula(self, formula: str, variables: Dict[str, float] = None) -> Dict[str, Any]:
        """Calculate single formula (core calculation method)"""
        # Parameter validation
        if not formula:
            return {"error": "Formula cannot be empty"}

        if not isinstance(formula, str):
            return {"error": "Formula must be a string"}

        if variables is not None and not isinstance(variables, dict):
            return {"error": "Variables must be in dictionary format"}

        formula = formula.strip().replace('^', '**')
        safe_env = self.safe_functions.copy()

        if variables:
            safe_env.update(variables)

        if not self._is_formula_safe(formula):
            return {"error": "Formula contains unsafe characters"}

        try:
            result = eval(formula, {"__builtins__": {}}, safe_env)
            return {
                "formula": formula,
                "result": result,
                "variables": variables
            }
        except Exception as e:
            return {"error": f"Formula calculation error: {str(e)}"}

    def _get_suite_description(self, suite_name: str) -> str:
        """Get description of statistical suite"""
        descriptions = {
            "descriptive_stats": "Descriptive statistics - Basic characteristics of data",
            "five_number_summary": "Five-number summary - Key quantiles of data distribution",
            "variability_analysis": "Variability analysis - Dispersion of data",
            "distribution_analysis": "Distribution analysis - Shape characteristics of data distribution",
            "basic_overview": "Basic overview - Quick understanding of basic data situation"
        }
        return descriptions.get(suite_name, "Unknown statistical suite")

    def _compare_datasets(self, datasets: List[List[float]]) -> Dict[str, Any]:
        """Compare statistical characteristics of multiple datasets"""
        # Parameter validation
        if not isinstance(datasets, list):
            return {"error": "Data for comparison must be in list format"}

        if len(datasets) < 2:
            return {"error": "At least two datasets are required for comparison"}

        # Validate that each dataset is a list and contains numeric values
        for i, dataset in enumerate(datasets):
            if not isinstance(dataset, list):
                return {"error": f"Dataset {i + 1} must be a list"}

            for j, item in enumerate(dataset):
                if not isinstance(item, (int, float)):
                    return {"error": f"Element {j + 1} in dataset {i + 1} must be numeric, current type: {type(item)}"}

        return {"result": (self._perform_dataset_comparison(datasets))}

    def _is_formula_safe(self, formula: str) -> bool:
        safe_pattern = r'^[a-zA-Z0-9\s\+\-\*\/\(\)\.\,\_\^\u4e00-\u9fff]+$'
        return bool(re.match(safe_pattern, formula))