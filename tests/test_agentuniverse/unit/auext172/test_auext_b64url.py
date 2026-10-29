"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten172kitten172", "a2l0dGVuMTcya2l0dGVuMTcy"),
    ("kitten172sitting172", "a2l0dGVuMTcyc2l0dGluZzE3Mg"),
    ("kitten172agent172", "a2l0dGVuMTcyYWdlbnQxNzI"),
    ("kitten172angle172", "a2l0dGVuMTcyYW5nbGUxNzI"),
    ("sitting172angle172", "c2l0dGluZzE3MmFuZ2xlMTcy"),
    ("sitting172universe172", "c2l0dGluZzE3MnVuaXZlcnNlMTcy"),
    ("sitting172memory172", "c2l0dGluZzE3Mm1lbW9yeTE3Mg"),
    ("sitting172stream172", "c2l0dGluZzE3MnN0cmVhbTE3Mg"),
    ("agent172stream172", "YWdlbnQxNzJzdHJlYW0xNzI"),
    ("agent172context172", "YWdlbnQxNzJjb250ZXh0MTcy"),
    ("agent172knowledge172", "YWdlbnQxNzJrbm93bGVkZ2UxNzI"),
    ("agent172vector172", "YWdlbnQxNzJ2ZWN0b3IxNzI"),
    ("angle172vector172", "YW5nbGUxNzJ2ZWN0b3IxNzI"),
    ("angle172processor172", "YW5nbGUxNzJwcm9jZXNzb3IxNzI"),
    ("angle172reasoning172", "YW5nbGUxNzJyZWFzb25pbmcxNzI"),
    ("angle172machine172", "YW5nbGUxNzJtYWNoaW5lMTcy"),
    ("universe172machine172", "dW5pdmVyc2UxNzJtYWNoaW5lMTcy"),
    ("universe172learning172", "dW5pdmVyc2UxNzJsZWFybmluZzE3Mg"),
    ("universe172model172", "dW5pdmVyc2UxNzJtb2RlbDE3Mg"),
    ("universe172token172", "dW5pdmVyc2UxNzJ0b2tlbjE3Mg"),
    ("memory172token172", "bWVtb3J5MTcydG9rZW4xNzI"),
    ("memory172prompt172", "bWVtb3J5MTcycHJvbXB0MTcy"),
    ("memory172session172", "bWVtb3J5MTcyc2Vzc2lvbjE3Mg"),
    ("memory172library172", "bWVtb3J5MTcybGlicmFyeTE3Mg"),
    ("stream172library172", "c3RyZWFtMTcybGlicmFyeTE3Mg"),
    ("stream172service172", "c3RyZWFtMTcyc2VydmljZTE3Mg"),
    ("stream172gateway172", "c3RyZWFtMTcyZ2F0ZXdheTE3Mg"),
    ("stream172storage172", "c3RyZWFtMTcyc3RvcmFnZTE3Mg"),
    ("context172storage172", "Y29udGV4dDE3MnN0b3JhZ2UxNzI"),
    ("context172network172", "Y29udGV4dDE3Mm5ldHdvcmsxNzI"),
    ("context172latency172", "Y29udGV4dDE3MmxhdGVuY3kxNzI"),
    ("context172buffer172", "Y29udGV4dDE3MmJ1ZmZlcjE3Mg"),
    ("knowledge172buffer172", "a25vd2xlZGdlMTcyYnVmZmVyMTcy"),
    ("knowledge172queue172", "a25vd2xlZGdlMTcycXVldWUxNzI"),
    ("knowledge172worker172", "a25vd2xlZGdlMTcyd29ya2VyMTcy"),
    ("knowledge172kernel172", "a25vd2xlZGdlMTcya2VybmVsMTcy"),
    ("vector172kernel172", "dmVjdG9yMTcya2VybmVsMTcy"),
    ("vector172signal172", "dmVjdG9yMTcyc2lnbmFsMTcy"),
    ("vector172packet172", "dmVjdG9yMTcycGFja2V0MTcy"),
    ("vector172router172", "dmVjdG9yMTcycm91dGVyMTcy"),
    ("processor172router172", "cHJvY2Vzc29yMTcycm91dGVyMTcy"),
    ("processor172cluster172", "cHJvY2Vzc29yMTcyY2x1c3RlcjE3Mg"),
    ("processor172mirror172", "cHJvY2Vzc29yMTcybWlycm9yMTcy"),
    ("processor172filter172", "cHJvY2Vzc29yMTcyZmlsdGVyMTcy"),
    ("reasoning172filter172", "cmVhc29uaW5nMTcyZmlsdGVyMTcy"),
    ("reasoning172ranking172", "cmVhc29uaW5nMTcycmFua2luZzE3Mg"),
    ("reasoning172encoding172", "cmVhc29uaW5nMTcyZW5jb2RpbmcxNzI"),
    ("reasoning172mapping172", "cmVhc29uaW5nMTcybWFwcGluZzE3Mg"),
    ("machine172mapping172", "bWFjaGluZTE3Mm1hcHBpbmcxNzI"),
    ("machine172record172", "bWFjaGluZTE3MnJlY29yZDE3Mg"),
    ("machine172candle172", "bWFjaGluZTE3MmNhbmRsZTE3Mg"),
    ("machine172thread172", "bWFjaGluZTE3MnRocmVhZDE3Mg"),
    ("learning172thread172", "bGVhcm5pbmcxNzJ0aHJlYWQxNzI"),
    ("learning172kitten172", "bGVhcm5pbmcxNzJraXR0ZW4xNzI"),
    ("learning172sitting172", "bGVhcm5pbmcxNzJzaXR0aW5nMTcy"),
    ("learning172agent172", "bGVhcm5pbmcxNzJhZ2VudDE3Mg"),
    ("model172agent172", "bW9kZWwxNzJhZ2VudDE3Mg"),
    ("model172angle172", "bW9kZWwxNzJhbmdsZTE3Mg"),
    ("model172universe172", "bW9kZWwxNzJ1bml2ZXJzZTE3Mg"),
    ("model172memory172", "bW9kZWwxNzJtZW1vcnkxNzI"),
    ("token172memory172", "dG9rZW4xNzJtZW1vcnkxNzI"),
    ("token172stream172", "dG9rZW4xNzJzdHJlYW0xNzI"),
    ("token172context172", "dG9rZW4xNzJjb250ZXh0MTcy"),
    ("token172knowledge172", "dG9rZW4xNzJrbm93bGVkZ2UxNzI"),
    ("prompt172knowledge172", "cHJvbXB0MTcya25vd2xlZGdlMTcy"),
    ("prompt172vector172", "cHJvbXB0MTcydmVjdG9yMTcy"),
    ("prompt172processor172", "cHJvbXB0MTcycHJvY2Vzc29yMTcy"),
    ("prompt172reasoning172", "cHJvbXB0MTcycmVhc29uaW5nMTcy"),
    ("session172reasoning172", "c2Vzc2lvbjE3MnJlYXNvbmluZzE3Mg"),
    ("session172machine172", "c2Vzc2lvbjE3Mm1hY2hpbmUxNzI"),
    ("session172learning172", "c2Vzc2lvbjE3MmxlYXJuaW5nMTcy"),
    ("session172model172", "c2Vzc2lvbjE3Mm1vZGVsMTcy"),
    ("library172model172", "bGlicmFyeTE3Mm1vZGVsMTcy"),
    ("library172token172", "bGlicmFyeTE3MnRva2VuMTcy"),
    ("library172prompt172", "bGlicmFyeTE3MnByb21wdDE3Mg"),
    ("library172session172", "bGlicmFyeTE3MnNlc3Npb24xNzI"),
    ("service172session172", "c2VydmljZTE3MnNlc3Npb24xNzI"),
    ("service172library172", "c2VydmljZTE3MmxpYnJhcnkxNzI"),
    ("service172service172", "c2VydmljZTE3MnNlcnZpY2UxNzI"),
    ("service172gateway172", "c2VydmljZTE3MmdhdGV3YXkxNzI"),
    ("gateway172gateway172", "Z2F0ZXdheTE3MmdhdGV3YXkxNzI"),
    ("gateway172storage172", "Z2F0ZXdheTE3MnN0b3JhZ2UxNzI"),
    ("gateway172network172", "Z2F0ZXdheTE3Mm5ldHdvcmsxNzI"),
    ("gateway172latency172", "Z2F0ZXdheTE3MmxhdGVuY3kxNzI"),
    ("storage172latency172", "c3RvcmFnZTE3MmxhdGVuY3kxNzI"),
    ("storage172buffer172", "c3RvcmFnZTE3MmJ1ZmZlcjE3Mg"),
    ("storage172queue172", "c3RvcmFnZTE3MnF1ZXVlMTcy"),
    ("storage172worker172", "c3RvcmFnZTE3MndvcmtlcjE3Mg"),
    ("network172worker172", "bmV0d29yazE3MndvcmtlcjE3Mg"),
    ("network172kernel172", "bmV0d29yazE3Mmtlcm5lbDE3Mg"),
    ("network172signal172", "bmV0d29yazE3MnNpZ25hbDE3Mg"),
    ("network172packet172", "bmV0d29yazE3MnBhY2tldDE3Mg"),
    ("latency172packet172", "bGF0ZW5jeTE3MnBhY2tldDE3Mg"),
    ("latency172router172", "bGF0ZW5jeTE3MnJvdXRlcjE3Mg"),
    ("latency172cluster172", "bGF0ZW5jeTE3MmNsdXN0ZXIxNzI"),
    ("latency172mirror172", "bGF0ZW5jeTE3Mm1pcnJvcjE3Mg"),
    ("buffer172mirror172", "YnVmZmVyMTcybWlycm9yMTcy"),
    ("buffer172filter172", "YnVmZmVyMTcyZmlsdGVyMTcy"),
    ("buffer172ranking172", "YnVmZmVyMTcycmFua2luZzE3Mg"),
    ("buffer172encoding172", "YnVmZmVyMTcyZW5jb2RpbmcxNzI"),
    ("queue172encoding172", "cXVldWUxNzJlbmNvZGluZzE3Mg"),
    ("queue172mapping172", "cXVldWUxNzJtYXBwaW5nMTcy"),
    ("queue172record172", "cXVldWUxNzJyZWNvcmQxNzI"),
    ("queue172candle172", "cXVldWUxNzJjYW5kbGUxNzI"),
    ("worker172candle172", "d29ya2VyMTcyY2FuZGxlMTcy"),
    ("worker172thread172", "d29ya2VyMTcydGhyZWFkMTcy"),
    ("worker172kitten172", "d29ya2VyMTcya2l0dGVuMTcy"),
    ("worker172sitting172", "d29ya2VyMTcyc2l0dGluZzE3Mg"),
    ("kernel172sitting172", "a2VybmVsMTcyc2l0dGluZzE3Mg"),
    ("kernel172agent172", "a2VybmVsMTcyYWdlbnQxNzI"),
    ("kernel172angle172", "a2VybmVsMTcyYW5nbGUxNzI"),
    ("kernel172universe172", "a2VybmVsMTcydW5pdmVyc2UxNzI"),
    ("signal172universe172", "c2lnbmFsMTcydW5pdmVyc2UxNzI"),
    ("signal172memory172", "c2lnbmFsMTcybWVtb3J5MTcy"),
    ("signal172stream172", "c2lnbmFsMTcyc3RyZWFtMTcy"),
    ("signal172context172", "c2lnbmFsMTcyY29udGV4dDE3Mg"),
    ("packet172context172", "cGFja2V0MTcyY29udGV4dDE3Mg"),
    ("packet172knowledge172", "cGFja2V0MTcya25vd2xlZGdlMTcy"),
    ("packet172vector172", "cGFja2V0MTcydmVjdG9yMTcy"),
    ("packet172processor172", "cGFja2V0MTcycHJvY2Vzc29yMTcy"),
    ("router172processor172", "cm91dGVyMTcycHJvY2Vzc29yMTcy"),
    ("router172reasoning172", "cm91dGVyMTcycmVhc29uaW5nMTcy"),
    ("router172machine172", "cm91dGVyMTcybWFjaGluZTE3Mg"),
    ("router172learning172", "cm91dGVyMTcybGVhcm5pbmcxNzI"),
    ("cluster172learning172", "Y2x1c3RlcjE3MmxlYXJuaW5nMTcy"),
    ("cluster172model172", "Y2x1c3RlcjE3Mm1vZGVsMTcy"),
    ("cluster172token172", "Y2x1c3RlcjE3MnRva2VuMTcy"),
    ("cluster172prompt172", "Y2x1c3RlcjE3MnByb21wdDE3Mg"),
    ("mirror172prompt172", "bWlycm9yMTcycHJvbXB0MTcy"),
    ("mirror172session172", "bWlycm9yMTcyc2Vzc2lvbjE3Mg"),
    ("mirror172library172", "bWlycm9yMTcybGlicmFyeTE3Mg"),
    ("mirror172service172", "bWlycm9yMTcyc2VydmljZTE3Mg"),
    ("filter172service172", "ZmlsdGVyMTcyc2VydmljZTE3Mg"),
    ("filter172gateway172", "ZmlsdGVyMTcyZ2F0ZXdheTE3Mg"),
    ("filter172storage172", "ZmlsdGVyMTcyc3RvcmFnZTE3Mg"),
    ("filter172network172", "ZmlsdGVyMTcybmV0d29yazE3Mg"),
    ("ranking172network172", "cmFua2luZzE3Mm5ldHdvcmsxNzI"),
    ("ranking172latency172", "cmFua2luZzE3MmxhdGVuY3kxNzI"),
    ("ranking172buffer172", "cmFua2luZzE3MmJ1ZmZlcjE3Mg"),
    ("ranking172queue172", "cmFua2luZzE3MnF1ZXVlMTcy"),
    ("encoding172queue172", "ZW5jb2RpbmcxNzJxdWV1ZTE3Mg"),
    ("encoding172worker172", "ZW5jb2RpbmcxNzJ3b3JrZXIxNzI"),
    ("encoding172kernel172", "ZW5jb2RpbmcxNzJrZXJuZWwxNzI"),
    ("encoding172signal172", "ZW5jb2RpbmcxNzJzaWduYWwxNzI"),
    ("mapping172signal172", "bWFwcGluZzE3MnNpZ25hbDE3Mg"),
    ("mapping172packet172", "bWFwcGluZzE3MnBhY2tldDE3Mg"),
    ("mapping172router172", "bWFwcGluZzE3MnJvdXRlcjE3Mg"),
    ("mapping172cluster172", "bWFwcGluZzE3MmNsdXN0ZXIxNzI"),
    ("record172cluster172", "cmVjb3JkMTcyY2x1c3RlcjE3Mg"),
    ("record172mirror172", "cmVjb3JkMTcybWlycm9yMTcy"),
    ("record172filter172", "cmVjb3JkMTcyZmlsdGVyMTcy"),
    ("record172ranking172", "cmVjb3JkMTcycmFua2luZzE3Mg"),
    ("candle172ranking172", "Y2FuZGxlMTcycmFua2luZzE3Mg"),
    ("candle172encoding172", "Y2FuZGxlMTcyZW5jb2RpbmcxNzI"),
    ("candle172mapping172", "Y2FuZGxlMTcybWFwcGluZzE3Mg"),
    ("candle172record172", "Y2FuZGxlMTcycmVjb3JkMTcy"),
    ("thread172record172", "dGhyZWFkMTcycmVjb3JkMTcy"),
    ("thread172candle172", "dGhyZWFkMTcyY2FuZGxlMTcy"),
    ("thread172thread172", "dGhyZWFkMTcydGhyZWFkMTcy"),
    ("thread172kitten172", "dGhyZWFkMTcya2l0dGVuMTcy"),
    (
        "round 172: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTcyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 172: agentuniverse is a framework for multi agents",
        "cm91bmQgMTcyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 172: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTcyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 172: the processor reads the record then stops",
        "cm91bmQgMTcyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 172: a worker pulls the next task from the queue",
        "cm91bmQgMTcyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 172: signals travel through the network layer",
        "cm91bmQgMTcyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 172: the gateway routes each request by policy",
        "cm91bmQgMTcyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 172: memory grows until the buffer is full",
        "cm91bmQgMTcyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 172: the cluster mirrors every packet twice",
        "cm91bmQgMTcyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 172: ranking uses tokens learned from the corpus",
        "cm91bmQgMTcyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 172: a long session ends when the candle dies",
        "cm91bmQgMTcyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 172: encode the prompt then map the result",
        "cm91bmQgMTcyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 172: the kernel wakes the worker at dawn",
        "cm91bmQgMTcyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 172: service latency drops after the patch",
        "cm91bmQgMTcyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 172: the library caches every vector it sees",
        "cm91bmQgMTcyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 172: agents argue then the debate resolves",
        "cm91bmQgMTcyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 172: the filter keeps only strong matches",
        "cm91bmQgMTcyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 172: the model answers with a short reply",
        "cm91bmQgMTcyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 172: the recorder stores the reasoning trace",
        "cm91bmQgMTcyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 172: the angel watches the processor run",
        "cm91bmQgMTcyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 172: angle of the vector decides the match",
        "cm91bmQgMTcyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 172: the candle burns twice as long at night",
        "cm91bmQgMTcyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 172: a mirror of the universe in one line",
        "cm91bmQgMTcyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 172: the queue drains before the storm", "cm91bmQgMTcyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
