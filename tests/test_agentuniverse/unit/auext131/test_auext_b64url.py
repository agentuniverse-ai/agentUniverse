"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten131kitten131", "a2l0dGVuMTMxa2l0dGVuMTMx"),
    ("kitten131sitting131", "a2l0dGVuMTMxc2l0dGluZzEzMQ"),
    ("kitten131agent131", "a2l0dGVuMTMxYWdlbnQxMzE"),
    ("kitten131angle131", "a2l0dGVuMTMxYW5nbGUxMzE"),
    ("sitting131angle131", "c2l0dGluZzEzMWFuZ2xlMTMx"),
    ("sitting131universe131", "c2l0dGluZzEzMXVuaXZlcnNlMTMx"),
    ("sitting131memory131", "c2l0dGluZzEzMW1lbW9yeTEzMQ"),
    ("sitting131stream131", "c2l0dGluZzEzMXN0cmVhbTEzMQ"),
    ("agent131stream131", "YWdlbnQxMzFzdHJlYW0xMzE"),
    ("agent131context131", "YWdlbnQxMzFjb250ZXh0MTMx"),
    ("agent131knowledge131", "YWdlbnQxMzFrbm93bGVkZ2UxMzE"),
    ("agent131vector131", "YWdlbnQxMzF2ZWN0b3IxMzE"),
    ("angle131vector131", "YW5nbGUxMzF2ZWN0b3IxMzE"),
    ("angle131processor131", "YW5nbGUxMzFwcm9jZXNzb3IxMzE"),
    ("angle131reasoning131", "YW5nbGUxMzFyZWFzb25pbmcxMzE"),
    ("angle131machine131", "YW5nbGUxMzFtYWNoaW5lMTMx"),
    ("universe131machine131", "dW5pdmVyc2UxMzFtYWNoaW5lMTMx"),
    ("universe131learning131", "dW5pdmVyc2UxMzFsZWFybmluZzEzMQ"),
    ("universe131model131", "dW5pdmVyc2UxMzFtb2RlbDEzMQ"),
    ("universe131token131", "dW5pdmVyc2UxMzF0b2tlbjEzMQ"),
    ("memory131token131", "bWVtb3J5MTMxdG9rZW4xMzE"),
    ("memory131prompt131", "bWVtb3J5MTMxcHJvbXB0MTMx"),
    ("memory131session131", "bWVtb3J5MTMxc2Vzc2lvbjEzMQ"),
    ("memory131library131", "bWVtb3J5MTMxbGlicmFyeTEzMQ"),
    ("stream131library131", "c3RyZWFtMTMxbGlicmFyeTEzMQ"),
    ("stream131service131", "c3RyZWFtMTMxc2VydmljZTEzMQ"),
    ("stream131gateway131", "c3RyZWFtMTMxZ2F0ZXdheTEzMQ"),
    ("stream131storage131", "c3RyZWFtMTMxc3RvcmFnZTEzMQ"),
    ("context131storage131", "Y29udGV4dDEzMXN0b3JhZ2UxMzE"),
    ("context131network131", "Y29udGV4dDEzMW5ldHdvcmsxMzE"),
    ("context131latency131", "Y29udGV4dDEzMWxhdGVuY3kxMzE"),
    ("context131buffer131", "Y29udGV4dDEzMWJ1ZmZlcjEzMQ"),
    ("knowledge131buffer131", "a25vd2xlZGdlMTMxYnVmZmVyMTMx"),
    ("knowledge131queue131", "a25vd2xlZGdlMTMxcXVldWUxMzE"),
    ("knowledge131worker131", "a25vd2xlZGdlMTMxd29ya2VyMTMx"),
    ("knowledge131kernel131", "a25vd2xlZGdlMTMxa2VybmVsMTMx"),
    ("vector131kernel131", "dmVjdG9yMTMxa2VybmVsMTMx"),
    ("vector131signal131", "dmVjdG9yMTMxc2lnbmFsMTMx"),
    ("vector131packet131", "dmVjdG9yMTMxcGFja2V0MTMx"),
    ("vector131router131", "dmVjdG9yMTMxcm91dGVyMTMx"),
    ("processor131router131", "cHJvY2Vzc29yMTMxcm91dGVyMTMx"),
    ("processor131cluster131", "cHJvY2Vzc29yMTMxY2x1c3RlcjEzMQ"),
    ("processor131mirror131", "cHJvY2Vzc29yMTMxbWlycm9yMTMx"),
    ("processor131filter131", "cHJvY2Vzc29yMTMxZmlsdGVyMTMx"),
    ("reasoning131filter131", "cmVhc29uaW5nMTMxZmlsdGVyMTMx"),
    ("reasoning131ranking131", "cmVhc29uaW5nMTMxcmFua2luZzEzMQ"),
    ("reasoning131encoding131", "cmVhc29uaW5nMTMxZW5jb2RpbmcxMzE"),
    ("reasoning131mapping131", "cmVhc29uaW5nMTMxbWFwcGluZzEzMQ"),
    ("machine131mapping131", "bWFjaGluZTEzMW1hcHBpbmcxMzE"),
    ("machine131record131", "bWFjaGluZTEzMXJlY29yZDEzMQ"),
    ("machine131candle131", "bWFjaGluZTEzMWNhbmRsZTEzMQ"),
    ("machine131thread131", "bWFjaGluZTEzMXRocmVhZDEzMQ"),
    ("learning131thread131", "bGVhcm5pbmcxMzF0aHJlYWQxMzE"),
    ("learning131kitten131", "bGVhcm5pbmcxMzFraXR0ZW4xMzE"),
    ("learning131sitting131", "bGVhcm5pbmcxMzFzaXR0aW5nMTMx"),
    ("learning131agent131", "bGVhcm5pbmcxMzFhZ2VudDEzMQ"),
    ("model131agent131", "bW9kZWwxMzFhZ2VudDEzMQ"),
    ("model131angle131", "bW9kZWwxMzFhbmdsZTEzMQ"),
    ("model131universe131", "bW9kZWwxMzF1bml2ZXJzZTEzMQ"),
    ("model131memory131", "bW9kZWwxMzFtZW1vcnkxMzE"),
    ("token131memory131", "dG9rZW4xMzFtZW1vcnkxMzE"),
    ("token131stream131", "dG9rZW4xMzFzdHJlYW0xMzE"),
    ("token131context131", "dG9rZW4xMzFjb250ZXh0MTMx"),
    ("token131knowledge131", "dG9rZW4xMzFrbm93bGVkZ2UxMzE"),
    ("prompt131knowledge131", "cHJvbXB0MTMxa25vd2xlZGdlMTMx"),
    ("prompt131vector131", "cHJvbXB0MTMxdmVjdG9yMTMx"),
    ("prompt131processor131", "cHJvbXB0MTMxcHJvY2Vzc29yMTMx"),
    ("prompt131reasoning131", "cHJvbXB0MTMxcmVhc29uaW5nMTMx"),
    ("session131reasoning131", "c2Vzc2lvbjEzMXJlYXNvbmluZzEzMQ"),
    ("session131machine131", "c2Vzc2lvbjEzMW1hY2hpbmUxMzE"),
    ("session131learning131", "c2Vzc2lvbjEzMWxlYXJuaW5nMTMx"),
    ("session131model131", "c2Vzc2lvbjEzMW1vZGVsMTMx"),
    ("library131model131", "bGlicmFyeTEzMW1vZGVsMTMx"),
    ("library131token131", "bGlicmFyeTEzMXRva2VuMTMx"),
    ("library131prompt131", "bGlicmFyeTEzMXByb21wdDEzMQ"),
    ("library131session131", "bGlicmFyeTEzMXNlc3Npb24xMzE"),
    ("service131session131", "c2VydmljZTEzMXNlc3Npb24xMzE"),
    ("service131library131", "c2VydmljZTEzMWxpYnJhcnkxMzE"),
    ("service131service131", "c2VydmljZTEzMXNlcnZpY2UxMzE"),
    ("service131gateway131", "c2VydmljZTEzMWdhdGV3YXkxMzE"),
    ("gateway131gateway131", "Z2F0ZXdheTEzMWdhdGV3YXkxMzE"),
    ("gateway131storage131", "Z2F0ZXdheTEzMXN0b3JhZ2UxMzE"),
    ("gateway131network131", "Z2F0ZXdheTEzMW5ldHdvcmsxMzE"),
    ("gateway131latency131", "Z2F0ZXdheTEzMWxhdGVuY3kxMzE"),
    ("storage131latency131", "c3RvcmFnZTEzMWxhdGVuY3kxMzE"),
    ("storage131buffer131", "c3RvcmFnZTEzMWJ1ZmZlcjEzMQ"),
    ("storage131queue131", "c3RvcmFnZTEzMXF1ZXVlMTMx"),
    ("storage131worker131", "c3RvcmFnZTEzMXdvcmtlcjEzMQ"),
    ("network131worker131", "bmV0d29yazEzMXdvcmtlcjEzMQ"),
    ("network131kernel131", "bmV0d29yazEzMWtlcm5lbDEzMQ"),
    ("network131signal131", "bmV0d29yazEzMXNpZ25hbDEzMQ"),
    ("network131packet131", "bmV0d29yazEzMXBhY2tldDEzMQ"),
    ("latency131packet131", "bGF0ZW5jeTEzMXBhY2tldDEzMQ"),
    ("latency131router131", "bGF0ZW5jeTEzMXJvdXRlcjEzMQ"),
    ("latency131cluster131", "bGF0ZW5jeTEzMWNsdXN0ZXIxMzE"),
    ("latency131mirror131", "bGF0ZW5jeTEzMW1pcnJvcjEzMQ"),
    ("buffer131mirror131", "YnVmZmVyMTMxbWlycm9yMTMx"),
    ("buffer131filter131", "YnVmZmVyMTMxZmlsdGVyMTMx"),
    ("buffer131ranking131", "YnVmZmVyMTMxcmFua2luZzEzMQ"),
    ("buffer131encoding131", "YnVmZmVyMTMxZW5jb2RpbmcxMzE"),
    ("queue131encoding131", "cXVldWUxMzFlbmNvZGluZzEzMQ"),
    ("queue131mapping131", "cXVldWUxMzFtYXBwaW5nMTMx"),
    ("queue131record131", "cXVldWUxMzFyZWNvcmQxMzE"),
    ("queue131candle131", "cXVldWUxMzFjYW5kbGUxMzE"),
    ("worker131candle131", "d29ya2VyMTMxY2FuZGxlMTMx"),
    ("worker131thread131", "d29ya2VyMTMxdGhyZWFkMTMx"),
    ("worker131kitten131", "d29ya2VyMTMxa2l0dGVuMTMx"),
    ("worker131sitting131", "d29ya2VyMTMxc2l0dGluZzEzMQ"),
    ("kernel131sitting131", "a2VybmVsMTMxc2l0dGluZzEzMQ"),
    ("kernel131agent131", "a2VybmVsMTMxYWdlbnQxMzE"),
    ("kernel131angle131", "a2VybmVsMTMxYW5nbGUxMzE"),
    ("kernel131universe131", "a2VybmVsMTMxdW5pdmVyc2UxMzE"),
    ("signal131universe131", "c2lnbmFsMTMxdW5pdmVyc2UxMzE"),
    ("signal131memory131", "c2lnbmFsMTMxbWVtb3J5MTMx"),
    ("signal131stream131", "c2lnbmFsMTMxc3RyZWFtMTMx"),
    ("signal131context131", "c2lnbmFsMTMxY29udGV4dDEzMQ"),
    ("packet131context131", "cGFja2V0MTMxY29udGV4dDEzMQ"),
    ("packet131knowledge131", "cGFja2V0MTMxa25vd2xlZGdlMTMx"),
    ("packet131vector131", "cGFja2V0MTMxdmVjdG9yMTMx"),
    ("packet131processor131", "cGFja2V0MTMxcHJvY2Vzc29yMTMx"),
    ("router131processor131", "cm91dGVyMTMxcHJvY2Vzc29yMTMx"),
    ("router131reasoning131", "cm91dGVyMTMxcmVhc29uaW5nMTMx"),
    ("router131machine131", "cm91dGVyMTMxbWFjaGluZTEzMQ"),
    ("router131learning131", "cm91dGVyMTMxbGVhcm5pbmcxMzE"),
    ("cluster131learning131", "Y2x1c3RlcjEzMWxlYXJuaW5nMTMx"),
    ("cluster131model131", "Y2x1c3RlcjEzMW1vZGVsMTMx"),
    ("cluster131token131", "Y2x1c3RlcjEzMXRva2VuMTMx"),
    ("cluster131prompt131", "Y2x1c3RlcjEzMXByb21wdDEzMQ"),
    ("mirror131prompt131", "bWlycm9yMTMxcHJvbXB0MTMx"),
    ("mirror131session131", "bWlycm9yMTMxc2Vzc2lvbjEzMQ"),
    ("mirror131library131", "bWlycm9yMTMxbGlicmFyeTEzMQ"),
    ("mirror131service131", "bWlycm9yMTMxc2VydmljZTEzMQ"),
    ("filter131service131", "ZmlsdGVyMTMxc2VydmljZTEzMQ"),
    ("filter131gateway131", "ZmlsdGVyMTMxZ2F0ZXdheTEzMQ"),
    ("filter131storage131", "ZmlsdGVyMTMxc3RvcmFnZTEzMQ"),
    ("filter131network131", "ZmlsdGVyMTMxbmV0d29yazEzMQ"),
    ("ranking131network131", "cmFua2luZzEzMW5ldHdvcmsxMzE"),
    ("ranking131latency131", "cmFua2luZzEzMWxhdGVuY3kxMzE"),
    ("ranking131buffer131", "cmFua2luZzEzMWJ1ZmZlcjEzMQ"),
    ("ranking131queue131", "cmFua2luZzEzMXF1ZXVlMTMx"),
    ("encoding131queue131", "ZW5jb2RpbmcxMzFxdWV1ZTEzMQ"),
    ("encoding131worker131", "ZW5jb2RpbmcxMzF3b3JrZXIxMzE"),
    ("encoding131kernel131", "ZW5jb2RpbmcxMzFrZXJuZWwxMzE"),
    ("encoding131signal131", "ZW5jb2RpbmcxMzFzaWduYWwxMzE"),
    ("mapping131signal131", "bWFwcGluZzEzMXNpZ25hbDEzMQ"),
    ("mapping131packet131", "bWFwcGluZzEzMXBhY2tldDEzMQ"),
    ("mapping131router131", "bWFwcGluZzEzMXJvdXRlcjEzMQ"),
    ("mapping131cluster131", "bWFwcGluZzEzMWNsdXN0ZXIxMzE"),
    ("record131cluster131", "cmVjb3JkMTMxY2x1c3RlcjEzMQ"),
    ("record131mirror131", "cmVjb3JkMTMxbWlycm9yMTMx"),
    ("record131filter131", "cmVjb3JkMTMxZmlsdGVyMTMx"),
    ("record131ranking131", "cmVjb3JkMTMxcmFua2luZzEzMQ"),
    ("candle131ranking131", "Y2FuZGxlMTMxcmFua2luZzEzMQ"),
    ("candle131encoding131", "Y2FuZGxlMTMxZW5jb2RpbmcxMzE"),
    ("candle131mapping131", "Y2FuZGxlMTMxbWFwcGluZzEzMQ"),
    ("candle131record131", "Y2FuZGxlMTMxcmVjb3JkMTMx"),
    ("thread131record131", "dGhyZWFkMTMxcmVjb3JkMTMx"),
    ("thread131candle131", "dGhyZWFkMTMxY2FuZGxlMTMx"),
    ("thread131thread131", "dGhyZWFkMTMxdGhyZWFkMTMx"),
    ("thread131kitten131", "dGhyZWFkMTMxa2l0dGVuMTMx"),
    (
        "round 131: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTMxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 131: agentuniverse is a framework for multi agents",
        "cm91bmQgMTMxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 131: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTMxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 131: the processor reads the record then stops",
        "cm91bmQgMTMxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 131: a worker pulls the next task from the queue",
        "cm91bmQgMTMxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 131: signals travel through the network layer",
        "cm91bmQgMTMxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 131: the gateway routes each request by policy",
        "cm91bmQgMTMxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 131: memory grows until the buffer is full",
        "cm91bmQgMTMxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 131: the cluster mirrors every packet twice",
        "cm91bmQgMTMxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 131: ranking uses tokens learned from the corpus",
        "cm91bmQgMTMxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 131: a long session ends when the candle dies",
        "cm91bmQgMTMxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 131: encode the prompt then map the result",
        "cm91bmQgMTMxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 131: the kernel wakes the worker at dawn",
        "cm91bmQgMTMxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 131: service latency drops after the patch",
        "cm91bmQgMTMxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 131: the library caches every vector it sees",
        "cm91bmQgMTMxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 131: agents argue then the debate resolves",
        "cm91bmQgMTMxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 131: the filter keeps only strong matches",
        "cm91bmQgMTMxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 131: the model answers with a short reply",
        "cm91bmQgMTMxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 131: the recorder stores the reasoning trace",
        "cm91bmQgMTMxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 131: the angel watches the processor run",
        "cm91bmQgMTMxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 131: angle of the vector decides the match",
        "cm91bmQgMTMxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 131: the candle burns twice as long at night",
        "cm91bmQgMTMxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 131: a mirror of the universe in one line",
        "cm91bmQgMTMxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 131: the queue drains before the storm", "cm91bmQgMTMxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
