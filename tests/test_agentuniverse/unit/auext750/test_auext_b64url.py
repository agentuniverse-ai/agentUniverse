"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten750kitten750", "a2l0dGVuNzUwa2l0dGVuNzUw"),
    ("kitten750sitting750", "a2l0dGVuNzUwc2l0dGluZzc1MA"),
    ("kitten750agent750", "a2l0dGVuNzUwYWdlbnQ3NTA"),
    ("kitten750angle750", "a2l0dGVuNzUwYW5nbGU3NTA"),
    ("sitting750angle750", "c2l0dGluZzc1MGFuZ2xlNzUw"),
    ("sitting750universe750", "c2l0dGluZzc1MHVuaXZlcnNlNzUw"),
    ("sitting750memory750", "c2l0dGluZzc1MG1lbW9yeTc1MA"),
    ("sitting750stream750", "c2l0dGluZzc1MHN0cmVhbTc1MA"),
    ("agent750stream750", "YWdlbnQ3NTBzdHJlYW03NTA"),
    ("agent750context750", "YWdlbnQ3NTBjb250ZXh0NzUw"),
    ("agent750knowledge750", "YWdlbnQ3NTBrbm93bGVkZ2U3NTA"),
    ("agent750vector750", "YWdlbnQ3NTB2ZWN0b3I3NTA"),
    ("angle750vector750", "YW5nbGU3NTB2ZWN0b3I3NTA"),
    ("angle750processor750", "YW5nbGU3NTBwcm9jZXNzb3I3NTA"),
    ("angle750reasoning750", "YW5nbGU3NTByZWFzb25pbmc3NTA"),
    ("angle750machine750", "YW5nbGU3NTBtYWNoaW5lNzUw"),
    ("universe750machine750", "dW5pdmVyc2U3NTBtYWNoaW5lNzUw"),
    ("universe750learning750", "dW5pdmVyc2U3NTBsZWFybmluZzc1MA"),
    ("universe750model750", "dW5pdmVyc2U3NTBtb2RlbDc1MA"),
    ("universe750token750", "dW5pdmVyc2U3NTB0b2tlbjc1MA"),
    ("memory750token750", "bWVtb3J5NzUwdG9rZW43NTA"),
    ("memory750prompt750", "bWVtb3J5NzUwcHJvbXB0NzUw"),
    ("memory750session750", "bWVtb3J5NzUwc2Vzc2lvbjc1MA"),
    ("memory750library750", "bWVtb3J5NzUwbGlicmFyeTc1MA"),
    ("stream750library750", "c3RyZWFtNzUwbGlicmFyeTc1MA"),
    ("stream750service750", "c3RyZWFtNzUwc2VydmljZTc1MA"),
    ("stream750gateway750", "c3RyZWFtNzUwZ2F0ZXdheTc1MA"),
    ("stream750storage750", "c3RyZWFtNzUwc3RvcmFnZTc1MA"),
    ("context750storage750", "Y29udGV4dDc1MHN0b3JhZ2U3NTA"),
    ("context750network750", "Y29udGV4dDc1MG5ldHdvcms3NTA"),
    ("context750latency750", "Y29udGV4dDc1MGxhdGVuY3k3NTA"),
    ("context750buffer750", "Y29udGV4dDc1MGJ1ZmZlcjc1MA"),
    ("knowledge750buffer750", "a25vd2xlZGdlNzUwYnVmZmVyNzUw"),
    ("knowledge750queue750", "a25vd2xlZGdlNzUwcXVldWU3NTA"),
    ("knowledge750worker750", "a25vd2xlZGdlNzUwd29ya2VyNzUw"),
    ("knowledge750kernel750", "a25vd2xlZGdlNzUwa2VybmVsNzUw"),
    ("vector750kernel750", "dmVjdG9yNzUwa2VybmVsNzUw"),
    ("vector750signal750", "dmVjdG9yNzUwc2lnbmFsNzUw"),
    ("vector750packet750", "dmVjdG9yNzUwcGFja2V0NzUw"),
    ("vector750router750", "dmVjdG9yNzUwcm91dGVyNzUw"),
    ("processor750router750", "cHJvY2Vzc29yNzUwcm91dGVyNzUw"),
    ("processor750cluster750", "cHJvY2Vzc29yNzUwY2x1c3Rlcjc1MA"),
    ("processor750mirror750", "cHJvY2Vzc29yNzUwbWlycm9yNzUw"),
    ("processor750filter750", "cHJvY2Vzc29yNzUwZmlsdGVyNzUw"),
    ("reasoning750filter750", "cmVhc29uaW5nNzUwZmlsdGVyNzUw"),
    ("reasoning750ranking750", "cmVhc29uaW5nNzUwcmFua2luZzc1MA"),
    ("reasoning750encoding750", "cmVhc29uaW5nNzUwZW5jb2Rpbmc3NTA"),
    ("reasoning750mapping750", "cmVhc29uaW5nNzUwbWFwcGluZzc1MA"),
    ("machine750mapping750", "bWFjaGluZTc1MG1hcHBpbmc3NTA"),
    ("machine750record750", "bWFjaGluZTc1MHJlY29yZDc1MA"),
    ("machine750candle750", "bWFjaGluZTc1MGNhbmRsZTc1MA"),
    ("machine750thread750", "bWFjaGluZTc1MHRocmVhZDc1MA"),
    ("learning750thread750", "bGVhcm5pbmc3NTB0aHJlYWQ3NTA"),
    ("learning750kitten750", "bGVhcm5pbmc3NTBraXR0ZW43NTA"),
    ("learning750sitting750", "bGVhcm5pbmc3NTBzaXR0aW5nNzUw"),
    ("learning750agent750", "bGVhcm5pbmc3NTBhZ2VudDc1MA"),
    ("model750agent750", "bW9kZWw3NTBhZ2VudDc1MA"),
    ("model750angle750", "bW9kZWw3NTBhbmdsZTc1MA"),
    ("model750universe750", "bW9kZWw3NTB1bml2ZXJzZTc1MA"),
    ("model750memory750", "bW9kZWw3NTBtZW1vcnk3NTA"),
    ("token750memory750", "dG9rZW43NTBtZW1vcnk3NTA"),
    ("token750stream750", "dG9rZW43NTBzdHJlYW03NTA"),
    ("token750context750", "dG9rZW43NTBjb250ZXh0NzUw"),
    ("token750knowledge750", "dG9rZW43NTBrbm93bGVkZ2U3NTA"),
    ("prompt750knowledge750", "cHJvbXB0NzUwa25vd2xlZGdlNzUw"),
    ("prompt750vector750", "cHJvbXB0NzUwdmVjdG9yNzUw"),
    ("prompt750processor750", "cHJvbXB0NzUwcHJvY2Vzc29yNzUw"),
    ("prompt750reasoning750", "cHJvbXB0NzUwcmVhc29uaW5nNzUw"),
    ("session750reasoning750", "c2Vzc2lvbjc1MHJlYXNvbmluZzc1MA"),
    ("session750machine750", "c2Vzc2lvbjc1MG1hY2hpbmU3NTA"),
    ("session750learning750", "c2Vzc2lvbjc1MGxlYXJuaW5nNzUw"),
    ("session750model750", "c2Vzc2lvbjc1MG1vZGVsNzUw"),
    ("library750model750", "bGlicmFyeTc1MG1vZGVsNzUw"),
    ("library750token750", "bGlicmFyeTc1MHRva2VuNzUw"),
    ("library750prompt750", "bGlicmFyeTc1MHByb21wdDc1MA"),
    ("library750session750", "bGlicmFyeTc1MHNlc3Npb243NTA"),
    ("service750session750", "c2VydmljZTc1MHNlc3Npb243NTA"),
    ("service750library750", "c2VydmljZTc1MGxpYnJhcnk3NTA"),
    ("service750service750", "c2VydmljZTc1MHNlcnZpY2U3NTA"),
    ("service750gateway750", "c2VydmljZTc1MGdhdGV3YXk3NTA"),
    ("gateway750gateway750", "Z2F0ZXdheTc1MGdhdGV3YXk3NTA"),
    ("gateway750storage750", "Z2F0ZXdheTc1MHN0b3JhZ2U3NTA"),
    ("gateway750network750", "Z2F0ZXdheTc1MG5ldHdvcms3NTA"),
    ("gateway750latency750", "Z2F0ZXdheTc1MGxhdGVuY3k3NTA"),
    ("storage750latency750", "c3RvcmFnZTc1MGxhdGVuY3k3NTA"),
    ("storage750buffer750", "c3RvcmFnZTc1MGJ1ZmZlcjc1MA"),
    ("storage750queue750", "c3RvcmFnZTc1MHF1ZXVlNzUw"),
    ("storage750worker750", "c3RvcmFnZTc1MHdvcmtlcjc1MA"),
    ("network750worker750", "bmV0d29yazc1MHdvcmtlcjc1MA"),
    ("network750kernel750", "bmV0d29yazc1MGtlcm5lbDc1MA"),
    ("network750signal750", "bmV0d29yazc1MHNpZ25hbDc1MA"),
    ("network750packet750", "bmV0d29yazc1MHBhY2tldDc1MA"),
    ("latency750packet750", "bGF0ZW5jeTc1MHBhY2tldDc1MA"),
    ("latency750router750", "bGF0ZW5jeTc1MHJvdXRlcjc1MA"),
    ("latency750cluster750", "bGF0ZW5jeTc1MGNsdXN0ZXI3NTA"),
    ("latency750mirror750", "bGF0ZW5jeTc1MG1pcnJvcjc1MA"),
    ("buffer750mirror750", "YnVmZmVyNzUwbWlycm9yNzUw"),
    ("buffer750filter750", "YnVmZmVyNzUwZmlsdGVyNzUw"),
    ("buffer750ranking750", "YnVmZmVyNzUwcmFua2luZzc1MA"),
    ("buffer750encoding750", "YnVmZmVyNzUwZW5jb2Rpbmc3NTA"),
    ("queue750encoding750", "cXVldWU3NTBlbmNvZGluZzc1MA"),
    ("queue750mapping750", "cXVldWU3NTBtYXBwaW5nNzUw"),
    ("queue750record750", "cXVldWU3NTByZWNvcmQ3NTA"),
    ("queue750candle750", "cXVldWU3NTBjYW5kbGU3NTA"),
    ("worker750candle750", "d29ya2VyNzUwY2FuZGxlNzUw"),
    ("worker750thread750", "d29ya2VyNzUwdGhyZWFkNzUw"),
    ("worker750kitten750", "d29ya2VyNzUwa2l0dGVuNzUw"),
    ("worker750sitting750", "d29ya2VyNzUwc2l0dGluZzc1MA"),
    ("kernel750sitting750", "a2VybmVsNzUwc2l0dGluZzc1MA"),
    ("kernel750agent750", "a2VybmVsNzUwYWdlbnQ3NTA"),
    ("kernel750angle750", "a2VybmVsNzUwYW5nbGU3NTA"),
    ("kernel750universe750", "a2VybmVsNzUwdW5pdmVyc2U3NTA"),
    ("signal750universe750", "c2lnbmFsNzUwdW5pdmVyc2U3NTA"),
    ("signal750memory750", "c2lnbmFsNzUwbWVtb3J5NzUw"),
    ("signal750stream750", "c2lnbmFsNzUwc3RyZWFtNzUw"),
    ("signal750context750", "c2lnbmFsNzUwY29udGV4dDc1MA"),
    ("packet750context750", "cGFja2V0NzUwY29udGV4dDc1MA"),
    ("packet750knowledge750", "cGFja2V0NzUwa25vd2xlZGdlNzUw"),
    ("packet750vector750", "cGFja2V0NzUwdmVjdG9yNzUw"),
    ("packet750processor750", "cGFja2V0NzUwcHJvY2Vzc29yNzUw"),
    ("router750processor750", "cm91dGVyNzUwcHJvY2Vzc29yNzUw"),
    ("router750reasoning750", "cm91dGVyNzUwcmVhc29uaW5nNzUw"),
    ("router750machine750", "cm91dGVyNzUwbWFjaGluZTc1MA"),
    ("router750learning750", "cm91dGVyNzUwbGVhcm5pbmc3NTA"),
    ("cluster750learning750", "Y2x1c3Rlcjc1MGxlYXJuaW5nNzUw"),
    ("cluster750model750", "Y2x1c3Rlcjc1MG1vZGVsNzUw"),
    ("cluster750token750", "Y2x1c3Rlcjc1MHRva2VuNzUw"),
    ("cluster750prompt750", "Y2x1c3Rlcjc1MHByb21wdDc1MA"),
    ("mirror750prompt750", "bWlycm9yNzUwcHJvbXB0NzUw"),
    ("mirror750session750", "bWlycm9yNzUwc2Vzc2lvbjc1MA"),
    ("mirror750library750", "bWlycm9yNzUwbGlicmFyeTc1MA"),
    ("mirror750service750", "bWlycm9yNzUwc2VydmljZTc1MA"),
    ("filter750service750", "ZmlsdGVyNzUwc2VydmljZTc1MA"),
    ("filter750gateway750", "ZmlsdGVyNzUwZ2F0ZXdheTc1MA"),
    ("filter750storage750", "ZmlsdGVyNzUwc3RvcmFnZTc1MA"),
    ("filter750network750", "ZmlsdGVyNzUwbmV0d29yazc1MA"),
    ("ranking750network750", "cmFua2luZzc1MG5ldHdvcms3NTA"),
    ("ranking750latency750", "cmFua2luZzc1MGxhdGVuY3k3NTA"),
    ("ranking750buffer750", "cmFua2luZzc1MGJ1ZmZlcjc1MA"),
    ("ranking750queue750", "cmFua2luZzc1MHF1ZXVlNzUw"),
    ("encoding750queue750", "ZW5jb2Rpbmc3NTBxdWV1ZTc1MA"),
    ("encoding750worker750", "ZW5jb2Rpbmc3NTB3b3JrZXI3NTA"),
    ("encoding750kernel750", "ZW5jb2Rpbmc3NTBrZXJuZWw3NTA"),
    ("encoding750signal750", "ZW5jb2Rpbmc3NTBzaWduYWw3NTA"),
    ("mapping750signal750", "bWFwcGluZzc1MHNpZ25hbDc1MA"),
    ("mapping750packet750", "bWFwcGluZzc1MHBhY2tldDc1MA"),
    ("mapping750router750", "bWFwcGluZzc1MHJvdXRlcjc1MA"),
    ("mapping750cluster750", "bWFwcGluZzc1MGNsdXN0ZXI3NTA"),
    ("record750cluster750", "cmVjb3JkNzUwY2x1c3Rlcjc1MA"),
    ("record750mirror750", "cmVjb3JkNzUwbWlycm9yNzUw"),
    ("record750filter750", "cmVjb3JkNzUwZmlsdGVyNzUw"),
    ("record750ranking750", "cmVjb3JkNzUwcmFua2luZzc1MA"),
    ("candle750ranking750", "Y2FuZGxlNzUwcmFua2luZzc1MA"),
    ("candle750encoding750", "Y2FuZGxlNzUwZW5jb2Rpbmc3NTA"),
    ("candle750mapping750", "Y2FuZGxlNzUwbWFwcGluZzc1MA"),
    ("candle750record750", "Y2FuZGxlNzUwcmVjb3JkNzUw"),
    ("thread750record750", "dGhyZWFkNzUwcmVjb3JkNzUw"),
    ("thread750candle750", "dGhyZWFkNzUwY2FuZGxlNzUw"),
    ("thread750thread750", "dGhyZWFkNzUwdGhyZWFkNzUw"),
    ("thread750kitten750", "dGhyZWFkNzUwa2l0dGVuNzUw"),
    (
        "round 750: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzUwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 750: agentuniverse is a framework for multi agents",
        "cm91bmQgNzUwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 750: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzUwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 750: the processor reads the record then stops",
        "cm91bmQgNzUwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 750: a worker pulls the next task from the queue",
        "cm91bmQgNzUwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 750: signals travel through the network layer",
        "cm91bmQgNzUwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 750: the gateway routes each request by policy",
        "cm91bmQgNzUwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 750: memory grows until the buffer is full",
        "cm91bmQgNzUwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 750: the cluster mirrors every packet twice",
        "cm91bmQgNzUwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 750: ranking uses tokens learned from the corpus",
        "cm91bmQgNzUwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 750: a long session ends when the candle dies",
        "cm91bmQgNzUwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 750: encode the prompt then map the result",
        "cm91bmQgNzUwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 750: the kernel wakes the worker at dawn",
        "cm91bmQgNzUwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 750: service latency drops after the patch",
        "cm91bmQgNzUwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 750: the library caches every vector it sees",
        "cm91bmQgNzUwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 750: agents argue then the debate resolves",
        "cm91bmQgNzUwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 750: the filter keeps only strong matches",
        "cm91bmQgNzUwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 750: the model answers with a short reply",
        "cm91bmQgNzUwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 750: the recorder stores the reasoning trace",
        "cm91bmQgNzUwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 750: the angel watches the processor run",
        "cm91bmQgNzUwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 750: angle of the vector decides the match",
        "cm91bmQgNzUwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 750: the candle burns twice as long at night",
        "cm91bmQgNzUwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 750: a mirror of the universe in one line",
        "cm91bmQgNzUwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 750: the queue drains before the storm", "cm91bmQgNzUwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
