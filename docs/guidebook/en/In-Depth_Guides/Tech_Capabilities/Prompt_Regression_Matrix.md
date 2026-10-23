# Offline Prompt regression matrix

Capture approved fixture inputs as golden messages using the real PromptConfiger, PromptManager, Agent.process_prompt inheritance, ChatPrompt and LangChain rendering path. No LLM/provider is called. This checks rendering regressions, not prompt quality or model responses.

Create a JSON fixture with paths to actual Prompt YAML files (relative to the fixture):

```json
{
  "version": 1,
  "prompts": [{"path": "prompts/demo/v1.yaml"}],
  "cases": [{
    "id": "english",
    "profile": {"prompt_version": "demo.v1"},
    "inputs": {},
    "bindings": {"name": "Ada"}
  }]
}
```

Example `prompts/demo/v1.yaml`:

```yaml
instruction: 'Hello {name}'
metadata:
  version: demo.v1
  type: PROMPT
```

```sh
# Explicitly approve creating/replacing the golden file:
python -X utf8 -m agentuniverse.prompt.regression_matrix fixture.json golden.json --update
# Normal check: never writes the baseline; exit 1 on differences/render failures.
python -X utf8 -m agentuniverse.prompt.regression_matrix fixture.json golden.json
```

Missing baseline files fail instead of being silently created. Failed rendering or missing variables cannot be approved. Update writes a flushed temporary file and replaces the selected baseline atomically; the fixture and prompt files cannot be selected as the baseline. No automatic update occurs. Review golden diffs before committing them.

`profile` supports introduction, target, instruction and prompt_version. The base Agent's actual precedence rules apply (including the distinction between null and empty string). `inputs` supports expert_framework, image_urls and audio_url. `bindings` supplies text-template variables. HTTP(S) media references are retained as actual multimodal messages without downloading media. Local media paths are rejected to prevent accidental fixture reads; this harness does not verify remote image/audio contents. Cases can cover multiple languages and profiles against multiple registered prompt versions.

The CLI supports only literal built-in Prompt YAML fields and metadata. Custom meta_class/classes, dynamic @FUNC/environment placeholders, duplicate YAML keys and ambiguous values are rejected; they are not silently emulated. This is deliberately not a generic application bootstrap. `render_matrix(cases)` can also run against an already registered stable PromptManager in a dedicated test process. It does not modify the registered prompts or inputs. The CLI temporarily registers selected prompts and restores the registry afterward; do not run its `main()` concurrently with a live application's registry mutations.

Snapshots contain deterministic role/content messages. Missing variables, missing prompt versions and rendering errors are explicit case statuses; exception text is omitted to avoid copying fixture contents into error messages. Diff output naturally contains rendered content: use only approved synthetic or shareable fixtures. File/case/output sizes are bounded, and JSON/YAML inputs never execute component code. Existing dependency warnings may appear on stderr.
