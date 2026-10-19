"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten149kitten149", "a2l0dGVuMTQ5a2l0dGVuMTQ5"),
    ("kitten149sitting149", "a2l0dGVuMTQ5c2l0dGluZzE0OQ"),
    ("kitten149agent149", "a2l0dGVuMTQ5YWdlbnQxNDk"),
    ("kitten149angle149", "a2l0dGVuMTQ5YW5nbGUxNDk"),
    ("sitting149angle149", "c2l0dGluZzE0OWFuZ2xlMTQ5"),
    ("sitting149universe149", "c2l0dGluZzE0OXVuaXZlcnNlMTQ5"),
    ("sitting149memory149", "c2l0dGluZzE0OW1lbW9yeTE0OQ"),
    ("sitting149stream149", "c2l0dGluZzE0OXN0cmVhbTE0OQ"),
    ("agent149stream149", "YWdlbnQxNDlzdHJlYW0xNDk"),
    ("agent149context149", "YWdlbnQxNDljb250ZXh0MTQ5"),
    ("agent149knowledge149", "YWdlbnQxNDlrbm93bGVkZ2UxNDk"),
    ("agent149vector149", "YWdlbnQxNDl2ZWN0b3IxNDk"),
    ("angle149vector149", "YW5nbGUxNDl2ZWN0b3IxNDk"),
    ("angle149processor149", "YW5nbGUxNDlwcm9jZXNzb3IxNDk"),
    ("angle149reasoning149", "YW5nbGUxNDlyZWFzb25pbmcxNDk"),
    ("angle149machine149", "YW5nbGUxNDltYWNoaW5lMTQ5"),
    ("universe149machine149", "dW5pdmVyc2UxNDltYWNoaW5lMTQ5"),
    ("universe149learning149", "dW5pdmVyc2UxNDlsZWFybmluZzE0OQ"),
    ("universe149model149", "dW5pdmVyc2UxNDltb2RlbDE0OQ"),
    ("universe149token149", "dW5pdmVyc2UxNDl0b2tlbjE0OQ"),
    ("memory149token149", "bWVtb3J5MTQ5dG9rZW4xNDk"),
    ("memory149prompt149", "bWVtb3J5MTQ5cHJvbXB0MTQ5"),
    ("memory149session149", "bWVtb3J5MTQ5c2Vzc2lvbjE0OQ"),
    ("memory149library149", "bWVtb3J5MTQ5bGlicmFyeTE0OQ"),
    ("stream149library149", "c3RyZWFtMTQ5bGlicmFyeTE0OQ"),
    ("stream149service149", "c3RyZWFtMTQ5c2VydmljZTE0OQ"),
    ("stream149gateway149", "c3RyZWFtMTQ5Z2F0ZXdheTE0OQ"),
    ("stream149storage149", "c3RyZWFtMTQ5c3RvcmFnZTE0OQ"),
    ("context149storage149", "Y29udGV4dDE0OXN0b3JhZ2UxNDk"),
    ("context149network149", "Y29udGV4dDE0OW5ldHdvcmsxNDk"),
    ("context149latency149", "Y29udGV4dDE0OWxhdGVuY3kxNDk"),
    ("context149buffer149", "Y29udGV4dDE0OWJ1ZmZlcjE0OQ"),
    ("knowledge149buffer149", "a25vd2xlZGdlMTQ5YnVmZmVyMTQ5"),
    ("knowledge149queue149", "a25vd2xlZGdlMTQ5cXVldWUxNDk"),
    ("knowledge149worker149", "a25vd2xlZGdlMTQ5d29ya2VyMTQ5"),
    ("knowledge149kernel149", "a25vd2xlZGdlMTQ5a2VybmVsMTQ5"),
    ("vector149kernel149", "dmVjdG9yMTQ5a2VybmVsMTQ5"),
    ("vector149signal149", "dmVjdG9yMTQ5c2lnbmFsMTQ5"),
    ("vector149packet149", "dmVjdG9yMTQ5cGFja2V0MTQ5"),
    ("vector149router149", "dmVjdG9yMTQ5cm91dGVyMTQ5"),
    ("processor149router149", "cHJvY2Vzc29yMTQ5cm91dGVyMTQ5"),
    ("processor149cluster149", "cHJvY2Vzc29yMTQ5Y2x1c3RlcjE0OQ"),
    ("processor149mirror149", "cHJvY2Vzc29yMTQ5bWlycm9yMTQ5"),
    ("processor149filter149", "cHJvY2Vzc29yMTQ5ZmlsdGVyMTQ5"),
    ("reasoning149filter149", "cmVhc29uaW5nMTQ5ZmlsdGVyMTQ5"),
    ("reasoning149ranking149", "cmVhc29uaW5nMTQ5cmFua2luZzE0OQ"),
    ("reasoning149encoding149", "cmVhc29uaW5nMTQ5ZW5jb2RpbmcxNDk"),
    ("reasoning149mapping149", "cmVhc29uaW5nMTQ5bWFwcGluZzE0OQ"),
    ("machine149mapping149", "bWFjaGluZTE0OW1hcHBpbmcxNDk"),
    ("machine149record149", "bWFjaGluZTE0OXJlY29yZDE0OQ"),
    ("machine149candle149", "bWFjaGluZTE0OWNhbmRsZTE0OQ"),
    ("machine149thread149", "bWFjaGluZTE0OXRocmVhZDE0OQ"),
    ("learning149thread149", "bGVhcm5pbmcxNDl0aHJlYWQxNDk"),
    ("learning149kitten149", "bGVhcm5pbmcxNDlraXR0ZW4xNDk"),
    ("learning149sitting149", "bGVhcm5pbmcxNDlzaXR0aW5nMTQ5"),
    ("learning149agent149", "bGVhcm5pbmcxNDlhZ2VudDE0OQ"),
    ("model149agent149", "bW9kZWwxNDlhZ2VudDE0OQ"),
    ("model149angle149", "bW9kZWwxNDlhbmdsZTE0OQ"),
    ("model149universe149", "bW9kZWwxNDl1bml2ZXJzZTE0OQ"),
    ("model149memory149", "bW9kZWwxNDltZW1vcnkxNDk"),
    ("token149memory149", "dG9rZW4xNDltZW1vcnkxNDk"),
    ("token149stream149", "dG9rZW4xNDlzdHJlYW0xNDk"),
    ("token149context149", "dG9rZW4xNDljb250ZXh0MTQ5"),
    ("token149knowledge149", "dG9rZW4xNDlrbm93bGVkZ2UxNDk"),
    ("prompt149knowledge149", "cHJvbXB0MTQ5a25vd2xlZGdlMTQ5"),
    ("prompt149vector149", "cHJvbXB0MTQ5dmVjdG9yMTQ5"),
    ("prompt149processor149", "cHJvbXB0MTQ5cHJvY2Vzc29yMTQ5"),
    ("prompt149reasoning149", "cHJvbXB0MTQ5cmVhc29uaW5nMTQ5"),
    ("session149reasoning149", "c2Vzc2lvbjE0OXJlYXNvbmluZzE0OQ"),
    ("session149machine149", "c2Vzc2lvbjE0OW1hY2hpbmUxNDk"),
    ("session149learning149", "c2Vzc2lvbjE0OWxlYXJuaW5nMTQ5"),
    ("session149model149", "c2Vzc2lvbjE0OW1vZGVsMTQ5"),
    ("library149model149", "bGlicmFyeTE0OW1vZGVsMTQ5"),
    ("library149token149", "bGlicmFyeTE0OXRva2VuMTQ5"),
    ("library149prompt149", "bGlicmFyeTE0OXByb21wdDE0OQ"),
    ("library149session149", "bGlicmFyeTE0OXNlc3Npb24xNDk"),
    ("service149session149", "c2VydmljZTE0OXNlc3Npb24xNDk"),
    ("service149library149", "c2VydmljZTE0OWxpYnJhcnkxNDk"),
    ("service149service149", "c2VydmljZTE0OXNlcnZpY2UxNDk"),
    ("service149gateway149", "c2VydmljZTE0OWdhdGV3YXkxNDk"),
    ("gateway149gateway149", "Z2F0ZXdheTE0OWdhdGV3YXkxNDk"),
    ("gateway149storage149", "Z2F0ZXdheTE0OXN0b3JhZ2UxNDk"),
    ("gateway149network149", "Z2F0ZXdheTE0OW5ldHdvcmsxNDk"),
    ("gateway149latency149", "Z2F0ZXdheTE0OWxhdGVuY3kxNDk"),
    ("storage149latency149", "c3RvcmFnZTE0OWxhdGVuY3kxNDk"),
    ("storage149buffer149", "c3RvcmFnZTE0OWJ1ZmZlcjE0OQ"),
    ("storage149queue149", "c3RvcmFnZTE0OXF1ZXVlMTQ5"),
    ("storage149worker149", "c3RvcmFnZTE0OXdvcmtlcjE0OQ"),
    ("network149worker149", "bmV0d29yazE0OXdvcmtlcjE0OQ"),
    ("network149kernel149", "bmV0d29yazE0OWtlcm5lbDE0OQ"),
    ("network149signal149", "bmV0d29yazE0OXNpZ25hbDE0OQ"),
    ("network149packet149", "bmV0d29yazE0OXBhY2tldDE0OQ"),
    ("latency149packet149", "bGF0ZW5jeTE0OXBhY2tldDE0OQ"),
    ("latency149router149", "bGF0ZW5jeTE0OXJvdXRlcjE0OQ"),
    ("latency149cluster149", "bGF0ZW5jeTE0OWNsdXN0ZXIxNDk"),
    ("latency149mirror149", "bGF0ZW5jeTE0OW1pcnJvcjE0OQ"),
    ("buffer149mirror149", "YnVmZmVyMTQ5bWlycm9yMTQ5"),
    ("buffer149filter149", "YnVmZmVyMTQ5ZmlsdGVyMTQ5"),
    ("buffer149ranking149", "YnVmZmVyMTQ5cmFua2luZzE0OQ"),
    ("buffer149encoding149", "YnVmZmVyMTQ5ZW5jb2RpbmcxNDk"),
    ("queue149encoding149", "cXVldWUxNDllbmNvZGluZzE0OQ"),
    ("queue149mapping149", "cXVldWUxNDltYXBwaW5nMTQ5"),
    ("queue149record149", "cXVldWUxNDlyZWNvcmQxNDk"),
    ("queue149candle149", "cXVldWUxNDljYW5kbGUxNDk"),
    ("worker149candle149", "d29ya2VyMTQ5Y2FuZGxlMTQ5"),
    ("worker149thread149", "d29ya2VyMTQ5dGhyZWFkMTQ5"),
    ("worker149kitten149", "d29ya2VyMTQ5a2l0dGVuMTQ5"),
    ("worker149sitting149", "d29ya2VyMTQ5c2l0dGluZzE0OQ"),
    ("kernel149sitting149", "a2VybmVsMTQ5c2l0dGluZzE0OQ"),
    ("kernel149agent149", "a2VybmVsMTQ5YWdlbnQxNDk"),
    ("kernel149angle149", "a2VybmVsMTQ5YW5nbGUxNDk"),
    ("kernel149universe149", "a2VybmVsMTQ5dW5pdmVyc2UxNDk"),
    ("signal149universe149", "c2lnbmFsMTQ5dW5pdmVyc2UxNDk"),
    ("signal149memory149", "c2lnbmFsMTQ5bWVtb3J5MTQ5"),
    ("signal149stream149", "c2lnbmFsMTQ5c3RyZWFtMTQ5"),
    ("signal149context149", "c2lnbmFsMTQ5Y29udGV4dDE0OQ"),
    ("packet149context149", "cGFja2V0MTQ5Y29udGV4dDE0OQ"),
    ("packet149knowledge149", "cGFja2V0MTQ5a25vd2xlZGdlMTQ5"),
    ("packet149vector149", "cGFja2V0MTQ5dmVjdG9yMTQ5"),
    ("packet149processor149", "cGFja2V0MTQ5cHJvY2Vzc29yMTQ5"),
    ("router149processor149", "cm91dGVyMTQ5cHJvY2Vzc29yMTQ5"),
    ("router149reasoning149", "cm91dGVyMTQ5cmVhc29uaW5nMTQ5"),
    ("router149machine149", "cm91dGVyMTQ5bWFjaGluZTE0OQ"),
    ("router149learning149", "cm91dGVyMTQ5bGVhcm5pbmcxNDk"),
    ("cluster149learning149", "Y2x1c3RlcjE0OWxlYXJuaW5nMTQ5"),
    ("cluster149model149", "Y2x1c3RlcjE0OW1vZGVsMTQ5"),
    ("cluster149token149", "Y2x1c3RlcjE0OXRva2VuMTQ5"),
    ("cluster149prompt149", "Y2x1c3RlcjE0OXByb21wdDE0OQ"),
    ("mirror149prompt149", "bWlycm9yMTQ5cHJvbXB0MTQ5"),
    ("mirror149session149", "bWlycm9yMTQ5c2Vzc2lvbjE0OQ"),
    ("mirror149library149", "bWlycm9yMTQ5bGlicmFyeTE0OQ"),
    ("mirror149service149", "bWlycm9yMTQ5c2VydmljZTE0OQ"),
    ("filter149service149", "ZmlsdGVyMTQ5c2VydmljZTE0OQ"),
    ("filter149gateway149", "ZmlsdGVyMTQ5Z2F0ZXdheTE0OQ"),
    ("filter149storage149", "ZmlsdGVyMTQ5c3RvcmFnZTE0OQ"),
    ("filter149network149", "ZmlsdGVyMTQ5bmV0d29yazE0OQ"),
    ("ranking149network149", "cmFua2luZzE0OW5ldHdvcmsxNDk"),
    ("ranking149latency149", "cmFua2luZzE0OWxhdGVuY3kxNDk"),
    ("ranking149buffer149", "cmFua2luZzE0OWJ1ZmZlcjE0OQ"),
    ("ranking149queue149", "cmFua2luZzE0OXF1ZXVlMTQ5"),
    ("encoding149queue149", "ZW5jb2RpbmcxNDlxdWV1ZTE0OQ"),
    ("encoding149worker149", "ZW5jb2RpbmcxNDl3b3JrZXIxNDk"),
    ("encoding149kernel149", "ZW5jb2RpbmcxNDlrZXJuZWwxNDk"),
    ("encoding149signal149", "ZW5jb2RpbmcxNDlzaWduYWwxNDk"),
    ("mapping149signal149", "bWFwcGluZzE0OXNpZ25hbDE0OQ"),
    ("mapping149packet149", "bWFwcGluZzE0OXBhY2tldDE0OQ"),
    ("mapping149router149", "bWFwcGluZzE0OXJvdXRlcjE0OQ"),
    ("mapping149cluster149", "bWFwcGluZzE0OWNsdXN0ZXIxNDk"),
    ("record149cluster149", "cmVjb3JkMTQ5Y2x1c3RlcjE0OQ"),
    ("record149mirror149", "cmVjb3JkMTQ5bWlycm9yMTQ5"),
    ("record149filter149", "cmVjb3JkMTQ5ZmlsdGVyMTQ5"),
    ("record149ranking149", "cmVjb3JkMTQ5cmFua2luZzE0OQ"),
    ("candle149ranking149", "Y2FuZGxlMTQ5cmFua2luZzE0OQ"),
    ("candle149encoding149", "Y2FuZGxlMTQ5ZW5jb2RpbmcxNDk"),
    ("candle149mapping149", "Y2FuZGxlMTQ5bWFwcGluZzE0OQ"),
    ("candle149record149", "Y2FuZGxlMTQ5cmVjb3JkMTQ5"),
    ("thread149record149", "dGhyZWFkMTQ5cmVjb3JkMTQ5"),
    ("thread149candle149", "dGhyZWFkMTQ5Y2FuZGxlMTQ5"),
    ("thread149thread149", "dGhyZWFkMTQ5dGhyZWFkMTQ5"),
    ("thread149kitten149", "dGhyZWFkMTQ5a2l0dGVuMTQ5"),
    (
        "round 149: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTQ5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 149: agentuniverse is a framework for multi agents",
        "cm91bmQgMTQ5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 149: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTQ5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 149: the processor reads the record then stops",
        "cm91bmQgMTQ5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 149: a worker pulls the next task from the queue",
        "cm91bmQgMTQ5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 149: signals travel through the network layer",
        "cm91bmQgMTQ5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 149: the gateway routes each request by policy",
        "cm91bmQgMTQ5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 149: memory grows until the buffer is full",
        "cm91bmQgMTQ5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 149: the cluster mirrors every packet twice",
        "cm91bmQgMTQ5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 149: ranking uses tokens learned from the corpus",
        "cm91bmQgMTQ5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 149: a long session ends when the candle dies",
        "cm91bmQgMTQ5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 149: encode the prompt then map the result",
        "cm91bmQgMTQ5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 149: the kernel wakes the worker at dawn",
        "cm91bmQgMTQ5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 149: service latency drops after the patch",
        "cm91bmQgMTQ5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 149: the library caches every vector it sees",
        "cm91bmQgMTQ5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 149: agents argue then the debate resolves",
        "cm91bmQgMTQ5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 149: the filter keeps only strong matches",
        "cm91bmQgMTQ5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 149: the model answers with a short reply",
        "cm91bmQgMTQ5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 149: the recorder stores the reasoning trace",
        "cm91bmQgMTQ5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 149: the angel watches the processor run",
        "cm91bmQgMTQ5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 149: angle of the vector decides the match",
        "cm91bmQgMTQ5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 149: the candle burns twice as long at night",
        "cm91bmQgMTQ5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 149: a mirror of the universe in one line",
        "cm91bmQgMTQ5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 149: the queue drains before the storm", "cm91bmQgMTQ5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
