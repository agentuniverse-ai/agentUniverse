"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten137kitten137", "a2l0dGVuMTM3a2l0dGVuMTM3"),
    ("kitten137sitting137", "a2l0dGVuMTM3c2l0dGluZzEzNw"),
    ("kitten137agent137", "a2l0dGVuMTM3YWdlbnQxMzc"),
    ("kitten137angle137", "a2l0dGVuMTM3YW5nbGUxMzc"),
    ("sitting137angle137", "c2l0dGluZzEzN2FuZ2xlMTM3"),
    ("sitting137universe137", "c2l0dGluZzEzN3VuaXZlcnNlMTM3"),
    ("sitting137memory137", "c2l0dGluZzEzN21lbW9yeTEzNw"),
    ("sitting137stream137", "c2l0dGluZzEzN3N0cmVhbTEzNw"),
    ("agent137stream137", "YWdlbnQxMzdzdHJlYW0xMzc"),
    ("agent137context137", "YWdlbnQxMzdjb250ZXh0MTM3"),
    ("agent137knowledge137", "YWdlbnQxMzdrbm93bGVkZ2UxMzc"),
    ("agent137vector137", "YWdlbnQxMzd2ZWN0b3IxMzc"),
    ("angle137vector137", "YW5nbGUxMzd2ZWN0b3IxMzc"),
    ("angle137processor137", "YW5nbGUxMzdwcm9jZXNzb3IxMzc"),
    ("angle137reasoning137", "YW5nbGUxMzdyZWFzb25pbmcxMzc"),
    ("angle137machine137", "YW5nbGUxMzdtYWNoaW5lMTM3"),
    ("universe137machine137", "dW5pdmVyc2UxMzdtYWNoaW5lMTM3"),
    ("universe137learning137", "dW5pdmVyc2UxMzdsZWFybmluZzEzNw"),
    ("universe137model137", "dW5pdmVyc2UxMzdtb2RlbDEzNw"),
    ("universe137token137", "dW5pdmVyc2UxMzd0b2tlbjEzNw"),
    ("memory137token137", "bWVtb3J5MTM3dG9rZW4xMzc"),
    ("memory137prompt137", "bWVtb3J5MTM3cHJvbXB0MTM3"),
    ("memory137session137", "bWVtb3J5MTM3c2Vzc2lvbjEzNw"),
    ("memory137library137", "bWVtb3J5MTM3bGlicmFyeTEzNw"),
    ("stream137library137", "c3RyZWFtMTM3bGlicmFyeTEzNw"),
    ("stream137service137", "c3RyZWFtMTM3c2VydmljZTEzNw"),
    ("stream137gateway137", "c3RyZWFtMTM3Z2F0ZXdheTEzNw"),
    ("stream137storage137", "c3RyZWFtMTM3c3RvcmFnZTEzNw"),
    ("context137storage137", "Y29udGV4dDEzN3N0b3JhZ2UxMzc"),
    ("context137network137", "Y29udGV4dDEzN25ldHdvcmsxMzc"),
    ("context137latency137", "Y29udGV4dDEzN2xhdGVuY3kxMzc"),
    ("context137buffer137", "Y29udGV4dDEzN2J1ZmZlcjEzNw"),
    ("knowledge137buffer137", "a25vd2xlZGdlMTM3YnVmZmVyMTM3"),
    ("knowledge137queue137", "a25vd2xlZGdlMTM3cXVldWUxMzc"),
    ("knowledge137worker137", "a25vd2xlZGdlMTM3d29ya2VyMTM3"),
    ("knowledge137kernel137", "a25vd2xlZGdlMTM3a2VybmVsMTM3"),
    ("vector137kernel137", "dmVjdG9yMTM3a2VybmVsMTM3"),
    ("vector137signal137", "dmVjdG9yMTM3c2lnbmFsMTM3"),
    ("vector137packet137", "dmVjdG9yMTM3cGFja2V0MTM3"),
    ("vector137router137", "dmVjdG9yMTM3cm91dGVyMTM3"),
    ("processor137router137", "cHJvY2Vzc29yMTM3cm91dGVyMTM3"),
    ("processor137cluster137", "cHJvY2Vzc29yMTM3Y2x1c3RlcjEzNw"),
    ("processor137mirror137", "cHJvY2Vzc29yMTM3bWlycm9yMTM3"),
    ("processor137filter137", "cHJvY2Vzc29yMTM3ZmlsdGVyMTM3"),
    ("reasoning137filter137", "cmVhc29uaW5nMTM3ZmlsdGVyMTM3"),
    ("reasoning137ranking137", "cmVhc29uaW5nMTM3cmFua2luZzEzNw"),
    ("reasoning137encoding137", "cmVhc29uaW5nMTM3ZW5jb2RpbmcxMzc"),
    ("reasoning137mapping137", "cmVhc29uaW5nMTM3bWFwcGluZzEzNw"),
    ("machine137mapping137", "bWFjaGluZTEzN21hcHBpbmcxMzc"),
    ("machine137record137", "bWFjaGluZTEzN3JlY29yZDEzNw"),
    ("machine137candle137", "bWFjaGluZTEzN2NhbmRsZTEzNw"),
    ("machine137thread137", "bWFjaGluZTEzN3RocmVhZDEzNw"),
    ("learning137thread137", "bGVhcm5pbmcxMzd0aHJlYWQxMzc"),
    ("learning137kitten137", "bGVhcm5pbmcxMzdraXR0ZW4xMzc"),
    ("learning137sitting137", "bGVhcm5pbmcxMzdzaXR0aW5nMTM3"),
    ("learning137agent137", "bGVhcm5pbmcxMzdhZ2VudDEzNw"),
    ("model137agent137", "bW9kZWwxMzdhZ2VudDEzNw"),
    ("model137angle137", "bW9kZWwxMzdhbmdsZTEzNw"),
    ("model137universe137", "bW9kZWwxMzd1bml2ZXJzZTEzNw"),
    ("model137memory137", "bW9kZWwxMzdtZW1vcnkxMzc"),
    ("token137memory137", "dG9rZW4xMzdtZW1vcnkxMzc"),
    ("token137stream137", "dG9rZW4xMzdzdHJlYW0xMzc"),
    ("token137context137", "dG9rZW4xMzdjb250ZXh0MTM3"),
    ("token137knowledge137", "dG9rZW4xMzdrbm93bGVkZ2UxMzc"),
    ("prompt137knowledge137", "cHJvbXB0MTM3a25vd2xlZGdlMTM3"),
    ("prompt137vector137", "cHJvbXB0MTM3dmVjdG9yMTM3"),
    ("prompt137processor137", "cHJvbXB0MTM3cHJvY2Vzc29yMTM3"),
    ("prompt137reasoning137", "cHJvbXB0MTM3cmVhc29uaW5nMTM3"),
    ("session137reasoning137", "c2Vzc2lvbjEzN3JlYXNvbmluZzEzNw"),
    ("session137machine137", "c2Vzc2lvbjEzN21hY2hpbmUxMzc"),
    ("session137learning137", "c2Vzc2lvbjEzN2xlYXJuaW5nMTM3"),
    ("session137model137", "c2Vzc2lvbjEzN21vZGVsMTM3"),
    ("library137model137", "bGlicmFyeTEzN21vZGVsMTM3"),
    ("library137token137", "bGlicmFyeTEzN3Rva2VuMTM3"),
    ("library137prompt137", "bGlicmFyeTEzN3Byb21wdDEzNw"),
    ("library137session137", "bGlicmFyeTEzN3Nlc3Npb24xMzc"),
    ("service137session137", "c2VydmljZTEzN3Nlc3Npb24xMzc"),
    ("service137library137", "c2VydmljZTEzN2xpYnJhcnkxMzc"),
    ("service137service137", "c2VydmljZTEzN3NlcnZpY2UxMzc"),
    ("service137gateway137", "c2VydmljZTEzN2dhdGV3YXkxMzc"),
    ("gateway137gateway137", "Z2F0ZXdheTEzN2dhdGV3YXkxMzc"),
    ("gateway137storage137", "Z2F0ZXdheTEzN3N0b3JhZ2UxMzc"),
    ("gateway137network137", "Z2F0ZXdheTEzN25ldHdvcmsxMzc"),
    ("gateway137latency137", "Z2F0ZXdheTEzN2xhdGVuY3kxMzc"),
    ("storage137latency137", "c3RvcmFnZTEzN2xhdGVuY3kxMzc"),
    ("storage137buffer137", "c3RvcmFnZTEzN2J1ZmZlcjEzNw"),
    ("storage137queue137", "c3RvcmFnZTEzN3F1ZXVlMTM3"),
    ("storage137worker137", "c3RvcmFnZTEzN3dvcmtlcjEzNw"),
    ("network137worker137", "bmV0d29yazEzN3dvcmtlcjEzNw"),
    ("network137kernel137", "bmV0d29yazEzN2tlcm5lbDEzNw"),
    ("network137signal137", "bmV0d29yazEzN3NpZ25hbDEzNw"),
    ("network137packet137", "bmV0d29yazEzN3BhY2tldDEzNw"),
    ("latency137packet137", "bGF0ZW5jeTEzN3BhY2tldDEzNw"),
    ("latency137router137", "bGF0ZW5jeTEzN3JvdXRlcjEzNw"),
    ("latency137cluster137", "bGF0ZW5jeTEzN2NsdXN0ZXIxMzc"),
    ("latency137mirror137", "bGF0ZW5jeTEzN21pcnJvcjEzNw"),
    ("buffer137mirror137", "YnVmZmVyMTM3bWlycm9yMTM3"),
    ("buffer137filter137", "YnVmZmVyMTM3ZmlsdGVyMTM3"),
    ("buffer137ranking137", "YnVmZmVyMTM3cmFua2luZzEzNw"),
    ("buffer137encoding137", "YnVmZmVyMTM3ZW5jb2RpbmcxMzc"),
    ("queue137encoding137", "cXVldWUxMzdlbmNvZGluZzEzNw"),
    ("queue137mapping137", "cXVldWUxMzdtYXBwaW5nMTM3"),
    ("queue137record137", "cXVldWUxMzdyZWNvcmQxMzc"),
    ("queue137candle137", "cXVldWUxMzdjYW5kbGUxMzc"),
    ("worker137candle137", "d29ya2VyMTM3Y2FuZGxlMTM3"),
    ("worker137thread137", "d29ya2VyMTM3dGhyZWFkMTM3"),
    ("worker137kitten137", "d29ya2VyMTM3a2l0dGVuMTM3"),
    ("worker137sitting137", "d29ya2VyMTM3c2l0dGluZzEzNw"),
    ("kernel137sitting137", "a2VybmVsMTM3c2l0dGluZzEzNw"),
    ("kernel137agent137", "a2VybmVsMTM3YWdlbnQxMzc"),
    ("kernel137angle137", "a2VybmVsMTM3YW5nbGUxMzc"),
    ("kernel137universe137", "a2VybmVsMTM3dW5pdmVyc2UxMzc"),
    ("signal137universe137", "c2lnbmFsMTM3dW5pdmVyc2UxMzc"),
    ("signal137memory137", "c2lnbmFsMTM3bWVtb3J5MTM3"),
    ("signal137stream137", "c2lnbmFsMTM3c3RyZWFtMTM3"),
    ("signal137context137", "c2lnbmFsMTM3Y29udGV4dDEzNw"),
    ("packet137context137", "cGFja2V0MTM3Y29udGV4dDEzNw"),
    ("packet137knowledge137", "cGFja2V0MTM3a25vd2xlZGdlMTM3"),
    ("packet137vector137", "cGFja2V0MTM3dmVjdG9yMTM3"),
    ("packet137processor137", "cGFja2V0MTM3cHJvY2Vzc29yMTM3"),
    ("router137processor137", "cm91dGVyMTM3cHJvY2Vzc29yMTM3"),
    ("router137reasoning137", "cm91dGVyMTM3cmVhc29uaW5nMTM3"),
    ("router137machine137", "cm91dGVyMTM3bWFjaGluZTEzNw"),
    ("router137learning137", "cm91dGVyMTM3bGVhcm5pbmcxMzc"),
    ("cluster137learning137", "Y2x1c3RlcjEzN2xlYXJuaW5nMTM3"),
    ("cluster137model137", "Y2x1c3RlcjEzN21vZGVsMTM3"),
    ("cluster137token137", "Y2x1c3RlcjEzN3Rva2VuMTM3"),
    ("cluster137prompt137", "Y2x1c3RlcjEzN3Byb21wdDEzNw"),
    ("mirror137prompt137", "bWlycm9yMTM3cHJvbXB0MTM3"),
    ("mirror137session137", "bWlycm9yMTM3c2Vzc2lvbjEzNw"),
    ("mirror137library137", "bWlycm9yMTM3bGlicmFyeTEzNw"),
    ("mirror137service137", "bWlycm9yMTM3c2VydmljZTEzNw"),
    ("filter137service137", "ZmlsdGVyMTM3c2VydmljZTEzNw"),
    ("filter137gateway137", "ZmlsdGVyMTM3Z2F0ZXdheTEzNw"),
    ("filter137storage137", "ZmlsdGVyMTM3c3RvcmFnZTEzNw"),
    ("filter137network137", "ZmlsdGVyMTM3bmV0d29yazEzNw"),
    ("ranking137network137", "cmFua2luZzEzN25ldHdvcmsxMzc"),
    ("ranking137latency137", "cmFua2luZzEzN2xhdGVuY3kxMzc"),
    ("ranking137buffer137", "cmFua2luZzEzN2J1ZmZlcjEzNw"),
    ("ranking137queue137", "cmFua2luZzEzN3F1ZXVlMTM3"),
    ("encoding137queue137", "ZW5jb2RpbmcxMzdxdWV1ZTEzNw"),
    ("encoding137worker137", "ZW5jb2RpbmcxMzd3b3JrZXIxMzc"),
    ("encoding137kernel137", "ZW5jb2RpbmcxMzdrZXJuZWwxMzc"),
    ("encoding137signal137", "ZW5jb2RpbmcxMzdzaWduYWwxMzc"),
    ("mapping137signal137", "bWFwcGluZzEzN3NpZ25hbDEzNw"),
    ("mapping137packet137", "bWFwcGluZzEzN3BhY2tldDEzNw"),
    ("mapping137router137", "bWFwcGluZzEzN3JvdXRlcjEzNw"),
    ("mapping137cluster137", "bWFwcGluZzEzN2NsdXN0ZXIxMzc"),
    ("record137cluster137", "cmVjb3JkMTM3Y2x1c3RlcjEzNw"),
    ("record137mirror137", "cmVjb3JkMTM3bWlycm9yMTM3"),
    ("record137filter137", "cmVjb3JkMTM3ZmlsdGVyMTM3"),
    ("record137ranking137", "cmVjb3JkMTM3cmFua2luZzEzNw"),
    ("candle137ranking137", "Y2FuZGxlMTM3cmFua2luZzEzNw"),
    ("candle137encoding137", "Y2FuZGxlMTM3ZW5jb2RpbmcxMzc"),
    ("candle137mapping137", "Y2FuZGxlMTM3bWFwcGluZzEzNw"),
    ("candle137record137", "Y2FuZGxlMTM3cmVjb3JkMTM3"),
    ("thread137record137", "dGhyZWFkMTM3cmVjb3JkMTM3"),
    ("thread137candle137", "dGhyZWFkMTM3Y2FuZGxlMTM3"),
    ("thread137thread137", "dGhyZWFkMTM3dGhyZWFkMTM3"),
    ("thread137kitten137", "dGhyZWFkMTM3a2l0dGVuMTM3"),
    (
        "round 137: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTM3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 137: agentuniverse is a framework for multi agents",
        "cm91bmQgMTM3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 137: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTM3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 137: the processor reads the record then stops",
        "cm91bmQgMTM3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 137: a worker pulls the next task from the queue",
        "cm91bmQgMTM3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 137: signals travel through the network layer",
        "cm91bmQgMTM3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 137: the gateway routes each request by policy",
        "cm91bmQgMTM3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 137: memory grows until the buffer is full",
        "cm91bmQgMTM3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 137: the cluster mirrors every packet twice",
        "cm91bmQgMTM3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 137: ranking uses tokens learned from the corpus",
        "cm91bmQgMTM3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 137: a long session ends when the candle dies",
        "cm91bmQgMTM3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 137: encode the prompt then map the result",
        "cm91bmQgMTM3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 137: the kernel wakes the worker at dawn",
        "cm91bmQgMTM3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 137: service latency drops after the patch",
        "cm91bmQgMTM3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 137: the library caches every vector it sees",
        "cm91bmQgMTM3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 137: agents argue then the debate resolves",
        "cm91bmQgMTM3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 137: the filter keeps only strong matches",
        "cm91bmQgMTM3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 137: the model answers with a short reply",
        "cm91bmQgMTM3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 137: the recorder stores the reasoning trace",
        "cm91bmQgMTM3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 137: the angel watches the processor run",
        "cm91bmQgMTM3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 137: angle of the vector decides the match",
        "cm91bmQgMTM3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 137: the candle burns twice as long at night",
        "cm91bmQgMTM3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 137: a mirror of the universe in one line",
        "cm91bmQgMTM3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 137: the queue drains before the storm", "cm91bmQgMTM3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
