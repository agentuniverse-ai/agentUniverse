# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/19 11:00
# @Author  : AI Assistant
# @Email   : assistant@agentuniverse.ai
# @FileName: document_classifier_demo.py

"""
文档分类器使用示例

本示例展示了如何使用agentUniverse的文档分类器功能：
1. 基础文档分类
2. 中文文档分类
3. 批量文档处理
4. 分类结果统计
"""

import sys
import os
from typing import List

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from agentuniverse.agent.action.knowledge.store.document import Document
from examples.third_party_examples.tools.document_classifier_tool.document_classifier import DocumentClassifier
from examples.third_party_examples.tools.document_classifier_tool.chinese_document_classifier import ChineseDocumentClassifier


def create_sample_documents() -> List[Document]:
    """创建示例文档"""
    documents = [
        Document(
            text="""
            Python是一种高级编程语言，具有简洁的语法和强大的功能。
            它广泛应用于Web开发、数据分析、人工智能等领域。
            本文档介绍了Python的基本语法、数据类型、控制结构等核心概念。
            """,
            metadata={"source": "python_tutorial.txt", "author": "技术团队"}
        ),
        Document(
            text="""
            本研究通过实验方法分析了机器学习算法在文本分类任务中的性能表现。
            实验结果表明，基于深度学习的模型在准确率方面显著优于传统方法。
            论文提出了新的注意力机制，有效提升了模型的分类效果。
            """,
            metadata={"source": "ml_research.pdf", "author": "研究团队"}
        ),
        Document(
            text="""
            据最新消息，某科技公司今日宣布完成新一轮融资，融资金额达到1亿美元。
            该轮融资将主要用于产品研发和市场拓展。公司CEO表示，这将有助于
            加速公司在人工智能领域的布局，提升市场竞争力。
            """,
            metadata={"source": "tech_news.txt", "author": "新闻部"}
        ),
        Document(
            text="""
            本季度财务报告显示，公司营业收入同比增长15%，净利润增长20%。
            主要增长动力来自于新产品的成功推出和市场份额的扩大。
            预计下季度将继续保持增长态势，全年目标有望超额完成。
            """,
            metadata={"source": "q3_report.pdf", "author": "财务部"}
        ),
        Document(
            text="""
            根据《中华人民共和国合同法》相关规定，甲乙双方就软件开发项目
            达成如下协议：项目周期为6个月，总金额为100万元。
            甲方负责提供需求文档，乙方负责系统设计和开发实现。
            """,
            metadata={"source": "contract.docx", "author": "法务部"}
        ),
        Document(
            text="""
            本课程将系统介绍数据结构与算法的基本概念和实现方法。
            内容包括：线性表、栈、队列、树、图等数据结构，
            以及排序、查找、动态规划等经典算法。
            通过理论学习和编程实践，帮助学生掌握算法设计思想。
            """,
            metadata={"source": "algorithm_course.md", "author": "教学部"}
        ),
        Document(
            text="""
            患者主诉：头痛、发热、乏力3天。体格检查：体温38.5℃，血压正常，
            心肺听诊无异常。实验室检查：白细胞计数升高，中性粒细胞比例增加。
            初步诊断：上呼吸道感染。建议：多休息，多饮水，口服解热镇痛药。
            """,
            metadata={"source": "patient_record.txt", "author": "医生"}
        )
    ]
    return documents


def demo_basic_classifier():
    """演示基础文档分类器"""
    print("=" * 60)
    print("基础文档分类器演示")
    print("=" * 60)
    
    # 创建分类器实例
    classifier = DocumentClassifier()
    
    # 设置分类类别
    classifier.set_categories([
        '技术文档', '学术论文', '新闻资讯', '商业报告', 
        '法律文档', '教育材料', '医疗文档', '其他'
    ])
    
    # 添加关键词规则
    classifier.add_keyword_rule('技术文档', [
        'Python', '编程', '代码', 'API', '接口', '函数', '方法', '类', '模块', '开发'
    ])
    classifier.add_keyword_rule('学术论文', [
        '研究', '实验', '分析', '论文', '学术', '理论', '模型', '假设', '验证', '数据'
    ])
    classifier.add_keyword_rule('新闻资讯', [
        '消息', '新闻', '事件', '发生', '宣布', '融资', '公司', 'CEO', '市场'
    ])
    classifier.add_keyword_rule('商业报告', [
        '报告', '财务', '收入', '利润', '增长', '季度', '预算', '投资', '收益'
    ])
    classifier.add_keyword_rule('法律文档', [
        '法律', '法规', '合同', '协议', '权利', '义务', '责任', '争议', '诉讼'
    ])
    classifier.add_keyword_rule('教育材料', [
        '课程', '学习', '教学', '教材', '练习', '考试', '学生', '老师', '知识点'
    ])
    classifier.add_keyword_rule('医疗文档', [
        '患者', '疾病', '症状', '诊断', '治疗', '药物', '医生', '医院', '健康'
    ])
    
    # 获取示例文档
    documents = create_sample_documents()
    
    # 对文档进行分类
    classified_docs = classifier.process_docs(documents)
    
    # 显示分类结果
    print("\n分类结果：")
    print("-" * 60)
    for i, doc in enumerate(classified_docs, 1):
        classification = doc.metadata.get('classification', '未分类')
        confidence = doc.metadata.get('classification_confidence', 0.0)
        source = doc.metadata.get('source', '未知')
        
        print(f"{i}. 文档: {source}")
        print(f"   分类: {classification}")
        print(f"   置信度: {confidence:.2f}")
        print(f"   内容预览: {doc.text[:50]}...")
        print()
    
    # 获取分类统计
    summary = classifier.get_classification_summary(classified_docs)
    print("分类统计摘要：")
    print("-" * 60)
    print(f"总文档数: {summary['total_documents']}")
    print(f"未分类文档数: {summary['unclassified_count']}")
    print(f"平均置信度: {summary['confidence_stats']['average']:.2f}")
    print(f"最高置信度: {summary['confidence_stats']['max']:.2f}")
    print(f"最低置信度: {summary['confidence_stats']['min']:.2f}")
    print("\n各类别文档数量:")
    for category, count in summary['category_counts'].items():
        print(f"  {category}: {count}")


def demo_chinese_classifier():
    """演示中文文档分类器"""
    print("\n" + "=" * 60)
    print("中文文档分类器演示")
    print("=" * 60)
    
    # 创建中文分类器实例
    classifier = ChineseDocumentClassifier()
    
    # 设置分类类别
    classifier.set_categories([
        '技术文档', '学术论文', '新闻资讯', '商业报告', 
        '法律文档', '教育材料', '医疗文档', '其他'
    ])
    
    # 添加中文关键词规则
    classifier.add_chinese_keyword_rule('技术文档', [
        'Python', '编程', '代码', 'API', '接口', '函数', '方法', '类', '模块', '开发', '技术', '系统'
    ])
    classifier.add_chinese_keyword_rule('学术论文', [
        '研究', '实验', '分析', '论文', '学术', '理论', '模型', '假设', '验证', '数据', '科学', '观察'
    ])
    classifier.add_chinese_keyword_rule('新闻资讯', [
        '消息', '新闻', '事件', '发生', '宣布', '融资', '公司', 'CEO', '市场', '报道', '记者'
    ])
    classifier.add_chinese_keyword_rule('商业报告', [
        '报告', '财务', '收入', '利润', '增长', '季度', '预算', '投资', '收益', '业务', '经营'
    ])
    classifier.add_chinese_keyword_rule('法律文档', [
        '法律', '法规', '合同', '协议', '权利', '义务', '责任', '争议', '诉讼', '法院', '律师'
    ])
    classifier.add_chinese_keyword_rule('教育材料', [
        '课程', '学习', '教学', '教材', '练习', '考试', '学生', '老师', '知识点', '教育', '培训'
    ])
    classifier.add_chinese_keyword_rule('医疗文档', [
        '患者', '疾病', '症状', '诊断', '治疗', '药物', '医生', '医院', '健康', '医疗', '临床'
    ])
    
    # 创建中文示例文档
    chinese_documents = [
        Document(
            text="Python是一种高级编程语言，具有简洁的语法和强大的功能。它广泛应用于Web开发、数据分析、人工智能等领域。",
            metadata={"source": "python教程.txt"}
        ),
        Document(
            text="本研究通过实验方法分析了机器学习算法在文本分类任务中的性能表现。实验结果表明，基于深度学习的模型在准确率方面显著优于传统方法。",
            metadata={"source": "机器学习论文.pdf"}
        ),
        Document(
            text="据最新消息，某科技公司今日宣布完成新一轮融资，融资金额达到1亿美元。该轮融资将主要用于产品研发和市场拓展。",
            metadata={"source": "科技新闻.txt"}
        ),
        Document(
            text="本季度财务报告显示，公司营业收入同比增长15%，净利润增长20%。主要增长动力来自于新产品的成功推出。",
            metadata={"source": "财务报告.pdf"}
        ),
        Document(
            text="根据《中华人民共和国合同法》相关规定，甲乙双方就软件开发项目达成如下协议：项目周期为6个月，总金额为100万元。",
            metadata={"source": "软件开发合同.docx"}
        ),
        Document(
            text="本课程将系统介绍数据结构与算法的基本概念和实现方法。内容包括：线性表、栈、队列、树、图等数据结构。",
            metadata={"source": "算法课程.md"}
        ),
        Document(
            text="患者主诉：头痛、发热、乏力3天。体格检查：体温38.5℃，血压正常。初步诊断：上呼吸道感染。",
            metadata={"source": "病历记录.txt"}
        )
    ]
    
    # 对文档进行分类
    classified_docs = classifier.process_docs(chinese_documents)
    
    # 显示分类结果
    print("\n中文文档分类结果：")
    print("-" * 60)
    for i, doc in enumerate(classified_docs, 1):
        classification = doc.metadata.get('classification', '未分类')
        confidence = doc.metadata.get('classification_confidence', 0.0)
        source = doc.metadata.get('source', '未知')
        
        print(f"{i}. 文档: {source}")
        print(f"   分类: {classification}")
        print(f"   置信度: {confidence:.2f}")
        print(f"   内容预览: {doc.text[:50]}...")
        print()
    
    # 获取文本统计信息
    print("文本统计信息：")
    print("-" * 60)
    for i, doc in enumerate(classified_docs, 1):
        stats = classifier.get_text_statistics(doc.text)
        print(f"文档 {i} ({doc.metadata.get('source', '未知')}):")
        print(f"  总字符数: {stats['total_chars']}")
        print(f"  总词数: {stats['total_words']}")
        print(f"  唯一词数: {stats['unique_words']}")
        print(f"  平均词长: {stats['avg_word_length']:.2f}")
        print(f"  高频词: {[word for word, count in stats['most_common_words'][:5]]}")
        print()


def demo_content_type_classification():
    """演示内容类型分类"""
    print("\n" + "=" * 60)
    print("内容类型自动分类演示")
    print("=" * 60)
    
    classifier = ChineseDocumentClassifier()
    
    # 测试不同类型的文档
    test_texts = [
        "这是一个Python编程教程，介绍了如何使用Python进行Web开发。",
        "本研究分析了深度学习在自然语言处理中的应用效果。",
        "今日股市收盘，上证指数上涨2.5%，成交量放大。",
        "公司第三季度财报显示，净利润同比增长30%。",
        "根据《民法典》规定，合同双方应当履行各自义务。",
        "本节课我们将学习数据结构中的二叉树遍历算法。",
        "患者出现发热、咳嗽等症状，建议进行血常规检查。"
    ]
    
    print("内容类型自动分类结果：")
    print("-" * 60)
    for i, text in enumerate(test_texts, 1):
        content_type = classifier.classify_by_content_type(text)
        print(f"{i}. 文本: {text[:30]}...")
        print(f"   内容类型: {content_type}")
        print()


def main():
    """主函数"""
    print("agentUniverse 文档分类器演示")
    print("=" * 60)
    
    try:
        # 基础分类器演示
        demo_basic_classifier()
        
        # 中文分类器演示
        demo_chinese_classifier()
        
        # 内容类型分类演示
        demo_content_type_classification()
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
