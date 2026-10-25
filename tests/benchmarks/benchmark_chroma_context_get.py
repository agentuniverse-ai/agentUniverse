"""Measure the cost of newest-first retrieval with limit=1, without network I/O.

Run: PYTHONPATH=. python tests/benchmarks/benchmark_chroma_context_get.py

Uses persistent Chroma, constant local embeddings and 1 KiB ASCII documents.
Setup is excluded. Each path is warmed once, then timed five times without
tracemalloc; peak Python allocations are measured in a separate call. Peaks
exclude native allocations and existing database/index memory. The comparison
path reproduces the old backend-limit-first algorithm, which can return the
wrong record. These are local measurements, not production latency guarantees.

Sample run (Python 3.12.15, Chroma 0.4.24, macOS arm64):
matches | backend-limit ms / peak MiB | newest-first ms / peak MiB
    100 |              0.19 / 0.03   |            1.64 / 0.53
  1,000 |              0.43 / 0.03   |           15.61 / 5.18
 10,000 |              4.86 / 0.03   |          212.61 / 51.66

A small result limit does not bound read volume or allocation. Large sessions
need selective filters or a store with backend timestamp ordering; lowering
limit alone cannot remove this cost while retaining correct newest-first data.
"""
import gc
import platform
from datetime import datetime, timedelta
from statistics import median
from tempfile import TemporaryDirectory
from time import perf_counter
import tracemalloc

import chromadb
from chromadb.api.client import SharedSystemClient
from chromadb.config import Settings

from agentuniverse.agent.context.context_model import ContextMetadata, ContextSegment, ContextType
from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class ConstantEmbedding:
    def __call__(self, input):
        return [[1., 0.] for _ in input]


def backend_limited(store):
    results = store._collection.get(where={'session_id': 'session'}, limit=1)
    segments = [store._metadata_to_segment(document, metadata)
                for document, metadata in zip(results['documents'], results['metadatas'])]
    segments.sort(key=lambda segment: segment.metadata.created_at, reverse=True)
    return segments[:1]


def measure(call):
    call()
    elapsed = []
    for _ in range(5):
        start = perf_counter()
        result = call()
        elapsed.append((perf_counter() - start) * 1000)
        del result
    gc.collect()
    tracemalloc.start()
    try:
        result = call()
        peak = tracemalloc.get_traced_memory()[1] / (1024 * 1024)
    finally:
        tracemalloc.stop()
    assert len(result) == 1
    return median(elapsed), peak


def main():
    print(f'Python {platform.python_version()}, Chroma {chromadb.__version__}, '
          f'{platform.system()} {platform.machine()}')
    print('matches,backend_limit_ms,backend_limit_peak_MiB,newest_ms,newest_peak_MiB')
    for count in (100, 1000, 10000):
        with TemporaryDirectory() as directory:
            client = chromadb.PersistentClient(
                path=directory, settings=Settings(anonymized_telemetry=False))
            try:
                collection = client.create_collection(
                    'benchmark_context', embedding_function=ConstantEmbedding())
                store = ChromaContextStore()
                store._collection = collection
                start = datetime(2026, 1, 1)
                for offset in range(0, count, 1000):
                    store.add([ContextSegment(
                        id=f'{index:06d}', content='x' * 1024, tokens=256,
                        type=ContextType.CONVERSATION,
                        metadata=ContextMetadata(created_at=start + timedelta(seconds=index)))
                        for index in range(offset, min(offset + 1000, count))],
                        session_id='session')
                assert store.get('session', limit=1)[0].id == f'{count - 1:06d}'
                old_ms, old_peak = measure(lambda: backend_limited(store))
                new_ms, new_peak = measure(lambda: store.get('session', limit=1))
                print(f'{count},{old_ms:.2f},{old_peak:.2f},{new_ms:.2f},{new_peak:.2f}',
                      flush=True)
            finally:
                client._system.stop()
                systems = getattr(SharedSystemClient, '_identifier_to_system', None)
                if systems is None:
                    systems = SharedSystemClient._identifer_to_system
                systems.pop(client._identifier, None)


if __name__ == '__main__':
    main()
