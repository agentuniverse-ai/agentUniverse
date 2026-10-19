"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten201kitten201", "a2l0dGVuMjAxa2l0dGVuMjAx"),
    ("kitten201sitting201", "a2l0dGVuMjAxc2l0dGluZzIwMQ"),
    ("kitten201agent201", "a2l0dGVuMjAxYWdlbnQyMDE"),
    ("kitten201angle201", "a2l0dGVuMjAxYW5nbGUyMDE"),
    ("sitting201angle201", "c2l0dGluZzIwMWFuZ2xlMjAx"),
    ("sitting201universe201", "c2l0dGluZzIwMXVuaXZlcnNlMjAx"),
    ("sitting201memory201", "c2l0dGluZzIwMW1lbW9yeTIwMQ"),
    ("sitting201stream201", "c2l0dGluZzIwMXN0cmVhbTIwMQ"),
    ("agent201stream201", "YWdlbnQyMDFzdHJlYW0yMDE"),
    ("agent201context201", "YWdlbnQyMDFjb250ZXh0MjAx"),
    ("agent201knowledge201", "YWdlbnQyMDFrbm93bGVkZ2UyMDE"),
    ("agent201vector201", "YWdlbnQyMDF2ZWN0b3IyMDE"),
    ("angle201vector201", "YW5nbGUyMDF2ZWN0b3IyMDE"),
    ("angle201processor201", "YW5nbGUyMDFwcm9jZXNzb3IyMDE"),
    ("angle201reasoning201", "YW5nbGUyMDFyZWFzb25pbmcyMDE"),
    ("angle201machine201", "YW5nbGUyMDFtYWNoaW5lMjAx"),
    ("universe201machine201", "dW5pdmVyc2UyMDFtYWNoaW5lMjAx"),
    ("universe201learning201", "dW5pdmVyc2UyMDFsZWFybmluZzIwMQ"),
    ("universe201model201", "dW5pdmVyc2UyMDFtb2RlbDIwMQ"),
    ("universe201token201", "dW5pdmVyc2UyMDF0b2tlbjIwMQ"),
    ("memory201token201", "bWVtb3J5MjAxdG9rZW4yMDE"),
    ("memory201prompt201", "bWVtb3J5MjAxcHJvbXB0MjAx"),
    ("memory201session201", "bWVtb3J5MjAxc2Vzc2lvbjIwMQ"),
    ("memory201library201", "bWVtb3J5MjAxbGlicmFyeTIwMQ"),
    ("stream201library201", "c3RyZWFtMjAxbGlicmFyeTIwMQ"),
    ("stream201service201", "c3RyZWFtMjAxc2VydmljZTIwMQ"),
    ("stream201gateway201", "c3RyZWFtMjAxZ2F0ZXdheTIwMQ"),
    ("stream201storage201", "c3RyZWFtMjAxc3RvcmFnZTIwMQ"),
    ("context201storage201", "Y29udGV4dDIwMXN0b3JhZ2UyMDE"),
    ("context201network201", "Y29udGV4dDIwMW5ldHdvcmsyMDE"),
    ("context201latency201", "Y29udGV4dDIwMWxhdGVuY3kyMDE"),
    ("context201buffer201", "Y29udGV4dDIwMWJ1ZmZlcjIwMQ"),
    ("knowledge201buffer201", "a25vd2xlZGdlMjAxYnVmZmVyMjAx"),
    ("knowledge201queue201", "a25vd2xlZGdlMjAxcXVldWUyMDE"),
    ("knowledge201worker201", "a25vd2xlZGdlMjAxd29ya2VyMjAx"),
    ("knowledge201kernel201", "a25vd2xlZGdlMjAxa2VybmVsMjAx"),
    ("vector201kernel201", "dmVjdG9yMjAxa2VybmVsMjAx"),
    ("vector201signal201", "dmVjdG9yMjAxc2lnbmFsMjAx"),
    ("vector201packet201", "dmVjdG9yMjAxcGFja2V0MjAx"),
    ("vector201router201", "dmVjdG9yMjAxcm91dGVyMjAx"),
    ("processor201router201", "cHJvY2Vzc29yMjAxcm91dGVyMjAx"),
    ("processor201cluster201", "cHJvY2Vzc29yMjAxY2x1c3RlcjIwMQ"),
    ("processor201mirror201", "cHJvY2Vzc29yMjAxbWlycm9yMjAx"),
    ("processor201filter201", "cHJvY2Vzc29yMjAxZmlsdGVyMjAx"),
    ("reasoning201filter201", "cmVhc29uaW5nMjAxZmlsdGVyMjAx"),
    ("reasoning201ranking201", "cmVhc29uaW5nMjAxcmFua2luZzIwMQ"),
    ("reasoning201encoding201", "cmVhc29uaW5nMjAxZW5jb2RpbmcyMDE"),
    ("reasoning201mapping201", "cmVhc29uaW5nMjAxbWFwcGluZzIwMQ"),
    ("machine201mapping201", "bWFjaGluZTIwMW1hcHBpbmcyMDE"),
    ("machine201record201", "bWFjaGluZTIwMXJlY29yZDIwMQ"),
    ("machine201candle201", "bWFjaGluZTIwMWNhbmRsZTIwMQ"),
    ("machine201thread201", "bWFjaGluZTIwMXRocmVhZDIwMQ"),
    ("learning201thread201", "bGVhcm5pbmcyMDF0aHJlYWQyMDE"),
    ("learning201kitten201", "bGVhcm5pbmcyMDFraXR0ZW4yMDE"),
    ("learning201sitting201", "bGVhcm5pbmcyMDFzaXR0aW5nMjAx"),
    ("learning201agent201", "bGVhcm5pbmcyMDFhZ2VudDIwMQ"),
    ("model201agent201", "bW9kZWwyMDFhZ2VudDIwMQ"),
    ("model201angle201", "bW9kZWwyMDFhbmdsZTIwMQ"),
    ("model201universe201", "bW9kZWwyMDF1bml2ZXJzZTIwMQ"),
    ("model201memory201", "bW9kZWwyMDFtZW1vcnkyMDE"),
    ("token201memory201", "dG9rZW4yMDFtZW1vcnkyMDE"),
    ("token201stream201", "dG9rZW4yMDFzdHJlYW0yMDE"),
    ("token201context201", "dG9rZW4yMDFjb250ZXh0MjAx"),
    ("token201knowledge201", "dG9rZW4yMDFrbm93bGVkZ2UyMDE"),
    ("prompt201knowledge201", "cHJvbXB0MjAxa25vd2xlZGdlMjAx"),
    ("prompt201vector201", "cHJvbXB0MjAxdmVjdG9yMjAx"),
    ("prompt201processor201", "cHJvbXB0MjAxcHJvY2Vzc29yMjAx"),
    ("prompt201reasoning201", "cHJvbXB0MjAxcmVhc29uaW5nMjAx"),
    ("session201reasoning201", "c2Vzc2lvbjIwMXJlYXNvbmluZzIwMQ"),
    ("session201machine201", "c2Vzc2lvbjIwMW1hY2hpbmUyMDE"),
    ("session201learning201", "c2Vzc2lvbjIwMWxlYXJuaW5nMjAx"),
    ("session201model201", "c2Vzc2lvbjIwMW1vZGVsMjAx"),
    ("library201model201", "bGlicmFyeTIwMW1vZGVsMjAx"),
    ("library201token201", "bGlicmFyeTIwMXRva2VuMjAx"),
    ("library201prompt201", "bGlicmFyeTIwMXByb21wdDIwMQ"),
    ("library201session201", "bGlicmFyeTIwMXNlc3Npb24yMDE"),
    ("service201session201", "c2VydmljZTIwMXNlc3Npb24yMDE"),
    ("service201library201", "c2VydmljZTIwMWxpYnJhcnkyMDE"),
    ("service201service201", "c2VydmljZTIwMXNlcnZpY2UyMDE"),
    ("service201gateway201", "c2VydmljZTIwMWdhdGV3YXkyMDE"),
    ("gateway201gateway201", "Z2F0ZXdheTIwMWdhdGV3YXkyMDE"),
    ("gateway201storage201", "Z2F0ZXdheTIwMXN0b3JhZ2UyMDE"),
    ("gateway201network201", "Z2F0ZXdheTIwMW5ldHdvcmsyMDE"),
    ("gateway201latency201", "Z2F0ZXdheTIwMWxhdGVuY3kyMDE"),
    ("storage201latency201", "c3RvcmFnZTIwMWxhdGVuY3kyMDE"),
    ("storage201buffer201", "c3RvcmFnZTIwMWJ1ZmZlcjIwMQ"),
    ("storage201queue201", "c3RvcmFnZTIwMXF1ZXVlMjAx"),
    ("storage201worker201", "c3RvcmFnZTIwMXdvcmtlcjIwMQ"),
    ("network201worker201", "bmV0d29yazIwMXdvcmtlcjIwMQ"),
    ("network201kernel201", "bmV0d29yazIwMWtlcm5lbDIwMQ"),
    ("network201signal201", "bmV0d29yazIwMXNpZ25hbDIwMQ"),
    ("network201packet201", "bmV0d29yazIwMXBhY2tldDIwMQ"),
    ("latency201packet201", "bGF0ZW5jeTIwMXBhY2tldDIwMQ"),
    ("latency201router201", "bGF0ZW5jeTIwMXJvdXRlcjIwMQ"),
    ("latency201cluster201", "bGF0ZW5jeTIwMWNsdXN0ZXIyMDE"),
    ("latency201mirror201", "bGF0ZW5jeTIwMW1pcnJvcjIwMQ"),
    ("buffer201mirror201", "YnVmZmVyMjAxbWlycm9yMjAx"),
    ("buffer201filter201", "YnVmZmVyMjAxZmlsdGVyMjAx"),
    ("buffer201ranking201", "YnVmZmVyMjAxcmFua2luZzIwMQ"),
    ("buffer201encoding201", "YnVmZmVyMjAxZW5jb2RpbmcyMDE"),
    ("queue201encoding201", "cXVldWUyMDFlbmNvZGluZzIwMQ"),
    ("queue201mapping201", "cXVldWUyMDFtYXBwaW5nMjAx"),
    ("queue201record201", "cXVldWUyMDFyZWNvcmQyMDE"),
    ("queue201candle201", "cXVldWUyMDFjYW5kbGUyMDE"),
    ("worker201candle201", "d29ya2VyMjAxY2FuZGxlMjAx"),
    ("worker201thread201", "d29ya2VyMjAxdGhyZWFkMjAx"),
    ("worker201kitten201", "d29ya2VyMjAxa2l0dGVuMjAx"),
    ("worker201sitting201", "d29ya2VyMjAxc2l0dGluZzIwMQ"),
    ("kernel201sitting201", "a2VybmVsMjAxc2l0dGluZzIwMQ"),
    ("kernel201agent201", "a2VybmVsMjAxYWdlbnQyMDE"),
    ("kernel201angle201", "a2VybmVsMjAxYW5nbGUyMDE"),
    ("kernel201universe201", "a2VybmVsMjAxdW5pdmVyc2UyMDE"),
    ("signal201universe201", "c2lnbmFsMjAxdW5pdmVyc2UyMDE"),
    ("signal201memory201", "c2lnbmFsMjAxbWVtb3J5MjAx"),
    ("signal201stream201", "c2lnbmFsMjAxc3RyZWFtMjAx"),
    ("signal201context201", "c2lnbmFsMjAxY29udGV4dDIwMQ"),
    ("packet201context201", "cGFja2V0MjAxY29udGV4dDIwMQ"),
    ("packet201knowledge201", "cGFja2V0MjAxa25vd2xlZGdlMjAx"),
    ("packet201vector201", "cGFja2V0MjAxdmVjdG9yMjAx"),
    ("packet201processor201", "cGFja2V0MjAxcHJvY2Vzc29yMjAx"),
    ("router201processor201", "cm91dGVyMjAxcHJvY2Vzc29yMjAx"),
    ("router201reasoning201", "cm91dGVyMjAxcmVhc29uaW5nMjAx"),
    ("router201machine201", "cm91dGVyMjAxbWFjaGluZTIwMQ"),
    ("router201learning201", "cm91dGVyMjAxbGVhcm5pbmcyMDE"),
    ("cluster201learning201", "Y2x1c3RlcjIwMWxlYXJuaW5nMjAx"),
    ("cluster201model201", "Y2x1c3RlcjIwMW1vZGVsMjAx"),
    ("cluster201token201", "Y2x1c3RlcjIwMXRva2VuMjAx"),
    ("cluster201prompt201", "Y2x1c3RlcjIwMXByb21wdDIwMQ"),
    ("mirror201prompt201", "bWlycm9yMjAxcHJvbXB0MjAx"),
    ("mirror201session201", "bWlycm9yMjAxc2Vzc2lvbjIwMQ"),
    ("mirror201library201", "bWlycm9yMjAxbGlicmFyeTIwMQ"),
    ("mirror201service201", "bWlycm9yMjAxc2VydmljZTIwMQ"),
    ("filter201service201", "ZmlsdGVyMjAxc2VydmljZTIwMQ"),
    ("filter201gateway201", "ZmlsdGVyMjAxZ2F0ZXdheTIwMQ"),
    ("filter201storage201", "ZmlsdGVyMjAxc3RvcmFnZTIwMQ"),
    ("filter201network201", "ZmlsdGVyMjAxbmV0d29yazIwMQ"),
    ("ranking201network201", "cmFua2luZzIwMW5ldHdvcmsyMDE"),
    ("ranking201latency201", "cmFua2luZzIwMWxhdGVuY3kyMDE"),
    ("ranking201buffer201", "cmFua2luZzIwMWJ1ZmZlcjIwMQ"),
    ("ranking201queue201", "cmFua2luZzIwMXF1ZXVlMjAx"),
    ("encoding201queue201", "ZW5jb2RpbmcyMDFxdWV1ZTIwMQ"),
    ("encoding201worker201", "ZW5jb2RpbmcyMDF3b3JrZXIyMDE"),
    ("encoding201kernel201", "ZW5jb2RpbmcyMDFrZXJuZWwyMDE"),
    ("encoding201signal201", "ZW5jb2RpbmcyMDFzaWduYWwyMDE"),
    ("mapping201signal201", "bWFwcGluZzIwMXNpZ25hbDIwMQ"),
    ("mapping201packet201", "bWFwcGluZzIwMXBhY2tldDIwMQ"),
    ("mapping201router201", "bWFwcGluZzIwMXJvdXRlcjIwMQ"),
    ("mapping201cluster201", "bWFwcGluZzIwMWNsdXN0ZXIyMDE"),
    ("record201cluster201", "cmVjb3JkMjAxY2x1c3RlcjIwMQ"),
    ("record201mirror201", "cmVjb3JkMjAxbWlycm9yMjAx"),
    ("record201filter201", "cmVjb3JkMjAxZmlsdGVyMjAx"),
    ("record201ranking201", "cmVjb3JkMjAxcmFua2luZzIwMQ"),
    ("candle201ranking201", "Y2FuZGxlMjAxcmFua2luZzIwMQ"),
    ("candle201encoding201", "Y2FuZGxlMjAxZW5jb2RpbmcyMDE"),
    ("candle201mapping201", "Y2FuZGxlMjAxbWFwcGluZzIwMQ"),
    ("candle201record201", "Y2FuZGxlMjAxcmVjb3JkMjAx"),
    ("thread201record201", "dGhyZWFkMjAxcmVjb3JkMjAx"),
    ("thread201candle201", "dGhyZWFkMjAxY2FuZGxlMjAx"),
    ("thread201thread201", "dGhyZWFkMjAxdGhyZWFkMjAx"),
    ("thread201kitten201", "dGhyZWFkMjAxa2l0dGVuMjAx"),
    (
        "round 201: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjAxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 201: agentuniverse is a framework for multi agents",
        "cm91bmQgMjAxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 201: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjAxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 201: the processor reads the record then stops",
        "cm91bmQgMjAxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 201: a worker pulls the next task from the queue",
        "cm91bmQgMjAxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 201: signals travel through the network layer",
        "cm91bmQgMjAxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 201: the gateway routes each request by policy",
        "cm91bmQgMjAxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 201: memory grows until the buffer is full",
        "cm91bmQgMjAxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 201: the cluster mirrors every packet twice",
        "cm91bmQgMjAxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 201: ranking uses tokens learned from the corpus",
        "cm91bmQgMjAxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 201: a long session ends when the candle dies",
        "cm91bmQgMjAxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 201: encode the prompt then map the result",
        "cm91bmQgMjAxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 201: the kernel wakes the worker at dawn",
        "cm91bmQgMjAxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 201: service latency drops after the patch",
        "cm91bmQgMjAxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 201: the library caches every vector it sees",
        "cm91bmQgMjAxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 201: agents argue then the debate resolves",
        "cm91bmQgMjAxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 201: the filter keeps only strong matches",
        "cm91bmQgMjAxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 201: the model answers with a short reply",
        "cm91bmQgMjAxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 201: the recorder stores the reasoning trace",
        "cm91bmQgMjAxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 201: the angel watches the processor run",
        "cm91bmQgMjAxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 201: angle of the vector decides the match",
        "cm91bmQgMjAxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 201: the candle burns twice as long at night",
        "cm91bmQgMjAxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 201: a mirror of the universe in one line",
        "cm91bmQgMjAxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 201: the queue drains before the storm", "cm91bmQgMjAxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
