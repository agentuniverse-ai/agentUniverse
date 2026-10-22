"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten30kitten30", "a2l0dGVuMzBraXR0ZW4zMA"),
    ("kitten30sitting30", "a2l0dGVuMzBzaXR0aW5nMzA"),
    ("kitten30agent30", "a2l0dGVuMzBhZ2VudDMw"),
    ("kitten30angle30", "a2l0dGVuMzBhbmdsZTMw"),
    ("sitting30angle30", "c2l0dGluZzMwYW5nbGUzMA"),
    ("sitting30universe30", "c2l0dGluZzMwdW5pdmVyc2UzMA"),
    ("sitting30memory30", "c2l0dGluZzMwbWVtb3J5MzA"),
    ("sitting30stream30", "c2l0dGluZzMwc3RyZWFtMzA"),
    ("agent30stream30", "YWdlbnQzMHN0cmVhbTMw"),
    ("agent30context30", "YWdlbnQzMGNvbnRleHQzMA"),
    ("agent30knowledge30", "YWdlbnQzMGtub3dsZWRnZTMw"),
    ("agent30vector30", "YWdlbnQzMHZlY3RvcjMw"),
    ("angle30vector30", "YW5nbGUzMHZlY3RvcjMw"),
    ("angle30processor30", "YW5nbGUzMHByb2Nlc3NvcjMw"),
    ("angle30reasoning30", "YW5nbGUzMHJlYXNvbmluZzMw"),
    ("angle30machine30", "YW5nbGUzMG1hY2hpbmUzMA"),
    ("universe30machine30", "dW5pdmVyc2UzMG1hY2hpbmUzMA"),
    ("universe30learning30", "dW5pdmVyc2UzMGxlYXJuaW5nMzA"),
    ("universe30model30", "dW5pdmVyc2UzMG1vZGVsMzA"),
    ("universe30token30", "dW5pdmVyc2UzMHRva2VuMzA"),
    ("memory30token30", "bWVtb3J5MzB0b2tlbjMw"),
    ("memory30prompt30", "bWVtb3J5MzBwcm9tcHQzMA"),
    ("memory30session30", "bWVtb3J5MzBzZXNzaW9uMzA"),
    ("memory30library30", "bWVtb3J5MzBsaWJyYXJ5MzA"),
    ("stream30library30", "c3RyZWFtMzBsaWJyYXJ5MzA"),
    ("stream30service30", "c3RyZWFtMzBzZXJ2aWNlMzA"),
    ("stream30gateway30", "c3RyZWFtMzBnYXRld2F5MzA"),
    ("stream30storage30", "c3RyZWFtMzBzdG9yYWdlMzA"),
    ("context30storage30", "Y29udGV4dDMwc3RvcmFnZTMw"),
    ("context30network30", "Y29udGV4dDMwbmV0d29yazMw"),
    ("context30latency30", "Y29udGV4dDMwbGF0ZW5jeTMw"),
    ("context30buffer30", "Y29udGV4dDMwYnVmZmVyMzA"),
    ("knowledge30buffer30", "a25vd2xlZGdlMzBidWZmZXIzMA"),
    ("knowledge30queue30", "a25vd2xlZGdlMzBxdWV1ZTMw"),
    ("knowledge30worker30", "a25vd2xlZGdlMzB3b3JrZXIzMA"),
    ("knowledge30kernel30", "a25vd2xlZGdlMzBrZXJuZWwzMA"),
    ("vector30kernel30", "dmVjdG9yMzBrZXJuZWwzMA"),
    ("vector30signal30", "dmVjdG9yMzBzaWduYWwzMA"),
    ("vector30packet30", "dmVjdG9yMzBwYWNrZXQzMA"),
    ("vector30router30", "dmVjdG9yMzByb3V0ZXIzMA"),
    ("processor30router30", "cHJvY2Vzc29yMzByb3V0ZXIzMA"),
    ("processor30cluster30", "cHJvY2Vzc29yMzBjbHVzdGVyMzA"),
    ("processor30mirror30", "cHJvY2Vzc29yMzBtaXJyb3IzMA"),
    ("processor30filter30", "cHJvY2Vzc29yMzBmaWx0ZXIzMA"),
    ("reasoning30filter30", "cmVhc29uaW5nMzBmaWx0ZXIzMA"),
    ("reasoning30ranking30", "cmVhc29uaW5nMzByYW5raW5nMzA"),
    ("reasoning30encoding30", "cmVhc29uaW5nMzBlbmNvZGluZzMw"),
    ("reasoning30mapping30", "cmVhc29uaW5nMzBtYXBwaW5nMzA"),
    ("machine30mapping30", "bWFjaGluZTMwbWFwcGluZzMw"),
    ("machine30record30", "bWFjaGluZTMwcmVjb3JkMzA"),
    ("machine30candle30", "bWFjaGluZTMwY2FuZGxlMzA"),
    ("machine30thread30", "bWFjaGluZTMwdGhyZWFkMzA"),
    ("learning30thread30", "bGVhcm5pbmczMHRocmVhZDMw"),
    ("learning30kitten30", "bGVhcm5pbmczMGtpdHRlbjMw"),
    ("learning30sitting30", "bGVhcm5pbmczMHNpdHRpbmczMA"),
    ("learning30agent30", "bGVhcm5pbmczMGFnZW50MzA"),
    ("model30agent30", "bW9kZWwzMGFnZW50MzA"),
    ("model30angle30", "bW9kZWwzMGFuZ2xlMzA"),
    ("model30universe30", "bW9kZWwzMHVuaXZlcnNlMzA"),
    ("model30memory30", "bW9kZWwzMG1lbW9yeTMw"),
    ("token30memory30", "dG9rZW4zMG1lbW9yeTMw"),
    ("token30stream30", "dG9rZW4zMHN0cmVhbTMw"),
    ("token30context30", "dG9rZW4zMGNvbnRleHQzMA"),
    ("token30knowledge30", "dG9rZW4zMGtub3dsZWRnZTMw"),
    ("prompt30knowledge30", "cHJvbXB0MzBrbm93bGVkZ2UzMA"),
    ("prompt30vector30", "cHJvbXB0MzB2ZWN0b3IzMA"),
    ("prompt30processor30", "cHJvbXB0MzBwcm9jZXNzb3IzMA"),
    ("prompt30reasoning30", "cHJvbXB0MzByZWFzb25pbmczMA"),
    ("session30reasoning30", "c2Vzc2lvbjMwcmVhc29uaW5nMzA"),
    ("session30machine30", "c2Vzc2lvbjMwbWFjaGluZTMw"),
    ("session30learning30", "c2Vzc2lvbjMwbGVhcm5pbmczMA"),
    ("session30model30", "c2Vzc2lvbjMwbW9kZWwzMA"),
    ("library30model30", "bGlicmFyeTMwbW9kZWwzMA"),
    ("library30token30", "bGlicmFyeTMwdG9rZW4zMA"),
    ("library30prompt30", "bGlicmFyeTMwcHJvbXB0MzA"),
    ("library30session30", "bGlicmFyeTMwc2Vzc2lvbjMw"),
    ("service30session30", "c2VydmljZTMwc2Vzc2lvbjMw"),
    ("service30library30", "c2VydmljZTMwbGlicmFyeTMw"),
    ("service30service30", "c2VydmljZTMwc2VydmljZTMw"),
    ("service30gateway30", "c2VydmljZTMwZ2F0ZXdheTMw"),
    ("gateway30gateway30", "Z2F0ZXdheTMwZ2F0ZXdheTMw"),
    ("gateway30storage30", "Z2F0ZXdheTMwc3RvcmFnZTMw"),
    ("gateway30network30", "Z2F0ZXdheTMwbmV0d29yazMw"),
    ("gateway30latency30", "Z2F0ZXdheTMwbGF0ZW5jeTMw"),
    ("storage30latency30", "c3RvcmFnZTMwbGF0ZW5jeTMw"),
    ("storage30buffer30", "c3RvcmFnZTMwYnVmZmVyMzA"),
    ("storage30queue30", "c3RvcmFnZTMwcXVldWUzMA"),
    ("storage30worker30", "c3RvcmFnZTMwd29ya2VyMzA"),
    ("network30worker30", "bmV0d29yazMwd29ya2VyMzA"),
    ("network30kernel30", "bmV0d29yazMwa2VybmVsMzA"),
    ("network30signal30", "bmV0d29yazMwc2lnbmFsMzA"),
    ("network30packet30", "bmV0d29yazMwcGFja2V0MzA"),
    ("latency30packet30", "bGF0ZW5jeTMwcGFja2V0MzA"),
    ("latency30router30", "bGF0ZW5jeTMwcm91dGVyMzA"),
    ("latency30cluster30", "bGF0ZW5jeTMwY2x1c3RlcjMw"),
    ("latency30mirror30", "bGF0ZW5jeTMwbWlycm9yMzA"),
    ("buffer30mirror30", "YnVmZmVyMzBtaXJyb3IzMA"),
    ("buffer30filter30", "YnVmZmVyMzBmaWx0ZXIzMA"),
    ("buffer30ranking30", "YnVmZmVyMzByYW5raW5nMzA"),
    ("buffer30encoding30", "YnVmZmVyMzBlbmNvZGluZzMw"),
    ("queue30encoding30", "cXVldWUzMGVuY29kaW5nMzA"),
    ("queue30mapping30", "cXVldWUzMG1hcHBpbmczMA"),
    ("queue30record30", "cXVldWUzMHJlY29yZDMw"),
    ("queue30candle30", "cXVldWUzMGNhbmRsZTMw"),
    ("worker30candle30", "d29ya2VyMzBjYW5kbGUzMA"),
    ("worker30thread30", "d29ya2VyMzB0aHJlYWQzMA"),
    ("worker30kitten30", "d29ya2VyMzBraXR0ZW4zMA"),
    ("worker30sitting30", "d29ya2VyMzBzaXR0aW5nMzA"),
    ("kernel30sitting30", "a2VybmVsMzBzaXR0aW5nMzA"),
    ("kernel30agent30", "a2VybmVsMzBhZ2VudDMw"),
    ("kernel30angle30", "a2VybmVsMzBhbmdsZTMw"),
    ("kernel30universe30", "a2VybmVsMzB1bml2ZXJzZTMw"),
    ("signal30universe30", "c2lnbmFsMzB1bml2ZXJzZTMw"),
    ("signal30memory30", "c2lnbmFsMzBtZW1vcnkzMA"),
    ("signal30stream30", "c2lnbmFsMzBzdHJlYW0zMA"),
    ("signal30context30", "c2lnbmFsMzBjb250ZXh0MzA"),
    ("packet30context30", "cGFja2V0MzBjb250ZXh0MzA"),
    ("packet30knowledge30", "cGFja2V0MzBrbm93bGVkZ2UzMA"),
    ("packet30vector30", "cGFja2V0MzB2ZWN0b3IzMA"),
    ("packet30processor30", "cGFja2V0MzBwcm9jZXNzb3IzMA"),
    ("router30processor30", "cm91dGVyMzBwcm9jZXNzb3IzMA"),
    ("router30reasoning30", "cm91dGVyMzByZWFzb25pbmczMA"),
    ("router30machine30", "cm91dGVyMzBtYWNoaW5lMzA"),
    ("router30learning30", "cm91dGVyMzBsZWFybmluZzMw"),
    ("cluster30learning30", "Y2x1c3RlcjMwbGVhcm5pbmczMA"),
    ("cluster30model30", "Y2x1c3RlcjMwbW9kZWwzMA"),
    ("cluster30token30", "Y2x1c3RlcjMwdG9rZW4zMA"),
    ("cluster30prompt30", "Y2x1c3RlcjMwcHJvbXB0MzA"),
    ("mirror30prompt30", "bWlycm9yMzBwcm9tcHQzMA"),
    ("mirror30session30", "bWlycm9yMzBzZXNzaW9uMzA"),
    ("mirror30library30", "bWlycm9yMzBsaWJyYXJ5MzA"),
    ("mirror30service30", "bWlycm9yMzBzZXJ2aWNlMzA"),
    ("filter30service30", "ZmlsdGVyMzBzZXJ2aWNlMzA"),
    ("filter30gateway30", "ZmlsdGVyMzBnYXRld2F5MzA"),
    ("filter30storage30", "ZmlsdGVyMzBzdG9yYWdlMzA"),
    ("filter30network30", "ZmlsdGVyMzBuZXR3b3JrMzA"),
    ("ranking30network30", "cmFua2luZzMwbmV0d29yazMw"),
    ("ranking30latency30", "cmFua2luZzMwbGF0ZW5jeTMw"),
    ("ranking30buffer30", "cmFua2luZzMwYnVmZmVyMzA"),
    ("ranking30queue30", "cmFua2luZzMwcXVldWUzMA"),
    ("encoding30queue30", "ZW5jb2RpbmczMHF1ZXVlMzA"),
    ("encoding30worker30", "ZW5jb2RpbmczMHdvcmtlcjMw"),
    ("encoding30kernel30", "ZW5jb2RpbmczMGtlcm5lbDMw"),
    ("encoding30signal30", "ZW5jb2RpbmczMHNpZ25hbDMw"),
    ("mapping30signal30", "bWFwcGluZzMwc2lnbmFsMzA"),
    ("mapping30packet30", "bWFwcGluZzMwcGFja2V0MzA"),
    ("mapping30router30", "bWFwcGluZzMwcm91dGVyMzA"),
    ("mapping30cluster30", "bWFwcGluZzMwY2x1c3RlcjMw"),
    ("record30cluster30", "cmVjb3JkMzBjbHVzdGVyMzA"),
    ("record30mirror30", "cmVjb3JkMzBtaXJyb3IzMA"),
    ("record30filter30", "cmVjb3JkMzBmaWx0ZXIzMA"),
    ("record30ranking30", "cmVjb3JkMzByYW5raW5nMzA"),
    ("candle30ranking30", "Y2FuZGxlMzByYW5raW5nMzA"),
    ("candle30encoding30", "Y2FuZGxlMzBlbmNvZGluZzMw"),
    ("candle30mapping30", "Y2FuZGxlMzBtYXBwaW5nMzA"),
    ("candle30record30", "Y2FuZGxlMzByZWNvcmQzMA"),
    ("thread30record30", "dGhyZWFkMzByZWNvcmQzMA"),
    ("thread30candle30", "dGhyZWFkMzBjYW5kbGUzMA"),
    ("thread30thread30", "dGhyZWFkMzB0aHJlYWQzMA"),
    ("thread30kitten30", "dGhyZWFkMzBraXR0ZW4zMA"),
    (
        "round 30: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMzA6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 30: agentuniverse is a framework for multi agents",
        "cm91bmQgMzA6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 30: knowledge stored as vectors enables retrieval",
        "cm91bmQgMzA6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 30: the processor reads the record then stops",
        "cm91bmQgMzA6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 30: a worker pulls the next task from the queue",
        "cm91bmQgMzA6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 30: signals travel through the network layer",
        "cm91bmQgMzA6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 30: the gateway routes each request by policy",
        "cm91bmQgMzA6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 30: memory grows until the buffer is full",
        "cm91bmQgMzA6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 30: the cluster mirrors every packet twice",
        "cm91bmQgMzA6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 30: ranking uses tokens learned from the corpus",
        "cm91bmQgMzA6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 30: a long session ends when the candle dies",
        "cm91bmQgMzA6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 30: encode the prompt then map the result",
        "cm91bmQgMzA6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 30: the kernel wakes the worker at dawn", "cm91bmQgMzA6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 30: service latency drops after the patch",
        "cm91bmQgMzA6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 30: the library caches every vector it sees",
        "cm91bmQgMzA6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 30: agents argue then the debate resolves",
        "cm91bmQgMzA6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 30: the filter keeps only strong matches",
        "cm91bmQgMzA6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 30: the model answers with a short reply",
        "cm91bmQgMzA6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 30: the recorder stores the reasoning trace",
        "cm91bmQgMzA6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 30: the angel watches the processor run", "cm91bmQgMzA6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 30: angle of the vector decides the match",
        "cm91bmQgMzA6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 30: the candle burns twice as long at night",
        "cm91bmQgMzA6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 30: a mirror of the universe in one line",
        "cm91bmQgMzA6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 30: the queue drains before the storm", "cm91bmQgMzA6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
