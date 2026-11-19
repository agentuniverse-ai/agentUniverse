"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten121kitten121", "a2l0dGVuMTIxa2l0dGVuMTIx"),
    ("kitten121sitting121", "a2l0dGVuMTIxc2l0dGluZzEyMQ"),
    ("kitten121agent121", "a2l0dGVuMTIxYWdlbnQxMjE"),
    ("kitten121angle121", "a2l0dGVuMTIxYW5nbGUxMjE"),
    ("sitting121angle121", "c2l0dGluZzEyMWFuZ2xlMTIx"),
    ("sitting121universe121", "c2l0dGluZzEyMXVuaXZlcnNlMTIx"),
    ("sitting121memory121", "c2l0dGluZzEyMW1lbW9yeTEyMQ"),
    ("sitting121stream121", "c2l0dGluZzEyMXN0cmVhbTEyMQ"),
    ("agent121stream121", "YWdlbnQxMjFzdHJlYW0xMjE"),
    ("agent121context121", "YWdlbnQxMjFjb250ZXh0MTIx"),
    ("agent121knowledge121", "YWdlbnQxMjFrbm93bGVkZ2UxMjE"),
    ("agent121vector121", "YWdlbnQxMjF2ZWN0b3IxMjE"),
    ("angle121vector121", "YW5nbGUxMjF2ZWN0b3IxMjE"),
    ("angle121processor121", "YW5nbGUxMjFwcm9jZXNzb3IxMjE"),
    ("angle121reasoning121", "YW5nbGUxMjFyZWFzb25pbmcxMjE"),
    ("angle121machine121", "YW5nbGUxMjFtYWNoaW5lMTIx"),
    ("universe121machine121", "dW5pdmVyc2UxMjFtYWNoaW5lMTIx"),
    ("universe121learning121", "dW5pdmVyc2UxMjFsZWFybmluZzEyMQ"),
    ("universe121model121", "dW5pdmVyc2UxMjFtb2RlbDEyMQ"),
    ("universe121token121", "dW5pdmVyc2UxMjF0b2tlbjEyMQ"),
    ("memory121token121", "bWVtb3J5MTIxdG9rZW4xMjE"),
    ("memory121prompt121", "bWVtb3J5MTIxcHJvbXB0MTIx"),
    ("memory121session121", "bWVtb3J5MTIxc2Vzc2lvbjEyMQ"),
    ("memory121library121", "bWVtb3J5MTIxbGlicmFyeTEyMQ"),
    ("stream121library121", "c3RyZWFtMTIxbGlicmFyeTEyMQ"),
    ("stream121service121", "c3RyZWFtMTIxc2VydmljZTEyMQ"),
    ("stream121gateway121", "c3RyZWFtMTIxZ2F0ZXdheTEyMQ"),
    ("stream121storage121", "c3RyZWFtMTIxc3RvcmFnZTEyMQ"),
    ("context121storage121", "Y29udGV4dDEyMXN0b3JhZ2UxMjE"),
    ("context121network121", "Y29udGV4dDEyMW5ldHdvcmsxMjE"),
    ("context121latency121", "Y29udGV4dDEyMWxhdGVuY3kxMjE"),
    ("context121buffer121", "Y29udGV4dDEyMWJ1ZmZlcjEyMQ"),
    ("knowledge121buffer121", "a25vd2xlZGdlMTIxYnVmZmVyMTIx"),
    ("knowledge121queue121", "a25vd2xlZGdlMTIxcXVldWUxMjE"),
    ("knowledge121worker121", "a25vd2xlZGdlMTIxd29ya2VyMTIx"),
    ("knowledge121kernel121", "a25vd2xlZGdlMTIxa2VybmVsMTIx"),
    ("vector121kernel121", "dmVjdG9yMTIxa2VybmVsMTIx"),
    ("vector121signal121", "dmVjdG9yMTIxc2lnbmFsMTIx"),
    ("vector121packet121", "dmVjdG9yMTIxcGFja2V0MTIx"),
    ("vector121router121", "dmVjdG9yMTIxcm91dGVyMTIx"),
    ("processor121router121", "cHJvY2Vzc29yMTIxcm91dGVyMTIx"),
    ("processor121cluster121", "cHJvY2Vzc29yMTIxY2x1c3RlcjEyMQ"),
    ("processor121mirror121", "cHJvY2Vzc29yMTIxbWlycm9yMTIx"),
    ("processor121filter121", "cHJvY2Vzc29yMTIxZmlsdGVyMTIx"),
    ("reasoning121filter121", "cmVhc29uaW5nMTIxZmlsdGVyMTIx"),
    ("reasoning121ranking121", "cmVhc29uaW5nMTIxcmFua2luZzEyMQ"),
    ("reasoning121encoding121", "cmVhc29uaW5nMTIxZW5jb2RpbmcxMjE"),
    ("reasoning121mapping121", "cmVhc29uaW5nMTIxbWFwcGluZzEyMQ"),
    ("machine121mapping121", "bWFjaGluZTEyMW1hcHBpbmcxMjE"),
    ("machine121record121", "bWFjaGluZTEyMXJlY29yZDEyMQ"),
    ("machine121candle121", "bWFjaGluZTEyMWNhbmRsZTEyMQ"),
    ("machine121thread121", "bWFjaGluZTEyMXRocmVhZDEyMQ"),
    ("learning121thread121", "bGVhcm5pbmcxMjF0aHJlYWQxMjE"),
    ("learning121kitten121", "bGVhcm5pbmcxMjFraXR0ZW4xMjE"),
    ("learning121sitting121", "bGVhcm5pbmcxMjFzaXR0aW5nMTIx"),
    ("learning121agent121", "bGVhcm5pbmcxMjFhZ2VudDEyMQ"),
    ("model121agent121", "bW9kZWwxMjFhZ2VudDEyMQ"),
    ("model121angle121", "bW9kZWwxMjFhbmdsZTEyMQ"),
    ("model121universe121", "bW9kZWwxMjF1bml2ZXJzZTEyMQ"),
    ("model121memory121", "bW9kZWwxMjFtZW1vcnkxMjE"),
    ("token121memory121", "dG9rZW4xMjFtZW1vcnkxMjE"),
    ("token121stream121", "dG9rZW4xMjFzdHJlYW0xMjE"),
    ("token121context121", "dG9rZW4xMjFjb250ZXh0MTIx"),
    ("token121knowledge121", "dG9rZW4xMjFrbm93bGVkZ2UxMjE"),
    ("prompt121knowledge121", "cHJvbXB0MTIxa25vd2xlZGdlMTIx"),
    ("prompt121vector121", "cHJvbXB0MTIxdmVjdG9yMTIx"),
    ("prompt121processor121", "cHJvbXB0MTIxcHJvY2Vzc29yMTIx"),
    ("prompt121reasoning121", "cHJvbXB0MTIxcmVhc29uaW5nMTIx"),
    ("session121reasoning121", "c2Vzc2lvbjEyMXJlYXNvbmluZzEyMQ"),
    ("session121machine121", "c2Vzc2lvbjEyMW1hY2hpbmUxMjE"),
    ("session121learning121", "c2Vzc2lvbjEyMWxlYXJuaW5nMTIx"),
    ("session121model121", "c2Vzc2lvbjEyMW1vZGVsMTIx"),
    ("library121model121", "bGlicmFyeTEyMW1vZGVsMTIx"),
    ("library121token121", "bGlicmFyeTEyMXRva2VuMTIx"),
    ("library121prompt121", "bGlicmFyeTEyMXByb21wdDEyMQ"),
    ("library121session121", "bGlicmFyeTEyMXNlc3Npb24xMjE"),
    ("service121session121", "c2VydmljZTEyMXNlc3Npb24xMjE"),
    ("service121library121", "c2VydmljZTEyMWxpYnJhcnkxMjE"),
    ("service121service121", "c2VydmljZTEyMXNlcnZpY2UxMjE"),
    ("service121gateway121", "c2VydmljZTEyMWdhdGV3YXkxMjE"),
    ("gateway121gateway121", "Z2F0ZXdheTEyMWdhdGV3YXkxMjE"),
    ("gateway121storage121", "Z2F0ZXdheTEyMXN0b3JhZ2UxMjE"),
    ("gateway121network121", "Z2F0ZXdheTEyMW5ldHdvcmsxMjE"),
    ("gateway121latency121", "Z2F0ZXdheTEyMWxhdGVuY3kxMjE"),
    ("storage121latency121", "c3RvcmFnZTEyMWxhdGVuY3kxMjE"),
    ("storage121buffer121", "c3RvcmFnZTEyMWJ1ZmZlcjEyMQ"),
    ("storage121queue121", "c3RvcmFnZTEyMXF1ZXVlMTIx"),
    ("storage121worker121", "c3RvcmFnZTEyMXdvcmtlcjEyMQ"),
    ("network121worker121", "bmV0d29yazEyMXdvcmtlcjEyMQ"),
    ("network121kernel121", "bmV0d29yazEyMWtlcm5lbDEyMQ"),
    ("network121signal121", "bmV0d29yazEyMXNpZ25hbDEyMQ"),
    ("network121packet121", "bmV0d29yazEyMXBhY2tldDEyMQ"),
    ("latency121packet121", "bGF0ZW5jeTEyMXBhY2tldDEyMQ"),
    ("latency121router121", "bGF0ZW5jeTEyMXJvdXRlcjEyMQ"),
    ("latency121cluster121", "bGF0ZW5jeTEyMWNsdXN0ZXIxMjE"),
    ("latency121mirror121", "bGF0ZW5jeTEyMW1pcnJvcjEyMQ"),
    ("buffer121mirror121", "YnVmZmVyMTIxbWlycm9yMTIx"),
    ("buffer121filter121", "YnVmZmVyMTIxZmlsdGVyMTIx"),
    ("buffer121ranking121", "YnVmZmVyMTIxcmFua2luZzEyMQ"),
    ("buffer121encoding121", "YnVmZmVyMTIxZW5jb2RpbmcxMjE"),
    ("queue121encoding121", "cXVldWUxMjFlbmNvZGluZzEyMQ"),
    ("queue121mapping121", "cXVldWUxMjFtYXBwaW5nMTIx"),
    ("queue121record121", "cXVldWUxMjFyZWNvcmQxMjE"),
    ("queue121candle121", "cXVldWUxMjFjYW5kbGUxMjE"),
    ("worker121candle121", "d29ya2VyMTIxY2FuZGxlMTIx"),
    ("worker121thread121", "d29ya2VyMTIxdGhyZWFkMTIx"),
    ("worker121kitten121", "d29ya2VyMTIxa2l0dGVuMTIx"),
    ("worker121sitting121", "d29ya2VyMTIxc2l0dGluZzEyMQ"),
    ("kernel121sitting121", "a2VybmVsMTIxc2l0dGluZzEyMQ"),
    ("kernel121agent121", "a2VybmVsMTIxYWdlbnQxMjE"),
    ("kernel121angle121", "a2VybmVsMTIxYW5nbGUxMjE"),
    ("kernel121universe121", "a2VybmVsMTIxdW5pdmVyc2UxMjE"),
    ("signal121universe121", "c2lnbmFsMTIxdW5pdmVyc2UxMjE"),
    ("signal121memory121", "c2lnbmFsMTIxbWVtb3J5MTIx"),
    ("signal121stream121", "c2lnbmFsMTIxc3RyZWFtMTIx"),
    ("signal121context121", "c2lnbmFsMTIxY29udGV4dDEyMQ"),
    ("packet121context121", "cGFja2V0MTIxY29udGV4dDEyMQ"),
    ("packet121knowledge121", "cGFja2V0MTIxa25vd2xlZGdlMTIx"),
    ("packet121vector121", "cGFja2V0MTIxdmVjdG9yMTIx"),
    ("packet121processor121", "cGFja2V0MTIxcHJvY2Vzc29yMTIx"),
    ("router121processor121", "cm91dGVyMTIxcHJvY2Vzc29yMTIx"),
    ("router121reasoning121", "cm91dGVyMTIxcmVhc29uaW5nMTIx"),
    ("router121machine121", "cm91dGVyMTIxbWFjaGluZTEyMQ"),
    ("router121learning121", "cm91dGVyMTIxbGVhcm5pbmcxMjE"),
    ("cluster121learning121", "Y2x1c3RlcjEyMWxlYXJuaW5nMTIx"),
    ("cluster121model121", "Y2x1c3RlcjEyMW1vZGVsMTIx"),
    ("cluster121token121", "Y2x1c3RlcjEyMXRva2VuMTIx"),
    ("cluster121prompt121", "Y2x1c3RlcjEyMXByb21wdDEyMQ"),
    ("mirror121prompt121", "bWlycm9yMTIxcHJvbXB0MTIx"),
    ("mirror121session121", "bWlycm9yMTIxc2Vzc2lvbjEyMQ"),
    ("mirror121library121", "bWlycm9yMTIxbGlicmFyeTEyMQ"),
    ("mirror121service121", "bWlycm9yMTIxc2VydmljZTEyMQ"),
    ("filter121service121", "ZmlsdGVyMTIxc2VydmljZTEyMQ"),
    ("filter121gateway121", "ZmlsdGVyMTIxZ2F0ZXdheTEyMQ"),
    ("filter121storage121", "ZmlsdGVyMTIxc3RvcmFnZTEyMQ"),
    ("filter121network121", "ZmlsdGVyMTIxbmV0d29yazEyMQ"),
    ("ranking121network121", "cmFua2luZzEyMW5ldHdvcmsxMjE"),
    ("ranking121latency121", "cmFua2luZzEyMWxhdGVuY3kxMjE"),
    ("ranking121buffer121", "cmFua2luZzEyMWJ1ZmZlcjEyMQ"),
    ("ranking121queue121", "cmFua2luZzEyMXF1ZXVlMTIx"),
    ("encoding121queue121", "ZW5jb2RpbmcxMjFxdWV1ZTEyMQ"),
    ("encoding121worker121", "ZW5jb2RpbmcxMjF3b3JrZXIxMjE"),
    ("encoding121kernel121", "ZW5jb2RpbmcxMjFrZXJuZWwxMjE"),
    ("encoding121signal121", "ZW5jb2RpbmcxMjFzaWduYWwxMjE"),
    ("mapping121signal121", "bWFwcGluZzEyMXNpZ25hbDEyMQ"),
    ("mapping121packet121", "bWFwcGluZzEyMXBhY2tldDEyMQ"),
    ("mapping121router121", "bWFwcGluZzEyMXJvdXRlcjEyMQ"),
    ("mapping121cluster121", "bWFwcGluZzEyMWNsdXN0ZXIxMjE"),
    ("record121cluster121", "cmVjb3JkMTIxY2x1c3RlcjEyMQ"),
    ("record121mirror121", "cmVjb3JkMTIxbWlycm9yMTIx"),
    ("record121filter121", "cmVjb3JkMTIxZmlsdGVyMTIx"),
    ("record121ranking121", "cmVjb3JkMTIxcmFua2luZzEyMQ"),
    ("candle121ranking121", "Y2FuZGxlMTIxcmFua2luZzEyMQ"),
    ("candle121encoding121", "Y2FuZGxlMTIxZW5jb2RpbmcxMjE"),
    ("candle121mapping121", "Y2FuZGxlMTIxbWFwcGluZzEyMQ"),
    ("candle121record121", "Y2FuZGxlMTIxcmVjb3JkMTIx"),
    ("thread121record121", "dGhyZWFkMTIxcmVjb3JkMTIx"),
    ("thread121candle121", "dGhyZWFkMTIxY2FuZGxlMTIx"),
    ("thread121thread121", "dGhyZWFkMTIxdGhyZWFkMTIx"),
    ("thread121kitten121", "dGhyZWFkMTIxa2l0dGVuMTIx"),
    (
        "round 121: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTIxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 121: agentuniverse is a framework for multi agents",
        "cm91bmQgMTIxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 121: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTIxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 121: the processor reads the record then stops",
        "cm91bmQgMTIxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 121: a worker pulls the next task from the queue",
        "cm91bmQgMTIxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 121: signals travel through the network layer",
        "cm91bmQgMTIxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 121: the gateway routes each request by policy",
        "cm91bmQgMTIxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 121: memory grows until the buffer is full",
        "cm91bmQgMTIxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 121: the cluster mirrors every packet twice",
        "cm91bmQgMTIxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 121: ranking uses tokens learned from the corpus",
        "cm91bmQgMTIxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 121: a long session ends when the candle dies",
        "cm91bmQgMTIxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 121: encode the prompt then map the result",
        "cm91bmQgMTIxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 121: the kernel wakes the worker at dawn",
        "cm91bmQgMTIxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 121: service latency drops after the patch",
        "cm91bmQgMTIxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 121: the library caches every vector it sees",
        "cm91bmQgMTIxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 121: agents argue then the debate resolves",
        "cm91bmQgMTIxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 121: the filter keeps only strong matches",
        "cm91bmQgMTIxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 121: the model answers with a short reply",
        "cm91bmQgMTIxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 121: the recorder stores the reasoning trace",
        "cm91bmQgMTIxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 121: the angel watches the processor run",
        "cm91bmQgMTIxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 121: angle of the vector decides the match",
        "cm91bmQgMTIxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 121: the candle burns twice as long at night",
        "cm91bmQgMTIxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 121: a mirror of the universe in one line",
        "cm91bmQgMTIxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 121: the queue drains before the storm", "cm91bmQgMTIxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
