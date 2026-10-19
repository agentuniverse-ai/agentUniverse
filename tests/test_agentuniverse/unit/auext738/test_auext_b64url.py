"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten738kitten738", "a2l0dGVuNzM4a2l0dGVuNzM4"),
    ("kitten738sitting738", "a2l0dGVuNzM4c2l0dGluZzczOA"),
    ("kitten738agent738", "a2l0dGVuNzM4YWdlbnQ3Mzg"),
    ("kitten738angle738", "a2l0dGVuNzM4YW5nbGU3Mzg"),
    ("sitting738angle738", "c2l0dGluZzczOGFuZ2xlNzM4"),
    ("sitting738universe738", "c2l0dGluZzczOHVuaXZlcnNlNzM4"),
    ("sitting738memory738", "c2l0dGluZzczOG1lbW9yeTczOA"),
    ("sitting738stream738", "c2l0dGluZzczOHN0cmVhbTczOA"),
    ("agent738stream738", "YWdlbnQ3MzhzdHJlYW03Mzg"),
    ("agent738context738", "YWdlbnQ3Mzhjb250ZXh0NzM4"),
    ("agent738knowledge738", "YWdlbnQ3Mzhrbm93bGVkZ2U3Mzg"),
    ("agent738vector738", "YWdlbnQ3Mzh2ZWN0b3I3Mzg"),
    ("angle738vector738", "YW5nbGU3Mzh2ZWN0b3I3Mzg"),
    ("angle738processor738", "YW5nbGU3Mzhwcm9jZXNzb3I3Mzg"),
    ("angle738reasoning738", "YW5nbGU3MzhyZWFzb25pbmc3Mzg"),
    ("angle738machine738", "YW5nbGU3MzhtYWNoaW5lNzM4"),
    ("universe738machine738", "dW5pdmVyc2U3MzhtYWNoaW5lNzM4"),
    ("universe738learning738", "dW5pdmVyc2U3MzhsZWFybmluZzczOA"),
    ("universe738model738", "dW5pdmVyc2U3Mzhtb2RlbDczOA"),
    ("universe738token738", "dW5pdmVyc2U3Mzh0b2tlbjczOA"),
    ("memory738token738", "bWVtb3J5NzM4dG9rZW43Mzg"),
    ("memory738prompt738", "bWVtb3J5NzM4cHJvbXB0NzM4"),
    ("memory738session738", "bWVtb3J5NzM4c2Vzc2lvbjczOA"),
    ("memory738library738", "bWVtb3J5NzM4bGlicmFyeTczOA"),
    ("stream738library738", "c3RyZWFtNzM4bGlicmFyeTczOA"),
    ("stream738service738", "c3RyZWFtNzM4c2VydmljZTczOA"),
    ("stream738gateway738", "c3RyZWFtNzM4Z2F0ZXdheTczOA"),
    ("stream738storage738", "c3RyZWFtNzM4c3RvcmFnZTczOA"),
    ("context738storage738", "Y29udGV4dDczOHN0b3JhZ2U3Mzg"),
    ("context738network738", "Y29udGV4dDczOG5ldHdvcms3Mzg"),
    ("context738latency738", "Y29udGV4dDczOGxhdGVuY3k3Mzg"),
    ("context738buffer738", "Y29udGV4dDczOGJ1ZmZlcjczOA"),
    ("knowledge738buffer738", "a25vd2xlZGdlNzM4YnVmZmVyNzM4"),
    ("knowledge738queue738", "a25vd2xlZGdlNzM4cXVldWU3Mzg"),
    ("knowledge738worker738", "a25vd2xlZGdlNzM4d29ya2VyNzM4"),
    ("knowledge738kernel738", "a25vd2xlZGdlNzM4a2VybmVsNzM4"),
    ("vector738kernel738", "dmVjdG9yNzM4a2VybmVsNzM4"),
    ("vector738signal738", "dmVjdG9yNzM4c2lnbmFsNzM4"),
    ("vector738packet738", "dmVjdG9yNzM4cGFja2V0NzM4"),
    ("vector738router738", "dmVjdG9yNzM4cm91dGVyNzM4"),
    ("processor738router738", "cHJvY2Vzc29yNzM4cm91dGVyNzM4"),
    ("processor738cluster738", "cHJvY2Vzc29yNzM4Y2x1c3RlcjczOA"),
    ("processor738mirror738", "cHJvY2Vzc29yNzM4bWlycm9yNzM4"),
    ("processor738filter738", "cHJvY2Vzc29yNzM4ZmlsdGVyNzM4"),
    ("reasoning738filter738", "cmVhc29uaW5nNzM4ZmlsdGVyNzM4"),
    ("reasoning738ranking738", "cmVhc29uaW5nNzM4cmFua2luZzczOA"),
    ("reasoning738encoding738", "cmVhc29uaW5nNzM4ZW5jb2Rpbmc3Mzg"),
    ("reasoning738mapping738", "cmVhc29uaW5nNzM4bWFwcGluZzczOA"),
    ("machine738mapping738", "bWFjaGluZTczOG1hcHBpbmc3Mzg"),
    ("machine738record738", "bWFjaGluZTczOHJlY29yZDczOA"),
    ("machine738candle738", "bWFjaGluZTczOGNhbmRsZTczOA"),
    ("machine738thread738", "bWFjaGluZTczOHRocmVhZDczOA"),
    ("learning738thread738", "bGVhcm5pbmc3Mzh0aHJlYWQ3Mzg"),
    ("learning738kitten738", "bGVhcm5pbmc3MzhraXR0ZW43Mzg"),
    ("learning738sitting738", "bGVhcm5pbmc3MzhzaXR0aW5nNzM4"),
    ("learning738agent738", "bGVhcm5pbmc3MzhhZ2VudDczOA"),
    ("model738agent738", "bW9kZWw3MzhhZ2VudDczOA"),
    ("model738angle738", "bW9kZWw3MzhhbmdsZTczOA"),
    ("model738universe738", "bW9kZWw3Mzh1bml2ZXJzZTczOA"),
    ("model738memory738", "bW9kZWw3MzhtZW1vcnk3Mzg"),
    ("token738memory738", "dG9rZW43MzhtZW1vcnk3Mzg"),
    ("token738stream738", "dG9rZW43MzhzdHJlYW03Mzg"),
    ("token738context738", "dG9rZW43Mzhjb250ZXh0NzM4"),
    ("token738knowledge738", "dG9rZW43Mzhrbm93bGVkZ2U3Mzg"),
    ("prompt738knowledge738", "cHJvbXB0NzM4a25vd2xlZGdlNzM4"),
    ("prompt738vector738", "cHJvbXB0NzM4dmVjdG9yNzM4"),
    ("prompt738processor738", "cHJvbXB0NzM4cHJvY2Vzc29yNzM4"),
    ("prompt738reasoning738", "cHJvbXB0NzM4cmVhc29uaW5nNzM4"),
    ("session738reasoning738", "c2Vzc2lvbjczOHJlYXNvbmluZzczOA"),
    ("session738machine738", "c2Vzc2lvbjczOG1hY2hpbmU3Mzg"),
    ("session738learning738", "c2Vzc2lvbjczOGxlYXJuaW5nNzM4"),
    ("session738model738", "c2Vzc2lvbjczOG1vZGVsNzM4"),
    ("library738model738", "bGlicmFyeTczOG1vZGVsNzM4"),
    ("library738token738", "bGlicmFyeTczOHRva2VuNzM4"),
    ("library738prompt738", "bGlicmFyeTczOHByb21wdDczOA"),
    ("library738session738", "bGlicmFyeTczOHNlc3Npb243Mzg"),
    ("service738session738", "c2VydmljZTczOHNlc3Npb243Mzg"),
    ("service738library738", "c2VydmljZTczOGxpYnJhcnk3Mzg"),
    ("service738service738", "c2VydmljZTczOHNlcnZpY2U3Mzg"),
    ("service738gateway738", "c2VydmljZTczOGdhdGV3YXk3Mzg"),
    ("gateway738gateway738", "Z2F0ZXdheTczOGdhdGV3YXk3Mzg"),
    ("gateway738storage738", "Z2F0ZXdheTczOHN0b3JhZ2U3Mzg"),
    ("gateway738network738", "Z2F0ZXdheTczOG5ldHdvcms3Mzg"),
    ("gateway738latency738", "Z2F0ZXdheTczOGxhdGVuY3k3Mzg"),
    ("storage738latency738", "c3RvcmFnZTczOGxhdGVuY3k3Mzg"),
    ("storage738buffer738", "c3RvcmFnZTczOGJ1ZmZlcjczOA"),
    ("storage738queue738", "c3RvcmFnZTczOHF1ZXVlNzM4"),
    ("storage738worker738", "c3RvcmFnZTczOHdvcmtlcjczOA"),
    ("network738worker738", "bmV0d29yazczOHdvcmtlcjczOA"),
    ("network738kernel738", "bmV0d29yazczOGtlcm5lbDczOA"),
    ("network738signal738", "bmV0d29yazczOHNpZ25hbDczOA"),
    ("network738packet738", "bmV0d29yazczOHBhY2tldDczOA"),
    ("latency738packet738", "bGF0ZW5jeTczOHBhY2tldDczOA"),
    ("latency738router738", "bGF0ZW5jeTczOHJvdXRlcjczOA"),
    ("latency738cluster738", "bGF0ZW5jeTczOGNsdXN0ZXI3Mzg"),
    ("latency738mirror738", "bGF0ZW5jeTczOG1pcnJvcjczOA"),
    ("buffer738mirror738", "YnVmZmVyNzM4bWlycm9yNzM4"),
    ("buffer738filter738", "YnVmZmVyNzM4ZmlsdGVyNzM4"),
    ("buffer738ranking738", "YnVmZmVyNzM4cmFua2luZzczOA"),
    ("buffer738encoding738", "YnVmZmVyNzM4ZW5jb2Rpbmc3Mzg"),
    ("queue738encoding738", "cXVldWU3MzhlbmNvZGluZzczOA"),
    ("queue738mapping738", "cXVldWU3MzhtYXBwaW5nNzM4"),
    ("queue738record738", "cXVldWU3MzhyZWNvcmQ3Mzg"),
    ("queue738candle738", "cXVldWU3MzhjYW5kbGU3Mzg"),
    ("worker738candle738", "d29ya2VyNzM4Y2FuZGxlNzM4"),
    ("worker738thread738", "d29ya2VyNzM4dGhyZWFkNzM4"),
    ("worker738kitten738", "d29ya2VyNzM4a2l0dGVuNzM4"),
    ("worker738sitting738", "d29ya2VyNzM4c2l0dGluZzczOA"),
    ("kernel738sitting738", "a2VybmVsNzM4c2l0dGluZzczOA"),
    ("kernel738agent738", "a2VybmVsNzM4YWdlbnQ3Mzg"),
    ("kernel738angle738", "a2VybmVsNzM4YW5nbGU3Mzg"),
    ("kernel738universe738", "a2VybmVsNzM4dW5pdmVyc2U3Mzg"),
    ("signal738universe738", "c2lnbmFsNzM4dW5pdmVyc2U3Mzg"),
    ("signal738memory738", "c2lnbmFsNzM4bWVtb3J5NzM4"),
    ("signal738stream738", "c2lnbmFsNzM4c3RyZWFtNzM4"),
    ("signal738context738", "c2lnbmFsNzM4Y29udGV4dDczOA"),
    ("packet738context738", "cGFja2V0NzM4Y29udGV4dDczOA"),
    ("packet738knowledge738", "cGFja2V0NzM4a25vd2xlZGdlNzM4"),
    ("packet738vector738", "cGFja2V0NzM4dmVjdG9yNzM4"),
    ("packet738processor738", "cGFja2V0NzM4cHJvY2Vzc29yNzM4"),
    ("router738processor738", "cm91dGVyNzM4cHJvY2Vzc29yNzM4"),
    ("router738reasoning738", "cm91dGVyNzM4cmVhc29uaW5nNzM4"),
    ("router738machine738", "cm91dGVyNzM4bWFjaGluZTczOA"),
    ("router738learning738", "cm91dGVyNzM4bGVhcm5pbmc3Mzg"),
    ("cluster738learning738", "Y2x1c3RlcjczOGxlYXJuaW5nNzM4"),
    ("cluster738model738", "Y2x1c3RlcjczOG1vZGVsNzM4"),
    ("cluster738token738", "Y2x1c3RlcjczOHRva2VuNzM4"),
    ("cluster738prompt738", "Y2x1c3RlcjczOHByb21wdDczOA"),
    ("mirror738prompt738", "bWlycm9yNzM4cHJvbXB0NzM4"),
    ("mirror738session738", "bWlycm9yNzM4c2Vzc2lvbjczOA"),
    ("mirror738library738", "bWlycm9yNzM4bGlicmFyeTczOA"),
    ("mirror738service738", "bWlycm9yNzM4c2VydmljZTczOA"),
    ("filter738service738", "ZmlsdGVyNzM4c2VydmljZTczOA"),
    ("filter738gateway738", "ZmlsdGVyNzM4Z2F0ZXdheTczOA"),
    ("filter738storage738", "ZmlsdGVyNzM4c3RvcmFnZTczOA"),
    ("filter738network738", "ZmlsdGVyNzM4bmV0d29yazczOA"),
    ("ranking738network738", "cmFua2luZzczOG5ldHdvcms3Mzg"),
    ("ranking738latency738", "cmFua2luZzczOGxhdGVuY3k3Mzg"),
    ("ranking738buffer738", "cmFua2luZzczOGJ1ZmZlcjczOA"),
    ("ranking738queue738", "cmFua2luZzczOHF1ZXVlNzM4"),
    ("encoding738queue738", "ZW5jb2Rpbmc3MzhxdWV1ZTczOA"),
    ("encoding738worker738", "ZW5jb2Rpbmc3Mzh3b3JrZXI3Mzg"),
    ("encoding738kernel738", "ZW5jb2Rpbmc3MzhrZXJuZWw3Mzg"),
    ("encoding738signal738", "ZW5jb2Rpbmc3MzhzaWduYWw3Mzg"),
    ("mapping738signal738", "bWFwcGluZzczOHNpZ25hbDczOA"),
    ("mapping738packet738", "bWFwcGluZzczOHBhY2tldDczOA"),
    ("mapping738router738", "bWFwcGluZzczOHJvdXRlcjczOA"),
    ("mapping738cluster738", "bWFwcGluZzczOGNsdXN0ZXI3Mzg"),
    ("record738cluster738", "cmVjb3JkNzM4Y2x1c3RlcjczOA"),
    ("record738mirror738", "cmVjb3JkNzM4bWlycm9yNzM4"),
    ("record738filter738", "cmVjb3JkNzM4ZmlsdGVyNzM4"),
    ("record738ranking738", "cmVjb3JkNzM4cmFua2luZzczOA"),
    ("candle738ranking738", "Y2FuZGxlNzM4cmFua2luZzczOA"),
    ("candle738encoding738", "Y2FuZGxlNzM4ZW5jb2Rpbmc3Mzg"),
    ("candle738mapping738", "Y2FuZGxlNzM4bWFwcGluZzczOA"),
    ("candle738record738", "Y2FuZGxlNzM4cmVjb3JkNzM4"),
    ("thread738record738", "dGhyZWFkNzM4cmVjb3JkNzM4"),
    ("thread738candle738", "dGhyZWFkNzM4Y2FuZGxlNzM4"),
    ("thread738thread738", "dGhyZWFkNzM4dGhyZWFkNzM4"),
    ("thread738kitten738", "dGhyZWFkNzM4a2l0dGVuNzM4"),
    (
        "round 738: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzM4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 738: agentuniverse is a framework for multi agents",
        "cm91bmQgNzM4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 738: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzM4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 738: the processor reads the record then stops",
        "cm91bmQgNzM4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 738: a worker pulls the next task from the queue",
        "cm91bmQgNzM4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 738: signals travel through the network layer",
        "cm91bmQgNzM4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 738: the gateway routes each request by policy",
        "cm91bmQgNzM4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 738: memory grows until the buffer is full",
        "cm91bmQgNzM4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 738: the cluster mirrors every packet twice",
        "cm91bmQgNzM4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 738: ranking uses tokens learned from the corpus",
        "cm91bmQgNzM4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 738: a long session ends when the candle dies",
        "cm91bmQgNzM4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 738: encode the prompt then map the result",
        "cm91bmQgNzM4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 738: the kernel wakes the worker at dawn",
        "cm91bmQgNzM4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 738: service latency drops after the patch",
        "cm91bmQgNzM4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 738: the library caches every vector it sees",
        "cm91bmQgNzM4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 738: agents argue then the debate resolves",
        "cm91bmQgNzM4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 738: the filter keeps only strong matches",
        "cm91bmQgNzM4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 738: the model answers with a short reply",
        "cm91bmQgNzM4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 738: the recorder stores the reasoning trace",
        "cm91bmQgNzM4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 738: the angel watches the processor run",
        "cm91bmQgNzM4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 738: angle of the vector decides the match",
        "cm91bmQgNzM4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 738: the candle burns twice as long at night",
        "cm91bmQgNzM4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 738: a mirror of the universe in one line",
        "cm91bmQgNzM4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 738: the queue drains before the storm", "cm91bmQgNzM4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
