"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten182kitten182", "a2l0dGVuMTgya2l0dGVuMTgy"),
    ("kitten182sitting182", "a2l0dGVuMTgyc2l0dGluZzE4Mg"),
    ("kitten182agent182", "a2l0dGVuMTgyYWdlbnQxODI"),
    ("kitten182angle182", "a2l0dGVuMTgyYW5nbGUxODI"),
    ("sitting182angle182", "c2l0dGluZzE4MmFuZ2xlMTgy"),
    ("sitting182universe182", "c2l0dGluZzE4MnVuaXZlcnNlMTgy"),
    ("sitting182memory182", "c2l0dGluZzE4Mm1lbW9yeTE4Mg"),
    ("sitting182stream182", "c2l0dGluZzE4MnN0cmVhbTE4Mg"),
    ("agent182stream182", "YWdlbnQxODJzdHJlYW0xODI"),
    ("agent182context182", "YWdlbnQxODJjb250ZXh0MTgy"),
    ("agent182knowledge182", "YWdlbnQxODJrbm93bGVkZ2UxODI"),
    ("agent182vector182", "YWdlbnQxODJ2ZWN0b3IxODI"),
    ("angle182vector182", "YW5nbGUxODJ2ZWN0b3IxODI"),
    ("angle182processor182", "YW5nbGUxODJwcm9jZXNzb3IxODI"),
    ("angle182reasoning182", "YW5nbGUxODJyZWFzb25pbmcxODI"),
    ("angle182machine182", "YW5nbGUxODJtYWNoaW5lMTgy"),
    ("universe182machine182", "dW5pdmVyc2UxODJtYWNoaW5lMTgy"),
    ("universe182learning182", "dW5pdmVyc2UxODJsZWFybmluZzE4Mg"),
    ("universe182model182", "dW5pdmVyc2UxODJtb2RlbDE4Mg"),
    ("universe182token182", "dW5pdmVyc2UxODJ0b2tlbjE4Mg"),
    ("memory182token182", "bWVtb3J5MTgydG9rZW4xODI"),
    ("memory182prompt182", "bWVtb3J5MTgycHJvbXB0MTgy"),
    ("memory182session182", "bWVtb3J5MTgyc2Vzc2lvbjE4Mg"),
    ("memory182library182", "bWVtb3J5MTgybGlicmFyeTE4Mg"),
    ("stream182library182", "c3RyZWFtMTgybGlicmFyeTE4Mg"),
    ("stream182service182", "c3RyZWFtMTgyc2VydmljZTE4Mg"),
    ("stream182gateway182", "c3RyZWFtMTgyZ2F0ZXdheTE4Mg"),
    ("stream182storage182", "c3RyZWFtMTgyc3RvcmFnZTE4Mg"),
    ("context182storage182", "Y29udGV4dDE4MnN0b3JhZ2UxODI"),
    ("context182network182", "Y29udGV4dDE4Mm5ldHdvcmsxODI"),
    ("context182latency182", "Y29udGV4dDE4MmxhdGVuY3kxODI"),
    ("context182buffer182", "Y29udGV4dDE4MmJ1ZmZlcjE4Mg"),
    ("knowledge182buffer182", "a25vd2xlZGdlMTgyYnVmZmVyMTgy"),
    ("knowledge182queue182", "a25vd2xlZGdlMTgycXVldWUxODI"),
    ("knowledge182worker182", "a25vd2xlZGdlMTgyd29ya2VyMTgy"),
    ("knowledge182kernel182", "a25vd2xlZGdlMTgya2VybmVsMTgy"),
    ("vector182kernel182", "dmVjdG9yMTgya2VybmVsMTgy"),
    ("vector182signal182", "dmVjdG9yMTgyc2lnbmFsMTgy"),
    ("vector182packet182", "dmVjdG9yMTgycGFja2V0MTgy"),
    ("vector182router182", "dmVjdG9yMTgycm91dGVyMTgy"),
    ("processor182router182", "cHJvY2Vzc29yMTgycm91dGVyMTgy"),
    ("processor182cluster182", "cHJvY2Vzc29yMTgyY2x1c3RlcjE4Mg"),
    ("processor182mirror182", "cHJvY2Vzc29yMTgybWlycm9yMTgy"),
    ("processor182filter182", "cHJvY2Vzc29yMTgyZmlsdGVyMTgy"),
    ("reasoning182filter182", "cmVhc29uaW5nMTgyZmlsdGVyMTgy"),
    ("reasoning182ranking182", "cmVhc29uaW5nMTgycmFua2luZzE4Mg"),
    ("reasoning182encoding182", "cmVhc29uaW5nMTgyZW5jb2RpbmcxODI"),
    ("reasoning182mapping182", "cmVhc29uaW5nMTgybWFwcGluZzE4Mg"),
    ("machine182mapping182", "bWFjaGluZTE4Mm1hcHBpbmcxODI"),
    ("machine182record182", "bWFjaGluZTE4MnJlY29yZDE4Mg"),
    ("machine182candle182", "bWFjaGluZTE4MmNhbmRsZTE4Mg"),
    ("machine182thread182", "bWFjaGluZTE4MnRocmVhZDE4Mg"),
    ("learning182thread182", "bGVhcm5pbmcxODJ0aHJlYWQxODI"),
    ("learning182kitten182", "bGVhcm5pbmcxODJraXR0ZW4xODI"),
    ("learning182sitting182", "bGVhcm5pbmcxODJzaXR0aW5nMTgy"),
    ("learning182agent182", "bGVhcm5pbmcxODJhZ2VudDE4Mg"),
    ("model182agent182", "bW9kZWwxODJhZ2VudDE4Mg"),
    ("model182angle182", "bW9kZWwxODJhbmdsZTE4Mg"),
    ("model182universe182", "bW9kZWwxODJ1bml2ZXJzZTE4Mg"),
    ("model182memory182", "bW9kZWwxODJtZW1vcnkxODI"),
    ("token182memory182", "dG9rZW4xODJtZW1vcnkxODI"),
    ("token182stream182", "dG9rZW4xODJzdHJlYW0xODI"),
    ("token182context182", "dG9rZW4xODJjb250ZXh0MTgy"),
    ("token182knowledge182", "dG9rZW4xODJrbm93bGVkZ2UxODI"),
    ("prompt182knowledge182", "cHJvbXB0MTgya25vd2xlZGdlMTgy"),
    ("prompt182vector182", "cHJvbXB0MTgydmVjdG9yMTgy"),
    ("prompt182processor182", "cHJvbXB0MTgycHJvY2Vzc29yMTgy"),
    ("prompt182reasoning182", "cHJvbXB0MTgycmVhc29uaW5nMTgy"),
    ("session182reasoning182", "c2Vzc2lvbjE4MnJlYXNvbmluZzE4Mg"),
    ("session182machine182", "c2Vzc2lvbjE4Mm1hY2hpbmUxODI"),
    ("session182learning182", "c2Vzc2lvbjE4MmxlYXJuaW5nMTgy"),
    ("session182model182", "c2Vzc2lvbjE4Mm1vZGVsMTgy"),
    ("library182model182", "bGlicmFyeTE4Mm1vZGVsMTgy"),
    ("library182token182", "bGlicmFyeTE4MnRva2VuMTgy"),
    ("library182prompt182", "bGlicmFyeTE4MnByb21wdDE4Mg"),
    ("library182session182", "bGlicmFyeTE4MnNlc3Npb24xODI"),
    ("service182session182", "c2VydmljZTE4MnNlc3Npb24xODI"),
    ("service182library182", "c2VydmljZTE4MmxpYnJhcnkxODI"),
    ("service182service182", "c2VydmljZTE4MnNlcnZpY2UxODI"),
    ("service182gateway182", "c2VydmljZTE4MmdhdGV3YXkxODI"),
    ("gateway182gateway182", "Z2F0ZXdheTE4MmdhdGV3YXkxODI"),
    ("gateway182storage182", "Z2F0ZXdheTE4MnN0b3JhZ2UxODI"),
    ("gateway182network182", "Z2F0ZXdheTE4Mm5ldHdvcmsxODI"),
    ("gateway182latency182", "Z2F0ZXdheTE4MmxhdGVuY3kxODI"),
    ("storage182latency182", "c3RvcmFnZTE4MmxhdGVuY3kxODI"),
    ("storage182buffer182", "c3RvcmFnZTE4MmJ1ZmZlcjE4Mg"),
    ("storage182queue182", "c3RvcmFnZTE4MnF1ZXVlMTgy"),
    ("storage182worker182", "c3RvcmFnZTE4MndvcmtlcjE4Mg"),
    ("network182worker182", "bmV0d29yazE4MndvcmtlcjE4Mg"),
    ("network182kernel182", "bmV0d29yazE4Mmtlcm5lbDE4Mg"),
    ("network182signal182", "bmV0d29yazE4MnNpZ25hbDE4Mg"),
    ("network182packet182", "bmV0d29yazE4MnBhY2tldDE4Mg"),
    ("latency182packet182", "bGF0ZW5jeTE4MnBhY2tldDE4Mg"),
    ("latency182router182", "bGF0ZW5jeTE4MnJvdXRlcjE4Mg"),
    ("latency182cluster182", "bGF0ZW5jeTE4MmNsdXN0ZXIxODI"),
    ("latency182mirror182", "bGF0ZW5jeTE4Mm1pcnJvcjE4Mg"),
    ("buffer182mirror182", "YnVmZmVyMTgybWlycm9yMTgy"),
    ("buffer182filter182", "YnVmZmVyMTgyZmlsdGVyMTgy"),
    ("buffer182ranking182", "YnVmZmVyMTgycmFua2luZzE4Mg"),
    ("buffer182encoding182", "YnVmZmVyMTgyZW5jb2RpbmcxODI"),
    ("queue182encoding182", "cXVldWUxODJlbmNvZGluZzE4Mg"),
    ("queue182mapping182", "cXVldWUxODJtYXBwaW5nMTgy"),
    ("queue182record182", "cXVldWUxODJyZWNvcmQxODI"),
    ("queue182candle182", "cXVldWUxODJjYW5kbGUxODI"),
    ("worker182candle182", "d29ya2VyMTgyY2FuZGxlMTgy"),
    ("worker182thread182", "d29ya2VyMTgydGhyZWFkMTgy"),
    ("worker182kitten182", "d29ya2VyMTgya2l0dGVuMTgy"),
    ("worker182sitting182", "d29ya2VyMTgyc2l0dGluZzE4Mg"),
    ("kernel182sitting182", "a2VybmVsMTgyc2l0dGluZzE4Mg"),
    ("kernel182agent182", "a2VybmVsMTgyYWdlbnQxODI"),
    ("kernel182angle182", "a2VybmVsMTgyYW5nbGUxODI"),
    ("kernel182universe182", "a2VybmVsMTgydW5pdmVyc2UxODI"),
    ("signal182universe182", "c2lnbmFsMTgydW5pdmVyc2UxODI"),
    ("signal182memory182", "c2lnbmFsMTgybWVtb3J5MTgy"),
    ("signal182stream182", "c2lnbmFsMTgyc3RyZWFtMTgy"),
    ("signal182context182", "c2lnbmFsMTgyY29udGV4dDE4Mg"),
    ("packet182context182", "cGFja2V0MTgyY29udGV4dDE4Mg"),
    ("packet182knowledge182", "cGFja2V0MTgya25vd2xlZGdlMTgy"),
    ("packet182vector182", "cGFja2V0MTgydmVjdG9yMTgy"),
    ("packet182processor182", "cGFja2V0MTgycHJvY2Vzc29yMTgy"),
    ("router182processor182", "cm91dGVyMTgycHJvY2Vzc29yMTgy"),
    ("router182reasoning182", "cm91dGVyMTgycmVhc29uaW5nMTgy"),
    ("router182machine182", "cm91dGVyMTgybWFjaGluZTE4Mg"),
    ("router182learning182", "cm91dGVyMTgybGVhcm5pbmcxODI"),
    ("cluster182learning182", "Y2x1c3RlcjE4MmxlYXJuaW5nMTgy"),
    ("cluster182model182", "Y2x1c3RlcjE4Mm1vZGVsMTgy"),
    ("cluster182token182", "Y2x1c3RlcjE4MnRva2VuMTgy"),
    ("cluster182prompt182", "Y2x1c3RlcjE4MnByb21wdDE4Mg"),
    ("mirror182prompt182", "bWlycm9yMTgycHJvbXB0MTgy"),
    ("mirror182session182", "bWlycm9yMTgyc2Vzc2lvbjE4Mg"),
    ("mirror182library182", "bWlycm9yMTgybGlicmFyeTE4Mg"),
    ("mirror182service182", "bWlycm9yMTgyc2VydmljZTE4Mg"),
    ("filter182service182", "ZmlsdGVyMTgyc2VydmljZTE4Mg"),
    ("filter182gateway182", "ZmlsdGVyMTgyZ2F0ZXdheTE4Mg"),
    ("filter182storage182", "ZmlsdGVyMTgyc3RvcmFnZTE4Mg"),
    ("filter182network182", "ZmlsdGVyMTgybmV0d29yazE4Mg"),
    ("ranking182network182", "cmFua2luZzE4Mm5ldHdvcmsxODI"),
    ("ranking182latency182", "cmFua2luZzE4MmxhdGVuY3kxODI"),
    ("ranking182buffer182", "cmFua2luZzE4MmJ1ZmZlcjE4Mg"),
    ("ranking182queue182", "cmFua2luZzE4MnF1ZXVlMTgy"),
    ("encoding182queue182", "ZW5jb2RpbmcxODJxdWV1ZTE4Mg"),
    ("encoding182worker182", "ZW5jb2RpbmcxODJ3b3JrZXIxODI"),
    ("encoding182kernel182", "ZW5jb2RpbmcxODJrZXJuZWwxODI"),
    ("encoding182signal182", "ZW5jb2RpbmcxODJzaWduYWwxODI"),
    ("mapping182signal182", "bWFwcGluZzE4MnNpZ25hbDE4Mg"),
    ("mapping182packet182", "bWFwcGluZzE4MnBhY2tldDE4Mg"),
    ("mapping182router182", "bWFwcGluZzE4MnJvdXRlcjE4Mg"),
    ("mapping182cluster182", "bWFwcGluZzE4MmNsdXN0ZXIxODI"),
    ("record182cluster182", "cmVjb3JkMTgyY2x1c3RlcjE4Mg"),
    ("record182mirror182", "cmVjb3JkMTgybWlycm9yMTgy"),
    ("record182filter182", "cmVjb3JkMTgyZmlsdGVyMTgy"),
    ("record182ranking182", "cmVjb3JkMTgycmFua2luZzE4Mg"),
    ("candle182ranking182", "Y2FuZGxlMTgycmFua2luZzE4Mg"),
    ("candle182encoding182", "Y2FuZGxlMTgyZW5jb2RpbmcxODI"),
    ("candle182mapping182", "Y2FuZGxlMTgybWFwcGluZzE4Mg"),
    ("candle182record182", "Y2FuZGxlMTgycmVjb3JkMTgy"),
    ("thread182record182", "dGhyZWFkMTgycmVjb3JkMTgy"),
    ("thread182candle182", "dGhyZWFkMTgyY2FuZGxlMTgy"),
    ("thread182thread182", "dGhyZWFkMTgydGhyZWFkMTgy"),
    ("thread182kitten182", "dGhyZWFkMTgya2l0dGVuMTgy"),
    (
        "round 182: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTgyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 182: agentuniverse is a framework for multi agents",
        "cm91bmQgMTgyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 182: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTgyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 182: the processor reads the record then stops",
        "cm91bmQgMTgyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 182: a worker pulls the next task from the queue",
        "cm91bmQgMTgyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 182: signals travel through the network layer",
        "cm91bmQgMTgyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 182: the gateway routes each request by policy",
        "cm91bmQgMTgyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 182: memory grows until the buffer is full",
        "cm91bmQgMTgyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 182: the cluster mirrors every packet twice",
        "cm91bmQgMTgyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 182: ranking uses tokens learned from the corpus",
        "cm91bmQgMTgyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 182: a long session ends when the candle dies",
        "cm91bmQgMTgyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 182: encode the prompt then map the result",
        "cm91bmQgMTgyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 182: the kernel wakes the worker at dawn",
        "cm91bmQgMTgyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 182: service latency drops after the patch",
        "cm91bmQgMTgyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 182: the library caches every vector it sees",
        "cm91bmQgMTgyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 182: agents argue then the debate resolves",
        "cm91bmQgMTgyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 182: the filter keeps only strong matches",
        "cm91bmQgMTgyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 182: the model answers with a short reply",
        "cm91bmQgMTgyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 182: the recorder stores the reasoning trace",
        "cm91bmQgMTgyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 182: the angel watches the processor run",
        "cm91bmQgMTgyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 182: angle of the vector decides the match",
        "cm91bmQgMTgyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 182: the candle burns twice as long at night",
        "cm91bmQgMTgyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 182: a mirror of the universe in one line",
        "cm91bmQgMTgyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 182: the queue drains before the storm", "cm91bmQgMTgyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
