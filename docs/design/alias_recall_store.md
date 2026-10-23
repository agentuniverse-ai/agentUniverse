# Configured glossary recall

AliasRecallStore queries one registered backend with the original query, then
explicit one-step glossary variants, **sequentially within each call**. It returns
an original-first union by Document ID. Use it when a controlled domain glossary
maps abbreviations/model names to terms present in the corpus. No LLM calls or
automatic synonym inference occur. Bad/ambiguous glossary entries can reduce
precision; this is not a guarantee of relevance improvement.

## Configure

Copy `agentuniverse/agent/action/knowledge/store/alias_recall_store.yaml.example`
into the application's store-config directory with a `.yaml` suffix. Set
`backend_store` to an existing store and supply `aliases`, for example:

```yaml
backend_store: manuals
aliases:
  EV:
    - electric vehicle
boundary: word
max_variants: 4
max_result_documents: 1000
```

Select `stores: [alias_recall_store]` in Knowledge and retain its ordinary router.
The shipped glossary is empty, so it performs one original lookup until configured.
Insert/upsert/update/delete (sync and async) pass through once to the backend, not
once per alias. Backend initialization/clients remain framework-owned.

The AliasQueryRouter class is used as a bounded internal planning helper, **not
shipped as a registered parallel router**. Initial real SQLite integration showed
that parallel alias routes could concurrently use SQLiteStore's shared connection
and fail. The supported entry point therefore executes variants sequentially in
AliasRecallStore. This does not serialize separate user requests or repair backend
thread safety; the backend must still support its deployment's concurrency.

## Exact semantics

- Original query first, followed by terms in their first matched source order;
  configured aliases retain their order. Text-identical variants are deduplicated.
- Matching is case-sensitive and literal, never a configurable regex. At the same
  source position longer overlapping terms win. A variant replaces all selected
  occurrences of one term; it does not combine different terms' aliases or cascade
  through replacement text. The original text is never normalized.
- `word` boundaries use Unicode alphanumeric characters/underscore at term edges.
  `substring` explicitly permits matching embedded terms, useful in unsegmented
  Chinese text but more prone to false matches.
- Default maximum 4 variants includes the original. Earlier variants win when the
  limit is reached. The planning helper also caps route count at 32; no unbounded
  Cartesian product of replacements or stores is generated.
- Every routed Query is independently deep-copied. Rewritten queries clear old
  keywords and embeddings, so they cannot reuse representations of the original
  words. Filters/ext_info and similarity_top_k remain unchanged. Image/text-bundle
  queries cannot be rewritten; query-only embeddings can remain on the original.
- A vector backend needs an embedding model to embed rewritten text. A backend
  that requires precomputed vectors only is unsuitable for alias expansion.
- The original backend result order wins, then new IDs from later variants. Scores
  are not normalized or compared across variants. The per-query top_k applies to
  each backend call, not the combined union; explicit combined budgets apply below.
  With Knowledge/RRF the wrapper is one store/channel, not extra votes per alias.
- Caller kwargs are copied per query. Returned documents are copied and ID-deduped;
  nested metadata cannot be changed by a caller through another returned copy.
  No extra query-provenance fields are injected into backend filters/documents.

## Failure and resource policy

Glossaries are limited to 128 terms, 16 replacements per term and 32,768 total
characters; term length 128, replacement length 256. Queries/expanded variants
default to 4,096 characters. NUL, blank terms/aliases, invalid options and oversized
expansion fail before backend calls. Default combined limits are 1,000 documents
and 2 million text characters, failing rather than silently truncating.

These bound expansion and retained text, not backend latency, metadata size or
peak provider memory. Metadata must be deep-copyable. Up to max_variants sequential
calls may multiply latency/cost; configure provider timeouts separately. Async
cancellation propagates to the currently awaited provider and no later variants
are started; cleanup remains the provider's responsibility.

Any provider error aborts the wrapper query rather than claiming partial recall
is complete. Existing Knowledge may log/suppress a failed store according to its
own contract. Nested AliasRecallStore backends are rejected; do not create indirect
cycles through other wrappers. Configuration must not be changed mid-request.
Aliases/filters are not an authorization mechanism.

## Evidence and scope

The actual integration loads a copied YAML template, registers real Store/router/
Jieba managers and reopens a real SQLite database. Baseline `EV` retrieves one
document; adding the configured `electric vehicle` query retrieves a second document
containing only that expansion while retaining the original match exactly once.
This is a controlled two-document fixture, not a production relevance benchmark.
Only tracing is patched in that integration. Unit tests additionally cover phrase
overlaps, Unicode boundaries, representation invalidation, caps, async cancellation
and all write delegates. Existing RRF integration tests run unchanged.
