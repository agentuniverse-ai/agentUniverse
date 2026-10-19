"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten731kitten731", "a2l0dGVuNzMxa2l0dGVuNzMx"),
    ("kitten731sitting731", "a2l0dGVuNzMxc2l0dGluZzczMQ"),
    ("kitten731agent731", "a2l0dGVuNzMxYWdlbnQ3MzE"),
    ("kitten731angle731", "a2l0dGVuNzMxYW5nbGU3MzE"),
    ("sitting731angle731", "c2l0dGluZzczMWFuZ2xlNzMx"),
    ("sitting731universe731", "c2l0dGluZzczMXVuaXZlcnNlNzMx"),
    ("sitting731memory731", "c2l0dGluZzczMW1lbW9yeTczMQ"),
    ("sitting731stream731", "c2l0dGluZzczMXN0cmVhbTczMQ"),
    ("agent731stream731", "YWdlbnQ3MzFzdHJlYW03MzE"),
    ("agent731context731", "YWdlbnQ3MzFjb250ZXh0NzMx"),
    ("agent731knowledge731", "YWdlbnQ3MzFrbm93bGVkZ2U3MzE"),
    ("agent731vector731", "YWdlbnQ3MzF2ZWN0b3I3MzE"),
    ("angle731vector731", "YW5nbGU3MzF2ZWN0b3I3MzE"),
    ("angle731processor731", "YW5nbGU3MzFwcm9jZXNzb3I3MzE"),
    ("angle731reasoning731", "YW5nbGU3MzFyZWFzb25pbmc3MzE"),
    ("angle731machine731", "YW5nbGU3MzFtYWNoaW5lNzMx"),
    ("universe731machine731", "dW5pdmVyc2U3MzFtYWNoaW5lNzMx"),
    ("universe731learning731", "dW5pdmVyc2U3MzFsZWFybmluZzczMQ"),
    ("universe731model731", "dW5pdmVyc2U3MzFtb2RlbDczMQ"),
    ("universe731token731", "dW5pdmVyc2U3MzF0b2tlbjczMQ"),
    ("memory731token731", "bWVtb3J5NzMxdG9rZW43MzE"),
    ("memory731prompt731", "bWVtb3J5NzMxcHJvbXB0NzMx"),
    ("memory731session731", "bWVtb3J5NzMxc2Vzc2lvbjczMQ"),
    ("memory731library731", "bWVtb3J5NzMxbGlicmFyeTczMQ"),
    ("stream731library731", "c3RyZWFtNzMxbGlicmFyeTczMQ"),
    ("stream731service731", "c3RyZWFtNzMxc2VydmljZTczMQ"),
    ("stream731gateway731", "c3RyZWFtNzMxZ2F0ZXdheTczMQ"),
    ("stream731storage731", "c3RyZWFtNzMxc3RvcmFnZTczMQ"),
    ("context731storage731", "Y29udGV4dDczMXN0b3JhZ2U3MzE"),
    ("context731network731", "Y29udGV4dDczMW5ldHdvcms3MzE"),
    ("context731latency731", "Y29udGV4dDczMWxhdGVuY3k3MzE"),
    ("context731buffer731", "Y29udGV4dDczMWJ1ZmZlcjczMQ"),
    ("knowledge731buffer731", "a25vd2xlZGdlNzMxYnVmZmVyNzMx"),
    ("knowledge731queue731", "a25vd2xlZGdlNzMxcXVldWU3MzE"),
    ("knowledge731worker731", "a25vd2xlZGdlNzMxd29ya2VyNzMx"),
    ("knowledge731kernel731", "a25vd2xlZGdlNzMxa2VybmVsNzMx"),
    ("vector731kernel731", "dmVjdG9yNzMxa2VybmVsNzMx"),
    ("vector731signal731", "dmVjdG9yNzMxc2lnbmFsNzMx"),
    ("vector731packet731", "dmVjdG9yNzMxcGFja2V0NzMx"),
    ("vector731router731", "dmVjdG9yNzMxcm91dGVyNzMx"),
    ("processor731router731", "cHJvY2Vzc29yNzMxcm91dGVyNzMx"),
    ("processor731cluster731", "cHJvY2Vzc29yNzMxY2x1c3RlcjczMQ"),
    ("processor731mirror731", "cHJvY2Vzc29yNzMxbWlycm9yNzMx"),
    ("processor731filter731", "cHJvY2Vzc29yNzMxZmlsdGVyNzMx"),
    ("reasoning731filter731", "cmVhc29uaW5nNzMxZmlsdGVyNzMx"),
    ("reasoning731ranking731", "cmVhc29uaW5nNzMxcmFua2luZzczMQ"),
    ("reasoning731encoding731", "cmVhc29uaW5nNzMxZW5jb2Rpbmc3MzE"),
    ("reasoning731mapping731", "cmVhc29uaW5nNzMxbWFwcGluZzczMQ"),
    ("machine731mapping731", "bWFjaGluZTczMW1hcHBpbmc3MzE"),
    ("machine731record731", "bWFjaGluZTczMXJlY29yZDczMQ"),
    ("machine731candle731", "bWFjaGluZTczMWNhbmRsZTczMQ"),
    ("machine731thread731", "bWFjaGluZTczMXRocmVhZDczMQ"),
    ("learning731thread731", "bGVhcm5pbmc3MzF0aHJlYWQ3MzE"),
    ("learning731kitten731", "bGVhcm5pbmc3MzFraXR0ZW43MzE"),
    ("learning731sitting731", "bGVhcm5pbmc3MzFzaXR0aW5nNzMx"),
    ("learning731agent731", "bGVhcm5pbmc3MzFhZ2VudDczMQ"),
    ("model731agent731", "bW9kZWw3MzFhZ2VudDczMQ"),
    ("model731angle731", "bW9kZWw3MzFhbmdsZTczMQ"),
    ("model731universe731", "bW9kZWw3MzF1bml2ZXJzZTczMQ"),
    ("model731memory731", "bW9kZWw3MzFtZW1vcnk3MzE"),
    ("token731memory731", "dG9rZW43MzFtZW1vcnk3MzE"),
    ("token731stream731", "dG9rZW43MzFzdHJlYW03MzE"),
    ("token731context731", "dG9rZW43MzFjb250ZXh0NzMx"),
    ("token731knowledge731", "dG9rZW43MzFrbm93bGVkZ2U3MzE"),
    ("prompt731knowledge731", "cHJvbXB0NzMxa25vd2xlZGdlNzMx"),
    ("prompt731vector731", "cHJvbXB0NzMxdmVjdG9yNzMx"),
    ("prompt731processor731", "cHJvbXB0NzMxcHJvY2Vzc29yNzMx"),
    ("prompt731reasoning731", "cHJvbXB0NzMxcmVhc29uaW5nNzMx"),
    ("session731reasoning731", "c2Vzc2lvbjczMXJlYXNvbmluZzczMQ"),
    ("session731machine731", "c2Vzc2lvbjczMW1hY2hpbmU3MzE"),
    ("session731learning731", "c2Vzc2lvbjczMWxlYXJuaW5nNzMx"),
    ("session731model731", "c2Vzc2lvbjczMW1vZGVsNzMx"),
    ("library731model731", "bGlicmFyeTczMW1vZGVsNzMx"),
    ("library731token731", "bGlicmFyeTczMXRva2VuNzMx"),
    ("library731prompt731", "bGlicmFyeTczMXByb21wdDczMQ"),
    ("library731session731", "bGlicmFyeTczMXNlc3Npb243MzE"),
    ("service731session731", "c2VydmljZTczMXNlc3Npb243MzE"),
    ("service731library731", "c2VydmljZTczMWxpYnJhcnk3MzE"),
    ("service731service731", "c2VydmljZTczMXNlcnZpY2U3MzE"),
    ("service731gateway731", "c2VydmljZTczMWdhdGV3YXk3MzE"),
    ("gateway731gateway731", "Z2F0ZXdheTczMWdhdGV3YXk3MzE"),
    ("gateway731storage731", "Z2F0ZXdheTczMXN0b3JhZ2U3MzE"),
    ("gateway731network731", "Z2F0ZXdheTczMW5ldHdvcms3MzE"),
    ("gateway731latency731", "Z2F0ZXdheTczMWxhdGVuY3k3MzE"),
    ("storage731latency731", "c3RvcmFnZTczMWxhdGVuY3k3MzE"),
    ("storage731buffer731", "c3RvcmFnZTczMWJ1ZmZlcjczMQ"),
    ("storage731queue731", "c3RvcmFnZTczMXF1ZXVlNzMx"),
    ("storage731worker731", "c3RvcmFnZTczMXdvcmtlcjczMQ"),
    ("network731worker731", "bmV0d29yazczMXdvcmtlcjczMQ"),
    ("network731kernel731", "bmV0d29yazczMWtlcm5lbDczMQ"),
    ("network731signal731", "bmV0d29yazczMXNpZ25hbDczMQ"),
    ("network731packet731", "bmV0d29yazczMXBhY2tldDczMQ"),
    ("latency731packet731", "bGF0ZW5jeTczMXBhY2tldDczMQ"),
    ("latency731router731", "bGF0ZW5jeTczMXJvdXRlcjczMQ"),
    ("latency731cluster731", "bGF0ZW5jeTczMWNsdXN0ZXI3MzE"),
    ("latency731mirror731", "bGF0ZW5jeTczMW1pcnJvcjczMQ"),
    ("buffer731mirror731", "YnVmZmVyNzMxbWlycm9yNzMx"),
    ("buffer731filter731", "YnVmZmVyNzMxZmlsdGVyNzMx"),
    ("buffer731ranking731", "YnVmZmVyNzMxcmFua2luZzczMQ"),
    ("buffer731encoding731", "YnVmZmVyNzMxZW5jb2Rpbmc3MzE"),
    ("queue731encoding731", "cXVldWU3MzFlbmNvZGluZzczMQ"),
    ("queue731mapping731", "cXVldWU3MzFtYXBwaW5nNzMx"),
    ("queue731record731", "cXVldWU3MzFyZWNvcmQ3MzE"),
    ("queue731candle731", "cXVldWU3MzFjYW5kbGU3MzE"),
    ("worker731candle731", "d29ya2VyNzMxY2FuZGxlNzMx"),
    ("worker731thread731", "d29ya2VyNzMxdGhyZWFkNzMx"),
    ("worker731kitten731", "d29ya2VyNzMxa2l0dGVuNzMx"),
    ("worker731sitting731", "d29ya2VyNzMxc2l0dGluZzczMQ"),
    ("kernel731sitting731", "a2VybmVsNzMxc2l0dGluZzczMQ"),
    ("kernel731agent731", "a2VybmVsNzMxYWdlbnQ3MzE"),
    ("kernel731angle731", "a2VybmVsNzMxYW5nbGU3MzE"),
    ("kernel731universe731", "a2VybmVsNzMxdW5pdmVyc2U3MzE"),
    ("signal731universe731", "c2lnbmFsNzMxdW5pdmVyc2U3MzE"),
    ("signal731memory731", "c2lnbmFsNzMxbWVtb3J5NzMx"),
    ("signal731stream731", "c2lnbmFsNzMxc3RyZWFtNzMx"),
    ("signal731context731", "c2lnbmFsNzMxY29udGV4dDczMQ"),
    ("packet731context731", "cGFja2V0NzMxY29udGV4dDczMQ"),
    ("packet731knowledge731", "cGFja2V0NzMxa25vd2xlZGdlNzMx"),
    ("packet731vector731", "cGFja2V0NzMxdmVjdG9yNzMx"),
    ("packet731processor731", "cGFja2V0NzMxcHJvY2Vzc29yNzMx"),
    ("router731processor731", "cm91dGVyNzMxcHJvY2Vzc29yNzMx"),
    ("router731reasoning731", "cm91dGVyNzMxcmVhc29uaW5nNzMx"),
    ("router731machine731", "cm91dGVyNzMxbWFjaGluZTczMQ"),
    ("router731learning731", "cm91dGVyNzMxbGVhcm5pbmc3MzE"),
    ("cluster731learning731", "Y2x1c3RlcjczMWxlYXJuaW5nNzMx"),
    ("cluster731model731", "Y2x1c3RlcjczMW1vZGVsNzMx"),
    ("cluster731token731", "Y2x1c3RlcjczMXRva2VuNzMx"),
    ("cluster731prompt731", "Y2x1c3RlcjczMXByb21wdDczMQ"),
    ("mirror731prompt731", "bWlycm9yNzMxcHJvbXB0NzMx"),
    ("mirror731session731", "bWlycm9yNzMxc2Vzc2lvbjczMQ"),
    ("mirror731library731", "bWlycm9yNzMxbGlicmFyeTczMQ"),
    ("mirror731service731", "bWlycm9yNzMxc2VydmljZTczMQ"),
    ("filter731service731", "ZmlsdGVyNzMxc2VydmljZTczMQ"),
    ("filter731gateway731", "ZmlsdGVyNzMxZ2F0ZXdheTczMQ"),
    ("filter731storage731", "ZmlsdGVyNzMxc3RvcmFnZTczMQ"),
    ("filter731network731", "ZmlsdGVyNzMxbmV0d29yazczMQ"),
    ("ranking731network731", "cmFua2luZzczMW5ldHdvcms3MzE"),
    ("ranking731latency731", "cmFua2luZzczMWxhdGVuY3k3MzE"),
    ("ranking731buffer731", "cmFua2luZzczMWJ1ZmZlcjczMQ"),
    ("ranking731queue731", "cmFua2luZzczMXF1ZXVlNzMx"),
    ("encoding731queue731", "ZW5jb2Rpbmc3MzFxdWV1ZTczMQ"),
    ("encoding731worker731", "ZW5jb2Rpbmc3MzF3b3JrZXI3MzE"),
    ("encoding731kernel731", "ZW5jb2Rpbmc3MzFrZXJuZWw3MzE"),
    ("encoding731signal731", "ZW5jb2Rpbmc3MzFzaWduYWw3MzE"),
    ("mapping731signal731", "bWFwcGluZzczMXNpZ25hbDczMQ"),
    ("mapping731packet731", "bWFwcGluZzczMXBhY2tldDczMQ"),
    ("mapping731router731", "bWFwcGluZzczMXJvdXRlcjczMQ"),
    ("mapping731cluster731", "bWFwcGluZzczMWNsdXN0ZXI3MzE"),
    ("record731cluster731", "cmVjb3JkNzMxY2x1c3RlcjczMQ"),
    ("record731mirror731", "cmVjb3JkNzMxbWlycm9yNzMx"),
    ("record731filter731", "cmVjb3JkNzMxZmlsdGVyNzMx"),
    ("record731ranking731", "cmVjb3JkNzMxcmFua2luZzczMQ"),
    ("candle731ranking731", "Y2FuZGxlNzMxcmFua2luZzczMQ"),
    ("candle731encoding731", "Y2FuZGxlNzMxZW5jb2Rpbmc3MzE"),
    ("candle731mapping731", "Y2FuZGxlNzMxbWFwcGluZzczMQ"),
    ("candle731record731", "Y2FuZGxlNzMxcmVjb3JkNzMx"),
    ("thread731record731", "dGhyZWFkNzMxcmVjb3JkNzMx"),
    ("thread731candle731", "dGhyZWFkNzMxY2FuZGxlNzMx"),
    ("thread731thread731", "dGhyZWFkNzMxdGhyZWFkNzMx"),
    ("thread731kitten731", "dGhyZWFkNzMxa2l0dGVuNzMx"),
    (
        "round 731: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzMxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 731: agentuniverse is a framework for multi agents",
        "cm91bmQgNzMxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 731: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzMxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 731: the processor reads the record then stops",
        "cm91bmQgNzMxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 731: a worker pulls the next task from the queue",
        "cm91bmQgNzMxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 731: signals travel through the network layer",
        "cm91bmQgNzMxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 731: the gateway routes each request by policy",
        "cm91bmQgNzMxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 731: memory grows until the buffer is full",
        "cm91bmQgNzMxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 731: the cluster mirrors every packet twice",
        "cm91bmQgNzMxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 731: ranking uses tokens learned from the corpus",
        "cm91bmQgNzMxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 731: a long session ends when the candle dies",
        "cm91bmQgNzMxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 731: encode the prompt then map the result",
        "cm91bmQgNzMxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 731: the kernel wakes the worker at dawn",
        "cm91bmQgNzMxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 731: service latency drops after the patch",
        "cm91bmQgNzMxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 731: the library caches every vector it sees",
        "cm91bmQgNzMxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 731: agents argue then the debate resolves",
        "cm91bmQgNzMxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 731: the filter keeps only strong matches",
        "cm91bmQgNzMxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 731: the model answers with a short reply",
        "cm91bmQgNzMxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 731: the recorder stores the reasoning trace",
        "cm91bmQgNzMxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 731: the angel watches the processor run",
        "cm91bmQgNzMxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 731: angle of the vector decides the match",
        "cm91bmQgNzMxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 731: the candle burns twice as long at night",
        "cm91bmQgNzMxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 731: a mirror of the universe in one line",
        "cm91bmQgNzMxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 731: the queue drains before the storm", "cm91bmQgNzMxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
