"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten138kitten138", "a2l0dGVuMTM4a2l0dGVuMTM4"),
    ("kitten138sitting138", "a2l0dGVuMTM4c2l0dGluZzEzOA"),
    ("kitten138agent138", "a2l0dGVuMTM4YWdlbnQxMzg"),
    ("kitten138angle138", "a2l0dGVuMTM4YW5nbGUxMzg"),
    ("sitting138angle138", "c2l0dGluZzEzOGFuZ2xlMTM4"),
    ("sitting138universe138", "c2l0dGluZzEzOHVuaXZlcnNlMTM4"),
    ("sitting138memory138", "c2l0dGluZzEzOG1lbW9yeTEzOA"),
    ("sitting138stream138", "c2l0dGluZzEzOHN0cmVhbTEzOA"),
    ("agent138stream138", "YWdlbnQxMzhzdHJlYW0xMzg"),
    ("agent138context138", "YWdlbnQxMzhjb250ZXh0MTM4"),
    ("agent138knowledge138", "YWdlbnQxMzhrbm93bGVkZ2UxMzg"),
    ("agent138vector138", "YWdlbnQxMzh2ZWN0b3IxMzg"),
    ("angle138vector138", "YW5nbGUxMzh2ZWN0b3IxMzg"),
    ("angle138processor138", "YW5nbGUxMzhwcm9jZXNzb3IxMzg"),
    ("angle138reasoning138", "YW5nbGUxMzhyZWFzb25pbmcxMzg"),
    ("angle138machine138", "YW5nbGUxMzhtYWNoaW5lMTM4"),
    ("universe138machine138", "dW5pdmVyc2UxMzhtYWNoaW5lMTM4"),
    ("universe138learning138", "dW5pdmVyc2UxMzhsZWFybmluZzEzOA"),
    ("universe138model138", "dW5pdmVyc2UxMzhtb2RlbDEzOA"),
    ("universe138token138", "dW5pdmVyc2UxMzh0b2tlbjEzOA"),
    ("memory138token138", "bWVtb3J5MTM4dG9rZW4xMzg"),
    ("memory138prompt138", "bWVtb3J5MTM4cHJvbXB0MTM4"),
    ("memory138session138", "bWVtb3J5MTM4c2Vzc2lvbjEzOA"),
    ("memory138library138", "bWVtb3J5MTM4bGlicmFyeTEzOA"),
    ("stream138library138", "c3RyZWFtMTM4bGlicmFyeTEzOA"),
    ("stream138service138", "c3RyZWFtMTM4c2VydmljZTEzOA"),
    ("stream138gateway138", "c3RyZWFtMTM4Z2F0ZXdheTEzOA"),
    ("stream138storage138", "c3RyZWFtMTM4c3RvcmFnZTEzOA"),
    ("context138storage138", "Y29udGV4dDEzOHN0b3JhZ2UxMzg"),
    ("context138network138", "Y29udGV4dDEzOG5ldHdvcmsxMzg"),
    ("context138latency138", "Y29udGV4dDEzOGxhdGVuY3kxMzg"),
    ("context138buffer138", "Y29udGV4dDEzOGJ1ZmZlcjEzOA"),
    ("knowledge138buffer138", "a25vd2xlZGdlMTM4YnVmZmVyMTM4"),
    ("knowledge138queue138", "a25vd2xlZGdlMTM4cXVldWUxMzg"),
    ("knowledge138worker138", "a25vd2xlZGdlMTM4d29ya2VyMTM4"),
    ("knowledge138kernel138", "a25vd2xlZGdlMTM4a2VybmVsMTM4"),
    ("vector138kernel138", "dmVjdG9yMTM4a2VybmVsMTM4"),
    ("vector138signal138", "dmVjdG9yMTM4c2lnbmFsMTM4"),
    ("vector138packet138", "dmVjdG9yMTM4cGFja2V0MTM4"),
    ("vector138router138", "dmVjdG9yMTM4cm91dGVyMTM4"),
    ("processor138router138", "cHJvY2Vzc29yMTM4cm91dGVyMTM4"),
    ("processor138cluster138", "cHJvY2Vzc29yMTM4Y2x1c3RlcjEzOA"),
    ("processor138mirror138", "cHJvY2Vzc29yMTM4bWlycm9yMTM4"),
    ("processor138filter138", "cHJvY2Vzc29yMTM4ZmlsdGVyMTM4"),
    ("reasoning138filter138", "cmVhc29uaW5nMTM4ZmlsdGVyMTM4"),
    ("reasoning138ranking138", "cmVhc29uaW5nMTM4cmFua2luZzEzOA"),
    ("reasoning138encoding138", "cmVhc29uaW5nMTM4ZW5jb2RpbmcxMzg"),
    ("reasoning138mapping138", "cmVhc29uaW5nMTM4bWFwcGluZzEzOA"),
    ("machine138mapping138", "bWFjaGluZTEzOG1hcHBpbmcxMzg"),
    ("machine138record138", "bWFjaGluZTEzOHJlY29yZDEzOA"),
    ("machine138candle138", "bWFjaGluZTEzOGNhbmRsZTEzOA"),
    ("machine138thread138", "bWFjaGluZTEzOHRocmVhZDEzOA"),
    ("learning138thread138", "bGVhcm5pbmcxMzh0aHJlYWQxMzg"),
    ("learning138kitten138", "bGVhcm5pbmcxMzhraXR0ZW4xMzg"),
    ("learning138sitting138", "bGVhcm5pbmcxMzhzaXR0aW5nMTM4"),
    ("learning138agent138", "bGVhcm5pbmcxMzhhZ2VudDEzOA"),
    ("model138agent138", "bW9kZWwxMzhhZ2VudDEzOA"),
    ("model138angle138", "bW9kZWwxMzhhbmdsZTEzOA"),
    ("model138universe138", "bW9kZWwxMzh1bml2ZXJzZTEzOA"),
    ("model138memory138", "bW9kZWwxMzhtZW1vcnkxMzg"),
    ("token138memory138", "dG9rZW4xMzhtZW1vcnkxMzg"),
    ("token138stream138", "dG9rZW4xMzhzdHJlYW0xMzg"),
    ("token138context138", "dG9rZW4xMzhjb250ZXh0MTM4"),
    ("token138knowledge138", "dG9rZW4xMzhrbm93bGVkZ2UxMzg"),
    ("prompt138knowledge138", "cHJvbXB0MTM4a25vd2xlZGdlMTM4"),
    ("prompt138vector138", "cHJvbXB0MTM4dmVjdG9yMTM4"),
    ("prompt138processor138", "cHJvbXB0MTM4cHJvY2Vzc29yMTM4"),
    ("prompt138reasoning138", "cHJvbXB0MTM4cmVhc29uaW5nMTM4"),
    ("session138reasoning138", "c2Vzc2lvbjEzOHJlYXNvbmluZzEzOA"),
    ("session138machine138", "c2Vzc2lvbjEzOG1hY2hpbmUxMzg"),
    ("session138learning138", "c2Vzc2lvbjEzOGxlYXJuaW5nMTM4"),
    ("session138model138", "c2Vzc2lvbjEzOG1vZGVsMTM4"),
    ("library138model138", "bGlicmFyeTEzOG1vZGVsMTM4"),
    ("library138token138", "bGlicmFyeTEzOHRva2VuMTM4"),
    ("library138prompt138", "bGlicmFyeTEzOHByb21wdDEzOA"),
    ("library138session138", "bGlicmFyeTEzOHNlc3Npb24xMzg"),
    ("service138session138", "c2VydmljZTEzOHNlc3Npb24xMzg"),
    ("service138library138", "c2VydmljZTEzOGxpYnJhcnkxMzg"),
    ("service138service138", "c2VydmljZTEzOHNlcnZpY2UxMzg"),
    ("service138gateway138", "c2VydmljZTEzOGdhdGV3YXkxMzg"),
    ("gateway138gateway138", "Z2F0ZXdheTEzOGdhdGV3YXkxMzg"),
    ("gateway138storage138", "Z2F0ZXdheTEzOHN0b3JhZ2UxMzg"),
    ("gateway138network138", "Z2F0ZXdheTEzOG5ldHdvcmsxMzg"),
    ("gateway138latency138", "Z2F0ZXdheTEzOGxhdGVuY3kxMzg"),
    ("storage138latency138", "c3RvcmFnZTEzOGxhdGVuY3kxMzg"),
    ("storage138buffer138", "c3RvcmFnZTEzOGJ1ZmZlcjEzOA"),
    ("storage138queue138", "c3RvcmFnZTEzOHF1ZXVlMTM4"),
    ("storage138worker138", "c3RvcmFnZTEzOHdvcmtlcjEzOA"),
    ("network138worker138", "bmV0d29yazEzOHdvcmtlcjEzOA"),
    ("network138kernel138", "bmV0d29yazEzOGtlcm5lbDEzOA"),
    ("network138signal138", "bmV0d29yazEzOHNpZ25hbDEzOA"),
    ("network138packet138", "bmV0d29yazEzOHBhY2tldDEzOA"),
    ("latency138packet138", "bGF0ZW5jeTEzOHBhY2tldDEzOA"),
    ("latency138router138", "bGF0ZW5jeTEzOHJvdXRlcjEzOA"),
    ("latency138cluster138", "bGF0ZW5jeTEzOGNsdXN0ZXIxMzg"),
    ("latency138mirror138", "bGF0ZW5jeTEzOG1pcnJvcjEzOA"),
    ("buffer138mirror138", "YnVmZmVyMTM4bWlycm9yMTM4"),
    ("buffer138filter138", "YnVmZmVyMTM4ZmlsdGVyMTM4"),
    ("buffer138ranking138", "YnVmZmVyMTM4cmFua2luZzEzOA"),
    ("buffer138encoding138", "YnVmZmVyMTM4ZW5jb2RpbmcxMzg"),
    ("queue138encoding138", "cXVldWUxMzhlbmNvZGluZzEzOA"),
    ("queue138mapping138", "cXVldWUxMzhtYXBwaW5nMTM4"),
    ("queue138record138", "cXVldWUxMzhyZWNvcmQxMzg"),
    ("queue138candle138", "cXVldWUxMzhjYW5kbGUxMzg"),
    ("worker138candle138", "d29ya2VyMTM4Y2FuZGxlMTM4"),
    ("worker138thread138", "d29ya2VyMTM4dGhyZWFkMTM4"),
    ("worker138kitten138", "d29ya2VyMTM4a2l0dGVuMTM4"),
    ("worker138sitting138", "d29ya2VyMTM4c2l0dGluZzEzOA"),
    ("kernel138sitting138", "a2VybmVsMTM4c2l0dGluZzEzOA"),
    ("kernel138agent138", "a2VybmVsMTM4YWdlbnQxMzg"),
    ("kernel138angle138", "a2VybmVsMTM4YW5nbGUxMzg"),
    ("kernel138universe138", "a2VybmVsMTM4dW5pdmVyc2UxMzg"),
    ("signal138universe138", "c2lnbmFsMTM4dW5pdmVyc2UxMzg"),
    ("signal138memory138", "c2lnbmFsMTM4bWVtb3J5MTM4"),
    ("signal138stream138", "c2lnbmFsMTM4c3RyZWFtMTM4"),
    ("signal138context138", "c2lnbmFsMTM4Y29udGV4dDEzOA"),
    ("packet138context138", "cGFja2V0MTM4Y29udGV4dDEzOA"),
    ("packet138knowledge138", "cGFja2V0MTM4a25vd2xlZGdlMTM4"),
    ("packet138vector138", "cGFja2V0MTM4dmVjdG9yMTM4"),
    ("packet138processor138", "cGFja2V0MTM4cHJvY2Vzc29yMTM4"),
    ("router138processor138", "cm91dGVyMTM4cHJvY2Vzc29yMTM4"),
    ("router138reasoning138", "cm91dGVyMTM4cmVhc29uaW5nMTM4"),
    ("router138machine138", "cm91dGVyMTM4bWFjaGluZTEzOA"),
    ("router138learning138", "cm91dGVyMTM4bGVhcm5pbmcxMzg"),
    ("cluster138learning138", "Y2x1c3RlcjEzOGxlYXJuaW5nMTM4"),
    ("cluster138model138", "Y2x1c3RlcjEzOG1vZGVsMTM4"),
    ("cluster138token138", "Y2x1c3RlcjEzOHRva2VuMTM4"),
    ("cluster138prompt138", "Y2x1c3RlcjEzOHByb21wdDEzOA"),
    ("mirror138prompt138", "bWlycm9yMTM4cHJvbXB0MTM4"),
    ("mirror138session138", "bWlycm9yMTM4c2Vzc2lvbjEzOA"),
    ("mirror138library138", "bWlycm9yMTM4bGlicmFyeTEzOA"),
    ("mirror138service138", "bWlycm9yMTM4c2VydmljZTEzOA"),
    ("filter138service138", "ZmlsdGVyMTM4c2VydmljZTEzOA"),
    ("filter138gateway138", "ZmlsdGVyMTM4Z2F0ZXdheTEzOA"),
    ("filter138storage138", "ZmlsdGVyMTM4c3RvcmFnZTEzOA"),
    ("filter138network138", "ZmlsdGVyMTM4bmV0d29yazEzOA"),
    ("ranking138network138", "cmFua2luZzEzOG5ldHdvcmsxMzg"),
    ("ranking138latency138", "cmFua2luZzEzOGxhdGVuY3kxMzg"),
    ("ranking138buffer138", "cmFua2luZzEzOGJ1ZmZlcjEzOA"),
    ("ranking138queue138", "cmFua2luZzEzOHF1ZXVlMTM4"),
    ("encoding138queue138", "ZW5jb2RpbmcxMzhxdWV1ZTEzOA"),
    ("encoding138worker138", "ZW5jb2RpbmcxMzh3b3JrZXIxMzg"),
    ("encoding138kernel138", "ZW5jb2RpbmcxMzhrZXJuZWwxMzg"),
    ("encoding138signal138", "ZW5jb2RpbmcxMzhzaWduYWwxMzg"),
    ("mapping138signal138", "bWFwcGluZzEzOHNpZ25hbDEzOA"),
    ("mapping138packet138", "bWFwcGluZzEzOHBhY2tldDEzOA"),
    ("mapping138router138", "bWFwcGluZzEzOHJvdXRlcjEzOA"),
    ("mapping138cluster138", "bWFwcGluZzEzOGNsdXN0ZXIxMzg"),
    ("record138cluster138", "cmVjb3JkMTM4Y2x1c3RlcjEzOA"),
    ("record138mirror138", "cmVjb3JkMTM4bWlycm9yMTM4"),
    ("record138filter138", "cmVjb3JkMTM4ZmlsdGVyMTM4"),
    ("record138ranking138", "cmVjb3JkMTM4cmFua2luZzEzOA"),
    ("candle138ranking138", "Y2FuZGxlMTM4cmFua2luZzEzOA"),
    ("candle138encoding138", "Y2FuZGxlMTM4ZW5jb2RpbmcxMzg"),
    ("candle138mapping138", "Y2FuZGxlMTM4bWFwcGluZzEzOA"),
    ("candle138record138", "Y2FuZGxlMTM4cmVjb3JkMTM4"),
    ("thread138record138", "dGhyZWFkMTM4cmVjb3JkMTM4"),
    ("thread138candle138", "dGhyZWFkMTM4Y2FuZGxlMTM4"),
    ("thread138thread138", "dGhyZWFkMTM4dGhyZWFkMTM4"),
    ("thread138kitten138", "dGhyZWFkMTM4a2l0dGVuMTM4"),
    (
        "round 138: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTM4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 138: agentuniverse is a framework for multi agents",
        "cm91bmQgMTM4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 138: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTM4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 138: the processor reads the record then stops",
        "cm91bmQgMTM4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 138: a worker pulls the next task from the queue",
        "cm91bmQgMTM4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 138: signals travel through the network layer",
        "cm91bmQgMTM4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 138: the gateway routes each request by policy",
        "cm91bmQgMTM4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 138: memory grows until the buffer is full",
        "cm91bmQgMTM4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 138: the cluster mirrors every packet twice",
        "cm91bmQgMTM4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 138: ranking uses tokens learned from the corpus",
        "cm91bmQgMTM4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 138: a long session ends when the candle dies",
        "cm91bmQgMTM4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 138: encode the prompt then map the result",
        "cm91bmQgMTM4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 138: the kernel wakes the worker at dawn",
        "cm91bmQgMTM4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 138: service latency drops after the patch",
        "cm91bmQgMTM4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 138: the library caches every vector it sees",
        "cm91bmQgMTM4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 138: agents argue then the debate resolves",
        "cm91bmQgMTM4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 138: the filter keeps only strong matches",
        "cm91bmQgMTM4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 138: the model answers with a short reply",
        "cm91bmQgMTM4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 138: the recorder stores the reasoning trace",
        "cm91bmQgMTM4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 138: the angel watches the processor run",
        "cm91bmQgMTM4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 138: angle of the vector decides the match",
        "cm91bmQgMTM4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 138: the candle burns twice as long at night",
        "cm91bmQgMTM4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 138: a mirror of the universe in one line",
        "cm91bmQgMTM4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 138: the queue drains before the storm", "cm91bmQgMTM4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
