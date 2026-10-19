"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten732kitten732", "a2l0dGVuNzMya2l0dGVuNzMy"),
    ("kitten732sitting732", "a2l0dGVuNzMyc2l0dGluZzczMg"),
    ("kitten732agent732", "a2l0dGVuNzMyYWdlbnQ3MzI"),
    ("kitten732angle732", "a2l0dGVuNzMyYW5nbGU3MzI"),
    ("sitting732angle732", "c2l0dGluZzczMmFuZ2xlNzMy"),
    ("sitting732universe732", "c2l0dGluZzczMnVuaXZlcnNlNzMy"),
    ("sitting732memory732", "c2l0dGluZzczMm1lbW9yeTczMg"),
    ("sitting732stream732", "c2l0dGluZzczMnN0cmVhbTczMg"),
    ("agent732stream732", "YWdlbnQ3MzJzdHJlYW03MzI"),
    ("agent732context732", "YWdlbnQ3MzJjb250ZXh0NzMy"),
    ("agent732knowledge732", "YWdlbnQ3MzJrbm93bGVkZ2U3MzI"),
    ("agent732vector732", "YWdlbnQ3MzJ2ZWN0b3I3MzI"),
    ("angle732vector732", "YW5nbGU3MzJ2ZWN0b3I3MzI"),
    ("angle732processor732", "YW5nbGU3MzJwcm9jZXNzb3I3MzI"),
    ("angle732reasoning732", "YW5nbGU3MzJyZWFzb25pbmc3MzI"),
    ("angle732machine732", "YW5nbGU3MzJtYWNoaW5lNzMy"),
    ("universe732machine732", "dW5pdmVyc2U3MzJtYWNoaW5lNzMy"),
    ("universe732learning732", "dW5pdmVyc2U3MzJsZWFybmluZzczMg"),
    ("universe732model732", "dW5pdmVyc2U3MzJtb2RlbDczMg"),
    ("universe732token732", "dW5pdmVyc2U3MzJ0b2tlbjczMg"),
    ("memory732token732", "bWVtb3J5NzMydG9rZW43MzI"),
    ("memory732prompt732", "bWVtb3J5NzMycHJvbXB0NzMy"),
    ("memory732session732", "bWVtb3J5NzMyc2Vzc2lvbjczMg"),
    ("memory732library732", "bWVtb3J5NzMybGlicmFyeTczMg"),
    ("stream732library732", "c3RyZWFtNzMybGlicmFyeTczMg"),
    ("stream732service732", "c3RyZWFtNzMyc2VydmljZTczMg"),
    ("stream732gateway732", "c3RyZWFtNzMyZ2F0ZXdheTczMg"),
    ("stream732storage732", "c3RyZWFtNzMyc3RvcmFnZTczMg"),
    ("context732storage732", "Y29udGV4dDczMnN0b3JhZ2U3MzI"),
    ("context732network732", "Y29udGV4dDczMm5ldHdvcms3MzI"),
    ("context732latency732", "Y29udGV4dDczMmxhdGVuY3k3MzI"),
    ("context732buffer732", "Y29udGV4dDczMmJ1ZmZlcjczMg"),
    ("knowledge732buffer732", "a25vd2xlZGdlNzMyYnVmZmVyNzMy"),
    ("knowledge732queue732", "a25vd2xlZGdlNzMycXVldWU3MzI"),
    ("knowledge732worker732", "a25vd2xlZGdlNzMyd29ya2VyNzMy"),
    ("knowledge732kernel732", "a25vd2xlZGdlNzMya2VybmVsNzMy"),
    ("vector732kernel732", "dmVjdG9yNzMya2VybmVsNzMy"),
    ("vector732signal732", "dmVjdG9yNzMyc2lnbmFsNzMy"),
    ("vector732packet732", "dmVjdG9yNzMycGFja2V0NzMy"),
    ("vector732router732", "dmVjdG9yNzMycm91dGVyNzMy"),
    ("processor732router732", "cHJvY2Vzc29yNzMycm91dGVyNzMy"),
    ("processor732cluster732", "cHJvY2Vzc29yNzMyY2x1c3RlcjczMg"),
    ("processor732mirror732", "cHJvY2Vzc29yNzMybWlycm9yNzMy"),
    ("processor732filter732", "cHJvY2Vzc29yNzMyZmlsdGVyNzMy"),
    ("reasoning732filter732", "cmVhc29uaW5nNzMyZmlsdGVyNzMy"),
    ("reasoning732ranking732", "cmVhc29uaW5nNzMycmFua2luZzczMg"),
    ("reasoning732encoding732", "cmVhc29uaW5nNzMyZW5jb2Rpbmc3MzI"),
    ("reasoning732mapping732", "cmVhc29uaW5nNzMybWFwcGluZzczMg"),
    ("machine732mapping732", "bWFjaGluZTczMm1hcHBpbmc3MzI"),
    ("machine732record732", "bWFjaGluZTczMnJlY29yZDczMg"),
    ("machine732candle732", "bWFjaGluZTczMmNhbmRsZTczMg"),
    ("machine732thread732", "bWFjaGluZTczMnRocmVhZDczMg"),
    ("learning732thread732", "bGVhcm5pbmc3MzJ0aHJlYWQ3MzI"),
    ("learning732kitten732", "bGVhcm5pbmc3MzJraXR0ZW43MzI"),
    ("learning732sitting732", "bGVhcm5pbmc3MzJzaXR0aW5nNzMy"),
    ("learning732agent732", "bGVhcm5pbmc3MzJhZ2VudDczMg"),
    ("model732agent732", "bW9kZWw3MzJhZ2VudDczMg"),
    ("model732angle732", "bW9kZWw3MzJhbmdsZTczMg"),
    ("model732universe732", "bW9kZWw3MzJ1bml2ZXJzZTczMg"),
    ("model732memory732", "bW9kZWw3MzJtZW1vcnk3MzI"),
    ("token732memory732", "dG9rZW43MzJtZW1vcnk3MzI"),
    ("token732stream732", "dG9rZW43MzJzdHJlYW03MzI"),
    ("token732context732", "dG9rZW43MzJjb250ZXh0NzMy"),
    ("token732knowledge732", "dG9rZW43MzJrbm93bGVkZ2U3MzI"),
    ("prompt732knowledge732", "cHJvbXB0NzMya25vd2xlZGdlNzMy"),
    ("prompt732vector732", "cHJvbXB0NzMydmVjdG9yNzMy"),
    ("prompt732processor732", "cHJvbXB0NzMycHJvY2Vzc29yNzMy"),
    ("prompt732reasoning732", "cHJvbXB0NzMycmVhc29uaW5nNzMy"),
    ("session732reasoning732", "c2Vzc2lvbjczMnJlYXNvbmluZzczMg"),
    ("session732machine732", "c2Vzc2lvbjczMm1hY2hpbmU3MzI"),
    ("session732learning732", "c2Vzc2lvbjczMmxlYXJuaW5nNzMy"),
    ("session732model732", "c2Vzc2lvbjczMm1vZGVsNzMy"),
    ("library732model732", "bGlicmFyeTczMm1vZGVsNzMy"),
    ("library732token732", "bGlicmFyeTczMnRva2VuNzMy"),
    ("library732prompt732", "bGlicmFyeTczMnByb21wdDczMg"),
    ("library732session732", "bGlicmFyeTczMnNlc3Npb243MzI"),
    ("service732session732", "c2VydmljZTczMnNlc3Npb243MzI"),
    ("service732library732", "c2VydmljZTczMmxpYnJhcnk3MzI"),
    ("service732service732", "c2VydmljZTczMnNlcnZpY2U3MzI"),
    ("service732gateway732", "c2VydmljZTczMmdhdGV3YXk3MzI"),
    ("gateway732gateway732", "Z2F0ZXdheTczMmdhdGV3YXk3MzI"),
    ("gateway732storage732", "Z2F0ZXdheTczMnN0b3JhZ2U3MzI"),
    ("gateway732network732", "Z2F0ZXdheTczMm5ldHdvcms3MzI"),
    ("gateway732latency732", "Z2F0ZXdheTczMmxhdGVuY3k3MzI"),
    ("storage732latency732", "c3RvcmFnZTczMmxhdGVuY3k3MzI"),
    ("storage732buffer732", "c3RvcmFnZTczMmJ1ZmZlcjczMg"),
    ("storage732queue732", "c3RvcmFnZTczMnF1ZXVlNzMy"),
    ("storage732worker732", "c3RvcmFnZTczMndvcmtlcjczMg"),
    ("network732worker732", "bmV0d29yazczMndvcmtlcjczMg"),
    ("network732kernel732", "bmV0d29yazczMmtlcm5lbDczMg"),
    ("network732signal732", "bmV0d29yazczMnNpZ25hbDczMg"),
    ("network732packet732", "bmV0d29yazczMnBhY2tldDczMg"),
    ("latency732packet732", "bGF0ZW5jeTczMnBhY2tldDczMg"),
    ("latency732router732", "bGF0ZW5jeTczMnJvdXRlcjczMg"),
    ("latency732cluster732", "bGF0ZW5jeTczMmNsdXN0ZXI3MzI"),
    ("latency732mirror732", "bGF0ZW5jeTczMm1pcnJvcjczMg"),
    ("buffer732mirror732", "YnVmZmVyNzMybWlycm9yNzMy"),
    ("buffer732filter732", "YnVmZmVyNzMyZmlsdGVyNzMy"),
    ("buffer732ranking732", "YnVmZmVyNzMycmFua2luZzczMg"),
    ("buffer732encoding732", "YnVmZmVyNzMyZW5jb2Rpbmc3MzI"),
    ("queue732encoding732", "cXVldWU3MzJlbmNvZGluZzczMg"),
    ("queue732mapping732", "cXVldWU3MzJtYXBwaW5nNzMy"),
    ("queue732record732", "cXVldWU3MzJyZWNvcmQ3MzI"),
    ("queue732candle732", "cXVldWU3MzJjYW5kbGU3MzI"),
    ("worker732candle732", "d29ya2VyNzMyY2FuZGxlNzMy"),
    ("worker732thread732", "d29ya2VyNzMydGhyZWFkNzMy"),
    ("worker732kitten732", "d29ya2VyNzMya2l0dGVuNzMy"),
    ("worker732sitting732", "d29ya2VyNzMyc2l0dGluZzczMg"),
    ("kernel732sitting732", "a2VybmVsNzMyc2l0dGluZzczMg"),
    ("kernel732agent732", "a2VybmVsNzMyYWdlbnQ3MzI"),
    ("kernel732angle732", "a2VybmVsNzMyYW5nbGU3MzI"),
    ("kernel732universe732", "a2VybmVsNzMydW5pdmVyc2U3MzI"),
    ("signal732universe732", "c2lnbmFsNzMydW5pdmVyc2U3MzI"),
    ("signal732memory732", "c2lnbmFsNzMybWVtb3J5NzMy"),
    ("signal732stream732", "c2lnbmFsNzMyc3RyZWFtNzMy"),
    ("signal732context732", "c2lnbmFsNzMyY29udGV4dDczMg"),
    ("packet732context732", "cGFja2V0NzMyY29udGV4dDczMg"),
    ("packet732knowledge732", "cGFja2V0NzMya25vd2xlZGdlNzMy"),
    ("packet732vector732", "cGFja2V0NzMydmVjdG9yNzMy"),
    ("packet732processor732", "cGFja2V0NzMycHJvY2Vzc29yNzMy"),
    ("router732processor732", "cm91dGVyNzMycHJvY2Vzc29yNzMy"),
    ("router732reasoning732", "cm91dGVyNzMycmVhc29uaW5nNzMy"),
    ("router732machine732", "cm91dGVyNzMybWFjaGluZTczMg"),
    ("router732learning732", "cm91dGVyNzMybGVhcm5pbmc3MzI"),
    ("cluster732learning732", "Y2x1c3RlcjczMmxlYXJuaW5nNzMy"),
    ("cluster732model732", "Y2x1c3RlcjczMm1vZGVsNzMy"),
    ("cluster732token732", "Y2x1c3RlcjczMnRva2VuNzMy"),
    ("cluster732prompt732", "Y2x1c3RlcjczMnByb21wdDczMg"),
    ("mirror732prompt732", "bWlycm9yNzMycHJvbXB0NzMy"),
    ("mirror732session732", "bWlycm9yNzMyc2Vzc2lvbjczMg"),
    ("mirror732library732", "bWlycm9yNzMybGlicmFyeTczMg"),
    ("mirror732service732", "bWlycm9yNzMyc2VydmljZTczMg"),
    ("filter732service732", "ZmlsdGVyNzMyc2VydmljZTczMg"),
    ("filter732gateway732", "ZmlsdGVyNzMyZ2F0ZXdheTczMg"),
    ("filter732storage732", "ZmlsdGVyNzMyc3RvcmFnZTczMg"),
    ("filter732network732", "ZmlsdGVyNzMybmV0d29yazczMg"),
    ("ranking732network732", "cmFua2luZzczMm5ldHdvcms3MzI"),
    ("ranking732latency732", "cmFua2luZzczMmxhdGVuY3k3MzI"),
    ("ranking732buffer732", "cmFua2luZzczMmJ1ZmZlcjczMg"),
    ("ranking732queue732", "cmFua2luZzczMnF1ZXVlNzMy"),
    ("encoding732queue732", "ZW5jb2Rpbmc3MzJxdWV1ZTczMg"),
    ("encoding732worker732", "ZW5jb2Rpbmc3MzJ3b3JrZXI3MzI"),
    ("encoding732kernel732", "ZW5jb2Rpbmc3MzJrZXJuZWw3MzI"),
    ("encoding732signal732", "ZW5jb2Rpbmc3MzJzaWduYWw3MzI"),
    ("mapping732signal732", "bWFwcGluZzczMnNpZ25hbDczMg"),
    ("mapping732packet732", "bWFwcGluZzczMnBhY2tldDczMg"),
    ("mapping732router732", "bWFwcGluZzczMnJvdXRlcjczMg"),
    ("mapping732cluster732", "bWFwcGluZzczMmNsdXN0ZXI3MzI"),
    ("record732cluster732", "cmVjb3JkNzMyY2x1c3RlcjczMg"),
    ("record732mirror732", "cmVjb3JkNzMybWlycm9yNzMy"),
    ("record732filter732", "cmVjb3JkNzMyZmlsdGVyNzMy"),
    ("record732ranking732", "cmVjb3JkNzMycmFua2luZzczMg"),
    ("candle732ranking732", "Y2FuZGxlNzMycmFua2luZzczMg"),
    ("candle732encoding732", "Y2FuZGxlNzMyZW5jb2Rpbmc3MzI"),
    ("candle732mapping732", "Y2FuZGxlNzMybWFwcGluZzczMg"),
    ("candle732record732", "Y2FuZGxlNzMycmVjb3JkNzMy"),
    ("thread732record732", "dGhyZWFkNzMycmVjb3JkNzMy"),
    ("thread732candle732", "dGhyZWFkNzMyY2FuZGxlNzMy"),
    ("thread732thread732", "dGhyZWFkNzMydGhyZWFkNzMy"),
    ("thread732kitten732", "dGhyZWFkNzMya2l0dGVuNzMy"),
    (
        "round 732: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzMyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 732: agentuniverse is a framework for multi agents",
        "cm91bmQgNzMyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 732: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzMyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 732: the processor reads the record then stops",
        "cm91bmQgNzMyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 732: a worker pulls the next task from the queue",
        "cm91bmQgNzMyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 732: signals travel through the network layer",
        "cm91bmQgNzMyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 732: the gateway routes each request by policy",
        "cm91bmQgNzMyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 732: memory grows until the buffer is full",
        "cm91bmQgNzMyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 732: the cluster mirrors every packet twice",
        "cm91bmQgNzMyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 732: ranking uses tokens learned from the corpus",
        "cm91bmQgNzMyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 732: a long session ends when the candle dies",
        "cm91bmQgNzMyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 732: encode the prompt then map the result",
        "cm91bmQgNzMyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 732: the kernel wakes the worker at dawn",
        "cm91bmQgNzMyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 732: service latency drops after the patch",
        "cm91bmQgNzMyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 732: the library caches every vector it sees",
        "cm91bmQgNzMyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 732: agents argue then the debate resolves",
        "cm91bmQgNzMyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 732: the filter keeps only strong matches",
        "cm91bmQgNzMyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 732: the model answers with a short reply",
        "cm91bmQgNzMyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 732: the recorder stores the reasoning trace",
        "cm91bmQgNzMyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 732: the angel watches the processor run",
        "cm91bmQgNzMyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 732: angle of the vector decides the match",
        "cm91bmQgNzMyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 732: the candle burns twice as long at night",
        "cm91bmQgNzMyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 732: a mirror of the universe in one line",
        "cm91bmQgNzMyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 732: the queue drains before the storm", "cm91bmQgNzMyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
