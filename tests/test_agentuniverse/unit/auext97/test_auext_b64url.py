"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten97kitten97", "a2l0dGVuOTdraXR0ZW45Nw"),
    ("kitten97sitting97", "a2l0dGVuOTdzaXR0aW5nOTc"),
    ("kitten97agent97", "a2l0dGVuOTdhZ2VudDk3"),
    ("kitten97angle97", "a2l0dGVuOTdhbmdsZTk3"),
    ("sitting97angle97", "c2l0dGluZzk3YW5nbGU5Nw"),
    ("sitting97universe97", "c2l0dGluZzk3dW5pdmVyc2U5Nw"),
    ("sitting97memory97", "c2l0dGluZzk3bWVtb3J5OTc"),
    ("sitting97stream97", "c2l0dGluZzk3c3RyZWFtOTc"),
    ("agent97stream97", "YWdlbnQ5N3N0cmVhbTk3"),
    ("agent97context97", "YWdlbnQ5N2NvbnRleHQ5Nw"),
    ("agent97knowledge97", "YWdlbnQ5N2tub3dsZWRnZTk3"),
    ("agent97vector97", "YWdlbnQ5N3ZlY3Rvcjk3"),
    ("angle97vector97", "YW5nbGU5N3ZlY3Rvcjk3"),
    ("angle97processor97", "YW5nbGU5N3Byb2Nlc3Nvcjk3"),
    ("angle97reasoning97", "YW5nbGU5N3JlYXNvbmluZzk3"),
    ("angle97machine97", "YW5nbGU5N21hY2hpbmU5Nw"),
    ("universe97machine97", "dW5pdmVyc2U5N21hY2hpbmU5Nw"),
    ("universe97learning97", "dW5pdmVyc2U5N2xlYXJuaW5nOTc"),
    ("universe97model97", "dW5pdmVyc2U5N21vZGVsOTc"),
    ("universe97token97", "dW5pdmVyc2U5N3Rva2VuOTc"),
    ("memory97token97", "bWVtb3J5OTd0b2tlbjk3"),
    ("memory97prompt97", "bWVtb3J5OTdwcm9tcHQ5Nw"),
    ("memory97session97", "bWVtb3J5OTdzZXNzaW9uOTc"),
    ("memory97library97", "bWVtb3J5OTdsaWJyYXJ5OTc"),
    ("stream97library97", "c3RyZWFtOTdsaWJyYXJ5OTc"),
    ("stream97service97", "c3RyZWFtOTdzZXJ2aWNlOTc"),
    ("stream97gateway97", "c3RyZWFtOTdnYXRld2F5OTc"),
    ("stream97storage97", "c3RyZWFtOTdzdG9yYWdlOTc"),
    ("context97storage97", "Y29udGV4dDk3c3RvcmFnZTk3"),
    ("context97network97", "Y29udGV4dDk3bmV0d29yazk3"),
    ("context97latency97", "Y29udGV4dDk3bGF0ZW5jeTk3"),
    ("context97buffer97", "Y29udGV4dDk3YnVmZmVyOTc"),
    ("knowledge97buffer97", "a25vd2xlZGdlOTdidWZmZXI5Nw"),
    ("knowledge97queue97", "a25vd2xlZGdlOTdxdWV1ZTk3"),
    ("knowledge97worker97", "a25vd2xlZGdlOTd3b3JrZXI5Nw"),
    ("knowledge97kernel97", "a25vd2xlZGdlOTdrZXJuZWw5Nw"),
    ("vector97kernel97", "dmVjdG9yOTdrZXJuZWw5Nw"),
    ("vector97signal97", "dmVjdG9yOTdzaWduYWw5Nw"),
    ("vector97packet97", "dmVjdG9yOTdwYWNrZXQ5Nw"),
    ("vector97router97", "dmVjdG9yOTdyb3V0ZXI5Nw"),
    ("processor97router97", "cHJvY2Vzc29yOTdyb3V0ZXI5Nw"),
    ("processor97cluster97", "cHJvY2Vzc29yOTdjbHVzdGVyOTc"),
    ("processor97mirror97", "cHJvY2Vzc29yOTdtaXJyb3I5Nw"),
    ("processor97filter97", "cHJvY2Vzc29yOTdmaWx0ZXI5Nw"),
    ("reasoning97filter97", "cmVhc29uaW5nOTdmaWx0ZXI5Nw"),
    ("reasoning97ranking97", "cmVhc29uaW5nOTdyYW5raW5nOTc"),
    ("reasoning97encoding97", "cmVhc29uaW5nOTdlbmNvZGluZzk3"),
    ("reasoning97mapping97", "cmVhc29uaW5nOTdtYXBwaW5nOTc"),
    ("machine97mapping97", "bWFjaGluZTk3bWFwcGluZzk3"),
    ("machine97record97", "bWFjaGluZTk3cmVjb3JkOTc"),
    ("machine97candle97", "bWFjaGluZTk3Y2FuZGxlOTc"),
    ("machine97thread97", "bWFjaGluZTk3dGhyZWFkOTc"),
    ("learning97thread97", "bGVhcm5pbmc5N3RocmVhZDk3"),
    ("learning97kitten97", "bGVhcm5pbmc5N2tpdHRlbjk3"),
    ("learning97sitting97", "bGVhcm5pbmc5N3NpdHRpbmc5Nw"),
    ("learning97agent97", "bGVhcm5pbmc5N2FnZW50OTc"),
    ("model97agent97", "bW9kZWw5N2FnZW50OTc"),
    ("model97angle97", "bW9kZWw5N2FuZ2xlOTc"),
    ("model97universe97", "bW9kZWw5N3VuaXZlcnNlOTc"),
    ("model97memory97", "bW9kZWw5N21lbW9yeTk3"),
    ("token97memory97", "dG9rZW45N21lbW9yeTk3"),
    ("token97stream97", "dG9rZW45N3N0cmVhbTk3"),
    ("token97context97", "dG9rZW45N2NvbnRleHQ5Nw"),
    ("token97knowledge97", "dG9rZW45N2tub3dsZWRnZTk3"),
    ("prompt97knowledge97", "cHJvbXB0OTdrbm93bGVkZ2U5Nw"),
    ("prompt97vector97", "cHJvbXB0OTd2ZWN0b3I5Nw"),
    ("prompt97processor97", "cHJvbXB0OTdwcm9jZXNzb3I5Nw"),
    ("prompt97reasoning97", "cHJvbXB0OTdyZWFzb25pbmc5Nw"),
    ("session97reasoning97", "c2Vzc2lvbjk3cmVhc29uaW5nOTc"),
    ("session97machine97", "c2Vzc2lvbjk3bWFjaGluZTk3"),
    ("session97learning97", "c2Vzc2lvbjk3bGVhcm5pbmc5Nw"),
    ("session97model97", "c2Vzc2lvbjk3bW9kZWw5Nw"),
    ("library97model97", "bGlicmFyeTk3bW9kZWw5Nw"),
    ("library97token97", "bGlicmFyeTk3dG9rZW45Nw"),
    ("library97prompt97", "bGlicmFyeTk3cHJvbXB0OTc"),
    ("library97session97", "bGlicmFyeTk3c2Vzc2lvbjk3"),
    ("service97session97", "c2VydmljZTk3c2Vzc2lvbjk3"),
    ("service97library97", "c2VydmljZTk3bGlicmFyeTk3"),
    ("service97service97", "c2VydmljZTk3c2VydmljZTk3"),
    ("service97gateway97", "c2VydmljZTk3Z2F0ZXdheTk3"),
    ("gateway97gateway97", "Z2F0ZXdheTk3Z2F0ZXdheTk3"),
    ("gateway97storage97", "Z2F0ZXdheTk3c3RvcmFnZTk3"),
    ("gateway97network97", "Z2F0ZXdheTk3bmV0d29yazk3"),
    ("gateway97latency97", "Z2F0ZXdheTk3bGF0ZW5jeTk3"),
    ("storage97latency97", "c3RvcmFnZTk3bGF0ZW5jeTk3"),
    ("storage97buffer97", "c3RvcmFnZTk3YnVmZmVyOTc"),
    ("storage97queue97", "c3RvcmFnZTk3cXVldWU5Nw"),
    ("storage97worker97", "c3RvcmFnZTk3d29ya2VyOTc"),
    ("network97worker97", "bmV0d29yazk3d29ya2VyOTc"),
    ("network97kernel97", "bmV0d29yazk3a2VybmVsOTc"),
    ("network97signal97", "bmV0d29yazk3c2lnbmFsOTc"),
    ("network97packet97", "bmV0d29yazk3cGFja2V0OTc"),
    ("latency97packet97", "bGF0ZW5jeTk3cGFja2V0OTc"),
    ("latency97router97", "bGF0ZW5jeTk3cm91dGVyOTc"),
    ("latency97cluster97", "bGF0ZW5jeTk3Y2x1c3Rlcjk3"),
    ("latency97mirror97", "bGF0ZW5jeTk3bWlycm9yOTc"),
    ("buffer97mirror97", "YnVmZmVyOTdtaXJyb3I5Nw"),
    ("buffer97filter97", "YnVmZmVyOTdmaWx0ZXI5Nw"),
    ("buffer97ranking97", "YnVmZmVyOTdyYW5raW5nOTc"),
    ("buffer97encoding97", "YnVmZmVyOTdlbmNvZGluZzk3"),
    ("queue97encoding97", "cXVldWU5N2VuY29kaW5nOTc"),
    ("queue97mapping97", "cXVldWU5N21hcHBpbmc5Nw"),
    ("queue97record97", "cXVldWU5N3JlY29yZDk3"),
    ("queue97candle97", "cXVldWU5N2NhbmRsZTk3"),
    ("worker97candle97", "d29ya2VyOTdjYW5kbGU5Nw"),
    ("worker97thread97", "d29ya2VyOTd0aHJlYWQ5Nw"),
    ("worker97kitten97", "d29ya2VyOTdraXR0ZW45Nw"),
    ("worker97sitting97", "d29ya2VyOTdzaXR0aW5nOTc"),
    ("kernel97sitting97", "a2VybmVsOTdzaXR0aW5nOTc"),
    ("kernel97agent97", "a2VybmVsOTdhZ2VudDk3"),
    ("kernel97angle97", "a2VybmVsOTdhbmdsZTk3"),
    ("kernel97universe97", "a2VybmVsOTd1bml2ZXJzZTk3"),
    ("signal97universe97", "c2lnbmFsOTd1bml2ZXJzZTk3"),
    ("signal97memory97", "c2lnbmFsOTdtZW1vcnk5Nw"),
    ("signal97stream97", "c2lnbmFsOTdzdHJlYW05Nw"),
    ("signal97context97", "c2lnbmFsOTdjb250ZXh0OTc"),
    ("packet97context97", "cGFja2V0OTdjb250ZXh0OTc"),
    ("packet97knowledge97", "cGFja2V0OTdrbm93bGVkZ2U5Nw"),
    ("packet97vector97", "cGFja2V0OTd2ZWN0b3I5Nw"),
    ("packet97processor97", "cGFja2V0OTdwcm9jZXNzb3I5Nw"),
    ("router97processor97", "cm91dGVyOTdwcm9jZXNzb3I5Nw"),
    ("router97reasoning97", "cm91dGVyOTdyZWFzb25pbmc5Nw"),
    ("router97machine97", "cm91dGVyOTdtYWNoaW5lOTc"),
    ("router97learning97", "cm91dGVyOTdsZWFybmluZzk3"),
    ("cluster97learning97", "Y2x1c3Rlcjk3bGVhcm5pbmc5Nw"),
    ("cluster97model97", "Y2x1c3Rlcjk3bW9kZWw5Nw"),
    ("cluster97token97", "Y2x1c3Rlcjk3dG9rZW45Nw"),
    ("cluster97prompt97", "Y2x1c3Rlcjk3cHJvbXB0OTc"),
    ("mirror97prompt97", "bWlycm9yOTdwcm9tcHQ5Nw"),
    ("mirror97session97", "bWlycm9yOTdzZXNzaW9uOTc"),
    ("mirror97library97", "bWlycm9yOTdsaWJyYXJ5OTc"),
    ("mirror97service97", "bWlycm9yOTdzZXJ2aWNlOTc"),
    ("filter97service97", "ZmlsdGVyOTdzZXJ2aWNlOTc"),
    ("filter97gateway97", "ZmlsdGVyOTdnYXRld2F5OTc"),
    ("filter97storage97", "ZmlsdGVyOTdzdG9yYWdlOTc"),
    ("filter97network97", "ZmlsdGVyOTduZXR3b3JrOTc"),
    ("ranking97network97", "cmFua2luZzk3bmV0d29yazk3"),
    ("ranking97latency97", "cmFua2luZzk3bGF0ZW5jeTk3"),
    ("ranking97buffer97", "cmFua2luZzk3YnVmZmVyOTc"),
    ("ranking97queue97", "cmFua2luZzk3cXVldWU5Nw"),
    ("encoding97queue97", "ZW5jb2Rpbmc5N3F1ZXVlOTc"),
    ("encoding97worker97", "ZW5jb2Rpbmc5N3dvcmtlcjk3"),
    ("encoding97kernel97", "ZW5jb2Rpbmc5N2tlcm5lbDk3"),
    ("encoding97signal97", "ZW5jb2Rpbmc5N3NpZ25hbDk3"),
    ("mapping97signal97", "bWFwcGluZzk3c2lnbmFsOTc"),
    ("mapping97packet97", "bWFwcGluZzk3cGFja2V0OTc"),
    ("mapping97router97", "bWFwcGluZzk3cm91dGVyOTc"),
    ("mapping97cluster97", "bWFwcGluZzk3Y2x1c3Rlcjk3"),
    ("record97cluster97", "cmVjb3JkOTdjbHVzdGVyOTc"),
    ("record97mirror97", "cmVjb3JkOTdtaXJyb3I5Nw"),
    ("record97filter97", "cmVjb3JkOTdmaWx0ZXI5Nw"),
    ("record97ranking97", "cmVjb3JkOTdyYW5raW5nOTc"),
    ("candle97ranking97", "Y2FuZGxlOTdyYW5raW5nOTc"),
    ("candle97encoding97", "Y2FuZGxlOTdlbmNvZGluZzk3"),
    ("candle97mapping97", "Y2FuZGxlOTdtYXBwaW5nOTc"),
    ("candle97record97", "Y2FuZGxlOTdyZWNvcmQ5Nw"),
    ("thread97record97", "dGhyZWFkOTdyZWNvcmQ5Nw"),
    ("thread97candle97", "dGhyZWFkOTdjYW5kbGU5Nw"),
    ("thread97thread97", "dGhyZWFkOTd0aHJlYWQ5Nw"),
    ("thread97kitten97", "dGhyZWFkOTdraXR0ZW45Nw"),
    (
        "round 97: the quick brown fox jumps over the lazy dog",
        "cm91bmQgOTc6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 97: agentuniverse is a framework for multi agents",
        "cm91bmQgOTc6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 97: knowledge stored as vectors enables retrieval",
        "cm91bmQgOTc6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 97: the processor reads the record then stops",
        "cm91bmQgOTc6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 97: a worker pulls the next task from the queue",
        "cm91bmQgOTc6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 97: signals travel through the network layer",
        "cm91bmQgOTc6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 97: the gateway routes each request by policy",
        "cm91bmQgOTc6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 97: memory grows until the buffer is full",
        "cm91bmQgOTc6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 97: the cluster mirrors every packet twice",
        "cm91bmQgOTc6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 97: ranking uses tokens learned from the corpus",
        "cm91bmQgOTc6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 97: a long session ends when the candle dies",
        "cm91bmQgOTc6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 97: encode the prompt then map the result",
        "cm91bmQgOTc6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 97: the kernel wakes the worker at dawn", "cm91bmQgOTc6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 97: service latency drops after the patch",
        "cm91bmQgOTc6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 97: the library caches every vector it sees",
        "cm91bmQgOTc6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 97: agents argue then the debate resolves",
        "cm91bmQgOTc6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 97: the filter keeps only strong matches",
        "cm91bmQgOTc6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 97: the model answers with a short reply",
        "cm91bmQgOTc6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 97: the recorder stores the reasoning trace",
        "cm91bmQgOTc6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 97: the angel watches the processor run", "cm91bmQgOTc6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 97: angle of the vector decides the match",
        "cm91bmQgOTc6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 97: the candle burns twice as long at night",
        "cm91bmQgOTc6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 97: a mirror of the universe in one line",
        "cm91bmQgOTc6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 97: the queue drains before the storm", "cm91bmQgOTc6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
