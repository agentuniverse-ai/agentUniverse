# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: semantic_chunker.py

"""
Semantic chunker — a knowledge pre-processing DocProcessor.

Splits a document into semantically coherent chunks by grouping adjacent
sentences whose embedding similarity is above a threshold. When adjacent
sentences are semantically dissimilar (similarity drops below a breakpoint),
a new chunk begins. This produces chunks that respect topic boundaries
better than fixed-size splitters (character/token/recursive).

Two modes:
- **Embedding mode** (\`\`embedding_name\`\` configured): uses an aU embedding
  component to embed each sentence, then computes cosine similarity between
  adjacent sentence pairs and splits at the largest semantic gaps.
- **Extractive mode** (default, no \`\`embedding_name\`\`): a dependency-free
  fallback that groups sentences by lexical overlap (Jaccard similarity on
  word sets), producing coarser but still meaningful boundaries.

Addresses #258 (knowledge pre-processing components).
"""

import logging
import math
import re
from typing import Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.embedding.embedding_manager import \
    EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

# Sentence boundary: matches . ! ? followed by whitespace/end, or newline.
_SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+|\n+")
_MIN_SENTENCE_LEN = 10  # skip very short fragments


class SemanticChunker(DocProcessor):
    """Semantic similarity-based document chunker.

    Attributes:
        embedding_name: Name of a registered aU embedding component. When set,
            cosine similarity between adjacent sentence embeddings drives the
            splitting. When unset, a lexical-overlap fallback is used.
        breakpoint_threshold: Percentile of similarity drops that triggers a
            new chunk. Higher = fewer, larger chunks; lower = more, smaller
            chunks. Default 75 (top quartile of drops become split points).
        max_chunk_size: Maximum characters per chunk. A chunk exceeding this
            is hard-split at a sentence boundary.
        min_chunk_size: Minimum characters per chunk. Shorter chunks are
            merged into the next one.
    """

    embedding_name: Optional[str] = None
    breakpoint_threshold: int = 75
    max_chunk_size: int = 2000
    min_chunk_size: int = 100

    def _process_docs(self, origin_docs: List[Document],
                      query=None) -> List[Document]:
        if not origin_docs:
            return []
        result: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            for chunk_text in self._split_text(text):
                meta = dict(doc.metadata or {})
                meta["chunk_method"] = "semantic"
                result.append(Document(text=chunk_text, metadata=meta))
        return result

    def _split_text(self, text: str) -> List[str]:
        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            return [text] if text.strip() else []

        if self.embedding_name:
            split_points = self._find_split_points_embedding(sentences)
        else:
            split_points = self._find_split_points_lexical(sentences)

        chunks = self._build_chunks(sentences, split_points)
        return self._merge_small_and_split_large(chunks)

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        raw = _SENTENCE_PATTERN.split(text.strip())
        return [s.strip() for s in raw if len(s.strip()) >= _MIN_SENTENCE_LEN]

    # ------------------------------------------------------------------ #
    # Embedding-based splitting
    # ------------------------------------------------------------------ #
    def _find_split_points_embedding(self, sentences: List[str]) -> List[int]:
        try:
            model = EmbeddingManager().get_instance_obj(self.embedding_name)
            embeddings = model.get_embeddings(sentences)
        except Exception as exc:
            logger.warning("SemanticChunker: embedding failed (%s), "
                           "falling back to lexical", exc)
            return self._find_split_points_lexical(sentences)

        if not embeddings or len(embeddings) < len(sentences):
            return self._find_split_points_lexical(sentences)

        similarities = []
        for i in range(len(embeddings) - 1):
            sim = self._cosine(embeddings[i], embeddings[i + 1])
            similarities.append(sim)

        if not similarities:
            return []

        # The breakpoint is the percentile of the *drops* in similarity.
        # A large drop means the topic shifted.
        drops = []
        for i in range(len(similarities)):
            if i == 0:
                drops.append(similarities[i])
            else:
                drops.append(similarities[i] - similarities[i - 1])

        if not drops:
            return []

        threshold = self._percentile([abs(d) for d in drops],
                                     self.breakpoint_threshold)
        split_points = []
        for i, d in enumerate(drops):
            if abs(d) >= threshold and d < 0:
                split_points.append(i + 1)
        return split_points

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    @staticmethod
    def _percentile(values: List[float], pct: int) -> float:
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        idx = int(len(sorted_vals) * pct / 100)
        idx = min(idx, len(sorted_vals) - 1)
        return sorted_vals[idx]

    # ------------------------------------------------------------------ #
    # Lexical-overlap fallback
    # ------------------------------------------------------------------ #
    def _find_split_points_lexical(self, sentences: List[str]) -> List[int]:
        words_list = [set(s.lower().split()) for s in sentences]
        split_points = []
        for i in range(len(words_list) - 1):
            overlap = self._jaccard(words_list[i], words_list[i + 1])
            if overlap < 0.25:  # low overlap = topic shift
                split_points.append(i + 1)
        return split_points

    @staticmethod
    def _jaccard(a: set, b: set) -> float:
        if not a and not b:
            return 1.0
        union = a | b
        if not union:
            return 0.0
        return len(a & b) / len(union)

    # ------------------------------------------------------------------ #
    # Chunk assembly + post-processing
    # ------------------------------------------------------------------ #
    @staticmethod
    def _build_chunks(sentences: List[str], split_points: List[int]) -> List[str]:
        if not split_points:
            return [" ".join(sentences)] if sentences else []
        chunks = []
        prev = 0
        for sp in split_points:
            chunks.append(" ".join(sentences[prev:sp]).strip())
            prev = sp
        if prev < len(sentences):
            chunks.append(" ".join(sentences[prev:]).strip())
        return [c for c in chunks if c]

    def _merge_small_and_split_large(self, chunks: List[str]) -> List[str]:
        # Merge chunks below min_chunk_size into the next one.
        merged: List[str] = []
        for chunk in chunks:
            if merged and len(merged[-1]) < self.min_chunk_size:
                merged[-1] = merged[-1] + " " + chunk
            else:
                merged.append(chunk)
        # Hard-split chunks above max_chunk_size at sentence boundaries.
        result: List[str] = []
        for chunk in merged:
            if len(chunk) <= self.max_chunk_size:
                result.append(chunk)
            else:
                result.extend(self._hard_split(chunk))
        return result

    def _hard_split(self, text: str) -> List[str]:
        sentences = self._split_sentences(text)
        chunks = []
        current = ""
        for s in sentences:
            if len(current) + len(s) + 1 > self.max_chunk_size and current:
                chunks.append(current.strip())
                current = s
            else:
                current = (current + " " + s).strip() if current else s
        if current.strip():
            chunks.append(current.strip())
        return chunks

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> "SemanticChunker":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "embedding_name"):
            self.embedding_name = doc_processor_configer.embedding_name
        if hasattr(doc_processor_configer, "breakpoint_threshold"):
            self.breakpoint_threshold = doc_processor_configer.breakpoint_threshold
        if hasattr(doc_processor_configer, "max_chunk_size"):
            self.max_chunk_size = doc_processor_configer.max_chunk_size
        if hasattr(doc_processor_configer, "min_chunk_size"):
            self.min_chunk_size = doc_processor_configer.min_chunk_size
        return self
