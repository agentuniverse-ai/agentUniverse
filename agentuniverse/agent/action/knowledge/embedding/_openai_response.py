"""Response alignment shared by the OpenAI and Azure OpenAI adapters."""
from typing import List, Sequence

from openai.types import Embedding


def ordered_embeddings(data: Sequence[Embedding], input_count: int) -> List[List[float]]:
    """Return a complete embedding batch in input-index order.

    Args:
        data: Embedding records decoded by the OpenAI SDK.
        input_count: Number of texts sent in this request.

    Returns:
        The original vectors in input order, without modifying response records.

    Raises:
        ValueError: If the count or indices cannot identify exactly one vector
            for every input. SDK response construction can retain invalid types.
    """
    if len(data) != input_count:
        raise ValueError(
            f"Invalid embedding response: expected {input_count} records, got {len(data)}"
        )
    by_index = {}
    for position, item in enumerate(data):
        index = getattr(item, "index", None)
        # bool is an int subclass, but cannot identify an input position here.
        if type(index) is not int or not 0 <= index < input_count:
            raise ValueError(
                f"Invalid embedding response: record {position} must have an integer "
                f"index in [0, {input_count})"
            )
        if index in by_index:
            raise ValueError(f"Invalid embedding response: duplicate index {index}")
        by_index[index] = item.embedding
    return [by_index[index] for index in range(input_count)]
