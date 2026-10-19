"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten9kitten9", "a2l0dGVuOWtpdHRlbjk"),
    ("kitten9sitting9", "a2l0dGVuOXNpdHRpbmc5"),
    ("kitten9agent9", "a2l0dGVuOWFnZW50OQ"),
    ("kitten9angle9", "a2l0dGVuOWFuZ2xlOQ"),
    ("sitting9angle9", "c2l0dGluZzlhbmdsZTk"),
    ("sitting9universe9", "c2l0dGluZzl1bml2ZXJzZTk"),
    ("sitting9memory9", "c2l0dGluZzltZW1vcnk5"),
    ("sitting9stream9", "c2l0dGluZzlzdHJlYW05"),
    ("agent9stream9", "YWdlbnQ5c3RyZWFtOQ"),
    ("agent9context9", "YWdlbnQ5Y29udGV4dDk"),
    ("agent9knowledge9", "YWdlbnQ5a25vd2xlZGdlOQ"),
    ("agent9vector9", "YWdlbnQ5dmVjdG9yOQ"),
    ("angle9vector9", "YW5nbGU5dmVjdG9yOQ"),
    ("angle9processor9", "YW5nbGU5cHJvY2Vzc29yOQ"),
    ("angle9reasoning9", "YW5nbGU5cmVhc29uaW5nOQ"),
    ("angle9machine9", "YW5nbGU5bWFjaGluZTk"),
    ("universe9machine9", "dW5pdmVyc2U5bWFjaGluZTk"),
    ("universe9learning9", "dW5pdmVyc2U5bGVhcm5pbmc5"),
    ("universe9model9", "dW5pdmVyc2U5bW9kZWw5"),
    ("universe9token9", "dW5pdmVyc2U5dG9rZW45"),
    ("memory9token9", "bWVtb3J5OXRva2VuOQ"),
    ("memory9prompt9", "bWVtb3J5OXByb21wdDk"),
    ("memory9session9", "bWVtb3J5OXNlc3Npb245"),
    ("memory9library9", "bWVtb3J5OWxpYnJhcnk5"),
    ("stream9library9", "c3RyZWFtOWxpYnJhcnk5"),
    ("stream9service9", "c3RyZWFtOXNlcnZpY2U5"),
    ("stream9gateway9", "c3RyZWFtOWdhdGV3YXk5"),
    ("stream9storage9", "c3RyZWFtOXN0b3JhZ2U5"),
    ("context9storage9", "Y29udGV4dDlzdG9yYWdlOQ"),
    ("context9network9", "Y29udGV4dDluZXR3b3JrOQ"),
    ("context9latency9", "Y29udGV4dDlsYXRlbmN5OQ"),
    ("context9buffer9", "Y29udGV4dDlidWZmZXI5"),
    ("knowledge9buffer9", "a25vd2xlZGdlOWJ1ZmZlcjk"),
    ("knowledge9queue9", "a25vd2xlZGdlOXF1ZXVlOQ"),
    ("knowledge9worker9", "a25vd2xlZGdlOXdvcmtlcjk"),
    ("knowledge9kernel9", "a25vd2xlZGdlOWtlcm5lbDk"),
    ("vector9kernel9", "dmVjdG9yOWtlcm5lbDk"),
    ("vector9signal9", "dmVjdG9yOXNpZ25hbDk"),
    ("vector9packet9", "dmVjdG9yOXBhY2tldDk"),
    ("vector9router9", "dmVjdG9yOXJvdXRlcjk"),
    ("processor9router9", "cHJvY2Vzc29yOXJvdXRlcjk"),
    ("processor9cluster9", "cHJvY2Vzc29yOWNsdXN0ZXI5"),
    ("processor9mirror9", "cHJvY2Vzc29yOW1pcnJvcjk"),
    ("processor9filter9", "cHJvY2Vzc29yOWZpbHRlcjk"),
    ("reasoning9filter9", "cmVhc29uaW5nOWZpbHRlcjk"),
    ("reasoning9ranking9", "cmVhc29uaW5nOXJhbmtpbmc5"),
    ("reasoning9encoding9", "cmVhc29uaW5nOWVuY29kaW5nOQ"),
    ("reasoning9mapping9", "cmVhc29uaW5nOW1hcHBpbmc5"),
    ("machine9mapping9", "bWFjaGluZTltYXBwaW5nOQ"),
    ("machine9record9", "bWFjaGluZTlyZWNvcmQ5"),
    ("machine9candle9", "bWFjaGluZTljYW5kbGU5"),
    ("machine9thread9", "bWFjaGluZTl0aHJlYWQ5"),
    ("learning9thread9", "bGVhcm5pbmc5dGhyZWFkOQ"),
    ("learning9kitten9", "bGVhcm5pbmc5a2l0dGVuOQ"),
    ("learning9sitting9", "bGVhcm5pbmc5c2l0dGluZzk"),
    ("learning9agent9", "bGVhcm5pbmc5YWdlbnQ5"),
    ("model9agent9", "bW9kZWw5YWdlbnQ5"),
    ("model9angle9", "bW9kZWw5YW5nbGU5"),
    ("model9universe9", "bW9kZWw5dW5pdmVyc2U5"),
    ("model9memory9", "bW9kZWw5bWVtb3J5OQ"),
    ("token9memory9", "dG9rZW45bWVtb3J5OQ"),
    ("token9stream9", "dG9rZW45c3RyZWFtOQ"),
    ("token9context9", "dG9rZW45Y29udGV4dDk"),
    ("token9knowledge9", "dG9rZW45a25vd2xlZGdlOQ"),
    ("prompt9knowledge9", "cHJvbXB0OWtub3dsZWRnZTk"),
    ("prompt9vector9", "cHJvbXB0OXZlY3Rvcjk"),
    ("prompt9processor9", "cHJvbXB0OXByb2Nlc3Nvcjk"),
    ("prompt9reasoning9", "cHJvbXB0OXJlYXNvbmluZzk"),
    ("session9reasoning9", "c2Vzc2lvbjlyZWFzb25pbmc5"),
    ("session9machine9", "c2Vzc2lvbjltYWNoaW5lOQ"),
    ("session9learning9", "c2Vzc2lvbjlsZWFybmluZzk"),
    ("session9model9", "c2Vzc2lvbjltb2RlbDk"),
    ("library9model9", "bGlicmFyeTltb2RlbDk"),
    ("library9token9", "bGlicmFyeTl0b2tlbjk"),
    ("library9prompt9", "bGlicmFyeTlwcm9tcHQ5"),
    ("library9session9", "bGlicmFyeTlzZXNzaW9uOQ"),
    ("service9session9", "c2VydmljZTlzZXNzaW9uOQ"),
    ("service9library9", "c2VydmljZTlsaWJyYXJ5OQ"),
    ("service9service9", "c2VydmljZTlzZXJ2aWNlOQ"),
    ("service9gateway9", "c2VydmljZTlnYXRld2F5OQ"),
    ("gateway9gateway9", "Z2F0ZXdheTlnYXRld2F5OQ"),
    ("gateway9storage9", "Z2F0ZXdheTlzdG9yYWdlOQ"),
    ("gateway9network9", "Z2F0ZXdheTluZXR3b3JrOQ"),
    ("gateway9latency9", "Z2F0ZXdheTlsYXRlbmN5OQ"),
    ("storage9latency9", "c3RvcmFnZTlsYXRlbmN5OQ"),
    ("storage9buffer9", "c3RvcmFnZTlidWZmZXI5"),
    ("storage9queue9", "c3RvcmFnZTlxdWV1ZTk"),
    ("storage9worker9", "c3RvcmFnZTl3b3JrZXI5"),
    ("network9worker9", "bmV0d29yazl3b3JrZXI5"),
    ("network9kernel9", "bmV0d29yazlrZXJuZWw5"),
    ("network9signal9", "bmV0d29yazlzaWduYWw5"),
    ("network9packet9", "bmV0d29yazlwYWNrZXQ5"),
    ("latency9packet9", "bGF0ZW5jeTlwYWNrZXQ5"),
    ("latency9router9", "bGF0ZW5jeTlyb3V0ZXI5"),
    ("latency9cluster9", "bGF0ZW5jeTljbHVzdGVyOQ"),
    ("latency9mirror9", "bGF0ZW5jeTltaXJyb3I5"),
    ("buffer9mirror9", "YnVmZmVyOW1pcnJvcjk"),
    ("buffer9filter9", "YnVmZmVyOWZpbHRlcjk"),
    ("buffer9ranking9", "YnVmZmVyOXJhbmtpbmc5"),
    ("buffer9encoding9", "YnVmZmVyOWVuY29kaW5nOQ"),
    ("queue9encoding9", "cXVldWU5ZW5jb2Rpbmc5"),
    ("queue9mapping9", "cXVldWU5bWFwcGluZzk"),
    ("queue9record9", "cXVldWU5cmVjb3JkOQ"),
    ("queue9candle9", "cXVldWU5Y2FuZGxlOQ"),
    ("worker9candle9", "d29ya2VyOWNhbmRsZTk"),
    ("worker9thread9", "d29ya2VyOXRocmVhZDk"),
    ("worker9kitten9", "d29ya2VyOWtpdHRlbjk"),
    ("worker9sitting9", "d29ya2VyOXNpdHRpbmc5"),
    ("kernel9sitting9", "a2VybmVsOXNpdHRpbmc5"),
    ("kernel9agent9", "a2VybmVsOWFnZW50OQ"),
    ("kernel9angle9", "a2VybmVsOWFuZ2xlOQ"),
    ("kernel9universe9", "a2VybmVsOXVuaXZlcnNlOQ"),
    ("signal9universe9", "c2lnbmFsOXVuaXZlcnNlOQ"),
    ("signal9memory9", "c2lnbmFsOW1lbW9yeTk"),
    ("signal9stream9", "c2lnbmFsOXN0cmVhbTk"),
    ("signal9context9", "c2lnbmFsOWNvbnRleHQ5"),
    ("packet9context9", "cGFja2V0OWNvbnRleHQ5"),
    ("packet9knowledge9", "cGFja2V0OWtub3dsZWRnZTk"),
    ("packet9vector9", "cGFja2V0OXZlY3Rvcjk"),
    ("packet9processor9", "cGFja2V0OXByb2Nlc3Nvcjk"),
    ("router9processor9", "cm91dGVyOXByb2Nlc3Nvcjk"),
    ("router9reasoning9", "cm91dGVyOXJlYXNvbmluZzk"),
    ("router9machine9", "cm91dGVyOW1hY2hpbmU5"),
    ("router9learning9", "cm91dGVyOWxlYXJuaW5nOQ"),
    ("cluster9learning9", "Y2x1c3RlcjlsZWFybmluZzk"),
    ("cluster9model9", "Y2x1c3Rlcjltb2RlbDk"),
    ("cluster9token9", "Y2x1c3Rlcjl0b2tlbjk"),
    ("cluster9prompt9", "Y2x1c3Rlcjlwcm9tcHQ5"),
    ("mirror9prompt9", "bWlycm9yOXByb21wdDk"),
    ("mirror9session9", "bWlycm9yOXNlc3Npb245"),
    ("mirror9library9", "bWlycm9yOWxpYnJhcnk5"),
    ("mirror9service9", "bWlycm9yOXNlcnZpY2U5"),
    ("filter9service9", "ZmlsdGVyOXNlcnZpY2U5"),
    ("filter9gateway9", "ZmlsdGVyOWdhdGV3YXk5"),
    ("filter9storage9", "ZmlsdGVyOXN0b3JhZ2U5"),
    ("filter9network9", "ZmlsdGVyOW5ldHdvcms5"),
    ("ranking9network9", "cmFua2luZzluZXR3b3JrOQ"),
    ("ranking9latency9", "cmFua2luZzlsYXRlbmN5OQ"),
    ("ranking9buffer9", "cmFua2luZzlidWZmZXI5"),
    ("ranking9queue9", "cmFua2luZzlxdWV1ZTk"),
    ("encoding9queue9", "ZW5jb2Rpbmc5cXVldWU5"),
    ("encoding9worker9", "ZW5jb2Rpbmc5d29ya2VyOQ"),
    ("encoding9kernel9", "ZW5jb2Rpbmc5a2VybmVsOQ"),
    ("encoding9signal9", "ZW5jb2Rpbmc5c2lnbmFsOQ"),
    ("mapping9signal9", "bWFwcGluZzlzaWduYWw5"),
    ("mapping9packet9", "bWFwcGluZzlwYWNrZXQ5"),
    ("mapping9router9", "bWFwcGluZzlyb3V0ZXI5"),
    ("mapping9cluster9", "bWFwcGluZzljbHVzdGVyOQ"),
    ("record9cluster9", "cmVjb3JkOWNsdXN0ZXI5"),
    ("record9mirror9", "cmVjb3JkOW1pcnJvcjk"),
    ("record9filter9", "cmVjb3JkOWZpbHRlcjk"),
    ("record9ranking9", "cmVjb3JkOXJhbmtpbmc5"),
    ("candle9ranking9", "Y2FuZGxlOXJhbmtpbmc5"),
    ("candle9encoding9", "Y2FuZGxlOWVuY29kaW5nOQ"),
    ("candle9mapping9", "Y2FuZGxlOW1hcHBpbmc5"),
    ("candle9record9", "Y2FuZGxlOXJlY29yZDk"),
    ("thread9record9", "dGhyZWFkOXJlY29yZDk"),
    ("thread9candle9", "dGhyZWFkOWNhbmRsZTk"),
    ("thread9thread9", "dGhyZWFkOXRocmVhZDk"),
    ("thread9kitten9", "dGhyZWFkOWtpdHRlbjk"),
    (
        "round 9: the quick brown fox jumps over the lazy dog",
        "cm91bmQgOTogdGhlIHF1aWNrIGJyb3duIGZveCBqdW1wcyBvdmVyIHRoZSBsYXp5IGRvZw",
    ),
    (
        "round 9: agentuniverse is a framework for multi agents",
        "cm91bmQgOTogYWdlbnR1bml2ZXJzZSBpcyBhIGZyYW1ld29yayBmb3IgbXVsdGkgYWdlbnRz",
    ),
    (
        "round 9: knowledge stored as vectors enables retrieval",
        "cm91bmQgOToga25vd2xlZGdlIHN0b3JlZCBhcyB2ZWN0b3JzIGVuYWJsZXMgcmV0cmlldmFs",
    ),
    (
        "round 9: the processor reads the record then stops",
        "cm91bmQgOTogdGhlIHByb2Nlc3NvciByZWFkcyB0aGUgcmVjb3JkIHRoZW4gc3RvcHM",
    ),
    (
        "round 9: a worker pulls the next task from the queue",
        "cm91bmQgOTogYSB3b3JrZXIgcHVsbHMgdGhlIG5leHQgdGFzayBmcm9tIHRoZSBxdWV1ZQ",
    ),
    (
        "round 9: signals travel through the network layer",
        "cm91bmQgOTogc2lnbmFscyB0cmF2ZWwgdGhyb3VnaCB0aGUgbmV0d29yayBsYXllcg",
    ),
    (
        "round 9: the gateway routes each request by policy",
        "cm91bmQgOTogdGhlIGdhdGV3YXkgcm91dGVzIGVhY2ggcmVxdWVzdCBieSBwb2xpY3k",
    ),
    (
        "round 9: memory grows until the buffer is full",
        "cm91bmQgOTogbWVtb3J5IGdyb3dzIHVudGlsIHRoZSBidWZmZXIgaXMgZnVsbA",
    ),
    (
        "round 9: the cluster mirrors every packet twice",
        "cm91bmQgOTogdGhlIGNsdXN0ZXIgbWlycm9ycyBldmVyeSBwYWNrZXQgdHdpY2U",
    ),
    (
        "round 9: ranking uses tokens learned from the corpus",
        "cm91bmQgOTogcmFua2luZyB1c2VzIHRva2VucyBsZWFybmVkIGZyb20gdGhlIGNvcnB1cw",
    ),
    (
        "round 9: a long session ends when the candle dies",
        "cm91bmQgOTogYSBsb25nIHNlc3Npb24gZW5kcyB3aGVuIHRoZSBjYW5kbGUgZGllcw",
    ),
    (
        "round 9: encode the prompt then map the result",
        "cm91bmQgOTogZW5jb2RlIHRoZSBwcm9tcHQgdGhlbiBtYXAgdGhlIHJlc3VsdA",
    ),
    ("round 9: the kernel wakes the worker at dawn", "cm91bmQgOTogdGhlIGtlcm5lbCB3YWtlcyB0aGUgd29ya2VyIGF0IGRhd24"),
    (
        "round 9: service latency drops after the patch",
        "cm91bmQgOTogc2VydmljZSBsYXRlbmN5IGRyb3BzIGFmdGVyIHRoZSBwYXRjaA",
    ),
    (
        "round 9: the library caches every vector it sees",
        "cm91bmQgOTogdGhlIGxpYnJhcnkgY2FjaGVzIGV2ZXJ5IHZlY3RvciBpdCBzZWVz",
    ),
    (
        "round 9: agents argue then the debate resolves",
        "cm91bmQgOTogYWdlbnRzIGFyZ3VlIHRoZW4gdGhlIGRlYmF0ZSByZXNvbHZlcw",
    ),
    ("round 9: the filter keeps only strong matches", "cm91bmQgOTogdGhlIGZpbHRlciBrZWVwcyBvbmx5IHN0cm9uZyBtYXRjaGVz"),
    ("round 9: the model answers with a short reply", "cm91bmQgOTogdGhlIG1vZGVsIGFuc3dlcnMgd2l0aCBhIHNob3J0IHJlcGx5"),
    (
        "round 9: the recorder stores the reasoning trace",
        "cm91bmQgOTogdGhlIHJlY29yZGVyIHN0b3JlcyB0aGUgcmVhc29uaW5nIHRyYWNl",
    ),
    ("round 9: the angel watches the processor run", "cm91bmQgOTogdGhlIGFuZ2VsIHdhdGNoZXMgdGhlIHByb2Nlc3NvciBydW4"),
    (
        "round 9: angle of the vector decides the match",
        "cm91bmQgOTogYW5nbGUgb2YgdGhlIHZlY3RvciBkZWNpZGVzIHRoZSBtYXRjaA",
    ),
    (
        "round 9: the candle burns twice as long at night",
        "cm91bmQgOTogdGhlIGNhbmRsZSBidXJucyB0d2ljZSBhcyBsb25nIGF0IG5pZ2h0",
    ),
    ("round 9: a mirror of the universe in one line", "cm91bmQgOTogYSBtaXJyb3Igb2YgdGhlIHVuaXZlcnNlIGluIG9uZSBsaW5l"),
    ("round 9: the queue drains before the storm", "cm91bmQgOTogdGhlIHF1ZXVlIGRyYWlucyBiZWZvcmUgdGhlIHN0b3Jt"),
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
