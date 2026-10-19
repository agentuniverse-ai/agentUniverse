"""Provider totals include overlapping cached/reasoning detail counters."""
import copy

from openai.types import CompletionUsage
from openai.types.chat import ChatCompletionChunk
import pytest

from agentuniverse.llm.llm_output import LLMOutput, TokenUsage


def chat_usage():
    return {
        "prompt_tokens": 100,
        "completion_tokens": 30,
        "total_tokens": 130,
        "prompt_tokens_details": {"cached_tokens": 40},
        "completion_tokens_details": {"reasoning_tokens": 10},
    }


def assert_totals(usage, prompt, completion):
    assert usage.prompt_tokens == prompt
    assert usage.completion_tokens == completion
    assert usage.total_tokens == prompt + completion
    serialized = usage.to_dict()
    assert serialized["prompt_tokens"] == prompt
    assert serialized["completion_tokens"] == completion
    assert serialized["total_tokens"] == prompt + completion


def test_sdk_chat_usage_does_not_add_cache_and_reasoning_twice():
    payload = CompletionUsage.model_validate(chat_usage())

    usage = TokenUsage.from_openai(payload.model_dump())

    assert_totals(usage, 100, 30)
    assert usage.cached_tokens == 40
    assert usage.reasoning_tokens == 10


def test_explicit_modality_details_can_overlap_cache_counts():
    usage = TokenUsage.from_openai({
        "prompt_tokens": 12, "completion_tokens": 8,
        "prompt_tokens_details": {
            "text_tokens": 5, "audio_tokens": 7, "cached_tokens": 9,
        },
        "completion_tokens_details": {
            "text_tokens": 3, "audio_tokens": 5, "reasoning_tokens": 2,
        },
    })

    assert_totals(usage, 12, 8)
    assert (usage.text_in, usage.audio_in, usage.cached_in) == (5, 7, 9)
    assert (usage.text_out, usage.audio_out, usage.reasoning_out) == (3, 5, 2)


def test_existing_input_output_branch_preserves_provider_totals():
    usage = TokenUsage.from_openai({
        "input_tokens": 20, "output_tokens": 10,
        "input_tokens_details": {"text_tokens": 8, "image_tokens": 12,
                                 "cached_tokens": 5},
        "output_token_details": {"text_tokens": 10, "reasoning_tokens": 4},
    })

    assert_totals(usage, 20, 10)
    assert usage.image_in == 12
    assert usage.cached_in == 5
    assert usage.reasoning_out == 4


def test_sdk_usage_chunk_reaches_public_channel_parser():
    from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

    chunk = ChatCompletionChunk(
        id="local-usage-chunk", created=0, model="local-fixture",
        object="chat.completion.chunk", choices=[],
        usage=CompletionUsage.model_validate(chat_usage()),
    )

    output = LLMChannel.parse_result(chunk)

    assert isinstance(output, LLMOutput)
    assert_totals(output.usage, 100, 30)


@pytest.mark.parametrize("reverse", [False, True])
def test_adding_provider_and_manual_counts_preserves_both_contracts(reverse):
    provider = TokenUsage.from_openai(chat_usage())
    manual = TokenUsage(text_in=5, cached_in=2, text_out=3, reasoning_out=1)
    before = provider.model_dump(), manual.model_dump()

    combined = manual + provider if reverse else provider + manual

    assert_totals(manual, 7, 4)
    assert_totals(combined, 107, 34)
    assert combined.cached_tokens == 42
    assert combined.reasoning_tokens == 11
    assert before == (provider.model_dump(), manual.model_dump())


def test_in_place_accumulation_keeps_provider_totals_and_identity():
    usage = TokenUsage()
    original = usage
    usage += TokenUsage.from_openai(chat_usage())
    usage += TokenUsage.from_openai(chat_usage())
    usage += TokenUsage(text_in=5, text_out=2)

    assert usage is original
    assert_totals(usage, 205, 62)
    assert usage.cached_tokens == 80
    assert usage.reasoning_tokens == 20


def test_self_accumulation_keeps_reported_totals():
    usage = TokenUsage.from_openai(chat_usage())
    original = usage
    usage += usage

    assert usage is original
    assert_totals(usage, 200, 60)


def test_nested_model_json_round_trip_preserves_authoritative_totals():
    original = LLMOutput(text="local", usage=TokenUsage.from_openai(chat_usage()))

    restored = LLMOutput.model_validate_json(original.model_dump_json())

    assert restored == original
    assert_totals(restored.usage, 100, 30)
    assert_totals(restored.usage + TokenUsage(text_in=1), 101, 30)


def test_to_dict_round_trip_does_not_reinflate_totals():
    usage = TokenUsage.from_openai(chat_usage())

    restored = TokenUsage.from_openai(usage.to_dict(keep_zero=True))

    assert_totals(restored, 100, 30)
    assert restored.cached_tokens == 40
    assert restored.reasoning_tokens == 10


def test_original_usage_payload_is_not_modified():
    payload = chat_usage()
    expected = copy.deepcopy(payload)

    usage = TokenUsage.from_openai(payload)

    assert payload == expected
    assert_totals(usage, 100, 30)


def test_legacy_manual_dump_and_addition_keep_existing_shape():
    usage = TokenUsage(text_in=3, cached_in=2, reasoning_out=1)
    fields = set(usage.model_dump())

    assert fields == {
        "text_in", "image_in", "audio_in", "cached_in", "text_out",
        "image_out", "audio_out", "cached_out", "reasoning_out",
    }
    assert_totals(usage, 5, 1)
    usage += usage
    assert_totals(usage, 10, 2)
    assert set(usage.model_dump()) == fields


@pytest.mark.parametrize("details", [None, [], "invalid"])
def test_non_mapping_details_still_use_reported_totals(details):
    usage = TokenUsage.from_openai({
        "prompt_tokens": 4, "completion_tokens": 2,
        "prompt_tokens_details": details, "completion_tokens_details": details,
    })

    assert_totals(usage, 4, 2)


def test_empty_usage_remains_zero():
    assert_totals(TokenUsage.from_openai({}), 0, 0)
