"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten111kitten111", "a2l0dGVuMTExa2l0dGVuMTEx"),
    ("kitten111sitting111", "a2l0dGVuMTExc2l0dGluZzExMQ"),
    ("kitten111agent111", "a2l0dGVuMTExYWdlbnQxMTE"),
    ("kitten111angle111", "a2l0dGVuMTExYW5nbGUxMTE"),
    ("sitting111angle111", "c2l0dGluZzExMWFuZ2xlMTEx"),
    ("sitting111universe111", "c2l0dGluZzExMXVuaXZlcnNlMTEx"),
    ("sitting111memory111", "c2l0dGluZzExMW1lbW9yeTExMQ"),
    ("sitting111stream111", "c2l0dGluZzExMXN0cmVhbTExMQ"),
    ("agent111stream111", "YWdlbnQxMTFzdHJlYW0xMTE"),
    ("agent111context111", "YWdlbnQxMTFjb250ZXh0MTEx"),
    ("agent111knowledge111", "YWdlbnQxMTFrbm93bGVkZ2UxMTE"),
    ("agent111vector111", "YWdlbnQxMTF2ZWN0b3IxMTE"),
    ("angle111vector111", "YW5nbGUxMTF2ZWN0b3IxMTE"),
    ("angle111processor111", "YW5nbGUxMTFwcm9jZXNzb3IxMTE"),
    ("angle111reasoning111", "YW5nbGUxMTFyZWFzb25pbmcxMTE"),
    ("angle111machine111", "YW5nbGUxMTFtYWNoaW5lMTEx"),
    ("universe111machine111", "dW5pdmVyc2UxMTFtYWNoaW5lMTEx"),
    ("universe111learning111", "dW5pdmVyc2UxMTFsZWFybmluZzExMQ"),
    ("universe111model111", "dW5pdmVyc2UxMTFtb2RlbDExMQ"),
    ("universe111token111", "dW5pdmVyc2UxMTF0b2tlbjExMQ"),
    ("memory111token111", "bWVtb3J5MTExdG9rZW4xMTE"),
    ("memory111prompt111", "bWVtb3J5MTExcHJvbXB0MTEx"),
    ("memory111session111", "bWVtb3J5MTExc2Vzc2lvbjExMQ"),
    ("memory111library111", "bWVtb3J5MTExbGlicmFyeTExMQ"),
    ("stream111library111", "c3RyZWFtMTExbGlicmFyeTExMQ"),
    ("stream111service111", "c3RyZWFtMTExc2VydmljZTExMQ"),
    ("stream111gateway111", "c3RyZWFtMTExZ2F0ZXdheTExMQ"),
    ("stream111storage111", "c3RyZWFtMTExc3RvcmFnZTExMQ"),
    ("context111storage111", "Y29udGV4dDExMXN0b3JhZ2UxMTE"),
    ("context111network111", "Y29udGV4dDExMW5ldHdvcmsxMTE"),
    ("context111latency111", "Y29udGV4dDExMWxhdGVuY3kxMTE"),
    ("context111buffer111", "Y29udGV4dDExMWJ1ZmZlcjExMQ"),
    ("knowledge111buffer111", "a25vd2xlZGdlMTExYnVmZmVyMTEx"),
    ("knowledge111queue111", "a25vd2xlZGdlMTExcXVldWUxMTE"),
    ("knowledge111worker111", "a25vd2xlZGdlMTExd29ya2VyMTEx"),
    ("knowledge111kernel111", "a25vd2xlZGdlMTExa2VybmVsMTEx"),
    ("vector111kernel111", "dmVjdG9yMTExa2VybmVsMTEx"),
    ("vector111signal111", "dmVjdG9yMTExc2lnbmFsMTEx"),
    ("vector111packet111", "dmVjdG9yMTExcGFja2V0MTEx"),
    ("vector111router111", "dmVjdG9yMTExcm91dGVyMTEx"),
    ("processor111router111", "cHJvY2Vzc29yMTExcm91dGVyMTEx"),
    ("processor111cluster111", "cHJvY2Vzc29yMTExY2x1c3RlcjExMQ"),
    ("processor111mirror111", "cHJvY2Vzc29yMTExbWlycm9yMTEx"),
    ("processor111filter111", "cHJvY2Vzc29yMTExZmlsdGVyMTEx"),
    ("reasoning111filter111", "cmVhc29uaW5nMTExZmlsdGVyMTEx"),
    ("reasoning111ranking111", "cmVhc29uaW5nMTExcmFua2luZzExMQ"),
    ("reasoning111encoding111", "cmVhc29uaW5nMTExZW5jb2RpbmcxMTE"),
    ("reasoning111mapping111", "cmVhc29uaW5nMTExbWFwcGluZzExMQ"),
    ("machine111mapping111", "bWFjaGluZTExMW1hcHBpbmcxMTE"),
    ("machine111record111", "bWFjaGluZTExMXJlY29yZDExMQ"),
    ("machine111candle111", "bWFjaGluZTExMWNhbmRsZTExMQ"),
    ("machine111thread111", "bWFjaGluZTExMXRocmVhZDExMQ"),
    ("learning111thread111", "bGVhcm5pbmcxMTF0aHJlYWQxMTE"),
    ("learning111kitten111", "bGVhcm5pbmcxMTFraXR0ZW4xMTE"),
    ("learning111sitting111", "bGVhcm5pbmcxMTFzaXR0aW5nMTEx"),
    ("learning111agent111", "bGVhcm5pbmcxMTFhZ2VudDExMQ"),
    ("model111agent111", "bW9kZWwxMTFhZ2VudDExMQ"),
    ("model111angle111", "bW9kZWwxMTFhbmdsZTExMQ"),
    ("model111universe111", "bW9kZWwxMTF1bml2ZXJzZTExMQ"),
    ("model111memory111", "bW9kZWwxMTFtZW1vcnkxMTE"),
    ("token111memory111", "dG9rZW4xMTFtZW1vcnkxMTE"),
    ("token111stream111", "dG9rZW4xMTFzdHJlYW0xMTE"),
    ("token111context111", "dG9rZW4xMTFjb250ZXh0MTEx"),
    ("token111knowledge111", "dG9rZW4xMTFrbm93bGVkZ2UxMTE"),
    ("prompt111knowledge111", "cHJvbXB0MTExa25vd2xlZGdlMTEx"),
    ("prompt111vector111", "cHJvbXB0MTExdmVjdG9yMTEx"),
    ("prompt111processor111", "cHJvbXB0MTExcHJvY2Vzc29yMTEx"),
    ("prompt111reasoning111", "cHJvbXB0MTExcmVhc29uaW5nMTEx"),
    ("session111reasoning111", "c2Vzc2lvbjExMXJlYXNvbmluZzExMQ"),
    ("session111machine111", "c2Vzc2lvbjExMW1hY2hpbmUxMTE"),
    ("session111learning111", "c2Vzc2lvbjExMWxlYXJuaW5nMTEx"),
    ("session111model111", "c2Vzc2lvbjExMW1vZGVsMTEx"),
    ("library111model111", "bGlicmFyeTExMW1vZGVsMTEx"),
    ("library111token111", "bGlicmFyeTExMXRva2VuMTEx"),
    ("library111prompt111", "bGlicmFyeTExMXByb21wdDExMQ"),
    ("library111session111", "bGlicmFyeTExMXNlc3Npb24xMTE"),
    ("service111session111", "c2VydmljZTExMXNlc3Npb24xMTE"),
    ("service111library111", "c2VydmljZTExMWxpYnJhcnkxMTE"),
    ("service111service111", "c2VydmljZTExMXNlcnZpY2UxMTE"),
    ("service111gateway111", "c2VydmljZTExMWdhdGV3YXkxMTE"),
    ("gateway111gateway111", "Z2F0ZXdheTExMWdhdGV3YXkxMTE"),
    ("gateway111storage111", "Z2F0ZXdheTExMXN0b3JhZ2UxMTE"),
    ("gateway111network111", "Z2F0ZXdheTExMW5ldHdvcmsxMTE"),
    ("gateway111latency111", "Z2F0ZXdheTExMWxhdGVuY3kxMTE"),
    ("storage111latency111", "c3RvcmFnZTExMWxhdGVuY3kxMTE"),
    ("storage111buffer111", "c3RvcmFnZTExMWJ1ZmZlcjExMQ"),
    ("storage111queue111", "c3RvcmFnZTExMXF1ZXVlMTEx"),
    ("storage111worker111", "c3RvcmFnZTExMXdvcmtlcjExMQ"),
    ("network111worker111", "bmV0d29yazExMXdvcmtlcjExMQ"),
    ("network111kernel111", "bmV0d29yazExMWtlcm5lbDExMQ"),
    ("network111signal111", "bmV0d29yazExMXNpZ25hbDExMQ"),
    ("network111packet111", "bmV0d29yazExMXBhY2tldDExMQ"),
    ("latency111packet111", "bGF0ZW5jeTExMXBhY2tldDExMQ"),
    ("latency111router111", "bGF0ZW5jeTExMXJvdXRlcjExMQ"),
    ("latency111cluster111", "bGF0ZW5jeTExMWNsdXN0ZXIxMTE"),
    ("latency111mirror111", "bGF0ZW5jeTExMW1pcnJvcjExMQ"),
    ("buffer111mirror111", "YnVmZmVyMTExbWlycm9yMTEx"),
    ("buffer111filter111", "YnVmZmVyMTExZmlsdGVyMTEx"),
    ("buffer111ranking111", "YnVmZmVyMTExcmFua2luZzExMQ"),
    ("buffer111encoding111", "YnVmZmVyMTExZW5jb2RpbmcxMTE"),
    ("queue111encoding111", "cXVldWUxMTFlbmNvZGluZzExMQ"),
    ("queue111mapping111", "cXVldWUxMTFtYXBwaW5nMTEx"),
    ("queue111record111", "cXVldWUxMTFyZWNvcmQxMTE"),
    ("queue111candle111", "cXVldWUxMTFjYW5kbGUxMTE"),
    ("worker111candle111", "d29ya2VyMTExY2FuZGxlMTEx"),
    ("worker111thread111", "d29ya2VyMTExdGhyZWFkMTEx"),
    ("worker111kitten111", "d29ya2VyMTExa2l0dGVuMTEx"),
    ("worker111sitting111", "d29ya2VyMTExc2l0dGluZzExMQ"),
    ("kernel111sitting111", "a2VybmVsMTExc2l0dGluZzExMQ"),
    ("kernel111agent111", "a2VybmVsMTExYWdlbnQxMTE"),
    ("kernel111angle111", "a2VybmVsMTExYW5nbGUxMTE"),
    ("kernel111universe111", "a2VybmVsMTExdW5pdmVyc2UxMTE"),
    ("signal111universe111", "c2lnbmFsMTExdW5pdmVyc2UxMTE"),
    ("signal111memory111", "c2lnbmFsMTExbWVtb3J5MTEx"),
    ("signal111stream111", "c2lnbmFsMTExc3RyZWFtMTEx"),
    ("signal111context111", "c2lnbmFsMTExY29udGV4dDExMQ"),
    ("packet111context111", "cGFja2V0MTExY29udGV4dDExMQ"),
    ("packet111knowledge111", "cGFja2V0MTExa25vd2xlZGdlMTEx"),
    ("packet111vector111", "cGFja2V0MTExdmVjdG9yMTEx"),
    ("packet111processor111", "cGFja2V0MTExcHJvY2Vzc29yMTEx"),
    ("router111processor111", "cm91dGVyMTExcHJvY2Vzc29yMTEx"),
    ("router111reasoning111", "cm91dGVyMTExcmVhc29uaW5nMTEx"),
    ("router111machine111", "cm91dGVyMTExbWFjaGluZTExMQ"),
    ("router111learning111", "cm91dGVyMTExbGVhcm5pbmcxMTE"),
    ("cluster111learning111", "Y2x1c3RlcjExMWxlYXJuaW5nMTEx"),
    ("cluster111model111", "Y2x1c3RlcjExMW1vZGVsMTEx"),
    ("cluster111token111", "Y2x1c3RlcjExMXRva2VuMTEx"),
    ("cluster111prompt111", "Y2x1c3RlcjExMXByb21wdDExMQ"),
    ("mirror111prompt111", "bWlycm9yMTExcHJvbXB0MTEx"),
    ("mirror111session111", "bWlycm9yMTExc2Vzc2lvbjExMQ"),
    ("mirror111library111", "bWlycm9yMTExbGlicmFyeTExMQ"),
    ("mirror111service111", "bWlycm9yMTExc2VydmljZTExMQ"),
    ("filter111service111", "ZmlsdGVyMTExc2VydmljZTExMQ"),
    ("filter111gateway111", "ZmlsdGVyMTExZ2F0ZXdheTExMQ"),
    ("filter111storage111", "ZmlsdGVyMTExc3RvcmFnZTExMQ"),
    ("filter111network111", "ZmlsdGVyMTExbmV0d29yazExMQ"),
    ("ranking111network111", "cmFua2luZzExMW5ldHdvcmsxMTE"),
    ("ranking111latency111", "cmFua2luZzExMWxhdGVuY3kxMTE"),
    ("ranking111buffer111", "cmFua2luZzExMWJ1ZmZlcjExMQ"),
    ("ranking111queue111", "cmFua2luZzExMXF1ZXVlMTEx"),
    ("encoding111queue111", "ZW5jb2RpbmcxMTFxdWV1ZTExMQ"),
    ("encoding111worker111", "ZW5jb2RpbmcxMTF3b3JrZXIxMTE"),
    ("encoding111kernel111", "ZW5jb2RpbmcxMTFrZXJuZWwxMTE"),
    ("encoding111signal111", "ZW5jb2RpbmcxMTFzaWduYWwxMTE"),
    ("mapping111signal111", "bWFwcGluZzExMXNpZ25hbDExMQ"),
    ("mapping111packet111", "bWFwcGluZzExMXBhY2tldDExMQ"),
    ("mapping111router111", "bWFwcGluZzExMXJvdXRlcjExMQ"),
    ("mapping111cluster111", "bWFwcGluZzExMWNsdXN0ZXIxMTE"),
    ("record111cluster111", "cmVjb3JkMTExY2x1c3RlcjExMQ"),
    ("record111mirror111", "cmVjb3JkMTExbWlycm9yMTEx"),
    ("record111filter111", "cmVjb3JkMTExZmlsdGVyMTEx"),
    ("record111ranking111", "cmVjb3JkMTExcmFua2luZzExMQ"),
    ("candle111ranking111", "Y2FuZGxlMTExcmFua2luZzExMQ"),
    ("candle111encoding111", "Y2FuZGxlMTExZW5jb2RpbmcxMTE"),
    ("candle111mapping111", "Y2FuZGxlMTExbWFwcGluZzExMQ"),
    ("candle111record111", "Y2FuZGxlMTExcmVjb3JkMTEx"),
    ("thread111record111", "dGhyZWFkMTExcmVjb3JkMTEx"),
    ("thread111candle111", "dGhyZWFkMTExY2FuZGxlMTEx"),
    ("thread111thread111", "dGhyZWFkMTExdGhyZWFkMTEx"),
    ("thread111kitten111", "dGhyZWFkMTExa2l0dGVuMTEx"),
    (
        "round 111: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTExOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 111: agentuniverse is a framework for multi agents",
        "cm91bmQgMTExOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 111: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTExOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 111: the processor reads the record then stops",
        "cm91bmQgMTExOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 111: a worker pulls the next task from the queue",
        "cm91bmQgMTExOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 111: signals travel through the network layer",
        "cm91bmQgMTExOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 111: the gateway routes each request by policy",
        "cm91bmQgMTExOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 111: memory grows until the buffer is full",
        "cm91bmQgMTExOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 111: the cluster mirrors every packet twice",
        "cm91bmQgMTExOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 111: ranking uses tokens learned from the corpus",
        "cm91bmQgMTExOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 111: a long session ends when the candle dies",
        "cm91bmQgMTExOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 111: encode the prompt then map the result",
        "cm91bmQgMTExOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 111: the kernel wakes the worker at dawn",
        "cm91bmQgMTExOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 111: service latency drops after the patch",
        "cm91bmQgMTExOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 111: the library caches every vector it sees",
        "cm91bmQgMTExOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 111: agents argue then the debate resolves",
        "cm91bmQgMTExOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 111: the filter keeps only strong matches",
        "cm91bmQgMTExOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 111: the model answers with a short reply",
        "cm91bmQgMTExOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 111: the recorder stores the reasoning trace",
        "cm91bmQgMTExOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 111: the angel watches the processor run",
        "cm91bmQgMTExOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 111: angle of the vector decides the match",
        "cm91bmQgMTExOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 111: the candle burns twice as long at night",
        "cm91bmQgMTExOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 111: a mirror of the universe in one line",
        "cm91bmQgMTExOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 111: the queue drains before the storm", "cm91bmQgMTExOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
