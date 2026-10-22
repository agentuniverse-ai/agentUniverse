"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten136kitten136", "a2l0dGVuMTM2a2l0dGVuMTM2"),
    ("kitten136sitting136", "a2l0dGVuMTM2c2l0dGluZzEzNg"),
    ("kitten136agent136", "a2l0dGVuMTM2YWdlbnQxMzY"),
    ("kitten136angle136", "a2l0dGVuMTM2YW5nbGUxMzY"),
    ("sitting136angle136", "c2l0dGluZzEzNmFuZ2xlMTM2"),
    ("sitting136universe136", "c2l0dGluZzEzNnVuaXZlcnNlMTM2"),
    ("sitting136memory136", "c2l0dGluZzEzNm1lbW9yeTEzNg"),
    ("sitting136stream136", "c2l0dGluZzEzNnN0cmVhbTEzNg"),
    ("agent136stream136", "YWdlbnQxMzZzdHJlYW0xMzY"),
    ("agent136context136", "YWdlbnQxMzZjb250ZXh0MTM2"),
    ("agent136knowledge136", "YWdlbnQxMzZrbm93bGVkZ2UxMzY"),
    ("agent136vector136", "YWdlbnQxMzZ2ZWN0b3IxMzY"),
    ("angle136vector136", "YW5nbGUxMzZ2ZWN0b3IxMzY"),
    ("angle136processor136", "YW5nbGUxMzZwcm9jZXNzb3IxMzY"),
    ("angle136reasoning136", "YW5nbGUxMzZyZWFzb25pbmcxMzY"),
    ("angle136machine136", "YW5nbGUxMzZtYWNoaW5lMTM2"),
    ("universe136machine136", "dW5pdmVyc2UxMzZtYWNoaW5lMTM2"),
    ("universe136learning136", "dW5pdmVyc2UxMzZsZWFybmluZzEzNg"),
    ("universe136model136", "dW5pdmVyc2UxMzZtb2RlbDEzNg"),
    ("universe136token136", "dW5pdmVyc2UxMzZ0b2tlbjEzNg"),
    ("memory136token136", "bWVtb3J5MTM2dG9rZW4xMzY"),
    ("memory136prompt136", "bWVtb3J5MTM2cHJvbXB0MTM2"),
    ("memory136session136", "bWVtb3J5MTM2c2Vzc2lvbjEzNg"),
    ("memory136library136", "bWVtb3J5MTM2bGlicmFyeTEzNg"),
    ("stream136library136", "c3RyZWFtMTM2bGlicmFyeTEzNg"),
    ("stream136service136", "c3RyZWFtMTM2c2VydmljZTEzNg"),
    ("stream136gateway136", "c3RyZWFtMTM2Z2F0ZXdheTEzNg"),
    ("stream136storage136", "c3RyZWFtMTM2c3RvcmFnZTEzNg"),
    ("context136storage136", "Y29udGV4dDEzNnN0b3JhZ2UxMzY"),
    ("context136network136", "Y29udGV4dDEzNm5ldHdvcmsxMzY"),
    ("context136latency136", "Y29udGV4dDEzNmxhdGVuY3kxMzY"),
    ("context136buffer136", "Y29udGV4dDEzNmJ1ZmZlcjEzNg"),
    ("knowledge136buffer136", "a25vd2xlZGdlMTM2YnVmZmVyMTM2"),
    ("knowledge136queue136", "a25vd2xlZGdlMTM2cXVldWUxMzY"),
    ("knowledge136worker136", "a25vd2xlZGdlMTM2d29ya2VyMTM2"),
    ("knowledge136kernel136", "a25vd2xlZGdlMTM2a2VybmVsMTM2"),
    ("vector136kernel136", "dmVjdG9yMTM2a2VybmVsMTM2"),
    ("vector136signal136", "dmVjdG9yMTM2c2lnbmFsMTM2"),
    ("vector136packet136", "dmVjdG9yMTM2cGFja2V0MTM2"),
    ("vector136router136", "dmVjdG9yMTM2cm91dGVyMTM2"),
    ("processor136router136", "cHJvY2Vzc29yMTM2cm91dGVyMTM2"),
    ("processor136cluster136", "cHJvY2Vzc29yMTM2Y2x1c3RlcjEzNg"),
    ("processor136mirror136", "cHJvY2Vzc29yMTM2bWlycm9yMTM2"),
    ("processor136filter136", "cHJvY2Vzc29yMTM2ZmlsdGVyMTM2"),
    ("reasoning136filter136", "cmVhc29uaW5nMTM2ZmlsdGVyMTM2"),
    ("reasoning136ranking136", "cmVhc29uaW5nMTM2cmFua2luZzEzNg"),
    ("reasoning136encoding136", "cmVhc29uaW5nMTM2ZW5jb2RpbmcxMzY"),
    ("reasoning136mapping136", "cmVhc29uaW5nMTM2bWFwcGluZzEzNg"),
    ("machine136mapping136", "bWFjaGluZTEzNm1hcHBpbmcxMzY"),
    ("machine136record136", "bWFjaGluZTEzNnJlY29yZDEzNg"),
    ("machine136candle136", "bWFjaGluZTEzNmNhbmRsZTEzNg"),
    ("machine136thread136", "bWFjaGluZTEzNnRocmVhZDEzNg"),
    ("learning136thread136", "bGVhcm5pbmcxMzZ0aHJlYWQxMzY"),
    ("learning136kitten136", "bGVhcm5pbmcxMzZraXR0ZW4xMzY"),
    ("learning136sitting136", "bGVhcm5pbmcxMzZzaXR0aW5nMTM2"),
    ("learning136agent136", "bGVhcm5pbmcxMzZhZ2VudDEzNg"),
    ("model136agent136", "bW9kZWwxMzZhZ2VudDEzNg"),
    ("model136angle136", "bW9kZWwxMzZhbmdsZTEzNg"),
    ("model136universe136", "bW9kZWwxMzZ1bml2ZXJzZTEzNg"),
    ("model136memory136", "bW9kZWwxMzZtZW1vcnkxMzY"),
    ("token136memory136", "dG9rZW4xMzZtZW1vcnkxMzY"),
    ("token136stream136", "dG9rZW4xMzZzdHJlYW0xMzY"),
    ("token136context136", "dG9rZW4xMzZjb250ZXh0MTM2"),
    ("token136knowledge136", "dG9rZW4xMzZrbm93bGVkZ2UxMzY"),
    ("prompt136knowledge136", "cHJvbXB0MTM2a25vd2xlZGdlMTM2"),
    ("prompt136vector136", "cHJvbXB0MTM2dmVjdG9yMTM2"),
    ("prompt136processor136", "cHJvbXB0MTM2cHJvY2Vzc29yMTM2"),
    ("prompt136reasoning136", "cHJvbXB0MTM2cmVhc29uaW5nMTM2"),
    ("session136reasoning136", "c2Vzc2lvbjEzNnJlYXNvbmluZzEzNg"),
    ("session136machine136", "c2Vzc2lvbjEzNm1hY2hpbmUxMzY"),
    ("session136learning136", "c2Vzc2lvbjEzNmxlYXJuaW5nMTM2"),
    ("session136model136", "c2Vzc2lvbjEzNm1vZGVsMTM2"),
    ("library136model136", "bGlicmFyeTEzNm1vZGVsMTM2"),
    ("library136token136", "bGlicmFyeTEzNnRva2VuMTM2"),
    ("library136prompt136", "bGlicmFyeTEzNnByb21wdDEzNg"),
    ("library136session136", "bGlicmFyeTEzNnNlc3Npb24xMzY"),
    ("service136session136", "c2VydmljZTEzNnNlc3Npb24xMzY"),
    ("service136library136", "c2VydmljZTEzNmxpYnJhcnkxMzY"),
    ("service136service136", "c2VydmljZTEzNnNlcnZpY2UxMzY"),
    ("service136gateway136", "c2VydmljZTEzNmdhdGV3YXkxMzY"),
    ("gateway136gateway136", "Z2F0ZXdheTEzNmdhdGV3YXkxMzY"),
    ("gateway136storage136", "Z2F0ZXdheTEzNnN0b3JhZ2UxMzY"),
    ("gateway136network136", "Z2F0ZXdheTEzNm5ldHdvcmsxMzY"),
    ("gateway136latency136", "Z2F0ZXdheTEzNmxhdGVuY3kxMzY"),
    ("storage136latency136", "c3RvcmFnZTEzNmxhdGVuY3kxMzY"),
    ("storage136buffer136", "c3RvcmFnZTEzNmJ1ZmZlcjEzNg"),
    ("storage136queue136", "c3RvcmFnZTEzNnF1ZXVlMTM2"),
    ("storage136worker136", "c3RvcmFnZTEzNndvcmtlcjEzNg"),
    ("network136worker136", "bmV0d29yazEzNndvcmtlcjEzNg"),
    ("network136kernel136", "bmV0d29yazEzNmtlcm5lbDEzNg"),
    ("network136signal136", "bmV0d29yazEzNnNpZ25hbDEzNg"),
    ("network136packet136", "bmV0d29yazEzNnBhY2tldDEzNg"),
    ("latency136packet136", "bGF0ZW5jeTEzNnBhY2tldDEzNg"),
    ("latency136router136", "bGF0ZW5jeTEzNnJvdXRlcjEzNg"),
    ("latency136cluster136", "bGF0ZW5jeTEzNmNsdXN0ZXIxMzY"),
    ("latency136mirror136", "bGF0ZW5jeTEzNm1pcnJvcjEzNg"),
    ("buffer136mirror136", "YnVmZmVyMTM2bWlycm9yMTM2"),
    ("buffer136filter136", "YnVmZmVyMTM2ZmlsdGVyMTM2"),
    ("buffer136ranking136", "YnVmZmVyMTM2cmFua2luZzEzNg"),
    ("buffer136encoding136", "YnVmZmVyMTM2ZW5jb2RpbmcxMzY"),
    ("queue136encoding136", "cXVldWUxMzZlbmNvZGluZzEzNg"),
    ("queue136mapping136", "cXVldWUxMzZtYXBwaW5nMTM2"),
    ("queue136record136", "cXVldWUxMzZyZWNvcmQxMzY"),
    ("queue136candle136", "cXVldWUxMzZjYW5kbGUxMzY"),
    ("worker136candle136", "d29ya2VyMTM2Y2FuZGxlMTM2"),
    ("worker136thread136", "d29ya2VyMTM2dGhyZWFkMTM2"),
    ("worker136kitten136", "d29ya2VyMTM2a2l0dGVuMTM2"),
    ("worker136sitting136", "d29ya2VyMTM2c2l0dGluZzEzNg"),
    ("kernel136sitting136", "a2VybmVsMTM2c2l0dGluZzEzNg"),
    ("kernel136agent136", "a2VybmVsMTM2YWdlbnQxMzY"),
    ("kernel136angle136", "a2VybmVsMTM2YW5nbGUxMzY"),
    ("kernel136universe136", "a2VybmVsMTM2dW5pdmVyc2UxMzY"),
    ("signal136universe136", "c2lnbmFsMTM2dW5pdmVyc2UxMzY"),
    ("signal136memory136", "c2lnbmFsMTM2bWVtb3J5MTM2"),
    ("signal136stream136", "c2lnbmFsMTM2c3RyZWFtMTM2"),
    ("signal136context136", "c2lnbmFsMTM2Y29udGV4dDEzNg"),
    ("packet136context136", "cGFja2V0MTM2Y29udGV4dDEzNg"),
    ("packet136knowledge136", "cGFja2V0MTM2a25vd2xlZGdlMTM2"),
    ("packet136vector136", "cGFja2V0MTM2dmVjdG9yMTM2"),
    ("packet136processor136", "cGFja2V0MTM2cHJvY2Vzc29yMTM2"),
    ("router136processor136", "cm91dGVyMTM2cHJvY2Vzc29yMTM2"),
    ("router136reasoning136", "cm91dGVyMTM2cmVhc29uaW5nMTM2"),
    ("router136machine136", "cm91dGVyMTM2bWFjaGluZTEzNg"),
    ("router136learning136", "cm91dGVyMTM2bGVhcm5pbmcxMzY"),
    ("cluster136learning136", "Y2x1c3RlcjEzNmxlYXJuaW5nMTM2"),
    ("cluster136model136", "Y2x1c3RlcjEzNm1vZGVsMTM2"),
    ("cluster136token136", "Y2x1c3RlcjEzNnRva2VuMTM2"),
    ("cluster136prompt136", "Y2x1c3RlcjEzNnByb21wdDEzNg"),
    ("mirror136prompt136", "bWlycm9yMTM2cHJvbXB0MTM2"),
    ("mirror136session136", "bWlycm9yMTM2c2Vzc2lvbjEzNg"),
    ("mirror136library136", "bWlycm9yMTM2bGlicmFyeTEzNg"),
    ("mirror136service136", "bWlycm9yMTM2c2VydmljZTEzNg"),
    ("filter136service136", "ZmlsdGVyMTM2c2VydmljZTEzNg"),
    ("filter136gateway136", "ZmlsdGVyMTM2Z2F0ZXdheTEzNg"),
    ("filter136storage136", "ZmlsdGVyMTM2c3RvcmFnZTEzNg"),
    ("filter136network136", "ZmlsdGVyMTM2bmV0d29yazEzNg"),
    ("ranking136network136", "cmFua2luZzEzNm5ldHdvcmsxMzY"),
    ("ranking136latency136", "cmFua2luZzEzNmxhdGVuY3kxMzY"),
    ("ranking136buffer136", "cmFua2luZzEzNmJ1ZmZlcjEzNg"),
    ("ranking136queue136", "cmFua2luZzEzNnF1ZXVlMTM2"),
    ("encoding136queue136", "ZW5jb2RpbmcxMzZxdWV1ZTEzNg"),
    ("encoding136worker136", "ZW5jb2RpbmcxMzZ3b3JrZXIxMzY"),
    ("encoding136kernel136", "ZW5jb2RpbmcxMzZrZXJuZWwxMzY"),
    ("encoding136signal136", "ZW5jb2RpbmcxMzZzaWduYWwxMzY"),
    ("mapping136signal136", "bWFwcGluZzEzNnNpZ25hbDEzNg"),
    ("mapping136packet136", "bWFwcGluZzEzNnBhY2tldDEzNg"),
    ("mapping136router136", "bWFwcGluZzEzNnJvdXRlcjEzNg"),
    ("mapping136cluster136", "bWFwcGluZzEzNmNsdXN0ZXIxMzY"),
    ("record136cluster136", "cmVjb3JkMTM2Y2x1c3RlcjEzNg"),
    ("record136mirror136", "cmVjb3JkMTM2bWlycm9yMTM2"),
    ("record136filter136", "cmVjb3JkMTM2ZmlsdGVyMTM2"),
    ("record136ranking136", "cmVjb3JkMTM2cmFua2luZzEzNg"),
    ("candle136ranking136", "Y2FuZGxlMTM2cmFua2luZzEzNg"),
    ("candle136encoding136", "Y2FuZGxlMTM2ZW5jb2RpbmcxMzY"),
    ("candle136mapping136", "Y2FuZGxlMTM2bWFwcGluZzEzNg"),
    ("candle136record136", "Y2FuZGxlMTM2cmVjb3JkMTM2"),
    ("thread136record136", "dGhyZWFkMTM2cmVjb3JkMTM2"),
    ("thread136candle136", "dGhyZWFkMTM2Y2FuZGxlMTM2"),
    ("thread136thread136", "dGhyZWFkMTM2dGhyZWFkMTM2"),
    ("thread136kitten136", "dGhyZWFkMTM2a2l0dGVuMTM2"),
    (
        "round 136: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTM2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 136: agentuniverse is a framework for multi agents",
        "cm91bmQgMTM2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 136: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTM2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 136: the processor reads the record then stops",
        "cm91bmQgMTM2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 136: a worker pulls the next task from the queue",
        "cm91bmQgMTM2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 136: signals travel through the network layer",
        "cm91bmQgMTM2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 136: the gateway routes each request by policy",
        "cm91bmQgMTM2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 136: memory grows until the buffer is full",
        "cm91bmQgMTM2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 136: the cluster mirrors every packet twice",
        "cm91bmQgMTM2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 136: ranking uses tokens learned from the corpus",
        "cm91bmQgMTM2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 136: a long session ends when the candle dies",
        "cm91bmQgMTM2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 136: encode the prompt then map the result",
        "cm91bmQgMTM2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 136: the kernel wakes the worker at dawn",
        "cm91bmQgMTM2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 136: service latency drops after the patch",
        "cm91bmQgMTM2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 136: the library caches every vector it sees",
        "cm91bmQgMTM2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 136: agents argue then the debate resolves",
        "cm91bmQgMTM2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 136: the filter keeps only strong matches",
        "cm91bmQgMTM2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 136: the model answers with a short reply",
        "cm91bmQgMTM2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 136: the recorder stores the reasoning trace",
        "cm91bmQgMTM2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 136: the angel watches the processor run",
        "cm91bmQgMTM2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 136: angle of the vector decides the match",
        "cm91bmQgMTM2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 136: the candle burns twice as long at night",
        "cm91bmQgMTM2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 136: a mirror of the universe in one line",
        "cm91bmQgMTM2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 136: the queue drains before the storm", "cm91bmQgMTM2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
