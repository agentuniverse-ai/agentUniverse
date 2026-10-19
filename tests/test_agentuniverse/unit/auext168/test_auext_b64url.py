"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten168kitten168", "a2l0dGVuMTY4a2l0dGVuMTY4"),
    ("kitten168sitting168", "a2l0dGVuMTY4c2l0dGluZzE2OA"),
    ("kitten168agent168", "a2l0dGVuMTY4YWdlbnQxNjg"),
    ("kitten168angle168", "a2l0dGVuMTY4YW5nbGUxNjg"),
    ("sitting168angle168", "c2l0dGluZzE2OGFuZ2xlMTY4"),
    ("sitting168universe168", "c2l0dGluZzE2OHVuaXZlcnNlMTY4"),
    ("sitting168memory168", "c2l0dGluZzE2OG1lbW9yeTE2OA"),
    ("sitting168stream168", "c2l0dGluZzE2OHN0cmVhbTE2OA"),
    ("agent168stream168", "YWdlbnQxNjhzdHJlYW0xNjg"),
    ("agent168context168", "YWdlbnQxNjhjb250ZXh0MTY4"),
    ("agent168knowledge168", "YWdlbnQxNjhrbm93bGVkZ2UxNjg"),
    ("agent168vector168", "YWdlbnQxNjh2ZWN0b3IxNjg"),
    ("angle168vector168", "YW5nbGUxNjh2ZWN0b3IxNjg"),
    ("angle168processor168", "YW5nbGUxNjhwcm9jZXNzb3IxNjg"),
    ("angle168reasoning168", "YW5nbGUxNjhyZWFzb25pbmcxNjg"),
    ("angle168machine168", "YW5nbGUxNjhtYWNoaW5lMTY4"),
    ("universe168machine168", "dW5pdmVyc2UxNjhtYWNoaW5lMTY4"),
    ("universe168learning168", "dW5pdmVyc2UxNjhsZWFybmluZzE2OA"),
    ("universe168model168", "dW5pdmVyc2UxNjhtb2RlbDE2OA"),
    ("universe168token168", "dW5pdmVyc2UxNjh0b2tlbjE2OA"),
    ("memory168token168", "bWVtb3J5MTY4dG9rZW4xNjg"),
    ("memory168prompt168", "bWVtb3J5MTY4cHJvbXB0MTY4"),
    ("memory168session168", "bWVtb3J5MTY4c2Vzc2lvbjE2OA"),
    ("memory168library168", "bWVtb3J5MTY4bGlicmFyeTE2OA"),
    ("stream168library168", "c3RyZWFtMTY4bGlicmFyeTE2OA"),
    ("stream168service168", "c3RyZWFtMTY4c2VydmljZTE2OA"),
    ("stream168gateway168", "c3RyZWFtMTY4Z2F0ZXdheTE2OA"),
    ("stream168storage168", "c3RyZWFtMTY4c3RvcmFnZTE2OA"),
    ("context168storage168", "Y29udGV4dDE2OHN0b3JhZ2UxNjg"),
    ("context168network168", "Y29udGV4dDE2OG5ldHdvcmsxNjg"),
    ("context168latency168", "Y29udGV4dDE2OGxhdGVuY3kxNjg"),
    ("context168buffer168", "Y29udGV4dDE2OGJ1ZmZlcjE2OA"),
    ("knowledge168buffer168", "a25vd2xlZGdlMTY4YnVmZmVyMTY4"),
    ("knowledge168queue168", "a25vd2xlZGdlMTY4cXVldWUxNjg"),
    ("knowledge168worker168", "a25vd2xlZGdlMTY4d29ya2VyMTY4"),
    ("knowledge168kernel168", "a25vd2xlZGdlMTY4a2VybmVsMTY4"),
    ("vector168kernel168", "dmVjdG9yMTY4a2VybmVsMTY4"),
    ("vector168signal168", "dmVjdG9yMTY4c2lnbmFsMTY4"),
    ("vector168packet168", "dmVjdG9yMTY4cGFja2V0MTY4"),
    ("vector168router168", "dmVjdG9yMTY4cm91dGVyMTY4"),
    ("processor168router168", "cHJvY2Vzc29yMTY4cm91dGVyMTY4"),
    ("processor168cluster168", "cHJvY2Vzc29yMTY4Y2x1c3RlcjE2OA"),
    ("processor168mirror168", "cHJvY2Vzc29yMTY4bWlycm9yMTY4"),
    ("processor168filter168", "cHJvY2Vzc29yMTY4ZmlsdGVyMTY4"),
    ("reasoning168filter168", "cmVhc29uaW5nMTY4ZmlsdGVyMTY4"),
    ("reasoning168ranking168", "cmVhc29uaW5nMTY4cmFua2luZzE2OA"),
    ("reasoning168encoding168", "cmVhc29uaW5nMTY4ZW5jb2RpbmcxNjg"),
    ("reasoning168mapping168", "cmVhc29uaW5nMTY4bWFwcGluZzE2OA"),
    ("machine168mapping168", "bWFjaGluZTE2OG1hcHBpbmcxNjg"),
    ("machine168record168", "bWFjaGluZTE2OHJlY29yZDE2OA"),
    ("machine168candle168", "bWFjaGluZTE2OGNhbmRsZTE2OA"),
    ("machine168thread168", "bWFjaGluZTE2OHRocmVhZDE2OA"),
    ("learning168thread168", "bGVhcm5pbmcxNjh0aHJlYWQxNjg"),
    ("learning168kitten168", "bGVhcm5pbmcxNjhraXR0ZW4xNjg"),
    ("learning168sitting168", "bGVhcm5pbmcxNjhzaXR0aW5nMTY4"),
    ("learning168agent168", "bGVhcm5pbmcxNjhhZ2VudDE2OA"),
    ("model168agent168", "bW9kZWwxNjhhZ2VudDE2OA"),
    ("model168angle168", "bW9kZWwxNjhhbmdsZTE2OA"),
    ("model168universe168", "bW9kZWwxNjh1bml2ZXJzZTE2OA"),
    ("model168memory168", "bW9kZWwxNjhtZW1vcnkxNjg"),
    ("token168memory168", "dG9rZW4xNjhtZW1vcnkxNjg"),
    ("token168stream168", "dG9rZW4xNjhzdHJlYW0xNjg"),
    ("token168context168", "dG9rZW4xNjhjb250ZXh0MTY4"),
    ("token168knowledge168", "dG9rZW4xNjhrbm93bGVkZ2UxNjg"),
    ("prompt168knowledge168", "cHJvbXB0MTY4a25vd2xlZGdlMTY4"),
    ("prompt168vector168", "cHJvbXB0MTY4dmVjdG9yMTY4"),
    ("prompt168processor168", "cHJvbXB0MTY4cHJvY2Vzc29yMTY4"),
    ("prompt168reasoning168", "cHJvbXB0MTY4cmVhc29uaW5nMTY4"),
    ("session168reasoning168", "c2Vzc2lvbjE2OHJlYXNvbmluZzE2OA"),
    ("session168machine168", "c2Vzc2lvbjE2OG1hY2hpbmUxNjg"),
    ("session168learning168", "c2Vzc2lvbjE2OGxlYXJuaW5nMTY4"),
    ("session168model168", "c2Vzc2lvbjE2OG1vZGVsMTY4"),
    ("library168model168", "bGlicmFyeTE2OG1vZGVsMTY4"),
    ("library168token168", "bGlicmFyeTE2OHRva2VuMTY4"),
    ("library168prompt168", "bGlicmFyeTE2OHByb21wdDE2OA"),
    ("library168session168", "bGlicmFyeTE2OHNlc3Npb24xNjg"),
    ("service168session168", "c2VydmljZTE2OHNlc3Npb24xNjg"),
    ("service168library168", "c2VydmljZTE2OGxpYnJhcnkxNjg"),
    ("service168service168", "c2VydmljZTE2OHNlcnZpY2UxNjg"),
    ("service168gateway168", "c2VydmljZTE2OGdhdGV3YXkxNjg"),
    ("gateway168gateway168", "Z2F0ZXdheTE2OGdhdGV3YXkxNjg"),
    ("gateway168storage168", "Z2F0ZXdheTE2OHN0b3JhZ2UxNjg"),
    ("gateway168network168", "Z2F0ZXdheTE2OG5ldHdvcmsxNjg"),
    ("gateway168latency168", "Z2F0ZXdheTE2OGxhdGVuY3kxNjg"),
    ("storage168latency168", "c3RvcmFnZTE2OGxhdGVuY3kxNjg"),
    ("storage168buffer168", "c3RvcmFnZTE2OGJ1ZmZlcjE2OA"),
    ("storage168queue168", "c3RvcmFnZTE2OHF1ZXVlMTY4"),
    ("storage168worker168", "c3RvcmFnZTE2OHdvcmtlcjE2OA"),
    ("network168worker168", "bmV0d29yazE2OHdvcmtlcjE2OA"),
    ("network168kernel168", "bmV0d29yazE2OGtlcm5lbDE2OA"),
    ("network168signal168", "bmV0d29yazE2OHNpZ25hbDE2OA"),
    ("network168packet168", "bmV0d29yazE2OHBhY2tldDE2OA"),
    ("latency168packet168", "bGF0ZW5jeTE2OHBhY2tldDE2OA"),
    ("latency168router168", "bGF0ZW5jeTE2OHJvdXRlcjE2OA"),
    ("latency168cluster168", "bGF0ZW5jeTE2OGNsdXN0ZXIxNjg"),
    ("latency168mirror168", "bGF0ZW5jeTE2OG1pcnJvcjE2OA"),
    ("buffer168mirror168", "YnVmZmVyMTY4bWlycm9yMTY4"),
    ("buffer168filter168", "YnVmZmVyMTY4ZmlsdGVyMTY4"),
    ("buffer168ranking168", "YnVmZmVyMTY4cmFua2luZzE2OA"),
    ("buffer168encoding168", "YnVmZmVyMTY4ZW5jb2RpbmcxNjg"),
    ("queue168encoding168", "cXVldWUxNjhlbmNvZGluZzE2OA"),
    ("queue168mapping168", "cXVldWUxNjhtYXBwaW5nMTY4"),
    ("queue168record168", "cXVldWUxNjhyZWNvcmQxNjg"),
    ("queue168candle168", "cXVldWUxNjhjYW5kbGUxNjg"),
    ("worker168candle168", "d29ya2VyMTY4Y2FuZGxlMTY4"),
    ("worker168thread168", "d29ya2VyMTY4dGhyZWFkMTY4"),
    ("worker168kitten168", "d29ya2VyMTY4a2l0dGVuMTY4"),
    ("worker168sitting168", "d29ya2VyMTY4c2l0dGluZzE2OA"),
    ("kernel168sitting168", "a2VybmVsMTY4c2l0dGluZzE2OA"),
    ("kernel168agent168", "a2VybmVsMTY4YWdlbnQxNjg"),
    ("kernel168angle168", "a2VybmVsMTY4YW5nbGUxNjg"),
    ("kernel168universe168", "a2VybmVsMTY4dW5pdmVyc2UxNjg"),
    ("signal168universe168", "c2lnbmFsMTY4dW5pdmVyc2UxNjg"),
    ("signal168memory168", "c2lnbmFsMTY4bWVtb3J5MTY4"),
    ("signal168stream168", "c2lnbmFsMTY4c3RyZWFtMTY4"),
    ("signal168context168", "c2lnbmFsMTY4Y29udGV4dDE2OA"),
    ("packet168context168", "cGFja2V0MTY4Y29udGV4dDE2OA"),
    ("packet168knowledge168", "cGFja2V0MTY4a25vd2xlZGdlMTY4"),
    ("packet168vector168", "cGFja2V0MTY4dmVjdG9yMTY4"),
    ("packet168processor168", "cGFja2V0MTY4cHJvY2Vzc29yMTY4"),
    ("router168processor168", "cm91dGVyMTY4cHJvY2Vzc29yMTY4"),
    ("router168reasoning168", "cm91dGVyMTY4cmVhc29uaW5nMTY4"),
    ("router168machine168", "cm91dGVyMTY4bWFjaGluZTE2OA"),
    ("router168learning168", "cm91dGVyMTY4bGVhcm5pbmcxNjg"),
    ("cluster168learning168", "Y2x1c3RlcjE2OGxlYXJuaW5nMTY4"),
    ("cluster168model168", "Y2x1c3RlcjE2OG1vZGVsMTY4"),
    ("cluster168token168", "Y2x1c3RlcjE2OHRva2VuMTY4"),
    ("cluster168prompt168", "Y2x1c3RlcjE2OHByb21wdDE2OA"),
    ("mirror168prompt168", "bWlycm9yMTY4cHJvbXB0MTY4"),
    ("mirror168session168", "bWlycm9yMTY4c2Vzc2lvbjE2OA"),
    ("mirror168library168", "bWlycm9yMTY4bGlicmFyeTE2OA"),
    ("mirror168service168", "bWlycm9yMTY4c2VydmljZTE2OA"),
    ("filter168service168", "ZmlsdGVyMTY4c2VydmljZTE2OA"),
    ("filter168gateway168", "ZmlsdGVyMTY4Z2F0ZXdheTE2OA"),
    ("filter168storage168", "ZmlsdGVyMTY4c3RvcmFnZTE2OA"),
    ("filter168network168", "ZmlsdGVyMTY4bmV0d29yazE2OA"),
    ("ranking168network168", "cmFua2luZzE2OG5ldHdvcmsxNjg"),
    ("ranking168latency168", "cmFua2luZzE2OGxhdGVuY3kxNjg"),
    ("ranking168buffer168", "cmFua2luZzE2OGJ1ZmZlcjE2OA"),
    ("ranking168queue168", "cmFua2luZzE2OHF1ZXVlMTY4"),
    ("encoding168queue168", "ZW5jb2RpbmcxNjhxdWV1ZTE2OA"),
    ("encoding168worker168", "ZW5jb2RpbmcxNjh3b3JrZXIxNjg"),
    ("encoding168kernel168", "ZW5jb2RpbmcxNjhrZXJuZWwxNjg"),
    ("encoding168signal168", "ZW5jb2RpbmcxNjhzaWduYWwxNjg"),
    ("mapping168signal168", "bWFwcGluZzE2OHNpZ25hbDE2OA"),
    ("mapping168packet168", "bWFwcGluZzE2OHBhY2tldDE2OA"),
    ("mapping168router168", "bWFwcGluZzE2OHJvdXRlcjE2OA"),
    ("mapping168cluster168", "bWFwcGluZzE2OGNsdXN0ZXIxNjg"),
    ("record168cluster168", "cmVjb3JkMTY4Y2x1c3RlcjE2OA"),
    ("record168mirror168", "cmVjb3JkMTY4bWlycm9yMTY4"),
    ("record168filter168", "cmVjb3JkMTY4ZmlsdGVyMTY4"),
    ("record168ranking168", "cmVjb3JkMTY4cmFua2luZzE2OA"),
    ("candle168ranking168", "Y2FuZGxlMTY4cmFua2luZzE2OA"),
    ("candle168encoding168", "Y2FuZGxlMTY4ZW5jb2RpbmcxNjg"),
    ("candle168mapping168", "Y2FuZGxlMTY4bWFwcGluZzE2OA"),
    ("candle168record168", "Y2FuZGxlMTY4cmVjb3JkMTY4"),
    ("thread168record168", "dGhyZWFkMTY4cmVjb3JkMTY4"),
    ("thread168candle168", "dGhyZWFkMTY4Y2FuZGxlMTY4"),
    ("thread168thread168", "dGhyZWFkMTY4dGhyZWFkMTY4"),
    ("thread168kitten168", "dGhyZWFkMTY4a2l0dGVuMTY4"),
    (
        "round 168: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTY4OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 168: agentuniverse is a framework for multi agents",
        "cm91bmQgMTY4OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 168: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTY4OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 168: the processor reads the record then stops",
        "cm91bmQgMTY4OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 168: a worker pulls the next task from the queue",
        "cm91bmQgMTY4OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 168: signals travel through the network layer",
        "cm91bmQgMTY4OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 168: the gateway routes each request by policy",
        "cm91bmQgMTY4OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 168: memory grows until the buffer is full",
        "cm91bmQgMTY4OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 168: the cluster mirrors every packet twice",
        "cm91bmQgMTY4OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 168: ranking uses tokens learned from the corpus",
        "cm91bmQgMTY4OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 168: a long session ends when the candle dies",
        "cm91bmQgMTY4OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 168: encode the prompt then map the result",
        "cm91bmQgMTY4OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 168: the kernel wakes the worker at dawn",
        "cm91bmQgMTY4OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 168: service latency drops after the patch",
        "cm91bmQgMTY4OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 168: the library caches every vector it sees",
        "cm91bmQgMTY4OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 168: agents argue then the debate resolves",
        "cm91bmQgMTY4OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 168: the filter keeps only strong matches",
        "cm91bmQgMTY4OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 168: the model answers with a short reply",
        "cm91bmQgMTY4OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 168: the recorder stores the reasoning trace",
        "cm91bmQgMTY4OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 168: the angel watches the processor run",
        "cm91bmQgMTY4OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 168: angle of the vector decides the match",
        "cm91bmQgMTY4OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 168: the candle burns twice as long at night",
        "cm91bmQgMTY4OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 168: a mirror of the universe in one line",
        "cm91bmQgMTY4OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 168: the queue drains before the storm", "cm91bmQgMTY4OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
