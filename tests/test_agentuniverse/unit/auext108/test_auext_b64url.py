"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten108kitten108", "a2l0dGVuMTA4a2l0dGVuMTA4"),
    ("kitten108sitting108", "a2l0dGVuMTA4c2l0dGluZzEwOA"),
    ("kitten108agent108", "a2l0dGVuMTA4YWdlbnQxMDg"),
    ("kitten108angle108", "a2l0dGVuMTA4YW5nbGUxMDg"),
    ("sitting108angle108", "c2l0dGluZzEwOGFuZ2xlMTA4"),
    ("sitting108universe108", "c2l0dGluZzEwOHVuaXZlcnNlMTA4"),
    ("sitting108memory108", "c2l0dGluZzEwOG1lbW9yeTEwOA"),
    ("sitting108stream108", "c2l0dGluZzEwOHN0cmVhbTEwOA"),
    ("agent108stream108", "YWdlbnQxMDhzdHJlYW0xMDg"),
    ("agent108context108", "YWdlbnQxMDhjb250ZXh0MTA4"),
    ("agent108knowledge108", "YWdlbnQxMDhrbm93bGVkZ2UxMDg"),
    ("agent108vector108", "YWdlbnQxMDh2ZWN0b3IxMDg"),
    ("angle108vector108", "YW5nbGUxMDh2ZWN0b3IxMDg"),
    ("angle108processor108", "YW5nbGUxMDhwcm9jZXNzb3IxMDg"),
    ("angle108reasoning108", "YW5nbGUxMDhyZWFzb25pbmcxMDg"),
    ("angle108machine108", "YW5nbGUxMDhtYWNoaW5lMTA4"),
    ("universe108machine108", "dW5pdmVyc2UxMDhtYWNoaW5lMTA4"),
    ("universe108learning108", "dW5pdmVyc2UxMDhsZWFybmluZzEwOA"),
    ("universe108model108", "dW5pdmVyc2UxMDhtb2RlbDEwOA"),
    ("universe108token108", "dW5pdmVyc2UxMDh0b2tlbjEwOA"),
    ("memory108token108", "bWVtb3J5MTA4dG9rZW4xMDg"),
    ("memory108prompt108", "bWVtb3J5MTA4cHJvbXB0MTA4"),
    ("memory108session108", "bWVtb3J5MTA4c2Vzc2lvbjEwOA"),
    ("memory108library108", "bWVtb3J5MTA4bGlicmFyeTEwOA"),
    ("stream108library108", "c3RyZWFtMTA4bGlicmFyeTEwOA"),
    ("stream108service108", "c3RyZWFtMTA4c2VydmljZTEwOA"),
    ("stream108gateway108", "c3RyZWFtMTA4Z2F0ZXdheTEwOA"),
    ("stream108storage108", "c3RyZWFtMTA4c3RvcmFnZTEwOA"),
    ("context108storage108", "Y29udGV4dDEwOHN0b3JhZ2UxMDg"),
    ("context108network108", "Y29udGV4dDEwOG5ldHdvcmsxMDg"),
    ("context108latency108", "Y29udGV4dDEwOGxhdGVuY3kxMDg"),
    ("context108buffer108", "Y29udGV4dDEwOGJ1ZmZlcjEwOA"),
    ("knowledge108buffer108", "a25vd2xlZGdlMTA4YnVmZmVyMTA4"),
    ("knowledge108queue108", "a25vd2xlZGdlMTA4cXVldWUxMDg"),
    ("knowledge108worker108", "a25vd2xlZGdlMTA4d29ya2VyMTA4"),
    ("knowledge108kernel108", "a25vd2xlZGdlMTA4a2VybmVsMTA4"),
    ("vector108kernel108", "dmVjdG9yMTA4a2VybmVsMTA4"),
    ("vector108signal108", "dmVjdG9yMTA4c2lnbmFsMTA4"),
    ("vector108packet108", "dmVjdG9yMTA4cGFja2V0MTA4"),
    ("vector108router108", "dmVjdG9yMTA4cm91dGVyMTA4"),
    ("processor108router108", "cHJvY2Vzc29yMTA4cm91dGVyMTA4"),
    ("processor108cluster108", "cHJvY2Vzc29yMTA4Y2x1c3RlcjEwOA"),
    ("processor108mirror108", "cHJvY2Vzc29yMTA4bWlycm9yMTA4"),
    ("processor108filter108", "cHJvY2Vzc29yMTA4ZmlsdGVyMTA4"),
    ("reasoning108filter108", "cmVhc29uaW5nMTA4ZmlsdGVyMTA4"),
    ("reasoning108ranking108", "cmVhc29uaW5nMTA4cmFua2luZzEwOA"),
    ("reasoning108encoding108", "cmVhc29uaW5nMTA4ZW5jb2RpbmcxMDg"),
    ("reasoning108mapping108", "cmVhc29uaW5nMTA4bWFwcGluZzEwOA"),
    ("machine108mapping108", "bWFjaGluZTEwOG1hcHBpbmcxMDg"),
    ("machine108record108", "bWFjaGluZTEwOHJlY29yZDEwOA"),
    ("machine108candle108", "bWFjaGluZTEwOGNhbmRsZTEwOA"),
    ("machine108thread108", "bWFjaGluZTEwOHRocmVhZDEwOA"),
    ("learning108thread108", "bGVhcm5pbmcxMDh0aHJlYWQxMDg"),
    ("learning108kitten108", "bGVhcm5pbmcxMDhraXR0ZW4xMDg"),
    ("learning108sitting108", "bGVhcm5pbmcxMDhzaXR0aW5nMTA4"),
    ("learning108agent108", "bGVhcm5pbmcxMDhhZ2VudDEwOA"),
    ("model108agent108", "bW9kZWwxMDhhZ2VudDEwOA"),
    ("model108angle108", "bW9kZWwxMDhhbmdsZTEwOA"),
    ("model108universe108", "bW9kZWwxMDh1bml2ZXJzZTEwOA"),
    ("model108memory108", "bW9kZWwxMDhtZW1vcnkxMDg"),
    ("token108memory108", "dG9rZW4xMDhtZW1vcnkxMDg"),
    ("token108stream108", "dG9rZW4xMDhzdHJlYW0xMDg"),
    ("token108context108", "dG9rZW4xMDhjb250ZXh0MTA4"),
    ("token108knowledge108", "dG9rZW4xMDhrbm93bGVkZ2UxMDg"),
    ("prompt108knowledge108", "cHJvbXB0MTA4a25vd2xlZGdlMTA4"),
    ("prompt108vector108", "cHJvbXB0MTA4dmVjdG9yMTA4"),
    ("prompt108processor108", "cHJvbXB0MTA4cHJvY2Vzc29yMTA4"),
    ("prompt108reasoning108", "cHJvbXB0MTA4cmVhc29uaW5nMTA4"),
    ("session108reasoning108", "c2Vzc2lvbjEwOHJlYXNvbmluZzEwOA"),
    ("session108machine108", "c2Vzc2lvbjEwOG1hY2hpbmUxMDg"),
    ("session108learning108", "c2Vzc2lvbjEwOGxlYXJuaW5nMTA4"),
    ("session108model108", "c2Vzc2lvbjEwOG1vZGVsMTA4"),
    ("library108model108", "bGlicmFyeTEwOG1vZGVsMTA4"),
    ("library108token108", "bGlicmFyeTEwOHRva2VuMTA4"),
    ("library108prompt108", "bGlicmFyeTEwOHByb21wdDEwOA"),
    ("library108session108", "bGlicmFyeTEwOHNlc3Npb24xMDg"),
    ("service108session108", "c2VydmljZTEwOHNlc3Npb24xMDg"),
    ("service108library108", "c2VydmljZTEwOGxpYnJhcnkxMDg"),
    ("service108service108", "c2VydmljZTEwOHNlcnZpY2UxMDg"),
    ("service108gateway108", "c2VydmljZTEwOGdhdGV3YXkxMDg"),
    ("gateway108gateway108", "Z2F0ZXdheTEwOGdhdGV3YXkxMDg"),
    ("gateway108storage108", "Z2F0ZXdheTEwOHN0b3JhZ2UxMDg"),
    ("gateway108network108", "Z2F0ZXdheTEwOG5ldHdvcmsxMDg"),
    ("gateway108latency108", "Z2F0ZXdheTEwOGxhdGVuY3kxMDg"),
    ("storage108latency108", "c3RvcmFnZTEwOGxhdGVuY3kxMDg"),
    ("storage108buffer108", "c3RvcmFnZTEwOGJ1ZmZlcjEwOA"),
    ("storage108queue108", "c3RvcmFnZTEwOHF1ZXVlMTA4"),
    ("storage108worker108", "c3RvcmFnZTEwOHdvcmtlcjEwOA"),
    ("network108worker108", "bmV0d29yazEwOHdvcmtlcjEwOA"),
    ("network108kernel108", "bmV0d29yazEwOGtlcm5lbDEwOA"),
    ("network108signal108", "bmV0d29yazEwOHNpZ25hbDEwOA"),
    ("network108packet108", "bmV0d29yazEwOHBhY2tldDEwOA"),
    ("latency108packet108", "bGF0ZW5jeTEwOHBhY2tldDEwOA"),
    ("latency108router108", "bGF0ZW5jeTEwOHJvdXRlcjEwOA"),
    ("latency108cluster108", "bGF0ZW5jeTEwOGNsdXN0ZXIxMDg"),
    ("latency108mirror108", "bGF0ZW5jeTEwOG1pcnJvcjEwOA"),
    ("buffer108mirror108", "YnVmZmVyMTA4bWlycm9yMTA4"),
    ("buffer108filter108", "YnVmZmVyMTA4ZmlsdGVyMTA4"),
    ("buffer108ranking108", "YnVmZmVyMTA4cmFua2luZzEwOA"),
    ("buffer108encoding108", "YnVmZmVyMTA4ZW5jb2RpbmcxMDg"),
    ("queue108encoding108", "cXVldWUxMDhlbmNvZGluZzEwOA"),
    ("queue108mapping108", "cXVldWUxMDhtYXBwaW5nMTA4"),
    ("queue108record108", "cXVldWUxMDhyZWNvcmQxMDg"),
    ("queue108candle108", "cXVldWUxMDhjYW5kbGUxMDg"),
    ("worker108candle108", "d29ya2VyMTA4Y2FuZGxlMTA4"),
    ("worker108thread108", "d29ya2VyMTA4dGhyZWFkMTA4"),
    ("worker108kitten108", "d29ya2VyMTA4a2l0dGVuMTA4"),
    ("worker108sitting108", "d29ya2VyMTA4c2l0dGluZzEwOA"),
    ("kernel108sitting108", "a2VybmVsMTA4c2l0dGluZzEwOA"),
    ("kernel108agent108", "a2VybmVsMTA4YWdlbnQxMDg"),
    ("kernel108angle108", "a2VybmVsMTA4YW5nbGUxMDg"),
    ("kernel108universe108", "a2VybmVsMTA4dW5pdmVyc2UxMDg"),
    ("signal108universe108", "c2lnbmFsMTA4dW5pdmVyc2UxMDg"),
    ("signal108memory108", "c2lnbmFsMTA4bWVtb3J5MTA4"),
    ("signal108stream108", "c2lnbmFsMTA4c3RyZWFtMTA4"),
    ("signal108context108", "c2lnbmFsMTA4Y29udGV4dDEwOA"),
    ("packet108context108", "cGFja2V0MTA4Y29udGV4dDEwOA"),
    ("packet108knowledge108", "cGFja2V0MTA4a25vd2xlZGdlMTA4"),
    ("packet108vector108", "cGFja2V0MTA4dmVjdG9yMTA4"),
    ("packet108processor108", "cGFja2V0MTA4cHJvY2Vzc29yMTA4"),
    ("router108processor108", "cm91dGVyMTA4cHJvY2Vzc29yMTA4"),
    ("router108reasoning108", "cm91dGVyMTA4cmVhc29uaW5nMTA4"),
    ("router108machine108", "cm91dGVyMTA4bWFjaGluZTEwOA"),
    ("router108learning108", "cm91dGVyMTA4bGVhcm5pbmcxMDg"),
    ("cluster108learning108", "Y2x1c3RlcjEwOGxlYXJuaW5nMTA4"),
    ("cluster108model108", "Y2x1c3RlcjEwOG1vZGVsMTA4"),
    ("cluster108token108", "Y2x1c3RlcjEwOHRva2VuMTA4"),
    ("cluster108prompt108", "Y2x1c3RlcjEwOHByb21wdDEwOA"),
    ("mirror108prompt108", "bWlycm9yMTA4cHJvbXB0MTA4"),
    ("mirror108session108", "bWlycm9yMTA4c2Vzc2lvbjEwOA"),
    ("mirror108library108", "bWlycm9yMTA4bGlicmFyeTEwOA"),
    ("mirror108service108", "bWlycm9yMTA4c2VydmljZTEwOA"),
    ("filter108service108", "ZmlsdGVyMTA4c2VydmljZTEwOA"),
    ("filter108gateway108", "ZmlsdGVyMTA4Z2F0ZXdheTEwOA"),
    ("filter108storage108", "ZmlsdGVyMTA4c3RvcmFnZTEwOA"),
    ("filter108network108", "ZmlsdGVyMTA4bmV0d29yazEwOA"),
    ("ranking108network108", "cmFua2luZzEwOG5ldHdvcmsxMDg"),
    ("ranking108latency108", "cmFua2luZzEwOGxhdGVuY3kxMDg"),
    ("ranking108buffer108", "cmFua2luZzEwOGJ1ZmZlcjEwOA"),
    ("ranking108queue108", "cmFua2luZzEwOHF1ZXVlMTA4"),
    ("encoding108queue108", "ZW5jb2RpbmcxMDhxdWV1ZTEwOA"),
    ("encoding108worker108", "ZW5jb2RpbmcxMDh3b3JrZXIxMDg"),
    ("encoding108kernel108", "ZW5jb2RpbmcxMDhrZXJuZWwxMDg"),
    ("encoding108signal108", "ZW5jb2RpbmcxMDhzaWduYWwxMDg"),
    ("mapping108signal108", "bWFwcGluZzEwOHNpZ25hbDEwOA"),
    ("mapping108packet108", "bWFwcGluZzEwOHBhY2tldDEwOA"),
    ("mapping108router108", "bWFwcGluZzEwOHJvdXRlcjEwOA"),
    ("mapping108cluster108", "bWFwcGluZzEwOGNsdXN0ZXIxMDg"),
    ("record108cluster108", "cmVjb3JkMTA4Y2x1c3RlcjEwOA"),
    ("record108mirror108", "cmVjb3JkMTA4bWlycm9yMTA4"),
    ("record108filter108", "cmVjb3JkMTA4ZmlsdGVyMTA4"),
    ("record108ranking108", "cmVjb3JkMTA4cmFua2luZzEwOA"),
    ("candle108ranking108", "Y2FuZGxlMTA4cmFua2luZzEwOA"),
    ("candle108encoding108", "Y2FuZGxlMTA4ZW5jb2RpbmcxMDg"),
    ("candle108mapping108", "Y2FuZGxlMTA4bWFwcGluZzEwOA"),
    ("candle108record108", "Y2FuZGxlMTA4cmVjb3JkMTA4"),
    ("thread108record108", "dGhyZWFkMTA4cmVjb3JkMTA4"),
    ("thread108candle108", "dGhyZWFkMTA4Y2FuZGxlMTA4"),
    ("thread108thread108", "dGhyZWFkMTA4dGhyZWFkMTA4"),
    ("thread108kitten108", "dGhyZWFkMTA4a2l0dGVuMTA4"),
    (
        "round 108: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTA4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 108: agentuniverse is a framework for multi agents",
        "cm91bmQgMTA4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 108: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTA4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 108: the processor reads the record then stops",
        "cm91bmQgMTA4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 108: a worker pulls the next task from the queue",
        "cm91bmQgMTA4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 108: signals travel through the network layer",
        "cm91bmQgMTA4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 108: the gateway routes each request by policy",
        "cm91bmQgMTA4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 108: memory grows until the buffer is full",
        "cm91bmQgMTA4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 108: the cluster mirrors every packet twice",
        "cm91bmQgMTA4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 108: ranking uses tokens learned from the corpus",
        "cm91bmQgMTA4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 108: a long session ends when the candle dies",
        "cm91bmQgMTA4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 108: encode the prompt then map the result",
        "cm91bmQgMTA4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 108: the kernel wakes the worker at dawn",
        "cm91bmQgMTA4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 108: service latency drops after the patch",
        "cm91bmQgMTA4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 108: the library caches every vector it sees",
        "cm91bmQgMTA4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 108: agents argue then the debate resolves",
        "cm91bmQgMTA4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 108: the filter keeps only strong matches",
        "cm91bmQgMTA4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 108: the model answers with a short reply",
        "cm91bmQgMTA4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 108: the recorder stores the reasoning trace",
        "cm91bmQgMTA4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 108: the angel watches the processor run",
        "cm91bmQgMTA4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 108: angle of the vector decides the match",
        "cm91bmQgMTA4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 108: the candle burns twice as long at night",
        "cm91bmQgMTA4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 108: a mirror of the universe in one line",
        "cm91bmQgMTA4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 108: the queue drains before the storm", "cm91bmQgMTA4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
