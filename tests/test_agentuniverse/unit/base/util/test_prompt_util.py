import pytest

from agentuniverse.base.util.prompt_util import split_text_on_tokens


def test_split_empty_text_with_zero_tokens():
    assert split_text_on_tokens("", 0) == [""]


@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap", "message"),
    [
        (0, 0, "chunk_size must be greater than zero"),
        (10, -1, "chunk_overlap must not be negative"),
        (10, 10, "chunk_overlap must be smaller than chunk_size"),
        (10, 11, "chunk_overlap must be smaller than chunk_size"),
    ],
)
def test_split_text_rejects_invalid_chunk_configuration(
    chunk_size, chunk_overlap, message
):
    with pytest.raises(ValueError, match=message):
        split_text_on_tokens("content", 1, chunk_size, chunk_overlap)


def test_split_text_makes_progress_when_character_chunks_round_to_same_size():
    chunks = split_text_on_tokens(
        "abc", text_token=100, chunk_size=40, chunk_overlap=39
    )

    assert chunks == ["a", "b", "c"]


def test_split_non_empty_text_requires_positive_token_count():
    with pytest.raises(ValueError, match="text_token must be greater than zero"):
        split_text_on_tokens("content", 0)
