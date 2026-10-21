# Privacy-Guarded Knowledge Q&A (privacy_guard_app)

A customer-support ticket Q&A sample where the knowledge base is **redacted before it ever reaches the LLM**. The sample tickets contain fictional emails, phone numbers, bank cards, national IDs and employee IDs; an agentUniverse DocProcessor pipeline redacts them at insert time and applies a second pass at recall time.

Highlights:

- Double redaction pipeline: `ticket_redactor` at insert (with custom employee-ID / order-No regexes) plus `recall_redactor` at recall (`log_key: null` so it never overwrites the insert-time statistics)
- Per-document `redaction_summary` metadata so answers can state what was masked
- BM25 retrieval via SQLiteStore + jieba — the whole retrieval path runs **offline with zero API keys**
- Sample card/ID numbers are structurally valid fakes: the component only redacts values passing Luhn / GB11643 checks, keeping false positives low

Quick start (offline, no keys):

```bash
cd examples/sample_apps/privacy_guard_app
export PYTHONPATH=$(pwd)/../../..:$(cd ../.. && pwd)
python intelligence/test/privacy_pipeline_test.py
```

For the online answer step, copy `config/custom_key.toml.sample` to `config/custom_key.toml` and set `DEEPSEEK_API_KEY`.

See [README_zh.md](README_zh.md) for the full Chinese walkthrough.
