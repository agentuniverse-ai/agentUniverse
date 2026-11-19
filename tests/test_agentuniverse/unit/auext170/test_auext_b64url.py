"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten170kitten170", "a2l0dGVuMTcwa2l0dGVuMTcw"),
    ("kitten170sitting170", "a2l0dGVuMTcwc2l0dGluZzE3MA"),
    ("kitten170agent170", "a2l0dGVuMTcwYWdlbnQxNzA"),
    ("kitten170angle170", "a2l0dGVuMTcwYW5nbGUxNzA"),
    ("sitting170angle170", "c2l0dGluZzE3MGFuZ2xlMTcw"),
    ("sitting170universe170", "c2l0dGluZzE3MHVuaXZlcnNlMTcw"),
    ("sitting170memory170", "c2l0dGluZzE3MG1lbW9yeTE3MA"),
    ("sitting170stream170", "c2l0dGluZzE3MHN0cmVhbTE3MA"),
    ("agent170stream170", "YWdlbnQxNzBzdHJlYW0xNzA"),
    ("agent170context170", "YWdlbnQxNzBjb250ZXh0MTcw"),
    ("agent170knowledge170", "YWdlbnQxNzBrbm93bGVkZ2UxNzA"),
    ("agent170vector170", "YWdlbnQxNzB2ZWN0b3IxNzA"),
    ("angle170vector170", "YW5nbGUxNzB2ZWN0b3IxNzA"),
    ("angle170processor170", "YW5nbGUxNzBwcm9jZXNzb3IxNzA"),
    ("angle170reasoning170", "YW5nbGUxNzByZWFzb25pbmcxNzA"),
    ("angle170machine170", "YW5nbGUxNzBtYWNoaW5lMTcw"),
    ("universe170machine170", "dW5pdmVyc2UxNzBtYWNoaW5lMTcw"),
    ("universe170learning170", "dW5pdmVyc2UxNzBsZWFybmluZzE3MA"),
    ("universe170model170", "dW5pdmVyc2UxNzBtb2RlbDE3MA"),
    ("universe170token170", "dW5pdmVyc2UxNzB0b2tlbjE3MA"),
    ("memory170token170", "bWVtb3J5MTcwdG9rZW4xNzA"),
    ("memory170prompt170", "bWVtb3J5MTcwcHJvbXB0MTcw"),
    ("memory170session170", "bWVtb3J5MTcwc2Vzc2lvbjE3MA"),
    ("memory170library170", "bWVtb3J5MTcwbGlicmFyeTE3MA"),
    ("stream170library170", "c3RyZWFtMTcwbGlicmFyeTE3MA"),
    ("stream170service170", "c3RyZWFtMTcwc2VydmljZTE3MA"),
    ("stream170gateway170", "c3RyZWFtMTcwZ2F0ZXdheTE3MA"),
    ("stream170storage170", "c3RyZWFtMTcwc3RvcmFnZTE3MA"),
    ("context170storage170", "Y29udGV4dDE3MHN0b3JhZ2UxNzA"),
    ("context170network170", "Y29udGV4dDE3MG5ldHdvcmsxNzA"),
    ("context170latency170", "Y29udGV4dDE3MGxhdGVuY3kxNzA"),
    ("context170buffer170", "Y29udGV4dDE3MGJ1ZmZlcjE3MA"),
    ("knowledge170buffer170", "a25vd2xlZGdlMTcwYnVmZmVyMTcw"),
    ("knowledge170queue170", "a25vd2xlZGdlMTcwcXVldWUxNzA"),
    ("knowledge170worker170", "a25vd2xlZGdlMTcwd29ya2VyMTcw"),
    ("knowledge170kernel170", "a25vd2xlZGdlMTcwa2VybmVsMTcw"),
    ("vector170kernel170", "dmVjdG9yMTcwa2VybmVsMTcw"),
    ("vector170signal170", "dmVjdG9yMTcwc2lnbmFsMTcw"),
    ("vector170packet170", "dmVjdG9yMTcwcGFja2V0MTcw"),
    ("vector170router170", "dmVjdG9yMTcwcm91dGVyMTcw"),
    ("processor170router170", "cHJvY2Vzc29yMTcwcm91dGVyMTcw"),
    ("processor170cluster170", "cHJvY2Vzc29yMTcwY2x1c3RlcjE3MA"),
    ("processor170mirror170", "cHJvY2Vzc29yMTcwbWlycm9yMTcw"),
    ("processor170filter170", "cHJvY2Vzc29yMTcwZmlsdGVyMTcw"),
    ("reasoning170filter170", "cmVhc29uaW5nMTcwZmlsdGVyMTcw"),
    ("reasoning170ranking170", "cmVhc29uaW5nMTcwcmFua2luZzE3MA"),
    ("reasoning170encoding170", "cmVhc29uaW5nMTcwZW5jb2RpbmcxNzA"),
    ("reasoning170mapping170", "cmVhc29uaW5nMTcwbWFwcGluZzE3MA"),
    ("machine170mapping170", "bWFjaGluZTE3MG1hcHBpbmcxNzA"),
    ("machine170record170", "bWFjaGluZTE3MHJlY29yZDE3MA"),
    ("machine170candle170", "bWFjaGluZTE3MGNhbmRsZTE3MA"),
    ("machine170thread170", "bWFjaGluZTE3MHRocmVhZDE3MA"),
    ("learning170thread170", "bGVhcm5pbmcxNzB0aHJlYWQxNzA"),
    ("learning170kitten170", "bGVhcm5pbmcxNzBraXR0ZW4xNzA"),
    ("learning170sitting170", "bGVhcm5pbmcxNzBzaXR0aW5nMTcw"),
    ("learning170agent170", "bGVhcm5pbmcxNzBhZ2VudDE3MA"),
    ("model170agent170", "bW9kZWwxNzBhZ2VudDE3MA"),
    ("model170angle170", "bW9kZWwxNzBhbmdsZTE3MA"),
    ("model170universe170", "bW9kZWwxNzB1bml2ZXJzZTE3MA"),
    ("model170memory170", "bW9kZWwxNzBtZW1vcnkxNzA"),
    ("token170memory170", "dG9rZW4xNzBtZW1vcnkxNzA"),
    ("token170stream170", "dG9rZW4xNzBzdHJlYW0xNzA"),
    ("token170context170", "dG9rZW4xNzBjb250ZXh0MTcw"),
    ("token170knowledge170", "dG9rZW4xNzBrbm93bGVkZ2UxNzA"),
    ("prompt170knowledge170", "cHJvbXB0MTcwa25vd2xlZGdlMTcw"),
    ("prompt170vector170", "cHJvbXB0MTcwdmVjdG9yMTcw"),
    ("prompt170processor170", "cHJvbXB0MTcwcHJvY2Vzc29yMTcw"),
    ("prompt170reasoning170", "cHJvbXB0MTcwcmVhc29uaW5nMTcw"),
    ("session170reasoning170", "c2Vzc2lvbjE3MHJlYXNvbmluZzE3MA"),
    ("session170machine170", "c2Vzc2lvbjE3MG1hY2hpbmUxNzA"),
    ("session170learning170", "c2Vzc2lvbjE3MGxlYXJuaW5nMTcw"),
    ("session170model170", "c2Vzc2lvbjE3MG1vZGVsMTcw"),
    ("library170model170", "bGlicmFyeTE3MG1vZGVsMTcw"),
    ("library170token170", "bGlicmFyeTE3MHRva2VuMTcw"),
    ("library170prompt170", "bGlicmFyeTE3MHByb21wdDE3MA"),
    ("library170session170", "bGlicmFyeTE3MHNlc3Npb24xNzA"),
    ("service170session170", "c2VydmljZTE3MHNlc3Npb24xNzA"),
    ("service170library170", "c2VydmljZTE3MGxpYnJhcnkxNzA"),
    ("service170service170", "c2VydmljZTE3MHNlcnZpY2UxNzA"),
    ("service170gateway170", "c2VydmljZTE3MGdhdGV3YXkxNzA"),
    ("gateway170gateway170", "Z2F0ZXdheTE3MGdhdGV3YXkxNzA"),
    ("gateway170storage170", "Z2F0ZXdheTE3MHN0b3JhZ2UxNzA"),
    ("gateway170network170", "Z2F0ZXdheTE3MG5ldHdvcmsxNzA"),
    ("gateway170latency170", "Z2F0ZXdheTE3MGxhdGVuY3kxNzA"),
    ("storage170latency170", "c3RvcmFnZTE3MGxhdGVuY3kxNzA"),
    ("storage170buffer170", "c3RvcmFnZTE3MGJ1ZmZlcjE3MA"),
    ("storage170queue170", "c3RvcmFnZTE3MHF1ZXVlMTcw"),
    ("storage170worker170", "c3RvcmFnZTE3MHdvcmtlcjE3MA"),
    ("network170worker170", "bmV0d29yazE3MHdvcmtlcjE3MA"),
    ("network170kernel170", "bmV0d29yazE3MGtlcm5lbDE3MA"),
    ("network170signal170", "bmV0d29yazE3MHNpZ25hbDE3MA"),
    ("network170packet170", "bmV0d29yazE3MHBhY2tldDE3MA"),
    ("latency170packet170", "bGF0ZW5jeTE3MHBhY2tldDE3MA"),
    ("latency170router170", "bGF0ZW5jeTE3MHJvdXRlcjE3MA"),
    ("latency170cluster170", "bGF0ZW5jeTE3MGNsdXN0ZXIxNzA"),
    ("latency170mirror170", "bGF0ZW5jeTE3MG1pcnJvcjE3MA"),
    ("buffer170mirror170", "YnVmZmVyMTcwbWlycm9yMTcw"),
    ("buffer170filter170", "YnVmZmVyMTcwZmlsdGVyMTcw"),
    ("buffer170ranking170", "YnVmZmVyMTcwcmFua2luZzE3MA"),
    ("buffer170encoding170", "YnVmZmVyMTcwZW5jb2RpbmcxNzA"),
    ("queue170encoding170", "cXVldWUxNzBlbmNvZGluZzE3MA"),
    ("queue170mapping170", "cXVldWUxNzBtYXBwaW5nMTcw"),
    ("queue170record170", "cXVldWUxNzByZWNvcmQxNzA"),
    ("queue170candle170", "cXVldWUxNzBjYW5kbGUxNzA"),
    ("worker170candle170", "d29ya2VyMTcwY2FuZGxlMTcw"),
    ("worker170thread170", "d29ya2VyMTcwdGhyZWFkMTcw"),
    ("worker170kitten170", "d29ya2VyMTcwa2l0dGVuMTcw"),
    ("worker170sitting170", "d29ya2VyMTcwc2l0dGluZzE3MA"),
    ("kernel170sitting170", "a2VybmVsMTcwc2l0dGluZzE3MA"),
    ("kernel170agent170", "a2VybmVsMTcwYWdlbnQxNzA"),
    ("kernel170angle170", "a2VybmVsMTcwYW5nbGUxNzA"),
    ("kernel170universe170", "a2VybmVsMTcwdW5pdmVyc2UxNzA"),
    ("signal170universe170", "c2lnbmFsMTcwdW5pdmVyc2UxNzA"),
    ("signal170memory170", "c2lnbmFsMTcwbWVtb3J5MTcw"),
    ("signal170stream170", "c2lnbmFsMTcwc3RyZWFtMTcw"),
    ("signal170context170", "c2lnbmFsMTcwY29udGV4dDE3MA"),
    ("packet170context170", "cGFja2V0MTcwY29udGV4dDE3MA"),
    ("packet170knowledge170", "cGFja2V0MTcwa25vd2xlZGdlMTcw"),
    ("packet170vector170", "cGFja2V0MTcwdmVjdG9yMTcw"),
    ("packet170processor170", "cGFja2V0MTcwcHJvY2Vzc29yMTcw"),
    ("router170processor170", "cm91dGVyMTcwcHJvY2Vzc29yMTcw"),
    ("router170reasoning170", "cm91dGVyMTcwcmVhc29uaW5nMTcw"),
    ("router170machine170", "cm91dGVyMTcwbWFjaGluZTE3MA"),
    ("router170learning170", "cm91dGVyMTcwbGVhcm5pbmcxNzA"),
    ("cluster170learning170", "Y2x1c3RlcjE3MGxlYXJuaW5nMTcw"),
    ("cluster170model170", "Y2x1c3RlcjE3MG1vZGVsMTcw"),
    ("cluster170token170", "Y2x1c3RlcjE3MHRva2VuMTcw"),
    ("cluster170prompt170", "Y2x1c3RlcjE3MHByb21wdDE3MA"),
    ("mirror170prompt170", "bWlycm9yMTcwcHJvbXB0MTcw"),
    ("mirror170session170", "bWlycm9yMTcwc2Vzc2lvbjE3MA"),
    ("mirror170library170", "bWlycm9yMTcwbGlicmFyeTE3MA"),
    ("mirror170service170", "bWlycm9yMTcwc2VydmljZTE3MA"),
    ("filter170service170", "ZmlsdGVyMTcwc2VydmljZTE3MA"),
    ("filter170gateway170", "ZmlsdGVyMTcwZ2F0ZXdheTE3MA"),
    ("filter170storage170", "ZmlsdGVyMTcwc3RvcmFnZTE3MA"),
    ("filter170network170", "ZmlsdGVyMTcwbmV0d29yazE3MA"),
    ("ranking170network170", "cmFua2luZzE3MG5ldHdvcmsxNzA"),
    ("ranking170latency170", "cmFua2luZzE3MGxhdGVuY3kxNzA"),
    ("ranking170buffer170", "cmFua2luZzE3MGJ1ZmZlcjE3MA"),
    ("ranking170queue170", "cmFua2luZzE3MHF1ZXVlMTcw"),
    ("encoding170queue170", "ZW5jb2RpbmcxNzBxdWV1ZTE3MA"),
    ("encoding170worker170", "ZW5jb2RpbmcxNzB3b3JrZXIxNzA"),
    ("encoding170kernel170", "ZW5jb2RpbmcxNzBrZXJuZWwxNzA"),
    ("encoding170signal170", "ZW5jb2RpbmcxNzBzaWduYWwxNzA"),
    ("mapping170signal170", "bWFwcGluZzE3MHNpZ25hbDE3MA"),
    ("mapping170packet170", "bWFwcGluZzE3MHBhY2tldDE3MA"),
    ("mapping170router170", "bWFwcGluZzE3MHJvdXRlcjE3MA"),
    ("mapping170cluster170", "bWFwcGluZzE3MGNsdXN0ZXIxNzA"),
    ("record170cluster170", "cmVjb3JkMTcwY2x1c3RlcjE3MA"),
    ("record170mirror170", "cmVjb3JkMTcwbWlycm9yMTcw"),
    ("record170filter170", "cmVjb3JkMTcwZmlsdGVyMTcw"),
    ("record170ranking170", "cmVjb3JkMTcwcmFua2luZzE3MA"),
    ("candle170ranking170", "Y2FuZGxlMTcwcmFua2luZzE3MA"),
    ("candle170encoding170", "Y2FuZGxlMTcwZW5jb2RpbmcxNzA"),
    ("candle170mapping170", "Y2FuZGxlMTcwbWFwcGluZzE3MA"),
    ("candle170record170", "Y2FuZGxlMTcwcmVjb3JkMTcw"),
    ("thread170record170", "dGhyZWFkMTcwcmVjb3JkMTcw"),
    ("thread170candle170", "dGhyZWFkMTcwY2FuZGxlMTcw"),
    ("thread170thread170", "dGhyZWFkMTcwdGhyZWFkMTcw"),
    ("thread170kitten170", "dGhyZWFkMTcwa2l0dGVuMTcw"),
    (
        "round 170: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTcwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 170: agentuniverse is a framework for multi agents",
        "cm91bmQgMTcwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 170: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTcwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 170: the processor reads the record then stops",
        "cm91bmQgMTcwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 170: a worker pulls the next task from the queue",
        "cm91bmQgMTcwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 170: signals travel through the network layer",
        "cm91bmQgMTcwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 170: the gateway routes each request by policy",
        "cm91bmQgMTcwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 170: memory grows until the buffer is full",
        "cm91bmQgMTcwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 170: the cluster mirrors every packet twice",
        "cm91bmQgMTcwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 170: ranking uses tokens learned from the corpus",
        "cm91bmQgMTcwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 170: a long session ends when the candle dies",
        "cm91bmQgMTcwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 170: encode the prompt then map the result",
        "cm91bmQgMTcwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 170: the kernel wakes the worker at dawn",
        "cm91bmQgMTcwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 170: service latency drops after the patch",
        "cm91bmQgMTcwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 170: the library caches every vector it sees",
        "cm91bmQgMTcwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 170: agents argue then the debate resolves",
        "cm91bmQgMTcwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 170: the filter keeps only strong matches",
        "cm91bmQgMTcwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 170: the model answers with a short reply",
        "cm91bmQgMTcwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 170: the recorder stores the reasoning trace",
        "cm91bmQgMTcwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 170: the angel watches the processor run",
        "cm91bmQgMTcwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 170: angle of the vector decides the match",
        "cm91bmQgMTcwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 170: the candle burns twice as long at night",
        "cm91bmQgMTcwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 170: a mirror of the universe in one line",
        "cm91bmQgMTcwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 170: the queue drains before the storm", "cm91bmQgMTcwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
