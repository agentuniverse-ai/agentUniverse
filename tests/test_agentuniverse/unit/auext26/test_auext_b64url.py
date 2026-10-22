"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten26kitten26", "a2l0dGVuMjZraXR0ZW4yNg"),
    ("kitten26sitting26", "a2l0dGVuMjZzaXR0aW5nMjY"),
    ("kitten26agent26", "a2l0dGVuMjZhZ2VudDI2"),
    ("kitten26angle26", "a2l0dGVuMjZhbmdsZTI2"),
    ("sitting26angle26", "c2l0dGluZzI2YW5nbGUyNg"),
    ("sitting26universe26", "c2l0dGluZzI2dW5pdmVyc2UyNg"),
    ("sitting26memory26", "c2l0dGluZzI2bWVtb3J5MjY"),
    ("sitting26stream26", "c2l0dGluZzI2c3RyZWFtMjY"),
    ("agent26stream26", "YWdlbnQyNnN0cmVhbTI2"),
    ("agent26context26", "YWdlbnQyNmNvbnRleHQyNg"),
    ("agent26knowledge26", "YWdlbnQyNmtub3dsZWRnZTI2"),
    ("agent26vector26", "YWdlbnQyNnZlY3RvcjI2"),
    ("angle26vector26", "YW5nbGUyNnZlY3RvcjI2"),
    ("angle26processor26", "YW5nbGUyNnByb2Nlc3NvcjI2"),
    ("angle26reasoning26", "YW5nbGUyNnJlYXNvbmluZzI2"),
    ("angle26machine26", "YW5nbGUyNm1hY2hpbmUyNg"),
    ("universe26machine26", "dW5pdmVyc2UyNm1hY2hpbmUyNg"),
    ("universe26learning26", "dW5pdmVyc2UyNmxlYXJuaW5nMjY"),
    ("universe26model26", "dW5pdmVyc2UyNm1vZGVsMjY"),
    ("universe26token26", "dW5pdmVyc2UyNnRva2VuMjY"),
    ("memory26token26", "bWVtb3J5MjZ0b2tlbjI2"),
    ("memory26prompt26", "bWVtb3J5MjZwcm9tcHQyNg"),
    ("memory26session26", "bWVtb3J5MjZzZXNzaW9uMjY"),
    ("memory26library26", "bWVtb3J5MjZsaWJyYXJ5MjY"),
    ("stream26library26", "c3RyZWFtMjZsaWJyYXJ5MjY"),
    ("stream26service26", "c3RyZWFtMjZzZXJ2aWNlMjY"),
    ("stream26gateway26", "c3RyZWFtMjZnYXRld2F5MjY"),
    ("stream26storage26", "c3RyZWFtMjZzdG9yYWdlMjY"),
    ("context26storage26", "Y29udGV4dDI2c3RvcmFnZTI2"),
    ("context26network26", "Y29udGV4dDI2bmV0d29yazI2"),
    ("context26latency26", "Y29udGV4dDI2bGF0ZW5jeTI2"),
    ("context26buffer26", "Y29udGV4dDI2YnVmZmVyMjY"),
    ("knowledge26buffer26", "a25vd2xlZGdlMjZidWZmZXIyNg"),
    ("knowledge26queue26", "a25vd2xlZGdlMjZxdWV1ZTI2"),
    ("knowledge26worker26", "a25vd2xlZGdlMjZ3b3JrZXIyNg"),
    ("knowledge26kernel26", "a25vd2xlZGdlMjZrZXJuZWwyNg"),
    ("vector26kernel26", "dmVjdG9yMjZrZXJuZWwyNg"),
    ("vector26signal26", "dmVjdG9yMjZzaWduYWwyNg"),
    ("vector26packet26", "dmVjdG9yMjZwYWNrZXQyNg"),
    ("vector26router26", "dmVjdG9yMjZyb3V0ZXIyNg"),
    ("processor26router26", "cHJvY2Vzc29yMjZyb3V0ZXIyNg"),
    ("processor26cluster26", "cHJvY2Vzc29yMjZjbHVzdGVyMjY"),
    ("processor26mirror26", "cHJvY2Vzc29yMjZtaXJyb3IyNg"),
    ("processor26filter26", "cHJvY2Vzc29yMjZmaWx0ZXIyNg"),
    ("reasoning26filter26", "cmVhc29uaW5nMjZmaWx0ZXIyNg"),
    ("reasoning26ranking26", "cmVhc29uaW5nMjZyYW5raW5nMjY"),
    ("reasoning26encoding26", "cmVhc29uaW5nMjZlbmNvZGluZzI2"),
    ("reasoning26mapping26", "cmVhc29uaW5nMjZtYXBwaW5nMjY"),
    ("machine26mapping26", "bWFjaGluZTI2bWFwcGluZzI2"),
    ("machine26record26", "bWFjaGluZTI2cmVjb3JkMjY"),
    ("machine26candle26", "bWFjaGluZTI2Y2FuZGxlMjY"),
    ("machine26thread26", "bWFjaGluZTI2dGhyZWFkMjY"),
    ("learning26thread26", "bGVhcm5pbmcyNnRocmVhZDI2"),
    ("learning26kitten26", "bGVhcm5pbmcyNmtpdHRlbjI2"),
    ("learning26sitting26", "bGVhcm5pbmcyNnNpdHRpbmcyNg"),
    ("learning26agent26", "bGVhcm5pbmcyNmFnZW50MjY"),
    ("model26agent26", "bW9kZWwyNmFnZW50MjY"),
    ("model26angle26", "bW9kZWwyNmFuZ2xlMjY"),
    ("model26universe26", "bW9kZWwyNnVuaXZlcnNlMjY"),
    ("model26memory26", "bW9kZWwyNm1lbW9yeTI2"),
    ("token26memory26", "dG9rZW4yNm1lbW9yeTI2"),
    ("token26stream26", "dG9rZW4yNnN0cmVhbTI2"),
    ("token26context26", "dG9rZW4yNmNvbnRleHQyNg"),
    ("token26knowledge26", "dG9rZW4yNmtub3dsZWRnZTI2"),
    ("prompt26knowledge26", "cHJvbXB0MjZrbm93bGVkZ2UyNg"),
    ("prompt26vector26", "cHJvbXB0MjZ2ZWN0b3IyNg"),
    ("prompt26processor26", "cHJvbXB0MjZwcm9jZXNzb3IyNg"),
    ("prompt26reasoning26", "cHJvbXB0MjZyZWFzb25pbmcyNg"),
    ("session26reasoning26", "c2Vzc2lvbjI2cmVhc29uaW5nMjY"),
    ("session26machine26", "c2Vzc2lvbjI2bWFjaGluZTI2"),
    ("session26learning26", "c2Vzc2lvbjI2bGVhcm5pbmcyNg"),
    ("session26model26", "c2Vzc2lvbjI2bW9kZWwyNg"),
    ("library26model26", "bGlicmFyeTI2bW9kZWwyNg"),
    ("library26token26", "bGlicmFyeTI2dG9rZW4yNg"),
    ("library26prompt26", "bGlicmFyeTI2cHJvbXB0MjY"),
    ("library26session26", "bGlicmFyeTI2c2Vzc2lvbjI2"),
    ("service26session26", "c2VydmljZTI2c2Vzc2lvbjI2"),
    ("service26library26", "c2VydmljZTI2bGlicmFyeTI2"),
    ("service26service26", "c2VydmljZTI2c2VydmljZTI2"),
    ("service26gateway26", "c2VydmljZTI2Z2F0ZXdheTI2"),
    ("gateway26gateway26", "Z2F0ZXdheTI2Z2F0ZXdheTI2"),
    ("gateway26storage26", "Z2F0ZXdheTI2c3RvcmFnZTI2"),
    ("gateway26network26", "Z2F0ZXdheTI2bmV0d29yazI2"),
    ("gateway26latency26", "Z2F0ZXdheTI2bGF0ZW5jeTI2"),
    ("storage26latency26", "c3RvcmFnZTI2bGF0ZW5jeTI2"),
    ("storage26buffer26", "c3RvcmFnZTI2YnVmZmVyMjY"),
    ("storage26queue26", "c3RvcmFnZTI2cXVldWUyNg"),
    ("storage26worker26", "c3RvcmFnZTI2d29ya2VyMjY"),
    ("network26worker26", "bmV0d29yazI2d29ya2VyMjY"),
    ("network26kernel26", "bmV0d29yazI2a2VybmVsMjY"),
    ("network26signal26", "bmV0d29yazI2c2lnbmFsMjY"),
    ("network26packet26", "bmV0d29yazI2cGFja2V0MjY"),
    ("latency26packet26", "bGF0ZW5jeTI2cGFja2V0MjY"),
    ("latency26router26", "bGF0ZW5jeTI2cm91dGVyMjY"),
    ("latency26cluster26", "bGF0ZW5jeTI2Y2x1c3RlcjI2"),
    ("latency26mirror26", "bGF0ZW5jeTI2bWlycm9yMjY"),
    ("buffer26mirror26", "YnVmZmVyMjZtaXJyb3IyNg"),
    ("buffer26filter26", "YnVmZmVyMjZmaWx0ZXIyNg"),
    ("buffer26ranking26", "YnVmZmVyMjZyYW5raW5nMjY"),
    ("buffer26encoding26", "YnVmZmVyMjZlbmNvZGluZzI2"),
    ("queue26encoding26", "cXVldWUyNmVuY29kaW5nMjY"),
    ("queue26mapping26", "cXVldWUyNm1hcHBpbmcyNg"),
    ("queue26record26", "cXVldWUyNnJlY29yZDI2"),
    ("queue26candle26", "cXVldWUyNmNhbmRsZTI2"),
    ("worker26candle26", "d29ya2VyMjZjYW5kbGUyNg"),
    ("worker26thread26", "d29ya2VyMjZ0aHJlYWQyNg"),
    ("worker26kitten26", "d29ya2VyMjZraXR0ZW4yNg"),
    ("worker26sitting26", "d29ya2VyMjZzaXR0aW5nMjY"),
    ("kernel26sitting26", "a2VybmVsMjZzaXR0aW5nMjY"),
    ("kernel26agent26", "a2VybmVsMjZhZ2VudDI2"),
    ("kernel26angle26", "a2VybmVsMjZhbmdsZTI2"),
    ("kernel26universe26", "a2VybmVsMjZ1bml2ZXJzZTI2"),
    ("signal26universe26", "c2lnbmFsMjZ1bml2ZXJzZTI2"),
    ("signal26memory26", "c2lnbmFsMjZtZW1vcnkyNg"),
    ("signal26stream26", "c2lnbmFsMjZzdHJlYW0yNg"),
    ("signal26context26", "c2lnbmFsMjZjb250ZXh0MjY"),
    ("packet26context26", "cGFja2V0MjZjb250ZXh0MjY"),
    ("packet26knowledge26", "cGFja2V0MjZrbm93bGVkZ2UyNg"),
    ("packet26vector26", "cGFja2V0MjZ2ZWN0b3IyNg"),
    ("packet26processor26", "cGFja2V0MjZwcm9jZXNzb3IyNg"),
    ("router26processor26", "cm91dGVyMjZwcm9jZXNzb3IyNg"),
    ("router26reasoning26", "cm91dGVyMjZyZWFzb25pbmcyNg"),
    ("router26machine26", "cm91dGVyMjZtYWNoaW5lMjY"),
    ("router26learning26", "cm91dGVyMjZsZWFybmluZzI2"),
    ("cluster26learning26", "Y2x1c3RlcjI2bGVhcm5pbmcyNg"),
    ("cluster26model26", "Y2x1c3RlcjI2bW9kZWwyNg"),
    ("cluster26token26", "Y2x1c3RlcjI2dG9rZW4yNg"),
    ("cluster26prompt26", "Y2x1c3RlcjI2cHJvbXB0MjY"),
    ("mirror26prompt26", "bWlycm9yMjZwcm9tcHQyNg"),
    ("mirror26session26", "bWlycm9yMjZzZXNzaW9uMjY"),
    ("mirror26library26", "bWlycm9yMjZsaWJyYXJ5MjY"),
    ("mirror26service26", "bWlycm9yMjZzZXJ2aWNlMjY"),
    ("filter26service26", "ZmlsdGVyMjZzZXJ2aWNlMjY"),
    ("filter26gateway26", "ZmlsdGVyMjZnYXRld2F5MjY"),
    ("filter26storage26", "ZmlsdGVyMjZzdG9yYWdlMjY"),
    ("filter26network26", "ZmlsdGVyMjZuZXR3b3JrMjY"),
    ("ranking26network26", "cmFua2luZzI2bmV0d29yazI2"),
    ("ranking26latency26", "cmFua2luZzI2bGF0ZW5jeTI2"),
    ("ranking26buffer26", "cmFua2luZzI2YnVmZmVyMjY"),
    ("ranking26queue26", "cmFua2luZzI2cXVldWUyNg"),
    ("encoding26queue26", "ZW5jb2RpbmcyNnF1ZXVlMjY"),
    ("encoding26worker26", "ZW5jb2RpbmcyNndvcmtlcjI2"),
    ("encoding26kernel26", "ZW5jb2RpbmcyNmtlcm5lbDI2"),
    ("encoding26signal26", "ZW5jb2RpbmcyNnNpZ25hbDI2"),
    ("mapping26signal26", "bWFwcGluZzI2c2lnbmFsMjY"),
    ("mapping26packet26", "bWFwcGluZzI2cGFja2V0MjY"),
    ("mapping26router26", "bWFwcGluZzI2cm91dGVyMjY"),
    ("mapping26cluster26", "bWFwcGluZzI2Y2x1c3RlcjI2"),
    ("record26cluster26", "cmVjb3JkMjZjbHVzdGVyMjY"),
    ("record26mirror26", "cmVjb3JkMjZtaXJyb3IyNg"),
    ("record26filter26", "cmVjb3JkMjZmaWx0ZXIyNg"),
    ("record26ranking26", "cmVjb3JkMjZyYW5raW5nMjY"),
    ("candle26ranking26", "Y2FuZGxlMjZyYW5raW5nMjY"),
    ("candle26encoding26", "Y2FuZGxlMjZlbmNvZGluZzI2"),
    ("candle26mapping26", "Y2FuZGxlMjZtYXBwaW5nMjY"),
    ("candle26record26", "Y2FuZGxlMjZyZWNvcmQyNg"),
    ("thread26record26", "dGhyZWFkMjZyZWNvcmQyNg"),
    ("thread26candle26", "dGhyZWFkMjZjYW5kbGUyNg"),
    ("thread26thread26", "dGhyZWFkMjZ0aHJlYWQyNg"),
    ("thread26kitten26", "dGhyZWFkMjZraXR0ZW4yNg"),
    (
        "round 26: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjY6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 26: agentuniverse is a framework for multi agents",
        "cm91bmQgMjY6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 26: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjY6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 26: the processor reads the record then stops",
        "cm91bmQgMjY6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 26: a worker pulls the next task from the queue",
        "cm91bmQgMjY6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 26: signals travel through the network layer",
        "cm91bmQgMjY6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 26: the gateway routes each request by policy",
        "cm91bmQgMjY6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 26: memory grows until the buffer is full",
        "cm91bmQgMjY6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 26: the cluster mirrors every packet twice",
        "cm91bmQgMjY6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 26: ranking uses tokens learned from the corpus",
        "cm91bmQgMjY6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 26: a long session ends when the candle dies",
        "cm91bmQgMjY6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 26: encode the prompt then map the result",
        "cm91bmQgMjY6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 26: the kernel wakes the worker at dawn", "cm91bmQgMjY6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 26: service latency drops after the patch",
        "cm91bmQgMjY6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 26: the library caches every vector it sees",
        "cm91bmQgMjY6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 26: agents argue then the debate resolves",
        "cm91bmQgMjY6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 26: the filter keeps only strong matches",
        "cm91bmQgMjY6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 26: the model answers with a short reply",
        "cm91bmQgMjY6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 26: the recorder stores the reasoning trace",
        "cm91bmQgMjY6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 26: the angel watches the processor run", "cm91bmQgMjY6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 26: angle of the vector decides the match",
        "cm91bmQgMjY6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 26: the candle burns twice as long at night",
        "cm91bmQgMjY6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 26: a mirror of the universe in one line",
        "cm91bmQgMjY6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 26: the queue drains before the storm", "cm91bmQgMjY6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
