# OpenAI-compatible provider context limits

The Gemini, Kimi, Baichuan and Qwen adapters use this precedence when computing
`max_context_length()`:

1. An explicit `max_context_length` from LLM configuration or agent-model overrides.
2. The adapter's existing model-specific context table.
3. The adapter's existing 8000-token fallback for an unknown model name.

Using an OpenAI-compatible transport does not make these models use the generic
OpenAI table or its 4096-token fallback. This matters because prompt processing
subtracts `max_tokens` from the context limit before truncating background text
or rejecting an output-token budget that leaves no room for input.

This change does not update provider model specifications or add model names.
For a model absent from the existing table, configure `max_context_length`
explicitly based on the limits of the actual deployment. The generic
`OpenAIStyleLLM` fallback is unchanged.
