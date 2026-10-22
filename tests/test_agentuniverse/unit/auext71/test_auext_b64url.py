"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten71kitten71", "a2l0dGVuNzFraXR0ZW43MQ"),
    ("kitten71sitting71", "a2l0dGVuNzFzaXR0aW5nNzE"),
    ("kitten71agent71", "a2l0dGVuNzFhZ2VudDcx"),
    ("kitten71angle71", "a2l0dGVuNzFhbmdsZTcx"),
    ("sitting71angle71", "c2l0dGluZzcxYW5nbGU3MQ"),
    ("sitting71universe71", "c2l0dGluZzcxdW5pdmVyc2U3MQ"),
    ("sitting71memory71", "c2l0dGluZzcxbWVtb3J5NzE"),
    ("sitting71stream71", "c2l0dGluZzcxc3RyZWFtNzE"),
    ("agent71stream71", "YWdlbnQ3MXN0cmVhbTcx"),
    ("agent71context71", "YWdlbnQ3MWNvbnRleHQ3MQ"),
    ("agent71knowledge71", "YWdlbnQ3MWtub3dsZWRnZTcx"),
    ("agent71vector71", "YWdlbnQ3MXZlY3Rvcjcx"),
    ("angle71vector71", "YW5nbGU3MXZlY3Rvcjcx"),
    ("angle71processor71", "YW5nbGU3MXByb2Nlc3Nvcjcx"),
    ("angle71reasoning71", "YW5nbGU3MXJlYXNvbmluZzcx"),
    ("angle71machine71", "YW5nbGU3MW1hY2hpbmU3MQ"),
    ("universe71machine71", "dW5pdmVyc2U3MW1hY2hpbmU3MQ"),
    ("universe71learning71", "dW5pdmVyc2U3MWxlYXJuaW5nNzE"),
    ("universe71model71", "dW5pdmVyc2U3MW1vZGVsNzE"),
    ("universe71token71", "dW5pdmVyc2U3MXRva2VuNzE"),
    ("memory71token71", "bWVtb3J5NzF0b2tlbjcx"),
    ("memory71prompt71", "bWVtb3J5NzFwcm9tcHQ3MQ"),
    ("memory71session71", "bWVtb3J5NzFzZXNzaW9uNzE"),
    ("memory71library71", "bWVtb3J5NzFsaWJyYXJ5NzE"),
    ("stream71library71", "c3RyZWFtNzFsaWJyYXJ5NzE"),
    ("stream71service71", "c3RyZWFtNzFzZXJ2aWNlNzE"),
    ("stream71gateway71", "c3RyZWFtNzFnYXRld2F5NzE"),
    ("stream71storage71", "c3RyZWFtNzFzdG9yYWdlNzE"),
    ("context71storage71", "Y29udGV4dDcxc3RvcmFnZTcx"),
    ("context71network71", "Y29udGV4dDcxbmV0d29yazcx"),
    ("context71latency71", "Y29udGV4dDcxbGF0ZW5jeTcx"),
    ("context71buffer71", "Y29udGV4dDcxYnVmZmVyNzE"),
    ("knowledge71buffer71", "a25vd2xlZGdlNzFidWZmZXI3MQ"),
    ("knowledge71queue71", "a25vd2xlZGdlNzFxdWV1ZTcx"),
    ("knowledge71worker71", "a25vd2xlZGdlNzF3b3JrZXI3MQ"),
    ("knowledge71kernel71", "a25vd2xlZGdlNzFrZXJuZWw3MQ"),
    ("vector71kernel71", "dmVjdG9yNzFrZXJuZWw3MQ"),
    ("vector71signal71", "dmVjdG9yNzFzaWduYWw3MQ"),
    ("vector71packet71", "dmVjdG9yNzFwYWNrZXQ3MQ"),
    ("vector71router71", "dmVjdG9yNzFyb3V0ZXI3MQ"),
    ("processor71router71", "cHJvY2Vzc29yNzFyb3V0ZXI3MQ"),
    ("processor71cluster71", "cHJvY2Vzc29yNzFjbHVzdGVyNzE"),
    ("processor71mirror71", "cHJvY2Vzc29yNzFtaXJyb3I3MQ"),
    ("processor71filter71", "cHJvY2Vzc29yNzFmaWx0ZXI3MQ"),
    ("reasoning71filter71", "cmVhc29uaW5nNzFmaWx0ZXI3MQ"),
    ("reasoning71ranking71", "cmVhc29uaW5nNzFyYW5raW5nNzE"),
    ("reasoning71encoding71", "cmVhc29uaW5nNzFlbmNvZGluZzcx"),
    ("reasoning71mapping71", "cmVhc29uaW5nNzFtYXBwaW5nNzE"),
    ("machine71mapping71", "bWFjaGluZTcxbWFwcGluZzcx"),
    ("machine71record71", "bWFjaGluZTcxcmVjb3JkNzE"),
    ("machine71candle71", "bWFjaGluZTcxY2FuZGxlNzE"),
    ("machine71thread71", "bWFjaGluZTcxdGhyZWFkNzE"),
    ("learning71thread71", "bGVhcm5pbmc3MXRocmVhZDcx"),
    ("learning71kitten71", "bGVhcm5pbmc3MWtpdHRlbjcx"),
    ("learning71sitting71", "bGVhcm5pbmc3MXNpdHRpbmc3MQ"),
    ("learning71agent71", "bGVhcm5pbmc3MWFnZW50NzE"),
    ("model71agent71", "bW9kZWw3MWFnZW50NzE"),
    ("model71angle71", "bW9kZWw3MWFuZ2xlNzE"),
    ("model71universe71", "bW9kZWw3MXVuaXZlcnNlNzE"),
    ("model71memory71", "bW9kZWw3MW1lbW9yeTcx"),
    ("token71memory71", "dG9rZW43MW1lbW9yeTcx"),
    ("token71stream71", "dG9rZW43MXN0cmVhbTcx"),
    ("token71context71", "dG9rZW43MWNvbnRleHQ3MQ"),
    ("token71knowledge71", "dG9rZW43MWtub3dsZWRnZTcx"),
    ("prompt71knowledge71", "cHJvbXB0NzFrbm93bGVkZ2U3MQ"),
    ("prompt71vector71", "cHJvbXB0NzF2ZWN0b3I3MQ"),
    ("prompt71processor71", "cHJvbXB0NzFwcm9jZXNzb3I3MQ"),
    ("prompt71reasoning71", "cHJvbXB0NzFyZWFzb25pbmc3MQ"),
    ("session71reasoning71", "c2Vzc2lvbjcxcmVhc29uaW5nNzE"),
    ("session71machine71", "c2Vzc2lvbjcxbWFjaGluZTcx"),
    ("session71learning71", "c2Vzc2lvbjcxbGVhcm5pbmc3MQ"),
    ("session71model71", "c2Vzc2lvbjcxbW9kZWw3MQ"),
    ("library71model71", "bGlicmFyeTcxbW9kZWw3MQ"),
    ("library71token71", "bGlicmFyeTcxdG9rZW43MQ"),
    ("library71prompt71", "bGlicmFyeTcxcHJvbXB0NzE"),
    ("library71session71", "bGlicmFyeTcxc2Vzc2lvbjcx"),
    ("service71session71", "c2VydmljZTcxc2Vzc2lvbjcx"),
    ("service71library71", "c2VydmljZTcxbGlicmFyeTcx"),
    ("service71service71", "c2VydmljZTcxc2VydmljZTcx"),
    ("service71gateway71", "c2VydmljZTcxZ2F0ZXdheTcx"),
    ("gateway71gateway71", "Z2F0ZXdheTcxZ2F0ZXdheTcx"),
    ("gateway71storage71", "Z2F0ZXdheTcxc3RvcmFnZTcx"),
    ("gateway71network71", "Z2F0ZXdheTcxbmV0d29yazcx"),
    ("gateway71latency71", "Z2F0ZXdheTcxbGF0ZW5jeTcx"),
    ("storage71latency71", "c3RvcmFnZTcxbGF0ZW5jeTcx"),
    ("storage71buffer71", "c3RvcmFnZTcxYnVmZmVyNzE"),
    ("storage71queue71", "c3RvcmFnZTcxcXVldWU3MQ"),
    ("storage71worker71", "c3RvcmFnZTcxd29ya2VyNzE"),
    ("network71worker71", "bmV0d29yazcxd29ya2VyNzE"),
    ("network71kernel71", "bmV0d29yazcxa2VybmVsNzE"),
    ("network71signal71", "bmV0d29yazcxc2lnbmFsNzE"),
    ("network71packet71", "bmV0d29yazcxcGFja2V0NzE"),
    ("latency71packet71", "bGF0ZW5jeTcxcGFja2V0NzE"),
    ("latency71router71", "bGF0ZW5jeTcxcm91dGVyNzE"),
    ("latency71cluster71", "bGF0ZW5jeTcxY2x1c3Rlcjcx"),
    ("latency71mirror71", "bGF0ZW5jeTcxbWlycm9yNzE"),
    ("buffer71mirror71", "YnVmZmVyNzFtaXJyb3I3MQ"),
    ("buffer71filter71", "YnVmZmVyNzFmaWx0ZXI3MQ"),
    ("buffer71ranking71", "YnVmZmVyNzFyYW5raW5nNzE"),
    ("buffer71encoding71", "YnVmZmVyNzFlbmNvZGluZzcx"),
    ("queue71encoding71", "cXVldWU3MWVuY29kaW5nNzE"),
    ("queue71mapping71", "cXVldWU3MW1hcHBpbmc3MQ"),
    ("queue71record71", "cXVldWU3MXJlY29yZDcx"),
    ("queue71candle71", "cXVldWU3MWNhbmRsZTcx"),
    ("worker71candle71", "d29ya2VyNzFjYW5kbGU3MQ"),
    ("worker71thread71", "d29ya2VyNzF0aHJlYWQ3MQ"),
    ("worker71kitten71", "d29ya2VyNzFraXR0ZW43MQ"),
    ("worker71sitting71", "d29ya2VyNzFzaXR0aW5nNzE"),
    ("kernel71sitting71", "a2VybmVsNzFzaXR0aW5nNzE"),
    ("kernel71agent71", "a2VybmVsNzFhZ2VudDcx"),
    ("kernel71angle71", "a2VybmVsNzFhbmdsZTcx"),
    ("kernel71universe71", "a2VybmVsNzF1bml2ZXJzZTcx"),
    ("signal71universe71", "c2lnbmFsNzF1bml2ZXJzZTcx"),
    ("signal71memory71", "c2lnbmFsNzFtZW1vcnk3MQ"),
    ("signal71stream71", "c2lnbmFsNzFzdHJlYW03MQ"),
    ("signal71context71", "c2lnbmFsNzFjb250ZXh0NzE"),
    ("packet71context71", "cGFja2V0NzFjb250ZXh0NzE"),
    ("packet71knowledge71", "cGFja2V0NzFrbm93bGVkZ2U3MQ"),
    ("packet71vector71", "cGFja2V0NzF2ZWN0b3I3MQ"),
    ("packet71processor71", "cGFja2V0NzFwcm9jZXNzb3I3MQ"),
    ("router71processor71", "cm91dGVyNzFwcm9jZXNzb3I3MQ"),
    ("router71reasoning71", "cm91dGVyNzFyZWFzb25pbmc3MQ"),
    ("router71machine71", "cm91dGVyNzFtYWNoaW5lNzE"),
    ("router71learning71", "cm91dGVyNzFsZWFybmluZzcx"),
    ("cluster71learning71", "Y2x1c3RlcjcxbGVhcm5pbmc3MQ"),
    ("cluster71model71", "Y2x1c3RlcjcxbW9kZWw3MQ"),
    ("cluster71token71", "Y2x1c3RlcjcxdG9rZW43MQ"),
    ("cluster71prompt71", "Y2x1c3RlcjcxcHJvbXB0NzE"),
    ("mirror71prompt71", "bWlycm9yNzFwcm9tcHQ3MQ"),
    ("mirror71session71", "bWlycm9yNzFzZXNzaW9uNzE"),
    ("mirror71library71", "bWlycm9yNzFsaWJyYXJ5NzE"),
    ("mirror71service71", "bWlycm9yNzFzZXJ2aWNlNzE"),
    ("filter71service71", "ZmlsdGVyNzFzZXJ2aWNlNzE"),
    ("filter71gateway71", "ZmlsdGVyNzFnYXRld2F5NzE"),
    ("filter71storage71", "ZmlsdGVyNzFzdG9yYWdlNzE"),
    ("filter71network71", "ZmlsdGVyNzFuZXR3b3JrNzE"),
    ("ranking71network71", "cmFua2luZzcxbmV0d29yazcx"),
    ("ranking71latency71", "cmFua2luZzcxbGF0ZW5jeTcx"),
    ("ranking71buffer71", "cmFua2luZzcxYnVmZmVyNzE"),
    ("ranking71queue71", "cmFua2luZzcxcXVldWU3MQ"),
    ("encoding71queue71", "ZW5jb2Rpbmc3MXF1ZXVlNzE"),
    ("encoding71worker71", "ZW5jb2Rpbmc3MXdvcmtlcjcx"),
    ("encoding71kernel71", "ZW5jb2Rpbmc3MWtlcm5lbDcx"),
    ("encoding71signal71", "ZW5jb2Rpbmc3MXNpZ25hbDcx"),
    ("mapping71signal71", "bWFwcGluZzcxc2lnbmFsNzE"),
    ("mapping71packet71", "bWFwcGluZzcxcGFja2V0NzE"),
    ("mapping71router71", "bWFwcGluZzcxcm91dGVyNzE"),
    ("mapping71cluster71", "bWFwcGluZzcxY2x1c3Rlcjcx"),
    ("record71cluster71", "cmVjb3JkNzFjbHVzdGVyNzE"),
    ("record71mirror71", "cmVjb3JkNzFtaXJyb3I3MQ"),
    ("record71filter71", "cmVjb3JkNzFmaWx0ZXI3MQ"),
    ("record71ranking71", "cmVjb3JkNzFyYW5raW5nNzE"),
    ("candle71ranking71", "Y2FuZGxlNzFyYW5raW5nNzE"),
    ("candle71encoding71", "Y2FuZGxlNzFlbmNvZGluZzcx"),
    ("candle71mapping71", "Y2FuZGxlNzFtYXBwaW5nNzE"),
    ("candle71record71", "Y2FuZGxlNzFyZWNvcmQ3MQ"),
    ("thread71record71", "dGhyZWFkNzFyZWNvcmQ3MQ"),
    ("thread71candle71", "dGhyZWFkNzFjYW5kbGU3MQ"),
    ("thread71thread71", "dGhyZWFkNzF0aHJlYWQ3MQ"),
    ("thread71kitten71", "dGhyZWFkNzFraXR0ZW43MQ"),
    (
        "round 71: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzE6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 71: agentuniverse is a framework for multi agents",
        "cm91bmQgNzE6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 71: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzE6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 71: the processor reads the record then stops",
        "cm91bmQgNzE6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 71: a worker pulls the next task from the queue",
        "cm91bmQgNzE6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 71: signals travel through the network layer",
        "cm91bmQgNzE6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 71: the gateway routes each request by policy",
        "cm91bmQgNzE6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 71: memory grows until the buffer is full",
        "cm91bmQgNzE6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 71: the cluster mirrors every packet twice",
        "cm91bmQgNzE6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 71: ranking uses tokens learned from the corpus",
        "cm91bmQgNzE6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 71: a long session ends when the candle dies",
        "cm91bmQgNzE6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 71: encode the prompt then map the result",
        "cm91bmQgNzE6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 71: the kernel wakes the worker at dawn", "cm91bmQgNzE6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 71: service latency drops after the patch",
        "cm91bmQgNzE6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 71: the library caches every vector it sees",
        "cm91bmQgNzE6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 71: agents argue then the debate resolves",
        "cm91bmQgNzE6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 71: the filter keeps only strong matches",
        "cm91bmQgNzE6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 71: the model answers with a short reply",
        "cm91bmQgNzE6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 71: the recorder stores the reasoning trace",
        "cm91bmQgNzE6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 71: the angel watches the processor run", "cm91bmQgNzE6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 71: angle of the vector decides the match",
        "cm91bmQgNzE6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 71: the candle burns twice as long at night",
        "cm91bmQgNzE6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 71: a mirror of the universe in one line",
        "cm91bmQgNzE6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 71: the queue drains before the storm", "cm91bmQgNzE6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
