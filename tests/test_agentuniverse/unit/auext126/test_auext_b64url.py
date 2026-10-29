"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten126kitten126", "a2l0dGVuMTI2a2l0dGVuMTI2"),
    ("kitten126sitting126", "a2l0dGVuMTI2c2l0dGluZzEyNg"),
    ("kitten126agent126", "a2l0dGVuMTI2YWdlbnQxMjY"),
    ("kitten126angle126", "a2l0dGVuMTI2YW5nbGUxMjY"),
    ("sitting126angle126", "c2l0dGluZzEyNmFuZ2xlMTI2"),
    ("sitting126universe126", "c2l0dGluZzEyNnVuaXZlcnNlMTI2"),
    ("sitting126memory126", "c2l0dGluZzEyNm1lbW9yeTEyNg"),
    ("sitting126stream126", "c2l0dGluZzEyNnN0cmVhbTEyNg"),
    ("agent126stream126", "YWdlbnQxMjZzdHJlYW0xMjY"),
    ("agent126context126", "YWdlbnQxMjZjb250ZXh0MTI2"),
    ("agent126knowledge126", "YWdlbnQxMjZrbm93bGVkZ2UxMjY"),
    ("agent126vector126", "YWdlbnQxMjZ2ZWN0b3IxMjY"),
    ("angle126vector126", "YW5nbGUxMjZ2ZWN0b3IxMjY"),
    ("angle126processor126", "YW5nbGUxMjZwcm9jZXNzb3IxMjY"),
    ("angle126reasoning126", "YW5nbGUxMjZyZWFzb25pbmcxMjY"),
    ("angle126machine126", "YW5nbGUxMjZtYWNoaW5lMTI2"),
    ("universe126machine126", "dW5pdmVyc2UxMjZtYWNoaW5lMTI2"),
    ("universe126learning126", "dW5pdmVyc2UxMjZsZWFybmluZzEyNg"),
    ("universe126model126", "dW5pdmVyc2UxMjZtb2RlbDEyNg"),
    ("universe126token126", "dW5pdmVyc2UxMjZ0b2tlbjEyNg"),
    ("memory126token126", "bWVtb3J5MTI2dG9rZW4xMjY"),
    ("memory126prompt126", "bWVtb3J5MTI2cHJvbXB0MTI2"),
    ("memory126session126", "bWVtb3J5MTI2c2Vzc2lvbjEyNg"),
    ("memory126library126", "bWVtb3J5MTI2bGlicmFyeTEyNg"),
    ("stream126library126", "c3RyZWFtMTI2bGlicmFyeTEyNg"),
    ("stream126service126", "c3RyZWFtMTI2c2VydmljZTEyNg"),
    ("stream126gateway126", "c3RyZWFtMTI2Z2F0ZXdheTEyNg"),
    ("stream126storage126", "c3RyZWFtMTI2c3RvcmFnZTEyNg"),
    ("context126storage126", "Y29udGV4dDEyNnN0b3JhZ2UxMjY"),
    ("context126network126", "Y29udGV4dDEyNm5ldHdvcmsxMjY"),
    ("context126latency126", "Y29udGV4dDEyNmxhdGVuY3kxMjY"),
    ("context126buffer126", "Y29udGV4dDEyNmJ1ZmZlcjEyNg"),
    ("knowledge126buffer126", "a25vd2xlZGdlMTI2YnVmZmVyMTI2"),
    ("knowledge126queue126", "a25vd2xlZGdlMTI2cXVldWUxMjY"),
    ("knowledge126worker126", "a25vd2xlZGdlMTI2d29ya2VyMTI2"),
    ("knowledge126kernel126", "a25vd2xlZGdlMTI2a2VybmVsMTI2"),
    ("vector126kernel126", "dmVjdG9yMTI2a2VybmVsMTI2"),
    ("vector126signal126", "dmVjdG9yMTI2c2lnbmFsMTI2"),
    ("vector126packet126", "dmVjdG9yMTI2cGFja2V0MTI2"),
    ("vector126router126", "dmVjdG9yMTI2cm91dGVyMTI2"),
    ("processor126router126", "cHJvY2Vzc29yMTI2cm91dGVyMTI2"),
    ("processor126cluster126", "cHJvY2Vzc29yMTI2Y2x1c3RlcjEyNg"),
    ("processor126mirror126", "cHJvY2Vzc29yMTI2bWlycm9yMTI2"),
    ("processor126filter126", "cHJvY2Vzc29yMTI2ZmlsdGVyMTI2"),
    ("reasoning126filter126", "cmVhc29uaW5nMTI2ZmlsdGVyMTI2"),
    ("reasoning126ranking126", "cmVhc29uaW5nMTI2cmFua2luZzEyNg"),
    ("reasoning126encoding126", "cmVhc29uaW5nMTI2ZW5jb2RpbmcxMjY"),
    ("reasoning126mapping126", "cmVhc29uaW5nMTI2bWFwcGluZzEyNg"),
    ("machine126mapping126", "bWFjaGluZTEyNm1hcHBpbmcxMjY"),
    ("machine126record126", "bWFjaGluZTEyNnJlY29yZDEyNg"),
    ("machine126candle126", "bWFjaGluZTEyNmNhbmRsZTEyNg"),
    ("machine126thread126", "bWFjaGluZTEyNnRocmVhZDEyNg"),
    ("learning126thread126", "bGVhcm5pbmcxMjZ0aHJlYWQxMjY"),
    ("learning126kitten126", "bGVhcm5pbmcxMjZraXR0ZW4xMjY"),
    ("learning126sitting126", "bGVhcm5pbmcxMjZzaXR0aW5nMTI2"),
    ("learning126agent126", "bGVhcm5pbmcxMjZhZ2VudDEyNg"),
    ("model126agent126", "bW9kZWwxMjZhZ2VudDEyNg"),
    ("model126angle126", "bW9kZWwxMjZhbmdsZTEyNg"),
    ("model126universe126", "bW9kZWwxMjZ1bml2ZXJzZTEyNg"),
    ("model126memory126", "bW9kZWwxMjZtZW1vcnkxMjY"),
    ("token126memory126", "dG9rZW4xMjZtZW1vcnkxMjY"),
    ("token126stream126", "dG9rZW4xMjZzdHJlYW0xMjY"),
    ("token126context126", "dG9rZW4xMjZjb250ZXh0MTI2"),
    ("token126knowledge126", "dG9rZW4xMjZrbm93bGVkZ2UxMjY"),
    ("prompt126knowledge126", "cHJvbXB0MTI2a25vd2xlZGdlMTI2"),
    ("prompt126vector126", "cHJvbXB0MTI2dmVjdG9yMTI2"),
    ("prompt126processor126", "cHJvbXB0MTI2cHJvY2Vzc29yMTI2"),
    ("prompt126reasoning126", "cHJvbXB0MTI2cmVhc29uaW5nMTI2"),
    ("session126reasoning126", "c2Vzc2lvbjEyNnJlYXNvbmluZzEyNg"),
    ("session126machine126", "c2Vzc2lvbjEyNm1hY2hpbmUxMjY"),
    ("session126learning126", "c2Vzc2lvbjEyNmxlYXJuaW5nMTI2"),
    ("session126model126", "c2Vzc2lvbjEyNm1vZGVsMTI2"),
    ("library126model126", "bGlicmFyeTEyNm1vZGVsMTI2"),
    ("library126token126", "bGlicmFyeTEyNnRva2VuMTI2"),
    ("library126prompt126", "bGlicmFyeTEyNnByb21wdDEyNg"),
    ("library126session126", "bGlicmFyeTEyNnNlc3Npb24xMjY"),
    ("service126session126", "c2VydmljZTEyNnNlc3Npb24xMjY"),
    ("service126library126", "c2VydmljZTEyNmxpYnJhcnkxMjY"),
    ("service126service126", "c2VydmljZTEyNnNlcnZpY2UxMjY"),
    ("service126gateway126", "c2VydmljZTEyNmdhdGV3YXkxMjY"),
    ("gateway126gateway126", "Z2F0ZXdheTEyNmdhdGV3YXkxMjY"),
    ("gateway126storage126", "Z2F0ZXdheTEyNnN0b3JhZ2UxMjY"),
    ("gateway126network126", "Z2F0ZXdheTEyNm5ldHdvcmsxMjY"),
    ("gateway126latency126", "Z2F0ZXdheTEyNmxhdGVuY3kxMjY"),
    ("storage126latency126", "c3RvcmFnZTEyNmxhdGVuY3kxMjY"),
    ("storage126buffer126", "c3RvcmFnZTEyNmJ1ZmZlcjEyNg"),
    ("storage126queue126", "c3RvcmFnZTEyNnF1ZXVlMTI2"),
    ("storage126worker126", "c3RvcmFnZTEyNndvcmtlcjEyNg"),
    ("network126worker126", "bmV0d29yazEyNndvcmtlcjEyNg"),
    ("network126kernel126", "bmV0d29yazEyNmtlcm5lbDEyNg"),
    ("network126signal126", "bmV0d29yazEyNnNpZ25hbDEyNg"),
    ("network126packet126", "bmV0d29yazEyNnBhY2tldDEyNg"),
    ("latency126packet126", "bGF0ZW5jeTEyNnBhY2tldDEyNg"),
    ("latency126router126", "bGF0ZW5jeTEyNnJvdXRlcjEyNg"),
    ("latency126cluster126", "bGF0ZW5jeTEyNmNsdXN0ZXIxMjY"),
    ("latency126mirror126", "bGF0ZW5jeTEyNm1pcnJvcjEyNg"),
    ("buffer126mirror126", "YnVmZmVyMTI2bWlycm9yMTI2"),
    ("buffer126filter126", "YnVmZmVyMTI2ZmlsdGVyMTI2"),
    ("buffer126ranking126", "YnVmZmVyMTI2cmFua2luZzEyNg"),
    ("buffer126encoding126", "YnVmZmVyMTI2ZW5jb2RpbmcxMjY"),
    ("queue126encoding126", "cXVldWUxMjZlbmNvZGluZzEyNg"),
    ("queue126mapping126", "cXVldWUxMjZtYXBwaW5nMTI2"),
    ("queue126record126", "cXVldWUxMjZyZWNvcmQxMjY"),
    ("queue126candle126", "cXVldWUxMjZjYW5kbGUxMjY"),
    ("worker126candle126", "d29ya2VyMTI2Y2FuZGxlMTI2"),
    ("worker126thread126", "d29ya2VyMTI2dGhyZWFkMTI2"),
    ("worker126kitten126", "d29ya2VyMTI2a2l0dGVuMTI2"),
    ("worker126sitting126", "d29ya2VyMTI2c2l0dGluZzEyNg"),
    ("kernel126sitting126", "a2VybmVsMTI2c2l0dGluZzEyNg"),
    ("kernel126agent126", "a2VybmVsMTI2YWdlbnQxMjY"),
    ("kernel126angle126", "a2VybmVsMTI2YW5nbGUxMjY"),
    ("kernel126universe126", "a2VybmVsMTI2dW5pdmVyc2UxMjY"),
    ("signal126universe126", "c2lnbmFsMTI2dW5pdmVyc2UxMjY"),
    ("signal126memory126", "c2lnbmFsMTI2bWVtb3J5MTI2"),
    ("signal126stream126", "c2lnbmFsMTI2c3RyZWFtMTI2"),
    ("signal126context126", "c2lnbmFsMTI2Y29udGV4dDEyNg"),
    ("packet126context126", "cGFja2V0MTI2Y29udGV4dDEyNg"),
    ("packet126knowledge126", "cGFja2V0MTI2a25vd2xlZGdlMTI2"),
    ("packet126vector126", "cGFja2V0MTI2dmVjdG9yMTI2"),
    ("packet126processor126", "cGFja2V0MTI2cHJvY2Vzc29yMTI2"),
    ("router126processor126", "cm91dGVyMTI2cHJvY2Vzc29yMTI2"),
    ("router126reasoning126", "cm91dGVyMTI2cmVhc29uaW5nMTI2"),
    ("router126machine126", "cm91dGVyMTI2bWFjaGluZTEyNg"),
    ("router126learning126", "cm91dGVyMTI2bGVhcm5pbmcxMjY"),
    ("cluster126learning126", "Y2x1c3RlcjEyNmxlYXJuaW5nMTI2"),
    ("cluster126model126", "Y2x1c3RlcjEyNm1vZGVsMTI2"),
    ("cluster126token126", "Y2x1c3RlcjEyNnRva2VuMTI2"),
    ("cluster126prompt126", "Y2x1c3RlcjEyNnByb21wdDEyNg"),
    ("mirror126prompt126", "bWlycm9yMTI2cHJvbXB0MTI2"),
    ("mirror126session126", "bWlycm9yMTI2c2Vzc2lvbjEyNg"),
    ("mirror126library126", "bWlycm9yMTI2bGlicmFyeTEyNg"),
    ("mirror126service126", "bWlycm9yMTI2c2VydmljZTEyNg"),
    ("filter126service126", "ZmlsdGVyMTI2c2VydmljZTEyNg"),
    ("filter126gateway126", "ZmlsdGVyMTI2Z2F0ZXdheTEyNg"),
    ("filter126storage126", "ZmlsdGVyMTI2c3RvcmFnZTEyNg"),
    ("filter126network126", "ZmlsdGVyMTI2bmV0d29yazEyNg"),
    ("ranking126network126", "cmFua2luZzEyNm5ldHdvcmsxMjY"),
    ("ranking126latency126", "cmFua2luZzEyNmxhdGVuY3kxMjY"),
    ("ranking126buffer126", "cmFua2luZzEyNmJ1ZmZlcjEyNg"),
    ("ranking126queue126", "cmFua2luZzEyNnF1ZXVlMTI2"),
    ("encoding126queue126", "ZW5jb2RpbmcxMjZxdWV1ZTEyNg"),
    ("encoding126worker126", "ZW5jb2RpbmcxMjZ3b3JrZXIxMjY"),
    ("encoding126kernel126", "ZW5jb2RpbmcxMjZrZXJuZWwxMjY"),
    ("encoding126signal126", "ZW5jb2RpbmcxMjZzaWduYWwxMjY"),
    ("mapping126signal126", "bWFwcGluZzEyNnNpZ25hbDEyNg"),
    ("mapping126packet126", "bWFwcGluZzEyNnBhY2tldDEyNg"),
    ("mapping126router126", "bWFwcGluZzEyNnJvdXRlcjEyNg"),
    ("mapping126cluster126", "bWFwcGluZzEyNmNsdXN0ZXIxMjY"),
    ("record126cluster126", "cmVjb3JkMTI2Y2x1c3RlcjEyNg"),
    ("record126mirror126", "cmVjb3JkMTI2bWlycm9yMTI2"),
    ("record126filter126", "cmVjb3JkMTI2ZmlsdGVyMTI2"),
    ("record126ranking126", "cmVjb3JkMTI2cmFua2luZzEyNg"),
    ("candle126ranking126", "Y2FuZGxlMTI2cmFua2luZzEyNg"),
    ("candle126encoding126", "Y2FuZGxlMTI2ZW5jb2RpbmcxMjY"),
    ("candle126mapping126", "Y2FuZGxlMTI2bWFwcGluZzEyNg"),
    ("candle126record126", "Y2FuZGxlMTI2cmVjb3JkMTI2"),
    ("thread126record126", "dGhyZWFkMTI2cmVjb3JkMTI2"),
    ("thread126candle126", "dGhyZWFkMTI2Y2FuZGxlMTI2"),
    ("thread126thread126", "dGhyZWFkMTI2dGhyZWFkMTI2"),
    ("thread126kitten126", "dGhyZWFkMTI2a2l0dGVuMTI2"),
    (
        "round 126: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTI2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 126: agentuniverse is a framework for multi agents",
        "cm91bmQgMTI2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 126: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTI2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 126: the processor reads the record then stops",
        "cm91bmQgMTI2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 126: a worker pulls the next task from the queue",
        "cm91bmQgMTI2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 126: signals travel through the network layer",
        "cm91bmQgMTI2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 126: the gateway routes each request by policy",
        "cm91bmQgMTI2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 126: memory grows until the buffer is full",
        "cm91bmQgMTI2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 126: the cluster mirrors every packet twice",
        "cm91bmQgMTI2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 126: ranking uses tokens learned from the corpus",
        "cm91bmQgMTI2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 126: a long session ends when the candle dies",
        "cm91bmQgMTI2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 126: encode the prompt then map the result",
        "cm91bmQgMTI2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 126: the kernel wakes the worker at dawn",
        "cm91bmQgMTI2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 126: service latency drops after the patch",
        "cm91bmQgMTI2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 126: the library caches every vector it sees",
        "cm91bmQgMTI2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 126: agents argue then the debate resolves",
        "cm91bmQgMTI2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 126: the filter keeps only strong matches",
        "cm91bmQgMTI2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 126: the model answers with a short reply",
        "cm91bmQgMTI2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 126: the recorder stores the reasoning trace",
        "cm91bmQgMTI2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 126: the angel watches the processor run",
        "cm91bmQgMTI2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 126: angle of the vector decides the match",
        "cm91bmQgMTI2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 126: the candle burns twice as long at night",
        "cm91bmQgMTI2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 126: a mirror of the universe in one line",
        "cm91bmQgMTI2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 126: the queue drains before the storm", "cm91bmQgMTI2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
