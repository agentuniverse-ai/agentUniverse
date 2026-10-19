"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten176kitten176", "a2l0dGVuMTc2a2l0dGVuMTc2"),
    ("kitten176sitting176", "a2l0dGVuMTc2c2l0dGluZzE3Ng"),
    ("kitten176agent176", "a2l0dGVuMTc2YWdlbnQxNzY"),
    ("kitten176angle176", "a2l0dGVuMTc2YW5nbGUxNzY"),
    ("sitting176angle176", "c2l0dGluZzE3NmFuZ2xlMTc2"),
    ("sitting176universe176", "c2l0dGluZzE3NnVuaXZlcnNlMTc2"),
    ("sitting176memory176", "c2l0dGluZzE3Nm1lbW9yeTE3Ng"),
    ("sitting176stream176", "c2l0dGluZzE3NnN0cmVhbTE3Ng"),
    ("agent176stream176", "YWdlbnQxNzZzdHJlYW0xNzY"),
    ("agent176context176", "YWdlbnQxNzZjb250ZXh0MTc2"),
    ("agent176knowledge176", "YWdlbnQxNzZrbm93bGVkZ2UxNzY"),
    ("agent176vector176", "YWdlbnQxNzZ2ZWN0b3IxNzY"),
    ("angle176vector176", "YW5nbGUxNzZ2ZWN0b3IxNzY"),
    ("angle176processor176", "YW5nbGUxNzZwcm9jZXNzb3IxNzY"),
    ("angle176reasoning176", "YW5nbGUxNzZyZWFzb25pbmcxNzY"),
    ("angle176machine176", "YW5nbGUxNzZtYWNoaW5lMTc2"),
    ("universe176machine176", "dW5pdmVyc2UxNzZtYWNoaW5lMTc2"),
    ("universe176learning176", "dW5pdmVyc2UxNzZsZWFybmluZzE3Ng"),
    ("universe176model176", "dW5pdmVyc2UxNzZtb2RlbDE3Ng"),
    ("universe176token176", "dW5pdmVyc2UxNzZ0b2tlbjE3Ng"),
    ("memory176token176", "bWVtb3J5MTc2dG9rZW4xNzY"),
    ("memory176prompt176", "bWVtb3J5MTc2cHJvbXB0MTc2"),
    ("memory176session176", "bWVtb3J5MTc2c2Vzc2lvbjE3Ng"),
    ("memory176library176", "bWVtb3J5MTc2bGlicmFyeTE3Ng"),
    ("stream176library176", "c3RyZWFtMTc2bGlicmFyeTE3Ng"),
    ("stream176service176", "c3RyZWFtMTc2c2VydmljZTE3Ng"),
    ("stream176gateway176", "c3RyZWFtMTc2Z2F0ZXdheTE3Ng"),
    ("stream176storage176", "c3RyZWFtMTc2c3RvcmFnZTE3Ng"),
    ("context176storage176", "Y29udGV4dDE3NnN0b3JhZ2UxNzY"),
    ("context176network176", "Y29udGV4dDE3Nm5ldHdvcmsxNzY"),
    ("context176latency176", "Y29udGV4dDE3NmxhdGVuY3kxNzY"),
    ("context176buffer176", "Y29udGV4dDE3NmJ1ZmZlcjE3Ng"),
    ("knowledge176buffer176", "a25vd2xlZGdlMTc2YnVmZmVyMTc2"),
    ("knowledge176queue176", "a25vd2xlZGdlMTc2cXVldWUxNzY"),
    ("knowledge176worker176", "a25vd2xlZGdlMTc2d29ya2VyMTc2"),
    ("knowledge176kernel176", "a25vd2xlZGdlMTc2a2VybmVsMTc2"),
    ("vector176kernel176", "dmVjdG9yMTc2a2VybmVsMTc2"),
    ("vector176signal176", "dmVjdG9yMTc2c2lnbmFsMTc2"),
    ("vector176packet176", "dmVjdG9yMTc2cGFja2V0MTc2"),
    ("vector176router176", "dmVjdG9yMTc2cm91dGVyMTc2"),
    ("processor176router176", "cHJvY2Vzc29yMTc2cm91dGVyMTc2"),
    ("processor176cluster176", "cHJvY2Vzc29yMTc2Y2x1c3RlcjE3Ng"),
    ("processor176mirror176", "cHJvY2Vzc29yMTc2bWlycm9yMTc2"),
    ("processor176filter176", "cHJvY2Vzc29yMTc2ZmlsdGVyMTc2"),
    ("reasoning176filter176", "cmVhc29uaW5nMTc2ZmlsdGVyMTc2"),
    ("reasoning176ranking176", "cmVhc29uaW5nMTc2cmFua2luZzE3Ng"),
    ("reasoning176encoding176", "cmVhc29uaW5nMTc2ZW5jb2RpbmcxNzY"),
    ("reasoning176mapping176", "cmVhc29uaW5nMTc2bWFwcGluZzE3Ng"),
    ("machine176mapping176", "bWFjaGluZTE3Nm1hcHBpbmcxNzY"),
    ("machine176record176", "bWFjaGluZTE3NnJlY29yZDE3Ng"),
    ("machine176candle176", "bWFjaGluZTE3NmNhbmRsZTE3Ng"),
    ("machine176thread176", "bWFjaGluZTE3NnRocmVhZDE3Ng"),
    ("learning176thread176", "bGVhcm5pbmcxNzZ0aHJlYWQxNzY"),
    ("learning176kitten176", "bGVhcm5pbmcxNzZraXR0ZW4xNzY"),
    ("learning176sitting176", "bGVhcm5pbmcxNzZzaXR0aW5nMTc2"),
    ("learning176agent176", "bGVhcm5pbmcxNzZhZ2VudDE3Ng"),
    ("model176agent176", "bW9kZWwxNzZhZ2VudDE3Ng"),
    ("model176angle176", "bW9kZWwxNzZhbmdsZTE3Ng"),
    ("model176universe176", "bW9kZWwxNzZ1bml2ZXJzZTE3Ng"),
    ("model176memory176", "bW9kZWwxNzZtZW1vcnkxNzY"),
    ("token176memory176", "dG9rZW4xNzZtZW1vcnkxNzY"),
    ("token176stream176", "dG9rZW4xNzZzdHJlYW0xNzY"),
    ("token176context176", "dG9rZW4xNzZjb250ZXh0MTc2"),
    ("token176knowledge176", "dG9rZW4xNzZrbm93bGVkZ2UxNzY"),
    ("prompt176knowledge176", "cHJvbXB0MTc2a25vd2xlZGdlMTc2"),
    ("prompt176vector176", "cHJvbXB0MTc2dmVjdG9yMTc2"),
    ("prompt176processor176", "cHJvbXB0MTc2cHJvY2Vzc29yMTc2"),
    ("prompt176reasoning176", "cHJvbXB0MTc2cmVhc29uaW5nMTc2"),
    ("session176reasoning176", "c2Vzc2lvbjE3NnJlYXNvbmluZzE3Ng"),
    ("session176machine176", "c2Vzc2lvbjE3Nm1hY2hpbmUxNzY"),
    ("session176learning176", "c2Vzc2lvbjE3NmxlYXJuaW5nMTc2"),
    ("session176model176", "c2Vzc2lvbjE3Nm1vZGVsMTc2"),
    ("library176model176", "bGlicmFyeTE3Nm1vZGVsMTc2"),
    ("library176token176", "bGlicmFyeTE3NnRva2VuMTc2"),
    ("library176prompt176", "bGlicmFyeTE3NnByb21wdDE3Ng"),
    ("library176session176", "bGlicmFyeTE3NnNlc3Npb24xNzY"),
    ("service176session176", "c2VydmljZTE3NnNlc3Npb24xNzY"),
    ("service176library176", "c2VydmljZTE3NmxpYnJhcnkxNzY"),
    ("service176service176", "c2VydmljZTE3NnNlcnZpY2UxNzY"),
    ("service176gateway176", "c2VydmljZTE3NmdhdGV3YXkxNzY"),
    ("gateway176gateway176", "Z2F0ZXdheTE3NmdhdGV3YXkxNzY"),
    ("gateway176storage176", "Z2F0ZXdheTE3NnN0b3JhZ2UxNzY"),
    ("gateway176network176", "Z2F0ZXdheTE3Nm5ldHdvcmsxNzY"),
    ("gateway176latency176", "Z2F0ZXdheTE3NmxhdGVuY3kxNzY"),
    ("storage176latency176", "c3RvcmFnZTE3NmxhdGVuY3kxNzY"),
    ("storage176buffer176", "c3RvcmFnZTE3NmJ1ZmZlcjE3Ng"),
    ("storage176queue176", "c3RvcmFnZTE3NnF1ZXVlMTc2"),
    ("storage176worker176", "c3RvcmFnZTE3NndvcmtlcjE3Ng"),
    ("network176worker176", "bmV0d29yazE3NndvcmtlcjE3Ng"),
    ("network176kernel176", "bmV0d29yazE3Nmtlcm5lbDE3Ng"),
    ("network176signal176", "bmV0d29yazE3NnNpZ25hbDE3Ng"),
    ("network176packet176", "bmV0d29yazE3NnBhY2tldDE3Ng"),
    ("latency176packet176", "bGF0ZW5jeTE3NnBhY2tldDE3Ng"),
    ("latency176router176", "bGF0ZW5jeTE3NnJvdXRlcjE3Ng"),
    ("latency176cluster176", "bGF0ZW5jeTE3NmNsdXN0ZXIxNzY"),
    ("latency176mirror176", "bGF0ZW5jeTE3Nm1pcnJvcjE3Ng"),
    ("buffer176mirror176", "YnVmZmVyMTc2bWlycm9yMTc2"),
    ("buffer176filter176", "YnVmZmVyMTc2ZmlsdGVyMTc2"),
    ("buffer176ranking176", "YnVmZmVyMTc2cmFua2luZzE3Ng"),
    ("buffer176encoding176", "YnVmZmVyMTc2ZW5jb2RpbmcxNzY"),
    ("queue176encoding176", "cXVldWUxNzZlbmNvZGluZzE3Ng"),
    ("queue176mapping176", "cXVldWUxNzZtYXBwaW5nMTc2"),
    ("queue176record176", "cXVldWUxNzZyZWNvcmQxNzY"),
    ("queue176candle176", "cXVldWUxNzZjYW5kbGUxNzY"),
    ("worker176candle176", "d29ya2VyMTc2Y2FuZGxlMTc2"),
    ("worker176thread176", "d29ya2VyMTc2dGhyZWFkMTc2"),
    ("worker176kitten176", "d29ya2VyMTc2a2l0dGVuMTc2"),
    ("worker176sitting176", "d29ya2VyMTc2c2l0dGluZzE3Ng"),
    ("kernel176sitting176", "a2VybmVsMTc2c2l0dGluZzE3Ng"),
    ("kernel176agent176", "a2VybmVsMTc2YWdlbnQxNzY"),
    ("kernel176angle176", "a2VybmVsMTc2YW5nbGUxNzY"),
    ("kernel176universe176", "a2VybmVsMTc2dW5pdmVyc2UxNzY"),
    ("signal176universe176", "c2lnbmFsMTc2dW5pdmVyc2UxNzY"),
    ("signal176memory176", "c2lnbmFsMTc2bWVtb3J5MTc2"),
    ("signal176stream176", "c2lnbmFsMTc2c3RyZWFtMTc2"),
    ("signal176context176", "c2lnbmFsMTc2Y29udGV4dDE3Ng"),
    ("packet176context176", "cGFja2V0MTc2Y29udGV4dDE3Ng"),
    ("packet176knowledge176", "cGFja2V0MTc2a25vd2xlZGdlMTc2"),
    ("packet176vector176", "cGFja2V0MTc2dmVjdG9yMTc2"),
    ("packet176processor176", "cGFja2V0MTc2cHJvY2Vzc29yMTc2"),
    ("router176processor176", "cm91dGVyMTc2cHJvY2Vzc29yMTc2"),
    ("router176reasoning176", "cm91dGVyMTc2cmVhc29uaW5nMTc2"),
    ("router176machine176", "cm91dGVyMTc2bWFjaGluZTE3Ng"),
    ("router176learning176", "cm91dGVyMTc2bGVhcm5pbmcxNzY"),
    ("cluster176learning176", "Y2x1c3RlcjE3NmxlYXJuaW5nMTc2"),
    ("cluster176model176", "Y2x1c3RlcjE3Nm1vZGVsMTc2"),
    ("cluster176token176", "Y2x1c3RlcjE3NnRva2VuMTc2"),
    ("cluster176prompt176", "Y2x1c3RlcjE3NnByb21wdDE3Ng"),
    ("mirror176prompt176", "bWlycm9yMTc2cHJvbXB0MTc2"),
    ("mirror176session176", "bWlycm9yMTc2c2Vzc2lvbjE3Ng"),
    ("mirror176library176", "bWlycm9yMTc2bGlicmFyeTE3Ng"),
    ("mirror176service176", "bWlycm9yMTc2c2VydmljZTE3Ng"),
    ("filter176service176", "ZmlsdGVyMTc2c2VydmljZTE3Ng"),
    ("filter176gateway176", "ZmlsdGVyMTc2Z2F0ZXdheTE3Ng"),
    ("filter176storage176", "ZmlsdGVyMTc2c3RvcmFnZTE3Ng"),
    ("filter176network176", "ZmlsdGVyMTc2bmV0d29yazE3Ng"),
    ("ranking176network176", "cmFua2luZzE3Nm5ldHdvcmsxNzY"),
    ("ranking176latency176", "cmFua2luZzE3NmxhdGVuY3kxNzY"),
    ("ranking176buffer176", "cmFua2luZzE3NmJ1ZmZlcjE3Ng"),
    ("ranking176queue176", "cmFua2luZzE3NnF1ZXVlMTc2"),
    ("encoding176queue176", "ZW5jb2RpbmcxNzZxdWV1ZTE3Ng"),
    ("encoding176worker176", "ZW5jb2RpbmcxNzZ3b3JrZXIxNzY"),
    ("encoding176kernel176", "ZW5jb2RpbmcxNzZrZXJuZWwxNzY"),
    ("encoding176signal176", "ZW5jb2RpbmcxNzZzaWduYWwxNzY"),
    ("mapping176signal176", "bWFwcGluZzE3NnNpZ25hbDE3Ng"),
    ("mapping176packet176", "bWFwcGluZzE3NnBhY2tldDE3Ng"),
    ("mapping176router176", "bWFwcGluZzE3NnJvdXRlcjE3Ng"),
    ("mapping176cluster176", "bWFwcGluZzE3NmNsdXN0ZXIxNzY"),
    ("record176cluster176", "cmVjb3JkMTc2Y2x1c3RlcjE3Ng"),
    ("record176mirror176", "cmVjb3JkMTc2bWlycm9yMTc2"),
    ("record176filter176", "cmVjb3JkMTc2ZmlsdGVyMTc2"),
    ("record176ranking176", "cmVjb3JkMTc2cmFua2luZzE3Ng"),
    ("candle176ranking176", "Y2FuZGxlMTc2cmFua2luZzE3Ng"),
    ("candle176encoding176", "Y2FuZGxlMTc2ZW5jb2RpbmcxNzY"),
    ("candle176mapping176", "Y2FuZGxlMTc2bWFwcGluZzE3Ng"),
    ("candle176record176", "Y2FuZGxlMTc2cmVjb3JkMTc2"),
    ("thread176record176", "dGhyZWFkMTc2cmVjb3JkMTc2"),
    ("thread176candle176", "dGhyZWFkMTc2Y2FuZGxlMTc2"),
    ("thread176thread176", "dGhyZWFkMTc2dGhyZWFkMTc2"),
    ("thread176kitten176", "dGhyZWFkMTc2a2l0dGVuMTc2"),
    (
        "round 176: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTc2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 176: agentuniverse is a framework for multi agents",
        "cm91bmQgMTc2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 176: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTc2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 176: the processor reads the record then stops",
        "cm91bmQgMTc2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 176: a worker pulls the next task from the queue",
        "cm91bmQgMTc2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 176: signals travel through the network layer",
        "cm91bmQgMTc2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 176: the gateway routes each request by policy",
        "cm91bmQgMTc2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 176: memory grows until the buffer is full",
        "cm91bmQgMTc2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 176: the cluster mirrors every packet twice",
        "cm91bmQgMTc2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 176: ranking uses tokens learned from the corpus",
        "cm91bmQgMTc2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 176: a long session ends when the candle dies",
        "cm91bmQgMTc2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 176: encode the prompt then map the result",
        "cm91bmQgMTc2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 176: the kernel wakes the worker at dawn",
        "cm91bmQgMTc2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 176: service latency drops after the patch",
        "cm91bmQgMTc2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 176: the library caches every vector it sees",
        "cm91bmQgMTc2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 176: agents argue then the debate resolves",
        "cm91bmQgMTc2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 176: the filter keeps only strong matches",
        "cm91bmQgMTc2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 176: the model answers with a short reply",
        "cm91bmQgMTc2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 176: the recorder stores the reasoning trace",
        "cm91bmQgMTc2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 176: the angel watches the processor run",
        "cm91bmQgMTc2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 176: angle of the vector decides the match",
        "cm91bmQgMTc2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 176: the candle burns twice as long at night",
        "cm91bmQgMTc2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 176: a mirror of the universe in one line",
        "cm91bmQgMTc2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 176: the queue drains before the storm", "cm91bmQgMTc2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
