"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten104kitten104", "a2l0dGVuMTA0a2l0dGVuMTA0"),
    ("kitten104sitting104", "a2l0dGVuMTA0c2l0dGluZzEwNA"),
    ("kitten104agent104", "a2l0dGVuMTA0YWdlbnQxMDQ"),
    ("kitten104angle104", "a2l0dGVuMTA0YW5nbGUxMDQ"),
    ("sitting104angle104", "c2l0dGluZzEwNGFuZ2xlMTA0"),
    ("sitting104universe104", "c2l0dGluZzEwNHVuaXZlcnNlMTA0"),
    ("sitting104memory104", "c2l0dGluZzEwNG1lbW9yeTEwNA"),
    ("sitting104stream104", "c2l0dGluZzEwNHN0cmVhbTEwNA"),
    ("agent104stream104", "YWdlbnQxMDRzdHJlYW0xMDQ"),
    ("agent104context104", "YWdlbnQxMDRjb250ZXh0MTA0"),
    ("agent104knowledge104", "YWdlbnQxMDRrbm93bGVkZ2UxMDQ"),
    ("agent104vector104", "YWdlbnQxMDR2ZWN0b3IxMDQ"),
    ("angle104vector104", "YW5nbGUxMDR2ZWN0b3IxMDQ"),
    ("angle104processor104", "YW5nbGUxMDRwcm9jZXNzb3IxMDQ"),
    ("angle104reasoning104", "YW5nbGUxMDRyZWFzb25pbmcxMDQ"),
    ("angle104machine104", "YW5nbGUxMDRtYWNoaW5lMTA0"),
    ("universe104machine104", "dW5pdmVyc2UxMDRtYWNoaW5lMTA0"),
    ("universe104learning104", "dW5pdmVyc2UxMDRsZWFybmluZzEwNA"),
    ("universe104model104", "dW5pdmVyc2UxMDRtb2RlbDEwNA"),
    ("universe104token104", "dW5pdmVyc2UxMDR0b2tlbjEwNA"),
    ("memory104token104", "bWVtb3J5MTA0dG9rZW4xMDQ"),
    ("memory104prompt104", "bWVtb3J5MTA0cHJvbXB0MTA0"),
    ("memory104session104", "bWVtb3J5MTA0c2Vzc2lvbjEwNA"),
    ("memory104library104", "bWVtb3J5MTA0bGlicmFyeTEwNA"),
    ("stream104library104", "c3RyZWFtMTA0bGlicmFyeTEwNA"),
    ("stream104service104", "c3RyZWFtMTA0c2VydmljZTEwNA"),
    ("stream104gateway104", "c3RyZWFtMTA0Z2F0ZXdheTEwNA"),
    ("stream104storage104", "c3RyZWFtMTA0c3RvcmFnZTEwNA"),
    ("context104storage104", "Y29udGV4dDEwNHN0b3JhZ2UxMDQ"),
    ("context104network104", "Y29udGV4dDEwNG5ldHdvcmsxMDQ"),
    ("context104latency104", "Y29udGV4dDEwNGxhdGVuY3kxMDQ"),
    ("context104buffer104", "Y29udGV4dDEwNGJ1ZmZlcjEwNA"),
    ("knowledge104buffer104", "a25vd2xlZGdlMTA0YnVmZmVyMTA0"),
    ("knowledge104queue104", "a25vd2xlZGdlMTA0cXVldWUxMDQ"),
    ("knowledge104worker104", "a25vd2xlZGdlMTA0d29ya2VyMTA0"),
    ("knowledge104kernel104", "a25vd2xlZGdlMTA0a2VybmVsMTA0"),
    ("vector104kernel104", "dmVjdG9yMTA0a2VybmVsMTA0"),
    ("vector104signal104", "dmVjdG9yMTA0c2lnbmFsMTA0"),
    ("vector104packet104", "dmVjdG9yMTA0cGFja2V0MTA0"),
    ("vector104router104", "dmVjdG9yMTA0cm91dGVyMTA0"),
    ("processor104router104", "cHJvY2Vzc29yMTA0cm91dGVyMTA0"),
    ("processor104cluster104", "cHJvY2Vzc29yMTA0Y2x1c3RlcjEwNA"),
    ("processor104mirror104", "cHJvY2Vzc29yMTA0bWlycm9yMTA0"),
    ("processor104filter104", "cHJvY2Vzc29yMTA0ZmlsdGVyMTA0"),
    ("reasoning104filter104", "cmVhc29uaW5nMTA0ZmlsdGVyMTA0"),
    ("reasoning104ranking104", "cmVhc29uaW5nMTA0cmFua2luZzEwNA"),
    ("reasoning104encoding104", "cmVhc29uaW5nMTA0ZW5jb2RpbmcxMDQ"),
    ("reasoning104mapping104", "cmVhc29uaW5nMTA0bWFwcGluZzEwNA"),
    ("machine104mapping104", "bWFjaGluZTEwNG1hcHBpbmcxMDQ"),
    ("machine104record104", "bWFjaGluZTEwNHJlY29yZDEwNA"),
    ("machine104candle104", "bWFjaGluZTEwNGNhbmRsZTEwNA"),
    ("machine104thread104", "bWFjaGluZTEwNHRocmVhZDEwNA"),
    ("learning104thread104", "bGVhcm5pbmcxMDR0aHJlYWQxMDQ"),
    ("learning104kitten104", "bGVhcm5pbmcxMDRraXR0ZW4xMDQ"),
    ("learning104sitting104", "bGVhcm5pbmcxMDRzaXR0aW5nMTA0"),
    ("learning104agent104", "bGVhcm5pbmcxMDRhZ2VudDEwNA"),
    ("model104agent104", "bW9kZWwxMDRhZ2VudDEwNA"),
    ("model104angle104", "bW9kZWwxMDRhbmdsZTEwNA"),
    ("model104universe104", "bW9kZWwxMDR1bml2ZXJzZTEwNA"),
    ("model104memory104", "bW9kZWwxMDRtZW1vcnkxMDQ"),
    ("token104memory104", "dG9rZW4xMDRtZW1vcnkxMDQ"),
    ("token104stream104", "dG9rZW4xMDRzdHJlYW0xMDQ"),
    ("token104context104", "dG9rZW4xMDRjb250ZXh0MTA0"),
    ("token104knowledge104", "dG9rZW4xMDRrbm93bGVkZ2UxMDQ"),
    ("prompt104knowledge104", "cHJvbXB0MTA0a25vd2xlZGdlMTA0"),
    ("prompt104vector104", "cHJvbXB0MTA0dmVjdG9yMTA0"),
    ("prompt104processor104", "cHJvbXB0MTA0cHJvY2Vzc29yMTA0"),
    ("prompt104reasoning104", "cHJvbXB0MTA0cmVhc29uaW5nMTA0"),
    ("session104reasoning104", "c2Vzc2lvbjEwNHJlYXNvbmluZzEwNA"),
    ("session104machine104", "c2Vzc2lvbjEwNG1hY2hpbmUxMDQ"),
    ("session104learning104", "c2Vzc2lvbjEwNGxlYXJuaW5nMTA0"),
    ("session104model104", "c2Vzc2lvbjEwNG1vZGVsMTA0"),
    ("library104model104", "bGlicmFyeTEwNG1vZGVsMTA0"),
    ("library104token104", "bGlicmFyeTEwNHRva2VuMTA0"),
    ("library104prompt104", "bGlicmFyeTEwNHByb21wdDEwNA"),
    ("library104session104", "bGlicmFyeTEwNHNlc3Npb24xMDQ"),
    ("service104session104", "c2VydmljZTEwNHNlc3Npb24xMDQ"),
    ("service104library104", "c2VydmljZTEwNGxpYnJhcnkxMDQ"),
    ("service104service104", "c2VydmljZTEwNHNlcnZpY2UxMDQ"),
    ("service104gateway104", "c2VydmljZTEwNGdhdGV3YXkxMDQ"),
    ("gateway104gateway104", "Z2F0ZXdheTEwNGdhdGV3YXkxMDQ"),
    ("gateway104storage104", "Z2F0ZXdheTEwNHN0b3JhZ2UxMDQ"),
    ("gateway104network104", "Z2F0ZXdheTEwNG5ldHdvcmsxMDQ"),
    ("gateway104latency104", "Z2F0ZXdheTEwNGxhdGVuY3kxMDQ"),
    ("storage104latency104", "c3RvcmFnZTEwNGxhdGVuY3kxMDQ"),
    ("storage104buffer104", "c3RvcmFnZTEwNGJ1ZmZlcjEwNA"),
    ("storage104queue104", "c3RvcmFnZTEwNHF1ZXVlMTA0"),
    ("storage104worker104", "c3RvcmFnZTEwNHdvcmtlcjEwNA"),
    ("network104worker104", "bmV0d29yazEwNHdvcmtlcjEwNA"),
    ("network104kernel104", "bmV0d29yazEwNGtlcm5lbDEwNA"),
    ("network104signal104", "bmV0d29yazEwNHNpZ25hbDEwNA"),
    ("network104packet104", "bmV0d29yazEwNHBhY2tldDEwNA"),
    ("latency104packet104", "bGF0ZW5jeTEwNHBhY2tldDEwNA"),
    ("latency104router104", "bGF0ZW5jeTEwNHJvdXRlcjEwNA"),
    ("latency104cluster104", "bGF0ZW5jeTEwNGNsdXN0ZXIxMDQ"),
    ("latency104mirror104", "bGF0ZW5jeTEwNG1pcnJvcjEwNA"),
    ("buffer104mirror104", "YnVmZmVyMTA0bWlycm9yMTA0"),
    ("buffer104filter104", "YnVmZmVyMTA0ZmlsdGVyMTA0"),
    ("buffer104ranking104", "YnVmZmVyMTA0cmFua2luZzEwNA"),
    ("buffer104encoding104", "YnVmZmVyMTA0ZW5jb2RpbmcxMDQ"),
    ("queue104encoding104", "cXVldWUxMDRlbmNvZGluZzEwNA"),
    ("queue104mapping104", "cXVldWUxMDRtYXBwaW5nMTA0"),
    ("queue104record104", "cXVldWUxMDRyZWNvcmQxMDQ"),
    ("queue104candle104", "cXVldWUxMDRjYW5kbGUxMDQ"),
    ("worker104candle104", "d29ya2VyMTA0Y2FuZGxlMTA0"),
    ("worker104thread104", "d29ya2VyMTA0dGhyZWFkMTA0"),
    ("worker104kitten104", "d29ya2VyMTA0a2l0dGVuMTA0"),
    ("worker104sitting104", "d29ya2VyMTA0c2l0dGluZzEwNA"),
    ("kernel104sitting104", "a2VybmVsMTA0c2l0dGluZzEwNA"),
    ("kernel104agent104", "a2VybmVsMTA0YWdlbnQxMDQ"),
    ("kernel104angle104", "a2VybmVsMTA0YW5nbGUxMDQ"),
    ("kernel104universe104", "a2VybmVsMTA0dW5pdmVyc2UxMDQ"),
    ("signal104universe104", "c2lnbmFsMTA0dW5pdmVyc2UxMDQ"),
    ("signal104memory104", "c2lnbmFsMTA0bWVtb3J5MTA0"),
    ("signal104stream104", "c2lnbmFsMTA0c3RyZWFtMTA0"),
    ("signal104context104", "c2lnbmFsMTA0Y29udGV4dDEwNA"),
    ("packet104context104", "cGFja2V0MTA0Y29udGV4dDEwNA"),
    ("packet104knowledge104", "cGFja2V0MTA0a25vd2xlZGdlMTA0"),
    ("packet104vector104", "cGFja2V0MTA0dmVjdG9yMTA0"),
    ("packet104processor104", "cGFja2V0MTA0cHJvY2Vzc29yMTA0"),
    ("router104processor104", "cm91dGVyMTA0cHJvY2Vzc29yMTA0"),
    ("router104reasoning104", "cm91dGVyMTA0cmVhc29uaW5nMTA0"),
    ("router104machine104", "cm91dGVyMTA0bWFjaGluZTEwNA"),
    ("router104learning104", "cm91dGVyMTA0bGVhcm5pbmcxMDQ"),
    ("cluster104learning104", "Y2x1c3RlcjEwNGxlYXJuaW5nMTA0"),
    ("cluster104model104", "Y2x1c3RlcjEwNG1vZGVsMTA0"),
    ("cluster104token104", "Y2x1c3RlcjEwNHRva2VuMTA0"),
    ("cluster104prompt104", "Y2x1c3RlcjEwNHByb21wdDEwNA"),
    ("mirror104prompt104", "bWlycm9yMTA0cHJvbXB0MTA0"),
    ("mirror104session104", "bWlycm9yMTA0c2Vzc2lvbjEwNA"),
    ("mirror104library104", "bWlycm9yMTA0bGlicmFyeTEwNA"),
    ("mirror104service104", "bWlycm9yMTA0c2VydmljZTEwNA"),
    ("filter104service104", "ZmlsdGVyMTA0c2VydmljZTEwNA"),
    ("filter104gateway104", "ZmlsdGVyMTA0Z2F0ZXdheTEwNA"),
    ("filter104storage104", "ZmlsdGVyMTA0c3RvcmFnZTEwNA"),
    ("filter104network104", "ZmlsdGVyMTA0bmV0d29yazEwNA"),
    ("ranking104network104", "cmFua2luZzEwNG5ldHdvcmsxMDQ"),
    ("ranking104latency104", "cmFua2luZzEwNGxhdGVuY3kxMDQ"),
    ("ranking104buffer104", "cmFua2luZzEwNGJ1ZmZlcjEwNA"),
    ("ranking104queue104", "cmFua2luZzEwNHF1ZXVlMTA0"),
    ("encoding104queue104", "ZW5jb2RpbmcxMDRxdWV1ZTEwNA"),
    ("encoding104worker104", "ZW5jb2RpbmcxMDR3b3JrZXIxMDQ"),
    ("encoding104kernel104", "ZW5jb2RpbmcxMDRrZXJuZWwxMDQ"),
    ("encoding104signal104", "ZW5jb2RpbmcxMDRzaWduYWwxMDQ"),
    ("mapping104signal104", "bWFwcGluZzEwNHNpZ25hbDEwNA"),
    ("mapping104packet104", "bWFwcGluZzEwNHBhY2tldDEwNA"),
    ("mapping104router104", "bWFwcGluZzEwNHJvdXRlcjEwNA"),
    ("mapping104cluster104", "bWFwcGluZzEwNGNsdXN0ZXIxMDQ"),
    ("record104cluster104", "cmVjb3JkMTA0Y2x1c3RlcjEwNA"),
    ("record104mirror104", "cmVjb3JkMTA0bWlycm9yMTA0"),
    ("record104filter104", "cmVjb3JkMTA0ZmlsdGVyMTA0"),
    ("record104ranking104", "cmVjb3JkMTA0cmFua2luZzEwNA"),
    ("candle104ranking104", "Y2FuZGxlMTA0cmFua2luZzEwNA"),
    ("candle104encoding104", "Y2FuZGxlMTA0ZW5jb2RpbmcxMDQ"),
    ("candle104mapping104", "Y2FuZGxlMTA0bWFwcGluZzEwNA"),
    ("candle104record104", "Y2FuZGxlMTA0cmVjb3JkMTA0"),
    ("thread104record104", "dGhyZWFkMTA0cmVjb3JkMTA0"),
    ("thread104candle104", "dGhyZWFkMTA0Y2FuZGxlMTA0"),
    ("thread104thread104", "dGhyZWFkMTA0dGhyZWFkMTA0"),
    ("thread104kitten104", "dGhyZWFkMTA0a2l0dGVuMTA0"),
    (
        "round 104: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTA0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 104: agentuniverse is a framework for multi agents",
        "cm91bmQgMTA0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 104: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTA0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 104: the processor reads the record then stops",
        "cm91bmQgMTA0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 104: a worker pulls the next task from the queue",
        "cm91bmQgMTA0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 104: signals travel through the network layer",
        "cm91bmQgMTA0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 104: the gateway routes each request by policy",
        "cm91bmQgMTA0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 104: memory grows until the buffer is full",
        "cm91bmQgMTA0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 104: the cluster mirrors every packet twice",
        "cm91bmQgMTA0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 104: ranking uses tokens learned from the corpus",
        "cm91bmQgMTA0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 104: a long session ends when the candle dies",
        "cm91bmQgMTA0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 104: encode the prompt then map the result",
        "cm91bmQgMTA0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 104: the kernel wakes the worker at dawn",
        "cm91bmQgMTA0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 104: service latency drops after the patch",
        "cm91bmQgMTA0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 104: the library caches every vector it sees",
        "cm91bmQgMTA0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 104: agents argue then the debate resolves",
        "cm91bmQgMTA0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 104: the filter keeps only strong matches",
        "cm91bmQgMTA0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 104: the model answers with a short reply",
        "cm91bmQgMTA0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 104: the recorder stores the reasoning trace",
        "cm91bmQgMTA0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 104: the angel watches the processor run",
        "cm91bmQgMTA0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 104: angle of the vector decides the match",
        "cm91bmQgMTA0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 104: the candle burns twice as long at night",
        "cm91bmQgMTA0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 104: a mirror of the universe in one line",
        "cm91bmQgMTA0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 104: the queue drains before the storm", "cm91bmQgMTA0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
