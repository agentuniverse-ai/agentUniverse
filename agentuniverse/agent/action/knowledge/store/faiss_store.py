# !/usr/bin/env python3
# ruff: noqa: TRY003

# @Time    : 2024/12/28 10:00
# @Author  : saswatsusmoy
# @Email   : saswatsusmoy9@gmail.com
# @FileName: faiss_store.py

import logging
import math
import os
import pickle
from numbers import Real
from pathlib import Path
from typing import Any, ClassVar

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
    "dimension": None,  # Infer from the first accepted embedding when omitted
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

    _SUPPORTED_INDEX_TYPES: ClassVar[frozenset[str]] = frozenset(
        {"IndexFlatL2", "IndexFlatIP", "IndexIVFFlat", "IndexIVFPQ", "IndexHNSWFlat"}
    )
    _FLOAT32_MAX: ClassVar[float] = 3.4028234663852886e38

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
        self._validate_config()
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
        self._expected_dimension()
        return self.faiss_index

    def _create_faiss_index(self, dimension: int):
        """Create a FAISS index based on the configuration.

        Args:
            dimension (int): The dimension of the vectors.

        Returns:
            faiss.Index: The created FAISS index.
        """
        self._validate_config()
        self._validate_positive_integer(dimension, "dimension")

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
            if dimension % m:
                raise ValueError("IndexIVFPQ dimension must be divisible by m")
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

    def _reset_metadata(self):
        """Reset metadata to empty state."""
        self.document_store = {}
        self.id_to_index = {}
        self.index_to_id = {}
        self._next_index = 0

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
        self._validate_config()
        k = self._top_k(query)

        embedding = query.embeddings
        query_embedding = None
        if embedding:
            if len(embedding) != 1:
                raise ValueError("FAISSStore.query accepts exactly one embedding vector")
            query_embedding = self._validate_vector(
                embedding[0],
                expected_dimension=self._expected_dimension(),
                field_name="query embedding",
            )

        if not self.faiss_index or self.faiss_index.ntotal == 0:
            return []

        # Get a query embedding only when the caller did not supply one.
        if query_embedding is None:
            if not query.query_str:
                return []
            if self.embedding_model is None:
                logger.warning("No embeddings provided in query and no embedding model configured")
                return []
            query_embedding = self._get_embedding(query.query_str, text_type="query")
            if not query_embedding:
                return []
            query_embedding = self._validate_vector(
                query_embedding,
                expected_dimension=self._expected_dimension(),
                field_name="query embedding",
            )

        # Convert to numpy array
        query_vector = np.array([query_embedding], dtype=np.float32)

        # Set search parameters for IVF indexes
        if hasattr(self.faiss_index, "nprobe"):
            self.faiss_index.nprobe = self.index_config.get("nprobe", 10)

        # Perform search
        k = min(k, self.faiss_index.ntotal)  # Can't search for more than available

        try:
            distances, indices = self.faiss_index.search(query_vector, k)

            # Convert results to documents
            documents = []
            for i, idx in enumerate(indices[0]):
                if idx != -1 and idx in self.index_to_id:
                    doc_id = self.index_to_id[idx]
                    if doc_id in self.document_store:
                        doc = self.document_store[doc_id]
                        # Add distance/score to metadata
                        doc_copy = Document(
                            id=doc.id,
                            text=doc.text,
                            metadata={**(doc.metadata or {}), "score": float(distances[0][i])},
                            embedding=doc.embedding,
                        )
                        documents.append(doc_copy)
            else:
                return documents
        except Exception:
            logger.exception("Error during FAISS search")
            return []

    def insert_document(self, documents: list[Document], **kwargs):
        """Insert documents into the FAISS index.

        Args:
            documents (List[Document]): The documents to be inserted.
            **kwargs: Arbitrary keyword arguments.
        """
        docs_to_add, embeddings_to_add = self._prepare_documents(documents, skip_existing=True)
        self._insert_prevalidated(docs_to_add, embeddings_to_add)

    def _insert_prevalidated(
        self,
        docs_to_add: list[Document],
        embeddings_to_add: list[list[float]],
    ) -> None:
        """Insert a fully validated batch into FAISS and its ID mappings."""
        if not docs_to_add:
            return

        # Initialize index if needed
        if self.faiss_index is None:
            dimension = len(embeddings_to_add[0])
            self.faiss_index = self._create_faiss_index(dimension)

            # Train index if needed (for IVF indexes)
            if hasattr(self.faiss_index, "is_trained") and not self.faiss_index.is_trained:
                nlist = self.index_config.get("nlist", 100)
                if len(embeddings_to_add) < nlist:
                    warning_msg = (
                        f"Not enough vectors ({len(embeddings_to_add)}) to train IVF index "
                        f"properly (need at least {nlist})"
                    )
                    logger.warning(warning_msg)
                train_vectors = np.array(embeddings_to_add, dtype=np.float32)
                self.faiss_index.train(train_vectors)

        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings_to_add, dtype=np.float32)

        # Add to FAISS index
        self.faiss_index.add(embeddings_array)

        # Update metadata
        for i, document in enumerate(docs_to_add):
            index_pos = self._next_index + i
            self.document_store[document.id] = document
            self.id_to_index[document.id] = index_pos
            self.index_to_id[index_pos] = document.id

        self._next_index += len(docs_to_add)

        # Save to disk
        self._save_index_and_metadata()

    def upsert_document(self, documents: list[Document], **kwargs):
        """Upsert documents into the FAISS index."""
        prepared_documents, prepared_embeddings = self._prepare_documents(documents, skip_existing=False)

        # For FAISS, we need to delete and re-insert for updates
        docs_to_insert = []
        docs_to_update = []

        for document in prepared_documents:
            if document.id in self.document_store:
                docs_to_update.append(document)
            else:
                docs_to_insert.append(document)

        # Delete existing documents
        for document in docs_to_update:
            self.delete_document(document.id)

        # Insert all documents
        all_docs = docs_to_update + docs_to_insert
        embeddings_by_id = {
            document.id: embedding for document, embedding in zip(prepared_documents, prepared_embeddings, strict=True)
        }
        self._insert_prevalidated(all_docs, [embeddings_by_id[document.id] for document in all_docs])

    def update_document(self, documents: list[Document], **kwargs):
        """Update documents in the FAISS index."""
        # For FAISS, update is the same as upsert
        self.upsert_document(documents, **kwargs)

    def delete_document(self, document_id: str, **kwargs):
        """Delete a document from the FAISS index.

        Note: FAISS doesn't support direct deletion, so we rebuild the index
        without the deleted document.
        """
        if document_id not in self.document_store:
            return

        # Remove from metadata
        del self.document_store[document_id]
        if document_id in self.id_to_index:
            del self.id_to_index[document_id]

        # Rebuild index_to_id mapping
        self.index_to_id = {v: k for k, v in self.id_to_index.items()}

        # For simplicity, we rebuild the entire index
        # In production, you might want to use a more efficient approach
        if self.document_store:
            documents = list(self.document_store.values())
            self._reset_faiss_index()
            self.insert_document(documents)
        else:
            self._reset_faiss_index()

    def _reset_faiss_index(self):
        """Reset the FAISS index to empty state."""
        self.faiss_index = None
        self.id_to_index = {}
        self.index_to_id = {}
        self._next_index = 0
        self._save_index_and_metadata()

    @staticmethod
    def _validate_positive_integer(value: Any, field_name: str) -> int:
        """Validate a positive integer configuration value."""
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{field_name} must be a positive integer")
        return value

    def _validate_config(self) -> None:
        """Validate FAISS settings before creating or mutating an index."""
        self._validate_config_values(self.index_config, self.similarity_top_k)

    def _validate_config_values(self, index_config: Any, similarity_top_k: Any) -> None:  # noqa: C901
        """Validate candidate settings without mutating the store."""
        if not isinstance(index_config, dict):
            raise TypeError("index_config must be an object")

        index_type = index_config.get("index_type", "IndexFlatL2")
        if not isinstance(index_type, str):
            raise TypeError("index_config.index_type must be a string")
        if index_type not in self._SUPPORTED_INDEX_TYPES:
            raise ValueError(f"Unsupported index type: {index_type}")

        dimension = index_config.get("dimension")
        if dimension is not None:
            self._validate_positive_integer(dimension, "index_config.dimension")

        if index_type in {"IndexIVFFlat", "IndexIVFPQ"}:
            self._validate_positive_integer(index_config.get("nlist", 100), "index_config.nlist")
            self._validate_positive_integer(index_config.get("nprobe", 10), "index_config.nprobe")

        if index_type == "IndexIVFPQ":
            m = self._validate_positive_integer(index_config.get("m", 8), "index_config.m")
            nbits = self._validate_positive_integer(index_config.get("nbits", 8), "index_config.nbits")
            if nbits > 24:
                raise ValueError("index_config.nbits must not exceed 24")
            if dimension is not None and dimension % m:
                raise ValueError("IndexIVFPQ dimension must be divisible by m")

        if index_type == "IndexHNSWFlat":
            for field_name, default in (("M", 16), ("efConstruction", 200), ("efSearch", 50)):
                self._validate_positive_integer(
                    index_config.get(field_name, default),
                    f"index_config.{field_name}",
                )

        if similarity_top_k is not None:
            self._validate_positive_integer(similarity_top_k, "similarity_top_k")

    def _prepare_documents(  # noqa: C901
        self,
        documents: Any,
        *,
        skip_existing: bool,
    ) -> tuple[list[Document], list[list[float]]]:
        """Materialize and validate a document batch before any index mutation."""
        if documents is None:
            return [], []
        try:
            documents = list(documents)
        except TypeError as exc:
            raise TypeError("documents must be an iterable of Document objects") from exc
        if not documents:
            return [], []
        if any(not isinstance(document, Document) for document in documents):
            raise TypeError("documents must contain only Document objects")

        self._validate_config()
        document_ids = [document.id for document in documents]
        if len(document_ids) != len(set(document_ids)):
            raise ValueError("documents must not contain duplicate IDs within one batch")

        candidates = []
        for document in documents:
            if skip_existing and document.id in self.document_store:
                continue

            embedding = document.embedding
            if not embedding:
                if self.embedding_model is not None:
                    embedding = self._get_embedding(document.text)
                else:
                    logger.warning(
                        f"No embedding for document {document.id} and no embedding model configured, skipping"
                    )
                    continue

            if not embedding:
                logger.warning(f"No embedding for document {document.id}, skipping")
                continue
            candidates.append((document, embedding))

        expected_dimension = self._expected_dimension()
        prepared_documents = []
        prepared_embeddings = []
        for document, embedding in candidates:
            validated_embedding = self._validate_vector(
                embedding,
                expected_dimension=expected_dimension,
                field_name="document embedding",
            )
            expected_dimension = expected_dimension or len(validated_embedding)
            prepared_documents.append(document)
            prepared_embeddings.append(validated_embedding)
        return prepared_documents, prepared_embeddings

    def _expected_dimension(self) -> int | None:
        """Return the configured/current dimension and reject disagreement."""
        configured_dimension = self.index_config.get("dimension")
        index_dimension = getattr(self.faiss_index, "d", None) if self.faiss_index is not None else None
        if index_dimension is not None:
            self._validate_positive_integer(index_dimension, "FAISS index dimension")
        if configured_dimension is not None and index_dimension is not None and configured_dimension != index_dimension:
            raise ValueError(
                f"FAISS index dimension {index_dimension} does not match configured dimension {configured_dimension}"
            )
        return index_dimension or configured_dimension

    def _validate_vector(
        self,
        vector: Any,
        *,
        expected_dimension: int | None,
        field_name: str,
    ) -> list[float]:
        """Return a finite FLOAT32-compatible vector with a validated shape."""
        if not isinstance(vector, list | tuple) or not vector:
            raise ValueError(f"{field_name} must be a non-empty numeric list")

        validated = []
        for value in vector:
            if isinstance(value, bool) or not isinstance(value, Real):
                raise ValueError(f"{field_name} must contain only finite numbers")  # noqa: TRY004
            converted = float(value)
            if not math.isfinite(converted) or abs(converted) > self._FLOAT32_MAX:
                raise ValueError(f"{field_name} must contain only finite FLOAT32-compatible numbers")
            validated.append(converted)

        if expected_dimension is not None and len(validated) != expected_dimension:
            raise ValueError(
                f"{field_name} dimension {len(validated)} does not match expected dimension {expected_dimension}"
            )
        return validated

    def _top_k(self, query: Query) -> int:
        """Resolve and validate the query-specific or default result count."""
        value = query.similarity_top_k if query.similarity_top_k is not None else self.similarity_top_k
        return self._validate_positive_integer(value, "similarity_top_k")

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
        configured_index = self.index_config
        if not isinstance(configured_index, dict):
            raise TypeError("index_config must be an object")
        if hasattr(faiss_store_configer, "index_config"):
            index_overrides = faiss_store_configer.index_config
            if not isinstance(index_overrides, dict):
                raise TypeError("index_config must be an object")
            configured_index = {**configured_index, **index_overrides}
        configured_top_k = (
            faiss_store_configer.similarity_top_k
            if hasattr(faiss_store_configer, "similarity_top_k")
            else self.similarity_top_k
        )
        self._validate_config_values(configured_index, configured_top_k)

        super()._initialize_by_component_configer(faiss_store_configer)

        if hasattr(faiss_store_configer, "index_path"):
            self.index_path = faiss_store_configer.index_path
        if hasattr(faiss_store_configer, "metadata_path"):
            self.metadata_path = faiss_store_configer.metadata_path
        if hasattr(faiss_store_configer, "index_config"):
            self.index_config = configured_index
        if hasattr(faiss_store_configer, "embedding_model"):
            self.embedding_model = faiss_store_configer.embedding_model
        if hasattr(faiss_store_configer, "similarity_top_k"):
            self.similarity_top_k = configured_top_k

        return self
