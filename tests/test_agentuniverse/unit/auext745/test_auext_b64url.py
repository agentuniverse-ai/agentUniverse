"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten745kitten745", "a2l0dGVuNzQ1a2l0dGVuNzQ1"),
    ("kitten745sitting745", "a2l0dGVuNzQ1c2l0dGluZzc0NQ"),
    ("kitten745agent745", "a2l0dGVuNzQ1YWdlbnQ3NDU"),
    ("kitten745angle745", "a2l0dGVuNzQ1YW5nbGU3NDU"),
    ("sitting745angle745", "c2l0dGluZzc0NWFuZ2xlNzQ1"),
    ("sitting745universe745", "c2l0dGluZzc0NXVuaXZlcnNlNzQ1"),
    ("sitting745memory745", "c2l0dGluZzc0NW1lbW9yeTc0NQ"),
    ("sitting745stream745", "c2l0dGluZzc0NXN0cmVhbTc0NQ"),
    ("agent745stream745", "YWdlbnQ3NDVzdHJlYW03NDU"),
    ("agent745context745", "YWdlbnQ3NDVjb250ZXh0NzQ1"),
    ("agent745knowledge745", "YWdlbnQ3NDVrbm93bGVkZ2U3NDU"),
    ("agent745vector745", "YWdlbnQ3NDV2ZWN0b3I3NDU"),
    ("angle745vector745", "YW5nbGU3NDV2ZWN0b3I3NDU"),
    ("angle745processor745", "YW5nbGU3NDVwcm9jZXNzb3I3NDU"),
    ("angle745reasoning745", "YW5nbGU3NDVyZWFzb25pbmc3NDU"),
    ("angle745machine745", "YW5nbGU3NDVtYWNoaW5lNzQ1"),
    ("universe745machine745", "dW5pdmVyc2U3NDVtYWNoaW5lNzQ1"),
    ("universe745learning745", "dW5pdmVyc2U3NDVsZWFybmluZzc0NQ"),
    ("universe745model745", "dW5pdmVyc2U3NDVtb2RlbDc0NQ"),
    ("universe745token745", "dW5pdmVyc2U3NDV0b2tlbjc0NQ"),
    ("memory745token745", "bWVtb3J5NzQ1dG9rZW43NDU"),
    ("memory745prompt745", "bWVtb3J5NzQ1cHJvbXB0NzQ1"),
    ("memory745session745", "bWVtb3J5NzQ1c2Vzc2lvbjc0NQ"),
    ("memory745library745", "bWVtb3J5NzQ1bGlicmFyeTc0NQ"),
    ("stream745library745", "c3RyZWFtNzQ1bGlicmFyeTc0NQ"),
    ("stream745service745", "c3RyZWFtNzQ1c2VydmljZTc0NQ"),
    ("stream745gateway745", "c3RyZWFtNzQ1Z2F0ZXdheTc0NQ"),
    ("stream745storage745", "c3RyZWFtNzQ1c3RvcmFnZTc0NQ"),
    ("context745storage745", "Y29udGV4dDc0NXN0b3JhZ2U3NDU"),
    ("context745network745", "Y29udGV4dDc0NW5ldHdvcms3NDU"),
    ("context745latency745", "Y29udGV4dDc0NWxhdGVuY3k3NDU"),
    ("context745buffer745", "Y29udGV4dDc0NWJ1ZmZlcjc0NQ"),
    ("knowledge745buffer745", "a25vd2xlZGdlNzQ1YnVmZmVyNzQ1"),
    ("knowledge745queue745", "a25vd2xlZGdlNzQ1cXVldWU3NDU"),
    ("knowledge745worker745", "a25vd2xlZGdlNzQ1d29ya2VyNzQ1"),
    ("knowledge745kernel745", "a25vd2xlZGdlNzQ1a2VybmVsNzQ1"),
    ("vector745kernel745", "dmVjdG9yNzQ1a2VybmVsNzQ1"),
    ("vector745signal745", "dmVjdG9yNzQ1c2lnbmFsNzQ1"),
    ("vector745packet745", "dmVjdG9yNzQ1cGFja2V0NzQ1"),
    ("vector745router745", "dmVjdG9yNzQ1cm91dGVyNzQ1"),
    ("processor745router745", "cHJvY2Vzc29yNzQ1cm91dGVyNzQ1"),
    ("processor745cluster745", "cHJvY2Vzc29yNzQ1Y2x1c3Rlcjc0NQ"),
    ("processor745mirror745", "cHJvY2Vzc29yNzQ1bWlycm9yNzQ1"),
    ("processor745filter745", "cHJvY2Vzc29yNzQ1ZmlsdGVyNzQ1"),
    ("reasoning745filter745", "cmVhc29uaW5nNzQ1ZmlsdGVyNzQ1"),
    ("reasoning745ranking745", "cmVhc29uaW5nNzQ1cmFua2luZzc0NQ"),
    ("reasoning745encoding745", "cmVhc29uaW5nNzQ1ZW5jb2Rpbmc3NDU"),
    ("reasoning745mapping745", "cmVhc29uaW5nNzQ1bWFwcGluZzc0NQ"),
    ("machine745mapping745", "bWFjaGluZTc0NW1hcHBpbmc3NDU"),
    ("machine745record745", "bWFjaGluZTc0NXJlY29yZDc0NQ"),
    ("machine745candle745", "bWFjaGluZTc0NWNhbmRsZTc0NQ"),
    ("machine745thread745", "bWFjaGluZTc0NXRocmVhZDc0NQ"),
    ("learning745thread745", "bGVhcm5pbmc3NDV0aHJlYWQ3NDU"),
    ("learning745kitten745", "bGVhcm5pbmc3NDVraXR0ZW43NDU"),
    ("learning745sitting745", "bGVhcm5pbmc3NDVzaXR0aW5nNzQ1"),
    ("learning745agent745", "bGVhcm5pbmc3NDVhZ2VudDc0NQ"),
    ("model745agent745", "bW9kZWw3NDVhZ2VudDc0NQ"),
    ("model745angle745", "bW9kZWw3NDVhbmdsZTc0NQ"),
    ("model745universe745", "bW9kZWw3NDV1bml2ZXJzZTc0NQ"),
    ("model745memory745", "bW9kZWw3NDVtZW1vcnk3NDU"),
    ("token745memory745", "dG9rZW43NDVtZW1vcnk3NDU"),
    ("token745stream745", "dG9rZW43NDVzdHJlYW03NDU"),
    ("token745context745", "dG9rZW43NDVjb250ZXh0NzQ1"),
    ("token745knowledge745", "dG9rZW43NDVrbm93bGVkZ2U3NDU"),
    ("prompt745knowledge745", "cHJvbXB0NzQ1a25vd2xlZGdlNzQ1"),
    ("prompt745vector745", "cHJvbXB0NzQ1dmVjdG9yNzQ1"),
    ("prompt745processor745", "cHJvbXB0NzQ1cHJvY2Vzc29yNzQ1"),
    ("prompt745reasoning745", "cHJvbXB0NzQ1cmVhc29uaW5nNzQ1"),
    ("session745reasoning745", "c2Vzc2lvbjc0NXJlYXNvbmluZzc0NQ"),
    ("session745machine745", "c2Vzc2lvbjc0NW1hY2hpbmU3NDU"),
    ("session745learning745", "c2Vzc2lvbjc0NWxlYXJuaW5nNzQ1"),
    ("session745model745", "c2Vzc2lvbjc0NW1vZGVsNzQ1"),
    ("library745model745", "bGlicmFyeTc0NW1vZGVsNzQ1"),
    ("library745token745", "bGlicmFyeTc0NXRva2VuNzQ1"),
    ("library745prompt745", "bGlicmFyeTc0NXByb21wdDc0NQ"),
    ("library745session745", "bGlicmFyeTc0NXNlc3Npb243NDU"),
    ("service745session745", "c2VydmljZTc0NXNlc3Npb243NDU"),
    ("service745library745", "c2VydmljZTc0NWxpYnJhcnk3NDU"),
    ("service745service745", "c2VydmljZTc0NXNlcnZpY2U3NDU"),
    ("service745gateway745", "c2VydmljZTc0NWdhdGV3YXk3NDU"),
    ("gateway745gateway745", "Z2F0ZXdheTc0NWdhdGV3YXk3NDU"),
    ("gateway745storage745", "Z2F0ZXdheTc0NXN0b3JhZ2U3NDU"),
    ("gateway745network745", "Z2F0ZXdheTc0NW5ldHdvcms3NDU"),
    ("gateway745latency745", "Z2F0ZXdheTc0NWxhdGVuY3k3NDU"),
    ("storage745latency745", "c3RvcmFnZTc0NWxhdGVuY3k3NDU"),
    ("storage745buffer745", "c3RvcmFnZTc0NWJ1ZmZlcjc0NQ"),
    ("storage745queue745", "c3RvcmFnZTc0NXF1ZXVlNzQ1"),
    ("storage745worker745", "c3RvcmFnZTc0NXdvcmtlcjc0NQ"),
    ("network745worker745", "bmV0d29yazc0NXdvcmtlcjc0NQ"),
    ("network745kernel745", "bmV0d29yazc0NWtlcm5lbDc0NQ"),
    ("network745signal745", "bmV0d29yazc0NXNpZ25hbDc0NQ"),
    ("network745packet745", "bmV0d29yazc0NXBhY2tldDc0NQ"),
    ("latency745packet745", "bGF0ZW5jeTc0NXBhY2tldDc0NQ"),
    ("latency745router745", "bGF0ZW5jeTc0NXJvdXRlcjc0NQ"),
    ("latency745cluster745", "bGF0ZW5jeTc0NWNsdXN0ZXI3NDU"),
    ("latency745mirror745", "bGF0ZW5jeTc0NW1pcnJvcjc0NQ"),
    ("buffer745mirror745", "YnVmZmVyNzQ1bWlycm9yNzQ1"),
    ("buffer745filter745", "YnVmZmVyNzQ1ZmlsdGVyNzQ1"),
    ("buffer745ranking745", "YnVmZmVyNzQ1cmFua2luZzc0NQ"),
    ("buffer745encoding745", "YnVmZmVyNzQ1ZW5jb2Rpbmc3NDU"),
    ("queue745encoding745", "cXVldWU3NDVlbmNvZGluZzc0NQ"),
    ("queue745mapping745", "cXVldWU3NDVtYXBwaW5nNzQ1"),
    ("queue745record745", "cXVldWU3NDVyZWNvcmQ3NDU"),
    ("queue745candle745", "cXVldWU3NDVjYW5kbGU3NDU"),
    ("worker745candle745", "d29ya2VyNzQ1Y2FuZGxlNzQ1"),
    ("worker745thread745", "d29ya2VyNzQ1dGhyZWFkNzQ1"),
    ("worker745kitten745", "d29ya2VyNzQ1a2l0dGVuNzQ1"),
    ("worker745sitting745", "d29ya2VyNzQ1c2l0dGluZzc0NQ"),
    ("kernel745sitting745", "a2VybmVsNzQ1c2l0dGluZzc0NQ"),
    ("kernel745agent745", "a2VybmVsNzQ1YWdlbnQ3NDU"),
    ("kernel745angle745", "a2VybmVsNzQ1YW5nbGU3NDU"),
    ("kernel745universe745", "a2VybmVsNzQ1dW5pdmVyc2U3NDU"),
    ("signal745universe745", "c2lnbmFsNzQ1dW5pdmVyc2U3NDU"),
    ("signal745memory745", "c2lnbmFsNzQ1bWVtb3J5NzQ1"),
    ("signal745stream745", "c2lnbmFsNzQ1c3RyZWFtNzQ1"),
    ("signal745context745", "c2lnbmFsNzQ1Y29udGV4dDc0NQ"),
    ("packet745context745", "cGFja2V0NzQ1Y29udGV4dDc0NQ"),
    ("packet745knowledge745", "cGFja2V0NzQ1a25vd2xlZGdlNzQ1"),
    ("packet745vector745", "cGFja2V0NzQ1dmVjdG9yNzQ1"),
    ("packet745processor745", "cGFja2V0NzQ1cHJvY2Vzc29yNzQ1"),
    ("router745processor745", "cm91dGVyNzQ1cHJvY2Vzc29yNzQ1"),
    ("router745reasoning745", "cm91dGVyNzQ1cmVhc29uaW5nNzQ1"),
    ("router745machine745", "cm91dGVyNzQ1bWFjaGluZTc0NQ"),
    ("router745learning745", "cm91dGVyNzQ1bGVhcm5pbmc3NDU"),
    ("cluster745learning745", "Y2x1c3Rlcjc0NWxlYXJuaW5nNzQ1"),
    ("cluster745model745", "Y2x1c3Rlcjc0NW1vZGVsNzQ1"),
    ("cluster745token745", "Y2x1c3Rlcjc0NXRva2VuNzQ1"),
    ("cluster745prompt745", "Y2x1c3Rlcjc0NXByb21wdDc0NQ"),
    ("mirror745prompt745", "bWlycm9yNzQ1cHJvbXB0NzQ1"),
    ("mirror745session745", "bWlycm9yNzQ1c2Vzc2lvbjc0NQ"),
    ("mirror745library745", "bWlycm9yNzQ1bGlicmFyeTc0NQ"),
    ("mirror745service745", "bWlycm9yNzQ1c2VydmljZTc0NQ"),
    ("filter745service745", "ZmlsdGVyNzQ1c2VydmljZTc0NQ"),
    ("filter745gateway745", "ZmlsdGVyNzQ1Z2F0ZXdheTc0NQ"),
    ("filter745storage745", "ZmlsdGVyNzQ1c3RvcmFnZTc0NQ"),
    ("filter745network745", "ZmlsdGVyNzQ1bmV0d29yazc0NQ"),
    ("ranking745network745", "cmFua2luZzc0NW5ldHdvcms3NDU"),
    ("ranking745latency745", "cmFua2luZzc0NWxhdGVuY3k3NDU"),
    ("ranking745buffer745", "cmFua2luZzc0NWJ1ZmZlcjc0NQ"),
    ("ranking745queue745", "cmFua2luZzc0NXF1ZXVlNzQ1"),
    ("encoding745queue745", "ZW5jb2Rpbmc3NDVxdWV1ZTc0NQ"),
    ("encoding745worker745", "ZW5jb2Rpbmc3NDV3b3JrZXI3NDU"),
    ("encoding745kernel745", "ZW5jb2Rpbmc3NDVrZXJuZWw3NDU"),
    ("encoding745signal745", "ZW5jb2Rpbmc3NDVzaWduYWw3NDU"),
    ("mapping745signal745", "bWFwcGluZzc0NXNpZ25hbDc0NQ"),
    ("mapping745packet745", "bWFwcGluZzc0NXBhY2tldDc0NQ"),
    ("mapping745router745", "bWFwcGluZzc0NXJvdXRlcjc0NQ"),
    ("mapping745cluster745", "bWFwcGluZzc0NWNsdXN0ZXI3NDU"),
    ("record745cluster745", "cmVjb3JkNzQ1Y2x1c3Rlcjc0NQ"),
    ("record745mirror745", "cmVjb3JkNzQ1bWlycm9yNzQ1"),
    ("record745filter745", "cmVjb3JkNzQ1ZmlsdGVyNzQ1"),
    ("record745ranking745", "cmVjb3JkNzQ1cmFua2luZzc0NQ"),
    ("candle745ranking745", "Y2FuZGxlNzQ1cmFua2luZzc0NQ"),
    ("candle745encoding745", "Y2FuZGxlNzQ1ZW5jb2Rpbmc3NDU"),
    ("candle745mapping745", "Y2FuZGxlNzQ1bWFwcGluZzc0NQ"),
    ("candle745record745", "Y2FuZGxlNzQ1cmVjb3JkNzQ1"),
    ("thread745record745", "dGhyZWFkNzQ1cmVjb3JkNzQ1"),
    ("thread745candle745", "dGhyZWFkNzQ1Y2FuZGxlNzQ1"),
    ("thread745thread745", "dGhyZWFkNzQ1dGhyZWFkNzQ1"),
    ("thread745kitten745", "dGhyZWFkNzQ1a2l0dGVuNzQ1"),
    (
        "round 745: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzQ1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 745: agentuniverse is a framework for multi agents",
        "cm91bmQgNzQ1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 745: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzQ1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 745: the processor reads the record then stops",
        "cm91bmQgNzQ1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 745: a worker pulls the next task from the queue",
        "cm91bmQgNzQ1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 745: signals travel through the network layer",
        "cm91bmQgNzQ1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 745: the gateway routes each request by policy",
        "cm91bmQgNzQ1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 745: memory grows until the buffer is full",
        "cm91bmQgNzQ1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 745: the cluster mirrors every packet twice",
        "cm91bmQgNzQ1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 745: ranking uses tokens learned from the corpus",
        "cm91bmQgNzQ1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 745: a long session ends when the candle dies",
        "cm91bmQgNzQ1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 745: encode the prompt then map the result",
        "cm91bmQgNzQ1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 745: the kernel wakes the worker at dawn",
        "cm91bmQgNzQ1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 745: service latency drops after the patch",
        "cm91bmQgNzQ1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 745: the library caches every vector it sees",
        "cm91bmQgNzQ1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 745: agents argue then the debate resolves",
        "cm91bmQgNzQ1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 745: the filter keeps only strong matches",
        "cm91bmQgNzQ1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 745: the model answers with a short reply",
        "cm91bmQgNzQ1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 745: the recorder stores the reasoning trace",
        "cm91bmQgNzQ1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 745: the angel watches the processor run",
        "cm91bmQgNzQ1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 745: angle of the vector decides the match",
        "cm91bmQgNzQ1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 745: the candle burns twice as long at night",
        "cm91bmQgNzQ1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 745: a mirror of the universe in one line",
        "cm91bmQgNzQ1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 745: the queue drains before the storm", "cm91bmQgNzQ1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
