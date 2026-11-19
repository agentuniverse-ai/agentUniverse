"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten184kitten184", "a2l0dGVuMTg0a2l0dGVuMTg0"),
    ("kitten184sitting184", "a2l0dGVuMTg0c2l0dGluZzE4NA"),
    ("kitten184agent184", "a2l0dGVuMTg0YWdlbnQxODQ"),
    ("kitten184angle184", "a2l0dGVuMTg0YW5nbGUxODQ"),
    ("sitting184angle184", "c2l0dGluZzE4NGFuZ2xlMTg0"),
    ("sitting184universe184", "c2l0dGluZzE4NHVuaXZlcnNlMTg0"),
    ("sitting184memory184", "c2l0dGluZzE4NG1lbW9yeTE4NA"),
    ("sitting184stream184", "c2l0dGluZzE4NHN0cmVhbTE4NA"),
    ("agent184stream184", "YWdlbnQxODRzdHJlYW0xODQ"),
    ("agent184context184", "YWdlbnQxODRjb250ZXh0MTg0"),
    ("agent184knowledge184", "YWdlbnQxODRrbm93bGVkZ2UxODQ"),
    ("agent184vector184", "YWdlbnQxODR2ZWN0b3IxODQ"),
    ("angle184vector184", "YW5nbGUxODR2ZWN0b3IxODQ"),
    ("angle184processor184", "YW5nbGUxODRwcm9jZXNzb3IxODQ"),
    ("angle184reasoning184", "YW5nbGUxODRyZWFzb25pbmcxODQ"),
    ("angle184machine184", "YW5nbGUxODRtYWNoaW5lMTg0"),
    ("universe184machine184", "dW5pdmVyc2UxODRtYWNoaW5lMTg0"),
    ("universe184learning184", "dW5pdmVyc2UxODRsZWFybmluZzE4NA"),
    ("universe184model184", "dW5pdmVyc2UxODRtb2RlbDE4NA"),
    ("universe184token184", "dW5pdmVyc2UxODR0b2tlbjE4NA"),
    ("memory184token184", "bWVtb3J5MTg0dG9rZW4xODQ"),
    ("memory184prompt184", "bWVtb3J5MTg0cHJvbXB0MTg0"),
    ("memory184session184", "bWVtb3J5MTg0c2Vzc2lvbjE4NA"),
    ("memory184library184", "bWVtb3J5MTg0bGlicmFyeTE4NA"),
    ("stream184library184", "c3RyZWFtMTg0bGlicmFyeTE4NA"),
    ("stream184service184", "c3RyZWFtMTg0c2VydmljZTE4NA"),
    ("stream184gateway184", "c3RyZWFtMTg0Z2F0ZXdheTE4NA"),
    ("stream184storage184", "c3RyZWFtMTg0c3RvcmFnZTE4NA"),
    ("context184storage184", "Y29udGV4dDE4NHN0b3JhZ2UxODQ"),
    ("context184network184", "Y29udGV4dDE4NG5ldHdvcmsxODQ"),
    ("context184latency184", "Y29udGV4dDE4NGxhdGVuY3kxODQ"),
    ("context184buffer184", "Y29udGV4dDE4NGJ1ZmZlcjE4NA"),
    ("knowledge184buffer184", "a25vd2xlZGdlMTg0YnVmZmVyMTg0"),
    ("knowledge184queue184", "a25vd2xlZGdlMTg0cXVldWUxODQ"),
    ("knowledge184worker184", "a25vd2xlZGdlMTg0d29ya2VyMTg0"),
    ("knowledge184kernel184", "a25vd2xlZGdlMTg0a2VybmVsMTg0"),
    ("vector184kernel184", "dmVjdG9yMTg0a2VybmVsMTg0"),
    ("vector184signal184", "dmVjdG9yMTg0c2lnbmFsMTg0"),
    ("vector184packet184", "dmVjdG9yMTg0cGFja2V0MTg0"),
    ("vector184router184", "dmVjdG9yMTg0cm91dGVyMTg0"),
    ("processor184router184", "cHJvY2Vzc29yMTg0cm91dGVyMTg0"),
    ("processor184cluster184", "cHJvY2Vzc29yMTg0Y2x1c3RlcjE4NA"),
    ("processor184mirror184", "cHJvY2Vzc29yMTg0bWlycm9yMTg0"),
    ("processor184filter184", "cHJvY2Vzc29yMTg0ZmlsdGVyMTg0"),
    ("reasoning184filter184", "cmVhc29uaW5nMTg0ZmlsdGVyMTg0"),
    ("reasoning184ranking184", "cmVhc29uaW5nMTg0cmFua2luZzE4NA"),
    ("reasoning184encoding184", "cmVhc29uaW5nMTg0ZW5jb2RpbmcxODQ"),
    ("reasoning184mapping184", "cmVhc29uaW5nMTg0bWFwcGluZzE4NA"),
    ("machine184mapping184", "bWFjaGluZTE4NG1hcHBpbmcxODQ"),
    ("machine184record184", "bWFjaGluZTE4NHJlY29yZDE4NA"),
    ("machine184candle184", "bWFjaGluZTE4NGNhbmRsZTE4NA"),
    ("machine184thread184", "bWFjaGluZTE4NHRocmVhZDE4NA"),
    ("learning184thread184", "bGVhcm5pbmcxODR0aHJlYWQxODQ"),
    ("learning184kitten184", "bGVhcm5pbmcxODRraXR0ZW4xODQ"),
    ("learning184sitting184", "bGVhcm5pbmcxODRzaXR0aW5nMTg0"),
    ("learning184agent184", "bGVhcm5pbmcxODRhZ2VudDE4NA"),
    ("model184agent184", "bW9kZWwxODRhZ2VudDE4NA"),
    ("model184angle184", "bW9kZWwxODRhbmdsZTE4NA"),
    ("model184universe184", "bW9kZWwxODR1bml2ZXJzZTE4NA"),
    ("model184memory184", "bW9kZWwxODRtZW1vcnkxODQ"),
    ("token184memory184", "dG9rZW4xODRtZW1vcnkxODQ"),
    ("token184stream184", "dG9rZW4xODRzdHJlYW0xODQ"),
    ("token184context184", "dG9rZW4xODRjb250ZXh0MTg0"),
    ("token184knowledge184", "dG9rZW4xODRrbm93bGVkZ2UxODQ"),
    ("prompt184knowledge184", "cHJvbXB0MTg0a25vd2xlZGdlMTg0"),
    ("prompt184vector184", "cHJvbXB0MTg0dmVjdG9yMTg0"),
    ("prompt184processor184", "cHJvbXB0MTg0cHJvY2Vzc29yMTg0"),
    ("prompt184reasoning184", "cHJvbXB0MTg0cmVhc29uaW5nMTg0"),
    ("session184reasoning184", "c2Vzc2lvbjE4NHJlYXNvbmluZzE4NA"),
    ("session184machine184", "c2Vzc2lvbjE4NG1hY2hpbmUxODQ"),
    ("session184learning184", "c2Vzc2lvbjE4NGxlYXJuaW5nMTg0"),
    ("session184model184", "c2Vzc2lvbjE4NG1vZGVsMTg0"),
    ("library184model184", "bGlicmFyeTE4NG1vZGVsMTg0"),
    ("library184token184", "bGlicmFyeTE4NHRva2VuMTg0"),
    ("library184prompt184", "bGlicmFyeTE4NHByb21wdDE4NA"),
    ("library184session184", "bGlicmFyeTE4NHNlc3Npb24xODQ"),
    ("service184session184", "c2VydmljZTE4NHNlc3Npb24xODQ"),
    ("service184library184", "c2VydmljZTE4NGxpYnJhcnkxODQ"),
    ("service184service184", "c2VydmljZTE4NHNlcnZpY2UxODQ"),
    ("service184gateway184", "c2VydmljZTE4NGdhdGV3YXkxODQ"),
    ("gateway184gateway184", "Z2F0ZXdheTE4NGdhdGV3YXkxODQ"),
    ("gateway184storage184", "Z2F0ZXdheTE4NHN0b3JhZ2UxODQ"),
    ("gateway184network184", "Z2F0ZXdheTE4NG5ldHdvcmsxODQ"),
    ("gateway184latency184", "Z2F0ZXdheTE4NGxhdGVuY3kxODQ"),
    ("storage184latency184", "c3RvcmFnZTE4NGxhdGVuY3kxODQ"),
    ("storage184buffer184", "c3RvcmFnZTE4NGJ1ZmZlcjE4NA"),
    ("storage184queue184", "c3RvcmFnZTE4NHF1ZXVlMTg0"),
    ("storage184worker184", "c3RvcmFnZTE4NHdvcmtlcjE4NA"),
    ("network184worker184", "bmV0d29yazE4NHdvcmtlcjE4NA"),
    ("network184kernel184", "bmV0d29yazE4NGtlcm5lbDE4NA"),
    ("network184signal184", "bmV0d29yazE4NHNpZ25hbDE4NA"),
    ("network184packet184", "bmV0d29yazE4NHBhY2tldDE4NA"),
    ("latency184packet184", "bGF0ZW5jeTE4NHBhY2tldDE4NA"),
    ("latency184router184", "bGF0ZW5jeTE4NHJvdXRlcjE4NA"),
    ("latency184cluster184", "bGF0ZW5jeTE4NGNsdXN0ZXIxODQ"),
    ("latency184mirror184", "bGF0ZW5jeTE4NG1pcnJvcjE4NA"),
    ("buffer184mirror184", "YnVmZmVyMTg0bWlycm9yMTg0"),
    ("buffer184filter184", "YnVmZmVyMTg0ZmlsdGVyMTg0"),
    ("buffer184ranking184", "YnVmZmVyMTg0cmFua2luZzE4NA"),
    ("buffer184encoding184", "YnVmZmVyMTg0ZW5jb2RpbmcxODQ"),
    ("queue184encoding184", "cXVldWUxODRlbmNvZGluZzE4NA"),
    ("queue184mapping184", "cXVldWUxODRtYXBwaW5nMTg0"),
    ("queue184record184", "cXVldWUxODRyZWNvcmQxODQ"),
    ("queue184candle184", "cXVldWUxODRjYW5kbGUxODQ"),
    ("worker184candle184", "d29ya2VyMTg0Y2FuZGxlMTg0"),
    ("worker184thread184", "d29ya2VyMTg0dGhyZWFkMTg0"),
    ("worker184kitten184", "d29ya2VyMTg0a2l0dGVuMTg0"),
    ("worker184sitting184", "d29ya2VyMTg0c2l0dGluZzE4NA"),
    ("kernel184sitting184", "a2VybmVsMTg0c2l0dGluZzE4NA"),
    ("kernel184agent184", "a2VybmVsMTg0YWdlbnQxODQ"),
    ("kernel184angle184", "a2VybmVsMTg0YW5nbGUxODQ"),
    ("kernel184universe184", "a2VybmVsMTg0dW5pdmVyc2UxODQ"),
    ("signal184universe184", "c2lnbmFsMTg0dW5pdmVyc2UxODQ"),
    ("signal184memory184", "c2lnbmFsMTg0bWVtb3J5MTg0"),
    ("signal184stream184", "c2lnbmFsMTg0c3RyZWFtMTg0"),
    ("signal184context184", "c2lnbmFsMTg0Y29udGV4dDE4NA"),
    ("packet184context184", "cGFja2V0MTg0Y29udGV4dDE4NA"),
    ("packet184knowledge184", "cGFja2V0MTg0a25vd2xlZGdlMTg0"),
    ("packet184vector184", "cGFja2V0MTg0dmVjdG9yMTg0"),
    ("packet184processor184", "cGFja2V0MTg0cHJvY2Vzc29yMTg0"),
    ("router184processor184", "cm91dGVyMTg0cHJvY2Vzc29yMTg0"),
    ("router184reasoning184", "cm91dGVyMTg0cmVhc29uaW5nMTg0"),
    ("router184machine184", "cm91dGVyMTg0bWFjaGluZTE4NA"),
    ("router184learning184", "cm91dGVyMTg0bGVhcm5pbmcxODQ"),
    ("cluster184learning184", "Y2x1c3RlcjE4NGxlYXJuaW5nMTg0"),
    ("cluster184model184", "Y2x1c3RlcjE4NG1vZGVsMTg0"),
    ("cluster184token184", "Y2x1c3RlcjE4NHRva2VuMTg0"),
    ("cluster184prompt184", "Y2x1c3RlcjE4NHByb21wdDE4NA"),
    ("mirror184prompt184", "bWlycm9yMTg0cHJvbXB0MTg0"),
    ("mirror184session184", "bWlycm9yMTg0c2Vzc2lvbjE4NA"),
    ("mirror184library184", "bWlycm9yMTg0bGlicmFyeTE4NA"),
    ("mirror184service184", "bWlycm9yMTg0c2VydmljZTE4NA"),
    ("filter184service184", "ZmlsdGVyMTg0c2VydmljZTE4NA"),
    ("filter184gateway184", "ZmlsdGVyMTg0Z2F0ZXdheTE4NA"),
    ("filter184storage184", "ZmlsdGVyMTg0c3RvcmFnZTE4NA"),
    ("filter184network184", "ZmlsdGVyMTg0bmV0d29yazE4NA"),
    ("ranking184network184", "cmFua2luZzE4NG5ldHdvcmsxODQ"),
    ("ranking184latency184", "cmFua2luZzE4NGxhdGVuY3kxODQ"),
    ("ranking184buffer184", "cmFua2luZzE4NGJ1ZmZlcjE4NA"),
    ("ranking184queue184", "cmFua2luZzE4NHF1ZXVlMTg0"),
    ("encoding184queue184", "ZW5jb2RpbmcxODRxdWV1ZTE4NA"),
    ("encoding184worker184", "ZW5jb2RpbmcxODR3b3JrZXIxODQ"),
    ("encoding184kernel184", "ZW5jb2RpbmcxODRrZXJuZWwxODQ"),
    ("encoding184signal184", "ZW5jb2RpbmcxODRzaWduYWwxODQ"),
    ("mapping184signal184", "bWFwcGluZzE4NHNpZ25hbDE4NA"),
    ("mapping184packet184", "bWFwcGluZzE4NHBhY2tldDE4NA"),
    ("mapping184router184", "bWFwcGluZzE4NHJvdXRlcjE4NA"),
    ("mapping184cluster184", "bWFwcGluZzE4NGNsdXN0ZXIxODQ"),
    ("record184cluster184", "cmVjb3JkMTg0Y2x1c3RlcjE4NA"),
    ("record184mirror184", "cmVjb3JkMTg0bWlycm9yMTg0"),
    ("record184filter184", "cmVjb3JkMTg0ZmlsdGVyMTg0"),
    ("record184ranking184", "cmVjb3JkMTg0cmFua2luZzE4NA"),
    ("candle184ranking184", "Y2FuZGxlMTg0cmFua2luZzE4NA"),
    ("candle184encoding184", "Y2FuZGxlMTg0ZW5jb2RpbmcxODQ"),
    ("candle184mapping184", "Y2FuZGxlMTg0bWFwcGluZzE4NA"),
    ("candle184record184", "Y2FuZGxlMTg0cmVjb3JkMTg0"),
    ("thread184record184", "dGhyZWFkMTg0cmVjb3JkMTg0"),
    ("thread184candle184", "dGhyZWFkMTg0Y2FuZGxlMTg0"),
    ("thread184thread184", "dGhyZWFkMTg0dGhyZWFkMTg0"),
    ("thread184kitten184", "dGhyZWFkMTg0a2l0dGVuMTg0"),
    (
        "round 184: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTg0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 184: agentuniverse is a framework for multi agents",
        "cm91bmQgMTg0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 184: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTg0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 184: the processor reads the record then stops",
        "cm91bmQgMTg0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 184: a worker pulls the next task from the queue",
        "cm91bmQgMTg0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 184: signals travel through the network layer",
        "cm91bmQgMTg0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 184: the gateway routes each request by policy",
        "cm91bmQgMTg0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 184: memory grows until the buffer is full",
        "cm91bmQgMTg0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 184: the cluster mirrors every packet twice",
        "cm91bmQgMTg0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 184: ranking uses tokens learned from the corpus",
        "cm91bmQgMTg0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 184: a long session ends when the candle dies",
        "cm91bmQgMTg0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 184: encode the prompt then map the result",
        "cm91bmQgMTg0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 184: the kernel wakes the worker at dawn",
        "cm91bmQgMTg0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 184: service latency drops after the patch",
        "cm91bmQgMTg0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 184: the library caches every vector it sees",
        "cm91bmQgMTg0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 184: agents argue then the debate resolves",
        "cm91bmQgMTg0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 184: the filter keeps only strong matches",
        "cm91bmQgMTg0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 184: the model answers with a short reply",
        "cm91bmQgMTg0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 184: the recorder stores the reasoning trace",
        "cm91bmQgMTg0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 184: the angel watches the processor run",
        "cm91bmQgMTg0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 184: angle of the vector decides the match",
        "cm91bmQgMTg0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 184: the candle burns twice as long at night",
        "cm91bmQgMTg0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 184: a mirror of the universe in one line",
        "cm91bmQgMTg0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 184: the queue drains before the storm", "cm91bmQgMTg0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
