"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten150kitten150", "a2l0dGVuMTUwa2l0dGVuMTUw"),
    ("kitten150sitting150", "a2l0dGVuMTUwc2l0dGluZzE1MA"),
    ("kitten150agent150", "a2l0dGVuMTUwYWdlbnQxNTA"),
    ("kitten150angle150", "a2l0dGVuMTUwYW5nbGUxNTA"),
    ("sitting150angle150", "c2l0dGluZzE1MGFuZ2xlMTUw"),
    ("sitting150universe150", "c2l0dGluZzE1MHVuaXZlcnNlMTUw"),
    ("sitting150memory150", "c2l0dGluZzE1MG1lbW9yeTE1MA"),
    ("sitting150stream150", "c2l0dGluZzE1MHN0cmVhbTE1MA"),
    ("agent150stream150", "YWdlbnQxNTBzdHJlYW0xNTA"),
    ("agent150context150", "YWdlbnQxNTBjb250ZXh0MTUw"),
    ("agent150knowledge150", "YWdlbnQxNTBrbm93bGVkZ2UxNTA"),
    ("agent150vector150", "YWdlbnQxNTB2ZWN0b3IxNTA"),
    ("angle150vector150", "YW5nbGUxNTB2ZWN0b3IxNTA"),
    ("angle150processor150", "YW5nbGUxNTBwcm9jZXNzb3IxNTA"),
    ("angle150reasoning150", "YW5nbGUxNTByZWFzb25pbmcxNTA"),
    ("angle150machine150", "YW5nbGUxNTBtYWNoaW5lMTUw"),
    ("universe150machine150", "dW5pdmVyc2UxNTBtYWNoaW5lMTUw"),
    ("universe150learning150", "dW5pdmVyc2UxNTBsZWFybmluZzE1MA"),
    ("universe150model150", "dW5pdmVyc2UxNTBtb2RlbDE1MA"),
    ("universe150token150", "dW5pdmVyc2UxNTB0b2tlbjE1MA"),
    ("memory150token150", "bWVtb3J5MTUwdG9rZW4xNTA"),
    ("memory150prompt150", "bWVtb3J5MTUwcHJvbXB0MTUw"),
    ("memory150session150", "bWVtb3J5MTUwc2Vzc2lvbjE1MA"),
    ("memory150library150", "bWVtb3J5MTUwbGlicmFyeTE1MA"),
    ("stream150library150", "c3RyZWFtMTUwbGlicmFyeTE1MA"),
    ("stream150service150", "c3RyZWFtMTUwc2VydmljZTE1MA"),
    ("stream150gateway150", "c3RyZWFtMTUwZ2F0ZXdheTE1MA"),
    ("stream150storage150", "c3RyZWFtMTUwc3RvcmFnZTE1MA"),
    ("context150storage150", "Y29udGV4dDE1MHN0b3JhZ2UxNTA"),
    ("context150network150", "Y29udGV4dDE1MG5ldHdvcmsxNTA"),
    ("context150latency150", "Y29udGV4dDE1MGxhdGVuY3kxNTA"),
    ("context150buffer150", "Y29udGV4dDE1MGJ1ZmZlcjE1MA"),
    ("knowledge150buffer150", "a25vd2xlZGdlMTUwYnVmZmVyMTUw"),
    ("knowledge150queue150", "a25vd2xlZGdlMTUwcXVldWUxNTA"),
    ("knowledge150worker150", "a25vd2xlZGdlMTUwd29ya2VyMTUw"),
    ("knowledge150kernel150", "a25vd2xlZGdlMTUwa2VybmVsMTUw"),
    ("vector150kernel150", "dmVjdG9yMTUwa2VybmVsMTUw"),
    ("vector150signal150", "dmVjdG9yMTUwc2lnbmFsMTUw"),
    ("vector150packet150", "dmVjdG9yMTUwcGFja2V0MTUw"),
    ("vector150router150", "dmVjdG9yMTUwcm91dGVyMTUw"),
    ("processor150router150", "cHJvY2Vzc29yMTUwcm91dGVyMTUw"),
    ("processor150cluster150", "cHJvY2Vzc29yMTUwY2x1c3RlcjE1MA"),
    ("processor150mirror150", "cHJvY2Vzc29yMTUwbWlycm9yMTUw"),
    ("processor150filter150", "cHJvY2Vzc29yMTUwZmlsdGVyMTUw"),
    ("reasoning150filter150", "cmVhc29uaW5nMTUwZmlsdGVyMTUw"),
    ("reasoning150ranking150", "cmVhc29uaW5nMTUwcmFua2luZzE1MA"),
    ("reasoning150encoding150", "cmVhc29uaW5nMTUwZW5jb2RpbmcxNTA"),
    ("reasoning150mapping150", "cmVhc29uaW5nMTUwbWFwcGluZzE1MA"),
    ("machine150mapping150", "bWFjaGluZTE1MG1hcHBpbmcxNTA"),
    ("machine150record150", "bWFjaGluZTE1MHJlY29yZDE1MA"),
    ("machine150candle150", "bWFjaGluZTE1MGNhbmRsZTE1MA"),
    ("machine150thread150", "bWFjaGluZTE1MHRocmVhZDE1MA"),
    ("learning150thread150", "bGVhcm5pbmcxNTB0aHJlYWQxNTA"),
    ("learning150kitten150", "bGVhcm5pbmcxNTBraXR0ZW4xNTA"),
    ("learning150sitting150", "bGVhcm5pbmcxNTBzaXR0aW5nMTUw"),
    ("learning150agent150", "bGVhcm5pbmcxNTBhZ2VudDE1MA"),
    ("model150agent150", "bW9kZWwxNTBhZ2VudDE1MA"),
    ("model150angle150", "bW9kZWwxNTBhbmdsZTE1MA"),
    ("model150universe150", "bW9kZWwxNTB1bml2ZXJzZTE1MA"),
    ("model150memory150", "bW9kZWwxNTBtZW1vcnkxNTA"),
    ("token150memory150", "dG9rZW4xNTBtZW1vcnkxNTA"),
    ("token150stream150", "dG9rZW4xNTBzdHJlYW0xNTA"),
    ("token150context150", "dG9rZW4xNTBjb250ZXh0MTUw"),
    ("token150knowledge150", "dG9rZW4xNTBrbm93bGVkZ2UxNTA"),
    ("prompt150knowledge150", "cHJvbXB0MTUwa25vd2xlZGdlMTUw"),
    ("prompt150vector150", "cHJvbXB0MTUwdmVjdG9yMTUw"),
    ("prompt150processor150", "cHJvbXB0MTUwcHJvY2Vzc29yMTUw"),
    ("prompt150reasoning150", "cHJvbXB0MTUwcmVhc29uaW5nMTUw"),
    ("session150reasoning150", "c2Vzc2lvbjE1MHJlYXNvbmluZzE1MA"),
    ("session150machine150", "c2Vzc2lvbjE1MG1hY2hpbmUxNTA"),
    ("session150learning150", "c2Vzc2lvbjE1MGxlYXJuaW5nMTUw"),
    ("session150model150", "c2Vzc2lvbjE1MG1vZGVsMTUw"),
    ("library150model150", "bGlicmFyeTE1MG1vZGVsMTUw"),
    ("library150token150", "bGlicmFyeTE1MHRva2VuMTUw"),
    ("library150prompt150", "bGlicmFyeTE1MHByb21wdDE1MA"),
    ("library150session150", "bGlicmFyeTE1MHNlc3Npb24xNTA"),
    ("service150session150", "c2VydmljZTE1MHNlc3Npb24xNTA"),
    ("service150library150", "c2VydmljZTE1MGxpYnJhcnkxNTA"),
    ("service150service150", "c2VydmljZTE1MHNlcnZpY2UxNTA"),
    ("service150gateway150", "c2VydmljZTE1MGdhdGV3YXkxNTA"),
    ("gateway150gateway150", "Z2F0ZXdheTE1MGdhdGV3YXkxNTA"),
    ("gateway150storage150", "Z2F0ZXdheTE1MHN0b3JhZ2UxNTA"),
    ("gateway150network150", "Z2F0ZXdheTE1MG5ldHdvcmsxNTA"),
    ("gateway150latency150", "Z2F0ZXdheTE1MGxhdGVuY3kxNTA"),
    ("storage150latency150", "c3RvcmFnZTE1MGxhdGVuY3kxNTA"),
    ("storage150buffer150", "c3RvcmFnZTE1MGJ1ZmZlcjE1MA"),
    ("storage150queue150", "c3RvcmFnZTE1MHF1ZXVlMTUw"),
    ("storage150worker150", "c3RvcmFnZTE1MHdvcmtlcjE1MA"),
    ("network150worker150", "bmV0d29yazE1MHdvcmtlcjE1MA"),
    ("network150kernel150", "bmV0d29yazE1MGtlcm5lbDE1MA"),
    ("network150signal150", "bmV0d29yazE1MHNpZ25hbDE1MA"),
    ("network150packet150", "bmV0d29yazE1MHBhY2tldDE1MA"),
    ("latency150packet150", "bGF0ZW5jeTE1MHBhY2tldDE1MA"),
    ("latency150router150", "bGF0ZW5jeTE1MHJvdXRlcjE1MA"),
    ("latency150cluster150", "bGF0ZW5jeTE1MGNsdXN0ZXIxNTA"),
    ("latency150mirror150", "bGF0ZW5jeTE1MG1pcnJvcjE1MA"),
    ("buffer150mirror150", "YnVmZmVyMTUwbWlycm9yMTUw"),
    ("buffer150filter150", "YnVmZmVyMTUwZmlsdGVyMTUw"),
    ("buffer150ranking150", "YnVmZmVyMTUwcmFua2luZzE1MA"),
    ("buffer150encoding150", "YnVmZmVyMTUwZW5jb2RpbmcxNTA"),
    ("queue150encoding150", "cXVldWUxNTBlbmNvZGluZzE1MA"),
    ("queue150mapping150", "cXVldWUxNTBtYXBwaW5nMTUw"),
    ("queue150record150", "cXVldWUxNTByZWNvcmQxNTA"),
    ("queue150candle150", "cXVldWUxNTBjYW5kbGUxNTA"),
    ("worker150candle150", "d29ya2VyMTUwY2FuZGxlMTUw"),
    ("worker150thread150", "d29ya2VyMTUwdGhyZWFkMTUw"),
    ("worker150kitten150", "d29ya2VyMTUwa2l0dGVuMTUw"),
    ("worker150sitting150", "d29ya2VyMTUwc2l0dGluZzE1MA"),
    ("kernel150sitting150", "a2VybmVsMTUwc2l0dGluZzE1MA"),
    ("kernel150agent150", "a2VybmVsMTUwYWdlbnQxNTA"),
    ("kernel150angle150", "a2VybmVsMTUwYW5nbGUxNTA"),
    ("kernel150universe150", "a2VybmVsMTUwdW5pdmVyc2UxNTA"),
    ("signal150universe150", "c2lnbmFsMTUwdW5pdmVyc2UxNTA"),
    ("signal150memory150", "c2lnbmFsMTUwbWVtb3J5MTUw"),
    ("signal150stream150", "c2lnbmFsMTUwc3RyZWFtMTUw"),
    ("signal150context150", "c2lnbmFsMTUwY29udGV4dDE1MA"),
    ("packet150context150", "cGFja2V0MTUwY29udGV4dDE1MA"),
    ("packet150knowledge150", "cGFja2V0MTUwa25vd2xlZGdlMTUw"),
    ("packet150vector150", "cGFja2V0MTUwdmVjdG9yMTUw"),
    ("packet150processor150", "cGFja2V0MTUwcHJvY2Vzc29yMTUw"),
    ("router150processor150", "cm91dGVyMTUwcHJvY2Vzc29yMTUw"),
    ("router150reasoning150", "cm91dGVyMTUwcmVhc29uaW5nMTUw"),
    ("router150machine150", "cm91dGVyMTUwbWFjaGluZTE1MA"),
    ("router150learning150", "cm91dGVyMTUwbGVhcm5pbmcxNTA"),
    ("cluster150learning150", "Y2x1c3RlcjE1MGxlYXJuaW5nMTUw"),
    ("cluster150model150", "Y2x1c3RlcjE1MG1vZGVsMTUw"),
    ("cluster150token150", "Y2x1c3RlcjE1MHRva2VuMTUw"),
    ("cluster150prompt150", "Y2x1c3RlcjE1MHByb21wdDE1MA"),
    ("mirror150prompt150", "bWlycm9yMTUwcHJvbXB0MTUw"),
    ("mirror150session150", "bWlycm9yMTUwc2Vzc2lvbjE1MA"),
    ("mirror150library150", "bWlycm9yMTUwbGlicmFyeTE1MA"),
    ("mirror150service150", "bWlycm9yMTUwc2VydmljZTE1MA"),
    ("filter150service150", "ZmlsdGVyMTUwc2VydmljZTE1MA"),
    ("filter150gateway150", "ZmlsdGVyMTUwZ2F0ZXdheTE1MA"),
    ("filter150storage150", "ZmlsdGVyMTUwc3RvcmFnZTE1MA"),
    ("filter150network150", "ZmlsdGVyMTUwbmV0d29yazE1MA"),
    ("ranking150network150", "cmFua2luZzE1MG5ldHdvcmsxNTA"),
    ("ranking150latency150", "cmFua2luZzE1MGxhdGVuY3kxNTA"),
    ("ranking150buffer150", "cmFua2luZzE1MGJ1ZmZlcjE1MA"),
    ("ranking150queue150", "cmFua2luZzE1MHF1ZXVlMTUw"),
    ("encoding150queue150", "ZW5jb2RpbmcxNTBxdWV1ZTE1MA"),
    ("encoding150worker150", "ZW5jb2RpbmcxNTB3b3JrZXIxNTA"),
    ("encoding150kernel150", "ZW5jb2RpbmcxNTBrZXJuZWwxNTA"),
    ("encoding150signal150", "ZW5jb2RpbmcxNTBzaWduYWwxNTA"),
    ("mapping150signal150", "bWFwcGluZzE1MHNpZ25hbDE1MA"),
    ("mapping150packet150", "bWFwcGluZzE1MHBhY2tldDE1MA"),
    ("mapping150router150", "bWFwcGluZzE1MHJvdXRlcjE1MA"),
    ("mapping150cluster150", "bWFwcGluZzE1MGNsdXN0ZXIxNTA"),
    ("record150cluster150", "cmVjb3JkMTUwY2x1c3RlcjE1MA"),
    ("record150mirror150", "cmVjb3JkMTUwbWlycm9yMTUw"),
    ("record150filter150", "cmVjb3JkMTUwZmlsdGVyMTUw"),
    ("record150ranking150", "cmVjb3JkMTUwcmFua2luZzE1MA"),
    ("candle150ranking150", "Y2FuZGxlMTUwcmFua2luZzE1MA"),
    ("candle150encoding150", "Y2FuZGxlMTUwZW5jb2RpbmcxNTA"),
    ("candle150mapping150", "Y2FuZGxlMTUwbWFwcGluZzE1MA"),
    ("candle150record150", "Y2FuZGxlMTUwcmVjb3JkMTUw"),
    ("thread150record150", "dGhyZWFkMTUwcmVjb3JkMTUw"),
    ("thread150candle150", "dGhyZWFkMTUwY2FuZGxlMTUw"),
    ("thread150thread150", "dGhyZWFkMTUwdGhyZWFkMTUw"),
    ("thread150kitten150", "dGhyZWFkMTUwa2l0dGVuMTUw"),
    (
        "round 150: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTUwOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 150: agentuniverse is a framework for multi agents",
        "cm91bmQgMTUwOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 150: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTUwOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 150: the processor reads the record then stops",
        "cm91bmQgMTUwOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 150: a worker pulls the next task from the queue",
        "cm91bmQgMTUwOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 150: signals travel through the network layer",
        "cm91bmQgMTUwOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 150: the gateway routes each request by policy",
        "cm91bmQgMTUwOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 150: memory grows until the buffer is full",
        "cm91bmQgMTUwOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 150: the cluster mirrors every packet twice",
        "cm91bmQgMTUwOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 150: ranking uses tokens learned from the corpus",
        "cm91bmQgMTUwOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 150: a long session ends when the candle dies",
        "cm91bmQgMTUwOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 150: encode the prompt then map the result",
        "cm91bmQgMTUwOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 150: the kernel wakes the worker at dawn",
        "cm91bmQgMTUwOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 150: service latency drops after the patch",
        "cm91bmQgMTUwOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 150: the library caches every vector it sees",
        "cm91bmQgMTUwOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 150: agents argue then the debate resolves",
        "cm91bmQgMTUwOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 150: the filter keeps only strong matches",
        "cm91bmQgMTUwOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 150: the model answers with a short reply",
        "cm91bmQgMTUwOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 150: the recorder stores the reasoning trace",
        "cm91bmQgMTUwOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 150: the angel watches the processor run",
        "cm91bmQgMTUwOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 150: angle of the vector decides the match",
        "cm91bmQgMTUwOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 150: the candle burns twice as long at night",
        "cm91bmQgMTUwOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 150: a mirror of the universe in one line",
        "cm91bmQgMTUwOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 150: the queue drains before the storm", "cm91bmQgMTUwOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
