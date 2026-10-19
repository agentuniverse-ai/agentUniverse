"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten146kitten146", "a2l0dGVuMTQ2a2l0dGVuMTQ2"),
    ("kitten146sitting146", "a2l0dGVuMTQ2c2l0dGluZzE0Ng"),
    ("kitten146agent146", "a2l0dGVuMTQ2YWdlbnQxNDY"),
    ("kitten146angle146", "a2l0dGVuMTQ2YW5nbGUxNDY"),
    ("sitting146angle146", "c2l0dGluZzE0NmFuZ2xlMTQ2"),
    ("sitting146universe146", "c2l0dGluZzE0NnVuaXZlcnNlMTQ2"),
    ("sitting146memory146", "c2l0dGluZzE0Nm1lbW9yeTE0Ng"),
    ("sitting146stream146", "c2l0dGluZzE0NnN0cmVhbTE0Ng"),
    ("agent146stream146", "YWdlbnQxNDZzdHJlYW0xNDY"),
    ("agent146context146", "YWdlbnQxNDZjb250ZXh0MTQ2"),
    ("agent146knowledge146", "YWdlbnQxNDZrbm93bGVkZ2UxNDY"),
    ("agent146vector146", "YWdlbnQxNDZ2ZWN0b3IxNDY"),
    ("angle146vector146", "YW5nbGUxNDZ2ZWN0b3IxNDY"),
    ("angle146processor146", "YW5nbGUxNDZwcm9jZXNzb3IxNDY"),
    ("angle146reasoning146", "YW5nbGUxNDZyZWFzb25pbmcxNDY"),
    ("angle146machine146", "YW5nbGUxNDZtYWNoaW5lMTQ2"),
    ("universe146machine146", "dW5pdmVyc2UxNDZtYWNoaW5lMTQ2"),
    ("universe146learning146", "dW5pdmVyc2UxNDZsZWFybmluZzE0Ng"),
    ("universe146model146", "dW5pdmVyc2UxNDZtb2RlbDE0Ng"),
    ("universe146token146", "dW5pdmVyc2UxNDZ0b2tlbjE0Ng"),
    ("memory146token146", "bWVtb3J5MTQ2dG9rZW4xNDY"),
    ("memory146prompt146", "bWVtb3J5MTQ2cHJvbXB0MTQ2"),
    ("memory146session146", "bWVtb3J5MTQ2c2Vzc2lvbjE0Ng"),
    ("memory146library146", "bWVtb3J5MTQ2bGlicmFyeTE0Ng"),
    ("stream146library146", "c3RyZWFtMTQ2bGlicmFyeTE0Ng"),
    ("stream146service146", "c3RyZWFtMTQ2c2VydmljZTE0Ng"),
    ("stream146gateway146", "c3RyZWFtMTQ2Z2F0ZXdheTE0Ng"),
    ("stream146storage146", "c3RyZWFtMTQ2c3RvcmFnZTE0Ng"),
    ("context146storage146", "Y29udGV4dDE0NnN0b3JhZ2UxNDY"),
    ("context146network146", "Y29udGV4dDE0Nm5ldHdvcmsxNDY"),
    ("context146latency146", "Y29udGV4dDE0NmxhdGVuY3kxNDY"),
    ("context146buffer146", "Y29udGV4dDE0NmJ1ZmZlcjE0Ng"),
    ("knowledge146buffer146", "a25vd2xlZGdlMTQ2YnVmZmVyMTQ2"),
    ("knowledge146queue146", "a25vd2xlZGdlMTQ2cXVldWUxNDY"),
    ("knowledge146worker146", "a25vd2xlZGdlMTQ2d29ya2VyMTQ2"),
    ("knowledge146kernel146", "a25vd2xlZGdlMTQ2a2VybmVsMTQ2"),
    ("vector146kernel146", "dmVjdG9yMTQ2a2VybmVsMTQ2"),
    ("vector146signal146", "dmVjdG9yMTQ2c2lnbmFsMTQ2"),
    ("vector146packet146", "dmVjdG9yMTQ2cGFja2V0MTQ2"),
    ("vector146router146", "dmVjdG9yMTQ2cm91dGVyMTQ2"),
    ("processor146router146", "cHJvY2Vzc29yMTQ2cm91dGVyMTQ2"),
    ("processor146cluster146", "cHJvY2Vzc29yMTQ2Y2x1c3RlcjE0Ng"),
    ("processor146mirror146", "cHJvY2Vzc29yMTQ2bWlycm9yMTQ2"),
    ("processor146filter146", "cHJvY2Vzc29yMTQ2ZmlsdGVyMTQ2"),
    ("reasoning146filter146", "cmVhc29uaW5nMTQ2ZmlsdGVyMTQ2"),
    ("reasoning146ranking146", "cmVhc29uaW5nMTQ2cmFua2luZzE0Ng"),
    ("reasoning146encoding146", "cmVhc29uaW5nMTQ2ZW5jb2RpbmcxNDY"),
    ("reasoning146mapping146", "cmVhc29uaW5nMTQ2bWFwcGluZzE0Ng"),
    ("machine146mapping146", "bWFjaGluZTE0Nm1hcHBpbmcxNDY"),
    ("machine146record146", "bWFjaGluZTE0NnJlY29yZDE0Ng"),
    ("machine146candle146", "bWFjaGluZTE0NmNhbmRsZTE0Ng"),
    ("machine146thread146", "bWFjaGluZTE0NnRocmVhZDE0Ng"),
    ("learning146thread146", "bGVhcm5pbmcxNDZ0aHJlYWQxNDY"),
    ("learning146kitten146", "bGVhcm5pbmcxNDZraXR0ZW4xNDY"),
    ("learning146sitting146", "bGVhcm5pbmcxNDZzaXR0aW5nMTQ2"),
    ("learning146agent146", "bGVhcm5pbmcxNDZhZ2VudDE0Ng"),
    ("model146agent146", "bW9kZWwxNDZhZ2VudDE0Ng"),
    ("model146angle146", "bW9kZWwxNDZhbmdsZTE0Ng"),
    ("model146universe146", "bW9kZWwxNDZ1bml2ZXJzZTE0Ng"),
    ("model146memory146", "bW9kZWwxNDZtZW1vcnkxNDY"),
    ("token146memory146", "dG9rZW4xNDZtZW1vcnkxNDY"),
    ("token146stream146", "dG9rZW4xNDZzdHJlYW0xNDY"),
    ("token146context146", "dG9rZW4xNDZjb250ZXh0MTQ2"),
    ("token146knowledge146", "dG9rZW4xNDZrbm93bGVkZ2UxNDY"),
    ("prompt146knowledge146", "cHJvbXB0MTQ2a25vd2xlZGdlMTQ2"),
    ("prompt146vector146", "cHJvbXB0MTQ2dmVjdG9yMTQ2"),
    ("prompt146processor146", "cHJvbXB0MTQ2cHJvY2Vzc29yMTQ2"),
    ("prompt146reasoning146", "cHJvbXB0MTQ2cmVhc29uaW5nMTQ2"),
    ("session146reasoning146", "c2Vzc2lvbjE0NnJlYXNvbmluZzE0Ng"),
    ("session146machine146", "c2Vzc2lvbjE0Nm1hY2hpbmUxNDY"),
    ("session146learning146", "c2Vzc2lvbjE0NmxlYXJuaW5nMTQ2"),
    ("session146model146", "c2Vzc2lvbjE0Nm1vZGVsMTQ2"),
    ("library146model146", "bGlicmFyeTE0Nm1vZGVsMTQ2"),
    ("library146token146", "bGlicmFyeTE0NnRva2VuMTQ2"),
    ("library146prompt146", "bGlicmFyeTE0NnByb21wdDE0Ng"),
    ("library146session146", "bGlicmFyeTE0NnNlc3Npb24xNDY"),
    ("service146session146", "c2VydmljZTE0NnNlc3Npb24xNDY"),
    ("service146library146", "c2VydmljZTE0NmxpYnJhcnkxNDY"),
    ("service146service146", "c2VydmljZTE0NnNlcnZpY2UxNDY"),
    ("service146gateway146", "c2VydmljZTE0NmdhdGV3YXkxNDY"),
    ("gateway146gateway146", "Z2F0ZXdheTE0NmdhdGV3YXkxNDY"),
    ("gateway146storage146", "Z2F0ZXdheTE0NnN0b3JhZ2UxNDY"),
    ("gateway146network146", "Z2F0ZXdheTE0Nm5ldHdvcmsxNDY"),
    ("gateway146latency146", "Z2F0ZXdheTE0NmxhdGVuY3kxNDY"),
    ("storage146latency146", "c3RvcmFnZTE0NmxhdGVuY3kxNDY"),
    ("storage146buffer146", "c3RvcmFnZTE0NmJ1ZmZlcjE0Ng"),
    ("storage146queue146", "c3RvcmFnZTE0NnF1ZXVlMTQ2"),
    ("storage146worker146", "c3RvcmFnZTE0NndvcmtlcjE0Ng"),
    ("network146worker146", "bmV0d29yazE0NndvcmtlcjE0Ng"),
    ("network146kernel146", "bmV0d29yazE0Nmtlcm5lbDE0Ng"),
    ("network146signal146", "bmV0d29yazE0NnNpZ25hbDE0Ng"),
    ("network146packet146", "bmV0d29yazE0NnBhY2tldDE0Ng"),
    ("latency146packet146", "bGF0ZW5jeTE0NnBhY2tldDE0Ng"),
    ("latency146router146", "bGF0ZW5jeTE0NnJvdXRlcjE0Ng"),
    ("latency146cluster146", "bGF0ZW5jeTE0NmNsdXN0ZXIxNDY"),
    ("latency146mirror146", "bGF0ZW5jeTE0Nm1pcnJvcjE0Ng"),
    ("buffer146mirror146", "YnVmZmVyMTQ2bWlycm9yMTQ2"),
    ("buffer146filter146", "YnVmZmVyMTQ2ZmlsdGVyMTQ2"),
    ("buffer146ranking146", "YnVmZmVyMTQ2cmFua2luZzE0Ng"),
    ("buffer146encoding146", "YnVmZmVyMTQ2ZW5jb2RpbmcxNDY"),
    ("queue146encoding146", "cXVldWUxNDZlbmNvZGluZzE0Ng"),
    ("queue146mapping146", "cXVldWUxNDZtYXBwaW5nMTQ2"),
    ("queue146record146", "cXVldWUxNDZyZWNvcmQxNDY"),
    ("queue146candle146", "cXVldWUxNDZjYW5kbGUxNDY"),
    ("worker146candle146", "d29ya2VyMTQ2Y2FuZGxlMTQ2"),
    ("worker146thread146", "d29ya2VyMTQ2dGhyZWFkMTQ2"),
    ("worker146kitten146", "d29ya2VyMTQ2a2l0dGVuMTQ2"),
    ("worker146sitting146", "d29ya2VyMTQ2c2l0dGluZzE0Ng"),
    ("kernel146sitting146", "a2VybmVsMTQ2c2l0dGluZzE0Ng"),
    ("kernel146agent146", "a2VybmVsMTQ2YWdlbnQxNDY"),
    ("kernel146angle146", "a2VybmVsMTQ2YW5nbGUxNDY"),
    ("kernel146universe146", "a2VybmVsMTQ2dW5pdmVyc2UxNDY"),
    ("signal146universe146", "c2lnbmFsMTQ2dW5pdmVyc2UxNDY"),
    ("signal146memory146", "c2lnbmFsMTQ2bWVtb3J5MTQ2"),
    ("signal146stream146", "c2lnbmFsMTQ2c3RyZWFtMTQ2"),
    ("signal146context146", "c2lnbmFsMTQ2Y29udGV4dDE0Ng"),
    ("packet146context146", "cGFja2V0MTQ2Y29udGV4dDE0Ng"),
    ("packet146knowledge146", "cGFja2V0MTQ2a25vd2xlZGdlMTQ2"),
    ("packet146vector146", "cGFja2V0MTQ2dmVjdG9yMTQ2"),
    ("packet146processor146", "cGFja2V0MTQ2cHJvY2Vzc29yMTQ2"),
    ("router146processor146", "cm91dGVyMTQ2cHJvY2Vzc29yMTQ2"),
    ("router146reasoning146", "cm91dGVyMTQ2cmVhc29uaW5nMTQ2"),
    ("router146machine146", "cm91dGVyMTQ2bWFjaGluZTE0Ng"),
    ("router146learning146", "cm91dGVyMTQ2bGVhcm5pbmcxNDY"),
    ("cluster146learning146", "Y2x1c3RlcjE0NmxlYXJuaW5nMTQ2"),
    ("cluster146model146", "Y2x1c3RlcjE0Nm1vZGVsMTQ2"),
    ("cluster146token146", "Y2x1c3RlcjE0NnRva2VuMTQ2"),
    ("cluster146prompt146", "Y2x1c3RlcjE0NnByb21wdDE0Ng"),
    ("mirror146prompt146", "bWlycm9yMTQ2cHJvbXB0MTQ2"),
    ("mirror146session146", "bWlycm9yMTQ2c2Vzc2lvbjE0Ng"),
    ("mirror146library146", "bWlycm9yMTQ2bGlicmFyeTE0Ng"),
    ("mirror146service146", "bWlycm9yMTQ2c2VydmljZTE0Ng"),
    ("filter146service146", "ZmlsdGVyMTQ2c2VydmljZTE0Ng"),
    ("filter146gateway146", "ZmlsdGVyMTQ2Z2F0ZXdheTE0Ng"),
    ("filter146storage146", "ZmlsdGVyMTQ2c3RvcmFnZTE0Ng"),
    ("filter146network146", "ZmlsdGVyMTQ2bmV0d29yazE0Ng"),
    ("ranking146network146", "cmFua2luZzE0Nm5ldHdvcmsxNDY"),
    ("ranking146latency146", "cmFua2luZzE0NmxhdGVuY3kxNDY"),
    ("ranking146buffer146", "cmFua2luZzE0NmJ1ZmZlcjE0Ng"),
    ("ranking146queue146", "cmFua2luZzE0NnF1ZXVlMTQ2"),
    ("encoding146queue146", "ZW5jb2RpbmcxNDZxdWV1ZTE0Ng"),
    ("encoding146worker146", "ZW5jb2RpbmcxNDZ3b3JrZXIxNDY"),
    ("encoding146kernel146", "ZW5jb2RpbmcxNDZrZXJuZWwxNDY"),
    ("encoding146signal146", "ZW5jb2RpbmcxNDZzaWduYWwxNDY"),
    ("mapping146signal146", "bWFwcGluZzE0NnNpZ25hbDE0Ng"),
    ("mapping146packet146", "bWFwcGluZzE0NnBhY2tldDE0Ng"),
    ("mapping146router146", "bWFwcGluZzE0NnJvdXRlcjE0Ng"),
    ("mapping146cluster146", "bWFwcGluZzE0NmNsdXN0ZXIxNDY"),
    ("record146cluster146", "cmVjb3JkMTQ2Y2x1c3RlcjE0Ng"),
    ("record146mirror146", "cmVjb3JkMTQ2bWlycm9yMTQ2"),
    ("record146filter146", "cmVjb3JkMTQ2ZmlsdGVyMTQ2"),
    ("record146ranking146", "cmVjb3JkMTQ2cmFua2luZzE0Ng"),
    ("candle146ranking146", "Y2FuZGxlMTQ2cmFua2luZzE0Ng"),
    ("candle146encoding146", "Y2FuZGxlMTQ2ZW5jb2RpbmcxNDY"),
    ("candle146mapping146", "Y2FuZGxlMTQ2bWFwcGluZzE0Ng"),
    ("candle146record146", "Y2FuZGxlMTQ2cmVjb3JkMTQ2"),
    ("thread146record146", "dGhyZWFkMTQ2cmVjb3JkMTQ2"),
    ("thread146candle146", "dGhyZWFkMTQ2Y2FuZGxlMTQ2"),
    ("thread146thread146", "dGhyZWFkMTQ2dGhyZWFkMTQ2"),
    ("thread146kitten146", "dGhyZWFkMTQ2a2l0dGVuMTQ2"),
    (
        "round 146: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTQ2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 146: agentuniverse is a framework for multi agents",
        "cm91bmQgMTQ2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 146: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTQ2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 146: the processor reads the record then stops",
        "cm91bmQgMTQ2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 146: a worker pulls the next task from the queue",
        "cm91bmQgMTQ2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 146: signals travel through the network layer",
        "cm91bmQgMTQ2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 146: the gateway routes each request by policy",
        "cm91bmQgMTQ2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 146: memory grows until the buffer is full",
        "cm91bmQgMTQ2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 146: the cluster mirrors every packet twice",
        "cm91bmQgMTQ2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 146: ranking uses tokens learned from the corpus",
        "cm91bmQgMTQ2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 146: a long session ends when the candle dies",
        "cm91bmQgMTQ2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 146: encode the prompt then map the result",
        "cm91bmQgMTQ2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 146: the kernel wakes the worker at dawn",
        "cm91bmQgMTQ2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 146: service latency drops after the patch",
        "cm91bmQgMTQ2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 146: the library caches every vector it sees",
        "cm91bmQgMTQ2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 146: agents argue then the debate resolves",
        "cm91bmQgMTQ2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 146: the filter keeps only strong matches",
        "cm91bmQgMTQ2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 146: the model answers with a short reply",
        "cm91bmQgMTQ2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 146: the recorder stores the reasoning trace",
        "cm91bmQgMTQ2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 146: the angel watches the processor run",
        "cm91bmQgMTQ2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 146: angle of the vector decides the match",
        "cm91bmQgMTQ2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 146: the candle burns twice as long at night",
        "cm91bmQgMTQ2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 146: a mirror of the universe in one line",
        "cm91bmQgMTQ2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 146: the queue drains before the storm", "cm91bmQgMTQ2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
