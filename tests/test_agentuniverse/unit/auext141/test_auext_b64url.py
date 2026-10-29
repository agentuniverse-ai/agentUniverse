"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten141kitten141", "a2l0dGVuMTQxa2l0dGVuMTQx"),
    ("kitten141sitting141", "a2l0dGVuMTQxc2l0dGluZzE0MQ"),
    ("kitten141agent141", "a2l0dGVuMTQxYWdlbnQxNDE"),
    ("kitten141angle141", "a2l0dGVuMTQxYW5nbGUxNDE"),
    ("sitting141angle141", "c2l0dGluZzE0MWFuZ2xlMTQx"),
    ("sitting141universe141", "c2l0dGluZzE0MXVuaXZlcnNlMTQx"),
    ("sitting141memory141", "c2l0dGluZzE0MW1lbW9yeTE0MQ"),
    ("sitting141stream141", "c2l0dGluZzE0MXN0cmVhbTE0MQ"),
    ("agent141stream141", "YWdlbnQxNDFzdHJlYW0xNDE"),
    ("agent141context141", "YWdlbnQxNDFjb250ZXh0MTQx"),
    ("agent141knowledge141", "YWdlbnQxNDFrbm93bGVkZ2UxNDE"),
    ("agent141vector141", "YWdlbnQxNDF2ZWN0b3IxNDE"),
    ("angle141vector141", "YW5nbGUxNDF2ZWN0b3IxNDE"),
    ("angle141processor141", "YW5nbGUxNDFwcm9jZXNzb3IxNDE"),
    ("angle141reasoning141", "YW5nbGUxNDFyZWFzb25pbmcxNDE"),
    ("angle141machine141", "YW5nbGUxNDFtYWNoaW5lMTQx"),
    ("universe141machine141", "dW5pdmVyc2UxNDFtYWNoaW5lMTQx"),
    ("universe141learning141", "dW5pdmVyc2UxNDFsZWFybmluZzE0MQ"),
    ("universe141model141", "dW5pdmVyc2UxNDFtb2RlbDE0MQ"),
    ("universe141token141", "dW5pdmVyc2UxNDF0b2tlbjE0MQ"),
    ("memory141token141", "bWVtb3J5MTQxdG9rZW4xNDE"),
    ("memory141prompt141", "bWVtb3J5MTQxcHJvbXB0MTQx"),
    ("memory141session141", "bWVtb3J5MTQxc2Vzc2lvbjE0MQ"),
    ("memory141library141", "bWVtb3J5MTQxbGlicmFyeTE0MQ"),
    ("stream141library141", "c3RyZWFtMTQxbGlicmFyeTE0MQ"),
    ("stream141service141", "c3RyZWFtMTQxc2VydmljZTE0MQ"),
    ("stream141gateway141", "c3RyZWFtMTQxZ2F0ZXdheTE0MQ"),
    ("stream141storage141", "c3RyZWFtMTQxc3RvcmFnZTE0MQ"),
    ("context141storage141", "Y29udGV4dDE0MXN0b3JhZ2UxNDE"),
    ("context141network141", "Y29udGV4dDE0MW5ldHdvcmsxNDE"),
    ("context141latency141", "Y29udGV4dDE0MWxhdGVuY3kxNDE"),
    ("context141buffer141", "Y29udGV4dDE0MWJ1ZmZlcjE0MQ"),
    ("knowledge141buffer141", "a25vd2xlZGdlMTQxYnVmZmVyMTQx"),
    ("knowledge141queue141", "a25vd2xlZGdlMTQxcXVldWUxNDE"),
    ("knowledge141worker141", "a25vd2xlZGdlMTQxd29ya2VyMTQx"),
    ("knowledge141kernel141", "a25vd2xlZGdlMTQxa2VybmVsMTQx"),
    ("vector141kernel141", "dmVjdG9yMTQxa2VybmVsMTQx"),
    ("vector141signal141", "dmVjdG9yMTQxc2lnbmFsMTQx"),
    ("vector141packet141", "dmVjdG9yMTQxcGFja2V0MTQx"),
    ("vector141router141", "dmVjdG9yMTQxcm91dGVyMTQx"),
    ("processor141router141", "cHJvY2Vzc29yMTQxcm91dGVyMTQx"),
    ("processor141cluster141", "cHJvY2Vzc29yMTQxY2x1c3RlcjE0MQ"),
    ("processor141mirror141", "cHJvY2Vzc29yMTQxbWlycm9yMTQx"),
    ("processor141filter141", "cHJvY2Vzc29yMTQxZmlsdGVyMTQx"),
    ("reasoning141filter141", "cmVhc29uaW5nMTQxZmlsdGVyMTQx"),
    ("reasoning141ranking141", "cmVhc29uaW5nMTQxcmFua2luZzE0MQ"),
    ("reasoning141encoding141", "cmVhc29uaW5nMTQxZW5jb2RpbmcxNDE"),
    ("reasoning141mapping141", "cmVhc29uaW5nMTQxbWFwcGluZzE0MQ"),
    ("machine141mapping141", "bWFjaGluZTE0MW1hcHBpbmcxNDE"),
    ("machine141record141", "bWFjaGluZTE0MXJlY29yZDE0MQ"),
    ("machine141candle141", "bWFjaGluZTE0MWNhbmRsZTE0MQ"),
    ("machine141thread141", "bWFjaGluZTE0MXRocmVhZDE0MQ"),
    ("learning141thread141", "bGVhcm5pbmcxNDF0aHJlYWQxNDE"),
    ("learning141kitten141", "bGVhcm5pbmcxNDFraXR0ZW4xNDE"),
    ("learning141sitting141", "bGVhcm5pbmcxNDFzaXR0aW5nMTQx"),
    ("learning141agent141", "bGVhcm5pbmcxNDFhZ2VudDE0MQ"),
    ("model141agent141", "bW9kZWwxNDFhZ2VudDE0MQ"),
    ("model141angle141", "bW9kZWwxNDFhbmdsZTE0MQ"),
    ("model141universe141", "bW9kZWwxNDF1bml2ZXJzZTE0MQ"),
    ("model141memory141", "bW9kZWwxNDFtZW1vcnkxNDE"),
    ("token141memory141", "dG9rZW4xNDFtZW1vcnkxNDE"),
    ("token141stream141", "dG9rZW4xNDFzdHJlYW0xNDE"),
    ("token141context141", "dG9rZW4xNDFjb250ZXh0MTQx"),
    ("token141knowledge141", "dG9rZW4xNDFrbm93bGVkZ2UxNDE"),
    ("prompt141knowledge141", "cHJvbXB0MTQxa25vd2xlZGdlMTQx"),
    ("prompt141vector141", "cHJvbXB0MTQxdmVjdG9yMTQx"),
    ("prompt141processor141", "cHJvbXB0MTQxcHJvY2Vzc29yMTQx"),
    ("prompt141reasoning141", "cHJvbXB0MTQxcmVhc29uaW5nMTQx"),
    ("session141reasoning141", "c2Vzc2lvbjE0MXJlYXNvbmluZzE0MQ"),
    ("session141machine141", "c2Vzc2lvbjE0MW1hY2hpbmUxNDE"),
    ("session141learning141", "c2Vzc2lvbjE0MWxlYXJuaW5nMTQx"),
    ("session141model141", "c2Vzc2lvbjE0MW1vZGVsMTQx"),
    ("library141model141", "bGlicmFyeTE0MW1vZGVsMTQx"),
    ("library141token141", "bGlicmFyeTE0MXRva2VuMTQx"),
    ("library141prompt141", "bGlicmFyeTE0MXByb21wdDE0MQ"),
    ("library141session141", "bGlicmFyeTE0MXNlc3Npb24xNDE"),
    ("service141session141", "c2VydmljZTE0MXNlc3Npb24xNDE"),
    ("service141library141", "c2VydmljZTE0MWxpYnJhcnkxNDE"),
    ("service141service141", "c2VydmljZTE0MXNlcnZpY2UxNDE"),
    ("service141gateway141", "c2VydmljZTE0MWdhdGV3YXkxNDE"),
    ("gateway141gateway141", "Z2F0ZXdheTE0MWdhdGV3YXkxNDE"),
    ("gateway141storage141", "Z2F0ZXdheTE0MXN0b3JhZ2UxNDE"),
    ("gateway141network141", "Z2F0ZXdheTE0MW5ldHdvcmsxNDE"),
    ("gateway141latency141", "Z2F0ZXdheTE0MWxhdGVuY3kxNDE"),
    ("storage141latency141", "c3RvcmFnZTE0MWxhdGVuY3kxNDE"),
    ("storage141buffer141", "c3RvcmFnZTE0MWJ1ZmZlcjE0MQ"),
    ("storage141queue141", "c3RvcmFnZTE0MXF1ZXVlMTQx"),
    ("storage141worker141", "c3RvcmFnZTE0MXdvcmtlcjE0MQ"),
    ("network141worker141", "bmV0d29yazE0MXdvcmtlcjE0MQ"),
    ("network141kernel141", "bmV0d29yazE0MWtlcm5lbDE0MQ"),
    ("network141signal141", "bmV0d29yazE0MXNpZ25hbDE0MQ"),
    ("network141packet141", "bmV0d29yazE0MXBhY2tldDE0MQ"),
    ("latency141packet141", "bGF0ZW5jeTE0MXBhY2tldDE0MQ"),
    ("latency141router141", "bGF0ZW5jeTE0MXJvdXRlcjE0MQ"),
    ("latency141cluster141", "bGF0ZW5jeTE0MWNsdXN0ZXIxNDE"),
    ("latency141mirror141", "bGF0ZW5jeTE0MW1pcnJvcjE0MQ"),
    ("buffer141mirror141", "YnVmZmVyMTQxbWlycm9yMTQx"),
    ("buffer141filter141", "YnVmZmVyMTQxZmlsdGVyMTQx"),
    ("buffer141ranking141", "YnVmZmVyMTQxcmFua2luZzE0MQ"),
    ("buffer141encoding141", "YnVmZmVyMTQxZW5jb2RpbmcxNDE"),
    ("queue141encoding141", "cXVldWUxNDFlbmNvZGluZzE0MQ"),
    ("queue141mapping141", "cXVldWUxNDFtYXBwaW5nMTQx"),
    ("queue141record141", "cXVldWUxNDFyZWNvcmQxNDE"),
    ("queue141candle141", "cXVldWUxNDFjYW5kbGUxNDE"),
    ("worker141candle141", "d29ya2VyMTQxY2FuZGxlMTQx"),
    ("worker141thread141", "d29ya2VyMTQxdGhyZWFkMTQx"),
    ("worker141kitten141", "d29ya2VyMTQxa2l0dGVuMTQx"),
    ("worker141sitting141", "d29ya2VyMTQxc2l0dGluZzE0MQ"),
    ("kernel141sitting141", "a2VybmVsMTQxc2l0dGluZzE0MQ"),
    ("kernel141agent141", "a2VybmVsMTQxYWdlbnQxNDE"),
    ("kernel141angle141", "a2VybmVsMTQxYW5nbGUxNDE"),
    ("kernel141universe141", "a2VybmVsMTQxdW5pdmVyc2UxNDE"),
    ("signal141universe141", "c2lnbmFsMTQxdW5pdmVyc2UxNDE"),
    ("signal141memory141", "c2lnbmFsMTQxbWVtb3J5MTQx"),
    ("signal141stream141", "c2lnbmFsMTQxc3RyZWFtMTQx"),
    ("signal141context141", "c2lnbmFsMTQxY29udGV4dDE0MQ"),
    ("packet141context141", "cGFja2V0MTQxY29udGV4dDE0MQ"),
    ("packet141knowledge141", "cGFja2V0MTQxa25vd2xlZGdlMTQx"),
    ("packet141vector141", "cGFja2V0MTQxdmVjdG9yMTQx"),
    ("packet141processor141", "cGFja2V0MTQxcHJvY2Vzc29yMTQx"),
    ("router141processor141", "cm91dGVyMTQxcHJvY2Vzc29yMTQx"),
    ("router141reasoning141", "cm91dGVyMTQxcmVhc29uaW5nMTQx"),
    ("router141machine141", "cm91dGVyMTQxbWFjaGluZTE0MQ"),
    ("router141learning141", "cm91dGVyMTQxbGVhcm5pbmcxNDE"),
    ("cluster141learning141", "Y2x1c3RlcjE0MWxlYXJuaW5nMTQx"),
    ("cluster141model141", "Y2x1c3RlcjE0MW1vZGVsMTQx"),
    ("cluster141token141", "Y2x1c3RlcjE0MXRva2VuMTQx"),
    ("cluster141prompt141", "Y2x1c3RlcjE0MXByb21wdDE0MQ"),
    ("mirror141prompt141", "bWlycm9yMTQxcHJvbXB0MTQx"),
    ("mirror141session141", "bWlycm9yMTQxc2Vzc2lvbjE0MQ"),
    ("mirror141library141", "bWlycm9yMTQxbGlicmFyeTE0MQ"),
    ("mirror141service141", "bWlycm9yMTQxc2VydmljZTE0MQ"),
    ("filter141service141", "ZmlsdGVyMTQxc2VydmljZTE0MQ"),
    ("filter141gateway141", "ZmlsdGVyMTQxZ2F0ZXdheTE0MQ"),
    ("filter141storage141", "ZmlsdGVyMTQxc3RvcmFnZTE0MQ"),
    ("filter141network141", "ZmlsdGVyMTQxbmV0d29yazE0MQ"),
    ("ranking141network141", "cmFua2luZzE0MW5ldHdvcmsxNDE"),
    ("ranking141latency141", "cmFua2luZzE0MWxhdGVuY3kxNDE"),
    ("ranking141buffer141", "cmFua2luZzE0MWJ1ZmZlcjE0MQ"),
    ("ranking141queue141", "cmFua2luZzE0MXF1ZXVlMTQx"),
    ("encoding141queue141", "ZW5jb2RpbmcxNDFxdWV1ZTE0MQ"),
    ("encoding141worker141", "ZW5jb2RpbmcxNDF3b3JrZXIxNDE"),
    ("encoding141kernel141", "ZW5jb2RpbmcxNDFrZXJuZWwxNDE"),
    ("encoding141signal141", "ZW5jb2RpbmcxNDFzaWduYWwxNDE"),
    ("mapping141signal141", "bWFwcGluZzE0MXNpZ25hbDE0MQ"),
    ("mapping141packet141", "bWFwcGluZzE0MXBhY2tldDE0MQ"),
    ("mapping141router141", "bWFwcGluZzE0MXJvdXRlcjE0MQ"),
    ("mapping141cluster141", "bWFwcGluZzE0MWNsdXN0ZXIxNDE"),
    ("record141cluster141", "cmVjb3JkMTQxY2x1c3RlcjE0MQ"),
    ("record141mirror141", "cmVjb3JkMTQxbWlycm9yMTQx"),
    ("record141filter141", "cmVjb3JkMTQxZmlsdGVyMTQx"),
    ("record141ranking141", "cmVjb3JkMTQxcmFua2luZzE0MQ"),
    ("candle141ranking141", "Y2FuZGxlMTQxcmFua2luZzE0MQ"),
    ("candle141encoding141", "Y2FuZGxlMTQxZW5jb2RpbmcxNDE"),
    ("candle141mapping141", "Y2FuZGxlMTQxbWFwcGluZzE0MQ"),
    ("candle141record141", "Y2FuZGxlMTQxcmVjb3JkMTQx"),
    ("thread141record141", "dGhyZWFkMTQxcmVjb3JkMTQx"),
    ("thread141candle141", "dGhyZWFkMTQxY2FuZGxlMTQx"),
    ("thread141thread141", "dGhyZWFkMTQxdGhyZWFkMTQx"),
    ("thread141kitten141", "dGhyZWFkMTQxa2l0dGVuMTQx"),
    (
        "round 141: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTQxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 141: agentuniverse is a framework for multi agents",
        "cm91bmQgMTQxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 141: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTQxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 141: the processor reads the record then stops",
        "cm91bmQgMTQxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 141: a worker pulls the next task from the queue",
        "cm91bmQgMTQxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 141: signals travel through the network layer",
        "cm91bmQgMTQxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 141: the gateway routes each request by policy",
        "cm91bmQgMTQxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 141: memory grows until the buffer is full",
        "cm91bmQgMTQxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 141: the cluster mirrors every packet twice",
        "cm91bmQgMTQxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 141: ranking uses tokens learned from the corpus",
        "cm91bmQgMTQxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 141: a long session ends when the candle dies",
        "cm91bmQgMTQxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 141: encode the prompt then map the result",
        "cm91bmQgMTQxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 141: the kernel wakes the worker at dawn",
        "cm91bmQgMTQxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 141: service latency drops after the patch",
        "cm91bmQgMTQxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 141: the library caches every vector it sees",
        "cm91bmQgMTQxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 141: agents argue then the debate resolves",
        "cm91bmQgMTQxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 141: the filter keeps only strong matches",
        "cm91bmQgMTQxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 141: the model answers with a short reply",
        "cm91bmQgMTQxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 141: the recorder stores the reasoning trace",
        "cm91bmQgMTQxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 141: the angel watches the processor run",
        "cm91bmQgMTQxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 141: angle of the vector decides the match",
        "cm91bmQgMTQxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 141: the candle burns twice as long at night",
        "cm91bmQgMTQxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 141: a mirror of the universe in one line",
        "cm91bmQgMTQxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 141: the queue drains before the storm", "cm91bmQgMTQxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
