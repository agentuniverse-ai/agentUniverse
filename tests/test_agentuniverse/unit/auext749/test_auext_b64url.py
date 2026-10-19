"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten749kitten749", "a2l0dGVuNzQ5a2l0dGVuNzQ5"),
    ("kitten749sitting749", "a2l0dGVuNzQ5c2l0dGluZzc0OQ"),
    ("kitten749agent749", "a2l0dGVuNzQ5YWdlbnQ3NDk"),
    ("kitten749angle749", "a2l0dGVuNzQ5YW5nbGU3NDk"),
    ("sitting749angle749", "c2l0dGluZzc0OWFuZ2xlNzQ5"),
    ("sitting749universe749", "c2l0dGluZzc0OXVuaXZlcnNlNzQ5"),
    ("sitting749memory749", "c2l0dGluZzc0OW1lbW9yeTc0OQ"),
    ("sitting749stream749", "c2l0dGluZzc0OXN0cmVhbTc0OQ"),
    ("agent749stream749", "YWdlbnQ3NDlzdHJlYW03NDk"),
    ("agent749context749", "YWdlbnQ3NDljb250ZXh0NzQ5"),
    ("agent749knowledge749", "YWdlbnQ3NDlrbm93bGVkZ2U3NDk"),
    ("agent749vector749", "YWdlbnQ3NDl2ZWN0b3I3NDk"),
    ("angle749vector749", "YW5nbGU3NDl2ZWN0b3I3NDk"),
    ("angle749processor749", "YW5nbGU3NDlwcm9jZXNzb3I3NDk"),
    ("angle749reasoning749", "YW5nbGU3NDlyZWFzb25pbmc3NDk"),
    ("angle749machine749", "YW5nbGU3NDltYWNoaW5lNzQ5"),
    ("universe749machine749", "dW5pdmVyc2U3NDltYWNoaW5lNzQ5"),
    ("universe749learning749", "dW5pdmVyc2U3NDlsZWFybmluZzc0OQ"),
    ("universe749model749", "dW5pdmVyc2U3NDltb2RlbDc0OQ"),
    ("universe749token749", "dW5pdmVyc2U3NDl0b2tlbjc0OQ"),
    ("memory749token749", "bWVtb3J5NzQ5dG9rZW43NDk"),
    ("memory749prompt749", "bWVtb3J5NzQ5cHJvbXB0NzQ5"),
    ("memory749session749", "bWVtb3J5NzQ5c2Vzc2lvbjc0OQ"),
    ("memory749library749", "bWVtb3J5NzQ5bGlicmFyeTc0OQ"),
    ("stream749library749", "c3RyZWFtNzQ5bGlicmFyeTc0OQ"),
    ("stream749service749", "c3RyZWFtNzQ5c2VydmljZTc0OQ"),
    ("stream749gateway749", "c3RyZWFtNzQ5Z2F0ZXdheTc0OQ"),
    ("stream749storage749", "c3RyZWFtNzQ5c3RvcmFnZTc0OQ"),
    ("context749storage749", "Y29udGV4dDc0OXN0b3JhZ2U3NDk"),
    ("context749network749", "Y29udGV4dDc0OW5ldHdvcms3NDk"),
    ("context749latency749", "Y29udGV4dDc0OWxhdGVuY3k3NDk"),
    ("context749buffer749", "Y29udGV4dDc0OWJ1ZmZlcjc0OQ"),
    ("knowledge749buffer749", "a25vd2xlZGdlNzQ5YnVmZmVyNzQ5"),
    ("knowledge749queue749", "a25vd2xlZGdlNzQ5cXVldWU3NDk"),
    ("knowledge749worker749", "a25vd2xlZGdlNzQ5d29ya2VyNzQ5"),
    ("knowledge749kernel749", "a25vd2xlZGdlNzQ5a2VybmVsNzQ5"),
    ("vector749kernel749", "dmVjdG9yNzQ5a2VybmVsNzQ5"),
    ("vector749signal749", "dmVjdG9yNzQ5c2lnbmFsNzQ5"),
    ("vector749packet749", "dmVjdG9yNzQ5cGFja2V0NzQ5"),
    ("vector749router749", "dmVjdG9yNzQ5cm91dGVyNzQ5"),
    ("processor749router749", "cHJvY2Vzc29yNzQ5cm91dGVyNzQ5"),
    ("processor749cluster749", "cHJvY2Vzc29yNzQ5Y2x1c3Rlcjc0OQ"),
    ("processor749mirror749", "cHJvY2Vzc29yNzQ5bWlycm9yNzQ5"),
    ("processor749filter749", "cHJvY2Vzc29yNzQ5ZmlsdGVyNzQ5"),
    ("reasoning749filter749", "cmVhc29uaW5nNzQ5ZmlsdGVyNzQ5"),
    ("reasoning749ranking749", "cmVhc29uaW5nNzQ5cmFua2luZzc0OQ"),
    ("reasoning749encoding749", "cmVhc29uaW5nNzQ5ZW5jb2Rpbmc3NDk"),
    ("reasoning749mapping749", "cmVhc29uaW5nNzQ5bWFwcGluZzc0OQ"),
    ("machine749mapping749", "bWFjaGluZTc0OW1hcHBpbmc3NDk"),
    ("machine749record749", "bWFjaGluZTc0OXJlY29yZDc0OQ"),
    ("machine749candle749", "bWFjaGluZTc0OWNhbmRsZTc0OQ"),
    ("machine749thread749", "bWFjaGluZTc0OXRocmVhZDc0OQ"),
    ("learning749thread749", "bGVhcm5pbmc3NDl0aHJlYWQ3NDk"),
    ("learning749kitten749", "bGVhcm5pbmc3NDlraXR0ZW43NDk"),
    ("learning749sitting749", "bGVhcm5pbmc3NDlzaXR0aW5nNzQ5"),
    ("learning749agent749", "bGVhcm5pbmc3NDlhZ2VudDc0OQ"),
    ("model749agent749", "bW9kZWw3NDlhZ2VudDc0OQ"),
    ("model749angle749", "bW9kZWw3NDlhbmdsZTc0OQ"),
    ("model749universe749", "bW9kZWw3NDl1bml2ZXJzZTc0OQ"),
    ("model749memory749", "bW9kZWw3NDltZW1vcnk3NDk"),
    ("token749memory749", "dG9rZW43NDltZW1vcnk3NDk"),
    ("token749stream749", "dG9rZW43NDlzdHJlYW03NDk"),
    ("token749context749", "dG9rZW43NDljb250ZXh0NzQ5"),
    ("token749knowledge749", "dG9rZW43NDlrbm93bGVkZ2U3NDk"),
    ("prompt749knowledge749", "cHJvbXB0NzQ5a25vd2xlZGdlNzQ5"),
    ("prompt749vector749", "cHJvbXB0NzQ5dmVjdG9yNzQ5"),
    ("prompt749processor749", "cHJvbXB0NzQ5cHJvY2Vzc29yNzQ5"),
    ("prompt749reasoning749", "cHJvbXB0NzQ5cmVhc29uaW5nNzQ5"),
    ("session749reasoning749", "c2Vzc2lvbjc0OXJlYXNvbmluZzc0OQ"),
    ("session749machine749", "c2Vzc2lvbjc0OW1hY2hpbmU3NDk"),
    ("session749learning749", "c2Vzc2lvbjc0OWxlYXJuaW5nNzQ5"),
    ("session749model749", "c2Vzc2lvbjc0OW1vZGVsNzQ5"),
    ("library749model749", "bGlicmFyeTc0OW1vZGVsNzQ5"),
    ("library749token749", "bGlicmFyeTc0OXRva2VuNzQ5"),
    ("library749prompt749", "bGlicmFyeTc0OXByb21wdDc0OQ"),
    ("library749session749", "bGlicmFyeTc0OXNlc3Npb243NDk"),
    ("service749session749", "c2VydmljZTc0OXNlc3Npb243NDk"),
    ("service749library749", "c2VydmljZTc0OWxpYnJhcnk3NDk"),
    ("service749service749", "c2VydmljZTc0OXNlcnZpY2U3NDk"),
    ("service749gateway749", "c2VydmljZTc0OWdhdGV3YXk3NDk"),
    ("gateway749gateway749", "Z2F0ZXdheTc0OWdhdGV3YXk3NDk"),
    ("gateway749storage749", "Z2F0ZXdheTc0OXN0b3JhZ2U3NDk"),
    ("gateway749network749", "Z2F0ZXdheTc0OW5ldHdvcms3NDk"),
    ("gateway749latency749", "Z2F0ZXdheTc0OWxhdGVuY3k3NDk"),
    ("storage749latency749", "c3RvcmFnZTc0OWxhdGVuY3k3NDk"),
    ("storage749buffer749", "c3RvcmFnZTc0OWJ1ZmZlcjc0OQ"),
    ("storage749queue749", "c3RvcmFnZTc0OXF1ZXVlNzQ5"),
    ("storage749worker749", "c3RvcmFnZTc0OXdvcmtlcjc0OQ"),
    ("network749worker749", "bmV0d29yazc0OXdvcmtlcjc0OQ"),
    ("network749kernel749", "bmV0d29yazc0OWtlcm5lbDc0OQ"),
    ("network749signal749", "bmV0d29yazc0OXNpZ25hbDc0OQ"),
    ("network749packet749", "bmV0d29yazc0OXBhY2tldDc0OQ"),
    ("latency749packet749", "bGF0ZW5jeTc0OXBhY2tldDc0OQ"),
    ("latency749router749", "bGF0ZW5jeTc0OXJvdXRlcjc0OQ"),
    ("latency749cluster749", "bGF0ZW5jeTc0OWNsdXN0ZXI3NDk"),
    ("latency749mirror749", "bGF0ZW5jeTc0OW1pcnJvcjc0OQ"),
    ("buffer749mirror749", "YnVmZmVyNzQ5bWlycm9yNzQ5"),
    ("buffer749filter749", "YnVmZmVyNzQ5ZmlsdGVyNzQ5"),
    ("buffer749ranking749", "YnVmZmVyNzQ5cmFua2luZzc0OQ"),
    ("buffer749encoding749", "YnVmZmVyNzQ5ZW5jb2Rpbmc3NDk"),
    ("queue749encoding749", "cXVldWU3NDllbmNvZGluZzc0OQ"),
    ("queue749mapping749", "cXVldWU3NDltYXBwaW5nNzQ5"),
    ("queue749record749", "cXVldWU3NDlyZWNvcmQ3NDk"),
    ("queue749candle749", "cXVldWU3NDljYW5kbGU3NDk"),
    ("worker749candle749", "d29ya2VyNzQ5Y2FuZGxlNzQ5"),
    ("worker749thread749", "d29ya2VyNzQ5dGhyZWFkNzQ5"),
    ("worker749kitten749", "d29ya2VyNzQ5a2l0dGVuNzQ5"),
    ("worker749sitting749", "d29ya2VyNzQ5c2l0dGluZzc0OQ"),
    ("kernel749sitting749", "a2VybmVsNzQ5c2l0dGluZzc0OQ"),
    ("kernel749agent749", "a2VybmVsNzQ5YWdlbnQ3NDk"),
    ("kernel749angle749", "a2VybmVsNzQ5YW5nbGU3NDk"),
    ("kernel749universe749", "a2VybmVsNzQ5dW5pdmVyc2U3NDk"),
    ("signal749universe749", "c2lnbmFsNzQ5dW5pdmVyc2U3NDk"),
    ("signal749memory749", "c2lnbmFsNzQ5bWVtb3J5NzQ5"),
    ("signal749stream749", "c2lnbmFsNzQ5c3RyZWFtNzQ5"),
    ("signal749context749", "c2lnbmFsNzQ5Y29udGV4dDc0OQ"),
    ("packet749context749", "cGFja2V0NzQ5Y29udGV4dDc0OQ"),
    ("packet749knowledge749", "cGFja2V0NzQ5a25vd2xlZGdlNzQ5"),
    ("packet749vector749", "cGFja2V0NzQ5dmVjdG9yNzQ5"),
    ("packet749processor749", "cGFja2V0NzQ5cHJvY2Vzc29yNzQ5"),
    ("router749processor749", "cm91dGVyNzQ5cHJvY2Vzc29yNzQ5"),
    ("router749reasoning749", "cm91dGVyNzQ5cmVhc29uaW5nNzQ5"),
    ("router749machine749", "cm91dGVyNzQ5bWFjaGluZTc0OQ"),
    ("router749learning749", "cm91dGVyNzQ5bGVhcm5pbmc3NDk"),
    ("cluster749learning749", "Y2x1c3Rlcjc0OWxlYXJuaW5nNzQ5"),
    ("cluster749model749", "Y2x1c3Rlcjc0OW1vZGVsNzQ5"),
    ("cluster749token749", "Y2x1c3Rlcjc0OXRva2VuNzQ5"),
    ("cluster749prompt749", "Y2x1c3Rlcjc0OXByb21wdDc0OQ"),
    ("mirror749prompt749", "bWlycm9yNzQ5cHJvbXB0NzQ5"),
    ("mirror749session749", "bWlycm9yNzQ5c2Vzc2lvbjc0OQ"),
    ("mirror749library749", "bWlycm9yNzQ5bGlicmFyeTc0OQ"),
    ("mirror749service749", "bWlycm9yNzQ5c2VydmljZTc0OQ"),
    ("filter749service749", "ZmlsdGVyNzQ5c2VydmljZTc0OQ"),
    ("filter749gateway749", "ZmlsdGVyNzQ5Z2F0ZXdheTc0OQ"),
    ("filter749storage749", "ZmlsdGVyNzQ5c3RvcmFnZTc0OQ"),
    ("filter749network749", "ZmlsdGVyNzQ5bmV0d29yazc0OQ"),
    ("ranking749network749", "cmFua2luZzc0OW5ldHdvcms3NDk"),
    ("ranking749latency749", "cmFua2luZzc0OWxhdGVuY3k3NDk"),
    ("ranking749buffer749", "cmFua2luZzc0OWJ1ZmZlcjc0OQ"),
    ("ranking749queue749", "cmFua2luZzc0OXF1ZXVlNzQ5"),
    ("encoding749queue749", "ZW5jb2Rpbmc3NDlxdWV1ZTc0OQ"),
    ("encoding749worker749", "ZW5jb2Rpbmc3NDl3b3JrZXI3NDk"),
    ("encoding749kernel749", "ZW5jb2Rpbmc3NDlrZXJuZWw3NDk"),
    ("encoding749signal749", "ZW5jb2Rpbmc3NDlzaWduYWw3NDk"),
    ("mapping749signal749", "bWFwcGluZzc0OXNpZ25hbDc0OQ"),
    ("mapping749packet749", "bWFwcGluZzc0OXBhY2tldDc0OQ"),
    ("mapping749router749", "bWFwcGluZzc0OXJvdXRlcjc0OQ"),
    ("mapping749cluster749", "bWFwcGluZzc0OWNsdXN0ZXI3NDk"),
    ("record749cluster749", "cmVjb3JkNzQ5Y2x1c3Rlcjc0OQ"),
    ("record749mirror749", "cmVjb3JkNzQ5bWlycm9yNzQ5"),
    ("record749filter749", "cmVjb3JkNzQ5ZmlsdGVyNzQ5"),
    ("record749ranking749", "cmVjb3JkNzQ5cmFua2luZzc0OQ"),
    ("candle749ranking749", "Y2FuZGxlNzQ5cmFua2luZzc0OQ"),
    ("candle749encoding749", "Y2FuZGxlNzQ5ZW5jb2Rpbmc3NDk"),
    ("candle749mapping749", "Y2FuZGxlNzQ5bWFwcGluZzc0OQ"),
    ("candle749record749", "Y2FuZGxlNzQ5cmVjb3JkNzQ5"),
    ("thread749record749", "dGhyZWFkNzQ5cmVjb3JkNzQ5"),
    ("thread749candle749", "dGhyZWFkNzQ5Y2FuZGxlNzQ5"),
    ("thread749thread749", "dGhyZWFkNzQ5dGhyZWFkNzQ5"),
    ("thread749kitten749", "dGhyZWFkNzQ5a2l0dGVuNzQ5"),
    (
        "round 749: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzQ5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 749: agentuniverse is a framework for multi agents",
        "cm91bmQgNzQ5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 749: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzQ5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 749: the processor reads the record then stops",
        "cm91bmQgNzQ5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 749: a worker pulls the next task from the queue",
        "cm91bmQgNzQ5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 749: signals travel through the network layer",
        "cm91bmQgNzQ5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 749: the gateway routes each request by policy",
        "cm91bmQgNzQ5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 749: memory grows until the buffer is full",
        "cm91bmQgNzQ5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 749: the cluster mirrors every packet twice",
        "cm91bmQgNzQ5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 749: ranking uses tokens learned from the corpus",
        "cm91bmQgNzQ5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 749: a long session ends when the candle dies",
        "cm91bmQgNzQ5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 749: encode the prompt then map the result",
        "cm91bmQgNzQ5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 749: the kernel wakes the worker at dawn",
        "cm91bmQgNzQ5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 749: service latency drops after the patch",
        "cm91bmQgNzQ5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 749: the library caches every vector it sees",
        "cm91bmQgNzQ5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 749: agents argue then the debate resolves",
        "cm91bmQgNzQ5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 749: the filter keeps only strong matches",
        "cm91bmQgNzQ5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 749: the model answers with a short reply",
        "cm91bmQgNzQ5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 749: the recorder stores the reasoning trace",
        "cm91bmQgNzQ5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 749: the angel watches the processor run",
        "cm91bmQgNzQ5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 749: angle of the vector decides the match",
        "cm91bmQgNzQ5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 749: the candle burns twice as long at night",
        "cm91bmQgNzQ5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 749: a mirror of the universe in one line",
        "cm91bmQgNzQ5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 749: the queue drains before the storm", "cm91bmQgNzQ5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
