"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten156kitten156", "a2l0dGVuMTU2a2l0dGVuMTU2"),
    ("kitten156sitting156", "a2l0dGVuMTU2c2l0dGluZzE1Ng"),
    ("kitten156agent156", "a2l0dGVuMTU2YWdlbnQxNTY"),
    ("kitten156angle156", "a2l0dGVuMTU2YW5nbGUxNTY"),
    ("sitting156angle156", "c2l0dGluZzE1NmFuZ2xlMTU2"),
    ("sitting156universe156", "c2l0dGluZzE1NnVuaXZlcnNlMTU2"),
    ("sitting156memory156", "c2l0dGluZzE1Nm1lbW9yeTE1Ng"),
    ("sitting156stream156", "c2l0dGluZzE1NnN0cmVhbTE1Ng"),
    ("agent156stream156", "YWdlbnQxNTZzdHJlYW0xNTY"),
    ("agent156context156", "YWdlbnQxNTZjb250ZXh0MTU2"),
    ("agent156knowledge156", "YWdlbnQxNTZrbm93bGVkZ2UxNTY"),
    ("agent156vector156", "YWdlbnQxNTZ2ZWN0b3IxNTY"),
    ("angle156vector156", "YW5nbGUxNTZ2ZWN0b3IxNTY"),
    ("angle156processor156", "YW5nbGUxNTZwcm9jZXNzb3IxNTY"),
    ("angle156reasoning156", "YW5nbGUxNTZyZWFzb25pbmcxNTY"),
    ("angle156machine156", "YW5nbGUxNTZtYWNoaW5lMTU2"),
    ("universe156machine156", "dW5pdmVyc2UxNTZtYWNoaW5lMTU2"),
    ("universe156learning156", "dW5pdmVyc2UxNTZsZWFybmluZzE1Ng"),
    ("universe156model156", "dW5pdmVyc2UxNTZtb2RlbDE1Ng"),
    ("universe156token156", "dW5pdmVyc2UxNTZ0b2tlbjE1Ng"),
    ("memory156token156", "bWVtb3J5MTU2dG9rZW4xNTY"),
    ("memory156prompt156", "bWVtb3J5MTU2cHJvbXB0MTU2"),
    ("memory156session156", "bWVtb3J5MTU2c2Vzc2lvbjE1Ng"),
    ("memory156library156", "bWVtb3J5MTU2bGlicmFyeTE1Ng"),
    ("stream156library156", "c3RyZWFtMTU2bGlicmFyeTE1Ng"),
    ("stream156service156", "c3RyZWFtMTU2c2VydmljZTE1Ng"),
    ("stream156gateway156", "c3RyZWFtMTU2Z2F0ZXdheTE1Ng"),
    ("stream156storage156", "c3RyZWFtMTU2c3RvcmFnZTE1Ng"),
    ("context156storage156", "Y29udGV4dDE1NnN0b3JhZ2UxNTY"),
    ("context156network156", "Y29udGV4dDE1Nm5ldHdvcmsxNTY"),
    ("context156latency156", "Y29udGV4dDE1NmxhdGVuY3kxNTY"),
    ("context156buffer156", "Y29udGV4dDE1NmJ1ZmZlcjE1Ng"),
    ("knowledge156buffer156", "a25vd2xlZGdlMTU2YnVmZmVyMTU2"),
    ("knowledge156queue156", "a25vd2xlZGdlMTU2cXVldWUxNTY"),
    ("knowledge156worker156", "a25vd2xlZGdlMTU2d29ya2VyMTU2"),
    ("knowledge156kernel156", "a25vd2xlZGdlMTU2a2VybmVsMTU2"),
    ("vector156kernel156", "dmVjdG9yMTU2a2VybmVsMTU2"),
    ("vector156signal156", "dmVjdG9yMTU2c2lnbmFsMTU2"),
    ("vector156packet156", "dmVjdG9yMTU2cGFja2V0MTU2"),
    ("vector156router156", "dmVjdG9yMTU2cm91dGVyMTU2"),
    ("processor156router156", "cHJvY2Vzc29yMTU2cm91dGVyMTU2"),
    ("processor156cluster156", "cHJvY2Vzc29yMTU2Y2x1c3RlcjE1Ng"),
    ("processor156mirror156", "cHJvY2Vzc29yMTU2bWlycm9yMTU2"),
    ("processor156filter156", "cHJvY2Vzc29yMTU2ZmlsdGVyMTU2"),
    ("reasoning156filter156", "cmVhc29uaW5nMTU2ZmlsdGVyMTU2"),
    ("reasoning156ranking156", "cmVhc29uaW5nMTU2cmFua2luZzE1Ng"),
    ("reasoning156encoding156", "cmVhc29uaW5nMTU2ZW5jb2RpbmcxNTY"),
    ("reasoning156mapping156", "cmVhc29uaW5nMTU2bWFwcGluZzE1Ng"),
    ("machine156mapping156", "bWFjaGluZTE1Nm1hcHBpbmcxNTY"),
    ("machine156record156", "bWFjaGluZTE1NnJlY29yZDE1Ng"),
    ("machine156candle156", "bWFjaGluZTE1NmNhbmRsZTE1Ng"),
    ("machine156thread156", "bWFjaGluZTE1NnRocmVhZDE1Ng"),
    ("learning156thread156", "bGVhcm5pbmcxNTZ0aHJlYWQxNTY"),
    ("learning156kitten156", "bGVhcm5pbmcxNTZraXR0ZW4xNTY"),
    ("learning156sitting156", "bGVhcm5pbmcxNTZzaXR0aW5nMTU2"),
    ("learning156agent156", "bGVhcm5pbmcxNTZhZ2VudDE1Ng"),
    ("model156agent156", "bW9kZWwxNTZhZ2VudDE1Ng"),
    ("model156angle156", "bW9kZWwxNTZhbmdsZTE1Ng"),
    ("model156universe156", "bW9kZWwxNTZ1bml2ZXJzZTE1Ng"),
    ("model156memory156", "bW9kZWwxNTZtZW1vcnkxNTY"),
    ("token156memory156", "dG9rZW4xNTZtZW1vcnkxNTY"),
    ("token156stream156", "dG9rZW4xNTZzdHJlYW0xNTY"),
    ("token156context156", "dG9rZW4xNTZjb250ZXh0MTU2"),
    ("token156knowledge156", "dG9rZW4xNTZrbm93bGVkZ2UxNTY"),
    ("prompt156knowledge156", "cHJvbXB0MTU2a25vd2xlZGdlMTU2"),
    ("prompt156vector156", "cHJvbXB0MTU2dmVjdG9yMTU2"),
    ("prompt156processor156", "cHJvbXB0MTU2cHJvY2Vzc29yMTU2"),
    ("prompt156reasoning156", "cHJvbXB0MTU2cmVhc29uaW5nMTU2"),
    ("session156reasoning156", "c2Vzc2lvbjE1NnJlYXNvbmluZzE1Ng"),
    ("session156machine156", "c2Vzc2lvbjE1Nm1hY2hpbmUxNTY"),
    ("session156learning156", "c2Vzc2lvbjE1NmxlYXJuaW5nMTU2"),
    ("session156model156", "c2Vzc2lvbjE1Nm1vZGVsMTU2"),
    ("library156model156", "bGlicmFyeTE1Nm1vZGVsMTU2"),
    ("library156token156", "bGlicmFyeTE1NnRva2VuMTU2"),
    ("library156prompt156", "bGlicmFyeTE1NnByb21wdDE1Ng"),
    ("library156session156", "bGlicmFyeTE1NnNlc3Npb24xNTY"),
    ("service156session156", "c2VydmljZTE1NnNlc3Npb24xNTY"),
    ("service156library156", "c2VydmljZTE1NmxpYnJhcnkxNTY"),
    ("service156service156", "c2VydmljZTE1NnNlcnZpY2UxNTY"),
    ("service156gateway156", "c2VydmljZTE1NmdhdGV3YXkxNTY"),
    ("gateway156gateway156", "Z2F0ZXdheTE1NmdhdGV3YXkxNTY"),
    ("gateway156storage156", "Z2F0ZXdheTE1NnN0b3JhZ2UxNTY"),
    ("gateway156network156", "Z2F0ZXdheTE1Nm5ldHdvcmsxNTY"),
    ("gateway156latency156", "Z2F0ZXdheTE1NmxhdGVuY3kxNTY"),
    ("storage156latency156", "c3RvcmFnZTE1NmxhdGVuY3kxNTY"),
    ("storage156buffer156", "c3RvcmFnZTE1NmJ1ZmZlcjE1Ng"),
    ("storage156queue156", "c3RvcmFnZTE1NnF1ZXVlMTU2"),
    ("storage156worker156", "c3RvcmFnZTE1NndvcmtlcjE1Ng"),
    ("network156worker156", "bmV0d29yazE1NndvcmtlcjE1Ng"),
    ("network156kernel156", "bmV0d29yazE1Nmtlcm5lbDE1Ng"),
    ("network156signal156", "bmV0d29yazE1NnNpZ25hbDE1Ng"),
    ("network156packet156", "bmV0d29yazE1NnBhY2tldDE1Ng"),
    ("latency156packet156", "bGF0ZW5jeTE1NnBhY2tldDE1Ng"),
    ("latency156router156", "bGF0ZW5jeTE1NnJvdXRlcjE1Ng"),
    ("latency156cluster156", "bGF0ZW5jeTE1NmNsdXN0ZXIxNTY"),
    ("latency156mirror156", "bGF0ZW5jeTE1Nm1pcnJvcjE1Ng"),
    ("buffer156mirror156", "YnVmZmVyMTU2bWlycm9yMTU2"),
    ("buffer156filter156", "YnVmZmVyMTU2ZmlsdGVyMTU2"),
    ("buffer156ranking156", "YnVmZmVyMTU2cmFua2luZzE1Ng"),
    ("buffer156encoding156", "YnVmZmVyMTU2ZW5jb2RpbmcxNTY"),
    ("queue156encoding156", "cXVldWUxNTZlbmNvZGluZzE1Ng"),
    ("queue156mapping156", "cXVldWUxNTZtYXBwaW5nMTU2"),
    ("queue156record156", "cXVldWUxNTZyZWNvcmQxNTY"),
    ("queue156candle156", "cXVldWUxNTZjYW5kbGUxNTY"),
    ("worker156candle156", "d29ya2VyMTU2Y2FuZGxlMTU2"),
    ("worker156thread156", "d29ya2VyMTU2dGhyZWFkMTU2"),
    ("worker156kitten156", "d29ya2VyMTU2a2l0dGVuMTU2"),
    ("worker156sitting156", "d29ya2VyMTU2c2l0dGluZzE1Ng"),
    ("kernel156sitting156", "a2VybmVsMTU2c2l0dGluZzE1Ng"),
    ("kernel156agent156", "a2VybmVsMTU2YWdlbnQxNTY"),
    ("kernel156angle156", "a2VybmVsMTU2YW5nbGUxNTY"),
    ("kernel156universe156", "a2VybmVsMTU2dW5pdmVyc2UxNTY"),
    ("signal156universe156", "c2lnbmFsMTU2dW5pdmVyc2UxNTY"),
    ("signal156memory156", "c2lnbmFsMTU2bWVtb3J5MTU2"),
    ("signal156stream156", "c2lnbmFsMTU2c3RyZWFtMTU2"),
    ("signal156context156", "c2lnbmFsMTU2Y29udGV4dDE1Ng"),
    ("packet156context156", "cGFja2V0MTU2Y29udGV4dDE1Ng"),
    ("packet156knowledge156", "cGFja2V0MTU2a25vd2xlZGdlMTU2"),
    ("packet156vector156", "cGFja2V0MTU2dmVjdG9yMTU2"),
    ("packet156processor156", "cGFja2V0MTU2cHJvY2Vzc29yMTU2"),
    ("router156processor156", "cm91dGVyMTU2cHJvY2Vzc29yMTU2"),
    ("router156reasoning156", "cm91dGVyMTU2cmVhc29uaW5nMTU2"),
    ("router156machine156", "cm91dGVyMTU2bWFjaGluZTE1Ng"),
    ("router156learning156", "cm91dGVyMTU2bGVhcm5pbmcxNTY"),
    ("cluster156learning156", "Y2x1c3RlcjE1NmxlYXJuaW5nMTU2"),
    ("cluster156model156", "Y2x1c3RlcjE1Nm1vZGVsMTU2"),
    ("cluster156token156", "Y2x1c3RlcjE1NnRva2VuMTU2"),
    ("cluster156prompt156", "Y2x1c3RlcjE1NnByb21wdDE1Ng"),
    ("mirror156prompt156", "bWlycm9yMTU2cHJvbXB0MTU2"),
    ("mirror156session156", "bWlycm9yMTU2c2Vzc2lvbjE1Ng"),
    ("mirror156library156", "bWlycm9yMTU2bGlicmFyeTE1Ng"),
    ("mirror156service156", "bWlycm9yMTU2c2VydmljZTE1Ng"),
    ("filter156service156", "ZmlsdGVyMTU2c2VydmljZTE1Ng"),
    ("filter156gateway156", "ZmlsdGVyMTU2Z2F0ZXdheTE1Ng"),
    ("filter156storage156", "ZmlsdGVyMTU2c3RvcmFnZTE1Ng"),
    ("filter156network156", "ZmlsdGVyMTU2bmV0d29yazE1Ng"),
    ("ranking156network156", "cmFua2luZzE1Nm5ldHdvcmsxNTY"),
    ("ranking156latency156", "cmFua2luZzE1NmxhdGVuY3kxNTY"),
    ("ranking156buffer156", "cmFua2luZzE1NmJ1ZmZlcjE1Ng"),
    ("ranking156queue156", "cmFua2luZzE1NnF1ZXVlMTU2"),
    ("encoding156queue156", "ZW5jb2RpbmcxNTZxdWV1ZTE1Ng"),
    ("encoding156worker156", "ZW5jb2RpbmcxNTZ3b3JrZXIxNTY"),
    ("encoding156kernel156", "ZW5jb2RpbmcxNTZrZXJuZWwxNTY"),
    ("encoding156signal156", "ZW5jb2RpbmcxNTZzaWduYWwxNTY"),
    ("mapping156signal156", "bWFwcGluZzE1NnNpZ25hbDE1Ng"),
    ("mapping156packet156", "bWFwcGluZzE1NnBhY2tldDE1Ng"),
    ("mapping156router156", "bWFwcGluZzE1NnJvdXRlcjE1Ng"),
    ("mapping156cluster156", "bWFwcGluZzE1NmNsdXN0ZXIxNTY"),
    ("record156cluster156", "cmVjb3JkMTU2Y2x1c3RlcjE1Ng"),
    ("record156mirror156", "cmVjb3JkMTU2bWlycm9yMTU2"),
    ("record156filter156", "cmVjb3JkMTU2ZmlsdGVyMTU2"),
    ("record156ranking156", "cmVjb3JkMTU2cmFua2luZzE1Ng"),
    ("candle156ranking156", "Y2FuZGxlMTU2cmFua2luZzE1Ng"),
    ("candle156encoding156", "Y2FuZGxlMTU2ZW5jb2RpbmcxNTY"),
    ("candle156mapping156", "Y2FuZGxlMTU2bWFwcGluZzE1Ng"),
    ("candle156record156", "Y2FuZGxlMTU2cmVjb3JkMTU2"),
    ("thread156record156", "dGhyZWFkMTU2cmVjb3JkMTU2"),
    ("thread156candle156", "dGhyZWFkMTU2Y2FuZGxlMTU2"),
    ("thread156thread156", "dGhyZWFkMTU2dGhyZWFkMTU2"),
    ("thread156kitten156", "dGhyZWFkMTU2a2l0dGVuMTU2"),
    (
        "round 156: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTU2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 156: agentuniverse is a framework for multi agents",
        "cm91bmQgMTU2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 156: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTU2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 156: the processor reads the record then stops",
        "cm91bmQgMTU2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 156: a worker pulls the next task from the queue",
        "cm91bmQgMTU2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 156: signals travel through the network layer",
        "cm91bmQgMTU2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 156: the gateway routes each request by policy",
        "cm91bmQgMTU2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 156: memory grows until the buffer is full",
        "cm91bmQgMTU2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 156: the cluster mirrors every packet twice",
        "cm91bmQgMTU2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 156: ranking uses tokens learned from the corpus",
        "cm91bmQgMTU2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 156: a long session ends when the candle dies",
        "cm91bmQgMTU2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 156: encode the prompt then map the result",
        "cm91bmQgMTU2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 156: the kernel wakes the worker at dawn",
        "cm91bmQgMTU2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 156: service latency drops after the patch",
        "cm91bmQgMTU2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 156: the library caches every vector it sees",
        "cm91bmQgMTU2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 156: agents argue then the debate resolves",
        "cm91bmQgMTU2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 156: the filter keeps only strong matches",
        "cm91bmQgMTU2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 156: the model answers with a short reply",
        "cm91bmQgMTU2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 156: the recorder stores the reasoning trace",
        "cm91bmQgMTU2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 156: the angel watches the processor run",
        "cm91bmQgMTU2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 156: angle of the vector decides the match",
        "cm91bmQgMTU2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 156: the candle burns twice as long at night",
        "cm91bmQgMTU2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 156: a mirror of the universe in one line",
        "cm91bmQgMTU2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 156: the queue drains before the storm", "cm91bmQgMTU2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
