"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten93kitten93", "a2l0dGVuOTNraXR0ZW45Mw"),
    ("kitten93sitting93", "a2l0dGVuOTNzaXR0aW5nOTM"),
    ("kitten93agent93", "a2l0dGVuOTNhZ2VudDkz"),
    ("kitten93angle93", "a2l0dGVuOTNhbmdsZTkz"),
    ("sitting93angle93", "c2l0dGluZzkzYW5nbGU5Mw"),
    ("sitting93universe93", "c2l0dGluZzkzdW5pdmVyc2U5Mw"),
    ("sitting93memory93", "c2l0dGluZzkzbWVtb3J5OTM"),
    ("sitting93stream93", "c2l0dGluZzkzc3RyZWFtOTM"),
    ("agent93stream93", "YWdlbnQ5M3N0cmVhbTkz"),
    ("agent93context93", "YWdlbnQ5M2NvbnRleHQ5Mw"),
    ("agent93knowledge93", "YWdlbnQ5M2tub3dsZWRnZTkz"),
    ("agent93vector93", "YWdlbnQ5M3ZlY3Rvcjkz"),
    ("angle93vector93", "YW5nbGU5M3ZlY3Rvcjkz"),
    ("angle93processor93", "YW5nbGU5M3Byb2Nlc3Nvcjkz"),
    ("angle93reasoning93", "YW5nbGU5M3JlYXNvbmluZzkz"),
    ("angle93machine93", "YW5nbGU5M21hY2hpbmU5Mw"),
    ("universe93machine93", "dW5pdmVyc2U5M21hY2hpbmU5Mw"),
    ("universe93learning93", "dW5pdmVyc2U5M2xlYXJuaW5nOTM"),
    ("universe93model93", "dW5pdmVyc2U5M21vZGVsOTM"),
    ("universe93token93", "dW5pdmVyc2U5M3Rva2VuOTM"),
    ("memory93token93", "bWVtb3J5OTN0b2tlbjkz"),
    ("memory93prompt93", "bWVtb3J5OTNwcm9tcHQ5Mw"),
    ("memory93session93", "bWVtb3J5OTNzZXNzaW9uOTM"),
    ("memory93library93", "bWVtb3J5OTNsaWJyYXJ5OTM"),
    ("stream93library93", "c3RyZWFtOTNsaWJyYXJ5OTM"),
    ("stream93service93", "c3RyZWFtOTNzZXJ2aWNlOTM"),
    ("stream93gateway93", "c3RyZWFtOTNnYXRld2F5OTM"),
    ("stream93storage93", "c3RyZWFtOTNzdG9yYWdlOTM"),
    ("context93storage93", "Y29udGV4dDkzc3RvcmFnZTkz"),
    ("context93network93", "Y29udGV4dDkzbmV0d29yazkz"),
    ("context93latency93", "Y29udGV4dDkzbGF0ZW5jeTkz"),
    ("context93buffer93", "Y29udGV4dDkzYnVmZmVyOTM"),
    ("knowledge93buffer93", "a25vd2xlZGdlOTNidWZmZXI5Mw"),
    ("knowledge93queue93", "a25vd2xlZGdlOTNxdWV1ZTkz"),
    ("knowledge93worker93", "a25vd2xlZGdlOTN3b3JrZXI5Mw"),
    ("knowledge93kernel93", "a25vd2xlZGdlOTNrZXJuZWw5Mw"),
    ("vector93kernel93", "dmVjdG9yOTNrZXJuZWw5Mw"),
    ("vector93signal93", "dmVjdG9yOTNzaWduYWw5Mw"),
    ("vector93packet93", "dmVjdG9yOTNwYWNrZXQ5Mw"),
    ("vector93router93", "dmVjdG9yOTNyb3V0ZXI5Mw"),
    ("processor93router93", "cHJvY2Vzc29yOTNyb3V0ZXI5Mw"),
    ("processor93cluster93", "cHJvY2Vzc29yOTNjbHVzdGVyOTM"),
    ("processor93mirror93", "cHJvY2Vzc29yOTNtaXJyb3I5Mw"),
    ("processor93filter93", "cHJvY2Vzc29yOTNmaWx0ZXI5Mw"),
    ("reasoning93filter93", "cmVhc29uaW5nOTNmaWx0ZXI5Mw"),
    ("reasoning93ranking93", "cmVhc29uaW5nOTNyYW5raW5nOTM"),
    ("reasoning93encoding93", "cmVhc29uaW5nOTNlbmNvZGluZzkz"),
    ("reasoning93mapping93", "cmVhc29uaW5nOTNtYXBwaW5nOTM"),
    ("machine93mapping93", "bWFjaGluZTkzbWFwcGluZzkz"),
    ("machine93record93", "bWFjaGluZTkzcmVjb3JkOTM"),
    ("machine93candle93", "bWFjaGluZTkzY2FuZGxlOTM"),
    ("machine93thread93", "bWFjaGluZTkzdGhyZWFkOTM"),
    ("learning93thread93", "bGVhcm5pbmc5M3RocmVhZDkz"),
    ("learning93kitten93", "bGVhcm5pbmc5M2tpdHRlbjkz"),
    ("learning93sitting93", "bGVhcm5pbmc5M3NpdHRpbmc5Mw"),
    ("learning93agent93", "bGVhcm5pbmc5M2FnZW50OTM"),
    ("model93agent93", "bW9kZWw5M2FnZW50OTM"),
    ("model93angle93", "bW9kZWw5M2FuZ2xlOTM"),
    ("model93universe93", "bW9kZWw5M3VuaXZlcnNlOTM"),
    ("model93memory93", "bW9kZWw5M21lbW9yeTkz"),
    ("token93memory93", "dG9rZW45M21lbW9yeTkz"),
    ("token93stream93", "dG9rZW45M3N0cmVhbTkz"),
    ("token93context93", "dG9rZW45M2NvbnRleHQ5Mw"),
    ("token93knowledge93", "dG9rZW45M2tub3dsZWRnZTkz"),
    ("prompt93knowledge93", "cHJvbXB0OTNrbm93bGVkZ2U5Mw"),
    ("prompt93vector93", "cHJvbXB0OTN2ZWN0b3I5Mw"),
    ("prompt93processor93", "cHJvbXB0OTNwcm9jZXNzb3I5Mw"),
    ("prompt93reasoning93", "cHJvbXB0OTNyZWFzb25pbmc5Mw"),
    ("session93reasoning93", "c2Vzc2lvbjkzcmVhc29uaW5nOTM"),
    ("session93machine93", "c2Vzc2lvbjkzbWFjaGluZTkz"),
    ("session93learning93", "c2Vzc2lvbjkzbGVhcm5pbmc5Mw"),
    ("session93model93", "c2Vzc2lvbjkzbW9kZWw5Mw"),
    ("library93model93", "bGlicmFyeTkzbW9kZWw5Mw"),
    ("library93token93", "bGlicmFyeTkzdG9rZW45Mw"),
    ("library93prompt93", "bGlicmFyeTkzcHJvbXB0OTM"),
    ("library93session93", "bGlicmFyeTkzc2Vzc2lvbjkz"),
    ("service93session93", "c2VydmljZTkzc2Vzc2lvbjkz"),
    ("service93library93", "c2VydmljZTkzbGlicmFyeTkz"),
    ("service93service93", "c2VydmljZTkzc2VydmljZTkz"),
    ("service93gateway93", "c2VydmljZTkzZ2F0ZXdheTkz"),
    ("gateway93gateway93", "Z2F0ZXdheTkzZ2F0ZXdheTkz"),
    ("gateway93storage93", "Z2F0ZXdheTkzc3RvcmFnZTkz"),
    ("gateway93network93", "Z2F0ZXdheTkzbmV0d29yazkz"),
    ("gateway93latency93", "Z2F0ZXdheTkzbGF0ZW5jeTkz"),
    ("storage93latency93", "c3RvcmFnZTkzbGF0ZW5jeTkz"),
    ("storage93buffer93", "c3RvcmFnZTkzYnVmZmVyOTM"),
    ("storage93queue93", "c3RvcmFnZTkzcXVldWU5Mw"),
    ("storage93worker93", "c3RvcmFnZTkzd29ya2VyOTM"),
    ("network93worker93", "bmV0d29yazkzd29ya2VyOTM"),
    ("network93kernel93", "bmV0d29yazkza2VybmVsOTM"),
    ("network93signal93", "bmV0d29yazkzc2lnbmFsOTM"),
    ("network93packet93", "bmV0d29yazkzcGFja2V0OTM"),
    ("latency93packet93", "bGF0ZW5jeTkzcGFja2V0OTM"),
    ("latency93router93", "bGF0ZW5jeTkzcm91dGVyOTM"),
    ("latency93cluster93", "bGF0ZW5jeTkzY2x1c3Rlcjkz"),
    ("latency93mirror93", "bGF0ZW5jeTkzbWlycm9yOTM"),
    ("buffer93mirror93", "YnVmZmVyOTNtaXJyb3I5Mw"),
    ("buffer93filter93", "YnVmZmVyOTNmaWx0ZXI5Mw"),
    ("buffer93ranking93", "YnVmZmVyOTNyYW5raW5nOTM"),
    ("buffer93encoding93", "YnVmZmVyOTNlbmNvZGluZzkz"),
    ("queue93encoding93", "cXVldWU5M2VuY29kaW5nOTM"),
    ("queue93mapping93", "cXVldWU5M21hcHBpbmc5Mw"),
    ("queue93record93", "cXVldWU5M3JlY29yZDkz"),
    ("queue93candle93", "cXVldWU5M2NhbmRsZTkz"),
    ("worker93candle93", "d29ya2VyOTNjYW5kbGU5Mw"),
    ("worker93thread93", "d29ya2VyOTN0aHJlYWQ5Mw"),
    ("worker93kitten93", "d29ya2VyOTNraXR0ZW45Mw"),
    ("worker93sitting93", "d29ya2VyOTNzaXR0aW5nOTM"),
    ("kernel93sitting93", "a2VybmVsOTNzaXR0aW5nOTM"),
    ("kernel93agent93", "a2VybmVsOTNhZ2VudDkz"),
    ("kernel93angle93", "a2VybmVsOTNhbmdsZTkz"),
    ("kernel93universe93", "a2VybmVsOTN1bml2ZXJzZTkz"),
    ("signal93universe93", "c2lnbmFsOTN1bml2ZXJzZTkz"),
    ("signal93memory93", "c2lnbmFsOTNtZW1vcnk5Mw"),
    ("signal93stream93", "c2lnbmFsOTNzdHJlYW05Mw"),
    ("signal93context93", "c2lnbmFsOTNjb250ZXh0OTM"),
    ("packet93context93", "cGFja2V0OTNjb250ZXh0OTM"),
    ("packet93knowledge93", "cGFja2V0OTNrbm93bGVkZ2U5Mw"),
    ("packet93vector93", "cGFja2V0OTN2ZWN0b3I5Mw"),
    ("packet93processor93", "cGFja2V0OTNwcm9jZXNzb3I5Mw"),
    ("router93processor93", "cm91dGVyOTNwcm9jZXNzb3I5Mw"),
    ("router93reasoning93", "cm91dGVyOTNyZWFzb25pbmc5Mw"),
    ("router93machine93", "cm91dGVyOTNtYWNoaW5lOTM"),
    ("router93learning93", "cm91dGVyOTNsZWFybmluZzkz"),
    ("cluster93learning93", "Y2x1c3RlcjkzbGVhcm5pbmc5Mw"),
    ("cluster93model93", "Y2x1c3RlcjkzbW9kZWw5Mw"),
    ("cluster93token93", "Y2x1c3RlcjkzdG9rZW45Mw"),
    ("cluster93prompt93", "Y2x1c3RlcjkzcHJvbXB0OTM"),
    ("mirror93prompt93", "bWlycm9yOTNwcm9tcHQ5Mw"),
    ("mirror93session93", "bWlycm9yOTNzZXNzaW9uOTM"),
    ("mirror93library93", "bWlycm9yOTNsaWJyYXJ5OTM"),
    ("mirror93service93", "bWlycm9yOTNzZXJ2aWNlOTM"),
    ("filter93service93", "ZmlsdGVyOTNzZXJ2aWNlOTM"),
    ("filter93gateway93", "ZmlsdGVyOTNnYXRld2F5OTM"),
    ("filter93storage93", "ZmlsdGVyOTNzdG9yYWdlOTM"),
    ("filter93network93", "ZmlsdGVyOTNuZXR3b3JrOTM"),
    ("ranking93network93", "cmFua2luZzkzbmV0d29yazkz"),
    ("ranking93latency93", "cmFua2luZzkzbGF0ZW5jeTkz"),
    ("ranking93buffer93", "cmFua2luZzkzYnVmZmVyOTM"),
    ("ranking93queue93", "cmFua2luZzkzcXVldWU5Mw"),
    ("encoding93queue93", "ZW5jb2Rpbmc5M3F1ZXVlOTM"),
    ("encoding93worker93", "ZW5jb2Rpbmc5M3dvcmtlcjkz"),
    ("encoding93kernel93", "ZW5jb2Rpbmc5M2tlcm5lbDkz"),
    ("encoding93signal93", "ZW5jb2Rpbmc5M3NpZ25hbDkz"),
    ("mapping93signal93", "bWFwcGluZzkzc2lnbmFsOTM"),
    ("mapping93packet93", "bWFwcGluZzkzcGFja2V0OTM"),
    ("mapping93router93", "bWFwcGluZzkzcm91dGVyOTM"),
    ("mapping93cluster93", "bWFwcGluZzkzY2x1c3Rlcjkz"),
    ("record93cluster93", "cmVjb3JkOTNjbHVzdGVyOTM"),
    ("record93mirror93", "cmVjb3JkOTNtaXJyb3I5Mw"),
    ("record93filter93", "cmVjb3JkOTNmaWx0ZXI5Mw"),
    ("record93ranking93", "cmVjb3JkOTNyYW5raW5nOTM"),
    ("candle93ranking93", "Y2FuZGxlOTNyYW5raW5nOTM"),
    ("candle93encoding93", "Y2FuZGxlOTNlbmNvZGluZzkz"),
    ("candle93mapping93", "Y2FuZGxlOTNtYXBwaW5nOTM"),
    ("candle93record93", "Y2FuZGxlOTNyZWNvcmQ5Mw"),
    ("thread93record93", "dGhyZWFkOTNyZWNvcmQ5Mw"),
    ("thread93candle93", "dGhyZWFkOTNjYW5kbGU5Mw"),
    ("thread93thread93", "dGhyZWFkOTN0aHJlYWQ5Mw"),
    ("thread93kitten93", "dGhyZWFkOTNraXR0ZW45Mw"),
    (
        "round 93: the quick brown fox jumps over the lazy dog",
        "cm91bmQgOTM6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 93: agentuniverse is a framework for multi agents",
        "cm91bmQgOTM6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 93: knowledge stored as vectors enables retrieval",
        "cm91bmQgOTM6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 93: the processor reads the record then stops",
        "cm91bmQgOTM6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 93: a worker pulls the next task from the queue",
        "cm91bmQgOTM6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 93: signals travel through the network layer",
        "cm91bmQgOTM6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 93: the gateway routes each request by policy",
        "cm91bmQgOTM6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 93: memory grows until the buffer is full",
        "cm91bmQgOTM6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 93: the cluster mirrors every packet twice",
        "cm91bmQgOTM6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 93: ranking uses tokens learned from the corpus",
        "cm91bmQgOTM6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 93: a long session ends when the candle dies",
        "cm91bmQgOTM6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 93: encode the prompt then map the result",
        "cm91bmQgOTM6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 93: the kernel wakes the worker at dawn", "cm91bmQgOTM6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 93: service latency drops after the patch",
        "cm91bmQgOTM6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 93: the library caches every vector it sees",
        "cm91bmQgOTM6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 93: agents argue then the debate resolves",
        "cm91bmQgOTM6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 93: the filter keeps only strong matches",
        "cm91bmQgOTM6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 93: the model answers with a short reply",
        "cm91bmQgOTM6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 93: the recorder stores the reasoning trace",
        "cm91bmQgOTM6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 93: the angel watches the processor run", "cm91bmQgOTM6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 93: angle of the vector decides the match",
        "cm91bmQgOTM6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 93: the candle burns twice as long at night",
        "cm91bmQgOTM6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 93: a mirror of the universe in one line",
        "cm91bmQgOTM6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 93: the queue drains before the storm", "cm91bmQgOTM6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
