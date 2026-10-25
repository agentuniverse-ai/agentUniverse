# Perplexity (Sonar) LLM Use

`PerplexityLLM` integrates the [Perplexity](https://www.perplexity.ai) API into agentUniverse. Perplexity is the company behind the **Sonar** family of online large language models: the fast and lightweight `sonar`, the extended-context `sonar-pro`, the chain-of-thought `sonar-reasoning` / `sonar-reasoning-pro` variants and the multi-step research model `sonar-deep-research`. Sonar models combine an LLM with live web search and return grounded answers with citations.

Perplexity exposes a fully **OpenAI-compatible** Chat Completions API at `https://api.perplexity.ai`, so the `PerplexityLLM` component simply extends `OpenAIStyleLLM` and only wires up the Perplexity credentials, API base URL and per-model context-length table. Streaming, tool calling, the async interface and the Langchain bridge all work out of the box.

---

## 1. Create the configuration file

Create a YAML file, for example `user_perplexity_llm.yaml`, and paste the following content into it.

```yaml
name: 'user_perplexity_llm'
description: 'user perplexity llm powered by the Perplexity Sonar models'
model_name: 'sonar'
max_tokens: 1000
temperature: 0.5
streaming: True
api_key: '${PERPLEXITY_API_KEY}'
api_base: 'https://api.perplexity.ai'
proxy: '${PERPLEXITY_PROXY}'
metadata:
  type: 'LLM'
  module: 'agentuniverse.llm.default.perplexity_llm'
  class: 'PerplexityLLM'
```

A ready-to-use `perplexity_llm.yaml.example` also ships with the source tree at
`agentuniverse/llm/default/perplexity_llm.yaml.example`.

**Note:** Model parameters such as `api_key`, `api_base` and `proxy` can be configured in three ways:

1. **Direct string value** - enter the API key directly in the configuration file.

    ```yaml
    api_key: 'pplx-***'
    ```

2. **Environment variable placeholder** - use the `${VARIABLE_NAME}` syntax to load the value from an environment variable. When agentUniverse starts it will automatically read the corresponding value.

    ```yaml
    api_key: '${PERPLEXITY_API_KEY}'
    ```

3. **Custom function loading** - use the `@FUNC` annotation to dynamically load the API key through a custom function at runtime.

    ```yaml
    api_key: '@FUNC(load_api_key(model_name="sonar"))'
    ```

    The function must be defined in the `YamlFuncExtension` class inside the `yaml_func_extension.py` file. Refer to the example in the sample project's [YamlFuncExtension](../../../../../../examples/sample_standard_app/config/yaml_func_extension.py). When agentUniverse loads this configuration it parses the `@FUNC` annotation, executes the `load_api_key` function with the supplied arguments, and replaces the annotation with the function's return value.

---

## 2. Pick a model

Perplexity regularly ships new Sonar models. Below are the models currently available on the Perplexity API together with their indicative context window (input + output tokens). The same values are hard-coded inside `PerplexityLLM.max_context_length`, so agentUniverse can budget prompts correctly even without a live API call.

| Model name             | Indicative context length |
| ---------------------- | ------------------------- |
| `sonar`                | 127072                    |
| `sonar-pro`            | ~200000 (200k)            |
| `sonar-reasoning`      | 127072                    |
| `sonar-reasoning-pro`  | ~128000 (128k)            |
| `sonar-deep-research`  | 127072                    |

**Note:** Perplexity documents an online context of 127072 tokens for the sonar generation and describes the limits as roughly 200k for `sonar` / `sonar-pro` and ~128k for `sonar-reasoning-pro`. Because the effective window depends on how much live search context is injected at request time, the table above is *indicative* — treat it as a budgeting aid rather than a hard guarantee.

Perplexity publishes both offline and `<modelname>-online` flavours of the Sonar models. `PerplexityLLM` resolves a trailing `-online` suffix (e.g. `sonar-online`) to the base model's context window automatically.

Always confirm the latest list on the [Perplexity models documentation](https://docs.perplexity.ai/guides/getting-started) page. If a model is not present in the table above, `PerplexityLLM` falls back to a conservative default of 8192 tokens.

---

## 3. Environment setup

The example YAML uses environment variable placeholders. The following section describes how to set those variables.

Required: `PERPLEXITY_API_KEY`
Optional: `PERPLEXITY_API_BASE`, `PERPLEXITY_PROXY`

### 3.1 Configure through Python code

```python
import os
os.environ['PERPLEXITY_API_KEY'] = 'pplx-***'
os.environ['PERPLEXITY_API_BASE'] = 'https://api.perplexity.ai'
```

### 3.2 Configure through the configuration file

In the `custom_key.toml` file located in your project's `config` directory, add the following entries:

```toml
PERPLEXITY_API_KEY="pplx-******"
PERPLEXITY_API_BASE="https://api.perplexity.ai"
PERPLEXITY_PROXY=""
```

---

## 4. Obtaining the Perplexity API key

1. Sign in at [https://www.perplexity.ai](https://www.perplexity.ai).
2. Open **Settings -> API** and generate a new API key.
3. Copy the generated `pplx-...` key and assign it to `PERPLEXITY_API_KEY`.

Pricing, rate limits and the free-tier terms are documented at [https://docs.perplexity.ai](https://docs.perplexity.ai).

---

## 5. Using the LLM in code

After the configuration is loaded by agentUniverse you can obtain the LLM instance and call it directly:

```python
from agentuniverse.llm.default.perplexity_llm import PerplexityLLM

llm = PerplexityLLM(model_name='sonar')

# Non-streaming
output = llm.call(messages=[{"role": "user", "content": "Hello!"}])
print(output.text)

# Streaming
for chunk in llm.call(messages=[{"role": "user", "content": "Count 1 to 5."}], streaming=True):
    print(chunk.text, end='')

# Async
import asyncio
async def main():
    out = await llm.acall(messages=[{"role": "user", "content": "Hello!"}])
    print(out.text)
asyncio.run(main())
```

Because Perplexity is OpenAI-compatible, every feature supported by `OpenAIStyleLLM` - tool calling, LangChain integration, tracing - is available without any extra work.

---

## 6. Tips

- agentUniverse ships with a ready-to-use template named `default_perplexity_llm` (see `perplexity_llm.yaml.example`). After configuring the `PERPLEXITY_API_KEY` environment variable you can rename it to `perplexity_llm.yaml` and reference it directly from your agents.
- Sonar answers are grounded in live web search results and the raw response carries a `citations` array (available through `output.raw`); pair the model with agentUniverse knowledge-base agents when fresh facts matter more than a private corpus.
- `sonar` is the cheapest and fastest entry point, `sonar-pro` handles longer prompts with more thorough search, the `sonar-reasoning` family exposes its chain of thought, and `sonar-deep-research` performs exhaustive multi-step retrieval — at correspondingly higher latency and cost.
