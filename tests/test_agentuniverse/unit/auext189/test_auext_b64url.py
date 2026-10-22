"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten189kitten189", "a2l0dGVuMTg5a2l0dGVuMTg5"),
    ("kitten189sitting189", "a2l0dGVuMTg5c2l0dGluZzE4OQ"),
    ("kitten189agent189", "a2l0dGVuMTg5YWdlbnQxODk"),
    ("kitten189angle189", "a2l0dGVuMTg5YW5nbGUxODk"),
    ("sitting189angle189", "c2l0dGluZzE4OWFuZ2xlMTg5"),
    ("sitting189universe189", "c2l0dGluZzE4OXVuaXZlcnNlMTg5"),
    ("sitting189memory189", "c2l0dGluZzE4OW1lbW9yeTE4OQ"),
    ("sitting189stream189", "c2l0dGluZzE4OXN0cmVhbTE4OQ"),
    ("agent189stream189", "YWdlbnQxODlzdHJlYW0xODk"),
    ("agent189context189", "YWdlbnQxODljb250ZXh0MTg5"),
    ("agent189knowledge189", "YWdlbnQxODlrbm93bGVkZ2UxODk"),
    ("agent189vector189", "YWdlbnQxODl2ZWN0b3IxODk"),
    ("angle189vector189", "YW5nbGUxODl2ZWN0b3IxODk"),
    ("angle189processor189", "YW5nbGUxODlwcm9jZXNzb3IxODk"),
    ("angle189reasoning189", "YW5nbGUxODlyZWFzb25pbmcxODk"),
    ("angle189machine189", "YW5nbGUxODltYWNoaW5lMTg5"),
    ("universe189machine189", "dW5pdmVyc2UxODltYWNoaW5lMTg5"),
    ("universe189learning189", "dW5pdmVyc2UxODlsZWFybmluZzE4OQ"),
    ("universe189model189", "dW5pdmVyc2UxODltb2RlbDE4OQ"),
    ("universe189token189", "dW5pdmVyc2UxODl0b2tlbjE4OQ"),
    ("memory189token189", "bWVtb3J5MTg5dG9rZW4xODk"),
    ("memory189prompt189", "bWVtb3J5MTg5cHJvbXB0MTg5"),
    ("memory189session189", "bWVtb3J5MTg5c2Vzc2lvbjE4OQ"),
    ("memory189library189", "bWVtb3J5MTg5bGlicmFyeTE4OQ"),
    ("stream189library189", "c3RyZWFtMTg5bGlicmFyeTE4OQ"),
    ("stream189service189", "c3RyZWFtMTg5c2VydmljZTE4OQ"),
    ("stream189gateway189", "c3RyZWFtMTg5Z2F0ZXdheTE4OQ"),
    ("stream189storage189", "c3RyZWFtMTg5c3RvcmFnZTE4OQ"),
    ("context189storage189", "Y29udGV4dDE4OXN0b3JhZ2UxODk"),
    ("context189network189", "Y29udGV4dDE4OW5ldHdvcmsxODk"),
    ("context189latency189", "Y29udGV4dDE4OWxhdGVuY3kxODk"),
    ("context189buffer189", "Y29udGV4dDE4OWJ1ZmZlcjE4OQ"),
    ("knowledge189buffer189", "a25vd2xlZGdlMTg5YnVmZmVyMTg5"),
    ("knowledge189queue189", "a25vd2xlZGdlMTg5cXVldWUxODk"),
    ("knowledge189worker189", "a25vd2xlZGdlMTg5d29ya2VyMTg5"),
    ("knowledge189kernel189", "a25vd2xlZGdlMTg5a2VybmVsMTg5"),
    ("vector189kernel189", "dmVjdG9yMTg5a2VybmVsMTg5"),
    ("vector189signal189", "dmVjdG9yMTg5c2lnbmFsMTg5"),
    ("vector189packet189", "dmVjdG9yMTg5cGFja2V0MTg5"),
    ("vector189router189", "dmVjdG9yMTg5cm91dGVyMTg5"),
    ("processor189router189", "cHJvY2Vzc29yMTg5cm91dGVyMTg5"),
    ("processor189cluster189", "cHJvY2Vzc29yMTg5Y2x1c3RlcjE4OQ"),
    ("processor189mirror189", "cHJvY2Vzc29yMTg5bWlycm9yMTg5"),
    ("processor189filter189", "cHJvY2Vzc29yMTg5ZmlsdGVyMTg5"),
    ("reasoning189filter189", "cmVhc29uaW5nMTg5ZmlsdGVyMTg5"),
    ("reasoning189ranking189", "cmVhc29uaW5nMTg5cmFua2luZzE4OQ"),
    ("reasoning189encoding189", "cmVhc29uaW5nMTg5ZW5jb2RpbmcxODk"),
    ("reasoning189mapping189", "cmVhc29uaW5nMTg5bWFwcGluZzE4OQ"),
    ("machine189mapping189", "bWFjaGluZTE4OW1hcHBpbmcxODk"),
    ("machine189record189", "bWFjaGluZTE4OXJlY29yZDE4OQ"),
    ("machine189candle189", "bWFjaGluZTE4OWNhbmRsZTE4OQ"),
    ("machine189thread189", "bWFjaGluZTE4OXRocmVhZDE4OQ"),
    ("learning189thread189", "bGVhcm5pbmcxODl0aHJlYWQxODk"),
    ("learning189kitten189", "bGVhcm5pbmcxODlraXR0ZW4xODk"),
    ("learning189sitting189", "bGVhcm5pbmcxODlzaXR0aW5nMTg5"),
    ("learning189agent189", "bGVhcm5pbmcxODlhZ2VudDE4OQ"),
    ("model189agent189", "bW9kZWwxODlhZ2VudDE4OQ"),
    ("model189angle189", "bW9kZWwxODlhbmdsZTE4OQ"),
    ("model189universe189", "bW9kZWwxODl1bml2ZXJzZTE4OQ"),
    ("model189memory189", "bW9kZWwxODltZW1vcnkxODk"),
    ("token189memory189", "dG9rZW4xODltZW1vcnkxODk"),
    ("token189stream189", "dG9rZW4xODlzdHJlYW0xODk"),
    ("token189context189", "dG9rZW4xODljb250ZXh0MTg5"),
    ("token189knowledge189", "dG9rZW4xODlrbm93bGVkZ2UxODk"),
    ("prompt189knowledge189", "cHJvbXB0MTg5a25vd2xlZGdlMTg5"),
    ("prompt189vector189", "cHJvbXB0MTg5dmVjdG9yMTg5"),
    ("prompt189processor189", "cHJvbXB0MTg5cHJvY2Vzc29yMTg5"),
    ("prompt189reasoning189", "cHJvbXB0MTg5cmVhc29uaW5nMTg5"),
    ("session189reasoning189", "c2Vzc2lvbjE4OXJlYXNvbmluZzE4OQ"),
    ("session189machine189", "c2Vzc2lvbjE4OW1hY2hpbmUxODk"),
    ("session189learning189", "c2Vzc2lvbjE4OWxlYXJuaW5nMTg5"),
    ("session189model189", "c2Vzc2lvbjE4OW1vZGVsMTg5"),
    ("library189model189", "bGlicmFyeTE4OW1vZGVsMTg5"),
    ("library189token189", "bGlicmFyeTE4OXRva2VuMTg5"),
    ("library189prompt189", "bGlicmFyeTE4OXByb21wdDE4OQ"),
    ("library189session189", "bGlicmFyeTE4OXNlc3Npb24xODk"),
    ("service189session189", "c2VydmljZTE4OXNlc3Npb24xODk"),
    ("service189library189", "c2VydmljZTE4OWxpYnJhcnkxODk"),
    ("service189service189", "c2VydmljZTE4OXNlcnZpY2UxODk"),
    ("service189gateway189", "c2VydmljZTE4OWdhdGV3YXkxODk"),
    ("gateway189gateway189", "Z2F0ZXdheTE4OWdhdGV3YXkxODk"),
    ("gateway189storage189", "Z2F0ZXdheTE4OXN0b3JhZ2UxODk"),
    ("gateway189network189", "Z2F0ZXdheTE4OW5ldHdvcmsxODk"),
    ("gateway189latency189", "Z2F0ZXdheTE4OWxhdGVuY3kxODk"),
    ("storage189latency189", "c3RvcmFnZTE4OWxhdGVuY3kxODk"),
    ("storage189buffer189", "c3RvcmFnZTE4OWJ1ZmZlcjE4OQ"),
    ("storage189queue189", "c3RvcmFnZTE4OXF1ZXVlMTg5"),
    ("storage189worker189", "c3RvcmFnZTE4OXdvcmtlcjE4OQ"),
    ("network189worker189", "bmV0d29yazE4OXdvcmtlcjE4OQ"),
    ("network189kernel189", "bmV0d29yazE4OWtlcm5lbDE4OQ"),
    ("network189signal189", "bmV0d29yazE4OXNpZ25hbDE4OQ"),
    ("network189packet189", "bmV0d29yazE4OXBhY2tldDE4OQ"),
    ("latency189packet189", "bGF0ZW5jeTE4OXBhY2tldDE4OQ"),
    ("latency189router189", "bGF0ZW5jeTE4OXJvdXRlcjE4OQ"),
    ("latency189cluster189", "bGF0ZW5jeTE4OWNsdXN0ZXIxODk"),
    ("latency189mirror189", "bGF0ZW5jeTE4OW1pcnJvcjE4OQ"),
    ("buffer189mirror189", "YnVmZmVyMTg5bWlycm9yMTg5"),
    ("buffer189filter189", "YnVmZmVyMTg5ZmlsdGVyMTg5"),
    ("buffer189ranking189", "YnVmZmVyMTg5cmFua2luZzE4OQ"),
    ("buffer189encoding189", "YnVmZmVyMTg5ZW5jb2RpbmcxODk"),
    ("queue189encoding189", "cXVldWUxODllbmNvZGluZzE4OQ"),
    ("queue189mapping189", "cXVldWUxODltYXBwaW5nMTg5"),
    ("queue189record189", "cXVldWUxODlyZWNvcmQxODk"),
    ("queue189candle189", "cXVldWUxODljYW5kbGUxODk"),
    ("worker189candle189", "d29ya2VyMTg5Y2FuZGxlMTg5"),
    ("worker189thread189", "d29ya2VyMTg5dGhyZWFkMTg5"),
    ("worker189kitten189", "d29ya2VyMTg5a2l0dGVuMTg5"),
    ("worker189sitting189", "d29ya2VyMTg5c2l0dGluZzE4OQ"),
    ("kernel189sitting189", "a2VybmVsMTg5c2l0dGluZzE4OQ"),
    ("kernel189agent189", "a2VybmVsMTg5YWdlbnQxODk"),
    ("kernel189angle189", "a2VybmVsMTg5YW5nbGUxODk"),
    ("kernel189universe189", "a2VybmVsMTg5dW5pdmVyc2UxODk"),
    ("signal189universe189", "c2lnbmFsMTg5dW5pdmVyc2UxODk"),
    ("signal189memory189", "c2lnbmFsMTg5bWVtb3J5MTg5"),
    ("signal189stream189", "c2lnbmFsMTg5c3RyZWFtMTg5"),
    ("signal189context189", "c2lnbmFsMTg5Y29udGV4dDE4OQ"),
    ("packet189context189", "cGFja2V0MTg5Y29udGV4dDE4OQ"),
    ("packet189knowledge189", "cGFja2V0MTg5a25vd2xlZGdlMTg5"),
    ("packet189vector189", "cGFja2V0MTg5dmVjdG9yMTg5"),
    ("packet189processor189", "cGFja2V0MTg5cHJvY2Vzc29yMTg5"),
    ("router189processor189", "cm91dGVyMTg5cHJvY2Vzc29yMTg5"),
    ("router189reasoning189", "cm91dGVyMTg5cmVhc29uaW5nMTg5"),
    ("router189machine189", "cm91dGVyMTg5bWFjaGluZTE4OQ"),
    ("router189learning189", "cm91dGVyMTg5bGVhcm5pbmcxODk"),
    ("cluster189learning189", "Y2x1c3RlcjE4OWxlYXJuaW5nMTg5"),
    ("cluster189model189", "Y2x1c3RlcjE4OW1vZGVsMTg5"),
    ("cluster189token189", "Y2x1c3RlcjE4OXRva2VuMTg5"),
    ("cluster189prompt189", "Y2x1c3RlcjE4OXByb21wdDE4OQ"),
    ("mirror189prompt189", "bWlycm9yMTg5cHJvbXB0MTg5"),
    ("mirror189session189", "bWlycm9yMTg5c2Vzc2lvbjE4OQ"),
    ("mirror189library189", "bWlycm9yMTg5bGlicmFyeTE4OQ"),
    ("mirror189service189", "bWlycm9yMTg5c2VydmljZTE4OQ"),
    ("filter189service189", "ZmlsdGVyMTg5c2VydmljZTE4OQ"),
    ("filter189gateway189", "ZmlsdGVyMTg5Z2F0ZXdheTE4OQ"),
    ("filter189storage189", "ZmlsdGVyMTg5c3RvcmFnZTE4OQ"),
    ("filter189network189", "ZmlsdGVyMTg5bmV0d29yazE4OQ"),
    ("ranking189network189", "cmFua2luZzE4OW5ldHdvcmsxODk"),
    ("ranking189latency189", "cmFua2luZzE4OWxhdGVuY3kxODk"),
    ("ranking189buffer189", "cmFua2luZzE4OWJ1ZmZlcjE4OQ"),
    ("ranking189queue189", "cmFua2luZzE4OXF1ZXVlMTg5"),
    ("encoding189queue189", "ZW5jb2RpbmcxODlxdWV1ZTE4OQ"),
    ("encoding189worker189", "ZW5jb2RpbmcxODl3b3JrZXIxODk"),
    ("encoding189kernel189", "ZW5jb2RpbmcxODlrZXJuZWwxODk"),
    ("encoding189signal189", "ZW5jb2RpbmcxODlzaWduYWwxODk"),
    ("mapping189signal189", "bWFwcGluZzE4OXNpZ25hbDE4OQ"),
    ("mapping189packet189", "bWFwcGluZzE4OXBhY2tldDE4OQ"),
    ("mapping189router189", "bWFwcGluZzE4OXJvdXRlcjE4OQ"),
    ("mapping189cluster189", "bWFwcGluZzE4OWNsdXN0ZXIxODk"),
    ("record189cluster189", "cmVjb3JkMTg5Y2x1c3RlcjE4OQ"),
    ("record189mirror189", "cmVjb3JkMTg5bWlycm9yMTg5"),
    ("record189filter189", "cmVjb3JkMTg5ZmlsdGVyMTg5"),
    ("record189ranking189", "cmVjb3JkMTg5cmFua2luZzE4OQ"),
    ("candle189ranking189", "Y2FuZGxlMTg5cmFua2luZzE4OQ"),
    ("candle189encoding189", "Y2FuZGxlMTg5ZW5jb2RpbmcxODk"),
    ("candle189mapping189", "Y2FuZGxlMTg5bWFwcGluZzE4OQ"),
    ("candle189record189", "Y2FuZGxlMTg5cmVjb3JkMTg5"),
    ("thread189record189", "dGhyZWFkMTg5cmVjb3JkMTg5"),
    ("thread189candle189", "dGhyZWFkMTg5Y2FuZGxlMTg5"),
    ("thread189thread189", "dGhyZWFkMTg5dGhyZWFkMTg5"),
    ("thread189kitten189", "dGhyZWFkMTg5a2l0dGVuMTg5"),
    (
        "round 189: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTg5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 189: agentuniverse is a framework for multi agents",
        "cm91bmQgMTg5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 189: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTg5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 189: the processor reads the record then stops",
        "cm91bmQgMTg5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 189: a worker pulls the next task from the queue",
        "cm91bmQgMTg5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 189: signals travel through the network layer",
        "cm91bmQgMTg5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 189: the gateway routes each request by policy",
        "cm91bmQgMTg5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 189: memory grows until the buffer is full",
        "cm91bmQgMTg5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 189: the cluster mirrors every packet twice",
        "cm91bmQgMTg5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 189: ranking uses tokens learned from the corpus",
        "cm91bmQgMTg5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 189: a long session ends when the candle dies",
        "cm91bmQgMTg5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 189: encode the prompt then map the result",
        "cm91bmQgMTg5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 189: the kernel wakes the worker at dawn",
        "cm91bmQgMTg5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 189: service latency drops after the patch",
        "cm91bmQgMTg5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 189: the library caches every vector it sees",
        "cm91bmQgMTg5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 189: agents argue then the debate resolves",
        "cm91bmQgMTg5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 189: the filter keeps only strong matches",
        "cm91bmQgMTg5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 189: the model answers with a short reply",
        "cm91bmQgMTg5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 189: the recorder stores the reasoning trace",
        "cm91bmQgMTg5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 189: the angel watches the processor run",
        "cm91bmQgMTg5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 189: angle of the vector decides the match",
        "cm91bmQgMTg5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 189: the candle burns twice as long at night",
        "cm91bmQgMTg5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 189: a mirror of the universe in one line",
        "cm91bmQgMTg5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 189: the queue drains before the storm", "cm91bmQgMTg5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
