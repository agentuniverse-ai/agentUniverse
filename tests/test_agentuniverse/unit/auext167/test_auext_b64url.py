"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten167kitten167", "a2l0dGVuMTY3a2l0dGVuMTY3"),
    ("kitten167sitting167", "a2l0dGVuMTY3c2l0dGluZzE2Nw"),
    ("kitten167agent167", "a2l0dGVuMTY3YWdlbnQxNjc"),
    ("kitten167angle167", "a2l0dGVuMTY3YW5nbGUxNjc"),
    ("sitting167angle167", "c2l0dGluZzE2N2FuZ2xlMTY3"),
    ("sitting167universe167", "c2l0dGluZzE2N3VuaXZlcnNlMTY3"),
    ("sitting167memory167", "c2l0dGluZzE2N21lbW9yeTE2Nw"),
    ("sitting167stream167", "c2l0dGluZzE2N3N0cmVhbTE2Nw"),
    ("agent167stream167", "YWdlbnQxNjdzdHJlYW0xNjc"),
    ("agent167context167", "YWdlbnQxNjdjb250ZXh0MTY3"),
    ("agent167knowledge167", "YWdlbnQxNjdrbm93bGVkZ2UxNjc"),
    ("agent167vector167", "YWdlbnQxNjd2ZWN0b3IxNjc"),
    ("angle167vector167", "YW5nbGUxNjd2ZWN0b3IxNjc"),
    ("angle167processor167", "YW5nbGUxNjdwcm9jZXNzb3IxNjc"),
    ("angle167reasoning167", "YW5nbGUxNjdyZWFzb25pbmcxNjc"),
    ("angle167machine167", "YW5nbGUxNjdtYWNoaW5lMTY3"),
    ("universe167machine167", "dW5pdmVyc2UxNjdtYWNoaW5lMTY3"),
    ("universe167learning167", "dW5pdmVyc2UxNjdsZWFybmluZzE2Nw"),
    ("universe167model167", "dW5pdmVyc2UxNjdtb2RlbDE2Nw"),
    ("universe167token167", "dW5pdmVyc2UxNjd0b2tlbjE2Nw"),
    ("memory167token167", "bWVtb3J5MTY3dG9rZW4xNjc"),
    ("memory167prompt167", "bWVtb3J5MTY3cHJvbXB0MTY3"),
    ("memory167session167", "bWVtb3J5MTY3c2Vzc2lvbjE2Nw"),
    ("memory167library167", "bWVtb3J5MTY3bGlicmFyeTE2Nw"),
    ("stream167library167", "c3RyZWFtMTY3bGlicmFyeTE2Nw"),
    ("stream167service167", "c3RyZWFtMTY3c2VydmljZTE2Nw"),
    ("stream167gateway167", "c3RyZWFtMTY3Z2F0ZXdheTE2Nw"),
    ("stream167storage167", "c3RyZWFtMTY3c3RvcmFnZTE2Nw"),
    ("context167storage167", "Y29udGV4dDE2N3N0b3JhZ2UxNjc"),
    ("context167network167", "Y29udGV4dDE2N25ldHdvcmsxNjc"),
    ("context167latency167", "Y29udGV4dDE2N2xhdGVuY3kxNjc"),
    ("context167buffer167", "Y29udGV4dDE2N2J1ZmZlcjE2Nw"),
    ("knowledge167buffer167", "a25vd2xlZGdlMTY3YnVmZmVyMTY3"),
    ("knowledge167queue167", "a25vd2xlZGdlMTY3cXVldWUxNjc"),
    ("knowledge167worker167", "a25vd2xlZGdlMTY3d29ya2VyMTY3"),
    ("knowledge167kernel167", "a25vd2xlZGdlMTY3a2VybmVsMTY3"),
    ("vector167kernel167", "dmVjdG9yMTY3a2VybmVsMTY3"),
    ("vector167signal167", "dmVjdG9yMTY3c2lnbmFsMTY3"),
    ("vector167packet167", "dmVjdG9yMTY3cGFja2V0MTY3"),
    ("vector167router167", "dmVjdG9yMTY3cm91dGVyMTY3"),
    ("processor167router167", "cHJvY2Vzc29yMTY3cm91dGVyMTY3"),
    ("processor167cluster167", "cHJvY2Vzc29yMTY3Y2x1c3RlcjE2Nw"),
    ("processor167mirror167", "cHJvY2Vzc29yMTY3bWlycm9yMTY3"),
    ("processor167filter167", "cHJvY2Vzc29yMTY3ZmlsdGVyMTY3"),
    ("reasoning167filter167", "cmVhc29uaW5nMTY3ZmlsdGVyMTY3"),
    ("reasoning167ranking167", "cmVhc29uaW5nMTY3cmFua2luZzE2Nw"),
    ("reasoning167encoding167", "cmVhc29uaW5nMTY3ZW5jb2RpbmcxNjc"),
    ("reasoning167mapping167", "cmVhc29uaW5nMTY3bWFwcGluZzE2Nw"),
    ("machine167mapping167", "bWFjaGluZTE2N21hcHBpbmcxNjc"),
    ("machine167record167", "bWFjaGluZTE2N3JlY29yZDE2Nw"),
    ("machine167candle167", "bWFjaGluZTE2N2NhbmRsZTE2Nw"),
    ("machine167thread167", "bWFjaGluZTE2N3RocmVhZDE2Nw"),
    ("learning167thread167", "bGVhcm5pbmcxNjd0aHJlYWQxNjc"),
    ("learning167kitten167", "bGVhcm5pbmcxNjdraXR0ZW4xNjc"),
    ("learning167sitting167", "bGVhcm5pbmcxNjdzaXR0aW5nMTY3"),
    ("learning167agent167", "bGVhcm5pbmcxNjdhZ2VudDE2Nw"),
    ("model167agent167", "bW9kZWwxNjdhZ2VudDE2Nw"),
    ("model167angle167", "bW9kZWwxNjdhbmdsZTE2Nw"),
    ("model167universe167", "bW9kZWwxNjd1bml2ZXJzZTE2Nw"),
    ("model167memory167", "bW9kZWwxNjdtZW1vcnkxNjc"),
    ("token167memory167", "dG9rZW4xNjdtZW1vcnkxNjc"),
    ("token167stream167", "dG9rZW4xNjdzdHJlYW0xNjc"),
    ("token167context167", "dG9rZW4xNjdjb250ZXh0MTY3"),
    ("token167knowledge167", "dG9rZW4xNjdrbm93bGVkZ2UxNjc"),
    ("prompt167knowledge167", "cHJvbXB0MTY3a25vd2xlZGdlMTY3"),
    ("prompt167vector167", "cHJvbXB0MTY3dmVjdG9yMTY3"),
    ("prompt167processor167", "cHJvbXB0MTY3cHJvY2Vzc29yMTY3"),
    ("prompt167reasoning167", "cHJvbXB0MTY3cmVhc29uaW5nMTY3"),
    ("session167reasoning167", "c2Vzc2lvbjE2N3JlYXNvbmluZzE2Nw"),
    ("session167machine167", "c2Vzc2lvbjE2N21hY2hpbmUxNjc"),
    ("session167learning167", "c2Vzc2lvbjE2N2xlYXJuaW5nMTY3"),
    ("session167model167", "c2Vzc2lvbjE2N21vZGVsMTY3"),
    ("library167model167", "bGlicmFyeTE2N21vZGVsMTY3"),
    ("library167token167", "bGlicmFyeTE2N3Rva2VuMTY3"),
    ("library167prompt167", "bGlicmFyeTE2N3Byb21wdDE2Nw"),
    ("library167session167", "bGlicmFyeTE2N3Nlc3Npb24xNjc"),
    ("service167session167", "c2VydmljZTE2N3Nlc3Npb24xNjc"),
    ("service167library167", "c2VydmljZTE2N2xpYnJhcnkxNjc"),
    ("service167service167", "c2VydmljZTE2N3NlcnZpY2UxNjc"),
    ("service167gateway167", "c2VydmljZTE2N2dhdGV3YXkxNjc"),
    ("gateway167gateway167", "Z2F0ZXdheTE2N2dhdGV3YXkxNjc"),
    ("gateway167storage167", "Z2F0ZXdheTE2N3N0b3JhZ2UxNjc"),
    ("gateway167network167", "Z2F0ZXdheTE2N25ldHdvcmsxNjc"),
    ("gateway167latency167", "Z2F0ZXdheTE2N2xhdGVuY3kxNjc"),
    ("storage167latency167", "c3RvcmFnZTE2N2xhdGVuY3kxNjc"),
    ("storage167buffer167", "c3RvcmFnZTE2N2J1ZmZlcjE2Nw"),
    ("storage167queue167", "c3RvcmFnZTE2N3F1ZXVlMTY3"),
    ("storage167worker167", "c3RvcmFnZTE2N3dvcmtlcjE2Nw"),
    ("network167worker167", "bmV0d29yazE2N3dvcmtlcjE2Nw"),
    ("network167kernel167", "bmV0d29yazE2N2tlcm5lbDE2Nw"),
    ("network167signal167", "bmV0d29yazE2N3NpZ25hbDE2Nw"),
    ("network167packet167", "bmV0d29yazE2N3BhY2tldDE2Nw"),
    ("latency167packet167", "bGF0ZW5jeTE2N3BhY2tldDE2Nw"),
    ("latency167router167", "bGF0ZW5jeTE2N3JvdXRlcjE2Nw"),
    ("latency167cluster167", "bGF0ZW5jeTE2N2NsdXN0ZXIxNjc"),
    ("latency167mirror167", "bGF0ZW5jeTE2N21pcnJvcjE2Nw"),
    ("buffer167mirror167", "YnVmZmVyMTY3bWlycm9yMTY3"),
    ("buffer167filter167", "YnVmZmVyMTY3ZmlsdGVyMTY3"),
    ("buffer167ranking167", "YnVmZmVyMTY3cmFua2luZzE2Nw"),
    ("buffer167encoding167", "YnVmZmVyMTY3ZW5jb2RpbmcxNjc"),
    ("queue167encoding167", "cXVldWUxNjdlbmNvZGluZzE2Nw"),
    ("queue167mapping167", "cXVldWUxNjdtYXBwaW5nMTY3"),
    ("queue167record167", "cXVldWUxNjdyZWNvcmQxNjc"),
    ("queue167candle167", "cXVldWUxNjdjYW5kbGUxNjc"),
    ("worker167candle167", "d29ya2VyMTY3Y2FuZGxlMTY3"),
    ("worker167thread167", "d29ya2VyMTY3dGhyZWFkMTY3"),
    ("worker167kitten167", "d29ya2VyMTY3a2l0dGVuMTY3"),
    ("worker167sitting167", "d29ya2VyMTY3c2l0dGluZzE2Nw"),
    ("kernel167sitting167", "a2VybmVsMTY3c2l0dGluZzE2Nw"),
    ("kernel167agent167", "a2VybmVsMTY3YWdlbnQxNjc"),
    ("kernel167angle167", "a2VybmVsMTY3YW5nbGUxNjc"),
    ("kernel167universe167", "a2VybmVsMTY3dW5pdmVyc2UxNjc"),
    ("signal167universe167", "c2lnbmFsMTY3dW5pdmVyc2UxNjc"),
    ("signal167memory167", "c2lnbmFsMTY3bWVtb3J5MTY3"),
    ("signal167stream167", "c2lnbmFsMTY3c3RyZWFtMTY3"),
    ("signal167context167", "c2lnbmFsMTY3Y29udGV4dDE2Nw"),
    ("packet167context167", "cGFja2V0MTY3Y29udGV4dDE2Nw"),
    ("packet167knowledge167", "cGFja2V0MTY3a25vd2xlZGdlMTY3"),
    ("packet167vector167", "cGFja2V0MTY3dmVjdG9yMTY3"),
    ("packet167processor167", "cGFja2V0MTY3cHJvY2Vzc29yMTY3"),
    ("router167processor167", "cm91dGVyMTY3cHJvY2Vzc29yMTY3"),
    ("router167reasoning167", "cm91dGVyMTY3cmVhc29uaW5nMTY3"),
    ("router167machine167", "cm91dGVyMTY3bWFjaGluZTE2Nw"),
    ("router167learning167", "cm91dGVyMTY3bGVhcm5pbmcxNjc"),
    ("cluster167learning167", "Y2x1c3RlcjE2N2xlYXJuaW5nMTY3"),
    ("cluster167model167", "Y2x1c3RlcjE2N21vZGVsMTY3"),
    ("cluster167token167", "Y2x1c3RlcjE2N3Rva2VuMTY3"),
    ("cluster167prompt167", "Y2x1c3RlcjE2N3Byb21wdDE2Nw"),
    ("mirror167prompt167", "bWlycm9yMTY3cHJvbXB0MTY3"),
    ("mirror167session167", "bWlycm9yMTY3c2Vzc2lvbjE2Nw"),
    ("mirror167library167", "bWlycm9yMTY3bGlicmFyeTE2Nw"),
    ("mirror167service167", "bWlycm9yMTY3c2VydmljZTE2Nw"),
    ("filter167service167", "ZmlsdGVyMTY3c2VydmljZTE2Nw"),
    ("filter167gateway167", "ZmlsdGVyMTY3Z2F0ZXdheTE2Nw"),
    ("filter167storage167", "ZmlsdGVyMTY3c3RvcmFnZTE2Nw"),
    ("filter167network167", "ZmlsdGVyMTY3bmV0d29yazE2Nw"),
    ("ranking167network167", "cmFua2luZzE2N25ldHdvcmsxNjc"),
    ("ranking167latency167", "cmFua2luZzE2N2xhdGVuY3kxNjc"),
    ("ranking167buffer167", "cmFua2luZzE2N2J1ZmZlcjE2Nw"),
    ("ranking167queue167", "cmFua2luZzE2N3F1ZXVlMTY3"),
    ("encoding167queue167", "ZW5jb2RpbmcxNjdxdWV1ZTE2Nw"),
    ("encoding167worker167", "ZW5jb2RpbmcxNjd3b3JrZXIxNjc"),
    ("encoding167kernel167", "ZW5jb2RpbmcxNjdrZXJuZWwxNjc"),
    ("encoding167signal167", "ZW5jb2RpbmcxNjdzaWduYWwxNjc"),
    ("mapping167signal167", "bWFwcGluZzE2N3NpZ25hbDE2Nw"),
    ("mapping167packet167", "bWFwcGluZzE2N3BhY2tldDE2Nw"),
    ("mapping167router167", "bWFwcGluZzE2N3JvdXRlcjE2Nw"),
    ("mapping167cluster167", "bWFwcGluZzE2N2NsdXN0ZXIxNjc"),
    ("record167cluster167", "cmVjb3JkMTY3Y2x1c3RlcjE2Nw"),
    ("record167mirror167", "cmVjb3JkMTY3bWlycm9yMTY3"),
    ("record167filter167", "cmVjb3JkMTY3ZmlsdGVyMTY3"),
    ("record167ranking167", "cmVjb3JkMTY3cmFua2luZzE2Nw"),
    ("candle167ranking167", "Y2FuZGxlMTY3cmFua2luZzE2Nw"),
    ("candle167encoding167", "Y2FuZGxlMTY3ZW5jb2RpbmcxNjc"),
    ("candle167mapping167", "Y2FuZGxlMTY3bWFwcGluZzE2Nw"),
    ("candle167record167", "Y2FuZGxlMTY3cmVjb3JkMTY3"),
    ("thread167record167", "dGhyZWFkMTY3cmVjb3JkMTY3"),
    ("thread167candle167", "dGhyZWFkMTY3Y2FuZGxlMTY3"),
    ("thread167thread167", "dGhyZWFkMTY3dGhyZWFkMTY3"),
    ("thread167kitten167", "dGhyZWFkMTY3a2l0dGVuMTY3"),
    (
        "round 167: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTY3OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 167: agentuniverse is a framework for multi agents",
        "cm91bmQgMTY3OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 167: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTY3OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 167: the processor reads the record then stops",
        "cm91bmQgMTY3OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 167: a worker pulls the next task from the queue",
        "cm91bmQgMTY3OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 167: signals travel through the network layer",
        "cm91bmQgMTY3OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 167: the gateway routes each request by policy",
        "cm91bmQgMTY3OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 167: memory grows until the buffer is full",
        "cm91bmQgMTY3OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 167: the cluster mirrors every packet twice",
        "cm91bmQgMTY3OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 167: ranking uses tokens learned from the corpus",
        "cm91bmQgMTY3OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 167: a long session ends when the candle dies",
        "cm91bmQgMTY3OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 167: encode the prompt then map the result",
        "cm91bmQgMTY3OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 167: the kernel wakes the worker at dawn",
        "cm91bmQgMTY3OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 167: service latency drops after the patch",
        "cm91bmQgMTY3OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 167: the library caches every vector it sees",
        "cm91bmQgMTY3OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 167: agents argue then the debate resolves",
        "cm91bmQgMTY3OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 167: the filter keeps only strong matches",
        "cm91bmQgMTY3OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 167: the model answers with a short reply",
        "cm91bmQgMTY3OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 167: the recorder stores the reasoning trace",
        "cm91bmQgMTY3OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 167: the angel watches the processor run",
        "cm91bmQgMTY3OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 167: angle of the vector decides the match",
        "cm91bmQgMTY3OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 167: the candle burns twice as long at night",
        "cm91bmQgMTY3OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 167: a mirror of the universe in one line",
        "cm91bmQgMTY3OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 167: the queue drains before the storm", "cm91bmQgMTY3OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
