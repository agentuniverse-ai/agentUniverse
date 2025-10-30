# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 10:30
# @Author  : AI Assistant
# @Email   : assistant@agentuniverse.ai
# @FileName: chinese_document_classifier.py

import jieba
import re
from typing import List, Dict, Any
from collections import Counter

from examples.third_party_examples.tools.document_classifier_tool.document_classifier import (
    DocumentClassifier
)


class ChineseDocumentClassifier(DocumentClassifier):
    """中文文档分类器
    
    专门针对中文文档优化的分类器，支持：
    - 中文关键词匹配
    - 中文正则表达式匹配
    - 基于jieba分词的关键词提取
    - 中文语义相似度计算
    - 中文LLM分类
    
    Attributes:
        use_jieba: 是否使用jieba分词
        min_word_length: 最小词长度
        stop_words: 停用词列表
        similarity_threshold: 语义相似度阈值
    """
    
    name: str = "chinese_document_classifier"
    description: str = "中文文档智能分类器，支持多种中文分类策略"
    
    # 中文特定配置
    use_jieba: bool = True
    min_word_length: int = 2
    stop_words: List[str] = []
    similarity_threshold: float = 0.6
    
    # 中文停用词（常用）
    DEFAULT_STOP_WORDS = [
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '里', '来', '下', '过', '他', '她', '它', '们', '我们', '你们', '他们', '这个', '那个', '这些', '那些', '什么', '怎么', '为什么', '哪里', '什么时候', '多少', '几个', '一些', '很多', '非常', '特别', '比较', '更', '最', '还', '又', '再', '已经', '正在', '将要', '可以', '能够', '应该', '必须', '需要', '想要', '希望', '觉得', '认为', '知道', '了解', '明白', '清楚', '记得', '忘记', '学习', '工作', '生活', '时间', '地方', '事情', '问题', '方法', '结果', '原因', '条件', '情况', '时候', '地方', '方面', '部分', '内容', '形式', '方式', '过程', '阶段', '步骤', '环节', '因素', '影响', '作用', '意义', '价值', '目的', '目标', '计划', '安排', '组织', '管理', '控制', '监督', '检查', '评估', '分析', '研究', '调查', '统计', '数据', '信息', '资料', '材料', '文件', '报告', '总结', '结论', '建议', '意见', '看法', '观点', '态度', '立场', '角度', '层面', '水平', '程度', '范围', '规模', '大小', '多少', '长短', '高低', '深浅', '粗细', '厚薄', '宽窄', '远近', '新旧', '好坏', '对错', '真假', '美丑', '善恶', '正邪', '是非', '黑白', '红绿', '蓝黄', '紫粉', '灰棕', '金银', '铜铁', '木石', '水火', '土气', '风雷', '雨雪', '冰霜', '云雾', '阳光', '月光', '星光', '灯光', '火光', '电光', '声音', '音乐', '歌曲', '舞蹈', '绘画', '书法', '雕塑', '建筑', '设计', '艺术', '文化', '历史', '传统', '现代', '未来', '过去', '现在', '今天', '明天', '昨天', '今年', '明年', '去年', '春天', '夏天', '秋天', '冬天', '一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日', '上午', '下午', '晚上', '夜里', '凌晨', '早晨', '中午', '傍晚', '深夜', '半夜', '整天', '全天', '部分', '全部', '一半', '三分之一', '四分之一', '五分之一', '十分之一', '百分之一', '千分之一', '万分之一', '亿分之一', '无限', '有限', '有限制', '无限制', '有条件', '无条件', '有可能', '不可能', '有希望', '无希望', '有前途', '无前途', '有发展', '无发展', '有进步', '无进步', '有改善', '无改善', '有提高', '无提高', '有提升', '无提升', '有增长', '无增长', '有减少', '无减少', '有下降', '无下降', '有上升', '无上升', '有增加', '无增加', '有减少', '无减少', '有变化', '无变化', '有改变', '无改变', '有改善', '无改善', '有提高', '无提高', '有提升', '无提升', '有增长', '无增长', '有减少', '无减少', '有下降', '无下降', '有上升', '无上升', '有增加', '无增加', '有减少', '无减少', '有变化', '无变化', '有改变', '无改变'
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化停用词
        if not self.stop_words:
            self.stop_words = self.DEFAULT_STOP_WORDS.copy()
            
        # 初始化jieba
        if self.use_jieba:
            jieba.initialize()

    def _classify_by_keywords(self, text: str) -> tuple[str, float]:
        """基于中文关键词匹配进行分类
        
        Args:
            text: 文档文本
            
        Returns:
            tuple: (分类结果, 置信度)
        """
        if not self.keyword_rules:
            return self.default_category, 0.0
            
        # 对文本进行分词处理
        if self.use_jieba:
            words = self._extract_keywords(text)
            text_processed = " ".join(words)
        else:
            text_processed = text
            
        category_scores = {}
        
        for category, keywords in self.keyword_rules.items():
            score = 0
            total_keywords = len(keywords)
            
            for keyword in keywords:
                # 支持模糊匹配
                if self._fuzzy_match(keyword, text_processed):
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

    def _extract_keywords(self, text: str) -> List[str]:
        """使用jieba提取关键词
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 关键词列表
        """
        if not self.use_jieba:
            return [text]
            
        # 分词
        words = jieba.lcut(text)
        
        # 过滤停用词和短词
        filtered_words = []
        for word in words:
            word = word.strip()
            if (len(word) >= self.min_word_length and 
                word not in self.stop_words and 
                not re.match(r'^[0-9\s\W]+$', word)):  # 过滤纯数字和特殊字符
                filtered_words.append(word)
                
        return filtered_words

    def _fuzzy_match(self, keyword: str, text: str) -> bool:
        """模糊匹配关键词
        
        Args:
            keyword: 关键词
            text: 文本
            
        Returns:
            bool: 是否匹配
        """
        # 精确匹配
        if keyword in text:
            return True
            
        # 分词后匹配
        if self.use_jieba:
            keyword_words = jieba.lcut(keyword)
            text_words = jieba.lcut(text)
            
            # 检查关键词的所有词是否都在文本中
            keyword_set = set(keyword_words)
            text_set = set(text_words)
            
            if keyword_set.issubset(text_set):
                return True
                
        return False

    def _build_classification_prompt(self, text: str) -> str:
        """构建中文LLM分类提示
        
        Args:
            text: 文档文本
            
        Returns:
            str: 分类提示
        """
        categories_str = "、".join(self.categories)
        
        prompt = f"""请对以下中文文档进行分类。

可选分类类别：{categories_str}

文档内容：
{text[:2000]}

请仔细分析文档内容，选择最合适的分类。请按照以下JSON格式返回分类结果：
{{
    "category": "分类结果",
    "confidence": 0.95,
    "reason": "分类理由（简要说明为什么选择这个分类）"
}}

如果文档内容无法明确分类，请选择"{self.default_category}"。
请确保分类结果准确，置信度要合理。
"""
        return prompt

    def add_chinese_keyword_rule(self, category: str, keywords: List[str]) -> None:
        """添加中文关键词分类规则
        
        Args:
            category: 分类类别
            keywords: 中文关键词列表
        """
        # 对关键词进行预处理
        processed_keywords = []
        for keyword in keywords:
            if self.use_jieba:
                # 使用jieba分词处理关键词
                words = jieba.lcut(keyword)
                processed_keywords.extend([w for w in words if len(w) >= self.min_word_length])
            else:
                processed_keywords.append(keyword)
                
        self.add_keyword_rule(category, processed_keywords)

    def add_chinese_regex_rule(self, category: str, pattern: str) -> None:
        """添加中文正则表达式分类规则
        
        Args:
            category: 分类类别
            pattern: 中文正则表达式模式
        """
        self.add_regex_rule(category, pattern)

    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """获取文本统计信息
        
        Args:
            text: 输入文本
            
        Returns:
            Dict: 文本统计信息
        """
        if self.use_jieba:
            words = self._extract_keywords(text)
            word_count = Counter(words)
            
            return {
                "total_chars": len(text),
                "total_words": len(words),
                "unique_words": len(word_count),
                "most_common_words": word_count.most_common(10),
                "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0
            }
        else:
            return {
                "total_chars": len(text),
                "total_words": len(text.split()),
                "unique_words": len(set(text.split())),
                "most_common_words": Counter(text.split()).most_common(10),
                "avg_word_length": len(text) / len(text.split()) if text.split() else 0
            }

    def classify_by_content_type(self, text: str) -> str:
        """根据内容类型进行基础分类
        
        Args:
            text: 输入文本
            
        Returns:
            str: 内容类型分类
        """
        # 检测文档类型的关键词
        type_keywords = {
            "技术文档": ["代码", "API", "接口", "函数", "方法", "类", "模块", "配置", "安装", "部署", "调试", "错误", "异常", "日志"],
            "学术论文": ["摘要", "引言", "方法", "实验", "结果", "讨论", "结论", "参考文献", "引用", "研究", "分析", "数据"],
            "新闻资讯": ["报道", "消息", "新闻", "事件", "发生", "时间", "地点", "人物", "原因", "影响", "结果"],
            "商业报告": ["报告", "分析", "数据", "统计", "趋势", "预测", "建议", "策略", "市场", "销售", "收入", "利润"],
            "法律文档": ["法律", "法规", "条例", "条款", "权利", "义务", "责任", "合同", "协议", "争议", "诉讼"],
            "教育材料": ["学习", "教学", "课程", "教材", "练习", "考试", "作业", "知识点", "概念", "原理", "方法"],
            "医疗文档": ["疾病", "症状", "诊断", "治疗", "药物", "手术", "检查", "化验", "病历", "处方", "康复"],
            "其他": []
        }
        
        text_lower = text.lower()
        max_score = 0
        best_type = "其他"
        
        for doc_type, keywords in type_keywords.items():
            if doc_type == "其他":
                continue
                
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > max_score:
                max_score = score
                best_type = doc_type
                
        return best_type
