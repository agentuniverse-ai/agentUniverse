"""Paragraph chunks with explicit Markdown footnote definitions attached."""
import hashlib
import json
import re
from collections import defaultdict, deque
from copy import deepcopy
from bisect import bisect_right

from pydantic import Field, StrictInt, StrictStr

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document


_LABEL = r"[A-Za-z0-9_-]{1,64}"
_DEFINITION = re.compile(r"^ {0,3}\[\^(" + _LABEL + r")\]:[ \t]*(.*)")
_REFERENCE = re.compile(r"\[\^(" + _LABEL + r")\]")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def _escaped(text, index):
    backslashes = 0
    while index > 0 and text[index - 1] == "\\":
        index -= 1
        backslashes += 1
    return backslashes % 2 == 1


def _scan(text):
    """Return definition spans, code mask and safe paragraph cut positions."""
    lines = text.splitlines(keepends=True)
    starts = []
    position = 0
    for line in lines:
        starts.append(position)
        position += len(line)
    excluded = bytearray(len(text))
    definitions = {}
    cuts = []
    fence = None
    index = 0
    while index < len(lines):
        line, start = lines[index], starts[index]
        end = start + len(line)
        marker = _FENCE.match(line.rstrip("\r\n"))
        if fence is not None:
            excluded[start:end] = b"\1" * (end - start)
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
            index += 1
            continue
        if marker:
            fence = (marker[1][0], len(marker[1]))
            excluded[start:end] = b"\1" * (end - start)
            index += 1
            continue
        definition = _DEFINITION.match(line)
        if definition:
            label = definition[1]
            if label in definitions:
                raise ValueError("duplicate footnote definition: " + label)
            last = index + 1
            while last < len(lines):
                if lines[last].startswith(("    ", "\t")):
                    last += 1
                elif not lines[last].strip():
                    lookahead = last + 1
                    while lookahead < len(lines) and not lines[lookahead].strip():
                        lookahead += 1
                    if lookahead < len(lines) and lines[lookahead].startswith(("    ", "\t")):
                        last = lookahead + 1
                    else:
                        break
                else:
                    break
            end = starts[last] if last < len(lines) else len(text)
            definitions[label] = (start, end)
            excluded[start:end] = b"\1" * (end - start)
            index = last
            continue
        if line.startswith(("    ", "\t")):
            excluded[start:end] = b"\1" * (end - start)
        elif not line.strip():
            cuts.append(end)
        index += 1
    # Match equal-length backtick runs, including multi-line inline code. A run
    # without a closing partner is literal text. Ignore fenced/definition runs.
    runs = [match for match in re.finditer(r"`+", text)
            if not excluded[match.start()] and not _escaped(text, match.start())]
    # Inline code cannot cross a blank paragraph boundary or a block that was
    # already excluded (for example a fenced block or footnote definition).
    barriers = sorted(set(cuts + [position for position, value in enumerate(excluded)
                                  if value and (position == 0 or not excluded[position - 1])]))
    by_length = defaultdict(deque)
    for number, match in enumerate(runs):
        by_length[len(match[0])].append(number)
    number = 0
    while number < len(runs):
        match = runs[number]
        partners = by_length[len(match[0])]
        while partners and partners[0] <= number:
            partners.popleft()
        if partners:
            closing = partners[0]
            end = runs[closing].end()
            barrier = bisect_right(barriers, match.start())
            if barrier < len(barriers) and barriers[barrier] < end:
                number += 1
                continue
            excluded[match.start():end] = b"\1" * (end - match.start())
            number = closing + 1
        else:
            number += 1
    return definitions, excluded, [cut for cut in cuts if cut == len(text) or not excluded[cut - 1]]


class FootnoteContextSplitter(DocProcessor):
    """Keep paragraph chunks self-contained for explicit ``[^label]`` notes.

    The character target is soft: paragraphs, code blocks and definitions are
    never cut internally. Hard document/output limits reject rather than truncate.
    All original characters remain in ordered source spans; attached notes may
    repeat. Definitions are local to each input document, with case-sensitive IDs.
    """
    chunk_chars: StrictInt = Field(default=1500, ge=1)
    max_document_chars: StrictInt = Field(default=1_000_000, ge=1)
    max_output_chars: StrictInt = Field(default=4_000_000, ge=1)
    max_references: StrictInt = Field(default=10_000, ge=1)
    missing: StrictStr = "report"
    source_key: StrictStr = "source"

    def _validate_options(self):
        for name in ("chunk_chars", "max_document_chars", "max_output_chars", "max_references"):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise ValueError(name + " must be a positive integer")
        if self.missing not in ("report", "error"):
            raise ValueError("missing must be report or error")
        if not isinstance(self.source_key, str) or not self.source_key.strip():
            raise ValueError("source_key must be nonblank")

    def _process_docs(self, origin_docs, query=None):
        self._validate_options()
        result = []
        output_chars = 0
        for document in origin_docs:
            text = document.text or ""
            if len(text) > self.max_document_chars:
                raise ValueError("document exceeds max_document_chars")
            metadata = document.metadata or {}
            if "footnote_context" in metadata:
                raise ValueError("footnote_context already present; do not split twice")
            source = metadata.get(self.source_key, document.id)
            if not isinstance(source, str) or not source:
                raise ValueError("source identity must be a nonempty string")
            definitions, excluded, cuts = _scan(text)
            references = [match for match in _REFERENCE.finditer(text)
                          if not excluded[match.start()] and not _escaped(text, match.start())]
            if len(references) > self.max_references:
                raise ValueError("document exceeds max_references")
            if self.missing == "error" and any(match[1] not in definitions for match in references):
                raise ValueError("unresolved footnote reference")
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            boundaries = sorted(set(cuts + [len(text)]))
            spans = []
            start = previous = 0
            for end in boundaries:
                if end - start > self.chunk_chars and previous > start:
                    spans.append((start, previous))
                    start = previous
                previous = end
            if start < len(text) or not spans:
                spans.append((start, len(text)))
            reference_index = 0
            for start, end in spans:
                linked = []
                markers = []
                missing = []
                content = text[start:end]
                labels = set()
                while reference_index < len(references) and references[reference_index].start() < end:
                    match = references[reference_index]
                    reference_index += 1
                    label = match[1]
                    markers.append({"label": label, "source_span": [match.start(), match.end()]})
                    if label in labels:
                        continue
                    labels.add(label)
                    if label not in definitions:
                        missing.append(label)
                        continue
                    note_start, note_end = definitions[label]
                    if start <= note_start and note_end <= end:
                        note_span = [note_start - start, note_end - start]
                        appended = False
                    else:
                        if output_chars + len(content) + 2 + note_end - note_start > self.max_output_chars:
                            raise ValueError("batch exceeds max_output_chars")
                        content += "\n\n"
                        note_span = [len(content), len(content) + note_end - note_start]
                        content += text[note_start:note_end]
                        appended = True
                    linked.append({"label": label, "source_span": [note_start, note_end],
                                   "output_span": note_span, "appended": appended})
                output_chars += len(content)
                if output_chars > self.max_output_chars:
                    raise ValueError("batch exceeds max_output_chars")
                copied = deepcopy(metadata)
                copied["footnote_context"] = {
                    "schema_version": 1, "source_id": source, "parent_id": document.id,
                    "source_sha256": digest, "source_span": [start, end],
                    "references": markers, "definitions": linked, "unresolved": missing,
                    "over_chunk_target": len(content) > self.chunk_chars,
                }
                identity = json.dumps([source, document.id, digest, start, end, content], ensure_ascii=False)
                result.append(Document(id=hashlib.sha256(identity.encode("utf-8")).hexdigest(),
                                       text=content, metadata=copied, embedding=[], keywords=set()))
        return result

    def _initialize_by_component_configer(self, config):
        names = ("chunk_chars", "max_document_chars", "max_output_chars", "max_references",
                 "missing", "source_key")
        validated = FootnoteContextSplitter(**{name: getattr(config, name, getattr(self, name)) for name in names})
        validated._validate_options()
        super()._initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(validated, name))
        return self
