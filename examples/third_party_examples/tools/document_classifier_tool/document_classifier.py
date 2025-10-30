# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 10:00
# @Author  : AI Assistant
# @Email   : assistant@agentuniverse.ai
# @FileName: document_classifier.py

import re
import json
from abc import abstractmethod
from typing import List, Optional, Dict, Any, Set, Union
from enum import Enum

from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.llm.llm_manager import LLMManager


class ClassificationStrategy(Enum):
    """文档分类策略枚举"""
    KEYWORD_MATCHING = "keyword_matching"  # 关键词匹配
    REGEX_PATTERN = "regex_pattern"        # 正则表达式匹配
    LLM_CLASSIFICATION = "llm_classification"  # 大语言模型分类
    HYBRID = "hybrid"                      # 混合策略


class DocumentClassifier(DocProcessor):
    """文档分类器基类
    
    提供多种文档分类策略，支持基于关键词、正则表达式、LLM等方法的文档自动分类。
    分类结果将存储在文档的metadata中，便于后续检索和处理。
    
    Attributes:
        categories: 分类类别列表
        strategy: 分类策略
        confidence_threshold: 置信度阈值
        default_category: 默认分类
        llm_name: 用于LLM分类的模型名称
    """
    
    component_type = DocProcessor.component_type
    name: Optional[str] = "document_classifier"
    description: Optional[str] = "智能文档分类器，支持多种分类策略"
    
    # 分类配置
    categories: List[str] = []
    strategy: ClassificationStrategy = ClassificationStrategy.KEYWORD_MATCHING
    confidence_threshold: float = 0.7
    default_category: str = "未分类"
    llm_name: Optional[str] = None
    
    # 关键词分类规则
    keyword_rules: Dict[str, List[str]] = {}
    
    # 正则表达式分类规则
    regex_rules: Dict[str, str] = {}
    
    # 分类结果存储键名
    classification_key: str = "classification"
    confidence_key: str = "classification_confidence"
    
    class Config:
        arbitrary_types_allowed = True

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """处理文档列表，为每个文档添加分类信息
        
        Args:
            origin_docs: 原始文档列表
            query: 查询对象（可选）
            
        Returns:
            List[Document]: 处理后的文档列表，包含分类信息
        """
        processed_docs = []
        
        for doc in origin_docs:
            # 对单个文档进行分类
            classified_doc = self._classify_document(doc)
            processed_docs.append(classified_doc)
            
        return processed_docs

    def _classify_document(self, document: Document) -> Document:
        """对单个文档进行分类
        
        Args:
            document: 待分类的文档
            
        Returns:
            Document: 包含分类信息的文档
        """
        # 确保metadata存在
        if document.metadata is None:
            document.metadata = {}
            
        # 获取文档文本
        text = document.text or ""
        
        # 根据策略进行分类
        if self.strategy == ClassificationStrategy.KEYWORD_MATCHING:
            category, confidence = self._classify_by_keywords(text)
        elif self.strategy == ClassificationStrategy.REGEX_PATTERN:
            category, confidence = self._classify_by_regex(text)
        elif self.strategy == ClassificationStrategy.LLM_CLASSIFICATION:
            category, confidence = self._classify_by_llm(text)
        elif self.strategy == ClassificationStrategy.HYBRID:
            category, confidence = self._classify_by_hybrid(text)
        else:
            category, confidence = self.default_category, 0.0
            
        # 存储分类结果
        document.metadata[self.classification_key] = category
        document.metadata[self.confidence_key] = confidence
        
        # 将分类结果添加到keywords中
        if category != self.default_category:
            document.keywords.add(f"分类:{category}")
            
        return document

    def _classify_by_keywords(self, text: str) -> tuple[str, float]:
        """基于关键词匹配进行分类
        
        Args:
            text: 文档文本
            
        Returns:
            tuple: (分类结果, 置信度)
        """
        if not self.keyword_rules:
            return self.default_category, 0.0
            
        text_lower = text.lower()
        category_scores = {}
        
        for category, keywords in self.keyword_rules.items():
            score = 0
            total_keywords = len(keywords)
            
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
                    
            if total_keywords > 0:
                confidence = score / total_keywords
                category_scores[category] = confidence
                
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            best_confidence = category_scores[best_category]
            
            if best_confidence >= self.confidence_threshold:
                return best_category, best_confidence
                
        return self.default_category, 0.0

    def _classify_by_regex(self, text: str) -> tuple[str, float]:
        """基于正则表达式进行分类
        
        Args:
            text: 文档文本
            
        Returns:
            tuple: (分类结果, 置信度)
        """
        if not self.regex_rules:
            return self.default_category, 0.0
            
        for category, pattern in self.regex_rules.items():
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                return category, 1.0
                
        return self.default_category, 0.0

    def _classify_by_llm(self, text: str) -> tuple[str, float]:
        """基于大语言模型进行分类
        
        Args:
            text: 文档文本
            
        Returns:
            tuple: (分类结果, 置信度)
        """
        if not self.llm_name or not self.categories:
            return self.default_category, 0.0
            
        try:
            # 构建分类提示
            prompt = self._build_classification_prompt(text)
            
            # 获取LLM实例
            llm_manager = LLMManager()
            llm = llm_manager.get_instance_by_name(self.llm_name)
            
            if not llm:
                return self.default_category, 0.0
                
            # 调用LLM进行分类
            response = llm.run(prompt)
            
            # 解析LLM响应
            category, confidence = self._parse_llm_response(response)
            
            return category, confidence
            
        except Exception as e:
            print(f"LLM分类出错: {e}")
            return self.default_category, 0.0

    def _classify_by_hybrid(self, text: str) -> tuple[str, float]:
        """混合策略分类
        
        Args:
            text: 文档文本
            
        Returns:
            tuple: (分类结果, 置信度)
        """
        # 先尝试关键词匹配
        keyword_category, keyword_confidence = self._classify_by_keywords(text)
        
        # 如果关键词匹配置信度足够高，直接返回
        if keyword_confidence >= self.confidence_threshold:
            return keyword_category, keyword_confidence
            
        # 尝试正则表达式匹配
        regex_category, regex_confidence = self._classify_by_regex(text)
        
        # 如果正则表达式匹配成功，返回结果
        if regex_confidence > 0:
            return regex_category, regex_confidence
            
        # 最后尝试LLM分类
        if self.llm_name:
            llm_category, llm_confidence = self._classify_by_llm(text)
            if llm_confidence >= self.confidence_threshold:
                return llm_category, llm_confidence
                
        # 如果所有策略都失败，返回关键词匹配结果（即使置信度较低）
        return keyword_category, keyword_confidence

    def _build_classification_prompt(self, text: str) -> str:
        """构建LLM分类提示
        
        Args:
            text: 文档文本
            
        Returns:
            str: 分类提示
        """
        categories_str = "、".join(self.categories)
        
        prompt = f"""请对以下文档进行分类。

可选分类类别：{categories_str}

文档内容：
{text[:2000]}  # 限制文本长度避免token过多

请按照以下JSON格式返回分类结果：
{{
    "category": "分类结果",
    "confidence": 0.95,
    "reason": "分类理由"
}}

如果文档内容无法明确分类，请选择"{self.default_category}"。
"""
        return prompt

    def _parse_llm_response(self, response: str) -> tuple[str, float]:
        """解析LLM响应
        
        Args:
            response: LLM响应文本
            
        Returns:
            tuple: (分类结果, 置信度)
        """
        try:
            # 尝试解析JSON响应
            if "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
                
                result = json.loads(json_str)
                category = result.get("category", self.default_category)
                confidence = float(result.get("confidence", 0.0))
                
                # 验证分类结果是否在有效类别中
                if category not in self.categories and category != self.default_category:
                    category = self.default_category
                    confidence = 0.0
                    
                return category, confidence
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"解析LLM响应失败: {e}")
            
        # 如果JSON解析失败，尝试简单的文本匹配
        response_lower = response.lower()
        for category in self.categories:
            if category.lower() in response_lower:
                return category, 0.8  # 给予中等置信度
                
        return self.default_category, 0.0

    def add_keyword_rule(self, category: str, keywords: List[str]) -> None:
        """添加关键词分类规则
        
        Args:
            category: 分类类别
            keywords: 关键词列表
        """
        if category not in self.keyword_rules:
            self.keyword_rules[category] = []
        self.keyword_rules[category].extend(keywords)
        
        # 确保类别在分类列表中
        if category not in self.categories:
            self.categories.append(category)

    def add_regex_rule(self, category: str, pattern: str) -> None:
        """添加正则表达式分类规则
        
        Args:
            category: 分类类别
            pattern: 正则表达式模式
        """
        self.regex_rules[category] = pattern
        
        # 确保类别在分类列表中
        if category not in self.categories:
            self.categories.append(category)

    def set_categories(self, categories: List[str]) -> None:
        """设置分类类别列表
        
        Args:
            categories: 分类类别列表
        """
        self.categories = categories

    def get_classification_summary(self, documents: List[Document]) -> Dict[str, Any]:
        """获取分类结果统计摘要
        
        Args:
            documents: 已分类的文档列表
            
        Returns:
            Dict: 分类统计摘要
        """
        summary = {
            "total_documents": len(documents),
            "category_counts": {},
            "confidence_stats": {
                "average": 0.0,
                "min": 1.0,
                "max": 0.0
            },
            "unclassified_count": 0
        }
        
        total_confidence = 0.0
        confidence_count = 0
        
        for doc in documents:
            if doc.metadata:
                category = doc.metadata.get(self.classification_key, self.default_category)
                confidence = doc.metadata.get(self.confidence_key, 0.0)
                
                # 统计分类数量
                if category not in summary["category_counts"]:
                    summary["category_counts"][category] = 0
                summary["category_counts"][category] += 1
                
                # 统计置信度
                if confidence > 0:
                    total_confidence += confidence
                    confidence_count += 1
                    summary["confidence_stats"]["min"] = min(summary["confidence_stats"]["min"], confidence)
                    summary["confidence_stats"]["max"] = max(summary["confidence_stats"]["max"], confidence)
                
                # 统计未分类文档
                if category == self.default_category:
                    summary["unclassified_count"] += 1
                    
        # 计算平均置信度
        if confidence_count > 0:
            summary["confidence_stats"]["average"] = total_confidence / confidence_count
            
        return summary
