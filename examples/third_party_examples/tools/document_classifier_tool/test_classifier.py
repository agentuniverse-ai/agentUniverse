# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 11:30
# @Author  : AI Assistant
# @Email   : assistant@agentuniverse.ai
# @FileName: test_classifier.py

"""
文档分类器测试文件

测试文档分类器的各种功能：
1. 基础分类功能
2. 中文分类功能
3. 不同策略分类
4. 边界情况处理
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from agentuniverse.agent.action.knowledge.store.document import Document
from examples.third_party_examples.tools.document_classifier_tool.document_classifier import (
    DocumentClassifier, 
    ClassificationStrategy
)
from examples.third_party_examples.tools.document_classifier_tool.chinese_document_classifier import ChineseDocumentClassifier


class TestDocumentClassifier(unittest.TestCase):
    """文档分类器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.classifier = DocumentClassifier()
        self.classifier.set_categories(['技术文档', '学术论文', '新闻资讯', '其他'])
        
        # 添加测试规则
        self.classifier.add_keyword_rule('技术文档', ['代码', '编程', 'API', '函数'])
        self.classifier.add_keyword_rule('学术论文', ['研究', '实验', '分析', '论文'])
        self.classifier.add_keyword_rule('新闻资讯', ['消息', '新闻', '事件', '报道'])
        
        self.test_documents = [
            Document(text="这是一个Python编程教程，介绍了如何使用API和函数。"),
            Document(text="本研究通过实验分析了机器学习算法的性能。"),
            Document(text="据最新消息，某公司今日宣布重大事件。"),
            Document(text="今天天气很好，适合出门散步。")  # 应该分类为"其他"
        ]
    
    def test_keyword_classification(self):
        """测试关键词分类"""
        self.classifier.strategy = ClassificationStrategy.KEYWORD_MATCHING
        
        classified_docs = self.classifier.process_docs(self.test_documents)
        
        # 检查第一个文档（技术文档）
        self.assertEqual(
            classified_docs[0].metadata['classification'], 
            '技术文档'
        )
        self.assertGreater(
            classified_docs[0].metadata['classification_confidence'], 
            0.5
        )
        
        # 检查第二个文档（学术论文）
        self.assertEqual(
            classified_docs[1].metadata['classification'], 
            '学术论文'
        )
        
        # 检查第三个文档（新闻资讯）
        self.assertEqual(
            classified_docs[2].metadata['classification'], 
            '新闻资讯'
        )
        
        # 检查第四个文档（其他）
        self.assertEqual(
            classified_docs[3].metadata['classification'], 
            '其他'
        )
    
    def test_regex_classification(self):
        """测试正则表达式分类"""
        self.classifier.strategy = ClassificationStrategy.REGEX_PATTERN
        
        # 添加正则表达式规则
        self.classifier.add_regex_rule('技术文档', r'(代码|编程|API|函数)')
        self.classifier.add_regex_rule('学术论文', r'(研究|实验|分析|论文)')
        self.classifier.add_regex_rule('新闻资讯', r'(消息|新闻|事件|报道)')
        
        classified_docs = self.classifier.process_docs(self.test_documents)
        
        # 检查分类结果
        self.assertEqual(
            classified_docs[0].metadata['classification'], 
            '技术文档'
        )
        self.assertEqual(
            classified_docs[1].metadata['classification'], 
            '学术论文'
        )
        self.assertEqual(
            classified_docs[2].metadata['classification'], 
            '新闻资讯'
        )
    
    def test_empty_document(self):
        """测试空文档处理"""
        empty_doc = Document(text="")
        classified_doc = self.classifier._classify_document(empty_doc)
        
        self.assertEqual(
            classified_doc.metadata['classification'], 
            '其他'
        )
        self.assertEqual(
            classified_doc.metadata['classification_confidence'], 
            0.0
        )
    
    def test_none_text_document(self):
        """测试None文本文档处理"""
        none_doc = Document(text=None)
        classified_doc = self.classifier._classify_document(none_doc)
        
        self.assertEqual(
            classified_doc.metadata['classification'], 
            '其他'
        )
    
    def test_classification_summary(self):
        """测试分类统计摘要"""
        classified_docs = self.classifier.process_docs(self.test_documents)
        summary = self.classifier.get_classification_summary(classified_docs)
        
        self.assertEqual(summary['total_documents'], 4)
        self.assertIn('技术文档', summary['category_counts'])
        self.assertIn('学术论文', summary['category_counts'])
        self.assertIn('新闻资讯', summary['category_counts'])
        self.assertIn('其他', summary['category_counts'])
    
    def test_add_keyword_rule(self):
        """测试添加关键词规则"""
        initial_count = len(self.classifier.keyword_rules)
        
        self.classifier.add_keyword_rule('新类别', ['新关键词'])
        
        self.assertEqual(len(self.classifier.keyword_rules), initial_count + 1)
        self.assertIn('新类别', self.classifier.keyword_rules)
        self.assertIn('新类别', self.classifier.categories)
    
    def test_add_regex_rule(self):
        """测试添加正则表达式规则"""
        initial_count = len(self.classifier.regex_rules)
        
        self.classifier.add_regex_rule('新类别', r'新正则')
        
        self.assertEqual(len(self.classifier.regex_rules), initial_count + 1)
        self.assertIn('新类别', self.classifier.regex_rules)
        self.assertIn('新类别', self.classifier.categories)


class TestChineseDocumentClassifier(unittest.TestCase):
    """中文文档分类器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.classifier = ChineseDocumentClassifier()
        self.classifier.set_categories(['技术文档', '学术论文', '新闻资讯', '其他'])
        
        # 添加中文关键词规则
        self.classifier.add_chinese_keyword_rule('技术文档', ['代码', '编程', 'API', '函数', '技术'])
        self.classifier.add_chinese_keyword_rule('学术论文', ['研究', '实验', '分析', '论文', '学术'])
        self.classifier.add_chinese_keyword_rule('新闻资讯', ['消息', '新闻', '事件', '报道', '记者'])
        
        self.chinese_documents = [
            Document(text="这是一个Python编程教程，介绍了如何使用API和函数进行技术开发。"),
            Document(text="本研究通过实验分析了机器学习算法的性能，这是一篇学术论文。"),
            Document(text="据最新消息，某公司今日宣布重大事件，记者现场报道。"),
            Document(text="今天天气很好，适合出门散步。")  # 应该分类为"其他"
        ]
    
    def test_chinese_keyword_classification(self):
        """测试中文关键词分类"""
        classified_docs = self.classifier.process_docs(self.chinese_documents)
        
        # 检查第一个文档（技术文档）
        self.assertEqual(
            classified_docs[0].metadata['classification'], 
            '技术文档'
        )
        
        # 检查第二个文档（学术论文）
        self.assertEqual(
            classified_docs[1].metadata['classification'], 
            '学术论文'
        )
        
        # 检查第三个文档（新闻资讯）
        self.assertEqual(
            classified_docs[2].metadata['classification'], 
            '新闻资讯'
        )
        
        # 检查第四个文档（其他）
        self.assertEqual(
            classified_docs[3].metadata['classification'], 
            '其他'
        )
    
    def test_jieba_keyword_extraction(self):
        """测试jieba关键词提取"""
        text = "这是一个Python编程教程，介绍了如何使用API和函数。"
        keywords = self.classifier._extract_keywords(text)
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        # 检查是否过滤了停用词
        self.assertNotIn('的', keywords)
        self.assertNotIn('是', keywords)
    
    def test_fuzzy_match(self):
        """测试模糊匹配"""
        # 精确匹配
        self.assertTrue(self.classifier._fuzzy_match('编程', '这是一个编程教程'))
        
        # 分词匹配
        self.assertTrue(self.classifier._fuzzy_match('Python编程', '这是一个Python编程教程'))
        
        # 不匹配
        self.assertFalse(self.classifier._fuzzy_match('Java', '这是一个Python教程'))
    
    def test_text_statistics(self):
        """测试文本统计"""
        text = "这是一个Python编程教程，介绍了如何使用API和函数。"
        stats = self.classifier.get_text_statistics(text)
        
        self.assertIn('total_chars', stats)
        self.assertIn('total_words', stats)
        self.assertIn('unique_words', stats)
        self.assertIn('most_common_words', stats)
        self.assertIn('avg_word_length', stats)
        
        self.assertGreater(stats['total_chars'], 0)
        self.assertGreater(stats['total_words'], 0)
    
    def test_content_type_classification(self):
        """测试内容类型分类"""
        # 技术文档
        tech_text = "这是一个Python编程教程，介绍了如何使用API和函数。"
        self.assertEqual(
            self.classifier.classify_by_content_type(tech_text), 
            '技术文档'
        )
        
        # 学术论文
        academic_text = "本研究通过实验分析了机器学习算法的性能。"
        self.assertEqual(
            self.classifier.classify_by_content_type(academic_text), 
            '学术论文'
        )
        
        # 新闻资讯
        news_text = "据最新消息，某公司今日宣布重大事件。"
        self.assertEqual(
            self.classifier.classify_by_content_type(news_text), 
            '新闻资讯'
        )
    
    def test_chinese_regex_classification(self):
        """测试中文正则表达式分类"""
        self.classifier.add_chinese_regex_rule('技术文档', r'(代码|编程|API|函数|技术)')
        self.classifier.add_chinese_regex_rule('学术论文', r'(研究|实验|分析|论文|学术)')
        self.classifier.add_chinese_regex_rule('新闻资讯', r'(消息|新闻|事件|报道|记者)')
        
        self.classifier.strategy = ClassificationStrategy.REGEX_PATTERN
        
        classified_docs = self.classifier.process_docs(self.chinese_documents)
        
        # 检查分类结果
        self.assertEqual(
            classified_docs[0].metadata['classification'], 
            '技术文档'
        )
        self.assertEqual(
            classified_docs[1].metadata['classification'], 
            '学术论文'
        )
        self.assertEqual(
            classified_docs[2].metadata['classification'], 
            '新闻资讯'
        )


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def setUp(self):
        """测试前准备"""
        self.classifier = DocumentClassifier()
        self.classifier.set_categories(['类别1', '类别2'])
    
    def test_no_categories(self):
        """测试无分类类别"""
        classifier = DocumentClassifier()
        doc = Document(text="测试文档")
        classified_doc = classifier._classify_document(doc)
        
        self.assertEqual(
            classified_doc.metadata['classification'], 
            '未分类'
        )
    
    def test_no_keyword_rules(self):
        """测试无关键词规则"""
        classifier = DocumentClassifier()
        classifier.set_categories(['类别1', '类别2'])
        
        doc = Document(text="测试文档")
        classified_doc = classifier._classify_document(doc)
        
        self.assertEqual(
            classified_doc.metadata['classification'], 
            '未分类'
        )
    
    def test_very_long_text(self):
        """测试超长文本"""
        long_text = "测试" * 10000  # 20000个字符
        doc = Document(text=long_text)
        classified_doc = self.classifier._classify_document(doc)
        
        # 应该能正常处理，不会出错
        self.assertIn('classification', classified_doc.metadata)
    
    def test_special_characters(self):
        """测试特殊字符"""
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        doc = Document(text=special_text)
        classified_doc = self.classifier._classify_document(doc)
        
        # 应该能正常处理特殊字符
        self.assertIn('classification', classified_doc.metadata)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
