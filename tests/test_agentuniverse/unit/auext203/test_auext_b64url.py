"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten203kitten203", "a2l0dGVuMjAza2l0dGVuMjAz"),
    ("kitten203sitting203", "a2l0dGVuMjAzc2l0dGluZzIwMw"),
    ("kitten203agent203", "a2l0dGVuMjAzYWdlbnQyMDM"),
    ("kitten203angle203", "a2l0dGVuMjAzYW5nbGUyMDM"),
    ("sitting203angle203", "c2l0dGluZzIwM2FuZ2xlMjAz"),
    ("sitting203universe203", "c2l0dGluZzIwM3VuaXZlcnNlMjAz"),
    ("sitting203memory203", "c2l0dGluZzIwM21lbW9yeTIwMw"),
    ("sitting203stream203", "c2l0dGluZzIwM3N0cmVhbTIwMw"),
    ("agent203stream203", "YWdlbnQyMDNzdHJlYW0yMDM"),
    ("agent203context203", "YWdlbnQyMDNjb250ZXh0MjAz"),
    ("agent203knowledge203", "YWdlbnQyMDNrbm93bGVkZ2UyMDM"),
    ("agent203vector203", "YWdlbnQyMDN2ZWN0b3IyMDM"),
    ("angle203vector203", "YW5nbGUyMDN2ZWN0b3IyMDM"),
    ("angle203processor203", "YW5nbGUyMDNwcm9jZXNzb3IyMDM"),
    ("angle203reasoning203", "YW5nbGUyMDNyZWFzb25pbmcyMDM"),
    ("angle203machine203", "YW5nbGUyMDNtYWNoaW5lMjAz"),
    ("universe203machine203", "dW5pdmVyc2UyMDNtYWNoaW5lMjAz"),
    ("universe203learning203", "dW5pdmVyc2UyMDNsZWFybmluZzIwMw"),
    ("universe203model203", "dW5pdmVyc2UyMDNtb2RlbDIwMw"),
    ("universe203token203", "dW5pdmVyc2UyMDN0b2tlbjIwMw"),
    ("memory203token203", "bWVtb3J5MjAzdG9rZW4yMDM"),
    ("memory203prompt203", "bWVtb3J5MjAzcHJvbXB0MjAz"),
    ("memory203session203", "bWVtb3J5MjAzc2Vzc2lvbjIwMw"),
    ("memory203library203", "bWVtb3J5MjAzbGlicmFyeTIwMw"),
    ("stream203library203", "c3RyZWFtMjAzbGlicmFyeTIwMw"),
    ("stream203service203", "c3RyZWFtMjAzc2VydmljZTIwMw"),
    ("stream203gateway203", "c3RyZWFtMjAzZ2F0ZXdheTIwMw"),
    ("stream203storage203", "c3RyZWFtMjAzc3RvcmFnZTIwMw"),
    ("context203storage203", "Y29udGV4dDIwM3N0b3JhZ2UyMDM"),
    ("context203network203", "Y29udGV4dDIwM25ldHdvcmsyMDM"),
    ("context203latency203", "Y29udGV4dDIwM2xhdGVuY3kyMDM"),
    ("context203buffer203", "Y29udGV4dDIwM2J1ZmZlcjIwMw"),
    ("knowledge203buffer203", "a25vd2xlZGdlMjAzYnVmZmVyMjAz"),
    ("knowledge203queue203", "a25vd2xlZGdlMjAzcXVldWUyMDM"),
    ("knowledge203worker203", "a25vd2xlZGdlMjAzd29ya2VyMjAz"),
    ("knowledge203kernel203", "a25vd2xlZGdlMjAza2VybmVsMjAz"),
    ("vector203kernel203", "dmVjdG9yMjAza2VybmVsMjAz"),
    ("vector203signal203", "dmVjdG9yMjAzc2lnbmFsMjAz"),
    ("vector203packet203", "dmVjdG9yMjAzcGFja2V0MjAz"),
    ("vector203router203", "dmVjdG9yMjAzcm91dGVyMjAz"),
    ("processor203router203", "cHJvY2Vzc29yMjAzcm91dGVyMjAz"),
    ("processor203cluster203", "cHJvY2Vzc29yMjAzY2x1c3RlcjIwMw"),
    ("processor203mirror203", "cHJvY2Vzc29yMjAzbWlycm9yMjAz"),
    ("processor203filter203", "cHJvY2Vzc29yMjAzZmlsdGVyMjAz"),
    ("reasoning203filter203", "cmVhc29uaW5nMjAzZmlsdGVyMjAz"),
    ("reasoning203ranking203", "cmVhc29uaW5nMjAzcmFua2luZzIwMw"),
    ("reasoning203encoding203", "cmVhc29uaW5nMjAzZW5jb2RpbmcyMDM"),
    ("reasoning203mapping203", "cmVhc29uaW5nMjAzbWFwcGluZzIwMw"),
    ("machine203mapping203", "bWFjaGluZTIwM21hcHBpbmcyMDM"),
    ("machine203record203", "bWFjaGluZTIwM3JlY29yZDIwMw"),
    ("machine203candle203", "bWFjaGluZTIwM2NhbmRsZTIwMw"),
    ("machine203thread203", "bWFjaGluZTIwM3RocmVhZDIwMw"),
    ("learning203thread203", "bGVhcm5pbmcyMDN0aHJlYWQyMDM"),
    ("learning203kitten203", "bGVhcm5pbmcyMDNraXR0ZW4yMDM"),
    ("learning203sitting203", "bGVhcm5pbmcyMDNzaXR0aW5nMjAz"),
    ("learning203agent203", "bGVhcm5pbmcyMDNhZ2VudDIwMw"),
    ("model203agent203", "bW9kZWwyMDNhZ2VudDIwMw"),
    ("model203angle203", "bW9kZWwyMDNhbmdsZTIwMw"),
    ("model203universe203", "bW9kZWwyMDN1bml2ZXJzZTIwMw"),
    ("model203memory203", "bW9kZWwyMDNtZW1vcnkyMDM"),
    ("token203memory203", "dG9rZW4yMDNtZW1vcnkyMDM"),
    ("token203stream203", "dG9rZW4yMDNzdHJlYW0yMDM"),
    ("token203context203", "dG9rZW4yMDNjb250ZXh0MjAz"),
    ("token203knowledge203", "dG9rZW4yMDNrbm93bGVkZ2UyMDM"),
    ("prompt203knowledge203", "cHJvbXB0MjAza25vd2xlZGdlMjAz"),
    ("prompt203vector203", "cHJvbXB0MjAzdmVjdG9yMjAz"),
    ("prompt203processor203", "cHJvbXB0MjAzcHJvY2Vzc29yMjAz"),
    ("prompt203reasoning203", "cHJvbXB0MjAzcmVhc29uaW5nMjAz"),
    ("session203reasoning203", "c2Vzc2lvbjIwM3JlYXNvbmluZzIwMw"),
    ("session203machine203", "c2Vzc2lvbjIwM21hY2hpbmUyMDM"),
    ("session203learning203", "c2Vzc2lvbjIwM2xlYXJuaW5nMjAz"),
    ("session203model203", "c2Vzc2lvbjIwM21vZGVsMjAz"),
    ("library203model203", "bGlicmFyeTIwM21vZGVsMjAz"),
    ("library203token203", "bGlicmFyeTIwM3Rva2VuMjAz"),
    ("library203prompt203", "bGlicmFyeTIwM3Byb21wdDIwMw"),
    ("library203session203", "bGlicmFyeTIwM3Nlc3Npb24yMDM"),
    ("service203session203", "c2VydmljZTIwM3Nlc3Npb24yMDM"),
    ("service203library203", "c2VydmljZTIwM2xpYnJhcnkyMDM"),
    ("service203service203", "c2VydmljZTIwM3NlcnZpY2UyMDM"),
    ("service203gateway203", "c2VydmljZTIwM2dhdGV3YXkyMDM"),
    ("gateway203gateway203", "Z2F0ZXdheTIwM2dhdGV3YXkyMDM"),
    ("gateway203storage203", "Z2F0ZXdheTIwM3N0b3JhZ2UyMDM"),
    ("gateway203network203", "Z2F0ZXdheTIwM25ldHdvcmsyMDM"),
    ("gateway203latency203", "Z2F0ZXdheTIwM2xhdGVuY3kyMDM"),
    ("storage203latency203", "c3RvcmFnZTIwM2xhdGVuY3kyMDM"),
    ("storage203buffer203", "c3RvcmFnZTIwM2J1ZmZlcjIwMw"),
    ("storage203queue203", "c3RvcmFnZTIwM3F1ZXVlMjAz"),
    ("storage203worker203", "c3RvcmFnZTIwM3dvcmtlcjIwMw"),
    ("network203worker203", "bmV0d29yazIwM3dvcmtlcjIwMw"),
    ("network203kernel203", "bmV0d29yazIwM2tlcm5lbDIwMw"),
    ("network203signal203", "bmV0d29yazIwM3NpZ25hbDIwMw"),
    ("network203packet203", "bmV0d29yazIwM3BhY2tldDIwMw"),
    ("latency203packet203", "bGF0ZW5jeTIwM3BhY2tldDIwMw"),
    ("latency203router203", "bGF0ZW5jeTIwM3JvdXRlcjIwMw"),
    ("latency203cluster203", "bGF0ZW5jeTIwM2NsdXN0ZXIyMDM"),
    ("latency203mirror203", "bGF0ZW5jeTIwM21pcnJvcjIwMw"),
    ("buffer203mirror203", "YnVmZmVyMjAzbWlycm9yMjAz"),
    ("buffer203filter203", "YnVmZmVyMjAzZmlsdGVyMjAz"),
    ("buffer203ranking203", "YnVmZmVyMjAzcmFua2luZzIwMw"),
    ("buffer203encoding203", "YnVmZmVyMjAzZW5jb2RpbmcyMDM"),
    ("queue203encoding203", "cXVldWUyMDNlbmNvZGluZzIwMw"),
    ("queue203mapping203", "cXVldWUyMDNtYXBwaW5nMjAz"),
    ("queue203record203", "cXVldWUyMDNyZWNvcmQyMDM"),
    ("queue203candle203", "cXVldWUyMDNjYW5kbGUyMDM"),
    ("worker203candle203", "d29ya2VyMjAzY2FuZGxlMjAz"),
    ("worker203thread203", "d29ya2VyMjAzdGhyZWFkMjAz"),
    ("worker203kitten203", "d29ya2VyMjAza2l0dGVuMjAz"),
    ("worker203sitting203", "d29ya2VyMjAzc2l0dGluZzIwMw"),
    ("kernel203sitting203", "a2VybmVsMjAzc2l0dGluZzIwMw"),
    ("kernel203agent203", "a2VybmVsMjAzYWdlbnQyMDM"),
    ("kernel203angle203", "a2VybmVsMjAzYW5nbGUyMDM"),
    ("kernel203universe203", "a2VybmVsMjAzdW5pdmVyc2UyMDM"),
    ("signal203universe203", "c2lnbmFsMjAzdW5pdmVyc2UyMDM"),
    ("signal203memory203", "c2lnbmFsMjAzbWVtb3J5MjAz"),
    ("signal203stream203", "c2lnbmFsMjAzc3RyZWFtMjAz"),
    ("signal203context203", "c2lnbmFsMjAzY29udGV4dDIwMw"),
    ("packet203context203", "cGFja2V0MjAzY29udGV4dDIwMw"),
    ("packet203knowledge203", "cGFja2V0MjAza25vd2xlZGdlMjAz"),
    ("packet203vector203", "cGFja2V0MjAzdmVjdG9yMjAz"),
    ("packet203processor203", "cGFja2V0MjAzcHJvY2Vzc29yMjAz"),
    ("router203processor203", "cm91dGVyMjAzcHJvY2Vzc29yMjAz"),
    ("router203reasoning203", "cm91dGVyMjAzcmVhc29uaW5nMjAz"),
    ("router203machine203", "cm91dGVyMjAzbWFjaGluZTIwMw"),
    ("router203learning203", "cm91dGVyMjAzbGVhcm5pbmcyMDM"),
    ("cluster203learning203", "Y2x1c3RlcjIwM2xlYXJuaW5nMjAz"),
    ("cluster203model203", "Y2x1c3RlcjIwM21vZGVsMjAz"),
    ("cluster203token203", "Y2x1c3RlcjIwM3Rva2VuMjAz"),
    ("cluster203prompt203", "Y2x1c3RlcjIwM3Byb21wdDIwMw"),
    ("mirror203prompt203", "bWlycm9yMjAzcHJvbXB0MjAz"),
    ("mirror203session203", "bWlycm9yMjAzc2Vzc2lvbjIwMw"),
    ("mirror203library203", "bWlycm9yMjAzbGlicmFyeTIwMw"),
    ("mirror203service203", "bWlycm9yMjAzc2VydmljZTIwMw"),
    ("filter203service203", "ZmlsdGVyMjAzc2VydmljZTIwMw"),
    ("filter203gateway203", "ZmlsdGVyMjAzZ2F0ZXdheTIwMw"),
    ("filter203storage203", "ZmlsdGVyMjAzc3RvcmFnZTIwMw"),
    ("filter203network203", "ZmlsdGVyMjAzbmV0d29yazIwMw"),
    ("ranking203network203", "cmFua2luZzIwM25ldHdvcmsyMDM"),
    ("ranking203latency203", "cmFua2luZzIwM2xhdGVuY3kyMDM"),
    ("ranking203buffer203", "cmFua2luZzIwM2J1ZmZlcjIwMw"),
    ("ranking203queue203", "cmFua2luZzIwM3F1ZXVlMjAz"),
    ("encoding203queue203", "ZW5jb2RpbmcyMDNxdWV1ZTIwMw"),
    ("encoding203worker203", "ZW5jb2RpbmcyMDN3b3JrZXIyMDM"),
    ("encoding203kernel203", "ZW5jb2RpbmcyMDNrZXJuZWwyMDM"),
    ("encoding203signal203", "ZW5jb2RpbmcyMDNzaWduYWwyMDM"),
    ("mapping203signal203", "bWFwcGluZzIwM3NpZ25hbDIwMw"),
    ("mapping203packet203", "bWFwcGluZzIwM3BhY2tldDIwMw"),
    ("mapping203router203", "bWFwcGluZzIwM3JvdXRlcjIwMw"),
    ("mapping203cluster203", "bWFwcGluZzIwM2NsdXN0ZXIyMDM"),
    ("record203cluster203", "cmVjb3JkMjAzY2x1c3RlcjIwMw"),
    ("record203mirror203", "cmVjb3JkMjAzbWlycm9yMjAz"),
    ("record203filter203", "cmVjb3JkMjAzZmlsdGVyMjAz"),
    ("record203ranking203", "cmVjb3JkMjAzcmFua2luZzIwMw"),
    ("candle203ranking203", "Y2FuZGxlMjAzcmFua2luZzIwMw"),
    ("candle203encoding203", "Y2FuZGxlMjAzZW5jb2RpbmcyMDM"),
    ("candle203mapping203", "Y2FuZGxlMjAzbWFwcGluZzIwMw"),
    ("candle203record203", "Y2FuZGxlMjAzcmVjb3JkMjAz"),
    ("thread203record203", "dGhyZWFkMjAzcmVjb3JkMjAz"),
    ("thread203candle203", "dGhyZWFkMjAzY2FuZGxlMjAz"),
    ("thread203thread203", "dGhyZWFkMjAzdGhyZWFkMjAz"),
    ("thread203kitten203", "dGhyZWFkMjAza2l0dGVuMjAz"),
    (
        "round 203: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjAzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 203: agentuniverse is a framework for multi agents",
        "cm91bmQgMjAzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 203: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjAzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 203: the processor reads the record then stops",
        "cm91bmQgMjAzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 203: a worker pulls the next task from the queue",
        "cm91bmQgMjAzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 203: signals travel through the network layer",
        "cm91bmQgMjAzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 203: the gateway routes each request by policy",
        "cm91bmQgMjAzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 203: memory grows until the buffer is full",
        "cm91bmQgMjAzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 203: the cluster mirrors every packet twice",
        "cm91bmQgMjAzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 203: ranking uses tokens learned from the corpus",
        "cm91bmQgMjAzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 203: a long session ends when the candle dies",
        "cm91bmQgMjAzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 203: encode the prompt then map the result",
        "cm91bmQgMjAzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 203: the kernel wakes the worker at dawn",
        "cm91bmQgMjAzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 203: service latency drops after the patch",
        "cm91bmQgMjAzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 203: the library caches every vector it sees",
        "cm91bmQgMjAzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 203: agents argue then the debate resolves",
        "cm91bmQgMjAzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 203: the filter keeps only strong matches",
        "cm91bmQgMjAzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 203: the model answers with a short reply",
        "cm91bmQgMjAzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 203: the recorder stores the reasoning trace",
        "cm91bmQgMjAzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 203: the angel watches the processor run",
        "cm91bmQgMjAzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 203: angle of the vector decides the match",
        "cm91bmQgMjAzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 203: the candle burns twice as long at night",
        "cm91bmQgMjAzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 203: a mirror of the universe in one line",
        "cm91bmQgMjAzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 203: the queue drains before the storm", "cm91bmQgMjAzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
