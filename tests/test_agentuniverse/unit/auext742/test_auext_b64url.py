"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten742kitten742", "a2l0dGVuNzQya2l0dGVuNzQy"),
    ("kitten742sitting742", "a2l0dGVuNzQyc2l0dGluZzc0Mg"),
    ("kitten742agent742", "a2l0dGVuNzQyYWdlbnQ3NDI"),
    ("kitten742angle742", "a2l0dGVuNzQyYW5nbGU3NDI"),
    ("sitting742angle742", "c2l0dGluZzc0MmFuZ2xlNzQy"),
    ("sitting742universe742", "c2l0dGluZzc0MnVuaXZlcnNlNzQy"),
    ("sitting742memory742", "c2l0dGluZzc0Mm1lbW9yeTc0Mg"),
    ("sitting742stream742", "c2l0dGluZzc0MnN0cmVhbTc0Mg"),
    ("agent742stream742", "YWdlbnQ3NDJzdHJlYW03NDI"),
    ("agent742context742", "YWdlbnQ3NDJjb250ZXh0NzQy"),
    ("agent742knowledge742", "YWdlbnQ3NDJrbm93bGVkZ2U3NDI"),
    ("agent742vector742", "YWdlbnQ3NDJ2ZWN0b3I3NDI"),
    ("angle742vector742", "YW5nbGU3NDJ2ZWN0b3I3NDI"),
    ("angle742processor742", "YW5nbGU3NDJwcm9jZXNzb3I3NDI"),
    ("angle742reasoning742", "YW5nbGU3NDJyZWFzb25pbmc3NDI"),
    ("angle742machine742", "YW5nbGU3NDJtYWNoaW5lNzQy"),
    ("universe742machine742", "dW5pdmVyc2U3NDJtYWNoaW5lNzQy"),
    ("universe742learning742", "dW5pdmVyc2U3NDJsZWFybmluZzc0Mg"),
    ("universe742model742", "dW5pdmVyc2U3NDJtb2RlbDc0Mg"),
    ("universe742token742", "dW5pdmVyc2U3NDJ0b2tlbjc0Mg"),
    ("memory742token742", "bWVtb3J5NzQydG9rZW43NDI"),
    ("memory742prompt742", "bWVtb3J5NzQycHJvbXB0NzQy"),
    ("memory742session742", "bWVtb3J5NzQyc2Vzc2lvbjc0Mg"),
    ("memory742library742", "bWVtb3J5NzQybGlicmFyeTc0Mg"),
    ("stream742library742", "c3RyZWFtNzQybGlicmFyeTc0Mg"),
    ("stream742service742", "c3RyZWFtNzQyc2VydmljZTc0Mg"),
    ("stream742gateway742", "c3RyZWFtNzQyZ2F0ZXdheTc0Mg"),
    ("stream742storage742", "c3RyZWFtNzQyc3RvcmFnZTc0Mg"),
    ("context742storage742", "Y29udGV4dDc0MnN0b3JhZ2U3NDI"),
    ("context742network742", "Y29udGV4dDc0Mm5ldHdvcms3NDI"),
    ("context742latency742", "Y29udGV4dDc0MmxhdGVuY3k3NDI"),
    ("context742buffer742", "Y29udGV4dDc0MmJ1ZmZlcjc0Mg"),
    ("knowledge742buffer742", "a25vd2xlZGdlNzQyYnVmZmVyNzQy"),
    ("knowledge742queue742", "a25vd2xlZGdlNzQycXVldWU3NDI"),
    ("knowledge742worker742", "a25vd2xlZGdlNzQyd29ya2VyNzQy"),
    ("knowledge742kernel742", "a25vd2xlZGdlNzQya2VybmVsNzQy"),
    ("vector742kernel742", "dmVjdG9yNzQya2VybmVsNzQy"),
    ("vector742signal742", "dmVjdG9yNzQyc2lnbmFsNzQy"),
    ("vector742packet742", "dmVjdG9yNzQycGFja2V0NzQy"),
    ("vector742router742", "dmVjdG9yNzQycm91dGVyNzQy"),
    ("processor742router742", "cHJvY2Vzc29yNzQycm91dGVyNzQy"),
    ("processor742cluster742", "cHJvY2Vzc29yNzQyY2x1c3Rlcjc0Mg"),
    ("processor742mirror742", "cHJvY2Vzc29yNzQybWlycm9yNzQy"),
    ("processor742filter742", "cHJvY2Vzc29yNzQyZmlsdGVyNzQy"),
    ("reasoning742filter742", "cmVhc29uaW5nNzQyZmlsdGVyNzQy"),
    ("reasoning742ranking742", "cmVhc29uaW5nNzQycmFua2luZzc0Mg"),
    ("reasoning742encoding742", "cmVhc29uaW5nNzQyZW5jb2Rpbmc3NDI"),
    ("reasoning742mapping742", "cmVhc29uaW5nNzQybWFwcGluZzc0Mg"),
    ("machine742mapping742", "bWFjaGluZTc0Mm1hcHBpbmc3NDI"),
    ("machine742record742", "bWFjaGluZTc0MnJlY29yZDc0Mg"),
    ("machine742candle742", "bWFjaGluZTc0MmNhbmRsZTc0Mg"),
    ("machine742thread742", "bWFjaGluZTc0MnRocmVhZDc0Mg"),
    ("learning742thread742", "bGVhcm5pbmc3NDJ0aHJlYWQ3NDI"),
    ("learning742kitten742", "bGVhcm5pbmc3NDJraXR0ZW43NDI"),
    ("learning742sitting742", "bGVhcm5pbmc3NDJzaXR0aW5nNzQy"),
    ("learning742agent742", "bGVhcm5pbmc3NDJhZ2VudDc0Mg"),
    ("model742agent742", "bW9kZWw3NDJhZ2VudDc0Mg"),
    ("model742angle742", "bW9kZWw3NDJhbmdsZTc0Mg"),
    ("model742universe742", "bW9kZWw3NDJ1bml2ZXJzZTc0Mg"),
    ("model742memory742", "bW9kZWw3NDJtZW1vcnk3NDI"),
    ("token742memory742", "dG9rZW43NDJtZW1vcnk3NDI"),
    ("token742stream742", "dG9rZW43NDJzdHJlYW03NDI"),
    ("token742context742", "dG9rZW43NDJjb250ZXh0NzQy"),
    ("token742knowledge742", "dG9rZW43NDJrbm93bGVkZ2U3NDI"),
    ("prompt742knowledge742", "cHJvbXB0NzQya25vd2xlZGdlNzQy"),
    ("prompt742vector742", "cHJvbXB0NzQydmVjdG9yNzQy"),
    ("prompt742processor742", "cHJvbXB0NzQycHJvY2Vzc29yNzQy"),
    ("prompt742reasoning742", "cHJvbXB0NzQycmVhc29uaW5nNzQy"),
    ("session742reasoning742", "c2Vzc2lvbjc0MnJlYXNvbmluZzc0Mg"),
    ("session742machine742", "c2Vzc2lvbjc0Mm1hY2hpbmU3NDI"),
    ("session742learning742", "c2Vzc2lvbjc0MmxlYXJuaW5nNzQy"),
    ("session742model742", "c2Vzc2lvbjc0Mm1vZGVsNzQy"),
    ("library742model742", "bGlicmFyeTc0Mm1vZGVsNzQy"),
    ("library742token742", "bGlicmFyeTc0MnRva2VuNzQy"),
    ("library742prompt742", "bGlicmFyeTc0MnByb21wdDc0Mg"),
    ("library742session742", "bGlicmFyeTc0MnNlc3Npb243NDI"),
    ("service742session742", "c2VydmljZTc0MnNlc3Npb243NDI"),
    ("service742library742", "c2VydmljZTc0MmxpYnJhcnk3NDI"),
    ("service742service742", "c2VydmljZTc0MnNlcnZpY2U3NDI"),
    ("service742gateway742", "c2VydmljZTc0MmdhdGV3YXk3NDI"),
    ("gateway742gateway742", "Z2F0ZXdheTc0MmdhdGV3YXk3NDI"),
    ("gateway742storage742", "Z2F0ZXdheTc0MnN0b3JhZ2U3NDI"),
    ("gateway742network742", "Z2F0ZXdheTc0Mm5ldHdvcms3NDI"),
    ("gateway742latency742", "Z2F0ZXdheTc0MmxhdGVuY3k3NDI"),
    ("storage742latency742", "c3RvcmFnZTc0MmxhdGVuY3k3NDI"),
    ("storage742buffer742", "c3RvcmFnZTc0MmJ1ZmZlcjc0Mg"),
    ("storage742queue742", "c3RvcmFnZTc0MnF1ZXVlNzQy"),
    ("storage742worker742", "c3RvcmFnZTc0Mndvcmtlcjc0Mg"),
    ("network742worker742", "bmV0d29yazc0Mndvcmtlcjc0Mg"),
    ("network742kernel742", "bmV0d29yazc0Mmtlcm5lbDc0Mg"),
    ("network742signal742", "bmV0d29yazc0MnNpZ25hbDc0Mg"),
    ("network742packet742", "bmV0d29yazc0MnBhY2tldDc0Mg"),
    ("latency742packet742", "bGF0ZW5jeTc0MnBhY2tldDc0Mg"),
    ("latency742router742", "bGF0ZW5jeTc0MnJvdXRlcjc0Mg"),
    ("latency742cluster742", "bGF0ZW5jeTc0MmNsdXN0ZXI3NDI"),
    ("latency742mirror742", "bGF0ZW5jeTc0Mm1pcnJvcjc0Mg"),
    ("buffer742mirror742", "YnVmZmVyNzQybWlycm9yNzQy"),
    ("buffer742filter742", "YnVmZmVyNzQyZmlsdGVyNzQy"),
    ("buffer742ranking742", "YnVmZmVyNzQycmFua2luZzc0Mg"),
    ("buffer742encoding742", "YnVmZmVyNzQyZW5jb2Rpbmc3NDI"),
    ("queue742encoding742", "cXVldWU3NDJlbmNvZGluZzc0Mg"),
    ("queue742mapping742", "cXVldWU3NDJtYXBwaW5nNzQy"),
    ("queue742record742", "cXVldWU3NDJyZWNvcmQ3NDI"),
    ("queue742candle742", "cXVldWU3NDJjYW5kbGU3NDI"),
    ("worker742candle742", "d29ya2VyNzQyY2FuZGxlNzQy"),
    ("worker742thread742", "d29ya2VyNzQydGhyZWFkNzQy"),
    ("worker742kitten742", "d29ya2VyNzQya2l0dGVuNzQy"),
    ("worker742sitting742", "d29ya2VyNzQyc2l0dGluZzc0Mg"),
    ("kernel742sitting742", "a2VybmVsNzQyc2l0dGluZzc0Mg"),
    ("kernel742agent742", "a2VybmVsNzQyYWdlbnQ3NDI"),
    ("kernel742angle742", "a2VybmVsNzQyYW5nbGU3NDI"),
    ("kernel742universe742", "a2VybmVsNzQydW5pdmVyc2U3NDI"),
    ("signal742universe742", "c2lnbmFsNzQydW5pdmVyc2U3NDI"),
    ("signal742memory742", "c2lnbmFsNzQybWVtb3J5NzQy"),
    ("signal742stream742", "c2lnbmFsNzQyc3RyZWFtNzQy"),
    ("signal742context742", "c2lnbmFsNzQyY29udGV4dDc0Mg"),
    ("packet742context742", "cGFja2V0NzQyY29udGV4dDc0Mg"),
    ("packet742knowledge742", "cGFja2V0NzQya25vd2xlZGdlNzQy"),
    ("packet742vector742", "cGFja2V0NzQydmVjdG9yNzQy"),
    ("packet742processor742", "cGFja2V0NzQycHJvY2Vzc29yNzQy"),
    ("router742processor742", "cm91dGVyNzQycHJvY2Vzc29yNzQy"),
    ("router742reasoning742", "cm91dGVyNzQycmVhc29uaW5nNzQy"),
    ("router742machine742", "cm91dGVyNzQybWFjaGluZTc0Mg"),
    ("router742learning742", "cm91dGVyNzQybGVhcm5pbmc3NDI"),
    ("cluster742learning742", "Y2x1c3Rlcjc0MmxlYXJuaW5nNzQy"),
    ("cluster742model742", "Y2x1c3Rlcjc0Mm1vZGVsNzQy"),
    ("cluster742token742", "Y2x1c3Rlcjc0MnRva2VuNzQy"),
    ("cluster742prompt742", "Y2x1c3Rlcjc0MnByb21wdDc0Mg"),
    ("mirror742prompt742", "bWlycm9yNzQycHJvbXB0NzQy"),
    ("mirror742session742", "bWlycm9yNzQyc2Vzc2lvbjc0Mg"),
    ("mirror742library742", "bWlycm9yNzQybGlicmFyeTc0Mg"),
    ("mirror742service742", "bWlycm9yNzQyc2VydmljZTc0Mg"),
    ("filter742service742", "ZmlsdGVyNzQyc2VydmljZTc0Mg"),
    ("filter742gateway742", "ZmlsdGVyNzQyZ2F0ZXdheTc0Mg"),
    ("filter742storage742", "ZmlsdGVyNzQyc3RvcmFnZTc0Mg"),
    ("filter742network742", "ZmlsdGVyNzQybmV0d29yazc0Mg"),
    ("ranking742network742", "cmFua2luZzc0Mm5ldHdvcms3NDI"),
    ("ranking742latency742", "cmFua2luZzc0MmxhdGVuY3k3NDI"),
    ("ranking742buffer742", "cmFua2luZzc0MmJ1ZmZlcjc0Mg"),
    ("ranking742queue742", "cmFua2luZzc0MnF1ZXVlNzQy"),
    ("encoding742queue742", "ZW5jb2Rpbmc3NDJxdWV1ZTc0Mg"),
    ("encoding742worker742", "ZW5jb2Rpbmc3NDJ3b3JrZXI3NDI"),
    ("encoding742kernel742", "ZW5jb2Rpbmc3NDJrZXJuZWw3NDI"),
    ("encoding742signal742", "ZW5jb2Rpbmc3NDJzaWduYWw3NDI"),
    ("mapping742signal742", "bWFwcGluZzc0MnNpZ25hbDc0Mg"),
    ("mapping742packet742", "bWFwcGluZzc0MnBhY2tldDc0Mg"),
    ("mapping742router742", "bWFwcGluZzc0MnJvdXRlcjc0Mg"),
    ("mapping742cluster742", "bWFwcGluZzc0MmNsdXN0ZXI3NDI"),
    ("record742cluster742", "cmVjb3JkNzQyY2x1c3Rlcjc0Mg"),
    ("record742mirror742", "cmVjb3JkNzQybWlycm9yNzQy"),
    ("record742filter742", "cmVjb3JkNzQyZmlsdGVyNzQy"),
    ("record742ranking742", "cmVjb3JkNzQycmFua2luZzc0Mg"),
    ("candle742ranking742", "Y2FuZGxlNzQycmFua2luZzc0Mg"),
    ("candle742encoding742", "Y2FuZGxlNzQyZW5jb2Rpbmc3NDI"),
    ("candle742mapping742", "Y2FuZGxlNzQybWFwcGluZzc0Mg"),
    ("candle742record742", "Y2FuZGxlNzQycmVjb3JkNzQy"),
    ("thread742record742", "dGhyZWFkNzQycmVjb3JkNzQy"),
    ("thread742candle742", "dGhyZWFkNzQyY2FuZGxlNzQy"),
    ("thread742thread742", "dGhyZWFkNzQydGhyZWFkNzQy"),
    ("thread742kitten742", "dGhyZWFkNzQya2l0dGVuNzQy"),
    (
        "round 742: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzQyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 742: agentuniverse is a framework for multi agents",
        "cm91bmQgNzQyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 742: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzQyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 742: the processor reads the record then stops",
        "cm91bmQgNzQyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 742: a worker pulls the next task from the queue",
        "cm91bmQgNzQyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 742: signals travel through the network layer",
        "cm91bmQgNzQyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 742: the gateway routes each request by policy",
        "cm91bmQgNzQyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 742: memory grows until the buffer is full",
        "cm91bmQgNzQyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 742: the cluster mirrors every packet twice",
        "cm91bmQgNzQyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 742: ranking uses tokens learned from the corpus",
        "cm91bmQgNzQyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 742: a long session ends when the candle dies",
        "cm91bmQgNzQyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 742: encode the prompt then map the result",
        "cm91bmQgNzQyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 742: the kernel wakes the worker at dawn",
        "cm91bmQgNzQyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 742: service latency drops after the patch",
        "cm91bmQgNzQyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 742: the library caches every vector it sees",
        "cm91bmQgNzQyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 742: agents argue then the debate resolves",
        "cm91bmQgNzQyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 742: the filter keeps only strong matches",
        "cm91bmQgNzQyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 742: the model answers with a short reply",
        "cm91bmQgNzQyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 742: the recorder stores the reasoning trace",
        "cm91bmQgNzQyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 742: the angel watches the processor run",
        "cm91bmQgNzQyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 742: angle of the vector decides the match",
        "cm91bmQgNzQyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 742: the candle burns twice as long at night",
        "cm91bmQgNzQyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 742: a mirror of the universe in one line",
        "cm91bmQgNzQyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 742: the queue drains before the storm", "cm91bmQgNzQyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
