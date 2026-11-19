"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten100kitten100", "a2l0dGVuMTAwa2l0dGVuMTAw"),
    ("kitten100sitting100", "a2l0dGVuMTAwc2l0dGluZzEwMA"),
    ("kitten100agent100", "a2l0dGVuMTAwYWdlbnQxMDA"),
    ("kitten100angle100", "a2l0dGVuMTAwYW5nbGUxMDA"),
    ("sitting100angle100", "c2l0dGluZzEwMGFuZ2xlMTAw"),
    ("sitting100universe100", "c2l0dGluZzEwMHVuaXZlcnNlMTAw"),
    ("sitting100memory100", "c2l0dGluZzEwMG1lbW9yeTEwMA"),
    ("sitting100stream100", "c2l0dGluZzEwMHN0cmVhbTEwMA"),
    ("agent100stream100", "YWdlbnQxMDBzdHJlYW0xMDA"),
    ("agent100context100", "YWdlbnQxMDBjb250ZXh0MTAw"),
    ("agent100knowledge100", "YWdlbnQxMDBrbm93bGVkZ2UxMDA"),
    ("agent100vector100", "YWdlbnQxMDB2ZWN0b3IxMDA"),
    ("angle100vector100", "YW5nbGUxMDB2ZWN0b3IxMDA"),
    ("angle100processor100", "YW5nbGUxMDBwcm9jZXNzb3IxMDA"),
    ("angle100reasoning100", "YW5nbGUxMDByZWFzb25pbmcxMDA"),
    ("angle100machine100", "YW5nbGUxMDBtYWNoaW5lMTAw"),
    ("universe100machine100", "dW5pdmVyc2UxMDBtYWNoaW5lMTAw"),
    ("universe100learning100", "dW5pdmVyc2UxMDBsZWFybmluZzEwMA"),
    ("universe100model100", "dW5pdmVyc2UxMDBtb2RlbDEwMA"),
    ("universe100token100", "dW5pdmVyc2UxMDB0b2tlbjEwMA"),
    ("memory100token100", "bWVtb3J5MTAwdG9rZW4xMDA"),
    ("memory100prompt100", "bWVtb3J5MTAwcHJvbXB0MTAw"),
    ("memory100session100", "bWVtb3J5MTAwc2Vzc2lvbjEwMA"),
    ("memory100library100", "bWVtb3J5MTAwbGlicmFyeTEwMA"),
    ("stream100library100", "c3RyZWFtMTAwbGlicmFyeTEwMA"),
    ("stream100service100", "c3RyZWFtMTAwc2VydmljZTEwMA"),
    ("stream100gateway100", "c3RyZWFtMTAwZ2F0ZXdheTEwMA"),
    ("stream100storage100", "c3RyZWFtMTAwc3RvcmFnZTEwMA"),
    ("context100storage100", "Y29udGV4dDEwMHN0b3JhZ2UxMDA"),
    ("context100network100", "Y29udGV4dDEwMG5ldHdvcmsxMDA"),
    ("context100latency100", "Y29udGV4dDEwMGxhdGVuY3kxMDA"),
    ("context100buffer100", "Y29udGV4dDEwMGJ1ZmZlcjEwMA"),
    ("knowledge100buffer100", "a25vd2xlZGdlMTAwYnVmZmVyMTAw"),
    ("knowledge100queue100", "a25vd2xlZGdlMTAwcXVldWUxMDA"),
    ("knowledge100worker100", "a25vd2xlZGdlMTAwd29ya2VyMTAw"),
    ("knowledge100kernel100", "a25vd2xlZGdlMTAwa2VybmVsMTAw"),
    ("vector100kernel100", "dmVjdG9yMTAwa2VybmVsMTAw"),
    ("vector100signal100", "dmVjdG9yMTAwc2lnbmFsMTAw"),
    ("vector100packet100", "dmVjdG9yMTAwcGFja2V0MTAw"),
    ("vector100router100", "dmVjdG9yMTAwcm91dGVyMTAw"),
    ("processor100router100", "cHJvY2Vzc29yMTAwcm91dGVyMTAw"),
    ("processor100cluster100", "cHJvY2Vzc29yMTAwY2x1c3RlcjEwMA"),
    ("processor100mirror100", "cHJvY2Vzc29yMTAwbWlycm9yMTAw"),
    ("processor100filter100", "cHJvY2Vzc29yMTAwZmlsdGVyMTAw"),
    ("reasoning100filter100", "cmVhc29uaW5nMTAwZmlsdGVyMTAw"),
    ("reasoning100ranking100", "cmVhc29uaW5nMTAwcmFua2luZzEwMA"),
    ("reasoning100encoding100", "cmVhc29uaW5nMTAwZW5jb2RpbmcxMDA"),
    ("reasoning100mapping100", "cmVhc29uaW5nMTAwbWFwcGluZzEwMA"),
    ("machine100mapping100", "bWFjaGluZTEwMG1hcHBpbmcxMDA"),
    ("machine100record100", "bWFjaGluZTEwMHJlY29yZDEwMA"),
    ("machine100candle100", "bWFjaGluZTEwMGNhbmRsZTEwMA"),
    ("machine100thread100", "bWFjaGluZTEwMHRocmVhZDEwMA"),
    ("learning100thread100", "bGVhcm5pbmcxMDB0aHJlYWQxMDA"),
    ("learning100kitten100", "bGVhcm5pbmcxMDBraXR0ZW4xMDA"),
    ("learning100sitting100", "bGVhcm5pbmcxMDBzaXR0aW5nMTAw"),
    ("learning100agent100", "bGVhcm5pbmcxMDBhZ2VudDEwMA"),
    ("model100agent100", "bW9kZWwxMDBhZ2VudDEwMA"),
    ("model100angle100", "bW9kZWwxMDBhbmdsZTEwMA"),
    ("model100universe100", "bW9kZWwxMDB1bml2ZXJzZTEwMA"),
    ("model100memory100", "bW9kZWwxMDBtZW1vcnkxMDA"),
    ("token100memory100", "dG9rZW4xMDBtZW1vcnkxMDA"),
    ("token100stream100", "dG9rZW4xMDBzdHJlYW0xMDA"),
    ("token100context100", "dG9rZW4xMDBjb250ZXh0MTAw"),
    ("token100knowledge100", "dG9rZW4xMDBrbm93bGVkZ2UxMDA"),
    ("prompt100knowledge100", "cHJvbXB0MTAwa25vd2xlZGdlMTAw"),
    ("prompt100vector100", "cHJvbXB0MTAwdmVjdG9yMTAw"),
    ("prompt100processor100", "cHJvbXB0MTAwcHJvY2Vzc29yMTAw"),
    ("prompt100reasoning100", "cHJvbXB0MTAwcmVhc29uaW5nMTAw"),
    ("session100reasoning100", "c2Vzc2lvbjEwMHJlYXNvbmluZzEwMA"),
    ("session100machine100", "c2Vzc2lvbjEwMG1hY2hpbmUxMDA"),
    ("session100learning100", "c2Vzc2lvbjEwMGxlYXJuaW5nMTAw"),
    ("session100model100", "c2Vzc2lvbjEwMG1vZGVsMTAw"),
    ("library100model100", "bGlicmFyeTEwMG1vZGVsMTAw"),
    ("library100token100", "bGlicmFyeTEwMHRva2VuMTAw"),
    ("library100prompt100", "bGlicmFyeTEwMHByb21wdDEwMA"),
    ("library100session100", "bGlicmFyeTEwMHNlc3Npb24xMDA"),
    ("service100session100", "c2VydmljZTEwMHNlc3Npb24xMDA"),
    ("service100library100", "c2VydmljZTEwMGxpYnJhcnkxMDA"),
    ("service100service100", "c2VydmljZTEwMHNlcnZpY2UxMDA"),
    ("service100gateway100", "c2VydmljZTEwMGdhdGV3YXkxMDA"),
    ("gateway100gateway100", "Z2F0ZXdheTEwMGdhdGV3YXkxMDA"),
    ("gateway100storage100", "Z2F0ZXdheTEwMHN0b3JhZ2UxMDA"),
    ("gateway100network100", "Z2F0ZXdheTEwMG5ldHdvcmsxMDA"),
    ("gateway100latency100", "Z2F0ZXdheTEwMGxhdGVuY3kxMDA"),
    ("storage100latency100", "c3RvcmFnZTEwMGxhdGVuY3kxMDA"),
    ("storage100buffer100", "c3RvcmFnZTEwMGJ1ZmZlcjEwMA"),
    ("storage100queue100", "c3RvcmFnZTEwMHF1ZXVlMTAw"),
    ("storage100worker100", "c3RvcmFnZTEwMHdvcmtlcjEwMA"),
    ("network100worker100", "bmV0d29yazEwMHdvcmtlcjEwMA"),
    ("network100kernel100", "bmV0d29yazEwMGtlcm5lbDEwMA"),
    ("network100signal100", "bmV0d29yazEwMHNpZ25hbDEwMA"),
    ("network100packet100", "bmV0d29yazEwMHBhY2tldDEwMA"),
    ("latency100packet100", "bGF0ZW5jeTEwMHBhY2tldDEwMA"),
    ("latency100router100", "bGF0ZW5jeTEwMHJvdXRlcjEwMA"),
    ("latency100cluster100", "bGF0ZW5jeTEwMGNsdXN0ZXIxMDA"),
    ("latency100mirror100", "bGF0ZW5jeTEwMG1pcnJvcjEwMA"),
    ("buffer100mirror100", "YnVmZmVyMTAwbWlycm9yMTAw"),
    ("buffer100filter100", "YnVmZmVyMTAwZmlsdGVyMTAw"),
    ("buffer100ranking100", "YnVmZmVyMTAwcmFua2luZzEwMA"),
    ("buffer100encoding100", "YnVmZmVyMTAwZW5jb2RpbmcxMDA"),
    ("queue100encoding100", "cXVldWUxMDBlbmNvZGluZzEwMA"),
    ("queue100mapping100", "cXVldWUxMDBtYXBwaW5nMTAw"),
    ("queue100record100", "cXVldWUxMDByZWNvcmQxMDA"),
    ("queue100candle100", "cXVldWUxMDBjYW5kbGUxMDA"),
    ("worker100candle100", "d29ya2VyMTAwY2FuZGxlMTAw"),
    ("worker100thread100", "d29ya2VyMTAwdGhyZWFkMTAw"),
    ("worker100kitten100", "d29ya2VyMTAwa2l0dGVuMTAw"),
    ("worker100sitting100", "d29ya2VyMTAwc2l0dGluZzEwMA"),
    ("kernel100sitting100", "a2VybmVsMTAwc2l0dGluZzEwMA"),
    ("kernel100agent100", "a2VybmVsMTAwYWdlbnQxMDA"),
    ("kernel100angle100", "a2VybmVsMTAwYW5nbGUxMDA"),
    ("kernel100universe100", "a2VybmVsMTAwdW5pdmVyc2UxMDA"),
    ("signal100universe100", "c2lnbmFsMTAwdW5pdmVyc2UxMDA"),
    ("signal100memory100", "c2lnbmFsMTAwbWVtb3J5MTAw"),
    ("signal100stream100", "c2lnbmFsMTAwc3RyZWFtMTAw"),
    ("signal100context100", "c2lnbmFsMTAwY29udGV4dDEwMA"),
    ("packet100context100", "cGFja2V0MTAwY29udGV4dDEwMA"),
    ("packet100knowledge100", "cGFja2V0MTAwa25vd2xlZGdlMTAw"),
    ("packet100vector100", "cGFja2V0MTAwdmVjdG9yMTAw"),
    ("packet100processor100", "cGFja2V0MTAwcHJvY2Vzc29yMTAw"),
    ("router100processor100", "cm91dGVyMTAwcHJvY2Vzc29yMTAw"),
    ("router100reasoning100", "cm91dGVyMTAwcmVhc29uaW5nMTAw"),
    ("router100machine100", "cm91dGVyMTAwbWFjaGluZTEwMA"),
    ("router100learning100", "cm91dGVyMTAwbGVhcm5pbmcxMDA"),
    ("cluster100learning100", "Y2x1c3RlcjEwMGxlYXJuaW5nMTAw"),
    ("cluster100model100", "Y2x1c3RlcjEwMG1vZGVsMTAw"),
    ("cluster100token100", "Y2x1c3RlcjEwMHRva2VuMTAw"),
    ("cluster100prompt100", "Y2x1c3RlcjEwMHByb21wdDEwMA"),
    ("mirror100prompt100", "bWlycm9yMTAwcHJvbXB0MTAw"),
    ("mirror100session100", "bWlycm9yMTAwc2Vzc2lvbjEwMA"),
    ("mirror100library100", "bWlycm9yMTAwbGlicmFyeTEwMA"),
    ("mirror100service100", "bWlycm9yMTAwc2VydmljZTEwMA"),
    ("filter100service100", "ZmlsdGVyMTAwc2VydmljZTEwMA"),
    ("filter100gateway100", "ZmlsdGVyMTAwZ2F0ZXdheTEwMA"),
    ("filter100storage100", "ZmlsdGVyMTAwc3RvcmFnZTEwMA"),
    ("filter100network100", "ZmlsdGVyMTAwbmV0d29yazEwMA"),
    ("ranking100network100", "cmFua2luZzEwMG5ldHdvcmsxMDA"),
    ("ranking100latency100", "cmFua2luZzEwMGxhdGVuY3kxMDA"),
    ("ranking100buffer100", "cmFua2luZzEwMGJ1ZmZlcjEwMA"),
    ("ranking100queue100", "cmFua2luZzEwMHF1ZXVlMTAw"),
    ("encoding100queue100", "ZW5jb2RpbmcxMDBxdWV1ZTEwMA"),
    ("encoding100worker100", "ZW5jb2RpbmcxMDB3b3JrZXIxMDA"),
    ("encoding100kernel100", "ZW5jb2RpbmcxMDBrZXJuZWwxMDA"),
    ("encoding100signal100", "ZW5jb2RpbmcxMDBzaWduYWwxMDA"),
    ("mapping100signal100", "bWFwcGluZzEwMHNpZ25hbDEwMA"),
    ("mapping100packet100", "bWFwcGluZzEwMHBhY2tldDEwMA"),
    ("mapping100router100", "bWFwcGluZzEwMHJvdXRlcjEwMA"),
    ("mapping100cluster100", "bWFwcGluZzEwMGNsdXN0ZXIxMDA"),
    ("record100cluster100", "cmVjb3JkMTAwY2x1c3RlcjEwMA"),
    ("record100mirror100", "cmVjb3JkMTAwbWlycm9yMTAw"),
    ("record100filter100", "cmVjb3JkMTAwZmlsdGVyMTAw"),
    ("record100ranking100", "cmVjb3JkMTAwcmFua2luZzEwMA"),
    ("candle100ranking100", "Y2FuZGxlMTAwcmFua2luZzEwMA"),
    ("candle100encoding100", "Y2FuZGxlMTAwZW5jb2RpbmcxMDA"),
    ("candle100mapping100", "Y2FuZGxlMTAwbWFwcGluZzEwMA"),
    ("candle100record100", "Y2FuZGxlMTAwcmVjb3JkMTAw"),
    ("thread100record100", "dGhyZWFkMTAwcmVjb3JkMTAw"),
    ("thread100candle100", "dGhyZWFkMTAwY2FuZGxlMTAw"),
    ("thread100thread100", "dGhyZWFkMTAwdGhyZWFkMTAw"),
    ("thread100kitten100", "dGhyZWFkMTAwa2l0dGVuMTAw"),
    (
        "round 100: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTAwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 100: agentuniverse is a framework for multi agents",
        "cm91bmQgMTAwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 100: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTAwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 100: the processor reads the record then stops",
        "cm91bmQgMTAwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 100: a worker pulls the next task from the queue",
        "cm91bmQgMTAwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 100: signals travel through the network layer",
        "cm91bmQgMTAwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 100: the gateway routes each request by policy",
        "cm91bmQgMTAwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 100: memory grows until the buffer is full",
        "cm91bmQgMTAwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 100: the cluster mirrors every packet twice",
        "cm91bmQgMTAwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 100: ranking uses tokens learned from the corpus",
        "cm91bmQgMTAwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 100: a long session ends when the candle dies",
        "cm91bmQgMTAwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 100: encode the prompt then map the result",
        "cm91bmQgMTAwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 100: the kernel wakes the worker at dawn",
        "cm91bmQgMTAwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 100: service latency drops after the patch",
        "cm91bmQgMTAwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 100: the library caches every vector it sees",
        "cm91bmQgMTAwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 100: agents argue then the debate resolves",
        "cm91bmQgMTAwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 100: the filter keeps only strong matches",
        "cm91bmQgMTAwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 100: the model answers with a short reply",
        "cm91bmQgMTAwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 100: the recorder stores the reasoning trace",
        "cm91bmQgMTAwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 100: the angel watches the processor run",
        "cm91bmQgMTAwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 100: angle of the vector decides the match",
        "cm91bmQgMTAwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 100: the candle burns twice as long at night",
        "cm91bmQgMTAwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 100: a mirror of the universe in one line",
        "cm91bmQgMTAwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 100: the queue drains before the storm", "cm91bmQgMTAwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
