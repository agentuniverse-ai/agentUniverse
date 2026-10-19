"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten179kitten179", "a2l0dGVuMTc5a2l0dGVuMTc5"),
    ("kitten179sitting179", "a2l0dGVuMTc5c2l0dGluZzE3OQ"),
    ("kitten179agent179", "a2l0dGVuMTc5YWdlbnQxNzk"),
    ("kitten179angle179", "a2l0dGVuMTc5YW5nbGUxNzk"),
    ("sitting179angle179", "c2l0dGluZzE3OWFuZ2xlMTc5"),
    ("sitting179universe179", "c2l0dGluZzE3OXVuaXZlcnNlMTc5"),
    ("sitting179memory179", "c2l0dGluZzE3OW1lbW9yeTE3OQ"),
    ("sitting179stream179", "c2l0dGluZzE3OXN0cmVhbTE3OQ"),
    ("agent179stream179", "YWdlbnQxNzlzdHJlYW0xNzk"),
    ("agent179context179", "YWdlbnQxNzljb250ZXh0MTc5"),
    ("agent179knowledge179", "YWdlbnQxNzlrbm93bGVkZ2UxNzk"),
    ("agent179vector179", "YWdlbnQxNzl2ZWN0b3IxNzk"),
    ("angle179vector179", "YW5nbGUxNzl2ZWN0b3IxNzk"),
    ("angle179processor179", "YW5nbGUxNzlwcm9jZXNzb3IxNzk"),
    ("angle179reasoning179", "YW5nbGUxNzlyZWFzb25pbmcxNzk"),
    ("angle179machine179", "YW5nbGUxNzltYWNoaW5lMTc5"),
    ("universe179machine179", "dW5pdmVyc2UxNzltYWNoaW5lMTc5"),
    ("universe179learning179", "dW5pdmVyc2UxNzlsZWFybmluZzE3OQ"),
    ("universe179model179", "dW5pdmVyc2UxNzltb2RlbDE3OQ"),
    ("universe179token179", "dW5pdmVyc2UxNzl0b2tlbjE3OQ"),
    ("memory179token179", "bWVtb3J5MTc5dG9rZW4xNzk"),
    ("memory179prompt179", "bWVtb3J5MTc5cHJvbXB0MTc5"),
    ("memory179session179", "bWVtb3J5MTc5c2Vzc2lvbjE3OQ"),
    ("memory179library179", "bWVtb3J5MTc5bGlicmFyeTE3OQ"),
    ("stream179library179", "c3RyZWFtMTc5bGlicmFyeTE3OQ"),
    ("stream179service179", "c3RyZWFtMTc5c2VydmljZTE3OQ"),
    ("stream179gateway179", "c3RyZWFtMTc5Z2F0ZXdheTE3OQ"),
    ("stream179storage179", "c3RyZWFtMTc5c3RvcmFnZTE3OQ"),
    ("context179storage179", "Y29udGV4dDE3OXN0b3JhZ2UxNzk"),
    ("context179network179", "Y29udGV4dDE3OW5ldHdvcmsxNzk"),
    ("context179latency179", "Y29udGV4dDE3OWxhdGVuY3kxNzk"),
    ("context179buffer179", "Y29udGV4dDE3OWJ1ZmZlcjE3OQ"),
    ("knowledge179buffer179", "a25vd2xlZGdlMTc5YnVmZmVyMTc5"),
    ("knowledge179queue179", "a25vd2xlZGdlMTc5cXVldWUxNzk"),
    ("knowledge179worker179", "a25vd2xlZGdlMTc5d29ya2VyMTc5"),
    ("knowledge179kernel179", "a25vd2xlZGdlMTc5a2VybmVsMTc5"),
    ("vector179kernel179", "dmVjdG9yMTc5a2VybmVsMTc5"),
    ("vector179signal179", "dmVjdG9yMTc5c2lnbmFsMTc5"),
    ("vector179packet179", "dmVjdG9yMTc5cGFja2V0MTc5"),
    ("vector179router179", "dmVjdG9yMTc5cm91dGVyMTc5"),
    ("processor179router179", "cHJvY2Vzc29yMTc5cm91dGVyMTc5"),
    ("processor179cluster179", "cHJvY2Vzc29yMTc5Y2x1c3RlcjE3OQ"),
    ("processor179mirror179", "cHJvY2Vzc29yMTc5bWlycm9yMTc5"),
    ("processor179filter179", "cHJvY2Vzc29yMTc5ZmlsdGVyMTc5"),
    ("reasoning179filter179", "cmVhc29uaW5nMTc5ZmlsdGVyMTc5"),
    ("reasoning179ranking179", "cmVhc29uaW5nMTc5cmFua2luZzE3OQ"),
    ("reasoning179encoding179", "cmVhc29uaW5nMTc5ZW5jb2RpbmcxNzk"),
    ("reasoning179mapping179", "cmVhc29uaW5nMTc5bWFwcGluZzE3OQ"),
    ("machine179mapping179", "bWFjaGluZTE3OW1hcHBpbmcxNzk"),
    ("machine179record179", "bWFjaGluZTE3OXJlY29yZDE3OQ"),
    ("machine179candle179", "bWFjaGluZTE3OWNhbmRsZTE3OQ"),
    ("machine179thread179", "bWFjaGluZTE3OXRocmVhZDE3OQ"),
    ("learning179thread179", "bGVhcm5pbmcxNzl0aHJlYWQxNzk"),
    ("learning179kitten179", "bGVhcm5pbmcxNzlraXR0ZW4xNzk"),
    ("learning179sitting179", "bGVhcm5pbmcxNzlzaXR0aW5nMTc5"),
    ("learning179agent179", "bGVhcm5pbmcxNzlhZ2VudDE3OQ"),
    ("model179agent179", "bW9kZWwxNzlhZ2VudDE3OQ"),
    ("model179angle179", "bW9kZWwxNzlhbmdsZTE3OQ"),
    ("model179universe179", "bW9kZWwxNzl1bml2ZXJzZTE3OQ"),
    ("model179memory179", "bW9kZWwxNzltZW1vcnkxNzk"),
    ("token179memory179", "dG9rZW4xNzltZW1vcnkxNzk"),
    ("token179stream179", "dG9rZW4xNzlzdHJlYW0xNzk"),
    ("token179context179", "dG9rZW4xNzljb250ZXh0MTc5"),
    ("token179knowledge179", "dG9rZW4xNzlrbm93bGVkZ2UxNzk"),
    ("prompt179knowledge179", "cHJvbXB0MTc5a25vd2xlZGdlMTc5"),
    ("prompt179vector179", "cHJvbXB0MTc5dmVjdG9yMTc5"),
    ("prompt179processor179", "cHJvbXB0MTc5cHJvY2Vzc29yMTc5"),
    ("prompt179reasoning179", "cHJvbXB0MTc5cmVhc29uaW5nMTc5"),
    ("session179reasoning179", "c2Vzc2lvbjE3OXJlYXNvbmluZzE3OQ"),
    ("session179machine179", "c2Vzc2lvbjE3OW1hY2hpbmUxNzk"),
    ("session179learning179", "c2Vzc2lvbjE3OWxlYXJuaW5nMTc5"),
    ("session179model179", "c2Vzc2lvbjE3OW1vZGVsMTc5"),
    ("library179model179", "bGlicmFyeTE3OW1vZGVsMTc5"),
    ("library179token179", "bGlicmFyeTE3OXRva2VuMTc5"),
    ("library179prompt179", "bGlicmFyeTE3OXByb21wdDE3OQ"),
    ("library179session179", "bGlicmFyeTE3OXNlc3Npb24xNzk"),
    ("service179session179", "c2VydmljZTE3OXNlc3Npb24xNzk"),
    ("service179library179", "c2VydmljZTE3OWxpYnJhcnkxNzk"),
    ("service179service179", "c2VydmljZTE3OXNlcnZpY2UxNzk"),
    ("service179gateway179", "c2VydmljZTE3OWdhdGV3YXkxNzk"),
    ("gateway179gateway179", "Z2F0ZXdheTE3OWdhdGV3YXkxNzk"),
    ("gateway179storage179", "Z2F0ZXdheTE3OXN0b3JhZ2UxNzk"),
    ("gateway179network179", "Z2F0ZXdheTE3OW5ldHdvcmsxNzk"),
    ("gateway179latency179", "Z2F0ZXdheTE3OWxhdGVuY3kxNzk"),
    ("storage179latency179", "c3RvcmFnZTE3OWxhdGVuY3kxNzk"),
    ("storage179buffer179", "c3RvcmFnZTE3OWJ1ZmZlcjE3OQ"),
    ("storage179queue179", "c3RvcmFnZTE3OXF1ZXVlMTc5"),
    ("storage179worker179", "c3RvcmFnZTE3OXdvcmtlcjE3OQ"),
    ("network179worker179", "bmV0d29yazE3OXdvcmtlcjE3OQ"),
    ("network179kernel179", "bmV0d29yazE3OWtlcm5lbDE3OQ"),
    ("network179signal179", "bmV0d29yazE3OXNpZ25hbDE3OQ"),
    ("network179packet179", "bmV0d29yazE3OXBhY2tldDE3OQ"),
    ("latency179packet179", "bGF0ZW5jeTE3OXBhY2tldDE3OQ"),
    ("latency179router179", "bGF0ZW5jeTE3OXJvdXRlcjE3OQ"),
    ("latency179cluster179", "bGF0ZW5jeTE3OWNsdXN0ZXIxNzk"),
    ("latency179mirror179", "bGF0ZW5jeTE3OW1pcnJvcjE3OQ"),
    ("buffer179mirror179", "YnVmZmVyMTc5bWlycm9yMTc5"),
    ("buffer179filter179", "YnVmZmVyMTc5ZmlsdGVyMTc5"),
    ("buffer179ranking179", "YnVmZmVyMTc5cmFua2luZzE3OQ"),
    ("buffer179encoding179", "YnVmZmVyMTc5ZW5jb2RpbmcxNzk"),
    ("queue179encoding179", "cXVldWUxNzllbmNvZGluZzE3OQ"),
    ("queue179mapping179", "cXVldWUxNzltYXBwaW5nMTc5"),
    ("queue179record179", "cXVldWUxNzlyZWNvcmQxNzk"),
    ("queue179candle179", "cXVldWUxNzljYW5kbGUxNzk"),
    ("worker179candle179", "d29ya2VyMTc5Y2FuZGxlMTc5"),
    ("worker179thread179", "d29ya2VyMTc5dGhyZWFkMTc5"),
    ("worker179kitten179", "d29ya2VyMTc5a2l0dGVuMTc5"),
    ("worker179sitting179", "d29ya2VyMTc5c2l0dGluZzE3OQ"),
    ("kernel179sitting179", "a2VybmVsMTc5c2l0dGluZzE3OQ"),
    ("kernel179agent179", "a2VybmVsMTc5YWdlbnQxNzk"),
    ("kernel179angle179", "a2VybmVsMTc5YW5nbGUxNzk"),
    ("kernel179universe179", "a2VybmVsMTc5dW5pdmVyc2UxNzk"),
    ("signal179universe179", "c2lnbmFsMTc5dW5pdmVyc2UxNzk"),
    ("signal179memory179", "c2lnbmFsMTc5bWVtb3J5MTc5"),
    ("signal179stream179", "c2lnbmFsMTc5c3RyZWFtMTc5"),
    ("signal179context179", "c2lnbmFsMTc5Y29udGV4dDE3OQ"),
    ("packet179context179", "cGFja2V0MTc5Y29udGV4dDE3OQ"),
    ("packet179knowledge179", "cGFja2V0MTc5a25vd2xlZGdlMTc5"),
    ("packet179vector179", "cGFja2V0MTc5dmVjdG9yMTc5"),
    ("packet179processor179", "cGFja2V0MTc5cHJvY2Vzc29yMTc5"),
    ("router179processor179", "cm91dGVyMTc5cHJvY2Vzc29yMTc5"),
    ("router179reasoning179", "cm91dGVyMTc5cmVhc29uaW5nMTc5"),
    ("router179machine179", "cm91dGVyMTc5bWFjaGluZTE3OQ"),
    ("router179learning179", "cm91dGVyMTc5bGVhcm5pbmcxNzk"),
    ("cluster179learning179", "Y2x1c3RlcjE3OWxlYXJuaW5nMTc5"),
    ("cluster179model179", "Y2x1c3RlcjE3OW1vZGVsMTc5"),
    ("cluster179token179", "Y2x1c3RlcjE3OXRva2VuMTc5"),
    ("cluster179prompt179", "Y2x1c3RlcjE3OXByb21wdDE3OQ"),
    ("mirror179prompt179", "bWlycm9yMTc5cHJvbXB0MTc5"),
    ("mirror179session179", "bWlycm9yMTc5c2Vzc2lvbjE3OQ"),
    ("mirror179library179", "bWlycm9yMTc5bGlicmFyeTE3OQ"),
    ("mirror179service179", "bWlycm9yMTc5c2VydmljZTE3OQ"),
    ("filter179service179", "ZmlsdGVyMTc5c2VydmljZTE3OQ"),
    ("filter179gateway179", "ZmlsdGVyMTc5Z2F0ZXdheTE3OQ"),
    ("filter179storage179", "ZmlsdGVyMTc5c3RvcmFnZTE3OQ"),
    ("filter179network179", "ZmlsdGVyMTc5bmV0d29yazE3OQ"),
    ("ranking179network179", "cmFua2luZzE3OW5ldHdvcmsxNzk"),
    ("ranking179latency179", "cmFua2luZzE3OWxhdGVuY3kxNzk"),
    ("ranking179buffer179", "cmFua2luZzE3OWJ1ZmZlcjE3OQ"),
    ("ranking179queue179", "cmFua2luZzE3OXF1ZXVlMTc5"),
    ("encoding179queue179", "ZW5jb2RpbmcxNzlxdWV1ZTE3OQ"),
    ("encoding179worker179", "ZW5jb2RpbmcxNzl3b3JrZXIxNzk"),
    ("encoding179kernel179", "ZW5jb2RpbmcxNzlrZXJuZWwxNzk"),
    ("encoding179signal179", "ZW5jb2RpbmcxNzlzaWduYWwxNzk"),
    ("mapping179signal179", "bWFwcGluZzE3OXNpZ25hbDE3OQ"),
    ("mapping179packet179", "bWFwcGluZzE3OXBhY2tldDE3OQ"),
    ("mapping179router179", "bWFwcGluZzE3OXJvdXRlcjE3OQ"),
    ("mapping179cluster179", "bWFwcGluZzE3OWNsdXN0ZXIxNzk"),
    ("record179cluster179", "cmVjb3JkMTc5Y2x1c3RlcjE3OQ"),
    ("record179mirror179", "cmVjb3JkMTc5bWlycm9yMTc5"),
    ("record179filter179", "cmVjb3JkMTc5ZmlsdGVyMTc5"),
    ("record179ranking179", "cmVjb3JkMTc5cmFua2luZzE3OQ"),
    ("candle179ranking179", "Y2FuZGxlMTc5cmFua2luZzE3OQ"),
    ("candle179encoding179", "Y2FuZGxlMTc5ZW5jb2RpbmcxNzk"),
    ("candle179mapping179", "Y2FuZGxlMTc5bWFwcGluZzE3OQ"),
    ("candle179record179", "Y2FuZGxlMTc5cmVjb3JkMTc5"),
    ("thread179record179", "dGhyZWFkMTc5cmVjb3JkMTc5"),
    ("thread179candle179", "dGhyZWFkMTc5Y2FuZGxlMTc5"),
    ("thread179thread179", "dGhyZWFkMTc5dGhyZWFkMTc5"),
    ("thread179kitten179", "dGhyZWFkMTc5a2l0dGVuMTc5"),
    (
        "round 179: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTc5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 179: agentuniverse is a framework for multi agents",
        "cm91bmQgMTc5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 179: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTc5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 179: the processor reads the record then stops",
        "cm91bmQgMTc5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 179: a worker pulls the next task from the queue",
        "cm91bmQgMTc5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 179: signals travel through the network layer",
        "cm91bmQgMTc5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 179: the gateway routes each request by policy",
        "cm91bmQgMTc5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 179: memory grows until the buffer is full",
        "cm91bmQgMTc5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 179: the cluster mirrors every packet twice",
        "cm91bmQgMTc5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 179: ranking uses tokens learned from the corpus",
        "cm91bmQgMTc5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 179: a long session ends when the candle dies",
        "cm91bmQgMTc5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 179: encode the prompt then map the result",
        "cm91bmQgMTc5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 179: the kernel wakes the worker at dawn",
        "cm91bmQgMTc5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 179: service latency drops after the patch",
        "cm91bmQgMTc5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 179: the library caches every vector it sees",
        "cm91bmQgMTc5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 179: agents argue then the debate resolves",
        "cm91bmQgMTc5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 179: the filter keeps only strong matches",
        "cm91bmQgMTc5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 179: the model answers with a short reply",
        "cm91bmQgMTc5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 179: the recorder stores the reasoning trace",
        "cm91bmQgMTc5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 179: the angel watches the processor run",
        "cm91bmQgMTc5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 179: angle of the vector decides the match",
        "cm91bmQgMTc5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 179: the candle burns twice as long at night",
        "cm91bmQgMTc5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 179: a mirror of the universe in one line",
        "cm91bmQgMTc5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 179: the queue drains before the storm", "cm91bmQgMTc5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
