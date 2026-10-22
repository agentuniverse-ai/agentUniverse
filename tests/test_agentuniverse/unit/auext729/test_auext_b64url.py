"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten729kitten729", "a2l0dGVuNzI5a2l0dGVuNzI5"),
    ("kitten729sitting729", "a2l0dGVuNzI5c2l0dGluZzcyOQ"),
    ("kitten729agent729", "a2l0dGVuNzI5YWdlbnQ3Mjk"),
    ("kitten729angle729", "a2l0dGVuNzI5YW5nbGU3Mjk"),
    ("sitting729angle729", "c2l0dGluZzcyOWFuZ2xlNzI5"),
    ("sitting729universe729", "c2l0dGluZzcyOXVuaXZlcnNlNzI5"),
    ("sitting729memory729", "c2l0dGluZzcyOW1lbW9yeTcyOQ"),
    ("sitting729stream729", "c2l0dGluZzcyOXN0cmVhbTcyOQ"),
    ("agent729stream729", "YWdlbnQ3MjlzdHJlYW03Mjk"),
    ("agent729context729", "YWdlbnQ3Mjljb250ZXh0NzI5"),
    ("agent729knowledge729", "YWdlbnQ3Mjlrbm93bGVkZ2U3Mjk"),
    ("agent729vector729", "YWdlbnQ3Mjl2ZWN0b3I3Mjk"),
    ("angle729vector729", "YW5nbGU3Mjl2ZWN0b3I3Mjk"),
    ("angle729processor729", "YW5nbGU3Mjlwcm9jZXNzb3I3Mjk"),
    ("angle729reasoning729", "YW5nbGU3MjlyZWFzb25pbmc3Mjk"),
    ("angle729machine729", "YW5nbGU3MjltYWNoaW5lNzI5"),
    ("universe729machine729", "dW5pdmVyc2U3MjltYWNoaW5lNzI5"),
    ("universe729learning729", "dW5pdmVyc2U3MjlsZWFybmluZzcyOQ"),
    ("universe729model729", "dW5pdmVyc2U3Mjltb2RlbDcyOQ"),
    ("universe729token729", "dW5pdmVyc2U3Mjl0b2tlbjcyOQ"),
    ("memory729token729", "bWVtb3J5NzI5dG9rZW43Mjk"),
    ("memory729prompt729", "bWVtb3J5NzI5cHJvbXB0NzI5"),
    ("memory729session729", "bWVtb3J5NzI5c2Vzc2lvbjcyOQ"),
    ("memory729library729", "bWVtb3J5NzI5bGlicmFyeTcyOQ"),
    ("stream729library729", "c3RyZWFtNzI5bGlicmFyeTcyOQ"),
    ("stream729service729", "c3RyZWFtNzI5c2VydmljZTcyOQ"),
    ("stream729gateway729", "c3RyZWFtNzI5Z2F0ZXdheTcyOQ"),
    ("stream729storage729", "c3RyZWFtNzI5c3RvcmFnZTcyOQ"),
    ("context729storage729", "Y29udGV4dDcyOXN0b3JhZ2U3Mjk"),
    ("context729network729", "Y29udGV4dDcyOW5ldHdvcms3Mjk"),
    ("context729latency729", "Y29udGV4dDcyOWxhdGVuY3k3Mjk"),
    ("context729buffer729", "Y29udGV4dDcyOWJ1ZmZlcjcyOQ"),
    ("knowledge729buffer729", "a25vd2xlZGdlNzI5YnVmZmVyNzI5"),
    ("knowledge729queue729", "a25vd2xlZGdlNzI5cXVldWU3Mjk"),
    ("knowledge729worker729", "a25vd2xlZGdlNzI5d29ya2VyNzI5"),
    ("knowledge729kernel729", "a25vd2xlZGdlNzI5a2VybmVsNzI5"),
    ("vector729kernel729", "dmVjdG9yNzI5a2VybmVsNzI5"),
    ("vector729signal729", "dmVjdG9yNzI5c2lnbmFsNzI5"),
    ("vector729packet729", "dmVjdG9yNzI5cGFja2V0NzI5"),
    ("vector729router729", "dmVjdG9yNzI5cm91dGVyNzI5"),
    ("processor729router729", "cHJvY2Vzc29yNzI5cm91dGVyNzI5"),
    ("processor729cluster729", "cHJvY2Vzc29yNzI5Y2x1c3RlcjcyOQ"),
    ("processor729mirror729", "cHJvY2Vzc29yNzI5bWlycm9yNzI5"),
    ("processor729filter729", "cHJvY2Vzc29yNzI5ZmlsdGVyNzI5"),
    ("reasoning729filter729", "cmVhc29uaW5nNzI5ZmlsdGVyNzI5"),
    ("reasoning729ranking729", "cmVhc29uaW5nNzI5cmFua2luZzcyOQ"),
    ("reasoning729encoding729", "cmVhc29uaW5nNzI5ZW5jb2Rpbmc3Mjk"),
    ("reasoning729mapping729", "cmVhc29uaW5nNzI5bWFwcGluZzcyOQ"),
    ("machine729mapping729", "bWFjaGluZTcyOW1hcHBpbmc3Mjk"),
    ("machine729record729", "bWFjaGluZTcyOXJlY29yZDcyOQ"),
    ("machine729candle729", "bWFjaGluZTcyOWNhbmRsZTcyOQ"),
    ("machine729thread729", "bWFjaGluZTcyOXRocmVhZDcyOQ"),
    ("learning729thread729", "bGVhcm5pbmc3Mjl0aHJlYWQ3Mjk"),
    ("learning729kitten729", "bGVhcm5pbmc3MjlraXR0ZW43Mjk"),
    ("learning729sitting729", "bGVhcm5pbmc3MjlzaXR0aW5nNzI5"),
    ("learning729agent729", "bGVhcm5pbmc3MjlhZ2VudDcyOQ"),
    ("model729agent729", "bW9kZWw3MjlhZ2VudDcyOQ"),
    ("model729angle729", "bW9kZWw3MjlhbmdsZTcyOQ"),
    ("model729universe729", "bW9kZWw3Mjl1bml2ZXJzZTcyOQ"),
    ("model729memory729", "bW9kZWw3MjltZW1vcnk3Mjk"),
    ("token729memory729", "dG9rZW43MjltZW1vcnk3Mjk"),
    ("token729stream729", "dG9rZW43MjlzdHJlYW03Mjk"),
    ("token729context729", "dG9rZW43Mjljb250ZXh0NzI5"),
    ("token729knowledge729", "dG9rZW43Mjlrbm93bGVkZ2U3Mjk"),
    ("prompt729knowledge729", "cHJvbXB0NzI5a25vd2xlZGdlNzI5"),
    ("prompt729vector729", "cHJvbXB0NzI5dmVjdG9yNzI5"),
    ("prompt729processor729", "cHJvbXB0NzI5cHJvY2Vzc29yNzI5"),
    ("prompt729reasoning729", "cHJvbXB0NzI5cmVhc29uaW5nNzI5"),
    ("session729reasoning729", "c2Vzc2lvbjcyOXJlYXNvbmluZzcyOQ"),
    ("session729machine729", "c2Vzc2lvbjcyOW1hY2hpbmU3Mjk"),
    ("session729learning729", "c2Vzc2lvbjcyOWxlYXJuaW5nNzI5"),
    ("session729model729", "c2Vzc2lvbjcyOW1vZGVsNzI5"),
    ("library729model729", "bGlicmFyeTcyOW1vZGVsNzI5"),
    ("library729token729", "bGlicmFyeTcyOXRva2VuNzI5"),
    ("library729prompt729", "bGlicmFyeTcyOXByb21wdDcyOQ"),
    ("library729session729", "bGlicmFyeTcyOXNlc3Npb243Mjk"),
    ("service729session729", "c2VydmljZTcyOXNlc3Npb243Mjk"),
    ("service729library729", "c2VydmljZTcyOWxpYnJhcnk3Mjk"),
    ("service729service729", "c2VydmljZTcyOXNlcnZpY2U3Mjk"),
    ("service729gateway729", "c2VydmljZTcyOWdhdGV3YXk3Mjk"),
    ("gateway729gateway729", "Z2F0ZXdheTcyOWdhdGV3YXk3Mjk"),
    ("gateway729storage729", "Z2F0ZXdheTcyOXN0b3JhZ2U3Mjk"),
    ("gateway729network729", "Z2F0ZXdheTcyOW5ldHdvcms3Mjk"),
    ("gateway729latency729", "Z2F0ZXdheTcyOWxhdGVuY3k3Mjk"),
    ("storage729latency729", "c3RvcmFnZTcyOWxhdGVuY3k3Mjk"),
    ("storage729buffer729", "c3RvcmFnZTcyOWJ1ZmZlcjcyOQ"),
    ("storage729queue729", "c3RvcmFnZTcyOXF1ZXVlNzI5"),
    ("storage729worker729", "c3RvcmFnZTcyOXdvcmtlcjcyOQ"),
    ("network729worker729", "bmV0d29yazcyOXdvcmtlcjcyOQ"),
    ("network729kernel729", "bmV0d29yazcyOWtlcm5lbDcyOQ"),
    ("network729signal729", "bmV0d29yazcyOXNpZ25hbDcyOQ"),
    ("network729packet729", "bmV0d29yazcyOXBhY2tldDcyOQ"),
    ("latency729packet729", "bGF0ZW5jeTcyOXBhY2tldDcyOQ"),
    ("latency729router729", "bGF0ZW5jeTcyOXJvdXRlcjcyOQ"),
    ("latency729cluster729", "bGF0ZW5jeTcyOWNsdXN0ZXI3Mjk"),
    ("latency729mirror729", "bGF0ZW5jeTcyOW1pcnJvcjcyOQ"),
    ("buffer729mirror729", "YnVmZmVyNzI5bWlycm9yNzI5"),
    ("buffer729filter729", "YnVmZmVyNzI5ZmlsdGVyNzI5"),
    ("buffer729ranking729", "YnVmZmVyNzI5cmFua2luZzcyOQ"),
    ("buffer729encoding729", "YnVmZmVyNzI5ZW5jb2Rpbmc3Mjk"),
    ("queue729encoding729", "cXVldWU3MjllbmNvZGluZzcyOQ"),
    ("queue729mapping729", "cXVldWU3MjltYXBwaW5nNzI5"),
    ("queue729record729", "cXVldWU3MjlyZWNvcmQ3Mjk"),
    ("queue729candle729", "cXVldWU3MjljYW5kbGU3Mjk"),
    ("worker729candle729", "d29ya2VyNzI5Y2FuZGxlNzI5"),
    ("worker729thread729", "d29ya2VyNzI5dGhyZWFkNzI5"),
    ("worker729kitten729", "d29ya2VyNzI5a2l0dGVuNzI5"),
    ("worker729sitting729", "d29ya2VyNzI5c2l0dGluZzcyOQ"),
    ("kernel729sitting729", "a2VybmVsNzI5c2l0dGluZzcyOQ"),
    ("kernel729agent729", "a2VybmVsNzI5YWdlbnQ3Mjk"),
    ("kernel729angle729", "a2VybmVsNzI5YW5nbGU3Mjk"),
    ("kernel729universe729", "a2VybmVsNzI5dW5pdmVyc2U3Mjk"),
    ("signal729universe729", "c2lnbmFsNzI5dW5pdmVyc2U3Mjk"),
    ("signal729memory729", "c2lnbmFsNzI5bWVtb3J5NzI5"),
    ("signal729stream729", "c2lnbmFsNzI5c3RyZWFtNzI5"),
    ("signal729context729", "c2lnbmFsNzI5Y29udGV4dDcyOQ"),
    ("packet729context729", "cGFja2V0NzI5Y29udGV4dDcyOQ"),
    ("packet729knowledge729", "cGFja2V0NzI5a25vd2xlZGdlNzI5"),
    ("packet729vector729", "cGFja2V0NzI5dmVjdG9yNzI5"),
    ("packet729processor729", "cGFja2V0NzI5cHJvY2Vzc29yNzI5"),
    ("router729processor729", "cm91dGVyNzI5cHJvY2Vzc29yNzI5"),
    ("router729reasoning729", "cm91dGVyNzI5cmVhc29uaW5nNzI5"),
    ("router729machine729", "cm91dGVyNzI5bWFjaGluZTcyOQ"),
    ("router729learning729", "cm91dGVyNzI5bGVhcm5pbmc3Mjk"),
    ("cluster729learning729", "Y2x1c3RlcjcyOWxlYXJuaW5nNzI5"),
    ("cluster729model729", "Y2x1c3RlcjcyOW1vZGVsNzI5"),
    ("cluster729token729", "Y2x1c3RlcjcyOXRva2VuNzI5"),
    ("cluster729prompt729", "Y2x1c3RlcjcyOXByb21wdDcyOQ"),
    ("mirror729prompt729", "bWlycm9yNzI5cHJvbXB0NzI5"),
    ("mirror729session729", "bWlycm9yNzI5c2Vzc2lvbjcyOQ"),
    ("mirror729library729", "bWlycm9yNzI5bGlicmFyeTcyOQ"),
    ("mirror729service729", "bWlycm9yNzI5c2VydmljZTcyOQ"),
    ("filter729service729", "ZmlsdGVyNzI5c2VydmljZTcyOQ"),
    ("filter729gateway729", "ZmlsdGVyNzI5Z2F0ZXdheTcyOQ"),
    ("filter729storage729", "ZmlsdGVyNzI5c3RvcmFnZTcyOQ"),
    ("filter729network729", "ZmlsdGVyNzI5bmV0d29yazcyOQ"),
    ("ranking729network729", "cmFua2luZzcyOW5ldHdvcms3Mjk"),
    ("ranking729latency729", "cmFua2luZzcyOWxhdGVuY3k3Mjk"),
    ("ranking729buffer729", "cmFua2luZzcyOWJ1ZmZlcjcyOQ"),
    ("ranking729queue729", "cmFua2luZzcyOXF1ZXVlNzI5"),
    ("encoding729queue729", "ZW5jb2Rpbmc3MjlxdWV1ZTcyOQ"),
    ("encoding729worker729", "ZW5jb2Rpbmc3Mjl3b3JrZXI3Mjk"),
    ("encoding729kernel729", "ZW5jb2Rpbmc3MjlrZXJuZWw3Mjk"),
    ("encoding729signal729", "ZW5jb2Rpbmc3MjlzaWduYWw3Mjk"),
    ("mapping729signal729", "bWFwcGluZzcyOXNpZ25hbDcyOQ"),
    ("mapping729packet729", "bWFwcGluZzcyOXBhY2tldDcyOQ"),
    ("mapping729router729", "bWFwcGluZzcyOXJvdXRlcjcyOQ"),
    ("mapping729cluster729", "bWFwcGluZzcyOWNsdXN0ZXI3Mjk"),
    ("record729cluster729", "cmVjb3JkNzI5Y2x1c3RlcjcyOQ"),
    ("record729mirror729", "cmVjb3JkNzI5bWlycm9yNzI5"),
    ("record729filter729", "cmVjb3JkNzI5ZmlsdGVyNzI5"),
    ("record729ranking729", "cmVjb3JkNzI5cmFua2luZzcyOQ"),
    ("candle729ranking729", "Y2FuZGxlNzI5cmFua2luZzcyOQ"),
    ("candle729encoding729", "Y2FuZGxlNzI5ZW5jb2Rpbmc3Mjk"),
    ("candle729mapping729", "Y2FuZGxlNzI5bWFwcGluZzcyOQ"),
    ("candle729record729", "Y2FuZGxlNzI5cmVjb3JkNzI5"),
    ("thread729record729", "dGhyZWFkNzI5cmVjb3JkNzI5"),
    ("thread729candle729", "dGhyZWFkNzI5Y2FuZGxlNzI5"),
    ("thread729thread729", "dGhyZWFkNzI5dGhyZWFkNzI5"),
    ("thread729kitten729", "dGhyZWFkNzI5a2l0dGVuNzI5"),
    (
        "round 729: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzI5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 729: agentuniverse is a framework for multi agents",
        "cm91bmQgNzI5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 729: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzI5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 729: the processor reads the record then stops",
        "cm91bmQgNzI5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 729: a worker pulls the next task from the queue",
        "cm91bmQgNzI5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 729: signals travel through the network layer",
        "cm91bmQgNzI5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 729: the gateway routes each request by policy",
        "cm91bmQgNzI5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 729: memory grows until the buffer is full",
        "cm91bmQgNzI5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 729: the cluster mirrors every packet twice",
        "cm91bmQgNzI5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 729: ranking uses tokens learned from the corpus",
        "cm91bmQgNzI5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 729: a long session ends when the candle dies",
        "cm91bmQgNzI5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 729: encode the prompt then map the result",
        "cm91bmQgNzI5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 729: the kernel wakes the worker at dawn",
        "cm91bmQgNzI5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 729: service latency drops after the patch",
        "cm91bmQgNzI5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 729: the library caches every vector it sees",
        "cm91bmQgNzI5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 729: agents argue then the debate resolves",
        "cm91bmQgNzI5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 729: the filter keeps only strong matches",
        "cm91bmQgNzI5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 729: the model answers with a short reply",
        "cm91bmQgNzI5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 729: the recorder stores the reasoning trace",
        "cm91bmQgNzI5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 729: the angel watches the processor run",
        "cm91bmQgNzI5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 729: angle of the vector decides the match",
        "cm91bmQgNzI5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 729: the candle burns twice as long at night",
        "cm91bmQgNzI5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 729: a mirror of the universe in one line",
        "cm91bmQgNzI5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 729: the queue drains before the storm", "cm91bmQgNzI5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
