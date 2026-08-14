"""Portable JSON Lines serialization for memory messages."""

# Dynamic, line-specific import errors are the public API of this module.
# ruff: noqa: TRY003

import json
from collections.abc import Iterable

from pydantic import ValidationError

from agentuniverse.agent.memory.message import Message


class TranscriptFormatError(ValueError):
    """Raised when transcript text cannot be decoded or parsed."""


class TranscriptTypeError(TypeError):
    """Raised when transcript APIs receive unsupported object types."""


def messages_to_jsonl(messages: Iterable[Message]) -> str:
    """Serialize an ordered message sequence as newline-delimited JSON.

    Every Pydantic field is preserved, including message identifiers. A final
    newline is emitted for non-empty transcripts so the result can be safely
    appended to JSONL files and streams.
    """
    records = []
    for index, message in enumerate(messages, start=1):
        if not isinstance(message, Message):
            raise TranscriptTypeError(f"Transcript item {index} must be a Message.")
        records.append(
            json.dumps(
                message.model_dump(mode="json"),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
    if not records:
        return ""
    return "\n".join(records) + "\n"


def messages_from_jsonl(transcript: str | bytes) -> list[Message]:
    """Load messages from JSONL text or UTF-8 bytes.

    Empty lines are ignored. Parse and validation failures include the source
    line number so imported transcripts can be repaired efficiently.
    """
    if isinstance(transcript, bytes):
        try:
            transcript = transcript.decode("utf-8")
        except UnicodeDecodeError as error:
            raise TranscriptFormatError("Transcript bytes must contain valid UTF-8.") from error
    if not isinstance(transcript, str):
        raise TranscriptTypeError("Transcript must be str or bytes.")

    messages = []
    for line_number, line in enumerate(transcript.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise TranscriptFormatError(f"Invalid JSON on transcript line {line_number}: {error.msg}.") from error
        try:
            messages.append(Message.model_validate(record))
        except ValidationError as error:
            raise TranscriptFormatError(f"Invalid message on transcript line {line_number}: {error}") from error
    return messages
