"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten52kitten52", "a2l0dGVuNTJraXR0ZW41Mg"),
    ("kitten52sitting52", "a2l0dGVuNTJzaXR0aW5nNTI"),
    ("kitten52agent52", "a2l0dGVuNTJhZ2VudDUy"),
    ("kitten52angle52", "a2l0dGVuNTJhbmdsZTUy"),
    ("sitting52angle52", "c2l0dGluZzUyYW5nbGU1Mg"),
    ("sitting52universe52", "c2l0dGluZzUydW5pdmVyc2U1Mg"),
    ("sitting52memory52", "c2l0dGluZzUybWVtb3J5NTI"),
    ("sitting52stream52", "c2l0dGluZzUyc3RyZWFtNTI"),
    ("agent52stream52", "YWdlbnQ1MnN0cmVhbTUy"),
    ("agent52context52", "YWdlbnQ1MmNvbnRleHQ1Mg"),
    ("agent52knowledge52", "YWdlbnQ1Mmtub3dsZWRnZTUy"),
    ("agent52vector52", "YWdlbnQ1MnZlY3RvcjUy"),
    ("angle52vector52", "YW5nbGU1MnZlY3RvcjUy"),
    ("angle52processor52", "YW5nbGU1MnByb2Nlc3NvcjUy"),
    ("angle52reasoning52", "YW5nbGU1MnJlYXNvbmluZzUy"),
    ("angle52machine52", "YW5nbGU1Mm1hY2hpbmU1Mg"),
    ("universe52machine52", "dW5pdmVyc2U1Mm1hY2hpbmU1Mg"),
    ("universe52learning52", "dW5pdmVyc2U1MmxlYXJuaW5nNTI"),
    ("universe52model52", "dW5pdmVyc2U1Mm1vZGVsNTI"),
    ("universe52token52", "dW5pdmVyc2U1MnRva2VuNTI"),
    ("memory52token52", "bWVtb3J5NTJ0b2tlbjUy"),
    ("memory52prompt52", "bWVtb3J5NTJwcm9tcHQ1Mg"),
    ("memory52session52", "bWVtb3J5NTJzZXNzaW9uNTI"),
    ("memory52library52", "bWVtb3J5NTJsaWJyYXJ5NTI"),
    ("stream52library52", "c3RyZWFtNTJsaWJyYXJ5NTI"),
    ("stream52service52", "c3RyZWFtNTJzZXJ2aWNlNTI"),
    ("stream52gateway52", "c3RyZWFtNTJnYXRld2F5NTI"),
    ("stream52storage52", "c3RyZWFtNTJzdG9yYWdlNTI"),
    ("context52storage52", "Y29udGV4dDUyc3RvcmFnZTUy"),
    ("context52network52", "Y29udGV4dDUybmV0d29yazUy"),
    ("context52latency52", "Y29udGV4dDUybGF0ZW5jeTUy"),
    ("context52buffer52", "Y29udGV4dDUyYnVmZmVyNTI"),
    ("knowledge52buffer52", "a25vd2xlZGdlNTJidWZmZXI1Mg"),
    ("knowledge52queue52", "a25vd2xlZGdlNTJxdWV1ZTUy"),
    ("knowledge52worker52", "a25vd2xlZGdlNTJ3b3JrZXI1Mg"),
    ("knowledge52kernel52", "a25vd2xlZGdlNTJrZXJuZWw1Mg"),
    ("vector52kernel52", "dmVjdG9yNTJrZXJuZWw1Mg"),
    ("vector52signal52", "dmVjdG9yNTJzaWduYWw1Mg"),
    ("vector52packet52", "dmVjdG9yNTJwYWNrZXQ1Mg"),
    ("vector52router52", "dmVjdG9yNTJyb3V0ZXI1Mg"),
    ("processor52router52", "cHJvY2Vzc29yNTJyb3V0ZXI1Mg"),
    ("processor52cluster52", "cHJvY2Vzc29yNTJjbHVzdGVyNTI"),
    ("processor52mirror52", "cHJvY2Vzc29yNTJtaXJyb3I1Mg"),
    ("processor52filter52", "cHJvY2Vzc29yNTJmaWx0ZXI1Mg"),
    ("reasoning52filter52", "cmVhc29uaW5nNTJmaWx0ZXI1Mg"),
    ("reasoning52ranking52", "cmVhc29uaW5nNTJyYW5raW5nNTI"),
    ("reasoning52encoding52", "cmVhc29uaW5nNTJlbmNvZGluZzUy"),
    ("reasoning52mapping52", "cmVhc29uaW5nNTJtYXBwaW5nNTI"),
    ("machine52mapping52", "bWFjaGluZTUybWFwcGluZzUy"),
    ("machine52record52", "bWFjaGluZTUycmVjb3JkNTI"),
    ("machine52candle52", "bWFjaGluZTUyY2FuZGxlNTI"),
    ("machine52thread52", "bWFjaGluZTUydGhyZWFkNTI"),
    ("learning52thread52", "bGVhcm5pbmc1MnRocmVhZDUy"),
    ("learning52kitten52", "bGVhcm5pbmc1MmtpdHRlbjUy"),
    ("learning52sitting52", "bGVhcm5pbmc1MnNpdHRpbmc1Mg"),
    ("learning52agent52", "bGVhcm5pbmc1MmFnZW50NTI"),
    ("model52agent52", "bW9kZWw1MmFnZW50NTI"),
    ("model52angle52", "bW9kZWw1MmFuZ2xlNTI"),
    ("model52universe52", "bW9kZWw1MnVuaXZlcnNlNTI"),
    ("model52memory52", "bW9kZWw1Mm1lbW9yeTUy"),
    ("token52memory52", "dG9rZW41Mm1lbW9yeTUy"),
    ("token52stream52", "dG9rZW41MnN0cmVhbTUy"),
    ("token52context52", "dG9rZW41MmNvbnRleHQ1Mg"),
    ("token52knowledge52", "dG9rZW41Mmtub3dsZWRnZTUy"),
    ("prompt52knowledge52", "cHJvbXB0NTJrbm93bGVkZ2U1Mg"),
    ("prompt52vector52", "cHJvbXB0NTJ2ZWN0b3I1Mg"),
    ("prompt52processor52", "cHJvbXB0NTJwcm9jZXNzb3I1Mg"),
    ("prompt52reasoning52", "cHJvbXB0NTJyZWFzb25pbmc1Mg"),
    ("session52reasoning52", "c2Vzc2lvbjUycmVhc29uaW5nNTI"),
    ("session52machine52", "c2Vzc2lvbjUybWFjaGluZTUy"),
    ("session52learning52", "c2Vzc2lvbjUybGVhcm5pbmc1Mg"),
    ("session52model52", "c2Vzc2lvbjUybW9kZWw1Mg"),
    ("library52model52", "bGlicmFyeTUybW9kZWw1Mg"),
    ("library52token52", "bGlicmFyeTUydG9rZW41Mg"),
    ("library52prompt52", "bGlicmFyeTUycHJvbXB0NTI"),
    ("library52session52", "bGlicmFyeTUyc2Vzc2lvbjUy"),
    ("service52session52", "c2VydmljZTUyc2Vzc2lvbjUy"),
    ("service52library52", "c2VydmljZTUybGlicmFyeTUy"),
    ("service52service52", "c2VydmljZTUyc2VydmljZTUy"),
    ("service52gateway52", "c2VydmljZTUyZ2F0ZXdheTUy"),
    ("gateway52gateway52", "Z2F0ZXdheTUyZ2F0ZXdheTUy"),
    ("gateway52storage52", "Z2F0ZXdheTUyc3RvcmFnZTUy"),
    ("gateway52network52", "Z2F0ZXdheTUybmV0d29yazUy"),
    ("gateway52latency52", "Z2F0ZXdheTUybGF0ZW5jeTUy"),
    ("storage52latency52", "c3RvcmFnZTUybGF0ZW5jeTUy"),
    ("storage52buffer52", "c3RvcmFnZTUyYnVmZmVyNTI"),
    ("storage52queue52", "c3RvcmFnZTUycXVldWU1Mg"),
    ("storage52worker52", "c3RvcmFnZTUyd29ya2VyNTI"),
    ("network52worker52", "bmV0d29yazUyd29ya2VyNTI"),
    ("network52kernel52", "bmV0d29yazUya2VybmVsNTI"),
    ("network52signal52", "bmV0d29yazUyc2lnbmFsNTI"),
    ("network52packet52", "bmV0d29yazUycGFja2V0NTI"),
    ("latency52packet52", "bGF0ZW5jeTUycGFja2V0NTI"),
    ("latency52router52", "bGF0ZW5jeTUycm91dGVyNTI"),
    ("latency52cluster52", "bGF0ZW5jeTUyY2x1c3RlcjUy"),
    ("latency52mirror52", "bGF0ZW5jeTUybWlycm9yNTI"),
    ("buffer52mirror52", "YnVmZmVyNTJtaXJyb3I1Mg"),
    ("buffer52filter52", "YnVmZmVyNTJmaWx0ZXI1Mg"),
    ("buffer52ranking52", "YnVmZmVyNTJyYW5raW5nNTI"),
    ("buffer52encoding52", "YnVmZmVyNTJlbmNvZGluZzUy"),
    ("queue52encoding52", "cXVldWU1MmVuY29kaW5nNTI"),
    ("queue52mapping52", "cXVldWU1Mm1hcHBpbmc1Mg"),
    ("queue52record52", "cXVldWU1MnJlY29yZDUy"),
    ("queue52candle52", "cXVldWU1MmNhbmRsZTUy"),
    ("worker52candle52", "d29ya2VyNTJjYW5kbGU1Mg"),
    ("worker52thread52", "d29ya2VyNTJ0aHJlYWQ1Mg"),
    ("worker52kitten52", "d29ya2VyNTJraXR0ZW41Mg"),
    ("worker52sitting52", "d29ya2VyNTJzaXR0aW5nNTI"),
    ("kernel52sitting52", "a2VybmVsNTJzaXR0aW5nNTI"),
    ("kernel52agent52", "a2VybmVsNTJhZ2VudDUy"),
    ("kernel52angle52", "a2VybmVsNTJhbmdsZTUy"),
    ("kernel52universe52", "a2VybmVsNTJ1bml2ZXJzZTUy"),
    ("signal52universe52", "c2lnbmFsNTJ1bml2ZXJzZTUy"),
    ("signal52memory52", "c2lnbmFsNTJtZW1vcnk1Mg"),
    ("signal52stream52", "c2lnbmFsNTJzdHJlYW01Mg"),
    ("signal52context52", "c2lnbmFsNTJjb250ZXh0NTI"),
    ("packet52context52", "cGFja2V0NTJjb250ZXh0NTI"),
    ("packet52knowledge52", "cGFja2V0NTJrbm93bGVkZ2U1Mg"),
    ("packet52vector52", "cGFja2V0NTJ2ZWN0b3I1Mg"),
    ("packet52processor52", "cGFja2V0NTJwcm9jZXNzb3I1Mg"),
    ("router52processor52", "cm91dGVyNTJwcm9jZXNzb3I1Mg"),
    ("router52reasoning52", "cm91dGVyNTJyZWFzb25pbmc1Mg"),
    ("router52machine52", "cm91dGVyNTJtYWNoaW5lNTI"),
    ("router52learning52", "cm91dGVyNTJsZWFybmluZzUy"),
    ("cluster52learning52", "Y2x1c3RlcjUybGVhcm5pbmc1Mg"),
    ("cluster52model52", "Y2x1c3RlcjUybW9kZWw1Mg"),
    ("cluster52token52", "Y2x1c3RlcjUydG9rZW41Mg"),
    ("cluster52prompt52", "Y2x1c3RlcjUycHJvbXB0NTI"),
    ("mirror52prompt52", "bWlycm9yNTJwcm9tcHQ1Mg"),
    ("mirror52session52", "bWlycm9yNTJzZXNzaW9uNTI"),
    ("mirror52library52", "bWlycm9yNTJsaWJyYXJ5NTI"),
    ("mirror52service52", "bWlycm9yNTJzZXJ2aWNlNTI"),
    ("filter52service52", "ZmlsdGVyNTJzZXJ2aWNlNTI"),
    ("filter52gateway52", "ZmlsdGVyNTJnYXRld2F5NTI"),
    ("filter52storage52", "ZmlsdGVyNTJzdG9yYWdlNTI"),
    ("filter52network52", "ZmlsdGVyNTJuZXR3b3JrNTI"),
    ("ranking52network52", "cmFua2luZzUybmV0d29yazUy"),
    ("ranking52latency52", "cmFua2luZzUybGF0ZW5jeTUy"),
    ("ranking52buffer52", "cmFua2luZzUyYnVmZmVyNTI"),
    ("ranking52queue52", "cmFua2luZzUycXVldWU1Mg"),
    ("encoding52queue52", "ZW5jb2Rpbmc1MnF1ZXVlNTI"),
    ("encoding52worker52", "ZW5jb2Rpbmc1MndvcmtlcjUy"),
    ("encoding52kernel52", "ZW5jb2Rpbmc1Mmtlcm5lbDUy"),
    ("encoding52signal52", "ZW5jb2Rpbmc1MnNpZ25hbDUy"),
    ("mapping52signal52", "bWFwcGluZzUyc2lnbmFsNTI"),
    ("mapping52packet52", "bWFwcGluZzUycGFja2V0NTI"),
    ("mapping52router52", "bWFwcGluZzUycm91dGVyNTI"),
    ("mapping52cluster52", "bWFwcGluZzUyY2x1c3RlcjUy"),
    ("record52cluster52", "cmVjb3JkNTJjbHVzdGVyNTI"),
    ("record52mirror52", "cmVjb3JkNTJtaXJyb3I1Mg"),
    ("record52filter52", "cmVjb3JkNTJmaWx0ZXI1Mg"),
    ("record52ranking52", "cmVjb3JkNTJyYW5raW5nNTI"),
    ("candle52ranking52", "Y2FuZGxlNTJyYW5raW5nNTI"),
    ("candle52encoding52", "Y2FuZGxlNTJlbmNvZGluZzUy"),
    ("candle52mapping52", "Y2FuZGxlNTJtYXBwaW5nNTI"),
    ("candle52record52", "Y2FuZGxlNTJyZWNvcmQ1Mg"),
    ("thread52record52", "dGhyZWFkNTJyZWNvcmQ1Mg"),
    ("thread52candle52", "dGhyZWFkNTJjYW5kbGU1Mg"),
    ("thread52thread52", "dGhyZWFkNTJ0aHJlYWQ1Mg"),
    ("thread52kitten52", "dGhyZWFkNTJraXR0ZW41Mg"),
    (
        "round 52: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNTI6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 52: agentuniverse is a framework for multi agents",
        "cm91bmQgNTI6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 52: knowledge stored as vectors enables retrieval",
        "cm91bmQgNTI6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 52: the processor reads the record then stops",
        "cm91bmQgNTI6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 52: a worker pulls the next task from the queue",
        "cm91bmQgNTI6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 52: signals travel through the network layer",
        "cm91bmQgNTI6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 52: the gateway routes each request by policy",
        "cm91bmQgNTI6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 52: memory grows until the buffer is full",
        "cm91bmQgNTI6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 52: the cluster mirrors every packet twice",
        "cm91bmQgNTI6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 52: ranking uses tokens learned from the corpus",
        "cm91bmQgNTI6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 52: a long session ends when the candle dies",
        "cm91bmQgNTI6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 52: encode the prompt then map the result",
        "cm91bmQgNTI6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 52: the kernel wakes the worker at dawn", "cm91bmQgNTI6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 52: service latency drops after the patch",
        "cm91bmQgNTI6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 52: the library caches every vector it sees",
        "cm91bmQgNTI6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 52: agents argue then the debate resolves",
        "cm91bmQgNTI6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 52: the filter keeps only strong matches",
        "cm91bmQgNTI6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 52: the model answers with a short reply",
        "cm91bmQgNTI6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 52: the recorder stores the reasoning trace",
        "cm91bmQgNTI6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 52: the angel watches the processor run", "cm91bmQgNTI6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 52: angle of the vector decides the match",
        "cm91bmQgNTI6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 52: the candle burns twice as long at night",
        "cm91bmQgNTI6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 52: a mirror of the universe in one line",
        "cm91bmQgNTI6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 52: the queue drains before the storm", "cm91bmQgNTI6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
