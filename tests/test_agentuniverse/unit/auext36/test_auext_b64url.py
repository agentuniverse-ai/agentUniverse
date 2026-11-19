"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten36kitten36", "a2l0dGVuMzZraXR0ZW4zNg"),
    ("kitten36sitting36", "a2l0dGVuMzZzaXR0aW5nMzY"),
    ("kitten36agent36", "a2l0dGVuMzZhZ2VudDM2"),
    ("kitten36angle36", "a2l0dGVuMzZhbmdsZTM2"),
    ("sitting36angle36", "c2l0dGluZzM2YW5nbGUzNg"),
    ("sitting36universe36", "c2l0dGluZzM2dW5pdmVyc2UzNg"),
    ("sitting36memory36", "c2l0dGluZzM2bWVtb3J5MzY"),
    ("sitting36stream36", "c2l0dGluZzM2c3RyZWFtMzY"),
    ("agent36stream36", "YWdlbnQzNnN0cmVhbTM2"),
    ("agent36context36", "YWdlbnQzNmNvbnRleHQzNg"),
    ("agent36knowledge36", "YWdlbnQzNmtub3dsZWRnZTM2"),
    ("agent36vector36", "YWdlbnQzNnZlY3RvcjM2"),
    ("angle36vector36", "YW5nbGUzNnZlY3RvcjM2"),
    ("angle36processor36", "YW5nbGUzNnByb2Nlc3NvcjM2"),
    ("angle36reasoning36", "YW5nbGUzNnJlYXNvbmluZzM2"),
    ("angle36machine36", "YW5nbGUzNm1hY2hpbmUzNg"),
    ("universe36machine36", "dW5pdmVyc2UzNm1hY2hpbmUzNg"),
    ("universe36learning36", "dW5pdmVyc2UzNmxlYXJuaW5nMzY"),
    ("universe36model36", "dW5pdmVyc2UzNm1vZGVsMzY"),
    ("universe36token36", "dW5pdmVyc2UzNnRva2VuMzY"),
    ("memory36token36", "bWVtb3J5MzZ0b2tlbjM2"),
    ("memory36prompt36", "bWVtb3J5MzZwcm9tcHQzNg"),
    ("memory36session36", "bWVtb3J5MzZzZXNzaW9uMzY"),
    ("memory36library36", "bWVtb3J5MzZsaWJyYXJ5MzY"),
    ("stream36library36", "c3RyZWFtMzZsaWJyYXJ5MzY"),
    ("stream36service36", "c3RyZWFtMzZzZXJ2aWNlMzY"),
    ("stream36gateway36", "c3RyZWFtMzZnYXRld2F5MzY"),
    ("stream36storage36", "c3RyZWFtMzZzdG9yYWdlMzY"),
    ("context36storage36", "Y29udGV4dDM2c3RvcmFnZTM2"),
    ("context36network36", "Y29udGV4dDM2bmV0d29yazM2"),
    ("context36latency36", "Y29udGV4dDM2bGF0ZW5jeTM2"),
    ("context36buffer36", "Y29udGV4dDM2YnVmZmVyMzY"),
    ("knowledge36buffer36", "a25vd2xlZGdlMzZidWZmZXIzNg"),
    ("knowledge36queue36", "a25vd2xlZGdlMzZxdWV1ZTM2"),
    ("knowledge36worker36", "a25vd2xlZGdlMzZ3b3JrZXIzNg"),
    ("knowledge36kernel36", "a25vd2xlZGdlMzZrZXJuZWwzNg"),
    ("vector36kernel36", "dmVjdG9yMzZrZXJuZWwzNg"),
    ("vector36signal36", "dmVjdG9yMzZzaWduYWwzNg"),
    ("vector36packet36", "dmVjdG9yMzZwYWNrZXQzNg"),
    ("vector36router36", "dmVjdG9yMzZyb3V0ZXIzNg"),
    ("processor36router36", "cHJvY2Vzc29yMzZyb3V0ZXIzNg"),
    ("processor36cluster36", "cHJvY2Vzc29yMzZjbHVzdGVyMzY"),
    ("processor36mirror36", "cHJvY2Vzc29yMzZtaXJyb3IzNg"),
    ("processor36filter36", "cHJvY2Vzc29yMzZmaWx0ZXIzNg"),
    ("reasoning36filter36", "cmVhc29uaW5nMzZmaWx0ZXIzNg"),
    ("reasoning36ranking36", "cmVhc29uaW5nMzZyYW5raW5nMzY"),
    ("reasoning36encoding36", "cmVhc29uaW5nMzZlbmNvZGluZzM2"),
    ("reasoning36mapping36", "cmVhc29uaW5nMzZtYXBwaW5nMzY"),
    ("machine36mapping36", "bWFjaGluZTM2bWFwcGluZzM2"),
    ("machine36record36", "bWFjaGluZTM2cmVjb3JkMzY"),
    ("machine36candle36", "bWFjaGluZTM2Y2FuZGxlMzY"),
    ("machine36thread36", "bWFjaGluZTM2dGhyZWFkMzY"),
    ("learning36thread36", "bGVhcm5pbmczNnRocmVhZDM2"),
    ("learning36kitten36", "bGVhcm5pbmczNmtpdHRlbjM2"),
    ("learning36sitting36", "bGVhcm5pbmczNnNpdHRpbmczNg"),
    ("learning36agent36", "bGVhcm5pbmczNmFnZW50MzY"),
    ("model36agent36", "bW9kZWwzNmFnZW50MzY"),
    ("model36angle36", "bW9kZWwzNmFuZ2xlMzY"),
    ("model36universe36", "bW9kZWwzNnVuaXZlcnNlMzY"),
    ("model36memory36", "bW9kZWwzNm1lbW9yeTM2"),
    ("token36memory36", "dG9rZW4zNm1lbW9yeTM2"),
    ("token36stream36", "dG9rZW4zNnN0cmVhbTM2"),
    ("token36context36", "dG9rZW4zNmNvbnRleHQzNg"),
    ("token36knowledge36", "dG9rZW4zNmtub3dsZWRnZTM2"),
    ("prompt36knowledge36", "cHJvbXB0MzZrbm93bGVkZ2UzNg"),
    ("prompt36vector36", "cHJvbXB0MzZ2ZWN0b3IzNg"),
    ("prompt36processor36", "cHJvbXB0MzZwcm9jZXNzb3IzNg"),
    ("prompt36reasoning36", "cHJvbXB0MzZyZWFzb25pbmczNg"),
    ("session36reasoning36", "c2Vzc2lvbjM2cmVhc29uaW5nMzY"),
    ("session36machine36", "c2Vzc2lvbjM2bWFjaGluZTM2"),
    ("session36learning36", "c2Vzc2lvbjM2bGVhcm5pbmczNg"),
    ("session36model36", "c2Vzc2lvbjM2bW9kZWwzNg"),
    ("library36model36", "bGlicmFyeTM2bW9kZWwzNg"),
    ("library36token36", "bGlicmFyeTM2dG9rZW4zNg"),
    ("library36prompt36", "bGlicmFyeTM2cHJvbXB0MzY"),
    ("library36session36", "bGlicmFyeTM2c2Vzc2lvbjM2"),
    ("service36session36", "c2VydmljZTM2c2Vzc2lvbjM2"),
    ("service36library36", "c2VydmljZTM2bGlicmFyeTM2"),
    ("service36service36", "c2VydmljZTM2c2VydmljZTM2"),
    ("service36gateway36", "c2VydmljZTM2Z2F0ZXdheTM2"),
    ("gateway36gateway36", "Z2F0ZXdheTM2Z2F0ZXdheTM2"),
    ("gateway36storage36", "Z2F0ZXdheTM2c3RvcmFnZTM2"),
    ("gateway36network36", "Z2F0ZXdheTM2bmV0d29yazM2"),
    ("gateway36latency36", "Z2F0ZXdheTM2bGF0ZW5jeTM2"),
    ("storage36latency36", "c3RvcmFnZTM2bGF0ZW5jeTM2"),
    ("storage36buffer36", "c3RvcmFnZTM2YnVmZmVyMzY"),
    ("storage36queue36", "c3RvcmFnZTM2cXVldWUzNg"),
    ("storage36worker36", "c3RvcmFnZTM2d29ya2VyMzY"),
    ("network36worker36", "bmV0d29yazM2d29ya2VyMzY"),
    ("network36kernel36", "bmV0d29yazM2a2VybmVsMzY"),
    ("network36signal36", "bmV0d29yazM2c2lnbmFsMzY"),
    ("network36packet36", "bmV0d29yazM2cGFja2V0MzY"),
    ("latency36packet36", "bGF0ZW5jeTM2cGFja2V0MzY"),
    ("latency36router36", "bGF0ZW5jeTM2cm91dGVyMzY"),
    ("latency36cluster36", "bGF0ZW5jeTM2Y2x1c3RlcjM2"),
    ("latency36mirror36", "bGF0ZW5jeTM2bWlycm9yMzY"),
    ("buffer36mirror36", "YnVmZmVyMzZtaXJyb3IzNg"),
    ("buffer36filter36", "YnVmZmVyMzZmaWx0ZXIzNg"),
    ("buffer36ranking36", "YnVmZmVyMzZyYW5raW5nMzY"),
    ("buffer36encoding36", "YnVmZmVyMzZlbmNvZGluZzM2"),
    ("queue36encoding36", "cXVldWUzNmVuY29kaW5nMzY"),
    ("queue36mapping36", "cXVldWUzNm1hcHBpbmczNg"),
    ("queue36record36", "cXVldWUzNnJlY29yZDM2"),
    ("queue36candle36", "cXVldWUzNmNhbmRsZTM2"),
    ("worker36candle36", "d29ya2VyMzZjYW5kbGUzNg"),
    ("worker36thread36", "d29ya2VyMzZ0aHJlYWQzNg"),
    ("worker36kitten36", "d29ya2VyMzZraXR0ZW4zNg"),
    ("worker36sitting36", "d29ya2VyMzZzaXR0aW5nMzY"),
    ("kernel36sitting36", "a2VybmVsMzZzaXR0aW5nMzY"),
    ("kernel36agent36", "a2VybmVsMzZhZ2VudDM2"),
    ("kernel36angle36", "a2VybmVsMzZhbmdsZTM2"),
    ("kernel36universe36", "a2VybmVsMzZ1bml2ZXJzZTM2"),
    ("signal36universe36", "c2lnbmFsMzZ1bml2ZXJzZTM2"),
    ("signal36memory36", "c2lnbmFsMzZtZW1vcnkzNg"),
    ("signal36stream36", "c2lnbmFsMzZzdHJlYW0zNg"),
    ("signal36context36", "c2lnbmFsMzZjb250ZXh0MzY"),
    ("packet36context36", "cGFja2V0MzZjb250ZXh0MzY"),
    ("packet36knowledge36", "cGFja2V0MzZrbm93bGVkZ2UzNg"),
    ("packet36vector36", "cGFja2V0MzZ2ZWN0b3IzNg"),
    ("packet36processor36", "cGFja2V0MzZwcm9jZXNzb3IzNg"),
    ("router36processor36", "cm91dGVyMzZwcm9jZXNzb3IzNg"),
    ("router36reasoning36", "cm91dGVyMzZyZWFzb25pbmczNg"),
    ("router36machine36", "cm91dGVyMzZtYWNoaW5lMzY"),
    ("router36learning36", "cm91dGVyMzZsZWFybmluZzM2"),
    ("cluster36learning36", "Y2x1c3RlcjM2bGVhcm5pbmczNg"),
    ("cluster36model36", "Y2x1c3RlcjM2bW9kZWwzNg"),
    ("cluster36token36", "Y2x1c3RlcjM2dG9rZW4zNg"),
    ("cluster36prompt36", "Y2x1c3RlcjM2cHJvbXB0MzY"),
    ("mirror36prompt36", "bWlycm9yMzZwcm9tcHQzNg"),
    ("mirror36session36", "bWlycm9yMzZzZXNzaW9uMzY"),
    ("mirror36library36", "bWlycm9yMzZsaWJyYXJ5MzY"),
    ("mirror36service36", "bWlycm9yMzZzZXJ2aWNlMzY"),
    ("filter36service36", "ZmlsdGVyMzZzZXJ2aWNlMzY"),
    ("filter36gateway36", "ZmlsdGVyMzZnYXRld2F5MzY"),
    ("filter36storage36", "ZmlsdGVyMzZzdG9yYWdlMzY"),
    ("filter36network36", "ZmlsdGVyMzZuZXR3b3JrMzY"),
    ("ranking36network36", "cmFua2luZzM2bmV0d29yazM2"),
    ("ranking36latency36", "cmFua2luZzM2bGF0ZW5jeTM2"),
    ("ranking36buffer36", "cmFua2luZzM2YnVmZmVyMzY"),
    ("ranking36queue36", "cmFua2luZzM2cXVldWUzNg"),
    ("encoding36queue36", "ZW5jb2RpbmczNnF1ZXVlMzY"),
    ("encoding36worker36", "ZW5jb2RpbmczNndvcmtlcjM2"),
    ("encoding36kernel36", "ZW5jb2RpbmczNmtlcm5lbDM2"),
    ("encoding36signal36", "ZW5jb2RpbmczNnNpZ25hbDM2"),
    ("mapping36signal36", "bWFwcGluZzM2c2lnbmFsMzY"),
    ("mapping36packet36", "bWFwcGluZzM2cGFja2V0MzY"),
    ("mapping36router36", "bWFwcGluZzM2cm91dGVyMzY"),
    ("mapping36cluster36", "bWFwcGluZzM2Y2x1c3RlcjM2"),
    ("record36cluster36", "cmVjb3JkMzZjbHVzdGVyMzY"),
    ("record36mirror36", "cmVjb3JkMzZtaXJyb3IzNg"),
    ("record36filter36", "cmVjb3JkMzZmaWx0ZXIzNg"),
    ("record36ranking36", "cmVjb3JkMzZyYW5raW5nMzY"),
    ("candle36ranking36", "Y2FuZGxlMzZyYW5raW5nMzY"),
    ("candle36encoding36", "Y2FuZGxlMzZlbmNvZGluZzM2"),
    ("candle36mapping36", "Y2FuZGxlMzZtYXBwaW5nMzY"),
    ("candle36record36", "Y2FuZGxlMzZyZWNvcmQzNg"),
    ("thread36record36", "dGhyZWFkMzZyZWNvcmQzNg"),
    ("thread36candle36", "dGhyZWFkMzZjYW5kbGUzNg"),
    ("thread36thread36", "dGhyZWFkMzZ0aHJlYWQzNg"),
    ("thread36kitten36", "dGhyZWFkMzZraXR0ZW4zNg"),
    (
        "round 36: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMzY6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 36: agentuniverse is a framework for multi agents",
        "cm91bmQgMzY6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 36: knowledge stored as vectors enables retrieval",
        "cm91bmQgMzY6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 36: the processor reads the record then stops",
        "cm91bmQgMzY6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 36: a worker pulls the next task from the queue",
        "cm91bmQgMzY6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 36: signals travel through the network layer",
        "cm91bmQgMzY6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 36: the gateway routes each request by policy",
        "cm91bmQgMzY6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 36: memory grows until the buffer is full",
        "cm91bmQgMzY6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 36: the cluster mirrors every packet twice",
        "cm91bmQgMzY6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 36: ranking uses tokens learned from the corpus",
        "cm91bmQgMzY6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 36: a long session ends when the candle dies",
        "cm91bmQgMzY6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 36: encode the prompt then map the result",
        "cm91bmQgMzY6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 36: the kernel wakes the worker at dawn", "cm91bmQgMzY6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 36: service latency drops after the patch",
        "cm91bmQgMzY6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 36: the library caches every vector it sees",
        "cm91bmQgMzY6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 36: agents argue then the debate resolves",
        "cm91bmQgMzY6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 36: the filter keeps only strong matches",
        "cm91bmQgMzY6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 36: the model answers with a short reply",
        "cm91bmQgMzY6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 36: the recorder stores the reasoning trace",
        "cm91bmQgMzY6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 36: the angel watches the processor run", "cm91bmQgMzY6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 36: angle of the vector decides the match",
        "cm91bmQgMzY6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 36: the candle burns twice as long at night",
        "cm91bmQgMzY6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 36: a mirror of the universe in one line",
        "cm91bmQgMzY6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 36: the queue drains before the storm", "cm91bmQgMzY6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
