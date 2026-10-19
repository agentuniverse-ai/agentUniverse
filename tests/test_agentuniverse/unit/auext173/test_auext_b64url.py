"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten173kitten173", "a2l0dGVuMTcza2l0dGVuMTcz"),
    ("kitten173sitting173", "a2l0dGVuMTczc2l0dGluZzE3Mw"),
    ("kitten173agent173", "a2l0dGVuMTczYWdlbnQxNzM"),
    ("kitten173angle173", "a2l0dGVuMTczYW5nbGUxNzM"),
    ("sitting173angle173", "c2l0dGluZzE3M2FuZ2xlMTcz"),
    ("sitting173universe173", "c2l0dGluZzE3M3VuaXZlcnNlMTcz"),
    ("sitting173memory173", "c2l0dGluZzE3M21lbW9yeTE3Mw"),
    ("sitting173stream173", "c2l0dGluZzE3M3N0cmVhbTE3Mw"),
    ("agent173stream173", "YWdlbnQxNzNzdHJlYW0xNzM"),
    ("agent173context173", "YWdlbnQxNzNjb250ZXh0MTcz"),
    ("agent173knowledge173", "YWdlbnQxNzNrbm93bGVkZ2UxNzM"),
    ("agent173vector173", "YWdlbnQxNzN2ZWN0b3IxNzM"),
    ("angle173vector173", "YW5nbGUxNzN2ZWN0b3IxNzM"),
    ("angle173processor173", "YW5nbGUxNzNwcm9jZXNzb3IxNzM"),
    ("angle173reasoning173", "YW5nbGUxNzNyZWFzb25pbmcxNzM"),
    ("angle173machine173", "YW5nbGUxNzNtYWNoaW5lMTcz"),
    ("universe173machine173", "dW5pdmVyc2UxNzNtYWNoaW5lMTcz"),
    ("universe173learning173", "dW5pdmVyc2UxNzNsZWFybmluZzE3Mw"),
    ("universe173model173", "dW5pdmVyc2UxNzNtb2RlbDE3Mw"),
    ("universe173token173", "dW5pdmVyc2UxNzN0b2tlbjE3Mw"),
    ("memory173token173", "bWVtb3J5MTczdG9rZW4xNzM"),
    ("memory173prompt173", "bWVtb3J5MTczcHJvbXB0MTcz"),
    ("memory173session173", "bWVtb3J5MTczc2Vzc2lvbjE3Mw"),
    ("memory173library173", "bWVtb3J5MTczbGlicmFyeTE3Mw"),
    ("stream173library173", "c3RyZWFtMTczbGlicmFyeTE3Mw"),
    ("stream173service173", "c3RyZWFtMTczc2VydmljZTE3Mw"),
    ("stream173gateway173", "c3RyZWFtMTczZ2F0ZXdheTE3Mw"),
    ("stream173storage173", "c3RyZWFtMTczc3RvcmFnZTE3Mw"),
    ("context173storage173", "Y29udGV4dDE3M3N0b3JhZ2UxNzM"),
    ("context173network173", "Y29udGV4dDE3M25ldHdvcmsxNzM"),
    ("context173latency173", "Y29udGV4dDE3M2xhdGVuY3kxNzM"),
    ("context173buffer173", "Y29udGV4dDE3M2J1ZmZlcjE3Mw"),
    ("knowledge173buffer173", "a25vd2xlZGdlMTczYnVmZmVyMTcz"),
    ("knowledge173queue173", "a25vd2xlZGdlMTczcXVldWUxNzM"),
    ("knowledge173worker173", "a25vd2xlZGdlMTczd29ya2VyMTcz"),
    ("knowledge173kernel173", "a25vd2xlZGdlMTcza2VybmVsMTcz"),
    ("vector173kernel173", "dmVjdG9yMTcza2VybmVsMTcz"),
    ("vector173signal173", "dmVjdG9yMTczc2lnbmFsMTcz"),
    ("vector173packet173", "dmVjdG9yMTczcGFja2V0MTcz"),
    ("vector173router173", "dmVjdG9yMTczcm91dGVyMTcz"),
    ("processor173router173", "cHJvY2Vzc29yMTczcm91dGVyMTcz"),
    ("processor173cluster173", "cHJvY2Vzc29yMTczY2x1c3RlcjE3Mw"),
    ("processor173mirror173", "cHJvY2Vzc29yMTczbWlycm9yMTcz"),
    ("processor173filter173", "cHJvY2Vzc29yMTczZmlsdGVyMTcz"),
    ("reasoning173filter173", "cmVhc29uaW5nMTczZmlsdGVyMTcz"),
    ("reasoning173ranking173", "cmVhc29uaW5nMTczcmFua2luZzE3Mw"),
    ("reasoning173encoding173", "cmVhc29uaW5nMTczZW5jb2RpbmcxNzM"),
    ("reasoning173mapping173", "cmVhc29uaW5nMTczbWFwcGluZzE3Mw"),
    ("machine173mapping173", "bWFjaGluZTE3M21hcHBpbmcxNzM"),
    ("machine173record173", "bWFjaGluZTE3M3JlY29yZDE3Mw"),
    ("machine173candle173", "bWFjaGluZTE3M2NhbmRsZTE3Mw"),
    ("machine173thread173", "bWFjaGluZTE3M3RocmVhZDE3Mw"),
    ("learning173thread173", "bGVhcm5pbmcxNzN0aHJlYWQxNzM"),
    ("learning173kitten173", "bGVhcm5pbmcxNzNraXR0ZW4xNzM"),
    ("learning173sitting173", "bGVhcm5pbmcxNzNzaXR0aW5nMTcz"),
    ("learning173agent173", "bGVhcm5pbmcxNzNhZ2VudDE3Mw"),
    ("model173agent173", "bW9kZWwxNzNhZ2VudDE3Mw"),
    ("model173angle173", "bW9kZWwxNzNhbmdsZTE3Mw"),
    ("model173universe173", "bW9kZWwxNzN1bml2ZXJzZTE3Mw"),
    ("model173memory173", "bW9kZWwxNzNtZW1vcnkxNzM"),
    ("token173memory173", "dG9rZW4xNzNtZW1vcnkxNzM"),
    ("token173stream173", "dG9rZW4xNzNzdHJlYW0xNzM"),
    ("token173context173", "dG9rZW4xNzNjb250ZXh0MTcz"),
    ("token173knowledge173", "dG9rZW4xNzNrbm93bGVkZ2UxNzM"),
    ("prompt173knowledge173", "cHJvbXB0MTcza25vd2xlZGdlMTcz"),
    ("prompt173vector173", "cHJvbXB0MTczdmVjdG9yMTcz"),
    ("prompt173processor173", "cHJvbXB0MTczcHJvY2Vzc29yMTcz"),
    ("prompt173reasoning173", "cHJvbXB0MTczcmVhc29uaW5nMTcz"),
    ("session173reasoning173", "c2Vzc2lvbjE3M3JlYXNvbmluZzE3Mw"),
    ("session173machine173", "c2Vzc2lvbjE3M21hY2hpbmUxNzM"),
    ("session173learning173", "c2Vzc2lvbjE3M2xlYXJuaW5nMTcz"),
    ("session173model173", "c2Vzc2lvbjE3M21vZGVsMTcz"),
    ("library173model173", "bGlicmFyeTE3M21vZGVsMTcz"),
    ("library173token173", "bGlicmFyeTE3M3Rva2VuMTcz"),
    ("library173prompt173", "bGlicmFyeTE3M3Byb21wdDE3Mw"),
    ("library173session173", "bGlicmFyeTE3M3Nlc3Npb24xNzM"),
    ("service173session173", "c2VydmljZTE3M3Nlc3Npb24xNzM"),
    ("service173library173", "c2VydmljZTE3M2xpYnJhcnkxNzM"),
    ("service173service173", "c2VydmljZTE3M3NlcnZpY2UxNzM"),
    ("service173gateway173", "c2VydmljZTE3M2dhdGV3YXkxNzM"),
    ("gateway173gateway173", "Z2F0ZXdheTE3M2dhdGV3YXkxNzM"),
    ("gateway173storage173", "Z2F0ZXdheTE3M3N0b3JhZ2UxNzM"),
    ("gateway173network173", "Z2F0ZXdheTE3M25ldHdvcmsxNzM"),
    ("gateway173latency173", "Z2F0ZXdheTE3M2xhdGVuY3kxNzM"),
    ("storage173latency173", "c3RvcmFnZTE3M2xhdGVuY3kxNzM"),
    ("storage173buffer173", "c3RvcmFnZTE3M2J1ZmZlcjE3Mw"),
    ("storage173queue173", "c3RvcmFnZTE3M3F1ZXVlMTcz"),
    ("storage173worker173", "c3RvcmFnZTE3M3dvcmtlcjE3Mw"),
    ("network173worker173", "bmV0d29yazE3M3dvcmtlcjE3Mw"),
    ("network173kernel173", "bmV0d29yazE3M2tlcm5lbDE3Mw"),
    ("network173signal173", "bmV0d29yazE3M3NpZ25hbDE3Mw"),
    ("network173packet173", "bmV0d29yazE3M3BhY2tldDE3Mw"),
    ("latency173packet173", "bGF0ZW5jeTE3M3BhY2tldDE3Mw"),
    ("latency173router173", "bGF0ZW5jeTE3M3JvdXRlcjE3Mw"),
    ("latency173cluster173", "bGF0ZW5jeTE3M2NsdXN0ZXIxNzM"),
    ("latency173mirror173", "bGF0ZW5jeTE3M21pcnJvcjE3Mw"),
    ("buffer173mirror173", "YnVmZmVyMTczbWlycm9yMTcz"),
    ("buffer173filter173", "YnVmZmVyMTczZmlsdGVyMTcz"),
    ("buffer173ranking173", "YnVmZmVyMTczcmFua2luZzE3Mw"),
    ("buffer173encoding173", "YnVmZmVyMTczZW5jb2RpbmcxNzM"),
    ("queue173encoding173", "cXVldWUxNzNlbmNvZGluZzE3Mw"),
    ("queue173mapping173", "cXVldWUxNzNtYXBwaW5nMTcz"),
    ("queue173record173", "cXVldWUxNzNyZWNvcmQxNzM"),
    ("queue173candle173", "cXVldWUxNzNjYW5kbGUxNzM"),
    ("worker173candle173", "d29ya2VyMTczY2FuZGxlMTcz"),
    ("worker173thread173", "d29ya2VyMTczdGhyZWFkMTcz"),
    ("worker173kitten173", "d29ya2VyMTcza2l0dGVuMTcz"),
    ("worker173sitting173", "d29ya2VyMTczc2l0dGluZzE3Mw"),
    ("kernel173sitting173", "a2VybmVsMTczc2l0dGluZzE3Mw"),
    ("kernel173agent173", "a2VybmVsMTczYWdlbnQxNzM"),
    ("kernel173angle173", "a2VybmVsMTczYW5nbGUxNzM"),
    ("kernel173universe173", "a2VybmVsMTczdW5pdmVyc2UxNzM"),
    ("signal173universe173", "c2lnbmFsMTczdW5pdmVyc2UxNzM"),
    ("signal173memory173", "c2lnbmFsMTczbWVtb3J5MTcz"),
    ("signal173stream173", "c2lnbmFsMTczc3RyZWFtMTcz"),
    ("signal173context173", "c2lnbmFsMTczY29udGV4dDE3Mw"),
    ("packet173context173", "cGFja2V0MTczY29udGV4dDE3Mw"),
    ("packet173knowledge173", "cGFja2V0MTcza25vd2xlZGdlMTcz"),
    ("packet173vector173", "cGFja2V0MTczdmVjdG9yMTcz"),
    ("packet173processor173", "cGFja2V0MTczcHJvY2Vzc29yMTcz"),
    ("router173processor173", "cm91dGVyMTczcHJvY2Vzc29yMTcz"),
    ("router173reasoning173", "cm91dGVyMTczcmVhc29uaW5nMTcz"),
    ("router173machine173", "cm91dGVyMTczbWFjaGluZTE3Mw"),
    ("router173learning173", "cm91dGVyMTczbGVhcm5pbmcxNzM"),
    ("cluster173learning173", "Y2x1c3RlcjE3M2xlYXJuaW5nMTcz"),
    ("cluster173model173", "Y2x1c3RlcjE3M21vZGVsMTcz"),
    ("cluster173token173", "Y2x1c3RlcjE3M3Rva2VuMTcz"),
    ("cluster173prompt173", "Y2x1c3RlcjE3M3Byb21wdDE3Mw"),
    ("mirror173prompt173", "bWlycm9yMTczcHJvbXB0MTcz"),
    ("mirror173session173", "bWlycm9yMTczc2Vzc2lvbjE3Mw"),
    ("mirror173library173", "bWlycm9yMTczbGlicmFyeTE3Mw"),
    ("mirror173service173", "bWlycm9yMTczc2VydmljZTE3Mw"),
    ("filter173service173", "ZmlsdGVyMTczc2VydmljZTE3Mw"),
    ("filter173gateway173", "ZmlsdGVyMTczZ2F0ZXdheTE3Mw"),
    ("filter173storage173", "ZmlsdGVyMTczc3RvcmFnZTE3Mw"),
    ("filter173network173", "ZmlsdGVyMTczbmV0d29yazE3Mw"),
    ("ranking173network173", "cmFua2luZzE3M25ldHdvcmsxNzM"),
    ("ranking173latency173", "cmFua2luZzE3M2xhdGVuY3kxNzM"),
    ("ranking173buffer173", "cmFua2luZzE3M2J1ZmZlcjE3Mw"),
    ("ranking173queue173", "cmFua2luZzE3M3F1ZXVlMTcz"),
    ("encoding173queue173", "ZW5jb2RpbmcxNzNxdWV1ZTE3Mw"),
    ("encoding173worker173", "ZW5jb2RpbmcxNzN3b3JrZXIxNzM"),
    ("encoding173kernel173", "ZW5jb2RpbmcxNzNrZXJuZWwxNzM"),
    ("encoding173signal173", "ZW5jb2RpbmcxNzNzaWduYWwxNzM"),
    ("mapping173signal173", "bWFwcGluZzE3M3NpZ25hbDE3Mw"),
    ("mapping173packet173", "bWFwcGluZzE3M3BhY2tldDE3Mw"),
    ("mapping173router173", "bWFwcGluZzE3M3JvdXRlcjE3Mw"),
    ("mapping173cluster173", "bWFwcGluZzE3M2NsdXN0ZXIxNzM"),
    ("record173cluster173", "cmVjb3JkMTczY2x1c3RlcjE3Mw"),
    ("record173mirror173", "cmVjb3JkMTczbWlycm9yMTcz"),
    ("record173filter173", "cmVjb3JkMTczZmlsdGVyMTcz"),
    ("record173ranking173", "cmVjb3JkMTczcmFua2luZzE3Mw"),
    ("candle173ranking173", "Y2FuZGxlMTczcmFua2luZzE3Mw"),
    ("candle173encoding173", "Y2FuZGxlMTczZW5jb2RpbmcxNzM"),
    ("candle173mapping173", "Y2FuZGxlMTczbWFwcGluZzE3Mw"),
    ("candle173record173", "Y2FuZGxlMTczcmVjb3JkMTcz"),
    ("thread173record173", "dGhyZWFkMTczcmVjb3JkMTcz"),
    ("thread173candle173", "dGhyZWFkMTczY2FuZGxlMTcz"),
    ("thread173thread173", "dGhyZWFkMTczdGhyZWFkMTcz"),
    ("thread173kitten173", "dGhyZWFkMTcza2l0dGVuMTcz"),
    (
        "round 173: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTczOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 173: agentuniverse is a framework for multi agents",
        "cm91bmQgMTczOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 173: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTczOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 173: the processor reads the record then stops",
        "cm91bmQgMTczOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 173: a worker pulls the next task from the queue",
        "cm91bmQgMTczOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 173: signals travel through the network layer",
        "cm91bmQgMTczOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 173: the gateway routes each request by policy",
        "cm91bmQgMTczOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 173: memory grows until the buffer is full",
        "cm91bmQgMTczOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 173: the cluster mirrors every packet twice",
        "cm91bmQgMTczOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 173: ranking uses tokens learned from the corpus",
        "cm91bmQgMTczOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 173: a long session ends when the candle dies",
        "cm91bmQgMTczOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 173: encode the prompt then map the result",
        "cm91bmQgMTczOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 173: the kernel wakes the worker at dawn",
        "cm91bmQgMTczOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 173: service latency drops after the patch",
        "cm91bmQgMTczOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 173: the library caches every vector it sees",
        "cm91bmQgMTczOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 173: agents argue then the debate resolves",
        "cm91bmQgMTczOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 173: the filter keeps only strong matches",
        "cm91bmQgMTczOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 173: the model answers with a short reply",
        "cm91bmQgMTczOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 173: the recorder stores the reasoning trace",
        "cm91bmQgMTczOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 173: the angel watches the processor run",
        "cm91bmQgMTczOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 173: angle of the vector decides the match",
        "cm91bmQgMTczOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 173: the candle burns twice as long at night",
        "cm91bmQgMTczOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 173: a mirror of the universe in one line",
        "cm91bmQgMTczOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 173: the queue drains before the storm", "cm91bmQgMTczOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
