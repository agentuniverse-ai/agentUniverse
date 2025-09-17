# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/8 15:23
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: temp.py
import jieba
from collections import defaultdict, Counter
import math


# 构建倒排索引
def build_inverted_index(corpus):
    inverted_index = defaultdict(list)
    for idx, document in enumerate(corpus):
        words = jieba.lcut(document)
        for word in set(words):
            inverted_index[word].append(idx)
    return inverted_index


# 计算 BM25
def compute_bm25(query, doc_id, corpus, inverted_index, k1=1.5, b=0.75):
    query_words = jieba.lcut(query)
    doc_words = jieba.lcut(corpus[doc_id])
    doc_length = len(doc_words)
    avg_doc_length = sum(len(jieba.lcut(doc)) for doc in corpus) / len(corpus)
    bm25_score = 0

    doc_counter = Counter(doc_words)

    for term in query_words:
        if term in inverted_index:
            term_freq = doc_counter[term]
            num_docs_with_term = len(inverted_index[term])
            idf = math.log((len(corpus) - num_docs_with_term + 0.5) / (num_docs_with_term + 0.5) + 1)
            bm25_term_score = (
                idf * (term_freq * (k1 + 1)) / (term_freq + k1 * (1 - b + b * (doc_length / avg_doc_length)))
            )
            bm25_score += bm25_term_score

    return bm25_score


# 示例数据
corpus = [
    "自然语言处理是人工智能的一个重要方向",
    "我喜欢学习新的技术",
    "自然语言处理包括很多技术，比如分词、词性标注、命名实体识别等",
]

# 构建倒排索引
inverted_index = build_inverted_index(corpus)

# 查询
query = "自然语言处理"
scores = {idx: compute_bm25(query, idx, corpus, inverted_index) for idx in range(len(corpus))}

# 排序并输出最相关的文档
sorted_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
for doc_id, score in sorted_docs:
    print(f"文档ID: {doc_id}, BM25分数: {score}, 内容: {corpus[doc_id]}")

if __name__ == "__main__":
    print("test")
