#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/23 16:25
# @Author  : SaladDay
# @FileName: epub_reader_demo.py

"""
EPUB Reader Demo

本demo展示了如何使用EpubReader来阅读EPUB电子书文件。
使用乔布斯传作为示例演示EPUB读取功能。
"""

import os
import requests
from pathlib import Path
from agentuniverse.agent.action.knowledge.reader.file.epub_reader import EpubReader
from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader

# 乔布斯传记EPUB文件配置
JOBS_BIOGRAPHY_URL = "https://drive.google.com/uc?export=download&id=1_KVCcPFatpe3Pl_4crIwLEWhMAUq3F0o"
JOBS_BIOGRAPHY_FILENAME = "steve_jobs_biography.epub"


def download_jobs_biography():
    """
    下载乔布斯传记EPUB文件
    """
    print("=== 下载乔布斯传记 ===")

    if Path(JOBS_BIOGRAPHY_FILENAME).exists():
        print(f"乔布斯传记文件已存在: {JOBS_BIOGRAPHY_FILENAME}")
        return True

    try:
        print("正在从Google Drive下载乔布斯传记...")
        response = requests.get(JOBS_BIOGRAPHY_URL, stream=True)
        response.raise_for_status()

        with open(JOBS_BIOGRAPHY_FILENAME, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"下载完成: {JOBS_BIOGRAPHY_FILENAME}")
        return True

    except Exception as e:
        print(f"下载失败: {e}")
        return False


def demo_epub_reader_direct():
    """
    直接使用EpubReader进行演示乔布斯传记
    """
    print("\n=== EPUB Reader Direct Usage Demo - 乔布斯传记 ===")

    # 初始化EPUB阅读器
    epub_reader = EpubReader()

    if Path(JOBS_BIOGRAPHY_FILENAME).exists():
        try:
            documents = epub_reader.load_data(JOBS_BIOGRAPHY_FILENAME)

            print(f"成功加载EPUB文件: {JOBS_BIOGRAPHY_FILENAME}")
            print(f"提取的章节数量: {len(documents)}")

            # 显示书籍元数据
            if documents:
                first_doc = documents[0]
                metadata = first_doc.metadata
                print(f"\n书籍信息:")
                print(f"标题: {metadata.get('title', 'Unknown')}")
                print(f"作者: {metadata.get('author', 'Unknown')}")
                print(f"语言: {metadata.get('language', 'Unknown')}")
                print(f"出版社: {metadata.get('publisher', 'Unknown')}")

                # 计算总字数
                total_words = sum(doc.metadata.get('word_count', 0) for doc in documents)
                print(f"总字数: {total_words:,}")

                # 显示前几章节
                print(f"\n前3章节预览:")
                for i, doc in enumerate(documents[:3]):
                    print(f"\n第{i+1}章 (文件: {doc.metadata.get('chapter_file', 'Unknown')}):")
                    print(f"字数: {doc.metadata.get('word_count', 0):,}")
                    # 显示前300个字符
                    content_preview = doc.text[:300] + "..." if len(doc.text) > 300 else doc.text
                    print(f"内容预览: {content_preview}")

        except Exception as e:
            print(f"读取EPUB文件时出错: {e}")
    else:
        print(f"EPUB文件不存在: {JOBS_BIOGRAPHY_FILENAME}")
        print("请先运行下载功能")


def demo_file_reader_auto_detection():
    """使用自动EPUB检测的FileReader演示乔布斯传记"""
    print("\n=== File Reader Auto Detection Demo - 乔布斯传记 ===")

    # 初始化文件阅读器
    file_reader = FileReader()

    # 乔布斯传记EPUB文件路径
    epub_file_path = Path(JOBS_BIOGRAPHY_FILENAME)

    if epub_file_path.exists():
        try:
            # FileReader将自动检测.epub扩展名并使用EpubReader
            documents = file_reader.load_data([epub_file_path])

            print(f"通过FileReader成功加载: {epub_file_path.name}")
            print(f"自动检测为EPUB格式")
            print(f"章节数量: {len(documents)}")

            # 显示所有章节的总字数
            total_words = sum(doc.metadata.get('word_count', 0) for doc in documents)
            print(f"总字数: {total_words:,}")

            # 分析章节分布
            if documents:
                print(f"\n章节分析:")
                longest_chapter = max(documents, key=lambda x: x.metadata.get('word_count', 0))
                shortest_chapter = min(documents, key=lambda x: x.metadata.get('word_count', 0))

                print(f"最长章节: {longest_chapter.metadata.get('chapter_file', 'Unknown')} ({longest_chapter.metadata.get('word_count', 0):,} 字)")
                print(f"最短章节: {shortest_chapter.metadata.get('chapter_file', 'Unknown')} ({shortest_chapter.metadata.get('word_count', 0):,} 字)")

                avg_words = total_words / len(documents) if documents else 0
                print(f"平均每章字数: {avg_words:,.0f}")

        except Exception as e:
            print(f"FileReader处理出错: {e}")
    else:
        print(f"EPUB文件不存在: {epub_file_path}")
        print("请先运行下载功能")


def demo_with_custom_metadata():
    """使用自定义元数据的EpubReader演示乔布斯传记"""
    print("\n=== EPUB Reader with Custom Metadata Demo - 乔布斯传记 ===")

    epub_reader = EpubReader()

    # 添加到每个文档的自定义元数据
    custom_metadata = {
        "source_type": "biography",
        "processing_date": "2025-09-23",
        "reader_version": "1.0",
        "category": "technology_biography",
        "subject": "Steve Jobs",
        "importance": "high",
        "language_original": "english"
    }

    if Path(JOBS_BIOGRAPHY_FILENAME).exists():
        try:
            # 加载自定义元数据
            documents = epub_reader.load_data(JOBS_BIOGRAPHY_FILENAME, ext_info=custom_metadata)

            print(f"加载带自定义元数据的乔布斯传记")
            print(f"文档数量: {len(documents)}")

            if documents:
                # 显示增强的元数据
                sample_doc = documents[0]
                print(f"\n增强元数据示例 (第1章):")
                for key, value in sample_doc.metadata.items():
                    print(f"  {key}: {value}")

                # 搜索特定关键词的章节
                print(f"\n关键词搜索示例:")
                keywords = ["Apple", "iPhone", "innovation", "design"]

                for keyword in keywords:
                    matching_chapters = []
                    for i, doc in enumerate(documents):
                        if keyword.lower() in doc.text.lower():
                            matching_chapters.append(i + 1)

                    if matching_chapters:
                        print(f"关键词 '{keyword}' 出现在章节: {matching_chapters[:5]}{'...' if len(matching_chapters) > 5 else ''} (共{len(matching_chapters)}章)")

        except Exception as e:
            print(f"自定义元数据处理出错: {e}")
    else:
        print(f"EPUB文件不存在: {JOBS_BIOGRAPHY_FILENAME}")
        print("请先运行下载功能")


def search_jobs_biography_content():
    """
    搜索乔布斯传记中的特定内容示例
    """
    print("\n=== 乔布斯传记内容搜索示例 ===")

    if not Path(JOBS_BIOGRAPHY_FILENAME).exists():
        print(f"EPUB文件不存在: {JOBS_BIOGRAPHY_FILENAME}")
        print("请先运行下载功能")
        return

    try:
        epub_reader = EpubReader()
        documents = epub_reader.load_data(JOBS_BIOGRAPHY_FILENAME)

        print(f"正在搜索乔布斯传记内容...")

        # 搜索关键主题
        search_topics = {
            "苹果公司创立": ["apple", "company", "founded", "start"],
            "个人电脑革命": ["personal computer", "pc", "macintosh", "mac"],
            "iPhone发布": ["iphone", "smartphone", "mobile"],
            "创新理念": ["innovation", "design", "think different"],
            "领导风格": ["leadership", "management", "team"]
        }

        topic_results = {}

        for topic, keywords in search_topics.items():
            matching_chapters = []
            for i, doc in enumerate(documents):
                text_lower = doc.text.lower()
                if any(keyword.lower() in text_lower for keyword in keywords):
                    matching_chapters.append({
                        'chapter_num': i + 1,
                        'file': doc.metadata.get('chapter_file', 'Unknown'),
                        'word_count': doc.metadata.get('word_count', 0)
                    })

            topic_results[topic] = matching_chapters

        # 显示搜索结果
        for topic, chapters in topic_results.items():
            if chapters:
                print(f"\n📖 {topic}:")
                print(f"   找到 {len(chapters)} 个相关章节")
                for chapter in chapters[:3]:  # 只显示前3个
                    print(f"   - 第{chapter['chapter_num']}章: {chapter['file']} ({chapter['word_count']:,} 字)")
                if len(chapters) > 3:
                    print(f"   ... 还有 {len(chapters) - 3} 个章节")
            else:
                print(f"\n📖 {topic}: 未找到相关内容")

        # 统计信息
        total_chapters = len(documents)
        total_words = sum(doc.metadata.get('word_count', 0) for doc in documents)

        print(f"\n📊 统计信息:")
        print(f"   总章节数: {total_chapters}")
        print(f"   总字数: {total_words:,}")
        print(f"   平均每章字数: {total_words // total_chapters:,}")

    except Exception as e:
        print(f"搜索过程中出错: {e}")


if __name__ == "__main__":
    print("🍎 乔布斯传记 EPUB Reader Demo")
    print("=" * 40)
    print("使用agentUniverse框架读取乔布斯传记EPUB文件")

    # 下载乔布斯传记
    if download_jobs_biography():
        # 运行所有演示
        demo_epub_reader_direct()
        demo_file_reader_auto_detection()
        demo_with_custom_metadata()
        search_jobs_biography_content()

        print("\n" + "=" * 40)
        print("🎉 演示完成！")
        print("\n📚 关于这本书:")
        print("《乔布斯传》是沃尔特·艾萨克森所著的史蒂夫·乔布斯官方传记")
        print("详细记录了乔布斯的生平、苹果公司的发展历程以及他对科技行业的影响")

    else:
        print("\n❌ 无法下载乔布斯传记文件，演示终止")

    print("\n💡 使用提示:")
    print("1. 安装依赖: pip install EbookLib requests")
    print("2. 可选安装BeautifulSoup以获得更好的HTML解析: pip install beautifulsoup4")
    print("3. 修改JOBS_BIOGRAPHY_URL变量以使用其他EPUB文件")
