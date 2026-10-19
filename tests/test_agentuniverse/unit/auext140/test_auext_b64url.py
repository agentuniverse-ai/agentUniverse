"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten140kitten140", "a2l0dGVuMTQwa2l0dGVuMTQw"),
    ("kitten140sitting140", "a2l0dGVuMTQwc2l0dGluZzE0MA"),
    ("kitten140agent140", "a2l0dGVuMTQwYWdlbnQxNDA"),
    ("kitten140angle140", "a2l0dGVuMTQwYW5nbGUxNDA"),
    ("sitting140angle140", "c2l0dGluZzE0MGFuZ2xlMTQw"),
    ("sitting140universe140", "c2l0dGluZzE0MHVuaXZlcnNlMTQw"),
    ("sitting140memory140", "c2l0dGluZzE0MG1lbW9yeTE0MA"),
    ("sitting140stream140", "c2l0dGluZzE0MHN0cmVhbTE0MA"),
    ("agent140stream140", "YWdlbnQxNDBzdHJlYW0xNDA"),
    ("agent140context140", "YWdlbnQxNDBjb250ZXh0MTQw"),
    ("agent140knowledge140", "YWdlbnQxNDBrbm93bGVkZ2UxNDA"),
    ("agent140vector140", "YWdlbnQxNDB2ZWN0b3IxNDA"),
    ("angle140vector140", "YW5nbGUxNDB2ZWN0b3IxNDA"),
    ("angle140processor140", "YW5nbGUxNDBwcm9jZXNzb3IxNDA"),
    ("angle140reasoning140", "YW5nbGUxNDByZWFzb25pbmcxNDA"),
    ("angle140machine140", "YW5nbGUxNDBtYWNoaW5lMTQw"),
    ("universe140machine140", "dW5pdmVyc2UxNDBtYWNoaW5lMTQw"),
    ("universe140learning140", "dW5pdmVyc2UxNDBsZWFybmluZzE0MA"),
    ("universe140model140", "dW5pdmVyc2UxNDBtb2RlbDE0MA"),
    ("universe140token140", "dW5pdmVyc2UxNDB0b2tlbjE0MA"),
    ("memory140token140", "bWVtb3J5MTQwdG9rZW4xNDA"),
    ("memory140prompt140", "bWVtb3J5MTQwcHJvbXB0MTQw"),
    ("memory140session140", "bWVtb3J5MTQwc2Vzc2lvbjE0MA"),
    ("memory140library140", "bWVtb3J5MTQwbGlicmFyeTE0MA"),
    ("stream140library140", "c3RyZWFtMTQwbGlicmFyeTE0MA"),
    ("stream140service140", "c3RyZWFtMTQwc2VydmljZTE0MA"),
    ("stream140gateway140", "c3RyZWFtMTQwZ2F0ZXdheTE0MA"),
    ("stream140storage140", "c3RyZWFtMTQwc3RvcmFnZTE0MA"),
    ("context140storage140", "Y29udGV4dDE0MHN0b3JhZ2UxNDA"),
    ("context140network140", "Y29udGV4dDE0MG5ldHdvcmsxNDA"),
    ("context140latency140", "Y29udGV4dDE0MGxhdGVuY3kxNDA"),
    ("context140buffer140", "Y29udGV4dDE0MGJ1ZmZlcjE0MA"),
    ("knowledge140buffer140", "a25vd2xlZGdlMTQwYnVmZmVyMTQw"),
    ("knowledge140queue140", "a25vd2xlZGdlMTQwcXVldWUxNDA"),
    ("knowledge140worker140", "a25vd2xlZGdlMTQwd29ya2VyMTQw"),
    ("knowledge140kernel140", "a25vd2xlZGdlMTQwa2VybmVsMTQw"),
    ("vector140kernel140", "dmVjdG9yMTQwa2VybmVsMTQw"),
    ("vector140signal140", "dmVjdG9yMTQwc2lnbmFsMTQw"),
    ("vector140packet140", "dmVjdG9yMTQwcGFja2V0MTQw"),
    ("vector140router140", "dmVjdG9yMTQwcm91dGVyMTQw"),
    ("processor140router140", "cHJvY2Vzc29yMTQwcm91dGVyMTQw"),
    ("processor140cluster140", "cHJvY2Vzc29yMTQwY2x1c3RlcjE0MA"),
    ("processor140mirror140", "cHJvY2Vzc29yMTQwbWlycm9yMTQw"),
    ("processor140filter140", "cHJvY2Vzc29yMTQwZmlsdGVyMTQw"),
    ("reasoning140filter140", "cmVhc29uaW5nMTQwZmlsdGVyMTQw"),
    ("reasoning140ranking140", "cmVhc29uaW5nMTQwcmFua2luZzE0MA"),
    ("reasoning140encoding140", "cmVhc29uaW5nMTQwZW5jb2RpbmcxNDA"),
    ("reasoning140mapping140", "cmVhc29uaW5nMTQwbWFwcGluZzE0MA"),
    ("machine140mapping140", "bWFjaGluZTE0MG1hcHBpbmcxNDA"),
    ("machine140record140", "bWFjaGluZTE0MHJlY29yZDE0MA"),
    ("machine140candle140", "bWFjaGluZTE0MGNhbmRsZTE0MA"),
    ("machine140thread140", "bWFjaGluZTE0MHRocmVhZDE0MA"),
    ("learning140thread140", "bGVhcm5pbmcxNDB0aHJlYWQxNDA"),
    ("learning140kitten140", "bGVhcm5pbmcxNDBraXR0ZW4xNDA"),
    ("learning140sitting140", "bGVhcm5pbmcxNDBzaXR0aW5nMTQw"),
    ("learning140agent140", "bGVhcm5pbmcxNDBhZ2VudDE0MA"),
    ("model140agent140", "bW9kZWwxNDBhZ2VudDE0MA"),
    ("model140angle140", "bW9kZWwxNDBhbmdsZTE0MA"),
    ("model140universe140", "bW9kZWwxNDB1bml2ZXJzZTE0MA"),
    ("model140memory140", "bW9kZWwxNDBtZW1vcnkxNDA"),
    ("token140memory140", "dG9rZW4xNDBtZW1vcnkxNDA"),
    ("token140stream140", "dG9rZW4xNDBzdHJlYW0xNDA"),
    ("token140context140", "dG9rZW4xNDBjb250ZXh0MTQw"),
    ("token140knowledge140", "dG9rZW4xNDBrbm93bGVkZ2UxNDA"),
    ("prompt140knowledge140", "cHJvbXB0MTQwa25vd2xlZGdlMTQw"),
    ("prompt140vector140", "cHJvbXB0MTQwdmVjdG9yMTQw"),
    ("prompt140processor140", "cHJvbXB0MTQwcHJvY2Vzc29yMTQw"),
    ("prompt140reasoning140", "cHJvbXB0MTQwcmVhc29uaW5nMTQw"),
    ("session140reasoning140", "c2Vzc2lvbjE0MHJlYXNvbmluZzE0MA"),
    ("session140machine140", "c2Vzc2lvbjE0MG1hY2hpbmUxNDA"),
    ("session140learning140", "c2Vzc2lvbjE0MGxlYXJuaW5nMTQw"),
    ("session140model140", "c2Vzc2lvbjE0MG1vZGVsMTQw"),
    ("library140model140", "bGlicmFyeTE0MG1vZGVsMTQw"),
    ("library140token140", "bGlicmFyeTE0MHRva2VuMTQw"),
    ("library140prompt140", "bGlicmFyeTE0MHByb21wdDE0MA"),
    ("library140session140", "bGlicmFyeTE0MHNlc3Npb24xNDA"),
    ("service140session140", "c2VydmljZTE0MHNlc3Npb24xNDA"),
    ("service140library140", "c2VydmljZTE0MGxpYnJhcnkxNDA"),
    ("service140service140", "c2VydmljZTE0MHNlcnZpY2UxNDA"),
    ("service140gateway140", "c2VydmljZTE0MGdhdGV3YXkxNDA"),
    ("gateway140gateway140", "Z2F0ZXdheTE0MGdhdGV3YXkxNDA"),
    ("gateway140storage140", "Z2F0ZXdheTE0MHN0b3JhZ2UxNDA"),
    ("gateway140network140", "Z2F0ZXdheTE0MG5ldHdvcmsxNDA"),
    ("gateway140latency140", "Z2F0ZXdheTE0MGxhdGVuY3kxNDA"),
    ("storage140latency140", "c3RvcmFnZTE0MGxhdGVuY3kxNDA"),
    ("storage140buffer140", "c3RvcmFnZTE0MGJ1ZmZlcjE0MA"),
    ("storage140queue140", "c3RvcmFnZTE0MHF1ZXVlMTQw"),
    ("storage140worker140", "c3RvcmFnZTE0MHdvcmtlcjE0MA"),
    ("network140worker140", "bmV0d29yazE0MHdvcmtlcjE0MA"),
    ("network140kernel140", "bmV0d29yazE0MGtlcm5lbDE0MA"),
    ("network140signal140", "bmV0d29yazE0MHNpZ25hbDE0MA"),
    ("network140packet140", "bmV0d29yazE0MHBhY2tldDE0MA"),
    ("latency140packet140", "bGF0ZW5jeTE0MHBhY2tldDE0MA"),
    ("latency140router140", "bGF0ZW5jeTE0MHJvdXRlcjE0MA"),
    ("latency140cluster140", "bGF0ZW5jeTE0MGNsdXN0ZXIxNDA"),
    ("latency140mirror140", "bGF0ZW5jeTE0MG1pcnJvcjE0MA"),
    ("buffer140mirror140", "YnVmZmVyMTQwbWlycm9yMTQw"),
    ("buffer140filter140", "YnVmZmVyMTQwZmlsdGVyMTQw"),
    ("buffer140ranking140", "YnVmZmVyMTQwcmFua2luZzE0MA"),
    ("buffer140encoding140", "YnVmZmVyMTQwZW5jb2RpbmcxNDA"),
    ("queue140encoding140", "cXVldWUxNDBlbmNvZGluZzE0MA"),
    ("queue140mapping140", "cXVldWUxNDBtYXBwaW5nMTQw"),
    ("queue140record140", "cXVldWUxNDByZWNvcmQxNDA"),
    ("queue140candle140", "cXVldWUxNDBjYW5kbGUxNDA"),
    ("worker140candle140", "d29ya2VyMTQwY2FuZGxlMTQw"),
    ("worker140thread140", "d29ya2VyMTQwdGhyZWFkMTQw"),
    ("worker140kitten140", "d29ya2VyMTQwa2l0dGVuMTQw"),
    ("worker140sitting140", "d29ya2VyMTQwc2l0dGluZzE0MA"),
    ("kernel140sitting140", "a2VybmVsMTQwc2l0dGluZzE0MA"),
    ("kernel140agent140", "a2VybmVsMTQwYWdlbnQxNDA"),
    ("kernel140angle140", "a2VybmVsMTQwYW5nbGUxNDA"),
    ("kernel140universe140", "a2VybmVsMTQwdW5pdmVyc2UxNDA"),
    ("signal140universe140", "c2lnbmFsMTQwdW5pdmVyc2UxNDA"),
    ("signal140memory140", "c2lnbmFsMTQwbWVtb3J5MTQw"),
    ("signal140stream140", "c2lnbmFsMTQwc3RyZWFtMTQw"),
    ("signal140context140", "c2lnbmFsMTQwY29udGV4dDE0MA"),
    ("packet140context140", "cGFja2V0MTQwY29udGV4dDE0MA"),
    ("packet140knowledge140", "cGFja2V0MTQwa25vd2xlZGdlMTQw"),
    ("packet140vector140", "cGFja2V0MTQwdmVjdG9yMTQw"),
    ("packet140processor140", "cGFja2V0MTQwcHJvY2Vzc29yMTQw"),
    ("router140processor140", "cm91dGVyMTQwcHJvY2Vzc29yMTQw"),
    ("router140reasoning140", "cm91dGVyMTQwcmVhc29uaW5nMTQw"),
    ("router140machine140", "cm91dGVyMTQwbWFjaGluZTE0MA"),
    ("router140learning140", "cm91dGVyMTQwbGVhcm5pbmcxNDA"),
    ("cluster140learning140", "Y2x1c3RlcjE0MGxlYXJuaW5nMTQw"),
    ("cluster140model140", "Y2x1c3RlcjE0MG1vZGVsMTQw"),
    ("cluster140token140", "Y2x1c3RlcjE0MHRva2VuMTQw"),
    ("cluster140prompt140", "Y2x1c3RlcjE0MHByb21wdDE0MA"),
    ("mirror140prompt140", "bWlycm9yMTQwcHJvbXB0MTQw"),
    ("mirror140session140", "bWlycm9yMTQwc2Vzc2lvbjE0MA"),
    ("mirror140library140", "bWlycm9yMTQwbGlicmFyeTE0MA"),
    ("mirror140service140", "bWlycm9yMTQwc2VydmljZTE0MA"),
    ("filter140service140", "ZmlsdGVyMTQwc2VydmljZTE0MA"),
    ("filter140gateway140", "ZmlsdGVyMTQwZ2F0ZXdheTE0MA"),
    ("filter140storage140", "ZmlsdGVyMTQwc3RvcmFnZTE0MA"),
    ("filter140network140", "ZmlsdGVyMTQwbmV0d29yazE0MA"),
    ("ranking140network140", "cmFua2luZzE0MG5ldHdvcmsxNDA"),
    ("ranking140latency140", "cmFua2luZzE0MGxhdGVuY3kxNDA"),
    ("ranking140buffer140", "cmFua2luZzE0MGJ1ZmZlcjE0MA"),
    ("ranking140queue140", "cmFua2luZzE0MHF1ZXVlMTQw"),
    ("encoding140queue140", "ZW5jb2RpbmcxNDBxdWV1ZTE0MA"),
    ("encoding140worker140", "ZW5jb2RpbmcxNDB3b3JrZXIxNDA"),
    ("encoding140kernel140", "ZW5jb2RpbmcxNDBrZXJuZWwxNDA"),
    ("encoding140signal140", "ZW5jb2RpbmcxNDBzaWduYWwxNDA"),
    ("mapping140signal140", "bWFwcGluZzE0MHNpZ25hbDE0MA"),
    ("mapping140packet140", "bWFwcGluZzE0MHBhY2tldDE0MA"),
    ("mapping140router140", "bWFwcGluZzE0MHJvdXRlcjE0MA"),
    ("mapping140cluster140", "bWFwcGluZzE0MGNsdXN0ZXIxNDA"),
    ("record140cluster140", "cmVjb3JkMTQwY2x1c3RlcjE0MA"),
    ("record140mirror140", "cmVjb3JkMTQwbWlycm9yMTQw"),
    ("record140filter140", "cmVjb3JkMTQwZmlsdGVyMTQw"),
    ("record140ranking140", "cmVjb3JkMTQwcmFua2luZzE0MA"),
    ("candle140ranking140", "Y2FuZGxlMTQwcmFua2luZzE0MA"),
    ("candle140encoding140", "Y2FuZGxlMTQwZW5jb2RpbmcxNDA"),
    ("candle140mapping140", "Y2FuZGxlMTQwbWFwcGluZzE0MA"),
    ("candle140record140", "Y2FuZGxlMTQwcmVjb3JkMTQw"),
    ("thread140record140", "dGhyZWFkMTQwcmVjb3JkMTQw"),
    ("thread140candle140", "dGhyZWFkMTQwY2FuZGxlMTQw"),
    ("thread140thread140", "dGhyZWFkMTQwdGhyZWFkMTQw"),
    ("thread140kitten140", "dGhyZWFkMTQwa2l0dGVuMTQw"),
    (
        "round 140: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTQwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 140: agentuniverse is a framework for multi agents",
        "cm91bmQgMTQwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 140: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTQwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 140: the processor reads the record then stops",
        "cm91bmQgMTQwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 140: a worker pulls the next task from the queue",
        "cm91bmQgMTQwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 140: signals travel through the network layer",
        "cm91bmQgMTQwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 140: the gateway routes each request by policy",
        "cm91bmQgMTQwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 140: memory grows until the buffer is full",
        "cm91bmQgMTQwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 140: the cluster mirrors every packet twice",
        "cm91bmQgMTQwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 140: ranking uses tokens learned from the corpus",
        "cm91bmQgMTQwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 140: a long session ends when the candle dies",
        "cm91bmQgMTQwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 140: encode the prompt then map the result",
        "cm91bmQgMTQwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 140: the kernel wakes the worker at dawn",
        "cm91bmQgMTQwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 140: service latency drops after the patch",
        "cm91bmQgMTQwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 140: the library caches every vector it sees",
        "cm91bmQgMTQwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 140: agents argue then the debate resolves",
        "cm91bmQgMTQwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 140: the filter keeps only strong matches",
        "cm91bmQgMTQwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 140: the model answers with a short reply",
        "cm91bmQgMTQwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 140: the recorder stores the reasoning trace",
        "cm91bmQgMTQwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 140: the angel watches the processor run",
        "cm91bmQgMTQwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 140: angle of the vector decides the match",
        "cm91bmQgMTQwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 140: the candle burns twice as long at night",
        "cm91bmQgMTQwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 140: a mirror of the universe in one line",
        "cm91bmQgMTQwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 140: the queue drains before the storm", "cm91bmQgMTQwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
