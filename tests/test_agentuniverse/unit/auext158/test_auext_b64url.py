"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten158kitten158", "a2l0dGVuMTU4a2l0dGVuMTU4"),
    ("kitten158sitting158", "a2l0dGVuMTU4c2l0dGluZzE1OA"),
    ("kitten158agent158", "a2l0dGVuMTU4YWdlbnQxNTg"),
    ("kitten158angle158", "a2l0dGVuMTU4YW5nbGUxNTg"),
    ("sitting158angle158", "c2l0dGluZzE1OGFuZ2xlMTU4"),
    ("sitting158universe158", "c2l0dGluZzE1OHVuaXZlcnNlMTU4"),
    ("sitting158memory158", "c2l0dGluZzE1OG1lbW9yeTE1OA"),
    ("sitting158stream158", "c2l0dGluZzE1OHN0cmVhbTE1OA"),
    ("agent158stream158", "YWdlbnQxNThzdHJlYW0xNTg"),
    ("agent158context158", "YWdlbnQxNThjb250ZXh0MTU4"),
    ("agent158knowledge158", "YWdlbnQxNThrbm93bGVkZ2UxNTg"),
    ("agent158vector158", "YWdlbnQxNTh2ZWN0b3IxNTg"),
    ("angle158vector158", "YW5nbGUxNTh2ZWN0b3IxNTg"),
    ("angle158processor158", "YW5nbGUxNThwcm9jZXNzb3IxNTg"),
    ("angle158reasoning158", "YW5nbGUxNThyZWFzb25pbmcxNTg"),
    ("angle158machine158", "YW5nbGUxNThtYWNoaW5lMTU4"),
    ("universe158machine158", "dW5pdmVyc2UxNThtYWNoaW5lMTU4"),
    ("universe158learning158", "dW5pdmVyc2UxNThsZWFybmluZzE1OA"),
    ("universe158model158", "dW5pdmVyc2UxNThtb2RlbDE1OA"),
    ("universe158token158", "dW5pdmVyc2UxNTh0b2tlbjE1OA"),
    ("memory158token158", "bWVtb3J5MTU4dG9rZW4xNTg"),
    ("memory158prompt158", "bWVtb3J5MTU4cHJvbXB0MTU4"),
    ("memory158session158", "bWVtb3J5MTU4c2Vzc2lvbjE1OA"),
    ("memory158library158", "bWVtb3J5MTU4bGlicmFyeTE1OA"),
    ("stream158library158", "c3RyZWFtMTU4bGlicmFyeTE1OA"),
    ("stream158service158", "c3RyZWFtMTU4c2VydmljZTE1OA"),
    ("stream158gateway158", "c3RyZWFtMTU4Z2F0ZXdheTE1OA"),
    ("stream158storage158", "c3RyZWFtMTU4c3RvcmFnZTE1OA"),
    ("context158storage158", "Y29udGV4dDE1OHN0b3JhZ2UxNTg"),
    ("context158network158", "Y29udGV4dDE1OG5ldHdvcmsxNTg"),
    ("context158latency158", "Y29udGV4dDE1OGxhdGVuY3kxNTg"),
    ("context158buffer158", "Y29udGV4dDE1OGJ1ZmZlcjE1OA"),
    ("knowledge158buffer158", "a25vd2xlZGdlMTU4YnVmZmVyMTU4"),
    ("knowledge158queue158", "a25vd2xlZGdlMTU4cXVldWUxNTg"),
    ("knowledge158worker158", "a25vd2xlZGdlMTU4d29ya2VyMTU4"),
    ("knowledge158kernel158", "a25vd2xlZGdlMTU4a2VybmVsMTU4"),
    ("vector158kernel158", "dmVjdG9yMTU4a2VybmVsMTU4"),
    ("vector158signal158", "dmVjdG9yMTU4c2lnbmFsMTU4"),
    ("vector158packet158", "dmVjdG9yMTU4cGFja2V0MTU4"),
    ("vector158router158", "dmVjdG9yMTU4cm91dGVyMTU4"),
    ("processor158router158", "cHJvY2Vzc29yMTU4cm91dGVyMTU4"),
    ("processor158cluster158", "cHJvY2Vzc29yMTU4Y2x1c3RlcjE1OA"),
    ("processor158mirror158", "cHJvY2Vzc29yMTU4bWlycm9yMTU4"),
    ("processor158filter158", "cHJvY2Vzc29yMTU4ZmlsdGVyMTU4"),
    ("reasoning158filter158", "cmVhc29uaW5nMTU4ZmlsdGVyMTU4"),
    ("reasoning158ranking158", "cmVhc29uaW5nMTU4cmFua2luZzE1OA"),
    ("reasoning158encoding158", "cmVhc29uaW5nMTU4ZW5jb2RpbmcxNTg"),
    ("reasoning158mapping158", "cmVhc29uaW5nMTU4bWFwcGluZzE1OA"),
    ("machine158mapping158", "bWFjaGluZTE1OG1hcHBpbmcxNTg"),
    ("machine158record158", "bWFjaGluZTE1OHJlY29yZDE1OA"),
    ("machine158candle158", "bWFjaGluZTE1OGNhbmRsZTE1OA"),
    ("machine158thread158", "bWFjaGluZTE1OHRocmVhZDE1OA"),
    ("learning158thread158", "bGVhcm5pbmcxNTh0aHJlYWQxNTg"),
    ("learning158kitten158", "bGVhcm5pbmcxNThraXR0ZW4xNTg"),
    ("learning158sitting158", "bGVhcm5pbmcxNThzaXR0aW5nMTU4"),
    ("learning158agent158", "bGVhcm5pbmcxNThhZ2VudDE1OA"),
    ("model158agent158", "bW9kZWwxNThhZ2VudDE1OA"),
    ("model158angle158", "bW9kZWwxNThhbmdsZTE1OA"),
    ("model158universe158", "bW9kZWwxNTh1bml2ZXJzZTE1OA"),
    ("model158memory158", "bW9kZWwxNThtZW1vcnkxNTg"),
    ("token158memory158", "dG9rZW4xNThtZW1vcnkxNTg"),
    ("token158stream158", "dG9rZW4xNThzdHJlYW0xNTg"),
    ("token158context158", "dG9rZW4xNThjb250ZXh0MTU4"),
    ("token158knowledge158", "dG9rZW4xNThrbm93bGVkZ2UxNTg"),
    ("prompt158knowledge158", "cHJvbXB0MTU4a25vd2xlZGdlMTU4"),
    ("prompt158vector158", "cHJvbXB0MTU4dmVjdG9yMTU4"),
    ("prompt158processor158", "cHJvbXB0MTU4cHJvY2Vzc29yMTU4"),
    ("prompt158reasoning158", "cHJvbXB0MTU4cmVhc29uaW5nMTU4"),
    ("session158reasoning158", "c2Vzc2lvbjE1OHJlYXNvbmluZzE1OA"),
    ("session158machine158", "c2Vzc2lvbjE1OG1hY2hpbmUxNTg"),
    ("session158learning158", "c2Vzc2lvbjE1OGxlYXJuaW5nMTU4"),
    ("session158model158", "c2Vzc2lvbjE1OG1vZGVsMTU4"),
    ("library158model158", "bGlicmFyeTE1OG1vZGVsMTU4"),
    ("library158token158", "bGlicmFyeTE1OHRva2VuMTU4"),
    ("library158prompt158", "bGlicmFyeTE1OHByb21wdDE1OA"),
    ("library158session158", "bGlicmFyeTE1OHNlc3Npb24xNTg"),
    ("service158session158", "c2VydmljZTE1OHNlc3Npb24xNTg"),
    ("service158library158", "c2VydmljZTE1OGxpYnJhcnkxNTg"),
    ("service158service158", "c2VydmljZTE1OHNlcnZpY2UxNTg"),
    ("service158gateway158", "c2VydmljZTE1OGdhdGV3YXkxNTg"),
    ("gateway158gateway158", "Z2F0ZXdheTE1OGdhdGV3YXkxNTg"),
    ("gateway158storage158", "Z2F0ZXdheTE1OHN0b3JhZ2UxNTg"),
    ("gateway158network158", "Z2F0ZXdheTE1OG5ldHdvcmsxNTg"),
    ("gateway158latency158", "Z2F0ZXdheTE1OGxhdGVuY3kxNTg"),
    ("storage158latency158", "c3RvcmFnZTE1OGxhdGVuY3kxNTg"),
    ("storage158buffer158", "c3RvcmFnZTE1OGJ1ZmZlcjE1OA"),
    ("storage158queue158", "c3RvcmFnZTE1OHF1ZXVlMTU4"),
    ("storage158worker158", "c3RvcmFnZTE1OHdvcmtlcjE1OA"),
    ("network158worker158", "bmV0d29yazE1OHdvcmtlcjE1OA"),
    ("network158kernel158", "bmV0d29yazE1OGtlcm5lbDE1OA"),
    ("network158signal158", "bmV0d29yazE1OHNpZ25hbDE1OA"),
    ("network158packet158", "bmV0d29yazE1OHBhY2tldDE1OA"),
    ("latency158packet158", "bGF0ZW5jeTE1OHBhY2tldDE1OA"),
    ("latency158router158", "bGF0ZW5jeTE1OHJvdXRlcjE1OA"),
    ("latency158cluster158", "bGF0ZW5jeTE1OGNsdXN0ZXIxNTg"),
    ("latency158mirror158", "bGF0ZW5jeTE1OG1pcnJvcjE1OA"),
    ("buffer158mirror158", "YnVmZmVyMTU4bWlycm9yMTU4"),
    ("buffer158filter158", "YnVmZmVyMTU4ZmlsdGVyMTU4"),
    ("buffer158ranking158", "YnVmZmVyMTU4cmFua2luZzE1OA"),
    ("buffer158encoding158", "YnVmZmVyMTU4ZW5jb2RpbmcxNTg"),
    ("queue158encoding158", "cXVldWUxNThlbmNvZGluZzE1OA"),
    ("queue158mapping158", "cXVldWUxNThtYXBwaW5nMTU4"),
    ("queue158record158", "cXVldWUxNThyZWNvcmQxNTg"),
    ("queue158candle158", "cXVldWUxNThjYW5kbGUxNTg"),
    ("worker158candle158", "d29ya2VyMTU4Y2FuZGxlMTU4"),
    ("worker158thread158", "d29ya2VyMTU4dGhyZWFkMTU4"),
    ("worker158kitten158", "d29ya2VyMTU4a2l0dGVuMTU4"),
    ("worker158sitting158", "d29ya2VyMTU4c2l0dGluZzE1OA"),
    ("kernel158sitting158", "a2VybmVsMTU4c2l0dGluZzE1OA"),
    ("kernel158agent158", "a2VybmVsMTU4YWdlbnQxNTg"),
    ("kernel158angle158", "a2VybmVsMTU4YW5nbGUxNTg"),
    ("kernel158universe158", "a2VybmVsMTU4dW5pdmVyc2UxNTg"),
    ("signal158universe158", "c2lnbmFsMTU4dW5pdmVyc2UxNTg"),
    ("signal158memory158", "c2lnbmFsMTU4bWVtb3J5MTU4"),
    ("signal158stream158", "c2lnbmFsMTU4c3RyZWFtMTU4"),
    ("signal158context158", "c2lnbmFsMTU4Y29udGV4dDE1OA"),
    ("packet158context158", "cGFja2V0MTU4Y29udGV4dDE1OA"),
    ("packet158knowledge158", "cGFja2V0MTU4a25vd2xlZGdlMTU4"),
    ("packet158vector158", "cGFja2V0MTU4dmVjdG9yMTU4"),
    ("packet158processor158", "cGFja2V0MTU4cHJvY2Vzc29yMTU4"),
    ("router158processor158", "cm91dGVyMTU4cHJvY2Vzc29yMTU4"),
    ("router158reasoning158", "cm91dGVyMTU4cmVhc29uaW5nMTU4"),
    ("router158machine158", "cm91dGVyMTU4bWFjaGluZTE1OA"),
    ("router158learning158", "cm91dGVyMTU4bGVhcm5pbmcxNTg"),
    ("cluster158learning158", "Y2x1c3RlcjE1OGxlYXJuaW5nMTU4"),
    ("cluster158model158", "Y2x1c3RlcjE1OG1vZGVsMTU4"),
    ("cluster158token158", "Y2x1c3RlcjE1OHRva2VuMTU4"),
    ("cluster158prompt158", "Y2x1c3RlcjE1OHByb21wdDE1OA"),
    ("mirror158prompt158", "bWlycm9yMTU4cHJvbXB0MTU4"),
    ("mirror158session158", "bWlycm9yMTU4c2Vzc2lvbjE1OA"),
    ("mirror158library158", "bWlycm9yMTU4bGlicmFyeTE1OA"),
    ("mirror158service158", "bWlycm9yMTU4c2VydmljZTE1OA"),
    ("filter158service158", "ZmlsdGVyMTU4c2VydmljZTE1OA"),
    ("filter158gateway158", "ZmlsdGVyMTU4Z2F0ZXdheTE1OA"),
    ("filter158storage158", "ZmlsdGVyMTU4c3RvcmFnZTE1OA"),
    ("filter158network158", "ZmlsdGVyMTU4bmV0d29yazE1OA"),
    ("ranking158network158", "cmFua2luZzE1OG5ldHdvcmsxNTg"),
    ("ranking158latency158", "cmFua2luZzE1OGxhdGVuY3kxNTg"),
    ("ranking158buffer158", "cmFua2luZzE1OGJ1ZmZlcjE1OA"),
    ("ranking158queue158", "cmFua2luZzE1OHF1ZXVlMTU4"),
    ("encoding158queue158", "ZW5jb2RpbmcxNThxdWV1ZTE1OA"),
    ("encoding158worker158", "ZW5jb2RpbmcxNTh3b3JrZXIxNTg"),
    ("encoding158kernel158", "ZW5jb2RpbmcxNThrZXJuZWwxNTg"),
    ("encoding158signal158", "ZW5jb2RpbmcxNThzaWduYWwxNTg"),
    ("mapping158signal158", "bWFwcGluZzE1OHNpZ25hbDE1OA"),
    ("mapping158packet158", "bWFwcGluZzE1OHBhY2tldDE1OA"),
    ("mapping158router158", "bWFwcGluZzE1OHJvdXRlcjE1OA"),
    ("mapping158cluster158", "bWFwcGluZzE1OGNsdXN0ZXIxNTg"),
    ("record158cluster158", "cmVjb3JkMTU4Y2x1c3RlcjE1OA"),
    ("record158mirror158", "cmVjb3JkMTU4bWlycm9yMTU4"),
    ("record158filter158", "cmVjb3JkMTU4ZmlsdGVyMTU4"),
    ("record158ranking158", "cmVjb3JkMTU4cmFua2luZzE1OA"),
    ("candle158ranking158", "Y2FuZGxlMTU4cmFua2luZzE1OA"),
    ("candle158encoding158", "Y2FuZGxlMTU4ZW5jb2RpbmcxNTg"),
    ("candle158mapping158", "Y2FuZGxlMTU4bWFwcGluZzE1OA"),
    ("candle158record158", "Y2FuZGxlMTU4cmVjb3JkMTU4"),
    ("thread158record158", "dGhyZWFkMTU4cmVjb3JkMTU4"),
    ("thread158candle158", "dGhyZWFkMTU4Y2FuZGxlMTU4"),
    ("thread158thread158", "dGhyZWFkMTU4dGhyZWFkMTU4"),
    ("thread158kitten158", "dGhyZWFkMTU4a2l0dGVuMTU4"),
    (
        "round 158: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTU4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 158: agentuniverse is a framework for multi agents",
        "cm91bmQgMTU4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 158: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTU4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 158: the processor reads the record then stops",
        "cm91bmQgMTU4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 158: a worker pulls the next task from the queue",
        "cm91bmQgMTU4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 158: signals travel through the network layer",
        "cm91bmQgMTU4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 158: the gateway routes each request by policy",
        "cm91bmQgMTU4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 158: memory grows until the buffer is full",
        "cm91bmQgMTU4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 158: the cluster mirrors every packet twice",
        "cm91bmQgMTU4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 158: ranking uses tokens learned from the corpus",
        "cm91bmQgMTU4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 158: a long session ends when the candle dies",
        "cm91bmQgMTU4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 158: encode the prompt then map the result",
        "cm91bmQgMTU4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 158: the kernel wakes the worker at dawn",
        "cm91bmQgMTU4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 158: service latency drops after the patch",
        "cm91bmQgMTU4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 158: the library caches every vector it sees",
        "cm91bmQgMTU4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 158: agents argue then the debate resolves",
        "cm91bmQgMTU4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 158: the filter keeps only strong matches",
        "cm91bmQgMTU4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 158: the model answers with a short reply",
        "cm91bmQgMTU4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 158: the recorder stores the reasoning trace",
        "cm91bmQgMTU4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 158: the angel watches the processor run",
        "cm91bmQgMTU4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 158: angle of the vector decides the match",
        "cm91bmQgMTU4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 158: the candle burns twice as long at night",
        "cm91bmQgMTU4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 158: a mirror of the universe in one line",
        "cm91bmQgMTU4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 158: the queue drains before the storm", "cm91bmQgMTU4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
