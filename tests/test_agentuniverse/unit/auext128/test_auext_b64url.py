"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten128kitten128", "a2l0dGVuMTI4a2l0dGVuMTI4"),
    ("kitten128sitting128", "a2l0dGVuMTI4c2l0dGluZzEyOA"),
    ("kitten128agent128", "a2l0dGVuMTI4YWdlbnQxMjg"),
    ("kitten128angle128", "a2l0dGVuMTI4YW5nbGUxMjg"),
    ("sitting128angle128", "c2l0dGluZzEyOGFuZ2xlMTI4"),
    ("sitting128universe128", "c2l0dGluZzEyOHVuaXZlcnNlMTI4"),
    ("sitting128memory128", "c2l0dGluZzEyOG1lbW9yeTEyOA"),
    ("sitting128stream128", "c2l0dGluZzEyOHN0cmVhbTEyOA"),
    ("agent128stream128", "YWdlbnQxMjhzdHJlYW0xMjg"),
    ("agent128context128", "YWdlbnQxMjhjb250ZXh0MTI4"),
    ("agent128knowledge128", "YWdlbnQxMjhrbm93bGVkZ2UxMjg"),
    ("agent128vector128", "YWdlbnQxMjh2ZWN0b3IxMjg"),
    ("angle128vector128", "YW5nbGUxMjh2ZWN0b3IxMjg"),
    ("angle128processor128", "YW5nbGUxMjhwcm9jZXNzb3IxMjg"),
    ("angle128reasoning128", "YW5nbGUxMjhyZWFzb25pbmcxMjg"),
    ("angle128machine128", "YW5nbGUxMjhtYWNoaW5lMTI4"),
    ("universe128machine128", "dW5pdmVyc2UxMjhtYWNoaW5lMTI4"),
    ("universe128learning128", "dW5pdmVyc2UxMjhsZWFybmluZzEyOA"),
    ("universe128model128", "dW5pdmVyc2UxMjhtb2RlbDEyOA"),
    ("universe128token128", "dW5pdmVyc2UxMjh0b2tlbjEyOA"),
    ("memory128token128", "bWVtb3J5MTI4dG9rZW4xMjg"),
    ("memory128prompt128", "bWVtb3J5MTI4cHJvbXB0MTI4"),
    ("memory128session128", "bWVtb3J5MTI4c2Vzc2lvbjEyOA"),
    ("memory128library128", "bWVtb3J5MTI4bGlicmFyeTEyOA"),
    ("stream128library128", "c3RyZWFtMTI4bGlicmFyeTEyOA"),
    ("stream128service128", "c3RyZWFtMTI4c2VydmljZTEyOA"),
    ("stream128gateway128", "c3RyZWFtMTI4Z2F0ZXdheTEyOA"),
    ("stream128storage128", "c3RyZWFtMTI4c3RvcmFnZTEyOA"),
    ("context128storage128", "Y29udGV4dDEyOHN0b3JhZ2UxMjg"),
    ("context128network128", "Y29udGV4dDEyOG5ldHdvcmsxMjg"),
    ("context128latency128", "Y29udGV4dDEyOGxhdGVuY3kxMjg"),
    ("context128buffer128", "Y29udGV4dDEyOGJ1ZmZlcjEyOA"),
    ("knowledge128buffer128", "a25vd2xlZGdlMTI4YnVmZmVyMTI4"),
    ("knowledge128queue128", "a25vd2xlZGdlMTI4cXVldWUxMjg"),
    ("knowledge128worker128", "a25vd2xlZGdlMTI4d29ya2VyMTI4"),
    ("knowledge128kernel128", "a25vd2xlZGdlMTI4a2VybmVsMTI4"),
    ("vector128kernel128", "dmVjdG9yMTI4a2VybmVsMTI4"),
    ("vector128signal128", "dmVjdG9yMTI4c2lnbmFsMTI4"),
    ("vector128packet128", "dmVjdG9yMTI4cGFja2V0MTI4"),
    ("vector128router128", "dmVjdG9yMTI4cm91dGVyMTI4"),
    ("processor128router128", "cHJvY2Vzc29yMTI4cm91dGVyMTI4"),
    ("processor128cluster128", "cHJvY2Vzc29yMTI4Y2x1c3RlcjEyOA"),
    ("processor128mirror128", "cHJvY2Vzc29yMTI4bWlycm9yMTI4"),
    ("processor128filter128", "cHJvY2Vzc29yMTI4ZmlsdGVyMTI4"),
    ("reasoning128filter128", "cmVhc29uaW5nMTI4ZmlsdGVyMTI4"),
    ("reasoning128ranking128", "cmVhc29uaW5nMTI4cmFua2luZzEyOA"),
    ("reasoning128encoding128", "cmVhc29uaW5nMTI4ZW5jb2RpbmcxMjg"),
    ("reasoning128mapping128", "cmVhc29uaW5nMTI4bWFwcGluZzEyOA"),
    ("machine128mapping128", "bWFjaGluZTEyOG1hcHBpbmcxMjg"),
    ("machine128record128", "bWFjaGluZTEyOHJlY29yZDEyOA"),
    ("machine128candle128", "bWFjaGluZTEyOGNhbmRsZTEyOA"),
    ("machine128thread128", "bWFjaGluZTEyOHRocmVhZDEyOA"),
    ("learning128thread128", "bGVhcm5pbmcxMjh0aHJlYWQxMjg"),
    ("learning128kitten128", "bGVhcm5pbmcxMjhraXR0ZW4xMjg"),
    ("learning128sitting128", "bGVhcm5pbmcxMjhzaXR0aW5nMTI4"),
    ("learning128agent128", "bGVhcm5pbmcxMjhhZ2VudDEyOA"),
    ("model128agent128", "bW9kZWwxMjhhZ2VudDEyOA"),
    ("model128angle128", "bW9kZWwxMjhhbmdsZTEyOA"),
    ("model128universe128", "bW9kZWwxMjh1bml2ZXJzZTEyOA"),
    ("model128memory128", "bW9kZWwxMjhtZW1vcnkxMjg"),
    ("token128memory128", "dG9rZW4xMjhtZW1vcnkxMjg"),
    ("token128stream128", "dG9rZW4xMjhzdHJlYW0xMjg"),
    ("token128context128", "dG9rZW4xMjhjb250ZXh0MTI4"),
    ("token128knowledge128", "dG9rZW4xMjhrbm93bGVkZ2UxMjg"),
    ("prompt128knowledge128", "cHJvbXB0MTI4a25vd2xlZGdlMTI4"),
    ("prompt128vector128", "cHJvbXB0MTI4dmVjdG9yMTI4"),
    ("prompt128processor128", "cHJvbXB0MTI4cHJvY2Vzc29yMTI4"),
    ("prompt128reasoning128", "cHJvbXB0MTI4cmVhc29uaW5nMTI4"),
    ("session128reasoning128", "c2Vzc2lvbjEyOHJlYXNvbmluZzEyOA"),
    ("session128machine128", "c2Vzc2lvbjEyOG1hY2hpbmUxMjg"),
    ("session128learning128", "c2Vzc2lvbjEyOGxlYXJuaW5nMTI4"),
    ("session128model128", "c2Vzc2lvbjEyOG1vZGVsMTI4"),
    ("library128model128", "bGlicmFyeTEyOG1vZGVsMTI4"),
    ("library128token128", "bGlicmFyeTEyOHRva2VuMTI4"),
    ("library128prompt128", "bGlicmFyeTEyOHByb21wdDEyOA"),
    ("library128session128", "bGlicmFyeTEyOHNlc3Npb24xMjg"),
    ("service128session128", "c2VydmljZTEyOHNlc3Npb24xMjg"),
    ("service128library128", "c2VydmljZTEyOGxpYnJhcnkxMjg"),
    ("service128service128", "c2VydmljZTEyOHNlcnZpY2UxMjg"),
    ("service128gateway128", "c2VydmljZTEyOGdhdGV3YXkxMjg"),
    ("gateway128gateway128", "Z2F0ZXdheTEyOGdhdGV3YXkxMjg"),
    ("gateway128storage128", "Z2F0ZXdheTEyOHN0b3JhZ2UxMjg"),
    ("gateway128network128", "Z2F0ZXdheTEyOG5ldHdvcmsxMjg"),
    ("gateway128latency128", "Z2F0ZXdheTEyOGxhdGVuY3kxMjg"),
    ("storage128latency128", "c3RvcmFnZTEyOGxhdGVuY3kxMjg"),
    ("storage128buffer128", "c3RvcmFnZTEyOGJ1ZmZlcjEyOA"),
    ("storage128queue128", "c3RvcmFnZTEyOHF1ZXVlMTI4"),
    ("storage128worker128", "c3RvcmFnZTEyOHdvcmtlcjEyOA"),
    ("network128worker128", "bmV0d29yazEyOHdvcmtlcjEyOA"),
    ("network128kernel128", "bmV0d29yazEyOGtlcm5lbDEyOA"),
    ("network128signal128", "bmV0d29yazEyOHNpZ25hbDEyOA"),
    ("network128packet128", "bmV0d29yazEyOHBhY2tldDEyOA"),
    ("latency128packet128", "bGF0ZW5jeTEyOHBhY2tldDEyOA"),
    ("latency128router128", "bGF0ZW5jeTEyOHJvdXRlcjEyOA"),
    ("latency128cluster128", "bGF0ZW5jeTEyOGNsdXN0ZXIxMjg"),
    ("latency128mirror128", "bGF0ZW5jeTEyOG1pcnJvcjEyOA"),
    ("buffer128mirror128", "YnVmZmVyMTI4bWlycm9yMTI4"),
    ("buffer128filter128", "YnVmZmVyMTI4ZmlsdGVyMTI4"),
    ("buffer128ranking128", "YnVmZmVyMTI4cmFua2luZzEyOA"),
    ("buffer128encoding128", "YnVmZmVyMTI4ZW5jb2RpbmcxMjg"),
    ("queue128encoding128", "cXVldWUxMjhlbmNvZGluZzEyOA"),
    ("queue128mapping128", "cXVldWUxMjhtYXBwaW5nMTI4"),
    ("queue128record128", "cXVldWUxMjhyZWNvcmQxMjg"),
    ("queue128candle128", "cXVldWUxMjhjYW5kbGUxMjg"),
    ("worker128candle128", "d29ya2VyMTI4Y2FuZGxlMTI4"),
    ("worker128thread128", "d29ya2VyMTI4dGhyZWFkMTI4"),
    ("worker128kitten128", "d29ya2VyMTI4a2l0dGVuMTI4"),
    ("worker128sitting128", "d29ya2VyMTI4c2l0dGluZzEyOA"),
    ("kernel128sitting128", "a2VybmVsMTI4c2l0dGluZzEyOA"),
    ("kernel128agent128", "a2VybmVsMTI4YWdlbnQxMjg"),
    ("kernel128angle128", "a2VybmVsMTI4YW5nbGUxMjg"),
    ("kernel128universe128", "a2VybmVsMTI4dW5pdmVyc2UxMjg"),
    ("signal128universe128", "c2lnbmFsMTI4dW5pdmVyc2UxMjg"),
    ("signal128memory128", "c2lnbmFsMTI4bWVtb3J5MTI4"),
    ("signal128stream128", "c2lnbmFsMTI4c3RyZWFtMTI4"),
    ("signal128context128", "c2lnbmFsMTI4Y29udGV4dDEyOA"),
    ("packet128context128", "cGFja2V0MTI4Y29udGV4dDEyOA"),
    ("packet128knowledge128", "cGFja2V0MTI4a25vd2xlZGdlMTI4"),
    ("packet128vector128", "cGFja2V0MTI4dmVjdG9yMTI4"),
    ("packet128processor128", "cGFja2V0MTI4cHJvY2Vzc29yMTI4"),
    ("router128processor128", "cm91dGVyMTI4cHJvY2Vzc29yMTI4"),
    ("router128reasoning128", "cm91dGVyMTI4cmVhc29uaW5nMTI4"),
    ("router128machine128", "cm91dGVyMTI4bWFjaGluZTEyOA"),
    ("router128learning128", "cm91dGVyMTI4bGVhcm5pbmcxMjg"),
    ("cluster128learning128", "Y2x1c3RlcjEyOGxlYXJuaW5nMTI4"),
    ("cluster128model128", "Y2x1c3RlcjEyOG1vZGVsMTI4"),
    ("cluster128token128", "Y2x1c3RlcjEyOHRva2VuMTI4"),
    ("cluster128prompt128", "Y2x1c3RlcjEyOHByb21wdDEyOA"),
    ("mirror128prompt128", "bWlycm9yMTI4cHJvbXB0MTI4"),
    ("mirror128session128", "bWlycm9yMTI4c2Vzc2lvbjEyOA"),
    ("mirror128library128", "bWlycm9yMTI4bGlicmFyeTEyOA"),
    ("mirror128service128", "bWlycm9yMTI4c2VydmljZTEyOA"),
    ("filter128service128", "ZmlsdGVyMTI4c2VydmljZTEyOA"),
    ("filter128gateway128", "ZmlsdGVyMTI4Z2F0ZXdheTEyOA"),
    ("filter128storage128", "ZmlsdGVyMTI4c3RvcmFnZTEyOA"),
    ("filter128network128", "ZmlsdGVyMTI4bmV0d29yazEyOA"),
    ("ranking128network128", "cmFua2luZzEyOG5ldHdvcmsxMjg"),
    ("ranking128latency128", "cmFua2luZzEyOGxhdGVuY3kxMjg"),
    ("ranking128buffer128", "cmFua2luZzEyOGJ1ZmZlcjEyOA"),
    ("ranking128queue128", "cmFua2luZzEyOHF1ZXVlMTI4"),
    ("encoding128queue128", "ZW5jb2RpbmcxMjhxdWV1ZTEyOA"),
    ("encoding128worker128", "ZW5jb2RpbmcxMjh3b3JrZXIxMjg"),
    ("encoding128kernel128", "ZW5jb2RpbmcxMjhrZXJuZWwxMjg"),
    ("encoding128signal128", "ZW5jb2RpbmcxMjhzaWduYWwxMjg"),
    ("mapping128signal128", "bWFwcGluZzEyOHNpZ25hbDEyOA"),
    ("mapping128packet128", "bWFwcGluZzEyOHBhY2tldDEyOA"),
    ("mapping128router128", "bWFwcGluZzEyOHJvdXRlcjEyOA"),
    ("mapping128cluster128", "bWFwcGluZzEyOGNsdXN0ZXIxMjg"),
    ("record128cluster128", "cmVjb3JkMTI4Y2x1c3RlcjEyOA"),
    ("record128mirror128", "cmVjb3JkMTI4bWlycm9yMTI4"),
    ("record128filter128", "cmVjb3JkMTI4ZmlsdGVyMTI4"),
    ("record128ranking128", "cmVjb3JkMTI4cmFua2luZzEyOA"),
    ("candle128ranking128", "Y2FuZGxlMTI4cmFua2luZzEyOA"),
    ("candle128encoding128", "Y2FuZGxlMTI4ZW5jb2RpbmcxMjg"),
    ("candle128mapping128", "Y2FuZGxlMTI4bWFwcGluZzEyOA"),
    ("candle128record128", "Y2FuZGxlMTI4cmVjb3JkMTI4"),
    ("thread128record128", "dGhyZWFkMTI4cmVjb3JkMTI4"),
    ("thread128candle128", "dGhyZWFkMTI4Y2FuZGxlMTI4"),
    ("thread128thread128", "dGhyZWFkMTI4dGhyZWFkMTI4"),
    ("thread128kitten128", "dGhyZWFkMTI4a2l0dGVuMTI4"),
    (
        "round 128: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTI4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 128: agentuniverse is a framework for multi agents",
        "cm91bmQgMTI4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 128: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTI4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 128: the processor reads the record then stops",
        "cm91bmQgMTI4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 128: a worker pulls the next task from the queue",
        "cm91bmQgMTI4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 128: signals travel through the network layer",
        "cm91bmQgMTI4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 128: the gateway routes each request by policy",
        "cm91bmQgMTI4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 128: memory grows until the buffer is full",
        "cm91bmQgMTI4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 128: the cluster mirrors every packet twice",
        "cm91bmQgMTI4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 128: ranking uses tokens learned from the corpus",
        "cm91bmQgMTI4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 128: a long session ends when the candle dies",
        "cm91bmQgMTI4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 128: encode the prompt then map the result",
        "cm91bmQgMTI4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 128: the kernel wakes the worker at dawn",
        "cm91bmQgMTI4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 128: service latency drops after the patch",
        "cm91bmQgMTI4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 128: the library caches every vector it sees",
        "cm91bmQgMTI4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 128: agents argue then the debate resolves",
        "cm91bmQgMTI4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 128: the filter keeps only strong matches",
        "cm91bmQgMTI4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 128: the model answers with a short reply",
        "cm91bmQgMTI4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 128: the recorder stores the reasoning trace",
        "cm91bmQgMTI4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 128: the angel watches the processor run",
        "cm91bmQgMTI4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 128: angle of the vector decides the match",
        "cm91bmQgMTI4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 128: the candle burns twice as long at night",
        "cm91bmQgMTI4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 128: a mirror of the universe in one line",
        "cm91bmQgMTI4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 128: the queue drains before the storm", "cm91bmQgMTI4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
