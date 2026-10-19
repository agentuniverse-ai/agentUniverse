"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten61kitten61", "a2l0dGVuNjFraXR0ZW42MQ"),
    ("kitten61sitting61", "a2l0dGVuNjFzaXR0aW5nNjE"),
    ("kitten61agent61", "a2l0dGVuNjFhZ2VudDYx"),
    ("kitten61angle61", "a2l0dGVuNjFhbmdsZTYx"),
    ("sitting61angle61", "c2l0dGluZzYxYW5nbGU2MQ"),
    ("sitting61universe61", "c2l0dGluZzYxdW5pdmVyc2U2MQ"),
    ("sitting61memory61", "c2l0dGluZzYxbWVtb3J5NjE"),
    ("sitting61stream61", "c2l0dGluZzYxc3RyZWFtNjE"),
    ("agent61stream61", "YWdlbnQ2MXN0cmVhbTYx"),
    ("agent61context61", "YWdlbnQ2MWNvbnRleHQ2MQ"),
    ("agent61knowledge61", "YWdlbnQ2MWtub3dsZWRnZTYx"),
    ("agent61vector61", "YWdlbnQ2MXZlY3RvcjYx"),
    ("angle61vector61", "YW5nbGU2MXZlY3RvcjYx"),
    ("angle61processor61", "YW5nbGU2MXByb2Nlc3NvcjYx"),
    ("angle61reasoning61", "YW5nbGU2MXJlYXNvbmluZzYx"),
    ("angle61machine61", "YW5nbGU2MW1hY2hpbmU2MQ"),
    ("universe61machine61", "dW5pdmVyc2U2MW1hY2hpbmU2MQ"),
    ("universe61learning61", "dW5pdmVyc2U2MWxlYXJuaW5nNjE"),
    ("universe61model61", "dW5pdmVyc2U2MW1vZGVsNjE"),
    ("universe61token61", "dW5pdmVyc2U2MXRva2VuNjE"),
    ("memory61token61", "bWVtb3J5NjF0b2tlbjYx"),
    ("memory61prompt61", "bWVtb3J5NjFwcm9tcHQ2MQ"),
    ("memory61session61", "bWVtb3J5NjFzZXNzaW9uNjE"),
    ("memory61library61", "bWVtb3J5NjFsaWJyYXJ5NjE"),
    ("stream61library61", "c3RyZWFtNjFsaWJyYXJ5NjE"),
    ("stream61service61", "c3RyZWFtNjFzZXJ2aWNlNjE"),
    ("stream61gateway61", "c3RyZWFtNjFnYXRld2F5NjE"),
    ("stream61storage61", "c3RyZWFtNjFzdG9yYWdlNjE"),
    ("context61storage61", "Y29udGV4dDYxc3RvcmFnZTYx"),
    ("context61network61", "Y29udGV4dDYxbmV0d29yazYx"),
    ("context61latency61", "Y29udGV4dDYxbGF0ZW5jeTYx"),
    ("context61buffer61", "Y29udGV4dDYxYnVmZmVyNjE"),
    ("knowledge61buffer61", "a25vd2xlZGdlNjFidWZmZXI2MQ"),
    ("knowledge61queue61", "a25vd2xlZGdlNjFxdWV1ZTYx"),
    ("knowledge61worker61", "a25vd2xlZGdlNjF3b3JrZXI2MQ"),
    ("knowledge61kernel61", "a25vd2xlZGdlNjFrZXJuZWw2MQ"),
    ("vector61kernel61", "dmVjdG9yNjFrZXJuZWw2MQ"),
    ("vector61signal61", "dmVjdG9yNjFzaWduYWw2MQ"),
    ("vector61packet61", "dmVjdG9yNjFwYWNrZXQ2MQ"),
    ("vector61router61", "dmVjdG9yNjFyb3V0ZXI2MQ"),
    ("processor61router61", "cHJvY2Vzc29yNjFyb3V0ZXI2MQ"),
    ("processor61cluster61", "cHJvY2Vzc29yNjFjbHVzdGVyNjE"),
    ("processor61mirror61", "cHJvY2Vzc29yNjFtaXJyb3I2MQ"),
    ("processor61filter61", "cHJvY2Vzc29yNjFmaWx0ZXI2MQ"),
    ("reasoning61filter61", "cmVhc29uaW5nNjFmaWx0ZXI2MQ"),
    ("reasoning61ranking61", "cmVhc29uaW5nNjFyYW5raW5nNjE"),
    ("reasoning61encoding61", "cmVhc29uaW5nNjFlbmNvZGluZzYx"),
    ("reasoning61mapping61", "cmVhc29uaW5nNjFtYXBwaW5nNjE"),
    ("machine61mapping61", "bWFjaGluZTYxbWFwcGluZzYx"),
    ("machine61record61", "bWFjaGluZTYxcmVjb3JkNjE"),
    ("machine61candle61", "bWFjaGluZTYxY2FuZGxlNjE"),
    ("machine61thread61", "bWFjaGluZTYxdGhyZWFkNjE"),
    ("learning61thread61", "bGVhcm5pbmc2MXRocmVhZDYx"),
    ("learning61kitten61", "bGVhcm5pbmc2MWtpdHRlbjYx"),
    ("learning61sitting61", "bGVhcm5pbmc2MXNpdHRpbmc2MQ"),
    ("learning61agent61", "bGVhcm5pbmc2MWFnZW50NjE"),
    ("model61agent61", "bW9kZWw2MWFnZW50NjE"),
    ("model61angle61", "bW9kZWw2MWFuZ2xlNjE"),
    ("model61universe61", "bW9kZWw2MXVuaXZlcnNlNjE"),
    ("model61memory61", "bW9kZWw2MW1lbW9yeTYx"),
    ("token61memory61", "dG9rZW42MW1lbW9yeTYx"),
    ("token61stream61", "dG9rZW42MXN0cmVhbTYx"),
    ("token61context61", "dG9rZW42MWNvbnRleHQ2MQ"),
    ("token61knowledge61", "dG9rZW42MWtub3dsZWRnZTYx"),
    ("prompt61knowledge61", "cHJvbXB0NjFrbm93bGVkZ2U2MQ"),
    ("prompt61vector61", "cHJvbXB0NjF2ZWN0b3I2MQ"),
    ("prompt61processor61", "cHJvbXB0NjFwcm9jZXNzb3I2MQ"),
    ("prompt61reasoning61", "cHJvbXB0NjFyZWFzb25pbmc2MQ"),
    ("session61reasoning61", "c2Vzc2lvbjYxcmVhc29uaW5nNjE"),
    ("session61machine61", "c2Vzc2lvbjYxbWFjaGluZTYx"),
    ("session61learning61", "c2Vzc2lvbjYxbGVhcm5pbmc2MQ"),
    ("session61model61", "c2Vzc2lvbjYxbW9kZWw2MQ"),
    ("library61model61", "bGlicmFyeTYxbW9kZWw2MQ"),
    ("library61token61", "bGlicmFyeTYxdG9rZW42MQ"),
    ("library61prompt61", "bGlicmFyeTYxcHJvbXB0NjE"),
    ("library61session61", "bGlicmFyeTYxc2Vzc2lvbjYx"),
    ("service61session61", "c2VydmljZTYxc2Vzc2lvbjYx"),
    ("service61library61", "c2VydmljZTYxbGlicmFyeTYx"),
    ("service61service61", "c2VydmljZTYxc2VydmljZTYx"),
    ("service61gateway61", "c2VydmljZTYxZ2F0ZXdheTYx"),
    ("gateway61gateway61", "Z2F0ZXdheTYxZ2F0ZXdheTYx"),
    ("gateway61storage61", "Z2F0ZXdheTYxc3RvcmFnZTYx"),
    ("gateway61network61", "Z2F0ZXdheTYxbmV0d29yazYx"),
    ("gateway61latency61", "Z2F0ZXdheTYxbGF0ZW5jeTYx"),
    ("storage61latency61", "c3RvcmFnZTYxbGF0ZW5jeTYx"),
    ("storage61buffer61", "c3RvcmFnZTYxYnVmZmVyNjE"),
    ("storage61queue61", "c3RvcmFnZTYxcXVldWU2MQ"),
    ("storage61worker61", "c3RvcmFnZTYxd29ya2VyNjE"),
    ("network61worker61", "bmV0d29yazYxd29ya2VyNjE"),
    ("network61kernel61", "bmV0d29yazYxa2VybmVsNjE"),
    ("network61signal61", "bmV0d29yazYxc2lnbmFsNjE"),
    ("network61packet61", "bmV0d29yazYxcGFja2V0NjE"),
    ("latency61packet61", "bGF0ZW5jeTYxcGFja2V0NjE"),
    ("latency61router61", "bGF0ZW5jeTYxcm91dGVyNjE"),
    ("latency61cluster61", "bGF0ZW5jeTYxY2x1c3RlcjYx"),
    ("latency61mirror61", "bGF0ZW5jeTYxbWlycm9yNjE"),
    ("buffer61mirror61", "YnVmZmVyNjFtaXJyb3I2MQ"),
    ("buffer61filter61", "YnVmZmVyNjFmaWx0ZXI2MQ"),
    ("buffer61ranking61", "YnVmZmVyNjFyYW5raW5nNjE"),
    ("buffer61encoding61", "YnVmZmVyNjFlbmNvZGluZzYx"),
    ("queue61encoding61", "cXVldWU2MWVuY29kaW5nNjE"),
    ("queue61mapping61", "cXVldWU2MW1hcHBpbmc2MQ"),
    ("queue61record61", "cXVldWU2MXJlY29yZDYx"),
    ("queue61candle61", "cXVldWU2MWNhbmRsZTYx"),
    ("worker61candle61", "d29ya2VyNjFjYW5kbGU2MQ"),
    ("worker61thread61", "d29ya2VyNjF0aHJlYWQ2MQ"),
    ("worker61kitten61", "d29ya2VyNjFraXR0ZW42MQ"),
    ("worker61sitting61", "d29ya2VyNjFzaXR0aW5nNjE"),
    ("kernel61sitting61", "a2VybmVsNjFzaXR0aW5nNjE"),
    ("kernel61agent61", "a2VybmVsNjFhZ2VudDYx"),
    ("kernel61angle61", "a2VybmVsNjFhbmdsZTYx"),
    ("kernel61universe61", "a2VybmVsNjF1bml2ZXJzZTYx"),
    ("signal61universe61", "c2lnbmFsNjF1bml2ZXJzZTYx"),
    ("signal61memory61", "c2lnbmFsNjFtZW1vcnk2MQ"),
    ("signal61stream61", "c2lnbmFsNjFzdHJlYW02MQ"),
    ("signal61context61", "c2lnbmFsNjFjb250ZXh0NjE"),
    ("packet61context61", "cGFja2V0NjFjb250ZXh0NjE"),
    ("packet61knowledge61", "cGFja2V0NjFrbm93bGVkZ2U2MQ"),
    ("packet61vector61", "cGFja2V0NjF2ZWN0b3I2MQ"),
    ("packet61processor61", "cGFja2V0NjFwcm9jZXNzb3I2MQ"),
    ("router61processor61", "cm91dGVyNjFwcm9jZXNzb3I2MQ"),
    ("router61reasoning61", "cm91dGVyNjFyZWFzb25pbmc2MQ"),
    ("router61machine61", "cm91dGVyNjFtYWNoaW5lNjE"),
    ("router61learning61", "cm91dGVyNjFsZWFybmluZzYx"),
    ("cluster61learning61", "Y2x1c3RlcjYxbGVhcm5pbmc2MQ"),
    ("cluster61model61", "Y2x1c3RlcjYxbW9kZWw2MQ"),
    ("cluster61token61", "Y2x1c3RlcjYxdG9rZW42MQ"),
    ("cluster61prompt61", "Y2x1c3RlcjYxcHJvbXB0NjE"),
    ("mirror61prompt61", "bWlycm9yNjFwcm9tcHQ2MQ"),
    ("mirror61session61", "bWlycm9yNjFzZXNzaW9uNjE"),
    ("mirror61library61", "bWlycm9yNjFsaWJyYXJ5NjE"),
    ("mirror61service61", "bWlycm9yNjFzZXJ2aWNlNjE"),
    ("filter61service61", "ZmlsdGVyNjFzZXJ2aWNlNjE"),
    ("filter61gateway61", "ZmlsdGVyNjFnYXRld2F5NjE"),
    ("filter61storage61", "ZmlsdGVyNjFzdG9yYWdlNjE"),
    ("filter61network61", "ZmlsdGVyNjFuZXR3b3JrNjE"),
    ("ranking61network61", "cmFua2luZzYxbmV0d29yazYx"),
    ("ranking61latency61", "cmFua2luZzYxbGF0ZW5jeTYx"),
    ("ranking61buffer61", "cmFua2luZzYxYnVmZmVyNjE"),
    ("ranking61queue61", "cmFua2luZzYxcXVldWU2MQ"),
    ("encoding61queue61", "ZW5jb2Rpbmc2MXF1ZXVlNjE"),
    ("encoding61worker61", "ZW5jb2Rpbmc2MXdvcmtlcjYx"),
    ("encoding61kernel61", "ZW5jb2Rpbmc2MWtlcm5lbDYx"),
    ("encoding61signal61", "ZW5jb2Rpbmc2MXNpZ25hbDYx"),
    ("mapping61signal61", "bWFwcGluZzYxc2lnbmFsNjE"),
    ("mapping61packet61", "bWFwcGluZzYxcGFja2V0NjE"),
    ("mapping61router61", "bWFwcGluZzYxcm91dGVyNjE"),
    ("mapping61cluster61", "bWFwcGluZzYxY2x1c3RlcjYx"),
    ("record61cluster61", "cmVjb3JkNjFjbHVzdGVyNjE"),
    ("record61mirror61", "cmVjb3JkNjFtaXJyb3I2MQ"),
    ("record61filter61", "cmVjb3JkNjFmaWx0ZXI2MQ"),
    ("record61ranking61", "cmVjb3JkNjFyYW5raW5nNjE"),
    ("candle61ranking61", "Y2FuZGxlNjFyYW5raW5nNjE"),
    ("candle61encoding61", "Y2FuZGxlNjFlbmNvZGluZzYx"),
    ("candle61mapping61", "Y2FuZGxlNjFtYXBwaW5nNjE"),
    ("candle61record61", "Y2FuZGxlNjFyZWNvcmQ2MQ"),
    ("thread61record61", "dGhyZWFkNjFyZWNvcmQ2MQ"),
    ("thread61candle61", "dGhyZWFkNjFjYW5kbGU2MQ"),
    ("thread61thread61", "dGhyZWFkNjF0aHJlYWQ2MQ"),
    ("thread61kitten61", "dGhyZWFkNjFraXR0ZW42MQ"),
    (
        "round 61: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNjE6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 61: agentuniverse is a framework for multi agents",
        "cm91bmQgNjE6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 61: knowledge stored as vectors enables retrieval",
        "cm91bmQgNjE6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 61: the processor reads the record then stops",
        "cm91bmQgNjE6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 61: a worker pulls the next task from the queue",
        "cm91bmQgNjE6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 61: signals travel through the network layer",
        "cm91bmQgNjE6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 61: the gateway routes each request by policy",
        "cm91bmQgNjE6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 61: memory grows until the buffer is full",
        "cm91bmQgNjE6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 61: the cluster mirrors every packet twice",
        "cm91bmQgNjE6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 61: ranking uses tokens learned from the corpus",
        "cm91bmQgNjE6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 61: a long session ends when the candle dies",
        "cm91bmQgNjE6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 61: encode the prompt then map the result",
        "cm91bmQgNjE6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 61: the kernel wakes the worker at dawn", "cm91bmQgNjE6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 61: service latency drops after the patch",
        "cm91bmQgNjE6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 61: the library caches every vector it sees",
        "cm91bmQgNjE6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 61: agents argue then the debate resolves",
        "cm91bmQgNjE6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 61: the filter keeps only strong matches",
        "cm91bmQgNjE6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 61: the model answers with a short reply",
        "cm91bmQgNjE6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 61: the recorder stores the reasoning trace",
        "cm91bmQgNjE6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 61: the angel watches the processor run", "cm91bmQgNjE6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 61: angle of the vector decides the match",
        "cm91bmQgNjE6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 61: the candle burns twice as long at night",
        "cm91bmQgNjE6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 61: a mirror of the universe in one line",
        "cm91bmQgNjE6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 61: the queue drains before the storm", "cm91bmQgNjE6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
