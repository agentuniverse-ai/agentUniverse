# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""split_texts must keep the original failure attached as the exception cause."""

import pytest

from agentuniverse.base.util import prompt_util


class _ExplodingLLM:
    """A minimal llm double whose whole job is to fail."""

    def get_num_tokens(self, text: str) -> int:  # pragma: no cover - never reached
        return 1


def test_split_texts_keeps_the_original_failure_as_the_cause(monkeypatch):
    boom = RuntimeError("tokenizer offline")

    def explode(*args, **kwargs):
        raise boom

    monkeypatch.setattr(prompt_util, "split_text_on_tokens", explode)

    with pytest.raises(ValueError) as caught:
        prompt_util.split_texts(texts=["a" * 50], llm=_ExplodingLLM(), chunk_size=10)

    # The wrapper message alone loses why it failed; the cause carries it.
    assert caught.value.__cause__ is boom


def test_split_texts_retry_path_also_keeps_the_cause(monkeypatch):
    boom = RuntimeError("tokenizer offline")

    def explode(*args, **kwargs):
        raise boom

    monkeypatch.setattr(prompt_util, "split_text_on_tokens", explode)

    with pytest.raises(ValueError) as caught:
        prompt_util.split_texts(texts=["a" * 50], llm=_ExplodingLLM(), chunk_size=10, retry=True)

    assert caught.value.__cause__ is boom
