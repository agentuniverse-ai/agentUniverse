# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/6 10:44
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: jieba_keyword_extractor.py
from typing import List

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

import jieba
import jieba.analyse

# nltk english stopwords
stop_words = {'or', "mustn't", 'how', 'their', 'again', 'few', 'other', 'who',
              'being', 'theirs', 'during', 'if', 'on', 'she', 'wouldn', 'why',
              'above', 'll', "weren't", 'your', 'are', 'an', 'over', 'his',
              'hasn', 'off', 'you', 'he', 'was', "you'd", 'me', 'ain', 'any',
              'what', 'most', 're', 'haven', "isn't", 'there', "it's", 'same',
              'm', 'only', 'my', 'needn', 'too', 'into', 'in', 'by', 'between',
              "that'll", "mightn't", "aren't", 'am', 'up', 'having', "you'll",
              "you're", 'these', 'mustn', 'himself', 'down', 'such', 'wasn',
              'ourselves', 'did', 'because', 'should', 'won', 'about', 'aren',
              'don', 'while', 't', 'isn', 'have', 'whom', 'myself', 'itself',
              'this', 'will', 'and', 'further', 'no', 'where', 'ma', 'yours',
              'been', "didn't", 'that', 'had', 'when', 'we', 'herself', 'some',
              'has', "she's", "needn't", "should've", 'of', "won't", 'both',
              'which', "haven't", 'yourself', 'through', 'the', 'from',
              "you've", 'for', 'then', 'hadn', 'a', 'them', 'as', 'after',
              'themselves', "shouldn't", 'they', 'y', 'doesn', 'didn', 'here',
              'ours', 'own', 'it', "hadn't", 'each', 'our', 'shouldn', 'all',
              'out', 'before', 'couldn', 'd', "doesn't", 'hers', "hasn't",
              'than', 'at', "don't", 'not', 'to', 'is', 'with', 'until',
              'does', 'yourselves', 'under', 'below', 'i', 'those', "wouldn't",
              'once', "couldn't", 'just', 's', 'shan', "wasn't", 'him', 'so',
              'can', 'doing', 'o', 'her', 'were', 'now', 'very', 'weren',
              'its', 'against', 'do', 've', 'be', 'mightn', 'but', "shan't",
              'nor', 'more'}

chinese_stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不',
                     '人', '都', '一', '一个', '上', '也', '很', '到', '说',
                     '要', '去', '你', '会', '着', '没有', '看', '好', '自己',
                     '请问', '您', '他', '于', '及', '即', '为', '最', '从', '以',
                     '了', '将', '与', '吗', '吧', '中', '#', '什么', '怎么', '哪个',
                     '哪些', '啥', '相关'}


class JiebaKeywordExtractor(DocProcessor):
    """Extracts keywords from documents using Jieba Chinese text segmentation."""
    top_k: int = 3

    def _process_docs(self, origin_docs: List[Document], query: Query = None) \
            -> List[Document]:
        """Extracts top keywords from documents after filtering stopwords.
        
        Args:
            origin_docs: List of documents to extract keywords from.
            query: Optional query object (not used in this processor).
            
        Returns:
            The original documents with keywords added to their metadata.
        """
        for _doc in origin_docs:
            words = jieba.lcut(_doc.text)
            filtered_words = [word for word in words if word not in
                              chinese_stopwords and word.lower() not in stop_words]
            keywords = jieba.analyse.extract_tags(" ".join(filtered_words),
                                                  topK=self.top_k)
            _doc.keywords.update(keywords)

        return origin_docs

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'DocProcessor':
        """Initializes the extractor with configuration parameters.
        
        Args:
            doc_processor_configer: Configuration object containing extractor parameters.
            
        Returns:
            Initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "top_k"):
            self.top_k = doc_processor_configer.top_k
        return self
