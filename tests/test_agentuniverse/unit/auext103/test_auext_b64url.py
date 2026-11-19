"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten103kitten103", "a2l0dGVuMTAza2l0dGVuMTAz"),
    ("kitten103sitting103", "a2l0dGVuMTAzc2l0dGluZzEwMw"),
    ("kitten103agent103", "a2l0dGVuMTAzYWdlbnQxMDM"),
    ("kitten103angle103", "a2l0dGVuMTAzYW5nbGUxMDM"),
    ("sitting103angle103", "c2l0dGluZzEwM2FuZ2xlMTAz"),
    ("sitting103universe103", "c2l0dGluZzEwM3VuaXZlcnNlMTAz"),
    ("sitting103memory103", "c2l0dGluZzEwM21lbW9yeTEwMw"),
    ("sitting103stream103", "c2l0dGluZzEwM3N0cmVhbTEwMw"),
    ("agent103stream103", "YWdlbnQxMDNzdHJlYW0xMDM"),
    ("agent103context103", "YWdlbnQxMDNjb250ZXh0MTAz"),
    ("agent103knowledge103", "YWdlbnQxMDNrbm93bGVkZ2UxMDM"),
    ("agent103vector103", "YWdlbnQxMDN2ZWN0b3IxMDM"),
    ("angle103vector103", "YW5nbGUxMDN2ZWN0b3IxMDM"),
    ("angle103processor103", "YW5nbGUxMDNwcm9jZXNzb3IxMDM"),
    ("angle103reasoning103", "YW5nbGUxMDNyZWFzb25pbmcxMDM"),
    ("angle103machine103", "YW5nbGUxMDNtYWNoaW5lMTAz"),
    ("universe103machine103", "dW5pdmVyc2UxMDNtYWNoaW5lMTAz"),
    ("universe103learning103", "dW5pdmVyc2UxMDNsZWFybmluZzEwMw"),
    ("universe103model103", "dW5pdmVyc2UxMDNtb2RlbDEwMw"),
    ("universe103token103", "dW5pdmVyc2UxMDN0b2tlbjEwMw"),
    ("memory103token103", "bWVtb3J5MTAzdG9rZW4xMDM"),
    ("memory103prompt103", "bWVtb3J5MTAzcHJvbXB0MTAz"),
    ("memory103session103", "bWVtb3J5MTAzc2Vzc2lvbjEwMw"),
    ("memory103library103", "bWVtb3J5MTAzbGlicmFyeTEwMw"),
    ("stream103library103", "c3RyZWFtMTAzbGlicmFyeTEwMw"),
    ("stream103service103", "c3RyZWFtMTAzc2VydmljZTEwMw"),
    ("stream103gateway103", "c3RyZWFtMTAzZ2F0ZXdheTEwMw"),
    ("stream103storage103", "c3RyZWFtMTAzc3RvcmFnZTEwMw"),
    ("context103storage103", "Y29udGV4dDEwM3N0b3JhZ2UxMDM"),
    ("context103network103", "Y29udGV4dDEwM25ldHdvcmsxMDM"),
    ("context103latency103", "Y29udGV4dDEwM2xhdGVuY3kxMDM"),
    ("context103buffer103", "Y29udGV4dDEwM2J1ZmZlcjEwMw"),
    ("knowledge103buffer103", "a25vd2xlZGdlMTAzYnVmZmVyMTAz"),
    ("knowledge103queue103", "a25vd2xlZGdlMTAzcXVldWUxMDM"),
    ("knowledge103worker103", "a25vd2xlZGdlMTAzd29ya2VyMTAz"),
    ("knowledge103kernel103", "a25vd2xlZGdlMTAza2VybmVsMTAz"),
    ("vector103kernel103", "dmVjdG9yMTAza2VybmVsMTAz"),
    ("vector103signal103", "dmVjdG9yMTAzc2lnbmFsMTAz"),
    ("vector103packet103", "dmVjdG9yMTAzcGFja2V0MTAz"),
    ("vector103router103", "dmVjdG9yMTAzcm91dGVyMTAz"),
    ("processor103router103", "cHJvY2Vzc29yMTAzcm91dGVyMTAz"),
    ("processor103cluster103", "cHJvY2Vzc29yMTAzY2x1c3RlcjEwMw"),
    ("processor103mirror103", "cHJvY2Vzc29yMTAzbWlycm9yMTAz"),
    ("processor103filter103", "cHJvY2Vzc29yMTAzZmlsdGVyMTAz"),
    ("reasoning103filter103", "cmVhc29uaW5nMTAzZmlsdGVyMTAz"),
    ("reasoning103ranking103", "cmVhc29uaW5nMTAzcmFua2luZzEwMw"),
    ("reasoning103encoding103", "cmVhc29uaW5nMTAzZW5jb2RpbmcxMDM"),
    ("reasoning103mapping103", "cmVhc29uaW5nMTAzbWFwcGluZzEwMw"),
    ("machine103mapping103", "bWFjaGluZTEwM21hcHBpbmcxMDM"),
    ("machine103record103", "bWFjaGluZTEwM3JlY29yZDEwMw"),
    ("machine103candle103", "bWFjaGluZTEwM2NhbmRsZTEwMw"),
    ("machine103thread103", "bWFjaGluZTEwM3RocmVhZDEwMw"),
    ("learning103thread103", "bGVhcm5pbmcxMDN0aHJlYWQxMDM"),
    ("learning103kitten103", "bGVhcm5pbmcxMDNraXR0ZW4xMDM"),
    ("learning103sitting103", "bGVhcm5pbmcxMDNzaXR0aW5nMTAz"),
    ("learning103agent103", "bGVhcm5pbmcxMDNhZ2VudDEwMw"),
    ("model103agent103", "bW9kZWwxMDNhZ2VudDEwMw"),
    ("model103angle103", "bW9kZWwxMDNhbmdsZTEwMw"),
    ("model103universe103", "bW9kZWwxMDN1bml2ZXJzZTEwMw"),
    ("model103memory103", "bW9kZWwxMDNtZW1vcnkxMDM"),
    ("token103memory103", "dG9rZW4xMDNtZW1vcnkxMDM"),
    ("token103stream103", "dG9rZW4xMDNzdHJlYW0xMDM"),
    ("token103context103", "dG9rZW4xMDNjb250ZXh0MTAz"),
    ("token103knowledge103", "dG9rZW4xMDNrbm93bGVkZ2UxMDM"),
    ("prompt103knowledge103", "cHJvbXB0MTAza25vd2xlZGdlMTAz"),
    ("prompt103vector103", "cHJvbXB0MTAzdmVjdG9yMTAz"),
    ("prompt103processor103", "cHJvbXB0MTAzcHJvY2Vzc29yMTAz"),
    ("prompt103reasoning103", "cHJvbXB0MTAzcmVhc29uaW5nMTAz"),
    ("session103reasoning103", "c2Vzc2lvbjEwM3JlYXNvbmluZzEwMw"),
    ("session103machine103", "c2Vzc2lvbjEwM21hY2hpbmUxMDM"),
    ("session103learning103", "c2Vzc2lvbjEwM2xlYXJuaW5nMTAz"),
    ("session103model103", "c2Vzc2lvbjEwM21vZGVsMTAz"),
    ("library103model103", "bGlicmFyeTEwM21vZGVsMTAz"),
    ("library103token103", "bGlicmFyeTEwM3Rva2VuMTAz"),
    ("library103prompt103", "bGlicmFyeTEwM3Byb21wdDEwMw"),
    ("library103session103", "bGlicmFyeTEwM3Nlc3Npb24xMDM"),
    ("service103session103", "c2VydmljZTEwM3Nlc3Npb24xMDM"),
    ("service103library103", "c2VydmljZTEwM2xpYnJhcnkxMDM"),
    ("service103service103", "c2VydmljZTEwM3NlcnZpY2UxMDM"),
    ("service103gateway103", "c2VydmljZTEwM2dhdGV3YXkxMDM"),
    ("gateway103gateway103", "Z2F0ZXdheTEwM2dhdGV3YXkxMDM"),
    ("gateway103storage103", "Z2F0ZXdheTEwM3N0b3JhZ2UxMDM"),
    ("gateway103network103", "Z2F0ZXdheTEwM25ldHdvcmsxMDM"),
    ("gateway103latency103", "Z2F0ZXdheTEwM2xhdGVuY3kxMDM"),
    ("storage103latency103", "c3RvcmFnZTEwM2xhdGVuY3kxMDM"),
    ("storage103buffer103", "c3RvcmFnZTEwM2J1ZmZlcjEwMw"),
    ("storage103queue103", "c3RvcmFnZTEwM3F1ZXVlMTAz"),
    ("storage103worker103", "c3RvcmFnZTEwM3dvcmtlcjEwMw"),
    ("network103worker103", "bmV0d29yazEwM3dvcmtlcjEwMw"),
    ("network103kernel103", "bmV0d29yazEwM2tlcm5lbDEwMw"),
    ("network103signal103", "bmV0d29yazEwM3NpZ25hbDEwMw"),
    ("network103packet103", "bmV0d29yazEwM3BhY2tldDEwMw"),
    ("latency103packet103", "bGF0ZW5jeTEwM3BhY2tldDEwMw"),
    ("latency103router103", "bGF0ZW5jeTEwM3JvdXRlcjEwMw"),
    ("latency103cluster103", "bGF0ZW5jeTEwM2NsdXN0ZXIxMDM"),
    ("latency103mirror103", "bGF0ZW5jeTEwM21pcnJvcjEwMw"),
    ("buffer103mirror103", "YnVmZmVyMTAzbWlycm9yMTAz"),
    ("buffer103filter103", "YnVmZmVyMTAzZmlsdGVyMTAz"),
    ("buffer103ranking103", "YnVmZmVyMTAzcmFua2luZzEwMw"),
    ("buffer103encoding103", "YnVmZmVyMTAzZW5jb2RpbmcxMDM"),
    ("queue103encoding103", "cXVldWUxMDNlbmNvZGluZzEwMw"),
    ("queue103mapping103", "cXVldWUxMDNtYXBwaW5nMTAz"),
    ("queue103record103", "cXVldWUxMDNyZWNvcmQxMDM"),
    ("queue103candle103", "cXVldWUxMDNjYW5kbGUxMDM"),
    ("worker103candle103", "d29ya2VyMTAzY2FuZGxlMTAz"),
    ("worker103thread103", "d29ya2VyMTAzdGhyZWFkMTAz"),
    ("worker103kitten103", "d29ya2VyMTAza2l0dGVuMTAz"),
    ("worker103sitting103", "d29ya2VyMTAzc2l0dGluZzEwMw"),
    ("kernel103sitting103", "a2VybmVsMTAzc2l0dGluZzEwMw"),
    ("kernel103agent103", "a2VybmVsMTAzYWdlbnQxMDM"),
    ("kernel103angle103", "a2VybmVsMTAzYW5nbGUxMDM"),
    ("kernel103universe103", "a2VybmVsMTAzdW5pdmVyc2UxMDM"),
    ("signal103universe103", "c2lnbmFsMTAzdW5pdmVyc2UxMDM"),
    ("signal103memory103", "c2lnbmFsMTAzbWVtb3J5MTAz"),
    ("signal103stream103", "c2lnbmFsMTAzc3RyZWFtMTAz"),
    ("signal103context103", "c2lnbmFsMTAzY29udGV4dDEwMw"),
    ("packet103context103", "cGFja2V0MTAzY29udGV4dDEwMw"),
    ("packet103knowledge103", "cGFja2V0MTAza25vd2xlZGdlMTAz"),
    ("packet103vector103", "cGFja2V0MTAzdmVjdG9yMTAz"),
    ("packet103processor103", "cGFja2V0MTAzcHJvY2Vzc29yMTAz"),
    ("router103processor103", "cm91dGVyMTAzcHJvY2Vzc29yMTAz"),
    ("router103reasoning103", "cm91dGVyMTAzcmVhc29uaW5nMTAz"),
    ("router103machine103", "cm91dGVyMTAzbWFjaGluZTEwMw"),
    ("router103learning103", "cm91dGVyMTAzbGVhcm5pbmcxMDM"),
    ("cluster103learning103", "Y2x1c3RlcjEwM2xlYXJuaW5nMTAz"),
    ("cluster103model103", "Y2x1c3RlcjEwM21vZGVsMTAz"),
    ("cluster103token103", "Y2x1c3RlcjEwM3Rva2VuMTAz"),
    ("cluster103prompt103", "Y2x1c3RlcjEwM3Byb21wdDEwMw"),
    ("mirror103prompt103", "bWlycm9yMTAzcHJvbXB0MTAz"),
    ("mirror103session103", "bWlycm9yMTAzc2Vzc2lvbjEwMw"),
    ("mirror103library103", "bWlycm9yMTAzbGlicmFyeTEwMw"),
    ("mirror103service103", "bWlycm9yMTAzc2VydmljZTEwMw"),
    ("filter103service103", "ZmlsdGVyMTAzc2VydmljZTEwMw"),
    ("filter103gateway103", "ZmlsdGVyMTAzZ2F0ZXdheTEwMw"),
    ("filter103storage103", "ZmlsdGVyMTAzc3RvcmFnZTEwMw"),
    ("filter103network103", "ZmlsdGVyMTAzbmV0d29yazEwMw"),
    ("ranking103network103", "cmFua2luZzEwM25ldHdvcmsxMDM"),
    ("ranking103latency103", "cmFua2luZzEwM2xhdGVuY3kxMDM"),
    ("ranking103buffer103", "cmFua2luZzEwM2J1ZmZlcjEwMw"),
    ("ranking103queue103", "cmFua2luZzEwM3F1ZXVlMTAz"),
    ("encoding103queue103", "ZW5jb2RpbmcxMDNxdWV1ZTEwMw"),
    ("encoding103worker103", "ZW5jb2RpbmcxMDN3b3JrZXIxMDM"),
    ("encoding103kernel103", "ZW5jb2RpbmcxMDNrZXJuZWwxMDM"),
    ("encoding103signal103", "ZW5jb2RpbmcxMDNzaWduYWwxMDM"),
    ("mapping103signal103", "bWFwcGluZzEwM3NpZ25hbDEwMw"),
    ("mapping103packet103", "bWFwcGluZzEwM3BhY2tldDEwMw"),
    ("mapping103router103", "bWFwcGluZzEwM3JvdXRlcjEwMw"),
    ("mapping103cluster103", "bWFwcGluZzEwM2NsdXN0ZXIxMDM"),
    ("record103cluster103", "cmVjb3JkMTAzY2x1c3RlcjEwMw"),
    ("record103mirror103", "cmVjb3JkMTAzbWlycm9yMTAz"),
    ("record103filter103", "cmVjb3JkMTAzZmlsdGVyMTAz"),
    ("record103ranking103", "cmVjb3JkMTAzcmFua2luZzEwMw"),
    ("candle103ranking103", "Y2FuZGxlMTAzcmFua2luZzEwMw"),
    ("candle103encoding103", "Y2FuZGxlMTAzZW5jb2RpbmcxMDM"),
    ("candle103mapping103", "Y2FuZGxlMTAzbWFwcGluZzEwMw"),
    ("candle103record103", "Y2FuZGxlMTAzcmVjb3JkMTAz"),
    ("thread103record103", "dGhyZWFkMTAzcmVjb3JkMTAz"),
    ("thread103candle103", "dGhyZWFkMTAzY2FuZGxlMTAz"),
    ("thread103thread103", "dGhyZWFkMTAzdGhyZWFkMTAz"),
    ("thread103kitten103", "dGhyZWFkMTAza2l0dGVuMTAz"),
    (
        "round 103: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTAzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 103: agentuniverse is a framework for multi agents",
        "cm91bmQgMTAzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 103: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTAzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 103: the processor reads the record then stops",
        "cm91bmQgMTAzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 103: a worker pulls the next task from the queue",
        "cm91bmQgMTAzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 103: signals travel through the network layer",
        "cm91bmQgMTAzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 103: the gateway routes each request by policy",
        "cm91bmQgMTAzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 103: memory grows until the buffer is full",
        "cm91bmQgMTAzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 103: the cluster mirrors every packet twice",
        "cm91bmQgMTAzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 103: ranking uses tokens learned from the corpus",
        "cm91bmQgMTAzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 103: a long session ends when the candle dies",
        "cm91bmQgMTAzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 103: encode the prompt then map the result",
        "cm91bmQgMTAzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 103: the kernel wakes the worker at dawn",
        "cm91bmQgMTAzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 103: service latency drops after the patch",
        "cm91bmQgMTAzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 103: the library caches every vector it sees",
        "cm91bmQgMTAzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 103: agents argue then the debate resolves",
        "cm91bmQgMTAzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 103: the filter keeps only strong matches",
        "cm91bmQgMTAzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 103: the model answers with a short reply",
        "cm91bmQgMTAzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 103: the recorder stores the reasoning trace",
        "cm91bmQgMTAzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 103: the angel watches the processor run",
        "cm91bmQgMTAzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 103: angle of the vector decides the match",
        "cm91bmQgMTAzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 103: the candle burns twice as long at night",
        "cm91bmQgMTAzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 103: a mirror of the universe in one line",
        "cm91bmQgMTAzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 103: the queue drains before the storm", "cm91bmQgMTAzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
