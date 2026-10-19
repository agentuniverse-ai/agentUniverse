"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten743kitten743", "a2l0dGVuNzQza2l0dGVuNzQz"),
    ("kitten743sitting743", "a2l0dGVuNzQzc2l0dGluZzc0Mw"),
    ("kitten743agent743", "a2l0dGVuNzQzYWdlbnQ3NDM"),
    ("kitten743angle743", "a2l0dGVuNzQzYW5nbGU3NDM"),
    ("sitting743angle743", "c2l0dGluZzc0M2FuZ2xlNzQz"),
    ("sitting743universe743", "c2l0dGluZzc0M3VuaXZlcnNlNzQz"),
    ("sitting743memory743", "c2l0dGluZzc0M21lbW9yeTc0Mw"),
    ("sitting743stream743", "c2l0dGluZzc0M3N0cmVhbTc0Mw"),
    ("agent743stream743", "YWdlbnQ3NDNzdHJlYW03NDM"),
    ("agent743context743", "YWdlbnQ3NDNjb250ZXh0NzQz"),
    ("agent743knowledge743", "YWdlbnQ3NDNrbm93bGVkZ2U3NDM"),
    ("agent743vector743", "YWdlbnQ3NDN2ZWN0b3I3NDM"),
    ("angle743vector743", "YW5nbGU3NDN2ZWN0b3I3NDM"),
    ("angle743processor743", "YW5nbGU3NDNwcm9jZXNzb3I3NDM"),
    ("angle743reasoning743", "YW5nbGU3NDNyZWFzb25pbmc3NDM"),
    ("angle743machine743", "YW5nbGU3NDNtYWNoaW5lNzQz"),
    ("universe743machine743", "dW5pdmVyc2U3NDNtYWNoaW5lNzQz"),
    ("universe743learning743", "dW5pdmVyc2U3NDNsZWFybmluZzc0Mw"),
    ("universe743model743", "dW5pdmVyc2U3NDNtb2RlbDc0Mw"),
    ("universe743token743", "dW5pdmVyc2U3NDN0b2tlbjc0Mw"),
    ("memory743token743", "bWVtb3J5NzQzdG9rZW43NDM"),
    ("memory743prompt743", "bWVtb3J5NzQzcHJvbXB0NzQz"),
    ("memory743session743", "bWVtb3J5NzQzc2Vzc2lvbjc0Mw"),
    ("memory743library743", "bWVtb3J5NzQzbGlicmFyeTc0Mw"),
    ("stream743library743", "c3RyZWFtNzQzbGlicmFyeTc0Mw"),
    ("stream743service743", "c3RyZWFtNzQzc2VydmljZTc0Mw"),
    ("stream743gateway743", "c3RyZWFtNzQzZ2F0ZXdheTc0Mw"),
    ("stream743storage743", "c3RyZWFtNzQzc3RvcmFnZTc0Mw"),
    ("context743storage743", "Y29udGV4dDc0M3N0b3JhZ2U3NDM"),
    ("context743network743", "Y29udGV4dDc0M25ldHdvcms3NDM"),
    ("context743latency743", "Y29udGV4dDc0M2xhdGVuY3k3NDM"),
    ("context743buffer743", "Y29udGV4dDc0M2J1ZmZlcjc0Mw"),
    ("knowledge743buffer743", "a25vd2xlZGdlNzQzYnVmZmVyNzQz"),
    ("knowledge743queue743", "a25vd2xlZGdlNzQzcXVldWU3NDM"),
    ("knowledge743worker743", "a25vd2xlZGdlNzQzd29ya2VyNzQz"),
    ("knowledge743kernel743", "a25vd2xlZGdlNzQza2VybmVsNzQz"),
    ("vector743kernel743", "dmVjdG9yNzQza2VybmVsNzQz"),
    ("vector743signal743", "dmVjdG9yNzQzc2lnbmFsNzQz"),
    ("vector743packet743", "dmVjdG9yNzQzcGFja2V0NzQz"),
    ("vector743router743", "dmVjdG9yNzQzcm91dGVyNzQz"),
    ("processor743router743", "cHJvY2Vzc29yNzQzcm91dGVyNzQz"),
    ("processor743cluster743", "cHJvY2Vzc29yNzQzY2x1c3Rlcjc0Mw"),
    ("processor743mirror743", "cHJvY2Vzc29yNzQzbWlycm9yNzQz"),
    ("processor743filter743", "cHJvY2Vzc29yNzQzZmlsdGVyNzQz"),
    ("reasoning743filter743", "cmVhc29uaW5nNzQzZmlsdGVyNzQz"),
    ("reasoning743ranking743", "cmVhc29uaW5nNzQzcmFua2luZzc0Mw"),
    ("reasoning743encoding743", "cmVhc29uaW5nNzQzZW5jb2Rpbmc3NDM"),
    ("reasoning743mapping743", "cmVhc29uaW5nNzQzbWFwcGluZzc0Mw"),
    ("machine743mapping743", "bWFjaGluZTc0M21hcHBpbmc3NDM"),
    ("machine743record743", "bWFjaGluZTc0M3JlY29yZDc0Mw"),
    ("machine743candle743", "bWFjaGluZTc0M2NhbmRsZTc0Mw"),
    ("machine743thread743", "bWFjaGluZTc0M3RocmVhZDc0Mw"),
    ("learning743thread743", "bGVhcm5pbmc3NDN0aHJlYWQ3NDM"),
    ("learning743kitten743", "bGVhcm5pbmc3NDNraXR0ZW43NDM"),
    ("learning743sitting743", "bGVhcm5pbmc3NDNzaXR0aW5nNzQz"),
    ("learning743agent743", "bGVhcm5pbmc3NDNhZ2VudDc0Mw"),
    ("model743agent743", "bW9kZWw3NDNhZ2VudDc0Mw"),
    ("model743angle743", "bW9kZWw3NDNhbmdsZTc0Mw"),
    ("model743universe743", "bW9kZWw3NDN1bml2ZXJzZTc0Mw"),
    ("model743memory743", "bW9kZWw3NDNtZW1vcnk3NDM"),
    ("token743memory743", "dG9rZW43NDNtZW1vcnk3NDM"),
    ("token743stream743", "dG9rZW43NDNzdHJlYW03NDM"),
    ("token743context743", "dG9rZW43NDNjb250ZXh0NzQz"),
    ("token743knowledge743", "dG9rZW43NDNrbm93bGVkZ2U3NDM"),
    ("prompt743knowledge743", "cHJvbXB0NzQza25vd2xlZGdlNzQz"),
    ("prompt743vector743", "cHJvbXB0NzQzdmVjdG9yNzQz"),
    ("prompt743processor743", "cHJvbXB0NzQzcHJvY2Vzc29yNzQz"),
    ("prompt743reasoning743", "cHJvbXB0NzQzcmVhc29uaW5nNzQz"),
    ("session743reasoning743", "c2Vzc2lvbjc0M3JlYXNvbmluZzc0Mw"),
    ("session743machine743", "c2Vzc2lvbjc0M21hY2hpbmU3NDM"),
    ("session743learning743", "c2Vzc2lvbjc0M2xlYXJuaW5nNzQz"),
    ("session743model743", "c2Vzc2lvbjc0M21vZGVsNzQz"),
    ("library743model743", "bGlicmFyeTc0M21vZGVsNzQz"),
    ("library743token743", "bGlicmFyeTc0M3Rva2VuNzQz"),
    ("library743prompt743", "bGlicmFyeTc0M3Byb21wdDc0Mw"),
    ("library743session743", "bGlicmFyeTc0M3Nlc3Npb243NDM"),
    ("service743session743", "c2VydmljZTc0M3Nlc3Npb243NDM"),
    ("service743library743", "c2VydmljZTc0M2xpYnJhcnk3NDM"),
    ("service743service743", "c2VydmljZTc0M3NlcnZpY2U3NDM"),
    ("service743gateway743", "c2VydmljZTc0M2dhdGV3YXk3NDM"),
    ("gateway743gateway743", "Z2F0ZXdheTc0M2dhdGV3YXk3NDM"),
    ("gateway743storage743", "Z2F0ZXdheTc0M3N0b3JhZ2U3NDM"),
    ("gateway743network743", "Z2F0ZXdheTc0M25ldHdvcms3NDM"),
    ("gateway743latency743", "Z2F0ZXdheTc0M2xhdGVuY3k3NDM"),
    ("storage743latency743", "c3RvcmFnZTc0M2xhdGVuY3k3NDM"),
    ("storage743buffer743", "c3RvcmFnZTc0M2J1ZmZlcjc0Mw"),
    ("storage743queue743", "c3RvcmFnZTc0M3F1ZXVlNzQz"),
    ("storage743worker743", "c3RvcmFnZTc0M3dvcmtlcjc0Mw"),
    ("network743worker743", "bmV0d29yazc0M3dvcmtlcjc0Mw"),
    ("network743kernel743", "bmV0d29yazc0M2tlcm5lbDc0Mw"),
    ("network743signal743", "bmV0d29yazc0M3NpZ25hbDc0Mw"),
    ("network743packet743", "bmV0d29yazc0M3BhY2tldDc0Mw"),
    ("latency743packet743", "bGF0ZW5jeTc0M3BhY2tldDc0Mw"),
    ("latency743router743", "bGF0ZW5jeTc0M3JvdXRlcjc0Mw"),
    ("latency743cluster743", "bGF0ZW5jeTc0M2NsdXN0ZXI3NDM"),
    ("latency743mirror743", "bGF0ZW5jeTc0M21pcnJvcjc0Mw"),
    ("buffer743mirror743", "YnVmZmVyNzQzbWlycm9yNzQz"),
    ("buffer743filter743", "YnVmZmVyNzQzZmlsdGVyNzQz"),
    ("buffer743ranking743", "YnVmZmVyNzQzcmFua2luZzc0Mw"),
    ("buffer743encoding743", "YnVmZmVyNzQzZW5jb2Rpbmc3NDM"),
    ("queue743encoding743", "cXVldWU3NDNlbmNvZGluZzc0Mw"),
    ("queue743mapping743", "cXVldWU3NDNtYXBwaW5nNzQz"),
    ("queue743record743", "cXVldWU3NDNyZWNvcmQ3NDM"),
    ("queue743candle743", "cXVldWU3NDNjYW5kbGU3NDM"),
    ("worker743candle743", "d29ya2VyNzQzY2FuZGxlNzQz"),
    ("worker743thread743", "d29ya2VyNzQzdGhyZWFkNzQz"),
    ("worker743kitten743", "d29ya2VyNzQza2l0dGVuNzQz"),
    ("worker743sitting743", "d29ya2VyNzQzc2l0dGluZzc0Mw"),
    ("kernel743sitting743", "a2VybmVsNzQzc2l0dGluZzc0Mw"),
    ("kernel743agent743", "a2VybmVsNzQzYWdlbnQ3NDM"),
    ("kernel743angle743", "a2VybmVsNzQzYW5nbGU3NDM"),
    ("kernel743universe743", "a2VybmVsNzQzdW5pdmVyc2U3NDM"),
    ("signal743universe743", "c2lnbmFsNzQzdW5pdmVyc2U3NDM"),
    ("signal743memory743", "c2lnbmFsNzQzbWVtb3J5NzQz"),
    ("signal743stream743", "c2lnbmFsNzQzc3RyZWFtNzQz"),
    ("signal743context743", "c2lnbmFsNzQzY29udGV4dDc0Mw"),
    ("packet743context743", "cGFja2V0NzQzY29udGV4dDc0Mw"),
    ("packet743knowledge743", "cGFja2V0NzQza25vd2xlZGdlNzQz"),
    ("packet743vector743", "cGFja2V0NzQzdmVjdG9yNzQz"),
    ("packet743processor743", "cGFja2V0NzQzcHJvY2Vzc29yNzQz"),
    ("router743processor743", "cm91dGVyNzQzcHJvY2Vzc29yNzQz"),
    ("router743reasoning743", "cm91dGVyNzQzcmVhc29uaW5nNzQz"),
    ("router743machine743", "cm91dGVyNzQzbWFjaGluZTc0Mw"),
    ("router743learning743", "cm91dGVyNzQzbGVhcm5pbmc3NDM"),
    ("cluster743learning743", "Y2x1c3Rlcjc0M2xlYXJuaW5nNzQz"),
    ("cluster743model743", "Y2x1c3Rlcjc0M21vZGVsNzQz"),
    ("cluster743token743", "Y2x1c3Rlcjc0M3Rva2VuNzQz"),
    ("cluster743prompt743", "Y2x1c3Rlcjc0M3Byb21wdDc0Mw"),
    ("mirror743prompt743", "bWlycm9yNzQzcHJvbXB0NzQz"),
    ("mirror743session743", "bWlycm9yNzQzc2Vzc2lvbjc0Mw"),
    ("mirror743library743", "bWlycm9yNzQzbGlicmFyeTc0Mw"),
    ("mirror743service743", "bWlycm9yNzQzc2VydmljZTc0Mw"),
    ("filter743service743", "ZmlsdGVyNzQzc2VydmljZTc0Mw"),
    ("filter743gateway743", "ZmlsdGVyNzQzZ2F0ZXdheTc0Mw"),
    ("filter743storage743", "ZmlsdGVyNzQzc3RvcmFnZTc0Mw"),
    ("filter743network743", "ZmlsdGVyNzQzbmV0d29yazc0Mw"),
    ("ranking743network743", "cmFua2luZzc0M25ldHdvcms3NDM"),
    ("ranking743latency743", "cmFua2luZzc0M2xhdGVuY3k3NDM"),
    ("ranking743buffer743", "cmFua2luZzc0M2J1ZmZlcjc0Mw"),
    ("ranking743queue743", "cmFua2luZzc0M3F1ZXVlNzQz"),
    ("encoding743queue743", "ZW5jb2Rpbmc3NDNxdWV1ZTc0Mw"),
    ("encoding743worker743", "ZW5jb2Rpbmc3NDN3b3JrZXI3NDM"),
    ("encoding743kernel743", "ZW5jb2Rpbmc3NDNrZXJuZWw3NDM"),
    ("encoding743signal743", "ZW5jb2Rpbmc3NDNzaWduYWw3NDM"),
    ("mapping743signal743", "bWFwcGluZzc0M3NpZ25hbDc0Mw"),
    ("mapping743packet743", "bWFwcGluZzc0M3BhY2tldDc0Mw"),
    ("mapping743router743", "bWFwcGluZzc0M3JvdXRlcjc0Mw"),
    ("mapping743cluster743", "bWFwcGluZzc0M2NsdXN0ZXI3NDM"),
    ("record743cluster743", "cmVjb3JkNzQzY2x1c3Rlcjc0Mw"),
    ("record743mirror743", "cmVjb3JkNzQzbWlycm9yNzQz"),
    ("record743filter743", "cmVjb3JkNzQzZmlsdGVyNzQz"),
    ("record743ranking743", "cmVjb3JkNzQzcmFua2luZzc0Mw"),
    ("candle743ranking743", "Y2FuZGxlNzQzcmFua2luZzc0Mw"),
    ("candle743encoding743", "Y2FuZGxlNzQzZW5jb2Rpbmc3NDM"),
    ("candle743mapping743", "Y2FuZGxlNzQzbWFwcGluZzc0Mw"),
    ("candle743record743", "Y2FuZGxlNzQzcmVjb3JkNzQz"),
    ("thread743record743", "dGhyZWFkNzQzcmVjb3JkNzQz"),
    ("thread743candle743", "dGhyZWFkNzQzY2FuZGxlNzQz"),
    ("thread743thread743", "dGhyZWFkNzQzdGhyZWFkNzQz"),
    ("thread743kitten743", "dGhyZWFkNzQza2l0dGVuNzQz"),
    (
        "round 743: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzQzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 743: agentuniverse is a framework for multi agents",
        "cm91bmQgNzQzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 743: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzQzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 743: the processor reads the record then stops",
        "cm91bmQgNzQzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 743: a worker pulls the next task from the queue",
        "cm91bmQgNzQzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 743: signals travel through the network layer",
        "cm91bmQgNzQzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 743: the gateway routes each request by policy",
        "cm91bmQgNzQzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 743: memory grows until the buffer is full",
        "cm91bmQgNzQzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 743: the cluster mirrors every packet twice",
        "cm91bmQgNzQzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 743: ranking uses tokens learned from the corpus",
        "cm91bmQgNzQzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 743: a long session ends when the candle dies",
        "cm91bmQgNzQzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 743: encode the prompt then map the result",
        "cm91bmQgNzQzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 743: the kernel wakes the worker at dawn",
        "cm91bmQgNzQzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 743: service latency drops after the patch",
        "cm91bmQgNzQzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 743: the library caches every vector it sees",
        "cm91bmQgNzQzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 743: agents argue then the debate resolves",
        "cm91bmQgNzQzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 743: the filter keeps only strong matches",
        "cm91bmQgNzQzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 743: the model answers with a short reply",
        "cm91bmQgNzQzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 743: the recorder stores the reasoning trace",
        "cm91bmQgNzQzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 743: the angel watches the processor run",
        "cm91bmQgNzQzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 743: angle of the vector decides the match",
        "cm91bmQgNzQzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 743: the candle burns twice as long at night",
        "cm91bmQgNzQzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 743: a mirror of the universe in one line",
        "cm91bmQgNzQzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 743: the queue drains before the storm", "cm91bmQgNzQzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
