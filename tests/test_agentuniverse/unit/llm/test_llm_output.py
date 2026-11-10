from agentuniverse.llm.llm_output import TokenUsage


def test_from_openai_parses_realtime_singular_detail_keys():
    usage = TokenUsage.from_openai(
        {
            "input_tokens": 13,
            "output_tokens": 9,
            "input_token_details": {
                "text_tokens": 8,
                "audio_tokens": 2,
                "cached_tokens": 3,
            },
            "output_token_details": {
                "text_tokens": 5,
                "audio_tokens": 4,
            },
        }
    )

    assert usage.text_in == 8
    assert usage.audio_in == 2
    assert usage.cached_in == 3
    assert usage.text_out == 5
    assert usage.audio_out == 4


def test_from_openai_parses_plural_output_detail_keys():
    usage = TokenUsage.from_openai(
        {
            "input_tokens": 12,
            "output_tokens": 5,
            "input_tokens_details": {
                "text_tokens": 5,
                "image_tokens": 7,
            },
            "output_tokens_details": {
                "text_tokens": 1,
                "image_tokens": 4,
            },
        }
    )

    assert usage.text_in == 5
    assert usage.image_in == 7
    assert usage.text_out == 1
    assert usage.image_out == 4
