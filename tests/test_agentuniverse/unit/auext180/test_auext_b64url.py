"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten180kitten180", "a2l0dGVuMTgwa2l0dGVuMTgw"),
    ("kitten180sitting180", "a2l0dGVuMTgwc2l0dGluZzE4MA"),
    ("kitten180agent180", "a2l0dGVuMTgwYWdlbnQxODA"),
    ("kitten180angle180", "a2l0dGVuMTgwYW5nbGUxODA"),
    ("sitting180angle180", "c2l0dGluZzE4MGFuZ2xlMTgw"),
    ("sitting180universe180", "c2l0dGluZzE4MHVuaXZlcnNlMTgw"),
    ("sitting180memory180", "c2l0dGluZzE4MG1lbW9yeTE4MA"),
    ("sitting180stream180", "c2l0dGluZzE4MHN0cmVhbTE4MA"),
    ("agent180stream180", "YWdlbnQxODBzdHJlYW0xODA"),
    ("agent180context180", "YWdlbnQxODBjb250ZXh0MTgw"),
    ("agent180knowledge180", "YWdlbnQxODBrbm93bGVkZ2UxODA"),
    ("agent180vector180", "YWdlbnQxODB2ZWN0b3IxODA"),
    ("angle180vector180", "YW5nbGUxODB2ZWN0b3IxODA"),
    ("angle180processor180", "YW5nbGUxODBwcm9jZXNzb3IxODA"),
    ("angle180reasoning180", "YW5nbGUxODByZWFzb25pbmcxODA"),
    ("angle180machine180", "YW5nbGUxODBtYWNoaW5lMTgw"),
    ("universe180machine180", "dW5pdmVyc2UxODBtYWNoaW5lMTgw"),
    ("universe180learning180", "dW5pdmVyc2UxODBsZWFybmluZzE4MA"),
    ("universe180model180", "dW5pdmVyc2UxODBtb2RlbDE4MA"),
    ("universe180token180", "dW5pdmVyc2UxODB0b2tlbjE4MA"),
    ("memory180token180", "bWVtb3J5MTgwdG9rZW4xODA"),
    ("memory180prompt180", "bWVtb3J5MTgwcHJvbXB0MTgw"),
    ("memory180session180", "bWVtb3J5MTgwc2Vzc2lvbjE4MA"),
    ("memory180library180", "bWVtb3J5MTgwbGlicmFyeTE4MA"),
    ("stream180library180", "c3RyZWFtMTgwbGlicmFyeTE4MA"),
    ("stream180service180", "c3RyZWFtMTgwc2VydmljZTE4MA"),
    ("stream180gateway180", "c3RyZWFtMTgwZ2F0ZXdheTE4MA"),
    ("stream180storage180", "c3RyZWFtMTgwc3RvcmFnZTE4MA"),
    ("context180storage180", "Y29udGV4dDE4MHN0b3JhZ2UxODA"),
    ("context180network180", "Y29udGV4dDE4MG5ldHdvcmsxODA"),
    ("context180latency180", "Y29udGV4dDE4MGxhdGVuY3kxODA"),
    ("context180buffer180", "Y29udGV4dDE4MGJ1ZmZlcjE4MA"),
    ("knowledge180buffer180", "a25vd2xlZGdlMTgwYnVmZmVyMTgw"),
    ("knowledge180queue180", "a25vd2xlZGdlMTgwcXVldWUxODA"),
    ("knowledge180worker180", "a25vd2xlZGdlMTgwd29ya2VyMTgw"),
    ("knowledge180kernel180", "a25vd2xlZGdlMTgwa2VybmVsMTgw"),
    ("vector180kernel180", "dmVjdG9yMTgwa2VybmVsMTgw"),
    ("vector180signal180", "dmVjdG9yMTgwc2lnbmFsMTgw"),
    ("vector180packet180", "dmVjdG9yMTgwcGFja2V0MTgw"),
    ("vector180router180", "dmVjdG9yMTgwcm91dGVyMTgw"),
    ("processor180router180", "cHJvY2Vzc29yMTgwcm91dGVyMTgw"),
    ("processor180cluster180", "cHJvY2Vzc29yMTgwY2x1c3RlcjE4MA"),
    ("processor180mirror180", "cHJvY2Vzc29yMTgwbWlycm9yMTgw"),
    ("processor180filter180", "cHJvY2Vzc29yMTgwZmlsdGVyMTgw"),
    ("reasoning180filter180", "cmVhc29uaW5nMTgwZmlsdGVyMTgw"),
    ("reasoning180ranking180", "cmVhc29uaW5nMTgwcmFua2luZzE4MA"),
    ("reasoning180encoding180", "cmVhc29uaW5nMTgwZW5jb2RpbmcxODA"),
    ("reasoning180mapping180", "cmVhc29uaW5nMTgwbWFwcGluZzE4MA"),
    ("machine180mapping180", "bWFjaGluZTE4MG1hcHBpbmcxODA"),
    ("machine180record180", "bWFjaGluZTE4MHJlY29yZDE4MA"),
    ("machine180candle180", "bWFjaGluZTE4MGNhbmRsZTE4MA"),
    ("machine180thread180", "bWFjaGluZTE4MHRocmVhZDE4MA"),
    ("learning180thread180", "bGVhcm5pbmcxODB0aHJlYWQxODA"),
    ("learning180kitten180", "bGVhcm5pbmcxODBraXR0ZW4xODA"),
    ("learning180sitting180", "bGVhcm5pbmcxODBzaXR0aW5nMTgw"),
    ("learning180agent180", "bGVhcm5pbmcxODBhZ2VudDE4MA"),
    ("model180agent180", "bW9kZWwxODBhZ2VudDE4MA"),
    ("model180angle180", "bW9kZWwxODBhbmdsZTE4MA"),
    ("model180universe180", "bW9kZWwxODB1bml2ZXJzZTE4MA"),
    ("model180memory180", "bW9kZWwxODBtZW1vcnkxODA"),
    ("token180memory180", "dG9rZW4xODBtZW1vcnkxODA"),
    ("token180stream180", "dG9rZW4xODBzdHJlYW0xODA"),
    ("token180context180", "dG9rZW4xODBjb250ZXh0MTgw"),
    ("token180knowledge180", "dG9rZW4xODBrbm93bGVkZ2UxODA"),
    ("prompt180knowledge180", "cHJvbXB0MTgwa25vd2xlZGdlMTgw"),
    ("prompt180vector180", "cHJvbXB0MTgwdmVjdG9yMTgw"),
    ("prompt180processor180", "cHJvbXB0MTgwcHJvY2Vzc29yMTgw"),
    ("prompt180reasoning180", "cHJvbXB0MTgwcmVhc29uaW5nMTgw"),
    ("session180reasoning180", "c2Vzc2lvbjE4MHJlYXNvbmluZzE4MA"),
    ("session180machine180", "c2Vzc2lvbjE4MG1hY2hpbmUxODA"),
    ("session180learning180", "c2Vzc2lvbjE4MGxlYXJuaW5nMTgw"),
    ("session180model180", "c2Vzc2lvbjE4MG1vZGVsMTgw"),
    ("library180model180", "bGlicmFyeTE4MG1vZGVsMTgw"),
    ("library180token180", "bGlicmFyeTE4MHRva2VuMTgw"),
    ("library180prompt180", "bGlicmFyeTE4MHByb21wdDE4MA"),
    ("library180session180", "bGlicmFyeTE4MHNlc3Npb24xODA"),
    ("service180session180", "c2VydmljZTE4MHNlc3Npb24xODA"),
    ("service180library180", "c2VydmljZTE4MGxpYnJhcnkxODA"),
    ("service180service180", "c2VydmljZTE4MHNlcnZpY2UxODA"),
    ("service180gateway180", "c2VydmljZTE4MGdhdGV3YXkxODA"),
    ("gateway180gateway180", "Z2F0ZXdheTE4MGdhdGV3YXkxODA"),
    ("gateway180storage180", "Z2F0ZXdheTE4MHN0b3JhZ2UxODA"),
    ("gateway180network180", "Z2F0ZXdheTE4MG5ldHdvcmsxODA"),
    ("gateway180latency180", "Z2F0ZXdheTE4MGxhdGVuY3kxODA"),
    ("storage180latency180", "c3RvcmFnZTE4MGxhdGVuY3kxODA"),
    ("storage180buffer180", "c3RvcmFnZTE4MGJ1ZmZlcjE4MA"),
    ("storage180queue180", "c3RvcmFnZTE4MHF1ZXVlMTgw"),
    ("storage180worker180", "c3RvcmFnZTE4MHdvcmtlcjE4MA"),
    ("network180worker180", "bmV0d29yazE4MHdvcmtlcjE4MA"),
    ("network180kernel180", "bmV0d29yazE4MGtlcm5lbDE4MA"),
    ("network180signal180", "bmV0d29yazE4MHNpZ25hbDE4MA"),
    ("network180packet180", "bmV0d29yazE4MHBhY2tldDE4MA"),
    ("latency180packet180", "bGF0ZW5jeTE4MHBhY2tldDE4MA"),
    ("latency180router180", "bGF0ZW5jeTE4MHJvdXRlcjE4MA"),
    ("latency180cluster180", "bGF0ZW5jeTE4MGNsdXN0ZXIxODA"),
    ("latency180mirror180", "bGF0ZW5jeTE4MG1pcnJvcjE4MA"),
    ("buffer180mirror180", "YnVmZmVyMTgwbWlycm9yMTgw"),
    ("buffer180filter180", "YnVmZmVyMTgwZmlsdGVyMTgw"),
    ("buffer180ranking180", "YnVmZmVyMTgwcmFua2luZzE4MA"),
    ("buffer180encoding180", "YnVmZmVyMTgwZW5jb2RpbmcxODA"),
    ("queue180encoding180", "cXVldWUxODBlbmNvZGluZzE4MA"),
    ("queue180mapping180", "cXVldWUxODBtYXBwaW5nMTgw"),
    ("queue180record180", "cXVldWUxODByZWNvcmQxODA"),
    ("queue180candle180", "cXVldWUxODBjYW5kbGUxODA"),
    ("worker180candle180", "d29ya2VyMTgwY2FuZGxlMTgw"),
    ("worker180thread180", "d29ya2VyMTgwdGhyZWFkMTgw"),
    ("worker180kitten180", "d29ya2VyMTgwa2l0dGVuMTgw"),
    ("worker180sitting180", "d29ya2VyMTgwc2l0dGluZzE4MA"),
    ("kernel180sitting180", "a2VybmVsMTgwc2l0dGluZzE4MA"),
    ("kernel180agent180", "a2VybmVsMTgwYWdlbnQxODA"),
    ("kernel180angle180", "a2VybmVsMTgwYW5nbGUxODA"),
    ("kernel180universe180", "a2VybmVsMTgwdW5pdmVyc2UxODA"),
    ("signal180universe180", "c2lnbmFsMTgwdW5pdmVyc2UxODA"),
    ("signal180memory180", "c2lnbmFsMTgwbWVtb3J5MTgw"),
    ("signal180stream180", "c2lnbmFsMTgwc3RyZWFtMTgw"),
    ("signal180context180", "c2lnbmFsMTgwY29udGV4dDE4MA"),
    ("packet180context180", "cGFja2V0MTgwY29udGV4dDE4MA"),
    ("packet180knowledge180", "cGFja2V0MTgwa25vd2xlZGdlMTgw"),
    ("packet180vector180", "cGFja2V0MTgwdmVjdG9yMTgw"),
    ("packet180processor180", "cGFja2V0MTgwcHJvY2Vzc29yMTgw"),
    ("router180processor180", "cm91dGVyMTgwcHJvY2Vzc29yMTgw"),
    ("router180reasoning180", "cm91dGVyMTgwcmVhc29uaW5nMTgw"),
    ("router180machine180", "cm91dGVyMTgwbWFjaGluZTE4MA"),
    ("router180learning180", "cm91dGVyMTgwbGVhcm5pbmcxODA"),
    ("cluster180learning180", "Y2x1c3RlcjE4MGxlYXJuaW5nMTgw"),
    ("cluster180model180", "Y2x1c3RlcjE4MG1vZGVsMTgw"),
    ("cluster180token180", "Y2x1c3RlcjE4MHRva2VuMTgw"),
    ("cluster180prompt180", "Y2x1c3RlcjE4MHByb21wdDE4MA"),
    ("mirror180prompt180", "bWlycm9yMTgwcHJvbXB0MTgw"),
    ("mirror180session180", "bWlycm9yMTgwc2Vzc2lvbjE4MA"),
    ("mirror180library180", "bWlycm9yMTgwbGlicmFyeTE4MA"),
    ("mirror180service180", "bWlycm9yMTgwc2VydmljZTE4MA"),
    ("filter180service180", "ZmlsdGVyMTgwc2VydmljZTE4MA"),
    ("filter180gateway180", "ZmlsdGVyMTgwZ2F0ZXdheTE4MA"),
    ("filter180storage180", "ZmlsdGVyMTgwc3RvcmFnZTE4MA"),
    ("filter180network180", "ZmlsdGVyMTgwbmV0d29yazE4MA"),
    ("ranking180network180", "cmFua2luZzE4MG5ldHdvcmsxODA"),
    ("ranking180latency180", "cmFua2luZzE4MGxhdGVuY3kxODA"),
    ("ranking180buffer180", "cmFua2luZzE4MGJ1ZmZlcjE4MA"),
    ("ranking180queue180", "cmFua2luZzE4MHF1ZXVlMTgw"),
    ("encoding180queue180", "ZW5jb2RpbmcxODBxdWV1ZTE4MA"),
    ("encoding180worker180", "ZW5jb2RpbmcxODB3b3JrZXIxODA"),
    ("encoding180kernel180", "ZW5jb2RpbmcxODBrZXJuZWwxODA"),
    ("encoding180signal180", "ZW5jb2RpbmcxODBzaWduYWwxODA"),
    ("mapping180signal180", "bWFwcGluZzE4MHNpZ25hbDE4MA"),
    ("mapping180packet180", "bWFwcGluZzE4MHBhY2tldDE4MA"),
    ("mapping180router180", "bWFwcGluZzE4MHJvdXRlcjE4MA"),
    ("mapping180cluster180", "bWFwcGluZzE4MGNsdXN0ZXIxODA"),
    ("record180cluster180", "cmVjb3JkMTgwY2x1c3RlcjE4MA"),
    ("record180mirror180", "cmVjb3JkMTgwbWlycm9yMTgw"),
    ("record180filter180", "cmVjb3JkMTgwZmlsdGVyMTgw"),
    ("record180ranking180", "cmVjb3JkMTgwcmFua2luZzE4MA"),
    ("candle180ranking180", "Y2FuZGxlMTgwcmFua2luZzE4MA"),
    ("candle180encoding180", "Y2FuZGxlMTgwZW5jb2RpbmcxODA"),
    ("candle180mapping180", "Y2FuZGxlMTgwbWFwcGluZzE4MA"),
    ("candle180record180", "Y2FuZGxlMTgwcmVjb3JkMTgw"),
    ("thread180record180", "dGhyZWFkMTgwcmVjb3JkMTgw"),
    ("thread180candle180", "dGhyZWFkMTgwY2FuZGxlMTgw"),
    ("thread180thread180", "dGhyZWFkMTgwdGhyZWFkMTgw"),
    ("thread180kitten180", "dGhyZWFkMTgwa2l0dGVuMTgw"),
    (
        "round 180: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTgwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 180: agentuniverse is a framework for multi agents",
        "cm91bmQgMTgwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 180: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTgwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 180: the processor reads the record then stops",
        "cm91bmQgMTgwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 180: a worker pulls the next task from the queue",
        "cm91bmQgMTgwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 180: signals travel through the network layer",
        "cm91bmQgMTgwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 180: the gateway routes each request by policy",
        "cm91bmQgMTgwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 180: memory grows until the buffer is full",
        "cm91bmQgMTgwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 180: the cluster mirrors every packet twice",
        "cm91bmQgMTgwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 180: ranking uses tokens learned from the corpus",
        "cm91bmQgMTgwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 180: a long session ends when the candle dies",
        "cm91bmQgMTgwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 180: encode the prompt then map the result",
        "cm91bmQgMTgwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 180: the kernel wakes the worker at dawn",
        "cm91bmQgMTgwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 180: service latency drops after the patch",
        "cm91bmQgMTgwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 180: the library caches every vector it sees",
        "cm91bmQgMTgwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 180: agents argue then the debate resolves",
        "cm91bmQgMTgwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 180: the filter keeps only strong matches",
        "cm91bmQgMTgwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 180: the model answers with a short reply",
        "cm91bmQgMTgwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 180: the recorder stores the reasoning trace",
        "cm91bmQgMTgwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 180: the angel watches the processor run",
        "cm91bmQgMTgwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 180: angle of the vector decides the match",
        "cm91bmQgMTgwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 180: the candle burns twice as long at night",
        "cm91bmQgMTgwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 180: a mirror of the universe in one line",
        "cm91bmQgMTgwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 180: the queue drains before the storm", "cm91bmQgMTgwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
