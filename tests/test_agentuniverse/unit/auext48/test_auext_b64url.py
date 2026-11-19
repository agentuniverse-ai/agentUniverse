"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten48kitten48", "a2l0dGVuNDhraXR0ZW40OA"),
    ("kitten48sitting48", "a2l0dGVuNDhzaXR0aW5nNDg"),
    ("kitten48agent48", "a2l0dGVuNDhhZ2VudDQ4"),
    ("kitten48angle48", "a2l0dGVuNDhhbmdsZTQ4"),
    ("sitting48angle48", "c2l0dGluZzQ4YW5nbGU0OA"),
    ("sitting48universe48", "c2l0dGluZzQ4dW5pdmVyc2U0OA"),
    ("sitting48memory48", "c2l0dGluZzQ4bWVtb3J5NDg"),
    ("sitting48stream48", "c2l0dGluZzQ4c3RyZWFtNDg"),
    ("agent48stream48", "YWdlbnQ0OHN0cmVhbTQ4"),
    ("agent48context48", "YWdlbnQ0OGNvbnRleHQ0OA"),
    ("agent48knowledge48", "YWdlbnQ0OGtub3dsZWRnZTQ4"),
    ("agent48vector48", "YWdlbnQ0OHZlY3RvcjQ4"),
    ("angle48vector48", "YW5nbGU0OHZlY3RvcjQ4"),
    ("angle48processor48", "YW5nbGU0OHByb2Nlc3NvcjQ4"),
    ("angle48reasoning48", "YW5nbGU0OHJlYXNvbmluZzQ4"),
    ("angle48machine48", "YW5nbGU0OG1hY2hpbmU0OA"),
    ("universe48machine48", "dW5pdmVyc2U0OG1hY2hpbmU0OA"),
    ("universe48learning48", "dW5pdmVyc2U0OGxlYXJuaW5nNDg"),
    ("universe48model48", "dW5pdmVyc2U0OG1vZGVsNDg"),
    ("universe48token48", "dW5pdmVyc2U0OHRva2VuNDg"),
    ("memory48token48", "bWVtb3J5NDh0b2tlbjQ4"),
    ("memory48prompt48", "bWVtb3J5NDhwcm9tcHQ0OA"),
    ("memory48session48", "bWVtb3J5NDhzZXNzaW9uNDg"),
    ("memory48library48", "bWVtb3J5NDhsaWJyYXJ5NDg"),
    ("stream48library48", "c3RyZWFtNDhsaWJyYXJ5NDg"),
    ("stream48service48", "c3RyZWFtNDhzZXJ2aWNlNDg"),
    ("stream48gateway48", "c3RyZWFtNDhnYXRld2F5NDg"),
    ("stream48storage48", "c3RyZWFtNDhzdG9yYWdlNDg"),
    ("context48storage48", "Y29udGV4dDQ4c3RvcmFnZTQ4"),
    ("context48network48", "Y29udGV4dDQ4bmV0d29yazQ4"),
    ("context48latency48", "Y29udGV4dDQ4bGF0ZW5jeTQ4"),
    ("context48buffer48", "Y29udGV4dDQ4YnVmZmVyNDg"),
    ("knowledge48buffer48", "a25vd2xlZGdlNDhidWZmZXI0OA"),
    ("knowledge48queue48", "a25vd2xlZGdlNDhxdWV1ZTQ4"),
    ("knowledge48worker48", "a25vd2xlZGdlNDh3b3JrZXI0OA"),
    ("knowledge48kernel48", "a25vd2xlZGdlNDhrZXJuZWw0OA"),
    ("vector48kernel48", "dmVjdG9yNDhrZXJuZWw0OA"),
    ("vector48signal48", "dmVjdG9yNDhzaWduYWw0OA"),
    ("vector48packet48", "dmVjdG9yNDhwYWNrZXQ0OA"),
    ("vector48router48", "dmVjdG9yNDhyb3V0ZXI0OA"),
    ("processor48router48", "cHJvY2Vzc29yNDhyb3V0ZXI0OA"),
    ("processor48cluster48", "cHJvY2Vzc29yNDhjbHVzdGVyNDg"),
    ("processor48mirror48", "cHJvY2Vzc29yNDhtaXJyb3I0OA"),
    ("processor48filter48", "cHJvY2Vzc29yNDhmaWx0ZXI0OA"),
    ("reasoning48filter48", "cmVhc29uaW5nNDhmaWx0ZXI0OA"),
    ("reasoning48ranking48", "cmVhc29uaW5nNDhyYW5raW5nNDg"),
    ("reasoning48encoding48", "cmVhc29uaW5nNDhlbmNvZGluZzQ4"),
    ("reasoning48mapping48", "cmVhc29uaW5nNDhtYXBwaW5nNDg"),
    ("machine48mapping48", "bWFjaGluZTQ4bWFwcGluZzQ4"),
    ("machine48record48", "bWFjaGluZTQ4cmVjb3JkNDg"),
    ("machine48candle48", "bWFjaGluZTQ4Y2FuZGxlNDg"),
    ("machine48thread48", "bWFjaGluZTQ4dGhyZWFkNDg"),
    ("learning48thread48", "bGVhcm5pbmc0OHRocmVhZDQ4"),
    ("learning48kitten48", "bGVhcm5pbmc0OGtpdHRlbjQ4"),
    ("learning48sitting48", "bGVhcm5pbmc0OHNpdHRpbmc0OA"),
    ("learning48agent48", "bGVhcm5pbmc0OGFnZW50NDg"),
    ("model48agent48", "bW9kZWw0OGFnZW50NDg"),
    ("model48angle48", "bW9kZWw0OGFuZ2xlNDg"),
    ("model48universe48", "bW9kZWw0OHVuaXZlcnNlNDg"),
    ("model48memory48", "bW9kZWw0OG1lbW9yeTQ4"),
    ("token48memory48", "dG9rZW40OG1lbW9yeTQ4"),
    ("token48stream48", "dG9rZW40OHN0cmVhbTQ4"),
    ("token48context48", "dG9rZW40OGNvbnRleHQ0OA"),
    ("token48knowledge48", "dG9rZW40OGtub3dsZWRnZTQ4"),
    ("prompt48knowledge48", "cHJvbXB0NDhrbm93bGVkZ2U0OA"),
    ("prompt48vector48", "cHJvbXB0NDh2ZWN0b3I0OA"),
    ("prompt48processor48", "cHJvbXB0NDhwcm9jZXNzb3I0OA"),
    ("prompt48reasoning48", "cHJvbXB0NDhyZWFzb25pbmc0OA"),
    ("session48reasoning48", "c2Vzc2lvbjQ4cmVhc29uaW5nNDg"),
    ("session48machine48", "c2Vzc2lvbjQ4bWFjaGluZTQ4"),
    ("session48learning48", "c2Vzc2lvbjQ4bGVhcm5pbmc0OA"),
    ("session48model48", "c2Vzc2lvbjQ4bW9kZWw0OA"),
    ("library48model48", "bGlicmFyeTQ4bW9kZWw0OA"),
    ("library48token48", "bGlicmFyeTQ4dG9rZW40OA"),
    ("library48prompt48", "bGlicmFyeTQ4cHJvbXB0NDg"),
    ("library48session48", "bGlicmFyeTQ4c2Vzc2lvbjQ4"),
    ("service48session48", "c2VydmljZTQ4c2Vzc2lvbjQ4"),
    ("service48library48", "c2VydmljZTQ4bGlicmFyeTQ4"),
    ("service48service48", "c2VydmljZTQ4c2VydmljZTQ4"),
    ("service48gateway48", "c2VydmljZTQ4Z2F0ZXdheTQ4"),
    ("gateway48gateway48", "Z2F0ZXdheTQ4Z2F0ZXdheTQ4"),
    ("gateway48storage48", "Z2F0ZXdheTQ4c3RvcmFnZTQ4"),
    ("gateway48network48", "Z2F0ZXdheTQ4bmV0d29yazQ4"),
    ("gateway48latency48", "Z2F0ZXdheTQ4bGF0ZW5jeTQ4"),
    ("storage48latency48", "c3RvcmFnZTQ4bGF0ZW5jeTQ4"),
    ("storage48buffer48", "c3RvcmFnZTQ4YnVmZmVyNDg"),
    ("storage48queue48", "c3RvcmFnZTQ4cXVldWU0OA"),
    ("storage48worker48", "c3RvcmFnZTQ4d29ya2VyNDg"),
    ("network48worker48", "bmV0d29yazQ4d29ya2VyNDg"),
    ("network48kernel48", "bmV0d29yazQ4a2VybmVsNDg"),
    ("network48signal48", "bmV0d29yazQ4c2lnbmFsNDg"),
    ("network48packet48", "bmV0d29yazQ4cGFja2V0NDg"),
    ("latency48packet48", "bGF0ZW5jeTQ4cGFja2V0NDg"),
    ("latency48router48", "bGF0ZW5jeTQ4cm91dGVyNDg"),
    ("latency48cluster48", "bGF0ZW5jeTQ4Y2x1c3RlcjQ4"),
    ("latency48mirror48", "bGF0ZW5jeTQ4bWlycm9yNDg"),
    ("buffer48mirror48", "YnVmZmVyNDhtaXJyb3I0OA"),
    ("buffer48filter48", "YnVmZmVyNDhmaWx0ZXI0OA"),
    ("buffer48ranking48", "YnVmZmVyNDhyYW5raW5nNDg"),
    ("buffer48encoding48", "YnVmZmVyNDhlbmNvZGluZzQ4"),
    ("queue48encoding48", "cXVldWU0OGVuY29kaW5nNDg"),
    ("queue48mapping48", "cXVldWU0OG1hcHBpbmc0OA"),
    ("queue48record48", "cXVldWU0OHJlY29yZDQ4"),
    ("queue48candle48", "cXVldWU0OGNhbmRsZTQ4"),
    ("worker48candle48", "d29ya2VyNDhjYW5kbGU0OA"),
    ("worker48thread48", "d29ya2VyNDh0aHJlYWQ0OA"),
    ("worker48kitten48", "d29ya2VyNDhraXR0ZW40OA"),
    ("worker48sitting48", "d29ya2VyNDhzaXR0aW5nNDg"),
    ("kernel48sitting48", "a2VybmVsNDhzaXR0aW5nNDg"),
    ("kernel48agent48", "a2VybmVsNDhhZ2VudDQ4"),
    ("kernel48angle48", "a2VybmVsNDhhbmdsZTQ4"),
    ("kernel48universe48", "a2VybmVsNDh1bml2ZXJzZTQ4"),
    ("signal48universe48", "c2lnbmFsNDh1bml2ZXJzZTQ4"),
    ("signal48memory48", "c2lnbmFsNDhtZW1vcnk0OA"),
    ("signal48stream48", "c2lnbmFsNDhzdHJlYW00OA"),
    ("signal48context48", "c2lnbmFsNDhjb250ZXh0NDg"),
    ("packet48context48", "cGFja2V0NDhjb250ZXh0NDg"),
    ("packet48knowledge48", "cGFja2V0NDhrbm93bGVkZ2U0OA"),
    ("packet48vector48", "cGFja2V0NDh2ZWN0b3I0OA"),
    ("packet48processor48", "cGFja2V0NDhwcm9jZXNzb3I0OA"),
    ("router48processor48", "cm91dGVyNDhwcm9jZXNzb3I0OA"),
    ("router48reasoning48", "cm91dGVyNDhyZWFzb25pbmc0OA"),
    ("router48machine48", "cm91dGVyNDhtYWNoaW5lNDg"),
    ("router48learning48", "cm91dGVyNDhsZWFybmluZzQ4"),
    ("cluster48learning48", "Y2x1c3RlcjQ4bGVhcm5pbmc0OA"),
    ("cluster48model48", "Y2x1c3RlcjQ4bW9kZWw0OA"),
    ("cluster48token48", "Y2x1c3RlcjQ4dG9rZW40OA"),
    ("cluster48prompt48", "Y2x1c3RlcjQ4cHJvbXB0NDg"),
    ("mirror48prompt48", "bWlycm9yNDhwcm9tcHQ0OA"),
    ("mirror48session48", "bWlycm9yNDhzZXNzaW9uNDg"),
    ("mirror48library48", "bWlycm9yNDhsaWJyYXJ5NDg"),
    ("mirror48service48", "bWlycm9yNDhzZXJ2aWNlNDg"),
    ("filter48service48", "ZmlsdGVyNDhzZXJ2aWNlNDg"),
    ("filter48gateway48", "ZmlsdGVyNDhnYXRld2F5NDg"),
    ("filter48storage48", "ZmlsdGVyNDhzdG9yYWdlNDg"),
    ("filter48network48", "ZmlsdGVyNDhuZXR3b3JrNDg"),
    ("ranking48network48", "cmFua2luZzQ4bmV0d29yazQ4"),
    ("ranking48latency48", "cmFua2luZzQ4bGF0ZW5jeTQ4"),
    ("ranking48buffer48", "cmFua2luZzQ4YnVmZmVyNDg"),
    ("ranking48queue48", "cmFua2luZzQ4cXVldWU0OA"),
    ("encoding48queue48", "ZW5jb2Rpbmc0OHF1ZXVlNDg"),
    ("encoding48worker48", "ZW5jb2Rpbmc0OHdvcmtlcjQ4"),
    ("encoding48kernel48", "ZW5jb2Rpbmc0OGtlcm5lbDQ4"),
    ("encoding48signal48", "ZW5jb2Rpbmc0OHNpZ25hbDQ4"),
    ("mapping48signal48", "bWFwcGluZzQ4c2lnbmFsNDg"),
    ("mapping48packet48", "bWFwcGluZzQ4cGFja2V0NDg"),
    ("mapping48router48", "bWFwcGluZzQ4cm91dGVyNDg"),
    ("mapping48cluster48", "bWFwcGluZzQ4Y2x1c3RlcjQ4"),
    ("record48cluster48", "cmVjb3JkNDhjbHVzdGVyNDg"),
    ("record48mirror48", "cmVjb3JkNDhtaXJyb3I0OA"),
    ("record48filter48", "cmVjb3JkNDhmaWx0ZXI0OA"),
    ("record48ranking48", "cmVjb3JkNDhyYW5raW5nNDg"),
    ("candle48ranking48", "Y2FuZGxlNDhyYW5raW5nNDg"),
    ("candle48encoding48", "Y2FuZGxlNDhlbmNvZGluZzQ4"),
    ("candle48mapping48", "Y2FuZGxlNDhtYXBwaW5nNDg"),
    ("candle48record48", "Y2FuZGxlNDhyZWNvcmQ0OA"),
    ("thread48record48", "dGhyZWFkNDhyZWNvcmQ0OA"),
    ("thread48candle48", "dGhyZWFkNDhjYW5kbGU0OA"),
    ("thread48thread48", "dGhyZWFkNDh0aHJlYWQ0OA"),
    ("thread48kitten48", "dGhyZWFkNDhraXR0ZW40OA"),
    (
        "round 48: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNDg6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 48: agentuniverse is a framework for multi agents",
        "cm91bmQgNDg6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 48: knowledge stored as vectors enables retrieval",
        "cm91bmQgNDg6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 48: the processor reads the record then stops",
        "cm91bmQgNDg6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 48: a worker pulls the next task from the queue",
        "cm91bmQgNDg6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 48: signals travel through the network layer",
        "cm91bmQgNDg6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 48: the gateway routes each request by policy",
        "cm91bmQgNDg6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 48: memory grows until the buffer is full",
        "cm91bmQgNDg6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 48: the cluster mirrors every packet twice",
        "cm91bmQgNDg6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 48: ranking uses tokens learned from the corpus",
        "cm91bmQgNDg6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 48: a long session ends when the candle dies",
        "cm91bmQgNDg6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 48: encode the prompt then map the result",
        "cm91bmQgNDg6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 48: the kernel wakes the worker at dawn", "cm91bmQgNDg6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 48: service latency drops after the patch",
        "cm91bmQgNDg6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 48: the library caches every vector it sees",
        "cm91bmQgNDg6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 48: agents argue then the debate resolves",
        "cm91bmQgNDg6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 48: the filter keeps only strong matches",
        "cm91bmQgNDg6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 48: the model answers with a short reply",
        "cm91bmQgNDg6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 48: the recorder stores the reasoning trace",
        "cm91bmQgNDg6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 48: the angel watches the processor run", "cm91bmQgNDg6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 48: angle of the vector decides the match",
        "cm91bmQgNDg6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 48: the candle burns twice as long at night",
        "cm91bmQgNDg6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 48: a mirror of the universe in one line",
        "cm91bmQgNDg6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 48: the queue drains before the storm", "cm91bmQgNDg6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
