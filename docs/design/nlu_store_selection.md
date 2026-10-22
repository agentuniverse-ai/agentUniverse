# NLU store selection

The NLU RAG router treats `store_amount` as the maximum number of distinct
configured stores to query. Comma-separated model output is stripped, empty
tokens and unknown names are removed, and repeated names are deduplicated before
the limit is applied. Names remain case-sensitive and first-seen order is kept.

For configured stores `alpha` and `beta`, a response of
`unknown, alpha, alpha, beta` with `store_amount=2` routes once to each store.
Previously unknown or repeated names consumed slots, omitting relevant stores
or querying one store twice. This does not invent a fallback selection when no
valid name is returned, change the prompt, or change the query object.
