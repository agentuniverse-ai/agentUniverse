"""Paired sentence ingestion and exact, source-addressed context expansion."""

import hashlib
import json
import re
import uuid
from typing import List

from pydantic import Field, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


def _identity(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, json.dumps(parts, ensure_ascii=False)))


def _spans(text):
    """Conservative punctuation/blank-line boundaries; exact trimmed offsets."""
    start = 0
    spans = []

    def append(end):
        nonlocal start
        left, right = start, end
        while left < right and text[left].isspace():
            left += 1
        while right > left and text[right - 1].isspace():
            right -= 1
        if left < right:
            spans.append((left, right))
        start = end

    for match in re.finditer(r'[.!?。！？]+["\'”’）)\]]*|\r?\n[ \t]*\r?\n', text):
        token = match[0]
        end = match.end()
        if token[0] in ".!?" and end < len(text) and not text[end].isspace():
            continue
        if token == ".":
            word_start = end - 2
            while word_start >= 0 and (text[word_start].isascii() and (text[word_start].isalpha() or text[word_start] == ".")):
                word_start -= 1
            word = re.fullmatch(r"([A-Za-z.]+)\.", text[word_start + 1:end])
            if word and (word[1].lower() in {"dr", "mr", "mrs", "ms", "prof", "sr", "jr", "e.g", "i.e"} or
                         re.fullmatch(r"(?:[A-Za-z]\.)*[A-Z]", word[1])):
                continue
        append(end)
    append(len(text))
    return spans


class SentenceWindowSplitter(DocProcessor):
    """Store individual sentences plus bounded original neighboring context.

    The budget is soft for a sentence longer than max_window_chars: it is
    retained alone and marked over_budget, never silently truncated.
    """

    window_radius: StrictInt = 1
    max_window_chars: StrictInt = 2000

    def __init__(self, **data):
        super().__init__(**data)
        self._validate_options()

    def _validate_options(self):
        if type(self.window_radius) is not int or self.window_radius < 0:
            raise ValueError("window_radius must be a nonnegative integer")
        if type(self.max_window_chars) is not int or self.max_window_chars <= 0:
            raise ValueError("max_window_chars must be a positive integer")

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Produce immutable-input sentence copies with source-specific IDs."""
        self._validate_options()
        result = []
        for doc in origin_docs:
            text = doc.text or ""
            spans = _spans(text)
            if not spans:
                result.append(doc)
                continue
            if "sentence_window" in (doc.metadata or {}):
                raise ValueError("sentence_window metadata is reserved")
            source = (doc.metadata or {}).get("source", (doc.metadata or {}).get("file_name", ""))
            if not isinstance(source, str):
                raise ValueError("source/file_name must be a string")
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            source_id = _identity(doc.id, source, digest)
            for index, (start, end) in enumerate(spans):
                left, right = index, index
                # Prefer nearer context, left before right on equal distance.
                for distance in range(1, min(self.window_radius, len(spans)) + 1):
                    candidate = index - distance
                    if candidate >= 0 and spans[right][1] - spans[candidate][0] <= self.max_window_chars:
                        left = candidate
                    candidate = index + distance
                    if candidate < len(spans) and spans[candidate][1] - spans[left][0] <= self.max_window_chars:
                        right = candidate
                window_start, window_end = spans[left][0], spans[right][1]
                metadata = dict(doc.metadata or {})
                metadata["sentence_window"] = {
                    "version": 1, "stage": "sentence", "source_id": source_id,
                    "source_document_id": doc.id, "source_digest": digest,
                    "source_length": len(text), "sentence_index": index,
                    "sentence_start": start, "sentence_end": end,
                    "window_start": window_start, "window_end": window_end,
                    "window_text": text[window_start:window_end],
                    "over_budget": window_end - window_start > self.max_window_chars,
                }
                result.append(doc.model_copy(update={
                    "id": _identity(source_id, start, end), "text": text[start:end],
                    "metadata": metadata, "embedding": [], "keywords": set(),
                }))
        return result

    def _initialize_by_component_configer(self, config: ComponentConfiger) -> 'SentenceWindowSplitter':
        names = ("window_radius", "max_window_chars")
        validated = SentenceWindowSplitter(**{key: getattr(config, key, getattr(self, key)) for key in names})
        super()._initialize_by_component_configer(config)
        for key in names:
            setattr(self, key, getattr(validated, key))
        return self


class SentenceWindowExpander(DocProcessor):
    """Expand ranked sentence hits, merging consistent overlapping windows.

    Only same-source windows with matching overlap text can merge. Unmerged
    windows remain in rank order; merged output occupies its earliest hit's
    rank. Missing window metadata passes through. Invalid present metadata
    raises. max_window_chars bounds merged text, not an oversized input window.
    """

    max_window_chars: StrictInt = 2000
    score_fields: List[StrictStr] = Field(default_factory=lambda: ["relevance_score", "bm25_score", "rrf_score"])

    def __init__(self, **data):
        super().__init__(**data)
        self._validate_options()

    def _validate_options(self):
        if type(self.max_window_chars) is not int or self.max_window_chars <= 0:
            raise ValueError("max_window_chars must be a positive integer")
        if (not isinstance(self.score_fields, list) or
                any(not isinstance(key, str) or not key.strip() or key == "sentence_window" for key in self.score_fields) or
                len(set(self.score_fields)) != len(self.score_fields)):
            raise ValueError("score_fields must contain unique nonblank keys other than sentence_window")

    @staticmethod
    def _validate_window(doc, info):
        if (not isinstance(info, dict) or type(info.get("version")) is not int or
                info["version"] != 1 or info.get("stage") != "sentence"):
            raise ValueError("sentence_window must be a version 1 sentence record")
        names = ("source_length", "sentence_index", "sentence_start", "sentence_end", "window_start", "window_end")
        if any(type(info.get(key)) is not int or info[key] < 0 for key in names):
            raise ValueError("sentence_window offsets must be nonnegative integers")
        if any(not isinstance(info.get(key), str) or not info[key] for key in ("source_id", "source_digest", "source_document_id")):
            raise ValueError("sentence_window source identity is missing")
        start, end = info["window_start"], info["window_end"]
        sentence_start, sentence_end = info["sentence_start"], info["sentence_end"]
        text = info.get("window_text")
        if (not isinstance(text, str) or len(text) != end - start or
                not 0 <= start <= sentence_start < sentence_end <= end <= info["source_length"] or
                doc.text != text[sentence_start - start:sentence_end - start]):
            raise ValueError("sentence_window text and offsets do not match the recalled sentence")

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> List[Document]:
        """Keep retrieval scores explicitly attached to their original sentences."""
        self._validate_options()
        entries = []
        for rank, doc in enumerate(origin_docs):
            if "sentence_window" not in (doc.metadata or {}):
                entries.append({"rank": rank, "doc": doc, "info": None})
                continue
            info = doc.metadata["sentence_window"]
            self._validate_window(doc, info)
            match = {"id": doc.id, "text": doc.text, "start": info["sentence_start"],
                     "end": info["sentence_end"], "index": info["sentence_index"], "rank": rank,
                     "scores": {key: doc.metadata[key] for key in self.score_fields if key in doc.metadata}}
            entries.append({"rank": rank, "doc": doc, "info": info,
                            "start": info["window_start"], "end": info["window_end"],
                            "text": info["window_text"], "matches": [match]})

        groups = []
        for entry in entries:
            if entry["info"] is None:
                groups.append(entry)
                continue
            # Repeat after a merge to handle a later hit bridging two windows.
            changed = True
            while changed:
                changed = False
                for other in list(groups):
                    if other["info"] is None or any(other["info"][key] != entry["info"][key]
                                                    for key in ("source_id", "source_digest", "source_length")):
                        continue
                    left, right = max(entry["start"], other["start"]), min(entry["end"], other["end"])
                    if left >= right:
                        continue
                    if (entry["text"][left - entry["start"]:right - entry["start"]] !=
                            other["text"][left - other["start"]:right - other["start"]]):
                        raise ValueError("same-source sentence windows contain inconsistent overlapping text")
                    start, end = min(entry["start"], other["start"]), max(entry["end"], other["end"])
                    identical = entry["start"] == other["start"] and entry["end"] == other["end"]
                    if end - start > self.max_window_chars and not identical:
                        continue
                    first, second = sorted([entry, other], key=lambda item: item["start"])
                    text = first["text"] + second["text"][max(0, first["end"] - second["start"]):]
                    best = min([entry, other], key=lambda item: item["rank"])
                    entry = dict(best, start=start, end=end, text=text,
                                 matches=sorted(entry["matches"] + other["matches"], key=lambda item: item["rank"]))
                    groups.remove(other)
                    changed = True
                    break
            groups.append(entry)

        result = []
        for entry in sorted(groups, key=lambda item: item["rank"]):
            doc, info = entry["doc"], entry["info"]
            if info is None:
                result.append(doc)
                continue
            metadata = {key: value for key, value in doc.metadata.items() if key not in self.score_fields}
            metadata["sentence_window"] = {
                "version": 1, "stage": "expanded", "source_id": info["source_id"],
                "source_document_id": info["source_document_id"], "source_digest": info["source_digest"],
                "source_length": info["source_length"], "window_start": entry["start"],
                "window_end": entry["end"], "matches": entry["matches"],
                "over_budget": len(entry["text"]) > self.max_window_chars,
            }
            result.append(doc.model_copy(update={
                "id": _identity(info["source_id"], "window", entry["start"], entry["end"]),
                "text": entry["text"], "metadata": metadata, "embedding": [], "keywords": set(),
            }))
        return result

    def _initialize_by_component_configer(self, config: ComponentConfiger) -> 'SentenceWindowExpander':
        names = ("max_window_chars", "score_fields")
        validated = SentenceWindowExpander(**{key: getattr(config, key, getattr(self, key)) for key in names})
        super()._initialize_by_component_configer(config)
        for key in names:
            setattr(self, key, getattr(validated, key))
        return self
