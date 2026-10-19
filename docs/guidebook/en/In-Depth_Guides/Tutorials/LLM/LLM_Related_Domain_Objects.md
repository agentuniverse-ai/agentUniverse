# LLM and Related Domain Objects
In this chapter, we will highlight LLM and related core domain objects. We have omitted their corresponding code parts. If you wish to learn more, please read the [API Reference](../../../In-Depth_Guides/Tech_Capabilities/Others/API_Reference.md) Section.

## LLM Base Class
Package path: `agentuniverse.llm.llm.LLM`

## LLM Manager
Package path: `agentuniverse.llm.llm_manager.LLMManager`

## Output Object
Package path:`agentuniverse.llm.llm_output.LLMOutput`

### Token usage totals

`TokenUsage.from_openai()` preserves the API's input and output totals in
`reported_prompt_tokens` and `reported_completion_tokens`. Cached input and
reasoning output are already included in those totals, so summing all detail
counters can count tokens twice. The original detail counters remain available.
For example, 100 prompt tokens (40 cached) and 30 completion tokens (10 reasoning)
remain 130 total tokens. See the [OpenAI usage reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create).

`+` and `+=` accumulate totals as well as details. Pydantic serialization retains
reported totals when present, so restoring an `LLMOutput` preserves its counts.
Monitoring also preserves explicitly reported zero totals. When provider usage
is absent, the existing local token estimation remains available.
Changing a detail counter does not change an explicitly reported provider total.
Manually constructed `TokenUsage(...)` objects without reported totals retain
the existing additive behavior and serialized field layout.
