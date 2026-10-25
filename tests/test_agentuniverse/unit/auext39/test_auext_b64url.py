"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten39kitten39", "a2l0dGVuMzlraXR0ZW4zOQ"),
    ("kitten39sitting39", "a2l0dGVuMzlzaXR0aW5nMzk"),
    ("kitten39agent39", "a2l0dGVuMzlhZ2VudDM5"),
    ("kitten39angle39", "a2l0dGVuMzlhbmdsZTM5"),
    ("sitting39angle39", "c2l0dGluZzM5YW5nbGUzOQ"),
    ("sitting39universe39", "c2l0dGluZzM5dW5pdmVyc2UzOQ"),
    ("sitting39memory39", "c2l0dGluZzM5bWVtb3J5Mzk"),
    ("sitting39stream39", "c2l0dGluZzM5c3RyZWFtMzk"),
    ("agent39stream39", "YWdlbnQzOXN0cmVhbTM5"),
    ("agent39context39", "YWdlbnQzOWNvbnRleHQzOQ"),
    ("agent39knowledge39", "YWdlbnQzOWtub3dsZWRnZTM5"),
    ("agent39vector39", "YWdlbnQzOXZlY3RvcjM5"),
    ("angle39vector39", "YW5nbGUzOXZlY3RvcjM5"),
    ("angle39processor39", "YW5nbGUzOXByb2Nlc3NvcjM5"),
    ("angle39reasoning39", "YW5nbGUzOXJlYXNvbmluZzM5"),
    ("angle39machine39", "YW5nbGUzOW1hY2hpbmUzOQ"),
    ("universe39machine39", "dW5pdmVyc2UzOW1hY2hpbmUzOQ"),
    ("universe39learning39", "dW5pdmVyc2UzOWxlYXJuaW5nMzk"),
    ("universe39model39", "dW5pdmVyc2UzOW1vZGVsMzk"),
    ("universe39token39", "dW5pdmVyc2UzOXRva2VuMzk"),
    ("memory39token39", "bWVtb3J5Mzl0b2tlbjM5"),
    ("memory39prompt39", "bWVtb3J5Mzlwcm9tcHQzOQ"),
    ("memory39session39", "bWVtb3J5MzlzZXNzaW9uMzk"),
    ("memory39library39", "bWVtb3J5MzlsaWJyYXJ5Mzk"),
    ("stream39library39", "c3RyZWFtMzlsaWJyYXJ5Mzk"),
    ("stream39service39", "c3RyZWFtMzlzZXJ2aWNlMzk"),
    ("stream39gateway39", "c3RyZWFtMzlnYXRld2F5Mzk"),
    ("stream39storage39", "c3RyZWFtMzlzdG9yYWdlMzk"),
    ("context39storage39", "Y29udGV4dDM5c3RvcmFnZTM5"),
    ("context39network39", "Y29udGV4dDM5bmV0d29yazM5"),
    ("context39latency39", "Y29udGV4dDM5bGF0ZW5jeTM5"),
    ("context39buffer39", "Y29udGV4dDM5YnVmZmVyMzk"),
    ("knowledge39buffer39", "a25vd2xlZGdlMzlidWZmZXIzOQ"),
    ("knowledge39queue39", "a25vd2xlZGdlMzlxdWV1ZTM5"),
    ("knowledge39worker39", "a25vd2xlZGdlMzl3b3JrZXIzOQ"),
    ("knowledge39kernel39", "a25vd2xlZGdlMzlrZXJuZWwzOQ"),
    ("vector39kernel39", "dmVjdG9yMzlrZXJuZWwzOQ"),
    ("vector39signal39", "dmVjdG9yMzlzaWduYWwzOQ"),
    ("vector39packet39", "dmVjdG9yMzlwYWNrZXQzOQ"),
    ("vector39router39", "dmVjdG9yMzlyb3V0ZXIzOQ"),
    ("processor39router39", "cHJvY2Vzc29yMzlyb3V0ZXIzOQ"),
    ("processor39cluster39", "cHJvY2Vzc29yMzljbHVzdGVyMzk"),
    ("processor39mirror39", "cHJvY2Vzc29yMzltaXJyb3IzOQ"),
    ("processor39filter39", "cHJvY2Vzc29yMzlmaWx0ZXIzOQ"),
    ("reasoning39filter39", "cmVhc29uaW5nMzlmaWx0ZXIzOQ"),
    ("reasoning39ranking39", "cmVhc29uaW5nMzlyYW5raW5nMzk"),
    ("reasoning39encoding39", "cmVhc29uaW5nMzllbmNvZGluZzM5"),
    ("reasoning39mapping39", "cmVhc29uaW5nMzltYXBwaW5nMzk"),
    ("machine39mapping39", "bWFjaGluZTM5bWFwcGluZzM5"),
    ("machine39record39", "bWFjaGluZTM5cmVjb3JkMzk"),
    ("machine39candle39", "bWFjaGluZTM5Y2FuZGxlMzk"),
    ("machine39thread39", "bWFjaGluZTM5dGhyZWFkMzk"),
    ("learning39thread39", "bGVhcm5pbmczOXRocmVhZDM5"),
    ("learning39kitten39", "bGVhcm5pbmczOWtpdHRlbjM5"),
    ("learning39sitting39", "bGVhcm5pbmczOXNpdHRpbmczOQ"),
    ("learning39agent39", "bGVhcm5pbmczOWFnZW50Mzk"),
    ("model39agent39", "bW9kZWwzOWFnZW50Mzk"),
    ("model39angle39", "bW9kZWwzOWFuZ2xlMzk"),
    ("model39universe39", "bW9kZWwzOXVuaXZlcnNlMzk"),
    ("model39memory39", "bW9kZWwzOW1lbW9yeTM5"),
    ("token39memory39", "dG9rZW4zOW1lbW9yeTM5"),
    ("token39stream39", "dG9rZW4zOXN0cmVhbTM5"),
    ("token39context39", "dG9rZW4zOWNvbnRleHQzOQ"),
    ("token39knowledge39", "dG9rZW4zOWtub3dsZWRnZTM5"),
    ("prompt39knowledge39", "cHJvbXB0Mzlrbm93bGVkZ2UzOQ"),
    ("prompt39vector39", "cHJvbXB0Mzl2ZWN0b3IzOQ"),
    ("prompt39processor39", "cHJvbXB0Mzlwcm9jZXNzb3IzOQ"),
    ("prompt39reasoning39", "cHJvbXB0MzlyZWFzb25pbmczOQ"),
    ("session39reasoning39", "c2Vzc2lvbjM5cmVhc29uaW5nMzk"),
    ("session39machine39", "c2Vzc2lvbjM5bWFjaGluZTM5"),
    ("session39learning39", "c2Vzc2lvbjM5bGVhcm5pbmczOQ"),
    ("session39model39", "c2Vzc2lvbjM5bW9kZWwzOQ"),
    ("library39model39", "bGlicmFyeTM5bW9kZWwzOQ"),
    ("library39token39", "bGlicmFyeTM5dG9rZW4zOQ"),
    ("library39prompt39", "bGlicmFyeTM5cHJvbXB0Mzk"),
    ("library39session39", "bGlicmFyeTM5c2Vzc2lvbjM5"),
    ("service39session39", "c2VydmljZTM5c2Vzc2lvbjM5"),
    ("service39library39", "c2VydmljZTM5bGlicmFyeTM5"),
    ("service39service39", "c2VydmljZTM5c2VydmljZTM5"),
    ("service39gateway39", "c2VydmljZTM5Z2F0ZXdheTM5"),
    ("gateway39gateway39", "Z2F0ZXdheTM5Z2F0ZXdheTM5"),
    ("gateway39storage39", "Z2F0ZXdheTM5c3RvcmFnZTM5"),
    ("gateway39network39", "Z2F0ZXdheTM5bmV0d29yazM5"),
    ("gateway39latency39", "Z2F0ZXdheTM5bGF0ZW5jeTM5"),
    ("storage39latency39", "c3RvcmFnZTM5bGF0ZW5jeTM5"),
    ("storage39buffer39", "c3RvcmFnZTM5YnVmZmVyMzk"),
    ("storage39queue39", "c3RvcmFnZTM5cXVldWUzOQ"),
    ("storage39worker39", "c3RvcmFnZTM5d29ya2VyMzk"),
    ("network39worker39", "bmV0d29yazM5d29ya2VyMzk"),
    ("network39kernel39", "bmV0d29yazM5a2VybmVsMzk"),
    ("network39signal39", "bmV0d29yazM5c2lnbmFsMzk"),
    ("network39packet39", "bmV0d29yazM5cGFja2V0Mzk"),
    ("latency39packet39", "bGF0ZW5jeTM5cGFja2V0Mzk"),
    ("latency39router39", "bGF0ZW5jeTM5cm91dGVyMzk"),
    ("latency39cluster39", "bGF0ZW5jeTM5Y2x1c3RlcjM5"),
    ("latency39mirror39", "bGF0ZW5jeTM5bWlycm9yMzk"),
    ("buffer39mirror39", "YnVmZmVyMzltaXJyb3IzOQ"),
    ("buffer39filter39", "YnVmZmVyMzlmaWx0ZXIzOQ"),
    ("buffer39ranking39", "YnVmZmVyMzlyYW5raW5nMzk"),
    ("buffer39encoding39", "YnVmZmVyMzllbmNvZGluZzM5"),
    ("queue39encoding39", "cXVldWUzOWVuY29kaW5nMzk"),
    ("queue39mapping39", "cXVldWUzOW1hcHBpbmczOQ"),
    ("queue39record39", "cXVldWUzOXJlY29yZDM5"),
    ("queue39candle39", "cXVldWUzOWNhbmRsZTM5"),
    ("worker39candle39", "d29ya2VyMzljYW5kbGUzOQ"),
    ("worker39thread39", "d29ya2VyMzl0aHJlYWQzOQ"),
    ("worker39kitten39", "d29ya2VyMzlraXR0ZW4zOQ"),
    ("worker39sitting39", "d29ya2VyMzlzaXR0aW5nMzk"),
    ("kernel39sitting39", "a2VybmVsMzlzaXR0aW5nMzk"),
    ("kernel39agent39", "a2VybmVsMzlhZ2VudDM5"),
    ("kernel39angle39", "a2VybmVsMzlhbmdsZTM5"),
    ("kernel39universe39", "a2VybmVsMzl1bml2ZXJzZTM5"),
    ("signal39universe39", "c2lnbmFsMzl1bml2ZXJzZTM5"),
    ("signal39memory39", "c2lnbmFsMzltZW1vcnkzOQ"),
    ("signal39stream39", "c2lnbmFsMzlzdHJlYW0zOQ"),
    ("signal39context39", "c2lnbmFsMzljb250ZXh0Mzk"),
    ("packet39context39", "cGFja2V0Mzljb250ZXh0Mzk"),
    ("packet39knowledge39", "cGFja2V0Mzlrbm93bGVkZ2UzOQ"),
    ("packet39vector39", "cGFja2V0Mzl2ZWN0b3IzOQ"),
    ("packet39processor39", "cGFja2V0Mzlwcm9jZXNzb3IzOQ"),
    ("router39processor39", "cm91dGVyMzlwcm9jZXNzb3IzOQ"),
    ("router39reasoning39", "cm91dGVyMzlyZWFzb25pbmczOQ"),
    ("router39machine39", "cm91dGVyMzltYWNoaW5lMzk"),
    ("router39learning39", "cm91dGVyMzlsZWFybmluZzM5"),
    ("cluster39learning39", "Y2x1c3RlcjM5bGVhcm5pbmczOQ"),
    ("cluster39model39", "Y2x1c3RlcjM5bW9kZWwzOQ"),
    ("cluster39token39", "Y2x1c3RlcjM5dG9rZW4zOQ"),
    ("cluster39prompt39", "Y2x1c3RlcjM5cHJvbXB0Mzk"),
    ("mirror39prompt39", "bWlycm9yMzlwcm9tcHQzOQ"),
    ("mirror39session39", "bWlycm9yMzlzZXNzaW9uMzk"),
    ("mirror39library39", "bWlycm9yMzlsaWJyYXJ5Mzk"),
    ("mirror39service39", "bWlycm9yMzlzZXJ2aWNlMzk"),
    ("filter39service39", "ZmlsdGVyMzlzZXJ2aWNlMzk"),
    ("filter39gateway39", "ZmlsdGVyMzlnYXRld2F5Mzk"),
    ("filter39storage39", "ZmlsdGVyMzlzdG9yYWdlMzk"),
    ("filter39network39", "ZmlsdGVyMzluZXR3b3JrMzk"),
    ("ranking39network39", "cmFua2luZzM5bmV0d29yazM5"),
    ("ranking39latency39", "cmFua2luZzM5bGF0ZW5jeTM5"),
    ("ranking39buffer39", "cmFua2luZzM5YnVmZmVyMzk"),
    ("ranking39queue39", "cmFua2luZzM5cXVldWUzOQ"),
    ("encoding39queue39", "ZW5jb2RpbmczOXF1ZXVlMzk"),
    ("encoding39worker39", "ZW5jb2RpbmczOXdvcmtlcjM5"),
    ("encoding39kernel39", "ZW5jb2RpbmczOWtlcm5lbDM5"),
    ("encoding39signal39", "ZW5jb2RpbmczOXNpZ25hbDM5"),
    ("mapping39signal39", "bWFwcGluZzM5c2lnbmFsMzk"),
    ("mapping39packet39", "bWFwcGluZzM5cGFja2V0Mzk"),
    ("mapping39router39", "bWFwcGluZzM5cm91dGVyMzk"),
    ("mapping39cluster39", "bWFwcGluZzM5Y2x1c3RlcjM5"),
    ("record39cluster39", "cmVjb3JkMzljbHVzdGVyMzk"),
    ("record39mirror39", "cmVjb3JkMzltaXJyb3IzOQ"),
    ("record39filter39", "cmVjb3JkMzlmaWx0ZXIzOQ"),
    ("record39ranking39", "cmVjb3JkMzlyYW5raW5nMzk"),
    ("candle39ranking39", "Y2FuZGxlMzlyYW5raW5nMzk"),
    ("candle39encoding39", "Y2FuZGxlMzllbmNvZGluZzM5"),
    ("candle39mapping39", "Y2FuZGxlMzltYXBwaW5nMzk"),
    ("candle39record39", "Y2FuZGxlMzlyZWNvcmQzOQ"),
    ("thread39record39", "dGhyZWFkMzlyZWNvcmQzOQ"),
    ("thread39candle39", "dGhyZWFkMzljYW5kbGUzOQ"),
    ("thread39thread39", "dGhyZWFkMzl0aHJlYWQzOQ"),
    ("thread39kitten39", "dGhyZWFkMzlraXR0ZW4zOQ"),
    (
        "round 39: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMzk6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 39: agentuniverse is a framework for multi agents",
        "cm91bmQgMzk6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 39: knowledge stored as vectors enables retrieval",
        "cm91bmQgMzk6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 39: the processor reads the record then stops",
        "cm91bmQgMzk6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 39: a worker pulls the next task from the queue",
        "cm91bmQgMzk6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 39: signals travel through the network layer",
        "cm91bmQgMzk6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 39: the gateway routes each request by policy",
        "cm91bmQgMzk6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 39: memory grows until the buffer is full",
        "cm91bmQgMzk6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 39: the cluster mirrors every packet twice",
        "cm91bmQgMzk6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 39: ranking uses tokens learned from the corpus",
        "cm91bmQgMzk6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 39: a long session ends when the candle dies",
        "cm91bmQgMzk6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 39: encode the prompt then map the result",
        "cm91bmQgMzk6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 39: the kernel wakes the worker at dawn", "cm91bmQgMzk6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 39: service latency drops after the patch",
        "cm91bmQgMzk6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 39: the library caches every vector it sees",
        "cm91bmQgMzk6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 39: agents argue then the debate resolves",
        "cm91bmQgMzk6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 39: the filter keeps only strong matches",
        "cm91bmQgMzk6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 39: the model answers with a short reply",
        "cm91bmQgMzk6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 39: the recorder stores the reasoning trace",
        "cm91bmQgMzk6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 39: the angel watches the processor run", "cm91bmQgMzk6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 39: angle of the vector decides the match",
        "cm91bmQgMzk6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 39: the candle burns twice as long at night",
        "cm91bmQgMzk6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 39: a mirror of the universe in one line",
        "cm91bmQgMzk6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 39: the queue drains before the storm", "cm91bmQgMzk6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
