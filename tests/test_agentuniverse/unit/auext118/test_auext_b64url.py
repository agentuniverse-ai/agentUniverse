"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten118kitten118", "a2l0dGVuMTE4a2l0dGVuMTE4"),
    ("kitten118sitting118", "a2l0dGVuMTE4c2l0dGluZzExOA"),
    ("kitten118agent118", "a2l0dGVuMTE4YWdlbnQxMTg"),
    ("kitten118angle118", "a2l0dGVuMTE4YW5nbGUxMTg"),
    ("sitting118angle118", "c2l0dGluZzExOGFuZ2xlMTE4"),
    ("sitting118universe118", "c2l0dGluZzExOHVuaXZlcnNlMTE4"),
    ("sitting118memory118", "c2l0dGluZzExOG1lbW9yeTExOA"),
    ("sitting118stream118", "c2l0dGluZzExOHN0cmVhbTExOA"),
    ("agent118stream118", "YWdlbnQxMThzdHJlYW0xMTg"),
    ("agent118context118", "YWdlbnQxMThjb250ZXh0MTE4"),
    ("agent118knowledge118", "YWdlbnQxMThrbm93bGVkZ2UxMTg"),
    ("agent118vector118", "YWdlbnQxMTh2ZWN0b3IxMTg"),
    ("angle118vector118", "YW5nbGUxMTh2ZWN0b3IxMTg"),
    ("angle118processor118", "YW5nbGUxMThwcm9jZXNzb3IxMTg"),
    ("angle118reasoning118", "YW5nbGUxMThyZWFzb25pbmcxMTg"),
    ("angle118machine118", "YW5nbGUxMThtYWNoaW5lMTE4"),
    ("universe118machine118", "dW5pdmVyc2UxMThtYWNoaW5lMTE4"),
    ("universe118learning118", "dW5pdmVyc2UxMThsZWFybmluZzExOA"),
    ("universe118model118", "dW5pdmVyc2UxMThtb2RlbDExOA"),
    ("universe118token118", "dW5pdmVyc2UxMTh0b2tlbjExOA"),
    ("memory118token118", "bWVtb3J5MTE4dG9rZW4xMTg"),
    ("memory118prompt118", "bWVtb3J5MTE4cHJvbXB0MTE4"),
    ("memory118session118", "bWVtb3J5MTE4c2Vzc2lvbjExOA"),
    ("memory118library118", "bWVtb3J5MTE4bGlicmFyeTExOA"),
    ("stream118library118", "c3RyZWFtMTE4bGlicmFyeTExOA"),
    ("stream118service118", "c3RyZWFtMTE4c2VydmljZTExOA"),
    ("stream118gateway118", "c3RyZWFtMTE4Z2F0ZXdheTExOA"),
    ("stream118storage118", "c3RyZWFtMTE4c3RvcmFnZTExOA"),
    ("context118storage118", "Y29udGV4dDExOHN0b3JhZ2UxMTg"),
    ("context118network118", "Y29udGV4dDExOG5ldHdvcmsxMTg"),
    ("context118latency118", "Y29udGV4dDExOGxhdGVuY3kxMTg"),
    ("context118buffer118", "Y29udGV4dDExOGJ1ZmZlcjExOA"),
    ("knowledge118buffer118", "a25vd2xlZGdlMTE4YnVmZmVyMTE4"),
    ("knowledge118queue118", "a25vd2xlZGdlMTE4cXVldWUxMTg"),
    ("knowledge118worker118", "a25vd2xlZGdlMTE4d29ya2VyMTE4"),
    ("knowledge118kernel118", "a25vd2xlZGdlMTE4a2VybmVsMTE4"),
    ("vector118kernel118", "dmVjdG9yMTE4a2VybmVsMTE4"),
    ("vector118signal118", "dmVjdG9yMTE4c2lnbmFsMTE4"),
    ("vector118packet118", "dmVjdG9yMTE4cGFja2V0MTE4"),
    ("vector118router118", "dmVjdG9yMTE4cm91dGVyMTE4"),
    ("processor118router118", "cHJvY2Vzc29yMTE4cm91dGVyMTE4"),
    ("processor118cluster118", "cHJvY2Vzc29yMTE4Y2x1c3RlcjExOA"),
    ("processor118mirror118", "cHJvY2Vzc29yMTE4bWlycm9yMTE4"),
    ("processor118filter118", "cHJvY2Vzc29yMTE4ZmlsdGVyMTE4"),
    ("reasoning118filter118", "cmVhc29uaW5nMTE4ZmlsdGVyMTE4"),
    ("reasoning118ranking118", "cmVhc29uaW5nMTE4cmFua2luZzExOA"),
    ("reasoning118encoding118", "cmVhc29uaW5nMTE4ZW5jb2RpbmcxMTg"),
    ("reasoning118mapping118", "cmVhc29uaW5nMTE4bWFwcGluZzExOA"),
    ("machine118mapping118", "bWFjaGluZTExOG1hcHBpbmcxMTg"),
    ("machine118record118", "bWFjaGluZTExOHJlY29yZDExOA"),
    ("machine118candle118", "bWFjaGluZTExOGNhbmRsZTExOA"),
    ("machine118thread118", "bWFjaGluZTExOHRocmVhZDExOA"),
    ("learning118thread118", "bGVhcm5pbmcxMTh0aHJlYWQxMTg"),
    ("learning118kitten118", "bGVhcm5pbmcxMThraXR0ZW4xMTg"),
    ("learning118sitting118", "bGVhcm5pbmcxMThzaXR0aW5nMTE4"),
    ("learning118agent118", "bGVhcm5pbmcxMThhZ2VudDExOA"),
    ("model118agent118", "bW9kZWwxMThhZ2VudDExOA"),
    ("model118angle118", "bW9kZWwxMThhbmdsZTExOA"),
    ("model118universe118", "bW9kZWwxMTh1bml2ZXJzZTExOA"),
    ("model118memory118", "bW9kZWwxMThtZW1vcnkxMTg"),
    ("token118memory118", "dG9rZW4xMThtZW1vcnkxMTg"),
    ("token118stream118", "dG9rZW4xMThzdHJlYW0xMTg"),
    ("token118context118", "dG9rZW4xMThjb250ZXh0MTE4"),
    ("token118knowledge118", "dG9rZW4xMThrbm93bGVkZ2UxMTg"),
    ("prompt118knowledge118", "cHJvbXB0MTE4a25vd2xlZGdlMTE4"),
    ("prompt118vector118", "cHJvbXB0MTE4dmVjdG9yMTE4"),
    ("prompt118processor118", "cHJvbXB0MTE4cHJvY2Vzc29yMTE4"),
    ("prompt118reasoning118", "cHJvbXB0MTE4cmVhc29uaW5nMTE4"),
    ("session118reasoning118", "c2Vzc2lvbjExOHJlYXNvbmluZzExOA"),
    ("session118machine118", "c2Vzc2lvbjExOG1hY2hpbmUxMTg"),
    ("session118learning118", "c2Vzc2lvbjExOGxlYXJuaW5nMTE4"),
    ("session118model118", "c2Vzc2lvbjExOG1vZGVsMTE4"),
    ("library118model118", "bGlicmFyeTExOG1vZGVsMTE4"),
    ("library118token118", "bGlicmFyeTExOHRva2VuMTE4"),
    ("library118prompt118", "bGlicmFyeTExOHByb21wdDExOA"),
    ("library118session118", "bGlicmFyeTExOHNlc3Npb24xMTg"),
    ("service118session118", "c2VydmljZTExOHNlc3Npb24xMTg"),
    ("service118library118", "c2VydmljZTExOGxpYnJhcnkxMTg"),
    ("service118service118", "c2VydmljZTExOHNlcnZpY2UxMTg"),
    ("service118gateway118", "c2VydmljZTExOGdhdGV3YXkxMTg"),
    ("gateway118gateway118", "Z2F0ZXdheTExOGdhdGV3YXkxMTg"),
    ("gateway118storage118", "Z2F0ZXdheTExOHN0b3JhZ2UxMTg"),
    ("gateway118network118", "Z2F0ZXdheTExOG5ldHdvcmsxMTg"),
    ("gateway118latency118", "Z2F0ZXdheTExOGxhdGVuY3kxMTg"),
    ("storage118latency118", "c3RvcmFnZTExOGxhdGVuY3kxMTg"),
    ("storage118buffer118", "c3RvcmFnZTExOGJ1ZmZlcjExOA"),
    ("storage118queue118", "c3RvcmFnZTExOHF1ZXVlMTE4"),
    ("storage118worker118", "c3RvcmFnZTExOHdvcmtlcjExOA"),
    ("network118worker118", "bmV0d29yazExOHdvcmtlcjExOA"),
    ("network118kernel118", "bmV0d29yazExOGtlcm5lbDExOA"),
    ("network118signal118", "bmV0d29yazExOHNpZ25hbDExOA"),
    ("network118packet118", "bmV0d29yazExOHBhY2tldDExOA"),
    ("latency118packet118", "bGF0ZW5jeTExOHBhY2tldDExOA"),
    ("latency118router118", "bGF0ZW5jeTExOHJvdXRlcjExOA"),
    ("latency118cluster118", "bGF0ZW5jeTExOGNsdXN0ZXIxMTg"),
    ("latency118mirror118", "bGF0ZW5jeTExOG1pcnJvcjExOA"),
    ("buffer118mirror118", "YnVmZmVyMTE4bWlycm9yMTE4"),
    ("buffer118filter118", "YnVmZmVyMTE4ZmlsdGVyMTE4"),
    ("buffer118ranking118", "YnVmZmVyMTE4cmFua2luZzExOA"),
    ("buffer118encoding118", "YnVmZmVyMTE4ZW5jb2RpbmcxMTg"),
    ("queue118encoding118", "cXVldWUxMThlbmNvZGluZzExOA"),
    ("queue118mapping118", "cXVldWUxMThtYXBwaW5nMTE4"),
    ("queue118record118", "cXVldWUxMThyZWNvcmQxMTg"),
    ("queue118candle118", "cXVldWUxMThjYW5kbGUxMTg"),
    ("worker118candle118", "d29ya2VyMTE4Y2FuZGxlMTE4"),
    ("worker118thread118", "d29ya2VyMTE4dGhyZWFkMTE4"),
    ("worker118kitten118", "d29ya2VyMTE4a2l0dGVuMTE4"),
    ("worker118sitting118", "d29ya2VyMTE4c2l0dGluZzExOA"),
    ("kernel118sitting118", "a2VybmVsMTE4c2l0dGluZzExOA"),
    ("kernel118agent118", "a2VybmVsMTE4YWdlbnQxMTg"),
    ("kernel118angle118", "a2VybmVsMTE4YW5nbGUxMTg"),
    ("kernel118universe118", "a2VybmVsMTE4dW5pdmVyc2UxMTg"),
    ("signal118universe118", "c2lnbmFsMTE4dW5pdmVyc2UxMTg"),
    ("signal118memory118", "c2lnbmFsMTE4bWVtb3J5MTE4"),
    ("signal118stream118", "c2lnbmFsMTE4c3RyZWFtMTE4"),
    ("signal118context118", "c2lnbmFsMTE4Y29udGV4dDExOA"),
    ("packet118context118", "cGFja2V0MTE4Y29udGV4dDExOA"),
    ("packet118knowledge118", "cGFja2V0MTE4a25vd2xlZGdlMTE4"),
    ("packet118vector118", "cGFja2V0MTE4dmVjdG9yMTE4"),
    ("packet118processor118", "cGFja2V0MTE4cHJvY2Vzc29yMTE4"),
    ("router118processor118", "cm91dGVyMTE4cHJvY2Vzc29yMTE4"),
    ("router118reasoning118", "cm91dGVyMTE4cmVhc29uaW5nMTE4"),
    ("router118machine118", "cm91dGVyMTE4bWFjaGluZTExOA"),
    ("router118learning118", "cm91dGVyMTE4bGVhcm5pbmcxMTg"),
    ("cluster118learning118", "Y2x1c3RlcjExOGxlYXJuaW5nMTE4"),
    ("cluster118model118", "Y2x1c3RlcjExOG1vZGVsMTE4"),
    ("cluster118token118", "Y2x1c3RlcjExOHRva2VuMTE4"),
    ("cluster118prompt118", "Y2x1c3RlcjExOHByb21wdDExOA"),
    ("mirror118prompt118", "bWlycm9yMTE4cHJvbXB0MTE4"),
    ("mirror118session118", "bWlycm9yMTE4c2Vzc2lvbjExOA"),
    ("mirror118library118", "bWlycm9yMTE4bGlicmFyeTExOA"),
    ("mirror118service118", "bWlycm9yMTE4c2VydmljZTExOA"),
    ("filter118service118", "ZmlsdGVyMTE4c2VydmljZTExOA"),
    ("filter118gateway118", "ZmlsdGVyMTE4Z2F0ZXdheTExOA"),
    ("filter118storage118", "ZmlsdGVyMTE4c3RvcmFnZTExOA"),
    ("filter118network118", "ZmlsdGVyMTE4bmV0d29yazExOA"),
    ("ranking118network118", "cmFua2luZzExOG5ldHdvcmsxMTg"),
    ("ranking118latency118", "cmFua2luZzExOGxhdGVuY3kxMTg"),
    ("ranking118buffer118", "cmFua2luZzExOGJ1ZmZlcjExOA"),
    ("ranking118queue118", "cmFua2luZzExOHF1ZXVlMTE4"),
    ("encoding118queue118", "ZW5jb2RpbmcxMThxdWV1ZTExOA"),
    ("encoding118worker118", "ZW5jb2RpbmcxMTh3b3JrZXIxMTg"),
    ("encoding118kernel118", "ZW5jb2RpbmcxMThrZXJuZWwxMTg"),
    ("encoding118signal118", "ZW5jb2RpbmcxMThzaWduYWwxMTg"),
    ("mapping118signal118", "bWFwcGluZzExOHNpZ25hbDExOA"),
    ("mapping118packet118", "bWFwcGluZzExOHBhY2tldDExOA"),
    ("mapping118router118", "bWFwcGluZzExOHJvdXRlcjExOA"),
    ("mapping118cluster118", "bWFwcGluZzExOGNsdXN0ZXIxMTg"),
    ("record118cluster118", "cmVjb3JkMTE4Y2x1c3RlcjExOA"),
    ("record118mirror118", "cmVjb3JkMTE4bWlycm9yMTE4"),
    ("record118filter118", "cmVjb3JkMTE4ZmlsdGVyMTE4"),
    ("record118ranking118", "cmVjb3JkMTE4cmFua2luZzExOA"),
    ("candle118ranking118", "Y2FuZGxlMTE4cmFua2luZzExOA"),
    ("candle118encoding118", "Y2FuZGxlMTE4ZW5jb2RpbmcxMTg"),
    ("candle118mapping118", "Y2FuZGxlMTE4bWFwcGluZzExOA"),
    ("candle118record118", "Y2FuZGxlMTE4cmVjb3JkMTE4"),
    ("thread118record118", "dGhyZWFkMTE4cmVjb3JkMTE4"),
    ("thread118candle118", "dGhyZWFkMTE4Y2FuZGxlMTE4"),
    ("thread118thread118", "dGhyZWFkMTE4dGhyZWFkMTE4"),
    ("thread118kitten118", "dGhyZWFkMTE4a2l0dGVuMTE4"),
    (
        "round 118: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTE4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 118: agentuniverse is a framework for multi agents",
        "cm91bmQgMTE4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 118: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTE4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 118: the processor reads the record then stops",
        "cm91bmQgMTE4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 118: a worker pulls the next task from the queue",
        "cm91bmQgMTE4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 118: signals travel through the network layer",
        "cm91bmQgMTE4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 118: the gateway routes each request by policy",
        "cm91bmQgMTE4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 118: memory grows until the buffer is full",
        "cm91bmQgMTE4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 118: the cluster mirrors every packet twice",
        "cm91bmQgMTE4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 118: ranking uses tokens learned from the corpus",
        "cm91bmQgMTE4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 118: a long session ends when the candle dies",
        "cm91bmQgMTE4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 118: encode the prompt then map the result",
        "cm91bmQgMTE4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 118: the kernel wakes the worker at dawn",
        "cm91bmQgMTE4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 118: service latency drops after the patch",
        "cm91bmQgMTE4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 118: the library caches every vector it sees",
        "cm91bmQgMTE4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 118: agents argue then the debate resolves",
        "cm91bmQgMTE4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 118: the filter keeps only strong matches",
        "cm91bmQgMTE4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 118: the model answers with a short reply",
        "cm91bmQgMTE4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 118: the recorder stores the reasoning trace",
        "cm91bmQgMTE4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 118: the angel watches the processor run",
        "cm91bmQgMTE4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 118: angle of the vector decides the match",
        "cm91bmQgMTE4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 118: the candle burns twice as long at night",
        "cm91bmQgMTE4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 118: a mirror of the universe in one line",
        "cm91bmQgMTE4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 118: the queue drains before the storm", "cm91bmQgMTE4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
