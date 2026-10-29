"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten123kitten123", "a2l0dGVuMTIza2l0dGVuMTIz"),
    ("kitten123sitting123", "a2l0dGVuMTIzc2l0dGluZzEyMw"),
    ("kitten123agent123", "a2l0dGVuMTIzYWdlbnQxMjM"),
    ("kitten123angle123", "a2l0dGVuMTIzYW5nbGUxMjM"),
    ("sitting123angle123", "c2l0dGluZzEyM2FuZ2xlMTIz"),
    ("sitting123universe123", "c2l0dGluZzEyM3VuaXZlcnNlMTIz"),
    ("sitting123memory123", "c2l0dGluZzEyM21lbW9yeTEyMw"),
    ("sitting123stream123", "c2l0dGluZzEyM3N0cmVhbTEyMw"),
    ("agent123stream123", "YWdlbnQxMjNzdHJlYW0xMjM"),
    ("agent123context123", "YWdlbnQxMjNjb250ZXh0MTIz"),
    ("agent123knowledge123", "YWdlbnQxMjNrbm93bGVkZ2UxMjM"),
    ("agent123vector123", "YWdlbnQxMjN2ZWN0b3IxMjM"),
    ("angle123vector123", "YW5nbGUxMjN2ZWN0b3IxMjM"),
    ("angle123processor123", "YW5nbGUxMjNwcm9jZXNzb3IxMjM"),
    ("angle123reasoning123", "YW5nbGUxMjNyZWFzb25pbmcxMjM"),
    ("angle123machine123", "YW5nbGUxMjNtYWNoaW5lMTIz"),
    ("universe123machine123", "dW5pdmVyc2UxMjNtYWNoaW5lMTIz"),
    ("universe123learning123", "dW5pdmVyc2UxMjNsZWFybmluZzEyMw"),
    ("universe123model123", "dW5pdmVyc2UxMjNtb2RlbDEyMw"),
    ("universe123token123", "dW5pdmVyc2UxMjN0b2tlbjEyMw"),
    ("memory123token123", "bWVtb3J5MTIzdG9rZW4xMjM"),
    ("memory123prompt123", "bWVtb3J5MTIzcHJvbXB0MTIz"),
    ("memory123session123", "bWVtb3J5MTIzc2Vzc2lvbjEyMw"),
    ("memory123library123", "bWVtb3J5MTIzbGlicmFyeTEyMw"),
    ("stream123library123", "c3RyZWFtMTIzbGlicmFyeTEyMw"),
    ("stream123service123", "c3RyZWFtMTIzc2VydmljZTEyMw"),
    ("stream123gateway123", "c3RyZWFtMTIzZ2F0ZXdheTEyMw"),
    ("stream123storage123", "c3RyZWFtMTIzc3RvcmFnZTEyMw"),
    ("context123storage123", "Y29udGV4dDEyM3N0b3JhZ2UxMjM"),
    ("context123network123", "Y29udGV4dDEyM25ldHdvcmsxMjM"),
    ("context123latency123", "Y29udGV4dDEyM2xhdGVuY3kxMjM"),
    ("context123buffer123", "Y29udGV4dDEyM2J1ZmZlcjEyMw"),
    ("knowledge123buffer123", "a25vd2xlZGdlMTIzYnVmZmVyMTIz"),
    ("knowledge123queue123", "a25vd2xlZGdlMTIzcXVldWUxMjM"),
    ("knowledge123worker123", "a25vd2xlZGdlMTIzd29ya2VyMTIz"),
    ("knowledge123kernel123", "a25vd2xlZGdlMTIza2VybmVsMTIz"),
    ("vector123kernel123", "dmVjdG9yMTIza2VybmVsMTIz"),
    ("vector123signal123", "dmVjdG9yMTIzc2lnbmFsMTIz"),
    ("vector123packet123", "dmVjdG9yMTIzcGFja2V0MTIz"),
    ("vector123router123", "dmVjdG9yMTIzcm91dGVyMTIz"),
    ("processor123router123", "cHJvY2Vzc29yMTIzcm91dGVyMTIz"),
    ("processor123cluster123", "cHJvY2Vzc29yMTIzY2x1c3RlcjEyMw"),
    ("processor123mirror123", "cHJvY2Vzc29yMTIzbWlycm9yMTIz"),
    ("processor123filter123", "cHJvY2Vzc29yMTIzZmlsdGVyMTIz"),
    ("reasoning123filter123", "cmVhc29uaW5nMTIzZmlsdGVyMTIz"),
    ("reasoning123ranking123", "cmVhc29uaW5nMTIzcmFua2luZzEyMw"),
    ("reasoning123encoding123", "cmVhc29uaW5nMTIzZW5jb2RpbmcxMjM"),
    ("reasoning123mapping123", "cmVhc29uaW5nMTIzbWFwcGluZzEyMw"),
    ("machine123mapping123", "bWFjaGluZTEyM21hcHBpbmcxMjM"),
    ("machine123record123", "bWFjaGluZTEyM3JlY29yZDEyMw"),
    ("machine123candle123", "bWFjaGluZTEyM2NhbmRsZTEyMw"),
    ("machine123thread123", "bWFjaGluZTEyM3RocmVhZDEyMw"),
    ("learning123thread123", "bGVhcm5pbmcxMjN0aHJlYWQxMjM"),
    ("learning123kitten123", "bGVhcm5pbmcxMjNraXR0ZW4xMjM"),
    ("learning123sitting123", "bGVhcm5pbmcxMjNzaXR0aW5nMTIz"),
    ("learning123agent123", "bGVhcm5pbmcxMjNhZ2VudDEyMw"),
    ("model123agent123", "bW9kZWwxMjNhZ2VudDEyMw"),
    ("model123angle123", "bW9kZWwxMjNhbmdsZTEyMw"),
    ("model123universe123", "bW9kZWwxMjN1bml2ZXJzZTEyMw"),
    ("model123memory123", "bW9kZWwxMjNtZW1vcnkxMjM"),
    ("token123memory123", "dG9rZW4xMjNtZW1vcnkxMjM"),
    ("token123stream123", "dG9rZW4xMjNzdHJlYW0xMjM"),
    ("token123context123", "dG9rZW4xMjNjb250ZXh0MTIz"),
    ("token123knowledge123", "dG9rZW4xMjNrbm93bGVkZ2UxMjM"),
    ("prompt123knowledge123", "cHJvbXB0MTIza25vd2xlZGdlMTIz"),
    ("prompt123vector123", "cHJvbXB0MTIzdmVjdG9yMTIz"),
    ("prompt123processor123", "cHJvbXB0MTIzcHJvY2Vzc29yMTIz"),
    ("prompt123reasoning123", "cHJvbXB0MTIzcmVhc29uaW5nMTIz"),
    ("session123reasoning123", "c2Vzc2lvbjEyM3JlYXNvbmluZzEyMw"),
    ("session123machine123", "c2Vzc2lvbjEyM21hY2hpbmUxMjM"),
    ("session123learning123", "c2Vzc2lvbjEyM2xlYXJuaW5nMTIz"),
    ("session123model123", "c2Vzc2lvbjEyM21vZGVsMTIz"),
    ("library123model123", "bGlicmFyeTEyM21vZGVsMTIz"),
    ("library123token123", "bGlicmFyeTEyM3Rva2VuMTIz"),
    ("library123prompt123", "bGlicmFyeTEyM3Byb21wdDEyMw"),
    ("library123session123", "bGlicmFyeTEyM3Nlc3Npb24xMjM"),
    ("service123session123", "c2VydmljZTEyM3Nlc3Npb24xMjM"),
    ("service123library123", "c2VydmljZTEyM2xpYnJhcnkxMjM"),
    ("service123service123", "c2VydmljZTEyM3NlcnZpY2UxMjM"),
    ("service123gateway123", "c2VydmljZTEyM2dhdGV3YXkxMjM"),
    ("gateway123gateway123", "Z2F0ZXdheTEyM2dhdGV3YXkxMjM"),
    ("gateway123storage123", "Z2F0ZXdheTEyM3N0b3JhZ2UxMjM"),
    ("gateway123network123", "Z2F0ZXdheTEyM25ldHdvcmsxMjM"),
    ("gateway123latency123", "Z2F0ZXdheTEyM2xhdGVuY3kxMjM"),
    ("storage123latency123", "c3RvcmFnZTEyM2xhdGVuY3kxMjM"),
    ("storage123buffer123", "c3RvcmFnZTEyM2J1ZmZlcjEyMw"),
    ("storage123queue123", "c3RvcmFnZTEyM3F1ZXVlMTIz"),
    ("storage123worker123", "c3RvcmFnZTEyM3dvcmtlcjEyMw"),
    ("network123worker123", "bmV0d29yazEyM3dvcmtlcjEyMw"),
    ("network123kernel123", "bmV0d29yazEyM2tlcm5lbDEyMw"),
    ("network123signal123", "bmV0d29yazEyM3NpZ25hbDEyMw"),
    ("network123packet123", "bmV0d29yazEyM3BhY2tldDEyMw"),
    ("latency123packet123", "bGF0ZW5jeTEyM3BhY2tldDEyMw"),
    ("latency123router123", "bGF0ZW5jeTEyM3JvdXRlcjEyMw"),
    ("latency123cluster123", "bGF0ZW5jeTEyM2NsdXN0ZXIxMjM"),
    ("latency123mirror123", "bGF0ZW5jeTEyM21pcnJvcjEyMw"),
    ("buffer123mirror123", "YnVmZmVyMTIzbWlycm9yMTIz"),
    ("buffer123filter123", "YnVmZmVyMTIzZmlsdGVyMTIz"),
    ("buffer123ranking123", "YnVmZmVyMTIzcmFua2luZzEyMw"),
    ("buffer123encoding123", "YnVmZmVyMTIzZW5jb2RpbmcxMjM"),
    ("queue123encoding123", "cXVldWUxMjNlbmNvZGluZzEyMw"),
    ("queue123mapping123", "cXVldWUxMjNtYXBwaW5nMTIz"),
    ("queue123record123", "cXVldWUxMjNyZWNvcmQxMjM"),
    ("queue123candle123", "cXVldWUxMjNjYW5kbGUxMjM"),
    ("worker123candle123", "d29ya2VyMTIzY2FuZGxlMTIz"),
    ("worker123thread123", "d29ya2VyMTIzdGhyZWFkMTIz"),
    ("worker123kitten123", "d29ya2VyMTIza2l0dGVuMTIz"),
    ("worker123sitting123", "d29ya2VyMTIzc2l0dGluZzEyMw"),
    ("kernel123sitting123", "a2VybmVsMTIzc2l0dGluZzEyMw"),
    ("kernel123agent123", "a2VybmVsMTIzYWdlbnQxMjM"),
    ("kernel123angle123", "a2VybmVsMTIzYW5nbGUxMjM"),
    ("kernel123universe123", "a2VybmVsMTIzdW5pdmVyc2UxMjM"),
    ("signal123universe123", "c2lnbmFsMTIzdW5pdmVyc2UxMjM"),
    ("signal123memory123", "c2lnbmFsMTIzbWVtb3J5MTIz"),
    ("signal123stream123", "c2lnbmFsMTIzc3RyZWFtMTIz"),
    ("signal123context123", "c2lnbmFsMTIzY29udGV4dDEyMw"),
    ("packet123context123", "cGFja2V0MTIzY29udGV4dDEyMw"),
    ("packet123knowledge123", "cGFja2V0MTIza25vd2xlZGdlMTIz"),
    ("packet123vector123", "cGFja2V0MTIzdmVjdG9yMTIz"),
    ("packet123processor123", "cGFja2V0MTIzcHJvY2Vzc29yMTIz"),
    ("router123processor123", "cm91dGVyMTIzcHJvY2Vzc29yMTIz"),
    ("router123reasoning123", "cm91dGVyMTIzcmVhc29uaW5nMTIz"),
    ("router123machine123", "cm91dGVyMTIzbWFjaGluZTEyMw"),
    ("router123learning123", "cm91dGVyMTIzbGVhcm5pbmcxMjM"),
    ("cluster123learning123", "Y2x1c3RlcjEyM2xlYXJuaW5nMTIz"),
    ("cluster123model123", "Y2x1c3RlcjEyM21vZGVsMTIz"),
    ("cluster123token123", "Y2x1c3RlcjEyM3Rva2VuMTIz"),
    ("cluster123prompt123", "Y2x1c3RlcjEyM3Byb21wdDEyMw"),
    ("mirror123prompt123", "bWlycm9yMTIzcHJvbXB0MTIz"),
    ("mirror123session123", "bWlycm9yMTIzc2Vzc2lvbjEyMw"),
    ("mirror123library123", "bWlycm9yMTIzbGlicmFyeTEyMw"),
    ("mirror123service123", "bWlycm9yMTIzc2VydmljZTEyMw"),
    ("filter123service123", "ZmlsdGVyMTIzc2VydmljZTEyMw"),
    ("filter123gateway123", "ZmlsdGVyMTIzZ2F0ZXdheTEyMw"),
    ("filter123storage123", "ZmlsdGVyMTIzc3RvcmFnZTEyMw"),
    ("filter123network123", "ZmlsdGVyMTIzbmV0d29yazEyMw"),
    ("ranking123network123", "cmFua2luZzEyM25ldHdvcmsxMjM"),
    ("ranking123latency123", "cmFua2luZzEyM2xhdGVuY3kxMjM"),
    ("ranking123buffer123", "cmFua2luZzEyM2J1ZmZlcjEyMw"),
    ("ranking123queue123", "cmFua2luZzEyM3F1ZXVlMTIz"),
    ("encoding123queue123", "ZW5jb2RpbmcxMjNxdWV1ZTEyMw"),
    ("encoding123worker123", "ZW5jb2RpbmcxMjN3b3JrZXIxMjM"),
    ("encoding123kernel123", "ZW5jb2RpbmcxMjNrZXJuZWwxMjM"),
    ("encoding123signal123", "ZW5jb2RpbmcxMjNzaWduYWwxMjM"),
    ("mapping123signal123", "bWFwcGluZzEyM3NpZ25hbDEyMw"),
    ("mapping123packet123", "bWFwcGluZzEyM3BhY2tldDEyMw"),
    ("mapping123router123", "bWFwcGluZzEyM3JvdXRlcjEyMw"),
    ("mapping123cluster123", "bWFwcGluZzEyM2NsdXN0ZXIxMjM"),
    ("record123cluster123", "cmVjb3JkMTIzY2x1c3RlcjEyMw"),
    ("record123mirror123", "cmVjb3JkMTIzbWlycm9yMTIz"),
    ("record123filter123", "cmVjb3JkMTIzZmlsdGVyMTIz"),
    ("record123ranking123", "cmVjb3JkMTIzcmFua2luZzEyMw"),
    ("candle123ranking123", "Y2FuZGxlMTIzcmFua2luZzEyMw"),
    ("candle123encoding123", "Y2FuZGxlMTIzZW5jb2RpbmcxMjM"),
    ("candle123mapping123", "Y2FuZGxlMTIzbWFwcGluZzEyMw"),
    ("candle123record123", "Y2FuZGxlMTIzcmVjb3JkMTIz"),
    ("thread123record123", "dGhyZWFkMTIzcmVjb3JkMTIz"),
    ("thread123candle123", "dGhyZWFkMTIzY2FuZGxlMTIz"),
    ("thread123thread123", "dGhyZWFkMTIzdGhyZWFkMTIz"),
    ("thread123kitten123", "dGhyZWFkMTIza2l0dGVuMTIz"),
    (
        "round 123: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTIzOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 123: agentuniverse is a framework for multi agents",
        "cm91bmQgMTIzOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 123: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTIzOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 123: the processor reads the record then stops",
        "cm91bmQgMTIzOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 123: a worker pulls the next task from the queue",
        "cm91bmQgMTIzOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 123: signals travel through the network layer",
        "cm91bmQgMTIzOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 123: the gateway routes each request by policy",
        "cm91bmQgMTIzOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 123: memory grows until the buffer is full",
        "cm91bmQgMTIzOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 123: the cluster mirrors every packet twice",
        "cm91bmQgMTIzOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 123: ranking uses tokens learned from the corpus",
        "cm91bmQgMTIzOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 123: a long session ends when the candle dies",
        "cm91bmQgMTIzOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 123: encode the prompt then map the result",
        "cm91bmQgMTIzOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 123: the kernel wakes the worker at dawn",
        "cm91bmQgMTIzOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 123: service latency drops after the patch",
        "cm91bmQgMTIzOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 123: the library caches every vector it sees",
        "cm91bmQgMTIzOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 123: agents argue then the debate resolves",
        "cm91bmQgMTIzOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 123: the filter keeps only strong matches",
        "cm91bmQgMTIzOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 123: the model answers with a short reply",
        "cm91bmQgMTIzOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 123: the recorder stores the reasoning trace",
        "cm91bmQgMTIzOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 123: the angel watches the processor run",
        "cm91bmQgMTIzOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 123: angle of the vector decides the match",
        "cm91bmQgMTIzOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 123: the candle burns twice as long at night",
        "cm91bmQgMTIzOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 123: a mirror of the universe in one line",
        "cm91bmQgMTIzOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 123: the queue drains before the storm", "cm91bmQgMTIzOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
