"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten132kitten132", "a2l0dGVuMTMya2l0dGVuMTMy"),
    ("kitten132sitting132", "a2l0dGVuMTMyc2l0dGluZzEzMg"),
    ("kitten132agent132", "a2l0dGVuMTMyYWdlbnQxMzI"),
    ("kitten132angle132", "a2l0dGVuMTMyYW5nbGUxMzI"),
    ("sitting132angle132", "c2l0dGluZzEzMmFuZ2xlMTMy"),
    ("sitting132universe132", "c2l0dGluZzEzMnVuaXZlcnNlMTMy"),
    ("sitting132memory132", "c2l0dGluZzEzMm1lbW9yeTEzMg"),
    ("sitting132stream132", "c2l0dGluZzEzMnN0cmVhbTEzMg"),
    ("agent132stream132", "YWdlbnQxMzJzdHJlYW0xMzI"),
    ("agent132context132", "YWdlbnQxMzJjb250ZXh0MTMy"),
    ("agent132knowledge132", "YWdlbnQxMzJrbm93bGVkZ2UxMzI"),
    ("agent132vector132", "YWdlbnQxMzJ2ZWN0b3IxMzI"),
    ("angle132vector132", "YW5nbGUxMzJ2ZWN0b3IxMzI"),
    ("angle132processor132", "YW5nbGUxMzJwcm9jZXNzb3IxMzI"),
    ("angle132reasoning132", "YW5nbGUxMzJyZWFzb25pbmcxMzI"),
    ("angle132machine132", "YW5nbGUxMzJtYWNoaW5lMTMy"),
    ("universe132machine132", "dW5pdmVyc2UxMzJtYWNoaW5lMTMy"),
    ("universe132learning132", "dW5pdmVyc2UxMzJsZWFybmluZzEzMg"),
    ("universe132model132", "dW5pdmVyc2UxMzJtb2RlbDEzMg"),
    ("universe132token132", "dW5pdmVyc2UxMzJ0b2tlbjEzMg"),
    ("memory132token132", "bWVtb3J5MTMydG9rZW4xMzI"),
    ("memory132prompt132", "bWVtb3J5MTMycHJvbXB0MTMy"),
    ("memory132session132", "bWVtb3J5MTMyc2Vzc2lvbjEzMg"),
    ("memory132library132", "bWVtb3J5MTMybGlicmFyeTEzMg"),
    ("stream132library132", "c3RyZWFtMTMybGlicmFyeTEzMg"),
    ("stream132service132", "c3RyZWFtMTMyc2VydmljZTEzMg"),
    ("stream132gateway132", "c3RyZWFtMTMyZ2F0ZXdheTEzMg"),
    ("stream132storage132", "c3RyZWFtMTMyc3RvcmFnZTEzMg"),
    ("context132storage132", "Y29udGV4dDEzMnN0b3JhZ2UxMzI"),
    ("context132network132", "Y29udGV4dDEzMm5ldHdvcmsxMzI"),
    ("context132latency132", "Y29udGV4dDEzMmxhdGVuY3kxMzI"),
    ("context132buffer132", "Y29udGV4dDEzMmJ1ZmZlcjEzMg"),
    ("knowledge132buffer132", "a25vd2xlZGdlMTMyYnVmZmVyMTMy"),
    ("knowledge132queue132", "a25vd2xlZGdlMTMycXVldWUxMzI"),
    ("knowledge132worker132", "a25vd2xlZGdlMTMyd29ya2VyMTMy"),
    ("knowledge132kernel132", "a25vd2xlZGdlMTMya2VybmVsMTMy"),
    ("vector132kernel132", "dmVjdG9yMTMya2VybmVsMTMy"),
    ("vector132signal132", "dmVjdG9yMTMyc2lnbmFsMTMy"),
    ("vector132packet132", "dmVjdG9yMTMycGFja2V0MTMy"),
    ("vector132router132", "dmVjdG9yMTMycm91dGVyMTMy"),
    ("processor132router132", "cHJvY2Vzc29yMTMycm91dGVyMTMy"),
    ("processor132cluster132", "cHJvY2Vzc29yMTMyY2x1c3RlcjEzMg"),
    ("processor132mirror132", "cHJvY2Vzc29yMTMybWlycm9yMTMy"),
    ("processor132filter132", "cHJvY2Vzc29yMTMyZmlsdGVyMTMy"),
    ("reasoning132filter132", "cmVhc29uaW5nMTMyZmlsdGVyMTMy"),
    ("reasoning132ranking132", "cmVhc29uaW5nMTMycmFua2luZzEzMg"),
    ("reasoning132encoding132", "cmVhc29uaW5nMTMyZW5jb2RpbmcxMzI"),
    ("reasoning132mapping132", "cmVhc29uaW5nMTMybWFwcGluZzEzMg"),
    ("machine132mapping132", "bWFjaGluZTEzMm1hcHBpbmcxMzI"),
    ("machine132record132", "bWFjaGluZTEzMnJlY29yZDEzMg"),
    ("machine132candle132", "bWFjaGluZTEzMmNhbmRsZTEzMg"),
    ("machine132thread132", "bWFjaGluZTEzMnRocmVhZDEzMg"),
    ("learning132thread132", "bGVhcm5pbmcxMzJ0aHJlYWQxMzI"),
    ("learning132kitten132", "bGVhcm5pbmcxMzJraXR0ZW4xMzI"),
    ("learning132sitting132", "bGVhcm5pbmcxMzJzaXR0aW5nMTMy"),
    ("learning132agent132", "bGVhcm5pbmcxMzJhZ2VudDEzMg"),
    ("model132agent132", "bW9kZWwxMzJhZ2VudDEzMg"),
    ("model132angle132", "bW9kZWwxMzJhbmdsZTEzMg"),
    ("model132universe132", "bW9kZWwxMzJ1bml2ZXJzZTEzMg"),
    ("model132memory132", "bW9kZWwxMzJtZW1vcnkxMzI"),
    ("token132memory132", "dG9rZW4xMzJtZW1vcnkxMzI"),
    ("token132stream132", "dG9rZW4xMzJzdHJlYW0xMzI"),
    ("token132context132", "dG9rZW4xMzJjb250ZXh0MTMy"),
    ("token132knowledge132", "dG9rZW4xMzJrbm93bGVkZ2UxMzI"),
    ("prompt132knowledge132", "cHJvbXB0MTMya25vd2xlZGdlMTMy"),
    ("prompt132vector132", "cHJvbXB0MTMydmVjdG9yMTMy"),
    ("prompt132processor132", "cHJvbXB0MTMycHJvY2Vzc29yMTMy"),
    ("prompt132reasoning132", "cHJvbXB0MTMycmVhc29uaW5nMTMy"),
    ("session132reasoning132", "c2Vzc2lvbjEzMnJlYXNvbmluZzEzMg"),
    ("session132machine132", "c2Vzc2lvbjEzMm1hY2hpbmUxMzI"),
    ("session132learning132", "c2Vzc2lvbjEzMmxlYXJuaW5nMTMy"),
    ("session132model132", "c2Vzc2lvbjEzMm1vZGVsMTMy"),
    ("library132model132", "bGlicmFyeTEzMm1vZGVsMTMy"),
    ("library132token132", "bGlicmFyeTEzMnRva2VuMTMy"),
    ("library132prompt132", "bGlicmFyeTEzMnByb21wdDEzMg"),
    ("library132session132", "bGlicmFyeTEzMnNlc3Npb24xMzI"),
    ("service132session132", "c2VydmljZTEzMnNlc3Npb24xMzI"),
    ("service132library132", "c2VydmljZTEzMmxpYnJhcnkxMzI"),
    ("service132service132", "c2VydmljZTEzMnNlcnZpY2UxMzI"),
    ("service132gateway132", "c2VydmljZTEzMmdhdGV3YXkxMzI"),
    ("gateway132gateway132", "Z2F0ZXdheTEzMmdhdGV3YXkxMzI"),
    ("gateway132storage132", "Z2F0ZXdheTEzMnN0b3JhZ2UxMzI"),
    ("gateway132network132", "Z2F0ZXdheTEzMm5ldHdvcmsxMzI"),
    ("gateway132latency132", "Z2F0ZXdheTEzMmxhdGVuY3kxMzI"),
    ("storage132latency132", "c3RvcmFnZTEzMmxhdGVuY3kxMzI"),
    ("storage132buffer132", "c3RvcmFnZTEzMmJ1ZmZlcjEzMg"),
    ("storage132queue132", "c3RvcmFnZTEzMnF1ZXVlMTMy"),
    ("storage132worker132", "c3RvcmFnZTEzMndvcmtlcjEzMg"),
    ("network132worker132", "bmV0d29yazEzMndvcmtlcjEzMg"),
    ("network132kernel132", "bmV0d29yazEzMmtlcm5lbDEzMg"),
    ("network132signal132", "bmV0d29yazEzMnNpZ25hbDEzMg"),
    ("network132packet132", "bmV0d29yazEzMnBhY2tldDEzMg"),
    ("latency132packet132", "bGF0ZW5jeTEzMnBhY2tldDEzMg"),
    ("latency132router132", "bGF0ZW5jeTEzMnJvdXRlcjEzMg"),
    ("latency132cluster132", "bGF0ZW5jeTEzMmNsdXN0ZXIxMzI"),
    ("latency132mirror132", "bGF0ZW5jeTEzMm1pcnJvcjEzMg"),
    ("buffer132mirror132", "YnVmZmVyMTMybWlycm9yMTMy"),
    ("buffer132filter132", "YnVmZmVyMTMyZmlsdGVyMTMy"),
    ("buffer132ranking132", "YnVmZmVyMTMycmFua2luZzEzMg"),
    ("buffer132encoding132", "YnVmZmVyMTMyZW5jb2RpbmcxMzI"),
    ("queue132encoding132", "cXVldWUxMzJlbmNvZGluZzEzMg"),
    ("queue132mapping132", "cXVldWUxMzJtYXBwaW5nMTMy"),
    ("queue132record132", "cXVldWUxMzJyZWNvcmQxMzI"),
    ("queue132candle132", "cXVldWUxMzJjYW5kbGUxMzI"),
    ("worker132candle132", "d29ya2VyMTMyY2FuZGxlMTMy"),
    ("worker132thread132", "d29ya2VyMTMydGhyZWFkMTMy"),
    ("worker132kitten132", "d29ya2VyMTMya2l0dGVuMTMy"),
    ("worker132sitting132", "d29ya2VyMTMyc2l0dGluZzEzMg"),
    ("kernel132sitting132", "a2VybmVsMTMyc2l0dGluZzEzMg"),
    ("kernel132agent132", "a2VybmVsMTMyYWdlbnQxMzI"),
    ("kernel132angle132", "a2VybmVsMTMyYW5nbGUxMzI"),
    ("kernel132universe132", "a2VybmVsMTMydW5pdmVyc2UxMzI"),
    ("signal132universe132", "c2lnbmFsMTMydW5pdmVyc2UxMzI"),
    ("signal132memory132", "c2lnbmFsMTMybWVtb3J5MTMy"),
    ("signal132stream132", "c2lnbmFsMTMyc3RyZWFtMTMy"),
    ("signal132context132", "c2lnbmFsMTMyY29udGV4dDEzMg"),
    ("packet132context132", "cGFja2V0MTMyY29udGV4dDEzMg"),
    ("packet132knowledge132", "cGFja2V0MTMya25vd2xlZGdlMTMy"),
    ("packet132vector132", "cGFja2V0MTMydmVjdG9yMTMy"),
    ("packet132processor132", "cGFja2V0MTMycHJvY2Vzc29yMTMy"),
    ("router132processor132", "cm91dGVyMTMycHJvY2Vzc29yMTMy"),
    ("router132reasoning132", "cm91dGVyMTMycmVhc29uaW5nMTMy"),
    ("router132machine132", "cm91dGVyMTMybWFjaGluZTEzMg"),
    ("router132learning132", "cm91dGVyMTMybGVhcm5pbmcxMzI"),
    ("cluster132learning132", "Y2x1c3RlcjEzMmxlYXJuaW5nMTMy"),
    ("cluster132model132", "Y2x1c3RlcjEzMm1vZGVsMTMy"),
    ("cluster132token132", "Y2x1c3RlcjEzMnRva2VuMTMy"),
    ("cluster132prompt132", "Y2x1c3RlcjEzMnByb21wdDEzMg"),
    ("mirror132prompt132", "bWlycm9yMTMycHJvbXB0MTMy"),
    ("mirror132session132", "bWlycm9yMTMyc2Vzc2lvbjEzMg"),
    ("mirror132library132", "bWlycm9yMTMybGlicmFyeTEzMg"),
    ("mirror132service132", "bWlycm9yMTMyc2VydmljZTEzMg"),
    ("filter132service132", "ZmlsdGVyMTMyc2VydmljZTEzMg"),
    ("filter132gateway132", "ZmlsdGVyMTMyZ2F0ZXdheTEzMg"),
    ("filter132storage132", "ZmlsdGVyMTMyc3RvcmFnZTEzMg"),
    ("filter132network132", "ZmlsdGVyMTMybmV0d29yazEzMg"),
    ("ranking132network132", "cmFua2luZzEzMm5ldHdvcmsxMzI"),
    ("ranking132latency132", "cmFua2luZzEzMmxhdGVuY3kxMzI"),
    ("ranking132buffer132", "cmFua2luZzEzMmJ1ZmZlcjEzMg"),
    ("ranking132queue132", "cmFua2luZzEzMnF1ZXVlMTMy"),
    ("encoding132queue132", "ZW5jb2RpbmcxMzJxdWV1ZTEzMg"),
    ("encoding132worker132", "ZW5jb2RpbmcxMzJ3b3JrZXIxMzI"),
    ("encoding132kernel132", "ZW5jb2RpbmcxMzJrZXJuZWwxMzI"),
    ("encoding132signal132", "ZW5jb2RpbmcxMzJzaWduYWwxMzI"),
    ("mapping132signal132", "bWFwcGluZzEzMnNpZ25hbDEzMg"),
    ("mapping132packet132", "bWFwcGluZzEzMnBhY2tldDEzMg"),
    ("mapping132router132", "bWFwcGluZzEzMnJvdXRlcjEzMg"),
    ("mapping132cluster132", "bWFwcGluZzEzMmNsdXN0ZXIxMzI"),
    ("record132cluster132", "cmVjb3JkMTMyY2x1c3RlcjEzMg"),
    ("record132mirror132", "cmVjb3JkMTMybWlycm9yMTMy"),
    ("record132filter132", "cmVjb3JkMTMyZmlsdGVyMTMy"),
    ("record132ranking132", "cmVjb3JkMTMycmFua2luZzEzMg"),
    ("candle132ranking132", "Y2FuZGxlMTMycmFua2luZzEzMg"),
    ("candle132encoding132", "Y2FuZGxlMTMyZW5jb2RpbmcxMzI"),
    ("candle132mapping132", "Y2FuZGxlMTMybWFwcGluZzEzMg"),
    ("candle132record132", "Y2FuZGxlMTMycmVjb3JkMTMy"),
    ("thread132record132", "dGhyZWFkMTMycmVjb3JkMTMy"),
    ("thread132candle132", "dGhyZWFkMTMyY2FuZGxlMTMy"),
    ("thread132thread132", "dGhyZWFkMTMydGhyZWFkMTMy"),
    ("thread132kitten132", "dGhyZWFkMTMya2l0dGVuMTMy"),
    (
        "round 132: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTMyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 132: agentuniverse is a framework for multi agents",
        "cm91bmQgMTMyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 132: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTMyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 132: the processor reads the record then stops",
        "cm91bmQgMTMyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 132: a worker pulls the next task from the queue",
        "cm91bmQgMTMyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 132: signals travel through the network layer",
        "cm91bmQgMTMyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 132: the gateway routes each request by policy",
        "cm91bmQgMTMyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 132: memory grows until the buffer is full",
        "cm91bmQgMTMyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 132: the cluster mirrors every packet twice",
        "cm91bmQgMTMyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 132: ranking uses tokens learned from the corpus",
        "cm91bmQgMTMyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 132: a long session ends when the candle dies",
        "cm91bmQgMTMyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 132: encode the prompt then map the result",
        "cm91bmQgMTMyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 132: the kernel wakes the worker at dawn",
        "cm91bmQgMTMyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 132: service latency drops after the patch",
        "cm91bmQgMTMyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 132: the library caches every vector it sees",
        "cm91bmQgMTMyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 132: agents argue then the debate resolves",
        "cm91bmQgMTMyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 132: the filter keeps only strong matches",
        "cm91bmQgMTMyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 132: the model answers with a short reply",
        "cm91bmQgMTMyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 132: the recorder stores the reasoning trace",
        "cm91bmQgMTMyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 132: the angel watches the processor run",
        "cm91bmQgMTMyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 132: angle of the vector decides the match",
        "cm91bmQgMTMyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 132: the candle burns twice as long at night",
        "cm91bmQgMTMyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 132: a mirror of the universe in one line",
        "cm91bmQgMTMyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 132: the queue drains before the storm", "cm91bmQgMTMyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
