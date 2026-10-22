"""Bounded opt-in synchronous store fan-out with explicit partial outcomes."""
import math
import time
from concurrent.futures import ThreadPoolExecutor, wait, CancelledError
from dataclasses import dataclass, field
from threading import RLock
from typing import Dict, List, Mapping

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store


class RetrievalCapacityError(RuntimeError):
    """The request would exceed the coordinator's total in-flight capacity."""


@dataclass(frozen=True)
class ChannelOutcome:
    status: str
    documents: List[Document] = field(default_factory=list)
    error_type: str = None
    still_running: bool = False


@dataclass(frozen=True)
class RetrievalReport:
    channels: Dict[str, ChannelOutcome]
    elapsed_seconds: float

    @property
    def partial(self):
        return any(outcome.status != "success" for outcome in self.channels.values())

    @property
    def documents(self):
        """Successful results in configured channel order, not score-fused order."""
        return [document for outcome in self.channels.values() for document in outcome.documents]


class DeadlineRetrievalCoordinator:
    """Own a bounded executor and keep timed-out running calls accounted for.

    Deadlines bound waiting, not Python thread lifetime or provider IO. Queued
    calls are cancelled when possible; running calls stay owned until completion.
    Application/provider code must arrange finite network timeouts. Reuse this
    coordinator across requests instead of creating unbounded executors per query.
    """

    def __init__(self, stores: Mapping[str, Store], *, max_workers=4,
                 max_inflight=16, max_documents_per_channel=100):
        for value, name in ((max_workers, "max_workers"), (max_inflight, "max_inflight"),
                            (max_documents_per_channel, "max_documents_per_channel")):
            if type(value) is not int or value < 1:
                raise ValueError(name + " must be a positive integer")
        if not isinstance(stores, Mapping) or not stores or len(stores) > max_inflight:
            raise ValueError("provide nonempty stores within max_inflight")
        if any(not isinstance(name, str) or not name.strip() or not isinstance(store, Store)
               for name, store in stores.items()):
            raise ValueError("stores require nonblank names and initialized Store objects")
        self._stores = dict(stores)
        self._max_inflight = max_inflight
        self._max_documents = max_documents_per_channel
        self._lock = RLock()
        self._futures = set()
        self._closed = False
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="retrieval-deadline")

    @property
    def inflight_count(self):
        """Snapshot of queued/running owned calls, including late calls."""
        with self._lock:
            return len(self._futures)

    def _release(self, future):
        with self._lock:
            self._futures.discard(future)

    def _run(self, name, store, query, deadline):
        if time.monotonic() >= deadline:
            return ChannelOutcome("timeout")
        try:
            documents = store.query(query)
            if time.monotonic() >= deadline:
                return ChannelOutcome("timeout")
            if not isinstance(documents, list):
                raise TypeError("store query must return a list")
            kept = documents[:self._max_documents]
            if any(not isinstance(document, Document) for document in kept):
                raise TypeError("store results must contain Documents")
            copied = []
            for document in kept:
                item = document.model_copy(deep=True)
                item.metadata = dict(item.metadata or {})
                item.metadata["recall_channel"] = name
                copied.append(item)
            if time.monotonic() >= deadline:
                return ChannelOutcome("timeout")
            return ChannelOutcome("success", copied)
        except Exception as error:
            # Do not expose provider messages, which can contain credentials.
            return ChannelOutcome("error", error_type=type(error).__name__)

    def query(self, query: Query, *, budget_seconds: float) -> RetrievalReport:
        """Query all configured stores or reject capacity before any submission.

        Success includes an empty successful result. Errors, cancelled calls and
        timeouts remain distinct. Late results never mutate a returned report.
        Each store receives its own deep-copied Query. Postprocessing/fusion and
        external cleanup time are not part of this retrieval waiting budget.
        """
        started = time.monotonic()
        if not isinstance(query, Query):
            raise TypeError("query must be a Query")
        if isinstance(budget_seconds, bool) or not isinstance(budget_seconds, (int, float)) or not math.isfinite(budget_seconds) or not 0 <= budget_seconds <= 86400:
            raise ValueError("budget_seconds must be finite and between 0 and 86400 seconds")
        deadline = started + budget_seconds
        detached = {name: query.model_copy(deep=True) for name in self._stores}
        futures = {}
        with self._lock:
            if self._closed:
                raise RuntimeError("retrieval coordinator is closed")
            if len(self._futures) + len(self._stores) > self._max_inflight:
                raise RetrievalCapacityError("in-flight retrieval capacity exceeded")
            try:
                for name, store in self._stores.items():
                    future = self._executor.submit(self._run, name, store, detached[name], deadline)
                    futures[name] = future
                    self._futures.add(future)
                    future.add_done_callback(self._release)
            except BaseException:
                for future in futures.values():
                    future.cancel()
                raise
        try:
            done, pending = wait(futures.values(), timeout=max(0.0, deadline - time.monotonic()))
            outcomes = {}
            for name, future in futures.items():
                if future in pending:
                    if future.cancelled():
                        outcomes[name] = ChannelOutcome("cancelled")
                    else:
                        future.cancel()
                        outcomes[name] = ChannelOutcome("timeout", still_running=not future.done())
                else:
                    try:
                        outcomes[name] = future.result()
                    except CancelledError:
                        outcomes[name] = ChannelOutcome("cancelled")
            return RetrievalReport(outcomes, time.monotonic() - started)
        except BaseException:
            for future in futures.values():
                future.cancel()
            raise

    def close(self, *, wait_for_running=True):
        """Stop admission and cancel queued work; optionally wait for running calls.

        False does not kill threads. Remaining calls stay counted and may keep the
        Python process alive. A later close(True) can join them. The context manager
        always waits, so leaving its scope may exceed a request's waiting budget.
        Store/provider resources remain owned by the caller.
        """
        if type(wait_for_running) is not bool:
            raise ValueError("wait_for_running must be a boolean")
        with self._lock:
            self._closed = True
        self._executor.shutdown(wait=wait_for_running, cancel_futures=True)

    def __enter__(self):
        with self._lock:
            if self._closed:
                raise RuntimeError("retrieval coordinator is closed")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
