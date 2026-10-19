"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten192kitten192", "a2l0dGVuMTkya2l0dGVuMTky"),
    ("kitten192sitting192", "a2l0dGVuMTkyc2l0dGluZzE5Mg"),
    ("kitten192agent192", "a2l0dGVuMTkyYWdlbnQxOTI"),
    ("kitten192angle192", "a2l0dGVuMTkyYW5nbGUxOTI"),
    ("sitting192angle192", "c2l0dGluZzE5MmFuZ2xlMTky"),
    ("sitting192universe192", "c2l0dGluZzE5MnVuaXZlcnNlMTky"),
    ("sitting192memory192", "c2l0dGluZzE5Mm1lbW9yeTE5Mg"),
    ("sitting192stream192", "c2l0dGluZzE5MnN0cmVhbTE5Mg"),
    ("agent192stream192", "YWdlbnQxOTJzdHJlYW0xOTI"),
    ("agent192context192", "YWdlbnQxOTJjb250ZXh0MTky"),
    ("agent192knowledge192", "YWdlbnQxOTJrbm93bGVkZ2UxOTI"),
    ("agent192vector192", "YWdlbnQxOTJ2ZWN0b3IxOTI"),
    ("angle192vector192", "YW5nbGUxOTJ2ZWN0b3IxOTI"),
    ("angle192processor192", "YW5nbGUxOTJwcm9jZXNzb3IxOTI"),
    ("angle192reasoning192", "YW5nbGUxOTJyZWFzb25pbmcxOTI"),
    ("angle192machine192", "YW5nbGUxOTJtYWNoaW5lMTky"),
    ("universe192machine192", "dW5pdmVyc2UxOTJtYWNoaW5lMTky"),
    ("universe192learning192", "dW5pdmVyc2UxOTJsZWFybmluZzE5Mg"),
    ("universe192model192", "dW5pdmVyc2UxOTJtb2RlbDE5Mg"),
    ("universe192token192", "dW5pdmVyc2UxOTJ0b2tlbjE5Mg"),
    ("memory192token192", "bWVtb3J5MTkydG9rZW4xOTI"),
    ("memory192prompt192", "bWVtb3J5MTkycHJvbXB0MTky"),
    ("memory192session192", "bWVtb3J5MTkyc2Vzc2lvbjE5Mg"),
    ("memory192library192", "bWVtb3J5MTkybGlicmFyeTE5Mg"),
    ("stream192library192", "c3RyZWFtMTkybGlicmFyeTE5Mg"),
    ("stream192service192", "c3RyZWFtMTkyc2VydmljZTE5Mg"),
    ("stream192gateway192", "c3RyZWFtMTkyZ2F0ZXdheTE5Mg"),
    ("stream192storage192", "c3RyZWFtMTkyc3RvcmFnZTE5Mg"),
    ("context192storage192", "Y29udGV4dDE5MnN0b3JhZ2UxOTI"),
    ("context192network192", "Y29udGV4dDE5Mm5ldHdvcmsxOTI"),
    ("context192latency192", "Y29udGV4dDE5MmxhdGVuY3kxOTI"),
    ("context192buffer192", "Y29udGV4dDE5MmJ1ZmZlcjE5Mg"),
    ("knowledge192buffer192", "a25vd2xlZGdlMTkyYnVmZmVyMTky"),
    ("knowledge192queue192", "a25vd2xlZGdlMTkycXVldWUxOTI"),
    ("knowledge192worker192", "a25vd2xlZGdlMTkyd29ya2VyMTky"),
    ("knowledge192kernel192", "a25vd2xlZGdlMTkya2VybmVsMTky"),
    ("vector192kernel192", "dmVjdG9yMTkya2VybmVsMTky"),
    ("vector192signal192", "dmVjdG9yMTkyc2lnbmFsMTky"),
    ("vector192packet192", "dmVjdG9yMTkycGFja2V0MTky"),
    ("vector192router192", "dmVjdG9yMTkycm91dGVyMTky"),
    ("processor192router192", "cHJvY2Vzc29yMTkycm91dGVyMTky"),
    ("processor192cluster192", "cHJvY2Vzc29yMTkyY2x1c3RlcjE5Mg"),
    ("processor192mirror192", "cHJvY2Vzc29yMTkybWlycm9yMTky"),
    ("processor192filter192", "cHJvY2Vzc29yMTkyZmlsdGVyMTky"),
    ("reasoning192filter192", "cmVhc29uaW5nMTkyZmlsdGVyMTky"),
    ("reasoning192ranking192", "cmVhc29uaW5nMTkycmFua2luZzE5Mg"),
    ("reasoning192encoding192", "cmVhc29uaW5nMTkyZW5jb2RpbmcxOTI"),
    ("reasoning192mapping192", "cmVhc29uaW5nMTkybWFwcGluZzE5Mg"),
    ("machine192mapping192", "bWFjaGluZTE5Mm1hcHBpbmcxOTI"),
    ("machine192record192", "bWFjaGluZTE5MnJlY29yZDE5Mg"),
    ("machine192candle192", "bWFjaGluZTE5MmNhbmRsZTE5Mg"),
    ("machine192thread192", "bWFjaGluZTE5MnRocmVhZDE5Mg"),
    ("learning192thread192", "bGVhcm5pbmcxOTJ0aHJlYWQxOTI"),
    ("learning192kitten192", "bGVhcm5pbmcxOTJraXR0ZW4xOTI"),
    ("learning192sitting192", "bGVhcm5pbmcxOTJzaXR0aW5nMTky"),
    ("learning192agent192", "bGVhcm5pbmcxOTJhZ2VudDE5Mg"),
    ("model192agent192", "bW9kZWwxOTJhZ2VudDE5Mg"),
    ("model192angle192", "bW9kZWwxOTJhbmdsZTE5Mg"),
    ("model192universe192", "bW9kZWwxOTJ1bml2ZXJzZTE5Mg"),
    ("model192memory192", "bW9kZWwxOTJtZW1vcnkxOTI"),
    ("token192memory192", "dG9rZW4xOTJtZW1vcnkxOTI"),
    ("token192stream192", "dG9rZW4xOTJzdHJlYW0xOTI"),
    ("token192context192", "dG9rZW4xOTJjb250ZXh0MTky"),
    ("token192knowledge192", "dG9rZW4xOTJrbm93bGVkZ2UxOTI"),
    ("prompt192knowledge192", "cHJvbXB0MTkya25vd2xlZGdlMTky"),
    ("prompt192vector192", "cHJvbXB0MTkydmVjdG9yMTky"),
    ("prompt192processor192", "cHJvbXB0MTkycHJvY2Vzc29yMTky"),
    ("prompt192reasoning192", "cHJvbXB0MTkycmVhc29uaW5nMTky"),
    ("session192reasoning192", "c2Vzc2lvbjE5MnJlYXNvbmluZzE5Mg"),
    ("session192machine192", "c2Vzc2lvbjE5Mm1hY2hpbmUxOTI"),
    ("session192learning192", "c2Vzc2lvbjE5MmxlYXJuaW5nMTky"),
    ("session192model192", "c2Vzc2lvbjE5Mm1vZGVsMTky"),
    ("library192model192", "bGlicmFyeTE5Mm1vZGVsMTky"),
    ("library192token192", "bGlicmFyeTE5MnRva2VuMTky"),
    ("library192prompt192", "bGlicmFyeTE5MnByb21wdDE5Mg"),
    ("library192session192", "bGlicmFyeTE5MnNlc3Npb24xOTI"),
    ("service192session192", "c2VydmljZTE5MnNlc3Npb24xOTI"),
    ("service192library192", "c2VydmljZTE5MmxpYnJhcnkxOTI"),
    ("service192service192", "c2VydmljZTE5MnNlcnZpY2UxOTI"),
    ("service192gateway192", "c2VydmljZTE5MmdhdGV3YXkxOTI"),
    ("gateway192gateway192", "Z2F0ZXdheTE5MmdhdGV3YXkxOTI"),
    ("gateway192storage192", "Z2F0ZXdheTE5MnN0b3JhZ2UxOTI"),
    ("gateway192network192", "Z2F0ZXdheTE5Mm5ldHdvcmsxOTI"),
    ("gateway192latency192", "Z2F0ZXdheTE5MmxhdGVuY3kxOTI"),
    ("storage192latency192", "c3RvcmFnZTE5MmxhdGVuY3kxOTI"),
    ("storage192buffer192", "c3RvcmFnZTE5MmJ1ZmZlcjE5Mg"),
    ("storage192queue192", "c3RvcmFnZTE5MnF1ZXVlMTky"),
    ("storage192worker192", "c3RvcmFnZTE5MndvcmtlcjE5Mg"),
    ("network192worker192", "bmV0d29yazE5MndvcmtlcjE5Mg"),
    ("network192kernel192", "bmV0d29yazE5Mmtlcm5lbDE5Mg"),
    ("network192signal192", "bmV0d29yazE5MnNpZ25hbDE5Mg"),
    ("network192packet192", "bmV0d29yazE5MnBhY2tldDE5Mg"),
    ("latency192packet192", "bGF0ZW5jeTE5MnBhY2tldDE5Mg"),
    ("latency192router192", "bGF0ZW5jeTE5MnJvdXRlcjE5Mg"),
    ("latency192cluster192", "bGF0ZW5jeTE5MmNsdXN0ZXIxOTI"),
    ("latency192mirror192", "bGF0ZW5jeTE5Mm1pcnJvcjE5Mg"),
    ("buffer192mirror192", "YnVmZmVyMTkybWlycm9yMTky"),
    ("buffer192filter192", "YnVmZmVyMTkyZmlsdGVyMTky"),
    ("buffer192ranking192", "YnVmZmVyMTkycmFua2luZzE5Mg"),
    ("buffer192encoding192", "YnVmZmVyMTkyZW5jb2RpbmcxOTI"),
    ("queue192encoding192", "cXVldWUxOTJlbmNvZGluZzE5Mg"),
    ("queue192mapping192", "cXVldWUxOTJtYXBwaW5nMTky"),
    ("queue192record192", "cXVldWUxOTJyZWNvcmQxOTI"),
    ("queue192candle192", "cXVldWUxOTJjYW5kbGUxOTI"),
    ("worker192candle192", "d29ya2VyMTkyY2FuZGxlMTky"),
    ("worker192thread192", "d29ya2VyMTkydGhyZWFkMTky"),
    ("worker192kitten192", "d29ya2VyMTkya2l0dGVuMTky"),
    ("worker192sitting192", "d29ya2VyMTkyc2l0dGluZzE5Mg"),
    ("kernel192sitting192", "a2VybmVsMTkyc2l0dGluZzE5Mg"),
    ("kernel192agent192", "a2VybmVsMTkyYWdlbnQxOTI"),
    ("kernel192angle192", "a2VybmVsMTkyYW5nbGUxOTI"),
    ("kernel192universe192", "a2VybmVsMTkydW5pdmVyc2UxOTI"),
    ("signal192universe192", "c2lnbmFsMTkydW5pdmVyc2UxOTI"),
    ("signal192memory192", "c2lnbmFsMTkybWVtb3J5MTky"),
    ("signal192stream192", "c2lnbmFsMTkyc3RyZWFtMTky"),
    ("signal192context192", "c2lnbmFsMTkyY29udGV4dDE5Mg"),
    ("packet192context192", "cGFja2V0MTkyY29udGV4dDE5Mg"),
    ("packet192knowledge192", "cGFja2V0MTkya25vd2xlZGdlMTky"),
    ("packet192vector192", "cGFja2V0MTkydmVjdG9yMTky"),
    ("packet192processor192", "cGFja2V0MTkycHJvY2Vzc29yMTky"),
    ("router192processor192", "cm91dGVyMTkycHJvY2Vzc29yMTky"),
    ("router192reasoning192", "cm91dGVyMTkycmVhc29uaW5nMTky"),
    ("router192machine192", "cm91dGVyMTkybWFjaGluZTE5Mg"),
    ("router192learning192", "cm91dGVyMTkybGVhcm5pbmcxOTI"),
    ("cluster192learning192", "Y2x1c3RlcjE5MmxlYXJuaW5nMTky"),
    ("cluster192model192", "Y2x1c3RlcjE5Mm1vZGVsMTky"),
    ("cluster192token192", "Y2x1c3RlcjE5MnRva2VuMTky"),
    ("cluster192prompt192", "Y2x1c3RlcjE5MnByb21wdDE5Mg"),
    ("mirror192prompt192", "bWlycm9yMTkycHJvbXB0MTky"),
    ("mirror192session192", "bWlycm9yMTkyc2Vzc2lvbjE5Mg"),
    ("mirror192library192", "bWlycm9yMTkybGlicmFyeTE5Mg"),
    ("mirror192service192", "bWlycm9yMTkyc2VydmljZTE5Mg"),
    ("filter192service192", "ZmlsdGVyMTkyc2VydmljZTE5Mg"),
    ("filter192gateway192", "ZmlsdGVyMTkyZ2F0ZXdheTE5Mg"),
    ("filter192storage192", "ZmlsdGVyMTkyc3RvcmFnZTE5Mg"),
    ("filter192network192", "ZmlsdGVyMTkybmV0d29yazE5Mg"),
    ("ranking192network192", "cmFua2luZzE5Mm5ldHdvcmsxOTI"),
    ("ranking192latency192", "cmFua2luZzE5MmxhdGVuY3kxOTI"),
    ("ranking192buffer192", "cmFua2luZzE5MmJ1ZmZlcjE5Mg"),
    ("ranking192queue192", "cmFua2luZzE5MnF1ZXVlMTky"),
    ("encoding192queue192", "ZW5jb2RpbmcxOTJxdWV1ZTE5Mg"),
    ("encoding192worker192", "ZW5jb2RpbmcxOTJ3b3JrZXIxOTI"),
    ("encoding192kernel192", "ZW5jb2RpbmcxOTJrZXJuZWwxOTI"),
    ("encoding192signal192", "ZW5jb2RpbmcxOTJzaWduYWwxOTI"),
    ("mapping192signal192", "bWFwcGluZzE5MnNpZ25hbDE5Mg"),
    ("mapping192packet192", "bWFwcGluZzE5MnBhY2tldDE5Mg"),
    ("mapping192router192", "bWFwcGluZzE5MnJvdXRlcjE5Mg"),
    ("mapping192cluster192", "bWFwcGluZzE5MmNsdXN0ZXIxOTI"),
    ("record192cluster192", "cmVjb3JkMTkyY2x1c3RlcjE5Mg"),
    ("record192mirror192", "cmVjb3JkMTkybWlycm9yMTky"),
    ("record192filter192", "cmVjb3JkMTkyZmlsdGVyMTky"),
    ("record192ranking192", "cmVjb3JkMTkycmFua2luZzE5Mg"),
    ("candle192ranking192", "Y2FuZGxlMTkycmFua2luZzE5Mg"),
    ("candle192encoding192", "Y2FuZGxlMTkyZW5jb2RpbmcxOTI"),
    ("candle192mapping192", "Y2FuZGxlMTkybWFwcGluZzE5Mg"),
    ("candle192record192", "Y2FuZGxlMTkycmVjb3JkMTky"),
    ("thread192record192", "dGhyZWFkMTkycmVjb3JkMTky"),
    ("thread192candle192", "dGhyZWFkMTkyY2FuZGxlMTky"),
    ("thread192thread192", "dGhyZWFkMTkydGhyZWFkMTky"),
    ("thread192kitten192", "dGhyZWFkMTkya2l0dGVuMTky"),
    (
        "round 192: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTkyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 192: agentuniverse is a framework for multi agents",
        "cm91bmQgMTkyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 192: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTkyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 192: the processor reads the record then stops",
        "cm91bmQgMTkyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 192: a worker pulls the next task from the queue",
        "cm91bmQgMTkyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 192: signals travel through the network layer",
        "cm91bmQgMTkyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 192: the gateway routes each request by policy",
        "cm91bmQgMTkyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 192: memory grows until the buffer is full",
        "cm91bmQgMTkyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 192: the cluster mirrors every packet twice",
        "cm91bmQgMTkyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 192: ranking uses tokens learned from the corpus",
        "cm91bmQgMTkyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 192: a long session ends when the candle dies",
        "cm91bmQgMTkyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 192: encode the prompt then map the result",
        "cm91bmQgMTkyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 192: the kernel wakes the worker at dawn",
        "cm91bmQgMTkyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 192: service latency drops after the patch",
        "cm91bmQgMTkyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 192: the library caches every vector it sees",
        "cm91bmQgMTkyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 192: agents argue then the debate resolves",
        "cm91bmQgMTkyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 192: the filter keeps only strong matches",
        "cm91bmQgMTkyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 192: the model answers with a short reply",
        "cm91bmQgMTkyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 192: the recorder stores the reasoning trace",
        "cm91bmQgMTkyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 192: the angel watches the processor run",
        "cm91bmQgMTkyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 192: angle of the vector decides the match",
        "cm91bmQgMTkyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 192: the candle burns twice as long at night",
        "cm91bmQgMTkyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 192: a mirror of the universe in one line",
        "cm91bmQgMTkyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 192: the queue drains before the storm", "cm91bmQgMTkyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
