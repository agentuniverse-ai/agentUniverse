"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten154kitten154", "a2l0dGVuMTU0a2l0dGVuMTU0"),
    ("kitten154sitting154", "a2l0dGVuMTU0c2l0dGluZzE1NA"),
    ("kitten154agent154", "a2l0dGVuMTU0YWdlbnQxNTQ"),
    ("kitten154angle154", "a2l0dGVuMTU0YW5nbGUxNTQ"),
    ("sitting154angle154", "c2l0dGluZzE1NGFuZ2xlMTU0"),
    ("sitting154universe154", "c2l0dGluZzE1NHVuaXZlcnNlMTU0"),
    ("sitting154memory154", "c2l0dGluZzE1NG1lbW9yeTE1NA"),
    ("sitting154stream154", "c2l0dGluZzE1NHN0cmVhbTE1NA"),
    ("agent154stream154", "YWdlbnQxNTRzdHJlYW0xNTQ"),
    ("agent154context154", "YWdlbnQxNTRjb250ZXh0MTU0"),
    ("agent154knowledge154", "YWdlbnQxNTRrbm93bGVkZ2UxNTQ"),
    ("agent154vector154", "YWdlbnQxNTR2ZWN0b3IxNTQ"),
    ("angle154vector154", "YW5nbGUxNTR2ZWN0b3IxNTQ"),
    ("angle154processor154", "YW5nbGUxNTRwcm9jZXNzb3IxNTQ"),
    ("angle154reasoning154", "YW5nbGUxNTRyZWFzb25pbmcxNTQ"),
    ("angle154machine154", "YW5nbGUxNTRtYWNoaW5lMTU0"),
    ("universe154machine154", "dW5pdmVyc2UxNTRtYWNoaW5lMTU0"),
    ("universe154learning154", "dW5pdmVyc2UxNTRsZWFybmluZzE1NA"),
    ("universe154model154", "dW5pdmVyc2UxNTRtb2RlbDE1NA"),
    ("universe154token154", "dW5pdmVyc2UxNTR0b2tlbjE1NA"),
    ("memory154token154", "bWVtb3J5MTU0dG9rZW4xNTQ"),
    ("memory154prompt154", "bWVtb3J5MTU0cHJvbXB0MTU0"),
    ("memory154session154", "bWVtb3J5MTU0c2Vzc2lvbjE1NA"),
    ("memory154library154", "bWVtb3J5MTU0bGlicmFyeTE1NA"),
    ("stream154library154", "c3RyZWFtMTU0bGlicmFyeTE1NA"),
    ("stream154service154", "c3RyZWFtMTU0c2VydmljZTE1NA"),
    ("stream154gateway154", "c3RyZWFtMTU0Z2F0ZXdheTE1NA"),
    ("stream154storage154", "c3RyZWFtMTU0c3RvcmFnZTE1NA"),
    ("context154storage154", "Y29udGV4dDE1NHN0b3JhZ2UxNTQ"),
    ("context154network154", "Y29udGV4dDE1NG5ldHdvcmsxNTQ"),
    ("context154latency154", "Y29udGV4dDE1NGxhdGVuY3kxNTQ"),
    ("context154buffer154", "Y29udGV4dDE1NGJ1ZmZlcjE1NA"),
    ("knowledge154buffer154", "a25vd2xlZGdlMTU0YnVmZmVyMTU0"),
    ("knowledge154queue154", "a25vd2xlZGdlMTU0cXVldWUxNTQ"),
    ("knowledge154worker154", "a25vd2xlZGdlMTU0d29ya2VyMTU0"),
    ("knowledge154kernel154", "a25vd2xlZGdlMTU0a2VybmVsMTU0"),
    ("vector154kernel154", "dmVjdG9yMTU0a2VybmVsMTU0"),
    ("vector154signal154", "dmVjdG9yMTU0c2lnbmFsMTU0"),
    ("vector154packet154", "dmVjdG9yMTU0cGFja2V0MTU0"),
    ("vector154router154", "dmVjdG9yMTU0cm91dGVyMTU0"),
    ("processor154router154", "cHJvY2Vzc29yMTU0cm91dGVyMTU0"),
    ("processor154cluster154", "cHJvY2Vzc29yMTU0Y2x1c3RlcjE1NA"),
    ("processor154mirror154", "cHJvY2Vzc29yMTU0bWlycm9yMTU0"),
    ("processor154filter154", "cHJvY2Vzc29yMTU0ZmlsdGVyMTU0"),
    ("reasoning154filter154", "cmVhc29uaW5nMTU0ZmlsdGVyMTU0"),
    ("reasoning154ranking154", "cmVhc29uaW5nMTU0cmFua2luZzE1NA"),
    ("reasoning154encoding154", "cmVhc29uaW5nMTU0ZW5jb2RpbmcxNTQ"),
    ("reasoning154mapping154", "cmVhc29uaW5nMTU0bWFwcGluZzE1NA"),
    ("machine154mapping154", "bWFjaGluZTE1NG1hcHBpbmcxNTQ"),
    ("machine154record154", "bWFjaGluZTE1NHJlY29yZDE1NA"),
    ("machine154candle154", "bWFjaGluZTE1NGNhbmRsZTE1NA"),
    ("machine154thread154", "bWFjaGluZTE1NHRocmVhZDE1NA"),
    ("learning154thread154", "bGVhcm5pbmcxNTR0aHJlYWQxNTQ"),
    ("learning154kitten154", "bGVhcm5pbmcxNTRraXR0ZW4xNTQ"),
    ("learning154sitting154", "bGVhcm5pbmcxNTRzaXR0aW5nMTU0"),
    ("learning154agent154", "bGVhcm5pbmcxNTRhZ2VudDE1NA"),
    ("model154agent154", "bW9kZWwxNTRhZ2VudDE1NA"),
    ("model154angle154", "bW9kZWwxNTRhbmdsZTE1NA"),
    ("model154universe154", "bW9kZWwxNTR1bml2ZXJzZTE1NA"),
    ("model154memory154", "bW9kZWwxNTRtZW1vcnkxNTQ"),
    ("token154memory154", "dG9rZW4xNTRtZW1vcnkxNTQ"),
    ("token154stream154", "dG9rZW4xNTRzdHJlYW0xNTQ"),
    ("token154context154", "dG9rZW4xNTRjb250ZXh0MTU0"),
    ("token154knowledge154", "dG9rZW4xNTRrbm93bGVkZ2UxNTQ"),
    ("prompt154knowledge154", "cHJvbXB0MTU0a25vd2xlZGdlMTU0"),
    ("prompt154vector154", "cHJvbXB0MTU0dmVjdG9yMTU0"),
    ("prompt154processor154", "cHJvbXB0MTU0cHJvY2Vzc29yMTU0"),
    ("prompt154reasoning154", "cHJvbXB0MTU0cmVhc29uaW5nMTU0"),
    ("session154reasoning154", "c2Vzc2lvbjE1NHJlYXNvbmluZzE1NA"),
    ("session154machine154", "c2Vzc2lvbjE1NG1hY2hpbmUxNTQ"),
    ("session154learning154", "c2Vzc2lvbjE1NGxlYXJuaW5nMTU0"),
    ("session154model154", "c2Vzc2lvbjE1NG1vZGVsMTU0"),
    ("library154model154", "bGlicmFyeTE1NG1vZGVsMTU0"),
    ("library154token154", "bGlicmFyeTE1NHRva2VuMTU0"),
    ("library154prompt154", "bGlicmFyeTE1NHByb21wdDE1NA"),
    ("library154session154", "bGlicmFyeTE1NHNlc3Npb24xNTQ"),
    ("service154session154", "c2VydmljZTE1NHNlc3Npb24xNTQ"),
    ("service154library154", "c2VydmljZTE1NGxpYnJhcnkxNTQ"),
    ("service154service154", "c2VydmljZTE1NHNlcnZpY2UxNTQ"),
    ("service154gateway154", "c2VydmljZTE1NGdhdGV3YXkxNTQ"),
    ("gateway154gateway154", "Z2F0ZXdheTE1NGdhdGV3YXkxNTQ"),
    ("gateway154storage154", "Z2F0ZXdheTE1NHN0b3JhZ2UxNTQ"),
    ("gateway154network154", "Z2F0ZXdheTE1NG5ldHdvcmsxNTQ"),
    ("gateway154latency154", "Z2F0ZXdheTE1NGxhdGVuY3kxNTQ"),
    ("storage154latency154", "c3RvcmFnZTE1NGxhdGVuY3kxNTQ"),
    ("storage154buffer154", "c3RvcmFnZTE1NGJ1ZmZlcjE1NA"),
    ("storage154queue154", "c3RvcmFnZTE1NHF1ZXVlMTU0"),
    ("storage154worker154", "c3RvcmFnZTE1NHdvcmtlcjE1NA"),
    ("network154worker154", "bmV0d29yazE1NHdvcmtlcjE1NA"),
    ("network154kernel154", "bmV0d29yazE1NGtlcm5lbDE1NA"),
    ("network154signal154", "bmV0d29yazE1NHNpZ25hbDE1NA"),
    ("network154packet154", "bmV0d29yazE1NHBhY2tldDE1NA"),
    ("latency154packet154", "bGF0ZW5jeTE1NHBhY2tldDE1NA"),
    ("latency154router154", "bGF0ZW5jeTE1NHJvdXRlcjE1NA"),
    ("latency154cluster154", "bGF0ZW5jeTE1NGNsdXN0ZXIxNTQ"),
    ("latency154mirror154", "bGF0ZW5jeTE1NG1pcnJvcjE1NA"),
    ("buffer154mirror154", "YnVmZmVyMTU0bWlycm9yMTU0"),
    ("buffer154filter154", "YnVmZmVyMTU0ZmlsdGVyMTU0"),
    ("buffer154ranking154", "YnVmZmVyMTU0cmFua2luZzE1NA"),
    ("buffer154encoding154", "YnVmZmVyMTU0ZW5jb2RpbmcxNTQ"),
    ("queue154encoding154", "cXVldWUxNTRlbmNvZGluZzE1NA"),
    ("queue154mapping154", "cXVldWUxNTRtYXBwaW5nMTU0"),
    ("queue154record154", "cXVldWUxNTRyZWNvcmQxNTQ"),
    ("queue154candle154", "cXVldWUxNTRjYW5kbGUxNTQ"),
    ("worker154candle154", "d29ya2VyMTU0Y2FuZGxlMTU0"),
    ("worker154thread154", "d29ya2VyMTU0dGhyZWFkMTU0"),
    ("worker154kitten154", "d29ya2VyMTU0a2l0dGVuMTU0"),
    ("worker154sitting154", "d29ya2VyMTU0c2l0dGluZzE1NA"),
    ("kernel154sitting154", "a2VybmVsMTU0c2l0dGluZzE1NA"),
    ("kernel154agent154", "a2VybmVsMTU0YWdlbnQxNTQ"),
    ("kernel154angle154", "a2VybmVsMTU0YW5nbGUxNTQ"),
    ("kernel154universe154", "a2VybmVsMTU0dW5pdmVyc2UxNTQ"),
    ("signal154universe154", "c2lnbmFsMTU0dW5pdmVyc2UxNTQ"),
    ("signal154memory154", "c2lnbmFsMTU0bWVtb3J5MTU0"),
    ("signal154stream154", "c2lnbmFsMTU0c3RyZWFtMTU0"),
    ("signal154context154", "c2lnbmFsMTU0Y29udGV4dDE1NA"),
    ("packet154context154", "cGFja2V0MTU0Y29udGV4dDE1NA"),
    ("packet154knowledge154", "cGFja2V0MTU0a25vd2xlZGdlMTU0"),
    ("packet154vector154", "cGFja2V0MTU0dmVjdG9yMTU0"),
    ("packet154processor154", "cGFja2V0MTU0cHJvY2Vzc29yMTU0"),
    ("router154processor154", "cm91dGVyMTU0cHJvY2Vzc29yMTU0"),
    ("router154reasoning154", "cm91dGVyMTU0cmVhc29uaW5nMTU0"),
    ("router154machine154", "cm91dGVyMTU0bWFjaGluZTE1NA"),
    ("router154learning154", "cm91dGVyMTU0bGVhcm5pbmcxNTQ"),
    ("cluster154learning154", "Y2x1c3RlcjE1NGxlYXJuaW5nMTU0"),
    ("cluster154model154", "Y2x1c3RlcjE1NG1vZGVsMTU0"),
    ("cluster154token154", "Y2x1c3RlcjE1NHRva2VuMTU0"),
    ("cluster154prompt154", "Y2x1c3RlcjE1NHByb21wdDE1NA"),
    ("mirror154prompt154", "bWlycm9yMTU0cHJvbXB0MTU0"),
    ("mirror154session154", "bWlycm9yMTU0c2Vzc2lvbjE1NA"),
    ("mirror154library154", "bWlycm9yMTU0bGlicmFyeTE1NA"),
    ("mirror154service154", "bWlycm9yMTU0c2VydmljZTE1NA"),
    ("filter154service154", "ZmlsdGVyMTU0c2VydmljZTE1NA"),
    ("filter154gateway154", "ZmlsdGVyMTU0Z2F0ZXdheTE1NA"),
    ("filter154storage154", "ZmlsdGVyMTU0c3RvcmFnZTE1NA"),
    ("filter154network154", "ZmlsdGVyMTU0bmV0d29yazE1NA"),
    ("ranking154network154", "cmFua2luZzE1NG5ldHdvcmsxNTQ"),
    ("ranking154latency154", "cmFua2luZzE1NGxhdGVuY3kxNTQ"),
    ("ranking154buffer154", "cmFua2luZzE1NGJ1ZmZlcjE1NA"),
    ("ranking154queue154", "cmFua2luZzE1NHF1ZXVlMTU0"),
    ("encoding154queue154", "ZW5jb2RpbmcxNTRxdWV1ZTE1NA"),
    ("encoding154worker154", "ZW5jb2RpbmcxNTR3b3JrZXIxNTQ"),
    ("encoding154kernel154", "ZW5jb2RpbmcxNTRrZXJuZWwxNTQ"),
    ("encoding154signal154", "ZW5jb2RpbmcxNTRzaWduYWwxNTQ"),
    ("mapping154signal154", "bWFwcGluZzE1NHNpZ25hbDE1NA"),
    ("mapping154packet154", "bWFwcGluZzE1NHBhY2tldDE1NA"),
    ("mapping154router154", "bWFwcGluZzE1NHJvdXRlcjE1NA"),
    ("mapping154cluster154", "bWFwcGluZzE1NGNsdXN0ZXIxNTQ"),
    ("record154cluster154", "cmVjb3JkMTU0Y2x1c3RlcjE1NA"),
    ("record154mirror154", "cmVjb3JkMTU0bWlycm9yMTU0"),
    ("record154filter154", "cmVjb3JkMTU0ZmlsdGVyMTU0"),
    ("record154ranking154", "cmVjb3JkMTU0cmFua2luZzE1NA"),
    ("candle154ranking154", "Y2FuZGxlMTU0cmFua2luZzE1NA"),
    ("candle154encoding154", "Y2FuZGxlMTU0ZW5jb2RpbmcxNTQ"),
    ("candle154mapping154", "Y2FuZGxlMTU0bWFwcGluZzE1NA"),
    ("candle154record154", "Y2FuZGxlMTU0cmVjb3JkMTU0"),
    ("thread154record154", "dGhyZWFkMTU0cmVjb3JkMTU0"),
    ("thread154candle154", "dGhyZWFkMTU0Y2FuZGxlMTU0"),
    ("thread154thread154", "dGhyZWFkMTU0dGhyZWFkMTU0"),
    ("thread154kitten154", "dGhyZWFkMTU0a2l0dGVuMTU0"),
    (
        "round 154: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTU0OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 154: agentuniverse is a framework for multi agents",
        "cm91bmQgMTU0OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 154: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTU0OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 154: the processor reads the record then stops",
        "cm91bmQgMTU0OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 154: a worker pulls the next task from the queue",
        "cm91bmQgMTU0OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 154: signals travel through the network layer",
        "cm91bmQgMTU0OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 154: the gateway routes each request by policy",
        "cm91bmQgMTU0OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 154: memory grows until the buffer is full",
        "cm91bmQgMTU0OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 154: the cluster mirrors every packet twice",
        "cm91bmQgMTU0OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 154: ranking uses tokens learned from the corpus",
        "cm91bmQgMTU0OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 154: a long session ends when the candle dies",
        "cm91bmQgMTU0OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 154: encode the prompt then map the result",
        "cm91bmQgMTU0OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 154: the kernel wakes the worker at dawn",
        "cm91bmQgMTU0OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 154: service latency drops after the patch",
        "cm91bmQgMTU0OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 154: the library caches every vector it sees",
        "cm91bmQgMTU0OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 154: agents argue then the debate resolves",
        "cm91bmQgMTU0OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 154: the filter keeps only strong matches",
        "cm91bmQgMTU0OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 154: the model answers with a short reply",
        "cm91bmQgMTU0OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 154: the recorder stores the reasoning trace",
        "cm91bmQgMTU0OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 154: the angel watches the processor run",
        "cm91bmQgMTU0OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 154: angle of the vector decides the match",
        "cm91bmQgMTU0OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 154: the candle burns twice as long at night",
        "cm91bmQgMTU0OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 154: a mirror of the universe in one line",
        "cm91bmQgMTU0OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 154: the queue drains before the storm", "cm91bmQgMTU0OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
