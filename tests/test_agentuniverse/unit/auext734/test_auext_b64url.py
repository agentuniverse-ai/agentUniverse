"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten734kitten734", "a2l0dGVuNzM0a2l0dGVuNzM0"),
    ("kitten734sitting734", "a2l0dGVuNzM0c2l0dGluZzczNA"),
    ("kitten734agent734", "a2l0dGVuNzM0YWdlbnQ3MzQ"),
    ("kitten734angle734", "a2l0dGVuNzM0YW5nbGU3MzQ"),
    ("sitting734angle734", "c2l0dGluZzczNGFuZ2xlNzM0"),
    ("sitting734universe734", "c2l0dGluZzczNHVuaXZlcnNlNzM0"),
    ("sitting734memory734", "c2l0dGluZzczNG1lbW9yeTczNA"),
    ("sitting734stream734", "c2l0dGluZzczNHN0cmVhbTczNA"),
    ("agent734stream734", "YWdlbnQ3MzRzdHJlYW03MzQ"),
    ("agent734context734", "YWdlbnQ3MzRjb250ZXh0NzM0"),
    ("agent734knowledge734", "YWdlbnQ3MzRrbm93bGVkZ2U3MzQ"),
    ("agent734vector734", "YWdlbnQ3MzR2ZWN0b3I3MzQ"),
    ("angle734vector734", "YW5nbGU3MzR2ZWN0b3I3MzQ"),
    ("angle734processor734", "YW5nbGU3MzRwcm9jZXNzb3I3MzQ"),
    ("angle734reasoning734", "YW5nbGU3MzRyZWFzb25pbmc3MzQ"),
    ("angle734machine734", "YW5nbGU3MzRtYWNoaW5lNzM0"),
    ("universe734machine734", "dW5pdmVyc2U3MzRtYWNoaW5lNzM0"),
    ("universe734learning734", "dW5pdmVyc2U3MzRsZWFybmluZzczNA"),
    ("universe734model734", "dW5pdmVyc2U3MzRtb2RlbDczNA"),
    ("universe734token734", "dW5pdmVyc2U3MzR0b2tlbjczNA"),
    ("memory734token734", "bWVtb3J5NzM0dG9rZW43MzQ"),
    ("memory734prompt734", "bWVtb3J5NzM0cHJvbXB0NzM0"),
    ("memory734session734", "bWVtb3J5NzM0c2Vzc2lvbjczNA"),
    ("memory734library734", "bWVtb3J5NzM0bGlicmFyeTczNA"),
    ("stream734library734", "c3RyZWFtNzM0bGlicmFyeTczNA"),
    ("stream734service734", "c3RyZWFtNzM0c2VydmljZTczNA"),
    ("stream734gateway734", "c3RyZWFtNzM0Z2F0ZXdheTczNA"),
    ("stream734storage734", "c3RyZWFtNzM0c3RvcmFnZTczNA"),
    ("context734storage734", "Y29udGV4dDczNHN0b3JhZ2U3MzQ"),
    ("context734network734", "Y29udGV4dDczNG5ldHdvcms3MzQ"),
    ("context734latency734", "Y29udGV4dDczNGxhdGVuY3k3MzQ"),
    ("context734buffer734", "Y29udGV4dDczNGJ1ZmZlcjczNA"),
    ("knowledge734buffer734", "a25vd2xlZGdlNzM0YnVmZmVyNzM0"),
    ("knowledge734queue734", "a25vd2xlZGdlNzM0cXVldWU3MzQ"),
    ("knowledge734worker734", "a25vd2xlZGdlNzM0d29ya2VyNzM0"),
    ("knowledge734kernel734", "a25vd2xlZGdlNzM0a2VybmVsNzM0"),
    ("vector734kernel734", "dmVjdG9yNzM0a2VybmVsNzM0"),
    ("vector734signal734", "dmVjdG9yNzM0c2lnbmFsNzM0"),
    ("vector734packet734", "dmVjdG9yNzM0cGFja2V0NzM0"),
    ("vector734router734", "dmVjdG9yNzM0cm91dGVyNzM0"),
    ("processor734router734", "cHJvY2Vzc29yNzM0cm91dGVyNzM0"),
    ("processor734cluster734", "cHJvY2Vzc29yNzM0Y2x1c3RlcjczNA"),
    ("processor734mirror734", "cHJvY2Vzc29yNzM0bWlycm9yNzM0"),
    ("processor734filter734", "cHJvY2Vzc29yNzM0ZmlsdGVyNzM0"),
    ("reasoning734filter734", "cmVhc29uaW5nNzM0ZmlsdGVyNzM0"),
    ("reasoning734ranking734", "cmVhc29uaW5nNzM0cmFua2luZzczNA"),
    ("reasoning734encoding734", "cmVhc29uaW5nNzM0ZW5jb2Rpbmc3MzQ"),
    ("reasoning734mapping734", "cmVhc29uaW5nNzM0bWFwcGluZzczNA"),
    ("machine734mapping734", "bWFjaGluZTczNG1hcHBpbmc3MzQ"),
    ("machine734record734", "bWFjaGluZTczNHJlY29yZDczNA"),
    ("machine734candle734", "bWFjaGluZTczNGNhbmRsZTczNA"),
    ("machine734thread734", "bWFjaGluZTczNHRocmVhZDczNA"),
    ("learning734thread734", "bGVhcm5pbmc3MzR0aHJlYWQ3MzQ"),
    ("learning734kitten734", "bGVhcm5pbmc3MzRraXR0ZW43MzQ"),
    ("learning734sitting734", "bGVhcm5pbmc3MzRzaXR0aW5nNzM0"),
    ("learning734agent734", "bGVhcm5pbmc3MzRhZ2VudDczNA"),
    ("model734agent734", "bW9kZWw3MzRhZ2VudDczNA"),
    ("model734angle734", "bW9kZWw3MzRhbmdsZTczNA"),
    ("model734universe734", "bW9kZWw3MzR1bml2ZXJzZTczNA"),
    ("model734memory734", "bW9kZWw3MzRtZW1vcnk3MzQ"),
    ("token734memory734", "dG9rZW43MzRtZW1vcnk3MzQ"),
    ("token734stream734", "dG9rZW43MzRzdHJlYW03MzQ"),
    ("token734context734", "dG9rZW43MzRjb250ZXh0NzM0"),
    ("token734knowledge734", "dG9rZW43MzRrbm93bGVkZ2U3MzQ"),
    ("prompt734knowledge734", "cHJvbXB0NzM0a25vd2xlZGdlNzM0"),
    ("prompt734vector734", "cHJvbXB0NzM0dmVjdG9yNzM0"),
    ("prompt734processor734", "cHJvbXB0NzM0cHJvY2Vzc29yNzM0"),
    ("prompt734reasoning734", "cHJvbXB0NzM0cmVhc29uaW5nNzM0"),
    ("session734reasoning734", "c2Vzc2lvbjczNHJlYXNvbmluZzczNA"),
    ("session734machine734", "c2Vzc2lvbjczNG1hY2hpbmU3MzQ"),
    ("session734learning734", "c2Vzc2lvbjczNGxlYXJuaW5nNzM0"),
    ("session734model734", "c2Vzc2lvbjczNG1vZGVsNzM0"),
    ("library734model734", "bGlicmFyeTczNG1vZGVsNzM0"),
    ("library734token734", "bGlicmFyeTczNHRva2VuNzM0"),
    ("library734prompt734", "bGlicmFyeTczNHByb21wdDczNA"),
    ("library734session734", "bGlicmFyeTczNHNlc3Npb243MzQ"),
    ("service734session734", "c2VydmljZTczNHNlc3Npb243MzQ"),
    ("service734library734", "c2VydmljZTczNGxpYnJhcnk3MzQ"),
    ("service734service734", "c2VydmljZTczNHNlcnZpY2U3MzQ"),
    ("service734gateway734", "c2VydmljZTczNGdhdGV3YXk3MzQ"),
    ("gateway734gateway734", "Z2F0ZXdheTczNGdhdGV3YXk3MzQ"),
    ("gateway734storage734", "Z2F0ZXdheTczNHN0b3JhZ2U3MzQ"),
    ("gateway734network734", "Z2F0ZXdheTczNG5ldHdvcms3MzQ"),
    ("gateway734latency734", "Z2F0ZXdheTczNGxhdGVuY3k3MzQ"),
    ("storage734latency734", "c3RvcmFnZTczNGxhdGVuY3k3MzQ"),
    ("storage734buffer734", "c3RvcmFnZTczNGJ1ZmZlcjczNA"),
    ("storage734queue734", "c3RvcmFnZTczNHF1ZXVlNzM0"),
    ("storage734worker734", "c3RvcmFnZTczNHdvcmtlcjczNA"),
    ("network734worker734", "bmV0d29yazczNHdvcmtlcjczNA"),
    ("network734kernel734", "bmV0d29yazczNGtlcm5lbDczNA"),
    ("network734signal734", "bmV0d29yazczNHNpZ25hbDczNA"),
    ("network734packet734", "bmV0d29yazczNHBhY2tldDczNA"),
    ("latency734packet734", "bGF0ZW5jeTczNHBhY2tldDczNA"),
    ("latency734router734", "bGF0ZW5jeTczNHJvdXRlcjczNA"),
    ("latency734cluster734", "bGF0ZW5jeTczNGNsdXN0ZXI3MzQ"),
    ("latency734mirror734", "bGF0ZW5jeTczNG1pcnJvcjczNA"),
    ("buffer734mirror734", "YnVmZmVyNzM0bWlycm9yNzM0"),
    ("buffer734filter734", "YnVmZmVyNzM0ZmlsdGVyNzM0"),
    ("buffer734ranking734", "YnVmZmVyNzM0cmFua2luZzczNA"),
    ("buffer734encoding734", "YnVmZmVyNzM0ZW5jb2Rpbmc3MzQ"),
    ("queue734encoding734", "cXVldWU3MzRlbmNvZGluZzczNA"),
    ("queue734mapping734", "cXVldWU3MzRtYXBwaW5nNzM0"),
    ("queue734record734", "cXVldWU3MzRyZWNvcmQ3MzQ"),
    ("queue734candle734", "cXVldWU3MzRjYW5kbGU3MzQ"),
    ("worker734candle734", "d29ya2VyNzM0Y2FuZGxlNzM0"),
    ("worker734thread734", "d29ya2VyNzM0dGhyZWFkNzM0"),
    ("worker734kitten734", "d29ya2VyNzM0a2l0dGVuNzM0"),
    ("worker734sitting734", "d29ya2VyNzM0c2l0dGluZzczNA"),
    ("kernel734sitting734", "a2VybmVsNzM0c2l0dGluZzczNA"),
    ("kernel734agent734", "a2VybmVsNzM0YWdlbnQ3MzQ"),
    ("kernel734angle734", "a2VybmVsNzM0YW5nbGU3MzQ"),
    ("kernel734universe734", "a2VybmVsNzM0dW5pdmVyc2U3MzQ"),
    ("signal734universe734", "c2lnbmFsNzM0dW5pdmVyc2U3MzQ"),
    ("signal734memory734", "c2lnbmFsNzM0bWVtb3J5NzM0"),
    ("signal734stream734", "c2lnbmFsNzM0c3RyZWFtNzM0"),
    ("signal734context734", "c2lnbmFsNzM0Y29udGV4dDczNA"),
    ("packet734context734", "cGFja2V0NzM0Y29udGV4dDczNA"),
    ("packet734knowledge734", "cGFja2V0NzM0a25vd2xlZGdlNzM0"),
    ("packet734vector734", "cGFja2V0NzM0dmVjdG9yNzM0"),
    ("packet734processor734", "cGFja2V0NzM0cHJvY2Vzc29yNzM0"),
    ("router734processor734", "cm91dGVyNzM0cHJvY2Vzc29yNzM0"),
    ("router734reasoning734", "cm91dGVyNzM0cmVhc29uaW5nNzM0"),
    ("router734machine734", "cm91dGVyNzM0bWFjaGluZTczNA"),
    ("router734learning734", "cm91dGVyNzM0bGVhcm5pbmc3MzQ"),
    ("cluster734learning734", "Y2x1c3RlcjczNGxlYXJuaW5nNzM0"),
    ("cluster734model734", "Y2x1c3RlcjczNG1vZGVsNzM0"),
    ("cluster734token734", "Y2x1c3RlcjczNHRva2VuNzM0"),
    ("cluster734prompt734", "Y2x1c3RlcjczNHByb21wdDczNA"),
    ("mirror734prompt734", "bWlycm9yNzM0cHJvbXB0NzM0"),
    ("mirror734session734", "bWlycm9yNzM0c2Vzc2lvbjczNA"),
    ("mirror734library734", "bWlycm9yNzM0bGlicmFyeTczNA"),
    ("mirror734service734", "bWlycm9yNzM0c2VydmljZTczNA"),
    ("filter734service734", "ZmlsdGVyNzM0c2VydmljZTczNA"),
    ("filter734gateway734", "ZmlsdGVyNzM0Z2F0ZXdheTczNA"),
    ("filter734storage734", "ZmlsdGVyNzM0c3RvcmFnZTczNA"),
    ("filter734network734", "ZmlsdGVyNzM0bmV0d29yazczNA"),
    ("ranking734network734", "cmFua2luZzczNG5ldHdvcms3MzQ"),
    ("ranking734latency734", "cmFua2luZzczNGxhdGVuY3k3MzQ"),
    ("ranking734buffer734", "cmFua2luZzczNGJ1ZmZlcjczNA"),
    ("ranking734queue734", "cmFua2luZzczNHF1ZXVlNzM0"),
    ("encoding734queue734", "ZW5jb2Rpbmc3MzRxdWV1ZTczNA"),
    ("encoding734worker734", "ZW5jb2Rpbmc3MzR3b3JrZXI3MzQ"),
    ("encoding734kernel734", "ZW5jb2Rpbmc3MzRrZXJuZWw3MzQ"),
    ("encoding734signal734", "ZW5jb2Rpbmc3MzRzaWduYWw3MzQ"),
    ("mapping734signal734", "bWFwcGluZzczNHNpZ25hbDczNA"),
    ("mapping734packet734", "bWFwcGluZzczNHBhY2tldDczNA"),
    ("mapping734router734", "bWFwcGluZzczNHJvdXRlcjczNA"),
    ("mapping734cluster734", "bWFwcGluZzczNGNsdXN0ZXI3MzQ"),
    ("record734cluster734", "cmVjb3JkNzM0Y2x1c3RlcjczNA"),
    ("record734mirror734", "cmVjb3JkNzM0bWlycm9yNzM0"),
    ("record734filter734", "cmVjb3JkNzM0ZmlsdGVyNzM0"),
    ("record734ranking734", "cmVjb3JkNzM0cmFua2luZzczNA"),
    ("candle734ranking734", "Y2FuZGxlNzM0cmFua2luZzczNA"),
    ("candle734encoding734", "Y2FuZGxlNzM0ZW5jb2Rpbmc3MzQ"),
    ("candle734mapping734", "Y2FuZGxlNzM0bWFwcGluZzczNA"),
    ("candle734record734", "Y2FuZGxlNzM0cmVjb3JkNzM0"),
    ("thread734record734", "dGhyZWFkNzM0cmVjb3JkNzM0"),
    ("thread734candle734", "dGhyZWFkNzM0Y2FuZGxlNzM0"),
    ("thread734thread734", "dGhyZWFkNzM0dGhyZWFkNzM0"),
    ("thread734kitten734", "dGhyZWFkNzM0a2l0dGVuNzM0"),
    (
        "round 734: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzM0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 734: agentuniverse is a framework for multi agents",
        "cm91bmQgNzM0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 734: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzM0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 734: the processor reads the record then stops",
        "cm91bmQgNzM0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 734: a worker pulls the next task from the queue",
        "cm91bmQgNzM0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 734: signals travel through the network layer",
        "cm91bmQgNzM0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 734: the gateway routes each request by policy",
        "cm91bmQgNzM0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 734: memory grows until the buffer is full",
        "cm91bmQgNzM0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 734: the cluster mirrors every packet twice",
        "cm91bmQgNzM0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 734: ranking uses tokens learned from the corpus",
        "cm91bmQgNzM0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 734: a long session ends when the candle dies",
        "cm91bmQgNzM0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 734: encode the prompt then map the result",
        "cm91bmQgNzM0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 734: the kernel wakes the worker at dawn",
        "cm91bmQgNzM0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 734: service latency drops after the patch",
        "cm91bmQgNzM0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 734: the library caches every vector it sees",
        "cm91bmQgNzM0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 734: agents argue then the debate resolves",
        "cm91bmQgNzM0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 734: the filter keeps only strong matches",
        "cm91bmQgNzM0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 734: the model answers with a short reply",
        "cm91bmQgNzM0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 734: the recorder stores the reasoning trace",
        "cm91bmQgNzM0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 734: the angel watches the processor run",
        "cm91bmQgNzM0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 734: angle of the vector decides the match",
        "cm91bmQgNzM0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 734: the candle burns twice as long at night",
        "cm91bmQgNzM0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 734: a mirror of the universe in one line",
        "cm91bmQgNzM0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 734: the queue drains before the storm", "cm91bmQgNzM0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
