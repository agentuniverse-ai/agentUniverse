# FAISS Vector Store

## Overview

The FAISS (Facebook AI Similarity Search) store is a high-performance vector database implementation for agentUniverse that provides efficient similarity search capabilities. FAISS is optimized for fast nearest neighbor search and clustering of dense vectors, making it ideal for large-scale similarity search applications.

## Features

- **Multiple Index Types**: Support for various FAISS index types including Flat, IVF, HNSW, and PQ
- **High Performance**: Optimized for both CPU and GPU operations
- **Persistent Storage**: Automatic saving and loading of indexes and metadata
- **Full CRUD Operations**: Complete support for Create, Read, Update, and Delete operations
- **Flexible Configuration**: Extensive configuration options for different use cases
- **Memory Efficiency**: Support for compressed indexes to reduce memory usage
- **Scalability**: Handles millions of vectors efficiently

## Installation

FAISS requires additional dependencies to be installed:

```bash
# For CPU-only version
pip install faiss-cpu

# For GPU-accelerated version (requires CUDA)
pip install faiss-gpu
```

## Configuration

### Basic Configuration

```yaml
name: 'my_faiss_store'
description: 'FAISS vector store for similarity search'
index_path: './data/faiss.index'
metadata_path: './data/faiss_metadata.pkl'
embedding_model: 'your_embedding_model'
similarity_top_k: 10
index_config:
  index_type: 'IndexFlatL2'
  dimension: 768
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.faiss_store'
  class: 'FAISSStore'
```

### Configuration Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | str | Yes | Unique name for the store |
| `description` | str | No | Description of the store |
| `index_path` | str | No | Path to save/load FAISS index file |
| `metadata_path` | str | No | Path to save/load document metadata |
| `embedding_model` | str | Yes | Name of the embedding model to use |
| `similarity_top_k` | int | No | Default number of results to return (default: 10) |
| `index_config` | dict | No | FAISS index configuration |

### Index Configuration Options

The `index_config` parameter allows you to specify the type and parameters of the FAISS index:

#### IndexFlatL2 (Exact Search)
```yaml
index_config:
  index_type: 'IndexFlatL2'
  dimension: 768
```

#### IndexFlatIP (Inner Product)
```yaml
index_config:
  index_type: 'IndexFlatIP'
  dimension: 768
```

#### IndexIVFFlat (Inverted File with Flat Quantizer)
```yaml
index_config:
  index_type: 'IndexIVFFlat'
  dimension: 768
  nlist: 100      # Number of clusters
  nprobe: 10      # Number of clusters to search
```

#### IndexIVFPQ (Inverted File with Product Quantization)
```yaml
index_config:
  index_type: 'IndexIVFPQ'
  dimension: 768
  nlist: 100      # Number of clusters
  nprobe: 10      # Number of clusters to search
  m: 8            # Number of subquantizers
  nbits: 8        # Bits per subquantizer
```

#### IndexHNSWFlat (Hierarchical Navigable Small World)
```yaml
index_config:
  index_type: 'IndexHNSWFlat'
  dimension: 768
  M: 16               # Number of bi-directional links
  efConstruction: 200 # Size of dynamic candidate list during construction
  efSearch: 50        # Size of dynamic candidate list during search
```

## Usage Examples

### Basic Usage

```python
from agentuniverse.agent.action.knowledge.store.faiss_store import FAISSStore
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query

# Initialize store
store = FAISSStore(
    index_path="./data/my_faiss.index",
    metadata_path="./data/my_faiss_metadata.pkl",
    embedding_model="your_embedding_model",
    index_config={
        "index_type": "IndexFlatL2",
        "dimension": 768
    }
)

# Initialize the client
store._new_client()

# Insert documents
documents = [
    Document(text="Python is a programming language", metadata={"topic": "programming"}),
    Document(text="Machine learning uses algorithms", metadata={"topic": "AI"}),
]
store.insert_document(documents)

# Query documents
query = Query(query_str="programming languages")
results = store.query(query)

for doc in results:
    print(f"Text: {doc.text}")
    print(f"Score: {doc.metadata.get('score')}")
```

### Advanced Usage with Different Index Types

```python
# High-performance HNSW index
hnsw_store = FAISSStore(
    index_path="./data/hnsw_faiss.index",
    metadata_path="./data/hnsw_metadata.pkl",
    embedding_model="your_embedding_model",
    index_config={
        "index_type": "IndexHNSWFlat",
        "dimension": 768,
        "M": 16,
        "efConstruction": 200,
        "efSearch": 50
    }
)

# Memory-efficient IVF-PQ index
ivfpq_store = FAISSStore(
    index_path="./data/ivfpq_faiss.index",
    metadata_path="./data/ivfpq_metadata.pkl",
    embedding_model="your_embedding_model",
    index_config={
        "index_type": "IndexIVFPQ",
        "dimension": 768,
        "nlist": 1000,
        "m": 8,
        "nbits": 8
    }
)
```

### CRUD Operations

```python
# Create/Insert
doc = Document(text="New document", metadata={"category": "test"})
store.insert_document([doc])

# Read/Query
query = Query(query_str="search term")
results = store.query(query)

# Update
updated_doc = Document(id=doc.id, text="Updated document", metadata={"category": "updated"})
store.update_document([updated_doc])

# Delete
store.delete_document(doc.id)

# Get document by ID
retrieved_doc = store.get_document_by_id(doc.id)

# List all document IDs
all_ids = store.list_document_ids()

# Get total document count
count = store.get_document_count()
```

## Index Type Comparison

| Index Type | Speed | Memory | Accuracy | Use Case |
|------------|-------|---------|----------|----------|
| IndexFlatL2 | Slow | High | 100% | Small datasets, exact search |
| IndexFlatIP | Slow | High | 100% | Small datasets, inner product |
| IndexIVFFlat | Fast | Medium | ~99% | Medium datasets, good balance |
| IndexIVFPQ | Very Fast | Low | ~95% | Large datasets, memory constrained |
| IndexHNSWFlat | Very Fast | High | ~99% | Large datasets, high performance |

## Performance Tuning

### For Speed
- Use `IndexHNSWFlat` with higher `efSearch` values
- Use `IndexIVFFlat` with appropriate `nprobe` settings
- Consider GPU acceleration for very large datasets

### For Memory Efficiency
- Use `IndexIVFPQ` with appropriate quantization parameters
- Reduce `M` parameter for HNSW indexes
- Use smaller `nlist` values for IVF indexes

### For Accuracy
- Use `IndexFlatL2` or `IndexFlatIP` for exact search
- Increase `efSearch` for HNSW indexes
- Increase `nprobe` for IVF indexes

## Best Practices

1. **Choose the Right Index Type**:
   - Use `IndexFlatL2` for small datasets (<10K vectors)
   - Use `IndexIVFFlat` for medium datasets (10K-1M vectors)
   - Use `IndexHNSWFlat` for large datasets requiring high performance
   - Use `IndexIVFPQ` for very large datasets with memory constraints

2. **Optimize Parameters**:
   - Set `nlist` to approximately `sqrt(N)` where N is the number of vectors
   - Start with `nprobe = nlist / 10` and adjust based on accuracy needs
   - For HNSW, use `M = 16-64` depending on dataset size

3. **Memory Management**:
   - Monitor memory usage, especially with flat indexes
   - Use persistent storage to avoid rebuilding indexes
   - Consider batch operations for large datasets

4. **Error Handling**:
   - Always check if the index is trained before adding vectors
   - Handle cases where no results are found
   - Implement retry logic for I/O operations

## Troubleshooting

### Common Issues

**Issue**: "Index is not trained"
```python
# Solution: Ensure enough training data for IVF indexes
if hasattr(index, 'is_trained') and not index.is_trained:
    # Need at least nlist vectors for training
    training_data = np.array(embeddings[:max(nlist, len(embeddings))])
    index.train(training_data)
```

**Issue**: "Dimension mismatch"
```python
# Solution: Ensure all embeddings have the same dimension
assert len(embedding) == expected_dimension
```

**Issue**: "Out of memory"
```python
# Solution: Use memory-efficient index types
index_config = {
    "index_type": "IndexIVFPQ",
    "nlist": 1000,
    "m": 8,
    "nbits": 8
}
```

### Performance Issues

**Slow Insertion**: Use batch operations instead of inserting documents one by one.

**Slow Search**: Adjust search parameters (`nprobe`, `efSearch`) based on accuracy requirements.

**High Memory Usage**: Consider using compressed indexes like `IndexIVFPQ`.

## Integration with agentUniverse

The FAISS store integrates seamlessly with agentUniverse's knowledge system:

```yaml
# In your knowledge configuration
name: 'my_knowledge'
description: 'Knowledge base with FAISS store'
stores:
  - 'my_faiss_store'
embedding_model: 'your_embedding_model'
metadata:
  type: 'KNOWLEDGE'
  module: 'agentuniverse.agent.action.knowledge.knowledge'
  class: 'Knowledge'
```

## Conclusion

The FAISS store provides a powerful and flexible solution for vector similarity search in agentUniverse. By choosing the appropriate index type and configuration, you can optimize for your specific use case, whether it's accuracy, speed, or memory efficiency.

For more information about FAISS, visit the [official FAISS documentation](https://github.com/facebookresearch/faiss).
