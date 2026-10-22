"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten96kitten96", "a2l0dGVuOTZraXR0ZW45Ng"),
    ("kitten96sitting96", "a2l0dGVuOTZzaXR0aW5nOTY"),
    ("kitten96agent96", "a2l0dGVuOTZhZ2VudDk2"),
    ("kitten96angle96", "a2l0dGVuOTZhbmdsZTk2"),
    ("sitting96angle96", "c2l0dGluZzk2YW5nbGU5Ng"),
    ("sitting96universe96", "c2l0dGluZzk2dW5pdmVyc2U5Ng"),
    ("sitting96memory96", "c2l0dGluZzk2bWVtb3J5OTY"),
    ("sitting96stream96", "c2l0dGluZzk2c3RyZWFtOTY"),
    ("agent96stream96", "YWdlbnQ5NnN0cmVhbTk2"),
    ("agent96context96", "YWdlbnQ5NmNvbnRleHQ5Ng"),
    ("agent96knowledge96", "YWdlbnQ5Nmtub3dsZWRnZTk2"),
    ("agent96vector96", "YWdlbnQ5NnZlY3Rvcjk2"),
    ("angle96vector96", "YW5nbGU5NnZlY3Rvcjk2"),
    ("angle96processor96", "YW5nbGU5NnByb2Nlc3Nvcjk2"),
    ("angle96reasoning96", "YW5nbGU5NnJlYXNvbmluZzk2"),
    ("angle96machine96", "YW5nbGU5Nm1hY2hpbmU5Ng"),
    ("universe96machine96", "dW5pdmVyc2U5Nm1hY2hpbmU5Ng"),
    ("universe96learning96", "dW5pdmVyc2U5NmxlYXJuaW5nOTY"),
    ("universe96model96", "dW5pdmVyc2U5Nm1vZGVsOTY"),
    ("universe96token96", "dW5pdmVyc2U5NnRva2VuOTY"),
    ("memory96token96", "bWVtb3J5OTZ0b2tlbjk2"),
    ("memory96prompt96", "bWVtb3J5OTZwcm9tcHQ5Ng"),
    ("memory96session96", "bWVtb3J5OTZzZXNzaW9uOTY"),
    ("memory96library96", "bWVtb3J5OTZsaWJyYXJ5OTY"),
    ("stream96library96", "c3RyZWFtOTZsaWJyYXJ5OTY"),
    ("stream96service96", "c3RyZWFtOTZzZXJ2aWNlOTY"),
    ("stream96gateway96", "c3RyZWFtOTZnYXRld2F5OTY"),
    ("stream96storage96", "c3RyZWFtOTZzdG9yYWdlOTY"),
    ("context96storage96", "Y29udGV4dDk2c3RvcmFnZTk2"),
    ("context96network96", "Y29udGV4dDk2bmV0d29yazk2"),
    ("context96latency96", "Y29udGV4dDk2bGF0ZW5jeTk2"),
    ("context96buffer96", "Y29udGV4dDk2YnVmZmVyOTY"),
    ("knowledge96buffer96", "a25vd2xlZGdlOTZidWZmZXI5Ng"),
    ("knowledge96queue96", "a25vd2xlZGdlOTZxdWV1ZTk2"),
    ("knowledge96worker96", "a25vd2xlZGdlOTZ3b3JrZXI5Ng"),
    ("knowledge96kernel96", "a25vd2xlZGdlOTZrZXJuZWw5Ng"),
    ("vector96kernel96", "dmVjdG9yOTZrZXJuZWw5Ng"),
    ("vector96signal96", "dmVjdG9yOTZzaWduYWw5Ng"),
    ("vector96packet96", "dmVjdG9yOTZwYWNrZXQ5Ng"),
    ("vector96router96", "dmVjdG9yOTZyb3V0ZXI5Ng"),
    ("processor96router96", "cHJvY2Vzc29yOTZyb3V0ZXI5Ng"),
    ("processor96cluster96", "cHJvY2Vzc29yOTZjbHVzdGVyOTY"),
    ("processor96mirror96", "cHJvY2Vzc29yOTZtaXJyb3I5Ng"),
    ("processor96filter96", "cHJvY2Vzc29yOTZmaWx0ZXI5Ng"),
    ("reasoning96filter96", "cmVhc29uaW5nOTZmaWx0ZXI5Ng"),
    ("reasoning96ranking96", "cmVhc29uaW5nOTZyYW5raW5nOTY"),
    ("reasoning96encoding96", "cmVhc29uaW5nOTZlbmNvZGluZzk2"),
    ("reasoning96mapping96", "cmVhc29uaW5nOTZtYXBwaW5nOTY"),
    ("machine96mapping96", "bWFjaGluZTk2bWFwcGluZzk2"),
    ("machine96record96", "bWFjaGluZTk2cmVjb3JkOTY"),
    ("machine96candle96", "bWFjaGluZTk2Y2FuZGxlOTY"),
    ("machine96thread96", "bWFjaGluZTk2dGhyZWFkOTY"),
    ("learning96thread96", "bGVhcm5pbmc5NnRocmVhZDk2"),
    ("learning96kitten96", "bGVhcm5pbmc5NmtpdHRlbjk2"),
    ("learning96sitting96", "bGVhcm5pbmc5NnNpdHRpbmc5Ng"),
    ("learning96agent96", "bGVhcm5pbmc5NmFnZW50OTY"),
    ("model96agent96", "bW9kZWw5NmFnZW50OTY"),
    ("model96angle96", "bW9kZWw5NmFuZ2xlOTY"),
    ("model96universe96", "bW9kZWw5NnVuaXZlcnNlOTY"),
    ("model96memory96", "bW9kZWw5Nm1lbW9yeTk2"),
    ("token96memory96", "dG9rZW45Nm1lbW9yeTk2"),
    ("token96stream96", "dG9rZW45NnN0cmVhbTk2"),
    ("token96context96", "dG9rZW45NmNvbnRleHQ5Ng"),
    ("token96knowledge96", "dG9rZW45Nmtub3dsZWRnZTk2"),
    ("prompt96knowledge96", "cHJvbXB0OTZrbm93bGVkZ2U5Ng"),
    ("prompt96vector96", "cHJvbXB0OTZ2ZWN0b3I5Ng"),
    ("prompt96processor96", "cHJvbXB0OTZwcm9jZXNzb3I5Ng"),
    ("prompt96reasoning96", "cHJvbXB0OTZyZWFzb25pbmc5Ng"),
    ("session96reasoning96", "c2Vzc2lvbjk2cmVhc29uaW5nOTY"),
    ("session96machine96", "c2Vzc2lvbjk2bWFjaGluZTk2"),
    ("session96learning96", "c2Vzc2lvbjk2bGVhcm5pbmc5Ng"),
    ("session96model96", "c2Vzc2lvbjk2bW9kZWw5Ng"),
    ("library96model96", "bGlicmFyeTk2bW9kZWw5Ng"),
    ("library96token96", "bGlicmFyeTk2dG9rZW45Ng"),
    ("library96prompt96", "bGlicmFyeTk2cHJvbXB0OTY"),
    ("library96session96", "bGlicmFyeTk2c2Vzc2lvbjk2"),
    ("service96session96", "c2VydmljZTk2c2Vzc2lvbjk2"),
    ("service96library96", "c2VydmljZTk2bGlicmFyeTk2"),
    ("service96service96", "c2VydmljZTk2c2VydmljZTk2"),
    ("service96gateway96", "c2VydmljZTk2Z2F0ZXdheTk2"),
    ("gateway96gateway96", "Z2F0ZXdheTk2Z2F0ZXdheTk2"),
    ("gateway96storage96", "Z2F0ZXdheTk2c3RvcmFnZTk2"),
    ("gateway96network96", "Z2F0ZXdheTk2bmV0d29yazk2"),
    ("gateway96latency96", "Z2F0ZXdheTk2bGF0ZW5jeTk2"),
    ("storage96latency96", "c3RvcmFnZTk2bGF0ZW5jeTk2"),
    ("storage96buffer96", "c3RvcmFnZTk2YnVmZmVyOTY"),
    ("storage96queue96", "c3RvcmFnZTk2cXVldWU5Ng"),
    ("storage96worker96", "c3RvcmFnZTk2d29ya2VyOTY"),
    ("network96worker96", "bmV0d29yazk2d29ya2VyOTY"),
    ("network96kernel96", "bmV0d29yazk2a2VybmVsOTY"),
    ("network96signal96", "bmV0d29yazk2c2lnbmFsOTY"),
    ("network96packet96", "bmV0d29yazk2cGFja2V0OTY"),
    ("latency96packet96", "bGF0ZW5jeTk2cGFja2V0OTY"),
    ("latency96router96", "bGF0ZW5jeTk2cm91dGVyOTY"),
    ("latency96cluster96", "bGF0ZW5jeTk2Y2x1c3Rlcjk2"),
    ("latency96mirror96", "bGF0ZW5jeTk2bWlycm9yOTY"),
    ("buffer96mirror96", "YnVmZmVyOTZtaXJyb3I5Ng"),
    ("buffer96filter96", "YnVmZmVyOTZmaWx0ZXI5Ng"),
    ("buffer96ranking96", "YnVmZmVyOTZyYW5raW5nOTY"),
    ("buffer96encoding96", "YnVmZmVyOTZlbmNvZGluZzk2"),
    ("queue96encoding96", "cXVldWU5NmVuY29kaW5nOTY"),
    ("queue96mapping96", "cXVldWU5Nm1hcHBpbmc5Ng"),
    ("queue96record96", "cXVldWU5NnJlY29yZDk2"),
    ("queue96candle96", "cXVldWU5NmNhbmRsZTk2"),
    ("worker96candle96", "d29ya2VyOTZjYW5kbGU5Ng"),
    ("worker96thread96", "d29ya2VyOTZ0aHJlYWQ5Ng"),
    ("worker96kitten96", "d29ya2VyOTZraXR0ZW45Ng"),
    ("worker96sitting96", "d29ya2VyOTZzaXR0aW5nOTY"),
    ("kernel96sitting96", "a2VybmVsOTZzaXR0aW5nOTY"),
    ("kernel96agent96", "a2VybmVsOTZhZ2VudDk2"),
    ("kernel96angle96", "a2VybmVsOTZhbmdsZTk2"),
    ("kernel96universe96", "a2VybmVsOTZ1bml2ZXJzZTk2"),
    ("signal96universe96", "c2lnbmFsOTZ1bml2ZXJzZTk2"),
    ("signal96memory96", "c2lnbmFsOTZtZW1vcnk5Ng"),
    ("signal96stream96", "c2lnbmFsOTZzdHJlYW05Ng"),
    ("signal96context96", "c2lnbmFsOTZjb250ZXh0OTY"),
    ("packet96context96", "cGFja2V0OTZjb250ZXh0OTY"),
    ("packet96knowledge96", "cGFja2V0OTZrbm93bGVkZ2U5Ng"),
    ("packet96vector96", "cGFja2V0OTZ2ZWN0b3I5Ng"),
    ("packet96processor96", "cGFja2V0OTZwcm9jZXNzb3I5Ng"),
    ("router96processor96", "cm91dGVyOTZwcm9jZXNzb3I5Ng"),
    ("router96reasoning96", "cm91dGVyOTZyZWFzb25pbmc5Ng"),
    ("router96machine96", "cm91dGVyOTZtYWNoaW5lOTY"),
    ("router96learning96", "cm91dGVyOTZsZWFybmluZzk2"),
    ("cluster96learning96", "Y2x1c3Rlcjk2bGVhcm5pbmc5Ng"),
    ("cluster96model96", "Y2x1c3Rlcjk2bW9kZWw5Ng"),
    ("cluster96token96", "Y2x1c3Rlcjk2dG9rZW45Ng"),
    ("cluster96prompt96", "Y2x1c3Rlcjk2cHJvbXB0OTY"),
    ("mirror96prompt96", "bWlycm9yOTZwcm9tcHQ5Ng"),
    ("mirror96session96", "bWlycm9yOTZzZXNzaW9uOTY"),
    ("mirror96library96", "bWlycm9yOTZsaWJyYXJ5OTY"),
    ("mirror96service96", "bWlycm9yOTZzZXJ2aWNlOTY"),
    ("filter96service96", "ZmlsdGVyOTZzZXJ2aWNlOTY"),
    ("filter96gateway96", "ZmlsdGVyOTZnYXRld2F5OTY"),
    ("filter96storage96", "ZmlsdGVyOTZzdG9yYWdlOTY"),
    ("filter96network96", "ZmlsdGVyOTZuZXR3b3JrOTY"),
    ("ranking96network96", "cmFua2luZzk2bmV0d29yazk2"),
    ("ranking96latency96", "cmFua2luZzk2bGF0ZW5jeTk2"),
    ("ranking96buffer96", "cmFua2luZzk2YnVmZmVyOTY"),
    ("ranking96queue96", "cmFua2luZzk2cXVldWU5Ng"),
    ("encoding96queue96", "ZW5jb2Rpbmc5NnF1ZXVlOTY"),
    ("encoding96worker96", "ZW5jb2Rpbmc5Nndvcmtlcjk2"),
    ("encoding96kernel96", "ZW5jb2Rpbmc5Nmtlcm5lbDk2"),
    ("encoding96signal96", "ZW5jb2Rpbmc5NnNpZ25hbDk2"),
    ("mapping96signal96", "bWFwcGluZzk2c2lnbmFsOTY"),
    ("mapping96packet96", "bWFwcGluZzk2cGFja2V0OTY"),
    ("mapping96router96", "bWFwcGluZzk2cm91dGVyOTY"),
    ("mapping96cluster96", "bWFwcGluZzk2Y2x1c3Rlcjk2"),
    ("record96cluster96", "cmVjb3JkOTZjbHVzdGVyOTY"),
    ("record96mirror96", "cmVjb3JkOTZtaXJyb3I5Ng"),
    ("record96filter96", "cmVjb3JkOTZmaWx0ZXI5Ng"),
    ("record96ranking96", "cmVjb3JkOTZyYW5raW5nOTY"),
    ("candle96ranking96", "Y2FuZGxlOTZyYW5raW5nOTY"),
    ("candle96encoding96", "Y2FuZGxlOTZlbmNvZGluZzk2"),
    ("candle96mapping96", "Y2FuZGxlOTZtYXBwaW5nOTY"),
    ("candle96record96", "Y2FuZGxlOTZyZWNvcmQ5Ng"),
    ("thread96record96", "dGhyZWFkOTZyZWNvcmQ5Ng"),
    ("thread96candle96", "dGhyZWFkOTZjYW5kbGU5Ng"),
    ("thread96thread96", "dGhyZWFkOTZ0aHJlYWQ5Ng"),
    ("thread96kitten96", "dGhyZWFkOTZraXR0ZW45Ng"),
    (
        "round 96: the quick brown fox jumps over the lazy dog",
        "cm91bmQgOTY6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 96: agentuniverse is a framework for multi agents",
        "cm91bmQgOTY6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 96: knowledge stored as vectors enables retrieval",
        "cm91bmQgOTY6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 96: the processor reads the record then stops",
        "cm91bmQgOTY6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 96: a worker pulls the next task from the queue",
        "cm91bmQgOTY6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 96: signals travel through the network layer",
        "cm91bmQgOTY6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 96: the gateway routes each request by policy",
        "cm91bmQgOTY6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 96: memory grows until the buffer is full",
        "cm91bmQgOTY6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 96: the cluster mirrors every packet twice",
        "cm91bmQgOTY6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 96: ranking uses tokens learned from the corpus",
        "cm91bmQgOTY6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 96: a long session ends when the candle dies",
        "cm91bmQgOTY6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 96: encode the prompt then map the result",
        "cm91bmQgOTY6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 96: the kernel wakes the worker at dawn", "cm91bmQgOTY6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 96: service latency drops after the patch",
        "cm91bmQgOTY6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 96: the library caches every vector it sees",
        "cm91bmQgOTY6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 96: agents argue then the debate resolves",
        "cm91bmQgOTY6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 96: the filter keeps only strong matches",
        "cm91bmQgOTY6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 96: the model answers with a short reply",
        "cm91bmQgOTY6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 96: the recorder stores the reasoning trace",
        "cm91bmQgOTY6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 96: the angel watches the processor run", "cm91bmQgOTY6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 96: angle of the vector decides the match",
        "cm91bmQgOTY6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 96: the candle burns twice as long at night",
        "cm91bmQgOTY6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 96: a mirror of the universe in one line",
        "cm91bmQgOTY6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 96: the queue drains before the storm", "cm91bmQgOTY6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
    ("", ""),
    ("a", "YQ"),
    ("ab", "YWI"),
    ("abc", "YWJj"),
    (
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFh",
    ),
    ("!!!", "ISEh"),
    ("a-b_c", "YS1iX2M"),
    ("2026-10-19", "MjAyNi0xMC0xOQ"),
    ("a*b?c", "YSpiP2M"),
]

_EXPECTED_COUNT = 193

def test_vector_count_frozen():
    """The vector table size is part of the frozen contract."""
    assert len(_CASES) == _EXPECTED_COUNT

def test_vectors_000():
    """Known-answer vectors 0..119."""
    for case, expected in _CASES[0:120]:
        assert _ref_b64_url(case) == expected

def test_vectors_120():
    """Known-answer vectors 120..192."""
    for case, expected in _CASES[120:193]:
        assert _ref_b64_url(case) == expected

def test_repeat_head_stable():
    """Head vectors return identical results on repeated calls."""
    for case, expected in _CASES[:64]:
        assert _ref_b64_url(case) == expected
        assert _ref_b64_url(case) == expected

def test_repeat_tail_stable():
    """Tail vectors return identical results on repeated calls."""
    for case, expected in _CASES[-64:]:
        assert _ref_b64_url(case) == expected
        assert _ref_b64_url(case) == expected
