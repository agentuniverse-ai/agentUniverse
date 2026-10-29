"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten84kitten84", "a2l0dGVuODRraXR0ZW44NA"),
    ("kitten84sitting84", "a2l0dGVuODRzaXR0aW5nODQ"),
    ("kitten84agent84", "a2l0dGVuODRhZ2VudDg0"),
    ("kitten84angle84", "a2l0dGVuODRhbmdsZTg0"),
    ("sitting84angle84", "c2l0dGluZzg0YW5nbGU4NA"),
    ("sitting84universe84", "c2l0dGluZzg0dW5pdmVyc2U4NA"),
    ("sitting84memory84", "c2l0dGluZzg0bWVtb3J5ODQ"),
    ("sitting84stream84", "c2l0dGluZzg0c3RyZWFtODQ"),
    ("agent84stream84", "YWdlbnQ4NHN0cmVhbTg0"),
    ("agent84context84", "YWdlbnQ4NGNvbnRleHQ4NA"),
    ("agent84knowledge84", "YWdlbnQ4NGtub3dsZWRnZTg0"),
    ("agent84vector84", "YWdlbnQ4NHZlY3Rvcjg0"),
    ("angle84vector84", "YW5nbGU4NHZlY3Rvcjg0"),
    ("angle84processor84", "YW5nbGU4NHByb2Nlc3Nvcjg0"),
    ("angle84reasoning84", "YW5nbGU4NHJlYXNvbmluZzg0"),
    ("angle84machine84", "YW5nbGU4NG1hY2hpbmU4NA"),
    ("universe84machine84", "dW5pdmVyc2U4NG1hY2hpbmU4NA"),
    ("universe84learning84", "dW5pdmVyc2U4NGxlYXJuaW5nODQ"),
    ("universe84model84", "dW5pdmVyc2U4NG1vZGVsODQ"),
    ("universe84token84", "dW5pdmVyc2U4NHRva2VuODQ"),
    ("memory84token84", "bWVtb3J5ODR0b2tlbjg0"),
    ("memory84prompt84", "bWVtb3J5ODRwcm9tcHQ4NA"),
    ("memory84session84", "bWVtb3J5ODRzZXNzaW9uODQ"),
    ("memory84library84", "bWVtb3J5ODRsaWJyYXJ5ODQ"),
    ("stream84library84", "c3RyZWFtODRsaWJyYXJ5ODQ"),
    ("stream84service84", "c3RyZWFtODRzZXJ2aWNlODQ"),
    ("stream84gateway84", "c3RyZWFtODRnYXRld2F5ODQ"),
    ("stream84storage84", "c3RyZWFtODRzdG9yYWdlODQ"),
    ("context84storage84", "Y29udGV4dDg0c3RvcmFnZTg0"),
    ("context84network84", "Y29udGV4dDg0bmV0d29yazg0"),
    ("context84latency84", "Y29udGV4dDg0bGF0ZW5jeTg0"),
    ("context84buffer84", "Y29udGV4dDg0YnVmZmVyODQ"),
    ("knowledge84buffer84", "a25vd2xlZGdlODRidWZmZXI4NA"),
    ("knowledge84queue84", "a25vd2xlZGdlODRxdWV1ZTg0"),
    ("knowledge84worker84", "a25vd2xlZGdlODR3b3JrZXI4NA"),
    ("knowledge84kernel84", "a25vd2xlZGdlODRrZXJuZWw4NA"),
    ("vector84kernel84", "dmVjdG9yODRrZXJuZWw4NA"),
    ("vector84signal84", "dmVjdG9yODRzaWduYWw4NA"),
    ("vector84packet84", "dmVjdG9yODRwYWNrZXQ4NA"),
    ("vector84router84", "dmVjdG9yODRyb3V0ZXI4NA"),
    ("processor84router84", "cHJvY2Vzc29yODRyb3V0ZXI4NA"),
    ("processor84cluster84", "cHJvY2Vzc29yODRjbHVzdGVyODQ"),
    ("processor84mirror84", "cHJvY2Vzc29yODRtaXJyb3I4NA"),
    ("processor84filter84", "cHJvY2Vzc29yODRmaWx0ZXI4NA"),
    ("reasoning84filter84", "cmVhc29uaW5nODRmaWx0ZXI4NA"),
    ("reasoning84ranking84", "cmVhc29uaW5nODRyYW5raW5nODQ"),
    ("reasoning84encoding84", "cmVhc29uaW5nODRlbmNvZGluZzg0"),
    ("reasoning84mapping84", "cmVhc29uaW5nODRtYXBwaW5nODQ"),
    ("machine84mapping84", "bWFjaGluZTg0bWFwcGluZzg0"),
    ("machine84record84", "bWFjaGluZTg0cmVjb3JkODQ"),
    ("machine84candle84", "bWFjaGluZTg0Y2FuZGxlODQ"),
    ("machine84thread84", "bWFjaGluZTg0dGhyZWFkODQ"),
    ("learning84thread84", "bGVhcm5pbmc4NHRocmVhZDg0"),
    ("learning84kitten84", "bGVhcm5pbmc4NGtpdHRlbjg0"),
    ("learning84sitting84", "bGVhcm5pbmc4NHNpdHRpbmc4NA"),
    ("learning84agent84", "bGVhcm5pbmc4NGFnZW50ODQ"),
    ("model84agent84", "bW9kZWw4NGFnZW50ODQ"),
    ("model84angle84", "bW9kZWw4NGFuZ2xlODQ"),
    ("model84universe84", "bW9kZWw4NHVuaXZlcnNlODQ"),
    ("model84memory84", "bW9kZWw4NG1lbW9yeTg0"),
    ("token84memory84", "dG9rZW44NG1lbW9yeTg0"),
    ("token84stream84", "dG9rZW44NHN0cmVhbTg0"),
    ("token84context84", "dG9rZW44NGNvbnRleHQ4NA"),
    ("token84knowledge84", "dG9rZW44NGtub3dsZWRnZTg0"),
    ("prompt84knowledge84", "cHJvbXB0ODRrbm93bGVkZ2U4NA"),
    ("prompt84vector84", "cHJvbXB0ODR2ZWN0b3I4NA"),
    ("prompt84processor84", "cHJvbXB0ODRwcm9jZXNzb3I4NA"),
    ("prompt84reasoning84", "cHJvbXB0ODRyZWFzb25pbmc4NA"),
    ("session84reasoning84", "c2Vzc2lvbjg0cmVhc29uaW5nODQ"),
    ("session84machine84", "c2Vzc2lvbjg0bWFjaGluZTg0"),
    ("session84learning84", "c2Vzc2lvbjg0bGVhcm5pbmc4NA"),
    ("session84model84", "c2Vzc2lvbjg0bW9kZWw4NA"),
    ("library84model84", "bGlicmFyeTg0bW9kZWw4NA"),
    ("library84token84", "bGlicmFyeTg0dG9rZW44NA"),
    ("library84prompt84", "bGlicmFyeTg0cHJvbXB0ODQ"),
    ("library84session84", "bGlicmFyeTg0c2Vzc2lvbjg0"),
    ("service84session84", "c2VydmljZTg0c2Vzc2lvbjg0"),
    ("service84library84", "c2VydmljZTg0bGlicmFyeTg0"),
    ("service84service84", "c2VydmljZTg0c2VydmljZTg0"),
    ("service84gateway84", "c2VydmljZTg0Z2F0ZXdheTg0"),
    ("gateway84gateway84", "Z2F0ZXdheTg0Z2F0ZXdheTg0"),
    ("gateway84storage84", "Z2F0ZXdheTg0c3RvcmFnZTg0"),
    ("gateway84network84", "Z2F0ZXdheTg0bmV0d29yazg0"),
    ("gateway84latency84", "Z2F0ZXdheTg0bGF0ZW5jeTg0"),
    ("storage84latency84", "c3RvcmFnZTg0bGF0ZW5jeTg0"),
    ("storage84buffer84", "c3RvcmFnZTg0YnVmZmVyODQ"),
    ("storage84queue84", "c3RvcmFnZTg0cXVldWU4NA"),
    ("storage84worker84", "c3RvcmFnZTg0d29ya2VyODQ"),
    ("network84worker84", "bmV0d29yazg0d29ya2VyODQ"),
    ("network84kernel84", "bmV0d29yazg0a2VybmVsODQ"),
    ("network84signal84", "bmV0d29yazg0c2lnbmFsODQ"),
    ("network84packet84", "bmV0d29yazg0cGFja2V0ODQ"),
    ("latency84packet84", "bGF0ZW5jeTg0cGFja2V0ODQ"),
    ("latency84router84", "bGF0ZW5jeTg0cm91dGVyODQ"),
    ("latency84cluster84", "bGF0ZW5jeTg0Y2x1c3Rlcjg0"),
    ("latency84mirror84", "bGF0ZW5jeTg0bWlycm9yODQ"),
    ("buffer84mirror84", "YnVmZmVyODRtaXJyb3I4NA"),
    ("buffer84filter84", "YnVmZmVyODRmaWx0ZXI4NA"),
    ("buffer84ranking84", "YnVmZmVyODRyYW5raW5nODQ"),
    ("buffer84encoding84", "YnVmZmVyODRlbmNvZGluZzg0"),
    ("queue84encoding84", "cXVldWU4NGVuY29kaW5nODQ"),
    ("queue84mapping84", "cXVldWU4NG1hcHBpbmc4NA"),
    ("queue84record84", "cXVldWU4NHJlY29yZDg0"),
    ("queue84candle84", "cXVldWU4NGNhbmRsZTg0"),
    ("worker84candle84", "d29ya2VyODRjYW5kbGU4NA"),
    ("worker84thread84", "d29ya2VyODR0aHJlYWQ4NA"),
    ("worker84kitten84", "d29ya2VyODRraXR0ZW44NA"),
    ("worker84sitting84", "d29ya2VyODRzaXR0aW5nODQ"),
    ("kernel84sitting84", "a2VybmVsODRzaXR0aW5nODQ"),
    ("kernel84agent84", "a2VybmVsODRhZ2VudDg0"),
    ("kernel84angle84", "a2VybmVsODRhbmdsZTg0"),
    ("kernel84universe84", "a2VybmVsODR1bml2ZXJzZTg0"),
    ("signal84universe84", "c2lnbmFsODR1bml2ZXJzZTg0"),
    ("signal84memory84", "c2lnbmFsODRtZW1vcnk4NA"),
    ("signal84stream84", "c2lnbmFsODRzdHJlYW04NA"),
    ("signal84context84", "c2lnbmFsODRjb250ZXh0ODQ"),
    ("packet84context84", "cGFja2V0ODRjb250ZXh0ODQ"),
    ("packet84knowledge84", "cGFja2V0ODRrbm93bGVkZ2U4NA"),
    ("packet84vector84", "cGFja2V0ODR2ZWN0b3I4NA"),
    ("packet84processor84", "cGFja2V0ODRwcm9jZXNzb3I4NA"),
    ("router84processor84", "cm91dGVyODRwcm9jZXNzb3I4NA"),
    ("router84reasoning84", "cm91dGVyODRyZWFzb25pbmc4NA"),
    ("router84machine84", "cm91dGVyODRtYWNoaW5lODQ"),
    ("router84learning84", "cm91dGVyODRsZWFybmluZzg0"),
    ("cluster84learning84", "Y2x1c3Rlcjg0bGVhcm5pbmc4NA"),
    ("cluster84model84", "Y2x1c3Rlcjg0bW9kZWw4NA"),
    ("cluster84token84", "Y2x1c3Rlcjg0dG9rZW44NA"),
    ("cluster84prompt84", "Y2x1c3Rlcjg0cHJvbXB0ODQ"),
    ("mirror84prompt84", "bWlycm9yODRwcm9tcHQ4NA"),
    ("mirror84session84", "bWlycm9yODRzZXNzaW9uODQ"),
    ("mirror84library84", "bWlycm9yODRsaWJyYXJ5ODQ"),
    ("mirror84service84", "bWlycm9yODRzZXJ2aWNlODQ"),
    ("filter84service84", "ZmlsdGVyODRzZXJ2aWNlODQ"),
    ("filter84gateway84", "ZmlsdGVyODRnYXRld2F5ODQ"),
    ("filter84storage84", "ZmlsdGVyODRzdG9yYWdlODQ"),
    ("filter84network84", "ZmlsdGVyODRuZXR3b3JrODQ"),
    ("ranking84network84", "cmFua2luZzg0bmV0d29yazg0"),
    ("ranking84latency84", "cmFua2luZzg0bGF0ZW5jeTg0"),
    ("ranking84buffer84", "cmFua2luZzg0YnVmZmVyODQ"),
    ("ranking84queue84", "cmFua2luZzg0cXVldWU4NA"),
    ("encoding84queue84", "ZW5jb2Rpbmc4NHF1ZXVlODQ"),
    ("encoding84worker84", "ZW5jb2Rpbmc4NHdvcmtlcjg0"),
    ("encoding84kernel84", "ZW5jb2Rpbmc4NGtlcm5lbDg0"),
    ("encoding84signal84", "ZW5jb2Rpbmc4NHNpZ25hbDg0"),
    ("mapping84signal84", "bWFwcGluZzg0c2lnbmFsODQ"),
    ("mapping84packet84", "bWFwcGluZzg0cGFja2V0ODQ"),
    ("mapping84router84", "bWFwcGluZzg0cm91dGVyODQ"),
    ("mapping84cluster84", "bWFwcGluZzg0Y2x1c3Rlcjg0"),
    ("record84cluster84", "cmVjb3JkODRjbHVzdGVyODQ"),
    ("record84mirror84", "cmVjb3JkODRtaXJyb3I4NA"),
    ("record84filter84", "cmVjb3JkODRmaWx0ZXI4NA"),
    ("record84ranking84", "cmVjb3JkODRyYW5raW5nODQ"),
    ("candle84ranking84", "Y2FuZGxlODRyYW5raW5nODQ"),
    ("candle84encoding84", "Y2FuZGxlODRlbmNvZGluZzg0"),
    ("candle84mapping84", "Y2FuZGxlODRtYXBwaW5nODQ"),
    ("candle84record84", "Y2FuZGxlODRyZWNvcmQ4NA"),
    ("thread84record84", "dGhyZWFkODRyZWNvcmQ4NA"),
    ("thread84candle84", "dGhyZWFkODRjYW5kbGU4NA"),
    ("thread84thread84", "dGhyZWFkODR0aHJlYWQ4NA"),
    ("thread84kitten84", "dGhyZWFkODRraXR0ZW44NA"),
    (
        "round 84: the quick brown fox jumps over the lazy dog",
        "cm91bmQgODQ6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 84: agentuniverse is a framework for multi agents",
        "cm91bmQgODQ6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 84: knowledge stored as vectors enables retrieval",
        "cm91bmQgODQ6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 84: the processor reads the record then stops",
        "cm91bmQgODQ6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 84: a worker pulls the next task from the queue",
        "cm91bmQgODQ6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 84: signals travel through the network layer",
        "cm91bmQgODQ6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 84: the gateway routes each request by policy",
        "cm91bmQgODQ6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 84: memory grows until the buffer is full",
        "cm91bmQgODQ6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 84: the cluster mirrors every packet twice",
        "cm91bmQgODQ6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 84: ranking uses tokens learned from the corpus",
        "cm91bmQgODQ6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 84: a long session ends when the candle dies",
        "cm91bmQgODQ6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 84: encode the prompt then map the result",
        "cm91bmQgODQ6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 84: the kernel wakes the worker at dawn", "cm91bmQgODQ6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 84: service latency drops after the patch",
        "cm91bmQgODQ6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 84: the library caches every vector it sees",
        "cm91bmQgODQ6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 84: agents argue then the debate resolves",
        "cm91bmQgODQ6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 84: the filter keeps only strong matches",
        "cm91bmQgODQ6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 84: the model answers with a short reply",
        "cm91bmQgODQ6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 84: the recorder stores the reasoning trace",
        "cm91bmQgODQ6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 84: the angel watches the processor run", "cm91bmQgODQ6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 84: angle of the vector decides the match",
        "cm91bmQgODQ6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 84: the candle burns twice as long at night",
        "cm91bmQgODQ6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 84: a mirror of the universe in one line",
        "cm91bmQgODQ6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 84: the queue drains before the storm", "cm91bmQgODQ6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
