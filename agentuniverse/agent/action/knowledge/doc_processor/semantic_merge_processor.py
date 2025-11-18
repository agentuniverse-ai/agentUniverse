# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/18 16:00
# @Author  : gaobaichuan.gbc
# @Email   : gaobaichuan.gbc@antgroup.com
# @FileName: semantic_merge_processor.py

from typing import List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SemanticMergeProcessor(DocProcessor):
    """Document processor that merges similar texts based on TF-IDF and cosine similarity.

    This processor groups similar documents together using TF-IDF vectorization and
    cosine similarity, then selects the highest scoring document from each group.

    Attributes:
        similarity_threshold: Threshold for cosine similarity to consider texts as similar.
        min_group_size: Minimum number of documents in a similarity group.
    """
    similarity_threshold: float = 0.2
    min_group_size: int = 2

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        """Process documents by merging similar texts.

        Args:
            origin_docs: List of documents to be processed.
            query: Query object (not used in this processor).

        Returns:
            List[Document]: Processed documents with similar texts merged.
        """
        if len(origin_docs) < self.min_group_size:
            return origin_docs

        # Extract document text and remove newlines
        texts = [doc.text.replace('\n', '') for doc in origin_docs]

        # Vectorize text using TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # Add stop words as needed
            lowercase=True
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

        # Calculate cosine similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)
        # Use similarity matrix to create similar document groups
        visited = [False] * len(origin_docs)
        similarity_groups = []

        for i in range(len(origin_docs)):
            if not visited[i]:
                group = [i]
                visited[i] = True
                # Find other documents similar to the current document
                for j in range(len(origin_docs)):
                    if i != j and not visited[j] and similarity_matrix[i][j] >= self.similarity_threshold:
                        group.append(j)
                        visited[j] = True
                # If group size is greater than or equal to minimum group size, add to similarity group list
                if len(group) >= self.min_group_size:
                    similarity_groups.append(group)

        # For each similar document group, select the document with the highest relevance score
        merged_docs = []
        used_indices = set()

        for group in similarity_groups:
            if not group:
                continue

            # Find the document with the highest relevance score in the group
            max_score = -1
            best_doc_idx = group[0]

            for doc_idx in group:
                score = origin_docs[doc_idx].metadata.get("relevance_score", 0.0)
                if score > max_score:
                    max_score = score
                    best_doc_idx = doc_idx

            # Create merged document, preserving original metadata and source set
            best_doc = origin_docs[best_doc_idx]

            # Add merge information
            if best_doc.metadata:
                best_doc.metadata["merged_from"] = f"[{', '.join(map(str, group))}]"
                best_doc.metadata["merge_count"] = len(group)
            else:
                best_doc.metadata = {
                    "merged_from": f"[{', '.join(map(str, group))}]",
                    "merge_count": len(group),
                    "relevance_score": max_score
                }

            merged_docs.append(best_doc)
            used_indices.update(group)

        # Add documents that do not belong to any similar group
        for i in range(len(origin_docs)):
            if i not in used_indices:
                merged_docs.append(origin_docs[i])

        return merged_docs

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'DocProcessor':
        """Initialize processor parameters from component configuration.

        Args:
            doc_processor_configer: Configuration object containing processor parameters.

        Returns:
            DocProcessor: The initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "similarity_threshold"):
            self.similarity_threshold = doc_processor_configer.similarity_threshold
        if hasattr(doc_processor_configer, "min_group_size"):
            self.min_group_size = doc_processor_configer.min_group_size
        return self
