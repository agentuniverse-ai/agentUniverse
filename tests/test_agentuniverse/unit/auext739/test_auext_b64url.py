"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten739kitten739", "a2l0dGVuNzM5a2l0dGVuNzM5"),
    ("kitten739sitting739", "a2l0dGVuNzM5c2l0dGluZzczOQ"),
    ("kitten739agent739", "a2l0dGVuNzM5YWdlbnQ3Mzk"),
    ("kitten739angle739", "a2l0dGVuNzM5YW5nbGU3Mzk"),
    ("sitting739angle739", "c2l0dGluZzczOWFuZ2xlNzM5"),
    ("sitting739universe739", "c2l0dGluZzczOXVuaXZlcnNlNzM5"),
    ("sitting739memory739", "c2l0dGluZzczOW1lbW9yeTczOQ"),
    ("sitting739stream739", "c2l0dGluZzczOXN0cmVhbTczOQ"),
    ("agent739stream739", "YWdlbnQ3MzlzdHJlYW03Mzk"),
    ("agent739context739", "YWdlbnQ3Mzljb250ZXh0NzM5"),
    ("agent739knowledge739", "YWdlbnQ3Mzlrbm93bGVkZ2U3Mzk"),
    ("agent739vector739", "YWdlbnQ3Mzl2ZWN0b3I3Mzk"),
    ("angle739vector739", "YW5nbGU3Mzl2ZWN0b3I3Mzk"),
    ("angle739processor739", "YW5nbGU3Mzlwcm9jZXNzb3I3Mzk"),
    ("angle739reasoning739", "YW5nbGU3MzlyZWFzb25pbmc3Mzk"),
    ("angle739machine739", "YW5nbGU3MzltYWNoaW5lNzM5"),
    ("universe739machine739", "dW5pdmVyc2U3MzltYWNoaW5lNzM5"),
    ("universe739learning739", "dW5pdmVyc2U3MzlsZWFybmluZzczOQ"),
    ("universe739model739", "dW5pdmVyc2U3Mzltb2RlbDczOQ"),
    ("universe739token739", "dW5pdmVyc2U3Mzl0b2tlbjczOQ"),
    ("memory739token739", "bWVtb3J5NzM5dG9rZW43Mzk"),
    ("memory739prompt739", "bWVtb3J5NzM5cHJvbXB0NzM5"),
    ("memory739session739", "bWVtb3J5NzM5c2Vzc2lvbjczOQ"),
    ("memory739library739", "bWVtb3J5NzM5bGlicmFyeTczOQ"),
    ("stream739library739", "c3RyZWFtNzM5bGlicmFyeTczOQ"),
    ("stream739service739", "c3RyZWFtNzM5c2VydmljZTczOQ"),
    ("stream739gateway739", "c3RyZWFtNzM5Z2F0ZXdheTczOQ"),
    ("stream739storage739", "c3RyZWFtNzM5c3RvcmFnZTczOQ"),
    ("context739storage739", "Y29udGV4dDczOXN0b3JhZ2U3Mzk"),
    ("context739network739", "Y29udGV4dDczOW5ldHdvcms3Mzk"),
    ("context739latency739", "Y29udGV4dDczOWxhdGVuY3k3Mzk"),
    ("context739buffer739", "Y29udGV4dDczOWJ1ZmZlcjczOQ"),
    ("knowledge739buffer739", "a25vd2xlZGdlNzM5YnVmZmVyNzM5"),
    ("knowledge739queue739", "a25vd2xlZGdlNzM5cXVldWU3Mzk"),
    ("knowledge739worker739", "a25vd2xlZGdlNzM5d29ya2VyNzM5"),
    ("knowledge739kernel739", "a25vd2xlZGdlNzM5a2VybmVsNzM5"),
    ("vector739kernel739", "dmVjdG9yNzM5a2VybmVsNzM5"),
    ("vector739signal739", "dmVjdG9yNzM5c2lnbmFsNzM5"),
    ("vector739packet739", "dmVjdG9yNzM5cGFja2V0NzM5"),
    ("vector739router739", "dmVjdG9yNzM5cm91dGVyNzM5"),
    ("processor739router739", "cHJvY2Vzc29yNzM5cm91dGVyNzM5"),
    ("processor739cluster739", "cHJvY2Vzc29yNzM5Y2x1c3RlcjczOQ"),
    ("processor739mirror739", "cHJvY2Vzc29yNzM5bWlycm9yNzM5"),
    ("processor739filter739", "cHJvY2Vzc29yNzM5ZmlsdGVyNzM5"),
    ("reasoning739filter739", "cmVhc29uaW5nNzM5ZmlsdGVyNzM5"),
    ("reasoning739ranking739", "cmVhc29uaW5nNzM5cmFua2luZzczOQ"),
    ("reasoning739encoding739", "cmVhc29uaW5nNzM5ZW5jb2Rpbmc3Mzk"),
    ("reasoning739mapping739", "cmVhc29uaW5nNzM5bWFwcGluZzczOQ"),
    ("machine739mapping739", "bWFjaGluZTczOW1hcHBpbmc3Mzk"),
    ("machine739record739", "bWFjaGluZTczOXJlY29yZDczOQ"),
    ("machine739candle739", "bWFjaGluZTczOWNhbmRsZTczOQ"),
    ("machine739thread739", "bWFjaGluZTczOXRocmVhZDczOQ"),
    ("learning739thread739", "bGVhcm5pbmc3Mzl0aHJlYWQ3Mzk"),
    ("learning739kitten739", "bGVhcm5pbmc3MzlraXR0ZW43Mzk"),
    ("learning739sitting739", "bGVhcm5pbmc3MzlzaXR0aW5nNzM5"),
    ("learning739agent739", "bGVhcm5pbmc3MzlhZ2VudDczOQ"),
    ("model739agent739", "bW9kZWw3MzlhZ2VudDczOQ"),
    ("model739angle739", "bW9kZWw3MzlhbmdsZTczOQ"),
    ("model739universe739", "bW9kZWw3Mzl1bml2ZXJzZTczOQ"),
    ("model739memory739", "bW9kZWw3MzltZW1vcnk3Mzk"),
    ("token739memory739", "dG9rZW43MzltZW1vcnk3Mzk"),
    ("token739stream739", "dG9rZW43MzlzdHJlYW03Mzk"),
    ("token739context739", "dG9rZW43Mzljb250ZXh0NzM5"),
    ("token739knowledge739", "dG9rZW43Mzlrbm93bGVkZ2U3Mzk"),
    ("prompt739knowledge739", "cHJvbXB0NzM5a25vd2xlZGdlNzM5"),
    ("prompt739vector739", "cHJvbXB0NzM5dmVjdG9yNzM5"),
    ("prompt739processor739", "cHJvbXB0NzM5cHJvY2Vzc29yNzM5"),
    ("prompt739reasoning739", "cHJvbXB0NzM5cmVhc29uaW5nNzM5"),
    ("session739reasoning739", "c2Vzc2lvbjczOXJlYXNvbmluZzczOQ"),
    ("session739machine739", "c2Vzc2lvbjczOW1hY2hpbmU3Mzk"),
    ("session739learning739", "c2Vzc2lvbjczOWxlYXJuaW5nNzM5"),
    ("session739model739", "c2Vzc2lvbjczOW1vZGVsNzM5"),
    ("library739model739", "bGlicmFyeTczOW1vZGVsNzM5"),
    ("library739token739", "bGlicmFyeTczOXRva2VuNzM5"),
    ("library739prompt739", "bGlicmFyeTczOXByb21wdDczOQ"),
    ("library739session739", "bGlicmFyeTczOXNlc3Npb243Mzk"),
    ("service739session739", "c2VydmljZTczOXNlc3Npb243Mzk"),
    ("service739library739", "c2VydmljZTczOWxpYnJhcnk3Mzk"),
    ("service739service739", "c2VydmljZTczOXNlcnZpY2U3Mzk"),
    ("service739gateway739", "c2VydmljZTczOWdhdGV3YXk3Mzk"),
    ("gateway739gateway739", "Z2F0ZXdheTczOWdhdGV3YXk3Mzk"),
    ("gateway739storage739", "Z2F0ZXdheTczOXN0b3JhZ2U3Mzk"),
    ("gateway739network739", "Z2F0ZXdheTczOW5ldHdvcms3Mzk"),
    ("gateway739latency739", "Z2F0ZXdheTczOWxhdGVuY3k3Mzk"),
    ("storage739latency739", "c3RvcmFnZTczOWxhdGVuY3k3Mzk"),
    ("storage739buffer739", "c3RvcmFnZTczOWJ1ZmZlcjczOQ"),
    ("storage739queue739", "c3RvcmFnZTczOXF1ZXVlNzM5"),
    ("storage739worker739", "c3RvcmFnZTczOXdvcmtlcjczOQ"),
    ("network739worker739", "bmV0d29yazczOXdvcmtlcjczOQ"),
    ("network739kernel739", "bmV0d29yazczOWtlcm5lbDczOQ"),
    ("network739signal739", "bmV0d29yazczOXNpZ25hbDczOQ"),
    ("network739packet739", "bmV0d29yazczOXBhY2tldDczOQ"),
    ("latency739packet739", "bGF0ZW5jeTczOXBhY2tldDczOQ"),
    ("latency739router739", "bGF0ZW5jeTczOXJvdXRlcjczOQ"),
    ("latency739cluster739", "bGF0ZW5jeTczOWNsdXN0ZXI3Mzk"),
    ("latency739mirror739", "bGF0ZW5jeTczOW1pcnJvcjczOQ"),
    ("buffer739mirror739", "YnVmZmVyNzM5bWlycm9yNzM5"),
    ("buffer739filter739", "YnVmZmVyNzM5ZmlsdGVyNzM5"),
    ("buffer739ranking739", "YnVmZmVyNzM5cmFua2luZzczOQ"),
    ("buffer739encoding739", "YnVmZmVyNzM5ZW5jb2Rpbmc3Mzk"),
    ("queue739encoding739", "cXVldWU3MzllbmNvZGluZzczOQ"),
    ("queue739mapping739", "cXVldWU3MzltYXBwaW5nNzM5"),
    ("queue739record739", "cXVldWU3MzlyZWNvcmQ3Mzk"),
    ("queue739candle739", "cXVldWU3MzljYW5kbGU3Mzk"),
    ("worker739candle739", "d29ya2VyNzM5Y2FuZGxlNzM5"),
    ("worker739thread739", "d29ya2VyNzM5dGhyZWFkNzM5"),
    ("worker739kitten739", "d29ya2VyNzM5a2l0dGVuNzM5"),
    ("worker739sitting739", "d29ya2VyNzM5c2l0dGluZzczOQ"),
    ("kernel739sitting739", "a2VybmVsNzM5c2l0dGluZzczOQ"),
    ("kernel739agent739", "a2VybmVsNzM5YWdlbnQ3Mzk"),
    ("kernel739angle739", "a2VybmVsNzM5YW5nbGU3Mzk"),
    ("kernel739universe739", "a2VybmVsNzM5dW5pdmVyc2U3Mzk"),
    ("signal739universe739", "c2lnbmFsNzM5dW5pdmVyc2U3Mzk"),
    ("signal739memory739", "c2lnbmFsNzM5bWVtb3J5NzM5"),
    ("signal739stream739", "c2lnbmFsNzM5c3RyZWFtNzM5"),
    ("signal739context739", "c2lnbmFsNzM5Y29udGV4dDczOQ"),
    ("packet739context739", "cGFja2V0NzM5Y29udGV4dDczOQ"),
    ("packet739knowledge739", "cGFja2V0NzM5a25vd2xlZGdlNzM5"),
    ("packet739vector739", "cGFja2V0NzM5dmVjdG9yNzM5"),
    ("packet739processor739", "cGFja2V0NzM5cHJvY2Vzc29yNzM5"),
    ("router739processor739", "cm91dGVyNzM5cHJvY2Vzc29yNzM5"),
    ("router739reasoning739", "cm91dGVyNzM5cmVhc29uaW5nNzM5"),
    ("router739machine739", "cm91dGVyNzM5bWFjaGluZTczOQ"),
    ("router739learning739", "cm91dGVyNzM5bGVhcm5pbmc3Mzk"),
    ("cluster739learning739", "Y2x1c3RlcjczOWxlYXJuaW5nNzM5"),
    ("cluster739model739", "Y2x1c3RlcjczOW1vZGVsNzM5"),
    ("cluster739token739", "Y2x1c3RlcjczOXRva2VuNzM5"),
    ("cluster739prompt739", "Y2x1c3RlcjczOXByb21wdDczOQ"),
    ("mirror739prompt739", "bWlycm9yNzM5cHJvbXB0NzM5"),
    ("mirror739session739", "bWlycm9yNzM5c2Vzc2lvbjczOQ"),
    ("mirror739library739", "bWlycm9yNzM5bGlicmFyeTczOQ"),
    ("mirror739service739", "bWlycm9yNzM5c2VydmljZTczOQ"),
    ("filter739service739", "ZmlsdGVyNzM5c2VydmljZTczOQ"),
    ("filter739gateway739", "ZmlsdGVyNzM5Z2F0ZXdheTczOQ"),
    ("filter739storage739", "ZmlsdGVyNzM5c3RvcmFnZTczOQ"),
    ("filter739network739", "ZmlsdGVyNzM5bmV0d29yazczOQ"),
    ("ranking739network739", "cmFua2luZzczOW5ldHdvcms3Mzk"),
    ("ranking739latency739", "cmFua2luZzczOWxhdGVuY3k3Mzk"),
    ("ranking739buffer739", "cmFua2luZzczOWJ1ZmZlcjczOQ"),
    ("ranking739queue739", "cmFua2luZzczOXF1ZXVlNzM5"),
    ("encoding739queue739", "ZW5jb2Rpbmc3MzlxdWV1ZTczOQ"),
    ("encoding739worker739", "ZW5jb2Rpbmc3Mzl3b3JrZXI3Mzk"),
    ("encoding739kernel739", "ZW5jb2Rpbmc3MzlrZXJuZWw3Mzk"),
    ("encoding739signal739", "ZW5jb2Rpbmc3MzlzaWduYWw3Mzk"),
    ("mapping739signal739", "bWFwcGluZzczOXNpZ25hbDczOQ"),
    ("mapping739packet739", "bWFwcGluZzczOXBhY2tldDczOQ"),
    ("mapping739router739", "bWFwcGluZzczOXJvdXRlcjczOQ"),
    ("mapping739cluster739", "bWFwcGluZzczOWNsdXN0ZXI3Mzk"),
    ("record739cluster739", "cmVjb3JkNzM5Y2x1c3RlcjczOQ"),
    ("record739mirror739", "cmVjb3JkNzM5bWlycm9yNzM5"),
    ("record739filter739", "cmVjb3JkNzM5ZmlsdGVyNzM5"),
    ("record739ranking739", "cmVjb3JkNzM5cmFua2luZzczOQ"),
    ("candle739ranking739", "Y2FuZGxlNzM5cmFua2luZzczOQ"),
    ("candle739encoding739", "Y2FuZGxlNzM5ZW5jb2Rpbmc3Mzk"),
    ("candle739mapping739", "Y2FuZGxlNzM5bWFwcGluZzczOQ"),
    ("candle739record739", "Y2FuZGxlNzM5cmVjb3JkNzM5"),
    ("thread739record739", "dGhyZWFkNzM5cmVjb3JkNzM5"),
    ("thread739candle739", "dGhyZWFkNzM5Y2FuZGxlNzM5"),
    ("thread739thread739", "dGhyZWFkNzM5dGhyZWFkNzM5"),
    ("thread739kitten739", "dGhyZWFkNzM5a2l0dGVuNzM5"),
    (
        "round 739: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzM5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 739: agentuniverse is a framework for multi agents",
        "cm91bmQgNzM5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 739: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzM5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 739: the processor reads the record then stops",
        "cm91bmQgNzM5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 739: a worker pulls the next task from the queue",
        "cm91bmQgNzM5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 739: signals travel through the network layer",
        "cm91bmQgNzM5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 739: the gateway routes each request by policy",
        "cm91bmQgNzM5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 739: memory grows until the buffer is full",
        "cm91bmQgNzM5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 739: the cluster mirrors every packet twice",
        "cm91bmQgNzM5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 739: ranking uses tokens learned from the corpus",
        "cm91bmQgNzM5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 739: a long session ends when the candle dies",
        "cm91bmQgNzM5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 739: encode the prompt then map the result",
        "cm91bmQgNzM5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 739: the kernel wakes the worker at dawn",
        "cm91bmQgNzM5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 739: service latency drops after the patch",
        "cm91bmQgNzM5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 739: the library caches every vector it sees",
        "cm91bmQgNzM5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 739: agents argue then the debate resolves",
        "cm91bmQgNzM5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 739: the filter keeps only strong matches",
        "cm91bmQgNzM5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 739: the model answers with a short reply",
        "cm91bmQgNzM5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 739: the recorder stores the reasoning trace",
        "cm91bmQgNzM5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 739: the angel watches the processor run",
        "cm91bmQgNzM5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 739: angle of the vector decides the match",
        "cm91bmQgNzM5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 739: the candle burns twice as long at night",
        "cm91bmQgNzM5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 739: a mirror of the universe in one line",
        "cm91bmQgNzM5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 739: the queue drains before the storm", "cm91bmQgNzM5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
