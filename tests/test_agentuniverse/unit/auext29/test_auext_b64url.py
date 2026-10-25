"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten29kitten29", "a2l0dGVuMjlraXR0ZW4yOQ"),
    ("kitten29sitting29", "a2l0dGVuMjlzaXR0aW5nMjk"),
    ("kitten29agent29", "a2l0dGVuMjlhZ2VudDI5"),
    ("kitten29angle29", "a2l0dGVuMjlhbmdsZTI5"),
    ("sitting29angle29", "c2l0dGluZzI5YW5nbGUyOQ"),
    ("sitting29universe29", "c2l0dGluZzI5dW5pdmVyc2UyOQ"),
    ("sitting29memory29", "c2l0dGluZzI5bWVtb3J5Mjk"),
    ("sitting29stream29", "c2l0dGluZzI5c3RyZWFtMjk"),
    ("agent29stream29", "YWdlbnQyOXN0cmVhbTI5"),
    ("agent29context29", "YWdlbnQyOWNvbnRleHQyOQ"),
    ("agent29knowledge29", "YWdlbnQyOWtub3dsZWRnZTI5"),
    ("agent29vector29", "YWdlbnQyOXZlY3RvcjI5"),
    ("angle29vector29", "YW5nbGUyOXZlY3RvcjI5"),
    ("angle29processor29", "YW5nbGUyOXByb2Nlc3NvcjI5"),
    ("angle29reasoning29", "YW5nbGUyOXJlYXNvbmluZzI5"),
    ("angle29machine29", "YW5nbGUyOW1hY2hpbmUyOQ"),
    ("universe29machine29", "dW5pdmVyc2UyOW1hY2hpbmUyOQ"),
    ("universe29learning29", "dW5pdmVyc2UyOWxlYXJuaW5nMjk"),
    ("universe29model29", "dW5pdmVyc2UyOW1vZGVsMjk"),
    ("universe29token29", "dW5pdmVyc2UyOXRva2VuMjk"),
    ("memory29token29", "bWVtb3J5Mjl0b2tlbjI5"),
    ("memory29prompt29", "bWVtb3J5Mjlwcm9tcHQyOQ"),
    ("memory29session29", "bWVtb3J5MjlzZXNzaW9uMjk"),
    ("memory29library29", "bWVtb3J5MjlsaWJyYXJ5Mjk"),
    ("stream29library29", "c3RyZWFtMjlsaWJyYXJ5Mjk"),
    ("stream29service29", "c3RyZWFtMjlzZXJ2aWNlMjk"),
    ("stream29gateway29", "c3RyZWFtMjlnYXRld2F5Mjk"),
    ("stream29storage29", "c3RyZWFtMjlzdG9yYWdlMjk"),
    ("context29storage29", "Y29udGV4dDI5c3RvcmFnZTI5"),
    ("context29network29", "Y29udGV4dDI5bmV0d29yazI5"),
    ("context29latency29", "Y29udGV4dDI5bGF0ZW5jeTI5"),
    ("context29buffer29", "Y29udGV4dDI5YnVmZmVyMjk"),
    ("knowledge29buffer29", "a25vd2xlZGdlMjlidWZmZXIyOQ"),
    ("knowledge29queue29", "a25vd2xlZGdlMjlxdWV1ZTI5"),
    ("knowledge29worker29", "a25vd2xlZGdlMjl3b3JrZXIyOQ"),
    ("knowledge29kernel29", "a25vd2xlZGdlMjlrZXJuZWwyOQ"),
    ("vector29kernel29", "dmVjdG9yMjlrZXJuZWwyOQ"),
    ("vector29signal29", "dmVjdG9yMjlzaWduYWwyOQ"),
    ("vector29packet29", "dmVjdG9yMjlwYWNrZXQyOQ"),
    ("vector29router29", "dmVjdG9yMjlyb3V0ZXIyOQ"),
    ("processor29router29", "cHJvY2Vzc29yMjlyb3V0ZXIyOQ"),
    ("processor29cluster29", "cHJvY2Vzc29yMjljbHVzdGVyMjk"),
    ("processor29mirror29", "cHJvY2Vzc29yMjltaXJyb3IyOQ"),
    ("processor29filter29", "cHJvY2Vzc29yMjlmaWx0ZXIyOQ"),
    ("reasoning29filter29", "cmVhc29uaW5nMjlmaWx0ZXIyOQ"),
    ("reasoning29ranking29", "cmVhc29uaW5nMjlyYW5raW5nMjk"),
    ("reasoning29encoding29", "cmVhc29uaW5nMjllbmNvZGluZzI5"),
    ("reasoning29mapping29", "cmVhc29uaW5nMjltYXBwaW5nMjk"),
    ("machine29mapping29", "bWFjaGluZTI5bWFwcGluZzI5"),
    ("machine29record29", "bWFjaGluZTI5cmVjb3JkMjk"),
    ("machine29candle29", "bWFjaGluZTI5Y2FuZGxlMjk"),
    ("machine29thread29", "bWFjaGluZTI5dGhyZWFkMjk"),
    ("learning29thread29", "bGVhcm5pbmcyOXRocmVhZDI5"),
    ("learning29kitten29", "bGVhcm5pbmcyOWtpdHRlbjI5"),
    ("learning29sitting29", "bGVhcm5pbmcyOXNpdHRpbmcyOQ"),
    ("learning29agent29", "bGVhcm5pbmcyOWFnZW50Mjk"),
    ("model29agent29", "bW9kZWwyOWFnZW50Mjk"),
    ("model29angle29", "bW9kZWwyOWFuZ2xlMjk"),
    ("model29universe29", "bW9kZWwyOXVuaXZlcnNlMjk"),
    ("model29memory29", "bW9kZWwyOW1lbW9yeTI5"),
    ("token29memory29", "dG9rZW4yOW1lbW9yeTI5"),
    ("token29stream29", "dG9rZW4yOXN0cmVhbTI5"),
    ("token29context29", "dG9rZW4yOWNvbnRleHQyOQ"),
    ("token29knowledge29", "dG9rZW4yOWtub3dsZWRnZTI5"),
    ("prompt29knowledge29", "cHJvbXB0Mjlrbm93bGVkZ2UyOQ"),
    ("prompt29vector29", "cHJvbXB0Mjl2ZWN0b3IyOQ"),
    ("prompt29processor29", "cHJvbXB0Mjlwcm9jZXNzb3IyOQ"),
    ("prompt29reasoning29", "cHJvbXB0MjlyZWFzb25pbmcyOQ"),
    ("session29reasoning29", "c2Vzc2lvbjI5cmVhc29uaW5nMjk"),
    ("session29machine29", "c2Vzc2lvbjI5bWFjaGluZTI5"),
    ("session29learning29", "c2Vzc2lvbjI5bGVhcm5pbmcyOQ"),
    ("session29model29", "c2Vzc2lvbjI5bW9kZWwyOQ"),
    ("library29model29", "bGlicmFyeTI5bW9kZWwyOQ"),
    ("library29token29", "bGlicmFyeTI5dG9rZW4yOQ"),
    ("library29prompt29", "bGlicmFyeTI5cHJvbXB0Mjk"),
    ("library29session29", "bGlicmFyeTI5c2Vzc2lvbjI5"),
    ("service29session29", "c2VydmljZTI5c2Vzc2lvbjI5"),
    ("service29library29", "c2VydmljZTI5bGlicmFyeTI5"),
    ("service29service29", "c2VydmljZTI5c2VydmljZTI5"),
    ("service29gateway29", "c2VydmljZTI5Z2F0ZXdheTI5"),
    ("gateway29gateway29", "Z2F0ZXdheTI5Z2F0ZXdheTI5"),
    ("gateway29storage29", "Z2F0ZXdheTI5c3RvcmFnZTI5"),
    ("gateway29network29", "Z2F0ZXdheTI5bmV0d29yazI5"),
    ("gateway29latency29", "Z2F0ZXdheTI5bGF0ZW5jeTI5"),
    ("storage29latency29", "c3RvcmFnZTI5bGF0ZW5jeTI5"),
    ("storage29buffer29", "c3RvcmFnZTI5YnVmZmVyMjk"),
    ("storage29queue29", "c3RvcmFnZTI5cXVldWUyOQ"),
    ("storage29worker29", "c3RvcmFnZTI5d29ya2VyMjk"),
    ("network29worker29", "bmV0d29yazI5d29ya2VyMjk"),
    ("network29kernel29", "bmV0d29yazI5a2VybmVsMjk"),
    ("network29signal29", "bmV0d29yazI5c2lnbmFsMjk"),
    ("network29packet29", "bmV0d29yazI5cGFja2V0Mjk"),
    ("latency29packet29", "bGF0ZW5jeTI5cGFja2V0Mjk"),
    ("latency29router29", "bGF0ZW5jeTI5cm91dGVyMjk"),
    ("latency29cluster29", "bGF0ZW5jeTI5Y2x1c3RlcjI5"),
    ("latency29mirror29", "bGF0ZW5jeTI5bWlycm9yMjk"),
    ("buffer29mirror29", "YnVmZmVyMjltaXJyb3IyOQ"),
    ("buffer29filter29", "YnVmZmVyMjlmaWx0ZXIyOQ"),
    ("buffer29ranking29", "YnVmZmVyMjlyYW5raW5nMjk"),
    ("buffer29encoding29", "YnVmZmVyMjllbmNvZGluZzI5"),
    ("queue29encoding29", "cXVldWUyOWVuY29kaW5nMjk"),
    ("queue29mapping29", "cXVldWUyOW1hcHBpbmcyOQ"),
    ("queue29record29", "cXVldWUyOXJlY29yZDI5"),
    ("queue29candle29", "cXVldWUyOWNhbmRsZTI5"),
    ("worker29candle29", "d29ya2VyMjljYW5kbGUyOQ"),
    ("worker29thread29", "d29ya2VyMjl0aHJlYWQyOQ"),
    ("worker29kitten29", "d29ya2VyMjlraXR0ZW4yOQ"),
    ("worker29sitting29", "d29ya2VyMjlzaXR0aW5nMjk"),
    ("kernel29sitting29", "a2VybmVsMjlzaXR0aW5nMjk"),
    ("kernel29agent29", "a2VybmVsMjlhZ2VudDI5"),
    ("kernel29angle29", "a2VybmVsMjlhbmdsZTI5"),
    ("kernel29universe29", "a2VybmVsMjl1bml2ZXJzZTI5"),
    ("signal29universe29", "c2lnbmFsMjl1bml2ZXJzZTI5"),
    ("signal29memory29", "c2lnbmFsMjltZW1vcnkyOQ"),
    ("signal29stream29", "c2lnbmFsMjlzdHJlYW0yOQ"),
    ("signal29context29", "c2lnbmFsMjljb250ZXh0Mjk"),
    ("packet29context29", "cGFja2V0Mjljb250ZXh0Mjk"),
    ("packet29knowledge29", "cGFja2V0Mjlrbm93bGVkZ2UyOQ"),
    ("packet29vector29", "cGFja2V0Mjl2ZWN0b3IyOQ"),
    ("packet29processor29", "cGFja2V0Mjlwcm9jZXNzb3IyOQ"),
    ("router29processor29", "cm91dGVyMjlwcm9jZXNzb3IyOQ"),
    ("router29reasoning29", "cm91dGVyMjlyZWFzb25pbmcyOQ"),
    ("router29machine29", "cm91dGVyMjltYWNoaW5lMjk"),
    ("router29learning29", "cm91dGVyMjlsZWFybmluZzI5"),
    ("cluster29learning29", "Y2x1c3RlcjI5bGVhcm5pbmcyOQ"),
    ("cluster29model29", "Y2x1c3RlcjI5bW9kZWwyOQ"),
    ("cluster29token29", "Y2x1c3RlcjI5dG9rZW4yOQ"),
    ("cluster29prompt29", "Y2x1c3RlcjI5cHJvbXB0Mjk"),
    ("mirror29prompt29", "bWlycm9yMjlwcm9tcHQyOQ"),
    ("mirror29session29", "bWlycm9yMjlzZXNzaW9uMjk"),
    ("mirror29library29", "bWlycm9yMjlsaWJyYXJ5Mjk"),
    ("mirror29service29", "bWlycm9yMjlzZXJ2aWNlMjk"),
    ("filter29service29", "ZmlsdGVyMjlzZXJ2aWNlMjk"),
    ("filter29gateway29", "ZmlsdGVyMjlnYXRld2F5Mjk"),
    ("filter29storage29", "ZmlsdGVyMjlzdG9yYWdlMjk"),
    ("filter29network29", "ZmlsdGVyMjluZXR3b3JrMjk"),
    ("ranking29network29", "cmFua2luZzI5bmV0d29yazI5"),
    ("ranking29latency29", "cmFua2luZzI5bGF0ZW5jeTI5"),
    ("ranking29buffer29", "cmFua2luZzI5YnVmZmVyMjk"),
    ("ranking29queue29", "cmFua2luZzI5cXVldWUyOQ"),
    ("encoding29queue29", "ZW5jb2RpbmcyOXF1ZXVlMjk"),
    ("encoding29worker29", "ZW5jb2RpbmcyOXdvcmtlcjI5"),
    ("encoding29kernel29", "ZW5jb2RpbmcyOWtlcm5lbDI5"),
    ("encoding29signal29", "ZW5jb2RpbmcyOXNpZ25hbDI5"),
    ("mapping29signal29", "bWFwcGluZzI5c2lnbmFsMjk"),
    ("mapping29packet29", "bWFwcGluZzI5cGFja2V0Mjk"),
    ("mapping29router29", "bWFwcGluZzI5cm91dGVyMjk"),
    ("mapping29cluster29", "bWFwcGluZzI5Y2x1c3RlcjI5"),
    ("record29cluster29", "cmVjb3JkMjljbHVzdGVyMjk"),
    ("record29mirror29", "cmVjb3JkMjltaXJyb3IyOQ"),
    ("record29filter29", "cmVjb3JkMjlmaWx0ZXIyOQ"),
    ("record29ranking29", "cmVjb3JkMjlyYW5raW5nMjk"),
    ("candle29ranking29", "Y2FuZGxlMjlyYW5raW5nMjk"),
    ("candle29encoding29", "Y2FuZGxlMjllbmNvZGluZzI5"),
    ("candle29mapping29", "Y2FuZGxlMjltYXBwaW5nMjk"),
    ("candle29record29", "Y2FuZGxlMjlyZWNvcmQyOQ"),
    ("thread29record29", "dGhyZWFkMjlyZWNvcmQyOQ"),
    ("thread29candle29", "dGhyZWFkMjljYW5kbGUyOQ"),
    ("thread29thread29", "dGhyZWFkMjl0aHJlYWQyOQ"),
    ("thread29kitten29", "dGhyZWFkMjlraXR0ZW4yOQ"),
    (
        "round 29: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjk6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 29: agentuniverse is a framework for multi agents",
        "cm91bmQgMjk6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 29: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjk6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 29: the processor reads the record then stops",
        "cm91bmQgMjk6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 29: a worker pulls the next task from the queue",
        "cm91bmQgMjk6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 29: signals travel through the network layer",
        "cm91bmQgMjk6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 29: the gateway routes each request by policy",
        "cm91bmQgMjk6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 29: memory grows until the buffer is full",
        "cm91bmQgMjk6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 29: the cluster mirrors every packet twice",
        "cm91bmQgMjk6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 29: ranking uses tokens learned from the corpus",
        "cm91bmQgMjk6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 29: a long session ends when the candle dies",
        "cm91bmQgMjk6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 29: encode the prompt then map the result",
        "cm91bmQgMjk6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 29: the kernel wakes the worker at dawn", "cm91bmQgMjk6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 29: service latency drops after the patch",
        "cm91bmQgMjk6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 29: the library caches every vector it sees",
        "cm91bmQgMjk6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 29: agents argue then the debate resolves",
        "cm91bmQgMjk6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 29: the filter keeps only strong matches",
        "cm91bmQgMjk6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 29: the model answers with a short reply",
        "cm91bmQgMjk6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 29: the recorder stores the reasoning trace",
        "cm91bmQgMjk6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 29: the angel watches the processor run", "cm91bmQgMjk6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 29: angle of the vector decides the match",
        "cm91bmQgMjk6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 29: the candle burns twice as long at night",
        "cm91bmQgMjk6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 29: a mirror of the universe in one line",
        "cm91bmQgMjk6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 29: the queue drains before the storm", "cm91bmQgMjk6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
