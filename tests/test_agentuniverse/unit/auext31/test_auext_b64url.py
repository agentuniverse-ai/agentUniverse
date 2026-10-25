"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten31kitten31", "a2l0dGVuMzFraXR0ZW4zMQ"),
    ("kitten31sitting31", "a2l0dGVuMzFzaXR0aW5nMzE"),
    ("kitten31agent31", "a2l0dGVuMzFhZ2VudDMx"),
    ("kitten31angle31", "a2l0dGVuMzFhbmdsZTMx"),
    ("sitting31angle31", "c2l0dGluZzMxYW5nbGUzMQ"),
    ("sitting31universe31", "c2l0dGluZzMxdW5pdmVyc2UzMQ"),
    ("sitting31memory31", "c2l0dGluZzMxbWVtb3J5MzE"),
    ("sitting31stream31", "c2l0dGluZzMxc3RyZWFtMzE"),
    ("agent31stream31", "YWdlbnQzMXN0cmVhbTMx"),
    ("agent31context31", "YWdlbnQzMWNvbnRleHQzMQ"),
    ("agent31knowledge31", "YWdlbnQzMWtub3dsZWRnZTMx"),
    ("agent31vector31", "YWdlbnQzMXZlY3RvcjMx"),
    ("angle31vector31", "YW5nbGUzMXZlY3RvcjMx"),
    ("angle31processor31", "YW5nbGUzMXByb2Nlc3NvcjMx"),
    ("angle31reasoning31", "YW5nbGUzMXJlYXNvbmluZzMx"),
    ("angle31machine31", "YW5nbGUzMW1hY2hpbmUzMQ"),
    ("universe31machine31", "dW5pdmVyc2UzMW1hY2hpbmUzMQ"),
    ("universe31learning31", "dW5pdmVyc2UzMWxlYXJuaW5nMzE"),
    ("universe31model31", "dW5pdmVyc2UzMW1vZGVsMzE"),
    ("universe31token31", "dW5pdmVyc2UzMXRva2VuMzE"),
    ("memory31token31", "bWVtb3J5MzF0b2tlbjMx"),
    ("memory31prompt31", "bWVtb3J5MzFwcm9tcHQzMQ"),
    ("memory31session31", "bWVtb3J5MzFzZXNzaW9uMzE"),
    ("memory31library31", "bWVtb3J5MzFsaWJyYXJ5MzE"),
    ("stream31library31", "c3RyZWFtMzFsaWJyYXJ5MzE"),
    ("stream31service31", "c3RyZWFtMzFzZXJ2aWNlMzE"),
    ("stream31gateway31", "c3RyZWFtMzFnYXRld2F5MzE"),
    ("stream31storage31", "c3RyZWFtMzFzdG9yYWdlMzE"),
    ("context31storage31", "Y29udGV4dDMxc3RvcmFnZTMx"),
    ("context31network31", "Y29udGV4dDMxbmV0d29yazMx"),
    ("context31latency31", "Y29udGV4dDMxbGF0ZW5jeTMx"),
    ("context31buffer31", "Y29udGV4dDMxYnVmZmVyMzE"),
    ("knowledge31buffer31", "a25vd2xlZGdlMzFidWZmZXIzMQ"),
    ("knowledge31queue31", "a25vd2xlZGdlMzFxdWV1ZTMx"),
    ("knowledge31worker31", "a25vd2xlZGdlMzF3b3JrZXIzMQ"),
    ("knowledge31kernel31", "a25vd2xlZGdlMzFrZXJuZWwzMQ"),
    ("vector31kernel31", "dmVjdG9yMzFrZXJuZWwzMQ"),
    ("vector31signal31", "dmVjdG9yMzFzaWduYWwzMQ"),
    ("vector31packet31", "dmVjdG9yMzFwYWNrZXQzMQ"),
    ("vector31router31", "dmVjdG9yMzFyb3V0ZXIzMQ"),
    ("processor31router31", "cHJvY2Vzc29yMzFyb3V0ZXIzMQ"),
    ("processor31cluster31", "cHJvY2Vzc29yMzFjbHVzdGVyMzE"),
    ("processor31mirror31", "cHJvY2Vzc29yMzFtaXJyb3IzMQ"),
    ("processor31filter31", "cHJvY2Vzc29yMzFmaWx0ZXIzMQ"),
    ("reasoning31filter31", "cmVhc29uaW5nMzFmaWx0ZXIzMQ"),
    ("reasoning31ranking31", "cmVhc29uaW5nMzFyYW5raW5nMzE"),
    ("reasoning31encoding31", "cmVhc29uaW5nMzFlbmNvZGluZzMx"),
    ("reasoning31mapping31", "cmVhc29uaW5nMzFtYXBwaW5nMzE"),
    ("machine31mapping31", "bWFjaGluZTMxbWFwcGluZzMx"),
    ("machine31record31", "bWFjaGluZTMxcmVjb3JkMzE"),
    ("machine31candle31", "bWFjaGluZTMxY2FuZGxlMzE"),
    ("machine31thread31", "bWFjaGluZTMxdGhyZWFkMzE"),
    ("learning31thread31", "bGVhcm5pbmczMXRocmVhZDMx"),
    ("learning31kitten31", "bGVhcm5pbmczMWtpdHRlbjMx"),
    ("learning31sitting31", "bGVhcm5pbmczMXNpdHRpbmczMQ"),
    ("learning31agent31", "bGVhcm5pbmczMWFnZW50MzE"),
    ("model31agent31", "bW9kZWwzMWFnZW50MzE"),
    ("model31angle31", "bW9kZWwzMWFuZ2xlMzE"),
    ("model31universe31", "bW9kZWwzMXVuaXZlcnNlMzE"),
    ("model31memory31", "bW9kZWwzMW1lbW9yeTMx"),
    ("token31memory31", "dG9rZW4zMW1lbW9yeTMx"),
    ("token31stream31", "dG9rZW4zMXN0cmVhbTMx"),
    ("token31context31", "dG9rZW4zMWNvbnRleHQzMQ"),
    ("token31knowledge31", "dG9rZW4zMWtub3dsZWRnZTMx"),
    ("prompt31knowledge31", "cHJvbXB0MzFrbm93bGVkZ2UzMQ"),
    ("prompt31vector31", "cHJvbXB0MzF2ZWN0b3IzMQ"),
    ("prompt31processor31", "cHJvbXB0MzFwcm9jZXNzb3IzMQ"),
    ("prompt31reasoning31", "cHJvbXB0MzFyZWFzb25pbmczMQ"),
    ("session31reasoning31", "c2Vzc2lvbjMxcmVhc29uaW5nMzE"),
    ("session31machine31", "c2Vzc2lvbjMxbWFjaGluZTMx"),
    ("session31learning31", "c2Vzc2lvbjMxbGVhcm5pbmczMQ"),
    ("session31model31", "c2Vzc2lvbjMxbW9kZWwzMQ"),
    ("library31model31", "bGlicmFyeTMxbW9kZWwzMQ"),
    ("library31token31", "bGlicmFyeTMxdG9rZW4zMQ"),
    ("library31prompt31", "bGlicmFyeTMxcHJvbXB0MzE"),
    ("library31session31", "bGlicmFyeTMxc2Vzc2lvbjMx"),
    ("service31session31", "c2VydmljZTMxc2Vzc2lvbjMx"),
    ("service31library31", "c2VydmljZTMxbGlicmFyeTMx"),
    ("service31service31", "c2VydmljZTMxc2VydmljZTMx"),
    ("service31gateway31", "c2VydmljZTMxZ2F0ZXdheTMx"),
    ("gateway31gateway31", "Z2F0ZXdheTMxZ2F0ZXdheTMx"),
    ("gateway31storage31", "Z2F0ZXdheTMxc3RvcmFnZTMx"),
    ("gateway31network31", "Z2F0ZXdheTMxbmV0d29yazMx"),
    ("gateway31latency31", "Z2F0ZXdheTMxbGF0ZW5jeTMx"),
    ("storage31latency31", "c3RvcmFnZTMxbGF0ZW5jeTMx"),
    ("storage31buffer31", "c3RvcmFnZTMxYnVmZmVyMzE"),
    ("storage31queue31", "c3RvcmFnZTMxcXVldWUzMQ"),
    ("storage31worker31", "c3RvcmFnZTMxd29ya2VyMzE"),
    ("network31worker31", "bmV0d29yazMxd29ya2VyMzE"),
    ("network31kernel31", "bmV0d29yazMxa2VybmVsMzE"),
    ("network31signal31", "bmV0d29yazMxc2lnbmFsMzE"),
    ("network31packet31", "bmV0d29yazMxcGFja2V0MzE"),
    ("latency31packet31", "bGF0ZW5jeTMxcGFja2V0MzE"),
    ("latency31router31", "bGF0ZW5jeTMxcm91dGVyMzE"),
    ("latency31cluster31", "bGF0ZW5jeTMxY2x1c3RlcjMx"),
    ("latency31mirror31", "bGF0ZW5jeTMxbWlycm9yMzE"),
    ("buffer31mirror31", "YnVmZmVyMzFtaXJyb3IzMQ"),
    ("buffer31filter31", "YnVmZmVyMzFmaWx0ZXIzMQ"),
    ("buffer31ranking31", "YnVmZmVyMzFyYW5raW5nMzE"),
    ("buffer31encoding31", "YnVmZmVyMzFlbmNvZGluZzMx"),
    ("queue31encoding31", "cXVldWUzMWVuY29kaW5nMzE"),
    ("queue31mapping31", "cXVldWUzMW1hcHBpbmczMQ"),
    ("queue31record31", "cXVldWUzMXJlY29yZDMx"),
    ("queue31candle31", "cXVldWUzMWNhbmRsZTMx"),
    ("worker31candle31", "d29ya2VyMzFjYW5kbGUzMQ"),
    ("worker31thread31", "d29ya2VyMzF0aHJlYWQzMQ"),
    ("worker31kitten31", "d29ya2VyMzFraXR0ZW4zMQ"),
    ("worker31sitting31", "d29ya2VyMzFzaXR0aW5nMzE"),
    ("kernel31sitting31", "a2VybmVsMzFzaXR0aW5nMzE"),
    ("kernel31agent31", "a2VybmVsMzFhZ2VudDMx"),
    ("kernel31angle31", "a2VybmVsMzFhbmdsZTMx"),
    ("kernel31universe31", "a2VybmVsMzF1bml2ZXJzZTMx"),
    ("signal31universe31", "c2lnbmFsMzF1bml2ZXJzZTMx"),
    ("signal31memory31", "c2lnbmFsMzFtZW1vcnkzMQ"),
    ("signal31stream31", "c2lnbmFsMzFzdHJlYW0zMQ"),
    ("signal31context31", "c2lnbmFsMzFjb250ZXh0MzE"),
    ("packet31context31", "cGFja2V0MzFjb250ZXh0MzE"),
    ("packet31knowledge31", "cGFja2V0MzFrbm93bGVkZ2UzMQ"),
    ("packet31vector31", "cGFja2V0MzF2ZWN0b3IzMQ"),
    ("packet31processor31", "cGFja2V0MzFwcm9jZXNzb3IzMQ"),
    ("router31processor31", "cm91dGVyMzFwcm9jZXNzb3IzMQ"),
    ("router31reasoning31", "cm91dGVyMzFyZWFzb25pbmczMQ"),
    ("router31machine31", "cm91dGVyMzFtYWNoaW5lMzE"),
    ("router31learning31", "cm91dGVyMzFsZWFybmluZzMx"),
    ("cluster31learning31", "Y2x1c3RlcjMxbGVhcm5pbmczMQ"),
    ("cluster31model31", "Y2x1c3RlcjMxbW9kZWwzMQ"),
    ("cluster31token31", "Y2x1c3RlcjMxdG9rZW4zMQ"),
    ("cluster31prompt31", "Y2x1c3RlcjMxcHJvbXB0MzE"),
    ("mirror31prompt31", "bWlycm9yMzFwcm9tcHQzMQ"),
    ("mirror31session31", "bWlycm9yMzFzZXNzaW9uMzE"),
    ("mirror31library31", "bWlycm9yMzFsaWJyYXJ5MzE"),
    ("mirror31service31", "bWlycm9yMzFzZXJ2aWNlMzE"),
    ("filter31service31", "ZmlsdGVyMzFzZXJ2aWNlMzE"),
    ("filter31gateway31", "ZmlsdGVyMzFnYXRld2F5MzE"),
    ("filter31storage31", "ZmlsdGVyMzFzdG9yYWdlMzE"),
    ("filter31network31", "ZmlsdGVyMzFuZXR3b3JrMzE"),
    ("ranking31network31", "cmFua2luZzMxbmV0d29yazMx"),
    ("ranking31latency31", "cmFua2luZzMxbGF0ZW5jeTMx"),
    ("ranking31buffer31", "cmFua2luZzMxYnVmZmVyMzE"),
    ("ranking31queue31", "cmFua2luZzMxcXVldWUzMQ"),
    ("encoding31queue31", "ZW5jb2RpbmczMXF1ZXVlMzE"),
    ("encoding31worker31", "ZW5jb2RpbmczMXdvcmtlcjMx"),
    ("encoding31kernel31", "ZW5jb2RpbmczMWtlcm5lbDMx"),
    ("encoding31signal31", "ZW5jb2RpbmczMXNpZ25hbDMx"),
    ("mapping31signal31", "bWFwcGluZzMxc2lnbmFsMzE"),
    ("mapping31packet31", "bWFwcGluZzMxcGFja2V0MzE"),
    ("mapping31router31", "bWFwcGluZzMxcm91dGVyMzE"),
    ("mapping31cluster31", "bWFwcGluZzMxY2x1c3RlcjMx"),
    ("record31cluster31", "cmVjb3JkMzFjbHVzdGVyMzE"),
    ("record31mirror31", "cmVjb3JkMzFtaXJyb3IzMQ"),
    ("record31filter31", "cmVjb3JkMzFmaWx0ZXIzMQ"),
    ("record31ranking31", "cmVjb3JkMzFyYW5raW5nMzE"),
    ("candle31ranking31", "Y2FuZGxlMzFyYW5raW5nMzE"),
    ("candle31encoding31", "Y2FuZGxlMzFlbmNvZGluZzMx"),
    ("candle31mapping31", "Y2FuZGxlMzFtYXBwaW5nMzE"),
    ("candle31record31", "Y2FuZGxlMzFyZWNvcmQzMQ"),
    ("thread31record31", "dGhyZWFkMzFyZWNvcmQzMQ"),
    ("thread31candle31", "dGhyZWFkMzFjYW5kbGUzMQ"),
    ("thread31thread31", "dGhyZWFkMzF0aHJlYWQzMQ"),
    ("thread31kitten31", "dGhyZWFkMzFraXR0ZW4zMQ"),
    (
        "round 31: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMzE6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 31: agentuniverse is a framework for multi agents",
        "cm91bmQgMzE6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 31: knowledge stored as vectors enables retrieval",
        "cm91bmQgMzE6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 31: the processor reads the record then stops",
        "cm91bmQgMzE6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 31: a worker pulls the next task from the queue",
        "cm91bmQgMzE6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 31: signals travel through the network layer",
        "cm91bmQgMzE6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 31: the gateway routes each request by policy",
        "cm91bmQgMzE6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 31: memory grows until the buffer is full",
        "cm91bmQgMzE6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 31: the cluster mirrors every packet twice",
        "cm91bmQgMzE6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 31: ranking uses tokens learned from the corpus",
        "cm91bmQgMzE6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 31: a long session ends when the candle dies",
        "cm91bmQgMzE6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 31: encode the prompt then map the result",
        "cm91bmQgMzE6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 31: the kernel wakes the worker at dawn", "cm91bmQgMzE6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 31: service latency drops after the patch",
        "cm91bmQgMzE6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 31: the library caches every vector it sees",
        "cm91bmQgMzE6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 31: agents argue then the debate resolves",
        "cm91bmQgMzE6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 31: the filter keeps only strong matches",
        "cm91bmQgMzE6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 31: the model answers with a short reply",
        "cm91bmQgMzE6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 31: the recorder stores the reasoning trace",
        "cm91bmQgMzE6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 31: the angel watches the processor run", "cm91bmQgMzE6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 31: angle of the vector decides the match",
        "cm91bmQgMzE6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 31: the candle burns twice as long at night",
        "cm91bmQgMzE6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 31: a mirror of the universe in one line",
        "cm91bmQgMzE6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 31: the queue drains before the storm", "cm91bmQgMzE6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
