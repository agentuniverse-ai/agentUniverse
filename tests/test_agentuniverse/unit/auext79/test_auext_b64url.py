"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten79kitten79", "a2l0dGVuNzlraXR0ZW43OQ"),
    ("kitten79sitting79", "a2l0dGVuNzlzaXR0aW5nNzk"),
    ("kitten79agent79", "a2l0dGVuNzlhZ2VudDc5"),
    ("kitten79angle79", "a2l0dGVuNzlhbmdsZTc5"),
    ("sitting79angle79", "c2l0dGluZzc5YW5nbGU3OQ"),
    ("sitting79universe79", "c2l0dGluZzc5dW5pdmVyc2U3OQ"),
    ("sitting79memory79", "c2l0dGluZzc5bWVtb3J5Nzk"),
    ("sitting79stream79", "c2l0dGluZzc5c3RyZWFtNzk"),
    ("agent79stream79", "YWdlbnQ3OXN0cmVhbTc5"),
    ("agent79context79", "YWdlbnQ3OWNvbnRleHQ3OQ"),
    ("agent79knowledge79", "YWdlbnQ3OWtub3dsZWRnZTc5"),
    ("agent79vector79", "YWdlbnQ3OXZlY3Rvcjc5"),
    ("angle79vector79", "YW5nbGU3OXZlY3Rvcjc5"),
    ("angle79processor79", "YW5nbGU3OXByb2Nlc3Nvcjc5"),
    ("angle79reasoning79", "YW5nbGU3OXJlYXNvbmluZzc5"),
    ("angle79machine79", "YW5nbGU3OW1hY2hpbmU3OQ"),
    ("universe79machine79", "dW5pdmVyc2U3OW1hY2hpbmU3OQ"),
    ("universe79learning79", "dW5pdmVyc2U3OWxlYXJuaW5nNzk"),
    ("universe79model79", "dW5pdmVyc2U3OW1vZGVsNzk"),
    ("universe79token79", "dW5pdmVyc2U3OXRva2VuNzk"),
    ("memory79token79", "bWVtb3J5Nzl0b2tlbjc5"),
    ("memory79prompt79", "bWVtb3J5Nzlwcm9tcHQ3OQ"),
    ("memory79session79", "bWVtb3J5NzlzZXNzaW9uNzk"),
    ("memory79library79", "bWVtb3J5NzlsaWJyYXJ5Nzk"),
    ("stream79library79", "c3RyZWFtNzlsaWJyYXJ5Nzk"),
    ("stream79service79", "c3RyZWFtNzlzZXJ2aWNlNzk"),
    ("stream79gateway79", "c3RyZWFtNzlnYXRld2F5Nzk"),
    ("stream79storage79", "c3RyZWFtNzlzdG9yYWdlNzk"),
    ("context79storage79", "Y29udGV4dDc5c3RvcmFnZTc5"),
    ("context79network79", "Y29udGV4dDc5bmV0d29yazc5"),
    ("context79latency79", "Y29udGV4dDc5bGF0ZW5jeTc5"),
    ("context79buffer79", "Y29udGV4dDc5YnVmZmVyNzk"),
    ("knowledge79buffer79", "a25vd2xlZGdlNzlidWZmZXI3OQ"),
    ("knowledge79queue79", "a25vd2xlZGdlNzlxdWV1ZTc5"),
    ("knowledge79worker79", "a25vd2xlZGdlNzl3b3JrZXI3OQ"),
    ("knowledge79kernel79", "a25vd2xlZGdlNzlrZXJuZWw3OQ"),
    ("vector79kernel79", "dmVjdG9yNzlrZXJuZWw3OQ"),
    ("vector79signal79", "dmVjdG9yNzlzaWduYWw3OQ"),
    ("vector79packet79", "dmVjdG9yNzlwYWNrZXQ3OQ"),
    ("vector79router79", "dmVjdG9yNzlyb3V0ZXI3OQ"),
    ("processor79router79", "cHJvY2Vzc29yNzlyb3V0ZXI3OQ"),
    ("processor79cluster79", "cHJvY2Vzc29yNzljbHVzdGVyNzk"),
    ("processor79mirror79", "cHJvY2Vzc29yNzltaXJyb3I3OQ"),
    ("processor79filter79", "cHJvY2Vzc29yNzlmaWx0ZXI3OQ"),
    ("reasoning79filter79", "cmVhc29uaW5nNzlmaWx0ZXI3OQ"),
    ("reasoning79ranking79", "cmVhc29uaW5nNzlyYW5raW5nNzk"),
    ("reasoning79encoding79", "cmVhc29uaW5nNzllbmNvZGluZzc5"),
    ("reasoning79mapping79", "cmVhc29uaW5nNzltYXBwaW5nNzk"),
    ("machine79mapping79", "bWFjaGluZTc5bWFwcGluZzc5"),
    ("machine79record79", "bWFjaGluZTc5cmVjb3JkNzk"),
    ("machine79candle79", "bWFjaGluZTc5Y2FuZGxlNzk"),
    ("machine79thread79", "bWFjaGluZTc5dGhyZWFkNzk"),
    ("learning79thread79", "bGVhcm5pbmc3OXRocmVhZDc5"),
    ("learning79kitten79", "bGVhcm5pbmc3OWtpdHRlbjc5"),
    ("learning79sitting79", "bGVhcm5pbmc3OXNpdHRpbmc3OQ"),
    ("learning79agent79", "bGVhcm5pbmc3OWFnZW50Nzk"),
    ("model79agent79", "bW9kZWw3OWFnZW50Nzk"),
    ("model79angle79", "bW9kZWw3OWFuZ2xlNzk"),
    ("model79universe79", "bW9kZWw3OXVuaXZlcnNlNzk"),
    ("model79memory79", "bW9kZWw3OW1lbW9yeTc5"),
    ("token79memory79", "dG9rZW43OW1lbW9yeTc5"),
    ("token79stream79", "dG9rZW43OXN0cmVhbTc5"),
    ("token79context79", "dG9rZW43OWNvbnRleHQ3OQ"),
    ("token79knowledge79", "dG9rZW43OWtub3dsZWRnZTc5"),
    ("prompt79knowledge79", "cHJvbXB0Nzlrbm93bGVkZ2U3OQ"),
    ("prompt79vector79", "cHJvbXB0Nzl2ZWN0b3I3OQ"),
    ("prompt79processor79", "cHJvbXB0Nzlwcm9jZXNzb3I3OQ"),
    ("prompt79reasoning79", "cHJvbXB0NzlyZWFzb25pbmc3OQ"),
    ("session79reasoning79", "c2Vzc2lvbjc5cmVhc29uaW5nNzk"),
    ("session79machine79", "c2Vzc2lvbjc5bWFjaGluZTc5"),
    ("session79learning79", "c2Vzc2lvbjc5bGVhcm5pbmc3OQ"),
    ("session79model79", "c2Vzc2lvbjc5bW9kZWw3OQ"),
    ("library79model79", "bGlicmFyeTc5bW9kZWw3OQ"),
    ("library79token79", "bGlicmFyeTc5dG9rZW43OQ"),
    ("library79prompt79", "bGlicmFyeTc5cHJvbXB0Nzk"),
    ("library79session79", "bGlicmFyeTc5c2Vzc2lvbjc5"),
    ("service79session79", "c2VydmljZTc5c2Vzc2lvbjc5"),
    ("service79library79", "c2VydmljZTc5bGlicmFyeTc5"),
    ("service79service79", "c2VydmljZTc5c2VydmljZTc5"),
    ("service79gateway79", "c2VydmljZTc5Z2F0ZXdheTc5"),
    ("gateway79gateway79", "Z2F0ZXdheTc5Z2F0ZXdheTc5"),
    ("gateway79storage79", "Z2F0ZXdheTc5c3RvcmFnZTc5"),
    ("gateway79network79", "Z2F0ZXdheTc5bmV0d29yazc5"),
    ("gateway79latency79", "Z2F0ZXdheTc5bGF0ZW5jeTc5"),
    ("storage79latency79", "c3RvcmFnZTc5bGF0ZW5jeTc5"),
    ("storage79buffer79", "c3RvcmFnZTc5YnVmZmVyNzk"),
    ("storage79queue79", "c3RvcmFnZTc5cXVldWU3OQ"),
    ("storage79worker79", "c3RvcmFnZTc5d29ya2VyNzk"),
    ("network79worker79", "bmV0d29yazc5d29ya2VyNzk"),
    ("network79kernel79", "bmV0d29yazc5a2VybmVsNzk"),
    ("network79signal79", "bmV0d29yazc5c2lnbmFsNzk"),
    ("network79packet79", "bmV0d29yazc5cGFja2V0Nzk"),
    ("latency79packet79", "bGF0ZW5jeTc5cGFja2V0Nzk"),
    ("latency79router79", "bGF0ZW5jeTc5cm91dGVyNzk"),
    ("latency79cluster79", "bGF0ZW5jeTc5Y2x1c3Rlcjc5"),
    ("latency79mirror79", "bGF0ZW5jeTc5bWlycm9yNzk"),
    ("buffer79mirror79", "YnVmZmVyNzltaXJyb3I3OQ"),
    ("buffer79filter79", "YnVmZmVyNzlmaWx0ZXI3OQ"),
    ("buffer79ranking79", "YnVmZmVyNzlyYW5raW5nNzk"),
    ("buffer79encoding79", "YnVmZmVyNzllbmNvZGluZzc5"),
    ("queue79encoding79", "cXVldWU3OWVuY29kaW5nNzk"),
    ("queue79mapping79", "cXVldWU3OW1hcHBpbmc3OQ"),
    ("queue79record79", "cXVldWU3OXJlY29yZDc5"),
    ("queue79candle79", "cXVldWU3OWNhbmRsZTc5"),
    ("worker79candle79", "d29ya2VyNzljYW5kbGU3OQ"),
    ("worker79thread79", "d29ya2VyNzl0aHJlYWQ3OQ"),
    ("worker79kitten79", "d29ya2VyNzlraXR0ZW43OQ"),
    ("worker79sitting79", "d29ya2VyNzlzaXR0aW5nNzk"),
    ("kernel79sitting79", "a2VybmVsNzlzaXR0aW5nNzk"),
    ("kernel79agent79", "a2VybmVsNzlhZ2VudDc5"),
    ("kernel79angle79", "a2VybmVsNzlhbmdsZTc5"),
    ("kernel79universe79", "a2VybmVsNzl1bml2ZXJzZTc5"),
    ("signal79universe79", "c2lnbmFsNzl1bml2ZXJzZTc5"),
    ("signal79memory79", "c2lnbmFsNzltZW1vcnk3OQ"),
    ("signal79stream79", "c2lnbmFsNzlzdHJlYW03OQ"),
    ("signal79context79", "c2lnbmFsNzljb250ZXh0Nzk"),
    ("packet79context79", "cGFja2V0Nzljb250ZXh0Nzk"),
    ("packet79knowledge79", "cGFja2V0Nzlrbm93bGVkZ2U3OQ"),
    ("packet79vector79", "cGFja2V0Nzl2ZWN0b3I3OQ"),
    ("packet79processor79", "cGFja2V0Nzlwcm9jZXNzb3I3OQ"),
    ("router79processor79", "cm91dGVyNzlwcm9jZXNzb3I3OQ"),
    ("router79reasoning79", "cm91dGVyNzlyZWFzb25pbmc3OQ"),
    ("router79machine79", "cm91dGVyNzltYWNoaW5lNzk"),
    ("router79learning79", "cm91dGVyNzlsZWFybmluZzc5"),
    ("cluster79learning79", "Y2x1c3Rlcjc5bGVhcm5pbmc3OQ"),
    ("cluster79model79", "Y2x1c3Rlcjc5bW9kZWw3OQ"),
    ("cluster79token79", "Y2x1c3Rlcjc5dG9rZW43OQ"),
    ("cluster79prompt79", "Y2x1c3Rlcjc5cHJvbXB0Nzk"),
    ("mirror79prompt79", "bWlycm9yNzlwcm9tcHQ3OQ"),
    ("mirror79session79", "bWlycm9yNzlzZXNzaW9uNzk"),
    ("mirror79library79", "bWlycm9yNzlsaWJyYXJ5Nzk"),
    ("mirror79service79", "bWlycm9yNzlzZXJ2aWNlNzk"),
    ("filter79service79", "ZmlsdGVyNzlzZXJ2aWNlNzk"),
    ("filter79gateway79", "ZmlsdGVyNzlnYXRld2F5Nzk"),
    ("filter79storage79", "ZmlsdGVyNzlzdG9yYWdlNzk"),
    ("filter79network79", "ZmlsdGVyNzluZXR3b3JrNzk"),
    ("ranking79network79", "cmFua2luZzc5bmV0d29yazc5"),
    ("ranking79latency79", "cmFua2luZzc5bGF0ZW5jeTc5"),
    ("ranking79buffer79", "cmFua2luZzc5YnVmZmVyNzk"),
    ("ranking79queue79", "cmFua2luZzc5cXVldWU3OQ"),
    ("encoding79queue79", "ZW5jb2Rpbmc3OXF1ZXVlNzk"),
    ("encoding79worker79", "ZW5jb2Rpbmc3OXdvcmtlcjc5"),
    ("encoding79kernel79", "ZW5jb2Rpbmc3OWtlcm5lbDc5"),
    ("encoding79signal79", "ZW5jb2Rpbmc3OXNpZ25hbDc5"),
    ("mapping79signal79", "bWFwcGluZzc5c2lnbmFsNzk"),
    ("mapping79packet79", "bWFwcGluZzc5cGFja2V0Nzk"),
    ("mapping79router79", "bWFwcGluZzc5cm91dGVyNzk"),
    ("mapping79cluster79", "bWFwcGluZzc5Y2x1c3Rlcjc5"),
    ("record79cluster79", "cmVjb3JkNzljbHVzdGVyNzk"),
    ("record79mirror79", "cmVjb3JkNzltaXJyb3I3OQ"),
    ("record79filter79", "cmVjb3JkNzlmaWx0ZXI3OQ"),
    ("record79ranking79", "cmVjb3JkNzlyYW5raW5nNzk"),
    ("candle79ranking79", "Y2FuZGxlNzlyYW5raW5nNzk"),
    ("candle79encoding79", "Y2FuZGxlNzllbmNvZGluZzc5"),
    ("candle79mapping79", "Y2FuZGxlNzltYXBwaW5nNzk"),
    ("candle79record79", "Y2FuZGxlNzlyZWNvcmQ3OQ"),
    ("thread79record79", "dGhyZWFkNzlyZWNvcmQ3OQ"),
    ("thread79candle79", "dGhyZWFkNzljYW5kbGU3OQ"),
    ("thread79thread79", "dGhyZWFkNzl0aHJlYWQ3OQ"),
    ("thread79kitten79", "dGhyZWFkNzlraXR0ZW43OQ"),
    (
        "round 79: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzk6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 79: agentuniverse is a framework for multi agents",
        "cm91bmQgNzk6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 79: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzk6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 79: the processor reads the record then stops",
        "cm91bmQgNzk6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 79: a worker pulls the next task from the queue",
        "cm91bmQgNzk6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 79: signals travel through the network layer",
        "cm91bmQgNzk6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 79: the gateway routes each request by policy",
        "cm91bmQgNzk6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 79: memory grows until the buffer is full",
        "cm91bmQgNzk6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 79: the cluster mirrors every packet twice",
        "cm91bmQgNzk6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 79: ranking uses tokens learned from the corpus",
        "cm91bmQgNzk6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 79: a long session ends when the candle dies",
        "cm91bmQgNzk6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 79: encode the prompt then map the result",
        "cm91bmQgNzk6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 79: the kernel wakes the worker at dawn", "cm91bmQgNzk6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 79: service latency drops after the patch",
        "cm91bmQgNzk6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 79: the library caches every vector it sees",
        "cm91bmQgNzk6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 79: agents argue then the debate resolves",
        "cm91bmQgNzk6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 79: the filter keeps only strong matches",
        "cm91bmQgNzk6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 79: the model answers with a short reply",
        "cm91bmQgNzk6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 79: the recorder stores the reasoning trace",
        "cm91bmQgNzk6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 79: the angel watches the processor run", "cm91bmQgNzk6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 79: angle of the vector decides the match",
        "cm91bmQgNzk6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 79: the candle burns twice as long at night",
        "cm91bmQgNzk6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 79: a mirror of the universe in one line",
        "cm91bmQgNzk6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 79: the queue drains before the storm", "cm91bmQgNzk6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
