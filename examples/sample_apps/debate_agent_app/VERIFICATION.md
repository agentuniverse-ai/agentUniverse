# Debate application verification

Verified on 2026-11-16, macOS 26.6 / arm64, Python 3.12.14.
Base PR revision: `2ec5a10c0c556795937b71584ed0d557a223de3b`.
The follow-up commit containing this report is the tested source (see Git history).

## Environment and rerun

From the repository root, in an isolated virtual environment:

```bash
pip install -e . pytest "httpx==0.27.2"
python -m pytest tests/test_agentuniverse/unit/agent/work_pattern/test_debate_work_pattern.py \
  examples/sample_apps/debate_agent_app/intelligence/test/test_debate_agent.py -q
```

The environment used the project's OpenAI 1.55.3, LangChain 0.1.20 and
langchain-core 0.1.52. HTTPX was pinned to 0.27.2 to avoid the removed `proxies`
constructor argument used by this OpenAI SDK version; no shared dependency
constraints were changed as part of this feature.

Result: **11 passed** (9 existing work-pattern unit tests, 2 application
integration cases), in 2.77 seconds. The application tests copy the sample into
a temporary directory and start its real TOML/YAML configuration. A local HTTP
server implements Chat Completions; the actual agents, prompts, LangChain/OpenAI
client and RAM memory storage run normally. Both sync and async cases execute
two rounds, pass the first critique into the next proposal, reach score 80,
stop at the threshold, parse the judge JSON and retrieve the final exchange by
session ID and coordinator agent ID. The HTTP fixture closes on teardown.

## Live services

Set these variables in a private shell environment; do not commit credentials:

```bash
export OPENAI_API_KEY="<private key>"
export OPENAI_API_BASE="<OpenAI-compatible service URL>"
export DEBATE_MODEL_NAME="<available model>"
RUN_LIVE_LLM_TESTS=1 python -m pytest \
  examples/sample_apps/debate_agent_app/intelligence/test/test_debate_agent.py -q -s
```

| Backend and adapter | Model | Sync | Async | Observed judgment |
| --- | --- | --- | --- | --- |
| User-provided OpenAI-compatible relay, DefaultOpenAILLM | gpt-6-luna | passed | passed | 1 round, score 100 in both cases |
| DeepSeek API, DefaultOpenAILLM (OpenAI-compatible endpoint) | deepseek-flash | passed | passed | 1 round, score 95 in both cases |

Both services returned the correct answer to the test question, `2 + 2`, through
all three roles. Judge JSON parsing, threshold-based early stopping and
coordinator memory persistence passed in all four runs. Results: **2 passed in
31.42s** for the relay; **2 passed in 22.89s** for DeepSeek. The tests cap model
output at 1024 tokens and disable SDK retries in their temporary LLM config.

These results cover the Chat Completions path in DefaultOpenAILLM. They do not
claim validation of the native DefaultDeepSeekLLM adapter, Anthropic protocol,
streaming, every model, or answer quality on complex tasks. Live generation is
variable; the deterministic two-round regression remains in the offline cases.
The relay's requested older sample model was unavailable, so validation used its
listed and successfully callable model. Private URLs, keys and raw authenticated
traffic are deliberately omitted from this report.

## Problems found and corrected

- AgentConfiger reads memory at the Agent YAML root. The sample had nested it
  under profile, so the intended memory was never connected. All four YAMLs now
  declare root-level memory; demo_memory also selects ram_memory_storage for
  retrieval.
- The coordinator treated its memory configuration dictionary as a Memory
  instance and called an unavailable add_message API. It now obtains memory
  through process_memory and persists through the framework's add_memory API,
  retaining the session and agent identity.
- Per-role model overrides prevented a single shared model/backend switch.
  Roles now inherit the shared LLM model resolved from DEBATE_MODEL_NAME.
- The old sample tests performed expensive manual live examples without testing
  configuration and persisted state. The same test file now contains automated
  sync/async application integration cases, with live calls explicitly enabled.

## Changed files

- agentuniverse/agent/template/debate_agent_template.py: framework memory access.
- Four debate_case Agent YAMLs: memory location and shared model inheritance.
- default_openai_llm.yaml: environment-based model selection.
- demo_memory.yaml: RAM retrieval storage.
- intelligence/test/test_debate_agent.py: actual app/HTTP integration coverage.
- simple_example.py: default model environment value.
- README.md, CHANGELOG.md and this file: setup, rerun and evidence.

No repository files were deleted. Tests write logs/database state into pytest's
temporary application directory, outside the source checkout. No API keys are
part of the committed source or public verification evidence.

## Final compatibility review

On 2026-11-16, merged upstream master
`f69b130bacaa784289ec8dc2a9798d122cd8fe5a` and reran the same combined
offline suite: **11 passed in 2.37s**. This exercises current framework
configuration loading, memory storage and HTTP client integration.
The earlier live-model results above remain evidence for the follow-up source
`b25e83700cd91aec0ab647f690a343eafa967a33`; no additional model calls were
needed for the upstream merge. The shared OpenAI client still sends the same
Chat Completions requests for these nonstreaming cases.

Also corrected the changelog's unsupported 1–10-round range claim; runtime
configuration remains as implemented, including the tested zero-round case.
No repository files were deleted by this follow-up. Other files brought in by
the merge are upstream changes, outside the feature diff against current master.
