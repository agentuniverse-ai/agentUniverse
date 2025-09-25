# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/24
# @Author  : GPT-5
# @FileName: faiss_store.py

from __future__ import annotations

from typing import List, Optional, Any
import os

try:
    import faiss  # type: ignore
except ImportError as e:
    raise ImportError(
        "faiss is not installed. Please install it with 'pip install faiss-cpu' or 'faiss-gpu'"
    ) from e

import numpy as np

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class FaissStore(Store):
    """A lightweight FAISS-based vector store with optional persistence.

    Attributes:
        embedding_model: Name of embedding component used when inputs lack vectors
        index_path: Optional path to persist/load FAISS index
        dimension: Vector dimension (required if creating a fresh index without data)
        similarity_top_k: Default top-k for search
    """

    embedding_model: Optional[str] = None
    index_path: Optional[str] = None
    dimension: Optional[int] = None
    similarity_top_k: Optional[int] = 10

    _index: Optional[Any] = None
    _ids: List[str] = []
    _metas: List[Optional[dict]] = []
    _texts: List[str] = []

    def _new_client(self) -> Any:
        if self.index_path and os.path.exists(self.index_path):
            self._index = faiss.read_index(self.index_path)
        return self._index

    def _new_async_client(self) -> Any:
        return self._new_client()

    def _save_if_needed(self):
        if self.index_path and self._index is not None:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self._index, self.index_path)

    def _ensure_index(self, dim: int):
        if self._index is None:
            self._index = faiss.IndexFlatIP(dim)

    def _append_meta(self, docs: List[Document]):
        for d in docs:
            self._ids.append(d.id)
            self._metas.append(d.metadata)
            self._texts.append(d.text or "")

    @staticmethod
    def _as_np(embs: List[List[float]]) -> np.ndarray:
        arr = np.asarray(embs, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
        return arr / norms

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.embedding_model:
            raise ValueError("embedding_model is required when embeddings are not provided")
        return EmbeddingManager().get_instance_obj(self.embedding_model).get_embeddings(texts)

    def query(self, query: Query, **kwargs) -> List[Document]:
        top_k = query.similarity_top_k if query.similarity_top_k else self.similarity_top_k
        if self._index is None or len(self._ids) == 0:
            return []
        q_embs = query.embeddings
        if not q_embs:
            q_embs = [self._embed_texts([query.query_str or ""])[0]]
        q = self._as_np(q_embs)
        scores, idxs = self._index.search(q, top_k)
        result: List[Document] = []
        for i in idxs[0]:
            if i == -1:
                continue
            result.append(Document(id=self._ids[i],
                                   text=self._texts[i],
                                   embedding=[],
                                   metadata=self._metas[i]))
        return result

    def insert_document(self, documents: List[Document], **kwargs):
        if not documents:
            return
        embeddings: List[List[float]] = []
        to_embed: List[str] = []
        pos: List[int] = []
        for i, d in enumerate(documents):
            if d.embedding:
                embeddings.append(d.embedding)
            else:
                to_embed.append(d.text or "")
                pos.append(i)
        if to_embed:
            embs = self._embed_texts(to_embed)
            for p, e in zip(pos, embs):
                documents[p].embedding = e
                embeddings.append(e)
        if not embeddings:
            return
        dim = len(embeddings[0]) if embeddings else (self.dimension or 0)
        if dim <= 0:
            raise ValueError("FAISS index dimension cannot be determined")
        self._ensure_index(dim)
        self._index.add(self._as_np(embeddings))
        self._append_meta(documents)
        self._save_if_needed()

    def upsert_document(self, documents: List[Document], **kwargs):
        if not documents:
            return
        target_ids = {d.id for d in documents}
        if self._ids:
            keep = [i for i, _id in enumerate(self._ids) if _id not in target_ids]
            if len(keep) != len(self._ids):
                kept_docs = [Document(id=self._ids[i], text=self._texts[i], metadata=self._metas[i]) for i in keep]
                self._index = None
                self._ids, self._texts, self._metas = [], [], []
                self.insert_document(kept_docs)
        self.insert_document(documents)

    def delete_document(self, document_id: str, **kwargs):
        if document_id in self._ids:
            idx = self._ids.index(document_id)
            kept_docs = [Document(id=self._ids[i], text=self._texts[i], metadata=self._metas[i])
                         for i in range(len(self._ids)) if i != idx]
            self._index = None
            self._ids, self._texts, self._metas = [], [], []
            self.insert_document(kept_docs)

    def update_document(self, documents: List[Document], **kwargs):
        self.upsert_document(documents, **kwargs)

    def _initialize_by_component_configer(self, store_configer: ComponentConfiger) -> 'FaissStore':
        super()._initialize_by_component_configer(store_configer)
        if hasattr(store_configer, 'embedding_model'):
            self.embedding_model = store_configer.embedding_model
        if hasattr(store_configer, 'index_path'):
            self.index_path = store_configer.index_path
        if hasattr(store_configer, 'dimension'):
            self.dimension = store_configer.dimension
        if hasattr(store_configer, 'similarity_top_k'):
            self.similarity_top_k = store_configer.similarity_top_k
        return self


