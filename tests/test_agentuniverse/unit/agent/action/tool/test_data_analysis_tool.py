# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/11 17:38
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: test_data_analysis_tool.py

import unittest
from agentuniverse.agent.action.tool.common_tool.data_analysis_tool import DataAnalysisTool


class DataAnalysisToolTest(unittest.TestCase):
    """
    Test cases for DataAnalysisTool class
    """

    def setUp(self) -> None:
        self.tool = DataAnalysisTool()

    # ==================== Single Formula Tests ====================
    
    def test_single_formula_normal(self) -> None:
        """Test single formula calculation normal case"""
        result = self.tool.execute('single_formula', '2 + 3')
        self.assertIn('result', result)
        self.assertEqual(result['result'], 5)
        self.assertEqual(result['formula'], '2 + 3')
        
    def test_single_formula_with_variables(self) -> None:
        """Test single formula calculation with variables"""
        result = self.tool.execute('single_formula', 'a + b', {'variables': {'a': 10, 'b': 20}})
        self.assertIn('result', result)
        self.assertEqual(result['result'], 30)
        
    def test_single_formula_error_none_data(self) -> None:
        """Test single formula calculation - None data error"""
        result = self.tool.execute('single_formula', None)
        self.assertIn('error', result)
        self.assertIn('Data cannot be empty', result['error'])
        
    def test_single_formula_error_undefined_variable(self) -> None:
        """Test single formula calculation - undefined variable error"""
        result = self.tool.execute('single_formula', 'a + b')
        self.assertIn('error', result)
        self.assertIn('Formula calculation error', result['error'])
        
    def test_single_formula_error_invalid_variables_type(self) -> None:
        """Test single formula calculation - invalid variables type error"""
        result = self.tool.execute('single_formula', 'a + b', {'variables': 'invalid'})
        self.assertIn('error', result)
        self.assertIn('Variables must be in dictionary format', result['error'])
        
    # ==================== Batch Formula Tests ====================
    
    def test_batch_formula_normal(self) -> None:
        """Test batch formula calculation normal case"""
        formulas = [
            {'name': 'area', 'formula': 'length * width', 'variables': {'length': 5, 'width': 3}},
            {'name': 'perimeter', 'formula': '2 * (length + width)', 'variables': {'length': 5, 'width': 3}}
        ]
        result = self.tool.execute('batch_formula', formulas)
        self.assertIn('result', result)
        self.assertEqual(result['success_count'], 2)
        self.assertEqual(result['total_count'], 2)
        self.assertIn('area', result['result'])
        self.assertIn('perimeter', result['result'])
        self.assertEqual(result['result']['area']['result'], 15)
        self.assertEqual(result['result']['perimeter']['result'], 16)
        
    def test_batch_formula_with_error(self) -> None:
        """Test batch formula calculation with errors"""
        formulas = [
            {'name': 'valid', 'formula': '2 + 3'},
            {'name': 'invalid', 'formula': 'undefined_var + 5'}
        ]
        result = self.tool.execute('batch_formula', formulas)
        self.assertIn('result', result)
        self.assertEqual(result['success_count'], 1)
        self.assertEqual(result['total_count'], 2)
        self.assertIn('valid', result['result'])
        self.assertIn('invalid', result['result'])
        self.assertNotIn('error', result['result']['valid'])
        self.assertIn('error', result['result']['invalid'])
        
    def test_batch_formula_error_empty_list(self) -> None:
        """Test batch formula calculation - empty list error"""
        result = self.tool.execute('batch_formula', [])
        self.assertIn('error', result)
        self.assertIn('Data list for batch formula calculation cannot be empty', result['error'])
        
    def test_batch_formula_error_invalid_type(self) -> None:
        """Test batch formula calculation - invalid data type error"""
        result = self.tool.execute('batch_formula', 'invalid')
        self.assertIn('error', result)
        self.assertIn('Data for batch formula calculation must be in list format', result['error'])
        
    def test_batch_formula_error_invalid_config_type(self) -> None:
        """Test batch formula calculation - invalid config type error"""
        formulas = [
            'invalid_config'
        ]
        result = self.tool.execute('batch_formula', formulas)
        self.assertIn('result', result)
        # Should have an error entry for the invalid config
        found_error = False
        for key in result['result']:
            if 'error' in result['result'][key]:
                found_error = True
                break
        self.assertTrue(found_error)
        
    # ==================== Formula Chain Tests ====================
    
    def test_formula_chain_normal(self) -> None:
        """Test formula chain calculation normal case"""
        formulas = [
            {'name': 'step1', 'formula': 'a + b', 'variables': {'a': 1, 'b': 2}},
            {'name': 'step2', 'formula': 'step1 * 2', 'variables': {}}
        ]
        result = self.tool.execute('formula_chain', formulas)
        self.assertIn('result', result)
        self.assertEqual(result['success_count'], 2)
        self.assertEqual(result['total_count'], 2)
        self.assertIn('step1', result['result'])
        self.assertIn('step2', result['result'])
        self.assertEqual(result['result']['step1']['result'], 3)
        self.assertEqual(result['result']['step2']['result'], 6)
        
    def test_formula_chain_with_error(self) -> None:
        """Test formula chain calculation with errors"""
        formulas = [
            {'name': 'step1', 'formula': '2 + 3'},
            {'name': 'step2', 'formula': 'step1 * undefined_var'}
        ]
        result = self.tool.execute('formula_chain', formulas)
        self.assertIn('result', result)
        # Should stop at the first error
        self.assertEqual(result['success_count'], 1)
        self.assertEqual(result['total_count'], 2)
        self.assertIn('step1', result['result'])
        self.assertIn('step2', result['result'])
        self.assertNotIn('error', result['result']['step1'])
        self.assertIn('error', result['result']['step2'])
        
    def test_formula_chain_error_empty_list(self) -> None:
        """Test formula chain calculation - empty list error"""
        result = self.tool.execute('formula_chain', [])
        self.assertIn('error', result)
        self.assertIn('Data list for chain formula calculation cannot be empty', result['error'])
        
    def test_formula_chain_error_invalid_type(self) -> None:
        """Test formula chain calculation - invalid data type error"""
        result = self.tool.execute('formula_chain', 'invalid')
        self.assertIn('error', result)
        self.assertIn('Data for chain formula calculation must be in list format', result['error'])
        
    # ==================== Statistical Suite Tests ====================
    
    def test_statistical_suite_normal_descriptive_stats(self) -> None:
        """Test statistical suite - descriptive stats normal case"""
        data = [1, 2, 3, 4, 5]
        result = self.tool.execute('statistical_suite', data, {'suite_name': 'descriptive_stats'})
        self.assertIn('result', result)
        self.assertIn('suite_description', result)
        self.assertIn('count', result['result'])
        self.assertIn('mean', result['result'])
        self.assertIn('median', result['result'])
        self.assertIn('min', result['result'])
        self.assertIn('max', result['result'])
        self.assertIn('range', result['result'])
        
    def test_statistical_suite_normal_five_number_summary(self) -> None:
        """Test statistical suite - five number summary normal case"""
        data = [1, 2, 3, 4, 5]
        result = self.tool.execute('statistical_suite', data, {'suite_name': 'five_number_summary'})
        self.assertIn('result', result)
        self.assertIn('min', result['result'])
        self.assertIn('q1', result['result'])
        self.assertIn('median', result['result'])
        self.assertIn('q3', result['result'])
        self.assertIn('max', result['result'])
        
    def test_statistical_suite_error_empty_list(self) -> None:
        """Test statistical suite - empty list error"""
        result = self.tool.execute('statistical_suite', [])
        self.assertIn('error', result)
        self.assertIn('Data list for statistical suite calculation cannot be empty', result['error'])
        
    def test_statistical_suite_error_invalid_type(self) -> None:
        """Test statistical suite - invalid data type error"""
        result = self.tool.execute('statistical_suite', 'invalid')
        self.assertIn('error', result)
        self.assertIn('Data for statistical suite calculation must be in list format', result['error'])
        
    def test_statistical_suite_error_invalid_data_type(self) -> None:
        """Test statistical suite - invalid data element type error"""
        result = self.tool.execute('statistical_suite', [1, 2, 'invalid'], {'suite_name': 'descriptive_stats'})
        self.assertIn('error', result)
        self.assertIn('Element 3 in data list must be numeric', result['error'])
        
    def test_statistical_suite_error_empty_suite_name(self) -> None:
        """Test statistical suite - empty suite name error"""
        result = self.tool.execute('statistical_suite', [1, 2, 3], {'suite_name': ''})
        self.assertIn('error', result)
        self.assertIn('Statistical suite name cannot be empty', result['error'])
        
    def test_statistical_suite_error_invalid_suite_name(self) -> None:
        """Test statistical suite - invalid suite name error"""
        result = self.tool.execute('statistical_suite', [1, 2, 3], {'suite_name': 'invalid_suite'})
        self.assertIn('error', result)
        self.assertIn('Unknown statistical suite', result['error'])
        
    # ==================== Data Comparison Tests ====================
    
    def test_data_comparison_normal(self) -> None:
        """Test data comparison normal case"""
        datasets = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = self.tool.execute('data_comparison', datasets)
        self.assertIn('result', result)
        self.assertIn('mean_comparison', result['result'])
        self.assertIn('variability_comparison', result['result'])
        self.assertIn('means', result['result']['mean_comparison'])
        self.assertIn('std_devs', result['result']['variability_comparison'])
        
    def test_data_comparison_error_insufficient_datasets(self) -> None:
        """Test data comparison - insufficient datasets error"""
        result = self.tool.execute('data_comparison', [[1, 2, 3]])
        self.assertIn('error', result)
        self.assertIn('At least two datasets are required for comparison', result['error'])
        
    def test_data_comparison_error_invalid_type(self) -> None:
        """Test data comparison - invalid data type error"""
        result = self.tool.execute('data_comparison', 'invalid')
        self.assertIn('error', result)
        self.assertIn('Data for comparison must be in list format', result['error'])
        
    def test_data_comparison_error_invalid_dataset_type(self) -> None:
        """Test data comparison - invalid dataset type error"""
        result = self.tool.execute('data_comparison', ['invalid', [1, 2, 3]])
        self.assertIn('error', result)
        self.assertIn('Dataset 1 must be a list', result['error'])
        
    def test_data_comparison_error_invalid_data_type(self) -> None:
        """Test data comparison - invalid data element type error"""
        result = self.tool.execute('data_comparison', [[1, 2, 'invalid'], [4, 5, 6]])
        self.assertIn('error', result)
        self.assertIn('Element 3 in dataset 1 must be numeric', result['error'])
        
    # ==================== General Error Tests ====================
    
    def test_execute_error_empty_operation(self) -> None:
        """Test execute - empty operation type error"""
        result = self.tool.execute('', 'data')
        self.assertIn('error', result)
        self.assertIn('Operation type cannot be empty', result['error'])
        
    def test_execute_error_none_data(self) -> None:
        """Test execute - None data error"""
        result = self.tool.execute('single_formula', None)
        self.assertIn('error', result)
        self.assertIn('Data cannot be empty', result['error'])
        
    def test_execute_error_invalid_operation(self) -> None:
        """Test execute - invalid operation type error"""
        result = self.tool.execute('invalid_operation', 'data')
        self.assertIn('error', result)
        self.assertIn('Unsupported operation type', result['error'])


if __name__ == '__main__':
    unittest.main()
