"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten199kitten199", "a2l0dGVuMTk5a2l0dGVuMTk5"),
    ("kitten199sitting199", "a2l0dGVuMTk5c2l0dGluZzE5OQ"),
    ("kitten199agent199", "a2l0dGVuMTk5YWdlbnQxOTk"),
    ("kitten199angle199", "a2l0dGVuMTk5YW5nbGUxOTk"),
    ("sitting199angle199", "c2l0dGluZzE5OWFuZ2xlMTk5"),
    ("sitting199universe199", "c2l0dGluZzE5OXVuaXZlcnNlMTk5"),
    ("sitting199memory199", "c2l0dGluZzE5OW1lbW9yeTE5OQ"),
    ("sitting199stream199", "c2l0dGluZzE5OXN0cmVhbTE5OQ"),
    ("agent199stream199", "YWdlbnQxOTlzdHJlYW0xOTk"),
    ("agent199context199", "YWdlbnQxOTljb250ZXh0MTk5"),
    ("agent199knowledge199", "YWdlbnQxOTlrbm93bGVkZ2UxOTk"),
    ("agent199vector199", "YWdlbnQxOTl2ZWN0b3IxOTk"),
    ("angle199vector199", "YW5nbGUxOTl2ZWN0b3IxOTk"),
    ("angle199processor199", "YW5nbGUxOTlwcm9jZXNzb3IxOTk"),
    ("angle199reasoning199", "YW5nbGUxOTlyZWFzb25pbmcxOTk"),
    ("angle199machine199", "YW5nbGUxOTltYWNoaW5lMTk5"),
    ("universe199machine199", "dW5pdmVyc2UxOTltYWNoaW5lMTk5"),
    ("universe199learning199", "dW5pdmVyc2UxOTlsZWFybmluZzE5OQ"),
    ("universe199model199", "dW5pdmVyc2UxOTltb2RlbDE5OQ"),
    ("universe199token199", "dW5pdmVyc2UxOTl0b2tlbjE5OQ"),
    ("memory199token199", "bWVtb3J5MTk5dG9rZW4xOTk"),
    ("memory199prompt199", "bWVtb3J5MTk5cHJvbXB0MTk5"),
    ("memory199session199", "bWVtb3J5MTk5c2Vzc2lvbjE5OQ"),
    ("memory199library199", "bWVtb3J5MTk5bGlicmFyeTE5OQ"),
    ("stream199library199", "c3RyZWFtMTk5bGlicmFyeTE5OQ"),
    ("stream199service199", "c3RyZWFtMTk5c2VydmljZTE5OQ"),
    ("stream199gateway199", "c3RyZWFtMTk5Z2F0ZXdheTE5OQ"),
    ("stream199storage199", "c3RyZWFtMTk5c3RvcmFnZTE5OQ"),
    ("context199storage199", "Y29udGV4dDE5OXN0b3JhZ2UxOTk"),
    ("context199network199", "Y29udGV4dDE5OW5ldHdvcmsxOTk"),
    ("context199latency199", "Y29udGV4dDE5OWxhdGVuY3kxOTk"),
    ("context199buffer199", "Y29udGV4dDE5OWJ1ZmZlcjE5OQ"),
    ("knowledge199buffer199", "a25vd2xlZGdlMTk5YnVmZmVyMTk5"),
    ("knowledge199queue199", "a25vd2xlZGdlMTk5cXVldWUxOTk"),
    ("knowledge199worker199", "a25vd2xlZGdlMTk5d29ya2VyMTk5"),
    ("knowledge199kernel199", "a25vd2xlZGdlMTk5a2VybmVsMTk5"),
    ("vector199kernel199", "dmVjdG9yMTk5a2VybmVsMTk5"),
    ("vector199signal199", "dmVjdG9yMTk5c2lnbmFsMTk5"),
    ("vector199packet199", "dmVjdG9yMTk5cGFja2V0MTk5"),
    ("vector199router199", "dmVjdG9yMTk5cm91dGVyMTk5"),
    ("processor199router199", "cHJvY2Vzc29yMTk5cm91dGVyMTk5"),
    ("processor199cluster199", "cHJvY2Vzc29yMTk5Y2x1c3RlcjE5OQ"),
    ("processor199mirror199", "cHJvY2Vzc29yMTk5bWlycm9yMTk5"),
    ("processor199filter199", "cHJvY2Vzc29yMTk5ZmlsdGVyMTk5"),
    ("reasoning199filter199", "cmVhc29uaW5nMTk5ZmlsdGVyMTk5"),
    ("reasoning199ranking199", "cmVhc29uaW5nMTk5cmFua2luZzE5OQ"),
    ("reasoning199encoding199", "cmVhc29uaW5nMTk5ZW5jb2RpbmcxOTk"),
    ("reasoning199mapping199", "cmVhc29uaW5nMTk5bWFwcGluZzE5OQ"),
    ("machine199mapping199", "bWFjaGluZTE5OW1hcHBpbmcxOTk"),
    ("machine199record199", "bWFjaGluZTE5OXJlY29yZDE5OQ"),
    ("machine199candle199", "bWFjaGluZTE5OWNhbmRsZTE5OQ"),
    ("machine199thread199", "bWFjaGluZTE5OXRocmVhZDE5OQ"),
    ("learning199thread199", "bGVhcm5pbmcxOTl0aHJlYWQxOTk"),
    ("learning199kitten199", "bGVhcm5pbmcxOTlraXR0ZW4xOTk"),
    ("learning199sitting199", "bGVhcm5pbmcxOTlzaXR0aW5nMTk5"),
    ("learning199agent199", "bGVhcm5pbmcxOTlhZ2VudDE5OQ"),
    ("model199agent199", "bW9kZWwxOTlhZ2VudDE5OQ"),
    ("model199angle199", "bW9kZWwxOTlhbmdsZTE5OQ"),
    ("model199universe199", "bW9kZWwxOTl1bml2ZXJzZTE5OQ"),
    ("model199memory199", "bW9kZWwxOTltZW1vcnkxOTk"),
    ("token199memory199", "dG9rZW4xOTltZW1vcnkxOTk"),
    ("token199stream199", "dG9rZW4xOTlzdHJlYW0xOTk"),
    ("token199context199", "dG9rZW4xOTljb250ZXh0MTk5"),
    ("token199knowledge199", "dG9rZW4xOTlrbm93bGVkZ2UxOTk"),
    ("prompt199knowledge199", "cHJvbXB0MTk5a25vd2xlZGdlMTk5"),
    ("prompt199vector199", "cHJvbXB0MTk5dmVjdG9yMTk5"),
    ("prompt199processor199", "cHJvbXB0MTk5cHJvY2Vzc29yMTk5"),
    ("prompt199reasoning199", "cHJvbXB0MTk5cmVhc29uaW5nMTk5"),
    ("session199reasoning199", "c2Vzc2lvbjE5OXJlYXNvbmluZzE5OQ"),
    ("session199machine199", "c2Vzc2lvbjE5OW1hY2hpbmUxOTk"),
    ("session199learning199", "c2Vzc2lvbjE5OWxlYXJuaW5nMTk5"),
    ("session199model199", "c2Vzc2lvbjE5OW1vZGVsMTk5"),
    ("library199model199", "bGlicmFyeTE5OW1vZGVsMTk5"),
    ("library199token199", "bGlicmFyeTE5OXRva2VuMTk5"),
    ("library199prompt199", "bGlicmFyeTE5OXByb21wdDE5OQ"),
    ("library199session199", "bGlicmFyeTE5OXNlc3Npb24xOTk"),
    ("service199session199", "c2VydmljZTE5OXNlc3Npb24xOTk"),
    ("service199library199", "c2VydmljZTE5OWxpYnJhcnkxOTk"),
    ("service199service199", "c2VydmljZTE5OXNlcnZpY2UxOTk"),
    ("service199gateway199", "c2VydmljZTE5OWdhdGV3YXkxOTk"),
    ("gateway199gateway199", "Z2F0ZXdheTE5OWdhdGV3YXkxOTk"),
    ("gateway199storage199", "Z2F0ZXdheTE5OXN0b3JhZ2UxOTk"),
    ("gateway199network199", "Z2F0ZXdheTE5OW5ldHdvcmsxOTk"),
    ("gateway199latency199", "Z2F0ZXdheTE5OWxhdGVuY3kxOTk"),
    ("storage199latency199", "c3RvcmFnZTE5OWxhdGVuY3kxOTk"),
    ("storage199buffer199", "c3RvcmFnZTE5OWJ1ZmZlcjE5OQ"),
    ("storage199queue199", "c3RvcmFnZTE5OXF1ZXVlMTk5"),
    ("storage199worker199", "c3RvcmFnZTE5OXdvcmtlcjE5OQ"),
    ("network199worker199", "bmV0d29yazE5OXdvcmtlcjE5OQ"),
    ("network199kernel199", "bmV0d29yazE5OWtlcm5lbDE5OQ"),
    ("network199signal199", "bmV0d29yazE5OXNpZ25hbDE5OQ"),
    ("network199packet199", "bmV0d29yazE5OXBhY2tldDE5OQ"),
    ("latency199packet199", "bGF0ZW5jeTE5OXBhY2tldDE5OQ"),
    ("latency199router199", "bGF0ZW5jeTE5OXJvdXRlcjE5OQ"),
    ("latency199cluster199", "bGF0ZW5jeTE5OWNsdXN0ZXIxOTk"),
    ("latency199mirror199", "bGF0ZW5jeTE5OW1pcnJvcjE5OQ"),
    ("buffer199mirror199", "YnVmZmVyMTk5bWlycm9yMTk5"),
    ("buffer199filter199", "YnVmZmVyMTk5ZmlsdGVyMTk5"),
    ("buffer199ranking199", "YnVmZmVyMTk5cmFua2luZzE5OQ"),
    ("buffer199encoding199", "YnVmZmVyMTk5ZW5jb2RpbmcxOTk"),
    ("queue199encoding199", "cXVldWUxOTllbmNvZGluZzE5OQ"),
    ("queue199mapping199", "cXVldWUxOTltYXBwaW5nMTk5"),
    ("queue199record199", "cXVldWUxOTlyZWNvcmQxOTk"),
    ("queue199candle199", "cXVldWUxOTljYW5kbGUxOTk"),
    ("worker199candle199", "d29ya2VyMTk5Y2FuZGxlMTk5"),
    ("worker199thread199", "d29ya2VyMTk5dGhyZWFkMTk5"),
    ("worker199kitten199", "d29ya2VyMTk5a2l0dGVuMTk5"),
    ("worker199sitting199", "d29ya2VyMTk5c2l0dGluZzE5OQ"),
    ("kernel199sitting199", "a2VybmVsMTk5c2l0dGluZzE5OQ"),
    ("kernel199agent199", "a2VybmVsMTk5YWdlbnQxOTk"),
    ("kernel199angle199", "a2VybmVsMTk5YW5nbGUxOTk"),
    ("kernel199universe199", "a2VybmVsMTk5dW5pdmVyc2UxOTk"),
    ("signal199universe199", "c2lnbmFsMTk5dW5pdmVyc2UxOTk"),
    ("signal199memory199", "c2lnbmFsMTk5bWVtb3J5MTk5"),
    ("signal199stream199", "c2lnbmFsMTk5c3RyZWFtMTk5"),
    ("signal199context199", "c2lnbmFsMTk5Y29udGV4dDE5OQ"),
    ("packet199context199", "cGFja2V0MTk5Y29udGV4dDE5OQ"),
    ("packet199knowledge199", "cGFja2V0MTk5a25vd2xlZGdlMTk5"),
    ("packet199vector199", "cGFja2V0MTk5dmVjdG9yMTk5"),
    ("packet199processor199", "cGFja2V0MTk5cHJvY2Vzc29yMTk5"),
    ("router199processor199", "cm91dGVyMTk5cHJvY2Vzc29yMTk5"),
    ("router199reasoning199", "cm91dGVyMTk5cmVhc29uaW5nMTk5"),
    ("router199machine199", "cm91dGVyMTk5bWFjaGluZTE5OQ"),
    ("router199learning199", "cm91dGVyMTk5bGVhcm5pbmcxOTk"),
    ("cluster199learning199", "Y2x1c3RlcjE5OWxlYXJuaW5nMTk5"),
    ("cluster199model199", "Y2x1c3RlcjE5OW1vZGVsMTk5"),
    ("cluster199token199", "Y2x1c3RlcjE5OXRva2VuMTk5"),
    ("cluster199prompt199", "Y2x1c3RlcjE5OXByb21wdDE5OQ"),
    ("mirror199prompt199", "bWlycm9yMTk5cHJvbXB0MTk5"),
    ("mirror199session199", "bWlycm9yMTk5c2Vzc2lvbjE5OQ"),
    ("mirror199library199", "bWlycm9yMTk5bGlicmFyeTE5OQ"),
    ("mirror199service199", "bWlycm9yMTk5c2VydmljZTE5OQ"),
    ("filter199service199", "ZmlsdGVyMTk5c2VydmljZTE5OQ"),
    ("filter199gateway199", "ZmlsdGVyMTk5Z2F0ZXdheTE5OQ"),
    ("filter199storage199", "ZmlsdGVyMTk5c3RvcmFnZTE5OQ"),
    ("filter199network199", "ZmlsdGVyMTk5bmV0d29yazE5OQ"),
    ("ranking199network199", "cmFua2luZzE5OW5ldHdvcmsxOTk"),
    ("ranking199latency199", "cmFua2luZzE5OWxhdGVuY3kxOTk"),
    ("ranking199buffer199", "cmFua2luZzE5OWJ1ZmZlcjE5OQ"),
    ("ranking199queue199", "cmFua2luZzE5OXF1ZXVlMTk5"),
    ("encoding199queue199", "ZW5jb2RpbmcxOTlxdWV1ZTE5OQ"),
    ("encoding199worker199", "ZW5jb2RpbmcxOTl3b3JrZXIxOTk"),
    ("encoding199kernel199", "ZW5jb2RpbmcxOTlrZXJuZWwxOTk"),
    ("encoding199signal199", "ZW5jb2RpbmcxOTlzaWduYWwxOTk"),
    ("mapping199signal199", "bWFwcGluZzE5OXNpZ25hbDE5OQ"),
    ("mapping199packet199", "bWFwcGluZzE5OXBhY2tldDE5OQ"),
    ("mapping199router199", "bWFwcGluZzE5OXJvdXRlcjE5OQ"),
    ("mapping199cluster199", "bWFwcGluZzE5OWNsdXN0ZXIxOTk"),
    ("record199cluster199", "cmVjb3JkMTk5Y2x1c3RlcjE5OQ"),
    ("record199mirror199", "cmVjb3JkMTk5bWlycm9yMTk5"),
    ("record199filter199", "cmVjb3JkMTk5ZmlsdGVyMTk5"),
    ("record199ranking199", "cmVjb3JkMTk5cmFua2luZzE5OQ"),
    ("candle199ranking199", "Y2FuZGxlMTk5cmFua2luZzE5OQ"),
    ("candle199encoding199", "Y2FuZGxlMTk5ZW5jb2RpbmcxOTk"),
    ("candle199mapping199", "Y2FuZGxlMTk5bWFwcGluZzE5OQ"),
    ("candle199record199", "Y2FuZGxlMTk5cmVjb3JkMTk5"),
    ("thread199record199", "dGhyZWFkMTk5cmVjb3JkMTk5"),
    ("thread199candle199", "dGhyZWFkMTk5Y2FuZGxlMTk5"),
    ("thread199thread199", "dGhyZWFkMTk5dGhyZWFkMTk5"),
    ("thread199kitten199", "dGhyZWFkMTk5a2l0dGVuMTk5"),
    (
        "round 199: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTk5OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 199: agentuniverse is a framework for multi agents",
        "cm91bmQgMTk5OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 199: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTk5OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 199: the processor reads the record then stops",
        "cm91bmQgMTk5OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 199: a worker pulls the next task from the queue",
        "cm91bmQgMTk5OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 199: signals travel through the network layer",
        "cm91bmQgMTk5OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 199: the gateway routes each request by policy",
        "cm91bmQgMTk5OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 199: memory grows until the buffer is full",
        "cm91bmQgMTk5OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 199: the cluster mirrors every packet twice",
        "cm91bmQgMTk5OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 199: ranking uses tokens learned from the corpus",
        "cm91bmQgMTk5OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 199: a long session ends when the candle dies",
        "cm91bmQgMTk5OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 199: encode the prompt then map the result",
        "cm91bmQgMTk5OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 199: the kernel wakes the worker at dawn",
        "cm91bmQgMTk5OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 199: service latency drops after the patch",
        "cm91bmQgMTk5OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 199: the library caches every vector it sees",
        "cm91bmQgMTk5OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 199: agents argue then the debate resolves",
        "cm91bmQgMTk5OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 199: the filter keeps only strong matches",
        "cm91bmQgMTk5OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 199: the model answers with a short reply",
        "cm91bmQgMTk5OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 199: the recorder stores the reasoning trace",
        "cm91bmQgMTk5OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 199: the angel watches the processor run",
        "cm91bmQgMTk5OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 199: angle of the vector decides the match",
        "cm91bmQgMTk5OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 199: the candle burns twice as long at night",
        "cm91bmQgMTk5OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 199: a mirror of the universe in one line",
        "cm91bmQgMTk5OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 199: the queue drains before the storm", "cm91bmQgMTk5OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
