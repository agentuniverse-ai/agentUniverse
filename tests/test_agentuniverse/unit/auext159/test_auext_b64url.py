"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten159kitten159", "a2l0dGVuMTU5a2l0dGVuMTU5"),
    ("kitten159sitting159", "a2l0dGVuMTU5c2l0dGluZzE1OQ"),
    ("kitten159agent159", "a2l0dGVuMTU5YWdlbnQxNTk"),
    ("kitten159angle159", "a2l0dGVuMTU5YW5nbGUxNTk"),
    ("sitting159angle159", "c2l0dGluZzE1OWFuZ2xlMTU5"),
    ("sitting159universe159", "c2l0dGluZzE1OXVuaXZlcnNlMTU5"),
    ("sitting159memory159", "c2l0dGluZzE1OW1lbW9yeTE1OQ"),
    ("sitting159stream159", "c2l0dGluZzE1OXN0cmVhbTE1OQ"),
    ("agent159stream159", "YWdlbnQxNTlzdHJlYW0xNTk"),
    ("agent159context159", "YWdlbnQxNTljb250ZXh0MTU5"),
    ("agent159knowledge159", "YWdlbnQxNTlrbm93bGVkZ2UxNTk"),
    ("agent159vector159", "YWdlbnQxNTl2ZWN0b3IxNTk"),
    ("angle159vector159", "YW5nbGUxNTl2ZWN0b3IxNTk"),
    ("angle159processor159", "YW5nbGUxNTlwcm9jZXNzb3IxNTk"),
    ("angle159reasoning159", "YW5nbGUxNTlyZWFzb25pbmcxNTk"),
    ("angle159machine159", "YW5nbGUxNTltYWNoaW5lMTU5"),
    ("universe159machine159", "dW5pdmVyc2UxNTltYWNoaW5lMTU5"),
    ("universe159learning159", "dW5pdmVyc2UxNTlsZWFybmluZzE1OQ"),
    ("universe159model159", "dW5pdmVyc2UxNTltb2RlbDE1OQ"),
    ("universe159token159", "dW5pdmVyc2UxNTl0b2tlbjE1OQ"),
    ("memory159token159", "bWVtb3J5MTU5dG9rZW4xNTk"),
    ("memory159prompt159", "bWVtb3J5MTU5cHJvbXB0MTU5"),
    ("memory159session159", "bWVtb3J5MTU5c2Vzc2lvbjE1OQ"),
    ("memory159library159", "bWVtb3J5MTU5bGlicmFyeTE1OQ"),
    ("stream159library159", "c3RyZWFtMTU5bGlicmFyeTE1OQ"),
    ("stream159service159", "c3RyZWFtMTU5c2VydmljZTE1OQ"),
    ("stream159gateway159", "c3RyZWFtMTU5Z2F0ZXdheTE1OQ"),
    ("stream159storage159", "c3RyZWFtMTU5c3RvcmFnZTE1OQ"),
    ("context159storage159", "Y29udGV4dDE1OXN0b3JhZ2UxNTk"),
    ("context159network159", "Y29udGV4dDE1OW5ldHdvcmsxNTk"),
    ("context159latency159", "Y29udGV4dDE1OWxhdGVuY3kxNTk"),
    ("context159buffer159", "Y29udGV4dDE1OWJ1ZmZlcjE1OQ"),
    ("knowledge159buffer159", "a25vd2xlZGdlMTU5YnVmZmVyMTU5"),
    ("knowledge159queue159", "a25vd2xlZGdlMTU5cXVldWUxNTk"),
    ("knowledge159worker159", "a25vd2xlZGdlMTU5d29ya2VyMTU5"),
    ("knowledge159kernel159", "a25vd2xlZGdlMTU5a2VybmVsMTU5"),
    ("vector159kernel159", "dmVjdG9yMTU5a2VybmVsMTU5"),
    ("vector159signal159", "dmVjdG9yMTU5c2lnbmFsMTU5"),
    ("vector159packet159", "dmVjdG9yMTU5cGFja2V0MTU5"),
    ("vector159router159", "dmVjdG9yMTU5cm91dGVyMTU5"),
    ("processor159router159", "cHJvY2Vzc29yMTU5cm91dGVyMTU5"),
    ("processor159cluster159", "cHJvY2Vzc29yMTU5Y2x1c3RlcjE1OQ"),
    ("processor159mirror159", "cHJvY2Vzc29yMTU5bWlycm9yMTU5"),
    ("processor159filter159", "cHJvY2Vzc29yMTU5ZmlsdGVyMTU5"),
    ("reasoning159filter159", "cmVhc29uaW5nMTU5ZmlsdGVyMTU5"),
    ("reasoning159ranking159", "cmVhc29uaW5nMTU5cmFua2luZzE1OQ"),
    ("reasoning159encoding159", "cmVhc29uaW5nMTU5ZW5jb2RpbmcxNTk"),
    ("reasoning159mapping159", "cmVhc29uaW5nMTU5bWFwcGluZzE1OQ"),
    ("machine159mapping159", "bWFjaGluZTE1OW1hcHBpbmcxNTk"),
    ("machine159record159", "bWFjaGluZTE1OXJlY29yZDE1OQ"),
    ("machine159candle159", "bWFjaGluZTE1OWNhbmRsZTE1OQ"),
    ("machine159thread159", "bWFjaGluZTE1OXRocmVhZDE1OQ"),
    ("learning159thread159", "bGVhcm5pbmcxNTl0aHJlYWQxNTk"),
    ("learning159kitten159", "bGVhcm5pbmcxNTlraXR0ZW4xNTk"),
    ("learning159sitting159", "bGVhcm5pbmcxNTlzaXR0aW5nMTU5"),
    ("learning159agent159", "bGVhcm5pbmcxNTlhZ2VudDE1OQ"),
    ("model159agent159", "bW9kZWwxNTlhZ2VudDE1OQ"),
    ("model159angle159", "bW9kZWwxNTlhbmdsZTE1OQ"),
    ("model159universe159", "bW9kZWwxNTl1bml2ZXJzZTE1OQ"),
    ("model159memory159", "bW9kZWwxNTltZW1vcnkxNTk"),
    ("token159memory159", "dG9rZW4xNTltZW1vcnkxNTk"),
    ("token159stream159", "dG9rZW4xNTlzdHJlYW0xNTk"),
    ("token159context159", "dG9rZW4xNTljb250ZXh0MTU5"),
    ("token159knowledge159", "dG9rZW4xNTlrbm93bGVkZ2UxNTk"),
    ("prompt159knowledge159", "cHJvbXB0MTU5a25vd2xlZGdlMTU5"),
    ("prompt159vector159", "cHJvbXB0MTU5dmVjdG9yMTU5"),
    ("prompt159processor159", "cHJvbXB0MTU5cHJvY2Vzc29yMTU5"),
    ("prompt159reasoning159", "cHJvbXB0MTU5cmVhc29uaW5nMTU5"),
    ("session159reasoning159", "c2Vzc2lvbjE1OXJlYXNvbmluZzE1OQ"),
    ("session159machine159", "c2Vzc2lvbjE1OW1hY2hpbmUxNTk"),
    ("session159learning159", "c2Vzc2lvbjE1OWxlYXJuaW5nMTU5"),
    ("session159model159", "c2Vzc2lvbjE1OW1vZGVsMTU5"),
    ("library159model159", "bGlicmFyeTE1OW1vZGVsMTU5"),
    ("library159token159", "bGlicmFyeTE1OXRva2VuMTU5"),
    ("library159prompt159", "bGlicmFyeTE1OXByb21wdDE1OQ"),
    ("library159session159", "bGlicmFyeTE1OXNlc3Npb24xNTk"),
    ("service159session159", "c2VydmljZTE1OXNlc3Npb24xNTk"),
    ("service159library159", "c2VydmljZTE1OWxpYnJhcnkxNTk"),
    ("service159service159", "c2VydmljZTE1OXNlcnZpY2UxNTk"),
    ("service159gateway159", "c2VydmljZTE1OWdhdGV3YXkxNTk"),
    ("gateway159gateway159", "Z2F0ZXdheTE1OWdhdGV3YXkxNTk"),
    ("gateway159storage159", "Z2F0ZXdheTE1OXN0b3JhZ2UxNTk"),
    ("gateway159network159", "Z2F0ZXdheTE1OW5ldHdvcmsxNTk"),
    ("gateway159latency159", "Z2F0ZXdheTE1OWxhdGVuY3kxNTk"),
    ("storage159latency159", "c3RvcmFnZTE1OWxhdGVuY3kxNTk"),
    ("storage159buffer159", "c3RvcmFnZTE1OWJ1ZmZlcjE1OQ"),
    ("storage159queue159", "c3RvcmFnZTE1OXF1ZXVlMTU5"),
    ("storage159worker159", "c3RvcmFnZTE1OXdvcmtlcjE1OQ"),
    ("network159worker159", "bmV0d29yazE1OXdvcmtlcjE1OQ"),
    ("network159kernel159", "bmV0d29yazE1OWtlcm5lbDE1OQ"),
    ("network159signal159", "bmV0d29yazE1OXNpZ25hbDE1OQ"),
    ("network159packet159", "bmV0d29yazE1OXBhY2tldDE1OQ"),
    ("latency159packet159", "bGF0ZW5jeTE1OXBhY2tldDE1OQ"),
    ("latency159router159", "bGF0ZW5jeTE1OXJvdXRlcjE1OQ"),
    ("latency159cluster159", "bGF0ZW5jeTE1OWNsdXN0ZXIxNTk"),
    ("latency159mirror159", "bGF0ZW5jeTE1OW1pcnJvcjE1OQ"),
    ("buffer159mirror159", "YnVmZmVyMTU5bWlycm9yMTU5"),
    ("buffer159filter159", "YnVmZmVyMTU5ZmlsdGVyMTU5"),
    ("buffer159ranking159", "YnVmZmVyMTU5cmFua2luZzE1OQ"),
    ("buffer159encoding159", "YnVmZmVyMTU5ZW5jb2RpbmcxNTk"),
    ("queue159encoding159", "cXVldWUxNTllbmNvZGluZzE1OQ"),
    ("queue159mapping159", "cXVldWUxNTltYXBwaW5nMTU5"),
    ("queue159record159", "cXVldWUxNTlyZWNvcmQxNTk"),
    ("queue159candle159", "cXVldWUxNTljYW5kbGUxNTk"),
    ("worker159candle159", "d29ya2VyMTU5Y2FuZGxlMTU5"),
    ("worker159thread159", "d29ya2VyMTU5dGhyZWFkMTU5"),
    ("worker159kitten159", "d29ya2VyMTU5a2l0dGVuMTU5"),
    ("worker159sitting159", "d29ya2VyMTU5c2l0dGluZzE1OQ"),
    ("kernel159sitting159", "a2VybmVsMTU5c2l0dGluZzE1OQ"),
    ("kernel159agent159", "a2VybmVsMTU5YWdlbnQxNTk"),
    ("kernel159angle159", "a2VybmVsMTU5YW5nbGUxNTk"),
    ("kernel159universe159", "a2VybmVsMTU5dW5pdmVyc2UxNTk"),
    ("signal159universe159", "c2lnbmFsMTU5dW5pdmVyc2UxNTk"),
    ("signal159memory159", "c2lnbmFsMTU5bWVtb3J5MTU5"),
    ("signal159stream159", "c2lnbmFsMTU5c3RyZWFtMTU5"),
    ("signal159context159", "c2lnbmFsMTU5Y29udGV4dDE1OQ"),
    ("packet159context159", "cGFja2V0MTU5Y29udGV4dDE1OQ"),
    ("packet159knowledge159", "cGFja2V0MTU5a25vd2xlZGdlMTU5"),
    ("packet159vector159", "cGFja2V0MTU5dmVjdG9yMTU5"),
    ("packet159processor159", "cGFja2V0MTU5cHJvY2Vzc29yMTU5"),
    ("router159processor159", "cm91dGVyMTU5cHJvY2Vzc29yMTU5"),
    ("router159reasoning159", "cm91dGVyMTU5cmVhc29uaW5nMTU5"),
    ("router159machine159", "cm91dGVyMTU5bWFjaGluZTE1OQ"),
    ("router159learning159", "cm91dGVyMTU5bGVhcm5pbmcxNTk"),
    ("cluster159learning159", "Y2x1c3RlcjE1OWxlYXJuaW5nMTU5"),
    ("cluster159model159", "Y2x1c3RlcjE1OW1vZGVsMTU5"),
    ("cluster159token159", "Y2x1c3RlcjE1OXRva2VuMTU5"),
    ("cluster159prompt159", "Y2x1c3RlcjE1OXByb21wdDE1OQ"),
    ("mirror159prompt159", "bWlycm9yMTU5cHJvbXB0MTU5"),
    ("mirror159session159", "bWlycm9yMTU5c2Vzc2lvbjE1OQ"),
    ("mirror159library159", "bWlycm9yMTU5bGlicmFyeTE1OQ"),
    ("mirror159service159", "bWlycm9yMTU5c2VydmljZTE1OQ"),
    ("filter159service159", "ZmlsdGVyMTU5c2VydmljZTE1OQ"),
    ("filter159gateway159", "ZmlsdGVyMTU5Z2F0ZXdheTE1OQ"),
    ("filter159storage159", "ZmlsdGVyMTU5c3RvcmFnZTE1OQ"),
    ("filter159network159", "ZmlsdGVyMTU5bmV0d29yazE1OQ"),
    ("ranking159network159", "cmFua2luZzE1OW5ldHdvcmsxNTk"),
    ("ranking159latency159", "cmFua2luZzE1OWxhdGVuY3kxNTk"),
    ("ranking159buffer159", "cmFua2luZzE1OWJ1ZmZlcjE1OQ"),
    ("ranking159queue159", "cmFua2luZzE1OXF1ZXVlMTU5"),
    ("encoding159queue159", "ZW5jb2RpbmcxNTlxdWV1ZTE1OQ"),
    ("encoding159worker159", "ZW5jb2RpbmcxNTl3b3JrZXIxNTk"),
    ("encoding159kernel159", "ZW5jb2RpbmcxNTlrZXJuZWwxNTk"),
    ("encoding159signal159", "ZW5jb2RpbmcxNTlzaWduYWwxNTk"),
    ("mapping159signal159", "bWFwcGluZzE1OXNpZ25hbDE1OQ"),
    ("mapping159packet159", "bWFwcGluZzE1OXBhY2tldDE1OQ"),
    ("mapping159router159", "bWFwcGluZzE1OXJvdXRlcjE1OQ"),
    ("mapping159cluster159", "bWFwcGluZzE1OWNsdXN0ZXIxNTk"),
    ("record159cluster159", "cmVjb3JkMTU5Y2x1c3RlcjE1OQ"),
    ("record159mirror159", "cmVjb3JkMTU5bWlycm9yMTU5"),
    ("record159filter159", "cmVjb3JkMTU5ZmlsdGVyMTU5"),
    ("record159ranking159", "cmVjb3JkMTU5cmFua2luZzE1OQ"),
    ("candle159ranking159", "Y2FuZGxlMTU5cmFua2luZzE1OQ"),
    ("candle159encoding159", "Y2FuZGxlMTU5ZW5jb2RpbmcxNTk"),
    ("candle159mapping159", "Y2FuZGxlMTU5bWFwcGluZzE1OQ"),
    ("candle159record159", "Y2FuZGxlMTU5cmVjb3JkMTU5"),
    ("thread159record159", "dGhyZWFkMTU5cmVjb3JkMTU5"),
    ("thread159candle159", "dGhyZWFkMTU5Y2FuZGxlMTU5"),
    ("thread159thread159", "dGhyZWFkMTU5dGhyZWFkMTU5"),
    ("thread159kitten159", "dGhyZWFkMTU5a2l0dGVuMTU5"),
    (
        "round 159: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTU5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 159: agentuniverse is a framework for multi agents",
        "cm91bmQgMTU5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 159: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTU5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 159: the processor reads the record then stops",
        "cm91bmQgMTU5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 159: a worker pulls the next task from the queue",
        "cm91bmQgMTU5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 159: signals travel through the network layer",
        "cm91bmQgMTU5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 159: the gateway routes each request by policy",
        "cm91bmQgMTU5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 159: memory grows until the buffer is full",
        "cm91bmQgMTU5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 159: the cluster mirrors every packet twice",
        "cm91bmQgMTU5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 159: ranking uses tokens learned from the corpus",
        "cm91bmQgMTU5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 159: a long session ends when the candle dies",
        "cm91bmQgMTU5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 159: encode the prompt then map the result",
        "cm91bmQgMTU5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 159: the kernel wakes the worker at dawn",
        "cm91bmQgMTU5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 159: service latency drops after the patch",
        "cm91bmQgMTU5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 159: the library caches every vector it sees",
        "cm91bmQgMTU5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 159: agents argue then the debate resolves",
        "cm91bmQgMTU5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 159: the filter keeps only strong matches",
        "cm91bmQgMTU5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 159: the model answers with a short reply",
        "cm91bmQgMTU5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 159: the recorder stores the reasoning trace",
        "cm91bmQgMTU5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 159: the angel watches the processor run",
        "cm91bmQgMTU5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 159: angle of the vector decides the match",
        "cm91bmQgMTU5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 159: the candle burns twice as long at night",
        "cm91bmQgMTU5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 159: a mirror of the universe in one line",
        "cm91bmQgMTU5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 159: the queue drains before the storm", "cm91bmQgMTU5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
