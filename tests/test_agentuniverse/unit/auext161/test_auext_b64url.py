"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten161kitten161", "a2l0dGVuMTYxa2l0dGVuMTYx"),
    ("kitten161sitting161", "a2l0dGVuMTYxc2l0dGluZzE2MQ"),
    ("kitten161agent161", "a2l0dGVuMTYxYWdlbnQxNjE"),
    ("kitten161angle161", "a2l0dGVuMTYxYW5nbGUxNjE"),
    ("sitting161angle161", "c2l0dGluZzE2MWFuZ2xlMTYx"),
    ("sitting161universe161", "c2l0dGluZzE2MXVuaXZlcnNlMTYx"),
    ("sitting161memory161", "c2l0dGluZzE2MW1lbW9yeTE2MQ"),
    ("sitting161stream161", "c2l0dGluZzE2MXN0cmVhbTE2MQ"),
    ("agent161stream161", "YWdlbnQxNjFzdHJlYW0xNjE"),
    ("agent161context161", "YWdlbnQxNjFjb250ZXh0MTYx"),
    ("agent161knowledge161", "YWdlbnQxNjFrbm93bGVkZ2UxNjE"),
    ("agent161vector161", "YWdlbnQxNjF2ZWN0b3IxNjE"),
    ("angle161vector161", "YW5nbGUxNjF2ZWN0b3IxNjE"),
    ("angle161processor161", "YW5nbGUxNjFwcm9jZXNzb3IxNjE"),
    ("angle161reasoning161", "YW5nbGUxNjFyZWFzb25pbmcxNjE"),
    ("angle161machine161", "YW5nbGUxNjFtYWNoaW5lMTYx"),
    ("universe161machine161", "dW5pdmVyc2UxNjFtYWNoaW5lMTYx"),
    ("universe161learning161", "dW5pdmVyc2UxNjFsZWFybmluZzE2MQ"),
    ("universe161model161", "dW5pdmVyc2UxNjFtb2RlbDE2MQ"),
    ("universe161token161", "dW5pdmVyc2UxNjF0b2tlbjE2MQ"),
    ("memory161token161", "bWVtb3J5MTYxdG9rZW4xNjE"),
    ("memory161prompt161", "bWVtb3J5MTYxcHJvbXB0MTYx"),
    ("memory161session161", "bWVtb3J5MTYxc2Vzc2lvbjE2MQ"),
    ("memory161library161", "bWVtb3J5MTYxbGlicmFyeTE2MQ"),
    ("stream161library161", "c3RyZWFtMTYxbGlicmFyeTE2MQ"),
    ("stream161service161", "c3RyZWFtMTYxc2VydmljZTE2MQ"),
    ("stream161gateway161", "c3RyZWFtMTYxZ2F0ZXdheTE2MQ"),
    ("stream161storage161", "c3RyZWFtMTYxc3RvcmFnZTE2MQ"),
    ("context161storage161", "Y29udGV4dDE2MXN0b3JhZ2UxNjE"),
    ("context161network161", "Y29udGV4dDE2MW5ldHdvcmsxNjE"),
    ("context161latency161", "Y29udGV4dDE2MWxhdGVuY3kxNjE"),
    ("context161buffer161", "Y29udGV4dDE2MWJ1ZmZlcjE2MQ"),
    ("knowledge161buffer161", "a25vd2xlZGdlMTYxYnVmZmVyMTYx"),
    ("knowledge161queue161", "a25vd2xlZGdlMTYxcXVldWUxNjE"),
    ("knowledge161worker161", "a25vd2xlZGdlMTYxd29ya2VyMTYx"),
    ("knowledge161kernel161", "a25vd2xlZGdlMTYxa2VybmVsMTYx"),
    ("vector161kernel161", "dmVjdG9yMTYxa2VybmVsMTYx"),
    ("vector161signal161", "dmVjdG9yMTYxc2lnbmFsMTYx"),
    ("vector161packet161", "dmVjdG9yMTYxcGFja2V0MTYx"),
    ("vector161router161", "dmVjdG9yMTYxcm91dGVyMTYx"),
    ("processor161router161", "cHJvY2Vzc29yMTYxcm91dGVyMTYx"),
    ("processor161cluster161", "cHJvY2Vzc29yMTYxY2x1c3RlcjE2MQ"),
    ("processor161mirror161", "cHJvY2Vzc29yMTYxbWlycm9yMTYx"),
    ("processor161filter161", "cHJvY2Vzc29yMTYxZmlsdGVyMTYx"),
    ("reasoning161filter161", "cmVhc29uaW5nMTYxZmlsdGVyMTYx"),
    ("reasoning161ranking161", "cmVhc29uaW5nMTYxcmFua2luZzE2MQ"),
    ("reasoning161encoding161", "cmVhc29uaW5nMTYxZW5jb2RpbmcxNjE"),
    ("reasoning161mapping161", "cmVhc29uaW5nMTYxbWFwcGluZzE2MQ"),
    ("machine161mapping161", "bWFjaGluZTE2MW1hcHBpbmcxNjE"),
    ("machine161record161", "bWFjaGluZTE2MXJlY29yZDE2MQ"),
    ("machine161candle161", "bWFjaGluZTE2MWNhbmRsZTE2MQ"),
    ("machine161thread161", "bWFjaGluZTE2MXRocmVhZDE2MQ"),
    ("learning161thread161", "bGVhcm5pbmcxNjF0aHJlYWQxNjE"),
    ("learning161kitten161", "bGVhcm5pbmcxNjFraXR0ZW4xNjE"),
    ("learning161sitting161", "bGVhcm5pbmcxNjFzaXR0aW5nMTYx"),
    ("learning161agent161", "bGVhcm5pbmcxNjFhZ2VudDE2MQ"),
    ("model161agent161", "bW9kZWwxNjFhZ2VudDE2MQ"),
    ("model161angle161", "bW9kZWwxNjFhbmdsZTE2MQ"),
    ("model161universe161", "bW9kZWwxNjF1bml2ZXJzZTE2MQ"),
    ("model161memory161", "bW9kZWwxNjFtZW1vcnkxNjE"),
    ("token161memory161", "dG9rZW4xNjFtZW1vcnkxNjE"),
    ("token161stream161", "dG9rZW4xNjFzdHJlYW0xNjE"),
    ("token161context161", "dG9rZW4xNjFjb250ZXh0MTYx"),
    ("token161knowledge161", "dG9rZW4xNjFrbm93bGVkZ2UxNjE"),
    ("prompt161knowledge161", "cHJvbXB0MTYxa25vd2xlZGdlMTYx"),
    ("prompt161vector161", "cHJvbXB0MTYxdmVjdG9yMTYx"),
    ("prompt161processor161", "cHJvbXB0MTYxcHJvY2Vzc29yMTYx"),
    ("prompt161reasoning161", "cHJvbXB0MTYxcmVhc29uaW5nMTYx"),
    ("session161reasoning161", "c2Vzc2lvbjE2MXJlYXNvbmluZzE2MQ"),
    ("session161machine161", "c2Vzc2lvbjE2MW1hY2hpbmUxNjE"),
    ("session161learning161", "c2Vzc2lvbjE2MWxlYXJuaW5nMTYx"),
    ("session161model161", "c2Vzc2lvbjE2MW1vZGVsMTYx"),
    ("library161model161", "bGlicmFyeTE2MW1vZGVsMTYx"),
    ("library161token161", "bGlicmFyeTE2MXRva2VuMTYx"),
    ("library161prompt161", "bGlicmFyeTE2MXByb21wdDE2MQ"),
    ("library161session161", "bGlicmFyeTE2MXNlc3Npb24xNjE"),
    ("service161session161", "c2VydmljZTE2MXNlc3Npb24xNjE"),
    ("service161library161", "c2VydmljZTE2MWxpYnJhcnkxNjE"),
    ("service161service161", "c2VydmljZTE2MXNlcnZpY2UxNjE"),
    ("service161gateway161", "c2VydmljZTE2MWdhdGV3YXkxNjE"),
    ("gateway161gateway161", "Z2F0ZXdheTE2MWdhdGV3YXkxNjE"),
    ("gateway161storage161", "Z2F0ZXdheTE2MXN0b3JhZ2UxNjE"),
    ("gateway161network161", "Z2F0ZXdheTE2MW5ldHdvcmsxNjE"),
    ("gateway161latency161", "Z2F0ZXdheTE2MWxhdGVuY3kxNjE"),
    ("storage161latency161", "c3RvcmFnZTE2MWxhdGVuY3kxNjE"),
    ("storage161buffer161", "c3RvcmFnZTE2MWJ1ZmZlcjE2MQ"),
    ("storage161queue161", "c3RvcmFnZTE2MXF1ZXVlMTYx"),
    ("storage161worker161", "c3RvcmFnZTE2MXdvcmtlcjE2MQ"),
    ("network161worker161", "bmV0d29yazE2MXdvcmtlcjE2MQ"),
    ("network161kernel161", "bmV0d29yazE2MWtlcm5lbDE2MQ"),
    ("network161signal161", "bmV0d29yazE2MXNpZ25hbDE2MQ"),
    ("network161packet161", "bmV0d29yazE2MXBhY2tldDE2MQ"),
    ("latency161packet161", "bGF0ZW5jeTE2MXBhY2tldDE2MQ"),
    ("latency161router161", "bGF0ZW5jeTE2MXJvdXRlcjE2MQ"),
    ("latency161cluster161", "bGF0ZW5jeTE2MWNsdXN0ZXIxNjE"),
    ("latency161mirror161", "bGF0ZW5jeTE2MW1pcnJvcjE2MQ"),
    ("buffer161mirror161", "YnVmZmVyMTYxbWlycm9yMTYx"),
    ("buffer161filter161", "YnVmZmVyMTYxZmlsdGVyMTYx"),
    ("buffer161ranking161", "YnVmZmVyMTYxcmFua2luZzE2MQ"),
    ("buffer161encoding161", "YnVmZmVyMTYxZW5jb2RpbmcxNjE"),
    ("queue161encoding161", "cXVldWUxNjFlbmNvZGluZzE2MQ"),
    ("queue161mapping161", "cXVldWUxNjFtYXBwaW5nMTYx"),
    ("queue161record161", "cXVldWUxNjFyZWNvcmQxNjE"),
    ("queue161candle161", "cXVldWUxNjFjYW5kbGUxNjE"),
    ("worker161candle161", "d29ya2VyMTYxY2FuZGxlMTYx"),
    ("worker161thread161", "d29ya2VyMTYxdGhyZWFkMTYx"),
    ("worker161kitten161", "d29ya2VyMTYxa2l0dGVuMTYx"),
    ("worker161sitting161", "d29ya2VyMTYxc2l0dGluZzE2MQ"),
    ("kernel161sitting161", "a2VybmVsMTYxc2l0dGluZzE2MQ"),
    ("kernel161agent161", "a2VybmVsMTYxYWdlbnQxNjE"),
    ("kernel161angle161", "a2VybmVsMTYxYW5nbGUxNjE"),
    ("kernel161universe161", "a2VybmVsMTYxdW5pdmVyc2UxNjE"),
    ("signal161universe161", "c2lnbmFsMTYxdW5pdmVyc2UxNjE"),
    ("signal161memory161", "c2lnbmFsMTYxbWVtb3J5MTYx"),
    ("signal161stream161", "c2lnbmFsMTYxc3RyZWFtMTYx"),
    ("signal161context161", "c2lnbmFsMTYxY29udGV4dDE2MQ"),
    ("packet161context161", "cGFja2V0MTYxY29udGV4dDE2MQ"),
    ("packet161knowledge161", "cGFja2V0MTYxa25vd2xlZGdlMTYx"),
    ("packet161vector161", "cGFja2V0MTYxdmVjdG9yMTYx"),
    ("packet161processor161", "cGFja2V0MTYxcHJvY2Vzc29yMTYx"),
    ("router161processor161", "cm91dGVyMTYxcHJvY2Vzc29yMTYx"),
    ("router161reasoning161", "cm91dGVyMTYxcmVhc29uaW5nMTYx"),
    ("router161machine161", "cm91dGVyMTYxbWFjaGluZTE2MQ"),
    ("router161learning161", "cm91dGVyMTYxbGVhcm5pbmcxNjE"),
    ("cluster161learning161", "Y2x1c3RlcjE2MWxlYXJuaW5nMTYx"),
    ("cluster161model161", "Y2x1c3RlcjE2MW1vZGVsMTYx"),
    ("cluster161token161", "Y2x1c3RlcjE2MXRva2VuMTYx"),
    ("cluster161prompt161", "Y2x1c3RlcjE2MXByb21wdDE2MQ"),
    ("mirror161prompt161", "bWlycm9yMTYxcHJvbXB0MTYx"),
    ("mirror161session161", "bWlycm9yMTYxc2Vzc2lvbjE2MQ"),
    ("mirror161library161", "bWlycm9yMTYxbGlicmFyeTE2MQ"),
    ("mirror161service161", "bWlycm9yMTYxc2VydmljZTE2MQ"),
    ("filter161service161", "ZmlsdGVyMTYxc2VydmljZTE2MQ"),
    ("filter161gateway161", "ZmlsdGVyMTYxZ2F0ZXdheTE2MQ"),
    ("filter161storage161", "ZmlsdGVyMTYxc3RvcmFnZTE2MQ"),
    ("filter161network161", "ZmlsdGVyMTYxbmV0d29yazE2MQ"),
    ("ranking161network161", "cmFua2luZzE2MW5ldHdvcmsxNjE"),
    ("ranking161latency161", "cmFua2luZzE2MWxhdGVuY3kxNjE"),
    ("ranking161buffer161", "cmFua2luZzE2MWJ1ZmZlcjE2MQ"),
    ("ranking161queue161", "cmFua2luZzE2MXF1ZXVlMTYx"),
    ("encoding161queue161", "ZW5jb2RpbmcxNjFxdWV1ZTE2MQ"),
    ("encoding161worker161", "ZW5jb2RpbmcxNjF3b3JrZXIxNjE"),
    ("encoding161kernel161", "ZW5jb2RpbmcxNjFrZXJuZWwxNjE"),
    ("encoding161signal161", "ZW5jb2RpbmcxNjFzaWduYWwxNjE"),
    ("mapping161signal161", "bWFwcGluZzE2MXNpZ25hbDE2MQ"),
    ("mapping161packet161", "bWFwcGluZzE2MXBhY2tldDE2MQ"),
    ("mapping161router161", "bWFwcGluZzE2MXJvdXRlcjE2MQ"),
    ("mapping161cluster161", "bWFwcGluZzE2MWNsdXN0ZXIxNjE"),
    ("record161cluster161", "cmVjb3JkMTYxY2x1c3RlcjE2MQ"),
    ("record161mirror161", "cmVjb3JkMTYxbWlycm9yMTYx"),
    ("record161filter161", "cmVjb3JkMTYxZmlsdGVyMTYx"),
    ("record161ranking161", "cmVjb3JkMTYxcmFua2luZzE2MQ"),
    ("candle161ranking161", "Y2FuZGxlMTYxcmFua2luZzE2MQ"),
    ("candle161encoding161", "Y2FuZGxlMTYxZW5jb2RpbmcxNjE"),
    ("candle161mapping161", "Y2FuZGxlMTYxbWFwcGluZzE2MQ"),
    ("candle161record161", "Y2FuZGxlMTYxcmVjb3JkMTYx"),
    ("thread161record161", "dGhyZWFkMTYxcmVjb3JkMTYx"),
    ("thread161candle161", "dGhyZWFkMTYxY2FuZGxlMTYx"),
    ("thread161thread161", "dGhyZWFkMTYxdGhyZWFkMTYx"),
    ("thread161kitten161", "dGhyZWFkMTYxa2l0dGVuMTYx"),
    (
        "round 161: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTYxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 161: agentuniverse is a framework for multi agents",
        "cm91bmQgMTYxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 161: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTYxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 161: the processor reads the record then stops",
        "cm91bmQgMTYxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 161: a worker pulls the next task from the queue",
        "cm91bmQgMTYxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 161: signals travel through the network layer",
        "cm91bmQgMTYxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 161: the gateway routes each request by policy",
        "cm91bmQgMTYxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 161: memory grows until the buffer is full",
        "cm91bmQgMTYxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 161: the cluster mirrors every packet twice",
        "cm91bmQgMTYxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 161: ranking uses tokens learned from the corpus",
        "cm91bmQgMTYxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 161: a long session ends when the candle dies",
        "cm91bmQgMTYxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 161: encode the prompt then map the result",
        "cm91bmQgMTYxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 161: the kernel wakes the worker at dawn",
        "cm91bmQgMTYxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 161: service latency drops after the patch",
        "cm91bmQgMTYxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 161: the library caches every vector it sees",
        "cm91bmQgMTYxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 161: agents argue then the debate resolves",
        "cm91bmQgMTYxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 161: the filter keeps only strong matches",
        "cm91bmQgMTYxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 161: the model answers with a short reply",
        "cm91bmQgMTYxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 161: the recorder stores the reasoning trace",
        "cm91bmQgMTYxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 161: the angel watches the processor run",
        "cm91bmQgMTYxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 161: angle of the vector decides the match",
        "cm91bmQgMTYxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 161: the candle burns twice as long at night",
        "cm91bmQgMTYxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 161: a mirror of the universe in one line",
        "cm91bmQgMTYxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 161: the queue drains before the storm", "cm91bmQgMTYxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
