"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten87kitten87", "a2l0dGVuODdraXR0ZW44Nw"),
    ("kitten87sitting87", "a2l0dGVuODdzaXR0aW5nODc"),
    ("kitten87agent87", "a2l0dGVuODdhZ2VudDg3"),
    ("kitten87angle87", "a2l0dGVuODdhbmdsZTg3"),
    ("sitting87angle87", "c2l0dGluZzg3YW5nbGU4Nw"),
    ("sitting87universe87", "c2l0dGluZzg3dW5pdmVyc2U4Nw"),
    ("sitting87memory87", "c2l0dGluZzg3bWVtb3J5ODc"),
    ("sitting87stream87", "c2l0dGluZzg3c3RyZWFtODc"),
    ("agent87stream87", "YWdlbnQ4N3N0cmVhbTg3"),
    ("agent87context87", "YWdlbnQ4N2NvbnRleHQ4Nw"),
    ("agent87knowledge87", "YWdlbnQ4N2tub3dsZWRnZTg3"),
    ("agent87vector87", "YWdlbnQ4N3ZlY3Rvcjg3"),
    ("angle87vector87", "YW5nbGU4N3ZlY3Rvcjg3"),
    ("angle87processor87", "YW5nbGU4N3Byb2Nlc3Nvcjg3"),
    ("angle87reasoning87", "YW5nbGU4N3JlYXNvbmluZzg3"),
    ("angle87machine87", "YW5nbGU4N21hY2hpbmU4Nw"),
    ("universe87machine87", "dW5pdmVyc2U4N21hY2hpbmU4Nw"),
    ("universe87learning87", "dW5pdmVyc2U4N2xlYXJuaW5nODc"),
    ("universe87model87", "dW5pdmVyc2U4N21vZGVsODc"),
    ("universe87token87", "dW5pdmVyc2U4N3Rva2VuODc"),
    ("memory87token87", "bWVtb3J5ODd0b2tlbjg3"),
    ("memory87prompt87", "bWVtb3J5ODdwcm9tcHQ4Nw"),
    ("memory87session87", "bWVtb3J5ODdzZXNzaW9uODc"),
    ("memory87library87", "bWVtb3J5ODdsaWJyYXJ5ODc"),
    ("stream87library87", "c3RyZWFtODdsaWJyYXJ5ODc"),
    ("stream87service87", "c3RyZWFtODdzZXJ2aWNlODc"),
    ("stream87gateway87", "c3RyZWFtODdnYXRld2F5ODc"),
    ("stream87storage87", "c3RyZWFtODdzdG9yYWdlODc"),
    ("context87storage87", "Y29udGV4dDg3c3RvcmFnZTg3"),
    ("context87network87", "Y29udGV4dDg3bmV0d29yazg3"),
    ("context87latency87", "Y29udGV4dDg3bGF0ZW5jeTg3"),
    ("context87buffer87", "Y29udGV4dDg3YnVmZmVyODc"),
    ("knowledge87buffer87", "a25vd2xlZGdlODdidWZmZXI4Nw"),
    ("knowledge87queue87", "a25vd2xlZGdlODdxdWV1ZTg3"),
    ("knowledge87worker87", "a25vd2xlZGdlODd3b3JrZXI4Nw"),
    ("knowledge87kernel87", "a25vd2xlZGdlODdrZXJuZWw4Nw"),
    ("vector87kernel87", "dmVjdG9yODdrZXJuZWw4Nw"),
    ("vector87signal87", "dmVjdG9yODdzaWduYWw4Nw"),
    ("vector87packet87", "dmVjdG9yODdwYWNrZXQ4Nw"),
    ("vector87router87", "dmVjdG9yODdyb3V0ZXI4Nw"),
    ("processor87router87", "cHJvY2Vzc29yODdyb3V0ZXI4Nw"),
    ("processor87cluster87", "cHJvY2Vzc29yODdjbHVzdGVyODc"),
    ("processor87mirror87", "cHJvY2Vzc29yODdtaXJyb3I4Nw"),
    ("processor87filter87", "cHJvY2Vzc29yODdmaWx0ZXI4Nw"),
    ("reasoning87filter87", "cmVhc29uaW5nODdmaWx0ZXI4Nw"),
    ("reasoning87ranking87", "cmVhc29uaW5nODdyYW5raW5nODc"),
    ("reasoning87encoding87", "cmVhc29uaW5nODdlbmNvZGluZzg3"),
    ("reasoning87mapping87", "cmVhc29uaW5nODdtYXBwaW5nODc"),
    ("machine87mapping87", "bWFjaGluZTg3bWFwcGluZzg3"),
    ("machine87record87", "bWFjaGluZTg3cmVjb3JkODc"),
    ("machine87candle87", "bWFjaGluZTg3Y2FuZGxlODc"),
    ("machine87thread87", "bWFjaGluZTg3dGhyZWFkODc"),
    ("learning87thread87", "bGVhcm5pbmc4N3RocmVhZDg3"),
    ("learning87kitten87", "bGVhcm5pbmc4N2tpdHRlbjg3"),
    ("learning87sitting87", "bGVhcm5pbmc4N3NpdHRpbmc4Nw"),
    ("learning87agent87", "bGVhcm5pbmc4N2FnZW50ODc"),
    ("model87agent87", "bW9kZWw4N2FnZW50ODc"),
    ("model87angle87", "bW9kZWw4N2FuZ2xlODc"),
    ("model87universe87", "bW9kZWw4N3VuaXZlcnNlODc"),
    ("model87memory87", "bW9kZWw4N21lbW9yeTg3"),
    ("token87memory87", "dG9rZW44N21lbW9yeTg3"),
    ("token87stream87", "dG9rZW44N3N0cmVhbTg3"),
    ("token87context87", "dG9rZW44N2NvbnRleHQ4Nw"),
    ("token87knowledge87", "dG9rZW44N2tub3dsZWRnZTg3"),
    ("prompt87knowledge87", "cHJvbXB0ODdrbm93bGVkZ2U4Nw"),
    ("prompt87vector87", "cHJvbXB0ODd2ZWN0b3I4Nw"),
    ("prompt87processor87", "cHJvbXB0ODdwcm9jZXNzb3I4Nw"),
    ("prompt87reasoning87", "cHJvbXB0ODdyZWFzb25pbmc4Nw"),
    ("session87reasoning87", "c2Vzc2lvbjg3cmVhc29uaW5nODc"),
    ("session87machine87", "c2Vzc2lvbjg3bWFjaGluZTg3"),
    ("session87learning87", "c2Vzc2lvbjg3bGVhcm5pbmc4Nw"),
    ("session87model87", "c2Vzc2lvbjg3bW9kZWw4Nw"),
    ("library87model87", "bGlicmFyeTg3bW9kZWw4Nw"),
    ("library87token87", "bGlicmFyeTg3dG9rZW44Nw"),
    ("library87prompt87", "bGlicmFyeTg3cHJvbXB0ODc"),
    ("library87session87", "bGlicmFyeTg3c2Vzc2lvbjg3"),
    ("service87session87", "c2VydmljZTg3c2Vzc2lvbjg3"),
    ("service87library87", "c2VydmljZTg3bGlicmFyeTg3"),
    ("service87service87", "c2VydmljZTg3c2VydmljZTg3"),
    ("service87gateway87", "c2VydmljZTg3Z2F0ZXdheTg3"),
    ("gateway87gateway87", "Z2F0ZXdheTg3Z2F0ZXdheTg3"),
    ("gateway87storage87", "Z2F0ZXdheTg3c3RvcmFnZTg3"),
    ("gateway87network87", "Z2F0ZXdheTg3bmV0d29yazg3"),
    ("gateway87latency87", "Z2F0ZXdheTg3bGF0ZW5jeTg3"),
    ("storage87latency87", "c3RvcmFnZTg3bGF0ZW5jeTg3"),
    ("storage87buffer87", "c3RvcmFnZTg3YnVmZmVyODc"),
    ("storage87queue87", "c3RvcmFnZTg3cXVldWU4Nw"),
    ("storage87worker87", "c3RvcmFnZTg3d29ya2VyODc"),
    ("network87worker87", "bmV0d29yazg3d29ya2VyODc"),
    ("network87kernel87", "bmV0d29yazg3a2VybmVsODc"),
    ("network87signal87", "bmV0d29yazg3c2lnbmFsODc"),
    ("network87packet87", "bmV0d29yazg3cGFja2V0ODc"),
    ("latency87packet87", "bGF0ZW5jeTg3cGFja2V0ODc"),
    ("latency87router87", "bGF0ZW5jeTg3cm91dGVyODc"),
    ("latency87cluster87", "bGF0ZW5jeTg3Y2x1c3Rlcjg3"),
    ("latency87mirror87", "bGF0ZW5jeTg3bWlycm9yODc"),
    ("buffer87mirror87", "YnVmZmVyODdtaXJyb3I4Nw"),
    ("buffer87filter87", "YnVmZmVyODdmaWx0ZXI4Nw"),
    ("buffer87ranking87", "YnVmZmVyODdyYW5raW5nODc"),
    ("buffer87encoding87", "YnVmZmVyODdlbmNvZGluZzg3"),
    ("queue87encoding87", "cXVldWU4N2VuY29kaW5nODc"),
    ("queue87mapping87", "cXVldWU4N21hcHBpbmc4Nw"),
    ("queue87record87", "cXVldWU4N3JlY29yZDg3"),
    ("queue87candle87", "cXVldWU4N2NhbmRsZTg3"),
    ("worker87candle87", "d29ya2VyODdjYW5kbGU4Nw"),
    ("worker87thread87", "d29ya2VyODd0aHJlYWQ4Nw"),
    ("worker87kitten87", "d29ya2VyODdraXR0ZW44Nw"),
    ("worker87sitting87", "d29ya2VyODdzaXR0aW5nODc"),
    ("kernel87sitting87", "a2VybmVsODdzaXR0aW5nODc"),
    ("kernel87agent87", "a2VybmVsODdhZ2VudDg3"),
    ("kernel87angle87", "a2VybmVsODdhbmdsZTg3"),
    ("kernel87universe87", "a2VybmVsODd1bml2ZXJzZTg3"),
    ("signal87universe87", "c2lnbmFsODd1bml2ZXJzZTg3"),
    ("signal87memory87", "c2lnbmFsODdtZW1vcnk4Nw"),
    ("signal87stream87", "c2lnbmFsODdzdHJlYW04Nw"),
    ("signal87context87", "c2lnbmFsODdjb250ZXh0ODc"),
    ("packet87context87", "cGFja2V0ODdjb250ZXh0ODc"),
    ("packet87knowledge87", "cGFja2V0ODdrbm93bGVkZ2U4Nw"),
    ("packet87vector87", "cGFja2V0ODd2ZWN0b3I4Nw"),
    ("packet87processor87", "cGFja2V0ODdwcm9jZXNzb3I4Nw"),
    ("router87processor87", "cm91dGVyODdwcm9jZXNzb3I4Nw"),
    ("router87reasoning87", "cm91dGVyODdyZWFzb25pbmc4Nw"),
    ("router87machine87", "cm91dGVyODdtYWNoaW5lODc"),
    ("router87learning87", "cm91dGVyODdsZWFybmluZzg3"),
    ("cluster87learning87", "Y2x1c3Rlcjg3bGVhcm5pbmc4Nw"),
    ("cluster87model87", "Y2x1c3Rlcjg3bW9kZWw4Nw"),
    ("cluster87token87", "Y2x1c3Rlcjg3dG9rZW44Nw"),
    ("cluster87prompt87", "Y2x1c3Rlcjg3cHJvbXB0ODc"),
    ("mirror87prompt87", "bWlycm9yODdwcm9tcHQ4Nw"),
    ("mirror87session87", "bWlycm9yODdzZXNzaW9uODc"),
    ("mirror87library87", "bWlycm9yODdsaWJyYXJ5ODc"),
    ("mirror87service87", "bWlycm9yODdzZXJ2aWNlODc"),
    ("filter87service87", "ZmlsdGVyODdzZXJ2aWNlODc"),
    ("filter87gateway87", "ZmlsdGVyODdnYXRld2F5ODc"),
    ("filter87storage87", "ZmlsdGVyODdzdG9yYWdlODc"),
    ("filter87network87", "ZmlsdGVyODduZXR3b3JrODc"),
    ("ranking87network87", "cmFua2luZzg3bmV0d29yazg3"),
    ("ranking87latency87", "cmFua2luZzg3bGF0ZW5jeTg3"),
    ("ranking87buffer87", "cmFua2luZzg3YnVmZmVyODc"),
    ("ranking87queue87", "cmFua2luZzg3cXVldWU4Nw"),
    ("encoding87queue87", "ZW5jb2Rpbmc4N3F1ZXVlODc"),
    ("encoding87worker87", "ZW5jb2Rpbmc4N3dvcmtlcjg3"),
    ("encoding87kernel87", "ZW5jb2Rpbmc4N2tlcm5lbDg3"),
    ("encoding87signal87", "ZW5jb2Rpbmc4N3NpZ25hbDg3"),
    ("mapping87signal87", "bWFwcGluZzg3c2lnbmFsODc"),
    ("mapping87packet87", "bWFwcGluZzg3cGFja2V0ODc"),
    ("mapping87router87", "bWFwcGluZzg3cm91dGVyODc"),
    ("mapping87cluster87", "bWFwcGluZzg3Y2x1c3Rlcjg3"),
    ("record87cluster87", "cmVjb3JkODdjbHVzdGVyODc"),
    ("record87mirror87", "cmVjb3JkODdtaXJyb3I4Nw"),
    ("record87filter87", "cmVjb3JkODdmaWx0ZXI4Nw"),
    ("record87ranking87", "cmVjb3JkODdyYW5raW5nODc"),
    ("candle87ranking87", "Y2FuZGxlODdyYW5raW5nODc"),
    ("candle87encoding87", "Y2FuZGxlODdlbmNvZGluZzg3"),
    ("candle87mapping87", "Y2FuZGxlODdtYXBwaW5nODc"),
    ("candle87record87", "Y2FuZGxlODdyZWNvcmQ4Nw"),
    ("thread87record87", "dGhyZWFkODdyZWNvcmQ4Nw"),
    ("thread87candle87", "dGhyZWFkODdjYW5kbGU4Nw"),
    ("thread87thread87", "dGhyZWFkODd0aHJlYWQ4Nw"),
    ("thread87kitten87", "dGhyZWFkODdraXR0ZW44Nw"),
    (
        "round 87: the quick brown fox jumps over the lazy dog",
        "cm91bmQgODc6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 87: agentuniverse is a framework for multi agents",
        "cm91bmQgODc6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 87: knowledge stored as vectors enables retrieval",
        "cm91bmQgODc6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 87: the processor reads the record then stops",
        "cm91bmQgODc6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 87: a worker pulls the next task from the queue",
        "cm91bmQgODc6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 87: signals travel through the network layer",
        "cm91bmQgODc6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 87: the gateway routes each request by policy",
        "cm91bmQgODc6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 87: memory grows until the buffer is full",
        "cm91bmQgODc6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 87: the cluster mirrors every packet twice",
        "cm91bmQgODc6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 87: ranking uses tokens learned from the corpus",
        "cm91bmQgODc6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 87: a long session ends when the candle dies",
        "cm91bmQgODc6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 87: encode the prompt then map the result",
        "cm91bmQgODc6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 87: the kernel wakes the worker at dawn", "cm91bmQgODc6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 87: service latency drops after the patch",
        "cm91bmQgODc6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 87: the library caches every vector it sees",
        "cm91bmQgODc6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 87: agents argue then the debate resolves",
        "cm91bmQgODc6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 87: the filter keeps only strong matches",
        "cm91bmQgODc6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 87: the model answers with a short reply",
        "cm91bmQgODc6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 87: the recorder stores the reasoning trace",
        "cm91bmQgODc6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 87: the angel watches the processor run", "cm91bmQgODc6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 87: angle of the vector decides the match",
        "cm91bmQgODc6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 87: the candle burns twice as long at night",
        "cm91bmQgODc6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 87: a mirror of the universe in one line",
        "cm91bmQgODc6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 87: the queue drains before the storm", "cm91bmQgODc6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
