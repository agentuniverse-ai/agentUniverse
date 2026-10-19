"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten736kitten736", "a2l0dGVuNzM2a2l0dGVuNzM2"),
    ("kitten736sitting736", "a2l0dGVuNzM2c2l0dGluZzczNg"),
    ("kitten736agent736", "a2l0dGVuNzM2YWdlbnQ3MzY"),
    ("kitten736angle736", "a2l0dGVuNzM2YW5nbGU3MzY"),
    ("sitting736angle736", "c2l0dGluZzczNmFuZ2xlNzM2"),
    ("sitting736universe736", "c2l0dGluZzczNnVuaXZlcnNlNzM2"),
    ("sitting736memory736", "c2l0dGluZzczNm1lbW9yeTczNg"),
    ("sitting736stream736", "c2l0dGluZzczNnN0cmVhbTczNg"),
    ("agent736stream736", "YWdlbnQ3MzZzdHJlYW03MzY"),
    ("agent736context736", "YWdlbnQ3MzZjb250ZXh0NzM2"),
    ("agent736knowledge736", "YWdlbnQ3MzZrbm93bGVkZ2U3MzY"),
    ("agent736vector736", "YWdlbnQ3MzZ2ZWN0b3I3MzY"),
    ("angle736vector736", "YW5nbGU3MzZ2ZWN0b3I3MzY"),
    ("angle736processor736", "YW5nbGU3MzZwcm9jZXNzb3I3MzY"),
    ("angle736reasoning736", "YW5nbGU3MzZyZWFzb25pbmc3MzY"),
    ("angle736machine736", "YW5nbGU3MzZtYWNoaW5lNzM2"),
    ("universe736machine736", "dW5pdmVyc2U3MzZtYWNoaW5lNzM2"),
    ("universe736learning736", "dW5pdmVyc2U3MzZsZWFybmluZzczNg"),
    ("universe736model736", "dW5pdmVyc2U3MzZtb2RlbDczNg"),
    ("universe736token736", "dW5pdmVyc2U3MzZ0b2tlbjczNg"),
    ("memory736token736", "bWVtb3J5NzM2dG9rZW43MzY"),
    ("memory736prompt736", "bWVtb3J5NzM2cHJvbXB0NzM2"),
    ("memory736session736", "bWVtb3J5NzM2c2Vzc2lvbjczNg"),
    ("memory736library736", "bWVtb3J5NzM2bGlicmFyeTczNg"),
    ("stream736library736", "c3RyZWFtNzM2bGlicmFyeTczNg"),
    ("stream736service736", "c3RyZWFtNzM2c2VydmljZTczNg"),
    ("stream736gateway736", "c3RyZWFtNzM2Z2F0ZXdheTczNg"),
    ("stream736storage736", "c3RyZWFtNzM2c3RvcmFnZTczNg"),
    ("context736storage736", "Y29udGV4dDczNnN0b3JhZ2U3MzY"),
    ("context736network736", "Y29udGV4dDczNm5ldHdvcms3MzY"),
    ("context736latency736", "Y29udGV4dDczNmxhdGVuY3k3MzY"),
    ("context736buffer736", "Y29udGV4dDczNmJ1ZmZlcjczNg"),
    ("knowledge736buffer736", "a25vd2xlZGdlNzM2YnVmZmVyNzM2"),
    ("knowledge736queue736", "a25vd2xlZGdlNzM2cXVldWU3MzY"),
    ("knowledge736worker736", "a25vd2xlZGdlNzM2d29ya2VyNzM2"),
    ("knowledge736kernel736", "a25vd2xlZGdlNzM2a2VybmVsNzM2"),
    ("vector736kernel736", "dmVjdG9yNzM2a2VybmVsNzM2"),
    ("vector736signal736", "dmVjdG9yNzM2c2lnbmFsNzM2"),
    ("vector736packet736", "dmVjdG9yNzM2cGFja2V0NzM2"),
    ("vector736router736", "dmVjdG9yNzM2cm91dGVyNzM2"),
    ("processor736router736", "cHJvY2Vzc29yNzM2cm91dGVyNzM2"),
    ("processor736cluster736", "cHJvY2Vzc29yNzM2Y2x1c3RlcjczNg"),
    ("processor736mirror736", "cHJvY2Vzc29yNzM2bWlycm9yNzM2"),
    ("processor736filter736", "cHJvY2Vzc29yNzM2ZmlsdGVyNzM2"),
    ("reasoning736filter736", "cmVhc29uaW5nNzM2ZmlsdGVyNzM2"),
    ("reasoning736ranking736", "cmVhc29uaW5nNzM2cmFua2luZzczNg"),
    ("reasoning736encoding736", "cmVhc29uaW5nNzM2ZW5jb2Rpbmc3MzY"),
    ("reasoning736mapping736", "cmVhc29uaW5nNzM2bWFwcGluZzczNg"),
    ("machine736mapping736", "bWFjaGluZTczNm1hcHBpbmc3MzY"),
    ("machine736record736", "bWFjaGluZTczNnJlY29yZDczNg"),
    ("machine736candle736", "bWFjaGluZTczNmNhbmRsZTczNg"),
    ("machine736thread736", "bWFjaGluZTczNnRocmVhZDczNg"),
    ("learning736thread736", "bGVhcm5pbmc3MzZ0aHJlYWQ3MzY"),
    ("learning736kitten736", "bGVhcm5pbmc3MzZraXR0ZW43MzY"),
    ("learning736sitting736", "bGVhcm5pbmc3MzZzaXR0aW5nNzM2"),
    ("learning736agent736", "bGVhcm5pbmc3MzZhZ2VudDczNg"),
    ("model736agent736", "bW9kZWw3MzZhZ2VudDczNg"),
    ("model736angle736", "bW9kZWw3MzZhbmdsZTczNg"),
    ("model736universe736", "bW9kZWw3MzZ1bml2ZXJzZTczNg"),
    ("model736memory736", "bW9kZWw3MzZtZW1vcnk3MzY"),
    ("token736memory736", "dG9rZW43MzZtZW1vcnk3MzY"),
    ("token736stream736", "dG9rZW43MzZzdHJlYW03MzY"),
    ("token736context736", "dG9rZW43MzZjb250ZXh0NzM2"),
    ("token736knowledge736", "dG9rZW43MzZrbm93bGVkZ2U3MzY"),
    ("prompt736knowledge736", "cHJvbXB0NzM2a25vd2xlZGdlNzM2"),
    ("prompt736vector736", "cHJvbXB0NzM2dmVjdG9yNzM2"),
    ("prompt736processor736", "cHJvbXB0NzM2cHJvY2Vzc29yNzM2"),
    ("prompt736reasoning736", "cHJvbXB0NzM2cmVhc29uaW5nNzM2"),
    ("session736reasoning736", "c2Vzc2lvbjczNnJlYXNvbmluZzczNg"),
    ("session736machine736", "c2Vzc2lvbjczNm1hY2hpbmU3MzY"),
    ("session736learning736", "c2Vzc2lvbjczNmxlYXJuaW5nNzM2"),
    ("session736model736", "c2Vzc2lvbjczNm1vZGVsNzM2"),
    ("library736model736", "bGlicmFyeTczNm1vZGVsNzM2"),
    ("library736token736", "bGlicmFyeTczNnRva2VuNzM2"),
    ("library736prompt736", "bGlicmFyeTczNnByb21wdDczNg"),
    ("library736session736", "bGlicmFyeTczNnNlc3Npb243MzY"),
    ("service736session736", "c2VydmljZTczNnNlc3Npb243MzY"),
    ("service736library736", "c2VydmljZTczNmxpYnJhcnk3MzY"),
    ("service736service736", "c2VydmljZTczNnNlcnZpY2U3MzY"),
    ("service736gateway736", "c2VydmljZTczNmdhdGV3YXk3MzY"),
    ("gateway736gateway736", "Z2F0ZXdheTczNmdhdGV3YXk3MzY"),
    ("gateway736storage736", "Z2F0ZXdheTczNnN0b3JhZ2U3MzY"),
    ("gateway736network736", "Z2F0ZXdheTczNm5ldHdvcms3MzY"),
    ("gateway736latency736", "Z2F0ZXdheTczNmxhdGVuY3k3MzY"),
    ("storage736latency736", "c3RvcmFnZTczNmxhdGVuY3k3MzY"),
    ("storage736buffer736", "c3RvcmFnZTczNmJ1ZmZlcjczNg"),
    ("storage736queue736", "c3RvcmFnZTczNnF1ZXVlNzM2"),
    ("storage736worker736", "c3RvcmFnZTczNndvcmtlcjczNg"),
    ("network736worker736", "bmV0d29yazczNndvcmtlcjczNg"),
    ("network736kernel736", "bmV0d29yazczNmtlcm5lbDczNg"),
    ("network736signal736", "bmV0d29yazczNnNpZ25hbDczNg"),
    ("network736packet736", "bmV0d29yazczNnBhY2tldDczNg"),
    ("latency736packet736", "bGF0ZW5jeTczNnBhY2tldDczNg"),
    ("latency736router736", "bGF0ZW5jeTczNnJvdXRlcjczNg"),
    ("latency736cluster736", "bGF0ZW5jeTczNmNsdXN0ZXI3MzY"),
    ("latency736mirror736", "bGF0ZW5jeTczNm1pcnJvcjczNg"),
    ("buffer736mirror736", "YnVmZmVyNzM2bWlycm9yNzM2"),
    ("buffer736filter736", "YnVmZmVyNzM2ZmlsdGVyNzM2"),
    ("buffer736ranking736", "YnVmZmVyNzM2cmFua2luZzczNg"),
    ("buffer736encoding736", "YnVmZmVyNzM2ZW5jb2Rpbmc3MzY"),
    ("queue736encoding736", "cXVldWU3MzZlbmNvZGluZzczNg"),
    ("queue736mapping736", "cXVldWU3MzZtYXBwaW5nNzM2"),
    ("queue736record736", "cXVldWU3MzZyZWNvcmQ3MzY"),
    ("queue736candle736", "cXVldWU3MzZjYW5kbGU3MzY"),
    ("worker736candle736", "d29ya2VyNzM2Y2FuZGxlNzM2"),
    ("worker736thread736", "d29ya2VyNzM2dGhyZWFkNzM2"),
    ("worker736kitten736", "d29ya2VyNzM2a2l0dGVuNzM2"),
    ("worker736sitting736", "d29ya2VyNzM2c2l0dGluZzczNg"),
    ("kernel736sitting736", "a2VybmVsNzM2c2l0dGluZzczNg"),
    ("kernel736agent736", "a2VybmVsNzM2YWdlbnQ3MzY"),
    ("kernel736angle736", "a2VybmVsNzM2YW5nbGU3MzY"),
    ("kernel736universe736", "a2VybmVsNzM2dW5pdmVyc2U3MzY"),
    ("signal736universe736", "c2lnbmFsNzM2dW5pdmVyc2U3MzY"),
    ("signal736memory736", "c2lnbmFsNzM2bWVtb3J5NzM2"),
    ("signal736stream736", "c2lnbmFsNzM2c3RyZWFtNzM2"),
    ("signal736context736", "c2lnbmFsNzM2Y29udGV4dDczNg"),
    ("packet736context736", "cGFja2V0NzM2Y29udGV4dDczNg"),
    ("packet736knowledge736", "cGFja2V0NzM2a25vd2xlZGdlNzM2"),
    ("packet736vector736", "cGFja2V0NzM2dmVjdG9yNzM2"),
    ("packet736processor736", "cGFja2V0NzM2cHJvY2Vzc29yNzM2"),
    ("router736processor736", "cm91dGVyNzM2cHJvY2Vzc29yNzM2"),
    ("router736reasoning736", "cm91dGVyNzM2cmVhc29uaW5nNzM2"),
    ("router736machine736", "cm91dGVyNzM2bWFjaGluZTczNg"),
    ("router736learning736", "cm91dGVyNzM2bGVhcm5pbmc3MzY"),
    ("cluster736learning736", "Y2x1c3RlcjczNmxlYXJuaW5nNzM2"),
    ("cluster736model736", "Y2x1c3RlcjczNm1vZGVsNzM2"),
    ("cluster736token736", "Y2x1c3RlcjczNnRva2VuNzM2"),
    ("cluster736prompt736", "Y2x1c3RlcjczNnByb21wdDczNg"),
    ("mirror736prompt736", "bWlycm9yNzM2cHJvbXB0NzM2"),
    ("mirror736session736", "bWlycm9yNzM2c2Vzc2lvbjczNg"),
    ("mirror736library736", "bWlycm9yNzM2bGlicmFyeTczNg"),
    ("mirror736service736", "bWlycm9yNzM2c2VydmljZTczNg"),
    ("filter736service736", "ZmlsdGVyNzM2c2VydmljZTczNg"),
    ("filter736gateway736", "ZmlsdGVyNzM2Z2F0ZXdheTczNg"),
    ("filter736storage736", "ZmlsdGVyNzM2c3RvcmFnZTczNg"),
    ("filter736network736", "ZmlsdGVyNzM2bmV0d29yazczNg"),
    ("ranking736network736", "cmFua2luZzczNm5ldHdvcms3MzY"),
    ("ranking736latency736", "cmFua2luZzczNmxhdGVuY3k3MzY"),
    ("ranking736buffer736", "cmFua2luZzczNmJ1ZmZlcjczNg"),
    ("ranking736queue736", "cmFua2luZzczNnF1ZXVlNzM2"),
    ("encoding736queue736", "ZW5jb2Rpbmc3MzZxdWV1ZTczNg"),
    ("encoding736worker736", "ZW5jb2Rpbmc3MzZ3b3JrZXI3MzY"),
    ("encoding736kernel736", "ZW5jb2Rpbmc3MzZrZXJuZWw3MzY"),
    ("encoding736signal736", "ZW5jb2Rpbmc3MzZzaWduYWw3MzY"),
    ("mapping736signal736", "bWFwcGluZzczNnNpZ25hbDczNg"),
    ("mapping736packet736", "bWFwcGluZzczNnBhY2tldDczNg"),
    ("mapping736router736", "bWFwcGluZzczNnJvdXRlcjczNg"),
    ("mapping736cluster736", "bWFwcGluZzczNmNsdXN0ZXI3MzY"),
    ("record736cluster736", "cmVjb3JkNzM2Y2x1c3RlcjczNg"),
    ("record736mirror736", "cmVjb3JkNzM2bWlycm9yNzM2"),
    ("record736filter736", "cmVjb3JkNzM2ZmlsdGVyNzM2"),
    ("record736ranking736", "cmVjb3JkNzM2cmFua2luZzczNg"),
    ("candle736ranking736", "Y2FuZGxlNzM2cmFua2luZzczNg"),
    ("candle736encoding736", "Y2FuZGxlNzM2ZW5jb2Rpbmc3MzY"),
    ("candle736mapping736", "Y2FuZGxlNzM2bWFwcGluZzczNg"),
    ("candle736record736", "Y2FuZGxlNzM2cmVjb3JkNzM2"),
    ("thread736record736", "dGhyZWFkNzM2cmVjb3JkNzM2"),
    ("thread736candle736", "dGhyZWFkNzM2Y2FuZGxlNzM2"),
    ("thread736thread736", "dGhyZWFkNzM2dGhyZWFkNzM2"),
    ("thread736kitten736", "dGhyZWFkNzM2a2l0dGVuNzM2"),
    (
        "round 736: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzM2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 736: agentuniverse is a framework for multi agents",
        "cm91bmQgNzM2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 736: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzM2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 736: the processor reads the record then stops",
        "cm91bmQgNzM2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 736: a worker pulls the next task from the queue",
        "cm91bmQgNzM2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 736: signals travel through the network layer",
        "cm91bmQgNzM2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 736: the gateway routes each request by policy",
        "cm91bmQgNzM2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 736: memory grows until the buffer is full",
        "cm91bmQgNzM2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 736: the cluster mirrors every packet twice",
        "cm91bmQgNzM2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 736: ranking uses tokens learned from the corpus",
        "cm91bmQgNzM2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 736: a long session ends when the candle dies",
        "cm91bmQgNzM2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 736: encode the prompt then map the result",
        "cm91bmQgNzM2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 736: the kernel wakes the worker at dawn",
        "cm91bmQgNzM2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 736: service latency drops after the patch",
        "cm91bmQgNzM2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 736: the library caches every vector it sees",
        "cm91bmQgNzM2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 736: agents argue then the debate resolves",
        "cm91bmQgNzM2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 736: the filter keeps only strong matches",
        "cm91bmQgNzM2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 736: the model answers with a short reply",
        "cm91bmQgNzM2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 736: the recorder stores the reasoning trace",
        "cm91bmQgNzM2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 736: the angel watches the processor run",
        "cm91bmQgNzM2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 736: angle of the vector decides the match",
        "cm91bmQgNzM2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 736: the candle burns twice as long at night",
        "cm91bmQgNzM2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 736: a mirror of the universe in one line",
        "cm91bmQgNzM2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 736: the queue drains before the storm", "cm91bmQgNzM2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
