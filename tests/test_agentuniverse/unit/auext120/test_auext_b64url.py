"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten120kitten120", "a2l0dGVuMTIwa2l0dGVuMTIw"),
    ("kitten120sitting120", "a2l0dGVuMTIwc2l0dGluZzEyMA"),
    ("kitten120agent120", "a2l0dGVuMTIwYWdlbnQxMjA"),
    ("kitten120angle120", "a2l0dGVuMTIwYW5nbGUxMjA"),
    ("sitting120angle120", "c2l0dGluZzEyMGFuZ2xlMTIw"),
    ("sitting120universe120", "c2l0dGluZzEyMHVuaXZlcnNlMTIw"),
    ("sitting120memory120", "c2l0dGluZzEyMG1lbW9yeTEyMA"),
    ("sitting120stream120", "c2l0dGluZzEyMHN0cmVhbTEyMA"),
    ("agent120stream120", "YWdlbnQxMjBzdHJlYW0xMjA"),
    ("agent120context120", "YWdlbnQxMjBjb250ZXh0MTIw"),
    ("agent120knowledge120", "YWdlbnQxMjBrbm93bGVkZ2UxMjA"),
    ("agent120vector120", "YWdlbnQxMjB2ZWN0b3IxMjA"),
    ("angle120vector120", "YW5nbGUxMjB2ZWN0b3IxMjA"),
    ("angle120processor120", "YW5nbGUxMjBwcm9jZXNzb3IxMjA"),
    ("angle120reasoning120", "YW5nbGUxMjByZWFzb25pbmcxMjA"),
    ("angle120machine120", "YW5nbGUxMjBtYWNoaW5lMTIw"),
    ("universe120machine120", "dW5pdmVyc2UxMjBtYWNoaW5lMTIw"),
    ("universe120learning120", "dW5pdmVyc2UxMjBsZWFybmluZzEyMA"),
    ("universe120model120", "dW5pdmVyc2UxMjBtb2RlbDEyMA"),
    ("universe120token120", "dW5pdmVyc2UxMjB0b2tlbjEyMA"),
    ("memory120token120", "bWVtb3J5MTIwdG9rZW4xMjA"),
    ("memory120prompt120", "bWVtb3J5MTIwcHJvbXB0MTIw"),
    ("memory120session120", "bWVtb3J5MTIwc2Vzc2lvbjEyMA"),
    ("memory120library120", "bWVtb3J5MTIwbGlicmFyeTEyMA"),
    ("stream120library120", "c3RyZWFtMTIwbGlicmFyeTEyMA"),
    ("stream120service120", "c3RyZWFtMTIwc2VydmljZTEyMA"),
    ("stream120gateway120", "c3RyZWFtMTIwZ2F0ZXdheTEyMA"),
    ("stream120storage120", "c3RyZWFtMTIwc3RvcmFnZTEyMA"),
    ("context120storage120", "Y29udGV4dDEyMHN0b3JhZ2UxMjA"),
    ("context120network120", "Y29udGV4dDEyMG5ldHdvcmsxMjA"),
    ("context120latency120", "Y29udGV4dDEyMGxhdGVuY3kxMjA"),
    ("context120buffer120", "Y29udGV4dDEyMGJ1ZmZlcjEyMA"),
    ("knowledge120buffer120", "a25vd2xlZGdlMTIwYnVmZmVyMTIw"),
    ("knowledge120queue120", "a25vd2xlZGdlMTIwcXVldWUxMjA"),
    ("knowledge120worker120", "a25vd2xlZGdlMTIwd29ya2VyMTIw"),
    ("knowledge120kernel120", "a25vd2xlZGdlMTIwa2VybmVsMTIw"),
    ("vector120kernel120", "dmVjdG9yMTIwa2VybmVsMTIw"),
    ("vector120signal120", "dmVjdG9yMTIwc2lnbmFsMTIw"),
    ("vector120packet120", "dmVjdG9yMTIwcGFja2V0MTIw"),
    ("vector120router120", "dmVjdG9yMTIwcm91dGVyMTIw"),
    ("processor120router120", "cHJvY2Vzc29yMTIwcm91dGVyMTIw"),
    ("processor120cluster120", "cHJvY2Vzc29yMTIwY2x1c3RlcjEyMA"),
    ("processor120mirror120", "cHJvY2Vzc29yMTIwbWlycm9yMTIw"),
    ("processor120filter120", "cHJvY2Vzc29yMTIwZmlsdGVyMTIw"),
    ("reasoning120filter120", "cmVhc29uaW5nMTIwZmlsdGVyMTIw"),
    ("reasoning120ranking120", "cmVhc29uaW5nMTIwcmFua2luZzEyMA"),
    ("reasoning120encoding120", "cmVhc29uaW5nMTIwZW5jb2RpbmcxMjA"),
    ("reasoning120mapping120", "cmVhc29uaW5nMTIwbWFwcGluZzEyMA"),
    ("machine120mapping120", "bWFjaGluZTEyMG1hcHBpbmcxMjA"),
    ("machine120record120", "bWFjaGluZTEyMHJlY29yZDEyMA"),
    ("machine120candle120", "bWFjaGluZTEyMGNhbmRsZTEyMA"),
    ("machine120thread120", "bWFjaGluZTEyMHRocmVhZDEyMA"),
    ("learning120thread120", "bGVhcm5pbmcxMjB0aHJlYWQxMjA"),
    ("learning120kitten120", "bGVhcm5pbmcxMjBraXR0ZW4xMjA"),
    ("learning120sitting120", "bGVhcm5pbmcxMjBzaXR0aW5nMTIw"),
    ("learning120agent120", "bGVhcm5pbmcxMjBhZ2VudDEyMA"),
    ("model120agent120", "bW9kZWwxMjBhZ2VudDEyMA"),
    ("model120angle120", "bW9kZWwxMjBhbmdsZTEyMA"),
    ("model120universe120", "bW9kZWwxMjB1bml2ZXJzZTEyMA"),
    ("model120memory120", "bW9kZWwxMjBtZW1vcnkxMjA"),
    ("token120memory120", "dG9rZW4xMjBtZW1vcnkxMjA"),
    ("token120stream120", "dG9rZW4xMjBzdHJlYW0xMjA"),
    ("token120context120", "dG9rZW4xMjBjb250ZXh0MTIw"),
    ("token120knowledge120", "dG9rZW4xMjBrbm93bGVkZ2UxMjA"),
    ("prompt120knowledge120", "cHJvbXB0MTIwa25vd2xlZGdlMTIw"),
    ("prompt120vector120", "cHJvbXB0MTIwdmVjdG9yMTIw"),
    ("prompt120processor120", "cHJvbXB0MTIwcHJvY2Vzc29yMTIw"),
    ("prompt120reasoning120", "cHJvbXB0MTIwcmVhc29uaW5nMTIw"),
    ("session120reasoning120", "c2Vzc2lvbjEyMHJlYXNvbmluZzEyMA"),
    ("session120machine120", "c2Vzc2lvbjEyMG1hY2hpbmUxMjA"),
    ("session120learning120", "c2Vzc2lvbjEyMGxlYXJuaW5nMTIw"),
    ("session120model120", "c2Vzc2lvbjEyMG1vZGVsMTIw"),
    ("library120model120", "bGlicmFyeTEyMG1vZGVsMTIw"),
    ("library120token120", "bGlicmFyeTEyMHRva2VuMTIw"),
    ("library120prompt120", "bGlicmFyeTEyMHByb21wdDEyMA"),
    ("library120session120", "bGlicmFyeTEyMHNlc3Npb24xMjA"),
    ("service120session120", "c2VydmljZTEyMHNlc3Npb24xMjA"),
    ("service120library120", "c2VydmljZTEyMGxpYnJhcnkxMjA"),
    ("service120service120", "c2VydmljZTEyMHNlcnZpY2UxMjA"),
    ("service120gateway120", "c2VydmljZTEyMGdhdGV3YXkxMjA"),
    ("gateway120gateway120", "Z2F0ZXdheTEyMGdhdGV3YXkxMjA"),
    ("gateway120storage120", "Z2F0ZXdheTEyMHN0b3JhZ2UxMjA"),
    ("gateway120network120", "Z2F0ZXdheTEyMG5ldHdvcmsxMjA"),
    ("gateway120latency120", "Z2F0ZXdheTEyMGxhdGVuY3kxMjA"),
    ("storage120latency120", "c3RvcmFnZTEyMGxhdGVuY3kxMjA"),
    ("storage120buffer120", "c3RvcmFnZTEyMGJ1ZmZlcjEyMA"),
    ("storage120queue120", "c3RvcmFnZTEyMHF1ZXVlMTIw"),
    ("storage120worker120", "c3RvcmFnZTEyMHdvcmtlcjEyMA"),
    ("network120worker120", "bmV0d29yazEyMHdvcmtlcjEyMA"),
    ("network120kernel120", "bmV0d29yazEyMGtlcm5lbDEyMA"),
    ("network120signal120", "bmV0d29yazEyMHNpZ25hbDEyMA"),
    ("network120packet120", "bmV0d29yazEyMHBhY2tldDEyMA"),
    ("latency120packet120", "bGF0ZW5jeTEyMHBhY2tldDEyMA"),
    ("latency120router120", "bGF0ZW5jeTEyMHJvdXRlcjEyMA"),
    ("latency120cluster120", "bGF0ZW5jeTEyMGNsdXN0ZXIxMjA"),
    ("latency120mirror120", "bGF0ZW5jeTEyMG1pcnJvcjEyMA"),
    ("buffer120mirror120", "YnVmZmVyMTIwbWlycm9yMTIw"),
    ("buffer120filter120", "YnVmZmVyMTIwZmlsdGVyMTIw"),
    ("buffer120ranking120", "YnVmZmVyMTIwcmFua2luZzEyMA"),
    ("buffer120encoding120", "YnVmZmVyMTIwZW5jb2RpbmcxMjA"),
    ("queue120encoding120", "cXVldWUxMjBlbmNvZGluZzEyMA"),
    ("queue120mapping120", "cXVldWUxMjBtYXBwaW5nMTIw"),
    ("queue120record120", "cXVldWUxMjByZWNvcmQxMjA"),
    ("queue120candle120", "cXVldWUxMjBjYW5kbGUxMjA"),
    ("worker120candle120", "d29ya2VyMTIwY2FuZGxlMTIw"),
    ("worker120thread120", "d29ya2VyMTIwdGhyZWFkMTIw"),
    ("worker120kitten120", "d29ya2VyMTIwa2l0dGVuMTIw"),
    ("worker120sitting120", "d29ya2VyMTIwc2l0dGluZzEyMA"),
    ("kernel120sitting120", "a2VybmVsMTIwc2l0dGluZzEyMA"),
    ("kernel120agent120", "a2VybmVsMTIwYWdlbnQxMjA"),
    ("kernel120angle120", "a2VybmVsMTIwYW5nbGUxMjA"),
    ("kernel120universe120", "a2VybmVsMTIwdW5pdmVyc2UxMjA"),
    ("signal120universe120", "c2lnbmFsMTIwdW5pdmVyc2UxMjA"),
    ("signal120memory120", "c2lnbmFsMTIwbWVtb3J5MTIw"),
    ("signal120stream120", "c2lnbmFsMTIwc3RyZWFtMTIw"),
    ("signal120context120", "c2lnbmFsMTIwY29udGV4dDEyMA"),
    ("packet120context120", "cGFja2V0MTIwY29udGV4dDEyMA"),
    ("packet120knowledge120", "cGFja2V0MTIwa25vd2xlZGdlMTIw"),
    ("packet120vector120", "cGFja2V0MTIwdmVjdG9yMTIw"),
    ("packet120processor120", "cGFja2V0MTIwcHJvY2Vzc29yMTIw"),
    ("router120processor120", "cm91dGVyMTIwcHJvY2Vzc29yMTIw"),
    ("router120reasoning120", "cm91dGVyMTIwcmVhc29uaW5nMTIw"),
    ("router120machine120", "cm91dGVyMTIwbWFjaGluZTEyMA"),
    ("router120learning120", "cm91dGVyMTIwbGVhcm5pbmcxMjA"),
    ("cluster120learning120", "Y2x1c3RlcjEyMGxlYXJuaW5nMTIw"),
    ("cluster120model120", "Y2x1c3RlcjEyMG1vZGVsMTIw"),
    ("cluster120token120", "Y2x1c3RlcjEyMHRva2VuMTIw"),
    ("cluster120prompt120", "Y2x1c3RlcjEyMHByb21wdDEyMA"),
    ("mirror120prompt120", "bWlycm9yMTIwcHJvbXB0MTIw"),
    ("mirror120session120", "bWlycm9yMTIwc2Vzc2lvbjEyMA"),
    ("mirror120library120", "bWlycm9yMTIwbGlicmFyeTEyMA"),
    ("mirror120service120", "bWlycm9yMTIwc2VydmljZTEyMA"),
    ("filter120service120", "ZmlsdGVyMTIwc2VydmljZTEyMA"),
    ("filter120gateway120", "ZmlsdGVyMTIwZ2F0ZXdheTEyMA"),
    ("filter120storage120", "ZmlsdGVyMTIwc3RvcmFnZTEyMA"),
    ("filter120network120", "ZmlsdGVyMTIwbmV0d29yazEyMA"),
    ("ranking120network120", "cmFua2luZzEyMG5ldHdvcmsxMjA"),
    ("ranking120latency120", "cmFua2luZzEyMGxhdGVuY3kxMjA"),
    ("ranking120buffer120", "cmFua2luZzEyMGJ1ZmZlcjEyMA"),
    ("ranking120queue120", "cmFua2luZzEyMHF1ZXVlMTIw"),
    ("encoding120queue120", "ZW5jb2RpbmcxMjBxdWV1ZTEyMA"),
    ("encoding120worker120", "ZW5jb2RpbmcxMjB3b3JrZXIxMjA"),
    ("encoding120kernel120", "ZW5jb2RpbmcxMjBrZXJuZWwxMjA"),
    ("encoding120signal120", "ZW5jb2RpbmcxMjBzaWduYWwxMjA"),
    ("mapping120signal120", "bWFwcGluZzEyMHNpZ25hbDEyMA"),
    ("mapping120packet120", "bWFwcGluZzEyMHBhY2tldDEyMA"),
    ("mapping120router120", "bWFwcGluZzEyMHJvdXRlcjEyMA"),
    ("mapping120cluster120", "bWFwcGluZzEyMGNsdXN0ZXIxMjA"),
    ("record120cluster120", "cmVjb3JkMTIwY2x1c3RlcjEyMA"),
    ("record120mirror120", "cmVjb3JkMTIwbWlycm9yMTIw"),
    ("record120filter120", "cmVjb3JkMTIwZmlsdGVyMTIw"),
    ("record120ranking120", "cmVjb3JkMTIwcmFua2luZzEyMA"),
    ("candle120ranking120", "Y2FuZGxlMTIwcmFua2luZzEyMA"),
    ("candle120encoding120", "Y2FuZGxlMTIwZW5jb2RpbmcxMjA"),
    ("candle120mapping120", "Y2FuZGxlMTIwbWFwcGluZzEyMA"),
    ("candle120record120", "Y2FuZGxlMTIwcmVjb3JkMTIw"),
    ("thread120record120", "dGhyZWFkMTIwcmVjb3JkMTIw"),
    ("thread120candle120", "dGhyZWFkMTIwY2FuZGxlMTIw"),
    ("thread120thread120", "dGhyZWFkMTIwdGhyZWFkMTIw"),
    ("thread120kitten120", "dGhyZWFkMTIwa2l0dGVuMTIw"),
    (
        "round 120: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTIwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 120: agentuniverse is a framework for multi agents",
        "cm91bmQgMTIwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 120: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTIwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 120: the processor reads the record then stops",
        "cm91bmQgMTIwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 120: a worker pulls the next task from the queue",
        "cm91bmQgMTIwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 120: signals travel through the network layer",
        "cm91bmQgMTIwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 120: the gateway routes each request by policy",
        "cm91bmQgMTIwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 120: memory grows until the buffer is full",
        "cm91bmQgMTIwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 120: the cluster mirrors every packet twice",
        "cm91bmQgMTIwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 120: ranking uses tokens learned from the corpus",
        "cm91bmQgMTIwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 120: a long session ends when the candle dies",
        "cm91bmQgMTIwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 120: encode the prompt then map the result",
        "cm91bmQgMTIwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 120: the kernel wakes the worker at dawn",
        "cm91bmQgMTIwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 120: service latency drops after the patch",
        "cm91bmQgMTIwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 120: the library caches every vector it sees",
        "cm91bmQgMTIwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 120: agents argue then the debate resolves",
        "cm91bmQgMTIwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 120: the filter keeps only strong matches",
        "cm91bmQgMTIwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 120: the model answers with a short reply",
        "cm91bmQgMTIwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 120: the recorder stores the reasoning trace",
        "cm91bmQgMTIwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 120: the angel watches the processor run",
        "cm91bmQgMTIwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 120: angle of the vector decides the match",
        "cm91bmQgMTIwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 120: the candle burns twice as long at night",
        "cm91bmQgMTIwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 120: a mirror of the universe in one line",
        "cm91bmQgMTIwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 120: the queue drains before the storm", "cm91bmQgMTIwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
