"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten166kitten166", "a2l0dGVuMTY2a2l0dGVuMTY2"),
    ("kitten166sitting166", "a2l0dGVuMTY2c2l0dGluZzE2Ng"),
    ("kitten166agent166", "a2l0dGVuMTY2YWdlbnQxNjY"),
    ("kitten166angle166", "a2l0dGVuMTY2YW5nbGUxNjY"),
    ("sitting166angle166", "c2l0dGluZzE2NmFuZ2xlMTY2"),
    ("sitting166universe166", "c2l0dGluZzE2NnVuaXZlcnNlMTY2"),
    ("sitting166memory166", "c2l0dGluZzE2Nm1lbW9yeTE2Ng"),
    ("sitting166stream166", "c2l0dGluZzE2NnN0cmVhbTE2Ng"),
    ("agent166stream166", "YWdlbnQxNjZzdHJlYW0xNjY"),
    ("agent166context166", "YWdlbnQxNjZjb250ZXh0MTY2"),
    ("agent166knowledge166", "YWdlbnQxNjZrbm93bGVkZ2UxNjY"),
    ("agent166vector166", "YWdlbnQxNjZ2ZWN0b3IxNjY"),
    ("angle166vector166", "YW5nbGUxNjZ2ZWN0b3IxNjY"),
    ("angle166processor166", "YW5nbGUxNjZwcm9jZXNzb3IxNjY"),
    ("angle166reasoning166", "YW5nbGUxNjZyZWFzb25pbmcxNjY"),
    ("angle166machine166", "YW5nbGUxNjZtYWNoaW5lMTY2"),
    ("universe166machine166", "dW5pdmVyc2UxNjZtYWNoaW5lMTY2"),
    ("universe166learning166", "dW5pdmVyc2UxNjZsZWFybmluZzE2Ng"),
    ("universe166model166", "dW5pdmVyc2UxNjZtb2RlbDE2Ng"),
    ("universe166token166", "dW5pdmVyc2UxNjZ0b2tlbjE2Ng"),
    ("memory166token166", "bWVtb3J5MTY2dG9rZW4xNjY"),
    ("memory166prompt166", "bWVtb3J5MTY2cHJvbXB0MTY2"),
    ("memory166session166", "bWVtb3J5MTY2c2Vzc2lvbjE2Ng"),
    ("memory166library166", "bWVtb3J5MTY2bGlicmFyeTE2Ng"),
    ("stream166library166", "c3RyZWFtMTY2bGlicmFyeTE2Ng"),
    ("stream166service166", "c3RyZWFtMTY2c2VydmljZTE2Ng"),
    ("stream166gateway166", "c3RyZWFtMTY2Z2F0ZXdheTE2Ng"),
    ("stream166storage166", "c3RyZWFtMTY2c3RvcmFnZTE2Ng"),
    ("context166storage166", "Y29udGV4dDE2NnN0b3JhZ2UxNjY"),
    ("context166network166", "Y29udGV4dDE2Nm5ldHdvcmsxNjY"),
    ("context166latency166", "Y29udGV4dDE2NmxhdGVuY3kxNjY"),
    ("context166buffer166", "Y29udGV4dDE2NmJ1ZmZlcjE2Ng"),
    ("knowledge166buffer166", "a25vd2xlZGdlMTY2YnVmZmVyMTY2"),
    ("knowledge166queue166", "a25vd2xlZGdlMTY2cXVldWUxNjY"),
    ("knowledge166worker166", "a25vd2xlZGdlMTY2d29ya2VyMTY2"),
    ("knowledge166kernel166", "a25vd2xlZGdlMTY2a2VybmVsMTY2"),
    ("vector166kernel166", "dmVjdG9yMTY2a2VybmVsMTY2"),
    ("vector166signal166", "dmVjdG9yMTY2c2lnbmFsMTY2"),
    ("vector166packet166", "dmVjdG9yMTY2cGFja2V0MTY2"),
    ("vector166router166", "dmVjdG9yMTY2cm91dGVyMTY2"),
    ("processor166router166", "cHJvY2Vzc29yMTY2cm91dGVyMTY2"),
    ("processor166cluster166", "cHJvY2Vzc29yMTY2Y2x1c3RlcjE2Ng"),
    ("processor166mirror166", "cHJvY2Vzc29yMTY2bWlycm9yMTY2"),
    ("processor166filter166", "cHJvY2Vzc29yMTY2ZmlsdGVyMTY2"),
    ("reasoning166filter166", "cmVhc29uaW5nMTY2ZmlsdGVyMTY2"),
    ("reasoning166ranking166", "cmVhc29uaW5nMTY2cmFua2luZzE2Ng"),
    ("reasoning166encoding166", "cmVhc29uaW5nMTY2ZW5jb2RpbmcxNjY"),
    ("reasoning166mapping166", "cmVhc29uaW5nMTY2bWFwcGluZzE2Ng"),
    ("machine166mapping166", "bWFjaGluZTE2Nm1hcHBpbmcxNjY"),
    ("machine166record166", "bWFjaGluZTE2NnJlY29yZDE2Ng"),
    ("machine166candle166", "bWFjaGluZTE2NmNhbmRsZTE2Ng"),
    ("machine166thread166", "bWFjaGluZTE2NnRocmVhZDE2Ng"),
    ("learning166thread166", "bGVhcm5pbmcxNjZ0aHJlYWQxNjY"),
    ("learning166kitten166", "bGVhcm5pbmcxNjZraXR0ZW4xNjY"),
    ("learning166sitting166", "bGVhcm5pbmcxNjZzaXR0aW5nMTY2"),
    ("learning166agent166", "bGVhcm5pbmcxNjZhZ2VudDE2Ng"),
    ("model166agent166", "bW9kZWwxNjZhZ2VudDE2Ng"),
    ("model166angle166", "bW9kZWwxNjZhbmdsZTE2Ng"),
    ("model166universe166", "bW9kZWwxNjZ1bml2ZXJzZTE2Ng"),
    ("model166memory166", "bW9kZWwxNjZtZW1vcnkxNjY"),
    ("token166memory166", "dG9rZW4xNjZtZW1vcnkxNjY"),
    ("token166stream166", "dG9rZW4xNjZzdHJlYW0xNjY"),
    ("token166context166", "dG9rZW4xNjZjb250ZXh0MTY2"),
    ("token166knowledge166", "dG9rZW4xNjZrbm93bGVkZ2UxNjY"),
    ("prompt166knowledge166", "cHJvbXB0MTY2a25vd2xlZGdlMTY2"),
    ("prompt166vector166", "cHJvbXB0MTY2dmVjdG9yMTY2"),
    ("prompt166processor166", "cHJvbXB0MTY2cHJvY2Vzc29yMTY2"),
    ("prompt166reasoning166", "cHJvbXB0MTY2cmVhc29uaW5nMTY2"),
    ("session166reasoning166", "c2Vzc2lvbjE2NnJlYXNvbmluZzE2Ng"),
    ("session166machine166", "c2Vzc2lvbjE2Nm1hY2hpbmUxNjY"),
    ("session166learning166", "c2Vzc2lvbjE2NmxlYXJuaW5nMTY2"),
    ("session166model166", "c2Vzc2lvbjE2Nm1vZGVsMTY2"),
    ("library166model166", "bGlicmFyeTE2Nm1vZGVsMTY2"),
    ("library166token166", "bGlicmFyeTE2NnRva2VuMTY2"),
    ("library166prompt166", "bGlicmFyeTE2NnByb21wdDE2Ng"),
    ("library166session166", "bGlicmFyeTE2NnNlc3Npb24xNjY"),
    ("service166session166", "c2VydmljZTE2NnNlc3Npb24xNjY"),
    ("service166library166", "c2VydmljZTE2NmxpYnJhcnkxNjY"),
    ("service166service166", "c2VydmljZTE2NnNlcnZpY2UxNjY"),
    ("service166gateway166", "c2VydmljZTE2NmdhdGV3YXkxNjY"),
    ("gateway166gateway166", "Z2F0ZXdheTE2NmdhdGV3YXkxNjY"),
    ("gateway166storage166", "Z2F0ZXdheTE2NnN0b3JhZ2UxNjY"),
    ("gateway166network166", "Z2F0ZXdheTE2Nm5ldHdvcmsxNjY"),
    ("gateway166latency166", "Z2F0ZXdheTE2NmxhdGVuY3kxNjY"),
    ("storage166latency166", "c3RvcmFnZTE2NmxhdGVuY3kxNjY"),
    ("storage166buffer166", "c3RvcmFnZTE2NmJ1ZmZlcjE2Ng"),
    ("storage166queue166", "c3RvcmFnZTE2NnF1ZXVlMTY2"),
    ("storage166worker166", "c3RvcmFnZTE2NndvcmtlcjE2Ng"),
    ("network166worker166", "bmV0d29yazE2NndvcmtlcjE2Ng"),
    ("network166kernel166", "bmV0d29yazE2Nmtlcm5lbDE2Ng"),
    ("network166signal166", "bmV0d29yazE2NnNpZ25hbDE2Ng"),
    ("network166packet166", "bmV0d29yazE2NnBhY2tldDE2Ng"),
    ("latency166packet166", "bGF0ZW5jeTE2NnBhY2tldDE2Ng"),
    ("latency166router166", "bGF0ZW5jeTE2NnJvdXRlcjE2Ng"),
    ("latency166cluster166", "bGF0ZW5jeTE2NmNsdXN0ZXIxNjY"),
    ("latency166mirror166", "bGF0ZW5jeTE2Nm1pcnJvcjE2Ng"),
    ("buffer166mirror166", "YnVmZmVyMTY2bWlycm9yMTY2"),
    ("buffer166filter166", "YnVmZmVyMTY2ZmlsdGVyMTY2"),
    ("buffer166ranking166", "YnVmZmVyMTY2cmFua2luZzE2Ng"),
    ("buffer166encoding166", "YnVmZmVyMTY2ZW5jb2RpbmcxNjY"),
    ("queue166encoding166", "cXVldWUxNjZlbmNvZGluZzE2Ng"),
    ("queue166mapping166", "cXVldWUxNjZtYXBwaW5nMTY2"),
    ("queue166record166", "cXVldWUxNjZyZWNvcmQxNjY"),
    ("queue166candle166", "cXVldWUxNjZjYW5kbGUxNjY"),
    ("worker166candle166", "d29ya2VyMTY2Y2FuZGxlMTY2"),
    ("worker166thread166", "d29ya2VyMTY2dGhyZWFkMTY2"),
    ("worker166kitten166", "d29ya2VyMTY2a2l0dGVuMTY2"),
    ("worker166sitting166", "d29ya2VyMTY2c2l0dGluZzE2Ng"),
    ("kernel166sitting166", "a2VybmVsMTY2c2l0dGluZzE2Ng"),
    ("kernel166agent166", "a2VybmVsMTY2YWdlbnQxNjY"),
    ("kernel166angle166", "a2VybmVsMTY2YW5nbGUxNjY"),
    ("kernel166universe166", "a2VybmVsMTY2dW5pdmVyc2UxNjY"),
    ("signal166universe166", "c2lnbmFsMTY2dW5pdmVyc2UxNjY"),
    ("signal166memory166", "c2lnbmFsMTY2bWVtb3J5MTY2"),
    ("signal166stream166", "c2lnbmFsMTY2c3RyZWFtMTY2"),
    ("signal166context166", "c2lnbmFsMTY2Y29udGV4dDE2Ng"),
    ("packet166context166", "cGFja2V0MTY2Y29udGV4dDE2Ng"),
    ("packet166knowledge166", "cGFja2V0MTY2a25vd2xlZGdlMTY2"),
    ("packet166vector166", "cGFja2V0MTY2dmVjdG9yMTY2"),
    ("packet166processor166", "cGFja2V0MTY2cHJvY2Vzc29yMTY2"),
    ("router166processor166", "cm91dGVyMTY2cHJvY2Vzc29yMTY2"),
    ("router166reasoning166", "cm91dGVyMTY2cmVhc29uaW5nMTY2"),
    ("router166machine166", "cm91dGVyMTY2bWFjaGluZTE2Ng"),
    ("router166learning166", "cm91dGVyMTY2bGVhcm5pbmcxNjY"),
    ("cluster166learning166", "Y2x1c3RlcjE2NmxlYXJuaW5nMTY2"),
    ("cluster166model166", "Y2x1c3RlcjE2Nm1vZGVsMTY2"),
    ("cluster166token166", "Y2x1c3RlcjE2NnRva2VuMTY2"),
    ("cluster166prompt166", "Y2x1c3RlcjE2NnByb21wdDE2Ng"),
    ("mirror166prompt166", "bWlycm9yMTY2cHJvbXB0MTY2"),
    ("mirror166session166", "bWlycm9yMTY2c2Vzc2lvbjE2Ng"),
    ("mirror166library166", "bWlycm9yMTY2bGlicmFyeTE2Ng"),
    ("mirror166service166", "bWlycm9yMTY2c2VydmljZTE2Ng"),
    ("filter166service166", "ZmlsdGVyMTY2c2VydmljZTE2Ng"),
    ("filter166gateway166", "ZmlsdGVyMTY2Z2F0ZXdheTE2Ng"),
    ("filter166storage166", "ZmlsdGVyMTY2c3RvcmFnZTE2Ng"),
    ("filter166network166", "ZmlsdGVyMTY2bmV0d29yazE2Ng"),
    ("ranking166network166", "cmFua2luZzE2Nm5ldHdvcmsxNjY"),
    ("ranking166latency166", "cmFua2luZzE2NmxhdGVuY3kxNjY"),
    ("ranking166buffer166", "cmFua2luZzE2NmJ1ZmZlcjE2Ng"),
    ("ranking166queue166", "cmFua2luZzE2NnF1ZXVlMTY2"),
    ("encoding166queue166", "ZW5jb2RpbmcxNjZxdWV1ZTE2Ng"),
    ("encoding166worker166", "ZW5jb2RpbmcxNjZ3b3JrZXIxNjY"),
    ("encoding166kernel166", "ZW5jb2RpbmcxNjZrZXJuZWwxNjY"),
    ("encoding166signal166", "ZW5jb2RpbmcxNjZzaWduYWwxNjY"),
    ("mapping166signal166", "bWFwcGluZzE2NnNpZ25hbDE2Ng"),
    ("mapping166packet166", "bWFwcGluZzE2NnBhY2tldDE2Ng"),
    ("mapping166router166", "bWFwcGluZzE2NnJvdXRlcjE2Ng"),
    ("mapping166cluster166", "bWFwcGluZzE2NmNsdXN0ZXIxNjY"),
    ("record166cluster166", "cmVjb3JkMTY2Y2x1c3RlcjE2Ng"),
    ("record166mirror166", "cmVjb3JkMTY2bWlycm9yMTY2"),
    ("record166filter166", "cmVjb3JkMTY2ZmlsdGVyMTY2"),
    ("record166ranking166", "cmVjb3JkMTY2cmFua2luZzE2Ng"),
    ("candle166ranking166", "Y2FuZGxlMTY2cmFua2luZzE2Ng"),
    ("candle166encoding166", "Y2FuZGxlMTY2ZW5jb2RpbmcxNjY"),
    ("candle166mapping166", "Y2FuZGxlMTY2bWFwcGluZzE2Ng"),
    ("candle166record166", "Y2FuZGxlMTY2cmVjb3JkMTY2"),
    ("thread166record166", "dGhyZWFkMTY2cmVjb3JkMTY2"),
    ("thread166candle166", "dGhyZWFkMTY2Y2FuZGxlMTY2"),
    ("thread166thread166", "dGhyZWFkMTY2dGhyZWFkMTY2"),
    ("thread166kitten166", "dGhyZWFkMTY2a2l0dGVuMTY2"),
    (
        "round 166: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTY2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 166: agentuniverse is a framework for multi agents",
        "cm91bmQgMTY2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 166: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTY2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 166: the processor reads the record then stops",
        "cm91bmQgMTY2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 166: a worker pulls the next task from the queue",
        "cm91bmQgMTY2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 166: signals travel through the network layer",
        "cm91bmQgMTY2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 166: the gateway routes each request by policy",
        "cm91bmQgMTY2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 166: memory grows until the buffer is full",
        "cm91bmQgMTY2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 166: the cluster mirrors every packet twice",
        "cm91bmQgMTY2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 166: ranking uses tokens learned from the corpus",
        "cm91bmQgMTY2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 166: a long session ends when the candle dies",
        "cm91bmQgMTY2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 166: encode the prompt then map the result",
        "cm91bmQgMTY2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 166: the kernel wakes the worker at dawn",
        "cm91bmQgMTY2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 166: service latency drops after the patch",
        "cm91bmQgMTY2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 166: the library caches every vector it sees",
        "cm91bmQgMTY2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 166: agents argue then the debate resolves",
        "cm91bmQgMTY2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 166: the filter keeps only strong matches",
        "cm91bmQgMTY2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 166: the model answers with a short reply",
        "cm91bmQgMTY2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 166: the recorder stores the reasoning trace",
        "cm91bmQgMTY2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 166: the angel watches the processor run",
        "cm91bmQgMTY2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 166: angle of the vector decides the match",
        "cm91bmQgMTY2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 166: the candle burns twice as long at night",
        "cm91bmQgMTY2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 166: a mirror of the universe in one line",
        "cm91bmQgMTY2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 166: the queue drains before the storm", "cm91bmQgMTY2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
