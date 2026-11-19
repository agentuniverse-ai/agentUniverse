"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten181kitten181", "a2l0dGVuMTgxa2l0dGVuMTgx"),
    ("kitten181sitting181", "a2l0dGVuMTgxc2l0dGluZzE4MQ"),
    ("kitten181agent181", "a2l0dGVuMTgxYWdlbnQxODE"),
    ("kitten181angle181", "a2l0dGVuMTgxYW5nbGUxODE"),
    ("sitting181angle181", "c2l0dGluZzE4MWFuZ2xlMTgx"),
    ("sitting181universe181", "c2l0dGluZzE4MXVuaXZlcnNlMTgx"),
    ("sitting181memory181", "c2l0dGluZzE4MW1lbW9yeTE4MQ"),
    ("sitting181stream181", "c2l0dGluZzE4MXN0cmVhbTE4MQ"),
    ("agent181stream181", "YWdlbnQxODFzdHJlYW0xODE"),
    ("agent181context181", "YWdlbnQxODFjb250ZXh0MTgx"),
    ("agent181knowledge181", "YWdlbnQxODFrbm93bGVkZ2UxODE"),
    ("agent181vector181", "YWdlbnQxODF2ZWN0b3IxODE"),
    ("angle181vector181", "YW5nbGUxODF2ZWN0b3IxODE"),
    ("angle181processor181", "YW5nbGUxODFwcm9jZXNzb3IxODE"),
    ("angle181reasoning181", "YW5nbGUxODFyZWFzb25pbmcxODE"),
    ("angle181machine181", "YW5nbGUxODFtYWNoaW5lMTgx"),
    ("universe181machine181", "dW5pdmVyc2UxODFtYWNoaW5lMTgx"),
    ("universe181learning181", "dW5pdmVyc2UxODFsZWFybmluZzE4MQ"),
    ("universe181model181", "dW5pdmVyc2UxODFtb2RlbDE4MQ"),
    ("universe181token181", "dW5pdmVyc2UxODF0b2tlbjE4MQ"),
    ("memory181token181", "bWVtb3J5MTgxdG9rZW4xODE"),
    ("memory181prompt181", "bWVtb3J5MTgxcHJvbXB0MTgx"),
    ("memory181session181", "bWVtb3J5MTgxc2Vzc2lvbjE4MQ"),
    ("memory181library181", "bWVtb3J5MTgxbGlicmFyeTE4MQ"),
    ("stream181library181", "c3RyZWFtMTgxbGlicmFyeTE4MQ"),
    ("stream181service181", "c3RyZWFtMTgxc2VydmljZTE4MQ"),
    ("stream181gateway181", "c3RyZWFtMTgxZ2F0ZXdheTE4MQ"),
    ("stream181storage181", "c3RyZWFtMTgxc3RvcmFnZTE4MQ"),
    ("context181storage181", "Y29udGV4dDE4MXN0b3JhZ2UxODE"),
    ("context181network181", "Y29udGV4dDE4MW5ldHdvcmsxODE"),
    ("context181latency181", "Y29udGV4dDE4MWxhdGVuY3kxODE"),
    ("context181buffer181", "Y29udGV4dDE4MWJ1ZmZlcjE4MQ"),
    ("knowledge181buffer181", "a25vd2xlZGdlMTgxYnVmZmVyMTgx"),
    ("knowledge181queue181", "a25vd2xlZGdlMTgxcXVldWUxODE"),
    ("knowledge181worker181", "a25vd2xlZGdlMTgxd29ya2VyMTgx"),
    ("knowledge181kernel181", "a25vd2xlZGdlMTgxa2VybmVsMTgx"),
    ("vector181kernel181", "dmVjdG9yMTgxa2VybmVsMTgx"),
    ("vector181signal181", "dmVjdG9yMTgxc2lnbmFsMTgx"),
    ("vector181packet181", "dmVjdG9yMTgxcGFja2V0MTgx"),
    ("vector181router181", "dmVjdG9yMTgxcm91dGVyMTgx"),
    ("processor181router181", "cHJvY2Vzc29yMTgxcm91dGVyMTgx"),
    ("processor181cluster181", "cHJvY2Vzc29yMTgxY2x1c3RlcjE4MQ"),
    ("processor181mirror181", "cHJvY2Vzc29yMTgxbWlycm9yMTgx"),
    ("processor181filter181", "cHJvY2Vzc29yMTgxZmlsdGVyMTgx"),
    ("reasoning181filter181", "cmVhc29uaW5nMTgxZmlsdGVyMTgx"),
    ("reasoning181ranking181", "cmVhc29uaW5nMTgxcmFua2luZzE4MQ"),
    ("reasoning181encoding181", "cmVhc29uaW5nMTgxZW5jb2RpbmcxODE"),
    ("reasoning181mapping181", "cmVhc29uaW5nMTgxbWFwcGluZzE4MQ"),
    ("machine181mapping181", "bWFjaGluZTE4MW1hcHBpbmcxODE"),
    ("machine181record181", "bWFjaGluZTE4MXJlY29yZDE4MQ"),
    ("machine181candle181", "bWFjaGluZTE4MWNhbmRsZTE4MQ"),
    ("machine181thread181", "bWFjaGluZTE4MXRocmVhZDE4MQ"),
    ("learning181thread181", "bGVhcm5pbmcxODF0aHJlYWQxODE"),
    ("learning181kitten181", "bGVhcm5pbmcxODFraXR0ZW4xODE"),
    ("learning181sitting181", "bGVhcm5pbmcxODFzaXR0aW5nMTgx"),
    ("learning181agent181", "bGVhcm5pbmcxODFhZ2VudDE4MQ"),
    ("model181agent181", "bW9kZWwxODFhZ2VudDE4MQ"),
    ("model181angle181", "bW9kZWwxODFhbmdsZTE4MQ"),
    ("model181universe181", "bW9kZWwxODF1bml2ZXJzZTE4MQ"),
    ("model181memory181", "bW9kZWwxODFtZW1vcnkxODE"),
    ("token181memory181", "dG9rZW4xODFtZW1vcnkxODE"),
    ("token181stream181", "dG9rZW4xODFzdHJlYW0xODE"),
    ("token181context181", "dG9rZW4xODFjb250ZXh0MTgx"),
    ("token181knowledge181", "dG9rZW4xODFrbm93bGVkZ2UxODE"),
    ("prompt181knowledge181", "cHJvbXB0MTgxa25vd2xlZGdlMTgx"),
    ("prompt181vector181", "cHJvbXB0MTgxdmVjdG9yMTgx"),
    ("prompt181processor181", "cHJvbXB0MTgxcHJvY2Vzc29yMTgx"),
    ("prompt181reasoning181", "cHJvbXB0MTgxcmVhc29uaW5nMTgx"),
    ("session181reasoning181", "c2Vzc2lvbjE4MXJlYXNvbmluZzE4MQ"),
    ("session181machine181", "c2Vzc2lvbjE4MW1hY2hpbmUxODE"),
    ("session181learning181", "c2Vzc2lvbjE4MWxlYXJuaW5nMTgx"),
    ("session181model181", "c2Vzc2lvbjE4MW1vZGVsMTgx"),
    ("library181model181", "bGlicmFyeTE4MW1vZGVsMTgx"),
    ("library181token181", "bGlicmFyeTE4MXRva2VuMTgx"),
    ("library181prompt181", "bGlicmFyeTE4MXByb21wdDE4MQ"),
    ("library181session181", "bGlicmFyeTE4MXNlc3Npb24xODE"),
    ("service181session181", "c2VydmljZTE4MXNlc3Npb24xODE"),
    ("service181library181", "c2VydmljZTE4MWxpYnJhcnkxODE"),
    ("service181service181", "c2VydmljZTE4MXNlcnZpY2UxODE"),
    ("service181gateway181", "c2VydmljZTE4MWdhdGV3YXkxODE"),
    ("gateway181gateway181", "Z2F0ZXdheTE4MWdhdGV3YXkxODE"),
    ("gateway181storage181", "Z2F0ZXdheTE4MXN0b3JhZ2UxODE"),
    ("gateway181network181", "Z2F0ZXdheTE4MW5ldHdvcmsxODE"),
    ("gateway181latency181", "Z2F0ZXdheTE4MWxhdGVuY3kxODE"),
    ("storage181latency181", "c3RvcmFnZTE4MWxhdGVuY3kxODE"),
    ("storage181buffer181", "c3RvcmFnZTE4MWJ1ZmZlcjE4MQ"),
    ("storage181queue181", "c3RvcmFnZTE4MXF1ZXVlMTgx"),
    ("storage181worker181", "c3RvcmFnZTE4MXdvcmtlcjE4MQ"),
    ("network181worker181", "bmV0d29yazE4MXdvcmtlcjE4MQ"),
    ("network181kernel181", "bmV0d29yazE4MWtlcm5lbDE4MQ"),
    ("network181signal181", "bmV0d29yazE4MXNpZ25hbDE4MQ"),
    ("network181packet181", "bmV0d29yazE4MXBhY2tldDE4MQ"),
    ("latency181packet181", "bGF0ZW5jeTE4MXBhY2tldDE4MQ"),
    ("latency181router181", "bGF0ZW5jeTE4MXJvdXRlcjE4MQ"),
    ("latency181cluster181", "bGF0ZW5jeTE4MWNsdXN0ZXIxODE"),
    ("latency181mirror181", "bGF0ZW5jeTE4MW1pcnJvcjE4MQ"),
    ("buffer181mirror181", "YnVmZmVyMTgxbWlycm9yMTgx"),
    ("buffer181filter181", "YnVmZmVyMTgxZmlsdGVyMTgx"),
    ("buffer181ranking181", "YnVmZmVyMTgxcmFua2luZzE4MQ"),
    ("buffer181encoding181", "YnVmZmVyMTgxZW5jb2RpbmcxODE"),
    ("queue181encoding181", "cXVldWUxODFlbmNvZGluZzE4MQ"),
    ("queue181mapping181", "cXVldWUxODFtYXBwaW5nMTgx"),
    ("queue181record181", "cXVldWUxODFyZWNvcmQxODE"),
    ("queue181candle181", "cXVldWUxODFjYW5kbGUxODE"),
    ("worker181candle181", "d29ya2VyMTgxY2FuZGxlMTgx"),
    ("worker181thread181", "d29ya2VyMTgxdGhyZWFkMTgx"),
    ("worker181kitten181", "d29ya2VyMTgxa2l0dGVuMTgx"),
    ("worker181sitting181", "d29ya2VyMTgxc2l0dGluZzE4MQ"),
    ("kernel181sitting181", "a2VybmVsMTgxc2l0dGluZzE4MQ"),
    ("kernel181agent181", "a2VybmVsMTgxYWdlbnQxODE"),
    ("kernel181angle181", "a2VybmVsMTgxYW5nbGUxODE"),
    ("kernel181universe181", "a2VybmVsMTgxdW5pdmVyc2UxODE"),
    ("signal181universe181", "c2lnbmFsMTgxdW5pdmVyc2UxODE"),
    ("signal181memory181", "c2lnbmFsMTgxbWVtb3J5MTgx"),
    ("signal181stream181", "c2lnbmFsMTgxc3RyZWFtMTgx"),
    ("signal181context181", "c2lnbmFsMTgxY29udGV4dDE4MQ"),
    ("packet181context181", "cGFja2V0MTgxY29udGV4dDE4MQ"),
    ("packet181knowledge181", "cGFja2V0MTgxa25vd2xlZGdlMTgx"),
    ("packet181vector181", "cGFja2V0MTgxdmVjdG9yMTgx"),
    ("packet181processor181", "cGFja2V0MTgxcHJvY2Vzc29yMTgx"),
    ("router181processor181", "cm91dGVyMTgxcHJvY2Vzc29yMTgx"),
    ("router181reasoning181", "cm91dGVyMTgxcmVhc29uaW5nMTgx"),
    ("router181machine181", "cm91dGVyMTgxbWFjaGluZTE4MQ"),
    ("router181learning181", "cm91dGVyMTgxbGVhcm5pbmcxODE"),
    ("cluster181learning181", "Y2x1c3RlcjE4MWxlYXJuaW5nMTgx"),
    ("cluster181model181", "Y2x1c3RlcjE4MW1vZGVsMTgx"),
    ("cluster181token181", "Y2x1c3RlcjE4MXRva2VuMTgx"),
    ("cluster181prompt181", "Y2x1c3RlcjE4MXByb21wdDE4MQ"),
    ("mirror181prompt181", "bWlycm9yMTgxcHJvbXB0MTgx"),
    ("mirror181session181", "bWlycm9yMTgxc2Vzc2lvbjE4MQ"),
    ("mirror181library181", "bWlycm9yMTgxbGlicmFyeTE4MQ"),
    ("mirror181service181", "bWlycm9yMTgxc2VydmljZTE4MQ"),
    ("filter181service181", "ZmlsdGVyMTgxc2VydmljZTE4MQ"),
    ("filter181gateway181", "ZmlsdGVyMTgxZ2F0ZXdheTE4MQ"),
    ("filter181storage181", "ZmlsdGVyMTgxc3RvcmFnZTE4MQ"),
    ("filter181network181", "ZmlsdGVyMTgxbmV0d29yazE4MQ"),
    ("ranking181network181", "cmFua2luZzE4MW5ldHdvcmsxODE"),
    ("ranking181latency181", "cmFua2luZzE4MWxhdGVuY3kxODE"),
    ("ranking181buffer181", "cmFua2luZzE4MWJ1ZmZlcjE4MQ"),
    ("ranking181queue181", "cmFua2luZzE4MXF1ZXVlMTgx"),
    ("encoding181queue181", "ZW5jb2RpbmcxODFxdWV1ZTE4MQ"),
    ("encoding181worker181", "ZW5jb2RpbmcxODF3b3JrZXIxODE"),
    ("encoding181kernel181", "ZW5jb2RpbmcxODFrZXJuZWwxODE"),
    ("encoding181signal181", "ZW5jb2RpbmcxODFzaWduYWwxODE"),
    ("mapping181signal181", "bWFwcGluZzE4MXNpZ25hbDE4MQ"),
    ("mapping181packet181", "bWFwcGluZzE4MXBhY2tldDE4MQ"),
    ("mapping181router181", "bWFwcGluZzE4MXJvdXRlcjE4MQ"),
    ("mapping181cluster181", "bWFwcGluZzE4MWNsdXN0ZXIxODE"),
    ("record181cluster181", "cmVjb3JkMTgxY2x1c3RlcjE4MQ"),
    ("record181mirror181", "cmVjb3JkMTgxbWlycm9yMTgx"),
    ("record181filter181", "cmVjb3JkMTgxZmlsdGVyMTgx"),
    ("record181ranking181", "cmVjb3JkMTgxcmFua2luZzE4MQ"),
    ("candle181ranking181", "Y2FuZGxlMTgxcmFua2luZzE4MQ"),
    ("candle181encoding181", "Y2FuZGxlMTgxZW5jb2RpbmcxODE"),
    ("candle181mapping181", "Y2FuZGxlMTgxbWFwcGluZzE4MQ"),
    ("candle181record181", "Y2FuZGxlMTgxcmVjb3JkMTgx"),
    ("thread181record181", "dGhyZWFkMTgxcmVjb3JkMTgx"),
    ("thread181candle181", "dGhyZWFkMTgxY2FuZGxlMTgx"),
    ("thread181thread181", "dGhyZWFkMTgxdGhyZWFkMTgx"),
    ("thread181kitten181", "dGhyZWFkMTgxa2l0dGVuMTgx"),
    (
        "round 181: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTgxOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 181: agentuniverse is a framework for multi agents",
        "cm91bmQgMTgxOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 181: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTgxOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 181: the processor reads the record then stops",
        "cm91bmQgMTgxOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 181: a worker pulls the next task from the queue",
        "cm91bmQgMTgxOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 181: signals travel through the network layer",
        "cm91bmQgMTgxOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 181: the gateway routes each request by policy",
        "cm91bmQgMTgxOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 181: memory grows until the buffer is full",
        "cm91bmQgMTgxOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 181: the cluster mirrors every packet twice",
        "cm91bmQgMTgxOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 181: ranking uses tokens learned from the corpus",
        "cm91bmQgMTgxOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 181: a long session ends when the candle dies",
        "cm91bmQgMTgxOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 181: encode the prompt then map the result",
        "cm91bmQgMTgxOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 181: the kernel wakes the worker at dawn",
        "cm91bmQgMTgxOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 181: service latency drops after the patch",
        "cm91bmQgMTgxOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 181: the library caches every vector it sees",
        "cm91bmQgMTgxOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 181: agents argue then the debate resolves",
        "cm91bmQgMTgxOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 181: the filter keeps only strong matches",
        "cm91bmQgMTgxOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 181: the model answers with a short reply",
        "cm91bmQgMTgxOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 181: the recorder stores the reasoning trace",
        "cm91bmQgMTgxOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 181: the angel watches the processor run",
        "cm91bmQgMTgxOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 181: angle of the vector decides the match",
        "cm91bmQgMTgxOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 181: the candle burns twice as long at night",
        "cm91bmQgMTgxOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 181: a mirror of the universe in one line",
        "cm91bmQgMTgxOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 181: the queue drains before the storm", "cm91bmQgMTgxOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
