"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten63kitten63", "a2l0dGVuNjNraXR0ZW42Mw"),
    ("kitten63sitting63", "a2l0dGVuNjNzaXR0aW5nNjM"),
    ("kitten63agent63", "a2l0dGVuNjNhZ2VudDYz"),
    ("kitten63angle63", "a2l0dGVuNjNhbmdsZTYz"),
    ("sitting63angle63", "c2l0dGluZzYzYW5nbGU2Mw"),
    ("sitting63universe63", "c2l0dGluZzYzdW5pdmVyc2U2Mw"),
    ("sitting63memory63", "c2l0dGluZzYzbWVtb3J5NjM"),
    ("sitting63stream63", "c2l0dGluZzYzc3RyZWFtNjM"),
    ("agent63stream63", "YWdlbnQ2M3N0cmVhbTYz"),
    ("agent63context63", "YWdlbnQ2M2NvbnRleHQ2Mw"),
    ("agent63knowledge63", "YWdlbnQ2M2tub3dsZWRnZTYz"),
    ("agent63vector63", "YWdlbnQ2M3ZlY3RvcjYz"),
    ("angle63vector63", "YW5nbGU2M3ZlY3RvcjYz"),
    ("angle63processor63", "YW5nbGU2M3Byb2Nlc3NvcjYz"),
    ("angle63reasoning63", "YW5nbGU2M3JlYXNvbmluZzYz"),
    ("angle63machine63", "YW5nbGU2M21hY2hpbmU2Mw"),
    ("universe63machine63", "dW5pdmVyc2U2M21hY2hpbmU2Mw"),
    ("universe63learning63", "dW5pdmVyc2U2M2xlYXJuaW5nNjM"),
    ("universe63model63", "dW5pdmVyc2U2M21vZGVsNjM"),
    ("universe63token63", "dW5pdmVyc2U2M3Rva2VuNjM"),
    ("memory63token63", "bWVtb3J5NjN0b2tlbjYz"),
    ("memory63prompt63", "bWVtb3J5NjNwcm9tcHQ2Mw"),
    ("memory63session63", "bWVtb3J5NjNzZXNzaW9uNjM"),
    ("memory63library63", "bWVtb3J5NjNsaWJyYXJ5NjM"),
    ("stream63library63", "c3RyZWFtNjNsaWJyYXJ5NjM"),
    ("stream63service63", "c3RyZWFtNjNzZXJ2aWNlNjM"),
    ("stream63gateway63", "c3RyZWFtNjNnYXRld2F5NjM"),
    ("stream63storage63", "c3RyZWFtNjNzdG9yYWdlNjM"),
    ("context63storage63", "Y29udGV4dDYzc3RvcmFnZTYz"),
    ("context63network63", "Y29udGV4dDYzbmV0d29yazYz"),
    ("context63latency63", "Y29udGV4dDYzbGF0ZW5jeTYz"),
    ("context63buffer63", "Y29udGV4dDYzYnVmZmVyNjM"),
    ("knowledge63buffer63", "a25vd2xlZGdlNjNidWZmZXI2Mw"),
    ("knowledge63queue63", "a25vd2xlZGdlNjNxdWV1ZTYz"),
    ("knowledge63worker63", "a25vd2xlZGdlNjN3b3JrZXI2Mw"),
    ("knowledge63kernel63", "a25vd2xlZGdlNjNrZXJuZWw2Mw"),
    ("vector63kernel63", "dmVjdG9yNjNrZXJuZWw2Mw"),
    ("vector63signal63", "dmVjdG9yNjNzaWduYWw2Mw"),
    ("vector63packet63", "dmVjdG9yNjNwYWNrZXQ2Mw"),
    ("vector63router63", "dmVjdG9yNjNyb3V0ZXI2Mw"),
    ("processor63router63", "cHJvY2Vzc29yNjNyb3V0ZXI2Mw"),
    ("processor63cluster63", "cHJvY2Vzc29yNjNjbHVzdGVyNjM"),
    ("processor63mirror63", "cHJvY2Vzc29yNjNtaXJyb3I2Mw"),
    ("processor63filter63", "cHJvY2Vzc29yNjNmaWx0ZXI2Mw"),
    ("reasoning63filter63", "cmVhc29uaW5nNjNmaWx0ZXI2Mw"),
    ("reasoning63ranking63", "cmVhc29uaW5nNjNyYW5raW5nNjM"),
    ("reasoning63encoding63", "cmVhc29uaW5nNjNlbmNvZGluZzYz"),
    ("reasoning63mapping63", "cmVhc29uaW5nNjNtYXBwaW5nNjM"),
    ("machine63mapping63", "bWFjaGluZTYzbWFwcGluZzYz"),
    ("machine63record63", "bWFjaGluZTYzcmVjb3JkNjM"),
    ("machine63candle63", "bWFjaGluZTYzY2FuZGxlNjM"),
    ("machine63thread63", "bWFjaGluZTYzdGhyZWFkNjM"),
    ("learning63thread63", "bGVhcm5pbmc2M3RocmVhZDYz"),
    ("learning63kitten63", "bGVhcm5pbmc2M2tpdHRlbjYz"),
    ("learning63sitting63", "bGVhcm5pbmc2M3NpdHRpbmc2Mw"),
    ("learning63agent63", "bGVhcm5pbmc2M2FnZW50NjM"),
    ("model63agent63", "bW9kZWw2M2FnZW50NjM"),
    ("model63angle63", "bW9kZWw2M2FuZ2xlNjM"),
    ("model63universe63", "bW9kZWw2M3VuaXZlcnNlNjM"),
    ("model63memory63", "bW9kZWw2M21lbW9yeTYz"),
    ("token63memory63", "dG9rZW42M21lbW9yeTYz"),
    ("token63stream63", "dG9rZW42M3N0cmVhbTYz"),
    ("token63context63", "dG9rZW42M2NvbnRleHQ2Mw"),
    ("token63knowledge63", "dG9rZW42M2tub3dsZWRnZTYz"),
    ("prompt63knowledge63", "cHJvbXB0NjNrbm93bGVkZ2U2Mw"),
    ("prompt63vector63", "cHJvbXB0NjN2ZWN0b3I2Mw"),
    ("prompt63processor63", "cHJvbXB0NjNwcm9jZXNzb3I2Mw"),
    ("prompt63reasoning63", "cHJvbXB0NjNyZWFzb25pbmc2Mw"),
    ("session63reasoning63", "c2Vzc2lvbjYzcmVhc29uaW5nNjM"),
    ("session63machine63", "c2Vzc2lvbjYzbWFjaGluZTYz"),
    ("session63learning63", "c2Vzc2lvbjYzbGVhcm5pbmc2Mw"),
    ("session63model63", "c2Vzc2lvbjYzbW9kZWw2Mw"),
    ("library63model63", "bGlicmFyeTYzbW9kZWw2Mw"),
    ("library63token63", "bGlicmFyeTYzdG9rZW42Mw"),
    ("library63prompt63", "bGlicmFyeTYzcHJvbXB0NjM"),
    ("library63session63", "bGlicmFyeTYzc2Vzc2lvbjYz"),
    ("service63session63", "c2VydmljZTYzc2Vzc2lvbjYz"),
    ("service63library63", "c2VydmljZTYzbGlicmFyeTYz"),
    ("service63service63", "c2VydmljZTYzc2VydmljZTYz"),
    ("service63gateway63", "c2VydmljZTYzZ2F0ZXdheTYz"),
    ("gateway63gateway63", "Z2F0ZXdheTYzZ2F0ZXdheTYz"),
    ("gateway63storage63", "Z2F0ZXdheTYzc3RvcmFnZTYz"),
    ("gateway63network63", "Z2F0ZXdheTYzbmV0d29yazYz"),
    ("gateway63latency63", "Z2F0ZXdheTYzbGF0ZW5jeTYz"),
    ("storage63latency63", "c3RvcmFnZTYzbGF0ZW5jeTYz"),
    ("storage63buffer63", "c3RvcmFnZTYzYnVmZmVyNjM"),
    ("storage63queue63", "c3RvcmFnZTYzcXVldWU2Mw"),
    ("storage63worker63", "c3RvcmFnZTYzd29ya2VyNjM"),
    ("network63worker63", "bmV0d29yazYzd29ya2VyNjM"),
    ("network63kernel63", "bmV0d29yazYza2VybmVsNjM"),
    ("network63signal63", "bmV0d29yazYzc2lnbmFsNjM"),
    ("network63packet63", "bmV0d29yazYzcGFja2V0NjM"),
    ("latency63packet63", "bGF0ZW5jeTYzcGFja2V0NjM"),
    ("latency63router63", "bGF0ZW5jeTYzcm91dGVyNjM"),
    ("latency63cluster63", "bGF0ZW5jeTYzY2x1c3RlcjYz"),
    ("latency63mirror63", "bGF0ZW5jeTYzbWlycm9yNjM"),
    ("buffer63mirror63", "YnVmZmVyNjNtaXJyb3I2Mw"),
    ("buffer63filter63", "YnVmZmVyNjNmaWx0ZXI2Mw"),
    ("buffer63ranking63", "YnVmZmVyNjNyYW5raW5nNjM"),
    ("buffer63encoding63", "YnVmZmVyNjNlbmNvZGluZzYz"),
    ("queue63encoding63", "cXVldWU2M2VuY29kaW5nNjM"),
    ("queue63mapping63", "cXVldWU2M21hcHBpbmc2Mw"),
    ("queue63record63", "cXVldWU2M3JlY29yZDYz"),
    ("queue63candle63", "cXVldWU2M2NhbmRsZTYz"),
    ("worker63candle63", "d29ya2VyNjNjYW5kbGU2Mw"),
    ("worker63thread63", "d29ya2VyNjN0aHJlYWQ2Mw"),
    ("worker63kitten63", "d29ya2VyNjNraXR0ZW42Mw"),
    ("worker63sitting63", "d29ya2VyNjNzaXR0aW5nNjM"),
    ("kernel63sitting63", "a2VybmVsNjNzaXR0aW5nNjM"),
    ("kernel63agent63", "a2VybmVsNjNhZ2VudDYz"),
    ("kernel63angle63", "a2VybmVsNjNhbmdsZTYz"),
    ("kernel63universe63", "a2VybmVsNjN1bml2ZXJzZTYz"),
    ("signal63universe63", "c2lnbmFsNjN1bml2ZXJzZTYz"),
    ("signal63memory63", "c2lnbmFsNjNtZW1vcnk2Mw"),
    ("signal63stream63", "c2lnbmFsNjNzdHJlYW02Mw"),
    ("signal63context63", "c2lnbmFsNjNjb250ZXh0NjM"),
    ("packet63context63", "cGFja2V0NjNjb250ZXh0NjM"),
    ("packet63knowledge63", "cGFja2V0NjNrbm93bGVkZ2U2Mw"),
    ("packet63vector63", "cGFja2V0NjN2ZWN0b3I2Mw"),
    ("packet63processor63", "cGFja2V0NjNwcm9jZXNzb3I2Mw"),
    ("router63processor63", "cm91dGVyNjNwcm9jZXNzb3I2Mw"),
    ("router63reasoning63", "cm91dGVyNjNyZWFzb25pbmc2Mw"),
    ("router63machine63", "cm91dGVyNjNtYWNoaW5lNjM"),
    ("router63learning63", "cm91dGVyNjNsZWFybmluZzYz"),
    ("cluster63learning63", "Y2x1c3RlcjYzbGVhcm5pbmc2Mw"),
    ("cluster63model63", "Y2x1c3RlcjYzbW9kZWw2Mw"),
    ("cluster63token63", "Y2x1c3RlcjYzdG9rZW42Mw"),
    ("cluster63prompt63", "Y2x1c3RlcjYzcHJvbXB0NjM"),
    ("mirror63prompt63", "bWlycm9yNjNwcm9tcHQ2Mw"),
    ("mirror63session63", "bWlycm9yNjNzZXNzaW9uNjM"),
    ("mirror63library63", "bWlycm9yNjNsaWJyYXJ5NjM"),
    ("mirror63service63", "bWlycm9yNjNzZXJ2aWNlNjM"),
    ("filter63service63", "ZmlsdGVyNjNzZXJ2aWNlNjM"),
    ("filter63gateway63", "ZmlsdGVyNjNnYXRld2F5NjM"),
    ("filter63storage63", "ZmlsdGVyNjNzdG9yYWdlNjM"),
    ("filter63network63", "ZmlsdGVyNjNuZXR3b3JrNjM"),
    ("ranking63network63", "cmFua2luZzYzbmV0d29yazYz"),
    ("ranking63latency63", "cmFua2luZzYzbGF0ZW5jeTYz"),
    ("ranking63buffer63", "cmFua2luZzYzYnVmZmVyNjM"),
    ("ranking63queue63", "cmFua2luZzYzcXVldWU2Mw"),
    ("encoding63queue63", "ZW5jb2Rpbmc2M3F1ZXVlNjM"),
    ("encoding63worker63", "ZW5jb2Rpbmc2M3dvcmtlcjYz"),
    ("encoding63kernel63", "ZW5jb2Rpbmc2M2tlcm5lbDYz"),
    ("encoding63signal63", "ZW5jb2Rpbmc2M3NpZ25hbDYz"),
    ("mapping63signal63", "bWFwcGluZzYzc2lnbmFsNjM"),
    ("mapping63packet63", "bWFwcGluZzYzcGFja2V0NjM"),
    ("mapping63router63", "bWFwcGluZzYzcm91dGVyNjM"),
    ("mapping63cluster63", "bWFwcGluZzYzY2x1c3RlcjYz"),
    ("record63cluster63", "cmVjb3JkNjNjbHVzdGVyNjM"),
    ("record63mirror63", "cmVjb3JkNjNtaXJyb3I2Mw"),
    ("record63filter63", "cmVjb3JkNjNmaWx0ZXI2Mw"),
    ("record63ranking63", "cmVjb3JkNjNyYW5raW5nNjM"),
    ("candle63ranking63", "Y2FuZGxlNjNyYW5raW5nNjM"),
    ("candle63encoding63", "Y2FuZGxlNjNlbmNvZGluZzYz"),
    ("candle63mapping63", "Y2FuZGxlNjNtYXBwaW5nNjM"),
    ("candle63record63", "Y2FuZGxlNjNyZWNvcmQ2Mw"),
    ("thread63record63", "dGhyZWFkNjNyZWNvcmQ2Mw"),
    ("thread63candle63", "dGhyZWFkNjNjYW5kbGU2Mw"),
    ("thread63thread63", "dGhyZWFkNjN0aHJlYWQ2Mw"),
    ("thread63kitten63", "dGhyZWFkNjNraXR0ZW42Mw"),
    (
        "round 63: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNjM6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 63: agentuniverse is a framework for multi agents",
        "cm91bmQgNjM6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 63: knowledge stored as vectors enables retrieval",
        "cm91bmQgNjM6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 63: the processor reads the record then stops",
        "cm91bmQgNjM6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 63: a worker pulls the next task from the queue",
        "cm91bmQgNjM6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 63: signals travel through the network layer",
        "cm91bmQgNjM6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 63: the gateway routes each request by policy",
        "cm91bmQgNjM6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 63: memory grows until the buffer is full",
        "cm91bmQgNjM6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 63: the cluster mirrors every packet twice",
        "cm91bmQgNjM6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 63: ranking uses tokens learned from the corpus",
        "cm91bmQgNjM6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 63: a long session ends when the candle dies",
        "cm91bmQgNjM6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 63: encode the prompt then map the result",
        "cm91bmQgNjM6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 63: the kernel wakes the worker at dawn", "cm91bmQgNjM6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 63: service latency drops after the patch",
        "cm91bmQgNjM6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 63: the library caches every vector it sees",
        "cm91bmQgNjM6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 63: agents argue then the debate resolves",
        "cm91bmQgNjM6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 63: the filter keeps only strong matches",
        "cm91bmQgNjM6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 63: the model answers with a short reply",
        "cm91bmQgNjM6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 63: the recorder stores the reasoning trace",
        "cm91bmQgNjM6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 63: the angel watches the processor run", "cm91bmQgNjM6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 63: angle of the vector decides the match",
        "cm91bmQgNjM6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 63: the candle burns twice as long at night",
        "cm91bmQgNjM6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 63: a mirror of the universe in one line",
        "cm91bmQgNjM6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 63: the queue drains before the storm", "cm91bmQgNjM6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
