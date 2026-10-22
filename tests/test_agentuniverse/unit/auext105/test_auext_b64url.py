"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten105kitten105", "a2l0dGVuMTA1a2l0dGVuMTA1"),
    ("kitten105sitting105", "a2l0dGVuMTA1c2l0dGluZzEwNQ"),
    ("kitten105agent105", "a2l0dGVuMTA1YWdlbnQxMDU"),
    ("kitten105angle105", "a2l0dGVuMTA1YW5nbGUxMDU"),
    ("sitting105angle105", "c2l0dGluZzEwNWFuZ2xlMTA1"),
    ("sitting105universe105", "c2l0dGluZzEwNXVuaXZlcnNlMTA1"),
    ("sitting105memory105", "c2l0dGluZzEwNW1lbW9yeTEwNQ"),
    ("sitting105stream105", "c2l0dGluZzEwNXN0cmVhbTEwNQ"),
    ("agent105stream105", "YWdlbnQxMDVzdHJlYW0xMDU"),
    ("agent105context105", "YWdlbnQxMDVjb250ZXh0MTA1"),
    ("agent105knowledge105", "YWdlbnQxMDVrbm93bGVkZ2UxMDU"),
    ("agent105vector105", "YWdlbnQxMDV2ZWN0b3IxMDU"),
    ("angle105vector105", "YW5nbGUxMDV2ZWN0b3IxMDU"),
    ("angle105processor105", "YW5nbGUxMDVwcm9jZXNzb3IxMDU"),
    ("angle105reasoning105", "YW5nbGUxMDVyZWFzb25pbmcxMDU"),
    ("angle105machine105", "YW5nbGUxMDVtYWNoaW5lMTA1"),
    ("universe105machine105", "dW5pdmVyc2UxMDVtYWNoaW5lMTA1"),
    ("universe105learning105", "dW5pdmVyc2UxMDVsZWFybmluZzEwNQ"),
    ("universe105model105", "dW5pdmVyc2UxMDVtb2RlbDEwNQ"),
    ("universe105token105", "dW5pdmVyc2UxMDV0b2tlbjEwNQ"),
    ("memory105token105", "bWVtb3J5MTA1dG9rZW4xMDU"),
    ("memory105prompt105", "bWVtb3J5MTA1cHJvbXB0MTA1"),
    ("memory105session105", "bWVtb3J5MTA1c2Vzc2lvbjEwNQ"),
    ("memory105library105", "bWVtb3J5MTA1bGlicmFyeTEwNQ"),
    ("stream105library105", "c3RyZWFtMTA1bGlicmFyeTEwNQ"),
    ("stream105service105", "c3RyZWFtMTA1c2VydmljZTEwNQ"),
    ("stream105gateway105", "c3RyZWFtMTA1Z2F0ZXdheTEwNQ"),
    ("stream105storage105", "c3RyZWFtMTA1c3RvcmFnZTEwNQ"),
    ("context105storage105", "Y29udGV4dDEwNXN0b3JhZ2UxMDU"),
    ("context105network105", "Y29udGV4dDEwNW5ldHdvcmsxMDU"),
    ("context105latency105", "Y29udGV4dDEwNWxhdGVuY3kxMDU"),
    ("context105buffer105", "Y29udGV4dDEwNWJ1ZmZlcjEwNQ"),
    ("knowledge105buffer105", "a25vd2xlZGdlMTA1YnVmZmVyMTA1"),
    ("knowledge105queue105", "a25vd2xlZGdlMTA1cXVldWUxMDU"),
    ("knowledge105worker105", "a25vd2xlZGdlMTA1d29ya2VyMTA1"),
    ("knowledge105kernel105", "a25vd2xlZGdlMTA1a2VybmVsMTA1"),
    ("vector105kernel105", "dmVjdG9yMTA1a2VybmVsMTA1"),
    ("vector105signal105", "dmVjdG9yMTA1c2lnbmFsMTA1"),
    ("vector105packet105", "dmVjdG9yMTA1cGFja2V0MTA1"),
    ("vector105router105", "dmVjdG9yMTA1cm91dGVyMTA1"),
    ("processor105router105", "cHJvY2Vzc29yMTA1cm91dGVyMTA1"),
    ("processor105cluster105", "cHJvY2Vzc29yMTA1Y2x1c3RlcjEwNQ"),
    ("processor105mirror105", "cHJvY2Vzc29yMTA1bWlycm9yMTA1"),
    ("processor105filter105", "cHJvY2Vzc29yMTA1ZmlsdGVyMTA1"),
    ("reasoning105filter105", "cmVhc29uaW5nMTA1ZmlsdGVyMTA1"),
    ("reasoning105ranking105", "cmVhc29uaW5nMTA1cmFua2luZzEwNQ"),
    ("reasoning105encoding105", "cmVhc29uaW5nMTA1ZW5jb2RpbmcxMDU"),
    ("reasoning105mapping105", "cmVhc29uaW5nMTA1bWFwcGluZzEwNQ"),
    ("machine105mapping105", "bWFjaGluZTEwNW1hcHBpbmcxMDU"),
    ("machine105record105", "bWFjaGluZTEwNXJlY29yZDEwNQ"),
    ("machine105candle105", "bWFjaGluZTEwNWNhbmRsZTEwNQ"),
    ("machine105thread105", "bWFjaGluZTEwNXRocmVhZDEwNQ"),
    ("learning105thread105", "bGVhcm5pbmcxMDV0aHJlYWQxMDU"),
    ("learning105kitten105", "bGVhcm5pbmcxMDVraXR0ZW4xMDU"),
    ("learning105sitting105", "bGVhcm5pbmcxMDVzaXR0aW5nMTA1"),
    ("learning105agent105", "bGVhcm5pbmcxMDVhZ2VudDEwNQ"),
    ("model105agent105", "bW9kZWwxMDVhZ2VudDEwNQ"),
    ("model105angle105", "bW9kZWwxMDVhbmdsZTEwNQ"),
    ("model105universe105", "bW9kZWwxMDV1bml2ZXJzZTEwNQ"),
    ("model105memory105", "bW9kZWwxMDVtZW1vcnkxMDU"),
    ("token105memory105", "dG9rZW4xMDVtZW1vcnkxMDU"),
    ("token105stream105", "dG9rZW4xMDVzdHJlYW0xMDU"),
    ("token105context105", "dG9rZW4xMDVjb250ZXh0MTA1"),
    ("token105knowledge105", "dG9rZW4xMDVrbm93bGVkZ2UxMDU"),
    ("prompt105knowledge105", "cHJvbXB0MTA1a25vd2xlZGdlMTA1"),
    ("prompt105vector105", "cHJvbXB0MTA1dmVjdG9yMTA1"),
    ("prompt105processor105", "cHJvbXB0MTA1cHJvY2Vzc29yMTA1"),
    ("prompt105reasoning105", "cHJvbXB0MTA1cmVhc29uaW5nMTA1"),
    ("session105reasoning105", "c2Vzc2lvbjEwNXJlYXNvbmluZzEwNQ"),
    ("session105machine105", "c2Vzc2lvbjEwNW1hY2hpbmUxMDU"),
    ("session105learning105", "c2Vzc2lvbjEwNWxlYXJuaW5nMTA1"),
    ("session105model105", "c2Vzc2lvbjEwNW1vZGVsMTA1"),
    ("library105model105", "bGlicmFyeTEwNW1vZGVsMTA1"),
    ("library105token105", "bGlicmFyeTEwNXRva2VuMTA1"),
    ("library105prompt105", "bGlicmFyeTEwNXByb21wdDEwNQ"),
    ("library105session105", "bGlicmFyeTEwNXNlc3Npb24xMDU"),
    ("service105session105", "c2VydmljZTEwNXNlc3Npb24xMDU"),
    ("service105library105", "c2VydmljZTEwNWxpYnJhcnkxMDU"),
    ("service105service105", "c2VydmljZTEwNXNlcnZpY2UxMDU"),
    ("service105gateway105", "c2VydmljZTEwNWdhdGV3YXkxMDU"),
    ("gateway105gateway105", "Z2F0ZXdheTEwNWdhdGV3YXkxMDU"),
    ("gateway105storage105", "Z2F0ZXdheTEwNXN0b3JhZ2UxMDU"),
    ("gateway105network105", "Z2F0ZXdheTEwNW5ldHdvcmsxMDU"),
    ("gateway105latency105", "Z2F0ZXdheTEwNWxhdGVuY3kxMDU"),
    ("storage105latency105", "c3RvcmFnZTEwNWxhdGVuY3kxMDU"),
    ("storage105buffer105", "c3RvcmFnZTEwNWJ1ZmZlcjEwNQ"),
    ("storage105queue105", "c3RvcmFnZTEwNXF1ZXVlMTA1"),
    ("storage105worker105", "c3RvcmFnZTEwNXdvcmtlcjEwNQ"),
    ("network105worker105", "bmV0d29yazEwNXdvcmtlcjEwNQ"),
    ("network105kernel105", "bmV0d29yazEwNWtlcm5lbDEwNQ"),
    ("network105signal105", "bmV0d29yazEwNXNpZ25hbDEwNQ"),
    ("network105packet105", "bmV0d29yazEwNXBhY2tldDEwNQ"),
    ("latency105packet105", "bGF0ZW5jeTEwNXBhY2tldDEwNQ"),
    ("latency105router105", "bGF0ZW5jeTEwNXJvdXRlcjEwNQ"),
    ("latency105cluster105", "bGF0ZW5jeTEwNWNsdXN0ZXIxMDU"),
    ("latency105mirror105", "bGF0ZW5jeTEwNW1pcnJvcjEwNQ"),
    ("buffer105mirror105", "YnVmZmVyMTA1bWlycm9yMTA1"),
    ("buffer105filter105", "YnVmZmVyMTA1ZmlsdGVyMTA1"),
    ("buffer105ranking105", "YnVmZmVyMTA1cmFua2luZzEwNQ"),
    ("buffer105encoding105", "YnVmZmVyMTA1ZW5jb2RpbmcxMDU"),
    ("queue105encoding105", "cXVldWUxMDVlbmNvZGluZzEwNQ"),
    ("queue105mapping105", "cXVldWUxMDVtYXBwaW5nMTA1"),
    ("queue105record105", "cXVldWUxMDVyZWNvcmQxMDU"),
    ("queue105candle105", "cXVldWUxMDVjYW5kbGUxMDU"),
    ("worker105candle105", "d29ya2VyMTA1Y2FuZGxlMTA1"),
    ("worker105thread105", "d29ya2VyMTA1dGhyZWFkMTA1"),
    ("worker105kitten105", "d29ya2VyMTA1a2l0dGVuMTA1"),
    ("worker105sitting105", "d29ya2VyMTA1c2l0dGluZzEwNQ"),
    ("kernel105sitting105", "a2VybmVsMTA1c2l0dGluZzEwNQ"),
    ("kernel105agent105", "a2VybmVsMTA1YWdlbnQxMDU"),
    ("kernel105angle105", "a2VybmVsMTA1YW5nbGUxMDU"),
    ("kernel105universe105", "a2VybmVsMTA1dW5pdmVyc2UxMDU"),
    ("signal105universe105", "c2lnbmFsMTA1dW5pdmVyc2UxMDU"),
    ("signal105memory105", "c2lnbmFsMTA1bWVtb3J5MTA1"),
    ("signal105stream105", "c2lnbmFsMTA1c3RyZWFtMTA1"),
    ("signal105context105", "c2lnbmFsMTA1Y29udGV4dDEwNQ"),
    ("packet105context105", "cGFja2V0MTA1Y29udGV4dDEwNQ"),
    ("packet105knowledge105", "cGFja2V0MTA1a25vd2xlZGdlMTA1"),
    ("packet105vector105", "cGFja2V0MTA1dmVjdG9yMTA1"),
    ("packet105processor105", "cGFja2V0MTA1cHJvY2Vzc29yMTA1"),
    ("router105processor105", "cm91dGVyMTA1cHJvY2Vzc29yMTA1"),
    ("router105reasoning105", "cm91dGVyMTA1cmVhc29uaW5nMTA1"),
    ("router105machine105", "cm91dGVyMTA1bWFjaGluZTEwNQ"),
    ("router105learning105", "cm91dGVyMTA1bGVhcm5pbmcxMDU"),
    ("cluster105learning105", "Y2x1c3RlcjEwNWxlYXJuaW5nMTA1"),
    ("cluster105model105", "Y2x1c3RlcjEwNW1vZGVsMTA1"),
    ("cluster105token105", "Y2x1c3RlcjEwNXRva2VuMTA1"),
    ("cluster105prompt105", "Y2x1c3RlcjEwNXByb21wdDEwNQ"),
    ("mirror105prompt105", "bWlycm9yMTA1cHJvbXB0MTA1"),
    ("mirror105session105", "bWlycm9yMTA1c2Vzc2lvbjEwNQ"),
    ("mirror105library105", "bWlycm9yMTA1bGlicmFyeTEwNQ"),
    ("mirror105service105", "bWlycm9yMTA1c2VydmljZTEwNQ"),
    ("filter105service105", "ZmlsdGVyMTA1c2VydmljZTEwNQ"),
    ("filter105gateway105", "ZmlsdGVyMTA1Z2F0ZXdheTEwNQ"),
    ("filter105storage105", "ZmlsdGVyMTA1c3RvcmFnZTEwNQ"),
    ("filter105network105", "ZmlsdGVyMTA1bmV0d29yazEwNQ"),
    ("ranking105network105", "cmFua2luZzEwNW5ldHdvcmsxMDU"),
    ("ranking105latency105", "cmFua2luZzEwNWxhdGVuY3kxMDU"),
    ("ranking105buffer105", "cmFua2luZzEwNWJ1ZmZlcjEwNQ"),
    ("ranking105queue105", "cmFua2luZzEwNXF1ZXVlMTA1"),
    ("encoding105queue105", "ZW5jb2RpbmcxMDVxdWV1ZTEwNQ"),
    ("encoding105worker105", "ZW5jb2RpbmcxMDV3b3JrZXIxMDU"),
    ("encoding105kernel105", "ZW5jb2RpbmcxMDVrZXJuZWwxMDU"),
    ("encoding105signal105", "ZW5jb2RpbmcxMDVzaWduYWwxMDU"),
    ("mapping105signal105", "bWFwcGluZzEwNXNpZ25hbDEwNQ"),
    ("mapping105packet105", "bWFwcGluZzEwNXBhY2tldDEwNQ"),
    ("mapping105router105", "bWFwcGluZzEwNXJvdXRlcjEwNQ"),
    ("mapping105cluster105", "bWFwcGluZzEwNWNsdXN0ZXIxMDU"),
    ("record105cluster105", "cmVjb3JkMTA1Y2x1c3RlcjEwNQ"),
    ("record105mirror105", "cmVjb3JkMTA1bWlycm9yMTA1"),
    ("record105filter105", "cmVjb3JkMTA1ZmlsdGVyMTA1"),
    ("record105ranking105", "cmVjb3JkMTA1cmFua2luZzEwNQ"),
    ("candle105ranking105", "Y2FuZGxlMTA1cmFua2luZzEwNQ"),
    ("candle105encoding105", "Y2FuZGxlMTA1ZW5jb2RpbmcxMDU"),
    ("candle105mapping105", "Y2FuZGxlMTA1bWFwcGluZzEwNQ"),
    ("candle105record105", "Y2FuZGxlMTA1cmVjb3JkMTA1"),
    ("thread105record105", "dGhyZWFkMTA1cmVjb3JkMTA1"),
    ("thread105candle105", "dGhyZWFkMTA1Y2FuZGxlMTA1"),
    ("thread105thread105", "dGhyZWFkMTA1dGhyZWFkMTA1"),
    ("thread105kitten105", "dGhyZWFkMTA1a2l0dGVuMTA1"),
    (
        "round 105: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTA1OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 105: agentuniverse is a framework for multi agents",
        "cm91bmQgMTA1OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 105: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTA1OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 105: the processor reads the record then stops",
        "cm91bmQgMTA1OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 105: a worker pulls the next task from the queue",
        "cm91bmQgMTA1OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 105: signals travel through the network layer",
        "cm91bmQgMTA1OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 105: the gateway routes each request by policy",
        "cm91bmQgMTA1OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 105: memory grows until the buffer is full",
        "cm91bmQgMTA1OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 105: the cluster mirrors every packet twice",
        "cm91bmQgMTA1OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 105: ranking uses tokens learned from the corpus",
        "cm91bmQgMTA1OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 105: a long session ends when the candle dies",
        "cm91bmQgMTA1OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 105: encode the prompt then map the result",
        "cm91bmQgMTA1OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 105: the kernel wakes the worker at dawn",
        "cm91bmQgMTA1OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 105: service latency drops after the patch",
        "cm91bmQgMTA1OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 105: the library caches every vector it sees",
        "cm91bmQgMTA1OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 105: agents argue then the debate resolves",
        "cm91bmQgMTA1OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 105: the filter keeps only strong matches",
        "cm91bmQgMTA1OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 105: the model answers with a short reply",
        "cm91bmQgMTA1OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 105: the recorder stores the reasoning trace",
        "cm91bmQgMTA1OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 105: the angel watches the processor run",
        "cm91bmQgMTA1OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 105: angle of the vector decides the match",
        "cm91bmQgMTA1OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 105: the candle burns twice as long at night",
        "cm91bmQgMTA1OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 105: a mirror of the universe in one line",
        "cm91bmQgMTA1OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 105: the queue drains before the storm", "cm91bmQgMTA1OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
