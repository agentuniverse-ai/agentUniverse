"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten116kitten116", "a2l0dGVuMTE2a2l0dGVuMTE2"),
    ("kitten116sitting116", "a2l0dGVuMTE2c2l0dGluZzExNg"),
    ("kitten116agent116", "a2l0dGVuMTE2YWdlbnQxMTY"),
    ("kitten116angle116", "a2l0dGVuMTE2YW5nbGUxMTY"),
    ("sitting116angle116", "c2l0dGluZzExNmFuZ2xlMTE2"),
    ("sitting116universe116", "c2l0dGluZzExNnVuaXZlcnNlMTE2"),
    ("sitting116memory116", "c2l0dGluZzExNm1lbW9yeTExNg"),
    ("sitting116stream116", "c2l0dGluZzExNnN0cmVhbTExNg"),
    ("agent116stream116", "YWdlbnQxMTZzdHJlYW0xMTY"),
    ("agent116context116", "YWdlbnQxMTZjb250ZXh0MTE2"),
    ("agent116knowledge116", "YWdlbnQxMTZrbm93bGVkZ2UxMTY"),
    ("agent116vector116", "YWdlbnQxMTZ2ZWN0b3IxMTY"),
    ("angle116vector116", "YW5nbGUxMTZ2ZWN0b3IxMTY"),
    ("angle116processor116", "YW5nbGUxMTZwcm9jZXNzb3IxMTY"),
    ("angle116reasoning116", "YW5nbGUxMTZyZWFzb25pbmcxMTY"),
    ("angle116machine116", "YW5nbGUxMTZtYWNoaW5lMTE2"),
    ("universe116machine116", "dW5pdmVyc2UxMTZtYWNoaW5lMTE2"),
    ("universe116learning116", "dW5pdmVyc2UxMTZsZWFybmluZzExNg"),
    ("universe116model116", "dW5pdmVyc2UxMTZtb2RlbDExNg"),
    ("universe116token116", "dW5pdmVyc2UxMTZ0b2tlbjExNg"),
    ("memory116token116", "bWVtb3J5MTE2dG9rZW4xMTY"),
    ("memory116prompt116", "bWVtb3J5MTE2cHJvbXB0MTE2"),
    ("memory116session116", "bWVtb3J5MTE2c2Vzc2lvbjExNg"),
    ("memory116library116", "bWVtb3J5MTE2bGlicmFyeTExNg"),
    ("stream116library116", "c3RyZWFtMTE2bGlicmFyeTExNg"),
    ("stream116service116", "c3RyZWFtMTE2c2VydmljZTExNg"),
    ("stream116gateway116", "c3RyZWFtMTE2Z2F0ZXdheTExNg"),
    ("stream116storage116", "c3RyZWFtMTE2c3RvcmFnZTExNg"),
    ("context116storage116", "Y29udGV4dDExNnN0b3JhZ2UxMTY"),
    ("context116network116", "Y29udGV4dDExNm5ldHdvcmsxMTY"),
    ("context116latency116", "Y29udGV4dDExNmxhdGVuY3kxMTY"),
    ("context116buffer116", "Y29udGV4dDExNmJ1ZmZlcjExNg"),
    ("knowledge116buffer116", "a25vd2xlZGdlMTE2YnVmZmVyMTE2"),
    ("knowledge116queue116", "a25vd2xlZGdlMTE2cXVldWUxMTY"),
    ("knowledge116worker116", "a25vd2xlZGdlMTE2d29ya2VyMTE2"),
    ("knowledge116kernel116", "a25vd2xlZGdlMTE2a2VybmVsMTE2"),
    ("vector116kernel116", "dmVjdG9yMTE2a2VybmVsMTE2"),
    ("vector116signal116", "dmVjdG9yMTE2c2lnbmFsMTE2"),
    ("vector116packet116", "dmVjdG9yMTE2cGFja2V0MTE2"),
    ("vector116router116", "dmVjdG9yMTE2cm91dGVyMTE2"),
    ("processor116router116", "cHJvY2Vzc29yMTE2cm91dGVyMTE2"),
    ("processor116cluster116", "cHJvY2Vzc29yMTE2Y2x1c3RlcjExNg"),
    ("processor116mirror116", "cHJvY2Vzc29yMTE2bWlycm9yMTE2"),
    ("processor116filter116", "cHJvY2Vzc29yMTE2ZmlsdGVyMTE2"),
    ("reasoning116filter116", "cmVhc29uaW5nMTE2ZmlsdGVyMTE2"),
    ("reasoning116ranking116", "cmVhc29uaW5nMTE2cmFua2luZzExNg"),
    ("reasoning116encoding116", "cmVhc29uaW5nMTE2ZW5jb2RpbmcxMTY"),
    ("reasoning116mapping116", "cmVhc29uaW5nMTE2bWFwcGluZzExNg"),
    ("machine116mapping116", "bWFjaGluZTExNm1hcHBpbmcxMTY"),
    ("machine116record116", "bWFjaGluZTExNnJlY29yZDExNg"),
    ("machine116candle116", "bWFjaGluZTExNmNhbmRsZTExNg"),
    ("machine116thread116", "bWFjaGluZTExNnRocmVhZDExNg"),
    ("learning116thread116", "bGVhcm5pbmcxMTZ0aHJlYWQxMTY"),
    ("learning116kitten116", "bGVhcm5pbmcxMTZraXR0ZW4xMTY"),
    ("learning116sitting116", "bGVhcm5pbmcxMTZzaXR0aW5nMTE2"),
    ("learning116agent116", "bGVhcm5pbmcxMTZhZ2VudDExNg"),
    ("model116agent116", "bW9kZWwxMTZhZ2VudDExNg"),
    ("model116angle116", "bW9kZWwxMTZhbmdsZTExNg"),
    ("model116universe116", "bW9kZWwxMTZ1bml2ZXJzZTExNg"),
    ("model116memory116", "bW9kZWwxMTZtZW1vcnkxMTY"),
    ("token116memory116", "dG9rZW4xMTZtZW1vcnkxMTY"),
    ("token116stream116", "dG9rZW4xMTZzdHJlYW0xMTY"),
    ("token116context116", "dG9rZW4xMTZjb250ZXh0MTE2"),
    ("token116knowledge116", "dG9rZW4xMTZrbm93bGVkZ2UxMTY"),
    ("prompt116knowledge116", "cHJvbXB0MTE2a25vd2xlZGdlMTE2"),
    ("prompt116vector116", "cHJvbXB0MTE2dmVjdG9yMTE2"),
    ("prompt116processor116", "cHJvbXB0MTE2cHJvY2Vzc29yMTE2"),
    ("prompt116reasoning116", "cHJvbXB0MTE2cmVhc29uaW5nMTE2"),
    ("session116reasoning116", "c2Vzc2lvbjExNnJlYXNvbmluZzExNg"),
    ("session116machine116", "c2Vzc2lvbjExNm1hY2hpbmUxMTY"),
    ("session116learning116", "c2Vzc2lvbjExNmxlYXJuaW5nMTE2"),
    ("session116model116", "c2Vzc2lvbjExNm1vZGVsMTE2"),
    ("library116model116", "bGlicmFyeTExNm1vZGVsMTE2"),
    ("library116token116", "bGlicmFyeTExNnRva2VuMTE2"),
    ("library116prompt116", "bGlicmFyeTExNnByb21wdDExNg"),
    ("library116session116", "bGlicmFyeTExNnNlc3Npb24xMTY"),
    ("service116session116", "c2VydmljZTExNnNlc3Npb24xMTY"),
    ("service116library116", "c2VydmljZTExNmxpYnJhcnkxMTY"),
    ("service116service116", "c2VydmljZTExNnNlcnZpY2UxMTY"),
    ("service116gateway116", "c2VydmljZTExNmdhdGV3YXkxMTY"),
    ("gateway116gateway116", "Z2F0ZXdheTExNmdhdGV3YXkxMTY"),
    ("gateway116storage116", "Z2F0ZXdheTExNnN0b3JhZ2UxMTY"),
    ("gateway116network116", "Z2F0ZXdheTExNm5ldHdvcmsxMTY"),
    ("gateway116latency116", "Z2F0ZXdheTExNmxhdGVuY3kxMTY"),
    ("storage116latency116", "c3RvcmFnZTExNmxhdGVuY3kxMTY"),
    ("storage116buffer116", "c3RvcmFnZTExNmJ1ZmZlcjExNg"),
    ("storage116queue116", "c3RvcmFnZTExNnF1ZXVlMTE2"),
    ("storage116worker116", "c3RvcmFnZTExNndvcmtlcjExNg"),
    ("network116worker116", "bmV0d29yazExNndvcmtlcjExNg"),
    ("network116kernel116", "bmV0d29yazExNmtlcm5lbDExNg"),
    ("network116signal116", "bmV0d29yazExNnNpZ25hbDExNg"),
    ("network116packet116", "bmV0d29yazExNnBhY2tldDExNg"),
    ("latency116packet116", "bGF0ZW5jeTExNnBhY2tldDExNg"),
    ("latency116router116", "bGF0ZW5jeTExNnJvdXRlcjExNg"),
    ("latency116cluster116", "bGF0ZW5jeTExNmNsdXN0ZXIxMTY"),
    ("latency116mirror116", "bGF0ZW5jeTExNm1pcnJvcjExNg"),
    ("buffer116mirror116", "YnVmZmVyMTE2bWlycm9yMTE2"),
    ("buffer116filter116", "YnVmZmVyMTE2ZmlsdGVyMTE2"),
    ("buffer116ranking116", "YnVmZmVyMTE2cmFua2luZzExNg"),
    ("buffer116encoding116", "YnVmZmVyMTE2ZW5jb2RpbmcxMTY"),
    ("queue116encoding116", "cXVldWUxMTZlbmNvZGluZzExNg"),
    ("queue116mapping116", "cXVldWUxMTZtYXBwaW5nMTE2"),
    ("queue116record116", "cXVldWUxMTZyZWNvcmQxMTY"),
    ("queue116candle116", "cXVldWUxMTZjYW5kbGUxMTY"),
    ("worker116candle116", "d29ya2VyMTE2Y2FuZGxlMTE2"),
    ("worker116thread116", "d29ya2VyMTE2dGhyZWFkMTE2"),
    ("worker116kitten116", "d29ya2VyMTE2a2l0dGVuMTE2"),
    ("worker116sitting116", "d29ya2VyMTE2c2l0dGluZzExNg"),
    ("kernel116sitting116", "a2VybmVsMTE2c2l0dGluZzExNg"),
    ("kernel116agent116", "a2VybmVsMTE2YWdlbnQxMTY"),
    ("kernel116angle116", "a2VybmVsMTE2YW5nbGUxMTY"),
    ("kernel116universe116", "a2VybmVsMTE2dW5pdmVyc2UxMTY"),
    ("signal116universe116", "c2lnbmFsMTE2dW5pdmVyc2UxMTY"),
    ("signal116memory116", "c2lnbmFsMTE2bWVtb3J5MTE2"),
    ("signal116stream116", "c2lnbmFsMTE2c3RyZWFtMTE2"),
    ("signal116context116", "c2lnbmFsMTE2Y29udGV4dDExNg"),
    ("packet116context116", "cGFja2V0MTE2Y29udGV4dDExNg"),
    ("packet116knowledge116", "cGFja2V0MTE2a25vd2xlZGdlMTE2"),
    ("packet116vector116", "cGFja2V0MTE2dmVjdG9yMTE2"),
    ("packet116processor116", "cGFja2V0MTE2cHJvY2Vzc29yMTE2"),
    ("router116processor116", "cm91dGVyMTE2cHJvY2Vzc29yMTE2"),
    ("router116reasoning116", "cm91dGVyMTE2cmVhc29uaW5nMTE2"),
    ("router116machine116", "cm91dGVyMTE2bWFjaGluZTExNg"),
    ("router116learning116", "cm91dGVyMTE2bGVhcm5pbmcxMTY"),
    ("cluster116learning116", "Y2x1c3RlcjExNmxlYXJuaW5nMTE2"),
    ("cluster116model116", "Y2x1c3RlcjExNm1vZGVsMTE2"),
    ("cluster116token116", "Y2x1c3RlcjExNnRva2VuMTE2"),
    ("cluster116prompt116", "Y2x1c3RlcjExNnByb21wdDExNg"),
    ("mirror116prompt116", "bWlycm9yMTE2cHJvbXB0MTE2"),
    ("mirror116session116", "bWlycm9yMTE2c2Vzc2lvbjExNg"),
    ("mirror116library116", "bWlycm9yMTE2bGlicmFyeTExNg"),
    ("mirror116service116", "bWlycm9yMTE2c2VydmljZTExNg"),
    ("filter116service116", "ZmlsdGVyMTE2c2VydmljZTExNg"),
    ("filter116gateway116", "ZmlsdGVyMTE2Z2F0ZXdheTExNg"),
    ("filter116storage116", "ZmlsdGVyMTE2c3RvcmFnZTExNg"),
    ("filter116network116", "ZmlsdGVyMTE2bmV0d29yazExNg"),
    ("ranking116network116", "cmFua2luZzExNm5ldHdvcmsxMTY"),
    ("ranking116latency116", "cmFua2luZzExNmxhdGVuY3kxMTY"),
    ("ranking116buffer116", "cmFua2luZzExNmJ1ZmZlcjExNg"),
    ("ranking116queue116", "cmFua2luZzExNnF1ZXVlMTE2"),
    ("encoding116queue116", "ZW5jb2RpbmcxMTZxdWV1ZTExNg"),
    ("encoding116worker116", "ZW5jb2RpbmcxMTZ3b3JrZXIxMTY"),
    ("encoding116kernel116", "ZW5jb2RpbmcxMTZrZXJuZWwxMTY"),
    ("encoding116signal116", "ZW5jb2RpbmcxMTZzaWduYWwxMTY"),
    ("mapping116signal116", "bWFwcGluZzExNnNpZ25hbDExNg"),
    ("mapping116packet116", "bWFwcGluZzExNnBhY2tldDExNg"),
    ("mapping116router116", "bWFwcGluZzExNnJvdXRlcjExNg"),
    ("mapping116cluster116", "bWFwcGluZzExNmNsdXN0ZXIxMTY"),
    ("record116cluster116", "cmVjb3JkMTE2Y2x1c3RlcjExNg"),
    ("record116mirror116", "cmVjb3JkMTE2bWlycm9yMTE2"),
    ("record116filter116", "cmVjb3JkMTE2ZmlsdGVyMTE2"),
    ("record116ranking116", "cmVjb3JkMTE2cmFua2luZzExNg"),
    ("candle116ranking116", "Y2FuZGxlMTE2cmFua2luZzExNg"),
    ("candle116encoding116", "Y2FuZGxlMTE2ZW5jb2RpbmcxMTY"),
    ("candle116mapping116", "Y2FuZGxlMTE2bWFwcGluZzExNg"),
    ("candle116record116", "Y2FuZGxlMTE2cmVjb3JkMTE2"),
    ("thread116record116", "dGhyZWFkMTE2cmVjb3JkMTE2"),
    ("thread116candle116", "dGhyZWFkMTE2Y2FuZGxlMTE2"),
    ("thread116thread116", "dGhyZWFkMTE2dGhyZWFkMTE2"),
    ("thread116kitten116", "dGhyZWFkMTE2a2l0dGVuMTE2"),
    (
        "round 116: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTE2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 116: agentuniverse is a framework for multi agents",
        "cm91bmQgMTE2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 116: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTE2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 116: the processor reads the record then stops",
        "cm91bmQgMTE2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 116: a worker pulls the next task from the queue",
        "cm91bmQgMTE2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 116: signals travel through the network layer",
        "cm91bmQgMTE2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 116: the gateway routes each request by policy",
        "cm91bmQgMTE2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 116: memory grows until the buffer is full",
        "cm91bmQgMTE2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 116: the cluster mirrors every packet twice",
        "cm91bmQgMTE2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 116: ranking uses tokens learned from the corpus",
        "cm91bmQgMTE2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 116: a long session ends when the candle dies",
        "cm91bmQgMTE2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 116: encode the prompt then map the result",
        "cm91bmQgMTE2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 116: the kernel wakes the worker at dawn",
        "cm91bmQgMTE2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 116: service latency drops after the patch",
        "cm91bmQgMTE2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 116: the library caches every vector it sees",
        "cm91bmQgMTE2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 116: agents argue then the debate resolves",
        "cm91bmQgMTE2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 116: the filter keeps only strong matches",
        "cm91bmQgMTE2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 116: the model answers with a short reply",
        "cm91bmQgMTE2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 116: the recorder stores the reasoning trace",
        "cm91bmQgMTE2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 116: the angel watches the processor run",
        "cm91bmQgMTE2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 116: angle of the vector decides the match",
        "cm91bmQgMTE2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 116: the candle burns twice as long at night",
        "cm91bmQgMTE2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 116: a mirror of the universe in one line",
        "cm91bmQgMTE2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 116: the queue drains before the storm", "cm91bmQgMTE2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
