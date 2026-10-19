"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten106kitten106", "a2l0dGVuMTA2a2l0dGVuMTA2"),
    ("kitten106sitting106", "a2l0dGVuMTA2c2l0dGluZzEwNg"),
    ("kitten106agent106", "a2l0dGVuMTA2YWdlbnQxMDY"),
    ("kitten106angle106", "a2l0dGVuMTA2YW5nbGUxMDY"),
    ("sitting106angle106", "c2l0dGluZzEwNmFuZ2xlMTA2"),
    ("sitting106universe106", "c2l0dGluZzEwNnVuaXZlcnNlMTA2"),
    ("sitting106memory106", "c2l0dGluZzEwNm1lbW9yeTEwNg"),
    ("sitting106stream106", "c2l0dGluZzEwNnN0cmVhbTEwNg"),
    ("agent106stream106", "YWdlbnQxMDZzdHJlYW0xMDY"),
    ("agent106context106", "YWdlbnQxMDZjb250ZXh0MTA2"),
    ("agent106knowledge106", "YWdlbnQxMDZrbm93bGVkZ2UxMDY"),
    ("agent106vector106", "YWdlbnQxMDZ2ZWN0b3IxMDY"),
    ("angle106vector106", "YW5nbGUxMDZ2ZWN0b3IxMDY"),
    ("angle106processor106", "YW5nbGUxMDZwcm9jZXNzb3IxMDY"),
    ("angle106reasoning106", "YW5nbGUxMDZyZWFzb25pbmcxMDY"),
    ("angle106machine106", "YW5nbGUxMDZtYWNoaW5lMTA2"),
    ("universe106machine106", "dW5pdmVyc2UxMDZtYWNoaW5lMTA2"),
    ("universe106learning106", "dW5pdmVyc2UxMDZsZWFybmluZzEwNg"),
    ("universe106model106", "dW5pdmVyc2UxMDZtb2RlbDEwNg"),
    ("universe106token106", "dW5pdmVyc2UxMDZ0b2tlbjEwNg"),
    ("memory106token106", "bWVtb3J5MTA2dG9rZW4xMDY"),
    ("memory106prompt106", "bWVtb3J5MTA2cHJvbXB0MTA2"),
    ("memory106session106", "bWVtb3J5MTA2c2Vzc2lvbjEwNg"),
    ("memory106library106", "bWVtb3J5MTA2bGlicmFyeTEwNg"),
    ("stream106library106", "c3RyZWFtMTA2bGlicmFyeTEwNg"),
    ("stream106service106", "c3RyZWFtMTA2c2VydmljZTEwNg"),
    ("stream106gateway106", "c3RyZWFtMTA2Z2F0ZXdheTEwNg"),
    ("stream106storage106", "c3RyZWFtMTA2c3RvcmFnZTEwNg"),
    ("context106storage106", "Y29udGV4dDEwNnN0b3JhZ2UxMDY"),
    ("context106network106", "Y29udGV4dDEwNm5ldHdvcmsxMDY"),
    ("context106latency106", "Y29udGV4dDEwNmxhdGVuY3kxMDY"),
    ("context106buffer106", "Y29udGV4dDEwNmJ1ZmZlcjEwNg"),
    ("knowledge106buffer106", "a25vd2xlZGdlMTA2YnVmZmVyMTA2"),
    ("knowledge106queue106", "a25vd2xlZGdlMTA2cXVldWUxMDY"),
    ("knowledge106worker106", "a25vd2xlZGdlMTA2d29ya2VyMTA2"),
    ("knowledge106kernel106", "a25vd2xlZGdlMTA2a2VybmVsMTA2"),
    ("vector106kernel106", "dmVjdG9yMTA2a2VybmVsMTA2"),
    ("vector106signal106", "dmVjdG9yMTA2c2lnbmFsMTA2"),
    ("vector106packet106", "dmVjdG9yMTA2cGFja2V0MTA2"),
    ("vector106router106", "dmVjdG9yMTA2cm91dGVyMTA2"),
    ("processor106router106", "cHJvY2Vzc29yMTA2cm91dGVyMTA2"),
    ("processor106cluster106", "cHJvY2Vzc29yMTA2Y2x1c3RlcjEwNg"),
    ("processor106mirror106", "cHJvY2Vzc29yMTA2bWlycm9yMTA2"),
    ("processor106filter106", "cHJvY2Vzc29yMTA2ZmlsdGVyMTA2"),
    ("reasoning106filter106", "cmVhc29uaW5nMTA2ZmlsdGVyMTA2"),
    ("reasoning106ranking106", "cmVhc29uaW5nMTA2cmFua2luZzEwNg"),
    ("reasoning106encoding106", "cmVhc29uaW5nMTA2ZW5jb2RpbmcxMDY"),
    ("reasoning106mapping106", "cmVhc29uaW5nMTA2bWFwcGluZzEwNg"),
    ("machine106mapping106", "bWFjaGluZTEwNm1hcHBpbmcxMDY"),
    ("machine106record106", "bWFjaGluZTEwNnJlY29yZDEwNg"),
    ("machine106candle106", "bWFjaGluZTEwNmNhbmRsZTEwNg"),
    ("machine106thread106", "bWFjaGluZTEwNnRocmVhZDEwNg"),
    ("learning106thread106", "bGVhcm5pbmcxMDZ0aHJlYWQxMDY"),
    ("learning106kitten106", "bGVhcm5pbmcxMDZraXR0ZW4xMDY"),
    ("learning106sitting106", "bGVhcm5pbmcxMDZzaXR0aW5nMTA2"),
    ("learning106agent106", "bGVhcm5pbmcxMDZhZ2VudDEwNg"),
    ("model106agent106", "bW9kZWwxMDZhZ2VudDEwNg"),
    ("model106angle106", "bW9kZWwxMDZhbmdsZTEwNg"),
    ("model106universe106", "bW9kZWwxMDZ1bml2ZXJzZTEwNg"),
    ("model106memory106", "bW9kZWwxMDZtZW1vcnkxMDY"),
    ("token106memory106", "dG9rZW4xMDZtZW1vcnkxMDY"),
    ("token106stream106", "dG9rZW4xMDZzdHJlYW0xMDY"),
    ("token106context106", "dG9rZW4xMDZjb250ZXh0MTA2"),
    ("token106knowledge106", "dG9rZW4xMDZrbm93bGVkZ2UxMDY"),
    ("prompt106knowledge106", "cHJvbXB0MTA2a25vd2xlZGdlMTA2"),
    ("prompt106vector106", "cHJvbXB0MTA2dmVjdG9yMTA2"),
    ("prompt106processor106", "cHJvbXB0MTA2cHJvY2Vzc29yMTA2"),
    ("prompt106reasoning106", "cHJvbXB0MTA2cmVhc29uaW5nMTA2"),
    ("session106reasoning106", "c2Vzc2lvbjEwNnJlYXNvbmluZzEwNg"),
    ("session106machine106", "c2Vzc2lvbjEwNm1hY2hpbmUxMDY"),
    ("session106learning106", "c2Vzc2lvbjEwNmxlYXJuaW5nMTA2"),
    ("session106model106", "c2Vzc2lvbjEwNm1vZGVsMTA2"),
    ("library106model106", "bGlicmFyeTEwNm1vZGVsMTA2"),
    ("library106token106", "bGlicmFyeTEwNnRva2VuMTA2"),
    ("library106prompt106", "bGlicmFyeTEwNnByb21wdDEwNg"),
    ("library106session106", "bGlicmFyeTEwNnNlc3Npb24xMDY"),
    ("service106session106", "c2VydmljZTEwNnNlc3Npb24xMDY"),
    ("service106library106", "c2VydmljZTEwNmxpYnJhcnkxMDY"),
    ("service106service106", "c2VydmljZTEwNnNlcnZpY2UxMDY"),
    ("service106gateway106", "c2VydmljZTEwNmdhdGV3YXkxMDY"),
    ("gateway106gateway106", "Z2F0ZXdheTEwNmdhdGV3YXkxMDY"),
    ("gateway106storage106", "Z2F0ZXdheTEwNnN0b3JhZ2UxMDY"),
    ("gateway106network106", "Z2F0ZXdheTEwNm5ldHdvcmsxMDY"),
    ("gateway106latency106", "Z2F0ZXdheTEwNmxhdGVuY3kxMDY"),
    ("storage106latency106", "c3RvcmFnZTEwNmxhdGVuY3kxMDY"),
    ("storage106buffer106", "c3RvcmFnZTEwNmJ1ZmZlcjEwNg"),
    ("storage106queue106", "c3RvcmFnZTEwNnF1ZXVlMTA2"),
    ("storage106worker106", "c3RvcmFnZTEwNndvcmtlcjEwNg"),
    ("network106worker106", "bmV0d29yazEwNndvcmtlcjEwNg"),
    ("network106kernel106", "bmV0d29yazEwNmtlcm5lbDEwNg"),
    ("network106signal106", "bmV0d29yazEwNnNpZ25hbDEwNg"),
    ("network106packet106", "bmV0d29yazEwNnBhY2tldDEwNg"),
    ("latency106packet106", "bGF0ZW5jeTEwNnBhY2tldDEwNg"),
    ("latency106router106", "bGF0ZW5jeTEwNnJvdXRlcjEwNg"),
    ("latency106cluster106", "bGF0ZW5jeTEwNmNsdXN0ZXIxMDY"),
    ("latency106mirror106", "bGF0ZW5jeTEwNm1pcnJvcjEwNg"),
    ("buffer106mirror106", "YnVmZmVyMTA2bWlycm9yMTA2"),
    ("buffer106filter106", "YnVmZmVyMTA2ZmlsdGVyMTA2"),
    ("buffer106ranking106", "YnVmZmVyMTA2cmFua2luZzEwNg"),
    ("buffer106encoding106", "YnVmZmVyMTA2ZW5jb2RpbmcxMDY"),
    ("queue106encoding106", "cXVldWUxMDZlbmNvZGluZzEwNg"),
    ("queue106mapping106", "cXVldWUxMDZtYXBwaW5nMTA2"),
    ("queue106record106", "cXVldWUxMDZyZWNvcmQxMDY"),
    ("queue106candle106", "cXVldWUxMDZjYW5kbGUxMDY"),
    ("worker106candle106", "d29ya2VyMTA2Y2FuZGxlMTA2"),
    ("worker106thread106", "d29ya2VyMTA2dGhyZWFkMTA2"),
    ("worker106kitten106", "d29ya2VyMTA2a2l0dGVuMTA2"),
    ("worker106sitting106", "d29ya2VyMTA2c2l0dGluZzEwNg"),
    ("kernel106sitting106", "a2VybmVsMTA2c2l0dGluZzEwNg"),
    ("kernel106agent106", "a2VybmVsMTA2YWdlbnQxMDY"),
    ("kernel106angle106", "a2VybmVsMTA2YW5nbGUxMDY"),
    ("kernel106universe106", "a2VybmVsMTA2dW5pdmVyc2UxMDY"),
    ("signal106universe106", "c2lnbmFsMTA2dW5pdmVyc2UxMDY"),
    ("signal106memory106", "c2lnbmFsMTA2bWVtb3J5MTA2"),
    ("signal106stream106", "c2lnbmFsMTA2c3RyZWFtMTA2"),
    ("signal106context106", "c2lnbmFsMTA2Y29udGV4dDEwNg"),
    ("packet106context106", "cGFja2V0MTA2Y29udGV4dDEwNg"),
    ("packet106knowledge106", "cGFja2V0MTA2a25vd2xlZGdlMTA2"),
    ("packet106vector106", "cGFja2V0MTA2dmVjdG9yMTA2"),
    ("packet106processor106", "cGFja2V0MTA2cHJvY2Vzc29yMTA2"),
    ("router106processor106", "cm91dGVyMTA2cHJvY2Vzc29yMTA2"),
    ("router106reasoning106", "cm91dGVyMTA2cmVhc29uaW5nMTA2"),
    ("router106machine106", "cm91dGVyMTA2bWFjaGluZTEwNg"),
    ("router106learning106", "cm91dGVyMTA2bGVhcm5pbmcxMDY"),
    ("cluster106learning106", "Y2x1c3RlcjEwNmxlYXJuaW5nMTA2"),
    ("cluster106model106", "Y2x1c3RlcjEwNm1vZGVsMTA2"),
    ("cluster106token106", "Y2x1c3RlcjEwNnRva2VuMTA2"),
    ("cluster106prompt106", "Y2x1c3RlcjEwNnByb21wdDEwNg"),
    ("mirror106prompt106", "bWlycm9yMTA2cHJvbXB0MTA2"),
    ("mirror106session106", "bWlycm9yMTA2c2Vzc2lvbjEwNg"),
    ("mirror106library106", "bWlycm9yMTA2bGlicmFyeTEwNg"),
    ("mirror106service106", "bWlycm9yMTA2c2VydmljZTEwNg"),
    ("filter106service106", "ZmlsdGVyMTA2c2VydmljZTEwNg"),
    ("filter106gateway106", "ZmlsdGVyMTA2Z2F0ZXdheTEwNg"),
    ("filter106storage106", "ZmlsdGVyMTA2c3RvcmFnZTEwNg"),
    ("filter106network106", "ZmlsdGVyMTA2bmV0d29yazEwNg"),
    ("ranking106network106", "cmFua2luZzEwNm5ldHdvcmsxMDY"),
    ("ranking106latency106", "cmFua2luZzEwNmxhdGVuY3kxMDY"),
    ("ranking106buffer106", "cmFua2luZzEwNmJ1ZmZlcjEwNg"),
    ("ranking106queue106", "cmFua2luZzEwNnF1ZXVlMTA2"),
    ("encoding106queue106", "ZW5jb2RpbmcxMDZxdWV1ZTEwNg"),
    ("encoding106worker106", "ZW5jb2RpbmcxMDZ3b3JrZXIxMDY"),
    ("encoding106kernel106", "ZW5jb2RpbmcxMDZrZXJuZWwxMDY"),
    ("encoding106signal106", "ZW5jb2RpbmcxMDZzaWduYWwxMDY"),
    ("mapping106signal106", "bWFwcGluZzEwNnNpZ25hbDEwNg"),
    ("mapping106packet106", "bWFwcGluZzEwNnBhY2tldDEwNg"),
    ("mapping106router106", "bWFwcGluZzEwNnJvdXRlcjEwNg"),
    ("mapping106cluster106", "bWFwcGluZzEwNmNsdXN0ZXIxMDY"),
    ("record106cluster106", "cmVjb3JkMTA2Y2x1c3RlcjEwNg"),
    ("record106mirror106", "cmVjb3JkMTA2bWlycm9yMTA2"),
    ("record106filter106", "cmVjb3JkMTA2ZmlsdGVyMTA2"),
    ("record106ranking106", "cmVjb3JkMTA2cmFua2luZzEwNg"),
    ("candle106ranking106", "Y2FuZGxlMTA2cmFua2luZzEwNg"),
    ("candle106encoding106", "Y2FuZGxlMTA2ZW5jb2RpbmcxMDY"),
    ("candle106mapping106", "Y2FuZGxlMTA2bWFwcGluZzEwNg"),
    ("candle106record106", "Y2FuZGxlMTA2cmVjb3JkMTA2"),
    ("thread106record106", "dGhyZWFkMTA2cmVjb3JkMTA2"),
    ("thread106candle106", "dGhyZWFkMTA2Y2FuZGxlMTA2"),
    ("thread106thread106", "dGhyZWFkMTA2dGhyZWFkMTA2"),
    ("thread106kitten106", "dGhyZWFkMTA2a2l0dGVuMTA2"),
    (
        "round 106: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTA2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 106: agentuniverse is a framework for multi agents",
        "cm91bmQgMTA2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 106: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTA2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 106: the processor reads the record then stops",
        "cm91bmQgMTA2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 106: a worker pulls the next task from the queue",
        "cm91bmQgMTA2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 106: signals travel through the network layer",
        "cm91bmQgMTA2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 106: the gateway routes each request by policy",
        "cm91bmQgMTA2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 106: memory grows until the buffer is full",
        "cm91bmQgMTA2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 106: the cluster mirrors every packet twice",
        "cm91bmQgMTA2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 106: ranking uses tokens learned from the corpus",
        "cm91bmQgMTA2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 106: a long session ends when the candle dies",
        "cm91bmQgMTA2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 106: encode the prompt then map the result",
        "cm91bmQgMTA2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 106: the kernel wakes the worker at dawn",
        "cm91bmQgMTA2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 106: service latency drops after the patch",
        "cm91bmQgMTA2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 106: the library caches every vector it sees",
        "cm91bmQgMTA2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 106: agents argue then the debate resolves",
        "cm91bmQgMTA2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 106: the filter keeps only strong matches",
        "cm91bmQgMTA2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 106: the model answers with a short reply",
        "cm91bmQgMTA2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 106: the recorder stores the reasoning trace",
        "cm91bmQgMTA2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 106: the angel watches the processor run",
        "cm91bmQgMTA2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 106: angle of the vector decides the match",
        "cm91bmQgMTA2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 106: the candle burns twice as long at night",
        "cm91bmQgMTA2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 106: a mirror of the universe in one line",
        "cm91bmQgMTA2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 106: the queue drains before the storm", "cm91bmQgMTA2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
