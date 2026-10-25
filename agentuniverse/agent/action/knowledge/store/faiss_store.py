# !/usr/bin/env python3

# @Time    : 2024/12/28 10:00
# @Author  : saswatsusmoy
# @Email   : saswatsusmoy9@gmail.com
# @FileName: faiss_store.py

import logging
import os
import pickle
from pathlib import Path
from typing import Any

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Module-level placeholders for optional dependencies; populated lazily
# by _new_client so that importing this module never requires faiss/numpy.
faiss = None
np = None

# Default configuration for FAISS index types
DEFAULT_INDEX_CONFIG = {
    "index_type": "IndexFlatL2",
    "dimension": 768,  # Default embedding dimension
    "nlist": 100,  # For IVF indexes
    "M": 16,  # For HNSW indexes
    "efConstruction": 200,  # For HNSW indexes
    "efSearch": 50,  # For HNSW indexes
    "nprobe": 10,  # For IVF search
}

# Set up logger
logger = logging.getLogger(__name__)


class FAISSStore(Store):
    """Object encapsulating the FAISS store that has vector search enabled.

    The FAISSStore object provides insert, query, update, and delete capabilities
    using Facebook's FAISS library for efficient similarity search.

    Attributes:
        index_path (Optional[str]): Path to save the FAISS index file.
        metadata_path (Optional[str]): Path to save the document metadata.
        index_config (Dict): Configuration for FAISS index creation.
        embedding_model (Optional[str]): Name of the embedding model to use.
        similarity_top_k (Optional[int]): Default number of top results to return.
        faiss_index (faiss.Index): The FAISS index object.
        document_store (Dict[str, Document]): In-memory document storage.
        id_to_index (Dict[str, int]): Mapping from document ID to FAISS index position.
        index_to_id (Dict[int, str]): Mapping from FAISS index position to document ID.
    """

    index_path: str | None = None
    metadata_path: str | None = None
    index_config: dict = None
    embedding_model: str | None = None
    similarity_top_k: int | None = 10
    faiss_index: Any = None
    document_store: dict[str, Document] = None
    id_to_index: dict[str, int] = None
    index_to_id: dict[int, str] = None
    _next_index: int = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.document_store = {}
        self.id_to_index = {}
        self.index_to_id = {}
        self._next_index = 0
        if self.index_config is None:
            self.index_config = DEFAULT_INDEX_CONFIG.copy()

    def _new_client(self) -> Any:
        """Initialize the FAISS index and load existing data if available."""
        global faiss, np
        if faiss is None or np is None:
            try:
                import faiss as _faiss
                import numpy as _np
            except ImportError as e:
                FAISS_NOT_INSTALLED_MSG = (
                    "FAISS is not installed. Please install it with 'pip install faiss-cpu' "
                    "for CPU version or 'pip install faiss-gpu' for GPU version."
                )
                raise ImportError(FAISS_NOT_INSTALLED_MSG) from e
            faiss = _faiss
            np = _np
        self._load_index_and_metadata()
        return self.faiss_index

    def _create_faiss_index(self, dimension: int):
        """Create a FAISS index based on the configuration.

        Args:
            dimension (int): The dimension of the vectors.

        Returns:
            faiss.Index: The created FAISS index.
        """
        index_type = self.index_config.get("index_type", "IndexFlatL2")

        if index_type == "IndexFlatL2":
            return faiss.IndexFlatL2(dimension)
        elif index_type == "IndexFlatIP":
            return faiss.IndexFlatIP(dimension)
        elif index_type == "IndexIVFFlat":
            nlist = self.index_config.get("nlist", 100)
            quantizer = faiss.IndexFlatL2(dimension)
            return faiss.IndexIVFFlat(quantizer, dimension, nlist)
        elif index_type == "IndexIVFPQ":
            nlist = self.index_config.get("nlist", 100)
            m = self.index_config.get("m", 8)  # Number of subquantizers
            nbits = self.index_config.get("nbits", 8)  # Bits per subquantizer
            quantizer = faiss.IndexFlatL2(dimension)
            return faiss.IndexIVFPQ(quantizer, dimension, nlist, m, nbits)
        elif index_type == "IndexHNSWFlat":
            M = self.index_config.get("M", 16)
            index = faiss.IndexHNSWFlat(dimension, M)
            index.hnsw.efConstruction = self.index_config.get("efConstruction", 200)
            index.hnsw.efSearch = self.index_config.get("efSearch", 50)
            return index
        else:
            UNSUPPORTED_INDEX_MSG = f"Unsupported index type: {index_type}"
            raise ValueError(UNSUPPORTED_INDEX_MSG)

    def _load_index_and_metadata(self):
        """Load existing FAISS index and metadata from disk."""
        if self.index_path and os.path.exists(self.index_path):
            try:
                self.faiss_index = faiss.read_index(self.index_path)
                logger.info(f"Loaded FAISS index from {self.index_path}")
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")
                self.faiss_index = None

        if self.metadata_path and os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, "rb") as f:
                    metadata = pickle.load(f)  # noqa: S301
                    self.document_store = metadata.get("document_store", {})
                    self.id_to_index = metadata.get("id_to_index", {})
                    self.index_to_id = metadata.get("index_to_id", {})
                    self._next_index = metadata.get("next_index", 0)
                logger.info(f"Loaded metadata from {self.metadata_path}")
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")
                self._reset_metadata()
        else:
            self._reset_metadata()

        # If no index was loaded and we have metadata, create empty index
        if self.faiss_index is None and self.document_store:
            # Try to infer dimension from existing documents
            for doc in self.document_store.values():
                if doc.embedding and len(doc.embedding) > 0:
                    dimension = len(doc.embedding)
                    self.faiss_index = self._create_faiss_index(dimension)
                    break

    def _reset_metadata(self) -> None:
        """Reset metadata to empty state."""
        self.document_store = {}
        self.id_to_index = {}
        self.index_to_id = {}
        self._next_index = 0

    def _remove_index_file(self) -> None:
        """Remove the persisted index; an already missing file is fine."""
        if not self.index_path:
            return
        try:
            os.remove(self.index_path)
        except FileNotFoundError:
            return
        except OSError:
            logger.exception("Failed to remove FAISS index file %s", self.index_path)

    def _save_index_and_metadata(self):
        """Save FAISS index and metadata to disk."""
        if self.faiss_index and self.index_path:
            try:
                # Ensure directory exists
                Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
                faiss.write_index(self.faiss_index, self.index_path)
                logger.info(f"Saved FAISS index to {self.index_path}")
            except Exception:
                logger.exception("Failed to save FAISS index")

        if self.metadata_path:
            try:
                # Ensure directory exists
                Path(self.metadata_path).parent.mkdir(parents=True, exist_ok=True)
                metadata = {
                    "document_store": self.document_store,
                    "id_to_index": self.id_to_index,
                    "index_to_id": self.index_to_id,
                    "next_index": self._next_index,
                }
                with open(self.metadata_path, "wb") as f:
                    pickle.dump(metadata, f)
                logger.info(f"Saved metadata to {self.metadata_path}")
            except Exception:
                logger.exception("Failed to save metadata")

    def _get_embedding(self, text: str, text_type: str = "document") -> list[float]:
        """Get embedding for a text using the configured embedding model.

        Args:
            text (str): The text to embed.
            text_type (str): Type of text ("document" or "query").

        Returns:
            List[float]: The embedding vector.
        """
        if not self.embedding_model:
            NO_EMBEDDING_MSG = "No embedding model configured. Please specify an embedding_model."
            raise ValueError(NO_EMBEDDING_MSG)

        try:
            embedding_instance = EmbeddingManager().get_instance_obj(self.embedding_model)
            embeddings = embedding_instance.get_embeddings([text], text_type=text_type)
            return embeddings[0] if embeddings else []
        except Exception as e:
            # For testing purposes, if embedding manager fails, return empty list
            logger.warning(f"Failed to get embeddings: {e}")
            return []

    def query(self, query: Query, **kwargs) -> list[Document]:  # noqa: C901
        """Query the FAISS index with the given query and return the top k results.

        Args:
            query (Query): The query object.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            List[Document]: List of documents retrieved by the query.
        """
        if not self.faiss_index or self.faiss_index.ntotal == 0:
            return []

        # Get query embedding
        embedding = query.embeddings
        if len(embedding) == 0:
            if not query.query_str:
                return []
            if self.embedding_model is None:
                logger.warning("No embeddings provided in query and no embedding model configured")
                return []
            embedding = [self._get_embedding(query.query_str, text_type="query")]

        if not embedding or len(embedding[0]) == 0:
            return []

        # Convert to numpy array
        query_vector = np.array(embedding, dtype=np.float32)
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        # Set search parameters for IVF indexes
        if hasattr(self.faiss_index, "nprobe"):
            self.faiss_index.nprobe = self.index_config.get("nprobe", 10)

        # Perform search
        k = query.similarity_top_k if query.similarity_top_k else self.similarity_top_k
        k = min(k, self.faiss_index.ntotal)  # Can't search for more than available

        try:
            distances, indices = self.faiss_index.search(query_vector, k)
        except Exception:
            logger.exception("Error during FAISS search")
            return []

        documents = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx not in self.index_to_id:
                continue
            document_id = self.index_to_id[idx]
            document = self.document_store.get(document_id)
            if document is None:
                continue
            documents.append(
                Document(
                    id=document.id,
                    text=document.text,
                    metadata={**(document.metadata or {}), "score": float(distances[0][i])},
                    embedding=document.embedding,
                )
            )
        return documents

    def insert_document(self, documents: list[Document], **kwargs) -> None:
        """Insert documents into the FAISS index.

        Args:
            documents (List[Document]): The documents to be inserted.
            **kwargs: Arbitrary keyword arguments.
        """
        if not documents:
            return
        new_documents = [
            document for document in documents if document.id not in self.document_store
        ]
        self._add_documents(new_documents)

    def _add_documents(self, documents: list[Document], skip_existing: bool = True) -> None:
        """Embed, index and persist documents in one pass.

        The vector produced for a document is written back to the document
        itself. Otherwise the stored copy has no embedding and a later rebuild
        (delete, load repair) either has to call the embedding model again or,
        when no model is configured, silently drops the document.
        """
        embeddings_to_add, docs_to_add = self._prepare_documents(documents, skip_existing)
        if not embeddings_to_add:
            return

        self._ensure_index(len(embeddings_to_add[0]), embeddings_to_add)
        embeddings_array = np.array(embeddings_to_add, dtype=np.float32)
        self.faiss_index.add(embeddings_array)

        first_position = self._next_index
        for offset, document in enumerate(docs_to_add):
            index_pos = first_position + offset
            self.document_store[document.id] = document
            self.id_to_index[document.id] = index_pos
            self.index_to_id[index_pos] = document.id

        self._next_index += len(docs_to_add)
        self._save_index_and_metadata()

    def _prepare_documents(
        self, documents: list[Document], skip_existing: bool
    ) -> tuple[list[list[float]], list[Document]]:
        """Collect vectors and the documents that own them, skipping unusable ones."""
        embeddings_to_add: list[list[float]] = []
        docs_to_add: list[Document] = []
        for document in documents:
            embedding = self._prepare_embedding(document, skip_existing)
            if embedding is None:
                continue
            document.embedding = embedding
            embeddings_to_add.append(embedding)
            docs_to_add.append(document)
        return embeddings_to_add, docs_to_add

    def _prepare_embedding(self, document: Document, skip_existing: bool) -> list[float] | None:
        """Return a vector for one document, or None when it cannot be indexed."""
        if skip_existing and document.id in self.document_store:
            return None

        embedding = document.embedding
        if not embedding:
            if self.embedding_model is None:
                logger.warning(
                    f"No embedding for document {document.id} and no embedding model configured, skipping"
                )
                return None
            embedding = self._get_embedding(document.text)

        if not embedding:
            logger.warning(f"No embedding for document {document.id}, skipping")
            return None

        index_dimension = getattr(self.faiss_index, "d", None) if self.faiss_index else None
        if index_dimension and len(embedding) != index_dimension:
            logger.warning(
                f"Embedding dimension {len(embedding)} for document {document.id} "
                f"does not match the index dimension {index_dimension}, skipping"
            )
            return None
        return list(embedding)

    def _ensure_index(self, dimension: int, vectors: list[list[float]]) -> None:
        """Create and (for IVF indexes) train the index when it does not exist yet."""
        if self.faiss_index is not None:
            return

        self.faiss_index = self._create_faiss_index(dimension)
        if hasattr(self.faiss_index, "is_trained") and not self.faiss_index.is_trained:
            nlist = self.index_config.get("nlist", 100)
            if len(vectors) < nlist:
                logger.warning(
                    f"Not enough vectors ({len(vectors)}) to train IVF index "
                    f"properly (need at least {nlist})"
                )
            self.faiss_index.train(np.array(vectors, dtype=np.float32))

    def upsert_document(self, documents: list[Document], **kwargs):
        """Upsert documents into the FAISS index."""
        # For FAISS, we need to delete and re-insert for updates
        docs_to_insert = []
        docs_to_update = []

        for document in documents:
            if document.id in self.document_store:
                docs_to_update.append(document)
            else:
                docs_to_insert.append(document)

        # Delete existing documents
        for document in docs_to_update:
            self.delete_document(document.id)

        # Insert all documents
        all_docs = docs_to_update + docs_to_insert
        self.insert_document(all_docs, **kwargs)

    def update_document(self, documents: list[Document], **kwargs):
        """Update documents in the FAISS index."""
        # For FAISS, update is the same as upsert
        self.upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs) -> None:
        """Delete a document from the FAISS index.

        FAISS doesn't support direct deletion, so the index is rebuilt from the
        remaining documents. The rebuild must bypass the "already stored" check
        used by ``insert_document``: the remaining documents are still in the
        catalog at that point, and skipping them all would leave the store with
        a populated catalog and no index at all.
        """
        if document_id not in self.document_store:
            return

        del self.document_store[document_id]
        if not self.document_store:
            self._reset_faiss_index()
            return
        self._rebuild_index()

    def _clear_index_state(self) -> None:
        """Forget the vectors while keeping the catalog untouched."""
        self.faiss_index = None
        self.id_to_index = {}
        self.index_to_id = {}
        self._next_index = 0

    def _rebuild_index(self) -> None:
        """Rebuild the vector index and id maps from the stored documents."""
        documents = list(self.document_store.values())
        self._clear_index_state()
        # _add_documents repopulates the catalog, so a document that cannot be
        # embedded again cannot leave a dangling metadata entry behind.
        self.document_store = {}
        self._add_documents(documents, skip_existing=False)
        if self.faiss_index is None:
            # Nothing could be embedded; make sure a stale index file cannot
            # resurrect the old vectors on the next load.
            self._remove_index_file()
            self._save_index_and_metadata()

    def _reset_faiss_index(self) -> None:
        """Drop every vector, the catalog and the persisted index file."""
        self._reset_metadata()
        self.faiss_index = None
        self._remove_index_file()
        self._save_index_and_metadata()

    def get_document_count(self) -> int:
        """Get the total number of documents in the store."""
        return len(self.document_store)

    def get_document_by_id(self, document_id: str) -> Document | None:
        """Get a document by its ID."""
        return self.document_store.get(document_id)

    def list_document_ids(self) -> list[str]:
        """List all document IDs in the store."""
        return list(self.document_store.keys())

    def _initialize_by_component_configer(self, faiss_store_configer: ComponentConfiger) -> "FAISSStore":
        """Initialize the FAISS store from configuration."""
        super()._initialize_by_component_configer(faiss_store_configer)

        if hasattr(faiss_store_configer, "index_path"):
            self.index_path = faiss_store_configer.index_path
        if hasattr(faiss_store_configer, "metadata_path"):
            self.metadata_path = faiss_store_configer.metadata_path
        if hasattr(faiss_store_configer, "index_config"):
            if self.index_config is None:
                self.index_config = DEFAULT_INDEX_CONFIG.copy()
            self.index_config.update(faiss_store_configer.index_config)
        if hasattr(faiss_store_configer, "embedding_model"):
            self.embedding_model = faiss_store_configer.embedding_model
        if hasattr(faiss_store_configer, "similarity_top_k"):
            self.similarity_top_k = faiss_store_configer.similarity_top_k

        return self
