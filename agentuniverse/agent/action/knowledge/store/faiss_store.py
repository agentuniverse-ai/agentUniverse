# !/usr/bin/env python3

# @Time    : 2024/12/28 10:00
# @Author  : saswatsusmoy
# @Email   : saswatsusmoy9@gmail.com
# @FileName: faiss_store.py

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# faiss and numpy are imported at module scope so every method (query / insert /
# _create_faiss_index / ...) sees the same names. They are optional dependencies:
# a hard module-level import would break environments without faiss installed,
# so each is wrapped and ``_new_client`` surfaces a clear ImportError when the
# store is actually used.
try:
    import faiss  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised via the skip guard in tests
    faiss = None  # type: ignore[assignment]

try:
    import numpy as np  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - numpy ships with faiss-cpu
    np = None  # type: ignore[assignment]

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

# On-disk metadata format tag, so future format changes can be detected/migrated.
METADATA_FORMAT_VERSION = "faiss-store-metadata-v1"

# Set up logger
logger = logging.getLogger(__name__)


def _json_default(obj):
    """Fallback JSON serializer normalizing numpy values that may reach metadata."""
    if np is not None:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.generic):
            return obj.item()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _require_dict(value: Any) -> dict:
    """Return ``value`` if it is a dict, else raise TypeError."""
    if not isinstance(value, dict):
        raise TypeError("value must be an object")
    return value


def _require_str(value: Any) -> str:
    """Return ``value`` if it is a str, else raise TypeError."""
    if not isinstance(value, str):
        raise TypeError("value must be a string")
    return value


def _require_int(value: Any) -> int:
    """Return ``value`` if it is a real integer, else raise TypeError.

    Booleans are rejected explicitly: ``isinstance(True, int)`` is True in
    Python, so a bare isinstance check would silently accept them.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("value must be an integer")
    return value


def _validate_metadata_payload(
    metadata: Any,
) -> tuple[dict[str, "Document"], dict[str, int], dict[int, str], int]:
    """Validate the loaded metadata envelope and reconstruct typed fields.

    Raises ``ValueError`` (structural/schema) or ``TypeError`` (individual
    fields with the wrong type) on any problem so the caller can reset the
    store as one coherent unit instead of half-populating it: wrong ``format``
    marker, non-object top level, malformed ``Document`` payloads, or
    ``index_to_id`` keys that are not integer FAISS positions.
    """
    if not isinstance(metadata, dict):
        raise TypeError("invalid metadata envelope")
    if metadata.get("format") != METADATA_FORMAT_VERSION:
        raise ValueError("unsupported metadata format marker")

    document_store_raw = _require_dict(metadata.get("document_store", {}))
    id_to_index_raw = _require_dict(metadata.get("id_to_index", {}))
    index_to_id_raw = _require_dict(metadata.get("index_to_id", {}))
    next_index = _require_int(metadata.get("next_index", 0))

    document_store: dict[str, Document] = {}
    for doc_id, doc_data in document_store_raw.items():
        _require_str(doc_id)
        _require_dict(doc_data)
        document_store[doc_id] = Document(**doc_data)

    id_to_index: dict[str, int] = {}
    for doc_id, position in id_to_index_raw.items():
        _require_str(doc_id)
        id_to_index[doc_id] = _require_int(position)

    # JSON object keys are strings; restore the integer FAISS positions.
    # Non-integer keys mean the file is corrupt — raise, do not guess.
    index_to_id: dict[int, str] = {}
    for key, doc_id in index_to_id_raw.items():
        try:
            position = int(key)
        except (TypeError, ValueError) as exc:
            raise ValueError("index_to_id key is not an integer position") from exc
        _require_str(doc_id)
        index_to_id[position] = doc_id

    return document_store, id_to_index, index_to_id, next_index


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
        if faiss is None:
            faiss_not_installed_msg = (
                "FAISS is not installed. Please install it with 'pip install faiss-cpu' "
                "for CPU version or 'pip install faiss-gpu' for GPU version."
            )
            raise ImportError(faiss_not_installed_msg)
        self._load_index_and_metadata()
        return self.faiss_index

    def _create_faiss_index(self, dimension: int):
        """Create a FAISS index based on the configuration.

        Args:
            dimension (int): The dimension of the vectors.

        Returns:
            faiss.Index: The created FAISS index.
        """
        if faiss is None:
            raise ImportError(
                "FAISS is not installed. Please install it with 'pip install faiss-cpu' "
                "for CPU version or 'pip install faiss-gpu' for GPU version."
            )
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
            unsupported_index_msg = f"Unsupported index type: {index_type}"
            raise ValueError(unsupported_index_msg)

    def _load_index_and_metadata(self):
        """Load existing FAISS index and metadata from disk."""
        if self.index_path and os.path.exists(self.index_path):
            try:
                self.faiss_index = faiss.read_index(self.index_path)
                logger.info(f"Loaded FAISS index from {self.index_path}")
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")
                self.faiss_index = None

        if not self._read_metadata_file():
            self._reset_metadata()

        # If no index was loaded and we have metadata, create empty index
        if self.faiss_index is None and self.document_store:
            # Try to infer dimension from existing documents
            for doc in self.document_store.values():
                if doc.embedding and len(doc.embedding) > 0:
                    dimension = len(doc.embedding)
                    self.faiss_index = self._create_faiss_index(dimension)
                    break

    def _read_metadata_file(self) -> bool:
        """Load document metadata from ``metadata_path`` as JSON.

        Returns True on success, False if the path is unset/missing or the file
        could not be parsed. Metadata is persisted as JSON (not pickle) so that
        loading it cannot execute arbitrary code: pickle deserialization of a
        writable metadata file is an RCE vector. A legacy pickle-format file is
        therefore unreadable and the caller resets to an empty store.

        On any structural problem — wrong ``format`` marker, top-level shape
        that is not an object, individual ``Document`` payloads that do not
        reconstruct, or non-integer ``index_to_id`` keys — the whole metadata
        set is discarded and the caller resets to an empty store, so the loaded
        FAISS index and metadata can never end up in an incoherent state.
        """
        if not (self.metadata_path and os.path.exists(self.metadata_path)):
            return False
        try:
            with open(self.metadata_path, encoding="utf-8") as f:
                metadata = json.load(f)
        except (OSError, ValueError) as exc:
            logger.warning(
                f"Failed to read metadata from {self.metadata_path}: {exc}. "
                "If this is a legacy pickle-format file from an older agentUniverse "
                "version, it is no longer supported (pickle deserialization is an RCE "
                "vector); re-index to regenerate it as JSON."
            )
            return False

        try:
            document_store, id_to_index, index_to_id, next_index = _validate_metadata_payload(metadata)
        except (ValueError, TypeError) as exc:
            logger.warning(
                f"Metadata at {self.metadata_path} failed schema validation: {exc}; "
                "resetting to an empty store to keep the FAISS index coherent."
            )
            return False

        self.document_store = document_store
        self.id_to_index = id_to_index
        self.index_to_id = index_to_id
        self._next_index = next_index
        logger.info(f"Loaded metadata from {self.metadata_path}")
        return True

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

        self._write_metadata_file()

    def _write_metadata_file(self) -> None:
        """Write document metadata to ``metadata_path`` as JSON.

        Writes through a temporary file in the same directory and atomically
        replaces the target, so an interrupted write cannot destroy the last
        usable metadata file: readers either see the previous version or the
        fully-written new one, never a half-flushed JSON document.
        """
        if not self.metadata_path:
            return
        directory = Path(self.metadata_path).parent
        temporary = None
        try:
            directory.mkdir(parents=True, exist_ok=True)
            metadata = {
                "format": METADATA_FORMAT_VERSION,
                "document_store": {doc_id: doc.model_dump(mode="json") for doc_id, doc in self.document_store.items()},
                "id_to_index": self.id_to_index,
                # FAISS positions are ints; store them as strings for JSON.
                "index_to_id": {str(k): v for k, v in self.index_to_id.items()},
                "next_index": self._next_index,
            }
            # Write to a sibling temp file first, fsync, then atomic rename.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                prefix=".faiss-metadata-",
                suffix=".tmp",
                dir=str(directory),
                delete=False,
            ) as tmp:
                temporary = tmp.name
                json.dump(metadata, tmp, ensure_ascii=False, default=_json_default)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(temporary, self.metadata_path)
            temporary = None
            logger.info(f"Saved metadata to {self.metadata_path}")
        except Exception:
            logger.exception("Failed to save metadata")
        finally:
            if temporary and os.path.exists(temporary):
                try:
                    os.unlink(temporary)
                except OSError:
                    logger.debug("Could not remove stale metadata temp file %s", temporary, exc_info=True)

    def _get_embedding(self, text: str, text_type: str = "document") -> list[float]:
        """Get embedding for a text using the configured embedding model.

        Args:
            text (str): The text to embed.
            text_type (str): Type of text ("document" or "query").

        Returns:
            List[float]: The embedding vector.
        """
        if not self.embedding_model:
            no_embedding_msg = "No embedding model configured. Please specify an embedding_model."
            raise ValueError(no_embedding_msg)

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

    def insert_document(self, documents: list[Document], **kwargs):  # noqa: C901
        """Insert documents into the FAISS index.

        Args:
            documents (List[Document]): The documents to be inserted.
            **kwargs: Arbitrary keyword arguments.
        """
        if not documents:
            return

        # Prepare embeddings and documents
        embeddings_to_add = []
        docs_to_add = []

        for document in documents:
            # Skip if document already exists
            if document.id in self.document_store:
                continue

            embedding = document.embedding
            if len(embedding) == 0:
                if self.embedding_model is not None:
                    embedding = self._get_embedding(document.text)
                else:
                    logger.warning(
                        f"No embedding for document {document.id} and no embedding model configured, skipping"
                    )
                    continue

            if len(embedding) == 0:
                logger.warning(f"No embedding for document {document.id}, skipping")
                continue

            embeddings_to_add.append(embedding)
            docs_to_add.append(document)

        if not embeddings_to_add:
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
